#!/usr/bin/env python3
"""
Amazon Store Report Retrieval - LinkFox Skill (linkfox-amazon-store-report)
============================================================================

Requests a report via the LinkFox store gateway, polls for completion, and downloads the result.

Usage:
  python get_report.py '{"sellerId": "A1234567890", "region": "NA", "reportType": "GET_MERCHANT_LISTINGS_ALL_DATA", "marketplaceIds": ["ATVPDKIKX0DER"]}'

Optional parameters:
  - dataStartTime:  ISO 8601 format (e.g., "2024-01-01T00:00:00Z")
  - dataEndTime:    ISO 8601 format
  - lastUpdatedDate: ISO 8601 (some Vendor reports; merged into create body when set)
  - reportOptions:  object (e.g. Brand Analytics: reportPeriod, asin/asins; Sales & Traffic: dateGranularity, asinGranularity)
  - pollInterval:   Seconds between status checks (default: 30)
  - maxAttempts:    Maximum polling attempts (default: 20)
  - skipDepCheck:   (boolean) skip the dependency check (default: false)
  - serveExtractedFileHttp: (boolean) start a short-lived local HTTP server and
    expose extractedFileHttpUrl for downloading the **already extracted** file (default: true)
  - serveHost:      bind address (default: "127.0.0.1")
  - servePort:      port; 0 = pick a free ephemeral port (default: 0)
  - serveSeconds:   how long to keep the HTTP server alive after printing JSON (default: 300, min 10)
  - includeAmazonSourceUrl: (boolean) if true, also include amazonDownloadUrl in JSON (default: false)

Dependency:
  This skill depends on `linkfox-amazon-store-auth`. On startup the script runs
  `check_auth_dependency.py`. If the dependency is missing, the script exits with
  the dedicated exit code 42 and emits a `DEPENDENCY_MISSING:` line on stderr so
  the calling agent can trigger installation of the dependency skill.
"""

from __future__ import annotations

import json
import os
import sys
import time
import tempfile
import gzip
import shutil
import subprocess
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError
from pathlib import Path


API_BASE_URL = (
    os.environ.get("LINKFOX_TOOL_GATEWAY")
    or os.environ.get("STORE_API_BASE_URL")
    or os.environ.get("SPAPI_BASE_URL", "https://tool-gateway.linkfox.com")
)
STORE_TOKENS_ENDPOINT = f"{API_BASE_URL}/spApi/storeTokens"
DEVELOPER_PROXY_ENDPOINT = f"{API_BASE_URL}/spApi/developerProxy"

DEFAULT_POLL_INTERVAL = 30  # seconds
DEFAULT_MAX_ATTEMPTS = 20

REQUIRED_SKILL = "linkfox-amazon-store-auth"
DEPENDENCY_EXIT_CODE = 42


def ensure_auth_skill_available() -> None:
    """
    Run check_auth_dependency.py (sibling script) to verify that the required
    dependency skill `linkfox-amazon-store-auth` is installed.

    Behaviour:
      - dependency found       → return silently
      - dependency missing     → exit 42 with DEPENDENCY_MISSING: on stderr
      - check script missing   → exit 42 with a conservative warning
                                 (agent should still treat it as missing)
    """
    here = Path(__file__).resolve().parent
    checker = here / "check_auth_dependency.py"

    if not checker.exists():
        payload = {
            "missingSkill": REQUIRED_SKILL,
            "reason": "check_auth_dependency.py not found next to get_report.py",
            "suggestedActions": [
                f"Install or restore skill '{REQUIRED_SKILL}' before running this skill.",
            ],
        }
        print(f"DEPENDENCY_MISSING: {json.dumps(payload, ensure_ascii=False)}", file=sys.stderr)
        sys.exit(DEPENDENCY_EXIT_CODE)

    try:
        result = subprocess.run(
            [sys.executable, str(checker)],
            capture_output=True,
            text=True,
            timeout=10,
        )
    except Exception as exc:  # pragma: no cover - defensive
        payload = {
            "missingSkill": REQUIRED_SKILL,
            "reason": f"Failed to run dependency check: {exc}",
        }
        print(f"DEPENDENCY_MISSING: {json.dumps(payload, ensure_ascii=False)}", file=sys.stderr)
        sys.exit(DEPENDENCY_EXIT_CODE)

    # Forward the checker's stderr so the agent can read it verbatim.
    if result.stderr:
        sys.stderr.write(result.stderr)
        if not result.stderr.endswith("\n"):
            sys.stderr.write("\n")

    if result.returncode == 0:
        return

    # Treat any non-zero return code as missing dependency; always use code 42.
    sys.exit(DEPENDENCY_EXIT_CODE)


