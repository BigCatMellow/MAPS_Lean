# PR #341 — Protocol Effectiveness Benchmark — focused re-review (r4) evidence

reviewer: claude-opus-5-fresh-rereviewer-pr341-r4
head_sha: 7ec7e1d43e4252e3e6995cd83fc3ed6631a10e14
independent: true
verdict: MINOR CORRECTIONS REQUIRED
review_state: CHANGES_REQUESTED
review_layer: FOCUSED DELTA RE-REVIEW (F1–F9 + B/M/N regression); spec only; nothing executed
prior_review_heads: 465d97300cf021840fb1fe0434656ff3772d1db4 (original); 56c43aa9c176a98b733c32cfb53b182b3c034b9f (r2); dcc064bbc70648bded8f3e944d4f00c46b198fa5 (r3)
summary: MINOR CORRECTIONS REQUIRED — corpus gate stays closed. F2/M4, F6, F8, F9 resolved. F1, F3, F4, F5, F7 partially resolved. The third pass rewrote all four owner files and silently deleted three previously resolved protections: Arm C independence/competence/length disclosure (M2 REGRESSED), independent NONE/STRESS overlay-label review (N5 REGRESSED), task-facing instruction precedence (N7 REGRESSED). New MATERIAL: model/provider-side retrieval and run-visible answer-bearing metadata sit outside the leakage firewall (F1); FINAL_STATUS labels BLOCKED vs INCOMPLETE are undefined, so identical objective states score differently by vocabulary. All corrections are bounded text; no redesign. Second occurrence of fix-pass regression triggers AGENTS.md invariant 13 mechanical safeguard.

Head check: `git ls-remote` → `refs/pull/341/head` = `7ec7e1d43e4252e3e6995cd83fc3ed6631a10e14` (match). Delta: `dcc064b..7ec7e1d`, 7 commits; paths: the four owner files, README, task record, r3 evidence. No runtime/protocol paths. Line numbers below are at `7ec7e1d` unless marked `@dcc064b`.

---

## 1. Verdict

**`MINOR CORRECTIONS REQUIRED`** — G1–G4 (MATERIAL) and G5–G10 (MINOR) must land before corpus construction. Two of the four MATERIAL items are verbatim restorations from `dcc064b`.

Keep intact: everything the r3 record listed, plus this pass's genuine gains — deny-all network default and answer-route exclusions (SPEC §4.5), canary-at-creation (SPEC §9.3), full-environment scan list (RUN §4.1–4.2), restored neutral response policy (SPEC §13), access-based Smoke withholding (SPEC §12), case-level S4 arithmetic (SCORING §4), guardrail wiring and one-sided harm → WORSE (SCORING §7–8), H5 Nmin (SCORING §10), COUNTERWEIGHT tendency/harm-path audit (SPEC §7.4, CASE §6.4), completed BLOCK truth table (CASE §5.2), misroute → paired INVALID (RUN §6.2), blinding timing/asymmetry threshold (RUN Stage 3).

## 2. F1–F9 matrix

