# Task Statement 5.6: Information Provenance

## Domain 5 — Context Management and Reliability (15% of the Exam)

---

## Core Idea

A multi-agent research system gathers data from 5 different sources and writes a synthesis report. The report is beautifully written, but one claim is being questioned: "Solar energy capacity grew 45%." Which source does this claim come from? When was it published? What was the source's original wording — a definitive measurement or a preliminary estimate?

If this information was lost during synthesis → **the citation is dead**. The reader cannot assess the claim's reliability.

This task statement teaches how to preserve claim-source mappings, how conflicting sources are handled and **by whom**, temporal awareness, and the structure of the report. It shares the same backbone as 5.1's "subagent metadata requirement" item: date, source location, methodology.

Exam scenario: **Multi-Agent Research System**. Exercise 4, steps 18 and 20 are the acceptance criteria for this statement.

---

## Structured Claim-Source Mappings

### Concept

The pieces of information to preserve for each finding (Exercise 4, step 18: "*claim, evidence excerpt, source URL/document name, and publication date*" + the source's own characterization):

| Component | Description | Example |
|---|---|---|
| **Claim** | The statement of the finding | "Solar energy capacity grew 45%" |
| **Source URL** | Link to the original source | "https://iea.org/reports/solar-2024" |
| **Document name** | Title of the source | "IEA Solar Market Report 2024" |
| **Relevant excerpt** | The relevant passage from the source | "Global solar PV capacity additions grew by 45%..." |
| **Publication date** | The source's publication / data collection date | "2024-06-15" |
| **Source characterization** | *How* the source presents the claim | "preliminary estimate" / "measured" / "projected" |
| **Methodology note** | The source's own scope statement | "includes utility-scale and rooftop" |

### Structured Format

```json
{
  "finding": {
    "claim": "Solar energy capacity grew 45% in 2024",
    "source_url": "https://iea.org/reports/solar-2024",
    "document_name": "IEA Solar Market Report 2024",
    "relevant_excerpt": "Global solar PV capacity additions grew by 45% year-on-year (preliminary estimate)...",
    "publication_date": "2024-06-15",
    "source_characterization": "preliminary estimate",
    "methodology_note": "includes utility-scale and rooftop installations"
  }
}
```

### Preservation During Synthesis

Critical rule: Downstream agents **preserve and merge** these mappings. Even if claims are rephrased during synthesis, the source link **and the characterization** must be preserved.

**WRONG — citation lost during synthesis:**
> "The renewable energy sector has seen significant growth. Solar and wind energy investments have increased."

**WRONG — citation present, characterization lost (more insidious):**
> "Solar energy capacity grew 45% [IEA, 2024-06]." — the source said "preliminary estimate"; synthesis upgraded it to a definitive measurement.

**CORRECT — citation and characterization preserved:**
> "According to the IEA's preliminary estimate, solar energy capacity grew 45% [IEA, 2024-06, rooftop included]. Wind energy investments reached $120B [IRENA, 2024-03]."

**Rule:** Synthesis neither **softens** nor **hardens** the source's degree of certainty. Exam guide: "*preserving original source characterizations and methodological context*".

> **Current note (does not change the exam answer):** The Messages API's **Citations** feature (`citations: {enabled: true}` on `document` blocks) enforces citation at the API level for the document analysis subagent — the response comes back with `cited_text` + document index + location; the "excerpt + location" part of the claim-source mapping can be taken from the API instead of a hand-built schema. In Anthropic's research system, a separate **CitationAgent** also determines citation placements as a post-processing step. The guide's answer is structured mapping; this box is about "how to implement it".

---

## Conflict Handling — Who Decides?

### Problem

Two reliable sources report different statistics:

- IEA: "Solar energy capacity grew 45%"
- BloombergNEF: "Solar energy capacity grew 38%"

### Wrong Approach

Picking one arbitrarily — at whatever layer:

- ❌ "Pick the more recent one"
- ❌ "Pick the more reputable source"
- ❌ "Take the average of the two"
- ❌ The document analysis subagent returning a single value with "I think this one is right"

### Correct Approach — three roles

The exam guide's Skills item: "*Completing document analysis with conflicting values included and explicitly annotated, letting the **coordinator** decide how to reconcile **before passing to synthesis***".

| Role | What it does | What it does not do |
|---|---|---|
| **Document analysis subagent** | *Completes* the analysis, **annotates** and returns both values with source, date and methodology note | Does not choose, average, or stay silent |
| **Coordinator** | Makes the reconciliation **decision**: present both / prioritize one by methodology / put in the "contested" section / request additional sources | Does not tell the subagent "pick one" |
| **Synthesis agent** | Writes according to the coordinator's decision; shows **both values with their sources** in the report | Does not reconcile on its own |

The end reader sees both values; but the *decision point in the architecture* is the coordinator — "leave the decision to the reader" alone is not wrong, but incomplete.

```json
{
  "claim": "Solar energy capacity growth in 2024",
  "conflicting_values": [
    {
      "value": "45%",
      "source": "IEA Solar Market Report 2024",
      "publication_date": "2024-06-15",
      "source_characterization": "preliminary estimate",
      "methodology_note": "Includes utility-scale and rooftop installations (source: methodology section, p.4)"
    },
    {
      "value": "38%",
      "source": "BloombergNEF New Energy Outlook",
      "publication_date": "2024-03-20",
      "source_characterization": "measured",
      "methodology_note": "Utility-scale installations only (source: p.2 scope note)"
    }
  ],
  "conflict_status": "unresolved — coordinator decision required",
  "reconciliation_hypothesis": "Scope difference (rooftop inclusion) may explain the gap — hypothesis, not stated by either source"
}
```

**Fabricated rationale warning:** `methodology_note` comes from the sources' *own* statements (with location). A sentence explaining the *reason* for the gap, however, is the synthesis agent's inference — if the source did not say so, it is labeled as a **hypothesis** (`reconciliation_hypothesis`), not written as fact. A sentence like "probably a scope difference", if not grounded in a source, is a doorway to hallucination.

---

## Temporal Awareness

### Problem

Two sources report different numbers, but this is not a conflict — the data is from different times:

- Source A (January 2024): "Unemployment rate 5.2%"
- Source B (June 2024): "Unemployment rate 4.8%"

This is not a conflict, it is change over time. But if the dates are not stated, it looks like a conflict.

### Solution

Make publication/data collection dates **mandatory** in structured outputs (same as the 5.1 subagent metadata item):

```json
{
  "data_points": [
    {
      "metric": "Unemployment rate",
      "value": "5.2%",
      "data_collection_date": "2024-01-15",
      "publication_date": "2024-02-01",
      "source": "National Statistics Office"
    },
    {
      "metric": "Unemployment rate",
      "value": "4.8%",
      "data_collection_date": "2024-06-15",
      "publication_date": "2024-07-01",
      "source": "National Statistics Office"
    }
  ],
  "temporal_note": "Values reflect different collection periods, not conflicting data"
}
```

### Revision ≠ temporal difference — a subtle distinction

| Situation | What is happening | Correct behavior |
|---|---|---|
| **Different periods** | January data measures January, June data measures June | Both values are correct; present with dates, not a conflict |
| **Revision of the same period** | The same institution later corrected the figure for the same period ("2023 emissions 37.4 → 36.8 Gt, revised") | The current (revised) value stands; but add a note "revised, previous value was X" |
| **Different institutions, different methods** | IEA vs BNEF | Conflict handling — the coordinator reconciles |

Without dates, these three situations cannot be distinguished. "The latest data is always correct" applies only to the second row; it is wrong for the first row.

---

## Report Skeleton — Well-Established / Contested / Gaps

The exam guide's Skills item: "*Structuring reports with explicit sections distinguishing **well-established findings from contested ones**, preserving original source characterizations and methodological context*". Exercise 4, step 20 makes this an acceptance criterion.

Combined with 5.3's coverage statements, the synthesis report skeleton has three sections:

```
## 1. Well-Established Findings
Findings where multiple independent sources agree, or a single strong source presents
as a definitive measurement. Each line: source, date, characterization.
- Wind investments $120B [IRENA 2024-03, measured; BNEF 2024-03, measured — consistent]

## 2. Contested Findings
Findings where reliable sources disagree. Both values, source, date, methodology;
the coordinator's reconciliation note and a hypothesis label if any.
- Solar capacity growth: 45% [IEA, preliminary estimate, rooftop included] vs 38% [BNEF, measured,
  utility-scale only] — scope difference hypothesis (sources do not state it)

## 3. Coverage Gaps (5.3)
Areas that remained limited due to inaccessible / missing sources.
- Geothermal: ScienceDirect timeout — single source, limited
```

The answer to the exam's "how should the synthesis report be structured?" question is this trio; "write a single coherent narrative, resolve the conflicts" is a distractor.

---

## Content-Appropriate Rendering

### Problem

Presenting all findings in a single flat format (e.g., always a list, always a table, always paragraphs) leads to information loss. Guide: "*rather than converting everything to a uniform format*".

### Solution

Each content type should be presented in its natural format — and know *what is lost* when you change the format:

| Content Type | Appropriate Format | What is lost when converted to a uniform format |
|---|---|---|
| Financial data | **Table** | In prose, cross-column comparison and units are lost |
| News / developments | **Prose** | In a table, the timeline and cause-effect linkage are lost |
| Technical findings | **Structured list** | In prose, scannability and categorization are lost |

**Rule:** Don't squeeze everything into a single flat format. Present financial data in a table, news in prose, technical findings in a structured list.

---

## Key Takeaways for the Exam

| Concept | Remember |
|---|---|
| Claim-source mapping | Claim + URL + document name + excerpt + date + **source characterization** + methodology |
| Preservation during synthesis | Downstream agents preserve and merge the mappings; neither soften nor harden the characterization |
| Citation death | Without the mapping, the citation is lost during synthesis; losing the characterization is more insidious |
| Conflict — who decides | Subagent annotates, **coordinator reconciles**, synthesis shows both with sources |
| Fabricated rationale | If the reason for the gap isn't in the source, label it `hypothesis`; don't write it as fact |
| Temporal awareness | Different periods → both correct; revision of the same period → current stands + note |
| Date requirement | Publication/data collection date is mandatory in structured output (5.1 metadata) |
| Report skeleton | Well-established / Contested / Coverage gaps (5.3) |
| Content format | Financial → table, news → prose, technical → structured list; a uniform format is information loss |

---

## Practice Scenario 1

> A multi-agent research system is writing an energy sector report. The synthesis agent produces this sentence:
>
> "Notable growth has been observed in the renewable energy sector in recent years. Solar energy capacity has increased significantly."
>
> The reader asks: "By what percentage? Which source? Which year?"
>
> The web search subagent had actually found specific data: 45% according to the IEA report, 42% according to the IRENA report.
>
> **What is the root cause and the solution?**
>
> **A)** Add a "be specific, cite sources" instruction to the synthesis agent's system prompt.
>
> **B)** The data passed from the web search subagent to the synthesis agent has no structured claim-source mappings. Require the subagent output to include claim + excerpt + source/URL + date + characterization; have synthesis preserve these mappings.
>
> **C)** The synthesis agent's context window is small — use a larger model.
>
> **D)** Have a post-synthesis "verification agent" read the report and search the web for a source for each claim.

