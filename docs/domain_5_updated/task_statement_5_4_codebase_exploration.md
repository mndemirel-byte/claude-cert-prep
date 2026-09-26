# Task Statement 5.4: Codebase Exploration

## Domain 5 — Context Management and Reliability (15% of the Exam)

---

## Core Idea

An agent exploring a large codebase runs for a long time. It reads files, examines classes, maps dependencies. During this process, **context degradation** is an unavoidable problem. The agent begins to lose the specific information it discovered early in the session and starts using general phrases like "typical patterns".

This task statement teaches how to detect context degradation, how to prevent it with four strategies, and how to recover after a crash.

Exam scenario: **Code Generation with Claude Code** — codebase exploration is done in a Claude Code session (interactively or via the Agent SDK); `/compact`, subagents, and the scratchpad are Claude Code tools.

---

## Context Degradation

### Symptoms

In long sessions, you observe the following changes in the agent's behavior:

1. **Generalization:** While the agent reports specific findings early in the session, such as "the UserService.authenticate() method does no null check at line 47", in later turns it starts using vague statements like "services of this kind usually perform authentication checks". Exam guide: "*referencing 'typical patterns' rather than specific classes discovered earlier*".

2. **Inconsistent answers:** It gives a different answer to the same question at turn 3 and at turn 30. Guide: "*models start giving inconsistent answers*".

3. **Contradictory references:** It misremembers a class it discovered earlier or references a method that does not exist.

4. **Context saturation:** Verbose exploration output (file listings, grep results, full file contents) fills up the context.

### Why Does It Happen? — Know the mechanism correctly

The common wrong explanation: "When the context window fills up, the oldest information drops off." **That is not what happens.** The Messages API does not silently discard old messages; if the window is exceeded, the request **returns an error** (prompt too long). In Claude Code, **automatic compaction** (summarization) runs as the limit approaches. The real causes of degradation are two:

| Stage | What happens | Name |
|---|---|---|
| **Before the limit is reached** | Every token spends from the model's limited **attention budget**; as the context grows, the model cannot locate the specific finding in the middle/old part and drifts toward general patterns | **Context rot** (Anthropic's term) |
| **After compaction** | During summarization, specific findings (line number, class name) turn into vague statements — the codebase version of 5.1's progressive summarization trap | Summary loss |

**Exam consequence:** This is the real rationale behind the "use a model with a larger context window" distractor — in the language of exam guide Q12: "*larger context windows don't solve attention quality issues*". Window size does not improve attention quality; it does not even delay the problem, you just experience the same context pollution across a larger area.

---

## Four Mitigation Strategies — Which One for Which Symptom?

| Symptom | Strategy | Why it works |
|---|---|---|
| Specific findings are getting lost | **1. Scratchpad file** | The finding lives outside the context, persistent on disk |
| Verbose exploration output is filling the context | **2. Subagent delegation** | Verbose output stays in the subagent's context; only a summary returns to the parent |
| Information transfer between phases is needed | **3. Summary injection** | The subagent inherits nothing; whatever it needs to know is written into its prompt |
| Context is full and the findings are safe | **4. `/compact <focus>`** | The narrative is summarized; the focus instruction preserves the critical findings |
| Crash | **Manifest** (below) | Recovery relies on structured state, not on the transcript |

The exam gives all four across four options; the differentiator is the *symptom*.

### 1. Scratchpad Files

Write key findings to a file and reference that file for subsequent questions. Anthropic's name for it: **structured note-taking**.

```markdown
<!-- NOTES.md — the session's working memory -->
## Exploration Findings
- UserService.authenticate(): null check missing (src/auth/user_service.py:47)
- PaymentGateway: no retry mechanism (src/payments/gateway.py)
- DatabasePool: max connection = 10, scaling problem (config/db.yaml)

## Open Questions
- does the refund flow call PaymentGateway directly, or via the queue?
```

