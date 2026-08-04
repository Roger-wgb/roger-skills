# Prompt Templates

Adapt these templates to the current agent environment. Do not include secrets, credentials, API keys, or private tokens in prompts.

## Perspective Discovery

```text
Topic: {topic}
Output goal: {output_goal}
Audience: {audience}

Identify {n} distinct research perspectives that would help produce a broad, well-organized, source-grounded treatment of this topic.

Include one "basic facts" perspective. For each perspective, provide:
- Name
- Why it matters
- What kinds of questions it should ask

Avoid duplicative or generic perspectives.
```

## Related Topic Survey

```text
Topic: {topic}

List related topics, comparable cases, or adjacent articles that could reveal useful article structure. For each, explain which sections or angles may transfer to this topic.

Do not claim the related topics are sources of fact unless they are actually inspected.
```

## Perspective-Guided Questions

```text
Topic: {topic}
Perspective: {perspective_name}
Perspective goal: {perspective_goal}
Known notes: {brief_notes}

Generate {k} research questions from this perspective. Questions should help build a strong outline or source-grounded draft.

Prefer questions about mechanisms, chronology, evidence, tradeoffs, disputes, and under-covered details. Avoid only basic who/what/when questions unless they are necessary.
```

## Follow-Up Questions

```text
Topic: {topic}
Perspective: {perspective_name}
Question asked: {question}
Source-grounded answer: {answer}
Current gaps: {gaps}

Generate up to {k} follow-up questions that would improve depth, accuracy, or coverage. Only ask follow-ups that are likely to change the outline or final writing.
```

## Contradiction Mapping

```text
Topic: {topic}
Perspective-grounded findings:
{findings}

Map only material disagreements:
- Which sources or perspectives make conflicting claims?
- What exact claim does each side make?
- Which side has stronger evidence, and why?
- What question would most reduce the important uncertainty?
- What do credible opposing sources agree on?
- Which relevant perspective or issue is still missing?

Do not manufacture conflict when authoritative evidence is one-sided. Preserve unresolved disagreement instead of averaging it into consensus.
```

## Source-Grounded Answer

```text
Topic: {topic}
Question: {question}
Sources:
{source_summaries}

Answer the question using only the provided sources. Structure the answer as:
- Supported answer
- Key evidence
- Disagreements or uncertainty
- Missing information

Mark any inference clearly. Do not invent facts or citations.
```

## Research Note Synthesis

```text
Topic: {topic}
Question-answer notes:
{notes}

Synthesize the notes into a concise research brief. Group findings by theme. Preserve source attribution for important claims. Separate facts, interpretations, disputes, and open questions.

Use categorical status labels where useful: verified, supported, inference, disputed, gap, or downgraded. Preserve material disagreements. Include a non-obvious connection only when a source explicitly supports it or when you provide a transparent reasoning chain and label it as inference; otherwise keep the facts separate.
```

## Research Readiness Review

```text
Topic: {topic}
Depth contract: {depth_contract}
Core questions: {core_questions}
Research brief: {research_brief}
Contradiction map: {contradiction_map}
Source portfolio: {source_portfolio}
Latest follow-up findings: {latest_follow_up}

Decide PASS or BLOCKED for locking a refined outline.

Check:
1. Every core question is supported, explicitly inferred from supported premises, disputed, or an explicit gap.
2. Every material perspective contributed source-grounded findings or is recorded as missing.
3. Important contradictions were investigated and retained when unresolved.
4. Source authority, type diversity, interested-source concentration, and localization fit the claims.
5. The proposed scope can be supported without padding, invented examples, or unsupported connections.
6. Another focused follow-up is unlikely to change a core answer or the outline.

Do not pass based on a raw source count. If BLOCKED, state whether to research further, narrow a claim, mark a gap, or revise scope. Return the Research Readiness template from output-formats.md.
```

## Draft Outline (Background Knowledge Only)

```text
Topic: {topic}
Output type: {output_type}
Audience: {audience}

Without using any research notes, sketch a multi-level outline for this topic based on background knowledge of what a strong reference treatment of this subject would typically cover.

Requirements:
- Use "#" for section titles, "##" for subsections, and so on.
- Include only headings, no other content.
- This is a draft framework, not a final structure — it will be refined against research next.
```

