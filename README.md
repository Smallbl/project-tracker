# 项目跟踪系统 (Project Tracker)

> 王的工作项目管理系统 | 招投标行业定制

## 功能

- 📋 项目卡片式展示
- ✅ 子任务勾选完成
- 📅 会议日程管理
- 🔄 数据本地持久化
- 📱 响应式设计

## 技术栈

- Python 3 (内置 http.server，无外部依赖)
- 原生 HTML/CSS/JS

## 启动

```bash
cd work/projects
python3 server.py
```

访问：`http://localhost:8765`

## 数据

- `data/projects.json` — 项目数据
- `index.html` — 前端页面（自动生成）
- `server.py` — Web 服务

## 开发

```bash
git add .
git commit -m "描述"
git push
```
