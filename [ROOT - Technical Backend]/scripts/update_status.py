#!/usr/bin/env python3
import json, os, sys, webbrowser
from datetime import datetime

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
DASHBOARD_HTML = os.path.join(ROOT_DIR, 'dashboard.html')
VOLUMES_HTML = os.path.join(ROOT_DIR, 'volumes_status.html')

JSON_FILENAMES = [
    'qa_responses_skeleton_v2.json',
    'requirements_skeleton_v2.json',
    'movius_dependencies_skeleton_v2.json',
    'compliance_verification_skeleton_v2.json',
    'volumes_completion_skeleton_v2.json',
    'deliverables_schedule_skeleton_v2.json',
    'rfp_document_skeleton_v2.json',
    'document_output_compliance_skeleton.json',
    'development_timeline_user_stories_skeleton.json',
    'proposal_master_dashboard_skeleton.json',
]

def json_paths():
    return [os.path.join(ROOT_DIR, n) for n in JSON_FILENAMES]

def read_json(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            t = f.read().strip() or '{}'
            return json.loads(t)
    except Exception as e:
        return {'__error__': str(e)}

def summarize(v):
    if isinstance(v, dict): return f'object · {len(v)} keys'
    if isinstance(v, list): return f'array · {len(v)} items'
    return type(v).__name__

def generate_dashboard():
    rows = []
    for p in json_paths():
        n = os.path.basename(p)
        ex = os.path.exists(p)
        mt = datetime.fromtimestamp(os.path.getmtime(p)).strftime('%Y-%m-%d %H:%M:%S') if ex else '—'
        sz = os.path.getsize(p) if ex else 0
        d = read_json(p)
        ok = not (isinstance(d, dict) and '__error__' in d)
        sm = d['__error__'] if not ok else summarize(d)
        rows.append((n, mt, sz, ok, sm))
    html = [
        '<!doctype html>','<meta charset="utf-8">','<title>Proposal Dashboard</title>',
        '<style>body{font-family:Segoe UI,Roboto,Arial;margin:24px} table{border-collapse:collapse;width:100%} th,td{border:1px solid #ccc;padding:8px 10px;text-align:left} th{background:#f5f7fb} .ok{color:#2e7d32}.bad{color:#c62828}.muted{color:#667} .nav a{margin-right:12px} .btn{display:inline-block;margin:4px 6px;padding:6px 10px;border:1px solid #ccc;border-radius:6px;background:#f7f9fc;cursor:pointer} .btn:disabled{opacity:.5;cursor:not-allowed} .toolbar{margin:12px 0 18px}</style>',
        '<div class="nav"><a href="dashboard.html">Dashboard</a><a href="volumes_status.html">Volumes Status</a></div>',
        '<h1>RPRTech · Proposal Status Dashboard</h1>',
        '<div class="toolbar">',
        '<button class="btn" onclick="runTask(\'validate_filenames\')">Validate Filenames</button>',
        '<button class="btn" onclick="runTask(\'check_page_counts\')">Check Page Counts</button>',
        '<button class="btn" onclick="runTask(\'compute_work_split\')">Compute Work Split</button>',
        '<button class="btn" onclick="runTask(\'check_fedramp_evidence\')">Check FedRAMP Evidence</button>',
        '<button class="btn" onclick="runTask(\'regen_dashboards\')">Regenerate Dashboards</button>',
        '<span id="runStatus" class="muted"></span>',
        '</div>',
        '<script>
async function runTask(task){
  const s = document.getElementById("runStatus");
  s.textContent = `Running ${task}...`;
  try{
    const res = await fetch(`http://127.0.0.1:8765/run?task=${task}`);
    const j = await res.json();
    s.textContent = `${task}: ${j.ok? 'OK' : 'FAILED'} (code ${j.returncode ?? 'n/a'})`;
  }catch(e){ s.textContent = `${task}: error ${e}`; }
}
</script>',
        '<table><tr><th>File</th><th>Updated</th><th>Size</th><th>Summary</th></tr>'
    ]
    for n,mt,sz,ok,sm in rows:
        cls = 'ok' if ok else 'bad'
        html.append(f'<tr><td>{n}</td><td class="muted">{mt}</td><td class="muted">{sz} B</td><td class="{cls}">{sm}</td></tr>')
    html.append('</table>')
    html.append(f'<p class="muted">Last generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>')
    with open(DASHBOARD_HTML,'w',encoding='utf-8') as f:
        f.write('\n'.join(html))

def generate_volumes_status():
    path = os.path.join(ROOT_DIR,'proposal_master_dashboard_skeleton.json')
    d = read_json(path)
    st = d.get('status',{}) if isinstance(d, dict) else {}
    overall = st.get('overall','Unknown')
    vol1 = st.get('vol1','Unknown')
    vol2 = st.get('vol2','Unknown')
    html = [
        '<!doctype html>','<meta charset="utf-8">','<title>Volumes Status</title>',
        '<style>body{font-family:Segoe UI,Roboto,Arial;margin:24px} .card{border:1px solid #ccc;border-radius:10px;padding:16px;margin-bottom:12px} .nav a{margin-right:12px} .btn{display:inline-block;margin:4px 6px;padding:6px 10px;border:1px solid #ccc;border-radius:6px;background:#f7f9fc;cursor:pointer}</style>',
        '<div class="nav"><a href="dashboard.html">Dashboard</a><a href="volumes_status.html">Volumes Status</a></div>',
        '<h1>Volumes Status</h1>',
        '<div class="card">'
        '<div style="margin-bottom:8px;"><button class="btn" onclick="runTask(\'validate_filenames\')">Validate Filenames</button> <button class="btn" onclick="runTask(\'check_page_counts\')">Check Page Counts</button> <button class="btn" onclick="runTask(\'regen_dashboards\')">Regenerate Dashboards</button> <span id="runStatus" class="muted"></span></div>'
        f'<div><strong>Overall:</strong> {overall}</div>'
        f'<div><strong>Volume 1 (Technical):</strong> {vol1}</div>'
        f'<div><strong>Volume 2 (Past Performance):</strong> {vol2}</div>'
        '</div>',
        '<script>
async function runTask(task){
  const s = document.getElementById("runStatus");
  s.textContent = `Running ${task}...`;
  try{
    const res = await fetch(`http://127.0.0.1:8765/run?task=${task}`);
    const j = await res.json();
    s.textContent = `${task}: ${j.ok? 'OK' : 'FAILED'} (code ${j.returncode ?? 'n/a'})`;
  }catch(e){ s.textContent = `${task}: error ${e}`; }
}
</script>'
    ]
    with open(VOLUMES_HTML,'w',encoding='utf-8') as f:
        f.write('\n'.join(html))

def cli(argv):
    if '--regen' in argv:
        generate_dashboard(); generate_volumes_status(); print('Dashboards regenerated.'); return 0
    if '--open' in argv:
        webbrowser.open('file://'+DASHBOARD_HTML); return 0
    print('Usage: update_status.py --regen | --open'); return 0

if __name__=='__main__': sys.exit(cli(sys.argv[1:]))
