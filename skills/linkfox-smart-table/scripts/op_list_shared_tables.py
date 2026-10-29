#!/usr/bin/env python3
"""智能表格-共享给我的表 - LinkFox Skill
调用 /smartTable/listSharedTables 接口。

列出**当前团队内、别人共享给我**的多维表及其下的数据表（我能看见、且不是我创建的）。

⚠️ 出参是**两层**的，与 listMyTables 同一形状：顶层 notebooks（多维表，total 是容器数），
数据表在 notebooks[].tables[] 里。按表名找 tableId 要遍历两层。
同一个容器返回的表可能不是它的全部内容 —— 只嵌我有权看的那几张。
在多维表上有协作角色时，还会带 dashboards / folders / pages / applications（仪表盘 / 文件夹 / 页面 / 应用，
为空时不出现），其中的 itemId 是 deleteNotebookItem 要的 id；只被共享了其中某几张表的看不到这四组。
表和这些内容带 folderId 时表示在哪个文件夹里。
身份来自网关注入的头，脚本不传任何用户/团队参数。
传 notebookId 只看这一个多维表（不回 looseTables）；它是我自己创建的时 404，并提示改用 listMyTables。

Usage:
  python smart_table.py listSharedTables                       # 默认第 1 页、每页 100
  python smart_table.py listSharedTables '{"page":2}'           # 指定分页
  python smart_table.py listSharedTables '{"notebookId":"nbkXXX"}'  # 只看一个多维表
  python smart_table.py listSharedTables '{}' --inline          # 强制全量打印到 stdout
"""

import json
import os
import sys
import time
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

API_PATH = "/smartTable/listSharedTables"
SLUG = "linkfox-smart-table-list-shared-tables"

# 响应 <= 该字节数时落盘后额外全量打印到 stdout；超过则只打摘要
SMALL_THRESHOLD = 8000

# linkfox_paths.py 由 scaffold 从 linkfoxagent-v2/_shared 复制到本目录 scripts/，原样不改。
from linkfox_paths import get_api_base, resolve_data_path


def get_api_url():
    return get_api_base() + API_PATH


def get_api_key():
    key = os.environ.get("LINKFOX_AGENT_API_KEY") or os.environ.get("LINKFOXAGENT_API_KEY")
    if not key:
        print(
            "API Key not configured. Please complete authorization first:\n"
            "1. Visit https://agent.linkfox.com -> 设置 -> API KEY to obtain your Key\n"
            "2. Set the environment variable: export LINKFOX_AGENT_API_KEY=your-key-here",
            file=sys.stderr,
        )
        sys.exit(1)
    return key


def call_api(params):
    req = Request(
        get_api_url(),
        data=json.dumps(params, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": get_api_key(),  # 值即 key 本身，不加任何前缀
            "Content-Type": "application/json; charset=utf-8",
            "User-Agent": "LinkFox-Skill/2.0",
            "SESSION_ID": os.environ.get("SESSION_ID", ""),
            "MESSAGE_ID": os.environ.get("MESSAGE_ID", ""),
            "MODE_ID": os.environ.get("MODE_ID", ""),
            "APP_NAME": os.environ.get("APP_NAME", ""),
        },
        method="POST",
    )
    try:
        with urlopen(req, timeout=120) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as e:
        body = e.read().decode("utf-8") if e.fp else ""
        try:
            return json.loads(body) if body else {"errcode": e.code, "errmsg": f"HTTP {e.code}: {e.reason}"}
        except Exception:
            return {"errcode": e.code, "errmsg": f"HTTP {e.code}: {e.reason}", "details": body}
    except URLError as e:
        return {"errcode": 0, "errmsg": f"Connection failed: {e.reason}"}


def _find_main_list(obj):
    """递归找到元素数最多的 list 字段。不写死字段名，适配任意结构。"""
    best = (None, None, -1)

    def walk(node, path):
        nonlocal best
        if isinstance(node, list):
            if len(node) > best[2]:
                best = (path, node, len(node))
        elif isinstance(node, dict):
            for k, v in node.items():
                walk(v, f"{path}.{k}" if path else k)

    walk(obj, "")
    return best[0], best[1]


# 多维表里数据表以外的四类内容：出参数组名 → (deleteNotebookItem 的 itemType, 给人看的名字)
NOTEBOOK_ITEM_ARRAYS = (
    ("dashboards", "dashboard", "仪表盘"),
    ("folders", "folder", "文件夹"),
    ("pages", "page", "页面"),
    ("applications", "application", "应用"),
)


def _folder_label(folder_id, folder_names):
    """「在哪个文件夹里」。folders 不在出参里时（只有表级共享）只能给 id。"""
    if not folder_id:
        return ""
    name = folder_names.get(folder_id)
    return f"  [在文件夹 {name!r} 里]" if name is not None else f"  [在文件夹 {folder_id} 里]"


def _summarize_tables(tables, indent, folder_names=None):
    """一行一张数据表：名字 + tableId（+ 所在文件夹）。这是 agent 真正要找的东西。"""
    folder_names = folder_names or {}
    for table in tables:
        if not isinstance(table, dict):
            continue
        folder = _folder_label(table.get("folderId"), folder_names)
        print(f"{indent}- {table.get('name')!r}  {table.get('tableId')}{folder}")


