# Task Statement 3.6: CI/CD Integration

## Domain 3 — Claude Code Configuration & Workflows (20% of the exam)

---

## Core Idea

Claude Code isn't only used interactively in the terminal — it can be integrated into **CI/CD pipelines**. PR review, test generation, code analysis can run automatically. This task statement teaches **how to configure** CI/CD integration and its **common pitfalls** (course modules: *Routines and Headless*, *GitHub Actions and Code Review*).

A Claude Code call in CI has **four components**; the exam tests each one separately:

1. **Non-interactivity** → `-p`
2. **Permissions** → `--allowedTools` / `--permission-mode`
3. **Structured output** → `--output-format json` + `--json-schema`
4. **Context** → CLAUDE.md, existing tests, prior review findings, a piped diff

---

## 1. The `-p` Flag — Non-Interactive Mode (Print Mode)

This is the single most-tested concept. **Memorize it.**

### Problem

A CI/CD pipeline runs:

```bash
claude "Analyze this PR"
```

The pipeline **hangs forever.** The logs show Claude **waiting for interactive input**.

### Fix

```bash
claude -p "Analyze this PR"
```

The `-p` (`--print`) flag runs Claude Code in **non-interactive mode**: no interactive terminal UI opens, the prompt is processed, the output is printed, and the process exits. Exit code: **0 on success, non-zero on failure** — the pipeline can branch on it.

> **Run Claude Code in a CI pipeline without `-p` and the pipeline hangs.** It's that simple.

### Feeding stdin

Non-interactive mode reads stdin; Claude Code fits into a pipe like any Unix tool:

```bash
git diff main | claude -p "Review this diff for typos; report file:line and the issue"
gh pr diff "$PR" | claude -p --append-system-prompt "You are a security engineer." --output-format json
```

An extra benefit of piping the diff: Claude **doesn't need Bash permission** to read it (see section 2). The stdin cap is 10 MB.

---

## 2. Permissions in CI — `-p` Alone Is Not Enough

**This is the exam's "second-level" question.** `-p` removes the interactive *UI* but **does not remove the permission system**: a `-p` session starts in **Manual (`default`) mode**. When Claude wants to edit a file or run a Bash command it asks for permission; in CI nobody answers → the request is **denied** and the work doesn't happen (or, if a permission host exists, the run waits).

| Symptom | Answer |
|---|---|
| Pipeline hangs, "waiting for input" | `-p` is missing |
| `-p` present, Claude says "I need permission to edit…", no file changes | Permission configuration is missing ↓ |

### Options

```bash
# (a) Pre-approve specific tools — permission-rule syntax
claude -p "Run the test suite and fix failures" --allowedTools "Bash(npm test *),Read,Edit"

# (b) Mode-based baseline
claude -p "Apply the lint fixes" --permission-mode acceptEdits   # file edits + mkdir/mv/cp auto-approved
claude -p "…" --permission-mode dontAsk                          # EVERYTHING that would prompt is denied — locked-down CI
claude -p "…" --permission-mode auto                             # a classifier approves/denies

# (c) Last resort
claude -p "…" --dangerously-skip-permissions                     # = bypassPermissions
```

- `--allowedTools` uses **permission-rule syntax**: `Bash(git diff *)` — ` *` enables prefix matching (the space matters: `git diff*` would also match `git diff-index`)
- `dontAsk` is the official recommendation: "Use this mode for CI pipelines or restricted environments where you pre-define what Claude may do; the session never waits for input." — reads and tools in `--allowedTools` run, everything else is silently denied
- Cap runaway runs with `--max-turns N` (exits with an error when the limit is hit) and `--max-budget-usd`
- Links to Domain 1.4 (permission modes) and Task 3.4 (plan mode is a permission mode too)

> **Exam rule:** "It hangs" → `-p`. "`-p` is there but it makes no changes / permission denied" → `--allowedTools` or `--permission-mode`. Timeout wrappers, `echo yes |`, version upgrades → always wrong.

---

## 3. Structured CI Output

In CI/CD pipelines human-readable text isn't enough — automated systems want **machine-parseable** output.

### Three output formats

| `--output-format` | What you get |
|---|---|
| `text` (default) | Plain text |
| `json` | One JSON object: `result` (text), `session_id`, `total_cost_usd`, usage metadata |
| `stream-json` | One event per line (with `--verbose`) — real-time streaming |

### Structured Findings with a JSON Schema

