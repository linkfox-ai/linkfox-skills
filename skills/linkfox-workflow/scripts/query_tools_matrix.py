#!/usr/bin/env python3
"""linkfox-workflow · 查 Linkfox 工具矩阵:有哪些工具、某个端点怎么调。

文档按会话缓存在 `<session>/data/tools-matrix/`,同一会话内重复查询不重复下载。

CLI:
  python scripts/query_tools_matrix.py catalog [--keyword <词> ...] [--slug <skill 名>] [--include-planned]
  python scripts/query_tools_matrix.py endpoints --key <工具 key>
  python scripts/query_tools_matrix.py endpoint --key <工具 key> (--index <编号> | --path <端点路径或端点标识>)
  [--refresh]                       # 忽略会话缓存,重新下载

输出:
  catalog    每行一个工具:key | 标题 | 平台 | 类型 | 状态 | 关联 skill
  endpoints  每行一个端点:#编号 方法 路径 [| 端点标识=<标识>] [| 非网关:<host>] [| 标题] | 关联 skill
  endpoint   该端点完整一节(请求地址 / 方式 / 参数表 / 响应结构 / 示例)

退出码:0 成功;1 网络失败;3 未找到工具或端点;4 写盘失败;64 CLI 用法错;65 内容非法。
"""

from __future__ import annotations

import argparse
import gzip
import json
import os
import re
import sys
import tempfile
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
from linkfox_paths import session_root  # type: ignore  # noqa: E402


MATRIX_BASE = "https://agent-files.linkfox.com/skills/_tools_matrix/api-docs"
CACHE_SUBDIR = os.path.join("data", "tools-matrix")
_KEY_RE = re.compile(r"^[a-z0-9_]{1,64}$")
_FILE_RE = re.compile(r"^tools/[a-z0-9_]{1,64}\.md$")
_HEADING_RE = re.compile(r"^## +([A-Z]+) +(/\S+)\s*$")
# 文档里字段行有中英两种标签,分隔符有 `：` / `:` / 损坏成 `?` 三种。
_SEP = r"\*{0,2}\s*[:：?]\s*"
_URL_RE = re.compile(r"(?:请求地址|Request URL)" + _SEP + r"`?https?://([^/\s`]+)(/[^\s`]*)")
_METHOD_RE = re.compile(r"(?:请求方式|Request method)" + _SEP + r"([A-Z]+)")
_IDENT_RE = re.compile(r"(?:端点标识|Endpoint identifier)" + _SEP + r"`([^`]+)`")
_SKILL_RE = re.compile(r"(?:对应Skill|Corresponding skills?)" + _SEP + r"(.+)")
_SLUG_RE = re.compile(r"`([A-Za-z0-9_-]+)`")
GATEWAY_HOST = "tool-gateway.linkfox.com"


def _die(msg: str, code: int = 1) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Query the Linkfox tools matrix")
    p.add_argument("--refresh", action="store_true", help="忽略会话缓存,重新下载")
    sub = p.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("catalog", help="列出工具")
    c.add_argument("--keyword", action="append", default=[], help="按标题/描述/平台/类型过滤,可重复,全部命中才算")
    c.add_argument("--slug", default="", help="按关联 skill 名反查工具")
    c.add_argument("--include-planned", action="store_true", help="同时列出未上线的工具")

    e = sub.add_parser("endpoints", help="列出某工具的全部端点")
    e.add_argument("--key", required=True)

    one = sub.add_parser("endpoint", help="输出某个端点的完整文档")
    one.add_argument("--key", required=True)
    pick = one.add_mutually_exclusive_group(required=True)
    pick.add_argument("--index", type=int, help="endpoints 清单里的编号(最准确)")
    pick.add_argument("--path", help="端点路径或端点标识")

    args = p.parse_args(argv)
    key = getattr(args, "key", None)
    if key is not None and not _KEY_RE.match(key):
        _die(f"--key 只能是小写字母、数字、下划线:{key}", 64)
    if getattr(args, "path", None) is not None:
        args.path = "/" + args.path.strip().lstrip("/")
        if args.path == "/":
            _die("--path 不能为空", 64)
    return args


