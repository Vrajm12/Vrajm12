#!/usr/bin/env python3
"""Build cohesive Obsidian-styled static SVG identity, architecture, and project assets."""

from __future__ import annotations

import html
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "assets"

FONT_SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Inter, Roboto, Helvetica, Arial, sans-serif"
FONT_MONO = "'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace"


def frame_defs(prefix: str, w: int, h: int, rx: int = 20) -> str:
    return f"""  <defs>
    <linearGradient id="{prefix}-bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#060a13"/>
      <stop offset="52%" stop-color="#0b1323"/>
      <stop offset="100%" stop-color="#101c33"/>
    </linearGradient>
    <linearGradient id="{prefix}-rim" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#42d6c5" stop-opacity="0.8"/>
      <stop offset="50%" stop-color="#668cff" stop-opacity="0.8"/>
      <stop offset="100%" stop-color="#b58aff" stop-opacity="0.8"/>
    </linearGradient>
    <pattern id="{prefix}-grid" width="28" height="28" patternUnits="userSpaceOnUse">
      <path d="M 28 0 L 0 0 0 28" fill="none" stroke="#8aa4c8" stroke-opacity="0.06"/>
    </pattern>
  </defs>
  <rect width="{w}" height="{h}" rx="{rx}" fill="url(#{prefix}-bg)" stroke="#1e304d" stroke-width="1.2"/>
  <rect width="{w}" height="{h}" rx="{rx}" fill="url(#{prefix}-grid)"/>
  <path d="M {rx} 0.9 H {w - rx}" stroke="url(#{prefix}-rim)" stroke-width="1.8"/>"""


def build_hero() -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="365" viewBox="0 0 1200 365" role="img" aria-label="Veeraj Matnale — Systems Architect, Product Engineer, Security Researcher">
{frame_defs("hero", 1200, 365, 22)}
  <defs>
    <radialGradient id="hero-glow" cx="0.82" cy="0.48" r="0.42">
      <stop offset="0%" stop-color="#42d6c5" stop-opacity="0.18"/>
      <stop offset="48%" stop-color="#668cff" stop-opacity="0.10"/>
      <stop offset="100%" stop-color="#060a13" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="hero-name" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#ffffff"/>
      <stop offset="68%" stop-color="#e8f1ff"/>
      <stop offset="100%" stop-color="#9ec5ff"/>
    </linearGradient>
  </defs>
  <rect width="1200" height="365" rx="22" fill="url(#hero-glow)"/>

  <!-- Right Architectural Topology Radar -->
  <g transform="translate(988, 182)">
    <circle cx="0" cy="0" r="138" fill="none" stroke="#1f3456" stroke-width="1" stroke-dasharray="4 6"/>
    <circle cx="0" cy="0" r="102" fill="none" stroke="#42d6c5" stroke-opacity="0.32" stroke-width="1.2"/>
    <circle cx="0" cy="0" r="66" fill="none" stroke="#668cff" stroke-opacity="0.45" stroke-width="1.4"/>
    <circle cx="0" cy="0" r="28" fill="#10253a" stroke="#42d6c5" stroke-width="1.6"/>
    <circle cx="0" cy="0" r="6" fill="#42d6c5"/>
    <path d="M-148 0 H148 M0 -148 V148 M-98 -98 L98 98 M98 -98 L-98 98" stroke="#6f91c7" stroke-opacity="0.14"/>

    <!-- Satellite Nodes -->
    <g font-family="{FONT_MONO}" font-size="9.5" font-weight="700" text-anchor="middle">
      <rect x="-34" y="-122" width="68" height="22" rx="11" fill="#0d2330" stroke="#42d6c5"/>
      <text x="0" y="-107" fill="#9cf2e6">SAAS / ERP</text>

      <rect x="66" y="-11" width="72" height="22" rx="11" fill="#132240" stroke="#668cff"/>
      <text x="102" y="4" fill="#c4d4ff">ZERO-TRUST</text>

      <rect x="-34" y="98" width="68" height="22" rx="11" fill="#23193a" stroke="#b58aff"/>
      <text x="0" y="113" fill="#e2cfff">AGENTIC AI</text>

      <rect x="-138" y="-11" width="72" height="22" rx="11" fill="#2b2116" stroke="#e8ad5a"/>
      <text x="-102" y="4" fill="#ffe1ad">UX SYSTEMS</text>
    </g>
  </g>

  <!-- Left Typography & Identity -->
  <g font-family="{FONT_SANS}">
    <rect x="56" y="42" width="448" height="28" rx="14" fill="#0e2034" stroke="#284366"/>
    <circle cx="74" cy="56" r="4.2" fill="#42d6c5"/>
    <text x="88" y="60" fill="#9cf2e6" font-family="{FONT_MONO}" font-size="11" font-weight="700" letter-spacing="1.4">FOUNDER &amp; CEO · TRIVERSE SOLUTIONS · PUNE, INDIA</text>

    <text x="54" y="146" fill="url(#hero-name)" font-size="64" font-weight="800" letter-spacing="-1.8">VEERAJ MATNALE</text>
    <text x="58" y="186" fill="#c9d8f0" font-size="22" font-weight="600">Systems Architect  <tspan fill="#42d6c5">·</tspan>  Product Engineer  <tspan fill="#668cff">·</tspan>  Security Researcher</text>
    <text x="58" y="220" fill="#899fc0" font-size="14.5">I design and ship the operational layer between what a business intends and what its software reliably executes.</text>

    <!-- Capability Pills -->
    <g transform="translate(58, 250)" font-family="{FONT_MONO}" font-size="11" font-weight="700" text-anchor="middle">
      <rect x="0" y="0" width="184" height="34" rx="17" fill="#0f2b33" stroke="#42d6c5" stroke-opacity="0.55"/>
      <text x="92" y="21" fill="#94f3e5">MULTI-TENANT PLATFORMS</text>

      <rect x="196" y="0" width="186" height="34" rx="17" fill="#132342" stroke="#668cff" stroke-opacity="0.55"/>
      <text x="289" y="21" fill="#c2d2ff">IOT &amp; CYBER RESILIENCE</text>

      <rect x="394" y="0" width="170" height="34" rx="17" fill="#231a3a" stroke="#b58aff" stroke-opacity="0.55"/>
      <text x="479" y="21" fill="#e1ceff">AI AGENT HARNESSES</text>

      <rect x="576" y="0" width="154" height="34" rx="17" fill="#2a2117" stroke="#e8ad5a" stroke-opacity="0.55"/>
      <text x="653" y="21" fill="#ffdfaa">DESIGN × DELIVERY</text>
    </g>

    <line x1="58" y1="308" x2="788" y2="308" stroke="#1b2c47"/>
    <text x="58" y="332" fill="#6f85a8" font-family="{FONT_MONO}" font-size="11" letter-spacing="1.3">VEERAJMATNALE.ME   //   TRIVERSESOLUTIONS.CO.IN   //   ORCID 0009-0009-4414-2901</text>
  </g>
