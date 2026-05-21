# Nexus Repository Layout

Nexus-specific files should live in the normal NetHack source tree whenever
they affect builds, installs, runtime behavior, or player-facing content.

`_work/` is coordination space. It may hold provisional Nexus workflow/setup
guides while the project conventions are still being established. Do not put
active Nexus runtime files, world files, or build inputs there.

## Durable Nexus Locations

- `dat/`
  - Nexus world topology and level content.
  - Use this for `dungeon.lua`, handcrafted Lua levels, and data that belongs
    in `nhdat`.

- `sys/unix/`
  - Unix runtime and install inputs for Nexus.
  - Use this for Nexus-specific rc/sysconf files that are installed by Unix
    hints.

- `sys/unix/hints/`
  - Unix build/install profiles.
  - `sys/unix/hints/nexus-local` is the local developer install profile.

- `_work/`
  - Provisional Nexus workflow/setup guides and coordination notes.
  - `nexus-dev-guide.md`, `nexus-layout.md`, and `nexus-player-guide.md` live
    here for now so Nexus setup policy remains encapsulated while it is still
    changing.

- `doc/`
  - Durable player/developer reference once a guide is ready to become
    long-lived project documentation.
  - Use this later for stable player-facing rc templates or explanations that
    should survive beyond temporary setup work.

- `src/`, `include/`, `util/`, and other NetHack source directories
  - Engine changes only when data/topology cannot express the Nexus behavior.
  - Keep these changes narrow and record intentional upstream divergences.

## Current Nexus Setup Files

- `sys/unix/hints/nexus-local`
  - Local Unix install profile.
  - Sets the Nexus install root, `HACKDIR`, `SYSCF_FILE`, tty build choices,
    and save compression command.

- `sys/unix/nexus.nethackrc`
  - Installed runtime rc file for the `nexus` launcher.
  - Used via `NETHACKOPTIONS=@.../nexus.nethackrc` so Nexus does not inherit a
    shared `~/.nethackrc`.

- `doc/config.nh`
  - Upstream sample user rc template.
  - Leave this as upstream unless Nexus intentionally replaces the generic
    sample. If Nexus needs its own player-facing sample later, add a separate
    `doc/nexus-config.nh`.

- `sys/unix/sysconf`
  - Upstream Unix sysconf sample/input.
  - Leave this as upstream for now. If Nexus needs a distinct system config,
    add `sys/unix/nexus.sysconf` and have `nexus-local` install it as
    `sysconf`.

## Temporary Coordination

Use `_work/` for planning and session coordination:

- tasks and plan tracking
- investigation notes
- Codex session summaries
- divergence notes before they are promoted into durable documentation
- provisional Nexus setup guides while policy remains in flux

When a note becomes a build rule, runtime default, stable player-facing
document, or source-of-truth convention, move or copy it into the appropriate
durable location above.
