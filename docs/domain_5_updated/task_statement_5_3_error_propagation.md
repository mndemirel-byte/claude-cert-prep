# Task Statement 5.3: Error Propagation

## Domain 5 — Context Management and Reliability (15% of the Exam)

---

## Core Idea

In multi-agent systems and data extraction pipelines, errors are inevitable. A tool times out, an API denies access, a data source returns nothing. The critical question is: **what do you do when an error occurs — and who does it?**

This task statement teaches how errors are handled across two layers (subagent local recovery → structured propagation to the coordinator), the three anti-patterns, and the difference between an access failure and a valid empty result.

Exam scenario: **Multi-Agent Research System** (coordinator + web search / document analysis / synthesis / report subagents). Official sample question Q8 comes straight from this statement.

---

## Two-Layer Recovery — Who Recovers What?

The exam guide's Skills item: *"Having subagents implement **local recovery for transient failures** and only propagate errors they cannot resolve, including what was attempted and partial results"*.

| Layer | Who | What it does | What it does not do |
|---|---|---|---|
| **1. Local recovery** | Subagent (or tool wrapper) | Tries to resolve the transient error internally with a **bounded** number of retries / backoff; tries an alternative source | Does not retry forever; does not hide the error |
| **2. Structured propagation** | Subagent → Coordinator | Passes what it could not resolve upward with **four-field** context: failure type, what was attempted, partial results, alternatives | Does not say a generic "search unavailable"; does not mark an empty result as "success" |
| **3. Recovery decision** | Coordinator | The three options from the Q8 rationale: **retry with a modified query** / **alternative approach** / **proceed with partial results** (+ coverage note) | Does not terminate the entire workflow because of a single error |

The exam's most tempting trap is the option that gets layer 1 right and breaks layer 2 (Anti-Pattern 3 below).

---

## Structured Error Context

When an error occurs, simply saying "an error occurred" is not enough. The error report must contain four pieces of information:

### 1. Failure Type

Recall from Domain 2.2 — four categories:

| Type | Description | Action (layer 1) | Action (layer 3) |
|---|---|---|---|
| **Transient** | Network timeout, temporary service outage | Bounded retry/backoff | If still failing, alternative source or partial continuation |
| **Validation** | Invalid parameter, format error | Fix the parameter, try again | Modified query |
| **Business** | Business-logic rejection | No retry | Alternative approach |
| **Permission** | Access denied | No retry | Escalation or permission request |

### 2. What Was Attempted

The specific query, parameters, **and what was tried during local recovery**:

```json
{
  "attempted_action": "journal_search",
  "query": "geothermal energy capacity 2023-2024",
  "parameters": {
    "database": "ScienceDirect",
    "date_range": "2023-01-01 to 2024-12-31",
    "filters": ["peer-reviewed"]
  },
  "local_recovery_tried": ["retry x3 with backoff (2s, 4s, 8s)", "cached copy: none available"]
}
```

### 3. Partial Results

Data gathered before the error:

```json
{
  "partial_results": {
    "sources_completed": ["IEA", "IRENA", "BloombergNEF"],
    "sources_failed": ["ScienceDirect"],
    "findings_so_far": [
      {"claim": "Solar capacity grew 45%", "source": "IEA"}
    ]
  }
}
```

### 4. Potential Alternative Approaches

Tried and untried alternatives are marked separately — so the coordinator can see what is still on the table:

```json
{
  "alternatives_untried": [
    "Try alternative database: Google Scholar",
    "Proceed with partial results and annotate gap"
  ],
  "alternatives_tried": [
    "Use cached version from last sync — no cache present"
  ]
}
```

---

## Three Anti-Patterns — EXAM CRITICAL

The exam guide lists three anti-patterns; all three are the wrong options in Q8.

### Anti-Pattern 1: Silent Suppression — Q8 C

Returning an empty result marked as "successful" even though the source could not be reached.

```json
// WRONG — the source was NOT reached, yet it says success
{
  "status": "success",
  "results": [],
  "source_reached": false,     // ← this is the truth; but the field is missing or ignored
  "error": null
}
```

**Why it is dangerous:** The coordinator does not know an error occurred. The recovery mechanism cannot kick in. The report is written on incomplete data, but nobody knows about the gap. Guide: "*prevents any recovery and risks incomplete research outputs*".

### Anti-Pattern 2: Workflow Termination — Q8 D

