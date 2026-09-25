# Task Statement 1.4: Workflow Enforcement and Handoff

## Domain 1 — Agentic Architecture & Orchestration (27% of Exam)

---

## The Core Idea

Agentic loops, multi-agent orchestration, context passing — all of these rely on Claude making **flexible** and **intelligent** decisions. But some decisions can't be left to flexibility. Some rules must be applied **every single time, without exception**.

That is exactly what this task statement teaches: **when do you trust Claude, and when do you enforce programmatically?**

---

## The Enforcement Spectrum

There are two approaches:

### Prompt-Based Guidance (Probabilistic)

You write an instruction in the system prompt — "Always verify the customer first." This works most of the time. But it's not a 100% guarantee. Claude can sometimes skip it. There is always a non-zero failure rate.

### Programmatic Enforcement (Deterministic)

You write a gate in code — a **prerequisite gate** that checks whether the `verify_identity` tool has completed successfully before the refund tool is called. If verification hasn't happened, the refund tool physically cannot run. Because the rule lives in code, it doesn't depend on the model "remembering."

---

## How a Prerequisite Gate Is Implemented — Two Patterns

The exam guide's Skills item: *"Implementing programmatic prerequisites blocking downstream tool calls."* There are two ways to implement this; you should know which applies given the context of an exam scenario.

### Pattern 1: A tool dispatcher gate in your own agentic loop (Messages API)

If you're executing the tool calls yourself (the loop from 1.1), the enforcement point is the tool dispatcher. You hold the state; if the prerequisite isn't met, you don't run the tool — you return an **explanatory error with `is_error: true`** to Claude.

```python
state = {"verified_customer_id": None}

def dispatch(block):
    if block.name == "verify_identity":
        result = verify_identity(**block.input)
        if result["ok"]:
            state["verified_customer_id"] = result["customer_id"]
        return tool_result(block.id, result)

    if block.name == "process_refund":
        if state["verified_customer_id"] is None:              # GATE
            return tool_result(
                block.id,
                "Rejected: verify_identity must complete successfully before "
                "process_refund is called. Verify the customer's identity first.",
                is_error=True,
            )
        return tool_result(block.id, process_refund(**block.input))
```

### Pattern 2: A `PreToolUse` hook in the Agent SDK / Claude Code

If the Agent SDK or Claude Code is running the loop, you use the `PreToolUse` hook, which intercepts **before** the tool call executes. The hook blocks the call by returning `permissionDecision: "deny"` and passes the reason to Claude via `permissionDecisionReason`. (The hook mechanism is covered in detail in Task Statement 1.5.)

```python
async def refund_gate(input_data, tool_use_id, context):
    if input_data["tool_name"] == "process_refund" and not state["verified_customer_id"]:
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason":
                    "verify_identity must complete successfully before process_refund.",
            }
        }
    return {}
```

What the two patterns share: **the rule lives in code, not in the prompt.** The only difference is who runs the loop.

### What "zero failures" means — and what it doesn't

The gate drives **rule violations** to zero: a refund *cannot happen* without verification. But the gate alone doesn't guarantee that Claude completes the task correctly. If the **reason** for the blocked call isn't fed back to Claude (an empty error or a silent rejection), Claude doesn't understand what it should do — it repeats the same call, gives up, or says "I can't process refunds." That's why in both patterns the rejection message must be **actionable**: what was blocked and **what must happen first**. Gate + explanatory rejection = deterministic rule + self-correcting agent.

---

## The Exam's Decision Rule

This is very clear and tested repeatedly:

- **If the consequences are financial, security-related, or compliance-related** → **Programmatic enforcement.** Always.
- **If the consequences are low-risk** (format preferences, style rules, tone) → Prompt-based guidance is sufficient.

The test is this question: **Does a single failure create monetary loss, a security breach, or legal risk?** If yes, a prompt is not enough.

> The exam will offer prompt-based solutions as options in high-risk scenarios — "strengthen the instruction," "put it in bold," "add few-shot examples," "repeat it 3 times." They're all in the same category: probabilistic. **Reject them.**

There's a reverse trap too: writing a hook for a low-risk preference (e.g. "answer with bullet points") is over-engineering. The right answer isn't always "hook" — the right answer is the one proportionate to the risk.

---

## Multi-Concern Request Handling

When a customer reports multiple issues at once:

1. **Decompose** the request into distinct issues
2. Investigate each **in parallel** with shared context
3. Synthesise a single **unified resolution**

Example: *"My package still hasn't arrived, I've also been billed the wrong amount, and now I want to close my account."*

- Decomposition: (a) delivery delay, (b) billing error, (c) account closure request — three independent items.
- Parallel investigation: shipment tracking, the invoice record, and account status are queried simultaneously with the same customer context (customer ID, order number).
- Unified response: address all three in a single, coherent message — not three separate replies.

When parallel does **not** apply: when the items depend on each other. For example, if account closure can't happen while a refund is open, item (c) depends on (b) — refund first, then closure. Decomposition still happens, but execution order follows the dependency (the parallel/sequential rule from 1.3).

Common failure: the agent handles only the first issue and forgets the rest. The decomposition step prevents this — every item is listed explicitly, and the response isn't considered complete until each one has an outcome.

---

## Structured Handoff Protocols

