#!/usr/bin/env python3
"""Check review-record finding anchors against the reviewed head commit.

Reads review.json, a trusted head SHA, a trusted changed-file list and a git
repository that contains the head commit. File content comes from the head
commit's tree through git, never from the working tree, and nothing in the
record is executed. Two checks run:

1. Every admitted change finding (route finding, origin change, not admitted
   through the contract with unmet_requirement, contradicted_claim or
   missing_issue) has at least one object anchor whose path is a changed file.
   String anchors cannot be located and do not count.
2. Every object anchor with a quote or a line resolves at head: the path is a
   regular UTF-8 file there, the quote equals a whole line after collapsing
   each whitespace run to one space and trimming both ends, and a given line
   number holds that quote (or exists, when the anchor has no quote).

Exit codes: 0 every check passed, 1 at least one mismatch (each names its
finding and anchor), 2 invalid input or git failure. A record with a patch
digest (dirty input) is refused with 2: its reviewed content is not a commit.
"""

import argparse
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

_SPEC = importlib.util.spec_from_file_location(
    'review_record', Path(__file__).resolve().parent / 'review_record.py')
record_tools = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(record_tools)
InvalidRecord, require = record_tools.InvalidRecord, record_tools.require

# Findings admitted through the linked contract or the PR body need no changed line.
CONTRACT_REASONS = {'unmet_requirement', 'contradicted_claim', 'missing_issue'}
REGULAR_MODES = (b'100644', b'100755')
# Literal pathspecs keep an anchor path from acting as a pattern; replace refs
# could otherwise substitute different objects for the reviewed commit.
GIT_ENV = {'GIT_LITERAL_PATHSPECS': '1', 'GIT_NO_REPLACE_OBJECTS': '1'}


def normalise(line):
    """Collapse whitespace runs to a single space and drop leading/trailing space."""
    return ' '.join(line.split())


class HeadTree:
    """Read files of one commit from a repository; cache each path's lines or problem."""

    def __init__(self, repo, head):
        self.repo, self.head, self.cache = repo, head, {}
        try:
            resolved = self.git('rev-parse', '--verify', '--quiet', head + '^{commit}')
        except InvalidRecord as error:
            raise InvalidRecord('head commit not found in repository: ' + str(error)) from error
        require(resolved.decode().strip() == head, 'head commit not found in repository')

    def git(self, *args):
        try:
            result = subprocess.run(['git', '-C', str(self.repo), *args], capture_output=True,
                                    env={**os.environ, **GIT_ENV}, check=False)
        except OSError as error:
            raise InvalidRecord('git unavailable: ' + str(error)) from error
        require(result.returncode == 0, 'git ' + args[0] + ' failed: '
                + result.stderr.decode(errors='replace').strip())
        return result.stdout

    def lines(self, path):
        """Return (lines, None) for a regular UTF-8 file at head, else (None, problem)."""
        if path not in self.cache:
            self.cache[path] = self.read(path)
        return self.cache[path]

    def read(self, path):
        wanted = os.fsencode(path)
        for entry in self.git('ls-tree', '-z', self.head, '--', path).split(b'\0'):
            meta, _, name = entry.partition(b'\t')
            if name != wanted:
                continue
            fields = meta.split(b' ')
            require(len(fields) == 3, 'unexpected git ls-tree output')
            mode, kind, obj = fields
            if kind != b'blob' or mode not in REGULAR_MODES:
                return None, 'not a regular file at head'
            data = self.git('cat-file', 'blob', obj.decode())
            if len(data) > record_tools.MAX_BYTES:
                return None, 'file exceeds size limit at head'
            try:
                content = data.decode('utf-8')
            except UnicodeDecodeError:
                return None, 'file is not UTF-8 text at head'
            # Count lines as git and editors do: split on newline only.
            parts = content.split('\n')
            return (parts[:-1] if content.endswith('\n') else parts), None
        return None, 'path absent at head'