### Correct Answer: B

**Why B is correct:** Citation death — the web search subagent found specific data but did not pass it to the synthesis agent in a structured format. The solution is at the source: the subagent output schema makes the claim-source mapping mandatory (Exercise 4, step 18), and synthesis preserves it.

**Why A is wrong:** A prompt instruction does not fix a structural problem. If the data arriving at the synthesis agent has no source mapping, saying "cite sources" cannot create the missing data — or worse, it makes the agent fabricate it.

**Why C is wrong:** The problem is not the context window size, it is the data format.

**Why D is wrong:** Searching for sources afterward is an attempt to rediscover the source the subagent *already found*; it carries the risk of linking to the wrong source and doubles the cost. Citations are preserved at generation time, not produced afterward.

---

## Practice Scenario 2

> A research report contains these two findings:
>
> - Source A (IEA, January 2024 publication): "2023 global carbon emissions 37.4 Gt (preliminary estimate)"
> - Source B (IEA, July 2024 publication): "2023 global carbon emissions 36.8 Gt (revised)"
>
> The agent flags this situation as "conflicting data" and cannot decide which value is correct.
>
> **Which is the correct approach?**
>
> **A)** Take the average of the two — 37.1 Gt.
>
> **B)** Present both values as different measurement periods — a temporal difference, not a conflict.
>
> **C)** A revision by the same institution for the same period (2023): the current value (36.8 Gt) stands; present it in the report with the note "revised, preliminary estimate was 37.4 Gt" and both publication dates.
>
> **D)** Remove both sources — conflicting data is unreliable.

