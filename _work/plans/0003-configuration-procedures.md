# 0003 - Configuration And Procedures

## Goal

Establish the practical developer and player environment for Nexus, including
branch workflow, keyword-substitution rules, player terminal setup, runtime
configuration habits, and plan/task procedures.

This plan continues the setup work that became visible after
`0001-environment-setup` was committed. `0001` remains closed; this plan tracks
the still-active policy and configuration work.

## Scope

In scope:

- developer guide for branch workflow, upstream update workflow, and NetHack
  keyword substitution
- player guide for the intended Windows 10 plus WSL terminal environment
- guidance for separating development terminals from the dedicated NetHack tty
  console
- Nexus runtime configuration conventions, including what belongs in
  `sys/unix/nexus.nethackrc` versus personal player config
- plan/task workflow rules, including plan closure policy
- Codex/session instructions needed to preserve those rules

Out of scope:

- booting into the custom Nexus Lua level
- NetHack gameplay design
- procedural generation
- inspecting or changing the user's Windows configuration directly
- importing Floating Eye code or gameplay patches

## Acceptance Criteria

- `_work/nexus-dev-guide.md` explains normal feature branches, upstream release
  update branches, and keyword-aware commits
- `_work/nexus-player-guide.md` explains the target player terminal setup
  without depending on inspecting Windows configuration
- workflow instructions say plans cannot be closed without explicit user
  approval
- Windows console fullscreen setup has a documented working approach for
  preserving 80x25 geometry while making the visible font/cell size larger; the
  current fullscreen approximation changes geometry and is not acceptable
- Windows Console Host glyph rendering has a documented working approach for
  avoiding tofu boxes in the chosen NetHack symbol set and VGA-style font
- Nexus runtime configuration policy is documented clearly enough to decide
  whether a setting belongs in the repo baseline or in a personal player rc
- any intentional upstream divergence discovered during this plan is recorded
  in `_work/divergences.md`

## Status

Todo.
