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
