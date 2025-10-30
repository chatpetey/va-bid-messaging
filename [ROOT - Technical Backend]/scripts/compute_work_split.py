#!/usr/bin/env python3
import json, os, sys
from datetime import datetime

try:
    import openpyxl  # for reading Schedule B.xlsx
except Exception:
    openpyxl = None

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
PRICE_XLSX = os.path.join(ROOT, 'RPRTech_Schedule B.xlsx')
REQ_JSON = os.path.join(ROOT, 'requirements_skeleton_v2.json')
COMP_JSON = os.path.join(ROOT, 'compliance_verification_skeleton_v2.json')
VOL_JSON  = os.path.join(ROOT, 'volumes_completion_skeleton_v2.json')
DASH_JSON = os.path.join(ROOT, 'proposal_master_dashboard_skeleton.json')


def read_prices_from_excel(xlsx_path):
    if not openpyxl:
        return {'ok': False, 'error': 'openpyxl_not_installed'}
    if not os.path.exists(xlsx_path):
        return {'ok': False, 'error': f'missing_xlsx:{xlsx_path}'}
    try:
        wb = openpyxl.load_workbook(xlsx_path, data_only=True)
        # Heuristic: use first sheet; expect columns: CLIN, Contractor (RPR/Movius), ExtendedPrice
        ws = wb.active
        rpr_total = 0.0
        movius_total = 0.0
        overall_total = 0.0
        for row in ws.iter_rows(min_row=2, values_only=True):
            if not row: continue
            clin = (row[0] or '').strip() if isinstance(row[0], str) else str(row[0] or '')
            contractor = (row[1] or '').strip().lower() if isinstance(row[1], str) else ''
            price = row[2]
            try:
                price_val = float(price or 0)
            except Exception:
                price_val = 0.0
            overall_total += price_val
            if 'rpr' in contractor:
                rpr_total += price_val
            elif 'movius' in contractor or 'sub' in contractor:
                movius_total += price_val
        pct_rpr = (rpr_total / overall_total * 100.0) if overall_total > 0 else 0.0
        pct_mov = (movius_total / overall_total * 100.0) if overall_total > 0 else 0.0
        return {
            'ok': True,
            'rpr_total': round(rpr_total, 2),
            'movius_total': round(movius_total, 2),
            'overall_total': round(overall_total, 2),
            'rpr_percentage': round(pct_rpr, 2),
            'movius_percentage': round(pct_mov, 2),
        }
    except Exception as e:
        return {'ok': False, 'error': str(e)}


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


def update_work_split_targets(calc):
    now = datetime.now().isoformat(timespec='seconds')
    ok = calc.get('ok', False) and calc.get('rpr_percentage', 0) >= 50.01

    # requirements_skeleton_v2.json.work_split_calculation
    req = read_json(REQ_JSON)
    req.setdefault('work_split_calculation', {})
    req['work_split_calculation'].update({
        'computed_source': 'auto_calculated_from_volume_iii_pricing',
        'rpr_tech_percentage': calc.get('rpr_percentage'),
        'movius_percentage': calc.get('movius_percentage'),
        'total_contract_value': calc.get('overall_total'),
        'last_calculated': now,
        'verification_status': 'pass' if ok else 'fail'
    })
    write_json(REQ_JSON, req)

    # compliance_verification_skeleton_v2.json.work_split_verification
    comp = read_json(COMP_JSON)
    comp.setdefault('work_split_verification', {})
    comp['work_split_verification'].update({
        'computed_source': 'auto_calculated_from_volume_iii_pricing',
        'rpr_tech_percentage': calc.get('rpr_percentage'),
        'movius_percentage': calc.get('movius_percentage'),
        'verification_status': 'pass' if ok else 'fail',
        'verified_at': now
    })
    write_json(COMP_JSON, comp)

    # volumes_completion_skeleton_v2.json.work_split_cross_reference
    vol = read_json(VOL_JSON)
    vol.setdefault('work_split_cross_reference', {})
    vol['work_split_cross_reference'].update({
        'rpr_tech_percentage': calc.get('rpr_percentage'),
        'movius_percentage': calc.get('movius_percentage'),
        'total_contract_value': calc.get('overall_total'),
        'verification_check': {
            'status': 'pass' if ok else 'fail',
            'last_calculated': now
        }
    })
    write_json(VOL_JSON, vol)

    # heartbeat into proposal_master_dashboard_skeleton.json
    dash = read_json(DASH_JSON)
    dash.setdefault('health_heartbeat', {})
    dash['health_heartbeat']['work_split'] = {
        'last_run': now,
        'ok': bool(ok),
        'rpr_percentage': calc.get('rpr_percentage'),
        'movius_percentage': calc.get('movius_percentage')
    }
    write_json(DASH_JSON, dash)


def main():
    calc = read_prices_from_excel(PRICE_XLSX)
    print(json.dumps(calc, indent=2))
    update_work_split_targets(calc)
    return 0 if calc.get('ok') else 1

if __name__ == '__main__':
    sys.exit(main())
