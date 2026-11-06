#!/usr/bin/env python3
"""SIF ASIN 流量来源分析。

用法：python sif_asin_summary.py '<JSON 参数>' [--inline] [--no-cache]
使用公共调用器的 24 小时缓存、完整落盘与大小响应展示；只在当前目录保存。
"""

import json
import os
from pathlib import Path
import secrets
import sys
import time

import call_api


API_PATH = "/sif/asinSummary"
SLUG = "linkfox-sif-asin-summary"


def _prepare_output_root():
    """请求前确认输出位置可写，避免公共调用器回退到其他目录。"""
    cwd = Path.cwd().resolve()
    if os.name != "nt" and (cwd == Path("/tmp") or Path("/tmp") in cwd.parents):
        raise OSError("禁止在 /tmp 下保存会话数据，请切换到可写的项目目录")
    root = cwd / "linkfox"
    root.mkdir(parents=True, exist_ok=True)
    root = root.resolve()
    if root.parent != cwd:
        raise OSError("linkfox 输出目录必须位于当前工作目录内")
    probe = root / (".write_probe-" + secrets.token_hex(6))
    with probe.open("x", encoding="utf-8"):
        pass
    probe.unlink()
    return str(root)


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    # 用法或 JSON 错误由公共调用器处理，不触发请求或生成会话目录。
    params_args = [arg for arg in argv if arg not in ("--inline", "--no-cache")]
    if not params_args:
        return call_api.run(API_PATH, SLUG, argv=argv)
    try:
        json.loads(params_args[0])
    except json.JSONDecodeError:
        return call_api.run(API_PATH, SLUG, argv=argv)

    previous_root = call_api._SESSION_CACHE.get("_root")
    try:
        root = _prepare_output_root()
        ts = time.time()
        sid = call_api._session_id(ts)
        session_path = (Path(root) / time.strftime("%Y-%m-%d", time.localtime(ts)) / sid).resolve()
        if Path(root) not in session_path.parents:
            raise OSError("SESSION_ID 对应的会话目录必须位于当前工作目录的 linkfox 内")
        call_api._SESSION_CACHE["_root"] = root
        call_api._ensure_session(ts)
        # 根目录可写不代表 data 子目录可写，必须在产生接口消耗前检查。
        data_path = (session_path / "data").resolve()
        if Path(root) not in data_path.parents:
            raise OSError("data 输出目录必须位于当前工作目录的 linkfox 内")
        data_path.mkdir(parents=True, exist_ok=True)
        # 使用与实际响应文件等长的文件名，也覆盖 Windows 长路径导致的写入失败。
        probe = data_path / (SLUG + "-" + secrets.token_hex(8) + ".json")
        with probe.open("x", encoding="utf-8"):
            pass
        probe.unlink()
        # 默认启用公共调用器缓存，不叠加第二层。
        return call_api.run(API_PATH, SLUG, argv=argv)
    except OSError as exc:
        print(f"当前工作目录无法保存完整响应：{exc}", file=sys.stderr)
        raise SystemExit(1)
    finally:
        if previous_root is None:
            call_api._SESSION_CACHE.pop("_root", None)
        else:
            call_api._SESSION_CACHE["_root"] = previous_root


if __name__ == "__main__":
    main()
