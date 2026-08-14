# Command Center Crash Investigation

Date: 2026-07-16
Status: Staged Command Center launch completed successfully; monitor for recurrence

## What happened

- The system journal stopped abruptly at approximately 09:28:57.
- The computer restarted at approximately 09:29:58 without a normal shutdown.
- On reboot, systemd reported that the journal had been uncleanly shut down.
- No kernel panic, out-of-memory event, overheating event, disk I/O error, or filesystem failure was recorded.

## Command Center correlation

- Command Center/WezTerm files were modified between 09:28:17 and 09:28:28.
- The lab watcher updated its state around 09:28:29.
- Hcom recorded Codex, Claude, Pi, and Librarian lab agents launching around 09:29:11.
- This makes the full AI Command Center Lab launch a credible trigger, although no project script was found deliberately rebooting or damaging the system.

## Suspected cause

The most likely explanation is an NVIDIA GPU or driver hard lock exposed by launching a new GPU-accelerated WezTerm window and several agents simultaneously.

The NVIDIA kernel modules loaded after reboot. An initial `nvidia-smi` check from a restricted diagnostic sandbox could not communicate with the RTX 2060 SUPER because that sandbox did not expose `/dev/nvidia*`; this was not a host GPU failure.

A host-level check at approximately 09:45 succeeded. The RTX 2060 SUPER was visible with driver 595.71.05, 111 MiB in use, a temperature of 37 C, and normal desktop processes attached. The installed NVIDIA userspace packages, loaded kernel module, and running kernel all match. The boot log still contains an NVIDIA USB-C/UCSI I2C timeout, but it did not prevent normal GPU operation.

The original abrupt restart therefore remains consistent with a transient GPU/driver hard lock, but the GPU is no longer stuck after reboot. The investigation has not established that Command Center itself deliberately rebooted the machine.

## Next steps

1. Keep important work saved and do not launch the full lab all at once yet.
2. Launch one ordinary WezTerm window without agents and confirm the desktop remains responsive.
3. Run one agent, then add the remaining agents one at a time while watching GPU state with `watch -n 2 nvidia-smi` from an ordinary host terminal.
4. Record the exact component and time if the display freezes or the machine resets again.
5. If another hard lock occurs, boot kernel 6.17.0-35 (or 6.14.0-29) from GRUB and repeat the same staged test before reinstalling the NVIDIA driver.
6. Treat `nvidia-gpu ... i2c timeout error e0000000` / `ucsi_ccg ... failed -110` as a secondary lead, especially if USB-C or DisplayPort behavior is involved.

## Verification after reboot

- Boot time: 2026-07-16 09:39:33
- Running kernel: 6.17.0-40-generic
- NVIDIA driver and firmware: 595.71.05
- Host `nvidia-smi`: successful at approximately 09:45
- GPU: NVIDIA GeForce RTX 2060 SUPER, 8192 MiB
- Temperature at verification: 37 C
- Previous kernels available for comparison: 6.17.0-35-generic and 6.14.0-29-generic

## Staged launch result

A staged reproduction test was completed between approximately 09:46 and 09:49:

1. Opened a plain WezTerm window with no agents.
2. Started one Codex agent. It initially stopped at an update prompt; the update was skipped and the agent reached its ready prompt.
3. Started the Claude lab wrapper and confirmed the agent was listening.
4. Started the Pi lab wrapper and confirmed the agent was active/listening.
5. Started the Librarian lab wrapper and confirmed it was active.

The stages used separate WezTerm windows rather than invoking the all-at-once launcher, so each addition could be observed independently. No freeze, restart, NVIDIA Xid, PCIe error, or new kernel GPU error occurred.

GPU observations:

- Plain WezTerm: 37 C, 129 MiB VRAM, approximately 16 W
- Codex and Claude present: 37 C, 146 MiB VRAM, approximately 16 W
- After Pi started: 40 C, 5119 MiB VRAM, approximately 42 W
- All staged roles present: 41-43 C, 6693 MiB VRAM, approximately 18-21 W across final samples

The large VRAM increase correlates with Pi/local-model activity, but temperatures and power remained normal. The original failure was not reproduced. Continue ordinary use while keeping this record; if the hard lock recurs, compare against the available older kernels and capture the exact launch stage and timestamp.

Project investigated:

`/home/mellow/Documents/Projects/MultiAgentProject-main`