**Advantage:** Findings persist independently of the context window. Even if the context is compacted, the agent can recover earlier findings by reading the file.

**Scratchpad ≠ CLAUDE.md — an exam distractor.** CLAUDE.md is the *persistent instruction* file loaded in every session (Domain 3.1: rules, conventions, commands). If session-specific exploration findings are written to CLAUDE.md, they (a) bloat the context of every session, and (b) pollute subsequent, unrelated sessions with stale findings. The scratchpad is the session's *working memory*; CLAUDE.md is the project's *constitution*.

> **Current note:** The API-side counterpart of the same pattern is the **memory tool** (beta) — it lets the agent write to and read from a persistent memory directory outside the context. In Anthropic's multi-agent research system, the lead agent saves its plan to memory before approaching the context limit. The exam answer is the scratchpad file; the memory tool is the tool-shaped form of the same idea.

### 2. Subagent Delegation

Create subagents for specific investigations. The main agent maintains high-level coordination. The exam guide's examples: "*find all test files*", "*trace refund flow dependencies*".

```
Main agent (coordination):
├── Subagent 1: "Find all test files and summarize coverage"
├── Subagent 2: "Trace the dependencies of the refund flow"
└── Subagent 3: "List the API endpoints and extract their auth requirements"
```

**Why it works (Agent SDK mechanism):** The subagent starts with a **clean context** — it does **not** receive the parent's conversation history or tool results. Intermediate tool calls and the 40 files it read stay in the subagent's own context; **only the final message** (the summary) returns to the parent. The guide's wording: "*isolating verbose exploration output while the main agent coordinates high-level understanding*".

**Its cost:** Because the subagent inherits nothing, whatever it needs to know is written into its prompt. Exam guide Exercise 4 step 16: "*each subagent receives its research findings directly in its prompt rather than relying on automatic context inheritance*". This is the rationale for the third strategy.

**When to use it:** When parallel exploration is needed in large codebases. Directly connected to Claude Code's built-in `Explore` subagent and the multi-agent orchestration in Domain 1.

### 3. Summary Injection

Summarize the findings of one exploration phase and inject them into the next phase's subagents **in their prompts**.

```
Phase 1: Exploration → findings to scratchpad + short summary
    ↓
Summary injection → into the prompts of Phase 2 subagents
    ↓
Phase 2: In-depth analysis (clean context + summary of previous findings)
```

**Advantage:** Provides information transfer between phases. Subagents know the previous phase's findings but do not carry the verbose exploration output.

**When to use it:** In multi-phase investigations — exploration → analysis → synthesis flows. It comes together with Strategy 2: because the subagent inherits nothing, injection is essential.

### 4. The `/compact` Command

When the context fills with verbose exploration output, `/compact` summarizes the conversation history and replaces it with the summary. The exam guide's Skills item: *"Using /compact to reduce context usage during extended exploration sessions when context fills with verbose discovery output"*.

| Command / mechanism | What it does | When |
|---|---|---|
| `/compact` | Summarizes the history, continues | You will continue the same job, the context is full |
| `/compact Focus on: bugs found and file paths` | **Focus instruction** — tells the summarizer what to preserve | To protect critical findings from summary loss (the fix for the 5.1 trap) |
| `# Compact instructions` section in CLAUDE.md | Persistent focus instruction | If the same things are to be preserved in every compaction |
| Automatic compaction | Runs on its own as the limit approaches | No intervention needed; but without a focus instruction, summary loss occurs |
| `/clear` | Does not summarize, **resets** | When switching to an unrelated job; if you will not continue |
| `/context` | Shows what is taking up space | Diagnosis before compacting |

**When it is the correct answer:** The context is full of verbose exploration output **and** the findings have already been captured in the scratchpad. Then `/compact <focus>` is the cheapest fix. If the findings are not in the scratchpad, write them there first, then compact — otherwise you will suffer summary loss. This ordering is this document's interpretation; the exam guide counts `/compact` as an independent strategy.

