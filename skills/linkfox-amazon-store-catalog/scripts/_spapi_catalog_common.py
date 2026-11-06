"""Catalog 参数映射、依赖检查与公共调用器适配；不缓存响应。"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Optional
from urllib.parse import quote

import call_api as api

REQUIRED_SKILL = "linkfox-amazon-store-auth"
DEPENDENCY_EXIT_CODE = 42
CATALOG_ITEMS_V2022 = "2022-04-01"
CATALOG_ITEMS_V2020 = "2020-12-01"
API_PATH = "/spApi/developerProxy"
SLUG = "linkfox-amazon-store-catalog"


def ensure_auth_skill_available(caller: str = "catalog script") -> None:
    here = Path(__file__).resolve().parent
    checker = here / "check_auth_dependency.py"
    if not checker.exists():
        payload = {
            "missingSkill": REQUIRED_SKILL,
            "reason": f"check_auth_dependency.py not found next to {caller}",
        }
        print(f"DEPENDENCY_MISSING: {json.dumps(payload, ensure_ascii=False)}", file=sys.stderr)
        sys.exit(DEPENDENCY_EXIT_CODE)
    try:
        result = subprocess.run(
            [sys.executable, str(checker)],
            capture_output=True,
            text=True,
            timeout=10,
        )
    except Exception as exc:  # pragma: no cover
        payload = {"missingSkill": REQUIRED_SKILL, "reason": str(exc)}
        print(f"DEPENDENCY_MISSING: {json.dumps(payload, ensure_ascii=False)}", file=sys.stderr)
        sys.exit(DEPENDENCY_EXIT_CODE)
    if result.stderr:
        sys.stderr.write(result.stderr)
        if not result.stderr.endswith("\n"):
            sys.stderr.write("\n")
    if result.returncode != 0:
        sys.exit(DEPENDENCY_EXIT_CODE)


def encode_path_segment(value: str) -> str:
    return quote(str(value).strip(), safe="")


def str_list(val: object, name: str) -> list[str]:
    if val is None:
        return []
    if isinstance(val, str):
        return [x.strip() for x in val.split(",") if x.strip()]
    if isinstance(val, list):
        return [str(x).strip() for x in val if str(x).strip()]
    print(f"{name} must be a string or string[]", file=sys.stderr)
    sys.exit(1)


def norm_marketplace_ids(params: dict, *, max_count: Optional[int] = None) -> list[str]:
    mids = params.get("marketplaceIds")
    if mids is None:
        mid = params.get("marketplaceId")
        if mid is not None:
            mids = [str(mid).strip()]
        else:
            return []
    else:
        mids = str_list(mids, "marketplaceIds")
    if max_count is not None and len(mids) > max_count:
        print(f"marketplaceIds length must be ≤ {max_count}", file=sys.stderr)
        sys.exit(1)
    return mids


def resolve_catalog_items_version(params: dict) -> str:
    ver = str(params.get("catalogItemsVersion") or CATALOG_ITEMS_V2022).strip()
    if ver not in (CATALOG_ITEMS_V2022, CATALOG_ITEMS_V2020):
        print(
            f"catalogItemsVersion must be {CATALOG_ITEMS_V2022} or {CATALOG_ITEMS_V2020}",
            file=sys.stderr,
        )
        sys.exit(1)
    return ver


def catalog_items_path(version: str, suffix: str = "items") -> str:
    return f"catalog/{version}/{suffix}"


def load_cli_params() -> dict:
    if len(sys.argv) < 2:
        return {}
    if sys.argv[1] in ("--help", "-h"):
        print(f"用法: {Path(sys.argv[0]).name} '<JSON 参数>' [--inline] [--no-cache]")
        print("请按 references/api.md 提供对应操作的 sellerId、region、站点和商品或搜索条件。")
        raise SystemExit(0)
    try:
        params = json.loads(sys.argv[1])
        if not isinstance(params, dict):
            print("JSON 参数必须为对象。", file=sys.stderr)
            raise SystemExit(1)
        return params
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)


def require_seller_region(params: dict) -> tuple[str, str]:
    for f in ("sellerId", "region"):
        if f not in params:
            print(f"Missing required field: {f}", file=sys.stderr)
            sys.exit(1)
    return str(params["sellerId"]), str(params["region"])


def _normal_response(http_status, proxy):
    """遵循公共基础规则；0 和 false 不视为空，错误体不作成功解析。"""
    if type(http_status) is not int or not 200 <= http_status < 300 or not isinstance(proxy, dict):
        return False
    code = proxy.get("errcode")
    if code is None:
        return True
    if isinstance(code, str):
        code = code.strip()
        if not code:
            return True
        if len(code) != 3 or not code.isascii() or not code.isdigit():
            return False
        code = int(code)
    return type(code) in (int, float) and 200 <= code < 300 and code % 1 == 0


def _merge_body(result, proxy, result_key):
    try:
        status = int(proxy.get("httpStatus") or 0)
    except (TypeError, ValueError):
        return
    if status != 200:
        return
    raw = proxy.get("body")
    if raw is None or not str(raw).strip():
        result[result_key] = None
        return
    try:
        result[result_key] = json.loads(str(raw))
    except json.JSONDecodeError:
        result[result_key] = None
        result[result_key + "Raw"] = raw


def run_proxy(operation, region, path, seller_id, query_string, *, result_key, version=None):
    """封装目录查询结果，由公共调用器处理 LinkFox HTTP 请求与响应落盘。"""
    params = {"region": region, "path": path, "method": "GET", "sellerId": seller_id}
    if query_string:
        params["queryString"] = query_string

    # 输出只允许位于当前工作目录；实际会话数据目录也须在请求前检查。
    root = Path.cwd() / "linkfox"
    root.mkdir(parents=True, exist_ok=True)

    transport = api.call_api
    previous_path = api._resolve_output_path
    previous_root = api._SESSION_CACHE.get("_root")
    previous_gateway = os.environ.get("LINKFOX_TOOL_GATEWAY")

    def with_catalog_result(api_path, request_params):
        http_status, proxy = transport(api_path, request_params)
        result = {
            "developerProxy": proxy,
            "resolvedPath": path,
            "queryString": query_string,
            "transportHttpStatus": http_status,
        }
        if version is not None:
            result["catalogItemsVersion"] = version
        if _normal_response(http_status, proxy):
            _merge_body(result, proxy, result_key)
        return http_status, result

    if not previous_gateway:
        os.environ["LINKFOX_TOOL_GATEWAY"] = (
            os.environ.get("STORE_API_BASE_URL")
            or os.environ.get("SPAPI_BASE_URL")
            or "https://tool-gateway.linkfox.com"
        )
    api._SESSION_CACHE["_root"] = str(root)
    api.call_api = with_catalog_result
    try:
        ts = time.time()
        session_id = api._session_id(ts)
        if (not session_id or session_id in (".", "..")
                or "/" in session_id or "\\" in session_id or Path(session_id).drive):
            raise ValueError("SESSION_ID 必须为单个非空目录名，不能包含路径或目录跳转。")
        data_dir = root / time.strftime("%Y-%m-%d", time.localtime(ts)) / session_id / "data"
        if not data_dir.resolve().is_relative_to(root.resolve()):
            raise ValueError("响应保存路径必须位于当前工作目录的 linkfox/ 内。")
        # 固定本次输出路径，避免检查根目录成功后，实际 data 目录才报错。
        # 保留微秒命名，防止同秒多次查询互相覆盖。
        output_path = Path(api.resolve_data_path(f"{SLUG}-{operation}", ts))
        if not output_path.resolve().is_relative_to(root.resolve()):
            raise ValueError("响应保存路径必须位于当前工作目录的 linkfox/ 内。")
        with tempfile.TemporaryFile(dir=output_path.parent):
            pass
        api._resolve_output_path = lambda _slug, _ts: str(output_path)
        argv = [json.dumps(params, ensure_ascii=False), "--no-cache"]
        if "--inline" in sys.argv[1:]:
            argv.append("--inline")
        api.run(API_PATH, f"{SLUG}-{operation}", argv=argv)
        # 公共脚本将写盘异常打印到 stderr；封装不能把未保存的结果当作完成。
        if not output_path.is_file() or output_path.stat().st_size == 0:
            raise OSError(f"完整响应未能保存到 {output_path}。")
    finally:
        api.call_api = transport
        api._resolve_output_path = previous_path
        if previous_root is None:
            api._SESSION_CACHE.pop("_root", None)
        else:
            api._SESSION_CACHE["_root"] = previous_root
        if previous_gateway is None:
            os.environ.pop("LINKFOX_TOOL_GATEWAY", None)
        else:
            os.environ["LINKFOX_TOOL_GATEWAY"] = previous_gateway
