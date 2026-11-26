#!/usr/bin/env python3
"""Generate live, native Obsidian-styled GitHub telemetry SVGs for Vrajm12/Vrajm12.

Generates 4 cohesive SVGs in assets/visuals/:
  1. streak-banner.svg     (All-Time Total, Current Streak Ring, Longest Streak, YTD)
  2. github-stats.svg      (Last 365 Days, Commits/Active Days, Repos, Stars, Followers)
  3. top-languages.svg     (Top 6 Languages across repositories)
  4. activity-velocity.svg (31-Day Daily Contribution Velocity Spline & Area Graph)
"""

from __future__ import annotations

import datetime as dt
import html
import json
import os
import re
import urllib.request
from pathlib import Path

USERNAME = os.environ.get("GH_USERNAME", "Vrajm12")
START_YEAR = 2023
ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "assets" / "visuals"

FONT_SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Inter, Roboto, Helvetica, Arial, sans-serif"
FONT_MONO = "'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace"

FALLBACK_COLORS = {
    "TypeScript": "#3178c6",
    "Python": "#42d6c5",
    "JavaScript": "#e8ad5a",
    "HTML": "#ff7b72",
    "CSS": "#b58aff",
    "Dart": "#00B4AB",
    "C++": "#f34b7d",
    "C": "#8b949e",
    "PLpgSQL": "#668cff",
    "Dockerfile": "#58a6ff",
}


def http_get(url: str) -> str:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": f"{USERNAME}-profile-telemetry-engine"},
    )
    with urllib.request.urlopen(req, timeout=25) as resp:
        return resp.read().decode("utf-8", errors="replace")


def graphql(query: str, token: str) -> dict:
    payload = json.dumps({"query": query}).encode("utf-8")
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": f"{USERNAME}-profile-telemetry-engine",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=25) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    if "errors" in data:
        raise RuntimeError(f"GraphQL error: {data['errors']}")
    return data["data"]


def parse_calendar_fragment(fragment: str) -> tuple[int | None, dict[str, int]]:
    normalized = " ".join(fragment.split())
    header_match = re.search(r"([\d,]+)\s+contributions?\s+in\s+", normalized, re.I)
    header_total = int(header_match.group(1).replace(",", "")) if header_match else None

    days = dict(re.findall(r'data-date="(\d{4}-\d{2}-\d{2})"[^>]*id="([^"]+)"', fragment))
    if not days:
        days = {d: cid for cid, d in re.findall(r'id="([^"]+)"[^>]*data-date="(\d{4}-\d{2}-\d{2})"', fragment)}

    tips = dict(re.findall(r'<tool-tip[^>]*for="([^"]+)"[^>]*>([^<]+)</tool-tip>', fragment))
    daily: dict[str, int] = {}
    for date_str, comp_id in days.items():
        tip_text = tips.get(comp_id, "")
        m = re.search(r"([\d,]+)\s+contribution", tip_text)
        daily[date_str] = int(m.group(1).replace(",", "")) if m else 0

    return header_total, daily


def fmt_short_date(d_str: str) -> str:
    d = dt.date.fromisoformat(d_str)
    return d.strftime("%b %d, %Y")


def fmt_month_day(d_str: str) -> str:
    d = dt.date.fromisoformat(d_str)
    return f"{d.strftime('%b')} {d.day}"