Sometimes the agent can't resolve the issue and must escalate to a human representative. The critical rule for this handoff:

> **Assume the human representative cannot access the conversation transcript.** The handoff summary must be self-contained — the human should be able to read it and carry on without looking at anything else.

What the handoff summary must include:

- **Customer identity** (customer ID) and verification status (was identity verified, and how)
- **Conversation summary** — what happened, what the customer asked for
- **Root cause analysis** — what caused the issue (or why it couldn't be determined)
- **Actions taken so far** — which tools were called, what was tried, what the outcomes were. Critical so the human doesn't retry the same things or ask the customer the same questions again.
- **Refund / transaction amount** (if applicable)
- **Why it was escalated** — outside the agent's authority, ambiguity, or customer request
- **Recommended action** — what the human representative should do

The handoff summary should be **structured**, not free text (fixed fields, ideally JSON) — the structured context passing principle from 1.3 applies here too. It may be consumed by a human, another system, or another agent.

---

## Key Exam Takeaways

| Concept | Remember |
|---|---|
| Prompt-based guidance | Probabilistic — works most of the time, no guarantee |
| Programmatic enforcement | Deterministic — the rule lives in code via a prerequisite gate |
| Two implementation patterns | Dispatcher gate in your own loop (reject with `is_error`) / `PreToolUse` hook in the Agent SDK (`permissionDecision: deny`) |
| Rejection message | Must be actionable — what was blocked + what to do first; otherwise the agent gets stuck |
| Decision rule | Financial / security / compliance → programmatic. Low risk → prompt is enough. Be proportionate to the risk |
| Multi-concern requests | Decompose → investigate independent items in parallel → dependent ones in order → one unified resolution |
| Handoff protocol | Self-contained, structured summary: customer ID, summary, root cause, **actions taken**, amount, escalation reason, recommended action |
| Exam trap | "Strengthen the prompt / add few-shot / repeat it" is a distractor at high risk; a hook is over-engineering at low risk |

---

## Practice Scenario 1

> Production data shows that in 8% of cases, a customer support agent processes a refund without verifying account ownership. This sometimes leads to refunds being issued to the wrong accounts.
>
> **How do you fix this?**
>
> **A)** Add a programmatic prerequisite gate that requires the `verify_identity` tool to have completed successfully before the refund tool can run.
>
> **B)** Strengthen the system prompt: add the instruction "Never process a refund without identity verification" and emphasise it in bold.
>
> **C)** Add few-shot examples — 3-4 example conversations showing the correct sequence.
>
> **D)** Add a routing classifier that directs refund requests into a verification flow first.

### Correct Answer: A

**Why A is correct:** This is an operation with financial consequences — refunds are going to the wrong accounts. It requires a deterministic guarantee. A programmatic prerequisite gate physically prevents the refund tool from running until `verify_identity` has completed. Rule violations drop to zero.

**Why B is wrong:** Strengthening the prompt is probabilistic — it might raise the rate from 92% to 97%, but it can't guarantee 100%. There's already an 8% failure rate, which is proof that the prompt isn't sufficient. The financial risk remains.

**Why C is wrong:** Few-shot examples are also prompt-based guidance. They *steer* the model's behaviour but don't *enforce* it. Same problem — not deterministic.

**Why D is wrong:** A routing classifier moves the problem somewhere else but doesn't solve it. The classifier can also make mistakes. And the real issue: the refund tool can still be called without verification. No gate, no guarantee.

---

## Practice Scenario 2

> To fix the problem from Scenario 1, a team adds a `PreToolUse` hook that blocks `process_refund` calls. The hook returns `permissionDecision: "deny"` when `verify_identity` hasn't completed — and returns nothing else.
>
> Wrong-account refunds drop to zero. But a new complaint begins: in many conversations the agent now tells the customer "I can't process a refund right now, please try again later," and never attempts identity verification at all.
>
> **What is the problem?**
>
> **A)** The hook is too strict — it should return `ask` instead of `deny` so refunds can proceed with human approval.
>
> **B)** The hook blocks the call but doesn't tell Claude **why** it was blocked. It should provide "call `verify_identity` first" via `permissionDecisionReason`, so the agent can self-correct and follow the right sequence.
>
> **C)** The gate approach doesn't suit this scenario — revert to the system prompt and strengthen the verification instruction.
>
> **D)** The `process_refund` tool should be removed from the agent entirely; refunds should always be handled by a human.

### Correct Answer: B

**Why B is correct:** The gate is working correctly — zero rule violations. What's missing is the feedback. Seeing a silent rejection, Claude doesn't know what to do and concludes "I can't process refunds." If the rejection message is actionable ("verify_identity must complete successfully before process_refund"), the agent calls verification, then processes the refund. The deterministic rule is preserved and the task gets done.

**Why A is wrong:** `ask` requests human approval; it doesn't make the rule any less deterministic, but it ties every refund to a human — it doesn't scale, and it doesn't fix the real problem (the agent not knowing why it was blocked).

**Why C is wrong:** Reverting to the prompt means going back to the 8% failure rate from Scenario 1. The problem isn't the gate, it's the gate's communication.

**Why D is wrong:** Removing the tool destroys the agent's function. The goal isn't to prohibit refunds but to guarantee they happen in the right order — which the gate already does.
