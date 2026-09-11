# PR #340 — handoff lifecycle infrastructure — independent review evidence

reviewer: SENTINEL-PR340-FRESH
head_sha: 6bc6ac9cfd577a303e8b24d20995f8afaa78ddfc
independent: true
summary: CHANGES REQUIRED. The durable-file lifecycle/register design is substantially sound, but the exact reviewed head violates the enforced root AGENTS.md size budget and the GitHub-thread-only lane does not explicitly require terminal CLOSED/SUPERSEDED lifecycle receipts.

## Review subject

- PR: `#340 — Track durable handoff acknowledgment and continuation`
- Reviewed implementation head: `6bc6ac9cfd577a303e8b24d20995f8afaa78ddfc`
- Base inspected for this feature-head review: `7dfcbd09a2df930ee3449ce047984e4da5cec460`
- Review layer: fresh independent feature/protocol review
- This file is a trailing review-evidence artifact only. The commit that adds this file is **not** the implementation head reviewed above.

## Scope and method

Read and followed root `AGENTS.md`, relevant `work/coordination/` instructions including the SENTINEL review contract and GitHub asynchronous-work rules, the exact PR diff, the new handoff register, handoff template, work navigation, `state/CURRENT.md`, the seeded legacy handoff, review-evidence enforcement, documentation-sprawl guard, and exact-head workflow results.

No substantive implementation was modified. Historical handoff reconciliation was not performed.

## Blocking findings

### B1 — root AGENTS.md exceeds the enforced size budget

Location: `AGENTS.md`; enforced by `tests/test_documentation_sprawl.py`.

At reviewed head `6bc6ac9cfd577a303e8b24d20995f8afaa78ddfc`, root `AGENTS.md` is 13,072 bytes while `MAX_AGENTS_MD_BYTES` is 13,000. The exact-head Runtime stack tests fail at `DocumentationSprawlGuardTests.test_always_read_entry_surfaces_have_explicit_size_budgets` with 1351 tests run, 1 failure, 5 skipped.

Concrete failure: the proposed canonical always-read instruction surface violates a repository-enforced invariant at the exact reviewed head.

Smallest sufficient correction: compact the root instruction surface by at least 72 bytes, preferably with margin, without weakening the handoff invariant; then rerun exact-head checks.

### B2 — thread-only handoffs lack an explicit terminal lifecycle requirement

Location: `work/handoffs/README.md`, section `GitHub-thread-only handoffs`, plus the related root invariant.

The durable-file protocol explicitly requires `CLOSED` with final evidence or `SUPERSEDED` with a replacement pointer. The thread-only rule explicitly says to leave review acknowledgment and durable continuation on the source issue/PR thread, but does not explicitly require the same terminal lifecycle transition there.

Concrete failure: A leaves a thread-only handoff; B records review and continuation, later completes or supersedes the work, but records no terminal handoff receipt. B can appear compliant with the stated thread-only rule. A later session sees a stale continuation receipt and must either keep treating the handoff as non-terminal or infer lifecycle closure from issue/PR merge/closure state. The latter would conflate work state with handoff lifecycle.

Smallest sufficient correction: require thread-only handoffs to record `CLOSED` with final evidence or `SUPERSEDED` with a replacement pointer on the same source thread, and state that issue/PR merge or closure alone does not establish lifecycle closure.

## Verified strengths / non-blocking observations

- `OPEN`, `ACKNOWLEDGED`, `CONTINUED`, `CLOSED`, `SUPERSEDED`, and legacy-only `UNTRIAGED` have distinct operational meanings for durable-file handoffs.
- Receipt is not continuation; continuation is not completion; `CONTINUED` requires a durable continuation pointer; terminal states require evidence/replacement pointers.
- Workstream state is explicitly separate from handoff lifecycle, avoiding overclaim from blocked/partial/ready state.
- `work/handoffs/README.md` is narrow: it does not mirror PR heads, CI, reviews, ownership, blockers, runtime status, or roadmap state.
- Register/handoff disagreement is explicitly a coordination defect requiring evidence-based repair before the handoff can be claimed handled.
- `work/README.md` provides a direct route to the register before broad directory search.
- Seeding the existing `state/CURRENT.md` pointer as `UNTRIAGED` preserves historical uncertainty and is conservative.
- `templates/handoff.md` captures the minimum forward-looking lifecycle receipt without copying volatile GitHub state. `Continued at` is somewhat overloaded for terminal/replacement evidence, but surrounding instructions make this non-blocking.
- Race safety is supplied by existing coordination ownership/claim rules rather than by the lifecycle register itself; under the repository's current coordination contract this is acceptable.

## Adversarial cases

| Case | Result |
|---|---|
| A creates; B acknowledges but does no work | Safe: remains `ACKNOWLEDGED`; receipt does not imply continuation. |
| B starts work; C resumes later | Safe for durable-file lane: `CONTINUED` requires a durable pointer C can follow. |
| Two sessions race to continue | Safe only in combination with existing ownership/claim rules; lifecycle disagreement is detectable and must be repaired. |
| Durable-file handoff is superseded | Safe: `SUPERSEDED` requires replacement pointer. |
| PR-thread-only handoff is continued, then terminates | **Blocking gap:** terminal thread receipt is not explicitly required. |
| Register conflicts with handoff | Safe: explicit coordination defect; check evidence and synchronize before claiming handled. |
| Handoff points to merged/closed PR but lacks lifecycle receipt | Must not infer lifecycle terminality from PR state; durable-file protocol remains conservative. |
| Historical handoff state unknowable | Safe: `UNTRIAGED`, no guessing. |
| Work finishes but lifecycle record remains open/continued | Protocol violation remains discoverable; durable-file rules require terminal update. |
| Agent sees GitHub merge and infers lifecycle closure | Not justified by the lifecycle/work-state separation; thread-only rules need the explicit terminal clarification in B2. |

## Validation

Exact reviewed head: `6bc6ac9cfd577a303e8b24d20995f8afaa78ddfc`.

- Runtime stack tests: **FAIL** at root `AGENTS.md` size guard (13,072 > 13,000).
- Review-evidence workflow at the implementation head: failed because the required PR #340 evidence artifact was not yet present. This trailing evidence-only commit is the allowed repository mechanism for satisfying that artifact requirement while keeping `head_sha` bound to the reviewed implementation state.

## Verdict

**CHANGES REQUIRED**.

Both blocking findings are narrow corrections. The underlying durable-file lifecycle/register model does not require redesign.