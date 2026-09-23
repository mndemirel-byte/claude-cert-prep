# Task Statement 1.1: Agentic Loops

## Domain 1 — Agentic Architecture & Orchestration (27% of Exam)

---

## The Core Idea

Normally, when you use Claude, it's a single exchange: you send a message, you get a response, done. An **agentic loop** turns Claude into something that can *act* — it can call tools, look at the results, think again, call more tools, and keep going until the job is finished.

Think of it like hiring a research assistant. You don't just ask them a question and get one answer. They go and look things up, come back with what they found, decide they need more information, go look up something else, and eventually come back with a complete answer. That's an agentic loop.

---

## The Lifecycle — Step by Step

Here's exactly how it works in code:

**Step 1:** You send a request to Claude via the Messages API. This includes a system prompt (the agent's instructions) and the conversation history.

**Step 2:** Claude responds. Every response has a field called `stop_reason`. This is the single most important field in agentic systems. It tells you *why Claude stopped generating*.

**Step 3:** You check `stop_reason`:

- If it's `"tool_use"` → Claude wants to use a tool. It's saying "I need to do something before I can give you a final answer." You execute the tool, take the result, **append it to the conversation history**, and send the whole thing back to Claude. Loop back to Step 2.
- If it's `"end_turn"` → Claude is finished. Present the response to the user. Exit the loop.

That's it. The entire agentic loop is: **send → check stop_reason → either execute tools and loop, or finish.**

The key detail: when you get tool results, you don't just send the results back in isolation. You append them to the full conversation history. Claude needs to see everything that's happened so far — its own previous reasoning, the tool calls it made, and now the results — so it can decide what to do next.

---

## The Three Anti-Patterns (Exam Traps)

The exam tests whether you know the **wrong** ways to control this loop. There are three, and you need to reject them instantly when you see them in answer options.

### Anti-pattern 1: Parsing Natural Language to Decide Completion

Checking if Claude's response contains the phrase "I'm done" or "Here's your final answer." This is unreliable because natural language is ambiguous — Claude might say "I'm done searching" but still need to synthesise results. The `stop_reason` field exists precisely so you don't have to guess from the text.

### Anti-pattern 2: Arbitrary Iteration Caps as the Primary Stopping Mechanism

For example, "stop after 10 loops no matter what." This is wrong because it either cuts off useful work (what if loop 11 was the important one?) or wastes time running unnecessary iterations. Claude signals when it's done via `stop_reason`. Iteration caps can be a *safety net*, but they should never be the primary control mechanism.

### Anti-pattern 3: Checking for Text Content as a Completion Signal

For example: `if response.content[0].type == "text": we're done`. This is a trap because **Claude can return text AND tool calls in the same response.** It might say "I found some initial results, let me now check the database" — that response has text *and* a tool_use block. If you stop because you saw text, you've terminated prematurely.

---

## Model-Driven vs Pre-Configured Decision-Making

In an agentic loop, **Claude decides** which tool to call and when, based on the context. You don't write a script that says "first call tool A, then tool B, then tool C." You give Claude access to tools and let it reason about which ones it needs.

The exam favours this model-driven approach for flexibility. However — when there are critical business rules (like "always verify identity before issuing a refund"), you enforce those programmatically, not by hoping Claude remembers. (Covered in detail in Task Statement 1.4.)

---

## Key Exam Takeaways

| Concept | Remember |
|---|---|
| `stop_reason` | The **only** reliable termination signal for the agentic loop |
| `"tool_use"` | Execute the tool, append result to history, send back to Claude |
| `"end_turn"` | Agent is finished — present the final response |
| Conversation history | Tool results must be **appended** to the full history, not sent in isolation |
| Anti-patterns | Never use natural language parsing, iteration caps, or content-type checks as the primary stopping mechanism |

---

## Practice Scenario

> A developer has built an agent that helps users research topics. The agent has access to a web search tool. The developer's loop logic checks `response.content[0].type == "text"` to determine when the agent has finished — if it finds text, it exits the loop and presents the response to the user.
>
> Users report that the agent frequently gives incomplete answers, often stopping after a single search when it should be doing further research.
>
> **What is the bug, and how should it be fixed?**

### Correct Answer

**Root Cause:** Claude can return text AND `tool_use` blocks in the same response. The developer's logic checks `content[0].type == "text"` and treats it as a completion signal. But Claude often returns a text block (e.g., "I found some initial results, let me search for more details") *alongside* a `tool_use` block in the same response. The loop sees the text, assumes the agent is done, and exits prematurely — even though Claude was still mid-task.

**The Fix:**

`stop_reason` is not inside the response text. It's a separate field on the response object itself. Think of the response as having two distinct parts:

- `response.content` → the actual content (text blocks, tool_use blocks, or both)
- `response.stop_reason` → a structured field that tells you *why* Claude stopped generating

The fix is to replace the content-type check with a `stop_reason` check:

- `stop_reason == "tool_use"` → Claude needs to use tools. Execute them, append results, loop again.
- `stop_reason == "end_turn"` → Claude is genuinely finished. Exit the loop.

```python
# WRONG — unreliable, causes premature termination
if response.content[0].type == "text":
    return response

# CORRECT — stop_reason is the only reliable signal
if response.stop_reason == "end_turn":
    return response
elif response.stop_reason == "tool_use":
    # execute the requested tool(s)
    # append tool results to conversation history
    # send updated conversation back to Claude
```

**Key Principle:** `stop_reason` is a **structured field on the response object**, not part of the response text. It is the only reliable mechanism for determining whether the agentic loop should continue or terminate.
