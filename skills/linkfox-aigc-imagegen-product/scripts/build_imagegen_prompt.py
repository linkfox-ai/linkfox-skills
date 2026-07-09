#!/usr/bin/env python3
"""
build_imagegen_prompt.py — 商品图 imagegen 提示词文件构建器（静态直出支线）

服务"白底图（WHITE_BG）静态直出"：从 references/types/white-bg.md 的 ```text``` 代码块
**动态提取**白底图静态正文作为最终 prompt（无占位符、不调 textgen、不过敏感词），
直接喂给 imagegen 出图。保证与 skill 规范同步、避免手抄截断或长正文经 shell 溢出。

商品图 collection 只有 WHITE_BG 走"静态直出"，其余类型（SCENE/CLOSE_UP/SELLING_POINT/*_APLUS）
都走 textgen 改写，用 build_textgen_params.py。

Usage:
  DATADIR=$(python <brand-gene根目录>/scripts/save_brand_gene.py --datadir)

  python scripts/build_imagegen_prompt.py \\
    --type WHITE_BG \\
    --image-urls '["https://example.com/product.jpg"]' \\
    --out "$DATADIR/imagegen_white.json"
"""

import argparse
import json
import os
import re
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WHITE_BG_REF = os.path.join(SCRIPT_DIR, "..", "references", "types", "white-bg.md")


def extract_white_bg_prompt() -> str:
    """从 references/types/white-bg.md 的 ```text``` 代码块提取白底图静态正文。

    单一来源：运营更新白底图正文只改 white-bg.md，本函数动态读取，
    避免把正文硬编码进脚本/shell 变量导致截断或 ARG_MAX 溢出。
    """
    ref_path = os.path.abspath(WHITE_BG_REF)
    if not os.path.isfile(ref_path):
        raise FileNotFoundError(f"白底图正文来源不存在: {ref_path}")
    with open(ref_path, encoding="utf-8") as f:
        md = f.read()
    m = re.search(r"```text\s*\n(.*?)\n```", md, re.S)
    if not m:
        raise ValueError(f"未在 {ref_path} 中找到 ```text``` 提示词正文代码块")
    prompt = m.group(1).strip()
    if not prompt:
        raise ValueError(f"{ref_path} 的 ```text``` 代码块为空")
    return prompt


def build_params(img_type: str, image_urls: list) -> dict:
    """构建 imagegen 参数 dict（供 CLI 与 collection_pipeline/single_task.py 共用）。"""
    if not isinstance(image_urls, list):
        raise ValueError("image_urls 必须是 list")
    if img_type == "WHITE_BG":
        return {"prompt": extract_white_bg_prompt(), "imageUrls": image_urls}
    raise ValueError(f"不支持的 imagegen 静态直出类型: {img_type}")


def main():
    parser = argparse.ArgumentParser(
        description="商品图 imagegen 提示词文件构建器（静态直出支线）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--type", required=True, choices=["WHITE_BG"], help="图片类型（仅白底图走静态直出）",
    )
    parser.add_argument(
        "--image-urls", required=True, help="JSON 数组格式的图片 URL 列表",
    )
    parser.add_argument("--out", required=True, help="输出 JSON 文件路径")
    args = parser.parse_args()

    try:
        image_urls = json.loads(args.image_urls)
        if not isinstance(image_urls, list):
            raise ValueError("imageUrls 必须是 JSON 数组")
    except (json.JSONDecodeError, ValueError) as e:
        print(f"ERROR: --image-urls 解析失败: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        params = build_params(args.type, image_urls)
    except (FileNotFoundError, ValueError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    out_path = os.path.abspath(args.out)
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    try:
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(params, f, ensure_ascii=False, indent=2)
    except OSError as e:
        print(f"ERROR: 写出参数文件失败: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"IMAGEGEN_PROMPT_PATH={out_path}")
    print(f"  type          : {args.type}")
    print("  source        : references/types/white-bg.md (静态正文动态提取)")
    print(f"  prompt_length : {len(params['prompt'])} chars")
    print(f"  image_urls    : {len(image_urls)} items")


if __name__ == "__main__":
    main()
