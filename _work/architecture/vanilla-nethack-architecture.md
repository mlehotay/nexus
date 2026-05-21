# Vanilla NetHack 5.0.0 Architecture

Date: 2026-05-21

This is an engineering description of the vanilla NetHack 5.0.0 architecture
as it matters to Nexus. It is source-grounded project coordination material,
not player-facing documentation.

The main architectural fact is that NetHack is not organized as a clean engine
with isolated content packs. It is a C game with many mature subsystems,
large global state, compile-time identity tables, runtime Lua level data, and
world-specific rules spread across normal gameplay code.

For Nexus, that means the upstream engine can be preserved, but "replace the
world" must account for hardwired topology, branch, quest, endgame, monster,
object, and save assumptions.

## High-Level Shape

Vanilla NetHack 5.0.0 has these major architectural surfaces:

- platform startup and window/sound setup in `sys/*/*main.c`
- common game startup, new-game setup, and turn loop in `src/allmain.c`
- global runtime and saved state declared through `include/decl.h`
- player state in `struct you` from `include/you.h`
- current level state in `svl.level`, exposed through `include/rm.h` macros
- dungeon topology in `struct dungeon`, `struct s_level`, `struct branch`, and
  `d_level` from `include/dungeon.h`
- object identities in compiled `objects[]` tables built from
  `include/objects.h`
- monster identities in compiled `mons[]` tables built from
  `include/monsters.h`
- Lua dungeon topology in `dat/dungeon.lua`
- Lua special levels in `dat/*.lua`, loaded by `src/sp_lev.c`
- save/restore code that serializes both game state and level state through
  explicit struct serializers

The architecture is global-state oriented. Module boundaries are mostly file
and convention boundaries, not strict ownership boundaries. Subsystems call
across each other through globals such as `u`, `svd`, `svl`, `svm`, `svc`,
`svq`, `svs`, and `program_state`.

## Process Startup

On Unix, `sys/unix/unixmain.c` performs platform setup, option and name
handling, lock/save-file handling, DLB initialization, vision initialization,
and window creation before entering the common game lifecycle.

The new-game path is:

```text
sys/unix/unixmain.c
  dlb_init()
  vision_init()
  init_sound_disp_gamewindows()
  restore_saved_game() or player_selection()
  newgame()
  moveloop(resuming)
```

Other ports have similar structure in their own `*main.c` files, then enter
the same common `newgame()` and `moveloop()` functions.

Very early process initialization is centralized in `src/allmain.c`:

```text
early_init()
  program_state_init()
  decl_globals_init()
  objects_globals_init()
  monst_globals_init()
  sys_early_init()
  runtime_info_init()
```

The object and monster global arrays exist before a new game starts. New-game
initialization then mutates them for the current game.

## New Game Lifecycle

`src/allmain.c:newgame()` is the key new-game sequence:

```text
newgame()
  initialize context ids, warning state, tribute state, uuid
  initialize monster vital flags from mons[].geno
  init_objects()
  role_init()
  init_dungeons()
  init_artifacts()
  u_init_misc()
  l_nhcore_init()
  reset_glyphmap()
  mklev()
  u_on_upstairs()
  vision_reset()
  check_special_room()
  makedog()
  initialize inventory attrs, display, skills, discoveries
  optional wizard kit and legacy text
  mark game worth saving
  welcome(TRUE)
```

Important ordering constraints:

- `init_objects()` must happen before initial inventory is created.
- `role_init()` must happen before dungeon, artifact, and player
  initialization.
- `init_dungeons()` happens before `u_init_misc()` so random monster selection
  used by initial inventory does not create odd tins or eggs.
- `mklev()` happens after the player location is initialized to dungeon 0,
  level 1 by `u_init_misc()`.

`src/u_init.c:u_init_misc()` zeros and initializes `u`, sets
`u.uz.dlevel = 1`, leaves the dungeon number at zero from the zeroed struct,
sets `u.uz0.dlevel = 0`, initializes the hero's monster form from the selected
role, sets starting HP/PW, hunger, alignment, and related player-state fields.

This is the first concrete reason dungeon 0, level 1 is the vanilla starting
assumption.

## Turn Model

`src/allmain.c:moveloop()` runs a short preamble, optionally enters the
tutorial, then repeatedly calls `moveloop_core()`.

The turn loop is movement-point based:

- `svc.context.move` indicates that actual time passed.
- hero movement points are tracked in `u.umovement`.
- monsters have their own `movement`.
- when the hero lacks enough movement for an action, monsters move through
  `movemon()`.
