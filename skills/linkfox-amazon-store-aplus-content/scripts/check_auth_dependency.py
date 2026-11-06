#!/usr/bin/env python3
"""
Dependency Check - linkfox-amazon-store-aplus-content
======================================================

本脚本用于判断当前运行环境里是否已经安装 / 加载了依赖 skill
`linkfox-amazon-store-auth`（与 `linkfox-amazon-store-report` 等共用同一检查逻辑）。

用法:
    python check_auth_dependency.py            # 默认检查
    python check_auth_dependency.py --json     # 以 JSON 输出结果

退出码约定（供 agent 程序化解析）:
    0   → 依赖已满足（找到 linkfox-amazon-store-auth 的 SKILL.md）
    42  → DEPENDENCY_MISSING: 未找到依赖 skill，agent 需要触发安装流程

stderr 结构化信号:
    - 若依赖缺失，stderr 第一行会以 `DEPENDENCY_MISSING:` 开头，
      后跟 JSON payload，包含所需 skill 名与建议的安装动作。
    - 成功时 stderr 以 `DEPENDENCY_OK:` 开头。

注意:
    这是一个**不联网**的本地探测脚本。它只检查文件系统上常见的
    skill 安装路径（含 **OpenClaw**、**Hermes Agent** 的常见布局）；
    真正的"能不能调授权接口"取决于依赖 skill 的脚本是否可执行——
    这一点由网关在业务请求中按 sellerId + region 解析授权后校验；
    当前 A+ 业务脚本不会另行调用 `/spApi/storeTokens`。

    OpenClaw 参考: workspace 下 `<workspace>/skills`、`<workspace>/.agents/skills`，
    以及 `~/.openclaw/skills`、`~/.agents/skills`（与官方文档优先级一致）。

    Hermes Agent 参考: `~/.hermes/skills/<category>/<skill-name>/SKILL.md`，
    以及 `~/.hermes/plugins/<plugin>/skills/<skill-name>/SKILL.md`；
    额外目录可在 `~/.hermes/config.yaml` 的 `skills.external_dirs` 中配置，
    本脚本无法解析 YAML，请通过环境变量 `HERMES_SKILLS_EXTERNAL_DIRS`（冒号
    或分号分隔的多个路径）或通用的 `LINKFOX_SKILLS_DIR` / `SKILLS_DIR` 注入。
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

REQUIRED_SKILL = "linkfox-amazon-store-auth"
# 依赖目录同时支持 linkfox-amazon-store-auth 与 linkfox-amazon-spapi-auth。
_AUTH_SKILL_DIR_ALIASES = ("linkfox-amazon-store-auth", "linkfox-amazon-spapi-auth")
DEPENDENCY_EXIT_CODE = 42


def _split_path_list(raw: str | None) -> list[Path]:
    """按 OS 路径分隔符拆分（Windows 为 `;`，Unix 为 `:`），避免误拆盘符。"""
    if not raw or not raw.strip():
        return []
    parts = [p.strip() for p in raw.split(os.pathsep) if p.strip()]
    return [Path(p).expanduser() for p in parts]


def candidate_skill_roots() -> list[Path]:
    """按常见的 skill 存放位置，由近到远返回候选根目录（扁平：root/<skill>/SKILL.md）。"""
    roots: list[Path] = []

    for env_var in ("LINKFOX_SKILLS_DIR", "SKILLS_DIR", "CURSOR_SKILLS_DIR"):
        p = os.environ.get(env_var)
        if p:
            roots.append(Path(p).expanduser())

    roots.extend(_split_path_list(os.environ.get("HERMES_SKILLS_EXTERNAL_DIRS")))

    for env_var in ("OPENCLAW_WORKSPACE", "OPENCLAW_ROOT", "OPENCLAW_WORKDIR"):
        ws = os.environ.get(env_var)
        if ws:
            w = Path(ws).expanduser()
            roots.append(w / "skills")
            roots.append(w / ".agents" / "skills")

    oc_skills = os.environ.get("OPENCLAW_SKILLS_DIR")
    if oc_skills:
        roots.append(Path(oc_skills).expanduser())

    try:
        cwd = Path.cwd()
        roots.append(cwd / "skills")
        roots.append(cwd / ".agents" / "skills")
    except OSError:
        pass

    here = Path(__file__).resolve()
    if len(here.parents) >= 3:
        roots.append(here.parents[2])

    home = Path.home()
    roots.extend([
        home / ".claude" / "skills",
        home / ".cursor" / "skills",
        home / ".cursor" / "skills-cursor",
        home / ".linkfox" / "skills",
    ])

    roots.extend([
        home / ".openclaw" / "skills",
        home / ".hermes" / "skills",
    ])

    seen: set[Path] = set()
    unique: list[Path] = []
    for r in roots:
        try:
            rr = r.resolve()
        except OSError:
            rr = r
        if rr not in seen:
            seen.add(rr)
            unique.append(r)
    return unique


def _hermes_category_skill_md(hermes_skills_root: Path, skill_dir_name: str) -> Path | None:
    if not hermes_skills_root.is_dir():
        return None
    for category_dir in sorted(hermes_skills_root.iterdir()):
        if not category_dir.is_dir():
            continue
        name = category_dir.name
        if name.startswith(".") or name == ".hub":
            continue
        candidate = category_dir / skill_dir_name / "SKILL.md"
        if candidate.is_file():
            return candidate
    return None


def _hermes_plugin_skill_md(home: Path, skill_dir_name: str) -> Path | None:
    plugins_root = home / ".hermes" / "plugins"
    if not plugins_root.is_dir():
        return None
    for plugin_dir in sorted(plugins_root.iterdir()):
        if not plugin_dir.is_dir():
            continue
        candidate = plugin_dir / "skills" / skill_dir_name / "SKILL.md"
        if candidate.is_file():
            return candidate
    return None


def locate_dependency() -> Path | None:
    home = Path.home()

    for skill_dir_name in _AUTH_SKILL_DIR_ALIASES:
        for root in candidate_skill_roots():
            target = root / skill_dir_name / "SKILL.md"
            if target.is_file():
                return target

        hermes_default = home / ".hermes" / "skills"
        found = _hermes_category_skill_md(hermes_default, skill_dir_name)
        if found is not None:
            return found

        hsh = os.environ.get("HERMES_SKILLS_HOME")
        if hsh:
            found = _hermes_category_skill_md(Path(hsh).expanduser(), skill_dir_name)
            if found is not None:
                return found

        found = _hermes_plugin_skill_md(home, skill_dir_name)
        if found is not None:
            return found

    return None


def searched_locations_for_report() -> list[str]:
    home = Path.home()
    out: list[str] = [str(p) for p in candidate_skill_roots()]
    out.append(str(home / ".hermes" / "skills"))
    out.append(str(home / ".hermes" / "plugins"))
    hsh = os.environ.get("HERMES_SKILLS_HOME")
    if hsh:
        out.append(str(Path(hsh).expanduser()))
    seen: set[str] = set()
    unique: list[str] = []
    for s in out:
        if s not in seen:
            seen.add(s)
            unique.append(s)
    return unique


def emit(as_json: bool, ok: bool, payload: dict) -> None:
    prefix = "DEPENDENCY_OK:" if ok else "DEPENDENCY_MISSING:"
    body = json.dumps(payload, ensure_ascii=False)
    if as_json:
        out = dict(payload)
        out["status"] = "ok" if ok else "missing"
        print(json.dumps(out, ensure_ascii=False, indent=2))
    print(f"{prefix} {body}", file=sys.stderr)


def main() -> None:
    parser = argparse.ArgumentParser(description="Check required dependency skill availability.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON on stdout.")
    args = parser.parse_args()

    found = locate_dependency()

    if found is not None:
        emit(
            as_json=args.json,
            ok=True,
            payload={
                "skill": REQUIRED_SKILL,
                "skillMdPath": str(found),
            },
        )
        sys.exit(0)

    payload = {
        "missingSkill": REQUIRED_SKILL,
        "reason": (
            f"linkfox-amazon-store-aplus-content 依赖 `{REQUIRED_SKILL}`，"
            "但在常见 skill 安装路径下未找到其 SKILL.md。"
        ),
        "searchedRoots": searched_locations_for_report(),
        "suggestedActions": [
            f"If a skill installer tool is available (e.g. install_skill / skill marketplace MCP), invoke it to install '{REQUIRED_SKILL}' immediately.",
            "Otherwise, ask the user to install the skill from https://skill.linkfox.com/ and retry.",
            "On OpenClaw: ensure the dependency is under <workspace>/skills, ~/.openclaw/skills, or ~/.agents/skills; set OPENCLAW_WORKSPACE or OPENCLAW_SKILLS_DIR if installs are non-default.",
            "On Hermes Agent: ensure the dependency is under ~/.hermes/skills/<category>/ or a plugin skills/ folder; for external_dirs from config.yaml, export HERMES_SKILLS_EXTERNAL_DIRS with OS path separators.",
            "Do NOT bypass the dependency by calling /spApi/authorizeUrl or /spApi/storeTokens directly from this skill.",
        ],
        "marketplaceUrl": "https://skill.linkfox.com/",
    }
    emit(as_json=args.json, ok=False, payload=payload)
    sys.exit(DEPENDENCY_EXIT_CODE)


if __name__ == "__main__":
    main()
