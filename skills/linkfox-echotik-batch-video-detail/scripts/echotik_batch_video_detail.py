#!/usr/bin/env python3
"""EchoTik 批量视频详情 CLI，提供本地缓存并复用公共调用与输出。

用法：python echotik_batch_video_detail.py '<JSON 参数>' [--inline] [--no-cache]
完整响应始终落盘；超过 8000 字节时默认输出摘要。
"""

import json
import os
import sys
import tempfile
import time

import call_api as transport


API_PATH = "/echotik/batchVideoDetail"
SLUG = "linkfox-echotik-batch-video-detail"


def _cwd_root():
    """响应落盘只允许使用当前工作目录，不回退其他目录。"""
    root = os.path.join(os.getcwd(), "linkfox")
    os.makedirs(root, exist_ok=True)
    return root


def main(argv=None):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

    argv = list(sys.argv[1:] if argv is None else argv)
    use_cache = "--no-cache" not in argv
    args = [arg for arg in argv if arg not in ("--inline", "--no-cache")]
    if not args:
        print("用法：echotik_batch_video_detail.py '<JSON 参数>' [--inline] [--no-cache]",
              file=sys.stderr)
        return 1
    try:
        params = json.loads(args[0])
    except json.JSONDecodeError as exc:
        print(f"JSON 参数格式错误：{exc}", file=sys.stderr)
        return 1

    # 仅在本次调用期间注入本地缓存和严格落盘策略；
    # 所有实际 HTTP 均由公共调用器执行，finally 恢复调用器函数。
    original_call = transport.call_api
    original_root = transport._linkfox_root
    original_output = transport._resolve_output_path
    response = None
    output_path = None

    def cached_call(api_path, body):
        nonlocal response
        cache_path = transport._cache_path(SLUG, body)
        result = transport._load_cache(cache_path) if use_cache else None
        if result is None:
            result = original_call(api_path, body)
            if use_cache:
                transport._save_cache(cache_path, result)
        response = result
        return result

    def resolve_output(slug, ts):
        nonlocal output_path
        output_path = transport.resolve_data_path(slug, time.time())
        return output_path

    try:
        transport._linkfox_root = _cwd_root
        # 先验证输出可写，再发请求；使用高精度时间避免同秒文件覆盖。
        _, session_dir = transport._ensure_session(time.time())
        data_dir = os.path.join(session_dir, "data")
        os.makedirs(data_dir, exist_ok=True)
        with tempfile.TemporaryFile(dir=data_dir):
            pass
        transport._resolve_output_path = resolve_output
        transport.call_api = cached_call
        # 业务封装已处理缓存读取和写入，公共层始终关闭缓存。
        transport.run(API_PATH, SLUG, argv=[*argv, "--no-cache"])
        # 公共 run 会捕获写文件异常；业务封装必须核验实际落盘，防止预检
        # 通过后磁盘写满等失败被当作成功。保留已有缓存，不自动重发付费请求。
        with open(output_path, encoding="utf-8") as saved:
            if saved.read() != json.dumps(response, ensure_ascii=False, indent=2):
                raise OSError("完整响应文件缺失或内容不完整")
    except OSError as exc:
        print(f"当前工作目录的数据保存失败：{exc}", file=sys.stderr)
        return 1
    finally:
        transport.call_api = original_call
        transport._linkfox_root = original_root
        transport._resolve_output_path = original_output
    return 0


if __name__ == "__main__":
    sys.exit(main())
