# Nexus Workflow

This is the lightweight coordination workflow for Nexus development.

Nexus is a standalone derivative of NetHack 5.0.0. It should not inherit
Floating Eye gameplay patches, IER governance, or Snowglobe implementation
rules. Snowglobe may be useful as conceptual reference for small explicit
worlds; upstream NetHack remains the code base.

## Branches

- `nexus` is the integration branch.
- Work branches should be short and named by front, for example:
  - `work/0001-environment`
  - `work/0002-boot-custom-level`
  - `work/topology-notes`

Avoid working directly on upstream branches such as `NetHack-5.0`.

## Work Surfaces

Plans describe work fronts. Tasks describe executable steps.

- Add a plan when the work has multiple steps, uncertainty, or acceptance
  criteria.
- Add a task for concrete work that can be completed and verified.
- Keep notes factual. Design intent belongs here until it becomes code or
  player-facing documentation.

## Codex Sessions

At the start of a code-changing session, Codex should check `git status` and
state the intended files before editing.

When the user says `wrap up`, `finish the session`, or equivalent, Codex should
close the session by doing the workflow maintenance, not just summarizing.

Wrap-up steps:

- check `git status`
- update `_work/tasks.csv` if task state changed
- add or update `_work/codex-log.md` if source files changed, a task or plan
  closed, or later sessions need the findings
- update `_work/divergences.md` if there was an intentional upstream NetHack
  divergence
- run or report the narrowest useful verification
- report files changed, verification, blockers or follow-up tasks, divergence
  status, and whether changes remain uncommitted

Use `codex-log.md` for durable session summaries when the work changes source
files, records findings that future sessions need, or closes a plan/task.

When the user says `commit this session`, Codex should perform the wrap-up
steps first, then commit. Commits that touch NetHack source, data, doc, or build
files should use NetHack's keyword-aware helpers:

```sh
git nhadd <paths>
git nhcommit
```

Use plain `git add` only for files that should not go through NetHack keyword
substitution. Do not commit unless the user explicitly asks for a commit.

## NetHack Setup

Use NetHack's local workflow helpers when committing source changes:

```sh
git nhadd <paths>
git nhcommit
```

The local substitution prefix is `FLEY`; the local project name is `Nexus`.

Use `sys/unix/hints/nexus-local` for local Unix builds. It installs Nexus under
`~/games/nethack/nexus/` and keeps the launcher name `nexus` separate from any
other local `nethack` command.

## Divergences

Any intentional departure from upstream NetHack should be recorded in
`divergences.md`.

Record at least:

- date
- plan id
- files changed
- what upstream assumption was changed
- why data-only configuration was not enough, if C changed

Do not record every ordinary content edit. Focus on changes that affect
upstream compatibility, topology, startup behavior, build assumptions, or
NetHack system semantics.
