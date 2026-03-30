#!/usr/bin/env python3
"""
项目跟踪系统 - Web服务
"""

import json
import os
import mimetypes
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse

PORT = 8765
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
PROJECTS_FILE = os.path.join(DATA_DIR, "projects.json")
INDEX_FILE = os.path.join(BASE_DIR, "index.html")


class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        path = urlparse(self.path).path
        
        # API
        if path.startswith('/api/'):
            action = path[5:]
            if action == 'projects':
                if os.path.exists(PROJECTS_FILE):
                    with open(PROJECTS_FILE, 'r', encoding='utf-8') as f:
                        content = f.read()
                else:
                    content = '{}'
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(content.encode())
                return
        
        # index.html
        if path == '/' or path == '' or path == '/index.html':
            with open(INDEX_FILE, 'r', encoding='utf-8') as f:
                content = f.read()
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content.encode())
            return
        
        # Static files
        fpath = os.path.join(BASE_DIR, path.lstrip('/'))
        if os.path.isfile(fpath):
            with open(fpath, 'rb') as f:
                content = f.read()
            ext = os.path.splitext(fpath)[1].lower()
            mime_type = mimetypes.guess_type(fpath)[0] or 'application/octet-stream'
            self.send_response(200)
            self.send_header('Content-Type', mime_type)
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
            return
        
        self.send_error(404)
    
    def do_POST(self):
        if self.path == '/api/projects':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            os.makedirs(DATA_DIR, exist_ok=True)
            with open(PROJECTS_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"ok": True}).encode())
            return
        self.send_error(404)
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        pass


def run():
    print(f"Starting server on port {PORT}...")
    server = HTTPServer(('0.0.0.0', PORT), Handler)
    print(f"Server running at http://localhost:{PORT}")
    print(f"Press Ctrl+C to stop")
    server.serve_forever()


if __name__ == '__main__':
    run()