```bash
claude -p "Review this PR" \
  --output-format json \
  --json-schema '{"type":"object","properties":{"issues":{"type":"array","items":{"type":"object","properties":{"file":{"type":"string"},"line":{"type":"integer"},"severity":{"type":"string"},"message":{"type":"string"}}}},"summary":{"type":"string"}},"required":["issues","summary"]}' \
  | jq '.structured_output'
```

- The structured result lands in the JSON's **`structured_output`** field; free text stays in `result`
- `--json-schema` works only in print mode; an invalid schema → exits with `Error: --json-schema is not a valid JSON Schema`
- Same principle as Domain 4.3 (structured output), on the CLI surface

**Benefit:** Automated systems can parse the `issues[]` array and post each finding **as an inline PR comment** — the exam guide's "machine-parseable structured findings for automated posting as inline PR comments".

---

## 4. Context — What Should CI's Claude Know?

### 4a. CLAUDE.md for CI

If Claude Code is invoked in a CI/CD pipeline to generate tests or review code, **project context documented in CLAUDE.md** is critical. By default `claude -p` loads the same context an interactive session would — CLAUDE.md included.

**What CLAUDE.md should contain (exam guide):**
- **Testing standards** — which framework (vitest, jest), which pattern (describe/it)
- **Valuable test criteria** — rules defining what should be tested (business logic, edge cases; not getters/setters)
- **Available fixtures** — what the test infrastructure already has, so no mocks from scratch
- **Review criteria** — what to look for in a review

**What happens without CLAUDE.md?** Claude Code generates **low-value boilerplate tests** — empty scaffolds that don't test real business logic; the framework is inconsistent; fixtures go unused.

> **Current note (does not change the exam answer):** The official recommendation for CI/scripts is `--bare`: hooks, skills, MCP, auto memory **and CLAUDE.md** are not loaded → identical results on every machine, faster startup ("will become the default for `-p`"). If you use `--bare`, you provide project context *explicitly* via `--append-system-prompt-file` / `--settings`. Without it, CLAUDE.md comes in automatically — but so do the repo's `.mcp.json` servers and hooks, without approval (security note). **Exam answer: CLAUDE.md.**

### 4b. Provide Existing Test Files in Context — A Separate Item!

A Skills bullet the exam guide counts **separately** from CLAUDE.md: "Providing **existing test files in context** so test generation avoids suggesting **duplicate scenarios** already covered by the test suite."

| Symptom | Fix |
|---|---|
| Tests are empty scaffolds, wrong framework, fixtures unused | Document standards/fixtures in CLAUDE.md |
| Tests **re-propose scenarios that already exist** | Put the **existing test files** in the prompt/context (`@tests/auth.test.ts` or stdin) |

CLAUDE.md gives the *rules*; the existing tests show *what's already covered*. They solve different problems.

### 4c. Incremental Review Context

When you re-run a review after new commits, **include the prior review findings in context** and instruct Claude to **report only new or still-unaddressed issues**.

**Why?** Without the prior findings, Claude re-reports the same issues → **duplicate comments** → erodes developer trust.

**The right approach — a flow combined with section 3:**
```bash
# First run: store findings as JSON
claude -p "Review this PR" --output-format json --json-schema "$SCHEMA" \
  | jq '.structured_output' > previous_findings.json

# New commit: pass prior findings, ask only for new/unaddressed
gh pr diff "$PR" | claude -p "Review this PR. Previous review findings: $(cat previous_findings.json).
Report ONLY new or still-unaddressed issues." --output-format json --json-schema "$SCHEMA"
```

---

## Session Context Isolation — The Same Session Can't Review Itself

This matters a lot and is tested:

> **The same Claude session that generated the code is LESS EFFECTIVE at reviewing its own changes.**

### Why?

The same session carries the reasoning context it built while writing the code. That context makes it **less likely** to question its own decisions. It has already justified its logic — reviewing again, it reaches the same conclusion. Best practices: "A reviewer running in a fresh context **sees only the diff and the criteria you give it, not the reasoning that produced the change**."

### Mechanism: how does "the same session" happen in CI?

Every `claude -p` call is **a new session by default** — isolation comes for free. The only way to continue a session is **`--continue`** (most recent) or **`--resume <session_id>`**. Therefore:

```bash
# ❌ WRONG — the review inherits the generation's reasoning context
claude -p "Implement the user auth module" --output-format json | jq -r .session_id > sid
claude -p "Now review the changes you made for security issues" --resume "$(cat sid)"

# ✅ RIGHT — an independent review session; it sees only the diff
claude -p "Implement the user auth module" --allowedTools "Edit,Bash(npm test *)"
git diff main | claude -p "Review this diff for security issues" --output-format json --json-schema "$SCHEMA"
```

