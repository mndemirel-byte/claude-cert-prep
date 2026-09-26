# Domain 3 — Practice Exam

## Claude Code Configuration & Workflows (20% of the exam)

**Distribution (10 questions):**
- 2 questions → CLAUDE.md Hierarchy (3.1)
- 2 questions → Custom Commands and Skills (3.2)
- 1 question → Path-Specific Rules (3.3)
- 2 questions → Plan Mode vs Direct Execution (3.4)
- 1 question → Iterative Refinement (3.5)
- 2 questions → CI/CD Integration (3.6)

**Passing threshold:** 8+/10

| Question | Task Statement | Concept tested |
|---|---|---|
| 1 | 3.1 | `CLAUDE.local.md` vs `~/.claude/CLAUDE.md` |
| 2 | 3.1 | `@path` imports load at launch vs directory CLAUDE.md on demand |
| 3 | 3.2 | `allowed-tools` (exam wording) + `context: fork` + personal skill |
| 4 | 3.2 | `disable-model-invocation` — only the user should trigger a side-effect skill |
| 5 | 3.3 | Scattered API files → glob rule; deterministic vs probabilistic |
| 6 | 3.4 | The "direct first, plan if needed" trap |
| 7 | 3.4 | Explore is read-only; the hybrid flow |
| 8 | 3.5 | Interacting fixes → one message |
| 9 | 3.6 | `-p` present but no changes → permissions |
| 10 | 3.6 | Duplicate test scenarios → existing tests in context (separate from CLAUDE.md) |

---

## Question 1 (Task Statement 3.1)

> A developer wants Claude Code to know, in every session on the e-commerce project they work on, their local sandbox URL (`http://localhost:4010`) and their personal test-customer ID. This is personal — it must not enter the repo. The developer also works on two other projects and wants this information **absent** from context there.
>
> **What is the most appropriate location?**
>
> **A)** `~/.claude/CLAUDE.md` — personal, not in Git.
>
> **B)** `CLAUDE.local.md` at the project root, added to `.gitignore`.
>
> **C)** `.claude/CLAUDE.md` — project level, loaded every session.
>
> **D)** `.claude/rules/sandbox.md` with `paths: ["**/*"]` in the frontmatter.

### Correct Answer: B

**Why B is correct:** Two constraints: personal (must not enter the repo) **and** project-specific (must not leak into other projects). `CLAUDE.local.md` exists for exactly that intersection — it sits at the project root, loads alongside `CLAUDE.md`, and goes into `.gitignore`.

**Why A is wrong:** `~/.claude/CLAUDE.md` is personal but loads in **every project** on the machine — the sandbox URL would be in context in the other two projects.

**Why C is wrong:** A project-level file goes into Git; the personal test ID would be shared with the team.

**Why D is wrong:** `.claude/rules/` is project scope and goes into Git; and `**/*` means "every file" — equivalent to an unconditional rule, providing no personal scoping.

---

## Question 2 (Task Statement 3.1)

> A monorepo's root `.claude/CLAUDE.md` has reached 600 lines: general standards + React rules for `web/` + Go rules for `api/` + Terraform rules for `infra/`. The team has two complaints: (1) Claude ignores some rules, (2) even while working in `api/`, the React rules consume tokens.
>
> A developer proposes: split the root file into four parts and import them with `@docs/react.md`, `@docs/go.md`, `@docs/terraform.md`.
>
> **Which of the two complaints does this proposal solve?**
>
> **A)** Both — imported files load only while working in the relevant directory.
>
> **B)** Only (1), partially — the file becomes organized, but imported files load **at launch** together; total context stays the same and the React rules are still spent in `api/`. For (2), directory-level `web/CLAUDE.md`, `api/CLAUDE.md`, `infra/CLAUDE.md` files (loaded on demand) are needed.
>
> **C)** Neither — import syntax only works in `~/.claude/CLAUDE.md`.
>
> **D)** Only (2) — imports are lazy-loaded but the file size doesn't change.

### Correct Answer: B

**Why B is correct:** `@path` imports are an **organization** tool: the files enter context at launch together with CLAUDE.md, saving no tokens. The bloat that leads to ignored rules (complaint 1) improves partially because the file becomes readable; but the real fix is reducing the total loaded text. Only **on-demand** mechanisms do that: directory-level CLAUDE.md (when a file in that directory is read) or `paths` rules.

**Why A is wrong:** Imports are not lazy-loaded; this is the most common confusion between 3.1 and 3.3.

