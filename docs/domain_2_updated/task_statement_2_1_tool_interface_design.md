# Task Statement 2.1: Tool Interface Design

## Domain 2 — Tool Design & MCP Integration (18% of the exam)

---

## Core Idea

When Claude runs as an agent, it has access to **tools** — functions such as querying a database, fetching customer data, sending an email, or calling an API. You define these tools and hand them to Claude through the API.

The critical point: **Claude decides which tool to call primarily by reading the tool's description.** The description is the **primary** mechanism for tool selection — but not the only one. The tool's **name**, its parameter names, and the parameter descriptions inside `input_schema` also influence selection. That is why the exam guide says "**renaming** tools and updating descriptions"; Anthropic's own measurements show naming and namespacing (`asana_search` vs `jira_search`) have a non-trivial effect on tool-use evaluations.

Think of it this way: you are in a dim room with 6 buttons. Each has a short label (the tool name), and someone reads you a few sentences describing each one. If the labels look alike **and** the descriptions are vague, you will sometimes press the wrong button.

That is exactly Claude's situation with poorly designed tool interfaces.

---

## Anatomy of a Tool Definition

In the Messages API a tool has three parts:

```json
{
  "name": "get_customer",
  "description": "Retrieves customer profile data (name, email, account tier, preferences) by customer ID or email address. Use for identity-focused queries such as 'who is this customer' or 'what plan are they on'. Do NOT use for order-related queries — use lookup_order instead. Does not return order history or billing information.",
  "input_schema": {
    "type": "object",
    "properties": {
      "customer_id": {
        "type": "string",
        "description": "Customer identifier, 'CUST-' prefix + 6 digits (e.g. CUST-004512). Use the email field if only the email is known."
      },
      "email": {
        "type": "string",
        "description": "The customer's registered email address. Used when customer_id is not provided."
      }
    },
    "required": []
  }
}
```

| Part | Role | Design rule |
|---|---|---|
| `name` | Short, distinctive identifier. Regex: `^[a-zA-Z0-9_-]{1,128}$` | Verb + object (`lookup_order`, `search_support_tickets`); namespace similar tools with prefixes/suffixes (`jira_search`, `asana_search`) |
| `description` | The text Claude reads to decide "when this tool" | **At least 3–4 sentences**, more for complex tools (official Anthropic guidance) |
| `input_schema` | JSON Schema — parameters, types, required fields | A `description` on every parameter; `enum` for bounded value sets; unambiguous names (`user_id`, not `user`) |

MCP uses the same structure under the name `inputSchema` (camelCase); the concept is identical.

---

## What a Good Tool Description Contains

Five essential components:

1. **What the tool does** — its primary purpose, stated plainly
2. **What inputs it expects** — formats, types, constraints
3. **Example queries it handles well** — concrete usage scenarios
4. **Edge cases and limitations** — what it does NOT do, what it does NOT return
5. **Explicit boundaries** — WHEN to use it versus similar tools, and when not to

### Poor Description

```
get_customer: "Retrieves customer information."
```

### Good Description

```
get_customer: "Retrieves customer profile data (name, email, account tier,
preferences) by customer ID or email address. Use for identity-focused queries
such as 'who is this customer' or 'what plan are they on'. Do NOT use for
order-related queries — use lookup_order instead. Does not return order
history or billing information."
```

The difference: the second tells Claude exactly when to pick this tool, when NOT to, and **what it will not get back**.

### Anthropic's official example

The good/poor pair from the official docs:

- ❌ `"Gets the stock price for a ticker."`
- ✅ `"Retrieves the current stock price for a given ticker symbol. The ticker symbol must be a valid symbol for a publicly traded company on a major US stock exchange like NYSE or NASDAQ. The tool will return the latest trade price in USD. It should be used when the user asks about the current or most recent price of a specific stock. It will not provide any other information about the stock or company."`

Four sentences: what it does, input constraint, what it returns, when to use it, what it does not return.

---

## The Misrouting Problem — Exam Favorite

The exam's favorite scenario: two tools with similar names and descriptions, and Claude keeps picking the wrong one.

The exam guide's own example: `analyze_content` vs `analyze_document` with near-identical descriptions. The official sample question (Q2): `get_customer` ("Retrieves customer information") vs `lookup_order` ("Retrieves order details").

### Example Scenario

- `get_customer`: "Retrieves customer information"
- `lookup_order`: "Retrieves order details"

User: *"Check the status of order #12345."*

Claude picks `get_customer`. Why? Both descriptions say "retrieves … information", both accept similar identifier formats. The descriptions are too vague for Claude to differentiate.

### Candidate Fixes and Their Evaluation

| Fix | Verdict | Why |
|---|---|---|
| **Expand tool descriptions** (input formats, example queries, edge cases, "use X instead of Y") | **✅ Correct first step** | Low effort, high leverage. Addresses the root cause directly. |
| **Rename tools + update descriptions** | **✅ Same category** | Exam guide Skill: "Renaming tools and updating descriptions to eliminate functional overlap." Done together with description expansion; not a competing option. |
| Add few-shot examples to the system prompt | ❌ Wrong | Adds token cost instead of fixing the description problem. Treats the symptom. |
| Add a routing classifier before Claude | ❌ Wrong | Over-engineering for a first step. You haven't tried the simple fix yet. |
| Consolidate into a single `lookup_entity` tool | ❌ Wrong | Moves the ambiguity from Claude into the tool; it doesn't disappear, it relocates. Breaks separation of concerns. |

> **Exam principle: The exam prefers low-effort, high-leverage fixes as the first step.** Better descriptions (and names) before a classifier. Always.

---

