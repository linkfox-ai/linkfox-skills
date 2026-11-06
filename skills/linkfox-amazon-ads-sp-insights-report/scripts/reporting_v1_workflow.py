#!/usr/bin/env python3
"""SP 洞察报告的账号映射、创建、轮询、CSV 下载及数据处理。

入口负责业务缓存及落盘，经公共调用器执行 LinkFox 请求；本模块仅直接下载
Amazon 返回的非 LinkFox CSV 素材。
"""

import gzip
import csv
import json
import os
import shutil
import sys
import time
from datetime import date, datetime
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


QUERY_ACCOUNTS_PATH = "adsApi/v1/query/advertiserAccounts"
CREATE_REPORTS_PATH = "adsApi/v1/create/reports"
RETRIEVE_REPORTS_PATH = "adsApi/v1/retrieve/reports"
VALID_REGIONS = {"NA", "EU", "FE"}
COMMON_PARAMS = {
    "profileId", "region", "startDate", "endDate", "timeUnit",
    "advertiserAccountId", "pollInterval", "maxAttempts", "reportId",
}
SENSITIVE_KEYS = {
    "accesstoken", "amzaccesstoken", "refreshtoken", "clientsecret",
    "lwaclientsecret", "clientid", "lwaclientid", "authorization",
    "amazonadvertisingapiclientid",
}
RUNNING_STATUSES = {"PENDING", "PROCESSING", "IN_QUEUE", "IN_PROGRESS"}
SUCCESS_STATUSES = {"COMPLETED", "SUCCESS"}
FAILED_STATUSES = {"FAILED", "FAILURE", "CANCELLED", "CANCELED"}


class WorkflowError(Exception):
    def __init__(self, message, details=None):
        super().__init__(message)
        self.message = message
        self.details = details


def _redact_presigned_urls(node):
    if isinstance(node, dict):
        redacted = {}
        for key, value in node.items():
            is_download_url = (
                _normalized_key(key) in {"url", "downloadurl", "location"}
                and isinstance(value, str)
                and value.lower().startswith(("http://", "https://"))
            )
            if is_download_url:
                redacted[key] = "[redacted]"
            else:
                redacted[key] = _redact_presigned_urls(value)
        return redacted
    if isinstance(node, list):
        return [_redact_presigned_urls(value) for value in node]
    if isinstance(node, str) and node.lower().startswith(("http://", "https://")):
        return "[redacted]"
    return node


def _fail(error_message, details=None, **extra):
    result = {"success": False, "error": error_message, "_cacheable": False}
    if details is not None:
        result["details"] = _redact_presigned_urls(details)
    result.update(extra)
    return result


def _required_string(params, key):
    value = params.get(key)
    if not isinstance(value, str) or not value.strip():
        raise WorkflowError("Missing or invalid parameter: %s" % key)
    return value.strip()


def _normalized_key(value):
    return "".join(ch for ch in str(value).lower() if ch.isalnum())


def _reject_sensitive_values(node, path="params"):
    if isinstance(node, dict):
        for key, value in node.items():
            if _normalized_key(key) in SENSITIVE_KEYS:
                raise WorkflowError(
                    "Amazon credentials must not be passed in skill parameters",
                    {"field": "%s.%s" % (path, key)},
                )
            _reject_sensitive_values(value, "%s.%s" % (path, key))
    elif isinstance(node, list):
        for index, value in enumerate(node):
            _reject_sensitive_values(value, "%s[%s]" % (path, index))


def _reject_unknown_params(params, kind):
    if not isinstance(params, dict):
        return
    allowed = set(COMMON_PARAMS)
    if kind == "audience":
        allowed.add("detailLevel")
    unknown = sorted(str(key) for key in params if key not in allowed)
    if unknown:
        if kind == "search-impression-share":
            hint = "Search impression share/rank cannot be combined with campaign, ad group, target, keyword, custom fields, dimensions, or groupBy."
        else:
            hint = "Only the parameters documented in the selected Reporting v1 reference are supported."
        raise WorkflowError(
            "Unsupported parameter(s): %s" % ", ".join(unknown),
            {"unsupported": unknown, "hint": hint},
        )


