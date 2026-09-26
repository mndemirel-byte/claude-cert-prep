# Task Statement 3.4: Plan Mode vs Direct Execution

## Domain 3 — Claude Code Configuration & Workflows (20% of the exam)

---

## Core Idea

When you give Claude Code a task there are two basic modes: **plan mode** (think first, then do) and **direct execution** (do it now). The exam expects you to know which one to use when.

The first thing to know: **plan mode is a *permission mode*.** It is part of the mode cycle that determines what Claude may do (`default` → `acceptEdits` → `plan`) (see Domain 1.4 and Task 3.6). "Direct execution" is not a separate mode; it is simply *not being* in plan mode.

---

## Plan Mode — Think First, Then Do

In plan mode Claude Code **researches and proposes changes but doesn't make them**: it reads files, runs exploratory commands, writes a plan — **it does not edit source**. Edits stay blocked until you approve the plan.

### Mechanism (the layer the exam doesn't ask about but study material skips)

| Step | How |
|---|---|
| Enter plan mode | `Shift+Tab` (cycle modes until `⏸ plan mode on`) · `/plan` prefix for a single prompt · `claude --permission-mode plan` · project default via `.claude/settings.json` → `"permissions": {"defaultMode": "plan"}` |
| Exploration | Claude delegates to the built-in **Plan** and **Explore** subagents — file reads don't bloat the main context |
| Plan | Claude presents the plan; `Ctrl+G` opens it in your editor for direct edits |
| Approval | **Yes, and use auto mode** (or *Yes, auto-accept edits* if auto is off) · **Yes, manually approve edits** · **No, keep planning** |
| Result | **Approval = exit plan mode + start implementing in the permission mode you chose.** To plan again: `Shift+Tab` or `/plan` |

> What study material calls the "hybrid approach" (plan → direct execution) is not a separate technique; it is plan mode's **normal lifecycle**: plan → approve → implement.

### When to Use It

- **Complex tasks** — large-scale changes
- **Multiple valid approaches** exist — you need to evaluate which is best
- **Architectural decisions** are needed (service boundaries, module dependencies)
- **Multi-file modifications** — e.g. a library migration affecting 45+ files
- **Exploration is required** — understand and design before changing anything
- **Unfamiliar code** — avoids solving the wrong problem ("preventing costly rework")
- Choosing between **integration approaches with different infrastructure requirements**

### Examples

| Task | Plan mode? | Why? |
|---|---|---|
| Restructure a monolith into microservices | ✅ Yes | Architectural decision, many approaches (exam guide Q5) |
| Replace the logging library in 45 files | ✅ Yes | Multi-file, impact analysis first |
| Understand and restructure a legacy codebase | ✅ Yes | Exploration needed, design needed |
| Choose between two integration approaches (webhook vs polling; different infra) | ✅ Yes | Multiple valid approaches, infrastructure impact |

---

## Direct Execution — Do It Now

In direct execution Claude Code goes **straight to implementation** without planning.

### When to Use It

- **Well-understood changes** — clear and limited scope
- **Single-file bug fix** — with a clear stack trace
- **Simple addition** — like adding a date validation conditional to one function
- **The right approach is already known** — no exploration or comparison needed

### The Official Heuristic

> **"If you could describe the diff in one sentence, skip the plan."**
> Plan mode adds value but **adds overhead**. Fixing a typo, adding a log line, renaming a variable → direct.

### Examples

| Task | Direct? | Why? |
|---|---|---|
| Fix a null pointer in one function (stack trace available) | ✅ Yes | Clear bug, single file, clear fix |
| Add validation to a date field | ✅ Yes | Limited scope, clear requirement |
| Add setup steps to the README | ✅ Yes | Simple addition |
| Off-by-one bug, error message available | ✅ Yes | The diff fits in one sentence |

---

## The Explore Subagent

In multi-phase tasks the **Explore subagent** comes into play:

- A built-in subagent; Claude uses it on its own when needed, and you can trigger it with "use a subagent to investigate X"
- **Read-only:** the Write and Edit tools are denied — Explore *cannot make changes*, it only explores
- Isolates **verbose discovery output** from the main conversation; returns a **summary**
- **Prevents context window exhaustion** — the fix for the "infinite exploration" anti-pattern
- Claude specifies a thoroughness level: *quick* / *medium* / *very thorough*
- Plan mode automatically uses Explore and the **Plan** subagent (also read-only) for discovery

