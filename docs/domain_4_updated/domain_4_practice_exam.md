# Domain 4 Practice Exam: Prompt Engineering and Structured Output

## General Information

- **Domain Weight:** 20% of the exam
- **Number of Questions:** 10
- **Passing Threshold:** 8/10 (aim for the high bar)
- **Difficulty:** Exam-level scenario-based questions
- **Scope:** All 6 Task Statements (4.1 – 4.6)
- **Note:** The questions are written from different angles than the practice questions in the lecture notes; memorizing the lecture questions is not enough.

---

> Answer the questions first, then check the answer key.

---

## Questions

---

### Question 1 — Task Statement 4.1 (Explicit Criteria)

A CI/CD code review agent reports three categories: security, logic errors, and code style. The code style category has a 60% false positive rate. A team lead says: *"False positives are harmless — the developer filters them out at a glance. The real risk is a missed bug; let's not turn off any category, in fact let's loosen the thresholds."* Another engineer proposes temporarily disabling the code style category.

**Which assessment is correct?**

**A)** The team lead is right; a false negative is always more expensive than a false positive, all categories should stay on  
**B)** The engineer is right; a high false positive category erodes developer trust, and this leads to correctly functioning security findings being ignored as well — the category should be disabled, its criteria clarified, measured, and then re-enabled  
**C)** Both are wrong; the correct solution is to add a "don't report if unsure" instruction for all categories  
**D)** Both are wrong; the code style category should be moved to a larger model  

---

### Question 2 — Task Statement 4.1 (Explicit Criteria)

An agent was given the following severity definition: *"Critical: Issues that threaten the system. Minor: Small issues."*

Which of the following is the fundamental problem arising from this definition?

**A)** The terms "critical" and "minor" are not technical jargon; the agent cannot understand them  
**B)** The definitions are prose-based; because "threatens the system" is a subjective expression, the agent calibrates differently on every run  
**C)** Two levels are not enough; at least five levels are required  
**D)** These definitions can only be used in the security domain and are not suitable for general code review  

---

### Question 3 — Task Statement 4.2 / 4.3 / 4.4 (null Diagnosis)

In an invoice extraction pipeline, the `invoice_date` field returns null for some documents. Investigation: the date *is present* in these documents, but in free-form formats such as "15 Ocak 2024" or "Jan 15, '24"; in table-formatted invoices (date in a separate cell) the field always comes out correctly.

**What is the most effective solution?**

**A)** Make the `invoice_date` field nullable — the information cannot be reliably extracted  
**B)** Add a retry loop with an error message: "invoice_date is null, the document contains a date, try again"  
**C)** Add 2-4 few-shot examples showing successful extraction from documents containing free-form dates (with `<example>` tags, with reasoning)  
**D)** Route these documents directly to human review  

---

### Question 4 — Task Statement 4.2 (Few-Shot Prompting)

A code review agent classifies certain cases inconsistently: it gives different answers on different runs to the question "Does this comment misdescribe the code's behavior, or is it an outdated note?" You have rewritten the instructions three times — the problem persists.

**What should you do in this situation?**

**A)** Make the instructions more detailed; explain every possible scenario separately  
**B)** Add few-shot examples for the 2-4 ambiguous cases; in each example, show the reasoning for why a decision was made  
**C)** Add a "don't flag if unsure" instruction (confidence-based filtering)  
**D)** Use a larger model — inconsistency is a capacity problem  

---

### Question 5 — Task Statement 4.3 / 4.4 (Semantic Validation)

An invoice extraction system uses `strict: true` tool_use. All JSON outputs conform to the schema. However, in the downstream system, for some invoices the sum of the line items does not equal the stated total.

**What is the most appropriate design to solve this problem?**

**A)** Remove tool_use, switch to prompt-based JSON — strict mode is breaking the arithmetic  
**B)** Add `calculated_total` to the schema; have the backend cross-check with its own sum; on mismatch, send a retry with an error message; if it still doesn't match after the retry, the document is probably internally contradictory → route to human review with `conflict_detected: true`  
**C)** Use a larger model — the small model is making arithmetic errors  
**D)** Make all fields "required" — so no value is left missing  

---

### Question 6 — Task Statement 4.3 (tool_choice)

A document pipeline has two stages: first the `extract_metadata` tool must extract the document's type and language, then depending on the type one of the `enrich_invoice` / `enrich_contract` tools must run. On the first call, the model must not jump directly to an enrichment tool.

**What is the correct `tool_choice` for the first call?**

**A)** `{"type": "auto"}` — the model figures out the order itself  
**B)** `{"type": "any"}` — the model definitely calls a tool  
**C)** `{"type": "tool", "name": "extract_metadata"}` — this tool is forced; on the next call, `auto` or `any`  
**D)** `{"type": "none"}` — have the type determined as text on the first call  

