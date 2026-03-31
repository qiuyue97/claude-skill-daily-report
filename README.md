# claude-skill-daily-report

A Claude Code skill for automating daily work report (日报) writing. During conversations, Claude silently logs your work progress. At the end of the day, invoke the skill to compose the final report through a guided conversation.

---

## Features

- **Auto worklog**: Claude detects work-related content in any conversation and silently appends it to today's worklog
- **Date folder auto-creation**: A folder for today's date is created automatically every time you open Claude
- **End-of-day report**: Invoke `/daily-report` to fill in tomorrow's plan and any missing sections through conversation, then get the final formatted report ready to paste

---

## Installation

### 1. Copy the skill file

Copy `SKILL.md` to your personal Claude Code skills directory:

```
~/.claude/skills/daily-report/SKILL.md
```

On Windows:
```
C:\Users\<your-username>\.claude\skills\daily-report\SKILL.md
```

### 2. Add the global worklog rule to CLAUDE.md

Append the contents of `CLAUDE.md` in this repo to your global Claude config file:

```
~/.claude/CLAUDE.md
```

On Windows:
```
C:\Users\<your-username>\.claude\CLAUDE.md
```

This tells every Claude session (regardless of working directory) to silently record work-related content into today's worklog.

> Adjust the `Worklog 路径` in `CLAUDE.md` to match where you want daily reports stored on your machine.

### 3. Set up the SessionStart hook

Add the following to your `~/.claude/settings.json` (on Windows: `C:\Users\<your-username>\.claude\settings.json`):

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python -c \"import os,datetime; today=datetime.date.today().strftime('%Y-%m-%d'); folder='<YOUR_DAILY_REPORT_PATH>/'+today; os.makedirs(folder,exist_ok=True); wl=folder+'/worklog.md'; open(wl,'a',encoding='utf-8').write('' if os.path.exists(wl) and os.path.getsize(wl)>0 else '# 工作日志 - '+today+'\\n\\n## 完成的工作\\n\\n## 问题与求助\\n\\n## 学习与思考\\n')\""
          }
        ]
      }
    ]
  }
}
```

Replace `<YOUR_DAILY_REPORT_PATH>` with the actual path where you want daily report folders created (use forward slashes even on Windows), for example:

```
C:/Users/yourname/daily-report
```

If `settings.json` already has other content, merge the `hooks` block into the existing JSON rather than replacing the file.

This hook runs every time a Claude session starts and:
- Creates a folder named with today's date (e.g. `2026-03-31/`)
- Initializes an empty `worklog.md` inside it if one doesn't exist yet

---

## Usage

### During the day

Just work normally. Whenever you mention completing a task, hitting a blocker, or having a technical insight, Claude will silently append it to `<daily-report-path>/<today>/worklog.md`.

### End of day

Invoke the skill:

```
/daily-report
```

Claude will:
1. Read today's worklog
2. Confirm completed items with you
3. Ask for tomorrow's plan and priorities
4. Ask about any learnings or reflections (if not already logged)
5. Generate the final report and write it to `daily-report.md`

---

## Report format

```
📅 日报 - 【部门】-[姓名] - YYYY年MM月DD日

✅ 今日完成 (Done)
【项目名称】[任务] 完成度X%：具体描述...

🚧 问题与求助 (Blockers)
问题：...
尝试：...
求助：...

📅 明日计划 (Plan)
【项目】[高/中/低优] 具体任务...

💡 学习与思考 (Growth)
新技能：...
业务洞察：...
反思：...
```

Update the department and name fields in `SKILL.md` to match your own.
