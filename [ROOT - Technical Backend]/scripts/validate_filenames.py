#!/usr/bin/env python3
import json, os, re, sys
from datetime import datetime

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
DRAFTS_DIR = os.path.join(ROOT, 'working_drafts')
OUTPUT_JSON = os.path.join(ROOT, 'proposal_master_dashboard_skeleton.json')

PATTERNS = [
    re.compile(r'^vol1_technical_.*\.(md|docx|pdf)$', re.I),
    re.compile(r'^vol2_pastperf_.*\.(md|docx|pdf)$', re.I),
    re.compile(r'^RPRTech_Phase I-.*\.(pdf|xlsx)$', re.I),
]

def is_allowed(name: str) -> bool:
    return any(p.search(name) for p in PATTERNS)

def scan_files():
    issues = []
    seen = []
    if not os.path.isdir(DRAFTS_DIR):
        return {'error': f'Missing drafts dir: {DRAFTS_DIR}', 'issues': [], 'ok': False}
    for name in sorted(os.listdir(DRAFTS_DIR)):
        path = os.path.join(DRAFTS_DIR, name)
        if os.path.isdir(path):
            continue
        if not is_allowed(name):
            issues.append({'file': name, 'issue': 'filename_not_matching_patterns'})
        seen.append({'file': name, 'size': os.path.getsize(path)})
    out = {
        'validation': {
            'checked_at': datetime.now().isoformat(timespec='seconds'),
            'drafts_dir': DRAFTS_DIR,
            'files_seen': seen,
            'issues': issues,
            'ok': len(issues) == 0,
        }
    }
    return out

def merge_into_dashboard(report):
    try:
        with open(OUTPUT_JSON, 'r', encoding='utf-8') as f:
            doc = json.load(f)
    except Exception:
        doc = {}
    doc['filename_validation'] = report['validation']
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
        f.write('\n')

def main():
    report = scan_files()
    print(json.dumps(report, indent=2))
    merge_into_dashboard(report)
    return 0 if report.get('validation',{}).get('ok') else 1

if __name__ == '__main__':
    sys.exit(main())
