"""素材准备、任务编排和媒体下载；LinkFox 请求由公共调用器执行。"""
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import re
import sys
import time
from urllib.parse import urlsplit
from urllib.request import Request, urlopen
from _aigc_runtime import api_error

MEDIA_FIELDS = {"imageUrl", "lastFrameImageUrl", "modelImageUrl", "sceneImageUrl",
                "sourceVideoUrl", "refVideoUrl", "imageList", "refImageList", "video"}
MIME_EXT = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp",
            "video/mp4": ".mp4", "video/quicktime": ".mov", "video/webm": ".webm",
            "application/zip": ".zip"}
EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".mp4", ".mov", ".webm", ".zip"}


def load_entry(path):
    spec = importlib.util.spec_from_file_location("material_" + path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check_output_directory():
    configured = (os.environ.get("ACPX_WORKSPACES") or "").split(os.pathsep)[0].strip()
    if configured and Path(configured).resolve() != Path.cwd().resolve():
        raise RuntimeError("请清除 ACPX_WORKSPACES 并从可写任务目录运行")
    output = Path.cwd() / "linkfox"
    output.mkdir(exist_ok=True)
    probe = output / (".write-probe-" + str(time.time_ns()))
    try:
        probe.write_bytes(b"")
    finally:
        probe.unlink(missing_ok=True)


def invoke(path, params, no_cache=False):
    module = load_entry(path)
    argv = sys.argv
    capture = io.StringIO()
    try:
        sys.argv = [str(path), json.dumps(params, ensure_ascii=False)]
        if no_cache:
            sys.argv.append("--no-cache")
        with contextlib.redirect_stdout(capture):
            module.main()
    finally:
        sys.argv = argv
    match = re.search(r"^Saved full response: (.+?) \(\d+ bytes\)$", capture.getvalue(), re.M)
    if not match:
        raise RuntimeError("接口入口未保存响应")
    artifact = Path(match.group(1))
    result = json.loads(artifact.read_text(encoding="utf-8"))
    if not isinstance(result, dict):
        raise RuntimeError("接口响应不是 JSON 对象")
    return result, artifact


def prepare_media(params, scripts):
    prepared = json.loads(json.dumps(params))
    uploaded = {}
    for key in MEDIA_FIELDS:
        value = prepared.get(key)
        if value is None or value == "" or value == []:
            continue
        sources = value if isinstance(value, list) else [value]
        urls = []
        for source in sources:
            if not isinstance(source, str) or not source.strip():
                raise RuntimeError("媒体字段必须为非空文件路径或源 URL")
            if source not in uploaded:
                payload = {"url" if source.startswith(("http://", "https://")) else "filePath": source}
                result, artifact = invoke(scripts / "upload_file.py", payload)
                if api_error(result) or not isinstance(result.get("viewUrl"), str) or not result["viewUrl"].startswith(("https://", "http://")):
                    print("Saved full response: " + str(artifact))
                    raise RuntimeError("素材上传失败，未提交生成任务；认证或用量错误见 references/onboarding.md")
                uploaded[source] = result["viewUrl"]
            urls.append(uploaded[source])
        prepared[key] = urls if isinstance(value, list) else urls[0]
    return prepared


def download_results(result, scripts):
    entry = scripts / "query_task.py"
    storage = load_entry(entry)
    slug = scripts.parent.name
    stamp = time.time()
    _, session = storage._ensure_session(stamp)
    session = Path(session)
    media = session / "media"
    media.mkdir(exist_ok=True)
    paths, items = [], []
    if result.get("status") == "SUCCESS":
        for index, item in enumerate(result.get("resultList") or [], 1):
            record = {"id": item.get("id"), "type": item.get("type")}
            for key in ("status", "errorCode", "errorMsg"):
                if key in item:
                    record[key] = item[key]
            items.append(record)
            url = item.get("url")
            if item.get("status") not in (None, 1) or not isinstance(url, str) or not url:
                continue
            temporary = media / (".download-" + str(time.time_ns()))
            try:
                if urlsplit(url).scheme not in {"http", "https"}:
                    raise ValueError("不支持的成品 URL")
                with urlopen(Request(url, headers={"User-Agent": "LinkFox-Skill/2.0"}), timeout=150) as response:
                    if urlsplit(response.geturl()).scheme not in {"http", "https"}:
                        raise ValueError("不支持的跳转协议")
                    ext = "." + str(item.get("format") or "").lower().lstrip(".")
                    if ext not in EXTENSIONS:
                        ext = Path(urlsplit(response.geturl()).path).suffix.lower()
                    if ext not in EXTENSIONS:
                        ext = MIME_EXT.get(response.headers.get_content_type(), ".bin")
                    with temporary.open("wb") as output:
                        while True:
                            chunk = response.read(65536)
                            if not chunk:
                                break
                            output.write(chunk)
                if temporary.stat().st_size == 0:
                    raise ValueError("成品文件为空")
                final = media / (slug + "-" + str(time.time_ns()) + "-" + str(index) + ext)
                temporary.replace(final)
                paths.append(str(final.resolve()))
                record["localPath"] = paths[-1]
                storage._update_meta(str(session), skill=slug, kind="media",
                                     file_rel=str(final.relative_to(session)), ts=stamp)
            except Exception:
                temporary.unlink(missing_ok=True)
                record["downloadError"] = "成品下载失败；从保存的查询响应重试下载，不重新生成"
    manifest = {"taskId": result.get("taskId"), "status": result.get("status"),
                "costToken": result.get("costToken"), "costCredit": result.get("costCredit"),
                "items": items, "mediaPaths": paths}
    artifact = Path(storage.resolve_data_path(slug + "-assets", time.time()))
    artifact.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Saved media manifest: " + str(artifact))
    if paths:
        print("Saved full response: " + json.dumps(paths, ensure_ascii=False))
    return paths, manifest
