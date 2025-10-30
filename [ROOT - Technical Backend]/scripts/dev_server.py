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
    def _set_cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def _json(self, code, obj):
        body = json.dumps(obj).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self._set_cors()
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self._set_cors()
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
        # Serve static files under ROOT (dashboards, JSON, etc.)
        path = url.path.lstrip('/') or 'dashboard.html'
        fs_path = os.path.join(ROOT, path)
        if os.path.isdir(fs_path):
            fs_path = os.path.join(fs_path, 'index.html')
        if os.path.exists(fs_path):
            try:
                with open(fs_path, 'rb') as f:
                    data = f.read()
                self.send_response(200)
                ctype = 'text/html; charset=utf-8'
                if fs_path.endswith('.json'): ctype = 'application/json; charset=utf-8'
                if fs_path.endswith('.css'): ctype = 'text/css; charset=utf-8'
                if fs_path.endswith('.js'): ctype = 'application/javascript; charset=utf-8'
                self.send_header('Content-Type', ctype)
                self.send_header('Content-Length', str(len(data)))
                self._set_cors()
                self.end_headers()
                self.wfile.write(data)
                return
            except Exception as e:
                return self._json(500, {'ok': False, 'error': str(e)})
        return self._json(404, {'ok': False, 'error': 'not_found', 'path': path})

def main():
    host = '0.0.0.0'
    port = int(os.environ.get('DEV_SERVER_PORT', '8765'))
    httpd = HTTPServer((host, port), Handler)
    print(f"Dev server running on http://{host}:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    sys.exit(main())


