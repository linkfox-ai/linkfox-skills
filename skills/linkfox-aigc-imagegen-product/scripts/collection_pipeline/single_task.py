"""单任务驱动器（cloth / product 共用）

由 ``--state <collection-state.json> --index <i>`` 在内存组装第 i 个任务，按类型分支跑：
  - textgen 改写支线（SCENE / SELLING_POINT / *_APLUS / cloth SIZE 阶段1）
  - 占位符直出支线（cloth MODEL_IMAGE / cloth SIZE 阶段2）
  - 静态直出支线（WHITE_BG）

stdout：一行 ``Saved full response: …``（成功为图片路径数组，失败为错误 JSON 路径）；
同时落盘 ``<datadir>/task-result-<id>.json`` 供 summary 阶段汇总。
被 dispatch 用 ``subprocess.run(capture_output=True)`` 调用——这行不会冒到对话气泡。
完整交付协议见 ``references/runtime/03-deliver.md``。
"""

from __future__ import annotations

import argparse
import importlib
import json
import os
import re
import subprocess
import sys
import time
from typing import Any, Callable

from .config import get_variant
from .utils import normalize_brand_key, write_task_result

SAVED_RE = re.compile(r"Saved full response:\s*(.+)\s*$", re.M)
TEXTGEN_TIMEOUT = 360
IMAGEGEN_TIMEOUT = 720

TRANSIENT_RE = re.compile(
    r"(Connection failed|Connection reset|timed?\s?out|timeout|Temporary failure|"
    r"HTTP 5\d\d|URLError|Polling timeout|Max retries|Read timed out)",
    re.I,
)
RETRY_BACKOFF_SEC = 2.0

CLOTH_TEXTGEN_TYPES = {"SCENE", "SELLING_POINT", "PREMIUM_APLUS", "STANDARD_APLUS", "PHONE_APLUS"}
PRODUCT_TEXTGEN_TYPES = {"SCENE", "CLOSE_UP", "SELLING_POINT", "PREMIUM_APLUS", "STANDARD_APLUS", "PHONE_APLUS"}
CLOTH_BRAND_GENE_TEXTGEN_TYPES = {"SELLING_POINT", "PREMIUM_APLUS", "STANDARD_APLUS", "PHONE_APLUS"}

CLOTH_DIRECT_IMAGEGEN_TYPES = {"WHITE_BG", "MODEL_IMAGE"}
PRODUCT_DIRECT_IMAGEGEN_TYPES = {"WHITE_BG"}

PRODUCT_ASSET_SLOT_BY_TYPE = {
    "WHITE_BG": "main",
    "SCENE": "main",
    "CLOSE_UP": "main",
    "SELLING_POINT": "main",
    "PREMIUM_APLUS": "aplus",
    "STANDARD_APLUS": "aplus",
    "PHONE_APLUS": "aplus",
}
PRODUCT_ASSET_LABEL_BY_TYPE = {
    "WHITE_BG": "白底图",
    "SCENE": "场景图",
    "CLOSE_UP": "特写图",
    "SELLING_POINT": "卖点图",
    "PREMIUM_APLUS": "高级A+图",
    "STANDARD_APLUS": "普通A+图",
    "PHONE_APLUS": "手机A+图",
}


