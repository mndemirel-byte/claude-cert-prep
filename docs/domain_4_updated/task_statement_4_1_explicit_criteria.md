# Task Statement 4.1: Explicit Criteria

## Domain 4 — Prompt Engineering and Structured Output (20% of the Exam)

---

## Core Idea

When directing a Claude agent for tasks like code review, security scanning, or document analysis, the most common mistake is this: **giving vague, subjective instructions.**

> *"Only report important findings."*
> *"Be conservative when you're not confident."*
> *"Only flag high-confidence issues."*

These instructions **do not work.** Claude has no reason to understand "important" or "high confidence" the way you mean it.

The right approach: **Categorical, concrete criteria.** Tell Claude **what it should do**, not "what it should feel."

> **Exam term:** The exam guide calls this wrong approach **"confidence-based filtering"** and calls the right approach "specific categorical criteria." When you see "skip if unsure," "report high-confidence findings," or "be conservative" in the answer choices, they are all the same distractor: confidence-based filtering.

> **Official prompting principle (the golden rule):** Show your prompt to a colleague who has very little context about the task and ask them to carry it out. If they get confused, Claude will get confused too. Be specific about the desired output format and boundaries; if the order or completeness of steps matters, use numbered steps. (The course's *Being clear and direct* / *Being specific* lessons.)

---

## Vague vs. Explicit Criteria — Side by Side

### ❌ Vague (Wrong Answer on the Exam)

```
"Only report high-confidence findings. When you are not sure,
prefer to be conservative. Skip trivial issues."
```

**Why it doesn't work:**
- "High confidence" is not a numeric threshold; Claude sets a different bar every time
- "Trivial" is a subjective concept; Claude has no access to the business context
- Vague instructions produce **inconsistent output** — same code, different findings on different runs
- "Be conservative" **does not increase precision** — the model simply reports less; it skips real findings, not just false positives

### ✅ Explicit (Correct Answer on the Exam)

```
"Only flag the following cases:
- The claimed behavior contradicts the actual code behavior
- A security vulnerability exists (injection, authentication bypass, explicit data leak)
- There is a clear logic error (wrong loop condition, null pointer risk)

SKIP the following:
- Minor style preferences (whitespace, naming conventions)
- Team-internal local patterns (local patterns — patterns accepted in this
  codebase that look like bugs from the outside but are deliberate choices)
- Performance improvement suggestions (unless a critical bottleneck)"
```

**Why it works:**
- Each rule is a **decision-tree node** — Claude either flags or skips, no interpretation
- The same code produces **consistent results** every time
- There is no gray area that requires human review

**Exam language:** report → *bugs, security*; skip → *minor style, local patterns*. The concept of "local patterns" (acceptable code patterns) shows up again in Task 4.2 with a few-shot example: "acceptable code patterns vs genuine issues".

---

## The False-Positive Trust Problem — The Exam's Favorite Trap

Understand this topic well: **the exam tries to mislead you here.**

### Scenario

You have a code review agent in a CI/CD pipeline. The agent reports three categories:
- **Security vulnerabilities** → 95% accuracy
- **Logic errors** → 90% accuracy
- **Documentation gaps** → 40% accuracy (too many false alarms)

Developers noticed that half of the "documentation gaps" findings are nonsense. What happens next?

**The real problem:** Developers now **look at security vulnerability findings with suspicion too.** When one category loses trust, the entire agent output looks unreliable.

### The Wrong Answers the Exam Offers

- *"Make all categories more conservative"* — No, this misses real issues
- *"Raise the confidence threshold for the documentation category"* — Vague, doesn't work (confidence-based filtering)
- *"Retrain the agent completely"* — Disproportionate, slow solution
- *"False positives are harmless, the developer filters them anyway; report everything"* — No; the cost of a false positive is precisely **loss of trust**, and that loss renders the accurate categories useless too

### ✅ The Correct Solution

**Temporarily disable the high-false-positive category** and preserve trust in the other categories while you improve that category's prompt.

```
Steps:
1. Remove the "documentation gaps" category from the pipeline
2. The security and logic categories keep running normally
3. Write new, explicit criteria for documentation (as below)
4. Measure on a labeled test set → Add it back once the false-positive rate is acceptable
```

**Core principle:** The fastest way to regain trust is to isolate the poorly performing component.

### How do you decide to "add it back"? — Eval

Step 4 is decided by measurement, not intuition. The essence of the course's *Prompt Evaluation* module:

```
1. Prepare a labeled test set: 50–100 real code snippets, each with a
   human-provided answer to "is there really a finding in this category?"
2. Run the agent with the new criteria on this set
3. Compute the false-positive / false-negative rate
   - Code-based grading: compare the output against the expected set of findings
   - Model-based grading: a second Claude scores the accuracy of the findings
4. Re-enable the category once it passes the threshold; if it doesn't, rewrite the criteria and measure again
```

The same labeled set is also used in Task 4.6 to calibrate confidence thresholds and in Task 4.5 to validate the prompt before a large batch — this is the horizontal theme of Domain 4: **don't roll a change back or forward without measuring it.**

---

## Severity Calibration — With Code Examples

The exam tries to mislead you here too: when it says *"Define severity levels,"* it offers you answers containing **prose descriptions**.

The correct answer always contains **real code examples**.

### ❌ Wrong Calibration (Prose Description)

```
"Critical: Issues that could crash the system or leak data.
Major: Bugs affecting important functionality.
Minor: Small issues."
```

**Why it doesn't work:** Claude's definition of "could crash the system" may not match yours.

### ✅ Correct Calibration (With Code Examples)

```python
# CRITICAL — always report:
def get_user(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"  # SQL injection
    # → Directly exposed to database attack

password = "admin123"  # Hardcoded credential in code
# → Credential leak

# MAJOR — report:
def calculate_total(items):
    total = 0
    for i in range(len(items) + 1):  # Off-by-one error
        total += items[i]

# MINOR — skip:
def getUserData():  # Should be snake_case instead of camelCase
    pass  # Style only; does not affect functionality
```

**Why it works:** Claude no longer interprets on its own — it checks "does this look like that code?"

### How is it embedded in the prompt? — `<example>` tags

In a real prompt, the code examples above are wrapped in XML tags so they are separated from the instructions (official prompting guide; the course's *Structure with XML tags* lesson). Otherwise the model may mistake the example for "the code to be reviewed."

```xml
<severity_examples>
<example severity="critical">
query = f"SELECT * FROM users WHERE id = {user_id}"
<why>User input is embedded directly into SQL → injection</why>
</example>
<example severity="major">
for i in range(len(items) + 1): total += items[i]
<why>Off-by-one: the last iteration raises IndexError</why>
</example>
<example severity="minor">
def getUserData(): ...
<why>Naming style only; behavior is correct → SKIP</why>
</example>
</severity_examples>
```

This structure is identical to Task 4.2 (few-shot) — severity calibration is actually a special case of few-shot.

---

## Key Takeaway List

| # | Key Takeaway |
|---|---------------|
| 1 | **Vague instructions → inconsistent output.** "Be conservative" is not an instruction, it's a wish. Exam name: *confidence-based filtering*. |
| 2 | **Explicit criteria = decision tree.** Each rule resolves to "flag" or "skip." Report: bugs, security. Skip: minor style, local patterns. |
| 3 | **Loss of trust in one category affects the entire agent.** Trust is holistic, not category-specific. |
| 4 | **Solution: Disable the problematic category**, improve it, measure on a labeled set, add it back. Don't slow down the whole system. |
| 5 | **For severity calibration, use real code examples, not prose** — inside `<example>` tags. |
| 6 | **The cost of a false positive is trust; the cost of a false negative is a missed bug.** Explicit criteria reduce both; a confidence threshold only trades one for the other. |

---

## Practice Questions and Answer Explanations

### Question 1

A security scanning agent sometimes fails to report real vulnerabilities and sometimes issues trivial warnings. The developer writes: *"Only report real security issues; skip if you're not sure."* Is this sufficient?

**A)** Yes, the concept of a "real security issue" is clear enough for Claude  
**B)** No, "real" and "if you're not sure" are subjective phrases; categorical criteria are needed  
**C)** No, but adding a confidence threshold to the prompt ("don't report below 80%") solves the problem  
**D)** Yes, Claude calibrates well in the security domain  

