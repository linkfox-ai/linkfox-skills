#!/usr/bin/env python3
"""
build_imagegen_prompt.py — 服饰图 imagegen 提示词文件构建器（静态直出 / 占位符直出支线）

服务"①静态直出"与"②占位符直出"支线：prompt 填好后直接喂给 imagegen 出图，**不经 textgen 改写**。
覆盖三类：
  - WHITE_BG（白底图/隐形模特）：①静态直出。从 references/types/white-bg.md 的 ```text``` 块
    动态提取静态正文作为 prompt（无占位符、不过敏感词），保证与 skill 规范同步、避免手抄截断。
  - MODEL_IMAGE（模特图）：②占位符直出。填 {image_desc}，不过敏感词
  - SIZE 阶段2（尺码图出图阶段）：②占位符直出。按 layout 选模板 → 填 {brandKey}/{language}/{analysis_result}
    → **末尾追加敏感词规避指令** → 出图

analysis_result 用 --analysis-file 注入，避免大文本经 shell 传参被截断/转义。
所有 null 入参一律替换为空串，避免 {xxx} 占位符残留。

Usage:
  DATADIR=$(python <brand-gene根目录>/scripts/save_brand_gene.py --datadir)

  # 白底图（WHITE_BG）：正文从 white-bg.md 动态提取，无需任何文本入参
  python scripts/build_imagegen_prompt.py \\
    --type WHITE_BG \\
    --image-urls '["https://example.com/cloth.jpg"]' \\
    --out "$DATADIR/imagegen_white.json"

  # 模特图（MODEL_IMAGE）
  python scripts/build_imagegen_prompt.py \\
    --type MODEL_IMAGE \\
    --image-urls '["https://example.com/cloth.jpg"]' \\
    --image-desc "海边度假风，金色阳光" \\
    --out "$DATADIR/imagegen_model.json"

  # 尺码图阶段2 普通版式（SIZE + layout=普通）
  python scripts/build_imagegen_prompt.py \\
    --type SIZE \\
    --layout 普通 \\
    --image-urls '["https://example.com/cloth.jpg"]' \\
    --brand-gene-file "<S1 save_brand_gene.py 落盘的 brandGeneJson 绝对路径>" \\
    --language 英文 \\
    --analysis-file "$DATADIR/size_analysis.txt" \\
    --out "$DATADIR/imagegen_size.json"

  # 尺码图阶段2 三版/三栏版式（SIZE + layout=三版）
  python scripts/build_imagegen_prompt.py \\
    --type SIZE \\
    --layout 三版 \\
    --image-urls '["https://example.com/cloth.jpg"]' \\
    --brand-gene-file "<S1 save_brand_gene.py 落盘的 brandGeneJson 绝对路径>" \\
    --language 英文 \\
    --analysis-file "$DATADIR/size_analysis.txt" \\
    --out "$DATADIR/imagegen_size3.json"
"""

import argparse
import json
import os
import re
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(SCRIPT_DIR, "templates")
WHITE_BG_REF = os.path.join(SCRIPT_DIR, "..", "references", "types", "white-bg.md")

SENSITIVITY_SUFFIX = (
    "\n\n【敏感词规避指令】：在撰写 Text on Image 文案时，必须主动规避所有违禁词、"
    "侵权词、敏感词汇，确保文案内容合规，不出现任何可能引发版权纠纷、"
    "品牌侵权或平台审核风险的词汇。"
)

# 尺码图阶段2 版式 → 模板映射。后端 layout 值"三栏"等同"三版"。
SIZE_LAYOUT_TEMPLATE = {
    "普通": "size-common.txt",
    "三版": "size-three-column.txt",
    "三栏": "size-three-column.txt",
}