def _positive_int(params, key, default, minimum, maximum):
    value = params.get(key, default)
    if isinstance(value, bool) or not isinstance(value, (int, str)):
        raise WorkflowError("%s must be an integer" % key)
    try:
        value = int(value)
    except (TypeError, ValueError):
        raise WorkflowError("%s must be an integer" % key)
    if value < minimum or value > maximum:
        raise WorkflowError("%s must be between %s and %s" % (key, minimum, maximum))
    return value


def _parse_date(value, key):
    try:
        parsed = datetime.strptime(value, "%Y-%m-%d").date()
        if parsed.isoformat() != value:
            raise ValueError("日期必须补齐年月日位数")
        return parsed
    except (TypeError, ValueError):
        raise WorkflowError("%s must use YYYY-MM-DD" % key)


def _validate_base_params(params, poll_only):
    if not isinstance(params, dict):
        raise WorkflowError("Parameters must be a JSON object")
    profile_id = params.get("profileId")
    if isinstance(profile_id, bool) or not isinstance(profile_id, (int, str)):
        raise WorkflowError("Missing or invalid parameter: profileId")
    profile_id = str(profile_id).strip()
    if (not profile_id.isascii() or not profile_id.isdecimal()
            or len(profile_id.lstrip('0')) > 19
            or not 0 < int(profile_id.lstrip('0') or '0') <= 9223372036854775807):
        raise WorkflowError("profileId 必须为Long范围内的正整数或数字字符串")
    profile_id = profile_id.lstrip('0') or '0'
    region = _required_string(params, "region").upper()
    if region not in VALID_REGIONS:
        raise WorkflowError("region must be one of NA, EU, FE")
    if poll_only:
        return profile_id, region, None, None, None

    start_text = _required_string(params, "startDate")
    end_text = _required_string(params, "endDate")
    start_date = _parse_date(start_text, "startDate")
    end_date = _parse_date(end_text, "endDate")
    if start_date > end_date:
        raise WorkflowError("startDate must not be after endDate")
    if end_date > date.today():
        raise WorkflowError("endDate must not be in the future")
    if end_date >= date.today():
        print(
            "Warning: endDate is today; Amazon reporting data may still be incomplete. "
            "Yesterday or earlier is recommended.",
            file=sys.stderr,
        )
    return profile_id, region, start_text, end_text, (end_date - start_date).days + 1


def _proxy_payload(profile_id, region, path, request_body):
    return {
        "region": region,
        "path": path,
        "method": "POST",
        "profileId": int(profile_id),
        "body": json.dumps(request_body, ensure_ascii=False, separators=(",", ":")),
        "contentType": "application/json",
    }


def _decode_proxy_response(raw, path):
    if not isinstance(raw, dict):
        raise WorkflowError("LinkFox gateway returned a non-object response", raw)
    if raw.get("error") and "httpStatus" not in raw:
        raise WorkflowError("LinkFox gateway request failed", raw)
    status = raw.get("httpStatus")
    try:
        status = int(status)
    except (TypeError, ValueError):
        raise WorkflowError("LinkFox gateway response is missing httpStatus", raw)
    body = raw.get("body")
    if isinstance(body, str):
        try:
            body = json.loads(body) if body else {}
        except json.JSONDecodeError:
            body = {"raw": body}
    elif body is None:
        body = {}
    if status < 200 or status >= 300:
        raise WorkflowError(
            "Amazon Ads API request failed",
            {"path": path, "httpStatus": status, "body": body},
        )
    if not isinstance(body, dict):
        raise WorkflowError("Amazon Ads API returned an unexpected response body", body)
    return body


