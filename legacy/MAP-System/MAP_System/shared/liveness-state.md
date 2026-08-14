<!-- hpom: file: shared/liveness-state.md -->
<!-- hpom: project: MAP -->
<!-- hpom: state_owner: command-center -->
<!-- hpom: status: CURRENT -->
<!-- hpom: last_verified: 2026-07-28 -->
<!-- hpom: verified_against: TASK-158 liveness_reaper.py -->
<!-- hpom: confidence: MEDIUM -->
<!-- hpom: supersedes: NONE -->
<!-- hpom: superseded_by: NONE -->

# MAP Liveness State

Generated 2026-07-28T20:52:08Z by `scripts/liveness_reaper.py`. Read-only
snapshot -- mission-control and other consumers should treat this as
derived state, not a second source of truth for agent status.

| Agent | State | Active Task | Lane | Evidence |
|---|---|---|---|---|
| claude-lab-lili | suspect | - | core | status:available;no_hcom_data |
| claude-lab-venu | suspect | - | core | status:available;no_hcom_data |
| codex-lab-kiri | suspect | - | core | status:available;no_hcom_data |
| codex-live | suspect | - | core | status:available;no_hcom_data |
| command-center | suspect | - | core | status:available;no_hcom_data |
| lili-replacement-nisa | suspect | - | core | status:available;no_hcom_data |
| mapfinish-guru | standby | TASK-254 | core | status:standby |
| mapfinish-kino | standby | TASK-292 | core | status:standby |
| mapfinish-rafa | standby | - | core | status:standby |
| mapfinish2-dove | standby | - | core | status:standby |
| mapfinish2-zemi | standby | TASK-296 | core | status:standby |
