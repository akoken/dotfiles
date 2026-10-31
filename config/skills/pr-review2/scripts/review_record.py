#!/usr/bin/env python3
"""Validate review evidence accounting; never execute commands or authenticate evidence."""

import argparse
import json
import math
from pathlib import Path, PurePosixPath
import re
import sys

MAX_BYTES = 5 * 1024 * 1024
SHA = re.compile(r'(?:[0-9a-f]{40}|[0-9a-f]{64})\Z')
DIGEST = re.compile(r'[0-9a-f]{64}\Z')


class InvalidRecord(ValueError):
    """An evidence artifact cannot support a decision."""


def require(condition, message):
    if not condition:
        raise InvalidRecord(message)


def text(value):
    return isinstance(value, str) and bool(value.strip())


def references(value, label, required=True):
    require(isinstance(value, list) and all(text(item) for item in value), label)
    require(not required or bool(value), label)


def object_list(record, key):
    items = record[key]
    require(isinstance(items, list) and all(isinstance(item, dict) for item in items), key)
    identifiers = [item['id'] for item in items]
    require(all(text(item) for item in identifiers) and len(set(identifiers)) == len(items), key)
    return items


def paths(value, label):
    require(isinstance(value, list) and all(text(item) for item in value), label)
    require(len(value) == len(set(value)), label)
    for item in value:
        path = PurePosixPath(item)
        require(not path.is_absolute() and '..' not in path.parts and '\\' not in item
                and path.as_posix() == item and item != '.', label)
    return set(value)


def boolean(value, label):
    require(type(value) is bool, label)
    return value


def validate_timing(timing):
    """Validate observational timing without deriving a verdict from speed."""
    require(isinstance(timing, dict), 'timing object')
    fields = ('elapsed_seconds', 'active_review_seconds', 'verification_seconds', 'ci_wait_seconds')
    for field in fields:
        require(field in timing, 'missing timing field: ' + field)
        value = timing[field]
        require(value is None or (type(value) in (int, float) and value >= 0
                and (type(value) is int or math.isfinite(value))), 'timing seconds: ' + field)
    references(timing['evidence'], 'timing evidence')
    elapsed = timing['elapsed_seconds']
    for field in fields[1:]:
        value = timing[field]
        require(elapsed is None or value is None or value <= elapsed,
                'timing category exceeds elapsed: ' + field)


