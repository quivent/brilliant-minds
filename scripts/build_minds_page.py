#!/usr/bin/env python3
"""
build_minds_page.py — generate the Brilliant Minds directory page.

Reads the collection from disk (minds/*/) and enriches each entry from
db/agents.db, so the page cannot drift from the corpus. A mind present on
disk but missing from the database is included and flagged.

Usage:
    python3 scripts/build_minds_page.py                      # writes minds/directory.html
    python3 scripts/build_minds_page.py --body out/body.html # also write a head-less body
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sqlite3
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MINDS_DIR = ROOT / "minds"
COMMANDS_DIR = ROOT / "commands"
DB_PATH = ROOT / "db" / "agents.db"
OUT_PATH = MINDS_DIR / "directory.html"

CORE_FILES = ["IDENTITY.md", "ACTIVATION.md", "CONTEXT.md", "INVOCATION.md"]

# Zones, in the order they appear on the page. Legacy zones and the five the
# induction protocol specifies both occur in the corpus.
ZONE_ORDER = [
    "computational", "synthesis", "empirical", "analysis", "analytical",
    "philosophical", "engineering", "experimental", "pedagogical", "strategy",
]
ZONE_BLURB = {
    "computational": "Formal systems, computation, machine intelligence",
    "synthesis": "Builders and connectors across domains",
    "empirical": "Measurement, experiment, evidence",
    "analysis": "Decomposition and rigorous critique",
    "analytical": "Derivation, estimators, bounded claims",
    "philosophical": "First questions, values, generative stance",
    "engineering": "Tools, systems and the people who ship with them",
    "experimental": "Material experiment and perceptual craft",
    "pedagogical": "Teaching as the primary act",
    "strategy": "Position, conflict and advantage",
}


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def first_line(pattern: str, text: str) -> str:
    m = re.search(pattern, text, re.MULTILINE)
    return re.sub(r"\s+", " ", m.group(1)).strip() if m else ""


def command_index() -> dict[str, str]:
    """Map a mind's slug to its slash command name, via the IDENTITY path each command cites."""
    index: dict[str, str] = {}
    for cmd in sorted(COMMANDS_DIR.glob("*.md")):
        body = read(cmd)
        for slug in re.findall(r"minds/([a-z0-9_]+)/IDENTITY\.md", body):
            index.setdefault(slug, cmd.stem)
    return index


def db_rows() -> dict[str, dict]:
    if not DB_PATH.exists():
        return {}
    conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            """
            SELECT a.id, a.name, a.role, a.avatar, a.description,
                   m.domains, m.era, m.primary_zone, m.characteristics, m.file_identity
            FROM mind_metadata m JOIN agents a ON a.id = m.id
            """
        ).fetchall()
    finally:
        conn.close()

    out: dict[str, dict] = {}
    for r in rows:
        slug = (r["file_identity"] or "").split("/")[0]
        if not slug:
            continue
        out[slug] = {
            "id": r["id"],
            "name": r["name"],
            "role": r["role"],
            "avatar": r["avatar"],
            "era": r["era"],
            "zone": r["primary_zone"],
            "domains": json.loads(r["domains"] or "[]"),
            "characteristics": json.loads(r["characteristics"] or "[]"),
        }
    return out


def collect() -> list[dict]:
    meta = db_rows()
    commands = command_index()
    minds = []

    for d in sorted(p for p in MINDS_DIR.iterdir() if p.is_dir()):
        slug = d.name
        activation = read(d / "ACTIVATION.md")
        context = read(d / "CONTEXT.md")
        row = meta.get(slug, {})

        name = row.get("name") or first_line(r"^#\s+(.+?)(?:\s+-\s+Activation)?$", activation) \
            or first_line(r"^#\s+(.+)$", context) or slug.replace("_", " ").title()
        era = row.get("era") or first_line(r"^\*\*\((.+?)\)\*\*", context)
        lens = first_line(r"^LENS:\s*(.+)$", activation)
        voice = first_line(r"^VOICE:\s*(.+)$", activation)
        role = row.get("role") or first_line(r"^##\s+Domain Expertise\s*\n+(.+)$", context)

        files = [f for f in CORE_FILES if (d / f).exists()]
        extra = sorted(p.name for p in d.glob("*.md") if p.name not in CORE_FILES)

        minds.append({
            "slug": slug,
            "name": name,
            "avatar": row.get("avatar") or "◆",
            "role": role,
            "era": era,
            "zone": row.get("zone") or "",
            "domains": row.get("domains", []),
            "lens": lens,
            "voice": voice,
            "command": commands.get(slug, ""),
            "files": files,
            "extra_count": len(extra),
            "indexed": slug in meta,
        })
    return minds


