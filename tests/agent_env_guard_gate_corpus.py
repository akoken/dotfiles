"""Frozen regression corpus of the secret-read rule (synthetic strings only).

Every row is a string handed to the guard on stdin; none is ever executed by a
test in this file, and no real `secret-get`, `op`, vault or key is used. The
tables are consumed by tests/test_agent_env_guard.py (class SecretReadGate).

The rule is flat (see the guard docstring): an input whose text spells a
guarded name is refused, whatever it would do, as text and as a list payload.
An input that spells no guarded name is not examined by the rule and decides
as on main. The tables below differ only in why a row is kept.
"""

# Direct secret reads and the forms that hide them. Every row spells a guarded
# name, so every row is denied.
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
    # SG23-QUOTED-MULTIWORD: a quoted "$@" or "${a[@]}" is several words, the
    # suffix lands on the last (set -- echo SYNTH; "$@/tail" prints SYNTH/tail)
    'set -- secret-get fake; "$@/true"',
    'set -- secret-get fake; "${@}/true"',
    'set -- secret-get fake; "$@"',
    'set -- secret-get fake; "${@:1}/true"',
    'a=(secret-get fake); "${a[@]}/x"',
    'a=(secret-get fake); "${a[@]}"',
    'a=(secret-get fake); "${a[@]:0}/x"',
    'a=(secret-get fake); "${(@)a}/x"',
    'a=(secret-get fake); "${(@kv)a}/x"',
    'a=(secret-get fake); "$a[@]/x"',
    'set -- secret-get fake; with-secret obss-llm KEY "$@/true"',
    'set -- secret-get fake; with-openrouter "$@/true"',
    'set -- secret-get fake; with-obss-llm "${@}/true"',
    'a=(secret-get fake); with-secret obss-llm KEY "${a[@]}/x"',
    'set -- op read x; env "$@/true"',
    'set -- op read x; time "$@/true"',
    'set -- op read x; nohup "$@/true"',
    'set -- secret-get fake; sudo "$@/true"',
    'set -- secret-get fake; command "$@/true"',
    'set -- secret-get fake; xargs "$@/true"',
    # SG23-NESTED-MULTIWORD: an inner expansion must not reset the outer
    # multi-word state (the reported probe, verbatim)
    'a=(secret-get fake); x=x; "${a[@]:-"${x}"}/true"',
    # SG23-INTEGER-NO-MASKING: every declaration builtin exports an assignment
    "integer -x OP_RUN_NO_MASKING=1; op run -- true",
    "integer OP_RUN_NO_MASKING=1",
    "float -x OP_RUN_NO_MASKING=1",
    "typeset -ix OP_RUN_NO_MASKING=1",
    # SUDO-K: -k, -K and -v skip nothing when a command follows
    "sudo -k secret-get fake",
    "sudo -u root -k secret-get fake",
    "sudo -vk secret-get fake",
    "sudo -kv secret-get fake",
    "sudo -K secret-get fake",
    "sudo -v secret-get fake",
    "sudo --reset-timestamp secret-get fake",
    "sudo --remove-timestamp secret-get fake",
    "sudo --validate secret-get fake",
    "sudo -k op read op://agent-keys/obss-llm/credential",
    # option tokens built by command or arithmetic expansion, or changed by quoting
    "bash -$(echo c) 'secret-get fake'",
    "bash -`echo c` 'secret-get fake'",
    "bash -$((1)) 'secret-get fake'",
    "bash -$((0+99)) 'secret-get fake'",
    "env -u$(echo X) true secret-get fake",
    "env -u`echo X` true secret-get fake",
    "env -u$((1)) true secret-get fake",
    "sudo -$(echo u) root secret-get fake",
    "bash '-c' 'secret-get fake'",
    'bash "-c" "secret-get fake"',
    'bash -"c" "secret-get fake"',
    "bash -\\c 'secret-get fake'",
    "bash ''-c 'secret-get fake'",
    "bash $'-c' 'secret-get fake'",
    "sudo '-u' root secret-get fake",
    "env '-S' 'secret-get fake'",
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



