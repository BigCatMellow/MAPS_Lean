# Risk and Change Control

Before a medium- or high-risk change, name the risk class, severity, owner,
mitigation, evidence, and rollback path. Common classes include security, data,
availability, external side effects, privacy, and architecture.

Use [the risk-register template](../templates/risk-register.md) to establish
the initial register during project bootstrap or before a consequential change.

## Change path

```text
scope → implement → evidence → independent review → proportional release note → observe
```

- Low-risk, reversible work: owner verification is enough.
- Medium-risk work: relevant automated or manual evidence and independent
  review.
- High-risk work: explicit acceptance criteria, reproduced reviewer evidence,
  operator-visible summary, and rollback plan before release.

At completion, ask one small learning question: did this expose an insight,
assumption, recurring failure, or improvement worth capturing? “No” is valid;
silently forgetting is not.
