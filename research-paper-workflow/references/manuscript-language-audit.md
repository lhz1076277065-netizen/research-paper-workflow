# Manuscript Language Audit

Use this protocol after substantive revision and before final acceptance. Its purpose is to remove non-academic drafting residue and formulaic language patterns, not to infer whether a human or a model wrote the text. Authorship detection from prose is unreliable; assess the language itself.

## Contents

- Hard gate
- Prohibited language classes
- Context-sensitive review
- Rewrite protocol
- Rewrite patterns
- Automated scan
- Manual semantic pass
- Acceptance record

## Hard Gate

Do not deliver or mark a manuscript ready until:

- every high- and medium-severity scanner finding has been rewritten or documented as a narrow false positive;
- no assistant response, drafting instruction, placeholder, conversational aside, promotional claim, or reader coaching remains;
- every paragraph has a defined scholarly function;
- the final manual semantic pass finds no empty, repetitive, vague, or unprofessional explanation;
- any required AI-use statement remains truthful, minimal, and located only in the appropriate declaration.

## Prohibited Language Classes

### Assistant and drafting residue

Remove response preambles, capability statements, apologies, offers of further help, and process narration. Examples include language equivalent to:

- announcing that a draft, revision, answer, table, or section follows;
- stating what the assistant can or cannot do;
- asking the author to insert, add, verify, discuss, or rewrite content;
- retaining TODO, TBD, bracketed placeholders, reviewer notes, or editing comments;
- describing the manuscript as ready merely because text was generated.

Convert the intended content into final manuscript prose or remove it.

### Reader-directed and conversational explanation

Remove direct address and coaching such as asking the reader to note, remember, imagine, or observe something. Remove casual simplifiers, rhetorical questions, contractions, conversational reassurance, and phrases equivalent to "as you can see," "of course," "simply put," or "in a nutshell."

State the proposition, evidence, or inference directly.

### Formulaic AI-style prose

Review stock phrasing that often carries little information, including ornamental openings, broad claims about a rapidly changing landscape, generic statements about complexity, repeated three-part lists, excessive parallel sentence structure, and fashionable verbs used without technical meaning.

Do not replace one stock phrase with another. Identify the sentence's function and rewrite it using the specific subject, operation, evidence, and implication.

### Promotional and unsupported evaluation

Remove words such as groundbreaking, revolutionary, game-changing, remarkable, unprecedented, highly innovative, superior, robust, accurate, effective, comprehensive, or significant when the manuscript does not immediately define and support the evaluation.

Replace praise with the measured quantity, comparison, uncertainty, condition, or citation that justifies it. Retain a term only when it has a precise technical definition or direct evidentiary support.

### Empty metadiscourse

Remove announcements about what a section will discuss, statements that something is worth noting, and transitions that repeat headings without advancing the argument. Section navigation is acceptable only when it is necessary in a long or structurally complex manuscript.

Replace metadiscourse with the substantive claim or a transition that states the logical relationship.

### Unprofessional explanation

Remove textbook-like tutoring, over-explanation of common concepts, subjective judgments, vague causal stories, colloquial analogies, and unsupported certainty. Avoid explaining why a result is "interesting" or "important" without specifying the scientific consequence.

Match explanation depth to the intended specialist audience. Define necessary terms, then focus on method, evidence, mechanism, boundary, and implication.

## Context-Sensitive Review

Pattern matches are leads, not proof. Inspect the complete sentence and paragraph.

- Preserve exact quotations when necessary and correctly cited.
- Preserve terms of art whose technical meaning is established in the manuscript.
- Preserve venue-required declarations, including accurate AI-use disclosure.
- Preserve justified uses of statistical significance, robustness, accuracy, effectiveness, or superiority only when the metric, comparator, uncertainty, and conditions are explicit.
- Record retained matches narrowly. Do not create broad allowlists that hide future defects.

## Rewrite Protocol

For every finding:

1. Identify the sentence's scholarly function: report method, state result, compare evidence, interpret mechanism, delimit scope, connect literature, or disclose limitation.
2. Identify the concrete subject, action, evidence, condition, and implication.
3. Delete content that performs no scholarly function.
4. Rewrite the complete sentence or paragraph in precise academic prose.
5. Verify that the rewrite does not alter the supported claim, numerical value, citation meaning, uncertainty, or limitation.
6. Read adjacent paragraphs to remove repetition and restore logical transitions.
7. Rerun the scan.

Do not use mechanical synonym replacement. It can preserve vagueness, distort technical meaning, and create unnatural prose.

## Rewrite Patterns

Use these transformations as structural patterns, not reusable stock sentences:

| Defect | Weak form | Academic revision principle |
|---|---|---|
| Empty emphasis | "It is worth noting that the error decreased." | State the decrease, comparison, and uncertainty directly. |
| Reader direction | "As can be seen in the figure, performance improved." | Name the figure and quantify the observed change. |
| Section narration | "The following section will discuss the validation." | Begin with the validation design or finding. |
| Promotional novelty | "The groundbreaking method achieved remarkable accuracy." | Report the metric, comparator, test conditions, and interval. |
| Formulaic abstraction | "The approach delves into the intricate interplay of several factors." | Name the factors and the analysis used to estimate their relationship. |
| Casual explanation | "Simply put, the model works well." | Define the evaluation criterion and report the measured result. |
| Unsupported certainty | "Clearly, the mechanism explains the outcome." | State whether the evidence supports, is consistent with, or cannot distinguish the mechanism. |
| Drafting instruction | "The author should add a limitation here." | Write the specific limitation and its effect on interpretation. |

After rewriting, compare the original and revised claims. The revision must improve precision without changing the evidence, direction, magnitude, scope, or uncertainty.

## Automated Scan

Run the bundled scanner using its absolute path resolved from this skill directory:

```bash
python "<installed-skill-directory>/scripts/audit_manuscript_language.py" MANUSCRIPT --fail-on medium --language auto
```

Supported inputs: `.md`, `.markdown`, `.txt`, `.rst`, `.tex`, `.html`, `.htm`, and `.docx`. English and Chinese rules are available through `--language auto|en|zh|both`. Directories are scanned recursively. Use `--json` for a machine-readable report and `--allow REGEX` only for a reviewed, exact matched phrase that is a false positive.

The default `medium` threshold fails when either high- or medium-severity findings remain. A clean exit does not replace manual review.

## Manual Semantic Pass

Read the rendered manuscript from title through declarations and inspect:

- paragraph purpose and relation to the research question;
- claim-evidence alignment and unsupported evaluation;
- repeated ideas, conclusions, transitions, and sentence templates;
- vague nouns, unspecified actors, empty abstractions, and ambiguous pronouns;
- excessive nominalization, clause stacking, and avoidable sentence length;
- abrupt topic shifts and decorative transitions;
- inconsistent terminology, tense, person, modality, and certainty;
- explanations that sound like author guidance rather than scholarship;
- traces of prompts, chats, revision instructions, or generation workflow;
- differences between editable and rendered versions.

Rewrite detected defects, regenerate the rendered file, and repeat the pass.

## Acceptance Record

Record:

`File | Scanner command | Scan time | High findings | Medium findings | Rewritten | Retained false positives with reasons | Manual reviewer/pass | Final status`

Final status is `pass` only when unresolved high and medium findings are zero and the manual semantic pass is complete.
