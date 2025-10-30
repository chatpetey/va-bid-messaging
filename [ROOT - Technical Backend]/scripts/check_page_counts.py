#!/usr/bin/env python3
import json, os, sys
from datetime import datetime

try:
    import pypdf
except Exception:
    pypdf = None

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
DRAFTS_DIR = os.path.join(ROOT, 'working_drafts')
OUTPUT_JSON = os.path.join(ROOT, 'proposal_master_dashboard_skeleton.json')


def pdf_page_count(path: str) -> int:
    if not pypdf:
        return -1
    with open(path, 'rb') as f:
        reader = pypdf.PdfReader(f)
        return len(reader.pages)


def scan_counts():
    counts = []
    if not os.path.isdir(DRAFTS_DIR):
        return {'error': f'Missing drafts dir: {DRAFTS_DIR}', 'ok': False}
    for name in sorted(os.listdir(DRAFTS_DIR)):
        path = os.path.join(DRAFTS_DIR, name)
        if os.path.isdir(path):
            continue
        pages = None
        status = 'unsupported'
        if name.lower().endswith('.pdf'):
            c = pdf_page_count(path)
            if c >= 0:
                pages = c
                status = 'ok'
            else:
                status = 'pypdf_missing'
        counts.append({'file': name, 'pages': pages, 'status': status})
    return {
        'page_counts': counts,
        'checked_at': datetime.now().isoformat(timespec='seconds'),
        'ok': True,
    }


def merge_into_dashboard(report):
    try:
        with open(OUTPUT_JSON, 'r', encoding='utf-8') as f:
            doc = json.load(f)
    except Exception:
        doc = {}
    doc['page_counts'] = report
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
        f.write('\n')


def main():
    rep = scan_counts()
    print(json.dumps(rep, indent=2))
    merge_into_dashboard(rep)
    return 0

if __name__ == '__main__':
    sys.exit(main())
