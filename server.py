#!/usr/bin/env python3
"""
项目跟踪系统 v2.0 - Flask + Jinja2
纯服务器端渲染，不依赖浏览器JavaScript
"""

import os
import json
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
PROJECTS_FILE = os.path.join(DATA_DIR, 'projects.json')


def load_data():
    """加载项目数据"""
    os.makedirs(DATA_DIR, exist_ok=True)
    if os.path.exists(PROJECTS_FILE):
        with open(PROJECTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'四建': [], '亚太': [], 'meetings': []}


def save_data(data):
    """保存项目数据"""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(PROJECTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


@app.route('/')
def index():
    """主页"""
    data = load_data()
    return render_template('index.html', 
                           projects=data,
                           active_tab=request.args.get('tab', 'all'))


@app.route('/toggle_task/<group>/<project_id>', methods=['POST'])
def toggle_task(group, project_id):
    """切换任务完成状态"""
    data = load_data()
    task_text = request.form.get('task_text', '')
    
    for p in data.get(group, []):
        if p.get('id') == project_id:
            for t in p.get('tasks', []):
                if t.get('text') == task_text:
                    t['done'] = not t.get('done', False)
                    break
            break
    
    save_data(data)
    return redirect(url_for('index', tab=group if group in ['四建', '亚太'] else 'all'))


@app.route('/update_priority/<group>/<project_id>', methods=['POST'])
def update_priority(group, project_id):
    """更新任务优先级"""
    data = load_data()
    task_text = request.form.get('task_text', '')
    
    for p in data.get(group, []):
        if p.get('id') == project_id:
            for t in p.get('tasks', []):
                if t.get('text') == task_text:
                    priorities = ['low', 'medium', 'high']
                    current = t.get('priority', 'medium')
                    idx = priorities.index(current)
                    t['priority'] = priorities[(idx + 1) % 3]
                    break
            break
    
    save_data(data)
    return redirect(url_for('index', tab=group if group in ['四建', '亚太'] else 'all'))


@app.route('/update_due/<group>/<project_id>', methods=['POST'])
def update_due(group, project_id):
    """更新任务截止日期"""
    data = load_data()
    task_text = request.form.get('task_text', '')
    new_due = request.form.get('due', '')
    
    for p in data.get(group, []):
        if p.get('id') == project_id:
            for t in p.get('tasks', []):
                if t.get('text') == task_text:
                    t['due'] = new_due
                    break
            break
    
    save_data(data)
    return redirect(url_for('index', tab=group if group in ['四建', '亚太'] else 'all'))


@app.route('/update_project/<group>/<project_id>', methods=['POST'])
def update_project(group, project_id):
    """更新项目信息"""
    data = load_data()
    
    for i, p in enumerate(data.get(group, [])):
        if p.get('id') == project_id:
            p['name'] = request.form.get('name', p.get('name', ''))
            p['status'] = request.form.get('status', p.get('status', ''))
            p['node'] = request.form.get('node', p.get('node', ''))
            p['deadline'] = request.form.get('deadline', p.get('deadline', ''))
            p['issues'] = request.form.get('issues', p.get('issues', ''))
            
            # 更新任务
            tasks_text = request.form.get('tasks', '')
            tasks = []
            for line in tasks_text.split('\n'):
                line = line.strip()
                if line:
                    done = line.startswith('✅')
                    text = line.replace('✅', '').replace('☐', '').strip()
                    tasks.append({'text': text, 'done': done, 'priority': 'medium', 'due': ''})
            p['tasks'] = tasks
            break
    
    save_data(data)
    return redirect(url_for('index', tab=group if group in ['四建', '亚太'] else 'all'))


if __name__ == '__main__':
    print("=" * 50)
    print("📋 项目跟踪系统 v2.0")
    print("=" * 50)
    print("🌐 访问地址: http://localhost:8765")
    print("📝 按 Ctrl+C 停止服务")
    print("=" * 50)
    app.run(host='0.0.0.0', port=8765, debug=False)
