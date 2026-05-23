# Nexus workflow checks. This file is not part of the NetHack build.

NEXUS_REF ?= nexus
UPSTREAM ?= upstream/NetHack-5.0
PY ?= python3
GIT := git --no-pager
BASE := $(shell git merge-base $(NEXUS_REF) $(UPSTREAM))

.PHONY: help base diff diff-full diff-stat touched workflow-check check audit

help:
	@printf '%s\n' 'Nexus workflow targets:'
	@printf '%s\n' '  base         show the current upstream merge base'
	@printf '%s\n' '  diff         list files currently different from upstream'
	@printf '%s\n' '  diff-stat    show current diff stat from upstream'
	@printf '%s\n' '  diff-full    show the full current diff from upstream'
	@printf '%s\n' '  touched      list files touched by Nexus-only commits'
	@printf '%s\n' '  workflow-check  check plans.csv and tasks.csv for workflow drift'
	@printf '%s\n' '  check        alias for workflow-check'
	@printf '%s\n' '  audit        run base, diff-stat, and diff'
	@printf '%s\n' ''
	@printf '%s\n' 'Variables:'
	@printf '%s\n' '  NEXUS_REF=nexus'
	@printf '%s\n' '  UPSTREAM=upstream/NetHack-5.0'
	@printf '%s\n' '  PY=python3'

base:
	@$(GIT) merge-base $(NEXUS_REF) $(UPSTREAM)

diff:
	$(GIT) diff --name-only $(BASE)..$(NEXUS_REF)

diff-stat:
	$(GIT) diff --stat $(BASE)..$(NEXUS_REF)

diff-full:
	$(GIT) diff $(BASE)..$(NEXUS_REF)

touched:
	$(GIT) log --no-merges --name-only --format= $(UPSTREAM)..$(NEXUS_REF) | sort -u

workflow-check:
	$(PY) _work/tools/check-workflow.py --root .

check: workflow-check

audit: base diff-stat diff
