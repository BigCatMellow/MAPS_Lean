# MAP Delivery Note — TASK-275 (CommandCenterUI loopback consolidation)

Uses the TASK-219 delivery-note format: one combined evidence document.
An independent review record stays separate (medium/high-risk lane).

## ⚠ External edit — the boundary gate, and how each element was satisfied

This task edited a file **outside the canonical MAP repo**. All six elements
required by `artifacts/planning/commandcenterui-boundary-decision.md`:

| # | Element | How it was satisfied |
|---|---|---|
| 1 | Explicit operator approval naming the external path | Given **directly by bigboss in session**, 2026-07-23, quoted verbatim below — not relayed |
| 2 | Output path | `/home/mellow/Projects/CommandCenterUI/app/server.py` and only that file, plus this note inside the MAP repo for evidence |
| 3 | Outside-scope note | CommandCenterUI is a separate codebase with its own runtime and restart lifecycle, outside MAP's normal writable scope |
| 4 | Validation plan | Defined in the task and executed below — restart, discovery, helper launch, and the ambient-env negative test |
| 5 | Read-only vs write-capable | **Neither.** Internal refactor of an existing surface. No new controls, no new endpoints, so the write-control spec requirement does not apply |
| 6 | Write-control spec | **N/A** — not write-capable control work |

Operator approval, verbatim:

> Approved: claude-lab-zaro may edit
> /home/mellow/Projects/CommandCenterUI/app/server.py to consolidate the three
> loopback constants behind one config point. No behaviour change, no remote
> support, no new controls.

**Provenance note.** This approval was first offered to me second-hand via
claude-lab-bima, and I declined to act on it, asking the operator to state it
directly instead. Earlier the same day I had refused to treat a relayed *policy*
decision as an *edit* approval, and accepting a relayed edit approval hours later
would have made that a preference rather than a standard. I had also just
reported that an unratified proposal became binding policy by citation. Recording
"operator approved" in canonical state on a relay is that same move. The
approval above is the operator's own words, typed directly.

## Change summary

- Risk lane: SECURITY / STRUCTURAL — a data-egress boundary in a running
  operator surface, in an external repo
- Why it exists: **DEC-029** permits a remote `OLLAMA_HOST` only as explicit,
  UI-visible configuration and keeps ambient env inheritance forbidden. Three
  separate hardcoded sites made the eventual second-machine change expensive
  and likely to be done in a hurry by someone who reverts the hardening to make
  it work. This is a no-behaviour-change refactor whose entire value is making
  that future change small and reviewable.
- What changed: one new constant `OLLAMA_HOST_PORT = "127.0.0.1:11434"`, with
  all three call sites resolving from it.

| Site | Before | After |
|---|---|---|
| `OLLAMA_URL` (was line 100) | `"http://127.0.0.1:11434"` | `f"http://{OLLAMA_HOST_PORT}"` |
| launched local helper (was line 424) | `env["OLLAMA_HOST"] = "127.0.0.1:11434"` | `env["OLLAMA_HOST"] = OLLAMA_HOST_PORT` |
| model discovery (was line 846) | `env["OLLAMA_HOST"] = "127.0.0.1:11434"` | `env["OLLAMA_HOST"] = OLLAMA_HOST_PORT` |

- What deliberately did **not** change: no remote support, no new endpoints, no
  new controls, no UI change, no behaviour change of any kind. The existing
  security comments were kept and consolidated at the configuration point.

## Scope discipline

The approval and the task both bounded this to three sites plus one constant.
The diff is **27 changed lines, of which only 7 are code** — 3 removed, 4 added:

```
+ OLLAMA_HOST_PORT = "127.0.0.1:11434"
+ OLLAMA_URL = f"http://{OLLAMA_HOST_PORT}"
+     env["OLLAMA_HOST"] = OLLAMA_HOST_PORT
+         env["OLLAMA_HOST"] = OLLAMA_HOST_PORT
- OLLAMA_URL = "http://127.0.0.1:11434"
-     env["OLLAMA_HOST"] = "127.0.0.1:11434"
-         env["OLLAMA_HOST"] = "127.0.0.1:11434"
```