def evaluate(record, *, expected_profile, expected_base, expected_head, changed_files, required_checks=(),
             policy_known=False, expected_patch_digest=None, baseline_head=None,
             delta_files=None):
    """Return canonical verdict and reasons, or reject malformed/inconsistent evidence."""
    try:
        require(isinstance(record, dict) and type(record['schema_version']) is int
                and record['schema_version'] == 1, 'unsupported schema')
        if 'timing' in record:
            validate_timing(record['timing'])
        profile = record['profile']
        require(expected_profile in ('general', 'aura-peer', 'aura-self')
                and profile == expected_profile, 'profile differs from trusted review mode')
        require(isinstance(expected_base, str) and SHA.fullmatch(expected_base)
                and isinstance(expected_head, str) and SHA.fullmatch(expected_head), 'expected revisions')
        subject = record['subject']
        require(subject['base'] == expected_base and subject['head'] == expected_head,
                'stale base/head')
        require(expected_patch_digest is None or (isinstance(expected_patch_digest, str)
                and DIGEST.fullmatch(expected_patch_digest)), 'expected patch digest')
        require(subject['patch_digest'] == expected_patch_digest, 'stale dirty-input digest')
        blockers, gaps = set(), set()
        if not boolean(policy_known, 'policy_known'):
            gaps.add('required-check policy unresolved')
        contract = record['contract']
        require(contract['state'] in ('resolved', 'none', 'missing_reference', 'unavailable'), 'contract')
        references(contract['evidence'], 'contract evidence', contract['state'] != 'none')
        if profile == 'aura-peer' and contract['state'] in ('none', 'missing_reference'):
            blockers.add('missing-issue-reference')
        elif contract['state'] in ('unavailable', 'missing_reference') or (
                profile == 'aura-self' and contract['state'] != 'resolved'):
            gaps.add('contract unresolved')

        coverage = record['coverage']
        require(coverage['mode'] in ('full', 'delta'), 'coverage mode')
        files = coverage['files']
        require(isinstance(files, list) and all(isinstance(item, dict) for item in files), 'coverage files')
        current_paths = paths([item['path'] for item in files], 'coverage paths')
        if not current_paths:
            gaps.add('no changed files')
        require(current_paths == paths(changed_files, 'expected changed paths'), 'changed-file mismatch')
        for key in ('dimensions_complete', 'context_complete'):
            if not boolean(coverage[key], key):
                gaps.add(key)
        delta = paths(coverage['delta_files'], 'record delta paths')
        if coverage['mode'] == 'delta':
            require(isinstance(baseline_head, str) and SHA.fullmatch(baseline_head)
                    and coverage['baseline_head'] == baseline_head, 'delta baseline identity')
            require(delta_files is not None and delta == paths(delta_files, 'expected delta paths'),
                    'delta path mismatch')
            require(delta <= current_paths, 'delta includes reverted/removed paths; perform a full review')
        else:
            require(not delta and coverage['baseline_head'] is None
                    and baseline_head is None and not delta_files, 'unexpected full-pass baseline')
        for item in files:
            state = item['state']
            require(state in ('reviewed', 'baseline', 'unreviewed'), 'coverage state')
            references(item['evidence'], 'coverage evidence', state != 'unreviewed')
            require(state != 'baseline' or (coverage['mode'] == 'delta' and item['path'] not in delta),
                    'delta change hidden by baseline')
            if state == 'unreviewed':
                gaps.add('unreviewed file')

        required = paths(list(required_checks), 'required check identities')
        checks = object_list(record, 'checks')
        check_ids = {item['id'] for item in checks}
        gaps.update('missing required check: ' + item for item in required - check_ids)
        for check in checks:
            is_required = boolean(check['required'], 'check required')
            require(check['id'] not in required or is_required, 'required check downgraded')
            require(check['head'] == expected_head, 'stale check head')
            require(check['status'] in ('passed', 'failed', 'pending', 'unavailable', 'skipped'), 'check status')
            require(check['attribution'] in ('introduced', 'pre_existing', 'unknown', 'not_applicable'),
                    'check attribution')
            references(check['evidence'], 'check evidence')
            if is_required and check['status'] != 'passed':
                if check['status'] == 'failed' and check['attribution'] == 'introduced':
                    blockers.add('check:' + check['id'])
                else:
                    gaps.add('unresolved check: ' + check['id'])

        self_findings = set()
        reasons = {'introduced_defect', 'unmet_requirement', 'contradicted_claim', 'introduced_gate_failure'}
        if profile != 'general':
            reasons |= {'aspirational_doc', 'missing_issue'}
        for finding in object_list(record, 'findings'):
            require(finding['severity'] in ('Critical', 'Minor', 'Style'), 'finding severity')
            require(finding['route'] in ('finding', 'observation', 'carried'), 'finding route')
            require(finding['status'] in ('open', 'fixed-and-verified', 'rejected-with-evidence',
                                          'deferred-with-rationale'), 'finding state')
            require(boolean(finding['verified'], 'finding verified'), 'unverified finding')
            require(finding['origin'] in ('change', 'base', 'unknown'), 'finding origin')
            references(finding['evidence'], 'finding/state evidence')
            references(finding['anchors'], 'finding anchors', finding['route'] == 'finding')
            if 'class' in finding or 'instances' in finding:
                require(text(finding.get('class')), 'finding class')
                references(finding.get('instances'), 'finding class instances')
            declared = finding['blocking_reasons']
            require(isinstance(declared, list) and all(isinstance(item, str) for item in declared)
                    and len(set(declared)) == len(declared) and set(declared) <= reasons, 'blocking reasons')
            is_defect = boolean(finding['defect'], 'defect')
            is_reachable = boolean(finding['reachable'], 'reachable')
            introduced_defect = is_defect and is_reachable and finding['origin'] == 'change'
            require('introduced_defect' not in declared or introduced_defect,
                    'unsupported introduced-defect claim')
            active = finding['status'] in ('open', 'deferred-with-rationale')
            is_blocker = active and (introduced_defect or bool(declared))
            require(not is_blocker or finding['route'] == 'finding', 'blocker hidden in routed observation')
            if is_blocker:
                blockers.add('finding:' + finding['id'])
            if active and finding['route'] == 'finding' and finding['severity'] in ('Critical', 'Minor'):
                self_findings.add(finding['id'])

        author_recorded = set()
        for criterion in object_list(record, 'requirements'):
            require(text(criterion['text']), 'requirement text')
            require(criterion['state'] in ('met', 'unmet', 'partial', 'unverified'), 'requirement state')
            references(criterion['implementation'], 'requirement implementation', criterion['state'] == 'met')
            references(criterion['verification'], 'requirement verification', criterion['state'] == 'met')
            basis = criterion.get('verification_basis')
            require(basis is None or basis in ('reviewer', 'ci', 'static', 'author-recorded'),
                    'requirement verification basis')
            if basis == 'author-recorded':
                require(criterion['state'] == 'met', 'author-recorded basis requires a met criterion')
                author_recorded.add(criterion['id'])
            if criterion['state'] in ('unmet', 'partial'):
                blockers.add('requirement:' + criterion['id'])
            elif criterion['state'] == 'unverified':
                gaps.add('unverified requirement: ' + criterion['id'])
        for gap in object_list(record, 'verification_gaps'):
            references(gap['evidence'], 'gap evidence')
            if boolean(gap['material'], 'gap material'):
                gaps.add('material gap: ' + gap['id'])

        verdict = ('REQUEST_CHANGES' if blockers or (profile == 'aura-self' and self_findings)
                   else 'NEEDS_REVIEW' if gaps else 'APPROVE')
        require(record['claimed_verdict'] == verdict, 'claimed verdict inconsistent with evidence')
        result = {'valid': True, 'verdict': verdict, 'blockers': sorted(blockers),
                  'self_disqualifying': sorted(self_findings) if profile == 'aura-self' else [],
                  'incomplete_reasons': sorted(gaps), 'errors': [],
                  'author_recorded_requirements': sorted(author_recorded)}
        if 'timing' in record:
            result['timing'] = record['timing']
        return result
    except (KeyError, TypeError, AttributeError) as error:
        raise InvalidRecord('missing or malformed record field') from error


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'duplicate JSON key')
        result[key] = value
    return result