Think of Explore as someone who goes off and does the research for you, then reports only the important findings — not all the raw data.

### When to Use It

- When the codebase needs to be explored and understood
- When many files will be inspected
- When you want to preserve the main conversation's context (link to Domain 5.1)

> **Exam trap:** The option "fix the 25 files with the Explore subagent" is wrong — Explore is read-only. The subagent that makes changes is `general-purpose`.

---

## The Combination Pattern (Hybrid Approach)

The most-tested approach in practice and on the exam:

1. Research and design in **plan mode** (discovery in the Explore/Plan subagents)
2. **Approve** the plan → the mode switches
3. Implement the planned approach with **direct execution**

Combining the two is a common and expected pattern — and mechanically it *is* plan approval.

### Example Flow

```
Task: migrate 30 files from log4j to SLF4J

Step 1 (plan mode — Shift+Tab):
- Discover the affected files (Explore subagent)
- Analyze import patterns
- Identify configuration differences
- Produce a migration plan → review with Ctrl+G

Step 2 (approval → direct execution):
- "Yes, manually approve edits" (or auto-accept)
- Update files per the plan
- Replace imports
- Update configuration files
- Run the tests (verification)
```

> **Tip (best practices):** For large plans, implementing the plan/spec in a **fresh session** gives clean context; the `showClearContextOnPlanAccept` setting adds a "clear context on approval" option.

---

## Decision Table

| Task characteristics | Mode | Rationale |
|---|---|---|
| Complex, many approaches | **Plan mode** | Evaluation needed |
| Multi-file change | **Plan mode** | Impact analysis first |
| Architectural decision | **Plan mode** | Design needed |
| Exploration needed / unfamiliar code | **Plan mode** | Understand first, then act |
| Single file, clear bug | **Direct** | Clear fix, do it now |
| Simple addition, limited scope | **Direct** | Planning unnecessary |
| Approach already known | **Direct** | Evaluation unnecessary |
| The diff fits in one sentence | **Direct** | Plan is overhead |
| Research + implementation | **Hybrid** | Plan → approve → direct execution |

---

## The Exam's Real Distractors (Exam Guide Q5)

The wrong options of the monolith → microservices question teach more than the "plan mode" answer:

| Option | Why wrong |
|---|---|
| "Start with direct execution and iterate; let the implementation reveal the service boundaries" | Dependencies discovered late → **costly rework** |
| "Use direct execution with comprehensive upfront instructions for each service" | Assumes you already know the right structure without exploring the code |
| **"Begin in direct execution and only switch to plan mode if you encounter unexpected complexity"** | The most tempting trap. The complexity is *already stated in the requirements* ("dozens of files", "decisions about service boundaries") — it isn't something that might emerge later. |

> **Exam rule:** If the question text mentions "many files", "architectural decision", "multiple approaches", the option "try direct first" is **always wrong**.

---

## Key Takeaways for the Exam

| Concept | Remember |
|---|---|
| Plan mode = permission mode | `Shift+Tab` / `/plan` / `--permission-mode plan`; reads, explores, writes a plan, **doesn't edit** |
| When plan mode | Complex tasks, many approaches, architectural decisions, many files (45+), exploration needed, unfamiliar code |
| Direct execution | Clear bug, limited scope, known approach, one-sentence diff |
| Approval flow | auto / manual approve / keep planning; **approval = exit mode + implement** |
| Explore subagent | Read-only; isolates verbose discovery, returns a summary, preserves context; plan mode uses it automatically |
| Hybrid approach | Plan → approve → direct execution: plan mode's normal flow |
| Q5 trap | "Direct first, plan if complexity appears" → wrong; the complexity is already known |
| Exam hint | "45 files", "migration", "restructuring", "service boundaries" → plan mode |
| Exam hint | "single file", "null pointer", "stack trace", "simple fix" → direct execution |

---

## Practice Scenario 1

> There are three tasks. Classify each as plan mode or direct execution:
>
> 1. Restructure a monolithic application into microservices
> 2. Fix a null pointer error in a single function (stack trace available)
> 3. Migrate 30 files from one logging library to another
>
> **A)** 1: Plan, 2: Plan, 3: Direct
>
> **B)** 1: Plan, 2: Direct, 3: Plan
>
> **C)** 1: Direct, 2: Direct, 3: Plan
>
> **D)** 1: Plan, 2: Direct, 3: Direct

