# Workflow

Use the smallest version of this workflow that satisfies the user's request. For quick tasks, stop after the outline. For deep research, complete all phases.

## Scaling Depth

"Quick" and "deep" change how much each phase costs, not which phases run. Even a quick outline-only request still passes through perspectives, questions, and the two-stage outline (Phase 7) — the difference is how much actual retrieval and note-taking happens at each step:

- Quick (e.g., "just give me an outline", a general or well-known topic, no sources provided): keep perspectives to 1 basic + 2-4 others and ask 1-3 questions per perspective. This rule overrides the larger Phase 2 and Phase 3 defaults. Answer from background knowledge instead of running new searches unless the topic is unfamiliar or time-sensitive, skip follow-up rounds, and label any concrete unsourced claims as provisional. Phase 4's source-record requirements apply only if retrieval is actually performed. Treat the resulting notes — however thin — as the input to the outline refinement step (Phase 7.2). This still produces a two-stage outline; the draft and refined versions simply differ less when little new information came in.
- Deep (e.g., "research X", citations required, a niche or fast-changing topic, a long-form draft requested): use the full 4-7 perspectives, run real searches per question, do 1-2 follow-up rounds, and let the refined outline differ substantially from the draft.

If it is genuinely unclear which mode the user wants, ask once rather than guessing.

## Persisting Intermediate State

A deep run generates a lot of intermediate text — perspective lists, per-question notes, source notes, the synthesized brief, and the outline. Holding all of it in the conversation crowds out the context the drafting phase needs, and loses everything if the run is interrupted.

For deep runs (multiple perspectives, real retrieval, a long draft), write these artifacts under a task-specific `.storm-research/<topic-slug>-<date-or-task-id>/` directory, using stable names such as `draft-outline.md`, `source-notes.md`, `research-brief.md`, and `refined-outline.md`. Never overwrite an existing task directory; choose a new suffix. Use the `Source Notes` and `Research Brief` templates in `references/output-formats.md`, then read the files back when synthesizing (Phase 6) and drafting (Phase 8). If the environment is read-only, keep the artifacts in context and tell the user that the run is not resumable from files.

Quick runs can stay in-context; the overhead of files is not worth it when little new information is gathered.

## Phase 1: Frame The Task

Clarify or infer:

- Topic
- Output type: outline, research brief, report, course framework, article, literature summary, or final draft
- Audience and depth
- Language
- Source and citation requirements
- Constraints: length, deadline, domain, format, forbidden sources
- Applicable country, region, or jurisdiction when it can change legal, policy, medical, financial, safety, or enterprise-governance conclusions

If ambiguity affects correctness or scope, ask. Otherwise state assumptions and proceed.

If the requested output needs an outline, create the background-only draft outline immediately after framing, before reading research notes or starting retrieval. Keep it as an internal artifact unless the user asks to see both versions. This ordering makes the first stage auditable instead of asking a single context to "forget" research it has already seen.

## Phase 2: Discover Perspectives

For deep mode, generate one basic perspective plus 4 to 7 additional perspectives. Quick mode uses the smaller range defined under Scaling Depth.

Use these sources for perspective discovery, in this order when available:

1. User-provided materials
2. Related articles, papers, manuals, or known comparable topics
3. Search results or bibliographic metadata
4. Domain heuristics (the agent's own general knowledge of how this category of topic is typically organized — e.g., how technology write-ups, historical events, or biographies are usually structured — used when no related materials or search results are available)

Perspective types:

- Basic facts: definitions, timeline, actors, terminology
- Historical development
- Technical or methodological details
- Stakeholders and institutions
- Applications and use cases
- Criticism, limitations, controversies
- Economics, policy, ethics, or social impact
- Future directions

Reject perspectives that are too broad, duplicative, or irrelevant to the requested output.

## Phase 3: Ask Questions

For each deep-mode perspective, produce 3 to 8 research questions. Quick mode uses 1 to 3. Prefer questions that uncover structure, mechanisms, evidence, tradeoffs, and missing context.

Avoid only asking:

- What is X?
- When did X happen?
- Who is involved?

Better question patterns:

- What changed over time, and why?
- Which mechanisms explain the result?
- What are the competing interpretations?
- What evidence supports or weakens this claim?
- What subtopics would a strong reference article include?
- What is often misunderstood or omitted?

## Phase 4: Gather Source-Grounded Answers

For each question:

1. Find or inspect relevant sources.
2. Summarize only what the sources support.
3. Record source identifiers: title, author or organization when known, date when known, URL or local file path, and relevant section.
4. Mark each note as fact, interpretation, inference, dispute, or open question.

If sources conflict, preserve the disagreement instead of forcing a single answer.

If the environment has no built-in web-search tool, you can call `scripts/web_search.py` (see SKILL.md) to fetch candidate sources, then vet each result's reliability against `references/source-policy.md` before using it. The returned snippets are only leads — open the underlying page or a reliable summary before recording a fact from it.

## Phase 5: Follow Up

Ask follow-up questions when:

- A source answer introduces a new important entity or concept.
- There is a contradiction.
- A major perspective has weak evidence.
- The likely outline has a gap.
- The user requested depth rather than a quick overview.

Limit follow-up rounds unless the user asks for exhaustive research. A good default is 1 to 2 follow-up rounds.

## Phase 6: Synthesize Research Notes

Merge notes across perspectives:

- Deduplicate repeated facts.
- Group related findings.
- Keep source attribution attached to claims.
- Separate direct evidence from agent inference.
- Identify coverage gaps and weakly sourced areas.

For deep runs, write the synthesized brief to a file (see Persisting Intermediate State) so the drafting phase can read it back without reloading every raw note into context.

## Phase 7: Build The Outline

Build the outline in two stages so the model's own background knowledge and the new research both shape the structure.

1. Draft outline: use the background-only outline created immediately after Phase 1, before research began. If it was not created then, do not pretend the current context is isolated: use a genuinely isolated subtask if available, or label the late-created version as a non-isolated baseline. This captures the generic structure a knowledgeable writer would expect.
2. Refined outline: revise the draft using the synthesized research notes. Add topic-specific sections the draft missed, reorder for the actual evidence found, and drop sections the research cannot support.

A strong refined outline should:

- Start with high-level orientation.
- Progress from background to core concepts to implications.
- Include topic-specific sections, not only generic headings.
- Represent major perspectives fairly.
- Avoid sections that cannot be supported by the gathered sources.

For Wikipedia-like output, avoid promotional framing and include neutral section titles.

Default to 2-3 heading levels (`#`, `##`, optionally `###`) unless the topic clearly needs more granularity — match the depth a comparable reference article would use.

Skipping the draft-then-refine step and writing the outline once from notes only tends to produce a less organized, narrower outline — keep both steps even for quick tasks.

Deliver only the refined outline by default. The draft outline is an internal comparison artifact unless the user requests the construction history.

If the user wants the refined outline mechanically checked, save it to a Markdown file first — `scripts/outline_lint.py` only runs against saved files, not in-conversation text.

## Phase 8: Draft Sections

Draft only after the outline is adequate or the user explicitly asks to skip outlining.

Rules:

- Write section by section.
- Use the source notes for claims. For deep runs, pull them from the saved source-notes file rather than re-deriving them from context.
- Cite or name sources when required.
- Avoid unsupported connective claims.
- Keep caveats where sources are uncertain or conflicting.
- Do not hide gaps with fluent prose.
- Write the lead/summary section last, after the body sections exist, so it reflects what was actually written rather than what was planned. Claims in the lead that merely restate or aggregate points already cited in the body do not need a duplicate citation; only attach a new citation if the lead introduces a fact not already supported in the body.
- Avoid undated relative time phrases ("currently", "as of now", "recently") — anchor to the date the underlying fact was true (the event date or the source's "as of" date), not the retrieval date, and omit the time reference entirely if no date is known.

## Phase 9: Verify

Before final delivery, check:

- Coverage: Does the outline answer the user's intended scope?
- Organization: Are sections ordered logically?
- Grounding: Are important claims backed by notes or citations?
- Neutrality: Did source tone leak into the draft?
- Over-association: Are unrelated facts connected without support?
- Paraphrase accuracy: For claims with a citation attached, does the paraphrase match what the source actually says? A citation being present does not mean the wording is faithful. This check is internal by default — only produce a visible Verification Report (see output-formats.md) if the user asked for review notes or the topic is high-stakes.
- Time-sensitive language: Are there undated relative time phrases that will go stale?
- Gaps: What should be researched next?

For an outline saved as Markdown, optionally run `scripts/outline_lint.py`. It only flags mechanical structure problems (heading-level jumps, duplicate or placeholder headings) and does not judge the two-stage outline process, source grounding, citation quality, or viewpoint balance — a clean lint result does not satisfy the checks above.
