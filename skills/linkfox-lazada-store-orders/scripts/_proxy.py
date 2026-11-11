"""Build and validate Lazada read-only requests."""
from datetime import datetime
import re

from call_api import run

API_PATH = "/lazada/developerProxy"
SLUG = "linkfox-lazada-store-orders"

OPERATIONS = {
    "listOrders": ("created_after created_before update_after update_before status sort_by sort_direction offset limit".split(), "created_after update_after".split(), "orders"),
    "getOrder": ("order_id".split(), "order_id".split(), ""),
    "getOrderItems": ("order_id".split(), "order_id".split(), "[]"),
}
PRIVATE_FIELDS = frozenset({
    "address", "addressbilling", "addressshipping", "billingaddress", "shippingaddress",
    "buyer", "buyername", "customer", "customerfirstname", "customerlastname",
    "customername", "consignee", "recipientname", "phonenumber", "mobile", "email",
    "buyeremail", "customeremail", "phone", "phone2", "taxid",
})
KNOWN_ERRORS = {
    "Lazada 授权已失效，请重新授权": "REAUTHORIZATION_REQUIRED",
    "Lazada 店铺授权已失效，请重新授权": "REAUTHORIZATION_REQUIRED",
    "Lazada 代理拒绝访问，请检查出口 IP 白名单": "LAZADA_PROXY_FORBIDDEN",
}
UPSTREAM_ERROR = re.compile(
    r"(?:Lazada 拒绝了查询|Lazada 应用缺少该接口权限|Lazada 请求频率超限，请稍后重试)"
    r"(?:，上游错误码 (?P<upstreamCode>[0-9]{1,9}|[A-Za-z][A-Za-z0-9_.-]{0,47}))?"
    r"(?:，请求编号 (?P<upstreamRequestId>[A-Za-z0-9_.-]{1,64}))?"
)


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def pagination_value(value):
    if type(value) is int:
        return value
    if isinstance(value, str) and value.isascii() and value.isdigit() and len(value) <= 10:
        return int(value)
    return -1


def valid_timestamp(value):
    # Normalize for Python 3.9 validation only. The original text is sent to the gateway.
    timestamp = re.sub(r"([+-][0-9]{2})([0-9]{2})$", r"\1:\2", value)
    timestamp = re.sub(r"\.([0-9]{1,9})(?=[+-]|Z$)",
                       lambda match: "." + match.group(1)[:6].ljust(6, "0"), timestamp)
    if timestamp.endswith("Z"):
        timestamp = timestamp[:-1] + "+00:00"
    try:
        return "T" in timestamp and datetime.fromisoformat(timestamp).utcoffset() is not None
    except ValueError:
        return False


def validate(params, operation):
    if not nonempty(params.get("connectionId")) or params.keys() - {"connectionId", "queryParams"}:
        raise ValueError("请提供授权店铺的 connectionId 和 queryParams")
    query = params.get("queryParams", {})
    fields, required, _ = OPERATIONS[operation]
    if not isinstance(query, dict) or query.keys() - set(fields):
        raise ValueError("queryParams 包含当前操作不支持的字段")
    if required and not any(name in query for name in required):
        raise ValueError("请按当前操作的接口说明提供查询标识或时间下界")
    for name, value in query.items():
        if name in {"offset", "limit"}:
            number = pagination_value(value)
            if name == "offset" and not 0 <= number <= 5000:
                raise ValueError("offset 必须在 0 至 5000 之间")
            if name == "limit" and not 1 <= number <= 100:
                raise ValueError("limit 必须在 1 至 100 之间")
        elif not nonempty(value):
            raise ValueError("查询参数须为非空字符串，ID 保持原始字符串格式")
        elif name.endswith("_id") and not re.fullmatch(r"[1-9][0-9]{0,19}", value):
            raise ValueError("商品或订单 ID 必须是 1 至 20 位的正整数文本")
        elif name.endswith(("_after", "_before")) and not valid_timestamp(value):
            raise ValueError("时间参数须包含时区的 ISO 8601 时间")
    return {"connectionId": params["connectionId"], "operation": operation, "queryParams": query}


def interpret(payload, operation):
    data = payload.get("data")
    envelope = data
    if not (isinstance(data, dict) and "data" in data) and "requestId" in payload:
        envelope = payload
    if not isinstance(envelope, dict) or "data" not in envelope:
        return False, {"error": "INVALID_PROXY_RESPONSE"}
    result = envelope["data"]
    shape = OPERATIONS[operation][2]
    if shape == "[]":
        valid = isinstance(result, list) and all(isinstance(item, dict) for item in result)
    elif shape:
        rows = result.get(shape) if isinstance(result, dict) else None
        valid = isinstance(rows, list) and all(isinstance(row, dict) for row in rows)
    else:
        valid = isinstance(result, dict) and bool(result)
    request_id = envelope.get("requestId")
    if not valid:
        return False, {"error": "INVALID_PROXY_DATA", "requestId": request_id}
    return True, {"data": result, "requestId": request_id}


def error_diagnostics(message):
    if not isinstance(message, str) or len(message) > 256:
        return {}
    message = message.removeprefix("第三方异常：")
    error = KNOWN_ERRORS.get(message)
    if error:
        return {"error": error}
    match = UPSTREAM_ERROR.fullmatch(message)
    return {name: value for name, value in match.groupdict().items() if value} if match else {}


def main(operation, output_slug):
    return run(API_PATH, f"{SLUG}-{output_slug}",
               prepare=lambda params: validate(params, operation),
               interpret=lambda payload: interpret(payload, operation),
               private_fields=PRIVATE_FIELDS, error_diagnostics=error_diagnostics)
