# 0001 - Environment Setup

## Goal

Set up Nexus as its own NetHack 5.0.0 derivative with a clean repository root,
a project branch, NetHack local developer configuration, and lightweight work
tracking.

## Scope

In scope:

- source tree directly under `/home/mlehotay/projects/nexus`
- `src/` and `dat/` at repository root
- branch work separated from upstream `NetHack-5.0`
- local NetHack setup using `FLEY`
- project name configured as `Nexus`
- `_work/` surfaces for plans, tasks, logs, workflow, and divergences

Out of scope:

- gameplay changes
- dungeon topology changes
- Lua level implementation
- build system changes beyond NetHack local setup
- importing Floating Eye patches

## Current State

Nexus is on branch `nexus`, based on the official NetHack
`NetHack-5.0.0_Release` tag.

Local NetHack config includes:

```text
nethack.substprefix=FLEY
nethack.projectname=Nexus
```

## Acceptance Criteria

- `git describe --tags --always` reports `NetHack-5.0.0_Release` on `nexus`
- `git config nethack.substprefix` reports `FLEY`
- `git config nethack.projectname` reports `Nexus`
- `_work/` contains workflow, plan, task, log, and divergence surfaces
- no Floating Eye source changes are present

## Status

Done.
