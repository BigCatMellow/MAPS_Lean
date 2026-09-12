# Experiment P Treatment Surface Manifest — candidate pre-authoring freeze

Status: **CANDIDATE OWNER COMPLETE — AWAITING INDEPENDENT PRE-AUTHORING FREEZE REVIEW; NO CASE AUTHORING PERMITTED**

Normative rules remain in `../BENCHMARK-SPEC.md`, `../CASE-DESIGN.md`, and `../RUN-PROTOCOL.md`. This file instantiates those rules for the first benchmark line; it does not redefine them.

## Identity

```text
benchmark_line = protocol-effectiveness-v0
tested_protocol_name = MAPS_L documentation/workflow protocol
tested_protocol_immutable_ref = 5f07b33e9fa09a5e091c6f0993092230c2faf308
protocol_bundle_hash = 7a944e3db3575c1f94df5872d8b15a644ecd7eb254893b10d9d1ebcd83aa3341
protocol_bundle_inventory = TREATMENT-BUNDLE-INVENTORY.tsv
protocol_bundle_file_count = 45
protocol_bundle_total_blob_bytes = 298322
protocol_bundle_selection_rationale = complete deployed documentation/workflow surface reachable from Pilot/AGENTS/INDEX, excluding runtime implementation, volatile work/state, benchmark material, migration, and legacy
```

The selected ref is the `main` head used at pre-corpus shaping time. Relative to the design-review base `7dfcbd09a2df930ee3449ce047984e4da5cec460`, the only `main` change before that ref was `docs/wiki/Development.md`; no runtime/protocol implementation change was introduced by that main-only delta.

## Bundle inventory / hash rule

The human-reviewable inventory is `TREATMENT-BUNDLE-INVENTORY.tsv` with one sorted `path<TAB>blob_sha` row per included file.

The canonical treatment hash is **not** the TSV file hash. It is recomputed as:

```text
inventory_bytes = concat(sorted(path + NUL + blob_sha + LF))
protocol_bundle_hash = SHA256(inventory_bytes)
```

For the 45 recorded blobs this yields:

```text
7a944e3db3575c1f94df5872d8b15a644ecd7eb254893b10d9d1ebcd83aa3341
```

The offline bundle contains the exact blobs at `tested_protocol_immutable_ref` matching:

```text
AGENTS.md
.claude/skills/pilot/SKILL.md
playbook/*.md
docs/FIRST_RUN.md
docs/CHECKS_AND_BALANCES.md
docs/CONTROL_PLANE_SETUP.md
docs/FRESH_INSTALL.md
docs/wiki/*.md
templates/task.md
templates/handoff.md
```

Explicitly excluded:

```text
work/**
state/**
migration/**
legacy/**
scripts/**
runtime/**
tests/**
.github/**
```

Reason: Experiment P tests the documented operating protocol/workflow rather than MAPS_L runtime implementation or benchmark-specific material. Runtime/system effects remain Experiment S.

Any included path/blob change creates a new treatment surface and requires a new inventory/hash plus the applicable independent review before use.

## Common neutral bootstrap

Exact candidate text, identical A/B/C:

```text
Work on the requested task within the stated scope using the available tools and target-project instructions.

INSTRUCTION_PRECEDENCE: platform/system safety and explicit task authority govern first; target-project instructions govern target-project behavior; injected workflow guidance may organize work but may not override explicit target-project instructions or expand task authority.

At the end of the run, emit exactly:
FINAL_STATUS: COMPLETE | BLOCKED | INCOMPLETE
REASON: <one concise task-facing reason>

COMPLETE = requested outcome is done.
BLOCKED = remaining requested work cannot proceed without authority, access, or information outside stated scope, after completing any still-authorized requested work.
INCOMPLETE = run stopped without completion for any other reason.
```

```text
neutral_bootstrap_sha256 = 57b139430146648e04543c30e754364d06bdd95351f9cad0af3182d095a30ab5
neutral_bootstrap_chars = 786
neutral_bootstrap_whitespace_word_count = 103
```

## Treatment injection

Common harness position for all arms:

