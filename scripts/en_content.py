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
("base",2,1):{"body":"""A customer-support agent has 3 tools:

- `get_account_info`: "Retrieves account information"
- `get_billing_info`: "Retrieves billing information"
- `get_subscription_info`: "Retrieves subscription information"

Users complain: when they say "I want to upgrade my subscription" the agent calls `get_account_info`; billing queries go to `get_subscription_info`. Overall misrouting rate is 30%.

**What should be done as the first step?**""",
 "opts":{"A":"Merge the three tools into a single `get_customer_data` tool — Claude can't err with one tool.",
         "B":"Add few-shot examples to the system prompt: \"use get_billing_info for billing questions, get_subscription_info for subscription questions\".",
         "C":"Expand each tool's description — state explicitly which data fields it returns, which query types it serves, and how it differs from the other tools; sharpen the names if needed (`get_billing_history`, `get_subscription_plan`).",
         "D":"Add an intent classifier before Claude — it analyzes the query and routes to the right tool."},
 "expl":"""**Why C is correct:** The root cause is vague descriptions — all three follow the "retrieves X information" format, and Claude can't differentiate. Expanding the descriptions (which fields it returns, which queries it serves, how it differs) and renaming if needed is a low-effort, high-leverage fix; it applies two exam-guide Skills together ("writing descriptions that clearly differentiate" + "renaming tools and updating descriptions").

**Why A is wrong:** Merging doesn't remove the ambiguity, it moves it into the tool — now the tool has to guess which data to return. Three different output contracts don't fit one tool; separation of concerns breaks.

**Why B is wrong:** Few-shot examples add token cost and treat the symptom, not the root cause. Prompt-based guidance is probabilistic; while descriptions are vague it won't provide a reliable fix.

**Why D is wrong:** An intent classifier is over-engineering for a first step. You haven't tried the simple fix (improving descriptions). A classifier adds complexity and maintenance cost."""},
("base",2,2):{"body":"""An agent has an `analyze_document` tool. In a single call it summarizes the document (output: plain text), extracts key data (output: list of JSON records) and verifies claims (output: supported/unsupported + evidence per claim). The three operations also have different input requirements: verification needs a list of claims, summarization doesn't. The agent sometimes runs unnecessary verification when only a summary is wanted, and sometimes returns only a summary when verification is wanted.

**What are the root cause and the fix?**""",
 "opts":{"A":"The tool's description is insufficient — write a more detailed description.",
         "B":"The tool combines three different purposes and three different input/output contracts in one interface — split it into purpose-specific tools: `summarize_content`, `extract_data_points` and `verify_claim_against_source`.",
         "C":"Add \"only perform the requested operation\" to the system prompt.",
         "D":"Add an `operation_type` field to the tool's input parameters — Claude specifies which operation it wants."},
 "expl":"""**Why B is correct:** The splitting criterion is not "how many operations" but "how many distinct purposes and output contracts". Here there are three different output schemas and different input requirements — one tool can't offer them under a coherent contract. Splitting into purpose-specific tools defines each tool precisely for one job with a defined input/output contract. Exam-guide Skill: "Splitting generic tools into purpose-specific tools with defined input/output contracts."

**Why A is wrong:** Improving the description clarifies *when* Claude calls the tool, but doesn't change *what the tool returns* — it still does all three jobs and the output schema stays ambiguous.

**Why C is wrong:** A prompt instruction is probabilistic. "Only perform the requested operation" doesn't change the tool's do-all-three structure — this is an interface problem, not a prompt problem.

**Why D is wrong:** An `operation_type` parameter selects the operation but doesn't fix the output contract — the tool returns three different schemas depending on `operation_type`, and Claude can't infer from the description which schema to expect; the `claims` parameter needed for verification is meaningless for the other operations. If these were steps of one workflow (see the `schedule_event` consolidation example) a single tool would be defensible; here there are three separate purposes."""},
("base",2,3):{"body":"""An agent is attempting an international money transfer. The MCP tool returns:

```json
{
  "isError": true,
  "content": [{ "type": "text", "text": "{\\"errorCategory\\":\\"business\\",\\"isRetryable\\":false,\\"description\\":\\"Transfer amount ($15,000) exceeds the daily limit ($10,000).\\",\\"customerMessage\\":\\"Your daily transfer limit is $10,000. Contact your account manager for higher limits.\\"}" }]
}
```

**What should the agent do?**""",
 "opts":{"A":"Wait 5 seconds and retry — it may be a transient error.",
         "B":"Automatically reduce the transfer amount to $10,000 and retry.",
         "C":"Not retry. Relay the `customerMessage` information to the customer and offer an alternative path (referral to the account manager).",
         "D":"Fix the input and retry — it may be a validation error."},
 "expl":"""**Why C is correct:** `errorCategory: "business"` and `isRetryable: false` — this is a business-rule violation; retrying is WRONG. Until the policy changes, the same operation fails every time. The agent should relay the `customerMessage` to the customer and offer an alternative path.

**Why A is wrong:** This is not a transient error — it's a business-rule error. Waiting doesn't change policy. `isRetryable: false` explicitly rejects a retry.

**Why B is wrong:** Changing the amount automatically overrides the customer's request. That business decision belongs to the customer; the agent must not reduce it to $10,000 on its own.

**Why D is wrong:** This is not a validation error — the format is right, the amount is a valid number. The problem is a business rule: the daily limit is exceeded. `errorCategory: "business"` states this explicitly."""},
("base",2,4):{"body":"""You are writing your own MCP server. The `lookup_order` tool throws a `-32602 Invalid params` JSON-RPC protocol error when the order number isn't in the database, and returns an empty result with `content: []` when the database connection drops. In production, the agent keeps saying "an error occurred" for non-existent order numbers, and during a database outage tells the customer "your order was not found".

**What are the root cause and the correct design?**""",
 "opts":{"A":"Increase the retry count — database outages are solved by retries.",
         "B":"Both situations are reported through the wrong channel. \"Order not found\" is a valid empty result → `isError: false` + `resultCount: 0`. A dropped database connection is a tool execution error → `isError: true` + `errorCategory: \"transient\"`, `isRetryable: true`. Protocol errors should be used only for unknown tools / arguments that violate the schema.",
         "C":"Throw a protocol error in both cases — so the client behaves consistently.",
         "D":"Add \"say 'order not found' instead of 'an error occurred'\" to the system prompt."},
 "expl":"""**Why B is correct:** MCP defines two error mechanisms: a protocol error (JSON-RPC `error`) does **not** reach the model — it stays in the client layer; a tool execution error (`isError: true`) reaches the model, which can self-correct. A non-existent order isn't even an error — a successful query with zero matches (`isError: false`). A dropped database connection is a real access failure; `isError: true` + transient/retryable metadata lets the agent make a retry decision. The current design encodes both situations backwards.

**Why A is wrong:** Retries don't change an empty result (non-existent order), and the agent won't recognize an outage returned as an empty array as an error in the first place, so it won't retry. The problem isn't the retry count; it's the signal structure.

**Why C is wrong:** A protocol error doesn't reach the model — Claude can't see what went wrong, can't fix the input, can't look for an alternative path. Business/API/validation errors must be returned *as results* with `isError: true`.

**Why D is wrong:** The prompt doesn't know what the tool returns in which situation; it can't tell the two apart. A structural problem needs a structural fix."""},
("base",2,5):{"body":"""A research agent has been given 16 tools: 5 web-search tools, 4 document-analysis tools, 3 database-query tools, 2 email tools and 2 calendar tools. The agent frequently picks the wrong tool and struggles to complete tasks.

At the same time, although metadata extraction is a mandatory first step, the agent sometimes skips it and goes straight to analysis.

**Which approach fixes both problems at once?**""",
 "opts":{"A":"Expand all tool descriptions and add \"always extract metadata first\" to the system prompt.",
         "B":"Distribute the tools across role-specific agents (4–5 tools each) and enforce the mandatory first step with `tool_choice: {\"type\": \"tool\", \"name\": \"extract_metadata\"}` on the first request; switch `tool_choice` back to `auto` on subsequent turns.",
         "C":"Distribute the tools across role-specific agents and use `tool_choice: {\"type\": \"tool\", \"name\": \"extract_metadata\"}` on all turns — so the step is never skipped.",
         "D":"Create a single \"do_everything\" tool and run all operations through it."},
 "expl":"""**Why B is correct:** It fixes both problems:
1. **Tool overload:** 16 tools → distribute across role-specific agents (4–5 each). Selection reliability rises.
2. **Mandatory first step:** forced `tool_choice` on the first request makes metadata extraction deterministic; the model can't skip it. Switching to `auto` on later turns lets the model proceed to analysis — exam guide: "ensure a specific tool is called first, then processing subsequent steps in follow-up turns."

**Why A is wrong:** Two-part, but both parts probabilistic. Expanding descriptions partially improves a 16-tool selection problem but doesn't fix the root cause (too many tools). The system-prompt instruction "always extract metadata" isn't a 100% guarantee. Mandatory steps need a deterministic mechanism (tool_choice).

**Why C is wrong:** The distribution part is right, but `tool_choice` is per request; left forced on every turn, the model is forced to call `extract_metadata` **on every turn** and never reaches analysis — an infinite metadata loop. Forced selection only on the first turn; then `auto`.

**Why D is wrong:** A single "do_everything" tool is the exact opposite of tool splitting. Piling all complexity into one tool makes it impossible for Claude to specify what it wants."""},
("base",2,6):{"body":"""In a document-processing pipeline Claude has three tools: `classify_invoice`, `classify_receipt`, `classify_contract` — each returns a different JSON schema. The pipeline parses Claude's response directly with `json.loads`. In production Claude sometimes returns text like "This document looks like an invoice, would you like me to classify it?" instead of calling a tool, and the pipeline crashes. For some documents Claude also calls two classification tools in a single response.

**Which configuration fixes both problems?**""",
 "opts":{"A":"`tool_choice: {\"type\": \"auto\"}` + \"always call a tool\" in the system prompt.",
         "B":"`tool_choice: {\"type\": \"any\"}` + `disable_parallel_tool_use: true` — the model must call one of the three tools, exactly one.",
         "C":"`tool_choice: {\"type\": \"tool\", \"name\": \"classify_invoice\"}` — most documents are invoices.",
         "D":"`tool_choice: {\"type\": \"none\"}` + parse the output with a regex."},
 "expl":"""**Why B is correct:** `any` guarantees the model **must** call a tool instead of returning text; which one is left to the model — one of the three schemas is certain to arrive. Exam-guide Skill: "Setting tool_choice: 'any' to guarantee the model calls a tool rather than returning conversational text." `disable_parallel_tool_use: true` prevents multiple `tool_use` blocks in one response; with `any` it yields the guarantee of "exactly one tool call".

**Why A is wrong:** `auto` leaves the model free to return text; a prompt instruction is probabilistic. A guarantee of "always call a tool" needs deterministic `tool_choice`.

**Why C is wrong:** Forcing one tool classifies receipts and contracts with the invoice schema too — wrong schema, wrong data. The choice should be left to the model while the obligation to call is enforced: that is the definition of `any`.

**Why D is wrong:** `none` switches tool use off entirely — the opposite direction. Parsing free text with a regex throws away the structured-output guarantee."""},
("base",2,7):{"body":"""A team is starting a new project. An MCP server will be configured for GitHub integration. A developer proposes this `.mcp.json`:

```json
{
  "mcpServers": {
    "github": {
      "type": "stdio",
      "command": "github-mcp-server",
      "env": {
        "GITHUB_TOKEN": "ghp_abc123def456ghi789"
      }
    }
  }
}
```

**What is the security problem in this configuration?**""",
 "opts":{"A":"Move the token to `.claude/settings.json` — MCP credentials belong in the settings file.",
         "B":"The GitHub token is written directly into `.mcp.json`. Since this file is under version control, the token will enter the repo. The token should be referenced as the `${GITHUB_TOKEN}` environment variable; each developer defines their own token in their local environment.",
         "C":"`~/.claude.json` should be used instead of `.mcp.json` — MCP configuration should always be at user level.",
         "D":"The token is too short — generate a stronger one."},
 "expl":"""**Why B is correct:** `.mcp.json` is under version control — tracked by Git and pushed to the repo. A token written directly into it is visible to everyone. Fix: the `${GITHUB_TOKEN}` environment-variable syntax (with a default via `${GITHUB_TOKEN:-}` if needed). Each developer sets their own token locally; tokens never enter the repo. Exam guide: "Environment variable expansion in .mcp.json for credential management without committing secrets."

**Why A is wrong:** `.claude/settings.json` is also a shared, version-controlled project file (Domain 3.1) — the token still enters the repo. Changing files relocates the problem rather than solving it; settings.json also isn't the right place for MCP server definitions.

**Why C is wrong:** `.mcp.json` (project) and `~/.claude.json` (user/local) serve different purposes. The team's shared tool configuration is information that should be shared — `.mcp.json` is the right place. The problem isn't the file's location; it's the hardcoded token.

**Why D is wrong:** The token's length or strength isn't the security problem here. Even the strongest token is compromised once it enters the repo."""},
("base",2,8):{"body":"""The team set up an MCP server that performs semantic search over the codebase (`mcp__codesearch__search`). The server does language-aware symbol resolution, cross-repo search and relevance ranking. The tool's description: "Searches code." Observation: Claude Code almost never calls this tool; it always uses the built-in `Grep` for code search and finds nothing on multi-repo queries.

**What is the most effective first step?**""",
 "opts":{"A":"Disable `Grep` via `disallowedTools` — so Claude is forced to use the MCP tool.",
         "B":"Enrich the MCP tool's description: state its capabilities (symbol resolution, cross-repo, relevance ranking), what it returns (file + line + symbol kind + score), and when it should be preferred over the built-in `Grep`.",
         "C":"Move the server to `~/.claude.json` — user-scope servers take precedence.",
         "D":"Write \"always use mcp__codesearch__search for code search\" in CLAUDE.md."},
 "expl":"""**Why B is correct:** The built-in `Grep`'s description is long, detailed and familiar; if the MCP tool says "Searches code", Claude picks the built-in tool that looks richer — even though the MCP tool is actually more capable. Exam-guide Skill: "Enhancing MCP tool descriptions to explain capabilities and outputs in detail, preventing the agent from preferring built-in tools over more capable MCP tools." Domain 2.1's description principles applied to MCP; low effort, root cause.

**Why A is wrong:** Disabling Grep forces Claude onto the heavy MCP tool even for single-repo, simple pattern searches; it suppresses the symptom by force without improving selection quality. And if the MCP server goes down, search capability is lost entirely.

**Why C is wrong:** Scope precedence (local > project > user) applies to conflicts between servers with the same *name*; it does not affect tool *selection*. Where the server is defined has nothing to do with which tool Claude prefers.

**Why D is wrong:** A CLAUDE.md instruction is probabilistic, and "always" forces MCP even for simple searches. The root cause is the weak description; fix that first. (After the description is fixed, a hint like "prefer codesearch for multi-repo searches" in CLAUDE.md could be considered as a supplement — not the first step.)"""},
("base",2,9):{"body":"""A developer is working in a large codebase. They need to:

1. Find all files that call the `fetchUserData` function
2. Find all `.config.yml` files in the project
3. Run the test suite after changing the found files

**Which tool is correct for each task?**""",
 "opts":{"A":"1: Grep, 2: Grep, 3: Grep — Grep handles every kind of search; check test output with Grep.",
         "B":"1: Glob (`**/*fetchUserData*`), 2: Grep (`.config.yml` pattern), 3: Bash.",
         "C":"1: Grep (`fetchUserData` — searches file contents), 2: Glob (`**/*.config.yml` — matches file paths), 3: Bash (`npm test`).",
         "D":"1: Read (read all files, filter), 2: Glob, 3: Edit."},
 "expl":"""**Why C is correct:** Each tool in its area of strength: Grep for content search (function calls live *inside* files), Glob for path matching (the extension is in the file *name*), Bash for running commands (the test suite — the one job no built-in tool can do).

**Why A is wrong:** Grep searches file contents — finding `.config.yml` files requires path matching (Glob). And Grep can't run commands; tests need Bash.

**Why B is wrong:** 1 and 2 are mapped backwards. Glob searches file paths — if `fetchUserData` isn't in a file name it returns nothing. Function calls are in file contents: Grep. The Bash part is right.

**Why D is wrong:** Reading all files with Read is a context-budget killer; Grep does the job in one pass. Edit changes files, it doesn't run tests — step 3 needs Bash."""},
("base",2,10):{"body":"""In Claude Code you want to change the line `timeout: 30` to `timeout: 60` in `config.ts`. The Edit tool returns: "old_string `timeout: 30` appears in 4 places in the file — match is not unique." All four are in different service blocks and you want to change only the one in the `paymentService` block.

**Which approach is correct?**""",
 "opts":{"A":"Re-run Edit with `replace_all: true` — all four lines get updated.",
         "B":"Widen `old_string` with surrounding lines (`paymentService: {\\n  retries: 3,\\n  timeout: 30`) so it matches only that block; if that still fails, load the file with Read and write the modified version with Write.",
         "C":"Run `sed -i 's/timeout: 30/timeout: 60/' config.ts` with Bash.",
         "D":"Write the file from scratch with Write — no need for Read, the content is already known."},
 "expl":"""**Why B is correct:** On Edit's uniqueness error the first step is the cheapest: add context to `old_string` so it matches one place. If that doesn't work, the exam guide's fallback kicks in: "When Edit fails due to non-unique text matches, using Read + Write as a fallback." The Read → Write order is mandatory — Claude Code refuses Write to an existing file that hasn't been read.

**Why A is wrong:** `replace_all` changes all four lines; the scenario wants only the `paymentService` block. `replace_all` is for "when you want every occurrence changed" (like renaming a variable), not for selective edits.

**Why C is wrong:** `sed` also changes all four lines (the same selectivity problem) and throws away Edit's uniqueness guarantee and readable diff; permission stays at the `Bash` level. Falling back to Bash when a built-in tool exists is wrong.

**Why D is wrong:** Write clobbers the whole file; without a Read, Claude Code refuses to write to an existing file, and Claude could lose content it hasn't seen. "The content is already known" is a dangerous assumption made without knowing the file's latest state."""},
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
("base",3,1):{"body":"""A developer wants Claude Code to know, in every session on the e-commerce project they work on, their local sandbox URL (`http://localhost:4010`) and their personal test-customer ID. This is personal — it must not enter the repo. The developer also works on two other projects and wants this information **absent** from context there.

**What is the most appropriate location?**""",
 "opts":{"A":"`~/.claude/CLAUDE.md` — personal, not in Git.",
         "B":"`CLAUDE.local.md` at the project root, added to `.gitignore`.",
         "C":"`.claude/CLAUDE.md` — project level, loaded every session.",
         "D":"`.claude/rules/sandbox.md` with `paths: [\"**/*\"]` in the frontmatter."},
 "expl":"""**Why B is correct:** Two constraints: personal (must not enter the repo) **and** project-specific (must not leak into other projects). `CLAUDE.local.md` exists for exactly that intersection — it sits at the project root, loads alongside `CLAUDE.md`, and goes into `.gitignore`.

**Why A is wrong:** `~/.claude/CLAUDE.md` is personal but loads in **every project** on the machine — the sandbox URL would be in context in the other two projects.

**Why C is wrong:** A project-level file goes into Git; the personal test ID would be shared with the team.

**Why D is wrong:** `.claude/rules/` is project scope and goes into Git; and `**/*` means "every file" — equivalent to an unconditional rule, providing no personal scoping."""},
("base",3,2):{"body":"""A monorepo's root `.claude/CLAUDE.md` has reached 600 lines: general standards + React rules for `web/` + Go rules for `api/` + Terraform rules for `infra/`. The team has two complaints: (1) Claude ignores some rules, (2) even while working in `api/`, the React rules consume tokens.

A developer proposes: split the root file into four parts and import them with `@docs/react.md`, `@docs/go.md`, `@docs/terraform.md`.

**Which of the two complaints does this proposal solve?**""",
 "opts":{"A":"Both — imported files load only while working in the relevant directory.",
         "B":"Only (1), partially — the file becomes organized, but imported files load **at launch** together; total context stays the same and the React rules are still spent in `api/`. For (2), directory-level `web/CLAUDE.md`, `api/CLAUDE.md`, `infra/CLAUDE.md` files (loaded on demand) are needed.",
         "C":"Neither — import syntax only works in `~/.claude/CLAUDE.md`.",
         "D":"Only (2) — imports are lazy-loaded but the file size doesn't change."},
 "expl":"""**Why B is correct:** `@path` imports are an **organization** tool: the files enter context at launch together with CLAUDE.md, saving no tokens. The bloat that leads to ignored rules (complaint 1) improves partially because the file becomes readable; but the real fix is reducing the total loaded text. Only **on-demand** mechanisms do that: directory-level CLAUDE.md (when a file in that directory is read) or `paths` rules.

**Why A is wrong:** Imports are not lazy-loaded; this is the most common confusion between 3.1 and 3.3.

**Why C is wrong:** Imports work in every CLAUDE.md (relative paths resolve relative to the importing file).

**Why D is wrong:** The opposite — imports load at launch; (2) is not solved."""},
("base",3,3):{"body":"""A team has these requirements:

1. A `/deploy-checklist` command for the whole team — a pre-deployment checklist
2. One developer wants a personal `/deep-analyze` skill that performs large codebase analyses — it produces very verbose output and must not pollute the main conversation
3. The `/deep-analyze` skill must only use read tools — no file writes or deletes

**Which configuration is correct?**""",
 "opts":{"A":"Both go in `.claude/commands/`.",
         "B":"`/deploy-checklist` → `.claude/commands/` (project-scoped). `/deep-analyze` → `~/.claude/skills/deep-analyze/SKILL.md` with `context: fork`, `agent: Explore` and `allowed-tools: Read Grep Glob` in the frontmatter.",
         "C":"Both should be written as procedures in CLAUDE.md.",
         "D":"`/deploy-checklist` → `~/.claude/commands/`. `/deep-analyze` → `.claude/skills/`."},
 "expl":"""**Why B is correct:** It meets all three requirements:
1. `/deploy-checklist` is team-wide → `.claude/commands/` (project-scoped, in Git, shared — exam guide Q4)
2. `/deep-analyze` is personal and verbose → `~/.claude/skills/` (personal) + `context: fork` (isolated context, main conversation clean)
3. Read tools only → in exam wording, `allowed-tools: Read Grep Glob`. **Note:** in real behavior `allowed-tools` *pre-approves* rather than restricts; a real restriction comes from `disallowed-tools: Write, Edit, Bash` or `agent: Explore` (which already denies Write/Edit). This option's `agent: Explore` provides that guarantee too.

**Why A is wrong:** `/deep-analyze` is a personal request — putting it in the team repo distributes it to everyone. The `context: fork` / tool-restriction frontmatter is also defined in the skill directory structure.

**Why C is wrong:** These are task-specific procedures — CLAUDE.md is for universal standards and is always loaded.

**Why D is wrong:** The placement is reversed. `/deploy-checklist` must be team-wide; `/deep-analyze` must be personal."""},
("base",3,4):{"body":"""A team created a skill at `.claude/skills/release/SKILL.md`: it tags a release, generates a changelog and runs `git push --tags`. The skill's `description` is "Publishes a new release". While a developer is chatting "I'm wondering whether these changes will make it into the next release", Claude loads the skill on its own and starts the release steps.

**What is the correct fix?**""",
 "opts":{"A":"Move the skill to `~/.claude/skills/` — personal skills aren't auto-triggered.",
         "B":"Add `disable-model-invocation: true` to the frontmatter — the skill loads only when the user types `/release`; Claude can't invoke it via description matching.",
         "C":"Add `context: fork` — the skill runs in an isolated context.",
         "D":"Remove `allowed-tools: Bash(git push *)` — so Claude can't push."},
 "expl":"""**Why B is correct:** Skills are triggered two ways: the user types `/name` **or** Claude decides the `description` matches the conversation. For side-effect workflows (deploy, release, commit) the second path is dangerous. `disable-model-invocation: true` exists for exactly this: "Only you can invoke it manually." The official best-practices example uses it too (the `fix-issue` skill).

**Why A is wrong:** Personal skills are also auto-triggered by description; location doesn't change the trigger path.

**Why C is wrong:** Fork isolates output; it doesn't stop the skill from *starting* by mistake — it keeps releasing in the background.

**Why D is wrong:** Removing `allowed-tools` only brings back the permission prompt; the skill still triggers, starts the steps, and asks permission to push. The root cause is triggering, not permissions."""},
("base",3,5):{"body":"""In a codebase, API endpoint files are scattered across `src/api/`, `src/routes/` and `modules/*/api/`. The team wants the same rules applied to all API files: rate-limiting checks, input validation, standardized error responses. The rules must be applied **automatically, without leaving it to Claude's discretion**.

**Which approach is correct?**""",
 "opts":{"A":"Copy the same rules into `src/api/CLAUDE.md`, `src/routes/CLAUDE.md` and every `modules/*/api/CLAUDE.md`.",
         "B":"Create `.claude/rules/api-conventions.md` — with `paths: [\"src/api/**/*\", \"src/routes/**/*\", \"modules/*/api/**/*\"]` in the frontmatter.",
         "C":"Write all API rules in the root CLAUDE.md.",
         "D":"Create an `/api-rules` skill — put \"use when editing API files\" in its description so Claude loads it when needed."},
 "expl":"""**Why B is correct:** Path-specific rules catch every API file in the codebase via glob patterns — whatever the directory. One rule file applies to all the scattered API files; it loads **deterministically** when a matching file is read. Token-efficient — in context only while working with an API file.

**Why A is wrong:** Copying the same rules into every directory is a maintenance nightmare. Change one rule and you update every copy. CLAUDE.md files are directory-bound.

**Why C is wrong:** The root CLAUDE.md is always loaded. Even while editing a frontend CSS file the API rules take up context — wasted tokens and file bloat.

**Why D is wrong:** The most tempting distractor. Claude *may* load the skill based on the description — but that is a **probabilistic** decision; it contradicts the "without leaving it to Claude's discretion" requirement. Exam guide Q6's rationale for option C: "relies on Claude choosing to load them, contradicting the need for deterministic automatic application based on file paths.\""""},
("base",3,6):{"body":"""A developer is assigned "convert the existing REST API to GraphQL": 40+ endpoints are affected, and decisions about schema design and resolver structure are needed. The developer thinks: "Plan mode adds overhead. I'll convert the first few endpoints in direct execution; if unexpected complexity comes up I'll switch to plan mode."

**How should this approach be assessed?**""",
 "opts":{"A":"Correct — starting with small steps reduces risk; planning once complexity appears is efficient.",
         "B":"Wrong — the complexity is not \"unexpected\"; it's already stated in the requirements (40+ endpoints, schema decisions). Exploration and design in plan mode come first, implementation after approval.",
         "C":"Wrong — the task should be handed entirely to the Explore subagent.",
         "D":"Correct — but the context should be cleared with `/clear` first."},
 "expl":"""**Why B is correct:** The exact counterpart of exam guide Q5's option D: "Begin in direct execution mode and only switch to plan mode if you encounter unexpected complexity" → official rationale: "ignores that the complexity is already stated in the requirements, not something that might emerge later." Many files + architectural decisions + multiple approaches → plan mode. Converting the first endpoints with the wrong schema design and then planning is costly rework.

**Why A is wrong:** The "plan mode is overhead" heuristic is for tasks whose diff fits in one sentence; a 40-endpoint conversion is not in that class.

**Why C is wrong:** Explore is read-only; it only discovers, makes no design decisions and doesn't implement.

**Why D is wrong:** `/clear` resets context; it doesn't fix a wrong mode choice."""},
("base",3,7):{"body":"""A developer wants to replace lodash with native JavaScript functions in 30 files. Their approach:

1. In plan mode, discover the affected files and decide the migration strategy
2. Approve the plan and implement with direct execution

A teammate objects: "Discovery will read too many files and fill the main context. Hand discovery **and implementation** to the Explore subagent."

**Which assessment is correct?**""",
 "opts":{"A":"The teammate is right — Explore both isolates discovery and makes the changes.",
         "B":"The developer's approach is correct (hybrid: plan → approve → direct execution). Discovery is already delegated to the Plan/Explore subagents in plan mode, preserving the main context; but Explore is **read-only** (Write/Edit denied) — it can't implement.",
         "C":"Both are wrong — 30 files is few; the whole thing should be direct execution.",
         "D":"Both are wrong — the whole thing should stay in plan mode, no approval needed."},
 "expl":"""**Why B is correct:** The hybrid approach is plan mode's normal lifecycle: discovery (in subagents) → plan → approve → implement. The teammate's concern (context filling) is already covered by plan mode's built-in Explore/Plan delegation. But the second half of the suggestion is wrong: Explore's tool set is read-only; the built-in subagent that makes changes is `general-purpose`, and implementation happens in the main session after plan approval anyway.

**Why A is wrong:** Explore denies Write/Edit — it can't implement.

**Why C is wrong:** A 30-file migration needs discovery and planning; starting directly creates rework.

**Why D is wrong:** Plan mode can't edit files; approval and a mode switch are required to implement."""},
("base",3,8):{"body":"""A developer reviews a payment function Claude Code wrote. Two findings:

1. Currency conversion rounds incorrectly (cents are lost)
2. The amount the function returns is logged and written to the invoice record based on the rounding result — when the rounding changes, the log format and the invoice field must change too

The developer first had only the rounding fixed; Claude did it, but the log and invoice code stayed on the old behavior. When the log/invoice was fixed in a second message, Claude rewrote the rounding function.

**What should the developer have done?**""",
 "opts":{"A":"Given both findings in one detailed message — the fixes interact; Claude can't make a consistent change without seeing the whole picture.",
         "B":"Fixed the log/invoice first, then the rounding — the order was wrong.",
         "C":"Created a separate skill for each finding.",
         "D":"Given 2–3 concrete input/output examples — the prose was interpreted inconsistently."},
 "expl":"""**Why A is correct:** The findings **interact**: the rounding decision determines the log format and the invoice field. Given sequentially, each round breaks the other — exactly a violation of the exam guide's "single detailed message when fixes interact" rule. One message saying "fix the rounding like this **and** update the log/invoice code to the new result" lets Claude produce a consistent design.

**Why B is wrong:** It's not an ordering problem but an interaction problem; in either order, two separate messages make the second round rewrite the first.

**Why C is wrong:** Skills are for repeated procedures; over-engineering for one-off fixes.

**Why D is wrong:** The problem isn't ambiguous prose (Claude did each fix correctly); the problem is the fixes being given separately."""},
("base",3,9):{"body":"""A CI job runs:

```bash
claude -p "Add missing null checks in src/services/" --output-format json
```

The job doesn't hang; exit code 0. But the `result` field says "I need permission to edit src/services/user.ts…" and no file has changed.

**What are the root cause and the fix?**""",
 "opts":{"A":"`-p` blocks editing — remove `-p` in CI.",
         "B":"A `-p` session starts in Manual permission mode; since nobody in CI can answer the permission prompt, the edits are denied. Add `--allowedTools \"Edit\"` (or `--permission-mode acceptEdits`).",
         "C":"`--output-format json` disables editing — use `text`.",
         "D":"Wrap the command in `timeout 600`."},
 "expl":"""**Why B is correct:** `-p` only removes the interactive UI; the permission system keeps working and `-p` starts in Manual mode. When an edit permission is requested and no answer arrives, the action is denied, Claude reports it in text, and the process exits "successfully". In CI, pre-define the work: tools/commands via `--allowedTools`, or the `acceptEdits` / `dontAsk` / `auto` mode.

**Why A is wrong:** Without `-p` the pipeline hangs. `-p` doesn't block editing; permissions do.

**Why C is wrong:** The output format is only how the result is printed; nothing to do with permissions.

**Why D is wrong:** It's not a time issue; the job already finishes. A timeout doesn't approve a denied permission."""},
("base",3,10):{"body":"""A team generates tests automatically in CI with `claude -p "Generate tests for the changed files"`. CLAUDE.md documents the testing standards (vitest, describe/it), valuable test criteria and fixtures; the generated tests are correct in framework and style. But developers complain: "On every PR, Claude re-proposes the very scenarios that already exist in `tests/auth.test.ts` (invalid token, expired session)."

**What are the root cause and the fix?**""",
 "opts":{"A":"Add a \"don't write duplicate tests\" rule to CLAUDE.md.",
         "B":"Claude doesn't see the existing test files — **provide the existing test files in context** (e.g. `@tests/auth.test.ts`, or include the test files of the changed modules in the prompt) so it doesn't propose scenarios already covered.",
         "C":"Use interactive mode instead of `-p`.",
         "D":"Structure the output with `--json-schema`."},
 "expl":"""**Why B is correct:** The Skills bullet the exam guide counts **separately** from CLAUDE.md: "Providing existing test files in context so test generation avoids suggesting duplicate scenarios already covered by the test suite." CLAUDE.md provides the *rules* (already working here: framework and style are right); only the existing test files show *what's already tested*.

**Why A is wrong:** A "don't write duplicate tests" rule can't be applied if Claude can't see what exists — missing information isn't fixed by a rule.

**Why C is wrong:** Interactive mode hangs in CI; the problem is context, not mode.

**Why D is wrong:** Structured output shapes the *format* of the output; it doesn't prevent duplicate *content*."""},
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
("base",4,1):{"body":"""A CI/CD code review agent reports three categories: security, logic errors, code style. The code style category has a 60% false-positive rate. A team lead says: *"False positives are harmless — the developer filters them out at a glance. The real risk is a missed bug; let's not turn off any category, in fact let's loosen the thresholds."* Another engineer proposes temporarily disabling the code style category.

**Which assessment is correct?**""",
 "opts":{"A":"The team lead is right; a false negative is always more expensive than a false positive, all categories should stay on",
         "B":"The engineer is right; a high false positive category erodes developer trust, and this leads to correctly functioning security findings being ignored as well — the category should be disabled, its criteria clarified, measured, and then re-enabled",
         "C":"Both are wrong; the correct solution is to add a \"don't report if unsure\" instruction for all categories",
         "D":"Both are wrong; the code style category should be moved to a larger model"},
 "expl":"""**Explanation:**

The exam guide's 4.1 Knowledge item: high false-positive categories also erode trust in the *accurate* categories ("undermine confidence in accurate categories"). Trust is holistic; the noise from the code style category leads to security findings being ignored too — which indirectly means missed bugs. Fix: isolation + criteria clarification + measurement on a labeled set + re-enabling.

- **(A) Wrong:** the "false positives are harmless" thesis is exactly what 4.1 refutes; loosening thresholds increases noise.
- **(C) Wrong:** "don't report if unsure" is confidence-based filtering; it filters out both false positives and real findings uncontrollably.
- **(D) Wrong:** the problem is criteria, not capacity.

**Concept covered:** Task 4.1 — False positive / trust relationship and isolation"""},
("base",4,2):{"body":"""An agent was given the following severity definition: *"Critical: Issues that threaten the system. Minor: Small issues."*

Which of the following is the fundamental problem arising from this definition?""",
 "opts":{"A":"The terms \"critical\" and \"minor\" are not technical jargon; the agent cannot understand them",
         "B":"The definitions are prose-based; because \"threatens the system\" is a subjective expression, the agent calibrates differently on every run",
         "C":"Two levels are not enough; at least five levels are required",
         "D":"These definitions can only be used in the security domain and are not suitable for general code review"},
 "expl":"""**Explanation:**

The expression "issues that threaten the system" is open to interpretation. Claude may calibrate this threshold differently on every run — the same code sometimes looks critical, sometimes minor. Solution: define severity with real code examples (with `<example>` tags).

- **(A) Wrong:** the terms are understood; the problem is that they are subjective.
- **(C) Wrong:** the number of levels is not the problem; concreteness is the problem.
- **(D) Wrong:** these definitions carry the same ambiguity problem in every domain.

**Concept covered:** Task 4.1 — Prose definition vs. calibration with code examples"""},
("base",4,3):{"body":"""In an invoice extraction pipeline, the `invoice_date` field returns null for some documents. Investigation: the date *is present* in these documents, but in free-form formats such as "15 Ocak 2024" or "Jan 15, '24"; in table-formatted invoices (date in a separate cell) the field always comes out correctly.

**What is the most effective solution?**""",
 "opts":{"A":"Make the `invoice_date` field nullable — the information cannot be reliably extracted",
         "B":"Add a retry loop with an error message: \"invoice_date is null, the document contains a date, try again\"",
         "C":"Add 2-4 few-shot examples showing successful extraction from documents containing free-form dates (with `<example>` tags, with reasoning)",
         "D":"Route these documents directly to human review"},
 "expl":"""**Explanation:**

The first case of the "null triad": the information **is present** in the document, the model does not recognize the different format. This is 4.2's job — few-shot teaches the "in this format, the date is here" mapping. Working in table format but not in free text confirms that the problem is *format diversity* (the typical finding of the document type × field accuracy table).

- **(A) Wrong:** nullable prevents fabrication when the information is *absent*; accepting null when the information is present is data loss (not 4.3's territory).
- **(B) Wrong:** retry fixes a format *mismatch* (a date extracted in the wrong format); but a format the model does not recognize at all is missed by retry the same way every time — it needs to be taught.
- **(D) Wrong:** handing an automatically solvable problem to humans does not scale.

**Concept covered:** Task 4.2 — null triad (few-shot vs nullable vs retry)"""},
("base",4,4):{"body":"""A code review agent classifies certain cases inconsistently: it gives different answers on different runs to the question "Does this comment misdescribe the code's behavior, or is it an outdated note?" You have rewritten the instructions three times — the problem persists.

**What should you do in this situation?**""",
 "opts":{"A":"Make the instructions more detailed; explain every possible scenario separately",
         "B":"Add few-shot examples for the 2-4 ambiguous cases; in each example, show the reasoning for why a decision was made",
         "C":"Add a \"don't flag if unsure\" instruction (confidence-based filtering)",
         "D":"Use a larger model — inconsistency is a capacity problem"},
 "expl":"""**Explanation:**

Rewriting the instructions was tried repeatedly — it didn't work. This shows that the amount of instruction is not the problem. The solution for inconsistency in ambiguous cases: show examples of those ambiguous cases + their reasoning (exam guide: "*show reasoning for why one action was chosen over plausible alternatives*").

- **(A) Wrong:** lengthening the instructions was already tried and failed.
- **(C) Wrong:** confidence-based filtering; the real problem is *when* the decision is made, not confidence.
- **(D) Wrong:** the problem is not model capacity, but how ambiguous cases are handled.

**Concept covered:** Task 4.2 — Few-shot + reasoning for ambiguous cases"""},
("base",4,5):{"body":"""An invoice extraction system uses `strict: true` tool_use. All JSON outputs conform to the schema. However, in the downstream system, for some invoices the sum of the line items does not equal the stated total.

**What is the most appropriate design to solve this problem?**""",
 "opts":{"A":"Remove tool_use, switch to prompt-based JSON — strict mode is breaking the arithmetic",
         "B":"Add `calculated_total` to the schema; have the backend cross-check with its own sum; on mismatch, send a retry with an error message; if it still doesn't match after the retry, the document is probably internally contradictory → route to human review with `conflict_detected: true`",
         "C":"Use a larger model — the small model is making arithmetic errors",
         "D":"Make all fields \"required\" — so no value is left missing"},
 "expl":"""**Explanation:**

Strict tool_use eliminates schema/syntax errors — but a total mismatch is a **semantic** error (exam guide: "*strict JSON schemas … do not prevent semantic errors, e.g., line items that don't sum to total*"). The solution is layered: `calculated_total` + the backend's independent calculation → retry with error message (if a line was misread, it gets fixed) → if it still doesn't match, the document is internally contradictory, retry cannot solve this → `conflict_detected` + human. The option establishes 4.4's "retry effective / not effective" distinction in a single flow.

- **(A) Wrong:** prompt-based JSON loses the syntax guarantee; strict does not affect arithmetic.
- **(C) Wrong:** changing the model does not replace the validation layer; no model can "correctly" sum a contradictory document.
- **(D) Wrong:** required fields increase the fabrication risk and do not validate the total.

**Concept covered:** Task 4.3 + 4.4 — The limit of strict, semantic validation, retry → conflict flow"""},
("base",4,6):{"body":"""A document pipeline has two stages: first the `extract_metadata` tool must extract the document's type and language, then depending on the type one of the `enrich_invoice` / `enrich_contract` tools must run. On the first call, the model must not jump directly to an enrichment tool.

**What is the correct `tool_choice` for the first call?**""",
 "opts":{"A":"`{\"type\": \"auto\"}` — the model figures out the order itself",
         "B":"`{\"type\": \"any\"}` — the model definitely calls a tool",
         "C":"`{\"type\": \"tool\", \"name\": \"extract_metadata\"}` — this tool is forced; on the next call, `auto` or `any`",
         "D":"`{\"type\": \"none\"}` — have the type determined as text on the first call"},
 "expl":"""**Explanation:**

The exam guide's Skills item, verbatim: "*Forcing a specific tool with `tool_choice: {"type": "tool", "name": "extract_metadata"}` to ensure a particular extraction runs **before enrichment steps**.*" In a sequential flow, `disable_parallel_tool_use: true` is also added.

- **(A) Wrong:** `auto` does not even guarantee a tool call; the order is left to the prompt (probabilistic).
- **(B) Wrong:** `any` guarantees a tool call but not *which one* — the model may jump directly to `enrich_invoice`.
- **(D) Wrong:** `none` prevents any tool call in this turn; the text output is unstructured and requires an extra call.

**Concept covered:** Task 4.3 — tool_choice modes, forcing a specific tool"""},
("base",4,7):{"body":"""A contract extraction system returns null for the `penalty_rate` field. Two retries were sent ("penalty_rate must be in the document, look again") — still null. The document contains the following line: *"See Appendix B for the penalty rate."* Appendix B was not provided to the pipeline.

**What is the correct diagnosis and solution?**""",
 "opts":{"A":"The information is not in the document → make the `penalty_rate` field nullable, accept null",
         "B":"The information is in an external document → retry won't work; add Appendix B to the context and re-run the extraction",
         "C":"Increase the retry count to 5 — the model will eventually find it",
         "D":"Add a few-shot example for `penalty_rate` — the model doesn't recognize the field"},
 "expl":"""**Explanation:**

The exam guide's retry-ineffective example: "*information exists only in an external document not provided*". The document explicitly references Appendix B — the information is *reachable* but not in the context. Retry looks at the same document, null again. The solution is not nullable, but **adding the missing document**; then the extraction (with retry if needed) works.

- **(A) Wrong:** nullable is correct when the information is *nowhere*; here there is a reference — accepting null is data loss.
- **(C) Wrong:** the retry count does not produce information the model does not have.
- **(D) Wrong:** few-shot teaches "how to extract"; as long as the information is not in the context, examples won't help.

**Concept covered:** Task 4.4 — Retry effectiveness limit (external document)"""},
("base",4,8):{"body":"""A company promises its customers that "an uploaded document is processed within 30 hours at most." Documents arrive irregularly throughout the day. For cost reasons, the Message Batches API will be used (processing upper bound 24 hours, no latency SLA).

**Which is the correct plan?**""",
 "opts":{"A":"Batch cannot be used — since the Batch API has no SLA, it is never used for any job with an SLA",
         "B":"One batch per day (at 02:00 at night) — most batches finish within 1 hour anyway",
         "C":"Send a batch at least every 6 hours (4 hours is safer): worst-case latency = wait + 24 hours ≤ 30 hours",
         "D":"Send documents one by one as individual batches as they arrive — each document finishes within 24 hours at most"},
 "expl":"""**Explanation:**

Exam guide Skills: "*4-hour windows to guarantee 30-hour SLA with 24-hour batch processing*". Formula: worst-case latency = waiting for the next submission (P) + 24 hours processing ≤ SLA → P ≤ 30 − 24 = **6 hours**. The guide's 4-hour window leaves a 2-hour margin.

- **(A) Wrong:** "no latency SLA" ≠ "no SLA can be given"; the 24-hour upper bound is enough to do the calculation. If the SLA were ≤ 24 hours, A would be correct.
- **(B) Wrong:** with one submission per day, a document arriving at 02:05 waits 24 hours + 24 hours processing = 48 > 30. "Most finish within 1 hour" is an average, not a guarantee.
- **(D) Wrong:** a batch per document defeats the purpose of batching (bulk submission) and creates rate limit / management overhead; also "finishes within 24 hours" is again an upper bound — technically it meets the SLA, but it is not the *planning* the question asks for.

**Concept covered:** Task 4.5 — Calculating submission frequency from the SLA"""},
("base",4,9):{"body":"""In an extraction pipeline, the model misses subtle errors (values placed in the wrong field, overlooked line items). There are three proposals: (1) add a "review your output carefully, fix errors" instruction to the extraction prompt; (2) enable extended thinking and increase the budget; (3) have the extraction validated by a separate Claude call that does not see the producer's reasoning.

**Which is the most effective?**""",
 "opts":{"A":"(1) — the cheapest; the model knows its own output best",
         "B":"(2) — more thinking budget provides more validation",
         "C":"(3) — the independent instance does not carry the production context; self-review instructions and thinking stay inside the same context",
         "D":"(1) + (2) together are as effective as (3) and cheaper"},
 "expl":"""**Explanation:**

Exam guide 4.6 Knowledge: "*Independent review instances (without prior reasoning context) are more effective at catching subtle issues than **self-review instructions or extended thinking**.*" A validation problem is not solved by *doing more* in the same session; it is solved by *changing the context*.

- **(A) Wrong:** "knows its own output best" is exactly the source of the problem — it inherits the production assumptions.
- **(B) Wrong:** thinking makes it think longer, not *from a different angle*; it operates inside the production context.
- **(D) Wrong:** the sum of two inadequate methods does not solve the context problem.

**Concept covered:** Task 4.6 — The limit of self-review; the instruction / thinking / independent instance triad"""},
("base",4,10):{"body":"""A team is building an invoice processing pipeline. Requirements:

1. Invoices arrive in different formats (table, text, nested list)
2. JSON must always conform to the schema
3. Semantic validation (total mismatch) is required
4. 2,000 invoices per week; cost is critical; there is a 36-hour processing commitment to the customer
5. Some invoices have no `payment_terms` information
6. High-confidence fields are automatic, low-confidence fields go to human review

**Which option correctly describes this system?**""",
 "opts":{"A":"Synchronous API (no batch because there is an SLA); all fields required; `tool_choice: auto`; no validation",
         "B":"Few-shot with `<example>` tags for format diversity; `strict: true` tool_use (payment_terms nullable); `calculated_total` + backend validation + retry with error message; Batch API, submission at least every 12 hours (12 + 24 ≤ 36); routing by per-field enum confidence, calibrated with a document type × field accuracy table",
         "C":"Multi-pass architecture with 50 instances per invoice; all fields required; no retry; synchronous API",
         "D":"Prompt-based JSON; all validation to humans; Batch API with one submission per day; no few-shot"},
 "expl":"""**Explanation:**

Each requirement maps to a technique:

| Requirement | Technique |
|---|---|
| Format diversity | Few-shot with `<example>` tags (Task 4.2) |
| Schema-conforming JSON | `strict: true` tool_use (Task 4.3) |
| Semantic validation | `calculated_total` + backend calculation + retry with error message (Task 4.4) |
| Cost + 36-hour commitment | Batch API; P ≤ 36 − 24 = 12 hours → submission at least every 12 hours (Task 4.5) |
| payment_terms sometimes absent | Nullable field (Task 4.3) |
| Confidence-based routing | Per-field enum confidence; calibration with the document type × field table (Task 4.6) |

- **(A) Wrong:** "no batch because there is an SLA" — 36 > 24, batch is possible; required fields create fabrication; `auto` gives no guarantee; no validation.
- **(C) Wrong:** the number of passes depends on the number of files; "50 instances per invoice" is the absence of cost intuition; required-all fabrication risk; no retry.
- **(D) Wrong:** prompt-based JSON is unreliable; one submission per day is 24 + 24 = 48 > 36 (SLA violation); leaving all validation to humans does not scale.

**Concept covered:** Task 4.1–4.6 integrated application"""},
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
("base",5,1):{"body":"""A customer support agent's first-contact resolution rate is 55%; the target is 80%. Logs show the agent escalating simple cases such as standard damage replacements with photo evidence, while attempting to resolve complex situations requiring policy exceptions on its own.

**What is the most effective way to improve escalation calibration?**""",
 "opts":{"A":"Add explicit escalation criteria with few-shot examples to the system prompt showing when to escalate and when to resolve autonomously.",
         "B":"Have the agent report a 1–10 confidence score before each response; if the score is below a threshold, automatically route the request to a human.",
         "C":"Build a separate classifier model trained on historical tickets; have it predict which requests require escalation before the main agent begins processing.",
         "D":"Measure customer frustration with sentiment analysis; auto-escalate when a negative sentiment threshold is exceeded."},
 "expl":"""**Explanation:** The exam guide's own question and rationale: the root cause is **unclear decision boundaries**; explicit criteria with few-shot examples address this directly and are the **proportionate first intervention** before adding infrastructure. Calibration is broken in both directions (simple ones escalated, complex ones handled autonomously); but examples show both boundaries.

- **(B) Wrong:** An LLM's self-reported confidence is not calibrated — the agent is already misplacing its confidence on hard cases. A threshold tries to solve a two-way problem with a one-way measure.
- **(C) Wrong:** Over-engineering — requires labeled data and ML infrastructure; prompt optimization has not yet been tried.
- **(D) Wrong:** Solves a different problem; sentiment does not correlate with case complexity.

**Concept covered:** Task 5.2 — Escalation criteria with few-shot examples, proportionality ladder"""},
("base",5,2):{"body":"""A web search subagent times out while researching a complex topic. You need to design how this error information flows to the coordinator agent.

**Which approach best enables intelligent recovery?**""",
 "opts":{"A":"Return structured error context to the coordinator including the error type, the attempted query, any partial results, and possible alternative approaches.",
         "B":"Implement automatic retry with exponential backoff inside the subagent; when all attempts are exhausted, return a generic \"search unavailable\" status to the coordinator.",
         "C":"Catch the timeout inside the subagent and return an empty result set marked as successful.",
         "D":"Propagate the timeout exception directly to a top-level handler and terminate the entire research workflow."},
 "expl":"""**Explanation:** Structured error context gives the coordinator the information it needs to decide: retry with a modified query, an alternative approach, or continue with partial results.

- **(B) Wrong:** The most tempting wrong option. Local retry (layer 1) is correct; but the generic "search unavailable" (layer 2) hides context from the coordinator — which query, what kind of error, whether partial results exist remain unknown.
- **(C) Wrong:** Silent suppression — marking the error as success blocks every form of recovery and creates the risk of incomplete research output.
- **(D) Wrong:** Unnecessarily terminates the entire workflow when recovery strategies could have worked.

**Concept covered:** Task 5.3 — Three anti-patterns, two-layer recovery"""},
("base",5,3):{"body":"""A customer support agent using a case facts block works flawlessly in single-issue conversations. A customer opens returns for two different orders and an invoice dispute in the same conversation; at turn 7, the agent responds to the invoice dispute with the refund amount of the first order.

**What is the root cause and the solution?**""",
 "opts":{"A":"The case facts block was corrupted during summarization; move the block outside the summarized history and include it in every prompt.",
         "B":"Tool results have filled the context; trim order queries to the fields needed for the return before adding them to context.",
         "C":"A single case facts block cannot represent multiple issues; build a separate context layer with a structured record per issue and an active-issue field.",
         "D":"The conversation history is not being sent in full; include all previous turns in subsequent requests."},
 "expl":"""**Explanation:** Case facts are for a single case; for multi-issue sessions the exam guide calls for "*structured issue data … into a separate context layer*". A record per issue + an active-issue field frees the agent from ambiguity about which issue it is on.

- **(A) Wrong:** The problem is not summarization of the block, it is its *structure*: a single `order_id` and a single `refund_amount` cannot represent three issues. The block is already kept outside.
- **(B) Wrong:** Tool result bloat produces a different symptom (budget exhaustion); not the mixing of issues.
- **(D) Wrong:** Even if the history is sent in full, the single-block structure cannot separate issues; a structural problem.

**Concept covered:** Task 5.1 — Multi-issue session context layer"""},
("base",5,4):{"body":"""A coordinator concatenates the research output of 7 subagents and passes it to the synthesis agent. The synthesis report handles the findings of the first two and last two subagents in detail but barely uses the findings of subagents 3–5. Each subagent output is structured and short.

**Which is the most effective fix?**""",
 "opts":{"A":"Add an instruction to the synthesis agent: \"weigh all subagent findings equally.\"",
         "B":"Redesign the subagents to return structured data instead of verbose content.",
         "C":"Reduce the number of subagents to 4; fewer inputs are processed more evenly.",
         "D":"Have the coordinator place a key-findings summary at the top of the merged input and separate each subagent output with explicit section headers."},
 "expl":"""**Explanation:** Lost-in-the-middle appears, in the exam guide's language, in "*aggregated inputs*"; the problem is in the format of the coordinator *doing the merging*. Solution: key-findings summary at the top + explicit section headers.

- **(A) Wrong:** An instruction does not change the attention mechanism; the content in the middle is still in the middle.
- **(B) Wrong:** The question already says the outputs are structured and short — upstream optimization has been done; the problem is the merge layout.
- **(C) Wrong:** Narrows the scope; with 4 subagents, the 2nd and 3rd still end up in the middle.

**Concept covered:** Task 5.1 — Lost in the middle (aggregated inputs)"""},
("base",5,5):{"body":"""A research coordinator receives `{"status": "success", "results": []}` from the document analysis subagent. Logs show the same query returned 9 results an hour earlier and that the document store was under maintenance at the time. The coordinator reported "no documents on this topic."

**What is the root cause?**""",
 "opts":{"A":"The coordinator should have retried the query once more upon seeing the empty result; empty results are always retried.",
         "B":"The subagent's response schema does not distinguish an access failure from a valid empty result; the maintenance outage propagated as \"success + empty array.\"",
         "C":"The coordinator should have sent the same query to a second subagent to verify the result.",
         "D":"The document store's maintenance is an external event; there is nothing the coordinator can do."},
 "expl":"""**Explanation:** If the same JSON shape describes two different realities (unreachable / no match), the schema is broken. The exam guide wants the distinction "*in error reporting*": `source_reached` / `failure_type` fields. The maintenance outage propagated as silent suppression.

- **(A) Wrong:** "Always retry empty results" is the reverse mistake: it re-queries valid empty results over and over. The retry decision requires *knowing* the access status; the schema doesn't provide it.
- **(C) Wrong:** A second subagent returns the same answer with the same broken schema.
- **(D) Wrong:** The outage is an external event, but its *staying silent* is the system's fault; had a structured error arrived, the coordinator could have waited and retried or added a coverage note.

**Concept covered:** Task 5.3 — Access failure vs valid empty result, distinction in the response schema"""},
("base",5,6):{"body":"""An architect notices that an agent doing codebase exploration drifts toward "typical patterns" in long sessions and explains to the team: "When the context window fills up, the oldest messages get dropped, so we should switch to a model with a larger window."

**What is the assessment of this explanation and recommendation?**""",
 "opts":{"A":"Explanation correct, recommendation correct: as the window grows, fewer messages are dropped and degradation is delayed.",
         "B":"Explanation wrong: the API does not drop messages; it returns an error if the limit is exceeded, and Claude Code summarizes. Degradation arises from attention budget dilution before the limit (context rot) and from summary loss after compaction; enlarging the window does not fix attention quality.",
         "C":"Explanation correct, recommendation wrong: messages do get dropped, but the solution is to run `/compact` more often.",
         "D":"Explanation wrong: the cause of degradation is the model forgetting the instruction; adding \"be specific\" to the system prompt is enough."},
 "expl":"""**Explanation:** The Messages API does not drop messages; it returns an error if the limit is exceeded; Claude Code auto-compacts as it nears the limit. Degradation arises through two mechanisms: context rot (attention budget) before the limit, summary loss after compaction. In the rationale for Q12: "*larger context windows don't solve attention quality issues*".

- **(A) Wrong:** Both the explanation and the recommendation are wrong; enlarging the window makes you experience the same context pollution over a wider area.
- **(C) Wrong:** The explanation is still wrong; more frequent compaction without a focus instruction and a scratchpad increases summary loss.
- **(D) Wrong:** The problem is not the instruction, it is attention and summarization; "be specific" does not bring back inaccessible information.

**Concept covered:** Task 5.4 — Context degradation mechanism, the large-window distractor"""},
("base",5,7):{"body":"""In a 3-hour exploration session with Claude Code, a context-full warning appears. The findings exist only inside the conversation. The developer will continue the same work. The team is debating two proposals: (1) write the findings to CLAUDE.md and run `/clear`, (2) have the findings written to NOTES.md and run `/compact` with a focus instruction.

**Which is correct and why?**""",
 "opts":{"A":"(1): CLAUDE.md is loaded automatically in every session, the findings are never lost; `/clear` gives the cleanest context.",
         "B":"Both are wrong: the correct solution is to disable auto-compact and continue until the window is full.",
         "C":"(2): NOTES.md is the session's working memory, whereas CLAUDE.md is the persistent instruction file — writing findings there bloats every session; `/compact <focus>` summarizes the narrative while preserving critical findings, whereas `/clear` resets without summarizing.",
         "D":"Both are correct: the file choice and the command choice are matters of preference."},
 "expl":"""**Explanation:** The scratchpad (NOTES.md) is the session's working memory, CLAUDE.md is the project's persistent instruction file (Domain 3.1); if exploration findings are written to CLAUDE.md, they bloat every session and pollute unrelated sessions. `/compact <focus>` summarizes the narrative while continuing the same work and preserves critical findings; `/clear` does not summarize, it resets — used when switching to unrelated work.

- **(A) Wrong:** CLAUDE.md's "never lost" property is precisely the problem; `/clear` throws away the context entirely for work that will continue.
- **(B) Wrong:** Disabling auto-compact means getting an error when you hit the limit.
- **(D) Wrong:** The file choice (session memory vs persistent instruction) and the command choice (summarize vs reset) are not preferences but semantic differences.

**Concept covered:** Task 5.4 — Scratchpad vs CLAUDE.md, `/compact` vs `/clear`"""},
("base",5,8):{"body":"""An extraction system running with calibrated field-level confidence auto-accepts fields above 92%, and the quality team manually checks a plain random sample of 50 extractions per week. After two months, two problems surface: (1) on a new vendor's invoice template, the model extracts a wrong due date with high confidence; because its volume is low, it never appeared in the 50-item sample; (2) invoices where the line-item sum does not match the grand total on the document passed with 95% model confidence.

**Which design solves both problems together?**""",
 "opts":{"A":"Split sampling into document type × field × confidence band strata (a minimum number of samples per stratum, including from high confidence); add a second signal to routing: if document validation finds a conflict (`conflict_detected`), send to human review regardless of confidence.",
         "B":"Raise the weekly sample to 200 and raise the auto-accept threshold to 98%.",
         "C":"Route the new vendor's invoices to human review and add a \"check the totals\" instruction to the model.",
         "D":"Ask for the confidence score as an enum and send everything other than `high` to a human."},
 "expl":"""**Explanation:** Two problems, two mechanisms. (1) Plain random sampling does not represent the low-volume type — the aggregate metrics trap repeats itself in sampling; stratified sampling (document type × field × confidence band, including from high confidence) catches the novel error pattern. (2) The model can pick a value with high confidence without noticing the contradictory document; the exam guide sends low confidence **or** a contradictory/ambiguous source document to a human — `conflict_detected` is the second door.

- **(B) Wrong:** A larger plain sample still sees the low-volume type rarely; raising the threshold does not measure document inconsistency.
- **(C) Wrong:** Vendor-specific routing patches the symptom (it won't catch the next new template); the sum check is deterministic validation, not left to the model.
- **(D) Wrong:** A change in representation does not change calibration; sending everything other than `high` to humans chokes capacity, and the contradictory document still passes with `high`.

**Concept covered:** Task 5.5 — Stratified sampling, two routing signals"""},
("base",5,9):{"body":"""The document analysis subagent finds different growth rates in two reliable reports (45% and 38%, different methodologies). The system designer is debating three options.

**Which one conforms to the exam guide's role distribution?**""",
 "opts":{"A":"Have the subagent evaluate the methodology and return the single value it finds more reliable; the coordinator and synthesis proceed with that value.",
         "B":"Have the subagent return the mean and standard deviation of the two values; have the report write it as a range.",
         "C":"Have the subagent return both values; have the synthesis agent pick the more recent one and write a single figure, noting the other in a footnote.",
         "D":"Have the subagent annotate both values with source, date, characterization and methodology note and complete the analysis; have the coordinator make the reconciliation decision; have synthesis show both in the \"contested findings\" section of the report with their sources."},
 "expl":"""**Explanation:** The exam guide's role distribution: the document analysis subagent annotates the conflicting values and *completes* the analysis; the **coordinator** makes the reconciliation decision before synthesis; synthesis shows both with their sources in the report under the "well-established / contested" distinction.

- **(A) Wrong:** The subagent returning a single value based on its "more reliable" judgment is an arbitrary choice; it hides information from the upper layers.
- **(B) Wrong:** A mean/range produces a number no source has stated; it makes the methodology difference invisible.
- **(C) Wrong:** "More recent" is also an arbitrary rule (valid only for revisions), and the synthesis agent is not the reconciliation layer.

**Concept covered:** Task 5.6 — Conflict handling, role distribution, report skeleton"""},
("base",5,10):{"body":"""A company operates a multi-agent system that includes customer support + research + document extraction. Five problems are reported:

1. When escalated to a representative, the customer has to explain the order number and their request from scratch
2. Simple damage replacements are escalated, while requests past the warranty period are approved by the agent
3. The research subagent retries with backoff on timeout, then returns "source unavailable"; the coordinator cannot try an alternative source
4. The synthesis report writes the figure the IEA called a "preliminary estimate" as if it were a definitive measurement
5. In an extraction system reporting 97% aggregate accuracy, a low-volume document type never appears in the weekly plain random sample

**Which option matches the five problems with the correct concept?**""",
 "opts":{"A":"1. Summarize the conversation history; 2. Lower the sentiment threshold; 3. Increase the retry count; 4. A \"cite sources\" instruction to the synthesis agent; 5. Increase the sample size",
         "B":"1. Case facts handoff context in the `escalate_to_human` call; 2. Explicit escalation criteria with few-shot examples (two-way calibration); 3. Structured error context instead of a generic status (retry is right, the message is wrong); 4. Preserve the source's characterization in the claim-source mapping; 5. Document type × field × confidence band stratified sampling",
         "C":"1. Larger context window; 2. Train a separate escalation classifier; 3. Halt the workflow on timeout, request human intervention; 4. Have a post-synthesis verification agent search for sources; 5. Raise the auto-accept threshold to 99%",
         "D":"1. Remove escalation, let the agent resolve everything; 2. Escalation based on the model's confidence score; 3. Have the subagent catch the error and return an empty result; 4. Remove the figure from the report; 5. Remove the low-volume type from the pipeline"},
 "expl":"""**Explanation:** Each problem matches a different Domain 5 concept:

| Problem | Concept | Solution |
|---|---|---|
| 1. Explaining from scratch on escalation | Task 5.2 + 5.1 — Handoff context | `escalate_to_human` + case facts |
| 2. Simple ones escalated, exceptions approved | Task 5.2 — Two-way calibration (Q3) | Explicit criteria with few-shot examples |
| 3. Generic status after retry | Task 5.3 — Anti-pattern 3 (Q8-B) | Structured error context |
| 4. "Preliminary estimate" → definitive measurement | Task 5.6 — Source characterization | `source_characterization` in the claim-source mapping |
| 5. Low-volume type absent from the sample | Task 5.5 — Stratified sampling | Document type × field × confidence band |

- **(A) Wrong:** Every solution is superficial: summarization does not provide handoff context; a sentiment threshold does not fix calibration; the retry count does not solve the generic message; an instruction does not create the characterization; a larger plain sample still misses the low-volume type.
- **(C) Wrong:** Disproportionate/wrong: a large window is unrelated to handoff; a classifier is over-engineering before the prompt has been tried; halting the workflow is an anti-pattern; searching for sources afterward does not bring back the characterization; a 99% threshold does not solve the stratum problem.
- **(D) Wrong:** Extreme solutions: removing escalation is a policy violation; the confidence score is an unreliable trigger; returning an empty result is silent suppression; removing the figure is information loss; removing the type is data loss.

**Concept covered:** Task 5.1–5.6 integrated application"""},
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
