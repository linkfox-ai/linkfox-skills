#!/usr/bin/env python3
"""
Amazon Ads Authorization URL Generator - LinkFox Skill
Calls the /amazonAds/authorizeUrl endpoint to generate authorization URL

Usage:
  python authorize_url.py '{"region": "NA", "accountName": "My Ads Account"}'
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


# 生产默认走 tool-gateway.linkfox.com；开发/测试期可 export AMAZON_ADS_BASE_URL=<url> 覆盖
API_BASE_URL = os.environ.get("AMAZON_ADS_BASE_URL") or "https://tool-gateway.linkfox.com"
API_ENDPOINT = f"{API_BASE_URL}/amazonAds/authorizeUrl"


def get_api_key():
    key = os.environ.get("LINKFOXAGENT_API_KEY")
    if not key:
        print(
            "API Key not configured. Please set the environment variable:\n"
            "  export LINKFOXAGENT_API_KEY=your-key-here",
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
            'Example: authorize_url.py \'{"region": "NA", "accountName": "My Ads Account"}\'',
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        params = json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        print(f"Invalid parameter format: {e}", file=sys.stderr)
        sys.exit(1)

    if "region" not in params or not params.get("region"):
        print("Note: 'region' not provided, defaulting to 'NA' (see SKILL.md)", file=sys.stderr)
        params["region"] = "NA"
    if params["region"] not in ("NA", "EU", "FE"):
        print(f"Error: 'region' must be one of NA / EU / FE, got {params['region']!r}", file=sys.stderr)
        sys.exit(1)

    if "accountName" not in params:
        print(
            "Error: 'accountName' is required — 授权前必须填写可识别的账号名，"
            "用于在已授权列表中区分。",
            file=sys.stderr,
        )
        sys.exit(1)
    account_name = params["accountName"]
    if not isinstance(account_name, str) or not account_name.strip():
        print(
            "Error: 'accountName' must be a non-empty string",
            file=sys.stderr,
        )
        sys.exit(1)
    params["accountName"] = account_name.strip()

    result = call_api(params)
    print(json.dumps(result, indent=2, ensure_ascii=False))

    if "authorizeUrl" in result:
        url = result["authorizeUrl"]
        # 经验：长 URL（~270 字符）在终端/聊天窗口里软换行时复制会被插入空格，导致 client_id 被污染、
        # Amazon 返回 400 StegoRuntimeOAuth2ClientManager:getClientDefinition。
        # 为此把 URL 同步落到临时文件并尝试写系统剪贴板，用户直接 Ctrl+V 即可避免这个坑。
        file_path = _save_url_to_file(url)
        clipboard_ok = _copy_to_clipboard(url)

        print("\n✓ Authorization URL generated.", file=sys.stderr)
        print(f"账号名: {params['accountName']}", file=sys.stderr)
        if clipboard_ok:
            print("✓ 已写入剪贴板 —— 浏览器地址栏直接 Ctrl+V / Cmd+V", file=sys.stderr)
        if file_path:
            print(f"✓ 已写入文件：{file_path}", file=sys.stderr)

        if clipboard_ok or file_path:
            # 有干净路径可用就不再裸打印 URL，避免终端软换行污染 client_id
            print(
                "请从上面的剪贴板或文件复制 URL；"
                "勿直接从终端/聊天窗口复制，软换行可能插入空格并污染 client_id。",
                file=sys.stderr,
            )
        else:
            # 兜底：剪贴板 + 文件都失败，只能裸打印
            print(
                "\n⚠️  剪贴板与文件均不可用，仅能以文本形式输出 URL。\n"
                "   从下方复制时，终端软换行可能插入空格并污染 client_id（Amazon 会报 400）。\n"
                "   如 agent 调用本脚本，请改用 stdout JSON 的 `authorizeUrl` 字段。",
                file=sys.stderr,
            )
            print(f"\n  {url}\n", file=sys.stderr)


def _save_url_to_file(url: str):
    """把干净 URL 写到 ~/.cache/linkfox/last_authorize_url.txt；失败返回 None。"""
    try:
        home = Path.home()
        cache_dir = home / ".cache" / "linkfox"
        cache_dir.mkdir(parents=True, exist_ok=True)
        f = cache_dir / "last_authorize_url.txt"
        f.write_text(url, encoding="utf-8", newline="")
        return str(f)
    except Exception:
        # 退而求其次：系统临时目录
        try:
            f = Path(tempfile.gettempdir()) / "linkfox_last_authorize_url.txt"
            f.write_text(url, encoding="utf-8", newline="")
            return str(f)
        except Exception:
            return None


def _copy_to_clipboard(url: str) -> bool:
    """Best-effort 跨平台写系统剪贴板；失败静默降级。"""
    plat = platform.system()
    try:
        if plat == "Windows":
            # 通过 clip.exe，stdin 走 utf-16 最稳
            p = subprocess.run(["clip.exe"], input=url, text=True, check=True, timeout=5)
            return p.returncode == 0
        if plat == "Darwin":
            p = subprocess.run(["pbcopy"], input=url, text=True, check=True, timeout=5)
            return p.returncode == 0
        # Linux：优先 xclip，再 xsel，再 wl-copy（Wayland）
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