def _call_proxy(call_api, profile_id, region, path, request_body):
    raw = call_api(_proxy_payload(profile_id, region, path, request_body))
    return _decode_proxy_response(raw, path)


def _find_next_token(body):
    for key in ("nextToken", "nextPageToken"):
        value = body.get(key)
        if isinstance(value, str) and value:
            return value
    pagination = body.get("pagination")
    if isinstance(pagination, dict):
        for key in ("nextToken", "nextPageToken"):
            value = pagination.get(key)
            if isinstance(value, str) and value:
                return value
    return None


def _collect_account_objects(node, output):
    if isinstance(node, list):
        for item in node:
            _collect_account_objects(item, output)
    elif isinstance(node, dict):
        alternate = node.get("alternateIds") or node.get("alternateIdentifiers")
        account_id = node.get("advertiserAccountId") or node.get("id")
        if account_id is not None and isinstance(alternate, list):
            output.append(node)
        for value in node.values():
            if isinstance(value, (dict, list)):
                _collect_account_objects(value, output)


def _alternate_matches(alternate_ids, profile_id):
    target = str(profile_id)
    for alternate in alternate_ids or []:
        if isinstance(alternate, dict):
            for key in ("value", "id", "alternateId", "profileId"):
                if str(alternate.get(key, "")) == target:
                    return True
        elif str(alternate) == target:
            return True
    return False


def _query_account_pages(call_api, profile_id, region, base_request):
    accounts = []
    seen_tokens = set()
    request_body = dict(base_request)
    while True:
        body = _call_proxy(call_api, profile_id, region, QUERY_ACCOUNTS_PATH, request_body)
        _collect_account_objects(body, accounts)
        token = _find_next_token(body)
        if not token or token in seen_tokens:
            break
        seen_tokens.add(token)
        request_body = dict(base_request)
        request_body["nextToken"] = token
    return accounts


def _resolve_advertiser_account(call_api, profile_id, region, explicit_id=None):
    if explicit_id is not None:
        explicit_id = str(explicit_id).strip()
        if not explicit_id:
            raise WorkflowError("advertiserAccountId must not be empty")
        return explicit_id

    accounts = []
    accounts.extend(_query_account_pages(call_api, profile_id, region, {}))
    accounts.extend(
        _query_account_pages(
            call_api,
            profile_id,
            region,
            {"isGlobalAccountFilter": {"include": [False]}},
        )
    )
    matches = []
    for account in accounts:
        alternate = account.get("alternateIds") or account.get("alternateIdentifiers") or []
        if _alternate_matches(alternate, profile_id):
            account_id = account.get("advertiserAccountId") or account.get("id")
            if account_id is not None:
                matches.append(str(account_id))
    unique = list(dict.fromkeys(matches))
    if not unique:
        raise WorkflowError(
            "Could not map profileId to an Ads v1 advertiserAccountId",
            {
                "profileId": profile_id,
                "hint": "Confirm the authorized profile can access Reporting API v1, or pass advertiserAccountId returned by query/advertiserAccounts.",
            },
        )
    if len(unique) > 1:
        raise WorkflowError(
            "profileId maps to multiple advertiser accounts",
            {"profileId": profile_id, "advertiserAccountIds": unique},
        )
    return unique[0]


def _time_fields(time_unit):
    if time_unit == "DAILY":
        return ["date.value"]
    if time_unit == "SUMMARY":
        return ["dateRange.value"]
    raise WorkflowError("timeUnit must be DAILY or SUMMARY")


