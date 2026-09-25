# Domain 1 — Practice Exam

## Agentic Architecture & Orchestration (27% of Exam)

**Distribution (16 questions):**
- 4 questions → Agentic loops (1.1): Q1, Q3, Q11, Q12
- 5 questions → Orchestration & context (1.2, 1.3): Q2, Q4, Q7, Q14, Q16
- 3 questions → Enforcement & hooks (1.4, 1.5): Q5, Q6, Q13
- 2 questions → Decomposition (1.6): Q8, Q9
- 2 questions → Session management (1.7): Q10, Q15

**Passing criterion:** 13+/16 (~80%)

---

## Question 1 (Task Statement 1.1)

> A customer support agent runs with the following loop logic:
>
> ```python
> for i in range(10):
>     response = call_claude(messages)
>     if "final answer" in response.content[0].text.lower():
>         return response
>     # execute tools and continue
> ```
>
> Users report three different problems:
> 1. The agent sometimes stops after 10 iterations without giving an answer
> 2. The agent sometimes stops even though it said "Here's my final answer so far, let me search for more details"
> 3. On some requests the loop crashes with `AttributeError: 'ToolUseBlock' object has no attribute 'text'`
>
> **Which approach fixes all three problems?**
>
> **A)** Raise the iteration cap from 10 to 25, check for "task complete" instead of "final answer", and wrap the `.text` access in `try/except`.
>
> **B)** Check the `response.stop_reason` field — exit on `"end_turn"`, and on `"tool_use"` execute every tool_use block in the entire `response.content` list and continue.
>
> **C)** Ask Claude "Are you done?" on every iteration and parse the answer.
>
> **D)** Remove the iteration cap and check only `response.content[0].type == "text"`.

### Correct Answer: B

**Why B is correct:** The code contains three separate bugs: an arbitrary iteration cap (the 10-loop limit, stopping silently), natural language parsing (searching for the phrase "final answer"), and the `content[0]` assumption (if the first block is a `tool_use` block there is no `.text` → crash). Checking `stop_reason` fixes the first two; iterating over the whole `content` list fixes the third. No guessing, parsing, or first-block assumption is needed.

**Why A is wrong:** Raising the cap, searching for a different string, and swallowing the error with `try/except` keeps all three anti-patterns alive. The number, the string, and the error handling change, but the structural problems remain — in particular, `try/except` hides the crash but doesn't stop the loop from making the wrong decision.

**Why C is wrong:** A different version of the natural language parsing anti-pattern. Claude saying "yes, I'm done" is just as ambiguous and unreliable; it also adds an extra API call to every iteration.

**Why D is wrong:** The content-type check anti-pattern. Claude can return text and tool_use blocks in the same response. Exiting on seeing text causes premature termination — and the `content[0]` assumption is still there.

---

## Question 2 (Task Statement 1.2)

> A multi-agent research system produces a report on "global food security challenges." The system consists of a coordinator, a web search subagent, a document analysis subagent, and a synthesis subagent.
>
> The final report is well-written but covers only climate change and water scarcity. Supply chain disruptions, political instability, and biotechnology are completely missing.
>
> When tested independently, the web search subagent returns excellent results for the query "food security supply chain disruption."
>
> **What is the root cause?**
>
> **A)** The web search subagent's search algorithm is inadequate.
>
> **B)** The synthesis subagent filtered out some topics.
>
> **C)** The coordinator's task decomposition is incomplete — it only created subtasks for climate and water.
>
> **D)** The subagents can't access the coordinator's full conversation history.

### Correct Answer: C

**Why C is correct:** A narrow decomposition failure. The subagents work perfectly when tested independently — the problem isn't with them. The coordinator decomposed "global food security challenges" into only climate and water. Supply chain, political instability, and biotechnology were never created as subtasks. Trace the failure to its origin — the coordinator's decomposition.

**Why A is wrong:** The web search subagent returns excellent results in independent testing. Its search capability is fine — it was simply never asked about those topics.

**Why B is wrong:** The synthesis subagent only synthesises the data it receives. If no research on supply chains was done, there's nothing to filter out.