## Tool Splitting vs Tool Consolidation

### Splitting

A tool is too broad. A single `analyze_document` tool summarizes, extracts data, AND verifies claims — three different purposes, three different output schemas.

**Fix: split into purpose-specific tools**

- `extract_data_points` — pulls structured data from the document (output: list of JSON records)
- `summarize_content` — produces a summary (output: text)
- `verify_claim_against_source` — checks whether a specific claim is supported by the source (output: supported/unsupported + evidence)

Each tool does one job, precisely described, with a **defined input/output contract**.

### Consolidation — the opposite pole

Splitting is not always right. Anthropic's "Writing tools for agents" guide warns about the opposite failure: many small tools that mirror API endpoints one-to-one (`list_users`, `list_events`, `create_event`) perform worse than a single tool covering the workflow a human would perform (`schedule_event`).

**The splitting criterion is not "how many operations" but "how many distinct purposes and output contracts":**

| Situation | Decision |
|---|---|
| Three operations, three different output schemas, triggered by different query types (`analyze_document`) | **Split** |
| Three API calls but one workflow, one result (`schedule_event`) | **Consolidate** |
| Two tools, same data source, only the descriptions are vague | **Neither — fix the descriptions** |

---

## Designing the Tool's Output

The exam guide says "expected inputs, **outputs**" — interface design is not only the input side. Whatever the tool returns is what Claude reasons with.

- **Return meaningful context:** `user: "Ayşe Yılmaz (a8f3-…)"` instead of `user_id: "a8f3-…"`. Anthropic's measurement: resolving UUIDs to meaningful names significantly improves Claude's precision.
- **A `response_format` parameter:** `concise` (default, only the essential fields) / `detailed` (all fields). The agent chooses according to its need.
- **Pagination, filtering, truncation:** Claude Code truncates MCP tool output at 25,000 tokens by default. Offer pagination (`page`, `limit`), range selection, and a hint in truncated responses ("try a narrower query").
- **State what it does not return:** negative boundaries like "does not return order history" prevent Claude from calling the tool with wrong expectations.

---

## System Prompt Conflicts — The Sneaky Trap

Even if your tool descriptions are perfect, **keyword-sensitive instructions in the system prompt can override them.**

Example: if the system prompt says "whenever the user mentions an order, always check the customer identity first", Claude may route order queries to `get_customer` regardless of the tool descriptions.

**Rule:** After updating tool descriptions, always review the system prompt for conflicts.

---

## Testing Tool Selection

The exam guide's preparation recommendation: *"Test tool selection reliability with ambiguous requests."*

Don't assume descriptions are fixed just because you edited them. Build a small evaluation set:

1. Write 20–30 realistic, **ambiguous** user queries ("something's wrong with my account", "resend last month's thing")
2. Record the expected tool for each
3. Run them, log the tool Claude selected
4. Measure the misrouting rate; find the most-confused pair; fix that pair's descriptions/names; re-measure

This is Domain 4's evaluation discipline applied to tool design.

---

## Key Takeaways for the Exam

| Concept | Remember |
|---|---|
| Tool description | The **primary** mechanism for Claude's tool selection (name + schema also matter) |
| Good description | What it does + inputs + examples + limitations + explicit boundaries; at least 3–4 sentences |
| `input_schema` | Description on every parameter, `enum` for value sets, unambiguous parameter names |
| Misrouting | Similar names/descriptions → wrong tool selection. First fix: expand descriptions + rename if needed |
| Tool splitting | Different purpose + different output contract → split. Same workflow → consolidate. |
| Output design | Meaningful context, `response_format`, pagination, "does not return" |
| System prompt conflict | Prompt instructions can override good descriptions — check for conflicts |
| Exam principle | Low effort, high leverage → descriptions/names before a classifier; split before consolidating (when purposes differ) |

---

## Practice Scenario

> An agent has two tools: `search_knowledge_base` and `search_tickets`. Both descriptions say "Searches for relevant information." Users report that support-ticket queries frequently go to the knowledge base.
>
> A developer proposes adding a routing classifier that analyzes the query and routes it to the correct tool before Claude sees it.
>
> **Is this the correct first step? Why?**
>
> **A)** Yes — the routing classifier analyzes the query and routes it to the right tool, solving the misrouting.
>
> **B)** No — expand the tool descriptions first. Add explicit boundaries such as "use for FAQs, product documentation, how-to guides; does not contain customer-specific case records" to `search_knowledge_base` and "use for existing support tickets, complaint history, open cases; does not contain general documentation" to `search_tickets`. If needed, sharpen the names too: `search_kb_articles` / `search_support_tickets`.
>
> **C)** No — merge the two tools into a single `search_all` tool.
>
> **D)** No — add 5 few-shot examples to the system prompt showing when to use each tool.

### Correct Answer: B

**Why B is correct:** The root cause is that the descriptions (and names) are ambiguous — both tools "search for relevant information". Claude cannot differentiate. Expanding the descriptions and renaming if needed is a low-effort, high-leverage fix aimed directly at the root cause. It applies two Skills from the exam guide at once ("writing tool descriptions that clearly differentiate" + "renaming tools and updating descriptions").

**Why A is wrong:** A routing classifier is over-engineering for a first step. You haven't tried the simple fix (improving descriptions). The classifier adds complexity and maintenance cost.

**Why C is wrong:** Merging breaks separation of concerns. Combining two different data sources (knowledge base and tickets) into one tool does not remove the ambiguity — it moves it inside the tool, which now has to guess which source to search.

**Why D is wrong:** Few-shot examples add token cost and treat the symptom, not the root cause. While the descriptions are vague, examples do not provide a reliable fix.
