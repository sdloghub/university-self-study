# Multimodal transcription and local OCR fallback

Read this reference for handwritten notes, photographs, screenshots, scanned pages, image-only PDFs, diagrams, or weak native extraction.

## Routing order

1. For searchable digital PDFs, extract the native text first.
2. For confirmed textless scanned PDF pages, start the uss pdf_ocr workflow; meanwhile use available model vision for required page review. For handwriting/images and missed visual structures, use model vision directly.
3. Use local PaddleOCR only when direct model vision is unavailable, the user requests local OCR, or the user explicitly prefers local batch processing.
4. If neither visual inspection nor local OCR is available, keep the source pending and record the gap. Do not invent text.

本项目无文字层 PDF 按 uss AGENTS.md 自动调用 pdf_ocr 的 PaddleOCR 官方 API；其他 hosted OCR 未获授权。不要打印 token。用户要求不上传时，使用当前模型视觉或可用本地 OCR。

## Codex/ChatGPT multimodal transcription

### Images

Inspect the original image directly. Transcribe visible text in reading order and retain:

- headings, lists, indentation, and question numbering;
- uncertain characters as `[无法辨认]` or `[疑似：…]`;
- equations as LaTeX only when the symbols are visually clear;
- brief structural descriptions for arrows, diagrams, tables, and spatial grouping;
- the source image path and page/image number.

Do not silently rewrite the content while transcribing. Put editorial cleanup into the final notes after the raw sidecar exists.

### Image-only or mixed PDFs

Use the PDF capability to determine page count and native text quality. Render only pages that require visual reading, then inspect those page images with model vision. Preserve explicit page markers such as:

```markdown
<!-- source-page: 12 -->

## 第 12 页
```

For mixed PDFs, combine reliable native text with visual transcription of weak pages. Never replace accurate native text with a lower-confidence transcription.

### Complex pages

For tables, formulas, charts, multiple columns, annotations, or diagrams:

- inspect the complete page before choosing reading order;
- preserve table headers and merged-cell meaning where visible;
- distinguish textual transcription from visual interpretation;
- mark reconstructed relationships and ambiguous formulas as `提取存疑`;
- retain or link the page image when text alone loses important meaning.

## Local fallback

Local fallback requires PaddlePaddle, PaddleOCR, and downloaded model weights. It sends no files to a hosted OCR service. Downloading dependencies and weights may require network access; using local OCR does not make the surrounding Codex conversation offline. Check the installed CLI help before choosing version-specific commands.

Plain image OCR:

```powershell
paddleocr ocr -i "INPUT" --save_path "OUTPUT_DIR" --device cpu
```

Layout-sensitive documents:

```powershell
paddleocr pp_structurev3 -i "INPUT" --save_path "OUTPUT_DIR" --device cpu
```

Do not assume a GPU or CUDA build. For multi-page PDFs, preserve page order and concatenate page Markdown only after verifying page numbering.

## Sidecar contract

Never overwrite the original file. Store OCR artifacts outside the final knowledge base:

```text
_extracted/
├─ source-name.ocr.md
├─ source-name.local-ocr.json
└─ source-name.ocr.assets/
```

Start normalized OCR Markdown with:

```yaml
---
source_file: "relative/original/path"
source_role: "user_note"
extraction_method: "native-text | codex-vision | local-paddleocr | paddleocr-official-api"
ocr_mode: "none | multimodal-vision | local-ocr | local-doc-parsing | official-api"
extraction_quality: "good | partial | poor | image_only | uncertain"
processed_at: "ISO-8601 timestamp"
---
```

When Codex/ChatGPT performs the transcription, write this sidecar directly. When local PaddleOCR emits compatible JSON, normalize it before indexing:

```powershell
python scripts/local_ocr_sidecar.py "LOCAL_JSON" "ORIGINAL_SOURCE" "_extracted/source.ocr.md" --mode ocr --source-role user_note
python scripts/local_ocr_sidecar.py "LOCAL_JSON" "ORIGINAL_SOURCE" "_extracted/source.ocr.md" --mode doc-parsing --source-role textbook
```

The helper never calls a network service.

## Quality rules

- Inspect representative pages before transcribing a long notebook.
- Keep raw transcription separate from editorial cleanup.
- Cross-check formulas, dates, names, negations, units, and question numbers against the source image.
- Treat diagrams, arrows, annotations, and spatial grouping as visual evidence; plain OCR text does not establish their relationships.
- When quality is too weak for reliable synthesis, embed or link the original page and record the issue in `00_资料缺口与待确认.md`.
- Never turn `[无法辨认]`, low-confidence text, or visual interpretation into a certain course fact.

## Index integration

Build `.course_index/` from normalized Markdown sidecars, not raw JSON. Include source file, page, source role, extraction method, OCR mode, extraction quality, and inferred chapter in chunks. Retain local raw artifacts for audit but exclude them from final study-note search unless explicitly requested.
