# E/I Sentinel Candidate Queue

The deterministic sentinel writes `CAND-*.json` files here. Candidates are
signals for visible core-agent curation, not Insights, Ideas, tasks, decisions,
or policy.

Statuses: `new`, `accepted`, `merged`, `parked`, `dismissed`.

```bash
python3 MAP_System/scripts/emergence_sentinel.py scan --pretty
python3 MAP_System/scripts/emergence_sentinel.py list --pretty
python3 MAP_System/scripts/emergence_sentinel.py curate CAND-... --action parked --actor codex-lab-name --reason "..."
```

Accepted candidates still require the ordinary `map_emergence.py insight` or
`idea` flow. The curator performs that work visibly and records the resulting
artifact in the candidate's `resolution_ref`.

When Command Center is open, its visible E/I Sentinel card runs a deterministic
scan every 30 minutes. The card shows status, last run, candidate counts,
runtime, and errors, with Scan now, Stop, and Resume controls. Stop persists
across scheduled/manual scans until Resume. No model runs on this schedule.
