# Nexus Codex Log

Concise append-only summaries for Codex sessions.

Use this when a session changes source files, closes a task, records findings
that future sessions need, or establishes project setup.

Entry shape:

```text
---

# codex-NNN - Short Title

**Plan:** `plan-id`
**Status:** recorded
**Timestamp:** YYYY-MM-DD HH:MM TZ

## Changes

...
```

---

# codex-001 - Work Surface Setup

**Plan:** `0001-environment-setup`
**Status:** recorded
**Timestamp:** 2026-05-20 02:20 EDT

## Changes

Created the initial Nexus `_work/` coordination surfaces.

Changed files:

- `_work/README.md`
- `_work/workflow.md`
- `_work/tasks.csv`
- `_work/codex-log.md`
- `_work/divergences.md`
- `_work/plans/README.md`
- `_work/plans/plans.csv`
- `_work/plans/0001-environment-setup.md`
- `_work/plans/0002-boot-custom-level.md`

Recorded that Nexus is a separate derivative from Floating Eye and should use
Floating Eye only as a workflow reference.

---

# codex-002 - Nexus Local Install Profile

**Plan:** `0001-environment-setup`
**Status:** recorded
**Timestamp:** 2026-05-20 18:45 EDT

## Changes

Added a Nexus-specific Unix hints file for local developer installs.

Changed files:

- `sys/unix/hints/nexus-local`
- `_work/install.md`
- `_work/README.md`
- `_work/workflow.md`
- `_work/tasks.csv`

The new hint installs Nexus under `~/games/nethack/nexus/` and copies
`sys/unix/sysconf` into the install root. This keeps Nexus separate from other
local NetHack derivatives and avoids using the ambiguous `nethack` launcher.

Created the local launcher:

- `~/.local/bin/nexus`

Verified `nexus --version` reports NetHack 5.0.0.

---

# codex-003 - Isolated Nexus Runtime Defaults

**Plan:** `0001-environment-setup`
**Status:** recorded
**Timestamp:** 2026-05-20 20:05 EDT

## Changes

Isolated Nexus from the user's shared NetHack defaults and fixed local save
compression for this install profile.

Changed files:

- `sys/unix/hints/nexus-local`
- `sys/unix/nexus.nethackrc`
- `_work/install.md`
- `_work/tasks.csv`
- `_work/codex-log.md`
- `_work/divergences.md`

`nexus-local` now compiles with `/bin/gzip` and `.gz` save compression instead
of the upstream `/usr/bin/compress` default, installs `nexus.nethackrc` beside
`sysconf`, and the `~/.local/bin/nexus` wrapper exports
`NETHACKOPTIONS=@.../nexus.nethackrc`.

Verified:

- `make all`
- `make install`
- `nexus --version`
- pseudo-terminal smoke test reaches the NetHack 5.0.0 character prompt
- throwaway `codextest` game saves as `1000codextest.gz`

---

# codex-004 - Durable Layout And Session Commands

**Plan:** `0001-environment-setup`
**Status:** recorded
**Timestamp:** 2026-05-20 20:15 EDT

## Changes

Documented where Nexus-specific files belong and made the Codex wrap-up and
commit commands explicit.

Changed files:

- `AGENTS.md`
- `_work/nexus-layout.md`
- `_work/README.md`
- `_work/workflow.md`
- `_work/codex-log.md`

`nexus-layout.md` records repository layout conventions. It was later moved
into `_work/` while the setup policy remained provisional.

`AGENTS.md` and `_work/workflow.md` now define:

- `wrap up` / `finish the session`
- `commit this session`

These commands require workflow maintenance, verification reporting, and
keyword-aware NetHack commits via `git nhadd` and `git nhcommit` when source,
data, doc, or build files are involved.

---

# codex-005 - Developer Guide And Keyword Substitution Notes

**Plan:** `0001-environment-setup`
**Status:** recorded
**Timestamp:** 2026-05-20 20:45 EDT

## Changes

