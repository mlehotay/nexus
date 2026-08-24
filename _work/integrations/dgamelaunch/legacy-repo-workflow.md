# FLEY Org Workflow

This is the lightweight coordination workflow for the Floating Eye Software
organizational governance repository.

It is paired with `fley-org/process/org-process.md`, which governs broader
conversation reconciliation, organization wrapup, and cross-repository
routing.

The repository is the source-of-truth workspace for organizational topology,
strategic initiatives, publication registry, authority boundaries, and
organization-level coordination notes.

## Work Surfaces

Plans describe work fronts. Todos describe executable steps.

- Add a plan when the work has multiple steps, uncertainty, dependencies, or
  acceptance criteria.
- Add a todo for concrete work that can be completed and verified.
- Use stable identifiers and do not reuse retired plan or todo IDs.
- Keep plan and todo state in the CSV dashboards.
- Use Markdown files for context, constraints, and decision notes.
- Record dependencies in `depends_on`; separate multiple dependencies with `|`.
- Do not mark a plan `done` unless the user explicitly asks for that plan to be
  closed or confirms a proposed closure.

Plans and todos track change work owned by this repository. They do not
duplicate organization registries:

- `projects/projects.csv` tracks managed project lifecycle.
- `projects/repositories.csv` tracks the current repository scope and authority
  boundaries.
- `projects/portfolio.csv` tracks which registered projects currently receive
  organization-level attention.
- `_work/plans/plans.csv` tracks multi-step changes to this repository.
- `_work/todo.csv` tracks executable steps in those changes.

Repo-local work may enter through organization wrapup or other cross-repository
routing. Creating a plan, todo, idea, note, or other authoritative repo surface
is an acceptable transfer of responsibility from conversation review into the
owning repository. Open work does not imply that the originating conversation
must remain active.

`_work/quick-status.md` is a brief maintainer-facing snapshot of current
attention, context, and concerns. It may summarize several registries or
repositories, but it is not authoritative for lifecycle, priority, plan, or
todo state. When it disagrees with a dashboard or registry, update the snapshot
or route the underlying state change to the authoritative surface.

## CSV Surface Types

CSV files used for coordination in Floating Eye repositories fall into two
governed types.

Workflow dashboards track executable work inside a repository. Accepted task
dashboard labels include `todo`, `tasks`, and domain-specific task labels such
as `gol-tasks` when the local workflow defines them. Workflow dashboards belong
to the repository that owns the work and do not replace organization-level
registries.

`fley-org` registries track organization-level state, such as repository
topology, strategic initiatives, project lifecycle, and publication governance.
Registries should have a documented schema, a clear authority boundary, and
evidence or notes sufficient to explain why each row belongs in the register.
They do not track executable work. Local `fley-org` work belongs in
`_work/plans/plans.csv` and `_work/todo.csv`.

Run `make check-registries` after registry or quick-status changes. The check
enforces current-scope repository coverage in the global project registry and
requires every current-scope repository identity in a `_work/quick-status.md`
heading. It also enforces portfolio visibility and validates canonical
repository identities, local checkout paths, repository relationships, and
project relationships.

Run `make local-tour` after changing a local top-level directory universe or
`projects/workspace-inventory.md`. It reports actual directories against the
inventory without modifying the inventory or failing on collaborator-specific
drift. Use `make check-local-tour` for strict validation. Override
`WORKSPACE_ROOT` and `WORKSPACE_INVENTORY` for other layouts.

The canonical repository workflow source is
`fley-org/process/repo-workflow.md`. Execution repositories may carry a
point-of-work copy at `_work/repo-workflow.md` and repo-specific additions in
`_work/local-workflow.md`. `make repo-tour` reports workflow-copy drift for
visibility; drift does not initially fail workflow checks. See
`docs/repo-workflow-installation.md` for adoption and update procedures.
Use `make check-repo-workflow` for strict validation of this repository's copy.

Do not treat arbitrary data CSV files as governance surfaces merely because
they are CSV. External datasets, analysis inputs, exports, and fixtures remain
repo-local data unless a workflow or registry README explicitly governs them.

Plans that need outcome review should include a verification-of-effectiveness
section with objectives achieved, evidence, residual risks, follow-on actions,
and lessons learned.

