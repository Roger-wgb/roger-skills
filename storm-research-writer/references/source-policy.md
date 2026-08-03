# Source Policy

Use this policy whenever the task involves external information, factual claims, citations, or topics where accuracy matters.

## Source Preference

Prefer:

1. Primary sources: official documents, datasets, standards, filings, papers, project docs, legal texts.
2. Scholarly and technical sources: peer-reviewed papers, arXiv with caution, books, conference materials.
3. Reputable secondary sources: established journalism, encyclopedias, expert explainers.
4. User-provided materials: only within the scope the user intends.

Use cautiously:

- Blogs and personal websites
- Vendor marketing pages
- Social media
- Forum posts
- AI-generated summaries
- Mirrors, scraped copies, and unattributed pages

Avoid when possible:

- Content farms
- SEO pages with no named author or organization
- Sources that do not support their claims
- Pages with obvious promotional or ideological framing unless the task is to analyze that framing

## Claim Discipline

Classify notes as:

- Fact: directly supported by a source.
- Interpretation: a source's analysis or framing.
- Inference: the agent's reasoning from supported facts.
- Dispute: sources disagree or uncertainty exists.
- Gap: important information not yet sourced.

Do not present inferences as sourced facts.

## Search Results Are Candidate Sources

Output from a search tool or `scripts/web_search.py` (title, url, snippet) is a set of *candidate* sources, not evidence. A snippet is a fragment chosen by the search engine, often truncated or paraphrased, and may not reflect what the page actually concludes.

- Do not state a factual conclusion on the strength of a snippet alone.
- Before recording any important claim as fact, open the original page or a reliable full-text summary and confirm the wording supports the exact claim.
- Judge each result's reliability using the Source Preference tiers above; a high search rank does not mean a source is authoritative.
- If the environment has no native page-fetch tool, use `scripts/fetch_url.py` (see SKILL.md) to open a candidate URL and confirm the wording against the actual page.
- If neither a native tool nor the script can retrieve the page, a snippet alone supports only a candidate lead — record the claim as a gap, not a fact.

## Citation Rules

When citations are required:

- Attach citations to the specific claims they support.
- Prefer source titles, authors or organizations, dates, and URLs or local paths.
- Do not cite a source for a claim it does not support.
- If using a local document, cite the file path and section or page when available.
- If a source is weak, state that limitation.
- A citation must entail the exact claim made, not just the general topic. Re-check paraphrased claims against the source wording — a citation that exists but supports a weaker, broader, or different claim is a separate failure mode from a missing citation, and is just as likely to mislead a reader.

## Output Language vs. Source Language

Choose sources by authority and relevance, not by what language the user wants the output in. When a source's original language differs from the output language:

- Keep the source title and organization or author name in their original language in the References list (a parenthetical translation is optional).
- Translate the supporting claim into the output language in the body text.
- For direct quotations, translate and mark the passage as a translation.
- When checking paraphrase accuracy (see workflow.md Phase 9), compare the translated claim's meaning against the original-language source, not just the surface wording.

## Neutrality

Watch for source tone leaking into the output. Rewrite promotional, emotional, partisan, or sensational language into neutral prose.

When a topic is contested:

- Represent major positions in proportion to the authority, quality, consistency, and current state of the evidence — not the raw number of sources or a fixed amount of space per side.
- Name who holds a view when relevant.
- Avoid implying consensus where none exists.
- Avoid false balance when evidence is strongly one-sided.

## Over-Association Guardrail

Do not connect two facts merely because they appeared in the same search session, article, or note set.

Before making a connective claim, ask:

- Does a source explicitly connect these facts?
- Is the causal or explanatory link obvious and low-risk?
- Would the claim still be true if the facts were considered independently?

If not, split the facts into separate sentences or mark the connection as a hypothesis.

## High-Stakes Topics

For medical, legal, financial, safety, policy, or rapidly changing topics:

- Use current and authoritative sources.
- Include date context.
- Avoid advice that exceeds the evidence.
- State uncertainty and recommend consulting qualified professionals when appropriate.