# The independent review of the PR at 5dedb04: 31 inputs the earlier guard allowed,
# 11 controls it denied and one healthy control (id, command, expected decision).
# The two commands that carried an absolute path use /tmp/probe/bin.
REVIEW_INPUTS = [
    ["CTL-direct", "secret-get fake-item", "deny"],
    ["CTL-eval", "eval 'secret-get fake-item'", "deny"],
    ["CTL-alias", "alias x=secret-get", "deny"],
    ["CTL-hash", "hash -p /tmp/probe/bin/secret-get x; x fake-item", "deny"],
    ["CTL-shell-stdin", "printf 'secret-get fake-item\\n' | bash", "deny"],
    ["CTL-xargs-I", "printf 'secret-get\\n' | xargs -I% % fake-item", "deny"],
    ["CTL-healthy", "git status && printf '%s\\n' ok", "allow"],
    ["XARGS-cluster", "printf 'secret-get\\n' | xargs -tI% % fake-item", "deny"],
    ["XARGS-cluster-sp", "printf 'secret-get\\n' | xargs -tI % % fake-item", "deny"],
    ["XARGS-J-cluster", "printf 'secret-get\\n' | xargs -tJ% % fake-item", "deny"],
    ["STDIN-dev-bash", "printf 'secret-get fake-item\\n' | bash /dev/stdin", "deny"],
    ["STDIN-dev-zsh", "printf 'secret-get fake-item\\n' | zsh -f /dev/stdin", "deny"],
    ["STDIN-fd0-heredoc", "sh /dev/fd/0 <<'EOF'\nsecret-get fake-item\nEOF", "deny"],
    ["STDIN-BASH_ENV", "printf 'secret-get fake-item\\n' | BASH_ENV=/dev/stdin bash -c true", "deny"],
    ["HASH-BASH_CMDS", "BASH_CMDS[x]=$(command -v secret-get); x fake-item", "deny"],
    ["HASH-zsh-commands", "commands[x]=$(command -v secret-get); x fake-item", "deny"],
    ["ALIAS-zsh-aliases", "aliases[x]=secret-get\nx fake-item", "deny"],
    ["ALIAS-bash-BASH_ALIASES", "shopt -s expand_aliases; BASH_ALIASES[x]=secret-get\nx fake-item", "deny"],
    ["FUNC-zsh-functions", "functions[f]='secret-get fake-item'; f", "deny"],
    ["EVAL-zsh-emulate", "emulate sh -c 'secret-get fake-item'", "deny"],
    ["DYN-bash-atP", "x='$(secret-get fake-item)'; printf '%s\\n' \"${x@P}\"", "deny"],
    ["DYN-arith-subscript", "x='a[$(secret-get fake-item)]'; echo $((x))", "deny"],
    ["DYN-PS4", "PS4='$(secret-get fake-item) '; set -x; true", "deny"],
    ["DYN-mapfile-C", "mapfile -C 'secret-get' -c 1 a <<< fake-item", "deny"],
    ["CASE-upper", "SECRET-GET fake-item", "deny"],
    ["CASE-mixed-path", "/tmp/probe/bin/Secret-Get fake-item", "deny"],
    ["CASE-op", "OP read op://fake-vault/fake-item/field", "deny"],
    ["OBS-tcsh-c", "tcsh -f -c 'secret-get fake-item'", "deny"],
    ["OBS-fnbody", "f() secret-get fake-item; f", "deny"],
    ["XARGS-I-cluster-arg", "printf 'secret-get\\n' | xargs -tI% sh -c '% fake-item'", "deny"],
    ["CTL-XARGS-I-arg", "printf 'secret-get\\n' | xargs -I% sh -c '% fake-item'", "deny"],
    ["CTL-XARGS-J", "printf 'secret-get\\n' | xargs -J% % fake-item", "deny"],
    ["ALIAS-zsh-aliases-eval", "aliases[x]=secret-get; eval 'x fake-item'", "deny"],
    ["ALIAS-zsh-aliases-append", "aliases+=(x secret-get); eval 'x fake-item'", "deny"],
    ["CTL-alias-zsh", "alias x=secret-get; eval 'x fake-item'", "deny"],
    ["NAMEDFD-redirect", "{fd}>/dev/null secret-get fake-item", "deny"],
    ["CTL-fd-digit", "2>/dev/null secret-get fake-item", "deny"],
    ["ZSH-short-if-cond", "if [[ -n x ]] secret-get fake-item", "deny"],
    ["ZSH-short-if-arith", "if (( 1 )) secret-get fake-item", "deny"],
    ["CTL-zsh-if-brace", "if [[ -n x ]] { secret-get fake-item }", "deny"],
    ["LEX-param-squote", "echo ${x:-'}'$(secret-get fake-item)'}'} #'", "deny"],
    ["LEX-param-brace", "echo ${x:-{} ; secret-get fake-item ; echo }", "deny"],
    ["OPRUN-child-fakeop", "op run -- secret-get fake-item", "deny"],
]


