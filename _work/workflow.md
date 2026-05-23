# Nexus Workflow

This is the lightweight coordination workflow for Nexus development.

Nexus is a standalone derivative of NetHack 5.0.0. It should not inherit
Floating Eye gameplay patches, IER governance, or Snowglobe implementation
rules. Snowglobe may be useful as conceptual reference for small explicit
worlds; upstream NetHack remains the code base.

## Branches

- `nexus` is the integration branch.
- Branch names should identify the plan or task they belong to, but the final
  Nexus branch naming convention is not settled yet.
- The current local branches use names such as
  `work-0002-boot-custom-level` and `work-0006-verification-procedure`.
  Treat that as existing local state, not as a durable naming rule.
- Candidate future conventions include:
  - `0006-verification-procedure`
  - `plan/0006-verification-procedure`
  - a repo-prefixed plan id such as `nexus-0006-verification-procedure`

Avoid working directly on upstream branches such as `NetHack-5.0`.

Do not rename existing branches just to tidy naming while active work is in
progress. Decide the convention deliberately, then migrate branch and plan
metadata as a small workflow cleanup if needed.

When one plan needs to test or document another plan before that older plan is
merged, create a stacked branch from the implementation branch being tested.
For example, the 0006 verification branch may branch from the 0002 boot branch
so it can exercise the exact 0002 boot path before 0002 reaches `nexus`.

Use stacked branches for verification work when the verification itself is a
separate concern from the implementation under test:

- keep the implementation branch focused on the runtime or data change
- keep the verification branch focused on test procedure, harnesses, and
  workflow documentation
- record in the plan which branch the verification branch is based on
- after testing, merge or commit the implementation branch first, then rebase
  or merge the verification branch onto `nexus` before integrating it
- if verification finds a runtime defect, fix the defect on the implementation
  branch when practical, then update the stacked verification branch

Do not use a stacked verification branch to hide implementation changes that
belong in the original plan. If the test process requires small helper scripts
or documentation, those belong with the verification plan.

## Work Surfaces

Plans describe work fronts. Tasks describe executable steps.

- Add a plan when the work has multiple steps, uncertainty, or acceptance
  criteria.
- Do not close a plan or mark it `done` unless the user explicitly asks for
  that plan to be closed or confirms a proposed closure. A wrap-up may report
  that a plan appears complete, but it must leave the plan open without that
  approval.
- Add a task for concrete work that can be completed and verified.
- Keep notes factual. Design intent belongs here until it becomes code or
  player-facing documentation.
- Verification plans should distinguish the thing being tested from the test
  procedure itself. A plan can say "test branch X before it merges" without
  absorbing branch X's runtime changes.
- Plan ids are currently numeric within this repository. A repo-prefixed plan
  id scheme, such as `nexus-0006`, is an open workflow decision.

Workflow-only tooling belongs in `_work/` when it is not needed by the
NetHack build, install, runtime startup, or player-facing data. Keep these
tools out of upstream NetHack makefiles unless they become part of a deliberate
Nexus build or release process.

Use `_work/nexus.mk` for local Nexus audit commands:

```sh
make -f _work/nexus.mk diff-stat
make -f _work/nexus.mk diff
make -f _work/nexus.mk touched
make -f _work/nexus.mk workflow-check
make -f _work/nexus.mk audit
```

The default comparison is `nexus` against `upstream/NetHack-5.0` at their
current merge base. Override `NEXUS_REF` or `UPSTREAM` when auditing a work
branch or a different upstream ref.

Interpret the targets narrowly:

- `diff` and `diff-stat` show what Nexus currently changes relative to the
  selected upstream baseline.
- `touched` shows files changed by commits reachable from `NEXUS_REF` but not
  from `UPSTREAM`.
- `workflow-check` checks `_work/plans/plans.csv`, `_work/tasks.csv`, and plan
  files for mechanical workflow drift.
- `_work/divergences.md` is the separate human-reviewed ledger of intentional
  departures from upstream NetHack.

Developer verification helpers, including pty smoke tests, belong in
`_work/tools/` unless they become required build inputs. They are Nexus
workflow artifacts, not NetHack runtime divergences, unless they change how
Nexus builds, installs, starts, or plays.

The workflow checker is intentionally lighter than the Halfbaked dashboard
system. It enforces only mechanical consistency: CSV headers, duplicate ids,
known statuses and priorities, task-to-plan resolution, dependency references,
plan file synchrony, and obvious stale execution state such as open tasks under
done plans.

## Codex Sessions

At the start of a code-changing session, Codex should check `git status` and
state the intended files before editing.

When the user says `wrap up`, `finish the session`, or equivalent, Codex should
close the session by doing the workflow maintenance, not just summarizing.

When the user says `summarize`, `summarize work`, `summarize open work`, or
equivalent, Codex should inspect the planning surfaces and report the open work
without changing files.

Summarize steps:

- check `git status`
- run `make -f _work/nexus.mk workflow-check` if the target exists, or report
  that the checker is unavailable
- read `_work/plans/plans.csv`, `_work/tasks.csv`, and `_work/todo.md`
- list non-terminal plans, grouped by status
- list open tasks, grouped by plan/front and including status, priority,
  branch, dependencies, and notes when useful
- summarize loose open items from `_work/todo.md` if any are present
- report dashboard errors or warnings before interpreting the work surface
- do not close plans, change task state, edit files, or commit as part of
  `summarize`

Wrap-up steps:

- check `git status`
- update `_work/tasks.csv` if task state changed
- add or update `_work/codex-log.md` if source files changed, a task closed,
  a plan closure was explicitly approved, or later sessions need the findings
- update `_work/divergences.md` if there was an intentional upstream NetHack
  divergence
- run or report the narrowest useful verification
- report files changed, verification, blockers or follow-up tasks, divergence
  status, and whether changes remain uncommitted

Use `codex-log.md` for durable session summaries when the work changes source
files, records findings that future sessions need, closes a task, or closes a
plan with explicit user approval.

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
