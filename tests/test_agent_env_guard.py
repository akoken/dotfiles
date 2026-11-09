"""Decision table for bin/agent-env-guard (PreToolUse command guard).

Runs the guard as a subprocess with Claude Code / Codex shaped hook input.
The decision tables never execute their commands. The corpus tests
(agent_env_guard_shell_corpus.py) also run each corpus command under sh,
bash and zsh inside agent_env_guard_harness.Sandbox: a synthetic
environment with a synthetic canary, shims for env/printenv/ps, and no user
startup files. Nothing reads the real environment or /proc.
"""

import ast
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import agent_env_guard_contract as contract  # noqa: E402
import agent_env_guard_harness as harness  # noqa: E402
from agent_env_guard_shell_corpus import CASES, KNOWN_LIMITS, PROFILES, WHY  # noqa: E402

# AGENT_ENV_GUARD_UNDER_TEST runs the same table against another copy of the
# guard (used to show a regression test is red on an older head).
GUARD = pathlib.Path(
    os.environ.get("AGENT_ENV_GUARD_UNDER_TEST")
    or pathlib.Path(__file__).resolve().parent.parent / "bin" / "agent-env-guard"
)
MARKER = "SYNTH-MARKER-guard-7f3c"
CATEGORIES = {"visible", "ran", "none", "parse_error"}
DUMPED = {"visible", "ran"}

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
# ENV-GUARD-01 round 3: here-string operator, and line continuation
# (backslash-newline) in delimiters, bodies, words and arithmetic, per the
# lexing contract in bin/agent-env-guard.
B = "\\"
LEXING_DENY = [
    'cat <<<"$(env)"',
    'cat <<<"`env`"',
    "cat <<<`env`",
    'cat <<<"$(echo $(env))"',
    f"cat <<EO{B}\nF\nEOF\nenv",
    f"cat <<EOF\nEO{B}\nF\nenv\n# EOF",
    f"cat <<-EOF\n\tEO{B}\nF\nenv\n# EOF",
    f"cat <<-EO{B}\nF\n\tEOF\nenv",
    f"cat <<{B}\nEOF\nx\nEOF\nenv",
    f"cat <{B}\n<EOF\nx\nEOF\nenv",
    f"cat <<A <<B\nA\nB{B}\n\nB\nenv",
    f"cat <<EOF\nline {B}\n$(env)\nEOF",
    f"en{B}\nv",
    f"e{B}\nn{B}\nv",
    f"printen{B}\nv",
    f"env {B}\n| cat",
    f'echo "$(en{B}\nv)"',
    "((x = 1 << 2))\nenv\n2",
    "x=$((1<<2)); env",
    'echo "# <<EOF"\nenv\nEOF',
    # Executed, but the output does not reach the terminal: still denied.
    'cat <<A <<"B"\n$(env)\nA\nliteral\nB',
    "echo $(( $(env | grep -c SYNTH) ))",
    f"cat /proc/self/envi{B}\nron",
    # A substitution's value is unknown, so it never counts as a name.
    "printenv $(echo HOME)",
    "env $(true)",
]
LEXING_ALLOW = [
    "cat <<<'$(env)'",
    f"cat <<<{B}`env{B}`",
    f"cat <<'EOF'\nEO{B}\nF\nenv\nEOF",
    f"cat <<'EO'{B}\nF\n$(env)\nEOF",
    f'cat <<"EOF"\nEOF{B}\nenv\nEOF',
    "echo x#<<EOF\nenv\nEOF",
    "echo $((1 << 2))",
    'printf "%s\\n" "$(date)"',
    f'env FOO=1 {B}\n  sh -c "echo ok"',
    "env FOO=1 date",
    "cat <<EOF\n$(date)\nEOF",
    "cat <<'EOF'\n$(env)\n`env`\nEOF",
]


