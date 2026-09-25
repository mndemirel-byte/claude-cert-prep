# Task Statement 1.6: Task Decomposition Strategies

## Domain 1 — Agentic Architecture & Orchestration (27% of Exam)

---

## The Core Idea

How do you break big tasks into pieces? There are two fundamental patterns, and you need to know when each is right. The selection criterion comes down to a single question: **are the steps known in advance, or are they discovered along the way?**

---

## Pattern 1: Fixed Sequential Pipeline (Prompt Chaining)

You split the work into predetermined sequential steps. Each step's output becomes the next step's input.

Example — code review:

1. Analyse each file one at a time
2. Then run an integration pass that checks dependencies across all files

**When to use:** Predictable, structured, multi-aspect tasks — code review, document processing, data transformation, flows like "extract → validate → format."

**Advantage:** Consistent and reliable; each step focuses on one job, output quality is predictable.

**Limitation:** Can't adapt to unexpected findings — at step 2 it can't say "actually I should have done step 1 differently."

### Programmatic gates between steps

The power of prompt chaining isn't only in the sequencing, but in being able to put code **between** the steps. Each step's output is checked programmatically before it goes to the next:

- If the extraction step returned an empty or schema-invalid result → don't proceed, retry or raise an error
- If the analysis step flagged a "critical security vulnerability" → skip the formatting step, escalate directly
- If a step's output exceeds the token budget → summarise, then continue

These gates are the deterministic enforcement logic from 1.4 applied to a pipeline: instead of trusting the model to decide "am I ready for the next step?", the code decides.

---

## Pattern 2: Dynamic Adaptive Decomposition

You generate subtasks dynamically based on what's discovered at each step.

Example — "add tests to a legacy codebase":

- First you map the structure
- You identify the high-impact areas
- You build a prioritised plan as dependencies emerge

**When to use:** Open-ended research tasks, problems that require exploration, situations where the subtasks can't be known in advance.

**Advantage:** Adapts to the problem; every discovery improves the plan.

**Limitation:** Less predictable — duration, cost, and scope can't be estimated up front.

### Stopping criteria and budget

The biggest risk of dynamic decomposition is **never-ending exploration**: the agent generates new subtasks at every step and never says "I know enough." That's why a dynamic plan is always designed with explicit bounds:

- **Goal definition:** a measurable end point such as "stop when test coverage of the 5 riskiest modules reaches 70%"
- **Budget:** a maximum number of subtasks, turns, or tokens (the safety-net logic from 1.1)
- **Depth limit:** how many levels subtasks may branch (nesting depth from 1.3)
- **Diminishing-returns threshold:** if new discoveries add nothing meaningful to the plan, end the exploration phase and move to execution

On the exam, the answer to "the agent has been mapping the codebase for weeks but hasn't written a single test" is not to abandon dynamic decomposition, but to **add stopping criteria and a budget**.

---

## Mapping to Anthropic's Pattern Terminology

The exam may use the pattern names from Anthropic's "Building Effective Agents" guide. What you've learned in Domain 1 maps to those patterns as follows:

| Building Effective Agents pattern | What it does | Domain 1 counterpart |
|---|---|---|
| **Prompt chaining** | Fixed sequential steps with programmatic gates between them | Pattern 1 in this lesson |
| **Routing** | Classify the input and direct it to the appropriate specialised flow | Dynamic subagent selection in 1.2 |
| **Parallelization — sectioning** | Run independent subtasks in parallel, then combine | Parallel spawning in 1.3; the per-file pass in this lesson |
| **Parallelization — voting** | Run the same task several times, take the majority/union | Multi-instance review in Domain 4 |
| **Orchestrator-workers** | A central orchestrator dynamically generates and distributes subtasks | Hub-and-spoke in 1.2; Pattern 2 in this lesson |
| **Evaluator-optimizer** | Generate → evaluate → refine loop | Iterative refinement in 1.2 |

The guide's core principle is also the exam's core principle: **choose the simplest pattern that suffices.** Don't build an orchestrator if a fixed pipeline is enough; don't spawn subagents if a single agent is enough. Complexity is added only when it delivers a measurable benefit.

---

## The Attention Dilution Problem (Exam Trap)

This is very important. If you process too many files or too much data in a single pass, Claude's attention dilutes. Result: it gives detailed feedback on some files and misses obvious bugs in others. Worse — **it flags a pattern as problematic in one file while approving the same code in another**. That inconsistency is the signature of attention dilution.

### Why "a bigger model / a bigger context window" doesn't fix it

The exam's favourite distractor. Attention dilution is not a **capacity** problem — 14 files fit in the context window; the problem isn't that they don't fit. The problem is that applying **the same criteria at the same depth** to every file in a single pass is structurally hard: the model relaxes the evaluation framework it set up at the start of the pass as it goes on, its priorities drift, and the issue types it found in the first files start to look "normal" in later ones. A bigger context window fits more files — and reproduces the same problem at a larger scale.

### The fix: multi-pass architecture

- **Pass 1 — Per-file local analysis:** Review each file separately, with the same prompt and the same criteria. Catch local issues. Every file gets "first file" treatment — that's where the consistency comes from.
- **Pass 2 — Cross-file integration:** Take the structured outputs of Pass 1; check data flow, dependencies, and inconsistencies across files. This pass sees Pass 1's findings, not the entire source code — so it doesn't suffer attention dilution itself.

