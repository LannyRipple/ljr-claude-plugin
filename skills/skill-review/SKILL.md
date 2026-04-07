---
name: skill-review
description: >-
  Reviews Claude Code skills and helps create or update them.

  **Workflow 1 — Review:** Trigger when the user asks to review, audit, improve, critique,
  or debug a skill; says "this skill isn't working right", "can you look at this skill",
  "help me improve my skill", or "find bugs in my skill"; or asks to "add requirement
  levels", "tighten this skill's language", or "this skill isn't following its instructions
  even though the language looks right". Also trigger when the user mentions a SKILL.md
  file and wants feedback on it.

  **Workflow 2 — Create or Update:** Trigger when the user asks to create a new skill,
  write a skill, turn a workflow into a skill, or update/restructure an existing skill's
  content or layout.
---

# Skill Review

## Before You Start

**Plugin skills are read-only.** Skills installed from a marketplace (typically under
`~/.claude/plugins/`) are owned by their plugin author, not the user — do not apply edits
to them. You can still read and review them and produce a review document. If issues are
found, tell the user and offer to help them find the plugin's repository or feedback channel
so they can submit the feedback to the author.

If the skill is under git control, check for a clean workspace (`git status`). If there
are uncommitted changes, surface that to the user and ask whether they want to stage or
commit before the review begins — the review will produce additional changes on top of
whatever is already modified, and they may want a clean checkpoint first. This is advisory:
if the user wants to proceed with a dirty state, that is fine — the review document they
approve before any edits are applied is their safety gate.

If the skill is not under git control, no additional preparation is needed — the review
document is the safety gate regardless of version control status.

---

## Requirement Levels

Terms in this skill use these levels:

- **MUST** / **MUST NOT** — No exceptions. Follow regardless of context.
- **SHOULD** / **SHOULD NOT** — Strong recommendation. Follow it unless you have a
  specific reason not to; note when you deviate and why.

Every MUST and SHOULD in this skill is paired with a rationale. Read the rationale before
deciding to deviate from a SHOULD — it describes what breaks when you skip it.

---

## Workflow Routing

| What the user wants | Workflow |
|---------------------|----------|
| Review, audit, critique, debug, improve an existing skill | Workflow 1 — Review |
| Create a new skill, write a skill, turn a workflow into a skill, update an existing skill's content or layout | Workflow 2 — Create or Update |

Any request to modify, edit, change, or update a skill's content — including targeted
single-step changes — SHOULD enter Workflow 2. Rationale: a bypassed review is the primary
source of undetected regressions. Bypass only when the change is purely cosmetic
(correcting a typo, fixing whitespace) with no risk of altering how Claude interprets or
executes the skill.

---

## Workflow 1 — Review

Your job is to review a Claude Code skill — its SKILL.md and any files it references —
and make targeted improvements to how clearly and effectively the skill instructs Claude.

You are reviewing *as Claude*: you know what makes instructions easy to follow, what
phrasing gets ignored, what flow causes confusion. Use that perspective.

### Review Criteria

Use these four lenses throughout the review. They apply both section-by-section and
to the skill as a whole.

#### 1. Clarity

Can Claude follow this instruction without ambiguity? Watch for:
- Vague verbs ("handle", "deal with", "ensure") where a specific action is needed
- Instructions that assume knowledge Claude won't have at that point
- Steps that could be read multiple ways

#### 2. Flow

Does information arrive before it is needed? Poor flow introduces a term or tool and
only explains it later. Good flow defines things before using them.

**Poor flow:**
> 1. Log in to the program.
> 2. The login-id to use is `snoopy`.

**Good flow:**
> - login-id: `snoopy`
> 1. Log in to the program using {login-id}.

Read the skill as if you've never seen it before. If you encounter something unexplained,
note it — that's a flow problem.

#### 3. Direction

Are mandatory actions unmistakably mandatory? Is it obvious when Claude acts vs. when the
user acts? Weak phrasing ("you might want to", "consider", "it's a good idea to") can
cause Claude to treat required steps as optional. Strengthen where it matters.

Also look for gaps: information or steps that would make the skill more effective but are
currently missing.

#### 4. Bug

Is the skill technically correct? Watch for:
- Wrong API calls, flags, or syntax in commands or code examples
- Instructions that would produce incorrect behavior if followed exactly
- Duplicate or contradictory content that would confuse execution

Bugs are distinct from clarity problems — a buggy instruction can be perfectly clear and
still wrong. Label these separately so the skill author knows to verify, not just reword.

### Review Document Format

After collecting all issues, produce a review document in this format before making any
changes. This gives the user a full picture and a chance to exclude anything before edits start.

