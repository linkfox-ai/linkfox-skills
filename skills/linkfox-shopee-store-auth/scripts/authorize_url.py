#!/usr/bin/env python3
"""
Shopee Store Authorization URL Generator - LinkFox Skill
Calls the /shopee/authorizeUrl endpoint to generate authorization URL

Usage:
  python authorize_url.py '{"shopName": "My Shop", "region": "cn"}'
  python authorize_url.py '{"region": "global"}'
"""

import json
import os
import platform
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

from _lf_output import emit_result, lf_inline_flag

# 生产默认走 tool-gateway.linkfox.com；开发/测试期可 export SHOPEE_API_BASE_URL=<url> 覆盖
API_BASE_URL = (os.environ.get("LINKFOX_TOOL_GATEWAY") or os.environ.get("SHOPEE_API_BASE_URL") or "https://tool-gateway.linkfox.com").rstrip("/")
API_ENDPOINT = f"{API_BASE_URL}/shopee/authorizeUrl"


def get_api_key():
    """
    获取配置在环境变量的API Key。
    如果获取不到，按 SKILL.md 的 **## 解决认证和积分问题** 处理。
    """
    key = os.environ.get("LINKFOX_AGENT_API_KEY") or os.environ.get("LINKFOXAGENT_API_KEY")
    if not key:
        print(
            "API Key 未配置",
            file=sys.stderr,
        )
        sys.exit(1)
    return key


def call_api(params: dict) -> dict:
    api_key = get_api_key()
    data = json.dumps(params).encode("utf-8")
    req = Request(
        API_ENDPOINT,
        data=data,
        headers={
            "Authorization": api_key,
            "Content-Type": "application/json",
            "User-Agent": "LinkFox-Skill/1.0",
        },
        method="POST",
    )
    try:
        with urlopen(req, timeout=60) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as e:
        body = e.read().decode("utf-8") if e.fp else ""
        return {"error": f"HTTP {e.code}: {e.reason}", "details": body}
    except URLError as e:
        return {"error": f"Connection failed: {e.reason}"}


def main():
    if len(sys.argv) < 2:
        print("Usage: authorize_url.py '<JSON parameters>'", file=sys.stderr)
        print(
            'Example: authorize_url.py \'{"shopName": "My Shop", "region": "cn"}\'',
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        params = json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        print(f"Invalid parameter format: {e}", file=sys.stderr)
        sys.exit(1)

    if "region" not in params or not params.get("region"):
        print("Note: 'region' not provided, defaulting to 'cn' (see SKILL.md)", file=sys.stderr)
        params["region"] = "cn"
    if params["region"] not in ("cn", "global", "br"):
        print(
            f"Error: 'region' must be one of cn / global / br, got {params['region']!r}",
            file=sys.stderr,
        )
        sys.exit(1)

    if "shopName" in params and isinstance(params["shopName"], str):
        shop_name = params["shopName"].strip()
        if shop_name:
            params["shopName"] = shop_name
        else:
            del params["shopName"]

    result = call_api(params)
    emit_result(result, lf_inline_flag())

    if "authorizeUrl" in result:
        url = result["authorizeUrl"]
        file_path = _save_url_to_file(url)
        clipboard_ok = _copy_to_clipboard(url)

        print("\n✓ Authorization URL generated.", file=sys.stderr)
        if params.get("shopName"):
            print(f"店铺名: {params['shopName']}", file=sys.stderr)
        if clipboard_ok:
            print("✓ 已写入剪贴板 —— 浏览器地址栏直接 Ctrl+V / Cmd+V", file=sys.stderr)
        if file_path:
            print(f"✓ 已写入文件：{file_path}", file=sys.stderr)

        if clipboard_ok or file_path:
            print(
                "请从上面的剪贴板或文件复制 URL；"
                "勿直接从终端/聊天窗口复制，软换行可能破坏 URL。",
                file=sys.stderr,
            )
        else:
            print(
                "\n⚠️  剪贴板与文件均不可用，仅能以文本形式输出 URL。\n"
                "   如 agent 调用本脚本，请改用 stdout JSON 的 `authorizeUrl` 字段。",
                file=sys.stderr,
            )
            print(f"\n  {url}\n", file=sys.stderr)


def _save_url_to_file(url: str):
    try:
        cache_dir = Path.home() / ".cache" / "linkfox"
        cache_dir.mkdir(parents=True, exist_ok=True)
        f = cache_dir / "last_shopee_authorize_url.txt"
        f.write_text(url, encoding="utf-8", newline="")
        return str(f)
    except Exception:
        try:
            f = Path(tempfile.gettempdir()) / "linkfox_last_shopee_authorize_url.txt"
            f.write_text(url, encoding="utf-8", newline="")
            return str(f)
        except Exception:
            return None


def _copy_to_clipboard(url: str) -> bool:
    plat = platform.system()
    try:
        if plat == "Windows":
            p = subprocess.run(["clip.exe"], input=url, text=True, check=True, timeout=5)
            return p.returncode == 0
        if plat == "Darwin":
            p = subprocess.run(["pbcopy"], input=url, text=True, check=True, timeout=5)
            return p.returncode == 0
        for cmd in (["xclip", "-selection", "clipboard"], ["xsel", "--clipboard", "--input"], ["wl-copy"]):
            try:
                p = subprocess.run(cmd, input=url, text=True, check=True, timeout=5)
                if p.returncode == 0:
                    return True
            except (FileNotFoundError, subprocess.CalledProcessError):
                continue
        return False
    except Exception:
        return False


if __name__ == "__main__":
    main()