### Correct Answer: C

**Why C is correct:** The two values measure *the same period* (2023) and come from the same institution; the second is explicitly "revised". This is neither a conflict nor a temporal difference — it is a revision. The current value stands, but the characterization (preliminary estimate → revised) and both dates are preserved.

**Why A is wrong:** Averaging mixes a preliminary estimate with a revised value; it produces a number no source has stated.

**Why B is wrong:** The exam's subtle trap: "different publication date" ≠ "different period". Both publications measure *2023*. A temporal difference applies when the *data collection period* differs; here the publication date differs, the period is the same.

**Why D is wrong:** Removing data that can be explained by a revision is information loss.

---

## Practice Scenario 3

> A coordinator gives the document analysis subagent the task "extract the sector growth rate". The subagent finds 45% and 38% in two reliable reports, and returns only 45%, saying "IEA is more reliable". The synthesis report writes 45% as the definitive figure; the client points to BNEF's 38% and questions the report.
>
> **Which role behaved incorrectly, and what is the correct flow?**
>
> **A)** The synthesis agent: it should have searched the web for both sources and compared them itself.
>
> **B)** The document analysis subagent: resolving the conflict is not its job. It should annotate both values with source, date, characterization and methodology note and complete the analysis; the coordinator should make the reconciliation decision; synthesis should show both in the "contested findings" section with their sources.
>
> **C)** The coordinator: it should have given the subagent an "always pick the most recent source" rule.
>
> **D)** Nobody is at fault; IEA really is the more reliable source.

### Correct Answer: B

**Why B is correct:** The exam guide's role distribution: the subagent annotates and completes, the coordinator reconciles, synthesis shows both. The subagent returning a single value based on its "more reliable" judgment is an arbitrary choice and hides information from the upper layers.

**Why A is wrong:** The synthesis agent is not the reconciliation layer; moreover, re-searching for a source the subagent already found is wasteful.

**Why C is wrong:** "Most recent" is also an arbitrary selection rule — it makes different methodologies invisible; it is valid only for revisions.

**Why D is wrong:** Even if it were a source reliability judgment, a difference between two reliable sources *cannot be hidden from the reader*; the report must show both in the "contested" section.
