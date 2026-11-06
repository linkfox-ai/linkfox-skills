#!/usr/bin/env python3
"""智慧芽专利权利要求翻译 CLI。

用法：python zhihuiya_claim_translated.py '<JSON 参数>' [--inline] [--no-cache]
默认启用 24 小时缓存；完整响应始终落盘，超过 8 KB 时输出摘要。
"""

import json
import os
import sys
import time

import call_api


API_PATH = "/zhihuiya/claimDataTranslated"
SLUG = "linkfox-zhihuiya-claim-data-translated"


def main():
    # 无参数或无效 JSON 使用公共调用器的 CLI 错误处理，不创建输出目录。
    argv = sys.argv[1:]
    params = [arg for arg in argv if arg not in ("--inline", "--no-cache")]
    if not params:
        return call_api.run(API_PATH, SLUG, argv)
    try:
        json.loads(params[0])
    except json.JSONDecodeError:
        return call_api.run(API_PATH, SLUG, argv)

    # 完整响应保存在当前目录，禁止公共调用器回退到其他目录。
    cwd = os.path.realpath(os.getcwd())
    if cwd == "/tmp" or cwd.startswith("/tmp/"):
        raise SystemExit("禁止在 /tmp 下保存结果，请切换到可写的项目目录。")
    call_api._SESSION_CACHE["_root"] = os.path.join(cwd, "linkfox")
    resolve_output = call_api._resolve_output_path
    try:
        # 请求前确认实际会话目录与文件可写；保留微秒精度以免同秒结果覆盖。
        out_path = resolve_output(SLUG, time.time())
        with open(out_path, "x", encoding="utf-8"):
            pass
    except OSError as exc:
        raise SystemExit(f"无法在当前目录保存完整响应，未发起接口请求：{exc}") from exc

    call_api._resolve_output_path = lambda slug, ts: out_path
    try:
        call_api.run(API_PATH, SLUG, argv)
    finally:
        call_api._resolve_output_path = resolve_output
        # 缺少密钥等提前退出不留下空响应文件。
        if os.path.isfile(out_path) and os.path.getsize(out_path) == 0:
            os.remove(out_path)


if __name__ == "__main__":
    main()
