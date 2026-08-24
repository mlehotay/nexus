# dgamelaunch Codex Log

Concise append-only summaries for Codex sessions.

Use this log when a session changes repository files, records findings that
future sessions need, or establishes project setup.

Entry shape:

```text
---

# codex-NNN - Short Title

**Plan:** `plan-id` or none
**Priority:** Pn
**Status:** recorded
**Timestamp:** YYYY-MM-DD HH:MM TZ

## Changes

...
```

---

# codex-001 - FLEY Context And Illithid Backup Investigation

**Plan:** none
**Priority:** P0
**Status:** recorded
**Timestamp:** 2026-06-15 16:35 EDT

## Changes

Established durable context for maintaining the Floating Eye Software
dgamelaunch repository and the public NetHack service on `illithid`.

Reviewed:

- `examples/avocado.txt`
- `examples/floatingeye.txt`
- `../nethack/sys/unix/Install.avocado`
- `../nethack/sys/unix/Install.turnip`
- `../site-ops/_work/plans/0007-illithid-maintenance.md`
- `../fley-org/templates/repo-workflow.md`
- `../fley-org/docs/repo-workflow-installation.md`
- two console logs recorded from SSH sessions on `illithid`

Created:

- `_work/fley-context.md`
- `_work/illithid-backup.md`
- `_work/repo-workflow-installation-problem.md`
- `_work/codex-log.md`

The context report records the three FLEY governance levels, repository
authority boundaries, local and production environments, historical deployment
model, and the requirement to preserve the existing `nh370` runtime and active
player state.

The backup investigation found the historical one-line backup command in
`examples/floatingeye.txt`. The newest clearly dated archive visible in the
console logs is from October 4, 2024, and all observed archives are stored on
the same host as the live data. The new backup runbook adds timestamped
filenames, incomplete-archive protection, archive verification, checksums,
restricted permissions, and off-host copying guidance. It also records that a
live `tar` archive is not a guaranteed point-in-time snapshot of active games.

An attempt to install the FLEY repo workflow was started and then deliberately
backed out. The unresolved problem is how to provide local workflow
verification in a legacy repository where the normal top-level `Makefile` is
generated from tracked `Makefile.in` and ignored by Git. No Makefile,
`Makefile.in`, `.gitignore`, dashboard, plan, `AGENTS.md`, or workflow
procedure was added or changed. Repo-workflow adoption remains incomplete.

No commands were run against `illithid` during this Codex session, and no
production data or services were changed.

## Verification

- `git diff --check` passed after each report was created.
- Git status showed only the new untracked `_work/` directory.

## Follow-Up

- Make and verify a current backup of the live dgamelaunch and NetHack data.
- Copy verified backups to protected off-host storage.
- Decide how this legacy repository should expose FLEY workflow verification
  before resuming repo-workflow installation.
- Develop a service manual covering maintenance, user support, recovery,
  variant deployment, scoreboard access, monitoring, and disaster recovery.