# Direct secret reads (SECRET-GUARD): `secret-get`, `op read` and
# `op item get` print a stored key, so an agent must not run them; keys stay
# usable through `with-secret` and the launchers. None of these is executed.
SECRET_DENY = [
    # the 2026-11-09 command: zsh MULTIOS sends the value to the pipe as well
    "/usr/bin/time -p ~/bin/secret-get obss-llm 2>&1 >/dev/null | rg real",
    # secret-get by bare name and by any path
    "secret-get obss-llm",
    "~/bin/secret-get obss-llm",
    "./bin/secret-get obss-llm",
    "bin/secret-get obss-llm",
    "/Users/akoken/bin/secret-get obss-llm",
    '"$HOME/bin/secret-get" obss-llm',
    "'secret-get' obss-llm",
    "\\secret-get obss-llm",
    "secret-get",
    "FOO=1 secret-get obss-llm",
    # pipelines, lists, groups and redirections
    "secret-get obss-llm | wc -c",
    "secret-get obss-llm > /dev/null",
    "secret-get obss-llm 2>&1 >/dev/null | cat",
    "true && secret-get obss-llm",
    "false || secret-get obss-llm",
    "true; secret-get obss-llm",
    "secret-get obss-llm &",
    "(secret-get obss-llm)",
    "{ secret-get obss-llm; }",
    "if true; then secret-get obss-llm; fi",
    "for i in 1; do secret-get obss-llm; done",
    "f() { secret-get obss-llm; }; f",
    # command, process and here-document substitution
    "echo $(secret-get obss-llm)",
    'echo "$(secret-get obss-llm)"',
    "echo `secret-get obss-llm`",
    "value=$(secret-get obss-llm)",
    "cat <(secret-get obss-llm)",
    "echo $(echo $(secret-get obss-llm))",
    "cat <<EOF\n$(secret-get obss-llm)\nEOF",
    "cat <<<\"$(secret-get obss-llm)\"",
    # shell strings, script operands and sourcing
    "sh -c 'secret-get obss-llm'",
    'bash -c "~/bin/secret-get obss-llm"',
    "zsh -c 'true; secret-get obss-llm'",
    "bash -lc 'echo a && secret-get obss-llm'",
    "bash ~/bin/secret-get obss-llm",
    "sh bin/secret-get obss-llm",
    "source bin/secret-get obss-llm",
    ". ./bin/secret-get obss-llm",
    "eval secret-get obss-llm",
    # wrappers
    "env secret-get obss-llm",
    "env -u FOO BAR=1 secret-get obss-llm",
    "command secret-get obss-llm",
    "time secret-get obss-llm",
    "time -p secret-get obss-llm",
    "/usr/bin/time -l secret-get obss-llm",
    "nohup secret-get obss-llm",
    "exec secret-get obss-llm",
    "sudo secret-get obss-llm",
    "nice -n 5 secret-get obss-llm",
    "timeout 5 secret-get obss-llm",
    "xargs secret-get",
    "echo obss-llm | xargs -n1 secret-get",
    "watch -n 1 secret-get obss-llm",
    "stdbuf -o0 secret-get obss-llm",
    "caffeinate secret-get obss-llm",
    "env FOO=1 nohup time /usr/bin/time -p ~/bin/secret-get obss-llm",
    # through with-secret and the launchers: the wrapped command is read
    "with-secret obss-llm OBSS_LLM_API_KEY secret-get xai",
    "with-obss-llm secret-get xai",
    "with-openrouter op read op://agent-keys/xai/credential",
    # op read, op inject and op document get print a stored value
    "op read op://agent-keys/obss-llm/credential",
    "op read --no-newline op://agent-keys/obss-llm/credential",
    "op read -n op://agent-keys/obss-llm/credential",
    "/opt/homebrew/bin/op read op://agent-keys/obss-llm/credential",
    "op read",
    "op inject -i template.tpl",
    "echo 'op://agent-keys/x/credential' | op inject",
    "op document get notes",
    "op documents get notes",
    "op run --no-masking -- true",
    # op item get, every spelling and every flag: any of --fields, --reveal,
    # --otp and --format json prints a value, and OP_FORMAT can change the
    # output of the bare form, so the whole subcommand is refused
    "op item get obss-llm",
    "op item get obss-llm --fields credential",
    "op item get obss-llm --fields label=credential --reveal",
    "op item get obss-llm --reveal",
    "op item get obss-llm --otp",
    "op item get obss-llm --format json",
    "op item get --vault agent-keys obss-llm",
    "op items get obss-llm",
    "op item get",
    "op --account obss item get obss-llm",
    "op --format json item get obss-llm",
    "op --cache --no-color item get obss-llm",
    "op --session abc item get obss-llm",
    "op item --vault agent-keys get obss-llm",
    "op -- item get obss-llm",
    "op get item obss-llm",
    "/opt/homebrew/bin/op item get obss-llm",
    "env OP_FORMAT=json op item get obss-llm",
    "time op read op://agent-keys/obss-llm/credential",
    "sh -c 'op item get obss-llm'",
    "echo $(op read op://agent-keys/obss-llm/credential)",
    "op item get obss-llm | wc -c",
    "OP_SERVICE_ACCOUNT_TOKEN=x op read op://agent-keys/obss-llm/credential",
    # an op command the guard cannot read is refused, not allowed
    'op "$@"',
    "op $SUBCOMMAND obss-llm",
    "op --unknown-flag item list",
    "op --cache=false item get obss-llm",
    # SG23-MASK: every effective no-masking form, flag or environment
    "op run --no-masking=true -- true",
    "op run --no-masking=1 -- true",
    "op run --no-masking=T -- true",
    "op run --no-masking=false -- true",
    "op run --env-file .env --no-masking -- true",
    "op run --no-masking",
    "op run --no-{masking,x} -- true",
    "op run --no-mask* -- true",
    "op run $FLAG -- true",
    'op run "--no-$X" -- true',
    "OP_RUN_NO_MASKING=true DB_PASSWORD=op://fake/test/password op run -- printenv DB_PASSWORD",
    "OP_RUN_NO_MASKING=1 op run -- true",
    "OP_RUN_NO_MASKING=false op run -- true",
    "OP_RUN_NO_MASKING= op run -- true",
    "OP_RUN_NO_MASKING+=1 op run -- true",
    "env OP_RUN_NO_MASKING=true op run -- true",
    "env -i OP_RUN_NO_MASKING=true op run -- true",
    "env -u FOO OP_RUN_NO_MASKING=1 /opt/homebrew/bin/op run -- true",
    "sudo OP_RUN_NO_MASKING=1 op run -- true",
    "export OP_RUN_NO_MASKING=true; op run -- true",
    "export -n OP_RUN_NO_MASKING=1",
    "declare -x OP_RUN_NO_MASKING=1; op run -- true",
    "typeset -x OP_RUN_NO_MASKING=1",
    "readonly OP_RUN_NO_MASKING=1",
    "sh -c 'OP_RUN_NO_MASKING=1 op run -- true'",
    "echo $(OP_RUN_NO_MASKING=1 op run -- true)",
    "env $X op run -- true",
    # SG23-GLOB: a glob or brace in the op command or subcommand word can
    # expand into read, inject or get
    "op r??d op://fake/test/password",
    "op re[a]d op://fake/test/password",
    "op rea* op://fake/test/password",
    "op ite? get x",
    "op item g?t x",
    "op item *et x",
    "op it{em,ems} get x",
    "op item {get,list} x",
    "op {read,whoami} x",
    "op * get x",
    "op doc* get x",
    "op --account * item list",
    "op --account {a,b} vault list",
    "touch read; op r??d op://agent-keys/obss-llm/credential",
    # SG23-MASK, class: a word with an unresolved expansion in the op run
    # option area is ambiguous, and every --no-masking[=value] is masking off
    "touch -- --no-masking=1; op run --no-mask*=1 -- true",
    "op run --no-mask*=1 -- true",
    "op run --no-mask?ng=1 -- true",
    "op run --no-maskin[g]=1 -- true",
    "op run --no-{masking,x}=1 -- true",
    "op run --no-masking=1 -- true",
    "op run --no-masking=0 -- true",
    "op run --no-masking=T -- true",
    "op run --no-masking=TRUE -- true",
    "op run --no-masking=True -- true",
    "op run --no-masking=yes -- true",
    "op run --no-masking= -- true",
    "op run --env-file *.env -- true",
    "op run --env-file=*.env -- true",
    "op run --environment {a,b} -- true",
    "op run --env-file \"$F\" -- true",
    "op run --env-file=$(echo x) -- true",
    "op run `echo --no-masking` -- true",
    "op run ? -- true",
    "op run [-]-no-masking -- true",
    # SG23-ARGV, class: option values and the `--` boundary follow op 2.42.0
    # arity; a value-taking option's next word is its value, even `--`
    "op run --env-file --no-masking --no-masking -- true",
    "op run --env-file -- --no-masking",
    "op run --environment -- --no-masking=1 -- true",
    "op run --env-file=x --no-masking -- true",
    "op --account --no-masking run --no-masking -- true",
    "op --account -- run --no-masking -- true",
    "op --format json run --no-masking -- true",
    "op --format=json run --no-masking -- true",
    "op run --future-flag --no-masking -- true",
    "op run --future=1 --no-masking -- true",
    "op run --future-flag -- true",
    "op run -x -- true",
    "op run -hv -- true",
    "op run printf %s --no-masking",
    "op run sh -c true",
    "op --future item list",
    "op item --future list",
    "touch read; op --account * r??d x",
]

