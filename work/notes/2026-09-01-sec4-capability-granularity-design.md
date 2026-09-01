# SEC4 capability granularity — network read/general reconciliation split + per-path filesystem-write (design)

**STATUS: DESIGN ONLY. Changes no runtime code, no schema, no checklist status.**
Phase 1 scoping — do not implement until this note lands and the coordinator
confirms the slice.

Dispatched off luve's PR #223 review note 1: *"§4 `network-read` at baseline
is the most generous edge — a Skill declaring only `network-read` still opens
outbound connections on a task with no `external_side_effect`... the impl
reviewer or a later granularity slice may want it gated,"* plus the PR #230
non-blocking out-of-scope item *"Per-capability granularity (`network-read` vs
`network-general`, `filesystem-write` scoped to paths) — slice 2 stays
whole-Skill / coarse-class."*

All facts re-verified against `origin/main` `89a8c60` (rule 14).

---

## 1. Re-verified facts

### 1a. Correction to the dispatch's framing: the tokens are already split

`work/roadmaps/agent-harness-capabilities/04-agentic-security.md` §5.1 already
lists `network-read` and `network-general` as **two distinct** vocabulary
tokens, and `runtime/skills/format.py::_CAPABILITY_TOKENS` (lines 27–39)
already contains both. There is no missing token to add. The actual gap is at
the **detector-reconciliation layer**, `runtime/skills/gate.py`:

```
_DETECTOR_CAPABILITY = {
    "SCRIPT_NETWORK_ACCESS": "network-general",   # one undifferentiated finding
    ...
}
_SATISFYING_TOKENS = {
    "network-general": frozenset({"network-general", "network-read"}),
}
```

`_NETWORK_ACCESS_RE = (?i)(?:\b(?:curl|wget)\b|\brequests\.(?:get|post|put|delete|request)\b|https?://)`
is **one** regex — it cannot distinguish a read-only network call from a
mutating one (curl/wget's verb depends on flags the regex never parses; a bare
`https://` mention carries no verb at all). So the detector always emits the
single `SCRIPT_NETWORK_ACCESS` finding, mapped to the single capability class
`network-general` — and `_SATISFYING_TOKENS` lets a Skill clear that finding
by declaring **either** `network-general` or the weaker `network-read`. That
is the actual "split" this note addresses: not a missing token, but an escape
hatch in reconciliation. Confirmed at `gate.py:118–130`.

### 1b. `filesystem-write` is unscoped at every layer, confirmed

`format.py::_CAPABILITY_TOKENS` has only the bare token; `gate.py::_DETECTOR_CAPABILITY["DESTRUCTIVE_OPERATION"]
= "filesystem-write"` (the `_DESTRUCTIVE_RE` detector matches text like `rm
-rf`/`DROP TABLE` with **no path extraction**); `runtime/skills/capability_policy.py::_BASELINE`
includes bare `filesystem-write` unconditionally, with the stated rationale
"gating it on `destructive_action` would DENY every implementation Skill." No
layer carries or checks a path today.

### 1c. The one existing parameterized-token precedent

`secret-use:<capability-name>`, `format.py:42` `_SECRET_USE_RE = ^secret-use:
[a-z0-9][a-z0-9-]*$`; `capability_policy.py::_required_flags` recognizes the
`secret-use:` prefix via `_SECRET_USE_PREFIX` and maps it to
`security_sensitive`. This is the shape a new parameterized token should copy.

### 1d. `task["output_paths"]` exists, separately from `task["policy"]`

`runtime/state/base.py:262-263` populates `task["output_paths"]` from
`task_output_paths` on every `get_task`; `runtime/context_builder.py:324`
already reads it (for Skill-selection signal tokens, unrelated to
capabilities). `capabilities_within_envelope` (`capability_policy.py`) reads
only `task.get("policy")` today — `output_paths` is a **different** part of
the same `task` dict, not currently wired to the capability intersection at
all.

### 1e. Zero live manifests to migrate

