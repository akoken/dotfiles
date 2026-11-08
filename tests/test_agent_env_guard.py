"""Decision table for bin/agent-env-guard (PreToolUse command guard).

Runs the guard as a subprocess with Claude Code / Codex shaped hook input and
checks the decision only; no command under test is ever executed. Marker
values are synthetic.
"""

import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

# AGENT_ENV_GUARD_UNDER_TEST runs the same table against another copy of the
# guard (used to show a regression test is red on an older head).
GUARD = pathlib.Path(
    os.environ.get("AGENT_ENV_GUARD_UNDER_TEST")
    or pathlib.Path(__file__).resolve().parent.parent / "bin" / "agent-env-guard"
)
MARKER = "SYNTH-MARKER-guard-7f3c"

DENY = [
    # ps with an environment flag, any spelling or order
    "ps -E",
    "ps -Eww",
    "ps -wwE",
    "ps -axE -o pid,command",
    "ps -A -E",
    "ps eww",
    "ps auxe",
    "ps axe",
    "ps -p 123 eww",
    "/bin/ps eww 1",
    "sudo ps -E",
    "nice -n 5 ps eww",
    "ps -ef | head; ps eww",
    "echo start && ps -Ewwo pid,command",
    "bash -lc 'ps eww'",
    "sh -c \"ps -E\"",
    "watch -n 1 ps eww",
    "echo \"$(ps eww)\"",
    "x=`ps -E`",
    "env FOO=1 ps eww",
    "timeout 5 ps -E",
    # whole-environment dumps
    "env",
    "env | sort",
    "/usr/bin/env",
    "env -u PATH",
    "env FOO=1",
    "printenv",
    "printenv -0",
    "printenv 2>/dev/null",
    "export -p",
    "export",
    "set",
    "set | grep KEY",
    "declare -x",
    "declare -p",
    "typeset -x",
    "readonly -p",
    "command env",
    "eval env",
    "env -S 'ps eww'",
    "cd /tmp\nenv",
    # /proc/<pid>/environ
    "cat /proc/self/environ",
    "tr '\\0' '\\n' < /proc/1/environ",
    "strings /proc/$PID/environ",
    "cat /proc/*/environ",
]

ALLOW = [
    "ps",
    "ps aux",
    "ps -ef",
    "ps -e -o pid,command",
    "ps -A",
    "ps -p 123 -o comm=",
    "ps -o pid,ppid,etime,command -p $$",
    "ps axo pid,state,command",
    "ps -U root",
    "printenv HOME",
    "printenv PATH HOME",
    "env FOO=1 npm test",
    "env -u CONTEXT7_API_KEY node script.js",
    "env -i PATH=/usr/bin /usr/bin/true",
    "env -i",
    "FOO=1 env BAR=2 make test",
    "export FOO=bar",
    "export -n FOO",
    "set -euo pipefail",
    "set -o",
    "set -- a b",
    "declare -p PATH",
    "declare -x FOO=bar",
    "typeset -i n=3",
    "command -v env",
    "git status && git diff",
    "gh auth status",
    "echo env",
    "grep -r environ src/",
    "echo ${#PATH}; ls",
    "cat <<'EOF' > notes.md\nenv\nset\nEOF",
    "xargs -n1 echo",
    "bash script.sh",
]

# Forms the patterns were not written against; kept separate so the table
# shows generalisation, not just recall.
UNSEEN_DENY = [
    "ps -wwwAE",
    "doas ps eww",
    "zsh -c 'export -p | head'",
    "nohup printenv > /tmp/x &",
    "( printenv )",
    "env -0",
    "sudo -u root env",
    "time printenv",
    "xargs -0 printf '%s\\n' < /proc/12/environ",
    "find . -name x | xargs env",
]
UNSEEN_ALLOW = [
    "ps -o user,pid,command -u akoken",
    "pgrep -fl node",
    "printenv -0 HOME",
    "env --unset=FOO python3 -V",
    "nice -n 5 make",
]


# Here-documents (ENV-GUARD-01). With an unquoted delimiter the shell runs
# command substitutions in the body; with any quoting of the delimiter the
# body is literal. Here-document operators inside quotes or comments are not
# operators, so they must not hide the following lines from inspection.
HEREDOC_DENY = [
    "cat <<EOF\n$(env)\nEOF",
    "cat <<EOF\n`env`\nEOF",
    "cat <<-EOF\n\t$(env)\n\tEOF",
    "cat <<EOF\n'$(printenv)'\nEOF",
    "cat <<EOF\nuser: $(echo $(env))\nEOF",
    "cat <<EOF\n$(env | (cat))\nEOF",
    "cat <<A <<B\nfirst\nA\n$(env)\nB",
    "cat <<EOF > out.txt\n$(export -p)\nEOF",
    "cat <<EOF\n$(ps eww)\nEOF",
    "echo '<<EOF'\nenv\nEOF",
    "echo hi # <<EOF\nenv\nEOF",
    "cat <<EOF\n$(env\nEOF",
]
HEREDOC_ALLOW = [
    "cat <<'EOF'\n$(env)\nEOF",
    "cat <<\"EOF\"\n`env`\nEOF",
    "cat <<E'OF'\n$(env)\nEOF",
    "cat <<\\EOF\n$(printenv)\nEOF",
    "cat <<-'EOF'\n\t$(env)\n\tEOF",
    "cat <<EOF\nbuilt $(date) on $(uname -s)\nEOF",
    "cat <<EOF\n$(env FOO=1 date)\nEOF",
    "cat <<EOF\nliteral \\$(env) and \\`env\\`\nEOF",
    "cat <<EOF\nHOME is $HOME\nEOF",
    "cat <<<\"$(date)\"",
    "echo '$(env)'",
]
# Cases the shell can run in the synthetic environment, to tie the guard's
# decision to what /bin/sh actually expands: deny exactly when the canary
# reaches the output. Excludes ps and the unterminated form (a syntax error).
SHELL_COUPLED = [c for c in HEREDOC_DENY + HEREDOC_ALLOW if "ps eww" not in c and "$(env\nEOF" not in c]

