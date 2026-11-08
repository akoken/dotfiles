"""Synthetic shell harness for the agent-env-guard tests.

Every shell runs with an explicit environment that holds only PATH (a shim
directory first, then /usr/bin:/bin), a temporary HOME and ZDOTDIR, LC_ALL
and a synthetic canary. User startup files are not read: bash gets
--noprofile --norc, zsh gets -f and an empty ZDOTDIR/HOME. zsh -f still
sources the system zshenv (/etc/zshenv, or /etc/zsh/zshenv on Debian), so
the profile check records whether one exists and verifies that PATH and the
canary are unchanged after startup.

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
            for name in os.listdir(cwd):
                if name != ".trace":
                    with open(os.path.join(cwd, name), encoding="utf-8", errors="replace") as fh:
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


def profile_key(shell):
    """Shell identity and major version, or None if the shell is absent."""
    argv = SHELL_ARGV[shell]
    if not os.path.exists(argv[0]):
        return None
    probe = 'printf "%s|%s" "${BASH_VERSION-}" "${ZSH_VERSION-}"'
    out = subprocess.run(argv + [probe], capture_output=True, text=True,
                         env={"PATH": "/usr/bin:/bin"}, timeout=10).stdout
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


def profiles():
    return {shell: key for shell in SHELL_ARGV if (key := profile_key(shell))}


def startup_report(sandbox):
    """Evidence that startup files did not change PATH or the canary."""
    report = {"system_zshenv": {p: os.path.exists(p) for p in SYSTEM_ZSHENV}}
    for shell in profiles():
        with tempfile.TemporaryDirectory(dir=sandbox.root) as cwd:
            trace = os.path.join(cwd, ".trace")
            env = sandbox.environment(trace)
            out = subprocess.run(
                SHELL_ARGV[shell] + ['printf "%s\\n%s" "$PATH" "$HOME"'], capture_output=True,
                text=True, env=env, cwd=cwd, timeout=10,
            ).stdout
            canary_name = subprocess.run(
                SHELL_ARGV[shell] + ['[ "$FAKE_TEST_API_KEY" = "$EXPECT" ] && echo same'],
                capture_output=True, text=True, env={**env, "EXPECT": CANARY}, cwd=cwd, timeout=10,
            ).stdout.strip()
        report[shell] = {
            "path_unchanged": out.split("\n")[0] == env["PATH"],
            "home_unchanged": out.split("\n")[-1] == env["HOME"],
            "canary_unchanged": canary_name == "same",
        }
    return report


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from agent_env_guard_shell_corpus import CASES

    box = Sandbox()
    try:
        keys = profiles()
        print(json.dumps({"profiles": keys, "startup": startup_report(box)}))
        for c in CASES:
            if c["run"]:
                print(json.dumps({"id": c["id"], **{keys[s]: box.run(s, c["command"]) for s in keys}}))
    finally:
        box.close()