def compute_streaks(all_days: dict[str, int], today_utc: dt.date) -> dict:
    if not all_days:
        return {
            "current": 0,
            "current_range": "No active streak",
            "longest": 0,
            "longest_range": "—",
            "first_active": f"Jan 1, {START_YEAR}",
            "active_days_365": 0,
        }

    sorted_dates = sorted(dt.date.fromisoformat(k) for k in all_days.keys() if dt.date.fromisoformat(k) <= today_utc)
    first_active_candidates = [d for d in sorted_dates if all_days.get(d.isoformat(), 0) > 0]
    first_active = first_active_candidates[0] if first_active_candidates else sorted_dates[0]

    longest = 0
    longest_start = first_active
    longest_end = first_active

    run = 0
    run_start = first_active
    prev_day: dt.date | None = None

    for d in sorted_dates:
        cnt = all_days.get(d.isoformat(), 0)
        if cnt > 0:
            if prev_day is not None and (d - prev_day).days == 1 and run > 0:
                run += 1
            else:
                run = 1
                run_start = d
            if run >= longest:
                longest = run
                longest_start = run_start
                longest_end = d
        else:
            run = 0
        prev_day = d

    # Current streak: allow today or yesterday (if today hasn't had a commit yet in UTC/IST boundary)
    latest_available = sorted_dates[-1]
    anchor = latest_available
    if all_days.get(anchor.isoformat(), 0) == 0:
        yesterday = anchor - dt.timedelta(days=1)
        if all_days.get(yesterday.isoformat(), 0) > 0:
            anchor = yesterday
        else:
            anchor = None

    current = 0
    cur_start = latest_available
    cur_end = latest_available
    if anchor is not None:
        cur_end = anchor
        cursor = anchor
        while all_days.get(cursor.isoformat(), 0) > 0:
            current += 1
            cur_start = cursor
            cursor -= dt.timedelta(days=1)

    cutoff_365 = latest_available - dt.timedelta(days=364)
    active_days_365 = sum(
        1 for d in sorted_dates if d >= cutoff_365 and all_days.get(d.isoformat(), 0) > 0
    )

    cur_range = (
        f"{fmt_month_day(cur_start.isoformat())} – {fmt_month_day(cur_end.isoformat())}"
        if current > 0
        else "Start a streak today"
    )
    long_range = (
        f"{fmt_month_day(longest_start.isoformat())} – {fmt_month_day(longest_end.isoformat())}, {longest_end.year}"
        if longest > 0
        else "—"
    )

    return {
        "current": current,
        "current_range": cur_range,
        "longest": longest,
        "longest_range": long_range,
        "first_active": fmt_short_date(first_active.isoformat()),
        "active_days_365": active_days_365,
    }