# The two findings fixed in round 6 of the earlier design.
ROUND_6 = [
    "a=(secret-get fake); x=x; \"${a[@]:-\"${x}\"}/true\"",
    "integer -x OP_RUN_NO_MASKING=1; op run -- true",
]


# SR-01, the finding of the single independent review at 0294c46: the strict
# grammar of that head allowed an input that wrote git configuration naming
# the guarded command and then had a listed git subcommand run it. Both
# inputs spell the name, so the flat rule denies them.
SR_01 = [
    "printf '[diff]\\n\\texternal = secret-get synthitem\\n' >> .git/config && git show --ext-diff",
    "echo 'f.txt diff=s' > .gitattributes && "
    "printf '[diff \"s\"]\\n\\ttextconv = secret-get synthitem\\n' >> .git/config && git diff HEAD~1",
]


# U+017F (LATIN SMALL LETTER LONG S) in place of an `s`. A case-insensitive
# macOS volume ran the guarded command under this spelling when measured, and
# str.lower() keeps the letter, so the spelling test folds case with
# str.casefold(). Each row is denied; the test states that expectation as a
# literal and does not ask the guard whether the row spells a name.
LONG_S = [
    "\u017fecret-get synthitem",
    "env \u017fecret-get synthitem",
    "/tmp/x/bin/\u017fecret-get synthitem",
    "\u017fECRET-GET synthitem",
    "echo ok && \u017fecret-get synthitem 2>&1 >/dev/null | rg real",
]
LONG_S_ARGV = [
    ["\u017fecret-get", "synthitem"],
    ["/tmp/x/bin/\u017fecret-get", "synthitem"],
    ["bash", "-lc", "\u017fecret-get synthitem"],
    ["zsh", "-lc", "env \u017fecret-get synthitem"],
]


# The seven mention forms of the original brief and one pipeline form. They
# print no key, and they spell a guarded name: preserving them was retired for
# shell inputs (2026-11-11), so each is denied.
MENTIONS = [
    "rg secret-get README.md",
    "cat bin/secret-get",
    "git log -- bin/secret-get",
    "op --version",
    "op whoami",
    "op vault list",
    "op item list",
    "echo secret-get | wc -c",
]


