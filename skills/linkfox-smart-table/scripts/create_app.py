#!/usr/bin/env python3
"""应用开发一条龙 - LinkFox Skill

把「选模板 → 建应用 → 拿源码 → 发布」压成一条命令，供 workbuddy / codex / Claude Code
等 agent 直接调用。串起来的是下面四个已有操作，不再让模型自己编排：

  listOfficialTemplates → listMyTables / createTable → createApplication
  → publishApplication → listApplications（校验）

⚠️ **在本机执行，不要在远端沙箱里执行。**
  `dev`（pnpm dev）和 `--build`（本机构建校验）都需要 Node/pnpm；发布由服务端构建。
  沙箱里通常没有 Node/pnpm 或装不上依赖，会直接失败。这些命令请交给用户本地终端执行。

子命令：

  templates   列出应用模板（让用户选基于哪个模板开发）
  apps        列出我的应用（修改已有应用时用）
  create      按模板新建应用 + 下载源码（默认不发布）
  dev         本地预览：启动 pnpm dev（Node server，http://localhost:3000），未登录走 SSO
  publish     用户确认后，把本地代码打包上传并发布（复用创建时的 sessionId）
  status      查看某个应用的本地状态 + 远端发布地址

Examples:
  python scripts/create_app.py templates
  python scripts/create_app.py templates --platform amazon --stage selection
  python scripts/create_app.py create --template amazon-search --name 我的选品库
  python scripts/create_app.py create --template amazon-search --name 我的选品库 --notebook-name 亚马逊选品
  # 默认工作目录是纯英文：./linkfox-apps/amazon-search-aplXxx
  # 本地预览（pnpm dev，未登录走 SSO）：
  python scripts/create_app.py dev --dir ./linkfox-apps/amazon-search-aplXxx
  # 用户确认要发布后再执行：
  python scripts/create_app.py publish --dir ./linkfox-apps/amazon-search-aplXxx --build
  python scripts/create_app.py apps --name 选品
  python scripts/create_app.py status --dir ./linkfox-apps/amazon-search-aplXxx

⚠️ 默认不发布：`create` 只建应用 + 下载源码；改代码在 `pnpm dev` 里改，
   用户明确同意上线后再 `publish`。不要每改一点就发布。

入参说明：
  --template        模板的 resourceId（如 amazon-search）。也接受 32 位十六进制 id，脚本会换成 resourceId。
  --name            应用名；同时作为默认多维表名和默认工作目录名。
  --notebook-id     建到哪个多维表（nbk 开头）。优先级最高。
  --notebook-name   按多维表名找；找不到会自动建一个，同名多个会报错让用户选。
  --dir             本地工作目录，默认 ./linkfox-apps/<templateId>-<applicationId>（纯英文）。
  --build           发布前在本机跑 pnpm install + pnpm build 做校验（沙箱里别用）。
  --force-upload    不尝试复用创建接口给的 sourceUrl，始终重新打包上传。
  --publish         create 建好后立即发布（不建议；默认先本地 pnpm dev 预览）。
  --force-new       同名应用已存在时仍然新建一个（默认复用已有应用）。

默认行为：create 只建应用 + 下载源码，不发布，结束时会打印本地预览命令。

状态文件：
  ~/.linkfox-skill/apps/<applicationId>.json   全局索引（列应用、找回 sessionId）
  <工作目录>/.linkfox-app.json                 本地工作目录状态（重新发布时用）

依赖：
  仅 stdlib；上传走同目录 linkfox_paths.upload_file()，需要 `pip install oss2`。
  模板下载包里的 .env / .env.local 已由服务端填好 clientId / notebookId / applicationId，
  本脚本不会改写它们。
"""

import argparse
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tarfile
import time
import urllib.error
import urllib.request
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
STATE_DIR = os.path.join(os.path.expanduser("~"), ".linkfox-skill", "apps")
DEFAULT_WORK_ROOT = os.path.join(os.getcwd(), "linkfox-apps")
STATE_FILE_NAME = ".linkfox-app.json"

# 打包时要排除的目录/文件（与模板仓库 publish-templates.mjs 的口径一致）
EXCLUDE_DIRS = {"node_modules", ".next", "out", "dist", ".git", ".turbo", ".vercel"}
EXCLUDE_FILE_SUFFIXES = (".tar.gz", ".tgz")
# 本地开发配置（如果存在）不打进发布包
EXCLUDE_FILES = {STATE_FILE_NAME, ".DS_Store", ".env.development.local", ".env.development"}

# createApplication 的锁最长 2 分钟，留一点余量
CREATE_LOCK_TIMEOUT = 150
RETRYABLE_CODES = {0, 408, 429, 500, 502, 503, 504}


class SkillError(RuntimeError):
    """可直接展示给用户的业务错误。"""


# ---------------------------------------------------------------------------
# 通用：加载已有 op 脚本、调用接口、写状态
# ---------------------------------------------------------------------------

_OP_CACHE = {}