`ls .claude/skills/` → exactly one bundled Skill, `pilot`; it has **no**
`capabilities` sidecar file. `/usr/bin/grep -rn "network-read\|filesystem-write"
.claude/` → nothing. There is no existing manifest anywhere in this repo that
either change could break.

### 1f. Gate-logic changes are not retroactive for already-recorded Skills

`runtime/skills/catalog.py::register_skill_catalog` (lines 264-294): "Idempotent:
entries whose content-addressed `catalog_key` already has a subject row are
skipped, so a re-run after a partial repo change only assesses the genuinely
new revisions." A change to `_SATISFYING_TOKENS` (or any gate logic) is
consulted only when `assess_skill` actually runs — for a not-yet-recorded
`catalog_key`. An already-`VALIDATED`/`APPROVED`/`ACTIVE` Skill's durable
lifecycle state is never re-derived by a later gate-logic change; only a
**new** Skill, or an **existing Skill whose content changes** (producing a new
content-addressed `catalog_key`), is assessed under the tightened rule.
Combined with 1e: tightening §2(A) below breaks nothing that exists today, and
only ever affects future/changed Skills.

### 1g. No schema involvement anywhere in this machinery

The capability manifest is a sidecar text file (`format.py`), a `tuple[str,
...]` descriptor field (`SkillDescriptor.declared_capabilities`), and a pure
dict-based policy check (`capability_policy.py`). No table, no column,
anywhere in the chain from parse to intersection.

---

## 2. The two changes, precisely

### (A) Close the `network-read` reconciliation escape hatch — `gate.py` only

Remove `"network-read"` from `_SATISFYING_TOKENS["network-general"]`, so the
alias set for `network-general` becomes `frozenset({"network-general"})`
(effectively: no alias — a declared `network-general` is the only thing that
satisfies a detected `SCRIPT_NETWORK_ACCESS` finding).

**Effect:** a Skill whose script/resource content actually trips the network
detector must now declare `network-general` to clear review (`DECLARED_CAPABILITY_USE`
INFO); declaring only `network-read` on such a Skill now leaves the detector
finding **undeclared** → `UNDECLARED_CAPABILITY` BLOCK → `QUARANTINE`.
`network-read` remains a valid, `_BASELINE`-permitted token for a Skill that
**self-asserts** read-only network use **without** tripping the detector
(prose-only Skills describing network behavior, or a future finer detector) —
today that assertion carries no enforcement teeth of its own (nothing emits a
read-only-specific finding), so the practical change is narrow and precise:
`network-read` stops being usable to *dodge* a real detected access; it is
unaffected as a plain descriptive declaration.

**`capability_policy.py` is unchanged.** `network-read` stays `_BASELINE`
(always-permitted) at the *policy* layer — self-declaring "I only read the
network" should not itself require `external_side_effect`; the fix is entirely
at the *gate-reconciliation* layer, which decides whether a Skill's actual
detected behavior is covered by what it declared.

**Why not a verb-aware detector instead?** Distinguishing read vs. write
network calls reliably (parsing curl/wget flags, HTTP client method calls,
tracking bare URL mentions to their calling context) is a materially larger,
separate effort with its own false-positive/negative risk — out of scope here
(rule 13). The reconciliation-level fix removes the actual escape hatch with a
one-line change and no new detector.

### (B) Optional per-path `filesystem-write:<path-prefix>` token — vocabulary + parsing only

Add a parameterized form alongside the existing bare `filesystem-write`,
mirroring `secret-use:<name>`'s shape exactly:

- `format.py`: `_FILESYSTEM_WRITE_PATH_RE = re.compile(r"^filesystem-write:
  [A-Za-z0-9_.\-/]+$")` (posix-relative-path-shaped suffix; no leading `/`,
  no `..` segment — reject traversal the same way a resource path is never
  absolute). Recognized in `_parse_capability_manifest`'s token-check branch
  alongside `_CAPABILITY_TOKENS` and `_SECRET_USE_RE`.
- A Skill **may** narrow its self-declared write claim (`filesystem-write:
  output/`) instead of the unscoped `filesystem-write`. Nothing requires it;
  bare `filesystem-write` keeps its exact current meaning.