- when both hero and monsters are out of movement, the engine increments
  `svm.moves`, recalculates movement, and runs once-per-turn effects.
- when the hero has enough movement, the engine processes player input through
  `rhack()`, which parses commands and calls gameplay functions such as
  `domove()`.

The loop is not a separate scheduler module. It directly calls many systems:
monster movement, random monster generation, timers, regions, hunger, spell
aging, sound, weather, water/air level bubbles, vision, status refresh, and
Lua core callbacks.

There are three useful timing buckets in `moveloop_core()`:

- once per global turn, after `svm.moves++`
- once per hero action that consumed time
- once per player input opportunity

This distinction matters for any future Nexus hooks. A branch-local rule must
be clear about whether it runs per turn, per hero action, during movement, or
during command parsing.

## Global State Model

NetHack 5 uses many global structs grouped in `include/decl.h`.

Examples:

- `u`: hero state, declared as `struct you`
- `svl`: saved level state, including the current `struct level`
- `svd`: saved dungeon/topology state
- `svm`: saved move/global monster vital state
- `svc`: saved context state for ongoing actions and miscellaneous game
  context
- `svq`: saved quest status
- `svs`: saved special-level and spell state
- `svb`: saved branch/object-class base state
- `program_state`: unsaved process/runtime state

`include/rm.h` exposes current-level state through macros:

- `levl` is `svl.level.locations`
- `fobj` is `svl.level.objlist`
- `fmon` is `svl.level.monlist`
- `OBJ_AT(x,y)` and `MON_AT(x,y)` check per-cell object and monster arrays
- `Sokoban` is `svl.level.flags.sokoban_rules`

This state layout means code often asks "where are we?" by reading `u.uz`,
`svl.level.flags`, and topology globals directly. It also means replacing a
world assumption is rarely isolated to one parser or one data file.

## Dungeon Topology

Topology is represented by four core types in `include/dungeon.h`:

- `d_level`: `{ dnum, dlevel }`, the pair used to identify a level
- `s_level`: registered special level, including a `d_level`, prototype file
  name, bones id, random variant count, and flags
- `dungeon`: dungeon/branch metadata including name, prototype, fill level,
  bone id, flags, entry level, number of levels, ledger start, and depth start
- `branch`: connection between two `d_level`s, with a branch type and direction

The `d_level` pair is not just display data. It is used for:

- current hero location (`u.uz`)
- previous location (`u.uz0`)
- stair and trap destinations
- monster and object migration
- level file ledgers
- branch endpoints
- save/restore references
- special-level checks

`ledger_no()` maps a `d_level` into a unique level-file number. `depth()` maps
a `d_level` into the logical dungeon depth used for generation, difficulty, and
display. These are derived from the owning `struct dungeon` fields
`ledger_start` and `depth_start`.

## Loading `dat/dungeon.lua`

`src/dungeon.c:init_dungeons()` loads topology from `dat/dungeon.lua` through a
private sandboxed Lua state:

```text
init_dungeons()
  nhl_init()
  nhl_loadlua(DUNGEON_FILE)
  read global Lua table "dungeon"
  for each dungeon table:
    parse dungeon metadata
    parse branch prototypes
    parse special-level prototypes
    place candidate special levels
    add placed special levels to svs.sp_levchn
  init_castle_tune()
  fixup_level_locations()
```

`dat/dungeon.lua` defines the canonical graph:

- The Dungeons of Doom
- Gehennom
- The Gnomish Mines
- The Quest
- Sokoban
- Fort Ludios
- Vlad's Tower
- The Elemental Planes
- The Tutorial

The first table entry becomes dungeon index 0 in normal load order. Vanilla
therefore expects `u.uz = { dnum = 0, dlevel = 1 }` to mean Dungeons of Doom,
level 1.

Special levels from the Lua topology file are placed probabilistically or at
fixed ranges. They are stored in the global special-level chain
`svs.sp_levchn`, sorted by dungeon and level.

## Hardwired Topology Names

After loading the Lua topology, `src/dungeon.c:fixup_level_locations()` maps
specific prototype names to quick-access globals in `svd.dungeon_topology`.

Examples include:

- `oracle`
- `medusa`
- `castle`
- `valley`
- `wizard1`, `wizard2`, `wizard3`
- `sanctum`
- `earth`, `water`, `fire`, `air`, `astral`
- `minend`
- `soko1`
- quest placeholders `x-strt`, `x-loca`, `x-goal`

It also hardwires dungeon names:

