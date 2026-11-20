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
        value = delta_record()
        self.assertEqual('APPROVE', self.evaluate(value, **DELTA)['verdict'])
        value['coverage']['files'][0]['state'] = 'baseline'
        with self.assertRaisesRegex(MODULE.InvalidRecord, 'delta change hidden by baseline'):
            self.evaluate(value, **DELTA)

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
        self.assertEqual(MODULE.UNKNOWN_SKILL, result['skill'])
        self.assertEqual('unknown', result['skill_identity'])
        self.assertNotIn('new_findings_present_at_previous_head', result)
        legacy['skill'] = None
        self.assertEqual(MODULE.UNKNOWN_SKILL, self.evaluate(legacy)['skill'])

    def test_recorded_identity_is_reported_and_matches_expectations(self):
        value = record()
        value['skill'] = identity()
        result = self.evaluate(value, expected_skill_version='2.7.0',
                               expected_skill_fingerprint='e' * 64)
        self.assertEqual('APPROVE', result['verdict'])
        self.assertEqual(identity(), result['skill'])
        self.assertEqual('verified', result['skill_identity'])
        self.assertEqual(identity(), self.evaluate(value)['skill'])
        self.assertEqual('self_reported', self.evaluate(value)['skill_identity'])

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

    def test_delta_rereview_needs_previous_head(self):
        for value in (record(), dict(record(), skill=identity()), delta_record()):
            with self.subTest(schema=value['schema_version'], skill='skill' in value):
                value['coverage'].update(mode='delta', baseline_head=PRIOR, delta_files=['src/paging.py'])
                value.pop('rereview', None)
                with self.assertRaisesRegex(MODULE.InvalidRecord, 'must record the previously reviewed head'):
                    self.evaluate(value, **DELTA)
        value = delta_record()
        value['rereview']['previous_head'] = 'd' * 40
        with self.assertRaisesRegex(MODULE.InvalidRecord, 'differs from delta baseline'):
            self.evaluate(value, **DELTA)
        value['rereview']['previous_head'] = PRIOR
        result = self.evaluate(value, **DELTA)
        self.assertEqual('APPROVE', result['verdict'])
        self.assertTrue(result['previous_head_verified'])


def current(**overrides):
    """A schema 2 record: every incompleteness source carries a cause."""
    value = record()
    value.update(schema_version=2, skill=identity(), stopped=None, claimed_run_status='complete')
    value.update(overrides)
    return value


def scoped(value, authority='brief: review src/paging.py only'):
    """Exclude a second changed file under an approved, narrower scope."""
    value['coverage']['files'].append({'path': 'src/other.py', 'state': 'unreviewed',
                                       'evidence': [], 'gap': 'G-scope'})
    value['verification_gaps'].append({'id': 'G-scope', 'material': True,
                                       'evidence': ['src/other.py excluded by the approved scope'],
                                       'cause': 'scope_limit', 'authority': authority})
    value['claimed_verdict'], value['claimed_run_status'] = 'NEEDS_REVIEW', 'incomplete'
    return value



def reviewer(model_family='claude', host='claude-code'):
    return {'host': host, 'model_family': model_family}


DELTA = {'baseline_head': PRIOR, 'delta_files': ['src/paging.py']}


def delta_record(**rereview):
    """A schema 2 delta re-review whose baseline came from this run's reviewer identity."""
    value = current(reviewer=reviewer())
    value['coverage'].update(mode='delta', baseline_head=PRIOR, delta_files=['src/paging.py'])
    value['rereview'] = {'previous_head': PRIOR, 'prior_finding_ids': [],
                         'previous_skill': identity(), 'previous_reviewer': reviewer(),
                         'baseline_identity': 'same'}
    value['rereview'].update(rereview)
    return value


def as_full_pass(value):
    """The same re-review performed as a full pass: nothing is reused from the baseline."""
    value['coverage'].update(mode='full', baseline_head=None, delta_files=[])
    return value


TWO_FILES = ['src/paging.py', 'src/other.py']