**Why C is wrong:** Imports work in every CLAUDE.md (relative paths resolve relative to the importing file).

**Why D is wrong:** The opposite — imports load at launch; (2) is not solved.

---

## Question 3 (Task Statement 3.2)

> A team has these requirements:
>
> 1. A `/deploy-checklist` command for the whole team — a pre-deployment checklist
> 2. One developer wants a personal `/deep-analyze` skill that performs large codebase analyses — it produces very verbose output and must not pollute the main conversation
> 3. The `/deep-analyze` skill must only use read tools — no file writes or deletes
>
> **Which configuration is correct?**
>
> **A)** Both go in `.claude/commands/`.
>
> **B)** `/deploy-checklist` → `.claude/commands/` (project-scoped). `/deep-analyze` → `~/.claude/skills/deep-analyze/SKILL.md` with `context: fork`, `agent: Explore` and `allowed-tools: Read Grep Glob` in the frontmatter.
>
> **C)** Both should be written as procedures in CLAUDE.md.
>
> **D)** `/deploy-checklist` → `~/.claude/commands/`. `/deep-analyze` → `.claude/skills/`.

### Correct Answer: B

**Why B is correct:** It meets all three requirements:
1. `/deploy-checklist` is team-wide → `.claude/commands/` (project-scoped, in Git, shared — exam guide Q4)
2. `/deep-analyze` is personal and verbose → `~/.claude/skills/` (personal) + `context: fork` (isolated context, main conversation clean)
3. Read tools only → in exam wording, `allowed-tools: Read Grep Glob`. **Note:** in real behavior `allowed-tools` *pre-approves* rather than restricts; a real restriction comes from `disallowed-tools: Write, Edit, Bash` or `agent: Explore` (which already denies Write/Edit). This option's `agent: Explore` provides that guarantee too.

**Why A is wrong:** `/deep-analyze` is a personal request — putting it in the team repo distributes it to everyone. The `context: fork` / tool-restriction frontmatter is also defined in the skill directory structure.

**Why C is wrong:** These are task-specific procedures — CLAUDE.md is for universal standards and is always loaded.

**Why D is wrong:** The placement is reversed. `/deploy-checklist` must be team-wide; `/deep-analyze` must be personal.

---

## Question 4 (Task Statement 3.2)

> A team created a skill at `.claude/skills/release/SKILL.md`: it tags a release, generates a changelog and runs `git push --tags`. The skill's `description` is "Publishes a new release". While a developer is chatting "I'm wondering whether these changes will make it into the next release", Claude loads the skill on its own and starts the release steps.
>
> **What is the correct fix?**
>
> **A)** Move the skill to `~/.claude/skills/` — personal skills aren't auto-triggered.
>
> **B)** Add `disable-model-invocation: true` to the frontmatter — the skill loads only when the user types `/release`; Claude can't invoke it via description matching.
>
> **C)** Add `context: fork` — the skill runs in an isolated context.
>
> **D)** Remove `allowed-tools: Bash(git push *)` — so Claude can't push.

### Correct Answer: B

**Why B is correct:** Skills are triggered two ways: the user types `/name` **or** Claude decides the `description` matches the conversation. For side-effect workflows (deploy, release, commit) the second path is dangerous. `disable-model-invocation: true` exists for exactly this: "Only you can invoke it manually." The official best-practices example uses it too (the `fix-issue` skill).

**Why A is wrong:** Personal skills are also auto-triggered by description; location doesn't change the trigger path.

**Why C is wrong:** Fork isolates output; it doesn't stop the skill from *starting* by mistake — it keeps releasing in the background.

**Why D is wrong:** Removing `allowed-tools` only brings back the permission prompt; the skill still triggers, starts the steps, and asks permission to push. The root cause is triggering, not permissions.

---

## Question 5 (Task Statement 3.3)

> In a codebase, API endpoint files are scattered across `src/api/`, `src/routes/` and `modules/*/api/`. The team wants the same rules applied to all API files: rate-limiting checks, input validation, standardized error responses. The rules must be applied **automatically, without leaving it to Claude's discretion**.
>
> **Which approach is correct?**
>
> **A)** Copy the same rules into `src/api/CLAUDE.md`, `src/routes/CLAUDE.md` and every `modules/*/api/CLAUDE.md`.
>
> **B)** Create `.claude/rules/api-conventions.md` — with `paths: ["src/api/**/*", "src/routes/**/*", "modules/*/api/**/*"]` in the frontmatter.
>
> **C)** Write all API rules in the root CLAUDE.md.
>
> **D)** Create an `/api-rules` skill — put "use when editing API files" in its description so Claude loads it when needed.

