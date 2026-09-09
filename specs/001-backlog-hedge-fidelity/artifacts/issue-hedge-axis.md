# Hedge/Qualifier Fidelity Axis: Schema, Metrics, and Test Cases

## Overview

This issue establishes a new measurement axis for hedge and qualifier preservation across the compression pipeline. Currently, the project can score whether facts survive compression but cannot score whether the epistemic status (the certainty, modality, and likelihood qualifications) of those facts is preserved. A hedged claim compressed into a bare assertion scores as perfect retention today. This work defines what it means for a hedge to survive *correctly*, and provides both a deterministic check and a model-judged validation.

### Terminology

To read and implement this issue cold, you need these two definitions:

- **rendered output**: The plaintext outline text produced by running this repository's structured-gist compression skill over a case's `source.md` at a given granularity level (skim, standard, or deep). It is the compressed version of the source, ready to be scored.

- **the harness**: The benchmark scoring pipeline in `skills/structured-gist/benchmarks/semantic-compression/` (orchestrated by `run.py`). It invokes compression on source files, runs metrics against the rendered output, and writes results to `results/deterministic.json` or `results/judged.json`. You do not need to read the harness code to implement this issue — you only need to know that rendered outputs are "the compressed outline text for a case at a given level" and the harness is "the thing that will eventually call these metrics you are defining."

- **`suite.json` case entry**: The harness's case roster is `skills/structured-gist/benchmarks/semantic-compression/suite.json`, shaped `{"cases": [...], "conditions": {}}`. Each entry in `"cases"` is `{"id": "<case-directory-name>", "lane": "deterministic"}` — e.g. an existing entry looks like `{"id": "registrar-hedge", "lane": "deterministic"}`. "Add the case to suite.json's cases list" means appending one such object, with `"id"` matching the case's directory name under `regression/` or `pressure-tests/`.

## Part 1: Gold-Set Schema Changes (T021)

The gold.json schema for each benchmark case must be extended with two new fields. This change is applied consistently across all existing benchmark case files via a migration script (not hand-edited), and all new cases are authored with these fields present from the start.

### 1a. New Fact Category: `epistemic`

Add a new fact category alongside the existing categories (e.g., `outcome`, `descriptive`, `cause_rationale`, `negation`, `failure`). 

**Name**: `epistemic`  
**Weight**: 3 (same as the existing `negation` category — confirm by checking any existing gold.json where `"category": "negation"` has `"weight": 3`)  
**Purpose**: Captures hedges, qualifiers, modal expressions, and epistemic markers that express uncertainty, likelihood, possibility, or non-committal framing of a claim.

**Examples** (illustrative, not exhaustive):
- "likely Squarespace Domains" — epistemic likelihood hedge
- "possibly Google Domains" — epistemic possibility hedge
- "is unconfirmed" — epistemic uncertainty marker
- "might have" — epistemic modal verb
- "probably" — epistemic adverb

### 1a-baseline. Existing Fact Schema (Before This Issue's Changes)

To understand what fields you are extending, here is a complete, real fact record from an existing gold.json file, before any epistemic or attaches_to fields are added:

```json
{
  "id": "f1",
  "text": "Service A's request timeout was decreased from 30 seconds to 5 seconds",
  "category": "outcome",
  "weight": 2.5,
  "precision_sensitive": true,
  "source_quote": "Service A's request timeout was decreased from 30 seconds to 5 seconds"
}
```

This fact comes from `skills/structured-gist/benchmarks/semantic-compression/regression/near-identical-numbers/gold.json`. It shows the baseline structure: every fact has `id`, `text`, `category`, `weight`, optional fields like `precision_sensitive`, and a `source_quote`. When you author new cases or extend existing ones, you will add the two new fields (`attaches_to` and epistemic category support) to records like this one.

**JSON formatting requirement for byte-identical idempotency**: The migration script MUST write JSON files in a fixed, documented format to ensure that running the script twice produces byte-identical output. Use `json.dumps(data, indent=2, sort_keys=False, ensure_ascii=True)` followed by a single trailing newline (Unix line ending). Document this exact convention in the migration script's docstring so that future reruns are checkable byte-for-byte.