</svg>
"""


def build_signature() -> str:
    stages = [
        ("01", "FRAME", "Boundaries & intent", "#42d6c5", "#0f2a32", "#9cf2e6"),
        ("02", "ARCHITECT", "Contracts & isolation", "#668cff", "#132342", "#c4d4ff"),
        ("03", "ENGINEER", "Clean domain delivery", "#b58aff", "#231a3a", "#e3d0ff"),
        ("04", "HARDEN", "Authz, tests & audit", "#e8ad5a", "#2b2116", "#ffe0ad"),
        ("05", "OPERATE", "Observe & iterate", "#42d6c5", "#0f2a32", "#9cf2e6"),
    ]
    cards = []
    arrows = []
    start_x = 308
    step_w = 158
    gap = 18
    for idx, (num, title, sub, stroke, fill, txt) in enumerate(stages):
        x = start_x + idx * (step_w + gap)
        cards.append(
            f"""    <g transform="translate({x}, 26)">
      <rect width="{step_w}" height="82" rx="13" fill="{fill}" stroke="{stroke}" stroke-opacity="0.6"/>
      <text x="14" y="24" fill="{stroke}" font-family="{FONT_MONO}" font-size="10" font-weight="700" letter-spacing="1.4">STAGE {num}</text>
      <text x="14" y="48" fill="{txt}" font-size="15" font-weight="800">{html.escape(title)}</text>
      <text x="14" y="68" fill="#8ea5c7" font-size="11.5">{html.escape(sub)}</text>
    </g>"""
        )
        if idx < len(stages) - 1:
            ax = x + step_w + 3
            arrows.append(
                f'<path d="M {ax} 67 H {ax + gap - 6} m -4 -4 l 4 4 l -4 4" fill="none" stroke="#5c769d" stroke-width="1.6" stroke-linecap="round"/>'
            )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="134" viewBox="0 0 1200 134" role="img" aria-label="Engineering execution loop">
{frame_defs("sig", 1200, 134, 18)}
  <g font-family="{FONT_SANS}">
    <text x="30" y="42" fill="#42d6c5" font-family="{FONT_MONO}" font-size="10.5" font-weight="700" letter-spacing="2.2">EXECUTION DOCTRINE</text>
    <text x="30" y="68" fill="#f1f6ff" font-size="20" font-weight="800">Engineering Loop</text>
    <text x="30" y="92" fill="#849ab9" font-size="12.5">Repeatable delivery from ambiguity</text>
    <text x="30" y="109" fill="#849ab9" font-size="12.5">to production-grade systems.</text>
{chr(10).join(cards)}
    {chr(10).join(arrows)}
  </g>
</svg>
"""