Killing the entire pipeline because of a single error.

```
Source 3/5 unreachable → CANCEL THE ENTIRE RESEARCH
```

**Why it is dangerous:** 4 sources were processed successfully — this throws those partial results away. Guide: "*terminates the entire workflow unnecessarily when recovery strategies could succeed*".

### Anti-Pattern 3: Generic Error Status — Q8 B

Automatic retry with exponential backoff inside the subagent — **correct up to this point** — but once all attempts are exhausted, returning only **"search unavailable"** to the coordinator.

```json
// WRONG — local recovery is right, propagation is wrong
{"status": "search_unavailable"}
```

**Why it is dangerous:** The guide's Knowledge item: "*generic error statuses ('search unavailable') hide valuable context from the coordinator*". The coordinator does not know which query failed, on which source, with what kind of error, or whether there were partial results → "*preventing informed decisions*". Retry with a modified query, an alternative source, or partial continuation — it cannot decide on any of them.

**Exam warning:** This option looks correct because it comes with the words "retry" and "exponential backoff". The retry is right; the **generic message** is wrong. Layer 1 ✔, layer 2 ✘.

### The Correct Approach — Q8 A

```json
{
  "status": "partial_success",
  "completed_sources": 4,
  "failed_sources": 1,
  "findings": [...],
  "errors": [
    {
      "source": "ScienceDirect",
      "failure_type": "transient",
      "source_reached": false,
      "attempted": "journal_search for geothermal data; 3 retries with backoff",
      "partial_results": "none from this source",
      "alternatives_untried": ["Google Scholar", "proceed with coverage gap"]
    }
  ],
  "coverage_note": "Geothermal section limited due to ScienceDirect timeout"
}
```

### Official sample question (Exam Guide Q8)

> A web search subagent times out while researching a complex topic. You must design how this error information flows to the coordinator. Which approach best enables intelligent recovery?
>
> **A)** Return **structured error context** to the coordinator including the failure type, the attempted query, any partial results, and potential alternative approaches.
> **B)** Implement automatic retry with exponential backoff inside the subagent; once all attempts are exhausted, return only a generic "search unavailable" status.
> **C)** Catch the timeout inside the subagent and return an **empty result set marked as successful**.
> **D)** Propagate the timeout exception directly to a top-level handler and **terminate the entire research workflow**.
>
> **Correct answer: A.** Structured context gives the coordinator the information it needs to decide — "*whether to retry with a modified query, try an alternative approach, or proceed with partial results*". B's generic status hides context; C suppresses the error as success; D terminates the workflow unnecessarily when recovery is possible.

---

## Access Failure vs Valid Empty Result — EXAM TRAP

This distinction is tested very subtly on the exam. Confusing the two situations leads to serious errors — and the distinction **must be visible in the response itself**.

### Access Failure

The tool **could not reach** the data source:

- Network timeout
- Invalid API key
- Service is down

→ **A retry can be considered** (layer 1, bounded). The data may be there, but we could not reach it.

### Valid Empty Result

The tool **reached** the data source and **found no** matching results:

- No records in the database for this date range
- No customer matches the search criteria
- This product is not in inventory

→ **A retry is UNNECESSARY.** The data source was reached successfully and the answer is "no results". This **is the answer itself**. Trying again gives the same result. The next step is not a retry but *a new decision*: a different query (coordinator), an additional identifier from the customer (5.2), or a coverage note.

### The distinction in the response schema — the exam guide's Skills item

*"Distinguishing access failures from valid empty results **in error reporting** so the coordinator can make appropriate decisions"*. In other words, the distinction is made not only in the agent's interpretation but **in the tool/subagent response**. If the same `{"status": "success", "results": []}` shape describes two different realities, the schema is broken.

```json
// Valid empty result — source reached, no matches
{
  "status": "ok",
  "source_reached": true,
  "match_count": 0,
  "query": "orders where phone = +90 555 ...",
  "message": "No orders found for this phone number"
}

// Access failure — source not reached
{
  "status": "error",
  "source_reached": false,
  "failure_type": "transient",
  "attempted": "orders lookup, 3 retries",
  "partial_results": null
}
```

The exact definition of silent suppression (Anti-Pattern 1) is now clear: **saying `status: ok/success` while `source_reached: false`.**

### Decision Table