def get_api_key():
    """
    获取配置在环境变量的API Key。
    如果获取不到，按 SKILL.md 的 **## 解决认证和积分问题** 处理。
    """
    key = os.environ.get("LINKFOX_AGENT_API_KEY") or os.environ.get("LINKFOXAGENT_API_KEY")
    if not key:
        print(
            "API Key 未配置",
            file=sys.stderr,
        )
        sys.exit(1)
    return key


def call_api(endpoint: str, params: dict) -> dict:
    """Call LinkFox API endpoint."""
    api_key = get_api_key()
    data = json.dumps(params).encode("utf-8")

    req = Request(
        endpoint,
        data=data,
        headers={
            "Authorization": api_key,
            "Content-Type": "application/json",
            "User-Agent": "LinkFox-Skill/1.0",
        },
        method="POST",
    )

    try:
        with urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as e:
        body = e.read().decode("utf-8") if e.fp else ""
        return {"error": f"HTTP {e.code}: {e.reason}", "details": body}
    except URLError as e:
        return {"error": f"Connection failed: {e.reason}"}


def get_store_tokens(seller_id: str, region: str) -> dict:
    """Get access tokens for the specified store."""
    print(f"🔑 Fetching access token for seller {seller_id} in region {region}...", file=sys.stderr)
    return call_api(STORE_TOKENS_ENDPOINT, {"sellerId": seller_id, "region": region})


def developer_proxy_call(region: str, path: str, method: str, access_token: str,
                         query_string: str = None, body: str = None, content_type: str = "application/json") -> dict:
    """Call Amazon APIs through the developer proxy."""
    params = {
        "region": region,
        "path": path,
        "method": method,
        "amzAccessToken": access_token,
    }
    if query_string:
        params["queryString"] = query_string
    if body:
        params["body"] = body
    if content_type:
        params["contentType"] = content_type

    return call_api(DEVELOPER_PROXY_ENDPOINT, params)


def create_report(
    region: str,
    access_token: str,
    report_type: str,
    marketplace_ids: list,
    data_start_time: str = None,
    data_end_time: str = None,
    report_options: dict = None,
    last_updated_date: str = None,
) -> dict:
    """Request a new report from Amazon."""
    print(f"📊 Requesting report: {report_type}", file=sys.stderr)

    body_data = {
        "reportType": report_type,
        "marketplaceIds": marketplace_ids,
    }
    if data_start_time:
        body_data["dataStartTime"] = data_start_time
    if data_end_time:
        body_data["dataEndTime"] = data_end_time
    if last_updated_date:
        body_data["lastUpdatedDate"] = last_updated_date
    if report_options and isinstance(report_options, dict):
        body_data["reportOptions"] = report_options

    result = developer_proxy_call(
        region=region,
        path="reports/2021-06-30/reports",
        method="POST",
        access_token=access_token,
        body=json.dumps(body_data),
        content_type="application/json"
    )

    return result


def get_report_status(region: str, access_token: str, report_id: str) -> dict:
    """Check the status of a report."""
    result = developer_proxy_call(
        region=region,
        path=f"reports/2021-06-30/reports/{report_id}",
        method="GET",
        access_token=access_token
    )
    return result


def get_report_document(region: str, access_token: str, report_document_id: str) -> dict:
    """Get report document download information."""
    result = developer_proxy_call(
        region=region,
        path=f"reports/2021-06-30/documents/{report_document_id}",
        method="GET",
        access_token=access_token
    )
    return result


