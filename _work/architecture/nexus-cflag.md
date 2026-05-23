# Nexus Compile-Time Flag Strategy

Date: 2026-05-21

Status: design note.

Scope: how Nexus should use `#ifdef NEXUS` without breaking vanilla NetHack
builds, alternate ports, or future build profiles.

## Summary

`NEXUS` should be an opt-in build feature macro. It should not be a platform
macro, a window-port macro, a runtime option, or a default in `include/config.h`.

The core rule is:

> Shared NetHack files may contain small guarded switch points. Nexus behavior
> should live in Nexus-owned files or Nexus-owned data.

For the first milestone, the likely switch point is the dungeon topology file:

```c
#ifdef NEXUS
#define DUNGEON_FILE "nexus-dungeon.lua"
#else
#define DUNGEON_FILE "dungeon.lua"
#endif
```

That lets non-Nexus builds keep loading vanilla `dungeon.lua`, while Nexus
builds load a separate topology file.

## Why This Is The Right Layer

The architecture reports identify several kinds of variability:

- compile-time feature and platform macros;
- hints and makefiles for build/install profiles;
- DLB and loose-file resource packaging;
- `SYSCF` and user rc files for runtime policy and preferences;
- Lua files for dungeon topology and special levels;
- save and bones formats for durable game state.

`NEXUS` belongs in the first two layers only:

- a build profile defines `NEXUS`;
- C code may compile Nexus-specific behavior only when `NEXUS` is defined.

It should not move world content into `sysconf`, window ports, or system-port
startup code. It should also not be used to casually change durable structs,
object identities, monster identities, save formats, or generated enum/table
surfaces.

## Definition Site

Define `NEXUS` in Nexus build profiles, beginning with:

```make
# sys/unix/hints/nexus-local
CFLAGS=... -DNEXUS ...
```

Do not define `NEXUS` in:

- `include/config.h`;
- `include/config1.h`;
- platform headers such as `include/unixconf.h`;
- generic makefile templates unless the stanza is conditional on a Nexus build
  profile.

Reason: `include/config.h` and platform headers are shared defaults. Putting
`NEXUS` there would make Nexus behavior leak into builds that did not ask for
it.

## Ownership Rules

Nexus-owned files may contain normal Nexus implementation without every line
being guarded:

- `include/nexus.h`;
- `src/nexus.c`;
- future `src/nexus_*.c`;
- `dat/nexus-dungeon.lua`;
- `dat/nexus-*.lua`;
- Nexus-specific hints files.

Shared NetHack files should only contain one of these patterns:

1. A small guarded constant or selection point.
2. A guarded include of a Nexus header.
3. A guarded call into a Nexus-owned function.
4. A guarded makefile/resource-list addition.

Avoid placing large bodies of Nexus logic directly inside shared files. If a
block grows beyond a few lines or needs more than one helper, move it into a
Nexus-owned module.

## Guard Patterns

### Small Constant Replacement

Use this when the upstream code already has one canonical value and Nexus needs
a different value.

```c
#ifdef NEXUS
#define DUNGEON_FILE "nexus-dungeon.lua"
#else
#define DUNGEON_FILE "dungeon.lua"
#endif
```

This is preferred for the first dungeon-topology change because it keeps the
existing `init_dungeons()` load path intact.

### Guarded Hook

Use this when the upstream flow is still correct, but Nexus needs a local
intervention at one point.

```c
#ifdef NEXUS
    nexus_after_dungeons_initialized();
#endif
```

The function should be declared in `include/nexus.h` and implemented in a
Nexus-owned source file.

### Guarded Alternative Expression

Use this sparingly. It is useful for simple choices but can become unreadable if
repeated often.

```c
    filename =
#ifdef NEXUS
        "nexus-dungeon.lua";
#else
        "dungeon.lua";
#endif
```

Prefer the constant pattern when possible.

### Compile-Time No-Op Wrapper

If a call site would be clearer without repeated `#ifdef` blocks, a header can
provide a no-op when Nexus is disabled:

```c
#ifdef NEXUS
void nexus_after_dungeons_initialized(void);
#else
#define nexus_after_dungeons_initialized() ((void) 0)
#endif
```

Use this only if the include itself is acceptable in non-Nexus builds and the
header has no Nexus-only dependencies. For early work, explicit `#ifdef NEXUS`
at call sites is easier to audit.

## Patterns To Avoid

Avoid runtime checks as the primary isolation mechanism:

```c
if (nexus_mode) {
    ...
}
```

A runtime flag does not protect other people's binaries from compiling or
linking the Nexus code. Runtime flags can be useful inside a `NEXUS` build, but
they are not a substitute for compile-time isolation.

Avoid broad guards around existing upstream functions:

```c
#ifdef NEXUS
/* copied and modified version of a large upstream function */
#else
/* original function */
#endif
```

