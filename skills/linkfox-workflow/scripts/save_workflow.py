#!/usr/bin/env python3
"""linkfox-workflow · linkfox-workflow agentflow v2 JSON → workspace 落盘。

读入调用方按 SKILL.md 产出的 workflow JSON 文件,做骨架校验并落到会话 workspace:
  - 只校验顶层 4 个字段:`description` (str) / `usecases` (list[str]) /
    `nodes` (list[dict]) / `edges` (list[dict])
  - 节点内部合法性由 SKILL.md 的 10 项检查负责,脚本不复刻
  - 新流程落到 <root>/<YYYY-MM-DD>/<session>/data/<slug>-<ts_us>.json
  - 修改已有流程一律用 --workflow-id 原地覆盖,路径和文件名保持不变:
    linkfox-workflow 系统的 flowId 才是 workflow 的唯一身份,文件名(= sourceKey)只是它的载体
  - **--workflow-id 带"服务端原文"门禁**:未先跑 fetch_workflow.py 拿回服务端 flowData,
    或拿回来的那份本地文件已被改动过,一律拒绝落盘(exit 64)。基线只能来自服务端 ——
    拿旧的本地副本当基线会把用户在画布上调过的 position、在 UI 上补填的 credential
    整份冲掉。落盘成功后清掉凭据,逼下一轮重新 fetch。
  - stdout: {"path", "bytes", "nodes", "edges", "mode"} + 一行 "Saved full response: <path> (<bytes> bytes)"
    (与 linkfox-listing-agent 系列 skill 对齐,便于下游 grep line.startswith("Saved full response:"))

CLI:
  python scripts/save_workflow.py \
    --content-file <path>            # 必填。JSON 片段文件
    [--slug <english-slug>]          # 可选。文件名前缀,必须以 `linkfox-workflow`
                                     #   开头(裸前缀,或 `linkfox-workflow-<后缀>`);
                                     #   不传时用默认值 `linkfox-workflow`。
                                     #   只在首次创建新流程时用,与 --workflow-id 互斥。
    [--workflow-id <flowId>]         # 可选。修改已有流程的唯一方式:按 workflowId 从索引
                                     #   反查本地文件并原地覆盖。前置条件是该本地文件必须是
                                     #   `fetch_workflow.py --workflow-id <同一个 id>` 刚落下的
                                     #   原封服务端副本(见上面的门禁)。
    [--allow-trigger-change]         # 可选。只配合 --workflow-id。开始节点(BusinessStart)的
                                     #   inputs / credential / id 默认与基线比对、不一致拒绝
                                     #   落盘(exit 65);用户本轮明确要求换触发时才带它放行。

    [--table-later]                  # 可选。流程里要选多维表的槽位(记录触发 / 读表 / 写表)
                                     #   tableId 还空着时默认拒绝落盘(exit 65),先用智能表格
                                     #   skill 列出用户的表、问用户选哪张;只有用户本轮明确说
                                     #   "表以后自己在界面上选"时才带它放行。
    [--secrets-from-user]            # 可选。password 字段(飞书 / 钉钉机器人地址、加签密钥)
                                     #   默认只能是空,或 refine 时与 fetch 基线一致;不符拒绝
                                     #   落盘(exit 65)。只有用户本轮亲手给了这些值时才带它放行。
    [--dry-run]                      # 可选。只校验不落盘(validate 意图用)
    [--restore-from <snapshotPath>]  # 可选。回滚到 fetch 留下的服务端快照(配 --workflow-id)

退出码:0 成功;64 CLI 用法错 / 门禁未通过;1 文件缺失/读失败;3 片段为空;
       4 写盘失败;65 JSON 非法 / 顶层骨架不合规。
"""

from __future__ import annotations

import json
import os
import re
import sys
import tempfile
import time


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# 同目录复制的 linkfox_paths.py(禁止跨目录 import _shared);把 scripts/ 加进 sys.path
sys.path.insert(0, SCRIPT_DIR)
from linkfox_paths import resolve_data_path  # type: ignore  # noqa: E402
from workflow_identity import (  # type: ignore  # noqa: E402
    begin_save,
    file_sha256,
    finish_save,
    is_pristine_server_copy,
    lookup_by_flow_id as lookup_flow_binding,
    mark_edited as mark_binding_edited,
    snapshot_belongs_to,
)
from workflow_spec import (  # type: ignore  # noqa: E402
    DEPRECATED_START_NAME,
    NODE_SPECS,
    NON_EXEC_NAMES,
    REQUIRED_START_NAME,
    START_NAMES,
    TERMINAL_NAMES,
    normalize as normalize_spec,
    SECRETS_FROM_USER_FLAG,
    TABLE_LATER_FLAG,
    inherit_from_baseline,
    secret_value_changes,
    start_trigger_changes,
    unselected_table_slots,
    validate as validate_spec,
)


_SLUG_ALLOWED_RE = re.compile(r"^linkfox-workflow(-[a-zA-Z0-9-]+)?$")
_SLUG_DEFAULT = "linkfox-workflow"
_GENERATED_FILENAME_RE = re.compile(
    r"^linkfox-workflow(?:-[a-zA-Z0-9-]+)?-[0-9]{10,}\.json$"
)
_FLOWID_RE = re.compile(r"[A-Za-z0-9_-]{6,64}")
# 节点 id 去掉 `<data.name>` 前缀后剩下的部分:必须是 `_` + 纯数字。
# 生成时约定顺序号(`_0`),画布新增的节点是随机数(`_415972`),两者都放行。
#
# **只放数字、不放字母**:`workflow_spec._NODE_REF_RE` 认的 `{{ <nodeId>.output... }}`
# 里 nodeId 也是 `[A-Za-z][A-Za-z0-9_]*_\d+`。这里放宽到字母的话,`_a1` 这类 id 能落盘,
# 但它的所有变量引用会被那条正则整体跳过 —— 锚名当字段、裸 `.output`、引用不存在的节点
# 全部静默放行,而运行时不报错也不替换。两处必须同宽。
_NODE_ID_RE = re.compile(r"_\d+")
_OUTER_FENCE_RE = re.compile(
    r"^\s*```(?:json)?\s*\n([\s\S]*?)\n```\s*$", re.IGNORECASE
)

