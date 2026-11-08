"""Synthetic shell harness for the agent-env-guard tests.

Every shell runs with an explicit environment that holds only PATH (a shim
directory first, then /usr/bin:/bin), a temporary HOME and ZDOTDIR, LC_ALL
and a synthetic canary. User startup files are not read: bash gets
--noprofile --norc, zsh gets -f and an empty ZDOTDIR/HOME. zsh -f still
sources the system zshenv (/etc/zshenv, or /etc/zsh/zshenv on Debian), so
the profile check records whether one exists and verifies that PATH and the
canary are unchanged after startup.

The startup surface is checked, not assumed (startup_report): after a shell
has started, the exported variable names must be the synthetic ones plus
the names the shell itself sets, every synthetic value must be unchanged,
no function may be defined, and zsh must show only its built-in default
aliases and the options -f and -c give it. A system zshenv that exported,
changed, aliased or set anything would fail that check.

The shims make dumps observable without real data: env and printenv record
a trace when they would dump and then run the real tool on the synthetic
environment; ps never runs the real ps, it records whether an environment
flag was given and prints a fixed line.

Run `python3 -I tests/agent_env_guard_harness.py` to print the measured
categories for this machine's profiles (used to review the corpus table).
"""

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

CANARY = "SYNTH-MARKER-corpus-4c1d"
SYNTAX_ERROR = re.compile(r"syntax error|parse error|unexpected|Syntax error|bad substitution|unmatched", re.I)

SHIM_ENV = r'''#!{python}
import os, sys
args = sys.argv[1:]
i = 0
while i < len(args):
    a = args[i]
    if a == "--":
        i += 1
        break
    if a in ("-u", "-C", "-P", "--unset", "--chdir"):
        i += 2
    elif a.startswith("-") and len(a) > 1:
        i += 1
    else:
        break
while i < len(args) and "=" in args[i] and not args[i].startswith("="):
    i += 1
if i >= len(args):
    with open(os.environ["GUARD_TRACE"], "a") as fh:
        fh.write("env-dump\n")
os.execv("/usr/bin/env", ["env"] + args)
'''

SHIM_PRINTENV = r'''#!{python}
import os, sys
if not [a for a in sys.argv[1:] if not a.startswith("-")]:
    with open(os.environ["GUARD_TRACE"], "a") as fh:
        fh.write("printenv-dump\n")
os.execv("/usr/bin/printenv", ["printenv"] + sys.argv[1:])
'''

SHIM_PS = r'''#!{python}
import os, sys
env_flag = False
for a in sys.argv[1:]:
    if a.startswith("-") and not a.startswith("--") and "E" in a[1:]:
        env_flag = True
    if not a.startswith("-") and a.isalpha() and "e" in a:
        env_flag = True
if env_flag:
    with open(os.environ["GUARD_TRACE"], "a") as fh:
        fh.write("ps-env\n")
print("  PID COMMAND")
print("    1 fake-ps-shim")
'''

SHELL_ARGV = {
    "sh": ["/bin/sh", "-c"],
    "bash": ["/bin/bash", "--noprofile", "--norc", "-c"],
    "zsh": ["/bin/zsh", "-f", "-c"],
}
SYSTEM_ZSHENV = ["/etc/zshenv", "/etc/zsh/zshenv"]