- `The Quest`
- `Sokoban`
- `The Gnomish Mines`
- `Vlad's Tower`
- `The Tutorial`

Those names become `quest_dnum`, `sokoban_dnum`, `mines_dnum`, `tower_dnum`,
and `tutorial_dnum`.

The comment in `fixup_level_locations()` says "I hate hardwiring these names."
That is the correct architectural warning: Lua provides the topology data, but
many canonical locations are still promoted into C globals and used throughout
the engine.

## Level Creation

`src/mklev.c:mklev()` creates or loads the current level:

```text
mklev()
  reseed RNGs
  init_mapseen(&u.uz)
  if getbones() succeeds, return
  makelevel()
  level_finalize_topology()
```

`makelevel()` decides which generation path to use:

- call `Is_special(&u.uz)` to find a registered special level
- if special and not Rogue level, call `makemaz(slev->proto)`
- else if the dungeon has a prototype file, call `makemaz("")`
- else if the dungeon has a fill level, call `makemaz(fill_lvl)`
- else if in Quest, derive role-specific fill level names
- else if in Gehennom or below Medusa in the main dungeon, create maze-like
  levels
- otherwise generate ordinary rooms, stairs, branches, rooms, monsters, and
  objects

This is the direct path that can boot a data-registered custom Lua level at
dungeon 0, level 1: `u.uz` starts there, `Is_special(&u.uz)` finds the special
level, and `makemaz(proto)` loads it.

## Lua Special Levels

`src/mkmaze.c:makemaz()` chooses a Lua special-level file name. For special
levels with variants, it expands names such as `soko1` to `soko1-1.lua` or
`soko1-2.lua`. If the file loads, it returns without ordinary maze generation.
If loading fails, it falls back to generic maze generation.

`src/sp_lev.c:load_special()` is the general loader:

```text
load_special(name)
  create_des_coder()
  load_lua(name)
  link_doors_rooms()
  remove_boundary_syms()
  ensure_way_out() if requested
  map_cleanup()
  wallification()
  flip_level_rnd()
  count_level_features()
  solidify_map() if requested
  fixup_special()
  premap_detect() if requested
```

The `des.*` Lua API is registered in `src/sp_lev.c`. It includes level
construction functions such as:

- `des.level_init`
- `des.level_flags`
- `des.map`
- `des.room`
- `des.corridor`
- `des.stair`
- `des.ladder`
- `des.object`
- `des.monster`
- `des.trap`
- `des.region`
- `des.levregion`
- `des.non_diggable`
- `des.non_passwall`
- `des.wallify`

The Lua special-level language is therefore a level-construction interface, not
a general replacement for all game rules. It places terrain, objects, monsters,
regions, and flags into C-owned level state.

Example: Sokoban levels in `dat/soko*.lua` set flags such as `mazelevel`,
`noteleport`, `premapped`, `sokoban`, and `solidify`, then place boulders,
holes, rolling-boulder traps, monsters, objects, and rewards.

## Objects

Object type identity is compiled, not loaded from Lua.

`src/objects.c` builds static initialization tables from `include/objects.h`:

```text
static struct objdescr obj_descr_init[NUM_OBJECTS + 1]
static struct objclass obj_init[NUM_OBJECTS + 1]
struct objdescr obj_descr[]
struct objclass objects[]
objects_globals_init() copies init tables into mutable globals
```

`include/objclass.h:struct objclass` defines object-type data such as:

- name and description indices
- discovery state
- merge behavior
- magic/charged/unique/wish flags
- direction or weapon strike mode
- material
- skill or armor category
- conveyed property
- object class
- delay, color, probability, weight, cost, damage, nutrition

`src/o_init.c:init_objects()` mutates the object table for the current game:

- initializes object description indices
- computes class base indices in `svb.bases`
- verifies object-class ordering
- sets gem probabilities by depth
- randomizes gem colors
- computes object-class probability totals
- shuffles unidentified descriptions for potions, scrolls, rings, wands,
  spellbooks, amulets, venom, and armor subgroups

Individual object instances are `struct obj` from `include/obj.h`. They store
an `otyp` index into `objects[]`, object id, coordinates, quantity, container
state, worn state, BUC state, knowledge flags, timers, artifact id, and many
overloaded fields.

Save/restore persists object instances and also persists object naming and
discovery state through `savenames()` and `restnames()`. This is why object
identity cannot be treated as a simple runtime Lua registry without accounting
for compiled indices and save format.

## Monsters

Monster type identity is also compiled.

