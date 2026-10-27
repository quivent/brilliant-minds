#!/bin/bash
# Session welcome hook - output appears in conversation

CWD="$PWD"
PROJECT_NAME=$(basename "$CWD")

# Check if current project is encoded
BRILLIANT_MINDS_ROOT="${BRILLIANT_MINDS_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
# Query projects.db via the sqlite3 CLI, falling back to python3's sqlite3 module
query_projects() {
    local db="$1" path="$2"
    if command -v sqlite3 >/dev/null 2>&1; then
        sqlite3 "$db" "SELECT name, domain, sensitivity FROM projects WHERE path = '$path';" 2>/dev/null
    elif command -v python3 >/dev/null 2>&1; then
        python3 -c '
import sqlite3, sys
try:
    con = sqlite3.connect(f"file:{sys.argv[1]}?mode=ro", uri=True)
    rows = con.execute(
        "SELECT name, domain, sensitivity FROM projects WHERE path = ?", (sys.argv[2],)
    ).fetchall()
except Exception:
    sys.exit(0)
print("\n".join("|".join("" if c is None else str(c) for c in r) for r in rows))
' "$db" "$path" 2>/dev/null
    fi
}

ENCODED=$(query_projects "$BRILLIANT_MINDS_ROOT/db/projects.db" "$CWD")

cat << EOF
<session-context>
## Agent Infrastructure

| Resource | Location |
|----------|----------|
| Project Encodings | \${BRILLIANT_MINDS_ROOT}/db/projects.db |
| Functional Agents | \${BRILLIANT_MINDS_ROOT}/db/agents.db |
| Brilliant Minds | \${BRILLIANT_MINDS_ROOT}/ |

### Commands
- \`/project-encode\` - Scan current project into database
- \`/app-agent\` - Load project context and constraints
- \`/shannon\`, \`/linus\`, \`/ferrucci\` - Summon brilliant minds

EOF

if [ -n "$ENCODED" ]; then
    echo "### Current Project: ENCODED ✓"
    echo "\`\`\`"
    echo "$ENCODED" | tr '|' '\t'
    echo "\`\`\`"
    echo "Run \`/app-agent\` to load project context."
else
    echo "### Current Project: $PROJECT_NAME (not encoded)"
    echo "Run \`/project-encode\` to create project identity."
fi

echo "</session-context>"

exit 0
