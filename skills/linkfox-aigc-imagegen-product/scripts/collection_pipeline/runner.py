#!/usr/bin/env python3
"""套图 pipeline CLI：plan / dispatch / summary 三阶段。

dispatch 在 skill 层用 ``ThreadPoolExecutor`` 并发跑 ``run_one_task.py --index 1..N``。

各阶段 stdout 概要（完整协议见 ``references/runtime/03-deliver.md``）：
  - plan：markdown 表格 + 1 行 status JSON
  - dispatch：1 行 status JSON（``success`` / ``failed`` 计数）；进度走 stderr
  - summary：含 ``![]()`` 内联引用的 markdown 明细 + 1 行 status JSON
"""

from __future__ import annotations

import argparse
import json
import os
import sys

from .plan import run_plan_phase
from .summary import run_summary_phase
from .utils import (
    apply_script_paths,
    print_plan_phase_result,
    resolve_skill_scripts,
)


def _load_job(path: str) -> dict:
    with open(os.path.abspath(path), encoding="utf-8") as f:
        return json.load(f)


def main(argv: list[str] | None = None, *, variant: str, skill_root: str) -> int:
    parser = argparse.ArgumentParser(description="套图 collection pipeline（plan / dispatch / summary）")
    parser.add_argument("--phase", required=True, choices=["plan", "dispatch", "summary"])
    parser.add_argument("--job", help="plan phase：job.json 路径")
    parser.add_argument("--state", help="dispatch / summary phase：collection-state.json 路径")
    args = parser.parse_args(argv)

    scripts = resolve_skill_scripts(skill_root)

    try:
        if args.phase == "plan":
            if not args.job:
                print("ERROR: plan phase 需要 --job", file=sys.stderr)
                return 1
            job = _load_job(args.job)
            apply_script_paths(job, scripts)
            result = run_plan_phase(job, skill_root=skill_root, variant_name=variant)
            datadir = os.path.abspath(
                job.get("datadir") or os.path.dirname(result.get("plan_file") or "")
            )
            print_plan_phase_result(result, datadir=datadir)
        elif args.phase == "dispatch":
            if not args.state:
                print("ERROR: dispatch phase 需要 --state", file=sys.stderr)
                return 1
            import re
            import subprocess
            from concurrent.futures import ThreadPoolExecutor, as_completed

            with open(args.state, encoding="utf-8") as f:
                state = json.load(f)
            total = len(state["task_specs"])
            run_script = state["run_one_task_script"]
            saved_re = re.compile(r"Saved full response:\s*(.+?)\s*$", re.M)

            def run_one(i):
                # capture：子任务 Saved full response 不透传到 dispatch stdout
                proc = subprocess.run(
                    [sys.executable, run_script, "--state", args.state, "--index", str(i)],
                    text=True, capture_output=True,
                )
                if proc.stderr:
                    sys.stderr.write(proc.stderr)
                images = []
                m = saved_re.search(proc.stdout or "")
                if m and m.group(1).startswith("["):  # 成功是 JSON 数组，失败是错误 JSON 路径
                    try:
                        images = json.loads(m.group(1))
                    except json.JSONDecodeError:
                        images = []
                return i, images

            results: dict[int, list] = {}
            with ThreadPoolExecutor(max_workers=total) as pool:
                futures = {pool.submit(run_one, i): i for i in range(1, total + 1)}
                for fut in as_completed(futures):
                    i, images = fut.result()
                    results[i] = images
            success_count = sum(1 for paths in results.values() if paths)
            dispatch_status = {
                "status": "dispatch_complete",
                "total": total,
                "success": success_count,
                "failed": total - success_count,
            }
            print(json.dumps(dispatch_status, ensure_ascii=False), flush=True)
        else:  # summary
            if not args.state:
                print("ERROR: summary phase 需要 --state", file=sys.stderr)
                return 1
            run_summary_phase(args.state)
        return 0
    except Exception as e:  # noqa: BLE001
        print(json.dumps({"status": "error", "error": str(e)}, ensure_ascii=False))
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(
        main(
            variant=os.environ.get("COLLECTION_VARIANT", "cloth"),
            skill_root=os.environ["SKILL_ROOT"],
        )
    )
