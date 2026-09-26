# Task Statement 2.3: Tool Distribution & tool_choice

## Domain 2 — Tool Design & MCP Integration (18% of the exam)

---

## Core Idea

How many tools do you give an agent? All of them, or only the ones it needs? And should the model decide whether to call a tool, or should you force it? This task statement answers exactly those two questions.

---

## The Tool Overload Problem

Give an agent 18 tools and selection reliability drops. Every extra tool raises decision complexity; Claude struggles to decide which tool to use when. Anthropic's own measurement: selection accuracy degrades noticeably beyond 30–50 tools; a typical multi-server MCP setup (GitHub + Slack + Sentry + Grafana + Splunk) loads ~55k tokens of tool definitions before any work begins.

**Optimal:** **4–5 tools** per agent, scoped to its role.

The core rule: **Each agent should have only the tools its role requires.**

- A synthesis agent should not have web-search tools — out-of-role tools get **misused** (the synthesis agent starts searching instead of synthesizing)
- A web-search agent should not have document-analysis tools
- Each agent should have a focused tool set for its own job

The official term: **principle of least privilege** — each agent gets the narrowest tool set sufficient for its job.

### How it is applied in Claude Code / the Agent SDK

Tool distribution is not an abstract principle; it is a field in the subagent definition:

```markdown
---
name: synthesis-agent
description: Turns findings into a single report
tools: Read, Write, verify_fact
---
```

- `tools` (allowlist) or `disallowedTools` (blocklist) in the `.claude/agents/*.md` frontmatter
- `AgentDefinition.tools` / `disallowedTools` in the Agent SDK
- MCP tools are listed by their `mcp__<server>__<tool>` name (`mcp__github__create_issue`)
- If `tools` is omitted, the subagent inherits all of the coordinator's tools — **the default is "everything"; narrow it deliberately**

(See Domain 1.3 — Subagent Invocation.)

### Current note (does not change the exam answer)

Anthropic also shipped an API-level answer to the many-tools problem: the **Tool Search Tool**. Tools are marked `defer_loading: true`; Claude searches with `tool_search_tool_regex` / `tool_search_tool_bm25` and loads only the 3–5 tools it needs, cutting tool-definition context by 85%+. Recommended threshold: 10+ tools or 10k+ tokens of definitions. It is not in the exam guide; **the exam answer is still "distribute by role, 4–5 per agent"** — this note explains where the "18 → 4–5" number comes from.

---

## tool_choice Configuration

There are **four** values — the exam expects you to tell them apart:

### 1. `"auto"` (default when tools are provided)
The model decides **itself** whether to call a tool. It may answer with plain text instead of a tool call.

**When to use:** General operation. Sufficient in most cases.

### 2. `"any"`
The model **must** call a tool, but chooses which one. It cannot return conversational text.

**When to use:** When you want **guaranteed structured output** in one of several schemas — "answer me with one of these three JSON schemas, not prose."

### 3. `{"type": "tool", "name": "extract_metadata"}`
The model **must** call this specific tool. No choice.

**When to use:** To enforce mandatory first steps. For example, requiring metadata extraction before enrichment steps.

### 4. `"none"` (default when no tools are provided)
The model may call **no** tool; it produces text only. The tools stay defined but are switched off for this turn.

**When to use:** When you keep sending tool definitions on every request (to preserve the prompt cache) but want text only on a specific turn — e.g. the final summary turn, a "write the explanation for the user" step.

### Summary Table

| Value | Behavior | Use case | Exam hint |
|---|---|---|---|
| `"auto"` | Model decides — tool or text | General operation | Default; "the model deciding is fine" |
| `"any"` | Must call a tool, picks which | Guaranteed structured output | "I don't want prose, one of the schemas" |
| `{"type":"tool","name":"X"}` | Must call the named tool | Mandatory first step | "Forced on turn 1, **`auto` on later turns**" |
| `"none"` | Calls no tool | Text-only turn | "Tools defined but off this turn" |

### Switching back to `auto` after a forced call — EXAM TRAP

The exam guide's Skills bullet reads exactly: *"Using tool_choice forced selection to ensure a specific tool is called **first, then processing subsequent steps in follow-up turns**."*

`tool_choice` works **per request**. You send the first request with `{"type":"tool","name":"extract_metadata"}`, the model calls `extract_metadata`, you append the `tool_result`. **If you don't switch `tool_choice` to `auto` on the second request**, the model is forced to call `extract_metadata` again — it never reaches the enrichment steps and loops on metadata forever.

```python
# Turn 1: mandatory first step
r1 = client.messages.create(..., tools=tools,
        tool_choice={"type": "tool", "name": "extract_metadata"})
messages += [assistant(r1.content), user(tool_results(r1))]

# Turn 2+: give the model freedom
r2 = client.messages.create(..., tools=tools, tool_choice={"type": "auto"})
```

Exam scenario: "We added a mandatory metadata step, but now the agent never gets to analysis; it keeps extracting metadata." → Answer: the forced `tool_choice` was not switched back to `auto` on subsequent turns.

### Additional nuances

- **`disable_parallel_tool_use: true`** — under `auto`, Claude may return several `tool_use` blocks in one response. This flag limits the response to at most one tool call; combined with `any`/`tool` it guarantees **exactly one** call. A natural part of the "mandatory first step" pattern. (See Domain 1.1 — parallel tool calls.)
- **Thinking with `any`/`tool`:** In forced tool use the assistant message is prefilled; the model emits no thinking/text block before the tool_use. Manual extended thinking (`thinking: {"type": "enabled"}`) **cannot be combined** with `any`/`tool` — the API returns an error. If you need thinking, use `auto`.
- **Current note (does not change the exam answer):** The newest models (Opus 5.5, Fable 5.1, Mythos 5.1) do not support `any` and `tool` (400 error); the alternative is `auto` + strict tool use, or structured outputs. **The exam guide treats `auto` / `any` / forced as valid; on the exam they are the correct answers.**

