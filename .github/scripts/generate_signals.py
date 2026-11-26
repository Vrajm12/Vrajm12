#!/usr/bin/env python3
"""Generate native SVG GitHub signal cards from live GitHub API data for Vrajm12/Vrajm12."""

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


def http_get(url: str, headers: dict[str, str] | None = None) -> str:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": f"{USERNAME}-profile-signals-generator",
            **(headers or {}),
        },
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        return resp.read().decode("utf-8", errors="replace")


def graphql(query: str, token: str) -> dict:
    payload = json.dumps({"query": query}).encode("utf-8")
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": f"{USERNAME}-profile-signals-generator",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=25) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    if "errors" in data:
        raise RuntimeError(f"GraphQL error: {data['errors']}")
    return data["data"]


def parse_public_contributions_html(fragment: str) -> int | None:
    normalized = " ".join(fragment.split())
    match = re.search(r"([\d,]+)\s+contributions?\s+in\s+", normalized, re.I)
    if match:
        return int(match.group(1).replace(",", ""))
    return None


def fetch_profile_contribution_totals(current_year: int) -> tuple[int | None, dict[int, int]]:
    """Read GitHub's public profile contributions endpoint (respects user's 'Include private contributions' setting)."""
    rolling = None
    try:
        frag = http_get(f"https://github.com/users/{USERNAME}/contributions")
        rolling = parse_public_contributions_html(frag)
    except Exception:
        pass

    yearly: dict[int, int] = {}
    for year in range(START_YEAR, current_year + 1):
        try:
            url = f"https://github.com/users/{USERNAME}/contributions?from={year}-01-01&to={year}-12-31"
            frag = http_get(url)
            val = parse_public_contributions_html(frag)
            if val is not None:
                yearly[year] = val
        except Exception:
            continue
    return rolling, yearly