SECRET_ALLOW = [
    # keys used through with-secret and the launchers never print the value
    "with-secret obss-llm OBSS_LLM_API_KEY qwen --version",
    "with-secret obss-llm CHECK sh -c 'test -n \"$CHECK\"'",
    "with-secret obss-llm CHECK sh -c 'printf %s \"$CHECK\" | wc -c'",
    "with-obss-llm ./run-eval.sh",
    "with-openrouter python agent/main.py",
    "grok --help",
    "jira issue list",
    "qwen",
    "qwen-or --version",
    "copilot-obss",
    "~/bin/with-secret xai XAI_API_KEY grok",
    "bash bin/with-secret xai XAI_API_KEY true",
    # mentions that are not invocations
    "rg secret-get README.md",
    "rg 'op read' README.md",
    "grep -n 'op item get' README.md",
    "cat bin/secret-get",
    "ls -l ~/bin/secret-get",
    "git log -- bin/secret-get",
    "git diff HEAD~1 -- bin/secret-get",
    "git commit -m 'document secret-get and op read'",
    "echo secret-get",
    "echo op item get",
    "echo secret-get | wc -c",
    "command -v secret-get",
    "type secret-get",
    "which secret-get",
    "shellcheck bin/secret-get",
    "chmod +x bin/secret-get",
    "ls bin | rg secret-get",
    "xargs -n1 echo secret-get",
    "cat docs/secret-get.md",
    "cat <<'EOF'\nsecret-get obss-llm\nop read x\nEOF",
    "cat <<EOF\nrun secret-get obss-llm and op read x\nEOF",
    "echo 'secret-get obss-llm'",
    "echo \"$(date) secret-get\"",
    "FOO=secret-get true",
    "echo op",
    "op",
    # similar names are not the commands
    "myop read x",
    "secret-get2 obss-llm",
    "secret-gets",
    "not-secret-get obss-llm",
    "/usr/bin/stop item get x",
    "oop read x",
    # op commands that print no value
    "op --version",
    "op -v",
    "op --help",
    "op help",
    "op whoami",
    "op vault list",
    "op vault list --format json",
    "op item list",
    "op item list --vault agent-keys",
    "op items list",
    "op item --vault agent-keys list",
    "op account list",
    "op --account obss vault list",
    "op --format json --no-color item list",
    "op --cache --debug whoami",
    "op signin",
    "op run -- true",
    "op run --env-file .env -- true",
    "env op whoami",
    "time op vault list",
    "sh -c 'op whoami'",
    # SG23-ARGV: what follows `--` is the child's argv, not op options
    "op run -- printf %s --no-masking",
    "op run -- printf %s --no-masking=true",
    "op run --env-file .env -- sh -c 'echo --no-masking'",
    "op run -- env OP_FORMAT=json true",
    'op run -- printf "%s" "$X"',
    "op -- whoami",
    # names that only mention the setting, and quoted look-alikes
    "echo OP_RUN_NO_MASKING",
    "echo OP_RUN_NO_MASKING=true",
    "rg OP_RUN_NO_MASKING README.md",
    "OP_RUN_NO_MASKING_NOTE=1 true",
    "export OP_FORMAT=json",
    "op 'r??d' x",
    "op item list '*'",
    "op item list *",
    "op vault list --format json *.json",
    "op run --env-file=.env -- true",
    # SG23-ARGV: a value-taking option consumes the next word, whatever it
    # looks like (op 2.42.0 `op run --help` and `op --help` flag tables)
    "op run --env-file --no-masking -- /usr/bin/printf X",
    "op run --env-file --no-masking=1 -- /usr/bin/printf X",
    "op run --environment --no-masking -- /usr/bin/printf X",
    "op run --env-file=--no-masking -- /usr/bin/printf X",
    "op run --environment=--no-masking -- /usr/bin/printf X",
    "op run --env-file a.env --env-file b.env --environment e1 -- true",
    "op run --env-file '*.env' -- true",
    "op run --env-file '--no-masking' -- true",
    "op run --help",
    "op run -h",
    "op --account --no-masking run -- true",
    "op --config --no-masking run -- true",
    "op --encoding --no-masking run -- true",
    "op --format --no-masking run -- true",
    "op --session --no-masking run -- true",
    "op --account=--no-masking run -- true",
    "op --format json run --env-file .env -- true",
    "op --cache=false run -- true",
    "op --debug --no-color --iso-timestamps run -- true",
    "op run --env-file -- -- true",
    "op run -- --no-masking",
    "op run --env-file x -- sh -c 'echo --no-masking'",
]

# Forms the guard cannot see; each one has a KNOWN_LIMITS row and a README line.
SECRET_LIMITS = [
    "printf 'secret-get obss-llm\\n' > s.sh; sh s.sh",
    "find . -maxdepth 0 -exec secret-get obss-llm \\;",
    "awk 'BEGIN { system(\"secret-get obss-llm\") }'",
    "with-secret obss-llm KEY printenv KEY",
]


def run_guard(payload, guard=None):
    proc = subprocess.run(
        [sys.executable, "-I", str(guard or GUARD)],
        input=payload,
        capture_output=True,
        text=True,
        timeout=10,
    )
    return proc


def decide(command, shape="claude", guard=None):
    if shape == "claude":
        payload = {"hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_input": {"command": command}}
    else:
        payload = {"hook_event_name": "PreToolUse", "tool_name": "Bash", "turn_id": "t", "tool_input": {"command": command}}
    proc = run_guard(json.dumps(payload), guard)
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

    def test_lexing_executable_forms_denied(self):
        self.check(LEXING_DENY, "deny")

    def test_lexing_literal_and_legitimate_forms_allowed(self):
        self.check(LEXING_ALLOW, "allow")

    def test_codex_shape(self):
        self.assertEqual(decide("ps eww", shape="codex")[0], "deny")
        self.assertEqual(decide("ps aux", shape="codex")[0], "allow")

    def test_secret_reads_denied(self):
        self.check(SECRET_DENY, "deny")

    def test_secret_free_forms_allowed(self):
        self.check(SECRET_ALLOW, "allow")

    def test_secret_limits_are_allowed(self):
        # KNOWN_LIMITS: the guard cannot see these (README "Known limitations").
        self.check(SECRET_LIMITS, "allow")

    def test_secret_deny_in_codex_shape(self):
        for command in SECRET_DENY[:3]:
            with self.subTest(command=command):
                self.assertEqual(decide(command, shape="codex")[0], "deny")
        self.assertEqual(decide("with-secret x V true", shape="codex")[0], "allow")


class CorpusTable(unittest.TestCase):
    """The written corpus is complete and self-consistent (no shell needed)."""

    def test_every_case_states_a_consistent_expectation(self):
        seen = set()
        for case in CASES:
            with self.subTest(case=case["id"]):
                self.assertNotIn(case["id"], seen)
                seen.add(case["id"])
                self.assertIn(case["decision"], {"allow", "deny"})
                if not case["run"]:
                    self.assertEqual(case["decision"], "deny")
                    continue
                observed = case["observed"]
                self.assertEqual(set(observed), set(PROFILES))
                self.assertLessEqual(set(observed.values()), CATEGORIES)
                dumped = DUMPED & set(observed.values())
                if case["decision"] == "allow":
                    # An allow is written out; one that dumps anywhere must name
                    # its documented known limitation (round 7, decision (c)).
                    self.assertIsNone(case["why"])
                    if dumped:
                        self.assertIn(case["limit"], KNOWN_LIMITS)
                    else:
                        self.assertIsNone(case["limit"])
                elif dumped:
                    self.assertIsNone(case["why"])
                else:
                    # "No dump seen" never implies allow: the deny says why.
                    self.assertIn(case["why"], WHY)

    def test_guard_decision_matches_the_table(self):
        for case in CASES:
            with self.subTest(case=case["id"]):
                self.assertEqual(decide(case["command"])[0], case["decision"])


