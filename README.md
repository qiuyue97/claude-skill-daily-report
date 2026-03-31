# claude-skill-daily-report

A Claude Code plugin that automates daily work logging and report composition.

- Claude silently logs your work progress to a daily worklog during conversations
- A date folder is created automatically every time you open Claude (via SessionStart hook)
- At end of day, invoke `/daily-report` to fill in tomorrow's plan and compose the final formatted report

---

## Installation

### Step 1: Register the marketplace

```
/plugin marketplace add qiuyue97/claude-skill-daily-report
```

### Step 2: Enable the plugin

```
/plugin install daily-report@qiuyue97-skills
```

The plugin system will automatically:
- Download and cache the plugin
- Register the `SessionStart` hook to create today's date folder and initialize `worklog.md`
- Make `/daily-report` available as a skill

### Step 3: Set your report directory (optional)

By default, daily reports are saved to `~/daily-report/<YYYY-MM-DD>/`. To use a custom path, set the `DAILY_REPORT_DIR` environment variable:

```bash
# macOS / Linux — add to ~/.zshrc or ~/.bashrc
export DAILY_REPORT_DIR="/your/custom/path"
```

```powershell
# Windows — set in System Environment Variables
DAILY_REPORT_DIR=C:\your\custom\path
```

### Step 4: Enable auto-logging during conversations

The plugin handles the skill and hook, but auto-logging (Claude silently writing to the worklog as you work) requires a rule in your global `~/.claude/CLAUDE.md`.

Append the contents of [`CLAUDE.md`](./CLAUDE.md) from this repo to your `~/.claude/CLAUDE.md`, and update the worklog path to match your `DAILY_REPORT_DIR`.

---

## Usage

### During the day

Work normally. Whenever you mention completing a task, hitting a blocker, or a technical insight, Claude silently appends it to `<DAILY_REPORT_DIR>/<today>/worklog.md`.

### End of day

```
/daily-report
```

Claude will read today's worklog, confirm completed items, ask for tomorrow's plan and priorities, then write the final report to `daily-report.md`.

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

Update the department and name fields in `skills/daily-report/SKILL.md` to match your own.

---

## Manual installation

If you prefer not to use the plugin system:

1. Copy `skills/daily-report/SKILL.md` to `~/.claude/skills/daily-report/SKILL.md`
2. Append `CLAUDE.md` contents to `~/.claude/CLAUDE.md`
3. Add to `~/.claude/settings.json`:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python -c \"import os,datetime; today=datetime.date.today().strftime('%Y-%m-%d'); base=os.environ.get('DAILY_REPORT_DIR',os.path.expanduser('~/daily-report')); folder=os.path.join(base,today); os.makedirs(folder,exist_ok=True); wl=os.path.join(folder,'worklog.md'); open(wl,'a',encoding='utf-8').write('' if os.path.exists(wl) and os.path.getsize(wl)>0 else '# Worklog - '+today+'\\n\\n## Done\\n\\n## Blockers\\n\\n## Learning\\n')\""
          }
        ]
      }
    ]
  }
}
```

---

## Repository structure

```
.
├── .claude-plugin/
│   ├── plugin.json          # Plugin metadata
│   └── marketplace.json     # Marketplace registry
├── hooks/
│   ├── hooks.json           # Hook definitions (SessionStart)
│   ├── session-start.cmd    # Windows hook script
│   └── session-start.sh     # macOS/Linux hook script
├── skills/
│   └── daily-report/
│       └── SKILL.md         # Claude Code skill definition
├── CLAUDE.md                # Global worklog rule — append to ~/.claude/CLAUDE.md
└── README.md
```

---

## License

MIT