# 节点 data.name → 预期输出锚点 name 列表,直接从 workflow_spec.NODE_SPECS 派生。
# 空列表 = 该节点没有输出锚点(Loop / DirectReply / StickyNote)。
# 缺失 = 未知节点(workflow_spec 已按 error 拦下),这里仅在 edge 侧兜底。
_EXPECTED_OUTPUT_ANCHORS: dict[str, list[str]] = {
    name: list(spec.anchors) for name, spec in NODE_SPECS.items()
}

# outputAnchors 是纯样板字段,normalize() 能按 data.name 完整代填。报错时必须把这条修法
# 说出来:否则 agent 会照着 "应为 X" 逐字段手改,id 和 name 两头来回试错 —— 会话
# 11b2bb9f 里就为一个 FillForm 锚点连续改了两轮(先 id 对 name 错,改完又反过来)。
_ANCHOR_FIX_HINT = (
    ";最省事的修法是**把整个 data.outputAnchors 字段删掉**,"
    "由 save_workflow.py 按 data.name 代填(不要逐字段手改)"
)

USAGE_TEXT = (
    "Usage:\n"
    "  save_workflow.py --content-file <path>\n"
    "      [--slug <english-slug> | --workflow-id <flowId>]\n"
    "\n"
    "  --content-file : agentflow v2 JSON 片段文件\n"
    "  --slug         : 文件名前缀,必须以 `linkfox-workflow` 开头。\n"
    "                   合法:`linkfox-workflow` 或 `linkfox-workflow-<后缀>`,\n"
    "                   后缀仅允许 [a-zA-Z0-9-]。\n"
    "                   不传时使用默认值 `linkfox-workflow`。\n"
    "                   只在首次创建新流程时用,与 --workflow-id 互斥。\n"
    "  --workflow-id  : 已在 linkfox-workflow 系统上的 flowId;从 workflow-index.json 反查本地文件\n"
    "                   并原地覆盖。修改已有 workflow 的唯一方式,不必记住路径。\n"
    "                   仅接受 linkfox 会话 data 目录内由本脚本生成的 JSON,且该文件必须是\n"
    "                   `fetch_workflow.py --workflow-id <同一个 id>` 刚落下的原封服务端副本。\n"
    "                   开始节点(BusinessStart)的触发配置被锁定:与基线不一致时拒绝落盘。\n"
    "  --allow-trigger-change : 仅当用户本轮明确要求换触发方式/改触发条件时才带,\n"
    "                   放行开始节点锁定;stdout 会回显 triggerChanges。\n"
    "  --table-later  : 仅当用户明确说\"表以后自己在界面上选\"时才带,放行 tableId 为空的\n"
    "                   选表槽位;stdout 的 tableLater 列出这些槽位,回复里要点名。\n"
    "  --secrets-from-user : 仅当用户本轮在对话里亲手给了机器人地址 / 加签密钥时才带,\n"
    "                   放行与基线不一致的 password 字段;不能拿别的流程或记忆里的值顶上。\n"
    "  --dry-run      : 只做补齐 + 全部校验,不写文件、不动 fetch 凭据与上传门禁。\n"
    "                   给 validate 用;generate / refine 直接正式保存,不要先 dry-run 一遍。\n"
    "  --restore-from : 回滚。配合 --workflow-id,内容取自 fetch_workflow.py 的 snapshotPath\n"
    "                   (必须是同一 workflowId 的快照);与 --content-file 互斥。仍需先 fetch,\n"
    "                   stdout 的 restoreOverwrites 列出会被改回去的节点。\n"
)


