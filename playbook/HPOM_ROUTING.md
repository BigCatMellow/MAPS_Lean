# Human-Paced Orchestration (HPOM)

HPOM is useful without MAP’s runtime: assign work to the cheapest competent
worker while keeping authority with the accountable owner.

"Competent" means competent for the whole execution envelope: reasoning,
instruction following, required context, tools, verification, and boundaries.
Use [Model Capability Routing](MODEL_CAPABILITY_ROUTING.md) when worker choice is
not obvious.

## Route in this order

1. Is the intent clear enough for observable acceptance criteria? If not, shape
   it before execution.
2. What capability does the work actually require: planning/integration,
   bounded implementation, investigation, review, or mechanical execution?
3. Does it require human preference, final judgment, architecture, security,
   or an irreversible decision? Keep that decision with the operator or
   accountable core agent.
4. What context, tools, structured output, and verification must the worker use
   reliably? Exclude workers that have not demonstrated competence for those
   requirements.
5. Is there a bounded scan, draft, classification, checklist, or edit that a
   cheaper helper can complete without changing project truth?
6. Is the coordination cost lower than the benefit of delegation or parallel
   work?
7. Are inputs, outputs, stop condition, and integration owner explicit enough
   for the selected worker? Increase instruction detail for narrower workers;
   route upward rather than writing an infinitely long prompt for an unsuitable
   worker.

## Authority stays separate from capability

| Role | Good use | Cannot do alone |
| --- | --- | --- |
| Operator | intent, priority, consequential approval | routine execution by default |
| Accountable core agent | integration, implementation, substantive review | self-approve its own work |
| Spawned helper | bounded research, inspection, alternate draft, checklist | take ownership or silently expand scope |
| Local/draft model | summarization, classification, suggestions, proven bounded edits | make final claims or consequential decisions without the required authority/review |

A local model may qualify for stronger work when the exact
`model + harness + runtime + tools` combination has been tested and proven
reliable. Locality is a deployment fact, not a permanent capability class.

Record any consequential delegation in the task or handoff: worker, scope,
inputs, output, stop condition, verification, and integration owner.

For instruction quality, use [Agent-Grade Instructions](AGENT_GRADE_INSTRUCTIONS.md).
For provider-specific setup and workflow notes, use
[Provider and Tool Guidance](PROVIDER_AND_TOOL_GUIDANCE.md).
