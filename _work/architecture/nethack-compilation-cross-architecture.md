# NetHack Compilation And Cross-Compile Architecture

Status: source-grounded vanilla NetHack 5 architecture note.

Date: 2026-05-21

## Executive Summary

NetHack 5 treats compilation as an architecture concern, not just a build
detail. The 5.0 build changes remove several historical host-platform data
generation steps and make cross-compilation mostly about one remaining problem:
building the game, Lua, platform support, and selected window support for the
target platform.

The main containment mechanism is separation:

- host tools run on the build host and produce portable package inputs;
- target objects are compiled with `TARGET_*` tools and target-specific flags;
- system ports live under `sys/`;
- window ports live under `win/`;
- build profiles and target selection live in makefiles and hints;
- runtime data is packaged either as loose files or through DLB;
- site/runtime policy is pushed into `sysconf` when `SYSCF` is enabled;
- dungeon, special level, and quest text sources are Lua runtime data instead
  of architecture-dependent build outputs.

For Nexus, this reinforces the current rule: use hints and makefiles for build
profiles, not world design. The first custom-world milestone should stay on the
existing local Unix/tty build profile, then add release or WASM build profiles
only when they become real deliverables.

## Main Source Surfaces

The portable build story is spread across a few layers:

- `Cross-compiling` explains the host/target model and why NetHack 5 changed
  the build.
- `sys/unix/setup.sh` installs active makefiles from the `sys/unix/Makefile.*`
  templates and selected hints.
- `sys/unix/Makefile.top` coordinates top-level targets, Lua support, generated
  data files, special level data, DLB packaging, install/update, and package
  handoff.
- `sys/unix/Makefile.src` selects C source files, system source files, window
  source files, compiler/linker variables, target-prefixed object output, and
  default `TARGET_*` variables.
- `sys/unix/hints/*.500` and `sys/unix/hints/include/*.500` contain platform,
  compiler, window, cross-compile, package, and install policy.
- `include/config*.h`, `include/global.h`, `include/unixconf.h`, and related
  platform headers are the C preprocessor layer after make has selected the
  build.
- `sys/windows/`, `sys/msdos/`, `sys/amiga/`, `sys/libnh/`, and other `sys/`
  folders hold system-specific ports or build flows.

This is intentionally not a single clean abstraction. It is an accumulated
portability system whose main control points are make variables, hints, macros,
source lists, and runtime data conventions.

## What Changed In NetHack 5

The top-level `Cross-compiling` document describes the central change from
NetHack 3.6 to NetHack 5:

- NetHack 3.6 built and ran `makedefs`, a level compiler, and a dungeon compiler
  during the build. Some outputs were architecture- or platform-dependent.
- NetHack 5 still builds and runs host utilities, but dungeon descriptions,
  special levels, and quest text are Lua data loaded and interpreted during
  gameplay.
- As a result, the build no longer needs to execute target-shaped level,
  dungeon, or quest text generators on the host.

The file `doc/fixes5-0-0.txt` records the same architectural change: the
build-time level and dungeon compilers were replaced with runtime Lua loading,
quest text conversion moved to Lua quest text loaded at runtime, and some
formerly build-time option/version functionality was split so target-platform
information can be produced by the target build.

This matters because cross-compiling is not just "use another compiler." If the
host emits binary game data using host struct layout, byte order, pointer size,
or alignment rules, that output may not be valid on the target. NetHack 5
reduces those host-generated target-shaped artifacts.

## Host Side

Host-side work is the part of the build that must execute on the build machine.
The `Cross-compiling` file identifies mandatory host work:

- build a host-native `util/makedefs` with `-DCROSSCOMPILE`;
- run `makedefs` to generate portable package/build inputs such as data,
  rumors, oracles, options, and headers;
- optionally build host utilities such as `dlb`, `uudecode`, `tilemap`,
  `tile2bmp`, `gif2txt`, and `ppmwrite` when a target package needs their
  outputs.

