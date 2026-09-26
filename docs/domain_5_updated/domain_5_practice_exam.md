# Domain 5 Practice Exam: Context Management and Reliability

## General Information

- **Domain Weight:** 15% of the exam
- **Number of Questions:** 10 (+ a 5-question additional practice section)
- **Passing Threshold:** 8/10
- **Difficulty:** Exam-level scenario-based questions — options are similar in length and each is partially plausible
- **Coverage:** All 6 Task Statements (5.1 – 5.6)

---

> Answer the questions first, then check the answer key. The scenarios from the lesson files do not repeat in this exam; each question tests the concept from a new angle.

---

## Questions

---

### Question 1 — Task Statement 5.2 (Escalation calibration) — Exam Guide Q3

A customer support agent's first-contact resolution rate is 55%; the target is 80%. Logs show the agent escalating simple cases such as standard damage replacements with photo evidence, while attempting to resolve complex situations requiring policy exceptions on its own.

**What is the most effective way to improve escalation calibration?**

**A)** Add explicit escalation criteria with few-shot examples to the system prompt showing when to escalate and when to resolve autonomously.

**B)** Have the agent report a 1–10 confidence score before each response; if the score is below a threshold, automatically route the request to a human.

**C)** Build a separate classifier model trained on historical tickets; have it predict which requests require escalation before the main agent begins processing.

**D)** Measure customer frustration with sentiment analysis; auto-escalate when a negative sentiment threshold is exceeded.

---

### Question 2 — Task Statement 5.3 (Error propagation) — Exam Guide Q8

A web search subagent times out while researching a complex topic. You need to design how this error information flows to the coordinator agent.

**Which approach best enables intelligent recovery?**

**A)** Return structured error context to the coordinator including the error type, the attempted query, any partial results, and possible alternative approaches.

**B)** Implement automatic retry with exponential backoff inside the subagent; when all attempts are exhausted, return a generic "search unavailable" status to the coordinator.

**C)** Catch the timeout inside the subagent and return an empty result set marked as successful.

**D)** Propagate the timeout exception directly to a top-level handler and terminate the entire research workflow.

---

### Question 3 — Task Statement 5.1 (Multi-issue session)

A customer support agent using a case facts block works flawlessly in single-issue conversations. A customer opens returns for two different orders and an invoice dispute in the same conversation; at turn 7, the agent responds to the invoice dispute with the refund amount of the first order.

**What is the root cause and the solution?**

**A)** The case facts block was corrupted during summarization; move the block outside the summarized history and include it in every prompt.

**B)** Tool results have filled the context; trim order queries to the fields needed for the return before adding them to context.

**C)** A single case facts block cannot represent multiple issues; build a separate context layer with a structured record per issue and an active-issue field.

**D)** The conversation history is not being sent in full; include all previous turns in subsequent requests.

---

### Question 4 — Task Statement 5.1 (Lost in the middle)

A coordinator concatenates the research output of 7 subagents and passes it to the synthesis agent. The synthesis report handles the findings of the first two and last two subagents in detail but barely uses the findings of subagents 3–5. Each subagent output is structured and short.

**Which is the most effective fix?**

**A)** Add an instruction to the synthesis agent: "weigh all subagent findings equally."

**B)** Redesign the subagents to return structured data instead of verbose content.

**C)** Reduce the number of subagents to 4; fewer inputs are processed more evenly.

**D)** Have the coordinator place a key-findings summary at the top of the merged input and separate each subagent output with explicit section headers.

---

### Question 5 — Task Statement 5.3 (Access failure vs valid empty result)

A research coordinator receives `{"status": "success", "results": []}` from the document analysis subagent. Logs show the same query returned 9 results an hour earlier and that the document store was under maintenance at the time. The coordinator reported "no documents on this topic."

**What is the root cause?**

**A)** The coordinator should have retried the query once more upon seeing the empty result; empty results are always retried.

**B)** The subagent's response schema does not distinguish an access failure from a valid empty result; the maintenance outage propagated as "success + empty array."

**C)** The coordinator should have sent the same query to a second subagent to verify the result.

**D)** The document store's maintenance is an external event; there is nothing the coordinator can do.

---

### Question 6 — Task Statement 5.4 (Context degradation mechanism)

An architect notices that an agent doing codebase exploration drifts toward "typical patterns" in long sessions and explains to the team: "When the context window fills up, the oldest messages get dropped, so we should switch to a model with a larger window."

**What is the assessment of this explanation and recommendation?**

**A)** Explanation correct, recommendation correct: as the window grows, fewer messages are dropped and degradation is delayed.

