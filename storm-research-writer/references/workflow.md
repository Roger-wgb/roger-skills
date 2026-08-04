# Workflow

Use the smallest version of this workflow that satisfies the user's request. For quick tasks, stop after the outline. For deep research, complete all phases.

## Scaling Depth

"Quick" and "deep" change how much each phase costs, not which phases run. Even a quick outline-only request still passes through perspectives, questions, and the two-stage outline (Phase 8) — the difference is how much actual retrieval and note-taking happens at each step:

- Quick (e.g., "just give me an outline", a general or well-known topic, no sources provided): keep perspectives to 1 basic + 2-4 others and ask 1-3 questions per perspective. This rule overrides the larger Phase 2 and Phase 3 defaults. Answer from background knowledge instead of running new searches unless the topic is unfamiliar or time-sensitive, skip follow-up rounds, and label any concrete unsourced claims as provisional. Phase 4's source-record requirements apply only if retrieval is actually performed. Treat the resulting notes — however thin — as the input to the outline refinement step (Phase 8.2). This still produces a two-stage outline; the draft and refined versions simply differ less when little new information came in.
- Deep (e.g., "research X", citations required, a niche or fast-changing topic, a long-form draft requested): use the full 4-7 perspectives, run real searches per question, map material disagreements, and continue focused follow-ups until the research-readiness gate passes or the remaining limitation is made explicit. One or two follow-up rounds are a cost-control default, not proof that the research is ready.

If it is genuinely unclear which mode the user wants, ask once rather than guessing.

For deep work, establish a depth contract during framing. Record the decisions the output should support, the expected explanatory treatment (for example mechanisms, chronology, cases, tradeoffs, or implementation detail), useful source types, localization needs, and any requested length. Treat length as a scope constraint, never as evidence of depth.

## Persisting Intermediate State

A deep run generates a lot of intermediate text — perspective lists, per-question notes, source notes, the synthesized brief, and the outline. Holding all of it in the conversation crowds out the context the drafting phase needs, and loses everything if the run is interrupted.

For deep runs (multiple perspectives, real retrieval, a long draft), write these artifacts under a task-specific `.storm-research/<topic-slug>-<date-or-task-id>/` directory, using stable names such as `draft-outline.md`, `source-notes.md`, `research-brief.md`, `research-readiness.md`, `refined-outline.md`, `section-evidence.md`, and `final-quality-review.md`. Never overwrite an existing task directory; choose a new suffix. Use the templates in `references/output-formats.md`, then read the files back when passing gates and drafting. If the environment is read-only, keep the artifacts in context and tell the user that the run is not resumable from files.

Quick runs can stay in-context; the overhead of files is not worth it when little new information is gathered.

## Phase 1: Frame The Task

Clarify or infer:

- Topic
- Output type: outline, research brief, report, course framework, article, literature summary, or final draft
- Audience and depth
- Depth contract: intended decisions, expected treatment, useful evidence mix, localization needs, and optional length target
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

After the first evidence pass, map material disagreements:

- Which perspectives or sources make conflicting claims?
- Which claim has stronger evidence, and why?
- What question would most reduce the important uncertainty?
- What do credible opposing sources agree on?
- Which relevant perspective or issue is still missing?

Do not manufacture conflict when authoritative evidence is one-sided. Continue only with follow-ups likely to change a core answer, resolve a material dispute, add a missing perspective, or change the refined outline. One or two rounds are a default budget; stop earlier when no useful follow-up remains and continue longer when the gate would otherwise be blocked.

## Phase 6: Synthesize Research Notes

Merge notes across perspectives:

- Deduplicate repeated facts.
- Group related findings.
- Keep source attribution attached to claims.
- Separate direct evidence from agent inference.
- Identify coverage gaps and weakly sourced areas.
- Preserve material disagreement instead of averaging it into a false consensus.
- Classify confidence categorically as `verified`, `supported`, `inference`, `disputed`, `gap`, or `downgraded`; do not rely on uncalibrated numeric confidence scores.
- Include a non-obvious connection only when a source explicitly connects the facts or the reasoning chain is written out and labeled as inference. Otherwise keep the facts separate.

For deep runs, write the synthesized brief to a file (see Persisting Intermediate State) so the drafting phase can read it back without reloading every raw note into context.

## Phase 7: Research Readiness Gate

Pass this semantic gate before locking the refined outline for any deep report or article. Write `research-readiness.md` using `references/output-formats.md` and set the decision to `PASS` or `BLOCKED`.

Set `PASS` only when:

- Every core question has a supported answer, an inference with supported premises, a preserved dispute, or an explicit evidence gap.
- Every material perspective has actually contributed source-grounded findings or is recorded as missing; naming a persona alone is not coverage.
- Important contradictions have been investigated and retained when unresolved.
- The source portfolio is fit for the claims: authoritative where available, sufficiently varied for the topic, and not silently dominated by one interested organization.
- The proposed outline can be supported without padding, invented examples, or unsupported connective claims.
- The stopping rationale is explicit. A practical signal is that the latest focused follow-up produced no new major claim, counterevidence, missing perspective, or outline-changing finding.

Set `BLOCKED` when a central conclusion or planned section lacks usable evidence. Return to Phases 3-5, narrow the claim, mark a gap, or revise the intended scope. Do not pass the gate by accumulating arbitrary source counts.

Quick work may use the same checks in a compact in-context review. Do not create the file when its overhead exceeds the task.

