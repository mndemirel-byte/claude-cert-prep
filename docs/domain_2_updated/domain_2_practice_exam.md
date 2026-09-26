# Domain 2 — Practice Exam

## Tool Design & MCP Integration (18% of the exam)

**Distribution (10 questions):**
- 2 questions → Tool interface design, misrouting, splitting/consolidation (2.1)
- 2 questions → Structured error responses (2.2)
- 2 questions → Tool distribution and tool_choice (2.3)
- 2 questions → MCP server integration (2.4)
- 2 questions → Built-in tools (2.5)

**Passing criterion:** 8+/10

**Scoring:**

| Score | Assessment |
|---|---|
| 10/10 | Domain ready — move to the next domain |
| 8–9/10 | Pass — re-read the task statement of each missed question |
| 6–7/10 | Borderline — restudy the relevant lesson notes, retake the exam |
| ≤5/10 | Restudy the domain from the start |

---

## Question 1 (Task Statement 2.1)

> A customer-support agent has 3 tools:
>
> - `get_account_info`: "Retrieves account information"
> - `get_billing_info`: "Retrieves billing information"
> - `get_subscription_info`: "Retrieves subscription information"
>
> Users complain: when they say "I want to upgrade my subscription" the agent calls `get_account_info`; billing queries go to `get_subscription_info`. Overall misrouting rate is 30%.
>
> **What should be done as the first step?**
>
> **A)** Merge the three tools into a single `get_customer_data` tool — Claude can't err with one tool.
>
> **B)** Add few-shot examples to the system prompt: "use get_billing_info for billing questions, get_subscription_info for subscription questions".
>
> **C)** Expand each tool's description — state explicitly which data fields it returns, which query types it serves, and how it differs from the other tools; sharpen the names if needed (`get_billing_history`, `get_subscription_plan`).
>
> **D)** Add an intent classifier before Claude — it analyzes the query and routes to the right tool.

### Correct Answer: C

**Why C is correct:** The root cause is vague descriptions — all three follow the "retrieves X information" format, and Claude can't differentiate. Expanding the descriptions (which fields it returns, which queries it serves, how it differs) and renaming if needed is a low-effort, high-leverage fix; it applies two exam-guide Skills together ("writing descriptions that clearly differentiate" + "renaming tools and updating descriptions").

**Why A is wrong:** Merging doesn't remove the ambiguity, it moves it into the tool — now the tool has to guess which data to return. Three different output contracts don't fit one tool; separation of concerns breaks.

**Why B is wrong:** Few-shot examples add token cost and treat the symptom, not the root cause. Prompt-based guidance is probabilistic; while descriptions are vague it won't provide a reliable fix.

**Why D is wrong:** An intent classifier is over-engineering for a first step. You haven't tried the simple fix (improving descriptions). A classifier adds complexity and maintenance cost.

---

## Question 2 (Task Statement 2.1)

> An agent has an `analyze_document` tool. In a single call it summarizes the document (output: plain text), extracts key data (output: list of JSON records) and verifies claims (output: supported/unsupported + evidence per claim). The three operations also have different input requirements: verification needs a list of claims, summarization doesn't. The agent sometimes runs unnecessary verification when only a summary is wanted, and sometimes returns only a summary when verification is wanted.
>
> **What are the root cause and the fix?**
>
> **A)** The tool's description is insufficient — write a more detailed description.
>
> **B)** The tool combines three different purposes and three different input/output contracts in one interface — split it into purpose-specific tools: `summarize_content`, `extract_data_points` and `verify_claim_against_source`.
>
> **C)** Add "only perform the requested operation" to the system prompt.
>
> **D)** Add an `operation_type` field to the tool's input parameters — Claude specifies which operation it wants.

### Correct Answer: B

**Why B is correct:** The splitting criterion is not "how many operations" but "how many distinct purposes and output contracts". Here there are three different output schemas and different input requirements — one tool can't offer them under a coherent contract. Splitting into purpose-specific tools defines each tool precisely for one job with a defined input/output contract. Exam-guide Skill: "Splitting generic tools into purpose-specific tools with defined input/output contracts."

