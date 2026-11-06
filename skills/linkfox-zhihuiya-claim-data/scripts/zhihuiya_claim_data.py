#!/usr/bin/env python3
"""智慧芽专利权利要求查询。

用法：python zhihuiya_claim_data.py '<JSON 参数>' [--inline] [--no-cache]
由公共调用器统一处理传输、24 小时缓存、会话落盘和摘要。
业务入口保证输出仅写入当前工作目录，不回退到临时目录。
"""

import json
import sys
import tempfile
from pathlib import Path

import call_api


API_PATH = "/zhihuiya/claimData"
SLUG = "linkfox-zhihuiya-claim-data"


def _output_root():
    """请求前检查输出位置，禁止写入 /tmp。"""
    cwd = Path.cwd().resolve()
    if cwd.as_posix() == "/tmp" or cwd.as_posix().startswith("/tmp/"):
        raise OSError("当前工作目录位于 /tmp，请切换到项目目录后执行")
    root = cwd / "linkfox"
    root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryFile(dir=root):
        pass
    return str(root)


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    params = [arg for arg in argv if arg not in ("--inline", "--no-cache")]
    # 缺少参数和 JSON 格式错误交给公共调用器输出 CLI 错误。
    if not params:
        return call_api.run(API_PATH, SLUG, argv=argv)
    try:
        json.loads(params[0])
    except json.JSONDecodeError:
        return call_api.run(API_PATH, SLUG, argv=argv)

    try:
        root = _output_root()
    except OSError as exc:
        print(f"当前目录不可用于保存完整响应：{exc}", file=sys.stderr)
        raise SystemExit(1) from exc

    # 仅在本次业务调用中限制输出根目录。
    original_root = call_api._linkfox_root
    call_api._linkfox_root = lambda: root
    try:
        # 根目录可写并不代表实际会话目录可用。先检查元数据及 data
        # 目录，避免收费请求完成后才发现目录被文件占用或没有写权限。
        try:
            _, session_dir = call_api._ensure_session(call_api.time.time())
            data_dir = Path(session_dir) / "data"
            data_dir.mkdir(parents=True, exist_ok=True)
            with tempfile.TemporaryFile(dir=data_dir):
                pass
        except OSError as exc:
            print(f"当前目录不可用于保存完整响应：{exc}", file=sys.stderr)
            raise SystemExit(1) from exc

        # 使用公共调用器按 slug 和参数生成的缓存，不叠加业务层缓存。
        return call_api.run(API_PATH, SLUG, argv=argv)
    finally:
        call_api._linkfox_root = original_root


if __name__ == "__main__":
    main()