class ShellCase(unittest.TestCase):
    """Runs sh, bash and zsh in harness.Sandbox: synthetic env, shims, no
    user startup files, never the real environment or /proc."""

    @classmethod
    def setUpClass(cls):
        cls.box = harness.Sandbox()
        cls.addClassCleanup(cls.box.close)
        cls.profiles = harness.profiles(cls.box)
        # Gate: no shell case runs unless every shell starts with exactly the
        # synthetic surface (system zshenv included, no name exemptions).
        problems = harness.startup_problems(harness.startup_report(cls.box))
        if problems:
            raise AssertionError(f"shell startup is not isolated: {problems}")

    def measure(self, command):
        return {key: self.box.run(shell, command) for shell, key in self.profiles.items()}


class ShellProfiles(ShellCase):
    def test_every_shell_is_a_verified_profile(self):
        # A missing shell or an unmeasured version fails instead of being skipped.
        self.assertEqual(set(self.profiles), set(harness.SHELL_ARGV))
        for shell, key in self.profiles.items():
            with self.subTest(shell=shell):
                self.assertIn(key, PROFILES)

    def test_startup_files_leave_the_synthetic_environment_alone(self):
        # zsh -f still sources the system zshenv (/etc/zshenv or
        # /etc/zsh/zshenv); the report names it, and every shell must start
        # with exactly the synthetic environment, no extra exports, aliases,
        # functions or options.
        report = harness.startup_report(self.box)
        for shell in self.profiles:
            with self.subTest(shell=shell, system_zshenv=report["system_zshenv"]):
                self.assertEqual(report[shell], harness.expected_surface(shell))

    def test_startup_check_detects_a_startup_file(self):
        # Control: a startup file that exports, aliases and defines something
        # (zsh without -f reads $ZDOTDIR/.zshenv) must show up in the report.
        # SHLVL is an integer in zsh: a non-numeric value would read as 0.
        with open(os.path.join(self.box.home, ".zshenv"), "w") as fh:
            fh.write("export SYNTH_STARTUP_EXTRA=1\nexport HOME=/elsewhere\n"
                     "export LOGNAME=SYNTH-STARTUP-MARKER\nexport SHLVL=7\n"
                     "alias zz=true\nzz_fn() { :; }\nsetopt extendedglob\n")
        argv = harness.SHELL_ARGV["zsh"]
        try:
            harness.SHELL_ARGV["zsh"] = ["/bin/zsh", "-c"]
            report = harness.startup_report(self.box)["zsh"]
        finally:
            harness.SHELL_ARGV["zsh"] = argv
            os.remove(os.path.join(self.box.home, ".zshenv"))
        self.assertIn("SYNTH_STARTUP_EXTRA", report["extra_exports"])
        self.assertIn("HOME", report["changed_values"])
        self.assertIn("LOGNAME", report["changed_values"])  # re-review ENV-GUARD-06
        self.assertIn("SHLVL", report["changed_values"])
        self.assertIn("zz=true", report["aliases"])
        self.assertIn("zz_fn", report["functions"])
        self.assertIn("extendedglob", report["options"])
        self.assertTrue(harness.startup_problems({"zsh": report}))

    def test_startup_check_detects_a_removed_export(self):
        # re-review ENV-GUARD-06 (368d4f8): a startup file that unexports or
        # unsets a shell-added name must fail the check, one control each.
        argv = harness.SHELL_ARGV["zsh"]
        for line, name in (("typeset +x OLDPWD", "OLDPWD"), ("typeset +x PWD", "PWD"),
                           ("unset SHLVL", "SHLVL"), ("unset LC_ALL", "LC_ALL")):
            with self.subTest(startup=line):
                with open(os.path.join(self.box.home, ".zshenv"), "w") as fh:
                    fh.write(line + "\n")
                try:
                    harness.SHELL_ARGV["zsh"] = ["/bin/zsh", "-c"]
                    report = harness.startup_report(self.box)["zsh"]
                finally:
                    harness.SHELL_ARGV["zsh"] = argv
                    os.remove(os.path.join(self.box.home, ".zshenv"))
                self.assertIn(name, report["missing_exports"])
                self.assertTrue(harness.startup_problems({"zsh": report}))


class CorpusMatchesShells(ShellCase):
    def test_measured_categories_match_the_table(self):
        for case in CASES:
            if not case["run"]:
                continue
            with self.subTest(case=case["id"]):
                measured = self.measure(case["command"])
                expected = {key: case["observed"][key] for key in measured}
                self.assertEqual(measured, expected)


def continuation_variants(command):
    """`command` with one backslash-newline inserted at every position."""
    for i in range(1, len(command)):
        yield command[:i] + B + "\n" + command[i:]


class ContinuationSweep(ShellCase):
    def test_guard_denies_every_variant_a_shell_dumps(self):
        bases = [case for case in CASES if case["sweep"]]
        self.assertTrue(bases)
        for case in bases:
            for variant in continuation_variants(case["command"]):
                measured = self.measure(variant)
                if DUMPED & set(measured.values()):
                    with self.subTest(case=case["id"], variant=variant, measured=measured):
                        self.assertEqual(decide(variant)[0], "deny")


# Structural rule (lexing contract): only LogicalSource reads the raw text.
# Outside it, the typed command may only be handed to LogicalSource (or
# type-checked, compared with "" and passed on to check_command).
RAW_NAMES = {"main": {"payload", "tool_input", "command"}, "check_command": {"command", "text"}}
RAW_SINKS = {"LogicalSource", "isinstance", "check_command"}
# Reflection could reach LogicalSource's private text without naming it.
REFLECTION = {"getattr", "setattr", "delattr", "vars", "eval", "exec", "compile",
              "globals", "locals", "__import__", "attrgetter", "methodcaller"}
ALLOWED_DUNDERS = {"__name__", "__new__"}
PRIVATE = {"_text", "_pos"}
# The guard's whole import surface: plain `import name` of these modules, no
# aliases and no `from` imports (an alias such as `attrgetter as reader`
# would hide reflection from a name check), and no module internals.
ALLOWED_IMPORTS = {"contextlib", "fnmatch", "json", "os", "re", "shlex", "sys"}
MODULE_INTERNALS = {"modules", "_getframe", "settrace", "setprofile", "__builtins__"}
# The reader API of LogicalSource; only the lexing layer may call it.
READER_API = {"peek", "at", "take", "take_physical_line", "physical_eof", "_skip"}
LAYER = {"LogicalSource", "Lexer"}


