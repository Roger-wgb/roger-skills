# STORM Method

STORM stands for Synthesis of Topic Outlines through Retrieval and Multi-perspective Question Asking.

The method addresses a common weakness in long-form generation: models often start writing before researching. STORM treats pre-writing as a separate stage. Before drafting, the agent explores the topic from multiple perspectives, asks source-grounded questions, and synthesizes a structured outline.

## Core Ideas

1. Diverse perspectives produce better questions.
2. Good research is iterative: answers should create follow-up questions.
3. Long-form writing should be planned with an outline before drafting.
4. Retrieval is more useful when guided by questions than by one broad topic query.
5. Source-grounded notes should constrain the final draft.
6. Outlines improve when they combine the model's own background knowledge with the new research, not just one or the other.

## Typical STORM-Inspired Pipeline

1. Start with a topic.
2. Identify related topics or comparable articles.
3. Derive perspectives that would make coverage broad and balanced.
4. Simulate a writer asking questions from each perspective.
5. Answer questions using trusted sources.
6. Ask follow-up questions when gaps or ambiguities appear.
7. Curate the collected information.
8. Draft an outline from background knowledge alone, before looking at the research.
9. Refine that draft outline using the curated research notes.
10. Optionally draft the article section by section with citations.

## Difference From Basic RAG

Basic RAG often searches the topic directly, retrieves a set of documents, and asks the model to summarize or write from them. STORM-style work uses retrieval as part of a question-asking process. It asks what needs to be known, from which perspective, and what follow-up information is missing.

This makes STORM especially useful for topics where the best article structure is not obvious at the beginning.

## Original STORM And Workflow Extensions

The NAACL 2024 STORM paper's core contribution is the pre-writing pipeline: discover perspectives from related articles, simulate multi-turn question asking with source-grounded answers, create a background-only outline, refine it with the gathered conversations, and then write sections from relevant references. Its reported evaluation emphasizes outline coverage, article organization, relevance, coverage, and citation verifiability.

Popular four-prompt adaptations often add fixed expert lenses, contradiction mapping, synthesis with action implications, and self-review. These are useful STORM-inspired extensions, not the paper's original four modules. This skill adopts contradiction mapping, research-readiness review, section evidence packets, and a final quality review while keeping that distinction explicit.

Do not treat self-assigned 1-10 confidence as source verification. Prefer categorical evidence states and inspect the underlying source. Treat a requested "hidden connection" as especially risky because the paper's expert evaluation identified over-association of unrelated facts as a failure mode; include it only with direct source support or a transparent reasoning chain labeled as inference.

## Known Failure Modes

- Source bias transfer: biased or promotional sources can shape the output.
- Over-association: the draft may connect unrelated facts because they appeared in the same research set.
- Unsupported synthesis: a claim may be plausible but not actually backed by the cited source.
- Shallow perspectives: generated perspectives may be generic unless grounded in related topics or domain knowledge.
- Coverage imbalance: the agent may over-focus on source-rich aspects and neglect under-documented but important ones.

Use the verification workflow and source policy to reduce these risks.