```
# Skill Review: <skill-name>

## Issues Found (N total across M files)

### <filename> (N issues)

**Issue N — Label | Section Name**
<one-sentence description of the problem>
**Proposed fix:** <concrete change>

...

## Summary
<one paragraph: count by label, callout of the most critical issues>
```

Rules for the document:
- Group issues by file, with a count per file in the header
- When there is only one file, write `N issues` in the header, omitting "across M files"
- Label each issue with exactly one of: `clarity`, `flow`, `direction`, `bug`
- "Proposed fix" must be a concrete change — not "clarify this" but the actual rewrite
- For anything genuinely ambiguous, write the question in place of the proposed fix

---

### Requirement Levels Preamble

Some skills need vocabulary that distinguishes hard requirements from strong recommendations.
When a skill uses imperative language but Claude is not treating it with the expected
strictness, explicit requirement levels help — they give Claude a defined framework for
weighing whether a step is mandatory or advisory.

#### When to add the preamble

Add it when the skill matches any of these risk profiles:

- Security, privacy, compliance, or data integrity implications
- High customer or financial blast radius
- Difficult rollback or uncertain side effects
- Irreversible actions that could cause harm to persons, infrastructure, reputation, etc.
- Regulated or safety-sensitive domains

Also add it when the user reports that the skill isn't following its own instructions
despite the language appearing clear — this is the signal that the vocabulary distinction
is missing.

#### Where to insert

Right after the skill's opening description paragraph (the "Your job is…" intro),
before the first major section heading. It should be the reader's first encounter with
the terms before any MUST or SHOULD appears.

#### Preamble text

Insert exactly:

```markdown
## Requirement Levels

Terms in this skill use these levels:

- **MUST** / **MUST NOT** — No exceptions. Follow regardless of context.
- **SHOULD** / **SHOULD NOT** — Strong recommendation. Follow it unless you have a
  specific reason not to; note when you deviate and why.

Every MUST and SHOULD in this skill is paired with a rationale. Read the rationale before
deciding to deviate from a SHOULD — it describes what breaks when you skip it.
```

---

### Review Steps

Work through these in order. Steps 1–4 are collection only — do not apply any changes yet.

#### Step 1: Section-by-Section Review of SKILL.md

Read each section. When a section uses `@filename` syntax, contains a markdown link to
another file, or instructs Claude to read a file, read that file immediately as part of
reviewing the section — the quality of the section often depends on what's in the
reference, and deferring it means you're reviewing blind.

For each issue found, record the label, your understanding of the intent, and your proposed
fix. If intent is genuinely ambiguous, record the question instead of guessing. Hold all
collected issues in working memory — you will output them at once in Step 5.

Do not apply fixes yet.

#### Step 2: Whole-Skill Review of SKILL.md

Read SKILL.md as a whole. The section-by-section pass can miss issues that span sections —
information placed later than it's needed, repeated context, or a skill that has grown long
enough to benefit from a restructure (e.g., moving workflows into `references/` files and
keeping only routing logic in SKILL.md).

Apply the same four lenses: clarity, flow, direction, bug.

Also assess risk profile: does this skill operate in any of the categories listed under
"Requirement Levels Preamble" (security, high blast radius, potential for harm, etc.)? If
so and the preamble is not already present, add a `direction` issue to your collected list:
"Add Requirement Levels preamble — this skill meets the risk threshold but the preamble is
absent." If the skill already uses MUST or SHOULD without the preamble, flag that too —
the vocabulary is undefined without it.

Do not apply fixes yet.

#### Step 3: Verify Referenced Files

Confirm that every file referenced in SKILL.md was reviewed during Step 1. For any that
were not, review them now using the same four lenses and record issues.

Do not apply fixes yet.

#### Step 4: Check Frontmatter

Review the `name` and `description` fields. Verify that `name` matches the directory name —
this is the slug used to invoke the skill as `/name`; if they don't match, record a `bug`
issue. A good `description` covers: what the skill does, when to trigger it, and key
synonyms or phrasings a user might say. Check that the description matches the skill's
actual current scope and trigger conditions. Record any needed revision as an issue
labeled `direction`.

Do not apply fixes yet.

#### Step 5: Produce Review Document

Output the full review document using the format above. For any questions you recorded
in Steps 1–4, ask them now and wait for answers before proceeding. After presenting the
document, output this as a standalone line:

`⚠ Exclude, modify, or discuss anything you do not want changed before confirming — The changes above are permanent once applied.`

Do not apply any fixes until the user explicitly confirms.

#### Step 6: Apply Fixes

Apply all approved fixes in order using the Edit tool to make targeted changes to
SKILL.md or the relevant referenced file. Prefer minimal diffs — change only what the
fix requires. For questions that were answered, apply the agreed-upon change. Skip any
issues the user excluded.

