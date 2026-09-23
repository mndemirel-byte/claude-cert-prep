# Task Statement 1.2: Multi-Agent Orchestration

## Domain 1 — Agentic Architecture & Orchestration (27% of Exam)

---

## The Core Idea

A single agent with a loop is powerful, but some problems are too complex for one agent to handle well. You need specialists. This is where **multi-agent orchestration** comes in.

The architecture the exam tests is called **hub-and-spoke**. Picture a wheel:

- **The hub** is the **coordinator agent**. It sits at the centre and runs the show.
- **The spokes** are **subagents** — specialists that each do one thing well (e.g., web search, document analysis, code review, synthesis).

The critical rule: **ALL communication flows through the coordinator.** Subagents never talk to each other directly. If the web search agent finds something that the synthesis agent needs, it doesn't pass it sideways — it returns its results to the coordinator, and the coordinator passes the relevant information to the synthesis agent.

---

## Why This Matters

This hub-and-spoke pattern gives you three things:

1. **Observability** — every piece of information flows through one place, so you can log and monitor everything.
2. **Consistent error handling** — if a subagent fails, the coordinator catches it and decides what to do.
3. **Control** — the coordinator decides what context each subagent sees, which prevents information leakage and keeps subagents focused.

---

## The Isolation Principle (Most Commonly Misunderstood Concept)

This is the concept the exam hammers hardest. Commit it to memory:

> **Subagents do NOT automatically inherit the coordinator's conversation history. Subagents do NOT share memory between invocations. Every piece of information a subagent needs must be explicitly included in its prompt.**

Think of each subagent like a brand new employee you're handing a task to. They know nothing about what's happened in the project unless you tell them in their briefing. If you forget to mention something, they simply don't know it.

---

## The Coordinator's Responsibilities

The coordinator does all of the following:

- **Task decomposition** — breaks a complex request into subtasks
- **Dynamic subagent selection** — decides which subagents are needed (not always all of them)
- **Context passing** — gives each subagent exactly the information it needs
- **Result aggregation** — collects outputs from subagents and combines them
- **Iterative refinement** — reviews the combined output, identifies gaps, and re-delegates if needed
- **Error handling** — catches failures and decides how to recover

---

## The Narrow Decomposition Failure (Exam Trap)

This is a specific failure mode the exam tests. Here's how it works:

A user asks: *"What is the impact of AI on creative industries?"*

The coordinator decomposes this into subtasks, but only generates subtasks about visual arts — digital painting, graphic design, illustration. It completely misses music, writing, film, and gaming.

Each subagent does excellent work on its assigned subtask. The synthesis is well-written. But the final report only covers visual arts.

**Where is the failure?** Not in the subagents. Not in the synthesis. The failure is in **the coordinator's task decomposition**. It sliced the problem too narrowly at the very start. The exam expects you to **trace the failure back to its origin**, not blame downstream components.

---

## Key Exam Takeaways

| Concept | Remember |
|---|---|
| Hub-and-spoke | Coordinator at the centre, subagents as spokes, ALL communication through the coordinator |
| Isolation principle | Subagents inherit nothing automatically — every piece of context must be explicitly passed |
| Coordinator responsibilities | Decomposition, selection, context passing, aggregation, refinement, error handling |
| Narrow decomposition | When the final output is missing entire topics, trace the failure back to the coordinator's decomposition |
| No direct subagent communication | Subagents never talk to each other — always through the coordinator |

---

## Practice Scenario

> A multi-agent research system has a coordinator, a web search subagent, a document analysis subagent, and a synthesis subagent. A user asks for a report on "renewable energy technologies."
>
> The final report is well-written and thoroughly researched, but it only covers solar and wind energy. Geothermal, tidal, biomass, and nuclear fusion are completely absent.
>
> The web search and document analysis subagents are functioning correctly — when tested independently with queries about geothermal or tidal energy, they return excellent results.
>
> **What is the root cause?**
>
> **A)** The web search subagent's search queries are too narrow and need broader search terms.
>
> **B)** The coordinator's task decomposition failed to include geothermal, tidal, biomass, and fusion as research subtopics.
>
> **C)** The synthesis subagent filtered out some research topics when combining the results.
>
> **D)** The subagents need access to the coordinator's full conversation history to understand the broader scope.

### Correct Answer: B

**Why B is correct:** The subagents work perfectly when given the right queries — the problem is they were never *asked* about geothermal, tidal, biomass, or fusion. The coordinator decomposed "renewable energy technologies" into only solar and wind subtopics. The failure originates at the coordinator's task decomposition step.

**Why A is wrong:** The web search subagent returns excellent results when tested independently with geothermal or tidal queries. Its search capability is fine — it was simply never given those topics to search for. The fault is upstream.

**Why C is wrong:** The synthesis subagent can only synthesise what it receives. If no research on geothermal or tidal was ever conducted, there's nothing for it to filter out. The missing topics were never researched in the first place.

**Why D is wrong:** This is the isolation principle trap. Giving subagents the coordinator's full conversation history is the opposite of good architecture. Subagents should receive only the specific context they need, explicitly passed by the coordinator. The fix is to improve the coordinator's decomposition, not to break the isolation principle.