**Why D is wrong:** The isolation principle trap. Giving subagents the full conversation history is not the right architectural approach. The fix is to broaden the coordinator's decomposition.

---

## Question 3 (Task Statement 1.1)

> In an agentic loop, Claude returns the following response:
>
> - `response.content[0]` → type: "text", text: "I found some relevant data. Let me query the sales database for Q3 numbers."
> - `response.content[1]` → type: "tool_use", name: "query_database", input: {...}
> - `response.stop_reason` → "tool_use"
>
> **What should the loop do?**
>
> **A)** Show the text block to the user and terminate the loop — Claude gave a text response.
>
> **B)** Execute the `query_database` tool, append the result to the conversation history as a `tool_result` block, and send it back to Claude. The text block may optionally be shown to the user as an interim progress message (streaming).
>
> **C)** Present the text block to the user as the final answer, reset the conversation history, and start a new conversation with the tool result.
>
> **D)** Ask Claude "Do you approve this tool call?"

### Correct Answer: B

**Why B is correct:** `stop_reason` is `"tool_use"` — that's the only signal that matters. Claude returned both a text block and a tool_use block, but `stop_reason` says clearly "I need to continue." Execute the tool, append the result to the existing history as a `tool_result` block matched by `tool_use_id`, send it back to Claude. The text block is Claude "thinking out loud" — showing it to the user as a progress message is harmless, but the loop decision is made from `stop_reason`.

**Why A is wrong:** The content-type check anti-pattern. Terminating the loop because a text block exists is a premature exit. `stop_reason` is still `"tool_use"`.

**Why C is wrong:** Two mistakes at once: treating the text block as the *final* answer (premature termination) and resetting the history. The tool result must be sent as a continuation of the existing history that contains Claude's own tool_use block; if the history is reset, there's no `tool_use` block for the `tool_result` to match and the API rejects the request.

**Why D is wrong:** In an agentic loop Claude makes its own decisions. Asking Claude to approve every tool call is meaningless — if human approval is required, that's done with an `ask` decision in a `PreToolUse` hook, not with an extra Claude call in the loop.

---

## Question 4 (Task Statement 1.3)

> A coordinator passes the web search subagent's findings to the synthesis subagent. The handoff is in the following format:
>
> ```
> "Solar energy capacity grew 45% in 2024. Wind energy investments
> reached $120B. Geothermal projects expanded in Iceland and Kenya."
> ```
>
> The synthesis subagent writes a good report but cites no sources for any claim.
>
> **What is the most effective fix?**
>
> **A)** Add a "cite a source for every claim" instruction to the synthesis subagent's system prompt.
>
> **B)** Switch the coordinator's context passing mechanism to a structured metadata format — map every claim to its source URL, document name, and page number.
>
> **C)** Tell the web search subagent to return its results in APA format.
>
> **D)** Give the synthesis subagent the coordinator's full conversation history.

### Correct Answer: B

**Why B is correct:** The problem is in context passing. The coordinator passes plain text — the synthesis agent doesn't know which claim came from which source. The fix: a structured metadata format — a JSON structure mapping every claim to a source URL, document name, and page number; that schema goes into the web search subagent's prompt so the structure is created at the start of the chain. With this structured data, the synthesis agent can attribute correctly.

**Why A is wrong:** The "cite sources" instruction is probabilistic and doesn't fix the root cause. If the data reaching the synthesis agent has no structured source information, a prompt instruction can't create the missing data.

**Why C is wrong:** APA is a presentation format, not a data structure. The problem isn't how pretty the format is but that metadata isn't separated from content. An APA string is still plain text — it doesn't provide a structured claim-source mapping.

**Why D is wrong:** The isolation principle trap. Passing the full conversation history violates the isolation principle and doesn't fix the problem.

---

## Question 5 (Task Statement 1.4)