# Rows that spell a guarded name and are not one of the direct reads above
# (mentions, non-printing `op` forms, prose): the cost of the flat rule. Each
# is denied. The first 24 were allowed by the strict grammar of 0294c46, the
# rest were refused there for their syntax or their command.
SPELLED_HARMLESS = [
    "rg secret-get README.md",
    "rg 'op read' README.md",
    "grep -n 'op item get' README.md",
    "cat bin/secret-get",
    "git log -- bin/secret-get",
    "git diff HEAD~1 -- bin/secret-get",
    "echo secret-get",
    "echo op item get",
    "echo secret-get | wc -c",
    "type secret-get",
    "which secret-get",
    "ls bin | rg secret-get",
    "cat docs/secret-get.md",
    "echo 'secret-get obss-llm'",
    "echo op",
    "op --version",
    "op --help",
    "op whoami",
    "op vault list",
    "op item list",
    "op account list",
    "echo OP_RUN_NO_MASKING",
    "echo OP_RUN_NO_MASKING=true",
    "rg OP_RUN_NO_MASKING README.md",
    "ls -l ~/bin/secret-get",
    "git commit -m 'document secret-get and op read'",
    "command -v secret-get",
    "shellcheck bin/secret-get",
    "chmod +x bin/secret-get",
    "xargs -n1 echo secret-get",
    "cat <<'EOF'\nsecret-get obss-llm\nop read x\nEOF",
    "cat <<EOF\nrun secret-get obss-llm and op read x\nEOF",
    "echo \"$(date) secret-get\"",
    "FOO=secret-get true",
    "op",
    "secret-get2 obss-llm",
    "secret-gets",
    "not-secret-get obss-llm",
    "op -v",
    "op help",
    "op vault list --format json",
    "op item list --vault agent-keys",
    "op items list",
    "op item --vault agent-keys list",
    "op --account obss vault list",
    "op --format json --no-color item list",
    "op --cache --debug whoami",
    "op signin",
    "op run -- true",
    "op run --env-file .env -- true",
    "env op whoami",
    "time op vault list",
    "sh -c 'op whoami'",
    "op run -- printf %s --no-masking",
    "op run -- printf %s --no-masking=true",
    "op run --env-file .env -- sh -c 'echo --no-masking'",
    "op run -- env OP_FORMAT=json true",
    "op run -- printf \"%s\" \"$X\"",
    "op -- whoami",
    "OP_RUN_NO_MASKING_NOTE=1 true",
    "op 'r??d' x",
    "op item list '*'",
    "op item list *",
    "op vault list --format json *.json",
    "op run --env-file=.env -- true",
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
    "sudo -l secret-get",
    "printf 'secret-get fake-item\\n' > s.sh",
]


# Rows that spell no guarded name: the secret-read rule does not examine them,
# so each decides exactly as main does (allow).
NOT_GATED_ALLOW = [
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
    "myop read x",
    "/usr/bin/stop item get x",
    "oop read x",
    "export OP_FORMAT=json",
    "\"$HOME/bin/tool\" --flag",
    "\"${HOME}/bin/tool\" --flag",
    "\"${x:-/usr/bin}/true\"",
    "\"${a[0]}/true\"",
    "\"${a[*]}/true\"",
    "\"$*/true\"",
    "\"${#a}/true\"",
    "\"$(echo /bin)/true\"",
    "sudo -k",
    "sudo -K",
    "sudo -v",
    "sudo -V",
    "sudo -kv",
    "sudo -l",
    "sudo --list",
    "sudo -e /etc/hosts",
]


# Programs that run another program from their arguments, with a guarded name
# in the text. rg --pre, rg --hostname-bin and git grep -O ran a synthetic
# stand-in when measured. Each spells the name and is denied.
RUNS_PROGRAM = [
    "rg --pre synthmark secret-get README.md",
    "rg --pre=synthmark secret-get README.md",
    "rg --hostname-bin synthmark secret-get README.md",
    "git grep -O synthmark secret-get",
    "git grep -Osynthmark secret-get",
    "git grep -nOsynthmark secret-get",
    "git grep --open-files-in-pager=synthmark secret-get",
    "git grep --open-f=synthmark secret-get",
]

