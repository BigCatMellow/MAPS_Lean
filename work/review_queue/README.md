# MAPS Review Queue

Purpose: keep completed implementation tranches easy to review later without
blocking unrelated forward work.

This folder is a **review staging area**, not task authority and not canonical
runtime state. Each packet should point to the exact branch/commit/PR and state:

- what changed;
- what was intentionally not changed;
- acceptance criteria;
- verification actually run;
- known gaps or deferred work;
- the files/surfaces a reviewer should inspect.

Suggested packet status:

```text
QUEUED → IN_REVIEW → CHANGES_REQUESTED | APPROVED
```

Do not copy source files here. Review the referenced revision so the packet
cannot drift into a second source of truth.
