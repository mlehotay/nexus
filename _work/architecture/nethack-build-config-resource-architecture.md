# NetHack Build, Configuration, and Resource Architecture

Date: 2026-05-21

Scope: NetHack 5.0.0 conditional compilation, DLB, SYSCF/sysconf, and nearby
build/resource topics relevant to Nexus.

This report is a companion to
`_work/architecture/vanilla-nethack-architecture.md`. The earlier report
describes runtime gameplay architecture. This one describes the configuration
and packaging surfaces that decide which runtime exists, where it finds its
files, and which policies are supplied by the local installation.

## Summary

NetHack's source is shaped by three overlapping configuration systems:

1. Compile-time macros choose the platform, window ports, optional features,
   security posture, file layout, and compatibility shims.
2. Build/install machinery generates data files, Makefiles, Lua headers, and
   optional packed data archives.
3. Runtime configuration files set local policy and player preferences.

These systems are intentionally not cleanly separated. Many source files mix
feature macros, platform macros, generated data assumptions, and runtime
configuration. For Nexus, the practical rule is:

- use data and Lua for world shape;
- use `sys/unix/hints/nexus-local` for local build and install policy;
- use `sys/unix/sysconf` and `sys/unix/nexus.nethackrc` for runtime policy and
  developer defaults;
- avoid adding new compile-time switches unless the behavior truly changes the
  built engine, installed resource model, or binary portability.

## Conditional Compilation

Conditional compilation is an architecture layer in NetHack, not incidental
noise. The codebase supports many historical and current build targets from one
tree, so `#ifdef` controls more than platform details. It also selects window
systems, file locations, save behavior, security checks, data packaging,
diagnostics, optional UI features, and compiler compatibility.

The central entry point is `include/config.h`. It defines `UNIX` by default,
includes `include/config1.h` for platform autodetection, chooses default window
systems, sets global filenames, enables SYSCF by default, declares compression
defaults, and then includes the lower-level portability headers that feed the
rest of the program.

Important macro families:

- Platform identity: `UNIX`, `WIN32`, `VMS`, `MSDOS`, `AMIGA`, `MACOS9`,
  `TOS`, `OS2`.
- Window/UI ports: `TTY_GRAPHICS`, `CURSES_GRAPHICS`, `X11_GRAPHICS`,
  `QT_GRAPHICS`, `MSWIN_GRAPHICS`, `SHIM_GRAPHICS`, `DEFAULT_WINDOW_SYS`.
- Resource packaging: `DLB`, `DLBLIB`, `DLBRSRC`, `DLBFILE`,
  `VERSION_IN_DLB_FILENAME`.
- Runtime policy: `SYSCF`, `SYSCF_FILE`, `SECURE`, `CONFIG_ERROR_SECURE`.
- File layout: `HACKDIR`, `CHDIR`, `VAR_PLAYGROUND`, `NOCWD_ASSUMPTIONS`,
  file-prefix categories such as data, level, save, bones, lock, and config.
- Save/recovery: `INSURANCE`, `SELF_RECOVER`, `CHECK_PANIC_SAVE`,
  `COMPRESS`, `COMPRESS_EXTENSION`, `ZLIB_COMP`.
- Display and symbols: `ENHANCED_SYMBOLS`, `STATUS_HILITES`,
  `TILES_IN_GLYPHMAP`, tty tile/sound escape-code options.
- Diagnostics and development: `DEBUG`, `PANICTRACE`, `CRASHREPORT`,
  `NOSTATICFN`, `EXTRA_SANITY_CHECKS`, `FREE_ALL_MEMORY`, `MONITOR_HEAP`.
- Lua/security: `NHL_SANDBOX` and Lua platform flags passed as `SYSCFLAGS`.

The include chain matters. `config.h` pulls in `config1.h` early so autodetected
ports can override the initial assumptions. `global.h` later includes the
platform-specific headers such as `unixconf.h`, `pcconf.h`, `windconf.h`,
`vmsconf.h`, and `amiconf.h`. This means some macros are defaults, some are
port corrections, and some are final policy.

When reading a random `#ifdef MAGIC_NOODLES`-style block, first classify it:

- Is it platform compatibility?
- Is it a built feature?
- Is it resource packaging?
- Is it local policy/security?
- Does it change structs, enums, save layout, or generated tables?

