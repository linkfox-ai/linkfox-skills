"""plan phase：S1 推理 + 品牌基因 + 落盘。"""

from __future__ import annotations

import json
import os
from typing import Any

from .brand_gene import extract_brand_gene
from .config import get_variant
from .utils import (
    build_slots_skeleton,
    expand_type_slots,
    extract_image_plan_list,
    load_template,
    merge_s1_result,
    normalize_brand_key,
    parse_json_from_text,
    plan_summary,
    resolve_skill_scripts,
    run_textgen,
    session_datadir,
)


def _needs_s1(job: dict, cfg: dict) -> bool:
    if job.get("skip_s1") is True:
        return False
    scene = (job.get("scene") or "D").upper()
    return scene in cfg["needs_s1_scenes"]


def _needs_brand_gene(job: dict, cfg: dict) -> bool:
    if job.get("brand_gene_file"):
        return False
    if job.get("extract_brand_gene") is False:
        return False
    scene = (job.get("scene") or "D").upper()
    return scene in cfg["extract_brand_gene_scenes"]


def _build_s1_prompt(job: dict, cfg: dict, slots: list[str]) -> str:
    template = load_template(cfg["s1_template"])
    labels = cfg["type_labels"]
    slot_desc = [f"{i}. {labels.get(t, t)} ({t})" for i, t in enumerate(slots, 1)]
    ctx_lines = []
    for key, label in (
        ("point", "用户完整卖点 point"),
        ("pointHint", "用户卖点方向 pointHint"),
        ("imageDesc", "用户画面描述 imageDesc"),
        ("sellingPoints", "商品档案卖点"),
        ("marketingPoints", "营销卖点"),
        ("material", "材质"),
        ("targetPerson", "受众"),
        ("brand", "品牌"),
        ("category", "品类"),
        ("sceneStyling", "场景搭配"),
        ("wearingExperience", "穿着体验"),
    ):
        val = job.get(key)
        if val:
            ctx_lines.append(f"- {label}: {val}")
    hist = job.get("historicalPoints") or []
    hist_text = "\n".join(f"- {p}" for p in hist if p) or "（无）"
    bk = normalize_brand_key(job.get("brandKey"))
    for key, label in (
        ("language", "目标语言 language"),
        ("platform", "平台 platform"),
        ("salesRegion", "销售地区 salesRegion"),
    ):
        val = bk.get(key)
        if val:
            ctx_lines.append(f"- {label}: {val}")
    return (
        template.replace("{slot_list}", "\n".join(slot_desc))
        .replace("{slot_count}", str(len(slots)))
        .replace("{context_block}", "\n".join(ctx_lines) if ctx_lines else "（无额外上下文）")
        .replace("{historical_points}", hist_text)
    )


def run_plan_phase(job: dict, *, skill_root: str, variant_name: str) -> dict[str, Any]:
    cfg = get_variant(variant_name)
    datadir = os.path.abspath(job.get("datadir") or session_datadir())
    os.makedirs(datadir, exist_ok=True)

    image_urls = job.get("imageUrls") or []
    if not image_urls or not all(isinstance(u, str) and u.startswith(("http://", "https://")) for u in image_urls):
        raise ValueError("job.imageUrls 须为非空 https URL 数组")

    aspect_ratio = job.get("aspectRatio") or job.get("ratio") or "1:1"
    aplus_ratio = job.get("aplusRatio") or ""
    scene = (job.get("scene") or "D").upper()
    brand_key = normalize_brand_key(job.get("brandKey"))

    slots = expand_type_slots(job.get("types"), cfg["default_plan_d"])
    skeleton = build_slots_skeleton(
        slots,
        aspect_ratio=aspect_ratio,
        aplus_ratio=aplus_ratio,
        user_image_desc=job.get("imageDesc") or "",
        language=brand_key.get("language") or "英文",
    )

    textgen_script = job.get("textgen_script") or ""
    if not textgen_script or not os.path.isfile(textgen_script):
        expected = resolve_skill_scripts(skill_root)["textgen_script"]
        raise FileNotFoundError(
            f"textgen_script 无效: {textgen_script!r}；"
            f"期望 sibling skills 路径: {expected}"
            + ("" if os.path.isfile(expected) else "（该路径也不存在，请检查 linkfox-aigc-textgen 是否已部署）")
        )

    plan = skeleton
    if _needs_s1(job, cfg):
        prompt = _build_s1_prompt(job, cfg, slots)
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
        s1_list = extract_image_plan_list(parsed)
        if not isinstance(s1_list, list):
            raise ValueError("S1 输出须含 imagePlanList 数组")
        plan = merge_s1_result(skeleton, s1_list)

    brand_gene_file = job.get("brand_gene_file")
    if brand_gene_file:
        brand_gene_file = os.path.abspath(brand_gene_file)
    elif _needs_brand_gene(job, cfg):
        save_script = job.get("brand_gene_save_script") or ""
        brand_gene_file = extract_brand_gene(
            image_urls=image_urls,
            brand_key=brand_key,
            textgen_script=textgen_script,
            save_script=save_script,
        )

    urls_path = os.path.join(datadir, "image-urls.json")
    with open(urls_path, "w", encoding="utf-8") as f:
        json.dump(image_urls, f, ensure_ascii=False)

    plan_path = os.path.join(datadir, "image-plan.json")
    with open(plan_path, "w", encoding="utf-8") as f:
        json.dump({"imagePlanList": plan}, f, ensure_ascii=False, indent=2)

    type_labels = cfg["type_labels"]
    task_specs = []
    for i, entry in enumerate(plan, start=1):
        ttype = entry.get("type") or ""
        label = type_labels.get(ttype, ttype)
        task_specs.append({"id": f"{i}-{label}", "type": ttype, "label": label})

    state = {
        "variant": cfg["variant"],
        "scene": scene,
        "imageUrls": image_urls,
        "image_urls_file": urls_path,
        "provider": job.get("provider") or "BANANA_PRO",
        "resolution": job.get("resolution") or "2K",
        "plan_file": plan_path,
        "brandKey": brand_key,
        "brand_gene_file": brand_gene_file,
        "textgen_script": textgen_script,
        "imagegen_script": job.get("imagegen_script"),
        "run_one_task_script": job.get("run_one_task_script"),
        "skill_root": os.path.abspath(skill_root),
        "datadir": datadir,
        "write_asset_manifest": cfg.get("write_asset_manifest", False),
        "task_specs": task_specs,
    }
    state_path = os.path.join(datadir, "collection-state.json")
    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

    skip_confirm = scene == "E" or job.get("skip_confirm") is True
    return {
        "status": "ready_to_dispatch" if skip_confirm else "awaiting_confirm",
        "skip_confirm": skip_confirm,
        "plan_file": plan_path,
        "state_file": state_path,
        "brand_gene_file": brand_gene_file,
        "image_urls_file": urls_path,
        "run_one_task_script": job.get("run_one_task_script"),
        "total": len(task_specs),
        "specs": [
            {"index": i, "id": s["id"], "type": s["type"], "label": s["label"]}
            for i, s in enumerate(task_specs, start=1)
        ],
        "summary": plan_summary(plan, cfg["type_labels"]),
    }
