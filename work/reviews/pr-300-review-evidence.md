reviewer: pr300review-demo
head_sha: 750ea7134622744e5d95a3d1ba9c57d69c21b8dc
independent: true
verdict: APPROVE
summary: |
  Documentation-only PR, verified against `gh pr diff 300` and a fresh clone
  (not the author's or coordinator's checkout). Diff touches exactly two new
  files: work/ideas/2026-09-05-revalidation-review-tier-s-ancestor-check-never-fires-on-a-p-IDEA-fe6c0f0f.md
  and work/notes/2026-09-05-dec003-known-bugs-followup.md. No runtime/,
  scripts/, tests/, or playbook/ paths touched.

  Emergence record: `scripts/emergence.py list` on the PR branch shows
  IDEA-fe6c0f0f present and well-formed; its own "## Promotion" section
  explicitly states "Not promoted" (promotion is a separate deliberate
  step per playbook/TASK_LIFECYCLE.md, correctly not performed here).

  Known-bugs note: both bugs (HcomAdapter.environment() HCOM_DIR
  override; tag-prefix vs bare-instance-name mismatch in
  _stopped_records_from_events) are described as observed/not-confirmed
  and explicitly "not fixed" / "for future pickup" -- no fix is claimed or
  attempted, no runtime code is included or modified, consistent with the
  file's own "Disposition" section.

  work/README.md already generically indexes both ideas/ and notes/ as
  directories (lines 26, 28) -- this PR adds files within existing
  indexed directories, not a new directory type (unlike PR #298's new
  subdirectory), so no index update was required.

  CI: `test` workflow was pending at review time; `review-evidence` check
  was failing only because this evidence file did not yet exist (expected
  pre-review state). No blocking issues found.
