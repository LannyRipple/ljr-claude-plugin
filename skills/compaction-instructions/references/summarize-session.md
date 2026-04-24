# summarize-session agent prompt

Use this as the prompt for an Explore sub-agent to extract a session summary from a JSONL file.

---

Read the session JSONL file at `{JSONL_PATH}` and extract the following for compaction instructions:

1. What was the user's overall goal / work intent?
2. What decisions were made?
3. What was accomplished (completed steps)?
4. What work was in progress when the context filled — and what is the next concrete action?
5. Any open questions or blockers?

Parse the assistant and user messages to reconstruct the session narrative. Focus on the content
of text messages, not tool call metadata. Look for patterns indicating the session was cut short
mid-task.

Return a structured summary with those 5 sections clearly labeled.
