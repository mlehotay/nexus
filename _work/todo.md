# Nexus Task Descriptions

This file defines task meaning, intent, and detailed notes.
`_work/tasks.csv` tracks task state, priority, branch, and dependencies.

Keep this file lightweight. Use it when a task needs more context than fits
cleanly in one CSV row, but does not deserve a full plan.

---

# task-011 - Audit Accidental Execute Bits

**Front:** `repo-hygiene`
**Priority:** `P2`
**Status:** `todo`
**Branch:** `nexus`

## Problem

While inspecting the `sys/msdos/` tree in Atom, several source files (`.c`,
`.h`) appeared in yellow/orange text in the file tree pane.

This was not Git modification highlighting. The files had the Unix executable
bit set:

```text
-rwxr-xr-x font.c
-rwxr-xr-x font.h
```

Atom, likely via `file-icons` or theme integration, visually distinguishes
executable files in the tree view.

## Why It Matters

Accidental execute bits on source files are harmless at runtime, but they are:

- visually noisy in Atom
- semantically incorrect for source files
- able to pollute Git mode-bit diffs on systems that preserve permissions

## Detection

Find executable C/H files:

```sh
find sys -type f \( -name "*.c" -o -name "*.h" \) -executable
```

Find all executable files for review:

```sh
find . -type f -executable
```

## Candidate Fix

Remove execute bits from source files that are not actual scripts/tools:

```sh
find sys -type f \( -name "*.c" -o -name "*.h" \) -exec chmod -x {} \;
```

Leave execute permission only on actual scripts/tools.

If Git repeatedly reports mode-bit changes on a filesystem that does not
preserve permissions consistently:

```sh
git config core.fileMode false
```

Prefer fixing incorrect permissions in the repo first before disabling mode
tracking globally.

## Done Means

- executable source files have been audited
- accidental execute bits have been removed where appropriate
- legitimate executable scripts/tools remain executable
- any filesystem limitation is documented before changing `core.fileMode`

---

# task-012 - Fix Windows Console Tofu Boxes

**Front:** `configuration-procedures`
**Priority:** `P1`
**Status:** `todo`
**Branch:** `work/0003-configuration-procedures`

## Problem

The dedicated Nexus Windows Console Host setup currently shows tofu boxes for
some glyphs. A tofu box means the active font or renderer could not find a
visible glyph for a character NetHack tried to display.

This is separate from the 80x25 fullscreen geometry problem, but both affect
the same player-facing terminal setup.

## Likely Causes

- The selected VGA-style font does not include every character produced by the
  chosen NetHack symbol set.
- Windows Console Host is not falling back to a broader font for missing
  glyphs.
- The NetHack symbol set uses characters or escape behavior that does not match
  the selected font and console host.
- The current runtime options may be asking for DEC/IBM graphics while the
  terminal/font combination expects a different representation.

## Candidate Fixes To Test

Test these without changing Windows configuration from automation:

- Try `symset:IBMGraphics_2` with the selected VGA font.
- Try `symset:DECgraphics` with the selected VGA font.
- Try a different VGA-style font that has better CP437/line-drawing coverage.
- If Unicode glyphs are involved, test a font with broader Unicode fallback;
  this may trade away the VGA look.
- Confirm whether the tofu boxes appear in the map, menus, status line, or
  message text; the affected window narrows down whether this is a symbol set,
  font, or terminal behavior problem.

## Detection

Record:

- Windows Console Host font name and size
- console buffer size and window size
- Nexus runtime options related to symbols and tty display
- which characters appear as tofu boxes
- whether the same symbols render correctly in a normal WSL terminal

## Done Means

- the tofu-producing glyphs are identified
- the relevant font, console, and NetHack symbol settings are recorded
- `_work/nexus-player-guide.md` describes a working glyph setup
- the Nexus task list does not refer to notes outside this repository