def fetch_metrics(token: str) -> dict:
    # Use IST (+05:30) as local reference date for Veeraj's profile
    ist = dt.timezone(dt.timedelta(hours=5, minutes=30))
    now_ist = dt.datetime.now(ist)
    today_date = now_ist.date()
    current_year = today_date.year

    use_viewer = False
    try:
        who = graphql("query { viewer { login } }", token)
        use_viewer = who["viewer"]["login"].lower() == USERNAME.lower()
    except Exception:
        use_viewer = False

    year_blocks = "\n".join(
        f'y{y}: contributionsCollection(from: "{y}-01-01T00:00:00Z", to: "{y}-12-31T23:59:59Z") {{ contributionCalendar {{ totalContributions weeks {{ contributionDays {{ date contributionCount }} }} }} }}'
        for y in range(START_YEAR, current_year + 1)
    )
    repo_filter = "" if use_viewer else ", privacy: PUBLIC"
    subject_root = "viewer" if use_viewer else f'user(login: "{USERNAME}")'

    query = f"""
    query {{
      subject: {subject_root} {{
        followers {{ totalCount }}
        rolling: contributionsCollection {{
          contributionCalendar {{
            totalContributions
            weeks {{ contributionDays {{ date contributionCount }} }}
          }}
        }}
        {year_blocks}
        repositories(first: 100, ownerAffiliations: OWNER, isFork: false{repo_filter}) {{
          totalCount
          nodes {{
            name
            isPrivate
            stargazerCount
            languages(first: 10, orderBy: {{field: SIZE, direction: DESC}}) {{
              edges {{ size node {{ name color }} }}
            }}
          }}
        }}
      }}
    }}
    """

    subj = graphql(query, token)["subject"]

    all_days: dict[str, int] = {}
    gql_yearly: dict[int, int] = {}
    for y in range(START_YEAR, current_year + 1):
        cal = subj[f"y{y}"]["contributionCalendar"]
        gql_yearly[y] = cal["totalContributions"]
        for w in cal["weeks"]:
            for d in w["contributionDays"]:
                all_days[d["date"]] = max(all_days.get(d["date"], 0), d["contributionCount"])

    gql_rolling = subj["rolling"]["contributionCalendar"]["totalContributions"]
    for w in subj["rolling"]["contributionCalendar"]["weeks"]:
        for d in w["contributionDays"]:
            all_days[d["date"]] = max(all_days.get(d["date"], 0), d["contributionCount"])

    # Also read public profile calendar HTML so GitHub Actions (with default GITHUB_TOKEN)
    # captures restricted/private contributions accurately without needing a PAT secret.
    html_rolling = None
    try:
        frag = http_get(f"https://github.com/users/{USERNAME}/contributions")
        html_rolling, rolling_days = parse_calendar_fragment(frag)
        for k, v in rolling_days.items():
            all_days[k] = max(all_days.get(k, 0), v)
    except Exception:
        pass

    html_yearly: dict[int, int] = {}
    for y in range(START_YEAR, current_year + 1):
        try:
            frag = http_get(f"https://github.com/users/{USERNAME}/contributions?from={y}-01-01&to={y}-12-31")
            y_tot, y_days = parse_calendar_fragment(frag)
            if y_tot is not None:
                html_yearly[y] = y_tot
            for k, v in y_days.items():
                all_days[k] = max(all_days.get(k, 0), v)
        except Exception:
            continue

    rolling_total = max(gql_rolling, html_rolling or 0)
    yearly_totals = {
        y: max(gql_yearly.get(y, 0), html_yearly.get(y, 0))
        for y in range(START_YEAR, current_year + 1)
    }
    all_time_total = sum(yearly_totals.values())
    current_year_total = yearly_totals.get(current_year, 0)

    streaks = compute_streaks(all_days, today_date)

    # Last 31 days series for velocity chart
    series_31: list[tuple[str, int]] = []
    for offset in range(30, -1, -1):
        d_iso = (today_date - dt.timedelta(days=offset)).isoformat()
        series_31.append((d_iso, all_days.get(d_iso, 0)))

    repos = subj["repositories"]["nodes"]
    total_stars = sum(r["stargazerCount"] for r in repos)
    repo_count = subj["repositories"]["totalCount"]

    MAX_REPO_LANG_BYTES = 2_500_000
    IGNORE_LANGS = {"Jupyter Notebook", "Shell", "Batchfile", "Makefile", "CMake", "Cython"}
    lang_totals: dict[str, int] = {}
    lang_colors: dict[str, str] = {}

    for repo in repos:
        for edge in repo["languages"]["edges"]:
            name = edge["node"]["name"]
            if name in IGNORE_LANGS:
                continue
            size = min(edge["size"], MAX_REPO_LANG_BYTES)
            lang_totals[name] = lang_totals.get(name, 0) + size
            if name not in lang_colors and edge["node"].get("color"):
                lang_colors[name] = edge["node"]["color"]

    sorted_langs = sorted(lang_totals.items(), key=lambda kv: kv[1], reverse=True)[:6]
    lang_sum = sum(sz for _, sz in sorted_langs) or 1
    languages = [
        {
            "name": name,
            "bytes": sz,
            "pct": (sz / lang_sum) * 100.0,
            "color": FALLBACK_COLORS.get(name, lang_colors.get(name, "#668cff")),
        }
        for name, sz in sorted_langs
    ]

    return {
        "rolling_total": rolling_total,
        "all_time_total": all_time_total,
        "current_year": current_year,
        "current_year_total": current_year_total,
        "streaks": streaks,
        "series_31": series_31,
        "repo_count": repo_count,
        "repo_label": "Owned Repos" if use_viewer else "Public Repos",
        "stars": total_stars,
        "followers": subj["followers"]["totalCount"],
        "languages": languages,
        "updated": now_ist.strftime("%b %d, %Y"),
    }


