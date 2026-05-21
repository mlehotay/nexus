# NetHack System and Window Port Architecture

Date: 2026-05-21

Scope: NetHack 5.0.0 system ports, window ports, `win/shim/winshim.c`,
WebAssembly/libnh support, and WINCHAIN.

This report complements:

- `_work/architecture/vanilla-nethack-architecture.md`
- `_work/architecture/nethack-build-config-resource-architecture.md`

The key distinction is that NetHack has system ports and window ports. They are
related but not the same thing.

## Summary

System ports adapt NetHack to a host operating environment: process entry,
signals, filesystem layout, user identity, permissions, terminal setup, random
sources, mail, suspend/shell behavior, install paths, and build rules.

Window ports adapt NetHack to a display/input environment: map rendering,
message windows, menus, status, text windows, prompts, glyph drawing, keyboard
and mouse input, colors, and window capabilities.

The boundary is practical rather than pure. Unix startup calls the window
selection machinery. Window ports sometimes need system-port helpers for tty
state or files. But the main interface is clear:

- system ports live mostly under `sys/` and platform config headers;
- window ports live mostly under `win/`;
- the game core talks to the selected UI through the global `windowprocs`
  function table.

For Nexus, this means the initial custom world should not need a new system
port or window port. Nexus currently uses the Unix system port and tty window
port through `sys/unix/hints/nexus-local`.

## System Ports

A system port is the code and build configuration that makes NetHack run as a
program on a platform. On Unix-like builds, the important files include:

- `sys/unix/unixmain.c`: process entry for normal Unix NetHack.
- `sys/unix/unixunix.c`: Unix-specific helpers such as shell/suspend checks and
  user-oriented behavior.
- `sys/unix/unixres.c`: Unix resource/path support.
- `sys/share/ioctl.c`, `sys/share/unixtty.c`, `sys/share/pcunix.c`: shared
  tty and Unix-ish helpers.
- `include/unixconf.h`: Unix port compile-time settings.
- `sys/unix/hints/*.500` and `sys/unix/hints/include/*.500`: build profile
  fragments.

Other system ports have their own entry and support files under directories
such as `sys/windows`, `sys/amiga`, and VMS-related headers.

The Unix startup sequence shows system-port responsibilities:

1. set process globals such as `gh.hname` and `svh.hackpid`;
2. select the default window interface with `choose_windows(DEFAULT_WINDOW_SYS)`;
3. process early options such as path, version, and score modes;
4. change to the playground/data directory when configured;
5. initialize options and sysconf;
6. identify the user and authorize modes;
7. process command-line options including `-w<windowtype>`;
8. commit any window chain;
9. initialize the selected window system;
10. initialize resource/data systems and enter restore/new-game flow.

That is why system ports are not just "OS glue." They own the process-level
order that makes sysconf, DLB, windows, locks, saves, and startup behavior
cohere.

## Window Ports

A window port implements `struct window_procs` from `include/winprocs.h`.
This is a large vtable of UI callbacks. It includes:

- lifecycle: `init_nhwindows`, `exit_nhwindows`, suspend/resume;
- character setup: `player_selection`, `askname`;
- window creation and display: message, status, map, menu, text, permanent
  inventory;
- output: `putstr`, `putmixed`, `print_glyph`, `raw_print`;
- input: `nhgetch`, `nh_poskey`, `yn_function`, `getlin`, `get_ext_cmd`;
- menus: start/add/end/select;
- synchronization and delay hooks;
- status field initialization and updates;
- history, inventory, preferences, color, and control hooks.

The global variable `windowprocs` stores the active implementation. Most game
code does not call tty, curses, X11, or shim functions directly. It calls
through macros such as `create_nhwindow`, `display_nhwindow`, `print_glyph`,
`raw_print`, and `nhgetch`, which dispatch through `windowprocs`.

Examples:

- `win/tty/wintty.c` defines `tty_procs`.
- `win/curses/cursmain.c` defines `curses_procs`.
- X11, Qt, Windows, Amiga, and other ports define their own tables.
- `win/shim/winshim.c` defines `shim_procs`.

Each window port advertises capabilities through `wincap`, `wincap2`, and
`has_color`. The core and option system use those flags to decide which
features are available. Examples include color, mouse support, tiled map,
permanent inventory, UTF-8 strings, status highlighting, terminal sizing,
window borders, menu scrolling, and extra status fields.

`src/windows.c` is the registry and dispatcher. Its `winchoices[]` table is
compiled from the enabled window macros:

- `TTY_GRAPHICS`
- `CURSES_GRAPHICS`
- `X11_GRAPHICS`
- `QT_GRAPHICS`
- `MSWIN_GRAPHICS`
- `SHIM_GRAPHICS`
- others on older or platform-specific ports

`choose_windows()` finds a named implementation, copies its vtable into
`windowprocs`, and runs the optional init/undo routine for ports that need
port-specific setup. Names beginning with `-` or `+` are reserved for WINCHAIN
processors and are not normal selectable window types.

## Modularity Model

