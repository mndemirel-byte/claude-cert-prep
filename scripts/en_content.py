SCEN_EN = {
1: {"ctx":"You are building a customer support resolution agent with the Claude Agent SDK. The agent handles high-ambiguity requests such as returns, billing disputes and account issues. It reaches your backend systems through custom MCP tools: <code>get_customer</code>, <code>lookup_order</code>, <code>process_refund</code>, <code>escalate_to_human</code>. Target: 80%+ first-contact resolution while knowing when to escalate.",
 "sig":[("1.1 Agentic loop","The loop is driven by <code>stop_reason</code>; searching for \"final answer\" text, iteration caps or text-block checks are traps."),
        ("1.4 / 1.5 Enforcement and hooks","Refund without identity verification → a programmatic prerequisite gate, not a prompt instruction. Refunds above $500 → block with a tool-call interception hook and redirect to a human. Date/status formats differing across MCP tools → normalise in a PostToolUse hook."),
        ("2.1 / 2.2 Tool design","Minimal descriptions such as \"Retrieves account info\" cause misrouting → the first step is enriching descriptions. Errors are structured with <code>isError</code> + <code>errorCategory</code> + <code>isRetryable</code>; business-rule errors are not retried."),
        ("5.1 Context preservation","Order number, amount and date vanish during summarisation → a persistent <em>case facts</em> block; trim 45-field tool results to the 5 relevant fields."),
        ("5.2 Escalation","Valid triggers: the customer asks for a human, a policy gap, inability to progress. Sentiment analysis and self-reported confidence are unreliable. Multiple customer matches → ask for another identifier, never pick heuristically."),
        ("5.3 Empty result vs access failure","<code>status: success, results: []</code> is a valid answer; no retry needed.")],
 "traps":["\"Repeat the instruction three times in the system prompt\" / \"use a bigger model\" — never the answer when money is at stake","Auto-escalating an angry customer — sentiment ≠ complexity","Basing the handoff summary on the transcript — the human agent cannot see it; the summary must be self-contained"]},
2: {"ctx":"You are using Claude Code to accelerate software development. Your team uses it for code generation, refactoring, debugging and documentation. You need to integrate it into your workflow with custom slash commands and CLAUDE.md configurations, and know when to use plan mode versus direct execution.",
 "sig":[("3.1 CLAUDE.md hierarchy","A new teammate doesn't get the rules → they live in <code>~/.claude/CLAUDE.md</code> (user level, not shared); move them to project level. A growing file → <code>@import</code> or <code>.claude/rules/</code>; verify what is loaded with <code>/memory</code>."),
        ("3.2 Commands and skills","A command shared with the team → <code>.claude/commands/</code> (in the repo). A skill with noisy output → <code>context: fork</code>; preventing destructive actions → <code>allowed-tools</code>; prompting for parameters → <code>argument-hint</code>. Skill = on-demand workflow, CLAUDE.md = always-loaded standard."),
        ("3.3 Path-specific rules","Scattered test files → <code>.claude/rules/</code> + <code>paths: [\"**/*.test.tsx\"]</code>; a directory CLAUDE.md is bound to one directory."),
        ("3.4 Plan mode","Architectural decisions, multi-file changes, several valid approaches → plan mode. A single-file fix with a clear stack trace → direct execution. Noisy discovery → the Explore subagent."),
        ("3.5 Iterative refinement","Prose interpreted inconsistently → 2–3 concrete before/after examples. Test-driven iteration, the interview pattern. Interacting issues in one message, independent ones sequentially."),
        ("1.7 / 5.4 Session management","Two approaches from the same baseline → <code>fork_session</code>; files unchanged → resume; stale context → a fresh session with an injected summary; long exploration → scratchpad files and <code>/compact</code>.")],
 "traps":["Piling everything into the root CLAUDE.md — token waste and inconsistency","Assuming personal (<code>~/.claude</code>) configuration is shared with the team","\"Start direct, switch to plan mode if it gets complex\" when the complexity is stated up front"]},
3: {"ctx":"You are building a multi-agent research system with the Claude Agent SDK. A coordinator agent delegates to specialised subagents: one searches the web, one analyses documents, one synthesises findings and one generates reports. The system researches topics and produces comprehensive, cited reports.",
 "sig":[("1.2 Coordination","The report misses whole subtopics while each subagent works fine in isolation → the coordinator's decomposition is too narrow. Hub-and-spoke: all communication goes through the coordinator. An iterative refinement loop for gaps in the synthesis output."),
        ("1.3 Context passing","Subagents do not inherit the coordinator's history; findings are placed explicitly in the prompt. Content and metadata (URL, document, page) are kept structurally separate to preserve attribution. Parallel subagents = several Task calls in a single response; <code>allowedTools</code> must include \"Task\"."),
        ("2.3 Tool distribution","4–5 tools per agent; 18 tools degrade selection. The synthesis agent gets a scoped <code>verify_fact</code> tool, not full web search; complex verification routes through the coordinator."),
        ("5.3 Error propagation","A timeout → structured error context (type, attempted query, partial results, alternatives). Silent suppression and halting the whole workflow are both anti-patterns. Transient failures are recovered locally in the subagent."),
        ("5.1 / 5.6 Context and provenance","Verbose subagent output exhausts the synthesis budget → change the upstream agent to return structured data. Conflicting statistics → present both with source and date; a temporal difference is not a contradiction. Claim-source mappings survive synthesis; coverage gaps are stated explicitly in the report.")],
 "traps":["Blaming a downstream agent (\"synthesis filtered it out\") — trace the failure to its source","Handing subagents the full conversation history — breaks the isolation principle","\"Pick the most recent value\" or \"average them\" for conflicting data"]},
4: {"ctx":"You are building developer productivity tools with the Claude Agent SDK. The agent helps engineers explore unfamiliar codebases, understand legacy systems, generate boilerplate and automate repetitive tasks. It uses the built-in tools (Read, Write, Bash, Grep, Glob) and integrates with MCP servers.",
 "sig":[("2.5 Built-in tools","Grep = file <em>contents</em> (function calls, error messages, imports); Glob = file <em>paths</em> (<code>**/*.test.tsx</code>). Edit needs a unique match; if it fails, Read + Write. Codebase understanding is built incrementally: Grep for entry points, Read to follow imports — not reading everything upfront."),
        ("2.4 MCP integration","Shared server → <code>.mcp.json</code> + <code>${TOKEN}</code>; personal/experimental → <code>~/.claude.json</code>. Content catalogues are exposed as MCP <em>resources</em> to cut exploratory calls. The agent prefers built-in Grep over an MCP tool → enrich the MCP description. Community servers for standard integrations (Jira), custom servers for team-specific workflows."),
        ("1.6 / 1.7 Decomposition and sessions","Open-ended tasks (\"add tests to a legacy codebase\") → map the structure first, find high-impact areas, adapt the plan as dependencies surface. Resuming with changed files → tell the agent what changed; extensive changes → a fresh session with an injected summary."),
        ("3.4 / 5.4 Exploration and context","Noisy discovery → the Explore subagent. Drifting to \"typical patterns\" in a long session = context degradation → scratchpad files, subagent delegation, manifests for crash recovery.")],
 "traps":["Searching for function calls with Glob","Applying fixed prompt chaining to an open-ended investigation","Trying to fix context degradation with \"a bigger context window\""]},
5: {"ctx":"You are integrating Claude Code into your CI/CD pipeline. The system runs automated code reviews, generates test cases and provides feedback on pull requests. You need to design prompts that give actionable feedback and minimise false positives.",
 "sig":[("3.6 CI integration","The pipeline hangs → <code>-p</code> / <code>--print</code>. Machine-readable findings → <code>--output-format json</code> + <code>--json-schema</code>. On re-runs, provide prior findings and report only new or still-open issues. Put existing test files in context; document testing standards and fixtures in CLAUDE.md."),
        ("4.1 Explicit criteria","Not \"are the comments accurate?\" but \"flag a comment only when it contradicts the code's behaviour\". \"Be conservative\" does not work. Temporarily disable a category whose false positives poison trust. Severity levels are defined with code examples."),
        ("4.2 Few-shot","For ambiguous cases (stale comment or wrong comment?) 2–4 examples with reasoning; the output format (location, issue, severity, fix) is demonstrated by example."),
        ("4.6 / 1.6 Multi-pass review","A single pass over 14+ files is inconsistent → per-file passes plus a cross-file integration pass. The session that generated the code reviews it poorly → an independent review instance."),
        ("4.5 Batch API","Blocking pre-merge checks → synchronous; overnight/weekly reports → batch (50% saving, 24 hours, no SLA).")],
 "traps":["\"Raise the confidence threshold\" for false positives — the problem is vague criteria","Keeping a single pass over a large PR with a bigger context window","Moving a blocking workflow to batch"]},
6: {"ctx":"You are building a structured data extraction system with Claude. It extracts information from unstructured documents, validates the output with JSON schemas and maintains high accuracy. It must handle edge cases gracefully and integrate with downstream systems.",
 "sig":[("4.3 Structured output via tool_use","Guaranteed schema compliance → tool_use + JSON schema; syntax errors disappear, semantic errors (totals don't add up) do not. Unknown document type with several schemas → <code>tool_choice: \"any\"</code>; a specific tool first → forced by name. A field that may be absent → nullable (prevents fabrication); extensible categories → enum + <code>\"other\"</code> + detail."),
        ("4.4 Validation-retry","The retry includes the document, the failed output and the specific error. Format errors are fixed by retry; missing information is not. Self-validation via <code>calculated_total</code> vs <code>stated_total</code> and <code>conflict_detected</code>."),
        ("4.2 Few-shot","Empty extractions across tables, plain text and nested lists → examples showing the layout variety."),
        ("4.5 Batch","Large volume, latency-tolerant → batch; isolate failures by <code>custom_id</code>, chunk oversized documents; refine the prompt on a sample before a large submission."),
        ("5.5 Human review","96% overall accuracy can hide weakness on one document type → stratified analysis. Confidence thresholds are calibrated with a labelled validation set; high-confidence output is continuously audited with stratified random sampling. Low confidence and conflicting sources → human review.")],
 "traps":["Required field + missing information → hallucination; the fix is a nullable field, not retry","\"The JSON is valid, so the extraction is correct\" — semantic validation is separate","Intuitive confidence thresholds; automating without labelled data"]},
}

SCEN_PAGE_EN = {
"h_sel":"How are scenarios selected?",
"sel":"""<p>The official guide defines it like this: the exam uses scenario-based questions; each scenario presents a realistic production context that frames a set of questions, and during the exam <strong>4 of the 6 scenarios are presented, picked at random</strong>. In practice:</p>
<ul>
<li>Questions are not standalone knowledge items; they sit under a scenario text that starts with "you are building…", and that scenario's tool names, target metrics and constraints are embedded in the question stems.</li>
<li>60 questions are spread across 4 scenarios (roughly 15 per scenario). You cannot know in advance which 4 will appear, so you must be ready for all six.</li>
<li>Domain weights (27 / 18 / 20 / 20 / 15%) are fixed and preserved on every form. What changes is <em>in which context</em> a given domain is asked.</li>
<li>Scores are reported on a 100–1000 scale, weighted by domain; the pass mark is 720. Scaled scoring exists to equate forms of slightly different difficulty — the scenario mix varies from form to form, the threshold does not.</li>
</ul>""",
"h_map":"Scenario × domain map",
"map_intro":"<p>Each scenario's <strong>primary domains</strong> from the guide (●) and the number of questions tied to it in this guide's mock pool:</p>",
"map_notes":"""<p>Practical conclusions from the map:</p><ul>
<li><strong>Domain 5</strong> is primary in four scenarios; whichever four are drawn, it is asked in a wide variety of contexts.</li>
<li><strong>Domain 4</strong> is primary only in scenarios 5 and 6. If scenario 6 is not drawn, most of Domain 4's 12 questions come from the CI/CD context (review criteria, false positives, multi-pass review, batch); if scenario 5 is not drawn, they come from extraction (nullable fields, validation-retry, few-shot for document variety).</li>
<li><strong>Domain 1</strong>'s 16 questions come from scenarios 1, 3 and 4; <strong>Domain 3</strong>'s 12 from scenarios 2, 4 and 5; <strong>Domain 2</strong>'s 11 from scenarios 1, 3 and 4.</li>
<li>Scenario 4 (Developer Productivity) bridges three domains — built-in tools, MCP and session management are asked together.</li>
</ul>""",
"h_impact":"How does this affect the questions?",
"impact":"""<p><strong>1. Each scenario has signature decision patterns.</strong> The same task statement wears a different face in different scenarios. Task 1.4 (enforcement) shows up as "refund without identity verification" in the support scenario and as "the agent tries to merge to main" in the CI scenario; the principle (deterministic enforcement) is the same, the surface differs.</p>
<p><strong>2. The question pattern is fed by the scenario.</strong> The typical structure in the guide's sample questions: <em>"Production logs/data show … — what is the most effective first step / root cause?"</em> All four options come from inside the scenario and all look workable. The correct one targets the root cause and is <em>proportionate</em>: fixing a description comes before adding a classifier, a nullable field before a retry loop, a prerequisite gate before a prompt instruction.</p>
<p><strong>3. Distractors are scenario-specific too.</strong> In high-stakes scenarios (finance, compliance, production databases) "add an instruction to the prompt", "bigger model", "bigger context window", "add a classifier", "route everything to a human" are almost always traps. The guide says it plainly: prompt-based compliance is probabilistic and insufficient when errors have financial consequences.</p>
<p><strong>4. Questions in a scenario build on each other.</strong> Consecutive questions under one scenario share the same tool set and target metric. Reading the scenario text carefully once (which tools exist, what the target is, which constraints apply) saves time on each of the next 15 questions — the information not repeated in a stem is in the scenario text.</p>
<p><strong>5. Preparation strategy:</strong> complement domain-based study with scenario-based revision. For each scenario, gather the tool set, target metric, typical failure modes and the matching architectural decision on one page; the cards below were made for that. On exam day, once you recognise the scenario you can largely predict which task statements are coming.</p>""",
"h_six":"The six scenarios",
"prim":"Primary domains",
"ctx_lbl":"Context (from the guide):",
"h_sig":"Decisions typically tested in this scenario",
"h_traps":"Common traps",
"pool":"The mock pool has {n} questions tied to this scenario.",
}