def download_report(url: str, output_path: str) -> bool:
    """Download report file from URL."""
    print(f"⬇️  Downloading report to {output_path}...", file=sys.stderr)

    try:
        req = Request(url, headers={"User-Agent": "LinkFox-Skill/1.0"})
        with urlopen(req, timeout=60) as response:
            with open(output_path, 'wb') as f:
                shutil.copyfileobj(response, f)
        print(f"✓ Downloaded successfully", file=sys.stderr)
        return True
    except Exception as e:
        print(f"❌ Download failed: {e}", file=sys.stderr)
        return False


def extract_if_compressed(file_path: str, extract_to: str) -> str:
    """Extract file if it's gzip compressed."""
    try:
        # Check if file is gzip compressed
        with open(file_path, 'rb') as f:
            if f.read(2) == b'\x1f\x8b':  # gzip magic number
                print(f"📦 Detected gzip compression, extracting...", file=sys.stderr)
                extracted_path = os.path.join(extract_to, "report_data.txt")
                with gzip.open(file_path, 'rb') as f_in:
                    with open(extracted_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                print(f"✓ Extracted to {extracted_path}", file=sys.stderr)
                return extracted_path
    except Exception as e:
        print(f"⚠️  Extraction failed: {e}, using original file", file=sys.stderr)

    return file_path


def _start_local_extracted_http_server(
    file_abs: Path,
    host: str,
    port: int,
) -> tuple[ThreadingHTTPServer, threading.Thread, str]:
    """
    Serve the extracted report file over HTTP on localhost so the user can
    download the **already decompressed** file via a browser or curl.

    Only paths '/' and '/download' are served. Bind defaults to 127.0.0.1.
    """
    file_abs = file_abs.resolve()
    if not file_abs.is_file():
        raise FileNotFoundError(str(file_abs))

    safe_name = file_abs.name.replace('"', "").replace("\\", "") or "report.txt"
    holder: dict[str, Path] = {"p": file_abs}

    class OneFileHandler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args) -> None:
            return

        def do_GET(self) -> None:  # noqa: N802
            path = self.path.split("?")[0]
            if path not in ("/", "/download"):
                self.send_error(404)
                return
            p = holder["p"]
            if not p.is_file():
                self.send_error(410, "Report file no longer available")
                return
            try:
                self.send_response(200)
                self.send_header("Content-Type", "application/octet-stream")
                self.send_header(
                    "Content-Disposition",
                    f'attachment; filename="{safe_name}"',
                )
                self.send_header("Content-Length", str(p.stat().st_size))
                self.end_headers()
                with p.open("rb") as fp:
                    shutil.copyfileobj(fp, self.wfile)
            except BrokenPipeError:
                return
            except Exception:
                if not self.wfile.closed:
                    try:
                        self.send_error(500)
                    except Exception:
                        pass

    ThreadingHTTPServer.allow_reuse_address = True
    srv = ThreadingHTTPServer((host, int(port)), OneFileHandler)
    actual_port = srv.server_address[1]
    thread = threading.Thread(target=srv.serve_forever, daemon=True)
    thread.start()
    time.sleep(0.15)
    url = f"http://{host}:{actual_port}/download"
    return srv, thread, url


