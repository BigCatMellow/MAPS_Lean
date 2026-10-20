# Dependencies: full-system causal requirements and promotion gates

- **Role:** candidate *cross-branch edges* for goal map [root](README.md); NOT an active runtime dependency table
- **Evidence:** [45/35 coverage crosswalk](COVERAGE.md) · [master roadmap](../00-MASTER-MAPS-CAPABILITY-ROADMAP.md) §§8–16 · [waves](WAVES.md)
- **Rule:** record "must be true before..." only where correctness, safety or evidence requires it. Keep optional enhancements `TRIGGERED`; avoid forcing all descendants into one critical path.

## Goal-level requirements (directed, not a mandatory step-by-step pipeline)

```text
                          HUMAN OBJECTIVE + PERMISSION
                                      │
                                      ▼
                                H01 INTENT / DONE
                                      │
                            ┌─────────┴────────────┐
                            ▼                      ▼
                    H02 PLAN / TASKS          H05 CONTEXT / SKILLS
                            │                      │
                            └─────────┬────────────┘
                                      ▼
                              H03 HARNESS / TOOLS
                                      │
                       H06 SAFETY ────┤
                         (across all) │
                                      ▼
                            H04 CONTINUITY / ENV
                                      │
                           H07 REVIEW / EVIDENCE
                                      │
                         ┌────────────┴────────────┐
                         ▼                         ▼
                   H08 REAL ADOPTION       H09 OUTCOME / EVAL
                         └────────────┬────────────┘
                                      ▼
                         VERIFIED / REVIEWED IMPROVEMENT
```

**This diagram shows support relationships, not a serial implementation mandate.** H06 safety and H07 evidence govern every relevant operation, including those before H04. H01/H02/H05 can be independently assessed before H08; H08 can begin with a selected narrow safe capability subset. H09 follows outcome data for comparisons, but its foundational tests/incident taxonomy already operate today.

## Exact critical edges and why

| Required consequence / node | Must be satisfied or deliberately constrained | Evidence of crossing the gate |
| --- | --- | --- |
| H02.3 worker dispatch | H01.2 accepted scope; H02.1 canonical owner/claim | Task readiness, lease/owner and inherited limits before operation |
| H03.2 consequential session lifecycle | H02.1 task/run binding; H06.2 capability-policy checks | Demonstrable denial on unauthorized start/send/resume/stop |
| H03.3 actual post-mutation validation | H03.1 stable operation boundary; H06 policies for effect class | Bad mutation caught near effect, retry/repair evidenced |
| H04.3 recover a real worker | H02.1 active lease; H04.1–H04.2 environment/worktree evidence; H06.3 policy | Stale/mismatched resume denied, error treated as UNKNOWN, no repeat effect |
| H05.2 activate imported Skill | H05.1 trust classes, H06.4 provenance/quarantine and current task capability | Unsafe/unreviewed Skill activation blocked on the actual path |
| H07.4 accept substantive review | H07.1 acceptance; H07.3 independence; H04.2 subject revision | Independent decision bound to exact artifact/current relevant base |
| H08.3 first external task | H01 approved target and actions; H02/H03/H05 usable subset; H06 actual guards; H07 review | Real repo/task through approved workflow with state isolation and outcome proof |
| H09.3 compare harness mechanisms | H09.2 real-run effective config hash + H09.1 identity + H07/H08 outcomes | Frozen fair comparator with quality, cost, defects, safety and independency evidence |
| H09.6 refine harness | H09.3 valid positive (or narrowed) evaluation, H06.5 promotion authority | Reviewed/versioned/rollback-capable decision, no self-modification |

## Explicit, non-required candidate edges

- **H05.5 semantic retrieval:** optional; only if frozen direct-vs-semantic test supports it, including hard negatives, ambiguous and vocabulary-shift cases.
- **H05.6 Capability Packs:** optional until repeated worker bundling need with stable prerequisites.
- **H04.6 snapshots:** optional until reconstruction fails measurably.
- **H06.6 credential broker:** mandatory *for a specific exposed secret boundary* if safer simpler controls cannot satisfy it, otherwise defer.
- **H08.5 non-GitHub CI, H08.6 fleet:** optional until target/ecosystem or multiple real projects justify them.
- **H09.7 time travel:** optional if debug reconstruction evidence is inadequate.
- **H01.6 mission object, H02.5 no-progress daemon, universal planning compiler:** not required by naming alone.

## Avoid a false dependency cycle

Successful outcomes feed learning; learning can suggest a new strategy/plan. This is a **feedback loop**, not a circular hard dependency: H08 does not wait for H09.6, and H09.6 does not automatically change H01 without acceptance. A new evaluated improvement is a separately versioned candidate with its own gate.

## Scope and portfolio constraints

The existing [Pilot Projects portfolio](https://github.com/BigCatMellow/Pilot_Projects/blob/main/PORTFOLIO.md) imposes cross-project attention limits and separately gates THINK/PLAN experimental mechanisms. This map documents the *full intended work*, not simultaneous authority to activate every branch. Existing MAPS_L task scopes and [coordination](../../coordination/README.md) govern live work.

**If a concrete external task requires a safety or portability property not named here**, add the missing edge after evidence-based challenge; don't quietly waive the condition, and don't impose unrelated speculative features as blockers.