def _log(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


def _is_transient(msg: str) -> bool:
    return bool(TRANSIENT_RE.search(msg or ""))


def _with_retry(label: str, fn: Callable[[], Any]) -> Any:
    """瞬时错误自动重试 1 次（退避 RETRY_BACKOFF_SEC）；业务失败直接抛出不重试。"""
    try:
        return fn()
    except RuntimeError as e:
        if _is_transient(str(e)):
            _log(f"[{label}] 瞬时错误，{RETRY_BACKOFF_SEC:.0f}s 后自动重试 1 次：{e}")
            time.sleep(RETRY_BACKOFF_SEC)
            return fn()
        raise


def _run_textgen(textgen_script: str, params: dict, task_id: str) -> str:
    """调官方 aigc_textgen.py --stdin --content-only，返回单行 content（换行为 ⏎ 占位符）。"""
    proc = subprocess.run(
        [sys.executable, textgen_script, "--stdin", "--content-only"],
        input=json.dumps(params, ensure_ascii=False),
        text=True,
        capture_output=True,
        timeout=TEXTGEN_TIMEOUT,
    )
    if proc.returncode != 0:
        tail = (proc.stderr or "").strip().splitlines()[-3:]
        raise RuntimeError(f"textgen 失败(exit={proc.returncode}): {' | '.join(tail)}")
    content = proc.stdout.rstrip("\n")
    if not content:
        raise RuntimeError("textgen 返回空 content")
    return content


def _run_imagegen(imagegen_script: str, params: dict, task_id: str) -> list[str]:
    """调官方 aigc_imagegen.py '<json>'，解析 'Saved full response:' 判定成败。"""
    proc = subprocess.run(
        [sys.executable, imagegen_script, json.dumps(params, ensure_ascii=False)],
        text=True,
        capture_output=True,
        timeout=IMAGEGEN_TIMEOUT,
    )
    m = SAVED_RE.search(proc.stdout or "")
    if not m:
        tail = (proc.stderr or proc.stdout or "").strip().splitlines()[-3:]
        raise RuntimeError(f"imagegen 无 'Saved full response' 输出: {' | '.join(tail)}")
    payload = m.group(1).strip()
    if payload.startswith("["):
        try:
            images = json.loads(payload)
        except json.JSONDecodeError:
            raise RuntimeError(f"imagegen 图片路径数组解析失败: {payload[:120]}")
        if not images:
            raise RuntimeError("imagegen 返回空图片数组")
        return images
    raise RuntimeError(f"imagegen 业务失败，错误详情见: {payload}")


def _resolve_brand_gene_text(spec: dict) -> str:
    """优先从 brand_gene_file 读盘；兼容内联 brand_gene_json。"""
    path = spec.get("brand_gene_file")
    if path:
        path = os.path.abspath(path)
        if not os.path.isfile(path):
            raise RuntimeError(f"brand_gene_file 不存在: {path}")
        with open(path, encoding="utf-8") as f:
            return json.dumps(json.load(f), ensure_ascii=False)
    return spec.get("brand_gene_json") or ""


def _load_skill_module(skill_root: str, module_name: str):
    """从指定 skill 的 scripts/ 目录动态导入 build_textgen_params / build_imagegen_prompt。"""
    scripts_dir = os.path.join(os.path.abspath(skill_root), "scripts")
    if not os.path.isdir(scripts_dir):
        raise RuntimeError(f"skill scripts 目录不存在: {scripts_dir}")
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    sys.modules.pop(module_name, None)
    return importlib.import_module(module_name)


def _build_assets_for_product(spec: dict, images: list[str]) -> list[dict]:
    """product variant 单任务结果对应的 asset 条目（供 summary 合并 asset manifest）。"""
    ttype = spec.get("type") or ""
    slot = PRODUCT_ASSET_SLOT_BY_TYPE.get(ttype, "main")
    base_label = spec.get("label") or PRODUCT_ASSET_LABEL_BY_TYPE.get(ttype, ttype or "图片")
    assets: list[dict] = []
    for idx, image in enumerate(images, start=1):
        if not isinstance(image, str) or not image:
            continue
        label = base_label if len(images) == 1 else f"{base_label} {idx}"
        asset: dict[str, Any] = {
            "src": image,
            "label": label,
            "kind": "image",
            "slot": slot,
            "type": ttype,
            "sourceTaskId": spec.get("id"),
        }
        for key in ("point", "layout", "image_desc", "ratio"):
            if spec.get(key):
                asset[key] = spec[key]
        assets.append(asset)
    return assets


def build_spec_from_plan(
    entry: dict,
    state: dict,
    *,
    variant: str,
    idx: int,
    type_labels: dict[str, str],
) -> dict:
    """从 image-plan entry + collection-state 在内存组装单任务 spec。

    - 任务级字段来自 plan entry：type / ratio / point / image_desc / layout / analysis_result / language(SIZE)
    - 编排级字段来自 state：imageUrls / provider / resolution / textgen_script / imagegen_script / brand_gene_file
    - brandKey → language / sales_region / platform（任务级 language 优先，主要为 SIZE）
    """
    ttype = entry.get("type")
    if not ttype:
        raise RuntimeError(f"image-plan 第 {idx} 条缺少 type")
    label = type_labels.get(ttype, ttype)

    image_urls = state.get("imageUrls") or []
    if not image_urls:
        urls_file = state.get("image_urls_file")
        if urls_file and os.path.isfile(os.path.abspath(urls_file)):
            with open(os.path.abspath(urls_file), encoding="utf-8") as f:
                image_urls = json.load(f)

    bk = normalize_brand_key(state.get("brandKey"))
    spec: dict[str, Any] = {
        "id": f"{idx}-{label}",
        "type": ttype,
        "label": label,
        "image_urls": image_urls,
        "ratio": entry.get("ratio") or "1:1",
        "provider": state.get("provider") or "BANANA_PRO",
        "resolution": state.get("resolution") or "2K",
        "textgen_script": state.get("textgen_script") or "",
        "imagegen_script": state.get("imagegen_script") or "",
        "brand_gene_file": state.get("brand_gene_file") or "",
        "datadir": os.path.abspath(state.get("datadir") or "."),
        "language": entry.get("language") or bk.get("language") or "英文",
        "sales_region": bk.get("salesRegion") or "美国",
        "platform": bk.get("platform") or "亚马逊",
    }
    for key in ("point", "desc", "image_desc", "layout", "analysis_result"):
        val = entry.get(key)
        if val:
            spec[key] = val
    del variant
    return spec


def _process_task(spec: dict, variant: str, skill_root: str) -> dict:
    """跑完单任务链路，返回与 task-result-<id>.json 同 schema 的结果 dict。"""
    tid = spec.get("id") or spec.get("type") or "unknown"
    ttype = spec.get("type") or ""
    image_urls = spec.get("image_urls") or []
    ratio = spec.get("ratio") or "1:1"
    label = spec.get("label") or ttype

    result: dict[str, Any] = {
        "id": tid,
        "type": ttype,
        "label": label,
        "status": "failed",
        "images": [],
        "error": None,
        "ratio": ratio,
    }
    for key in ("point", "desc", "layout", "image_desc"):
        val = spec.get(key)
        if val:
            result[key] = val

    try:
        if not isinstance(image_urls, list) or not image_urls:
            raise RuntimeError("image_urls 为空——拒绝带空图出图（步骤1护栏）")
        if not all(isinstance(u, str) and u.startswith(("http://", "https://")) for u in image_urls):
            raise RuntimeError("image_urls 含非 http(s) 地址——需先经 linkfox-file-upload 上传")

        textgen_script = spec.get("textgen_script") or ""
        imagegen_script = spec.get("imagegen_script") or ""
        provider = spec.get("provider") or "BANANA_PRO"
        resolution = spec.get("resolution") or "2K"
        if not os.path.isfile(imagegen_script):
            raise RuntimeError(f"imagegen_script 路径不存在: {imagegen_script}")

        bt_module = _load_skill_module(skill_root, "build_textgen_params")
        bi_module = _load_skill_module(skill_root, "build_imagegen_prompt")

        brand_gene = _resolve_brand_gene_text(spec)
        language = spec.get("language") or "英文"
        sales_region = spec.get("sales_region") or "美国"
        platform = spec.get("platform") or "亚马逊"

        textgen_types = CLOTH_TEXTGEN_TYPES if variant == "cloth" else PRODUCT_TEXTGEN_TYPES
        direct_types = CLOTH_DIRECT_IMAGEGEN_TYPES if variant == "cloth" else PRODUCT_DIRECT_IMAGEGEN_TYPES

        # 分支 1：textgen 改写 → imagegen
        if ttype in textgen_types:
            if not os.path.isfile(textgen_script):
                raise RuntimeError(f"textgen_script 路径不存在: {textgen_script}")
            tg_brand = brand_gene
            if variant == "cloth" and ttype not in CLOTH_BRAND_GENE_TEXTGEN_TYPES:
                tg_brand = ""
            tg_params = bt_module.build_params(
                ttype, image_urls,
                point=spec.get("point", ""),
                layout=spec.get("layout", ""),
                image_desc=spec.get("image_desc", ""),
                brand_gene=tg_brand,
                language=language,
                sales_region=sales_region,
                platform=platform,
                ratio=ratio,
            )
            _log(f"[{tid}] textgen 改写中…")
            final_prompt = _with_retry(
                f"{tid} textgen", lambda: _run_textgen(textgen_script, tg_params, tid)
            )
            ig_params = {
                "prompt": final_prompt,
                "imageUrls": image_urls,
                "provider": provider,
                "outputNum": 1,
                "aspectRatio": ratio,
                "resolution": resolution,
            }
            _log(f"[{tid}] 出图中…")
            result["images"] = _with_retry(
                f"{tid} imagegen", lambda: _run_imagegen(imagegen_script, ig_params, tid)
            )
            result["status"] = "success"
            if variant == "product":
                result["assets"] = _build_assets_for_product(spec, result["images"])
            return result

        # 分支 2：cloth SIZE 两阶段（阶段1 textgen 前置分析 → 阶段2 占位符出图）
        if variant == "cloth" and ttype == "SIZE":
            if not os.path.isfile(textgen_script):
                raise RuntimeError(f"textgen_script 路径不存在: {textgen_script}")
            analysis = spec.get("analysis_result") or ""
            if not analysis:
                pre_params = bt_module.build_params("SIZE_PRE_ANALYSIS", image_urls)
                _log(f"[{tid}] 尺码图阶段1 前置分析中…")
                analysis = _with_retry(
                    f"{tid} 阶段1", lambda: _run_textgen(textgen_script, pre_params, tid)
                )
            ig_params = bi_module.build_params(
                "SIZE", image_urls,
                layout=spec.get("layout", "普通"),
                brand_gene=brand_gene,
                language=language,
                analysis_result=analysis,
            )
            ig_params.update(
                provider=provider, outputNum=1,
                aspectRatio=ratio, resolution=resolution,
            )
            _log(f"[{tid}] 尺码图阶段2 出图中…")
            result["images"] = _with_retry(
                f"{tid} imagegen", lambda: _run_imagegen(imagegen_script, ig_params, tid)
            )
            result["status"] = "success"
            return result

        # 分支 3：占位符 / 静态直出（一步 imagegen）
        if ttype in direct_types:
            if variant == "cloth":
                ig_params = bi_module.build_params(
                    ttype, image_urls,
                    image_desc=spec.get("image_desc", ""),
                )
            else:
                ig_params = bi_module.build_params(ttype, image_urls)
            ig_params.update(
                provider=provider, outputNum=1,
                aspectRatio=ratio, resolution=resolution,
            )
            _log(f"[{tid}] 出图中…")
            result["images"] = _with_retry(
                f"{tid} imagegen", lambda: _run_imagegen(imagegen_script, ig_params, tid)
            )
            result["status"] = "success"
            if variant == "product":
                result["assets"] = _build_assets_for_product(spec, result["images"])
            return result

        raise RuntimeError(f"variant={variant} 不支持任务类型: {ttype}")

    except Exception as e:  # noqa: BLE001 单任务失败不能传播至 Bash 退出码
        result["error"] = str(e)
        _log(f"[{tid}] ❌ {e}")
        return result


def _emit_and_persist(result: dict, datadir: str) -> None:
    """单任务完成后：emit 一行 Saved full response，落盘 task-result 片段。"""
    write_task_result(datadir, result)
    if result.get("status") in ("success", "dry-run") and result.get("images"):
        body = json.dumps(list(result["images"]), ensure_ascii=False)
        print(f"Saved full response: {body}", flush=True)
        return
    err_path = _write_error_file(datadir, result)
    print(f"Saved full response: {err_path}", flush=True)


def _write_error_file(datadir: str, result: dict) -> str:
    """落盘单任务错误 JSON（与 imagegen 失败协议字段对齐：errcode/errmsg/error）。"""
    os.makedirs(datadir, exist_ok=True)
    ts = int(time.time() * 1000)
    safe_id = re.sub(r"[^0-9A-Za-z\u4e00-\u9fff_-]+", "-", str(result.get("id") or "unknown"))
    payload = {
        "errcode": 5000,
        "errmsg": "collection task failed",
        "error": str(result.get("error") or "unknown error"),
        "taskId": result.get("id"),
        "taskType": result.get("type"),
        "ratio": result.get("ratio"),
        "label": result.get("label"),
    }
    path = os.path.join(datadir, f"collection-task-error-{safe_id}-{ts}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return os.path.abspath(path)


def main(variant: str, *, skill_root: str | None = None) -> int:
    """CLI 入口，由 cloth / product 的 ``scripts/run_one_task.py`` 薄壳调用。"""
    cfg = get_variant(variant)
    parser = argparse.ArgumentParser(description=f"套图单任务驱动器（variant={cfg['variant']}）")
    parser.add_argument("--state", required=True, help="collection-state.json 路径（plan 阶段已落盘）")
    parser.add_argument("--index", required=True, type=int, help="任务序号（1-based，对应 image-plan.json 第 i 条）")
    args = parser.parse_args()

    state_path = os.path.abspath(args.state)
    if not os.path.isfile(state_path):
        print(f"ERROR: state 文件不存在: {state_path}", file=sys.stderr)
        return 2
    with open(state_path, encoding="utf-8") as f:
        state = json.load(f)

    plan_path = os.path.abspath(state.get("plan_file") or "")
    if not os.path.isfile(plan_path):
        print(f"ERROR: image-plan.json 不存在: {plan_path}", file=sys.stderr)
        return 2
    with open(plan_path, encoding="utf-8") as f:
        plan_list = (json.load(f) or {}).get("imagePlanList") or []

    idx = args.index
    if idx < 1 or idx > len(plan_list):
        print(f"ERROR: --index {idx} 超出 imagePlanList 范围 [1, {len(plan_list)}]", file=sys.stderr)
        return 2
    entry = plan_list[idx - 1]

    skill_root_abs = os.path.abspath(skill_root) if skill_root else None
    if not skill_root_abs:
        if not state.get("skill_root"):
            print("ERROR: 必须通过 main(skill_root=...) 或 state.skill_root 提供 skill 根目录", file=sys.stderr)
            return 2
        skill_root_abs = os.path.abspath(state["skill_root"])

    datadir = os.path.abspath(state.get("datadir") or os.path.dirname(state_path))
    spec = build_spec_from_plan(
        entry, state, variant=cfg["variant"], idx=idx, type_labels=cfg["type_labels"]
    )
    result = _process_task(spec, cfg["variant"], skill_root_abs)
    _emit_and_persist(result, datadir)
    return 0
