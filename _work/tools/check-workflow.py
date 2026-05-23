#!/usr/bin/env python3
"""Lightweight Nexus workflow dashboard checks."""

from __future__ import annotations

import argparse
import csv
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path


PLAN_HEADERS = ["id", "status", "priority", "branch", "notes"]
TASK_HEADERS = ["id", "status", "front", "priority", "branch", "depends_on", "notes"]

PLAN_STATUSES = {"todo", "doing", "done", "dropped", "parked"}
TASK_STATUSES = {"todo", "ready", "doing", "review", "blocked", "done", "dropped", "parked"}
PRIORITIES = {"P0", "P1", "P2", "P3"}
TERMINAL_PLAN_STATUSES = {"done", "dropped"}
TERMINAL_TASK_STATUSES = {"done", "dropped", "parked"}


@dataclass(frozen=True)
class Row:
    path: Path
    line: int
    data: dict[str, str]

    @property
    def id(self) -> str:
        return self.data.get("id", "")


@dataclass
class Finding:
    path: Path
    line: int
    severity: str
    code: str
    message: str


def plan_slug(plan_id: str) -> str:
    parts = plan_id.split("-", 1)
    return parts[1] if len(parts) == 2 and parts[0].isdigit() else plan_id


def load_csv(path: Path, expected_headers: list[str], findings: list[Finding]) -> list[Row]:
    try:
        with path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames or []
            if headers != expected_headers:
                findings.append(
                    Finding(
                        path,
                        1,
                        "error",
                        "bad-header",
                        f"expected header {','.join(expected_headers)}; found {','.join(headers)}",
                    )
                )
                return []
            return [
                Row(path=path, line=line, data={k: (v or "").strip() for k, v in row.items()})
                for line, row in enumerate(reader, start=2)
            ]
    except FileNotFoundError:
        findings.append(Finding(path, 1, "error", "missing-file", "required dashboard is missing"))
        return []


def add(finding_list: list[Finding], row: Row, severity: str, code: str, message: str) -> None:
    finding_list.append(Finding(row.path, row.line, severity, code, message))


def check_ids(rows: list[Row], kind: str, findings: list[Finding]) -> None:
    seen: dict[str, Row] = {}
    for row in rows:
        if not row.id:
            add(findings, row, "error", "missing-id", f"{kind} row has blank id")
        elif row.id in seen:
            add(findings, row, "error", "duplicate-id", f"{kind} id {row.id!r} duplicates line {seen[row.id].line}")
        else:
            seen[row.id] = row


def resolve_front(front: str, plan_by_id: dict[str, Row]) -> str | None:
    if front in plan_by_id:
        return front

    slug_matches = [plan_id for plan_id in plan_by_id if plan_slug(plan_id) == front]
    if len(slug_matches) == 1:
        return slug_matches[0]

    prefix_matches = [plan_id for plan_id in plan_by_id if plan_slug(plan_id).startswith(front)]
    if len(prefix_matches) == 1:
        return prefix_matches[0]

    return None


def check_plan_files(plan_rows: list[Row], plans_dir: Path, findings: list[Finding]) -> None:
    plan_ids = {row.id for row in plan_rows if row.id}
    for row in plan_rows:
        if row.id and not (plans_dir / f"{row.id}.md").exists():
            add(findings, row, "error", "missing-plan-file", f"plan {row.id!r} has no _work/plans/{row.id}.md")

    for path in sorted(plans_dir.glob("[0-9][0-9][0-9][0-9]-*.md")):
        plan_id = path.stem
        if plan_id not in plan_ids:
            findings.append(
                Finding(
                    path,
                    1,
                    "error",
                    "unlisted-plan-file",
                    f"plan file {path} is not listed in _work/plans/plans.csv",
                )
            )


def check_dependencies(task_rows: list[Row], task_by_id: dict[str, Row], findings: list[Finding]) -> None:
    graph: dict[str, list[str]] = {}
    for row in task_rows:
        raw = row.data.get("depends_on", "")
        deps = [dep.strip() for dep in raw.split("|") if dep.strip()]
        graph[row.id] = deps
        if raw and not deps:
            add(findings, row, "error", "bad-dependency", f"task {row.id!r} has malformed dependencies")
        if len(deps) != len(set(deps)):
            add(findings, row, "error", "duplicate-dependency", f"task {row.id!r} repeats a dependency")
        for dep in deps:
            if dep == row.id:
                add(findings, row, "error", "self-dependency", f"task {row.id!r} depends on itself")
            elif dep not in task_by_id:
                add(findings, row, "error", "missing-dependency", f"task {row.id!r} depends on unknown task {dep!r}")

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(task_id: str, stack: list[str]) -> None:
        if task_id in visited:
            return
        if task_id in visiting:
            cycle = stack[stack.index(task_id) :] + [task_id]
            row = task_by_id[task_id]
            add(findings, row, "error", "dependency-cycle", "dependency cycle: " + " -> ".join(cycle))
            return
        visiting.add(task_id)
        for dep in graph.get(task_id, []):
            if dep in task_by_id:
                visit(dep, stack + [dep])
        visiting.remove(task_id)
        visited.add(task_id)

    for task_id in graph:
        visit(task_id, [task_id])