- **This note's slice stops at vocabulary + parsing.** It does **not** wire
  the declared path against anything (§4) — see the reasoning there.

---

## 3. Mapping into `declared ⊆ permitted` (`capability_policy.py`) — backward compatible

- `network-read`: **no change.** Stays in `_BASELINE`. Change (A) lives
  entirely in `gate.py`'s reconciliation, never touches the policy module.
- `filesystem-write:<path-prefix>`: add a prefix branch to `_required_flags`,
  the same shape as the existing `_SECRET_USE_PREFIX` branch —
  `token.startswith("filesystem-write:")` → treated as `_BASELINE` (returns
  `()`, i.e. no `task_policy` flag required), **identically to bare
  `filesystem-write`**. A path-scoped write claim is strictly narrower than
  the unscoped claim it specializes, so it can never need *more* permission
  than what is already baseline-permitted today. `capabilities_within_envelope`
  does not (yet) compare the declared path against `task["output_paths"]` or
  anything else — see §4.

**Backward compatibility:** both changes are additive at the vocabulary layer.
Every manifest that exists today (none, per 1e) needs no edit. For any future
manifest: a bare `filesystem-write` declaration is completely unaffected. A
`network-read`-only declaration is unaffected **unless** the Skill's content
also trips the network detector, in which case (per 1f) only a *new or
content-changed* registration is assessed under the tightened rule — no
already-recorded subject is retroactively re-evaluated or demoted.

---

## 4. Explicitly out of scope for this note

- **Enforcing** the `filesystem-write:<path>` scope against `task["output_paths"]`
  (or any other boundary). `capabilities_within_envelope`'s current signature
  reads only `task.get("policy")`; wiring `output_paths` in is a **second,
  independent intersection axis** — a new function parameter, a path-prefix
  match, and its own test surface. A distinct, reviewable slice, not folded
  into this vocabulary/parsing change.
- **A verb-aware network detector** (read vs. write) at the `gate.py` regex
  layer — see §2(A) rationale.
- **Any change to `_DETECTOR_CAPABILITY`** — `DESTRUCTIVE_OPERATION →
  filesystem-write` stays coarse; the destructive-operation regex cannot
  localize to a path either, so there is nothing yet to reconcile a
  path-scoped declaration against on the detector side.
- **Per-host `network-general` scoping** — same shape of problem as
  path-scoped writes, not addressed here.
- **`THIRD_PARTY` Skills / the operator trust-root question** — unrelated,
  stays batched with SEC4 Half 3 per the slice-1/slice-2 notes.
- **Retroactive re-assessment** of any already-recorded Skill subject — never
  proposed, and 1f shows the mechanism doesn't do this anyway.
- **Any schema/table change** — none needed anywhere in this design (1g).

---

## 5. OPERATOR DECISION

**None required to land this note, and none required to implement §2(B)** (the
additive path-scoped token is a strict narrowing of an already-permitted
capability — no new permission is granted, so no new authority question
arises).

**§2(A) — stated plainly rather than resolved, per the dispatch's
instruction:** removing `network-read` from `_SATISFYING_TOKENS` is a
technical security-mapping tightening — the same category PR #223's
independent review treated as "reviewer scrutiny, not operator sign-off" for
the whole `capability_policy.py` table, and 1e/1f show it changes behavior for
**zero** Skills that exist in this repo today. It is not, in this reviewer's
judgment, an operator-authority question. **If a future implementer or
reviewer judges it consequential enough to want operator awareness before it
ships** — e.g. because it will make some future category of third-party Skill
harder to pass gate review without also carrying `external_side_effect` — that
is a reviewer's call to escalate at implementation time, not a block on
writing or approving this design note. Flagged, not decided, here.

---

## 6. Smallest slice — impl surface (Phase 2, NOT this note)

1. **`runtime/skills/gate.py`**: remove `"network-read"` from
   `_SATISFYING_TOKENS["network-general"]` (one entry); update the two nearby
   comments that describe the alias (lines ~126–130) to state the tightened
   behavior.