def card(m: dict) -> str:
    e = html.escape
    haystack = " ".join([
        m["name"], m["role"], m["zone"], m["lens"], m["command"], *m["domains"]
    ]).lower()

    domains = "".join(
        f'<li class="domain">{e(d)}</li>' for d in m["domains"][:4]
    )
    cmd = (
        f'<button class="cmd" type="button" data-cmd="/{e(m["command"])}" '
        f'title="Copy /{e(m["command"])}">/{e(m["command"])}</button>'
        if m["command"] else '<span class="cmd cmd-none">no command</span>'
    )
    flag = "" if m["indexed"] else '<span class="flag" title="Files on disk, no row in agents.db">unindexed</span>'
    era = f'<span class="era">{e(m["era"])}</span>' if m["era"] else ""
    lens = f'<p class="lens">{e(m["lens"])}</p>' if m["lens"] else \
           (f'<p class="lens lens-role">{e(m["role"])}</p>' if m["role"] else "")

    return f"""<article class="mind" data-zone="{e(m['zone'])}" data-search="{e(haystack)}">
  <header class="mind-head">
    <span class="avatar" aria-hidden="true">{e(m['avatar'])}</span>
    <div class="mind-id">
      <h3 class="mind-name">{e(m['name'])}</h3>
      <p class="mind-role">{e(m['role'])}{' · ' if m['role'] and m['era'] else ''}{era}</p>
    </div>
  </header>
  {lens}
  <ul class="domains">{domains}</ul>
  <footer class="mind-foot">
    {cmd}
    <span class="files" title="{len(m['files'])} core documents, {m['extra_count']} supplementary">{len(m['files'])}/4{f" +{m['extra_count']}" if m['extra_count'] else ""}</span>
    {flag}
  </footer>
</article>"""