The last category is the risky one for Nexus. Macros that change compiled
tables, struct fields, save formats, object or monster identities, or window
ABI are architectural. Macros that only affect a local path, helper executable,
or diagnostic option are usually build/install policy.

## Current Nexus Build Profile

Nexus currently uses `sys/unix/hints/nexus-local` as its active local Unix
profile. That hints file sets:

- a Nexus-local install root under `~/games/nethack/nexus`;
- `HACKDIR` to the installed playground;
- `SYSCF` and `SYSCF_FILE` pointing at the installed `sysconf`;
- `SECURE`;
- `CONFIG_ERROR_SECURE=FALSE` for local developer usability;
- gzip save compression via `/bin/gzip` and `.gz`;
- tty window objects and libraries;
- Lua platform flags via `SYSCFLAGS=-DLUA_USE_POSIX`;
- install hooks for both `sysconf` and `nexus.nethackrc`.

It does not define `DLB`, so the current Nexus developer build uses loose data
files in the installed playground rather than a packed `nhdat` archive.

This is good for early Nexus work because editing and inspecting installed
`dat/*.lua` files does not require rebuilding a data archive. A future release
profile could enable DLB, but that should be a packaging decision, not a world
architecture decision.

## DLB

DLB means "data librarian." It is NetHack's optional packed-resource layer.
When `DLB` is not defined, `include/dlb.h` aliases the DLB API directly to
stdio:

- `dlb` is `FILE`;
- `dlb_fopen` is `fopen`;
- `dlb_fgets` is `fgets`;
- `dlb_init()` and `dlb_cleanup()` are no-ops.

When `DLB` is defined, `src/dlb.c` provides a stdio-like interface over one or
more packed data libraries. The default Unix-style library is `nhdat`. Code
that reads support data uses `dlb_fopen()` and related calls so it can work in
both modes.

DLB has two implementations:

- `DLBLIB`: an archive file containing many support files plus an internal
  directory.
- `DLBRSRC`: legacy Mac resource-fork handling.

For Unix-like builds, `DLBLIB` is the relevant path. `src/dlb.c` opens the DLB
archive, reads its directory, keeps the archive open, and returns handles that
track a slice of the archive. Reads are clamped to that slice. If a named file
is not found inside the archive, the DLB layer falls back to looking for an
external data file with `fopen_datafile()`.

The archive tool is `util/dlb_main.c`. It can create, list, and extract DLB
archives. The top-level Unix makefile builds `dat/nhdat` with:

```text
../util/dlb cf nhdat $(DATDLB)
```

`sys/unix/Makefile.top` separates installed data into:

- `DATDLB`: help files, `dungeon.lua`, `tribute`, special Lua levels, quest Lua
  levels, and processed variable data such as `data`, `rumors`, `oracles`, and
  `options`.
- `DATNODLB`: files left outside the archive, currently `license`, `symbols`,
  and any window-port extra data in `VARDATND`.

The makefile decides whether to install DLB or loose files by looking for
`librarian` in `dat/options`. Its `check-dlb` target builds `nhdat` when that
option is present.

DLB implications for Nexus:

- DLB is packaging and lookup, not game logic.
- With DLB disabled, installed data files are ordinary files.
- With DLB enabled, many data files are read from `nhdat`, but the runtime can
  still fall back to loose external files for names not found in the archive.
- External pagers cannot see inside DLB, which is why `unixconf.h` warns about
  pager behavior when DLB is enabled.
- During early world work, DLB adds rebuild/reinstall friction for `dungeon.lua`
  and level Lua files.
- If Nexus later ships as a release package, DLB may be useful to keep the data
  install compact and coherent.

## SYSCF and sysconf

NetHack calls the global site configuration facility `SYSCF`. The installed
text file is normally named `sysconf`. "SYSCONFIG" is the conceptual role; in
this codebase the actual macro and many comments use `SYSCF`.

`include/config.h` enables it by default:

```c
#ifndef SYSCF
#define SYSCF
#define SYSCF_FILE "sysconf"
#endif
```

The Nexus local hints file overrides `SYSCF_FILE` at compile time so the binary
looks for the installed Nexus sysconf:

```text
-DSYSCF -DSYSCF_FILE="$(HACKDIR)/sysconf"
```

If a build has `SYSCF` and `SYSCF_FILE`, the file must exist and be readable.
`src/options.c` calls `assure_syscf_file()`, initializes config-error handling,
sets the option phase to `syscf_opt`, and parses the file with
`read_config_file(SYSCF_FILE, set_in_sysconf)`. If parsing fails, startup can
terminate.

