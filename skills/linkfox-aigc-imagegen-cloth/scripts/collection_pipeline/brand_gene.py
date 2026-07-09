"""品牌基因提取（plan phase 内 subprocess 调 textgen）。"""

from __future__ import annotations

import json
import os
import sys

from .utils import load_template, normalize_brand_key, parse_json_from_text, run_subprocess, run_textgen


def _fill_missing_fields(gene: dict) -> dict:
    bc = gene.setdefault("brandColor", {})
    if isinstance(bc, dict):
        bc.setdefault("brandColor (品牌主色)", "#EAF86C")
        bc.setdefault("背景策略-风格定义", "现代极简生活方式场景，符合目标市场审美")
        bc.setdefault("背景策略-场景关键词", "自然光, 木质, 绿植, 简约")
        bc.setdefault("背景策略-光影", "柔和自然侧光，暖色温，轻微长投影增强立体感")
        bc.setdefault("Brand Injection（品牌植入）", "品牌主色作为点缀色自然融入场景道具")
    fs = gene.setdefault("fontStyle", {})
    if isinstance(fs, dict):
        fs.setdefault("字体策略", "几何无衬线体")
        fs.setdefault("字体风格", "Montserrat")
        fs.setdefault("颜色策略-Heading", '["Heading Color"：品牌主色]')
        fs.setdefault("颜色策略-Body/Sub", '["Body color"：#333333]')
        fs.setdefault(
            "灵活反白",
            "You are authorized to switch to Matte White (#FFFFFF) text whenever using a dark background or a solid brand-color panel.",
        )
        fs.setdefault("排版", "Non-italic, standard leading")
    return gene


def extract_brand_gene(
    *,
    image_urls: list[str],
    brand_key: dict | None,
    textgen_script: str,
    save_script: str,
) -> str:
    bk = normalize_brand_key(brand_key)
    template = load_template("brand-gene-extract.txt")
    prompt = template.replace("{brand_key_json}", json.dumps(bk, ensure_ascii=False, indent=2))
    content = run_textgen(
        textgen_script,
        {
            "prompt": prompt,
            "imageUrls": image_urls,
            "model": "GEM_3_1_PRO",
            "thinkingLevel": "high",
        },
    )
    parsed = parse_json_from_text(content)
    if isinstance(parsed, list):
        if not parsed:
            raise RuntimeError("brandGeneJson 为空列表")
        gene = parsed[0]
    elif isinstance(parsed, dict):
        gene = parsed
    else:
        raise RuntimeError(f"brandGeneJson 格式异常: {type(parsed)}")
    gene = _fill_missing_fields(gene)
    payload = [gene]

    if not os.path.isfile(save_script):
        raise FileNotFoundError(f"save_brand_gene 脚本不存在: {save_script}")

    proc = run_subprocess([sys.executable, save_script], input_text=json.dumps(payload, ensure_ascii=False))
    if proc.returncode != 0:
        raise RuntimeError(f"save_brand_gene 失败: {(proc.stderr or proc.stdout or '').strip()}")
    for line in (proc.stdout or "").splitlines():
        if "Saved full response:" in line:
            path = line.split("Saved full response:", 1)[1].strip().split(" ", 1)[0]
            return os.path.abspath(path)
    raise RuntimeError("save_brand_gene 未返回 Saved full response 路径")
