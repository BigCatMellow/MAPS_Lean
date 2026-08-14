In my map system, do I need to have MD files explaining how each agent could act like pretend you're a programmer pretend you're a front-end developer? Or is it fair to assume that it would be able to figure that out on its own. I've seen people use those kind of things for similar projects and they define like I guess roles and those files
Worked for 26s
The practical answer

Do not create role files merely saying, “Pretend you are a programmer” or “Act as a front-end developer.” A capable coding model already understands the general knowledge associated with those professions.

However, you should create Markdown files defining what those roles mean inside the MAP system.

The important distinction is:

The model knows what a front-end developer is. It does not know what your front-end agent is responsible for.

What the agent can usually infer

Without a role file, an agent can generally infer that a front-end developer should:

Build user interfaces.
Work with HTML, CSS, JavaScript, React, or similar tools.
Consider accessibility and responsive layouts.
Connect the interface to back-end services.
Test visible behavior.

You do not need to teach it those basics unless you want a particular method.

What must be explicitly defined

Your role files should establish the agent’s operating contract, including:

Mission — what result it owns.
Authority — what it may change without approval.
Boundaries — what belongs to another agent.
Inputs — what information it expects to receive.
Outputs — what it must produce when finished.
Quality requirements — tests, accessibility, documentation, error handling, and so forth.
Handoffs — when and how it reports work to another agent.
Escalation rules — what it should do when blocked or uncertain.

That is much more useful than assigning a fictional persona.

Weak role file
# Front-End Developer

You are an expert front-end developer.
Write clean, modern code.
Use best practices.

This adds very little. The instructions are broad, subjective, and mostly restate abilities the model already has.

Useful MAP role file
# Front-End Implementation Agent

## Mission

Implement approved interface specifications as working, tested components.

## Responsibilities

- Build interface components from the assigned specification.
- Reuse existing project components before creating new ones.
- Preserve established visual and interaction conventions.
- Handle loading, empty, error, and success states.
- Test keyboard navigation and responsive behavior.
- Report missing API requirements to the manager.

## Boundaries

- Do not change product requirements.
- Do not redesign approved interfaces without reporting the concern.
- Do not change back-end data structures directly.
- Do not introduce a new framework or dependency without approval.

## Required completion report

- Files changed
- Behavior implemented
- Tests performed
- Known limitations
- Assumptions made
- Follow-up work required

This tells the agent how it fits into your organization, not how to impersonate a profession.

Recommended MAP structure

I would use four levels of instruction:

MAP/
├── AGENTS.md
├── standards/
│   ├── coding-standards.md
│   ├── definition-of-done.md
│   └── reporting-standard.md
├── roles/
│   ├── manager.md
│   ├── implementation-agent.md
│   ├── research-agent.md
│   ├── review-agent.md
│   ├── triage-agent.md
│   └── emergence-agent.md
└── skills/
    ├── frontend-implementation.md
    ├── debugging.md
    ├── code-review.md
    ├── repository-research.md
    └── test-writing.md
AGENTS.md

Contains rules that apply to every agent:

How assignments are received.
How agents document assumptions.
How agents report blockers.
How agents avoid duplicating work.
How changes are validated.
How work is handed back to management.
roles/

Defines organizational responsibility:

Manager
Researcher
Implementer
Reviewer
Triage agent
Emergence and innovation agent
skills/

Defines reusable methods for particular kinds of work:

Building a front end.
Debugging a failure.
Performing research.
Reviewing security.
Writing tests.

This lets a single implementation agent load the appropriate skill instead of requiring separate permanent identities for “React developer,” “Python developer,” “database developer,” and every other specialty.

The manager should supply the immediate task

The role file should remain relatively stable. The manager should provide the changing information:

## Assignment

Create the settings screen described in `specs/settings-screen.md`.

## Relevant context

- Framework: React
- Existing components: `src/components/ui/`
- API contract: `docs/settings-api.md`

## Constraints

- Do not add dependencies.
- Preserve the existing desktop layout.
- Mobile width must work at 360 pixels.

## Acceptance criteria

- Settings load from the API.
- Changes can be saved.
- API errors are visible.
- Keyboard navigation works.
- Existing tests continue to pass.

The effective agent context becomes:

Global MAP rules
+ assigned organizational role
+ relevant technical skill
+ immediate task packet
+ project files

Current coding-agent systems follow a similar layered approach: repository-wide instructions handle general project rules, path-specific instructions handle local concerns, and specialized agent or skill files are loaded for particular workflows. GitHub explicitly recommends keeping always-on instructions broadly applicable rather than overloading them with narrowly relevant material.

My recommendation for MAP

Create role files, but do not write them as elaborate character descriptions.

Use this rule:

Describe the job only where the job differs from common knowledge. Spend most of the file defining responsibility, authority, process, boundaries, and evidence of completion.

For your system, you likely need approximately six to ten stable organizational roles, not dozens of pretend professions. Programming specialties should usually be selectable skills or task playbooks, while manager, researcher, reviewer, triage, and emergence roles deserve distinct operating contracts.

Friday 7:05 PM
ant_colony.txt
Document
here is the conversation i had with gemini about the idea of the MAP system
Recommended MAP team with detailed responsibilities

The system should use functional seats, not permanent agents that remain active. A model occupies a seat for one task or stage, produces an artifact, and exits.

You
└── Project DRI — Claude Sonnet
    ├── Scout — Claude Haiku or Ollama
    ├── Implementer — Codex
    ├── Precision Editor — Aider
    └── Independent Reviewer — fresh Claude Sonnet
         └── Escalation — Claude Opus
1. Human Owner — You

You remain above MAP. No agent should silently assume your authority.

Responsibilities
State the desired outcome.
Approve major changes in scope or direction.
Resolve subjective product decisions.
Approve irreversible or high-risk operations.
Decide when two technically valid approaches reflect different preferences.
Override MAP’s recommendation when necessary.
Decisions reserved for you
Major redesigns
New paid services or dependencies
Destructive database operations
Publishing or releasing software
Handling credentials
Substantial privacy or security tradeoffs
Abandoning or changing the project’s original purpose
What you should normally receive

Agents should not dump technical chatter on you. They should present:

decision_needed: true
question: Should conflicts automatically use load order or require user confirmation?

options:
  - name: Load-order default
    benefit: Faster automatic merging
    risk: May silently choose an unwanted file

  - name: User confirmation
    benefit: Safer and more transparent
    risk: More interruptions

recommendation: User confirmation
reason: Conflict intent cannot be determined reliably from file order alone.
2. Project DRI — Claude Sonnet

DRI means Directly Responsible Individual. This agent owns understanding the request and turning it into valid work. It does not necessarily perform the work itself.

This is your normal MAP leader.

Core mission

Convert your request into a coherent, correctly scoped, verifiable plan.

Responsibilities
Understand the request
Determine what you are actually trying to accomplish.
Identify ambiguities, assumptions, and missing requirements.
Distinguish requested work from optional improvements.
Preserve the user-facing purpose of the project.
Understand the project
Read relevant project instructions.
Inspect the repository structure.
Locate applicable architecture decisions.
Identify dependencies and affected systems.
Ask a Scout for evidence when broad repository exploration is needed.
Shape tasks
Break work into appropriately sized tasks.
Determine which tasks depend on others.
Define writable and readable scopes.
Select the required skills.
Write measurable acceptance criteria.
Assign an appropriate implementation method.
Decide whether parallel execution is safe.
Coordinate work
Submit ready tasks to the queue.
Interpret escalations from Codex.
Revise bad or incomplete task packets.
Prevent duplicate or conflicting work.
Coordinate integration between completed tasks.
Preserve project direction
Compare implementation results with the original goal.
Detect when technically valid work has drifted from the desired product.
Maintain the project-level roadmap and active priorities.
Sonnet should produce

For a normal feature:

task_id: TASK-204
title: Detect file conflicts between selected Torchlight II mods

objective:
  Identify destination paths supplied by more than one selected mod before
  creating the merged package.

non_goals:
  - Do not automatically resolve conflicts.
  - Do not redesign the mod-selection interface.
  - Do not alter source mod archives.

dependencies:
  - Existing archive-reader service
  - Existing normalized-path utility