## Phase 8: Build The Outline

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

After refining the outline, run `scripts/outline_lint.py` when applicable and lock it only after the research-readiness decision is `PASS`.

## Phase 9: Section Evidence Gate

Before drafting a deep final output, copy the refined outline's complete heading tree into `section-evidence.md`. For every leaf section, create a section evidence packet using `references/output-formats.md`.

Each packet must state:

- The section's purpose and questions.
- The claims it can make and each claim's type (`fact`, `interpretation`, `inference`, `dispute`, or `gap`).
- The exact sources supporting those claims.
- Material disagreement, uncertainty, boundary, or evidence gap.
- The intended depth (`brief`, `standard`, or `deep`) under the task's depth contract.

Mechanisms, cases, comparisons, and action implications are conditional requirements: include them when they serve the section's purpose and reliable evidence exists. Do not fabricate a case or false opposing view to fill a template.

Set the gate to `PASS` only when every leaf section is writable from its packet. If a packet is thin, return to research, narrow the section, merge or remove it in the refined outline, or keep an explicit evidence-gap section. Re-run outline validation after any structural change.

Run `scripts/report_structure_lint.py refined-outline.md section-evidence.md` to confirm mechanically that the complete heading tree is present and every leaf packet is non-empty. A clean result does not replace the semantic checks above.

## Phase 10: Draft Sections

Draft only after the outline is adequate or the user explicitly asks to skip outlining.

Rules:

- Lock the refined outline as the structure contract after it passes `outline_lint.py` or an equivalent manual check.
- Create the final draft by copying the refined outline's complete heading tree verbatim before writing prose. Standard scaffolding headings such as Summary and References may be added; other additions require updating the refined outline first.
- Draft from `section-evidence.md`, not from a title-only heading-to-source map.
- Write one leaf section at a time. Do not silently delete, rename, merge, add, or reorder substantive headings to improve flow or shorten the output.
- If evidence cannot support a planned section, keep it and state the gap, or revise and revalidate the refined outline before continuing. Never solve the problem by omitting the section only from the final draft.
- Use the source notes and section evidence packet for claims. For deep runs, pull them from saved artifacts rather than re-deriving them from context.
- Match the declared section depth. Where relevant, develop the section through a core judgment, explanation or mechanism, source-grounded evidence, case or comparison, material counterpoint, boundary, and implication. Use only the elements that fit the section; do not force a rigid paragraph formula.
- Cite or name sources when required.
- Avoid unsupported connective claims.
- Keep caveats where sources are uncertain or conflicting.
- Do not hide gaps with fluent prose.
- Write the lead/summary section last, after the body sections exist, so it reflects what was actually written rather than what was planned. Claims in the lead that merely restate or aggregate points already cited in the body do not need a duplicate citation; only attach a new citation if the lead introduces a fact not already supported in the body.
- Avoid undated relative time phrases ("currently", "as of now", "recently") — anchor to the date the underlying fact was true (the event date or the source's "as of" date), not the retrieval date, and omit the time reference entirely if no date is known.

## Phase 11: Verify And Pass The Final Quality Gate

Before final delivery, check:

- Structure conformance: Does every refined-outline heading appear verbatim at the same level and in the same order? Are all leaf sections non-empty? Are there unapproved substantive headings?
- Coverage: Does the outline answer the user's intended scope?
- Explanatory depth: Do core sections explain why, how, under what conditions, or with what consequences when the depth contract requires it?
- Organization: Are sections ordered logically?
- Grounding: Are important claims backed by notes or citations?
- Neutrality: Did source tone leak into the draft?
- Over-association: Are unrelated facts connected without support?
- Paraphrase accuracy: For claims with a citation attached, does the paraphrase match what the source actually says? A citation being present does not mean the wording is faithful. This check is internal by default — only produce a visible Verification Report (see output-formats.md) if the user asked for review notes or the topic is high-stakes.
- Time-sensitive language: Are there undated relative time phrases that will go stale?
- Gaps: What should be researched next?
- Disagreement preservation: Did synthesis retain material conflicts, evidence downgrades, and missing perspectives?
- Proportionality: Does important material receive adequate treatment without padding, excessive headings, or repetition?
- Decision usefulness: For analytical output, does the report make the evidence's implications clear to the intended audience? Skip this criterion for neutral reference output when actionability is not requested.

For an outline saved as Markdown, optionally run `scripts/outline_lint.py`. It only flags mechanical structure problems (heading-level jumps, duplicate or placeholder headings) and does not judge the two-stage outline process, source grounding, citation quality, or viewpoint balance — a clean lint result does not satisfy the checks above.

When both `refined-outline.md` and the final Markdown draft exist, run `scripts/report_structure_lint.py` before delivery. Exit code 0 is required. If it fails, fix the final draft or intentionally revise and revalidate the outline; do not deliver with a warning. If the script is unavailable, manually create a one-to-one checklist of outline heading, final heading, level, order, and content status. The manual checklist must have no failures before delivery.

For deep final writing, also write `final-quality-review.md` using `references/output-formats.md`. Set the decision to `PASS` only when the output satisfies the task's depth contract and has no critical failure in coverage, explanatory depth, grounding, disagreement preservation, organization, source quality, citation entailment, time-sensitive phrasing, or over-association. Mechanical signals such as section length, citation density, and repeated phrasing may reveal problems, but none proves semantic depth. A `BLOCKED` decision requires revision and another review before delivery.
