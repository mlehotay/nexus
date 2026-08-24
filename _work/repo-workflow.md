# FLEY Repository Workflow

This document defines the common operational workflow for Floating Eye Software
(FLEY) execution repositories.

It establishes the shared engineering execution model used across FLEY projects
while remaining independent of any particular programming language, framework,
or regulatory domain.

Repository workflows provide a stable operational foundation for engineering
work. Higher-level organizational governance, including the FLEY Quality
Management System (QMS), builds upon this foundation rather than replacing it.

This workflow is intentionally technology-neutral. It defines common engineering
behavior rather than prescribing particular programming languages, build
systems, test runners, or development tools.

---

# Purpose

The repository workflow provides a common way to organize engineering work
across FLEY repositories.

It governs:

* planning and execution within a repository;
* repository-local work tracking;
* engineering documentation;
* engineering verification activities;
* coordination between repositories;
* contributor expectations;
* session management for human and AI contributors.

The workflow intentionally focuses on engineering execution.

It does not define:

* organizational strategy;
* Management Review;
* controlled document approval;
* Design Control;
* CAPA;
* formal verification or validation;
* other QMS-governed activities.

Those responsibilities belong to higher governance layers.

The repository workflow should remain stable even as repository technologies,
organizational structure, and QMS processes evolve.

---

# Capabilities and Obligations

The FLEY architecture intentionally separates **engineering capability** from
**governance obligations**.

Repository workflows define reusable engineering capabilities.

Governance processes determine when those capabilities must be exercised, what
additional controls apply, and what evidence must be retained.

Repository workflows answer:

> How is engineering work performed?

The QMS answers:

> Which engineering activities are required, reviewed, approved, recorded, and
> retained?

This distinction allows engineering practice to remain stable while governance
requirements scale according to organizational, contractual, or regulatory
needs.

For example:

| Repository Capability  | Governance Responsibility                                            |
| ---------------------- | -------------------------------------------------------------------- |
| `make test`            | determine whether execution constitutes formal verification evidence |
| Pull Request           | determine approval requirements                                      |
| Git tag                | determine whether it represents an approved release baseline         |
| Markdown documentation | determine whether the document is controlled                         |
| Repository plans       | determine whether they satisfy Quality Planning activities           |
| Repository tasks       | determine whether they satisfy controlled planning activities        |
| Risk records           | determine whether they become controlled organizational risks        |

**Capabilities belong to engineering. Obligations belong to governance.**

Governance should compose existing engineering capabilities rather than
duplicating or replacing them.

---

# Relationship to the FLEY QMS

The repository workflow forms the operational execution layer of the FLEY
architecture.

Repository execution continuously produces engineering outputs, including:

* source code;
* documentation;
* engineering tests;
* design discussions;
* implementation plans;
* repository tasks;
* repository status information.

Higher-level governance processes may consume these outputs.

For example:

* Design Control may designate repository tests as formal verification
  activities.
* Document Control may designate selected Markdown files as controlled
  documents.
* Management Review may use repository status information as organizational
  input.
* Quality Planning may reference repository plans.
* Risk Management may promote repository observations into controlled risk
  records.

Repository workflows intentionally define stable engineering interfaces that
higher-level governance may invoke. Examples include repository test commands,
planning artifacts, pull requests, engineering documentation, release
procedures, and status reports.

Higher-level governance should reference these interfaces rather than redefine
repository execution.

The repository workflow therefore provides engineering capabilities.

The QMS imposes governance obligations.

Neither replaces the other.

---

# Relationship to Organizational Governance

This workflow is paired with:

`fley-org/process/org-process.md`

which governs organization-level reconciliation, cross-repository routing,
organizational wrap-up, and enterprise coordination.

Repository workflows own engineering execution.

Organization workflows own organizational coordination.

The QMS owns controlled governance processes.

Together they form a layered architecture:

```text
Engineering Execution
        ↓
Organizational Coordination
        ↓
Governance
```

Each layer builds upon the previous one without replacing it.

---

# Work Surfaces

