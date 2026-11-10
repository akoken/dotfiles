"""Pinned reference text for the agent-env-guard promise (W-1).

The guard makes one limited promise: the hook blocks the patterns it
recognises; a command that passes is not evidence of security. A scan for
misleading sentences cannot prove that no such sentence exists, so the text
that states the promise is pinned here instead, and tests/test_agent_env_guard.py
requires each surface to equal its reference exactly. Whitespace is the only
thing normalised (wrapping differs per surface; comment markers are removed
from comment blocks).

Changing the promise is deliberate: edit the surface and the reference in
the same commit, so the wording change is reviewed in one place.

Each surface paragraph is found by its opening words. If those words change
the paragraph is reported as missing, which fails the test the same way.
"""

import ast
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent

# The sentence every surface repeats.
PROMISE = (
    "The hook blocks the patterns it recognises; a command that passes is not "
    "evidence of security."
)

# Fixed frame of every deny message: "agent-env-guard: <reason>. " then
# DENY_HINT, a space and PROMISE. Only <reason> varies per denied form.
DENY_PREFIX = "agent-env-guard: "
DENY_HINT = (
    "Read a single variable with `printenv NAME` (or `[ -n \"${NAME+x}\" ]` to "
    "test presence), list processes without environments (`ps -o pid,ppid,command`), "
    "and pass values with `env NAME=value command`."
)

GUARD_DOCSTRING = (
    'This is a best-effort tripwire, not a security boundary. It blocks the '
    'dump commands it recognises, read by the lexing contract below for sh, '
    'bash and zsh, and refuses forms it cannot read (unknown syntax, options '
    'a wrapper table does not know, a command name it cannot resolve, '
    'exceeded size or nesting limits) with a short reason that never quotes '
    'the command. An allow only means that no recognised pattern matched. The '
    'hook blocks the patterns it recognises; a command that passes is not '
    'evidence of security. Known commands that still dump and pass are listed '
    'in the README ("Agent Secret Hygiene") and in '
    'tests/agent_env_guard_shell_corpus.py (KNOWN_LIMITS). '
)

GUARD_CONTRACT_COMMENT = (
    'Read as a tripwire (see the docstring): the contract says how the text '
    'is split. The hook blocks the patterns it recognises; a command that '
    'passes is not evidence of security. '
)

CORPUS_DOCSTRING = (
    '"No canary seen" never implies allow: the decision column is written out '
    'for every case. The harness checks it against the measured profiles: a '
    'case any profile marks visible or ran is denied unless it carries a '
    'KNOWN_LIMITS id, which records a known limitation (it dumps and the '
    'guard still passes it). The hook blocks the patterns it recognises; a '
    'command that passes is not evidence of security. An allow row in this '
    'corpus is no such evidence either. '
)

README_COMMAND_GUARD = (
    '**Command guard**: `bin/agent-env-guard` is a PreToolUse hook for Claude '
    'Code (`settings.json`) and Codex (`config.toml`) that denies '
    'whole-environment dumps (`env`, `printenv` with no name, `export -p`, '
    'bare `set`, `declare -x`/`-p`), `ps` with environment flags (`-E`, BSD '
    '`e` as in `ps eww`) and reads of `/proc/<pid>/environ`. Ordinary `ps`, '
    '`printenv NAME`, `env NAME=value command` and `env -u NAME command` '
    'still run. **It is a best-effort tripwire, not a security boundary**: it '
    'blocks the dump commands it recognises and refuses forms it cannot read '
    '(for example zsh glob qualifiers, ANSI-C escapes, a redirection before '
    'the command name, a command name built from a variable or a glob, an '
    'option a wrapper table does not know, `env -S`, a shell reading stdin, '
    'nesting or size over the limits), with a short reason that does not '
    'quote the command. An allow only means that no recognised pattern '
    'matched: the hook blocks the patterns it recognises; a command that '
    'passes is not evidence of security. Everyday forms such as `git status '
    '&& git diff`, `env FOO=1 true` and quoted here-documents pass. Codex '
    'runs the hook only after it is trusted with `/hooks`. Tests: `python3 -m '
    "unittest discover -s tests -p 'test_agent_env_guard.py'` (needs `sh`, "
    '`bash` and `zsh`; the shell corpus runs each case in a synthetic '
    'environment, never the real one). '
)


# surface name -> reference text
REFERENCE = {
    "guard docstring": GUARD_DOCSTRING,
    "guard contract comment": GUARD_CONTRACT_COMMENT,
    "corpus docstring": CORPUS_DOCSTRING,
    "README command guard bullet": README_COMMAND_GUARD,
}


def squash(text):
    """Collapse every whitespace run to one space; nothing else changes."""
    return re.sub(r"\s+", " ", text).strip()


def _paragraphs(text):
    return re.split(r"\n\s*\n", text)


def _one(found, surface):
    if len(found) != 1:
        raise AssertionError(f"{surface}: expected exactly one pinned paragraph, found {len(found)}")
    return found[0]


def guard_docstring(source):
    doc = ast.get_docstring(ast.parse(source), clean=True) or ""
    return _one([p for p in _paragraphs(doc) if p.startswith("This is a best-effort tripwire")],
                "guard docstring")


def guard_contract_comment(source):
    lines = source.splitlines()
    starts = [i for i, line in enumerate(lines) if line.startswith("# Read as a tripwire")]
    i = _one(starts, "guard contract comment")
    block = []
    while i < len(lines) and re.fullmatch(r"#.+", lines[i]):
        block.append(re.sub(r"^#\s?", "", lines[i]))
        i += 1
    return "\n".join(block)


def corpus_docstring(source):
    doc = ast.get_docstring(ast.parse(source), clean=True) or ""
    return _one([p for p in _paragraphs(doc) if p.startswith('"No canary seen"')],
                "corpus docstring")


def readme_command_guard(text):
    lines = text.splitlines()
    i = _one([n for n, line in enumerate(lines) if line.startswith("- **Command guard**")],
             "README command guard bullet")
    bullet = [lines[i][2:]]
    i += 1
    while i < len(lines) and lines[i].strip() and not lines[i].startswith("- "):
        bullet.append(lines[i])
        i += 1
    return "\n".join(bullet)


def surfaces(guard_source, corpus_source, readme_text):
    """Every pinned surface as {name: text actually found}."""
    return {
        "guard docstring": guard_docstring(guard_source),
        "guard contract comment": guard_contract_comment(guard_source),
        "corpus docstring": corpus_docstring(corpus_source),
        "README command guard bullet": readme_command_guard(readme_text),
    }


def pin_violations(guard_source, corpus_source, readme_text):
    """Names of the surfaces that do not equal their reference."""
    bad = []
    try:
        found = surfaces(guard_source, corpus_source, readme_text)
    except AssertionError as exc:
        return [str(exc)]
    for name, reference in REFERENCE.items():
        if squash(found[name]) != squash(reference):
            bad.append(name)
    return bad


def deny_frame_violations(reason):
    """Why a deny message is not <prefix><reason>. <hint> <promise>, if so."""
    tail = f". {DENY_HINT} {PROMISE}"
    if not reason.startswith(DENY_PREFIX):
        return ["prefix"]
    if not reason.endswith(tail):
        return ["tail"]
    if len(reason) == len(DENY_PREFIX) + len(tail) - 1:
        return ["empty reason"]
    return []
