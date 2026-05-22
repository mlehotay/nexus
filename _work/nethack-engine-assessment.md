# NetHack Engine Assessment For Nexus

Date: 2026-05-21

This note captures the relevant Nexus context from the initial project
discussion and early source inspection. It is coordination material for
`_work/`; it is not runtime content, build input, or player-facing canon.

## Project Scope

Nexus is a standalone NetHack 5.0.0 derivative. It should live outside the IER
repository and should not inherit IER governance, release checks, vocabulary, or
theory constraints.

The project is not trying to make:

- a full roguelike
- a full conversion
- an IER game
- a NetHack ascension benchmark
- a general-purpose AI environment

The project is trying to make:

> a tiny standalone world running on the NetHack 5.0.0 engine.

The working rule remains:

> Preserve NetHack systems. Replace NetHack world assumptions.

## Desired First Milestone

The first Nexus milestone is deliberately small:

```text
launch Nexus
start a new game
appear in one handcrafted custom Lua level
move around
see normal NetHack rendering/messages/status
```

This is the proof that the project is real. Content, procedural generation,
combat balance, new roles, new monsters, and larger world design should wait
until this milestone works.

## Why NetHack 5 Matters

The inspected NetHack tree is a NetHack 5-era source tree with Lua dungeon and
special-level infrastructure. That makes the engine a good target for a tiny
world experiment because more of the dungeon/topology surface is represented as
Lua data rather than only compiled legacy dungeon description files.

The key opportunity is to replace the canonical dungeon topology and starting
level with a minimal custom topology before doing engine surgery.

## Source Orientation

The relevant startup path identified from source inspection:

- `src/allmain.c`
  - `newgame()` is the new-game startup sequence.
  - It calls `init_objects()`, `role_init()`, `init_dungeons()`,
    `init_artifacts()`, `u_init_misc()`, `l_nhcore_init()`, then `mklev()`.
- `src/dungeon.c`
  - `init_dungeons()` initializes dungeon topology.
  - It loads `dat/dungeon.lua` through `nhl_loadlua()`.
  - It reads the global Lua table `dungeon`.
  - It registers dungeons, levels, branches, special levels, and level
    locations.
  - It calls `fixup_level_locations()` after topology construction.
- `dat/dungeon.lua`
  - Defines the canonical dungeon list, including the Dungeons of Doom,
    Gehennom, Mines, Sokoban, Quest, Elemental Planes, Fort Ludios, and
    Tutorial.
  - Defines branches and special level prototypes.
- `src/mklev.c`
  - `mklev()` calls `makelevel()`.
  - `makelevel()` checks whether the current `u.uz` location is a registered
    special level using `Is_special(&u.uz)`.
  - If special, it calls `makemaz(slev->proto)`.
  - Otherwise it may use a dungeon prototype, fill level, quest fill level,
    maze generation, or ordinary room generation.
- `src/sp_lev.c`
  - `load_special()` loads Lua special-level files and finalizes topology,
    doors, map cleanup, wallification, branch fixups, and premapping.
- `include/dungeon.h`
  - Defines `d_level`, `s_level`, `dungeon`, `branch`, and branch types.
  - Several canonical helpers remain hardwired by known special-level globals
    such as `oracle_level`, `qstart_level`, `medusa_level`, `astral_level`, and
    others.

## The Core Engine Problem

NetHack's engine is not just a map loader. It is a game whose startup, level
selection, branch traversal, quest logic, endgame logic, messages, achievements,
teleport rules, and status text all assume a canonical dungeon graph.

The immediate problem is therefore not "draw a custom map." The immediate
problem is:

> Can dungeon 0, level 1 be made into a Nexus-authored special Lua level while
> leaving enough canonical topology present, stubbed, or harmless that startup
> and ordinary play do not panic?

This should be tested as a data/topology problem first. If a reduced
`dat/dungeon.lua` can express a one-level world, the first milestone may need
little or no C. If hardwired canonical checks require named levels or globals to
exist, Nexus should either keep inert placeholders or make the narrowest C
change necessary.

## Likely Data-First Strategy

Start with a work branch for plan `0002-boot-custom-level`.

Investigate before editing:

1. Confirm whether the first dungeon in `dat/dungeon.lua` becomes `dnum == 0`.
2. Confirm how level `base = 1` and a special level name place a special level
   at dungeon level 1.
3. Confirm whether `mklev()` will load a registered special level at
   `u.uz == { dnum: 0, dlevel: 1 }`.
4. Identify which canonical levels are required by `fixup_level_locations()`,
   `role_init()`, quest setup, achievements, or startup sanity checks.
5. Try the smallest `dat/dungeon.lua` change that starts on a Nexus special
   level.

Candidate first content:

- add `dat/nexus-start.lua`
- register it as the level-1 special level of the first dungeon
- keep the map sparse and ordinary
- include normal entry/exit assumptions if needed by startup
- avoid custom monsters/items until the map boots

## C Changes To Avoid Initially

Avoid changing these until a data-only attempt has been proven insufficient:

- role/race/stat initialization
- monster and object definitions
- command handling
- save/restore formats
- inventory systems
- combat systems
- window ports
- quest and endgame logic
- topology structs
- special-level loader behavior

If C becomes unavoidable, prefer a tiny compatibility shim or explicit Nexus
mode guard over broad deletion of canonical behavior.

## Expected Hardwired Assumptions

The following may block a one-level world or a heavily stripped
`dat/dungeon.lua`:

- named special levels used by globals in `src/dungeon.c`
- quest branch assumptions
- Oracle/Quest relationships
- dungeon depth calculations
- branch stair placement
- endgame or Gehennom references
- achievements/livelog text
- teleport rules that special-case branches or one-level dungeons
- code that assumes dungeon 0 is the main dungeon
- code that expects level 1 to have an upstairs/start location

These are not reasons to abandon the data-first path. They are the places to
look when a stripped topology panics.

## NLE5 Relationship

`nle5` should be a parallel project, not part of Nexus.

Nexus owns:

- NetHack 5 world/topology/content changes
- custom Lua levels
- local NetHack build/install conventions
- runtime behavior as a human-playable tiny world

NLE5 owns:

- Python control loop
- environment reset/step API
- observations, glyphs, messages, status, rendering
- optional later integration with Nexus as a target engine

Dependency direction:

```text
nle5 may point at Nexus later
Nexus should not depend on nle5
```

Do not let NLE5 requirements drive Nexus before the first custom level boots.
Do not make Nexus preserve NLE 3.6.x benchmark semantics or ascension
compatibility.

## NLE Paper Context

The referenced PDF is the original NetHack Learning Environment paper. It is
relevant because it describes NetHack as a fast, symbolic, procedurally
generated RL environment with observations such as glyphs, messages, status,
and terminal state.

For Nexus, the important lesson is not "train an ascension agent." The useful
lesson is that NetHack can be exposed as a controllable symbolic environment.
That suggests a later path where NLE5 can drive Nexus worlds after the human
playable tiny-world milestone exists.

## Near-Term Recommendation

For Nexus, continue with plan `0002-boot-custom-level`:

1. Inspect `init_dungeons()` and `dat/dungeon.lua` behavior from the current
   Nexus checkout.
2. Add one minimal handcrafted Lua level.
3. Try to place it at dungeon 0, level 1 with data/topology changes.
4. Build/install using the existing Nexus local workflow.
5. Record every intentional upstream topology/startup divergence in
   `_work/divergences.md`.

For NLE5, keep only alignment notes for now. It should not block or reshape the
Nexus boot milestone.