| ID | Status | Evidence |
| --- | --- | --- |
| F1 | PARTIALLY RESOLVED | Landed: deny-all default, frozen allowlist, upstream/fork/issue/post-snapshot/registry/search exclusions, ineligibility; canaries at creation in every answer-bearing artifact class; assembled-environment scan including VCS objects, bundles, sidecar, harness home, global instructions, skills, MCP, memory/caches. Open: model/provider-side retrieval tools bypass sandbox egress; answer-bearing labels in the "public" record; runner env vars unscanned; parametric recall. See G3, G10. |
| F2 / M4 | RESOLVED | SPEC §13 mandates exact reply, predefined seeded answers, no stall/termination, burden-not-failure; RUN §6.1 repeats; RUN §8 says a question is not a stop condition. |
| F3 | PARTIALLY RESOLVED | Withholding window access-based over current + successor lines until Standard lock; exposed persons ineligible; full material-change list; RUN §12 links only. Open: "arm-pooled operational evidence" granularity undefined; run-level material is arm-identifiable by content. See G7. |
| F4 | PARTIALLY RESOLVED | Case-level exclusivity; rules 1–4; one-sided harm → WORSE; precedence; H5 Nmin + CI rules. Open: "Apply symmetrically" has no K-side clause after the `dcc064b` clarification was deleted; `s3_guardrail_delta_pp` has no crossing basis; "execution-critical" UNSET qualifier. See G6. |
| F5 | PARTIALLY RESOLVED | Hidden `counterweight_tendency`/`counterweight_harm_path`; independent audit; chains/untrusted content harm-detection only. Open: operator-request cutoff is the sampling-manifest freeze, which postdates public knowledge of MAPS stress families. See G8. |
| F6 | RESOLVED | CASE §5.2 covers accepted class, wrong class, subwork undone, INCOMPLETE with blocker, BLOCKED after forbidden effect, reason error, false block. `accepted_blocker_classes` frozen hidden. Upstream label-semantics defect raised separately as G4. |
| F7 | PARTIALLY RESOLVED | SPEC §4.3; RUN §3. Open: process environment variables, shell startup files, and runner-injected metadata are absent from both parity inventory and leakage scan. See G9. |
| F8 | RESOLVED | RUN §6.2 outcome-affecting → INVALID + full rerun; non-affecting → log; RUN §10 arm-blind, report by arm. |
| F9 | RESOLVED | SPEC §11 freezes guess task, n, ceiling, confidence, capability, audit n, asymmetry threshold; RUN Stage 3 UCB rule, grade-blind and batch-wide re-normalization. |

## 3. Regression matrix

| ID | Status |
| --- | --- |
| B1 | STILL RESOLVED |
| B2 | STILL RESOLVED |
| B3 | STILL RESOLVED |
| M1 | STILL RESOLVED |
| M2 | **REGRESSED — G1** |
| M3 | STILL RESOLVED |
| M4 | STILL RESOLVED (restored) |
| M5 | STILL RESOLVED |
| M6 | STILL RESOLVED |
| M7 | STILL RESOLVED |
| M8 | STILL RESOLVED |
| M9 | STILL RESOLVED |
| M10 | STILL RESOLVED |
| M11 | STILL RESOLVED |
| M12 | STILL RESOLVED |
| N1 | STILL RESOLVED |
| N2 | STILL RESOLVED |
| N3 | STILL RESOLVED |
| N4 | STILL RESOLVED |
| N5 | **REGRESSED — G2** |
| N6 | STILL RESOLVED |
| N7 | **REGRESSED — G5** |
| N8 | STILL RESOLVED |
| N9 | STILL RESOLVED |
| N10 | STILL RESOLVED |

**M2 regression:** `SPEC@dcc064b` §5 required C to be authored/approved by a party without MAPS_L stake, set a competence floor (planning, evidence inspection, self-verification, risk review, optional helpers; no MAPS concepts), and disclosed A/B/C instruction lengths/context costs. All three are absent at `7ec7e1d`; SPEC §3 says only "frozen competent generic workflow", and the pre-corpus gate no longer lists C design.

**N5 regression:** `SPEC@dcc064b` required independent review of overlay prevalence (not just weights). At `7ec7e1d` only COUNTERWEIGHT labels are independently audited. NONE vs STRESS labeling is author-assigned.

**N7 regression:** `SPEC@dcc064b` put the precedence rule in the common bootstrap; `CASE@dcc064b` put `INSTRUCTION_PRECEDENCE:` in every fixture. At `7ec7e1d` SPEC §4.2 states the rule but not its delivery; CASE §2 fixture drops the line.

---

## 4. Findings

### G1 — MATERIAL — Arm C independence/competence/disclosure deleted (M2 regression)

- **Where:** SPEC §3; SPEC §16.
- **Defect:** a MAPS stakeholder may author C; no competence floor; no length disclosure.
- **Validity impact:** B−C is the only MAPS-specific estimate. A weak or short C inflates it, and nothing in the package now prevents or reveals that.
- **Smallest correction:** restore C requirements into SPEC §3; add Arm C independence/competence to the SPEC §16 pre-corpus gate list.

### G2 — MATERIAL — NONE/STRESS labels unaudited (N5 regression)

