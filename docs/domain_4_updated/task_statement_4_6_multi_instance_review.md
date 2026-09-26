# Task Statement 4.6: Multi-Instance Review

## Domain 4 — Prompt Engineering and Structured Output (20% of the Exam)

---

## Core Idea

If a model reviews its own output in its own session, it is highly likely to overlook the same errors because it carries its original context. The solution: **an independent instance re-reviews without the prior context.**

This resembles the "reviewing your own code" problem in software development — a human can't do it well either.

---

## Self-Review Limitations

### Scenario

A model analyzed a complex invoice document and extracted 8 line items. Now the same model is asked to verify its own extraction.

### Why Does It Fail?

```
When the model looks at its own analysis:
- The context it used while producing the original is still active
- The tendency "I made this interpretation, it seemed reasonable at the time"
- Its own logic errors look natural — because it built them with that logic
- Information it missed can be missed again — attention goes to the same places

Result: High probability of skipping subtle errors when reviewing its own output
```

The exam guide's sentence: "*a model retains reasoning context from generation, making it less likely to question its own decisions in the same session*".

### Three options — the trio the exam compares

The exam guide compares the independent instance against two things: "*more effective … than **self-review instructions** or **extended thinking***". The exam's options are exactly this trio:

| Approach | What it does | Why it's not enough |
|----------|----------|--------------|
| **Self-review instruction** ("Carefully review your answer, fix the errors") | Asks for a second look in the same session | Same context, same blind spots; the model counts its own reasoning as "verified" |
| **Extended thinking** (turn on thinking / increase its budget) | Thinks longer in the same session | Thinking longer is not thinking *differently*; thinking runs **inside** the generation context, not outside it. "More thinking = more verification" is the exam's trap |
| **Independent instance** (separate API call, without the generation reasoning) | Sees the output with zero context | ✅ Doesn't inherit the generation's assumptions; catches subtle inconsistencies |

**Rule:** You can't solve the verification problem by *doing more in the same session* (instructions, thinking); you solve it by *changing the context*.

### The Solution: Independent Instance

```
Instance A → Analyzes the document → Extraction X

Independent review (the exam guide's definition):
Instance B → Sees the document + X; but does NOT see A's REASONING
             (separate API call; no A conversation history / thinking)
→ B looks at the question "Is X correct?" without inheriting A's assumptions

Alternative technique — double extraction + diff:
Instance B → Extracts independently WITHOUT EVER SEEING X → Extraction Y
→ Fields where X ≠ Y go to human review
(This is "regeneration", not "review"; more expensive, yields field-level disagreement)
```

The exam's Skills item is the first one: "*Using a second independent Claude instance to review generated code **without the generator's reasoning context***" — the reviewer *sees the output*, *does not see the reasoning*.

### A second instance with a different role / system prompt

To take independence one step further, the reviewer is given a **different role** — "adversarial reviewer":

```
System (reviewer): "You are an auditor. Assume the extraction below is WRONG.
For each field, look for evidence in the document; mark every value for which you cannot find evidence as 'unverified'.
You do not see the rationale of the model that made the extraction — there is only the document and the result."
```

This is the same thing as the Writer/Reviewer pattern in Domain 3.6 and the principle "the reviewer sees only the diff, not the reasoning that produced it"; subagents starting with a clean context in Domain 1.3 is the orchestration form of the same principle.

---

## Multi-Pass Architecture

You are analyzing a large codebase. What happens if you provide all the files in a single pass?

### The Single-Pass Problem

```
Problem: Attention dilution
- 50 files are provided at once
- The model pays more attention to early files
- Late files receive superficial analysis
- The same pattern is flagged in file A, skipped in file B → CONTRADICTORY feedback
- Obvious errors slip through

Symptoms (exam guide Q12): "detailed comments on some files, superficial on others;
obvious errors missed; feedback that contradicts itself"
```

**Wording warning:** In this section, "contradictory finding" is a *symptom* of the single pass; in the "Conflicting Findings" section below, it is an output the cross-pass *deliberately produces* (the differing decisions of two instances are flagged). Same word, two different meanings.

