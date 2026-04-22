# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a Claude Code plugin — a collection of skills (slash commands) that extend Claude Code behavior. There is no build system, test suite, or compiled code. All artifacts are Markdown files.

## Structure

```
skills/
  {SKILL_NAME}/
    SKILL.md          # Skill definition (frontmatter + instructions)
    references/       # Files that SKILL.md delegates to via @filename or explicit read instructions
    assets/           # Templates and static files used at runtime
```

A skill is invoked as `/{SKILL_NAME}` in Claude Code. The `name` field in SKILL.md frontmatter must match the directory name exactly — a mismatch is a bug.

## Skills in This Repo

- **radar** — Personal assistant named after Radar O'Reilly. Maintains a persistent memory file at `~/tmp/radar-memory.md`. Triggered by addressing "Radar" by name or by note/todo requests directed at it.
- **skill-review** — Reviews and improves SKILL.md files using four lenses: clarity, flow, direction, bug. Produces a review document before applying any edits.
- **using-tmux** — Provides patterns for writing output to tmux display panes. Contains workflows for billboard (append-only), persistent billboard (file-backed), and show-and-go (one-shot) display modes.

## Skill Authoring Conventions

- Use `{VARIABLE_NAME}` (curly braces, uppercase) for placeholder variables in skill instructions — not `<variable-name>` angle-bracket style.
- `SKILL.md` frontmatter fields: `name` (matches dir), `description` (trigger conditions + what it does)
- Instructions in `references/` files are read at runtime by Claude following the skill's routing logic — they are not loaded automatically
- `assets/` holds templates and static content the skill copies or reads at runtime
- Skills should use `dangerouslyDisableSandbox: true` on any Bash call that needs tmux socket access, clipboard (`pbcopy`), or browser (`open`)
- Requirement Levels preamble (MUST/SHOULD vocabulary) belongs in skills with security, high blast-radius, or irreversible actions

## Installing / Deploying

This repo is distributed as a Claude Code marketplace plugin. Skills are installed and
updated through the plugin system — **do not copy files directly into `~/.claude/skills/`**.

To deploy a change:
1. Edit skills in `./skills/`
2. Bump the version: `scripts/bump-version.sh` (default: patch). Do NOT edit `plugin.json` by hand — the script has a double-bump guard.
3. Commit and push to GitHub
4. Restart the Claude Code session — it will auto-update from the marketplace on startup

## Useful Information and Gotchas

- **This is a plugin repo.** Skills are loaded via the marketplace, not by direct file
  installation. Changes only take effect after a push to GitHub followed by a session
  restart that triggers a marketplace refresh.

- **Subagents cannot write to `~/.claude/skills/`** — that path is outside the sandbox
  write allowlist. Even if you wanted to deploy directly, the main Claude agent would have
  to do the write. Don't bother: use the push-and-restart flow above.

- **Version bump is required on every release.** `.claude-plugin/plugin.json` is the
  authoritative version source. Bump it before committing or the marketplace may not
  detect the update.

- **This is a personal repo — no GUS work ID is needed in commit messages.** The standard
  Salesforce commit subject format (`@{GUS_Work_ID} ...`) does not apply here. Write
  plain commit messages.

## Coordination — Twining Lifecycle Gates

IMPORTANT: These gates are BLOCKING REQUIREMENTS for every task involving code exploration, modification, or architectural decisions.

### Gate 1: Context Assembly (BEFORE any work)
- MUST call `twining_assemble` with task description and narrowest scope BEFORE reading code or making changes
- MUST call `twining_why` on files you intend to modify
- NEVER start working without these calls — skipping creates blind decisions that conflict with existing work

### Gate 2: Record (BEFORE committing or ending)
- MUST call `twining_record` before every `git commit` or session end — hooks enforce this
- Include what you did (summary) and any choices you made (decisions array)
- Write decisions as natural sentences: "Chose X over Y — reason"
- For findings/warnings during work, use `twining_post` directly

### Housekeeping
- Run `twining_housekeeping({})` at the start of long sessions to check for stale state — preview is safe, execute only if needed

### Critical Rules
- Use narrowest scope: `src/auth/` not `project`
- NEVER skip Gate 1 — #1 cause of wasted work and conflicting decisions
- NEVER skip Gate 2 — hooks will block your commit and session exit until you record
