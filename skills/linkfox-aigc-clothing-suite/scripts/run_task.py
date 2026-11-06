#!/usr/bin/env python3
"""上传源素材、仅创建一次、查询任务并保存媒体。"""
import argparse
import json
import os
from pathlib import Path
import sys
import time
import uuid
from material_runtime import api_error, check_output_directory, download_results, invoke, prepare_media

CREATE_SCRIPT = "wear_collection_async.py"
VIDEO = False


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("parameters", nargs="?", help="JSON 参数，或使用 '-' 从 stdin 读取")
    parser.add_argument("--params-file", type=Path)
    parser.add_argument("--task-id", help="恢复已接受任务的查询，不重复上传或创建")
    parser.add_argument("--member-id")
    parser.add_argument("--timeout", type=float, default=1200 if VIDEO else 600)
    parser.add_argument("--poll-interval", type=float, default=10)
    parser.add_argument("--initial-delay", type=float, default=None)
    args = parser.parse_args()
    if args.timeout <= 0 or args.poll_interval < 0 or args.initial_delay is not None and args.initial_delay < 0:
        parser.error("超时必须为正数，等待间隔不能为负数")
    if args.parameters and args.params_file:
        parser.error("JSON 参数与 --params-file 只能选一种")
    scripts = Path(__file__).resolve().parent
    check_output_directory()
    if not os.environ.get("SESSION_ID"):
        os.environ["SESSION_ID"] = "aigc-" + uuid.uuid4().hex[:12]
    raw = args.params_file.read_text(encoding="utf-8") if args.params_file else args.parameters
    if raw == "-":
        raw = sys.stdin.read()
    params = json.loads(raw) if raw else {}
    if not isinstance(params, dict):
        parser.error("参数必须为 JSON 对象")
    if not args.task_id and not raw:
        parser.error("请提供 JSON 参数、--params-file 或 --task-id")
    if args.task_id and raw:
        parser.error("恢复仅接受 --task-id 和 --member-id，不能混入创建参数")
    if args.task_id:
        task_id = args.task_id
        artifact = None
    else:
        unknown = set(params) - {"requestId", "chatId", "messageId", "title", "params"}
        if unknown:
            parser.error("创建外层仅接受 requestId/chatId/messageId/title/params")
        business_params = params.get("params")
        if not isinstance(business_params, dict) or not business_params:
            parser.error("params 必须为非空业务参数对象")
        prepared = dict(params)
        prepared["params"] = prepare_media(business_params, scripts)
        created, artifact = invoke(scripts / CREATE_SCRIPT, prepared)
        if api_error(created) or not created.get("taskId"):
            print("Saved full response: " + str(artifact))
            raise RuntimeError("创建失败；认证或算力问题按 references/onboarding.md 处理")
        task_id = str(created["taskId"])
    print("Task accepted: taskId=" + task_id, file=sys.stderr)
    query = {"taskId": task_id}
    member_id = args.member_id
    if member_id:
        query["memberId"] = member_id
    deadline = time.monotonic() + args.timeout
    initial = args.initial_delay if args.initial_delay is not None else (0 if args.task_id else 120 if VIDEO else 10)
    time.sleep(min(initial, args.timeout))
    interval = args.poll_interval
    while time.monotonic() < deadline:
        result, artifact = invoke(scripts / "query_task.py", query, no_cache=True)
        if api_error(result):
            print("Saved full response: " + str(artifact))
            raise RuntimeError("查询失败；保留 taskId，认证或算力问题按 references/onboarding.md 处理")
        status = result.get("status")
        if status == "SUCCESS":
            paths, manifest = download_results(result, scripts)
            print("最终费用：" + json.dumps({"costToken": result.get("costToken"), "costCredit": result.get("costCredit")}, ensure_ascii=False), file=sys.stderr)
            if not paths:
                print("Saved full response: " + str(artifact))
            if any(item.get("downloadError") for item in manifest["items"]):
                print("部分下载失败，请保留此查询响应：" + str(artifact), file=sys.stderr)
            return 0
        if status == "FAILED":
            print("Saved full response: " + str(artifact))
            print("任务失败，不自动重新创建", file=sys.stderr)
            return 1
        if status != "PROCESSING":
            print("Saved full response: " + str(artifact))
            raise RuntimeError("任务状态未知，停止轮询，不重新创建任务")
        print("Task processing: taskId=" + task_id, file=sys.stderr)
        time.sleep(min(interval, max(0, deadline - time.monotonic())))
        if not VIDEO and args.poll_interval >= 5:
            interval = max(5, interval - 1)
    if artifact:
        print("Saved full response: " + str(artifact))
    print("Task pending: taskId=" + task_id + "；使用 --task-id 恢复，不重复创建", file=sys.stderr)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, RuntimeError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