Added a Nexus developer guide covering repository workflow, file location
policy, local build orientation, divergence records, and the NetHack
keyword-substitution system.

Changed files:

- `_work/nexus-dev-guide.md`
- `_work/nexus-layout.md`
- `_work/codex-log.md`

The guide records the Nexus convention for NetHack headers: leave untouched
upstream `$NHDT-...$` headers alone, but convert the first-line header to
`$FLEY-...$` when a Nexus commit intentionally changes a NetHack-owned file
handled by `NHSUBST`. New Nexus-owned source files should start with FLEY
variables and be staged with `git nhadd`.

It also explains the branch workflow: short feature branches start from
`nexus`, then merge back into `nexus`; they do not branch from the official
NetHack 5.0.0 tag during ordinary feature work.

---

# codex-006 - Configuration Procedures Plan

**Plan:** `0003-configuration-procedures`
**Status:** opened
**Timestamp:** 2026-05-21

## Changes

Left `0001-environment-setup` closed and opened
`0003-configuration-procedures` for the remaining developer workflow, player
terminal setup, runtime configuration, and procedure work.

Changed files:

- `_work/plans/plans.csv`
- `_work/plans/0003-configuration-procedures.md`
- `_work/workflow.md`
- `AGENTS.md`
- `_work/codex-log.md`

Workflow instructions now say plans cannot be marked `done` unless the user
explicitly asks for that plan to be closed or confirms a proposed closure.

---

# codex-007 - Move Nexus Guides To Work Area

**Plan:** `0003-configuration-procedures`
**Status:** recorded
**Timestamp:** 2026-05-21

## Changes

Moved the provisional Nexus guide documents from `doc/` into `_work/` while
the developer workflow, player terminal setup, and layout policies remain in
flux. Added the current baseline tty/player options to `sys/unix/nexus.nethackrc`.

Changed files:

- `_work/nexus-dev-guide.md`
- `_work/nexus-layout.md`
- `_work/nexus-player-guide.md`
- `_work/README.md`
- `_work/plans/0003-configuration-procedures.md`
- `AGENTS.md`
- `sys/unix/nexus.nethackrc`
- `_work/codex-log.md`

Active runtime files, world files, and build inputs still belong in the normal
NetHack tree. The moved guides are coordination documents for now and may move
again when the policy settles. The runtime rc now selects tty display behavior,
DEC graphics, color/status presentation, message behavior, and disclosure/score
defaults for the Nexus launcher.

---

# codex-008 - Engine Assessment And NLE5 Alignment

**Plan:** `0002-boot-custom-level`
**Status:** recorded
**Timestamp:** 2026-05-21

## Changes

Added a Nexus engine assessment note summarizing the relevant NetHack 5 startup
and topology findings from the initial project discussion.

Changed Nexus files:

- `_work/nethack-engine-assessment.md`
- `_work/codex-log.md`

The assessment records the first milestone, the data-first strategy, the
startup path through `newgame()`, `init_dungeons()`, `dat/dungeon.lua`,
`mklev()`, and `load_special()`, likely hardwired canonical dungeon
assumptions, and the recommendation to continue plan
`0002-boot-custom-level` by trying to place a custom Lua level at dungeon 0,
level 1 before making C changes.

Also updated the parallel `nle5` project for alignment:

- `/home/mlehotay/projects/nle5/_work/README.md`
- `/home/mlehotay/projects/nle5/_work/nexus-alignment.md`
- `/home/mlehotay/projects/nle5/AGENTS.md`
- `/home/mlehotay/projects/nle5/nle5-codex-copypasta.md`

Those NLE5 notes keep the dependency direction explicit: NLE5 may later point
at Nexus as a target engine, but Nexus should not depend on NLE5, and NLE5
benchmark or agent concerns should not drive Nexus before the custom
human-playable level boots.

---

# codex-009 - Vanilla NetHack Architecture Reference

**Plan:** `0004-vanilla-nethack-architecture`
**Status:** recorded
**Timestamp:** 2026-05-21

