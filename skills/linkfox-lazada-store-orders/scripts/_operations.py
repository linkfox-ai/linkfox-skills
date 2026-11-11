"""Run the named Lazada operations exposed by this Skill."""
import argparse
from pathlib import Path
import re
import sys
from uuid import UUID

from call_api import run

STATUS_PATH = "/lazada/operationStatus"
WRITE_STATUSES = {"PENDING", "SUCCEEDED", "REJECTED", "PARTIAL", "UNKNOWN"}
PRIVATE_FIELDS = frozenset({
    "address", "addressbilling", "addressshipping", "billingaddress", "shippingaddress",
    "buyer", "buyername", "customer", "customerfirstname", "customerlastname",
    "customername", "consignee", "recipientname", "phonenumber", "mobile", "email",
    "buyeremail", "customeremail", "phone", "phone2", "taxid", "bankaccount",
    "bankaccountnumber", "accountnumber",
})
KNOWN_ERRORS = {
    "Lazada 授权已失效，请重新授权": "REAUTHORIZATION_REQUIRED",
    "Lazada 店铺授权已失效，请重新授权": "REAUTHORIZATION_REQUIRED",
    "Lazada 代理拒绝访问，请检查出口 IP 白名单": "LAZADA_PROXY_FORBIDDEN",
    "Lazada 店铺写操作尚未启用": "LAZADA_WRITES_DISABLED",
    "requestId 已用于其他 Lazada 操作或不同参数": "LAZADA_REQUEST_ID_CONFLICT",
    "找不到当前店铺的 Lazada 操作记录": "LAZADA_OPERATION_NOT_FOUND",
}
UPSTREAM_ERROR = re.compile(
    r"(?:Lazada 拒绝了查询|Lazada 应用缺少该接口权限|Lazada 请求频率超限，请稍后重试)"
    r"(?:，上游错误码 (?P<upstreamCode>[0-9]{1,9}|[A-Za-z][A-Za-z0-9_.-]{0,47}))?"
    r"(?:，请求编号 (?P<upstreamRequestId>[A-Za-z0-9_.-]{1,64}))?"
)


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def valid_request_id(value):
    if not isinstance(value, str):
        return False
    try:
        return str(UUID(value)) == value.lower()
    except ValueError:
        return False


def prepare(request, operation, write):
    if not nonempty(request.get("connectionId")):
        raise ValueError("请提供已授权店铺的 connectionId")
    status = operation == "operationStatus"
    allowed = {"connectionId", "requestId"} if status else {"connectionId", "params"}
    if write:
        allowed.add("requestId")
    if request.keys() - allowed:
        raise ValueError("输入含该操作不支持的字段，见 references/api.md")
    payload = {"connectionId": request["connectionId"]}
    if write or status:
        request_id = request.get("requestId")
        if not valid_request_id(request_id):
            raise ValueError("requestId 必须为带连字符的 UUID")
        payload["requestId"] = request_id.lower()
    if not status:
        params = request.get("params", {})
        if not isinstance(params, dict):
            raise ValueError("params 必须为 JSON 对象")
        payload.update({"operation": operation, "params": params})
    return payload


def interpret(payload, expected_request_id, status_query, response_check=None):
    data = payload.get("data")
    envelope = payload if "requestId" in payload else data
    if (isinstance(data, dict) and "data" in data and "requestId" in data
            and "clientRequestId" not in payload):
        envelope = data
    if not isinstance(envelope, dict) or "data" not in envelope:
        return False, {"error": "INVALID_PROXY_RESPONSE"}
    request_id = envelope.get("requestId")
    if not isinstance(request_id, str) or not re.fullmatch(r"[A-Za-z0-9_.-]{1,64}", request_id):
        request_id = None
    result = {"data": envelope["data"], "requestId": request_id}
    if expected_request_id is None:
        if (not isinstance(result["data"], (dict, list))
                or response_check is not None and not response_check(result["data"])):
            return False, {"error": "INVALID_PROXY_DATA", "requestId": result["requestId"]}
        return True, result
    status = envelope.get("status")
    if (not isinstance(status, str) or status not in WRITE_STATUSES
            or envelope.get("clientRequestId") != expected_request_id):
        return False, {"error": "INVALID_OPERATION_STATUS", "clientRequestId": expected_request_id}
    result.update({"clientRequestId": expected_request_id, "status": status})
    return status_query or status == "SUCCEEDED", result


def error_diagnostics(message):
    if not isinstance(message, str) or len(message) > 256:
        return {}
    message = message.removeprefix("第三方异常：").removeprefix("参数错误：")
    error = KNOWN_ERRORS.get(message)
    if error:
        return {"error": error}
    match = UPSTREAM_ERROR.fullmatch(message)
    return {name: value for name, value in match.groupdict().items() if value} if match else {}


def main(api_path, slug, operations, argv=None, *, private_operations=frozenset(),
         private_fields=frozenset(), response_checks=None):
    parser = argparse.ArgumentParser()
    choices = list(operations)
    if any(operations.values()):
        choices.append("operationStatus")
    parser.add_argument("operation", choices=choices)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("params", nargs="?", help="JSON object")
    source.add_argument("--params-file", type=Path, help="UTF-8 JSON file")
    parser.add_argument("--inline", action="store_true")
    parser.add_argument("--no-cache", action="store_true")
    args = parser.parse_args(argv)
    try:
        raw = args.params_file.read_text(encoding="utf-8-sig") if args.params_file else args.params
    except (OSError, UnicodeError):
        print("无法读取 UTF-8 JSON 参数文件", file=sys.stderr)
        return 2
    options = [flag for flag, enabled in (("--inline", args.inline), ("--no-cache", args.no_cache)) if enabled]
    operation = args.operation
    status_query = operation == "operationStatus"
    path = STATUS_PATH if status_query else api_path
    expected_request_id = None

    def prepare_request(params):
        nonlocal expected_request_id
        payload = prepare(params, operation, operations.get(operation, False))
        expected_request_id = payload.get("requestId")
        return payload

    return run(path, f"{slug}-{operation}", argv=[raw, *options],
               prepare=prepare_request,
               interpret=lambda payload: interpret(payload, expected_request_id, status_query,
                                                   (response_checks or {}).get(operation)),
               private_fields=PRIVATE_FIELDS | private_fields, error_diagnostics=error_diagnostics,
               private_output=operation in private_operations,
               failure_context=lambda params: ({"clientRequestId": params["requestId"]}
                                               if "requestId" in params else {}))
