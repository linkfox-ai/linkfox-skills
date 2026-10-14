#!/usr/bin/env python3
"""智能表格-往已有多维表里加一张数据表 - LinkFox Skill
调用 /smartTable/addTable 接口。

往**已有的多维表（容器）**里加一张数据表，需要 notebookId（`nbk` 开头）。
没有 notebookId、要从零开始建的，用 create-table（那条会连容器一起建）。

只建**表结构**，不接受初始数据（建完再调 createRecords 写入；不是 updateRecords——那条只能改已有行）。
**表名不保证唯一**：同一个容器里同名反复加不报错也不复用（可能两张都叫「X」，
也可能第二张被加上「 2」后缀，取决于后端引擎）—— 认 tableId，别按表名找表。

Usage:
  python smart_table.py addTable '{"notebookId":"nbkXXXX","name":"竞品对比"}'
  python smart_table.py addTable '{"notebookId":"nbkXXXX","name":"竞品对比","fields":[{"name":"标题","type":"singleLineText"},{"name":"价格","type":"number"}]}'
"""

import json
import os
import sys
import time
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

API_PATH = "/smartTable/addTable"
SLUG = "linkfox-smart-table-add-table"

# 响应 <= 该字节数时落盘后额外全量打印到 stdout；超过则只打摘要
SMALL_THRESHOLD = 8000

# 允许的字段类型。刻意只放"自足"的几种——只看字段定义本身就能建出来，
# 不需要引用别的表/别的字段。与后端 SMART_TABLE_FIELD_TYPES 一致，
# 也与 create-table 那条完全同一份（两条路面对的是同一个问题：哪些类型能一次填对）。
FIELD_TYPES = (
    "singleLineText",
    "longText",
    "number",
    "singleSelect",
    "multipleSelect",
    "date",
    "checkbox",
    "rating",
    # image 存的是图片外链（一个字符串），服务端建列时翻成「单行文本 + 图片展示形态」。
    # 服务端**不校验**取值是不是合法 URL，写什么存什么；不是图片时前端画占位图。
    "image",
    # attachment 存的是文件（我们自己的存储）。建列无需选项；往格子里放图走
    # smart_table.py uploadAttachment，不能直接写 URL。
    "attachment",
)

# 首列（主字段）不能用的类型。
# ⚠️ 这一条对 addTable **成立**（加的是一张新表，第一个字段会被设为主字段），
# 但对 add-fields（往已有表加列）**不成立**——加列永远不产生主字段。别顺手统一。
NON_PRIMARY_TYPES = ("checkbox", "attachment")

# 选项类字段必须给 choices
CHOICE_TYPES = ("singleSelect", "multipleSelect")

# linkfox_paths.py 由 scaffold 从 linkfoxagent-v2/_shared 复制到本目录 scripts/，原样不改。
from linkfox_paths import get_api_base, resolve_data_path
# 附件 AI 列的模型清单与 ai 预检（改模型只改那个文件）
from image_models import prepare_field_ai


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


def summarize(result):
    """打印紧凑摘要。加表的响应很小，正常走不到这里。"""
    if not isinstance(result, dict):
        print(f"Response type: {type(result).__name__}")
        print(json.dumps(result, ensure_ascii=False)[:500])
        return
    print(f"Top-level keys: {list(result.keys())}")
    for k in ("errcode", "errmsg", "notebookId", "tableId", "name", "url", "createdTime"):
        if k in result and isinstance(result[k], (int, float, bool, str)):
            print(f"  {k}: {result[k]}")
    fields = result.get("fields")
    if isinstance(fields, list):
        print(f"  fields ({len(fields)}): {json.dumps(fields, ensure_ascii=False)}")


def _resolve_output_path(ts):
    """落到 <cwd>/linkfox/<date>/<session>/data/<slug>-<ts>.json。"""
    return resolve_data_path(SLUG, ts)


