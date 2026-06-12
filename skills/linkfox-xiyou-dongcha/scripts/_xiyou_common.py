#!/usr/bin/env python3
"""Shared helpers for 西柚找词 (Xiyou) LinkFox gateway calls."""

import json
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

GATEWAY_BASE = "https://tool-gateway.linkfox.com/xiyou"
TIMEOUT_SEC = 60

LINKFOX_KEY_DOC = (
    "https://skill.linkfox.com/linkfoxskills/guide.htm"
)
XIYOU_OPENAPI_PORTAL = (
    "https://www.xydc.com/openapi?xiyou-insights-web=%2Fopenapi"
)


def get_linkfox_api_key() -> str:
    key = os.environ.get("LINKFOXAGENT_API_KEY", "").strip()
    if not key:
        print(
            "未配置 LinkFox API Key。请先完成授权：\n"
            f"1. 前往 {LINKFOX_KEY_DOC} 获取 Key\n"
            "2. 设置环境变量：export LINKFOXAGENT_API_KEY=your-key-here",
            file=sys.stderr,
        )
        sys.exit(1)
    return key


def get_xiyou_credentials() -> tuple[str, str]:
    client_id = os.environ.get("XIYOU_CLIENT_ID", "").strip()
    client_secret = os.environ.get("XIYOU_CLIENT_SECRET", "").strip()
    missing = []
    if not client_id:
        missing.append("XIYOU_CLIENT_ID")
    if not client_secret:
        missing.append("XIYOU_CLIENT_SECRET")
    if missing:
        print(
            "未配置西柚找词 OpenAPI 凭证。请在环境变量中设置：\n"
            f"  export XIYOU_CLIENT_ID=<16位 Client ID>\n"
            f"  export XIYOU_CLIENT_SECRET=<24位 Client Secret>\n"
            f"凭证获取地址：{XIYOU_OPENAPI_PORTAL}\n"
            f"缺少：{', '.join(missing)}",
            file=sys.stderr,
        )
        sys.exit(1)
    return client_id, client_secret


def merge_auth(params: dict) -> dict:
    client_id, client_secret = get_xiyou_credentials()
    payload = dict(params)
    payload["clientId"] = client_id
    payload["clientSecret"] = client_secret
    return payload


def call_xiyou_api(route: str, params: dict) -> dict:
    api_key = get_linkfox_api_key()
    url = f"{GATEWAY_BASE}/{route.lstrip('/')}"
    body = json.dumps(merge_auth(params), ensure_ascii=False).encode("utf-8")
    req = Request(
        url,
        data=body,
        headers={
            "Authorization": api_key,
            "Content-Type": "application/json",
            "User-Agent": "LinkFox-Skill/1.0",
        },
        method="POST",
    )
    try:
        with urlopen(req, timeout=TIMEOUT_SEC) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as e:
        detail = e.read().decode("utf-8") if e.fp else ""
        return {"error": f"HTTP {e.code}: {e.reason}", "details": detail}
    except URLError as e:
        return {"error": f"Connection failed: {e.reason}"}
