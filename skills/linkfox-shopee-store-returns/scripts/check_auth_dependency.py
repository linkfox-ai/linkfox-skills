#!/usr/bin/env python3
"""
Dependency Check - linkfox-shopee-store-returns
=================================================

探测是否已安装 `linkfox-shopee-store-auth`。
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

REQUIRED_SKILL = "linkfox-shopee-store-auth"
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


def locate_dependency() -> Path | None:
    for root in candidate_skill_roots():
        target = root / REQUIRED_SKILL / "SKILL.md"
        if target.is_file():
            return target
    return None


def searched_locations_for_report() -> list[str]:
    return [str(p) for p in candidate_skill_roots()]


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
            f"linkfox-shopee-store-returns 依赖 `{REQUIRED_SKILL}`，"
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