| Situation | Did the tool reach the source? | Result | Action |
|---|---|---|---|
| Access failure | ❌ No (`source_reached: false`) | Unknown | Bounded retry (layer 1) → structured propagation |
| Valid empty result | ✅ Yes (`source_reached: true`) | No matches | Do not retry — this IS the answer; new decision (different query / additional identifier / coverage note) |

---

## Retry Rules — One Table Across Domains

The question "when to retry?" appears with three separate answers in 4.4, 5.2, and 5.3. One table:

| Situation | Retry? | Who | Source |
|---|---|---|---|
| Transient access failure (timeout, 5xx) | ✅ Bounded, with backoff | Subagent (layer 1) | 5.3 |
| Semantic extraction error, information **is** in the document | ✅ With the error message, 2–3 times | Extraction loop | 4.4 |
| Information **not** in the document / in an external document | ❌ Nullable schema / add the document | — | 4.4 |
| Valid empty result | ❌ This is the answer; additional identifier from the customer | Agent | 5.3 + 5.2 |
| Permission / business error | ❌ Escalation / alternative | Coordinator | 5.3 |

---

## Coverage Annotations

### Problem

A synthesis report is supposed to cover 5 energy sources. But the geothermal data source could not be reached. The report silently skips the geothermal section.

When the reader reads the report, they cannot tell whether geothermal was deliberately excluded or whether the data was missing.

### Solution

In the synthesis output, state which findings are **well-supported** and which areas have **gaps**:

```
## Research Coverage
- Solar energy: ✅ Comprehensive (3 sources)
- Wind energy: ✅ Comprehensive (2 sources)
- Hydroelectric: ✅ Comprehensive (2 sources)
- Biomass: ✅ Partial (1 source)
- Geothermal: ⚠️ Limited — data missing due to ScienceDirect access timeout
```

**Rule:** Explicit coverage annotation instead of silent omission. "The geothermal energy section is limited due to an inaccessible journal source" is always better than silent omission.

This section is part of the same report as 5.6's "well-supported / contested" distinction. The skeleton of a synthesis report has three sections: **Supported findings / Contested findings (5.6) / Coverage gaps (5.3)**.

### How is it tested? (Exam Guide Exercise 4, step 19)

*"Simulate a subagent timeout and verify the coordinator receives structured error context (failure type, attempted query, partial results). Test that the coordinator can proceed with partial results and annotate the final output with coverage gaps."* — So the acceptance criterion has three steps: timeout simulation → does the coordinator receive structured context → does the report carry a coverage note.

> **Current note (Agent SDK):** An API error that *terminates a subagent early* (rate limit, etc.) is not delivered to the coordinator as the subagent's *result* in the Agent SDK. In other words, structured error context does not come automatically from the infrastructure; the subagent's own output or the **tool wrapper** must produce it. For the "ScienceDirect timeout" in the scenario, the right place is the tool wrapper — the same as Domain 2.2's structured error response schema.

---

## Key Takeaways for the Exam

| Concept | Remember |
|---|---|
| Two layers | Subagent local recovery (bounded retry) → propagate what it cannot resolve in structured form → coordinator decides |
| The coordinator's three options | Retry with a modified query / alternative approach / proceed with partial results |
| Structured error context | Failure type + what was attempted (including local recovery) + partial results + alternatives |
| Anti-pattern 1: silent suppression | `success` while `source_reached: false` — recovery is blocked |
| Anti-pattern 2: workflow termination | Killing the entire pipeline for a single error — partial results are lost |
| Anti-pattern 3: generic status | Retry is right, "search unavailable" is wrong — the coordinator is left blind |
| Access failure | Source not reached → consider a bounded retry |
| Valid empty result | Source reached, no matches → retry is UNNECESSARY; new decision |
| Distinction in the schema | `source_reached` / `failure_type` fields — the distinction must be visible in the response |
| Coverage annotations | Supported / with gaps — no silent omission; same report skeleton as 5.6 |

---

## Practice Scenario 1

