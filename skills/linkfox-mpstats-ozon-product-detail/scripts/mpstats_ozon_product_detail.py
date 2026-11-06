#!/usr/bin/env python3
"""MPSTATS Ozon 单 SKU 详情查询。

用法：python mpstats_ozon_product_detail.py '<JSON 参数>' [--inline] [--no-cache]
校验商品编号，按规范化参数生成缓存键并提供 24 小时缓存；传输、归档与摘要委托公共调用器。
"""

import hashlib
import json
import os
import secrets
import sys
import time

import call_api as api_runner


API_PATH = "/mpstats/ozon/productDetail"
SLUG = "linkfox-mpstats-ozon-product-detail"
CACHE_TTL_SEC = 24 * 60 * 60


def normalize_params(params):
    if not isinstance(params, dict):
        raise ValueError("参数必须为 JSON 对象")
    if "productIds" in params:
        raise ValueError("请使用单个 productId；不接受 productIds 数组")
    if "productId" not in params:
        raise ValueError("缺少必填参数 productId")

    product_id = params["productId"]
    if isinstance(product_id, bool) or product_id is None:
        raise ValueError("productId 必须为单个整数或非空字符串")
    if isinstance(product_id, (list, dict)):
        raise ValueError("productId 必须为单个编号，不能是数组或对象")
    if not isinstance(product_id, (int, str)):
        raise ValueError("productId 必须为单个整数或非空字符串")
    if isinstance(product_id, str):
        product_id = product_id.strip()
        if not product_id:
            raise ValueError("productId 必须为非空字符串或整数")

    normalized = dict(params)
    normalized["productId"] = product_id
    return normalized

def _cache_key(params):
    raw = json.dumps(params, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def _cache_path(params):
    cwd = os.getcwd()
    path = os.path.join(cwd, "linkfox", ".cache", SLUG)
    os.makedirs(path, exist_ok=True)
    return os.path.join(path, f"{SLUG}-{_cache_key(params)}.json")


def _load_cache(path):
    try:
        if not os.path.isfile(path):
            return None
        if time.time() - os.path.getmtime(path) > CACHE_TTL_SEC:
            return None
        with open(path, encoding="utf-8") as f:
            payload = json.load(f)
        if isinstance(payload, dict):
            # 本地标记损坏不应丢弃仍可复用的业务数据并触发额外收费请求。
            if not isinstance(payload.get("_cache"), dict):
                payload["_cache"] = {}
            payload["_cache"]["hit"] = True
        return payload
    except (OSError, UnicodeError, json.JSONDecodeError):
        return None


def _save_cache(path, payload):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
    except OSError:
        pass


def _prepare_output_root():
    """请求前验证当前目录可写，禁止公共调用器回退到其他目录。"""
    root = os.path.abspath(os.path.join(os.getcwd(), "linkfox"))
    os.makedirs(root, exist_ok=True)
    probe = os.path.join(root, ".write_probe-" + secrets.token_hex(8))
    with open(probe, "x", encoding="utf-8"):
        pass
    os.remove(probe)
    return root


def _call_with_http_status(transport, api_path, params):
    """保留真实 HTTP 状态，供认证引导和响应判定使用。"""
    original_urlopen = api_runner.urlopen
    http_status = None

    def tracked_urlopen(*args, **kwargs):
        nonlocal http_status
        try:
            response = original_urlopen(*args, **kwargs)
        except api_runner.HTTPError as exc:
            http_status = exc.code
            raise
        http_status = response.getcode()
        return response

    api_runner.urlopen = tracked_urlopen
    try:
        result = transport(api_path, params)
    finally:
        api_runner.urlopen = original_urlopen
    if isinstance(result, dict) and http_status is not None:
        result["_http_status"] = http_status
    return result


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    usage = "用法：mpstats_ozon_product_detail.py '<JSON 参数>' [--inline] [--no-cache]"
    if "--help" in argv or "-h" in argv:
        print(usage)
        return
    inline = "--inline" in argv
    use_cache = "--no-cache" not in argv
    argv = [a for a in argv if a not in ("--inline", "--no-cache")]
    if not argv:
        print(usage, file=sys.stderr)
        sys.exit(1)
    try:
        params = normalize_params(json.loads(argv[0]))
    except (json.JSONDecodeError, ValueError) as exc:
        print(f"参数无效：{exc}", file=sys.stderr)
        sys.exit(1)
    try:
        root = _prepare_output_root()
        cache_path = _cache_path(params)
    except OSError as exc:
        print(f"当前工作目录不可写：{exc}", file=sys.stderr)
        sys.exit(1)

    original_transport = api_runner.call_api
    previous_root = api_runner._SESSION_CACHE.get("_root")

    def cached_transport(api_path, request_params):
        # 仅业务封装管理缓存；run 的缓存始终关闭。
        result = _load_cache(cache_path) if use_cache else None
        if result is None:
            result = _call_with_http_status(original_transport, api_path, request_params)
            if use_cache:
                _save_cache(cache_path, result)
        return result

    # 公共 run 不返回业务对象，临时提供带业务缓存的传输入口；finally 保证可重复嵌入调用。
    api_runner.call_api = cached_transport
    api_runner._SESSION_CACHE["_root"] = root
    try:
        runner_argv = [json.dumps(params, ensure_ascii=False), "--no-cache"]
        if inline:
            runner_argv.append("--inline")
        api_runner.run(API_PATH, SLUG, argv=runner_argv)
    finally:
        api_runner.call_api = original_transport
        if previous_root is None:
            api_runner._SESSION_CACHE.pop("_root", None)
        else:
            api_runner._SESSION_CACHE["_root"] = previous_root


if __name__ == "__main__":
    main()