`src/monst.c` builds `mons_init[]` from `include/monsters.h`, then
`monst_globals_init()` copies it into the mutable global `mons[]`.

`include/permonst.h:struct permonst` defines monster-type data:

- names
- stable `PM_*` index
- display symbol
- level, speed, armor class, magic resistance, alignment
- generation flags
- attack array
- corpse weight and nutrition
- sound and size
- resistances and conveyed resistances
- monster behavior flags
- difficulty and color

Individual monsters are `struct monst` from `include/monst.h`. A monster
instance stores a pointer to `struct permonst`, its permanent monster index
`mnum`, id, position, HP, movement points, inventory, tameness/peacefulness,
appearance state, and many flags.

The game also tracks per-species mutable vital state in `svm.mvitals[]`, such
as genocided status, corpseless status, born count, death count, and seen
state. `newgame()` seeds this from `mons[i].geno`.

Like objects, monster identities are pervasive integer indices and pointers.
Lua levels can request monsters by name or class, but those requests resolve
into compiled `mons[]` entries.

## Player State, Roles, And Quest Coupling

The player is not a separate entity component. The hero is primarily `struct
you u`, plus the hero-as-monster state `gy.youmonst`, plus selected role/race
state in globals such as `gu.urole` and `gu.urace`.

Role/race initialization affects:

- initial monster form
- starting inventory
- attributes
- skills
- alignment
- quest text and quest monster genders
- role-specific Quest level file substitutions

Quest architecture is especially coupled:

- `role_init()` initializes quest-related role state.
- `dat/dungeon.lua` uses placeholder levels `x-strt`, `x-loca`, and `x-goal`.
- `fixup_level_locations()` maps those placeholders to `qstart_level`,
  `qlocate_level`, and `nemesis_level`, then rewrites their prototype names to
  role-specific file names.
- `src/quest.c` drives quest messages, purity checks, leader/nemesis state,
  artifact handling, and expulsion.
- `svq.quest_status` and `u.uevent` persist quest progress.

This is not data-only branch behavior. It is data plus role tables plus C
logic plus saved progress flags.

## Branch And World Rules

Many world rules are implemented by checking canonical topology globals or
level flags from ordinary gameplay code.

Examples:

- `In_sokoban(&u.uz)` checks whether the current dungeon number equals
  `sokoban_dnum`.
- `Sokoban` checks `svl.level.flags.sokoban_rules`.
- `In_quest()`, `In_mines()`, `In_hell()`, and `In_endgame()` are C helpers.
- `Is_oracle_level()`, `Is_medusa_level()`, `Is_stronghold()`,
  `Is_sanctum()`, and similar macros compare `u.uz` to hardwired topology
  globals.
- `Invocation_lev()` identifies the vibrating-square level in C.
- level travel, teleport, digging, falling, rising, monster generation, and
  messages use those helpers directly.

Sokoban is a useful example. Lua levels set `des.level_flags(..., "sokoban",
...)`, but Sokoban behavior is implemented across C code:

- movement and boulder pushing in `src/hack.c`
- trap behavior and pit/hole filling in `src/trap.c`
- monster movement restrictions in `src/monmove.c` and `src/dogmove.c`
- reward handling in `src/sp_lev.c`
- conduct and achievement reporting in `src/insight.c` and `src/topten.c`
- overview/map behavior in `src/dungeon.c`

So a "branch rule" in vanilla NetHack is often not localized. It may be a
level flag, a dungeon-number check, a special-level name, an achievement, and
several gameplay hooks.

## Save And Restore

NetHack save/restore is explicit and struct-aware.

`src/save.c:dosave0()` saves the current level, then saves game state:

```text
savelev(current ledger)
savegamestate()
```

`savegamestate()` writes:

- uid and game uuid
- moves
- context
- flags
- player state `u`
- timers and light sources
- inventory and migrating objects
- migrating monsters
- monster vital state
- dungeon topology and branches
- level chain metadata
- quest status
- spellbook state
- artifacts
- oracles
- player name/fruit
- object names/discoveries
- message history
- game log
- Lua data

`src/dungeon.c:save_dungeon()` serializes the dungeon count, all
`struct dungeon` entries, `svd.dungeon_topology`, castle tune, branches,
level-info array, invocation position, and mapseen chain.

`src/save.c:savelev()` writes the current level file contents, including level
locations, remembered terrain, stairs, destinations, level flags, doors, rooms,
objects, monsters, traps, regions, exclusions, timers, lights, and other
level-local state.