> An e-commerce agent sometimes processes refunds without verifying the customer's order history. In 5% of these cases the refund goes to the wrong order and the company loses money.
>
> The current system prompt contains this instruction: "Always verify the customer's order history before processing a refund."
>
> **What is the correct solution?**
>
> **A)** Repeat this instruction 3 times in the system prompt and emphasise it in bold.
>
> **B)** Add a `PreToolUse` hook that requires the `verify_order_history` tool to have completed successfully before the `process_refund` tool can run; on rejection, pass "call verify_order_history first" to Claude via `permissionDecisionReason`.
>
> **C)** Show the correct sequence with few-shot examples — add 5 different scenarios.
>
> **D)** Cap the refund amount at $100.

### Correct Answer: B

**Why B is correct:** An operation with financial consequences — refunds to the wrong order. The `PreToolUse` hook physically prevents the `process_refund` tool from running until `verify_order_history` has completed successfully; rule violations drop to zero. Because the rejection reason is passed to Claude, the agent calls verification and then completes the refund in the right order.

**Why A is wrong:** Repeating the prompt is probabilistic. Bold text and repetition might raise the success rate but can't guarantee 100%. The instruction is already in the prompt and it's failing 5% of the time.

**Why C is wrong:** Few-shot examples are also prompt-based guidance. They steer the model's behaviour but don't enforce it. Not deterministic.

**Why D is wrong:** Capping the amount doesn't solve the problem — refunds under $100 can still go to the wrong order. And the real problem is the missing verification, not the amount.

---

## Question 6 (Task Statement 1.5)

> An agent receives date information from three different **third-party** MCP servers (you have no access to their source code):
> - CRM tool → Unix timestamp (1719849600)
> - Shipping tool → "June 15, 2024"
> - Payment tool → "2024-06-15T00:00:00Z"
>
> Claude sometimes makes mistakes in date comparisons because the formats are inconsistent.
>
> **What is the correct solution?**
>
> **A)** Add the instruction "convert all dates to ISO 8601 format" to Claude's system prompt.
>
> **B)** Ask the three MCP server vendors to change their APIs to return ISO 8601.
>
> **C)** Use a `PostToolUse` hook to convert the dates in every tool result to a standard format via `updatedToolOutput`, before sending them to Claude.
>
> **D)** Add a reference table explaining the date formats to Claude's prompt.

### Correct Answer: C

**Why C is correct:** This is exactly what a `PostToolUse` hook is for — converting heterogeneous data from different tools into a standard format in code, before it reaches Claude. `updatedToolOutput` replaces the tool result itself; the hook runs deterministically, and Claude always sees a clean, consistent date format.

**Why A is wrong:** A prompt instruction is probabilistic. Claude might convert a Unix timestamp incorrectly or behave inconsistently across formats. Format conversion is a job for code, not the model.

**Why B is wrong:** Waiting for third-party vendors to change their APIs leaves control with an external dependency — even if it happens, it takes time and isn't guaranteed. Normalisation should happen at your boundary. (Note: if the tools were your own MCP servers, fixing them at the source would be a legitimate option — that's why the question says "third-party.")

**Why D is wrong:** A reference table is also prompt-based guidance. Claude applying the table correctly isn't guaranteed. An information-adding approach where a structural solution is needed.

---

## Question 7 (Task Statement 1.3)

> A coordinator needs to launch 3 subagents at once: web search, document analysis, and data visualisation. The three subagents are independent — none needs another's output. The current implementation launches each in sequence — first web search completes, then document analysis, then data visualisation.
>
> Total time: 45 seconds. Each subagent takes about 15 seconds.
>
> **What is the correct way to reduce latency?**
>
> **A)** Use a faster model for each subagent.
>
> **B)** Launch the subagents in parallel by making multiple Task tool calls in a single coordinator response.
>
> **C)** Let the subagents communicate with each other directly — skip the coordinator.
>
> **D)** Reduce the number of subagents to 2 — remove data visualisation.

### Correct Answer: B

**Why B is correct:** Parallel spawning. Because the subtasks are independent, if the coordinator makes multiple Task tool calls in a single response, the subagents start in parallel. 3 subagents × 15 seconds sequentially = 45 seconds. With parallel launching ≈ 15 seconds. A 3× speedup without sacrificing any feature.

