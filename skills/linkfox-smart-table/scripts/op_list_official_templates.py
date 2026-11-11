#!/usr/bin/env python3
"""智能表格-查询官方模板 - LinkFox Skill。

调用公开接口 /agent-studio/table-template/list，只读，不自动复制或增加使用计数。
这是 Agent 后端接口，使用 LINKFOX_AGENT_USER_API_URL，不走表格工具网关、不需要 API Key。

Usage:
  python smart_table.py listOfficialTemplates
  python smart_table.py listOfficialTemplates '{"keyword":"选品","pageSize":24}'
  python smart_table.py listOfficialTemplates '{"platform":"amazon","stage":"selection"}'
  python smart_table.py listOfficialTemplates '{"id":"<列表返回的模板 ID>"}' --inline
"""

import json
import os
import sys
import time
from http.client import HTTPException
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from linkfox_paths import resolve_data_path

API_PATH = "/agent-studio/table-template/list"
SLUG = "linkfox-smart-table-list-official-templates"
SMALL_THRESHOLD = 8000


def get_api_url():
    """返回公开 Agent 接口地址，沿用同目录 onboarding 的环境配置。"""
    # 该路由由 Agent 后端公开提供；不能套用 /smartTable 的网关地址或要求用户授权。
    base = os.environ.get("LINKFOX_AGENT_USER_API_URL") or "https://agent-api.linkfox.com"
    return base.rstrip("/") + API_PATH


def call_api(params):
    """POST 查询参数，返回接口 JSON 对象；HTTP、网络或解析失败返回结构化错误。"""
    try:
        req = Request(
            get_api_url(),
            data=json.dumps(params, ensure_ascii=False).encode("utf-8"),
            headers={
                "Content-Type": "application/json; charset=utf-8",
                "User-Agent": "LinkFox-Skill/2.0",
                "SESSION_ID": os.environ.get("SESSION_ID", ""),
                "MESSAGE_ID": os.environ.get("MESSAGE_ID", ""),
                "MODE_ID": os.environ.get("MODE_ID", ""),
                "APP_NAME": os.environ.get("APP_NAME", ""),
            },
            method="POST",
        )
        with urlopen(req, timeout=120) as response:
            result = json.loads(response.read().decode("utf-8"))
        if not isinstance(result, dict):
            return {"errcode": 0, "errmsg": "Invalid response: expected a JSON object"}
        if result.get("errcode") in (None, 0, 200) and not isinstance(result.get("list"), list):
            return {"errcode": 502, "errmsg": "Invalid response: missing template list"}
        return result
    except HTTPError as e:
        try:
            result = json.loads(e.read().decode("utf-8")) if e.fp else None
        except (json.JSONDecodeError, UnicodeError, OSError, HTTPException):
            result = None
        if isinstance(result, dict):
            # 非 2xx 响应不能因为正文缺省成功码而被当成一次成功查询。
            if result.get("errcode") in (None, 0, 200):
                result["errcode"] = e.code
            result.setdefault("errmsg", f"HTTP {e.code}: {e.reason}")
            return result
        return {"errcode": e.code, "errmsg": f"HTTP {e.code}: {e.reason}"}
    except URLError as e:
        return {"errcode": 0, "errmsg": f"Connection failed: {e.reason}"}
    except (OSError, HTTPException) as e:
        return {"errcode": 0, "errmsg": f"Request failed: {e}"}
    except (json.JSONDecodeError, UnicodeError, ValueError) as e:
        return {"errcode": 0, "errmsg": f"Invalid request URL or JSON response: {e}"}