class RunStatusTests(unittest.TestCase):
    evaluate = ReviewRecordTests.evaluate

    def test_complete_run_binds_revisions_and_skill_identity(self):
        result = self.evaluate(current())
        self.assertEqual('APPROVE', result['verdict'])
        self.assertEqual(2, result['schema_version'])
        self.assertEqual({'base': BASE, 'head': HEAD, 'patch_digest': None}, result['subject'])
        self.assertEqual(identity(), result['skill'])
        status = result['run_status']
        self.assertEqual(('complete', 'complete', 'complete'),
                         (status['state'], status['approved_scope_status'], status['claimed']))
        self.assertEqual(([], [], [], None),
                         (status['causes'], status['reasons'], status['authorities'], status['stopped']))

    def test_complete_run_can_request_changes(self):
        value = current(claimed_verdict='REQUEST_CHANGES', findings=[finding()])
        result = self.evaluate(value)
        self.assertEqual('REQUEST_CHANGES', result['verdict'])
        self.assertEqual('complete', result['run_status']['state'])

    def test_scope_limit_is_incomplete_but_distinct_from_an_abandoned_run(self):
        result = self.evaluate(scoped(current()), changed_files=TWO_FILES)
        status = result['run_status']
        self.assertEqual('NEEDS_REVIEW', result['verdict'])
        self.assertEqual(('incomplete', 'complete'), (status['state'], status['approved_scope_status']))
        self.assertEqual(['scope_limit'], status['causes'])
        self.assertEqual(['brief: review src/paging.py only'], status['authorities'])
        self.assertEqual({'file:src/other.py', 'gap:G-scope'}, {item['ref'] for item in status['reasons']})
        self.assertTrue(all(item['gap'] == 'G-scope' for item in status['reasons']))

        abandoned = scoped(current())
        abandoned['stopped'] = {'cause': 'tool_failure', 'evidence': ['session log: fetch timed out']}
        status = self.evaluate(abandoned, changed_files=TWO_FILES)['run_status']
        self.assertEqual(('incomplete', 'incomplete'), (status['state'], status['approved_scope_status']))
        self.assertEqual(['scope_limit', 'tool_failure'], status['causes'])
        self.assertEqual({'cause': 'tool_failure', 'evidence': ['session log: fetch timed out']},
                         status['stopped'])

    def test_scope_limited_required_check_keeps_approved_scope_complete(self):
        value = current(claimed_verdict='NEEDS_REVIEW', claimed_run_status='incomplete')
        value['checks'].append({'id': 'specialist:security', 'required': True, 'status': 'skipped',
                                'attribution': 'not_applicable', 'head': HEAD,
                                'evidence': ['specialist pass not run'], 'cause': 'scope_limit',
                                'authority': 'maintainer decision 2026-11-01'})
        status = self.evaluate(value, required_checks=['tests', 'specialist:security'])['run_status']
        self.assertEqual(('incomplete', 'complete'), (status['state'], status['approved_scope_status']))
        value['checks'][-1].update(cause='platform_refusal', evidence=['refusal text quoted in report'])
        del value['checks'][-1]['authority']
        status = self.evaluate(value, required_checks=['tests', 'specialist:security'])['run_status']
        self.assertEqual(['platform_refusal'], status['causes'])
        self.assertEqual('incomplete', status['approved_scope_status'])

    def test_claimed_status_must_match_the_computed_one(self):
        with self.assertRaisesRegex(MODULE.InvalidRecord, 'claimed run status inconsistent'):
            self.evaluate(scoped(current(), 'brief line 4') | {'claimed_run_status': 'complete'},
                          changed_files=TWO_FILES)
        with self.assertRaisesRegex(MODULE.InvalidRecord, 'claimed run status inconsistent'):
            self.evaluate(current(claimed_run_status='incomplete'))
        for claimed in (None, 'partial', True):
            with self.subTest(claimed=claimed):
                with self.assertRaisesRegex(MODULE.InvalidRecord, 'claimed run status'):
                    self.evaluate(current(claimed_run_status=claimed))
        value = current()
        del value['claimed_run_status']
        with self.assertRaisesRegex(MODULE.InvalidRecord, 'claimed run status'):
            self.evaluate(value)

    def test_every_open_source_needs_a_cause_and_evidence(self):
        cases = []
        value = current(claimed_verdict='NEEDS_REVIEW', claimed_run_status='incomplete')
        value['verification_gaps'] = [{'id': 'G1', 'material': True, 'evidence': ['probe not run']}]
        cases.append((value, {}, 'missing cause/authority: gap G1'))
        value = scoped(current())
        del value['coverage']['files'][-1]['gap']
        cases.append((value, {'changed_files': TWO_FILES}, 'missing gap: file:src/other.py'))
        value = current(claimed_verdict='NEEDS_REVIEW', claimed_run_status='incomplete')
        value['checks'][0]['status'] = 'pending'
        cases.append((value, {}, 'missing cause/authority: check tests'))
        value = current(claimed_verdict='NEEDS_REVIEW', claimed_run_status='incomplete')
        value['coverage']['dimensions_complete'] = False
        cases.append((value, {}, 'missing dimensions_gap'))
        value = current(claimed_verdict='NEEDS_REVIEW', claimed_run_status='incomplete')
        value['requirements'][0].update(state='unverified', implementation=[], verification=[])
        cases.append((value, {}, 'missing gap: requirement:R1'))
        value = current(claimed_verdict='NEEDS_REVIEW', claimed_run_status='incomplete')
        value['contract'] = {'state': 'unavailable', 'evidence': ['issue API unavailable']}
        cases.append((value, {}, 'missing gap: contract'))
        value = current()
        value['verification_gaps'] = [{'id': 'G2', 'material': False, 'evidence': ['raw logs elsewhere']}]
        cases.append((value, {}, 'missing cause/authority: gap G2'))
        for value, options, message in cases:
            with self.subTest(message=message):
                with self.assertRaisesRegex(MODULE.InvalidRecord, message):
                    self.evaluate(value, **options)

    def test_linked_sources_take_the_material_gap_cause(self):
        value = current(claimed_verdict='NEEDS_REVIEW', claimed_run_status='incomplete')
        value['verification_gaps'] = [{'id': 'G1', 'material': True, 'cause': 'environment',
                                       'evidence': ['no fixture database on this host']}]
        value['coverage'].update(dimensions_complete=False, dimensions_gap='G1',
                                 context_complete=False, context_gap='G1')
        value['contract'] = {'state': 'unavailable', 'evidence': ['issue API down'], 'gap': 'G1'}
        value['requirements'][0].update(state='unverified', implementation=[], verification=[], gap='G1')
        status = self.evaluate(value)['run_status']
        self.assertEqual(['environment'], status['causes'])
        self.assertEqual({'gap:G1', 'coverage:dimensions_complete', 'coverage:context_complete',
                          'contract', 'requirement:R1'}, {item['ref'] for item in status['reasons']})
        self.assertTrue(all(item['evidence'] == ['no fixture database on this host']
                            for item in status['reasons']))

    def test_malformed_causes_links_and_stops_are_rejected(self):
        def gap(**fields):
            value = current(claimed_verdict='NEEDS_REVIEW', claimed_run_status='incomplete')
            value['verification_gaps'] = [dict({'id': 'G1', 'material': True, 'evidence': ['e']}, **fields)]
            return value
        cases = [
            (gap(cause='scope_limit'), 'authority is required with scope_limit'),
            (gap(cause='scope_limit', authority=' '), 'authority: gap G1'),
            (gap(cause='quota', authority='brief line 3'), 'authority is required with scope_limit'),
            (gap(cause='Quota'), 'cause class'),
            (gap(cause=['quota']), 'cause class'),
            (gap(authority='brief line 3'), 'authority without cause'),
            (current(stopped={'cause': 'scope_limit', 'authority': 'brief', 'evidence': ['e']}),
             'not a stopped run'),
            (current(stopped={'cause': 'quota', 'evidence': []}), 'stopped evidence'),
            (current(stopped={'evidence': ['e']}), 'missing cause/authority: stopped'),
            (current(stopped='quota'), 'stopped'),
            (current(skill=None), 'needs skill identity'),
        ]
        value = current()
        del value['stopped']
        cases.append((value, 'missing stopped'))
        value = scoped(current())
        value['verification_gaps'][0]['material'] = False
        cases.append((value, 'must name a material verification gap'))
        value = scoped(current())
        value['coverage']['files'][-1]['gap'] = 'G-missing'
        cases.append((value, 'must name a material verification gap'))
        value = current()
        value['checks'][0]['cause'] = 'other'
        cases.append((value, 'field not applicable: check tests'))
        value = current()
        value['coverage']['files'][0]['gap'] = 'G1'
        cases.append((value, 'field not applicable: file:src/paging.py'))
        for value, message in cases:
            with self.subTest(message=message):
                with self.assertRaisesRegex(MODULE.InvalidRecord, message):
                    self.evaluate(value, changed_files=[item['path'] for item in value['coverage']['files']])

    def test_validator_side_reasons_carry_unknown_cause_with_evidence(self):
        value = current(claimed_verdict='NEEDS_REVIEW', claimed_run_status='incomplete')
        result = self.evaluate(value, policy_known=False, required_checks=['tests', 'security-diff'])
        status = result['run_status']
        self.assertEqual(('incomplete', 'incomplete'), (status['state'], status['approved_scope_status']))
        self.assertEqual(['unknown'], status['causes'])
        evidence = {item['ref']: item['evidence'] for item in status['reasons']}
        self.assertEqual({'policy': ['validator: --policy-known not supplied'],
                          'check:security-diff': ['validator: required check absent from record']},
                         evidence)

    def test_legacy_record_reads_unknown_and_refuses_half_migration(self):
        value = record()
        value['coverage']['files'].append({'path': 'src/other.py', 'state': 'unreviewed', 'evidence': []})
        value['claimed_verdict'] = 'NEEDS_REVIEW'
        result = self.evaluate(value, changed_files=TWO_FILES)
        status = result['run_status']
        self.assertEqual(1, result['schema_version'])
        self.assertEqual(('incomplete', 'unknown', 'unknown', 'unknown'),
                         (status['state'], status['approved_scope_status'], status['stopped'],
                          status['claimed']))
        self.assertEqual(['unknown'], status['causes'])
        self.assertEqual(MODULE.UNKNOWN_SKILL, result['skill'])
        self.assertEqual('complete', self.evaluate(record())['run_status']['approved_scope_status'])
        for field, item in (('claimed_run_status', 'incomplete'), ('stopped', None)):
            with self.subTest(field=field):
                with self.assertRaisesRegex(MODULE.InvalidRecord, 'schema 2 field in schema 1 record'):
                    self.evaluate(dict(value, **{field: item}), changed_files=TWO_FILES)
        value['coverage']['files'][-1]['gap'] = 'G1'
        value['verification_gaps'] = [{'id': 'G1', 'material': True, 'evidence': ['e'],
                                       'cause': 'quota'}]
        with self.assertRaisesRegex(MODULE.InvalidRecord, 'schema 2 field in schema 1 record'):
            self.evaluate(value, changed_files=TWO_FILES)
        for version in (0, 3, '2', True):
            with self.subTest(version=version):
                with self.assertRaisesRegex(MODULE.InvalidRecord, 'unsupported schema'):
                    self.evaluate(current(schema_version=version))

    def test_schema1_rejects_schema2_keys_by_presence_even_when_null(self):
        legacy = record()
        self.assertNotIn('claimed_run_status', legacy)
        self.assertTrue(self.evaluate(legacy)['valid'])
        for field in ('claimed_run_status', 'stopped'):
            with self.subTest(field=field):
                with self.assertRaisesRegex(MODULE.InvalidRecord, 'schema 2 field in schema 1 record'):
                    self.evaluate(dict(record(), **{field: None}))
        unreviewed = {'path': 'src/other.py', 'state': 'unreviewed', 'evidence': []}
        for holder, key in (('gap', 'cause'), ('gap', 'authority'), ('file', 'gap'),
                            ('coverage', 'dimensions_gap'), ('coverage', 'context_gap'),
                            ('check', 'cause')):
            with self.subTest(holder=holder, key=key):
                value = record()
                value['claimed_verdict'] = 'NEEDS_REVIEW'
                value['checks'][0]['status'] = 'pending'
                value['coverage'].update(dimensions_complete=False, context_complete=False)
                value['coverage']['files'].append(dict(unreviewed))
                value['verification_gaps'] = [{'id': 'G1', 'material': True, 'evidence': ['e']}]
                target = {'gap': value['verification_gaps'][0], 'file': value['coverage']['files'][-1],
                          'coverage': value['coverage'], 'check': value['checks'][0]}[holder]
                self.assertTrue(self.evaluate(value, changed_files=TWO_FILES)['valid'])
                target[key] = None
                with self.assertRaisesRegex(MODULE.InvalidRecord, 'schema 2 field in schema 1 record'):
                    self.evaluate(value, changed_files=TWO_FILES)

    def test_cli_rejects_explicit_null_claimed_run_status_in_schema1(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            artifact, changed = folder / 'review.json', folder / 'changed.json'
            changed.write_text(json.dumps(['src/paging.py']))
            args = [sys.executable, str(SCRIPT), str(artifact), '--expected-profile', 'general',
                    '--expected-base', BASE, '--expected-head', HEAD, '--changed-files', str(changed),
                    '--require-check', 'tests', '--policy-known']
            artifact.write_text(json.dumps(record()))
            result = subprocess.run(args, capture_output=True, text=True)
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            artifact.write_text(json.dumps(record() | {'claimed_run_status': None}))
            result = subprocess.run(args, capture_output=True, text=True)
            self.assertEqual(2, result.returncode, result.stdout + result.stderr)
            output = json.loads(result.stdout)
            self.assertFalse(output['valid'])
            self.assertEqual('incomplete', output['run_status']['state'])

    def test_cli_reports_run_status_and_identity_and_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            artifact, changed = folder / 'review.json', folder / 'changed.json'
            changed.write_text(json.dumps(TWO_FILES))
            artifact.write_text(json.dumps(scoped(current())))
            args = [sys.executable, str(SCRIPT), str(artifact), '--expected-profile', 'general',
                    '--expected-base', BASE, '--expected-head', HEAD, '--changed-files', str(changed),
                    '--require-check', 'tests', '--policy-known']
            result = subprocess.run(args, capture_output=True, text=True)
            self.assertEqual(1, result.returncode, result.stdout + result.stderr)
            output = json.loads(result.stdout)
            self.assertEqual(('incomplete', 'complete'), (output['run_status']['state'],
                                                          output['run_status']['approved_scope_status']))
            self.assertEqual(HEAD, output['subject']['head'])
            self.assertEqual('2.7.0', output['skill']['version'])
            claimed = scoped(current()) | {'claimed_run_status': 'complete'}
            artifact.write_text(json.dumps(claimed))
            result = subprocess.run(args, capture_output=True, text=True)
            self.assertEqual(2, result.returncode)
            output = json.loads(result.stdout)
            self.assertFalse(output['valid'])
            self.assertEqual(('incomplete', ['unknown']),
                             (output['run_status']['state'], output['run_status']['causes']))


class BaselineIdentityTests(unittest.TestCase):
    """The delta gate compares the previous review's reviewer identity with this run's."""
    evaluate = ReviewRecordTests.evaluate
    TRUSTED = {'expected_skill_version': '2.7.0', 'expected_skill_fingerprint': 'e' * 64,
               'expected_model_family': 'claude', 'expected_previous_skill_version': '2.7.0',
               'expected_previous_skill_fingerprint': 'e' * 64,
               'expected_previous_model_family': 'claude'}

    def test_same_identity_allows_a_plain_delta(self):
        result = self.evaluate(delta_record(), **DELTA)
        self.assertEqual('APPROVE', result['verdict'])
        self.assertEqual(reviewer(), result['reviewer'])
        self.assertEqual('self_reported', result['reviewer_identity'])
        self.assertEqual({'state': 'same', 'delta_allowed': True, 'disclosure_required': False,
                          'previous_skill': identity(), 'previous_reviewer': reviewer(),
                          'verified': False}, result['baseline_identity'])
        result = self.evaluate(delta_record(), **DELTA, **self.TRUSTED)
        self.assertTrue(result['baseline_identity']['verified'])
        self.assertEqual('verified', result['reviewer_identity'])

    def test_skill_difference_allows_a_delta_only_when_disclosed(self):
        earlier = identity(version='2.6.0', fingerprint='f' * 64)
        result = self.evaluate(delta_record(previous_skill=earlier, baseline_identity='skill_differs'),
                               **DELTA)
        self.assertEqual('APPROVE', result['verdict'])
        self.assertEqual(('skill_differs', True, True),
                         tuple(result['baseline_identity'][key]
                               for key in ('state', 'delta_allowed', 'disclosure_required')))
        self.assertEqual(earlier, result['baseline_identity']['previous_skill'])
        # A full pass reuses nothing from the baseline, so nothing needs disclosure.
        result = self.evaluate(as_full_pass(delta_record(previous_skill=earlier,
                                                         baseline_identity='skill_differs')))
        self.assertEqual(('skill_differs', True, False),
                         tuple(result['baseline_identity'][key]
                               for key in ('state', 'delta_allowed', 'disclosure_required')))
        for claimed, message in (('same', 'claimed baseline identity inconsistent'),
                                 (None, 'must state rereview.baseline_identity'),
                                 ('different', 'baseline identity state')):
            with self.subTest(claimed=claimed):
                value = delta_record(previous_skill=earlier, baseline_identity=claimed)
                with self.assertRaisesRegex(MODULE.InvalidRecord, message):
                    self.evaluate(value, **DELTA)
        # A same-version label cannot hide a changed package: the fingerprint decides.
        relabelled = identity(fingerprint='f' * 64)
        with self.assertRaisesRegex(MODULE.InvalidRecord, 'claimed baseline identity inconsistent'):
            self.evaluate(delta_record(previous_skill=relabelled), **DELTA)

    def test_model_family_difference_requires_a_full_pass(self):
        for claimed in ('model_family_differs', 'same', None):
            with self.subTest(claimed=claimed):
                value = delta_record(previous_reviewer=reviewer('gpt', 'codex'),
                                     baseline_identity=claimed)
                with self.assertRaisesRegex(MODULE.InvalidRecord,
                                            'different reviewer model family; perform a full review'):
                    self.evaluate(value, **DELTA)
        # Same family on another host is not a family change.
        result = self.evaluate(delta_record(previous_reviewer=reviewer(host='opencode')), **DELTA)
        self.assertEqual('same', result['baseline_identity']['state'])
        value = as_full_pass(delta_record(previous_reviewer=reviewer('gpt', 'codex'),
                                          baseline_identity='model_family_differs'))
        result = self.evaluate(value)
        self.assertEqual('APPROVE', result['verdict'])
        self.assertEqual(('model_family_differs', False, False),
                         tuple(result['baseline_identity'][key]
                               for key in ('state', 'delta_allowed', 'disclosure_required')))

    def test_placeholder_model_family_is_missing_identity_not_a_family(self):
        # A run whose model was not recorded may write a placeholder such as unknown. Two
        # placeholders are not the same family: the delta must fall back to a full pass.
        for placeholder in MODULE.PLACEHOLDER_FAMILIES:
            for sides in (('record', 'rereview'), ('record',), ('rereview',)):
                with self.subTest(placeholder=placeholder, sides=sides):
                    value = delta_record()
                    if 'record' in sides:
                        value['reviewer'] = reviewer(placeholder, MODULE.UNKNOWN)
                    if 'rereview' in sides:
                        value['rereview']['previous_reviewer'] = reviewer(placeholder, MODULE.UNKNOWN)
                    for claimed in ('same', 'model_family_unknown'):
                        value['rereview']['baseline_identity'] = claimed
                        with self.assertRaisesRegex(MODULE.InvalidRecord,
                                                    'model family is unknown; perform a full review'):
                            self.evaluate(value, **DELTA)
                    full = as_full_pass(value)
                    result = self.evaluate(full)
                    self.assertEqual('model_family_unknown', result['baseline_identity']['state'])
                    self.assertFalse(result['baseline_identity']['delta_allowed'])
        value = as_full_pass(delta_record(previous_reviewer=reviewer('unknown'),
                                          baseline_identity='model_family_unknown'))
        value['reviewer'] = reviewer('unknown')
        result = self.evaluate(value)
        self.assertEqual(MODULE.UNKNOWN_REVIEWER, result['reviewer'])
        self.assertEqual('unknown', result['reviewer_identity'])
        self.assertEqual(MODULE.UNKNOWN_REVIEWER, result['baseline_identity']['previous_reviewer'])
        # A placeholder can neither satisfy nor stand in for a trusted expectation.
        with self.assertRaisesRegex(MODULE.InvalidRecord, 'reviewer identity absent'):
            self.evaluate(value, expected_model_family='claude')
        with self.assertRaisesRegex(MODULE.InvalidRecord, 'previous reviewer identity absent'):
            self.evaluate(value, expected_previous_model_family='claude')
        for option in ('expected_model_family', 'expected_previous_model_family'):
            with self.subTest(option=option):
                with self.assertRaisesRegex(MODULE.InvalidRecord, option.replace('_', ' ')):
                    self.evaluate(delta_record(), **DELTA, **{option: 'unknown'})

    def test_missing_previous_identity_reads_unknown_never_same(self):
        for holder, key in (('rereview', 'previous_reviewer'), ('record', 'reviewer')):
            for absent in ('omitted', 'null'):
                with self.subTest(missing=key, absent=absent):
                    value = delta_record(baseline_identity='model_family_unknown')
                    target = value['rereview'] if holder == 'rereview' else value
                    if absent == 'omitted':
                        del target[key]
                    else:
                        target[key] = None
                    with self.assertRaisesRegex(MODULE.InvalidRecord,
                                                'model family is unknown; perform a full review'):
                        self.evaluate(value, **DELTA)
                    result = self.evaluate(as_full_pass(value))
                    self.assertEqual('model_family_unknown', result['baseline_identity']['state'])
                    self.assertFalse(result['baseline_identity']['delta_allowed'])
        for absent in ('omitted', 'null'):
            with self.subTest(missing='previous_skill', absent=absent):
                value = delta_record(baseline_identity='skill_unknown')
                if absent == 'omitted':
                    del value['rereview']['previous_skill']
                else:
                    value['rereview']['previous_skill'] = None
                result = self.evaluate(value, **DELTA)
                self.assertEqual(('skill_unknown', True, True),
                                 tuple(result['baseline_identity'][key]
                                       for key in ('state', 'delta_allowed', 'disclosure_required')))
                self.assertEqual(MODULE.UNKNOWN_SKILL, result['baseline_identity']['previous_skill'])
                value['rereview']['baseline_identity'] = 'same'
                with self.assertRaisesRegex(MODULE.InvalidRecord, 'claimed baseline identity inconsistent'):
                    self.evaluate(value, **DELTA)
        # A baseline record that predates the fields: a full-pass re-review still validates.
        value = rereview_record('no')
        value.update(schema_version=2, skill=identity(), stopped=None, claimed_run_status='complete')
        result = self.evaluate(value)
        self.assertEqual(MODULE.UNKNOWN_REVIEWER, result['reviewer'])
        self.assertEqual('unknown', result['reviewer_identity'])
        self.assertEqual({'state': 'model_family_unknown', 'delta_allowed': False,
                          'disclosure_required': False, 'previous_skill': MODULE.UNKNOWN_SKILL,
                          'previous_reviewer': MODULE.UNKNOWN_REVIEWER, 'verified': False},
                         result['baseline_identity'])
        self.assertNotIn('baseline_identity', self.evaluate(current()))

    def test_schema1_cannot_carry_identity_or_qualify_a_delta(self):
        legacy = rereview_record('no')
        self.assertEqual('model_family_unknown', self.evaluate(legacy)['baseline_identity']['state'])
        legacy['coverage'].update(mode='delta', baseline_head=PRIOR, delta_files=['src/paging.py'])
        with self.assertRaisesRegex(MODULE.InvalidRecord, 'model family is unknown'):
            self.evaluate(legacy, **DELTA)
        for key in ('previous_skill', 'previous_reviewer', 'baseline_identity'):
            with self.subTest(key=key):
                value = rereview_record('no')
                value['rereview'][key] = None
                with self.assertRaisesRegex(MODULE.InvalidRecord, 'schema 1 record: rereview.' + key):
                    self.evaluate(value)
        with self.assertRaisesRegex(MODULE.InvalidRecord, 'schema 1 record: reviewer'):
            self.evaluate(dict(record(), reviewer=None))

    def test_expected_identities_bind_the_record(self):
        cases = [
            ({'expected_model_family': 'gpt'}, 'reviewer model family differs from expected'),
            ({'expected_previous_model_family': 'gpt'},
             'previous reviewer model family differs from expected'),
            ({'expected_previous_skill_fingerprint': 'f' * 64},
             'previous skill fingerprint differs from expected'),
            ({'expected_previous_skill_version': '2.6.0'}, 'previous skill version differs from expected'),
            ({'expected_previous_model_family': 'Claude'}, 'expected previous model family'),
            ({'expected_model_family': ''}, 'expected model family'),
            ({'expected_previous_skill_fingerprint': 'abc'}, 'expected previous skill fingerprint'),
            ({'expected_previous_skill_version': 'latest'}, 'expected previous skill version'),
        ]
        for options, message in cases:
            with self.subTest(options=options):
                with self.assertRaisesRegex(MODULE.InvalidRecord, message):
                    self.evaluate(delta_record(), **DELTA, **options)
        for key, options in (('previous_reviewer', {'expected_previous_model_family': 'claude'}),
                             ('previous_skill', {'expected_previous_skill_fingerprint': 'e' * 64})):
            with self.subTest(absent=key):
                value = as_full_pass(delta_record(**{key: None}))
                value['rereview'].pop('baseline_identity')
                with self.assertRaisesRegex(MODULE.InvalidRecord, 'identity absent'):
                    self.evaluate(value, **options)
        with self.assertRaisesRegex(MODULE.InvalidRecord, 'reviewer identity absent'):
            self.evaluate(current(), expected_model_family='claude')
        for options in ({'expected_previous_model_family': 'claude'},
                        {'expected_previous_skill_version': '2.7.0'},
                        {'expected_previous_skill_fingerprint': 'e' * 64}):
            with self.subTest(without_rereview=options):
                with self.assertRaisesRegex(MODULE.InvalidRecord,
                                            'previous reviewer identity expected but not recorded'):
                    self.evaluate(current(reviewer=reviewer()), **options)

    def test_malformed_reviewer_identity_is_rejected(self):
        for bad, message in ((reviewer('Claude'), 'reviewer model family'),
                             (reviewer('claude opus'), 'reviewer model family'),
                             (reviewer(''), 'reviewer model family'),
                             (reviewer(host=' '), 'reviewer host'),
                             ({'host': 'claude-code'}, 'malformed record field'),
                             ('claude', 'reviewer host')):
            for holder in ('record', 'rereview'):
                with self.subTest(bad=bad, holder=holder):
                    value = as_full_pass(delta_record())
                    value['rereview'].pop('baseline_identity')
                    if holder == 'record':
                        value['reviewer'] = bad
                    else:
                        value['rereview']['previous_reviewer'] = bad
                    with self.assertRaisesRegex(MODULE.InvalidRecord, message):
                        self.evaluate(value)
        value = delta_record(previous_skill=identity(fingerprint='E' * 64))
        with self.assertRaisesRegex(MODULE.InvalidRecord, 'previous skill fingerprint'):
            self.evaluate(value, **DELTA)

    def test_cli_reports_baseline_identity_and_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            artifact, changed, delta = (folder / name for name in ('review.json', 'changed.json',
                                                                    'delta.json'))
            changed.write_text(json.dumps(['src/paging.py']))
            delta.write_text(json.dumps(['src/paging.py']))
            args = [sys.executable, str(SCRIPT), str(artifact), '--expected-profile', 'general',
                    '--expected-base', BASE, '--expected-head', HEAD, '--changed-files', str(changed),
                    '--require-check', 'tests', '--policy-known', '--baseline-head', PRIOR,
                    '--delta-files', str(delta), '--expected-previous-head', PRIOR]
            trusted = ['--expected-skill-version', '2.7.0', '--expected-skill-fingerprint', 'e' * 64,
                       '--expected-model-family', 'claude', '--expected-previous-skill-version', '2.6.0',
                       '--expected-previous-skill-fingerprint', 'f' * 64,
                       '--expected-previous-model-family', 'claude']
            earlier = identity(version='2.6.0', fingerprint='f' * 64)
            artifact.write_text(json.dumps(delta_record(previous_skill=earlier,
                                                        baseline_identity='skill_differs')))
            result = subprocess.run(args + trusted, capture_output=True, text=True)
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            output = json.loads(result.stdout)
            self.assertEqual(('skill_differs', True, True),
                             tuple(output['baseline_identity'][key]
                                   for key in ('state', 'disclosure_required', 'verified')))
            self.assertEqual(reviewer(), output['reviewer'])
            mismatch = trusted[:-1] + ['gpt']
            result = subprocess.run(args + mismatch, capture_output=True, text=True)
            self.assertEqual(2, result.returncode, result.stdout + result.stderr)
            artifact.write_text(json.dumps(delta_record(previous_reviewer=reviewer('gpt', 'codex'),
                                                        baseline_identity='model_family_differs')))
            result = subprocess.run(args, capture_output=True, text=True)
            self.assertEqual(2, result.returncode, result.stdout + result.stderr)
            output = json.loads(result.stdout)
            self.assertFalse(output['valid'])
            self.assertIn('perform a full review', output['errors'][0])
            self.assertEqual('incomplete', output['run_status']['state'])


class AnchorShapeTests(unittest.TestCase):
    """The validator checks anchor shape only; locating anchors belongs to verify_anchors.py."""

    def evaluate(self, *anchors, route='finding'):
        value = record()
        value['findings'] = [finding(anchors=list(anchors), route=route, origin='base', defect=False)]
        value['claimed_verdict'] = 'APPROVE'
        return MODULE.evaluate(value, expected_profile='general', expected_base=BASE,
                               expected_head=HEAD, changed_files=['src/paging.py'],
                               required_checks=['tests'], policy_known=True)

    def test_string_and_object_anchors_are_accepted_without_reading_targets(self):
        accepted = [
            ('changed:src/paging.py:2',),
            ({'path': 'src/paging.py'},),
            ({'path': 'src/paging.py', 'line': 2, 'quote': '    return page * size'},),
            ({'path': 'src/paging.py', 'line': 2, 'quote': 'return page * size', 'commit': PRIOR},),
            # Shape only: a path outside the changed set or absent on disk is still well formed.
            ({'path': 'docs/never-read.md', 'quote': 'not opened by the validator'},
             'issue:321'),
        ]
        for anchors in accepted:
            with self.subTest(anchors=anchors):
                self.assertEqual('APPROVE', self.evaluate(*anchors)['verdict'])
        self.assertEqual('APPROVE', self.evaluate(route='observation')['verdict'])

    def test_malformed_anchor_objects_are_rejected(self):
        rejected = [
            {},
            {'line': 2, 'quote': 'x = 1'},
            {'path': 'src/paging.py', 'qoute': 'typo keys are not silently ignored'},
            {'path': '/abs/src/paging.py'},
            {'path': '../src/paging.py'},
            {'path': 'src/paging.py', 'line': 2},
            {'path': 'src/paging.py', 'commit': PRIOR},
            {'path': 'src/paging.py', 'quote': 'x = 1', 'commit': 'not-a-sha'},
            {'path': 'src/paging.py', 'quote': 'x = 1', 'commit': PRIOR.upper()},
            {'path': 'src/paging.py', 'line': 0},
            {'path': 'src/paging.py', 'line': True},
            {'path': 'src/paging.py', 'line': '2'},
            {'path': 'src/paging.py', 'quote': '   '},
            {'path': 'src/paging.py', 'quote': 'two\nlines'},
            {'path': 'src/paging.py', 'quote': 'carriage\rreturn'},
            {'path': 'src/paging.py', 'quote': 7},
            '',
            7,
        ]
        for anchor in rejected:
            with self.subTest(anchor=anchor):
                with self.assertRaisesRegex(MODULE.InvalidRecord, 'finding anchors'):
                    self.evaluate(anchor)
        with self.assertRaisesRegex(MODULE.InvalidRecord, 'finding anchors'):
            self.evaluate()


if __name__ == '__main__':
    unittest.main()
