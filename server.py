#!/usr/bin/env python3
"""
项目跟踪系统 v2.0 - Flask + Jinja2
纯服务器端渲染，不依赖浏览器JavaScript
"""

import os
import json
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, jsonify
import html

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
PROJECTS_FILE = os.path.join(DATA_DIR, 'projects.json')


def load_data():
    os.makedirs(DATA_DIR, exist_ok=True)
    if os.path.exists(PROJECTS_FILE):
        with open(PROJECTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'四建': [], '亚太': [], 'meetings': []}


def save_data(data):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(PROJECTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


@app.route('/')
def index():
    data = load_data()
    return render_template('index.html', 
                           projects=data,
                           active_tab=request.args.get('tab', 'all'))


@app.route('/toggle_task', methods=['POST'])
def toggle_task():
    data = load_data()
    group = request.form.get('group', '')
    project_id = request.form.get('project_id', '')
    task_text = request.form.get('task_text', '')
    tab = request.form.get('tab', 'all')
    
    for p in data.get(group, []):
        if p.get('id') == project_id:
            for t in p.get('tasks', []):
                if t.get('text') == task_text:
                    t['done'] = not t.get('done', False)
                    break
            break
    
    save_data(data)
    return redirect(url_for('index', tab=tab if tab in ['all', '四建', '亚太', 'meetings'] else 'all') + f"#project-{project_id}")


@app.route('/update_priority', methods=['POST'])
def update_priority():
    data = load_data()
    group = request.form.get('group', '')
    project_id = request.form.get('project_id', '')
    task_text = request.form.get('task_text', '')
    tab = request.form.get('tab', 'all')
    
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
    return redirect(url_for('index', tab=tab if tab in ['all', '四建', '亚太', 'meetings'] else 'all') + f"#project-{project_id}")


@app.route('/update_due', methods=['POST'])
def update_due():
    data = load_data()
    group = request.form.get('group', '')
    project_id = request.form.get('project_id', '')
    task_text = request.form.get('task_text', '')
    new_due = request.form.get('due', '')
    tab = request.form.get('tab', 'all')
    
    for p in data.get(group, []):
        if p.get('id') == project_id:
            for t in p.get('tasks', []):
                if t.get('text') == task_text:
                    t['due'] = new_due
                    break
            break
    
    save_data(data)
    anchor = f"project-{project_id}"
    return redirect(url_for('index', tab=tab if tab in ['all', '四建', '亚太', 'meetings'] else 'all') + f"#{anchor}")


@app.route('/clear_due', methods=['POST'])
def clear_due():
    data = load_data()
    group = request.form.get('group', '')
    project_id = request.form.get('project_id', '')
    task_text = request.form.get('task_text', '')
    tab = request.form.get('tab', 'all')
    
    for p in data.get(group, []):
        if p.get('id') == project_id:
            for t in p.get('tasks', []):
                if t.get('text') == task_text:
                    t['due'] = ''
                    break
            break
    
    save_data(data)
    return redirect(url_for('index', tab=tab if tab in ['all', '四建', '亚太', 'meetings'] else 'all') + f"#project-{project_id}")


@app.route('/update_project', methods=['POST'])
def update_project():
    data = load_data()
    group = request.form.get('group', '')
    project_id = request.form.get('project_id', '')
    tab = request.form.get('tab', 'all')
    
    for i, p in enumerate(data.get(group, [])):
        if p.get('id') == project_id:
            p['name'] = request.form.get('name', p.get('name', ''))
            p['status_text'] = request.form.get('status_text', '')
            p['status_color'] = request.form.get('status_color', '')
            p['node'] = request.form.get('node', p.get('node', ''))
            p['deadline'] = request.form.get('deadline', p.get('deadline', ''))
            p['issues'] = request.form.get('issues', p.get('issues', ''))
            
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
    return redirect(url_for('index', tab=tab if tab in ['all', '四建', '亚太', 'meetings'] else 'all'))


@app.route('/daily.html')
def daily():
    return render_template('daily.html')


@app.route('/update_task_name', methods=['POST'])
def update_task_name():
    data = load_data()
    group = request.form.get('group', '')
    project_id = request.form.get('project_id', '')
    old_text = request.form.get('old_text', '')
    new_text = request.form.get('new_text', '')
    tab = request.form.get('tab', 'all')
    
    for p in data.get(group, []):
        if p.get('id') == project_id:
            for t in p.get('tasks', []):
                if t.get('text') == old_text:
                    t['text'] = new_text
                    break
            break
    
    save_data(data)
    return redirect(url_for('index', tab=tab if tab in ['all', '四建', '亚太', 'meetings'] else 'all') + f"#project-{project_id}")


# ==================== 每日任务模块 API ====================

def json_response(data):
    return jsonify(data)

TASK_STATUSES = ['pending', 'in_progress', 'completed']
TASK_SOURCES = ['planned', 'temp']
TASK_PRIORITIES = ['low', 'medium', 'high']


@app.route('/api/daily_tasks', methods=['GET'])
def get_daily_tasks():
    date_filter = request.args.get('date')
    with open('data/daily_tasks.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    tasks = data.get('tasks', [])
    if date_filter:
        tasks = [t for t in tasks if t.get('date') == date_filter]
    return json_response({'tasks': tasks})


@app.route('/api/daily_tasks', methods=['POST'])
def create_daily_task():
    req = request.get_json()
    # 输入校验
    if not req.get('content', '').strip():
        return jsonify({'error': '任务内容不能为空'}), 400
    date_val = req.get('date', '').strip()
    if date_val:
        try:
            datetime.strptime(date_val, '%Y-%m-%d')
        except ValueError:
            return jsonify({'error': '日期格式错误，应为YYYY-MM-DD'}), 400
    with open('data/daily_tasks.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    data['last_id'] += 1
    new_task = {
        'id': data['last_id'],
        'content': html.escape(req.get('content', '')),
        'date': req.get('date', ''),
        'status': 'pending',
        'source': req.get('source', 'planned'),
        'source_dept': req.get('source_dept', ''),
        'priority': req.get('priority', 'medium'),
        'notes': html.escape(req.get('notes', '')),
        'tags': req.get('tags', []),
        'project': req.get('project', ''),
        'created_at': str(datetime.now()),
        'completed_at': None
    }
    data['tasks'].append(new_task)
    with open('data/daily_tasks.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return json_response({'task': new_task})


@app.route('/api/daily_tasks/<int:task_id>', methods=['PUT'])
def update_daily_task(task_id):
    req = request.get_json()
    with open('data/daily_tasks.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    for task in data['tasks']:
        if task['id'] == task_id:
            for key in ['content', 'date', 'status', 'source', 'source_dept', 'priority', 'notes', 'tags', 'project']:
                if key in req:
                    task[key] = req[key]
            if task['status'] == 'completed' and not task.get('completed_at'):
                task['completed_at'] = str(datetime.now())
            elif task['status'] != 'completed':
                task['completed_at'] = None
            break
    with open('data/daily_tasks.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return json_response({'task': task})


@app.route('/api/daily_tasks/<int:task_id>', methods=['DELETE'])
def delete_daily_task(task_id):
    with open('data/daily_tasks.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    data['tasks'] = [t for t in data['tasks'] if t['id'] != task_id]
    with open('data/daily_tasks.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return json_response({'success': True})


@app.route('/api/daily_tasks/<int:task_id>/toggle', methods=['POST'])
def toggle_daily_task(task_id):
    with open('data/daily_tasks.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    for task in data['tasks']:
        if task['id'] == task_id:
            task['status'] = 'completed' if task['status'] != 'completed' else 'pending'
            task['completed_at'] = str(datetime.now()) if task['status'] == 'completed' else None
            break
    with open('data/daily_tasks.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return json_response({'task': task})


@app.route('/api/daily_tasks/stats', methods=['GET'])
def daily_tasks_stats():
    date_filter = request.args.get('date', '')
    with open('data/daily_tasks.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    tasks = data.get('tasks', [])
    if date_filter:
        tasks = [t for t in tasks if t.get('date') == date_filter]
    total = len(tasks)
    completed = len([t for t in tasks if t.get('status') == 'completed'])
    pending = len([t for t in tasks if t.get('status') == 'pending'])
    in_progress = len([t for t in tasks if t.get('status') == 'in_progress'])
    temp_count = len([t for t in tasks if t.get('source') == 'temp'])
    return json_response({
        'total': total,
        'completed': completed,
        'pending': pending,
        'in_progress': in_progress,
        'temp_count': temp_count,
        'completion_rate': round(completed / total * 100, 1) if total > 0 else 0
    })


# ==================== 启动 ====================

if __name__ == '__main__':
    print("=" * 50)
    print("📋 项目跟踪系统 v2.0")
    print("=" * 50)
    print("🌐 访问地址: http://localhost:8765")
    print("📝 按 Ctrl+C 停止服务")
    print("=" * 50)
    app.run(host='0.0.0.0', port=8765, debug=False)
