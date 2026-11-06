#!/usr/bin/env python3
"""智慧芽专利简要著录查询。

用法：python zhihuiya_simple_bibliography.py '<JSON 参数>' [--inline] [--no-cache]
完整响应始终落盘；默认使用公共调用器的 24 小时缓存，不叠加业务缓存。
"""

import os
import tempfile
import time

import call_api


API_PATH = "/zhihuiya/simpleBibliography"
SLUG = "linkfox-zhihuiya-simple-bibliography"


def main(argv=None):
    # 数据只写当前工作目录；请求前检查，避免公共调用器回退到其他目录。
    root = os.path.join(os.getcwd(), "linkfox")
    os.makedirs(root, exist_ok=True)
    with tempfile.TemporaryFile(dir=root):
        pass
    previous_root = call_api._SESSION_CACHE.get("_root")
    call_api._SESSION_CACHE["_root"] = root
    try:
        # 根目录可写不代表本次会话的输出目录可用；先检查实际落盘位置。
        _, session_dir = call_api._ensure_session(time.time())
        data_dir = os.path.join(session_dir, "data")
        os.makedirs(data_dir, exist_ok=True)
        with tempfile.TemporaryFile(dir=data_dir):
            pass
        call_api.run(API_PATH, SLUG, argv=argv)
    finally:
        if previous_root is None:
            call_api._SESSION_CACHE.pop("_root", None)
        else:
            call_api._SESSION_CACHE["_root"] = previous_root


if __name__ == "__main__":
    main()