**Why A is wrong:** A faster model may shorten each subagent, but the sequential structure remains. 3 × 10 seconds = 30 seconds is still slower than 15 seconds in parallel. And a model change may cost quality.

**Why C is wrong:** Violates the fundamental rule of hub-and-spoke architecture — all communication flows through the coordinator. Direct communication loses observability, error handling, and control.

**Why D is wrong:** Loss of functionality. Removing a feature instead of solving the problem is not the right approach.

---

## Question 8 (Task Statement 1.6)

> A code review agent analyses a 20-file PR in a single pass. Results:
>
> - It gives detailed, high-quality feedback on the first 5 files
> - It completely misses obvious null pointer bugs in files 15-20
> - It praises the `async/await` pattern as "best practice" in file 4 but flags the same pattern as an "anti-pattern" in file 18
>
> **What is the problem and the solution?**
>
> **A)** The context window is insufficient — a bigger model should be used.
>
> **B)** The files should be ordered by importance.
>
> **C)** The instruction "pay equal attention to all files and be consistent" should be added to the system prompt.
>
> **D)** Switch to a multi-pass architecture: per-file local analysis + a cross-file integration pass.

### Correct Answer: D

**Why D is correct:** The classic symptoms of attention dilution — inconsistent depth (detailed on the first files, superficial on the last) and contradictory judgements (different reactions to the same pattern). Multi-pass architecture: first analyse each file separately with the same criteria (per-file local analysis — can run in parallel), then check cross-file inconsistencies and dependencies over the findings (cross-file integration pass). Fixes both problems.

**Why A is wrong:** The problem isn't context window size, it's attention distribution — 20 files already fit. A bigger model has the same structural problem applying the same criteria at the same depth to 20 files in a single pass.

**Why B is wrong:** Changing the order changes which files get neglected but doesn't fix attention dilution. Still a single pass, still diluted attention.

**Why C is wrong:** A prompt instruction is probabilistic, and a prompt solution to a structural problem. Saying "pay equal attention" doesn't eliminate attention dilution — this is an architectural problem.

---

## Question 9 (Task Statement 1.6)

> An agent is given the task "add tests to a legacy codebase." The codebase is large and complex — dependencies are unknown in advance, and testability varies from file to file.
>
> **Which decomposition strategy is more appropriate?**
>
> **A)** Fixed sequential pipeline — first list all files, then write tests for each, then run them.
>
> **B)** Dynamic adaptive decomposition — first map the structure, identify high-impact areas, update the plan as dependencies emerge; put an explicit stopping criterion and budget on the exploration phase.
>
> **C)** Analyse all files in a single pass and write tests for the 5 most important.
>
> **D)** Pick 10 files at random and write tests for them.

### Correct Answer: B

**Why B is correct:** Legacy codebase = unknown dependencies, variable testability, a problem requiring exploration. This is an open-ended research task. Dynamic adaptive decomposition updates the plan based on what's discovered at each step — first you map the structure, identify high-impact areas, prioritise as dependencies emerge. The stopping criterion and budget prevent exploration from continuing forever.

**Why A is wrong:** Fixed sequential pipelines are for predictable tasks. In a legacy codebase the dependencies aren't known in advance — predetermined sequential steps can't adapt to unexpected findings.

**Why C is wrong:** All files in a single pass = attention dilution risk. And focusing on only 5 files arbitrarily narrows the scope.

**Why D is wrong:** Random selection has no strategic value. The risk of missing high-impact areas is very high.

---

## Question 10 (Task Statement 1.7)

> A developer resumes an agent session that had been working on a codebase for 3 days. In the meantime the developer has made extensive changes to 5 files — some functions deleted, new modules added, the API structure changed.
>
> After resuming, the agent gives advice referencing the deleted functions and behaves as if unaware of the new modules.
>
> **What is the correct approach?**
>
> **A)** Add the instruction "re-check the files at the start of every session" to the agent's system prompt.
>
> **B)** Use a model with a bigger context window.
>
> **C)** Because the changes are extensive and structural, do a fresh start with summary injection — inject a structured summary of the prior findings (findings, decisions, remaining work, changed files) into the new session.
>
> **D)** Create two branches with fork_session and pick the best result.

