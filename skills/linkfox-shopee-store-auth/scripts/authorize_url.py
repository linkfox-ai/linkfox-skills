#!/usr/bin/env python3
"""生成 Shopee ERP / AD 授权链接，保留完整 URL 文件与剪贴板输出。"""

import platform
import subprocess
import sys
import tempfile
from pathlib import Path

from _shopee_auth_common import normalize_app_type, read_params, run_request


def call_api(params):
    return run_request("/shopee/authorizeUrl", "authorize-url", params)


def main():
    params = read_params(
        "用法：python authorize_url.py '<JSON 参数>' [--inline] [--no-cache]\n"
        "例如：{\"shopName\":\"我的虾皮店铺\",\"region\":\"cn\",\"appType\":\"erp\"}"
    )
    if not params.get("region"):
        print("未指定 region，使用默认 cn。", file=sys.stderr)
        params["region"] = "cn"
    if params["region"] not in ("cn", "global", "br"):
        print(f"region 必须为 cn / global / br，收到 {params['region']!r}。", file=sys.stderr)
        raise SystemExit(1)
    normalize_app_type(params)
    if isinstance(params.get("shopName"), str):
        shop_name = params["shopName"].strip()
        if shop_name:
            params["shopName"] = shop_name
        else:
            del params["shopName"]

    result = call_api(params)
    if "authorizeUrl" in result:
        url = result["authorizeUrl"]
        file_path = _save_url_to_file(url)
        clipboard_ok = _copy_to_clipboard(url)
        print("\n已生成授权链接。", file=sys.stderr)
        print(f"appType: {params['appType']}", file=sys.stderr)
        if params["appType"] == "ad":
            print("这是广告（AD）应用授权，与 ERP 授权相互独立。", file=sys.stderr)
        if params.get("shopName"):
            print(f"店铺名: {params['shopName']}", file=sys.stderr)
        print("授权地址约 1 小时有效，请勿复用旧 URL。", file=sys.stderr)
        print("请在日常运营该店铺的安全网络环境中打开链接；建议使用紫鸟等防关联浏览器，"
              "切勿在陌生或公共网络下操作。", file=sys.stderr)
        if clipboard_ok:
            print("已写入剪贴板，可在浏览器地址栏 Ctrl+V / Cmd+V。", file=sys.stderr)
        if file_path:
            print(f"已写入文件：{file_path}", file=sys.stderr)
        if clipboard_ok or file_path:
            print("请从剪贴板或文件复制 URL；避免终端或聊天窗口软换行破坏链接。", file=sys.stderr)
        else:
            print("剪贴板与文件均不可用，请读取 stdout JSON 的 authorizeUrl 字段。", file=sys.stderr)
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
