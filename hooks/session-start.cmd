@echo off
python -c "
import os, datetime
today = datetime.date.today().strftime('%%Y-%%m-%%d')
base = os.environ.get('DAILY_REPORT_DIR', os.path.join(os.path.expanduser('~'), 'daily-report'))
folder = os.path.join(base, today)
os.makedirs(folder, exist_ok=True)
wl = os.path.join(folder, 'worklog.md')
if not os.path.exists(wl) or os.path.getsize(wl) == 0:
    with open(wl, 'w', encoding='utf-8') as f:
        f.write('# 工作日志 - ' + today + '\n\n## 完成的工作\n\n## 问题与求助\n\n## 学习与思考\n')
"
