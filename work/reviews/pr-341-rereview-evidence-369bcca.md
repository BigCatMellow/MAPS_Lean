# PR #341 — focused J3/v5 safeguard re-review (r9)

reviewer: claude-opus-5-fresh-rereviewer-pr341-r9
head_sha: 369bccaf68b258c70eb6efec0c9f70115c8014cb
prior_head: fd2408fda31d574554bf345cde6319fe8313bd90
independent: true
verdict: APPROVED FOR CORPUS CONSTRUCTION
review_state: APPROVED
review_layer: focused J3/v5 safeguard re-review; spec only; nothing executed
summary: APPROVED FOR CORPUS CONSTRUCTION. J3 RESOLVED. v5 whole-document pins reject every additive contradiction placed anywhere in the five normative owners, including r8 probe 9/9b, sibling-section, CASE §5, RUN, SPEC Smoke, REPORT sixth-verdict/terminal, duplicate/shadow-heading, and coordinated manifest+owner variants (all green under v4, all red under v5). Owner blobs byte-identical at r7/r8/head; independently recomputed normalized digests match checker constants. Prior layers intact and independently effective. I2–I4, B/M/N/F/G/H, and 512-state S4 carry forward. No benchmark semantics changed.

## Target and scope

- PR head at review start: `369bccaf68b258c70eb6efec0c9f70115c8014cb` — matched.
- Diff `fd2408f..369bcca`: checker, FRICTION-PR341 carrier, package README, owning task, r8 evidence. No owner document, manifest, or workflow change.
- Scope: J3/v5 only. J2/J4 not reopened. No corpus, holdout, execution, model/API call, spend, runtime change, or merge.

## Baseline

`python scripts/check_protocol_effectiveness_benchmark_anchors.py` → PASS: 49 findings, 107 semantic anchors, 13 structurally pinned sections, 5 pinned owner documents.

## Owner blobs and whole-document digests

Blob IDs identical at `5f1ef8e` (r7), `fd2408f` (r8), and `369bcca`. Digests recomputed with an independent normalizer (not importing the checker) from git blobs at all three commits; checker constants read via AST.

| Owner | Blob | Normalized SHA-256 | Result |
| --- | --- | --- | --- |
| BENCHMARK-SPEC.md | 78b0b7f87a | 86909cba…40cac6 | MATCH |
| CASE-DESIGN.md | d256fb1bb2 | 363c5a0f…c0bfa | MATCH |
| RUN-PROTOCOL.md | 5effb6c787 | d5cf4fe8…436939 | MATCH |
| SCORING-AND-ANALYSIS.md | ff75de6ae4 | f40d4625…eeaf66 | MATCH |
| REPORT-TEMPLATE.md | 5f53c1c3fa | 558cecc5…e35c14ae | MATCH |

Values also equal those published in the r8 evidence. REFERENCES.md unchanged r7→head.

## Mutation matrix

Temporary local mutations only; each restored and tree verified clean. Every mutation run against v5 (head) and v4 (`fd2408f` checker) on the same tree. Result = safeguard behaved correctly.

| Probe | Expected | v5 | v4 | Caught by | Result |
| --- | --- | --- | --- | --- | --- |
| 9 cutoff exception inside SPEC §7.1 (rule intact) | FAIL | red | green | whole-doc | PASS |
| 9b cutoff exception in SPEC §14 | FAIL | red | green | whole-doc | PASS |
| 9b cutoff exception at SPEC §16 end | FAIL | red | green | whole-doc | PASS |
| 9b cutoff exception in SPEC §10 | FAIL | red | green | whole-doc | PASS |
| A SCORING §11 comparator softens WORSE | FAIL | red | green | whole-doc | PASS |
| A SCORING §5 comparator softens WORSE | FAIL | red | green | whole-doc | PASS |
| A SCORING §20 EOF comparator softens WORSE | FAIL | red | green | whole-doc | PASS |
| B CASE §5.2 wrong-class row → TRUE_BLOCK | FAIL | red | green | whole-doc | PASS |
| B CASE §5.3 BLOCKED_WRONG_CLASS counts as success | FAIL | red | green | whole-doc | PASS |
| C RUN §10 single-arm rerun | FAIL | red | green | whole-doc | PASS |
| C RUN §5 single-arm rerun | FAIL | red | green | whole-doc | PASS |
| C RUN §13 EOF single-arm rerun | FAIL | red | green | whole-doc | PASS |
| D SPEC §15 arm-identifiable Smoke tuning | FAIL | red | green | whole-doc | PASS |
| D SPEC §14 arm-identifiable Smoke tuning | FAIL | red | green | whole-doc | PASS |
| E REPORT sixth verdict in Verdict derivation | FAIL | red | green | whole-doc | PASS |
| E REPORT sixth verdict in Disposition | FAIL | red | green | whole-doc | PASS |
| E REPORT terminal weakening in Terminal strata | FAIL | red | green | whole-doc | PASS |
| Duplicate `## 8. TRADEOFF_RULE_V1` | FAIL | red | green | unique-heading + whole-doc | PASS |
| Duplicate `## Verdicts` | FAIL | red | green | unique-heading + whole-doc | PASS |
| Shadow: accepted copy first, altered second occurrence | FAIL | red | green | unique-heading + whole-doc | PASS |
| Missing finding ID (M6) | FAIL | red | red | 49-ID set | PASS |
| Extra finding ID | FAIL | red | red | 49-ID set | PASS |
| Duplicate finding ID | FAIL | red | red | 49-ID set | PASS |
| Owner-path retarget H1 → README | FAIL | red | red | owner map | PASS |
| Trivial anchor (`WORSE`) | FAIL | red | red | anchor quality + anchor presence | PASS |
| Heading-only anchor | FAIL | red | red | anchor quality | PASS |
| Duplicate anchor | FAIL | red | red | duplicate-anchor | PASS |
| H1 below minimum count | FAIL | red | red | min count | PASS |
| Coordinated manifest anchor + SCORING exception | FAIL | red | green | whole-doc | PASS |
| README M12 declaration removed | FAIL | red | red | anchor presence | PASS |
| `PROMISING` in REPORT Interpretation | FAIL | red | red | report vocab + whole-doc | PASS |
| Canonical verdict line altered | FAIL | red | red | section hash + whole-doc | PASS |
| BLOCKED_WRONG_CLASS removed | FAIL | red | red | report vocab + section + anchor + whole-doc | PASS |
| One-character punctuation edit in RUN §10 | FAIL | red | green | whole-doc | PASS |
| CRLF, all five owners | PASS | green | green | — | PASS |
| EOL whitespace on body lines | PASS | green | green | — | PASS |
| Extra/leading/trailing blank lines + CRLF | PASS | green | green | — | PASS |
| Generic 20+ char anchor substitution (J4, owners unchanged) | PASS (known optional) | green | green | — | as expected |

