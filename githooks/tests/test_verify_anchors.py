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
    'src/repeat.py': 'retry()\nwait()\n  retry()\n',
    'src/empty.py': '',
    'src/blank.py': '\n',
    'src/no_newline.py': 'first\nlast',
}
CHANGED = ['src/paging.py', 'src/pkg/mod.py', 'src/binary.dat', 'src/removed.py', 'src/link.py',
           'src/repeat.py', 'src/empty.py', 'src/blank.py', 'src/no_newline.py']
VERIFIED = {'path': 'src/paging.py', 'line': 3, 'quote': 'return (page - 1) * size'}


def git(repo, *args):
    return subprocess.run(['git', '-C', str(repo), *args], env=GIT_ENV, check=True,
                          capture_output=True).stdout.decode().strip()


def write(repo, files):
    for name, content in files.items():
        path = repo / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content if isinstance(content, bytes) else content.encode())


def finding(id='F1', origin='change', route='finding', reasons=(), anchors=None):
    return {'id': id, 'severity': 'Minor', 'route': route, 'status': 'open', 'verified': True,
            'origin': origin, 'defect': True, 'reachable': True, 'evidence': ['static:trace'],
            'blocking_reasons': list(reasons),
            'anchors': anchors if anchors is not None else [dict(VERIFIED)]}


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

    def resolved(self, result):
        return {(item['finding'], item['anchor']): item['line'] for item in result['resolved']}

    def test_real_anchors_resolve_to_one_line_with_whitespace_normalisation(self):
        result = self.check(
            finding(),
            finding('F2', anchors=[{'path': 'src/paging.py', 'quote': 'return size'}]),
            finding('F3', anchors=[{'path': 'src/pkg/mod.py', 'line': 2, 'quote': 'OTHER = 2'}]),
            finding('F4', anchors=['changed:src/paging.py:6',
                                   {'path': 'src/paging.py', 'line': 6, 'quote': 'def limit(size):'}]),
            finding('F5', origin='base', anchors=[
                {'path': 'src/other.py', 'quote': '  return   cache.get(key)  '}]),
            finding('F6', anchors=[{'path': 'src/no_newline.py', 'quote': 'last'}]))
        self.assertTrue(result['verified'], result)
        self.assertEqual({('F1', 0): 3, ('F2', 0): 7, ('F3', 0): 2, ('F4', 1): 6, ('F5', 0): 2,
                          ('F6', 0): 2}, self.resolved(result))
        self.assertEqual([], result['file_level'])
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
                self.assertEqual([('F1', 0, 'quote not found at head'),
                                  ('F1', None, 'no verified quote in a changed file')],
                                 self.problems(result))
                self.assertEqual('src/paging.py', result['mismatches'][0]['path'])

    def test_drifted_line_is_a_mismatch(self):
        result = self.check(finding(anchors=[
            {'path': 'src/paging.py', 'line': 2, 'quote': 'return (page - 1) * size'}, dict(VERIFIED)]))
        self.assertEqual([('F1', 0, 'quote is at line(s) 3, not line 2')], self.problems(result))

    def test_repeated_quote_resolves_only_the_given_line_or_must_be_unique(self):
        # Regression: line 3 of a quote also on line 1 used to resolve as [1, 3].
        result = self.check(finding(anchors=[{'path': 'src/repeat.py', 'line': 3, 'quote': 'retry()'}]))
        self.assertTrue(result['verified'], result)
        self.assertEqual({('F1', 0): 3}, self.resolved(result))
        result = self.check(finding(anchors=[{'path': 'src/repeat.py', 'line': 1, 'quote': 'retry()'}]))
        self.assertEqual({('F1', 0): 1}, self.resolved(result))
        # Without a line the quote cannot pick a comment position, so it is not verified.
        result = self.check(finding(anchors=[{'path': 'src/repeat.py', 'quote': 'retry()'}]))
        self.assertEqual([('F1', 0, 'quote matches lines 1, 3; add line to pick one'),
                          ('F1', None, 'no verified quote in a changed file')], self.problems(result))
        self.assertEqual({}, self.resolved(result))
        result = self.check(finding(anchors=[{'path': 'src/repeat.py', 'line': 2, 'quote': 'retry()'}]))
        self.assertEqual([('F1', 0, 'quote is at line(s) 1, 3, not line 2'),
                          ('F1', None, 'no verified quote in a changed file')], self.problems(result))
        # Healthy neighbour: a unique line in the same file still resolves without a line.
        result = self.check(finding(anchors=[{'path': 'src/repeat.py', 'quote': 'wait()'}]))
        self.assertEqual({('F1', 0): 2}, self.resolved(result))

    def test_empty_blob_has_zero_lines(self):
        # Regression: a zero-byte file used to count as one empty line.
        tree = MODULE.CommitTree(self.repo, self.head)
        self.assertEqual(([], None), tree.lines('src/empty.py'))
        self.assertEqual(([''], None), tree.lines('src/blank.py'))
        self.assertEqual((['first', 'last'], None), tree.lines('src/no_newline.py'))
        result = self.check(finding(anchors=[{'path': 'src/empty.py', 'line': 1, 'quote': 'x'}]))
        self.assertIn(('F1', 0, 'quote not found at head'), self.problems(result))
        # A line without a quote proves nothing and is refused as malformed.
        with self.assertRaisesRegex(MODULE.InvalidRecord, 'anchor line'):
            self.check(finding(anchors=[{'path': 'src/empty.py', 'line': 1}]))

    def test_path_only_anchor_needs_unquotable_changed_file(self):
        # Regression: a quotable changed file anchored by path alone used to verify with nothing resolved.
        for path in ('src/paging.py', 'src/repeat.py', 'src/no_newline.py'):
            with self.subTest(path=path):
                result = self.check(finding(anchors=[{'path': path}]))
                self.assertFalse(result['verified'])
                self.assertEqual([('F1', None, 'no verified quote in a changed file')],
                                 self.problems(result))
                self.assertEqual([], result['file_level'])
        exceptions = {
            'src/removed.py': 'path absent at head',
            'src/link.py': 'not a regular file at head',
            'src/binary.dat': 'file is not UTF-8 text at head',
            'src/empty.py': 'no nonblank line at head',
            'src/blank.py': 'no nonblank line at head',
        }
        for path, reason in exceptions.items():
            with self.subTest(path=path):
                result = self.check(finding(anchors=[{'path': path}]))
                self.assertTrue(result['verified'], result)
                self.assertEqual([{'finding': 'F1', 'anchor': 0, 'path': path, 'reason': reason}],
                                 result['file_level'])
        # An unquotable file outside the changed set is no exception.
        result = self.check(finding(anchors=[{'path': 'src/removed.py'}]),
                            changed=[path for path in CHANGED if path != 'src/removed.py'])
        self.assertEqual([('F1', None, 'no verified quote in a changed file')], self.problems(result))
        # A verified quote makes extra path-only anchors irrelevant to the location check.
        result = self.check(finding(anchors=[dict(VERIFIED), {'path': 'src/other.py'}]))
        self.assertTrue(result['verified'], result)
        self.assertEqual([], result['file_level'])

    def test_unreadable_quote_targets_are_mismatches_not_passes(self):
        cases = {
            'path absent at head': {'path': 'src/removed.py', 'quote': 'return 1'},
            'not a regular file at head': {'path': 'src/link.py', 'quote': 'paging.py'},
            'file is not UTF-8 text at head': {'path': 'src/binary.dat', 'quote': 'bad'},
        }
        for problem, anchor in cases.items():
            with self.subTest(problem):
                result = self.check(finding(anchors=[anchor, dict(VERIFIED)]))
                self.assertEqual([('F1', 0, problem)], self.problems(result))
        # Literal pathspecs: a glob-shaped anchor path never matches src/paging.py.
        result = self.check(finding(anchors=[{'path': 'src/*.py', 'quote': 'return (page - 1) * size'},
                                             dict(VERIFIED)]), changed=CHANGED + ['src/*.py'])
        self.assertEqual([('F1', 0, 'path absent at head')], self.problems(result))
        # A directory is not a file, even when the path is in the changed set.
        result = self.check(finding(anchors=[{'path': 'src/pkg', 'quote': 'VALUE = 1'}, dict(VERIFIED)]),
                            changed=CHANGED + ['src/pkg'])
        self.assertEqual([('F1', 0, 'not a regular file at head')], self.problems(result))

    def test_change_finding_needs_verified_quote_in_changed_file(self):
        unanchored = [
            [{'path': 'src/other.py', 'quote': 'return cache.get(key)'}],
            ['changed:src/paging.py:3'],
            [{'path': 'src/other.py'}, 'issue:321'],
        ]
        for anchors in unanchored:
            with self.subTest(anchors=anchors):
                result = self.check(finding(anchors=anchors))
                self.assertEqual([('F1', None, 'no verified quote in a changed file')],
                                 self.problems(result))

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
                self.assertEqual([('F1', None, 'no verified quote in a changed file')],
                                 self.problems(result))
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
            'line without quote': dict(record=self.record(finding(anchors=[{'path': 'src/paging.py',
                                                                            'line': 3}]))),
            'missing findings': dict(record={'subject': {'head': self.head, 'patch_digest': None}}),
            'bad changed path': dict(changed_files=['../escape.py']),
            'head not in repo': dict(expected_head='e' * 40, record=self.record(finding(), head='e' * 40)),
        }
        for label, override in cases.items():
            with self.subTest(label):
                params = {'record': self.record(finding()), 'expected_head': self.head,
                          'changed_files': CHANGED, 'repo': self.repo}
                params.update(override)
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
                (self.record(finding(anchors=[{'path': 'src/paging.py', 'quote': 'fake()'},
                                              dict(VERIFIED)])), 1),
                (self.record(finding(), digest='d' * 64), 2),
            ]
            for value, code in cases:
                artifact.write_text(json.dumps(value))
                result = subprocess.run(args, capture_output=True, text=True)
                self.assertEqual(code, result.returncode, result.stdout + result.stderr)
                output = json.loads(result.stdout)
                self.assertEqual(code == 0, output['verified'])
                self.assertEqual(code != 2, output['valid'])
                if code == 0:
                    self.assertEqual([{'finding': 'F1', 'anchor': 0, 'path': 'src/paging.py',
                                       'line': 3, 'commit': self.head}], output['resolved'])
                if code == 1:
                    self.assertEqual([{'finding': 'F1', 'anchor': 0, 'path': 'src/paging.py',
                                       'problem': 'quote not found at head'}], output['mismatches'])
            artifact.write_text('{"findings": [], "findings": []}')
            result = subprocess.run(args, capture_output=True, text=True)
            self.assertEqual(2, result.returncode)
            self.assertEqual(['duplicate JSON key'], json.loads(result.stdout)['errors'])


