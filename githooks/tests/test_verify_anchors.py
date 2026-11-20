"""Exercise anchor verification against real git commits, with real and fabricated anchors."""

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / 'config/skills/pr-review2/scripts/verify_anchors.py'
SPEC = importlib.util.spec_from_file_location('verify_anchors', SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
# Keep fixture commits independent of the developer's git configuration and signing.
GIT_ENV = {**os.environ, 'GIT_CONFIG_GLOBAL': os.devnull, 'GIT_CONFIG_NOSYSTEM': '1',
           'GIT_AUTHOR_NAME': 'Fixture', 'GIT_AUTHOR_EMAIL': 'fixture@example.invalid',
           'GIT_COMMITTER_NAME': 'Fixture', 'GIT_COMMITTER_EMAIL': 'fixture@example.invalid'}
BASE_FILES = {
    'src/paging.py': 'def offset(page, size):\n    return page * size\n',
    'src/other.py': 'def helper():\n    return cache.get(key)\n',
    'src/removed.py': 'def legacy():\n    return 1\n',
}
HEAD_FILES = {
    'src/paging.py': ('def offset(page, size):\n    # pages start at one\n'
                      '    return (page - 1) * size\n\n\ndef limit(size):\n\treturn  size\n'),
    'src/pkg/mod.py': 'VALUE = 1\r\nOTHER = 2\r\n',
    'src/binary.dat': b'\xff\xfe\x00bad',
}
CHANGED = ['src/paging.py', 'src/pkg/mod.py', 'src/binary.dat', 'src/removed.py', 'src/link.py']


def git(repo, *args):
    return subprocess.run(['git', '-C', str(repo), *args], env=GIT_ENV, check=True,
                          capture_output=True).stdout.decode().strip()


def write(repo, files):
    for name, content in files.items():
        path = repo / name
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            path.write_bytes(content)
        else:
            path.write_bytes(content.encode())


def finding(id='F1', origin='change', route='finding', reasons=(), anchors=None):
    return {'id': id, 'severity': 'Minor', 'route': route, 'status': 'open', 'verified': True,
            'origin': origin, 'defect': True, 'reachable': True, 'evidence': ['static:trace'],
            'blocking_reasons': list(reasons),
            'anchors': anchors if anchors is not None else [
                {'path': 'src/paging.py', 'line': 3, 'quote': 'return (page - 1) * size'}]}


class VerifyAnchorsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.repo = Path(cls.temp.name) / 'repo'
        cls.repo.mkdir()
        git(cls.repo, 'init', '-q')
        write(cls.repo, BASE_FILES)
        git(cls.repo, 'add', '-A')
        git(cls.repo, 'commit', '-q', '-m', 'base')
        cls.base = git(cls.repo, 'rev-parse', 'HEAD')
        (cls.repo / 'src/removed.py').unlink()
        write(cls.repo, HEAD_FILES)
        (cls.repo / 'src/link.py').symlink_to('paging.py')
        git(cls.repo, 'add', '-A')
        git(cls.repo, 'commit', '-q', '-m', 'head')
        cls.head = git(cls.repo, 'rev-parse', 'HEAD')
        # An uncommitted edit: the verifier must read the head commit, not this working tree.
        (cls.repo / 'src/paging.py').write_text('worktree_only_line = True\n')

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def record(self, *findings, head=None, digest=None):
        return {'schema_version': 2, 'subject': {'base': self.base, 'head': head or self.head,
                                                 'patch_digest': digest},
                'findings': list(findings)}

    def check(self, *findings, changed=CHANGED, **options):
        return MODULE.check(self.record(*findings, **options), expected_head=self.head,
                            changed_files=list(changed), repo=self.repo)

    def problems(self, result):
        return [(item['finding'], item['anchor'], item['problem']) for item in result['mismatches']]

    def test_real_anchors_resolve_with_whitespace_normalisation(self):
        result = self.check(
            finding(),
            finding('F2', anchors=[{'path': 'src/paging.py', 'quote': 'return size'}]),
            finding('F3', anchors=[{'path': 'src/pkg/mod.py', 'line': 2, 'quote': 'OTHER = 2'}]),
            finding('F4', anchors=['changed:src/paging.py:6', {'path': 'src/paging.py', 'line': 6}]),
            finding('F5', origin='base', anchors=[
                {'path': 'src/other.py', 'quote': '  return   cache.get(key)  '}]))
        self.assertTrue(result['verified'], result)
        self.assertEqual([], result['mismatches'])
        resolved = {(item['finding'], item['anchor']): item['lines'] for item in result['resolved']}
        self.assertEqual({('F1', 0): [3], ('F2', 0): [7], ('F3', 0): [2], ('F4', 1): [6],
                          ('F5', 0): [2]}, resolved)
        self.assertEqual(['F4'], result['string_anchors'])

    def test_fabricated_or_misplaced_quotes_are_mismatches(self):
        cases = {
            'invented code': {'path': 'src/paging.py', 'quote': 'return page * size + 1'},
            'code from another file': {'path': 'src/paging.py', 'quote': 'return cache.get(key)'},
            'base-only line': {'path': 'src/paging.py', 'quote': 'return page * size'},
            'working-tree-only line': {'path': 'src/paging.py', 'quote': 'worktree_only_line = True'},
            'partial line': {'path': 'src/paging.py', 'quote': 'return (page - 1)'},
        }
        for label, anchor in cases.items():
            with self.subTest(label):
                result = self.check(finding(anchors=[anchor]))
                self.assertFalse(result['verified'])
                self.assertEqual([('F1', 0, 'quote not found at head')], self.problems(result))
                self.assertEqual('src/paging.py', result['mismatches'][0]['path'])

    def test_drifted_line_and_out_of_range_line_are_mismatches(self):
        result = self.check(finding(anchors=[
            {'path': 'src/paging.py', 'line': 2, 'quote': 'return (page - 1) * size'},
            {'path': 'src/paging.py', 'line': 99}]))
        self.assertEqual([('F1', 0, 'quote is at line(s) 3, not line 2'),
                          ('F1', 1, 'line beyond end of file (7 lines)')], self.problems(result))

    def test_unreadable_targets_are_mismatches_not_passes(self):
        cases = {
            'path absent at head': {'path': 'src/removed.py', 'quote': 'return 1'},
            'not a regular file at head': {'path': 'src/link.py', 'quote': 'paging.py'},
            'file is not UTF-8 text at head': {'path': 'src/binary.dat', 'line': 1},
        }
        for problem, anchor in cases.items():
            with self.subTest(problem):
                self.assertEqual([('F1', 0, problem)], self.problems(self.check(finding(anchors=[anchor]))))
        # Literal pathspecs: a glob-shaped anchor path never matches src/paging.py.
        result = self.check(finding(anchors=[{'path': 'src/*.py', 'quote': 'return (page - 1) * size'}]),
                            changed=CHANGED + ['src/*.py'])
        self.assertEqual([('F1', 0, 'path absent at head')], self.problems(result))
        # A directory is not a file, even when the path is in the changed set.
        result = self.check(finding(anchors=[{'path': 'src/pkg', 'line': 1}]), changed=CHANGED + ['src/pkg'])
        self.assertEqual([('F1', 0, 'not a regular file at head')], self.problems(result))

    def test_change_finding_needs_object_anchor_in_changed_file(self):
        unanchored = [
            [{'path': 'src/other.py', 'quote': 'return cache.get(key)'}],
            ['changed:src/paging.py:3'],
            [{'path': 'src/other.py'}, 'issue:321'],
        ]
        for anchors in unanchored:
            with self.subTest(anchors=anchors):
                result = self.check(finding(anchors=anchors))
                self.assertIn(('F1', None, 'no object anchor in a changed file'), self.problems(result))
        # A deleted changed file still anchors a finding about its removal; only quotes need head.
        self.assertTrue(self.check(finding(anchors=[{'path': 'src/removed.py'}]))['verified'])

    def test_scope_rule_exempts_only_contract_routes_and_non_change_findings(self):
        outside = [{'path': 'src/other.py', 'quote': 'return cache.get(key)'}]
        result = self.check(
            finding('F1', origin='base', anchors=outside),
            finding('F2', reasons=['unmet_requirement'], anchors=outside),
            finding('F3', reasons=['contradicted_claim'], anchors=['pr-body:testing-section']),
            finding('F4', route='observation', anchors=[]),
            finding('F5', route='carried', origin='unknown', anchors=outside))
        self.assertTrue(result['verified'], result)
        self.assertEqual(['F2', 'F3'], result['contract_admitted'])
        # introduced_defect or a gate failure is not a contract route: the line rule applies.
        for reason in ('introduced_defect', 'introduced_gate_failure', 'aspirational_doc'):
            with self.subTest(reason=reason):
                result = self.check(finding(reasons=[reason], anchors=outside))
                self.assertEqual([('F1', None, 'no object anchor in a changed file')], self.problems(result))
        # Exempt findings still get their quotes checked.
        result = self.check(finding(reasons=['unmet_requirement'],
                                    anchors=[{'path': 'src/other.py', 'quote': 'invented'}]))
        self.assertEqual([('F1', 0, 'quote not found at head')], self.problems(result))

    def test_invalid_input_is_refused(self):
        cases = {
            'dirty input': dict(record=self.record(finding(), digest='d' * 64)),
            'stale head': dict(record=self.record(finding(), head=self.base)),
            'malformed anchor': dict(record=self.record(finding(anchors=[{'path': 'src/paging.py',
                                                                          'qoute': 'x'}]))),
            'missing findings': dict(record={'subject': {'head': self.head, 'patch_digest': None}}),
            'bad changed path': dict(changed=['../escape.py']),
            'head not in repo': dict(expected_head='e' * 40, record=self.record(finding(), head='e' * 40)),
        }
        for label, override in cases.items():
            with self.subTest(label):
                params = {'record': self.record(finding()), 'expected_head': self.head,
                          'changed_files': CHANGED, 'repo': self.repo}
                params.update({('changed_files' if key == 'changed' else key): value
                               for key, value in override.items()})
                record = params.pop('record')
                with self.assertRaises(MODULE.InvalidRecord):
                    MODULE.check(record, **params)
        with tempfile.TemporaryDirectory() as directory, self.assertRaises(MODULE.InvalidRecord):
            MODULE.check(self.record(finding()), expected_head=self.head, changed_files=CHANGED,
                         repo=directory)

    def test_cli_exit_codes_and_machine_readable_output(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            artifact, changed = folder / 'review.json', folder / 'changed.json'
            changed.write_text(json.dumps(CHANGED))
            args = [sys.executable, '-I', str(SCRIPT), str(artifact), '--expected-head', self.head,
                    '--changed-files', str(changed), '--repo', str(self.repo)]
            cases = [
                (self.record(finding()), 0),
                (self.record(finding(anchors=[{'path': 'src/paging.py', 'quote': 'fake()'}])), 1),
                (self.record(finding(), digest='d' * 64), 2),
            ]
            for value, code in cases:
                artifact.write_text(json.dumps(value))
                result = subprocess.run(args, capture_output=True, text=True)
                self.assertEqual(code, result.returncode, result.stdout + result.stderr)
                output = json.loads(result.stdout)
                self.assertEqual(code == 0, output['verified'])
                self.assertEqual(code != 2, output['valid'])
                if code == 1:
                    self.assertEqual([{'finding': 'F1', 'anchor': 0, 'path': 'src/paging.py',
                                       'problem': 'quote not found at head'}], output['mismatches'])
            artifact.write_text('{"findings": [], "findings": []}')
            result = subprocess.run(args, capture_output=True, text=True)
            self.assertEqual(2, result.returncode)
            self.assertEqual(['duplicate JSON key'], json.loads(result.stdout)['errors'])


if __name__ == '__main__':
    unittest.main()
