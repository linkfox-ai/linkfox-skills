#!/usr/bin/env python3
"""智能表格-解除工作流关联 - LinkFox Skill
调用 /smartTable/unregisterWorkflow 接口。

把一条流从多维表下面摘掉。**不删除工作流本身** —— 流还在工作流侧。

⚠️ 不可逆（但可以用 register-workflow 重新登记，触发表要重新设）。
⚠️ 幂等：unregistered 和 not_found 都表示「多维表这边已经没有这条流了」，
   收到 200 就不要重试。但 flowId 抄错也会得到 not_found，别当成「已清干净」。

顺序固定：① 解除关联（本脚本）→ ② 到工作流侧删流。反过来会在侧栏留死节点。

Usage:
  python smart_table.py unregisterWorkflow '{"flowId":"your-flow-id"}' --yes
  python smart_table.py unregisterWorkflow '<JSON>' --yes --inline
"""

import json
import os
import sys
import time
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

API_PATH = "/smartTable/unregisterWorkflow"
SLUG = "linkfox-smart-table-unregister-workflow"

# 响应 <= 该字节数时落盘后额外全量打印到 stdout；超过则只打摘要
SMALL_THRESHOLD = 8000

# linkfox_paths.py 由 scaffold 从 linkfoxagent-v2/_shared 复制到本目录 scripts/，原样不改。
from linkfox_paths import get_api_base, resolve_data_path


def get_api_url():
    return get_api_base() + API_PATH


def get_api_key():
    key = os.environ.get("LINKFOX_AGENT_API_KEY") or os.environ.get("LINKFOXAGENT_API_KEY")
    if not key:
        print(
            "API Key not configured. Please complete authorization first:\n"
            "1. Visit https://agent.linkfox.com -> 设置 -> API KEY to obtain your Key\n"
            "2. Set the environment variable: export LINKFOX_AGENT_API_KEY=your-key-here",
            file=sys.stderr,
        )
        sys.exit(1)
    return key


def call_api(params):
    req = Request(
        get_api_url(),
        data=json.dumps(params, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": get_api_key(),  # 值即 key 本身，不加任何前缀
            "Content-Type": "application/json; charset=utf-8",
            "User-Agent": "LinkFox-Skill/2.0",
            "SESSION_ID": os.environ.get("SESSION_ID", ""),
            "MESSAGE_ID": os.environ.get("MESSAGE_ID", ""),
            "MODE_ID": os.environ.get("MODE_ID", ""),
            "APP_NAME": os.environ.get("APP_NAME", ""),
        },
        method="POST",
    )
    try:
        with urlopen(req, timeout=120) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as e:
        body = e.read().decode("utf-8") if e.fp else ""
        try:
            return json.loads(body) if body else {"errcode": e.code, "errmsg": f"HTTP {e.code}: {e.reason}"}
        except Exception:
            return {"errcode": e.code, "errmsg": f"HTTP {e.code}: {e.reason}", "details": body}
    except URLError as e:
        return {"errcode": 0, "errmsg": f"Connection failed: {e.reason}"}


def summarize(result):
    """打印紧凑摘要。这个接口的响应很小，正常走不到这里。"""
    if not isinstance(result, dict):
        print(f"Response type: {type(result).__name__}")
        print(json.dumps(result, ensure_ascii=False)[:500])
        return
    print(f"Top-level keys: {list(result.keys())}")
    for k in ("errcode", "errmsg", "status"):
        if k in result and isinstance(result[k], (int, float, bool, str)):
            print(f"  {k}: {result[k]}")


def _resolve_output_path(ts):
    """落到 <cwd>/linkfox/<date>/<session>/data/<slug>-<ts>.json。"""
    return resolve_data_path(SLUG, ts)


def _validate(params):
    if not isinstance(params, dict):
        return "参数必须是 JSON 对象"
    if not params.get("flowId"):
        # flowId 的格式由工作流侧定，所以只查非空，不查前缀
        return "缺少 flowId（工作流侧那条流的 id）"
    return None


def main():
    argv = sys.argv[1:]
    inline = "--inline" in argv
    confirmed = "--yes" in argv
    argv = [a for a in argv if a not in ("--inline", "--yes")]

    if not argv:
        print(
            f"Usage: smart_table.py unregisterWorkflow '{{\"flowId\":\"your-flow-id\"}}' --yes [--inline]",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        params = json.loads(argv[0])
    except json.JSONDecodeError as e:
        print(f"Invalid parameter format: {e}", file=sys.stderr)
        sys.exit(1)

    problem = _validate(params)
    if problem:
        print(problem, file=sys.stderr)
        sys.exit(1)

    if not confirmed:
        print(
            f"拒绝执行：解除关联不可逆。flowId={params['flowId']} 将从多维表下面摘掉，"
            "之后它从侧栏消失、不再被记录变化触发（**流本身不会被删除**，仍在工作流侧）。\n"
            "先用 smart_table.py listWorkflows 读出来给用户确认是哪一条，再加 --yes 重跑。\n"
            "提示：只想让它暂时不触发的话，用 smart_table.py updateWorkflowTriggerTable "
            "传 tableId=null 解绑就够了，关联还在、以后好恢复。",
            file=sys.stderr,
        )
        sys.exit(2)

    result = call_api(params)

    serialized = json.dumps(result, ensure_ascii=False, indent=2)
    ts = int(time.time())
    out_path = _resolve_output_path(ts)
    try:
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(serialized)
        print(f"Saved full response: {out_path} ({len(serialized)} bytes)")
    except OSError as e:
        print(f"Failed to save to {out_path}: {e}", file=sys.stderr)

    if isinstance(result, dict) and result.get("errcode") != 200:
        print(
            f"Business error: errcode={result.get('errcode')} errmsg={result.get('errmsg')}",
            file=sys.stderr,
        )
    elif isinstance(result, dict):
        status = result.get("status")
        # 两种 status 都是成功（幂等），但要说清各自含义，别让调用方重试或误判。
        if status == "not_found":
            print(
                "status=not_found：多维表这边**本来就没有**这条关联（重试过、或压根没登记过）。\n"
                "目标已达成，不要重试。但注意 flowId 抄错也会得到这个结果 —— "
                "如果你确信这条关联应该存在，先用 smart_table.py listWorkflows 核对 id。"
            )
        elif status == "unregistered":
            print(
                "已解除：这条流不再挂在多维表下、不再被记录变化触发。\n"
                "⚠️ **工作流本身没有被删除**，它还在工作流侧。要彻底删掉请到工作流侧做第 2 步。"
            )

    if inline or len(serialized.encode("utf-8")) <= SMALL_THRESHOLD:
        print(serialized)
    else:
        summarize(result)


if __name__ == "__main__":
    main()
