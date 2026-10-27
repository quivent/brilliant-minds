#!/usr/bin/env python3
"""Merge the Brilliant Minds hooks into the user's Claude Code settings.

Called by install.sh. Idempotent: re-running adds nothing new.
Only the "hooks" block and env.BRILLIANT_MINDS_ROOT are touched - the user's
own settings (theme, tui, plugins, ...) are left exactly as they were.

A hook whose command cannot run on this machine (a wrong-architecture binary)
is retargeted to a host-specific build next to it - agent-sqlite-linux-x86_64
for agent-sqlite - and skipped with a note only when no such build exists.
"""

import json
import os
import platform
import shutil
import sys
import time
from pathlib import Path

GREEN, YELLOW, DIM, RESET = "\033[32m", "\033[33m", "\033[2m", "\033[0m"


def runnable(cmd: str, root: Path) -> tuple[bool, str]:
    """Can this hook command actually execute here?"""
    path_str = cmd.split()[0].replace("${BRILLIANT_MINDS_ROOT}", str(root))
    path = Path(path_str)
    if not path.exists():
        return False, "missing"
    if not os.access(path, os.X_OK):
        return False, "not executable"

    with open(path, "rb") as fh:
        magic = fh.read(4)

    if magic[:2] == b"#!":
        return True, ""
    system = platform.system()
    if magic == b"\x7fELF":
        return (True, "") if system == "Linux" else (False, f"ELF binary on {system}")
    if magic in (b"\xcf\xfa\xed\xfe", b"\xce\xfa\xed\xfe", b"\xca\xfe\xba\xbe"):
        return (True, "") if system == "Darwin" else (False, f"macOS binary on {system}")
    return True, ""


def host_suffix() -> str:
    return f"{platform.system().lower()}-{platform.machine()}"


def resolve(cmd: str, root: Path) -> tuple[str | None, str]:
    """Return a runnable form of this hook command, or None with a reason.

    A command whose binary was built for another platform is retargeted to a
    sibling named <binary>-<os>-<arch> when one exists, so a repo can carry
    builds for several hosts without the hook path changing per machine.
    """
    ok, why = runnable(cmd, root)
    if ok:
        return cmd, ""

    head, _, tail = cmd.partition(" ")
    for candidate in (f"{head}-{host_suffix()}", f"{head}-{platform.system().lower()}"):
        ok, _ = runnable(candidate, root)
        if ok:
            return (candidate + (" " + tail if tail else "")), ""
    return None, why


def merge_event(existing: list, incoming: list) -> int:
    """Add incoming hook groups to an event, skipping commands already present."""
    present = {
        h.get("command")
        for group in existing
        for h in group.get("hooks", [])
    }
    added = 0
    for group in incoming:
        new_hooks = [h for h in group.get("hooks", []) if h.get("command") not in present]
        if not new_hooks:
            continue
        matcher = group.get("matcher")
        target = next(
            (g for g in existing if g.get("matcher") == matcher),
            None,
        )
        if target is None:
            target = {k: v for k, v in group.items() if k != "hooks"}
            target["hooks"] = []
            existing.append(target)
        target["hooks"].extend(new_hooks)
        added += len(new_hooks)
    return added


def main() -> int:
    root = Path(sys.argv[1]).resolve()
    claude_home = Path(sys.argv[2]).expanduser()
    settings_path = claude_home / "settings.json"
    source_path = root / "hooks" / "settings.json"

    source = json.loads(source_path.read_text())
    source_hooks = source.get("hooks", {})

    settings = {}
    if settings_path.exists():
        try:
            settings = json.loads(settings_path.read_text())
        except json.JSONDecodeError as exc:
            print(f"error: {settings_path} is not valid JSON ({exc})", file=sys.stderr)
            return 1
        backup_dir = claude_home / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)
        backup = backup_dir / f"settings.json.{time.strftime('%Y%m%d-%H%M%S')}.bak"
        shutil.copy2(settings_path, backup)
        print(f"{DIM}  backup: {backup}{RESET}")

    settings.setdefault("env", {})["BRILLIANT_MINDS_ROOT"] = str(root)

    hooks = settings.setdefault("hooks", {})
    added = skipped = 0
    for event, groups in source_hooks.items():
        usable, unusable = [], []
        for group in groups:
            keep = []
            for hook in group.get("hooks", []):
                command, why = resolve(hook.get("command", ""), root)
                if command is None:
                    unusable.append((hook, why))
                else:
                    keep.append({**hook, "command": command})
            if keep:
                usable.append({**{k: v for k, v in group.items() if k != "hooks"}, "hooks": keep})
        for hook, why in unusable:
            name = Path(hook["command"].split()[0]).name
            print(f"{YELLOW}  ! skipped {event}/{name} — {why}{RESET}")
            print(f"{DIM}    build one as hooks/{name}-{host_suffix()} to enable it{RESET}")
            skipped += 1
        if usable:
            added += merge_event(hooks.setdefault(event, []), usable)

    if not hooks:
        settings.pop("hooks", None)

    claude_home.mkdir(parents=True, exist_ok=True)
    tmp = settings_path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(settings, indent=2) + "\n")
    tmp.replace(settings_path)

    if added:
        print(f"{GREEN}  ✓ {added} hook(s) merged into {settings_path}{RESET}")
    else:
        print(f"{GREEN}  ✓ hooks already present in {settings_path}{RESET}")
    if skipped:
        print(f"{DIM}  {skipped} hook(s) not installed on this platform{RESET}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
