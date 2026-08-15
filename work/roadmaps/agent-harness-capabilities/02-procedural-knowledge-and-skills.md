# Roadmap 02 — Procedural Knowledge & Skills

Status: `PLANNING ONLY — NOT ACTIVE AUTHORITY`

Purpose: give MAPS a disciplined way to package reusable expertise, procedures, tool bundles, and examples without bloating `AGENTS.md`, relying on persona prompts, or treating imported community content as trusted authority.

Source research themes:

- Agent Skills open specification and progressive disclosure
- Claude/Copilot/OpenHands/Kiro/Devin procedural packaging
- Kiro Powers / dynamic capability loading
- separation of knowledge, procedure, flow, and tools
- empirical problems in public `SKILL.md` quality
- supply-chain and routing concerns

---

# 1. Why this roadmap exists

MAPS increasingly needs reusable know-how:

- database migration procedures;
- release verification;
- security review;
- incident triage;
- repository-specific build/test workflows;
- domain-specific coding practices;
- tool usage instructions;
- repeatable handoff/review procedures.

The wrong responses are:

1. keep appending everything to `AGENTS.md`;
2. create permanent “expert agents” for every domain;
3. expose every procedure/tool to every worker;
4. download arbitrary community Skills and trust them;
5. treat all context as one undifferentiated memory bucket.

The target is a **progressively loaded, provenance-aware procedural layer**.

---

# 2. Information classes

MAPS should explicitly distinguish the following.

## 2.1 Authority / invariant

Example:

> Production deployment requires operator approval.

Lives in authoritative policy/instructions, not a Skill.

## 2.2 Task context

Example:

> TASK-0042 changes runtime policy evaluation.

Task-specific; loaded through Context Builder/task state.

## 2.3 Fact / knowledge

Example:

> Service X listens on port 8443.

May be useful context. Not a procedure or authority by default.

## 2.4 Skill / procedure

Example:

> How to perform a safe PostgreSQL schema migration.

Reusable method loaded when applicable.

## 2.5 Flow

Example:

> Prepare review → run checks → create submission → route reviewer.

A stable deterministic sequence executed mechanically when mature enough.

## 2.6 Tool / capability

Example:

> PostgreSQL query execution.

Concrete ability, distinct from instructions for using it safely.

## 2.7 Example / demonstration

A compact validated exemplar showing a difficult procedure in action.

Examples are evidence/support for a Skill, not always-on prompt content.

---

# 3. Target architecture

```text
             Task requirements
                    │
                    ▼
             Context Builder
                    │
          ┌─────────┼──────────┐
          ▼         ▼          ▼
       authority   facts   candidate skills
                              │
                              ▼
                       Skill Registry
                              │
                    trust + routing + version
                              │
                              ▼
                     Progressive loading
                              │
                 ┌────────────┼────────────┐
                 ▼            ▼            ▼
              SKILL.md      scripts     references/examples
                 │
                 ▼
            Harness / worker
                 │
                 ▼
            required tools
```

No Skill may bypass canonical policy/authority.

---

# 4. Agent Skills compatibility

## 4.1 Adopt the open directory shape

Preferred base format:

```text
skills/<skill-name>/
  SKILL.md
  scripts/        optional
  references/     optional
  assets/         optional
  examples/       optional MAPS convention
```

Preserve compatibility with the open Agent Skills ecosystem where practical.

## 4.2 Minimum metadata

At minimum use standard-compatible metadata for:

```text
name
description
```

The description must answer both:

- what does this Skill do?
- when should it be used?

Routing quality depends heavily on this.

## 4.3 MAPS-specific metadata

Do not require custom fields until evidence proves they help, but likely useful optional metadata includes:

```yaml
metadata:
  maps-version: 1
  maps-risk: low|medium|high
  maps-required-capabilities:
    - filesystem-write
    - python
  maps-optional-capabilities:
    - git-worktree
  maps-forbidden-capabilities:
    - external-deploy
  maps-review: owner|independent
  maps-trust: bundled|approved-third-party|advisory|quarantined
```