`src/cfgfiles.c` uses the same parser for user config and sysconf but marks
some statements as sysconf-only. The sysconf-only statements populate the
global `sysopt` structure declared in `include/sys.h`.

Examples of sysconf-only policy:

- `WIZARDS`, `EXPLORERS`, `SHELLERS`;
- `MAXPLAYERS`;
- `SUPPORT`, `RECOVER`;
- `GENERICUSERS`;
- `DEBUGFILES`, `MSGHANDLER`;
- `BONES_POOLS`;
- score/record settings such as `PERSMAX`, `ENTRYMAX`, `POINTSMIN`;
- save and restore checks such as `CHECK_SAVE_UID`, `CHECK_PLNAME`;
- `SEDUCE`, `HIDEUSAGE`;
- `PANICTRACE_*`, `GDBPATH`, `GREPPATH`, `CRASHREPORTURL`;
- `ACCESSIBILITY`.

`OPTIONS` is different. It is accepted in sysconf, but it is ordinary NetHack
runtime option syntax used to provide system-wide defaults. User configuration
is still parsed later, so normal user options are not the same as sysconf-only
authority settings.

Important distinction:

- `sysconf` is local installation policy.
- `nethackrc` or `NETHACKOPTIONS` is user/player preference.
- command-line options and environment variables provide early overrides or
  config-file selection.

For Nexus, sysconf should not become a gameplay or lore data file. It is a
place for local authority, paths, score policy, diagnostics, and installation
defaults. Nexus world content belongs in `dat/`, Lua files, or future explicit
world-data modules.

## Startup Placement

On Unix, `sys/unix/unixmain.c` calls `initoptions()` early in startup. That is
where SYSCF policy becomes available before the game authorizes wizard/explore
mode, decides locking limits, opens files, and starts a new game.

The same Unix startup later calls `dlb_init()` before `newgame()`. This is
necessary because `newgame()` and the initialization beneath it read support
data such as dungeon topology and Lua levels. In non-DLB builds, this call
compiles away to a no-op macro.

The resulting order is:

1. process entry and early argument handling;
2. local config/sysconf and option setup;
3. authorization and file/playground handling;
4. DLB initialization if compiled;
5. `newgame()` and data-driven game startup.

That order explains why SYSCF is policy and DLB is resource plumbing. Both are
available before world topology is loaded, but neither is itself dungeon logic.

## Build and Generated Surfaces

NetHack's source tree is not the exact build tree. Unix builds are configured
by running setup machinery that uses hints files to generate active Makefiles.
For Nexus, the durable local policy belongs in `sys/unix/hints/nexus-local`,
not in generated `src/Makefile` edits.

Nearby generated surfaces:

- `sys/unix/setup.sh` and hints files generate the active Unix build files.
- `sys/unix/Makefile.top` coordinates game, utility, data, DLB, and install
  targets.
- `sys/unix/Makefile.dat` builds processed data such as `data`, `rumors`,
  `oracles`, `engrave`, `epitaph`, `bogusmon`, and `options`.
- `util/makedefs` generates several data and header artifacts from source
  tables and text inputs.
- `include/nhlua.h` is generated by the top-level makefile from the vendored
  Lua headers.
- Lua special levels are no longer compiled by a level compiler; they are data
  files installed or packed as Lua.

This matters because not every file that looks source-like should be edited as
source. Some are generated outputs. Some are installed loose data. Some are
packed into DLB depending on the build profile.

## Nearby Topics Worth Tracking

File prefixes and path policy:

NetHack routes different file classes through prefix categories: data, level,
save, bones, lock, score, config, trouble, and sysconf. Runtime config can set
some of these via statements like `HACKDIR`, `LEVELDIR`, `SAVEDIR`, `BONESDIR`,
`DATADIR`, `SCOREDIR`, `LOCKDIR`, `CONFIGDIR`, and `TROUBLEDIR`. In secure
builds, config errors and path control are intentionally constrained.

Security mode:

`SECURE`, `SHELL`, `SUSPEND`, `SHELLERS`, `CONFIG_ERROR_SECURE`, file
ownership, install permissions, and setuid/setgid assumptions interact. Nexus'
local developer profile uses non-setuid-style local permissions, but the
source still carries upstream multi-user assumptions.

Save compatibility:

Compile-time choices can affect save compatibility when they alter compiled
tables, feature sets, struct layout, or constants. Nexus should be especially
cautious around macros or edits that affect monsters, objects, dungeon
constants, level structs, global flags, or save/restore code.

Window ports:

Window systems are compiled into the binary and selected by default or runtime
option. UI resource files can be part of install data. This is separate from
world replacement, but it matters for test reproducibility and for deciding
which interface Nexus targets first.

Lua sandboxing:

Lua is both a data authoring language and a runtime embedding interface.
`NHL_SANDBOX` gates parts of `src/nhlua.c`; Lua's own platform flags are passed
through `SYSCFLAGS`. Nexus should treat Lua enablement, sandboxing, and helper
library exposure as engine policy, while treating Lua dungeon and level files
as world data.

Diagnostics:

`PANICTRACE`, `CRASHREPORT`, `DEBUGFILES`, `NOSTATICFN`, and
`EXTRA_SANITY_CHECKS` are useful during investigation but should not be mixed
with world design. They alter observability and sometimes binary behavior, not
canonical dungeon assumptions.

## Nexus Guidance

For the next phase of Nexus architecture:

1. Keep early Nexus builds non-DLB unless packaging becomes the topic.
2. Keep local developer build choices in `sys/unix/hints/nexus-local`.
3. Keep local runtime policy in `sys/unix/sysconf`.
4. Keep player/runtime preferences in `sys/unix/nexus.nethackrc`.
5. Put world topology and handcrafted level content in `dat/` Lua files.
6. Do not use sysconf for lore, monsters, item definitions, or branch rules.
7. Do not introduce a Nexus feature macro unless the code truly needs a
   compile-time difference.
8. If a new macro is unavoidable, document its default, affected files,
   save-format risk, and whether it is build policy or engine behavior.
9. Treat generated files and installed files as separate surfaces.
10. Record every intentional upstream divergence in `_work/divergences.md`.

## Open Questions

1. Should Nexus keep DLB disabled permanently for developer builds and reserve
   it only for release/package profiles?
2. Should Nexus create a separate release hints file later, distinct from
   `nexus-local`, with DLB and stricter config-error/security settings?
3. Should the Nexus architecture define a naming convention for any future
   Nexus-specific compile-time macros to avoid untracked `#ifdef` growth?
4. Should there be a short "configuration ownership" document that says where
   to put build policy, install policy, player defaults, world topology, and
   lore data?
5. `src/options.c` contains SYSCF parsing logic in both `initoptions()` and
   `initoptions_init()`. Is the double parse on the ordinary startup path
   intentional, harmless duplication, or a NetHack 5 transition artifact worth
   auditing separately?
6. If Nexus eventually moves more content into Lua, should Lua file lookup stay
   purely under the existing data-prefix/DLB system, or should Nexus add a
   clearer world-data namespace?
7. Which compile-time choices are included in NetHack's version/feature
   compatibility checks strongly enough to protect Nexus saves after future
   build-profile changes?

## Source Anchors

- `include/config.h`: central compile-time defaults, SYSCF default, window
  system selection, file names, compression, DLB comment block, diagnostics.
- `include/config1.h`: platform autodetection and early port overrides.
- `include/global.h`: global portability include order, support file names,
  common types, feature constants.
- `include/unixconf.h`: Unix port choices, pager/DLB notes, shell/job-control
  behavior, random source, local Unix defaults.
- `include/dlb.h`: DLB API, stdio aliases when DLB is disabled, archive mode
  declarations when enabled.
- `src/dlb.c`: DLB archive lookup, directory parsing, file-slice reads, loose
  file fallback.
- `util/dlb_main.c`: archive creation/list/extract utility.
- `sys/unix/Makefile.top`: `DATDLB`, `DATNODLB`, `check-dlb`, `dlb`, install
  split between DLB and loose data files.
- `sys/unix/Makefile.dat`: generated data targets.
- `sys/unix/hints/nexus-local`: current Nexus build and install policy.
- `sys/unix/sysconf`: sample installed SYSCF file.
- `src/options.c`: option initialization, SYSCF parse phase, user rc parsing.
- `src/cfgfiles.c`: shared config parser and sysconf-only statements.
- `include/sys.h` and `src/sys.c`: `sysopt` storage and defaults.
- `sys/unix/unixmain.c`: Unix startup order, `initoptions()`, `dlb_init()`,
  wizard/explore authorization, lock/player handling.