> A multi-agent research system is collecting data from 5 academic sources. 4 sources returned results successfully. The 5th source (ScienceDirect) produced a network timeout error.
>
> The agent's current behavior: after the timeout, it cancels the entire research and returns a "research could not be completed" message.
>
> **Which is the correct approach?**
>
> **A)** Cancelling the entire research is correct — a report should not be written with missing data.
>
> **B)** The subagent should attempt a bounded retry with backoff; if it still fails, it should pass the failure type, attempted query, and partial results to the coordinator in structured form; the coordinator should proceed with the 4 sources and add a coverage annotation to the synthesis output.
>
> **C)** The subagent should attempt a bounded retry with backoff; if it still fails, it should return a "source unavailable" status to the coordinator, and the coordinator should proceed with the 4 sources.
>
> **D)** The subagent should catch the timeout and return an empty result set as successful; the coordinator should start the synthesis assuming all 5 sources completed.

### Correct Answer: B

**Why B is correct:** Both layers are right: local bounded retry, then structured propagation; the coordinator proceeds with partial results and adds a coverage note. Q8-A + Exercise 4 step 19.

**Why A is wrong:** The workflow termination anti-pattern. It throws away the results of 4 successful sources because of a single failure.

**Why C is wrong:** The most tempting wrong option (Q8-B). The local retry is right, but the generic "source unavailable" status leaves the coordinator blind: could an alternative database have been tried, were there partial findings, was the error transient — unknown. Even if the coordinator proceeds, the report's coverage note cannot be written.

**Why D is wrong:** Silent suppression (Q8-C). Success is reported even though the source could not be reached; the coordinator does not know about the gap, and the report comes out silently incomplete.

---

## Practice Scenario 2

> A customer support agent is looking up a customer's order. The tool returns the following result:
>
> ```json
> {
>   "status": "ok",
>   "source_reached": true,
>   "match_count": 0,
>   "message": "No orders found matching criteria"
> }
> ```
>
> The agent interprets this result as "order not found, let's try again" and runs the same query 3 more times.
>
> **What is the problem with this behavior?**
>
> **A)** The agent should increase the retry count — 3 is not enough, it should try 10.
>
> **B)** The agent is confusing a valid empty result with an access failure. `source_reached: true` — the tool reached the source and found no match. This is the answer itself; a retry is unnecessary. The next step is to ask the customer for an additional identifier.
>
> **C)** The tool is malfunctioning — it should always return at least one result.
>
> **D)** The agent should search with other fields (email, name) without asking the customer — not with the same parameters.

### Correct Answer: B

**Why B is correct:** `source_reached: true` + `match_count: 0` = valid empty result. This is not an access failure; trying again gives the same result. The correct next step, as in 5.2, is to ask the customer for an additional identifier.

**Why A is wrong:** More retries return the same valid empty result. The problem is not the retry count but the interpretation of the result.

**Why C is wrong:** The tool is working correctly — in fact it is well designed: it clearly reports that the source was reached and there was no match. "No match" is a valid answer.

**Why D is wrong:** The agent searching with other fields on its own without asking the customer carries the risk of reaching the wrong customer (the 5.2 heuristic-selection trap). The additional identifier is requested *from the customer*.

---

## Practice Scenario 3

> A research coordinator receives the following response from its web search subagent:
>
> ```json
> {"status": "success", "results": []}
> ```
>
> Logs show that the same query returned 12 results 30 seconds earlier and that the tool provider was experiencing an outage at that moment. The coordinator reported "no sources on this topic" and moved on.
>
> **What is the root cause?**
>
> **A)** The coordinator should have retried — an empty result is always retried.
>
> **B)** The subagent's response schema does not distinguish an access failure from a valid empty result; the outage was propagated as "success + empty array" (silent suppression). `source_reached` / `failure_type` fields should be added to the schema, the subagent should first attempt local retry for the transient error, and if it cannot resolve it, return a structured error.
>
> **C)** The coordinator should have sent the same query to a second subagent to verify the result.
>
> **D)** The tool provider's outage is an external problem; there is nothing the coordinator can do.

### Correct Answer: B

**Why B is correct:** The schema collapses two different realities (not reached / no match) into the same shape. That is why the coordinator mistook the outage for "no sources". The fix is both in the schema (the distinction must be visible) and in the layers (local retry → structured propagation).

**Why A is wrong:** "Always retry an empty result" is the exact opposite error: it also queries valid empty results over and over. To decide on a retry, the access status must first be *known* — the schema does not provide it.

**Why C is wrong:** A second subagent would return the same "success + empty" answer with the same broken schema; the problem is in the propagation layer, not in execution.

**Why D is wrong:** The outage is an external problem, but its *staying silent* is the system's problem: had a structured error arrived, the coordinator would have tried an alternative source or added a coverage note to the report.
