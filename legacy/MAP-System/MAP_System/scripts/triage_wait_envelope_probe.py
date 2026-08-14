#!/usr/bin/env python3
"""Disposable triage-envelope probe (LURE, 2026-07-20).

Reconstructs "explainable wait" records from raw hcom signals only
(request messages + replies + agent life events). Never reads hcom's own
reqwatch notices, which are held out as labels. No authority or integration;
writes only the explicitly selected output artifact.
"""
import argparse
import json
import re
from datetime import datetime

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("input", help="Frozen hcom event JSONL input")
parser.add_argument(
    "--output",
    default="triage_envelope_records.json",
    help="Output records JSON path (default: %(default)s)",
)
args = parser.parse_args()

with open(args.input, encoding="utf-8") as source:
    evs = [json.loads(line) for line in source if line.strip()]
evs.sort(key=lambda e: e["id"])

def ts(e): return datetime.fromisoformat(e["ts"])
CORE = {"lure", "kiri", "lilo", "hana"}          # core agents seen this window
def short(mention: str) -> str:
    return mention.lstrip("@").split("-")[-1].lower()

# ---- raw signal extraction (ground truth notices deliberately excluded) ----
GT_MARK = ("went idle without responding", "stopped without responding")
msgs = [e for e in evs if e["type"] == "message"
        and not any(m in e["data"].get("text", "") for m in GT_MARK)]
life = [e for e in evs if e["type"] == "life"]

# agent -> ordered life transitions
def life_after(agent, t, action):
    return next((e for e in life if e["instance"] == agent
                 and e["data"].get("action") == action and ts(e) > t), None)

def replied(agent, t, requester=None, req_id=None):
    """First message from `agent` after t that actually reaches `requester`.

    A message merely sent by the agent to somebody else is NOT a response to
    this request. Directional evidence used, in order:
      1. explicit reply_to_local == req_id, or
      2. a delivery of that message to the requester
         (status context 'deliver:<agent>' recorded ON the requester).
    """
    for m in msgs:
        if m["instance"] != agent or ts(m) <= t:
            continue
        if req_id is not None and m["data"].get("reply_to_local") == req_id:
            return m
        if requester is None:
            return m
        for e in evs:                       # delivery of THIS message to requester
            if e["type"] != "status" or e["id"] <= m["id"] or e["id"] > m["id"] + 40:
                continue
            ctx = str(e["data"].get("context", ""))
            if (e["instance"] == requester and ctx.startswith("deliver:")
                    and short(ctx.split(":", 1)[1]) == short(agent)):
                return m
    return None

def live_at(agent, t):
    """Is agent ready (not stopped) as of time t?"""
    last = None
    for e in life:
        if e["instance"] == agent and ts(e) <= t and e["data"].get("action") in ("ready", "stopped"):
            last = e["data"]["action"]
    return last == "ready"

# ---- detect waits ----
records = []
for m in msgs:
    if m["data"].get("intent") != "request":
        continue
    sender = m["instance"]
    t0 = ts(m)
    # Recipients: hcom records delivery as a status event ON THE RECIPIENT with
    # context "deliver:<sender>". Correlate within a short window after send.
    # Upper-bound the window at the sender's NEXT message, otherwise deliveries
    # belonging to a later message get mis-attributed to this one.
    nxt = next((x["id"] for x in msgs
                if x["instance"] == sender and x["id"] > m["id"]), 10**9)
    recips = set()
    for e in evs:
        if e["type"] != "status" or e["id"] <= m["id"] or e["id"] >= nxt:
            continue
        ctx = str(e["data"].get("context", ""))
        if ctx.startswith("deliver:") and short(ctx.split(":", 1)[1]) == short(sender):
            recips.add(e["instance"])
    recips = {r for r in recips if r in CORE and r != sender}
    for a in recips:
        rep = replied(a, t0, requester=sender, req_id=m["id"])
        stop = life_after(a, t0, "stopped")
        # stranded == agent stopped before ever replying
        if rep and (not stop or ts(rep) <= ts(stop)):
            state, detect_at = "RESOLVED", ts(rep)
        elif stop:
            state, detect_at = "STRANDED", ts(stop)
        else:
            state, detect_at = "WAITING_ON_AGENT", None
        rec = {
            "request_id": m["id"], "requested_at": m["ts"], "owner": a, "requester": sender,
            "state": state,
            "detected_at": detect_at.isoformat() if detect_at else None,
            "latency_s": (detect_at - t0).total_seconds() if detect_at else None,
            "waiting_for": m["data"].get("text", "")[:110].replace("\n", " "),
        }
        if state == "STRANDED":
            # ---- the envelope's decision-relevant additions ----
            alts = sorted(x for x in CORE
                          if x not in (a, sender) and live_at(x, detect_at))
            rec |= {
                "why": f"{a} stopped at {detect_at.isoformat()} without responding",
                "resumes_when": f"{a} returns ready, or the request is rerouted",
                "reroute_candidates": alts,
                "timeout_action": (f"reroute to {alts[0]}" if alts
                                   else "no live non-author core agent; escalate to operator"),
                "impact": "requester blocked awaiting an independent response",
            }
        records.append(rec)

stranded = [r for r in records if r["state"] == "STRANDED"]
print(json.dumps({
    "total_requests_examined": sum(1 for m in msgs if m["data"].get("intent") == "request"),
    "wait_records": len(records),
    "resolved": sum(1 for r in records if r["state"] == "RESOLVED"),
    "stranded": len(stranded),
    "still_waiting": sum(1 for r in records if r["state"] == "WAITING_ON_AGENT"),
}, indent=2))
print("\n=== STRANDED (envelopes) ===")
for r in stranded:
    print(f"\nreq #{r['request_id']} owner={r['owner']} requested={r['requested_at']}")
    print(f"  detected_at   : {r['detected_at']}  (+{r['latency_s']:.0f}s)")
    print(f"  why           : {r['why']}")
    print(f"  reroute       : {r['timeout_action']}  candidates={r['reroute_candidates']}")
    print(f"  waiting_for   : {r['waiting_for'][:90]}")
with open(args.output, "w", encoding="utf-8") as destination:
    json.dump(records, destination, indent=2)
    destination.write("\n")