# Stated limits of the secret-read rule. Each id is named in the README; each
# row decides as main does (allow), because the rule does not examine it.
STATED_LIMITS = {
    # a guarded command reached by another name
    "SECRET-LIMIT-01": ["mykey fake-item", "/tmp/mykey fake-item"],
    # a script file: one command writes it without spelling the name, another
    # runs it (a write that spells the name is in SPELLED_HARMLESS: denied)
    "SECRET-LIMIT-02": ["printf '%s-get fake-item\\n' secret > s.sh", "sh s.sh"],
    # the name is not spelled in the text, so what a program, an env operand or
    # a configuration file builds is not examined (the last row is the
    # unspelled twin of SR-01)
    "SECRET-LIMIT-03": [
        "find . -maxdepth 0 -exec sec*et-get fake-item ';'",
        "python3 -c 'import os; os.system(\"sec\"+\"ret-get fake-item\")'",
        "env \"$(printf sec)ret-get\" fake-item",
        "printf '[diff]\\n\\texternal = %s-get synthitem\\n' secret >> .git/config && git show --ext-diff",
    ],
    # a launcher or with-secret child can print its own key
    "SECRET-LIMIT-04": ["with-secret obss-llm KEY printenv KEY"],
    # the boundary of the spelling test: it removes the quotes of $'' and $""
    # and leaves the `$`
    "SECRET-LIMIT-05": [
        "env secret-$''get synthitem",
        "env secret-$\"\"get synthitem",
    ],
    # not fixed here: the env-dump lexer class of issue 24, and `sudo -k env`
    # of issue 25. They pass on main and pass here.
    "ENV-LEXER-01": [
        "echo ${x:-'}'$(env)'}'} #'",
        "echo ${x:-{} ; env ; echo }",
        "printf 'env\\n' | bash /dev/stdin",
        "printf 'env\\n' | zsh -f /dev/stdin",
        "sh /dev/fd/0 <<'EOF'\nenv\nEOF",
        "printf 'env\\n' | BASH_ENV=/dev/stdin bash -c true",
        "{fd}>/dev/null env",
        "if [[ -n x ]] env",
        "if (( 1 )) env",
        "emulate sh -c env",
        "ENV",
        "BASH_CMDS[x]=$(command -v env); x",
        "commands[x]=$(command -v env); x",
        "functions[f]='env'; f",
        "aliases[x]=env; eval 'x'",
        "printf 'env\\n' | xargs -tJ% %",
        "printf 'env\\n' | xargs -tI% %",
        "x='$(env)'; printf '%s\\n' \"${x@P}\"",
        "x='a[$(env)]'; echo $((x))",
        "PS4='$(env) '; set -x; true",
        "mapfile -C 'env' -c 1 a <<< x",
    ],
    "ENV-SUDO-K-01": ["sudo -k env"],
}

# Supported list-shaped payloads (tool_input.command as an argv list): the hook
# joins it with shlex.join and reads it as one text. (argv, expected decision)
LIST_PAYLOADS = [
    (["secret-get", "fake-item"], "deny"),
    (["/tmp/x/bin/secret-get", "fake-item"], "deny"),
    (["op", "read", "op://fake-vault/fake-item/field"], "deny"),
    (["op", "item", "get", "fake-item"], "deny"),
    (["bash", "-lc", "secret-get fake-item"], "deny"),
    (["zsh", "-lc", "secret-get fake-item"], "deny"),
    (["bash", "-lc", "rg secret-get README.md"], "deny"),
    (["rg", "secret-get", "README.md"], "deny"),            # the seven mention forms as argv
    (["cat", "bin/secret-get"], "deny"),
    (["git", "log", "--", "bin/secret-get"], "deny"),
    (["op", "--version"], "deny"),
    (["op", "whoami"], "deny"),
    (["op", "vault", "list"], "deny"),
    (["op", "item", "list"], "deny"),
    (["echo", "secret-get"], "deny"),
    (["printf", "%s\\n", "it's op"], "deny"),               # a quoted element still spells the word
    (["git", "status"], "allow"),                 # spells no name: decided as main
    (["bash", "-lc", "git status && git diff"], "allow"),
]
