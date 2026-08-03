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
```

## Section Drafting

```text
Topic: {topic}
Section heading: {section_heading}
Section purpose: {section_purpose}
Relevant source notes:
{source_notes}

Draft this section in a neutral, informative style. Use only supported claims. Keep citations or source references attached when required. Do not connect facts unless the sources support the connection.
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
1. Unsupported claims
2. Over-association between unrelated facts
3. Source bias or non-neutral tone
4. Missing major perspectives
5. Weak organization
6. Citations that exist but paraphrase the source inaccurately (separate from missing citations)
7. Undated relative time phrases that will go stale

Return actionable fixes, not a general critique.
```