def fetch_metrics(token: str) -> dict:
    now = dt.datetime.now(dt.timezone.utc)
    current_year = now.year

    use_viewer = False
    try:
        who = graphql("query { viewer { login } }", token)
        use_viewer = who["viewer"]["login"].lower() == USERNAME.lower()
    except Exception:
        use_viewer = False

    year_blocks = "\n".join(
        f'y{y}: contributionsCollection(from: "{y}-01-01T00:00:00Z", to: "{y}-12-31T23:59:59Z") {{ contributionCalendar {{ totalContributions }} }}'
        for y in range(START_YEAR, current_year + 1)
    )

    repo_filter = "" if use_viewer else ", privacy: PUBLIC"
    subject_root = "viewer" if use_viewer else f'user(login: "{USERNAME}")'

    query = f"""
    query {{
      subject: {subject_root} {{
        followers {{ totalCount }}
        rolling: contributionsCollection {{
          contributionCalendar {{ totalContributions }}
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
    gql_rolling = subj["rolling"]["contributionCalendar"]["totalContributions"]
    gql_yearly = {
        y: subj[f"y{y}"]["contributionCalendar"]["totalContributions"]
        for y in range(START_YEAR, current_year + 1)
    }

    html_rolling, html_yearly = fetch_profile_contribution_totals(current_year)

    rolling_total = max(gql_rolling, html_rolling or 0)
    yearly_totals = {
        y: max(gql_yearly.get(y, 0), html_yearly.get(y, 0))
        for y in range(START_YEAR, current_year + 1)
    }
    all_time_total = sum(yearly_totals.values())
    current_year_total = yearly_totals.get(current_year, 0)

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
        "repo_count": repo_count,
        "repo_label": "Owned Repos" if use_viewer else "Public Repos",
        "stars": total_stars,
        "followers": subj["followers"]["totalCount"],
        "languages": languages,
        "updated": now.strftime("%b %d, %Y"),
    }


def render_stats_svg(m: dict) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="580" height="215" viewBox="0 0 580 215" role="img" aria-label="GitHub engineering metrics for {USERNAME}">
  <rect width="580" height="215" rx="18" fill="#0c1422" stroke="#293a55"/>
  <g font-family="Segoe UI, Arial, sans-serif">
    <text x="26" y="34" fill="#42d6c5" font-size="11" font-weight="700" letter-spacing="2.5">GITHUB TELEMETRY</text>
    <text x="26" y="57" fill="#eef4ff" font-size="18" font-weight="700">Contribution &amp; Repository Overview</text>
    <text x="554" y="34" fill="#7f93b2" font-size="11" text-anchor="end">Synced {html.escape(m['updated'])}</text>

    <g transform="translate(26, 76)">
      <rect width="166" height="54" rx="12" fill="#132238" stroke="#668cff" stroke-opacity=".45"/>
      <text x="14" y="21" fill="#9db1d7" font-size="11">Last 365 Days</text>
      <text x="14" y="43" fill="#eef4ff" font-size="20" font-weight="800">{m['rolling_total']:,}</text>
    </g>

    <g transform="translate(207, 76)">
      <rect width="166" height="54" rx="12" fill="#122d33" stroke="#42d6c5" stroke-opacity=".45"/>
      <text x="14" y="21" fill="#8ed4cc" font-size="11">All-Time Total</text>
      <text x="14" y="43" fill="#b5fff4" font-size="20" font-weight="800">{m['all_time_total']:,}</text>
    </g>

    <g transform="translate(388, 76)">
      <rect width="166" height="54" rx="12" fill="#231c38" stroke="#b58aff" stroke-opacity=".45"/>
      <text x="14" y="21" fill="#c0a8e8" font-size="11">{m['current_year']} YTD</text>
      <text x="14" y="43" fill="#e6d4ff" font-size="20" font-weight="800">{m['current_year_total']:,}</text>
    </g>

    <g transform="translate(26, 143)">
      <rect width="166" height="48" rx="10" fill="#111b2d" stroke="#243550"/>
      <text x="14" y="19" fill="#7f93b2" font-size="11">{html.escape(m['repo_label'])}</text>
      <text x="14" y="38" fill="#d7e2ff" font-size="16" font-weight="700">{m['repo_count']}</text>
    </g>

    <g transform="translate(207, 143)">
      <rect width="166" height="48" rx="10" fill="#111b2d" stroke="#243550"/>
      <text x="14" y="19" fill="#7f93b2" font-size="11">Stars Earned</text>
      <text x="14" y="38" fill="#ffe0ad" font-size="16" font-weight="700">{m['stars']}</text>
    </g>

    <g transform="translate(388, 143)">
      <rect width="166" height="48" rx="10" fill="#111b2d" stroke="#243550"/>
      <text x="14" y="19" fill="#7f93b2" font-size="11">Followers</text>
      <text x="14" y="38" fill="#d7e2ff" font-size="16" font-weight="700">{m['followers']}</text>
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
            f'<rect x="{x_cursor:.1f}" y="74" width="{w:.1f}" height="12" fill="{item["color"]}"/>'
        )
        x_cursor += w

    legend_items = []
    for idx, item in enumerate(langs):
        col = idx % 2
        row = idx // 2
        lx = 26 + col * 270
        ly = 114 + row * 31
        pct_bar_w = max((item["pct"] / 100.0) * 90.0, 3.0)
        legend_items.append(
            f"""    <g transform="translate({lx}, {ly})">
      <circle cx="6" cy="-4" r="5" fill="{item['color']}"/>
      <text x="18" y="0" fill="#d7e2ff" font-size="12.5" font-weight="600">{html.escape(item['name'])}</text>
      <text x="248" y="0" fill="#9db1d7" font-size="12" text-anchor="end">{item['pct']:.1f}%</text>
      <rect x="18" y="7" width="230" height="4" rx="2" fill="#17243a"/>
      <rect x="18" y="7" width="{min(pct_bar_w * 2.55, 230.0):.1f}" height="4" rx="2" fill="{item['color']}"/>
    </g>"""
        )

    segments_svg = "\n      ".join(segments)
    legend_svg = "\n".join(legend_items)

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="580" height="215" viewBox="0 0 580 215" role="img" aria-label="Top programming languages for {USERNAME}">
  <defs>
    <clipPath id="lang-bar-clip">
      <rect x="26" y="74" width="528" height="12" rx="6"/>
    </clipPath>
  </defs>
  <rect width="580" height="215" rx="18" fill="#0c1422" stroke="#293a55"/>
  <g font-family="Segoe UI, Arial, sans-serif">
    <text x="26" y="34" fill="#668cff" font-size="11" font-weight="700" letter-spacing="2.5">CODE DISTRIBUTION</text>
    <text x="26" y="57" fill="#eef4ff" font-size="18" font-weight="700">Top Languages Across Repositories</text>

    <rect x="26" y="74" width="528" height="12" rx="6" fill="#17243a"/>
    <g clip-path="url(#lang-bar-clip)">
      {segments_svg}
    </g>

{legend_svg}
  </g>
</svg>
"""


def main() -> None:
    token = os.environ.get("STATS_TOKEN") or os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        raise SystemExit("Missing STATS_TOKEN / GITHUB_TOKEN / GH_TOKEN environment variable.")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    metrics = fetch_metrics(token)
    (OUT_DIR / "github-stats.svg").write_text(render_stats_svg(metrics), encoding="utf-8")
    (OUT_DIR / "top-languages.svg").write_text(render_languages_svg(metrics), encoding="utf-8")
    print(
        f"Generated SVGs: rolling={metrics['rolling_total']}, all_time={metrics['all_time_total']}, "
        f"repos={metrics['repo_count']} ({metrics['repo_label']}), langs={[l['name'] for l in metrics['languages']]}"
    )


if __name__ == "__main__":
    main()
