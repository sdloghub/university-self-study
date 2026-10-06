#!/usr/bin/env python3
"""Normalize compatible local PaddleOCR JSON into an auditable Markdown sidecar."""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def yaml_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def page_number(page: dict, fallback: int) -> int:
    for key in ("pageIndex", "page_index", "page", "pageNum", "page_num"):
        value = page.get(key)
        if isinstance(value, int):
            return value + 1 if key in {"pageIndex", "page_index"} else value
    return fallback


def unwrap_result(page: dict) -> dict:
    result = page.get("res") if isinstance(page.get("res"), dict) else page
    return result.get("overall_ocr_res") or result.get("prunedResult") or result.get("pruned_result") or result


def extract_ocr_page(page: dict) -> tuple[str, list[float]]:
    result = unwrap_result(page)
    texts = result.get("rec_texts") or result.get("texts") or []
    scores = result.get("rec_scores") or result.get("scores") or []
    numeric_scores = [float(score) for score in scores if isinstance(score, (int, float))]
    lines = []
    for index, text in enumerate(texts):
        value = str(text).strip()
        if not value:
            continue
        score = scores[index] if index < len(scores) and isinstance(scores[index], (int, float)) else None
        if score is not None and score < 0.60:
            lines.append(f"[OCR低置信度 {score:.2f}] {value}")
        else:
            lines.append(value)
    return "\n\n".join(lines), numeric_scores


def markdown_body(page: dict) -> str:
    result = page.get("res") if isinstance(page.get("res"), dict) else page
    markdown = result.get("markdown")
    if isinstance(markdown, dict):
        markdown = markdown.get("markdown_text") or markdown.get("markdownText")
    return str(result.get("markdownText") or result.get("markdown_text") or markdown or "").strip()


def extraction_quality(mode: str, scores: list[float], has_text: bool) -> str:
    if not has_text:
        return "empty"
    if mode == "doc-parsing" or not scores:
        return "partial"
    mean = sum(scores) / len(scores)
    if mean >= 0.85:
        return "good"
    if mean >= 0.60:
        return "partial"
    return "poor"


def payload_pages(payload) -> list[dict]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if not isinstance(payload, dict):
        return []
    pages = payload.get("pages")
    if isinstance(pages, list):
        return [item for item in pages if isinstance(item, dict)]
    return [payload]


def normalize(payload, mode: str) -> tuple[list[str], list[float]]:
    markdown_pages = []
    all_scores = []
    numbered = [(page_number(page.get("res", page), index), page)
                for index, page in enumerate(payload_pages(payload), start=1)]
    numbers = [number for number, _ in numbered]
    if any(n < 1 for n in numbers) or len(numbers) != len(set(numbers)):
        raise ValueError('Invalid or duplicate physical page numbers; normalize the OCR export first')
    for number, page in sorted(numbered, key=lambda item: item[0]):
        if mode == "doc-parsing":
            body = markdown_body(page)
        else:
            body, scores = extract_ocr_page(page)
            all_scores.extend(scores)
        markdown_pages.append(
            f"<!-- source-page: {number} -->\n\n## 第 {number} 页\n\n{body or '[未识别到可用文本]'}"
        )
    return markdown_pages, all_scores


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("raw_json", help="Local PaddleOCR JSON output")
    parser.add_argument("source_file", help="Original source path recorded in frontmatter")
    parser.add_argument("output", help="Normalized Markdown sidecar path")
    parser.add_argument("--mode", choices=("ocr", "doc-parsing"), required=True)
    parser.add_argument("--source-role", default="unclassified_source")
    args = parser.parse_args()

    payload = json.loads(Path(args.raw_json).read_text(encoding="utf-8"))
    pages, scores = normalize(payload, args.mode)
    quality = extraction_quality(args.mode, scores, any("[未识别到可用文本]" not in page for page in pages))
    processed_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    frontmatter = [
        "---",
        f"source_file: {yaml_string(args.source_file)}",
        f"source_role: {yaml_string(args.source_role)}",
        'extraction_method: "local-paddleocr"',
        f'ocr_mode: "local-{args.mode}"',
        f"extraction_quality: {yaml_string(quality)}",
        f"processed_at: {yaml_string(processed_at)}",
        "---",
    ]
    content = "\n".join(frontmatter) + "\n\n" + "\n\n".join(pages) + "\n"
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content, encoding="utf-8")


if __name__ == "__main__":
    main()
