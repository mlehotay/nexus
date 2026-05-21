# NetHack Savefile and Bonesfile Architecture

Date: 2026-05-21

Scope: NetHack 5.0.0 savefiles, level files, bones files, serialization format,
Lua saved state, and implications for Nexus architecture boundaries.

This report complements:

- `_work/architecture/vanilla-nethack-architecture.md`
- `_work/architecture/nethack-build-config-resource-architecture.md`
- `_work/architecture/nethack-system-window-port-architecture.md`

## Summary

NetHack savefiles and bones files are serialized representations of world
state. They are useful architecture boundaries because they reveal what the
engine considers durable game state, what is level-local, what is global, and
what must be reconstructed after loading.

The short answer to the format question:

- NetHack 5 has a newer savefile abstraction, `NHFILE`, with explicit
  serializer functions for many structs and primitive types.
- It still defaults to the historical binary struct-level format for ordinary
  gameplay savefiles, temporary level files, and bones files in this tree.
- It is not a Lua-native save format.
- Lua contributes a small serialized string for `nh_lua_variables`, but the
  world state is still C state: structs, chains, arrays, counters, flags,
  object lists, monster lists, level maps, and dungeon topology.
- There is an export-ascii / field-level framework and utility code, but the
  normal savefile and bonesfile creation paths currently force historical
  struct-level mode.

For Nexus, this means save/bones boundaries are meaningful scope boundaries,
but not convenient high-level data APIs. They are lower-level persistence
contracts tied to C structs and compatibility checks.

## File Types

NetHack uses the `NHFILE` abstraction for three related persistence surfaces:

- `NHF_LEVELFILE`: temporary per-level files used while a game is in progress.
- `NHF_SAVEFILE`: full save files used by `#save`, hangup save, restore, and
  checkpoint/recovery paths.
- `NHF_BONESFILE`: partial world-state files created from a dead character's
  level and later imported into another game.

The `NHFILE` object stores:

- the file descriptor or `FILE *`;
- read/write/free/convert mode flags;
- file type;
- selected save format index;
- whether the file is `structlevel` or `fieldlevel`;
- whether content is binary;
- logging/debug pointers;
- endian state;
- optional conversion target.

The relevant definitions are in `include/hack.h`:

```c
enum saveformats {
    invalid = 0,
    historical = 1,     /* entire struct, binary, as-is */
    exportascii = 2,    /* each field written out as ascii text */
    NUM_SAVEFORMATS
};
```

That comment is the important anchor: historical mode is still whole-struct
binary serialization.

## Serialization Layer

The serialization layer is split across:

- `include/savefile.h`: public `Sfo_*` and `Sfi_*` serializer declarations.
- `include/sfprocs.h`: serializer procedure tables.
- `include/sfmacros.h`: shared macro list of types to generate serializers for.
- `src/sfbase.c`: dispatch layer that chooses struct-level or field-level
  serializer functions based on the active `NHFILE`.
- `src/sfstruct.c`: historical binary struct-level serializer implementation.
- `util/sfexpasc.c`: export-ascii field-level implementation.
- `util/sfctool.c`: conversion/inspection utility for savefile formats.

The normal code calls functions/macros such as:

- `Sfo_int`, `Sfi_int`;
- `Sfo_obj`, `Sfi_obj`;
- `Sfo_monst`, `Sfi_monst`;
- `Sfo_rm`, `Sfi_rm`;
- `Sfo_you`, `Sfi_you`;
- `Sfo_dungeon`, `Sfi_dungeon`;
- `Sfo_s_level`, `Sfi_s_level`.

Those calls make save/restore code read like field-level serialization even
when the active implementation is historical binary struct dumps. In historical
mode, `src/sfstruct.c` ultimately writes or reads the full struct with
`bwrite()` and `mread()`.

This is a major difference from old direct call sites, but not a complete
semantic break from the NetHack 3.x model. The representation is still deeply
struct-shaped.

## Active Format In This Tree

`sf_init()` registers the available serializers:

- `historical` gets struct-level read/write procedures.
- `exportascii` gets field-level procedure slots, but runtime registration is
  not enough to make gameplay saves use it.

Actual file creation is decisive:

- `create_levelfile()` sets level files to struct-level, binary, historical.
- `open_levelfile()` expects struct-level, binary, historical.
- `create_savefile()` currently has `boolean do_historical = TRUE` and sets
  savefiles to struct-level, binary, historical.
- `open_savefile()` also forces historical mode.
- `create_bonesfile()` and `open_bonesfile()` contain scaffolding for
  `sysopt.bonesformat`, but creation opens the historical path in the current
  code.

So normal Nexus developer builds should be assumed to use historical binary
savefiles and bonesfiles unless this code is intentionally changed and tested.

## Savefile Lifecycle

