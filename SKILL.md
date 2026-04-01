---
name: daily-report
description: Use when the user wants to write, update, or finalize their daily work report (日报), or when invoked at end of day to compose the final report through conversation.
---

# 日报 Skill

## 配置文件

所有个人信息从 `config.json` 读取（与本文件同目录）。参考 `config.example.json` 创建。

**必填字段：**
- **部门**：`department`
- **姓名**：`name`
- **日报根目录**：`daily_report_dir`，默认 `~/daily-report/`
- **今日目录**：`{daily_report_dir}/{今天日期YYYY-MM-DD}/`
- **工作日志**：今日目录下的 `worklog.md`（对话中自动维护）
- **最终日报**：今日目录下的 `daily-report.md`（调用 skill 时生成）

**可选字段（飞书推送）：**
- `app_id`、`app_secret`：飞书自建应用凭证
- `bitable_app_token`、`table_id`：目标多维表格
- 推送脚本：`scripts/push_to_feishu.py`（与本文件同目录）
- 若未配置飞书字段，跳过推送步骤即可，不影响日报生成

---

## 行为一：对话中自动维护 worklog（被动）

在任何对话中，只要用户提到了以下内容，立即将其追加写入当天的 `worklog.md`：
- 完成了某个任务或进展
- 遇到问题、尝试了什么方案、需要求助
- 有技术心得、业务洞察或反思

**追加规则**：
- 读取现有 worklog.md，将新内容合并到对应章节，不要覆盖已有内容
- 若 worklog.md 不存在，先用下方模板初始化再写入

### worklog.md 模板

```markdown
# 工作日志 - YYYY-MM-DD

## 完成的工作
<!-- 格式：- 【项目名称】[任务] 完成度X%：具体描述 -->

## 问题与求助
<!-- 格式：
问题：...
尝试：...
求助：...
-->

## 学习与思考
<!-- 格式：
新技能：...
业务洞察：...
反思：...
-->
```

---

## 行为二：生成最终日报并推送（主动，用户调用时）

### 步骤

1. **读取** `config.json`，获取 `name`、`department`
2. **读取** 今日目录下的 `worklog.md`，掌握已记录内容
3. **逐项确认已完成内容**（如有缺失或描述不清，向用户询问补充）
4. **询问明日计划**：请用户说明明天各项任务及优先级（高/中/低）
5. **补充学习与思考**（如 worklog 中无记录，询问用户）
6. **确认是否有 Blockers**（如无，填"无"）
7. **生成日报**，写入 `daily-report.md`，并在对话中完整输出供用户复制
8. **[可选] 推送到飞书**：仅当 `config.json` 中包含 `app_id`、`app_secret`、`bitable_app_token` 时执行：
   - 询问用户发送时间（格式：YYYY-MM-DD HH:MM）
   - 调用推送脚本：
     ```
     python <skill_dir>/scripts/push_to_feishu.py --send-time "YYYY-MM-DD HH:MM"
     ```
   - 输出 `[OK] Daily report pushed to Feishu Bitable` 即成功
   - 若 `config.json` 中无飞书相关字段，跳过此步骤

### 日报格式（严格照此输出，不得更改结构）

从 `config.json` 读取 `department` 和 `name` 填入对应位置：

```
📅 日报 - 【{department}】-[{name}] - YYYY年MM月DD日

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

**无问题时**：🚧 部分写 `无`
**无学习内容时**：💡 部分写 `无`

---

## 注意事项

- 今日目录由 session start hook 自动创建，skill 无需重复创建文件夹，只需读写文件
- 日期以系统当前日期为准（`datetime.date.today()`），不要猜测或硬编码
- 生成日报前必须通过对话确认明日计划，不可自行编造
- worklog 中没有记录的内容，询问用户后再填写，不可虚构
- 推送前必须与用户确认发送时间，不可自行填写