### Correct Answer: C

**Why C is correct:** Extensive changes to 5 files — functions deleted, new modules added, the API changed. This exceeds the "a few files changed" level; the structure has changed. The tool results are entirely stale. Even resume + specific notification may not be enough, because the structural assumptions in the agent's context are invalid. Fresh start with summary injection: a new clean session + a structured summary of the prior findings. Free of stale data, a fresh start without losing prior knowledge.

**Why A is wrong:** A prompt instruction is probabilistic and tries to solve the problem in the wrong place. The real issue is that the data in the context is stale — a "check the files" instruction doesn't reliably fix that.

**Why B is wrong:** The problem isn't context window size, it's stale data. A bigger model gives the same wrong advice from the same old tool results.

**Why D is wrong:** fork_session is for comparing different approaches. The problem here is stale context — even if you branch, both branches start from the same stale data, and the problem isn't solved.

---

## Question 11 (Task Statement 1.1) — NEW

> The loop of a report-generating agent checks only the `end_turn` and `tool_use` values; in every other case it treats the response as final and presents it to the user. Users report two complaints:
>
> 1. Long reports are sometimes cut off mid-sentence and presented that way
> 2. On some requests that use the (server-side) web search tool, after a few searches the agent gives a half-finished answer along the lines of "I couldn't complete the research"
>
> **What is the root cause and the fix?**
>
> **A)** The `max_tokens` value is too low — raising it from 4096 to 8192 fixes both problems.
>
> **B)** The loop doesn't handle the `max_tokens` and `pause_turn` stop_reason values. `max_tokens` → the response is truncated, don't treat it as finished, continue it; `pause_turn` → the server-side tool loop was paused, append the response to history as-is and send again.
>
> **C)** Add the instruction "keep the report short and limit searches to 3" to the system prompt.
>
> **D)** Add a check to the loop: "if the response doesn't end with a full stop, continue."

### Correct Answer: B

**Why B is correct:** The two symptoms correspond to two different `stop_reason` values. Problem 1: the output hit the `max_tokens` limit — because the loop doesn't recognise it, it treats the truncated response as "finished." Problem 2: when a server-side tool (web search) reaches its iteration limit, the API returns `pause_turn`; because the loop doesn't recognise that either, it presents the half-done research. A correct loop handles all `stop_reason` values: `max_tokens` → continue, `pause_turn` → resend with the same history.

**Why A is wrong:** Raising `max_tokens` postpones the first problem for a while, but the loop still doesn't recognise the `max_tokens` case — a longer report gets cut off again. It has nothing to do with the second problem (`pause_turn`).

**Why C is wrong:** Prompt-based, and tries to hide the symptom. Shortening the report doesn't deliver the output the user wanted; limiting searches is no substitute for handling `pause_turn` correctly.

**Why D is wrong:** A variant of the natural language parsing anti-pattern — inferring completion from punctuation is unreliable. `stop_reason` exists precisely for this.

---

## Question 12 (Task Statement 1.1) — NEW

> An agent gives Claude a `get_inventory` tool to compare stock data for three regions. Claude returns three `tool_use` blocks in a single response (one per region). The developer's code:
>
> ```python
> for block in response.content:
>     if block.type == "tool_use":
>         result = get_inventory(**block.input)
>         messages.append({"role": "user", "content": [
>             {"type": "tool_result", "tool_use_id": block.id, "content": result}
>         ]})
> ```
>
> The second API call returns a 400 error.
>
> **What is the problem?**
>
> **A)** Claude can only call one tool at a time; `disable_parallel_tool_use: true` should be set via `tool_choice`.
>
> **B)** Each `tool_result` is appended as a separate user message. The results for all `tool_use` blocks in an assistant response must be collected in the `content` list of the immediately following **single** user message.
>
> **C)** The `tool_result` blocks should be sent with the `assistant` role.
>
> **D)** The tool results were sent without appending the assistant response to history; first `response.content` should be appended as an assistant message, then each result as a separate user message.