**B)** Explanation wrong: the API does not drop messages; it returns an error if the limit is exceeded, and Claude Code summarizes. Degradation arises from attention budget dilution before the limit (context rot) and from summary loss after compaction; enlarging the window does not fix attention quality.

**C)** Explanation correct, recommendation wrong: messages do get dropped, but the solution is to run `/compact` more often.

**D)** Explanation wrong: the cause of degradation is the model forgetting the instruction; adding "be specific" to the system prompt is enough.

---

### Question 7 — Task Statement 5.4 (Scratchpad vs CLAUDE.md, /compact vs /clear)

In a 3-hour exploration session with Claude Code, a context-full warning appears. The findings exist only inside the conversation. The developer will continue the same work. The team is debating two proposals: (1) write the findings to CLAUDE.md and run `/clear`, (2) have the findings written to NOTES.md and run `/compact` with a focus instruction.

**Which is correct and why?**

**A)** (1): CLAUDE.md is loaded automatically in every session, the findings are never lost; `/clear` gives the cleanest context.

**B)** Both are wrong: the correct solution is to disable auto-compact and continue until the window is full.

**C)** (2): NOTES.md is the session's working memory, whereas CLAUDE.md is the persistent instruction file — writing findings there bloats every session; `/compact <focus>` summarizes the narrative while preserving critical findings, whereas `/clear` resets without summarizing.

**D)** Both are correct: the file choice and the command choice are matters of preference.

---

### Question 8 — Task Statement 5.5 (Stratified sampling + second signal)

An extraction system running with calibrated field-level confidence auto-accepts fields above 92%, and the quality team manually checks a plain random sample of 50 extractions per week. After two months, two problems surface: (1) on a new vendor's invoice template, the model extracts a wrong due date with high confidence; because its volume is low, it never appeared in the 50-item sample; (2) invoices where the line-item sum does not match the grand total on the document passed with 95% model confidence.

**Which design solves both problems together?**

**A)** Split sampling into document type × field × confidence band strata (a minimum number of samples per stratum, including from high confidence); add a second signal to routing: if document validation finds a conflict (`conflict_detected`), send to human review regardless of confidence.

**B)** Raise the weekly sample to 200 and raise the auto-accept threshold to 98%.

**C)** Route the new vendor's invoices to human review and add a "check the totals" instruction to the model.

**D)** Ask for the confidence score as an enum and send everything other than `high` to a human.

---

### Question 9 — Task Statement 5.6 (Conflict — who decides)

The document analysis subagent finds different growth rates in two reliable reports (45% and 38%, different methodologies). The system designer is debating three options.

**Which one conforms to the exam guide's role distribution?**

**A)** Have the subagent evaluate the methodology and return the single value it finds more reliable; the coordinator and synthesis proceed with that value.

**B)** Have the subagent return the mean and standard deviation of the two values; have the report write it as a range.

**C)** Have the subagent return both values; have the synthesis agent pick the more recent one and write a single figure, noting the other in a footnote.

**D)** Have the subagent annotate both values with source, date, characterization and methodology note and complete the analysis; have the coordinator make the reconciliation decision; have synthesis show both in the "contested findings" section of the report with their sources.

---

### Question 10 — Integrated Scenario (Whole Domain)

A company operates a multi-agent system that includes customer support + research + document extraction. Five problems are reported:

1. When escalated to a representative, the customer has to explain the order number and their request from scratch
2. Simple damage replacements are escalated, while requests past the warranty period are approved by the agent
3. The research subagent retries with backoff on timeout, then returns "source unavailable"; the coordinator cannot try an alternative source
4. The synthesis report writes the figure the IEA called a "preliminary estimate" as if it were a definitive measurement
5. In an extraction system reporting 97% aggregate accuracy, a low-volume document type never appears in the weekly plain random sample

**Which option matches the five problems with the correct concept?**

**A)**
1. Summarize the conversation history
2. Lower the sentiment threshold
3. Increase the retry count
4. A "cite sources" instruction to the synthesis agent
5. Increase the sample size

**B)**
1. Case facts handoff context in the `escalate_to_human` call
2. Explicit escalation criteria with few-shot examples (two-way calibration)
3. Structured error context instead of a generic status (retry is right, the message is wrong)
4. Preserve the source's characterization in the claim-source mapping
5. Document type × field × confidence band stratified sampling

**C)**
1. Larger context window
2. Train a separate escalation classifier
3. Halt the workflow on timeout, request human intervention
4. Have a post-synthesis verification agent search for sources
5. Raise the auto-accept threshold to 99%

