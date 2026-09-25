# Task Statement 1.3: Subagent Invocation and Context Passing

## Domain 1 — Agentic Architecture & Orchestration (27% of Exam)

---

## The Core Idea

In Task Statement 1.2 we learned that the coordinator manages subagents. Now we get to the real question: **how does the coordinator create subagents, and how does it pass information to them?**

---

## The Task Tool

The coordinator's mechanism for creating subagents is the **Task tool**. The critical detail: if `"Task"` is not in the coordinator's `allowedTools` list, it cannot create subagents — at all.

> **Naming note:** The exam guide calls this tool `Task`, and **that is the correct answer on the exam**. In the current Agent SDK the tool has been renamed `Agent`: it appears as `Agent` in `tool_use` blocks, while the tools list in the `system:init` message still says `Task`. If you see either name in a scenario, know that it's the same mechanism.

---

## AgentDefinition — How a Subagent Is Defined

Every subagent is defined by an **AgentDefinition**. The three core fields the exam emphasises:

- **Description** — a short explanation of what the subagent does and **when it should be used**. The coordinator decides which subagent to select by reading this (dynamic selection from 1.2).
- **System prompt** (`prompt`) — the subagent's behavioural rules and instructions
- **Tool restrictions** (`tools`) — the tools the subagent can access (only what it needs — least privilege)

The real SDK has further fields that matter in practice:

| Field | What it does | Where it shows up in an exam scenario |
|---|---|---|
| `description` (required) | When to use it | Coordinator picks the wrong subagent → description is vague |
| `prompt` (required) | The subagent's system prompt | Subagent doesn't know the quality criteria → not in the prompt |
| `tools` | Allowed tool list | Subagent deletes files → unnecessary permission granted |
| `disallowedTools` | Tools removed from the inherited set | "Everything except these" instead of an explicit `tools` list |
| `model` | A different model for the subagent (`haiku`, `sonnet`, `opus`, `inherit`) | Cost: a cheaper model for a simple search subagent |
| `maxTurns` | Maximum number of turns the subagent may run | Subagent researches endlessly → no turn limit |

There are two ways to define one, and both produce the same AgentDefinition structure: **file-based** (`.claude/agents/<name>.md` — `description`, `tools`, `model` in the frontmatter; the system prompt in the body) and **programmatic** (the `agents={...}` option in the Agent SDK). The exam asks about the mechanism, not the file syntax.

---

## Context Passing — The Most Critical Topic

Recall the isolation principle from 1.2: subagents don't inherit the coordinator's conversation history. So how does the coordinator pass information? Three fundamental rules:

### Rule 1: Include Prior Agents' Findings Directly in the Prompt

For example, if you're having a synthesis agent write a report, you must copy the results the web search agent found and the information the document analysis agent extracted into the synthesis agent's prompt. The synthesis agent doesn't "know" these — if you don't provide them, it can't see them.

By "include" we mean the **complete findings**, not a summary like "the web search agent found good results." If the coordinator abbreviates the findings, the synthesis agent works from the abbreviated version.

### Rule 2: Use Structured Data Formats — Separate Content from Metadata

This is very important and frequently tested. When passing information to subagents, sending raw text is not enough. You must send source URLs, document names, and page numbers in a structured format, separate from the content. That way attribution is preserved across agents.

Bad example:
```
"The global solar market grew 25% in 2024 according to some reports."
```

Good example:
```json
{
  "claim": "The global solar market grew 25% in 2024",
  "source_url": "https://iea.org/reports/solar-2024",
  "document": "IEA Solar Market Report 2024",
  "page": 12
}
```

**Where does this structure come from?** The coordinator can't convert plain text into JSON after the fact — if the source information was lost in the text, it can't be recovered. The structured format must start **in the subagent's output**: the coordinator puts an output schema into the research subagent's prompt ("Return every finding as JSON with the fields `claim / source_url / document / page`"). That way the metadata is never lost along the chain — search → coordinator → synthesis. (Structured output techniques are covered in detail in Domain 4.)

### Rule 3: Specify Goals and Quality Criteria, Not Procedural Instructions

Coordinator prompts should state research goals and quality criteria, not step-by-step procedural instructions. This lets the subagent adapt to context.

- **Wrong:** "First search for this, then read that, then write this."
- **Right:** "Research developments in renewable energy over the last 2 years. Cite a source for every claim. Cover at least 5 different energy types."

The four components of a good subagent prompt: **the goal** (what to produce), **scope boundaries** (what not to cover — scope partitioning from 1.2), **quality criteria** (sources, minimum coverage, format), and **the output schema** (Rule 2).

---

## Parallel Spawning — Speed Optimisation

The coordinator can make **multiple Task tool calls in a single response**. This launches the subagents **in parallel**. (The mechanism is the same as parallel tool use in 1.1 — multiple `tool_use` blocks in one assistant response.)

For example, in a single response the coordinator can:

- Task tool → launch the web search agent
- Task tool → launch the document analysis agent

This is much faster than launching each in a separate turn, sequentially. Three subagents × 15 seconds sequentially = 45 seconds; in parallel ≈ 15 seconds. The exam tests latency awareness.

### When not to spawn in parallel

Parallel spawning is for subtasks that are **independent of each other**. If one subagent's output is another's input (search → synthesis), you can't launch both at once — the findings synthesis needs don't exist yet. The correct pattern: launch the independent ones in parallel, collect the results, then launch the dependent one.

On the exam, a "launch everything in parallel" option is a distractor when there are dependencies between the subtasks.

### Scope and cost control