# English versions of quiz questions. Keys: ("base", domain, n) or ("extra", domain, idx) or ("extra2", idx)
Q_EN = {
("base",1,1):{"body":"""A customer support agent runs with the following loop logic:

```python
for i in range(10):
    response = call_claude(messages)
    if "final answer" in response.content[0].text.lower():
        return response
    # execute tools and continue
```

Users report three different problems:
1. The agent sometimes stops after 10 iterations without giving an answer
2. The agent sometimes stops even though it said "Here's my final answer so far, let me search for more details"
3. On some requests the loop crashes with `AttributeError: 'ToolUseBlock' object has no attribute 'text'`

**Which approach fixes all three problems?**""",
 "opts":{"A":"Raise the iteration cap from 10 to 25, check for \"task complete\" instead of \"final answer\", and wrap the `.text` access in `try/except`.", "B":"Check the `response.stop_reason` field — exit on `\"end_turn\"`, and on `\"tool_use\"` execute every tool_use block in the entire `response.content` list and continue.", "C":"Ask Claude \"Are you done?\" on every iteration and parse the answer.", "D":"Remove the iteration cap and check only `response.content[0].type == \"text\"`."},
 "expl":"""**Why B is correct:** The code contains three separate bugs: an arbitrary iteration cap (the 10-loop limit, stopping silently), natural language parsing (searching for the phrase "final answer"), and the `content[0]` assumption (if the first block is a `tool_use` block there is no `.text` → crash). Checking `stop_reason` fixes the first two; iterating over the whole `content` list fixes the third. No guessing, parsing, or first-block assumption is needed.

**Why A is wrong:** Raising the cap, searching for a different string, and swallowing the error with `try/except` keeps all three anti-patterns alive. The number, the string, and the error handling change, but the structural problems remain — in particular, `try/except` hides the crash but doesn't stop the loop from making the wrong decision.

**Why C is wrong:** A different version of the natural language parsing anti-pattern. Claude saying "yes, I'm done" is just as ambiguous and unreliable; it also adds an extra API call to every iteration.

**Why D is wrong:** The content-type check anti-pattern. Claude can return text and tool_use blocks in the same response. Exiting on seeing text causes premature termination — and the `content[0]` assumption is still there."""},
("base",1,2):{"body":"""A multi-agent research system produces a report on "global food security challenges." The system consists of a coordinator, a web search subagent, a document analysis subagent, and a synthesis subagent.

The final report is well-written but covers only climate change and water scarcity. Supply chain disruptions, political instability, and biotechnology are completely missing.

When tested independently, the web search subagent returns excellent results for the query "food security supply chain disruption."

**What is the root cause?**""",
 "opts":{"A":"The web search subagent's search algorithm is inadequate.", "B":"The synthesis subagent filtered out some topics.", "C":"The coordinator's task decomposition is incomplete — it only created subtasks for climate and water.", "D":"The subagents can't access the coordinator's full conversation history."},
 "expl":"""**Why C is correct:** A narrow decomposition failure. The subagents work perfectly when tested independently — the problem isn't with them. The coordinator decomposed "global food security challenges" into only climate and water. Supply chain, political instability, and biotechnology were never created as subtasks. Trace the failure to its origin — the coordinator's decomposition.

**Why A is wrong:** The web search subagent returns excellent results in independent testing. Its search capability is fine — it was simply never asked about those topics.

**Why B is wrong:** The synthesis subagent only synthesises the data it receives. If no research on supply chains was done, there's nothing to filter out.

**Why D is wrong:** The isolation principle trap. Giving subagents the full conversation history is not the right architectural approach. The fix is to broaden the coordinator's decomposition."""},
("base",1,3):{"body":"""In an agentic loop, Claude returns the following response:

- `response.content[0]` → type: "text", text: "I found some relevant data. Let me query the sales database for Q3 numbers."
- `response.content[1]` → type: "tool_use", name: "query_database", input: {...}
- `response.stop_reason` → "tool_use"

**What should the loop do?**""",
 "opts":{"A":"Show the text block to the user and terminate the loop — Claude gave a text response.", "B":"Execute the `query_database` tool, append the result to the conversation history as a `tool_result` block, and send it back to Claude. The text block may optionally be shown to the user as an interim progress message (streaming).", "C":"Present the text block to the user as the final answer, reset the conversation history, and start a new conversation with the tool result.", "D":"Ask Claude \"Do you approve this tool call?\""},
 "expl":"""**Why B is correct:** `stop_reason` is `"tool_use"` — that's the only signal that matters. Claude returned both a text block and a tool_use block, but `stop_reason` says clearly "I need to continue." Execute the tool, append the result to the existing history as a `tool_result` block matched by `tool_use_id`, send it back to Claude. The text block is Claude "thinking out loud" — showing it to the user as a progress message is harmless, but the loop decision is made from `stop_reason`.

**Why A is wrong:** The content-type check anti-pattern. Terminating the loop because a text block exists is a premature exit. `stop_reason` is still `"tool_use"`.

**Why C is wrong:** Two mistakes at once: treating the text block as the *final* answer (premature termination) and resetting the history. The tool result must be sent as a continuation of the existing history that contains Claude's own tool_use block; if the history is reset, there's no `tool_use` block for the `tool_result` to match and the API rejects the request.

**Why D is wrong:** In an agentic loop Claude makes its own decisions. Asking Claude to approve every tool call is meaningless — if human approval is required, that's done with an `ask` decision in a `PreToolUse` hook, not with an extra Claude call in the loop."""},
("base",1,4):{"body":"""A coordinator passes the web search subagent's findings to the synthesis subagent. The handoff is in the following format:

```
"Solar energy capacity grew 45% in 2024. Wind energy investments
reached $120B. Geothermal projects expanded in Iceland and Kenya."
```

The synthesis subagent writes a good report but cites no sources for any claim.

**What is the most effective fix?**""",
 "opts":{"A":"Add a \"cite a source for every claim\" instruction to the synthesis subagent's system prompt.", "B":"Switch the coordinator's context passing mechanism to a structured metadata format — map every claim to its source URL, document name, and page number.", "C":"Tell the web search subagent to return its results in APA format.", "D":"Give the synthesis subagent the coordinator's full conversation history."},
 "expl":"""**Why B is correct:** The problem is in context passing. The coordinator passes plain text — the synthesis agent doesn't know which claim came from which source. The fix: a structured metadata format — a JSON structure mapping every claim to a source URL, document name, and page number; that schema goes into the web search subagent's prompt so the structure is created at the start of the chain. With this structured data, the synthesis agent can attribute correctly.

**Why A is wrong:** The "cite sources" instruction is probabilistic and doesn't fix the root cause. If the data reaching the synthesis agent has no structured source information, a prompt instruction can't create the missing data.

**Why C is wrong:** APA is a presentation format, not a data structure. The problem isn't how pretty the format is but that metadata isn't separated from content. An APA string is still plain text — it doesn't provide a structured claim-source mapping.

**Why D is wrong:** The isolation principle trap. Passing the full conversation history violates the isolation principle and doesn't fix the problem."""},
("base",1,5):{"body":"""An e-commerce agent sometimes processes refunds without verifying the customer's order history. In 5% of these cases the refund goes to the wrong order and the company loses money.

The current system prompt contains this instruction: "Always verify the customer's order history before processing a refund."

**What is the correct solution?**""",
 "opts":{"A":"Repeat this instruction 3 times in the system prompt and emphasise it in bold.", "B":"Add a `PreToolUse` hook that requires the `verify_order_history` tool to have completed successfully before the `process_refund` tool can run; on rejection, pass \"call verify_order_history first\" to Claude via `permissionDecisionReason`.", "C":"Show the correct sequence with few-shot examples — add 5 different scenarios.", "D":"Cap the refund amount at $100."},
 "expl":"""**Why B is correct:** An operation with financial consequences — refunds to the wrong order. The `PreToolUse` hook physically prevents the `process_refund` tool from running until `verify_order_history` has completed successfully; rule violations drop to zero. Because the rejection reason is passed to Claude, the agent calls verification and then completes the refund in the right order.

**Why A is wrong:** Repeating the prompt is probabilistic. Bold text and repetition might raise the success rate but can't guarantee 100%. The instruction is already in the prompt and it's failing 5% of the time.

**Why C is wrong:** Few-shot examples are also prompt-based guidance. They steer the model's behaviour but don't enforce it. Not deterministic.

**Why D is wrong:** Capping the amount doesn't solve the problem — refunds under $100 can still go to the wrong order. And the real problem is the missing verification, not the amount."""},
("base",1,6):{"body":"""An agent receives date information from three different **third-party** MCP servers (you have no access to their source code):
- CRM tool → Unix timestamp (1719849600)
- Shipping tool → "June 15, 2024"
- Payment tool → "2024-06-15T00:00:00Z"

Claude sometimes makes mistakes in date comparisons because the formats are inconsistent.

**What is the correct solution?**""",
 "opts":{"A":"Add the instruction \"convert all dates to ISO 8601 format\" to Claude's system prompt.", "B":"Ask the three MCP server vendors to change their APIs to return ISO 8601.", "C":"Use a `PostToolUse` hook to convert the dates in every tool result to a standard format via `updatedToolOutput`, before sending them to Claude.", "D":"Add a reference table explaining the date formats to Claude's prompt."},
 "expl":"""**Why C is correct:** This is exactly what a `PostToolUse` hook is for — converting heterogeneous data from different tools into a standard format in code, before it reaches Claude. `updatedToolOutput` replaces the tool result itself; the hook runs deterministically, and Claude always sees a clean, consistent date format.

**Why A is wrong:** A prompt instruction is probabilistic. Claude might convert a Unix timestamp incorrectly or behave inconsistently across formats. Format conversion is a job for code, not the model.

**Why B is wrong:** Waiting for third-party vendors to change their APIs leaves control with an external dependency — even if it happens, it takes time and isn't guaranteed. Normalisation should happen at your boundary. (Note: if the tools were your own MCP servers, fixing them at the source would be a legitimate option — that's why the question says "third-party.")

**Why D is wrong:** A reference table is also prompt-based guidance. Claude applying the table correctly isn't guaranteed. An information-adding approach where a structural solution is needed."""},
("base",1,7):{"body":"""A coordinator needs to launch 3 subagents at once: web search, document analysis, and data visualisation. The three subagents are independent — none needs another's output. The current implementation launches each in sequence — first web search completes, then document analysis, then data visualisation.

Total time: 45 seconds. Each subagent takes about 15 seconds.

**What is the correct way to reduce latency?**""",
 "opts":{"A":"Use a faster model for each subagent.", "B":"Launch the subagents in parallel by making multiple Task tool calls in a single coordinator response.", "C":"Let the subagents communicate with each other directly — skip the coordinator.", "D":"Reduce the number of subagents to 2 — remove data visualisation."},
 "expl":"""**Why B is correct:** Parallel spawning. Because the subtasks are independent, if the coordinator makes multiple Task tool calls in a single response, the subagents start in parallel. 3 subagents × 15 seconds sequentially = 45 seconds. With parallel launching ≈ 15 seconds. A 3× speedup without sacrificing any feature.

**Why A is wrong:** A faster model may shorten each subagent, but the sequential structure remains. 3 × 10 seconds = 30 seconds is still slower than 15 seconds in parallel. And a model change may cost quality.

**Why C is wrong:** Violates the fundamental rule of hub-and-spoke architecture — all communication flows through the coordinator. Direct communication loses observability, error handling, and control.

**Why D is wrong:** Loss of functionality. Removing a feature instead of solving the problem is not the right approach."""},
("base",1,8):{"body":"""A code review agent analyses a 20-file PR in a single pass. Results:

- It gives detailed, high-quality feedback on the first 5 files
- It completely misses obvious null pointer bugs in files 15-20
- It praises the `async/await` pattern as "best practice" in file 4 but flags the same pattern as an "anti-pattern" in file 18

**What is the problem and the solution?**""",
 "opts":{"A":"The context window is insufficient — a bigger model should be used.", "B":"The files should be ordered by importance.", "C":"The instruction \"pay equal attention to all files and be consistent\" should be added to the system prompt.", "D":"Switch to a multi-pass architecture: per-file local analysis + a cross-file integration pass."},
 "expl":"""**Why D is correct:** The classic symptoms of attention dilution — inconsistent depth (detailed on the first files, superficial on the last) and contradictory judgements (different reactions to the same pattern). Multi-pass architecture: first analyse each file separately with the same criteria (per-file local analysis — can run in parallel), then check cross-file inconsistencies and dependencies over the findings (cross-file integration pass). Fixes both problems.

**Why A is wrong:** The problem isn't context window size, it's attention distribution — 20 files already fit. A bigger model has the same structural problem applying the same criteria at the same depth to 20 files in a single pass.

**Why B is wrong:** Changing the order changes which files get neglected but doesn't fix attention dilution. Still a single pass, still diluted attention.

**Why C is wrong:** A prompt instruction is probabilistic, and a prompt solution to a structural problem. Saying "pay equal attention" doesn't eliminate attention dilution — this is an architectural problem."""},
("base",1,9):{"body":"""An agent is given the task "add tests to a legacy codebase." The codebase is large and complex — dependencies are unknown in advance, and testability varies from file to file.

**Which decomposition strategy is more appropriate?**""",
 "opts":{"A":"Fixed sequential pipeline — first list all files, then write tests for each, then run them.", "B":"Dynamic adaptive decomposition — first map the structure, identify high-impact areas, update the plan as dependencies emerge; put an explicit stopping criterion and budget on the exploration phase.", "C":"Analyse all files in a single pass and write tests for the 5 most important.", "D":"Pick 10 files at random and write tests for them."},
 "expl":"""**Why B is correct:** Legacy codebase = unknown dependencies, variable testability, a problem requiring exploration. This is an open-ended research task. Dynamic adaptive decomposition updates the plan based on what's discovered at each step — first you map the structure, identify high-impact areas, prioritise as dependencies emerge. The stopping criterion and budget prevent exploration from continuing forever.

**Why A is wrong:** Fixed sequential pipelines are for predictable tasks. In a legacy codebase the dependencies aren't known in advance — predetermined sequential steps can't adapt to unexpected findings.

**Why C is wrong:** All files in a single pass = attention dilution risk. And focusing on only 5 files arbitrarily narrows the scope.

**Why D is wrong:** Random selection has no strategic value. The risk of missing high-impact areas is very high."""},
("base",1,10):{"body":"""A developer resumes an agent session that had been working on a codebase for 3 days. In the meantime the developer has made extensive changes to 5 files — some functions deleted, new modules added, the API structure changed.

After resuming, the agent gives advice referencing the deleted functions and behaves as if unaware of the new modules.

**What is the correct approach?**""",
 "opts":{"A":"Add the instruction \"re-check the files at the start of every session\" to the agent's system prompt.", "B":"Use a model with a bigger context window.", "C":"Because the changes are extensive and structural, do a fresh start with summary injection — inject a structured summary of the prior findings (findings, decisions, remaining work, changed files) into the new session.", "D":"Create two branches with fork_session and pick the best result."},
 "expl":"""**Why C is correct:** Extensive changes to 5 files — functions deleted, new modules added, the API changed. This exceeds the "a few files changed" level; the structure has changed. The tool results are entirely stale. Even resume + specific notification may not be enough, because the structural assumptions in the agent's context are invalid. Fresh start with summary injection: a new clean session + a structured summary of the prior findings. Free of stale data, a fresh start without losing prior knowledge.

**Why A is wrong:** A prompt instruction is probabilistic and tries to solve the problem in the wrong place. The real issue is that the data in the context is stale — a "check the files" instruction doesn't reliably fix that.

**Why B is wrong:** The problem isn't context window size, it's stale data. A bigger model gives the same wrong advice from the same old tool results.

**Why D is wrong:** fork_session is for comparing different approaches. The problem here is stale context — even if you branch, both branches start from the same stale data, and the problem isn't solved."""},
("base",1,11):{"body":"""The loop of a report-generating agent checks only the `end_turn` and `tool_use` values; in every other case it treats the response as final and presents it to the user. Users report two complaints:

1. Long reports are sometimes cut off mid-sentence and presented that way
2. On some requests that use the (server-side) web search tool, after a few searches the agent gives a half-finished answer along the lines of "I couldn't complete the research"

**What is the root cause and the fix?**""",
 "opts":{"A":"The `max_tokens` value is too low — raising it from 4096 to 8192 fixes both problems.", "B":"The loop doesn't handle the `max_tokens` and `pause_turn` stop_reason values. `max_tokens` → the response is truncated, don't treat it as finished, continue it; `pause_turn` → the server-side tool loop was paused, append the response to history as-is and send again.", "C":"Add the instruction \"keep the report short and limit searches to 3\" to the system prompt.", "D":"Add a check to the loop: \"if the response doesn't end with a full stop, continue.\""},
 "expl":"""**Why B is correct:** The two symptoms correspond to two different `stop_reason` values. Problem 1: the output hit the `max_tokens` limit — because the loop doesn't recognise it, it treats the truncated response as "finished." Problem 2: when a server-side tool (web search) reaches its iteration limit, the API returns `pause_turn`; because the loop doesn't recognise that either, it presents the half-done research. A correct loop handles all `stop_reason` values: `max_tokens` → continue, `pause_turn` → resend with the same history.

**Why A is wrong:** Raising `max_tokens` postpones the first problem for a while, but the loop still doesn't recognise the `max_tokens` case — a longer report gets cut off again. It has nothing to do with the second problem (`pause_turn`).

**Why C is wrong:** Prompt-based, and tries to hide the symptom. Shortening the report doesn't deliver the output the user wanted; limiting searches is no substitute for handling `pause_turn` correctly.

**Why D is wrong:** A variant of the natural language parsing anti-pattern — inferring completion from punctuation is unreliable. `stop_reason` exists precisely for this."""},
("base",1,12):{"body":"""An agent gives Claude a `get_inventory` tool to compare stock data for three regions. Claude returns three `tool_use` blocks in a single response (one per region). The developer's code:

```python
for block in response.content:
    if block.type == "tool_use":
        result = get_inventory(**block.input)
        messages.append({"role": "user", "content": [
            {"type": "tool_result", "tool_use_id": block.id, "content": result}
        ]})
```

The second API call returns a 400 error.

**What is the problem?**""",
 "opts":{"A":"Claude can only call one tool at a time; `disable_parallel_tool_use: true` should be set via `tool_choice`.", "B":"Each `tool_result` is appended as a separate user message. The results for all `tool_use` blocks in an assistant response must be collected in the `content` list of the immediately following **single** user message.", "C":"The `tool_result` blocks should be sent with the `assistant` role.", "D":"The tool results were sent without appending the assistant response to history; first `response.content` should be appended as an assistant message, then each result as a separate user message."},
 "expl":"""**Why B is correct:** The rule: every `tool_use` block in an assistant turn must have a matching `tool_result` in the immediately following user message. The code produces three separate user messages; because the first user message contains only one result, the other two `tool_use` blocks are left unanswered and the API rejects the request. The fix: collect the three `tool_result` blocks in one list and append them as a single user message.

**Why A is wrong:** Parallel tool use isn't a bug, it's a feature that reduces latency. Disabling it removes the symptom, but the right thing is to write the loop so it handles parallel calls.

**Why C is wrong:** `tool_result` blocks are always sent with the `user` role. The role is right; the message structure is wrong.

**Why D is wrong:** It's true that the assistant response must be appended to history (it may just not be shown in the snippet), but the "each result as a separate user message" part is precisely the bug. Half right, half wrong."""},
("base",1,13):{"body":"""A finance agent can transfer money with a `wire_transfer` tool. The team wants transfers over $10,000 not to go through without manager approval. A developer proposes: "Let's write a `PostToolUse` hook for `wire_transfer`; if the amount exceeds $10,000 and there's no approval, the hook blocks the operation."

**What is the correct assessment of this proposal?**""",
 "opts":{"A":"The proposal is correct — `PostToolUse` can see the tool result, so it can check the amount and block.", "B":"The proposal is wrong — by the time `PostToolUse` runs, the transfer has already happened; it can't block. The check belongs in a `PreToolUse` hook: if the amount exceeds the threshold and there's no approval, return `permissionDecision: \"deny\"` (or `\"ask\"` for human approval).", "C":"The proposal is wrong — instead of a hook, the system prompt instruction \"request approval for transfers over $10,000\" is sufficient.", "D":"The proposal is correct but incomplete — a `Stop` hook should be added alongside the `PostToolUse` hook."},
 "expl":"""**Why B is correct:** `PostToolUse` fires **after** the tool runs — the money is already gone. This hook can transform or log the result but can't undo the operation. Blocking a tool call is `PreToolUse`'s job: the amount is visible in `input`; if the threshold is exceeded and there's no approval, return `deny` (with a rejection reason) or `ask` for a human-approval flow.

**Why A is wrong:** `PostToolUse` seeing the result doesn't give it the power to block; in terms of timing, it's too late. A classic exam trap.

**Why C is wrong:** A financial operation where a single failure is costly — a prompt is probabilistic, a deterministic guarantee is required.

**Why D is wrong:** The `Stop` hook fires when the main agent finishes its turn; it has nothing to do with the transfer. Adding another wrong hook to a wrong hook is not a solution."""},
("base",1,14):{"body":"""A coordinator launches four research subagents for a report on "AI regulation": "EU regulation," "US regulation," "global regulatory trends," and "AI Act analysis." Logs: the "global trends" subagent re-fetched most of the EU and US sources; the "AI Act analysis" and "EU regulation" subagents processed nearly the same documents. Token cost is 2× what was expected, and the synthesis report describes the AI Act in three different places in three different ways.

**What is the root cause and the most effective fix?**""",
 "opts":{"A":"Add a \"merge duplicate sections\" instruction to the synthesis subagent.", "B":"The coordinator's scope partitioning is wrong — the subtasks overlap (\"global trends\" covers EU/US; \"AI Act\" is a subset of \"EU\"). Re-decompose with disjoint scopes and write into each subagent's prompt what it should not cover.", "C":"Let the subagents talk to each other so they can share which sources have been fetched.", "D":"Reduce the subagents to 2: \"EU\" and \"US.\""},
 "expl":"""**Why B is correct:** This is a scope-overlap problem — the opposite of narrow decomposition. An umbrella subtask ("global trends") and a subset subtask ("AI Act" ⊂ "EU") collide with the others. The coordinator must define disjoint subtasks (e.g. "EU — including the AI Act," "US," "countries outside the EU and US," and if needed a disjoint axis such as "cross-sector comparison") and state the boundaries in the prompts. Duplication is prevented at the source; cost and inconsistency are solved together.

**Why A is wrong:** Masks the symptom at the end; the cost of the duplicate research has already been paid. Trace the failure to its origin.

**Why C is wrong:** A hub-and-spoke violation — loss of observability and control; it doesn't fix the root cause (overlapping decomposition).

**Why D is wrong:** Arbitrarily narrows the scope — global trends and countries outside the EU/US go unreported. The problem isn't the number of subagents, it's the overlapping scopes."""},
("base",1,15):{"body":"""A developer ran a codebase analysis session with the Agent SDK and saved the session ID. Now they want to start two independent refactoring attempts from the same analysis and write the following code:

```python
options = ClaudeAgentOptions(fork_session=True)
```

On every run the agent does the analysis from scratch; it remembers nothing from the prior session.

**What is the problem?**""",
 "opts":{"A":"`fork_session` on its own doesn't specify a session — it must be used with `resume=\"<session_id>\"`, which says which session to branch from. Without `resume`, every run is a new, empty session.", "B":"`continue_conversation=True` should be used instead of `fork_session`; it finds the last session automatically and branches it.", "C":"Agent SDK sessions aren't written to disk; the analysis summary has to be injected into the prompt manually.", "D":"`fork_session=\"<session_id>\"` should be written instead of `fork_session=True`."},
 "expl":"""**Why A is correct:** `fork_session` is a flag: it says "don't overwrite the session you're resuming, branch off with a new ID." Which session gets copied is determined by `resume`. When `resume` isn't given, there's nothing to branch from — the SDK opens a new, empty session and the agent naturally starts from scratch. Correct usage: `ClaudeAgentOptions(resume="<session_id>", fork_session=True)` — once for each attempt.

**Why B is wrong:** `continue_conversation` **continues** the most recent session, it doesn't branch — the two attempts would contaminate the same session in sequence. And there's no guarantee that the "most recent" session is the analysis session.

**Why C is wrong:** Sessions are written to disk; `resume` exists precisely for that. Manual summary injection (fresh start) is a valid technique but unnecessary here — the analysis isn't stale, it was just invoked with the wrong option.

**Why D is wrong:** `fork_session` is a boolean; the session identifier goes in the `resume` parameter."""},
("base",1,16):{"body":"""A coordinator agent launches research subagents; those subagents launch further subagents for their own subtopics, which launch more for sub-subtopics. Logs show dozens of subagents three levels deep. A single run costs 8× what was expected, it's impossible to trace which finding came from which subagent, and some sub-subtopics overlap.

**What is the most appropriate fix?**""",
 "opts":{"A":"Assign a cheaper `model` to every subagent — cost goes down.", "B":"Limit nested subagent depth (`CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`, e.g. 1) and centralise decomposition in the coordinator: the coordinator itself defines the subtopics as disjoint, subagents research only the scope they're given and don't spawn new subagents.", "C":"Let the subagents communicate with each other directly so they can resolve the overlap themselves.", "D":"Remove all subagents; let the coordinator research on its own."},
 "expl":"""**Why B is correct:** Uncontrolled nested spawning produces three problems at once: compounding cost, loss of observability (hub-and-spoke's "everything goes through the coordinator" principle erodes with depth), and fragmented decomposition (when every level does its own decomposition, scopes overlap). A depth limit and centralised decomposition fix all three: the coordinator is the single decomposition point, subagents are leaf nodes.

**Why A is wrong:** A cheaper model reduces cost but doesn't change the number of subagents, the loss of observability, or the scope overlap. Only one of the symptoms, and only partly.

**Why C is wrong:** A hub-and-spoke violation; it makes the observability problem even worse.

**Why D is wrong:** Throws away the benefits of parallelism and specialisation entirely; attention dilution risk in a single agent. The problem isn't using subagents, it's not controlling depth and decomposition."""},
("extra",1,0):{"body":"""A fintech company is building an agent that processes refunds. The system prompt says: *"Always call the `verify_identity` tool before issuing a refund."* A production audit shows that 14 of 1,200 refunds were processed without identity verification. The compliance team wants that number to be zero.

**What is the most appropriate fix?**""",
 "opts":{"A":"Strengthen the system prompt instruction by writing it in capitals and repeating it three times.",
         "B":"Add a prerequisite gate in the code of the `issue_refund` tool that rejects the request unless a successful `verify_identity` call exists in the same session.",
         "C":"Use a stronger model — bigger models follow instructions better.",
         "D":"Run an audit agent after every refund and report the ones that skipped verification."},
 "expl":"""**Why B is correct:** Rules with financial and compliance risk are enforced programmatically, not with prompts. Prompt-based guidance is probabilistic — even 98.8% compliance is insufficient for compliance purposes. A prerequisite gate makes an unverified refund physically impossible: a 100% guarantee.

**Why A is wrong:** Repeating the instruction is still a probabilistic approach. The rate may drop, but zero cannot be guaranteed.

**Why C is wrong:** Model strength can raise compliance but never gives a deterministic guarantee. Exam trap: in a high-stakes scenario "a bigger model" is never the answer.

**Why D is wrong:** After-the-fact auditing detects the error, it does not prevent it. The money is already gone — compliance asked for prevention, not detection."""},
("extra",1,1):{"body":"""A DevOps agent built with the Claude Agent SDK can run commands through a `run_shell` tool. The team wants commands containing `DROP` or `TRUNCATE` against the production database to **never** run under any circumstances. They also want the raw JSON returned by the `list_pods` tool simplified (unnecessary metadata dropped) before it reaches Claude.

**Which hook combination is correct for these two requirements?**""",
 "opts":{"A":"A system prompt instruction for both — hooks add unnecessary complexity.",
         "B":"A PreToolUse hook for the `DROP/TRUNCATE` block (intercept and reject the tool call); a PostToolUse hook for JSON simplification (transform the tool result before it reaches Claude).",
         "C":"A PostToolUse hook for both — check the result after the command runs and return an error if it was dangerous.",
         "D":"A PostToolUse hook for the `DROP/TRUNCATE` block; a PreToolUse hook for JSON simplification."},
 "expl":"""**Why B is correct:** The two hook points serve two different jobs. Intercepting a tool call **before it runs** (PreToolUse) enforces business rules deterministically — the dangerous command never executes. Intercepting a tool result **before it reaches Claude** (PostToolUse) is for data normalisation and simplification.

**Why A is wrong:** "Never under any circumstances" requires a deterministic guarantee. Prompts are probabilistic; a single failure can wipe the production database. Decision rule: if one error causes money or data loss → hook.

**Why C is wrong:** PostToolUse fires **after** the command has run — the `DROP` has already been applied. Too late to block.

**Why D is wrong:** The hook points are reversed. PreToolUse cannot see the result (it does not exist yet); PostToolUse cannot block the call (it already ran)."""},
("extra",1,2):{"body":"""A developer closed an agent session last night that was refactoring a large monorepo. This morning they want to continue. No files changed overnight, but the developer wants to compare two refactoring strategies (adapter pattern vs. direct rewrite) and choose the better one.

**What is the most appropriate approach?**""",
 "opts":{"A":"Resume the session and ask Claude to try both strategies one after the other in the same session.",
         "B":"Forget yesterday's session entirely, start a fresh session per strategy and re-explore the codebase each time.",
         "C":"Create two independent branches from yesterday's session with `fork_session` — try one strategy per branch and compare the results.",
         "D":"Do a fresh start with summary injection — inject a summary of yesterday's findings into a new session and proceed with a single strategy."},
 "expl":"""**Why C is correct:** The context is valid (no files changed) and the goal is **comparing different approaches from the same baseline**. That is exactly what `fork_session` is for: the shared discovery context is preserved, each branch proceeds independently and neither contaminates the other.

**Why A is wrong:** Trying both strategies sequentially in one session contaminates the context — the second attempt is influenced by the first one's decisions and half-finished changes. No clean comparison.

**Why B is wrong:** Re-exploring the codebase twice is wasted cost. Yesterday's context is still valid — there is no reason to discard it.

**Why D is wrong:** A fresh start is for stale context (changed files). Nothing is stale here; and "proceed with a single strategy" does not meet the comparison requirement."""},
("extra",1,3):{"body":"""In a legal research system the coordinator passes three research subagents' findings to a writing subagent. For the handoff it pastes all three subagents' full conversation histories (~140K tokens) into the writing subagent's prompt. The writing subagent frequently omits important findings and sometimes mistakes the research subagents' interim notes for final findings.

**What are the root cause and the fix?**""",
 "opts":{"A":"The writing subagent's model is inadequate — use a model with a larger context window.",
         "B":"Context passing is wrong — instead of raw history, ask each subagent for a structured, self-contained findings summary (finding, source, confidence) and pass only those.",
         "C":"Run the research subagents in the same session as the writing subagent so they share memory.",
         "D":"Add the instruction \"ignore interim notes, use only final findings\" to the writing subagent."},
 "expl":"""**Why B is correct:** Passing raw conversation history to subagents is an anti-pattern. Within 140K tokens the writing subagent cannot tell a finding from an interim thought, and its attention dilutes. The correct handoff protocol: each subagent produces a structured, self-contained summary (finding, source, confidence) and the coordinator passes only those. Each subagent gets exactly what it needs — no more.

**Why A is wrong:** The problem is not context size but the structure of what is passed. A bigger window does not stop interim notes being read as findings.

**Why C is wrong:** Breaks the isolation principle. Shared memory increases context pollution rather than reducing it.

**Why D is wrong:** Treats the symptom with a prompt instruction. The difference between an interim note and a finding is not explicit in raw text — an instruction cannot resolve it reliably."""},
("extra",1,4):{"body":"""An e-commerce company is building a multi-agent system that produces launch content: (1) market research, (2) competitor pricing analysis, (3) target audience analysis, (4) marketing copy based on the output of the first three. The four steps currently run sequentially and take 11 minutes in total. The product team wants it faster.

**Which arrangement is correct?**""",
 "opts":{"A":"Run all four steps in parallel — every subagent is independent.",
         "B":"Run the first three (research, pricing, audience) in parallel; once all complete, start the fourth (copywriting) sequentially.",
         "C":"Merge the four steps into a single agent — subagent coordination adds latency.",
         "D":"Keep the sequence but give each subagent a smaller, faster model."},
 "expl":"""**Why B is correct:** The parallel/sequential decision follows **data dependencies**. The first three steps are independent — their only input is the product info. The fourth depends on all three outputs. The right pattern: independent steps in parallel (fan-out), the dependent one afterwards (fan-in). Total time drops to roughly the longest research step plus the writing step.

**Why A is wrong:** Copywriting takes the other three outputs as input. Started in parallel it writes with no data — a dependency violation.

**Why C is wrong:** Merging causes focus loss and context bloat, and removes the parallelism opportunity entirely — probably slower.

**Why D is wrong:** A smaller model risks quality and does not fix the structural latency (needless sequencing). Fix the architecture first, then look at model choice."""},
("extra",1,5):{"body":"""A coordinator decomposes the review of a 40-page contract into **one subagent per paragraph** (~600 subagents). Result: cost 8× higher than expected, total time longer, and cross-paragraph contradictions (e.g. a definition in section 3 inconsistent with its use in section 27) never caught in the final report.

**What is the source of the problem?**""",
 "opts":{"A":"Too many subagents; coordination overhead and over-fine decomposition fragment the context — decompose into meaningful units (section/clause) and add a separate integration pass for cross-references.",
         "B":"The subagents are not using a strong enough model.",
         "C":"The coordinator lacks an aggregation step — add a summary subagent to merge outputs; the decomposition level is fine.",
         "D":"Contract review is not suited to decomposition — give the whole document to a single agent."},
 "expl":"""**Why A is correct:** Decomposition granularity is a balance. Too coarse → a single agent drowns; too fine → coordination cost explodes and **relationships between units are lost**. A paragraph is not a meaningful unit for a contract; a clause or section is. Cross-consistency (section 3 ↔ section 27) is something no single subagent can see — it needs a separate integration pass.

**Why B is wrong:** The problem is structural, not model strength. Each subagent probably reviews its paragraph well; nobody looks between paragraphs.

**Why C is wrong:** An aggregation step is needed, but "the decomposition level is fine" is false — 600 subagents are the direct cause of the cost and time problem. Adding a summary alone does not fix cost.

**Why D is wrong:** An overreaction. 40 pages in one context causes attention dilution; the problem is not decomposition itself but its granularity."""},
}