The same principle in interactive use is the **Writer/Reviewer** pattern (two separate sessions) and, inside Claude Code, the **adversarial review subagent** (a subagent in a fresh context that sees only the diff). Link to Domain 4.6 (multi-instance review).

> **Exam rule:** "The review finds almost nothing but humans find plenty" + "same session / `--continue`" → an independent review session. Improving the prompt, changing the model, adding criteria to CLAUDE.md doesn't fix the root cause.

---

## GitHub Actions Integration

The concrete counterpart of the exam guide's "inline PR comments" is `anthropics/claude-code-action@v1` (course module: *GitHub Actions and Code Review*).

| Topic | Detail |
|---|---|
| Setup | `/install-github-app` (GitHub App + secret + workflow PR) or manual: `.github/workflows/claude.yml` |
| **Interactive mode** | Without a `prompt` in the workflow, Claude waits for an **`@claude`** mention in an issue/PR comment |
| **Automation mode** | With a `prompt`, it runs on any GitHub event: review when a PR opens, daily report on a cron |
| `claude_args` | CLI flags: `--allowedTools "mcp__github_inline_comment__create_inline_comment"`, `--max-turns 5`, `--model …` |
| Credentials | **GitHub Secrets only**: `anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}` or `claude_code_oauth_token`. **Never commit them** |
| CLAUDE.md | The action reads the repo root's CLAUDE.md — "Define project standards in CLAUDE.md" |
| Cost | `--max-turns`, workflow timeouts, concurrency; keep CLAUDE.md concise (read on every run) |

```yaml
on:
  pull_request:
    types: [opened, synchronize]
jobs:
  review:
    runs-on: ubuntu-latest
    permissions: { contents: read, pull-requests: read, id-token: write }
    steps:
      - uses: actions/checkout@v6
      - uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          prompt: "/code-review:code-review --comment ${{ github.repository }}/pull/${{ github.event.pull_request.number }}"
          claude_args: '--allowedTools "mcp__github_inline_comment__create_inline_comment"'
```

---

## Key Takeaways for the Exam

| Concept | Remember |
|---|---|
| `-p` / `--print` | Mandatory in CI/CD — non-interactive mode. Without it the pipeline hangs. Exit code 0 / non-zero |
| Permissions | `-p` starts in Manual mode; for changes use `--allowedTools "Edit,Bash(npm test *)"` or `--permission-mode acceptEdits/dontAsk/auto` |
| `--output-format json` | Machine-parseable; `result`, `session_id`, `total_cost_usd` |
| `--json-schema` | Schema-conforming output → the **`structured_output`** field; for inline PR comments |
| stdin pipe | `git diff main \| claude -p "…"` — no Bash permission needed |
| CLAUDE.md for CI | Testing standards, valuable test criteria, fixtures, review criteria — without it, boilerplate tests |
| Existing test files | Put them in context → no duplicate test-scenario suggestions (separate item from CLAUDE.md) |
| Incremental review | Include prior findings, "report only new/unaddressed issues" |
| Session isolation | Every `claude -p` is a new session; **don't review with `--continue`/`--resume`** — an independent session sees the diff fresh |
| GitHub Actions | `@claude` (interactive) vs `prompt` (automation); secrets; `claude_args` |
| `--bare` (current note) | Deterministic startup in CI; also skips CLAUDE.md → provide context explicitly |
| Exam favorite | "Pipeline hangs" → `-p`. "Makes no changes" → permissions |

---

## Practice Scenario 1

> A CI pipeline script runs:
>
> ```bash
> claude "Analyze this PR for potential bugs"
> ```
>
> The pipeline hangs forever. The logs show Claude waiting for input.
>
> **What is the correct fix?**
>
> **A)** Wrap the command in a timeout — kill it automatically after 60 seconds.
>
> **B)** Add the `-p` flag — `claude -p "Analyze this PR for potential bugs"` — to run in non-interactive mode.
>
> **C)** Pipe `echo "yes" |` into the command — so it answers "yes" automatically.
>
> **D)** Upgrade Claude Code — it might be a bug in the old version.

### Correct Answer: B

**Why B is correct:** The `-p` flag runs Claude Code in non-interactive (print) mode. No interactive UI opens; it analyzes directly, prints the output and exits. Always use `-p` in CI/CD pipelines.

**Why A is wrong:** A timeout doesn't solve the problem — it cuts Claude's analysis short and produces no output. The problem is Claude opening the interactive UI; the fix is turning it off (`-p`).

**Why C is wrong:** An `echo "yes"` pipe is unreliable and dangerous. The interactive UI doesn't wait for "yes" on stdin; and approving without knowing what was asked blindly bypasses the permission mechanism.