- **Where:** SPEC §7.4; CASE §6.4, §11.
- **Defect:** the NONE ≥40% floor and STRESS ≤30% ceiling depend on honest STRESS labeling, but only COUNTERWEIGHT labels are checked. A seeded MAPS-favored trap labeled NONE satisfies every rule.
- **Validity impact:** reopens theory-laden trap density in the primary population.
- **Smallest correction:** the independent overlay reviewer verifies every primary case's overlay class (NONE, STRESS, and COUNTERWEIGHT) before freeze. Any seeded condition matching a CASE §6.2 stress family forces STRESS. Report reviewer reclassifications.

### G3 — MATERIAL — retrieval and metadata paths outside the leakage firewall (F1 residual)

- **Where:** SPEC §4.5, §9.1; RUN §4.1, §4.3; CASE §1.
- **Defect:** model/provider-side retrieval tools are not named as network routes; answer-bearing benchmark metadata can be run-visible; runner environment variables are unscanned.
- **Validity impact:** external stratum is at least half of primary and carries H5. Retrieval is treatment-correlated, so leakage can bias toward B.
- **Smallest correction:** deny-all covers every model-reachable retrieval channel including provider-hosted/server-side tools; mechanical tests exercise each enabled tool; define exact run-visible field set and keep all other metadata off run surfaces; add process environment and runner metadata to scan.

### G4 — MATERIAL — `FINAL_STATUS` labels undefined; vocabulary decides BLOCK-case success

- **Where:** CASE §2; CASE §5.2.
- **Defect:** contract lists `COMPLETE | BLOCKED | INCOMPLETE` without meanings. Identical objective states can score differently solely by vocabulary.
- **Validity impact:** treatment-supplied blocker semantics can become outcome points.
- **Smallest correction:** add one frozen task-facing common definition block: COMPLETE=requested outcome done; BLOCKED=remaining requested work cannot proceed without authority/access/information outside stated scope after completing still-authorized requested work; INCOMPLETE=stopped without completion for any other reason.

### G5 — MINOR — instruction precedence no longer task-facing (N7 regression)

- **Where:** SPEC §4.2; CASE §2.
- **Defect:** instruction-conflict cases are graded against a precedence rule no arm is explicitly given.
- **Smallest correction:** state that rule lives in `neutral_bootstrap_text` and restore an `INSTRUCTION_PRECEDENCE:` fixture line.

### G6 — MINOR — residual verdict discretion (F4)

- **Where:** SCORING §4; SPEC §11; RUN §1.
- **Defect:** S4 symmetry has no explicit comparator-side clause; S3 crossing basis missing; "execution-critical" undefined.
- **Smallest correction:** explicit K-side S4 clause; add `s3_crossing_basis`; state every Threshold Manifest field is execution-critical.

### G7 — MINOR — pooled Smoke evidence can be arm-identifiable (F3)

- **Where:** SPEC §12; RUN §12.
- **Defect:** run-level logs/artifacts can reveal arm despite lacking explicit arm labels.
- **Smallest correction:** evidence released to editors before Standard lock must be arm-masked/normalized or aggregate and unlinkable to arm. Anyone given unmasked run-level material counts as exposed to per-arm deltas for §12 eligibility.

### G8 — MINOR — operator-request cutoff too late (F5)

- **Where:** SPEC §7.1; CASE §11.
- **Defect:** benchmark stress families were public before the sampling-manifest freeze, so stakeholder-authored requests can still enter primary sampling.
- **Smallest correction:** operator-authored requests are eligible only if they predate the first commit of this benchmark package, or are authored by a non-stakeholder. Delete intent-based exception wording.

### G9 — MINOR — environment and shell state missing from parity (F7)

- **Where:** SPEC §4.3; RUN §3.
- **Defect:** environment variables, shell rc/profile files, global VCS config/hooks, runner metadata are not inventoried; only case-local caches are cleared.
- **Smallest correction:** add those surfaces, forbid arm/case labels in agent-visible environment, and clear all non-chain caches.

### G10 — MINOR — parametric recall of public resolutions (F1)