def _validate(params):
    """本地预检。把 agent 最容易填错的几处在发请求前挡掉，并给出人话原因。"""
    if not isinstance(params, dict):
        return "参数必须是 JSON 对象"

    notebook_id = params.get("notebookId")
    if not notebook_id:
        # 最可能的情形：照着别的 smart-table skill 传了 tableId。
        # 那些接口都按 tableId 寻址，只有这条按容器寻址。
        if params.get("tableId"):
            return (
                "addTable 要的是 notebookId（多维表/容器 id，`nbk` 开头），不是 tableId。"
                "tableId 指的是一张已经存在的数据表，而这条接口是要**新建**一张表。"
                "用 smart_table.py listMyTables 查出目标多维表的 notebookId"
                "（在出参的 notebooks[].notebookId 里）"
            )
        return (
            "缺少 notebookId（要加到哪个多维表下面，`nbk` 开头）。"
            "从 create-table 的出参、或 list-my-tables / list-shared-tables 的 notebooks[].notebookId 拿"
        )
    if not str(notebook_id).startswith("nbk"):
        return (
            f"notebookId={notebook_id!r} 看起来不是多维表 id —— 它应该以 `nbk` 开头。"
            "`tbl` 开头的是数据表 id（读写记录用的），`bse` 开头的是内部概念、这套接口不接受"
        )
    if not params.get("name"):
        return "缺少 name（新数据表的表名）"
    if "records" in params:
        return (
            "加表不接受初始数据（records）。先加表，拿到 tableId 后调 "
            "smart_table.py createRecords 写入"
            "（不是 update-records——那条只能改已有行，刚建的表是 0 行）"
        )

    fields = params.get("fields")
    if fields is None:
        return None
    if not isinstance(fields, list) or not fields:
        return "fields 要么不传（建一张单列文本表），要么是非空数组"
    for i, field in enumerate(fields):
        if not isinstance(field, dict):
            return f"fields[{i}] 必须是对象"
        if not field.get("name"):
            return f"fields[{i}] 缺少 name"
        ftype = field.get("type")
        if ftype not in FIELD_TYPES:
            return (
                f"fields[{i}].type={ftype!r} 不支持。可用类型：{', '.join(FIELD_TYPES)}。"
                "关联/公式/汇总/成员这些需要引用其他表或字段，第一版不开放，"
                "先用基础类型建表、再到前端补"
            )
        if ftype in CHOICE_TYPES and not field.get("choices"):
            return f"fields[{i}]（{ftype}）必须提供 choices，例如 [{{\"name\":\"待处理\"}}]"
        if i == 0 and ftype in NON_PRIMARY_TYPES:
            return (
                f"第一个字段不能是 {ftype} 类型（它是这张新表的主字段，要能代表一行的内容）。"
                "换成 singleLineText 之类，再把这个字段放到后面"
            )
        if "ai" in field:
            problem = prepare_field_ai(field, f"fields[{i}]")
            if problem:
                return problem
    return None


def main():
    argv = sys.argv[1:]
    inline = "--inline" in argv
    argv = [a for a in argv if a != "--inline"]

    if not argv:
        print(
            f"Usage: smart_table.py addTable "
            '\'{"notebookId":"nbkXXXX","name":"表名","fields":[{"name":"标题","type":"singleLineText"}]}\' [--inline]',
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        params = json.loads(argv[0])
    except json.JSONDecodeError as e:
        print(f"Invalid parameter format: {e}", file=sys.stderr)
        sys.exit(1)

    problem = _validate(params)
    if problem:
        print(problem, file=sys.stderr)
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
        # 404 = 那个 notebookId 在我的团队里查不到。可能是打错了、也可能属于别人的团队
        # ——两种情形服务端都回 404（看不见的东西连存在都不告诉你），所以提示要覆盖两者。
        hint = (
            "\n这个 notebookId 在你的团队里查不到：确认 id 没打错，"
            "并且它是用 list-my-tables / list-shared-tables 查出来的（跨团队的多维表不可见）。"
            if result.get("errcode") == 404
            else ""
        )
        print(
            f"Business error: errcode={result.get('errcode')} errmsg={result.get('errmsg')}{hint}",
            file=sys.stderr,
        )

    if inline or len(serialized.encode("utf-8")) <= SMALL_THRESHOLD:
        print(serialized)
    else:
        summarize(result)


if __name__ == "__main__":
    main()
