#!/bin/sh
# install.sh - Brilliant Minds installs itself (no Fifth required)
#
#   git clone git@github.com:quivent/brilliant-minds.git
#   cd brilliant-minds
#   ./install.sh
#
# Installs:
#   1. the Fifth package     -> $FIFTH_HOME/packages/brilliant-minds/
#   2. the slash commands    -> ~/.claude/commands/
#   3. the hooks             -> ~/.claude/settings.json
#   4. the Python API        -> .venv/   (only with --with-python)
#
# Plain POSIX shell, so installing needs neither the Fifth interpreter nor an
# assembler. Equivalent to install.fs / install.s, which remain as alternates.
#
# Flags:
#   --package-only   just the Fifth package (old install.fs behaviour)
#   --no-commands    skip the slash commands
#   --no-hooks       skip the hooks
#   --with-python    also create .venv and install the Python API deps
#   --uninstall      remove the command symlinks and the Fifth package

set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
FIFTH_HOME=${FIFTH_HOME:-${HOME:-/tmp}/.fifth}
DEST="$FIFTH_HOME/packages/brilliant-minds"
CLAUDE_HOME=${CLAUDE_CONFIG_DIR:-${HOME:-/tmp}/.claude}

do_commands=1 do_hooks=1 do_python=0 uninstall=0

for arg in "$@"; do
  case "$arg" in
    --package-only) do_commands=0; do_hooks=0 ;;
    --no-commands)  do_commands=0 ;;
    --no-hooks)     do_hooks=0 ;;
    --with-python)  do_python=1 ;;
    --uninstall)    uninstall=1 ;;
    -h|--help)      sed -n '2,25p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "install.sh: unknown option $arg" >&2; exit 2 ;;
  esac
done

green() { printf '\033[32m%s\033[0m\n' "$1"; }
dim()   { printf '\033[2m%s\033[0m\n' "$1"; }

if [ "$uninstall" -eq 1 ]; then
  for link in "$CLAUDE_HOME"/commands/*.md; do
    [ -L "$link" ] || continue
    case "$(readlink "$link")" in "$ROOT"/commands/*) rm -f "$link" ;; esac
  done
  rm -rf "$DEST"
  green "✓ brilliant-minds uninstalled (hooks left in $CLAUDE_HOME/settings.json)"
  dim "  remove the hooks block by hand, or restore a backup from $CLAUDE_HOME/backups/"
  exit 0
fi

if [ ! -f "$ROOT/pkg/package.fs" ]; then
  echo "error: cannot read $ROOT/pkg/package.fs" >&2
  exit 1
fi

echo
echo "Brilliant Minds — installing"
echo

# ------------------------------------------------------------------
# 1. Fifth package
# ------------------------------------------------------------------
if [ -f "$DEST/package.fs" ] &&
   cmp -s "$ROOT/pkg/package.fs" "$DEST/package.fs" &&
   [ "$(cat "$DEST/root.txt" 2>/dev/null)" = "$ROOT" ]; then
  green "✓ package already registered at $DEST"
else
  mkdir -p "$DEST"
  cp "$ROOT/pkg/package.fs" "$DEST/package.fs"
  printf '%s' "$ROOT" > "$DEST/root.txt"      # so the package can find db/agents.db
  green "✓ package registered at $DEST"
fi
dim "  use pkg:brilliant-minds   (needs the Fifth interpreter)"

# ------------------------------------------------------------------
# 2. Slash commands
# ------------------------------------------------------------------
if [ "$do_commands" -eq 1 ]; then
  mkdir -p "$CLAUDE_HOME/commands"
  linked=0 kept=0 clashed=0
  for cmd in "$ROOT"/commands/*.md; do
    [ -f "$cmd" ] || continue
    target="$CLAUDE_HOME/commands/$(basename "$cmd")"
    if [ -L "$target" ] && [ "$(readlink "$target")" = "$cmd" ]; then
      kept=$((kept + 1))
    elif [ -e "$target" ] && [ ! -L "$target" ]; then
      echo "  ! kept existing $(basename "$target") (not ours)" >&2
      clashed=$((clashed + 1))
    else
      ln -sfn "$cmd" "$target"
      linked=$((linked + 1))
    fi
  done
  green "✓ $((linked + kept)) slash commands in $CLAUDE_HOME/commands/"
  [ "$linked" -gt 0 ] && dim "  $linked newly linked, $kept already present" || true
  [ "$clashed" -gt 0 ] && dim "  $clashed skipped — a real file of that name was already there" || true
  dim "  /shannon  /linus  /ferrucci  /feynman  /project-encode  /app-agent  …"
fi

# ------------------------------------------------------------------
# 3. Hooks
# ------------------------------------------------------------------
if [ "$do_hooks" -eq 1 ]; then
  # The agent hook ships prebuilt for macOS arm64. On any other host, build it
  # from hooks/agent-precontext-sqlite/ into a host-suffixed name, which
  # install_claude_hooks.py then picks up. Needs cargo and a C compiler.
  host_bin="agent-sqlite-$(uname -s | tr '[:upper:]' '[:lower:]')-$(uname -m)"
  if [ ! -x "$ROOT/hooks/$host_bin" ] && [ "$(uname -s)-$(uname -m)" != "Darwin-arm64" ]; then
    CARGO=$(command -v cargo || echo "$HOME/.cargo/bin/cargo")
    if [ -x "$CARGO" ]; then
      dim "  building $host_bin …"
      if (cd "$ROOT/hooks/agent-precontext-sqlite" && "$CARGO" build --release --quiet); then
        cp "$ROOT/hooks/agent-precontext-sqlite/target/release/agent-precontext-sqlite" \
           "$ROOT/hooks/$host_bin"
        green "✓ built hooks/$host_bin"
      else
        echo "  ! agent hook build failed — continuing without it" >&2
      fi
    fi
  fi

  if command -v python3 >/dev/null 2>&1; then
    python3 "$ROOT/scripts/install_claude_hooks.py" "$ROOT" "$CLAUDE_HOME"
  else
    echo "  ! python3 not found — skipping hooks; merge hooks/settings.json by hand" >&2
  fi
fi

# ------------------------------------------------------------------
# 4. Python API (opt-in: creates a venv, needs the network)
# ------------------------------------------------------------------
if [ "$do_python" -eq 1 ]; then
  if [ ! -x "$ROOT/.venv/bin/python" ]; then
    python3 -m venv "$ROOT/.venv"
  fi
  "$ROOT/.venv/bin/pip" install --quiet --upgrade pip
  "$ROOT/.venv/bin/pip" install --quiet anthropic pyyaml
  green "✓ Python API ready in $ROOT/.venv"
  dim "  source .venv/bin/activate"
fi

echo
green "✓ brilliant-minds installed"
dim "  root: $ROOT"