def _decode(raw: bytes) -> str:
    if raw[:2] == b"\x1f\x8b":
        raw = gzip.decompress(raw)
    return raw.decode("utf-8")


def _download(rel: str) -> str:
    req = Request(
        f"{MATRIX_BASE}/{rel}",
        headers={"Accept-Encoding": "gzip", "User-Agent": "LinkFox-Workflow-Agent/1.0"},
    )
    try:
        with urlopen(req, timeout=60) as resp:
            return _decode(resp.read())
    except HTTPError as exc:
        if exc.code == 404:
            _die(f"工具矩阵里没有 {rel}", 3)
        _die(f"下载 {rel} 失败:HTTP {exc.code}", 1)
    except (URLError, TimeoutError, OSError) as exc:
        _die(f"下载 {rel} 失败:{exc}", 1)
    except UnicodeDecodeError:
        _die(f"{rel} 不是 UTF-8 文本", 65)
    raise AssertionError("unreachable")


def _write_atomic(path: str, content: str) -> None:
    tmp_path = ""
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=os.path.dirname(path),
            prefix=".tools-matrix-", suffix=".tmp", delete=False,
        ) as f:
            tmp_path = f.name
            f.write(content)
        os.replace(tmp_path, path)
    except OSError as exc:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)
        _die(f"写入缓存失败:{exc}", 4)


def _fetch(rel: str, refresh: bool) -> str:
    """会话内缓存:命中就读本地,否则下载并落到会话目录。"""
    cache_path = os.path.join(session_root(), CACHE_SUBDIR, rel.replace("/", "__"))
    if not refresh and os.path.isfile(cache_path):
        with open(cache_path, encoding="utf-8") as f:
            return f.read()
    text = _download(rel)
    _write_atomic(cache_path, text)
    return text


def _load_catalog(refresh: bool) -> list[dict[str, Any]]:
    try:
        items = json.loads(_fetch("catalog.json", refresh)).get("items")
    except json.JSONDecodeError:
        _die("catalog.json 不是合法 JSON", 65)
    if not isinstance(items, list):
        _die("catalog.json 缺少 items 列表", 65)
    return [i for i in items if isinstance(i, dict)]


def _skill_slugs(item: dict[str, Any]) -> list[str]:
    return [s["slug"] for s in item.get("skills") or [] if isinstance(s, dict) and s.get("slug")]


def _haystack(item: dict[str, Any]) -> str:
    parts = [item.get("key"), item.get("title"), item.get("description"), item.get("vendor")]
    parts += list(item.get("platform") or []) + list(item.get("type") or [])
    parts += [s.get("name") for s in item.get("skills") or [] if isinstance(s, dict)]
    return " ".join(str(p) for p in parts if p).lower()


def filter_catalog(
    items: list[dict[str, Any]], keywords: list[str], slug: str, include_planned: bool
) -> list[dict[str, Any]]:
    out = []
    for item in items:
        if not include_planned and item.get("status") != "live":
            continue
        if slug and slug not in _skill_slugs(item):
            continue
        hay = _haystack(item)
        if any(k.strip().lower() not in hay for k in keywords if k.strip()):
            continue
        out.append(item)
    return out


def format_catalog_line(item: dict[str, Any]) -> str:
    return " | ".join([
        str(item.get("key", "")),
        str(item.get("title", "")),
        ",".join(item.get("platform") or []),
        ",".join(item.get("type") or []),
        str(item.get("status", "")),
        ",".join(_skill_slugs(item)),
    ])


def _tool_file(items: list[dict[str, Any]], key: str) -> str:
    for item in items:
        if item.get("key") == key:
            rel = str(item.get("file") or "")
            if not _FILE_RE.match(rel):
                _die(f"工具 {key} 的文档路径非法:{rel!r}", 65)
            if item.get("status") != "live":
                print(f"WARNING: 工具 {key} 状态为 {item.get('status')},还没有可调用的接口", file=sys.stderr)
            return rel
    _die(f"工具矩阵里没有 key={key};先用 catalog 子命令查 key", 3)
    raise AssertionError("unreachable")


