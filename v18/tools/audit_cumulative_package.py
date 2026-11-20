#!/usr/bin/env python3
"""Audit the final cumulative V18 tree, skill handoffs, and current manifests."""
from __future__ import annotations
import argparse, hashlib, json, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from v18 import validate

EXCLUDED={'.git','.venv','node_modules','__pycache__','.pytest_cache','.mypy_cache','.ruff_cache','target','build'}
def main():
    p=argparse.ArgumentParser(); p.add_argument('--root',type=Path,default=Path('.')); root=p.parse_args().root.resolve()
    report=validate(root); skills=list((root/'.agents/skills').glob('*/SKILL.md'))
    if len(skills)!=179: raise SystemExit(f'Expected 179 skills, found {len(skills)}')
    if any(f.is_file() and f.suffix in {'.pyc','.pyo'} and not any(x in EXCLUDED for x in f.relative_to(root).parts) for f in root.rglob('*')):
        raise SystemExit('Generated Python bytecode remains in the release tree')
    paths=sorted(f for f in root.rglob('*') if f.is_file() and not any(x in EXCLUDED for x in f.relative_to(root).parts))
    policies={'SHA256SUMS.txt':{'SHA256SUMS.txt','V14_SHA256SUMS.txt','V18_SHA256SUMS.txt'},
      'V18_SHA256SUMS.txt':{'V14_SHA256SUMS.txt','V18_SHA256SUMS.txt'},
      'V14_SHA256SUMS.txt':{'V14_SHA256SUMS.txt'}}
    counts={}
    for name,excluded in policies.items():
        manifest=root/name
        if not manifest.is_file(): raise SystemExit(f'Missing current manifest: {name}')
        seen=set(); rows=0
        for line in manifest.read_text(encoding='utf-8').splitlines():
            digest,rel=line.split('  ',1)
            if rel in seen: raise SystemExit(f'Duplicate checksum entry: {rel}')
            seen.add(rel); target=root/rel
            if not target.is_file() or hashlib.sha256(target.read_bytes()).hexdigest()!=digest: raise SystemExit(f'Checksum mismatch: {rel}')
            rows+=1
        expected={f.relative_to(root).as_posix() for f in paths if f.name not in excluded}
        if seen!=expected: raise SystemExit(f'{name} coverage mismatch: missing={len(expected-seen)}, extra={len(seen-expected)}')
        counts[name]=rows
    print('Cumulative V18 audit passed.')
    print(json.dumps({**report,'files':len(paths),'manifest_entries':counts},indent=2))
if __name__=='__main__': main()
