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

# ===== 服务器代码更新检测 =====
SERVER_FILE = os.path.abspath(__file__)
_server_mtime = os.path.getmtime(SERVER_FILE)
_restart_warned = False

@app.after_request
def set_restart_header(response):
    """检测 server.py 是否被修改，每次响应都追加提示头"""
    global _server_mtime
    if os.path.getmtime(SERVER_FILE) > _server_mtime:
        response.headers['X-Server-Restart-Required'] = 'true'
        response.headers['X-Restart-Message'] = 'server.py 已更新，请重启服务器'
    return response


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


@app.route('/update_task_detail', methods=['POST'])
def update_task_detail():
    """更新任务的完整详情：任务名称、优先级、截止日期、意见备注"""
    data = load_data()
    group = request.form.get('group', '')
    project_id = request.form.get('project_id', '')
    task_text = request.form.get('task_text', '')
    new_text = request.form.get('text', '')
    priority = request.form.get('priority', 'medium')
    due = request.form.get('due', '')
    opinion = request.form.get('opinion', '')
    tab = request.form.get('tab', 'all')
    
    for p in data.get(group, []):
        if p.get('id') == project_id:
            for t in p.get('tasks', []):
                if t.get('text') == task_text:
                    t['text'] = new_text
                    t['priority'] = priority
                    t['due'] = due
                    t['opinion'] = opinion
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
    task_id = str(task_id)
    for task in data['tasks']:
        if str(task['id']) == task_id:
            for key in ['content', 'date', 'status', 'source', 'source_dept', 'priority', 'notes', 'tags', 'project']:
                if key in req:
                    task[key] = req[key]
            # 同步 done 和 status
            if 'status' in task:
                task['done'] = (task['status'] == 'completed')
            elif 'done' in task:
                task['status'] = 'completed' if task['done'] else 'pending'
            break
    with open('data/daily_tasks.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return json_response({'task': task})


@app.route('/api/daily_tasks/<int:task_id>', methods=['DELETE'])
def delete_daily_task(task_id):
    with open('data/daily_tasks.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    task_id = str(task_id)
    data['tasks'] = [t for t in data['tasks'] if str(t['id']) != task_id]
    with open('data/daily_tasks.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return json_response({'success': True})


@app.route('/api/daily_tasks/<int:task_id>/toggle', methods=['POST'])
def toggle_daily_task(task_id):
    with open('data/daily_tasks.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    task_id = str(task_id)
    for task in data['tasks']:
        if str(task['id']) == task_id:
            task['done'] = not task.get('done', False)
            task['status'] = 'completed' if task['done'] else 'pending'
            task['completed_at'] = str(datetime.now()) if task['done'] else None
            break
    with open('data/daily_tasks.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return json_response({'task': task})


# ==================== 项目管理 API（表单提交） ====================

@app.route('/add_company', methods=['POST'])
def add_company():
    """动态添加新公司"""
    company_name = request.form.get('company_name', '').strip()
    tab = request.form.get('tab', 'all')
    if not company_name:
        return redirect(url_for('index', tab=tab))
    data = load_data()
    # 避免重复添加
    if company_name not in data:
        data[company_name] = []
        save_data(data)
    return redirect(url_for('index', tab=tab))


@app.route('/get_companies', methods=['GET'])
def get_companies():
    """获取所有公司列表（用于动态下拉）"""
    data = load_data()
    companies = [g for g in data.keys() if g != 'meetings']
    return jsonify({'companies': companies})


@app.route('/add_project', methods=['POST'])
def add_project():
    """新建项目"""
    name = request.form.get('name', '').strip()
    group = request.form.get('group', '').strip()
    status = request.form.get('status', '进行中').strip()
    node = request.form.get('node', '').strip()
    deadline = request.form.get('deadline', '').strip()
    issues = request.form.get('issues', '').strip()
    tab = request.form.get('tab', 'all')

    # 立即添加的任务（可选）
    task_name = request.form.get('task_name', '').strip()
    task_priority = request.form.get('task_priority', 'medium').strip()
    task_due = request.form.get('task_due', '').strip()
    task_opinion = request.form.get('task_opinion', '').strip()

    if not name or not group:
        return redirect(url_for('index', tab=tab))

    data = load_data()
    if group not in data:
        data[group] = []
    if group == 'meetings':
        return redirect(url_for('index', tab=tab))

    # 生成项目ID（动态根据公司名生成）
    prefix = ''.join([c for c in group if c.isalnum()])[:8].lower()
    existing_ids = [p['id'] for p in data.get(group, []) if p['id'].startswith(prefix)]
    nums = [int(x.split('-')[-1]) for x in existing_ids if x.split('-')[-1].isdigit()]
    next_num = max(nums) + 1 if nums else 1
    project_id = f'{prefix}-{str(next_num).zfill(3)}'

    tasks = []
    if task_name:
        tasks.append({
            'text': html.escape(task_name),
            'done': False,
            'priority': task_priority if task_priority in ['low', 'medium', 'high'] else 'medium',
            'due': task_due,
            'opinion': html.escape(task_opinion),
            'createdAt': datetime.now().strftime('%Y-%m-%d')
        })

    new_project = {
        'id': project_id,
        'name': html.escape(name),
        'status': status,
        'node': html.escape(node),
        'deadline': deadline,
        'issues': html.escape(issues),
        'tasks': tasks,
        'status_text': status,
        'status_color': ''
    }
    data[group].insert(0, new_project)
    save_data(data)
    return redirect(url_for('index', tab=tab if tab in ['all', '四建', '亚太', 'meetings'] else 'all') + f'#project-{project_id}')


@app.route('/delete_project', methods=['POST'])
def delete_project():
    """删除项目"""
    group = request.form.get('group', '').strip()
    project_id = request.form.get('project_id', '').strip()
    tab = request.form.get('tab', 'all')

    data = load_data()
    if group in data and group != 'meetings':
        data[group] = [p for p in data[group] if p.get('id') != project_id]

    save_data(data)
    return redirect(url_for('index', tab=tab if tab in ['all', '四建', '亚太', 'meetings'] else 'all'))


@app.route('/add_task', methods=['POST'])
def add_task():
    """在项目下添加任务"""
    group = request.form.get('group', '').strip()
    project_id = request.form.get('project_id', '').strip()
    task_name = request.form.get('task_name', '').strip()
    priority = request.form.get('priority', 'medium').strip()
    due = request.form.get('due', '').strip()
    opinion = request.form.get('opinion', '').strip()
    createdAt = request.form.get('createdAt', '').strip()
    tab = request.form.get('tab', 'all')

    if not group or not project_id or not task_name:
        return redirect(url_for('index', tab=tab if tab in ['all', '四建', '亚太', 'meetings'] else 'all') + f'#project-{project_id}')

    data = load_data()
    if group not in data or group == 'meetings':
        return redirect(url_for('index', tab=tab))

    for p in data[group]:
        if p.get('id') == project_id:
            p.setdefault('tasks', []).append({
                'text': html.escape(task_name),
                'done': False,
                'priority': priority if priority in ['low', 'medium', 'high'] else 'medium',
                'due': due,
                'opinion': html.escape(opinion),
                'createdAt': createdAt or datetime.now().strftime('%Y-%m-%d')
            })
            break

    save_data(data)
    return redirect(url_for('index', tab=tab if tab in ['all', '四建', '亚太', 'meetings'] else 'all') + f'#project-{project_id}')


@app.route('/delete_task', methods=['POST'])
def delete_task():
    """删除任务"""
    group = request.form.get('group', '').strip()
    project_id = request.form.get('project_id', '').strip()
    task_text = request.form.get('task_text', '').strip()
    tab = request.form.get('tab', 'all')

    data = load_data()
    if group in data and group != 'meetings':
        for p in data[group]:
            if p.get('id') == project_id:
                p['tasks'] = [t for t in p.get('tasks', []) if t.get('text') != task_text]
                break

    save_data(data)
    return redirect(url_for('index', tab=tab if tab in ['all', '四建', '亚太', 'meetings'] else 'all') + f'#project-{project_id}')


# ==================== 每日任务统计 API ====================

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