Q_EN.update({
("base",2,1):{"body":"""A customer support agent has 3 tools:

- `get_account_info`: "Retrieves account information"
- `get_billing_info`: "Retrieves billing information"
- `get_subscription_info`: "Retrieves subscription information"

Users complain: when they say "I want to upgrade my subscription" the agent calls `get_account_info`; billing queries go to `get_subscription_info`. Overall misrouting rate is 30%.

**What should be done as the first step?**""",
 "opts":{"A":"Merge the three tools into a single `get_customer_data` tool — Claude can't make mistakes with one tool.",
         "B":"Add few-shot examples to the system prompt such as \"use get_billing_info for billing questions, get_subscription_info for subscription questions\".",
         "C":"Expand each tool's description — state clearly which data fields it returns, which query types it is for, and how it differs from the other tools.",
         "D":"Add an intent classifier before Claude — it analyses the query and routes it to the right tool."},
 "expl":"""**Why C is correct:** The root cause is vague descriptions — all three tools follow the "retrieves X information" pattern and Claude cannot differentiate. Expanding the descriptions (which fields are returned, which queries they serve, how they differ) is a low-effort, high-leverage fix that targets the root cause directly.

**Why A is wrong:** Merging breaks separation of concerns. Combining three data sources in one tool loses tool focus and needlessly inflates the data returned. It also takes far more effort.

**Why B is wrong:** Few-shot examples add token cost and treat the symptom, not the root cause. While descriptions are vague, examples are not a reliable fix. Prompt-based guidance is probabilistic.

**Why D is wrong:** An intent classifier is over-engineering for a first step. You haven't tried the simple fix (better descriptions) yet. A classifier adds complexity and maintenance cost."""},
("base",2,2):{"body":"""An agent has an `analyze_document` tool. In a single call it summarises the document, extracts key data and verifies claims. The agent sometimes runs unnecessary verification when only a summary was requested, and sometimes returns only a summary when verification was requested.

**What are the root cause and the fix?**""",
 "opts":{"A":"The tool's description is inadequate — write a more detailed description.",
         "B":"The tool is too broad — split it into three purpose-specific tools: `summarize_content`, `extract_data_points` and `verify_claim_against_source`.",
         "C":"Add \"only perform the requested operation\" to the system prompt.",
         "D":"Add an `operation_type` field to the tool's input parameters — Claude specifies which operation it wants."},
 "expl":"""**Why B is correct:** The tool does three different jobs — summarising, extraction, verification. Claude triggers all three with one call and cannot control which output it wants. Splitting into purpose-specific tools defines each precisely for one job. Claude can select exactly the operation it needs.

**Why A is wrong:** A better description clarifies what a single tool does, but does not fix the structural problem — the tool still does three jobs at once. A better description improves when Claude calls the tool, not what the tool does.

**Why C is wrong:** A prompt instruction is probabilistic. Saying "only do the requested operation" does not change the tool's three-in-one structure — this is an architectural problem, not a prompt problem.

**Why D is wrong:** An `operation_type` parameter is a workaround — it moves the complexity inside the tool. The tool still contains three separate logics; you've just added a switch. Clean architecture: each tool does one job."""},
("base",2,3):{"body":"""An agent is attempting an international money transfer. The tool returns:

```json
{
  "isError": true,
  "errorCategory": "business",
  "isRetryable": false,
  "description": "Transfer amount ($15,000) exceeds the daily limit ($10,000).",
  "customerMessage": "Your daily transfer limit is $10,000. Contact your account manager for higher limits."
}
```

**What should the agent do?**""",
 "opts":{"A":"Wait 5 seconds and retry — it may be a transient error.",
         "B":"Automatically reduce the transfer amount to $10,000 and retry.",
         "C":"Do not retry. Relay the information in `customerMessage` to the customer and offer an alternative path (referral to the account manager).",
         "D":"Fix the input and retry — it may be a validation error."},
 "expl":"""**Why C is correct:** `errorCategory: "business"` and `isRetryable: false` — this is a business-rule violation; retrying is WRONG. Until the policy changes the same operation will fail every time. The agent should relay the `customerMessage` to the customer and offer the alternative path (account manager).

**Why A is wrong:** This is not a transient error — it is a business-rule error. Waiting does not change the policy. The same error returns after 5 seconds or 5 minutes. `isRetryable: false` explicitly rules out retrying.

**Why B is wrong:** Changing the amount automatically overrides the customer's request. The customer wants to transfer $15,000 — the agent must not unilaterally reduce it to $10,000. That business decision belongs to the customer.

**Why D is wrong:** This is not a validation error — the format is correct and the amount is a valid number. The problem is a business rule: the daily limit is exceeded. `errorCategory: "business"` states it explicitly. Validation errors are about input format (wrong type, missing field)."""},
("base",2,4):{"body":"""In a multi-agent system the web search subagent gets a timeout on an API call. The subagent retries twice more but fails.

**What should the subagent do?**""",
 "opts":{"A":"Swallow the error silently and return an empty result — don't bother the coordinator with unnecessary information.",
         "B":"Propagate to the coordinator immediately at the first timeout — local retries are a waste of time.",
         "C":"Propagate the error to the coordinator — including partial results (what it obtained before the timeout) and the recovery steps attempted (2 retries).",
         "D":"Retry in an infinite loop — transient errors eventually resolve."},
 "expl":"""**Why C is correct:** The subagent attempted local recovery (2 retries) and failed. Now it has an error it cannot resolve locally. Correct behaviour: propagate to the coordinator, but in an informed way — include partial results and the recovery steps attempted. The coordinator can then decide: try a different subagent, use a different source, or route to a human.

**Why A is wrong:** Swallowing the error silently is the most dangerous approach. The coordinator stays unaware of the problem and may interpret the empty result as "no data" (the access-failure vs empty-result confusion). Information loss and wrong decisions.

**Why B is wrong:** Propagating at the first timeout skips the local recovery opportunity. Transient errors are usually fixed by retrying — the subagent should try first. Propagating every transient error to the coordinator creates needless load and latency.

**Why D is wrong:** An infinite retry loop locks the system. The assumption that transient errors "eventually resolve" is not always true — a service can be down for a long time. After a reasonable number of retries (2–3), if unresolved, propagate upward."""},
("base",2,5):{"body":"""A research agent has been given 16 tools: 5 web search tools, 4 document analysis tools, 3 database query tools, 2 email tools and 2 calendar tools. The agent frequently picks the wrong tool and struggles to complete tasks.

At the same time, although metadata extraction is a mandatory first step, the agent sometimes skips it and goes straight to analysis.

**Which approach solves both problems?**""",
 "opts":{"A":"Expand all tool descriptions and add \"always extract metadata first\" to the system prompt.",
         "B":"Distribute the tools across role-specific agents (4–5 tools per agent) and enforce the mandatory first step with `tool_choice: {\"type\": \"tool\", \"name\": \"extract_metadata\"}`.",
         "C":"Reduce the tool count to 8 — remove the least used tools.",
         "D":"Create a single \"do_everything\" tool and run all operations through it."},
 "expl":"""**Why B is correct:** It solves both problems:
1. **Tool overload:** 16 tools → distribute across role-specific agents (4–5 tools each). Selection reliability improves.
2. **Mandatory first step:** `tool_choice: {"type": "tool", "name": "extract_metadata"}` forces metadata extraction deterministically. The model cannot skip it — it is physically required to call this tool.

**Why A is wrong:** A two-part fix, but both parts are probabilistic. Expanding descriptions partially improves the 16-tool selection problem but does not fix the root cause (too many tools). The system prompt instruction "always extract metadata" is probabilistic — no 100% guarantee. Mandatory steps need a deterministic mechanism (tool_choice).

**Why C is wrong:** Reducing the tool count loses functionality. And choosing which tools to remove by "least used" is wrong — a rarely used tool may be critical. The real fix is not removing tools but distributing them to the right agents.

**Why D is wrong:** A single "do_everything" tool is the exact opposite of tool splitting. Piling all complexity into one tool makes it impossible for Claude to specify what it wants. A bigger version of the `analyze_document` problem in question 2."""},
("base",2,6):{"body":"""A team is starting a new project. An MCP server will be configured for the GitHub integration. A developer proposes this `.mcp.json`:

```json
{
  "mcpServers": {
    "github": {
      "command": "github-mcp-server",
      "env": {
        "GITHUB_TOKEN": "ghp_abc123def456ghi789"
      }
    }
  }
}
```

**What is the security problem in this configuration?**""",
 "opts":{"A":"The `github-mcp-server` command is wrong — the correct command should be `mcp-github`.",
         "B":"The GitHub token is written directly into `.mcp.json`. Because this file is under version control the token will enter the repo. The token should be referenced as the `${GITHUB_TOKEN}` environment variable.",
         "C":"`~/.claude.json` should be used instead of `.mcp.json` — MCP configuration should always be at user level.",
         "D":"The token is too short — a stronger token should be generated."},
 "expl":"""**Why B is correct:** `.mcp.json` is under version control — tracked by Git and pushed to the repo. If the token is written directly into the file, everyone can see it once it is pushed. A security breach. Fix: use the `${GITHUB_TOKEN}` environment variable syntax. Each developer sets their own token locally; tokens never enter the repo.

**Why A is wrong:** The command name is not the configuration's security problem. The question asks about the security issue — the correct command name is a separate matter.

**Why C is wrong:** `.mcp.json` (project level) and `~/.claude.json` (user level) exist for different purposes. Project-level tool configuration is information that should be shared with the team — `.mcp.json` is the right place. The problem is not the file's location but the hard-coded token.

**Why D is wrong:** The token's length or strength is not the security problem here. The issue is where the token is stored — in plain text in a version-controlled file. Even the strongest token is compromised once it enters the repo."""},
("base",2,7):{"body":"""A developer is working in a large codebase and needs to complete two tasks:

1. Find all files that call the `fetchUserData` function
2. Find all `.config.yml` files in the project

**Which tool is correct for each task?**""",
 "opts":{"A":"Use Grep for both — Grep does every kind of search.",
         "B":"Glob for task 1 (`**/*fetchUserData*`), Grep for task 2 (`fetchUserData` pattern).",
         "C":"Grep for task 1 (`fetchUserData` pattern — searches file contents), Glob for task 2 (`**/*.config.yml` — matches file paths).",
         "D":"Use Read for both — read all files and filter manually."},
 "expl":"""**Why C is correct:** Each tool is used where it is strong:
1. **Grep** for the function name `fetchUserData` in file **contents** → finds the files that call this function
2. **Glob** to match the `**/*.config.yml` pattern against file **paths** → finds the config files

Grep = content search. Glob = path matching. Each in the right place.

**Why A is wrong:** Grep searches file contents — finding `.config.yml` files requires matching file paths, which is Glob's job. You cannot search by file extension with Grep (searching for the string ".config.yml" inside file contents is a different thing).

**Why B is wrong:** The mapping is reversed. Glob searches file **paths** — if the function name `fetchUserData` does not appear in a file name (and it usually doesn't) Glob returns nothing. Function calls live in file **contents** — that is Grep's job.

**Why D is wrong:** Reading all files with Read is the worst approach — very slow, a context-budget killer. Grep and Glob do these jobs in one efficient step. Reading all files upfront is never the right approach."""},
("extra",2,0):{"body":"""An order management agent's `create_shipment` tool returns this on error:

```json
{ "error": "Request failed" }
```

The agent behaves the same way for insufficient stock (a permanent business-rule error) and for a temporary timeout of the shipping API (transient): in both cases it retries 5 times and gives up.

**How should the error response be redesigned?**""",
 "opts":{"A":"Turn the error message into a longer, more descriptive natural-language text — let the agent read it and decide.",
         "B":"Add structured fields: a machine-readable error code, an `isRetryable` flag and a `suggestion` field telling the agent the next step (e.g. \"insufficient stock — offer the customer an alternative product\").",
         "C":"Throw all errors as exceptions and terminate the agentic loop — let a human resolve errors.",
         "D":"Reduce the retry count from 5 to 2 — less time is wasted on permanent errors."},
 "expl":"""**Why B is correct:** A structured error response provides three things: (1) type discrimination via an error code, (2) a deterministic retry decision via `isRetryable` — retry if transient, don't if it's a business rule, (3) the next step via `suggestion`, so the agent knows rather than guesses. The agent chooses the right path from these fields.

**Why A is wrong:** Having the agent parse a natural-language error message is probabilistic — checking whether the word "timeout" appears is unreliable and breaks when the model changes.

**Why C is wrong:** Transient errors are situations the agent can resolve on its own; escalating to a human every time makes the automation pointless.

**Why D is wrong:** Changing the retry count does not fix the root cause (inability to distinguish error types). Transient errors may not resolve in 2 attempts, and permanent errors don't need even 2."""},
("extra",2,1):{"body":"""In a form-filling agent, the first step must always be extracting the fields from the document with the `extract_fields` tool. But when running with `tool_choice: "auto"` the agent sometimes produces a plain text answer without calling a tool ("This document looks like an invoice…") and the flow breaks.

**What is the correct fix?**""",
 "opts":{"A":"Add \"always call extract_fields first\" to the system prompt.",
         "B":"Use `tool_choice: {\"type\": \"tool\", \"name\": \"extract_fields\"}` on the first call, then return to `\"auto\"` on subsequent turns.",
         "C":"Use `tool_choice: \"any\"` — the agent is guaranteed to call a tool.",
         "D":"Remove all other tools — with only one tool left, Claude has to call it."},
 "expl":"""**Why B is correct:** When a specific tool must be the mandatory first step, you force that tool by name with `tool_choice` — deterministic. Returning to `"auto"` afterwards lets the model make its own decisions for the rest of the flow.

**Why A is wrong:** A prompt instruction is probabilistic; the "sometimes doesn't call a tool" problem is exactly what that inadequacy looks like.

**Why C is wrong:** `"any"` guarantees a tool call but not **which** one — the agent may pick `validate_form` or another tool. A specific tool requires forcing by name.

**Why D is wrong:** Removing tools also removes the capabilities needed later in the flow (validation, submission). Large side effects, no solution."""},
("extra",2,2):{"body":"""A team is adding the GitHub MCP server to the project. This line was written to the config file and committed to the repo:

```json
{ "mcpServers": { "github": { "command": "npx", "args": ["-y", "@modelcontextprotocol/server-github"],
  "env": { "GITHUB_TOKEN": "ghp_AbC123..." } } } }
```

The security team objects to the token being exposed in the repo. But the team wants the server configuration to be shared by all members and under version control.

**What is the correct arrangement?**""",
 "opts":{"A":"Move the configuration to each developer's own `~/.claude.json` — no MCP config in the repo at all.",
         "B":"Define the server in the project-level `.mcp.json`, reference the token value with the environment-variable syntax `\"GITHUB_TOKEN\": \"${GITHUB_TOKEN}\"`; each developer defines the token in their own environment.",
         "C":"Base64-encode the token and commit that.",
         "D":"Make the repo private — the token can be exposed in a private repo."},
 "expl":"""**Why B is correct:** `.mcp.json` is project level — version-controlled and shared with the team; the server definition lives there. Credentials are referenced with the `${GITHUB_TOKEN}` environment-variable syntax so the token stays out of the repo. Both requirements (shared config + secret credentials) are met.

**Why A is wrong:** `~/.claude.json` is user level — not shared. It violates the team's "shared and version-controlled" requirement; every developer would have to set up the same config by hand.

**Why C is wrong:** Base64 is encoding, not encryption — reversed with one command. No security.

**Why D is wrong:** Even in a private repo the token stays in git history, spreads to every cloned machine and is hard to rotate. Credentials are never committed."""},
("extra",2,3):{"body":"""A developer working in Claude Code wants to find **every call site** of the `PaymentGateway` class in the codebase, and then list all `.yaml` files under `config/`. The agent uses Glob for the first task and Grep for the second, and both results come back incomplete.

**What is the correct tool mapping?**""",
 "opts":{"A":"Grep for both tasks — Grep is more comprehensive.",
         "B":"Grep for the call sites (search file contents for the `PaymentGateway` pattern); Glob for the YAML list (match the `config/**/*.yaml` path pattern).",
         "C":"Glob for both tasks — Glob is faster.",
         "D":"Glob for the call sites (`**/*PaymentGateway*`); Grep for the YAML list (search for the `.yaml` text)."},
 "expl":"""**Why B is correct:** Grep searches for text patterns in file **contents** — function/class calls, imports, error messages. Glob matches name patterns against file **paths** — files by extension, config files. Call sites are a content question → Grep; the YAML list is a path question → Glob.

**Why A is wrong:** Listing files with Grep is indirect and noisy — the ".yaml" text can also appear inside contents, and file names may be missed.

**Why C is wrong:** Glob does not look inside files — if the `PaymentGateway` class name does not appear in a file name (it usually doesn't) no call sites are found. That is exactly why the results in the scenario are incomplete.

**Why D is wrong:** This is the faulty mapping from the scenario itself. The reversed usage leaves both results incomplete."""},
})