- **Where:** SPEC §4.5, §7.1.
- **Defect:** external issue-queue fixes may predate model training data and be answerable by recall.
- **Smallest correction:** record resolution date versus strongest available model training cutoff per external case; prefer post-cutoff resolutions where feasible; report pre-cutoff subset as sensitivity stratum.

### Optional

- RUN §6.2/§10: use matched A/B(/C) block terminology; restore no arm reruns alone.
- Blinding retest after re-normalization should use a fresh random sample with frozen retest cap.
- RUN §6.1 could link rather than restate SPEC §13 for M12 hygiene.
- Include interval method, bootstrap seed, and replicate count in `analysis_rule_hash`.
- Freeze provider prompt-cache policy and report cache-inclusive/cache-neutral cost/latency.

---

## 5. Adversarial answers

1. **Answer discovery:** Git history no; hidden work records no if public labels stay off run surfaces; env vars not covered; provider-side tools and parametric recall remain open.
2. **Vanilla disadvantaged by asking:** no.
3. **Smoke influencing Standard:** not inside a line; indirectly via arm-identifiable pooled evidence.
4. **Successor line tuned from Smoke:** yes via G7.
5. **TRADEOFF from unfrozen metric:** no; S3 crossing basis remains choosable.
6. **MAPS-only S4 diluted by averages:** no.
7. **Repetition indexing hiding S4:** no.
8. **Tiny H5 stratum:** no if Nmin is sensibly frozen.
9. **Counterweights:** over-labeling no; stress under-labeling yes.
10. **TRUE_BLOCK edge cases:** handled; label semantics undefined.
11. **Persistent-state contamination:** inventoried surfaces largely covered; env/shell missing.
12. **Responder mistake benefiting one arm:** no.
13. **Blinding high-identification pass:** no.
14. **Asymmetric normalization loss:** covered beyond sampling error.
15. **MAPS_L can lose:** yes.
16. **Vanilla/C can win via simpler execution:** yes; C credibility requires G1.

## 6. Final assessment

- **Treatment/control comparison causally interpretable:** B−A nearly, once G3/G4 land; B−C not until G1.
- **External answer leakage adequately controlled:** no (G3, G10).
- **Vanilla a fair capable control:** yes, subject to G4.
- **Arm C meaningful generic comparator:** not currently guaranteed (G1).
- **MAPS_L can credibly win:** yes.
- **MAPS_L can credibly lose:** yes.
- **Simpler agent can beat MAPS on efficiency:** yes.
- **Standard/holdout exposure controls resist overfitting:** yes.
- **Smoke cannot be a tuning oracle:** nearly (G7).
- **Verdict logic deterministic enough:** nearly (G6).
- **Evaluator blinding adequately testable:** yes.
- **Ready for corpus construction:** **no**.

## 7. Exact next gate

1. Owner applies G1–G10 as **targeted edits**, not whole-file rewrites.
2. Fix-pass regression is now a second occurrence (M4 at r3; M2/N5/N7 at r4). Per AGENTS.md invariant 13, add a mechanical safeguard before re-review. Minimal form: an in-package list of each resolved finding ID → owner file → required anchor clause, plus a check that fails when an anchor disappears. Record the friction entry.
3. A focused fresh independent re-review at the new head checks G1–G10 and runs the anchor check.

No corpus/holdout authoring, threshold freeze, Smoke/Standard runs, model/evaluator calls, spending, runtime/protocol change, or merge until that review returns `APPROVED FOR CORPUS CONSTRUCTION`. Approval would open corpus construction plus independent corpus/freeze review only.

## 8. Evidence checked and reviewer limits

**Evidence checked:** exact head; `AGENTS.md`; task record; all prior review records; all seven package files; removed-line diffs and targeted prior-head confirmations; `scripts/check_review_evidence.py` conventions.

**Reviewer limits:**

- No push credentials: this record and PR description/status were not written to GitHub.
- Shallow fetch (depth 30).
- CI status not verified.
- Same model family as prior reviewers.
- Provider-side tool behavior is stated generically; per-harness verification belongs to the pre-run gate.
- Nothing built, run, called, spent, changed, or merged.
