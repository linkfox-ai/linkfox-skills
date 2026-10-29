#!/usr/bin/env python3
"""Upload source media, create once, poll the shared task query, and save media."""
import argparse
import json
import os
from pathlib import Path
import sys
import time
import uuid
from material_runtime import api_error, check_output_directory, download_results, invoke, prepare_media

CREATE_SCRIPT = "multi_image_fusion_async.py"
VIDEO = False


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("parameters", nargs="?", help="JSON parameters, or '-' to read JSON from stdin")
    parser.add_argument("--params-file", type=Path)
    parser.add_argument("--task-id", help="Resume querying an accepted task; never upload or create again")
    parser.add_argument("--member-id")
    parser.add_argument("--timeout", type=float, default=1200 if VIDEO else 600)
    parser.add_argument("--poll-interval", type=float, default=10)
    parser.add_argument("--initial-delay", type=float, default=None)
    args = parser.parse_args()
    if args.timeout <= 0 or args.poll_interval < 0 or args.initial_delay is not None and args.initial_delay < 0:
        parser.error("Timeout must be positive; delays cannot be negative")
    if args.parameters and args.params_file:
        parser.error("Choose JSON parameters or --params-file")
    scripts = Path(__file__).resolve().parent
    check_output_directory()
    if not os.environ.get("SESSION_ID"):
        os.environ["SESSION_ID"] = "aigc-" + uuid.uuid4().hex[:12]
    raw = args.params_file.read_text(encoding="utf-8") if args.params_file else args.parameters
    if raw == "-":
        raw = sys.stdin.read()
    params = json.loads(raw) if raw else {}
    if not isinstance(params, dict):
        parser.error("Parameters must be a JSON object")
    if not args.task_id and not raw:
        parser.error("Supply parameters, --params-file, or --task-id")
    if args.task_id and raw:
        parser.error("Resume accepts --task-id and --member-id, not creation parameters")
    if args.task_id:
        task_id = args.task_id
        artifact = None
    else:
        unknown = set(params) - {"requestId", "chatId", "messageId", "title", "params"}
        if unknown:
            parser.error("Creation accepts only requestId/chatId/messageId/title/params at the top level")
        business_params = params.get("params")
        if not isinstance(business_params, dict) or not business_params:
            parser.error("params must be a nonempty business-parameter object")
        prepared = dict(params)
        prepared["params"] = prepare_media(business_params, scripts)
        created, artifact = invoke(scripts / CREATE_SCRIPT, prepared)
        if api_error(created) or not created.get("taskId"):
            print("Saved full response: " + str(artifact))
            raise RuntimeError("Creation failed; see references/onboarding.md for auth/billing errors")
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
            raise RuntimeError("Query failed; keep taskId and follow references/onboarding.md for auth/billing errors")
        status = result.get("status")
        if status == "SUCCESS":
            paths, manifest = download_results(result, scripts)
            print("Final cost: " + json.dumps({"costToken": result.get("costToken"), "costCredit": result.get("costCredit")}, ensure_ascii=False), file=sys.stderr)
            if not paths:
                print("Saved full response: " + str(artifact))
            if any(item.get("downloadError") for item in manifest["items"]):
                print("Some downloads failed; retain this query response: " + str(artifact), file=sys.stderr)
            return 0
        if status == "FAILED":
            print("Saved full response: " + str(artifact))
            print("Task failed; do not recreate automatically", file=sys.stderr)
            return 1
        if status != "PROCESSING":
            print("Saved full response: " + str(artifact))
            raise RuntimeError("Unknown task status; stop polling without creating a new task")
        print("Task processing: taskId=" + task_id, file=sys.stderr)
        time.sleep(min(interval, max(0, deadline - time.monotonic())))
        if not VIDEO and args.poll_interval >= 5:
            interval = max(5, interval - 1)
    if artifact:
        print("Saved full response: " + str(artifact))
    print("Task pending: taskId=" + task_id + "; resume with --task-id, do not create again", file=sys.stderr)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, RuntimeError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
