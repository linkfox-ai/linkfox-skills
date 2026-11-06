"""Read-only business-specific AIGC model catalog."""
import argparse
import json
import os
import sys
import time
from http.client import HTTPException
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen

VIDEO_CODES = {"SEED_V25": "doubao-seedance-2-5", "SEED": "doubao-seedance-2-0", "HAPPY_HORSE": "happyhorse-v2", "WAN3": "WAN3", "MODEL": "kling-v3-omni", "GEMINI_OMNI_FLASH_1_1": "gemini-omni-flash"}
IMAGE_CODES = {"QWEN_IMAGE_3_PRO": "QWEN_IMAGE_3_PRO"}
LIST_FIELDS = ("supportedRatios", "supportedResolutions", "supportedDurations", "supportedQualities")
# Only documented per-entry limits. Unknown models have no inferred limit.
MULTI_LIMITS = {"BANANA": 3, "BANANA_2_LITE": 10, "BANANA_2": 10, "BANANA_PRO": 10, "WAN2_7": 9, "QWEN_IMAGE_3_PRO": 3, "SEEDREAM5_PRO": 10, "GPT_2_IMAGE": 6, "GPT_2_5_IMAGE": 10, "GPT_2_5_F_IMAGE": 10, "AIDRAW_EDIT": 4}
SUITE_LIMITS = {key: 5 for key in ("BANANA_2", "BANANA_2_LITE", "BANANA_PRO", "WAN2_7", "SEEDREAM5_PRO", "GPT_2_IMAGE", "GPT_2_5_IMAGE", "GPT_2_5_F_IMAGE")}
SUITE_LIMITS["AIDRAW_EDIT"] = 4

def parse_model_args(argv):
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--list-models", action="store_true")
    parser.add_argument("--inline", action="store_true")
    parser.add_argument("--no-cache", action="store_true")
    parser.add_argument("--allowed-models")
    args, remaining = parser.parse_known_args(argv)
    allowed = None
    if args.allowed_models is not None:
        try:
            allowed = json.loads(args.allowed_models)
        except (TypeError, ValueError) as error:
            raise ValueError("--allowed-models must be a JSON array of nonempty strings") from error
        if not isinstance(allowed, list) or not all(isinstance(x, str) and x.strip() for x in allowed):
            raise ValueError("--allowed-models must be a JSON array of nonempty strings")
        if not args.list_models:
            raise ValueError("--allowed-models is only valid with --list-models")
    if args.list_models and remaining:
        raise ValueError("Unrecognized arguments for --list-models: " + " ".join(remaining))
    return args.list_models, args.inline, allowed

def _normalize(row, kind, biz_type):
    if not isinstance(row, dict) or not all(isinstance(row.get(k), str) and row[k].strip() for k in ("code", "name")):
        raise ValueError("Invalid model code or name")
    for key in LIST_FIELDS:
        val = row.get(key)
        if val is not None and (not isinstance(val, list) or not all(isinstance(x, str) for x in val)):
            raise ValueError("Invalid model capability: " + key)
    for key in ("isMaintenance", "supportVoice", "supportLastFrame"):
        if key in row and not isinstance(row[key], bool):
            raise ValueError("Invalid model flag: " + key)
    if "refImageCount" in row and (type(row["refImageCount"]) is not int or row["refImageCount"] < 0):
        raise ValueError("Invalid reference image count")
    extra = row.get("extraConfig")
    if extra is not None and not isinstance(extra, dict):
        raise ValueError("Invalid extraConfig")
    modes = (extra or {}).get("supportModes")
    if modes is not None and (not isinstance(modes, list) or not all(isinstance(x, str) for x in modes)):
        raise ValueError("Invalid supportModes")
    api = row.get("apiCode")
    if api is not None and (not isinstance(api, str) or not api.strip()):
        raise ValueError("Invalid apiCode")
    item = dict(row)
    value = api or (IMAGE_CODES if kind == "image" else VIDEO_CODES).get(row["code"])
    item["requestValue"] = value
    item["aliases"] = list(dict.fromkeys(x for x in (row["code"], api, value, row["name"]) if x))
    if "refImageCount" in row:
        item["modelRefImageCount"] = row["refImageCount"]
        limit = 1 if biz_type == 61 else (MULTI_LIMITS.get(value) if biz_type == 62 else SUITE_LIMITS.get(value) if biz_type in (69, 71) else None)
        if limit is not None:
            item["refImageCount"] = min(row["refImageCount"], limit)
        elif biz_type in (62, 69, 71):
            item["refImageCount"] = None
    return item

def _select(models, allowed):
    selected = []
    seen = set()
    allowed_set = None if allowed is None else {x.strip().casefold() for x in allowed}
    for item in models:
        if item.get("isMaintenance") is True:
            continue
        aliases = item.get("aliases") or [x for x in (item.get("code"), item.get("name"), item.get("requestValue")) if isinstance(x, str)]
        if allowed_set is not None and not allowed_set.intersection(x.casefold() for x in aliases):
            continue
        value = item.get("requestValue")
        key = value.casefold() if isinstance(value, str) and value else None
        if key is not None and key in seen:
            continue
        if key is not None:
            seen.add(key)
        selected.append(item)
    return selected

def load_catalog(kind, biz_type, allowed=None):
    base = (os.environ.get("LINKFOX_AI_API_URL", "").strip() or "https://ai-api.linkfox.com").rstrip("/")
    path = "/image/model/config/list" if kind == "image" else "/image/video/model/config/list"
    result = {"source": "remote", "bizType": biz_type, "entry": kind}
    try:
        request = Request(base + path + "?bizType=" + str(biz_type), headers={"Referer": "https://wiki.linkfox.com/", "User-Agent": "LinkFox-Skill/2.0"})
        with urlopen(request, timeout=5) as response:
            payload = json.loads(response.read().decode("utf-8"))
        if not isinstance(payload, dict) or payload.get("code") not in (200, "200") or not isinstance(payload.get("data"), list):
            raise ValueError("Invalid model catalog response")
        result.update(models=_select([_normalize(row, kind, biz_type) for row in payload["data"]], allowed), rawResponse=payload)
    except (URLError, HTTPException, OSError, TimeoutError, UnicodeError, ValueError) as error:
        with Path(__file__).with_name("model_fallback.json").open(encoding="utf-8") as handle:
            models = json.load(handle)
        result.update(source="fallback", fallbackReason=type(error).__name__, models=_select(models, allowed))
    return result

def list_models(kind, biz_type, slug, resolve_data_path, inline, allowed=None):
    catalog = load_catalog(kind, biz_type, allowed)
    out = None
    try:
        out = resolve_data_path(slug + "-models", time.time())
        with open(out, "w", encoding="utf-8") as handle:
            json.dump(catalog, handle, ensure_ascii=False, indent=2)
    except OSError as error:
        print("Failed to save model catalog: " + str(error), file=sys.stderr)
    result = {key: value for key, value in catalog.items() if key != "rawResponse"}
    result["dataFile"] = out
    if not inline and len(json.dumps(result, ensure_ascii=False).encode("utf-8")) > 8000:
        result["modelCount"] = len(result["models"])
        result["models"] = [{key: model.get(key) for key in ("name", "code", "requestValue")} for model in result["models"]]
        result["notice"] = "See dataFile for full capabilities, or use --inline."
    print(json.dumps(result, ensure_ascii=False))