Per-file passes catch local issues consistently; the integration pass catches cross-file issues.

### The cost trade-off

Multi-pass means more API calls: 14 + 1 calls for 14 files, instead of 1 call in a single pass. That's an acceptable trade-off because (a) the per-file calls are independent and can run **in parallel** (total time doesn't grow), (b) each call is small (total token cost isn't very different from one large call), and (c) the cost of a missed bug exceeds the cost of the extra calls. On the exam, "multi-pass is too expensive, go back to a single pass" is a distractor.

---

## Key Exam Takeaways

| Concept | Remember |
|---|---|
| Fixed sequential pipeline (prompt chaining) | Predetermined sequential steps with programmatic gates between them — for predictable tasks |
| Dynamic adaptive decomposition | Subtasks generated from discoveries — for open-ended research; **stopping criteria and a budget are mandatory** |
| Selection criterion | Are the steps known in advance? Yes → pipeline. No → dynamic |
| Building Effective Agents mapping | Prompt chaining, routing, parallelization (sectioning/voting), orchestrator-workers, evaluator-optimizer — choose the simplest pattern that suffices |
| Attention dilution | Too much data in one pass → inconsistent depth and contradictory judgements; a consistency problem, not a capacity problem |
| Multi-pass architecture | Per-file local analysis (parallel) + cross-file integration — the fix for attention dilution |
| Exam trap | "Bigger model," "write 'pay equal attention' in the prompt," "multi-pass is expensive" — none of these fix the structural problem |

---

## Practice Scenario 1

> A code review agent analyses a 14-file pull request in a single pass. Results:
>
> - It gives very detailed feedback on some files and misses obvious bugs in others
> - It flags a pattern as an "anti-pattern" in file 3, but approves the same code in file 11
>
> **What is the problem and how should it be fixed?**
>
> **A)** The agent's context window is insufficient — a bigger model should be used.
>
> **B)** Processing 14 files in a single pass causes attention dilution — switch to a multi-pass architecture: per-file local analysis + cross-file integration.
>
> **C)** Add the instruction "pay equal attention to every file" to the agent's system prompt.
>
> **D)** Order the files by priority rather than alphabetically.

### Correct Answer: B

**Why B is correct:** Processing 14 files in one pass dilutes Claude's attention. Inconsistent depth and different reactions to the same pattern are the classic symptoms. The multi-pass architecture — first analyse each file separately with the same criteria, then run a cross-file integration pass over the findings — fixes both problems.

**Why A is wrong:** The problem isn't context window size, it's attention distribution. The 14 files already fit. A bigger model has the same consistency problem in a single pass; a bigger context window just lets more files suffer the same problem.

**Why C is wrong:** A prompt instruction is probabilistic. Saying "pay equal attention" doesn't fix attention dilution — this is a structural architecture problem, not a prompt problem.

**Why D is wrong:** Changing the order changes which files get neglected, but doesn't fix the problem. Still a single pass, still diluted attention.

---

## Practice Scenario 2

> A team builds an agent that processes customer support emails. The work for every email is fixed: (1) extract structured fields (customer, product, issue type), (2) classify the issue, (3) draft a response, (4) check the draft for tone and compliance. The team implements this with a dynamic orchestrator that "generates subtasks based on what's discovered at each step." Result: for some emails the orchestrator generates 12 subtasks, for others 2; processing time is unpredictable; and even when step 1 extracts empty fields, step 3 still runs and produces a fabricated response.
>
> **What is the most appropriate fix?**
>
> **A)** Write a more detailed system prompt for the orchestrator — tell it to generate exactly 4 subtasks for every email.
>
> **B)** This job consists of four fixed, predictable steps — replace the dynamic orchestrator with a prompt chaining pipeline; put programmatic gates between the steps (if the extracted fields are empty, don't proceed to step 3; retry or escalate).
>
> **C)** Launch 4 subagents in parallel for every email — that makes the duration predictable.
>
> **D)** Add the instruction "don't generate a response if the fields are empty" to step 3.

### Correct Answer: B

**Why B is correct:** The steps are known in advance and identical for every email — this is fixed-pipeline work, not dynamic decomposition. A dynamic orchestrator adds unnecessary complexity and unpredictability here. Prompt chaining runs every email through the same 4 steps; the programmatic gate between steps deterministically prevents an empty extraction result from leaking into the next step. The "simplest pattern that suffices" principle.

**Why A is wrong:** Forcing a dynamic orchestrator to behave like a fixed one via the prompt is patching the wrong pattern. It will probabilistically generate "usually 4" subtasks, but won't deliver the predictability of a fixed pipeline, and it doesn't solve the empty-fields problem.

**Why C is wrong:** The steps depend on each other — classification needs the extraction, the draft needs the classification. Parallel launching is only for independent subtasks (1.3); here every step works from the previous one's output.

**Why D is wrong:** A prompt instruction is probabilistic. Rather than trusting step 3 to notice the "fields are empty" condition and stop, a code gate between the steps is the deterministic solution. It also doesn't address the main problem (the wrong pattern choice).
