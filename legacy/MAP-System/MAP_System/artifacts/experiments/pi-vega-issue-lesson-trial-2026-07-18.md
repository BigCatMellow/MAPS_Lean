# Pi Trial Assignment — Issue/Lesson Tracker: KICK-01 & PARITY Lessons

**status**: active  | **owner**: codex-lab-lilo  
**helper**: local-map-advisor-vega | **scope read-only advisory only (no edits/claims)**  

---

## Evidence-based findings from KICK-01/PARITY_NOT_ESTABLISHED artifacts:

| # | issue or lesson                  | evidence path                          | impact            | smallest next experiment       | type   |
|--|----------------------------------|---------------------------------------|-------------------|-------------------------------|--------|
| 1| frozen-frame assumptions/risks missing      | task233-review#C1 PARTIAL              → add explicit pre-input risks/assumptions    | KICK-02 evidence gap, partial acceptance criteria failure           | observe                              `frozen-frame-assumptions-risks-partial`     |
| 2| time-zone inconsistency            (header "EDT" vs hcom records)         : task233-review:C3 PARTIAL              → clock drift from review to submission       | measurement precision error in friction analysis           | investigate:   `timezone-correlation-check-verify-evidence-interval`     |
| 3| stale pending-final section        duplicated after scenario completion    (section #10 vs header status)               task233-review:C4 contradiction      → remove post-submission repetition; align with "completed/submitted" state           | report consistency degradation, misleading participant-turn counts       | investigate:   `pending-contradiction-clean-finished-state`     |
| 4| parity-audit deferred pending TASK-227    (command-center changes blocked without owner work)                → task233-release confirms PARITY_NOT_ESTABLISHED and defers any UI/deploy changes           | implementation blocker until rework complete                      | observe                              `deploy-parity-gated-by-task-owner-rework`     |
| 5| review independence confirmed        (Rori excluded from SUCCESS, Hana cancelled)      task233-review:C2 PASS                 → hcom events #4375/4410 distinct from Rori/Hana contributions    | validation model robustness; no cross-agent bias                       | observe                              `contribution-independence-validated`     |
| 6| dry-run installer evidence collected        (no install/restart)                    task234-parity-audit                     → command-center launches test before any code implementation           | read-only boundaries enforced correctly                                | observe                              `dry-run-launch-evidence-collected-no-state-change`      |

---

## Completed per advisory role: NO file/writing/edit/claim changes, only extraction.
All observations sourced from specified artifact list; findings suitable for future full-lifecycle test planning without automatic promotion or fixes proposed directly in this bounded scope output path.  

**next check**: await `@bigboss/initiate` request-initiation task assignment OR new lilo directive beyond advisory read-only boundaries.