def _die(msg: str, code: int = 1) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def _parse_cli() -> dict:
    args = sys.argv[1:]

    # 阻挡 stdin / argv 内联 JSON 之类的坏姿势(shell 转义 / argv 长度容易踩坑)
    if len(args) == 1 and (args[0] == "-" or args[0].lstrip().startswith(("{", "["))):
        print(
            "ERROR: 不接受 stdin / argv 内联 JSON。请用 --content-file 传路径。\n",
            file=sys.stderr,
        )
        print(USAGE_TEXT, file=sys.stderr)
        sys.exit(64)

    parsed: dict = {
        "content_file": None,
        "slug": None,
        "workflow_id": None,
        "allow_trigger_change": False,
        "table_later": False,
        "secrets_from_user": False,
        "dry_run": False,
        "restore_from": None,
    }
    i = 0
    while i < len(args):
        a = args[i]
        if a in ("-h", "--help"):
            print(USAGE_TEXT)
            sys.exit(0)
        elif a == "--content-file":
            if i + 1 >= len(args):
                _die("--content-file 需要一个路径参数", 64)
            parsed["content_file"] = args[i + 1]
            i += 2
        elif a == "--slug":
            if i + 1 >= len(args):
                _die("--slug 需要一个字符串参数", 64)
            parsed["slug"] = args[i + 1]
            i += 2
        elif a == "--workflow-id":
            if i + 1 >= len(args):
                _die("--workflow-id 需要一个字符串参数", 64)
            parsed["workflow_id"] = args[i + 1]
            i += 2
        elif a == "--allow-trigger-change":
            parsed["allow_trigger_change"] = True
            i += 1
        elif a == "--table-later":
            parsed["table_later"] = True
            i += 1
        elif a == SECRETS_FROM_USER_FLAG:
            parsed["secrets_from_user"] = True
            i += 1
        elif a == "--dry-run":
            parsed["dry_run"] = True
            i += 1
        elif a == "--restore-from":
            if i + 1 >= len(args):
                _die("--restore-from 需要一个快照路径参数", 64)
            parsed["restore_from"] = args[i + 1]
            i += 2
        elif a == "--existing-file":
            # 这个参数已被移除:按本地路径定位身份会让"本地磁盘"成为事实上的身份来源。
            # 明确报错而不是当成未知参数,否则老调用方会拿到一句它看不懂的 usage。
            _die(
                "--existing-file 已移除。修改已有 workflow 用 "
                "`--workflow-id <flowId>`(拿不到 flowId 就先问用户,或用 "
                "`fetch_workflow.py --workflow-id <id>` 把它拉到本地)",
                64,
            )
        else:
            print(f"ERROR: 未识别的参数:{a}\n", file=sys.stderr)
            print(USAGE_TEXT, file=sys.stderr)
            sys.exit(64)

    if parsed["restore_from"] is not None:
        if parsed["content_file"]:
            _die("--restore-from 与 --content-file 互斥;恢复时内容只来自快照", 64)
        if not parsed["workflow_id"]:
            _die("--restore-from 必须配合 --workflow-id(恢复的是哪个 workflow)", 64)
        if parsed["dry_run"]:
            _die("--restore-from 不支持 --dry-run;快照本身就是服务端原文", 64)
        parsed["content_file"] = parsed["restore_from"]
    if not parsed["content_file"]:
        print("ERROR: --content-file 必填。\n", file=sys.stderr)
        print(USAGE_TEXT, file=sys.stderr)
        sys.exit(64)
    if parsed["slug"] is not None and not _SLUG_ALLOWED_RE.match(parsed["slug"]):
        _die(
            "--slug 必须以 `linkfox-workflow` 开头(合法:`linkfox-workflow` 或 "
            "`linkfox-workflow-<后缀>`,后缀仅允许 [a-zA-Z0-9-];"
            f"正则 ^linkfox-workflow(-[a-zA-Z0-9-]+)?$),当前值:{parsed['slug']!r}",
            64,
        )
    if parsed["slug"] is not None and parsed["workflow_id"] is not None:
        _die("--slug 与 --workflow-id 互斥;新流程用 --slug,修改已有流程用 --workflow-id", 64)
    if parsed["workflow_id"] is not None and not _FLOWID_RE.fullmatch(parsed["workflow_id"].strip()):
        _die(f"--workflow-id 格式非法:{parsed['workflow_id']!r}", 64)

    return parsed


def _read_content(path: str) -> str:
    if not os.path.isfile(path):
        _die(f"--content-file 指向的文件不存在:{path}", 1)
    try:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
    except OSError as e:
        _die(f"读 --content-file 失败:{e}", 1)
    # 兜底:片段偶尔被 ```json ... ``` 代码围栏包一层,剥掉
    m = _OUTER_FENCE_RE.match(text)
    if m:
        text = m.group(1)
    text = text.strip()
    if not text:
        _die("--content-file 内容为空。", 3)
    return text


def _validate_skeleton(data: object) -> dict:
    """只查顶层 4 字段 + 类型。节点级校验归 _validate_nodes_and_edges。"""
    if not isinstance(data, dict):
        _die("顶层必须是对象(dict),当前是 " + type(data).__name__, 65)
    missing = [
        k for k in ("description", "usecases", "nodes", "edges") if k not in data
    ]
    if missing:
        _die(f"顶层缺字段:{missing};需要 description/usecases/nodes/edges", 65)
    extra = [k for k in data if k not in ("description", "usecases", "nodes", "edges")]
    if extra:
        _die(
            f"顶层多余字段:{extra};agentflow v2 顶层只允许 "
            "description/usecases/nodes/edges",
            65,
        )
    if not isinstance(data["description"], str):
        _die("description 必须是字符串", 65)
    if not (
        isinstance(data["usecases"], list)
        and all(isinstance(x, str) for x in data["usecases"])
    ):
        _die("usecases 必须是字符串数组", 65)
    if not (
        isinstance(data["nodes"], list)
        and all(isinstance(x, dict) for x in data["nodes"])
    ):
        _die("nodes 必须是对象数组", 65)
    if not (
        isinstance(data["edges"], list)
        and all(isinstance(x, dict) for x in data["edges"])
    ):
        _die("edges 必须是对象数组", 65)
    if not data["nodes"]:
        _die("nodes 为空;至少要有一个 BusinessStart 开始节点", 65)
    return data  # type: ignore[return-value]


