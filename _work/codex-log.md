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
- `doc/nexus-layout.md`
- `_work/README.md`
- `_work/workflow.md`
- `_work/codex-log.md`

`doc/nexus-layout.md` is now the durable source for repository layout
conventions. `_work/` remains temporary coordination space only.

`AGENTS.md` and `_work/workflow.md` now define:

- `wrap up` / `finish the session`
- `commit this session`

These commands require workflow maintenance, verification reporting, and
keyword-aware NetHack commits via `git nhadd` and `git nhcommit` when source,
data, doc, or build files are involved.
