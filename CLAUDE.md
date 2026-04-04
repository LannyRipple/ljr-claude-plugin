# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a Claude Code plugin — a collection of skills (slash commands) that extend Claude Code behavior. There is no build system, test suite, or compiled code. All artifacts are Markdown files.

## Structure

```
skills/
  <skill-name>/
    SKILL.md          # Skill definition (frontmatter + instructions)
    references/       # Files that SKILL.md delegates to via @filename or explicit read instructions
    assets/           # Templates and static files used at runtime
```

A skill is invoked as `/<skill-name>` in Claude Code. The `name` field in SKILL.md frontmatter must match the directory name exactly — a mismatch is a bug.

## Skills in This Repo

- **radar** — Personal assistant named after Radar O'Reilly. Maintains a persistent memory file at `~/tmp/radar-memory.md`. Triggered by addressing "Radar" by name or by note/todo requests directed at it.
- **skill-review** — Reviews and improves SKILL.md files using four lenses: clarity, flow, direction, bug. Produces a review document before applying any edits.
- **using-tmux** — Provides patterns for writing output to tmux display panes. Contains workflows for billboard (append-only), persistent billboard (file-backed), and show-and-go (one-shot) display modes.

## Skill Authoring Conventions

- `SKILL.md` frontmatter fields: `name` (matches dir), `description` (trigger conditions + what it does)
- Instructions in `references/` files are read at runtime by Claude following the skill's routing logic — they are not loaded automatically
- `assets/` holds templates and static content the skill copies or reads at runtime
- Skills should use `dangerouslyDisableSandbox: true` on any Bash call that needs tmux socket access, clipboard (`pbcopy`), or browser (`open`)
- Requirement Levels preamble (MUST/SHOULD vocabulary) belongs in skills with security, high blast-radius, or irreversible actions

## Installing / Deploying

Skills in this repo are intended to be installed into `~/.claude/skills/` so Claude Code can load them. Subagents spawned by Claude cannot write to `~/.claude/skills/` — that path is outside the sandbox write allowlist. The main Claude agent must perform those writes.