Some source files can be needed both by host tools and the target executable.
The cross-compile notes explicitly call out the need to keep host-native object
files separate from target object files. In the Unix make path, target objects
are isolated with `TARGETPFX`, which cross hints set to a directory such as
`../targets/wasm/` or `../targets/msdos/`.

`doc/makedefs.txt` shows that `makedefs` remains a general build-time utility,
but its job is narrower than in older NetHack releases. It still generates
files such as `onames.h`, `pm.h`, `date.h`, `data.base`, rumors, oracles,
bogus monster names, engravings, epitaphs, and conditional documentation
filters.

## Target Side

Target-side work is compiled by the compiler that emits code for the eventual
runtime platform. `sys/unix/Makefile.src` defaults the target variables to the
ordinary native variables:

- `TARGET_CC = $(CC)`
- `TARGET_CFLAGS = $(CFLAGS) $(CSTD)`
- `TARGET_LINK = $(LINK)`
- `TARGET_CXX = $(CXX)`
- `TARGET_CXXFLAGS = $(CXXFLAGS)`
- `TARGET_LIBS = $(LIBS)`
- `TARGET_AR = $(AR)`

Cross hints override those variables. The target build includes:

- the NetHack core C sources;
- the selected `sys/` platform source files;
- the selected `win/` window source files, or shim/libnh sources;
- Lua, which is mandatory in NetHack 5;
- optional regular expression, curses, PDCurses, tile, sound, or package
  support required by the target.

`CROSSCOMPILE` and `CROSSCOMPILE_TARGET` are the broad C macro signals that code
is being built in this split mode. Target-specific macros such as
`CROSS_TO_WASM`, `CROSS_TO_MSDOS`, `CROSS_TO_MIPS`, and `CROSS_TO_AMIGA` refine
that choice.

## Unix Hints And Multi-Window Selection

The Unix hints system is the main build-profile containment mechanism. A hints
file can set install paths, compiler flags, `SYSCF`, compression commands,
selected window source, libraries, ownership, permissions, and extra install
steps.

`sys/unix/hints/include/multiw-2.500` contains the multi-window selection layer.
It accepts make-time selections such as:

- `WANT_WIN_TTY=1`
- `WANT_WIN_CURSES=1`
- `WANT_WIN_X11=1`
- `WANT_WIN_QT=1`
- `WANT_WIN_ALL=1`
- `WANT_DEFAULT=tty|curses|X11|Qt`
- `WANT_LIBNH=1`

That include file then produces `WINCFLAGS`, `WINSRC`, and window object lists.
This is where build variability becomes linked window functionality. It is
still not world logic; it only controls which interfaces are compiled into the
program and which interface is selected by default.

Nexus already uses a local hints profile, `sys/unix/hints/nexus-local`, for a
Unix/tty developer install. That profile sets local install paths, `SYSCF`,
`SYSCF_FILE`, `SECURE`, gzip compression, Lua POSIX flags, tty window source,
and local file permissions. It deliberately says it is not a new system port or
window port.

## Cross-Compile Targets In This Tree

`sys/unix/hints/include/cross-pre1.500` declares the current cross target modes:

- `CROSS_TO_MSDOS`
- `CROSS_TO_WASM`
- `CROSS_TO_MIPS`
- `CROSS_TO_AMIGA`

Each mode sets `CROSS=1`, usually requests target Lua, sets `TARGET`,
`TARGETDIR`, `TARGETPFX`, and clears target libraries or packaging variables
before later includes repopulate them.

`sys/unix/hints/include/cross-pre2.500` contains the target recipes.

For MSDOS, it uses a DJGPP cross compiler, builds target Lua and PDCurses, sets
`-DDLB`, `-DCROSSCOMPILE_TARGET`, `-DCROSS_TO_MSDOS`, selects `sys/msdos` and
`sys/share` sources, and emits target executables into `targets/msdos/`.
Packaging is completed by `dospkg` rules in `cross-post.500`.

