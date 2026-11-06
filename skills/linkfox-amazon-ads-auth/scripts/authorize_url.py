#!/usr/bin/env python3
"""
Amazon Ads 授权链接生成脚本。
通过公共调用器生成授权链接，手动模式保留 URL 导出行为。

用法：
  python authorize_url.py '{"region": "NA", "accountName": "My Ads Account"}'
"""

import json
import os
import platform
import subprocess
import sys
import tempfile
from pathlib import Path

from _ads_auth_common import request, cli_params

# 生产默认走 tool-gateway.linkfox.com；开发/测试期可 export AMAZON_ADS_BASE_URL=<url> 覆盖
API_BASE_URL = (os.environ.get("LINKFOX_TOOL_GATEWAY") or os.environ.get("AMAZON_ADS_BASE_URL") or "https://tool-gateway.linkfox.com").rstrip("/")


def call_api(params: dict) -> dict:
    """自动授权兼容入口：仅返回内存中的 JSON，不写 URL 文件或剪贴板。"""
    return request("/amazonAds/authorizeUrl", params)


def main():
    try:
        params = cli_params(sys.argv[1:], required=True)
    except ValueError as e:
        print(f"参数格式错误：{e}", file=sys.stderr)
        sys.exit(1)

    if "region" not in params or not params.get("region"):
        print("未提供 region，默认使用 NA（详见 references/api.md）", file=sys.stderr)
        params["region"] = "NA"
    if params["region"] not in ("NA", "EU", "FE"):
        print(f"region 必须为 NA / EU / FE，收到 {params['region']!r}", file=sys.stderr)
        sys.exit(1)

    if "accountName" not in params:
        print(
            "缺少 accountName：授权前必须填写可识别的账号名，"
            "用于在已授权列表中区分。",
            file=sys.stderr,
        )
        sys.exit(1)
    account_name = params["accountName"]
    if not isinstance(account_name, str) or not account_name.strip():
        print(
            "accountName 必须为非空字符串",
            file=sys.stderr,
        )
        sys.exit(1)
    params["accountName"] = account_name.strip()

    result = request("/amazonAds/authorizeUrl", params, persist=True,
                     inline="--inline" in sys.argv[1:])
    if result.get("error"):
        sys.exit(1)

    if "authorizeUrl" in result:
        url = result["authorizeUrl"]
        # 经验：长 URL（~270 字符）在终端/聊天窗口里软换行时复制会被插入空格，导致 client_id 被污染、
        # Amazon 返回 400 StegoRuntimeOAuth2ClientManager:getClientDefinition。
        # 为此把 URL 同步落到临时文件并尝试写系统剪贴板，用户直接 Ctrl+V 即可避免这个坑。
        file_path = _save_url_to_file(url)
        clipboard_ok = _copy_to_clipboard(url)

        print("\n✓ 已生成授权链接。", file=sys.stderr)
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
    """尽力跨平台写入系统剪贴板；失败时静默降级。"""
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
