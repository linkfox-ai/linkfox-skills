#!/usr/bin/env python3
"""读取本地或下载远程素材，进程内编码后调用内置 Base64 上传入口。"""
import base64
import importlib.util
import json
from pathlib import Path
import sys
from urllib.error import URLError
from urllib.parse import unquote, urlsplit
from urllib.request import Request, urlopen
from material_runtime import check_output_directory

MAX_BYTES = 35 * 1024 * 1024
EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".mp4", ".mov"}
MIME_EXTENSIONS = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp",
                   "video/mp4": ".mp4", "video/quicktime": ".mov"}


def read_source(params):
    local, remote = params.get("filePath"), params.get("url")
    if bool(local) == bool(remote):
        raise SystemExit("filePath 与 url 必须恰好提供一个")
    if local:
        if not isinstance(local, str):
            raise SystemExit("filePath 必须为字符串")
        source = Path(local).expanduser().resolve()
        if not source.is_file():
            raise SystemExit("素材文件不存在")
        name = source.name
        if source.suffix.lower() not in EXTENSIONS:
            raise SystemExit("支持的扩展名：jpg/jpeg/png/webp/mp4/mov")
        with source.open("rb") as media:
            content = media.read(MAX_BYTES + 1)
    else:
        if not isinstance(remote, str):
            raise SystemExit("url 必须为字符串")
        parsed = urlsplit(remote)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise SystemExit("源素材 URL 必须使用 HTTP(S)")
        try:
            # 接口凭证只发送给上传接口，不发送给素材源站。
            with urlopen(Request(remote, headers={"User-Agent": "LinkFox-Skill/2.0"}), timeout=150) as response:
                if urlsplit(response.geturl()).scheme not in {"http", "https"}:
                    raise SystemExit("源素材跳转必须使用 HTTP(S)")
                name = Path(unquote(urlsplit(response.geturl()).path)).name
                declared_type = response.headers.get_content_type()
                content = response.read(MAX_BYTES + 1)
        except (URLError, OSError, ValueError):
            raise SystemExit("源素材下载失败，未上传或创建生成任务")
        if Path(name).suffix.lower() not in EXTENSIONS:
            ext = MIME_EXTENSIONS.get(declared_type)
            if not ext:
                if content.startswith(b"\x89PNG\r\n\x1a\n"): ext = ".png"
                elif content.startswith(b"\xff\xd8\xff"): ext = ".jpg"
                elif content[:4] == b"RIFF" and content[8:12] == b"WEBP": ext = ".webp"
                elif content[4:8] == b"ftyp": ext = ".mov" if content[8:12] == b"qt  " else ".mp4"
            if not ext:
                raise SystemExit("无法识别支持的素材格式，请核对源文件及其实际扩展名")
            name = "media" + ext
    if not content or len(content) > MAX_BYTES:
        raise SystemExit("文件必须非空且不超过 35MiB")
    file_name = params.get("fileName") or name
    if not isinstance(file_name, str) or Path(file_name).suffix.lower() not in EXTENSIONS:
        raise SystemExit("fileName 必须包含支持的媒体扩展名")
    if Path(file_name).suffix.lower().replace(".jpeg", ".jpg") != Path(name).suffix.lower().replace(".jpeg", ".jpg"):
        raise SystemExit("fileName 必须保留源媒体格式")
    return Path(file_name).name, content


def main():
    if len(sys.argv) < 2 or sys.argv[1] in {"--help", "-h"}:
        print("用法：upload_file.py '<包含 filePath 或 url 的 JSON>' [--inline]")
        if len(sys.argv) < 2:
            raise SystemExit(1)
        return
    try:
        params = json.loads(sys.argv[1])
    except json.JSONDecodeError:
        raise SystemExit("JSON 参数格式错误")
    if not isinstance(params, dict):
        raise SystemExit("参数必须为 JSON 对象")
    check_output_directory()
    entry = Path(__file__).resolve().with_name("upload_by_base64.py")
    spec = importlib.util.spec_from_file_location("aigc_media_upload", entry)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.get_api_key()  # 下载源素材前检查凭证。
    name, content = read_source(params)
    payload = {"fileName": name, "base64": base64.b64encode(content).decode("ascii")}
    inline = "--inline" in sys.argv[2:]
    # 文件字节仅存在于进程内，不进入操作系统命令行或请求文件。
    argv = [json.dumps(payload, ensure_ascii=False), "--no-cache"]
    if inline:
        argv.append("--inline")
    module.main(argv)


if __name__ == "__main__":
    main()