def check(record, *, expected_head, changed_files, repo):
    """Return the JSON-ready result; raise InvalidRecord for unusable input."""
    try:
        require(isinstance(record, dict), 'record object')
        require(isinstance(expected_head, str) and record_tools.SHA.fullmatch(expected_head),
                'expected head')
        subject = record['subject']
        require(subject['head'] == expected_head, 'stale head')
        require(subject['patch_digest'] is None,
                'dirty input: anchors are checked only against a committed head')
        changed = record_tools.paths(changed_files, 'expected changed paths')
        findings = record_tools.object_list(record, 'findings')
        for finding in findings:
            require(finding['route'] in ('finding', 'observation', 'carried'), 'finding route')
            require(finding['origin'] in ('change', 'base', 'unknown'), 'finding origin')
            require(isinstance(finding['blocking_reasons'], list), 'blocking reasons')
            record_tools.anchors(finding['anchors'], 'finding anchors', finding['route'] == 'finding')
        tree = HeadTree(repo, expected_head)
        mismatches, resolved, exempt, unlocated = [], [], [], []

        def mismatch(finding, index, anchor, problem):
            mismatches.append({'finding': finding['id'], 'anchor': index,
                               'path': anchor['path'] if anchor else None, 'problem': problem})

        for finding in findings:
            located = [item for item in finding['anchors'] if isinstance(item, dict)]
            if len(located) < len(finding['anchors']):
                unlocated.append(finding['id'])
            if finding['route'] == 'finding' and finding['origin'] == 'change':
                if set(finding['blocking_reasons']) & CONTRACT_REASONS:
                    exempt.append(finding['id'])
                elif not any(item['path'] in changed for item in located):
                    mismatch(finding, None, None, 'no object anchor in a changed file')
            for index, anchor in enumerate(finding['anchors']):
                if not isinstance(anchor, dict) or not {'line', 'quote'} & set(anchor):
                    continue
                lines, problem = tree.lines(anchor['path'])
                if problem:
                    mismatch(finding, index, anchor, problem)
                    continue
                line = anchor.get('line')
                if 'quote' in anchor:
                    quote = normalise(anchor['quote'])
                    found = [number for number, text in enumerate(lines, 1) if normalise(text) == quote]
                    if not found:
                        mismatch(finding, index, anchor, 'quote not found at head')
                        continue
                    if line is not None and line not in found:
                        mismatch(finding, index, anchor, 'quote is at line(s) '
                                 + ', '.join(map(str, found)) + ', not line ' + str(line))
                        continue
                else:
                    if line > len(lines):
                        mismatch(finding, index, anchor,
                                 'line beyond end of file (' + str(len(lines)) + ' lines)')
                        continue
                    found = [line]
                resolved.append({'finding': finding['id'], 'anchor': index,
                                 'path': anchor['path'], 'lines': found})
        return {'valid': True, 'verified': not mismatches, 'head': expected_head,
                'mismatches': mismatches, 'resolved': resolved,
                'contract_admitted': sorted(exempt), 'string_anchors': sorted(set(unlocated)),
                'errors': []}
    except (KeyError, TypeError, AttributeError) as error:
        raise InvalidRecord('missing or malformed record field') from error


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('record', help='review.json to check')
    parser.add_argument('--expected-head', required=True,
                        help='full head SHA from a trusted target read')
    parser.add_argument('--changed-files', required=True,
                        help='JSON array of all changed paths from the verified diff')
    parser.add_argument('--repo', required=True,
                        help='git repository that contains the head commit')
    args = parser.parse_args()
    try:
        result = check(record_tools.read_json(args.record), expected_head=args.expected_head,
                       changed_files=record_tools.read_json(args.changed_files), repo=args.repo)
        print(json.dumps(result, sort_keys=True))
        return 0 if result['verified'] else 1
    except (InvalidRecord, OSError, ValueError, RecursionError) as error:
        message = str(error) if isinstance(error, InvalidRecord) else 'unreadable JSON input'
        print(json.dumps({'valid': False, 'verified': False, 'errors': [message]}, sort_keys=True))
        return 2


if __name__ == '__main__':
    sys.exit(main())