- Subagents can spawn subagents of their own (nesting). The default depth limit is 3, configurable via `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`. As depth grows, observability drops and cost compounds — a single level is enough for most designs.
- The number of subagents running concurrently directly affects cost and rate limits. "10 subagents in parallel" is not always better than "3 subagents in parallel"; scope partitioning (1.2) determines how many subagents are actually needed.

---

## fork_session

`fork_session` copies an existing session's history to create **independent branches** from a shared analysis baseline.

Use case: you want to compare two different testing strategies against the same codebase analysis. With `fork_session` you create two independent branches from the common starting point. Each branch runs independently after the fork point; the original session is unchanged.

**Critical mechanism detail:** `fork_session` does nothing on its own — it is **always used together with `resume`**. `resume=<session_id>` says which session to copy; `fork_session=True` says "don't overwrite that session, branch off with a new session ID." Without `resume`, `fork_session` is meaningless; without `fork_session`, `resume` continues the original session.

A forked branch **does** receive the history up to the fork point — the deliberate exception to the isolation principle (1.2). Decision rules and the resume vs. fresh-start comparison are in Task Statement 1.7.

---

## Key Exam Takeaways

| Concept | Remember |
|---|---|
| Task tool | The mechanism for creating subagents — must be in the coordinator's `allowedTools` (`Task` on the exam; `Agent` in the current SDK) |
| AgentDefinition | Description (when to use) + system prompt + tool restrictions; also `model` and `maxTurns` |
| Context passing | Include prior agents' findings in the prompt **in full** — not a summary |
| Structured metadata | Claim-source mapping — separate content from metadata; the structure starts in the subagent's output schema |
| Coordinator prompts | Goal + scope boundary + quality criteria + output schema; no step-by-step instructions |
| Parallel spawning | Multiple Task calls in one response → **independent** subagents run in parallel; dependent ones run sequentially |
| Nested subagents | Default depth 3; deeper nesting lowers observability and raises cost |
| fork_session | Always together with `resume`; copies history up to the fork point, leaves the original unchanged |

---

## Practice Scenario 1

> A multi-agent research system exists. The web search subagent and the document analysis subagent work perfectly — both produce rich, sourced data. But in the final report produced by the synthesis subagent, many claims are **unattributed** — it's unclear which information came from where.
>
> **What is the root cause and how should it be fixed?**
>
> **A)** The synthesis subagent's system prompt doesn't ask for attribution — add a "cite a source for every claim" instruction to the prompt.
>
> **B)** The coordinator's context passing mechanism doesn't include structured metadata — the subagents' output should be converted to a structured format that maps claims to sources.
>
> **C)** The web search subagent doesn't return source URLs — URLs should be added to the search results.
>
> **D)** The synthesis subagent should be given the coordinator's full conversation history so it can see the sources.

### Correct Answer: B

**Why B is correct:** The problem is in *how* the information is passed. The web search and document analysis agents work correctly — they produce the data. But when the coordinator passes that data to the synthesis agent, it sends it as plain text without including the metadata (source URL, document name, page number) in parsed form. The synthesis agent sees raw text but can't tell which claim came from which source. The fix: put an output schema into the research subagents' prompts and convert the output into a structured format that maps claims to sources.

**Why A is wrong:** Adding an instruction to the prompt may help, but it's not the root cause. Even if you tell the synthesis agent "cite sources," if the data it receives doesn't contain source information in structured form, it has nothing to cite. A prompt instruction can't create missing data.

**Why C is wrong:** The question states explicitly — the web search subagent works perfectly and produces sourced data. The problem isn't in production, it's in the coordinator's passing mechanism.

**Why D is wrong:** Isolation principle trap. Giving subagents the coordinator's full conversation history is not the right architectural approach — it violates the isolation principle. The fix is for the coordinator to pass context with structured metadata.

---

## Practice Scenario 2

> A coordinator uses three subagents for a customer complaint analysis: `fetch_tickets` (pulls support records), `classify` (sorts records into categories), and `report` (writes an executive summary from the category distribution). Wanting to reduce latency, the developer makes the coordinator issue all three Task calls **in a single response**.
>
> Result: `classify` runs with an empty record list and returns "no categories found," and `report` produces a summary saying "no data." `fetch_tickets`, meanwhile, correctly retrieved 240 records.
>
> **What is the problem, and what is the correct design?**
>
> **A)** The `classify` and `report` subagents should be given the coordinator's full conversation history so they can see the records.
>
> **B)** The three subagents are dependent on each other — `classify` needs `fetch_tickets`' output, and `report` needs `classify`'s output. Parallel spawning is only for independent subtasks; the coordinator should launch them sequentially and include each step's full output in the next one's prompt.
>
> **C)** The `classify` subagent's `maxTurns` should be increased so it can wait for the records to arrive.
>
> **D)** The subagents should communicate directly — `fetch_tickets` should notify `classify` when it finishes.

### Correct Answer: B

**Why B is correct:** This is a sequential dependency chain. When all three are launched at once, `classify` and `report` run before the input they need has been produced. Parallel spawning buys speed, but only when the subtasks are independent. The correct design: `fetch_tickets` → include its output in the `classify` prompt → include that output in the `report` prompt. If the work were independent (for example, three `fetch_tickets` pulling records for different regions), parallel would be correct.

**Why A is wrong:** Isolation principle trap. Even with the full history, the timing problem remains — when `classify` starts, `fetch_tickets` hasn't finished, so there's nothing in the history to see. The problem isn't missing context, it's ordering.

**Why C is wrong:** Subagents don't "wait" for each other's results; each works with whatever is in its prompt and finishes. Raising `maxTurns` just lets `classify` struggle with an empty list for longer — it doesn't fetch the data.

**Why D is wrong:** A hub-and-spoke violation. Direct subagent-to-subagent communication loses observability; managing the ordering is the coordinator's job.