**✅ Answer: B**

*Explanation:* The phrases "real security issue" and "if you're not sure" are subjective. Claude may set a different bar on every run. The right approach: categorical criteria such as "SQL injection, credential hardcoding, authentication bypass — report these. Deprecation warnings, performance suggestions — skip these." (C) is the percentage version of confidence-based filtering — the model's own confidence estimate is not calibrated, and the threshold only leads to reporting less; it cannot solve both the "real vulnerabilities are missed" and the "trivial warnings" problems at the same time.

---

### Question 2

A pipeline has three analysis categories: security (92% accuracy), performance (88% accuracy), code style (35% accuracy). Developers are starting to lose trust in the security findings. What is the best action?

**A)** Raise the thresholds of all categories above 90%  
**B)** Temporarily disable the code style category, keep running the others  
**C)** Replace the agent with a larger model  
**D)** Collect more sample data for all three categories  

**✅ Answer: B**

*Explanation:* The problem is that the code style category is poisoning trust. The solution is isolation: remove the bad category, let the good categories keep running. Raising thresholds (A) misses real issues. Changing the model (C) is disproportionate. Collecting more data (D) doesn't address the root cause — the problem is the prompt criteria.

---

### Question 3

Which is the most effective definition for severity levels?

**A)** "Critical: Issues that threaten system security. Major: Bugs that break important functionality."  
**B)** A scheme showing each level with concrete code examples: "Critical: injection patterns like `query = f"SELECT * FROM users WHERE id = {user_id}"`"  
**C)** A percentage confidence threshold for each level: "Critical: 95%+, Major: 80-95%"  
**D)** General descriptions compiled from developers' past review notes  

