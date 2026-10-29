#!/usr/bin/env python3
"""Check the shared skill inventory and harness links using only the stdlib."""

import argparse
import os
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

HARNESSES = ('claude', 'codex', 'copilot', 'opencode')
REVIEW_SKILLS = ('code-review-expert2', 'pr-review2')
REVIEW_SHARED_FILES = (
    'references/review-protocol.md', 'references/mutation-testing.md',
    'references/security-routing.md', 'references/review-record.md',
    'scripts/review_record.py', 'references/focused-reviews.md',
)
# Inline links (including images) and reference-style link definitions.
LINK = re.compile(r'\[[^\]\n]*\]\(\s*(<[^>\n]+>|[^\s)]+)(?:\s+["\'][^\n]*?["\'])?\s*\)')
LINK_DEFINITION = re.compile(r'^\s{0,3}\[[^\]\n]+\]:\s*(<[^>\n]+>|\S+)', re.M)
RESOURCE = re.compile(r'(?<![\w.-])(?:references|scripts)/[^\s`"\'<>\[\](){}]*')
SKILL_REFERENCE = re.compile(
    r'`([a-z0-9]+(?:-[a-z0-9]+)*)`\s+skill\b|'
    r'\bskill\s+`([a-z0-9]+(?:-[a-z0-9]+)*)`', re.I)
REVIEW_EVAL = 'pr-review2/eval'
CLASS_KEY = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\.[a-z0-9]+(?:-[a-z0-9]+)*')
CLASS_COLUMNS = 6
SEEDED_SECTIONS = ('Class recognition', 'Instance recall')
CONTROL_SECTIONS = ('False blockers',)
RESULT_FIELDS = ('reviewer', 'skill-version', 'candidate-sha256', 'case', 'host', 'model')
RESULT_REVIEWER = 'pr-review2'
ANCHOR = re.compile(r'^\s*- \S+:\d+', re.M)


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


def section(text, heading):
    """Return the body under a level-2 heading, or None when it is absent."""
    match = re.search(rf'^## {re.escape(heading)}[ \t]*\n(.*?)(?=^## |\Z)', text, re.M | re.S)
    return match.group(1) if match else None


def case_list(cell):
    return [] if cell == 'none' else [name.strip() for name in cell.split(',') if name.strip()]