Custom metadata supplements rather than overrides policy.

---

# 5. Progressive disclosure model

The Skill system should minimize context cost.

## Stage A — discovery metadata

Load only compact catalog metadata:

```text
skill ID
name
description
trust state
version/hash
high-level capability requirements
```

## Stage B — activation

When selected, load `SKILL.md` body.

## Stage C — execution support

Load references/scripts/examples only when the procedure reaches a step requiring them.

Never load entire skill libraries at startup.

---

# 6. Skill registry

## 6.1 Purpose

Provide a derived/read-oriented index of installed/available Skills and their provenance.

The registry should answer:

- what Skills exist?
- which version/hash?
- where did each come from?
- what trust state?
- what capabilities do they require?
- what tasks/domains are they intended for?
- when were they last validated?
- are they superseded/quarantined?

## 6.2 Authority

The registry does not grant task authority.

A Skill being `APPROVED` means it is an approved reusable procedure, not that every task may execute every capability it mentions.

## 6.3 Storage

Prefer manifests/indexes derived from filesystem + small approval metadata rather than copying entire Skill content into SQLite.

If approval state becomes durable canonical data, it should store references/hashes, not duplicate Skill bodies.

---

# 7. Skill lifecycle

Candidate lifecycle:

```text
DISCOVERED
   ↓
VALIDATED_METADATA
   ↓
QUARANTINED_FOR_REVIEW
   ↓
APPROVED
   ↓
ACTIVE
   ├─ SUPERSEDED
   ├─ QUARANTINED
   └─ RETIRED
```

For bundled/local Skills, discovery and review may be simpler, but the same provenance principles apply.

A Skill update creates a new hash/version requiring re-evaluation if behavior may have changed.

No silent auto-update of active procedures.

---

# 8. Skill quality gate

## 8.1 Metadata lint

Check:

- name unique/stable;
- description clear and specific;
- intended activation scope explicit;
- no contradictory metadata;
- version/hash present;
- references resolve.

## 8.2 Instruction lint

Look for:

- vague roleplay instead of actionable procedure;
- giant redundant prose;
- hidden authority claims;
- instructions contradicting current MAPS invariants;
- undeclared tool/capability requirements;
- unsafe unconditional destructive/external steps;
- missing failure branches;
- missing completion criteria.

## 8.3 Resource lint

Check scripts/references/assets for:

- unexpected executables;
- network access;
- secrets/credentials;
- path traversal;
- large unnecessary assets;
- generated binaries without provenance;
- unsupported dependencies.

Static lint does not prove safety; it is an early filter.

## 8.4 Behavioral evaluation

Run representative tasks to test:

- correct Skill selection;
- correct non-selection on hard negatives;
- instruction usefulness;
- tool/capability compatibility;
- adherence to task authority;
- outcome quality;
- context/token cost.

---

# 9. Skill routing

## 9.1 Routing should be explicit-first

Strong signals:

- task type;
- declared capability requirements;
- repository/project configuration;
- explicit task source/reference;
- known file/domain mapping;
- user/operator-selected Skill.

Semantic matching may supplement, not replace, these signals.

## 9.2 Skill-selection experiment

Before relying heavily on autonomous Skill selection, build a frozen eval set:

```text
positive tasks
near-miss tasks
paraphrased tasks
vocabulary-shift tasks
hard negatives
no-skill tasks
multi-skill tasks
```

Measure:

- precision;
- recall;
- false activation;
- missed activation;
- top-k ranking;
- context overhead.

This directly guards against the legacy lexical-retrieval failure pattern.

## 9.3 Ambiguous routing

If two Skills materially conflict or imply different consequential procedures:

- surface ambiguity;
- do not merge them by improvisation;
- use explicit task/project selection or ask/route for decision.

---

# 10. Context Builder integration

Context Builder should classify loaded material by purpose.

