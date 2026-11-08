"""Exercise externally observable review-record safety decisions and CLI behavior."""

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / 'config/skills/code-review-expert2/scripts/review_record.py'
SPEC = importlib.util.spec_from_file_location('review_record', SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
BASE, HEAD, PRIOR = 'a' * 40, 'b' * 40, 'c' * 40


def record():
    return {
        'schema_version': 1, 'profile': 'general',
        'subject': {'base': BASE, 'head': HEAD, 'patch_digest': None},
        'contract': {'state': 'resolved', 'evidence': ['issue:321']},
        'coverage': {'mode': 'full', 'files': [
            {'path': 'src/paging.py', 'state': 'reviewed', 'evidence': ['static:src/paging.py:2']}
        ], 'dimensions_complete': True, 'context_complete': True,
            'baseline_head': None, 'delta_files': []},
        'checks': [{'id': 'tests', 'required': True, 'status': 'passed',
                    'attribution': 'not_applicable', 'head': HEAD, 'evidence': ['run:tests:exit-0']}],
        'findings': [],
        'requirements': [{'id': 'R1', 'text': 'First page starts at offset zero', 'state': 'met',
                          'implementation': ['src/paging.py:2'], 'verification': ['run:tests:exit-0']}],
        'verification_gaps': [], 'claimed_verdict': 'APPROVE',
    }


def finding(**overrides):
    value = {'id': 'F1', 'severity': 'Minor', 'route': 'finding', 'status': 'open',
             'verified': True, 'origin': 'change', 'defect': True, 'reachable': True,
             'anchors': ['changed:src/paging.py:2'], 'evidence': ['static:offset(1,10)=10'],
             'blocking_reasons': []}
    value.update(overrides)
    return value


class ReviewRecordTests(unittest.TestCase):
    def evaluate(self, value, **options):
        params = {'expected_profile': 'general', 'expected_base': BASE, 'expected_head': HEAD,
                  'changed_files': ['src/paging.py'], 'required_checks': ['tests'],
                  'policy_known': True}
        params.update(options)
        return MODULE.evaluate(value, **params)

    def test_untrusted_profile_cannot_bypass_self_or_peer_policy(self):
        value = record()
        value['findings'] = [finding(defect=False)]
        for profile in ('general', 'aura-peer'):
            with self.subTest(profile=profile):
                value['profile'] = profile
                with self.assertRaises(MODULE.InvalidRecord):
                    self.evaluate(value, expected_profile='aura-self')
        value = record()
        value['contract'] = {'state': 'missing_reference', 'evidence': ['missing issue']}
        with self.assertRaises(MODULE.InvalidRecord):
            self.evaluate(value, expected_profile='aura-peer')

    def test_general_no_contract_is_distinct_from_unavailable(self):
        value = record()
        value['contract'] = {'state': 'none', 'evidence': []}
        value['requirements'] = []
        self.assertEqual('APPROVE', self.evaluate(value)['verdict'])
        value['contract'] = {'state': 'unavailable', 'evidence': ['issue API unavailable']}
        value['claimed_verdict'] = 'NEEDS_REVIEW'
        self.assertEqual('NEEDS_REVIEW', self.evaluate(value)['verdict'])

    def test_reverted_delta_path_requires_documented_full_fallback(self):
        value = record()
        value['coverage'].update(mode='delta', baseline_head=PRIOR, delta_files=['src/reverted.py'])
        with self.assertRaisesRegex(MODULE.InvalidRecord, 'perform a full review'):
            self.evaluate(value, baseline_head=PRIOR, delta_files=['src/reverted.py'])
        value['coverage'].update(mode='full', baseline_head=None, delta_files=[])
        self.assertEqual('APPROVE', self.evaluate(value)['verdict'])

    def test_unavailable_general_contract_cannot_be_approved(self):
        for state in ('unavailable', 'missing_reference'):
            with self.subTest(state=state):
                value = record()
                value['contract']['state'] = state
                with self.assertRaises(MODULE.InvalidRecord):
                    self.evaluate(value)

    def test_complete_record_and_stale_revision(self):
        self.assertEqual('APPROVE', self.evaluate(record())['verdict'])
        with self.assertRaises(MODULE.InvalidRecord):
            self.evaluate(record(), expected_head=PRIOR)

    def test_missing_or_downgraded_required_security_check(self):
        value = record()
        value['claimed_verdict'] = 'NEEDS_REVIEW'
        result = self.evaluate(value, required_checks=['tests', 'security-diff'])
        self.assertEqual('NEEDS_REVIEW', result['verdict'])
        self.assertIn('missing required check: security-diff', result['incomplete_reasons'])
        value['checks'].append({'id': 'security-diff', 'required': False, 'status': 'passed',
                                'attribution': 'not_applicable', 'head': HEAD,
                                'evidence': ['specialist:report']})
        with self.assertRaises(MODULE.InvalidRecord):
            self.evaluate(value, required_checks=['tests', 'security-diff'])

    def test_unknown_policy_and_unreviewed_file_prevent_approval(self):
        value = record()
        with self.assertRaises(MODULE.InvalidRecord):
            self.evaluate(value, policy_known=False)
        value['claimed_verdict'] = 'NEEDS_REVIEW'
        self.assertEqual('NEEDS_REVIEW', self.evaluate(value, policy_known=False)['verdict'])
        value['coverage']['files'][0]['state'] = 'unreviewed'
        self.assertIn('unreviewed file', self.evaluate(value)['incomplete_reasons'])

    def test_requirement_mapping_cannot_claim_unverified_success(self):
        value = record()
        value['requirements'][0]['verification'] = []
        with self.assertRaises(MODULE.InvalidRecord):
            self.evaluate(value)
        value = record()
        value['requirements'][0]['state'] = 'unmet'
        value['claimed_verdict'] = 'REQUEST_CHANGES'
        self.assertIn('requirement:R1', self.evaluate(value)['blockers'])

    def test_author_recorded_criterion_is_met_and_disclosed(self):
        value = record()
        value['requirements'][0].update(
            text='The paid probe has run once and its result is recorded in docs/probe.md',
            implementation=['docs/probe.md:1-30'],
            verification=['author-recorded:docs/probe.md:1-30', 'author-recorded:pr-comment:42'],
            verification_basis='author-recorded')
        value['verification_gaps'] = [{'id': 'raw-probe-artifacts', 'material': False,
                                       'evidence': ['raw logs kept outside the repository']}]
        result = self.evaluate(value)
        self.assertEqual('APPROVE', result['verdict'])
        self.assertEqual(['R1'], result['author_recorded_requirements'])
        value['verification_gaps'][0]['material'] = True
        value['claimed_verdict'] = 'NEEDS_REVIEW'
        self.assertIn('material gap: raw-probe-artifacts', self.evaluate(value)['incomplete_reasons'])
        value = record()
        value['requirements'][0].update(state='unverified', verification=[],
                                        verification_basis='author-recorded')
        with self.assertRaisesRegex(MODULE.InvalidRecord, 'author-recorded basis requires'):
            self.evaluate(value)
        value['requirements'][0].update(state='met', verification=['doc:probe.md'],
                                        verification_basis='hearsay')
        with self.assertRaisesRegex(MODULE.InvalidRecord, 'verification basis'):
            self.evaluate(value)

    def test_minor_regression_blocks_even_without_declared_reason(self):
        value = record()
        value['findings'] = [finding()]
        value['claimed_verdict'] = 'REQUEST_CHANGES'
        self.assertIn('finding:F1', self.evaluate(value)['blockers'])
        value['findings'][0]['route'] = 'carried'
        with self.assertRaises(MODULE.InvalidRecord):
            self.evaluate(value)

    def test_defect_class_lists_instances_without_changing_verdict(self):
        value = record()
        value['findings'] = [finding(**{'class': 'missing null check',
                                        'instances': ['src/a.py:4', 'src/b.py:9', 'src/c.py:2']})]
        value['claimed_verdict'] = 'REQUEST_CHANGES'
        self.assertEqual(['finding:F1'], self.evaluate(value)['blockers'])
        for changes in ({'class': ''}, {'class': ['missing null check']}, {'instances': []},
                        {'instances': ['']}, {'instances': 'src/a.py:4'}, {'instances': None}):
            with self.subTest(changes=changes):
                value['findings'] = [finding(**dict({'class': 'missing null check',
                                                     'instances': ['src/a.py:4']}, **changes))]
                with self.assertRaises(MODULE.InvalidRecord):
                    self.evaluate(value)
        for field in ('class', 'instances'):
            with self.subTest(only=field):
                value['findings'] = [finding(**{field: {'class': 'missing null check',
                                                        'instances': ['src/a.py:4']}[field]})]
                with self.assertRaises(MODULE.InvalidRecord):
                    self.evaluate(value)

    def test_deferral_does_not_resolve_and_fixed_needs_evidence(self):
        value = record()
        value['findings'] = [finding(status='deferred-with-rationale')]
        value['claimed_verdict'] = 'REQUEST_CHANGES'
        self.assertTrue(self.evaluate(value)['blockers'])
        value['findings'][0]['status'] = 'fixed-and-verified'
        value['claimed_verdict'] = 'APPROVE'
        self.assertEqual('APPROVE', self.evaluate(value)['verdict'])
        value['findings'][0]['evidence'] = []
        with self.assertRaises(MODULE.InvalidRecord):
            self.evaluate(value)

    def test_peer_and_self_minor_quality_decisions_differ(self):
        value = record()
        value['profile'] = 'aura-peer'
        value['findings'] = [finding(defect=False)]
        self.assertEqual('APPROVE', self.evaluate(value, expected_profile='aura-peer')['verdict'])
        value['profile'] = 'aura-self'
        value['claimed_verdict'] = 'REQUEST_CHANGES'
        result = self.evaluate(value, expected_profile='aura-self')
        self.assertEqual([], result['blockers'])
        self.assertEqual(['F1'], result['self_disqualifying'])

    def test_failed_gate_attribution_and_partial_required_run(self):
        for attribution, verdict in [('introduced', 'REQUEST_CHANGES'),
                                     ('pre_existing', 'NEEDS_REVIEW'), ('unknown', 'NEEDS_REVIEW')]:
            with self.subTest(attribution=attribution):
                value = record()
                value['checks'][0].update(status='failed', attribution=attribution)
                value['claimed_verdict'] = verdict
                self.assertEqual(verdict, self.evaluate(value)['verdict'])
        for state in ('pending', 'unavailable', 'skipped'):
            with self.subTest(state=state):
                value = record()
                value['timing'] = {'elapsed_seconds': 5, 'active_review_seconds': 3,
                                   'verification_seconds': 4, 'ci_wait_seconds': None,
                                   'evidence': ['fixture timing log']}
                value['checks'][0]['status'] = state
                value['claimed_verdict'] = 'NEEDS_REVIEW'
                self.assertEqual('NEEDS_REVIEW', self.evaluate(value)['verdict'])

    def test_missing_issue_is_a_peer_blocker_and_a_self_gap(self):
        for profile, verdict in [('aura-peer', 'REQUEST_CHANGES'), ('aura-self', 'NEEDS_REVIEW')]:
            with self.subTest(profile=profile):
                value = record()
                value['profile'] = profile
                value['contract'] = {'state': 'missing_reference', 'evidence': ['PR body has no issue']}
                value['claimed_verdict'] = verdict
                self.assertEqual(verdict, self.evaluate(value, expected_profile=profile)['verdict'])

    def test_delta_cannot_hide_current_changes_as_prior_coverage(self):
        value = record()
        value['coverage'].update(mode='delta', baseline_head=PRIOR, delta_files=['src/paging.py'])
        self.assertEqual('APPROVE', self.evaluate(value, baseline_head=PRIOR,
                                                delta_files=['src/paging.py'])['verdict'])
        value['coverage']['files'][0]['state'] = 'baseline'
        with self.assertRaises(MODULE.InvalidRecord):
            self.evaluate(value, baseline_head=PRIOR, delta_files=['src/paging.py'])

    def test_dirty_digest_and_file_identity_are_bound(self):
        value = record()
        value['subject']['patch_digest'] = 'd' * 64
        with self.assertRaises(MODULE.InvalidRecord):
            self.evaluate(value)
        self.assertEqual('APPROVE', self.evaluate(value, expected_patch_digest='d' * 64)['verdict'])
        with self.assertRaises(MODULE.InvalidRecord):
            self.evaluate(value, changed_files=['src/other.py'], expected_patch_digest='d' * 64)

    def test_malformed_fields_and_duplicate_ids_fail_closed(self):
        value = record()
        value['coverage']['dimensions_complete'] = 'yes'
        with self.assertRaises(MODULE.InvalidRecord):
            self.evaluate(value)
        value = record()
        value['checks'].append(copy.deepcopy(value['checks'][0]))
        with self.assertRaises(MODULE.InvalidRecord):
            self.evaluate(value)

    def test_empty_target_cannot_gain_approval(self):
        value = record()
        value['coverage']['files'] = []
        value['claimed_verdict'] = 'NEEDS_REVIEW'
        self.assertIn('no changed files', self.evaluate(value, changed_files=[])['incomplete_reasons'])

    def test_json_reader_rejects_nonfinite_and_oversized_inputs(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'record.json'
            path.write_text('{"value": NaN}')
            with self.assertRaises(MODULE.InvalidRecord):
                MODULE.read_json(path)
            path.write_bytes(b' ' * (MODULE.MAX_BYTES + 1))
            with self.assertRaises(MODULE.InvalidRecord):
                MODULE.read_json(path)

    def test_timing_records_overlap_and_preserves_unknowns_and_verdict(self):
        value = record()
        value['timing'] = {'elapsed_seconds': 180, 'active_review_seconds': 100,
                           'verification_seconds': 90, 'ci_wait_seconds': None,
                           'evidence': ['review-clock.jsonl:1-12']}
        result = self.evaluate(value)
        self.assertEqual('APPROVE', result['verdict'])
        self.assertEqual(value['timing'], result['timing'])
        # Concurrent categories may legitimately sum to more than elapsed time.
        value['timing'] = {key: None for key in value['timing']}
        value['timing']['evidence'] = ['No timing clock was available']
        self.assertEqual('APPROVE', self.evaluate(value)['verdict'])
        del value['timing']
        self.assertNotIn('timing', self.evaluate(value))

    def test_timing_rejects_fabrication_shaped_or_inconsistent_values(self):
        template = {'elapsed_seconds': 180, 'active_review_seconds': 100,
                    'verification_seconds': 90, 'ci_wait_seconds': None,
                    'evidence': ['review-clock.jsonl:1-12']}
        for field in ('elapsed_seconds', 'active_review_seconds', 'verification_seconds', 'ci_wait_seconds'):
            for seconds in (True, -1, float('inf'), float('nan'), '12'):
                with self.subTest(field=field, seconds=seconds):
                    value = record()
                    value['timing'] = dict(template, **{field: seconds})
                    with self.assertRaises(MODULE.InvalidRecord):
                        self.evaluate(value)
        for changes in ({'ci_wait_seconds': 181}, {'evidence': []}, {'evidence': ['']}):
            value = record()
            value['timing'] = dict(template, **changes)
            with self.assertRaises(MODULE.InvalidRecord):
                self.evaluate(value)
        value = record()
        value['timing'] = dict(template)
        del value['timing']['elapsed_seconds']
        with self.assertRaises(MODULE.InvalidRecord):
            self.evaluate(value)

    def test_short_timing_does_not_clear_pending_required_gate(self):
        value = record()
        value['timing'] = {'elapsed_seconds': 0, 'active_review_seconds': 0,
                           'verification_seconds': 0, 'ci_wait_seconds': 0,
                           'evidence': ['Clock observed an immediate fixture result']}
        value['checks'][0]['status'] = 'pending'
        value['claimed_verdict'] = 'NEEDS_REVIEW'
        self.assertEqual('NEEDS_REVIEW', self.evaluate(value)['verdict'])

    def test_cli_returns_machine_readable_safe_exit_codes(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            artifact = folder / 'review.json'
            changed = folder / 'changed.json'
            changed.write_text(json.dumps(['src/paging.py']))
            args = [sys.executable, str(SCRIPT), str(artifact), '--expected-profile', 'general', '--expected-base', BASE,
                    '--expected-head', HEAD, '--changed-files', str(changed),
                    '--require-check', 'tests', '--policy-known']
            for state, expected_code in [('passed', 0), ('pending', 1)]:
                value = record()
                value['timing'] = {'elapsed_seconds': 5, 'active_review_seconds': 3,
                                   'verification_seconds': 4, 'ci_wait_seconds': None,
                                   'evidence': ['fixture timing log']}
                value['checks'][0]['status'] = state
                value['claimed_verdict'] = 'APPROVE' if state == 'passed' else 'NEEDS_REVIEW'
                artifact.write_text(json.dumps(value))
                result = subprocess.run(args, capture_output=True, text=True)
                self.assertEqual(expected_code, result.returncode, result.stdout + result.stderr)
                self.assertTrue(json.loads(result.stdout)['valid'])
                self.assertEqual(value['timing'], json.loads(result.stdout)['timing'])
            artifact.write_text('{"schema_version":1,"schema_version":1}')
            result = subprocess.run(args, capture_output=True, text=True)
            self.assertEqual(2, result.returncode)
            self.assertFalse(json.loads(result.stdout)['valid'])
            self.assertEqual('NEEDS_REVIEW', json.loads(result.stdout)['verdict'])


SKILL_FILES = {'SKILL.md': 'name: demo\n', 'references/a.md': 'alpha\n',
               'scripts/tool.py': 'print(1)\n'}


def identity(**overrides):
    value = {'name': 'pr-review2', 'version': '2.7.0', 'fingerprint': 'e' * 64}
    value.update(overrides)
    return value


def rereview_record(*presence):
    value = record()
    value['rereview'] = {'previous_head': PRIOR, 'prior_finding_ids': ['F0']}
    value['findings'] = [finding(id='F0', status='fixed-and-verified')]
    for number, state in enumerate(presence, 1):
        value['findings'].append(finding(id=f'F{number}', origin='base', defect=False,
                                         present_at_previous_head=state))
    return value


class SkillIdentityTests(unittest.TestCase):
    evaluate = ReviewRecordTests.evaluate

    def write_skill(self, root, files=SKILL_FILES):
        for name, content in files.items():
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)

    def test_legacy_record_without_identity_still_validates(self):
        legacy = json.loads(json.dumps(record()))
        self.assertNotIn('skill', legacy)
        result = self.evaluate(legacy)
        self.assertEqual('APPROVE', result['verdict'])
        self.assertIsNone(result['skill'])
        self.assertNotIn('new_findings_present_at_previous_head', result)
        legacy['skill'] = None
        self.assertIsNone(self.evaluate(legacy)['skill'])

    def test_recorded_identity_is_reported_and_matches_expectations(self):
        value = record()
        value['skill'] = identity()
        result = self.evaluate(value, expected_skill_version='2.7.0',
                               expected_skill_fingerprint='e' * 64)
        self.assertEqual('APPROVE', result['verdict'])
        self.assertEqual(identity(), result['skill'])
        self.assertEqual(identity(), self.evaluate(value)['skill'])

    def test_malformed_or_mismatched_identity_is_rejected(self):
        cases = [
            ({'version': 'v2.7'}, {}, 'skill version'),
            ({'version': 270}, {}, 'skill version'),
            ({'version': '\uff12.7.0'}, {}, 'skill version'),
            ({'fingerprint': 'E' * 64}, {}, 'skill fingerprint'),
            ({'fingerprint': 'e' * 40}, {}, 'skill fingerprint'),
            ({'name': ' '}, {}, 'skill name'),
            ({}, {'expected_skill_version': '2.6.0'}, 'version differs'),
            ({}, {'expected_skill_fingerprint': 'f' * 64}, 'fingerprint differs'),
            ({}, {'expected_skill_version': 'latest'}, 'expected skill version'),
            ({}, {'expected_skill_fingerprint': 'abc'}, 'expected skill fingerprint'),
        ]
        for overrides, options, message in cases:
            with self.subTest(overrides=overrides, options=options):
                value = record()
                value['skill'] = identity(**overrides)
                with self.assertRaisesRegex(MODULE.InvalidRecord, message):
                    self.evaluate(value, **options)
        for skill in ({'name': 'pr-review2', 'version': '2.7.0'}, 'pr-review2', []):
            with self.subTest(skill=skill):
                value = record()
                value['skill'] = skill
                with self.assertRaises(MODULE.InvalidRecord):
                    self.evaluate(value)

    def test_expected_identity_refuses_a_legacy_record(self):
        for options in ({'expected_skill_version': '2.7.0'},
                        {'expected_skill_fingerprint': 'e' * 64}):
            with self.subTest(options=options):
                with self.assertRaisesRegex(MODULE.InvalidRecord, 'identity absent'):
                    self.evaluate(record(), **options)

    def test_fingerprint_covers_package_and_ignores_eval_and_caches(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_skill(root)
            first = MODULE.skill_fingerprint(root)
            self.assertRegex(first, r'^[0-9a-f]{64}$')
            lines = ''.join(f"{hashlib.sha256(SKILL_FILES[name].encode()).hexdigest()}  {name}\n"
                            for name in sorted(SKILL_FILES))
            self.assertEqual(hashlib.sha256(lines.encode()).hexdigest(), first)
            self.write_skill(root, {'eval/cases/x/oracle.md': 'hidden\n',
                                    'tests/test_x.py': 'outside package\n',
                                    'scripts/__pycache__/tool.cpython-312.pyc': 'cache',
                                    'references/.DS_Store': 'finder'})
            self.assertEqual(first, MODULE.skill_fingerprint(root))
            self.write_skill(root, {'references/a.md': 'alpha changed\n'})
            self.assertNotEqual(first, MODULE.skill_fingerprint(root))
            for extra in ('references/b.md', 'scripts/.hidden.py', 'scripts/stale.pyc'):
                with self.subTest(extra=extra):
                    self.write_skill(root, {'references/a.md': 'alpha\n', extra: 'new\n'})
                    self.assertNotEqual(first, MODULE.skill_fingerprint(root))
                    (root / extra).unlink()
            self.assertEqual(first, MODULE.skill_fingerprint(root))

    def test_fingerprint_refuses_record_separators_in_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            left, right = Path(directory) / 'left', Path(directory) / 'right'
            first, second = 'first reference\n', 'second reference\n'
            self.write_skill(left, {'SKILL.md': 'name: demo\n', 'references/a.md': first,
                                    'references/b.md': second})
            digest = hashlib.sha256(second.encode()).hexdigest()
            self.write_skill(right, {'SKILL.md': 'name: demo\n',
                                     f'references/a.md\n{digest}  references/b.md': first})
            with self.assertRaisesRegex(MODULE.InvalidRecord, 'control character'):
                MODULE.skill_fingerprint(right)
            self.assertRegex(MODULE.skill_fingerprint(left), r'^[0-9a-f]{64}$')
            for number, name in enumerate(('references/tab\there.md', 'references/cr\rhere.md')):
                with self.subTest(name=name):
                    other = Path(directory) / f'other-{number}'
                    self.write_skill(other, {'SKILL.md': 'name: demo\n', name: first})
                    with self.assertRaisesRegex(MODULE.InvalidRecord, 'control character'):
                        MODULE.skill_fingerprint(other)

    def test_fingerprint_refuses_missing_entry_and_symlinks(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaisesRegex(MODULE.InvalidRecord, 'lacks SKILL.md'):
                MODULE.skill_fingerprint(root)
            self.write_skill(root)
            (root / 'references/link.md').symlink_to(root / 'references/a.md')
            with self.assertRaisesRegex(MODULE.InvalidRecord, 'symlink'):
                MODULE.skill_fingerprint(root)
            (root / 'references/link.md').unlink()
            (root / 'references/nested').symlink_to(root / 'scripts', target_is_directory=True)
            with self.assertRaisesRegex(MODULE.InvalidRecord, 'symlink'):
                MODULE.skill_fingerprint(root)
            for empty in ('', ' '):
                with self.assertRaisesRegex(MODULE.InvalidRecord, 'skill directory'):
                    MODULE.skill_fingerprint(empty)

    def test_cli_prints_fingerprint_and_checks_expected_version(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            self.write_skill(folder / 'skill')
            result = subprocess.run([sys.executable, str(SCRIPT), '--skill-fingerprint',
                                     str(folder / 'skill')], capture_output=True, text=True)
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual(MODULE.skill_fingerprint(folder / 'skill'), result.stdout.strip())
            result = subprocess.run([sys.executable, str(SCRIPT), '--skill-fingerprint', str(folder)],
                                    capture_output=True, text=True)
            self.assertEqual(2, result.returncode)
            artifact, changed = folder / 'review.json', folder / 'changed.json'
            changed.write_text(json.dumps(['src/paging.py']))
            value = record()
            value['skill'] = identity()
            artifact.write_text(json.dumps(value))
            args = [sys.executable, str(SCRIPT), str(artifact), '--expected-profile', 'general',
                    '--expected-base', BASE, '--expected-head', HEAD, '--changed-files', str(changed),
                    '--require-check', 'tests', '--policy-known']
            for extra, code in [(['--expected-skill-version', '2.7.0'], 0),
                                (['--expected-skill-version', '2.6.0'], 2),
                                (['--expected-skill-fingerprint', 'e' * 64], 0),
                                (['--expected-skill-fingerprint', 'f' * 64], 2),
                                (['--expected-previous-head', PRIOR], 2)]:
                with self.subTest(extra=extra):
                    result = subprocess.run(args + extra, capture_output=True, text=True)
                    self.assertEqual(code, result.returncode, result.stdout + result.stderr)
            value['rereview'] = {'previous_head': PRIOR, 'prior_finding_ids': []}
            artifact.write_text(json.dumps(value))
            result = subprocess.run(args + ['--expected-previous-head', PRIOR],
                                    capture_output=True, text=True)
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertTrue(json.loads(result.stdout)['previous_head_verified'])
            for bad in (['--skill-fingerprint', ''], ['--skill-fingerprint', str(folder / 'skill'),
                                                       str(artifact)]):
                with self.subTest(bad=bad):
                    result = subprocess.run([sys.executable, str(SCRIPT)] + bad,
                                            capture_output=True, text=True)
                    self.assertEqual(2, result.returncode)
            result = subprocess.run(args[:3], capture_output=True, text=True)
            self.assertEqual(2, result.returncode)
            self.assertIn('missing required arguments', result.stderr)


class PreviousHeadPresenceTests(unittest.TestCase):
    evaluate = ReviewRecordTests.evaluate

    def test_new_findings_record_yes_no_or_unknown(self):
        value = rereview_record('yes', 'no', 'unknown')
        result = self.evaluate(value, expected_previous_head=PRIOR)
        self.assertEqual('APPROVE', result['verdict'])
        self.assertEqual({'yes': ['F1'], 'no': ['F2'], 'unknown': ['F3']},
                         result['new_findings_present_at_previous_head'])
        self.assertTrue(result['previous_head_verified'])
        self.assertFalse(self.evaluate(value)['previous_head_verified'])

    def test_presence_is_observational_not_a_verdict_input(self):
        for state in ('yes', 'no', 'unknown'):
            with self.subTest(state=state):
                value = rereview_record()
                value['findings'].append(finding(id='F9', present_at_previous_head=state))
                value['claimed_verdict'] = 'REQUEST_CHANGES'
                self.assertEqual(['finding:F9'], self.evaluate(value)['blockers'])

    def test_missing_or_invalid_presence_is_rejected(self):
        for state in ('maybe', 'Yes', '', True, None, ['yes']):
            with self.subTest(state=state):
                with self.assertRaisesRegex(MODULE.InvalidRecord, 'yes/no/unknown'):
                    self.evaluate(rereview_record(state))
        value = rereview_record()
        value['findings'].append(finding(id='F1', origin='base', defect=False))
        with self.assertRaisesRegex(MODULE.InvalidRecord, 'yes/no/unknown'):
            self.evaluate(value)

    def test_presence_only_on_new_findings_of_a_rereview(self):
        value = rereview_record()
        value['findings'][0]['present_at_previous_head'] = 'yes'
        with self.assertRaisesRegex(MODULE.InvalidRecord, 'only to new re-review findings'):
            self.evaluate(value)
        value = record()
        value['findings'] = [finding(origin='base', defect=False, present_at_previous_head='no')]
        with self.assertRaisesRegex(MODULE.InvalidRecord, 'only to new re-review findings'):
            self.evaluate(value)

    def test_previous_head_identity_is_bound(self):
        with self.assertRaisesRegex(MODULE.InvalidRecord, 'differs from expected'):
            self.evaluate(rereview_record('no'), expected_previous_head='d' * 40)
        with self.assertRaisesRegex(MODULE.InvalidRecord, 'expected but not recorded'):
            self.evaluate(record(), expected_previous_head=PRIOR)
        with self.assertRaisesRegex(MODULE.InvalidRecord, 'expected previous head'):
            self.evaluate(rereview_record('no'), expected_previous_head=PRIOR[:12])
        value = rereview_record('no')
        value['rereview']['prior_finding_ids'].append('F7')
        with self.assertRaisesRegex(MODULE.InvalidRecord, 'prior finding missing'):
            self.evaluate(value)
        for rereview in ({'previous_head': PRIOR[:12], 'prior_finding_ids': []},
                         {'previous_head': PRIOR, 'prior_finding_ids': ['F0', 'F0']},
                         {'previous_head': PRIOR}, 'c' * 40):
            with self.subTest(rereview=rereview):
                value = record()
                value['rereview'] = rereview
                with self.assertRaises(MODULE.InvalidRecord):
                    self.evaluate(value)

    def test_delta_rereview_needs_previous_head_once_identity_is_recorded(self):
        value = record()
        value['coverage'].update(mode='delta', baseline_head=PRIOR, delta_files=['src/paging.py'])
        delta = {'baseline_head': PRIOR, 'delta_files': ['src/paging.py']}
        self.assertEqual('APPROVE', self.evaluate(value, **delta)['verdict'])
        value['skill'] = identity()
        with self.assertRaisesRegex(MODULE.InvalidRecord, 'must record the previously reviewed head'):
            self.evaluate(value, **delta)
        value['rereview'] = {'previous_head': 'd' * 40, 'prior_finding_ids': []}
        with self.assertRaisesRegex(MODULE.InvalidRecord, 'differs from delta baseline'):
            self.evaluate(value, **delta)
        value['rereview']['previous_head'] = PRIOR
        result = self.evaluate(value, **delta)
        self.assertEqual('APPROVE', result['verdict'])
        self.assertTrue(result['previous_head_verified'])


if __name__ == '__main__':
    unittest.main()
