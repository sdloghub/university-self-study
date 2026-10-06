# Evidence, questions and quality

## Stable evidence

Every topic needs one or more links to physical source pages. Store source paths relative to a declared course root, source hash, physical page, printed label when known, extraction method, and review status. Keep source snapshots when hashes change; existing references then require review.

Native extraction and visual supplements are separate records. A visual sidecar records exactly which pages were examined and what text or relationship was recovered. Never turn a whole PDF's `good` label into proof that all figures were read.

## Questions

`questions.jsonl` contains automatically detected **candidates**. False positives and missed questions are expected. Each candidate carries stable ID, page, raw context and `status: candidate`; it must not be counted as a verified source question.

`questions.reviewed.jsonl` contains agent-confirmed records, not user-confirmed records unless the user actually reviewed them. Fields:

- `id`, `source_file`, `source_sha256`, `page` (physical PDF page)
- `original_prompt`, `context` (full code/options if required)
- `question_kind`: `source_question`, `adapted_source_question`, or `generated`
- `answer`, `answer_origin`: `source` or `agent_derived`
- `reviewer`: `codex` or `user`, `reviewed_at`, `status`: `reviewed` or `needs_review`
- `note_targets`, `evidence_excerpt`, `coverage`: `A/B/C/D` only after actual review

Review the entire question, not a first-line fragment. A code-output question without its code is incomplete. If the source has no answer, derive the answer and say so. Do not promote a lecture explanation into an original exercise; label it as generated or adapted.

## Coverage

Keyword retrieval only says that potentially relevant text exists. `coverage_check.py` returns a pending review state and B/D compatibility hints, never automatically A. A means the note explicitly supplies all answer requirements with checked evidence. B means partial explanation; C means the answer relies on a clearly marked secondary source; D means missing or unresolved. Record reviewer and evidence with every final rating.

## Quality gates

- Structure: links, metadata and file separation.
- Evidence: exact page links, source changes, raw question context, uncertain transcription.
- Learning value: distinct explanations, runnable examples where appropriate, no generic repeated filler.
- Subject correctness: example execution, hand-checked derivations, or bounded official reference checks.

Report each gate separately. A tool's `ok` is only the scope that tool actually checks. Extraction quality is a source property; note review status is a different property.