Layer isolation: with whole-doc constants re-baselined to the mutated tree, duplicate/shadow headings still fail on unique-heading, `PROMISING` still fails on report vocabulary, and a pinned S4 section edit still fails on section hash. Whole-document pins extend, not replace, prior layers.

## Safeguard layers

49-ID set, owner map, anchor quality, duplicate-anchor, minimum counts, 13 section hashes, report vocabulary (canonical two verdict lines, `BLOCKED_WRONG_CLASS`, forbidden tokens): intact. Whole-document hashes: new, checker-owned, effective. Unique-heading: new, effective independently.

## Carried-forward results

Owner blobs are byte-identical to the r7/r8 reviewed versions; carry-forward is valid.

- I2: STILL RESOLVED
- I3: STILL RESOLVED
- I4: STILL RESOLVED
- B/M/N/F/G/H: STILL RESOLVED
- S4 (r8): 512 states; 0 ambiguous; 0 unhandled; 0 semantic mismatches. SCORING digest `f40d4625…eeaf66` matches.

## CI at exact head

- review-evidence run `34636847625`: step `Verify protocol benchmark resolved-finding anchors` success; step `Verify review evidence for exact head` failure — reproduced locally: canonical `pr-341-review-evidence.md` still bound to `465d973`. Expected fail-closed; not a J3 failure.
- Runtime stack tests run `34636847537`: success.

## Findings

No BLOCKING, MATERIAL, or MINOR findings for this gate.

OPTIONAL:

1. Normalization uses `str.splitlines()`, so replacing a newline with U+2028, form feed, or NEL is digest-equivalent (v4 same). Cannot add or remove printable text; may affect rendering. Fix if desired: split only on `\n` after `\r\n`/`\r` normalization, or reject those characters.
2. Pre-existing fail-closed false positives (v4 same): trailing whitespace on a pinned heading line and on the multi-line G3 anchor turns the check red.
3. Outside the five-owner boundary: contradictions appended to README or a new package file claiming precedence remain green. Not the observed regression class; governed by one-concept/one-owner and diff review. Optional hardening: pin the package file set.
4. J3 task edit removed the task's `## AGI readiness` block while retaining `AGI status: AGI READY`. Restore when shaping the corpus-construction task.
5. Canonical `FRICTION_LOG.md` append remains pending (carrier exists; already tracked in task).

## Adversarial answers

1. Additive contradiction anywhere in the five owners without failing: no.
2. Relocation to unpinned sibling section escapes: no.
3. RUN changes undetected: no.
4. Duplicate pinned heading confuses extraction while green: no.
5. Manifest-only edit authorizes changed owner: no.
6. Sixth verdict outside `## Verdicts`: no.
7. Terminal semantics weakened outside `## Terminal calibration`: no.
8. Cutoff non-retroactivity contradicted elsewhere in SPEC: no.
9. Fails closed on any normative owner edit, requiring explicit checker change and fresh review: yes (whitespace/line-ending normalization only).
10. Proportional: yes. Six recorded regression/safeguard-gap occurrences r3–r8; owners are pre-registration artifacts that should be frozen at this gate; SPEC §14 already requires versioning for changes; next phase does not require owner edits.
11. J3 correction altered experimental semantics: no.

## Final assessment

v5 catches additive contradictions anywhere in the five normative owners. The invariant-13 repeated-regression pattern is adequately mechanically guarded. Owner semantics are unchanged. MAPS_L can still credibly win or lose; Arm C attribution, leakage controls, stress/counterweight rules, verdict logic, and holdout protections remain intact as independently verified at r8 on identical blobs.

Operational note: filling SPEC §11 `UNSET` thresholds in place will trip the pin by design; do it under the pre-run gate with a checker hash update and review, or as a separate frozen manifest.

The pre-corpus design gate is open. The next authorized phase is bounded construction of the initial primary corpus and sealed holdout followed by fresh independent corpus/pre-freeze review. Benchmark execution remains prohibited.
