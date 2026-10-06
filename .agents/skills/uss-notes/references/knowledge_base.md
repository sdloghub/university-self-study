# Knowledge-base compatibility

Read this reference before creating a new final knowledge base or modifying an existing one.

## Profiles

### Obsidian

Use when the user names Obsidian or an existing vault contains `.obsidian/` or `[[wikilinks]]`.

- UTF-8 Markdown files.
- YAML properties for stable metadata.
- `[[Page]]` and `[[Page#Heading]]` links for durable concepts and chapters.
- Relative embeds such as `![[assets/page-001.png]]` when the vault already uses them.
- Obsidian callouts only when they improve review, such as uncertainty or exam emphasis.

### Portable Markdown

Use when the destination is unspecified or may be imported into another knowledge-base product.

- CommonMark/GFM Markdown.
- YAML frontmatter with scalar values or simple lists.
- Relative links such as `[概念](../概念.md)` and relative images.
- Put attachments under `assets/` near the final vault.
- Avoid block references, Obsidian embeds, Dataview queries, and plugin-specific syntax.

### Existing knowledge base

Inspect existing files before writing. Preserve its metadata keys, date format, folder structure, attachment folder, link syntax, aliases, and naming rules. Do not migrate syntax or rename folders unless requested.

## Recommended note properties

Use only fields that add retrieval or maintenance value:

```yaml
---
title: "Note title"
aliases: []
tags: []
course: "Course name"
chapter: "Chapter identifier"
source_roles: []
status: "draft | reviewed | needs-review"
updated: "YYYY-MM-DD"
---
```

Keep detailed source/page/OCR records in `资料依据`, `不确定内容`, `00_资料索引.md`, and OCR sidecars instead of bloating every note's frontmatter.

## Links and filenames

- Prefer stable concept, chapter, person, standard, case, method, or formula targets.
- Do not create a standalone note for every minor term.
- Keep filenames readable and stable. Avoid characters invalid on Windows: `< > : " / \\ | ? *`.
- Use relative paths and preserve case consistently.
- When both portable links and Obsidian compatibility matter, use standard Markdown links in the body and stable filenames; Obsidian resolves them correctly.

## Attachments and source preservation

- Do not move or alter originals unless requested.
- Keep OCR/debug artifacts outside the final vault in `_extracted/`.
- Copy only user-facing figures or page images into the final `assets/` folder.
- Link every copied asset relatively and record its source file/page.

## Updating an existing vault

- Read global index and progress files before editing.
- Preserve human edits and links.
- Merge new evidence into affected notes only.
- If OCR contradicts existing text, retain both and mark `来源冲突` or `提取存疑`.
- Re-run vault validation after batch changes.