#### Step 7: Summary

Present a summary as a bullet list: one item per change, format `[file:section] — what
changed`.

---

### Handling a Standalone "Add Requirement Levels" Request

*Skip this section if you are running a full review. Only follow this section when the
user's sole request is to add requirement levels.*

If the user asks to "add requirement levels" or says the skill isn't obeying instructions:
1. Read the skill
2. Assess it against the risk categories in "Requirement Levels Preamble" above
3. If it does not meet the threshold, tell the user directly:
   - State which categories you assessed and why none apply
   - Explain that adding MUST/SHOULD to a low-stakes skill trains Claude to treat routine
     steps as hard requirements, which degrades the vocabulary's signal in skills that
     genuinely need it
   - If the skill is under-obeyed despite clear language, name the more likely cause:
     vague verbs, weak flow, missing rationale, or a direction gap — and offer to fix those
     instead via a standard review
   - Ask whether to proceed with adding the preamble anyway or address the underlying issue
   - Stop here and wait for the user to decide before taking any further action
4. If it meets the threshold (or the user confirms to proceed despite the assessment):
   - Insert the preamble at the location specified in "Where to insert" above
   - Scan for any existing MUST/SHOULD without a paired rationale and flag those as
     `direction` issues — the vocabulary is only meaningful when every instance explains
     what breaks if it is skipped

If the user chooses to proceed with a full review instead, restart from Step 1 above.

---

## Workflow 2 — Create or Update

Your job is to help the user write a new skill or update an existing one, then review it
using Workflow 1 when the skill is in good shape.

### Step 1: Load Construction Guidance

Read `references/skill-construction-guidance.md` before doing anything else. It covers
description-writing patterns, progressive disclosure organization, writing style, and skill
triggering — and links to the official docs for file anatomy and frontmatter schema.
Keep it in mind throughout this workflow.

### Step 2: Capture Intent

The current conversation may already contain a workflow the user wants to capture (e.g.,
"turn this into a skill"). If so, extract answers from the conversation history first —
the tools used, the sequence of steps, corrections the user made, input/output formats
observed. Fill gaps and confirm with the user before writing.

Gather:
1. What should this skill enable Claude to do?
2. When should this skill trigger? (what user phrases or contexts)
3. What is the expected output or behavior?
4. Are there multiple workflows or operation modes?

Ask one clarifying question at a time. Do not start writing until all four questions above have been answered, even if briefly.

### Step 3: Draft the Skill

Based on the conversation and construction guidance:

**Script constraint:** Do not implement non-trivial scripts without explicit user direction.
Describe the script's purpose in a comment block and stop there.

- Write `SKILL.md` with correct frontmatter (`name`, `description`)
- If the skill has multiple workflows or operation modes, add a routing table near the top
- Move large or domain-specific content to `references/` files; keep SKILL.md under 500 lines
- If the skill needs bundled scripts, describe what each script should do in a comment block

Present the draft to the user. Ask for feedback before treating it as final.

### Step 4: Iterate

Revise based on the user's feedback. Repeat until the user is satisfied with the content.

### Step 5: Review

Your context is contaminated — you authored or edited this skill and know the intent behind
every choice. A solo review will miss issues your familiarity obscures. Run the review twice
and merge the results.

**5a. Your review**
Run Workflow 1 Steps 1–4 on the current skill. Collect your issues but do not output them yet.

**5b. Sub-agent review**
Spawn a sub-agent with no prior context about the target skill. The sub-agent prompt must
include:
- The path to this skill's own SKILL.md file — you know it, because you are currently
  executing from it. Tell the sub-agent to read that file first to load the Workflow 1
  review criteria, steps, and document format natively.
- The full text of the target skill's SKILL.md and all referenced files, pasted directly
  into the prompt.
- Instruction to apply Workflow 1 Steps 1–4 to the target skill content and return only
  the issues section of the Review Document.

The sub-agent has no knowledge of how the target skill was written. Its findings represent
what a reader encountering the skill cold will stumble over.

**5c. Merge**
Compare the two issue lists. For each item:
- **Both found** — include it; high confidence
- **Your find only** — include all of them; mark any that rely on intent you know but the
  skill never states with `(author context)` after the label, so the user can weigh it
  knowing the finding depends on unstated intent
- **Sub-agent only** — include all of them; these are exactly the gaps your context hid
  from you

**5d. Produce unified review document**
Output the merged issue list using the Review Document Format from Workflow 1. In the
Summary paragraph, note how many issues were unique to each reviewer and how many were shared.

Then continue with Workflow 1 Steps 5 through 7 — present to user, await confirmation,
apply fixes, summary.