def obsidian_defs(prefix: str, width: int, height: int) -> str:
    return f"""  <defs>
    <linearGradient id="{prefix}-bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#070b14"/>
      <stop offset="55%" stop-color="#0c1424"/>
      <stop offset="100%" stop-color="#0f1b31"/>
    </linearGradient>
    <linearGradient id="{prefix}-rim" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#42d6c5" stop-opacity="0.75"/>
      <stop offset="50%" stop-color="#668cff" stop-opacity="0.75"/>
      <stop offset="100%" stop-color="#b58aff" stop-opacity="0.75"/>
    </linearGradient>
    <linearGradient id="{prefix}-ring" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#42d6c5"/>
      <stop offset="100%" stop-color="#668cff"/>
    </linearGradient>
    <pattern id="{prefix}-dots" width="24" height="24" patternUnits="userSpaceOnUse">
      <circle cx="2" cy="2" r="1" fill="#8aa4c8" fill-opacity="0.08"/>
    </pattern>
  </defs>
  <rect width="{width}" height="{height}" rx="18" fill="url(#{prefix}-bg)" stroke="#1f304d" stroke-width="1.2"/>
  <rect width="{width}" height="{height}" rx="18" fill="url(#{prefix}-dots)"/>
  <path d="M 18 0.8 H {width - 18}" stroke="url(#{prefix}-rim)" stroke-width="1.6"/>"""


