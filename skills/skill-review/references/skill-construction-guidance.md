# Skill Construction Guidance

> **Source:** This guidance is extracted from the `skill-creator` skill, located at
> `~/.claude/plugins/cache/claude-plugins-official/skill-creator/unknown/skills/skill-creator/SKILL.md`.
> If asked to check for updates to this guidance, read that file and compare.

Use this guidance when drafting or updating skill files.

---

## Anatomy of a Skill

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter (name, description required)
│   └── Markdown instructions
└── Bundled Resources (optional)
    ├── scripts/    - Executable code for deterministic/repetitive tasks
    ├── references/ - Docs loaded into context as needed
    └── assets/     - Files used in output (templates, icons, fonts)
```

## Progressive Disclosure

Skills use a three-level loading system:

1. **Metadata** (name + description) — Always in context (~100 words)
2. **SKILL.md body** — In context whenever the skill triggers (<500 lines ideal)
3. **Bundled resources** — Loaded as needed (unlimited; scripts can execute without loading)

Key patterns:
- Keep SKILL.md under 500 lines. If you're approaching this limit, add another layer of
  hierarchy with clear pointers about where to go next.
- Reference files clearly from SKILL.md with guidance on when to read them.
- For large reference files (>300 lines), include a table of contents.

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

## Frontmatter

- **name**: Skill identifier (must match the directory name — this is the slug for `/name` invocation)
- **description**: The primary triggering mechanism. Cover both what the skill does AND
  the specific contexts for when to use it. All "when to use" info belongs here, not in
  the body. Make descriptions slightly "pushy" — Claude tends to undertrigger skills, so
  instead of "How to build a dashboard", write "How to build a dashboard. Use this skill
  whenever the user mentions dashboards, data visualization, or wants to display any kind
  of data, even if they don't explicitly ask for a 'dashboard'."

## Writing Patterns

Use the imperative form for instructions.

The pattern below shows a common form found in existing skills — note that the Writing Style section below cautions against overusing all-caps imperatives.

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

## Writing Style

- Explain *why* things are important rather than relying on heavy-handed MUSTs. Use theory
  of mind and keep instructions general rather than narrowly tied to specific examples.
- If you find yourself writing ALWAYS or NEVER in all caps, or using rigid structures,
  that's a yellow flag — reframe and explain the reasoning so Claude understands why the
  requirement exists. That's a more effective approach than repetition or emphasis alone.
- Keep the prompt lean. Remove things that aren't pulling their weight.
- Draft first, then read with fresh eyes and improve.

## Principle of Lack of Surprise

Skills must not contain malware, exploit code, or any content that could compromise
system security. A skill's contents should not surprise the user given its described
intent. Do not create misleading skills or skills designed to facilitate unauthorized
access, data exfiltration, or other malicious activities.

## How Skill Triggering Works

Skills appear in Claude's `available_skills` list with their name and description. Claude
decides whether to consult a skill based on that description. Claude only consults skills
for tasks it cannot easily handle on its own — simple, one-step queries may not trigger a
skill even if the description matches, because Claude can handle them directly with basic
tools. Complex, multi-step, or specialized queries reliably trigger skills when the
description matches.

