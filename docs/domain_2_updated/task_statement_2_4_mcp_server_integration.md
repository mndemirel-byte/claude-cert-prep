# Task Statement 2.4: MCP Server Integration

## Domain 2 — Tool Design & MCP Integration (18% of the exam)

---

## Core Idea

MCP (Model Context Protocol) is the open protocol that connects Claude to external tools and data sources. An MCP server is written once; Claude Code, Claude Desktop, the Agent SDK and the Messages API's MCP connector can all use the same server. This task statement teaches how MCP servers are configured and scoped in Claude Code, and when to build a custom server.

---

## MCP's Three Primitives

An MCP server offers three kinds of things (the Intro to MCP course gives all three equal weight):

| Primitive | What | Who triggers it | How it appears in Claude Code |
|---|---|---|---|
| **Tools** | Functions the model calls (create issue, run query) | The model | Tools named `mcp__<server>__<tool>` |
| **Resources** | Read-only content / data catalogs (schema, doc tree, issue list) | Application / user | `@server:protocol://resource` mentions |
| **Prompts** | Ready-made prompt templates the server offers | The user | `/mcp__server__prompt` slash commands |

---

## The Scoping Hierarchy

The exam guide emphasizes two levels: **project** (`.mcp.json`) and **user** (`~/.claude.json`). Claude Code's actual model has three scopes; knowing the third (local) explains the "I wanted to share with the team but it didn't land in `.mcp.json`" mistake.

| Scope | Stored in | Loaded in | Shared with team | For |
|---|---|---|---|---|
| **local** (the `claude mcp add` **default**) | `~/.claude.json`, keyed by project path | That project only | ❌ | Personal experiments, single-project credentials |
| **project** | `.mcp.json` (repo root) | That project only | ✅ **via version control** | The team's shared tooling — everyone gets the same configuration |
| **user** | `~/.claude.json` top level | **All** projects | ❌ | Personal, project-independent tools |

```bash
claude mcp add --transport http shared-server --scope project https://example.com/mcp   # → .mcp.json
claude mcp add --transport http hubspot --scope user https://mcp.hubspot.com/anthropic   # → ~/.claude.json (all projects)
claude mcp add --transport http stripe https://mcp.stripe.com                            # → local (the default!)
```

**Precedence** (when the same name is defined in several places): local > project > user > plugin servers > claude.ai connectors > organization-managed (highest).

### Approval mechanism for project `.mcp.json` — security

So that someone cloning a repo does not unknowingly run a foreign server, Claude Code **asks for approval on first use** of servers coming from `.mcp.json` in interactive sessions. They show as `⏸ Pending approval` in the `/mcp` panel. `claude -p` (headless) and Agent SDK sessions load them without prompting.

Settings (`settings.json`):
- `enableAllProjectMcpServers: false` → reject all `.mcp.json` servers
- `enabledMcpjsonServers: [...]` / `disabledMcpjsonServers: [...]` → allowlist / blocklist
- `claude mcp reset-project-choices` → reset approval decisions

Exam scenario: "The team added a server to `.mcp.json`, but its tools don't appear in my session." → The server is awaiting approval (approve via `/mcp`) or disabled by settings.

### Important Detail
Tools from all configured servers are **discovered at connection time** (`tools/list`) and are available simultaneously. The tools of all three scopes merge into one pool — which is why many servers = many tools = the overload risk from Domain 2.3.

---

## Transport Types

| Transport | How it works | `.mcp.json` fields | When |
|---|---|---|---|
| **stdio** | Claude Code starts the server as a local child process | `type: "stdio"`, `command`, `args`, `env` | Local tools, npm/Python packages |
| **http** | Streamable HTTP to a remote server | `type: "http"`, `url`, `headers`, `oauth` | SaaS integrations (Notion, Stripe, Sentry…) |
| **sse** | Server-Sent Events — **deprecated** | `type: "sse"`, `url` | Only legacy servers without http |

```bash
# stdio: "--" separates Claude's options from the server command
claude mcp add --transport stdio --env AIRTABLE_API_KEY=YOUR_KEY airtable -- npx -y airtable-mcp-server

# http + header
claude mcp add --transport http secure-api https://api.example.com/mcp --header "Authorization: Bearer token"
```