def check_dashboards(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    plans_path = root / "_work/plans/plans.csv"
    tasks_path = root / "_work/tasks.csv"
    plans_dir = root / "_work/plans"

    plan_rows = load_csv(plans_path, PLAN_HEADERS, findings)
    task_rows = load_csv(tasks_path, TASK_HEADERS, findings)
    check_ids(plan_rows, "plan", findings)
    check_ids(task_rows, "task", findings)

    plan_by_id = {row.id: row for row in plan_rows if row.id}
    task_by_id = {row.id: row for row in task_rows if row.id}
    tasks_by_plan: dict[str, list[Row]] = defaultdict(list)

    for row in plan_rows:
        status = row.data.get("status", "")
        priority = row.data.get("priority", "")
        if status not in PLAN_STATUSES:
            add(findings, row, "error", "bad-status", f"plan {row.id!r} has invalid status {status!r}")
        if priority not in PRIORITIES:
            add(findings, row, "error", "bad-priority", f"plan {row.id!r} has invalid priority {priority!r}")
        if priority == "P0" and status != "doing":
            add(findings, row, "error", "p0-inactive", f"plan {row.id!r} uses P0 but is not doing")
        if status == "parked" and priority in {"P0", "P1"}:
            add(findings, row, "error", "parked-priority", f"parked plan {row.id!r} uses active priority {priority}")

    for row in task_rows:
        status = row.data.get("status", "")
        priority = row.data.get("priority", "")
        branch = row.data.get("branch", "")
        front = row.data.get("front", "")
        if status not in TASK_STATUSES:
            add(findings, row, "error", "bad-status", f"task {row.id!r} has invalid status {status!r}")
        if priority not in PRIORITIES:
            add(findings, row, "error", "bad-priority", f"task {row.id!r} has invalid priority {priority!r}")
        if status == "parked" and priority in {"P0", "P1"}:
            add(findings, row, "error", "parked-priority", f"parked task {row.id!r} uses active priority {priority}")

        plan_id = resolve_front(front, plan_by_id)
        if plan_id is None:
            add(findings, row, "error", "unknown-front", f"task {row.id!r} front {front!r} does not match a plan")
            continue

        plan = plan_by_id[plan_id]
        tasks_by_plan[plan_id].append(row)
        plan_status = plan.data.get("status", "")
        plan_branch = plan.data.get("branch", "")

        if status == "doing" and plan_status != "doing":
            add(findings, row, "error", "active-in-inactive-plan", f"task {row.id!r} is doing under {plan_status} plan {plan_id!r}")
        if priority == "P0" and (status != "doing" or plan_status != "doing"):
            add(findings, row, "error", "p0-inactive", f"task {row.id!r} uses P0 outside active doing work")
        if plan_status in TERMINAL_PLAN_STATUSES and status not in TERMINAL_TASK_STATUSES:
            add(findings, row, "error", "open-task-in-terminal-plan", f"task {row.id!r} is {status} under {plan_status} plan {plan_id!r}")
        if status not in TERMINAL_TASK_STATUSES and branch != plan_branch:
            add(findings, row, "warning", "branch-drift", f"task {row.id!r} branch {branch!r} differs from plan {plan_id!r} branch {plan_branch!r}")

    for plan_id, plan in plan_by_id.items():
        if plan.data.get("status") == "done":
            unfinished = [task.id for task in tasks_by_plan.get(plan_id, []) if task.data.get("status") not in TERMINAL_TASK_STATUSES]
            if unfinished:
                add(findings, plan, "error", "done-plan-has-open-tasks", f"done plan {plan_id!r} has open tasks: {', '.join(unfinished)}")

    check_dependencies(task_rows, task_by_id, findings)
    check_plan_files(plan_rows, plans_dir, findings)
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="repository root")
    args = parser.parse_args()

    findings = check_dashboards(args.root)
    errors = [finding for finding in findings if finding.severity == "error"]
    warnings = [finding for finding in findings if finding.severity == "warning"]

    for finding in findings:
        rel = finding.path.relative_to(args.root) if finding.path.is_absolute() else finding.path
        print(f"{rel}:{finding.line}: workflow-{finding.severity}: {finding.code}: {finding.message}")

    print(f"workflow-check: {len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
