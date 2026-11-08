"""Shell-coupled corpus for bin/agent-env-guard (ENV-GUARD-01).

Each case states the guard decision explicitly and, per verified shell
profile, what the shell does with the command in a synthetic environment
(PATH + a synthetic canary, no user startup files):

  visible      the canary reaches output or a file (a dump ran)
  ran          a dump command ran (shim trace) but its output was not seen
  none         no dump ran and the shell reported no syntax error
  parse_error  the shell rejected the command as a syntax error

"No canary seen" never implies allow: the decision column is written out for
every case, and the harness only checks that it is consistent (a case any
profile marks visible or ran must be denied).

Profiles are keyed by shell and major version (sh=bash3 is macOS /bin/sh,
sh=dash is Debian/Ubuntu /bin/sh). A profile missing from a case's table is
an unverified profile and fails the test instead of being guessed.

Cases with run=False are decision-only: they read /proc, need privileges or
never exit, so the harness never executes them.
"""

B = "\\"
NL = "\n"
C = B + NL  # line continuation

# A deny case whose dump no profile shows (no visible or ran) states why it
# is denied anyway; "no canary seen" is never a reason to allow:
#   builtin_suppressed  a builtin dump ran with its output discarded (the
#                       shims cannot trace builtins)
#   unknown             an operand or command text is only known at run time
#   branch              the dump sits in a branch this environment skipped
#   parse_error         the lexer refuses the text (unterminated construct)
WHY = {"builtin_suppressed", "unknown", "branch", "parse_error"}
CASES = []


def case(case_id, command, decision, why=None, run=True, sweep=False):
    CASES.append({
        "id": case_id, "command": command, "decision": decision,
        "why": why, "observed": {}, "run": run, "sweep": sweep,
    })