**✅ Answer: B**

*Explanation:* Prose descriptions (A) are open to interpretation. Confidence thresholds (C) yield inconsistent calibration. Past notes (D) are unstructured. Real code examples make Claude ask "does this look like that code?" — no interpretation, just pattern matching.

---

### Question 4

An agent is given this instruction: *"Only report high-priority issues."* Which problem arises?

**A)** The agent doesn't run; "high priority" is not a valid parameter  
**B)** The agent reports everything and does no filtering  
**C)** Because "high priority" is subjective, it produces inconsistent results across runs  
**D)** The agent returns an incorrect error message  

**✅ Answer: C**

*Explanation:* Claude runs and does filter, but sets the "high priority" threshold differently each time. The same codebase may produce different findings. Inconsistency is the real cost of vague criteria.

---

### Question 5

Last month the instruction *"don't report if you're not sure"* was added to a code review agent. False positives decreased, but developers now notice that two SQL injections that surfaced in production were never flagged in PR review. What happened, and what should be done?

**A)** The instruction worked; a separate "always report" exception should be added for injections, and the rest stays the same  
**B)** The confidence threshold filtered out real findings along with the false positives; the instruction should be removed and replaced with categorical criteria (injection, credential, auth bypass → report; style, suggestions → skip)  
**C)** Model capacity is insufficient; a larger model should be used  
**D)** The instruction should be changed to "if you're not sure, route to human review"  

**✅ Answer: B**

*Explanation:* The classic result of confidence-based filtering: the model sets its own "being sure" bar and simply reports less — you cannot control which findings get dropped. (A) patches the symptom; every newly missed bug requires a new exception, and the underlying vague instruction remains. (C) the problem is not capacity, it's criteria. (D) preserves the phrase "if you're not sure"; routing (Task 4.6) is placed *on top of* categorical criteria, not in place of them.
