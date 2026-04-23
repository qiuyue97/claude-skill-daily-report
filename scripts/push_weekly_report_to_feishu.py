#!/usr/bin/env python3
"""
Push weekly report to Feishu Docs (docx).
Usage: python push_weekly_report_to_feishu.py --report-file /path/to/report.md
       python push_weekly_report_to_feishu.py --report-file /path/to/report.md --folder-token <token>
"""

import json
import sys
import argparse
import requests
from pathlib import Path

import io
if isinstance(sys.stdout, io.TextIOWrapper) and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

SCRIPT_DIR = Path(__file__).parent.parent  # skills/daily-report root
CONFIG_PATH = SCRIPT_DIR / "config.json"
FEISHU_BASE = "https://open.feishu.cn/open-apis"


def load_config():
    if not CONFIG_PATH.exists():
        print(f"Error: config.json not found at {CONFIG_PATH}")
        print("Please copy config.example.json to config.json and fill in your values.")
        sys.exit(1)
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)


def get_tenant_access_token(app_id: str, app_secret: str) -> str:
    resp = requests.post(
        f"{FEISHU_BASE}/auth/v3/tenant_access_token/internal",
        json={"app_id": app_id, "app_secret": app_secret},
        headers={"Content-Type": "application/json; charset=utf-8"},
    )
    data = resp.json()
    if data.get("code") != 0:
        print(f"Error getting token: {data}")
        sys.exit(1)
    return data["tenant_access_token"]


def create_document(token: str, title: str, folder_token: str = "") -> str:
    """Create an empty Feishu Doc and return its document_id."""
    body = {"title": title}
    if folder_token:
        body["folder_token"] = folder_token
    resp = requests.post(
        f"{FEISHU_BASE}/docx/v1/documents",
        json=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8",
        },
    )
    data = resp.json()
    if data.get("code") != 0:
        print(f"Error creating document: {data}")
        sys.exit(1)
    doc_id = data["data"]["document"]["document_id"]
    print(f"  Created document: {doc_id}")
    return doc_id


def convert_markdown(token: str, content: str) -> tuple[list[str], list[dict]]:
    """Convert Markdown to Feishu block tree. Returns (first_level_block_ids, blocks)."""
    resp = requests.post(
        f"{FEISHU_BASE}/docx/v1/documents/blocks/convert",
        json={"content_type": "markdown", "content": content},
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8",
        },
    )
    data = resp.json()
    if data.get("code") != 0:
        print(f"Error converting markdown: {data}")
        sys.exit(1)
    return data["data"]["first_level_block_ids"], data["data"]["blocks"]


def strip_readonly_fields(blocks: list[dict]) -> list[dict]:
    """Remove read-only fields (e.g. merge_info on table blocks) that cause insert errors."""
    cleaned = []
    for block in blocks:
        b = dict(block)
        # table and grid cells: strip merge_info
        for key in ("table", "grid", "table_cell", "grid_column"):
            if key in b and isinstance(b[key], dict):
                b[key] = {k: v for k, v in b[key].items() if k != "merge_info"}
        cleaned.append(b)
    return cleaned


def insert_blocks(token: str, doc_id: str, first_level_ids: list[str], blocks: list[dict]):
    """Insert block tree into document root in batches of 1000."""
    BATCH = 1000
    # Split first_level_ids into batches; all descendants sent with the first batch,
    # subsequent batches only contain the new top-level IDs (already present in blocks).
    for i in range(0, len(first_level_ids), BATCH):
        batch_ids = first_level_ids[i:i + BATCH]
        # On first batch send all blocks; on subsequent send only remaining ones
        batch_blocks = blocks if i == 0 else [b for b in blocks if b.get("block_id") in _all_descendants(batch_ids, blocks)]
        payload = {
            "children_id": batch_ids,
            "index": -1,
            "descendants": strip_readonly_fields(batch_blocks),
        }
        resp = requests.post(
            f"{FEISHU_BASE}/docx/v1/documents/{doc_id}/blocks/{doc_id}/descendant",
            json=payload,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json; charset=utf-8",
            },
        )
        data = resp.json()
        if data.get("code") != 0:
            print(f"Error inserting blocks (batch {i // BATCH + 1}): {data}")
            sys.exit(1)
    print(f"  Inserted {len(blocks)} blocks into document.")


def _all_descendants(root_ids: list[str], blocks: list[dict]) -> set[str]:
    """Collect all block IDs reachable from root_ids in the block tree."""
    id_map = {b["block_id"]: b for b in blocks if "block_id" in b}
    result = set()
    queue = list(root_ids)
    while queue:
        bid = queue.pop()
        if bid in result:
            continue
        result.add(bid)
        block = id_map.get(bid, {})
        queue.extend(block.get("children", []))
    return result


def derive_title(report_path: Path) -> str:
    """Extract title from filename, e.g. 王林海-2026.04.20-2026.04.26-工作周报.md → same without .md."""
    return report_path.stem


def main():
    parser = argparse.ArgumentParser(description="Push weekly report to Feishu Docs")
    parser.add_argument("--report-file", required=True, help="周报文件路径（.md）")
    parser.add_argument("--folder-token", default=None, help="目标文件夹 token（可选，覆盖 config）")
    args = parser.parse_args()

    config = load_config()

    app_id = config.get("weekly_app_id")
    app_secret = config.get("weekly_app_secret")
    if not app_id or not app_secret:
        print("Error: weekly_app_id and weekly_app_secret must be set in config.json")
        sys.exit(1)

    folder_token = args.folder_token or config.get("weekly_folder_token", "")

    report_path = Path(args.report_file)
    if not report_path.exists():
        print(f"Error: report file not found: {report_path}")
        sys.exit(1)

    report_content = report_path.read_text(encoding="utf-8")
    title = derive_title(report_path)

    print(f"Pushing weekly report: {title}")
    token = get_tenant_access_token(app_id, app_secret)
    doc_id = create_document(token, title, folder_token)
    first_level_ids, blocks = convert_markdown(token, report_content)
    insert_blocks(token, doc_id, first_level_ids, blocks)
    print(f"[OK] Weekly report pushed to Feishu Docs (document_id: {doc_id})")


if __name__ == "__main__":
    main()