Q_EN.update({
("base",3,1):{"body":"""Four developers on a team work on the same repo. Developer A has defined rules that make Claude Code always use the `vitest` framework and follow the `describe/it` structure when writing tests. The other 3 developers get inconsistent test output from Claude Code — sometimes it uses `jest`, sometimes `mocha`.

Developer A's rules are defined in `~/.claude/CLAUDE.md`.

**What are the root cause and the fix?**""",
 "opts":{"A":"The other developers' Claude Code versions differ — everyone should update to the same version.",
         "B":"The rules are at user level (`~/.claude/CLAUDE.md`) — they apply only to Developer A. They should move to project level (`.claude/CLAUDE.md`) so the whole team gets them.",
         "C":"Each developer should copy the same rules into their own `~/.claude/CLAUDE.md`.",
         "D":"Developer A should synchronise memories with the `/memory` command."},
 "expl":"""**Why B is correct:** `~/.claude/CLAUDE.md` is user level — not in Git, not shared. Only Developer A gets these rules. Fix: move them to `.claude/CLAUDE.md` (project level). Under version control, everyone who clones the repo gets the rules.

**Why A is wrong:** a version difference doesn't explain the test-framework preference. The problem is the missing instructions, not the software version.

**Why C is wrong:** manual copying isn't sustainable — when the rules change everyone has to update. The project-level file reaches everyone automatically.

**Why D is wrong:** `/memory` is a diagnostic tool, not a synchronisation tool."""},
("base",3,2):{"body":"""A project's root `.claude/CLAUDE.md` contains general coding standards. The project has this structure:

```
/
├── .claude/CLAUDE.md  (general standards)
├── frontend/          (React)
├── backend/           (Python/FastAPI)
└── infrastructure/    (Terraform)
```

The team wants to apply different language- and framework-specific rules per subdirectory. At the same time it doesn't want `.claude/CLAUDE.md` to grow too large.

**What is the right approach?**""",
 "opts":{"A":"Write all rules into the single `.claude/CLAUDE.md` — size isn't a problem.",
         "B":"Create directory-level `CLAUDE.md` files in each subdirectory (`frontend/CLAUDE.md`, `backend/CLAUDE.md`, `infrastructure/CLAUDE.md`) and/or reference modular files from `.claude/CLAUDE.md` with the `@import` syntax.",
         "C":"Each developer writes the rules for their area in their own `~/.claude/CLAUDE.md`.",
         "D":"Move all rules into skill files — invoke the relevant skill each time."},
 "expl":"""**Why B is correct:** two mechanisms work together: directory-level CLAUDE.md files apply rules specific to that directory (React rules in frontend, Python rules in backend). The `@import` syntax provides modular organisation — reference external files instead of one big file. Both approaches are version-controlled and shared.

**Why A is wrong:** cramming everything into one file wastes tokens. There's no point loading React rules while working in the backend.

**Why C is wrong:** user level isn't shared. New members don't get the rules. No standardisation.

**Why D is wrong:** skills are invoked on demand — universal standards must always be loaded. Skills are for task-specific procedures, CLAUDE.md for universal standards."""},
("base",3,3):{"body":"""A team has these requirements:

1. A `/deploy-checklist` command the whole team will use — a pre-deployment checklist
2. One developer wants a personal `/deep-analyze` skill that performs large codebase analyses — it produces very detailed output and must not pollute the main conversation
3. The `/deep-analyze` skill must use only read tools — no file writes or deletes

**Which configuration is correct?**""",
 "opts":{"A":"Both go in `.claude/commands/`.",
         "B":"`/deploy-checklist` → `.claude/commands/` (project-scoped). `/deep-analyze` → a `SKILL.md` in `~/.claude/skills/` with the `context: fork` and `allowed-tools: [Read, Grep, Glob]` frontmatter.",
         "C":"Both should be written as procedures in CLAUDE.md.",
         "D":"`/deploy-checklist` → `~/.claude/commands/`. `/deep-analyze` → `.claude/skills/`."},
 "expl":"""**Why B is correct:** it meets all three requirements:
1. `/deploy-checklist` is team-wide → `.claude/commands/` (project-scoped, in Git, shared)
2. `/deep-analyze` is personal with detailed output → `~/.claude/skills/` (personal) + `context: fork` (isolated context, main conversation clean)
3. Read tools only → `allowed-tools: [Read, Grep, Glob]` (destructive actions blocked)

**Why A is wrong:** `/deep-analyze` is a personal request — putting it in team commands affects everyone. `context: fork` and `allowed-tools` are also configured in skill frontmatter.

**Why C is wrong:** these are task-specific procedures — CLAUDE.md is for universal standards. CLAUDE.md is always loaded, no on-demand invocation.

**Why D is wrong:** the placement is reversed. `/deploy-checklist` must be team-wide (`.claude/commands/`); the personal directory isn't shared. `/deep-analyze` must be personal (`~/.claude/skills/`); the team directory affects everyone."""},
("base",3,4):{"body":"""In a codebase the API endpoint files are scattered across `src/api/`, `src/routes/` and `modules/*/api/`. The team wants the same rules in all API files: rate-limiting checks, input validation, standardised error responses.

**What is the right approach?**""",
 "opts":{"A":"Copy the same rules into `src/api/CLAUDE.md`, `src/routes/CLAUDE.md` and every `modules/*/api/CLAUDE.md`.",
         "B":"Create `.claude/rules/api-conventions.md` — with the frontmatter `paths: [\"src/api/**/*\", \"src/routes/**/*\", \"modules/*/api/**/*\"]`.",
         "C":"Write all API rules into the root CLAUDE.md.",
         "D":"Create an `/api-rules` skill — invoked whenever an API file is touched."},
 "expl":"""**Why B is correct:** path-specific rules catch API files across the whole codebase via glob patterns — whatever directory they're in. One rule file applies to all the scattered API files. Token-efficient — loaded only while editing an API file.

**Why A is wrong:** copying the same rules into every directory is a maintenance nightmare. When a rule changes, every copy must be updated. Path-specific rules solve this with one file.

**Why C is wrong:** the root CLAUDE.md is always loaded. Even while editing a frontend CSS file the API rules occupy context — token waste.

**Why D is wrong:** skills are invoked on demand — you'd have to remember to invoke it every time an API file is touched. Path-specific rules load automatically."""},
("base",3,5):{"body":"""A developer has been given three tasks:

1. Convert the existing REST API to GraphQL — 40+ endpoints affected
2. Fix an off-by-one error in a single function — error message and stack trace available
3. Understand a large legacy module — 30 files, unclear dependencies — very detailed output expected in the exploration phase

**Which mode is correct for each task?**""",
 "opts":{"A":"1: Plan mode, 2: Direct execution, 3: Explore sub-agent + plan mode",
         "B":"1: Direct execution, 2: Direct execution, 3: Plan mode",
         "C":"1: Plan mode, 2: Plan mode, 3: Direct execution",
         "D":"All plan mode — stay on the safe side."},
 "expl":"""**Why A is correct:**
1. **REST → GraphQL = plan mode.** 40+ endpoints, architectural decision, multi-file change. Analyse first, design the schema, then implement.
2. **Off-by-one error = direct execution.** Stack trace available, single file, clear bug. Planning unnecessary.
3. **Legacy module exploration = Explore sub-agent + plan mode.** 30 files, unclear dependencies — the Explore sub-agent isolates the detailed exploration (main conversation stays clean), then plan mode designs the restructuring.

**Why B is wrong:** doing a 40+ endpoint migration with direct execution is far too risky. Impact analysis and schema design come first.

**Why C is wrong:** plan mode is unnecessary for an off-by-one error. Direct execution is dangerous for the legacy module — changing without exploring.

**Why D is wrong:** plan mode for simple bug fixes wastes time. Matching the right mode to the right task matters."""},
("base",3,6):{"body":"""A developer wants to replace the lodash library with native JavaScript functions in 30 files. They planned this approach:

1. First, in plan mode, discover the affected files and determine the migration strategy
2. Then implement the plan with direct execution

**Is this approach correct?**""",
 "opts":{"A":"No — the whole process should stay in plan mode, never switching to direct execution.",
         "B":"Yes — the hybrid approach is correct. Research and design in plan mode, implement with direct execution.",
         "C":"No — the whole process should be direct execution; 30 files is a small number.",
         "D":"No — the Explore sub-agent should be used instead of plan mode."},
 "expl":"""**Why B is correct:** the hybrid approach (plan → direct execution) is a common and expected pattern. Discover the lodash usages across 30 files in plan mode, determine which native functions replace them, then implement with direct execution. The most efficient approach.

**Why A is wrong:** implementing in plan mode is needlessly slow. Once the plan is complete, direct execution is faster.

**Why C is wrong:** a 30-file migration requires exploration and planning. Starting with direct execution leads to problems.

**Why D is wrong:** the Explore sub-agent can be part of the exploration phase but isn't enough on its own. Plan mode covers exploration + design. Explore is used additionally when very detailed exploration output needs isolating."""},
("base",3,7):{"body":"""A developer gives Claude Code this instruction:

*"Make the error messages more user-friendly — remove technical jargon and write descriptive messages."*

Claude Code produces a different result every time — sometimes very formal, sometimes very informal, sometimes mixing languages. Inconsistent.

**Which technique should be tried first?**""",
 "opts":{"A":"Add a \"be consistent\" instruction to the prompt.",
         "B":"Give 2–3 concrete input/output examples — before/after examples of the form old error message → new error message.",
         "C":"Create a separate command for each error message.",
         "D":"Run Claude Code in a test mode and check each output manually."},
 "expl":"""**Why B is correct:** the prose instruction is interpreted inconsistently — "user-friendly" means something different to everyone. Concrete examples are precise — 2–3 before/after examples of the form "given this old message, produce this new message" let the model extract the pattern and apply it consistently.

**Why A is wrong:** "be consistent" is also a prose instruction — ambiguous. Claude is already trying to be consistent; the problem is the instruction's ambiguity.

**Why C is wrong:** over-engineering. Creating hundreds of commands for hundreds of error messages isn't practical. 2–3 examples are far simpler and more effective.

**Why D is wrong:** manual checking isn't sustainable. Checking every output instead of improving automatically throws away Claude Code's advantage."""},
("base",3,8):{"body":"""A team generates tests automatically with Claude Code in its CI pipeline. The generated tests:

- Consist of empty test scaffolds — they don't test real business logic
- Don't use the existing fixtures — they create mocks from scratch in every test
- Use inconsistent frameworks — sometimes jest, sometimes vitest

Pipeline command: `claude -p "Generate tests for the changed files"`

**What are the root cause and the fix?**""",
 "opts":{"A":"The `-p` flag lowers test quality — it should run in interactive mode.",
         "B":"Test standards, valuable-test criteria and existing fixtures aren't documented in CLAUDE.md. Adding this information to CLAUDE.md lets Claude Code generate high-quality, standards-compliant tests.",
         "C":"Claude Code isn't suited to test generation — another tool should be used.",
         "D":"A separate prompt should be written for each test file."},
 "expl":"""**Why B is correct:** Claude Code gets project context from CLAUDE.md. If test standards, the framework preference (vitest), fixtures and valuable-test criteria aren't documented in CLAUDE.md, Claude Code produces generic boilerplate tests. Once added: the right framework, existing fixtures, meaningful tests that exercise business logic.

**Why A is wrong:** the `-p` flag doesn't affect test quality — it only turns off waiting for interactive input. It's mandatory in CI. The quality problem comes from missing context.

**Why C is wrong:** Claude Code can generate tests — given the right context. The problem isn't the tool's ability but the missing configuration.

**Why D is wrong:** a separate prompt per file isn't sustainable. Define the standards once in CLAUDE.md and they're applied automatically on every run."""},
("extra",3,0):{"body":"""In a large monorepo, test files (`*.test.ts`, `*.spec.ts`) are spread across more than 60 different directories. The team wants to define special rules (fixture usage, mock standards) that load only while test files are being edited, and doesn't want those rules bloating the context while working on other files.

**Which mechanism fits best?**""",
 "opts":{"A":"Add the test rules to the root `CLAUDE.md` — always loaded.",
         "B":"Put a `CLAUDE.md` with the test rules in each of the 60+ directories.",
         "C":"Create a path-based rule file under `.claude/rules/` with the glob patterns `**/*.test.ts` and `**/*.spec.ts` defined in its YAML frontmatter.",
         "D":"Move the test rules into a skill and have developers invoke it when writing tests."},
 "expl":"""**Why C is correct:** path-based rules (`.claude/rules/` + glob pattern) catch files scattered across the whole codebase with one definition, and load **only while a matching file is being edited**. Both requirements — coverage (60+ directories) and token efficiency — are met. Exam trap: "apply rules to test files in N directories" → path-based rules.

**Why A is wrong:** the root CLAUDE.md is always loaded — it bloats the context in non-test work too. The exact opposite of the requirement.

**Why B is wrong:** a directory-level CLAUDE.md applies to one directory; 60+ copies are a maintenance nightmare and a source of inconsistency. They also load for non-test files in that directory.

**Why D is wrong:** skills are invoked manually; they don't guarantee automatic application of the rules. If a developer forgets to invoke it, the rule isn't applied."""},
("extra",3,1):{"body":"""A developer wants Claude Code to write API error messages in a specific format. They wrote a three-paragraph explanation in the root `CLAUDE.md`: *"Error messages should be user-friendly, contain no technical detail, but give the developer helpful context…"*. Result: the format differs on every run — sometimes too technical, sometimes too vague.

**What is the most effective improvement?**""",
 "opts":{"A":"Expand the explanation to five paragraphs and define every rule in more detail.",
         "B":"Replace the prose explanation with 2–3 concrete before/after examples: bad message → good message pairs.",
         "C":"Correct the output by hand each time and show Claude the correction — it learns over time.",
         "D":"Use a bigger model; small models can't follow long instructions."},
 "expl":"""**Why B is correct:** the most effective iterative-refinement technique is concrete input/output examples. Prose definitions such as "user-friendly but with context" are subjective and interpreted differently on every run. 2–3 before/after examples pin down the target — the model generalises better from examples than from prose. Exam trap: "prose is interpreted inconsistently" → answer: concrete examples.

**Why A is wrong:** more prose means more room for interpretation. The source of the inconsistency isn't the explanation's brevity but its subjectivity.

**Why C is wrong:** Claude doesn't learn across sessions; each manual correction is one-off. Lasting improvement must be reflected in the CLAUDE.md definition.

**Why D is wrong:** model size doesn't make a subjective definition objective. A bigger model interprets "user-friendly" differently too."""},
("extra",3,2):{"body":"""Before every PR, a team types the same 6-step checklist (lint, type check, tests, changelog update, security scan, PR description generation) into Claude Code by hand each time. Team members write the steps in different orders or leave some out; results are inconsistent.

**What is the most appropriate fix?**""",
 "opts":{"A":"Write the 6 steps into the root `CLAUDE.md` — loaded in every session.",
         "B":"Create a custom slash command such as `pr-check.md` under `.claude/commands/`; define the 6 steps in one reusable command and commit it to the repo.",
         "C":"Each developer defines their own shortcut under `~/.claude/`.",
         "D":"Move the steps into a CI pipeline and take Claude Code out of the loop."},
 "expl":"""**Why B is correct:** for a repeated, multi-step workflow a custom slash command is the exact fix: the steps are defined once, run consistently via `/pr-check`, and because it's committed to the repo the whole team uses the same version.

**Why A is wrong:** CLAUDE.md is for always-applicable **rules**; writing a workflow procedure there loads unnecessary tokens in every session and has no "run now" trigger.

**Why C is wrong:** personal shortcuts aren't shared — the team-wide inconsistency problem continues unchanged.

**Why D is wrong:** some steps (PR description generation, changelog writing) can't be done mechanically in CI. And the question asks how to improve the Claude Code workflow, not remove it."""},
("extra",3,3):{"body":"""A team added automated Claude Code review of every PR to GitHub Actions. Two weeks later: the review step takes 25 minutes on some PRs, the agent sometimes tries to merge the PR directly into `main`, and API cost is 4× the forecast.

**Which set of changes addresses all three problems correctly?**""",
 "opts":{"A":"Remove the review step and run it manually once a week.",
         "B":"Restrict the agent's permissions to read + comment only (no merge/push rights), limit the review scope to the PR diff only, and put a time/turn limit on the run.",
         "C":"Tell the agent in the system prompt \"never merge and finish in 5 minutes\".",
         "D":"Use a smaller model — faster and cheaper."},
 "expl":"""**Why B is correct:** in CI/CD the agent runs autonomously with no human oversight — so the limits are set **through configuration**: (1) permissions narrowed to the minimum (least privilege: read + comment, no merge), (2) scope limited to the diff so the agent doesn't wander the whole repo burning time and money, (3) a turn/time limit bounds both duration and cost.

**Why A is wrong:** destroys the value of the automation; the problem isn't automation, it's unbounded automation.

**Why C is wrong:** a prompt instruction is probabilistic — "never merge" isn't a permission constraint. If merge rights exist, the risk exists. High-risk actions are blocked at the permission layer.

**Why D is wrong:** a smaller model lowers review quality and does nothing about the merge attempts. The real source of the cost is unbounded scope."""},
})

