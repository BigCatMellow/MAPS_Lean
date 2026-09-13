"""Fail CI when a durable handoff under `work/handoffs/` is unregistered, or
when a non-legacy registered handoff is missing its required receipt block.

Why this exists (CLAUDE.md rule 20 -- a repeating failure gets a mechanical
safeguard, not another reactive fix). PR #340 introduced the durable-handoff
register (`work/handoffs/README.md`) and required every new forward-looking
handoff to carry a receipt block near its top (`Handoff ID:` / `Handoff
status:` / `Reviewed:` / `Continued at:`), registered in the same change.
Nothing enforced it: the very next two handoffs written after #340 merged
(sessions 42 and 43, on `MAPS_Lean_Handoff_2026-09-*` files outside this
repo) both skipped the receipt, and it was only caught because a handoff-audit
pass happened to notice and flag it (fixed in #354). An internal insight
(`INSIGHT-bbb3b845`, written the same day as #340) had already predicted this
exact failure mode: a new standing register with no reconciliation owner
drifts. This check is that mechanical safeguard for the half of the problem
that lives inside git -- see `playbook/ROADMAP_TRAJECTORY_CHECK.md` for the
other half (the `/home/home` session-handoff files, which are outside any
repo and can never be CI-checked; the periodic trajectory check covers those).

What it checks, at HEAD, unconditionally (like the sibling safeguards in this
same workflow):

1. Every `*.md` file directly under `work/handoffs/` (excluding `README.md`
   itself) must be referenced by at least one row of the register table under
   the `## Register` heading. An unregistered handoff file is always a
   failure, legacy or not -- registration itself is required for every
   durable handoff (see the register's own "Legacy" rule 6).
2. For each such row whose Handoff ID does NOT start with `LEGACY-` (i.e. a
   handoff created under the new, forward-looking convention rather than
   grandfathered in by the original bulk-registration sweep), the handoff
   file itself must contain a `Handoff ID:` line and a `Handoff status:`
   line -- the required receipt. `LEGACY-*` rows are exempt: they predate the
   register and are deliberately not retrofitted (README.md's own Legacy
   rule 6 says do not bulk-guess or retrofit legacy handoffs).
3. When a receipt is present, its `Handoff ID:` value must match the ID the
   register uses for that file -- catches a copy-pasted or hand-edited ID
   drifting out of sync between the two locations.

Only scans `work/handoffs/*.md` at HEAD (mirrors how the sibling checks in
this workflow scan their whole target tree, not a PR diff) -- so this also
guards against a legacy file's row being edited to drop its `LEGACY-` prefix
without ever adding the receipt the new prefix would require.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
HANDOFFS_DIR = REPO_ROOT / "work" / "handoffs"
REGISTER_FILE = HANDOFFS_DIR / "README.md"

REGISTER_SECTION_RE = re.compile(r"^## Register\s*$", re.M)
RECEIPT_ID_RE = re.compile(r"^Handoff ID:\s*(\S+)", re.M)
RECEIPT_STATUS_RE = re.compile(r"^Handoff status:\s*(\S+)", re.M)
MD_FILENAME_RE = re.compile(r"([A-Za-z0-9_.\-]+\.md)")


def _parse_register_rows(register_text: str) -> dict[str, str]:
    """{handoff_id: handoff_cell_text} for every data row under '## Register'.

    Only the register table (below the '## Register' heading) is parsed --
    the '## Handoff lifecycle' table earlier in the same file uses the same
    '| `WORD` | ...' shape for its status-definition rows (e.g. '| `OPEN` |
    Handoff exists but ...') and must not be mistaken for real entries.
    """
    section_match = REGISTER_SECTION_RE.search(register_text)
    body = register_text[section_match.end():] if section_match else ""
    rows: dict[str, str] = {}
    for line in body.splitlines():
        line = line.strip()
        if not line.startswith("|") or not line.endswith("|"):
            continue
        cols = [c.strip() for c in line.strip("|").split("|")]
        if len(cols) < 3:
            continue
        hid = cols[0].strip("` ")
        if not hid or hid == "---" or hid == "Handoff ID":
            continue
        rows[hid] = cols[2]  # the "Handoff" column: link/filename to the file
    return rows


def scan(handoffs_dir: Path = HANDOFFS_DIR) -> list[str]:
    if not (handoffs_dir / "README.md").exists():
        return [f"{handoffs_dir}/README.md not found -- register missing entirely"]
    register_text = (handoffs_dir / "README.md").read_text(encoding="utf-8")
    rows = _parse_register_rows(register_text)

    filename_to_ids: dict[str, list[str]] = {}
    for hid, handoff_cell in rows.items():
        # A markdown link '[`x.md`](x.md)' repeats the filename (link text +
        # URL) -- dedupe per row so one row never yields the same id twice.
        cell_filenames = set(MD_FILENAME_RE.findall(handoff_cell))
        for filename in cell_filenames:
            filename_to_ids.setdefault(filename, []).append(hid)

    failures: list[str] = []
    md_files = sorted(
        p for p in handoffs_dir.glob("*.md") if p.name != "README.md"
    )
    for path in md_files:
        ids_for_file = filename_to_ids.get(path.name, [])
        if not ids_for_file:
            failures.append(
                f"work/handoffs/{path.name}: not registered in "
                "work/handoffs/README.md -- add a row under '## Register' "
                "per the Update Protocol (rule 1)."
            )
            continue

        text = path.read_text(encoding="utf-8")
        id_match = RECEIPT_ID_RE.search(text)
        status_match = RECEIPT_STATUS_RE.search(text)
        has_receipt = id_match is not None and status_match is not None

        for hid in ids_for_file:
            if hid.startswith("LEGACY-"):
                continue  # grandfathered: predates the register, no receipt required
            if not has_receipt:
                failures.append(
                    f"work/handoffs/{path.name}: registered as `{hid}` (a "
                    "non-legacy handoff) but is missing the required receipt "
                    "block ('Handoff ID:' and 'Handoff status:' lines near "
                    "its top -- see README.md's 'Required receipt' section)."
                )
            elif id_match.group(1) != hid:
                failures.append(
                    f"work/handoffs/{path.name}: its own receipt says "
                    f"'Handoff ID: {id_match.group(1)}' but the register "
                    f"lists it as `{hid}` -- these must match."
                )
    return failures


def main() -> int:
    failures = scan()
    if failures:
        print("Handoff receipt/registration check failed:\n")
        print("\n\n".join(f"- {f}" for f in failures))
        return 1
    print("check_handoff_receipts: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