def fold_string(node):
    """The constant string an expression of string literals builds, or None."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left, right = fold_string(node.left), fold_string(node.right)
        return left + right if left is not None and right is not None else None
    if isinstance(node, ast.JoinedStr):
        parts = [fold_string(v) for v in node.values if isinstance(v, ast.Constant)]
        return "".join(p for p in parts if p is not None)
    return None


def raw_access_violations(source):
    tree = ast.parse(source)
    parent = {child: node for node in ast.walk(tree) for child in ast.iter_child_nodes(node)}

    def enclosing(node, kind):
        while node in parent:
            node = parent[node]
            if isinstance(node, kind):
                return node
        return None

    def allowed(name):
        up = parent[name]
        if isinstance(up, ast.Call) and name in up.args and isinstance(up.func, ast.Name):
            return up.func.id in RAW_SINKS
        if isinstance(up, ast.Attribute) and up.attr == "get":
            call = parent[up]
            return (isinstance(call, ast.Call) and len(call.args) == 1
                    and isinstance(call.args[0], ast.Constant))
        if isinstance(up, ast.Compare):
            return (up.left is name and len(up.ops) == 1 and isinstance(up.ops[0], ast.Eq)
                    and isinstance(up.comparators[0], ast.Constant) and up.comparators[0].value == "")
        if isinstance(up, ast.comprehension) and up.iter is name:
            call = parent[enclosing(up, ast.GeneratorExp)]
            return (isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute)
                    and call.func.attr == "join" and getattr(call.func.value, "id", None) == "shlex")
        return False

    def owner(node):
        cls = enclosing(node, ast.ClassDef)
        return cls.name if cls else None

    violations = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and node.attr in PRIVATE and owner(node) != "LogicalSource":
            violations.append(f"line {node.lineno}: .{node.attr} outside LogicalSource")
        if isinstance(node, ast.Constant) and node.value in PRIVATE and owner(node) != "LogicalSource":
            violations.append(f"line {node.lineno}: private name as a string outside LogicalSource")
        if isinstance(node, ast.ImportFrom):
            violations.append(f"line {node.lineno}: `from {node.module} import ...`")
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name not in ALLOWED_IMPORTS or alias.asname:
                    violations.append(f"line {node.lineno}: import of `{alias.name}`")
        if isinstance(node, ast.Attribute) and node.attr in MODULE_INTERNALS:
            violations.append(f"line {node.lineno}: module internals `.{node.attr}`")
        if isinstance(node, (ast.BinOp, ast.JoinedStr)):
            folded = fold_string(node)
            if folded is not None and any(p in folded for p in PRIVATE) and owner(node) != "LogicalSource":
                violations.append(f"line {node.lineno}: private name built from strings")
        if isinstance(node, ast.Name) and node.id in REFLECTION:
            violations.append(f"line {node.lineno}: reflective `{node.id}`")
        if isinstance(node, ast.Attribute) and node.attr in {"attrgetter", "methodcaller"}:
            violations.append(f"line {node.lineno}: reflective `.{node.attr}`")
        if (isinstance(node, ast.Attribute) and node.attr.startswith("__")
                and node.attr not in ALLOWED_DUNDERS):
            violations.append(f"line {node.lineno}: dunder access `.{node.attr}`")
        if isinstance(node, ast.Attribute) and node.attr in READER_API and owner(node) not in LAYER:
            violations.append(f"line {node.lineno}: reader `.{node.attr}` outside the lexing layer")
        if isinstance(node, ast.FunctionDef) and node.name in RAW_NAMES:
            for name in ast.walk(node):
                if (isinstance(name, ast.Name) and isinstance(name.ctx, ast.Load)
                        and name.id in RAW_NAMES[node.name] and not allowed(name)):
                    violations.append(f"line {name.lineno}: raw `{name.id}` used in {node.name}()")
    return violations


SEEDED_RAW_ACCESS = [
    # re-review ENV-GUARD-07 (eb86707): an import-alias reflective read
    ("import contextlib\n", "import contextlib\nfrom operator import attrgetter as field_reader\n"),
    ("        self.src = src\n",
     '        self.src = src\n        self.debug_prefix = field_reader("_te" + "xt")(src)[:80]\n'),
    ("import contextlib\n", "import contextlib\nimport operator as op\n"),
    ("import contextlib\n", "import contextlib\nimport importlib\n"),
    ("        self.src = src\n", "        self.src = src\n        self.mods = sys.modules\n"),
    # re-review ENV-GUARD-07: a reflective read of the private text
    ("        self.src = src\n", '        self.src = src\n        self.debug_prefix = getattr(src, "_text")[:80]\n'),
    ("        self.src = src\n", "        self.src = src\n        self.debug = vars(src)\n"),
    ("        self.src = src\n", "        self.src = src\n        self.debug = src.__dict__\n"),
    # the reader API used outside the lexing layer
    ("    tokens = lexer.lex_code()\n",
     '    if "environ" in lexer.src.take_physical_line():\n        raise Deny("x")\n    tokens = lexer.lex_code()\n'),
    # the pre-lexer guard's whitespace test on the raw command
    ('command == ""', "not command.strip()"),
    # a raw-text /proc belt next to the lexer
    ("    lexer = Lexer(LogicalSource(command), depth)\n",
     '    if "/proc/" in command:\n        raise Deny("proc")\n    lexer = Lexer(LogicalSource(command), depth)\n'),
    # a lexer reaching around LogicalSource
    ("        self.src = src\n", "        self.src = src\n        self.raw = src._text\n"),
]


class StructuralRule(unittest.TestCase):
    def test_guard_reads_raw_text_only_through_logical_source(self):
        self.assertEqual(raw_access_violations(GUARD.read_text()), [])

    def test_seeded_raw_access_is_caught(self):
        source = GUARD.read_text()
        for old, new in SEEDED_RAW_ACCESS:
            with self.subTest(seed=new):
                self.assertIn(old, source)
                self.assertTrue(raw_access_violations(source.replace(old, new, 1)))


PROMISE = ("The hook blocks the patterns it recognises; a command that passes is not "
           "evidence of security.")
# Round-6 wording and absolute rules: wrong in any sentence, negated or not
# (round 8, ENV-GUARD-14).
STALE_CLAIMS = [re.compile(p) for p in (
    r"\bpositive\b.*\ballow\b|\ballow\s+rule\b",
    r"\bevery\s+accepted\s+command\b",
    r"\bmust\s+be\s+denied\b",
    r"\ba\s+command\s+is\s+denied\s+when\s+any\b",
    r"\bthe\s+guarantee\s+covers\b",
)]
# A sentence that states one of these without a negation claims more than the
# promise.
SAFETY_CLAIMS = [re.compile(p) for p in (
    r"\b(allow|allows|allowed|accepted|permitted|passing|passes|passed|pass)\b.*"
    r"\b(is|are|be|stays?|remains?)\s+(safe|secure|harmless)\b",
    r"\bguarantee",
    r"\bevidence\s+of\s+(security|safety)\b",
)]
NEGATION = re.compile(r"\b(not|never|no|nor|cannot)\b|n't\b")
SEEDED_CLAIMS = [
    "All permitted commands are safe.",
    "A command that passes is evidence of security.",
    "The guard guarantees that an allowed command dumps nothing.",
    "Every case a profile marks visible must be denied.",
    "The positive allow rule holds for every case.",
    "No canary is seen, so the positive allow rule passes it.",
    "A command is denied when any shell would run a denied form.",
]


def normalised(text):
    """Lowercased prose with comment markers and line breaks folded away."""
    return re.sub(r"[\s#]+", " ", text).lower()


def safety_claims(text):
    """Sentences that claim more than the limited promise.

    A secondary tripwire only. It is lexical: it matches a fixed vocabulary,
    and it skips every sentence that contains a negation word anywhere, so
    "Allowed commands are safe and do not dump." passes. A clean result is
    not proof that no misleading claim exists; the pinned reference text
    (agent_env_guard_contract.py, PinnedContractText) is what holds the
    promise in place.
    """
    found = []
    for sentence in re.split(r"[.;:!?](?:\s|$)", normalised(text)):
        if any(claim.search(sentence) for claim in STALE_CLAIMS) or (
                not NEGATION.search(sentence)
                and any(claim.search(sentence) for claim in SAFETY_CLAIMS)):
            found.append(sentence.strip())
    return found


class LimitedGuaranteeIsStated(unittest.TestCase):
    """README, the guard (docstring, contract and deny messages) and the
    shell corpus make the same limited promise (round 7 decision (c), round 8
    ENV-GUARD-14): the hook blocks the patterns it recognises; a command that
    passes is not evidence of security."""

    README = pathlib.Path(__file__).resolve().parent.parent / "README.md"
    TESTS = pathlib.Path(__file__).resolve().parent
    CORPUS = TESTS / "agent_env_guard_shell_corpus.py"
    HARNESS = TESTS / "agent_env_guard_harness.py"

    def texts(self):
        return {"README": self.README.read_text(), "guard": GUARD.read_text(),
                "corpus": self.CORPUS.read_text(), "harness": self.HARNESS.read_text()}

    def test_readme_lists_every_known_limitation_by_command(self):
        readme = self.README.read_text()
        self.assertIn("best-effort tripwire, not a security boundary", readme)
        for case in CASES:
            if case["limit"]:
                with self.subTest(case=case["id"]):
                    self.assertTrue(case["limit"] in readme, case["limit"])
                    self.assertTrue(f"`{case['command']}`" in readme, case["command"])

    def test_every_text_states_the_promise(self):
        promise = normalised(PROMISE)
        for name in ("README", "guard", "corpus"):
            with self.subTest(text=name):
                self.assertIn(promise, normalised(self.texts()[name]))
        self.assertIn("tripwire", normalised(self.texts()["README"]))
        self.assertIn("tripwire", normalised(self.texts()["guard"]))

    def test_no_text_claims_more_than_the_promise(self):
        for name, text in self.texts().items():
            with self.subTest(text=name):
                self.assertEqual(safety_claims(text), [])

    def test_seeded_claims_are_caught(self):
        # Each seeded sentence, added to each real text, must be reported:
        # the scan is checked, not assumed.
        for name, text in self.texts().items():
            for seed in SEEDED_CLAIMS:
                with self.subTest(text=name, seed=seed):
                    self.assertTrue(safety_claims(text + "\n# " + seed + "\n"))
        self.assertEqual(safety_claims(PROMISE), [])

    def test_deny_messages_state_the_promise(self):
        for command in ("env", "ps -E", "echo $'a\\tb'"):
            with self.subTest(command=command):
                decision, reason = decide(command)
                self.assertEqual(decision, "deny")
                self.assertIn(PROMISE, reason)
                self.assertEqual(safety_claims(reason), [])


SECRET_FORMS = {
    # command -> text the deny reason must name
    "secret-get obss-llm": "secret-get",
    "~/bin/secret-get obss-llm": "secret-get",
    "op read op://agent-keys/obss-llm/credential": "op read",
    "op item get obss-llm --fields credential": "op item get",
    "op inject": "op inject",
    "op document get notes": "op document get",
    "op run --no-masking -- true": "op run --no-masking",
}
SEED_SECRET_CLAIM = "A key read through this hook is safe because the hook blocks it."


class SecretReadMessages(unittest.TestCase):
    """A denied secret read follows the deny contract: it names the matched
    form and the alternative, restates the promise and never echoes the
    command text."""

    def test_reason_names_the_form_and_the_alternative(self):
        for command, form in SECRET_FORMS.items():
            with self.subTest(command=command):
                decision, reason = decide(command)
                self.assertEqual(decision, "deny")
                self.assertIn(f"`{form}`", reason)
                self.assertIn("`with-secret <item> <VAR> <command>`", reason)
                self.assertIn("launcher", reason)
                self.assertIn(PROMISE, reason)
                self.assertEqual(contract.deny_frame_violations(reason), [])
                self.assertEqual(safety_claims(reason), [])

    def test_the_environment_hint_is_not_used_for_a_secret_read(self):
        reason = decide("secret-get obss-llm")[1]
        self.assertNotIn("printenv NAME", reason)
        self.assertIn("printenv NAME", decide("env")[1])

    def test_reason_never_echoes_the_command(self):
        for command in (
            f"secret-get {MARKER}",
            f"echo {MARKER}; ~/bin/secret-get obss-llm",
            f"op read op://{MARKER}/x/credential",
            f"op item get {MARKER} --fields credential",
            f"FAKE_TEST_API_KEY={MARKER} secret-get obss-llm",
            f"sh -c 'secret-get {MARKER}'",
        ):
            with self.subTest(command=command):
                decision, reason = decide(command)
                self.assertEqual(decision, "deny")
                self.assertNotIn(MARKER, reason)

    def test_a_secret_read_in_the_codex_shape_carries_the_same_reason(self):
        self.assertEqual(decide("secret-get obss-llm", shape="codex"),
                         decide("secret-get obss-llm", shape="claude"))

    def test_edited_secret_hint_fails_the_frame(self):
        guard = GUARD.read_text()
        seeds = {
            "one word of the secret hint": ("Do not print a stored key", "Do not show a stored key"),
            "seed in the secret hint": ("never print it, and", "never print it. " + SEED_W1 + " And"),
        }
        with tempfile.TemporaryDirectory() as tmp:
            for label, (old, new) in seeds.items():
                with self.subTest(seed=label):
                    self.assertEqual(guard.count(old), 1, old)
                    copy = pathlib.Path(tmp) / "agent-env-guard"
                    copy.write_text(guard.replace(old, new, 1))
                    decision, reason = decide("secret-get obss-llm", guard=copy)
                    self.assertEqual(decision, "deny")
                    self.assertTrue(contract.deny_frame_violations(reason), reason)

    def test_secret_forms_do_not_widen_the_environment_rules(self):
        # Healthy neighbours: the environment rules still decide as before.
        self.assertEqual(decide("printenv HOME")[0], "allow")
        self.assertEqual(decide("env")[0], "deny")


class SecretReadDocs(unittest.TestCase):
    """The README states the rule and its limits, and no longer tells an
    agent to run a command the guard denies."""

    README = LimitedGuaranteeIsStated.README
    CHECK = "with-secret <item> CHECK sh -c 'test -n \"$CHECK\"'"

    def test_readme_documents_the_rule_and_the_op_decision(self):
        readme = contract.squash(self.README.read_text())
        for text in ("`secret-get`", "`op read`", "`op item get`", "`op inject`",
                     "`op document get`", "`op run --no-masking`", "`with-secret`",
                     "Humans running commands in their own terminal, outside an agent"):
            with self.subTest(text=text):
                self.assertIn(text, readme)
        self.assertIn("any flag", readme)

    def test_readme_no_longer_tells_an_agent_to_print_a_key(self):
        readme = self.README.read_text()
        self.assertNotIn("`secret-get <item> | wc -c`", readme)
        self.assertIn(self.CHECK, readme)

    def test_the_documented_check_is_allowed(self):
        self.assertEqual(decide(self.CHECK.replace("<item>", "obss-llm"))[0], "allow")

    def test_every_guard_text_mentions_the_secret_rule(self):
        self.assertIn("secret-get", GUARD.read_text().split('"""')[1])
        self.assertIn("secret-get", LimitedGuaranteeIsStated.CORPUS.read_text())


