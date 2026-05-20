# Nexus Work Area

Local planning notes, investigation logs, and task checklists for Nexus.

Keep source changes in the normal NetHack tree. Use this directory for context
that helps coordinate work without changing gameplay or engine behavior.

## Purpose

`_work/` is for development coordination only. It is not gameplay content, not
engine code, and not a source of truth for player-facing behavior.

Use it to answer:

- what are we doing next?
- what branch or dev front owns the work?
- what changed in a Codex session?
- what intentional upstream NetHack divergences have we introduced?

## Files

- `tasks.csv` tracks small executable tasks.
- `plans/plans.csv` tracks larger work fronts.
- `plans/*.md` stores context, constraints, and acceptance criteria for a plan.
- `codex-log.md` records concise session summaries when useful.
- `divergences.md` records intentional departures from upstream NetHack.
- `workflow.md` describes the working process.

## Rules

- Keep `nexus` as the integration branch.
- Do work on short branches when a change is more than a quick note.
- Record C changes and topology assumptions in `divergences.md`.
- Prefer data/topology changes before engine surgery.
- Keep this directory lightweight; revise the workflow when it becomes friction.
