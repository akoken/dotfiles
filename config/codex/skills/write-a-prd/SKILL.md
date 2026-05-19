---
name: write-a-prd
description: Create a PRD through user interview, codebase exploration, module design, success criteria, risk analysis, and testing strategy. Use when user wants to write a PRD, create a product requirements document, or plan a new feature.
---

This skill will be invoked when the user wants to create a PRD. You may skip steps if you don't consider them necessary.

1. Ask the user for a long, detailed description of the problem they want to solve and any potential ideas for solutions.

2. Explore the repo to verify their assertions and understand the current state of the codebase.

3. Interview the user about the parts of the plan that remain unclear after repo exploration. Resolve the core problem, target users, success metrics, constraints, non-goals, and major product/technical decisions. Do not invent missing constraints; ask or mark them as `TBD`.

4. Sketch out the major modules you will need to build or modify to complete the implementation. Actively look for opportunities to extract deep modules that can be tested in isolation.

A deep module (as opposed to a shallow module) is one which encapsulates a lot of functionality in a simple, testable interface which rarely changes.

Check with the user that these modules match their expectations. Check with the user which modules they want tests written for.

5. Once you have a complete understanding of the problem and solution, use the template below to write the PRD. Produce the PRD in the conversation or in a file if the user asks for one.

Use concrete, measurable language. Avoid vague requirements like "fast", "easy", or "intuitive" unless they are backed by measurable acceptance criteria.

<prd-template>

## Problem Statement

The problem that the user is facing, from the user's perspective.

## Solution

The solution to the problem, from the user's perspective.

## Success Criteria

3-5 measurable outcomes that define whether the feature worked. Include product, operational, quality, or evaluation metrics as appropriate.

## User Stories

A LONG, numbered list of user stories. Each user story should be in the format of:

1. As an <actor>, I want a <feature>, so that <benefit>

<user-story-example>
1. As a mobile bank customer, I want to see balance on my accounts, so that I can make better informed decisions about my spending
</user-story-example>

This list of user stories should be extremely extensive and cover all aspects of the feature.

## Acceptance Criteria

Concrete "done" criteria for the user stories. Prefer externally observable behavior over implementation details.

## Implementation Decisions

A list of implementation decisions that were made. This can include:

- The modules that will be built/modified
- The interfaces of those modules that will be modified
- Technical clarifications from the developer
- Architectural decisions
- Schema changes
- API contracts
- Specific interactions

Do NOT include specific file paths or code snippets. They may end up being outdated very quickly.

## Security, Privacy, and Data Handling

Any security, privacy, permission, compliance, retention, logging, or data-migration requirements. Mark as `N/A` only when the feature has no meaningful data or access-control implications.

## AI System Requirements

Include this section only when the feature uses AI. Capture model/tool requirements, grounding/citation needs, failure modes, evaluation strategy, and quality thresholds.

## Testing Decisions

A list of testing decisions that were made. Include:

- A description of what makes a good test (only test external behavior, not implementation details)
- Which modules will be tested
- Prior art for the tests (i.e. similar types of tests in the codebase)
- Any benchmark, fixture, integration, end-to-end, accessibility, or AI-evaluation coverage needed

## Out of Scope

A description of the things that are out of scope for this PRD.

## Risks and Mitigations

The main product, technical, migration, security, performance, cost, dependency, and rollout risks, each paired with a mitigation or open decision.

## Rollout Plan

The intended delivery phases, feature flags, migration order, release checks, monitoring, and fallback plan where relevant.

## Further Notes

Any further notes about the feature.

</prd-template>