Repository work is organized around durable engineering artifacts.

Plans describe engineering work fronts.

Tasks describe concrete, verifiable engineering work that can be completed,
reviewed, and tracked independently.

Plans should be created when work involves:

* multiple implementation steps;
* uncertainty;
* dependencies;
* acceptance criteria;
* architectural decisions.

Tasks should describe executable engineering work.

Stable identifiers shall not be reused.

Repository dashboards remain authoritative for repository execution.

Plans and tasks track repository-owned work.

They do not replace organization registries or controlled QMS records.

Creating a plan, task, note, or other authoritative repository artifact
constitutes successful transfer of responsibility from conversation into the
repository.

Conversation history should not remain the authoritative engineering record.

Repository work surfaces should remain:

* durable;
* version controlled where practical;
* reviewable;
* independently understandable;
* suitable for future contributors.

---

# Repository Authority

Execution repositories own:

* engineering implementation;
* local planning;
* engineering tasks;
* engineering documentation;
* local testing;
* engineering acceptance criteria;
* repository architecture;
* repository-local risks;
* local release readiness.

Repository workflows intentionally avoid governing organization-wide concerns.

Those belong to their respective authoritative processes.

---

# Organization Authority

Organization-level authority resides within `fley-org`.

Examples include:

* repository topology;
* portfolio management;
* publication registry;
* organizational coordination;
* enterprise initiatives.

Organization registries describe organizational state rather than executable
repository work.

---

# QMS Authority

Controlled governance resides within `fley-qms`.

Examples include:

* SOPs;
* Work Instructions;
* Design Control;
* Change Control;
* CAPA;
* Management Review;
* Document Control;
* Risk and Opportunity Management;
* Quality Planning.

These processes may reference repository artifacts while remaining
authoritative for governance decisions.

---

# Work Tracking

Plans and tasks remain repository-owned engineering artifacts.

Plans:

* describe engineering objectives;
* identify dependencies;
* define acceptance criteria;
* coordinate multi-step work.

Tasks:

* identify concrete executable engineering work;
* reference plans where applicable;
* record execution state;
* should be independently reviewable whenever practical.

Repository dashboards describe engineering execution only.

Higher-level governance may reference repository plans and tasks but should not
duplicate repository execution state.

---

# Quick Status

`_work/quick-status.md` provides a concise maintainer-oriented summary of the
repository's current operational state.

It summarizes engineering attention rather than organizational governance.

Quick status documents may summarize:

* active engineering work;
* repository health;
* important context;
* current priorities;
* notable blockers.

They are intentionally concise.

When disagreement exists between quick-status and authoritative dashboards,
update the quick-status document or the authoritative engineering surface as
appropriate.

Quick status is informative.

Plans, tasks, and registries remain authoritative.

---

# CSV Surface Types

CSV files used for coordination in Floating Eye repositories fall into two
governed categories.

## Workflow Dashboards

Workflow dashboards describe executable engineering work owned by the
repository.

Accepted dashboard labels include:

* `tasks`
* repository-specific task dashboards
* other engineering dashboards defined by the local workflow

Workflow dashboards:

* belong to the repository that owns the work;
* track execution state;
* do not replace organizational registries.

## Organization Registries

Organization registries belong to `fley-org`.

They describe organization-level state such as:

* repository topology;
* project lifecycle;
* portfolio membership;
* publication governance.

Registries should have:

* a documented schema;
* a clear authority boundary;
* sufficient evidence or notes to justify each record.

Registries do not track executable engineering work.

Repository engineering work belongs in repository plans and task dashboards.

Do not treat arbitrary CSV data files as governance artifacts merely because
they use CSV format.

Analysis datasets, exports, fixtures, and other engineering data remain
repository-local unless a documented workflow explicitly governs them.

---

# Plan Closure

Plans should remain open until:

* acceptance criteria are satisfied;
* verification is complete;
* residual follow-up work is identified;
* the user explicitly approves closure.

Plans requiring outcome review should include a Verification of Effectiveness
(VoE) section summarizing:

* objectives achieved;
* supporting evidence;
* residual risks;
* follow-up work;
* lessons learned.

Codex should identify plans that appear to satisfy their acceptance criteria.

Closure review should occur after verification but before marking a plan
`done`.

The closure prompt should summarize:

* the completed objectives;
* supporting evidence;
* residual risks;
* remaining follow-up work.

If the user confirms closure:

* update the plan status;
* update dashboard state;
* record the closure in the Codex log if applicable.

If the user does not approve closure, leave the plan open and record remaining
work as appropriate.

---

# Dashboard Schema

Repository dashboards provide the authoritative execution state for engineering
work.

## Plans

`_work/plans/plans.csv`

```csv
id,status,track,priority,depends_on,notes
```

## Tasks

`_work/tasks.csv`

```csv
id,status,plan,track,priority,depends_on,notes
```

Task notes that do not belong in the dashboard may be recorded in:

```text
_work/tasks.md
```

---

## Status Values

Supported workflow states are:

* `todo`
* `ready`
* `doing`
* `review`
* `blocked`
* `parked`
* `done`
* `dropped`

Definitions:

* **todo** — work exists but has not yet been evaluated for execution.
* **ready** — all declared dependencies are complete and the work may begin.
* **doing** — engineering work is actively underway.
* **review** — implementation is complete and awaiting review or verification.
* **blocked** — execution cannot continue because a dependency or external
  condition remains unresolved.
* **parked** — intentionally deferred without cancellation.
* **done** — completed.
* **dropped** — intentionally abandoned.

Rows in `ready` must not have unfinished dependencies.

Rows in `blocked` should identify the dependency or external condition
preventing execution.

---

## Dependency Rules

Dependency relationships should form an acyclic graph.

Separate multiple dependencies using:

```text
|
```

Dependencies should identify engineering prerequisites rather than merely
describing preferred sequencing.

---

## Dashboard Consistency

Repository dashboards should remain internally consistent.

Validation should ensure:

* valid statuses;
* valid priorities;
* valid references;
* valid dependency syntax;
* acyclic dependency graphs;
* plans and associated plan files remain synchronized;
* active tasks reference existing plans where applicable;
* `ready` rows have no unfinished declared dependencies;
* `doing` and `review` rows have no unfinished declared dependencies;
* tasks attached to plans in `doing` should have a parent plan also in
  `doing`.

---

## Priority Values

Priority values are:

* `P0` — urgent or blocking.
* `P1` — milestone-critical.
* `P2` — useful soon.
* `P3` — later or housekeeping.

Repositories may define additional scheduling practices while preserving the
common priority vocabulary.

---

## Repository Validation

Repositories should provide narrow validation appropriate to their workflow.

Typical checks include:

```text
make check-plans
make check-tasks
make check-registries
```

Repository-specific validation commands may extend these checks while preserving
the common workflow semantics.

---

# Codex Sessions

Codex sessions should preserve repository integrity while minimizing unnecessary
changes.

The repository remains the authoritative engineering record.

Conversation is transient.

Repository artifacts are durable.

---

## Session Start

Before making changes:

* inspect `git status`;
* inspect relevant plans;
* inspect relevant tasks;
* inspect relevant repository documentation when needed;
* identify the intended files before editing;
* understand the current engineering state before proposing changes.

Unexpected repository state should be acknowledged before proceeding.

---

## During Execution

Engineering work should remain focused.

Codex should:

* keep changes narrowly scoped to the requested work;
* maintain plans and task dashboards when execution state changes;
* record durable engineering findings in repository artifacts;
* avoid unrelated modifications;
* preserve existing repository conventions whenever practical;
* prefer durable repository-local processes over ephemeral experiments in
  `/tmp` or other transient environments whenever practical;
* prefer reusable tests, scripts, fixtures, documentation, or `make` targets
  over one-off verification commands whenever practical;
* avoid introducing temporary engineering debt merely to complete a task;
* do not install software, modify the development environment, or make
  persistent environment changes unless explicitly requested by the user.

