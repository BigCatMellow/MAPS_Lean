# Claude/Codex evaluation and reliability mechanisms — 2026-08-27 through 2026-09-03

Status: `RESEARCH — NOT ACTIVE AUTHORITY`

Purpose: consolidate useful external mechanisms for measuring harness value, verifying intended changes, reconstructing real evaluations, and testing reliability under failure.

Related research:
- [Research routing index](../README.md)
- [Harness findings](../agent-harness/2026-08-27-to-2026-09-03-claude-codex-mechanisms.md)
- [Skills/tools findings](../skills-and-tools/2026-08-27-to-2026-09-03-claude-codex-mechanisms.md)
- [Security/authority findings](../security-and-authority/2026-08-27-to-2026-09-03-claude-codex-mechanisms.md)

## Executive findings

1. harness mechanisms should be evaluated by controlled ablation rather than intuition;
2. green tests are insufficient when the requested structural change can be bypassed;
3. real historical repository changes can become stronger evaluations than synthetic tasks;
4. verification should include adversarial or counterexample-seeking checks when risk warrants;
5. model, harness version, context policy, and environment form one experimental configuration;
6. instruction effectiveness and Skill value should be measured against behavior without them.

---

## 1. Harness ablation: hold the model constant

**Sources:**
- HarnessBench — https://github.com/nyosegawa/harness-bench
- harness-focused implementation — https://github.com/ya5h-P/harnessbench

**Mechanism:** keep model, task, repository state, and grader fixed; vary only the harness/control-plane mechanism.

**Problem solved:** model quality and harness quality are commonly confounded.

**Evidence:** public benchmark implementations include hidden execution-grounded grading, repeated runs, confidence intervals, paired tests, and distinct runaway outcomes.

**Failure modes:** task-set overfitting; rankings may not transfer across models or task classes.

**MAPS disposition:** `ADAPT METHODOLOGY`. The Proof Phase should compare baseline agent versus baseline plus selected MAPS mechanism where feasible.

---

## 2. Falsifiable harness engineering

**Sources:**
- Agentic Harness Engineering — https://arxiv.org/abs/2604.25850
- implementation — https://github.com/mqbazhaoyu/ahe

**Mechanism:** after an observed failure, identify one suspected harness component, state the predicted measurable effect before changing it, then keep/revert based on later evidence.

**Problem solved:** uncontrolled prompt/rule/tool tweaking creates hindsight bias and makes it impossible to know what helped.

**Evidence:** authors report Terminal-Bench 2 pass@1 improvement from 69.7% to 77.0% over ten iterations and cross-model gains from the frozen evolved harness; ablations attribute gains mainly to structural harness components rather than system-prompt edits.

**Failure modes:** autonomous harness self-modification creates governance risk and can optimize to noisy evaluations.

**MAPS disposition:** `ADAPT EXPERIMENT LOG`, not self-rewriting. Record observed failure, suspected mechanism, change, predicted effect, measurement, verdict.

---

## 3. Verify intent, not only behavioral output

**Source:** SWE Refactor Bench — https://arxiv.org/abs/2608.23564

**Mechanism:** before ordinary tests, audit whether the requested structural migration actually occurred; then run frozen tests and agentic counterexample hunting.

**Problem solved:** an agent can make tests pass while avoiding the requested architectural transformation.

**Evidence:** benchmark covers 20 repository migrations and 26 model/client configurations. Full acceptance was rare; adversarial verification still found hidden bugs after extensive fixed tests.

**Failure modes:** structural checks can overfit implementation details instead of validating intent.

**MAPS disposition:** `ADAPT PRINCIPLE`. Separate outcome correctness, intent correctness, and adversarial correctness when relevant.

---

## 4. Historical change -> executable evaluation

**Source:** Change2Task — https://arxiv.org/abs/2607.28591 and Microsoft Research publication page: https://www.microsoft.com/en-us/research/publication/change2task-from-repository-changes-to-executable-coding-agent-tasks-and-environments/

**Mechanism:** reconstruct a real merged repository change as a task on a healthy newer base, prove the broken/incomplete state, then prove the known repair restores correctness.

**Problem solved:** synthetic evaluations often miss real repository complexity, while old revisions rot and become hard to execute.

**Evidence:** authors report 1,130 eligible changes, 79.6% verified task construction, and high matched outcome agreement on reconstructed tasks.

**Failure modes:** reconstruction machinery is substantial; historical fixes may no longer map cleanly to modern code.

**MAPS disposition:** `TEST MANUALLY` with 3–5 old MAPS fixes before building any pipeline.

