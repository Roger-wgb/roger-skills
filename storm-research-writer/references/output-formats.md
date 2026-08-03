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

## Final Report

```markdown
# {title}

## Summary
{concise overview}

## Main Analysis
{sectioned body}

## Evidence Notes
{important citations or source notes}

## Limitations
{uncertainty, gaps, weak sources}

## Further Research
{next questions}
```

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
