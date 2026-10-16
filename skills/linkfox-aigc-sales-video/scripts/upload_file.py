#!/usr/bin/env python3
"""Read a file or download a source URL, then use the official Base64 upload entry."""
import base64
import importlib.util
import json
from pathlib import Path
import sys
from urllib.error import URLError
from urllib.parse import unquote, urlsplit
from urllib.request import Request, urlopen

MAX_BYTES = 10 * 1024 * 1024
EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".mp4", ".mov"}
MIME_EXTENSIONS = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp",
                   "video/mp4": ".mp4", "video/quicktime": ".mov"}


def read_source(params):
    local, remote = params.get("filePath"), params.get("url")
    if bool(local) == bool(remote):
        raise SystemExit("Supply exactly one of filePath or url")
    if local:
        if not isinstance(local, str):
            raise SystemExit("filePath must be a string")
        source = Path(local).expanduser().resolve()
        if not source.is_file():
            raise SystemExit("Media file does not exist")
        name = source.name
        if source.suffix.lower() not in EXTENSIONS:
            raise SystemExit("Supported extensions: jpg/jpeg/png/webp/mp4/mov")
        with source.open("rb") as media:
            content = media.read(MAX_BYTES + 1)
    else:
        if not isinstance(remote, str):
            raise SystemExit("url must be a string")
        parsed = urlsplit(remote)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise SystemExit("Source URL must use HTTP(S)")
        try:
            # API credentials are sent only to the upload API, never the source host.
            with urlopen(Request(remote, headers={"User-Agent": "LinkFox-Skill/2.0"}), timeout=150) as response:
                if urlsplit(response.geturl()).scheme not in {"http", "https"}:
                    raise SystemExit("Source redirect must use HTTP(S)")
                name = Path(unquote(urlsplit(response.geturl()).path)).name
                declared_type = response.headers.get_content_type()
                content = response.read(MAX_BYTES + 1)
        except (URLError, OSError, ValueError):
            raise SystemExit("Source download failed; no upload or generation was submitted")
        if Path(name).suffix.lower() not in EXTENSIONS:
            ext = MIME_EXTENSIONS.get(declared_type)
            if not ext:
                if content.startswith(b"\x89PNG\r\n\x1a\n"): ext = ".png"
                elif content.startswith(b"\xff\xd8\xff"): ext = ".jpg"
                elif content[:4] == b"RIFF" and content[8:12] == b"WEBP": ext = ".webp"
                elif content[4:8] == b"ftyp": ext = ".mov" if content[8:12] == b"qt  " else ".mp4"
            if not ext:
                raise SystemExit("Cannot identify supported media; supply fileName with its actual extension")
            name = "media" + ext
    if not content or len(content) > MAX_BYTES:
        raise SystemExit("File must be nonempty and at most 10MB")
    file_name = params.get("fileName") or name
    if not isinstance(file_name, str) or Path(file_name).suffix.lower() not in EXTENSIONS:
        raise SystemExit("fileName requires a supported media extension")
    if Path(file_name).suffix.lower().replace(".jpeg", ".jpg") != Path(name).suffix.lower().replace(".jpeg", ".jpg"):
        raise SystemExit("fileName must keep the source media format")
    return Path(file_name).name, content


def main():
    if len(sys.argv) < 2:
        raise SystemExit("Usage: upload_file.py '<JSON with filePath or url>' [--inline]")
    try:
        params = json.loads(sys.argv[1])
    except json.JSONDecodeError:
        raise SystemExit("Invalid JSON parameters")
    if not isinstance(params, dict):
        raise SystemExit("Parameters must be a JSON object")
    entry = Path(__file__).resolve().with_name("upload_by_base64.py")
    spec = importlib.util.spec_from_file_location("aigc_media_upload", entry)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.get_api_key()  # Check credentials before downloading source material.
    name, content = read_source(params)
    payload = {"fileName": name, "base64": base64.b64encode(content).decode("ascii")}
    inline = "--inline" in sys.argv[2:]
    # File bytes stay in this process, outside the OS command line and request files.
    sys.argv = [str(entry), json.dumps(payload, ensure_ascii=False), "--no-cache"]
    if inline:
        sys.argv.append("--inline")
    module.main()


if __name__ == "__main__":
    main()