scope:
  writable:
    - src/conflicts/**
    - tests/conflicts/**
  readable:
    - src/archive/**
    - src/merge/**
    - docs/architecture/**

acceptance_criteria:
  - Conflicting destination paths are detected.
  - Path comparisons follow Windows case-insensitivity.
  - Identical duplicates are distinguished from differing files.
  - Existing nonconflicting merges still pass.
  - Results include the contributing mod names.

required_evidence:
  - Code diff
  - Unit-test results
  - Integration-test results
  - Assumptions and limitations

risk: medium
implementer: codex
reviewer: independent-assurance
Sonnet should not
Perform every task merely because it can.
Approve its own implementation.
Rewrite large areas without a task packet.
Create unnecessary tasks to imitate a large organization.
keep reading implementation logs while Codex works.
Substitute vague instructions like “use best practices” for acceptance criteria.
Turn every minor change into a formal multi-agent workflow.
When Sonnet should work directly

Sonnet may implement rather than delegate when:

The task is mostly architectural reasoning.
The code change is inseparable from the design reasoning.
Codex has repeatedly misunderstood the issue.
The change is small but unusually ambiguous.
The task concerns MAP’s own governance or role definitions.
The cost of explaining the task exceeds the cost of completing it.
3. Scout — Claude Haiku or Ollama

The Scout is a read-only investigator. It gathers evidence but does not decide project direction.

Core mission

Find and compress the information another agent needs without changing the project.

Responsibilities
Map unfamiliar repositories.
Locate entry points, symbols, tests, and dependencies.
Find all uses of an interface or function.
Summarize large files or logs.
Trace a request through several modules.
Identify likely relevant architecture documents.
Compare current behavior with documented expectations.
Produce evidence with file and symbol references.
Create compact task fingerprints after work is completed.
Example assignment
investigation: Trace how mod load order currently affects merged output

questions:
  - Where is load order stored?
  - Where is archive iteration ordered?
  - Which function decides the winning file?
  - What tests currently cover ordering?

write_access: none

output:
  - Relevant files and symbols
  - Current behavior
  - Existing test coverage
  - Uncertainties
Expected output
finding:
  load_order_source:
    file: src/project/selectedMods.ts
    symbol: SelectedMod.position

  merge_order:
    file: src/merge/buildMergePlan.ts
    symbol: buildMergePlan
    behavior: Iterates selectedMods in ascending position order.

  conflict_behavior:
    file: src/merge/writeMergedFiles.ts
    symbol: writeMergedFiles
    behavior: Later files overwrite earlier files without recording the conflict.

tests:
  - tests/merge/loadOrder.test.ts

uncertainties:
  - No test covers paths differing only by capitalization.
Haiku versus Ollama
Claude Haiku

Prefer Haiku when:

Repository understanding must be reliable.
The investigation spans many modules.
Results are being used to shape an important task.
Fast API-based analysis is acceptable.
Ollama

Prefer a local model when:

Privacy or local processing matters.
The task is classification, extraction, or summarization.
Mistakes are easy for another agent to verify.
You are benchmarking local models.
The task does not justify API usage.
Scout restrictions

The Scout should not:

Write code.
Decide the final architecture.
Mark tasks complete.
Create implementation requirements from guesses.
Condense uncertainty into false certainty.
recommend major changes without showing evidence.
4. Primary Implementer — Codex

Codex is the normal code-producing executor.

Core mission

Implement one approved task within its scope and submit verifiable evidence.

Responsibilities
Before editing
Read the task packet.
Confirm the base repository revision.
Inspect relevant project instructions and skills.
Read the necessary code and tests.
Detect contradictions or insufficient context.
Escalate before making unsupported architectural assumptions.
During implementation
Work only in the assigned branch or worktree.
Keep changes focused on the objective.
Follow existing project patterns.
Add or update tests.
Avoid unrelated cleanup.
Record significant implementation decisions.
Run incremental checks while working.
Before submission
Run every required verification command.
Confirm expected artifacts exist.
Review its own diff for accidental changes.
Check that no forbidden files were modified.
Report assumptions and known limitations.
Submit work for review rather than calling it approved.
Codex input
MAP Constitution
+ Delivery Implementer role
+ applicable project instructions
+ selected skills
+ immutable task packet
+ relevant source context
+ prior failed-attempt summary, when applicable
Codex output
task_id: TASK-204
status: submitted
base_commit: 8c20f9d
result_commit: db17e65

changed_files:
  - src/conflicts/buildConflictIndex.ts
  - src/conflicts/types.ts
  - tests/conflicts/buildConflictIndex.test.ts

implementation_summary:
  Added normalized-path indexing and separate classifications for identical
  duplicates and differing-file conflicts.

verification:
  - command: npm run typecheck
    exit_code: 0
  - command: npm test -- tests/conflicts/buildConflictIndex.test.ts
    exit_code: 0
  - command: npm test
    exit_code: 0

assumptions:
  - Windows-style case-insensitive path handling is required on every platform.

known_limitations:
  - Content equality currently uses complete-file hashing.

artifacts:
  diff: artifacts/TASK-204.diff
  test_log: artifacts/TASK-204-tests.log
Codex may decide
How to structure local implementation details.
Which existing helper functions to reuse.
How to name private functions.
Which tests are needed to demonstrate acceptance.
How to fix local defects discovered within scope.
Codex must escalate
It needs to modify a file outside the writable scope.
Acceptance criteria contradict one another.
A dependency is missing.
The existing architecture cannot support the request.
A new dependency appears necessary.
A public interface must change.
Tests reveal an unrelated existing defect.
Repeated implementation attempts fail.
The task would cause data-loss or security risk.
Codex should not
Redefine the requirement.
Expand scope because it sees an opportunity.
perform broad refactoring without approval.
Approve or merge its own work.
Hide failed tests.
Modify MAP’s state records directly outside the runtime protocol.
Continue indefinitely after repeated failures.
5. Independent Reviewer — fresh Claude Sonnet session

This is logically separate from the Project DRI, even when it uses the same model.

The important separation is:

Fresh context
Different role instructions
Read-only access
Original requirements
No inherited commitment to Codex’s solution
Core mission

Attempt to prove that submitted work does not satisfy the requirement.

The reviewer is not there to praise the implementation or explain what it does. It is there to find material failures.

Responsibilities
Requirement review
Compare the implementation against the original objective.
Check every acceptance criterion.
Ensure non-goals were respected.
Detect technically correct but product-wrong behavior.
Code review
Inspect changed code.
Inspect connected code outside the diff.
Check architecture compatibility.
Detect hidden edge cases.
Look for unnecessary complexity.
Evaluate error handling and maintainability.
Evidence review
Verify that test commands actually ran.
Check that tests meaningfully cover the requirement.
Re-run tests when allowed.
Distinguish implementer claims from verified evidence.
Check that artifacts correspond to the stated commit.
Scope review
Detect unrelated changes.
Verify allowed-path compliance.
Identify public interface or dependency changes.
Confirm no generated, credential, or sensitive files were introduced.
Reviewer input
Original user request
Approved task-packet revision
Relevant project decisions
Submitted commit or diff
Verification logs
Relevant surrounding code
Implementer assumptions and limitations

The reviewer should not receive all of Codex’s internal conversation unless a specific failure requires it.

Reviewer output
Approval
decision: approved

criteria:
  AC-1: passed
  AC-2: passed
  AC-3: passed
  AC-4: passed

evidence:
  - Normalized paths are indexed in buildConflictIndex.
  - Case-insensitive behavior is covered by test AC-2.
  - Full regression suite completed successfully.

residual_risk:
  - Hashing large archives may need future performance evaluation.
Changes requested
decision: changes_requested

findings:
  - id: REV-1
    severity: high
    criterion: AC-2
    issue: Paths are lowercased but slash direction is not normalized.
    evidence:
      file: src/conflicts/buildConflictIndex.ts
      lines: 31-38
    required_outcome:
      Treat "data\\file.dat" and "data/file.dat" as the same destination path.

  - id: REV-2
    severity: medium
    issue: The duplicate-file test uses equal filenames but not equal contents.
    evidence:
      file: tests/conflicts/buildConflictIndex.test.ts
      lines: 72-94
Reviewer should not
Rewrite the code during review.
Reject work only because it would have chosen another style.
Introduce new requirements.
Accept work solely because tests pass.
trust the implementer’s summary without checking evidence.
Review the implementation against the planner’s summary while ignoring your original request.
6. Escalation and specialist reasoning — Claude Opus

Opus is not the normal boss. It is a high-cost escalation resource for difficult judgment.

Core mission

Resolve problems that remain ambiguous, interconnected, high-risk, or disputed after normal MAP processing.

Appropriate responsibilities
Architecture
Design major system boundaries.
Compare competing architectural approaches.
Analyze cross-component consequences.
Plan difficult migrations.
identify long-term maintenance risks.
Failure diagnosis
Analyze repeated failed Codex attempts.
Determine whether the task packet itself is wrong.
Separate implementation failure from architectural incompatibility.
Reframe a task that cannot be completed safely as written.
Dispute resolution
Evaluate disagreement between the DRI and reviewer.
Determine whether acceptance criteria are unreasonable.
Decide whether a defect belongs to the current task or a separate task.
Recommend a revised plan for human approval.
High-risk review
Authentication and authorization
Encryption or secret handling
Database migrations
Destructive operations
User-data handling
Release-critical architecture
Opus should receive

Only the evidence needed for the escalated issue:

escalation:
  issue: Three implementations failed to preserve mod load-order behavior.

original_requirement: ...
architecture_context: ...
attempts:
  - attempt: 1
    failure: ...
  - attempt: 2
    failure: ...
  - attempt: 3
    failure: ...
review_findings: ...
decision_needed: Revise implementation or redesign merge-plan representation?
Opus should produce
Root-cause analysis
Options and tradeoffs
Recommended decision
Revised task boundaries
Risks and required human decisions
Opus should not
Handle simple edits.
remain active as a permanent supervisor.
perform repetitive repository searches Haiku can do.
review every routine task.
approve a major strategic choice without your involvement.
7. Precision Editor — Aider

Aider is best treated as an interactive editing instrument, not a separate decision-making department.

Core mission

Apply narrow, well-understood changes under direct human or MAP supervision.

Best responsibilities
Rename symbols across a known set of files.
Apply a specific review correction.
Implement a small, explicit refactor.
Repair a localized test.
Make a change while you watch the diff.
Test local Ollama models against bounded editing tasks.
Use a repository map to locate likely files.
Typical Aider assignment
Change normalizeModPath() so it normalizes both slash direction and case.
Update only:
- src/paths/normalizeModPath.ts
- tests/paths/normalizeModPath.test.ts

Add tests for:
- data/file.dat
- DATA\FILE.DAT

Run the targeted test after editing.
Do not change public interfaces.
Aider is preferable when
You already know the exact correction.
You want to approve each edit.
The change is too small to justify a complete MAP cycle.
You want a local model to perform the edit.
Codex’s broader autonomy is unnecessary.
Aider should not
independently shape large tasks.
compete with Codex on the same assignment.
serve as the final reviewer.
own project-level decisions.
make broad changes from an underspecified instruction.
8. Local Utility Agents — Ollama models

Local models should begin as low-risk support workers. Promote them only after they demonstrate acceptable performance.

Appropriate responsibilities
Information processing
Summarize logs.
Extract file and symbol names.
Classify task type and risk.
Draft task fingerprints.
Identify repeated failure messages.
Convert unstructured reports into structured records.
Repository support
Produce a first-pass repository map.
Search for likely relevant files.
Generate test ideas.
Compare similar functions.
Draft documentation.
Bounded implementation

Only after testing:

Small boilerplate additions
Mechanical renaming
Formatting
Simple test generation
Straightforward transformations with strong tests
Local model output must be treated as untrusted

For example, a local model can propose:

likely_failure_cause:
  category: path-normalization
  evidence:
    - Both failures involve backslash-separated destination paths.
confidence: medium

A stronger agent or deterministic check should verify it.

Promotion ladder
Level 1: Classification and extraction
Level 2: Summarization and repository scouting
Level 3: Test suggestions and documentation
Level 4: Small supervised edits through Aider
Level 5: Independent low-risk implementation

Do not promote a model because one example worked. Evaluate it across repeated representative tasks.

9. Deterministic MAP runtime

This is not an LLM, but it should hold more operational authority than any agent.

Core mission

Enforce rules that cannot safely depend on model obedience.

Responsibilities
Store canonical task state.
Create and validate task claims.
Enforce one writer per worktree.
Assemble agent context.
Start and stop agent runs.
Enforce tool and path permissions.
Track token, time, and retry budgets.
Run required tests.
Record artifacts.
Validate state transitions.
Detect stale or conflicting work.
Prevent self-review.
Preserve event and audit history.
Route escalations.
What should never be left solely to prompts
File-system containment
Claim ownership
Allowed tools
Maximum retries
Test execution
Approval identity
State transitions
Secret detection
Destructive-operation approval
Artifact existence
Base-commit consistency
Standard workflows
Tiny, obvious edit
You
→ Aider or Codex
→ deterministic tests
→ you inspect

Examples:

Fix a typo.
Rename one local symbol.
Correct an obvious test expectation.
Normal feature
You state goal
→ Sonnet shapes task
→ Codex implements
→ MAP runs checks
→ fresh Sonnet reviews
→ Codex corrects findings if needed
→ MAP approves state transition
→ you release

This is the default.

Unfamiliar repository area
Sonnet identifies missing knowledge
→ Haiku/Ollama Scout investigates
→ Sonnet creates task packet
→ Codex implements
→ MAP verifies
→ fresh Sonnet reviews
Difficult debugging
Haiku/Ollama gathers logs and code paths
→ Sonnet forms testable hypotheses
→ Codex runs experiments
→ Codex implements the supported fix
→ fresh Sonnet reviews
→ Opus enters only if failures persist
Major architectural change
Sonnet performs initial analysis
→ Opus evaluates architecture and tradeoffs
→ you approve direction
→ Sonnet divides work
→ one or two Codex workers use separate worktrees
→ deterministic integration checks
→ fresh Sonnet reviews tasks
→ Opus reviews final architecture only when risk justifies it
Responsibility matrix
Activity	Sonnet DRI	Codex	Sonnet Reviewer	Opus	Haiku/Ollama	Aider	Runtime
Interpret user goal	Owns	No	Checks	Escalation	No	No	No
Shape task	Owns	May question	Checks	Escalation	Evidence only	No	Validates schema
Explore repository	Directs	Task-specific	Review-specific	As needed	Primary	Limited	Provides tools
Write production code	Occasionally	Primary	No	Exception	Usually no	Narrow edits	Enforces scope
Run tests	May inspect	During work	May rerun	As needed	No	Targeted	Authoritative
Approve implementation	No	No	Recommends	High-risk review	No	No	Enforces transition
Resolve architecture	Normal	Escalates	Raises concerns	Difficult cases	Evidence only	No	Records decision
Maintain task state	No	Requests transition	Requests transition	No	No	No	Owns
Summarize logs	May	May	May	May	Primary	No	Stores full logs
Make human decisions	No	No	No	Recommends	No	No	No
The central division of labor
Sonnet asks:
What exactly should be done?

Haiku or Ollama asks:
Where is the relevant evidence?

Codex asks:
How do I implement this correctly?

Fresh Sonnet asks:
What is wrong or incomplete?

Opus asks:
Why is the normal process failing, and what larger decision is required?

Aider asks:
What exact edit should I apply?

MAP runtime asks:
Is this action permitted, verifiable, and valid?

That gives each tool a narrow, nonduplicative purpose while keeping the ordinary workflow small.

Humor me and let's treat the agent roles like superheroes as an analogy 
The MAP League

Think of MAP as a superhero organization. Each agent has a specialty, but you do not deploy the entire team every time somebody steals a bicycle.

                         YOU
                  The Mission Authority
                           │
                           ▼
                  SONNET — The Captain
                  plans and coordinates
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
       HAIKU/OLLAMA      CODEX         AIDER
         The Scout      The Builder   The Surgeon
              │            │            │
              └────────────┴────────────┘
                           │
                           ▼
               FRESH SONNET — The Sentinel
                  independently reviews
                           │
                  difficult problem?
                           ▼
                    OPUS — The Oracle

              MAP RUNTIME — The Watchtower
       permissions, records, alarms, and containment
1. You — The Mission Authority
Superhero analogy

You are the person who decides what the team is fighting for. You are closer to Professor X, Nick Fury, or the civilian authority directing the Justice League than an ordinary field hero.

Your power

You possess something none of the agents have:

The ability to decide what you actually want.

Agents can reason about code, architecture, risk, and implementation. They cannot independently determine your preferences or decide what compromises you are willing to accept.

Responsibilities
Define the real mission.
Approve major changes in direction.
Decide between valid but subjective alternatives.
Approve destructive or expensive actions.
Decide whether a project is still serving its intended purpose.
Overrule the team when necessary.
Example

The team might report:

“Automatic conflict resolution is technically possible, but it could silently choose the wrong mod file.”

You decide whether the program should prioritize convenience or user control.

Weakness

You should not have to inspect every terminal command or settle every minor naming decision. If MAP constantly interrupts you over trivial matters, the team is failing to filter decisions properly.

2. Claude Sonnet — The Captain
Comparable heroes

Cyclops, Captain America, or Batman when he is coordinating the team rather than fighting personally.

Primary power

Situational understanding.

Sonnet looks at a vague objective, the project’s current condition, available resources, and possible dangers, then turns that into a workable mission.

Responsibilities
Interpret your request.
Understand the relevant project context.
Distinguish the goal from optional improvements.
Identify unknowns and risks.
Break the mission into sensible tasks.
Assign the correct agent.
Define what success looks like.
Coordinate dependencies.
Replan when circumstances change.
Protect the larger project direction.
What The Captain says

Not:

“Codex, make the feature good.”

Instead:

“Codex, add conflict detection before merge execution. Preserve current load ordering, normalize Windows paths, distinguish identical duplicates from actual conflicts, and do not implement automatic resolution. These five tests define success.”

Special ability: mission packets

The Captain transforms a vague civilian request into an operational briefing:

mission: Detect conflicts between selected Torchlight II mods

objectives:
  - Identify duplicate destination paths.
  - Distinguish identical files from incompatible files.
  - Show which mods contributed each file.

restrictions:
  - Do not modify source archives.
  - Do not automatically resolve conflicts.
  - Do not redesign unrelated screens.

success_conditions:
  - Windows path capitalization is normalized.
  - Existing merges continue to work.
  - Conflict results are covered by tests.
What Sonnet should not do
Fight every battle personally.
Follow Codex around commenting on every keystroke.
Approve its own implementation.
Turn a five-minute repair into a twelve-agent operation.
Invent project requirements merely to make the plan more elaborate.
Weakness

The Captain can misunderstand the original mission. If Sonnet creates the wrong acceptance criteria, Codex may perfectly complete the wrong task.

That is why the reviewer must receive your original request—not merely Sonnet’s interpretation.

3. Claude Haiku — The Scout
Comparable heroes

The Flash, Nightcrawler, Spider-Man performing reconnaissance, or a technologically enhanced field scout.

Primary power

Speedy reconnaissance and information compression.

Haiku moves quickly through the repository, finds relevant locations, and reports what matters without attempting to command the mission.

Responsibilities
Map unfamiliar parts of a repository.
Find relevant files, symbols, and tests.
Trace data or control flow.
Summarize long logs.
Locate all uses of an interface.
Identify likely dependencies.
Compare related implementations.
Prepare compact evidence for Sonnet or Codex.
Produce task fingerprints after completion.
Example mission

“Find where mod load order is stored, where it affects merge output, and which tests currently cover it. Do not modify anything.”

Scout report
load_order_source:
  file: src/project/selectedMods.ts
  symbol: SelectedMod.position

merge_behavior:
  file: src/merge/buildMergePlan.ts
  symbol: buildMergePlan
  finding: Mods are processed in ascending position order.

overwrite_behavior:
  file: src/merge/writeMergedFiles.ts
  finding: Later files overwrite earlier files without recording a conflict.

missing_test:
  - No test covers paths differing only by capitalization.
What Haiku should not do
Make architectural decisions.
Write production code during reconnaissance.
Declare the mission complete.
Convert uncertain evidence into confident conclusions.
Act as a second project manager.
Weakness

The Scout is fast, but speed can produce shallow interpretations. Sonnet must decide what the evidence means.

4. Ollama models — The Local Patrol
Comparable heroes

Street-level heroes, support drones, junior team members, or regional defenders.

They may not possess world-saving power, but they are nearby, inexpensive to deploy, and useful for routine work.

Primary power

Availability and local operation.

They can handle repetitive or lower-risk work without consuming paid API access.

Responsibilities

Initially:

Classify tasks.
Summarize logs.
Extract names, paths, and errors.
Draft task fingerprints.
Organize documentation.
Produce repository overviews.
Suggest tests.
Compare structured files.

After demonstrating reliability:

Make small supervised edits.
Generate straightforward tests.
Apply mechanical transformations.
Handle low-risk implementation with strong automated validation.
Promotion system
Rookie:
Classification and extraction

Field Scout:
Repository summaries and log analysis

Support Hero:
Test suggestions and documentation

Junior Operative:
Small edits through Aider

Full Field Agent:
Independent low-risk tasks
What local models should not initially do
Change architecture.
Perform security-critical work.
Migrate databases.
approve releases.
Make broad autonomous edits without strong tests.
Weakness

A local model may sound as confident as a frontier model despite understanding less. MAP should promote local models based on demonstrated results, not confidence or benchmark marketing.

5. Codex — The Builder
Comparable heroes

Iron Man, Forge, Cyborg, or Mister Terrific when actively constructing systems.

Primary power

Turning a mission plan into working machinery.

Codex is the team member most likely to enter the workshop, modify the actual system, run tests, discover implementation problems, and produce a functioning result.

Responsibilities
Read the approved mission packet.
Inspect relevant code and tests.
Implement the requested behavior.
Add or repair tests.
Run type checks, linters, builds, and test suites.
Keep the change within scope.
Preserve existing project conventions.
Report assumptions and limitations.
Submit a patch or commit for independent review.
Codex’s field report
mission: TASK-204
status: submitted

changed:
  - src/conflicts/buildConflictIndex.ts
  - src/conflicts/types.ts
  - tests/conflicts/buildConflictIndex.test.ts

tests:
  targeted: passed
  full_suite: passed
  typecheck: passed

assumptions:
  - Mod paths should be compared case-insensitively on every platform.

known_risk:
  - Large-file equality currently requires full hashing.
Codex may decide
Local function structure.
Private implementation details.
Which existing utilities to reuse.
How to construct tests.
How to correct defects within its assigned scope.
Codex must call for help when
It needs to modify forbidden files.
The mission contradicts the existing architecture.
Requirements conflict.
A new dependency is necessary.
A public API must change.
Tests reveal a larger unrelated problem.
Multiple reasonable attempts fail.
What Codex should not do
Rewrite the mission.
Add unrelated improvements.
Declare itself approved.
Hide failed tests.
Keep fighting indefinitely after repeated failure.
Modify architecture simply because another design looks cleaner.
Weakness

The Builder can become focused on making the machinery work and miss whether it is the machinery you actually asked for.

That is why Codex needs both The Captain and The Sentinel.

6. Aider — The Surgeon
Comparable heroes

Ant-Man, the Atom, or a precision specialist capable of entering a machine and fixing one exact component.

Primary power

Small, controlled, visible edits.

Aider is not the hero you call to command the invasion. It is the specialist you call when you already know which wire needs repairing.

Responsibilities
Apply a specific review correction.
Rename a symbol across known files.
Repair a localized test.
Perform a narrow refactor.
Make supervised changes while you inspect the diff.
Give Ollama models a controlled editing interface.
Use its repository map to locate nearby code.
Good mission

“Normalize slash direction inside normalizeModPath(), add two test cases, and change no public interfaces.”

Bad mission

“Make the whole application better.”

What Aider should not do
Design the project architecture.
Independently redefine requirements.
Compete with Codex by implementing the same mission.
Approve its own changes.
Wander through unrelated systems.
Weakness

The Surgeon is only as effective as the diagnosis. A precise edit to the wrong location remains wrong.

7. Fresh Claude Sonnet — The Sentinel
Comparable heroes

Batman as contingency planner, Daredevil cross-examining evidence, or a skeptical Watchman assigned to find weaknesses.

This is still Sonnet, but it occupies a different role in a fresh session.

The Captain asks:

“How should we accomplish the mission?”

The Sentinel asks:

“How does this solution fail?”

Primary power

Adversarial review.

The Sentinel tries to disprove that the submitted work is correct.

Responsibilities
Compare the implementation with your original request.
Check every acceptance criterion.
Inspect the changed code.
Inspect connected code outside the diff.
Look for edge cases.
Verify that tests actually prove the claimed behavior.
Identify unrelated changes.
Detect product drift.
Check maintainability and architecture.
Approve, reject, or request specific changes.
Sentinel report
decision: changes_requested

findings:
  - severity: high
    problem: Backslashes and forward slashes are treated as different paths.
    evidence: src/conflicts/buildConflictIndex.ts lines 31-38
    required_result:
      data/file.dat and DATA\FILE.DAT must resolve to the same destination.

  - severity: medium
    problem: Duplicate-content testing does not verify actual file contents.
    evidence: tests/conflicts/buildConflictIndex.test.ts lines 72-94
The Sentinel should receive
Your original request
The approved mission packet
The submitted diff or commit
Test results
Relevant architecture decisions
Codex’s assumptions and limitations

It should not inherit Codex’s entire conversation or confidence.

What The Sentinel should not do
Rewrite the code during review.
Reject work because it prefers another style.
Introduce new requirements.
Trust Codex’s summary without checking evidence.
Praise the implementation instead of investigating it.
Weakness

Because the Captain and Sentinel may use the same underlying model, they can share similar blind spots. For high-risk work, Opus or a different model family may provide an additional challenge.

8. Claude Opus — The Oracle
Comparable heroes

Doctor Strange, Superman reserved for catastrophic threats, or Batman when solving a crisis involving the entire system.

Primary power

Deep reasoning over difficult, interconnected problems.

Opus should not patrol ordinary streets. It enters when normal procedures fail or when the stakes justify the cost.

Responsibilities
Resolve major architectural questions.
Diagnose repeated failed implementations.
Analyze conflicts between requirements and existing design.
Compare difficult alternatives.
Review security-sensitive work.
Plan complex migrations.
Settle disputes between Captain, Builder, and Sentinel.
Recommend a revised mission to you.
Appropriate emergency signal
crisis:
  mission: Preserve load order while introducing conflict resolution.
  failed_attempts: 3
  recurring_problem:
    Every approach changes overwrite behavior used by existing projects.
  decision_required:
    Extend the merge-plan format or preserve implicit overwrite semantics?
Oracle response
Explain the root cause.
Separate symptoms from the actual architectural conflict.
Present alternatives.
State tradeoffs.
Recommend a direction.
Identify what requires your approval.
Produce a revised plan.
What Opus should not do
Fix typos.
Summarize ordinary logs.
Remain constantly active.
Review every simple change.
Use expensive reasoning where tests can answer the question.
Make subjective project decisions without you.
Weakness

The Oracle is powerful but expensive, slower, and still fallible. Calling Opus for every task is like summoning Doctor Strange because the printer jammed.

9. MAP Runtime — The Watchtower
Comparable systems

The Batcomputer, Avengers Tower, the Justice League Watchtower, or JARVIS.

The Watchtower is not another superhero. It is the infrastructure that prevents superheroes from destroying the city while attempting to save it.

Primary power

Deterministic authority.

Agents can reason and recommend. The Watchtower enforces.

Responsibilities
Store canonical task state.
Assign missions.
Enforce claims and leases.
Create isolated worktrees.
Restrict tools and writable paths.
Start and stop agents.
Enforce token, time, and retry limits.
Run authoritative tests.
Store artifacts and logs.
Detect conflicting work.
Prevent an agent from reviewing itself.
Record every state transition.
Escalate failures.
Require human approval for dangerous operations.
Example

Codex says:

“I need to edit src/auth/secrets.ts.”

The Watchtower does not debate the request. It checks the mission scope.

ACCESS DENIED

Requested path:
src/auth/secrets.ts

Writable mission scope:
src/conflicts/**
tests/conflicts/**

Required action:
Submit scope-expansion request to Project DRI.
Weakness

The Watchtower cannot determine whether a feature is enjoyable, elegant, or aligned with your intent. It can enforce rules, but it cannot replace judgment.

Deployment levels
Street-level problem

Examples:

Typo
Simple test repair
Narrow rename
Obvious local bug
Aider or Codex
→ Watchtower checks
→ You inspect

No need to assemble the Justice League.

Standard villain

Examples:

Normal feature
Moderate bug
Several connected files
New behavior requiring tests
The Captain — Sonnet
        ↓
The Builder — Codex
        ↓
The Watchtower — automated checks
        ↓
The Sentinel — fresh Sonnet

This is the standard MAP deployment.

Mystery investigation

Examples:

Unknown bug origin
Unfamiliar repository area
Confusing logs
Unclear dependencies
The Scout — Haiku/Ollama
        ↓ evidence
The Captain — Sonnet
        ↓ plan
The Builder — Codex
        ↓ implementation
The Sentinel — fresh Sonnet
Precision repair

Examples:

Reviewer found one exact defect
Small refactor
Local model experiment
The Surgeon — Aider
        ↓
The Watchtower — tests
        ↓
The Sentinel or You
World-ending crisis

Examples:

Architectural failure
Repeated failed implementations
Security-sensitive migration
Data-loss risk
Fundamental disagreement among agents
The Scout gathers evidence
        ↓
The Captain explains the current situation
        ↓
The Oracle — Opus
        ↓ recommendation
You make the consequential decision
        ↓
The Captain creates the revised mission
        ↓
The Builder implements it
        ↓
The Sentinel reviews it
Team rules
Never deploy two heroes to perform the same role

Do not have Codex, Aider, and Ollama all independently implement the same change unless you are deliberately comparing them.

That creates three competing realities and makes the reviewer the actual implementer.

Never let The Builder approve The Builder

Codex can self-check, but it cannot independently approve its work.

Never confuse power with authority

Opus may be more capable than Sonnet, but that does not mean it gets to decide your preferences.

Never send the whole team automatically

The smallest adequate deployment is usually the most efficient.

The Watchtower outranks field-agent confidence

A model saying “the tests pass” is not authoritative. The runtime running the tests is authoritative.

The simple version
MAP member	Superhero role	Primary question
You	Mission Authority	What are we trying to achieve?
Sonnet	The Captain	What should the team do?
Haiku	The Scout	Where is the relevant evidence?
Ollama	Local Patrol	What inexpensive support work can be handled locally?
Codex	The Builder	How do I make it work?
Aider	The Surgeon	What exact edit needs to be made?
Fresh Sonnet	The Sentinel	What is wrong with this result?
Opus	The Oracle	Why is the normal process failing?
MAP runtime	The Watchtower	Is this action allowed and verifiably complete?

The superhero version of MAP is therefore not a crowd of powerful characters shouting in a headquarters.

It is a controlled response team:

The Captain defines the mission, the Scout finds the path, the Builder does the work, the Surgeon handles precise repairs, the Sentinel challenges the result, the Oracle resolves crises, and the Watchtower keeps everyone inside the rules.

Yesterday 9:00 AM
Ideally if you were building the files for the system from the ground for tasks, what would it look like? The goal being for ease of indexing, reducing token cost, and the other things we talked about, what would a template for that look like 
Worked for 1m 12s
Ideal MAP file architecture

The system should separate four kinds of information:

Rules — stable instructions such as roles, policies, and skills.
Work — current objectives, scope, dependencies, and acceptance criteria.
Evidence — diffs, tests, logs, reviews, and decisions.
Memory — compact summaries that help future agents retrieve relevant history.

The central rule is:

Each fact should have one canonical home. Other files should reference it by ID or path rather than copying it.

This reduces contradictions, simplifies indexing, and prevents every agent from loading the entire project history.

1. Two-level structure

Use a global MAP installation plus a smaller project-local directory.

Global MAP system
~/.map/
├── system/
│   ├── CONSTITUTION.md
│   ├── policies/
│   │   ├── execution.yaml
│   │   ├── security.yaml
│   │   ├── review.yaml
│   │   └── escalation.yaml
│   ├── roles/
│   │   ├── project-dri.md
│   │   ├── delivery-implementer.md
│   │   ├── independent-reviewer.md
│   │   ├── scout.md
│   │   ├── triage.md
│   │   └── knowledge-state.md
│   ├── skills/
│   │   ├── index.yaml
│   │   ├── frontend-react/
│   │   │   ├── SKILL.md
│   │   │   └── checks.yaml
│   │   ├── typescript-debugging/
│   │   │   ├── SKILL.md
│   │   │   └── checks.yaml
│   │   └── git-review/
│   │       └── SKILL.md
│   ├── schemas/
│   │   ├── task.schema.json
│   │   ├── handoff.schema.json
│   │   ├── review.schema.json
│   │   ├── run-manifest.schema.json
│   │   └── event.schema.json
│   └── routing/
│       ├── agents.yaml
│       └── capability-routes.yaml
│
├── runtime/
│   ├── map.sqlite
│   ├── locks/
│   ├── worktrees/
│   ├── runs/
│   └── logs/
│
├── artifacts/
│   ├── sha256/
│   └── index.jsonl
│
└── cache/
    ├── repository-maps/
    ├── symbols/
    └── embeddings/
Project-local MAP directory
project-root/
├── .map/
│   ├── project.yaml
│   ├── PROJECT.md
│   ├── CURRENT.md
│   │
│   ├── architecture/
│   │   ├── SYSTEM.md
│   │   ├── COMPONENTS.md
│   │   └── interfaces.yaml
│   │
│   ├── decisions/
│   │   ├── index.jsonl
│   │   ├── ADR-0001-use-sqlite.md
│   │   └── ADR-0002-normalize-mod-paths.md
│   │
│   ├── workstreams/
│   │   ├── WS-001-conflict-analysis.md
│   │   └── WS-002-merge-execution.md
│   │
│   ├── tasks/
│   │   ├── active/
│   │   │   └── TASK-0204/
│   │   │       ├── task.yaml
│   │   │       ├── runs/
│   │   │       │   └── RUN-0204-01/
│   │   │       │       ├── manifest.yaml
│   │   │       │       ├── events.jsonl
│   │   │       │       └── summary.yaml
│   │   │       ├── submissions/
│   │   │       │   └── SUB-0204-01.yaml
│   │   │       └── reviews/
│   │   │           └── REV-0204-01.yaml
│   │   └── archive/
│   │       └── 2026/
│   │           └── 07/
│   │
│   ├── memory/
│   │   ├── task-fingerprints.jsonl
│   │   ├── workstream-digests/
│   │   ├── failure-patterns.jsonl
│   │   └── insight-ledger.jsonl
│   │
│   ├── indexes/
│   │   ├── task-index.jsonl
│   │   ├── decision-index.jsonl
│   │   ├── artifact-index.jsonl
│   │   ├── repository-map.json
│   │   └── symbol-index.jsonl
│   │
│   └── generated/
│       ├── project-snapshot.md
│       ├── active-tasks.md
│       └── dependency-graph.json
│
├── src/
├── tests/
└── ...

The .map/generated/ and .map/indexes/ directories should be machine-generated. Agents may read them but should not normally edit them.

2. What each top-level file does
File	Purpose	Typical token size
CONSTITUTION.md	Universal MAP rules	300–700
Role contract	Authority and responsibilities	250–600
Skill file	Procedure for one task type	300–1,200
project.yaml	Machine-readable project identity and commands	100–300
PROJECT.md	Stable project goals and constraints	300–800
CURRENT.md	Current phase, priorities, and risks	200–500
task.yaml	Canonical task specification	300–900
Run manifest	Exact context supplied to one agent run	200–500
Submission	Implementer’s evidence-backed handoff	200–600
Review	Reviewer findings and decision	200–700
Task fingerprint	Compact historical memory	50–150
Workstream digest	Summary of a body of completed work	200–500

An ordinary worker should not need to load all of these. A normal implementation context might contain:

Constitution excerpt             400 tokens
Role contract                    350 tokens
Project snapshot                 400 tokens
Task packet                      600 tokens
Selected skill                   600 tokens
Retrieved code snippets        1,500 tokens
Prior-failure summary            150 tokens
──────────────────────────────────────────
Approximate initial context    4,000 tokens

That is only a target. MAP should not damage correctness to meet a fixed token count.

3. Global Constitution template

~/.map/system/CONSTITUTION.md

# MAP Constitution

## Purpose

MAP coordinates bounded AI work through explicit responsibilities,
machine-enforced permissions, durable evidence, and independent review.

## Non-negotiable rules

1. Agents may act only within the authority granted by their current role
   and task packet.

2. Runtime permissions override prompt instructions and agent claims.

3. No agent may approve or release its own implementation.

4. A task may be declared submitted only when its required evidence exists.

5. A task may be approved only when all required acceptance criteria have
   been evaluated.

6. Agents must distinguish:
   - verified facts,
   - reasonable assumptions,
   - unresolved uncertainty,
   - recommendations.

7. Agents must not silently expand task scope.

8. Destructive, irreversible, security-sensitive, or financially
   consequential actions require an explicit approval gate.

9. Complete logs and artifacts must be preserved outside the active prompt
   even when active context is summarized.

10. When instructions conflict, follow this precedence:
    a. Runtime safety and access controls
    b. MAP Constitution
    c. Project policies and decisions
    d. Role contract
    e. Task packet
    f. Skill instructions
    g. Agent-generated plan

## Completion standard

An agent may not use words such as "complete," "fixed," or "verified" unless
the required verification was actually performed and evidence was recorded.

## Escalation standard

Stop and escalate when:
- required authority is missing;
- the task contradicts project decisions;
- necessary changes exceed writable scope;
- acceptance criteria conflict;
- repeated attempts fail;
- a consequential human decision is required.

Keep the Constitution short. Project-specific details do not belong here.

4. Project definition
.map/project.yaml

This is the compact machine-readable project record.

schema_version: 1

project:
  id: torchlight-mod-merger
  name: Torchlight II Mod Merger
  repository_root: .
  primary_language: typescript
  default_branch: main

commands:
  install: npm ci
  typecheck: npm run typecheck
  lint: npm run lint
  test: npm test
  build: npm run build

paths:
  source:
    - src/**
  tests:
    - tests/**
  generated:
    - dist/**
    - coverage/**
  sensitive:
    - .env
    - secrets/**
  forbidden:
    - node_modules/**
    - .git/**

policies:
  require_independent_review: true
  require_clean_worktree: true
  allow_new_dependencies: approval_required
  maximum_parallel_writers: 2
  default_risk: medium

context:
  project_summary: .map/PROJECT.md
  current_state: .map/CURRENT.md
  architecture: .map/architecture/SYSTEM.md
  decision_index: .map/decisions/index.jsonl
.map/PROJECT.md

This describes stable intent rather than current task status.

# Torchlight II Mod Merger

## Purpose

Create a desktop application that combines compatible Torchlight II mods
while identifying conflicts clearly and preserving source mod archives.

## Product principles

- Never modify source mod archives.
- Show conflicts before producing a merged package.
- Prefer explicit user control over silent destructive resolution.
- Preserve reproducibility: the same inputs and settings should produce
  the same output.
- Explain failures in language understandable to nontechnical users.

## Technical principles

- Use an intermediate merge manifest before writing output.
- Normalize destination paths before comparing files.
- Separate archive reading, conflict analysis, merge planning, and output.
- Keep domain logic independent from the user interface.

## Out of scope

- Editing mod contents.
- Downloading mods.
- Automatically determining subjective mod compatibility.
.map/CURRENT.md

This file is rewritten periodically and kept small.

# Current Project State

Updated: 2026-07-25

## Current phase

Conflict-analysis foundation.

## Active objective

Detect destination-path conflicts before merge execution.

## Current priorities

1. Build normalized virtual-file index.
2. Distinguish identical duplicates from differing-file conflicts.
3. Expose results through the existing merge-plan API.

## Known risks

- Torchlight archives may use inconsistent path separators and case.
- Existing load-order behavior is not fully covered by tests.
- Hashing large files may affect performance.

## Active workstreams

- WS-001 — Archive ingestion
- WS-002 — Conflict analysis
- WS-003 — Merge execution

This is the project briefing agents read. It should never become a complete project diary.

5. Role contract template

~/.map/system/roles/delivery-implementer.md

# Role: Delivery Implementer

## Mission

Implement one approved task within its assigned scope and submit
verifiable evidence for independent review.

## Owns

- Local implementation decisions within the task's writable scope
- Tests required to demonstrate acceptance
- Accurate reporting of changes, failures, assumptions, and limitations

## May

- Read paths listed in the task packet
- Modify writable paths listed in the task packet
- Run approved project commands
- Request additional context
- Request scope expansion
- Escalate contradictions or blocked work

## Must

1. Confirm the task ID, revision, and base revision before editing.
2. Inspect applicable instructions and project decisions.
3. Preserve existing behavior outside the task objective.
4. Add or update tests when behavior changes.
5. Run every required verification command.
6. Review the final diff for accidental changes.
7. Submit evidence rather than self-approving.

## Must not

- Modify forbidden or unlisted paths
- Change public interfaces without authorization
- Add dependencies without authorization
- Perform unrelated cleanup
- Rewrite task objectives
- Mark work approved or released
- Conceal failed checks

## Required output

A structured implementation submission containing:

- task and run identifiers;
- result revision;
- changed files;
- implementation summary;
- verification evidence;
- assumptions;
- known limitations;
- artifact references.

## Escalate when

- scope is insufficient;
- requirements conflict;
- project architecture blocks the objective;
- a dependency is missing;
- repeated attempts fail;
- a security, privacy, or data-loss concern appears.

Every role file should use approximately the same headings:

Mission
Owns
May
Must
Must not
Required input
Required output
Escalate when
Completion condition

This makes role files easy to index and compare.

6. Skill structure

Skills are procedures, not personalities.

Skill index

~/.map/system/skills/index.yaml

skills:
  - id: typescript-debugging
    title: TypeScript Debugging
    description: Diagnose and repair TypeScript runtime or compile failures.
    triggers:
      - typescript error
      - failing test
      - runtime exception
    path: typescript-debugging/SKILL.md
    estimated_tokens: 650

  - id: frontend-react
    title: React Component Implementation
    description: Implement or modify React UI components with tests.
    triggers:
      - react
      - component
      - user interface
    path: frontend-react/SKILL.md
    estimated_tokens: 800

  - id: git-review
    title: Git Diff Review
    description: Review a submitted diff against a task specification.
    triggers:
      - review
      - submitted implementation
    path: git-review/SKILL.md
    estimated_tokens: 550

The agent initially sees only this metadata. The full skill loads only when selected.

Skill template

~/.map/system/skills/typescript-debugging/SKILL.md

# Skill: TypeScript Debugging

## Use when

- TypeScript compilation fails
- A JavaScript or TypeScript test fails
- Runtime behavior contradicts expected typed behavior

## Do not use when

- The task is primarily architectural
- The failure concerns deployment infrastructure
- The affected code is outside authorized scope

## Procedure

1. Reproduce the failure using the narrowest reliable command.
2. Record the exact error and failing location.
3. Trace the value or control path that reaches the failure.
4. Identify the smallest supported root cause.
5. Add or update a test that fails before the correction.
6. Apply the narrowest correction consistent with project design.
7. Run:
   - the targeted test;
   - the relevant test group;
   - type checking;
   - the full required verification suite.

## Evidence requirements

- Reproduction command
- Original failure
- Root-cause statement
- Changed files
- Targeted test result
- Required project checks

## Common failure patterns

- Fixing the symptom without reproducing the issue
- Broad use of `any`
- Suppressing errors rather than correcting them
- Updating expectations to match incorrect behavior
- Changing unrelated modules

## Escalate when

- Correct behavior is ambiguous
- The type model conflicts with runtime data
- The required correction changes a public contract

Skills should normally stay below roughly 1,000 tokens. Detailed reference material should live in separate files and load only when needed.

7. Canonical task template

Each task gets a directory:

.map/tasks/active/TASK-0204/
└── task.yaml
task.yaml
schema_version: 1

identity:
  id: TASK-0204
  revision: 3
  project_id: torchlight-mod-merger
  workstream_id: WS-002
  title: Detect destination-path conflicts
  created_at: 2026-07-25T14:00:00-04:00
  created_by: project-dri-run-118

state:
  status: ready
  priority: high
  risk: medium

objective:
  statement: >
    Detect destination paths supplied by more than one selected mod before
    producing the merged package.

  rationale: >
    The current merge process allows later files to overwrite earlier files
    without explaining the conflict to the user.

non_goals:
  - Do not automatically resolve conflicts.
  - Do not redesign the mod-selection interface.
  - Do not modify source archives.
  - Do not change existing load-order semantics.

dependencies:
  requires:
    - TASK-0197
  blocks:
    - TASK-0211

scope:
  writable:
    - src/conflicts/**
    - tests/conflicts/**
  readable:
    - src/archive/**
    - src/merge/**
    - src/paths/**
    - tests/merge/**
    - .map/architecture/**
    - .map/decisions/**
  forbidden:
    - src/auth/**
    - migrations/**
    - package.json
    - package-lock.json

context:
  project_refs:
    - .map/PROJECT.md
    - .map/CURRENT.md
    - .map/architecture/SYSTEM.md

  decision_refs:
    - ADR-0002

  required_skills:
    - typescript-debugging

  retrieval_queries:
    - mod destination path normalization
    - merge overwrite behavior
    - load order tests

capability_requirements:
  task_type: implementation
  coding_complexity: medium
  reasoning_complexity: medium
  expected_context: medium
  privacy: standard
  multimodal: false

constraints:
  - Reuse the existing normalized-path utility where possible.
  - Preserve existing public merge-plan behavior unless explicitly extended.
  - New dependencies require approval.

acceptance_criteria:
  - id: AC-1
    statement: >
      Two different mods supplying the same normalized destination path are
      recorded as a conflict.
    verifier: automated_test
    required_evidence:
      - test_result

  - id: AC-2
    statement: >
      Path comparison treats slash direction and capitalization according to
      Windows path behavior.
    verifier: automated_test
    required_evidence:
      - test_result

  - id: AC-3
    statement: >
      Identical duplicate files are classified separately from files with
      different contents.
    verifier: automated_test
    required_evidence:
      - test_result

  - id: AC-4
    statement: Existing nonconflicting merge tests continue to pass.
    verifier: command
    command: npm test
    required_evidence:
      - command_exit_code
      - log_reference

required_checks:
  - npm run typecheck
  - npm test -- tests/conflicts
  - npm test

expected_artifacts:
  - implementation_submission
  - code_diff
  - verification_log

budgets:
  maximum_attempts: 3
  maximum_runtime_minutes: 45
  maximum_scope_expansions: 1

escalation:
  when:
    - Required work touches an unlisted writable path.
    - Existing load-order semantics are unclear.
    - A public interface must change.
    - Content comparison requires a new external dependency.

completion:
  submission_required: true
  independent_review_required: true
  human_approval_required: false
Important task-design principle

The task declares capability needs, not a specific model:

capability_requirements:
  task_type: implementation
  coding_complexity: medium

The routing system decides that this should go to Codex. This prevents model names from being embedded throughout project history.

8. Model and harness routing
~/.map/system/routing/agents.yaml

Use stable aliases so model changes affect one file.

agents:
  captain:
    harness: claude-code
    model_alias: claude-default-lead
    role: project-dri

  scout-fast:
    harness: claude-code
    model_alias: claude-fast
    role: scout

  scout-local:
    harness: aider
    model_alias: ollama-local-scout
    role: scout

  builder:
    harness: codex
    model_alias: codex-default
    role: delivery-implementer

  surgeon:
    harness: aider
    model_alias: aider-default
    role: delivery-implementer

  sentinel:
    harness: claude-code
    model_alias: claude-default-reviewer
    role: independent-reviewer
    fresh_context: true
    write_access: false

  oracle:
    harness: claude-code
    model_alias: claude-escalation
    role: escalation-analyst
capability-routes.yaml
routes:
  - match:
      task_type: planning
      reasoning_complexity:
        - low
        - medium
    use: captain

  - match:
      task_type: repository_investigation
      risk:
        - low
        - medium
    prefer:
      - scout-local
      - scout-fast

  - match:
      task_type: implementation
      coding_complexity:
        - medium
        - high
    use: builder

  - match:
      task_type: precision_edit
      coding_complexity: low
    use: surgeon

  - match:
      task_type: review
    use: sentinel

  - match:
      reasoning_complexity: critical
    use: oracle

This is where the superhero seats become operational routing.

9. Run manifest

Every time an agent starts, MAP generates a run folder.

.map/tasks/active/TASK-0204/runs/RUN-0204-01/
├── manifest.yaml
├── events.jsonl
└── summary.yaml
manifest.yaml

This records exactly what the agent was shown.

schema_version: 1

run:
  id: RUN-0204-01
  task_id: TASK-0204
  task_revision: 3
  agent_alias: builder
  role: delivery-implementer
  started_at: 2026-07-25T15:10:00-04:00

repository:
  base_commit: 8c20f9df
  worktree: runtime/worktrees/RUN-0204-01

instructions:
  - ref: system/CONSTITUTION.md
    version_hash: sha256:111aaa

  - ref: system/roles/delivery-implementer.md
    version_hash: sha256:222bbb

  - ref: project/.map/PROJECT.md
    version_hash: sha256:333ccc

  - ref: project/.map/CURRENT.md
    version_hash: sha256:444ddd

skills:
  - id: typescript-debugging
    ref: system/skills/typescript-debugging/SKILL.md
    version_hash: sha256:555eee

task:
  ref: .map/tasks/active/TASK-0204/task.yaml
  revision: 3
  version_hash: sha256:666fff

retrieved_context:
  - ref: src/merge/buildMergePlan.ts
    lines: 18-96
    reason: Current merge ordering
    version_hash: sha256:777ggg

  - ref: src/paths/normalizeModPath.ts
    lines: 1-54
    reason: Existing path-normalization utility
    version_hash: sha256:888hhh

  - ref: tests/merge/loadOrder.test.ts
    lines: 1-140
    reason: Existing behavior coverage
    version_hash: sha256:999iii

prior_attempts: []

runtime_limits:
  maximum_turns: 30
  maximum_tool_failures: 3
  maximum_minutes: 45

permissions:
  tools:
    - read_file
    - edit_file
    - run_command
    - search_repository

  writable_paths:
    - src/conflicts/**
    - tests/conflicts/**

This solves several problems:

Reproducibility
Auditability
Context debugging
Prompt comparison
Token accounting
Detecting missing information
Evaluating whether a model failed or the context packet failed
10. Event log

events.jsonl is append-only.

{"time":"2026-07-25T15:10:00-04:00","type":"RUN_STARTED","run_id":"RUN-0204-01"}
{"time":"2026-07-25T15:11:04-04:00","type":"FILE_READ","path":"src/merge/buildMergePlan.ts","lines":"18-96"}
{"time":"2026-07-25T15:15:23-04:00","type":"FILE_WRITTEN","path":"src/conflicts/buildConflictIndex.ts"}
{"time":"2026-07-25T15:19:41-04:00","type":"CHECK_FAILED","command":"npm test -- tests/conflicts","exit_code":1,"artifact":"artifact://sha256/abc123"}
{"time":"2026-07-25T15:24:10-04:00","type":"CHECK_PASSED","command":"npm test -- tests/conflicts","exit_code":0,"artifact":"artifact://sha256/def456"}
{"time":"2026-07-25T15:29:33-04:00","type":"RUN_SUBMITTED","submission_id":"SUB-0204-01"}

The active agent should not receive this entire stream. Triage and auditing tools can query it. A compact summary is generated when needed.

11. Implementation handoff

submissions/SUB-0204-01.yaml

schema_version: 1

submission:
  id: SUB-0204-01
  task_id: TASK-0204
  task_revision: 3
  run_id: RUN-0204-01
  submitted_at: 2026-07-25T15:29:33-04:00

repository:
  base_commit: 8c20f9df
  result_commit: db17e65a

result:
  summary: >
    Added normalized destination-path indexing and separate classifications
    for identical duplicates and differing-file conflicts.

changed_files:
  - path: src/conflicts/buildConflictIndex.ts
    change: created
  - path: src/conflicts/types.ts
    change: created
  - path: tests/conflicts/buildConflictIndex.test.ts
    change: created

acceptance_results:
  - criterion: AC-1
    claimed_status: passed
    evidence:
      - artifact://sha256/test-ac1

  - criterion: AC-2
    claimed_status: passed
    evidence:
      - artifact://sha256/test-ac2

  - criterion: AC-3
    claimed_status: passed
    evidence:
      - artifact://sha256/test-ac3

  - criterion: AC-4
    claimed_status: passed
    evidence:
      - artifact://sha256/full-test-log

verification:
  - command: npm run typecheck
    exit_code: 0
    artifact: artifact://sha256/typecheck-log

  - command: npm test -- tests/conflicts
    exit_code: 0
    artifact: artifact://sha256/conflict-test-log

  - command: npm test
    exit_code: 0
    artifact: artifact://sha256/full-test-log

assumptions:
  - Windows-style path comparison should be used on every host platform.

limitations:
  - File identity currently requires complete-file hashing.

unresolved_risks:
  - Large archives may need future hashing-performance optimization.

artifacts:
  diff: artifact://sha256/task-0204-diff
  run_log: artifact://sha256/run-0204-log

Note the phrase claimed_status. The implementer claims that it passed; the reviewer and runtime verify it.

12. Review template

reviews/REV-0204-01.yaml

schema_version: 1

review:
  id: REV-0204-01
  task_id: TASK-0204
  task_revision: 3
  submission_id: SUB-0204-01
  reviewer_run_id: RUN-0204-REVIEW-01
  reviewer_role: independent-reviewer
  reviewed_at: 2026-07-25T16:05:00-04:00

independence:
  implementation_run_id: RUN-0204-01
  same_run_as_implementer: false
  reviewer_write_access: false

decision: changes_requested

criteria:
  - id: AC-1
    result: passed
    evidence:
      - src/conflicts/buildConflictIndex.ts
      - artifact://sha256/test-ac1

  - id: AC-2
    result: failed
    evidence:
      - src/conflicts/buildConflictIndex.ts:31-38
    explanation: >
      The implementation lowercases paths but does not normalize backslashes
      to forward slashes.

  - id: AC-3
    result: passed

  - id: AC-4
    result: passed

findings:
  - id: FIND-0204-01
    severity: high
    category: correctness
    criterion: AC-2
    statement: >
      Paths that differ only by slash direction are treated as different
      destinations.
    evidence:
      file: src/conflicts/buildConflictIndex.ts
      lines: 31-38
    required_outcome: >
      Normalize slash direction before inserting paths into the conflict index.
    suggested_scope:
      - src/paths/normalizeModPath.ts
      - tests/paths/normalizeModPath.test.ts

  - id: FIND-0204-02
    severity: medium
    category: test_quality
    statement: >
      No test combines capitalization and slash-direction differences.

residual_risks:
  - Large-file hashing performance remains unmeasured.

next_action:
  type: return_to_implementation
  required_findings:
    - FIND-0204-01
    - FIND-0204-02

Review findings should specify the required outcome, not rewrite the implementation for Codex.

13. Task fingerprint

When a task is approved or released, generate one compact memory record.

.map/memory/task-fingerprints.jsonl

{"task_id":"TASK-0204","workstream":"WS-002","title":"Detect destination-path conflicts","result":"Added normalized path conflict indexing with separate identical-duplicate classification.","changed_concepts":["path normalization","conflict indexing","content hashing"],"key_files":["src/conflicts/buildConflictIndex.ts","src/paths/normalizeModPath.ts"],"failure_pattern":"Initial implementation normalized case but not slash direction.","reusable_insight":"Any mod-path identity check must normalize case and slash direction before comparison.","risk":"medium","completed_at":"2026-07-25"}

This is what future agents search first.

They should not open the full task directory unless the fingerprint appears relevant.

14. Workstream digest

After several related tasks, Knowledge and State creates a digest.

.map/memory/workstream-digests/WS-002.md

# WS-002 — Conflict Analysis

Updated: 2026-07-25
Tasks summarized: TASK-0197, TASK-0204, TASK-0208

## Current capability

The system builds a normalized virtual-file index for selected mods and
distinguishes:

- unique files;
- identical duplicates;
- differing-content conflicts.

## Important decisions

- Path identity follows Windows-style case-insensitive comparison.
- Both slash styles are normalized before comparison.
- Source archives remain immutable.
- Conflict detection occurs before merge-plan execution.

## Repeated failure patterns

- Implementations frequently normalize case but forget slash direction.
- Tests must cover both path identity and content identity.

## Relevant files

- `src/paths/normalizeModPath.ts`
- `src/conflicts/buildConflictIndex.ts`
- `src/conflicts/types.ts`

## Open risks

- Hashing performance for very large mod collections is unmeasured.
- User-facing conflict-resolution policy remains undecided.

This is more useful than making future agents read ten completed tasks.

15. Decision record

.map/decisions/ADR-0002-normalize-mod-paths.md

---
id: ADR-0002
status: accepted
date: 2026-07-25
scope:
  - path identity
  - conflict detection
tags:
  - paths
  - windows
  - mod-merging
---

# Normalize mod paths using Windows semantics

## Context

Torchlight II mod archives may contain paths with inconsistent capitalization
and slash direction. Treating these as separate paths produces incorrect
conflict results.

## Decision

Before comparing destination paths:

1. Replace backslashes with forward slashes.
2. Remove redundant separators.
3. Resolve `.` segments.
4. Reject unsafe parent traversal.
5. Compare using case-insensitive normalized values.

The original display path may be preserved separately.

## Consequences

### Positive

- Conflict detection matches expected Windows behavior.
- Archive behavior is consistent across host platforms.

### Negative

- Normalized identity and displayed path must be stored separately.
- Case-only differences cannot represent distinct destination files.

## Related tasks

- TASK-0197
- TASK-0204

Decisions should be indexed by tags, affected paths, concepts, and status.

16. Index formats

JSONL works well because:

Each record is independent.
Appending is cheap.
It is easy to stream.
It is easy to grep.
Individual lines can be embedded for semantic search.
A corrupt line does not destroy the complete index.
Task index

.map/indexes/task-index.jsonl

{"id":"TASK-0204","title":"Detect destination-path conflicts","status":"approved","workstream":"WS-002","risk":"medium","tags":["conflicts","paths","hashing"],"summary":"Added normalized virtual-file conflict indexing.","archive_path":".map/tasks/archive/2026/07/TASK-0204"}
Decision index
{"id":"ADR-0002","status":"accepted","title":"Normalize mod paths using Windows semantics","tags":["paths","windows"],"affected_paths":["src/paths/**","src/conflicts/**"],"path":".map/decisions/ADR-0002-normalize-mod-paths.md"}
Artifact index
{"artifact_id":"sha256:abc123","type":"test_log","task_id":"TASK-0204","run_id":"RUN-0204-01","size_bytes":18240,"path":"~/.map/artifacts/sha256/ab/abc123","created_at":"2026-07-25T15:29:00-04:00"}

These indexes are projections. SQLite remains authoritative for operational state.

17. Context retrieval order

When an agent receives a task, MAP should retrieve context in this order:

1. Exact task references
2. Applicable project decisions
3. Relevant project instructions
4. Files named in acceptance criteria
5. Symbols referenced by those files
6. Connected tests
7. Relevant task fingerprints
8. Workstream digest
9. Full historical task evidence only when needed

A worker should initially receive something like:

Always loaded
─────────────
Constitution excerpt
Role contract
Task packet
Project snapshot

Loaded when selected
────────────────────
One or two skill files
Relevant decisions

Retrieved dynamically
─────────────────────
Repository map
Symbols
Code ranges
Tests
Prior-failure summaries

Stored out of band
──────────────────
Complete files
Full logs
Historical conversations
Large diffs
Complete task archives
18. What should not be created

Avoid these patterns:

One enormous project-memory file
PROJECT_MEMORY.md

After hundreds of tasks, every agent pays to read irrelevant history.

One giant mutable state.json

It becomes a concurrency bottleneck and mixes unrelated state.

One role file per profession
senior-react-developer.md
sql-expert.md
css-wizard.md

Use stable organizational roles plus temporary skills.

Full transcripts as handoffs

A handoff should contain outcomes, evidence, assumptions, and references—not every thought and failed command.

Duplicated descriptions

Do not manually repeat the same objective in:

task database
task YAML
task Markdown
state JSON
handoff
project log

Keep one canonical task file and generate projections from it.

19. Minimum viable version

The complete structure can be built gradually. MAP v1 only needs:

.map/
├── project.yaml
├── PROJECT.md
├── CURRENT.md
├── decisions/
├── tasks/
│   ├── active/
│   └── archive/
├── memory/
│   └── task-fingerprints.jsonl
└── indexes/
    └── task-index.jsonl

~/.map/
├── system/
│   ├── CONSTITUTION.md
│   ├── roles/
│   ├── skills/
│   └── routing/
├── runtime/
│   └── map.sqlite
└── artifacts/

For each task, start with only:

TASK-XXXX/
├── task.yaml
├── runs/
│   └── RUN-XXXX-01/
│       └── manifest.yaml
├── submissions/
│   └── SUB-XXXX-01.yaml
└── reviews/
    └── REV-XXXX-01.yaml

That captures the essential chain:

Intent
→ bounded task
→ reproducible agent context
→ implementation evidence
→ independent review
→ compact historical memory
Final template philosophy

The ideal MAP filesystem uses three levels of detail:

Immediate context
Task packet + selected instructions + relevant snippets

Operational evidence
Runs + events + submissions + reviews + artifacts

Long-term memory
Fingerprints + workstream digests + decision records

The result is that an agent working on Task 204 does not need to understand Tasks 1 through 203. It receives a compact assignment, the relevant rules, the applicable decisions, and only the portions of history that retrieval identifies as useful.

That is the file-system version of the superhero team:

The Captain writes the mission packet.
The Scout locates supporting intelligence.
The Builder creates a submission.
The Sentinel writes the review.
The Oracle creates escalation decisions.
The Watchtower owns the database, manifests, indexes, permissions, and evidence.
