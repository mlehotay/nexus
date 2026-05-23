# Nexus Boot Guard Map

Date: 2026-05-22

Status: initial architecture map for `task-019`.

Scope: map the first `0002-boot-custom-level` implementation against the
`NEXUS` compile-time guarding strategy. This is not gameplay design and does
not implement the boot milestone.

## Goal

Booting into one handcrafted Nexus level should prove the smallest useful
variant boundary:

- non-Nexus builds keep upstream NetHack topology and data loading;
- Nexus builds opt into Nexus topology and data files;
- shared C changes are limited to guarded switch points;
- Nexus world content lives in Nexus-owned Lua files.

## Expected Touch Points

| File | Ownership | Expected Change | Guarding |
| --- | --- | --- | --- |
| `sys/unix/hints/nexus-local` | Nexus build profile | Add `-DNEXUS` to local C flags. | No `#ifdef`; this profile is already Nexus-owned. |
| `src/dungeon.c` | shared NetHack source | Select `nexus-dungeon.lua` instead of `dungeon.lua` when `NEXUS` is defined. | Guard only the `DUNGEON_FILE` definition. |
| `sys/unix/Makefile.top` | shared build/resource list | Ensure Nexus Lua files are installed and later packable in DLB. | Prefer make-level conditional or harmless extra data; avoid changing vanilla file semantics. |
| `dat/nexus-dungeon.lua` | Nexus data | Define the minimal topology for the first Nexus world. | Nexus-owned data; no C guard. |
| `dat/nexus-start.lua` | Nexus data | Define the first handcrafted level. | Nexus-owned data; no C guard. |
| `_work/divergences.md` | workflow record | Record the intentional topology filename divergence once implemented. | Not runtime code. |

## Preferred First C Change

The first shared-source change should be only:

```c
#ifdef NEXUS
#define DUNGEON_FILE "nexus-dungeon.lua"
#else
#define DUNGEON_FILE "dungeon.lua"
#endif
```

This preserves the existing `init_dungeons()` flow:

```text
init_dungeons()
  nhl_init()
  nhl_loadlua(DUNGEON_FILE)
  read global Lua table "dungeon"
  register dungeons, branches, and special levels
  fixup_level_locations()
```

No Nexus-specific parser, startup path, system port, or window port is needed
for the proof of concept.

## Resource Strategy

Loose-file development builds are the first target. The local Nexus profile
currently avoids DLB, so the first verification should prove installed loose
files are present and loadable.

The implementation still needs to avoid a DLB trap:

- if `DUNGEON_FILE` is `nexus-dungeon.lua`, a future DLB build must include
  `nexus-dungeon.lua`;
- if `nexus-dungeon.lua` references `nexus-start.lua`, that level file must
  also be in the installed data set or DLB;
- success in a loose-file install does not prove packaged-resource correctness.

Open resource decision:

- Install Nexus Lua files only under a `NEXUS` build condition, or install them
  as unused extra data in all builds.

The safer compatibility posture is conditional installation. The simpler early
development posture is harmless extra data. Either is acceptable only if
non-Nexus runtime behavior still loads `dungeon.lua`.

## Data Boundary

The first Nexus topology should prefer data changes over engine surgery:

- make dungeon 0 level 1 a Nexus-authored special level;
- keep the ordinary `u_init_misc()` starting assumption of dungeon 0, level 1;
- let `mklev()` find the special level through `Is_special(&u.uz)`;
- load the level through the existing `makemaz()` and `load_special()` path.

That path tests the actual NetHack systems Nexus wants to preserve:

- startup ordering;
- Lua dungeon topology loading;
- special-level registration;
- level creation;
- rendering, movement, messages, objects, monsters, persistence hooks.

## Known Risk Points

`fixup_level_locations()` promotes canonical names and dungeons into C globals.
A minimal Nexus topology may expose hardwired assumptions if required canonical
locations are absent.

Risk handling:

- first try a topology that leaves enough inert compatibility scaffolding for
  `fixup_level_locations()`;
- only add C changes when the data topology cannot satisfy startup;
- keep any C workaround behind `#ifdef NEXUS`;
- record each workaround as an upstream divergence.

Bones are another risk, but they do not need to be solved before the first boot
unless the custom topology creates immediate bones lookup failures.

## Verification Targets

Narrowest useful verification for the implementation patch:

1. Build the Nexus local profile with `NEXUS` defined.
2. Install/update data files.
3. Launch the `nexus` command or equivalent local binary.
4. Confirm the player starts on the handcrafted level.
5. Confirm basic movement and rendering work.
6. Confirm the generated or captured compile command includes `-DNEXUS`.
7. Confirm a non-Nexus build path would still select `DUNGEON_FILE
   "dungeon.lua"` by source inspection or a clean non-Nexus compile.

## Decision For The Next Runtime Patch

Use `NEXUS` only to select the topology filename and package the Nexus Lua data.
Do not add a Nexus C module, new startup function, new runtime option, or save
state for the first boot attempt.

If that fails, the failure should determine the next guarded switch point.
