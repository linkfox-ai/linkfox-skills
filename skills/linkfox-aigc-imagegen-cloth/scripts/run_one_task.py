#!/usr/bin/env python3
"""服饰套图单任务驱动器（cloth variant 薄壳）。

接受 ``--state <collection-state.json> --index <i>``（1-based），从 plan 阶段落盘的
state + image-plan.json 在内存组装第 i 个任务，按任务 type 跑通 textgen + imagegen 全链路：
  - textgen 改写支线（SCENE / SELLING_POINT / *_APLUS）
  - 占位符直出支线（MODEL_IMAGE / SIZE 阶段2）
  - SIZE 两阶段（阶段1 textgen 前置分析 → 阶段2 占位符出图）
  - 静态直出支线（WHITE_BG，从 references/types/white-bg.md 提取）

stdout 输出一行 ``Saved full response: ["/abs/img.png"]``（成功）或失败 JSON 路径，
同时落盘 ``<datadir>/task-result-<id>.json`` 片段供 summary 阶段汇总。

由 agent 在 plan 确认后，并发 N 次调用本脚本（每个任务 1 次 Bash，--index 1..N）。
完整交付协议见 ``references/runtime/03-deliver.md``。
"""

import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, SCRIPT_DIR)  # 本地 collection_pipeline 包，不再外引 _shared

from collection_pipeline.single_task import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main(variant="cloth", skill_root=SKILL_ROOT))