def reject_constant(_):
    raise InvalidRecord('non-finite JSON value')


def read_json(path):
    with Path(path).open('rb') as stream:
        data = stream.read(MAX_BYTES + 1)
    require(len(data) <= MAX_BYTES, 'JSON input exceeds size limit')
    return json.loads(data, object_pairs_hook=unique_object,
                      parse_constant=reject_constant)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('record')
    parser.add_argument('--expected-profile', choices=('general', 'aura-peer', 'aura-self'), required=True)
    parser.add_argument('--expected-base', required=True)
    parser.add_argument('--expected-head', required=True)
    parser.add_argument('--expected-patch-digest')
    parser.add_argument('--changed-files', required=True)
    parser.add_argument('--baseline-head')
    parser.add_argument('--delta-files')
    parser.add_argument('--require-check', action='append', default=[])
    parser.add_argument('--policy-known', action='store_true')
    args = parser.parse_args()
    try:
        result = evaluate(read_json(args.record), expected_profile=args.expected_profile,
                          expected_base=args.expected_base,
                          expected_head=args.expected_head, changed_files=read_json(args.changed_files),
                          required_checks=args.require_check, policy_known=args.policy_known,
                          expected_patch_digest=args.expected_patch_digest, baseline_head=args.baseline_head,
                          delta_files=read_json(args.delta_files) if args.delta_files else None)
        print(json.dumps(result, sort_keys=True))
        return 0 if result['verdict'] == 'APPROVE' else 1
    except (InvalidRecord, OSError, ValueError, RecursionError) as error:
        print(json.dumps({'valid': False, 'verdict': 'NEEDS_REVIEW',
                          'errors': [str(error) if isinstance(error, InvalidRecord) else 'unreadable JSON input']}))
        return 2


if __name__ == '__main__':
    sys.exit(main())
