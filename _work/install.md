# Nexus Local Install

Nexus uses a named local install root so it can coexist with other NetHack
variants on the same machine.

## Variant Launcher Convention

Keep bare `nethack` out of the Nexus workflow. On this machine, multiple
NetHack derivatives may exist at the same time:

- Floating Eye local development
- Floating Eye server build
- Towel UI experiment
- Nexus
- NLE
- upstream or stock NetHack builds

Use explicit launcher names in `~/.local/bin`:

```text
nexus
nh-floatingeye
nh-fe-server
nh-towel
nh-nle
nh-vanilla-50
```

The launcher name should identify the variant or build line. `nethack` can
remain whatever personal default the user chooses.

## Nexus Install Root

The Nexus local Unix hint is:

```text
sys/unix/hints/nexus-local
```

It installs under:

```text
~/games/nethack/nexus/
```

The generated NetHack wrapper is:

```text
~/games/nethack/nexus/games/nethack
```

The stable launcher is:

```text
~/.local/bin/nexus
```

That launcher sets:

```text
HACKDIR=/home/mlehotay/games/nethack/nexus/games/lib/nethackdir
NETHACKOPTIONS=@/home/mlehotay/games/nethack/nexus/games/lib/nethackdir/nexus.nethackrc
```

This prevents Nexus from inheriting unrelated settings from a shared
`~/.nethackrc`, such as variant-specific roles, fruit names, menu colors, or
window-port experiments.

The launcher must be a regular shell wrapper, not a symlink to the generated
NetHack wrapper. `make install` recreates `~/games/nethack/nexus/games/nethack`,
and the stable wrapper needs to keep exporting the Nexus rc path.

The `nexus-local` hint also sets the save compression command to `/bin/gzip`
with `.gz` save files. The upstream default can point at `/usr/bin/compress`,
which is not available on this machine.

## Setup And Install

From the repository root:

```sh
cd sys/unix
sh setup.sh hints/nexus-local
cd ../..
make fetch-Lua
make all
make install
```

`nexus-local` also installs `sys/unix/sysconf`, because this NetHack 5.0.0 tree
uses the runtime `SYSCF` configuration path. It also installs
`sys/unix/nexus.nethackrc` into the same install root for the `nexus` launcher.

The local launcher is maintained outside the repository at `~/.local/bin/nexus`
so it can remain stable while the generated NetHack wrapper is recreated by
`make install`.
