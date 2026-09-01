# PR #239 review evidence — 6.9/S6 slice 3 (per-resource sha256) scoping note

Independent verification-only review by maps-lean-luve (gela authored). Design
only, 1 file (`work/notes/2026-09-01-6.9-slice3-per-resource-hash-design.md`,
+265); no runtime / tests / schema / checklist change. Verdict in the note =
PARK.

## Checks (all against merged main ccbd87e / #237)

1. **"`load_skill_resource` whole-dir-verifies + zero production callers" —
   ACCURATE, both halves.** `runtime/skills/format.py:457`: allowlist-checks
   `relative_path in descriptor.resource_paths`, then calls
   `_verified_snapshot(descriptor)` (recomputes the whole-directory hash,
   raises `SkillChangedError` unless it equals `descriptor.content_sha256`)
   before returning the one file's bytes. `/usr/bin/grep -rn "load_skill_resource"
   runtime/` → only the `__init__` re-export + docstring/comment mentions
   (`context_builder.py:397,495`, `flow_start.py:115` — no `(` call site). No
   production caller.
2. **`execution_resources` manifest is inert — ACCURATE.** `/usr/bin/grep -rn
   "execution_resources" runtime/ tests/` → only `context_builder.py` (the
   writer + the `skill_execution_resources_listed` coverage counter) and a
   `flow_start.py` docstring. Nothing reads
   `plan["skills"][i]["execution_resources"]`.
3. **Scope fork NOT conflated — CONFIRMED.** Verdict PARK + §3 are strictly
   field-only ("add one field parallel to `resource_sizes` + surface it in the
   manifest"); §4 explicitly separates partial-resource verification (skipping
   `_verified_snapshot`) as "a different, larger slice" with its own
   correctness decision. Matches slice-2 §6's deferral wording.
4. **§3 field-only spec mirrors the merged `resource_sizes` pattern
   accurately — CONFIRMED.** Same `tuple[tuple[str, str], ...] = ()` shape,
   same `resource_paths` ordering, populate in both `_descriptor_for_root` and
   `load_skill`, add to the `load_skill` `SkillChangedError` identity check,
   `"sha256"` manifest key from `dict(descriptor.resource_hashes)` with the
   None-when-unrecorded convention. Per-file digests fold into the existing
   `_directory_hash` read (no second read). Executable as a one-shot dispatch.
5. **Operator decision NONE — CONFIRMED vs wave12.**
   `work/tasks/context-budget-classification-wave12.md`: operator approval is
   required only for a field "read by other code to decide what to load/fetch".
   A recorded/exposed per-resource digest drives no load/fetch decision — it
   rides the trust gate's existing LOAD decision, same as `resource_sizes`.

## PARK is the right call

Rule 8 (smallest change) + rule 13 (bounded first; machinery only on repeated
evidence). The note's Q1 table traces all four would-be consumers and shows
each is hypothetical: `load_skill_resource` callers (none — and it
whole-dir-verifies anyway, making a per-resource digest redundant on that
path); a downstream manifest reader (none — manifest verified inert); a
drift-localizing re-discovery workflow (none); a partial-verification fast path
(none — §4's larger design). PARK hides no real consumer need and no operator
call (both independently verified). The §3 spec is kept ready for a one-shot
dispatch when a consumer appears.

Non-blocking: the note's §4 "confirm which interpretation slice 3 is" is
slightly stale vs the coordinator's already-made field-only resolution —
annotated at merge (field-only, PARK stands). `python3 -m runtime.smoke` exit 0.

reviewer: maps-lean-luve
head_sha: 98637e7445fa5b4de939a960329d16a2325dac50
independent: true
summary: APPROVE — verification-only review of a design-only PARK scoping note; all five dispatch checks verified against merged main ccbd87e (load_skill_resource whole-dir-verifies and has zero production callers; execution_resources manifest is inert; the scope fork is explicitly separated not conflated; the §3 field-only spec mirrors the merged resource_sizes pattern and is one-shot-dispatchable; no operator decision per wave12); PARK is a sound rule 8/13 defer that hides no real consumer need.