---

## 5. Realistic consequential-action tests without real consequence

**Source:** ClawBench — https://github.com/reacher-z/ClawBench

**Mechanism:** run the agent in a real environment but intercept the final irreversible network/action boundary, then grade the attempted request instead of performing the side effect.

**Problem solved:** realistic external-action evaluation otherwise risks placing orders, sending messages, creating accounts, etc.

**Evidence:** working benchmark pattern; evidence supports feasibility more than superiority.

**Failure modes:** interception can diverge from the real final system behavior; not every external action has a clean intercept seam.

**MAPS disposition:** `STUDY AS PROOF-PHASE SAFETY PATTERN` for future destructive/external-action tests.

---

## 6. Harness/version identity is part of reproducibility

**Source:** current Codex regression reports, including https://github.com/openai/codex/issues/41318

**Mechanism:** record model, reasoning effort, harness/client version, context-management behavior/settings, and environment identity as one run configuration.

**Problem solved:** harness regressions can be misattributed to model intelligence or task difficulty.

**Evidence:** detailed user report of a newer Codex configuration entering prolonged context/compaction loops while completed-run correctness remained otherwise normal. Root cause remains unconfirmed.

**Failure modes:** over-recording creates benchmark provenance bureaucracy.

**MAPS disposition:** `ADAPT MINIMAL METADATA`; use existing EnvironmentSpec/run identity where possible.

---

## 7. Instruction effectiveness requires a no-instruction control

**Source:** Harness-IF — https://arxiv.org/abs/2608.11727

**Mechanism:** rerun tasks without the operational rule to distinguish genuine instruction-following from behavior the agent would have produced anyway.

**Problem solved:** observing compliance does not prove the instruction caused it.

**Evidence:** across 12 frontier models, performance fell on rules designed to oppose default behavior; instruction location also affected compliance.

**Failure modes:** paired tests add evaluation cost and may be hard for subjective rules.

**MAPS disposition:** `TEST` 3–5 important rules that oppose likely default agent behavior.

---

## 8. Skill effectiveness requires a no-Skill control

**Source:** SWE-Skills-Bench — https://github.com/GeniusHTX/SWE-Skills-Bench and https://arxiv.org/abs/2603.15401

**Mechanism:** same task/model/harness with versus without the relevant Skill.

**Problem solved:** procedural packages can increase context and complexity without improving outcomes.

**Evidence:** most tested public Skills produced no pass-rate improvement; a small specialized subset helped substantially; some hurt performance.

**Failure modes:** applicability/routing errors can make a useful Skill appear weak.

**MAPS disposition:** `ADAPT AS PROMOTION EVIDENCE`.

---

## 9. Task class matters when interpreting agent success

**Source:** OpenAI/Asana Codex case study — https://openai.com/index/asana/

**Mechanism:** distinguish repetitive, mechanically checkable transformations from ambiguous architectural work when interpreting outcomes.

**Problem solved:** impressive results on highly decomposable migrations can be overgeneralized to weak-oracle engineering work.

**Evidence:** vendor/customer case study reports large productivity gains on Enzyme removal; not independent research.

**Failure modes:** elaborate task taxonomies become process overhead.

**MAPS disposition:** `ADAPT LIGHTLY`; use a few experimental labels such as ambiguity and verifiability.

---

## 10. Completion should be independently evidenced

**Source:** Gauntlet — https://github.com/dykim-ai/gauntlet

**Mechanism:** when the coding agent attempts to stop, apply deterministic checks and independent semantic review of actual diff/evidence before accepting completion.

**Problem solved:** the creator is a weak authority for deciding its own work is done.

**Evidence:** small/new community project with weak adoption evidence; mechanism aligns with independent-review principles.

**Failure modes:** automatic rule promotion/severity from frequency is not evidence of importance and should not be copied.

**MAPS disposition:** `STUDY COMPLETION BOUNDARY`; `IGNORE` frequency-based automatic authority promotion.

---

## Complexity warnings

Do not infer that MAPS needs:

- an autonomous benchmark factory;
- continuous self-modifying harness optimization;
- heavy adversarial review on every task;
- a large task taxonomy;
- complete trajectory retention without a concrete forensic/evaluation use.

## Highest-value next mechanism tests

1. **Harness ablation:** same model/task, baseline versus selected MAPS mechanism.
2. **Intent verification:** one task where ordinary tests could pass via the wrong implementation.
3. **Historical MAPS PR reconstruction:** manually turn 3 old fixes into fresh-agent evaluations.