Everything else is comment. Nothing was touched opportunistically. Exactly one
hardcoded `127.0.0.1:11434` literal remains in the file, and it is the
configuration point itself.

File integrity: sha256 `eb6fca40…073977` before, `1fd4d689…53429e` after;
2396 → 2415 lines (net +19, all comment).

## Verification

The decisive property is criterion 2 — that the configuration point does **not**
read an ambient `OLLAMA_HOST`. It was proven by running, not asserted. The test
sets `OLLAMA_HOST=192.0.2.99:1`, a TEST-NET-1 address that is unroutable by
definition: if the ambient value were inherited, `ollama list` could not reach a
model and discovery would return zero.

| Check | Command | Result |
|---|---|---|
| Ambient env does not redirect (**new code**) | `OLLAMA_HOST=192.0.2.99:1` → `ollama_models()` | **10 models discovered**; `OLLAMA_HOST_PORT = 127.0.0.1:11434`, `OLLAMA_URL = http://127.0.0.1:11434` |
| Control — identical test on **pre-edit** code | same, against the pre-edit copy | **10 models, identical names** → no behaviour change |
| Clean environment (no ambient var) | `ollama_models()` | **10 models** → unchanged |
| Server starts cleanly | `server.py --host 127.0.0.1 --port 8799` with bogus ambient host | **HTTP 200** on `/` |
| Syntax | `python -m py_compile` | OK |
| No ambient reads remain | grep for `environ.*OLLAMA` / `getenv.*OLLAMA` | **none** |

Model names matched exactly between pre-edit and post-edit runs
(`deepseek-r1:8b`, `llama3.2:1b`, `nomic-embed-text:latest`,
`qwen2.5-coder:1.5b`, `qwen2.5-coder:1.5b-16k`, `qwen2.5-coder:7b`, …).

Overall: **PASS**.

### The operator's running instance was not disturbed

A live instance (pid 423223) was already serving on port 8765 when this work
started. It was **not** restarted. The startup check ran a separate throwaway
instance on port 8799, which stopped cleanly; port 8765 answered HTTP 200
before, during, and after.

**Consequence the reviewer and operator should both know:** the running UI is
still executing the pre-edit code and will pick up this change on its next
restart. That is safe precisely because the change is behaviour-neutral — the
control run above shows pre-edit and post-edit produce identical results — but
it does mean "verified" here means verified against a fresh process, not against
the operator's live one. Restarting an operator's working surface without asking
is not a decision this task had approval for.

### Not directly exercised

The launched-local-helper path (former line 424) sets `OLLAMA_HOST` on a
subprocess environment for an agent launch. Actually launching an agent to
observe it would have started a real terminal session, so it was verified
statically: the site now assigns the same `OLLAMA_HOST_PORT` constant that the
two dynamically-tested paths resolve from, and that constant is proven to equal
loopback. Stated plainly rather than implied as tested.

## Acceptance-criteria mapping

| # | Criterion | Evidence | Status |
|---|---|---|---|
| 1 | All three sites resolve from one config point defaulting to `127.0.0.1:11434` | table above; line numbers re-verified at edit time (100/424/846 → 116-117/442/865) | MET |
| 2 | Config point does not read ambient `OLLAMA_HOST`, proven by running | unroutable-host test, 10 models discovered | MET |
| 3 | No behaviour change — clean start, discovery works, helper targets loopback | control run identical; HTTP 200; helper path static (see above) | MET |
| 4 | No remote support, endpoints, controls, or changes outside the consolidation | 7 code lines, all three sites; one literal remains | MET |
| 5 | DEC-029 referenced in the code comment | comment at the configuration point cites DEC-029 and its rationale | MET |
| 6 | TASK-219 template; independent reviewer, not zaro and not bima | this note; review routed separately | MET |

## Reversibility

Single-file, seven code lines, semantically identical. Pre-edit copy retained in
the session scratchpad with its sha256 recorded above. Reverting is restoring
three string literals.

Owner / implemented by: claude-lab-zaro
Approved for external edit by: bigboss (operator), directly, 2026-07-23
Verified at: 2026-07-23