For remote servers requiring OAuth: the browser flow from the `/mcp` panel, or `claude mcp login <server>`.

---

## Environment Variable Expansion

`.mcp.json` supports the `${VAR_NAME}` and `${VAR_NAME:-default}` syntax. Expansion works in **all** of `command`, `args`, `env`, `url` and `headers`. This keeps credentials out of version control.

```json
{
  "mcpServers": {
    "github": {
      "type": "stdio",
      "command": "github-mcp-server",
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      }
    },
    "api-server": {
      "type": "http",
      "url": "${API_BASE_URL:-https://api.example.com}/mcp",
      "headers": {
        "Authorization": "Bearer ${API_KEY}"
      }
    }
  }
}
```

**Advantage:** Each developer sets their own token locally. Tokens never enter the repo. Security is preserved.

Details:
- If a variable is unset and has no default, the config still loads; `claude mcp list` shows a warning and the text stays as `${VAR}`.
- Safety measure: in a remote server's `url`/`headers`, Claude's own credentials such as `ANTHROPIC_API_KEY`, `ANTHROPIC_AUTH_TOKEN` read as **empty** — a `.mcp.json` cannot leak your API key to a foreign server.

---

## Tool Naming: `mcp__<server>__<tool>`

MCP tools appear in Claude Code as `mcp__<server-name>__<tool-name>` (`mcp__github__create_issue`). This full name is used in:

- Permission rules (`settings.json` → `permissions.allow: ["mcp__github__*"]`)
- Subagent `tools` lists (Domain 2.3 / 1.3)
- Hook matchers (Domain 1.5)
- Skill `allowed-tools`

Servers bundled with plugins take the form `mcp__plugin_<plugin>_<server>__<tool>`.

---

## MCP Resources

MCP servers can offer not only tools but **resources**:

- Issue summaries
- Documentation hierarchies
- Database schemas

**Benefit:** They show agents a catalog of available data — no exploratory tool calls needed. Fewer unnecessary queries.

Example: an agent sees the database schema as an MCP resource and knows which tables exist — instead of 3–4 exploratory calls like "list tables", "show columns", it queries the right table directly.

In Claude Code: a mention such as `@postgres:schema://orders` pulls the resource into the conversation; the built-in `ListMcpResourcesTool` / `ReadMcpResourceTool` give programmatic access.

---

## MCP Output Limit

Claude Code truncates MCP tool results at **25,000 tokens** by default (warning at 10,000; configurable via `MAX_MCP_OUTPUT_TOKENS`). Beyond the limit the result is written to a file and a file reference enters the context. The fix for "the tool returns the whole table and bloats context" is server-side: pagination, filtering, `response_format: concise` (see Domain 2.1 — output design).

---

## The Build vs Use Decision

This decision is tested on the exam. The rule is clear:

### Evaluate Community MCP Servers First
For standard integrations (Jira, GitHub, Slack, databases), **community / official MCP servers** already exist. Use them.

### When to Build a Custom Server?
**Only** when team-specific workflows are not covered by community servers.

Examples:
- Connection to the company's proprietary internal API → custom server needed
- Standard Jira integration → community server suffices
- Jira exists, but a team-specific composite workflow like "at sprint close, pull data from 5 systems and produce a report in our template" → community server + a custom "workflow" tool (or a custom server)

### What "evaluate" means — checklist

| Criterion | Question |
|---|---|
| Coverage | Does it offer the operations you need (create / update / query)? |
| Maintenance | Is it active, releasing versions, official or community? |
| Authentication | Does its token / OAuth model fit your security policy? |
| Tool quality | Are descriptions detailed, is the tool count reasonable (a 50-tool server = context load)? |
| Security | Tool annotations and descriptions from untrusted sources are "untrusted" — the spec requires it |

### Enhancing MCP Tool Descriptions

An important detail: the agent sometimes prefers built-in tools (like Grep) over MCP tools. The mechanism: the built-in `Grep`'s description is long, detailed and familiar; if the MCP tool says `"Searches code"`, Claude picks the built-in tool that "looks richer" — even when the MCP tool is actually more capable (semantic search, index, cross-repo).