def extract_white_bg_prompt() -> str:
    """从 references/types/white-bg.md 的 ```text``` 代码块提取白底图静态正文。

    单一来源：运营更新白底图正文只改 white-bg.md，本函数动态读取，
    避免把 900+ 字正文硬编码进脚本/shell 变量导致截断或 ARG_MAX 溢出。
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
    image_desc: str = "",
    layout: str = "普通",
    brand_gene: str = "",
    language: str = "英文",
    analysis_result: str = "",
) -> dict:
    """构建 imagegen 参数 dict（供 CLI 与 collection_pipeline/single_task.py 共用）。

    WHITE_BG → 静态正文直出；MODEL_IMAGE → 填 {image_desc}；
    SIZE → 按 layout 选模板填 {brandKey}/{language(固定取调用方)}/{analysis_result} 并追加敏感词规避。
    所有 null 入参一律退化为空串。返回 {"prompt":..., "imageUrls":...}。
    """
    if not isinstance(image_urls, list):
        raise ValueError("image_urls 必须是 list")

    if img_type == "WHITE_BG":
        return {"prompt": extract_white_bg_prompt(), "imageUrls": image_urls}

    if img_type == "MODEL_IMAGE":
        template = _read_template("model-image.txt")
        prompt = template.replace("{image_desc}", image_desc or "")
        return {"prompt": prompt, "imageUrls": image_urls}

    if img_type == "SIZE":
        layout = layout or "普通"
        template_file = SIZE_LAYOUT_TEMPLATE.get(layout)
        if not template_file:
            raise ValueError(
                f"未知 SIZE 版式 '{layout}'，仅支持: {', '.join(SIZE_LAYOUT_TEMPLATE.keys())}"
            )
        template = _read_template(template_file)
        prompt = template
        prompt = prompt.replace("{brandKey}", brand_gene or "")
        prompt = prompt.replace("{language}", language or "英文")
        prompt = prompt.replace("{analysis_result}", analysis_result or "")
        prompt += SENSITIVITY_SUFFIX
        return {"prompt": prompt, "imageUrls": image_urls}

    raise ValueError(f"不支持的 imagegen 类型: {img_type}")


def main():
    parser = argparse.ArgumentParser(
        description="服饰图 imagegen 提示词文件构建器（占位符直出支线）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--type", required=True, choices=["WHITE_BG", "MODEL_IMAGE", "SIZE"],
        help="图片类型",
    )
    parser.add_argument(
        "--image-urls", required=True,
        help="JSON 数组格式的图片 URL 列表",
    )
    parser.add_argument("--image-desc", default="", help="MODEL_IMAGE 画面内容")
    parser.add_argument(
        "--layout", default="普通",
        help="SIZE 版式：普通 / 三版（后端值'三栏'等同三版）",
    )
    parser.add_argument(
        "--brand-gene-json", default="",
        help="品牌基因 JSON 字符串（与 --brand-gene-file 二选一）",
    )
    parser.add_argument(
        "--brand-gene-file", default="",
        help="品牌基因 JSON 文件路径（与 --brand-gene-json 二选一）",
    )
    parser.add_argument("--language", default="英文", help="SIZE 图片文字语言")
    parser.add_argument(
        "--analysis-file", default="",
        help="SIZE 阶段1前置分析结果文本文件路径（注入 {analysis_result}）",
    )
    parser.add_argument("--out", required=True, help="输出 JSON 文件路径")

    args = parser.parse_args()

    # --- 解析 imageUrls ---
    try:
        image_urls = json.loads(args.image_urls)
        if not isinstance(image_urls, list):
            raise ValueError("imageUrls 必须是 JSON 数组")
    except (json.JSONDecodeError, ValueError) as e:
        print(f"ERROR: --image-urls 解析失败: {e}", file=sys.stderr)
        sys.exit(1)

    # --- 解析品牌基因（仅 SIZE 用）---
    brand_gene = args.brand_gene_json or ""
    if not brand_gene and args.brand_gene_file:
        bgf = os.path.abspath(args.brand_gene_file)
        if not os.path.isfile(bgf):
            print(f"ERROR: 品牌基因文件不存在: {bgf}", file=sys.stderr)
            sys.exit(1)
        with open(bgf, encoding="utf-8") as f:
            brand_gene = f.read().strip()

    # --- 读取前置分析结果（仅 SIZE 用）---
    analysis_result = ""
    if args.analysis_file:
        af = os.path.abspath(args.analysis_file)
        if not os.path.isfile(af):
            print(f"ERROR: 分析结果文件不存在: {af}", file=sys.stderr)
            sys.exit(1)
        with open(af, encoding="utf-8") as f:
            analysis_result = f.read().strip()

    # --- 构建参数（与编排器共用 build_params）---
    try:
        params = build_params(
            args.type,
            image_urls,
            image_desc=args.image_desc,
            layout=args.layout,
            brand_gene=brand_gene,
            language=args.language,
            analysis_result=analysis_result,
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

    print(f"IMAGEGEN_PROMPT_PATH={out_path}")
    print(f"  type          : {args.type}")
    if args.type == "SIZE":
        print(f"  layout        : {args.layout}  ->  {SIZE_LAYOUT_TEMPLATE.get(args.layout or '普通')}")
        print("  sensitivity   : 已追加敏感词规避指令")
    elif args.type == "WHITE_BG":
        print("  source        : references/types/white-bg.md (静态正文动态提取)")
    print(f"  prompt_length : {len(prompt)} chars")
    print(f"  image_urls    : {len(image_urls)} items")


if __name__ == "__main__":
    main()
