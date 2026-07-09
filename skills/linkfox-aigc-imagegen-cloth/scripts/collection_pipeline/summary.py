"""summary phase（cloth / product 共用）

按 state.``task_specs`` 顺序读取 single_task 落盘的 ``task-result-<id>.json``
片段，stdout 输出：

  1. 末尾 markdown 成功明细（含每张成功图的 ``![label](abs_path)`` 内联引用 +
     失败项），由 agent 原样转发；
  2. 1 行 status JSON（含 ``asset_manifest_file`` 等），agent 内部解析、不展示。

仅 product variant 额外合并写出 ``collection-asset-manifest.json``。
完整交付协议见 ``references/runtime/03-deliver.md``。
"""

from __future__ import annotations

import json
import os
import time
from typing import Any

from .config import get_variant
from .utils import (
    emit_completion_summary,
    merge_assets_from_results,
    read_task_results,
)


def _load_state(state_file: str) -> dict:
    state_path = os.path.abspath(state_file)
    if not os.path.isfile(state_path):
        raise FileNotFoundError(f"state 文件不存在: {state_path}")
    with open(state_path, encoding="utf-8") as f:
        return json.load(f)


def _spec_to_task(spec_meta: dict, result: dict) -> dict:
    """把 dispatch 写入 state 的 spec 元数据 + 任务结果片段合并为 ``format_completion_summary`` 期望的 task 字典。

    summary 只用 task 中的 ``id`` / ``type`` / ``label`` / ``point`` 字段渲染明细，
    其余字段（layout / ratio 等）保留以便日后扩展。
    """
    task: dict[str, Any] = {
        "id": spec_meta.get("id") or result.get("id"),
        "type": spec_meta.get("type") or result.get("type"),
        "label": spec_meta.get("label") or result.get("label"),
    }
    for key in ("point", "desc", "layout", "ratio", "image_desc"):
        val = result.get(key)
        if val:
            task[key] = val
    return task


def _write_asset_manifest(
    *,
    datadir: str,
    state: dict,
    results: list[dict],
    out_path: str,
) -> str:
    """汇总各任务结果片段中的 assets[] 字段，写出 collection-asset-manifest.json。

    与 product 旧 run_collection.py._write_asset_manifest 保持字段兼容：
    schema / source / assets / summary（main + aplus 计数）。
    """
    assets = merge_assets_from_results(results)
    payload = {
        "schema": "linkfox-listing-asset-manifest/v1",
        "source": {
            "kind": f"linkfox-aigc-imagegen-{state.get('variant') or 'product'}",
            "datadir": datadir,
            "provider": state.get("provider"),
            "resolution": state.get("resolution"),
        },
        "assets": assets,
        "summary": {
            "total": len(assets),
            "main": sum(1 for a in assets if a.get("slot") == "main"),
            "aplus": sum(1 for a in assets if a.get("slot") == "aplus"),
        },
    }
    out = os.path.abspath(out_path)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return out


def run_summary_phase(state_file: str) -> dict[str, Any]:
    """summary phase 主流程，stdout 直接打印末尾 markdown + status JSON。

    返回值用于上层 runner 兜底（如校验目录、日志记录），不再额外 print。
    """
    state = _load_state(state_file)
    variant = (state.get("variant") or "cloth").strip().lower()
    cfg = get_variant(variant)

    datadir = os.path.abspath(state.get("datadir") or os.path.dirname(os.path.abspath(state_file)))
    spec_metas = state.get("task_specs") or []
    if not isinstance(spec_metas, list) or not spec_metas:
        raise ValueError("state.task_specs 为空——summary 阶段须由 plan 阶段先写入 task_specs 列表")

    expected_ids = [str(s.get("id") or "") for s in spec_metas]
    results = read_task_results(datadir, expected_ids)
    tasks = [_spec_to_task(s, r) for s, r in zip(spec_metas, results)]

    emit_completion_summary(results=results, tasks=tasks, type_labels=cfg["type_labels"])

    asset_manifest_path: str | None = None
    if cfg.get("write_asset_manifest"):
        out = state.get("asset_manifest_file") or os.path.join(datadir, "collection-asset-manifest.json")
        asset_manifest_path = _write_asset_manifest(
            datadir=datadir,
            state=state,
            results=results,
            out_path=out,
        )

    success_count = sum(1 for r in results if r.get("status") in ("success", "dry-run"))
    status_payload = {
        "status": "completed",
        "variant": variant,
        "datadir": datadir,
        "total": len(results),
        "success": success_count,
        "failed": len(results) - success_count,
        "summary_emitted_at": int(time.time() * 1000),
    }
    if asset_manifest_path:
        status_payload["asset_manifest_file"] = asset_manifest_path

    print(json.dumps(status_payload, ensure_ascii=False), flush=True)
    return status_payload
