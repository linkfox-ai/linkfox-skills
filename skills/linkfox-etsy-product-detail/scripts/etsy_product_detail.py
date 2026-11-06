#!/usr/bin/env python3
"""查询 Etsy 商品详情，支持 CLI、24 小时缓存与当前目录落盘。

用法：python etsy_product_detail.py '<JSON 参数>' [--inline] [--no-cache]
HTTP、缓存、摘要及会话元数据统一交给 call_api.run。
"""

import json
from pathlib import Path
import re
import sys
import tempfile
import time
from urllib.parse import urlsplit

import call_api as api


API_PATH = "/etsy/product/detail"
SLUG = "linkfox-etsy-product-detail"


def validate_params(params):
    """在消耗算力前检查商品直链约束，不改写 URL。"""
    if not isinstance(params, dict):
        raise ValueError("JSON 参数必须是对象")
    url = params.get("productUrl")
    if not isinstance(url, str) or not url or any(c.isspace() for c in url):
        raise ValueError("productUrl 必须是完整的 Etsy HTTPS 商品直链")
    try:
        parsed = urlsplit(url)
        host = (parsed.hostname or "").lower()
        valid = (
            parsed.scheme == "https"
            and (host == "etsy.com" or host.endswith(".etsy.com"))
            and parsed.username is None
            and parsed.password is None
            and parsed.port in (None, 443)
            and re.fullmatch(r"/listing/[0-9]+(?:/[^/]+)?/?", parsed.path)
        )
    except ValueError:
        valid = False
    if not valid:
        raise ValueError("productUrl 须使用 Etsy 域名、HTTPS 默认端口和 /listing/<数字ID>，最多一个标题 slug，不得含用户凭据")


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    arguments = [a for a in argv if a not in ("--inline", "--no-cache")]
    if not arguments or "--help" in argv or "-h" in argv:
        help_requested = "--help" in argv or "-h" in argv
        print("用法：etsy_product_detail.py '<JSON 参数>' [--inline] [--no-cache]",
              file=sys.stdout if help_requested else sys.stderr)
        return 0 if help_requested else 1
    try:
        params = json.loads(arguments[0])
        validate_params(params)
    except (ValueError, TypeError) as exc:
        print(f"参数错误：{exc}", file=sys.stderr)
        return 1

    # 公共调用器负责缓存路径、排序 JSON 的 SHA256 前 16 位及 TTL，
    # 业务封装不叠加缓存读写。
    root = Path.cwd() / "linkfox"
    previous_root = api._SESSION_CACHE.get("_root")
    previous_output_path = api._resolve_output_path
    try:
        # 禁止回退到临时目录；请求前检查 cwd，固定公共调用器的根目录。
        root.mkdir(parents=True, exist_ok=True)
        api._SESSION_CACHE["_root"] = str(root)
        # 提前创建并检查完整会话路径，避免请求收费后才发现 data/ 不可写。
        _, session_dir = api._ensure_session(time.time())
        data_dir = Path(session_dir) / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryFile(dir=data_dir):
            pass
        out_path = None

        def resolve_output_path(slug, _ts):
            nonlocal out_path
            # 收到响应后再登记实际文件；微秒时间戳避免同秒响应覆盖。
            out_path = Path(api.resolve_data_path(slug, time.time()))
            return str(out_path)

        api._resolve_output_path = resolve_output_path
        api.run(API_PATH, SLUG, argv=argv)
        # 公共调用器会记录并吞掉保存异常；封装必须据实际文件返回失败，不能重试请求。
        with out_path.open(encoding="utf-8") as saved:
            json.load(saved)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"当前目录无法完整保存响应：{exc}", file=sys.stderr)
        return 1
    finally:
        api._resolve_output_path = previous_output_path
        if previous_root is None:
            api._SESSION_CACHE.pop("_root", None)
        else:
            api._SESSION_CACHE["_root"] = previous_root
    return 0


if __name__ == "__main__":
    sys.exit(main())
