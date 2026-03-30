#!/usr/bin/env python3
"""
项目跟踪系统 - Web服务
启动后访问 http://localhost:8765
"""

import json
import os
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse
from pathlib import Path

PORT = 8765
BASE_DIR = Path(__file__).parent.resolve()
DATA_DIR = BASE_DIR / "data"
PROJECTS_FILE = DATA_DIR / "projects.json"

INDEX_FILE = BASE_DIR / "index.html"


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
        
        # Static files
        fpath = BASE_DIR / path.lstrip('/')
        if fpath.is_file():
            self.path = str(fpath)
            return SimpleHTTPRequestHandler.do_GET(self)
        
        # index.html fallback
        if path == '/' or path == '' or path == '/index.html':
            self.path = str(INDEX_FILE)
            return SimpleHTTPRequestHandler.do_GET(self)
        
        self.send_error(404)
    
    def do_POST(self):
        if self.path == '/api/projects':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
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
        pass  # 静默日志


def run():
    PROJECTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    # 如果数据文件不存在，创建默认数据
    if not PROJECTS_FILE.exists():
        default_data = {
            "四建": [], "亚太": [], "meetings": []
        }
        with open(PROJECTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_data, f, ensure_ascii=False, indent=2)
    
    os.chdir(BASE_DIR)
    server = HTTPServer(('0.0.0.0', PORT), Handler)
    
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        lan_ip = s.getsockname()[0]
        s.close()
    except:
        lan_ip = '127.0.0.1'
    
    print(f"✅ 项目跟踪系统已启动!")
    print(f"📍 访问地址: http://localhost:{PORT}")
    print(f"🌐 局域网: http://{lan_ip}:{PORT}")
    print(f"📁 静态文件: {BASE_DIR}")
    print(f"\n按 Ctrl+C 停止服务")
    server.serve_forever()


if __name__ == '__main__':
    run()