### 1b. New Field: `attaches_to` (optional)

Every fact record gains an optional `attaches_to` field that names the fact-id of the claim this qualifier modifies. This field is particularly important for `epistemic` category facts, as it enables detecting when a hedge survives compression but becomes bound to the wrong claim.

**Field name**: `attaches_to`  
**Type**: string (the fact id it modifies, e.g., `"f1"`)  
**Required**: No (omit if the fact does not modify another fact, e.g., stand-alone assertions)  
**Purpose**: When a hedge survives in the rendered output but is now attached to a different claim than its source, the `attaches_to` binding makes that mismatch detectable. A surviving hedge attached to the wrong claim counts as "survived" under the deterministic `hedge_survival_rate` metric but counts as a failure under the judged `caveat_attach_accuracy` metric.

**Example**:
```json
{
  "id": "f10",
  "text": "the registrar is unconfirmed",
  "category": "epistemic",
  "weight": 3,
  "attaches_to": "f1",
  "source_quote": "Registrar is unconfirmed"
}
```

Here, fact f10 (the epistemic hedge) is bound to fact f1 (the claim it qualifies).

### 1c. Application

- Write a migration script (e.g., Python, bash) that adds the schema shape to every existing case's gold.json file. The added shape must be identical across all cases: `"epistemic"` category with `weight: 3`, and an optional `attaches_to` field on every fact record (present but null/absent where not applicable). The script must be deterministic and idempotent: running it twice on the same case produces byte-identical output.
- Document which cases are affected (all eight existing semantic-compression benchmark cases, plus any new cases from step 3).
- All new cases authored in step 3 must be authored with both fields present from the start.

---

## Part 2: Metric Definitions (T022)

Two metrics measure hedge fidelity, operating at different levels of validation:

### 2a. `hedge_survival_rate` (Deterministic, No Model Calls)

**Tier**: Deterministic. No model calls. No human judge. Shippable ahead of the harness rebuild.

**Definition**:

The fraction of source-side hedge occurrences that survive in the rendered output, subject to the following conditions:

1. **Source-side identification**: Use a hedge lexicon to identify all hedge tokens/phrases in the source text. The lexicon is grounded in published linguistics literature on epistemic-hedging taxonomies (hedge markers, modal verbs, epistemic adverbs, approximators, evidential frames) and reviewed by the supervising operator before use.

2. **Binding to retained facts**: For each hedge occurrence in the source, match it against the facts that citation it (via `source_quote` in the gold set). The hedge counts only if the fact it binds to is recorded as retained (not dropped or fully omitted) in the gold scoring.

3. **Rendering-side survival**: Check whether the matched hedge text survives in the rendered outline output using this operational definition: A hedge is considered to survive if *either* (a) the exact hedge token/phrase from the lexicon appears case-insensitively as a substring anywhere in the rendered output's text for the node(s) containing the bound fact, *or* (b) at least one other term from the same lexicon category as the original hedge appears in that node's text (e.g., source hedge was `"likely"`, rendered node contains `"probably"` instead — both are from the `epistemic_adverbs` category, so the epistemic force is preserved even though the exact word changed and the hedge is marked as survived). No paraphrase detection beyond same-lexicon-category substitution is attempted — anything looser (semantic paraphrase without a shared lexicon term) is explicitly NOT counted as survived by this deterministic metric; detecting such loose paraphrases is the job of the separate judged metric `caveat_attach_accuracy`.

4. **Final score**: 
   ```
   hedge_survival_rate = 
     (count of hedges matching retained facts and appearing in rendering) 
     / (count of hedges matching retained facts in source)
   ```

**Important distinction**: This metric counts a hedge as "surviving" even if it has migrated to a different claim than its original attachment (a hedge that originally modified claim f1 but now modifies claim f2 still counts as surviving). This is a deliberate simplification to make the metric deterministic. Detecting incorrect attachment is the job of the separate judged metric below.

**Lexicon specification**:

- **Lexicon location**: `skills/structured-gist/benchmarks/semantic-compression/scoring/hedge_lexicon.json` — this is the canonical, version-controlled lexicon used by all metrics.
- **Current status**: The lexicon is **DRAFT** pending supervising-operator review per this project's redaction/review policy. It MUST NOT be used to score any test case until that review is completed and documented.
- **Structure**: The lexicon is organized into 8 categories, each with a `citation` (one or more academic sources with DOI/URL), a `description`, and a `terms` list. Example categories currently in the lexicon (DRAFT):
  - **`modal_verbs`** (Hyland, 2005): Terms like `might`, `may`, `could`, `should`, `would` — express possibility, probability, or conditionality.
  - **`epistemic_adverbs`** (Lakoff, 1973): Terms like `likely`, `probably`, `possibly`, `perhaps`, `presumably`, `apparently`, `seemingly` — modify the degree of certainty of a proposition.
  - **`approximators`** (Kilicoglu & Bergler, 2011): Terms like `approximately`, `roughly`, `about`, `around`, `almost` — hedge by indicating estimates and non-precise quantities.
  - **`evidential_frames`**, **`knowledge_shields`**, **`tentative_language`**, **`quantifier_hedges`**, **`negation_hedges`**: Five additional categories, each with their own citations and term lists.
- The operator reviews the complete lexicon and may add/remove entries before it is used to score any case.
- Once the review is recorded, the final lexicon is committed to the repository and locked for scoring.

---

### 2b. `caveat_attach_accuracy` (Model-Judged, Sonnet Tier)

