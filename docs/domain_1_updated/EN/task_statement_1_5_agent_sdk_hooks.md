# Task Statement 1.5: Agent SDK Hooks

## Domain 1 — Agentic Architecture & Orchestration (27% of Exam)

---

## The Core Idea

In Task Statement 1.4 we learned why programmatic enforcement is necessary. Now we learn **how** it's implemented in the Agent SDK and Claude Code. The answer: **hooks**.

Hooks are pieces of code that run automatically at specific events in the agent's lifecycle. Whatever the model "decides," the hook runs — which is what makes it deterministic. The two hooks the exam focuses on are the ones placed **before** and **after** a tool call.

---

## PreToolUse Hooks (Before the Tool Runs)

When Claude decides to call a tool, this hook intercepts **before the tool executes**.

**Purpose: enforcing business rules (policy enforcement).**

Examples:

- Block refunds over $500 and route them to a human escalation workflow
- Block international transfers unless a compliance check has been performed
- Require manager approval for certain operations
- Prerequisite gate: block `process_refund` until `verify_identity` has completed (Pattern 2 from 1.4)

Decisions the hook can return:

| Output | Effect |
|---|---|
| `permissionDecision: "allow"` | The tool runs (bypassing the permission system) |
| `permissionDecision: "deny"` | The tool **does not run**; `permissionDecisionReason` is passed to Claude |
| `permissionDecision: "ask"` | The user is asked for approval |
| `updatedInput` | The tool runs with modified input (e.g. redirecting a file path into a sandbox, masking PII) |

`permissionDecisionReason` is not decoration: as we saw in 1.4, if the reason for the rejection doesn't reach Claude, the agent can't self-correct. Every `deny` should carry a "do this first" message.

The exam guide refers to this hook as "tool call interception" — you may see either phrase on the exam; the technical name is **`PreToolUse`**.

---

## PostToolUse Hooks (After the Tool Runs)

Intercepts **after** the tool has run, **before** the result reaches Claude.

**Purpose: data normalisation and enrichment.**

Different MCP tools return data in different formats — one gives a Unix timestamp, another ISO 8601. One returns a numeric status code, another a string. A PostToolUse hook converts all these formats into a standard one. Result: Claude always sees clean, consistent data — regardless of which tool produced it.

Outputs the hook can return:

| Output | Effect |
|---|---|
| `updatedToolOutput` | **Replaces** the tool result Claude will see — this is exactly where normalisation happens |
| `additionalContext` | Adds context for Claude without changing the result (e.g. "these dates are in UTC") |

### Exam trap: PostToolUse cannot block

By the time PostToolUse runs, **the tool has already executed**. The refund has already been issued, the transfer has already been sent. This hook can transform the result, log it, or annotate it for Claude — but it cannot undo or block the operation. A "block the risky operation with PostToolUse" option is always wrong; blocking is **PreToolUse**'s job.

---

## Other Hook Events

The exam's core is Pre/PostToolUse, but for "which hook for this job?" questions you should recognise the full list:

| Event | When it fires | Typical use |
|---|---|---|
| `PreToolUse` | Before a tool call | Policy enforcement, prerequisite gates, input correction |
| `PostToolUse` | After a tool runs successfully | Normalisation, enrichment, audit logging |
| `PostToolUseFailure` | When a tool returns an error | Error logging, alerting |
| `UserPromptSubmit` | When the user submits a prompt, before it reaches Claude | Injecting context, blocking prohibited content |
| `Stop` | When the main agent finishes its turn | "Don't finish until tests pass" checks, output validation |
| `SubagentStart` / `SubagentStop` | When a subagent starts / finishes | Logging subagent output, cost tracking |
| `PreCompact` | Before context compaction | Saving critical information before it's compressed |
| `SessionStart` / `SessionEnd` | When a session starts / ends | Environment setup, end-of-session reports |
| `PermissionRequest` | When a tool requires permission | Programmatic permission decisions |
| `Notification` | When a system notification is generated | Forwarding notifications to external systems |

---

## How Hooks Are Defined

There are two forms; both use the same event model.

**Claude Code — `settings.json`:** The hook is a shell command. Event data arrives on stdin as JSON. The decision is communicated in one of two ways: the **exit code** (0 = continue, **2 = block**; the message on stderr is passed to Claude) or JSON written to stdout (the fields above under `hookSpecificOutput`).

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [{ "type": "command", "command": "python3 .claude/hooks/guard.py" }]
      }
    ]
  }
}
```

**Agent SDK — programmatic callback:** The hook is a function; it receives the event data and returns the output structure above.

```python
from claude_agent_sdk import ClaudeAgentOptions, HookMatcher

