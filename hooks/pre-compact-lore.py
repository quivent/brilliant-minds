#!/usr/bin/env python3
"""
Pre-Compact Lore Saver

Saves the full transcript BEFORE context compaction happens.
Ensures no conversation content is lost when context window fills up.
Triggered by PreCompact hook (both manual /compact and auto-compact).
"""

import sys
import os

# Add hooks directory to path for shared module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lore_utils import (
    LORE_DIR,
    MIN_TURNS,
    read_hook_input,
    parse_transcript,
    get_timestamp,
    get_cwd,
    count_human_messages,
    format_as_markdown,
    generate_title,
    generate_checkpoint_filename,
    save_chronicle,
    is_valid_transcript,
)


def main():
    hook_input = read_hook_input()
    if not hook_input:
        print("No hook input received", file=sys.stderr)
        return

    transcript_path = hook_input.get('transcript_path', '')
    session_id = hook_input.get('session_id', 'unknown')
    trigger = hook_input.get('trigger', 'unknown')  # 'manual' or 'auto'
    cwd = get_cwd(hook_input)

    if not is_valid_transcript(transcript_path):
        print(f"Transcript not found or not a file: {transcript_path}", file=sys.stderr)
        return

    messages = parse_transcript(transcript_path)

    if count_human_messages(messages) < MIN_TURNS:
        print(f"Session too short, skipping checkpoint", file=sys.stderr)
        return

    # Generate title once, pass to all functions that need it
    title = generate_title(messages)
    timestamp = get_timestamp(messages)

    markdown = format_as_markdown(messages, timestamp, cwd, title, is_checkpoint=True)
    filename = generate_checkpoint_filename(title, session_id)
    output_path = LORE_DIR / filename

    if not save_chronicle(output_path, markdown, f"Pre-compact checkpoint ({trigger})"):
        sys.exit(1)


if __name__ == '__main__':
    main()