**Why A is wrong:** Improving the description clarifies *when* Claude calls the tool, but doesn't change *what the tool returns* — it still does all three jobs and the output schema stays ambiguous.

**Why C is wrong:** A prompt instruction is probabilistic. "Only perform the requested operation" doesn't change the tool's do-all-three structure — this is an interface problem, not a prompt problem.

**Why D is wrong:** An `operation_type` parameter selects the operation but doesn't fix the output contract — the tool returns three different schemas depending on `operation_type`, and Claude can't infer from the description which schema to expect; the `claims` parameter needed for verification is meaningless for the other operations. If these were steps of one workflow (see the `schedule_event` consolidation example) a single tool would be defensible; here there are three separate purposes.

---

## Question 3 (Task Statement 2.2)

> An agent is attempting an international money transfer. The MCP tool returns:
>
> ```json
> {
>   "isError": true,
>   "content": [{ "type": "text", "text": "{\"errorCategory\":\"business\",\"isRetryable\":false,\"description\":\"Transfer amount ($15,000) exceeds the daily limit ($10,000).\",\"customerMessage\":\"Your daily transfer limit is $10,000. Contact your account manager for higher limits.\"}" }]
> }
> ```
>
> **What should the agent do?**
>
> **A)** Wait 5 seconds and retry — it may be a transient error.
>
> **B)** Automatically reduce the transfer amount to $10,000 and retry.
>
> **C)** Not retry. Relay the `customerMessage` information to the customer and offer an alternative path (referral to the account manager).
>
> **D)** Fix the input and retry — it may be a validation error.

### Correct Answer: C

**Why C is correct:** `errorCategory: "business"` and `isRetryable: false` — this is a business-rule violation; retrying is WRONG. Until the policy changes, the same operation fails every time. The agent should relay the `customerMessage` to the customer and offer an alternative path.

**Why A is wrong:** This is not a transient error — it's a business-rule error. Waiting doesn't change policy. `isRetryable: false` explicitly rejects a retry.

**Why B is wrong:** Changing the amount automatically overrides the customer's request. That business decision belongs to the customer; the agent must not reduce it to $10,000 on its own.

**Why D is wrong:** This is not a validation error — the format is right, the amount is a valid number. The problem is a business rule: the daily limit is exceeded. `errorCategory: "business"` states this explicitly.

---

## Question 4 (Task Statement 2.2)

> You are writing your own MCP server. The `lookup_order` tool throws a `-32602 Invalid params` JSON-RPC protocol error when the order number isn't in the database, and returns an empty result with `content: []` when the database connection drops. In production, the agent keeps saying "an error occurred" for non-existent order numbers, and during a database outage tells the customer "your order was not found".
>
> **What are the root cause and the correct design?**
>
> **A)** Increase the retry count — database outages are solved by retries.
>
> **B)** Both situations are reported through the wrong channel. "Order not found" is a valid empty result → `isError: false` + `resultCount: 0`. A dropped database connection is a tool execution error → `isError: true` + `errorCategory: "transient"`, `isRetryable: true`. Protocol errors should be used only for unknown tools / arguments that violate the schema.
>
> **C)** Throw a protocol error in both cases — so the client behaves consistently.
>
> **D)** Add "say 'order not found' instead of 'an error occurred'" to the system prompt.

### Correct Answer: B

**Why B is correct:** MCP defines two error mechanisms: a protocol error (JSON-RPC `error`) does **not** reach the model — it stays in the client layer; a tool execution error (`isError: true`) reaches the model, which can self-correct. A non-existent order isn't even an error — a successful query with zero matches (`isError: false`). A dropped database connection is a real access failure; `isError: true` + transient/retryable metadata lets the agent make a retry decision. The current design encodes both situations backwards.

**Why A is wrong:** Retries don't change an empty result (non-existent order), and the agent won't recognize an outage returned as an empty array as an error in the first place, so it won't retry. The problem isn't the retry count; it's the signal structure.

**Why C is wrong:** A protocol error doesn't reach the model — Claude can't see what went wrong, can't fix the input, can't look for an alternative path. Business/API/validation errors must be returned *as results* with `isError: true`.

**Why D is wrong:** The prompt doesn't know what the tool returns in which situation; it can't tell the two apart. A structural problem needs a structural fix.

