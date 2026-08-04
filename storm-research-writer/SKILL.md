---
name: "storm-research-writer"
description: "Use when an agent needs to perform STORM-inspired research and writing: multi-perspective topic exploration, question-driven research, source-grounded synthesis, outline generation, Wikipedia-like article drafting, research reports, course frameworks, literature-style briefs, or any task where the user asks to research before writing, use STORM, ask questions from multiple perspectives, build an outline from sources, or produce a grounded long-form draft. Do not use for simple rewriting, proofreading, summarization, translation, or short answers that do not require research, sources, or an outline."
metadata:
  version: "1.0.2"
  author: "roger"
---

# Storm Research Writer

## Overview

Use this skill to turn a topic into a researched outline or grounded long-form draft through a STORM-inspired workflow: discover perspectives, ask better questions, gather source-backed answers, synthesize notes, build an outline, and verify the result.

The skill is tool-agnostic. Use whatever reliable sources and tools are available in the current agent environment: web search, local files, PDFs, user-provided notes, connected drives, databases, or manual source lists.

## Quick Workflow

1. Frame the task: topic, target audience, output type, depth, language, jurisdiction when relevant, and citation needs. Create the background-only draft outline now if the task needs an outline.
2. Discover perspectives: include one basic-facts perspective plus several domain or stakeholder perspectives.
3. Ask questions: generate perspective-guided questions, then follow up when answers reveal gaps.
4. Gather evidence: answer each question from sources and separate facts, interpretations, and inferences.
5. Synthesize notes: merge overlapping findings and preserve source attribution.
6. Build an outline: refine the existing background-only draft with the synthesized research notes before drafting.
7. Draft if requested: lock the refined outline as the structure contract, copy its heading tree into the draft, and fill each section from source notes. Synthesize the lead/summary last.
8. Verify: block delivery until the final draft passes structure conformance plus coverage, grounding, source quality, paraphrase accuracy, time-sensitive phrasing, and over-association checks.

## Reference Routing

Read only the files needed for the user request:

- `references/storm-method.md`: Read when the user asks what STORM is, asks to compare STORM with RAG, or wants the method explained.
- `references/workflow.md`: Read for any substantial research, outline, report, article, or course-generation task.
- `references/prompts.md`: Read when generating reusable prompts or running the workflow step by step.
- `references/source-policy.md`: Read whenever external sources, citations, factual claims, controversial topics, or high-stakes accuracy are involved.
- `references/output-formats.md`: Read when the user wants a structured deliverable or when choosing an output template.

## Operating Rules

- Start with a brief plan for multi-step work: each step should include how it will be verified.
- Prefer the minimum workflow that satisfies the request. For a quick outline, do not run a full article pipeline.
- Do not silently invent sources. Mark unsourced claims as hypotheses or leave them out.
- Distinguish what sources say from what the agent infers.
- Preserve minority or conflicting viewpoints when they matter to the topic.
- Avoid over-association: do not connect two facts unless a source or strong reasoning supports the connection.
- For legal, policy, medical, financial, safety, or enterprise-governance research, establish the applicable country, region, or jurisdiction before deep retrieval. If it is missing and would change the answer, ask rather than defaulting to the most visible sources.
- Do not output secrets, credentials, API keys, or tokens in notes, logs, examples, or generated text.
- If the user asks for final writing, still produce or validate an outline before drafting unless they explicitly say to skip planning.
- Treat the refined outline as a structure contract. Do not silently delete, rename, merge, add, or reorder substantive sections while drafting. Update and revalidate the refined outline first when evidence or user direction requires a structural change.

## Optional Scripts

Resolve optional scripts relative to the directory containing this loaded `SKILL.md`. Do not assume the skill has been installed under a particular home-directory path. If the script or Python is unavailable, skip it and state the limitation instead of executing an empty path. The examples below use `<skill-directory>` as a placeholder and work from source checkouts as well as installed copies.

Use `scripts/outline_lint.py` only when an outline has been saved to a Markdown file and the user wants a quick mechanical check. The script is advisory; human review and source verification remain required.

```bash
python3 "<skill-directory>/scripts/outline_lint.py" path/to/outline.md
```

Use `scripts/report_structure_lint.py` as a mandatory delivery gate whenever both a refined outline and final Markdown draft exist. It checks that every outline heading appears at the same level and in the same order, rejects unapproved extra sections, and rejects empty leaf sections. A non-zero exit blocks delivery. Standard scaffolding such as Summary and References may be added without appearing in the outline.

```bash
python3 "<skill-directory>/scripts/report_structure_lint.py" \
  path/to/refined-outline.md path/to/final-report.md
```

If the script cannot run, perform the same one-to-one heading audit manually and state that the gate was manual. Do not claim that structure conformance passed merely because `outline_lint.py` passed.

Use `scripts/web_search.py` only when the current environment has no native web-search tool and the task genuinely needs external sources. It queries a search API (Brave, Tavily, or SerpAPI) and returns candidate sources as JSON (`title`, `url`, `snippet`, `source`, `published_date`). The API key is read from an environment variable (`BRAVE_SEARCH_API_KEY`, `TAVILY_API_KEY`, or `SERPAPI_API_KEY`) and is never printed. Results are candidate sources only — apply `references/source-policy.md` before treating any snippet as fact.

If neither native retrieval nor a configured search provider is available, do not silently fabricate a researched result. Ask the user for sources, or offer an explicitly unverified research plan/background-knowledge outline. If the request requires current facts or citations, stop and explain what retrieval capability is missing.

```bash
python3 "<skill-directory>/scripts/web_search.py" "your query" -n 5  # optional: -d domain.com (repeatable), -p provider
```

Use `scripts/fetch_url.py` to open one of those candidate URLs and read its
actual text before recording a fact from it — this closes the search → verify
loop that `references/source-policy.md` requires. It fetches an http(s) page,
drops scripts/markup, and prints the title plus readable body (size- and
time-capped). A search snippet is only a lead; the fetched page is what you
verify the exact wording against.

```bash
python3 "<skill-directory>/scripts/fetch_url.py" "https://example.com/article" -n 20000
```
