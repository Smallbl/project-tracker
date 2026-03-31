#!/bin/bash
# 自动备份脚本 - 每天 23:30 执行
cd /Users/doujiang/.openclaw/workspace/work/projects
git add -A
if ! git diff --cached --quiet; then
    git commit -m "auto backup: $(date '+%Y-%m-%d %H:%M')"
    git push 2>&1
fi