---

## Question 5 (Task Statement 2.3)

> A research agent has been given 16 tools: 5 web-search tools, 4 document-analysis tools, 3 database-query tools, 2 email tools and 2 calendar tools. The agent frequently picks the wrong tool and struggles to complete tasks.
>
> At the same time, although metadata extraction is a mandatory first step, the agent sometimes skips it and goes straight to analysis.
>
> **Which approach fixes both problems at once?**
>
> **A)** Expand all tool descriptions and add "always extract metadata first" to the system prompt.
>
> **B)** Distribute the tools across role-specific agents (4–5 tools each) and enforce the mandatory first step with `tool_choice: {"type": "tool", "name": "extract_metadata"}` on the first request; switch `tool_choice` back to `auto` on subsequent turns.
>
> **C)** Distribute the tools across role-specific agents and use `tool_choice: {"type": "tool", "name": "extract_metadata"}` on all turns — so the step is never skipped.
>
> **D)** Create a single "do_everything" tool and run all operations through it.

### Correct Answer: B

**Why B is correct:** It fixes both problems:
1. **Tool overload:** 16 tools → distribute across role-specific agents (4–5 each). Selection reliability rises.
2. **Mandatory first step:** forced `tool_choice` on the first request makes metadata extraction deterministic; the model can't skip it. Switching to `auto` on later turns lets the model proceed to analysis — exam guide: "ensure a specific tool is called first, then processing subsequent steps in follow-up turns."

**Why A is wrong:** Two-part, but both parts probabilistic. Expanding descriptions partially improves a 16-tool selection problem but doesn't fix the root cause (too many tools). The system-prompt instruction "always extract metadata" isn't a 100% guarantee. Mandatory steps need a deterministic mechanism (tool_choice).

**Why C is wrong:** The distribution part is right, but `tool_choice` is per request; left forced on every turn, the model is forced to call `extract_metadata` **on every turn** and never reaches analysis — an infinite metadata loop. Forced selection only on the first turn; then `auto`.

**Why D is wrong:** A single "do_everything" tool is the exact opposite of tool splitting. Piling all complexity into one tool makes it impossible for Claude to specify what it wants.

---

## Question 6 (Task Statement 2.3)

> In a document-processing pipeline Claude has three tools: `classify_invoice`, `classify_receipt`, `classify_contract` — each returns a different JSON schema. The pipeline parses Claude's response directly with `json.loads`. In production Claude sometimes returns text like "This document looks like an invoice, would you like me to classify it?" instead of calling a tool, and the pipeline crashes. For some documents Claude also calls two classification tools in a single response.
>
> **Which configuration fixes both problems?**
>
> **A)** `tool_choice: {"type": "auto"}` + "always call a tool" in the system prompt.
>
> **B)** `tool_choice: {"type": "any"}` + `disable_parallel_tool_use: true` — the model must call one of the three tools, exactly one.
>
> **C)** `tool_choice: {"type": "tool", "name": "classify_invoice"}` — most documents are invoices.
>
> **D)** `tool_choice: {"type": "none"}` + parse the output with a regex.

### Correct Answer: B

**Why B is correct:** `any` guarantees the model **must** call a tool instead of returning text; which one is left to the model — one of the three schemas is certain to arrive. Exam-guide Skill: "Setting tool_choice: 'any' to guarantee the model calls a tool rather than returning conversational text." `disable_parallel_tool_use: true` prevents multiple `tool_use` blocks in one response; with `any` it yields the guarantee of "exactly one tool call".

**Why A is wrong:** `auto` leaves the model free to return text; a prompt instruction is probabilistic. A guarantee of "always call a tool" needs deterministic `tool_choice`.

**Why C is wrong:** Forcing one tool classifies receipts and contracts with the invoice schema too — wrong schema, wrong data. The choice should be left to the model while the obligation to call is enforced: that is the definition of `any`.

**Why D is wrong:** `none` switches tool use off entirely — the opposite direction. Parsing free text with a regex throws away the structured-output guarantee.

---

## Question 7 (Task Statement 2.4)

