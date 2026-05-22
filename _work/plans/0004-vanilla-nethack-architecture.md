# 0004 - Vanilla NetHack Architecture

## Goal

Produce a quality-engineering description of the vanilla NetHack 5.0.0
architecture before deciding the durable Nexus architecture.

This plan exists because Nexus should preserve NetHack systems and replace
NetHack world assumptions deliberately. That requires a clear description of
the upstream engine as it actually is, not an imagined clean architecture.

The result should be an engineering reference that explains the runtime
architecture, data flow, state ownership, and hardwired assumptions well enough
to guide safe Nexus changes.

## Scope

In scope:

- new-game startup and initialization order
- command loop and turn progression at the level needed to understand movement,
  messages, inventory, monsters, objects, and persistence
- dungeon topology initialization from `dat/dungeon.lua`
- special-level registration and Lua level loading
- ordinary level generation versus special-level generation
- object and monster initialization, identity tables, and save-format
  assumptions
- branch, quest, Sokoban, endgame, and other major world-specific special cases
- Lua/C interfaces and where data becomes compiled engine state
- major global state structures and how they shape module responsibilities
- architecture risks for downstream projects that want to replace world
  assumptions

Out of scope:

- designing Nexus-specific systems
- changing code
- rewriting NetHack architecture into a preferred shape
- exhaustive function-by-function documentation
- importing external architecture theory or IER governance
- producing player-facing lore or gameplay design

## Deliverable

Create `_work/architecture/vanilla-nethack-architecture.md`.

The document should be factual and source-grounded. It should describe the
architecture in layers or subsystems, but only where those layers are supported
by the code. It should call out places where NetHack is intentionally coupled
through globals, compile-time tables, or canonical dungeon assumptions.

Suggested sections:

- startup and game lifecycle
- command loop and turn model
- world topology and dungeon graph
- level creation and loading
- Lua special-level system
- objects and inventory
- monsters and actors
- player state and role/race initialization
- branches, Quest, Sokoban, endgame, and other world rules
- save/restore interfaces and persistence responsibilities
- data files, generated files, and compiled tables
- architecture constraints for world replacement
- glossary of important structs, globals, and files

## Starting Questions

1. What are the main runtime phases from process startup to first player turn?
2. Which subsystems are initialized before dungeon topology, and which depend on
   topology already existing?
3. How does `dat/dungeon.lua` become C structures, and what invariants does the
   engine expect after loading it?
4. How are Lua special levels registered, selected, loaded, and finalized?
5. Which parts of level generation are data-driven, and which are hardwired C
   behavior?
6. How are object and monster identities represented in compiled tables,
   headers, and saves?
7. Which features look like branch-local rules but are implemented as global
   engine checks?
8. Which canonical levels, branches, and globals are assumed by code outside
   dungeon initialization?
9. Which interfaces are stable enough for Nexus to build on, and which are
   implementation details that should be treated carefully?
10. What architecture facts must be known before moving items, monsters, lore,
    or branch rules into Lua-authored data?

## Investigation Sequence

1. Trace startup from `main()` or the relevant platform entry point through
   `newgame()` and first level creation.
2. Trace `init_dungeons()` and the `dat/dungeon.lua` loading path into internal
   topology structures.
3. Trace `mklev()`, `makelevel()`, `makemaz()`, and `load_special()` enough to
   explain ordinary and special level creation.
4. Inspect object and monster table initialization, generated headers, and save
   references.
5. Inspect representative branch/world special cases, starting with Sokoban,
   Quest, Oracle, Gehennom, and endgame.
6. Document the global state and structs that define architecture constraints.
7. Summarize the implications for projects that replace the canonical world.

## Acceptance Criteria

- `_work/architecture/vanilla-nethack-architecture.md` exists and is
  source-grounded
- the document explains startup, topology, level loading, object/monster data,
  branch rules, and save/restore responsibilities at engineering depth
- claims are tied to specific files or structs where practical
- the document distinguishes data-driven surfaces from hardwired C assumptions
- risks and constraints for Nexus architecture are explicitly called out
- no runtime behavior changes are made by this plan

## Status

Done.