---

### Question 7 — Task Statement 4.4 (Retry Effectiveness Limit)

A contract extraction system returns null for the `penalty_rate` field. Two retries were sent ("penalty_rate must be in the document, look again") — still null. The document contains the following line: *"See Appendix B for the penalty rate."* Appendix B was not provided to the pipeline.

**What is the correct diagnosis and solution?**

**A)** The information is not in the document → make the `penalty_rate` field nullable, accept null  
**B)** The information is in an external document → retry won't work; add Appendix B to the context and re-run the extraction  
**C)** Increase the retry count to 5 — the model will eventually find it  
**D)** Add a few-shot example for `penalty_rate` — the model doesn't recognize the field  

---

### Question 8 — Task Statement 4.5 (SLA Calculation)

A company promises its customers that "an uploaded document is processed within 30 hours at most." Documents arrive irregularly throughout the day. For cost reasons, the Message Batches API will be used (processing upper bound 24 hours, no latency SLA).

**Which is the correct plan?**

**A)** Batch cannot be used — since the Batch API has no SLA, it is never used for any job with an SLA  
**B)** One batch per day (at 02:00 at night) — most batches finish within 1 hour anyway  
**C)** Send a batch at least every 6 hours (4 hours is safer): worst-case latency = wait + 24 hours ≤ 30 hours  
**D)** Send documents one by one as individual batches as they arrive — each document finishes within 24 hours at most  

---

### Question 9 — Task Statement 4.6 (Validation Architecture)

In an extraction pipeline, the model misses subtle errors (values placed in the wrong field, overlooked line items). There are three proposals: (1) add a "review your output carefully, fix errors" instruction to the extraction prompt; (2) enable extended thinking and increase the budget; (3) have the extraction validated by a separate Claude call that does not see the producer's reasoning.

**Which is the most effective?**

**A)** (1) — the cheapest; the model knows its own output best  
**B)** (2) — more thinking budget provides more validation  
**C)** (3) — the independent instance does not carry the production context; self-review instructions and thinking stay inside the same context  
**D)** (1) + (2) together are as effective as (3) and cheaper  

---

### Question 10 — Integrated Scenario (Entire Domain)

A team is building an invoice processing pipeline. Requirements:
1. Invoices arrive in different formats (table, text, nested list)
2. JSON must always conform to the schema
3. Semantic validation (total mismatch) is required
4. 2,000 invoices per week; cost is critical; there is a 36-hour processing commitment to the customer
5. Some invoices have no `payment_terms` information
6. High-confidence fields are automatic, low-confidence fields go to human review

**Which option correctly describes this system?**

**A)** Synchronous API (no batch because there is an SLA); all fields required; `tool_choice: auto`; no validation  
**B)** Few-shot with `<example>` tags for format diversity; `strict: true` tool_use (payment_terms nullable); `calculated_total` + backend validation + retry with error message; Batch API, submission at least every 12 hours (12 + 24 ≤ 36); routing by per-field enum confidence, calibrated with a document type × field accuracy table  
**C)** Multi-pass architecture with 50 instances per invoice; all fields required; no retry; synchronous API  
**D)** Prompt-based JSON; all validation to humans; Batch API with one submission per day; no few-shot  

---

## Answer Key and Explanations

---

### Question 1 → **B**

**Explanation:**

The exam guide's 4.1 Knowledge item: high false positive categories also erode trust in the *accurate* categories ("undermine confidence in accurate categories"). Trust is holistic; the noise of the code style category leads to security findings being ignored as well — which indirectly means missed bugs. The solution is isolation + criteria clarification + measurement on a labeled set + re-enabling.

- **(A) Wrong:** The "false positives are harmless" thesis is the thesis 4.1 refutes; loosening thresholds increases noise.
- **(C) Wrong:** "Don't report if unsure" = confidence-based filtering; it filters out both false positives and real findings in an uncontrolled way.
- **(D) Wrong:** The problem is criteria, not capacity.

**Concept covered:** Task 4.1 — False positive / trust relationship and isolation

---

### Question 2 → **B**

**Explanation:**

The expression "issues that threaten the system" is open to interpretation. Claude may calibrate this threshold differently on every run — the same code sometimes looks critical, sometimes minor. Solution: define severity with real code examples (with `<example>` tags).

- **(A) Wrong:** The terms are understood; the problem is that they are subjective.
- **(C) Wrong:** The number of levels is not the problem; concreteness is the problem.
- **(D) Wrong:** These definitions carry the same ambiguity problem in every domain.

**Concept covered:** Task 4.1 — Prose definition vs. calibration with code examples

---

### Question 3 → **C**

**Explanation:**