def _validate_nodes_and_edges(data: dict) -> list[str]:
    """核心结构校验:三位一体 id / 锚点形状 / edge↔锚点绑定 / 度约束。

    linkfox-workflow 系统保存时会按 `outputAnchors[].id` 重建 edge 绑定,锚点缺 id 或
    命名与 edge.sourceHandle 对不上 → 所有指向该锚点的 edge 被静默丢弃,
    画布上就只剩孤立节点。这里全部当 error 拦在落盘前。

    深度契约校验(节点身份字段、变量引用、Condition operation、Iteration 父子、
    edge 元数据)委托给 `workflow_spec.validate`;它的 error 与本函数的 error 合并后
    一起决定是否拒绝落盘,warning 由调用方打印,不阻塞。

    返回 warning 列表。
    """
    errors: list[str] = []
    nodes = data["nodes"]
    edges = data["edges"]

    # 每个 flow 必须且只能有一个 BusinessStart 作为开始节点。
    # LinkFox 分支已用 BusinessStart 全面替换原生 Start,后者被视为过时节点。
    # 名称常量集中在 workflow_spec,避免两处各写一份而漂移。
    _REQUIRED_START_NAME = REQUIRED_START_NAME
    _DEPRECATED_START_NAME = DEPRECATED_START_NAME
    _START_NODE_NAMES = START_NAMES

    # ---- 节点级 ---------------------------------------------------------
    seen_ids: dict[str, int] = {}
    node_by_id: dict[str, dict] = {}
    start_node_names_seen: list[str] = []

    for idx, node in enumerate(nodes):
        top_id = node.get("id")
        node_data = node.get("data") if isinstance(node.get("data"), dict) else None
        if not isinstance(top_id, str) or not top_id:
            errors.append(f"nodes[{idx}].id 必须是非空字符串")
            continue
        if node_data is None:
            errors.append(f"nodes[{idx}]({top_id}) 缺少 data 对象")
            continue

        data_id = node_data.get("id")
        data_name = node_data.get("name")
        data_type = node_data.get("type")

        if top_id in seen_ids:
            errors.append(f"nodes[{idx}].id 重复:{top_id}")
        seen_ids[top_id] = idx
        node_by_id[top_id] = node

        if data_id != top_id:
            errors.append(
                f"nodes[{idx}]({top_id}) data.id={data_id!r} 与顶层 id 不一致"
            )

        if not isinstance(data_name, str) or not data_name:
            errors.append(f"nodes[{idx}]({top_id}) data.name 必须是非空字符串")
            continue

        # 三位一体:顶层 id 必须是 `<data.name>_<数字>`。
        #
        # 校验前缀与"后缀是数字",但**不要求后缀是顺序号**。生成新节点时约定用顺序号
        # (`_0` / `_1`,见 flow-structure.md),而**画布上新增的节点后缀是随机数**
        # (前端形如 `fillFormAgentflow_415972`)。曾经这里强制"后缀 = 该 data.name
        # 出现的顺序号",导致任何在 linkfox-workflow 界面里建过节点的 flow 都能 fetch、
        # 一 save 就被拒 —— 节点级 refine 第一步就死。顺序号对运行时没有影响:
        # `sourceHandle` 是 `<nodeId>-output-<anchorName>`,anchor 名由 data.name
        # 决定,与后缀数值无关。真正必须成立的是"前缀等于 data.name"(便于人眼核对
        # 节点类型)、"后缀是数字"(与 `workflow_spec._NODE_REF_RE` 同宽,见该常量
        # 上方注释)与 id 唯一性(上面已查)。
        if not _NODE_ID_RE.fullmatch(top_id[len(data_name):]) or not top_id.startswith(
            data_name
        ):
            errors.append(
                f"nodes[{idx}] id={top_id!r} 与命名约定不一致,应为 "
                f"{data_name!r} + '_' + 数字(如 {data_name}_0,或画布生成的 "
                f"{data_name}_415972);新建节点用 <data.name>_<现有最大 index + 1>,"
                "基线里已有的 id 原样保留"
            )

        if data_name in _START_NODE_NAMES:
            start_node_names_seen.append(data_name)

        # ---- outputAnchors 形状 ----------------------------------------
        anchors = node_data.get("outputAnchors")
        expected_names = _EXPECTED_OUTPUT_ANCHORS.get(data_name)
        if anchors is None or not isinstance(anchors, list):
            errors.append(
                f"nodes[{idx}]({top_id}) data.outputAnchors 必须是数组"
            )
        elif expected_names is not None:
            if not expected_names:
                # Loop / DirectReply / StickyNote:允许空,允许缺
                if anchors:
                    errors.append(
                        f"nodes[{idx}]({top_id}) {data_name} 不应有 outputAnchors,"
                        f"当前有 {len(anchors)} 个"
                    )
            else:
                actual_names = []
                for aidx, anchor in enumerate(anchors):
                    if not isinstance(anchor, dict):
                        errors.append(
                            f"nodes[{idx}]({top_id}) outputAnchors[{aidx}] 必须是对象"
                        )
                        actual_names.append(None)
                        continue
                    missing_fields = [
                        k for k in ("id", "name", "label", "description")
                        if k not in anchor
                    ]
                    if missing_fields:
                        errors.append(
                            f"nodes[{idx}]({top_id}) outputAnchors[{aidx}] "
                            f"缺字段 {missing_fields};必须含 id/name/label/description"
                            f"{_ANCHOR_FIX_HINT}"
                        )
                    a_id = anchor.get("id")
                    a_name = anchor.get("name")
                    if isinstance(a_name, str) and isinstance(a_id, str):
                        want = f"{top_id}-output-{a_name}"
                        if a_id != want:
                            errors.append(
                                f"nodes[{idx}]({top_id}) outputAnchors[{aidx}].id="
                                f"{a_id!r},应为 {want!r}"
                                f"(id 恒为 <节点id>-output-<name>,name 才是锚名)"
                                f"{_ANCHOR_FIX_HINT}"
                            )
                    actual_names.append(a_name if isinstance(a_name, str) else None)

                # 锚名集合必须严格匹配预期(顺序不敏感,数量必须一致)
                if sorted(n for n in actual_names if n is not None) != sorted(expected_names):
                    errors.append(
                        f"nodes[{idx}]({top_id}) {data_name} outputAnchors 锚名集合="
                        f"{actual_names},应为 {expected_names}"
                        f"{_ANCHOR_FIX_HINT}"
                    )

    if _DEPRECATED_START_NAME in start_node_names_seen:
        errors.append(
            f"检测到原生 Start 节点(data.name={_DEPRECATED_START_NAME});"
            f"LinkFox flow 必须使用 BusinessStart(data.name={_REQUIRED_START_NAME}) "
            "作为唯一开始节点,请替换。"
        )
    business_start_count = start_node_names_seen.count(_REQUIRED_START_NAME)
    if business_start_count == 0:
        errors.append(
            "缺少开始节点;每个 flow 必须且只能有一个 BusinessStart "
            f"(data.name={_REQUIRED_START_NAME})"
        )
    elif business_start_count > 1:
        errors.append(
            f"存在 {business_start_count} 个 BusinessStart 节点;每个 flow 只允许一个"
        )

    # ---- edge 级 -------------------------------------------------------
    # 预建 source_id -> 该节点所有锚点 id 的集合
    anchor_ids_by_node: dict[str, set[str]] = {}
    for nid, node in node_by_id.items():
        node_data = node.get("data") or {}
        anchors = node_data.get("outputAnchors") or []
        ids = set()
        if isinstance(anchors, list):
            for a in anchors:
                if isinstance(a, dict) and isinstance(a.get("id"), str):
                    ids.add(a["id"])
        anchor_ids_by_node[nid] = ids

    outgoing: dict[str, int] = {}
    incoming: dict[str, int] = {}

    for eidx, edge in enumerate(edges):
        source = edge.get("source")
        target = edge.get("target")
        source_handle = edge.get("sourceHandle")
        target_handle = edge.get("targetHandle")

        if not isinstance(source, str) or source not in node_by_id:
            errors.append(f"edges[{eidx}].source={source!r} 未在 nodes 中找到")
            continue
        if not isinstance(target, str) or target not in node_by_id:
            errors.append(f"edges[{eidx}].target={target!r} 未在 nodes 中找到")
            continue
        if not isinstance(source_handle, str) or not source_handle:
            errors.append(f"edges[{eidx}].sourceHandle 必须是非空字符串")
            continue

        # 核心:sourceHandle 必须命中 source 节点的 outputAnchors[].id
        anchors = anchor_ids_by_node.get(source, set())
        if anchors and source_handle not in anchors:
            errors.append(
                f"edges[{eidx}].sourceHandle={source_handle!r} 未命中节点 {source} "
                f"的 outputAnchors[].id={sorted(anchors)};linkfox-workflow 系统保存时会静默丢弃该 edge"
            )
        elif not anchors:
            errors.append(
                f"edges[{eidx}] 指向节点 {source},但该节点没有可用的输出锚点"
            )

        if target_handle != target:
            errors.append(
                f"edges[{eidx}].targetHandle={target_handle!r} 应等于 target={target!r}"
            )

        outgoing[source] = outgoing.get(source, 0) + 1
        incoming[target] = incoming.get(target, 0) + 1

    # ---- 度约束 --------------------------------------------------------
    _TERMINAL_NAMES = TERMINAL_NAMES
    _NON_EXEC_NAMES = NON_EXEC_NAMES
    connectivity_relevant = [
        (nid, node)
        for nid, node in node_by_id.items()
        if ((node.get("data") or {}).get("name") or "") not in _NON_EXEC_NAMES
    ]

    for nid, node in node_by_id.items():
        name = ((node.get("data") or {}).get("name") or "")
        if name in _START_NODE_NAMES and incoming.get(nid, 0) > 0:
            errors.append(f"开始节点 {nid}({name}) 不允许有入边")
        if name in _TERMINAL_NAMES and outgoing.get(nid, 0) > 0:
            errors.append(f"{name} 节点 {nid} 不允许有出边")

    # ---- 连通性:第一次生成时最常见的坑就是 edges 为空/节点变孤岛 -----
    if len(connectivity_relevant) > 1:
        if not edges:
            errors.append(
                f"flow 有 {len(connectivity_relevant)} 个执行节点但 edges 为空;"
                "每个非 StickyNote 节点必须至少参与一条 edge,否则画布上是散落的孤岛"
            )
        # 孤立节点:既不作为 source 也不作为 target 出现
        connected: set[str] = set()
        for e in edges:
            if isinstance(e, dict):
                if isinstance(e.get("source"), str):
                    connected.add(e["source"])
                if isinstance(e.get("target"), str):
                    connected.add(e["target"])
        for nid, node in connectivity_relevant:
            if nid not in connected:
                name = (node.get("data") or {}).get("name") or ""
                errors.append(
                    f"节点 {nid}({name}) 未参与任何 edge,画布上会显示为孤立节点"
                )

        # BusinessStart 必须至少有一条出边,否则 flow 无法启动下游
        for nid, node in connectivity_relevant:
            name = (node.get("data") or {}).get("name") or ""
            if name == "businessStartAgentflow" and outgoing.get(nid, 0) == 0:
                errors.append(
                    f"BusinessStart 节点 {nid} 没有出边;flow 无法启动下游节点"
                )

        # 末端节点的判定。
        #
        # 曾经这里要求"任何非 Loop/DirectReply 的节点都必须有出边",但那是错的:
        # agentflow v2 允许 flow 停在最后一个动作节点上(Agent 的回答、SendNotification
        # 发完通知、WriteFile 写完表就是 flow 的终点),linkfox-workflow 系统会把最后一个节点的输出作为
        # 结果返回。按旧规则,`BusinessStart → DataReader → SendNotification` 这种完全正常的
        # 业务流会被拒绝落盘。
        #
        # 真正的 bug 只有一种:**分支节点**(Condition / ConditionAgent / HumanInput)一条
        # 出边都没有 —— 加了分支却没有任何分支去向,该节点毫无意义且必然是漏写。
        _BRANCH_NAMES = {
            "conditionAgentflow",
            "conditionAgentAgentflow",
            "humanInputAgentflow",
        }
        for nid, node in connectivity_relevant:
            name = (node.get("data") or {}).get("name") or ""
            if name not in _BRANCH_NAMES:
                continue
            if incoming.get(nid, 0) > 0 and outgoing.get(nid, 0) == 0:
                errors.append(
                    f"分支节点 {nid}({name}) 一条出边都没有;分支必须至少接一条下游路径,"
                    "否则执行链会在此断路"
                )

    # 深度契约校验。放在最后,这样"id/锚点/连通性"这类基础问题先报,信息更聚焦。
    spec_errors, warnings = validate_spec(data)
    errors.extend(spec_errors)

    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        for w in warnings:
            print(f"WARN: {w}", file=sys.stderr)
        print(
            f"ERROR: 共 {len(errors)} 项节点/边校验失败,拒绝落盘。"
            "修正 workflow.fragment.json 后重跑;详见 references/flow-structure.md 的"
            "『Anchor 形状规范』与 references/lifecycle-actions.md 的 validate 章节。",
            file=sys.stderr,
        )
        sys.exit(65)
    return warnings


