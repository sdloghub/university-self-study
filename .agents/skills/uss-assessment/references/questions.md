# Source questions and useful practice

Read [共享证据规范](../../uss-source-index/references/evidence_quality.md) for the persisted schema and coverage meanings.

## Candidate to confirmed question

questions.jsonl holds automatic candidates, which may miss screenshots or include rhetorical prompts. Read the full page, code, figures, choices and neighboring-page setup. Preserve exact wording and location. An incomplete question remains needs_review. Identical wording on different pages may be different questions.

Write confirmed source questions to questions.reviewed.jsonl with source hash, physical page, original prompt/context, answer provenance, reviewer and note targets. Codex review is not user confirmation. Recheck when the source hash changes.

## Answers and inventories

- Source answer exists: preserve it, add reasoning, and identify corrections separately.
- No source answer: derive and verify it; label agent_derived.
- Conflicting answers: keep the conflict and source references.
- Missing code or image: recover it or record a gap; do not invent setup.

An optional question index may list topic, type, year/source and answer state. Infer frequency only from an enumerated dataset; lecture emphasis does not establish exam weight.

## Coverage

coverage_check.py retrieves lexical candidates. Its B/D compatibility hints are pending review, not semantic scores. Inspect the entire question against the actual note and record final A/B/C/D plus rationale: A all requirements supported, B partial, C dependent on marked supplements, D absent or unresolved. Structural validation never establishes answer coverage.

## Practice

Generate exercises only when requested or implied. Separate original, adapted and new questions. If no source questions exist, say so rather than fabricate a source-question index.

Each exercise needs a concrete task, sufficient code/data, an answer, reasoning and a concept link. Prefer output prediction, debugging, counterexamples, derivations and applications over generic chapter reflections. Quality matters more than fixed counts. Do not label generated practice as exam predictions without evidence.