> A team is starting a new project. An MCP server will be configured for GitHub integration. A developer proposes this `.mcp.json`:
>
> ```json
> {
>   "mcpServers": {
>     "github": {
>       "type": "stdio",
>       "command": "github-mcp-server",
>       "env": {
>         "GITHUB_TOKEN": "ghp_abc123def456ghi789"
>       }
>     }
>   }
> }
> ```
>
> **What is the security problem in this configuration?**
>
> **A)** Move the token to `.claude/settings.json` — MCP credentials belong in the settings file.
>
> **B)** The GitHub token is written directly into `.mcp.json`. Since this file is under version control, the token will enter the repo. The token should be referenced as the `${GITHUB_TOKEN}` environment variable; each developer defines their own token in their local environment.
>
> **C)** `~/.claude.json` should be used instead of `.mcp.json` — MCP configuration should always be at user level.
>
> **D)** The token is too short — generate a stronger one.

### Correct Answer: B

**Why B is correct:** `.mcp.json` is under version control — tracked by Git and pushed to the repo. A token written directly into it is visible to everyone. Fix: the `${GITHUB_TOKEN}` environment-variable syntax (with a default via `${GITHUB_TOKEN:-}` if needed). Each developer sets their own token locally; tokens never enter the repo. Exam guide: "Environment variable expansion in .mcp.json for credential management without committing secrets."

**Why A is wrong:** `.claude/settings.json` is also a shared, version-controlled project file (Domain 3.1) — the token still enters the repo. Changing files relocates the problem rather than solving it; settings.json also isn't the right place for MCP server definitions.

**Why C is wrong:** `.mcp.json` (project) and `~/.claude.json` (user/local) serve different purposes. The team's shared tool configuration is information that should be shared — `.mcp.json` is the right place. The problem isn't the file's location; it's the hardcoded token.

**Why D is wrong:** The token's length or strength isn't the security problem here. Even the strongest token is compromised once it enters the repo.

---

## Question 8 (Task Statement 2.4)

> The team set up an MCP server that performs semantic search over the codebase (`mcp__codesearch__search`). The server does language-aware symbol resolution, cross-repo search and relevance ranking. The tool's description: "Searches code." Observation: Claude Code almost never calls this tool; it always uses the built-in `Grep` for code search and finds nothing on multi-repo queries.
>
> **What is the most effective first step?**
>
> **A)** Disable `Grep` via `disallowedTools` — so Claude is forced to use the MCP tool.
>
> **B)** Enrich the MCP tool's description: state its capabilities (symbol resolution, cross-repo, relevance ranking), what it returns (file + line + symbol kind + score), and when it should be preferred over the built-in `Grep`.
>
> **C)** Move the server to `~/.claude.json` — user-scope servers take precedence.
>
> **D)** Write "always use mcp__codesearch__search for code search" in CLAUDE.md.

### Correct Answer: B

**Why B is correct:** The built-in `Grep`'s description is long, detailed and familiar; if the MCP tool says "Searches code", Claude picks the built-in tool that looks richer — even though the MCP tool is actually more capable. Exam-guide Skill: "Enhancing MCP tool descriptions to explain capabilities and outputs in detail, preventing the agent from preferring built-in tools over more capable MCP tools." Domain 2.1's description principles applied to MCP; low effort, root cause.

**Why A is wrong:** Disabling Grep forces Claude onto the heavy MCP tool even for single-repo, simple pattern searches; it suppresses the symptom by force without improving selection quality. And if the MCP server goes down, search capability is lost entirely.

**Why C is wrong:** Scope precedence (local > project > user) applies to conflicts between servers with the same *name*; it does not affect tool *selection*. Where the server is defined has nothing to do with which tool Claude prefers.

**Why D is wrong:** A CLAUDE.md instruction is probabilistic, and "always" forces MCP even for simple searches. The root cause is the weak description; fix that first. (After the description is fixed, a hint like "prefer codesearch for multi-repo searches" in CLAUDE.md could be considered as a supplement — not the first step.)

---

## Question 9 (Task Statement 2.5)