The modularity is C-level function-table modularity, not plugin loading.

Window ports are selected at compile time and linked into the binary. Runtime
selection only chooses among the compiled-in tables. If a build does not define
`CURSES_GRAPHICS`, then `curses` is not a runtime choice. If a build does not
compile `win/shim/winshim.c` with `SHIM_GRAPHICS`, then `shim` is not a runtime
choice.

This has several consequences:

- Adding a new window port is a source/build change, not a data change.
- Adding a new system port is larger: entry point, platform config, build
  machinery, filesystem/process behavior, and often terminal/resource helpers.
- The core depends on the `window_procs` contract being complete and stable.
- Capability flags are part of the UI contract.
- Some "generic" helper implementations live in core files such as
  `src/windows.c`, allowing ports to reuse functions like generic mixed text,
  message menu behavior, or status fallbacks.

The design is old-school but effective. It lets NetHack support different
display environments without making dungeon, object, monster, and turn logic
depend on a specific renderer.

## Shim Window Port

`win/shim/winshim.c` is explicitly described as "not an actual windowing port"
but a fake window port for libnethack. Practically, it is a bridge between the
NetHack `window_procs` interface and an embedding application.

It defines `shim_procs`, a normal `struct window_procs`, so the core sees it as
a window port named `shim`. But most shim functions do not render anything.
Instead, they package the window call name, return pointer, format string, and
arguments, then call an external callback supplied by the embedding host.

There are two callback modes:

Native `libnethack.a` mode:

- `shim_graphics_set_callback(shim_callback_t cb)` stores a C callback.
- Each shim function calls that callback with:
  - the window function name;
  - a return-value pointer, or null for void;
  - a compact format string;
  - variadic arguments.

WebAssembly/Emscripten mode:

- `shim_graphics_set_callback(char *cbName)` stores the name of a JavaScript
  callback on `globalThis`.
- Shim calls go through an `EM_JS` helper named `local_callback`.
- `local_callback` converts WASM pointers and typed arguments into JavaScript
  values, calls the named JS function, writes the return value back to WASM
  memory, and resumes execution.

The format strings are a miniature ABI. The first character describes the
return type. Remaining characters describe argument types. The README documents
types such as integer, string, pointer, character, and void. The C source also
has specialized internal conventions for coord-sized values and other cases.

The shim's capability flags advertise an ASCII/color/mouse-capable interface
with status-related features when compiled. That means the embedding host is
responsible for actually honoring the callbacks well enough to satisfy the
advertised capabilities.

## WASM and libnh

The WASM build is not just "Unix NetHack in a browser." It uses a different
system entry path and the shim window port.

Important files:

- `sys/libnh/libnhmain.c`: library-oriented entry point. For Emscripten, the
  exported entry is `main`; otherwise it exposes `nhmain`.
- `sys/libnh/README.md`: describes `libnethack.a`, `nethack.js`, and the shim
  callback API.
- `sys/unix/hints/include/cross-pre2.500`: WASM build fragment.
- `win/shim/winshim.c`: shim window implementation.

The WASM hints set:

- Emscripten tools such as `emcc` and `emar`;
- `CROSS_TO_WASM` and `CROSSCOMPILE_TARGET`;
- `DLB`;
- `HACKDIR`;
- `DEFAULT_WINDOW_SYS="shim"`;
- `NOTTYGRAPHICS`;
- `SHIM_GRAPHICS`;
- `LIBNH`;
- a reduced source set using `sys/libnh/libnhmain.c` and `win/shim/winshim.c`;
- output under `targets/wasm`.

`libnhmain.c` mirrors much of Unix startup but is shaped for embedding. In
Emscripten builds it also calls JavaScript helper initialization functions:

- `js_helpers_init()`;
- `js_constants_init()`;
- `js_globals_init()`.

The shim's Emscripten path uses Asyncify. The source comments say the
implementation uses `Asyncify.handleSleep()` rather than `handleAsync()` because
the callback is indirect through a runtime callback name and Emscripten cannot
predict the stack-unwinding path. It also has a reentry guard because nested
shim callbacks can break Asyncify.

There is a special Emscripten case for inventory updates: a comment says calling
`repopulate_perminvent()` from `shim_update_inventory()` causes reentrancy that
breaks Asyncify. The code still calls `repopulate_perminvent()` when permanent
inventory is enabled, but the comment marks it as a known sensitive area.

For Nexus, the main architectural point is that WASM already has a plausible UI
escape hatch: use the shim port and let JavaScript own rendering/input. That is
separate from the world architecture and should not drive the first custom Lua
level milestone.

## WINCHAIN

WINCHAIN is an optional window-call processor chain. It is compiled with
`WINCHAIN` and included by build options such as `WANT_WINCHAIN=1`.

Normal window dispatch is:

```text
core -> windowprocs -> real window port
```

WINCHAIN changes this to:

```text
core -> -chainin -> processor(s) -> -chainout -> real window port
```

The processor chain is assembled in `src/windows.c`:

1. runtime configuration adds `+` processors with `addto_windowchain()`;
2. `commit_windowchain()` prepends `-chainin` and appends `-chainout`;
3. each link gets an allocation phase and an initialization phase;
4. the first chain link's `window_procs` replaces global `windowprocs`;
5. calls now flow through chain-aware function tables.

`include/winprocs.h` defines both:

- `struct window_procs`: the normal vtable, with no per-link data parameter;
- `struct chain_procs`: a parallel vtable whose first argument is a private
  per-link data pointer.

The two adapter endpoints are:

- `win/chain/wc_chainin.c`: adapts normal `window_procs` calls into
  `chain_procs` calls by inserting private chain data.
- `win/chain/wc_chainout.c`: adapts final `chain_procs` calls back into the
  real `window_procs` signature.

`win/chain/wc_trace.c` is an example processor. It logs window calls to a trace
file and forwards each call to the next chain element.

This is middleware for UI calls. It is not a system port and not a renderer by
itself. Its natural uses are tracing, logging, inspection, transformation, or
testing of the window API.

## Configuration Surface

Window-port selection can happen in several places:

- compile-time macros decide which ports are linked;
- `DEFAULT_WINDOW_SYS` decides the initial choice;
- command-line `-w<name>` can select another compiled-in port;
- config options can set window type;
- WINCHAIN options can add processors when compiled.

The hints system exposes common build choices:

- `WANT_WIN_TTY=1`;
- `WANT_WIN_CURSES=1`;
- `WANT_WIN_X11=1`;
- `WANT_WIN_Qt=1`;
- `WANT_WIN_ALL=1`;
- `WANT_WINCHAIN=1`;
- `WANT_LIBNH=1`;
- `CROSS_TO_WASM=1`;
- `WANT_DEFAULT=tty`, `curses`, `X11`, or `Qt`.

Nexus' local profile is intentionally simple: Unix system port, tty window
port, no WINCHAIN, no shim, no WASM. That keeps the first milestone focused on
world topology and level loading rather than display abstraction.

## Nexus Implications

The system/window port split should inform Nexus architecture but not dominate
it.

Keep for now:

- Unix system port through `sys/unix`;
- tty window port through `win/tty`;
- local hints in `sys/unix/hints/nexus-local`;
- no new system port;
- no new window port;
- no WINCHAIN unless tracing the window API becomes useful;
- no WASM work until the native tiny world boots.

Potential later uses:

- WINCHAIN tracing could help document the UI call sequence during startup,
  character selection, map display, inventory, and prompts.
- The shim port could become a future path for a browser or library embedding
  of Nexus.
- A separate release or experimental hints file could enable `SHIM_GRAPHICS`,
  `LIBNH`, or `CROSS_TO_WASM` without complicating `nexus-local`.

Avoid:

- putting world logic into system-port files;
- putting gameplay rules into window ports;
- treating shim callbacks as a gameplay API;
- letting WASM packaging decisions shape early C/Lua world architecture;
- creating a Nexus window port just to change text, symbols, or defaults.

## Open Questions

1. Should Nexus eventually keep a separate `nexus-wasm` or `nexus-libnh` hints
   profile rather than extending `nexus-local`?
2. Would WINCHAIN trace logs be useful for documenting first-turn UI flow, or is
   that premature until the custom level boots?
3. If Nexus later wants a richer frontend, should it target the existing shim
   callback API first instead of creating a new window port?
4. Does the shim API expose enough structured glyph/status/menu information for
   a future Nexus-specific web UI, or would it need a narrower higher-level API?
5. Should Nexus record a firm boundary that system/window ports must not carry
   lore, branch rules, or world topology?
6. Should the vanilla architecture plan include a small appendix listing which
   game core modules call `windowprocs` directly versus using wrapper helpers?

## Source Anchors

- `include/winprocs.h`: `struct window_procs`, `struct chain_procs`, window
  capability flags, WINCHAIN setup constants.
- `include/wintype.h`: `winid`, menu item types, window kinds, glyph info,
  text attributes.
- `src/windows.c`: active `windowprocs`, compiled window registry,
  `choose_windows()`, WINCHAIN assembly, generic window helpers.
- `sys/unix/unixmain.c`: normal Unix startup order and window initialization.
- `sys/libnh/libnhmain.c`: libnh/WASM-style startup.
- `win/tty/wintty.c`: tty window port implementation table.
- `win/curses/cursmain.c`: curses window port implementation table.
- `win/shim/winshim.c`: shim callback bridge and Emscripten Asyncify bridge.
- `win/chain/wc_chainin.c`: normal window-procs to chain-procs adapter.
- `win/chain/wc_chainout.c`: chain-procs back to normal window-procs adapter.
- `win/chain/wc_trace.c`: example trace processor.
- `sys/libnh/README.md`: libnh and WASM API notes.
- `sys/unix/README-hints`: build switches for window ports, WINCHAIN, libnh,
  and WASM.
- `sys/unix/hints/include/cross-pre2.500`: WASM build settings.
- `sys/unix/Makefile.src`: shim and chain source/object lists.