### The Multi-Pass Solution

```
Stage 1: Local per-file analysis
  - Each file is analyzed separately
  - Consistent depth guarantee — every file gets full attention
  - Output: Per-file findings

Stage 2: Cross-file integration pass
  - A separate instance sees all the file findings
  - Detects data-flow issues (is data sanitized in A still clean in B?)
  - Flags conflicting findings
  - Catches system-level patterns
```

```python
def multi_pass_review(files: dict) -> dict:
    
    # Stage 1: Local per-file analysis
    file_findings = {}
    for filename, content in files.items():
        findings = analyze_file(filename, content)  # Separate instance
        file_findings[filename] = findings
    
    # Stage 2: Cross-file integration
    integration_findings = cross_file_analysis(file_findings)  # Separate instance
    
    return {
        "per_file": file_findings,
        "cross_file": integration_findings,
        "total_findings": merge_and_deduplicate(file_findings, integration_findings)
    }
```

**Cost and parallelism:** N files = N calls. If the review is not blocking (nightly audit), Stage 1's N calls are submitted as **a single batch** (Task 4.5, 50%), and Stage 2 is a single call once the batch finishes. In a blocking PR review, the N calls are made synchronously and in parallel. A design like "50 instances per document" is the absence of cost intuition — the number of passes depends on the number of files, not the number of documents.

### Q12's distractors — why are they wrong?

| Option | Why it's attractive | Why it's wrong |
|-----|--------------|--------------|
| "Ask for smaller PRs" | Seems to touch the root cause | A process change; legitimate 14-file PRs happen. The review architecture should not depend on PR size |
| "A model with a larger context window" | "It doesn't fit" is assumed | The files already fit; the problem is *attention*, not window size. A larger window can increase dilution |
| "Run the same review 3 times, majority vote (consensus voting)" | Seems to solve inconsistency with statistics | All three passes suffer the same dilution; the majority *masks* the inconsistency, doesn't resolve the cause of the contradiction; 3× cost |
| **"Local per-file pass + separate integration pass"** | — | ✅ The root cause (attention dilution) is directly addressed |

---

## Confidence-Based Routing

Not every finding is equal. Some findings are clear, some are uncertain.

### Structure

Ask the model to report its own confidence for each finding — **as an enum, not as a percentage**:

```json
{
  "finding_id": "SEC-003",
  "description": "Potential authentication bypass",
  "severity": "critical",
  "confidence": "low",
  "confidence_reason": "Code is complex; context is missing for a full analysis of the authentication logic",
  "recommendation": "Security expert review required"
}
```

Why an enum? The model's self-reported confidence is **not calibrated**; "83%" gives false precision and takes you back to the "confidence threshold" trap from Task 4.1. `high/medium/low` + `confidence_reason` is made meaningful with the calibration set (below). `confidence_reason` is a **feedback field** like `detected_pattern` in Task 4.4: frequently seen low-confidence reasons → feed back into the 4.1 criterion / 4.2 example.

### Field-level confidence (for extraction)

In code review, confidence is per *finding*. In document extraction, it is reported per **field** — Preparation Exercise 3 step 15: "*field-level confidence scores, route low-confidence extractions to human review, and analyze accuracy **by document type and field***".

```json
{
  "invoice_number": {"value": "INV-2024-117", "confidence": "high"},
  "payment_due_date": {"value": "2024-02-15", "confidence": "low",
                       "confidence_reason": "The document has two different dates; which one is the due date is unclear"},
  "total_amount": {"value": 125050, "confidence": "high"}
}
```

Routing is done at the **field** level, not the finding level: `payment_due_date` goes to the human queue, the other fields pass automatically — not the whole document.

### Routing Logic

```python
def route_findings(findings: list) -> dict:
    auto_approve = []
    human_review = []
    
    for finding in findings:
        if finding["confidence"] == "high":
            auto_approve.append(finding)  # Continue to the pipeline
        elif finding["confidence"] in ["medium", "low"]:
            human_review.append(finding)   # Human review queue
    
    return {
        "automated": auto_approve,
        "human_review": human_review
    }
```

