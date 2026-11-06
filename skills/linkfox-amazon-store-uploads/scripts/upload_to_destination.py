#!/usr/bin/env python3
"""
Amazon Store — PUT or multipart POST to createUploadDestinationForResource URL
=================================================================

在调用 create_upload_destination_for_resource 之后，将文件上传到返回的 **url**，
并附带响应中的 **headers**（不经 developerProxy）。

Usage:
  python upload_to_destination.py '{
    "uploadUrl": "https://...",
    "headers": { "Content-Type": "image/jpeg", "Content-MD5": "..." },
    "filePath": "/path/to/image.jpg"
  }'

也可传 uploadDestination 对象（含 url、headers）：
  "uploadDestination": { "url": "...", "headers": { ... } }

A+ 表单上传传 method: "POST"；URL 查询参数自动作为 multipart 字段，
可用 formFields 补充字段，fileName 和 contentType 指定文件名与文件 MIME 类型。
"""

from __future__ import annotations

import json
import mimetypes
from pathlib import Path
import secrets
import sys
from urllib.parse import parse_qsl, urlsplit, urlunsplit
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from _spapi_uploads_common import (
    API_BASE_URL, output_context, emit_result, lf_inline_flag, load_cli_params,
    load_file_bytes, resolve_upload_destination,
)


def _resolve_upload_target(params: dict) -> tuple[str, dict]:
    supplied = params.get("uploadDestination")
    dest = resolve_upload_destination(supplied)
    if isinstance(supplied, dict) and dest is None:
        print("uploadDestination contains an invalid or unsuccessful response", file=sys.stderr)
        sys.exit(1)
    if isinstance(dest, dict):
        url = dest.get("url") or params.get("uploadUrl")
        headers = dest.get("headers") or params.get("headers") or {}
    else:
        url = params.get("uploadUrl")
        headers = params.get("headers") or {}
    if not url:
        print("Missing uploadUrl or uploadDestination.url", file=sys.stderr)
        sys.exit(1)
    if not isinstance(headers, dict):
        print("headers must be a JSON object", file=sys.stderr)
        sys.exit(1)
    parsed = urlsplit(str(url).strip())
    # DNS 绝对域名末尾的点不改变目标；与配置网关统一后再判断。
    host = (parsed.hostname or "").lower().rstrip(".")
    gateway_host = (urlsplit(API_BASE_URL).hostname or "").lower().rstrip(".")
    if host == "linkfox.com" or host.endswith(".linkfox.com") or (gateway_host and host == gateway_host):
        print("上传地址必须是非 LinkFox 的预签名地址", file=sys.stderr)
        sys.exit(1)
    return str(url).strip(), {str(k): str(v) for k, v in headers.items()}


def _build_upload_request(params: dict, upload_url: str, headers: dict, payload: bytes) -> Request:
    method = str(params.get("method", "PUT")).upper().strip()
    if method == "PUT":
        return Request(upload_url, data=payload, headers=headers, method=method)
    if method != "POST":
        raise ValueError("method must be PUT or POST")

    parsed = urlsplit(upload_url)
    fields = dict(parse_qsl(parsed.query, keep_blank_values=True))
    extra_fields = params.get("formFields", {})
    if not isinstance(extra_fields, dict):
        raise ValueError("formFields must be an object of strings")
    fields.update(extra_fields)
    for name, value in fields.items():
        if not isinstance(name, str) or not isinstance(value, str):
            raise ValueError("formFields names and values must be strings")
        if name.lower() == "file" or any(c in name for c in ('"', "\r", "\n", "\\")):
            raise ValueError("formFields must use safe names and must not contain file")

    file_name = str(params.get("fileName") or Path(params.get("filePath") or "upload.bin").name)
    for char in ('"', "\r", "\n", "\\"):
        file_name = file_name.replace(char, "_")
    file_type = str(params.get("contentType") or next(
        (v for k, v in headers.items() if k.lower() == "content-type"),
        mimetypes.guess_type(file_name)[0] or "application/octet-stream",
    ))
    if "\r" in file_type or "\n" in file_type:
        raise ValueError("contentType must not contain newlines")

    boundary = "LinkFoxUpload" + secrets.token_hex(16)
    parts = []
    for name, value in fields.items():
        parts.append(
            f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{value}\r\n'.encode("utf-8")
        )
    parts.extend([
        f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="{file_name}"\r\n'
        f"Content-Type: {file_type}\r\n\r\n".encode("utf-8"),
        payload,
        f"\r\n--{boundary}--\r\n".encode("ascii"),
    ])
    # POST 的 Content-Type 描述整个 multipart 请求；文件 MIME 类型写入文件 part。
    post_headers = {k: v for k, v in headers.items() if k.lower() not in ("content-type", "content-length")}
    post_headers["Content-Type"] = f"multipart/form-data; boundary={boundary}"
    post_url = urlunsplit((parsed.scheme, parsed.netloc, parsed.path, "", ""))
    return Request(post_url, data=b"".join(parts), headers=post_headers, method=method)


def upload_file(params: dict, *, payload: bytes | None = None) -> dict:
    """独立上传或复用链式入口读取的同一份文件字节。"""
    upload_url, hdrs = _resolve_upload_target(params)
    if payload is None:
        payload = load_file_bytes(params)
    if not payload:
        print("Provide filePath, content, or contentBase64", file=sys.stderr)
        sys.exit(1)

    with output_context():
        pass

    try:
        req = _build_upload_request(params, upload_url, hdrs, payload)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
    out: dict = {
        "uploadUrl": req.full_url,
        "method": req.get_method(),
        "bytesUploaded": len(payload),
        "requestHeaders": hdrs if req.get_method() == "PUT" else dict(req.header_items()),
    }
    try:
        with urlopen(req, timeout=300) as resp:
            out["httpStatus"] = resp.status
            out["success"] = 200 <= resp.status < 300
    except HTTPError as e:
        body = e.read().decode("utf-8", errors="replace") if e.fp else ""
        out["httpStatus"] = e.code
        out["success"] = False
        out["error"] = f"HTTP {e.code}: {e.reason}"
        out["details"] = body[:2000]
    except URLError as e:
        out["success"] = False
        out["error"] = f"Connection failed: {e.reason}"

    inline = lf_inline_flag()
    emit_result(out, inline=inline)
    if not out.get("success"):
        sys.exit(1)
    return out


def main() -> None:
    params = load_cli_params()
    if not params:
        print(
            "Usage: upload_to_destination.py '<JSON>'\n"
            "Required: uploadUrl (or uploadDestination), headers, "
            "and filePath | content | contentBase64",
            file=sys.stderr,
        )
        sys.exit(1)
    upload_file(params)


if __name__ == "__main__":
    main()