For WASM, it uses Emscripten (`emcc`, `emar`), sets `DEFAULT_WINDOW_SYS="shim"`,
uses `SHIM_GRAPHICS` and `LIBNH`, disables tty graphics and mail, enables DLB,
uses `sys/libnh/libnhmain.c`, `win/shim/winshim.c`, and Unix/shared support
sources, and emits `targets/wasm/nethack.js` plus embedded data. The
`sys/libnh/README.md` documents this as the `make CROSS_TO_WASM=1 all` path.

For MIPS, it uses `mipsel-linux-gnu-*` tools, target Lua, target ncurses, DLB,
Unix system sources, and package rules that assemble a MIPS package under
`targets/mips/`.

For Amiga, it uses a m68k Amiga GCC toolchain, target Lua, target regex, Amiga
system and window sources, tile support, and package rules that produce
`targets/amiga/NH370AMI.ZIP`. `sys/amiga/README.amiga` says native Amiga
compilation is not supported for this path; cross-compilation with GCC is
required.

Windows has a separate build flow. `sys/windows/build-vs.txt` documents Visual
Studio x64 and ARM64 targets. It also records the same host/target issue: to
cross-build x64 from ARM64 or ARM64 from x64, the native build must first
produce host-native tools such as `uudecode.exe`, `makedefs.exe`,
`tilemap.exe`, `tile2bmp.exe`, and `dlb.exe`.

## DLB, SYSCF, And Data Packaging

DLB and `SYSCF` are adjacent to compilation because they decide how the compiled
program will find data and policy at runtime.

`sys/unix/Makefile.top` defines the data sets:

- `DATDLB` contains data that can be packed into `dat/nhdat`, including help
  files, `dungeon.lua`, tribute, special level Lua files, quest level Lua files,
  and runtime data such as `quest.lua`, `rumors`, and `oracles`.
- `DATNODLB` contains files left outside the DLB, such as `license` and
  `symbols`, plus interface-specific data.
- `check-dlb` inspects `dat/options` for `librarian` and builds DLB when
  requested.
- `dofiles-dlb` installs `nhdat` plus non-DLB data; `dofiles-nodlb` installs
  loose data files.

Cross builds tend to force DLB on because a single data bundle is easier to
package into constrained or browser-like targets. The WASM path embeds
`wasm-data` into the Emscripten output and copies a target `sysconf` into that
data root.

`SYSCF` shifts some site policy out of the executable and into a runtime
`sysconf` file. In a cross-compile context, that is useful because the target
package can carry target-appropriate paths, secure settings, and runtime policy
instead of baking everything into C macros.

## Generated Artifacts

Generated artifacts fall into three rough groups.

Build support and headers:

- `include/nhlua.h` is generated by the top makefile from the fetched Lua
  headers.
- Lua is fetched separately and built into `lib/lua/liblua-5.4.8.a` for native
  builds or target-prefixed target libraries for cross builds.
- `makedefs` emits headers such as `pm.h`, `onames.h`, and `date.h`.

Runtime data:

- `data`, `rumors`, `oracles`, `options`, `bogusmon`, `engrave`, and `epitaph`
  are generated through `makedefs` and `dat/` make rules.
- `dungeon.lua`, special level Lua files, quest level Lua files, and
  `quest.lua` are runtime data included directly in the package or DLB.

Interface/package data:

- tile outputs such as `nhtiles.bmp` and `x11tiles` are generated only when the
  selected target/window package needs them.
- target packages create records, logs, `sysconf`, DLB data, and platform
  wrapper files appropriate to the target.

The important point for Nexus is that not every generated file is a source of
world semantics. Some generated files are package mechanics, some are object or
monster indexes, and some are platform/window assets.

## How Variability Is Contained