class Sandbox:
    def __init__(self):
        self.root = tempfile.mkdtemp(prefix="agent-env-guard-")
        self.shims = os.path.join(self.root, "shims")
        self.home = os.path.join(self.root, "home")
        os.makedirs(self.shims)
        os.makedirs(self.home)
        for name, body in (("env", SHIM_ENV), ("printenv", SHIM_PRINTENV), ("ps", SHIM_PS)):
            path = os.path.join(self.shims, name)
            with open(path, "w") as fh:
                fh.write(body.replace("{python}", sys.executable))
            os.chmod(path, 0o755)

    def close(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def environment(self, trace):
        return {
            "PATH": f"{self.shims}:/usr/bin:/bin",
            "HOME": self.home,
            "ZDOTDIR": self.home,
            "LC_ALL": "C",
            "FAKE_TEST_API_KEY": CANARY,
            "GUARD_TRACE": trace,
        }

    def run(self, shell, command):
        """Category of `command` under one shell (see the corpus docstring)."""
        with tempfile.TemporaryDirectory(dir=self.root) as cwd:
            trace = os.path.join(cwd, ".trace")
            open(trace, "w").close()
            proc = subprocess.run(
                SHELL_ARGV[shell] + [command], capture_output=True, text=True,
                env=self.environment(trace), cwd=cwd, timeout=20, stdin=subprocess.DEVNULL,
            )
            seen = proc.stdout + proc.stderr
            for folder, _dirs, names in os.walk(cwd):
                for name in names:
                    path = os.path.join(folder, name)
                    if path != trace and os.path.isfile(path):
                        with open(path, encoding="utf-8", errors="replace") as fh:
                            seen += fh.read()
            with open(trace) as fh:
                ran = fh.read().strip()
        if CANARY in seen:
            return "visible"
        if ran:
            return "ran"
        if SYNTAX_ERROR.search(proc.stderr):
            return "parse_error"
        return "none"


def profile_key(shell, sandbox):
    """Shell identity and major version, or None if the shell is absent.
    The probe runs in the same isolated environment as the corpus."""
    argv = SHELL_ARGV[shell]
    if not os.path.exists(argv[0]):
        return None
    probe = 'printf "%s|%s" "${BASH_VERSION-}" "${ZSH_VERSION-}"'
    with tempfile.TemporaryDirectory(dir=sandbox.root) as cwd:
        out = subprocess.run(argv + [probe], capture_output=True, text=True, cwd=cwd,
                             env=sandbox.environment(os.path.join(cwd, ".trace")), timeout=10).stdout
    bash_version, zsh_version = (out.split("|") + [""])[:2]
    if shell == "sh":
        if bash_version:
            return "sh=bash" + bash_version.split(".")[0]
        if os.path.realpath("/bin/sh").endswith("dash"):
            return "sh=dash"
        return "sh=unknown"
    if shell == "bash":
        return "bash" + bash_version.split(".")[0] if bash_version else "bash=unknown"
    return "zsh" + zsh_version.split(".")[0] if zsh_version else "zsh=unknown"


def profiles(sandbox):
    return {shell: key for shell in SHELL_ARGV if (key := profile_key(shell, sandbox))}


# Names a shell adds to the environment by itself (zsh also exports LOGNAME).
SHELL_EXPORTS = {"PWD", "OLDPWD", "SHLVL", "_", "LOGNAME"}
# What `zsh -f -c` shows with no startup file changing anything (measured on
# macOS and Ubuntu: identical).
ZSH_DEFAULT_OPTIONS = ["nohashdirs", "norcs"]
ZSH_DEFAULT_ALIASES = ["run-help=man", "which-command=whence"]
SURFACE_PROBE = {
    "zsh": "setopt; echo :aliases; alias; echo :functions; print -l ${(k)functions}",
    "bash": "echo :aliases; alias; echo :functions; declare -F",
    "sh": "echo :aliases; alias; echo :functions; (declare -F) 2>/dev/null",
}


def startup_report(sandbox):
    """What a started shell carries beyond the synthetic environment."""
    report = {"system_zshenv": {p: os.path.exists(p) for p in SYSTEM_ZSHENV}}
    for shell in profiles(sandbox):
        with tempfile.TemporaryDirectory(dir=sandbox.root) as cwd:
            env = sandbox.environment(os.path.join(cwd, ".trace"))
            run = lambda script, extra=None: subprocess.run(  # noqa: E731
                SHELL_ARGV[shell] + [script], capture_output=True, text=True,
                env={**env, **(extra or {})}, cwd=cwd, timeout=10, stdin=subprocess.DEVNULL,
            ).stdout
            # Names only; the absolute path bypasses the env shim.
            names = {line.split("=", 1)[0] for line in run("/usr/bin/env").splitlines() if "=" in line}
            unchanged = {
                name: run('[ "$(printenv %s)" = "$EXPECT" ] && echo same' % name,
                          {"EXPECT": value}).strip() == "same"
                for name, value in env.items()
            }
            surface = run(SURFACE_PROBE[shell])
        options, _, rest = surface.partition(":aliases\n")
        aliases, _, functions = rest.partition(":functions\n")
        report[shell] = {
            "extra_exports": sorted(names - set(env) - SHELL_EXPORTS),
            "changed_values": sorted(name for name, same in unchanged.items() if not same),
            "options": options.split(),
            "aliases": aliases.split(),
            "functions": functions.split(),
        }
    return report


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from agent_env_guard_shell_corpus import CASES

    box = Sandbox()
    try:
        keys = profiles(box)
        print(json.dumps({"profiles": keys, "startup": startup_report(box)}))
        for c in CASES:
            if c["run"]:
                print(json.dumps({"id": c["id"], **{keys[s]: box.run(s, c["command"]) for s in keys}}))
    finally:
        box.close()
