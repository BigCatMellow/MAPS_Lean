# Insight Record

Insight ID: INS-0037
Project: MAP
Related task: NONE
Detected by: claude-lab-niko
Date: 2026-07-21
Status: RAW

## Short description


- obs: obs: a newly spawned agent can hang on a host firewall approval prompt while hcom still reports it 'active', and connectivity tests from the parent agent all pass and mislead the diagnosis

## Trigger


- src: exp263-freeze-lavi sat at 'Unable to connect to API (ENOTFOUND) - Retrying, attempt 4/10' and never executed a single tool call. hcom list reported it as 'active' the whole time. Operator later explained the host firewall was holding the new process's first outbound connection pending their approval, and they were away from keyboard.

## The synthesis


- synth: A newly spawned agent's first API call can block on a per-process host firewall prompt. The symptom is an ENOTFOUND retry loop inside the agent, while hcom reports the agent as 'active' because the process is alive. Connectivity tests run from an ALREADY-APPROVED process (such as the spawning agent) all pass, which actively misleads the diagnosis toward 'transient network blip'. The distinguishing check is not DNS or curl from the parent -- it is whether the new agent has completed any successful call at all.

## Why it might matter


- why: This produced a wrong diagnosis and an unnecessary kill/respawn tonight. It also explains a general class of 'agent spawned but never started' failures, and it means spawning agents is not actually unattended: it can require the operator at the keyboard. Anyone planning overnight or batch agent work needs to know that.

## Evidence


- ev: exp263-freeze-lavi terminal at attempt 4/10 with zero tool calls; hcom list status 'active' throughout; getent + curl from claude-lab-niko showing api.anthropic.com reachable over both IPv4 (160.79.104.10) and IPv6 in <100ms; operator statement 2026-07-21 that the firewall required approval while they were away.

## Risk


- risk: Acting on this insight by auto-approving firewall prompts would trade an observability gap for a security hole. The fix direction is detection and signalling, not automatic approval.

## Scope


- scope: Only the files and artifacts named in this record.

## Recommended next action

- [ ] ignore
- [ ] park
- [ ] task
- [ ] idea
- [ ] experiment
- [ ] escalate-human

## Notes

- note:
