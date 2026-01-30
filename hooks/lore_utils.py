#!/usr/bin/env python3
"""
Shared utilities for Lore chronicle hooks.

Used by both transcript-to-lore.py and pre-compact-lore.py.
Compatible with Python 3.9+.
"""

import json
import sys
import os
import re
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any, Union

# Configuration
LORE_DIR = Path.home() / "Lore" / "chronicles"

# Safe MIN_TURNS parsing with fallback and validation
def _parse_min_turns() -> int:
    try:
        return max(1, int(os.environ.get('LORE_MIN_TURNS', '3')))
    except ValueError:
        return 3

MIN_TURNS = _parse_min_turns()
del _parse_min_turns  # Clean up module namespace


def read_hook_input() -> Optional[Dict[str, Any]]:
    """Read JSON input from stdin (provided by Claude Code hook system)."""
    try:
        return json.loads(sys.stdin.read())
    except json.JSONDecodeError:
        return None


def parse_transcript(transcript_path: str) -> List[Dict[str, Any]]:
    """Parse .jsonl transcript into list of messages."""
    messages: List[Dict[str, Any]] = []
    try:
        with open(transcript_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:  # Skip empty lines early
                    continue
                try:
                    entry = json.loads(line)
                    if entry.get('type') in ('human', 'user', 'assistant'):
                        messages.append(entry)
                except json.JSONDecodeError:
                    continue
    except (FileNotFoundError, PermissionError, OSError) as e:
        print(f"Error reading transcript: {e}", file=sys.stderr)
        return []
    return messages


def extract_text(content: Union[str, List, None, Any]) -> str:
    """Extract text from message content (handles both string and list formats)."""
    if content is None:
        return ''
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        texts = []
        for item in content:
            if isinstance(item, dict):
                if item.get('type') == 'text':
                    texts.append(item.get('text', ''))
                elif item.get('type') == 'tool_use':
                    tool_name = item.get('name', 'unknown')
                    texts.append(f"*[Tool: {tool_name}]*")
                elif item.get('type') == 'tool_result':
                    texts.append("*[Tool result received]*")
        return '\n'.join(texts)
    return str(content)


def extract_plain_text(content: Union[str, List, None, Any]) -> str:
    """Extract only human-readable text, excluding tool markers."""
    text = extract_text(content)
    # Remove tool markers
    text = re.sub(r'\*\[Tool: [^\]]+\]\*\n?', '', text)
    text = re.sub(r'\*\[Tool result received\]\*\n?', '', text)
    return text.strip()


def has_meaningful_text(content: Union[str, List, None, Any]) -> bool:
    """Check if content has text beyond just tool markers."""
    return bool(extract_plain_text(content))


def format_date(timestamp: str) -> str:
    """Format ISO timestamp as human-readable date."""
    try:
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        return dt.strftime('%B %d, %Y')
    except (ValueError, AttributeError, TypeError):
        if isinstance(timestamp, str) and 'T' in timestamp:
            return timestamp.split('T')[0]
        return str(timestamp) if timestamp else 'Unknown date'


def slugify(text: str, max_length: int = 40) -> str:
    """Convert text to a valid filename slug."""
    if not text:
        return 'unnamed'

    slug = text.lower().strip()
    # Transliterate common unicode to ascii approximations
    slug = slug.replace('\u2019', '')  # smart quote
    slug = slug.replace('\u2018', '')  # smart quote
    slug = slug.replace('\u201c', '')  # smart double quote
    slug = slug.replace('\u201d', '')  # smart double quote

    # Replace non-ASCII and special chars with spaces (ASCII-only for filesystem safety)
    slug = re.sub(r'[^a-z0-9\s-]', ' ', slug)
    # Replace spaces/hyphens with underscore
    slug = re.sub(r'[\s_-]+', '_', slug)
    slug = slug.strip('_')

    # Truncate to max length at word boundary
    if len(slug) > max_length:
        slug = slug[:max_length].rsplit('_', 1)[0]

    return slug if slug else 'unnamed'


def generate_title(messages: List[Dict[str, Any]]) -> str:
    """Generate a title from the first substantive user message."""
    for msg in messages:
        if msg.get('type') in ('human', 'user'):
            message = msg.get('message', {})
            content = message.get('content', msg.get('content', ''))
            text = extract_plain_text(content)
            if text:
                first_line = text.split('\n')[0]
                return slugify(first_line)
    return 'unnamed'


def get_timestamp(messages: List[Dict[str, Any]]) -> str:
    """Get timestamp from first message or return current time."""
    if messages:
        first_ts = messages[0].get('timestamp', '')
        if first_ts:
            return first_ts
    return datetime.now().isoformat()


def get_cwd(hook_input: Dict[str, Any]) -> str:
    """Get current working directory from hook input or environment."""
    # Prefer hook input, fall back to env var
    return hook_input.get('cwd', '') or os.environ.get('CLAUDE_PROJECT_DIR', '')


def get_short_id(session_id: Optional[str]) -> str:
    """Get short session ID, handling empty/None cases."""
    if session_id:
        return session_id[:8]
    return 'unknown'


def count_human_messages(messages: List[Dict[str, Any]]) -> int:
    """Count human/user messages in transcript."""
    return len([m for m in messages if m.get('type') in ('human', 'user')])


def format_as_markdown(
    messages: List[Dict[str, Any]],
    timestamp: str,
    cwd: str,
    title: str,
    is_checkpoint: bool = False,
) -> str:
    """Convert messages to readable markdown format."""
    project = Path(cwd).name if cwd else "unknown"
    date_str = format_date(timestamp)

    # Build header
    checkpoint_note = ""
    if is_checkpoint:
        checkpoint_note = "\n\n*[Pre-compaction checkpoint - conversation continued]*"

    lines = [
        f"# {title.replace('_', ' ').title()}",
        "",
        f"*{date_str} \u00b7 {project}*{checkpoint_note}",
        "",
        "---",
        ""
    ]

    for msg in messages:
        msg_type = msg.get('type', 'unknown')
        message = msg.get('message', {})
        content = message.get('content', msg.get('content', ''))

        if msg_type in ('human', 'user'):
            lines.append("## Operator")
            lines.append("")
            lines.append(extract_text(content))
            lines.append("")
            lines.append("---")
            lines.append("")
        elif msg_type == 'assistant':
            # Only include if there's meaningful text beyond tool calls
            if has_meaningful_text(content):
                lines.append("## Command Center")
                lines.append("")
                lines.append(extract_text(content))
                lines.append("")
                lines.append("---")
                lines.append("")

    lines.append("")
    lines.append("*End of chronicle*")

    return '\n'.join(lines)


def save_chronicle(
    output_path: Path,
    content: str,
    description: str = "Chronicle"
) -> bool:
    """Save chronicle to file atomically with error handling. Returns success status."""
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Atomic write: write to temp file, then rename
        # This prevents corrupted files if process crashes mid-write
        fd, temp_path = tempfile.mkstemp(
            suffix='.tmp',
            dir=output_path.parent,
            prefix='.lore_'
        )
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                f.write(content)
            # Atomic rename on POSIX systems
            os.rename(temp_path, output_path)
        except Exception:
            # Clean up temp file on failure
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            raise

        print(f"{description} saved: {output_path}")
        return True
    except (OSError, IOError, PermissionError) as e:
        print(f"Error saving {description.lower()}: {e}", file=sys.stderr)
        return False


def generate_filename(title: str, session_id: str, suffix: str = "") -> str:
    """Generate filename from title with optional suffix."""
    short_id = get_short_id(session_id)
    if suffix:
        return f"{title}_{suffix}_{short_id}.md"
    return f"{title}_{short_id}.md"


def generate_checkpoint_filename(title: str, session_id: str) -> str:
    """Generate unique checkpoint filename with full timestamp."""
    short_id = get_short_id(session_id)
    # Include date, time, and milliseconds for uniqueness
    now = datetime.now()
    ts = now.strftime('%Y%m%d_%H%M%S') + f'_{now.microsecond // 1000:03d}'
    return f"{title}_checkpoint_{ts}_{short_id}.md"


def is_valid_transcript(path: str) -> bool:
    """Check if path is a valid transcript file."""
    return bool(path) and os.path.isfile(path)