def _audience_fields(params, time_unit):
    fields = _time_fields(time_unit) + [
        "advertiserAccount.id",
        "adProduct.value",
        "audienceSegment.id",
        "audienceSegment.name",
        "audienceSegment.type",
        "audienceSegment.classCode",
        "audienceSegment.source",
        "audienceSegmentCountry.code",
        "budgetCurrency.value",
        "metric.impressions",
        "metric.clicks",
        "metric.totalCost",
        "metric.purchases",
        "metric.sales",
        "metric.roas",
    ]
    detail_level = str(params.get("detailLevel", "ACCOUNT")).upper()
    if detail_level == "CAMPAIGN":
        fields[2:2] = ["campaign.id", "campaign.name"]
    elif detail_level == "AD_GROUP":
        fields[2:2] = ["campaign.id", "campaign.name", "adGroup.id", "adGroup.name"]
    elif detail_level != "ACCOUNT":
        raise WorkflowError("detailLevel must be ACCOUNT, CAMPAIGN, or AD_GROUP")
    return fields


def _search_share_fields(time_unit):
    return _time_fields(time_unit) + [
        "advertiserAccount.id",
        "adProduct.value",
        "searchTerm.value",
        "metric.impressionShare",
        "metric.impressionShareRank",
    ]


def _build_create_body(kind, advertiser_account_id, start_date, end_date, params):
    time_unit = str(params.get("timeUnit", "DAILY")).upper()
    if kind == "audience":
        fields = _audience_fields(params, time_unit)
    elif kind == "search-impression-share":
        fields = _search_share_fields(time_unit)
    else:
        raise WorkflowError("Unsupported report workflow: %s" % kind)
    return {
        "accessRequestedAccounts": [
            {"advertiserAccountId": advertiser_account_id}
        ],
        "reports": [
            {
                "format": "CSV",
                "periods": [
                    {"datePeriod": {"startDate": start_date, "endDate": end_date}}
                ],
                "query": {
                    "fields": fields,
                    "filter": {
                        "on": {
                            "field": "adProduct.value",
                            "comparisonOperator": "EQUALS",
                            "not": False,
                            "values": ["SPONSORED_PRODUCTS"],
                        }
                    },
                },
            }
        ],
    }, fields


def _find_report(body, report_id=None):
    candidates = []

    def walk(node):
        if isinstance(node, list):
            for item in node:
                walk(item)
        elif isinstance(node, dict):
            if any(key in node for key in ("reportId", "status", "completedReportParts")):
                candidates.append(node)
            for value in node.values():
                if isinstance(value, (dict, list)):
                    walk(value)

    walk(body.get("success", body))
    if report_id:
        for candidate in candidates:
            if str(candidate.get("reportId", "")) == str(report_id):
                return candidate
        return None
    for candidate in candidates:
        if candidate.get("reportId"):
            return candidate
    return None


def _create_report(call_api, profile_id, region, create_body):
    body = _call_proxy(call_api, profile_id, region, CREATE_REPORTS_PATH, create_body)
    report = _find_report(body)
    if not report or not report.get("reportId"):
        raise WorkflowError("Create report response did not include reportId", body)
    return str(report["reportId"]), report


def _retrieve_report(call_api, profile_id, region, report_id):
    body = _call_proxy(
        call_api,
        profile_id,
        region,
        RETRIEVE_REPORTS_PATH,
        {"reportIds": [report_id]},
    )
    report = _find_report(body, report_id)
    if not report:
        raise WorkflowError("Retrieve report response did not include the requested report", body)
    return report


def _part_url(part):
    if isinstance(part, str):
        return part
    if not isinstance(part, dict):
        return None
    for key in ("url", "downloadUrl", "location"):
        value = part.get(key)
        if isinstance(value, str) and value:
            return value
    return None


def _download_part_to_file(url, path):
    request = Request(url, headers={"User-Agent": "LinkFox-Skill/2.0"})
    try:
        with urlopen(request, timeout=150) as response, open(path, "wb") as output:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                output.write(chunk)
    except HTTPError as exc:
        raise WorkflowError(
            "Failed to download a completed report part",
            {"httpStatus": exc.code, "reason": str(exc.reason)},
        )
    except URLError as exc:
        raise WorkflowError("Failed to download a completed report part", str(exc.reason))
    except OSError as exc:
        raise WorkflowError("Failed to store a completed report part", str(exc))


