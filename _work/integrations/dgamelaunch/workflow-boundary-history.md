# Repo Workflow Installation Problem

> Resolved on 2026-08-23 by establishing Nexus as workflow authority for
> dgamelaunch. This file is retained as migration history. The correct outcome
> is to keep FLEY `_work/`, `AGENTS.md`, and workflow build targets out of the
> upstream-derived dgamelaunch checkout.

## Summary

An attempt to install the FLEY repository workflow in `dgamelaunch` was paused
because the workflow installation guidance and this legacy repository's build
layout do not fit together cleanly.

The unresolved issue is how to provide the workflow's narrow local verification
command or Make target without unexpectedly changing, replacing, or becoming
coupled to dgamelaunch's existing build system.

The repo-workflow installation remains incomplete. No workflow dashboard,
`AGENTS.md`, workflow procedure, local workflow supplement, Codex log, or
workflow Make target is currently installed.

## Repository Build Layout

This repository predates FLEY and uses a generated top-level `Makefile` for its
existing dgamelaunch build.

Relevant facts:

- `Makefile.in` is tracked and contains the dgamelaunch build rules.
- `/Makefile` is explicitly ignored in `.gitignore`.
- The top-level `Makefile` does not currently exist in this checkout.
- The generated `Makefile` can be removed by the existing `distclean` target.
- Creating a new tracked top-level `Makefile` would conflict with the current
  expectation that this path is generated and ignored.
- Adding workflow targets to `Makefile.in` would modify the legacy product
  build machinery and cause generated Makefiles to include FLEY workflow
  commands.

These facts do not affect the running dgamelaunch service on `illithid` by
themselves. A local Makefile only runs commands when someone explicitly invokes
it. The concern is repository design, maintainability, and avoiding accidental
changes to a legacy build process without a deliberate decision.

## Workflow Installation Requirement

The FLEY installation guide at:

```text
../fley-org/docs/repo-workflow-installation.md
```

requires an adopted repository to:

```text
Add a narrow local verification command or Make target.
```

The guide allows local Make targets or wrappers but does not prescribe how to
handle a repository whose tracked build template generates and owns the normal
top-level `Makefile` path.

## What Happened

The requested installation began by:

1. inspecting the FLEY installation guide and canonical workflow template
2. inspecting the existing `_work/` reports and repository Git state
3. creating `_work/plans/` as an empty directory
4. copying the canonical workflow to `_work/repo-workflow.md`

During discussion of the verification command, several possible approaches
were identified:

- create a separate workflow-specific Makefile
- create a normal top-level `Makefile`
- add workflow targets to `Makefile.in`
- use a non-Make verification wrapper or documented command

The maintainer requested a normal workflow Makefile, then paused the work after
the relationship with the existing generated Makefile became unclear.

The copied `_work/repo-workflow.md` was removed. No Makefile, `Makefile.in`,
`.gitignore`, or other build file was changed. The empty `_work/plans/`
directory is not represented in Git and has no effect.

## Why Installation Was Paused

Installing most workflow surfaces would be straightforward, but completing the
installation without resolving verification ownership would leave an
ambiguous or fragile setup.

A normal tracked top-level `Makefile` would require changing `.gitignore` and
would occupy a path currently reserved for generated build output. It could
also be overwritten by the existing configuration process.

Changing `Makefile.in` would make workflow support part of the legacy product
build template. That may be appropriate, but it is a product-build decision,
not merely an administrative workflow installation detail.

A separate Makefile or wrapper would avoid changing the product build path,
but it would introduce a new invocation convention that should be intentionally
selected and documented.

## Unresolved Decision

Before resuming workflow installation, choose how this repository will expose
local workflow verification:

1. **Separate workflow Makefile**

   Use a tracked file such as `Makefile.workflow`, invoked with
   `make -f Makefile.workflow check-work`. This avoids the generated product
   Makefile path but differs from the usual `make check-work` convention.

2. **Standalone verification script**

   Use a tracked script such as `scripts/check-work` that invokes the
   organization-owned checkers. This avoids Makefile ownership entirely.

3. **Product build integration**

   Add workflow targets to `Makefile.in`, accepting that FLEY workflow support
   becomes part of the generated dgamelaunch Makefile.

4. **Tracked top-level Makefile redesign**

   Redesign the repository so a tracked top-level `Makefile` coordinates both
   workflow and product build behavior. This has the largest effect and should
   not be treated as a routine workflow installation.

5. **Documented external command only**

   Document direct invocations of `../fley-org` checks without adding a local
   wrapper. The installation guide permits a narrow local verification command,
   but this option should be confirmed as sufficient for adopted status.

## Current Safe State

- Repo-workflow adoption is incomplete.
- Existing `_work/` reports and console logs remain informational only.
- No workflow dashboards or plan files have been created.
- No product build files have been changed.
- No production server commands or changes were made.

## References

```text
.gitignore
Makefile.in
../fley-org/docs/repo-workflow-installation.md
../fley-org/templates/repo-workflow.md
_work/fley-context.md
```