### Correct Answer: B

**Why B is correct:**
1. **Monolith → microservices = plan mode.** Architectural decision, multiple approaches, large-scale change. Analyze first, design, then implement.
2. **Null pointer fix = direct execution.** Single file, stack trace available, clear bug, clear fix — the diff fits in one sentence.
3. **30-file library migration = plan mode.** Multi-file change; discover affected files, analyze import patterns, then implement.

**Why A is wrong:** Plan mode for task 2 (null pointer) is needless overhead — a clear bug in one file, fix it directly.

**Why C is wrong:** Direct execution for task 1 (monolith restructuring) is dangerous — implementing an architectural decision without exploring and designing creates costly rework.

**Why D is wrong:** Direct execution for task 3 (30-file migration) is risky — impact analysis and a plan are needed first.

---

## Practice Scenario 2

> A developer works in a large codebase. They want to understand and restructure a legacy module. The module has 25 files and unclear dependencies.
>
> The developer wants to:
> - First explore the codebase and map the dependencies
> - Then produce a restructuring plan
> - Finally implement the plan
>
> But they worry the discovery phase will produce a lot of verbose output — polluting the main conversation's context.
>
> **Which approach is correct?**
>
> **A)** Do the whole thing in direct execution — exploration is unnecessary.
>
> **B)** Use the Explore subagent for discovery (isolates verbose output, returns a summary), design in plan mode, approve the plan and implement with direct execution.
>
> **C)** Read the 25 files one by one with Read, bringing everything into the main conversation.
>
> **D)** Do everything at once in plan mode — discovery, design and implementation together, without ever leaving the mode.

### Correct Answer: B

**Why B is correct:** A three-phase hybrid approach:
1. Discovery with the **Explore subagent** — verbose output stays in the isolated context, only summaries return. The context window is preserved. (Plan mode does this automatically too; the developer can also say "use a subagent to map the dependencies".)
2. Design in **plan mode** — build the restructuring plan from the findings, review it with `Ctrl+G`.
3. **Approve → direct execution** for implementation.

**Why A is wrong:** A 25-file legacy module with unclear dependencies — exploration is absolutely necessary. Starting with direct execution means changing things blindly.

**Why C is wrong:** Bringing 25 files into the main conversation one by one exhausts the context window (the "infinite exploration" anti-pattern). The Explore subagent solves exactly that — isolate and summarize.

**Why D is wrong:** **Plan mode cannot edit files.** Discovery and design happen in plan mode (and discovery is already delegated to the Plan/Explore subagents — no pollution), but *implementation* requires approving the plan and leaving the mode. "Implement without ever leaving the mode" is mechanically impossible.

---

## Practice Scenario 3

> A developer is given this task: "Connect the payment service to a third-party provider. There are two approaches, webhook-based and polling-based; one needs queue infrastructure, the other a scheduled job. The change will touch about 20 files."
>
> The developer's plan: "I'll start implementing the webhook approach in direct execution; if unexpected complexity with the queue infrastructure comes up, I'll switch to plan mode."
>
> **How should this approach be assessed?**
>
> **A)** Correct — plan mode adds overhead; switching when a problem appears is efficient.
>
> **B)** Wrong — the task involves "multiple valid approaches + different infrastructure requirements + many files"; the complexity is already stated in the requirements. Compare the two approaches in plan mode first, decide, then implement.
>
> **C)** Wrong — the task should be solved with the Explore subagent alone; plan mode is unnecessary.
>
> **D)** Correct — but starting with polling would be safer.

### Correct Answer: B

**Why B is correct:** Verbatim from the exam guide's Skills bullet: "choosing between integration approaches with different infrastructure requirements" → plan mode. The complexity is not "unexpected"; it is explicit in the requirements. Changing 20 files with the wrong approach and then discovering the queue infrastructure doesn't fit is costly rework — exactly what plan mode prevents. (The study-note counterpart of exam guide Q5's option D.)

**Why A is wrong:** The "plan mode is overhead" heuristic is for small tasks *whose diff fits in one sentence*; a choice between two architectural approaches is not in that class.

**Why C is wrong:** Explore is read-only and only discovers; evaluating two approaches and producing a plan is plan mode's job (which uses Explore internally).

**Why D is wrong:** Which approach is "safer" is exactly what can't be known without comparing; the problem isn't the initial pick, it's making the pick without analysis.