def render_streak_banner_svg(m: dict) -> str:
    st = m["streaks"]
    ring_pct = min(max(st["current"] / max(st["longest"], 14), 0.12), 1.0)
    circumference = 2 * 3.14159 * 48
    dash = circumference * ring_pct

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="196" viewBox="0 0 1200 196" role="img" aria-label="All-time contributions and streak telemetry for {USERNAME}">
{obsidian_defs("stk", 1200, 196)}
  <g font-family="{FONT_SANS}">
    <!-- Panel 1: All-Time Contributions -->
    <g transform="translate(0, 0)">
      <text x="200" y="54" fill="#42d6c5" font-family="{FONT_MONO}" font-size="11" font-weight="700" letter-spacing="2" text-anchor="middle">ALL-TIME CONTRIBUTIONS</text>
      <text x="200" y="114" fill="#f3f8ff" font-size="46" font-weight="800" text-anchor="middle">{m['all_time_total']:,}</text>
      <text x="200" y="145" fill="#8ea4c8" font-size="13" text-anchor="middle">{html.escape(st['first_active'])} – Present</text>
      <rect x="122" y="158" width="156" height="22" rx="11" fill="#102932" stroke="#42d6c5" stroke-opacity="0.35"/>
      <text x="200" y="173" fill="#8cf0e2" font-family="{FONT_MONO}" font-size="10.5" font-weight="600" text-anchor="middle">+{max(1000 - m['all_time_total'], 0)} TO 1,000 MILESTONE</text>
    </g>

    <line x1="400" y1="30" x2="400" y2="166" stroke="#1f314f" stroke-width="1.2"/>

    <!-- Panel 2: Active Streak Ring -->
    <g transform="translate(600, 96)">
      <circle cx="0" cy="-6" r="56" fill="#101f36" fill-opacity="0.7"/>
      <circle cx="0" cy="-6" r="48" fill="none" stroke="#1b2d4a" stroke-width="7"/>
      <circle cx="0" cy="-6" r="48" fill="none" stroke="url(#stk-ring)" stroke-width="7" stroke-linecap="round"
              stroke-dasharray="{dash:.1f} {circumference:.1f}" transform="rotate(-90 0 -6)"/>
      <!-- Flame badge -->
      <circle cx="0" cy="-54" r="12" fill="#0c1526" stroke="#42d6c5" stroke-width="1.4"/>
      <path d="M0 -61 C3 -56, 5 -54, 5 -51 C5 -48, 2.8 -46, 0 -46 C-2.8 -46, -5 -48, -5 -51 C-5 -53.5, -3 -56, 0 -61 Z" fill="#42d6c5"/>
      <text x="0" y="4" fill="#ffffff" font-size="30" font-weight="800" text-anchor="middle">{st['current']}</text>
      <text x="0" y="21" fill="#8cf0e2" font-family="{FONT_MONO}" font-size="9.5" font-weight="700" letter-spacing="1.2" text-anchor="middle">DAYS</text>
      <text x="0" y="64" fill="#eef4ff" font-size="14" font-weight="700" text-anchor="middle">Current Active Streak</text>
      <text x="0" y="83" fill="#8ea4c8" font-size="12" text-anchor="middle">{html.escape(st['current_range'])}</text>
    </g>

    <line x1="800" y1="30" x2="800" y2="166" stroke="#1f314f" stroke-width="1.2"/>

    <!-- Panel 3: Longest Streak & YTD -->
    <g transform="translate(800, 0)">
      <text x="200" y="54" fill="#b58aff" font-family="{FONT_MONO}" font-size="11" font-weight="700" letter-spacing="2" text-anchor="middle">PEAK CONSISTENCY</text>
      <text x="200" y="114" fill="#f3f8ff" font-size="46" font-weight="800" text-anchor="middle">{st['longest']} <tspan font-size="20" fill="#b8c7e0" font-weight="600">days</tspan></text>
      <text x="200" y="145" fill="#8ea4c8" font-size="13" text-anchor="middle">Longest Streak · {html.escape(st['longest_range'])}</text>
      <rect x="112" y="158" width="176" height="22" rx="11" fill="#211a38" stroke="#b58aff" stroke-opacity="0.35"/>
      <text x="200" y="173" fill="#dfccff" font-family="{FONT_MONO}" font-size="10.5" font-weight="600" text-anchor="middle">{m['current_year']} YTD: {m['current_year_total']:,} CONTRIBUTIONS</text>
    </g>
  </g>