def build_pipeline_diagram(
    prefix: str,
    eyebrow: str,
    title: str,
    subtitle: str,
    nodes: list[tuple[str, str, list[str], str, str, str]],
    footer_note: str | None = None,
) -> str:
    h = 290 if footer_note else 255
    n = len(nodes)
    margin = 30
    gap = 22
    usable = 1200 - 2 * margin - (n - 1) * gap
    box_w = usable / n

    boxes = []
    arrows = []
    for idx, (tag, head, lines, stroke, fill, head_fill) in enumerate(nodes):
        x = margin + idx * (box_w + gap)
        line_elems = "".join(
            f'<text x="{box_w/2:.1f}" y="{76 + li*20}" fill="#9eb3d4" font-size="12" text-anchor="middle">{html.escape(ln)}</text>'
            for li, ln in enumerate(lines)
        )
        box_h = 118 if len(lines) <= 2 else 132
        y = 94 if box_h == 118 else 87
        boxes.append(
            f"""    <g transform="translate({x:.1f}, {y})">
      <rect width="{box_w:.1f}" height="{box_h}" rx="14" fill="{fill}" stroke="{stroke}" stroke-opacity="0.65"/>
      <text x="{box_w/2:.1f}" y="24" fill="{stroke}" font-family="{FONT_MONO}" font-size="10" font-weight="700" letter-spacing="1.5" text-anchor="middle">{html.escape(tag)}</text>
      <text x="{box_w/2:.1f}" y="50" fill="{head_fill}" font-size="14.5" font-weight="800" text-anchor="middle">{html.escape(head)}</text>
      {line_elems}
    </g>"""
        )
        if idx < n - 1:
            ax1 = x + box_w + 3
            ax2 = x + box_w + gap - 3
            arrows.append(
                f'<path d="M {ax1:.1f} 153 H {ax2:.1f} m -5 -4.5 l 5 4.5 l -5 4.5" fill="none" stroke="#6882a8" stroke-width="1.8" stroke-linecap="round"/>'
            )

    footer_svg = ""
    if footer_note:
        footer_svg = f"""
    <rect x="30" y="236" width="1140" height="34" rx="10" fill="#0d182b" stroke="#1f3250"/>
    <text x="600" y="258" fill="#92a8ca" font-family="{FONT_MONO}" font-size="11" text-anchor="middle">{html.escape(footer_note)}</text>"""

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="{h}" viewBox="0 0 1200 {h}" role="img" aria-label="{html.escape(title)}">
{frame_defs(prefix, 1200, h, 18)}
  <g font-family="{FONT_SANS}">
    <text x="30" y="34" fill="#42d6c5" font-family="{FONT_MONO}" font-size="10.5" font-weight="700" letter-spacing="2.2">{html.escape(eyebrow)}</text>
    <text x="30" y="58" fill="#f2f7ff" font-size="18.5" font-weight="800">{html.escape(title)}</text>
    <text x="1170" y="56" fill="#7f95b8" font-size="12" text-anchor="end">{html.escape(subtitle)}</text>
{chr(10).join(boxes)}
    {chr(10).join(arrows)}{footer_svg}
  </g>
