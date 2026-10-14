"""linkfox-workflow · workflowId ↔ 本地 workflow 文件的持久绑定表。

**为什么需要这张表**

上传/反查链路上,`sourceKey` 就是本地文件的 basename,而 basename 里带微秒时间戳
(`linkfox-workflow-<slug>-<ts_us>.json`)。也就是说"文件名"是一次性的:
`fetch_workflow.py` 每次调用都会生成新文件名,`save_workflow.py` 不传
`--existing-file` 也会生成新文件名。一旦文件名变了,`sourceKey` 就变了,
workflow-studio 侧 `(group_id, member_id, source_key, flow_type)` 唯一键必然 miss,
上传就退化成 POST 新建 —— 这正是"二次对话编辑产生了新的工作流"这个 bug。

所以真正的唯一身份是 **linkfox-workflow 系统的 flowId**,不是文件名。本模块把
`flowId → 本地文件路径` 的绑定落到 `<linkfox_root>/workflow-index.json`,
让 fetch / save / upload 三个脚本都能**确定性地**找回同一份本地文件与同一个 flowId,
不再依赖调用方(LLM)记住上一轮的路径。

索引是跨会话的(放在 linkfox root,而不是某个 session 目录下),因此换天、换
SESSION_ID 之后继续编辑同一个 workflow 仍然命中同一份文件、同一个 flowId。

索引结构(version 1):

    {
      "version": 1,
      "flows": {
        "<workflowId>": {
          "path": "/abs/.../data/linkfox-workflow-x-1730000000000000.json",
          "name": "订单跟单流程",
          "flowType": "AGENTFLOW",
          "updatedAt": "2026-08-24T10:00:00+0800",
          "serverHash": "<fetch 落下这份文件时内容的 sha256>"
        }
      }
    }

`serverHash` 是**本地文件仍是"原封服务端副本"的唯一凭据**:`fetch_workflow.py` 每次
GET 到服务端 flowData 并落盘后写它,`save_workflow.py --workflow-id` 落盘前校验它
(内容被改过、或压根没 fetch 过,一律拒绝落盘),`mark_edited()` 在落盘成功后清掉它
—— 于是"每轮 refine 必须先从服务端取基线"这条规则由脚本机械保证,不靠文档自觉。
缺这个字段的老绑定一律按"不是新鲜的服务端副本"处理(让 agent 补一次 fetch 即自愈)。

索引是**缓存而非真相源**,两个方向都可能变 stale,处理方式不同:

- **linkfox-workflow 系统侧 flow 被删** → `upload_workflow.py` 校验到 404 后调 `forget()` 主动清掉条目。
- **本地文件被删**(会话 workspace 清理) → `lookup_by_flow_id` 直接当"没绑定过"返回 None,
  不抛错。

索引损坏时当空表处理,写失败只丢缓存 —— 绝不因为索引问题让上传失败。
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile
import time
from typing import Any, Optional


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)
from linkfox_paths import session_root  # type: ignore  # noqa: E402


INDEX_BASENAME = "workflow-index.json"
INDEX_VERSION = 1


def _linkfox_root() -> str:
    """linkfox 根目录 = <root>/<YYYY-MM-DD>/<session> 往上两级。

    复用 `linkfox_paths.session_root()` 而不是它的私有 `_linkfox_root`,
    避免改动被所有 skill 共享的 linkfox_paths.py。
    """
    return os.path.dirname(os.path.dirname(session_root()))


def index_path() -> str:
    return os.path.join(_linkfox_root(), INDEX_BASENAME)


def load_index() -> dict[str, Any]:
    """读索引;缺失/损坏/结构不对都返回空表,绝不抛异常。"""
    try:
        with open(index_path(), encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        return {"version": INDEX_VERSION, "flows": {}}
    if not isinstance(data, dict) or not isinstance(data.get("flows"), dict):
        return {"version": INDEX_VERSION, "flows": {}}
    data["version"] = INDEX_VERSION
    return data


def _save_index(data: dict[str, Any]) -> None:
    """原子写;写失败只是丢缓存,不让调用方失败。"""
    target = index_path()
    tmp_path = ""
    try:
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=os.path.dirname(target),
            prefix=".workflow-index-",
            suffix=".json.tmp",
            delete=False,
        ) as f:
            tmp_path = f.name
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, target)
    except OSError:
        if tmp_path:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass


def lookup_by_flow_id(flow_id: str) -> Optional[dict[str, Any]]:
    """按 workflowId 找绑定条目;返回 None 表示没绑定过或本地文件已不在。

    会话 workspace 可能被清掉(落在系统临时目录下、或按天目录被删),此时索引里的 path
    指向一个不存在的文件。这种条目当"没绑定过"处理,让调用方自然走新建路径,而不是抛一个
    "文件不存在"把上层卡住 —— 索引是缓存,不是真相源。
    """
    key = (flow_id or "").strip()
    if not key:
        return None
    entry = load_index()["flows"].get(key)
    if not isinstance(entry, dict):
        return None
    path = entry.get("path")
    if not isinstance(path, str) or not path or not os.path.isfile(path):
        return None
    return entry


def lookup_by_path(path: str) -> tuple[str, dict[str, Any]] | tuple[None, None]:
    """按本地文件路径反查 (workflowId, 条目);未绑定返回 (None, None)。

    调用方手里就攥着这个文件,所以这里不再重复判存在性;只做路径等值比对。
    """
    target = os.path.abspath(os.path.expanduser(path or ""))
    if not target:
        return None, None
    for flow_id, entry in load_index()["flows"].items():
        if not isinstance(entry, dict):
            continue
        recorded = entry.get("path")
        if isinstance(recorded, str) and os.path.abspath(recorded) == target:
            return flow_id, entry
    return None, None


def content_sha256(text: str) -> str:
    """一段文本按 utf-8 编码后的 sha256;写入与校验两端都走这里,保证同源。"""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def file_sha256(path: str) -> str:
    """文件字节的 sha256;读不到返回空串(空串永远匹配不上任何 serverHash)。"""
    try:
        with open(path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except OSError:
        return ""


def is_pristine_server_copy(flow_id: str) -> tuple[bool, str]:
    """本地绑定文件是否仍是 fetch 下来后原封未动的那份服务端副本。

    返回 (是否原封, 说明)。说明只在 False 时有意义,直接给调用方贴进报错。
    """
    binding = lookup_by_flow_id(flow_id)
    if binding is None:
        return False, "尚未绑定本地文件"
    recorded = binding.get("serverHash")
    if not isinstance(recorded, str) or not recorded:
        return False, "绑定里没有 serverHash(这份本地副本不是 fetch 下来的,或已被改动过)"
    actual = file_sha256(binding["path"])
    if not actual:
        return False, "本地绑定文件读不到"
    if actual != recorded:
        return False, "本地绑定文件的内容与 fetch 下来的那份不一致(已被改动)"
    return True, ""


def register(
    flow_id: str,
    path: str,
    name: str = "",
    flow_type: str = "",
    server_hash: str | None = None,
) -> None:
    """写入/更新绑定。

    同一个本地文件只允许绑定一个 flowId,因此写入前把指向同一路径的其它条目清掉
    (例如某个 flow 被删后重建,复用了同一份本地 JSON)。

    `server_hash` 只有 `fetch_workflow.py`(拿到服务端 flowData 并落盘)才传;
    其它调用方(upload)传默认值,等于清掉该字段 —— 上传后的本地内容已经是"改过"的,
    不该再被当成服务端原文。
    """
    key = (flow_id or "").strip()
    target = os.path.abspath(os.path.expanduser(path or ""))
    if not key or not target:
        return
    data = load_index()
    flows = data["flows"]
    for other_id in [
        other_id
        for other_id, entry in flows.items()
        if other_id != key
        and isinstance(entry, dict)
        and isinstance(entry.get("path"), str)
        and os.path.abspath(entry["path"]) == target
    ]:
        flows.pop(other_id, None)
    entry = {
        "path": target,
        "name": (name or "").strip(),
        "flowType": (flow_type or "").strip().upper(),
        "updatedAt": time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime()),
    }
    if server_hash:
        entry["serverHash"] = server_hash
    flows[key] = entry
    _save_index(data)


def mark_edited(flow_id: str) -> None:
    """落盘成功后调用:清掉 serverHash,逼下一轮 refine 重新 fetch 拿基线。

    清除而不是更新成新内容的哈希 —— 新内容是本轮自己写的,不是服务端原文,
    拿它当"原封副本"凭据等于把门禁让开了。
    """
    key = (flow_id or "").strip()
    if not key:
        return
    data = load_index()
    entry = data["flows"].get(key)
    if not isinstance(entry, dict) or "serverHash" not in entry:
        return
    entry.pop("serverHash", None)
    _save_index(data)


# ---- 服务端原文快照(回滚用) --------------------------------------------------
#
# "改回上一版"如果靠重新构造 JSON,就是重放而不是恢复 —— 重放错了,恢复到的是一个从未存在
# 过的版本。所以 fetch 每次把拿到的服务端原文另存一份快照,恢复时直接上送快照。
#
# 快照放在 `<linkfox_root>/workflow-snapshots/<workflowId>/`,**不在会话 data 目录、
# 文件名也不以 `linkfox-workflow` 开头**:那是 workflow 文件的命名空间(basename = sourceKey),
# 混进去会被当成另一个 workflow。每个 workflowId 只保留最近 SNAPSHOT_KEEP 份。

SNAPSHOT_DIRNAME = "workflow-snapshots"
SNAPSHOT_KEEP = 5


def _snapshot_dir(flow_id: str) -> str:
    return os.path.join(_linkfox_root(), SNAPSHOT_DIRNAME, flow_id)


def save_snapshot(flow_id: str, content: str) -> str:
    """写一份服务端原文快照,返回路径;写失败返回空串(快照是附加能力,不让 fetch 失败)。"""
    key = (flow_id or "").strip()
    if not key or "/" in key or "\\" in key or key.startswith("."):
        return ""
    folder = _snapshot_dir(key)
    # 文件名按字典序 = 时间序:纳秒时间戳定长补零,同一秒内连续 fetch 也不会乱序。
    path = os.path.join(folder, f"snapshot-{time.time_ns():020d}.json")
    try:
        os.makedirs(folder, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        old = sorted(n for n in os.listdir(folder) if n.startswith("snapshot-"))
        for name in old[:-SNAPSHOT_KEEP]:
            try:
                os.unlink(os.path.join(folder, name))
            except OSError:
                pass
    except OSError:
        return ""
    return path


def list_snapshots(flow_id: str) -> list[str]:
    """该 workflowId 的快照路径,旧 → 新。"""
    folder = _snapshot_dir((flow_id or "").strip())
    try:
        names = sorted(n for n in os.listdir(folder) if n.startswith("snapshot-"))
    except OSError:
        return []
    return [os.path.join(folder, n) for n in names]


def snapshot_belongs_to(flow_id: str, path: str) -> bool:
    """快照路径必须真的落在该 workflowId 的快照目录里 —— 防止拿别的流程的快照覆盖本流程。"""
    folder = os.path.realpath(_snapshot_dir((flow_id or "").strip()))
    target = os.path.realpath(os.path.expanduser(path or ""))
    return os.path.dirname(target) == folder and os.path.isfile(target)


# ---- 保存 → 上传门禁 ---------------------------------------------------------
#
# 复盘(2026-10-08)里出过的真实事故:新片段 `save_workflow.py` 校验失败,agent 却照样
# 拿上一版落盘文件跑了 `upload_workflow.py`,又接着执行 —— 线上跑的是旧版本,回复说的是
# 新版本。"保存失败就停"写在文档里拦不住,所以落到索引里两条机械凭据:
#
# - `pendingSave`:`save_workflow.py` 一开始就写上,只有落盘成功才清掉。保存中途任何一种
#   失败(校验 error / 门禁 / 写盘)都会把它留在原地 —— 此后任何上传都被拒,直到下一次
#   保存成功。
# - `saves[<abs path>]`:保存成功时记下落盘内容的 sha256。上传只接受"内容与最近一次
#   成功保存完全一致"的文件;保存之后再被手改过、或压根没经过保存脚本的文件一律拒绝。
#
# 两者都放在跨会话的索引里:每次脚本调用的自动 session 目录各不相同,放 session 目录
# 下 upload 看不到 save 写的东西。


def begin_save() -> None:
    """保存开始:挂上 pendingSave。写失败只丢门禁(索引写失败本来就静默)。"""
    data = load_index()
    data["pendingSave"] = {
        "startedAt": time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime()),
    }
    _save_index(data)


def finish_save(path: str, sha: str) -> None:
    """保存成功:清掉 pendingSave,记下这份文件的内容哈希。"""
    target = os.path.abspath(os.path.expanduser(path or ""))
    data = load_index()
    data.pop("pendingSave", None)
    saves = data.get("saves")
    if not isinstance(saves, dict):
        saves = {}
    if target and sha:
        saves[target] = sha
    data["saves"] = saves
    _save_index(data)


def check_uploadable(path: str) -> tuple[bool, str]:
    """这份文件能不能上传。返回 (能否, 不能时的原因)。"""
    target = os.path.abspath(os.path.expanduser(path or ""))
    data = load_index()
    if isinstance(data.get("pendingSave"), dict):
        return False, (
            "最近一次 save_workflow.py 没有成功结束(校验报错、门禁拒绝或写盘失败),"
            "磁盘上的文件不是你这一轮想上传的版本"
        )
    saves = data.get("saves")
    recorded = saves.get(target) if isinstance(saves, dict) else None
    if not isinstance(recorded, str) or not recorded:
        return False, "这份文件没有经过 save_workflow.py 落盘(或落盘记录已丢失)"
    if file_sha256(target) != recorded:
        return False, "这份文件在 save_workflow.py 落盘之后又被改动过"
    return True, ""


def forget(flow_id: str) -> None:
    """删掉一个绑定(linkfox-workflow 系统侧 flow 已不存在时由 upload 调用)。"""
    key = (flow_id or "").strip()
    if not key:
        return
    data = load_index()
    if data["flows"].pop(key, None) is not None:
        _save_index(data)