</svg>
"""


def render_stats_svg(m: dict) -> str:
    st = m["streaks"]
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="580" height="225" viewBox="0 0 580 225" role="img" aria-label="GitHub engineering metrics for {USERNAME}">
{obsidian_defs("stat", 580, 225)}
  <g font-family="{FONT_SANS}">
    <text x="26" y="34" fill="#42d6c5" font-family="{FONT_MONO}" font-size="10.5" font-weight="700" letter-spacing="2.2">LIVE TELEMETRY // 01</text>
    <text x="26" y="58" fill="#f2f7ff" font-size="18" font-weight="700">Contribution &amp; Repository Footprint</text>
    <rect x="430" y="20" width="124" height="22" rx="11" fill="#111e34" stroke="#283d60"/>
    <circle cx="443" cy="31" r="3.5" fill="#42d6c5"/>
    <text x="453" y="35" fill="#9db2d4" font-family="{FONT_MONO}" font-size="10">{html.escape(m['updated'])}</text>

    <g transform="translate(26, 78)">
      <rect width="166" height="58" rx="12" fill="#112038" stroke="#668cff" stroke-opacity="0.45"/>
      <text x="14" y="21" fill="#9db1d7" font-size="11" font-weight="500">Rolling 365 Days</text>
      <text x="14" y="46" fill="#f3f8ff" font-size="22" font-weight="800">{m['rolling_total']:,}</text>
    </g>

    <g transform="translate(207, 78)">
      <rect width="166" height="58" rx="12" fill="#102a31" stroke="#42d6c5" stroke-opacity="0.45"/>
      <text x="14" y="21" fill="#8ed4cc" font-size="11" font-weight="500">All-Time Total</text>
      <text x="14" y="46" fill="#b5fff4" font-size="22" font-weight="800">{m['all_time_total']:,}</text>
    </g>

    <g transform="translate(388, 78)">
      <rect width="166" height="58" rx="12" fill="#211a37" stroke="#b58aff" stroke-opacity="0.45"/>
      <text x="14" y="21" fill="#c0a8e8" font-size="11" font-weight="500">Active Days (1Y)</text>
      <text x="14" y="46" fill="#e6d4ff" font-size="22" font-weight="800">{st['active_days_365']}</text>
    </g>

    <g transform="translate(26, 150)">
      <rect width="166" height="50" rx="10" fill="#0e182a" stroke="#1f314f"/>
      <text x="14" y="19" fill="#7f93b2" font-size="11">{html.escape(m['repo_label'])}</text>
      <text x="14" y="39" fill="#d7e2ff" font-size="16" font-weight="700">{m['repo_count']}</text>
    </g>

    <g transform="translate(207, 150)">
      <rect width="166" height="50" rx="10" fill="#0e182a" stroke="#1f314f"/>
      <text x="14" y="19" fill="#7f93b2" font-size="11">Stars Earned</text>
      <text x="14" y="39" fill="#ffe0ad" font-size="16" font-weight="700">{m['stars']}</text>
    </g>

    <g transform="translate(388, 150)">
      <rect width="166" height="50" rx="10" fill="#0e182a" stroke="#1f314f"/>
      <text x="14" y="19" fill="#7f93b2" font-size="11">Followers</text>
      <text x="14" y="39" fill="#d7e2ff" font-size="16" font-weight="700">{m['followers']}</text>
    </g>
  </g>
</svg>
"""


def render_languages_svg(m: dict) -> str:
    langs = m["languages"]
    bar_width = 528.0
    x_cursor = 26.0
    segments = []
    for idx, item in enumerate(langs):
        w = max((item["pct"] / 100.0) * bar_width, 4.0)
        if idx == len(langs) - 1:
            w = max(26.0 + bar_width - x_cursor, 4.0)
        segments.append(
            f'<rect x="{x_cursor:.1f}" y="76" width="{w:.1f}" height="12" fill="{item["color"]}"/>'
        )
        x_cursor += w

    legend_items = []
    for idx, item in enumerate(langs):
        col = idx % 2
        row = idx // 2
        lx = 26 + col * 270
        ly = 118 + row * 32
        pct_bar_w = max((item["pct"] / 100.0) * 90.0, 3.0)
        legend_items.append(
            f"""    <g transform="translate({lx}, {ly})">
      <circle cx="6" cy="-4" r="5" fill="{item['color']}"/>
      <text x="18" y="0" fill="#e4edff" font-size="12.5" font-weight="600">{html.escape(item['name'])}</text>
      <text x="252" y="0" fill="#9db1d7" font-family="{FONT_MONO}" font-size="11.5" text-anchor="end">{item['pct']:.1f}%</text>
      <rect x="18" y="7" width="234" height="4.5" rx="2.2" fill="#152238"/>
      <rect x="18" y="7" width="{min(pct_bar_w * 2.6, 234.0):.1f}" height="4.5" rx="2.2" fill="{item['color']}"/>
    </g>"""
        )

    segments_svg = "\n      ".join(segments)
    legend_svg = "\n".join(legend_items)

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="580" height="225" viewBox="0 0 580 225" role="img" aria-label="Top programming languages for {USERNAME}">
{obsidian_defs("lang", 580, 225)}
  <clipPath id="lang-bar-clip">
    <rect x="26" y="76" width="528" height="12" rx="6"/>
  </clipPath>
  <g font-family="{FONT_SANS}">
    <text x="26" y="34" fill="#668cff" font-family="{FONT_MONO}" font-size="10.5" font-weight="700" letter-spacing="2.2">CODE DISTRIBUTION // 02</text>
    <text x="26" y="58" fill="#f2f7ff" font-size="18" font-weight="700">Primary Languages by Code Volume</text>

    <rect x="26" y="76" width="528" height="12" rx="6" fill="#152238"/>
    <g clip-path="url(#lang-bar-clip)">
      {segments_svg}
    </g>

