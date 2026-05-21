# Nexus Developer Guide

This is the working orientation for Nexus development in this NetHack 5.0.0
tree. Nexus keeps NetHack's engine and simulation systems, but replaces the
canonical world assumptions gradually and deliberately.

## Core Rule

Prefer data and topology changes before engine surgery.

For the first milestone, start with:

- `dat/dungeon.lua`
- one handcrafted Lua level file under `dat/`
- the smallest possible build/install adjustment needed to launch Nexus

Do not begin by making a full roguelike, adding procedural generation, or
rewriting NetHack systems that are not yet blocking the tiny custom world.

## Branches

- `nexus` is the integration branch.
- Nontrivial work should happen on short work branches, for example
  `work/0002-boot-custom-level`.
- Do not work directly on upstream branches such as `NetHack-5.0`.

The normal Nexus workflow is:

```text
official NetHack 5.0.0 release tag
        |
        v
      nexus
        |
        v
  work/small-feature
        |
        v
      nexus
```

That means feature branches start from `nexus`, not from the official NetHack
5.0.0 tag or an upstream NetHack branch. The upstream release tag is the
ancestor Nexus began from. Once Nexus has local setup, documentation, install
rules, and world changes, new work needs those Nexus changes as its base.

Branch from the upstream tag only when you are deliberately creating a new
integration line from upstream NetHack. That is not the ordinary feature
workflow.

To start a feature branch:

```sh
git switch nexus
git status --short
git switch -c work/0002-boot-custom-level
```

If `nexus` has moved elsewhere and this checkout tracks a remote, update it
before creating the branch:

```sh
git switch nexus
git pull --ff-only
git switch -c work/0002-boot-custom-level
```

Do the work on the feature branch. Keep commits focused. For commits touching
NetHack source, data, docs, or build files, use the keyword-aware helpers:

```sh
git nhadd <paths>
git nhcommit
```

To merge the finished work back into `nexus`:

```sh
git switch nexus
git merge --no-ff work/0002-boot-custom-level
```

Resolve conflicts if Git reports any, run the narrowest useful verification,
then commit the merge if Git did not do so automatically. If the merge touches
files with FLEY substitution variables, run `git nhadd <paths>` before the
final merge commit.

After the merge is complete and no longer needed locally, the short branch can
be deleted:

```sh
git branch -d work/0002-boot-custom-level
```

Use `git branch -d`, not `-D`, so Git refuses to delete a branch whose commits
have not been merged.

Before editing, check the worktree:

```sh
git status --short
```

Work with any existing user changes. Do not revert unrelated changes.

## Where Files Belong

Use the normal NetHack tree for active Nexus runtime and build files:

- `dat/` for world topology, Lua levels, and data packaged into `nhdat`
- `sys/unix/` for Unix runtime and install inputs
- `sys/unix/hints/` for Unix build/install profiles
- `src/`, `include/`, and `util/` only when data cannot express the behavior

Use `_work/` for coordination: plans, tasks, session summaries, divergence
notes, and the provisional Nexus setup guides while these policies are still
changing. It is not runtime content or build input.

Move a guide into `doc/` later if it becomes stable player/developer
documentation rather than active setup policy.

## NetHack Keyword Substitution

NetHack has its own RCS/CVS-style keyword substitution workflow layered on top
of Git. It is installed by `DEVEL/nhgitset.pl` and exposed through local Git
aliases:

```sh
git nhadd <paths>
git nhcommit
git nhsub <paths>
```

In this repository, the local config is:

```sh
nethack.substprefix=FLEY
nethack.projectname=Nexus
```

`nethack.substprefix` controls which keyword prefix is rewritten. For Nexus,
only `$FLEY-...$` variables are rewritten. Existing upstream `$NHDT-...$`
variables are not touched by `git nhadd`, because `NHDT` is not this repo's
configured prefix.

The common first line in C source files looks like this:

```c
/* NetHack 5.0  file.c  $NHDT-Date: ... $  $NHDT-Branch: ... $:$NHDT-Revision: ... $ */
```

