# Workflow, resume and incremental updates

## Scope and course workflow

Follow SKILL.md's lightweight, course, existing-vault or query route. Preserve established output paths. Small notes do not need all course-level artifacts.

1. Inventory originals and existing notes. Read status, gaps and progress. Resolve source roles from content, not filenames alone.
2. Extract native text; inspect handwriting, screenshots and diagrams when needed. Save raw extraction before editorial writing, with physical pages distinct from printed labels.
3. Build or refresh the index once. Query full relevant pages. Index health measures extraction signals, not note correctness.
4. Infer chapters and discipline. Reuse known preferences; communicate assumptions and continue within authorization. Ask only for consequential missing decisions.
5. Write concrete explanations and examples. Use derivation, code execution or source comparison as appropriate. Link coherent topics to exact source pages.
6. If source questions matter, inspect candidates and save complete context in questions.reviewed.jsonl. Separate source answers from derived answers; do not invent exam weight.
7. Assemble merged notes and navigation from the same reviewed content. Retain requested terminology, chapter links and concept dependencies. Add review routes and generated practice when requested or implied by exam preparation.
8. Validate structure and evidence, save gaps and next actions, then publish through baseline checks.

## Resume

Read available equivalents of 00_项目状态.md, 00_章节进度表.md, 00_资料索引.md, 00_资料缺口与待确认.md, progress.json and questions.reviewed.jsonl. Do not require all of these for lightweight work.

Track each chapter's source revision, extraction status, writing status, evidence review, subject checks, output path, gaps and next action. Index metadata and writing completion are separate fields. Rebuilding must preserve writing decisions.

Size batches by content and context, not a fixed chapter count. Persist progress before pauses. Resume unfinished work instead of rerunning an old generator over the whole vault.

## Change impact

- Added or changed source: inspect its chapters, linked concepts, citations, answers, merged note and inventory.
- Removed source: flag stale references; do not delete user notes automatically.
- New questions: deepen corresponding explanations, not unrelated chapters.
- New handwriting: retain user annotations and uncertainty.
- Query: retrieve and answer with pages; no regeneration.

## Safe publication

Stage output outside the vault and keep prior generated hashes in a separate state manifest. For initial migration, use a known pristine baseline only after comparing it to current notes. Never label edited current files as pristine merely to suppress conflicts.

```powershell
python scripts/safe_publish.py --staging STAGING --vault VAULT --state STATE_JSON --baseline BASELINE
python scripts/safe_publish.py --staging STAGING --vault VAULT --state STATE_JSON --baseline BASELINE --apply
```

Default is dry run. Conflicts stop the planned publication and leave candidates in staging. Merge human edits deliberately. The script backs up replacements and never deletes notes. Replacement is atomic per file, not across the whole vault; an OS failure midway may require recovery from backups and staging.

## Delivery

Report extraction coverage, visual review scope, reviewed questions, executed examples, structural checks and gaps separately. Use bounded official research for source conflicts or version-sensitive corrections and mark it as supplemental. Course authority defines course scope, not universal technical truth.
