#!/usr/bin/env python3
"""PreToolUse hook for the Bash tool: block email send commands unless AUTONOMY.md allows them.

A send, reply or forward command is let through only when AUTONOMY.md, in the
project root, has both of these lines:

    Level: 3
    Send command: <anything other than "not set">

AUTONOMY.md has exactly one "Level:" line, with the value 0, 1, 2, 3 or PAUSED.
A missing file, no "Level:" line, more than one, or any other value is PAUSED.

Every other Bash command passes with no decision, so the normal permission
rules still apply. The hook can only block; it never approves anything.

Input: the hook JSON on stdin. Block: exit code 2 with the reason on stderr.
This is a guard rail, not a sandbox. It reads the words of the command line
(quoted text with spaces, options and email addresses are skipped), so it does
not see a send that is hidden inside a script or a quoted `bash -c` string.
Keep the permission allowlist tight as well.
"""
import json
import os
import re
import shlex
import sys

SEND_WORDS = {"send", "reply", "forward"}


def autonomy(project_dir):
    """Return (level, send_command_set). level is "0".."3" or "PAUSED"."""
    levels, send_set = [], False
    try:
        with open(os.path.join(project_dir, "AUTONOMY.md"), encoding="utf-8") as f:
            for line in f:
                s = line.strip()
                m = re.match(r"^Level:\s*(.*)$", s)
                if m:
                    levels.append(m.group(1).strip())
                m = re.match(r"^Send command:\s*(.*)$", s)
                if m:
                    value = m.group(1).strip().strip("`").strip().lower()
                    send_set = value not in ("", "not set")
    except OSError:
        return "PAUSED", False
    if len(levels) != 1 or levels[0] not in ("0", "1", "2", "3"):
        return "PAUSED", send_set
    return levels[0], send_set


def has_send_word(tokens):
    """Command words only: no spaces (so not a subject or body), no option, no address."""
    for token in tokens:
        if token.startswith("-") or "@" in token or re.search(r"\s", token):
            continue
        if SEND_WORDS & set(re.split(r"[^a-z]+", token.lower())):
            return True
    return False


def is_send(command):
    """True when send, reply or forward appears as a command word."""
    try:
        lexer = shlex.shlex(command, posix=True, punctuation_chars=True)
        lexer.whitespace_split = True
        return has_send_word(list(lexer))
    except ValueError:
        # Quotes do not balance (for example a here-document with an apostrophe).
        # Look only at each line up to its first quote or here-document marker.
        heads = [re.split(r"['\"]|<<", line)[0] for line in command.splitlines()]
        return any(has_send_word(h.split()) for h in heads)


def main():
    try:
        data = json.load(sys.stdin)
    except ValueError:
        print("send-guard: hook input is not JSON, command blocked", file=sys.stderr)
        return 2
    if data.get("tool_name") != "Bash":
        return 0
    command = (data.get("tool_input") or {}).get("command") or ""
    if not is_send(command):
        return 0
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or "."
    level, send_set = autonomy(project_dir)
    if level == "PAUSED":
        reason = "AUTONOMY.md is PAUSED (or has no single valid Level line)"
    elif level != "3":
        reason = "AUTONOMY.md is at Level %s and a send needs Level 3" % level
    elif not send_set:
        reason = "AUTONOMY.md has no send command set"
    else:
        return 0
    print("send-guard: blocked a send, reply or forward command. %s. "
          "Create a draft instead and list it under 'Needs you'." % reason, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
