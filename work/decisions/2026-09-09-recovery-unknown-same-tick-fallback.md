# Decision: UNKNOWN harness resume does not permit same-tick direct fallback

Date: 2026-09-09
Status: `ACCEPTED — BOUNDED RECOVERY POLICY`
Owner: Harness / Recovery

## Decision

For a recovery incident with an exact task/run/session binding, once `HarnessService.resume(...)` returns a non-success `OperationResult` whose `retry` is `RetryDisposition.UNKNOWN`, recovery MUST NOT immediately issue the legacy direct `hcom.resume(...)` fallback in the same tick.

The bounded exception is a known pre-dispatch rollout/configuration result such as `CANONICAL_GUARD_REQUIRED`; that outcome has not reached the provider effect and retains its existing compatibility fallback. Existing canonical denials (`HOOK_DENIED`, `APPROVAL_REQUIRED`) keep their dedicated handling.

An UNKNOWN result is not terminal. The incident consumes the ordinary recovery attempt, remains `probing`, and follows the existing backoff. A later tick first re-observes current session state; if the session is live, the incident resolves without another resume.

## Why

Three existing MAPS facts now agree:

1. `RetryDisposition.UNKNOWN` is defined as repeat safety not being known.
2. Harness Mechanics already says ambiguous consequential operations should reconcile rather than blindly repeat.
3. PR #327 characterized a real recovery seam where an UNKNOWN harness result was immediately followed by a second side-effecting direct resume while the retry/operation evidence was dropped.

Treating UNKNOWN as permission for an immediate second attempt would silently strengthen uncertainty into `SAFE`. No evidence currently supports that conversion.

## Smallest implementation

- Preserve `operation_id`, `retry`, and `mutated` in `harness_resume` evidence for the ambiguous result.
- Suppress only the same-tick direct fallback for returned non-success UNKNOWN results that are not known pre-dispatch compatibility outcomes.
- Keep ordinary probing/backoff bookkeeping and fresh session observation on the next tick.
- Change the PR #327 characterization into an explicit policy regression and add a production Hcom transport-failure case.

## Deliberate non-goals / residual questions

This decision does **not** authorize:

- a general operation/idempotency ledger;
- pre-dispatch durable logical operation identity;
- provider idempotency-key plumbing;
- schema changes;
- changes to task authority or capability status;
- a new recovery state;
- permanent suppression of later retries;
- changes to `RetryDisposition.UNSAFE` handling;
- changes to the raw `HarnessService.resume()` exception path.

The broader external-effect correctness work still needs separate owner decisions on durable intent identity, provider propagation, receipts/reconciliation, and which external-effect classes can safely retry.

## Evidence / predecessor

- `work/notes/2026-09-09-external-effect-idempotency-audit.md`
- `tests/test_recovery_external_effect_ambiguity.py`
- `work/roadmaps/agent-harness-capabilities/01-harness-mechanics.md`
- reviewed characterization: PR #327

Human scope authorization: operator instruction on 2026-09-09 to proceed through the recommended reviewed-gap order, beginning with recovery ambiguity. This decision stays inside that bounded objective and does not expand to the general idempotency architecture.