## Plan Closure Review

When work appears to satisfy a plan's acceptance criteria, Codex should identify
the plan as a closure candidate and ask the user whether to close it.

Closure review should happen after verification, before marking the plan `done`.
The prompt should name the plan, summarize the evidence, and state any residual
risks or follow-on tasks. If the user confirms closure, update the plan status,
dashboard row, and Codex log. If the user does not confirm closure, leave the
plan open and record any follow-up work that remains.

## Dashboard Schema

The organization-owned dashboard policy and operating procedures are defined
in `fley-org/docs/dashboard-policy-and-procedures.md`. This section provides
the point-of-work summary.

`_work/plans/plans.csv`:

```csv
id,status,track,priority,depends_on,notes
```

`_work/todo.csv`:

```csv
id,status,plan,track,priority,depends_on,notes
```

Status values:

- `todo`
- `ready`: all declared dependencies are `done`; eligible for execution
- `doing`
- `review`
- `blocked`: cannot proceed because a dependency or external condition is unfinished
- `parked`
- `done`
- `dropped`

Rows in `ready` must not have unfinished dependencies. Use `blocked` when a
declared dependency prevents execution.

Reusable dashboard policy also requires:

- rows in `doing` or `review` to have no unfinished declared dependencies
- doing todos attached to plans to have a doing parent plan
- valid statuses, priorities, references, dependency syntax, and acyclic graphs
- active plan rows and plan files to remain synchronized

Task `track` values classify the task's functional work domain and do not
necessarily inherit from the parent plan. Release-envelope and status-relative
priority rules are repository-specific.

Priority values:

- `P0` urgent or blocking
- `P1` milestone-critical
- `P2` useful soon
- `P3` later or housekeeping

## Codex Sessions

At the start of a code-changing or content-changing session, Codex should:

- check `git status`
- inspect the relevant dashboard rows and plan files
- state the intended files before editing

During work, Codex should keep changes scoped, update dashboards when state
changes, record durable findings, and avoid unrelated modifications.

When the user says `wrap up`, `finish the session`, or equivalent, Codex should
close the session by doing workflow maintenance, not just summarizing.

When the user says `summarize`, `summarize work`, `summarize open work`, or
equivalent, Codex should inspect the planning surfaces and report the open work
without changing files.

Summarize steps:

- check `git status`
- run `make check-plans` and `make check-todo` if the targets exist, or report
  that local dashboard checkers are unavailable
- read `_work/plans/plans.csv`, `_work/todo.csv`, and `_work/todo.md`
- list non-terminal plans, grouped by status
- list open todos, grouped by plan or work front and including status,
  priority, dependencies, and notes when useful
- summarize loose open items from `_work/todo.md` if any are present
- report dashboard errors or warnings before interpreting the work surface
- do not close plans, change todo state, edit files, or commit as part of
  `summarize`

Wrap-up steps:

- check `git status`
- update `_work/todo.csv` if task state changed
- update `_work/plans/plans.csv` if plan state changed and the user approved
  closure or state movement
- identify plans whose acceptance criteria appear satisfied and prompt the user
  for closure approval before marking any plan `done`
- add or update `_work/codex-log.md` if source files changed, a task closed, a
  plan closure was explicitly approved, or later sessions need the findings
- when work originated from organization wrapup, ensure its plans, todos,
  notes, or routing decisions are recorded in authoritative surfaces before
  considering the originating conversation reconciled
- run or report the narrowest useful verification
- report files changed, verification, blockers or follow-up tasks, and whether
  changes remain uncommitted

When the user says `commit this session`, Codex should perform the wrap-up
steps first, then commit. Do not commit unless the user explicitly asks for a
commit.

## Routing Boundaries

Routing means selecting the authoritative owning surface and recording the work
there. Do not duplicate executable state in registries or unrelated repository
dashboards. Keep a coordination pointer in `fley-org` only when cross-repository
visibility or temporary delegation tracking is needed.

Route work to:

- `fley-org` for organizational topology, portfolio, authority, publication
  registry, and enterprise-level coordination
- `fley-qms` for controlled SOP, WI, CAPA, Change Control, and controlled
  process governance
- execution repositories for implementation and operational tasks
