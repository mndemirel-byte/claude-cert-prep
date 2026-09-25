# Task Statement 1.7: Session State and Resumption

## Domain 1 — Agentic Architecture & Orchestration (27% of Exam)

---

## The Core Idea

Agents can run for a long time. Sometimes you need to leave a session and come back later. Or the agent has been running for a long time and the context has started to degrade. This task statement answers the question: **how do you manage a session?**

A session is the full conversation transcript Claude Code keeps on disk: user messages, Claude's responses, every tool call and its result. That record is what lets you resume a session later, branch it, or summarise it into a new one.

---

## The Three Options

### Option 1: Resume (`--resume <session-name>`)

Continues a specific session from where it left off. All prior context — tool calls, results, Claude's reasoning — is preserved as-is.

**When to use:** The prior context is still valid and the files haven't changed significantly. For example, you left a research session halfway and will continue tomorrow — the data is still current.

### Option 2: fork_session

Copies an existing session's history to create **independent branches** from a shared analysis baseline. The original session is unchanged; each branch gets a new session ID.

**When to use:** You want to try different approaches from the same starting point. For example, comparing two different refactoring strategies against the same codebase analysis. Each branch runs independently; you do the analysis once and use it twice.

**Mechanism:** `fork_session` doesn't work on its own — it's always paired with `resume`. `resume` says which session to copy; `fork_session` says "don't overwrite, branch" (details in 1.3).

### Option 3: Fresh Start with Summary Injection

You start a new session but inject a **structured summary** of the prior findings into the initial context. It doesn't rediscover from scratch — it takes the prior knowledge as a summary and continues from there.

**When to use:** Tool results have gone stale, files have changed extensively, or context quality has degraded in a long session.

**How it's done:** The summary goes into the new session's first prompt, or into the system prompt via `--append-system-prompt`; if it needs to persist across the project, it goes into CLAUDE.md. A good summary isn't free text — it has fixed fields:

```markdown
## Prior session summary (2026-09-24)
- Findings: the auth module does JWT validation in `verify_token()`; 3 endpoints bypass it (list: ...)
- Decisions made: middleware approach chosen, decorator approach rejected (reason: ...)
- Work completed: `auth/middleware.py` written, tests pass
- Remaining work: wire the 3 endpoints to the middleware, remove the old decorator
- Files changed since then: `routes/api.py` (rewritten), `models/user.py` (field added)
```

Critical: the summary should state **what may no longer be valid** as well as **what is known** — the agent starts with "re-check these" rather than with stale assumptions.

---

## Mechanism Table — CLI and SDK

The exam may ask about the mechanism by name. The counterparts:

| Operation | Claude Code CLI | Agent SDK option |
|---|---|---|
| Continue the most recent session | `claude --continue` (`-c`) | `continue_conversation=True` |
| Continue a specific session | `claude --resume <name or ID>` (`-r`) | `resume="<session_id>"` |
| Open the session picker | `claude --resume` (no argument) | — |
| Name a session | `claude --name <name>` (at startup) / `/rename <name>` (in session) | — |
| Branch | resume with `--fork-session` / `/branch` (in session) | `resume="<id>", fork_session=True` |
| Resume up to a specific message | — | `resume_session_at="<message_uuid>"` |
| Use a custom session ID | — | `session_id="<uuid>"` |

The difference between `--continue` and `--resume`: `--continue` opens the **most recent** session in the current directory without you choosing; `--resume` selects a specific session by name or ID. In long-running projects, naming sessions (`--name`, `/rename`) saves you from memorising IDs — that's what the exam guide calls "named session resumption."

---

## The Stale Context Problem (Exam Trap)

This is very important. A developer resumes a session but has changed files in the meantime. The agent's context still holds the old tool results (old file contents, old grep output). The agent reasons from them — it gives advice about code that no longer exists, or makes contradictory suggestions.

Don't expect the agent to suspect "the file may have changed" on its own: the tool result in its context is reality to it. **You** have to report the staleness.

**The fix:** If you're resuming and files have changed, **tell the agent specifically which files changed** — so it does targeted re-analysis. Don't ask it to rediscover everything from scratch.

> "Since the last session, `routes/api.py` and `models/user.py` have changed. Treat your earlier findings about these files as invalid and re-read both. The other files are unchanged."

**But if the changes are extensive or the tool results are entirely stale** → a fresh start with summary injection is more reliable. The rule of thumb: if you can enumerate the changed files, resume + notify; if you can't, or the structure itself has changed (modules deleted, API redesigned), fresh start.

---

## A Fourth Option: Context Compaction

The problem "context quality degraded in a long session" has one more answer besides a fresh start: **compaction**. Claude Code automatically summarises the conversation as the context approaches its limit; with the `/compact` command you can trigger it whenever you want, with an optional focus ("preserve the test findings").

Compaction vs. fresh start:

| | Compaction | Fresh start with summary injection |
|---|---|---|
| Who summarises | Claude, automatically | You (or Claude in the prior session, under your direction) |
| Session | The same session continues | A new session |
| Control | Low — the model decides what to keep | High — you decide the summary's content |
| Stale tool results | Summarised, but not known to be stale | Explicitly flagged in the summary |
| Best fit | Context is full, files haven't changed | Files have changed and/or a controlled restart is wanted |

The `PreCompact` hook (1.5) is used to write critical information to a file before compaction — a safety net for details compaction might lose.

---

## Decision Table

| Situation | Correct approach |
|---|---|
| Context still valid, files unchanged | **Resume** |
| Try different approaches from the same baseline | **fork_session** (resume + fork) |
| Resume + a few files changed | Resume + **report the specific file changes** |
| Tool results stale, files changed extensively, structure changed | **Fresh start with summary injection** |
| Context is full but files haven't changed | **Compaction** (`/compact`) |

---

## Key Exam Takeaways

| Concept | Remember |
|---|---|
| Resume | Context valid, files unchanged → continue where it left off; `--continue` = most recent, `--resume` = chosen session |
| Session naming | `--name` / `/rename` → `--resume <name>`; the exam guide's "named session resumption" |
| fork_session | Always with `resume`; independent branches from a shared baseline, the original is unchanged |
| Fresh start with summary injection | Stale context, extensive changes → new session + structured summary (findings, decisions, remaining work, **changed files**) |
| Stale context problem | Contradictory advice after resume → the agent is relying on stale tool results; it won't notice on its own |
| Specific file notification | Resume + changed files → say which files changed, targeted re-analysis |
| Compaction | Context full, files unchanged → `/compact`; preserve critical info with a `PreCompact` hook |
| Exam trap | "Rediscover everything," "use a bigger model," "fork and pick the best" — none of these fix the problem |

---

## Practice Scenario 1

> A developer resumes an agent session that was working on a codebase. In the meantime they've made significant changes to 3 files. The agent gives contradictory advice about these files — at one point it says "refactor this function," but the function has already been changed.
>
> **What is the problem and what is the correct approach?**
>
> **A)** The agent's context window is insufficient — a bigger model should be used.
>
> **B)** The agent is reasoning from stale tool results — when resuming, the changed files should be reported specifically, or if the tool results are entirely stale, a fresh start with summary injection should be done.
>
> **C)** Add the instruction "re-check the files" to the agent's system prompt.
>
> **D)** Create two branches with fork_session and pick the best result.

### Correct Answer: B

**Why B is correct:** The agent is reasoning from old tool results — the files have changed, but the agent doesn't know and can't know. The fix is two-tiered: if the changes are limited (3 files, enumerable), resume and report the specific file changes; if the changes are extensive or the context is entirely degraded, do a fresh start with summary injection.

**Why A is wrong:** The problem isn't context window size, it's stale data. A bigger model makes the same mistakes from the same old data.

**Why C is wrong:** A prompt instruction is probabilistic and untargeted — "re-check the files" doesn't say which files changed; the agent either re-reads everything (waste) or still trusts the stale data. Specific notification is needed.

**Why D is wrong:** fork_session is for comparing different approaches. The problem here is stale context — even if you branch, both branches start from the same stale data.

---

## Practice Scenario 2

> A team runs a long Claude Code session doing dependency analysis on a large monorepo. The analysis took 40 minutes and is complete. Now the team wants to try two different migration strategies separately — (a) gradual module-by-module migration, (b) a single big-bang migration — from the same analysis baseline, and compare the results. The codebase hasn't changed since the analysis.
>
> **What is the most efficient approach?**
>
> **A)** Start two new sessions and redo the analysis in each — that way every strategy runs in a clean context.
>
> **B)** In the same session, try (a) first, then say "now try (b)" — let Claude compare the two.
>
> **C)** Branch the analysis session twice with `resume` + `fork_session`; run one strategy in each branch. The analysis is done once, both branches inherit it, and they don't affect each other.
>
> **D)** Summarise the analysis session with `/compact`, then try the two strategies sequentially in the same session.

### Correct Answer: C

**Why C is correct:** This is exactly fork_session's use case — independent branches from a shared analysis baseline. The 40-minute analysis is done once; each branch inherits the history up to the fork point and runs its own strategy independently. The branches don't pollute each other's context, the original analysis session stays intact, and you get two clean results to compare.

**Why A is wrong:** Repeating the 40-minute analysis twice is waste. The code hasn't changed, so the analysis isn't stale — there's no justification for redoing it.

**Why B is wrong:** Trying them sequentially in the same session means strategy (b) runs in a context contaminated by (a)'s outputs and decisions. The comparison isn't fair; moreover, file changes made during (a) affect (b).

**Why D is wrong:** Compaction shrinks the context but provides no isolation — the contamination problem from B remains. And there's no context-full problem here; the problem is the need for two independent experiments.
