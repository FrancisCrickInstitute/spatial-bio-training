# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

The canonical project guide is `AGENTS.md`: the workshop plan, decisions, target layout, order of work and open questions. It is imported here so it stays the single source of truth. Update `AGENTS.md`, not this file, when project facts change.

@AGENTS.md

## Quick orientation

- **This is a training-workshop repo, not a software package.** There is no build, no tests and no CI. Day 2 material will be Jupyter notebooks, and nothing here is meant to be imported.
- **The CellSurvey pipeline code is gone from this repo.** Don't restore it. Point to upstream [CellSurvey](https://github.com/FrancisCrickInstitute/CellSurvey) instead. An `upstream` git remote (SSH) may be configured for fetching it.
- **Until step 2 lands, the pixi environment is stale.** `pixi.toml` still describes CellSurvey's Stardist/TensorFlow environment.
- **Keep participant-facing text and the plan in step**: the programme in `README.md` mirrors the table in `AGENTS.md`.
