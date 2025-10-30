#!/usr/bin/env python3
import json, os, subprocess, sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
SCRIPTS = os.path.join(ROOT, 'scripts')

TASKS = {
    'validate_filenames': [sys.executable, os.path.join(SCRIPTS, 'validate_filenames.py')],
    'check_page_counts': [sys.executable, os.path.join(SCRIPTS, 'check_page_counts.py')],
    'compute_work_split': [sys.executable, os.path.join(SCRIPTS, 'compute_work_split.py')],
    'check_fedramp_evidence': [sys.executable, os.path.join(SCRIPTS, 'check_fedramp_evidence.py')],
    'regen_dashboards': [sys.executable, os.path.join(SCRIPTS, 'update_status.py'), '--regen'],
}

class Handler(BaseHTTPRequestHandler):
    def _json(self, code, obj):
        body = json.dumps(obj).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Access-Control-Allow-Origin', 'http://localhost')
        self.send_header('Access-Control-Allow-Origin', 'http://127.0.0.1')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        url = urlparse(self.path)
        if url.path == '/health':
            return self._json(200, {'ok': True})
        if url.path == '/run':
            q = parse_qs(url.query)
            task = (q.get('task') or [''])[0]
            cmd = TASKS.get(task)
            if not cmd:
                return self._json(400, {'ok': False, 'error': 'unknown_task', 'task': task})
            try:
                proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
                return self._json(200, {
                    'ok': proc.returncode == 0,
                    'returncode': proc.returncode,
                    'stdout': proc.stdout,
                    'stderr': proc.stderr,
                    'task': task,
                })
            except Exception as e:
                return self._json(500, {'ok': False, 'error': str(e), 'task': task})
        return self._json(404, {'ok': False, 'error': 'not_found'})

def main():
    host = '127.0.0.1'
    port = int(os.environ.get('DEV_SERVER_PORT', '8765'))
    httpd = HTTPServer((host, port), Handler)
    print(f"Dev server running on http://{host}:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    sys.exit(main())


