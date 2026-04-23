---
name: weekly-report
description: Use when the user wants to generate a weekly work report (周报) by summarizing the current week's daily reports.
---

# 周报 Skill

## 配置文件

从 `config.json`（与 daily-report skill 同目录）读取：
- `name`：姓名
- `department`：部门
- `daily_report_dir`：日报根目录
- `weekly_report_dir`：周报输出目录

---

## 步骤

1. **获取当前日期**：运行 Bash `date` 命令，确认今天是周几

2. **推算本周日期范围**：以周一为起点（ISO 8601），计算本周一到周日的7个日期
   ```bash
   python -c "
   import datetime
   today = datetime.date.today()
   monday = today - datetime.timedelta(days=today.weekday())
   for i in range(7):
       d = monday + datetime.timedelta(days=i)
       print(d.strftime('%Y-%m-%d'))
   "
   ```

3. **读取本周日报**：遍历7个日期，尝试读取 `{daily_report_dir}/{YYYY-MM-DD}/daily-report.md`，跳过文件不存在的日期，不报错

4. **读取 config.json**：获取 `name`、`weekly_report_dir`

5. **汇总内容**：将各日报的"今日完成"、"问题与求助"章节整理归纳

6. **询问下周计划**：从各日报"明日计划"中提取线索，向用户确认下周任务及优先级，不可自行编造

7. **生成周报**：按下方格式写入：
   `{weekly_report_dir}/{name}-{周一YYYY.MM.DD}-{周日YYYY.MM.DD}-工作周报.md`

8. **在对话中输出完整内容**供用户复制

---

## 周报格式（严格照此输出，不得更改结构）

```
曾总、董老师：

以下是我本周的周报内容，请查收。

## 一、本周工作内容

1. **[项目名] - [工作主题]**：具体描述，突出做了什么、结果如何
...

## 二、下周工作计划

1. 【项目】[高/中/低优] 具体任务
...

## 三、遇到的问题和挑战 / 需要支持的地方

1. 问题描述、已尝试方案、需要的支持
...
```

**无 Blockers 时**：第三节写 `无`
**无下周计划时**：第二节写 `无`

---

## 归纳规则

- 同一项目多天的工作**合并为一条**，不要逐日罗列
- 从各日报"问题与求助"提取 Blockers，跨天相同问题**去重合并**
- 用简洁的技术语言描述，保留关键技术细节

---

## 注意事项

- 日期必须以 `date` 命令实际结果为准，不要猜测或硬编码
- 周一为一周第一天（ISO 8601），周日为最后一天
- 若某天没有日报文件，静默跳过，不影响周报生成
- **下周计划必须向用户确认后填写，不可虚构**
- 文件名格式：`{name}-{周一YYYY.MM.DD}-{周日YYYY.MM.DD}-工作周报.md`，例：`王林海-2026.04.20-2026.04.26-工作周报.md`
