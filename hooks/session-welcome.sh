#!/bin/bash
# Session welcome hook - output appears in conversation

CWD="$PWD"
PROJECT_NAME=$(basename "$CWD")

# Check if current project is encoded
BRILLIANT_MINDS_ROOT="${BRILLIANT_MINDS_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
ENCODED=$(sqlite3 "$BRILLIANT_MINDS_ROOT/db/projects.db" "SELECT name, domain, sensitivity FROM projects WHERE path = '$CWD';" 2>/dev/null)

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