The build contains variability through layered choices:

1. Setup selects an active makefile/hints profile.
2. Hints set install paths, compiler flags, system policy, window choices, and
   optional target modes.
3. Multi-window includes translate `WANT_WIN_*` options into C macros and source
   lists.
4. Cross includes translate `CROSS_TO_*` options into target compilers, target
   object directories, target source lists, target flags, and package rules.
5. C headers compile out or compile in platform, security, file layout,
   compression, DLB, window, and compatibility behavior.
6. DLB and loose-file install rules decide the runtime data layout.
7. `SYSCF` and runtime config files decide late policy that should not require
   rebuilding the executable.
8. Lua dungeon, level, and quest files defer world topology and authored content
   to runtime data.

This is the reason the other vanilla architecture reports should not be read as
independent modules. System ports, window ports, DLB, `SYSCF`, Lua data loading,
and savefile compatibility intersect at build time. The build system chooses
which combinations exist in a binary and package; runtime code then operates
within those compiled and packaged choices.

## Nexus Implications

Nexus should keep build-profile concerns separate from world replacement:

- Continue using `sys/unix/hints/nexus-local` as the local native development
  profile.
- Keep the first milestone on the existing Unix/tty path unless the custom
  dungeon topology truly requires otherwise.
- Do not put lore, branch behavior, dungeon rules, item definitions, or Nexus
  world identity into hints files.
- Treat DLB as a packaging choice. Keep loose files convenient for development
  if useful, and enable DLB for release or WASM-style targets when packaging
  requires it.
- Treat `SYSCF` as runtime/site policy, not game design.
- If Nexus later needs a browser or embedded frontend, start from the existing
  `CROSS_TO_WASM`, libnh, and shim architecture instead of inventing a separate
  engine entry point.
- If Nexus later needs release builds, create explicit build profiles such as
  `nexus-release` or `nexus-wasm` rather than overloading `nexus-local`.
- Record build-profile differences as project procedure or divergence only
  when they intentionally depart from upstream behavior.

The NetHack 5 Lua conversion is directly helpful for Nexus: `dat/dungeon.lua`
and Lua special levels are already runtime-authored data, so the first custom
world does not need to introduce a new compiler, parser, or target-dependent
generated format.

## Open Questions

- Should Nexus have distinct `nexus-local`, `nexus-release`, and `nexus-wasm`
  hints profiles, or should cross/release builds wait until after the first
  custom level milestone?
- Should development installs keep DLB disabled for easier inspection, or
  should Nexus always exercise the same DLB path expected in release packages?
- If Nexus adds custom Lua dungeon and level files, what makefile or data-list
  changes are required so native, DLB, and future cross packages include the
  same files?
- Which generated files must be regenerated when Nexus changes C object tables,
  monster tables, role tables, or options?
- How should Nexus define save compatibility across build profiles, especially
  if a future WASM build uses different file layout or persistence plumbing?
- Should `nexus-local` remain tty-only until the first milestone is complete, or
  should curses be added early to exercise a second window port?
- What is the minimum useful CI matrix: native Unix/tty only, native plus DLB,
  or native plus one cross target?
- If a future Nexus frontend uses libnh/shim, should the window shim remain an
  engine interface only, or should Nexus expose higher-level semantic events?

## Source Anchors

- `Cross-compiling`
- `doc/fixes5-0-0.txt`
- `doc/makedefs.txt`
- `sys/unix/Makefile.top`
- `sys/unix/Makefile.src`
- `sys/unix/README-hints`
- `sys/unix/hints/nexus-local`
- `sys/unix/hints/include/multiw-2.500`
- `sys/unix/hints/include/cross-pre1.500`
- `sys/unix/hints/include/cross-pre2.500`
- `sys/unix/hints/include/cross-post.500`
- `sys/libnh/README.md`
- `sys/windows/build-vs.txt`
- `sys/amiga/README.amiga`
