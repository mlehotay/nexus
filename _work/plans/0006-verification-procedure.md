# 0006 - Verification Procedure

## Goal

Develop a repeatable Nexus verification process, starting with regression
coverage for the `0002-boot-custom-level` branch before it is merged.

The immediate purpose is to preserve the checks from codex-0019 as durable
developer procedure instead of one-off session output.

## Branch Context

This plan is developed on `work-0006-verification-procedure`, stacked from
`work-0002-boot-custom-level`.

That branch shape is intentional:

- `0002` owns the first custom boot implementation.
- `0006` owns the verification procedure and any test harness or workflow
  documentation.
- `0006` should test the exact 0002 state before 0002 is merged.
- If testing finds a defect in the 0002 implementation, fix it on the 0002
  branch when practical, then update this stacked branch.

Integration order should normally be:

1. finish and commit the 0002 implementation branch;
2. run the 0006 procedure against 0002;
3. merge 0002 into `nexus`;
4. rebase or merge 0006 onto updated `nexus`;
5. merge 0006 when its documentation or harness is ready.

## Scope

In scope:

- document the Nexus local verification procedure
- preserve the codex-0019 boot smoke test as repeatable regression coverage
- define how pseudo-terminal testing works for the tty window port
- verify both sides of the 0002 `NEXUS` guard: Nexus-enabled boot and
  non-Nexus vanilla boot
- verify that wizard mode is accessible for developer testing; deeper wizard
  mode scenarios can wait until there is behavior worth probing with strategic
  inputs
- identify the smallest useful automated or semi-automated harness
- record practical setup assumptions, command lines, expected outputs, and
  failure signals

Out of scope:

- gameplay design
- procedural generation
- broad CI design before local verification is understood
- replacing NetHack's tty window port
- changing the 0002 runtime implementation except when verification exposes a
  defect that must be fixed on the 0002 branch

## Regression Targets From 0002

The first regression suite should cover the behavior verified in codex-0019:

- `sys/unix/hints/nexus-local` builds with `NEXUS` enabled
- `make all` succeeds
- `make install` installs the Nexus runtime data
- the installed `nexus` launcher or binary starts
- the player starts on the handcrafted `dat/nexus-start.lua` level
- tty rendering displays the handcrafted map
- input is accepted
- the location/status reports `Nexus`
- quitting exits cleanly

The same suite should also cover the non-Nexus side of the guarded 0002 change:

- `sys/unix/hints/linux-minimal` builds with `NEXUS` disabled
- the non-Nexus build still selects `dungeon.lua`, not `nexus-dungeon.lua`
- the player starts on Dlvl 1 in the Dungeons of Doom with `NEXUS` disabled
- tty rendering, input, and clean quit still work in the non-Nexus boot path

`sys/unix/hints/nexus-local` currently defines `NEXUS`, so it is not a
NEXUS-disabled regression target by default. If Nexus needs a local
NEXUS-disabled build with the same install layout as `nexus-local`, plan 0006
should decide whether to use a temporary build override or add a separate
non-Nexus local hints profile.

These checks should be treated as regressions for future topology, Lua level,
build profile, and install changes.

## Pseudo-Terminal Testing

The tty window port expects to run inside a terminal. A plain pipe does not
fully model terminal behavior because tty rendering uses cursor movement,
screen dimensions, terminal modes, and interactive keystrokes.

A pseudo terminal, or pty, gives the game a controlled fake terminal. A test
harness can use it to:

- set a stable terminal size, initially 80x25
- launch the installed `nexus` command
- send startup, movement, and quit keystrokes
- capture the rendered screen or transcript
- assert that expected text appears, such as `Nexus`
- fail if the process hangs, panics, or exits with the wrong status

The first harness may be a small local script, but it should be explicit enough
that another session can rerun it without reconstructing the interaction from
memory.

## DLB Coverage

DLB testing is out of scope for the first 0006 pass. The current target is to
test the actual behavioral surface changed by 0002: choosing
`nexus-dungeon.lua` when `NEXUS` is enabled, and preserving the vanilla
`dungeon.lua` path when `NEXUS` is disabled.

Future packaging work may add DLB tests, but they should not block the initial
0002 verification procedure.

## Wizard Mode

Wizard mode is a developer verification tool for Nexus. It should be available
in local developer installs so testers can inspect topology, movement, object
placement, level transitions, and later Nexus-specific world assumptions.

The first procedure should verify only that `nexus -D` enters actual debug mode
rather than being denied and downgraded to explore mode. Because the Unix build
uses `SYSCF`, this depends on the installed `sysconf` `WIZARDS` setting.
Behavioral wizard-mode tests can be added later when Nexus has specific
developer scenarios to exercise.

Initial wizard-mode checks:

- document how local `sysconf` authorizes wizard mode
- launch `nexus -D` through a pty
- assert that debug mode is available
- quit cleanly without leaving test saves behind

Later wizard-mode checks may cover controlled wishing, level inspection, level
teleport, or debug commands once those commands are selected as standard Nexus
developer tools.

## Acceptance Criteria

- `_work/workflow.md` explains how to use stacked verification branches
- this plan records that 0006 is stacked from the 0002 branch under test
- a repeatable manual or scripted smoke-test procedure exists for the 0002 boot
  regression targets
- the procedure explains what a pseudo terminal is and why tty tests need one
- Nexus-enabled and NEXUS-disabled boot paths are both tested
- DLB testing is explicitly deferred from the first 0006 pass
- wizard-mode access is documented and verified, or a blocker is recorded
- any intentional upstream divergence discovered while enabling verification is
  recorded in `_work/divergences.md`

## Status

Done.

## Progress

2026-05-22:

- Created this plan on a verification branch stacked from the 0002 boot branch.
- Documented the branch model in `_work/workflow.md`.
- Captured the codex-0019 boot checks as explicit regression targets.

2026-05-23:

- Narrowed the first verification pass to the actual 0002 guard behavior.
- Added explicit NEXUS-disabled regression targets for `linux-minimal` and
  vanilla Dungeons of Doom startup.
- Deferred DLB testing from the initial 0002 verification scope.
- Added `_work/verification.md` and `_work/tools/nh-pty-smoke.py`.
- Documented that profile switching needs `make clean`; otherwise stale object
  files can preserve the previous `NEXUS` state.
- Verified `nexus-local` NEXUS-enabled boot: clean build, install, pty launch,
  handcrafted level display, `#overview` reports `Nexus`, and `#quit` exits
  cleanly.
- Verified `linux-minimal` NEXUS-disabled boot after installing the required
  `sysconf`: clean build, install, pty launch, `#overview` reports
  `Dungeons of Doom`, `Nexus` is absent, and `#quit` exits cleanly.
- Initially found the wizard-mode blocker: `sysconf` allowed only
  `root games`, so `nexus -D` was denied for the normal developer user and
  fell back to explore mode.
- Lowered the pty smoke harness default timeout to 10 seconds.
- Enabled `CHECK_PLNAME=1` in `sys/unix/sysconf` so wizard mode can use the
  upstream-style `WIZARDS=root games` list with `nexus -u games -D`; the first
  wizard-mode check remains access-only.
- Verified access-only wizard mode: `nexus -u games -D -p Arc -r Hum -@`
  starts as `wizard`, reaches Dlvl 1, does not fall back to explore mode, and
  quits cleanly.
- User confirmed closure after 0002 and 0006 were merged into `nexus`.