### Correct Answer: B

**Why B is correct:** Path-specific rules catch every API file in the codebase via glob patterns — whatever the directory. One rule file applies to all the scattered API files; it loads **deterministically** when a matching file is read. Token-efficient — in context only while working with an API file.

**Why A is wrong:** Copying the same rules into every directory is a maintenance nightmare. Change one rule and you update every copy. CLAUDE.md files are directory-bound.

**Why C is wrong:** The root CLAUDE.md is always loaded. Even while editing a frontend CSS file the API rules take up context — wasted tokens and file bloat.

**Why D is wrong:** The most tempting distractor. Claude *may* load the skill based on the description — but that is a **probabilistic** decision; it contradicts the "without leaving it to Claude's discretion" requirement. Exam guide Q6's rationale for option C: "relies on Claude choosing to load them, contradicting the need for deterministic automatic application based on file paths."

---

## Question 6 (Task Statement 3.4)

> A developer is assigned "convert the existing REST API to GraphQL": 40+ endpoints are affected, and decisions about schema design and resolver structure are needed. The developer thinks: "Plan mode adds overhead. I'll convert the first few endpoints in direct execution; if unexpected complexity comes up I'll switch to plan mode."
>
> **How should this approach be assessed?**
>
> **A)** Correct — starting with small steps reduces risk; planning once complexity appears is efficient.
>
> **B)** Wrong — the complexity is not "unexpected"; it's already stated in the requirements (40+ endpoints, schema decisions). Exploration and design in plan mode come first, implementation after approval.
>
> **C)** Wrong — the task should be handed entirely to the Explore subagent.
>
> **D)** Correct — but the context should be cleared with `/clear` first.

### Correct Answer: B

**Why B is correct:** The exact counterpart of exam guide Q5's option D: "Begin in direct execution mode and only switch to plan mode if you encounter unexpected complexity" → official rationale: "ignores that the complexity is already stated in the requirements, not something that might emerge later." Many files + architectural decisions + multiple approaches → plan mode. Converting the first endpoints with the wrong schema design and then planning is costly rework.

**Why A is wrong:** The "plan mode is overhead" heuristic is for tasks whose diff fits in one sentence; a 40-endpoint conversion is not in that class.

**Why C is wrong:** Explore is read-only; it only discovers, makes no design decisions and doesn't implement.

**Why D is wrong:** `/clear` resets context; it doesn't fix a wrong mode choice.

---

## Question 7 (Task Statement 3.4)

> A developer wants to replace lodash with native JavaScript functions in 30 files. Their approach:
>
> 1. In plan mode, discover the affected files and decide the migration strategy
> 2. Approve the plan and implement with direct execution
>
> A teammate objects: "Discovery will read too many files and fill the main context. Hand discovery **and implementation** to the Explore subagent."
>
> **Which assessment is correct?**
>
> **A)** The teammate is right — Explore both isolates discovery and makes the changes.
>
> **B)** The developer's approach is correct (hybrid: plan → approve → direct execution). Discovery is already delegated to the Plan/Explore subagents in plan mode, preserving the main context; but Explore is **read-only** (Write/Edit denied) — it can't implement.
>
> **C)** Both are wrong — 30 files is few; the whole thing should be direct execution.
>
> **D)** Both are wrong — the whole thing should stay in plan mode, no approval needed.

### Correct Answer: B

**Why B is correct:** The hybrid approach is plan mode's normal lifecycle: discovery (in subagents) → plan → approve → implement. The teammate's concern (context filling) is already covered by plan mode's built-in Explore/Plan delegation. But the second half of the suggestion is wrong: Explore's tool set is read-only; the built-in subagent that makes changes is `general-purpose`, and implementation happens in the main session after plan approval anyway.

**Why A is wrong:** Explore denies Write/Edit — it can't implement.

**Why C is wrong:** A 30-file migration needs discovery and planning; starting directly creates rework.

**Why D is wrong:** Plan mode can't edit files; approval and a mode switch are required to implement.

---

## Question 8 (Task Statement 3.5)

