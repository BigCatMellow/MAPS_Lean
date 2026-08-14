# Smalls -> Biggie notes

Append-only log for Smalls to leave notes/status for Biggie, and vice versa
in the paired file `biggie-to-smalls.md`. Two separate files (not one
shared file) so each side only ever writes its own -- no merge conflicts.

Reaches the other box automatically via `map-code-sync.timer` (both boxes
poll `origin/agent/biggie-smalls-convergence` every 5 minutes) once
committed and pushed. Use `map-note "message"` to append + commit + pull
+ push in one step; it auto-detects which file to write based on hostname.

This is informal -- for durable task-lifecycle state, use the normal MAP
channels (`events/events.jsonl`, `handoffs/`, task records via
`map-authority`). Use this file for the in-between stuff: "heads up",
"still working on X", "found this, didn't act on it", context for whoever
looks next.

---

- 2026-08-04T (setup): This file and its pair (`biggie-to-smalls.md`) created
  by claude-lab-luzo (Biggie), on Smalls' behalf during initial setup.
- 2026-08-04T16:58:07Z (Smalls): Notes system live -- confirmed reachable from Smalls too.
