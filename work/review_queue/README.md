# MAPS Review Queue

Purpose: keep completed implementation tranches easy to review later without
blocking unrelated forward work.

This folder is a **review staging area**, not task authority and not canonical
runtime state. Each packet points to the exact PR/task/surfaces and records:

- what changed;
- what was intentionally not changed;
- acceptance criteria / intended behavior;
- verification actually run;
- known gaps or deferred work;
- the files/surfaces a reviewer should inspect.

Do not copy source files here. Review the referenced revision so the packet
cannot drift into a second source of truth.

## Queued packets

| Packet | Status | Validation |
|---|---|---|
| [Priority observability and operating safeguards](priority-observability.md) | `QUEUED` | Runtime stack run `31886183653` passed |
| [Outcome feedback](outcome-feedback.md) | `QUEUED` | Runtime stack run `31886288275` passed |
| [Context Builder v1](context-builder-v1.md) | `QUEUED` | Runtime stack run `31886431884` passed |
| [Status surface v1](status-surface-v1.md) | `QUEUED` | Runtime stack run `31886549262` passed |
| [Pull-request CI validation](pr-ci-validation.md) | `QUEUED` | Enabled the successful PR runs above |

Suggested packet lifecycle:

```text
QUEUED → IN_REVIEW → CHANGES_REQUESTED | APPROVED
```

## Review order

A practical order is:

1. pull-request CI validation;
2. priority observability / operating safeguards;
3. outcome feedback;
4. Context Builder v1;
5. status surface v1.

The ordering is for review convenience only. It does not create task dependency
or implementation authority.
