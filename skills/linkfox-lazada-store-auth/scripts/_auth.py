"""Validate and interpret Lazada connection operations."""
from urllib.parse import parse_qsl, urlsplit

from call_api import SECRET_KEYS, normalized, run

SLUG = "linkfox-lazada-store-auth"

STATUSES = ("PENDING", "AUTHORIZED", "DENIED", "FAILED", "EXPIRED")
FIELDS = {
    "authorizeUrl": (set(), {"shopName"}),
    "authorizationStatus": ({"requestId"}, set()),
    "authorizedStores": (set(), set()),
    "disconnect": ({"connectionId"}, set()),
}
FORBIDDEN_QUERY_KEYS = SECRET_KEYS | {"code"}


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def validate(params, operation):
    required, optional = FIELDS[operation]
    if not required <= params.keys() or params.keys() - required - optional:
        raise ValueError("授权操作的参数字段不正确，见 references/api.md")
    if any(not nonempty(value) for value in params.values()):
        raise ValueError("授权参数必须是非空字符串")
    return params


def authorization_url(result):
    value = result.get("authorizeUrl")
    if not nonempty(value) or any(ch.isspace() or not ch.isprintable() for ch in value):
        return None
    try:
        url = urlsplit(value)
        if (
            url.scheme != "https"
            or url.netloc.lower() not in {"auth.lazada.com", "auth.lazada.com:443"}
            or url.path != "/oauth/authorize"
            or url.fragment
        ):
            return None
        pairs = parse_qsl(url.query.replace(";", "&"), keep_blank_values=True)
        if any(normalized(name) in FORBIDDEN_QUERY_KEYS for name, _ in pairs):
            return None
        return value
    except ValueError:
        return None


def interpret(payload, operation):
    result = payload.get("data", payload)
    if not isinstance(result, dict):
        return False, {"error": "INVALID_AUTH_RESPONSE"}
    if operation == "authorizeUrl":
        success = nonempty(result.get("requestId")) and result.get("status") == "PENDING"
        if success and authorization_url(result):
            return True, {name: result[name] for name in ("requestId", "status", "authorizeUrl")}
    elif operation == "authorizationStatus":
        if nonempty(result.get("requestId")) and result.get("status") in STATUSES:
            return True, {name: result[name] for name in ("requestId", "status")}
    elif operation == "authorizedStores":
        stores = result.get("stores")
        if isinstance(stores, list) and all(
            isinstance(store, dict) and nonempty(store.get("connectionId")) for store in stores
        ):
            fields = ("connectionId", "region", "sellerId", "shopName", "status")
            return True, {"total": result.get("total", len(stores)),
                          "stores": [{field: store[field] for field in fields if field in store}
                                     for store in stores]}
    elif operation == "disconnect":
        if nonempty(result.get("connectionId")) and type(result.get("disconnected")) is bool:
            return result["disconnected"], {name: result[name] for name in ("connectionId", "disconnected")}
    return False, {"error": "INVALID_AUTH_RESPONSE"}


def main(api_path, operation, output_slug, argv=None):
    return run(api_path, f"{SLUG}-{output_slug}", argv=argv, prepare=lambda params: validate(params, operation),
               interpret=lambda payload: interpret(payload, operation),
               transient=authorization_url if operation == "authorizeUrl" else None)
