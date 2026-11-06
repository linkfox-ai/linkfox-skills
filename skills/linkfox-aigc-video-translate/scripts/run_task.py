#!/usr/bin/env python3
"""上传源素材、创建一次翻译任务、轮询查询并下载成品。"""
import argparse
import json
import math
import os
from pathlib import Path
import sys
import time
import uuid
import call_api
from material_runtime import api_error, check_output_directory, download_results, invoke, prepare_media

CREATE_SCRIPT = "video_translation_async.py"
VIDEO = True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("parameters", nargs="?", help="JSON 参数，或使用 '-' 从标准输入读取 JSON")
    parser.add_argument("--params-file", type=Path)
    parser.add_argument("--task-id", help="恢复已接受任务的查询，不重新上传或创建")
    parser.add_argument("--member-id")
    parser.add_argument("--timeout", type=float, default=1200 if VIDEO else 600)
    parser.add_argument("--poll-interval", type=float, default=10)
    parser.add_argument("--initial-delay", type=float, default=None)
    args = parser.parse_args()
    delays = [args.timeout, args.poll_interval]
    if args.initial_delay is not None:
        delays.append(args.initial_delay)
    if (not all(math.isfinite(value) for value in delays)
            or args.timeout <= 0 or args.poll_interval < 0
            or args.initial_delay is not None and args.initial_delay < 0):
        parser.error("超时必须为有限正数，延迟必须为有限非负数")
    if args.parameters and args.params_file:
        parser.error("JSON 位置参数与 --params-file 只能选择一个")
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
        parser.error("恢复仅接收 --task-id 和 --member-id，不接收创建参数")
    call_api.get_api_key()
    if args.task_id:
        task_id = args.task_id
        artifact = None
    else:
        unknown = set(params) - {"requestId", "chatId", "messageId", "title", "params"}
        if unknown:
            parser.error("创建参数顶层只允许 requestId/chatId/messageId/title/params")
        business_params = params.get("params")
        if not isinstance(business_params, dict) or not business_params:
            parser.error("params 必须为非空业务参数对象")
        prepared = dict(params)
        prepared["params"] = prepare_media(business_params, scripts)
        created, artifact = invoke(scripts / CREATE_SCRIPT, prepared)
        if api_error(created) or not created.get("taskId"):
            print("Saved full response: " + str(artifact))
            raise RuntimeError("创建失败；认证或用量错误见 references/onboarding.md")
        task_id = str(created["taskId"])
    print("任务已接受：taskId=" + task_id, file=sys.stderr)
    query = {"taskId": task_id}
    member_id = args.member_id
    if member_id:
        query["memberId"] = member_id
    deadline = time.monotonic() + args.timeout
    initial = args.initial_delay if args.initial_delay is not None else (0 if args.task_id else 120 if VIDEO else 10)
    time.sleep(min(initial, args.timeout))
    interval = max(10, args.poll_interval) if VIDEO else args.poll_interval
    while time.monotonic() < deadline:
        result, artifact = invoke(scripts / "query_task.py", query, no_cache=True)
        if api_error(result):
            print("Saved full response: " + str(artifact))
            raise RuntimeError("查询失败；保留 taskId，认证或用量错误按 references/onboarding.md 处理")
        status = result.get("status")
        if status == "SUCCESS":
            paths, manifest = download_results(result, scripts)
            print("最终费用：" + json.dumps({"costToken": result.get("costToken"), "costCredit": result.get("costCredit")}, ensure_ascii=False), file=sys.stderr)
            if not paths:
                print("Saved full response: " + str(artifact))
            if any(item.get("downloadError") for item in manifest["items"]):
                print("部分下载失败；请保留此查询响应：" + str(artifact), file=sys.stderr)
            return 0
        if status == "FAILED":
            print("Saved full response: " + str(artifact))
            print("任务失败，不自动重新创建", file=sys.stderr)
            return 1
        if status != "PROCESSING":
            print("Saved full response: " + str(artifact))
            raise RuntimeError("任务状态未知；停止轮询，不创建新任务")
        print("任务处理中：taskId=" + task_id, file=sys.stderr)
        time.sleep(min(interval, max(0, deadline - time.monotonic())))
        if not VIDEO and args.poll_interval >= 5:
            interval = max(5, interval - 1)
    if artifact:
        print("Saved full response: " + str(artifact))
    print("任务仍在等待：taskId=" + task_id + "；请通过 --task-id 恢复，不重新创建", file=sys.stderr)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, RuntimeError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