---

## Crash Recovery

### Problem

While a multi-agent system is running, an agent crashes. The findings the agent had gathered up to that point are lost. When the system restarts, does everything have to be rediscovered from scratch?

### Solution: Manifest File

Each agent exports its structured state to a known file location (a manifest). Exam guide: "*each agent exports state to a known location, and the coordinator loads a manifest on resume*".

```json
// state/research_agent_manifest.json
{
  "agent_id": "research_agent_01",
  "phase": "analysis",
  "completed_tasks": [
    "source_collection",
    "initial_categorization"
  ],
  "pending_tasks": [
    "deep_analysis_geothermal",
    "cross_reference_check"
  ],
  "key_findings": [
    {"claim": "Solar grew 45%", "source": "IEA", "source_location": "p.12", "publication_date": "2024-06-15"},
    {"claim": "Wind hit $120B", "source": "IRENA", "source_location": "exec summary", "publication_date": "2024-03-20"}
  ],
  "last_checkpoint": "2024-03-15T14:30:00Z"
}
```

### Recovery Flow

1. The coordinator is restarted
2. It loads the manifest files
3. It injects each agent's state into the agent prompts (the same mechanism as summary injection)
4. The agents continue from where they left off — they do not start from scratch

**Rule:** Each agent writes its structured state to the manifest file regularly (checkpoint). In case of a crash, the coordinator recovers by loading these manifests. The manifest is never summarized (5.1 table: structured records are never summarized).

### Manifest vs session resume — why is "restore the full history" wrong?

> **Current note:** The Agent SDK writes the session to disk (`.jsonl`); `resume=<session_id>` or `continue_conversation=True` restores the *full transcript*, and `fork_session` branches it. So "store and restore the full conversation history" is *possible* today. Why is the exam answer still the manifest? The SDK documentation's own advice: "*Don't rely on session resume … capture the results you need as application state and pass them into a fresh session's prompt — often more robust.*" Three reasons: (1) the transcript is verbose; once restored it immediately consumes the context budget, and the degradation picks up where it left off; (2) the session file is machine-bound, a different host/container requires a `SessionStore`; (3) the manifest is *application state* — compact, portable, auditable. Resume is "continue from where you were"; the manifest is "continue from what you know".

---

## Key Takeaways for the Exam

| Concept | Remember |
|---|---|
| Symptoms of context degradation | Specific → general ("typical patterns"), inconsistent answers, contradictory references |
| Why it happens | Context rot (attention budget) + summary loss after compaction — **not** "old messages drop off" |
| The large window distractor | Window size does not fix attention quality (Q12 rationale) |
| Scratchpad | Write findings to a file (NOTES.md); **not** CLAUDE.md — that is the persistent instruction file |
| Subagent delegation | Clean context, verbose output stays inside, only the final message returns; inherits nothing |
| Summary injection | Write the phase summary into the next subagents' prompts — essential because they inherit nothing |
| `/compact` | With a focus instruction (`/compact <focus>`, CLAUDE.md compact instructions); `/clear` resets, does not summarize |
| Crash recovery | Each agent writes a manifest, the coordinator loads it and injects it into the prompt; not transcript resume |

---

## Practice Scenario 1

> A developer is running an agent session that has been exploring a large codebase for 2 hours. At the beginning, the agent reported specific findings such as "there is a race condition in the PaymentService.process() method, the lock mechanism is missing at line 142".
>
> Now it uses vague statements like "thread safety concerns should generally be taken into account in services of this kind".
>
> **Which is the most effective solution?**
>
> **A)** Use a model with a larger context window.
>
> **B)** Add an "always be specific" instruction to the agent's system prompt.
>
> **C)** Write the key findings to a scratchpad file; create subagents for subsequent research phases and inject a summary of the findings into the subagent prompts.
>
> **D)** Write the findings to CLAUDE.md so they are loaded automatically in every session.

### Correct Answer: C