class Section:
    """文档里的一个端点。

    `path` 是请求地址里的路径,即 LinkfoxHTTP 的 `path`;转发类接口(`developerProxy` /
    `temu/proxy`)多个端点共用一个 path,靠 `ident`(端点标识)区分。
    """

    def __init__(self, index: int, title: str, method: str, host: str, path: str, ident: str, skills: list[str], text: str):
        self.index, self.title, self.method, self.host, self.path = index, title, method, host, path
        self.ident, self.skills, self.text = ident, skills, text

    def label(self) -> str:
        parts = [f"#{self.index} " + f"{self.method} {self.path}".strip()]
        if self.ident and self.ident.strip("/") != self.path.strip("/"):
            parts.append(f"端点标识={self.ident}")
        if self.host and self.host != GATEWAY_HOST:
            parts.append(f"非网关:{self.host}")
        if self.title != f"{self.method} {self.path}":
            parts.append(self.title)
        if self.skills:
            parts.append(",".join(self.skills))
        return " | ".join(parts)


def split_sections(doc: str) -> list[Section]:
    """按 `## ` 切分出端点。取不到请求路径的 `## ` 节(前言、附录)跳过。"""
    chunks: list[list[str]] = []
    for line in doc.splitlines():
        if line.startswith("## "):
            chunks.append([line])
        elif chunks:
            chunks[-1].append(line)
    sections: list[Section] = []
    for chunk in chunks:
        text = "\n".join(chunk).rstrip()
        head = _HEADING_RE.match(chunk[0])
        url = _URL_RE.search(text)
        if not head and not url:
            continue
        method = _METHOD_RE.search(text)
        ident = _IDENT_RE.search(text)
        skill = _SKILL_RE.search(text)
        sections.append(Section(
            index=len(sections) + 1,
            title=chunk[0][3:].strip(),
            method=head.group(1) if head else (method.group(1) if method else ""),
            host=url.group(1) if url else GATEWAY_HOST,
            path=head.group(2) if head else url.group(2),
            ident=ident.group(1).strip() if ident else "",
            skills=_SLUG_RE.findall(skill.group(1)) if skill else [],
            text=text,
        ))
    return sections


def find_sections(sections: list[Section], query: str) -> list[Section]:
    """按端点标识或请求路径查找:先精确,再后缀。"""
    q = query.strip().strip("/")

    def keys(sec: Section) -> list[str]:
        return [k.strip("/") for k in (sec.ident, sec.path) if k]

    for match in (lambda k: k == q, lambda k: k.endswith("/" + q) or k == q):
        hits = [sec for sec in sections if any(match(k) for k in keys(sec))]
        # 精确命中转发入口时,一个 path 对应很多端点,只算命中了"标识等于它"的那些。
        idented = [sec for sec in hits if sec.ident and match(sec.ident.strip("/"))]
        if idented:
            return idented
        if hits:
            return hits
    return []


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    items = _load_catalog(args.refresh)

    if args.cmd == "catalog":
        hits = filter_catalog(items, args.keyword, args.slug.strip(), args.include_planned)
        if not hits:
            print("没有匹配的工具")
            return 3
        for item in hits:
            print(format_catalog_line(item))
        return 0

    sections = split_sections(_fetch(_tool_file(items, args.key), args.refresh))
    if not sections:
        _die(f"工具 {args.key} 的文档里没有可识别的端点", 65)

    if args.cmd == "endpoints":
        for sec in sections:
            print(sec.label())
        return 0

    if args.index is not None:
        if not 1 <= args.index <= len(sections):
            _die(f"--index 超出范围:工具 {args.key} 共 {len(sections)} 个端点", 3)
        print(sections[args.index - 1].text)
        return 0

    hits = find_sections(sections, args.path)
    if not hits:
        _die(f"工具 {args.key} 里没有端点 {args.path};先用 endpoints 子命令看清单", 3)
    if len(hits) > 1:
        _die(
            f"{args.path} 匹配到 {len(hits)} 个端点,请用 --index <编号> 选一个:\n"
            + "\n".join(sec.label() for sec in hits[:20]),
            3,
        )
    print(hits[0].text)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BrokenPipeError:  # 下游管道提前关闭(如 | head)不算失败
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        sys.exit(0)
