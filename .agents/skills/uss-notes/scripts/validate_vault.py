#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit
from collections import defaultdict
from functools import lru_cache

GLOBAL_FILES = [
    '00_总目录.md',
    '00_资料索引.md',
    '00_术语索引.md',
    '00_资料缺口与待确认.md',
    '00_检索日志.md',
]

ARTIFACT_DIR_NAMES = {'.course_index', '_extracted', '_working'}

PLACEHOLDER_PATTERNS = [
    # Match human-language template tokens without flagging valid code such as
    # Java generics (<T>) or relational expressions (<, <=, >, >=).
    re.compile(r'<(?:[一-鿿][^>\n]{0,29}|(?:chapter|course|concept|title|name|file)[^>\n]{0,24})>', re.I),
    re.compile(r'核心概念A'),
    re.compile(r'前置章节_章节名'),
    re.compile(r'第二章_章节名'),
    re.compile(r'03_某类型文件'),
]

LEAKAGE_PATTERNS = [
    re.compile(r'Do not require', re.I),
    re.compile(r'\.claude[\\/]', re.I),
    re.compile(r'\.codex[\\/]', re.I),
    re.compile(r'\.agents[\\/]', re.I),
    re.compile(r'lower-level skill', re.I),
    re.compile(r'internal rubric', re.I),
    re.compile(r'This skill controls', re.I),
]

WIKILINK_RE = re.compile(r'\[\[([^\]]+)\]\]')


def read_json(path: Path, default=None):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except json.JSONDecodeError:
        return default


def is_artifact_path(path: Path, root: Path):
    try:
        rel_parts = path.relative_to(root).parts
    except ValueError:
        return False
    return any(part in ARTIFACT_DIR_NAMES for part in rel_parts)


def markdown_files(vault_dir: Path):
    return sorted(p for p in vault_dir.rglob('*.md') if not is_artifact_path(p, vault_dir))


def nested_artifact_dirs(vault_dir: Path):
    found = []
    for path in vault_dir.rglob('*'):
        if path.is_dir() and path.name in ARTIFACT_DIR_NAMES:
            found.append(path.relative_to(vault_dir).as_posix())
    return sorted(found)


def resolve_index_dir(vault_dir: Path, index_dir_arg: str | None):
    if index_dir_arg:
        return Path(index_dir_arg)
    sibling = vault_dir.parent / '.course_index'
    if sibling.exists():
        return sibling
    legacy_inside = vault_dir / '.course_index'
    if legacy_inside.exists():
        return legacy_inside
    return sibling


def index_is_inside_vault(vault_dir: Path, index_dir: Path):
    try:
        index_dir.resolve().relative_to(vault_dir.resolve())
        return True
    except ValueError:
        return False


def link_targets(vault_dir: Path, files):
    targets = set()
    for path in files:
        rel = path.relative_to(vault_dir).as_posix()
        targets.add(rel)
        targets.add(rel[:-3])
        targets.add(path.stem)
    return targets


def normalize_link(raw: str):
    target = raw.split('|', 1)[0].split('#', 1)[0].strip()
    return target.replace('\\', '/')


def prose(text):
    text = re.sub(r'(?ms)^([`~]{3,})[^\n]*\n.*?^\1[^\n]*$', '', text)
    return re.sub(r'`[^`\n]*`', '', text)


@lru_cache(maxsize=128)
def pdf_pages(path):
    from pypdf import PdfReader
    return len(PdfReader(path).pages)


def has_anchor(path, fragment, wiki=False):
    text = prose(path.read_text('utf-8', errors='replace'))
    fragment = unquote(fragment)
    if wiki and fragment.startswith('^'):
        return bool(re.search(r'\^' + re.escape(fragment[1:]) + r'\s*$', text, re.M))
    headings = re.findall(r'^#{1,6}\s+(.+?)\s*#*\s*$', text, re.M)
    if wiki:
        return fragment in headings
    slugs = [re.sub(r'[^\w\-\s]', '', h.lower()).replace(' ', '-') for h in headings]
    return fragment in headings or fragment in slugs