{legend_svg}
  </g>
</svg>
"""


def smooth_svg_path(points: list[tuple[float, float]]) -> str:
    if not points:
        return ""
    if len(points) == 1:
        return f"M {points[0][0]:.1f} {points[0][1]:.1f}"
    parts = [f"M {points[0][0]:.1f} {points[0][1]:.1f}"]
    for i in range(len(points) - 1):
        p0 = points[max(i - 1, 0)]
        p1 = points[i]
        p2 = points[i + 1]
        p3 = points[min(i + 2, len(points) - 1)]
        cp1x = p1[0] + (p2[0] - p0[0]) / 6.0
        cp1y = p1[1] + (p2[1] - p0[1]) / 6.0
        cp2x = p2[0] - (p3[0] - p1[0]) / 6.0
        cp2y = p2[1] - (p3[1] - p1[1]) / 6.0
        # Clamp control point y within chart floor/ceiling so curves never dip below zero baseline
        baseline_y = max(pt[1] for pt in points)
        top_y = min(pt[1] for pt in points)
        cp1y = min(max(cp1y, top_y - 6), baseline_y)
        cp2y = min(max(cp2y, top_y - 6), baseline_y)
        parts.append(f"C {cp1x:.1f} {cp1y:.1f}, {cp2x:.1f} {cp2y:.1f}, {p2[0]:.1f} {p2[1]:.1f}")
    return " ".join(parts)


def render_velocity_svg(m: dict) -> str:
    series: list[tuple[str, int]] = m["series_31"]
    counts = [c for _, c in series]
    total_31 = sum(counts)
    peak = max(counts) if counts else 1
    y_max = max(((peak + 3) // 4) * 4, 8)

    left_x = 64.0
    right_x = 1156.0
    top_y = 84.0
    bottom_y = 228.0
    chart_w = right_x - left_x
    chart_h = bottom_y - top_y

    pts: list[tuple[float, float]] = []
    for idx, (_, cnt) in enumerate(series):
        x = left_x + (idx / max(len(series) - 1, 1)) * chart_w
        y = bottom_y - (cnt / y_max) * chart_h
        pts.append((x, y))

    curve = smooth_svg_path(pts)
    area = f"{curve} L {pts[-1][0]:.1f} {bottom_y:.1f} L {pts[0][0]:.1f} {bottom_y:.1f} Z"

    # Horizontal gridlines
    grid_lines = []
    for step in range(5):
        val = int(round((y_max / 4) * step))
        gy = bottom_y - (step / 4.0) * chart_h
        grid_lines.append(
            f'<line x1="{left_x:.1f}" y1="{gy:.1f}" x2="{right_x:.1f}" y2="{gy:.1f}" stroke="#192942" stroke-dasharray="4 4"/>'
            f'<text x="{left_x - 12:.1f}" y="{gy + 4:.1f}" fill="#6e84a6" font-family="{FONT_MONO}" font-size="10.5" text-anchor="end">{val}</text>'
        )

    # X-axis labels & nodes
    nodes_svg = []
    x_labels = []
    for idx, ((d_iso, cnt), (px, py)) in enumerate(zip(series, pts)):
        d_obj = dt.date.fromisoformat(d_iso)
        if idx % 3 == 0 or idx == len(series) - 1:
            lbl = d_obj.strftime("%b %d") if (idx == 0 or d_obj.day == 1 or idx == len(series) - 1) else str(d_obj.day)
            x_labels.append(
                f'<text x="{px:.1f}" y="{bottom_y + 22:.1f}" fill="#7f95b8" font-family="{FONT_MONO}" font-size="10" text-anchor="middle">{lbl}</text>'
            )
        dot_fill = "#42d6c5" if cnt > 0 else "#1c2d48"
        dot_r = "4.2" if cnt >= peak and peak > 0 else ("3.2" if cnt > 0 else "2.3")
        nodes_svg.append(
            f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{dot_r}" fill="{dot_fill}" stroke="#08101e" stroke-width="1.4"/>'
        )
        if cnt > 0 and (cnt == peak or cnt >= max(peak * 0.6, 6)):
            nodes_svg.append(
                f'<text x="{px:.1f}" y="{py - 9:.1f}" fill="#b5fff4" font-family="{FONT_MONO}" font-size="10" font-weight="700" text-anchor="middle">{cnt}</text>'
            )

    grid_block = "\n    ".join(grid_lines)
    labels_block = "\n    ".join(x_labels)
    nodes_block = "\n    ".join(nodes_svg)

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="276" viewBox="0 0 1200 276" role="img" aria-label="31-day contribution velocity graph for {USERNAME}">
{obsidian_defs("vel", 1200, 276)}
  <defs>
    <linearGradient id="vel-area" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#42d6c5" stop-opacity="0.34"/>
      <stop offset="65%" stop-color="#668cff" stop-opacity="0.10"/>
      <stop offset="100%" stop-color="#0c1424" stop-opacity="0.0"/>
    </linearGradient>
    <linearGradient id="vel-stroke" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#668cff"/>
      <stop offset="55%" stop-color="#42d6c5"/>
      <stop offset="100%" stop-color="#b58aff"/>
    </linearGradient>
  </defs>
  <g font-family="{FONT_SANS}">
    <text x="32" y="34" fill="#42d6c5" font-family="{FONT_MONO}" font-size="10.5" font-weight="700" letter-spacing="2.2">CONTRIBUTION VELOCITY // LAST 31 DAYS</text>
    <text x="32" y="58" fill="#f2f7ff" font-size="18" font-weight="700">Daily Engineering Activity (Public + Private Repositories)</text>

    <rect x="938" y="22" width="228" height="32" rx="16" fill="#102338" stroke="#42d6c5" stroke-opacity="0.4"/>
    <text x="1052" y="42" fill="#9cf2e6" font-family="{FONT_MONO}" font-size="11" font-weight="700" text-anchor="middle">31-DAY OUTPUT: {total_31} · PEAK: {peak}/DAY</text>

    {grid_block}
    <path d="{area}" fill="url(#vel-area)"/>
    <path d="{curve}" fill="none" stroke="url(#vel-stroke)" stroke-width="2.8" stroke-linecap="round"/>
    {nodes_block}
    {labels_block}
  </g>
</svg>
"""


def main() -> None:
    token = os.environ.get("STATS_TOKEN") or os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        raise SystemExit("Missing STATS_TOKEN / GITHUB_TOKEN / GH_TOKEN environment variable.")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    metrics = fetch_metrics(token)

    (OUT_DIR / "streak-banner.svg").write_text(render_streak_banner_svg(metrics), encoding="utf-8")
    (OUT_DIR / "github-stats.svg").write_text(render_stats_svg(metrics), encoding="utf-8")
    (OUT_DIR / "top-languages.svg").write_text(render_languages_svg(metrics), encoding="utf-8")
    (OUT_DIR / "activity-velocity.svg").write_text(render_velocity_svg(metrics), encoding="utf-8")

    print(
        f"Generated 4 telemetry SVGs: all_time={metrics['all_time_total']}, "
        f"rolling={metrics['rolling_total']}, ytd={metrics['current_year_total']}, "
        f"streak={metrics['streaks']['current']}d (max {metrics['streaks']['longest']}d)"
    )


if __name__ == "__main__":
    main()