## Changes

Started plan `0004` and created the initial vanilla NetHack 5 architecture
reference.

Changed files:

- `_work/architecture/vanilla-nethack-architecture.md`
- `_work/plans/0004-vanilla-nethack-architecture.md`
- `_work/plans/plans.csv`
- `_work/tasks.csv`
- `_work/codex-log.md`

The new reference describes startup, new-game initialization, the turn loop,
global state, dungeon topology, `dat/dungeon.lua`, special Lua levels, object
and monster identity tables, Quest/Sokoban/endgame coupling, save/restore
save/restore responsibilities, Lua interfaces, and architecture constraints for
Nexus world replacement. Plan `0004` remains open and marked `doing`; task
`task-013` is closed for the initial document pass.

---

# codex-010 - Build Configuration Resource Report

**Plan:** `0004-vanilla-nethack-architecture`
**Status:** recorded
**Timestamp:** 2026-05-21

## Changes

Added a companion architecture report for conditional compilation, DLB,
SYSCF/sysconf, and nearby build/resource topics.

Changed files:

- `_work/architecture/nethack-build-config-resource-architecture.md`
- `_work/tasks.csv`
- `_work/codex-log.md`

The report records the distinction between compile-time feature macros, DLB
resource packaging, SYSCF local site policy, generated build surfaces, and
runtime/player configuration. It also records Nexus guidance to keep early
developer builds non-DLB, use `sys/unix/hints/nexus-local` for local build
policy, avoid sysconf as world data, and avoid new compile-time feature macros
unless they are truly required.

---

# codex-011 - System And Window Port Report

**Plan:** `0004-vanilla-nethack-architecture`
**Status:** recorded
**Timestamp:** 2026-05-21

## Changes

Added a companion architecture report for system ports, window ports, shim,
WASM/libnh, and WINCHAIN.

Changed files:

- `_work/architecture/nethack-system-window-port-architecture.md`
- `_work/tasks.csv`
- `_work/codex-log.md`

The report records the distinction between system ports and window ports, the
`windowprocs` vtable model, compile-time versus runtime window selection,
`win/shim/winshim.c` as a callback bridge for libnh/WASM, and WINCHAIN as a
window-call middleware mechanism. It recommends keeping Nexus on the existing
Unix + tty path until the native custom world milestone is working.

---

# codex-012 - Save And Bones Architecture Report

**Plan:** `0004-vanilla-nethack-architecture`
**Status:** recorded
**Timestamp:** 2026-05-21

## Changes

Added a companion architecture report for savefiles, level files, bones files,
serialization formats, Lua saved state, and Nexus persistence scopes.

Changed files:

- `_work/architecture/nethack-save-bones-architecture.md`
- `_work/tasks.csv`
- `_work/codex-log.md`

The report records that NetHack 5 has an `NHFILE` savefile abstraction and
field-level/export-ascii machinery, but ordinary gameplay saves and bones in
this tree still use the historical binary struct-level format. It also records
how global game state, level-local state, bones transfer state, and Lua
`nh_lua_variables` persistence should inform future Nexus module responsibilities.

---

# codex-013 - Architecture Reports Directory

**Plan:** `0004-vanilla-nethack-architecture`
**Status:** recorded
**Timestamp:** 2026-05-21

## Changes

Moved the vanilla NetHack architecture reports into `_work/architecture/` and
added a short directory README with an executive summary.

Changed files:

- `_work/architecture/README.md`
- `_work/architecture/vanilla-nethack-architecture.md`
- `_work/architecture/nethack-build-config-resource-architecture.md`
- `_work/architecture/nethack-system-window-port-architecture.md`
- `_work/architecture/nethack-save-bones-architecture.md`
- `_work/plans/0004-vanilla-nethack-architecture.md`
- `_work/plans/0005-nexus-architecture.md`
- `_work/README.md`
- `_work/codex-log.md`