def build(minds: list[dict]) -> str:
    by_zone: dict[str, list[dict]] = {}
    for m in minds:
        by_zone.setdefault(m["zone"] or "unzoned", []).append(m)

    order = [z for z in ZONE_ORDER if z in by_zone] + \
            [z for z in sorted(by_zone) if z not in ZONE_ORDER]

    chips = "".join(
        f'<button class="chip" type="button" data-zone="{html.escape(z)}">'
        f'{html.escape(z)}<span class="chip-n">{len(by_zone[z])}</span></button>'
        for z in order
    )

    sections = []
    for z in order:
        group = sorted(by_zone[z], key=lambda m: m["name"].split()[-1].lower())
        sections.append(f"""<section class="zone" data-zone="{html.escape(z)}">
  <div class="zone-head">
    <h2 class="zone-name">{html.escape(z)}</h2>
    <p class="zone-blurb">{html.escape(ZONE_BLURB.get(z, 'Unassigned'))}</p>
    <span class="zone-n">{len(group)}</span>
  </div>
  <div class="grid">
{chr(10).join(card(m) for m in group)}
  </div>
</section>""")

    commands = sum(1 for m in minds if m["command"])
    indexed = sum(1 for m in minds if m["indexed"])

    return f"""<title>The 96 Minds</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600;8..60,700&display=swap">
<style>
/* Layout: sticky filter bar over zone-grouped card grid — a directory, read by scanning. */
:root {{
  --paper:#f6f5f2; --surface:#ffffff; --surface-2:#efede8;
  --ink:#1b1a17; --ink-2:#4b473f; --muted:#6f6a60;
  --line:#e3e0d8; --line-2:#cfcabe;
  --accent:#33567f; --accent-2:#1f3a5c; --accent-bg:#e8eef6;
  --gold:#9a7320; --gold-bg:#f6eeda;
  --serif:"Source Serif 4",Georgia,"Times New Roman",serif;
  --sans:"IBM Plex Sans",-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
  --mono:"IBM Plex Mono",ui-monospace,SFMono-Regular,Menlo,monospace;
}}
@media (prefers-color-scheme:dark) {{
  :root:not([data-theme="light"]) {{
    --paper:#121211; --surface:#191918; --surface-2:#222120;
    --ink:#eceae4; --ink-2:#b6b1a7; --muted:#8c877d;
    --line:#2a2926; --line-2:#3b3935;
    --accent:#8fb4dd; --accent-2:#b3cdea; --accent-bg:#1b2735;
    --gold:#d9b368; --gold-bg:#322913;
    color-scheme:dark;
  }}
}}
:root[data-theme="dark"] {{
  --paper:#121211; --surface:#191918; --surface-2:#222120;
  --ink:#eceae4; --ink-2:#b6b1a7; --muted:#8c877d;
  --line:#2a2926; --line-2:#3b3935;
  --accent:#8fb4dd; --accent-2:#b3cdea; --accent-bg:#1b2735;
  --gold:#d9b368; --gold-bg:#322913;
  color-scheme:dark;
}}

*,*::before,*::after {{ box-sizing:border-box; }}
body {{
  margin:0; background:var(--paper); color:var(--ink);
  font:400 15px/1.6 var(--sans); -webkit-font-smoothing:antialiased;
}}
@media (prefers-reduced-motion:reduce) {{ *{{transition:none!important;animation:none!important}} }}
:focus-visible {{ outline:2px solid var(--accent); outline-offset:2px; border-radius:4px; }}

.wrap {{
  max-width:1280px; margin:0 auto;
  padding-left:max(16px,env(safe-area-inset-left,0px));
  padding-right:max(16px,env(safe-area-inset-right,0px));
}}

/* masthead */
.masthead {{ border-bottom:1px solid var(--line); background:var(--surface); }}
.masthead .wrap {{ padding-block:34px 26px; }}
.eyebrow {{
  font:500 11px/1 var(--mono); letter-spacing:.14em; text-transform:uppercase;
  color:var(--gold); margin:0 0 14px;
}}
h1 {{
  font:700 clamp(30px,5.4vw,46px)/1.08 var(--serif); letter-spacing:-.02em;
  margin:0 0 10px; text-wrap:balance;
}}
h1 em {{ color:var(--accent); font-style:italic; font-weight:400; }}
.standfirst {{ margin:0; max-width:62ch; color:var(--ink-2); font-size:16px; }}
.tallies {{
  display:flex; flex-wrap:wrap; gap:8px 26px; margin:22px 0 0; padding:0; list-style:none;
  font:500 12.5px/1 var(--mono); color:var(--muted); font-variant-numeric:tabular-nums;
}}
.tallies b {{ color:var(--ink); font-weight:500; }}

/* filter bar */
.bar {{
  position:sticky; top:env(safe-area-inset-top,0px); z-index:10;
  background:var(--surface); border-bottom:1px solid var(--line);
}}
body::before {{
  content:""; position:fixed; inset:0 0 auto; height:env(safe-area-inset-top,0px);
  background:var(--surface); z-index:11;
}}
.bar .wrap {{ padding-block:12px; display:flex; flex-wrap:wrap; gap:10px; align-items:center; }}
#q {{
  flex:1 1 240px; min-width:0; padding:9px 13px;
  font:400 14px var(--sans); color:var(--ink);
  background:var(--paper); border:1px solid var(--line-2); border-radius:8px;
}}
#q::placeholder {{ color:var(--muted); }}
.chips {{ display:flex; flex-wrap:wrap; gap:6px; min-width:0; }}
.chip {{
  display:inline-flex; align-items:baseline; gap:6px; cursor:pointer;
  padding:6px 11px; border:1px solid var(--line-2); border-radius:999px;
  background:var(--paper); color:var(--ink-2);
  font:500 12px var(--sans); letter-spacing:.01em;
}}
.chip:hover {{ border-color:var(--accent); color:var(--accent); }}
.chip[aria-pressed="true"] {{ background:var(--accent-bg); border-color:var(--accent); color:var(--accent-2); }}
.chip-n {{ font:500 11px var(--mono); color:var(--muted); font-variant-numeric:tabular-nums; }}
.chip[aria-pressed="true"] .chip-n {{ color:var(--accent); }}
.reset {{
  margin-left:auto; padding:6px 10px; cursor:pointer;
  background:none; border:0; color:var(--muted);
  font:500 12px var(--sans); text-decoration:underline; text-underline-offset:3px;
}}
.reset:hover {{ color:var(--accent); }}

/* zones */
main .wrap {{ padding-block:34px 72px; }}
.zone + .zone {{ margin-top:52px; }}
.zone-head {{
  display:flex; align-items:baseline; gap:12px; flex-wrap:wrap;
  padding-bottom:10px; margin-bottom:20px; border-bottom:1px solid var(--line);
}}
.zone-name {{
  margin:0; font:600 19px/1.2 var(--serif); letter-spacing:.01em;
  text-transform:capitalize;
}}
.zone-blurb {{ margin:0; color:var(--muted); font-size:13.5px; flex:1 1 auto; min-width:0; }}
.zone-n {{
  font:500 12px var(--mono); color:var(--muted); font-variant-numeric:tabular-nums;
}}

.grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(285px,1fr)); gap:14px; }}

/* cards */
.mind {{
  display:flex; flex-direction:column; gap:11px; min-width:0;
  padding:16px 17px 14px; background:var(--surface);
  border:1px solid var(--line); border-radius:10px;
}}
.mind:hover {{ border-color:var(--line-2); }}
.mind-head {{ display:flex; gap:11px; align-items:flex-start; min-width:0; }}
.avatar {{
  flex:0 0 auto; width:32px; height:32px; display:grid; place-items:center;
  font-size:17px; line-height:1; background:var(--surface-2);
  border:1px solid var(--line); border-radius:8px;
}}
.mind-id {{ min-width:0; }}
.mind-name {{ margin:0; font:600 16.5px/1.25 var(--serif); letter-spacing:-.005em; }}
.mind-role {{
  margin:3px 0 0; color:var(--muted); font-size:12.5px; line-height:1.45;
}}
.era {{ font:400 12px var(--mono); white-space:nowrap; }}
.lens {{
  margin:0; font-size:13.5px; line-height:1.55; color:var(--ink-2);
  border-left:2px solid var(--accent-bg); padding-left:11px;
}}
.lens-role {{ border-left-color:var(--line); color:var(--muted); font-style:italic; }}
.domains {{ display:flex; flex-wrap:wrap; gap:5px; margin:0; padding:0; list-style:none; }}
.domain {{
  font:400 11px/1 var(--sans); color:var(--muted);
  padding:4px 8px; background:var(--surface-2); border-radius:5px;
}}
.mind-foot {{
  display:flex; align-items:center; gap:9px; flex-wrap:wrap;
  margin-top:auto; padding-top:11px; border-top:1px solid var(--line);
}}
.cmd {{
  font:500 12.5px var(--mono); color:var(--accent); cursor:pointer;
  padding:4px 9px; background:var(--accent-bg);
  border:1px solid transparent; border-radius:6px;
}}
.cmd:hover {{ border-color:var(--accent); }}
.cmd.copied {{ background:var(--gold-bg); color:var(--gold); }}
.cmd-none {{ background:none; color:var(--muted); cursor:default; padding-left:0; }}
.files {{
  font:400 11.5px var(--mono); color:var(--muted);
  font-variant-numeric:tabular-nums; margin-left:auto;
}}
.flag {{
  font:500 10px/1 var(--sans); letter-spacing:.06em; text-transform:uppercase;
  color:var(--gold); background:var(--gold-bg); padding:4px 7px; border-radius:4px;
}}

.empty {{ display:none; padding:56px 0; text-align:center; color:var(--muted); }}
.empty.on {{ display:block; }}
.zone[hidden] {{ display:none; }}

footer.foot {{ border-top:1px solid var(--line); background:var(--surface); }}
footer.foot .wrap {{
  padding-block:22px 30px; color:var(--muted);
  font:400 12.5px/1.6 var(--mono);
}}
</style>

<header class="masthead"><div class="wrap">
  <p class="eyebrow">Brilliant Minds · Corpus Directory</p>
  <h1>The 96 Minds <em>and what each one sees</em></h1>
  <p class="standfirst">Every mind in the collection, with the lens it reasons through and the
  command that summons it. Each entry is a generating function, not a biography — the files
  encode a way of looking at a problem.</p>
  <ul class="tallies">
    <li><b>{len(minds)}</b> minds</li>
    <li><b>{commands}</b> slash commands</li>
    <li><b>{len(by_zone)}</b> zones</li>
    <li><b>{indexed}</b> indexed in agents.db</li>
    <li>built {date.today().isoformat()}</li>
  </ul>
</div></header>

<div class="bar"><div class="wrap">
  <input id="q" type="search" placeholder="Search name, domain, lens, command…" autocomplete="off" aria-label="Search minds">
  <div class="chips" role="group" aria-label="Filter by zone">{chips}</div>
  <button class="reset" id="reset" type="button">Clear</button>
</div></div>

<main><div class="wrap">
{chr(10).join(sections)}
<p class="empty" id="empty">No mind matches that.</p>
</div></main>

<footer class="foot"><div class="wrap">
  Generated from minds/ and db/agents.db by scripts/build_minds_page.py · run it again after /induct
</div></footer>

<script>
(function () {{
  var q = document.getElementById("q");
  var reset = document.getElementById("reset");
  var empty = document.getElementById("empty");
  var chips = Array.prototype.slice.call(document.querySelectorAll(".chip"));
  var cards = Array.prototype.slice.call(document.querySelectorAll(".mind"));
  var zones = Array.prototype.slice.call(document.querySelectorAll(".zone"));
  var active = null;

  function apply() {{
    var term = q.value.trim().toLowerCase();
    cards.forEach(function (c) {{
      var okZone = !active || c.dataset.zone === active;
      var okTerm = !term || c.dataset.search.indexOf(term) !== -1;
      c.hidden = !(okZone && okTerm);
    }});
    var shown = 0;
    zones.forEach(function (z) {{
      var n = z.querySelectorAll(".mind:not([hidden])").length;
      z.hidden = n === 0;
      shown += n;
    }});
    empty.classList.toggle("on", shown === 0);
  }}

  chips.forEach(function (chip) {{
    chip.setAttribute("aria-pressed", "false");
    chip.addEventListener("click", function () {{
      active = active === chip.dataset.zone ? null : chip.dataset.zone;
      chips.forEach(function (c) {{
        c.setAttribute("aria-pressed", String(c.dataset.zone === active));
      }});
      apply();
    }});
  }});

  q.addEventListener("input", apply);
  reset.addEventListener("click", function () {{
    q.value = ""; active = null;
    chips.forEach(function (c) {{ c.setAttribute("aria-pressed", "false"); }});
    apply(); q.focus();
  }});

  document.addEventListener("click", function (ev) {{
    var btn = ev.target.closest ? ev.target.closest(".cmd[data-cmd]") : null;
    if (!btn) return;
    var text = btn.dataset.cmd;
    function flash() {{
      var was = btn.textContent;
      btn.textContent = "copied";
      btn.classList.add("copied");
      setTimeout(function () {{ btn.textContent = was; btn.classList.remove("copied"); }}, 1100);
    }}
    try {{
      navigator.clipboard.writeText(text).then(flash, select);
    }} catch (e) {{ select(); }}
    function select() {{
      var r = document.createRange();
      r.selectNodeContents(btn);
      var s = window.getSelection();
      s.removeAllRanges(); s.addRange(r);
    }}
  }});
}})();
</script>"""


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--body", help="also write a head-less body (for publishing as an artifact)")
    ap.add_argument("--out", default=str(OUT_PATH), help="output HTML path")
    args = ap.parse_args()

    minds = collect()
    body = build(minds)

    full = (
        '<!DOCTYPE html>\n<html lang="en">\n<head>\n'
        '<meta charset="UTF-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">\n'
        f"{body.split('</style>', 1)[0]}</style>\n</head>\n<body>\n"
        f"{body.split('</style>', 1)[1].strip()}\n</body>\n</html>\n"
    )
    Path(args.out).write_text(full, encoding="utf-8")
    print(f"wrote {Path(args.out).relative_to(ROOT)}  ({len(full)//1024} KB, {len(minds)} minds)")

    if args.body:
        Path(args.body).write_text(body, encoding="utf-8")
        print(f"wrote {args.body}  (head-less body for publishing)")


if __name__ == "__main__":
    main()
