#!/usr/bin/env python3
"""
Dependency Check - linkfox-amazon-store-customer-feedback
==============================================

与 `linkfox-amazon-store-listings` / `linkfox-amazon-store-pricing` 相同逻辑：
探测是否已安装 `linkfox-amazon-store-auth`。
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

REQUIRED_SKILL = "linkfox-amazon-store-auth"
_AUTH_SKILL_DIR_ALIASES = ("linkfox-amazon-store-auth", "linkfox-amazon-spapi-auth")
DEPENDENCY_EXIT_CODE = 42


def _split_path_list(raw: str | None) -> list[Path]:
    if not raw or not raw.strip():
        return []
    parts = [p.strip() for p in raw.split(os.pathsep) if p.strip()]
    return [Path(p).expanduser() for p in parts]


def candidate_skill_roots() -> list[Path]:
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
        if category_dir.name.startswith(".") or category_dir.name == ".hub":
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
        found = _hermes_category_skill_md(home / ".hermes" / "skills", skill_dir_name)
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
            payload={"skill": REQUIRED_SKILL, "skillMdPath": str(found)},
        )
        sys.exit(0)

    payload = {
        "missingSkill": REQUIRED_SKILL,
        "reason": (
            f"linkfox-amazon-store-customer-feedback 依赖 `{REQUIRED_SKILL}`，"
            "但在常见 skill 安装路径下未找到其 SKILL.md。"
        ),
        "searchedRoots": searched_locations_for_report(),
        "suggestedActions": [
            f"If a skill installer tool is available, install '{REQUIRED_SKILL}' immediately.",
            "Otherwise ask the user to install from https://skill.linkfox.com/ and retry.",
        ],
        "marketplaceUrl": "https://skill.linkfox.com/",
    }
    emit(as_json=args.json, ok=False, payload=payload)
    sys.exit(DEPENDENCY_EXIT_CODE)


if __name__ == "__main__":
    main()
