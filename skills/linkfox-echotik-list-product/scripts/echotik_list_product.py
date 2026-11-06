#!/usr/bin/env python3
"""EchoTik TikTok 商品搜索；使用公共调用器及单层 24 小时缓存。

用法：python echotik_list_product.py '<JSON 参数>' [--inline] [--no-cache]
完整响应始终落盘；不超过 8 KB 时全量输出，否则输出摘要。
"""

import sys
import tempfile
from pathlib import Path

import call_api as api

API_PATH = "/echotik/listProduct"
SLUG = "linkfox-echotik-list-product"


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    # 目录策略由业务入口实现。
    # 在请求前验证 cwd，避免公共调用器回退到家目录或临时目录。
    root = Path.cwd() / "linkfox"
    try:
        cwd = Path.cwd().resolve()
        forbidden = Path("/tmp").resolve()
        if cwd == forbidden or forbidden in cwd.parents:
            raise OSError("原始响应禁止写入 /tmp，请切换到可写项目目录")
        root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryFile(dir=root):
            pass
    except OSError as exc:
        print(f"当前工作目录不可用于保存响应：{exc}", file=sys.stderr)
        raise SystemExit(1)

    previous_root = api._SESSION_CACHE.get("_root")
    previous_output_path = api._resolve_output_path
    api._SESSION_CACHE["_root"] = str(root)
    try:
        # 根目录可写不代表会话 data 目录可写；请求前检查实际落盘位置。
        # 提前使用微秒时间生成路径，也避免公共调用器秒级时间覆盖同秒结果。
        try:
            out_path = api.resolve_data_path(SLUG, api.time.time())
            # 检查完整文件名，覆盖 Windows 路径长度和已有目标文件等情况。
            with Path(out_path).open("x", encoding="utf-8"):
                pass
            Path(out_path).unlink()
        except OSError as exc:
            print(f"会话数据目录不可用于保存响应：{exc}", file=sys.stderr)
            raise SystemExit(1)
        api._resolve_output_path = lambda slug, _ts: out_path
        # 使用公共调用器的单层缓存及其缓存键和目录。
        return api.run(API_PATH, SLUG, argv=argv)
    finally:
        api._resolve_output_path = previous_output_path
        if previous_root is None:
            api._SESSION_CACHE.pop("_root", None)
        else:
            api._SESSION_CACHE["_root"] = previous_root


if __name__ == "__main__":
    main()