def _load_op(op_snake):
    """加载同目录 op_<snake>.py。复用里面的 call_api，避免再写一份 HTTP。"""
    if op_snake in _OP_CACHE:
        return _OP_CACHE[op_snake]
    if HERE not in sys.path:
        sys.path.insert(0, HERE)
    path = os.path.join(HERE, "op_" + op_snake + ".py")
    if not os.path.isfile(path):
        raise SkillError("找不到操作实现：" + path)
    spec = importlib.util.spec_from_file_location("create_app_op_" + op_snake, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    _OP_CACHE[op_snake] = module
    return module


def _call(op_snake, params, *, ok_codes=(200,), allow_missing_code=False):
    """调一个 op 的 call_api，把业务错误收敛成 SkillError。

    ⚠️ 这些接口 HTTP 恒 200，成功与否看 errcode；连接失败时 call_api 返回 errcode=0。
    """
    result = _load_op(op_snake).call_api(params)
    if not isinstance(result, dict):
        raise SkillError("%s 返回格式异常：%r" % (op_snake, result))
    code = result.get("errcode")
    if code is None and allow_missing_code:
        return result
    if code not in ok_codes:
        raise SkillError(
            "%s 失败：errcode=%s errmsg=%s"
            % (op_snake, code, str(result.get("errmsg") or "").strip())
        )
    return result


def _errmsg(result):
    return str((result or {}).get("errmsg") or "").strip()


def _now():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _require_api_key():
    if os.environ.get("LINKFOX_AGENT_API_KEY") or os.environ.get("LINKFOXAGENT_API_KEY"):
        return
    raise SkillError(
        "未检测到 LINKFOX_AGENT_API_KEY / LINKFOXAGENT_API_KEY。\n"
        "请先运行 linkfox-onboarding 完成登录：\n"
        "  python <skills>/linkfox-onboarding/scripts/send_verify_code.py <手机号>\n"
        "  python <skills>/linkfox-onboarding/scripts/login_and_get_key.py <手机号> <验证码> skill\n"
        "拿到 api_key 后写入环境变量并重启会话。详见 docs/app-development-guide.md 第 3 节。"
    )


def _write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


def _read_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _state_path_for(application_id):
    return os.path.join(STATE_DIR, application_id + ".json")


def _save_state(state):
    state["updatedAt"] = _now()
    _write_json(_state_path_for(state["applicationId"]), state)
    workdir = state.get("workdir")
    # 只在工作目录已经存在时写副本，避免把「仅存在于远端列表」的应用也造出一个空工作目录
    if workdir and os.path.isdir(workdir):
        _write_json(os.path.join(workdir, STATE_FILE_NAME), state)
    return state


def _save_session_record(state, action):
    """按仓库约定，把本次结果另存一份到会话 data/ 目录，便于回看。"""
    try:
        if HERE not in sys.path:
            sys.path.insert(0, HERE)
        import linkfox_paths

        path = linkfox_paths.resolve_data_path("linkfox-app-" + action, time.time())
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(_public_state(state), f, ensure_ascii=False, indent=2)
    except Exception:
        # 会话目录写失败不影响主流程
        pass


def _find_state(args):
    """按 --state / --dir / --application-id / --name 找一个已保存的应用状态。"""
    if args.state:
        return _read_json(os.path.abspath(os.path.expanduser(args.state)))
    if args.dir:
        path = os.path.join(os.path.abspath(os.path.expanduser(args.dir)), STATE_FILE_NAME)
        if os.path.isfile(path):
            return _read_json(path)
        raise SkillError("目录里没有 %s：%s（不是本脚本创建的工作目录？）" % (STATE_FILE_NAME, path))
    if args.application_id:
        path = _state_path_for(args.application_id)
        if os.path.isfile(path):
            return _read_json(path)
        raise SkillError("本地没有这个应用的状态文件：%s" % path)
    if args.name:
        return _find_state_by_name(args.name)
    raise SkillError("需要 --dir / --state / --application-id / --name 之一")


def _iter_states():
    if not os.path.isdir(STATE_DIR):
        return
    for name in sorted(os.listdir(STATE_DIR)):
        if not name.endswith(".json"):
            continue
        try:
            yield _read_json(os.path.join(STATE_DIR, name))
        except (OSError, ValueError):
            continue


def _find_state_by_name(name):
    wanted = name.strip().lower()
    exact = []
    fuzzy = []
    for state in _iter_states():
        app_name = str(state.get("name") or "")
        if app_name.lower() == wanted:
            exact.append(state)
        elif wanted in app_name.lower():
            fuzzy.append(state)
    candidates = exact or fuzzy
    if len(candidates) == 1:
        return candidates[0]
    if not candidates:
        raise SkillError("本地没有应用名为 %r 的状态文件" % name)
    lines = ["匹配到多个应用，请用 --application-id 或 --dir 指定："]
    for state in candidates:
        lines.append(
            "  - %s  applicationId=%s  workdir=%s"
            % (state.get("name"), state.get("applicationId"), state.get("workdir"))
        )
    raise SkillError("\n".join(lines))


def _ascii_token(value, fallback="app"):
    """目录/文件名只用 ASCII：中文应用名、路径分隔符等一律剔除。"""
    import re

    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", str(value or "")).strip("-._")
    return cleaned or fallback


def _default_workdir(template_id, application_id):
    """默认工作目录用纯英文：./linkfox-apps/<templateId>-<applicationId>。

    中文应用名放在状态文件里，不参与目录名，避免 pnpm / tar / Windows 路径出问题。
    """
    app_token = _ascii_token(application_id or "", "app-" + str(int(time.time())))
    return os.path.join(DEFAULT_WORK_ROOT, _ascii_token(template_id) + "-" + app_token)


# ---------------------------------------------------------------------------
# 查询：模板 / 多维表 / 应用
# ---------------------------------------------------------------------------

def _list_app_templates(platform="", stage="", keyword="", fetch_all=True):
    params = {"templateType": "app", "page": 1, "pageSize": 50}
    if platform:
        params["platform"] = platform
    if stage:
        params["stage"] = stage
    if keyword:
        params["keyword"] = keyword

    rows = []
    page = 1
    while True:
        params["page"] = page
        result = _load_op("list_official_templates").call_api(params)
        code = result.get("errcode") if isinstance(result, dict) else None
        # 公开模板接口成功时 errcode 可能缺省 / 0 / 200；但连接失败也会回 errcode=0，
        # 所以只有同时带 list 才算成功，避免把网络错误读成「模板列表为空」。
        page_rows = result.get("list") if isinstance(result, dict) else None
        if code not in (None, 0, 200) or not isinstance(page_rows, list):
            raise SkillError(
                "获取应用模板失败：errcode=%s errmsg=%s"
                % (code, str((result or {}).get("errmsg") or "").strip())
            )
        rows.extend(page_rows)
        total = result.get("total")
        if not fetch_all or not page_rows:
            break
        if isinstance(total, int) and len(rows) >= total:
            break
        if len(page_rows) < params["pageSize"] or page >= 200:
            break
        page += 1
    return rows


def _find_template(value):
    """把用户给的 resourceId 或 32 位 id 解析成模板记录。"""
    wanted = (value or "").strip()
    if not wanted:
        raise SkillError("--template 不能为空")
    templates = _list_app_templates()
    hits = [
        t for t in templates
        if str(t.get("resourceId") or "").strip() == wanted
        or str(t.get("id") or "").strip() == wanted
    ]
    if len(hits) == 1:
        template = hits[0]
        if not template.get("resourceId"):
            raise SkillError("模板 %r 缺少 resourceId，无法创建" % wanted)
        return template
    if not hits:
        sample = "、".join(
            sorted({str(t.get("resourceId")) for t in templates if t.get("resourceId")})[:20]
        )
        raise SkillError(
            "找不到模板 %r。可用模板 resourceId 例如：%s\n先运行 templates 子命令查看完整清单。"
            % (wanted, sample or "（模板列表为空）")
        )
    raise SkillError("模板 %r 命中多条，请改用 resourceId 精确指定" % wanted)


def _list_all_notebooks():
    """listMyTables 分页拉全，返回 notebooks 数组。"""
    notebooks = []
    page = 1
    while True:
        result = _call("list_my_tables", {"page": page, "perPage": 100})
        rows = result.get("notebooks")
        if not isinstance(rows, list):
            rows = []
        notebooks.extend(rows)
        total = result.get("total")
        if not rows or (isinstance(total, int) and len(notebooks) >= total):
            break
        if len(rows) < 100 or page >= 50:
            break
        page += 1
    return notebooks


def _resolve_notebook(args):
    """返回 (notebookId, notebookName, created)。"""
    notebook_id = (args.notebook_id or "").strip()
    if notebook_id:
        if not notebook_id.startswith("nbk"):
            raise SkillError("--notebook-id 要 nbk 开头的多维表 id，不是数据表 id")
        return notebook_id, "", False

    wanted = (args.notebook_name or args.name).strip()
    matches = [n for n in _list_all_notebooks() if str(n.get("name") or "").strip() == wanted]
    if len(matches) == 1:
        return matches[0].get("notebookId"), wanted, False
    if len(matches) > 1:
        ids = "\n".join("  - %s  %s" % (n.get("notebookId"), n.get("name")) for n in matches)
        raise SkillError("多维表名 %r 命中多个，请用 --notebook-id 指定：\n%s" % (wanted, ids))

    # 找不到就建一个（createTable 会同时建容器和一张默认表）。requestKey 保证重试不会建重。
    request_key = "linkfox-app-nb-" + hashlib.sha1(wanted.encode("utf-8")).hexdigest()[:16]
    result = _call("create_table", {"name": wanted, "requestKey": request_key})
    new_id = result.get("notebookId")
    if not new_id:
        raise SkillError("createTable 没有返回 notebookId：%r" % result)
    return new_id, result.get("notebookName") or wanted, True


def _list_applications(name="", notebook_id=""):
    params = {}
    if name:
        params["name"] = name
    if notebook_id:
        params["notebookId"] = notebook_id
    result = _call("list_applications", params)
    rows = result.get("applications")
    return rows if isinstance(rows, list) else []


def _find_existing_app(name, notebook_id):
    """按名字 + 多维表精确找应用。name 接口是包含匹配，这里必须自己收窄。"""
    wanted = name.strip()
    for app in _list_applications(name=wanted, notebook_id=notebook_id):
        if str(app.get("name") or "").strip() == wanted:
            return app
    return None


# ---------------------------------------------------------------------------
# 创建 / 发布
# ---------------------------------------------------------------------------

def _create_application(notebook_id, template_id, name):
    """createApplication：处理 409 锁、网络超时和「不幂等」三件事。"""
    payload = {"notebookId": notebook_id, "templateId": template_id, "name": name}
    deadline = time.time() + CREATE_LOCK_TIMEOUT
    last_error = ""

    while True:
        result = _load_op("create_application").call_api(payload)
        code = result.get("errcode") if isinstance(result, dict) else None
        message = _errmsg(result)

        if code == 200:
            if not result.get("sessionId"):
                raise SkillError(
                    "应用已创建，但没有拿到 sessionId（进不去编辑器）。"
                    "applicationId=%s，可从应用列表打开。" % result.get("applicationId")
                )
            return result

        if code == 409 and "已有应用正在创建中" in message:
            # 按用户挡的锁，跟多维表/模板无关；锁最长 2 分钟自己过期。
            if time.time() >= deadline:
                raise SkillError("等待创建锁超时（约 2 分钟）：%s" % message)
            if not last_error:
                print("上一个创建请求还没结束，等待锁释放后重试…", file=sys.stderr)
            last_error = message
            time.sleep(5)
            continue

        # 另一种 409 是「本次会话 id 已被占用」（极少见），同样按不幂等处理：
        # 先查有没有建出来，确认没有才重新发起。
        if code in RETRYABLE_CODES or code == 409:
            # 不幂等：先查有没有建出来，确认没有才重试。
            time.sleep(2)
            existing = _find_existing_app(name, notebook_id)
            if existing:
                print(
                    "创建请求没拿到回包，但应用已经建好了，继续使用：%s"
                    % existing.get("applicationId"),
                    file=sys.stderr,
                )
                return {
                    "errcode": 200,
                    "applicationId": existing.get("applicationId"),
                    "sessionId": existing.get("sessionId"),
                    "name": existing.get("name"),
                    "notebookId": existing.get("notebookId"),
                    "sourceUrl": None,
                    "_recovered": True,
                }
            if time.time() >= deadline:
                raise SkillError(
                    "创建应用失败：errcode=%s errmsg=%s（已确认没有建出来）" % (code, message)
                )
            last_error = message
            time.sleep(3)
            continue

        raise SkillError("创建应用失败：errcode=%s errmsg=%s" % (code, message))


def _publish(session_id, source_url, *, timeout_rounds=4):
    """publishApplication：同 session 并发会 409，同参数重试是安全的。"""
    payload = {"sessionId": session_id, "sourceUrl": source_url}
    last_error = ""
    for _ in range(timeout_rounds):
        result = _load_op("publish_application").call_api(payload)
        code = result.get("errcode") if isinstance(result, dict) else None
        if code == 200:
            if not result.get("publishUrl"):
                raise SkillError(
                    "发布接口返回成功但没有 publishUrl，按失败处理。"
                    "用 applications 命令确认上线状态。"
                )
            return result
        message = _errmsg(result)
        if code == 409:
            # 同一个 sessionId 上一次发布还没跑完；等锁过期，用同样参数再发。
            print("这个应用正在发布中，等待后重试…", file=sys.stderr)
            last_error = message
            time.sleep(5)
            continue
        if code in RETRYABLE_CODES:
            # 发布按 session 幂等，同样参数重发是安全的
            last_error = message
            time.sleep(3)
            continue
        raise SkillError("发布失败：errcode=%s errmsg=%s" % (code, message))
    raise SkillError("发布多次重试仍失败：%s" % last_error)


def _download(url, dest_path):
    if not url:
        raise SkillError("没有可下载的 sourceUrl（创建接口没给，且本地也没有缓存）")
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    request = urllib.request.Request(url, headers={"User-Agent": "LinkFox-Skill/2.0"})
    try:
        with urllib.request.urlopen(request, timeout=300) as response:
            with open(dest_path, "wb") as f:
                shutil.copyfileobj(response, f)
    except (urllib.error.URLError, OSError) as error:
        raise SkillError("下载源码包失败：%s" % error)


def _safe_extract(archive_path, dest_dir):
    os.makedirs(dest_dir, exist_ok=True)
    try:
        with tarfile.open(archive_path, "r:*") as tar:
            members = tar.getmembers()
            for member in members:
                name = member.name.replace("\\", "/")
                parts = [p for p in name.split("/") if p not in ("", ".")]
                if name.startswith("/") or ".." in parts:
                    raise SkillError("源码包里有不安全的路径：%s" % member.name)
            try:
                tar.extractall(dest_dir, filter="data")  # Python 3.12+
            except TypeError:
                tar.extractall(dest_dir)
    except (tarfile.TarError, OSError) as error:
        raise SkillError("解压源码包失败：%s" % error)


def _find_project_root(base_dir):
    """源码包根目录可能就是项目，也可能套了一层模板目录。"""
    if os.path.isfile(os.path.join(base_dir, "package.json")):
        return base_dir
    for entry in os.listdir(base_dir):
        candidate = os.path.join(base_dir, entry)
        if os.path.isdir(candidate) and os.path.isfile(os.path.join(candidate, "package.json")):
            return candidate
    raise SkillError("源码包里找不到 package.json：%s" % base_dir)


def _assert_no_key_in_publish_env(project_root):
    """发布包会带上 .env / .env.local；这里禁止把 API Key 写进去，避免打进线上产物。"""
    for name in (".env", ".env.local"):
        path = os.path.join(project_root, name)
        if not os.path.isfile(path):
            continue
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                text = line.strip()
                if not text or text.startswith("#") or "=" not in text:
                    continue
                key, value = text.split("=", 1)
                if key.strip() == "NEXT_PUBLIC_LINKFOX_API_KEY" and value.strip().strip('"').strip("'"):
                    raise SkillError(
                        "%s 里写了 NEXT_PUBLIC_LINKFOX_API_KEY，发布后会被打进线上产物。"
                        "本地预览不需要把 Key 写进 env（应用会走 SSO）；请删掉这一行再发布。"
                        % name
                    )


def _run_command(command, cwd, env=None):
    display = " ".join(command)
    print("+ %s" % display, file=sys.stderr)
    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
    except FileNotFoundError:
        raise SkillError(
            "找不到命令 %r。请在本机安装 Node/pnpm 后重试；"
            "远端沙箱里通常没有 pnpm，不要在那里做本地构建校验。" % command[0]
        )
    if completed.returncode != 0:
        tail = "\n".join((completed.stdout or "").strip().splitlines()[-25:])
        raise SkillError("命令失败（%s）：\n%s" % (display, tail))
    return completed.stdout or ""


def _build_project(project_dir):
    pnpm = shutil.which("pnpm")
    if not pnpm:
        raise SkillError(
            "找不到 pnpm。本地构建校验必须在用户电脑上执行；"
            "如果只想发布、不做本地校验，请去掉 --build。"
        )
    _run_command([pnpm, "install", "--frozen-lockfile", "--prefer-offline"], project_dir)
    env = dict(os.environ)
    env["NEXT_PUBLIC_BASE_PATH"] = "/"
    _run_command([pnpm, "build"], project_dir, env=env)


def _pack_project(workdir, out_path):
    """把工作目录重新打成 tar.gz。保持原包布局，排除构建产物与依赖。"""
    with tarfile.open(out_path, "w:gz") as tar:
        for root, dirs, files in os.walk(workdir):
            dirs[:] = sorted(d for d in dirs if d not in EXCLUDE_DIRS)
            for name in dirs:
                full = os.path.join(root, name)
                rel = os.path.relpath(full, workdir)
                tar.add(full, arcname=rel, recursive=False)
            for name in files:
                if name in EXCLUDE_FILES or name.endswith(EXCLUDE_FILE_SUFFIXES):
                    continue
                full = os.path.join(root, name)
                rel = os.path.relpath(full, workdir)
                tar.add(full, arcname=rel, recursive=False)


def _upload_once(path):
    if HERE not in sys.path:
        sys.path.insert(0, HERE)
    import linkfox_paths  # 同目录副本

    result = linkfox_paths.upload_file(path, slug="linkfox-app")
    url = result.get("url") if isinstance(result, dict) else None
    if not url:
        raise SkillError("上传源码包失败：没有返回 url")
    return url


def _upload_package(path):
    """上传到 OSS，返回公网 URL。复用 linkfox_paths 的 STS 直传。

    发布侧用 `tar -xzf` 解包，不看扩展名。个别环境 OSS 白名单只放 zip 不放 gz 时，
    把同一份 tar.gz 内容改名成 .zip 再传即可（内容仍是 gzip，解包不受影响）。
    """
    try:
        import linkfox_paths  # noqa: F401  先探一下依赖
    except ImportError as error:
        raise SkillError("缺少 linkfox_paths：%s" % error)
    try:
        return _upload_once(path)
    except SkillError:
        raise
    except Exception as error:  # oss2 缺失、STS 失败、类型白名单等
        message = str(error)
        if "oss2" in message:
            raise SkillError("上传需要 oss2，请先执行：pip install oss2")
        if "不在 OSS 允许列表中" in message and path.endswith(".gz"):
            fallback = path[:-3] + ".zip"  # app.tar.gz -> app.tar.zip
            shutil.copyfile(path, fallback)
            print(
                "OSS 白名单不含 gz，改用 .zip 扩展名上传同一份 tar.gz 内容…",
                file=sys.stderr,
            )
            try:
                return _upload_once(fallback)
            finally:
                try:
                    os.remove(fallback)
                except OSError:
                    pass
        raise SkillError("上传源码包失败：%s" % message)


def _prepare_local_copy(state, source_url):
    """下载创建接口给的源码包到工作目录；已存在则不覆盖。"""
    workdir = state["workdir"]
    if os.path.isfile(os.path.join(workdir, STATE_FILE_NAME)):
        return workdir
    os.makedirs(workdir, exist_ok=True)
    archive = os.path.join(workdir, "_source.tar.gz")
    _download(source_url, archive)
    _safe_extract(archive, workdir)
    try:
        os.remove(archive)
    except OSError:
        pass
    # 工作目录建好后补写一份本地状态，供 publish / status 直接读取
    _write_json(os.path.join(workdir, STATE_FILE_NAME), state)
    return workdir


def _find_app_by_id(application_id, name, notebook_id):
    for app in _list_applications(name=name or "", notebook_id=notebook_id or ""):
        if str(app.get("applicationId")) == str(application_id):
            return app
    return None


def _verify_publish(application_id, name, notebook_id, expected_url=None):
    """列表校验：拿远端真实的 publishUrl，避免只信发布接口的回显。"""
    for attempt in range(3):
        app = _find_app_by_id(application_id, name, notebook_id)
        if app and app.get("publishUrl"):
            return app
        if attempt < 2:
            time.sleep(2)
    app = _find_app_by_id(application_id, name, notebook_id)
    if app is None:
        raise SkillError("发布后没有在应用列表里找到这个应用（applicationId=%s）" % application_id)
    if expected_url and not app.get("publishUrl"):
        # 列表偶尔会有延迟；发布接口已经回了地址时不算失败，提示一下即可。
        print(
            "提示：发布接口已返回地址，但应用列表里还没更新 publishUrl（可能稍后生效）。",
            file=sys.stderr,
        )
    return app


# ---------------------------------------------------------------------------
# 子命令
# ---------------------------------------------------------------------------

def cmd_templates(args):
    rows = _list_app_templates(
        platform=args.platform or "",
        stage=args.stage or "",
        keyword=args.keyword or "",
        fetch_all=not args.first_page,
    )
    if args.json:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
        return 0
    if not rows:
        print("没有匹配的应用模板。")
        return 0

    print("应用模板（共 %d 个）：" % len(rows))
    print()
    header = "%-4s %-28s %-10s %-11s %-10s %s" % ("序号", "模板名", "平台", "阶段", "使用次数", "resourceId")
    print(header)
    print("-" * len(header))
    for index, row in enumerate(rows, 1):
        name = str(row.get("name") or "")[:26]
        print(
            "%-4s %-28s %-10s %-11s %-10s %s"
            % (
                index,
                name,
                str(row.get("platform") or "-"),
                str(row.get("stage") or "-"),
                str(row.get("usageCount") or 0),
                str(row.get("resourceId") or ""),
            )
        )
        intro = str(row.get("intro") or "").strip()
        if intro and not args.brief:
            print("     %s" % intro[:120])
    print()
    print("下一步：让用户选一个 resourceId，然后执行")
    print("  python scripts/create_app.py create --template <resourceId> --name <应用名>")
    return 0


def cmd_apps(args):
    _require_api_key()
    params = {}
    if args.name:
        params["name"] = args.name
    if args.notebook:
        params["notebookName"] = args.notebook
    if args.source:
        params["source"] = args.source
    result = _call("list_applications", params)
    rows = result.get("applications") if isinstance(result.get("applications"), list) else []

    local = {}
    for state in _iter_states():
        local[str(state.get("applicationId"))] = state

    if args.json:
        for row in rows:
            state = local.get(str(row.get("applicationId"))) or {}
            row["localWorkdir"] = state.get("workdir")
        print(json.dumps(rows, ensure_ascii=False, indent=2))
        return 0

    if not rows:
        print("没有找到应用。")
        return 0
    print("我的应用（共 %d 个）：" % len(rows))
    print()
    header = "%-4s %-24s %-20s %-12s %s" % ("序号", "应用名", "所属多维表", "本地工作目录", "发布地址")
    print(header)
    print("-" * len(header))
    for index, row in enumerate(rows, 1):
        state = local.get(str(row.get("applicationId"))) or {}
        workdir = state.get("workdir") or "-"
        if len(workdir) > 20:
            workdir = "..." + workdir[-17:]
        publish_url = row.get("publishUrl") or "未发布"
        print(
            "%-4s %-24s %-20s %-12s %s"
            % (
                index,
                str(row.get("name") or "")[:22],
                str(row.get("notebookName") or row.get("notebookId") or "")[:18],
                workdir,
                publish_url,
            )
        )
    print()
    print("修改已有应用：有本地工作目录的，改完执行")
    print("  python scripts/create_app.py publish --dir <本地工作目录>")
    print("没有本地工作目录的，请到 LinkFox 应用编辑器里修改（本 skill 不提供存量应用源码下载）。")
    return 0


def _print_preview_steps(workdir):
    print("", file=sys.stderr)
    print("应用和源码已准备好，默认先本地预览，不要直接发布：", file=sys.stderr)
    print('  python scripts/create_app.py dev --dir "%s"' % workdir, file=sys.stderr)
    print("dev 会启动 pnpm dev（Node server）；未登录会走 SSO，", file=sys.stderr)
    print("浏览器打开 http://localhost:3000，用 LinkFox 账号登录后给用户确认。", file=sys.stderr)
    print("改代码也在这个目录里改，dev 会热更新；不要每改一点就发布。", file=sys.stderr)
    print("用户明确要发布到线上后，再执行：", file=sys.stderr)
    print('  python scripts/create_app.py publish --dir "%s"' % workdir, file=sys.stderr)


def cmd_create(args):
    _require_api_key()
    name = (args.name or "").strip()
    if not name:
        raise SkillError("--name 不能为空")

    template = _find_template(args.template)
    template_id = str(template["resourceId"]).strip()
    print("使用模板：%s（%s）" % (template.get("name") or template_id, template_id), file=sys.stderr)

    notebook_id, notebook_name, notebook_created = _resolve_notebook(args)
    if notebook_created:
        print("已创建多维表：%s（%s）" % (notebook_name or name, notebook_id), file=sys.stderr)
    else:
        print("使用多维表：%s（%s）" % (notebook_name or name, notebook_id), file=sys.stderr)

    existing = _find_existing_app(name, notebook_id)
    if existing and not args.force_new:
        print(
            "这个多维表里已有同名应用 %r（applicationId=%s），直接复用；要新建加 --force-new。"
            % (name, existing.get("applicationId")),
            file=sys.stderr,
        )
        state = _state_from_app(existing)
        if not os.path.isfile(os.path.join(state["workdir"], STATE_FILE_NAME)):
            print("本地没有源码副本；可执行 publish --dir 前先确认代码来源。", file=sys.stderr)
        if not args.publish:
            if os.path.isdir(state.get("workdir") or ""):
                _print_preview_steps(state["workdir"])
            print(json.dumps(_public_state(state), ensure_ascii=False, indent=2))
            return 0
        if not existing.get("publishUrl"):
            raise SkillError(
                "复用了已有应用，但它还没有发布过，本地也没有源码包。"
                "请到 LinkFox 应用编辑器里发布，或加 --force-new 新建一个。"
            )
        print(json.dumps(_public_state(state), ensure_ascii=False, indent=2))
        return 0

    created = _create_application(notebook_id, template_id, name)
    workdir = os.path.abspath(
        os.path.expanduser(args.dir)
        if args.dir
        else _default_workdir(template_id, created.get("applicationId"))
    )
    state = {
        "applicationId": created.get("applicationId"),
        "sessionId": created.get("sessionId"),
        "name": created.get("name") or name,
        "notebookId": created.get("notebookId") or notebook_id,
        "notebookName": notebook_name or name,
        "templateId": template_id,
        "templateName": template.get("name") or "",
        "workdir": workdir,
        "sourceUrl": created.get("sourceUrl"),
        "publishUrl": None,
        "createdAt": _now(),
    }
    # sourceUrl 不落库，创建成功必须立刻保存
    _save_state(state)
    print("应用已创建：applicationId=%s sessionId=%s" % (state["applicationId"], state["sessionId"]), file=sys.stderr)

    if created.get("sourceUrl"):
        try:
            _prepare_local_copy(state, created["sourceUrl"])
            print("源码已下载到：%s" % workdir, file=sys.stderr)
        except SkillError as error:
            # 下载失败不阻断发布：没改代码时可以直接把 sourceUrl 交给发布接口
            print("警告：下载源码失败（%s），先尝试直接用 sourceUrl 发布。" % error, file=sys.stderr)
    else:
        print(
            "警告：创建接口没给 sourceUrl，无法修改源码；本地工作目录为空。",
            file=sys.stderr,
        )

    if not args.publish:
        # 默认停在本地：先给用户预览，确认后再手动 publish
        _print_preview_steps(workdir)
        _save_session_record(state, "create")
        print(json.dumps(_public_state(state), ensure_ascii=False, indent=2))
        return 0

    if args.build and os.path.isfile(os.path.join(workdir, "package.json")):
        _build_project(workdir)

    published = _publish_for_state(state, use_original_first=not args.force_upload)
    state["publishUrl"] = published.get("publishUrl")
    _save_state(state)

    # 列表校验；失败不影响已经拿到的 publishUrl，但会提示
    try:
        remote = _verify_publish(
            state["applicationId"], state["name"], state["notebookId"], state["publishUrl"]
        )
        if remote.get("publishUrl"):
            state["publishUrl"] = remote["publishUrl"]
            _save_state(state)
    except SkillError as error:
        print("提示：%s" % error, file=sys.stderr)

    _save_session_record(state, "create")
    print(json.dumps(_public_state(state), ensure_ascii=False, indent=2))
    return 0


PLACEHOLDER_CLIENT_ID = "lf_48e91437-58b4-4aeb-91ce-daefd8a70212"


def _ensure_env_files(project_root):
    """发布侧要求 .env 和 .env.local 都存在且含 clientId（见 verifyProjectEnv）。

    下载包理论上两个文件都已填好；这里只做兜底：缺一个就复制另一个，
    仍是模板占位符时直接报错，避免上传后才在服务端拿到一个看不出原因的 424。
    """
    env_path = os.path.join(project_root, ".env")
    env_local_path = os.path.join(project_root, ".env.local")
    has_env = os.path.isfile(env_path)
    has_env_local = os.path.isfile(env_local_path)
    if not has_env and not has_env_local:
        raise SkillError(
            "源码包里没有 .env / .env.local。发布接口会校验 clientId，缺了会被拒。"
            "请重新下载创建接口给的源码包，不要用别处拷来的代码。"
        )
    if not has_env:
        shutil.copyfile(env_local_path, env_path)
    if not has_env_local:
        shutil.copyfile(env_path, env_local_path)

    for path in (env_path, env_local_path):
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except OSError as error:
            raise SkillError("读取环境文件失败：%s" % error)
        if PLACEHOLDER_CLIENT_ID in content:
            raise SkillError(
                "源码包里的 NEXT_PUBLIC_LINKFOX_SSO_CLIENT_ID 还是模板占位符，"
                "说明这份代码不是从创建接口下载的（或已被覆盖）。"
                "请用创建接口返回的 sourceUrl 重新下载后再改。"
            )


def _publish_for_state(state, *, use_original_first):
    """优先复用创建接口给的 sourceUrl；失败再走「下载 → 打包 → 上传 → 发布」。"""
    session_id = state.get("sessionId")
    if not session_id:
        raise SkillError("状态里没有 sessionId，无法发布")

    if use_original_first and state.get("sourceUrl"):
        try:
            print("尝试直接发布创建接口返回的源码包（内容已填好 ID）…", file=sys.stderr)
            return _publish(session_id, state["sourceUrl"])
        except SkillError as error:
            print("直接发布失败，改为重新打包上传：%s" % error, file=sys.stderr)

    workdir = state.get("workdir")
    if not workdir or not os.path.isdir(workdir):
        raise SkillError("本地工作目录不存在：%s" % workdir)
    project_root = _find_project_root(workdir)
    _ensure_env_files(project_root)
    _assert_no_key_in_publish_env(project_root)

    archive = os.path.join(
        os.path.dirname(workdir),
        _ascii_token(state.get("applicationId"), "app") + "-publish.tar.gz",
    )
    _pack_project(workdir, archive)
    print("已打包：%s" % archive, file=sys.stderr)
    source_url = _upload_package(archive)
    print("已上传：%s" % source_url, file=sys.stderr)
    return _publish(session_id, source_url)


def _state_from_app(app):
    application_id = app.get("applicationId")
    state = None
    if application_id:
        path = _state_path_for(application_id)
        if os.path.isfile(path):
            state = _read_json(path)
    if state is None:
        state = {
            "applicationId": application_id,
            "sessionId": app.get("sessionId"),
            "name": app.get("name"),
            "notebookId": app.get("notebookId"),
            "notebookName": app.get("notebookName"),
            "templateId": "",
            "workdir": _default_workdir(app.get("templateId") or "app", application_id),
            "sourceUrl": None,
            "publishUrl": app.get("publishUrl"),
            "createdAt": _now(),
        }
        _save_state(state)
    return state


def _public_state(state):
    keys = (
        "applicationId",
        "sessionId",
        "name",
        "notebookId",
        "notebookName",
        "templateId",
        "templateName",
        "publishUrl",
        "workdir",
        "createdAt",
        "updatedAt",
    )
    return {key: state.get(key) for key in keys if key in state}


def cmd_dev(args):
    """本地预览：启动 pnpm dev（Node server），未登录走 SSO。"""
    state = _find_state(args)
    workdir = state.get("workdir") or ""
    if not workdir or not os.path.isdir(workdir):
        raise SkillError("本地工作目录不存在：%s" % workdir)
    project_root = _find_project_root(workdir)

    if not (
        os.path.isfile(os.path.join(project_root, ".env"))
        or os.path.isfile(os.path.join(project_root, ".env.local"))
    ):
        print("警告：没有 .env / .env.local，可能是源码包下载不完整。", file=sys.stderr)

    pnpm = shutil.which("pnpm")
    if not pnpm:
        raise SkillError(
            "找不到 pnpm。本地预览必须在用户电脑上执行；"
            "请先安装 Node/pnpm，不要在远端沙箱里跑。"
        )
    if args.install or not os.path.isdir(os.path.join(project_root, "node_modules")):
        _run_command([pnpm, "install", "--frozen-lockfile", "--prefer-offline"], project_root)

    port = str(args.port or 3000)
    print("本地预览：http://localhost:%s" % port, file=sys.stderr)
    print(
        "应用默认直连 https://agent-studio-api.linkfox.vip/tool-gateway；"
        "未登录会走 SSO，用 LinkFox 账号登录即可。",
        file=sys.stderr,
    )
    print("如果页面卡在「正在准备登录」，请用 localhost 打开，不要用 127.0.0.1。", file=sys.stderr)
    print("改代码会热更新；不要每改一点就发布。", file=sys.stderr)
    try:
        completed = subprocess.run([pnpm, "dev", "--", "-p", port], cwd=project_root, check=False)
    except FileNotFoundError:
        raise SkillError("无法启动 pnpm dev：找不到 " + pnpm)
    return completed.returncode


def cmd_publish(args):
    _require_api_key()
    state = _find_state(args)
    if not state.get("sessionId"):
        raise SkillError("状态里没有 sessionId，无法发布；请用 create 重新建一个应用")

    workdir = state.get("workdir") or os.path.abspath(os.path.expanduser(args.dir or ""))
    if not workdir or not os.path.isdir(workdir):
        raise SkillError("本地工作目录不存在：%s" % workdir)
    state["workdir"] = workdir

    if args.build:
        _build_project(_find_project_root(workdir))

    published = _publish_for_state(state, use_original_first=False)
    state["publishUrl"] = published.get("publishUrl")
    _save_state(state)

    try:
        remote = _verify_publish(
            state["applicationId"], state["name"], state["notebookId"], state["publishUrl"]
        )
        if remote.get("publishUrl"):
            state["publishUrl"] = remote["publishUrl"]
            _save_state(state)
    except SkillError as error:
        print("提示：%s" % error, file=sys.stderr)

    _save_session_record(state, "publish")
    print(json.dumps(_public_state(state), ensure_ascii=False, indent=2))
    return 0


def cmd_status(args):
    _require_api_key()
    state = None
    if args.dir or args.state or args.application_id or args.name:
        state = _find_state(args)
    if state is None:
        raise SkillError("需要 --dir / --state / --application-id / --name 之一")

    app = None
    if state.get("applicationId"):
        for row in _list_applications(name=state.get("name") or "", notebook_id=state.get("notebookId") or ""):
            if str(row.get("applicationId")) == str(state.get("applicationId")):
                app = row
                break
    else:
        app = _find_existing_app(state.get("name") or "", state.get("notebookId") or "")

    if app:
        state["publishUrl"] = app.get("publishUrl")
        state["sessionId"] = state.get("sessionId") or app.get("sessionId")
        _save_state(state)
    print(json.dumps(_public_state(state), ensure_ascii=False, indent=2))
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser():
    parser = argparse.ArgumentParser(
        prog="create_app.py",
        description="LinkFox 应用开发一条龙：模板清单 / 新建 / 发布 / 修改",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("templates", help="列出应用模板")
    p.add_argument("--platform", default="", help="amazon / walmart / tiktok / ozon，留空不限")
    p.add_argument("--stage", default="", help="selection / procurement / listing / fulfillment，留空不限")
    p.add_argument("--keyword", default="", help="按名称/简介模糊搜索")
    p.add_argument("--first-page", action="store_true", help="只取第一页（默认拉全）")
    p.add_argument("--brief", action="store_true", help="不显示简介")
    p.add_argument("--json", action="store_true", help="输出 JSON")
    p.set_defaults(func=cmd_templates)

    p = sub.add_parser("apps", help="列出我的应用（修改已有应用时用）")
    p.add_argument("--name", default="", help="应用名，包含匹配")
    p.add_argument("--notebook", default="", help="多维表名，包含匹配")
    p.add_argument("--source", default="", choices=["", "mine", "shared", "all"], help="mine / shared / all")
    p.add_argument("--json", action="store_true", help="输出 JSON")
    p.set_defaults(func=cmd_apps)

    p = sub.add_parser("create", help="按模板新建应用 + 下载源码（默认不发布）")
    p.add_argument("--template", required=True, help="模板 resourceId（如 amazon-search）")
    p.add_argument("--name", required=True, help="应用名")
    p.add_argument("--notebook-id", default="", help="nbk 开头的多维表 id")
    p.add_argument("--notebook-name", default="", help="多维表名；不存在会自动创建")
    p.add_argument(
        "--dir",
        default="",
        help="本地工作目录，默认 ./linkfox-apps/<templateId>-<applicationId>（纯英文）",
    )
    p.add_argument("--build", action="store_true", help="发布前在本机跑 pnpm install + pnpm build 校验")
    p.add_argument("--force-upload", action="store_true", help="始终重新打包上传，不复用创建接口的 sourceUrl")
    p.add_argument("--force-new", action="store_true", help="同名应用已存在时仍然新建")
    p.add_argument("--publish", action="store_true", help="建好后立即发布（默认不发布，先本地 pnpm dev 预览）")
    # 兼容旧参数：现在默认就不发布，--no-publish 等同于默认行为
    p.add_argument("--no-publish", action="store_true", help=argparse.SUPPRESS)
    p.set_defaults(func=cmd_create)

    p = sub.add_parser("dev", help="本地预览（pnpm dev，未登录走 SSO）")
    p.add_argument("--dir", default="", help="本地工作目录")
    p.add_argument("--state", default="", help="状态文件路径")
    p.add_argument("--application-id", default="", help="应用 id（apl 开头）")
    p.add_argument("--name", default="", help="应用名")
    p.add_argument("--port", type=int, default=3000, help="本地端口，默认 3000")
    p.add_argument("--install", action="store_true", help="强制先跑 pnpm install")
    p.set_defaults(func=cmd_dev)

    p = sub.add_parser("publish", help="改完本地代码后重新发布")
    p.add_argument("--dir", default="", help="本地工作目录")
    p.add_argument("--state", default="", help="状态文件路径")
    p.add_argument("--application-id", default="", help="应用 id（apl 开头）")
    p.add_argument("--name", default="", help="应用名")
    p.add_argument("--build", action="store_true", help="发布前在本机跑 pnpm install + pnpm build 校验")
    p.set_defaults(func=cmd_publish)

    p = sub.add_parser("status", help="查看应用状态")
    p.add_argument("--dir", default="", help="本地工作目录")
    p.add_argument("--state", default="", help="状态文件路径")
    p.add_argument("--application-id", default="", help="应用 id（apl 开头）")
    p.add_argument("--name", default="", help="应用名")
    p.set_defaults(func=cmd_status)

    return parser


def _ensure_api_key_alias():
    """linkfox_paths 只读 LINKFOX_AGENT_API_KEY；这里兼容老变量名 LINKFOXAGENT_API_KEY。"""
    if not os.environ.get("LINKFOX_AGENT_API_KEY"):
        legacy = os.environ.get("LINKFOXAGENT_API_KEY")
        if legacy:
            os.environ["LINKFOX_AGENT_API_KEY"] = legacy


def main(argv=None):
    _ensure_api_key_alias()
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args) or 0
    except SkillError as error:
        print("错误：%s" % error, file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("已取消", file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.exit(main())