### Correct Answer: B

**Why B is correct:** The rule: every `tool_use` block in an assistant turn must have a matching `tool_result` in the immediately following user message. The code produces three separate user messages; because the first user message contains only one result, the other two `tool_use` blocks are left unanswered and the API rejects the request. The fix: collect the three `tool_result` blocks in one list and append them as a single user message.

**Why A is wrong:** Parallel tool use isn't a bug, it's a feature that reduces latency. Disabling it removes the symptom, but the right thing is to write the loop so it handles parallel calls.

**Why C is wrong:** `tool_result` blocks are always sent with the `user` role. The role is right; the message structure is wrong.

**Why D is wrong:** It's true that the assistant response must be appended to history (it may just not be shown in the snippet), but the "each result as a separate user message" part is precisely the bug. Half right, half wrong.

---

## Question 13 (Task Statement 1.5) — NEW

> A finance agent can transfer money with a `wire_transfer` tool. The team wants transfers over $10,000 not to go through without manager approval. A developer proposes: "Let's write a `PostToolUse` hook for `wire_transfer`; if the amount exceeds $10,000 and there's no approval, the hook blocks the operation."
>
> **What is the correct assessment of this proposal?**
>
> **A)** The proposal is correct — `PostToolUse` can see the tool result, so it can check the amount and block.
>
> **B)** The proposal is wrong — by the time `PostToolUse` runs, the transfer has already happened; it can't block. The check belongs in a `PreToolUse` hook: if the amount exceeds the threshold and there's no approval, return `permissionDecision: "deny"` (or `"ask"` for human approval).
>
> **C)** The proposal is wrong — instead of a hook, the system prompt instruction "request approval for transfers over $10,000" is sufficient.
>
> **D)** The proposal is correct but incomplete — a `Stop` hook should be added alongside the `PostToolUse` hook.

### Correct Answer: B

**Why B is correct:** `PostToolUse` fires **after** the tool runs — the money is already gone. This hook can transform or log the result but can't undo the operation. Blocking a tool call is `PreToolUse`'s job: the amount is visible in `input`; if the threshold is exceeded and there's no approval, return `deny` (with a rejection reason) or `ask` for a human-approval flow.

**Why A is wrong:** `PostToolUse` seeing the result doesn't give it the power to block; in terms of timing, it's too late. A classic exam trap.

**Why C is wrong:** A financial operation where a single failure is costly — a prompt is probabilistic, a deterministic guarantee is required.

**Why D is wrong:** The `Stop` hook fires when the main agent finishes its turn; it has nothing to do with the transfer. Adding another wrong hook to a wrong hook is not a solution.

---

## Question 14 (Task Statement 1.2) — NEW

> A coordinator launches four research subagents for a report on "AI regulation": "EU regulation," "US regulation," "global regulatory trends," and "AI Act analysis." Logs: the "global trends" subagent re-fetched most of the EU and US sources; the "AI Act analysis" and "EU regulation" subagents processed nearly the same documents. Token cost is 2× what was expected, and the synthesis report describes the AI Act in three different places in three different ways.
>
> **What is the root cause and the most effective fix?**
>
> **A)** Add a "merge duplicate sections" instruction to the synthesis subagent.
>
> **B)** The coordinator's scope partitioning is wrong — the subtasks overlap ("global trends" covers EU/US; "AI Act" is a subset of "EU"). Re-decompose with disjoint scopes and write into each subagent's prompt what it should not cover.
>
> **C)** Let the subagents talk to each other so they can share which sources have been fetched.
>
> **D)** Reduce the subagents to 2: "EU" and "US."

### Correct Answer: B

**Why B is correct:** This is a scope-overlap problem — the opposite of narrow decomposition. An umbrella subtask ("global trends") and a subset subtask ("AI Act" ⊂ "EU") collide with the others. The coordinator must define disjoint subtasks (e.g. "EU — including the AI Act," "US," "countries outside the EU and US," and if needed a disjoint axis such as "cross-sector comparison") and state the boundaries in the prompts. Duplication is prevented at the source; cost and inconsistency are solved together.