def main():
    if len(sys.argv) < 2:
        print("Usage: get_report.py '<JSON parameters>'", file=sys.stderr)
        print('Required fields: sellerId, region, reportType, marketplaceIds', file=sys.stderr)
        print('Example: get_report.py \'{"sellerId": "A123", "region": "NA", "reportType": "GET_MERCHANT_LISTINGS_ALL_DATA", "marketplaceIds": ["ATVPDKIKX0DER"]}\'', file=sys.stderr)
        sys.exit(1)

    try:
        params = json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    # Dependency check: ensure linkfox-amazon-store-auth is installed before
    # touching any gateway endpoint. Agents should read the DEPENDENCY_MISSING:
    # payload on stderr and trigger installation of the auth skill.
    if not params.get("skipDepCheck"):
        ensure_auth_skill_available()

    # Validate required parameters
    required_fields = ["sellerId", "region", "reportType", "marketplaceIds"]
    missing = [f for f in required_fields if f not in params]
    if missing:
        print(f"❌ Missing required parameters: {', '.join(missing)}", file=sys.stderr)
        sys.exit(1)

    seller_id = params["sellerId"]
    region = params["region"]
    report_type = params["reportType"]
    marketplace_ids = params["marketplaceIds"]
    data_start_time = params.get("dataStartTime")
    data_end_time = params.get("dataEndTime")
    last_updated_date = params.get("lastUpdatedDate")
    report_options = params.get("reportOptions")
    poll_interval = params.get("pollInterval", DEFAULT_POLL_INTERVAL)
    max_attempts = params.get("maxAttempts", DEFAULT_MAX_ATTEMPTS)

    # Step 1: Get access tokens
    tokens_result = get_store_tokens(seller_id, region)
    if "error" in tokens_result or "accessToken" not in tokens_result:
        print(f"❌ Failed to get access token: {tokens_result}", file=sys.stderr)
        sys.exit(1)

    access_token = tokens_result["accessToken"]
    print("✓ Access token retrieved", file=sys.stderr)

    # Step 2: Create report request
    create_result = create_report(
        region,
        access_token,
        report_type,
        marketplace_ids,
        data_start_time,
        data_end_time,
        report_options if isinstance(report_options, dict) else None,
        last_updated_date if isinstance(last_updated_date, str) else None,
    )

    if "error" in create_result:
        print(f"❌ Failed to create report: {create_result}", file=sys.stderr)
        sys.exit(1)

    if create_result.get("errcode") != 200:
        print(f"❌ API error: {create_result}", file=sys.stderr)
        sys.exit(1)

    http_status = create_result.get("httpStatus")
    if http_status != 202:
        body = json.loads(create_result.get("body", "{}"))
        print(f"❌ Report gateway error (HTTP {http_status}): {body}", file=sys.stderr)
        sys.exit(1)

    # Parse report ID from response
    body = json.loads(create_result.get("body", "{}"))
    report_id = body.get("reportId")
    if not report_id:
        print(f"❌ No reportId in response: {body}", file=sys.stderr)
        sys.exit(1)

    print(f"✓ Report request created: {report_id}", file=sys.stderr)

    # Step 3: Poll for report completion
    print(f"⏳ Polling for report completion (checking every {poll_interval}s, max {max_attempts} attempts)...", file=sys.stderr)

    for attempt in range(1, max_attempts + 1):
        status_result = get_report_status(region, access_token, report_id)

        if "error" in status_result or status_result.get("errcode") != 200:
            print(f"❌ Failed to check status: {status_result}", file=sys.stderr)
            sys.exit(1)

        status_body = json.loads(status_result.get("body", "{}"))
        processing_status = status_body.get("processingStatus")

        print(f"[{attempt}/{max_attempts}] Status: {processing_status}", file=sys.stderr)

        if processing_status == "DONE":
            report_document_id = status_body.get("reportDocumentId")
            if not report_document_id:
                print(f"❌ No reportDocumentId in response: {status_body}", file=sys.stderr)
                sys.exit(1)
            print(f"✓ Report completed: {report_document_id}", file=sys.stderr)
            break
        elif processing_status == "FATAL":
            print(f"❌ Report generation failed with FATAL status", file=sys.stderr)
            print(f"Details: {json.dumps(status_body, indent=2)}", file=sys.stderr)
            sys.exit(1)
        elif processing_status == "CANCELLED":
            print(f"❌ Report was cancelled", file=sys.stderr)
            sys.exit(1)
        elif processing_status in ["IN_QUEUE", "IN_PROGRESS"]:
            if attempt < max_attempts:
                time.sleep(poll_interval)
            else:
                print(f"❌ Timeout: Report still processing after {max_attempts} attempts", file=sys.stderr)
                sys.exit(1)
        else:
            print(f"❌ Unknown status: {processing_status}", file=sys.stderr)
            sys.exit(1)
    else:
        print(f"❌ Max attempts reached without completion", file=sys.stderr)
        sys.exit(1)

    # Step 4: Get report document info
    print(f"📄 Fetching report document info...", file=sys.stderr)
    doc_result = get_report_document(region, access_token, report_document_id)

    if "error" in doc_result or doc_result.get("errcode") != 200:
        print(f"❌ Failed to get document info: {doc_result}", file=sys.stderr)
        sys.exit(1)

    doc_body = json.loads(doc_result.get("body", "{}"))
    download_url = doc_body.get("url")
    if not download_url:
        print(f"❌ No download URL in response: {doc_body}", file=sys.stderr)
        sys.exit(1)

    print(f"✓ Report document metadata retrieved (downloading to local temp...)", file=sys.stderr)

    # Step 5: Download report
    temp_dir = tempfile.mkdtemp(prefix="amazon_report_")
    print(f"📁 Temporary directory: {temp_dir}", file=sys.stderr)

    download_path = os.path.join(temp_dir, "report_download")
    if not download_report(download_url, download_path):
        print(f"❌ Download failed", file=sys.stderr)
        sys.exit(1)

    # Step 6: Extract if compressed
    final_path = extract_if_compressed(download_path, temp_dir)
    resolved_path = str(Path(final_path).resolve())
    resolved_file = Path(final_path).resolve()
    file_name = resolved_file.name
    local_file_uri = resolved_file.as_uri()

    # Show file info
    file_size = os.path.getsize(final_path)
    print(f"\n✅ Report downloaded successfully!", file=sys.stderr)
    print(f"📊 Report Type: {report_type}", file=sys.stderr)
    print(f"\n📂 文件保存位置（本地，已解压）:", file=sys.stderr)
    print(f"    完整路径: {resolved_path}", file=sys.stderr)
    print(f"    文件名:   {file_name}", file=sys.stderr)
    print(f"📦 Size: {file_size:,} bytes", file=sys.stderr)
    print(f"\n🖥️  本机 file URI（便于部分客户端直接打开本地文件）:", file=sys.stderr)
    print(f"    {local_file_uri}", file=sys.stderr)

    serve_http = params.get("serveExtractedFileHttp", True)
    serve_host = str(params.get("serveHost") or "127.0.0.1")
    serve_port = int(params.get("servePort") or 0)
    serve_seconds = int(params.get("serveSeconds", 300))
    if serve_http:
        serve_seconds = max(10, serve_seconds)

    http_server: ThreadingHTTPServer | None = None
    http_thread: threading.Thread | None = None
    extracted_http_url: str | None = None
    if serve_http:
        try:
            http_server, http_thread, extracted_http_url = _start_local_extracted_http_server(
                Path(final_path), serve_host, serve_port
            )
        except OSError as e:
            print(f"⚠️  Could not start local HTTP server for extracted file: {e}", file=sys.stderr)
            print("   Falling back to path/localFileUri only (no extractedFileHttpUrl).", file=sys.stderr)
            http_server = None
            http_thread = None
            extracted_http_url = None

    if extracted_http_url:
        print(f"\n🌐 已解压文件 · 本机 HTTP 下载链接（{serve_seconds}s 内用浏览器打开即可保存）:", file=sys.stderr)
        print(f"    {extracted_http_url}", file=sys.stderr)
        print(
            "    （仅本机可访问；脚本在计时结束后会关闭服务，链接即失效。）",
            file=sys.stderr,
        )

    # Show first few lines as preview
    try:
        with open(final_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()[:5]
        if lines:
            print(f"\n📋 Preview (first {len(lines)} lines):", file=sys.stderr)
            for line in lines:
                print(f"  {line.rstrip()}", file=sys.stderr)
    except Exception as e:
        print(f"⚠️  Could not preview file: {e}", file=sys.stderr)

    # Output final result as JSON
    compression_algorithm = doc_body.get("compressionAlgorithm")
    include_amazon = bool(params.get("includeAmazonSourceUrl"))
    if params.get("omitAmazonDownloadUrl") is True:
        include_amazon = False
    elif params.get("omitAmazonDownloadUrl") is False:
        include_amazon = True

    result = {
        "success": True,
        "reportId": report_id,
        "reportDocumentId": report_document_id,
        "reportType": report_type,
        "downloadPath": resolved_path,
        "fileName": file_name,
        "localFileUri": local_file_uri,
        "tempDirectory": temp_dir,
        "fileSize": file_size,
    }
    if compression_algorithm:
        result["compressionAlgorithm"] = compression_algorithm
    if extracted_http_url:
        result["extractedFileHttpUrl"] = extracted_http_url
        result["extractedFileHttpServeSeconds"] = serve_seconds
        result["extractedFileHttpNote"] = (
            "本机临时 HTTP 服务提供的直链，用于下载**已解压**后的报告文件；"
            f"仅在 serveSeconds={serve_seconds} 内有效，服务停止后链接不可用。"
            " 需在运行本脚本的同一台机器上用浏览器访问（默认绑定 127.0.0.1）。"
        )
    if include_amazon:
        result["amazonDownloadUrl"] = download_url
        result["amazonDownloadUrlNote"] = (
            "Amazon 预签名源地址（通常为压缩包）；与 extractedFileHttpUrl 不同，"
            "一般无需提供给终端用户。"
        )

    emit_result(result, lf_inline_flag())

    if http_server is not None:
        try:
            print(
                f"\n⏳ 本地 HTTP 服务保持 {serve_seconds}s，以便你通过上方链接下载已解压文件…",
                file=sys.stderr,
            )
            time.sleep(serve_seconds)
        except KeyboardInterrupt:
            print("\n⚠️  Interrupted; shutting down local HTTP server.", file=sys.stderr)
        finally:
            http_server.shutdown()
            http_server.server_close()
            if http_thread is not None:
                http_thread.join(timeout=5.0)
            print("✓ Local HTTP server stopped.", file=sys.stderr)


if __name__ == "__main__":
    main()


# ===== LinkFox 统一输出层（落盘 + 摘要，无缓存）=====
# 本块追加到共享模块（_xxx_common.py）末尾，供各入口脚本调用 emit_result()。
# 依赖：json, os, sys, time, secrets, tempfile（共享模块通常已 import json/os/sys；
#       若缺 time/secrets/tempfile，请在文件顶部补 import）。

import time as _lf_time
import secrets as _lf_secrets
import tempfile as _lf_tempfile

LF_SMALL_THRESHOLD = 8000
_LF_SESSION_CACHE: dict = {}

SLUG = "linkfox-amazon-store-report"


def _lf_root() -> str:
    cached = _LF_SESSION_CACHE.get("_root")
    if cached:
        return cached
    candidates = []
    acpx = (os.environ.get("ACPX_WORKSPACES") or "").strip()
    if acpx:
        acpx = acpx.split(os.pathsep)[0].strip()
        if acpx:
            candidates.append(os.path.join(acpx, "linkfox"))
    candidates.append(os.path.join(os.getcwd(), "linkfox"))
    candidates.append(os.path.join(os.path.expanduser("~"), "linkfox"))
    candidates.append(os.path.join(_lf_tempfile.gettempdir(), "linkfox"))
    for root in candidates:
        try:
            os.makedirs(root, exist_ok=True)
            probe = os.path.join(root, ".write_probe")
            with open(probe, "w", encoding="utf-8") as f:
                f.write("")
            os.remove(probe)
        except OSError:
            continue
        root = os.path.abspath(root)
        _LF_SESSION_CACHE["_root"] = root
        return root
    fallback = os.path.abspath(candidates[-1])
    _LF_SESSION_CACHE["_root"] = fallback
    return fallback


def _lf_iso(ts: float) -> str:
    return _lf_time.strftime("%Y-%m-%dT%H:%M:%S%z", _lf_time.localtime(ts))


def _lf_session_id(ts: float) -> str:
    env = os.environ.get("SESSION_ID")
    if env:
        return env.strip()
    if "_auto" not in _LF_SESSION_CACHE:
        _LF_SESSION_CACHE["_auto"] = (
            _lf_time.strftime("%H%M%S", _lf_time.localtime(ts)) + "-" + _lf_secrets.token_hex(3)
        )
    return _LF_SESSION_CACHE["_auto"]


def _lf_find_main_list(obj):
    best = (None, None, -1)

    def walk(node, path):
        nonlocal best
        if isinstance(node, list):
            if len(node) > best[2]:
                best = (path, node, len(node))
        elif isinstance(node, dict):
            for k, v in node.items():
                walk(v, f"{path}.{k}" if path else k)

    walk(obj, "")
    return best[0], best[1]


def _lf_summarize(result) -> None:
    if not isinstance(result, dict):
        print(f"Response type: {type(result).__name__}")
        print(json.dumps(result, ensure_ascii=False)[:500])
        return
    print(f"Top-level keys: {list(result.keys())}")
    for k in ("errcode", "errorCode", "code", "errmsg", "msg",
              "total", "totalCount", "count", "currentPage", "perPage",
              "costToken", "costTime", "success"):
        if k in result:
            v = result[k]
            if isinstance(v, (int, float, bool, str)):
                print(f"  {k}: {v}")
    list_path, main_list = _lf_find_main_list(result)
    if list_path is not None and main_list:
        print(f"\nMain list field: `{list_path}` (length={len(main_list)})")
        sample = main_list[:3]
        print(f"Sample (first {len(sample)} of {len(main_list)}):")
        print(json.dumps(sample, indent=2, ensure_ascii=False))


def _lf_ensure_meta(root: str, session_dir: str, date_str: str, sid: str, ts: float) -> None:
    meta_path = os.path.join(session_dir, "_meta.json")
    if os.path.exists(meta_path):
        return
    meta = {
        "session_id": sid,
        "date": date_str,
        "started_at": _lf_iso(ts),
        "skills_called": [],
        "deliverables": [],
        "data_files": [],
        "media_files": [],
    }
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    try:
        with open(os.path.join(root, "index.jsonl"), "a", encoding="utf-8") as f:
            f.write(
                json.dumps(
                    {
                        "session_id": sid,
                        "date": date_str,
                        "path": os.path.relpath(session_dir, root),
                        "started_at": _lf_iso(ts),
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )
    except OSError:
        pass


def _lf_update_meta(session_dir: str, *, skill: str, file_rel: str, ts: float) -> None:
    meta_path = os.path.join(session_dir, "_meta.json")
    try:
        with open(meta_path, encoding="utf-8") as f:
            meta = json.load(f)
    except (OSError, json.JSONDecodeError):
        return
    if skill and skill not in meta.setdefault("skills_called", []):
        meta["skills_called"].append(skill)
    files = meta.setdefault("data_files", [])
    if file_rel not in files:
        files.append(file_rel)
    meta["last_used_at"] = _lf_iso(ts)
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)


def emit_result(result, slug=SLUG, inline=False):
    """落盘完整响应到 linkfox/<date>/<session>/data/<slug>-<ts>.json；大响应只打印摘要。无缓存。"""
    serialized = json.dumps(result, ensure_ascii=False, indent=2)
    ts = _lf_time.time()
    date_str = _lf_time.strftime("%Y-%m-%d", _lf_time.localtime(ts))
    sid = _lf_session_id(ts)
    root = _lf_root()
    session_dir = os.path.join(root, date_str, sid)
    os.makedirs(session_dir, exist_ok=True)
    _lf_ensure_meta(root, session_dir, date_str, sid, ts)
    data_dir = os.path.join(session_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    out = os.path.join(data_dir, f"{slug}-{int(ts * 1_000_000)}.json")
    try:
        with open(out, "w", encoding="utf-8") as f:
            f.write(serialized)
        print(f"Saved full response: {out} ({len(serialized)} bytes)")
    except OSError as e:
        print(f"Failed to save to {out}: {e}", file=sys.stderr)
    _lf_update_meta(session_dir, skill=slug, file_rel=os.path.relpath(out, session_dir), ts=ts)
    if inline or len(serialized.encode("utf-8")) <= LF_SMALL_THRESHOLD:
        print(serialized)
    else:
        _lf_summarize(result)


def lf_inline_flag() -> bool:
    """入口脚本用：从 sys.argv 判断是否 --inline。"""
    return "--inline" in sys.argv
