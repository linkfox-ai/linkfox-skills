#!/usr/bin/env python3
"""Convert WebP inputs to JPEG before calling 1688 image search."""

from __future__ import annotations

import base64
import binascii
import io
import os
import tempfile
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from upload_image import extract_public_url, get_presigned_url, upload_file


class ImagePreparationError(ValueError):
    pass


def detect_image_format(data: bytes) -> str | None:
    if data.startswith(b"\xff\xd8\xff"):
        return "jpeg"
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "webp"
    return None


def _read_url_prefix(image_url: str) -> bytes:
    headers = {
        "Accept": "image/*",
        "Range": "bytes=0-63",
        "User-Agent": "LinkFox-Skill/2.0",
    }
    try:
        with urlopen(Request(image_url, headers=headers), timeout=30) as response:
            return response.read(64)
    except (HTTPError, URLError, OSError, ValueError):
        pass

    try:
        headers.pop("Range", None)
        with urlopen(Request(image_url, headers=headers), timeout=30) as response:
            return response.read(64)
    except HTTPError as exc:
        raise ImagePreparationError(
            f"cannot inspect image URL: HTTP {exc.code}"
        ) from exc
    except (URLError, OSError, ValueError) as exc:
        raise ImagePreparationError("cannot inspect image URL") from exc


def _download_image(image_url: str) -> bytes:
    try:
        with urlopen(
            Request(
                image_url,
                headers={"Accept": "image/*", "User-Agent": "LinkFox-Skill/2.0"},
            ),
            timeout=60,
        ) as response:
            return response.read()
    except HTTPError as exc:
        raise ImagePreparationError(f"cannot download image URL: HTTP {exc.code}") from exc
    except (URLError, OSError, ValueError) as exc:
        raise ImagePreparationError("cannot download image URL") from exc


def _convert_to_jpeg(data: bytes, image_format: str) -> bytes:
    try:
        from PIL import Image, ImageOps, UnidentifiedImageError, features
    except ImportError as exc:
        raise ImagePreparationError(
            "Pillow is required to convert WebP; install Pillow>=10.4,<13"
        ) from exc

    if image_format == "webp" and not features.check("webp"):
        raise ImagePreparationError("the installed Pillow build has no WebP support")

    try:
        with Image.open(io.BytesIO(data)) as opened:
            opened.seek(0)
            image = ImageOps.exif_transpose(opened)
            image.load()
            has_alpha = image.mode in {"RGBA", "LA"} or "transparency" in image.info
            if has_alpha:
                rgba = image.convert("RGBA")
                rgb = Image.new("RGB", rgba.size, "white")
                rgb.paste(rgba, mask=rgba.getchannel("A"))
            else:
                rgb = image.convert("RGB")
            output = io.BytesIO()
            rgb.save(output, format="JPEG", quality=90)
            return output.getvalue()
    except (UnidentifiedImageError, OSError) as exc:
        raise ImagePreparationError(f"cannot decode {image_format.upper()} image") from exc


def _upload_jpeg(data: bytes) -> str:
    fd, temp_path = tempfile.mkstemp(suffix=".jpg")
    try:
        with os.fdopen(fd, "wb") as temp_file:
            temp_file.write(data)
        presigned_url = get_presigned_url("image/jpeg", "jpg")
        upload_file(presigned_url, temp_path, "image/jpeg")
        return extract_public_url(presigned_url)
    finally:
        try:
            os.remove(temp_path)
        except OSError:
            pass


def prepare_search_params(params: dict[str, Any]) -> dict[str, Any]:
    prepared = dict(params)
    if str(prepared.get("imageId") or "").strip():
        return prepared

    image_base64 = prepared.get("imageBase64")
    if isinstance(image_base64, str) and image_base64.strip():
        try:
            source = base64.b64decode(image_base64, validate=True)
        except (binascii.Error, ValueError):
            return prepared
        image_format = detect_image_format(source)
        if image_format == "webp":
            prepared["imageBase64"] = base64.b64encode(
                _convert_to_jpeg(source, image_format)
            ).decode("ascii")
        return prepared

    image_url = prepared.get("imageUrl")
    if not isinstance(image_url, str) or not image_url.strip():
        return prepared

    image_format = detect_image_format(_read_url_prefix(image_url.strip()))
    if image_format != "webp":
        return prepared

    source = _download_image(image_url.strip())
    prepared["imageUrl"] = _upload_jpeg(_convert_to_jpeg(source, image_format))
    return prepared