class OpOptionTables(unittest.TestCase):
    """The guard's op option tables equal the flag tables of op 2.42.0
    (tests/fixtures/op-2.42.0-flags.txt: `op --help` Global Flags and `op run
    --help` Flags, captured with an empty HOME, no network and no vault). A
    flag of the real CLI the guard lacks, or one it adds, fails here; at run
    time an option outside the tables is refused because its arity is unknown."""

    FIXTURE = pathlib.Path(__file__).resolve().parent / "fixtures" / "op-2.42.0-flags.txt"
    FLAG_LINE = re.compile(r"^\s+(?:(-\w), )?(--[\w-]+)(?:\s+(\w+))?\s{2,}\S")

    @classmethod
    def tables(cls):
        sections, current = {}, None
        for line in cls.FIXTURE.read_text().splitlines():
            if line.startswith("== "):
                current = sections.setdefault(line[3:], {"values": set(), "flags": set()})
                continue
            match = cls.FLAG_LINE.match(line)
            if match and current is not None:
                short, long_name, kind = match.groups()
                names = {long_name} | ({short} if short else set())
                current["values" if kind else "flags"] |= names
        return sections

    @staticmethod
    def guard_module():
        import importlib.machinery
        import importlib.util
        loader = importlib.machinery.SourceFileLoader("guard_under_test", str(GUARD))
        spec = importlib.util.spec_from_loader("guard_under_test", loader)
        module = importlib.util.module_from_spec(spec)
        loader.exec_module(module)
        return module

    def test_fixture_is_the_documented_help_output(self):
        sections = self.tables()
        self.assertEqual(set(sections), {"op --help", "op run --help"})
        self.assertEqual(sections["op run --help"]["values"], {"--env-file", "--environment"})
        self.assertIn("--no-masking", sections["op run --help"]["flags"])
        self.assertIn("--account", sections["op --help"]["values"])
        self.assertIn("--cache", sections["op --help"]["flags"])

    def test_guard_tables_equal_the_cli_tables(self):
        sections, guard = self.tables(), self.guard_module()
        self.assertEqual(set(guard.OP_GLOBAL_VALUE), sections["op --help"]["values"])
        self.assertEqual(set(guard.OP_GLOBAL_BOOL), sections["op --help"]["flags"])
        self.assertEqual(set(guard.OP_RUN_VALUE), sections["op run --help"]["values"])
        self.assertEqual(set(guard.OP_RUN_BOOL), sections["op run --help"]["flags"])

    def test_every_documented_value_flag_consumes_a_masking_lookalike(self):
        sections = self.tables()
        for flag in sorted(sections["op --help"]["values"]):
            with self.subTest(flag=flag, form="global, separate value"):
                self.assertEqual(decide(f"op {flag} --no-masking run -- true")[0], "allow")
            with self.subTest(flag=flag, form="global, attached value"):
                self.assertEqual(decide(f"op {flag}=--no-masking run -- true")[0], "allow")
            with self.subTest(flag=flag, form="then a real flag"):
                self.assertEqual(decide(f"op {flag} --no-masking run --no-masking -- true")[0], "deny")
        for flag in sorted(sections["op run --help"]["values"]):
            with self.subTest(flag=flag, form="run, separate value"):
                self.assertEqual(decide(f"op run {flag} --no-masking -- true")[0], "allow")
            with self.subTest(flag=flag, form="run, attached value"):
                self.assertEqual(decide(f"op run {flag}=--no-masking -- true")[0], "allow")
            with self.subTest(flag=flag, form="then a real flag"):
                self.assertEqual(decide(f"op run {flag} --no-masking --no-masking -- true")[0], "deny")
            with self.subTest(flag=flag, form="consumes the boundary"):
                self.assertEqual(decide(f"op run {flag} -- --no-masking")[0], "deny")

    def test_every_documented_boolean_flag_takes_no_value_word(self):
        sections = self.tables()
        for flag in sorted(f for f in sections["op --help"]["flags"] if f.startswith("--")):
            with self.subTest(flag=flag):
                # a boolean flag does not consume the next word: it stays the command
                self.assertEqual(decide(f"op {flag} run --no-masking -- true")[0], "deny")
                self.assertEqual(decide(f"op {flag} run -- true")[0], "allow")