def _summarize_notebook(notebook):
    """一个多维表：表头一行计数，下面先列数据表，再列仪表盘 / 文件夹 / 页面 / 应用。

    返回 (表数, 有没有这四类内容)。
    """
    tables = notebook.get("tables") if isinstance(notebook.get("tables"), list) else []
    items = {
        key: [x for x in notebook.get(key) if isinstance(x, dict)]
        for key, _, _ in NOTEBOOK_ITEM_ARRAYS
        if isinstance(notebook.get(key), list) and notebook.get(key)
    }
    folder_names = {f.get("itemId"): f.get("name") for f in items.get("folders", [])}

    counts = [f"{len(tables)} 张表"] + [
        f"{len(items[key])} 个{label}" for key, _, label in NOTEBOOK_ITEM_ARRAYS if key in items
    ]
    print()
    print(f"  [{notebook.get('name')!r}]  {notebook.get('notebookId')}  ({'、'.join(counts)})")
    _summarize_tables(tables, "    ", folder_names)
    for key, item_type, label in NOTEBOOK_ITEM_ARRAYS:
        if key not in items:
            continue
        print(f"    {label}（{key}，itemType={item_type}）：")
        for item in items[key]:
            folder = _folder_label(item.get("folderId"), folder_names)
            print(f"      - {item.get('name')!r}  {item.get('itemId')}{folder}")
    return len(tables), bool(items)


def summarize(result):
    """打印紧凑摘要。

    ⚠️ 出参是**两层**的（多维表 → 数据表），所以这里刻意**不用**通用的"找最大 list"启发式：
    那个办法不会下钻到 notebooks[i].tables，只会挑中 notebooks 或 looseTables.tables，
    然后把前 3 个容器整个 dump 出来 —— 而摘要分支恰恰是响应大、agent 最需要按名字找
    tableId 的时候。按层级列成「容器 → 表」才有用。

    没有 notebooks 字段时回落到通用逻辑：部署窗口里 skill 可能撞上还没更新的后端
    （那时返回的是旧的扁平 tables），回落能让它至少不瞎。
    """
    if not isinstance(result, dict):
        print(f"Response type: {type(result).__name__}")
        print(json.dumps(result, ensure_ascii=False)[:500])
        return

    print(f"Top-level keys: {list(result.keys())}")
    for k in ("errcode", "errmsg", "total", "perPage", "currentPage"):
        if k in result and isinstance(result[k], (int, float, bool, str)):
            print(f"  {k}: {result[k]}")

    notebooks = result.get("notebooks")
    if not isinstance(notebooks, list):
        # 旧形状（扁平 tables）或未知形状：回落到通用启发式
        list_path, main_list = _find_main_list(result)
        if list_path is not None and main_list:
            sample = main_list[:3]
            print()
            print(f"Main list field: `{list_path}` (length={len(main_list)})")
            print(f"Sample (first {len(sample)} of {len(main_list)}):")
            print(json.dumps(sample, indent=2, ensure_ascii=False))
        return

    total_tables = 0
    has_items = False
    print()
    print(f"多维表 {len(notebooks)} 个（total={result.get('total')} 是容器数）：")
    for notebook in notebooks:
        if not isinstance(notebook, dict):
            continue
        table_count, notebook_has_items = _summarize_notebook(notebook)
        total_tables += table_count
        has_items = has_items or notebook_has_items

    loose = result.get("looseTables")
    if isinstance(loose, dict):
        loose_tables = loose.get("tables") if isinstance(loose.get("tables"), list) else []
        total_tables += len(loose_tables)
        print()
        print(f"  [不属于任何多维表]  ({loose.get('total')} 张表)")
        _summarize_tables(loose_tables, "    ")

    print()
    print(f"数据表合计 {total_tables} 张。按表名找 tableId 时上面两处都要看。")
    if has_items:
        print(
            "仪表盘 / 文件夹 / 页面 / 应用的 itemId 给 deleteNotebookItem 用，itemType 取它所在的那一组；"
            "删文件夹会把 [在文件夹 … 里] 的那些一起带走。工作流不在这里，用 listWorkflows 看。"
        )
    print("没列出仪表盘 / 文件夹 / 页面 / 应用的多维表，可能只是你只被共享了其中某几张表，不代表里面没有。")


def _resolve_output_path(ts):
    """落到 <cwd>/linkfox/<date>/<session>/data/<slug>-<ts>.json。"""
    return resolve_data_path(SLUG, ts)


def main():
    argv = sys.argv[1:]
    inline = "--inline" in argv
    argv = [a for a in argv if a != "--inline"]

    # 无参即默认第 1 页：这个接口所有入参都是可选的
    raw = argv[0] if argv else "{}"
    try:
        params = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"Invalid parameter format: {e}", file=sys.stderr)
        sys.exit(1)

    result = call_api(params)

    serialized = json.dumps(result, ensure_ascii=False, indent=2)
    ts = int(time.time())
    out_path = _resolve_output_path(ts)
    try:
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(serialized)
        print(f"Saved full response: {out_path} ({len(serialized)} bytes)")
    except OSError as e:
        print(f"Failed to save to {out_path}: {e}", file=sys.stderr)

    # 业务失败不靠 HTTP 状态码判断，看 errcode
    if isinstance(result, dict) and result.get("errcode") != 200:
        print(
            f"Business error: errcode={result.get('errcode')} errmsg={result.get('errmsg')}",
            file=sys.stderr,
        )

    if inline or len(serialized.encode("utf-8")) <= SMALL_THRESHOLD:
        print(serialized)
    else:
        summarize(result)


if __name__ == "__main__":
    main()
