#!/usr/bin/env python3
"""智能表格-加列 - LinkFox Skill
调用 /smartTable/addFields 接口。

往已有表追加新列（一律加到最后）。

⚠️ **重名是报错，不是自动改名**：表里已有"价格"、再加"价格"会 400 且一列都不加。
   收到重名报错时**不要自己改名重试** —— 那正是这道检查要防的事
   （改了名之后调用方往"价格"写数据，实际写进了原有那一列，全程没有提示）。

Usage:
  python smart_table.py addFields '{"tableId":"tblXXX","fields":[{"name":"备注","type":"singleLineText"}]}'
  python smart_table.py addFields '<JSON>' --inline
"""

import json
import os
import sys
import time
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

API_PATH = "/smartTable/addFields"
SLUG = "linkfox-smart-table-add-fields"

# 响应 <= 该字节数时落盘后额外全量打印到 stdout；超过则只打摘要
SMALL_THRESHOLD = 8000

MAX_FIELDS = 50

# 与服务端 SMART_TABLE_FIELD_TYPES 一致。本地先拦一次是为了给"为什么这个类型不行"的解释，
# 服务端那份才是权威（本地漏了也只是多一次往返，不会放行）。
ALLOWED_TYPES = (
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
    # smart_table.py uploadAttachment，不能直接写 URL。加列不产生主字段，所以无首列限制。
    "attachment",
    # 查找引用（页面上的「查找引用」）：按条件从**你自己创建的**另一张表取值，算出来的、写不进去。
    # 必须带 lookup 配置，预检见 lookup_spec.py
    "lookup",
)
CHOICE_TYPES = ("singleSelect", "multipleSelect")

# linkfox_paths.py 由 scaffold 从 linkfoxagent-v2/_shared 复制到本目录 scripts/，原样不改。
from linkfox_paths import get_api_base, resolve_data_path
# 附件 AI 列的模型清单与 ai 预检（改模型只改那个文件）
from image_models import prepare_field_ai
# 查找引用列的 lookup 预检（三条建列脚本共用）
from lookup_spec import check_field_lookup


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
    """加完之后的完整表头，一行一个字段。"""
    if not isinstance(result, dict):
        print(f"Response type: {type(result).__name__}")
        print(json.dumps(result, ensure_ascii=False)[:500])
        return

    fields = result.get("fields") or []
    print(f"已加 {result.get('added')} 列；加完共 {len(fields)} 个字段：")
    for field in fields:
        if not isinstance(field, dict):
            continue
        marks = []
        if field.get("isPrimary"):
            marks.append("主字段")
        if field.get("isComputed"):
            marks.append("算出来的·写不进去")
        if field.get("isMultipleCellValue"):
            marks.append("多值·传数组")
        suffix = f"  [{' / '.join(marks)}]" if marks else ""
        print(f"  {field.get('name')}  ({field.get('type')}){suffix}")
        if field.get("choices"):
            print(f"      可选项: {field['choices']}")
        lookup = field.get("lookup")
        if isinstance(lookup, dict):
            source = lookup.get("tableName") or lookup.get("tableId")
            print(
                f"      查找引用: {source}.{lookup.get('fieldName')}"
                f"  计算方式={lookup.get('computeMode')}  条件={json.dumps(lookup.get('conditions'), ensure_ascii=False)}"
            )


def _resolve_output_path(ts):
    """落到 <cwd>/linkfox/<date>/<session>/data/<slug>-<ts>.json。"""
    return resolve_data_path(SLUG, ts)


def _validate(params):
    if not isinstance(params, dict):
        return "参数必须是 JSON 对象"
    table_id = params.get("tableId")
    if not table_id:
        return "缺少 tableId（以 tbl 开头）"
    if not str(table_id).startswith("tbl"):
        return (
            f"tableId 必须以 tbl 开头，收到 {table_id!r}。"
            "用 smart_table.py listMyTables 按表名找到它。"
        )

    fields = params.get("fields")
    if not isinstance(fields, list) or not fields:
        return "缺少 fields（非空数组）"
    if len(fields) > MAX_FIELDS:
        return f"一次最多加 {MAX_FIELDS} 列，收到 {len(fields)} 列；分批调用"

    seen = set()
    for index, field in enumerate(fields):
        where = f"fields[{index}]"
        if not isinstance(field, dict):
            return f"{where} 必须是对象"
        name = field.get("name")
        if not name or not isinstance(name, str):
            return f"{where} 缺少 name（列名）"
        if name in seen:
            # 服务端也拦，本地先拦是为了不白跑一趟网络
            return f"{where} 的列名 {name!r} 在本次请求里重复了；一次请求里每个列名只能出现一次"
        seen.add(name)

        field_type = field.get("type")
        if field_type not in ALLOWED_TYPES:
            return (
                f"{where} 的 type {field_type!r} 不支持。本接口只放这几种："
                f"{', '.join(ALLOWED_TYPES)}。"
                "公式/汇总/关联/人员这些要在页面上加。"
            )

        if field_type in CHOICE_TYPES:
            choices = field.get("choices")
            if not isinstance(choices, list) or not choices:
                return f"{where}（{field_type}）必须提供 choices"
            bad = [c for c in choices if not isinstance(c, dict) or not c.get("name")]
            if bad:
                return (
                    f"{where} 的 choices 每项必须是 {{\"name\": \"选项名\"}} 这样的对象，"
                    "不是字符串数组"
                )

        if "ai" in field:
            problem = prepare_field_ai(field, where)
            if problem:
                return problem
        problem = check_field_lookup(field, where)
        if problem:
            return problem
    return None


def main():
    argv = sys.argv[1:]
    inline = "--inline" in argv
    argv = [a for a in argv if a != "--inline"]

    if not argv:
        print(
            f"Usage: smart_table.py addFields "
            '\'{"tableId":"tblXXX","fields":[{"name":"备注","type":"singleLineText"}]}\' [--inline]',
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
        print(
            f"Business error: errcode={result.get('errcode')} errmsg={result.get('errmsg')}\n"
            "失败一般意味着**一列都没加**；唯一例外是报错里写了「普通列已建好，但这几列查找引用没建成」——"
            "那时普通列已经在表里了，只用 addFields 补点名的那几列查找引用，别把整批重发（会撞重名）。\n"
            "若是重名报错：不要自己改名重试，把撞上的列名告诉用户，让他决定复用已有列还是换名字。",
            file=sys.stderr,
        )
        print(serialized)
        return

    if inline or len(serialized.encode("utf-8")) <= SMALL_THRESHOLD:
        print(serialized)
    else:
        summarize(result)


if __name__ == "__main__":
    main()
