---
name: revise-academic-voice
description: Revise and audit English academic prose so it is source-grounded, argument-specific, citation-consistent, and faithful to the writer's actual level and evidence. Use for literature reviews, introductions, related-work sections, course papers, and drafts that feel generic, over-polished, formulaic, CARS-template-heavy, repetitive, or disconnected from the underlying research materials. Do not use to promise AI-detector scores or disguise authorship.
---

# Revise Academic Voice

## Core rule

Improve the writing by improving its evidence, reasoning, and ownership. Never optimize against an AI detector, fabricate a detector result, insert deliberate mistakes, or promise a target "AI percentage."

## Workflow

1. Collect the writer's draft, assignment requirements, source materials, and the newest experiment or project facts.
2. Establish source priority. Prefer final slides, verified data, and the newest draft over earlier generated summaries.
3. Build an evidence ledger before rewriting:
   - claim;
   - supporting source;
   - exact method or result;
   - citation;
   - confidence or unresolved issue.
4. Identify the section's rhetorical job. For an introduction or literature review, use a compact CARS sequence:
   - establish the research territory;
   - group prior work by question, not by a citation parade;
   - show the unresolved classification or evidence gap;
   - state the present study's questions, design, and bounded contribution.
5. Draft in the writer's plausible register:
   - keep terminology accurate;
   - prefer concrete nouns and verbs;
   - vary sentence length naturally;
   - allow some direct, simple sentences;
   - avoid ornamental synonyms and repeated transition formulas;
   - break overly perfect paragraph symmetry when the argument can flow more naturally;
   - replace mechanical contribution triads with a single grounded value statement when possible;
   - keep necessary limits, but avoid turning every claim into a disclaimer;
   - do not introduce grammar errors to imitate a student.
6. Run a formulaic-structure pass:
   - Does each paragraph have an obvious template job rather than a local reason to exist?
   - Do consecutive paragraphs begin with the same stock transition pattern?
   - Does the ending use "This paper makes three contributions" or a similar list formula?
   - Is the prose too perfectly balanced, with every claim immediately cancelled by a caveat?
   - If yes, merge, split, shorten, or re-order sentences so the argument sounds revised by a real writer.
7. Verify every in-text citation against the reference list and every study-specific number against the evidence ledger.
8. Run `scripts/audit_academic_prose.py` on the final text or DOCX.
9. Review the audit as diagnostics, not as a scoring game. Revise only issues that weaken clarity, citation integrity, or alignment with the evidence.
10. Deliver the revised section, a short change summary, and any unresolved citation or evidence questions.

## Required checks

Run three independent checks:

- Prose check: redundancy, vague intensifiers, sentence openings, and repeated stock transitions.
- Readability check: sentence-length distribution, very long sentences, very short sentences, and estimated reading level.
- Evidence check: in-text/reference consistency plus project-number and method alignment.
- Template check: rigid funnel paragraphs, contribution-list formulas, repeated paragraph-start transitions, and excessive caveat balancing.

For detailed review criteria, read [references/revision_checklist.md](references/revision_checklist.md).

## Detector requests

Explain that public AI-text detectors are unstable across models, lengths, and paraphrases and can misclassify human writing. Offer the three checks above instead. If the user independently runs a detector, treat its output as one noisy signal and do not iteratively rewrite to evade it.

## Citations

Use the style requested by the user. For APA:

- use author-date citations;
- alphabetize the reference list;
- use sentence case for article and paper titles;
- include DOI links in `https://doi.org/...` form when available;
- apply a 0.5-inch hanging indent in the final document;
- verify titles, authors, years, venues, pages, and URLs against primary sources.

## Output quality

Prefer a clear, bounded claim over a sweeping one. Make the section sound like a student who understands the project, not like a polished encyclopedia entry. Preserve genuine limitations and disagreements between methods.