**Tier**: Model-judged. Requires Sonnet-tier judgment (escalated from the harness's default tier).

**Definition**:

For each hedge that survives in the rendered output (including the hedges counted by `hedge_survival_rate` above), a Sonnet model judges whether the hedge is **correctly attached to the same claim it modified in the source**, as opposed to surviving but migrating to a different claim.

**Judgment Protocol**:

1. For each test case, extract:
   - The **source excerpt** containing the original claim and its qualifying hedge
   - The **rendered output** for the same conceptual claim area
   
2. Show the judge both the source and the rendered output **side-by-side per claim**. Never show the rendered output alone.

3. The judge answers per hedge: "Is the hedge attached to the correct claim?" Options: `correct`, `incorrect`, `ambiguous` (if the judge cannot determine with confidence).

4. Compute:
   ```
   caveat_attach_accuracy = 
     (count of correct attachments) 
     / (count of correctly-survived hedges that were judged, excluding ambiguous)
   ```

**Judge call shape** (example prompt sent to Sonnet-tier model):

```
SYSTEM: You are checking whether a hedge/qualifier in rendered, compressed text is
still attached to the same claim it modified in the original source.

SOURCE EXCERPT:
The domain registrar is unconfirmed - likely Squarespace Domains (site was built there),
possibly Google Domains legacy or another registrar.

RENDERED OUTPUT (same claim area):
Domain registrar
  - likely Squarespace Domains
  - possibly Google Domains (legacy)
  - unconfirmed

HEDGE UNDER REVIEW: "likely"
CLAIM IT MODIFIED IN SOURCE: "Squarespace Domains is the likely registrar"

QUESTION: In the rendered output, is this hedge (or its lexicon-category
equivalent) still qualifying the SAME claim it modified in the source, or has it
drifted to qualify a different claim, or is it unclear? Answer exactly one of:
correct | incorrect | ambiguous.
```

Each (hedge, case, rendering-level) triple generates one call to the model (Sonnet tier). The response is parsed for the exact word `correct`, `incorrect`, or `ambiguous` (case-insensitive, first matching token) and recorded in the results.

**Why separate from `hedge_survival_rate`?**: The deterministic metric can be fooled by a hedge that survives but migrates. The judged metric is what actually validates correctness of attachment. We measure both because the deterministic metric is cheap and ships early, while the judged metric requires human oversight and can be run later or on a sample.

---

## Part 3: Test Cases (T023)

Three test cases ground the hedging measurement, derived from existing corpus material and subject to redaction review before use.

### Test Case 1: Registrar — Stacked Epistemic Hedge

**Source excerpt** (from real-world corpus, redaction-reviewed and APPROVED):
```
Registrar is unconfirmed - likely Squarespace Domains (site was built there), 
possibly Google Domains legacy or another registrar.
```

**What this tests**: A stacked epistemic hedge — a primary uncertainty marker (`unconfirmed`) followed by a series of qualified alternatives (`likely X, possibly Y, possibly Z`). Tests whether the compression preserves not just the fact itself but the nested epistemic structure (likelihood, possibility, alternation).

**Implementing this test case**: (a) Create or confirm a `gold.json` file for this case under `skills/structured-gist/benchmarks/semantic-compression/pressure-tests/registrar-hedge/` (this directory and its `source.md`, the full un-truncated redaction-APPROVED source message, already exist in this repo — see that directory) containing fact records shaped like the schema examples above (with the new `attaches_to` field for epistemic facts), (b) `source.md` in the same directory already contains the full source text from which these facts are drawn (not just the excerpt above), (c) add the case to `suite.json`'s cases list, (d) no rendering/scoring run is required to close this issue — that happens when the harness (T036+) processes the case; this issue's job is just to get the gold.json file correctly authored and the case registered.

**Schema example** (for reference):
```json
{
  "id": "f_registrar_claim",
  "text": "The domain registrar is one of: Squarespace Domains, Google Domains (legacy), or another registrar",
  "category": "outcome",
  "weight": 2.5,
  "source_quote": "Registrar is unconfirmed - likely Squarespace Domains (site was built there), possibly Google Domains legacy or another registrar"
},
{
  "id": "f_registrar_hedge",
  "text": "the registrar is unconfirmed",
  "category": "epistemic",
  "weight": 3,
  "attaches_to": "f_registrar_claim",
  "source_quote": "Registrar is unconfirmed"
},
{
  "id": "f_registrar_likelihood",
  "text": "Squarespace Domains is the likely registrar",
  "category": "epistemic",
  "weight": 3,
  "attaches_to": "f_registrar_claim",
  "source_quote": "likely Squarespace Domains"
}
```

---

### Test Case 2: Reserved / Dropped Candidate

**Status**: A second corpus candidate was identified and reviewed under this project's redaction process. It was **DROPPED** and is not usable anywhere in the repository, issue comments, or examples.

**Reason**: The excerpt named a real third-party individual and linked them to personal contact information (specifically, a personal phone number). This falls squarely within the project's redaction policy (personal names, phone numbers, account identifiers, or URLs containing them).

**Consequence**: Per the project's design decision (documented in `specs/001-backlog-hedge-fidelity/redaction-log.md`), no fallback candidate is sought when an excerpt is DROPPED. The new issue proceeds with two test cases instead of three, and this omission is by design, not an oversight.

**Implementing this test case**: No implementation action for this case — it is intentionally absent; this section exists only to record why. The section remains here for transparency and to document the redaction decision.

---

### Test Case 3: Deontic Modality — Obligation and Permission Hedging

**Source**: Reframing of GitHub issue #8 in this repository (domattioli/structured-gist).

**What is deontic modality?** Deontic language expresses obligation, permission, requirement, or lack thereof. Examples: "must," "should," "ought," "may," "can," "permitted," "required," "forbidden." These are distinct from epistemic hedges (which express likelihood and certainty) but function similarly: they qualify and temper a claim by expressing what is required vs. optional vs. prohibited.

**Use case** (paraphrased from issue #8): 

Issue #8 proposes exploring whether agent-facing documentation (like `SKILL.md`) should be authored in structured-gist's outline format. The proposal contains classic deontic modality:
- **"should be authored"** — obligation/recommendation
- **"might help"** — tentative modal (weaker commitment than "will help")
- **"not in scope for this issue"** — prohibition/constraint
- **"should be discussed"** — requirement before action

**Concrete test case**:

Construct an outline about a technical requirement with interspersed deontic-modality hedges. Example:

```
# Proposed Design: Documentation Restructuring

Policy
  - Documentation MUST be authored in outline format
  - Agent-facing rules SHOULD be tabular, not prose
  - Complex examples MAY remain in prose if tabular form loses nuance
  
Rationale
  - Outline format might improve agent rule-following accuracy
  - Terse nodes might cause structure loss unless rules are inherently list-shaped
  - Not a commitment: this requires measurement before adoption

Out of scope for this experiment
  - Rewriting unstructured prose narratives into outlines
  - Changing SKILL.md itself until measurement is complete
```

**Gold schema** (for reference):
```json
{
  "id": "f_policy_must",
  "text": "Documentation MUST be authored in outline format",
  "category": "outcome",
  "weight": 2.5,
  "source_quote": "Documentation MUST be authored in outline format"
},
{
  "id": "f_modality_must_marker",
  "text": "the requirement is mandatory (MUST)",
  "category": "epistemic",
  "weight": 3,
  "attaches_to": "f_policy_must",
  "source_quote": "MUST"
},
{
  "id": "f_policy_should",
  "text": "Agent-facing rules SHOULD be tabular",
  "category": "outcome",
  "weight": 2.5,
  "source_quote": "Agent-facing rules SHOULD be tabular"
},
{
  "id": "f_modality_should_marker",
  "text": "the recommendation is less binding than MUST (SHOULD)",
  "category": "epistemic",
  "weight": 3,
  "attaches_to": "f_policy_should",
  "source_quote": "SHOULD"
},
{
  "id": "f_policy_may",
  "text": "Complex examples MAY remain in prose",
  "category": "outcome",
  "weight": 2.5,
  "source_quote": "Complex examples MAY remain in prose"
},
{
  "id": "f_modality_may_marker",
  "text": "the option is permissive, not required (MAY)",
  "category": "epistemic",
  "weight": 3,
  "attaches_to": "f_policy_may",
  "source_quote": "MAY"
}
```

**What this tests**: Whether deontic-modality hedges (obligation/permission) are preserved when claims are compressed. Unlike epistemic hedges (likelihood), deontic hedges alter the *normative force* of a claim. Compressing "Documentation MUST be in outline format" to "Documentation is in outline format" loses the obligation signal. This test case ensures the compression preserves obligation/permission gradations (MUST vs. SHOULD vs. MAY), not just likelihood hedges.

**Implementing this test case**: (a) Create or confirm a `gold.json` file for this case under `skills/structured-gist/benchmarks/semantic-compression/pressure-tests/deontic-modality/` containing fact records shaped like the schema examples above (marking MUST/SHOULD/MAY qualifiers as `epistemic` category facts with `attaches_to` fields pointing to the policy claims they modify), (b) ensure `source.md` in the same directory contains the full design proposal or policy text from which these facts are drawn, (c) add the case to `suite.json`'s cases list, (d) no rendering/scoring run is required to close this issue — that happens when the harness (T036+) processes the case; this issue's job is just to get the source+gold files correctly authored and registered.

---

## Acceptance Criteria

- [ ] The gold-set migration script adds `"epistemic"` category (weight 3) and optional `"attaches_to"` field to all eight existing benchmark case files.
- [ ] Both schema changes produce byte-identical output when the script is run twice on the same input (idempotency).
- [ ] The `hedge_survival_rate` metric is implemented as a deterministic, source-text-aware comparison requiring no model calls. It is shippable ahead of the harness rebuild.
- [ ] The hedge lexicon is grounded in published references, documented with URLs per entry or entry cluster, and reviewed by the supervising operator before use.
- [ ] The `caveat_attach_accuracy` metric is implemented with Sonnet-tier judgment, showing source + rendered output side-by-side per claim.
- [ ] All three test cases (registrar, dropped status, deontic modality) are in the repository and traceable back to this issue.
- [ ] A reader encountering this issue text alone, without access to the spec or prior sessions, can implement all schema changes, both metrics, and all test cases directly from this text.

---

## References

- Spec: `specs/001-backlog-hedge-fidelity/spec.md` (requirements FR-006 through FR-009a, FR-022, FR-026)
- Redaction log: `specs/001-backlog-hedge-fidelity/redaction-log.md` (APPROVED and DROPPED verdicts)
- Reframed issue: GitHub issue #8 (deontic modality content repurposed as test case 3)
- Gold-set schema: `skills/structured-gist/benchmarks/semantic-compression/regression/near-identical-numbers/gold.json` (confirm existing `negation` weight = 3)