Candidate output:

```text
AUTHORITY
- AGENTS.md
- task policy

TASK SOURCES
- explicit files
- dependencies

ACTIVE SKILLS
- database-migration@hash

SUPPORTING REFERENCES
- references/postgres-locking.md

ON-DEMAND
- examples/
- large API docs
```

Context plan should state why each Skill was selected and its trust/version state.

---

# 11. Capability Packs

A later abstraction may combine procedural knowledge with executable requirements.

Example:

```text
CapabilityPack: postgres-migration

Skill:
  database-migration

Required capabilities:
  postgres-read
  postgres-write
  filesystem-read

Optional:
  backup-tool

Hooks:
  before_destructive_action
  after_schema_change

Environment:
  postgres-client >= X

Review:
  independent
```

This can simplify routing and progressive tool loading.

Important:

- pack does not grant capabilities;
- task/policy still authorizes them;
- packs should not become mini-agent personas.

---

# 12. Examples / demonstrations

Some procedures benefit from a compact exemplar.

Rules:

- examples optional;
- only load when Skill active and needed;
- sanitize secrets/user data;
- include tool/version compatibility;
- version with Skill;
- validate periodically;
- do not treat one successful trajectory as universally correct.

Possible structure:

```text
examples/
  successful-migration.yaml
  failure-recovery.yaml
```

Use examples as evidence and teaching aids, not authority.

---

# 13. Third-party Skill provenance

For every imported Skill preserve:

```text
source repository/package
source revision/tag/commit
content hash
import date
license if relevant
publisher/author metadata
requested capabilities
network requirements
script presence
review result
behavioral eval result
approval identity/date
```

Trust classes might be:

```text
T0 BUNDLED_REVIEWED
T1 PINNED_THIRD_PARTY_APPROVED
T2 ADVISORY_TEXT_ONLY
T3 QUARANTINED_UNTRUSTED
```

Names are provisional; semantics matter more.

---

# 14. Supply-chain rules

- no automatic execution of newly discovered scripts;
- no auto-update without revalidation;
- pin versions/hashes for approved external Skills;
- external references remain untrusted content;
- Skill text cannot override AGENTS/policy/operator requirements;
- requested capability expansion requires explicit review;
- executable resources receive stronger scrutiny than prose-only Skills;
- remote content fetched at runtime should be treated as untrusted task context unless specifically approved.

---

# 15. Failure modes

## 15.1 Skill description routes too broadly

Symptom: irrelevant tasks activate Skill.

Response:

- mark routing defect;
- preserve false-positive eval case;
- revise description/routing metadata;
- do not compensate with opaque prompt hacks.

## 15.2 Skill conflicts with current policy

Policy wins. Record mismatch; quarantine/revise Skill if conflict is structural.

## 15.3 Skill update changes required capabilities

New version requires review. Existing approved hash remains pinned until superseded.

## 15.4 Skill script fails

Treat as tool/script failure, not agent reasoning failure. Preserve operation evidence and failure class.

## 15.5 Skill references stale docs

Hashes/version metadata should make drift visible. Depending on importance, warn, invalidate, or require revalidation.

## 15.6 Multiple Skills apply

Allow composition only when their roles are compatible and ordering/interaction is defined. Otherwise surface ambiguity.

---

# 16. Security requirements

- Skill text is not authority;
- scripts run through normal capability/policy/hook controls;
- Skills cannot request secret values in durable task text;
- third-party executable content quarantined by default;
- tool/capability requests declared before activation where possible;
- Skill output does not become persistent guidance automatically;
- imported examples/reference content treated as untrusted information;
- privilege escalation hidden in procedure text must be denied mechanically.

---

# 17. Testing strategy

## 17.1 Format/parser tests

- valid/invalid `SKILL.md`;
- metadata parsing;
- optional resources;
- duplicate IDs;
- version/hash calculation.

## 17.2 Routing tests