def _materialize_csv(raw_path, output_path):
    try:
        with open(raw_path, "rb") as source:
            is_gzip = source.read(2) == b"\x1f\x8b"
        if not is_gzip:
            os.replace(raw_path, output_path)
            return
        with gzip.open(raw_path, "rb") as source, open(output_path, "wb") as output:
            shutil.copyfileobj(source, output, length=1024 * 1024)
        os.remove(raw_path)
    except (OSError, EOFError) as exc:
        for path in (raw_path, output_path):
            try:
                if os.path.exists(path):
                    os.remove(path)
            except OSError:
                pass
        raise WorkflowError("Amazon report part is invalid gzip/CSV data", str(exc))


def _preview_csv(path):
    preview = []
    row_count = 0
    try:
        with open(path, encoding="utf-8-sig", newline="") as source:
            for row in csv.DictReader(source):
                row_count += 1
                if len(preview) < 10:
                    preview.append(row)
    except UnicodeDecodeError as exc:
        raise WorkflowError("Amazon report part is not UTF-8 CSV", str(exc))
    except (csv.Error, OSError) as exc:
        raise WorkflowError("Failed to parse Amazon report CSV", str(exc))
    return preview, row_count


def _remove_if_present(path):
    try:
        if os.path.exists(path):
            os.remove(path)
    except OSError:
        pass


def _download_completed_parts(report, resolve_data_path, skill_slug):
    parts = report.get("completedReportParts") or report.get("reportParts") or []
    if not isinstance(parts, list):
        raise WorkflowError("Completed report returned invalid completedReportParts", report)
    report_format = str(report.get("format", "CSV")).upper()
    if report_format != "CSV":
        raise WorkflowError("Completed report returned an unexpected format", report_format)
    if not parts:
        return [], 0, []
    files = []
    preview = []
    total_rows = 0
    try:
        for index, part in enumerate(parts, 1):
            url = _part_url(part)
            if not url:
                raise WorkflowError("A completed report part did not include a download URL", part)
            out_path = resolve_data_path(skill_slug + "-part-%02d" % index, time.time(), "csv")
            raw_path = out_path + ".download"
            _download_part_to_file(url, raw_path)
            _materialize_csv(raw_path, out_path)
            rows, row_count = _preview_csv(out_path)
            files.append({"part": index, "path": os.path.abspath(out_path), "rowCount": row_count})
            total_rows += row_count
            if len(preview) < 10:
                preview.extend(rows[: 10 - len(preview)])
    except Exception:
        if "raw_path" in locals():
            _remove_if_present(raw_path)
        if "out_path" in locals():
            _remove_if_present(out_path)
        for completed in files:
            _remove_if_present(completed["path"])
        raise
    return files, total_rows, preview