def find_broken_links(vault_dir: Path, files, published_root=None):
    targets = link_targets(vault_dir, files)
    by_stem = defaultdict(list)
    for item in files:
        by_stem[item.stem].append(item)
    broken = []
    for path in files:
        text = prose(path.read_text(encoding='utf-8', errors='replace'))
        def record(raw, reason):
            broken.append({'file': path.relative_to(vault_dir).as_posix(), 'link': raw, 'reason': reason})
        for raw in WIKILINK_RE.findall(text):
            target = normalize_link(raw)
            if target.startswith(('http:', 'https:', 'mailto:')):
                continue
            resolved = None
            if not target:
                resolved = path
            elif '/' in target:
                choices = [vault_dir / target, path.parent / target]
                resolved = next((c if c.is_file() else c.with_suffix('.md') for c in choices if c.is_file() or c.with_suffix('.md').is_file()), None)
                if resolved is None:
                    record(raw, 'missing path')
            elif len(by_stem.get(Path(target).stem, [])) != 1:
                record(raw, 'missing or ambiguous note')
            else:
                resolved = by_stem[Path(target).stem][0]
            link = raw.split('|', 1)[0]
            if resolved and '#' in link and not has_anchor(resolved,link.split('#',1)[1],True):
                record(raw, 'missing heading or block anchor')
        for raw in re.findall(r'!?\[[^\]\n]*\]\((<[^>]+>|[^\s)]+)(?:\s+"[^"\n]*")?\)', text):
            raw = raw.strip('<>')
            parsed = urlsplit(raw)
            if parsed.scheme or raw.startswith('//'):
                continue
            dest = (path.parent / unquote(parsed.path)).resolve() if parsed.path else path
            if published_root and parsed.path:
                try:
                    dest.relative_to(vault_dir.resolve())
                except ValueError:
                    dest = (Path(published_root) / path.relative_to(vault_dir).parent / unquote(parsed.path)).resolve()
            if not dest.is_file():
                record(raw, 'missing local file')
                continue
            if dest.suffix.lower() == '.md' and parsed.fragment and not has_anchor(dest, parsed.fragment):
                record(raw, 'missing heading anchor')
            if dest.suffix.lower() == '.pdf' and parsed.fragment.startswith('page='):
                try:
                    page = int(parsed.fragment[5:])
                    if not 1 <= page <= pdf_pages(str(dest)):
                        record(raw, 'PDF page out of range')
                except ImportError:
                    pass  # file checked; page bounds require optional pypdf
                except (ValueError, OSError):
                    record(raw, 'invalid PDF page reference')
    return broken


def repeated_explanations(vault_dir, files):
    seen = defaultdict(list)
    for path in files:
        text = prose(path.read_text('utf-8'))
        if not re.search(r'type: (?:knowledge-point|chapter-note)', text):
            continue
        for paragraph in re.split(r'\n\s*\n', text):
            paragraph = paragraph.strip()
            if len(paragraph) >= 65 and not paragraph.startswith(('#','-','>','---','[')):
                seen[paragraph].append(path.relative_to(vault_dir).as_posix())
    return [{'text': k[:150], 'files': v} for k,v in seen.items() if len(set(v)) >= 3]


def find_pattern_hits(vault_dir: Path, files, patterns):
    hits = []
    for path in files:
        text = prose(path.read_text(encoding='utf-8', errors='replace'))
        for pattern in patterns:
            match = pattern.search(text)
            if match:
                hits.append({
                    'file': path.relative_to(vault_dir).as_posix(),
                    'match': match.group(0)[:80],
                })
                break
    return hits


