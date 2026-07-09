#!/usr/bin/env python3
"""
Amazon Ads Report Retrieval - LinkFox Skill (linkfox-amazon-ads-report)
=======================================================================

Requests an Amazon Advertising report (SP/SB/SD/ST/DSP) via v3 API (two-stage:
create → poll; the poll response carries the download URL, GZIP_JSON/CSV).

脚本仅做"异步报告执行器"：带着调用方给的入参请求 Amazon，轮询到完成后下载解压。
`adProduct` / `groupBy` / `columns` 由调用方（agent）在 `references/report-types/`
下的对应 .md 文件中查表后显式传入。

Usage:
  python get_report.py '{"profileId": 1234567890, "region": "NA",
                             "reportTypeId": "spCampaigns",
                             "adProduct": "SPONSORED_PRODUCTS",
                             "groupBy": ["campaign"],
                             "columns": ["date","campaignId","campaignName",
                                         "impressions","clicks","cost"],
                             "startDate": "2026-04-27","endDate": "2026-05-03"}'

Required parameters:
  - profileId         number
  - region            NA / EU / FE
  - reportTypeId      e.g. spCampaigns / sbAdGroup（见 references/report-types/<sp|sb>/）
  - adProduct         SPONSORED_PRODUCTS / SPONSORED_BRANDS（来源 frontmatter）
  - groupBy           list（来源 frontmatter）
  - columns           list（来源 Base metrics 表）
  - startDate / endDate  YYYY-MM-DD

Optional parameters:
  - name              报告显示名（默认按 reportTypeId + 时间窗自动生成）
  - timeUnit          DAILY / SUMMARY，默认 SUMMARY
  - format            默认 GZIP_JSON（DSP 等类型支持 CSV）
  - pollInterval      默认 30 秒
  - maxAttempts       默认 20
  - skipDepCheck      跳过依赖检查（默认 false）
  - serveExtractedFileHttp / serveHost / servePort / serveSeconds
                      本机 HTTP 暴露已解压文件，默认开启 300s
  - includeAmazonSourceUrl
                      是否把 Amazon 预签名 URL 也回给用户，默认 false
"""

import json
import os
import re
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


# 生产默认走 tool-gateway.linkfox.com；开发/测试期可 export AMAZON_ADS_BASE_URL=<url> 覆盖
API_BASE_URL = (
    os.environ.get("LINKFOX_TOOL_GATEWAY")
    or os.environ.get("AMAZON_ADS_BASE_URL")
    or "https://tool-gateway.linkfox.com"
)
STORE_TOKENS_ENDPOINT = f"{API_BASE_URL}/amazonAds/storeTokens"
DEVELOPER_PROXY_ENDPOINT = f"{API_BASE_URL}/amazonAds/developerProxy"

DEFAULT_POLL_INTERVAL = 30
DEFAULT_MAX_ATTEMPTS = 20

REQUIRED_SKILL = "linkfox-amazon-ads-auth"
DEPENDENCY_EXIT_CODE = 42

SP_CREATE_REPORT_CONTENT_TYPE = "application/vnd.createasyncreportrequest.v3+json"

# Amazon 对相同参数的报告请求做去重：命中时返回 HTTP 425，body 形如：
# {"code":"425","detail":"The Request is a duplicate of : 7df1ef5d-45ba-40cc-b607-ff2148cf4f5e"}
# 我们从中解析出老 reportId，无缝转为轮询该老报告。
_DUPLICATE_REPORT_ID_RE = re.compile(r"duplicate of\s*:\s*([0-9a-fA-F-]{36})")


def extract_duplicate_report_id(body: str):
    if not body:
        return None
    m = _DUPLICATE_REPORT_ID_RE.search(body)
    return m.group(1) if m else None

# 列与 groupBy 的真相源是 references/report-types/<adProduct>/<reportTypeId>.md。
# Agent 在调用前按 SKILL.md "调用前必读" 流程读取 frontmatter + Base metrics 表，
# 构造 adProduct/groupBy/columns 三个参数后显式传入本脚本。


def ensure_auth_skill_available() -> None:
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
    except Exception as exc:
        payload = {
            "missingSkill": REQUIRED_SKILL,
            "reason": f"Failed to run dependency check: {exc}",
        }
        print(f"DEPENDENCY_MISSING: {json.dumps(payload, ensure_ascii=False)}", file=sys.stderr)
        sys.exit(DEPENDENCY_EXIT_CODE)

    if result.stderr:
        sys.stderr.write(result.stderr)
        if not result.stderr.endswith("\n"):
            sys.stderr.write("\n")

    if result.returncode == 0:
        return
    sys.exit(DEPENDENCY_EXIT_CODE)


