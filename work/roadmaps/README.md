# MAPS roadmaps

Status: `PLANNING INDEX — NOT ACTIVE AUTHORITY`

Use this page as the **roadmap router**. Do not open every roadmap to discover
which one matters.

## Route by question

| Question | Open | Do not use it for |
| --- | --- | --- |
| How do capability areas fit/depend on each other? | [MASTER capability roadmap](00-MASTER-MAPS-CAPABILITY-ROADMAP.md) | live PR/task state |
| What capability evidence/status was last reconciled? | [Capability checklist](CAPABILITY_CHECKLIST.md) | permission or live truth; re-verify current code/tests/CI |
| What did Prime-derived lifecycle/harness work contribute? | [Prime Agent roadmap](prime-agent-capability-roadmap.md) | current queue/status |
| How should operator requests compile into bounded work? | [Operator Intent Compiler](operator-intent-compiler.md) | global authority |
| What is the detailed harness/security/environment/learning plan? | [Agent-harness roadmap set](agent-harness-capabilities/README.md) | current implementation status without verification |
| What PR/CI/review work is live now? | [Coordination entry](../coordination/README.md) → live GitHub | any roadmap snapshot |

These are large planning artifacts. Once you know the relevant question, read the
matching section/file only. Do not absorb the full roadmap corpus as context.

## Planning hierarchy

```text
this router
  ↓
MASTER roadmap                = cross-capability architecture/dependencies
  ↓
detailed capability roadmaps = subsystem design

CAPABILITY_CHECKLIST          = dated evidence/status overlay
live GitHub + code/tests      = current facts
```

Roadmaps plan work; they do not create authority. [`AGENTS.md`](../../AGENTS.md),
the approved project/task permission envelope, canonical runtime/task state,
merged code/tests, and explicit operator decisions remain stronger.

## Supporting evidence

Open only when a roadmap/task links them for a concrete reason:

- [`work/research/`](../research/)
- [`work/context/`](../context/)
- [`migration/LEGACY_IDEA_RECOVERY_AUDIT.md`](../../migration/LEGACY_IDEA_RECOVERY_AUDIT.md)
- [`migration/FUTURE_IDEAS_BACKLOG.md`](../../migration/FUTURE_IDEAS_BACKLOG.md)

Historical dated reconciliation/dispatch files in this directory are evidence,
not a required onboarding sequence. Live state wins when they disagree.
