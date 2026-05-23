# 0002 - Boot Custom Level

## Goal

Launch NetHack 5.0.0 and place the player in one handcrafted Nexus Lua level.

This is the first gameplay-facing milestone. It should prove that Nexus can
replace the canonical starting world assumption while preserving NetHack's
engine and simulation systems.

## Scope

In scope:

- inspect startup and dungeon-generation code before editing
- add one minimal Nexus Lua level
- identify the smallest `dat/dungeon.lua` topology change
- prefer data/topology changes before C changes
- document any intentional upstream divergence
- verify with the narrowest practical build/run target

Out of scope:

- procedural generation
- new combat systems
- role, race, stat, or balance changes
- importing Floating Eye changes
- solving quest, ascension, endgame, or branch systems beyond immediate boot

## Starting Questions

1. Where does new-game startup initialize the dungeon topology?
2. How does `dat/dungeon.lua` become internal dungeon and special-level state?
3. How does `mklev()` choose special Lua levels versus ordinary generation?
4. Can dungeon 0 level 1 be a Nexus special level without C changes?
5. Which hardwired canonical names block a data-only single-world topology?

## Acceptance Criteria

- NetHack launches from the Nexus tree
- player starts on a custom handcrafted Lua level
- basic movement and rendering work
- canonical Dungeons of Doom starting structure is bypassed or replaced
- every intentional upstream divergence is recorded in `_work/divergences.md`

## Status

Done.

## Progress

2026-05-22:

- Added an opt-in `NEXUS` build path in the Nexus local hints profile.
- Added `dat/nexus-dungeon.lua` as a Nexus-owned topology file.
- Added `dat/nexus-start.lua` as the first handcrafted Nexus level.
- Guarded `src/dungeon.c` so Nexus builds load `nexus-dungeon.lua` while
  non-Nexus builds keep `dungeon.lua`.
- Added Nexus Lua files to the install/DLB data list through `NEXUSDAT`.
- Verified the installed Nexus binary boots to the handcrafted map and accepts
  basic input in the tty window port.

2026-05-23:

- User confirmed closure after the 0002 implementation and the stacked 0006
  verification branch were merged into `nexus`.