def validate(vault_dir: Path, index_dir_arg: str | None = None, mode="course", published_root=None):
    files = markdown_files(vault_dir)
    names = {p.name for p in files}
    warnings = []
    artifacts = nested_artifact_dirs(vault_dir)
    if artifacts:
        warnings.append('working artifact directories should be outside the final vault: ' + ', '.join(artifacts[:10]))
    missing_globals = [name for name in GLOBAL_FILES if name not in names] if mode == 'course' else []
    if missing_globals:
        warnings.append('missing global files: ' + ', '.join(missing_globals))

    broken_links = find_broken_links(vault_dir, files, published_root)
    if broken_links:
        warnings.append(f'broken wikilinks found: {len(broken_links)}')

    placeholders = find_pattern_hits(vault_dir, files, PLACEHOLDER_PATTERNS)
    if placeholders:
        warnings.append(f'placeholder text found: {len(placeholders)} files')

    leakage = find_pattern_hits(vault_dir, files, LEAKAGE_PATTERNS)
    if leakage:
        warnings.append(f'possible prompt/process leakage: {len(leakage)} files')

    if '00_已有题目索引.md' in names and '00_题目覆盖与笔记补强.md' not in names:
        warnings.append('source-question index exists but coverage/strengthening file is missing')

    has_external_marker = any('外部补充' in p.read_text(encoding='utf-8', errors='replace') for p in files)
    if has_external_marker and '00_外部资料补充.md' not in names:
        warnings.append('external supplement markers exist but 00_外部资料补充.md is missing')

    index_health = None
    index_dir = resolve_index_dir(vault_dir, index_dir_arg)
    if index_dir.exists():
        if index_is_inside_vault(vault_dir, index_dir):
            warnings.append('index directory is inside the final vault; keep it beside the vault')
        index_health = read_json(index_dir / 'health.json', {}) or {}
        if index_health.get('status') == 'needs_review':
            warnings.append('index health needs review')
        for warning in index_health.get('warnings') or []:
            warnings.append('index warning: ' + warning)
    elif index_dir_arg:
        warnings.append(f'index directory not found: {index_dir}')

    duplicates = repeated_explanations(vault_dir, files)
    if duplicates:
        warnings.append(f'repeated explanations: {len(duplicates)}')
    missing_sources = [p.relative_to(vault_dir).as_posix() for p in files if re.search(r'type: (?:knowledge-point|chapter-note)', p.read_text('utf-8')) and not re.search(r'#page=\d+|第\s*\d+\s*页', p.read_text('utf-8'))]
    if missing_sources:
        warnings.append(f'notes without precise source pages: {len(missing_sources)}')
    status = 'ok' if not warnings else 'needs_review'
    return {
        'status': status, 'structural_status': status, 'semantic_review': 'not_performed_by_validator',
        'repeated_explanations': duplicates, 'missing_source_pages': missing_sources,
        'vault_dir': str(vault_dir),
        'index_dir': str(index_dir),
        'markdown_files': len(files),
        'nested_artifact_dirs': artifacts,
        'missing_global_files': missing_globals,
        'broken_links': broken_links[:50],
        'placeholder_hits': placeholders[:50],
        'leakage_hits': leakage[:50],
        'index_health': index_health,
        'warnings': warnings,
    }


def print_markdown(result):
    print('# Vault health\n')
    print(f"- Status: {result['status']}")
    print(f"- Vault: {result['vault_dir']}")
    print(f"- Index: {result['index_dir']}")
    print(f"- Markdown files: {result['markdown_files']}")
    if result['warnings']:
        print('\n## Warnings')
        for warning in result['warnings']:
            print(f"- {warning}")
    else:
        print('\nNo warnings.')
    if result['broken_links']:
        print('\n## Broken wikilinks')
        for item in result['broken_links'][:20]:
            print(f"- {item['file']}: [[{item['link']}]]")
    if result['placeholder_hits']:
        print('\n## Placeholder hits')
        for item in result['placeholder_hits'][:20]:
            print(f"- {item['file']}: {item['match']}")
    if result['leakage_hits']:
        print('\n## Leakage candidates')
        for item in result['leakage_hits'][:20]:
            print(f"- {item['file']}: {item['match']}")


def main():
    ap = argparse.ArgumentParser(description='Check a course note vault for common organization and hygiene issues.')
    ap.add_argument('vault_dir')
    ap.add_argument('--index-dir', default='')
    ap.add_argument('--mode', choices=['course', 'lightweight'], default='course')
    ap.add_argument('--published-root', help='Final vault location for resolving staged external relative links')
    ap.add_argument('--json', action='store_true')
    args = ap.parse_args()

    result = validate(Path(args.vault_dir), args.index_dir or None, args.mode, args.published_root)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print_markdown(result)
    return 0 if result['status'] == 'ok' else 1


if __name__ == '__main__':
    raise SystemExit(main())
