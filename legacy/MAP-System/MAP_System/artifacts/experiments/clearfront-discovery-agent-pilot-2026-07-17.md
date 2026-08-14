# ClearFront Discovery Agent Pilot — Independent Output

## Findings

```yaml
- title: Align the guaranteed one-cost opening hand with the governing rules
  classification: risk_or_contradiction
  trigger:
    - purpose_and_lifecycle
    - contradiction
    - assumption
  problem: The shipped game guarantees each player at least one one-cost card in the opening hand, and the in-app Rules modal promises that guarantee, but the governing playtest rules specify only a three-card opening hand. This is a real randomness and balance rule that currently bypasses the documented rules-decision path.
  user_impact: Players learn and plan around a consistency guarantee that is not present in the canonical rules; future balance work could unknowingly preserve, remove, or double-compensate for it.
  proposed_response: Ask the product owner whether the guarantee is intentional. If yes, add it to the governing rules through the SCOPE/design-review path; if no, remove the in-app claim and separately decide whether implementation should change. Add a deterministic opening-hand assertion only after that disposition.
  minimal_version: Record one explicit retain-or-remove decision and make the governing rules, in-app Rules modal, and one focused test agree.
  alternatives:
    - Document the behavior as a temporary prototype parameter pending playtest.
    - Remove only the in-app promise until a balance decision is made, while explicitly tracking the implementation behavior as provisional.
  evidence:
    - "Observed: Projects/ClearFront/app/js/state.js:249-260 searches the shuffled deck for a cost-1 card and moves it into the opening hand before drawing the remainder."
    - "Observed: Projects/ClearFront/app/index.html:196 states, 'Your opening hand always includes at least one 1-cost card.'"
    - "Observed: Projects/ClearFront/source/game-card-combat-effects/clearfront_rules.md sections 3 and 5 specify a three-card start but no cost guarantee."
    - "Observed: Projects/ClearFront/artifacts/research/rules-conformance-audit.md section 3 calls the starting-game behavior MATCHES but does not disposition this extra rule."
    - "Inference: Because the guarantee changes draw variance and first-turn playability, it is a balance/rules behavior rather than presentation copy."
  confidence: high
  scores:
    user_value: 4
    goal_alignment: 5
    necessity: 4
    novelty: 4
    leverage: 4
    confidence: 5
    reversibility: 5
    complexity: 1
    maintenance_burden: 1
    scope_risk: 3
  recommendation: ask_user
  reasoning_summary: This is a small, directly evidenced three-way contract mismatch. Resolving it before content or balance work prevents the canonical rules, player-facing rules, and test oracle from drifting further.

- title: Establish keyboard and assistive-technology operability at the central card-rendering seam
  classification: likely_requirement
  trigger:
    - omission
    - emergence
    - analogy
    - effortless_skill
  problem: Core game actions are attached as click handlers to dynamically rendered article elements, while overlays lack dialog semantics and focus handling. Mouse and touch paths are developed and tested, but no keyboard or assistive-technology path is represented in the current requirements or test evidence.
  user_impact: A player who cannot reliably use pointer or touch input may be unable to choose a Champion, play a card, select attackers or blockers, inspect card details, or navigate/close modal screens.
  proposed_response: First run a focused accessibility baseline over the complete match lifecycle. Then use the centralized createCardElement/render paths to give actionable cards semantic controls, keyboard activation, meaningful accessible names and state, visible focus, and modal focus management. Add a small keyboard lifecycle smoke test rather than a broad new framework.
  minimal_version: Prove Champion selection, one card play, attacker selection, blocker assignment, modal open/close, and New Game are keyboard-operable with visible focus; mark overlays as dialogs and restore focus on close.
  alternatives:
    - Add a documented keyboard control mode using existing buttons and roving focus.
    - If full card-grid navigation is deferred, publish the limitation and first make deck selection, rules, restart, and modal closure keyboard-correct.
  evidence:
    - "Observed: Projects/ClearFront/app/js/render.js:430-468 creates cards as article elements; actionable cards receive a CSS class but no tabindex, button role, accessible pressed/disabled state, or keyboard listener."
    - "Observed: Projects/ClearFront/app/js/render.js:342,396,424 attaches core Champion, unit, and hand actions only through click listeners."
    - "Observed: Projects/ClearFront/app/index.html:178-260 defines the deck chooser and six modal overlays without role=dialog, aria-modal, labelled-by relationships, or focus-management metadata."
    - "Observed: Projects/ClearFront/app/js/input.js covers mouse hover and touch-hold inspection; repository searches find no keydown path for equivalent card inspection or activation."
    - "Inference: TASK-212 through TASK-216 centralized rendering/input behavior, making this substantially cheaper and less duplicative now than in the original monolith."
    - "Proposal: Treat this as a user-access requirement candidate, not a new game mechanic or mandatory rules change."
  confidence: high
  scores:
    user_value: 5
    goal_alignment: 4
    necessity: 4
    novelty: 3
    leverage: 5
    confidence: 5
    reversibility: 5
    complexity: 3
    maintenance_burden: 2
    scope_risk: 2
  recommendation: investigate
  reasoning_summary: Accessibility is absent from both the lifecycle and verification story, yet the completed decomposition created a small number of leverage points where semantic interaction can be added and tested without altering game rules.

- title: Do not add automatic match save-and-resume in the current prototype phase
  classification: rejected_idea
  trigger:
    - purpose_and_lifecycle
    - analogy
    - divergence
  problem: Browser games often preserve interrupted sessions, so local persistence initially appears to fill a lifecycle-recovery gap.
  user_impact: Save-and-resume could protect a long match from an accidental refresh, but it would also preserve hidden hands, deck order, AI state, undo state, and pending asynchronous combat/UI phases whose restoration contract is currently undefined.
  proposed_response: Reject automatic persistence for now. Reconsider only if observed match length or user testing shows refresh/interruption loss is a recurring problem, and then begin with an explicit safe-state snapshot boundary rather than arbitrary live-state serialization.
  minimal_version: No implementation. If evidence emerges, time matches and record interruption complaints before designing persistence.
  alternatives:
    - Provide the existing New/Play again recovery path only.
    - Later support restartable deterministic match seeds for testing, not player-visible resume.
  evidence:
    - "Observed: Projects/ClearFront/app/js/state.js:114-143 initializes a match with hidden deck/hand data and transient target/combat state."
    - "Observed: Projects/ClearFront/app/index.html:371-372 and the game-over overlay provide explicit New and Play again closure/recovery paths."
    - "Observed: Projects/ClearFront/shared/project-brief.md defines a local static prototype and does not identify persistence as a current objective."
    - "Inference: Arbitrary restoration would add state-versioning and hidden-information correctness burden disproportionate to demonstrated user value."
  confidence: medium
  scores:
    user_value: 2
    goal_alignment: 2
    necessity: 1
    novelty: 2
    leverage: 2
    confidence: 3
    reversibility: 3
    complexity: 5
    maintenance_burden: 5
    scope_risk: 4
  recommendation: reject
  reasoning_summary: The analogy is common but the need is unproven, while safe restoration crosses hidden-information and transient-phase boundaries. The current explicit restart path is proportionate to this prototype.

- title: Do not add new factions or mechanics merely to complete the design document's catalog
  classification: rejected_idea
  trigger:
    - contradiction
    - divergence
    - non_forcing
  problem: The rules name Equipment, Mind, Forge, Neutral, Rush, Drain, and Stun behaviors that are absent or narrower in the implementation, which can invite a feature-completion batch before the product owner decides whether code or rules are authoritative.
  user_impact: Premature completion would increase card, UI, balance, and tracking complexity and could harden provisional rules without evidence that they improve the current four-faction prototype.
  proposed_response: Reject feature generation as a discovery recommendation. Preserve the already-recorded conformance disposition question and require one decision at a time, with the design checklist and playtest evidence, before implementation.
  minimal_version: No new mechanic or content task from this pilot; route only the existing implementation-versus-spec decision to the owner.
  alternatives:
    - Revise the playtest rules to label unshipped systems as future scope.
    - Select one existing deviation for a bounded playtest after the general disposition is made.
  evidence:
    - "Observed: Projects/ClearFront/artifacts/research/rules-conformance-audit.md prioritized follow-up 1 already records the missing-system scope decision."
    - "Observed: Projects/ClearFront/artifacts/reviews/clearfront-independent-delivery-audit-2026-07-17.md P0 already routes implementation-versus-spec disposition before content work."
    - "Observed: Projects/ClearFront/source/game-card-combat-effects/clearfront_design_principles.md sections 3-5 require mechanics to earn their place and prefer consolidation over novelty."
    - "Inference: Recommending any particular missing faction/mechanic here would duplicate known work and violate the pilot's non-forcing purpose."
  confidence: high
  scores:
    user_value: 1
    goal_alignment: 2
    necessity: 1
    novelty: 1
    leverage: 1
    confidence: 5
    reversibility: 2
    complexity: 5
    maintenance_burden: 5
    scope_risk: 5
  recommendation: reject
  reasoning_summary: The gap is real but already known, and no evidence selects implementation over rules revision or one missing system over another. Generating features now would be duplication and scope drift.
```

## Pass coverage and method note

All seven passes were performed independently against the completed ClearFront phase: the end-to-end player lifecycle and recovery paths; omission categories including input, navigation, accessibility, testing, security/privacy, and onboarding; opportunities created by the decomposition; analogous card-game and browser-app problems; rule/design/implementation contradictions; conservative, high-leverage, cross-domain, and unusual-but-plausible divergence; and explicit evaluation on all ten required dimensions. I absorbed the governing rules/design, current app architecture, TASK-207–220 records and evidence, independent audit, decisions/current state, existing ClearFront E/I, and Sentinel pilot before curation. I did not read the frozen known-findings adjudication artifact. Two proposals survived; two tempting ideas were retained as rejected ideas for future deduplication. No implementation, task, decision, policy, E/I, or promotion files were changed.