def _changed_node_ids(before: dict, after: dict) -> list[str]:
    """两份 flow 之间内容不同、新增或删除的节点 id(忽略 position 等画布坐标)。"""

    def index(flow: dict) -> dict[str, str]:
        out: dict[str, str] = {}
        for n in flow.get("nodes") or []:
            if isinstance(n, dict) and isinstance(n.get("id"), str):
                out[n["id"]] = json.dumps(n.get("data"), ensure_ascii=False, sort_keys=True)
        return out

    a, b = index(before), index(after)
    return sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))


def _resolve_existing_file(path: str) -> tuple[str, dict]:
    """只接受 LinkFox 会话 data 目录里、由本脚本生成过的 workflow 文件。

    路径来自 `--workflow-id` 的索引反查而不是调用方随手给的,但仍要逐条验证 ——
    索引是缓存,可能指向一个已被清掉的、或别人手写的 JSON。
    """
    target = os.path.abspath(os.path.expanduser(path))
    if not os.path.isfile(target):
        _die(f"workflowId 绑定的本地文件不存在:{target}(重新 fetch 一次即可重建)", 1)
    basename = os.path.basename(target)
    parent = os.path.dirname(target)
    session_dir = os.path.dirname(parent)
    if os.path.basename(parent) != "data":
        _die(f"workflowId 绑定的文件不在 linkfox 会话的 data 目录:{target}", 64)
    if not _GENERATED_FILENAME_RE.fullmatch(basename):
        _die(
            "workflowId 绑定的文件名不是本脚本生成的 workflow 文件:" + basename,
            64,
        )
    if not os.path.isfile(os.path.join(session_dir, "_meta.json")):
        _die("workflowId 绑定的文件所在目录缺少会话 _meta.json,拒绝覆盖", 64)

    # Refuse to overwrite an unrelated JSON file that only happens to match the name.
    try:
        with open(target, "r", encoding="utf-8") as f:
            current = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        _die(f"读取已有 workflow 失败:{e}", 65)
    # 返回解析后的内容:门禁已保证它是原封服务端副本,开始节点锁定拿它当基线比对。
    return target, _validate_skeleton(current)