**D)**
1. Remove escalation, let the agent resolve everything
2. Escalation based on the model's confidence score
3. Have the subagent catch the error and return an empty result
4. Remove the figure from the report
5. Remove the low-volume type from the pipeline

---

## Answer Key and Explanations

---

### Question 1 → **A**

**Explanation:** The exam guide's own question and rationale: the root cause is **unclear decision boundaries**; explicit criteria with few-shot examples address this directly and are the **proportionate first intervention** before adding infrastructure. Calibration is broken in both directions (simple ones escalated, complex ones handled autonomously); but examples show both boundaries.

- **(B) Wrong:** An LLM's self-reported confidence is not calibrated — the agent is already misplacing its confidence on hard cases. A threshold tries to solve a two-way problem with a one-way measure.
- **(C) Wrong:** Over-engineering — requires labeled data and ML infrastructure; prompt optimization has not yet been tried.
- **(D) Wrong:** Solves a different problem; sentiment does not correlate with case complexity.

**Concept covered:** Task 5.2 — Escalation criteria with few-shot examples, proportionality ladder

---

### Question 2 → **A**

**Explanation:** Structured error context gives the coordinator the information it needs to decide: retry with a modified query, an alternative approach, or continue with partial results.

- **(B) Wrong:** The most tempting wrong option. Local retry (layer 1) is correct; but the generic "search unavailable" (layer 2) hides context from the coordinator — which query, what kind of error, whether partial results exist remain unknown.
- **(C) Wrong:** Silent suppression — marking the error as success blocks every form of recovery and creates the risk of incomplete research output.
- **(D) Wrong:** Unnecessarily terminates the entire workflow when recovery strategies could have worked.

**Concept covered:** Task 5.3 — Three anti-patterns, two-layer recovery

---

### Question 3 → **C**

**Explanation:** Case facts are for a single case; for multi-issue sessions the exam guide calls for "*structured issue data … into a separate context layer*". A record per issue + an active-issue field frees the agent from ambiguity about which issue it is on.

- **(A) Wrong:** The problem is not summarization of the block, it is its *structure*: a single `order_id` and a single `refund_amount` cannot represent three issues. The block is already kept outside.
- **(B) Wrong:** Tool result bloat produces a different symptom (budget exhaustion); not the mixing of issues.
- **(D) Wrong:** Even if the history is sent in full, the single-block structure cannot separate issues; a structural problem.

**Concept covered:** Task 5.1 — Multi-issue session context layer

---

### Question 4 → **D**

**Explanation:** Lost-in-the-middle appears, in the exam guide's language, in "*aggregated inputs*"; the problem is in the format of the coordinator *doing the merging*. Solution: key-findings summary at the top + explicit section headers.

- **(A) Wrong:** An instruction does not change the attention mechanism; the content in the middle is still in the middle.
- **(B) Wrong:** The question already says the outputs are structured and short — upstream optimization has been done; the problem is the merge layout.
- **(C) Wrong:** Narrows the scope; with 4 subagents, the 2nd and 3rd still end up in the middle.

**Concept covered:** Task 5.1 — Lost in the middle (aggregated inputs)

---

### Question 5 → **B**

**Explanation:** If the same JSON shape describes two different realities (unreachable / no match), the schema is broken. The exam guide wants the distinction "*in error reporting*": `source_reached` / `failure_type` fields. The maintenance outage propagated as silent suppression.

- **(A) Wrong:** "Always retry empty results" is the reverse mistake: it re-queries valid empty results over and over. The retry decision requires *knowing* the access status; the schema doesn't provide it.
- **(C) Wrong:** A second subagent returns the same answer with the same broken schema.
- **(D) Wrong:** The outage is an external event, but its *staying silent* is the system's fault; had a structured error arrived, the coordinator could have waited and retried or added a coverage note.

**Concept covered:** Task 5.3 — Access failure vs valid empty result, distinction in the response schema

---

### Question 6 → **B**

**Explanation:** The Messages API does not drop messages; it returns an error if the limit is exceeded; Claude Code auto-compacts as it nears the limit. Degradation arises through two mechanisms: context rot (attention budget) before the limit, summary loss after compaction. In the rationale for Q12: "*larger context windows don't solve attention quality issues*".

- **(A) Wrong:** Both the explanation and the recommendation are wrong; enlarging the window makes you experience the same context pollution over a wider area.
- **(C) Wrong:** The explanation is still wrong; more frequent compaction without a focus instruction and a scratchpad increases summary loss.
- **(D) Wrong:** The problem is not the instruction, it is attention and summarization; "be specific" does not bring back inaccessible information.

