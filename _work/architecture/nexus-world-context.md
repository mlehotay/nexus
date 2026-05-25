# Nexus World Context

Date: 2026-05-25

Status: initial architecture note for `0007-nexus-build-world-context`.

Scope: define a small, source-grounded direction for tying Nexus world identity
to loaded dungeon topology and build/resource validation. This is not a
general modular engine design, a gameplay plan, or a rewrite proposal.

## Summary

Nexus needs an engine-visible world context, but the first version should be
small and tied to NetHack's existing dungeon loading path.

The current Nexus build identity is compile-time and resource-driven:

- `sys/unix/hints/nexus-local` defines `-DNEXUS`;
- `src/dungeon.c` selects `nexus-dungeon.lua` when `NEXUS` is defined;
- `dat/nexus-dungeon.lua` defines the Nexus topology;
- `dat/nexus-start.lua` defines the first handcrafted level.

That is enough to boot, but not enough to prove that the binary, installed
resources, loaded topology, savefiles, and bonesfiles all describe the same
world. The next step is to let the loaded dungeon data declare what world it
is and what canonical NetHack features it provides or intentionally omits.

## Current Source Anchors

NetHack already has places where this belongs.

### Dungeon Loading

`init_dungeons()` in `src/dungeon.c` initializes a private Lua state, loads
`DUNGEON_FILE`, reads the global Lua `dungeon` table, and fills the internal
dungeon, branch, and special-level structures.

Nexus currently changes only `DUNGEON_FILE`:

```c
#ifdef NEXUS
#define DUNGEON_FILE "nexus-dungeon.lua"
#else
#define DUNGEON_FILE "dungeon.lua"
#endif
```

This is the right first switch point. World context should be read during this
same loading phase, not from a separate startup path.

### Saved Dungeon Globals

`include/decl.h` defines `struct instance_globals_saved_d`, exposed through
the saved dungeon-global group `svd`. It already contains:

- `dungeons[MAXDUNGEON]`;
- `dungeon_topology`;
- down-destination state;
- doors;
- object discovery data.

This is the closest existing equivalent to a "dungeon global" area. If world
context remains about loaded topology and dungeon capabilities, it should live
near this group or in a clearly adjacent saved structure. Do not create an
unrelated global just because `struct you u` exists for the player.

### Save And Bones Versioning

Save and bones files already carry compatibility data. `store_version()` writes
critical structure-size bytes plus `struct version_info`, and `validate()`
checks those values before restore or bones load.

This machinery is useful for persisted-file compatibility, but it does not
validate that a new-game Nexus binary is paired with the correct installed Lua
data. World context should therefore have two jobs:

- startup/resource validation for new games;
- persisted-world compatibility for save and bones files when Nexus world
  state becomes durable.

### `suppress_alert`

`OPTIONS=suppress_alert:5.0.0` is not compatibility machinery. It stores a
feature-alert threshold in `flags.suppress_alert` so code can suppress warnings
about known version-specific feature changes. It should not be used for Nexus
identity, resource validation, or save/bones compatibility.

## Proposed Data Shape

Add a small top-level world metadata table to `dat/nexus-dungeon.lua`.

Initial sketch:

```lua
world = {
   id = "nexus",
   version = "0.1",
   canonical = false,
   features = {
      quest = false,
      sokoban = false,
      mines = false,
      gehennom = false,
      endgame = false,
      tutorial = false,
   },
}
```

For vanilla `dat/dungeon.lua`, the equivalent can initially be implicit:

```text
world id: nethack
canonical: true
canonical features present unless source inspection proves otherwise
```

Do not require upstream `dungeon.lua` to grow Nexus-owned metadata unless a
later decision explicitly accepts that divergence.

## Proposed C Shape

If data-only topology cleanup proves that C needs explicit world context, add
the smallest structure needed to answer current questions.

Candidate:

```c
struct world_context {
    char id[16];
    char version[16];
    char dungeon_file[32];
    unsigned long flags;
};
```

Candidate flags:

```text
WORLD_CANONICAL
WORLD_HAS_QUEST
WORLD_HAS_SOKOBAN
WORLD_HAS_MINES
WORLD_HAS_GEHENNOM
WORLD_HAS_ENDGAME
WORLD_HAS_TUTORIAL
```

This should not become a full rules engine. The first use is validation and
safe absence checks for canonical topology.

## Rule For Using World Context

Prefer generic topology queries first.

Good questions:

- Is there a dungeon named `The Quest`?
- Is there a registered special level named `oracle`?
- Does this topology provide an endgame branch?
- Did the loaded world declare canonical feature `quest` present?

Avoid broad world checks when a topology query is enough:

```c
if (world_is_nexus()) {
    ...
}
```

World id is useful for validation and diagnostics. Feature and topology
capability checks are better for behavior.

## Startup Validation

Nexus builds should detect mixed binary/data state early.

For `NEXUS` builds:

- `DUNGEON_FILE` must be `nexus-dungeon.lua`;
- the loaded world id must be `nexus`;
- `nexus-start` must be registered and placed at dungeon 0 level 1;
- required Nexus level files must be available through the active resource
  path, loose files or DLB;
- missing canonical features are allowed only if the world metadata says they
  are absent.

For non-`NEXUS` builds:

- `DUNGEON_FILE` must remain `dungeon.lua`;
- startup should keep vanilla behavior;
- Nexus metadata or extra installed Nexus data must not change runtime
  behavior.

## Save And Bones Implications

World context becomes save/bones relevant when Nexus can persist a game beyond
the first experimental boot.

Near-term policy:

- savefiles and bonesfiles from vanilla NetHack should not be loaded into
  Nexus if the loaded topology or entity assumptions are incompatible;
- Nexus savefiles and bonesfiles should not be loaded by vanilla NetHack;
- any world-context structure added to saved state requires normal save-format
  discipline and likely an `EDITLEVEL` or feature compatibility decision.

Bones also use dungeon bone ids and level ids. If Nexus changes topology or
removes canonical branches, bones compatibility must be tested separately from
ordinary save/restore.

## Relationship To Build Isolation

`NEXUS` remains the compile-time opt-in boundary. World context does not
replace it.

Use both layers:

- compile-time `NEXUS` decides whether Nexus code and data selection are part
  of this binary;
- loaded world context verifies that the selected data describes the expected
  world;
- save/bones versioning protects durable files from incompatible reuse.

This avoids relying on any single mechanism for every job.

## Relationship To `0007`

Plan `0007-nexus-build-world-context` should use this note as the narrow design
target:

1. Audit current Nexus topology and build/resource leakage.
2. Reduce `dat/nexus-dungeon.lua` data-first.
3. Add only the world-context metadata needed to validate the loaded topology.
4. Add C storage or predicates only after a real blocker appears.
5. Extend verification to catch mixed binary/data state.

## Non-Goals

This note does not propose:

- an entity-component-system rewrite;
- generic mod packages;
- networking or replay;
- a declarative goal engine;
- moving monsters, objects, roles, or prayers into data;
- replacing NetHack save/restore architecture.

Those may be useful long-term ideas, but they are not the next Nexus build and
world-context step.

## Open Questions

1. Should vanilla world context remain implicit, or should `dat/dungeon.lua`
   eventually declare `world = { id = "nethack" }`?
2. Should missing canonical dungeons be represented by feature flags, nullable
   dungeon numbers, or direct topology queries?
3. Which current hardwired name lookups must tolerate absence before
   `dat/nexus-dungeon.lua` can become tiny?
4. Should Nexus immediately disable bones while topology is unstable?
5. Should world id/version be included in paniclog or `#version` output for
   developer diagnostics?
