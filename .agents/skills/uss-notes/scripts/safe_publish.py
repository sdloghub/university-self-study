"""Publish staged files only against a known baseline. Dry run by default."""
import argparse
import hashlib
import json
import os
import shutil
from datetime import datetime
from pathlib import Path


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def inside(root, rel):
    path = root / rel
    path.resolve().relative_to(root.resolve())
    return path


def publish(staging, vault, state, baseline=None, apply=False):
    staging, vault, state = map(Path, (staging, vault, state))
    baseline = Path(baseline) if baseline else None
    known = json.loads(state.read_text('utf-8')).get('files', {}) if state.exists() else {}
    plan, conflicts, hashes = [], [], dict(known)
    for src in sorted(staging.rglob('*')):
        if src.is_symlink():
            raise ValueError('Staging must not contain symbolic links')
        if not src.is_file():
            continue
        rel = src.relative_to(staging).as_posix()
        dst = inside(vault, rel)
        new, old = digest(src), digest(dst)
        expected = known.get(rel)
        if expected is None and baseline:
            expected = digest(inside(baseline, rel))
        if dst.exists() and not dst.is_file():
            conflicts.append(rel)
        elif old == new:
            hashes[rel] = new
        elif old is not None and (expected is None or old != expected):
            conflicts.append(rel)
        else:
            plan.append((rel, src, dst, old))
            hashes[rel] = new
    result = {'status': 'conflict' if conflicts else 'ready', 'changed': len(plan),
              'conflicts': conflicts, 'applied': False}
    if not apply or conflicts:
        return result
    stamp = datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    backup = state.parent / 'publish-backups' / stamp
    for rel, src, dst, old in plan:
        # Recheck immediately before mutation; concurrent changes must abort.
        if digest(dst) != old:
            raise RuntimeError('File changed after planning: ' + rel)
        if old is not None:
            saved = inside(backup, rel)
            saved.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(dst, saved)
        dst.parent.mkdir(parents=True, exist_ok=True)
        temp = dst.with_name(dst.name + '.publishing-' + stamp)
        shutil.copy2(src, temp)
        os.replace(temp, dst)
    state.parent.mkdir(parents=True, exist_ok=True)
    temp = state.with_name(state.name + '.tmp-' + stamp)
    temp.write_text(json.dumps({'version': 1, 'files': hashes}, ensure_ascii=False, indent=2), 'utf-8')
    os.replace(temp, state)
    result.update(status='published', applied=True, backup=str(backup))
    return result


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    for option in ('staging', 'vault', 'state'):
        ap.add_argument('--' + option, required=True)
    ap.add_argument('--baseline')
    ap.add_argument('--apply', action='store_true')
    args = ap.parse_args()
    result = publish(**vars(args))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(1 if result['conflicts'] else 0)
