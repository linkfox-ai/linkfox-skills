"""套图编排 variant 配置（cloth / product）。"""

from __future__ import annotations

APLUS_TYPES = frozenset({"PREMIUM_APLUS", "STANDARD_APLUS", "PHONE_APLUS"})
SP_APLUS_TYPES = frozenset({"SELLING_POINT", *APLUS_TYPES})
SIZE_TYPES = frozenset({"SIZE"})
SP_LAYOUTS = ["概览", "功能", "品质", "场景"]
SIZE_LAYOUTS = ["普通", "三版"]

TYPE_LABELS_CLOTH = {
    "WHITE_BG": "白底图",
    "MODEL_IMAGE": "模特图",
    "SCENE": "种草图",
    "SELLING_POINT": "卖点图",
    "PREMIUM_APLUS": "高级A+图",
    "STANDARD_APLUS": "普通A+图",
    "PHONE_APLUS": "手机A+图",
    "SIZE": "尺码图",
}

TYPE_LABELS_PRODUCT = {
    "WHITE_BG": "白底图",
    "SCENE": "场景图",
    "CLOSE_UP": "特写图",
    "SELLING_POINT": "卖点图",
    "PREMIUM_APLUS": "高级A+图",
    "STANDARD_APLUS": "普通A+图",
    "PHONE_APLUS": "手机A+图",
}

DEFAULT_RATIOS = {
    "WHITE_BG": "1:1",
    "MODEL_IMAGE": "1:1",
    "SCENE": "1:1",
    "CLOSE_UP": "1:1",
    "SELLING_POINT": "1:1",
    "SIZE": "1:1",
    "PREMIUM_APLUS": "1464:600",
    "STANDARD_APLUS": "970:600",
    "PHONE_APLUS": "600:450",
}

VARIANTS = {
    "cloth": {
        "variant": "cloth",
        "default_plan_d": [
            ("SELLING_POINT", 3),
            ("SCENE", 2),
            ("MODEL_IMAGE", 1),
            ("WHITE_BG", 1),
        ],
        "type_labels": TYPE_LABELS_CLOTH,
        "s1_template": "s1-reasoning-cloth.txt",
        "needs_s1_scenes": frozenset({"B", "C", "D", "F"}),
        "extract_brand_gene_scenes": frozenset({"D"}),
        "write_asset_manifest": False,
    },
    "product": {
        "variant": "product",
        "default_plan_d": [
            ("SELLING_POINT", 3),
            ("SCENE", 2),
            ("WHITE_BG", 1),
        ],
        "type_labels": TYPE_LABELS_PRODUCT,
        "s1_template": "s1-reasoning-product.txt",
        "needs_s1_scenes": frozenset({"B", "C", "D", "F"}),
        "extract_brand_gene_scenes": frozenset({"D"}),
        "write_asset_manifest": True,
    },
}


def get_variant(name: str) -> dict:
    key = (name or "").strip().lower()
    if key not in VARIANTS:
        raise ValueError(f"未知 variant: {name!r}，可选: {', '.join(VARIANTS)}")
    return VARIANTS[key]
