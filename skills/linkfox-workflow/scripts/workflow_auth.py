"""linkfox-workflow · 鉴权失败的诊断提示(不回显密钥)。

脚本从不打印 API Key,这是对的;但代价是"鉴权失败"一个症状背后有好几种根因(用错了 key
类型、变量值带空格或引号、变量没注入),调用方只看到一个裸的 401。这里在 401 / 403 时补一句
针对性的排查提示 —— 只说"怎么查",不输出 key 的任何内容。
"""

from __future__ import annotations

import re

_AUTH_FAIL_RE = re.compile(r"HTTP (401|403)\b")

AUTH_HINT = (
    "鉴权失败排查:① 确认用的是 LinkFox Agent API Key(环境变量 LINKFOX_AGENT_API_KEY,"
    "通常以 sk- 开头),不是登录态 token / JWT;② 值里不要带引号,等号两侧不要有空格;"
    "③ 在 pod 里由平台注入,本地调试才需要自己 export。脚本不会打印 key 的值,也不要把它贴进对话"
)


def with_auth_hint(message: str) -> str:
    """消息里出现 HTTP 401/403 时追加排查提示,否则原样返回。"""
    if _AUTH_FAIL_RE.search(message or "") and AUTH_HINT not in message:
        return f"{message}\n{AUTH_HINT}"
    return message


def clean_key(value: str) -> str:
    """去掉首尾空白与成对引号 —— `.env` 里写成 KEY="sk-..." 或等号后多空格是最常见的误配。"""
    v = (value or "").strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in {'"', "'"}:
        v = v[1:-1].strip()
    return v