Repository-local engineering processes should generally be preferred over
session-specific workarounds.

---

## Verification

Where practical, verify engineering work before declaring completion.

Verification should use repository-owned engineering processes.

Prefer documented repository commands such as:

```text
make test
make lint
make check-plans
make check-tasks
```

or their documented repository equivalents.

When verification cannot be completed, clearly identify:

* what was verified;
* what was not verified;
* why verification could not be completed.

Repository testing remains governed by the repository testing process.

---

## Wrap-Up

Before concluding a session:

* update plans when objectives change;
* update task status when execution changes;
* record durable engineering notes where appropriate;
* identify remaining follow-up work;
* identify plans that may be ready for closure.

Wrap-up should leave the repository in a state that another contributor can
understand without relying upon conversation history.

---

## Plan Completion

When a plan appears complete:

* summarize completed objectives;
* summarize supporting evidence;
* summarize remaining follow-up work;
* identify residual risks if known;
* ask whether the user wishes to close the plan.

Codex should recommend plan closure when appropriate.

Codex should never close plans without explicit user approval.

---

## Repository State

Repository modifications should be intentional.

Avoid:

* partially updated dashboards;
* orphaned tasks;
* stale execution state;
* undocumented engineering changes;
* incomplete engineering notes when they materially affect future work.

Repository consistency is preferred over conversational convenience.

---

# Routing Boundaries

Routing selects the authoritative owner for engineering and governance
information.

Every durable artifact should have one authoritative owner.

Higher governance layers should reference repository artifacts rather than
duplicate them whenever practical.

---

## Execution Repositories

Execution repositories own:

* implementation;
* engineering plans;
* engineering tasks;
* repository documentation;
* engineering architecture;
* engineering testing;
* engineering verification;
* engineering release readiness;
* repository-local risks.

Execution repositories remain authoritative for engineering execution.

A workspace may reuse this workflow without joining the FLEY organizational
surface. When a top-level sibling workspace contains `.fleyignore`, broad FLEY
workspace discovery must treat it as outside the observation boundary: do not
inventory it, report its name or state, count it as drift, or route its work.
The marker does not prevent access by an explicitly targeted command; such
access requires separate authorization from the workspace owner.

---

## Organization

`fley-org` owns:

* organization topology;
* portfolio coordination;
* publication registries;
* organizational planning;
* organizational reconciliation;
* enterprise coordination;
* cross-repository governance.

Organization processes coordinate repositories.

They do not replace repository execution.

---

## Quality Management

`fley-qms` owns controlled governance including:

* SOPs;
* Work Instructions;
* Design Control;
* Change Control;
* CAPA;
* Management Review;
* Document Control;
* Risk and Opportunity Management;
* Quality Planning;
* controlled records.

The QMS should impose governance obligations upon engineering activities rather
than redefine repository engineering processes.

---

## Authority Principle

Repository execution should remain authoritative for engineering work.

Organization workflows should remain authoritative for organizational
coordination.

The QMS should remain authoritative for controlled governance.

Engineering capability should exist independently of governance obligations.

Higher governance layers should compose engineering capabilities rather than
replace them.

---

## Layered Architecture

The FLEY workflow intentionally separates engineering execution,
organizational coordination, and governance.

```text
Engineering Execution
        ↓
Operational Telemetry
        ↓
Organizational Coordination
        ↓
Management Review
        ↓
Governance Decisions
        ↓
Engineering Execution
```

Engineering work continuously informs governance.

Governance continuously improves engineering.

Neither layer duplicates the responsibilities of another.

---

# Guiding Principles

Repository workflows should be:

* durable;
* repeatable;
* deterministic where practical;
* reviewable;
* repository-owned;
* technology-neutral;
* automation-friendly;
* minimally prescriptive;
* suitable for long-term maintenance.

Engineering knowledge should accumulate in repository artifacts rather than
conversation history whenever practical.

Repository workflows define engineering capability.

Governance defines engineering obligations.

Capabilities belong to engineering.

Obligations belong to governance.
