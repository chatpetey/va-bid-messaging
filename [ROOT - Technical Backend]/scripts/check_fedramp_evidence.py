#!/usr/bin/env python3
import json, os, sys
from datetime import datetime

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
MOVIUS_JSON = os.path.join(ROOT, 'movius_dependencies_skeleton_v2.json')
COMP_JSON   = os.path.join(ROOT, 'compliance_verification_skeleton_v2.json')
DASH_JSON   = os.path.join(ROOT, 'proposal_master_dashboard_skeleton.json')

REQUIRED_PROOF_TYPES = [
    ('doc', 'ATO Letter'),
    ('doc', 'SSP'),
    ('url', 'Marketplace'),
    ('screenshot', 'Marketplace Screenshot'),
    ('doc', '3PAO SAR'),
]


def read_json(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            t = f.read().strip() or '{}'
            return json.loads(t)
    except Exception:
        return {}


def write_json(path, obj):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write('\n')


def find_fedramp_dependency(doc):
    for dep in doc.get('dependencies', []):
        if dep.get('dependency_id') == 'movius_003':
            return dep
    return None


def verify_proof_chain(dep):
    evidence = dep.get('evidence', []) if isinstance(dep, dict) else []
    found = {
        'ato_letter': False,
        'ssp_summary': False,
        'marketplace_url': False,
        'marketplace_screenshot': False,
        'sar_3pao': False,
    }
    for e in evidence:
        t = e.get('type')
        ref = (e.get('ref') or '').lower()
        if t == 'doc' and 'ato' in ref:
            found['ato_letter'] = True
        if t == 'doc' and 'ssp' in ref:
            found['ssp_summary'] = True
        if t == 'url' and 'marketplace' in ref:
            found['marketplace_url'] = True
        if t == 'screenshot' and 'marketplace' in ref:
            found['marketplace_screenshot'] = True
        if t == 'doc' and ('3pao' in ref or 'sar' in ref):
            found['sar_3pao'] = True
    ok = all(found.values())
    return ok, found


def write_results(ok, found):
    now = datetime.now().isoformat(timespec='seconds')

    comp = read_json(COMP_JSON)
    comp.setdefault('fedramp_evidence_verification', {})
    comp['fedramp_evidence_verification'].update({
        'required': list(found.keys()),
        'present': [k for k,v in found.items() if v],
        'missing': [k for k,v in found.items() if not v],
        'verification_status': 'pass' if ok else 'fail',
        'verified_at': now
    })
    write_json(COMP_JSON, comp)

    dash = read_json(DASH_JSON)
    dash.setdefault('health_heartbeat', {})
    dash['health_heartbeat']['fedramp_evidence'] = {
        'last_run': now,
        'ok': bool(ok)
    }
    write_json(DASH_JSON, dash)


def main():
    d = read_json(MOVIUS_JSON)
    dep = find_fedramp_dependency(d)
    ok, found = verify_proof_chain(dep or {})
    print(json.dumps({'ok': ok, 'details': found}, indent=2))
    write_results(ok, found)
    return 0 if ok else 1

if __name__ == '__main__':
    sys.exit(main())