2. **`runtime/skills/format.py`**: add `_FILESYSTEM_WRITE_PATH_RE`; recognize
   it in `_parse_capability_manifest`'s token-check branch (same `if line in
   _CAPABILITY_TOKENS or _SECRET_USE_RE.match(line):` shape, one more
   alternative).
3. **`runtime/skills/capability_policy.py`**: add a `filesystem-write:` prefix
   branch to `_required_flags`, mirroring the existing `_SECRET_USE_PREFIX`
   branch — returns `()` (baseline).
4. **Tests**:
   - `tests/test_skills_quality_gate*.py` (or wherever `_SATISFYING_TOKENS` is
     exercised): a Skill declaring only `network-read` with a script that
     trips `SCRIPT_NETWORK_ACCESS` → `UNDECLARED_CAPABILITY` BLOCK (was
     previously `DECLARED_CAPABILITY_USE` INFO); the same Skill declaring
     `network-general` → still `DECLARED_CAPABILITY_USE` INFO (unchanged); a
     Skill declaring `network-read` with **no** network-touching content →
     still clean (no detector fired, nothing to reconcile — unaffected).
   - `tests/test_skills_format.py`: `filesystem-write:output/` parses as a
     valid declared-capability token; `filesystem-write:` (empty suffix),
     `filesystem-write:../etc`, and `filesystem-write:/abs` are rejected
     (manifest `MALFORMED`, same as any unrecognized line today).
   - `tests/test_skill_capability_manifest.py` (or `capability_policy.py`'s
     own test module): `capabilities_within_envelope(["filesystem-write:x/"],
     any_policy)` → permitted, identical to `capabilities_within_envelope(
     ["filesystem-write"], any_policy)`.
   - ≥5 mutations across the changed `_SATISFYING_TOKENS` set, the new regex,
     and the new prefix branch.
5. **`work/roadmaps/CAPABILITY_CHECKLIST.md`**: one evidence clause on the
   SEC4 (and/or 6.10) row — "capability granularity: `network-read` no longer
   satisfies a detected generic network access; `filesystem-write:<path>` is a
   valid, baseline-permitted narrower declaration; path enforcement deferred."
   **No status flip.**

### MAY / MUST NOT

- **MAY change**: `runtime/skills/gate.py` (`_SATISFYING_TOKENS` one entry +
  adjacent comments), `runtime/skills/format.py` (one new regex + one
  recognition branch), `runtime/skills/capability_policy.py` (`_required_flags`
  one new prefix branch), the named tests, `CAPABILITY_CHECKLIST.md` evidence
  text.
- **MUST NOT**:
  - touch `schema.sql` or any table;
  - write the manifest into `task_policy`, or make any `HookRegistry` guard
    read it;
  - wire `filesystem-write:<path>` enforcement against `task["output_paths"]`
    or anything else (§4 — a later slice);
  - change `_DETECTOR_CAPABILITY`, or add/change any detector regex
    (`_NETWORK_ACCESS_RE`, `_DESTRUCTIVE_RE`, etc.);
  - change the meaning of bare `filesystem-write` or `network-general`;
  - re-assess or mutate any already-recorded Skill lifecycle subject;
  - flip any checklist status.

### Acceptance

1. A Skill whose content trips `SCRIPT_NETWORK_ACCESS` and declares only
   `network-read` → `UNDECLARED_CAPABILITY` BLOCK (previously satisfied).
2. The same Skill declaring `network-general` → `DECLARED_CAPABILITY_USE` INFO
   (unchanged behavior).
3. `filesystem-write:<path>` parses as a valid token; malformed suffixes
   (`filesystem-write:`, `filesystem-write:../x`, `filesystem-write:/x`) →
   manifest `MALFORMED`, same as any unrecognized line today.
4. `capabilities_within_envelope` treats `filesystem-write:<path>` identically
   to bare `filesystem-write` (baseline-permitted, no flag required).
5. `CAPABILITY_CHECKLIST.md` gains one evidence clause; **no status flip**.
6. ≥5 mutations killed on the changed reconciliation set / new regex / new
   prefix branch.

### Verification

One blocking foreground `python3 -m unittest` over the gate / format /
capability-manifest / context-builder test modules touched by the change (the
impl task names the exact set once it starts — mirrors the pattern of every
other design note this session). `python3 -m runtime.smoke` exit 0. `git diff
--stat origin/main` = only the MAY-change files.

---

## 7. STOP-condition check (dispatch)

- *Does the split require touching already-shipped manifests in a breaking
  way?* — **No.** No manifests exist in the repo (1e); already-recorded Skill
  subjects are never re-assessed by a gate-logic change (1f).
- *Does this need a schema change?* — **No.** Confirmed at every layer (1g).
- *Is any operator-only judgment call unavoidable?* — **No, not unavoidable.**
  §5 states the one place a reviewer *might* want to escalate, but the note
  does not treat that as a block — it is flagged plainly rather than resolved,
  per the dispatch's own instruction.

No STOP condition triggered as a block on writing this note. §5 records the
one judgment point a future reviewer may choose to escalate.

---

## Resume prompt

You are implementing the **SEC4 capability granularity** slice for
MAPS_Lean — Phase 2 of
`work/notes/2026-09-01-sec4-capability-granularity-design.md` §2/§6. Worktree
off `origin/main`; `git fetch origin main` first; re-verify every cited
callsite at your HEAD (rule 14).

Source of truth: this note §2 "The two changes, precisely" and §6 "Smallest
slice", and the files it cites: `runtime/skills/gate.py`
(`_DETECTOR_CAPABILITY`, `_SATISFYING_TOKENS`, `_NETWORK_ACCESS_RE`),
`runtime/skills/format.py` (`_CAPABILITY_TOKENS`, `_SECRET_USE_RE`,
`_parse_capability_manifest`), `runtime/skills/capability_policy.py`
(`_BASELINE`, `_REQUIRES`, `_SECRET_USE_PREFIX`, `_required_flags`),
`work/roadmaps/agent-harness-capabilities/04-agentic-security.md` §5.1.

Implement exactly §6: (1) remove `"network-read"` from
`_SATISFYING_TOKENS["network-general"]` in `gate.py`, update the adjacent
comments. (2) `_FILESYSTEM_WRITE_PATH_RE` in `format.py`, recognized in
`_parse_capability_manifest`. (3) a `filesystem-write:` prefix branch in
`capability_policy.py::_required_flags`, returning `()` (baseline), mirroring
`_SECRET_USE_PREFIX`. (4) tests per §6 item 4 incl. ≥5 mutations. (5) one
`CAPABILITY_CHECKLIST.md` evidence clause on the SEC4/6.10 row, **no status
flip**.

MUST NOT (see §6): touch `schema.sql`; write the manifest into `task_policy`
or add a runtime-guard read of it; wire `filesystem-write:<path>` enforcement
against `output_paths` or anything else (a later slice — do not build it even
partially); change `_DETECTOR_CAPABILITY` or any detector regex; change the
meaning of bare `filesystem-write` or `network-general`; re-assess any
already-recorded Skill subject; flip any checklist status.

Tests: one blocking foreground `python3 -m unittest` over the exact modules
you touch (name them in your PR). `python3 -m runtime.smoke` exit 0. Push
before any full-suite run; if machine test-contention is active, follow the
coordinator's current targeted-modules protocol and delegate the full suite to
CI (state which modules you ran, in the PR body).

PR into `main` (never push). Do NOT spawn your own reviewer — ping the
coordinator with the PR number. Independent review + mutation; reviewer
commits the evidence file. No self-merge.

STOP + flag the coordinator if: the network-reconciliation change turns out to
affect a Skill that exists by the time you implement (re-run 1e's check at
your HEAD — a new bundled Skill may have landed with a `capabilities` sidecar
since this note was written); or a reviewer/coordinator decides §5's escalation
point should in fact block until the operator weighs in — do not silently
decide either way yourself.
