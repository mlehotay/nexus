# 0007 - Nexus Build World Context

## Goal

Clean up the current Nexus build surface and define how world context is tied
to the loaded dungeon topology inside the engine.

This plan starts from the post-`0002`, `0004`, and `0006` state: Nexus can boot
into one handcrafted Lua level, the vanilla NetHack architecture has been
surveyed, and the boot behavior has a repeatable verification procedure.

The next question is narrower than `0005-nexus-architecture`: before designing
durable Nexus content layers, determine where the current Nexus build still
carries canonical Dungeons of Doom assumptions and what minimal engine-visible
world context should replace implicit assumptions.

`_work/architecture/nexus-world-context.md` is the source-grounded design note
for this plan. It narrows the target to loaded-world metadata, topology
capability checks, startup resource validation, and save/bones compatibility
implications without proposing a general engine rewrite.

## Problem Statement

The current Nexus implementation proves the first milestone but remains a
thin overlay on upstream topology.

`NEXUS` builds currently:

- load `dat/nexus-dungeon.lua` instead of `dat/dungeon.lua`;
- start on `dat/nexus-start.lua`;
- show `Nexus` in `#overview`;
- avoid showing `Dungeons of Doom` in the basic smoke path.

However, `dat/nexus-dungeon.lua` still contains most of the canonical NetHack
branch graph and level registry. The engine also resolves several canonical
dungeon names into global dungeon numbers and exposes many special-level and
branch predicates through `include/dungeon.h`.

The build therefore has two related cleanup needs:

- make Nexus build and install outputs less ambiguous and less prone to mixed
  vanilla/Nexus resource state;
- make loaded world identity explicit enough that C code can ask about the
  active world or topology contract instead of assuming that dungeon 0 and the
  canonical branch names imply the Dungeons of Doom.

## Scope

In scope:

- inventory current Nexus build outputs, installed resources, and generated
  state that can mix vanilla and Nexus assumptions;
- identify where canonical Dungeons of Doom assumptions still leak into Nexus
  builds after the first boot milestone;
- reduce `dat/nexus-dungeon.lua` toward the smallest topology that still boots
  and satisfies engine invariants;
- determine which canonical names are required by C initialization versus only
  retained by copied data;
- design the smallest world-context representation tied to the loaded dungeon
  file or parsed dungeon topology;
- keep vanilla NetHack behavior unchanged when `NEXUS` is not defined;
- update verification so the new checks catch accidental returns to canonical
  topology or mixed resource state;
- record intentional upstream divergences when Nexus removes or replaces
  canonical topology assumptions.

Out of scope:

- final Nexus lore architecture;
- broad content migration for roles, monsters, objects, quest text, or
  ascension;
- procedural generation;
- replacing combat, inventory, persistence, or display systems;
- designing a full dungeon-logic framework before a concrete rule needs it;
- closing `0005-nexus-architecture`.

## Current Leak Inventory

### Topology Data

`dat/nexus-dungeon.lua` is the primary leak. It renames dungeon 0 to `Nexus`
and adds `nexus-start` at level 1, but otherwise retains much of upstream
topology:

- The Gnomish Mines
- Sokoban
- The Quest
- Fort Ludios
- Gehennom
- The Elemental Planes
- Rogue level
- Oracle
- Big Room
- Medusa
- Castle
- Vlad's Tower
- Tutorial

This makes Nexus visibly small at startup but internally still shaped like
canonical NetHack.

### Engine Name Binding

`src/dungeon.c` hardwires several dungeon names after Lua topology loading:

- `The Quest`
- `Sokoban`
- `The Gnomish Mines`
- `Vlad's Tower`
- `The Tutorial`

These names become global dungeon numbers used by predicates such as
`In_quest()`, `In_mines()`, `In_sokoban()`, and `In_V_tower()`.

### Special-Level Predicates

`include/dungeon.h` exposes canonical special-level predicates for Astral,
elemental planes, Medusa, Oracle, Valley, demon lairs, Wizard tower, Sanctum,
Rogue, Castle, Big Room, Quest levels, Knox, Mines end, and Sokoban end.

These predicates are not just display helpers; they drive generation,
movement, teleport, scoring, achievements, prayers, monster behavior, traps,
and map overview behavior.

### Level Generation

`src/mklev.c` still contains branch and special-level decisions for Quest,
Gehennom, Medusa, Mines, Rogue, Fort Ludios, and other canonical regions.

Some of those decisions are harmless while the corresponding topology is
absent. Others may panic or misbehave if a named dungeon or special level is
removed without an engine compatibility strategy.

### Build And Resource Packaging

`sys/unix/hints/nexus-local` defines `-DNEXUS` and adds `NEXUSDAT`, but
`sys/unix/Makefile.top` still packages the full upstream data set, including
canonical special levels and quest levels.

This is acceptable for the first milestone, but it should be audited so Nexus
does not depend on accidental loose-file availability or stale installed data.

### Runtime Lore And Presentation

The basic boot smoke path still shows upstream role and quest framing text,
including Moloch, the Amulet of Yendor, Gehennom, and deity names. That is a
known leak, but it should not drive this plan unless the text blocks build or
world-context cleanup.