**Fix:** Enrich the MCP tool description to detail **capabilities and output**: what it can do, what it returns, how it differs from the built-in ("unlike Grep, resolves symbol definitions and references language-aware; results include file + line + symbol kind"). The exam guide's Skills wording: *"explain capabilities and outputs in detail."* This is Domain 2.1's description principles applied to MCP.

---

## The Agent SDK and API Side

| Path | How | When |
|---|---|---|
| **Claude Code** | `.mcp.json` / `claude mcp add` | Interactive and headless development |
| **Agent SDK** | `mcpServers` option (same JSON structure); `allowedTools: ["mcp__github__*"]` | Your own agent application, using Claude Code's capabilities programmatically |
| **Agent SDK in-process** | `createSdkMcpServer` + `tool()` — no separate process, tools defined inside the app | Small app-specific tools; when you don't want to manage a child process |
| **Messages API MCP connector** | `mcp_servers: [{url, name, …}]` in the request | Connecting to a remote MCP server straight from the API, without Claude Code |

The practice scenario's "no need for MCP, call the Jira API directly" option should be read against this table: writing your own tool function with the Messages API and calling Jira REST **is a legitimate architecture** (the Building with the Claude API course does exactly that). MCP's advantage is not necessity: standardization, reusability (one server for every client), discovery (`tools/list`), and being **the** integration path in the Claude Code context.

---

## Key Takeaways for the Exam

| Concept | Remember |
|---|---|
| `.mcp.json` | Project scope — version controlled, shared with the team, approval on first use |
| `~/.claude.json` | User scope (all projects) **and** local scope (one project, the `claude mcp add` default) — both personal |
| `--scope project` | State it explicitly to share with the team; default is local |
| Environment variables | `${VAR}` / `${VAR:-default}` — command, args, env, url, headers; credentials outside the repo |
| Transport | stdio (local process), http (remote), sse (deprecated) |
| `mcp__server__tool` | Permissions, subagent `tools`, hook matchers, skill allowed-tools |
| Three primitives | Tools (model calls), Resources (`@server:…`), Prompts (`/mcp__server__prompt`) |
| MCP resources | Content catalogs — fewer exploratory queries |
| Output limit | 25k tokens default → server-side pagination |
| Build vs use | Standard integration → community server. Team-specific workflow → custom server |
| Description enhancement | Capability + output detail → so the agent doesn't prefer built-ins over MCP |
| SDK / API | `mcpServers`, in-process `createSdkMcpServer`, API `mcp_servers` connector |

---

## Practice Scenario

> A team wants to set up a Jira integration. A developer proposes building a custom MCP server — it will connect to the Jira API, create issues, update statuses and fetch sprint information.
>
> **Is this the right approach?**
>
> **A)** Yes — a custom server fits the team's needs exactly and gives full control.
>
> **B)** No — evaluate the existing Jira MCP server first. Standard issue creation, status updates and sprint retrieval are already covered. Build a custom server only if there are team-specific workflows not covered.
>
> **C)** No — MCP isn't needed; have Claude Code make `curl` calls to the Jira REST API through the Bash tool.
>
> **D)** No — have each developer add the Jira server to their own `~/.claude.json` with `--scope user`, so everyone works with their own token.

### Correct Answer: B

**Why B is correct:** Standard Jira operations (issue creation, status updates, sprint info) are already covered by existing MCP servers. Building a custom server is wasted effort — maintenance, testing, upgrade cost. Exam guide: "Choosing existing community MCP servers over custom implementations for standard integrations, reserving custom servers for team-specific workflows."

**Why A is wrong:** "Full control" sounds nice, but building from scratch when a solution exists is over-engineering. Exam principle: simple, low-effort fix first. If a team-specific need emerges, then a custom server (or a small extra tool next to the existing server).

**Why C is wrong:** Bash + `curl` gives Claude no discoverable tool interface, no schema, no structured error response (`isError`), and no permission-rule granularity; every call is a free-text command, can't be shared with the team, and requires `Bash` permission. (Note: writing *your own tool function* with the Messages API is legitimate — but this option proposes bypassing MCP inside Claude Code, not that.)

**Why D is wrong:** Scope confusion. The team's shared integration belongs in `.mcp.json` (project scope) so everyone gets the same configuration; personal tokens stay outside via the `${JIRA_TOKEN}` environment variable. Each developer defining their own user-scope entry causes configuration drift, and a newcomer can't discover the setup.