The first case of the "null triad": the information **is present** in the document, the model does not recognize the different format. This is 4.2's job — few-shot teaches the "in this format, the date is here" mapping. Working in table format but not in free text confirms that the problem is *format diversity* (the typical finding of the document type × field accuracy table).

- **(A) Wrong:** Nullable prevents fabrication when the information is *absent*; accepting null when the information is present is data loss (not 4.3's territory).
- **(B) Wrong:** Retry fixes a format *mismatch* (a date extracted in the wrong format); but a format the model does not recognize at all is missed by retry the same way every time — it needs to be taught.
- **(D) Wrong:** Handing an automatically solvable problem to humans does not scale.

**Concept covered:** Task 4.2 — null triad (few-shot vs nullable vs retry)

---

### Question 4 → **B**

**Explanation:**

Rewriting the instructions was tried repeatedly — it didn't work. This shows that the amount of instruction is not the problem. The solution for inconsistency in ambiguous cases: show examples of those ambiguous cases + their reasoning (exam guide: "*show reasoning for why one action was chosen over plausible alternatives*").

- **(A) Wrong:** Lengthening the instructions was already tried and failed.
- **(C) Wrong:** Confidence-based filtering; the real problem is *when* the decision is made, not confidence.
- **(D) Wrong:** The problem is not model capacity, but how ambiguous cases are handled.

**Concept covered:** Task 4.2 — Few-shot + reasoning for ambiguous cases

---

### Question 5 → **B**

**Explanation:**

Strict tool_use eliminates schema/syntax errors — but a total mismatch is a **semantic** error (exam guide: "*strict JSON schemas … do not prevent semantic errors, e.g., line items that don't sum to total*"). The solution is layered: `calculated_total` + the backend's independent calculation → retry with error message (if a line was misread, it gets fixed) → if it still doesn't match, the document is internally contradictory, retry cannot solve this → `conflict_detected` + human. The option establishes 4.4's "retry effective / not effective" distinction in a single flow.

- **(A) Wrong:** Prompt-based JSON loses the syntax guarantee; strict does not affect arithmetic.
- **(C) Wrong:** Changing the model does not replace the validation layer; no model can "correctly" sum a contradictory document.
- **(D) Wrong:** Required fields increase the fabrication risk and do not validate the total.

**Concept covered:** Task 4.3 + 4.4 — The limit of strict, semantic validation, retry → conflict flow

---

### Question 6 → **C**

**Explanation:**

The exam guide's Skills item, verbatim: "*Forcing a specific tool with `tool_choice: {"type": "tool", "name": "extract_metadata"}` to ensure a particular extraction runs **before enrichment steps**.*" In a sequential flow, `disable_parallel_tool_use: true` is also added.

- **(A) Wrong:** `auto` does not even guarantee a tool call; the order is left to the prompt (probabilistic).
- **(B) Wrong:** `any` guarantees a tool call but not *which one* — the model may jump directly to `enrich_invoice`.
- **(D) Wrong:** `none` prevents any tool call in this turn; the text output is unstructured and requires an extra call.

**Concept covered:** Task 4.3 — tool_choice modes, forcing a specific tool

---

### Question 7 → **B**

**Explanation:**

The exam guide's retry-ineffective example: "*information exists only in an external document not provided*". The document explicitly references Appendix B — the information is *reachable* but not in the context. Retry looks at the same document, null again. The solution is not nullable, but **adding the missing document**; then the extraction (with retry if needed) works.

- **(A) Wrong:** Nullable is correct when the information is *nowhere*; here there is a reference — accepting null is data loss.
- **(C) Wrong:** The retry count does not produce information the model does not have.
- **(D) Wrong:** Few-shot teaches "how to extract"; as long as the information is not in the context, examples won't help.

**Concept covered:** Task 4.4 — Retry effectiveness limit (external document)

---

### Question 8 → **C**

**Explanation:**

Exam guide Skills: "*4-hour windows to guarantee 30-hour SLA with 24-hour batch processing*". Formula: worst-case latency = waiting for the next submission (P) + 24 hours processing ≤ SLA → P ≤ 30 − 24 = **6 hours**. The guide's 4-hour window leaves a 2-hour margin.

- **(A) Wrong:** "No latency SLA" ≠ "no SLA can be given"; the 24-hour upper bound is enough to do the calculation. If the SLA were ≤ 24 hours, A would be correct.
- **(B) Wrong:** With one submission per day, a document arriving at 02:05 waits 24 hours + 24 hours processing = 48 > 30. "Most finish within 1 hour" is an average, not a guarantee.
- **(D) Wrong:** A batch per document defeats the purpose of batching (bulk submission) and creates rate limit / management overhead; also "finishes within 24 hours" is again an upper bound — technically it meets the SLA, but it is not the *planning* the question asks for.

**Concept covered:** Task 4.5 — Calculating submission frequency from the SLA

---

### Question 9 → **C**

**Explanation:**

Exam guide 4.6 Knowledge: "*Independent review instances (without prior reasoning context) are more effective at catching subtle issues than **self-review instructions or extended thinking**.*" A validation problem is not solved by *doing more* in the same session; it is solved by *changing the context*.

- **(A) Wrong:** "Knows its own output best" is exactly the source of the problem — it inherits the production assumptions.
- **(B) Wrong:** Thinking makes it think longer, not *from a different angle*; it operates inside the production context.
- **(D) Wrong:** The sum of two inadequate methods does not solve the context problem.

**Concept covered:** Task 4.6 — The limit of self-review; the instruction / thinking / independent instance triad

---

### Question 10 → **B**

**Explanation:**

Each requirement maps to a technique:

| Requirement | Technique |
|------------|--------|
| Format diversity | Few-shot with `<example>` tags (Task 4.2) |
| Schema-conforming JSON | `strict: true` tool_use (Task 4.3) |
| Semantic validation | `calculated_total` + backend calculation + retry with error message (Task 4.4) |
| Cost + 36-hour commitment | Batch API; P ≤ 36 − 24 = 12 hours → submission at least every 12 hours (Task 4.5) |
| payment_terms sometimes absent | Nullable field (Task 4.3) |
| Confidence-based routing | Per-field enum confidence; calibration with the document type × field table (Task 4.6) |

- **(A) Wrong:** "No batch because there is an SLA" — 36 > 24, batch is possible; required fields create fabrication; `auto` gives no guarantee; no validation.
- **(C) Wrong:** The number of passes depends on the number of files; "50 instances per invoice" is the absence of cost intuition; required-all fabrication risk; no retry.
- **(D) Wrong:** Prompt-based JSON is unreliable; one submission per day is 24 + 24 = 48 > 36 (SLA violation); leaving all validation to humans does not scale.

**Concept covered:** Task 4.1–4.6 integrated application

---

## Results

| Score | Assessment |
|------|---------------|
| 10/10 | Excellent — You are ready for the exam |
| 8-9/10 | Good — Review the Task Statements you missed |
| 6-7/10 | Improving — Re-study the Tasks covered by the questions you got wrong |
| 5 and below | Re-read the fundamental concepts, then retake the test |

---

## Which Question Covers Which Task?

| Question | Task Statement |
|------|----------------|
| 1 | 4.1 — Explicit Criteria (False positive / trust, isolation) |
| 2 | 4.1 — Explicit Criteria (Severity calibration) |
| 3 | 4.2 (+4.3, 4.4) — null diagnosis: few-shot vs nullable vs retry |
| 4 | 4.2 — Few-Shot (Ambiguous decision inconsistency) |
| 5 | 4.3 + 4.4 — The limit of strict, semantic validation, retry → conflict |
| 6 | 4.3 — tool_choice (forcing a specific tool) |
| 7 | 4.4 — Retry effectiveness limit (external document) |
| 8 | 4.5 — Calculating submission frequency from the SLA |
| 9 | 4.6 — Self-review vs thinking vs independent instance |
| 10 | 4.1–4.6 — Integrated scenario |

---

## Bonus Drill — Quick Discrimination (answers below)

Exam points covered in the lecture notes that did not fit into the main test. Give a one-word/one-line answer for each:

1. In a 500-document batch, 12 requests are `expired` and 8 requests are `errored` ("too large"). Which is resubmitted unchanged, and which is resubmitted chunked?
2. Manual extended thinking is enabled; you sent `tool_choice: {"type": "any"}`. What happens?
3. In a 14-file PR review there is inconsistent depth and contradictory comments. Why don't "a larger context window" and "run 3 times, majority vote" solve it?
4. All four few-shot examples contain a `TODO` comment; the agent started skipping bugs without a `TODO`. The rule?
5. A pipeline script hangs with `claude "Analyze PR"`; does the `--batch` flag solve it?
6. In extraction, is confidence reported per finding or per field; and with which table is calibration done?

**Answers:** (1) `expired` → as is; `errored` too large → chunk it. (2) Error — `any`/`tool` are not supported with manual thinking; use `auto` (+ `strict`). (3) The problem is not fit but *attention dilution*; a larger window can increase dilution, majority vote experiences the same dilution three times and masks the inconsistency → split the pass. (4) Examples must be *diverse*; a superficial shared feature teaches an unwanted pattern. (5) No — there is no such flag as `--batch`; the answer is `-p`; the Message Batches API is a separate Messages API feature. (6) Per field (enum confidence + `confidence_reason`); calibrated with the document type × field accuracy matrix.