That creates a maintenance fork inside one file. Prefer extracting a narrow
selection point.

Avoid negative guards for normal upstream behavior:

```c
#ifndef NEXUS
/* upstream behavior */
#endif
```

This makes the vanilla path look exceptional. Use `#ifdef NEXUS` for the
variant and leave the ordinary upstream path visually primary.

## Build And Resource Handling

The C macro alone is not enough. If Nexus C code selects Nexus data files, the
build and install rules must also make those files available.

For loose-file development builds:

- `dat/nexus-dungeon.lua` must be installed into the data directory;
- `dat/nexus-*.lua` level files must also be installed;
- non-Nexus installs do not need those files unless they are harmless extras.

For DLB builds:

- Nexus data files must be included in the DLB file list when `NEXUS` is active;
- if `DUNGEON_FILE` becomes `nexus-dungeon.lua`, that file must be in DLB or
  available as a loose fallback;
- a Nexus DLB build should be tested separately because loose-file success does
  not prove packaged-resource success.

The current local profile keeps DLB off, which is useful while topology and
level files are changing. The strategy still needs to account for future DLB
and cross builds so that Nexus does not silently depend on loose local files.

## File Naming

Use explicit Nexus names rather than replacing vanilla files in place:

- `dat/nexus-dungeon.lua`, not a modified `dat/dungeon.lua`;
- `dat/nexus-start.lua`, not a repurposed canonical level name;
- `src/nexus.c` or `src/nexus_*.c`, not unrelated additions to broad gameplay
  modules;
- `include/nexus.h` for Nexus declarations.

This keeps non-Nexus data and Nexus data visible side by side and reduces the
chance that a vanilla build consumes Nexus content by accident.

## Save And Bones Caution

The save/bones reports matter for `#ifdef` policy. Some compile-time changes
are just behavior selection. Others change the shape or meaning of durable
state.

Treat these as high-risk under `NEXUS`:

- changing struct layouts;
- changing `NUM_OBJECTS`, `NUMMONS`, `PM_*`, `otyp`, or object-class ordering;
- changing dungeon constants that affect ledger numbering or depth mapping;
- changing save/restore order;
- changing bones eligibility or bones IDs;
- adding persistent Nexus state without explicit save/restore ownership.

If Nexus eventually needs any of those, the change should have a separate
design note and an explicit divergence entry. It should not be bundled with the
first `NEXUS` flag introduction.

## Suggested First Implementation

First patch:

1. Add `-DNEXUS` to `sys/unix/hints/nexus-local`.
2. Add `dat/nexus-dungeon.lua`.
3. Add the first handcrafted level file, probably `dat/nexus-start.lua`.
4. Guard `DUNGEON_FILE` in `src/dungeon.c`.
5. Add Nexus data files to the install/resource list in the narrowest practical
   way.
6. Build and run the Nexus profile.
7. Build without `NEXUS`, or at least inspect the generated compile command, to
   verify the vanilla path still selects `dungeon.lua`.

Intentional divergence to record:

```text
When compiled with NEXUS, the game loads Nexus dungeon topology from
nexus-dungeon.lua instead of vanilla dungeon.lua. Builds without NEXUS keep the
upstream topology filename and load path.
```

## Review Checklist

For every future Nexus C change, answer these before merging:

- Is the changed file Nexus-owned or shared upstream NetHack code?
- If shared, is every Nexus behavior guarded by `#ifdef NEXUS`?
- Could the same change be moved into `src/nexus*.c` behind one guarded call?
- Does a non-Nexus build compile and link without Nexus source files?
- Does a non-Nexus runtime avoid loading Nexus data files?
- Are loose-file and future DLB resource paths both accounted for?
- Does the change alter structs, enum/table identities, save files, bones, or
  generated artifacts?
- If it is an intentional upstream divergence, is `_work/divergences.md`
  updated?

## Open Decisions

1. Should Nexus data files be installed only for `NEXUS` builds, or always
   installed as harmless unused data?
2. Should there be a separate `NEXUS_DLB` or `nexus-release` profile later, or
   should DLB remain a normal packaging choice independent of `NEXUS`?
3. Should Nexus start with one umbrella module, `src/nexus.c`, or immediately
   split by responsibility, such as `src/nexus_topology.c`?
4. Should early Nexus builds disable bones under `NEXUS`, or leave bones alone
   until topology replacement proves it is a real blocker?
5. What is the minimum non-Nexus verification target we will run before
   accepting guarded changes?

## Current Working Rule

Start with one macro:

```text
NEXUS
```

Do not introduce additional Nexus-specific macros until there is a concrete
build or compatibility distinction that `NEXUS` alone cannot express.

The discipline is simple: Nexus can diverge, but only when the build asked for
Nexus.