## Investigation Sequence

1. Capture the exact current Nexus build and install surface:
   compiled macros, installed data files, launcher behavior, generated
   makefiles, `nhdat` or loose-file assumptions, save directory, bones state,
   and local rc/sysconf inputs.
2. Audit `dat/nexus-dungeon.lua` against `dat/dungeon.lua` and classify every
   retained dungeon, branch, and special level as required, inert
   compatibility scaffolding, accidental copy-through, or intentionally
   preserved for later.
3. Try the smallest data-only topology reduction in a work branch:
   keep dungeon 0 and `nexus-start`; remove or neutralize one canonical
   branch family at a time; run the existing pty smoke test after each
   reduction.
4. When a removal fails, trace the failure to the exact C assumption:
   missing hardwired dungeon name, missing special-level global, level
   generation branch, map overview, teleport, scoring, achievement, or other
   subsystem.
5. Decide whether each blocker should be handled by data scaffolding,
   guarded Nexus C behavior, or deferred inert compatibility.
6. Design a minimal world-context structure or API tied to loaded topology.
   Candidate questions:
   - Which dungeon file or parsed metadata identifies the active world?
   - Does the engine need a `world_id`, feature flags, named-level registry, or
     topology capability flags?
   - Should Nexus context live in `svd.dungeon_topology`, a new world-context
     struct, or Nexus-owned guarded source?
   - Which checks should remain generic topology queries rather than
     `#ifdef NEXUS` branches?
7. Add verification checks for any accepted cleanup:
   startup still reaches Nexus, `#overview` remains Nexus-only for visited
   topology, removed canonical branches are not visible, and non-Nexus builds
   still boot into Dungeons of Doom.
8. Update `_work/divergences.md` for every intentional upstream divergence.

## Candidate Implementation Directions

### Data-First Cleanup

Start by reducing `dat/nexus-dungeon.lua`. This respects the Nexus boundary of
changing topology before engine surgery.

Preferred outcome:

- a tiny `Nexus` dungeon with only the levels and exits required for the
  current milestone;
- canonical branch data removed unless it is proven necessary;
- any remaining compatibility scaffolding documented in comments and
  `_work/divergences.md`.

### Explicit World Context

If data-only cleanup exposes hard engine assumptions, add the smallest
engine-visible world context described by
`_work/architecture/nexus-world-context.md`.

Possible forms:

- a parsed top-level `world = { id = "nexus", ... }` table in
  `dat/nexus-dungeon.lua`;
- a loaded dungeon file identifier for diagnostics and validation;
- topology capability flags or nullable canonical dungeon ids;
- generic topology queries that can answer whether Quest, Sokoban, Mines,
  Gehennom, endgame, or tutorial are present;
- a Nexus-only guarded fallback for missing canonical dungeons during
  `init_dungeons()`, only if topology queries and metadata are not enough.

The preferred design should let C ask direct questions such as "does this
loaded topology provide Quest?" or "does this world use canonical endgame?"
rather than treating missing names as impossible.

### Build Isolation

Audit whether Nexus should install only Nexus-required Lua data in the local
profile or continue installing all upstream data while the world is in flux.

Near-term build cleanup should focus on avoiding accidental stale state:

- require clean rebuilds when switching `NEXUS`;
- verify installed `nexus-dungeon.lua` and `nexus-start.lua`;
- detect when a Nexus binary is paired with missing Nexus data;
- detect when a non-Nexus binary accidentally loads Nexus data.

## Acceptance Criteria

- the current Nexus build leak inventory is recorded with file and subsystem
  references;
- `dat/nexus-dungeon.lua` has been audited and each retained canonical dungeon
  or special level has a reason;
- at least one topology-reduction experiment has been attempted and verified,
  or a concrete blocker has been traced to source;
- the plan identifies the smallest needed world-context representation, or
  records that data-only cleanup remains sufficient for now;
- any proposed world-context implementation is evaluated against
  `_work/architecture/nexus-world-context.md`;
- any C changes are guarded or structured so non-`NEXUS` builds preserve
  vanilla NetHack behavior;
- verification covers Nexus-enabled and NEXUS-disabled boot after cleanup;
- `_work/divergences.md` records intentional upstream topology or engine
  divergence;
- follow-up executable tasks are added to `_work/tasks.csv` when the work is
  ready to implement.

## Open Questions

1. Can `dat/nexus-dungeon.lua` remove Quest, Sokoban, Mines, Gehennom, and
   endgame immediately, or do hardwired name lookups require inert stubs?
2. Should the loaded dungeon file itself define a world id, or should `NEXUS`
   builds infer world identity from compile-time configuration?
3. Should world context describe named canonical features as absent/present,
   or should C code query the parsed topology directly?
4. Which canonical globals can safely be left unassigned, and which macros or
   predicates assume that their target level always exists?
5. Should missing canonical topology be a valid Nexus condition or a startup
   error unless explicitly allowed by world metadata?
6. How should DLB packaging be tested once Nexus stops relying on loose-file
   development installs?
7. Which runtime lore leaks should remain deferred to `0005`, and which must
   be handled because they expose build/world identity confusion?

## Status

Todo.