### Confidence Threshold Calibration

```
How to calibrate?
1. Build a labeled validation set (100 findings reviewed by a security expert /
   100 invoices verified by accounting)
2. Compare the model's confidence levels with actual outcomes
3. Find the optimal threshold: "medium" confidence → X% error rate

Result: Confidence thresholds are based on concrete error rates — not intuition
```

**Document type × field accuracy matrix** (Exercise 3 step 15): calibration is not a single aggregate number, it is a table —

| | `total_amount` | `payment_due_date` | `line_items` |
|---|---|---|---|
| Table-formatted invoice | 98% | 95% | 97% |
| Plain-text invoice | 91% | **71%** | 84% |
| Nested list | 95% | 88% | **76%** |

This table drives two decisions: (1) for which cells human checking is required despite "high" confidence, (2) **for which format a few-shot example should be added** (Task 4.2 — the "plain text + due date" example). This is the same set as the eval set from Task 4.1; Domain 4's closed loop runs through here.

---

## Conflicting Findings — Same Code, Different Instance Decisions

```
Instance A: auth.py → "no rate limiting, critical"
Instance B (cross-file pass): rate limiting seen in middleware.py
→ auth.py finding: false alarm, or can the middleware be bypassed?

This conflict is flagged automatically:
{
  "conflict_detected": true,
  "finding_a": "auth.py: no rate limiting — critical",
  "finding_b": "middleware.py: global rate limiting exists",
  "resolution": "human_review",
  "conflict_reason": "Unclear whether the middleware covers the auth endpoint"
}
```

This is the *desired* output of the cross-pass — the same `conflict_detected` + explanation pattern as in Task 4.4.

---

## The Exam's Trap: "The Same Model Can Review Its Own Output"

The exam presents options like these:

> *"To reduce cost, we run both the extraction and the verification step in the same model session."*
> *"To improve accuracy, we turned on extended thinking in the extraction call and raised the budget to 10k tokens."*

**The problem with these approaches:**
- Same session = same context = same blind spots
- The model finds its own prior reasoning natural
- Thinking makes it think longer, not *from another angle*
- The benefit of independent review disappears

**The correct approach:**
- A **separate API call** for review (independent context, no generator reasoning)
- For high-risk findings, a second instance with a **different system prompt** (adversarial reviewer)
- For critical decisions, **human verification** (via confidence routing)

---

## Full Architecture: CI/CD Code Review Pipeline

```
PR Opened
│
├─ [Parallel] Per-file analysis (N instances, each 1 file)
│   ├─ src/auth.py → {findings, confidence, confidence_reason}
│   ├─ src/api.py  → {findings, confidence, confidence_reason}
│   └─ src/db.py   → {findings, confidence, confidence_reason}
│
├─ [Cross-file] Integration analysis (independent instance, sees the file findings)
│   ├─ Data-flow check
│   ├─ Conflict detection (conflict_detected)
│   └─ System-wide patterns
│
├─ [Routing] Confidence-based ordering
│   ├─ High confidence → Automatic flagging
│   └─ Low/medium confidence → Human review queue
│
└─ [Output] PR comment + prioritized findings list
    └─ [Feedback] dismissed findings + detected_pattern + confidence_reason
        → 4.1 criterion / 4.2 example update → measurement on the eval set
```

---

## Key Takeaway List

| # | Key Takeaway |
|---|---------------|
| 1 | **Self-review is limited** — same session, same blind spots. Neither a self-review *instruction* nor **extended thinking** solves this; changing the context does. |
| 2 | **An independent instance** sees the output, not the generator's *reasoning*; more effective with an adversarial role. |
| 3 | **Per-file analysis** prevents attention dilution — every file gets full attention. A larger context window or majority voting doesn't solve this. |
| 4 | **The cross-file integration pass** catches data-flow and conflict issues. In a non-blocking review, Stage 1 can be a single batch. |
| 5 | **Confidence-based routing:** enum confidence (`high/medium/low`) + `confidence_reason`; high → automatic, low → human. **Field**-level in extraction. |
| 6 | **Confidence thresholds are calibrated with a labeled validation set** — document type × field matrix; not intuition. |
| 7 | **Conflicting findings** are flagged with `conflict_detected: true`, a human reviews. |

