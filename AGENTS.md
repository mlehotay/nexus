# AGENTS.md

Instructions for Codex and other filesystem-native agents working in this repository.

## Project Identity

This repository is for Nexus: a tiny standalone world built on the NetHack 5.0.0 engine.

Goal:

> Preserve NetHack systems. Replace NetHack world assumptions.

This is not an IER repository and should not inherit IER governance, vocabulary, release checks, or theory constraints.

## Scope

Keep the initial scope aggressively small:

- one custom world
- one handcrafted Lua level
- minimal or no combat
- calm traversal
- basic NetHack movement, inventory, objects, creatures, line of sight, persistence, and messages

Do not make a full roguelike.
Do not make an IER game.
Do not build a full conversion at the start.
Do not begin with procedural generation.

## First Milestone

Success condition:

```text
NetHack 5 launches
The player starts in a custom Lua level
Basic movement and rendering work
The canonical Dungeons of Doom structure is bypassed or replaced
```

## Architecture Boundary

Prefer changing data/topology before engine surgery:

- start with `dat/dungeon.lua`
- add one custom Lua level file
- identify the minimum C changes only if the topology cannot express the tiny world
- keep branch, quest, ascension, special-case, and endgame systems untouched until they become real blockers

Use `_work/nexus-layout.md` for the current Nexus directory conventions.
`_work/` may hold provisional Nexus workflow and setup guides while those
policies are still being established. Do not put active Nexus runtime files,
world files, or build inputs there.

## Operating Rules

- Read startup and dungeon-generation code before editing.
- Keep diffs minimal and reversible.
- Preserve upstream NetHack systems unless replacing a world assumption requires otherwise.
- Avoid unrelated content, balance, item, monster, or UI changes.
- Use the narrowest build/run target available.
- Record every intentional divergence from upstream.

## Workflow

Use `_work/` for lightweight coordination. It is not gameplay content and does
not define player-facing behavior.

Primary workflow files:

- `_work/nexus.mk` provides workflow-only audit targets for comparing Nexus
  with upstream NetHack and reviewing recorded divergences.
- `_work/repo-workflow.md` is the point-of-work copy of the canonical FLEY
  repository workflow.
- `_work/local-workflow.md` supplements it with Nexus branch, task, Codex, and
  divergence habits.
- `_work/tasks.csv` tracks executable tasks.
- `_work/plans/plans.csv` tracks larger work fronts.
- `_work/plans/*.md` stores plan context, constraints, and acceptance criteria.
- `_work/codex-log.md` records concise Codex session summaries when useful.
- `_work/divergences.md` records intentional upstream NetHack divergences.

Durable Nexus runtime and build files belong in the normal NetHack tree,
especially `dat/`, `sys/unix/`, and `sys/unix/hints/`. Provisional Nexus
workflow/setup guides currently live in `_work/`; see `_work/nexus-layout.md`.
Keep workflow-only audit targets and developer verification helpers in
`_work/` unless they become required build inputs or player-facing behavior.

Branch rules:

- Treat `nexus` as the integration branch.
- Do nontrivial work on short branches, such as `work/0002-boot-custom-level`.
- Do not work directly on upstream branches such as `NetHack-5.0`.
- Do not import Floating Eye code or gameplay patches. `../nethack` may be used
  as a workflow reference only.

Codex session rules:

- Check `git status` before editing.
- State intended files before changing source files.
- Work with existing user changes; do not revert unrelated changes.
- Add a `_work/codex-log.md` entry when a session changes source files, closes
  a task, closes a plan with explicit user approval, or records findings needed
  by later sessions.
- At the end of a code-changing session, summarize changed files,
  verification, blockers, and any needed `_work/divergences.md` update.

Nexus audit commands:

- Use `make -f _work/nexus.mk diff-stat` and
  `make -f _work/nexus.mk diff` to review what Nexus currently changes
  relative to the upstream merge base.
- Use `make -f _work/nexus.mk touched` to list files touched by Nexus-only
  commits.
- Use `make -f _work/nexus.mk workflow-check` to check `_work/plans/plans.csv`,
  `_work/tasks.csv`, and plan files for mechanical workflow drift.
- Review `_work/divergences.md` separately as the human-reviewed divergence
  ledger.
- The audit makefile is workflow-only. Do not wire it into NetHack's normal
  makefiles without an explicit Nexus build/release decision.

Session wrap-up command:

- If the user says `summarize`, `summarize work`, `summarize open work`, or
  equivalent, inspect `_work/plans/plans.csv`, `_work/tasks.csv`, and
  `_work/todo.md`, run `make -f _work/nexus.mk workflow-check` when available,
  and report open plans, open tasks, loose todo items, and any dashboard
  errors. Do not edit files, close work, or commit during this operation.
- If the user says `wrap up`, `finish the session`, or equivalent, do the
  workflow closeout without waiting for another prompt.
- Check `git status`.
- Update `_work/tasks.csv` if task state changed.
- Add or update `_work/codex-log.md` if the session changed source files,
  closed a task, closed a plan with explicit user approval, or recorded
  findings needed by later sessions.
- Update `_work/divergences.md` if there was an intentional upstream NetHack
  divergence.
- Run or report the narrowest useful verification.
- Summarize changed files, verification, blockers, and whether changes remain
  uncommitted.

Commit command:

- If the user says `commit this session`, first perform the wrap-up steps.
- Stage files with `git nhadd` when the commit touches NetHack source, data,
  doc, or build files, so NetHack keyword substitution hooks run.
- Use `git add` only for files that should not go through NetHack keyword
  substitution.
- Use `git nhcommit` for the commit.
- Do not commit unless the user explicitly asks for a commit.

NetHack local workflow:

- The local substitution prefix is `FLEY`.
- The local project name is `Nexus`.
- Use `git nhadd` and `git nhcommit` for commits that touch NetHack source
  files so NetHack keyword substitution hooks run.

Planning conventions:

- Plan `0001-environment-setup` covers repository, branch, FLEY, and workflow
  setup.
- Plan `0002-boot-custom-level` covers the first milestone: booting into one
  handcrafted Nexus Lua level.
- Plan `0003-configuration-procedures` covers developer workflow, player
  terminal setup, runtime configuration conventions, and project procedures.
- Do not close a plan or mark it `done` unless the user explicitly asks for
  that plan to be closed or confirms a proposed closure. During wrap-up, report
  that a plan appears complete if appropriate, but leave it open without that
  approval.
- Keep the workflow lighter than Halfbaked governance. Nexus should not inherit
  IER governance, vocabulary, release checks, or theory constraints.

## Suggested First Codex Prompt

```text
I want to create Nexus, a tiny standalone NetHack 5.0.0 world.

My goal is not to add a branch to the Dungeons of Doom.
I want to keep the NetHack engine and simulation systems but replace the canonical dungeon structure.

Please inspect the source and identify:

1. where dungeon initialization begins
2. how dat/dungeon.lua is loaded and translated into internal topology
3. how special Lua levels are registered and loaded
4. the smallest data-only change that might boot into one custom level
5. where C changes become unavoidable, if anywhere
6. a minimal proof-of-concept plan

Do not design gameplay yet.
Do not add procedural generation yet.
Prioritize booting into one handcrafted custom place.
```