def _write_atomic(path: str, content: str) -> None:
    """Replace one exact workflow file without exposing a partially written JSON."""
    tmp_path = ""
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=os.path.dirname(path),
            prefix=".workflow-update-",
            suffix=".json.tmp",
            delete=False,
        ) as f:
            tmp_path = f.name
            f.write(content)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, path)
    except OSError as e:
        if tmp_path:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
        _die(f"写 workflow 失败 {path}: {e}", 4)


def main() -> None:
    # 行缓冲:run_in_background 时 stdout 被重定向到文件,块缓冲会让唯一那行结果 JSON 滞留
    try:
        sys.stdout.reconfigure(line_buffering=True)  # type: ignore[attr-defined]
        sys.stderr.reconfigure(line_buffering=True)  # type: ignore[attr-defined]
    except AttributeError:
        pass

    # 保存→上传门禁:先挂 pendingSave,只有落盘成功才摘掉。之后任何一处 _die / sys.exit
    # 都会让它留着,upload_workflow.py 据此拒绝上传磁盘上的旧版本。
    # --dry-run 不写盘,也就不碰门禁:既不挂 pendingSave,也不动 fetch 凭据。
    # 在解析参数之前判断,保证"参数写错"同样会挂上 pendingSave(那也是一次失败的保存)。
    dry_run = "--dry-run" in sys.argv[1:]
    if not dry_run:
        begin_save()
    args = _parse_cli()
    if args["restore_from"] is not None and not snapshot_belongs_to(
        args["workflow_id"].strip(), args["restore_from"]
    ):
        # 先于读内容 / 校验:拿别的流程的文件覆盖本流程,是身份问题,不是格式问题。
        _die(
            f"--restore-from 指向的不是 workflowId {args['workflow_id'].strip()} 的快照:"
            f"{args['restore_from']};快照只能来自 fetch_workflow.py 的 snapshotPath",
            64,
        )
    text = _read_content(args["content_file"])

    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        _die(f"JSON 解析失败:{e.msg} (line {e.lineno} col {e.colno})", 65)

    data = _validate_skeleton(data)
    # refine:没动的节点只写 id + data.name,position / inputs / credential / 手写的 inputParams
    # 从 fetch 基线按 id 拷回。必须在 normalize 之前 —— 否则缺的 position 会先被自动排版
    # 占掉,用户在画布上拖好的布局就丢了。基线只认门禁放行的服务端原文;不放行时这里
    # 什么都不做,下面的门禁会给出正式报错。--restore-from 的快照本身就是完整原文,不补。
    baseline_filled: list[str] = []
    early_id = (args["workflow_id"] or "").strip()
    if early_id and args["restore_from"] is None:
        early_binding = lookup_flow_binding(early_id)
        if early_binding and is_pristine_server_copy(early_id)[0]:
            try:
                with open(early_binding["path"], "r", encoding="utf-8") as f:
                    baseline_filled = inherit_from_baseline(data, json.load(f))
            except (OSError, json.JSONDecodeError):
                baseline_filled = []  # 读不了就不补;_resolve_existing_file 会正式报错
    # 先补齐纯样板字段(type / version / color / baseClasses / 锚点 / edge id 等),
    # 再校验。这些值完全由 data.name 推导,让模型手抄只是在制造出错机会。
    # 已存在但与 spec 不符的值不会被改写,交给校验报错。
    normalized = normalize_spec(data)
    warnings = _validate_nodes_and_edges(data)
    pending_tables = unselected_table_slots(data)

    if dry_run:
        # 只校验:error 已在上面按 65 退出;走到这里就是校验通过。不写文件、不改索引。
        # validate 看的常是用户贴来的 JSON,表没选不算结构错误,如实列出即可。
        warnings = warnings + [
            f"{s['nodeId']}({s['role']})还没选好:{s['missing']}" for s in pending_tables
        ]
        report: dict = {
            "mode": "dry-run",
            "valid": True,
            "nodes": len(data["nodes"]),
            "edges": len(data["edges"]),
        }
        if normalized:
            report["normalized"] = normalized
        if pending_tables:
            report["unselectedTables"] = pending_tables
        if warnings:
            report["warnings"] = warnings
        print(json.dumps(report, ensure_ascii=False, indent=2))
        for w in warnings:
            print(f"WARN: {w}", file=sys.stderr)
        print("Dry run: 校验通过,未写入任何文件")
        sys.exit(0)

    workflow_id = (args["workflow_id"] or "").strip()
    bound_workflow_id = ""
    trigger_changes: list[str] = []
    restore_overwrites: list[str] | None = None
    if args["allow_trigger_change"] and not workflow_id:
        _die("--allow-trigger-change 只能和 --workflow-id 一起用(首次创建没有基线可比)", 64)

    if workflow_id:
        # workflowId 是唯一身份;索引里必须已有绑定(fetch 或上一次 upload 写入)。
        binding = lookup_flow_binding(workflow_id)
        if not binding:
            _die(
                f"workflowId {workflow_id} 尚未绑定本地文件;先跑 "
                "`fetch_workflow.py --workflow-id <id>` 把该 workflow 从服务端拉到本地",
                64,
            )
        # 门禁:改动基线只能是刚从服务端 fetch 下来、还没被动过的那份文件。
        # 少了这一道,agent 可以拿上一轮遗留的本地副本当基线直接改,用户画布上的
        # position、UI 里补填的 credential 会被整份冲掉 —— 这种"省一次 fetch"的
        # 错误在文档里写过规则也拦不住,所以放在脚本里。
        pristine, why = is_pristine_server_copy(workflow_id)
        if not pristine:
            _die(
                f"workflowId {workflow_id} 的本地副本不能作为改动基线:{why}。"
                f"基线必须来自服务端,先跑 "
                f"`python scripts/fetch_workflow.py --workflow-id {workflow_id}` "
                "拉回最新 flowData,在这份文件上改,再重跑本脚本",
                64,
            )
        out_path, baseline = _resolve_existing_file(binding["path"])
        if args["restore_from"] is not None:
            # 回滚:内容是该 workflow 之前某次 fetch 的服务端原文。必须属于同一个 workflowId,
            # 否则就是拿别的流程覆盖本流程。仍要求先 fetch(上面的门禁),这样能告诉调用方
            # 恢复会冲掉哪些"快照之后的改动"(含用户在界面上做的)。
            restore_overwrites = _changed_node_ids(baseline, data)
            # 恢复的目的就是回到快照里的配置,包括被临时改掉的触发方式,所以自动放行。
            args["allow_trigger_change"] = True
        # 开始节点锁定(缺陷 #7114401338):用户在 UI 上配好的触发方式(尤其是从多维表
        # 新建时的记录触发)被 AI 生成时顺手改成了手动启动。触发配置是用户的,不是
        # agent 推断出来的,所以和基线不一致一律拒绝 —— 只有用户明确要求换触发时才
        # 带 --allow-trigger-change 放行。
        trigger_changes = start_trigger_changes(baseline, data)
        if trigger_changes and not args["allow_trigger_change"]:
            for c in trigger_changes:
                print(f"ERROR: 开始节点触发配置被改动:{c}", file=sys.stderr)
            print(
                "ERROR: 开始节点(BusinessStart)的触发配置是用户在 UI 上配好的,refine 时必须"
                "从基线原样保留(inputs / credential / 节点 id 一字不动),拒绝落盘。"
                "把开始节点整块从 fetch 基线拷回来再重跑;只有用户本轮明确要求换触发方式"
                "或改触发条件时,才带 --allow-trigger-change",
                file=sys.stderr,
            )
            sys.exit(65)
        if not trigger_changes:
            # 开始节点与基线逐字一致 → 上面那些"写死了运行时对象 / credential 只填一处"
            # 的 warning 指向的都是用户在 UI 上绑好的真实值。照着它"留空"恰好就是本缺陷
            # 的另一种形态(清掉 tableId,订阅断掉),所以 refine 时对开始节点不再报。
            start_ids = {
                n.get("id")
                for n in data["nodes"]
                if isinstance(n.get("data"), dict)
                and n["data"].get("name") == REQUIRED_START_NAME
            }
            warnings = [
                w for w in warnings
                if not (
                    any(w.startswith(f"{sid} ") for sid in start_ids)
                    and ("写死了运行时对象" in w or "FLOWISE_CREDENTIAL_ID" in w)
                )
            ]
        # 基线里本来就空着、这一轮也没碰的选表槽位不拦:那是用户之前选择"以后再配"的
        # 遗留,拦它会让一次无关的 refine(比如只改某个通知文案)也过不去。只提示一句。
        baseline_blank = {
            (s["nodeId"], s["role"]) for s in unselected_table_slots(baseline)
        }
        inherited = [s for s in pending_tables if (s["nodeId"], s["role"]) in baseline_blank]
        pending_tables = [s for s in pending_tables if (s["nodeId"], s["role"]) not in baseline_blank]
        warnings = warnings + [
            f"{s['nodeId']}({s['role']})在基线里就没选表,本轮未改动;可以顺便问用户要不要现在选"
            for s in inherited
        ]
        bound_workflow_id = workflow_id
        mode = "updated"
    else:
        ts = time.time()
        slug = (args["slug"] or _SLUG_DEFAULT).strip()
        out_path = os.path.abspath(resolve_data_path(slug, ts, "json"))
        mode = "created"

    # 缺陷 #7130761097:新流程 B 的飞书机器人地址偷偷沿用了同会话里 A 的。password 字段
    # 只能来自用户 —— refine 时随 fetch 基线带回(用户在界面上填的),或用户本轮亲口给的。
    # 回滚的内容本身是服务端快照,不在此列。
    secret_changes: list[str] = []
    if args["restore_from"] is None:
        secret_changes = secret_value_changes(baseline if workflow_id else None, data)
    if secret_changes and not args["secrets_from_user"]:
        for c in secret_changes:
            print(f"ERROR: 机器人地址 / 密钥字段不是来自用户:{c}", file=sys.stderr)
        print(
            "ERROR: password 字段(飞书 / 钉钉机器人地址、加签密钥)只能留空,或在 refine 时与 "
            "fetch 基线保持一致,拒绝落盘。不要从会话里别的流程、上一轮生成或记忆里沿用这些值 —— "
            "那会把通知发进别的流程的群。把这些字段改回空串(refine 时从基线拷回原值)重跑,"
            "回复里提醒用户在界面上填;只有用户本轮在对话里亲手给了这个流程的地址 / 密钥时,"
            f"才带 {SECRETS_FROM_USER_FLAG}",
            file=sys.stderr,
        )
        sys.exit(65)

    if pending_tables and not args["table_later"]:
        # 缺陷 #7130931254:生成时把表留空、让用户自己去界面上配,是在偷懒 —— 用户的表
        # 用智能表格 skill 一查就有。这里机械拦住,逼 agent 先问"用哪张表"。
        for s in pending_tables:
            print(f"ERROR: {s['nodeId']}「{s['label']}」的{s['role']}还没选好:{s['missing']}", file=sys.stderr)
        print(
            "ERROR: 流程里有要选多维表的节点还没选表,拒绝落盘。先跑 "
            "`linkfox-smart-table` 的 `listMyTables`(必要时加 `listSharedTables`)"
            "列出用户的多维表格和数据表,把候选列给用户、问清每个槽位用哪张表,"
            "再把选中的 notebookId(nbk… / 散表 __loose__)和 tableId(tbl…)写进节点重跑;"
            f"只有用户明确说表以后自己在界面上选时,才带 {TABLE_LATER_FLAG}",
            file=sys.stderr,
        )
        sys.exit(65)

    # 规范化输出:4 空格缩进,与 response-contract.md 一致
    final = json.dumps(data, ensure_ascii=False, indent=4)

    _write_atomic(out_path, final)
    finish_save(out_path, file_sha256(out_path))

    if bound_workflow_id:
        # 落盘成功 → 这份文件已经不是服务端原文了。清掉 fetch 留下的凭据,下一次
        # `--workflow-id` 落盘必须先重新 fetch —— "每轮 refine 都从服务端取基线"
        # 由此变成机械约束,而不是一句谁都可以绕过的文档规则。
        mark_binding_edited(bound_workflow_id)

    summary = {
        "path": out_path,
        "bytes": len(final.encode("utf-8")),
        "nodes": len(data["nodes"]),
        "edges": len(data["edges"]),
        "mode": mode,
    }
    if bound_workflow_id:
        summary["workflowId"] = bound_workflow_id
    if pending_tables:
        # 带 --table-later 放行的槽位:回复里要告诉用户哪些节点还得去界面上选表。
        summary["tableLater"] = pending_tables
    if restore_overwrites is not None:
        summary["restoredFrom"] = os.path.abspath(args["restore_from"])
        # 快照之后被改动(或新增 / 删除)的节点:恢复会把它们一并改回去,回复里要点名。
        summary["restoreOverwrites"] = restore_overwrites
    if secret_changes:
        # 带 --secrets-from-user 放行的字段(只有节点 id + 字段名,不含值)。
        summary["secretsFromUser"] = secret_changes
    if trigger_changes:
        # 放行了也要回显:回复里必须告诉用户触发配置变了,以及 UI 上要重新保存一次订阅。
        summary["triggerChanges"] = trigger_changes
    # 把"影响画布观感"的补齐从几十条样板字段里拎出来:position 被自动生成意味着
    # 用户在 linkfox-workflow 系统上手工摆的位置没被带过来(refine 时尤其要警觉),混在
    # normalized 里根本看不见,上一次就因此让用户误判"改并行没生效"。
    #
    # **只认精确的 `.position`,不能用 `".position" in n` 子串匹配** —— 那会把
    # `.positionAbsolute` 一起算进去。基线带了真实 `position`、只是缺
    # `positionAbsolute`(fetch 回来的 flowData 很常见)时,子串匹配会报出一条假的
    # layoutNotes;而 SKILL.md 告诉 agent"refine 时出现 layoutNotes 基本等于漏了
    # fetch,先 fetch 重来" —— 一条假信号会让它把已经正确的一轮判成返工。
    # `positionAbsolute` 是纯派生值(直接拷 position),归到样板字段里。
    layout_notes = [n for n in normalized if n.endswith(".position")]
    boilerplate = [n for n in normalized if not n.endswith(".position")]
    if layout_notes:
        summary["layoutNotes"] = layout_notes
    if baseline_filled:
        # 只报条数:逐条列出会把 stdout 撑大,模型也不需要据此做任何事。
        summary["inheritedFromBaseline"] = len(baseline_filled)
    if boilerplate:
        # 让调用方知道脚本替它补了哪些样板字段,下次可以直接省略。
        summary["normalized"] = boilerplate
    if warnings:
        # warning 不阻塞落盘,但要让调用方看见并在回复里如实转述。
        summary["warnings"] = warnings
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if layout_notes:
        print(
            f"WARN: 有 {len(layout_notes)} 个节点的 position 是脚本按拓扑自动生成的;"
            "若这是 refine,说明基线 JSON 没带用户在 linkfox-workflow 系统上手工调整过的坐标 —— "
            "请在回复里提醒用户画布布局可能需要重新拖动。",
            file=sys.stderr,
        )
    for w in warnings:
        print(f"WARN: {w}", file=sys.stderr)
    print(f"Saved full response: {out_path} ({summary['bytes']} bytes)")


if __name__ == "__main__":
    main()