def get_api_key():
    key = os.environ.get("LINKFOX_AGENT_API_KEY") or os.environ.get("LINKFOXAGENT_API_KEY")
    if not key:
        print(
            "❌ API Key not configured. Please set the environment variable:\n"
            "  export LINKFOXAGENT_API_KEY=your-key-here",
            file=sys.stderr,
        )
        sys.exit(1)
    return key


def call_api(endpoint: str, params: dict) -> dict:
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
        with urlopen(req, timeout=60) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as e:
        body = e.read().decode("utf-8") if e.fp else ""
        return {"error": f"HTTP {e.code}: {e.reason}", "details": body}
    except URLError as e:
        return {"error": f"Connection failed: {e.reason}"}


def get_store_tokens(profile_id: int) -> dict:
    print(f"🔑 Fetching access token for profileId={profile_id}...", file=sys.stderr)
    return call_api(STORE_TOKENS_ENDPOINT, {"profileId": profile_id})


def developer_proxy_call(region: str, path: str, method: str, access_token: str, profile_id: int,
                         query_string: str = None, body: str = None,
                         content_type: str = "application/json") -> dict:
    params = {
        "region": region,
        "path": path,
        "method": method,
        "amzAccessToken": access_token,
        "profileId": profile_id,
    }
    if query_string:
        params["queryString"] = query_string
    if body:
        params["body"] = body
    if content_type:
        params["contentType"] = content_type
    return call_api(DEVELOPER_PROXY_ENDPOINT, params)


def create_report(region: str, access_token: str, profile_id: int,
                  report_type_id: str, start_date: str, end_date: str,
                  name: str, ad_product: str, group_by: list, columns: list,
                  time_unit: str, fmt: str) -> dict:
    print(f"📊 Requesting SP report: {report_type_id} ({start_date} ~ {end_date})", file=sys.stderr)
    body = {
        "name": name,
        "startDate": start_date,
        "endDate": end_date,
        "configuration": {
            "adProduct": ad_product,
            "groupBy": group_by,
            "columns": columns,
            "reportTypeId": report_type_id,
            "timeUnit": time_unit,
            "format": fmt,
        },
    }
    return developer_proxy_call(
        region=region,
        path="reporting/reports",
        method="POST",
        access_token=access_token,
        profile_id=profile_id,
        body=json.dumps(body),
        content_type=SP_CREATE_REPORT_CONTENT_TYPE,
    )


def get_report_status(region: str, access_token: str, profile_id: int, report_id: str) -> dict:
    return developer_proxy_call(
        region=region,
        path=f"reporting/reports/{report_id}",
        method="GET",
        access_token=access_token,
        profile_id=profile_id,
    )