> A developer reviews a payment function Claude Code wrote. Two findings:
>
> 1. Currency conversion rounds incorrectly (cents are lost)
> 2. The amount the function returns is logged and written to the invoice record based on the rounding result — when the rounding changes, the log format and the invoice field must change too
>
> The developer first had only the rounding fixed; Claude did it, but the log and invoice code stayed on the old behavior. When the log/invoice was fixed in a second message, Claude rewrote the rounding function.
>
> **What should the developer have done?**
>
> **A)** Given both findings in one detailed message — the fixes interact; Claude can't make a consistent change without seeing the whole picture.
>
> **B)** Fixed the log/invoice first, then the rounding — the order was wrong.
>
> **C)** Created a separate skill for each finding.
>
> **D)** Given 2–3 concrete input/output examples — the prose was interpreted inconsistently.

### Correct Answer: A

**Why A is correct:** The findings **interact**: the rounding decision determines the log format and the invoice field. Given sequentially, each round breaks the other — exactly a violation of the exam guide's "single detailed message when fixes interact" rule. One message saying "fix the rounding like this **and** update the log/invoice code to the new result" lets Claude produce a consistent design.

**Why B is wrong:** It's not an ordering problem but an interaction problem; in either order, two separate messages make the second round rewrite the first.

**Why C is wrong:** Skills are for repeated procedures; over-engineering for one-off fixes.

**Why D is wrong:** The problem isn't ambiguous prose (Claude did each fix correctly); the problem is the fixes being given separately.

---

## Question 9 (Task Statement 3.6)

> A CI job runs:
>
> ```bash
> claude -p "Add missing null checks in src/services/" --output-format json
> ```
>
> The job doesn't hang; exit code 0. But the `result` field says "I need permission to edit src/services/user.ts…" and no file has changed.
>
> **What are the root cause and the fix?**
>
> **A)** `-p` blocks editing — remove `-p` in CI.
>
> **B)** A `-p` session starts in Manual permission mode; since nobody in CI can answer the permission prompt, the edits are denied. Add `--allowedTools "Edit"` (or `--permission-mode acceptEdits`).
>
> **C)** `--output-format json` disables editing — use `text`.
>
> **D)** Wrap the command in `timeout 600`.

### Correct Answer: B

**Why B is correct:** `-p` only removes the interactive UI; the permission system keeps working and `-p` starts in Manual mode. When an edit permission is requested and no answer arrives, the action is denied, Claude reports it in text, and the process exits "successfully". In CI, pre-define the work: tools/commands via `--allowedTools`, or the `acceptEdits` / `dontAsk` / `auto` mode.

**Why A is wrong:** Without `-p` the pipeline hangs. `-p` doesn't block editing; permissions do.

**Why C is wrong:** The output format is only how the result is printed; nothing to do with permissions.

**Why D is wrong:** It's not a time issue; the job already finishes. A timeout doesn't approve a denied permission.

---

## Question 10 (Task Statement 3.6)

> A team generates tests automatically in CI with `claude -p "Generate tests for the changed files"`. CLAUDE.md documents the testing standards (vitest, describe/it), valuable test criteria and fixtures; the generated tests are correct in framework and style. But developers complain: "On every PR, Claude re-proposes the very scenarios that already exist in `tests/auth.test.ts` (invalid token, expired session)."
>
> **What are the root cause and the fix?**
>
> **A)** Add a "don't write duplicate tests" rule to CLAUDE.md.
>
> **B)** Claude doesn't see the existing test files — **provide the existing test files in context** (e.g. `@tests/auth.test.ts`, or include the test files of the changed modules in the prompt) so it doesn't propose scenarios already covered.
>
> **C)** Use interactive mode instead of `-p`.
>
> **D)** Structure the output with `--json-schema`.

### Correct Answer: B

**Why B is correct:** The Skills bullet the exam guide counts **separately** from CLAUDE.md: "Providing existing test files in context so test generation avoids suggesting duplicate scenarios already covered by the test suite." CLAUDE.md provides the *rules* (already working here: framework and style are right); only the existing test files show *what's already tested*.

**Why A is wrong:** A "don't write duplicate tests" rule can't be applied if Claude can't see what exists — missing information isn't fixed by a rule.

**Why C is wrong:** Interactive mode hangs in CI; the problem is context, not mode.

**Why D is wrong:** Structured output shapes the *format* of the output; it doesn't prevent duplicate *content*.

---

## Scoring

| Correct | Assessment |
|---|---|
| 10/10 | Domain 3 done — move on to the next domain |
| 8–9/10 | Pass — re-read the task statement of the missed question once |
| 6–7/10 | Re-study the relevant task statement files, retake the exam |
| ≤5/10 | Re-study Domain 3 from the start; especially 3.2 (triggering + `allowed-tools`) and 3.6 (permissions) |