# Round 1 (fb9742f): unquoted here-document bodies
case("R1a", "cat <<EOF\n$(env)\nEOF", "deny", sweep=True)
case("R1b", "cat <<EOF\n`env`\nEOF", "deny", sweep=True)
case("R1c", "cat <<-EOF\n\t$(env)\n\tEOF", "deny", sweep=True)
case("R1d", "cat <<EOF\n'$(printenv)'\nEOF", "deny")
case("R1e", "cat <<EOF\nuser: $(echo $(env))\nEOF", "deny")
case("R1f", "cat <<EOF\n$(env | (cat))\nEOF", "deny")
case("R1g", "cat <<A <<B\nfirst\nA\n$(env)\nB", "deny", sweep=True)
case("R1h", "cat <<EOF > out.txt\n$(export -p)\nEOF", "deny")
case("R1i", "cat <<EOF\n$(ps eww)\nEOF", "deny")
case("R1j", "echo '<<EOF'\nenv\nEOF", "deny", sweep=True)
case("R1k", "echo hi # <<EOF\nenv\nEOF", "deny", sweep=True)
case("R1l", "cat <<EOF\n$(env\nEOF", "deny", why="parse_error")
# Round 2 (42bf64f): here-string and continuation in delimiters
case("R2a", 'cat <<<"$(env)"', "deny", sweep=True)
case("R2b", 'cat <<<"`env`"', "deny", sweep=True)
case("R2c", f"cat <<EO{C}F\nEOF\nenv", "deny", sweep=True)
case("R2d", f"cat <<EOF\nEO{C}F\nenv\n# EOF", "deny", sweep=True)
case("R2e", f"en{C}v", "deny", sweep=True)
case("R2f", "((x = 1 << 2))\nenv\n2", "deny", sweep=True)
case("R2g", f"cat <<-EOF\n\tEO{C}F\nenv\n# EOF", "deny")
case("R2h", f"cat <<{C}EOF\nx\nEOF\nenv", "deny")
case("R2i", 'echo "# <<EOF"\nenv\nEOF', "deny")
# Round 3 (f646c41): split here-string operator
case("R3", f'cat <{C}<<"$(env)"', "deny", sweep=True)
# Split operators
case("S1", f'cat <<{C}<"$(env)"', "deny")
case("S2", f'cat <{C}<{C}<"$(env)"', "deny")
case("S4", f'cat <<<{C}"$(env)"', "deny")
case("S5", f"cat <{C}<EOF\n$(env)\nEOF", "deny")
case("S7", f"cat <{C}<-EOF\n\t$(env)\n\tEOF", "deny")
case("S8", f"cat <<{C}-EOF\n\t$(env)\n\tEOF", "deny")
case("S9", f"cat <<-{C}EOF\n\t$(env)\n\tEOF", "deny")
case("S10", f"echo ${C}(env)", "deny", sweep=True)
case("S11", f'echo "${C}(env)"', "deny")
case("S12", f"echo $({C}env)", "deny")
case("S13", f'echo "$({C}env)"', "deny")
case("S14", f"echo ${C}((1<<2))\nenv\n2", "deny")
case("S15", f"echo `en{C}v`", "deny")
case("S16", f'echo "`en{C}v`"', "deny")
case("S17", f"false |{C}| env", "deny", sweep=True)
case("S18", f"true &{C}& env", "deny", sweep=True)
case("S20", f"true ;{C} env", "deny")
case("S21", f"true {C}; env", "deny")
case("S22", f"true ;{C}; env", "deny")
case("S23", f"echo x |{C} env", "deny", sweep=True)
case("S24", f"echo x {C}| env", "deny")
case("S26", f"env 2>{C}/dev/null", "deny")
# dash vs bash/zsh: delimiter reached through a continuation in the body
case("D1", f"cat <<EOF\nEO{C}F\necho '$(env)'\nEOF", "deny")
case("D2", f"cat <<EOF\nfoo{C}EOF\necho '$(env)'\nEOF", "deny")
case("D3", f"cat <<-EOF\n\tEO{C}\tF\necho '$(env)'\nEOF", "deny")
# Context: where continuation does not apply
case("C1", f"# c {C}env", "deny")
case("C2", f"echo a # c {C}env", "deny")
case("C3", f"echo 'a{C}' ; en{C}v", "deny")
case("C5", f"cat <<EOF\nEO{C}F\nenv\nEOF", "deny")
case("C6", "echo $'x\\' y' ; env ; echo 'z'", "deny")
case("C7", "echo $'a\\'' ; env", "deny")
case("C8", f"echo $'a{C}b' ; en{C}v", "deny")
# zsh code-running forms
case("Z1", 'echo /tmp(e:"env >&2":)', "deny")
case("Z2", "echo ${(e):-'$(env)'}", "deny")
case("Z3", "cat =(env)", "deny")
# Compound commands and reserved words
case("G1", "{ env; }", "deny", sweep=True)
case("G2", "if true; then env; fi", "deny", sweep=True)
case("G3", "for x in 1; do env; done", "deny")
case("G4", "! env", "deny")
case("G5", "f() { env; }; f", "deny")
case("G6", "while true; do env; break; done", "deny")
case("G7", "function f { env; }; f", "deny")
case("G8", "repeat 1 env", "deny")
case("G9", "nocorrect printenv", "deny")
case("G10", "case x in x) env;; esac", "deny")
case("G11", "echo $(case x in x) env;; esac)", "deny")
case("G12", "echo $( (env) )", "deny", sweep=True)
case("G13", "echo ${HOME:-$(env)}", "deny", why="branch")
case("G14", "a=(1 $(env)); echo ${a[@]}", "deny")
case("G15", "[[ -n $(env) ]] && echo set", "deny")
case("G16", "coproc env; wait", "deny")
# Dumps whose output is not seen: denied, still observable as ran / none
case("V1", 'cat <<A <<"B"\n$(env)\nA\nliteral\nB', "deny")
case("V2", "echo $(( $(env | grep -c SYNTH) ))", "deny")
case("V3", f"printenv {C}>/dev/null", "deny")
case("V4", f"x=$({C}env)", "deny")
case("V5", "printenv $(echo HOME)", "deny", why="unknown")
case("V6", "env $(true)", "deny")
case("V7", "export -p > /dev/null", "deny", why="builtin_suppressed")
case("V8", 'eval "$UNSET_COMMAND"', "deny", why="unknown")
case("V9", 'sh -c "$UNSET_COMMAND"', "deny", why="unknown")
case("V10", "printenv $UNSET_NAME", "deny")
# Process listings through the ps shim (the real ps never runs)
case("P1", "ps eww", "deny")
case("P2", "ps -wwE", "deny")
case("P3", f"ps -E{C}ww", "deny")
case("P4", "ps aux", "allow")
case("P5", "ps -o pid,command -p $$", "allow")
# Decision-only (never executed)
case("N1", "cat /proc/self/environ", "deny", run=False)
case("N2", f"cat /proc/self/envi{C}ron", "deny", run=False)
case("N3", "cat /proc/self/env*", "deny", run=False)
case("N4", "sudo ps -E", "deny", run=False)
# Literal, quoted and legitimate forms: allowed (explicit list)
case("A1", "cat <<'EOF'\n$(env)\nEOF", "allow", sweep=True)
case("A2", 'cat <<"EOF"\n`env`\nEOF', "allow")
case("A3", "cat <<E'OF'\n$(env)\nEOF", "allow")
case("A4", "cat <<\\EOF\n$(printenv)\nEOF", "allow")
case("A5", "cat <<-'EOF'\n\t$(env)\n\tEOF", "allow")
case("A6", "cat <<EOF\nbuilt $(date +%Y) on $(uname -s)\nEOF", "allow", sweep=True)
case("A7", "cat <<EOF\n$(env FOO=1 date +%Y)\nEOF", "allow")
case("A8", "cat <<EOF\nliteral \\$(env) and \\`env\\`\nEOF", "allow")
case("A9", "cat <<EOF\nHOME is $HOME\nEOF", "allow")
case("A10", 'cat <<<"$(date +%Y)"', "allow")
case("A11", "echo '$(env)'", "allow")
case("A12", "cat <<<'$(env)'", "allow")
case("A13", f"cat <<'EOF'\nEO{C}F\nenv\nEOF", "allow")
case("A14", f"cat <<'EO'{C}F\n$(env)\nEOF", "allow")
case("A15", f'cat <<"EOF"\nEOF{C}env\nEOF', "allow")
case("A16", "echo x#<<EOF\nenv\nEOF", "allow")
case("A17", "echo $((1 << 2))", "allow")
case("A18", 'printf "%s\\n" "$(date +%Y)"', "allow", sweep=True)
case("A19", f"env FOO=1 {C}  sh -c 'echo ok'", "allow", sweep=True)
case("A20", "env FOO=1 date +%Y", "allow")
case("A21", f"cat <{C}<'EOF'\n$(env)\nEOF", "allow")
case("A22", f"cat <{C}<<'$(env)'", "allow")
case("A23", "for env in a b; do echo $env; done", "allow")
case("A24", "a=(-e foo); echo ${a[1]}", "allow")
case("A25", "case $HOME in a) echo hi;; esac", "allow")
case("A26", "f() { echo hi; }; f", "allow")
case("A27", "printenv HOME", "allow")
case("A28", "env -u FOO sh -c 'echo ok'", "allow")
case("A29", "if [ -d . ]; then echo y; fi", "allow")
case("A30", 'export PATH="$HOME/bin:$PATH"', "allow")
case("A31", "x=$((1+2)); echo $x", "allow")
case("A32", "echo ${#PATH}", "allow")
# $(\<NL>( joins to $(( in every profile: arithmetic on a variable named env
case("A33", f"x=$({C}(env))", "allow")