SEED_W1 = "Allowed commands are safe and do not dump."

# (surface, where the text lives, regex that opens its paragraph)
PINNED = [
    ("guard docstring", "guard", r"This is a best-effort tripwire"),
    ("guard contract comment", "guard", r"# Read as a tripwire"),
    ("corpus docstring", "corpus", r'"No canary seen"'),
    ("README command guard bullet", "readme", r"- \*\*Command guard\*\*"),
]
END_OF_PROMISE = r"not(?:\s|#)+evidence(?:\s|#)+of(?:\s|#)+security\."


def after_promise(anchor, seed):
    """(pattern, replacement): add `seed` right after the promise sentence of
    the paragraph that starts at `anchor`."""
    return re.compile(r"(" + anchor + r"[\s\S]*?" + END_OF_PROMISE + r")"), r"\1 " + seed


def one_word(anchor):
    """(pattern, replacement): change one word of the paragraph at `anchor`."""
    return re.compile(r"(" + anchor + r"[\s\S]*?)\brecognises\b"), r"\1knows"


class PinnedContractText(unittest.TestCase):
    """The text that states the promise equals its pinned reference (W-1).

    safety_claims() is a vocabulary scan that skips negated sentences, so a
    sentence such as SEED_W1 added to a surface passes it. Each surface
    paragraph (guard docstring and contract comment, corpus docstring, README
    command guard bullet) and the deny message frame (prefix, safe hint and
    PROMISE) must therefore equal agent_env_guard_contract.REFERENCE
    modulo whitespace. Changing the promise means changing the reference in
    the same commit.

    Limit: only the pinned paragraphs and the fixed deny frame are exact. The
    per-form <reason> inside a deny message and any text outside the pinned
    paragraphs are covered only by the secondary vocabulary scan.
    """

    def real(self):
        return {"guard": GUARD.read_text(),
                "corpus": LimitedGuaranteeIsStated.CORPUS.read_text(),
                "readme": LimitedGuaranteeIsStated.README.read_text()}

    def violations(self, sources):
        return contract.pin_violations(sources["guard"], sources["corpus"], sources["readme"])

    def test_current_text_equals_the_reference(self):
        self.assertEqual(self.violations(self.real()), [])

    def test_every_surface_has_a_reference_and_a_seed_target(self):
        self.assertEqual({name for name, _, _ in PINNED}, set(contract.REFERENCE))

    def test_tripwire_alone_misses_a_negated_claim(self):
        # The reason the text is pinned: the scan lets SEED_W1 through.
        self.assertEqual(safety_claims(SEED_W1), [])
        for name, text in self.texts_with_seed().items():
            with self.subTest(text=name):
                self.assertEqual(safety_claims(text), [])

    def texts_with_seed(self):
        out = {}
        for name, kind, anchor in PINNED:
            pattern, repl = after_promise(anchor, SEED_W1)
            out[name] = pattern.sub(repl, self.real()[kind], count=1)
        return out

    def test_seeded_sentence_fails_the_pin_on_every_surface(self):
        for name, kind, anchor in PINNED:
            with self.subTest(surface=name):
                pattern, repl = after_promise(anchor, SEED_W1)
                sources = self.real()
                sources[kind], count = pattern.subn(repl, sources[kind], count=1)
                self.assertEqual(count, 1)
                self.assertEqual(self.violations(sources), [name])

    def test_one_word_edit_fails_the_pin_on_every_surface(self):
        for name, kind, anchor in PINNED:
            with self.subTest(surface=name):
                pattern, repl = one_word(anchor)
                sources = self.real()
                sources[kind], count = pattern.subn(repl, sources[kind], count=1)
                self.assertEqual(count, 1)
                self.assertEqual(self.violations(sources), [name])

    def test_rewrapping_alone_is_not_an_edit(self):
        # Only whitespace is normalised: re-wrapped text still equals the reference.
        for name, kind, anchor in PINNED:
            with self.subTest(surface=name):
                pattern = re.compile(r"(" + anchor + r"[\s\S]*?)\brecognises; a command\b")
                sources = self.real()
                gap = "\n# " if name == "guard contract comment" else "\n  "
                sources[kind], count = pattern.subn(
                    lambda m: m.group(1) + "recognises;" + gap + "a" + gap + "command", sources[kind], count=1)
                self.assertEqual(count, 1)
                self.assertEqual(self.violations(sources), [])

    def test_missing_paragraph_fails_the_pin(self):
        sources = self.real()
        sources["corpus"] = sources["corpus"].replace('"No canary seen"', '"No canary"')
        self.assertTrue(self.violations(sources))

    def test_deny_messages_follow_the_pinned_frame(self):
        for command in ("env", "ps -E", "echo $'a\\tb'", "echo " + "a" * 200_001):
            with self.subTest(command=command[:20]):
                decision, reason = decide(command)
                self.assertEqual(decision, "deny")
                self.assertEqual(contract.deny_frame_violations(reason), [])

    def test_seeded_and_edited_deny_wording_fails_the_frame(self):
        guard = GUARD.read_text()
        seeds = {
            "seed in PROMISE": ('"evidence of security."', f'"evidence of security. {SEED_W1}"'),
            "seed after PROMISE in the message": (
                "{hint} {PROMISE}\"", "{hint} {PROMISE} " + SEED_W1 + "\""),
            "seed before PROMISE in the message": (
                "{hint} {PROMISE}\"", "{hint} " + SEED_W1 + " {PROMISE}\""),
            "one word of PROMISE": ('"The hook blocks the patterns it recognises;',
                                    '"The hook blocks the patterns it knows;'),
            "one word of the safe hint": ("Read a single variable", "Read a single value"),
            "message prefix": ('f"agent-env-guard: {reason}.', 'f"env-guard: {reason}.'),
        }
        with tempfile.TemporaryDirectory() as tmp:
            for label, (old, new) in seeds.items():
                with self.subTest(seed=label):
                    self.assertEqual(guard.count(old), 1, old)
                    copy = pathlib.Path(tmp) / "agent-env-guard"
                    copy.write_text(guard.replace(old, new, 1))
                    decision, reason = decide("env", guard=copy)
                    self.assertEqual(decision, "deny")
                    self.assertTrue(contract.deny_frame_violations(reason), reason)


