# Nexus Verification

This document records local verification procedures for Nexus work. The first
procedure preserves the plan 0002 boot checks as repeatable regression tests
before merging the 0002 branch.

This smoke test is not the whole future test strategy. New runtime, data,
build, save, movement, topology, or UI changes should add verification
procedures that match their actual risk.

## Scope

The first verification pass tests the actual behavior changed by plan 0002:

- `NEXUS` builds load `nexus-dungeon.lua` and start on the handcrafted Nexus
  level.
- non-`NEXUS` builds still load upstream `dungeon.lua` and start on Dlvl 1 in
  the Dungeons of Doom.

DLB packaging is not part of this first pass.

## Pseudo-Terminal Smoke Tests

NetHack's tty window port expects a real terminal interface. A normal pipe is
not enough because tty rendering uses cursor movement, terminal size, terminal
modes, and single-key input.

The repo-local smoke runner is:

```sh
_work/tools/nh-pty-smoke.py
```

It creates a pseudo terminal, sets the terminal size to 80x25 by default,
launches a NetHack command, waits for required text, optionally sends `#quit`,
confirms the quit prompt, and fails on timeout or missing text. The default
timeout is 10 seconds; use `--timeout` for slower diagnostic runs.

Use unique character names for smoke tests so old saves and locks do not affect
the result.

Write transient smoke-test captures under:

```text
_work/verification-runs/
```

That directory is ignored except for its `.gitignore`; keep raw terminal logs
there rather than in `/tmp` so a later session can inspect the most recent
local run while avoiding accidental commits.

## Nexus-Enabled Boot

Build and install the Nexus local profile:

```sh
sh sys/unix/setup.sh sys/unix/hints/nexus-local
make clean
make all
make install
```

Use `make clean` when switching hints profiles. The generated makefiles can
change compile flags without forcing every object to rebuild; plan 0006 caught
this when a stale `dungeon.o` kept non-NEXUS behavior after switching to
`nexus-local`.

Run the installed Nexus launcher through the pty smoke harness:

```sh
_work/tools/nh-pty-smoke.py \
  --expect "Hello NxsT0001" \
  --expect "Dlvl:1" \
  --forbid "Dungeons of Doom" \
  --after-expect-send "#overview\r" \
  --post-expect Nexus \
  --quit \
  --log _work/verification-runs/nexus-local.log \
  -- ~/.local/bin/nexus -u NxsT0001-Arc-Hum-Mal-Law
```

Expected result:

- the command exits successfully
- the screen reaches the level display
- `#overview` reports `Nexus`
- the screen does not contain `Dungeons of Doom`
- `#quit` is accepted and the process exits cleanly

## NEXUS-Disabled Boot

Build and install the minimal Linux profile:

```sh
sh sys/unix/setup.sh sys/unix/hints/linux-minimal
make clean
make all
make install
```

This profile does not currently install `sysconf`, but `SYSCF` is enabled by
default in this NetHack tree. Until the profile is adjusted, copy the sysconf
file into the minimal playground before running the smoke test:

```sh
cp sys/unix/sysconf ~/nethack-minimal/games/lib/nethackdir/sysconf
```

Run the installed minimal wrapper through the pty smoke harness:

```sh
_work/tools/nh-pty-smoke.py \
  --expect "Hello NhT0001" \
  --expect "Dlvl:1" \
  --forbid "Nexus" \
  --after-expect-send "#overview\r" \
  --post-expect "Dungeons of Doom" \
  --quit \
  --log _work/verification-runs/linux-minimal.log \
  -- ~/nethack-minimal/games/nethack -u NhT0001-Arc-Hum-Mal-Law
```

Expected result:

- the command exits successfully
- the screen contains `Dungeons of Doom`
- the screen contains `Dlvl:1`
- the screen does not contain `Nexus`
- `#quit` is accepted and the process exits cleanly

## Wizard Mode

Wizard mode is a developer verification tool. It should be available for local
Nexus testing so developers can inspect topology, level placement, objects, and
later Nexus-specific world assumptions.

The Nexus local build uses `SYSCF`, so wizard mode access is controlled by the
installed `sysconf` `WIZARDS` setting. Nexus local development uses
`CHECK_PLNAME=1`, so the wizard-mode command supplies the authorized player
name `games`.

The initial wizard-mode procedure only verifies access. More useful wizard
mode tests will need strategic inputs once there is behavior worth probing,
such as moving toward a monster, wishing for an object, or inspecting branch
state.

```sh
_work/tools/nh-pty-smoke.py \
  --expect "Hello wizard" \
  --expect "Dlvl:1" \
  --forbid "Entering explore/discovery mode instead" \
  --quit \
  --log _work/verification-runs/wizard-mode.log \
  -- ~/.local/bin/nexus -u games -D -p Arc -r Hum -@
```

In wizard mode, NetHack changes the player name to `wizard` after
authorization, so the expected greeting remains `Hello wizard`.

## Failure Signals

Treat any of these as a failed verification:

- build or install command fails
- pty smoke test times out
- required text is missing
- forbidden text appears
- `#quit` cannot exit cleanly
- an old save or lock changes the startup path
- a NEXUS-disabled build reaches `Nexus`
- a NEXUS-enabled build reaches the Dungeons of Doom
