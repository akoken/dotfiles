#!/usr/bin/env python3
"""Check the shared skill inventory and harness links using only the stdlib."""

import argparse
import os
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

HARNESSES = ('claude', 'codex', 'copilot', 'opencode')
# Inline links (including images) and reference-style link definitions.
LINK = re.compile(r'\[[^\]\n]*\]\(\s*(<[^>\n]+>|[^\s)]+)(?:\s+["\'][^\n]*?["\'])?\s*\)')
LINK_DEFINITION = re.compile(r'^\s{0,3}\[[^\]\n]+\]:\s*(<[^>\n]+>|\S+)', re.M)
RESOURCE = re.compile(r'(?<![\w.-])(?:references|scripts)/[^\s`"\'<>\[\](){}]*')
SKILL_REFERENCE = re.compile(
    r'`([a-z0-9]+(?:-[a-z0-9]+)*)`\s+skill\b|'
    r'\bskill\s+`([a-z0-9]+(?:-[a-z0-9]+)*)`', re.I)


def frontmatter(text):
    """Read the required scalar fields; support quoted and block scalars."""
    lines = text.splitlines()
    if not lines or lines[0] != '---':
        return {}
    try:
        end = lines.index('---', 1)
    except ValueError:
        return {}
    fields = {}
    for index, line in enumerate(lines[1:end], 1):
        match = re.match(r'^(name|description):\s*(.*?)\s*$', line)
        if not match:
            continue
        key, value = match.groups()
        if re.fullmatch(r'[>|][+-]?', value):
            block = []
            for following in lines[index + 1:end]:
                if following and not following[0].isspace():
                    break
                block.append(following.strip())
            value = ' '.join(block).strip()
        elif value.startswith(('"', "'")):
            value = value[1:-1] if value.endswith(value[0]) else ''
        else:
            value = re.split(r'\s+#', value, maxsplit=1)[0].strip()
            if value in ('null', '~') or value.startswith('#'):
                value = ''
        fields[key] = value
    return fields


def lint(root):
    shared = root / 'config/skills'
    findings = []

    def report(path, line, message):
        findings.append(f'{path.relative_to(root)}:{line}: {message}')

    if not shared.is_dir():
        report(shared, 1, 'shared skill directory is missing')
        return findings
    executable = shared / 'agent-guard/bin/agent-guard'
    if not executable.is_file() or not os.access(executable, os.X_OK):
        report(executable, 1, 'agent-guard executable is missing or not executable')
    skills = {path.name: path for path in shared.iterdir() if path.is_dir()}
    for name, directory in sorted(skills.items()):
        entry = directory / 'SKILL.md'
        if not entry.is_file():
            report(entry, 1, 'missing SKILL.md')
            continue
        content = entry.read_text(encoding='utf-8')
        metadata = frontmatter(content)
        for field in ('name', 'description'):
            if not metadata.get(field):
                report(entry, 1, f'frontmatter requires {field}')
        if metadata.get('name') and metadata['name'] != name:
            report(entry, 1, f'frontmatter name must be {name}')

        targets = {}
        link_spans = []
        for pattern in (LINK, LINK_DEFINITION):
            for match in pattern.finditer(content):
                link_spans.append(match.span())
                target = match.group(1).strip('<>')
                parsed = urlsplit(target)
                if parsed.scheme or parsed.netloc or target.startswith(('/', '#')):
                    continue
                target = unquote(parsed.path)
                if target:
                    targets.setdefault(target, content.count('\n', 0, match.start()) + 1)
        for match in RESOURCE.finditer(content):
            if any(start <= match.start() < end for start, end in link_spans):
                continue
            # Absolute harness paths embed scripts/foo.py; resolve that suffix
            # against the current shared skill just like a local reference.
            target = unquote(urlsplit(match.group().rstrip('.,;:')).path)
            targets.setdefault(target, content.count('\n', 0, match.start()) + 1)
        for target, line in sorted(targets.items()):
            if not (directory / target).exists():
                report(entry, line, f'missing relative resource: {target}')

    for document in sorted(shared.rglob('*.md')):
        content = document.read_text(encoding='utf-8')
        for number, line in enumerate(content.splitlines(), 1):
            if '/Users/' in line:
                report(document, number, 'nonportable /Users/ path')
        for match in SKILL_REFERENCE.finditer(content):
            name = match.group(1) or match.group(2)
            if name not in skills:
                report(document, content.count('\n', 0, match.start()) + 1,
                       f'unknown skill: {name}')

    for harness in HARNESSES:
        directory = root / 'config' / harness / 'skills'
        if not directory.is_dir():
            report(directory, 1, 'missing harness skill directory')
            continue
        for link in sorted(directory.rglob('*')):
            if link.is_symlink() and not (link / 'SKILL.md').is_file():
                report(link, 1, 'dangling skill symlink or target lacks SKILL.md')
    return findings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fix-hint', action='store_true',
                        help='print a short repair hint before findings')
    args = parser.parse_args()
    if args.fix_hint:
        print('Fix shared skill metadata/resources and repoint harness links to config/skills.')
    findings = lint(Path(__file__).resolve().parents[1])
    for finding in findings:
        print(finding)
    if not findings:
        print('skills-lint: OK')
    return int(bool(findings))


if __name__ == '__main__':
    raise SystemExit(main())
