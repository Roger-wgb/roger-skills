# Output Formats

Use these templates when the user does not provide a required structure.

## Choosing A Template

- Outline only, no annotation needed: plain heading-only Markdown (see the Draft/Refine Outline prompts in prompts.md) — skip the templates below.
- Outline as an annotated planning artifact: Article Outline below.
- Wikipedia-style or other cited long-form article: Cited Article below.
- Analytical report, not encyclopedia-style: Final Report below.
- Everything else: pick the closest matching template below and adapt field names to the task.

## Research Brief

```markdown
# Research Brief: {topic}

## Goal
{output goal, audience, scope}

## Depth Contract
- Intended decisions:
- Expected treatment:
- Useful evidence mix:
- Localization needs:
- Length constraint, if any:

## Perspectives
- {perspective}: {why it matters}

## Key Questions
- {question}

## Source-Grounded Notes
### {theme}
- Claim: {supported claim}
  Source: {source}
  Type: {fact | interpretation | inference | dispute | gap}

## Coverage Gaps
- {gap and suggested follow-up}

## Suggested Outline
{outline}
```

## Research Readiness

Use this for the semantic gate before locking a deep refined outline. `PASS` means the evidence is ready for the declared scope, not that all possible information has been exhausted.

```markdown
# Research Readiness: {topic}

## Decision
{PASS | BLOCKED}

## Core Question Status
- Question:
  Status: {verified | supported | inference | disputed | gap | downgraded}
  Evidence:
  Remaining issue:

## Perspective Coverage
- Perspective:
  Contribution:
  Sources:
  Missing or overrepresented:

## Contradiction Map
- Competing claims:
  Stronger evidence and why:
  Resolution status:
  Follow-up performed:

## Source Portfolio
- Authority and source-type mix:
- Interested-source concentration:
- Localization coverage:

## Blocking Gaps
- {none, or gap plus required action}

## Stopping Rationale
{why another focused round is or is not likely to change a core answer or the outline}
```

## Article Outline

```markdown
# {topic}

## 1. Lead / Overview
- Purpose:
- Key points:
- Source support:

## 2. Background
- Purpose:
- Key points:
- Source support:

## 3. {Topic-specific section}
- Purpose:
- Key points:
- Source support:

## Coverage Gaps
- {gap}
```

## Cited Article

Use this as the default shape for a Wikipedia-style or other long-form article that requires inline citations. Unless the user specifies a different citation style, use numbered bracket citations, matching how STORM's own output renders sources.

Length targets given by the user refer to body prose (lead + sections), not the References list or headings. Do not include sections like "Limitations" or "Further Research" here — those belong to the Final Report template, not a Wikipedia-style article; keep weak-source caveats inline in the prose instead (e.g., "according to one report...").

```markdown
# {topic}

{Lead/summary paragraph — write this last, after the body sections below, and only cite facts here that are not already cited in the body}

## {Section heading}
{Body prose. Attach a citation marker like [1] immediately after the sentence or clause it supports. A sentence with multiple supporting sources can stack markers: [1][2].}

## {Next section heading}
...

## References
1. {Source title or description} — {author or organization, if known} — {date, if known} — {URL or local file path}
2. ...
```

## Source Notes

```markdown
# Source Notes: {topic}

## {source title}
- Author / organization:
- Date:
- URL or file:
- Reliability:
- Relevant claims:
- Useful for sections:
- Caveats:
```

## Section Evidence Packets

Copy the refined outline's complete heading tree verbatim. Add the following packet under every leaf heading. Keep mechanisms, cases, comparisons, and action implications optional unless they serve the section purpose and reliable evidence exists.

```markdown
# Section Evidence: {topic}

{copy the refined outline heading tree verbatim}

{under each leaf heading:}

- Purpose:
- Key questions:
- Claims and types:
  - Claim:
    Type: {fact | interpretation | inference | dispute | gap}
    Evidence:
- Material disagreement / uncertainty:
- Boundary / gap:
- Depth: {brief | standard | deep}
- Optional mechanism:
- Optional case or comparison:
- Optional implication:
```

## Final Report

```markdown
# {title}

## Summary
{concise overview}

{copy every substantive heading from refined-outline.md verbatim, preserving level and order; fill each leaf section rather than replacing the heading tree with a generic "Main Analysis" section}

## Evidence Notes
{important citations or source notes}

## Limitations
{uncertainty, gaps, weak sources}

## Further Research
{next questions}
```

`Summary`, `Evidence Notes`, `Limitations`, `Further Research`, and reference sections are standard scaffolding and may be added even when absent from the refined outline. All other substantive headings must come from the locked refined outline unless that outline is revised and revalidated first.

## Verification Report

```markdown
# Verification Notes

## Unsupported Or Weak Claims
- Claim:
  Issue:
  Fix:

## Over-Association Risks
- Passage:
  Risk:
  Fix:

## Missing Perspectives
- Perspective:
  Why it matters:

## Source Quality Issues
- Source:
  Concern:
  Replacement or caveat:
```

## Final Quality Review

Use this semantic gate for deep final writing. A critical failure in any required dimension blocks delivery. Do not infer `PASS` from word count, citation count, or the structure lint result.

```markdown
# Final Quality Review: {topic}

## Decision
{PASS | BLOCKED}

## Depth Contract Fit
- Intended decisions served:
- Expected treatment delivered:
- Material shortfall:

## Quality Dimensions
- Coverage: {PASS | BLOCKED} — {reason}
- Explanatory depth: {PASS | BLOCKED} — {reason}
- Grounding and citation entailment: {PASS | BLOCKED} — {reason}
- Disagreement preservation: {PASS | BLOCKED} — {reason}
- Organization and proportionality: {PASS | BLOCKED} — {reason}
- Source quality and neutrality: {PASS | BLOCKED} — {reason}
- Time-sensitive phrasing: {PASS | BLOCKED} — {reason}
- Over-association: {PASS | BLOCKED} — {reason}
- Decision usefulness, when required: {PASS | BLOCKED | N/A} — {reason}

## Required Revisions
- {none, or concrete revision}
```
