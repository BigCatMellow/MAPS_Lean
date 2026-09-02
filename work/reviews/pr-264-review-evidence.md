# PR #264 review evidence — 6.9/S6 promotion-gate step RE-RUN (NO FLIP)

reviewer: maps-lean-nava
head_sha: d4c2753b96018cd87da1a7d121d923e419aec43e
independent: true
summary: APPROVE. Independent of the author (vame). nava ran the original #250 gate step; this re-run also lands NO-FLIP and nava's job was to check vame read #250 + the evidence correctly, not defend #250. All 5 dispatch checks pass: (1) EXP-B re-run independently — every metric matches the doc exactly (exact 19/25, exact_rate 0.76, false_activation_cases 0, selection_f1 0.8666..., precision 1.0, recall 0.7647, HARD_NEGATIVE 1.0, VOCABULARY_SHIFT + AMBIGUOUS 0.0, corpus_sha256 2cff0e40…4565 unchanged; 3 tests OK, runtime/ byte-unmodified). (2) §2's criterion table is a faithful redo of #250 §3 — the dispositive HARD_NEGATIVE cap (4/4 false-activate at #250) is genuinely resolved to 0/4, confirmed by the run, not hand-waved; f1 0.722→0.867. (3) §3's "route (a) blocked on §6.33" is sound and directly grounded in the roadmap: §6.33's own promotion gate names "paraphrases, vocabulary shifts, hard negatives" as its eval categories and mandates "explicit-first" for the Context Builder — so closing VOCABULARY_SHIFT lexically either regresses HARD_NEGATIVE (V01 lemmatised == H02/H03 shape) or requires a synonym map = §6.33 query-expansion; AMBIGUOUS margin regresses MULTI_SKILL's genuine ties. No untried lexical path that doesn't regress an already-passing category. (4) No status cell changes value (6.9 IN PROGRESS→IN PROGRESS; S6 gains one prose clause, status unchanged; L4 prose corrected post-#260); checklist edit is prose-only; no runtime/tests/corpus touch; `/usr/bin/grep -nE '^(<<<<<<<|=======|>>>>>>>)'` → empty; scoreboard 16/13/6 unchanged. (5) §4's deferral of the §6.9-vs-§6.33 scope call to an operator §17.3 ruling (not a reviewer) is correct — §17.3 explicitly lists "explicit operator decision" as status evidence, and a reviewer unilaterally overriding a prior independent NO-FLIP on the "literal gate is met" technicality is the status-truth anti-pattern (rule 11 / rule 17). vame recommends YES but leaves the call to the operator — the right posture.

## What was verified

**1. EXP-B re-run (rule 14).** `python3 -m unittest tests.test_exp_b_skill_routing -v` → Ran 3, OK.
```
corpus_sha256          2cff0e405c2f0201759ad8d23ed84fbb60bc1ec7d5513be2ad9b4c54fe5f4565  (UNCHANGED)
exact_cases 19  exact_rate 0.76  false_activation_cases 0  missed_activation_cases 4
ambiguity_misses 2  selection_precision 1.0  selection_recall 0.7647058823529411  selection_f1 0.8666666666666666
category_accuracy: DIRECT 1.0  PARAPHRASE 1.0  MULTI_SKILL 1.0  NO_SKILL 1.0  HARD_NEGATIVE 1.0  VOCABULARY_SHIFT 0.0  AMBIGUOUS 0.0
```
Matches the doc §1 to the digit. `git diff --stat` = the note + `CAPABILITY_CHECKLIST.md` only.

**2. §2 vs #250 §3.** #250 §3 item 3 (hard-negative false-activation cap, 4/4 FAIL) was explicitly "dispositive. NO FLIP"; item 4 (f1 0.722) "middling". vame's §2: item 1 MET, item 2 1.00×4 (no regression — confirmed), item 3 "RESOLVED" (0/4, HARD_NEGATIVE 1.00 — confirmed by independent run), item 4 0.867. Faithful; resolution of item 3 is real, not asserted.

**3. §3 "route (a) blocked on §6.33" — load-bearing, sound.** §6.33 (roadmap lines 1375–1387): "Semantic retrieval / query expansion — EVIDENCE-GATED"; "Context Builder stays explicit-first"; promotion gate = frozen eval with "paraphrases, vocabulary shifts, hard negatives and no-answer cases ... meaningful improvement over explicit/baseline". VOCABULARY_SHIFT is literally §6.33's own eval category. vame's mechanism check (V01 credential→credentials weight 1.0 == H02/H03 lexical shape; any floor admitting V01 re-admits H02/H03 → HARD_NEGATIVE regresses; V02–V04 need true synonymy; AMBIGUOUS margin loose enough for A01 also flags genuine M01 tie → MULTI_SKILL regresses) = same conclusion luve's #260 review reached; re-checked against frozen corpus. Distinguishing signal in every residual case is semantic, not lexical = §6.33 by the roadmap's own words.

**4. No status flip / prose-only / no markers.** 6.9 IN PROGRESS→IN PROGRESS; S6 gains "Gate step RE-RUN … NO FLIP" clause, status unchanged; L4 prose corrected to post-#260 numbers. No runtime/tests/*.json change. Conflict-marker grep → empty. Scoreboard DONE 16 / IN PROGRESS 13 / NOT STARTED 6 — unchanged.

**5. §4 NO-FLIP reasoning vs rule 11 / rule 17.** Both readings stated honestly. NO-FLIP rests on: (i) #250 ruled "0.00 on §6.9's own listed categories is not DONE" + set routes (a)/(b); #260 completed 1 of 3 of (a), §3 shows (a) can't finish under explicit-first → only (b); (ii) the §6.9-vs-§6.33 scope-boundary is an authority call, §17.3 lists "explicit operator decision" as exactly that evidence type; (iii) a reviewer resolving it unilaterally is the status-truth anti-pattern. Correct — operator's call, not reviewer's.

## Verdict: APPROVE
Faithful, independently-reproduced redo of the #250 gate step against #260's numbers. NO-FLIP correct: dispositive #250 item resolved, route (a) genuinely §6.33-blocked (grounded in §6.33's own promotion-gate text), remaining scope call is the operator's under §17.3. No status flip, prose-only checklist edit (incl. L4 correction folded in), no conflict markers, corpus frozen.