</svg>
"""


def build_project_card(
    slug: str,
    category: str,
    title: str,
    subtitle: str,
    pills: list[str],
    accent: str,
    surface: str,
    badge_bg: str,
) -> str:
    pill_elems = []
    px = 28
    for p in pills:
        pw = len(p) * 7.6 + 22
        pill_elems.append(
            f'<rect x="{px:.0f}" y="198" width="{pw:.0f}" height="26" rx="13" fill="{badge_bg}" stroke="{accent}" stroke-opacity="0.4"/>'
            f'<text x="{px + pw/2:.1f}" y="215" fill="#dce7fb" font-family="{FONT_MONO}" font-size="10.5" font-weight="600" text-anchor="middle">{html.escape(p)}</text>'
        )
        px += pw + 10

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="600" height="252" viewBox="0 0 600 252" role="img" aria-label="{html.escape(title)}">
  <defs>
    <linearGradient id="{slug}-bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#070c16"/>
      <stop offset="55%" stop-color="{surface}"/>
      <stop offset="100%" stop-color="#0b1324"/>
    </linearGradient>
    <pattern id="{slug}-dots" width="22" height="22" patternUnits="userSpaceOnUse">
      <circle cx="2" cy="2" r="1" fill="#9bb4d8" fill-opacity="0.08"/>
    </pattern>
  </defs>
  <rect width="600" height="252" rx="18" fill="url(#{slug}-bg)" stroke="{accent}" stroke-opacity="0.5" stroke-width="1.2"/>
  <rect width="600" height="252" rx="18" fill="url(#{slug}-dots)"/>
  <path d="M 18 1 H 582" stroke="{accent}" stroke-opacity="0.85" stroke-width="1.8"/>

  <!-- Geometric Motif -->
  <circle cx="522" cy="66" r="96" fill="{accent}" fill-opacity="0.07"/>
  <circle cx="522" cy="66" r="62" fill="none" stroke="{accent}" stroke-opacity="0.24"/>
  <circle cx="522" cy="66" r="28" fill="none" stroke="{accent}" stroke-opacity="0.38" stroke-dasharray="4 4"/>
  <path d="M432 34 H576 M456 66 H576 M482 98 H576" stroke="{accent}" stroke-opacity="0.22"/>

  <g font-family="{FONT_SANS}">
    <rect x="28" y="24" width="{len(category)*8.2 + 24:.0f}" height="24" rx="12" fill="{badge_bg}" stroke="{accent}" stroke-opacity="0.45"/>
    <text x="{28 + (len(category)*8.2 + 24)/2:.1f}" y="40" fill="{accent}" font-family="{FONT_MONO}" font-size="10.5" font-weight="700" letter-spacing="1.4" text-anchor="middle">{html.escape(category)}</text>

    <text x="28" y="102" fill="#f4f8ff" font-size="31" font-weight="800" letter-spacing="-0.6">{html.escape(title)}</text>
    <text x="28" y="136" fill="#bfd0ea" font-size="15.5" font-weight="500">{html.escape(subtitle)}</text>
    <line x1="28" y1="176" x2="572" y2="176" stroke="#1e314f"/>
    {"".join(pill_elems)}
  </g>
</svg>
"""


def build_tech_map() -> str:
    rows = [
        ("LANGUAGES", "#42d6c5", "#0f2a32", ["TypeScript", "Python", "JavaScript", "C++", "C", "Dart", "SQL", "HTML / CSS"]),
        ("FRONTEND & MOBILE", "#668cff", "#132342", ["Next.js", "React", "Flutter", "React Native", "Tailwind CSS", "Vite", "Design Systems"]),
        ("BACKEND & CLOUD", "#b58aff", "#221939", ["NestJS", "Node.js", "FastAPI", "Flask", "REST / GraphQL", "Docker", "Linux", "Azure"]),
        ("DATA, AI & SEC", "#e8ad5a", "#2a2016", ["PostgreSQL", "Prisma", "Redis", "MongoDB", "MCP Servers", "Ollama", "n8n", "ETSI / Zero-Trust"]),
    ]
    row_elems = []
    for idx, (label, accent, bg, items) in enumerate(rows):
        ry = 86 + idx * 54
        pills = []
        px = 238.0
        for it in items:
            pw = len(it) * 7.7 + 26
            pills.append(
                f'<rect x="{px:.1f}" y="{ry}" width="{pw:.1f}" height="36" rx="10" fill="{bg}" stroke="{accent}" stroke-opacity="0.45"/>'
                f'<text x="{px + pw/2:.1f}" y="{ry + 23}" fill="#e6f0ff" font-family="{FONT_MONO}" font-size="11.5" font-weight="600" text-anchor="middle">{html.escape(it)}</text>'
            )
            px += pw + 10
        row_elems.append(
            f'<text x="32" y="{ry + 23}" fill="{accent}" font-family="{FONT_MONO}" font-size="11.5" font-weight="700" letter-spacing="1.4">{html.escape(label)}</text>'
            + "".join(pills)
        )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="318" viewBox="0 0 1200 318" role="img" aria-label="Technology stack matrix">
{frame_defs("tech", 1200, 318, 18)}
  <g font-family="{FONT_SANS}">
    <text x="32" y="34" fill="#42d6c5" font-family="{FONT_MONO}" font-size="10.5" font-weight="700" letter-spacing="2.2">CAPABILITY STACK</text>
    <text x="32" y="58" fill="#f2f7ff" font-size="18.5" font-weight="800">Production Toolkit — Selected by Problem Boundary, Not Hype</text>
    {chr(10).join(row_elems)}
  </g>