Frozen positive/negative/paraphrase/hard-negative corpus.

## 17.3 Progressive-loading tests

Verify unrelated Skill bodies/resources never enter context.

## 17.4 Security tests

Malicious Skills:

- claims to override policy;
- asks for root filesystem;
- hides destructive shell script;
- requires undeclared network access;
- poisons references;
- misleading routing description;
- attempts to exfiltrate credentials.

## 17.5 Compatibility tests

Verify standard-compatible Skills work without MAPS-specific metadata.

## 17.6 Outcome tests

Compare tasks with/without Skill:

- quality;
- rework;
- operator intervention;
- context cost;
- tool errors;
- escaped defects.

---

# 18. Metrics

Useful:

- Skill routing precision/recall;
- false activation rate;
- no-skill abstention accuracy;
- average Skill context tokens loaded;
- outcome delta versus baseline;
- rework/operator-intervention delta;
- stale/superseded Skill activation attempts blocked;
- third-party Skill quarantine/rejection reasons;
- percentage of active Skills with current eval/provenance.

Avoid:

- total number of Skills;
- number of Skill activations;
- community catalog size.

More Skills is not inherently better.

---

# 19. Implementation phases

## S1 — Information classification

Document/map authority vs facts vs Skills vs flows vs tools vs examples.

Exit gate: Context Builder/review guidance can name these categories consistently.

## S2 — Skills format support

Implement discovery/parsing of standard `SKILL.md` directories.

Exit gate: bundled Skills load with progressive disclosure and no new authority.

## S3 — Catalog + provenance

Add derived catalog and hash/provenance records.

Exit gate: every active Skill has stable identity/version/source/trust state.

## S4 — Routing evaluation

Build frozen Skill-selection corpus and baseline routing logic.

Exit gate: acceptable precision/recall/hard-negative performance defined and measured.

## S5 — Quality/security gate

Metadata/resource lint + quarantine lifecycle + adversarial tests.

Exit gate: malicious/unsafe example Skills are caught or mechanically constrained.

## S6 — Context Builder integration

Load selected Skills progressively with selection reasons and trust labels.

Exit gate: unrelated Skills demonstrably stay out of context.

## S7 — Capability Packs experiment

Only after Skills + Harness API + EnvironmentSpec are stable.

Exit gate: one or two real domains show value without becoming hidden authority bundles.

---

# 20. Concrete task backlog

1. Define MAPS information classes.
2. Define Skill directory discovery rules.
3. Implement standard metadata parser.
4. Implement stable Skill hash/version identity.
5. Create two bundled pilot Skills.
6. Implement progressive Skill loading.
7. Add derived Skill catalog.
8. Add provenance/trust metadata storage/projection.
9. Create Skill metadata lint.
10. Create Skill instruction/resource lint.
11. Build Skill-selection frozen eval corpus.
12. Add hard-negative/paraphrase routing tests.
13. Integrate Skill selection into Context Builder.
14. Add explicit activation reason to context plan.
15. Build third-party quarantine workflow.
16. Add malicious Skill adversarial suite.
17. Define optional exemplar format.
18. Evaluate exemplar usefulness on one hard procedure.
19. Prototype one Capability Pack after Harness/Environment prerequisites.
20. Add Skill outcome comparison to Learning/Eval roadmap.

---

# 21. Definition of done

Procedural Knowledge & Skills v1 is done when:

- MAPS can use open-format Skills as reusable procedures;
- `AGENTS.md` remains focused on always-active invariants rather than becoming a procedure encyclopedia;
- Skills load progressively and unrelated resources stay out of context;
- every active Skill has stable identity, version/hash, provenance, and trust state;
- routing is measured on positive/paraphrase/hard-negative/no-skill cases;
- third-party executable resources are quarantined/reviewed;
- Skills cannot override canonical policy or grant capabilities;
- Skill changes require explicit version/revalidation rather than silent behavior drift;
- outcome data can later tell us whether a Skill actually helps.