`src/restore.c` reverses this order carefully. It restores role state before
reading the saved player and dungeon data, restores inventory and migrating
entities, restores dungeon topology, restores level files, then reconnects
timers, lights, and pointer-like references.

The important architecture constraint is that many saved structures contain
integer ids, enum values, array indices, and serialized struct layouts. Changing
object or monster identity tables, dungeon topology representation, or struct
layouts is therefore a save-format decision, not just a data authoring decision.

## Lua Boundaries

NetHack 5 has two relevant Lua surfaces:

- `dat/dungeon.lua`, loaded by `init_dungeons()` in a private sandboxed state
- special-level files loaded by `load_special()` through the `des.*` API

`newgame()` also calls `l_nhcore_init()` to create a Lua state that lasts until
end of game. `moveloop_core()` calls Lua core callbacks such as per-turn and
end-turn hooks when registered.

The dungeon/topology Lua surface creates C topology structures. The special
level Lua surface creates C level state. Neither surface currently makes items,
monsters, branches, or rules fully Lua-owned.

## Data-Driven Versus Hardwired

Data-driven surfaces:

- dungeon and branch layout in `dat/dungeon.lua`
- special level maps and placed content in `dat/*.lua`
- level flags set by Lua special levels
- themed rooms and fill levels
- some special-level random variants

Compiled identity surfaces:

- object type table `objects[]`
- monster type table `mons[]`
- role and race tables
- artifact table
- symbols and glyph mapping
- many enums used in saves and switch statements

Hardwired world assumptions:

- starting location is dungeon 0, level 1
- named canonical levels are mapped into `svd.dungeon_topology`
- named canonical dungeons are resolved by literal strings
- Quest placeholder levels are rewritten based on role filecode
- many gameplay systems check `In_sokoban`, `In_quest`, `In_endgame`,
  `Inhell`, or specific `Is_*` level macros
- achievements and livelog text name canonical branches and milestones
- save/restore serializes topology and identity state in C structs

## Constraints For Nexus

The safest Nexus path is to treat NetHack 5 as a preserved C simulation engine
with a partially data-driven world layer, not as a generic roguelike engine.

Immediate implications:

- A minimal custom starting level should be attempted through `dat/dungeon.lua`
  and a Lua special level first.
- A reduced topology must either keep hardwired canonical names available or
  patch the C code that assumes them.
- Custom item and monster data should not move to Lua until the object and
  monster identity/save constraints are explicitly designed.
- Branch-local logic needs a real module boundary because vanilla branch rules
  are scattered through global gameplay code.
- Sokoban is a good case study for branch logic, but not a clean plug-in model.
- Quest and endgame systems should be left inert unless they block the first
  boot milestone.
- Any C change replacing a canonical world assumption is an upstream
  divergence and should be recorded.

## Glossary

- `u`: global hero state, `struct you`.
- `u.uz`: current dungeon/level pair.
- `u.uz0`: previous dungeon/level pair.
- `d_level`: `{ dnum, dlevel }` location identity.
- `struct dungeon`: metadata for a dungeon/branch of levels.
- `struct s_level`: registered special level.
- `struct branch`: connection between two dungeons or levels.
- `svd.dungeons`: loaded dungeon metadata array.
- `svd.dungeon_topology`: quick-access canonical topology globals.
- `svs.sp_levchn`: linked list of registered special levels.
- `svb.branches`: linked list of dungeon branches.
- `svl.level`: current level state.
- `svm.moves`: global turn counter.
- `objects[]`: mutable global object-type table.
- `mons[]`: mutable global monster-type table.
- `svm.mvitals[]`: per-monster-species saved vital state.
- `svc.context`: saved action/context state.
- `svq.quest_status`: saved Quest progress.
- `program_state`: unsaved process/runtime state.

## Source Map

Primary files inspected for this pass:

- `sys/unix/unixmain.c`
- `src/allmain.c`
- `src/dungeon.c`
- `include/dungeon.h`
- `include/hack.h`
- `include/decl.h`
- `include/rm.h`
- `src/mklev.c`
- `src/mkmaze.c`
- `src/sp_lev.c`
- `dat/dungeon.lua`
- `dat/soko1-1.lua`
- `dat/oracle.lua`
- `src/objects.c`
- `include/objects.h`
- `include/objclass.h`
- `include/obj.h`
- `src/o_init.c`
- `src/monst.c`
- `include/monsters.h`
- `include/permonst.h`
- `include/monst.h`
- `src/u_init.c`
- `src/quest.c`
- `src/save.c`
- `src/restore.c`