</svg>
"""


def main() -> None:
    (ASSETS / "identity").mkdir(parents=True, exist_ok=True)
    (ASSETS / "architecture").mkdir(parents=True, exist_ok=True)
    (ASSETS / "projects").mkdir(parents=True, exist_ok=True)
    (ASSETS / "visuals").mkdir(parents=True, exist_ok=True)

    (ASSETS / "identity" / "hero.svg").write_text(build_hero(), encoding="utf-8")
    (ASSETS / "identity" / "signature.svg").write_text(build_signature(), encoding="utf-8")

    (ASSETS / "architecture" / "system-design.svg").write_text(
        build_pipeline_diagram(
            "sys",
            "REFERENCE ARCHITECTURE // 01",
            "TriHub Multi-Tenant Platform Topology",
            "Logical request-to-worker execution plane",
            [
                ("SURFACE", "CLIENTS", ["Next.js Web", "Flutter Mobile"], "#668cff", "#12223d", "#dce8ff"),
                ("INGRESS", "EDGE / API", ["AuthN & JWT", "Rate & Tenant Guards"], "#42d6c5", "#0f2a32", "#b5fff4"),
                ("CORE", "DOMAIN ENGINE", ["NestJS Modules", "RBAC & Policies"], "#668cff", "#142442", "#dce8ff"),
                ("STATE", "PERSISTENCE", ["PostgreSQL · Prisma", "Redis Cache"], "#b58aff", "#22193a", "#e8d6ff"),
                ("ASYNC", "OUTBOX & JOBS", ["Transactional Events", "Realtime & Workers"], "#e8ad5a", "#2a2016", "#ffe1ad"),
            ],
            "CROSS-CUTTING TELEMETRY  ·  STRUCTURED AUDIT LOGS  ·  IDEMPOTENT RETRIES  ·  TENANT-SCOPED OBSERVABILITY",
        ),
        encoding="utf-8",
    )

    (ASSETS / "architecture" / "multi-tenancy.svg").write_text(
        build_pipeline_diagram(
            "mt",
            "ISOLATION MODEL // 02",
            "Zero-Trust Multi-Tenant Request Path",
            "Context resolved once and enforced server-side",
            [
                ("STEP 01", "INGRESS", ["Host / Header", "Signed Claims"], "#668cff", "#12223d", "#dce8ff"),
                ("STEP 02", "RESOLVE", ["Tenant Lookup", "Status Check"], "#42d6c5", "#0f2a32", "#b5fff4"),
                ("STEP 03", "AUTHORIZE", ["Role + Permission", "Tenant Boundary Guard"], "#b58aff", "#22193a", "#e8d6ff"),
                ("STEP 04", "SCOPE QUERY", ["Mandatory companyId", "Prisma / SQL Filter"], "#668cff", "#142442", "#dce8ff"),
                ("STEP 05", "ISOLATED IO", ["Zero Cross-Tenant Leak", "Scoped Cache Keys"], "#42d6c5", "#0f2a32", "#b5fff4"),
            ],
        ),
        encoding="utf-8",
    )

    (ASSETS / "architecture" / "security.svg").write_text(
        build_pipeline_diagram(
            "sec",
            "DEFENSE IN DEPTH // 03",
            "Security as an Architectural Property",
            "Layered controls across identity, schema, and runtime",
            [
                ("LAYER 01", "IDENTITY", ["Verified Sessions", "Token Rotation"], "#668cff", "#12223d", "#dce8ff"),
                ("LAYER 02", "ACCESS", ["Least-Privilege RBAC", "Policy Guards"], "#42d6c5", "#0f2a32", "#b5fff4"),
                ("LAYER 03", "BOUNDARY", ["Strict DTO Schemas", "Parameterized SQL"], "#b58aff", "#22193a", "#e8d6ff"),
                ("LAYER 04", "TELEMETRY", ["Rate Limiting", "Immutable Audit Trail"], "#e8ad5a", "#2a2016", "#ffe1ad"),
                ("LAYER 05", "RESILIENCE", ["Graceful Degradation", "Verified Recovery"], "#42d6c5", "#0f2a32", "#b5fff4"),
            ],
        ),
        encoding="utf-8",
    )

    (ASSETS / "architecture" / "data-flow.svg").write_text(
        build_pipeline_diagram(
            "df",
            "RELIABILITY // 04",
            "Transactional Outbox & Event Flow",
            "Atomic state mutation with guaranteed side-effect delivery",
            [
                ("WRITE", "COMMAND", ["Schema Validation", "Idempotency Key"], "#668cff", "#12223d", "#dce8ff"),
                ("ATOMIC", "DB TXN", ["Domain State Write", "+ Outbox Record"], "#42d6c5", "#0f2a32", "#b5fff4"),
                ("RELAY", "DISPATCHER", ["Poller / Stream", "Ordered Publish"], "#b58aff", "#22193a", "#e8d6ff"),
                ("WORKERS", "CONSUMERS", ["Notifications", "Analytics & Sync"], "#e8ad5a", "#2a2016", "#ffe1ad"),
                ("VERIFY", "OBSERVE", ["Dead-Letter Queue", "Delivery Metrics"], "#42d6c5", "#0f2a32", "#b5fff4"),
            ],
        ),
        encoding="utf-8",
    )

    projects = [
        ("trihub", "ENTERPRISE SAAS", "TRIHUB ERP & CRM", "Unified multi-tenant academic & operations platform", ["Next.js", "NestJS", "PostgreSQL", "Flutter"], "#42d6c5", "#0e262e", "#10313a"),
        ("priviot", "CYBERSECURITY", "PRIVIOT SHIELD", "Autonomous IoT vulnerability & ETSI EN 303 645 auditing", ["Python", "NVD / KEV", "EPSS", "Zero-Trust"], "#668cff", "#11203b", "#15284a"),
        ("astraforge", "OPEN-SOURCE AI", "ASTRAFORGE", "Modular agent skill architecture for verified execution", ["Agentic AI", "Orchestration", "Workflows"], "#b58aff", "#1f1735", "#281d45"),
        ("astramem", "AI INFRASTRUCTURE", "ASTRAMEM", "Local-first persistent memory & MCP recall engine", ["MCP Server", "Vector / FTS", "Python"], "#e8ad5a", "#261d14", "#332618"),
        ("ml-rdm", "PUBLISHED RESEARCH", "ML-RDM DEFENSE", "Multi-layered resilient model against ransomware ecosystems", ["MDPI Preprint", "ML Security", "DOI Published"], "#42d6c5", "#0e262e", "#10313a"),
        ("vok", "REVENUE SYSTEMS", "VOK LEADGEN", "Structured B2B lead discovery & qualification engine", ["Automation", "Data Pipelines", "Scoring"], "#b58aff", "#1f1735", "#281d45"),
        ("edvora", "APPLIED ML", "EDVORA ANALYTICS", "Early student dropout-risk prediction & cohort insights", ["Scikit-learn", "Python", "Predictive ML"], "#668cff", "#11203b", "#15284a"),
        ("yaatrasarthi", "PRODUCT & UX", "YAATRASARTHI", "Human-centred itinerary & travel assistance workflows", ["UX Systems", "Full-Stack", "Planning"], "#42d6c5", "#0e262e", "#10313a"),
    ]
    for args in projects:
        (ASSETS / "projects" / f"{args[0]}.svg").write_text(build_project_card(*args), encoding="utf-8")

    (ASSETS / "visuals" / "technology-map.svg").write_text(build_tech_map(), encoding="utf-8")
    print("Built 15 cohesive Obsidian SVG assets.")


if __name__ == "__main__":
    main()