**Why A is wrong:** Masks the symptom at the end; the cost of the duplicate research has already been paid. Trace the failure to its origin.

**Why C is wrong:** A hub-and-spoke violation — loss of observability and control; it doesn't fix the root cause (overlapping decomposition).

**Why D is wrong:** Arbitrarily narrows the scope — global trends and countries outside the EU/US go unreported. The problem isn't the number of subagents, it's the overlapping scopes.

---

## Question 15 (Task Statement 1.7 / 1.3) — NEW

> A developer ran a codebase analysis session with the Agent SDK and saved the session ID. Now they want to start two independent refactoring attempts from the same analysis and write the following code:
>
> ```python
> options = ClaudeAgentOptions(fork_session=True)
> ```
>
> On every run the agent does the analysis from scratch; it remembers nothing from the prior session.
>
> **What is the problem?**
>
> **A)** `fork_session` on its own doesn't specify a session — it must be used with `resume="<session_id>"`, which says which session to branch from. Without `resume`, every run is a new, empty session.
>
> **B)** `continue_conversation=True` should be used instead of `fork_session`; it finds the last session automatically and branches it.
>
> **C)** Agent SDK sessions aren't written to disk; the analysis summary has to be injected into the prompt manually.
>
> **D)** `fork_session="<session_id>"` should be written instead of `fork_session=True`.

### Correct Answer: A

**Why A is correct:** `fork_session` is a flag: it says "don't overwrite the session you're resuming, branch off with a new ID." Which session gets copied is determined by `resume`. When `resume` isn't given, there's nothing to branch from — the SDK opens a new, empty session and the agent naturally starts from scratch. Correct usage: `ClaudeAgentOptions(resume="<session_id>", fork_session=True)` — once for each attempt.

**Why B is wrong:** `continue_conversation` **continues** the most recent session, it doesn't branch — the two attempts would contaminate the same session in sequence. And there's no guarantee that the "most recent" session is the analysis session.

**Why C is wrong:** Sessions are written to disk; `resume` exists precisely for that. Manual summary injection (fresh start) is a valid technique but unnecessary here — the analysis isn't stale, it was just invoked with the wrong option.

**Why D is wrong:** `fork_session` is a boolean; the session identifier goes in the `resume` parameter.

---

## Question 16 (Task Statement 1.3) — NEW

> A coordinator agent launches research subagents; those subagents launch further subagents for their own subtopics, which launch more for sub-subtopics. Logs show dozens of subagents three levels deep. A single run costs 8× what was expected, it's impossible to trace which finding came from which subagent, and some sub-subtopics overlap.
>
> **What is the most appropriate fix?**
>
> **A)** Assign a cheaper `model` to every subagent — cost goes down.
>
> **B)** Limit nested subagent depth (`CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`, e.g. 1) and centralise decomposition in the coordinator: the coordinator itself defines the subtopics as disjoint, subagents research only the scope they're given and don't spawn new subagents.
>
> **C)** Let the subagents communicate with each other directly so they can resolve the overlap themselves.
>
> **D)** Remove all subagents; let the coordinator research on its own.

### Correct Answer: B

**Why B is correct:** Uncontrolled nested spawning produces three problems at once: compounding cost, loss of observability (hub-and-spoke's "everything goes through the coordinator" principle erodes with depth), and fragmented decomposition (when every level does its own decomposition, scopes overlap). A depth limit and centralised decomposition fix all three: the coordinator is the single decomposition point, subagents are leaf nodes.

**Why A is wrong:** A cheaper model reduces cost but doesn't change the number of subagents, the loss of observability, or the scope overlap. Only one of the symptoms, and only partly.

**Why C is wrong:** A hub-and-spoke violation; it makes the observability problem even worse.

**Why D is wrong:** Throws away the benefits of parallelism and specialisation entirely; attention dilution risk in a single agent. The problem isn't using subagents, it's not controlling depth and decomposition.