The move keeps `_work/` readable while preserving plan `0004` as the active
source-grounded vanilla architecture work front.

---

# codex-014 - Close Vanilla Architecture Plan

**Plan:** `0004-vanilla-nethack-architecture`
**Status:** closed
**Timestamp:** 2026-05-21

## Changes

Closed plan `0004` with explicit user approval.

Changed files:

- `_work/plans/0004-vanilla-nethack-architecture.md`
- `_work/plans/plans.csv`
- `_work/codex-log.md`

Plan `0004` is complete. The source-grounded vanilla architecture materials now
live under `_work/architecture/` and cover runtime architecture, build/resource
configuration, system/window ports, and save/bones persistence scopes. No
runtime source, data, or build behavior changed.

---

# codex-015 - Compilation And Cross-Compile Architecture Report

**Plan:** `0004-vanilla-nethack-architecture`
**Status:** recorded after plan closure
**Timestamp:** 2026-05-21

## Changes

Added an additional vanilla architecture report covering NetHack 5 compilation,
cross-compilation, host-vs-target build separation, hints, generated artifacts,
DLB/SYSCF packaging, and how build variability contains platform and window
port choices.

Changed files:

- `_work/architecture/nethack-compilation-cross-architecture.md`
- `_work/architecture/README.md`
- `_work/tasks.csv`
- `_work/codex-log.md`

The report records that NetHack 5's Lua dungeon, level, and quest text shift is
also a cross-compilation architecture change: it removes target-shaped
build-time generated dungeon/level/quest artifacts and leaves target-specific
work concentrated in `TARGET_*` compilation, selected system/window sources,
runtime data packaging, and target package rules. No runtime source, data, or
build behavior changed.

---

# codex-016 - Clarify Architecture Terminology

**Plan:** `0004-vanilla-nethack-architecture`
**Status:** recorded after plan closure
**Timestamp:** 2026-05-21

## Changes

Replaced the unclear architecture term across `_work` architecture and planning
docs with more specific language such as interface, responsibility, scope,
separation, compatibility, and control point.

Changed files:

- `_work/architecture/README.md`
- `_work/architecture/vanilla-nethack-architecture.md`
- `_work/architecture/nethack-build-config-resource-architecture.md`
- `_work/architecture/nethack-system-window-port-architecture.md`
- `_work/architecture/nethack-save-bones-architecture.md`
- `_work/architecture/nethack-compilation-cross-architecture.md`
- `_work/plans/0004-vanilla-nethack-architecture.md`
- `_work/plans/0005-nexus-architecture.md`
- `_work/nethack-engine-assessment.md`
- `_work/tasks.csv`
- `_work/codex-log.md`

No runtime source, data, or build behavior changed.

---

# codex-017 - Record Nexus Compile-Time Flag Strategy

**Plan:** `0005-nexus-architecture`
**Status:** design note added
**Timestamp:** 2026-05-21

## Changes

Expanded `_work/architecture/nexus-cflag.md` into a durable design note for using
`#ifdef NEXUS` without leaking Nexus behavior into vanilla NetHack builds.

The note defines `NEXUS` as an opt-in build feature macro owned by Nexus build
profiles, recommends guarded switch points in shared NetHack files, reserves
Nexus behavior for Nexus-owned source/data files, and calls out resource,
DLB, save, bones, and review-checklist concerns.

Changed files:

- `_work/architecture/nexus-cflag.md`
- `_work/codex-log.md`

No runtime source, data, or build behavior changed.

---

# codex-018 - Start Nexus Architecture Plan

**Plan:** `0005-nexus-architecture`
**Status:** plan started; first guard map recorded
**Timestamp:** 2026-05-22

## Changes

Marked `0005-nexus-architecture` as doing, added executable Nexus architecture
tasks, registered the moved `nexus-cflag.md` architecture note, and added
`_work/architecture/nexus-boot-guard-map.md`.