def _validate(params):
    """检查查询对象和字段类型；返回首条错误，合法时返回 None，默认值由后端处理。"""
    if not isinstance(params, dict):
        return "参数必须是 JSON 对象"
    allowed = {"id", "templateType", "platform", "stage", "categoryId", "keyword", "page", "pageSize"}
    extra = set(params) - allowed
    if extra:
        return f"不支持的参数：{', '.join(sorted(extra))}。分页用 pageSize，不是 perPage。"
    for key in ("id", "templateType", "platform", "stage", "categoryId", "keyword"):
        value = params.get(key)
        if value is not None and not isinstance(value, str):
            return f"{key} 必须是字符串"
    template_id = (params.get("id") or "").strip()
    if template_id and len(template_id) != 32:
        return "id 必须是列表返回的 32 字符模板 ID，不是 notebookId / tableId"
    for key in ("page", "pageSize"):
        value = params.get(key)
        if value is not None and (type(value) is not int or value < 1):
            return f"{key} 必须是大于等于 1 的整数"
    if params.get("pageSize") is not None and params["pageSize"] > 50:
        return "pageSize 最大为 50；更多模板请递增 page 分页查询"
    return None


def summarize(result):
    """摘要保留分页及前三条模板的选择信息；完整详情仍从落盘 JSON 按需读取。"""
    print(f"Top-level keys: {list(result.keys())}")
    for key in ("errcode", "errmsg", "total", "page", "pageSize"):
        if key in result:
            print(f"  {key}: {result[key]}")
    rows = result.get("list")
    if isinstance(rows, list):
        print(f"Main list field: `list` (length={len(rows)})")
        for row in rows[:3]:
            if not isinstance(row, dict):
                continue
            sample = {key: row.get(key) for key in ("id", "name", "templateType", "platform", "stage", "shareUrl")}
            # 详情图片与 HTML 往往很大，摘要只展示简介，避免前三条详情也塞满上下文。
            sample["intro"] = str(row.get("intro") or "")[:300]
            print(json.dumps(sample, ensure_ascii=False))
        if len(rows) > 3:
            print("这里只展示前 3 条；其余模板请从完整响应文件读取。")


def _resolve_output_path(ts):
    """通过共享路径工具返回本次查询的会话数据路径。"""
    return resolve_data_path(SLUG, ts)


def main():
    """解析可选查询参数，调用接口并始终落盘，按 UTF-8 大小决定 stdout 输出。"""
    argv = sys.argv[1:]
    inline = "--inline" in argv
    argv = [arg for arg in argv if arg != "--inline"]
    if len(argv) > 1:
        print("Usage: smart_table.py listOfficialTemplates '<JSON 参数>' [--inline]", file=sys.stderr)
        sys.exit(1)
    try:
        params = json.loads(argv[0] if argv else "{}")
    except json.JSONDecodeError as e:
        print(f"Invalid parameter format: {e}", file=sys.stderr)
        sys.exit(1)
    problem = _validate(params)
    if problem:
        print(problem, file=sys.stderr)
        sys.exit(1)

    result = call_api(params)
    serialized = json.dumps(result, ensure_ascii=False, indent=2)
    size = len(serialized.encode("utf-8"))
    try:
        out_path = _resolve_output_path(int(time.time()))
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(serialized)
        print(f"Saved full response: {out_path} ({size} bytes)")
    except OSError as e:
        print(f"Failed to save full response: {e}", file=sys.stderr)
        # 没有可回读的文件时不能只给摘要，否则大响应剩余模板会丢失。
        print(serialized)
        sys.exit(1)

    # 公开 Agent 接口与 /smartTable 不同：成功码可缺省或为 0 / 200，还要确认拿到了列表。
    if result.get("errcode") not in (None, 0, 200) or not isinstance(result.get("list"), list):
        print(
            f"Business error: errcode={result.get('errcode')} errmsg={result.get('errmsg')}",
            file=sys.stderr,
        )
    elif result.get("list") == []:
        print("没有匹配的已发布官方模板；可以更换关键词或筛选条件。")

    if inline or size <= SMALL_THRESHOLD:
        print(serialized)
    else:
        summarize(result)


if __name__ == "__main__":
    main()
