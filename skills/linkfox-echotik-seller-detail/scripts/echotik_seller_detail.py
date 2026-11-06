#!/usr/bin/env python3
"""EchoTik TikTok 店铺详情：复用公共调用、单层缓存及会话输出。

用法：python echotik_seller_detail.py '<JSON 参数>' [--inline] [--no-cache]
使用单层本地缓存，有效期为 24 小时；--no-cache 跳过读写。
"""

import json
import os
from pathlib import Path
import sys
import tempfile

import call_api


API_PATH = "/echotik/sellerDetail"
SLUG = "linkfox-echotik-seller-detail"


def main():
    argv = sys.argv[1:]
    # 无参数或非法 JSON 交给公共 CLI 报错，不创建输出目录。
    params = [arg for arg in argv if arg not in ("--inline", "--no-cache")]
    if not params:
        return call_api.run(API_PATH, SLUG, argv)
    try:
        json.loads(params[0])
    except json.JSONDecodeError:
        return call_api.run(API_PATH, SLUG, argv)

    # 完整响应落盘在 cwd；在付费请求前确认可写，不使用公共器的目录回退。
    root = Path.cwd().resolve() / "linkfox"
    if os.name != "nt" and (root == Path("/tmp") or Path("/tmp") in root.parents):
        raise OSError("本技能禁止写入 /tmp，请切换到可写的项目目录")
    root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryFile(dir=root):
        pass
    call_api._SESSION_CACHE["_root"] = str(root)
    return call_api.run(API_PATH, SLUG, argv)


if __name__ == "__main__":
    main()
