#!/usr/bin/env python3
"""
induct.py — write a new mind into the brilliant-minds collection.

Deterministic side of the induction machine. The LLM side (the /induct
slash command) drafts the markdown content, then hands a JSON spec to
this script, which:

  1. Creates minds/{slug}/ with IDENTITY, ACTIVATION, CONTEXT, INVOCATION
  2. Creates commands/{command_name}.md
  3. Inserts a row in agents
  4. Inserts a row in mind_metadata

Usage:
    python3 scripts/induct.py < spec.json
    python3 scripts/induct.py spec.json
    python3 scripts/induct.py --force spec.json   # overwrite existing

Spec schema is documented inline in REQUIRED_FIELDS / FILE_NAMES below.
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MINDS_DIR = ROOT / "minds"
COMMANDS_DIR = ROOT / "commands"
DB_PATH = ROOT / "db" / "agents.db"

FILE_NAMES = ["IDENTITY.md", "ACTIVATION.md", "CONTEXT.md", "INVOCATION.md"]

REQUIRED_FIELDS = [
    "id",            # kebab-case, primary key in agents.db (e.g. "judea-pearl")
    "slug",          # snake_case, directory name under minds/ (e.g. "judea_pearl")
    "command_name",  # slash command file stem under commands/ (e.g. "pearl")
    "name",          # human-readable name (e.g. "Judea Pearl")
    "role",          # short role string (e.g. "Causal Inference & AI")
    "avatar",        # emoji
    "description",   # short description, typically "Name (era)"
    "domains",       # list[str]
    "era",           # e.g. "1936-" or "1903-1957"
    "teaching_style",   # short slug, e.g. "do_calculus"
    "primary_zone",     # one of: philosophical, analytical, experimental, ...
    "characteristics",  # list[str]
    "files",         # dict[str, str] keyed by FILE_NAMES
    "command_md",    # full markdown body of commands/{command_name}.md
]

OPTIONAL_FIELDS = {
    "stage": "genius",
    "source": "brilliant-minds",
    "version": 1,
    "status": "idle",
    "priority": 50,
    # 32-element float vector. Unknown by default; smarter encoding can
    # come later (similarity to nearest existing mind, learned mapping, ...).
    "params": [0.0] * 32,
}


def slug_re_check(value: str, pattern: str, label: str) -> None:
    if not re.fullmatch(pattern, value):
        raise SystemExit(f"invalid {label}: {value!r} (must match /{pattern}/)")


def validate(spec: dict) -> None:
    missing = [k for k in REQUIRED_FIELDS if k not in spec]
    if missing:
        raise SystemExit(f"spec missing required fields: {missing}")

    slug_re_check(spec["id"], r"[a-z0-9]+(-[a-z0-9]+)*", "id")
    slug_re_check(spec["slug"], r"[a-z0-9]+(_[a-z0-9]+)*", "slug")
    slug_re_check(spec["command_name"], r"[a-z0-9]+(-[a-z0-9]+)*", "command_name")

    files = spec["files"]
    if set(files.keys()) != set(FILE_NAMES):
        raise SystemExit(
            f"spec.files keys must be exactly {FILE_NAMES}, got {sorted(files.keys())}"
        )
    for name, body in files.items():
        if not isinstance(body, str) or not body.strip():
            raise SystemExit(f"spec.files[{name!r}] must be a non-empty string")

    if not isinstance(spec["command_md"], str) or not spec["command_md"].strip():
        raise SystemExit("spec.command_md must be a non-empty string")

    for list_field in ("domains", "characteristics"):
        v = spec[list_field]
        if not isinstance(v, list) or not all(isinstance(x, str) for x in v):
            raise SystemExit(f"spec.{list_field} must be list[str]")

    params = spec.get("params", OPTIONAL_FIELDS["params"])
    if not (isinstance(params, list) and len(params) == 32
            and all(isinstance(x, (int, float)) for x in params)):
        raise SystemExit("spec.params must be a 32-element list of numbers")


def write_files(spec: dict, force: bool) -> tuple[Path, Path]:
    mind_dir = MINDS_DIR / spec["slug"]
    cmd_path = COMMANDS_DIR / f"{spec['command_name']}.md"

    if mind_dir.exists() and not force:
        raise SystemExit(f"refuse: {mind_dir} already exists (use --force to overwrite)")
    if cmd_path.exists() and not force:
        raise SystemExit(f"refuse: {cmd_path} already exists (use --force to overwrite)")

    mind_dir.mkdir(parents=True, exist_ok=True)
    for name, body in spec["files"].items():
        (mind_dir / name).write_text(body, encoding="utf-8")
    cmd_path.write_text(spec["command_md"], encoding="utf-8")

    return mind_dir, cmd_path


def insert_db(spec: dict, force: bool) -> None:
    if not DB_PATH.exists():
        raise SystemExit(f"agents.db not found at {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    try:
        existing = conn.execute(
            "SELECT 1 FROM agents WHERE id = ?", (spec["id"],)
        ).fetchone()
        if existing and not force:
            raise SystemExit(f"refuse: agent id {spec['id']!r} already in db (use --force)")
        if existing and force:
            conn.execute("DELETE FROM mind_metadata WHERE id = ?", (spec["id"],))
            conn.execute("DELETE FROM agents WHERE id = ?", (spec["id"],))

        get = lambda key: spec.get(key, OPTIONAL_FIELDS[key])

        conn.execute(
            """
            INSERT INTO agents (
                id, name, role, avatar, source, version,
                status, stage, description, priority
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                spec["id"], spec["name"], spec["role"], spec["avatar"],
                get("source"), get("version"),
                get("status"), get("stage"), spec["description"], get("priority"),
            ),
        )

        conn.execute(
            """
            INSERT INTO mind_metadata (
                id, domains, era, teaching_style, primary_zone, characteristics,
                file_identity, file_context, file_activation, file_standalone, params
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                spec["id"],
                json.dumps(spec["domains"]),
                spec["era"],
                spec["teaching_style"],
                spec["primary_zone"],
                json.dumps(spec["characteristics"]),
                f"{spec['slug']}/IDENTITY.md",
                f"{spec['slug']}/CONTEXT.md",
                f"{spec['slug']}/ACTIVATION.md",
                None,
                json.dumps(get("params")),
            ),
        )
        conn.commit()
    finally:
        conn.close()


def main() -> None:
    p = argparse.ArgumentParser(description="Write a new mind into brilliant-minds.")
    p.add_argument("spec", nargs="?", help="path to JSON spec (omit to read stdin)")
    p.add_argument("--force", action="store_true", help="overwrite existing mind")
    p.add_argument("--dry-run", action="store_true", help="validate only, write nothing")
    args = p.parse_args()

    raw = Path(args.spec).read_text(encoding="utf-8") if args.spec else sys.stdin.read()
    try:
        spec = json.loads(raw)
    except json.JSONDecodeError as e:
        raise SystemExit(f"invalid JSON: {e}")

    validate(spec)
    if args.dry_run:
        print(f"[dry-run] spec valid for {spec['name']!r}")
        return

    mind_dir, cmd_path = write_files(spec, force=args.force)
    insert_db(spec, force=args.force)

    print(f"inducted {spec['name']!r}")
    print(f"  mind:    {mind_dir.relative_to(ROOT)}")
    print(f"  command: {cmd_path.relative_to(ROOT)}")
    print(f"  db id:   {spec['id']}")


if __name__ == "__main__":
    main()
