# Skill Construction Guidance

> **Source:** This guidance is extracted from the `skill-creator` skill, located at
> `~/.claude/plugins/cache/claude-plugins-official/skill-creator/unknown/skills/skill-creator/SKILL.md`.
> If asked to check for updates to this guidance, read that file and compare.

Use this guidance when drafting or updating skill files.

For the canonical reference on file structure, frontmatter field schema, bundled resource
directories, the three-level loading system, and `@filename` import syntax, see the
official Claude Code documentation:

- [Skills guide](https://docs.anthropic.com/en/docs/claude-code/skills)
- [Plugins reference](https://docs.anthropic.com/en/docs/claude-code/plugins-reference)

This document covers the opinionated patterns and decisions the official docs leave open.

---

## Referencing Shared Plugin Resources

When a skill needs to reference a file that is shared across multiple skills — such as a
top-level `references/` file or a `scripts/` utility — do not copy that file into each
skill's directory. Instead, use the `${CLAUDE_PLUGIN_ROOT}` variable.

`${CLAUDE_PLUGIN_ROOT}` expands to the plugin's installation directory at runtime and is
substituted inline anywhere it appears in skill content. Because the plugin is copied to
a cache directory on install, only paths within the plugin root are guaranteed to resolve.

**When to use it:**
- A shared reference document lives at the plugin root (e.g., `references/style-guide.md`)
- A script or tool in the plugin's `scripts/` or `bin/` directory is called from multiple skills

**Example — reading a shared reference file:**
```
Read the style guide at `${CLAUDE_PLUGIN_ROOT}/references/style-guide.md` before drafting output.
```

**Example — invoking a shared script:**
```bash
${CLAUDE_PLUGIN_ROOT}/scripts/validate.sh "$1"
```

Do not use `${CLAUDE_PLUGIN_ROOT}` for files that belong to only one skill — those should
live in that skill's own directory and be referenced with a relative path or `@filename` syntax.

---

## Writing Effective Descriptions

`description` is the primary triggering mechanism — Claude decides whether to load this
skill based on description alone.

**Make descriptions slightly pushy.** Claude tends to undertrigger skills. Instead of
"How to build a dashboard", write "Use this skill whenever the user mentions dashboards,
data visualization, or wants to display any kind of data, even if they don't explicitly
ask for a 'dashboard'."

**Front-load the use case.** The description has a ~250 character soft limit for trigger
matching. Put the key trigger phrase first.

All "when to use" information belongs in the description, not the body.

---

## Progressive Disclosure: Organization Patterns

The three-level loading system is documented officially. This section covers how to
organize within it.

**Keep SKILL.md under 500 lines.** If approaching this limit, move detailed content to
`references/` files with clear pointers about when to read them. For large reference files
(>300 lines), include a table of contents.

**Domain organization** — When a skill supports multiple domains or frameworks, organize
by variant so Claude reads only what's relevant:

```
cloud-deploy/
├── SKILL.md (workflow + selection logic)
└── references/
    ├── aws.md
    ├── gcp.md
    └── azure.md
```

---

## Writing Patterns

Use the imperative form for instructions.

**Defining output formats:**
```markdown
## Report structure
ALWAYS use this exact template:
# [Title]
## Executive summary
## Key findings
## Recommendations
```

**Examples pattern:**
```markdown
## Commit message format
**Example 1:**
Input: Added user authentication with JWT tokens
Output: feat(auth): implement JWT-based authentication
```

---

## Writing Style

- Explain *why* things are important rather than relying on heavy-handed MUSTs. Use theory
  of mind and keep instructions general rather than narrowly tied to specific examples.
- If you find yourself writing ALWAYS or NEVER in all caps, or using rigid structures,
  that's a yellow flag — reframe and explain the reasoning so Claude understands why the
  requirement exists. That's a more effective approach than repetition or emphasis alone.
- Keep the prompt lean. Remove things that aren't pulling their weight.
- Draft first, then read with fresh eyes and improve.

---

## Principle of Lack of Surprise

Skills must not contain malware, exploit code, or any content that could compromise
system security. A skill's contents should not surprise the user given its described
intent. Do not create misleading skills or skills designed to facilitate unauthorized
access, data exfiltration, or other malicious activities.

---

## How Skill Triggering Works

Skills appear in Claude's `available_skills` list with their name and description. Claude
consults skills for tasks it cannot easily handle on its own — simple, one-step queries
may not trigger a skill even if the description matches, because Claude can handle them
directly. Complex, multi-step, or specialized queries reliably trigger skills when the
description matches.

The implication: descriptions need to signal complexity, not just topic. "Build a
dashboard" is weaker than "Build a dashboard — use this skill, which includes template
selection, data binding patterns, and layout guidance."