**Why D is wrong:** This is not a bug; it is expected behavior. Claude Code runs interactively by default. In CI the `-p` flag is required.

---

## Practice Scenario 2

> A team does automated code review with Claude Code in a CI pipeline. The pipeline follows these steps:
> 1. `claude -p "Implement the feature described in the issue" --output-format json` → the `session_id` is saved
> 2. `claude -p "Review the changes you just made for bugs and security issues" --resume $SESSION_ID`
>
> The review results are very positive — it finds almost nothing. But human reviewers find many issues in the same code.
>
> **What is the root cause?**
>
> **A)** Claude Code's review capability is insufficient — use a different model.
>
> **B)** With `--resume`, the review inherits the reasoning context of the session that generated the code — it doesn't question its own decisions. The review should run in an **independent `claude -p` call** without `--resume`, seeing only the diff.
>
> **C)** The review prompt is weak — add more detailed review instructions.
>
> **D)** CLAUDE.md is missing review standards.

### Correct Answer: B

**Why B is correct:** The session-isolation rule. `--resume` continues the same session; the review carries the reasoning made while writing the code — it has already justified its decisions and reaches the same conclusion on re-inspection. An independent `claude -p` call (default: new session) sees the code for the first time, as a diff only, and reviews without bias.

**Why A is wrong:** The problem isn't the model's capability but contextual bias. The same model reviews far more effectively in an independent session.

**Why C is wrong:** Prompt improvement may help a little but doesn't fix the root cause. The same session is reviewing its own code — however good the prompt, the reasoning context creates bias.

**Why D is wrong:** CLAUDE.md matters for review criteria, but the problem here is structural — session isolation. Even with standards, the same session falls short at questioning its own code.

---

## Practice Scenario 3

> A CI pipeline reviews every PR with Claude Code. When new commits arrive the review is re-run. Developers complain: "Claude reports the same issues every time — it keeps flagging things I've already fixed."
>
> **What is the fix?**
>
> **A)** Use a different prompt on each run — Claude produces the same findings when it sees the same prompt.
>
> **B)** Run the review only against the latest commit — ignore earlier files.
>
> **C)** Include the prior review findings in context and instruct Claude to "report only new or still-unaddressed issues".
>
> **D)** Reduce the review frequency — run once before merge rather than on every PR update.

### Correct Answer: C

**Why C is correct:** Incremental review context. Including the prior findings (ideally the previous run's `structured_output` JSON) tells Claude what was already reported and what was fixed. With the instruction "report only new or unaddressed issues" the duplicate comments disappear. Developer trust is preserved.

**Why A is wrong:** A different prompt doesn't help — if Claude doesn't know the prior findings it will rediscover and re-report the same issues.

**Why B is wrong:** Looking only at the latest commit misses file-wide issues. A commit may have partially fixed a larger problem — the full context is needed.

**Why D is wrong:** Reducing frequency postpones the problem rather than solving it, and loses the early-feedback benefit.

---

## Practice Scenario 4

> A CI job runs:
>
> ```bash
> claude -p "Fix all ESLint errors in src/" --output-format json
> ```
>
> The job doesn't hang and exits with code zero; but the `result` field contains text like "I need permission to edit src/utils.ts…" and no file has changed.
>
> **What are the root cause and the fix?**
>
> **A)** The `-p` flag blocks editing — remove `-p` in CI.
>
> **B)** A `-p` session starts in Manual permission mode; since nobody in CI can answer the permission prompt, the edits are denied. Add `--allowedTools "Edit,Bash(npx eslint *)"` or `--permission-mode acceptEdits`.
>
> **C)** `--output-format json` disables editing — use `text`.
>
> **D)** Wrap the command in `timeout 300` — Claude isn't getting enough time.

### Correct Answer: B

**Why B is correct:** `-p` only removes the interactive UI; the permission system works as usual and `-p` starts in Manual mode. When an edit permission is requested and no answer arrives, the action is denied, Claude reports that in text, and the process exits "successfully". In CI, pre-define the work: specific tools/commands via `--allowedTools`, or the `acceptEdits` (file edits auto-approved) / `dontAsk` (locked down) / `auto` (classifier) mode.

**Why A is wrong:** Without `-p` the pipeline hangs (Scenario 1). `-p` doesn't block editing; permissions do.

**Why C is wrong:** The output format only determines how the result is printed; it has nothing to do with permissions.

**Why D is wrong:** It's not a time issue; the job already finishes normally. A timeout doesn't approve a denied permission.