The normal save path starts in `dosave()` and `dosave0()` in `src/save.c`.

High-level flow:

1. suppress status/inventory updates and clean transient in-progress state;
2. open or create the savefile with `create_savefile()`;
3. write version/critical-byte metadata with `store_version()`;
4. write player name;
5. write the current level with `savelev()`;
6. write global game state with `savegamestate()`;
7. load every other existing level file, write that level into the savefile,
   and delete the temporary level file;
8. close the savefile;
9. delete lock/current level files;
10. run savefile conversion/compression hooks.

`savegamestate()` persists global state that is not just the current map:

- user id and Nexus/NetHack UUID;
- move counter and context;
- flags;
- player struct `u`;
- realtime fields;
- killers;
- global timers and light sources;
- inventory;
- ball and chain edge cases;
- migrating objects and monsters;
- monster vital statistics;
- dungeon topology and level-info chain;
- quest status;
- spellbook state;
- artifacts and oracle state;
- player role/race string fields;
- fruit definitions;
- object/monster names;
- message history;
- gamelog;
- Lua variables.

That list is a practical map of "global durable game state."

## Level File and Level State

The in-progress game has per-level files, distinct from the final full
savefile. Level files are temporary persistence for levels the player has
visited but that are not currently resident in memory.

`savelev()` and `savelev_core()` serialize a level. The level payload includes:

- process id and ledger number;
- cemetery/bones information;
- `levl[x][y]` map cells;
- `lastseentyp`;
- timestamp/move marker;
- stairs and destination areas;
- level flags;
- doors and rooms;
- level timers and light sources;
- monsters;
- worms;
- traps;
- floor objects;
- buried objects;
- bill objects;
- engravings;
- shop damage;
- regions;
- bubbles/clouds for Water/Air levels;
- exclusion zones;
- tracks.

That is the natural level-local boundary. If Nexus creates branch-local or
dungeon-local rule state in C, save/restore needs a clear decision: is the
state global game state, level-local state, or derivable from topology/Lua data?

## Restore Lifecycle

Restore is centered in `src/restore.c`.

Important points:

- `validate()` and `uptodate()` check version, feature set, entity counts, and
  critical sizes before accepting files.
- `getlev()` restores one level from a save, level file, or bones file.
- `restgamestate()` restores global game state.
- Pointers are not trusted as live pointers. Object/monster chains are rebuilt,
  contained objects are re-linked, worn pointers are restored, timers and light
  sources are relinked, and derived arrays such as level object grids are
  reconstructed.
- Some fields are adjusted around save/restore, such as relative timestamps.

This reinforces the main architectural lesson: the savefile format is
struct-shaped, but save/restore is not a blind memory image of the entire
process. It is a coordinated sequence of struct writes plus reconstruction and
fixups.

## Version and Compatibility

`store_version()` writes a `version_info` struct containing:

- `incarnation`: version number;
- `feature_set`: bitmask of compile-time feature settings;
- `entity_count`: monster/object sanity count.

It also writes "critical bytes": compact records of primitive and key struct
sizes. `validate()` asks `uptodate()` to check these for struct-level files.

This matters for Nexus because changes to durable structs, monster/object
counts, compile-time features, or architecture-sensitive constants can make old
saves unusable or dangerous. The save compatibility boundary is stricter than
the source boundary.

## Bones Files

Bones files are not full saves. They are transformed level snapshots produced
after death and later imported into another game.

Bones creation is in `savebones()` in `src/bones.c`.

Before writing, NetHack modifies the dead character's level:

- removes the hero from the map;
- clears visibility/memory state;
- adds a cemetery record describing who died, how, when, and where;
- marks wizard bones when applicable;
- sanitizes or strips object knowledge and user-provided names;
- converts or removes unique/endgame objects;
- adjusts artifacts to avoid duplicates;
- removes unsafe monster incarnation details;
- records fruit types used by objects on the level;
- updates monsters before restoration.

The bones file then writes:

- version metadata;
- ancestor UUID;
- bones id;
- fruit chain;
- a level snapshot via `savelev()`.

Bones loading is in `getbones()`:

- skip if bones are disabled, discover mode is active, this level forbids bones,
  or random chance rejects them;
- open and validate the bones file;
- confirm the bones id matches the current level;
- call `getlev()` with bonesfile type;
- adjust object and monster ids;
- sanitize names and engravings;
- remove extinct/genocided monsters;
- fix artifacts, shop damage, object ages, and ghostly objects;
- delete the bones file after successful use.

Bones are therefore a cross-game level import format, not merely "a savefile
where the player died." They are an explicit boundary between one run's world
state and another run's world state.

## Lua State

NetHack 5 does save some Lua-owned state, but only through a narrow mechanism.