def lint_review_eval(evaluation, report):
    """Check eval case files, the defect class registry and recorded result headers."""
    case_root = evaluation / 'cases'
    cases = {path.name: path for path in case_root.iterdir() if path.is_dir()} \
        if case_root.is_dir() else {}
    for name, case in sorted(cases.items()):
        for required in ('input.md', 'oracle.md'):
            path = case / required
            if not path.is_file() or not path.read_text(encoding='utf-8').strip():
                report(path, 1, f'eval case requires nonempty {required}')

    registry = evaluation / 'classes.md'
    if not registry.is_file():
        report(registry, 1, 'missing defect class registry')
    else:
        keys = set()
        for number, line in enumerate(registry.read_text(encoding='utf-8').splitlines(), 1):
            if not line.startswith('|'):
                continue
            cells = [cell.strip() for cell in line.strip().strip('|').split('|')]
            if cells[0] == 'Key' or set(''.join(cells)) <= set('-: '):
                continue
            if len(cells) != CLASS_COLUMNS:
                report(registry, number, f'class row needs {CLASS_COLUMNS} columns')
                continue
            key, invariant, count, seeded, controls, target = cells
            key = key.strip('`')
            if not CLASS_KEY.fullmatch(key):
                report(registry, number, f'class key must be <surface>.<broken-invariant>: {key}')
                continue
            if key in keys:
                report(registry, number, f'duplicate class key: {key}')
            keys.add(key)
            if not invariant or not target:
                report(registry, number, f'class {key} requires an invariant and a target')
            if not count.isdigit() or int(count) < 1:
                report(registry, number, f'class {key} requires a positive seeded instance count')
            seeded_cases, control_cases = case_list(seeded), case_list(controls)
            if not seeded_cases:
                report(registry, number, f'class {key} requires a seeded case')
            invariant_words = key.split('.', 1)[1].split('-')
            leaks = (key, '-'.join(invariant_words), ' '.join(invariant_words))
            roles = [(name, SEEDED_SECTIONS) for name in seeded_cases]
            roles += [(name, CONTROL_SECTIONS) for name in control_cases]
            for name, headings in roles:
                if name not in cases:
                    report(registry, number, f'class {key} names unknown eval case: {name}')
                    continue
                if any(word in name.split('-') for word in invariant_words if len(word) >= 4):
                    report(registry, number, f'eval case name reveals class {key}: {name}')
                case_input = cases[name] / 'input.md'
                if case_input.is_file() and any(
                        leak in case_input.read_text(encoding='utf-8').lower() for leak in leaks):
                    report(case_input, 1, f'eval input reveals class {key}')
                oracle = cases[name] / 'oracle.md'
                if not oracle.is_file():
                    continue
                text = oracle.read_text(encoding='utf-8')
                for heading in headings:
                    if section(text, heading) is None:
                        report(oracle, 1, f'oracle for class {key} requires section: {heading}')
                recall = section(text, 'Instance recall')
                if headings is SEEDED_SECTIONS and recall is not None and count.isdigit():
                    found = len(ANCHOR.findall(recall))
                    if found != int(count):
                        report(oracle, 1, f'instance recall lists {found} path:line anchors; '
                                          f'class {key} registers {count}')
        if not keys:
            report(registry, 1, 'defect class registry has no class rows')

    results = evaluation / 'results'
    for result in sorted(results.glob('*.md')) if results.is_dir() else ():
        if result.name == 'README.md':
            continue
        header = {}
        for line in result.read_text(encoding='utf-8').splitlines():
            match = re.match(r'^([a-z0-9-]+):\s*(.*?)\s*$', line)
            if not match:
                break
            header[match.group(1)] = match.group(2)
        for field in RESULT_FIELDS:
            if not header.get(field):
                report(result, 1, f'result requires reviewer identity field: {field}')
        if header.get('reviewer') and header['reviewer'] != RESULT_REVIEWER:
            report(result, 1, f'result reviewer must be {RESULT_REVIEWER}')
        version, digest = header.get('skill-version'), header.get('candidate-sha256')
        if version and not re.fullmatch(r'\d+\.\d+\.\d+', version):
            report(result, 1, 'result skill-version must be a metadata.version like 2.5.0')
        if digest and not re.fullmatch(r'[0-9a-f]{64}', digest):
            report(result, 1, 'result candidate-sha256 must be 64 lowercase hex digits')
        if header.get('case') and header['case'] not in cases:
            report(result, 1, f'result names unknown eval case: {header["case"]}')


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

    if any(name in skills for name in REVIEW_SKILLS):
        for name in REVIEW_SKILLS:
            if name not in skills:
                report(shared / name / 'SKILL.md', 1, 'missing paired review skill')
        if all(name in skills for name in REVIEW_SKILLS):
            for relative in REVIEW_SHARED_FILES:
                left, right = (skills[name] / relative for name in REVIEW_SKILLS)
                if not left.is_file() or not right.is_file():
                    report(left if not left.is_file() else right, 1, 'missing shared review resource')
                elif left.read_bytes() != right.read_bytes():
                    report(right, 1, f'shared review resource differs from {REVIEW_SKILLS[0]}: {relative}')

    evaluation = shared / REVIEW_EVAL
    if evaluation.is_dir():
        lint_review_eval(evaluation, report)

    for harness in HARNESSES:
        directory = root / 'config' / harness / 'skills'
        if not directory.is_dir():
            report(directory, 1, 'missing harness skill directory')
            continue
        for link in sorted(directory.rglob('*')):
            if link.is_symlink() and not (link / 'SKILL.md').is_file():
                report(link, 1, 'dangling skill symlink or target lacks SKILL.md')
        for name in sorted(skills):
            if not (directory / name).is_symlink():
                report(directory, 1, f'missing harness link for skill: {name}')
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
