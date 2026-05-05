# skill-review

Reviews and improves Claude Code skills (SKILL.md files).

For a full understanding of this skill, read its files in
[ljr-claude-plugin/skills/skill-review](https://github.com/lripple/ljr-claude-plugin/tree/main/skills/skill-review).

---

## The Core Idea

Skill instructions are code — they can have bugs, ambiguities, and flow problems.
This skill reviews SKILL.md files through four lenses: **clarity** (can Claude follow
this without ambiguity?), **flow** (does information arrive before it's needed?),
**direction** (are required steps unmistakably required?), and **bug** (is the
instruction technically correct?).

For new skills, it runs a dual-agent review: your (author-biased) read plus an
independent sub-agent read, merged. The sub-agent's findings surface the gaps your
familiarity hides.

---

## Workflows

### Review an existing skill

```
/skill-review
"review skills/radar/SKILL.md"
"audit this skill for issues"
"find bugs in my notify-me skill"
```

Produces a review document grouped by file, each issue labeled and with a concrete
proposed fix. No changes are applied until you confirm.

### Create or update a skill

```
"create a new skill for X"
"turn this workflow into a skill"
"update the skill-review skill to add Y"
```

Walks through gathering intent, drafts SKILL.md, iterates with you, then runs the
dual-agent review before finalizing.

---

## Things Worth Knowing

**Load this skill before working on other skills.** When building or reviewing a skill,
invoke `/skill-review` at the start of the session so the review criteria and workflow
are in context. Without it, Claude approximates the workflow from memory and misses
subtleties.

**The dual-agent review is the most valuable part.** The sub-agent has no knowledge of
how the skill was written. Its findings are exactly the gaps author familiarity hides.
Accept its issues seriously.

**MUST/SHOULD preamble is not for every skill.** Adding requirement-level vocabulary to
a low-stakes skill degrades the signal in skills that genuinely need it. The review
criteria spell out when the preamble is warranted (security, high blast radius,
irreversible actions).

**Plugin skills are read-only.** Skills installed from a marketplace can be reviewed but
not edited in place. Issues go to the plugin's source repo.