## Refine Outline (With Research)

```text
Topic: {topic}
Output type: {output_type}
Audience: {audience}
Draft outline:
{draft_outline}
Research brief:
{research_brief}

Revise the draft outline using the research brief. Requirements:
- Add topic-specific sections the draft missed.
- Reorder or rename sections to match what the research actually supports.
- Drop or flag sections the research brief cannot support.
- Cover the topic broadly and proportionately.
- Organize from orientation to details to implications.
- Include a final "Coverage gaps" section if important gaps remain.
- Keep the number and granularity of sections proportionate to the available evidence; do not create many thin leaf sections merely to look comprehensive.
```

## Section Evidence Packet

```text
Topic: {topic}
Depth contract: {depth_contract}
Locked refined outline: {refined_outline}
Research brief: {research_brief}
Source notes: {source_notes}
Contradiction map: {contradiction_map}

Copy the complete refined-outline heading tree verbatim. Under every leaf heading, create a packet with:
- Purpose
- Key questions
- Claims, each with type and exact evidence
- Material disagreement or uncertainty
- Boundary or evidence gap
- Intended depth: brief, standard, or deep

Add a mechanism, case, comparison, or action implication only when it serves that section and reliable evidence exists. Do not invent content to fill the packet. If a leaf section is not writable, return BLOCKED and recommend more research or an explicit outline revision.
```

## Section Drafting

```text
Topic: {topic}
Section heading: {section_heading}
Section purpose: {section_purpose}
Locked outline path or heading tree: {refined_outline}
Relevant source notes:
{source_notes}
Section evidence packet:
{section_evidence_packet}
Declared depth:
{declared_depth}

Draft only the requested section under its exact locked-outline heading. Do not rename it, merge it into another section, introduce a new substantive heading, or omit planned child headings. Match the declared depth. Where relevant, develop a core judgment through explanation or mechanism, evidence, case or comparison, material counterpoint, boundary, and implication; use only the elements that fit the section. Keep citations attached to the claims they support. Do not connect facts unless a source supports the connection or a transparent reasoning chain is labeled as inference. If the packet cannot support the section, write an explicit evidence gap or stop and request an outline revision.
```

## Lead / Summary Synthesis

```text
Topic: {topic}
Drafted sections:
{drafted_sections}

Write a concise lead/summary section that accurately reflects what the drafted sections actually say. Do not introduce claims that are absent from the drafted sections. Avoid undated relative time phrases ("currently", "as of now") — use a specific date or omit the time reference.
```

## Verification

```text
Topic: {topic}
Output:
{output}
Source notes:
{source_notes}

Review the output for:
1. Structure drift from the refined outline: missing, renamed, merged, added, reordered, level-changed, or empty sections
2. Unsupported claims
3. Over-association between unrelated facts
4. Source bias or non-neutral tone
5. Missing major perspectives
6. Weak organization
7. Citations that exist but paraphrase the source inaccurately (separate from missing citations)
8. Undated relative time phrases that will go stale
9. Material disagreements, evidence downgrades, or missing perspectives erased during synthesis
10. Thin core sections that state definitions or recommendations without the explanation required by the depth contract
11. Disproportionate treatment, excessive headings, padding, or repetition
12. Decision usefulness for analytical output, when requested

Return actionable fixes, not a general critique.
```

## Final Quality Gate

```text
Topic: {topic}
Depth contract: {depth_contract}
Refined outline: {refined_outline}
Section evidence packets: {section_evidence}
Final draft: {final_draft}
Source notes: {source_notes}

Return the Final Quality Review template from output-formats.md and decide PASS or BLOCKED.

Evaluate coverage, explanatory depth, grounding and citation entailment, disagreement preservation, organization and proportionality, source quality and neutrality, time-sensitive phrasing, over-association, and decision usefulness when required. A critical failure blocks delivery. Treat section length, citation density, and repeated phrasing only as warning signals; none proves depth. If BLOCKED, provide concrete revisions and review again after they are applied.
```