Q_EN.update({
("base",4,1):{"body":"""A code review agent running in a CI/CD pipeline reports three categories: security vulnerabilities, logic errors and code-style issues. Developers noticed the "code style" category has a 60% false-positive rate. This has started to shake their trust in the security findings too.

**What is the best short-term action?**""",
 "opts":{"A":"Raise the confidence thresholds of the security and logic categories to 95%, make all categories more conservative",
         "B":"Use a bigger model for all three categories",
         "C":"Temporarily disable the code-style category; keep security and logic running, improve the code-style prompt",
         "D":"Restructure the agent completely; merge the categories"},
 "expl":"""**Explanation:**

A trust problem requires isolation. The code-style category is poisoning the reliability of the other categories with its high false-positive rate. Fix: temporarily remove the badly performing category, keep the good ones running, improve the bad one separately.

- **(A) Wrong:** raising thresholds misses real problems; the issue is criteria, not thresholds.
- **(B) Wrong:** a bigger model doesn't fix a prompt-calibration problem.
- **(D) Wrong:** a complete restructure is disproportionate and slow.

**Concept covered:** Task 4.1 — the false-positive trust problem and the isolation fix"""},
("base",4,2):{"body":"""An agent was given this severity definition: *"Critical: issues that threaten the system. Minor: small issues."*

Which of the following is the fundamental problem caused by this definition?""",
 "opts":{"A":"\"Critical\" and \"minor\" aren't technical jargon; the agent can't understand them",
         "B":"The definitions are prose-based; because \"threaten the system\" is subjective, the agent calibrates differently on every run",
         "C":"Two levels aren't enough; at least five are needed",
         "D":"These definitions can only be used in the security domain, not for general code review"},
 "expl":"""**Explanation:**

"Issues that threaten the system" is open to interpretation. Claude can calibrate this threshold differently on every run — the same code looks critical one time and minor the next. Fix: define severity with real code examples.

- **(A) Wrong:** the terms are understood; the problem is that they're subjective.
- **(C) Wrong:** the number of levels isn't the problem; concreteness is.
- **(D) Wrong:** these definitions have a general validity problem.

**Concept covered:** Task 4.1 — prose definitions vs calibration with code examples"""},
("base",4,3):{"body":"""An extraction pipeline processes different document formats: some invoices are tables, some plain text, some nested lists. The model sometimes returns "null" for fields even though the information is present.

**What is the most effective fix?**""",
 "opts":{"A":"Make all fields \"required\" in the JSON schema — prevents returning null",
         "B":"Instruct the model \"if the information exists you must extract it, never return null\"",
         "C":"Add 2–4 few-shot examples showing successful extraction from each format type; one should cover the \"null if no information\" scenario",
         "D":"Deploy a separate model per document format"},
 "expl":"""**Explanation:**

The model can't find the information in the document — a format-variety problem. Few-shot examples teach the map "the information is here" for each format. The "null if no information" example ensures returning null instead of inventing.

- **(A) Wrong:** required fields lead to fabrication — the model is forced to invent a value for the required field.
- **(B) Wrong:** this instruction was already tried; it doesn't fix the format problem.
- **(D) Wrong:** a separate model is over-engineering.

**Concept covered:** Task 4.2 — reducing hallucination in document extraction"""},
("base",4,4):{"body":"""A code review agent classifies certain cases inconsistently: to the question "does this comment misdescribe the code's behaviour, or is it an old note?" it gives different answers on different runs. You've rewritten the instructions three times — the problem persists.

**What should you do in this situation?**""",
 "opts":{"A":"Make the instructions more detailed; explain every possible scenario separately",
         "B":"Add few-shot examples for the 2–4 ambiguous cases; in each example show the reasoning for why a decision was made",
         "C":"Add a confidence threshold as a parameter: \"don't flag if unsure\"",
         "D":"Use a bigger model — inconsistency is a capacity problem"},
 "expl":"""**Explanation:**

Instruction rewriting was tried repeatedly — it didn't work. That shows the volume of instructions isn't the problem. The fix for inconsistency in ambiguous cases: show examples of those ambiguous cases + their reasoning.

- **(A) Wrong:** lengthening the instructions was already tried and failed.
- **(C) Wrong:** a confidence threshold "skip if unsure" — but the real problem is when the decision should be made.
- **(D) Wrong:** the problem isn't model capacity but how ambiguous cases are handled.

**Concept covered:** Task 4.2 — few-shot + reasoning for ambiguous cases"""},
("base",4,5):{"body":"""An invoice extraction system uses tool_use. All JSON output is syntactically valid. However the downstream system reports invoice total mismatches: the sum of line items doesn't equal the stated total.

**What is the most appropriate approach to fix this?**""",
 "opts":{"A":"Remove tool_use, switch to prompt-based JSON",
         "B":"Add a `calculated_total` field to the schema; in the validation step check `stated_total == calculated_total`; send a retry on mismatch",
         "C":"Use a bigger model — the small model makes arithmetic errors",
         "D":"Make all fields \"required\" — so no value is missing"},
 "expl":"""**Explanation:**

Tool_use fixes syntax problems — the JSON is valid. But it doesn't prevent semantic errors (wrong total). Once `calculated_total` is added to the schema, the model fills it by summing each line; the validation step detects the mismatch and a retry gives a chance to fix it.

- **(A) Wrong:** prompt-based JSON loses the syntax guarantee.
- **(C) Wrong:** changing the model doesn't fix this kind of semantic inconsistency.
- **(D) Wrong:** required fields raise the fabrication risk and don't verify the total.

**Concept covered:** Task 4.3 — limits of tool_use + semantic validation"""},
("base",4,6):{"body":"""A pipeline receives documents in unknown formats (invoice, contract, receipt or other). Different extraction tools were defined per format. **Guaranteed structured output** is required.

**Which `tool_choice` setting should be used?**""",
 "opts":{"A":"`\"auto\"` — the model picks the most suitable tool",
         "B":"`{\"type\": \"tool\", \"name\": \"extract_invoice\"}` — every document is processed with the invoice tool",
         "C":"`\"any\"` — the model must call a tool, and decides which one itself",
         "D":"Don't specify `tool_choice` — the default behaviour gives guaranteed output"},
 "expl":"""**Explanation:**

`"any"` forces the model to call a tool — guaranteed structured output. The model decides which tool to pick based on the document type.

- **(A) Wrong:** `"auto"` can return a text response — no guarantee.
- **(B) Wrong:** forcing a specific tool treats every document as an invoice — misclassification.
- **(D) Wrong:** the default is `"auto"` — no guarantee.

**Concept covered:** Task 4.3 — tool_choice modes"""},
("base",4,7):{"body":"""An extraction system keeps returning null for the `payment_terms` field. A retry message was sent: *"payment_terms cannot be null, required field."* The second attempt also returned null.

**What is the correct diagnosis and fix?**""",
 "opts":{"A":"Increase the retry count — the model eventually finds the right value",
         "B":"Use a stronger model — the small model doesn't see the field",
         "C":"The information is probably not in the document; retry is ineffective. Make `payment_terms` nullable/optional",
         "D":"Add a few-shot example: show \"how to extract payment_terms\""},
 "expl":"""**Explanation:**

Still null after two retries — the problem is that the information isn't in the document. The model is looking at the same document; if the information isn't there, retry doesn't help. The right fix: make the field nullable.

- **(A) Wrong:** retry doesn't fix a source problem — it only spends time and money.
- **(B) Wrong:** a bigger model will look at the same document.
- **(D) Wrong:** few-shot teaches "how to extract", but if the information isn't there no example helps.

**Concept covered:** Task 4.4 — the limit of retry effectiveness"""},
("base",4,8):{"body":"""An engineering team runs two tasks: (a) a weekly analysis of 200 documents archived every night, (b) a security scan that runs when a pull request is opened. To cut costs they plan to move both to the Batch API.

**Is this plan correct? Explain.**""",
 "opts":{"A":"Yes, both tasks are suitable for batch",
         "B":"Yes, but only the weekly analysis should use batch; the security scan must stay synchronous",
         "C":"No, the Batch API can only be used for fewer than 10 documents",
         "D":"Yes, but batch jobs only run between 00:00 and 06:00"},
 "expl":"""**Explanation:**

The weekly archive analysis is latency-tolerant — batch is suitable. The PR security scan is a blocking workflow — developers wait for the result before merging; synchronous is required.

- **(A) Wrong:** the PR security scan can't wait.
- **(C) Wrong:** the Batch API isn't limited by document count.
- **(D) Wrong:** the Batch API doesn't run on a time window.

**Concept covered:** Task 4.5 — the synchronous vs batch decision rule"""},
("base",4,9):{"body":"""A code review system analyses each file in a separate instance (50 files = 50 calls). Per-file findings are collected. However some cross-file problems are missed: for example, data sanitised in file A being used unsafely in file B.

**What should you do to fix this?**""",
 "opts":{"A":"Give all 50 files to a single instance — it sees the cross-file context",
         "B":"In addition to the per-file analyses, run an independent cross-file integration pass that sees all file findings",
         "C":"Split the files into groups of 5, use a single instance per group",
         "D":"Leave cross-file problems to human review; automation only works per file"},
 "expl":"""**Explanation:**

Per-file analysis prevents attention dilution — that part works correctly. But to detect cross-file problems you need an independent integration pass that sees all file findings.

- **(A) Wrong:** giving 50 files to a single instance causes attention dilution.
- **(C) Wrong:** grouping is a partial fix; it doesn't provide a full cross-file view.
- **(D) Wrong:** automation can detect cross-file problems too — before a human steps in.

**Concept covered:** Task 4.6 — multi-pass architecture"""},
("base",4,10):{"body":"""A team is building an invoice processing pipeline. Requirements:

1. Invoices arrive in different formats (table, text, nested list)
2. JSON must always be syntactically valid
3. Semantic validation (total mismatch) is required
4. 2,000 invoices are processed per week, cost is critical
5. Some invoices have no `payment_terms` information
6. High-confidence findings go automatic, low-confidence findings to human review

**Which option describes this system correctly?**""",
 "opts":{"A":"Process all 2,000 invoices with the synchronous API; make all schema fields required; tool_choice: auto; no validation step",
         "B":"Few-shot examples for invoice formats; JSON schema via tool_use (payment_terms nullable); validation with calculated_total; Batch API (latency-tolerant); confidence-based routing",
         "C":"A multi-pass architecture per invoice (50 instances); all fields required; no retry loop; synchronous API",
         "D":"Prompt-based JSON (no tool_use); leave all validation to humans; Batch API; no few-shot"},
 "expl":"""**Explanation:**

Each requirement maps to a technique:

| Requirement | Technique |
|---|---|
| Format variety | Few-shot examples (Task 4.2) |
| Valid JSON | Tool_use + JSON schema (Task 4.3) |
| Semantic validation | calculated_total + validation (Task 4.4) |
| Cost + latency tolerance | Batch API (Task 4.5) |
| payment_terms sometimes absent | Nullable field (Task 4.3) |
| Confidence-based routing | confidence routing (Task 4.6) |

- **(A) Wrong:** required fields cause fabrication; auto tool_choice gives no guarantee; no validation.
- **(C) Wrong:** 50 instances per invoice for 2,000 invoices is excessive; all-required is a fabrication risk.
- **(D) Wrong:** prompt-based JSON is unreliable; leaving all validation to humans doesn't scale.

**Concept covered:** Tasks 4.1–4.6 integrated application"""},
("extra",4,0):{"body":"""A company wants to classify 20,000 customer reviews every night; the results must make the 09:00 morning report, but minute-level precision doesn't matter. The same team also runs a synchronous review step on every PR in the code repository. An engineer wanting to cut cost proposes moving both workloads to the Batch API.

**Which assessment is correct?**""",
 "opts":{"A":"Move both to the Batch API — the 50% saving applies everywhere.",
         "B":"Move the overnight classification to the Batch API (latency-tolerant, 50% cost advantage, completes within 24 hours); keep the PR review synchronous (blocking workflow, batch has no SLA).",
         "C":"Move neither — the Batch API isn't reliable for production workloads.",
         "D":"Move the PR review to the Batch API (code review takes long), keep the overnight classification synchronous (volume is large)."},
 "expl":"""**Why B is correct:** the Batch API decision follows latency tolerance. Overnight classification: large volume, hours of tolerance, no hard deadline → batch is ideal (50% saving, up to 24 hours processing). PR review: the developer waits for the result, the merge is blocked → synchronous is mandatory; batch has no SLA, the PR could wait for hours.

**Why A is wrong:** blocking workflows (CI/CD, pre-merge) are always synchronous. Batch's lack of an SLA breaks the PR flow.

**Why C is wrong:** the Batch API is designed precisely for latency-tolerant, high-volume production workloads.

**Why D is wrong:** the mapping is reversed. Volume doesn't require synchronous; latency tolerance is the deciding factor."""},
("extra",4,1):{"body":"""In a code review system a single Claude session reviews a 35-file PR and then self-reviews its own findings with a "look again" instruction. Despite that, cross-file data-flow bugs (a return type changed in one file breaking a call in another) keep slipping through.

**What is the most effective architectural change?**""",
 "opts":{"A":"Repeat the self-review step 3 times — new problems are caught each round.",
         "B":"Run independent review instances per file (to prevent attention dilution), then add a separate cross-file integration pass that takes the findings as input; the finding-producing instances don't carry each other's context.",
         "C":"Instead of sending 35 files in one prompt, use a model with a bigger context window.",
         "D":"Add the sentence \"pay special attention to cross-file type mismatches\" to the review prompt."},
 "expl":"""**Why B is correct:** self-review is limited — the same session carries the same blind spots. The fix has two layers: (1) independent instances per file → each file gets full attention, no earlier context pollution; (2) a separate cross-file integration pass → data-flow and contradiction problems are caught exactly here, because this pass's input is the findings from all files.

**Why A is wrong:** re-running the same session repeats the same blind spots. What's missed comes from the context structure, not from lack of effort.

**Why C is wrong:** the problem isn't the context not fitting; 35 files in one context cause attention dilution. A bigger window doesn't fix dilution.

**Why D is wrong:** prompt emphasis may help but doesn't fix the architectural problem (single session, diluted attention, no cross-pass)."""},
("extra2",5):{"body":"""In a contract extraction schema the `termination_date` field is defined as `required`. An audit found that for open-ended contracts with no end date the model produced plausible-looking but invented dates. The JSON always conforms to the schema.

**What are the root cause and the fix?**""",
 "opts":{"A":"The model is hallucinating — use a bigger model.",
         "B":"Because the field is `required` the model invents a value to satisfy the schema; make the field **nullable/optional** and state the rule \"return null if not in the document\" in the prompt.",
         "C":"Add a retry loop — the invented dates get corrected on the second attempt.",
         "D":"Remove the `termination_date` field from the schema entirely."},
 "expl":"""**Why B is correct:** a field defined as required pushes the model to invent when the source document lacks the information. If the information may be absent from the document, the field is designed as **nullable**; returning null becomes a valid output and the hallucination disappears.

**Why A is wrong:** the problem isn't model capacity but the schema design forcing the model. A bigger model also tries to fill a required field.

**Why C is wrong:** retry doesn't work if the information isn't in the document — the model invents again. Retry fixes format errors; it doesn't create missing information.

**Why D is wrong:** for contracts that do have an end date this is a valuable field; removing it is data loss."""},
("extra2",6):{"body":"""In an invoice extraction schema the `expense_category` field has this enum: `["travel","software","hardware","office"]`. In production, when expenses that don't fit these four categories arrive (training, consulting, legal) the model squeezes them into a random category; the accounting reports come out wrong.

**How should the schema be fixed?**""",
 "opts":{"A":"Remove the enum, make the field free text.",
         "B":"Add an `\"other\"` value to the enum and a `category_detail` (free text) field next to it; if needed also define an `\"unclear\"` value for ambiguous cases.",
         "C":"Update the enum for every new expense type and redeploy the pipeline.",
         "D":"Instruct in the prompt \"mark non-matching expenses as office\"."},
 "expl":"""**Why B is correct:** the standard pattern for extensible categories: `"other"` + a detail field. Instead of squeezing non-matching cases, the model picks `other` and gives the detail as free text; accounting can review those records separately. `"unclear"` also explicitly marks ambiguous cases.

**Why A is wrong:** the consistency the enum provides (always the same label for the same expense) is lost; reporting breaks.

**Why C is wrong:** unsustainable — every new type needs a deploy and is still misclassified the first time it arrives.

**Why D is wrong:** deliberately producing wrong data; the problem becomes invisible but the reports are still wrong."""},
("extra2",7):{"body":"""In an extraction pipeline the Pydantic validation reports "expected ISO 8601, got '15/03/2024'" for the `invoice_date` field. The current retry logic resends the same prompt with no changes; the success rate is 12%.

**How should the retry be designed?**""",
 "opts":{"A":"Raise the retry count from 3 to 8.",
         "B":"Add the original document, the failed extraction and the **specific validation error** to the retry request (\"invoice_date must be ISO 8601; '15/03/2024' found\") — let the model make a targeted correction.",
         "C":"Remove the validation — fix the date format downstream.",
         "D":"Use a different model for the retry."},
 "expl":"""**Why B is correct:** retry-with-error-feedback: without knowing what went wrong the model repeats the same mistake. Given the document + the failed output + the specific error together, format errors are fixed at a high rate. This is a format error — exactly the class where retry works.

**Why A is wrong:** more attempts with the same input produce the same output; the success rate stays down to chance.

**Why C is wrong:** removing the validation signal pushes the problem downstream and hides other errors too.

**Why D is wrong:** the problem isn't the model but the retry without feedback. Changing the model adds cost and complexity."""},
("extra2",8):{"body":"""In a 5,000-document Batch API submission 180 requests failed: 140 with "context length exceeded", 40 with a temporary server error. The engineer plans to resubmit all 5,000 documents as they are.

**What is the correct approach?**""",
 "opts":{"A":"Go ahead with the plan — batch repeats are cheap.",
         "B":"Isolate only the 180 failed documents via `custom_id`; resubmit the 140 that exceeded context in chunks (chunking), and the 40 with the temporary error as they are.",
         "C":"Process the 180 documents one by one with the synchronous API — batch is unreliable.",
         "D":"Drop the context-exceeding documents from the pipeline; resubmit only the 40 temporary errors."},
 "expl":"""**Why B is correct:** the rule of batch error handling: match request to response via `custom_id`, resubmit **only the failures**, and resubmit with a change matching the cause — chunking for size overflow, as-is for temporary errors.

**Why A is wrong:** reprocessing 4,820 successful documents is needless cost and time; and the 140 fail again unless changed.

**Why C is wrong:** batch isn't unreliable; the failures have explainable causes. Synchronous processing doubles the cost and doesn't fix the context problem.

**Why D is wrong:** dropping 140 documents is data loss; they can be processed with chunking."""},
# --- mock-only EXTRA2 questions for Domains 2 and 3 that were still Turkish ---
("extra2",0):{"body":"""A developer productivity agent makes 15–20 exploratory tool calls every session to understand the open work in the team's Jira (`list_projects`, then `list_issues` per project, then `get_issue` per issue). This consumes the first minutes of the session and a large share of the context budget.

**What is the most appropriate fix?**""",
 "opts":{"A":"Instruct the agent \"only look at the 5 most important issues first\".",
         "B":"Expose the issue summaries as an **MCP resource** (a content catalogue) on the MCP server — the agent sees a map of the available data in one go, no exploratory calls needed.",
         "C":"Merge the three tools into a single `get_everything` tool.",
         "D":"Write the exploratory call results to a file and reuse them in later sessions."},
 "expl":"""**Why B is correct:** MCP resources exist exactly for this: they make content catalogues (issue summaries, document hierarchies, database schemas) visible to the agent **without exploratory tool calls**. Tools are for actions, resources are for visibility.

**Why A is wrong:** the instruction doesn't reduce exploration cost — the agent still has to list to know which 5 issues matter.

**Why C is wrong:** one giant tool returns enormous data in one call; it bloats the context more than exploratory calls and breaks tool focus.

**Why D is wrong:** the cache goes stale (issues change) and doesn't change the nature of the problem — it's still tool-based exploration, just deferred."""},
("extra2",1):{"body":"""The team configured a powerful MCP server capable of semantic code search (`code_search`: returns symbol definitions, the call graph and type information). But according to the logs the agent almost always prefers the built-in Grep tool and hardly ever calls the MCP tool. The MCP tool's description: *"Searches code."*

**What is the most effective first step?**""",
 "opts":{"A":"Remove Grep from the agent's tool set — so it's forced to use the MCP tool.",
         "B":"Enrich the MCP tool's description: explain what it returns (symbol definitions, call graph, type information), which queries it beats Grep for, and example uses.",
         "C":"Write \"always use code_search, never Grep\" in the system prompt.",
         "D":"Remove the MCP server — the built-in tools are enough."},
 "expl":"""**Why B is correct:** tool selection rests on descriptions. With the description "Searches code" the agent can't see how the MCP tool differs from Grep and picks the familiar one. A description that spells out capabilities and outputs lets the agent prefer the more capable tool **by its own decision**. Low effort, high impact.

**Why A is wrong:** Grep has valid uses (error-message search, simple patterns). Removing it loses capability; the root cause (a weak description) isn't fixed.

**Why C is wrong:** a rigid prompt instruction forces the MCP tool even where Grep fits better; it's also probabilistic. Without fixing the description, the instruction papers over the symptom.

**Why D is wrong:** the problem isn't that the MCP tool is unnecessary but that it isn't discoverable."""},
("extra2",2):{"body":"""The agent uses the Edit tool to replace the line `return null;` in a file with `return defaultConfig;`. The tool returns an error: the expression `return null;` occurs in 7 different places in the file and it's ambiguous which one to change.

**What is the correct approach?**""",
 "opts":{"A":"Call Edit 7 times — change them all.",
         "B":"Give Edit wider, unique context (e.g. include the preceding lines with the function signature); if that fails too, load the whole file with Read, make the targeted change and write the whole thing back with Write.",
         "C":"Run `sed` via Bash and replace the first match.",
         "D":"Delete the file and regenerate it from scratch."},
 "expl":"""**Why B is correct:** Edit requires a unique text match. The first step is adding enough context to make the match unique; if that isn't possible, the official fallback is **Read + Write**: load the full file, make the change, write it all. Always works, just more expensive.

**Why A is wrong:** only one place should change; changing 7 breaks behaviour.

**Why C is wrong:** the "first match" may not be the right place; sed's escaping rules are error-prone and it bypasses the safety/permission layer of Claude Code's file tools.

**Why D is wrong:** disproportionate and risky — the rest of the file can change during regeneration."""},
("extra2",3):{"body":"""An agent is tasked with understanding "how the refund flow works" in an unfamiliar 1,200-file codebase. Current approach: the agent first reads all files with Read, then tries to answer. The context usually fills up within the first 200 files and the agent never reaches the actual flow.

**What is the correct exploration strategy?**""",
 "opts":{"A":"Use a model with a bigger context window and keep reading all files.",
         "B":"Incremental exploration: find the entry points with Grep (e.g. `refund`, `processRefund`), then open only the relevant files with Read and follow the imports to trace the flow.",
         "C":"List all `.ts` files with Glob and read them in alphabetical order.",
         "D":"Instruct the agent \"only read the important files\"."},
 "expl":"""**Why B is correct:** codebase understanding is built **incrementally**: find entry points with Grep, follow imports with Read to trace the flow. Only relevant files enter the context; maybe 15 of the 1,200 files get read.

**Why A is wrong:** 1,200 files fit in no context; even if they did, attention dilution follows. The approach is structurally wrong.

**Why C is wrong:** Glob matches path patterns, it doesn't look at contents; alphabetical reading has nothing to do with relevance.

**Why D is wrong:** the agent can't know what's important without looking at contents — the instruction offers no concrete method."""},
("extra2",4):{"body":"""A developer is working on a multi-phase task: first exploring and understanding a large legacy module, then applying a series of changes. The exploration phase produces dozens of file reads and long Grep output; by the time implementation starts, the main conversation's context is full of exploration noise and Claude Code becomes inconsistent during implementation.

**What is the most appropriate approach?**""",
 "opts":{"A":"Delegate the exploration phase to an **Explore subagent** — the detailed read/search output stays in the subagent's context, only a structured summary returns to the main conversation; then run the implementation phase in a clean context.",
         "B":"Keep exploration and implementation in the same session but run `/compact` every 10 files.",
         "C":"Skip the exploration phase — go straight to implementation, reading files as needed.",
         "D":"Open a separate session for each file."},
 "expl":"""**Why A is correct:** the Explore subagent exists for exactly this scenario: it isolates noisy exploration output, returns a summary to the main conversation and prevents context exhaustion in multi-phase tasks. A subagent for plan-mode/exploration + a clean context for implementation is a good combination.

**Why B is wrong:** `/compact` can help, but specific findings (class names, line numbers) can be lost during summarisation; it's more reliable for the noise never to enter the main context at all.

**Why C is wrong:** changing a legacy module without exploration means dependencies are discovered late and costly rework follows.

**Why D is wrong:** context loss between sessions — every session re-explores from scratch."""},
("extra2",10):{"body":"""The Claude Code review in CI runs from scratch on every new commit. Developers complain that issues already commented on and still unfixed are added again as new comments every time, and PRs fill up with dozens of duplicate comments.

**What is the most appropriate fix?**""",
 "opts":{"A":"Run the review only when the PR is first opened.",
         "B":"On re-runs, provide the earlier review findings in the context and tell Claude to report only **new or still-unresolved** issues, skipping repeats.",
         "C":"Delete all old comments on the PR before every run.",
         "D":"Limit the review to the last commit's diff only."},
 "expl":"""**Why B is correct:** given the earlier findings in context, Claude knows what was already reported; it reports only new or still-open issues. The duplicate-comment problem is solved at the source and the history is preserved.

**Why A is wrong:** later commits aren't reviewed — new bugs slip through.

**Why C is wrong:** review history and developer discussions are deleted; the same issues come back as new comments anyway.

**Why D is wrong:** the last commit may not contain the open issues from earlier commits; cross-file context is lost too."""},
("extra2",11):{"body":"""A CI step takes the output of `claude -p "Review the PR"` and tries to post it line by line as PR comments. Because the output is free text, parsing frequently breaks: sometimes bullet points, sometimes a table, sometimes paragraphs; file name and line number appear in inconsistent positions.

**What is the correct fix?**""",
 "opts":{"A":"Add \"write every finding in the 'file:line — message' format\" to the prompt and parse with a regex.",
         "B":"Force the output to a schema (file, line, severity, message, suggestion) with the `--output-format json` and `--json-schema` flags; let the CI step turn the structured JSON directly into inline comments.",
         "C":"Paste the output as-is into a single PR comment.",
         "D":"Run the review in interactive mode and copy the output by hand."},
 "expl":"""**Why B is correct:** the official mechanism for machine-readable output in CI is `--output-format json` + `--json-schema`. The schema is enforced, format surprises disappear, and inline PR comment generation becomes deterministic.

**Why A is wrong:** asking for a format via a prompt instruction is probabilistic; the regex keeps breaking. Using that while schema enforcement exists is an anti-pattern.

**Why C is wrong:** the value of inline, line-based comments is lost; the developer has to hunt for the line meant.

**Why D is wrong:** CI is automation; interactive mode suspends the pipeline (`-p` exists for exactly that reason)."""},
})

