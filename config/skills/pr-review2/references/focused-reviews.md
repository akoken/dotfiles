# Focused Review Lenses

Select lenses from changed behavior and affected callers, not file extensions alone. Use
these questions within the normal pass; they do not require four extra agents or four
full-file passes. Read the applicable section only. Mark a lens not applicable with a
brief reason. A focused user request narrows scope only when explicitly agreed; a lens
selection does not silently waive the rest of a complete PR review or required gates.

Use a separate specialist only for a material unresolved question, demonstrated complexity,
or a project/user requirement, when delegation and the runner are permitted. Give it the
immutable input, relevant callers/defenses and an open question, not an asserted verdict.
Integrate its evidence through the normal verification and blocker pipeline. Missing
optional specialization alone is not an incomplete gate; an unresolved material question
or explicitly required pass is. Security routing retains its existing requirements.

## Errors, cancellation and fallbacks

Apply when error handling, retry, cancellation, default-on-failure behavior, or callers of
those paths change. Trace failure -> handler -> recovery/result -> user or upstream caller.

- Can an unsuccessful operation become a success response, empty collection, stale result,
  or fabricated data that violates the contract? Distinguish legitimate empty results from
  unavailable data and intentionally supported degraded behavior.
- Does a fallback preserve authorization, tenant and data-validity invariants? Is its
  provenance or degraded state observable where the contract requires it?
- Are cancellation, timeout and business rejection kept distinct from unexpected faults?
  Could a retry swallow cancellation or repeat a non-idempotent side effect? Trace cleanup
  and the caller's ability to stop, recover or report the failure.
- Locate the responsible handling boundary. An intentional outer catch, Result return,
  graceful fallback, or caller-level logging is valid counterevidence. Do not demand a
  catch/log at every layer, duplicate logging, or raw error/secret disclosure to users.

For a finding identify the reachable failure, required result, actual propagation/fallback,
causal change and impact. A broad catch, optional chaining or default value alone is not
proof. Keep hardening proposals separate from a verified regression.

## Type invariants

Apply when a type's construction, validation, serialization/deserialization, exposed state,
or mutation paths change. Start with the contract's valid states and transitions.

- Can constructors, factories, deserializers, clone/copy operations or setters create an
  invalid instance? Can later mutation bypass a previously checked invariant?
- Do mutable collections/references escape so callers can invalidate protected state?
  Check actual ownership and reachable mutation before proposing defensive copies.
- Are constraints enforced at a real trust boundary or guaranteed by the type/upstream
  caller? A transport DTO need not be a rich domain object. Do not invent business rules,
  wrapper types, validation layers, or blanket immutability requirements.

Report an actual invalid state/transition, its creation path and effect. Prefer existing
project types and compile-time guarantees where appropriate; keep optional API redesign
separate. No numerical design score substitutes for invariant evidence.

## Comments and documentation claims

Apply when comments/docs change OR implementation changes can invalidate existing claims
in the affected API/code. Inspect relevant unchanged comments too, not unrelated documents.

Check parameter/return/exception docs, examples, side effects and stated assumptions against
implementation and callers. Verify affected concurrency/thread-safety, complexity, caching,
security and retry claims with evidence. Unknown performance or concurrency proof is a gap,
not an invented contradiction. Distinguish obsolete factual claims from wording preferences;
do not demand comments that merely repeat code or remove useful rationale automatically.
A false comment and its underlying runtime defect share one finding when they have the
same root cause; retain independent documentation defects only when independently actionable.

## Test behavior and refactoring resilience

Apply when production behavior or tests exercising it change, including test-only changes
for unchanged production code. Map required behavior -> reachable scenario -> assertion and
check existing unit/integration/E2E coverage before proposing another test.

Look for tautologies, mocks replacing the behavior under test, assertions over mock setup,
and internal call/ordering assertions that fail a behavior-preserving refactor without
protecting a stated protocol. Interaction/order assertions are valid for contracts such as
transaction ordering, authorization-before-I/O, idempotency and external side effects.
Name the required property and concrete regression or harmless refactor affected; do not
turn preferred test style into a defect. Where a real test gap remains, identify the missing
input/assertion. Mutation testing supplements this reasoning; it does not authenticate the
requirement, prove refactoring resilience, or justify killing equivalent mutants.

## Provenance

The focused lenses were informed by the official
[PR review toolkit agents](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/pr-review-toolkit/agents).
They adapt the error, type, comment and test questions to this skill's verified findings,
project-specific contracts and review-only boundaries; plugin-specific defaults are not gates.