def download_report(url: str, output_path: str) -> bool:
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
    try:
        with open(file_path, 'rb') as f:
            head = f.read(2)
        if head == b'\x1f\x8b':
            print(f"📦 Detected gzip compression, extracting...", file=sys.stderr)
            extracted_path = os.path.join(extract_to, "report_data.json")
            with gzip.open(file_path, 'rb') as f_in:
                with open(extracted_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            print(f"✓ Extracted to {extracted_path}", file=sys.stderr)
            return extracted_path
    except Exception as e:
        print(f"⚠️  Extraction failed: {e}, using original file", file=sys.stderr)
    return file_path


def _start_local_extracted_http_server(file_abs: Path, host: str, port: int):
    file_abs = file_abs.resolve()
    if not file_abs.is_file():
        raise FileNotFoundError(str(file_abs))
    safe_name = file_abs.name.replace('"', "").replace("\\", "") or "report.json"
    holder = {"p": file_abs}

    class OneFileHandler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):
            return

        def do_GET(self):
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
                self.send_header("Content-Disposition", f'attachment; filename="{safe_name}"')
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
        print('Required: profileId, region, reportTypeId, startDate, endDate', file=sys.stderr)
        sys.exit(1)

    try:
        params = json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    if not params.get("skipDepCheck"):
        ensure_auth_skill_available()

    # 入参分两种模式：
    # - 全链路：创建 → 轮询 → 下载（需要全部必填）
    # - 仅轮询：调用方传入已有 reportId（例如上次客户端超时但报告仍在跑；或命中 Amazon 去重）→ 只需 profileId / region
    provided_report_id = params.get("reportId")
    poll_only = bool(provided_report_id)

    if poll_only:
        required = ["profileId", "region"]
    else:
        required = ["profileId", "region", "reportTypeId", "startDate", "endDate",
                    "adProduct", "groupBy", "columns"]
    missing = [f for f in required if not params.get(f)]
    if missing:
        if poll_only:
            print(
                f"❌ Missing required parameters (poll-only mode): {', '.join(missing)}",
                file=sys.stderr,
            )
        else:
            print(
                f"❌ Missing required parameters: {', '.join(missing)}\n"
                f"   `adProduct` / `groupBy` / `columns` 必须由调用方显式传入。\n"
                f"   请先打开 references/report-types/<adProduct-dir>/{params.get('reportTypeId','<reportTypeId>')}.md：\n"
                f"     • 从 frontmatter 读出 adProduct / groupBy\n"
                f"     • 从 Base metrics 表挑选本次需要的 columns\n"
                f"   然后调用本脚本并传入这三个字段。\n"
                f"   若只想轮询一个已在跑的 reportId，可传入 `reportId` 字段（无需 startDate/endDate/adProduct/groupBy/columns）。",
                file=sys.stderr,
            )
        sys.exit(1)

    profile_id = int(params["profileId"])
    region = params["region"]
    report_type_id = params.get("reportTypeId")
    start_date = params.get("startDate")
    end_date = params.get("endDate")

    # 数据新鲜度提示（非强制拦截）：上游数据有 ~12 小时延迟，endDate=今天往往拉到空或不完整数据。
    # 我们只提示不拦截，是否需要修改日期由调用方自行决定。仅全链路模式需要此检查。
    if not poll_only and end_date:
        try:
            from datetime import datetime, date, timedelta
            _end = datetime.strptime(end_date, "%Y-%m-%d").date()
            _today = date.today()
            if _end >= _today:
                print(
                    f"⚠️  endDate={end_date} 为今天或未来日期。"
                    f"上游数据有 ~12 小时延迟，建议 endDate <= {(_today - timedelta(days=1)).isoformat()}（昨天及之前）。"
                    "本次仍按入参提交，但可能返回空或不完整数据。",
                    file=sys.stderr,
                )
        except ValueError:
            # 日期格式错误交给上游返回详细原因
            pass
    name = params.get("name") or (f"{report_type_id}_{start_date}_{end_date}" if report_type_id else None)
    ad_product = params.get("adProduct")
    group_by = params.get("groupBy")
    columns = params.get("columns")
    time_unit = params.get("timeUnit", "SUMMARY")
    fmt = params.get("format", "GZIP_JSON")
    poll_interval = params.get("pollInterval", DEFAULT_POLL_INTERVAL)
    max_attempts = params.get("maxAttempts", DEFAULT_MAX_ATTEMPTS)

    # Step 1: 取令牌
    tokens_result = get_store_tokens(profile_id)
    if "error" in tokens_result or "accessToken" not in tokens_result:
        print(f"❌ Failed to get access token: {tokens_result}", file=sys.stderr)
        sys.exit(1)
    access_token = tokens_result["accessToken"]
    print("✓ Access token retrieved", file=sys.stderr)

    # Step 2: 获取待轮询的 reportId —— 两种来源
    #   (a) 调用方直接传 reportId（例如上次超时但报告仍在跑）
    #   (b) 向 Amazon 发起创建；若命中同参数去重（HTTP 425），解析老 reportId 后无缝转为轮询
    if poll_only:
        report_id = provided_report_id
        print(f"↩️  复用已有 reportId={report_id}，跳过创建，直接轮询。", file=sys.stderr)
    else:
        create_result = create_report(region, access_token, profile_id,
                                      report_type_id, start_date, end_date,
                                      name, ad_product, group_by, columns, time_unit, fmt)
        if "error" in create_result:
            print(f"❌ Failed to create report: {create_result}", file=sys.stderr)
            sys.exit(1)
        http_status = create_result.get("httpStatus")
        raw_body = create_result.get("body", "") or ""

        # Amazon 的同参数去重：HTTP 425 + body 含老 reportId。自动转入轮询该老报告。
        if http_status == 425:
            dedup_id = extract_duplicate_report_id(raw_body)
            if not dedup_id:
                print(
                    f"❌ HTTP 425 but could not parse duplicate reportId: {raw_body}",
                    file=sys.stderr,
                )
                sys.exit(1)
            print(
                f"↩️  Amazon 返回 HTTP 425：同参数已有在跑的报告 (reportId={dedup_id})，"
                f"改为轮询该已有报告，不再新建。",
                file=sys.stderr,
            )
            report_id = dedup_id
        elif http_status is None or http_status // 100 != 2:
            print(f"❌ Amazon Ads API error (HTTP {http_status}): {raw_body}", file=sys.stderr)
            sys.exit(1)
        else:
            try:
                body = json.loads(raw_body or "{}")
            except Exception as e:
                print(f"❌ Failed to parse create response body: {e}", file=sys.stderr)
                sys.exit(1)
            report_id = body.get("reportId")
            if not report_id:
                print(f"❌ No reportId in create response: {body}", file=sys.stderr)
                sys.exit(1)
            print(f"✓ Report request created: {report_id}", file=sys.stderr)

    # Step 3: 轮询
    print(f"⏳ Polling for report completion (every {poll_interval}s, max {max_attempts} attempts)...", file=sys.stderr)
    download_url = None
    last_status = None
    # ~5 分钟的提示节点；用 pollInterval 反推，避免用户改 pollInterval 后不准
    progress_nudge_at = max(1, 300 // max(int(poll_interval), 1))
    for attempt in range(1, max_attempts + 1):
        status_result = get_report_status(region, access_token, profile_id, report_id)
        if "error" in status_result:
            print(f"❌ Failed to check status: {status_result}", file=sys.stderr)
            sys.exit(1)
        hs = status_result.get("httpStatus")
        if hs is None or hs // 100 != 2:
            print(f"❌ Report status HTTP {hs}: {status_result.get('body')}", file=sys.stderr)
            sys.exit(1)
        try:
            status_body = json.loads(status_result.get("body", "{}"))
        except Exception as e:
            print(f"❌ Failed to parse status body: {e}", file=sys.stderr)
            sys.exit(1)
        status = (status_body.get("status") or "").upper()
        last_status = status
        print(f"[{attempt}/{max_attempts}] Status: {status}", file=sys.stderr)
        if status == "COMPLETED" or status == "SUCCESS":
            download_url = status_body.get("url")
            if not download_url:
                print(f"❌ No url in completed response: {status_body}", file=sys.stderr)
                sys.exit(1)
            print(f"✓ Report completed", file=sys.stderr)
            break
        elif status in ("FAILURE", "FAILED", "CANCELLED"):
            failure_reason = status_body.get("failureReason")
            failure_result = {
                "success": False,
                "error": f"Report generation failed with status={status}",
                "reportId": report_id,
                "status": status,
                "failureReason": failure_reason,
                "pollAttempts": attempt,
            }
            print(json.dumps(failure_result, indent=2, ensure_ascii=False))
            print(f"❌ Report generation failed: {failure_reason or status}", file=sys.stderr)
            sys.exit(1)
        elif status in ("PENDING", "PROCESSING", "IN_QUEUE", "IN_PROGRESS"):
            # 5 分钟左右给用户一个耐心提示（仅打一次，避免刷屏）
            if attempt == progress_nudge_at and attempt < max_attempts:
                print(
                    f"⏱️  已等 ~{attempt * int(poll_interval)}s，报告仍在 Amazon 侧生成。"
                    f"报告生成通常 2–10 分钟，耐心等待中…",
                    file=sys.stderr,
                )
            if attempt < max_attempts:
                time.sleep(poll_interval)
            # 最后一次迭代仍是 PROCESSING → 自然跳出循环，走下方结构化超时处理
        else:
            print(f"❌ Unknown status: {status}", file=sys.stderr)
            sys.exit(1)

    # 轮询窗口用尽但报告仍在生成：结构化退出，让 agent 询问用户是否继续等待
    if download_url is None:
        elapsed = max_attempts * int(poll_interval)
        timeout_result = {
            "success": False,
            "status": "STILL_PROCESSING",
            "reportId": report_id,
            "reportTypeId": report_type_id,
            "profileId": profile_id,
            "lastStatus": last_status,
            "pollAttempts": max_attempts,
            "elapsedSeconds": elapsed,
            "message": (
                f"客户端已等 ~{elapsed} 秒（{max_attempts} 次轮询）报告仍在 Amazon 侧生成，"
                f"并未失败。用 reportId 切换到仅轮询模式即可继续等待。"
            ),
            "resumeHint": {
                "mode": "poll-only",
                "note": "传入 reportId + 更大的 maxAttempts 继续轮询同一份报告",
                "params": {
                    "profileId": profile_id,
                    "region": region,
                    "reportId": report_id,
                    "maxAttempts": 60,
                    "pollInterval": int(poll_interval),
                },
            },
        }
        print(json.dumps(timeout_result, indent=2, ensure_ascii=False))
        print(
            f"⏳ 客户端轮询 {max_attempts} 次（~{elapsed}s）仍未完成，报告本身未坏。"
            f"stdout 已输出 reportId 与续跑参数。Agent 应询问用户是否继续等待"
            f"（如 maxAttempts=60 约 30 分钟 / maxAttempts=120 约 1 小时），或稍后用 reportId 回来。",
            file=sys.stderr,
        )
        sys.exit(2)

    # Step 4: 下载 + 解压
    temp_dir = tempfile.mkdtemp(prefix="amazon_ads_report_")
    print(f"📁 Temporary directory: {temp_dir}", file=sys.stderr)
    download_path = os.path.join(temp_dir, "report_download")
    if not download_report(download_url, download_path):
        sys.exit(1)
    final_path = extract_if_compressed(download_path, temp_dir)
    resolved_file = Path(final_path).resolve()
    resolved_path = str(resolved_file)
    file_name = resolved_file.name
    local_file_uri = resolved_file.as_uri()
    file_size = os.path.getsize(final_path)

    print(f"\n✅ Report downloaded successfully!", file=sys.stderr)
    print(f"📊 Report Type: {report_type_id}", file=sys.stderr)
    print(f"\n📂 文件保存位置（本地，已解压）:", file=sys.stderr)
    print(f"    完整路径: {resolved_path}", file=sys.stderr)
    print(f"    文件名:   {file_name}", file=sys.stderr)
    print(f"📦 Size: {file_size:,} bytes", file=sys.stderr)
    print(f"\n🖥️  本机 file URI: {local_file_uri}", file=sys.stderr)

    # Step 5: 本机 HTTP 暴露
    serve_http = params.get("serveExtractedFileHttp", True)
    serve_host = str(params.get("serveHost") or "127.0.0.1")
    serve_port = int(params.get("servePort") or 0)
    serve_seconds = int(params.get("serveSeconds", 300))
    if serve_http:
        serve_seconds = max(10, serve_seconds)

    http_server = None
    http_thread = None
    extracted_http_url = None
    if serve_http:
        try:
            http_server, http_thread, extracted_http_url = _start_local_extracted_http_server(
                Path(final_path), serve_host, serve_port
            )
        except OSError as e:
            print(f"⚠️  Could not start local HTTP server: {e}", file=sys.stderr)

    if extracted_http_url:
        print(f"\n🌐 已解压文件 · 本机 HTTP 下载链接（{serve_seconds}s 内用浏览器打开即可保存）:", file=sys.stderr)
        print(f"    {extracted_http_url}", file=sys.stderr)
        print("    （仅本机可访问；脚本在计时结束后会关闭服务，链接即失效。）", file=sys.stderr)

    # Step 6: 预览前 5 行
    try:
        with open(final_path, 'r', encoding='utf-8') as f:
            preview = f.read(2048)
        if preview:
            print(f"\n📋 Preview (first 2KB):", file=sys.stderr)
            for line in preview.splitlines()[:5]:
                print(f"  {line[:200]}", file=sys.stderr)
    except Exception as e:
        print(f"⚠️  Could not preview file: {e}", file=sys.stderr)

    include_amazon = bool(params.get("includeAmazonSourceUrl"))
    result = {
        "success": True,
        "reportId": report_id,
        "reportTypeId": report_type_id,
        "profileId": profile_id,
        "downloadPath": resolved_path,
        "fileName": file_name,
        "localFileUri": local_file_uri,
        "tempDirectory": temp_dir,
        "fileSize": file_size,
    }
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
            "Amazon 预签名源地址（通常为 GZIP_JSON 压缩包），与 extractedFileHttpUrl 不同，"
            "一般无需提供给终端用户。"
        )
    emit_result(result, lf_inline_flag())

    if http_server is not None:
        try:
            print(f"\n⏳ 本地 HTTP 服务保持 {serve_seconds}s …", file=sys.stderr)
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

SLUG = "linkfox-amazon-ads-report"


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