The new guard map connects the first boot-custom-level milestone to the
`NEXUS` compile-time strategy. It identifies the expected touch points:
`sys/unix/hints/nexus-local`, `src/dungeon.c`, `sys/unix/Makefile.top`, new
`dat/nexus-*.lua` files, and `_work/divergences.md`. It recommends keeping the
first shared C change to a guarded `DUNGEON_FILE` selection only.

Changed files:

- `_work/architecture/README.md`
- `_work/architecture/nexus-boot-guard-map.md`
- `_work/plans/0005-nexus-architecture.md`
- `_work/plans/plans.csv`
- `_work/tasks.csv`
- `_work/codex-log.md`

No runtime source, data, or build behavior changed.

---

# codex-019 - Minimal Nexus Boot Build

**Plan:** `0002-boot-custom-level`
**Status:** first milestone verified; plan left open for user confirmation
**Timestamp:** 2026-05-22

## Changes

Implemented the minimal opt-in Nexus boot path.

Changed runtime/build files:

- `src/dungeon.c`
- `sys/unix/hints/nexus-local`
- `sys/unix/Makefile.top`
- `dat/nexus-dungeon.lua`
- `dat/nexus-start.lua`

Changed workflow files:

- `_work/divergences.md`
- `_work/plans/0002-boot-custom-level.md`
- `_work/tasks.csv`
- `_work/codex-log.md`

The Nexus local build now defines `NEXUS`, and `NEXUS` builds load
`nexus-dungeon.lua` instead of `dungeon.lua`. The Nexus topology registers a
fixed `nexus-start.lua` special level at dungeon 0 level 1. Non-Nexus builds
still select `dungeon.lua`.

Verification:

- `sh sys/unix/setup.sh sys/unix/hints/nexus-local`
- `make all`
- `make install`
- pseudo-terminal run of the installed Nexus binary

The installed binary booted to the handcrafted Nexus map, rendered the level in
tty, accepted input, reported the location as `Nexus`, and quit cleanly.
`make install` and the runtime check needed approval because they write under
`~/games/nethack/nexus`.

---

# codex-020 - Start Verification Procedure Plan

**Plan:** `0006-verification-procedure`
**Status:** plan started; implementation tasks created
**Timestamp:** 2026-05-23

## Changes

Created the stacked `0006-verification-procedure` plan to develop repeatable
testing for the `0002-boot-custom-level` branch before merge.

The workflow now documents stacked verification branches. It also records that
current local branch names are existing state rather than settled policy, and
keeps branch naming plus repo-prefixed plan ids as open workflow decisions. The
plan records that 0006 is stacked from 0002, focuses the first verification
pass on the actual 0002 `NEXUS` guard behavior, defers DLB testing, and calls
out wizard-mode access as a developer verification target.

Added tasks for:

- documenting the manual 0002 verification procedure
- choosing and implementing a pseudo-terminal smoke-test harness
- testing Nexus-enabled `nexus-local` boot
- testing NEXUS-disabled `linux-minimal` vanilla boot
- verifying wizard-mode access
- running the full 0006 procedure against the stacked 0002 branch

Changed files:

- `_work/workflow.md`
- `_work/plans/plans.csv`
- `_work/plans/0006-verification-procedure.md`
- `_work/tasks.csv`
- `_work/codex-log.md`

Verification: documentation/task update only; no runtime tests run.

No runtime source, data, build behavior, or upstream divergence changed.

---

# codex-021 - Execute Verification Procedure

**Plan:** `0006-verification-procedure`
**Status:** verification procedure implemented and run; wizard-mode access enabled
**Timestamp:** 2026-05-23

## Changes

Added the first Nexus verification procedure and pty smoke harness.

Changed runtime/config files:

- `sys/unix/sysconf`

Changed workflow files:

- `_work/verification.md`
- `_work/tools/nh-pty-smoke.py`
- `_work/tools/.gitignore`
- `_work/verification-runs/.gitignore`
- `_work/plans/0006-verification-procedure.md`
- `_work/tasks.csv`
- `_work/divergences.md`
- `_work/codex-log.md`