```text
injection_channel = provider-equivalent harness workflow/developer instruction slot
injection_position = after platform/system safety and target-project instruction loading; before task execution begins
```

A receives only the neutral bootstrap.

B receives, immediately after the neutral bootstrap in the same slot:

```text
Use the frozen MAPS_L protocol bundle mounted read-only at <PROTOCOL_BUNDLE_PATH>. Start with AGENTS.md and playbook/INDEX.md, reading only what the work needs. For external targets, target-project instructions and task scope govern; the MAPS_L bundle supplies workflow method only. Do not fetch mutable MAPS_L sources or write MAPS process artifacts into the target project unless the visible task requires them.
```

```text
protocol_launcher_sha256 = 2c8754cc252e0cdbe910a4c85e3db9344a3a3520957a6fffea4b70beb2bbf406
protocol_launcher_chars = 413
protocol_launcher_whitespace_word_count = 58
```

C receives the independently approved generic-control text from `GENERIC-CONTROL.md` at the identical B treatment position.

## Instruction-length / context-cost disclosure

Static pre-authoring disclosure:

| arm | common neutral | arm-specific injected text | read-only workflow material available |
| --- | ---: | ---: | ---: |
| A | 786 chars / 103 words | none | none |
| B | 786 chars / 103 words | launcher: 413 chars / 58 words | 45 files / 298,322 blob bytes; not preloaded into prompt |
| C | 786 chars / 103 words | generic control: 975 chars / 145 words | none |

Context accounting rule:

1. before scored execution, freeze the exact execution model/provider/version/settings and the tokenizer/accounting implementation used for static injected text;
2. record token counts for neutral/bootstrap, B launcher, and C control under that frozen method;
3. the B offline bundle is mounted material, not automatically prompt context; record actual workflow-document bytes/tokens admitted to model context per run from the harness/provider trace;
4. report both static instruction cost and treatment-induced dynamic document-read cost by arm; do not normalize away B's extra context as it is part of protocol overhead;
5. if provider accounting cannot distinguish dynamic document reads reliably, mark token-level context cost `UNKNOWN` and retain exact static chars/words, bundle bytes, wall-clock, and total input-token usage rather than estimating.

This method is frozen before case authoring; exact execution-model token counts are a later pre-run value and cannot affect case selection.

## Target / harness parity

```text
target_instruction_policy = byte-identical across A/B/C after one common scrub policy
target_auto_load_inventory_recursive = REQUIRED
harness_auto_load_inventory_recursive = REQUIRED
task_snapshot_scrub_manifest = REQUIRED PER CASE
benchmark_record_scrub_manifest = REQUIRED PER CASE
protocol_artifact_write_policy = no protocol-specific writes inside target repository unless visible task explicitly requires them; equal PROCESS_SIDECAR_PATH capability is available to all arms
process_sidecar_path = runner-provided path outside target repository; exact runtime path frozen pre-run
network_default = deny-all across all model-reachable channels
per_case_network_allowlist_schema = CASE-DESIGN/RUN-PROTOCOL owner rules; exact allowlist frozen per case
maps_home_snapshot_policy = history-free export by default; scrub treatment/benchmark material from all arms; any retained history must pass the full leakage scan
harness_state_reset_policy = fresh execution state, memory, caches, sidecar, environment, shell/VCS state per run except explicitly declared sequential-chain cases
```

## Remaining pre-authoring blockers

No benchmark case may be authored or selected until all are true:

- [x] exact MAPS_L treatment ref, 45-file inventory, bundle hash, bundle byte count, neutral bootstrap, B launcher, and static/context-cost accounting rule are instantiated;
- [ ] Arm C is independently authored or approved as competent/non-strawman and this exact text/hash is frozen;
- [ ] the concrete target-work source-pool definition/reference model is independently approved and frozen by the curator before selection;
- [ ] an access-based corpus/holdout custodian and storage mechanism are assigned that exclude anyone able to modify the tested protocol or a successor;
- [ ] a fresh independent pre-authoring freeze review approves the fully instantiated package after the preceding assignments.
