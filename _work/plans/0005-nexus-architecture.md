# 0005 - Nexus Architecture

## Goal

Define the durable architecture for Nexus as a small standalone world on the
NetHack 5.0.0 engine.

This plan depends on `0004-vanilla-nethack-architecture`. Nexus architecture
should start from a quality-engineering description of vanilla NetHack 5.0.0,
then decide which upstream assumptions to preserve, wrap, replace, or leave
inert.

The architectural direction is:

```text
NetHack 5 engine in C
Lua-authored dungeons and world data
a Nexus dungeon-logic layer for branch-specific rules
separate but intersecting content layers for lore, characters, monsters, and items
```

This plan should turn that direction into boundaries, module responsibilities,
open questions, and a sequence of small experiments. It should not replace the
first milestone of booting one handcrafted custom level.

## Scope

In scope:

- use the vanilla NetHack architecture reference to define the systems Nexus
  should preserve
- define what belongs in Lua dungeon/topology data versus C engine code
- evaluate whether item data can be moved or mirrored into Lua without breaking
  NetHack object initialization, saves, or compile-time assumptions
- identify a narrow Nexus dungeon-logic module boundary for branch rules such
  as Sokoban-style puzzle rules, local traversal constraints, and branch-local
  state
- define how lore, characters, monsters, items, branches, and level scripts
  should reference each other without becoming one large global content file
- record intentional upstream divergences when architecture decisions replace
  canonical NetHack assumptions
- keep architecture work grounded in small bootable experiments

Out of scope:

- building a full conversion before the first custom level boots
- procedural generation as an initial requirement
- redesigning combat, roles, races, alignment, or ascension systems up front
- importing Floating Eye or IER systems
- defining final lore canon before the runtime boundaries are understood
- broad C refactors that are not forced by a tested architecture need

## Proposed Layers

### Engine Layer

The engine layer is NetHack 5 C code that Nexus should preserve wherever
possible:

- command loop, movement, line of sight, messages, persistence, inventory, and
  object/monster simulation
- level creation and loading machinery
- save/restore and window-port behavior
- special-level Lua loader and dungeon topology initialization

Nexus changes to this layer should be minimal, explicit, and recorded as
upstream divergences.

### World Topology Layer

The topology layer describes which places exist and how they connect.

Initial home:

- `dat/dungeon.lua`
- custom Lua level files under the normal NetHack data tree

Near-term goal:

- make dungeon 0 level 1 a Nexus-authored place
- avoid canonical branch and endgame dependencies unless they are still needed
  as inert compatibility structure

### Dungeon Logic Layer

The dungeon logic layer is the proposed new Nexus module boundary for rules that
belong to places and branches rather than to the global engine.

Candidate responsibilities:

- branch-local rule hooks, such as Sokoban block movement or puzzle completion
- local environmental constraints
- branch-local state and progression flags
- level-entry and level-exit behavior that is not merely topology
- lightweight integration between Lua-authored levels and C simulation events

This layer should be designed after inspecting existing special cases in
NetHack, especially Sokoban, Quest, Gehennom, endgame, branch traversal,
achievements, and level flags. The first version may be a thin C module with
clear hooks rather than a large framework.

### Content Data Layer

The content data layer covers data that Nexus may eventually author in Lua or
other structured files:

- items and object identities
- monsters and creature identities
- characters and named entities
- branch and place metadata
- lore references and presentation text

This layer should avoid premature migration. NetHack object and monster data
have compile-time and save-format assumptions, so any Lua move must be tested
as a small experiment before becoming policy.

### Lore And Meaning Layer

Lore is not just prose. It intersects with:

- topology: where things are
- characters: who exists
- monsters: what creatures mean in this world
- items: what objects are called and used for
- branch logic: what local rules express about a place
- messages: what the player sees

The architecture should let lore annotate or bind these systems without making
runtime code depend on a single monolithic story file.

## Open Questions

1. What is the smallest stable interface between C level events and
   branch-local dungeon logic?
2. Should Nexus dungeon logic be C-first, Lua-first, or a C module that exposes
   carefully chosen Lua hooks?
3. Which existing NetHack special cases are branch rules disguised as global C
   checks?
4. Can Sokoban rules be isolated as the first model for branch-local logic, or
   are they too entangled to serve as the pattern?
5. Which parts of `objects.c`, `monst.c`, and related headers must remain
   compiled data for save compatibility and engine assumptions?
6. Can items be authored in Lua and compiled/generated into NetHack tables, or
   should Lua item data initially be descriptive metadata layered over existing
   object definitions?
7. How should named characters differ from monsters mechanically and in data?
8. Should lore references live beside levels, beside entities, or in a separate
   registry with stable ids?
9. What ids need to be durable across saves: branches, places, characters,
   monsters, objects, lore entries, puzzle state, or all of them?
10. How much canonical topology must remain as compatibility scaffolding while
    Nexus replaces the starting world?
11. Which canonical systems should be left inert for a long time instead of
    removed: Quest, endgame, Gehennom, Oracle, alignment, achievements, or
    branch-specific messages?
12. Where should Nexus draw the line between data-only replacement and an
    explicit upstream divergence in C?

## Investigation Sequence

1. Complete or advance `0004-vanilla-nethack-architecture` enough to identify
   the relevant upstream boundaries and hardwired assumptions.
2. Complete or advance `0002-boot-custom-level` enough to prove the custom
   starting topology.
3. Inspect existing C special cases for branch-local behavior, starting with
   Sokoban and Quest.
4. Classify each special case as topology data, level data, branch logic,
   content data, or global engine behavior.
5. Draft the smallest possible dungeon-logic module boundary.
6. Prototype one narrow hook only after a real branch rule needs it.
7. Inspect object and monster initialization paths before deciding whether Lua
   content data can own items or creatures.
8. Define stable ids and file ownership rules for lore, characters, monsters,
   places, and items.

## Acceptance Criteria

- architecture decisions are grounded in
  `_work/architecture/vanilla-nethack-architecture.md`
- architecture notes identify the preserved C engine boundary
- topology, dungeon logic, content data, and lore layers have clear
  responsibilities
- branch-local rule examples are traced to current NetHack code
- item and monster Lua migration questions are answered by source inspection,
  not assumption
- at least one small experiment validates or rejects the proposed dungeon-logic
  boundary
- intentional upstream divergences discovered during the work are recorded in
  `_work/divergences.md`
- follow-up executable tasks are added to `_work/tasks.csv` when the questions
  become concrete implementation work

## Status

Todo.
