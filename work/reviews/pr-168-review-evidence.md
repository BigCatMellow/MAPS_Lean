reviewer: agent-a3a2201138b7c1d1b (independent reviewer, did not author this PR)
head_sha: 269a60ebd6de7cae5f886f5ddf43013a8088adef
independent: true
rebase_note: Rebound by the author from 0288ac257fdb524cc8ee71dd0091ed89e07e8d6c (the commit the reviewer actually read) after `git merge origin/main` was required to satisfy branch protection ("head branch is not up to date with the base branch"), picking up PR #167 (SEC4 design note) and PR #169 (tenth-seat protocol design note, `playbook/TENTH_SEAT_REVIEW.md`) — both docs-only. The reviewed content is provably unchanged: `git diff 0288ac2 269a60e --stat -- work/notes/2026-08-25-rns-validation-tier-hookin-design.md runtime/ tests/ scripts/` is empty, so the design note under review and every file the reviewer greped against are byte-identical at the rebound head. `check_review_evidence.py`'s walk-back never walks past a merge commit, so the rebind is required rather than optional.
summary: APPROVED — design-only note, no blocking defect. Every code claim in the note was re-derived independently at the reviewed head (three CAPABILITY_CHECKLIST quotes are byte-exact; the Option A rejection argument is real; all four claimed greps reproduce; the parse/to_dict round-trip matches key by key including nested allow-sets; the proposed §2.2 placement is structurally correct against a full read of tick()). The five hard non-goals are genuinely respected, the inertness disclosure is explicit and unmissable, and nothing is marked DONE. Six non-blocking findings recorded (N1-N6), of which N1 (the stated reason the #160 source guard survives is wrong in kind — that guard is a whole-file substring scan, not an import check) and N4 (no stated authority argument for executing DB-sourced shell commands unattended) are the two the implementation task should absorb before it starts.

# Review: PR #168 — RnS resume-path validation-tier hook-in design

- Reviewed artifact: `work/notes/2026-08-25-rns-validation-tier-hookin-design.md` (new, 433 lines)
- Reviewer: `agent-a3a2201138b7c1d1b` — did not author the note, did not author #160 or #165
- Verdict: `APPROVED` — no blocking finding; six non-blocking findings (N1-N6)

## 0. Method

Everything below was re-derived from the source at the reviewed head with
`grep`/`sed`/`Read`. No claim in the note was accepted because the note asserts it.
Where the note cites a line number, the line was opened and the cited construct
confirmed to be there.

## 1. Output boundary — PASS

```
$ git diff origin/main...HEAD --name-only
work/notes/2026-08-25-rns-validation-tier-hookin-design.md
$ git diff origin/main...HEAD --stat
 ...2026-08-25-rns-validation-tier-hookin-design.md | 433 +++++++++++++++++++++
 1 file changed, 433 insertions(+)
```

Exactly one new file. No `runtime/`, no `tests/`, no roadmap or checklist file. The
branch's later merge of `origin/main` brought in only two unrelated docs
(`work/notes/2026-08-25-sec4-skill-lifecycle-persistence-design.md`,
`work/reviews/pr-167-review-evidence.md`); the three-dot diff above is computed from
the merge base and is unaffected by it.

## 2. Grounding — the quoted exit-gate language is byte-exact — PASS

`sed -n '25p;48p;114p' work/roadmaps/CAPABILITY_CHECKLIST.md` was read and compared
against §1.1 word by word. All three block quotes (H4, E4, 6.5) reproduce the evidence
cell of their row verbatim, including the em dash in H4, the `--` double hyphens in E4
and 6.5, and the parenthetical file references. Nothing is paraphrased, softened, or
trimmed. The row labels (`H4 — Immediate validation hooks`,
`E4 — Validation tiers`, `6.5 | Immediate deterministic validation`) and the
`IN PROGRESS` statuses are also accurate.

## 3. Grounding — the Option A rejection argument is real, not invented — PASS

This is the load-bearing argument of the note, so each link in the chain was opened.

1. `runtime/environment/validation.py` — `make_validation_hook`'s inner `_callback`
   returns `HookOutcome(HookDirective.DENY, reason=..., annotations=...)` when
   `result.passed` is false. Confirmed by reading lines 166-199. The note's cite of
   `:196` lands inside that DENY construction. There is indeed no non-blocking
   registration mode: the only two returns are ALLOW and DENY.
2. `runtime/harness/service.py:294-298` is exactly
   `enforcement_error = self._require_canonical_enforcement(HookEvent.BEFORE_RESUME, "resume")`
   followed by the early return — and it sits *before* the `self.hooks.run(...)` call
   that begins at line 300. So the note's claim that the canonical guard gates
   `resume()` before hooks run is correct, and the `CANONICAL_GUARD_REQUIRED` code it
   would return is real (`service.py:72`).
3. `service.py:309-310` is `if not before.permitted: return self._hook_block("resume", before)`.
   Exact line match.
4. `service.py:121` is `code = "HOOK_DENIED" if result.denied else "APPROVAL_REQUIRED"`.
   Exact line match.
5. `runtime/recovery/supervisor.py:24` is
   `_CANONICAL_DENIAL_CODES = {"HOOK_DENIED", "APPROVAL_REQUIRED"}`. Exact line match.
6. `supervisor.py:404` sets `action = "resume_denied"` inside the
   `elif str(result.code) in _CANONICAL_DENIAL_CODES:` branch, which also sets
   `resolved = True` and is the one branch that does not fall through to the direct
   `hcom.resume()` fallback (confirmed by reading through to line 411).

So a DENY from *any* `BEFORE_RESUME` hook — including a validation hook — would be
indistinguishable, both in the recorded `code` and in `tick()`'s branch selection,
from a canonical-run denial. The note's central reason for rejecting Option A holds.

## 4. Grounding — the four claimed greps — PASS (all four reproduce)

```
$ grep -rn "run_validation_tier\|make_validation_hook" --include=*.py .
```
→ `runtime/environment/validation.py` (definitions, 126/166/184),
`runtime/environment/__init__.py` (re-exports, 28/29/51/53),
`tests/test_environment_validation.py`, and `tests/test_recovery_supervisor.py:907`
(the forbidden-literal list). **Zero production callers**, as claimed.

```
$ grep -rn "HarnessService(\|HcomHarnessAdapter(" --include=*.py .
```
→ 23 hits, every one under `tests/`. **No production construction**, as claimed. The
quoted `production.py` docstring line ("`harness_service` and `environment_reader` are
intentionally left `None`") is verbatim, and the constructor at `production.py:81-90`
does omit both.

```
$ grep -rn "EnvironmentSpec" runtime/recovery/
```
→ exit status 1, zero hits. As claimed.

```
$ grep -rn "record_run_environment_evidence" --include=*.py .
```
→ `runtime/state/environment.py:44` (the definition) and four call sites in
`tests/test_run_environment_evidence.py`. **Zero production writers**, as claimed —
which is what makes §3.3's inertness disclosure true rather than defensive.

## 5. Grounding — the #160 source guard, and whether Option B really keeps it passing

`tests/test_recovery_supervisor.py:901` is
`def test_no_validation_tier_commands_or_task_mutation_in_source(self):` and it does
forbid `environmentspec`, `make_validation_hook`, `claim_task(`, `submit_task(`,
`record_review(`, `promote_ready(`, `update_contract(`. The note's cite is accurate and
the test exists.

Does Option B keep it passing unmodified? **Yes, achievably** — but the note's stated
*reason* is wrong in kind. See finding N1. The conclusion survives; the reasoning
given to the implementer does not, and an implementer following §6 literally could
break the guard while obeying every word of it.

## 6. Grounding — the `EnvironmentSpec` round-trip, key by key — PASS

`runtime/environment/spec.py` has **no `from_dict`** (grep for `from_dict` in that file
returns nothing), `to_dict` at line 168, `parse_environment_spec` at 195,
`load_environment_spec` at 317. All four cites accurate.

`to_dict()` emits exactly twelve top-level keys: `environment_id`, `version`,
`repository`, `runtimes`, `required_tools`, `setup`, `maintenance`, `validation`,
`network`, `services`, `secrets`, `artifacts`. `parse_environment_spec`'s
`_reject_unknown` allow-set at 196-211 is exactly those same twelve, no more and no
fewer. The nested allow-sets match the nested emitted keys too:
`repository` → `{base_revision, require_clean_worktree}` (spec.py:223);
`setup` → `{commands}` (248); `maintenance` → `{commands}` (252);
`validation` → `{quick, normal, full}` (258);
`network` → `{mode, allowed_domains}` (271);
`secrets` → `{required_names}` (289); `artifacts` → `{dependency_inputs}` (295).
Every one corresponds to what `to_dict` puts in that sub-dict. The round-trip claim is
correct and the instruction not to add a `from_dict` is right.

The note's further instruction — assert the parsed `spec.sha256` equals the row's
stored hash — is well-founded: `record_run_environment_evidence` writes `spec.sha256`
into a real `environment_spec_hash` column (`runtime/state/environment.py`, the INSERT
at 119-142), and `EnvironmentSpec.__post_init__` recomputes `sha256` from the canonical
JSON of `to_dict()`, so the comparison is meaningful rather than tautological.

## 7. Grounding — the evidence reader and the `repo_root` gap — PASS

- `runtime/state/environment.py`: `record_run_environment_evidence` at 44,
  `spec_snapshot = self._canonical_json(spec.to_dict())` at 89, the
  `run_manifests` existence check at 107-117, the INSERT at 119-142,
  `list_run_environment_evidence` at 172 with `ORDER BY id`, and
  `_decode_environment_row` at 33-42 `json.loads`-decoding `spec_snapshot`. Every cite
  in §3.1 is accurate.
- `RecoverySupervisor.environment_reader` is documented at `supervisor.py:62-65` as
  "must expose `list_run_environment_evidence(run_id) -> list[dict]`". Accurate — so
  the note is right that no new reader interface is needed.
- `run_validation_tier(..., repo_root=...)` does `Path(repo_root).resolve()` and raises
  `ValidationTierError("repo_root must be a directory")` if not a directory
  (validation.py:144-146). Accurate.
- `production.py`'s `run_recovery_tick` signature takes `hcom_dir`, `hcom_executable`,
  `hcom_timeout_seconds`, `recovery_state_path` — and **no repo root**. Accurate.
- `recovery-tick` is defined at `runtime/cli.py:155-177` and exposes `--binding`,
  `--hcom-dir`, `--hcom-executable`, `--hcom-timeout-seconds` — **no `--repo-root`**.
  Accurate. `context --repo-root` is at cli.py:145 and `flow start --repo-root` at
  cli.py:239, **both `default='.'`**. Accurate. See N6.
- `_default_executor`'s `timeout=600` per command is at validation.py:59, and
  `CLAIM_PIGGYBACK_HCOM_TIMEOUT_SECONDS = 3.0` at production.py:51 with the bounding
  rationale in the comment above it. Both accurate, so Q2's cost framing is real.

## 8. Placement — I read `tick()` in full — PASS

`tick()` spans `supervisor.py:267-451`. Walking the per-incident loop:

- non-`scheduled`/`probing` → `continue`
- advisory `evidence` read at 285; `harness_resume` initialised `None` at 290
- terminal session → `suppress`, `continue` (action dict at ~296-303)
- task missing / not ACTIVE / claim changed → `suppress`, `continue` (~320-327)
- session live → `resolve`, `continue` (~335-342)
- `due_at` computed 346-348; `if now < due_at: continue` at 349
- `attempt = int(...)` 352; `if attempt >= len(self.backoff_seconds)` 353 → `fail`,
  `continue` (action dict ending 364-366)
- `resolved = False` at 368; harness attempt 369-414; direct fallback 416-423;
  bookkeeping 425-437; final action dict appended 439-448

The note's proposed insertion point — after the retry-budget block and before line 368
— is therefore exactly right: it is the first point at which the incident is
committed to a resume attempt, and every earlier outcome has already `continue`d out,
so §2.2's guarantee ("no validation command runs for an incident that is not about to
be resumed") is structurally enforced by the control flow rather than by convention.
The cited `harness_resume` shapes at 290, 377-389 and 414 are all where the note says
they are (414 is the `{"attempted": False, "reason": binding_reason}` form), so
mirroring that shape for `resume_validation` is a real, existing precedent and not an
invented one.

I also confirmed §2.3's rejection of a post-tick wrapper: `run_recovery_tick` receives
`actions = supervisor.tick()` only after the whole loop has returned
(`production.py:91-97`), so a wrapper genuinely cannot observe anything pre-resume.

## 9. Non-goals — genuinely respected, not merely listed — PASS

Each of the five hard constraints was tested against the *recommended* design rather
than against the list:

- **No report cache.** Non-goal 1 is explicit, and Q3 goes further than the list does:
  it accepts that N incidents sharing a spec will run the tier N times rather than
  reach for reuse, and states outright that "reuse the result within a single tick is
  a cache and is out of scope". The per-tick cap it proposes instead is a *counter that
  skips and records a reason* — it stores no `ValidationTierResult` and nothing is read
  back — so it is not a cache in disguise. Clean.
- **No default `EnvironmentSpec`.** §3.2 explicitly rejects `load_environment_spec` and
  names the conventional-path / repo-root / config-default variants as the forbidden
  thing. §3.1 admits exactly one source, bound to the incident's own `run_id`. Non-goal
  2 restates it including the subtle variants ("the last spec we saw", synthesising
  from a fingerprint). Clean.
- **`repo_root` is not an ambient default.** §3.4 requires an explicit caller-supplied
  value with "no implicit cwd default", and makes absence a first-class reported
  skip (`no_repo_root`) rather than a fallback. Non-goal 3 forbids inferring it from
  cwd, `git rev-parse`, or the recovery-state path. This is the place an ambient
  default would most naturally sneak in, and the note closes it deliberately. Clean,
  with the caveat in N6.
- **No always-on daemon.** Nothing in the design creates a process, thread, timer, or
  schedule. The only new execution is `run_validation_tier`'s own bounded
  `subprocess.run`, inside a pass whose cadence still comes entirely from an external
  event (a `maps claim`, or a human/CI invoking `recovery-tick`). Non-goal 5 cites
  master roadmap §7.1 ("Large persistent `mapd` supervisor daemon", roadmap line 1441,
  "Rejected by default") and §7.9 ("Continuous discovery/process-police agents", line
  1473, "Rejected by default. Prefer bounded audits and deterministic checks") — both
  quoted accurately, and neither is violated.
- **No mandatory gate.** This is the constraint the design is *built around*: Option A
  is rejected precisely because it would be a gate by construction, §2.2's last bullet
  states no decision branch reads the result, Q1 makes "proceed, and flag" a decision
  that must be tested, and non-goal 6 enumerates the specific ways a gate could leak in
  (denying the resume, marking suppressed/failed, consuming retry budget differently,
  implying incompatibility). Q9 additionally keeps it out of the
  `EnvironmentCompatibilityReport` story. Clean.
- **No external project pilot.** Non-goal 4; nothing in §2/§3/§6 reaches outside the
  repo. Clean.

## 10. Rigor bar — PASS

Compared section for section against the two established notes in the same lineage,
`work/notes/2026-08-21-rns-harness-validation-callsite-design.md` (#154) and
`work/notes/2026-08-24-rns-production-trigger-loop-design.md` (#162), whose shared
skeleton is Finding / Decision / Non-goals / Behavior questions / Bounded follow-up /
Roadmap impact:

| Bar element | #154 | #162 | #168 |
| --- | --- | --- | --- |
| Evidence-backed Finding | yes | yes | yes — §1, grep-derived, with a stated head |
| Explicit decision | yes | yes | yes — §2.2 |
| Rejected alternatives | one | one | **three** (§2.1 Option A, §2.3 post-tick wrapper, §3.2 file loader) |
| Explicit non-goals | 5 bullets | yes | **12 numbered**, each traceable to a section |
| Open questions | 4 | yes | **9**, each with a recommendation and a required test |
| Bounded follow-up | yes | yes | yes — §6, per-file allowed scope plus a test list |
| Honest roadmap impact | yes | yes | yes — §7, see §11 below |

#168 meets the bar and is the most thorough of the three on rejected alternatives and
on non-goals. Its §5 is materially better than the predecessor's equivalent section:
each question carries a recommendation *and* an explicit instruction that the task
must decide and test it, which is the "answer, not guess" property the bar asks for.

It also correctly discharges its inherited obligations: every bullet of #154's
"Validation-tier fast-follow" section is addressed (quick tier → §2.5; resume-adjacent
placement → §2.1/§2.2; spec from explicit task/run evidence → §3; compatibility
semantics preserved → Q9), and each of #154's five fast-follow non-goals reappears in
§4 in a refined, more specific form.

## 11. Honesty and the inertness claim — PASS, and this is the note's strongest section

The claim is that the implementation will be inert in production. It is **true**: with
zero production writers of `record_run_environment_evidence` (verified in §4 above),
`list_run_environment_evidence(run_id)` returns `[]` for every real run, so no spec can
be sourced and no command can execute. §3.3 states this in bold as "every incident
reports `{"attempted": False, "reason": "no_spec_bound"}` and no validation command
runs anywhere", explains why that is correct rather than a defect, and explicitly
forbids the implementer from "fixing" it with a fallback — which is the exact failure
mode that would otherwise reintroduce a default spec.

Nothing is marked DONE. Non-goal 12 forbids marking 6.5/H4/E4 `DONE` or editing any
roadmap status field, and §7 states the note "completes nothing", that even the
implementation "does not by itself close 6.5/H4/E4", and that the rows should change
only when a real run carries bound evidence and a tier result is observed — which it
names as a distinct later piece of evidence, not this task's acceptance criterion. The
status line at the top ("design complete; no runtime code changed by this note") is
accurate. No reader could come away believing the row is closed.

## 12. Test suite

Run as a blocking foreground call from the worktree root:

```
$ python3 -m unittest discover -s tests
----------------------------------------------------------------------
Ran 806 tests in 1413.928s

OK (skipped=6)
```

Exit code 0. **806 tests, 0 failures, 0 errors, 6 skipped.**

The guard test was additionally run on its own —
`python3 -m unittest tests.test_recovery_supervisor -k no_validation_tier -v` →
`Ran 1 test in 5.445s / OK` — since §2.4's central promise is that this specific test
keeps passing unmodified.

The suite result is unchanged by this PR by construction (the PR adds one Markdown file
and touches no Python), so this is a baseline confirmation rather than a check of the
change.

CI at the reviewed head: `gh run list --branch rns-validation-tier-design` shows
`Runtime stack tests  success` (run 32901614655) and `review-evidence  failure`
(run 32901614646) — the latter is this very file being absent, and is expected to clear
once this commit lands.

## 13. Findings

No blocking findings. The note is design-only, its claims verify, and its constraints
hold.

### N1 — non-blocking, but the implementation task should absorb it first: §2.4 gives the wrong *reason* the #160 guard survives

§2.4 says supervisor.py "never imports `EnvironmentSpec` or `make_validation_hook`, so
the test keeps passing", and §6 phrases the constraint as "No
`EnvironmentSpec`/validation imports". But the guard is not an import check. It is:

```python
text = source.read_text(encoding="utf-8").lower()
for forbidden in ("environmentspec", "make_validation_hook", ...):
    self.assertNotIn(forbidden, text)
```

— a lowercased substring scan of the entire file, comments and docstrings included. The
hazard is concrete rather than theoretical: §2.2 asks for a new `resume_validator`
constructor input documented the way `environment_reader` and `harness_service` already
are, and those two are documented at `supervisor.py:62-76` with multi-line comments that
name their interfaces. An implementer writing the natural analogue — "when set, runs the
`EnvironmentSpec`-declared quick validation tier" — obeys §6 to the letter (no import)
and still turns the guard red. The note should say the literal must not appear anywhere
in `supervisor.py`'s source text, and that the new input must be documented in
interface-only terms (e.g. "must expose `validate_for_run(run_id) -> dict | None`")
without naming the spec type.

### N2 — non-blocking: §2.2 and Q4 specify two different representations for the same state

§2.2 says `resume_validation` is `None` "when no validator is configured". Q4's closed
reason vocabulary includes `no_validator_configured`, which only makes sense as
`{"attempted": False, "reason": "no_validator_configured"}` — a dict. Both cannot be
the contract. This matters because Q4's stated goal is that a consumer can never
confuse "missing" with "passed", and an ambiguous null-vs-dict contract for the most
common production state (§3.3: every incident, every tick) is exactly where that
confusion would start. The task should pick one; `None` for "no validator" reads more
consistent with how `harness_resume` already behaves, in which case
`no_validator_configured` should come out of the Q4 vocabulary.

### N3 — non-blocking: the design reads the same evidence table twice per incident, and does not say what happens when only one of the two readers is configured

`tick()` already calls `self._advisory_environment_evidence(incident.get("run_id"))` at
`supervisor.py:285`, and that returns the full decoded rows — `spec_snapshot` included
— for the same `run_id` the validator would use. A validator taking only `run_id` must
therefore open the table a second time for the same incident in the same tick. Two
consequences worth deciding rather than inheriting: it is a redundant read, and the two
reads can in principle observe different rows, so `environment_evidence` and
`resume_validation` on the same action dict could disagree about what the run declared.
Passing the already-read rows into the validator would remove both. The counter-argument
is real — `environment_reader` may be `None` while a validator is configured — but the
note does not consider that combination at all, and it should: as written, a deployment
with a validator and no `environment_reader` is a supported configuration whose
behavior is unspecified.

### N4 — non-blocking, and the largest thing the note does not discuss: no stated authority argument for executing DB-sourced commands unattended

`run_validation_tier` executes `spec.validation.quick` as shell commands via
`subprocess.run(..., cwd=repo_root)`, and its docstring justifies that on the grounds
that the commands are "declared, trusted operator/environment-authoring content (the
same trust boundary `EnvironmentSpec.setup_commands` already relies on), not caller
input". On the path this note proposes, the commands do not arrive from an
operator-authored file — they arrive from a `run_environment_evidence` row, decoded from
`spec_snapshot`, and are executed by an unattended recovery pass with no human in the
loop, potentially piggybacked on a `maps claim`. That may well be fine, but the note
never states the argument, and it is the one place where this design widens a trust
boundary rather than narrowing one. Recommend the implementation task state explicitly
who is authorised to write `run_environment_evidence` rows (the `recorded_by` actor),
and that executing a row's `validation.quick` is deliberately being treated as the same
authority as executing that spec's `setup_commands`. Q2's decision to keep validation
off the `claim` path already limits the blast radius, which is a good instinct — this
finding asks for the reasoning to be written down rather than left implicit.

### N5 — non-blocking, cosmetic: one line-number cite drifts

§2.3 cites `run_recovery_tick (production.py:80-97)`. The function is defined at
`production.py:54` and runs to 97; 80-97 is only its body's tail. Every other cite I
checked (roughly thirty of them) is accurate to the line. Not worth a re-spin on its
own.

### N6 — non-blocking: say out loud that the new `--repo-root` must *not* copy the existing convention

§3.4 correctly requires "no implicit cwd default", and correctly cites the two existing
`--repo-root` flags — but both of those are `default='.'` (cli.py:145, cli.py:239). An
implementer adding a third `--repo-root` will reach for the house style and get an
ambient cwd default, which is precisely non-goal 3. The note has the right rule and the
contradicting precedent in the same paragraph without flagging the tension; one clause
("deliberately unlike `context`/`flow start`, this flag must default to `None`, not
`'.'`") would close it.

## 14. Reviewer limits

- This is a design note; there is no executable artifact to test, so no
  non-tautology or mutation check was possible. What I could verify is that every
  factual claim the design rests on is true at this head, and that the proposed
  placement is consistent with the actual control flow of `tick()` — both done by
  reading the source, not the prose.
- I did not evaluate whether an advisory (non-gating) validation tier is the right
  *product* answer for H4's exit gate. I verified that the note's reading of the exit
  gate is supported by the exact checklist text, and that its choice is internally
  consistent with the non-goals it inherited. Whether validation should eventually
  become mandatory is explicitly deferred by §2.1 and Q9 to a later policy task, and I
  agree that deferral is the correct scope call here.
- The greps in §1.2 of the note are attributed to `8923adb`; I re-ran them at the
  reviewed head rather than at that sha, and they all still hold, so nothing turns on
  the difference.
- I did not review the two unrelated docs the branch's merge of `origin/main` brought
  in; they are outside this PR's contribution and outside the three-dot diff. The
  suite run above was started before that merge and finished after it; the merge is
  two Markdown files and no Python (`git diff a93d01d..0288ac2 --name-only` lists only
  those two), so the run's result carries to the bound head unchanged.