**Concept covered:** Task 5.4 — Context degradation mechanism, the large-window distractor

---

### Question 7 → **C**

**Explanation:** The scratchpad (NOTES.md) is the session's working memory, CLAUDE.md is the project's persistent instruction file (Domain 3.1); if exploration findings are written to CLAUDE.md, they bloat every session and pollute unrelated sessions. `/compact <focus>` summarizes the narrative while continuing the same work and preserves critical findings; `/clear` does not summarize, it resets — used when switching to unrelated work.

- **(A) Wrong:** CLAUDE.md's "never lost" property is precisely the problem; `/clear` throws away the context entirely for work that will continue.
- **(B) Wrong:** Disabling auto-compact means getting an error when you hit the limit.
- **(D) Wrong:** The file choice (session memory vs persistent instruction) and the command choice (summarize vs reset) are not preferences but semantic differences.

**Concept covered:** Task 5.4 — Scratchpad vs CLAUDE.md, `/compact` vs `/clear`

---

### Question 8 → **A**

**Explanation:** Two problems, two mechanisms. (1) Plain random sampling does not represent the low-volume type — the aggregate metrics trap repeats itself in sampling; stratified sampling (document type × field × confidence band, including from high confidence) catches the novel error pattern. (2) The model can pick a value with high confidence without noticing the contradictory document; the exam guide sends low confidence **or** a contradictory/ambiguous source document to a human — `conflict_detected` is the second door.

- **(B) Wrong:** A larger plain sample still sees the low-volume type rarely; raising the threshold does not measure document inconsistency.
- **(C) Wrong:** Vendor-specific routing patches the symptom (it won't catch the next new template); the sum check is deterministic validation, not left to the model.
- **(D) Wrong:** A change in representation does not change calibration; sending everything other than `high` to humans chokes capacity, and the contradictory document still passes with `high`.

**Concept covered:** Task 5.5 — Stratified sampling, two routing signals

---

### Question 9 → **D**

**Explanation:** The exam guide's role distribution: the document analysis subagent annotates the conflicting values and *completes* the analysis; the **coordinator** makes the reconciliation decision before synthesis; synthesis shows both with their sources in the report under the "well-established / contested" distinction.

- **(A) Wrong:** The subagent returning a single value based on its "more reliable" judgment is an arbitrary choice; it hides information from the upper layers.
- **(B) Wrong:** A mean/range produces a number no source has stated; it makes the methodology difference invisible.
- **(C) Wrong:** "More recent" is also an arbitrary rule (valid only for revisions), and the synthesis agent is not the reconciliation layer.

**Concept covered:** Task 5.6 — Conflict handling, role distribution, report skeleton

---

### Question 10 → **B**

**Explanation:** Each problem matches a different Domain 5 concept:

| Problem | Concept | Solution |
|-------|--------|-------|
| 1. Explaining from scratch on escalation | Task 5.2 + 5.1 — Handoff context | `escalate_to_human` + case facts |
| 2. Simple ones escalated, exceptions approved | Task 5.2 — Two-way calibration (Q3) | Explicit criteria with few-shot examples |
| 3. Generic status after retry | Task 5.3 — Anti-pattern 3 (Q8-B) | Structured error context |
| 4. "Preliminary estimate" → definitive measurement | Task 5.6 — Source characterization | `source_characterization` in the claim-source mapping |
| 5. Low-volume type absent from the sample | Task 5.5 — Stratified sampling | Document type × field × confidence band |

- **(A) Wrong:** Every solution is superficial: summarization does not provide handoff context; a sentiment threshold does not fix calibration; the retry count does not solve the generic message; an instruction does not create the characterization; a larger plain sample still misses the low-volume type.
- **(C) Wrong:** Disproportionate/wrong: a large window is unrelated to handoff; a classifier is over-engineering before the prompt has been tried; halting the workflow is an anti-pattern; searching for sources afterward does not bring back the characterization; a 99% threshold does not solve the stratum problem.
- **(D) Wrong:** Extreme solutions: removing escalation is a policy violation; the confidence score is an unreliable trigger; returning an empty result is silent suppression; removing the figure is information loss; removing the type is data loss.

**Concept covered:** Task 5.1–5.6 integrated application

---

## Results

| Score | Assessment |
|------|---------------|
| 10/10 | Excellent — You are ready for the exam |
| 8-9/10 | Good — Review the Task Statements you missed |
| 6-7/10 | Improving — Re-study the Tasks covered by the questions you got wrong |
| 5 and below | Re-read the core concepts, then retake the exam |

---

## Which Task Does Each Question Cover?

| Question | Task Statement |
|------|----------------|
| 1 | 5.2 — Escalation criteria with few-shot examples (Exam Guide Q3) |
| 2 | 5.3 — Three anti-patterns, two-layer recovery (Exam Guide Q8) |
| 3 | 5.1 — Multi-issue session context layer |
| 4 | 5.1 — Lost in the middle (aggregated inputs) |
| 5 | 5.3 — Access failure vs valid empty result, response schema |
| 6 | 5.4 — Context degradation mechanism |
| 7 | 5.4 — Scratchpad vs CLAUDE.md, `/compact` vs `/clear` |
| 8 | 5.5 — Stratified sampling + contradictory document signal |
| 9 | 5.6 — Conflict handling, role distribution |
| 10 | 5.1–5.6 — Integrated scenario |

---

## Additional Practice Section (5 questions — not scored)

### Extra 1 — 5.1 (Subagent metadata)

The synthesis agent reports the findings "unemployment 5.2%" and "unemployment 4.8%" from two subagents as a conflict. The subagent outputs contain the fields `{claim, source, relevance}`.

**A)** Add an instruction to the synthesis agent: "resolve conflicts by source reliability."
**B)** Make publication/data collection date, source location and methodology fields mandatory in the subagent output schema; seeing the dates, synthesis distinguishes a temporal difference from a conflict.
**C)** Merge the two subagents into a single subagent; a single source produces no conflicts.
**D)** Give the synthesis agent web search and ask it to find the dates itself.

