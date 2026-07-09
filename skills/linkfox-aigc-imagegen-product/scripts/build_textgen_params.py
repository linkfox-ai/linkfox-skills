#!/usr/bin/env python3
"""
build_textgen_params.py — 商品图 textgen 参数文件构建器

根据图片类型选择对应模板，填充占位符，生成 textgen 链式调用所需的 JSON 参数文件。
解决 agent 并行构造多个 textgen 参数文件时 Write 工具输出过大导致参数丢失的问题。

Usage:
  DATADIR=$(python <brand-gene根目录>/scripts/save_brand_gene.py --datadir)

  # 场景图
  python <本skill根目录>/scripts/build_textgen_params.py \\
    --type SCENE \\
    --image-urls '["https://example.com/a.jpg"]' \\
    --point "防水透气，户外徒步无惧风雨" \\
    --out "$DATADIR/textgen_scene.json"

  # 卖点图
  python <本skill根目录>/scripts/build_textgen_params.py \\
    --type SELLING_POINT \\
    --image-urls '["https://example.com/a.jpg"]' \\
    --point "轻量化设计，仅重 280g" \\
    --layout "概览" \\
    --brand-gene-json '{"brandColor":"#8B252E"}' \\
    --ratio "1:1" \\
    --out "$DATADIR/textgen_sp.json"

  # 品牌基因从文件读取
  python <本skill根目录>/scripts/build_textgen_params.py \\
    --type PREMIUM_APLUS \\
    --image-urls '["https://example.com/a.jpg"]' \\
    --point "核心卖点" \\
    --layout "功能" \\
    --brand-gene-file "<S1 save_brand_gene.py 落盘的 brandGeneJson 绝对路径>" \\
    --ratio "1464:600" \\
    --out "$DATADIR/textgen_aplus.json"
"""

import argparse
import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(SCRIPT_DIR, "templates")

TYPE_CONFIG = {
    "SCENE": {
        "template": "scene.txt",
        "model": "GEM_3_FLASH",
        "thinkingLevel": "low",
        "sensitivity": False,
    },
    "CLOSE_UP": {
        "template": "close-up.txt",
        "model": "GEM_3_FLASH",
        "thinkingLevel": "low",
        "sensitivity": False,
    },
    "SELLING_POINT": {
        "template": "selling-point-aplus.txt",
        "model": "GEM_3_1_PRO",
        "thinkingLevel": "high",
        "sensitivity": True,
    },
    "PREMIUM_APLUS": {
        "template": "selling-point-aplus.txt",
        "model": "GEM_3_1_PRO",
        "thinkingLevel": "high",
        "sensitivity": True,
    },
    "STANDARD_APLUS": {
        "template": "selling-point-aplus.txt",
        "model": "GEM_3_1_PRO",
        "thinkingLevel": "high",
        "sensitivity": True,
    },
    "PHONE_APLUS": {
        "template": "selling-point-aplus.txt",
        "model": "GEM_3_1_PRO",
        "thinkingLevel": "high",
        "sensitivity": True,
    },
}

SENSITIVITY_SUFFIX = (
    "\n\n【敏感词规避指令】：在撰写 Text on Image 文案时，必须主动规避所有违禁词、"
    "侵权词、敏感词汇，确保文案内容合规，不出现任何可能引发版权纠纷、"
    "品牌侵权或平台审核风险的词汇。"
)


def _build_layout_info(img_type: str, layout: str) -> str:
    """根据类型和 layout 标签构建 layoutInfo 版式意图文本。"""
    if not layout:
        return ""
    if img_type == "SELLING_POINT":
        return f"卖点图·{layout}点展示版式：按概览/功能/品质/场景之一组织模块"
    if img_type == "PREMIUM_APLUS":
        return f"高级A+·{layout}点多模块版式"
    if img_type == "STANDARD_APLUS":
        return f"普通A+·{layout}点多模块版式"
    if img_type == "PHONE_APLUS":
        return ""
    return ""


def _read_template(name: str) -> str:
    template_path = os.path.join(TEMPLATES_DIR, name)
    if not os.path.isfile(template_path):
        raise FileNotFoundError(f"模板文件不存在: {template_path}")
    with open(template_path, encoding="utf-8") as f:
        return f.read()