The harness launches tty NetHack commands through a pseudo terminal, checks
expected and forbidden text, can send a follow-up command such as `#overview`,
handles common pager prompts, sends `#quit`, and writes transient captures
under `_work/verification-runs/`.

Verification:

- `python3 -m py_compile _work/tools/nh-pty-smoke.py`
- `sh sys/unix/setup.sh sys/unix/hints/nexus-local`
- `make clean`
- `make all`
- `make install`
- pty smoke of `~/.local/bin/nexus`
- `sh sys/unix/setup.sh sys/unix/hints/linux-minimal`
- `make clean`
- `make all`
- `make install`
- copy `sys/unix/sysconf` into the linux-minimal playground
- pty smoke of `~/nethack-minimal/games/nethack`
- pty smoke of `~/.local/bin/nexus -D`

Results:

- NEXUS-enabled `nexus-local` build used `-DNEXUS`, installed successfully,
  booted to the handcrafted map, `#overview` reported `Nexus`, and `#quit`
  exited cleanly.
- NEXUS-disabled `linux-minimal` build compiled without `-DNEXUS`, installed
  successfully, `#overview` reported `Dungeons of Doom`, `Nexus` was absent,
  and `#quit` exited cleanly after installing the required `sysconf`.
- Profile switching requires `make clean`; an early run caught stale object
  files preserving the previous `NEXUS` state after changing hints.
- Wizard mode was initially blocked for the normal developer user: installed
  `sysconf` allowed only `root games`, so `nexus -D` was denied and fell back
  to explore mode.

Follow-up adjustment:

- lowered the pty smoke default timeout to 10 seconds;
- clarified that the current smoke test is the first verification procedure,
  not the complete future test strategy;
- narrowed wizard-mode verification to access only for now;
- enabled wizard mode for local user `mlehotay` in `sys/unix/sysconf`;
- installed the updated `sysconf` into the Nexus local playground;
- verified `nexus -D -p Arc -r Hum -@` starts as `wizard`, reaches Dlvl 1,
  does not fall back to explore mode, and quits cleanly.

Tasks `task-022` through `task-027` are marked done. Plan 0006 remains open
until the user explicitly confirms closure.

Runtime configuration changed: `sys/unix/sysconf` now authorizes local user
`mlehotay` for wizard mode. The intentional divergence is recorded in
`_work/divergences.md`.

---

# codex-022 - Record Console Host Settings

**Plan:** `0003-configuration-procedures`
**Status:** terminal configuration finding recorded
**Timestamp:** 2026-05-23

## Changes

Recorded the current dedicated Nexus Windows Console Host settings:

- font: `Flexi IBM VGA True (437)`
- `Disable Scroll-Forward`: enabled

Changed files:

- `_work/nexus-player-guide.md`
- `_work/plans/0003-configuration-procedures.md`
- `_work/codex-log.md`

No runtime source, data, build behavior, or upstream divergence changed.

---

# codex-023 - Merge And Close Plans 0002 0004 And 0006

**Plans:** `0002-boot-custom-level`, `0004-vanilla-nethack-architecture`, `0006-verification-procedure`
**Status:** branches merged; plan statuses closed with user confirmation
**Timestamp:** 2026-05-23

## Changes

Merged the completed stacked branches into `nexus`:

- `work-0002-boot-custom-level`
- `work-0006-verification-procedure`

Closed plans `0002-boot-custom-level` and `0006-verification-procedure` after
explicit user confirmation. Corrected the stale `plans.csv` status for
`0004-vanilla-nethack-architecture`, which had already been closed with
explicit user approval.

Changed files after merge:

- `_work/plans/0002-boot-custom-level.md`
- `_work/plans/0006-verification-procedure.md`
- `_work/plans/plans.csv`
- `_work/codex-log.md`

Verification: branch merge and plan-state update only; previous 0006 runtime
verification remains the relevant check.
