# Floating Eye dgamelaunch Context

> Migrated from `../dgamelaunch/_work/fley-context.md` on 2026-08-23.
> Nexus now owns the FLEY workflow for dgamelaunch and the Floating Eye
> NetHack variant. The dgamelaunch and nethack source checkouts remain free of
> FLEY `_work/` and `AGENTS.md` files; site-ops owns Illithid host operations.

## Purpose

This document records the organizational, repository, development, deployment,
and operational context for the Floating Eye Software (`FLEY`) dgamelaunch
repository.

The dgamelaunch repository predates FLEY by many years and does not adopt the
FLEY repo-level workflow. Its FLEY planning, decisions, and verification belong
in Nexus.

## Governance Layers

FLEY uses three distinct levels of governance:

1. `fley-qms` governs controlled SOPs, work instructions, and regulated work.
2. The `fley-org` organization process governs how FLEY decides what to work on
   next and handles organization-level prioritization and coordination.
3. The repo-level workflow governs how approved work gets done within an
   individual repository.

The canonical repo-level workflow template is:

```text
../fley-org/process/repo-workflow.md
```

Not all repositories have adopted the repo-level workflow. Legacy repositories
such as `dgamelaunch` must not be assumed to use it. Workflow installation or
adoption should be an explicit, separately scoped decision.

## Repository Roles

### dgamelaunch

Local checkout:

```text
~/projects/dgamelaunch
```

This repository contains the dgamelaunch implementation and supporting
examples. It is currently on the `master` branch.

Relevant operational notes:

```text
../dgamelaunch/examples/avocado.txt
../dgamelaunch/examples/floatingeye.txt
```

### NetHack Variant

Local checkout:

```text
~/projects/nethack
```

This is the NetHack variant used by the Floating Eye public server. It is
currently on the `floatingeye` branch.

Relevant installation notes:

```text
sys/unix/Install.avocado
sys/unix/Install.turnip
```

Relevant build hints:

```text
sys/unix/hints/avocado
sys/unix/hints/floatingeye
```

### site-ops

Local checkout:

```text
~/projects/site-ops
```

`site-ops` owns web-estate operations and contains the current planning surface
for maintenance of the public NetHack host:

```text
_work/plans/0007-illithid-maintenance.md
```

Static deployment of `www.floatingeye.net` is separate from NetHack and
dgamelaunch server maintenance.

### fley-org

Local checkout:

```text
~/projects/fley-org
```

`fley-org` is authoritative for organization-level topology, priorities,
authority boundaries, and coordination. Its organization process decides what
FLEY works on next. Its repo-workflow template describes how repositories may
manage approved work after adopting the workflow.

### fley-qms

`fley-qms` is authoritative for controlled SOPs, work instructions, CAPA,
change control, and regulated process governance. Routine repository work
should not be treated as QMS-controlled work unless the applicable controlled
process says otherwise.

## Systems And Environments

### turnip

`turnip` is the maintainer's laptop and local development system. The active
local checkouts are under:

```text
~/projects/dgamelaunch
~/projects/nethack
```

The NetHack instructions in `sys/unix/Install.turnip` describe both a
single-user local build and a chrooted build intended to resemble the public
server environment.

For a single-user local NetHack build, the instructions use
`sys/unix/hints/avocado`. For a chrooted Floating Eye build, they use
`sys/unix/hints/floatingeye`.

### avocado

`avocado` is the older development and test environment referenced by:

```text
examples/avocado.txt
../nethack/sys/unix/Install.avocado
```

The older checkout layout uses `~/sandbox` rather than `~/projects`.

### illithid / floatingeye.net

`illithid` is the public dgamelaunch and NetHack host for `floatingeye.net`.
The deployed chroot is rooted at:

```text
/opt/dgl
```

The existing NetHack runtime is:

```text
/opt/dgl/nh370
```

The public game service is reachable through the `nethack@floatingeye.net`
account. Deployment and maintenance notes are in
`examples/floatingeye.txt` and the `site-ops` illithid maintenance plan.

## Build And Deployment Model

The local and production notes establish the following general model:

- Build NetHack with `sys/unix/hints/floatingeye` for the dgamelaunch chroot.
- Build dgamelaunch with SQLite and shared-memory support and configure it to
  use `/opt/dgl/etc/dgamelaunch.conf`.
- Use `dgl-create-chroot` when creating the dgamelaunch chroot.
- Use NetHack `make install` for a fresh installation.
- Use NetHack `make update` for an existing deployed runtime when appropriate.
- Test the deployed NetHack binary from inside the chroot.
- Preserve ownership and permissions required by the `games` account and
  dgamelaunch.

These notes are historical operational guidance, not a complete or approved
production change procedure. Commands that delete or replace `/opt/dgl`, or
that update the existing runtime, require a separately reviewed production
plan.

The historical instructions contain a naming inconsistency between
`make fetch-Lua` and `make fetch-lua`. Confirm the valid target in the NetHack
checkout before relying on either spelling.

## Critical Production Constraint

The existing `nh370` runtime and dgamelaunch player state must be preserved.

On May 22, 2026, the live game menu showed an active `nh370` game for user
`iia`, started May 22, 2026 at 13:03:14, on dungeon level 38. This demonstrates
that illithid maintenance is not simply a rebuild or redeployment problem.

Any dgamelaunch, NetHack, operating-system, or host change must preserve:

- active and recoverable player games
- NetHack save compatibility
- required runtime state
- dgamelaunch user and player data
- enough of the existing `nh370` runtime to finish legacy games

Do not wipe `/opt/dgl` or replace the existing `nh370` runtime in a way that
breaks unfinished games.

NetHack 5.0.0 should be introduced side-by-side with `nh370`. Existing games
must continue using the compatible legacy runtime until they end or are
retired, while new games can use a separate NetHack 5.0.0 menu entry and
runtime.

## Work Routing

Use these ownership boundaries when new work is identified:

- Route controlled or regulated process changes to `fley-qms`.
- Route organization priorities, repository authority, and cross-repository
  coordination to `fley-org` and its organization process.
- Keep dgamelaunch source changes in `../dgamelaunch`, governed by the Nexus
  workflow.
- Keep NetHack variant source and build-hint changes in `../nethack`, governed
  by the Nexus workflow.
- Keep public-host inventory and illithid maintenance planning in `site-ops`.
- Keep static `www.floatingeye.net` deployment separate from public NetHack
  host maintenance.

Do not add FLEY dashboards, plan files, wrap-up procedures, `_work/`, or
`AGENTS.md` to either upstream-derived source checkout.

## Source References

```text
examples/avocado.txt
examples/floatingeye.txt
../nethack/sys/unix/Install.avocado
../nethack/sys/unix/Install.turnip
../site-ops/_work/plans/0007-illithid-maintenance.md
../fley-org/process/repo-workflow.md
```