**Answer: B.** 5.1's metadata item and 5.6's temporal awareness are the same solution: dates are mandatory. (A) source reliability does not resolve a temporal difference; (C) loss of coverage; (D) re-searching for a date the subagent already knows.

---

### Extra 2 — 5.2 (Policy silent)

The policy says "returns of gifted products are processed with a gift receipt." A customer requests a return without a gift receipt, using the purchaser's order number. The policy does not cover this case.

**A)** Since the order number can be verified, process the return; the policy is interpreted broadly.
**B)** Refuse, saying "returns cannot be processed without a gift receipt"; the policy requires it.
**C)** The policy is silent in this case — a policy gap; escalate with handoff context and explain to the customer.
**D)** Decide based on how angry the customer is.

**Answer: C.** The policy defines one path but does *not prohibit* anything outside that path — it is silent. (A) exceeding authority; (B) "absent" ≠ "forbidden", refusing is also stepping outside the policy; (D) unreliable trigger.

---

### Extra 3 — 5.3 (The coordinator's three options)

The coordinator receives a structured error from the web search subagent: `failure_type: transient, attempted: "query X, 3 retries", partial_results: 2 of 5 sources, alternatives_untried: ["Google Scholar"]`.

**What are the coordinator's options?**

**A)** Only halting the workflow and waiting for a human.
**B)** Retrying with a modified query, trying the alternative source (Google Scholar), or continuing with 2 sources and adding a coverage note to the report.
**C)** Trying the same query on the same source 10 more times.
**D)** Discarding the partial results and starting from scratch.

**Answer: B.** The trio from Q8's rationale. Structured context is exactly what makes these three decisions possible; with a generic status, none of them could have been chosen.

---

### Extra 4 — 5.4 (Manifest vs resume)

Two designs are being debated for post-crash recovery of a multi-agent system: (1) store each subagent's `session_id` and restore the full transcript with `resume`; (2) have each agent write a manifest containing completed/pending tasks and key findings, which the coordinator injects into the prompt.

**A)** (1): The transcript is complete, no information is lost.
**B)** (2): The manifest is compact application state; the transcript is verbose, consumes the context budget when restored, and is machine-bound — the SDK docs also recommend capturing results as application state and providing them to a new session.
**C)** Both give the same result.
**D)** Neither: more reliable infrastructure is needed to prevent the crash.

**Answer: B.** The exam guide's answer is the manifest; even the current SDK says "don't rely on session resume".

---

### Extra 5 — 5.6 (Revision)

The same statistics institution publishes "2025 inflation 38.2% (flash)" in February and "2025 inflation 37.9% (final)" in May. The report presents the two values side by side as "data from different periods."

**A)** Correct: the publication dates differ, therefore a temporal difference.
**B)** Wrong: the two values measure the same period (2025); this is a revision. The final value stands, with the note "flash was 38.2%, revised" and both dates preserved.
**C)** Wrong: the average should be taken.
**D)** Wrong: the flash value is authoritative because it was the first publication.

**Answer: B.** A publication date difference ≠ a data period difference. In a revision the current value stands, the characterization and dates are preserved.
