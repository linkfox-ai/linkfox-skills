"""素材编排与下载；LinkFox 请求由业务入口委托公共模板。"""
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
from _aigc_api import api_error

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
        raise RuntimeError("Unset ACPX_WORKSPACES and run from a writable task directory")
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
        raise RuntimeError("API entry did not save its response")
    artifact = Path(match.group(1))
    result = json.loads(artifact.read_text(encoding="utf-8"))
    if not isinstance(result, dict):
        raise RuntimeError("API response is not a JSON object")
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
                raise RuntimeError("Media fields require nonempty file paths or source URLs")
            if source not in uploaded:
                payload = {"url" if source.startswith(("http://", "https://")) else "filePath": source}
                result, artifact = invoke(scripts / "upload_file.py", payload)
                if api_error(result) or not isinstance(result.get("viewUrl"), str) or not result["viewUrl"].startswith(("https://", "http://")):
                    print("Saved full response: " + str(artifact))
                    raise RuntimeError("Media upload failed; generation was not submitted. See references/onboarding.md for auth/billing errors")
                uploaded[source] = result["viewUrl"]
            urls.append(uploaded[source])
        prepared[key] = urls if isinstance(value, list) else urls[0]
    return prepared


def download_results(result, scripts):
    if api_error(result):
        raise RuntimeError("查询响应异常，保留原始响应并停止下载")
    results = result.get("resultList")
    if results is None:
        results = []
    if not isinstance(results, list):
        raise RuntimeError("resultList 必须是数组，保留原始响应并停止下载")
    entry = scripts / "query_task.py"
    if not entry.exists():
        entry = scripts / "task_query.py"
    storage = load_entry(entry)
    slug = scripts.parent.name
    stamp = time.time()
    _, session = storage._ensure_session(stamp)
    session = Path(session)
    media = session / "media"
    media.mkdir(exist_ok=True)
    paths, items = [], []
    if result.get("status") == "SUCCESS":
        for index, item in enumerate(results, 1):
            if not isinstance(item, dict):
                items.append({"id": None, "type": None, "downloadError": "结果项不是对象，未下载"})
                continue
            record = {"id": item.get("id"), "type": item.get("type")}
            for key in ("status", "errorCode", "errorMsg"):
                if key in item:
                    record[key] = item[key]
            items.append(record)
            url = item.get("url")
            if item.get("status") not in (None, 1) or not isinstance(url, str) or not url:
                record["downloadError"] = "结果项未成功或缺少下载地址，未下载；保留查询响应，不重建任务"
                continue
            temporary = media / (".download-" + str(time.time_ns()))
            try:
                if urlsplit(url).scheme not in {"http", "https"}:
                    raise ValueError("Unsupported result URL")
                with urlopen(Request(url, headers={"User-Agent": "LinkFox-Skill/2.0"}), timeout=150) as response:
                    if urlsplit(response.geturl()).scheme not in {"http", "https"}:
                        raise ValueError("Unsupported redirect")
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
                    raise ValueError("Empty result file")
                final = media / (slug + "-" + str(time.time_ns()) + "-" + str(index) + ext)
                temporary.replace(final)
                paths.append(str(final.resolve()))
                record["localPath"] = paths[-1]
                storage._update_meta(str(session), skill=slug, kind="media",
                                     file_rel=str(final.relative_to(session)), ts=stamp)
            except Exception:
                temporary.unlink(missing_ok=True)
                record["downloadError"] = "Result download failed; retry download from the saved query response, not generation"
    manifest = {"taskId": result.get("taskId"), "status": result.get("status"),
                "costToken": result.get("costToken"), "costCredit": result.get("costCredit"),
                "items": items, "mediaPaths": paths}
    artifact = Path(storage.resolve_data_path(slug + "-assets", time.time()))
    artifact.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Saved media manifest: " + str(artifact))
    if paths:
        print("Saved full response: " + json.dumps(paths, ensure_ascii=False))
    return paths, manifest
