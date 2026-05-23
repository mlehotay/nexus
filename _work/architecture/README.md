# Architecture Reports

Short source-grounded reports for understanding vanilla NetHack 5 before
designing durable Nexus architecture.

Executive summary:

- NetHack is a C simulation engine with Lua-authored dungeon topology and
  special levels, but most durable game identity still lives in C structs,
  globals, tables, and save/restore code.
- The safest Nexus path is data-first: replace world topology and levels before
  changing engine systems.
- Compile-time macros, DLB, SYSCF, system ports, and window ports are build,
  packaging, runtime policy, and platform mechanisms. They are not good places
  for world or lore logic.
- Compilation and cross-compilation assemble those mechanisms into a concrete
  binary and package; hints and make variables contain most of that
  variability.
- Savefiles and bonesfiles show the real persistence scopes: global game
  state, level-local state, and cross-game bones transfer state.
- Open Nexus architecture questions should be answered against these existing
  responsibilities instead of inventing a clean architecture from scratch.

Reports:

- `vanilla-nethack-architecture.md`
- `nethack-build-config-resource-architecture.md`
- `nethack-compilation-cross-architecture.md`
- `nethack-system-window-port-architecture.md`
- `nethack-save-bones-architecture.md`
- `nexus-cflag.md`
- `nexus-boot-guard-map.md`
