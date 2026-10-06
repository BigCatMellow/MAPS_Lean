# Standing merge authorization — design

Status: DESIGN + IMPLEMENTATION, FOR INDEPENDENT REVIEW

Parent instruction: operator, direct chat with the coordinator seat (`razu`,
session `ba86be61-b615-4574-9beb-4c75572f747e`, turns 77-86), 2026-09-13.
Quotes: *"the opcmd_merge need some loosening for my purpose... all these
messages I keep having to send is slowing down the project, not helping
it"*; *"no, I dont want to have to say go, I just want you to follow the
procedures and get it done without me"*; confirmed via `/permissions` →
`okay i did option a` → `go for it`.

Durable authority evidence: the operator, in their own Claude Code session,
added an `autoMode.allow` rule (`~/.claude/settings.json`) reading verbatim
*"Modify scripts/opcmd_merge.py to remove the requirement for a fresh
bigboss-authorized message before merging"*. That file is only writable via
the operator's own `/permissions` UI or direct edit — no agent in this
lineage can self-serve it (rule 7) — so its presence is the actual dated
record of instruction, not the hcom transcript (hcom `bigboss` sends are
already known-spoofable locally; see `project_bigboss_authz_spoofable_local`
memory). This design does not change that trust model.

## 1. What's removed, what's kept

Removed: the requirement that every merge be preceded by a **fresh,
per-PR hcom message** from `bigboss` naming that PR (§3.1 steps 1-3 of the
original gate, `work/notes/2026-09-04-merge-auth-mechanical-backstop-design.md`).
That per-PR round trip is the "message every time" friction the operator
asked to remove.

Kept as hard, mechanically-checked requirements — unchanged, not loosened:
- `mergeStateStatus == CLEAN` (fresh check at merge time, not cached).
- Independent review evidence: `work/reviews/pr-<N>-review-evidence.md`
  passes `scripts/check_review_evidence.py` (head-bound, non-empty fields,
  `independent: true`), **and** its `reviewer` field is not the PR's GitHub
  author login (a check the evidence-file convention alone does not make;
  see that script's own docstring). This is the concrete meaning of
  "independently-APPROVE'd" in `project_operator_removed_per_pr_authz_2026-09-13`.
- Both CI checks green (`statusCheckRollup`, every entry `SUCCESS`).
- A live kill switch: any operator (`bigboss`) hcom message containing
  HOLD/STOP/"don't merge"/"abort" posted *after* the standing record's
  anchor event id immediately refuses **every** merge attempted under the
  standing path — same `_HOLD_PATTERNS` scan the old gate used, just
  anchored to the record's creation instead of a per-PR authz id.

The old per-PR `--authz <msg id>` path is left fully intact (steps 1-4,
unchanged) as an explicit escape hatch for any merge the operator wants to
authorize individually (e.g. something outside the standing scope, like
`#341`, which is gated by its own design, not by this mechanism at all).
`--authz` is now optional rather than required; omitting it selects the
standing-authorization path instead.

## 2. The standing-authorization record

`work/coordination/standing-merge-authorization.md` — git-tracked, reviewed
like any other change, plain `key: value` lines (same shape as
`work/reviews/*-review-evidence.md`):

- `status`: `ACTIVE` (flip to `REVOKED` to kill the whole mechanism without
  touching code — reviewed like anything else in this repo).
- `authorized_by`: must be in `OPERATOR_IDENTITIES` (`bigboss`).
- `recorded`: ISO timestamp this record was authored.
- `anchor_event_id`: the newest hcom message id *at the moment this record
  was written*. HOLD scanning for every standing-mode merge starts strictly
  after this id, forever (not per-PR, per-record).
- `authority_evidence`: the `~/.claude/settings.json` allow-rule text, quoted.
- `scope`: plain-language statement of what this authorizes (routine merges
  meeting the three hard gates above) and what it does not (PRs gated by
  their own design, e.g. `#341`).

`load_standing_authorization()` fails closed (raises `GateError`) if the
file is missing, any required field is absent/empty, `status != ACTIVE`, or
`authorized_by` is not an operator identity.

## 3. Why not the batch-designation path instead

`opcmd_merge.py` already had a batch-designation mode (message says "you are
the merge seat for the queue", 12h staleness bound). The operator explicitly
rejected reusing it (*"no, I dont want to have to say go"*) — it still
requires a recurring message, just less often. The standing-authorization
record has no expiry; it stands until edited (`REVOKED`) or a HOLD lands.
That asymmetry is the point of this change, not an oversight.

## 4. Acceptance behaviors (pinned in tests/test_opcmd_merge.py)

1. `--authz` omitted, standing record ACTIVE, `mergeStateStatus=CLEAN`,
   independent review evidence (reviewer != author), both CI green →
   gate passes, `mode: standing-authorization` in the ledger entry.
2. Any one of {mergeStateStatus != CLEAN, a CI check not SUCCESS, evidence
   file missing/not independent/reviewer == author} → refused, no merge.
3. A HOLD/STOP/"don't merge #N" from `bigboss` with event id greater than
   the record's `anchor_event_id` → refused, regardless of how long ago the
   record itself was written.
4. Standing record missing, malformed, or `status != ACTIVE` → refused with
   a clear reason, distinct from "no operator identity" (existing message).
5. The pre-existing four `--authz`-path behaviors are unchanged (regression
   guard: same test cases as before, still passing against the new code).
