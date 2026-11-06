#!/usr/bin/env python3
"""读取文件或下载源 URL，再通过内置 Base64 入口上传。"""
import base64
import importlib.util
import json
from pathlib import Path
import sys
from urllib.error import URLError
from urllib.parse import unquote, urlsplit
from urllib.request import Request, urlopen
from _aigc_runtime import check_output_directory

MAX_BYTES = 10 * 1024 * 1024
EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".mp4", ".mov"}
MIME_EXTENSIONS = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp",
                   "video/mp4": ".mp4", "video/quicktime": ".mov"}


def read_source(params):
    local, remote = params.get("filePath"), params.get("url")
    if bool(local) == bool(remote):
        raise SystemExit("filePath 与 url 必须且只能提供一个")
    if local:
        if not isinstance(local, str):
            raise SystemExit("filePath 必须为字符串")
        source = Path(local).expanduser().resolve()
        if not source.is_file():
            raise SystemExit("素材文件不存在")
        name = source.name
        if source.suffix.lower() not in EXTENSIONS:
            raise SystemExit("支持扩展名：jpg/jpeg/png/webp/mp4/mov")
        with source.open("rb") as media:
            content = media.read(MAX_BYTES + 1)
    else:
        if not isinstance(remote, str):
            raise SystemExit("url 必须为字符串")
        parsed = urlsplit(remote)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise SystemExit("源 URL 必须使用 HTTP(S)")
        try:
            # API 凭证仅发往上传接口，不发给素材源站。
            with urlopen(Request(remote, headers={"User-Agent": "LinkFox-Skill/2.0"}), timeout=150) as response:
                if urlsplit(response.geturl()).scheme not in {"http", "https"}:
                    raise SystemExit("源地址重定向必须使用 HTTP(S)")
                name = Path(unquote(urlsplit(response.geturl()).path)).name
                declared_type = response.headers.get_content_type()
                content = response.read(MAX_BYTES + 1)
        except (URLError, OSError, ValueError):
            raise SystemExit("源素材下载失败，未提交上传或生成")
        if Path(name).suffix.lower() not in EXTENSIONS:
            ext = MIME_EXTENSIONS.get(declared_type)
            if not ext:
                if content.startswith(b"\x89PNG\r\n\x1a\n"): ext = ".png"
                elif content.startswith(b"\xff\xd8\xff"): ext = ".jpg"
                elif content[:4] == b"RIFF" and content[8:12] == b"WEBP": ext = ".webp"
                elif content[4:8] == b"ftyp": ext = ".mov" if content[8:12] == b"qt  " else ".mp4"
            if not ext:
                raise SystemExit("无法识别支持的素材格式，请提供带真实扩展名的 fileName")
            name = "media" + ext
    if not content or len(content) > MAX_BYTES:
        raise SystemExit("文件必须非空且不超过 10MB")
    file_name = params.get("fileName") or name
    if not isinstance(file_name, str) or Path(file_name).suffix.lower() not in EXTENSIONS:
        raise SystemExit("fileName 必须带支持的素材扩展名")
    if Path(file_name).suffix.lower().replace(".jpeg", ".jpg") != Path(name).suffix.lower().replace(".jpeg", ".jpg"):
        raise SystemExit("fileName 必须保持源素材格式")
    return Path(file_name).name, content


def main():
    if len(sys.argv) < 2:
        raise SystemExit("用法：upload_file.py '<包含 filePath 或 url 的 JSON>' [--inline]")
    try:
        params = json.loads(sys.argv[1])
    except json.JSONDecodeError:
        raise SystemExit("JSON 参数无效")
    if not isinstance(params, dict):
        raise SystemExit("参数必须为 JSON 对象")
    check_output_directory()
    entry = Path(__file__).resolve().with_name("upload_by_base64.py")
    spec = importlib.util.spec_from_file_location("aigc_media_upload", entry)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.get_api_key()  # 先检查凭证，再下载源素材。
    name, content = read_source(params)
    payload = {"fileName": name, "base64": base64.b64encode(content).decode("ascii")}
    inline = "--inline" in sys.argv[2:]
    # 文件内容仅在进程内处理，不进入操作系统命令行或请求文件。
    sys.argv = [str(entry), json.dumps(payload, ensure_ascii=False), "--no-cache"]
    if inline:
        sys.argv.append("--inline")
    module.main()


if __name__ == "__main__":
    main()
