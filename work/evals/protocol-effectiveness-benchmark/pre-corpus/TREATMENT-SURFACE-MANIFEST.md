# Experiment P Treatment Surface Manifest — candidate pre-authoring freeze

Status: **CANDIDATE — NOT FROZEN; NO CASE AUTHORING PERMITTED**

Normative rules remain in `../BENCHMARK-SPEC.md`, `../CASE-DESIGN.md`, and `../RUN-PROTOCOL.md`. This file instantiates those rules for the first benchmark line; it does not redefine them.

## Identity

```text
benchmark_line = protocol-effectiveness-v0
tested_protocol_name = MAPS_L documentation/workflow protocol
tested_protocol_immutable_ref = 5f07b33e9fa09a5e091c6f0993092230c2faf308
protocol_bundle_hash = UNSET — must be generated and frozen before any case authoring
protocol_bundle_selection_rationale = complete deployed documentation/workflow surface reachable from Pilot/AGENTS/INDEX, excluding runtime implementation, volatile work/state, benchmark material, migration, and legacy
```

The selected ref is the current `main` head at pre-corpus shaping time. Relative to the design-review base `7dfcbd09a2df930ee3449ce047984e4da5cec460`, the only `main` change is `docs/wiki/Development.md`; no runtime/protocol source changed outside that documentation snapshot.

## Frozen bundle path rule

The offline bundle SHALL contain the exact blobs at `tested_protocol_immutable_ref` matching:

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

Explicitly excluded from the treatment bundle:

```text
work/**
state/**
migration/**
legacy/**
scripts/**
src/**
tests/**
.github/**
work/evals/protocol-effectiveness-benchmark/**
```

Reason: Experiment P tests the documented operating protocol/workflow rather than MAPS_L runtime implementation or benchmark-specific material. Runtime/system effects remain Experiment S.

Before freeze, generate a deterministic sorted `<path>\0<blob_sha>\n` inventory for every included file and set `protocol_bundle_hash = SHA256(inventory_bytes)`. Preserve the inventory beside this manifest. Any path/blob change creates a new treatment surface.

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

## Pre-authoring blockers

No benchmark case may be authored or selected until all are true:

- `protocol_bundle_hash` and exact inventory are set;
- Arm C is independently authored or approved and its text/hash/context cost are frozen;
- A/B/C instruction lengths/context costs are measured under the intended tokenizer/context accounting method;
- the target-work sampling manifest is frozen by an independent curator;
- an access-based corpus/holdout custody mechanism exists that excludes anyone able to modify the tested protocol or a successor;
- a fresh independent pre-authoring freeze review approves this instantiated package.
