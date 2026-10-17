"""Exercise externally observable review-record safety decisions and CLI behavior."""

import copy
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

    def test_minor_regression_blocks_even_without_declared_reason(self):
        value = record()
        value['findings'] = [finding()]
        value['claimed_verdict'] = 'REQUEST_CHANGES'
        self.assertIn('finding:F1', self.evaluate(value)['blockers'])
        value['findings'][0]['route'] = 'carried'
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


if __name__ == '__main__':
    unittest.main()