# Measured categories per verified profile, in PROFILES order. Source:
# `python3 -I tests/agent_env_guard_harness.py` on macOS 27 (sh=bash3, bash3,
# zsh5) and on ubuntu:24.04 (sh=dash, bash5, zsh5; both zsh5 columns agree).
PROFILES = ("sh=bash3", "bash3", "zsh5", "sh=dash", "bash5")
OBSERVED = {
    "R1a": "visible visible visible visible visible",
    "R1b": "visible visible visible visible visible",
    "R1c": "visible visible visible visible visible",
    "R1d": "visible visible visible visible visible",
    "R1e": "visible visible visible visible visible",
    "R1f": "visible visible visible visible visible",
    "R1g": "visible visible visible visible visible",
    "R1h": "visible visible visible visible visible",
    "R1i": "ran ran ran ran ran",
    "R1j": "visible visible visible visible visible",
    "R1k": "visible visible visible visible visible",
    "R1l": "parse_error parse_error parse_error parse_error parse_error",
    "R2a": "visible visible visible parse_error visible",
    "R2b": "visible visible visible parse_error visible",
    "R2c": "visible visible visible visible visible",
    "R2d": "visible visible visible none visible",
    "R2e": "visible visible visible visible visible",
    "R2f": "visible visible visible none visible",
    "R2g": "visible visible visible none visible",
    "R2h": "visible visible visible visible visible",
    "R2i": "visible visible visible visible visible",
    "R3": "visible visible parse_error parse_error visible",
    "S1": "visible visible parse_error parse_error visible",
    "S2": "visible visible parse_error parse_error visible",
    "S4": "visible visible visible parse_error visible",
    "S5": "visible visible parse_error visible visible",
    "S7": "visible visible parse_error visible visible",
    "S8": "visible visible visible visible visible",
    "S9": "visible visible visible visible visible",
    "S10": "visible visible visible visible visible",
    "S11": "visible visible none visible visible",
    "S12": "visible visible visible visible visible",
    "S13": "visible visible visible visible visible",
    "S14": "visible visible visible visible visible",
    "S15": "visible visible visible visible visible",
    "S16": "visible visible visible visible visible",
    "S17": "visible visible parse_error visible visible",
    "S18": "visible visible parse_error visible visible",
    "S20": "visible visible visible visible visible",
    "S21": "visible visible visible visible visible",
    "S22": "parse_error parse_error visible parse_error parse_error",
    "S23": "visible visible visible visible visible",
    "S24": "visible visible visible visible visible",
    "S26": "visible visible visible visible visible",
    "D1": "none none none visible none",
    "D2": "visible visible visible visible visible",
    "D3": "visible visible visible visible visible",
    "C1": "visible visible visible visible visible",
    "C2": "visible visible visible visible visible",
    "C3": "visible visible visible visible visible",
    "C5": "visible visible visible none visible",
    "C6": "visible visible visible parse_error visible",
    "C7": "visible visible visible parse_error visible",
    "C8": "visible visible visible visible visible",
    "Z1": "parse_error parse_error visible parse_error parse_error",
    "Z2": "parse_error parse_error visible parse_error parse_error",
    "Z3": "parse_error parse_error visible parse_error parse_error",
    "G1": "visible visible visible visible visible",
    "G2": "visible visible visible visible visible",
    "G3": "visible visible visible visible visible",
    "G4": "visible visible visible visible visible",
    "G5": "visible visible visible visible visible",
    "G6": "visible visible visible visible visible",
    "G7": "visible visible visible parse_error visible",
    "G8": "none none visible none none",
    "G9": "none none visible none none",
    "G10": "visible visible visible visible visible",
    "G11": "parse_error parse_error visible visible visible",
    "G12": "visible visible visible visible visible",
    "G13": "none none none none none",
    "G14": "visible visible visible parse_error visible",
    "G15": "ran ran ran ran ran",
    "G16": "none none ran none ran",
    "V1": "ran ran visible ran ran",
    "V2": "ran ran ran ran ran",
    "V3": "ran ran ran ran ran",
    "V4": "ran ran ran ran ran",
    "V5": "none none none none none",
    "V6": "visible visible visible visible visible",
    "V7": "none none none none none",
    "V8": "none none none none none",
    "V9": "none none none none none",
    "V10": "visible visible visible visible visible",
    "P1": "ran ran ran ran ran",
    "P2": "ran ran ran ran ran",
    "P3": "ran ran ran ran ran",
    "P4": "none none none none none",
    "P5": "none none none none none",
    "A1": "none none none none none",
    "A2": "none none none none none",
    "A3": "none none none none none",
    "A4": "none none none none none",
    "A5": "none none none none none",
    "A6": "none none none none none",
    "A7": "none none none none none",
    "A8": "none none none none none",
    "A9": "none none none none none",
    "A10": "none none none parse_error none",
    "A11": "none none none none none",
    "A12": "none none none parse_error none",
    "A13": "none none none none none",
    "A14": "none none none none none",
    "A15": "none none none none none",
    "A16": "none none none none none",
    "A17": "none none none none none",
    "A18": "none none none none none",
    "A19": "none none none none none",
    "A20": "none none none none none",
    "A21": "none none parse_error none none",
    "A22": "none none parse_error parse_error none",
    "A23": "none none none none none",
    "A24": "none none none parse_error none",
    "A25": "none none none none none",
    "A26": "none none none none none",
    "A27": "none none none none none",
    "A28": "none none none none none",
    "A29": "none none none none none",
    "A30": "none none none none none",
    "A31": "none none none none none",
    "A32": "none none none none none",
    "A33": "none none none none none",
}

# A case missing here stays unmeasured ({}) and fails the table test.
for _case in CASES:
    if _case["run"] and _case["id"] in OBSERVED:
        _case["observed"] = dict(zip(PROFILES, OBSERVED[_case["id"]].split()))
