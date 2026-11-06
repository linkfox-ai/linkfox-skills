#!/usr/bin/env python3
"""睿观实用新型/发明专利检测 CLI。

用法：python ruiguan_utility_patent_detection.py '<JSON 参数>' [--inline] [--no-cache]
使用公共调用器的单层 24 小时缓存及输出流程，缓存文件使用固定路径和参数哈希。
"""

import os
import sys
import tempfile

import call_api

API_PATH = "/ruiguan/utilityPatentDetection"
SLUG = "linkfox-ruiguan-utility-patent-detection"


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    # 业务入口将响应落盘目录固定为当前工作目录下的 linkfox/。
    root = os.path.abspath(os.path.join(os.getcwd(), "linkfox"))
    try:
        os.makedirs(root, exist_ok=True)
        with tempfile.TemporaryFile(dir=root):
            pass
    except OSError as exc:
        print(f"当前工作目录不可写：{exc}", file=sys.stderr)
        return 1
    call_api._SESSION_CACHE["_root"] = root
    # 缓存路径、哈希算法和 TTL 由公共调用器统一维护。
    # 由 run 唯一管理缓存。
    call_api.run(API_PATH, SLUG, argv=argv)
    return 0


if __name__ == "__main__":
    sys.exit(main())
