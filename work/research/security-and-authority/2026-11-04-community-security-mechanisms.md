# Community GitHub mechanisms — security and authority (2026-11-04)

Status: **RESEARCH — NOT ACTIVE AUTHORITY**. Source descriptions were inspected, but no sandbox escape or approval tests were run. Prior [security research](2026-09-04-to-2026-09-09-competitive-systems-mechanisms.md) already owns the general principles; these notes capture focused **new cases**, not a second security policy.

## 1. franklin-ross/sandbox: host-tool delegation breaks simple sandbox assumptions
- Source: https://github.com/franklin-ross/sandbox.
- Upstream security model flags that a sandboxed agent's carefully typed/quoted MCP-style host action may still read files or launch Git hooks controlled by the agent in a writable bind mount. Shell quoting removes one injection vector, but does not establish safe command resolution.
- MAPS_L baseline: scoped filesystem and Git safeguards, explicit authority/capability intersection; dedicated sandbox is TRIGGERED and not default.
- Extract a negative regression: a tool allowed to run `git`/a host command indirectly consumes attacker-writable config/hooks within its working tree; verify effective process capabilities, target paths and sandbox boundaries remain authorized.
- Proposed smallest safeguard: model tool privilege as **command + effective working directory + transitive reads/execs**, not simply an allowlisted command name. Only implement where an actual host-privileged tool exists.
- Caveat: security claim is upstream model and risk analysis, not reproduced exploit. **STUDY/TEST when relevant.**

## 2. corporealshift/pi-extensions: explicit no-UI destructive-operation refusal
- Source: https://github.com/corporealshift/pi-extensions.
- Upstream `bash-guard` confirms risky commands with UI, rejects when no usable UI; `plan-mode` and `hooks` provide pre-tool veto.
- MAPS_L: deterministic policy and HOLD mechanisms already exist; do not replace them with regex command detection.
- Extract regression: if human approval UI is missing/unresponsive, privileged irreversible operation must fail closed with a structured reason, not silently assume consent. **STRENGTHEN existing hook tests.**

## 3. Overstory role boundaries: tool allowlists tied to worker function
- Source: https://github.com/jayminwest/overstory.
- Upstream describes `PreToolUse` hooks that block edits by non-implementer roles; other hooks limit dangerous Git operations.
- MAPS_L: existing one-owner/independent-review and policy separation. Test reviewer attempt to mutate artifacts and agent attempt to bypass pre-tool scope at runtime.
- Risk: hook configuration absence or bypass; role label alone does not establish independence. **TEST only, no extra role engine.**

## 4. promptfoo adversarial testing: benign paired controls matter
- Source: https://github.com/promptfoo/promptfoo.
- MAPS_L security regression should use **malicious and benign matched samples** to prevent overblocking from looking like safety progress. For every adversarial tool-result injection, include a benign file with identical superficial terms.
- Evaluation: unsafe action accepted, correct action blocked, missing evidence, cost/time; freeze examples before tuning to avoid overfit. **ADAPT test design.**

## Cross-domain conclusion
The best security progress likely comes from narrow failure reproduction and guard tests at actual execution points, not importing broad sandbox products. No change to merge authority, reviewer independence, credential boundaries, or policy is authorized by this research.