Q_EN.update({
("base",5,1):{"body":"""A customer support agent works across long conversations. To manage the token budget the conversation history is summarised every 5 turns. In turn 3 the customer stated: "I want a $189.50 refund for order #7723, placed on 15 February."

In turn 10 the agent says to the customer: "Which order can I help you with?"

At the same time, tool results are added to the context as-is — every order lookup returns 45 fields.

**Which approach fixes both problems?**""",
 "opts":{"A":"Enlarge the context window and reduce the summarisation frequency to every 10 turns",
         "B":"Extract the transactional facts (order no, amount, date) into a persistent \"case facts\" block and never summarise it. Trim the tool results to the 5 relevant fields, then add them to the context.",
         "C":"Add \"never forget customer details\" to the agent's system prompt and store tool results in JSON format",
         "D":"Don't summarise — keep the whole conversation history as-is"},
 "expl":"""**Explanation:**

Two problems at once: the progressive summarisation trap (order details lost during summarisation) and tool-result bloat (45 fields added to the context as-is). Fix: preserve the transactional facts with a case facts block + trim verbose results to the relevant fields with tool result trimming.

- **(A) Wrong:** a bigger context window and lower summarisation frequency delay the problem, they don't fix it. The same information loss happens at turn 10.
- **(C) Wrong:** a prompt instruction is probabilistic. If the summarised information has been physically removed from the context, the instruction does nothing. JSON format doesn't fix tool-result bloat.
- **(D) Wrong:** never summarising exhausts the token budget quickly — unsustainable in long conversations.

**Concept covered:** Task 5.1 — case facts block + tool result trimming"""},
("base",5,2):{"body":"""In a multi-agent research system the web search agent returns a 3-page detailed analysis, chain of thought and alternative hypotheses for every query. The downstream synthesis agent's context budget is 8K tokens. The budget is exhausted after 3 sources — but 7 sources must be analysed.

**What is the most effective fix?**""",
 "opts":{"A":"Raise the synthesis agent's context budget to 64K",
         "B":"Reduce the number of sources to 3 — it fits the budget",
         "C":"Modify the web search agent to return structured data (key facts, citations, relevance score) — instead of verbose content and chains of thought",
         "D":"Add \"write briefly\" to the synthesis agent"},
 "expl":"""**Explanation:**

Upstream agent optimisation. The problem isn't in the synthesis agent but in the web search agent's verbose output. Returning structured data (key facts, citations, relevance score) instead of a 3-page chain of thought uses the token budget efficiently.

- **(A) Wrong:** raising the budget is expensive and doesn't fix the structural problem — at 15 sources the same problem returns.
- **(B) Wrong:** narrowing the scope lowers research quality.
- **(D) Wrong:** the fix in the wrong place. The problem isn't the synthesis agent's output but its input.

**Concept covered:** Task 5.1 — upstream agent optimisation"""},
("base",5,3):{"body":"""A customer writes to a support agent: "This order hasn't arrived for 3 days, I'm getting really angry now!" The agent checks the order status and sees it will be delivered today.

**What should the agent do?**""",
 "opts":{"A":"The customer is angry → escalate to a human representative immediately",
         "B":"Acknowledge the frustration and offer the resolution: \"I'm sorry for the delay. Your order will be delivered today — your tracking number is X.\"",
         "C":"Check the customer's confidence score — escalate if low",
         "D":"Tell the customer \"calm down\" and to keep waiting"},
 "expl":"""**Explanation:**

The customer is angry but the problem is simple — the order is delivered today. Sentiment-based escalation is an unreliable trigger. Correct: acknowledge the frustration, offer the resolution.

- **(A) Wrong:** sentiment-based escalation — anger isn't proportional to case complexity.
- **(C) Wrong:** the model confidence score is an unreliable escalation trigger.
- **(D) Wrong:** "calm down" damages the customer experience and doesn't solve the problem.

**Concept covered:** Task 5.2 — unreliable triggers + the frustration nuance"""},
("base",5,4):{"body":"""A customer says "This product is $20 cheaper on a competitor's site, I want a price match." The agent checks the policy document: "We refund the difference on price drops on our own site." The policy has no information about competitor price matching.

At the same time, a customer search for the name "Ahmet Yılmaz" returns 4 different "Ahmet Yılmaz" matches.

**Which approach handles both situations correctly?**""",
 "opts":{"A":"Accept the competitor price match by interpreting the policy broadly. Of the 4 matches pick the one with the most recent order.",
         "B":"Refuse the competitor price match — it's not in the policy. Pick the most active customer account.",
         "C":"Competitor price matching is a policy gap — escalate. For the customer match, ask for additional identifying information (email, phone, order no).",
         "D":"Decide by the customer's mood — escalate if angry, refuse if calm. Pick one of the 4 matches at random."},
 "expl":"""**Explanation:**

Two separate problems: (1) competitor price matching isn't defined in the policy — a policy gap, escalation is needed. (2) 4 customer matches — no heuristic pick, ask for additional identifying information.

- **(A) Wrong:** no authority to interpret the policy broadly. A heuristic customer pick risks a wrong match.
- **(B) Wrong:** refusing outright isn't appropriate for a policy gap — a human should decide. A heuristic customer pick is wrong.
- **(D) Wrong:** a sentiment-based decision is unreliable. A random customer pick is unacceptable.

**Concept covered:** Task 5.2 — policy gap + ambiguous customer matching"""},
("base",5,5):{"body":"""A research pipeline collects data from 6 academic databases. 5 databases returned results successfully. The 6th (PubMed) gave a network timeout error. The agent's current behaviour: when an error occurs it returns an empty result array with `"status": "success"`.

**What is the problem with this behaviour and the correct fix?**""",
 "opts":{"A":"No problem — an empty result is a valid result",
         "B":"The silent suppression anti-pattern. Marking an access failure as successful blocks the recovery mechanism. Correct: report the failure type (transient), what was attempted and the partial results in a structured way.",
         "C":"Stop the pipeline entirely — continuing with incomplete data is dangerous",
         "D":"Retry PubMed in an infinite loop — eventually it works"},
 "expl":"""**Explanation:**

The silent suppression anti-pattern. Marking an access failure as `"success"` blocks every recovery mechanism. Correct: report the failure type (transient/network timeout), what was attempted (the PubMed query, parameters) and the partial results in a structured way.

- **(A) Wrong:** this is an access failure, not a valid empty result. Network timeout = the source couldn't be reached.
- **(C) Wrong:** the workflow termination anti-pattern. Throws away the results of 5 successful sources.
- **(D) Wrong:** infinite retry locks the system.

**Concept covered:** Task 5.3 — silent suppression + structured error context"""},
("base",5,6):{"body":"""A customer support agent searches for an order by the customer's phone number. The tool returns:

```json
{
  "status": "success",
  "results": [],
  "message": "No orders found for this phone number"
}
```

The agent takes this result and retries 3 more times with the same phone number.

**What is the problem with this behaviour?**""",
 "opts":{"A":"Too few retries — it should try 10 times",
         "B":"It should retry with different parameters — try email instead of phone",
         "C":"The agent is confusing a valid empty result with an access failure. Status \"success\" — the tool reached the source and found no match. That is the answer itself; retry is unnecessary.",
         "D":"The tool is faulty — it should always return at least one result"},
 "expl":"""**Explanation:**

The access failure vs valid empty result distinction. Status `"success"` → the tool reached the source successfully. `results: []` → no match found. This isn't an access failure but a valid empty result. Retrying gives the same result.

- **(A) Wrong:** more retries return the same valid empty result.
- **(B) Wrong:** changing parameters arbitrarily risks reaching the wrong customer. Ask the customer for additional information first.
- **(D) Wrong:** the tool works correctly — "no match" is a valid answer.

**Concept covered:** Task 5.3 — access failure vs valid empty result"""},
("base",5,7):{"body":"""A developer has been analysing a large codebase with an agent session for 4 hours. At the start the agent reported specific class names, line numbers and method signatures. Now it uses generic phrases like "dependency injection is generally used in these modules".

At the same time, the team complains that when these agent sessions crash they have to start from scratch.

**Which approach fixes both problems?**""",
 "opts":{"A":"Use a model with a bigger context window and never close the session",
         "B":"Write the key findings to a scratchpad file. Delegate deep investigations to subagents. Have each agent write its state to a manifest file — after a crash the coordinator recovers by loading the manifests.",
         "C":"Add \"be specific\" to the agent and store the full conversation history in a database in case of a crash",
         "D":"Restart the session every hour — so there's no context degradation"},
 "expl":"""**Explanation:**

Two problems: (1) context degradation — the shift from specific findings to generic phrases. Fix: scratchpad + subagent delegation. (2) missing crash recovery. Fix: each agent writes its state to a manifest file, the coordinator loads it during recovery.

- **(A) Wrong:** a bigger model delays context degradation, doesn't fix it. "Never close" ignores the crash scenario.
- **(C) Wrong:** a prompt instruction doesn't fix context degradation — the information has physically dropped. Storing the full history in a database restores verbose data — it exhausts the context budget immediately.
- **(D) Wrong:** restarting every hour loses the earlier findings — unsustainable.

**Concept covered:** Task 5.4 — context degradation + crash recovery"""},
("base",5,8):{"body":"""A document extraction system reports 96% overall accuracy. Management plans to move to full automation. Field-level confidence thresholds were set at 80% — intuitively, without any validation data.

Internal audit reports two findings:
1. There's a 35% error rate on handwritten documents
2. In fields where the model says 85% confidence, real accuracy is 58%

**Which approach addresses both problems?**""",
 "opts":{"A":"Raise the confidence threshold to 95% and remove handwritten documents from the pipeline",
         "B":"Evaluate accuracy separately by document type and field segment — route handwritten documents to human review. Calibrate the confidence thresholds with labelled validation sets (ground truth data).",
         "C":"Use a bigger model — both accuracy and confidence scores improve",
         "D":"Keep 100% human review for all document types — automation is unreliable"},
 "expl":"""**Explanation:**

Two problems: (1) the aggregate metrics trap — 96% overall accuracy hides the 35% error on handwritten documents. Fix: evaluate separately by document type, route low-performing types to human review. (2) uncalibrated confidence — 85% confidence = 58% accuracy. Fix: calibrate with labelled validation sets.

- **(A) Wrong:** raising the threshold doesn't fix the calibration problem. Removing handwritten documents is data loss.
- **(C) Wrong:** a bigger model guarantees neither calibration nor per-document-type performance.
- **(D) Wrong:** 100% human review is a needless resource cost — unnecessary for standard invoices at 99.5% accuracy.

**Concept covered:** Task 5.5 — aggregate metrics trap + confidence calibration"""},
("base",5,9):{"body":"""In a research report two sources report different values for the same metric:
- IEA (March 2024): "Global wind capacity 1,021 GW"
- GWEC (June 2024): "Global wind capacity 1,089 GW"

The synthesis agent flags this as "conflicting data" and removes both sources from the report.

**What is the right approach?**""",
 "opts":{"A":"Use the more recent GWEC value — the latest data is correct",
         "B":"Take the average of the two — 1,055 GW",
         "C":"Present both values with source citations and dates. Note that the difference may stem from different measurement periods — temporal context.",
         "D":"Removing both sources from the report is correct — conflicting data is unreliable"},
 "expl":"""**Explanation:**

Temporal awareness + conflict handling. IEA March 2024 and GWEC June 2024 — different measurement periods give different values. This isn't a conflict but change over time. Present both values with dates, state the temporal context.

- **(A) Wrong:** the assumption "the latest data is correct" doesn't always hold — they measure different periods.
- **(B) Wrong:** the average is meaningless — a mix of different periods.
- **(D) Wrong:** removing both sources is information loss — explainable by temporal context.

**Concept covered:** Task 5.6 — temporal awareness + conflict handling"""},
("base",5,10):{"body":"""A company is building a comprehensive multi-agent system covering customer support + research + document extraction. The system has these problems:
1. The customer support agent asks for the customer's order number again in turn 8
2. Angry customers are automatically routed to a human representative — 60% of cases were simple requests the agent could have resolved
3. When one source times out in the research pipeline, the whole research is cancelled
4. The synthesis report contains vague phrases like "significant developments occurred in the sector" — no specific values or sources
5. Document extraction reports 95% overall accuracy but performance per document type hasn't been tested

**Which option correctly maps these 5 problems?**""",
 "opts":{"A":"All problems are solved with a bigger model",
         "B":"1. Case facts block → preserve transactional facts; 2. Remove sentiment-based escalation → three valid triggers; 3. Continue with partial results → structured error report + coverage annotation; 4. Structured claim-source mappings → preserve claim-source links; 5. Validation by document type → stratified performance analysis",
         "C":"1. Reduce summarisation frequency; 2. Lower the escalation threshold; 3. Increase the retry count; 4. Write a more detailed system prompt; 5. Raise the confidence threshold to 99%",
         "D":"1. Keep the full conversation history — never summarise; 2. Route all customers to a human representative; 3. Remove the faulty source from the pipeline; 4. Add \"be specific\" to the synthesis agent; 5. 100% human review for all document types"},
 "expl":"""**Explanation:**

Each problem maps to a different Domain 5 concept:

| Problem | Concept | Fix |
|---|---|---|
| 1. Order no asked again | Task 5.1 — progressive summarisation | Case facts block |
| 2. Angry customers needlessly escalated | Task 5.2 — unreliable trigger | Sentiment-based → three valid triggers |
| 3. One error cancels all research | Task 5.3 — workflow termination | Continue with partial results + report the error |
| 4. Vague phrases in the synthesis report | Task 5.6 — citation death | Claim-source mappings |
| 5. Not tested by document type | Task 5.5 — aggregate metrics trap | Stratified validation |

- **(A) Wrong:** a bigger model doesn't fix structural problems — each needs a different architectural fix.
- **(C) Wrong:** every fix is superficial — none addresses the root cause (summarisation frequency, escalation threshold, retry count, prompt instruction, confidence threshold).
- **(D) Wrong:** extreme fixes — never summarising, routing all customers, removing the source, 100% human review are all resource waste and data loss.

**Concept covered:** Tasks 5.1–5.6 integrated application"""},
("extra2",9):{"body":"""An extraction system writes fields with a confidence score above 90% directly into the ERP without human review. For six months nobody has checked these "high-confidence" outputs. A new supplier started using a different layout on its invoices, and errors flowed into the system unnoticed.

**What mechanism is missing?**""",
 "opts":{"A":"Raise the confidence threshold to 99%.",
         "B":"Continuously route a portion of the high-confidence extractions to human review via **stratified random sampling** — monitor the error rate and catch novel error patterns (such as a new document layout) early.",
         "C":"Put all extractions back under 100% human review.",
         "D":"Process the new supplier's invoices manually."},
 "expl":"""**Why B is correct:** high confidence doesn't mean "no audit needed". Stratified random sampling measures the real error rate on the automated path and makes **novel error patterns** such as distribution shift (a new layout, a new supplier) visible. It's a permanent monitoring mechanism.

**Why A is wrong:** raising the threshold doesn't catch the cases where the model is wrongly confident; the model can report 95% confidence on the new layout too.

**Why C is wrong:** destroys the value of the automation; disproportionate.

**Why D is wrong:** fixes this supplier but you'll notice the next change late again — no systemic mechanism."""},
})
