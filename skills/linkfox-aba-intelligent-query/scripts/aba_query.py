#!/usr/bin/env python3
"""ABA 智能查询入口，复用公共调用、24 小时缓存和响应输出。

用法：python aba_query.py '<JSON 参数>' [--inline] [--no-cache]
缓存路径和键固定；仅使用公共实现这一层缓存。
查询数据固定保存在当前工作目录，不回退到其他目录。
"""

import json
import os
import sys
import tempfile
import time

import call_api


API_PATH = "/aba/intelligentQuery"
SLUG = "linkfox-aba-intelligent-query"


def _prepare_output_root():
    """在请求前验证当前目录可写，并固定公共脚本的数据根目录。"""
    root = os.path.abspath(os.path.join(os.getcwd(), "linkfox"))
    os.makedirs(root, exist_ok=True)
    # 唯一探针避免覆盖已有文件；不使用临时目录作为回退。
    with tempfile.TemporaryFile(dir=root):
        pass
    call_api._SESSION_CACHE["_root"] = root


def _reserve_output_path():
    """请求前确认会话目录可写，并独占保留文件，避免同秒调用互相覆盖。"""
    ts = time.time()
    _, session_dir = call_api._ensure_session(ts)
    data_dir = os.path.join(session_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    stamp = time.time_ns() // 1000
    while True:
        path = os.path.join(data_dir, f"{SLUG}-{stamp}.json")
        try:
            with open(path, "x", encoding="utf-8"):
                pass
        except FileExistsError:
            stamp += 1
        else:
            return path, session_dir


def _find_main_list(result):
    """遍历 ABA 表数组内的数据行，避免摘要把整张表作为一条样本输出。"""
    best = (None, None, -1)

    def walk(node, path):
        nonlocal best
        if isinstance(node, list):
            if len(node) > best[2]:
                best = (path, node, len(node))
            for index, value in enumerate(node):
                walk(value, f"{path}[{index}]")
        elif isinstance(node, dict):
            for key, value in node.items():
                walk(value, f"{path}.{key}" if path else key)

    walk(result, "")
    return best[0], best[1]


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv in (["--help"], ["-h"]):
        print("用法：aba_query.py '<JSON 参数>' [--inline] [--no-cache]")
        print("默认复用 24 小时本地缓存；--inline 全量输出；--no-cache 禁用缓存。")
        return
    # 缺参和 JSON 格式错误仍交由公共 CLI 处理，不创建数据目录。
    output_path = None
    session_dir = None
    payload = [arg for arg in argv if arg not in ("--inline", "--no-cache")]
    if payload:
        try:
            json.loads(payload[0])
        except json.JSONDecodeError:
            pass
        else:
            try:
                _prepare_output_root()
                output_path, session_dir = _reserve_output_path()
            except OSError as exc:
                print(f"当前工作目录不可写，无法保存完整响应：{exc}", file=sys.stderr)
                raise SystemExit(1)
    # 仅在本次业务调用期间使用嵌套列表遍历，不修改公共文件。
    previous = call_api._find_main_list
    previous_output_path = call_api._resolve_output_path
    call_api._find_main_list = _find_main_list
    if output_path is not None:
        call_api._resolve_output_path = lambda slug, ts: output_path
    try:
        call_api.run(API_PATH, SLUG, argv=argv)
        if output_path is not None:
            # 公共 CLI 会打印写入错误而继续；业务入口必须确认完整 JSON 已保存。
            # 验证成功后才登记文件，失败不将空文件注册为完整数据。
            with open(output_path, encoding="utf-8") as saved:
                json.load(saved)
            call_api._update_meta(
                session_dir, skill=SLUG, kind="data",
                file_rel=os.path.relpath(output_path, session_dir), ts=time.time(),
            )
    except (OSError, json.JSONDecodeError) as exc:
        print(f"完整响应保存失败：{exc}", file=sys.stderr)
        raise SystemExit(1)
    finally:
        call_api._find_main_list = previous
        call_api._resolve_output_path = previous_output_path
        if output_path is not None:
            try:
                if os.path.getsize(output_path) == 0:
                    os.remove(output_path)
            except OSError:
                pass


if __name__ == "__main__":
    main()