class Limits(unittest.TestCase):
    def test_oversized_command_is_denied_visibly(self):
        decision, reason = decide("echo " + "a" * 200_001)
        self.assertEqual(decision, "deny")
        self.assertIn("too large", reason)

    def test_deep_nesting_is_denied_visibly(self):
        for command in ("echo " + "$(" * 12 + "date" + ")" * 12, "eval " * 12 + "date"):
            with self.subTest(command=command[:40]):
                decision, reason = decide(command)
                self.assertEqual(decision, "deny")
                self.assertIn("too deep", reason)

    def test_deep_expression_nesting_is_denied_visibly(self):
        # re-review ENV-GUARD-08: ${...} recursion shares the nesting budget
        for command in ("echo " + "${a:-" * 40 + "ok" + "}" * 40,
                        "echo " + '"$(' * 20 + "date" + ')"' * 20):
            with self.subTest(command=command[:40]):
                decision, reason = decide(command)
                self.assertEqual(decision, "deny")
                self.assertIn("too deep", reason)

    def test_moderate_nesting_is_allowed(self):
        self.assertEqual(decide("echo ${a:-${b:-${c:-ok}}}")[0], "allow")
        self.assertEqual(decide("echo $(echo $(echo $(date)))")[0], "allow")
        self.assertEqual(decide("eval eval eval date")[0], "allow")


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
