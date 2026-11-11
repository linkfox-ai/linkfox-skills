#!/usr/bin/env python3
"""视频业务入口：处理 CLI 和当前工作目录约束，使用公共调用与单层缓存。"""

import json
import os
import sys
import tempfile
from pathlib import Path

import call_api


def run_video(api_path, operation, argv=None):
    """按接口隔离缓存；目录不可写时先报错，不请求网络或回退目录。"""
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError, OSError):
        pass
    argv = list(sys.argv[1:] if argv is None else argv)
    positional = [a for a in argv if a not in ("--inline", "--no-cache")]
    if not positional:
        print(f"用法：{os.path.basename(sys.argv[0])} '<JSON 参数>' [--inline] [--no-cache]",
              file=sys.stderr)
        return 1
    try:
        params = json.loads(positional[0])
    except json.JSONDecodeError as exc:
        print(f"参数 JSON 格式错误：{exc}", file=sys.stderr)
        return 1
    if not isinstance(params, dict):
        print("JSON 参数必须为对象", file=sys.stderr)
        return 1

    root = Path.cwd() / "linkfox"
    previous_root = call_api._SESSION_CACHE.get("_root")
    previous_output_path = call_api._resolve_output_path
    phase = "当前工作目录数据保存"
    try:
        root.mkdir(parents=True, exist_ok=True)
        # 探测实际会话数据目录，确保在收费请求前发现目录不可写。
        call_api._SESSION_CACHE["_root"] = str(root)
        _, session = call_api._ensure_session(call_api.time.time())
        data_dir = Path(session) / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryFile(dir=data_dir):
            pass

        def unique_output_path(slug, _timestamp):
            """独占创建微秒文件名，防止同秒调用覆盖已保存的响应。"""
            ts = call_api.time.time()
            stamp = int(ts * 1_000_000)
            while True:
                output = data_dir / f"{slug}-{stamp}.json"
                try:
                    with output.open("x", encoding="utf-8"):
                        pass
                    break
                except FileExistsError:
                    stamp += 1
            call_api._update_meta(
                str(session), skill=slug, kind="data",
                file_rel=os.path.relpath(output, session), ts=ts,
            )
            return str(output)

        call_api._resolve_output_path = unique_output_path
        # 缓存仅由 call_api.run 管理，使用单层缓存。
        phase = "接口调用或响应处理"
        return call_api.run(api_path, f"linkfox-kalodata-tiktok-video-{operation}", argv=argv)
    except OSError as exc:
        print(f"{phase}失败（{type(exc).__name__}）：{exc}", file=sys.stderr)
        return 1
    finally:
        call_api._resolve_output_path = previous_output_path
        if previous_root is None:
            call_api._SESSION_CACHE.pop("_root", None)
        else:
            call_api._SESSION_CACHE["_root"] = previous_root
