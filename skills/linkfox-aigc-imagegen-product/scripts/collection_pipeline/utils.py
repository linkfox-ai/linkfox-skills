"""套图 pipeline 通用工具。"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
from typing import Any

from .config import APLUS_TYPES, DEFAULT_RATIOS, SP_APLUS_TYPES, SP_LAYOUTS, SIZE_LAYOUTS, SIZE_TYPES

TEXTGEN_TIMEOUT = 360
TRANSIENT_RE = re.compile(
    r"(Connection failed|Connection reset|timed?\s?out|timeout|Temporary failure|"
    r"HTTP 5\d\d|URLError|Polling timeout|Max retries|Read timed out)",
    re.I,
)
JSON_BLOCK_RE = re.compile(r"```(?:json)?\s*([\s\S]*?)```", re.I)


def shared_root() -> str:
    return os.path.dirname(os.path.abspath(__file__))


# ===== linkfox_paths 内联块（自包含，无外部依赖，无 oss2）=====
# 替代 `import linkfox_paths`，避免外引 _shared。
# 提供：get_api_base / resolve_data_path / session_root / download_media
#       / encode_nl / decode_nl / decode_nl_in_obj
import json as _lf_json
import os as _lf_os
import secrets as _lf_secrets
import time as _lf_time
import tempfile as _lf_tempfile
from types import SimpleNamespace as _lf_SimpleNamespace

_LF_SESSION_CACHE = {}
NL_PLACEHOLDER = "⏎"


def get_api_base():
    """网关基础地址：env LINKFOX_TOOL_GATEWAY 优先，缺省回退正式地址。"""
    return (_lf_os.environ.get("LINKFOX_TOOL_GATEWAY") or "https://tool-gateway.linkfox.com").rstrip("/")


def _lf_format_iso(ts):
    return _lf_time.strftime("%Y-%m-%dT%H:%M:%S%z", _lf_time.localtime(ts))


def _lf_session_id(ts):
    env = _lf_os.environ.get("SESSION_ID")
    if env:
        return env.strip()
    if "_auto" not in _LF_SESSION_CACHE:
        _LF_SESSION_CACHE["_auto"] = (
            _lf_time.strftime("%H%M%S", _lf_time.localtime(ts)) + "-" + _lf_secrets.token_hex(3)
        )
    return _LF_SESSION_CACHE["_auto"]


def _lf_linkfox_root():
    cached = _LF_SESSION_CACHE.get("_root")
    if cached:
        return cached
    candidates = []
    acpx = (_lf_os.environ.get("ACPX_WORKSPACES") or "").strip()
    if acpx:
        acpx = acpx.split(_lf_os.pathsep)[0].strip()
        if acpx:
            candidates.append(_lf_os.path.join(acpx, "linkfox"))
    candidates.append(_lf_os.path.join(_lf_os.getcwd(), "linkfox"))
    candidates.append(_lf_os.path.join(_lf_os.path.expanduser("~"), "linkfox"))
    candidates.append(_lf_os.path.join(_lf_tempfile.gettempdir(), "linkfox"))
    for root in candidates:
        try:
            _lf_os.makedirs(root, exist_ok=True)
            probe = _lf_os.path.join(root, ".write_probe")
            with open(probe, "w", encoding="utf-8") as f:
                f.write("")
            _lf_os.remove(probe)
        except OSError:
            continue
        root = _lf_os.path.abspath(root)
        _LF_SESSION_CACHE["_root"] = root
        return root
    fallback = _lf_os.path.abspath(candidates[-1])
    _LF_SESSION_CACHE["_root"] = fallback
    return fallback


def _lf_ensure_meta(root, session_dir, date_str, sid, ts):
    meta_path = _lf_os.path.join(session_dir, "_meta.json")
    if _lf_os.path.exists(meta_path):
        return
    meta = {
        "session_id": sid,
        "date": date_str,
        "started_at": _lf_format_iso(ts),
        "skills_called": [],
        "deliverables": [],
        "data_files": [],
        "media_files": [],
    }
    with open(meta_path, "w", encoding="utf-8") as f:
        _lf_json.dump(meta, f, ensure_ascii=False, indent=2)
    try:
        with open(_lf_os.path.join(root, "index.jsonl"), "a", encoding="utf-8") as f:
            f.write(
                _lf_json.dumps(
                    {
                        "session_id": sid,
                        "date": date_str,
                        "path": _lf_os.path.relpath(session_dir, root),
                        "started_at": _lf_format_iso(ts),
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )
    except OSError:
        pass


def _lf_update_meta(session_dir, *, skill, kind, file_rel, ts):
    meta_path = _lf_os.path.join(session_dir, "_meta.json")
    try:
        with open(meta_path, encoding="utf-8") as f:
            meta = _lf_json.load(f)
    except (OSError, _lf_json.JSONDecodeError):
        return
    if skill and skill not in meta.setdefault("skills_called", []):
        meta["skills_called"].append(skill)
    bucket = {"data": "data_files", "deliverable": "deliverables", "media": "media_files"}.get(
        kind, "data_files"
    )
    files = meta.setdefault(bucket, [])
    if file_rel not in files:
        files.append(file_rel)
    meta["last_used_at"] = _lf_format_iso(ts)
    with open(meta_path, "w", encoding="utf-8") as f:
        _lf_json.dump(meta, f, ensure_ascii=False, indent=2)


def _lf_ensure_session(ts):
    date_str = _lf_time.strftime("%Y-%m-%d", _lf_time.localtime(ts))
    sid = _lf_session_id(ts)
    root = _lf_linkfox_root()
    session_dir = _lf_os.path.join(root, date_str, sid)
    _lf_os.makedirs(session_dir, exist_ok=True)
    _lf_ensure_meta(root, session_dir, date_str, sid, ts)
    return root, session_dir


def resolve_data_path(slug, ts, ext="json"):
    """普通 skill 的原始数据落到 <session>/data/<slug>-<ts>.<ext>。"""
    _, session_dir = _lf_ensure_session(ts)
    sub = _lf_os.path.join(session_dir, "data")
    _lf_os.makedirs(sub, exist_ok=True)
    out = _lf_os.path.join(sub, f"{slug}-{int(ts * 1_000_000)}.{ext}")
    _lf_update_meta(session_dir, skill=slug, kind="data", file_rel=_lf_os.path.relpath(out, session_dir), ts=ts)
    return out


def session_root(ts=None):
    """返回当前 session 目录。"""
    if ts is None:
        ts = _lf_time.time()
    _, session_dir = _lf_ensure_session(ts)
    return session_dir


def download_media(url, slug, ts=None, ext=None, timeout=300):
    """下载 URL 到 <session>/media/<slug>-<ts>.<ext>，返回本地路径；失败返回 None。"""
    import sys as _lf_sys
    from urllib.request import urlopen as _lf_urlopen, Request as _lf_Request
    import posixpath as _lf_posixpath

    if not url or not isinstance(url, str):
        return None

    if not url.startswith("http://") and not url.startswith("https://"):
        print(f"[download_media] Unsupported URL scheme: {url[:80]}", file=_lf_sys.stderr)
        return None

    if ts is None:
        ts = _lf_time.time()

    guessed_ext = ext
    if not guessed_ext:
        path_part = url.split("?")[0]
        candidate = _lf_posixpath.splitext(path_part)[1].lstrip(".")
        if candidate and len(candidate) <= 5 and candidate.isalnum():
            guessed_ext = candidate
        else:
            guessed_ext = "bin"

    _, session_dir = _lf_ensure_session(ts)
    media_dir = _lf_os.path.join(session_dir, "media")
    _lf_os.makedirs(media_dir, exist_ok=True)
    tmp_filename = f".tmp-{slug}-{int(ts * 1_000_000)}.download"
    tmp_path = _lf_os.path.join(media_dir, tmp_filename)

    req = _lf_Request(url, headers={"User-Agent": "LinkFox-Skill/2.0"})
    try:
        with _lf_urlopen(req, timeout=timeout) as resp:
            if guessed_ext == "bin":
                ct = resp.headers.get("Content-Type", "")
                if "mp4" in ct:
                    guessed_ext = "mp4"
                elif "webm" in ct:
                    guessed_ext = "webm"
                elif "png" in ct:
                    guessed_ext = "png"
                elif "jpeg" in ct or "jpg" in ct:
                    guessed_ext = "jpg"
                elif "webp" in ct:
                    guessed_ext = "webp"
                elif "gif" in ct:
                    guessed_ext = "gif"
            with open(tmp_path, "wb") as f:
                while True:
                    chunk = resp.read(65536)
                    if not chunk:
                        break
                    f.write(chunk)

        ts_us = int(ts * 1_000_000)
        final_path = _lf_os.path.join(media_dir, f"{slug}-{ts_us}.{guessed_ext}")
        _lf_os.replace(tmp_path, final_path)
        _lf_update_meta(session_dir, skill=slug, kind="media", file_rel=_lf_os.path.relpath(final_path, session_dir), ts=ts)
        return final_path
    except Exception as e:
        print(f"[download_media] Failed to download {url}: {e}", file=_lf_sys.stderr)
        try:
            if _lf_os.path.exists(tmp_path):
                _lf_os.remove(tmp_path)
        except OSError:
            pass
        return None


def encode_nl(text):
    if not isinstance(text, str):
        return text
    text = text.replace("\\r\\n", NL_PLACEHOLDER)
    text = text.replace("\\n", NL_PLACEHOLDER)
    text = text.replace("\\r", NL_PLACEHOLDER)
    text = text.replace("\r\n", NL_PLACEHOLDER)
    text = text.replace("\r", NL_PLACEHOLDER)
    text = text.replace("\n", NL_PLACEHOLDER)
    return text


def decode_nl(text):
    if not isinstance(text, str):
        return text
    return text.replace(NL_PLACEHOLDER, "\n")


def decode_nl_in_obj(obj):
    if isinstance(obj, str):
        return decode_nl(obj)
    if isinstance(obj, list):
        return [decode_nl_in_obj(item) for item in obj]
    if isinstance(obj, dict):
        return {k: decode_nl_in_obj(v) for k, v in obj.items()}
    return obj


def linkfox_paths_module():
    """返回暴露 linkfox_paths 公共 API 的 namespace（内联实现，无外引 _shared）。"""
    return _lf_SimpleNamespace(
        get_api_base=get_api_base,
        resolve_data_path=resolve_data_path,
        session_root=session_root,
        download_media=download_media,
        encode_nl=encode_nl,
        decode_nl=decode_nl,
        decode_nl_in_obj=decode_nl_in_obj,
        NL_PLACEHOLDER=NL_PLACEHOLDER,
    )


def session_datadir() -> str:
    lp = linkfox_paths_module()
    d = os.path.join(lp.session_root(time.time()), "data")
    os.makedirs(d, exist_ok=True)
    return d


def resolve_skills_root(*, skill_root: str | None = None) -> str:
    """返回 skills 仓库根目录（各 linkfox-* skill 的父目录）。

    本 skill 已将 collection_pipeline 本地化到 scripts/collection_pipeline/，
    shared_root() 指向本地包；通过探测 skill_root 父目录定位同级 skill（如
    linkfox-aigc-textgen），不能从 skill_root 再向上一级，否则 flat 部署
    （…/skills/<skill>）会误指到 …/.ce/ 而非 …/skills/。
    """
    shared_dir = os.path.dirname(shared_root())  # 本地 scripts/
    skills_root = os.path.dirname(shared_dir)
    if skill_root:
        alt = os.path.dirname(os.path.abspath(skill_root))
        for candidate in (skills_root, alt):
            probe = os.path.join(candidate, "linkfox-aigc-textgen", "scripts", "aigc_textgen.py")
            if os.path.isfile(probe):
                return candidate
    return skills_root


def resolve_skill_scripts(skill_root: str) -> dict[str, str]:
    skill_root = os.path.abspath(skill_root)
    skills_root = resolve_skills_root(skill_root=skill_root)
    return {
        "skill_root": skill_root,
        "textgen_script": os.path.join(skills_root, "linkfox-aigc-textgen", "scripts", "aigc_textgen.py"),
        "imagegen_script": os.path.join(skills_root, "linkfox-aigc-imagegen", "scripts", "aigc_imagegen.py"),
        "brand_gene_save_script": os.path.join(
            skills_root, "linkfox-aigc-imagegen-brand-gene-extract", "scripts", "save_brand_gene.py"
        ),
        "run_one_task_script": os.path.join(skill_root, "scripts", "run_one_task.py"),
    }


def apply_script_paths(job: dict, scripts: dict[str, str]) -> None:
    """写入下游脚本绝对路径；job 中已有且文件存在则保留，否则用自动解析结果。"""
    for script_key in (
        "textgen_script",
        "imagegen_script",
        "brand_gene_save_script",
        "run_one_task_script",
    ):
        resolved = scripts[script_key]
        existing = job.get(script_key)
        if existing and os.path.isfile(os.path.abspath(str(existing))):
            job[script_key] = os.path.abspath(str(existing))
        else:
            job[script_key] = resolved


def load_template(name: str) -> str:
    path = os.path.join(shared_root(), "templates", name)
    if not os.path.isfile(path):
        raise FileNotFoundError(f"模板不存在: {path}")
    with open(path, encoding="utf-8") as f:
        return f.read()


def is_transient(msg: str) -> bool:
    return bool(TRANSIENT_RE.search(msg or ""))


def run_subprocess(cmd: list[str], *, input_text: str | None = None, timeout: int = 120) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, input=input_text, text=True, capture_output=True, timeout=timeout)


def run_textgen(textgen_script: str, params: dict, *, content_only: bool = False) -> str:
    cmd = [sys.executable, textgen_script, "--stdin"]
    if content_only:
        cmd.append("--content-only")
    last_err = ""
    for attempt in range(2):
        if attempt:
            time.sleep(2.0)
        proc = run_subprocess(cmd, input_text=json.dumps(params, ensure_ascii=False), timeout=TEXTGEN_TIMEOUT)
        if proc.returncode == 0:
            body = (proc.stdout or "").strip()
            if content_only:
                if not body:
                    raise RuntimeError("textgen 返回空 content")
                return body
            try:
                data = json.loads(body)
            except json.JSONDecodeError as e:
                raise RuntimeError(f"textgen stdout 非 JSON: {e}; tail={body[:200]}") from e
            content = _extract_content(data)
            if not content:
                raise RuntimeError("textgen 响应无 content")
            return content
        last_err = (proc.stderr or proc.stdout or "").strip()
        if not is_transient(last_err):
            break
    tail = last_err.splitlines()[-3:] if last_err else ["unknown"]
    raise RuntimeError(f"textgen 失败: {' | '.join(tail)}")


def _extract_content(data: dict) -> str:
    if isinstance(data.get("content"), str):
        return data["content"]
    inner = data.get("data")
    if isinstance(inner, dict) and isinstance(inner.get("content"), str):
        return inner["content"]
    return ""


def parse_json_from_text(text: str) -> Any:
    text = (text or "").strip()
    lp = linkfox_paths_module()
    text = lp.decode_nl(text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    m = JSON_BLOCK_RE.search(text)
    if m:
        return json.loads(m.group(1).strip())
    for opener, closer in (("{", "}"), ("[", "]")):
        start = text.find(opener)
        end = text.rfind(closer)
        if start >= 0 and end > start:
            return json.loads(text[start : end + 1])
    raise ValueError("无法从 textgen 输出解析 JSON")


def extract_image_plan_list(parsed: Any) -> Any:
    # 剥离最外层「仅含单个 list 元素」的数组包裹（可能嵌套多层）
    while isinstance(parsed, list) and len(parsed) == 1 and isinstance(parsed[0], list):
        parsed = parsed[0]
    # 形如 [{"imagePlanList": [...]}] —— 单元素数组里包着目标对象
    if (
        isinstance(parsed, list)
        and len(parsed) == 1
        and isinstance(parsed[0], dict)
        and "imagePlanList" in parsed[0]
    ):
        parsed = parsed[0]
    plan = parsed.get("imagePlanList") if isinstance(parsed, dict) else parsed
    # imagePlanList 值本身也可能被多包一层
    while isinstance(plan, list) and len(plan) == 1 and isinstance(plan[0], list):
        plan = plan[0]
    return plan


def expand_type_slots(types_spec: list[dict] | None, default_plan: list[tuple[str, int]]) -> list[str]:
    if not types_spec:
        slots: list[str] = []
        for ttype, count in default_plan:
            slots.extend([ttype] * count)
        return slots
    slots = []
    for item in types_spec:
        ttype = item.get("type")
        count = int(item.get("count") or 1)
        if not ttype or count < 1:
            raise ValueError(f"非法 types 条目: {item!r}")
        slots.extend([ttype] * count)
    return slots


def resolve_ratio(ttype: str, aspect_ratio: str, aplus_ratio: str) -> str:
    if ttype in APLUS_TYPES:
        return aplus_ratio or aspect_ratio or DEFAULT_RATIOS.get(ttype, "1464:600")
    return aspect_ratio or DEFAULT_RATIOS.get(ttype, "1:1")


def assign_layouts(slots: list[str]) -> list[str]:
    sp_i = 0
    size_i = 0
    layouts: list[str] = []
    for ttype in slots:
        if ttype in SP_APLUS_TYPES:
            layouts.append(SP_LAYOUTS[sp_i % len(SP_LAYOUTS)])
            sp_i += 1
        elif ttype in SIZE_TYPES:
            layouts.append(SIZE_LAYOUTS[size_i % len(SIZE_LAYOUTS)])
            size_i += 1
        else:
            layouts.append("")
    return layouts


def default_image_desc_for_type(ttype: str) -> str:
    if ttype == "SIZE":
        return "这是一张商品尺码示意图，图中详细标注了产品的各项关键参数"
    return ""


def normalize_brand_key(brand_key: dict | None) -> dict:
    """collection-job / state 中的 brandKey 默认值补齐。"""
    bk = dict(brand_key or {})
    bk.setdefault("language", "英文")
    bk.setdefault("platform", "亚马逊")
    bk.setdefault("salesRegion", "美国")
    bk.setdefault("brandColor", "")
    bk.setdefault("fontStyle", "")
    bk.setdefault("brandName", "")
    return bk


def build_slots_skeleton(
    slots: list[str],
    *,
    aspect_ratio: str,
    aplus_ratio: str,
    user_image_desc: str,
    language: str = "英文",
) -> list[dict]:
    layouts = assign_layouts(slots)
    plan: list[dict] = []
    for ttype, layout in zip(slots, layouts):
        entry: dict[str, Any] = {
            "type": ttype,
            "point": "",
            "desc": "",
            "image_desc": default_image_desc_for_type(ttype),
            "ratio": resolve_ratio(ttype, aspect_ratio, aplus_ratio),
            "layout": layout,
        }
        if ttype == "MODEL_IMAGE" and user_image_desc:
            entry["image_desc"] = user_image_desc
        if ttype == "SIZE":
            entry["language"] = language or "英文"
        plan.append(entry)
    return plan


def merge_s1_result(base: list[dict], s1_list: list[dict]) -> list[dict]:
    if len(s1_list) != len(base):
        raise ValueError(f"S1 返回条目数 {len(s1_list)} 与规划槽位 {len(base)} 不一致")
    merged: list[dict] = []
    for b, s in zip(base, s1_list):
        row = dict(b)
        for key in ("type", "point", "desc", "image_desc", "ratio", "layout", "language"):
            val = s.get(key)
            if val is not None and val != "":
                if key == "type" and val != row["type"]:
                    raise ValueError(f"S1 类型 {val} 与槽位 {row['type']} 不一致")
                row[key] = val
        merged.append(row)
    return merged


def plan_summary(plan: list[dict], type_labels: dict[str, str]) -> list[dict]:
    out = []
    for i, row in enumerate(plan, 1):
        ttype = row.get("type", "")
        out.append(
            {
                "index": i,
                "type": ttype,
                "label": type_labels.get(ttype, ttype),
                "desc": row.get("desc") or "—",
                "point": row.get("point") or "—",
                "image_desc": row.get("image_desc") or "—",
                "ratio": row.get("ratio") or "1:1",
            }
        )
    return out


SAVED_FULL_RESPONSE_PREFIX = "Saved full response: "


def _sanitize_table_cell(val: Any) -> str:
    """表格单元格：禁止 | / 换行，空值统一为 —。"""
    if val is None or val == "":
        return "—"
    s = str(val).replace("\r\n", " ").replace("\n", " ").replace("\r", " ")
    s = s.replace("|", "/").replace("｜", "/")
    s = s.strip()
    return s if s else "—"


def format_plan_summary_table(summary: list[dict]) -> str:
    """plan phase 用户可见 Markdown 表格（写入 plan-summary md 文件）。"""
    lines = [
        "# 套图规划方案",
        "",
        "| 序号 | 类型 | 简述 | 画面内容 | 比例 |",
        "|------|------|------|----------|------|",
    ]
    for row in summary:
        label = row.get("label") or row.get("type") or "—"
        lines.append(
            "| {index} | {label} | {desc} | {image_desc} | {ratio} |".format(
                index=row.get("index", ""),
                label=_sanitize_table_cell(label),
                desc=_sanitize_table_cell(row.get("desc", "—")),
                # point=_sanitize_table_cell(row.get("point", "—")),
                image_desc=_sanitize_table_cell(row.get("image_desc", "—")),
                ratio=_sanitize_table_cell(row.get("ratio", "1:1")),
            )
        )
    return "\n".join(lines) + "\n"


def write_plan_summary_md(datadir: str, summary: list[dict]) -> str:
    """把 plan summary 写到 datadir/plan-summary-<ts>.md，返回绝对路径。

    文件仅作留档；用户可见表格由 print_plan_phase_result 直接 print 到 stdout，
    由 agent 原样转发。bridge 不会内联渲染 Saved full response 中的 md 路径。
    """
    os.makedirs(datadir, exist_ok=True)
    ts = int(time.time() * 1000)
    path = os.path.join(datadir, f"plan-summary-{ts}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(format_plan_summary_table(summary))
    return os.path.abspath(path)


def format_saved_response_line(payload: Any) -> str:
    """构造单行 acpx-bridge 行级协议字符串。

    - payload 为 list → ``Saved full response: ["a.png", ...]``（成功图）
    - payload 为 str → ``Saved full response: /abs/path.json``（失败 JSON 或 md 路径）
    """
    if isinstance(payload, list):
        body = json.dumps(payload, ensure_ascii=False)
    else:
        body = str(payload)
    return f"{SAVED_FULL_RESPONSE_PREFIX}{body}"


def emit_saved_response(payload: Any) -> None:
    """流式 print 一行 Saved full response（格式见 ``format_saved_response_line``）。"""
    print(format_saved_response_line(payload), flush=True)


def print_plan_phase_result(result: dict, *, datadir: str | None = None) -> None:
    """plan phase stdout 顺序：先 markdown 表格正文（agent 原样转发到对话回复），
    后跟一行 status JSON（agent 内部解析，不展示给用户）。

    历史版本曾试图通过 ``Saved full response: <md 路径>`` 让 bridge 自动把
    plan-summary md 文件渲染到对话气泡，但 bridge 对包在 Bash 工具调用里的
    ``Saved full response`` 不会做 md 内容内联渲染，导致用户看不到规划表格。
    现改为：md 文件仍写盘留档，markdown 表格内容**直接打印到 stdout**，
    与 dispatch summary 阶段「原样转发末尾 markdown」的机制对齐。

    - awaiting_confirm 且有 summary → 写 md 文件、stdout 打 markdown 表格、再打 status JSON
    - ready_to_dispatch / error → 仅打 status JSON（无需用户确认或无表格内容）
    """
    if result.get("status") == "awaiting_confirm":
        summary = result.get("summary")
        if isinstance(summary, list) and summary:
            target_dir = datadir or os.path.dirname(result.get("plan_file") or "") or os.getcwd()
            md_path = write_plan_summary_md(target_dir, summary)
            result["plan_summary_file"] = md_path
            print(format_plan_summary_table(summary), flush=True)
    print(json.dumps(result, ensure_ascii=False))


def task_result_path(datadir: str, task_id: str) -> str:
    """task-result 片段落盘绝对路径（single_task 写、summary 读）。"""
    safe_id = re.sub(r"[^0-9A-Za-z\u4e00-\u9fff_-]+", "-", str(task_id or "unknown"))
    return os.path.abspath(os.path.join(datadir, f"task-result-{safe_id}.json"))


def write_task_result(datadir: str, payload: dict) -> str:
    """single_task 完成后写 task-result-<id>.json 片段，返回绝对路径。

    片段结构（summary 阶段消费）：
      - id / type / label / status (success|failed) / images[] / error
      - 用户可见字段：point / layout / ratio
      - product variant 额外：assets[]（slot/label/kind/type/sourceTaskId/src/...）
    """
    os.makedirs(datadir, exist_ok=True)
    path = task_result_path(datadir, str(payload.get("id") or "unknown"))
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return path


def read_task_results(datadir: str, expected_ids: list[str]) -> list[dict]:
    """按 expected_ids 顺序读 task-result 片段；缺片段 → 视为失败任务。

    expected_ids 一般来自 plan 阶段写入 state.json 的 task_specs[].id 列表。
    缺文件常见于：单任务 Bash 异常崩溃、agent 漏发 / 跳过该 Bash。
    """
    results: list[dict] = []
    for tid in expected_ids:
        path = task_result_path(datadir, tid)
        if os.path.isfile(path):
            try:
                with open(path, encoding="utf-8") as f:
                    results.append(json.load(f))
                continue
            except (OSError, json.JSONDecodeError) as e:
                results.append({
                    "id": tid,
                    "status": "failed",
                    "error": f"task-result 片段读取失败: {e}",
                })
                continue
        results.append({
            "id": tid,
            "status": "failed",
            "error": "task-result 片段缺失（单任务 Bash 未输出该片段）",
        })
    return results


def merge_assets_from_results(results: list[dict]) -> list[dict]:
    """从所有任务结果片段汇总 assets[]（仅 product variant 的任务会有）。"""
    merged: list[dict] = []
    for row in results:
        if not isinstance(row, dict):
            continue
        for asset in row.get("assets") or []:
            if isinstance(asset, dict):
                merged.append(asset)
    return merged


def collect_success_image_paths(results: list[Any] | None) -> list[str]:
    """按 results 顺序，扁平收集成功任务的 media 绝对路径。"""
    paths: list[str] = []
    if not isinstance(results, list):
        return paths
    for row in results:
        if not isinstance(row, dict):
            continue
        if row.get("status") not in ("success", "dry-run"):
            continue
        for img in row.get("images") or []:
            if isinstance(img, str) and img:
                paths.append(img)
    return paths


def _task_label(task: dict, type_labels: dict[str, str] | None = None) -> str:
    ttype = task.get("type") or ""
    if type_labels and type_labels.get(ttype):
        return type_labels[ttype]
    tid = task.get("id") or ""
    if isinstance(tid, str) and "-" in tid:
        # build_collection_manifest 的 id 形如 "1-场景图"
        tail = tid.split("-", 1)[1]
        if tail:
            return tail
    return ttype or "图片"


def format_completion_summary(
    *,
    results: list[dict],
    tasks: list[dict],
    type_labels: dict[str, str] | None = None,
    variant: str | None = None,  # 向后兼容，已不使用
) -> str:
    """返回套图末尾 markdown 成功明细字符串。

    格式：``X/Y 概述`` + 每张成功图两行（``- **第 N 张 · {label}**　简述：…`` +
    缩进 2 空格的 ``  ![{label}]({abs_path})`` 内联引用）+ 「失败项」列表（如有）。

    不含 ``<linkfox-suggestion-*>`` / A+ 推荐句等对话呈现层标签——由 agent 在
    回复正文末尾追加。完整交付协议见 ``references/runtime/03-deliver.md``。
    """
    del variant
    total = len(tasks)
    success_count = sum(1 for r in results if isinstance(r, dict) and r.get("status") in ("success", "dry-run"))
    failed_count = total - success_count
    lines: list[str] = []
    if total == success_count:
        lines.append(f"**{success_count}/{total} 全部生成成功**")
    elif success_count == 0:
        lines.append(f"**0/{total} 生成失败**")
    else:
        lines.append(f"**{success_count}/{total} 生成成功，{failed_count} 张失败**")
    lines.append("")
    for idx, (task, result) in enumerate(zip(tasks, results), start=1):
        label = _task_label(task, type_labels)
        if isinstance(result, dict) and result.get("status") in ("success", "dry-run"):
            desc = (task.get("desc") or "").strip()
            tail = f"　简述：{desc}" if desc else ""
            lines.append(f"- **第 {idx} 张 · {label}**{tail}")
            first_img = next(
                (img for img in (result.get("images") or []) if isinstance(img, str) and img),
                "",
            )
            if first_img:
                lines.append(f"  ![{label}]({first_img})")
    failed_rows = [
        (idx, task, result)
        for idx, (task, result) in enumerate(zip(tasks, results), start=1)
        if isinstance(result, dict) and result.get("status") == "failed"
    ]
    if failed_rows:
        lines.append("")
        lines.append("**失败项：**")
        lines.append("")
        for idx, task, result in failed_rows:
            label = _task_label(task, type_labels)
            err = (result.get("error") or "未知错误").strip().splitlines()[0]
            lines.append(f"- 第 {idx} 张 · {label}：{err}")
    return "\n".join(lines)


def emit_completion_summary(
    *,
    results: list[dict],
    tasks: list[dict],
    type_labels: dict[str, str] | None = None,
    variant: str | None = None,  # 向后兼容，已不使用
    emit_images: bool = False,
) -> None:
    """流式 print ``format_completion_summary`` 返回的 markdown 明细。"""
    del variant, emit_images
    print(
        format_completion_summary(results=results, tasks=tasks, type_labels=type_labels),
        flush=True,
    )
