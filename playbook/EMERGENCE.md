# Emergence and Improvement (E/I)

Discovery is valuable, but it must not hijack an assigned task.

```text
observe → connect → synthesize → name → test → promote
```

- **Insight:** a notable observation.
- **Synthesis:** a meaningful connection between observations.
- **Idea:** a bounded possible improvement.
- **Experiment:** a safe test.
- **Promotion:** a deliberate decision to make it a task, decision, or project.

Rule: notice freely, act carefully, promote deliberately.

Capture a concise record in `work/` or project-specific `insights/`, `ideas/`,
and `experiments/` folders. Include:

- the observation;
- source/context as a direct relative Markdown link when the source is in the
  repository;
- related insight/synthesis/idea/experiment/task/decision links that give the
  record meaning;
- potential value;
- the smallest next test;
- current disposition when known: `ACTIVE | TEST | WATCH | DEFERRED | BLOCKED |
  RESOLVED | REJECTED | SUPERSEDED`.

Only an approved/promoted item can expand implementation scope.

When later work changes the record's disposition, **do not rewrite the original
observation as though the future was known at capture time**. Add a short
forward link instead, for example:

```text
Insight → related synthesis / idea
Idea → tested by experiment
Experiment → informs decision
Idea → promoted to task
Task / PR → implements idea
Old record → superseded or resolved by newer record
```

A promoted idea must not remain permanently labeled only `Not promoted` after
later work adopts it. A rejected or superseded idea should preserve the reason
and link to the decision/replacement so future agents do not rediscover it as
new.

Prefer links over copied explanation. Reverse backlinks may be derived by
simple tooling; do not create duplicate mutable truth just to make a graph look
complete.

