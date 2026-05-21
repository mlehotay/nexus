# Nexus Player Guide

This guide describes the intended terminal setup for playing Nexus/NetHack on Windows 10 with WSL.

The goal is:

- tty gameplay
- IBM VGA-style presentation
- fixed 80x25 geometry
- modern WSL runtime
- minimal terminal interference

---

# Design

Use two separate terminal environments:

| Purpose | Environment |
|---|---|
| Development | Large modern Ubuntu shell |
| Nexus/NetHack | Fixed 80x25 VGA console |

Do not try to make one profile serve both purposes.

---

# Architecture

Important distinction:

| Component | Purpose |
|---|---|
| `wsl.exe` | launches Linux |
| `bash` | Linux shell |
| `conhost.exe` | terminal renderer/window |

The important requirement is:

```text id="4r55q7"
terminal host = Windows Console Host
````

NOT:

```text id="xxqg3x"
shell = cmd.exe
```

WSL already runs correctly inside conhost on this machine.

Do NOT enable:

```text id="dzf5s2"
Use legacy console
```

Legacy console breaks modern WSL behavior.

---

# Actual Working Configuration

| Setting            | Value                                           |
| ------------------ | ----------------------------------------------- |
| Shortcut Name      | `Nexus`                                         |
| Target             | `C:\Windows\System32\wsl.exe -- bash -lc nexus` |
| Start In           | `C:\Windows\System32`                           |
| Font               | `Flexi IBM VGA False`                           |
| Font Size          | `28`                                            |
| Screen Buffer Size | `80x25`                                         |
| Window Size        | `80x25`                                         |
| Legacy Console     | Disabled                                        |

---

# Creating the Shortcut

Create manually:

```text id="chqx8v"
Right-click Desktop -> New -> Shortcut
```

Target:

```text id="u99n7z"
C:\Windows\System32\wsl.exe -- bash -lc nexus
```

Name:

```text id="yvq2w8"
Nexus
```

Launch once, then configure:

* font
* geometry
* QuickEdit disabled

Windows stores console settings per shortcut context.

---

# Fullscreen Notes

Use:

```text id="7qen0q"
Alt+Enter
```

to toggle fullscreen/maximized console mode.

Modern Windows no longer supports true VGA fullscreen hardware text modes, but conhost provides a close approximation.

Repeated fullscreen toggling may corrupt geometry and introduce scrollbars. If this happens:

* close the console
* relaunch cleanly

Avoid repeatedly toggling modes during play.

---

# NetHack Configuration

After terminal setup is stable, configure gameplay options:

```text id="74q6u7"
OPTIONS=windowtype:tty
OPTIONS=symset:DECGraphics
OPTIONS=msg_window:combination
OPTIONS=number_pad:0
OPTIONS=showrace,lit_corridor,boulder:0
OPTIONS=hitpointbar,time
```

---

# Intended Result

The final environment should feel like:

* classic DOS tty NetHack
* fixed VGA console
* modern Linux backend
* separate from the normal development shell