---

## Scoped Cross-Role Tools — EXAM QUESTION

This pattern is the exam guide's official sample question (Q9). Learn the scenario, the fix, **and every distractor**.

### Problem

A synthesis agent frequently hands control back to the coordinator for simple fact verification; the coordinator invokes the web-search agent, the result comes back, synthesis restarts. Each time adds 2–3 round trips and total latency rises **40%**. **85%** of verifications are simple lookups (dates, names, statistics); **15%** need deeper investigation.

### Fix: a Scoped verify_fact Tool

Give the synthesis agent a **scoped `verify_fact` tool** — it can only do simple lookups. Complex verifications still go through the coordinator to the web-search agent.

**Result:**
- The coordinator round trip disappears for 85% of cases
- The remaining 15% still flows through the coordinator — architectural integrity preserved
- Official rationale: **principle of least privilege** — the synthesis agent gets *just enough* for the 85% common case, no more

### Why the Other Fixes Are Wrong (including Q9's real distractors)

| Fix | Why wrong |
|---|---|
| **Accumulate verifications, send them to the coordinator as a batch at the end of the pass** (Q9 option B) | *Batches* the latency instead of removing it — at least one extra round trip remains. Worse: the synthesis agent keeps writing on unverified claims, then has to go back and fix them; paragraphs built on a wrong claim get rewritten. |
| **Give the synthesis agent all web-search tools** (Q9 option C) | Too much authority — out-of-role tools get misused; the synthesis agent starts researching, its role blurs. The web-search agent's expertise is lost for the 15% deep cases. Violates least privilege. |
| **Have the web-search agent proactively cache extra context around every source** (Q9 option D) | Speculative — you can't know in advance what will need verifying; context bloats, cost rises, and the 15% deep cases still aren't solved. |
| Run the coordinator on a faster model | Doesn't remove the structural latency — the round trip is still there. |
| Remove the verification step | Loss of functionality — verification is a quality step. |
| Give the synthesis agent a full `fetch_url` | Too broad — security risk, loss of focus. |

---

## Replacing Generic Tools with Constrained Alternatives

Instead of giving subagents general-purpose tools, give them constrained alternatives:

- ❌ `fetch_url` — can fetch any URL, security risk (prompt-injection surface, data exfiltration)
- ✅ `load_document` — validates and fetches only approved document URLs

- ❌ `run_sql` — runs any query
- ✅ `get_order_by_id` — a single-parameter, read-only query

Safer, more focused, less error-prone. This is the *scope* dimension of least privilege (distribution above was the *count* dimension).

---

## Key Takeaways for the Exam

| Concept | Remember |
|---|---|
| Tool overload | 18 tools = selection reliability drops. Optimal: 4–5 per agent, by role |
| Out-of-role tools | Get misused (synthesis agent searches) → don't grant them |
| Least privilege | Narrowest set sufficient for the job — in **count and scope** |
| How it's applied | Subagent `tools` / `disallowedTools`; MCP tools as `mcp__server__tool` |
| `"auto"` | Default — model picks tool or text |
| `"any"` | Must call a tool, picks which — guaranteed structured output |
| `{"type":"tool","name":"X"}` | Forces a specific tool — mandatory first step; **switch to `auto` next turn** |
| `"none"` | No tools this turn, text only |
| `disable_parallel_tool_use` | One tool call per response; with `any`/`tool`, "exactly one" |
| Thinking + forced | Manual extended thinking can't be combined with `any`/`tool` |
| Scoped cross-role tools | Narrow tool for high-frequency simple needs; complex cases via the coordinator |
| Constrained alternatives | `load_document` instead of `fetch_url` — security and focus |

---

## Practice Scenario

> A synthesis agent frequently needs to verify claims while writing the final report. For each verification it hands control to the coordinator, the coordinator invokes the web-search subagent, the result comes back. This adds 2–3 round trips per task and raises total latency by 40%. 85% of verifications are simple "is X true?" lookups; 15% require deep investigation.
>
> **What is the most effective way to reduce latency while maintaining system reliability?**
>
> **A)** Give the synthesis agent a scoped `verify_fact` tool — simple lookups are resolved in the agent directly, complex verifications continue to flow through the coordinator to the web-search agent.
>
> **B)** Have the synthesis agent accumulate all verification needs and return them as a batch to the coordinator at the end of its pass; the coordinator sends them all to the web-search agent at once.
>
> **C)** Give the synthesis agent access to all web-search tools — it handles every verification itself without going through the coordinator.
>
> **D)** Have the web-search agent proactively cache extra context around each source during initial research — anticipating what the synthesis agent might need to verify.

### Correct Answer: A

**Why A is correct:** 85% of cases are simple lookups — going through the coordinator for those is needless latency. The scoped `verify_fact` tool resolves simple verifications in the agent; the 15% complex ones still flow coordinator → web-search agent. Least privilege: the synthesis agent gets *just enough* for the common case. Latency drops, architectural integrity is preserved.

**Why B is wrong:** Batching *accumulates* latency rather than removing it — at least one extra round trip remains. The synthesis agent also keeps writing on unverified claims; when the results arrive it must rewrite sections built on wrong claims. Quality and latency can both get worse.

**Why C is wrong:** All web-search tools is too much authority. Out-of-role tools get misused — the synthesis agent starts researching, its role blurs. The 15% deep cases lose the web-search agent's expertise. A least-privilege violation.

**Why D is wrong:** Speculative — which claims will need verification can't be known in advance. Context bloats, cost rises; the 15% deep cases still go to the coordinator. Adds cost without solving the problem.