> A developer is working in a large codebase. They need to:
>
> 1. Find all files that call the `fetchUserData` function
> 2. Find all `.config.yml` files in the project
> 3. Run the test suite after changing the found files
>
> **Which tool is correct for each task?**
>
> **A)** 1: Grep, 2: Grep, 3: Grep — Grep handles every kind of search; check test output with Grep.
>
> **B)** 1: Glob (`**/*fetchUserData*`), 2: Grep (`.config.yml` pattern), 3: Bash.
>
> **C)** 1: Grep (`fetchUserData` — searches file contents), 2: Glob (`**/*.config.yml` — matches file paths), 3: Bash (`npm test`).
>
> **D)** 1: Read (read all files, filter), 2: Glob, 3: Edit.

### Correct Answer: C

**Why C is correct:** Each tool in its area of strength: Grep for content search (function calls live *inside* files), Glob for path matching (the extension is in the file *name*), Bash for running commands (the test suite — the one job no built-in tool can do).

**Why A is wrong:** Grep searches file contents — finding `.config.yml` files requires path matching (Glob). And Grep can't run commands; tests need Bash.

**Why B is wrong:** 1 and 2 are mapped backwards. Glob searches file paths — if `fetchUserData` isn't in a file name it returns nothing. Function calls are in file contents: Grep. The Bash part is right.

**Why D is wrong:** Reading all files with Read is a context-budget killer; Grep does the job in one pass. Edit changes files, it doesn't run tests — step 3 needs Bash.

---

## Question 10 (Task Statement 2.5)

> In Claude Code you want to change the line `timeout: 30` to `timeout: 60` in `config.ts`. The Edit tool returns: "old_string `timeout: 30` appears in 4 places in the file — match is not unique." All four are in different service blocks and you want to change only the one in the `paymentService` block.
>
> **Which approach is correct?**
>
> **A)** Re-run Edit with `replace_all: true` — all four lines get updated.
>
> **B)** Widen `old_string` with surrounding lines (`paymentService: {\n  retries: 3,\n  timeout: 30`) so it matches only that block; if that still fails, load the file with Read and write the modified version with Write.
>
> **C)** Run `sed -i 's/timeout: 30/timeout: 60/' config.ts` with Bash.
>
> **D)** Write the file from scratch with Write — no need for Read, the content is already known.

### Correct Answer: B

**Why B is correct:** On Edit's uniqueness error the first step is the cheapest: add context to `old_string` so it matches one place. If that doesn't work, the exam guide's fallback kicks in: "When Edit fails due to non-unique text matches, using Read + Write as a fallback." The Read → Write order is mandatory — Claude Code refuses Write to an existing file that hasn't been read.

**Why A is wrong:** `replace_all` changes all four lines; the scenario wants only the `paymentService` block. `replace_all` is for "when you want every occurrence changed" (like renaming a variable), not for selective edits.

**Why C is wrong:** `sed` also changes all four lines (the same selectivity problem) and throws away Edit's uniqueness guarantee and readable diff; permission stays at the `Bash` level. Falling back to Bash when a built-in tool exists is wrong.

**Why D is wrong:** Write clobbers the whole file; without a Read, Claude Code refuses to write to an existing file, and Claude could lose content it hasn't seen. "The content is already known" is a dangerous assumption made without knowing the file's latest state.

---

## Question → Task Statement Mapping

| Question | Task Statement | Concept tested |
|---|---|---|
| 1 | 2.1 | Misrouting — description expansion + renaming, first-step principle |
| 2 | 2.1 | Splitting criterion — distinct purpose + distinct output contract |
| 3 | 2.2 | Business error — `isRetryable: false`, `customerMessage`, no retry |
| 4 | 2.2 | Protocol error vs `isError`; access failure vs valid empty result |
| 5 | 2.3 | Tool overload; forced `tool_choice` → `auto` on the next turn |
| 6 | 2.3 | Guaranteed structured output with `any`; `disable_parallel_tool_use` |
| 7 | 2.4 | `.mcp.json` + `${VAR}` — keeping credentials out of the repo; scope distinction |
| 8 | 2.4 | Enhancing MCP tool descriptions — the built-in-preference problem |
| 9 | 2.5 | Grep (content) vs Glob (path) vs Bash (command) |
| 10 | 2.5 | Edit uniqueness failure → widen context → Read + Write; when `replace_all` |
