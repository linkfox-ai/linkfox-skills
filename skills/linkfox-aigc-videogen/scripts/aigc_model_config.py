"""Query-only public AIGC catalog. Never validate or rewrite generation requests.

Canonical source: linkfox-skills-repository skills/linkfox-aigc-imagegen/scripts/aigc_model_config.py.
Deploy a byte-for-byte
copy and aigc_model_fallbacks.json beside each generation script; no cross-skill imports.
Only the public config host receives GETs, never gateway credentials or session headers.
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import sys
import time
from pathlib import Path
from http.client import HTTPException
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

# Production default only; resolve LINKFOX_AI_API_URL separately for each query.
CONFIG_BASE_URL = "https://ai-api.linkfox.com"
CONFIG_TIMEOUT = 5
# Effective input capacity of the unchanged imageGenAsync entry, not a model whitelist.
IMAGE_ENTRY_REF_IMAGE_LIMIT = 10
IMAGE_ALIASES = {
    "BANANA": "LF_BN_1", "BANANA_2": "LF_BN_2", "BANANA_PRO": "LF_BN_3",
    "GPT_2_IMAGE": "LF_GT_1", "AIDRAW_EDIT": "LF_AD_1", "WAN2_7": "LF_WN_1",
    "SEEDREAM5": "LF_SD_1", "GPT_2_5_IMAGE": "LF_GT_2",
    "GPT_2_5_F_IMAGE": "LF_GT_2_F", "SEEDREAM5_PRO": "LF_SD_2",
    "GEMINI_FLASH": "LF_BN_1", "GEMINI_31_FLASH_IMAGE": "LF_BN_2",
    "GEMINI_FLASH_PRO": "LF_BN_3", "GEMINI_NANO_BANANA_2_1": "BANANA_2_1",
    "GEMINI_31_FLASH_LITE": "BANANA_2_LITE",
}
VIDEO_ALIASES = {"MODEL": "KLING", "PRODUCT": "HAILUO", "HAILUO3": "MINIMAX_V2"}
LIST_FIELDS = ("supportedRatios", "supportedResolutions", "supportedDurations", "supportedQualities")
CAPABILITY_FIELDS = LIST_FIELDS + ("refImageCount", "supportVoice", "supportLastFrame", "supportCamera",
                                  "supportEcoMode", "supportPromptExpand", "defaultResolution", "extraConfig")


def get_config_base_url():
    """Resolve the model-config service independently from the generation gateway."""
    return (os.environ.get("LINKFOX_AI_API_URL", "").strip() or CONFIG_BASE_URL).rstrip("/")


def canonical_request(kind, value):
    if not isinstance(value, str):
        raise ValueError("模型请求值必须是字符串")
    value = value.strip()
    upper = value.upper()
    aliases = IMAGE_ALIASES if kind == "image" else VIDEO_ALIASES
    known = set(aliases.values()) if kind == "image" else {"KLING", "SEED", "SEED_FAST", "SEED_V25", "SEED_MINI", "HAPPY_HORSE", "MINIMAX_V2", "WAN", "WAN3", "HAILUO", "MODEL_V2_6"}
    return aliases.get(upper, upper if upper in known else value)


def _normalize(kind, row):
    if not isinstance(row, dict) or not all(isinstance(row.get(k), str) and row[k].strip() for k in ("code", "name")):
        raise ValueError("模型配置条目缺少 code/name")
    for key in LIST_FIELDS:
        if key in row and row[key] is not None and (not isinstance(row[key], list) or not all(isinstance(v, str) for v in row[key])):
            raise ValueError("模型能力列表格式错误: " + key)
    for key in ("isMaintenance", "supportVoice", "supportLastFrame"):
        if key in row and not isinstance(row[key], bool):
            raise ValueError("模型能力开关格式错误: " + key)
    if "refImageCount" in row and (type(row["refImageCount"]) is not int or row["refImageCount"] < 0):
        raise ValueError("模型参考图上限格式错误")
    if row.get("extraConfig") is not None and not isinstance(row["extraConfig"], dict):
        raise ValueError("模型扩展能力格式错误")
    modes = (row.get("extraConfig") or {}).get("supportModes")
    if modes is not None and (not isinstance(modes, list) or not all(isinstance(v, str) for v in modes)):
        raise ValueError("模型模式列表格式错误")
    if kind == "image":
        # Unknown configuration codes without apiCode cannot safely be sent as providers.
        value = row.get("apiCode") or (row["code"] if row["code"].upper() in IMAGE_ALIASES or row["code"].startswith("LF_") else None)
        if not isinstance(value, str) or not value.strip():
            return None
    else:
        # Video apiCode is a downstream provider ID, NOT the tool gateway videoType.
        value = row["code"]
    request_value = canonical_request(kind, value)
    result = {k: copy.deepcopy(row[k]) for k in CAPABILITY_FIELDS if k in row}
    if kind == "image" and "refImageCount" in result:
        result["modelRefImageCount"] = result["refImageCount"]
        result["refImageCount"] = min(result["refImageCount"], IMAGE_ENTRY_REF_IMAGE_LIMIT)
    result.update(name=row["name"], code=row["code"], requestValue=request_value,
                  isDefault=bool(row.get("isDefault", False)), isMaintenance=bool(row.get("isMaintenance", False)))
    if row.get("apiCode"):
        result["apiCode"] = row["apiCode"]
    result["aliases"] = list(dict.fromkeys([row["code"], value, request_value, row["name"]]))
    return result


def _filter(kind, rows, allowed_models):
    if allowed_models is not None and (not isinstance(allowed_models, (list, tuple)) or not all(isinstance(v, str) and v.strip() for v in allowed_models)):
        raise ValueError("业务模型白名单必须是字符串数组")
    allowed = None if allowed_models is None else {canonical_request(kind, v) for v in allowed_models}
    normalized = [_normalize(kind, row) for row in rows]
    # Prefer the canonical channel record; never union incompatible channel capabilities.
    chosen = {}
    for item in (v for v in normalized if v is not None):
        key = item["requestValue"]
        old = chosen.get(key)
        if old is None or item["code"].upper() == key:
            chosen[key] = item
    models = []
    for item in chosen.values():
        if item["isMaintenance"]:
            continue
        if allowed is not None and item["requestValue"] not in allowed and not any(canonical_request(kind, v) in allowed for v in item["aliases"]):
            continue
        modes = (item.get("extraConfig") or {}).get("supportModes")
        if kind == "video" and modes is not None and not {"refImage", "firstLastFrame"}.intersection(modes):
            continue
        if kind == "video_multi":
            modes = (item.get("extraConfig") or {}).get("supportModes")
            if modes is not None and "refImage" not in modes:
                continue
            if item.get("refImageCount", 0) < 1:
                continue
        models.append(item)
    return models


def load_catalog(kind, allowed_models=None):
    if kind not in ("image", "video", "video_multi"):
        raise ValueError("未知生成入口")
    # Validate caller restrictions before network handling; a bad allowlist is not a fetch failure.
    if allowed_models is not None and (not isinstance(allowed_models, (list, tuple)) or not all(isinstance(v, str) and v.strip() for v in allowed_models)):
        raise ValueError("业务模型白名单必须是字符串数组")
    biz_type = 201 if kind == "image" else 88
    endpoint = "/image/model/config/list" if kind == "image" else "/image/video/model/config/list"
    catalog = {"source": "remote", "bizType": biz_type, "entry": kind}
    try:
        request = Request(get_config_base_url() + endpoint + "?bizType=" + str(biz_type),
                          headers={"Referer": "https://wiki.linkfox.com/", "User-Agent": "LinkFox-Skill/2.0"}, method="GET")
        with urlopen(request, timeout=CONFIG_TIMEOUT) as response:
            payload = json.loads(response.read().decode("utf-8"))
        if not isinstance(payload, dict) or payload.get("code") not in (200, "200") or not isinstance(payload.get("data"), list):
            raise ValueError("模型列表响应状态或结构错误")
        # [] and all-maintenance are valid successes: do NOT revive static models.
        catalog["models"] = _filter(kind, payload["data"], allowed_models)
        catalog["rawResponse"] = payload
    except (HTTPError, URLError, HTTPException, OSError, TimeoutError, UnicodeError, ValueError) as error:
        with Path(__file__).with_name("aigc_model_fallbacks.json").open(encoding="utf-8") as handle:
            fallback = json.load(handle)
        catalog.update(source="fallback", fallbackReason=type(error).__name__,
                       models=_filter(kind, fallback[kind], allowed_models))
    return catalog



def parse_model_args(argv):
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--list-models", action="store_true")
    parser.add_argument("--allowed-models")
    parser.add_argument("--inline", action="store_true")
    options, remaining = parser.parse_known_args(argv)
    try:
        allowed = None if options.allowed_models is None else json.loads(options.allowed_models)
    except json.JSONDecodeError as error:
        raise ValueError("--allowed-models 必须是 JSON 字符串数组") from error
    if options.allowed_models is not None and (not isinstance(allowed, list) or not all(isinstance(v, str) and v.strip() for v in allowed)):
        raise ValueError("--allowed-models 必须是 JSON 字符串数组")
    if options.allowed_models is not None and not options.list_models:
        raise ValueError("--allowed-models 仅用于模型列表查询；生成仍按原业务流程提交参数")
    return options.list_models, allowed, options.inline, remaining


def save_catalog(catalog, resolve_data_path, slug):
    try:
        out = resolve_data_path(slug + "-models", time.time())
        with open(out, "w", encoding="utf-8") as handle:
            json.dump(catalog, handle, ensure_ascii=False, indent=2)
        return out
    except OSError as error:
        print("Failed to save model config: " + str(error), file=sys.stderr)
        return None


def print_catalog(catalog, out, inline=False):
    result = {k: v for k, v in catalog.items() if k != "rawResponse"}
    result["dataFile"] = out
    serialized = json.dumps(result, ensure_ascii=False)
    if not inline and len(serialized.encode("utf-8")) > 8000:
        result["modelCount"] = len(result["models"])
        result["models"] = [{k: m[k] for k in ("name", "requestValue")} for m in result["models"]]
        result["notice"] = "完整能力见 dataFile；或 --list-models --inline"
    # This is configuration, NOT a media result: don't emit Saved full response.
    print(json.dumps(result, ensure_ascii=False))