VALIDATOR = ROOT / 'config/skills/pr-review2/scripts/review_record.py'


class ClosedFindingTests(unittest.TestCase):
    """A fix that restores a file to base removes it from the diff; its closed finding stays valid."""

    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.folder = Path(cls.temp.name)
        cls.repo = cls.folder / 'repo'
        cls.repo.mkdir()
        git(cls.repo, 'init', '-q')
        write(cls.repo, {'lib.py': 'def total(items):\n    return sum(items)\n', 'notes.md': 'v1\n'})
        git(cls.repo, 'add', '-A')
        git(cls.repo, 'commit', '-q', '-m', 'base')
        cls.base = git(cls.repo, 'rev-parse', 'HEAD')
        write(cls.repo, {'lib.py': 'def total(items):\n    return sum(items) + 1\n'})
        git(cls.repo, 'commit', '-q', '-am', 'previously reviewed head with the defect')
        cls.previous = git(cls.repo, 'rev-parse', 'HEAD')
        write(cls.repo, {'lib.py': 'def total(items):\n    return sum(items)\n', 'notes.md': 'v2\n'})
        git(cls.repo, 'commit', '-q', '-am', 'fix restores lib.py to base')
        cls.head = git(cls.repo, 'rev-parse', 'HEAD')
        changed = git(cls.repo, 'diff', '--name-only', cls.base, cls.head).split()
        assert changed == ['notes.md'], changed  # lib.py has left the diff entirely
        cls.changed = cls.folder / 'changed.json'
        cls.changed.write_text(json.dumps(changed))

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def record(self, status='fixed-and-verified', **anchor):
        quoted = {'path': 'lib.py', 'line': 2, 'quote': 'return sum(items) + 1',
                  'commit': self.previous}
        quoted.update(anchor)
        quoted = {key: value for key, value in quoted.items() if value is not None}
        active = status in ('open', 'deferred-with-rationale')
        return {
            'schema_version': 2, 'profile': 'general',
            'skill': {'name': 'pr-review2', 'version': '2.9.0', 'fingerprint': 'e' * 64},
            'subject': {'base': self.base, 'head': self.head, 'patch_digest': None},
            'contract': {'state': 'none', 'evidence': []},
            'coverage': {'mode': 'full', 'files': [
                {'path': 'notes.md', 'state': 'reviewed', 'evidence': ['static:notes.md:1']}],
                'dimensions_complete': True, 'context_complete': True,
                'baseline_head': None, 'delta_files': []},
            'rereview': {'previous_head': self.previous, 'prior_finding_ids': ['F1']},
            'checks': [], 'requirements': [], 'verification_gaps': [], 'stopped': None,
            'findings': [{'id': 'F1', 'severity': 'Minor', 'route': 'finding', 'status': status,
                          'verified': True, 'origin': 'change', 'defect': True, 'reachable': True,
                          'anchors': [quoted], 'evidence': ['static:lib.py restored to base at head'],
                          'blocking_reasons': ['introduced_defect']}],
            'claimed_verdict': 'REQUEST_CHANGES' if active else 'APPROVE',
            'claimed_run_status': 'complete'}

    def run_both(self, value):
        artifact = self.folder / 'review.json'
        artifact.write_text(json.dumps(value))
        validator = subprocess.run(
            [sys.executable, '-I', str(VALIDATOR), str(artifact), '--expected-profile', 'general',
             '--expected-base', self.base, '--expected-head', self.head, '--changed-files',
             str(self.changed), '--policy-known', '--expected-previous-head', self.previous],
            capture_output=True, text=True)
        verifier = subprocess.run(
            [sys.executable, '-I', str(SCRIPT), str(artifact), '--expected-head', self.head,
             '--changed-files', str(self.changed), '--repo', str(self.repo)],
            capture_output=True, text=True)
        return validator, verifier

    def test_closed_finding_on_file_that_left_the_diff_passes_both_clis(self):
        validator, verifier = self.run_both(self.record())
        self.assertEqual(0, validator.returncode, validator.stdout + validator.stderr)
        self.assertEqual('APPROVE', json.loads(validator.stdout)['verdict'])
        self.assertEqual(0, verifier.returncode, verifier.stdout + verifier.stderr)
        output = json.loads(verifier.stdout)
        self.assertEqual([{'finding': 'F1', 'anchor': 0, 'path': 'lib.py', 'line': 2,
                           'commit': self.previous}], output['resolved'])
        self.assertEqual([], output['mismatches'])

    def test_closed_quote_is_still_checked_at_its_commit(self):
        cases = {
            'quote absent at the bound commit': (dict(quote='return sum(items) + 2'),
                                                 'quote not found at ' + self.previous),
            'unbound quote defaults to the head': (dict(commit=None), 'quote not found at head'),
            'bound commit missing from repo': (dict(commit='f' * 40),
                                               'commit not found in repository: ' + 'f' * 40),
        }
        for label, (anchor, problem) in cases.items():
            with self.subTest(label):
                validator, verifier = self.run_both(self.record(**anchor))
                self.assertEqual(0, validator.returncode, validator.stdout)
                self.assertEqual(1, verifier.returncode, verifier.stdout + verifier.stderr)
                self.assertEqual([problem], [item['problem']
                                             for item in json.loads(verifier.stdout)['mismatches']])

    def test_active_finding_still_needs_a_quote_in_the_current_diff(self):
        for status in ('open', 'deferred-with-rationale'):
            with self.subTest(status=status):
                validator, verifier = self.run_both(self.record(status))
                self.assertEqual(1, validator.returncode, validator.stdout)
                self.assertEqual(1, verifier.returncode, verifier.stdout + verifier.stderr)
                self.assertEqual(
                    ['quote of an active finding is bound to ' + self.previous + ', not the head',
                     'no verified quote in a changed file'],
                    [item['problem'] for item in json.loads(verifier.stdout)['mismatches']])
        # Healthy neighbour: a rejected finding is closed too.
        validator, verifier = self.run_both(self.record('rejected-with-evidence'))
        self.assertEqual((0, 0), (validator.returncode, verifier.returncode), verifier.stdout)


if __name__ == '__main__':
    unittest.main()