def run_guard(payload):
    proc = subprocess.run(
        [sys.executable, "-I", str(GUARD)],
        input=payload,
        capture_output=True,
        text=True,
        timeout=10,
    )
    return proc


def decide(command, shape="claude"):
    if shape == "claude":
        payload = {"hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_input": {"command": command}}
    else:
        payload = {"hook_event_name": "PreToolUse", "tool_name": "Bash", "turn_id": "t", "tool_input": {"command": command}}
    proc = run_guard(json.dumps(payload))
    if proc.returncode != 0:
        raise AssertionError(f"guard exited {proc.returncode}: {proc.stderr}")
    if not proc.stdout.strip():
        return "allow", ""
    out = json.loads(proc.stdout)
    spec = out["hookSpecificOutput"]
    assert spec["hookEventName"] == "PreToolUse"
    return spec["permissionDecision"], spec["permissionDecisionReason"]


class GuardDecisions(unittest.TestCase):
    def check(self, commands, expected):
        for command in commands:
            with self.subTest(command=command):
                self.assertEqual(decide(command)[0], expected)

    def test_denied_forms(self):
        self.check(DENY, "deny")

    def test_allowed_forms(self):
        self.check(ALLOW, "allow")

    def test_unseen_denied_forms(self):
        self.check(UNSEEN_DENY, "deny")

    def test_unseen_allowed_forms(self):
        self.check(UNSEEN_ALLOW, "allow")

    def test_heredoc_executable_bodies_denied(self):
        self.check(HEREDOC_DENY, "deny")

    def test_heredoc_literal_bodies_and_safe_expansions_allowed(self):
        self.check(HEREDOC_ALLOW, "allow")

    def test_codex_shape(self):
        self.assertEqual(decide("ps eww", shape="codex")[0], "deny")
        self.assertEqual(decide("ps aux", shape="codex")[0], "allow")


class GuardMatchesShellExpansion(unittest.TestCase):
    """Runs /bin/sh with only PATH and a synthetic canary, never the real env."""

    def test_guard_denies_exactly_the_bodies_the_shell_expands(self):
        clean = {"PATH": "/usr/bin:/bin", "FAKE_TEST_API_KEY": MARKER}
        for command in SHELL_COUPLED:
            with self.subTest(command=command):
                with tempfile.TemporaryDirectory() as cwd:
                    shell = subprocess.run(
                        ["/bin/sh", "-c", command], capture_output=True, text=True,
                        env=clean, cwd=cwd, timeout=10,
                    )
                    output = shell.stdout + shell.stderr
                    for name in os.listdir(cwd):
                        with open(os.path.join(cwd, name), encoding="utf-8", errors="replace") as fh:
                            output += fh.read()
                leaked = MARKER in output
                self.assertEqual(decide(command)[0], "deny" if leaked else "allow")

class GuardOutputCarriesNoMarker(unittest.TestCase):
    def test_deny_message_does_not_echo_command(self):
        for command in (
            f"env FAKE_TEST_API_KEY={MARKER}",
            f"FAKE_TEST_API_KEY={MARKER} printenv",
            f"printenv; echo {MARKER}",
        ):
            with self.subTest(command=command):
                decision, reason = decide(command)
                self.assertEqual(decision, "deny")
                self.assertNotIn(MARKER, reason)
                self.assertIn("printenv NAME", reason)

    def test_malformed_input_fails_closed_without_echo(self):
        proc = run_guard(f'{{"tool_input": {{"command": "{MARKER}')
        self.assertEqual(proc.returncode, 0)
        out = json.loads(proc.stdout)
        self.assertEqual(out["hookSpecificOutput"]["permissionDecision"], "deny")
        self.assertNotIn(MARKER, proc.stdout + proc.stderr)

    def test_non_bash_input_is_ignored(self):
        proc = run_guard(json.dumps({"tool_name": "Read", "tool_input": {"file_path": MARKER}}))
        self.assertEqual((proc.returncode, proc.stdout, proc.stderr), (0, "", ""))


if __name__ == "__main__":
    unittest.main()
