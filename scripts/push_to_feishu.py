#!/usr/bin/env python3
"""
Push daily report to Feishu Bitable.
Usage: python push_to_feishu.py --send-time "2026-03-31 18:00"
       python push_to_feishu.py --send-time "2026-03-31 18:00" --report-file /path/to/daily-report.md
"""

import json
import sys
import argparse
import datetime
import requests
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.parent  # skills/daily-report root
CONFIG_PATH = SCRIPT_DIR / "config.json"


def load_config():
    if not CONFIG_PATH.exists():
        print(f"Error: config.json not found at {CONFIG_PATH}")
        print("Please copy config.example.json to config.json and fill in your values.")
        sys.exit(1)
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)


def get_tenant_access_token(app_id: str, app_secret: str) -> str:
    resp = requests.post(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        json={"app_id": app_id, "app_secret": app_secret},
        headers={"Content-Type": "application/json; charset=utf-8"},
    )
    data = resp.json()
    if data.get("code") != 0:
        print(f"Error getting token: {data}")
        sys.exit(1)
    return data["tenant_access_token"]


def push_record(token: str, app_token: str, table_id: str, report_content: str, send_time_ms: int):
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
    }
    payload = {
        "fields": {
            "日报内容": report_content,
            "发送时间": send_time_ms,
        }
    }
    resp = requests.post(url, json=payload, headers=headers)
    data = resp.json()
    if data.get("code") != 0:
        print(f"Error creating record: {data}")
        sys.exit(1)
    record_id = data.get("data", {}).get("record", {}).get("record_id", "")
    print(f"[OK] Daily report pushed to Feishu Bitable (record_id: {record_id})")


def parse_send_time(time_str: str) -> int:
    """Parse 'YYYY-MM-DD HH:MM' to millisecond timestamp."""
    dt = datetime.datetime.strptime(time_str.strip(), "%Y-%m-%d %H:%M")
    return int(dt.timestamp() * 1000)


def main():
    parser = argparse.ArgumentParser(description="Push daily report to Feishu Bitable")
    parser.add_argument("--send-time", required=True, help="发送时间，格式: YYYY-MM-DD HH:MM")
    parser.add_argument("--report-file", default=None, help="日报文件路径（默认读今日 daily-report.md）")
    args = parser.parse_args()

    config = load_config()

    if args.report_file:
        report_path = Path(args.report_file)
    else:
        today = datetime.date.today().strftime("%Y-%m-%d")
        report_dir = Path(config.get("daily_report_dir", str(Path.home() / "daily-report")))
        report_path = report_dir / today / "daily-report.md"

    if not report_path.exists():
        print(f"Error: report file not found: {report_path}")
        sys.exit(1)

    report_content = report_path.read_text(encoding="utf-8")
    send_time_ms = parse_send_time(args.send_time)

    token = get_tenant_access_token(config["app_id"], config["app_secret"])
    push_record(token, config["bitable_app_token"], config["table_id"], report_content, send_time_ms)


if __name__ == "__main__":
    main()