**Why C is correct:** Classic symptoms of context degradation — the shift from specific findings to general statements. Three strategies are applied together: make the findings persistent with the scratchpad, investigate in a clean context with subagents, and transfer information between phases with summary injection.

**Why A is wrong:** Window size does not improve attention quality (context rot). In a larger window, the same verbose output produces the same degradation.

**Why B is wrong:** A prompt instruction is probabilistic. The problem is not that the model is "lazy" but that its attention is diluted by context pollution and specific information is lost in the summary after compaction. Saying "be specific" does not bring back information it cannot access.

**Why D is wrong:** CLAUDE.md is the persistent instruction file; if session-specific findings are written there, they bloat every session's context and pollute unrelated sessions. The scratchpad is session memory; CLAUDE.md is the project constitution.

---

## Practice Scenario 2

> A multi-agent research system is running with 3 subagents. The system experiences a crash. On restart, the coordinator starts the subagents from scratch — the 2-hour data collection phase that had already been completed is repeated.
>
> **Which mechanism should have been implemented to prevent this problem?**
>
> **A)** Use more reliable hardware — so that crashes do not happen.
>
> **B)** Each agent should regularly write its structured state (completed/pending tasks, key findings) to a manifest file. During recovery, the coordinator should load the manifest files and inject them into the agent prompts, restarting the agents from where they left off.
>
> **C)** Use the Agent SDK's session persistence: store each subagent's `session_id`, and after a crash restore the full conversation history with `resume`.
>
> **D)** Reduce the number of agents — so that a single agent's crash does not affect the whole system.

### Correct Answer: B

**Why B is correct:** The crash recovery mechanism. Each agent writes structured state to a manifest file; during recovery, the coordinator loads these manifests and injects them into the agent prompts. The agents continue from where they left off, not from scratch.

**Why A is wrong:** Hardware reliability reduces crashes but does not eliminate them. A recovery mechanism must exist in every system.

**Why C is wrong:** Technically possible, but it has three problems: the full transcript is verbose and immediately consumes the context budget once restored; the session file is machine-bound; and the SDK documentation's own advice is, rather than relying on resume, to capture the results as application state and pass them to a fresh session via the prompt — that is, a manifest.

**Why D is wrong:** Reducing the number of agents does not solve crash recovery. Even a single agent can crash — a recovery mechanism is necessary.

---

## Practice Scenario 3

> A developer who has been extracting the module boundaries of a monolith with Claude Code for 3 hours receives a context saturation warning. Most of the findings exist only in the conversation so far; nothing has been written to any file. The developer immediately runs `/compact` and continues; 20 minutes later the agent says "we discussed earlier which services the payment module depends on, but I don't remember the details".
>
> **What went wrong, and what should the correct order have been?**
>
> **A)** `/clear` should have been used instead of `/compact`; a clean context works better.
>
> **B)** The compaction ran without a focus instruction, and because the findings were not in any file, they were lost in the summary. The correct order: first have the findings written to the scratchpad, then summarize with `/compact Focus on: module boundaries and dependency list`.
>
> **C)** Automatic compaction should have been turned off and a model with a larger window chosen.
>
> **D)** The dependency list should have been written to CLAUDE.md; compaction does not summarize CLAUDE.md.

### Correct Answer: B

**Why B is correct:** The compaction's summarizer did not know what to preserve (no focus instruction), and the findings were nowhere outside the context — 5.1's progressive summarization trap. Scratchpad + focused compaction solves both.

**Why A is wrong:** `/clear` does not summarize, it resets — all of the findings would have been gone. When continuing the same job, `/clear` is the wrong tool.

**Why C is wrong:** Window size does not solve summary loss or context rot; turning off automatic compaction means getting an error once the limit is hit.

**Why D is wrong:** CLAUDE.md is unaffected by compaction, true — but a session-specific dependency list does not belong there; every subsequent session would open with this list. The right place is the scratchpad.
