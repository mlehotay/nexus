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