---

## Practice Questions and Answer Explanations

### Question 1

A code review system verifies every extraction in the same Claude session. What fundamental problem does it experience?

**A)** The verification step is too expensive  
**B)** Since the model carries its own reasoning context, it may overlook the same errors  
**C)** Two calls cannot be made in the same session  
**D)** The output format changes  

**✅ Answer: B**

*Explanation:* The model in the same session carries the context it used while producing the first extraction. Because of this context, its tendency to find its own errors "reasonable" increases. An independent instance does not carry this context and catches subtle inconsistencies better.

---

### Question 2

In a single-pass review of a 14-file PR, some files get detailed comments, others superficial ones; an obvious error was missed and there is contradictory feedback for two files. What is the best restructuring?

**A)** Use a model with a larger context window — so all files fit comfortably  
**B)** Analyze each file in a separate pass for local issues, then run a separate integration pass focused on cross-file data flow  
**C)** Run the same review three times, report the findings flagged by the majority  
**D)** Ask developers to open smaller PRs  

**✅ Answer: B**

*Explanation:* Exam guide Q12. The symptoms (inconsistent depth, missed obvious error, contradictory feedback) are symptoms of **attention dilution**; only splitting the pass addresses the root cause. (A) the problem is attention, not fit — dilution can increase as the window grows. (C) all three passes suffer the same dilution; the majority masks the inconsistency, 3× cost. (D) makes the review architecture dependent on PR size; legitimate large PRs happen.

---

### Question 3

How should confidence thresholds be calibrated in confidence-based routing?

**A)** Determined based on developer intuition  
**B)** Adjusted according to the model's suggestion  
**C)** Confidence levels are compared with actual outcomes over a labeled validation set  
**D)** Industry-standard thresholds are used (80% confidence = high)  

**✅ Answer: C**

*Explanation:* The "medium confidence → human review" decision should be based on data, not intuition. The correlation of model confidence levels with actual error rates is measured over labeled findings verified by security experts. This gives a concrete threshold — and the document type × field matrix shows which cells are weak.

---

### Question 4

File A has a "no rate limiting — critical" finding. The cross-file pass finds a global rate limiting middleware in file B. How should this be handled?

**A)** Automatically close the finding in file A — the middleware exists  
**B)** Can the middleware be bypassed? There is uncertainty → flag with conflict_detected: true, let a human review  
**C)** Report both findings, ignore the conflict  
**D)** Re-analyze file A, start a retry loop  

**✅ Answer: B**

*Explanation:* Whether the middleware covers the auth endpoint cannot be determined automatically. In such uncertainties, flagging with `conflict_detected: true` and routing to human review is the correct approach. Closing automatically (A) creates a security risk; ignoring (C) doesn't resolve the conflict.

---

### Question 5

In an extraction pipeline, the model is observed to miss subtle errors. Three proposals are on the table: (1) add a "carefully review your output and fix it" instruction to the prompt, (2) turn on extended thinking and increase the budget, (3) have the extraction verified by a separate Claude call that does not see the generator's reasoning. Which is the most effective and why?

**A)** (2) — more thinking budget means more verification  
**B)** (1) — the cheapest, and the model knows its own output best  
**C)** (3) — an independent instance that doesn't carry the generation context, unlike the self-review instruction and thinking, doesn't inherit its own assumptions  
**D)** (1) and (2) together — instruction + thinking is as effective as an independent instance and cheaper  

**✅ Answer: C**

*Explanation:* Exam guide: "*Independent review instances … are more effective at catching subtle issues than self-review instructions or extended thinking*". (A) thinking thinks longer *inside* the same context; it doesn't provide a different angle. (B) "knows its own output best" is exactly the source of the problem. (D) adding two insufficient methods together doesn't solve the context problem.
