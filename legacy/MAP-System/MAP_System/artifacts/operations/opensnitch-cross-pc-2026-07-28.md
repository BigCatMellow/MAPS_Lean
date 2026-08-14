# TASK-301 OpenSnitch Cross-PC Operations Record

- status: verified
- host_checked: KUDU (`192.168.1.177`)
- peer: RUKI / MediaCenter (`192.168.1.153`)
- opensnitch_version: `1.5.8`
- opensnitch_unit: `opensnitch.service`
- peer_opensnitch: not installed

## Baseline

- `opensnitch.service` was enabled and active on KUDU.
- `/etc/opensnitchd/default-config.json` used `DefaultAction: allow` and
  `InterceptUnknown: false`.
- Existing permanent process-wide allow rules already covered `/usr/bin/ssh`
  and `/home/mellow/.local/bin/hcom`.
- Existing OpenSnitch rules are user-owned state and are not removed or
  rewritten by this task.

## Managed Rules

- `map-kudu-ruki-ssh`: allow only `/usr/bin/ssh` to `192.168.1.153:22`.
- `map-kudu-hcom-relay`: allow the exact installed `hcom` path. Relay broker
  addresses are dynamic, so destination IP pinning would cause avoidable
  outages.
- Both rules are outbound application rules. They do not open an inbound port.

## Verification

- `python3 -m unittest MAP_System.tests.test_install_opensnitch_rules -v`:
  3 tests passed.
- `python3 MAP_System/scripts/install_opensnitch_rules.py --check`:
  2 templates validated.
- Privileged installation reported `changed=2 unchanged=0`; both installed
  files parse as JSON and have mode `0644`.
- `opensnitch.service` restarted successfully at
  `2026-07-28 17:37:46 EDT`, is `enabled`, and is `active/running`.
- The post-restart journal reports `Loading rules from
  /etc/opensnitchd/rules` and no rule parsing error.
- The restricted `map-authority route` request to RUKI returned
  `version=1`, `ok=true`, and `returncode=0`.
- `hcom status` reported `relay: connected` and `relay-worker: running`.
- Live sockets after reload included:
  - `/usr/bin/ssh` from `192.168.1.177` to `192.168.1.153:22`.
  - `hcom` from `192.168.1.177` to the current relay endpoint on port `8883`.

## Known Observation

- OpenSnitch 1.5.8 logged several packet queue timeout lines immediately after
  restart. The service remained running and both protected connections
  succeeded afterward. These messages predated TASK-301 and are not rule parse
  failures.
