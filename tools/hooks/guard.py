#!/usr/bin/env python3
"""PreToolUse guard for Bash commands in this repo (wired in .claude/settings.json). Exit 2 blocks the command and
shows the reason to Claude. It enforces three standing rules:
  1. the replica secrets (~/.bc25b-replica-password, ~/.bc25b-galaxy-team) never go near git;
  2. commits use explicit paths: no `git add -A`, `git add --all`, `git add .` or `git commit -a`;
  3. only the local champion (research/tourney/champion.txt) is submitted to the replica (owner prompt #8).
     Crown with tools/crown.sh, which updates champion.txt before it submits.
"""
import json
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def block(why):
    print(f'guard: blocked: {why}', file=sys.stderr)
    sys.exit(2)


def main():
    try:
        cmd = json.load(sys.stdin).get('tool_input', {}).get('command', '') or ''
    except ValueError:
        return
    secrets = ('.bc25b-replica-password', '.bc25b-galaxy-team')
    if any(s in cmd for s in secrets) and re.search(r'\bgit\b|\bgh\b', cmd):
        block('a replica secret file appears in a git command; never commit or share it')
    if re.search(r'\bgit\s+add\s+(-A\b|--all\b|\.(\s|$|;|&))', cmd) or re.search(r'\bgit\s+commit\s+(-\w*a\w*\b)', cmd):
        block('commit explicit paths only (no git add -A/--all/. or commit -a)')
    for m in re.finditer(r'contest\.py\s+submit\s+(\S+)', cmd):
        bot = os.path.basename(m.group(1).rstrip('/'))
        try:
            champ = open(os.path.join(REPO, 'research', 'tourney', 'champion.txt')).read().strip()
        except OSError:
            champ = ''
        if bot != champ:
            block(f'only the local champion ({champ or "unknown"}) may be submitted, not {bot}; '
                  'crown with tools/crown.sh NEW OLD "desc"')


if __name__ == '__main__':
    main()
