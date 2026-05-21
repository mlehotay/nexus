# Nexus Divergences From Upstream NetHack

This file records intentional departures from upstream NetHack 5.0.0.

Record divergences that affect startup, topology, build assumptions, system
semantics, or compatibility with upstream data. Do not record ordinary notes or
temporary investigation.

Entry shape:

```text
## YYYY-MM-DD - Short Title

- Plan: `plan-id`
- Files:
- Upstream assumption:
- Nexus change:
- Reason:
- Verification:
```

## 2026-05-20 - Local Nexus Runtime Isolation

- Plan: `0001-environment-setup`
- Files: `sys/unix/hints/nexus-local`, `sys/unix/nexus.nethackrc`
- Upstream assumption: a local Unix install may use the default user rc search
  path and the compile-time default compression command.
- Nexus change: the `nexus` launcher exports `NETHACKOPTIONS` to an installed
  Nexus rc file, and `nexus-local` compiles save compression as `/bin/gzip`
  with `.gz` files.
- Reason: this machine has multiple NetHack derivatives and a shared
  `~/.nethackrc`; Nexus must not inherit unrelated fruit, role, UI, or window
  settings. `/usr/bin/compress` is not available on this system.
- Verification: `make all`, `make install`, `nexus --version`, a
  pseudo-terminal launch to the NetHack 5.0.0 character prompt, and a
  throwaway `codextest` save file written as `1000codextest.gz`.