def run_report_workflow(params, call_api, resolve_data_path, kind, skill_slug):
    """Run account mapping, report creation, polling, and part download."""
    report_id = None
    try:
        _reject_sensitive_values(params)
        _reject_unknown_params(params, kind)
        poll_only = isinstance(params, dict) and "reportId" in params
        if poll_only:
            report_id = _required_string(params, "reportId")
        profile_id, region, start_date, end_date, span_days = _validate_base_params(params, poll_only)
        poll_interval = _positive_int(params, "pollInterval", 60, 5, 300)
        max_attempts = _positive_int(params, "maxAttempts", 10, 1, 120)
        fields = None
        advertiser_account_id = None
        created_report = None

        if not poll_only:
            # 固定字段和枚举在账号查询前校验，避免非法组合先发出网关请求。
            _build_create_body(kind, "validation-only", start_date, end_date, params)
            advertiser_account_id = _resolve_advertiser_account(
                call_api,
                profile_id,
                region,
                params.get("advertiserAccountId"),
            )
            create_body, fields = _build_create_body(
                kind,
                advertiser_account_id,
                start_date,
                end_date,
                params,
            )
            report_id, created_report = _create_report(
                call_api, profile_id, region, create_body
            )

        started = time.time()
        last_status = ""
        report = created_report or {}
        progress_nudge_at = max(
            2,
            ((5 * 60 + poll_interval - 1) // poll_interval) + 1,
        )
        progress_nudge_sent = False
        print(
            "Polling Amazon Ads report every %ss (max %s attempts). "
            "Report generation usually takes about 2-10 minutes and can occasionally take longer."
            % (poll_interval, max_attempts),
            file=sys.stderr,
        )
        for attempt in range(1, max_attempts + 1):
            report = _retrieve_report(call_api, profile_id, region, report_id)
            last_status = str(report.get("status", "")).upper()
            print(
                "Amazon Ads report %s: %s (%s/%s)"
                % (report_id, last_status or "UNKNOWN", attempt, max_attempts),
                file=sys.stderr,
            )
            if last_status in SUCCESS_STATUSES:
                files, total_rows, preview = _download_completed_parts(
                    report, resolve_data_path, skill_slug
                )
                result = {
                    "success": True,
                    "status": last_status,
                    "reportId": report_id,
                    "reportKind": kind,
                    "profileId": int(profile_id),
                    "pollAttempts": attempt,
                    "elapsedSeconds": round(time.time() - started, 3),
                    "totalRows": total_rows,
                    "dataFiles": files,
                    "preview": preview,
                    "_cacheable": True,
                }
                if advertiser_account_id:
                    result["advertiserAccountId"] = advertiser_account_id
                if fields:
                    result["fields"] = fields
                if start_date:
                    result["startDate"] = start_date
                    result["endDate"] = end_date
                    result["dateSpanDays"] = span_days
                return result
            if last_status in FAILED_STATUSES:
                return _fail(
                    "Amazon Ads report generation failed",
                    report,
                    reportId=report_id,
                    status=last_status,
                    pollAttempts=attempt,
                )
            if last_status and last_status not in RUNNING_STATUSES:
                return _fail(
                    "Amazon Ads report returned an unknown status",
                    report,
                    reportId=report_id,
                    status=last_status,
                    pollAttempts=attempt,
                )
            if (
                not progress_nudge_sent
                and attempt >= progress_nudge_at
                and attempt < max_attempts
            ):
                progress_nudge_sent = True
                elapsed = round(time.time() - started)
                print(
                    "Amazon Ads report is still being generated after about %ss. "
                    "This is normal for asynchronous reports; continuing to wait without creating a duplicate report."
                    % elapsed,
                    file=sys.stderr,
                )
            if attempt < max_attempts:
                time.sleep(poll_interval)

        elapsed = round(time.time() - started, 3)
        print(
            "The client polling window ended after about %ss, but the Amazon Ads report has not failed. "
            "Use the returned reportId and resume parameters to continue polling the same report."
            % elapsed,
            file=sys.stderr,
        )
        return _fail(
            "Amazon Ads report is still processing",
            report,
            status="STILL_PROCESSING",
            lastStatus=last_status,
            reportId=report_id,
            pollAttempts=max_attempts,
            elapsedSeconds=elapsed,
            message=(
                "The client polling window ended while Amazon was still generating the report. "
                "The report has not failed; continue with the same reportId instead of creating a duplicate report."
            ),
            resumeHint={
                "mode": "poll-only",
                "note": "Continue polling the same reportId with a larger maxAttempts value.",
                "params": {
                    "profileId": int(profile_id),
                    "region": region,
                    "reportId": report_id,
                    "pollInterval": poll_interval,
                    "maxAttempts": min(max_attempts * 2, 120),
                }
            },
        )
    except WorkflowError as exc:
        return _fail(exc.message, exc.details, **({"reportId": report_id} if report_id else {}))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return _fail(
            "Failed to process Amazon Ads report", str(exc),
            **({"reportId": report_id} if report_id else {}),
        )