options = ClaudeAgentOptions(
    hooks={
        "PreToolUse": [HookMatcher(matcher="process_refund", hooks=[refund_gate])],
        "PostToolUse": [HookMatcher(matcher="mcp__crm__.*", hooks=[normalize_dates])],
    }
)
```

The **matcher** concept matters: it determines which tools the hook applies to (a tool name or a regex). Without a matcher, the hook runs on every tool call — unnecessary latency and the risk of blocking by accident. On the exam, the answer to "the hook is slowing down every tool" is to narrow the matcher.

---

## Decision Framework

| Approach | Guarantee | Use case |
|---|---|---|
| **Not granting the tool at all** (`allowedTools` / `disallowedTools`, permission modes) | Deterministic | When the agent should **never** perform that operation — the simplest solution |
| **Hooks** | Deterministic | The operation is permitted but **conditional** — business rules, compliance, prerequisites, normalisation |
| **Prompts** | Probabilistic | Preferences, style rules, soft guidance |

> **If a single failure creates monetary loss or legal risk → a hook (or don't grant the tool at all).**

Exam nuance: a hook is not always the best answer. If the agent should never call a tool under any circumstances, removing it from `allowedTools` is simpler and safer than writing a hook. Hooks are for conditional rules — "sometimes yes, sometimes no."

---

## Key Exam Takeaways

| Concept | Remember |
|---|---|
| `PreToolUse` | Before the tool runs — `allow` / `deny` / `ask` / `updatedInput`; blocking happens here |
| `PostToolUse` | After the tool runs — normalisation via `updatedToolOutput`, enrichment via `additionalContext`; **cannot block** |
| `permissionDecisionReason` | Goes with every `deny` — so the agent can self-correct |
| Other events | `Stop` (completion checks), `SubagentStop` (subagent logging), `PreCompact`, `UserPromptSubmit`, `PostToolUseFailure` |
| Definition | `settings.json` (shell, exit code 2 = block) or an SDK callback; narrow the scope with a **matcher** |
| Hook = deterministic | Business rules, compliance, financial controls |
| Prompt = probabilistic | Sufficient for preferences and soft rules |
| Simplest deterministic solution | If the tool is never needed, remove it from `allowedTools` — don't write a hook |

---

## Practice Scenario 1

> An agent occasionally processes international transfers with the `send_transfer` tool without running the required compliance checks (the `compliance_check` tool). This creates regulatory risk.
>
> **What is the correct solution?**
>
> **A)** Add the instruction "always call compliance_check before an international transfer" to the system prompt and reinforce it with 3 example conversations.
>
> **B)** Add a `PostToolUse` hook on `send_transfer` that blocks the operation if the transfer is international and no compliance check was performed.
>
> **C)** Add a `PreToolUse` hook on `send_transfer` that returns `permissionDecision: "deny"` with the reason "call compliance_check first" if the transfer is international and `compliance_check` has not completed successfully.
>
> **D)** Remove the `send_transfer` tool from `allowedTools`; have humans handle all transfers.

### Correct Answer: C

**Why C is correct:** Regulatory risk = a single failure has legal consequences; a deterministic guarantee is required. The `PreToolUse` hook intercepts **before the transfer happens**, checks the condition, and blocks the call if it isn't met. Because the rejection reason is passed to Claude, the agent calls the compliance check and then completes the transfer in the correct order.

**Why A is wrong:** Prompt instructions and few-shot examples are probabilistic — they raise the success rate (say from 92% to 97%) but can't guarantee 100%. Even one unchecked transfer carries penalty risk.

**Why B is wrong:** `PostToolUse` runs **after** the tool executes — the transfer has already been sent. This hook can transform or log the result but cannot block the operation. A classic exam trap.

**Why D is wrong:** Removing the tool entirely is deterministic but disproportionate — it also blocks domestic transfers and transfers that have passed the compliance check. The rule is conditional ("block if the check wasn't done"), which is exactly what hooks are for.

---

## Practice Scenario 2

> A code review agent pulls data from three MCP servers (GitHub, Jira, a CI system). Each returns timestamps in a different format (Unix epoch, ISO 8601, "2 hours ago"). The agent gives inconsistent answers to "which change is the most recent?" questions.
>
> The team adds a `PostToolUse` hook, but the hook only returns a note via `additionalContext`: "dates may be in different formats, be careful." The inconsistency persists.
>
> **What is the most effective fix?**
>
> **A)** Move the hook to `PreToolUse` and add a "return ISO 8601" parameter to the tool inputs.
>
> **B)** The hook should convert all timestamps to ISO 8601 via `updatedToolOutput` instead of `additionalContext` — fix the data rather than telling Claude to "be careful."
>
> **C)** Modify the source code of the three MCP servers so they all return the same format.
>
> **D)** Add a reference table explaining the date formats to the system prompt.

### Correct Answer: B

**Why B is correct:** `additionalContext` informs Claude but still leaves the conversion to the model — that's a probabilistic solution that wastes the hook's deterministic power. `updatedToolOutput` **replaces** the tool result before it reaches Claude: every timestamp is converted to ISO 8601 in code, and Claude only ever sees consistent data. Normalisation is a job for code, not for the model.

**Why A is wrong:** `PreToolUse` modifies the input, not the output. You can't assume third-party MCP tools have a "return ISO 8601" parameter; the output format isn't under your control, but transforming the output is.

**Why C is wrong:** Modifying third-party servers usually isn't possible; even when it is, it leaves control with an external dependency. Normalisation should happen at your boundary.

**Why D is wrong:** Prompt-based guidance — probabilistic. It's another form of the approach already tried with `additionalContext`, and insufficient for the same reason.