def build_params(
    img_type: str,
    image_urls: list,
    *,
    point: str = "",
    layout: str = "",
    image_desc: str = "",
    brand_gene: str = "",
    language: str = "英文",
    sales_region: str = "美国",
    platform: str = "亚马逊",
    ratio: str = "1:1",
) -> dict:
    """构建 textgen 参数 dict（供 CLI 与 collection_pipeline/single_task.py 共用）。

    所有 null/空入参一律退化为空串或类型默认值，避免 {xxx} 占位符残留。
    """
    if img_type not in TYPE_CONFIG:
        raise ValueError(f"不支持的 textgen 类型: {img_type}")
    if not isinstance(image_urls, list):
        raise ValueError("image_urls 必须是 list")

    config = TYPE_CONFIG[img_type]
    template = _read_template(config["template"])

    point = point or ""
    image_desc = image_desc or ""
    brand_gene = brand_gene or ""
    language = language or "英文"
    sales_region = sales_region or "美国"
    platform = platform or "亚马逊"
    ratio = ratio or "1:1"
    layout_info = _build_layout_info(img_type, layout or "")

    prompt = template
    prompt = prompt.replace("{customer_keywords}", point)
    prompt = prompt.replace("{brandKey}", brand_gene)
    prompt = prompt.replace("{customSetting}", image_desc)
    prompt = prompt.replace("{language}", language)
    prompt = prompt.replace("{salesRegion}", sales_region)
    prompt = prompt.replace("{platform}", platform)
    prompt = prompt.replace("{Ratio}", ratio)
    prompt = prompt.replace("{layoutInfo}", layout_info)
    prompt = prompt.replace("{infringingWords}", "")

    if config["sensitivity"]:
        prompt += SENSITIVITY_SUFFIX

    return {
        "prompt": prompt,
        "imageUrls": image_urls,
        "model": config["model"],
        "thinkingLevel": config["thinkingLevel"],
    }


def main():
    parser = argparse.ArgumentParser(
        description="商品图 textgen 参数文件构建器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--type", required=True, choices=list(TYPE_CONFIG.keys()),
        help="图片类型",
    )
    parser.add_argument(
        "--image-urls", required=True,
        help="JSON 数组格式的图片 URL 列表",
    )
    parser.add_argument("--point", default="", help="核心卖点")
    parser.add_argument("--layout", default="", help="版式标签(概览/功能/品质/场景)")
    parser.add_argument("--image-desc", default="", help="画面内容/用户自定义")
    parser.add_argument(
        "--brand-gene-json", default="",
        help="品牌基因 JSON 字符串（与 --brand-gene-file 二选一）",
    )
    parser.add_argument(
        "--brand-gene-file", default="",
        help="品牌基因 JSON 文件路径（与 --brand-gene-json 二选一）",
    )
    parser.add_argument("--language", default="英文", help="语言")
    parser.add_argument("--sales-region", default="美国", help="销售地区")
    parser.add_argument("--platform", default="亚马逊", help="平台")
    parser.add_argument("--ratio", default="1:1", help="图片比例")
    parser.add_argument("--out", required=True, help="输出 JSON 文件路径")

    args = parser.parse_args()
    config = TYPE_CONFIG[args.type]

    # --- 解析 imageUrls ---
    try:
        image_urls = json.loads(args.image_urls)
        if not isinstance(image_urls, list):
            raise ValueError("imageUrls 必须是 JSON 数组")
    except (json.JSONDecodeError, ValueError) as e:
        print(f"ERROR: --image-urls 解析失败: {e}", file=sys.stderr)
        sys.exit(1)

    # --- 解析品牌基因 ---
    brand_gene = args.brand_gene_json or ""
    if not brand_gene and args.brand_gene_file:
        bgf = os.path.abspath(args.brand_gene_file)
        if not os.path.isfile(bgf):
            print(f"ERROR: 品牌基因文件不存在: {bgf}", file=sys.stderr)
            sys.exit(1)
        with open(bgf, encoding="utf-8") as f:
            brand_gene = f.read().strip()

    # --- 构建参数（与编排器共用 build_params）---
    try:
        params = build_params(
            args.type,
            image_urls,
            point=args.point,
            layout=args.layout,
            image_desc=args.image_desc,
            brand_gene=brand_gene,
            language=args.language,
            sales_region=args.sales_region,
            platform=args.platform,
            ratio=args.ratio,
        )
    except (FileNotFoundError, ValueError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    prompt = params["prompt"]

    # --- 写出 ---
    out_path = os.path.abspath(args.out)
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    try:
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(params, f, ensure_ascii=False, indent=2)
    except OSError as e:
        print(f"ERROR: 写出参数文件失败: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"TEXTGEN_PARAMS_PATH={out_path}")
    print(f"  type          : {args.type}")
    print(f"  model         : {config['model']}")
    print(f"  thinkingLevel : {config['thinkingLevel']}")
    print(f"  prompt_length : {len(prompt)} chars")
    print(f"  image_urls    : {len(image_urls)} items")
    if config["sensitivity"]:
        print("  sensitivity   : 已追加敏感词规避指令")


if __name__ == "__main__":
    main()