`save_luadata()` calls `get_nh_lua_variables()` and writes the returned string.
`restore_luadata()` reads that string, loads it into the Lua core state, and
executes it.

The Lua-side table is `nh_lua_variables` in `dat/nhcore.lua`. Lua helper code
can store values there through `nh.variable()`. The saved representation is a
Lua assignment string that reconstructs that table.

This is not a Lua serialization of the whole game. It is a small persistent
Lua variable surface embedded inside the broader C save format.

For Nexus, this may become useful for lightweight Lua-authored branch or level
state, but it should not be mistaken for a robust world database. If Nexus
stores meaningful world state in Lua, it needs rules about:

- allowed value types;
- ownership of keys;
- global versus level-local state;
- migration/versioning;
- whether state should survive bones import;
- whether state is authoritative or cache/derived state.

## Save/Bones as Scope Boundaries

These boundaries are useful for Nexus planning:

Global save state:

- player identity and role/race/gender/alignment;
- inventory and worn equipment;
- global objects and monsters in migration;
- dungeon topology and level metadata;
- quest/status/artifact/oracle/fruit/name tables;
- global timers/lights;
- Lua variables;
- message/gamelog history.

Level state:

- map cells;
- rooms, doors, stairs, destinations;
- level flags;
- local monsters and objects;
- traps, engravings, regions, damage, bubbles, tracks;
- local timers/lights;
- cemetery/bones metadata.

Bones-transfer state:

- sanitized level state after death;
- cemetery record;
- old fruit/object/monster mappings;
- artifacts and unique objects adjusted for another game;
- old player identity preserved only in controlled places.

Non-saved or reconstructed state:

- many process/runtime fields in `program_state`;
- live pointers and object grid links;
- terminal/window state;
- derived visibility/display state;
- some transient action state that gets cleaned before saving.

For Nexus, this suggests a design discipline:

- If a new rule state affects all future play, decide where it lives in
  `savegamestate()`.
- If it is only meaningful on one level, decide where it lives in `savelev()`.
- If it should cross games via bones, decide how it is sanitized in `bones.c`.
- If it is derived from Lua topology/content, do not save it unless recomputing
  it is unsafe or impossible.

## Nexus Guidance

1. Treat save/restore as an engine contract, not a gameplay extension point.
2. Avoid changing durable C structs until the first custom world boots.
3. If a new Nexus C module owns durable state, add explicit save/restore hooks
   at the right boundary instead of relying on incidental globals.
4. Keep Lua persistent state small and namespaced.
5. Decide early whether Nexus branch logic state is global, level-local, or
   derived.
6. Avoid enabling export-ascii or changing save formats as part of world work.
7. Record save compatibility impacts in `_work/divergences.md` whenever a
   change can invalidate existing saves or bones.
8. Consider disabling or tightly controlling bones during early custom-world
   work if canonical branches and Nexus topology diverge heavily.

## Open Questions

1. Should Nexus initially disable bones while replacing dungeon topology, then
   re-enable them after the new world's level identity rules are clear?
2. Should Nexus reserve a namespace inside `nh_lua_variables`, such as
   `nexus`, for Lua-owned persistent world state?
3. Does Nexus need level-local Lua persistence, or is global Lua persistence
   enough for the first milestone?
4. If a future dungeon-logic module owns Sokoban-like rule state, should that
   state live in C savegamestate, level save data, or Lua variables?
5. Should Nexus define a save-compatibility policy before changing objects,
   monsters, topology structs, or save-relevant globals?
6. Is `sysopt.bonesformat` scaffolding intentionally incomplete for normal
   runtime bones, or is it a transition path worth investigating later?
7. Should the architecture report include a table mapping each `savegamestate()`
   and `savelev()` section to the owning source module?

## Source Anchors

- `include/hack.h`: `NHFILE`, save format enums, file type constants, mode
  flags.
- `include/savefile.h`: serializer declarations.
- `include/sfprocs.h`: serializer procedure tables.
- `include/sfmacros.h`: shared serializer type list.
- `src/sfbase.c`: serializer dispatch and `sf_init()`.
- `src/sfstruct.c`: historical binary struct-level serializer.
- `util/sfexpasc.c`: export-ascii field-level serializer.
- `util/sfctool.c`: savefile conversion/inspection utility.
- `src/files.c`: create/open/delete level files, savefiles, and bonesfiles.
- `src/save.c`: `dosave0()`, `savegamestate()`, `savelev()`.
- `src/restore.c`: `dorecover()`, `restgamestate()`, `getlev()`, object and
  monster reconstruction.
- `src/version.c`: version info, critical byte checks, save validation.
- `src/bones.c`: bones eligibility, creation, sanitization, loading, deletion.
- `src/nhlua.c`: Lua variable save/restore.
- `dat/nhcore.lua`: `nh_lua_variables` root table.
