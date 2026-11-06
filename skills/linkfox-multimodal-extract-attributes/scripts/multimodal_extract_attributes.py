#!/usr/bin/env python3
"""提取商品图片视觉属性与提示词。

用法：python multimodal_extract_attributes.py '<JSON 参数>' [--inline] [--no-cache]
公共调用器提供 24 小时缓存、认证兼容、完整落盘与摘要输出。
"""

import json
from pathlib import Path
import secrets
import sys
import time

import call_api

API_PATH = "/multimodal/extractPromptsFromMainImage"
SLUG = "linkfox-multimodal-extract-attributes"


def _check_writable(directory):
    directory.mkdir(parents=True, exist_ok=True)
    probe = directory / ('.write_probe-' + secrets.token_hex(6))
    with probe.open('x', encoding='utf-8'):
        pass
    probe.unlink()


def _prepare_output_root():
    """请求前检查实际会话数据目录，严格在当前工作目录内落盘。"""
    cwd = Path.cwd().resolve()
    if cwd == Path('/tmp').resolve() or Path('/tmp').resolve() in cwd.parents:
        raise OSError("本技能禁止在 /tmp 下保存结果，请切换到可写工作目录")
    root = (cwd / 'linkfox').resolve()
    ts = time.time()
    session = (root / time.strftime('%Y-%m-%d', time.localtime(ts))
               / call_api._session_id(ts)).resolve()
    data = (session / 'data').resolve()
    if not root.is_relative_to(cwd) or not session.is_relative_to(root) or not data.is_relative_to(root):
        raise OSError("会话输出路径必须位于当前工作目录的 linkfox/ 下")
    _check_writable(root)
    _check_writable(data)
    return root, session, data, ts


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    previous_root = call_api._SESSION_CACHE.get('_root')
    previous_resolver = call_api._resolve_output_path
    outputs = []
    try:
        root, session, data, ts = _prepare_output_root()
        call_api._SESSION_CACHE['_root'] = str(root)
        # 在请求前写入会话元信息，提前暴露实际目录的写入错误。
        call_api._ensure_meta(str(root), str(session),
                              time.strftime('%Y-%m-%d', time.localtime(ts)),
                              call_api._session_id(ts), ts)

        def resolve_output(slug, _ts):
            # 公共调用器传入整秒时间；业务层独占预留文件，避免同秒响应覆盖。
            stamp = time.time_ns()
            while True:
                path = data / f'{slug}-{stamp}.json'
                try:
                    with path.open('x', encoding='utf-8'):
                        pass
                    break
                except FileExistsError:
                    stamp += 1
            outputs.append(path)
            call_api._update_meta(str(session), skill=slug, kind='data',
                                  file_rel=str(path.relative_to(session)), ts=time.time())
            return str(path)

        # 仅适配落盘路径；请求、24 小时缓存与 stdout 策略仍由公共调用器执行。
        call_api._resolve_output_path = resolve_output
        call_api.run(API_PATH, SLUG, argv=argv)
        for path in outputs:
            # 公共调用器会打印写入错误；业务入口还须识别空文件和磁盘写满留下的残缺 JSON。
            try:
                with path.open(encoding='utf-8') as saved:
                    json.load(saved)
            except (OSError, ValueError) as exc:
                raise OSError("完整响应保存失败；请修复工作目录后使用已有缓存恢复结果") from exc
    except OSError as exc:
        print(f"当前工作目录不可用于保存完整响应：{exc}", file=sys.stderr)
        return 1
    finally:
        call_api._resolve_output_path = previous_resolver
        if previous_root is None:
            call_api._SESSION_CACHE.pop('_root', None)
        else:
            call_api._SESSION_CACHE['_root'] = previous_root
        for path in outputs:
            # 只清理本次预留但没有写入响应的空文件。
            try:
                if path.is_file() and path.stat().st_size == 0:
                    path.unlink()
            except OSError:
                pass
    return 0


if __name__ == '__main__':
    sys.exit(main())
