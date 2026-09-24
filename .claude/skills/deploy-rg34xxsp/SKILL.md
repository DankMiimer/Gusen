---
name: deploy-rg34xxsp
description: Put the current build of Gusen on the owner's Anbernic RG34XXSP (PortMaster) and read back what happened. Use when asked to deploy, install, or test on the handheld/device.
---

# Deploy to the RG34XXSP

1. Only deploy a build whose tests pass (`/playtest` first).
2. `python tools/deploy.py`: copies `port/Gusen.sh`, `port/gusen/` and `game/`
   (as `gusen/gamedata`, without tests) to `\\GAMEBOY\share\roms\ports`.
   Device saves are kept. Other target: `--ports <path>` or env `GUSEN_PORTS`
   (e.g. an SD card in a reader).
3. You can't press the handheld's buttons. Ask the owner to start **Gusen**
   from *Ports* (update the game list if it's new) and say what they see. Give
   them the checklist from `docs/HANDOFF.md` ("Not verified yet") that's still
   open.
4. Afterwards: `python tools/deploy.py --log` prints `gusen/log.txt` from the
   device (LÖVE errors, PortMaster output). Settings/saves are in
   `\\GAMEBOY\share\roms\ports\gusen\saves\love\gusen\`.
5. Update `docs/HANDOFF.md`: tick what was confirmed, note anything new.

If the share isn't reachable: the handheld must be on, on the same Wi-Fi, with
network sharing enabled. Don't guess other hosts or credentials; ask.