Those fields mean:

- `Date`: last substitution date, normally the time `git nhadd`, `git nhcommit`,
  or `git nhsub` rewrote the file
- `Branch`: current Git branch at substitution time
- `Revision`: an RCS-style value based on the number of commits that affected
  that file
- `Brev`: a combined `Branch:Revision` form used in some files
- `Project`: the configured project name, here `Nexus`, where a file uses it

The substitution only runs for files selected by `.gitattributes`. Currently
this covers C headers, C sources, C++ files, shell scripts, Perl scripts,
`Porting`, and `README`.

## NHDT Versus FLEY

Treat `$NHDT-...$` as upstream NetHack metadata. Treat `$FLEY-...$` as Nexus
metadata.

Rules for Nexus work:

- Leave untouched upstream files exactly as they are, including `$NHDT-...$`
  headers.
- When a Nexus commit intentionally changes a NetHack-owned source, header,
  script, or build file that already has an `$NHDT-...$` first-line header and
  is handled by `NHSUBST`, convert that header to `$FLEY-...$` in the same
  commit.
- Convert only files you are already changing. Do not bulk-convert the tree.
- For a new Nexus-owned source file, use the existing NetHack header style but
  with unexpanded FLEY variables:

```c
/* NetHack 5.0  newfile.c  $FLEY-Date$  $FLEY-Branch$:$FLEY-Revision$ */
```

Then stage with `git nhadd`; it will expand the fields.

Do not hand-maintain the timestamp, branch, or revision values. Either write
unexpanded variables such as `$FLEY-Date$`, or change the prefix from `NHDT` to
`FLEY` and let `git nhadd` refresh the values.

You do not need to add these comments to existing files that do not already use
them. For new C source or header files, copy the local NetHack header style and
use FLEY variables from the start.

## Staging And Committing

For NetHack source, data, documentation, or build files, prefer:

```sh
git nhadd <paths>
git nhcommit
```

`git nhadd` is essentially:

```sh
git nhsub <paths>
git add <paths>
```

`git nhcommit` is essentially:

```sh
git nhsub <paths>
git commit
```

The goal is to run `nhsub` immediately before Git snapshots the file.

Plain `git add` is acceptable for files that should not go through NetHack
keyword substitution. It is also acceptable after you have already run
`git nhsub <paths>` yourself.

If you accidentally use plain `git add` on a file that should have had FLEY
keywords refreshed, nothing catastrophic happens. The metadata just remains
stale. Run `git nhadd <paths>` before committing.

## Useful Keyword Commands

Preview substitution without writing:

```sh
git nhsub -n -v <paths>
```

Force substitution for already clean files:

```sh
git nhsub -f <paths>
```

Use metadata to reconstruct dates from file history:

```sh
git nhsub -m -f <paths>
```

Do not immediately follow `git nhsub -m` with `git nhadd` or `git nhcommit`,
because those commands rerun `nhsub` and replace the metadata date with the
current date.

## Merges

The repository config installs a merge driver named `NHsubst`. It knows how to
resolve simple one-line conflicts in substitution variables for the configured
prefix. For Nexus, that means FLEY variables.

This helps prevent metadata-only conflicts, but it is not a substitute for
reviewing real source conflicts.

## Divergences

Record intentional upstream divergences in `_work/divergences.md` when they
change compatibility, topology, startup behavior, build assumptions, or NetHack
system semantics.

Record at least:

- date
- plan id
- files changed
- upstream assumption changed
- why data-only configuration was not enough, if C changed

Ordinary content edits do not need divergence entries.

## Local Unix Build

Use the Nexus local hints profile:

```sh
sh sys/unix/setup.sh sys/unix/hints/nexus-local
make all
make install
```

The local profile installs Nexus under `~/games/nethack/nexus/` and provides a
separate `nexus` launcher so this tree does not collide with other NetHack
builds.

Use the narrowest useful verification for the change. For early boot work, a
small smoke test that reaches the NetHack character prompt or launches the
custom level is more useful than broad unrelated testing.
