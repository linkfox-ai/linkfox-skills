#!/usr/bin/env python3
"""上传本地图片，仅输出安全元数据。"""

import json
import mimetypes
import os
import re
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from _chuhaijiang_transport import request_json, is_normal_response

API_PATH = "/chuhaijiang/upload/presigned-url"
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}


def _safe_message(value):
    """保留诊断消息，去除可能回显的凭证与临时地址。"""
    message = str(value or "")
    for key in (os.environ.get("LINKFOX_AGENT_API_KEY"), os.environ.get("LINKFOXAGENT_API_KEY")):
        if key:
            message = message.replace(key, "[已隐藏密钥]")
    return re.sub(r"https?://[^\s\"'<>]+", "[已隐藏地址]", message)


def request_upload_target(file_name: str):
    status, result = request_json(API_PATH, {"fileName": file_name})
    if not is_normal_response(status, result) or not isinstance(result, dict) or result.get("error"):
        # 保留认证/余额状态用于 onboarding，不回显完整错误正文。
        code = result.get("errcode") if isinstance(result, dict) else None
        message = result.get("errmsg") or result.get("error") if isinstance(result, dict) else "响应结构无效"
        print(f"申请上传地址失败：HTTP {status}，errcode={_safe_message(code)}；{_safe_message(message)}", file=sys.stderr)
        raise SystemExit(1)

    data = result.get("data") if isinstance(result.get("data"), dict) else {}
    # url 仅用于 PUT；signed_url 为临时读取地址，禁止用作上传兜底。
    upload_url = data.get("url")
    os_key = data.get("os_key") or data.get("osKey")
    os_bucket = data.get("os_bucket") or data.get("osBucket")
    if not upload_url or not os_key:
        print("Upload target response did not contain url and os_key.", file=sys.stderr)
        raise SystemExit(1)
    return (
        str(upload_url),
        str(os_key),
        os_bucket,
        result.get("request_id"),
        result.get("errcode"),
        _safe_message(result.get("errmsg")) if result.get("errmsg") is not None else None,
        sorted(data.keys()),
    )


def upload_file(upload_url: str, file_path: Path, content_type: str) -> int:
    try:
        request = Request(
            upload_url,
            data=file_path.read_bytes(),
            headers={"Content-Type": content_type},
            method="PUT",
        )
        with urlopen(request, timeout=150) as response:
            if response.status not in (200, 201, 204):
                raise RuntimeError(f"unexpected upload status {response.status}")
            return response.status
    except (HTTPError, URLError, TimeoutError, ValueError, RuntimeError):
        print("图片上传失败，请检查外部上传服务状态。", file=sys.stderr)
        raise SystemExit(1) from None


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: upload_image.py <local-image.jpg|jpeg|png>", file=sys.stderr)
        raise SystemExit(1)

    file_path = Path(sys.argv[1]).expanduser().resolve()
    if not file_path.is_file():
        print(f"File not found: {file_path}", file=sys.stderr)
        raise SystemExit(1)
    if file_path.suffix.lower() not in ALLOWED_EXTENSIONS:
        print("Unsupported image format. Use jpg, jpeg, or png.", file=sys.stderr)
        raise SystemExit(1)

    content_type = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
    (
        upload_url,
        os_key,
        os_bucket,
        request_id,
        errcode,
        errmsg,
        presign_data_fields,
    ) = request_upload_target(file_path.name)
    upload_status = upload_file(upload_url, file_path, content_type)
    print(
        json.dumps(
            {
                "osKey": os_key,
                "osBucket": os_bucket,
                "fileName": file_path.name,
                "contentType": content_type,
                "fileSize": file_path.stat().st_size,
                "uploadStatus": upload_status,
                "requestId": request_id,
                "errcode": errcode,
                "errmsg": errmsg,
                "presignDataFields": presign_data_fields,
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
