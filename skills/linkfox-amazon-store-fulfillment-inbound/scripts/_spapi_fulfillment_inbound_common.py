"""Shared runner for Amazon Fulfillment Inbound SP-API entry scripts."""

from __future__ import annotations

import json
import hashlib
import os
import re
import secrets
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Callable
from urllib.parse import quote

from _spapi_fulfillment_inbound_specs import OPERATION_SPECS
from _spapi_fulfillment_inbound_validators import ValidationError, validate_request_body
from _linkfox_gateway import call_api as _template_call_api


API_BASE_URL = (
    os.environ.get("LINKFOX_TOOL_GATEWAY")
    or os.environ.get("STORE_API_BASE_URL")
    or os.environ.get("SPAPI_BASE_URL")
    or "https://tool-gateway.linkfox.com"
).rstrip("/")
DEVELOPER_PROXY_ENDPOINT = f"{API_BASE_URL}/spApi/developerProxy"

REQUIRED_SKILL = "linkfox-amazon-store-auth"
DEPENDENCY_EXIT_CODE = 42
REGIONS = frozenset({"NA", "EU", "FE"})
FORBIDDEN_TOKEN_FIELDS = frozenset({"accessToken", "amzAccessToken", "refreshToken"})
FORBIDDEN_OVERRIDE_FIELDS = frozenset({"body", "contentType", "method", "path", "queryString"})
FORBIDDEN_TOKEN_FIELDS_CASEFOLD = frozenset(field.casefold() for field in FORBIDDEN_TOKEN_FIELDS)
FORBIDDEN_OVERRIDE_FIELDS_CASEFOLD = frozenset(
    field.casefold() for field in FORBIDDEN_OVERRIDE_FIELDS
)
MAX_REQUEST_BODY_LENGTH = 1_048_576
MAX_PATH_LENGTH = 2048
MAX_QUERY_STRING_LENGTH = 4096
MAX_SELLER_ID_LENGTH = 64

SLUG = "linkfox-amazon-store-fulfillment-inbound"
LF_SMALL_THRESHOLD = 8000
_LF_SESSION_CACHE: dict[str, str] = {}


def ensure_auth_skill_available(caller: str = "Fulfillment Inbound script") -> None:
    checker = Path(__file__).resolve().parent / "check_auth_dependency.py"
    if not checker.exists():
        payload = {
            "missingSkill": REQUIRED_SKILL,
            "reason": f"check_auth_dependency.py not found next to {caller}",
        }
        print(f"DEPENDENCY_MISSING: {json.dumps(payload, ensure_ascii=False)}", file=sys.stderr)
        raise SystemExit(DEPENDENCY_EXIT_CODE)
    try:
        result = subprocess.run(
            [sys.executable, str(checker)],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except Exception as exc:  # pragma: no cover - environment-specific failure
        payload = {"missingSkill": REQUIRED_SKILL, "reason": str(exc)}
        print(f"DEPENDENCY_MISSING: {json.dumps(payload, ensure_ascii=False)}", file=sys.stderr)
        raise SystemExit(DEPENDENCY_EXIT_CODE) from exc
    if result.stderr:
        sys.stderr.write(result.stderr)
        if not result.stderr.endswith("\n"):
            sys.stderr.write("\n")
    if result.returncode != 0:
        raise SystemExit(DEPENDENCY_EXIT_CODE)


def call_api(endpoint: str, params: dict[str, Any]) -> dict[str, Any]:
    if endpoint != DEVELOPER_PROXY_ENDPOINT:
        raise ValueError(f"Unexpected gateway endpoint: {endpoint}")
    try:
        return _template_call_api(params)
    except json.JSONDecodeError as exc:
        return {"error": f"Gateway returned invalid JSON: {exc}"}


def developer_proxy_call(
    region: str,
    path: str,
    method: str,
    seller_id: str,
    *,
    query_string: str | None = None,
    body: str | None = None,
    content_type: str = "application/json",
) -> dict[str, Any]:
    params: dict[str, Any] = {
        "region": region,
        "path": path,
        "method": method,
        "sellerId": seller_id,
    }
    if query_string:
        params["queryString"] = query_string
    if body is not None:
        params["body"] = body
        params["contentType"] = content_type
    return call_api(DEVELOPER_PROXY_ENDPOINT, params)


def _required_text(params: dict[str, Any], name: str) -> str:
    value = params.get(name)
    if value is None or not str(value).strip():
        raise ValidationError(f"Missing required field: {name}")
    return str(value).strip()


def _canonical_enum(value: Any, allowed: tuple[str, ...], field: str) -> str:
    text = str(value).strip()
    if not text:
        raise ValidationError(f"{field} must not be blank")
    if text in allowed:
        return text
    matches = [candidate for candidate in allowed if candidate.casefold() == text.casefold()]
    if len(matches) == 1:
        return matches[0]
    raise ValidationError(f"{field} must be one of: {', '.join(allowed)}")


def _list_value(value: Any, field: str) -> list[Any]:
    if isinstance(value, str):
        values = [item.strip() for item in value.split(",") if item.strip()]
    elif isinstance(value, (list, tuple)):
        values = list(value)
    else:
        raise ValidationError(f"{field} must be an array or comma-separated string")
    if any(item is None or not str(item).strip() for item in values):
        raise ValidationError(f"{field} must not contain blank values")
    return values


def _normalise_query_value(value: Any, spec: dict[str, Any]) -> Any:
    name = spec["name"]
    kind = spec["kind"]
    allowed = spec["enum"]
    if kind == "integer":
        if isinstance(value, bool):
            raise ValidationError(f"{name} must be an integer")
        try:
            converted = int(value)
        except (TypeError, ValueError) as exc:
            raise ValidationError(f"{name} must be an integer") from exc
        if isinstance(value, float) and not value.is_integer():
            raise ValidationError(f"{name} must be an integer")
        if spec["minimum"] is not None and converted < spec["minimum"]:
            raise ValidationError(f"{name} must be at least {spec['minimum']}")
        if spec["maximum"] is not None and converted > spec["maximum"]:
            raise ValidationError(f"{name} must be at most {spec['maximum']}")
        return converted
    if kind == "list":
        values = _list_value(value, name)
        if spec["minItems"] is not None and len(values) < spec["minItems"]:
            raise ValidationError(f"{name} must contain at least {spec['minItems']} item(s)")
        if spec["maxItems"] is not None and len(values) > spec["maxItems"]:
            raise ValidationError(f"{name} must contain at most {spec['maxItems']} item(s)")
        if allowed:
            values = [_canonical_enum(item, allowed, name) for item in values]
        values = [str(item).strip() for item in values]
        for item in values:
            _validate_string_constraints(item, spec, name)
        return values
    if isinstance(value, (dict, list, tuple)):
        raise ValidationError(f"{name} must be a scalar value")
    if allowed:
        return _canonical_enum(value, allowed, name)
    text = str(value).strip()
    if not text and spec["minLength"] != 0:
        raise ValidationError(f"{name} must not be blank")
    _validate_string_constraints(text, spec, name)
    return text


def _validate_string_constraints(value: str, spec: dict[str, Any], field: str) -> None:
    minimum = spec["minLength"]
    maximum = spec["maxLength"]
    if minimum is not None and len(value) < minimum:
        raise ValidationError(f"{field} length must be at least {minimum}")
    if maximum is not None and len(value) > maximum:
        raise ValidationError(f"{field} length must be at most {maximum}")
    pattern = spec["pattern"]
    if pattern and re.fullmatch(pattern, value) is None:
        raise ValidationError(f"{field} must match {pattern}")
    if spec["format"] == "date-time":
        # Amazon expects ISO 8601. Validate the documented shape while still
        # accepting either Z or an explicit UTC offset.
        iso8601 = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(?::\d{2}(?:\.\d+)?)?(?:Z|[+-]\d{2}:\d{2})$"
        if re.fullmatch(iso8601, value) is None:
            raise ValidationError(f"{field} must use ISO 8601 date-time format")


def build_path(spec: dict[str, Any], params: dict[str, Any]) -> str:
    path = spec["path"]
    for name in spec["pathParams"]:
        value = params.get(name)
        supports_confirmation_alias = spec["operationId"] in {"getLabels", "getBillOfLading"}
        alias_value = params.get("shipmentConfirmationId") if supports_confirmation_alias else None
        if value is not None and not str(value).strip():
            value = None
        if alias_value is not None and not str(alias_value).strip():
            alias_value = None
        if value is not None and alias_value is not None and str(value).strip() != str(alias_value).strip():
            raise ValidationError("shipmentId and shipmentConfirmationId must not conflict")
        if value is None and name == "shipmentId" and supports_confirmation_alias:
            value = alias_value
        if value is None or not str(value).strip():
            alias = " (or shipmentConfirmationId)" if name == "shipmentId" and supports_confirmation_alias else ""
            raise ValidationError(f"Missing required field: {name}{alias}")
        text = str(value).strip()
        rule = spec["pathParamRules"].get(name)
        if rule:
            minimum = rule["minLength"]
            maximum = rule["maxLength"]
            if len(text) < minimum or len(text) > maximum:
                raise ValidationError(
                    f"{name} length must be between {minimum} and {maximum}"
                )
            if re.fullmatch(rule["pattern"], text) is None:
                raise ValidationError(f"{name} must match {rule['pattern']}")
        path = path.replace("{" + name + "}", quote(text, safe=""))
    if len(path) > MAX_PATH_LENGTH:
        raise ValidationError(f"resolved path must not exceed {MAX_PATH_LENGTH} characters")
    return path


def build_query_string(spec: dict[str, Any], params: dict[str, Any]) -> str | None:
    parts: list[str] = []
    for query_spec in spec["queryParams"]:
        name = query_spec["name"]
        value = params.get(name)
        if value is None:
            if query_spec["required"]:
                raise ValidationError(f"Missing required field: {name}")
            continue
        value = _normalise_query_value(value, query_spec)
        wire = query_spec["wire"]
        if query_spec["kind"] == "list":
            if query_spec["collection"] == "multi":
                if spec["operationId"] in {"listItemComplianceDetails", "listPrepDetails"} and name == "mskus":
                    encoded_items = (
                        quote(
                            item.replace("%", "%25").replace("+", "%2B").replace(",", "%2C"),
                            safe="",
                        )
                        for item in value
                    )
                    parts.extend(f"{wire}={item}" for item in encoded_items)
                else:
                    parts.extend(f"{wire}={quote(item, safe='')}" for item in value)
            elif query_spec["collection"] == "csv":
                parts.append(f"{wire}={quote(','.join(value), safe='')}")
            else:  # defensive: every list spec must declare its wire shape
                raise RuntimeError(f"Unsupported list collection: {query_spec['collection']}")
        else:
            parts.append(f"{wire}={quote(str(value), safe='')}")
    _validate_conditional_query(spec["operationId"], params)
    query_string = "&".join(parts) or None
    if query_string is not None and len(query_string) > MAX_QUERY_STRING_LENGTH:
        raise ValidationError(
            f"queryString must not exceed {MAX_QUERY_STRING_LENGTH} characters after encoding"
        )
    return query_string


def _validate_conditional_query(operation_id: str, params: dict[str, Any]) -> None:
    if operation_id == "getShipments":
        query_type = str(params.get("queryType", "")).upper()
        if query_type == "SHIPMENT" and not (
            params.get("shipmentStatusList") or params.get("shipmentIdList")
        ):
            raise ValidationError(
                "getShipments with queryType=SHIPMENT requires shipmentStatusList or shipmentIdList"
            )
        if query_type == "DATE_RANGE" and not (
            params.get("lastUpdatedAfter") and params.get("lastUpdatedBefore")
        ):
            raise ValidationError(
                "getShipments with queryType=DATE_RANGE requires lastUpdatedAfter and lastUpdatedBefore"
            )
        if query_type == "NEXT_TOKEN" and not params.get("nextToken"):
            raise ValidationError("getShipments with queryType=NEXT_TOKEN requires nextToken")
        mode_fields = {
            "SHIPMENT": {"lastUpdatedAfter", "lastUpdatedBefore", "nextToken"},
            "DATE_RANGE": {"shipmentStatusList", "shipmentIdList", "nextToken"},
            "NEXT_TOKEN": {
                "shipmentStatusList",
                "shipmentIdList",
                "lastUpdatedAfter",
                "lastUpdatedBefore",
            },
        }
        conflicting = sorted(field for field in mode_fields.get(query_type, set()) if params.get(field) is not None)
        if conflicting:
            raise ValidationError(
                f"getShipments queryType={query_type} must not include: {', '.join(conflicting)}"
            )
    elif operation_id == "getShipmentItems":
        query_type = str(params.get("queryType", "")).upper()
        if query_type == "DATE_RANGE" and not (
            params.get("lastUpdatedAfter") and params.get("lastUpdatedBefore")
        ):
            raise ValidationError(
                "getShipmentItems with queryType=DATE_RANGE requires lastUpdatedAfter and lastUpdatedBefore"
            )
        if query_type == "NEXT_TOKEN" and not params.get("nextToken"):
            raise ValidationError("getShipmentItems with queryType=NEXT_TOKEN requires nextToken")
        conflicting = {
            "DATE_RANGE": {"nextToken"},
            "NEXT_TOKEN": {"lastUpdatedAfter", "lastUpdatedBefore"},
        }.get(query_type, set())
        present = sorted(field for field in conflicting if params.get(field) is not None)
        if present:
            raise ValidationError(
                f"getShipmentItems queryType={query_type} must not include: {', '.join(present)}"
            )


def build_request_body(spec: dict[str, Any], params: dict[str, Any]) -> tuple[dict[str, Any] | None, str | None]:
    body_spec = spec["requestBody"]
    if body_spec is None:
        if "requestBody" in params:
            raise ValidationError(f"{spec['operationId']} does not accept requestBody")
        return None, None

    if "requestBody" in params:
        body_obj = params["requestBody"]
    else:
        reserved = {
            "sellerId",
            "region",
            "skipDepCheck",
            "confirmWrite",
            "shipmentConfirmationId",
            *spec["pathParams"],
            *(query_spec["name"] for query_spec in spec["queryParams"]),
        }
        body_obj = {key: value for key, value in params.items() if key not in reserved}

    if not isinstance(body_obj, dict):
        raise ValidationError("requestBody must be an object")
    if not body_obj and not body_spec["allowEmpty"]:
        raise ValidationError("requestBody must not be empty")
    for key in body_spec["requiredKeys"]:
        if key not in body_obj or body_obj[key] is None:
            raise ValidationError(f"Missing required field: requestBody.{key}")
    validate_request_body(body_spec["validator"], body_obj)
    body_json = json.dumps(body_obj, ensure_ascii=False, separators=(",", ":"))
    if len(body_json) > MAX_REQUEST_BODY_LENGTH:
        raise ValidationError(
            f"requestBody must not exceed {MAX_REQUEST_BODY_LENGTH} characters"
        )
    return body_obj, body_json


def _parse_proxy_body(proxy: dict[str, Any]) -> Any:
    raw = proxy.get("body")
    if raw is None or (isinstance(raw, str) and not raw.strip()):
        return None
    if isinstance(raw, (dict, list, int, float, bool)):
        return raw
    try:
        return json.loads(str(raw))
    except json.JSONDecodeError:
        return raw


def _is_success(proxy: dict[str, Any], statuses: tuple[int, ...], transport_http_status: int | None = 200) -> bool:
    transport_http_status = getattr(proxy, "transport_http_status", transport_http_status)
    if type(transport_http_status) is not int or not 200 <= transport_http_status < 300:
        return False
    errcode = proxy.get("errcode")
    if isinstance(errcode, str):
        errcode = errcode.strip()
        if errcode:
            if len(errcode) != 3 or not errcode.isascii() or not errcode.isdigit():
                return False
            errcode = int(errcode)
    if errcode is not None and errcode != "":
        if type(errcode) not in (int, float) or not 200 <= errcode < 300 or errcode % 1:
            return False
    status = proxy.get("httpStatus")
    if isinstance(status, str):
        status = status.strip()
        if len(status) != 3 or not status.isascii() or not status.isdigit():
            return False
        status = int(status)
    if type(status) not in (int, float) or status not in statuses:
        return False
    return True


def _find_operation_id(value: Any) -> str | None:
    if not isinstance(value, dict):
        return None
    operation_id = value.get("operationId")
    if operation_id is not None and str(operation_id).strip():
        return str(operation_id).strip()
    payload = value.get("payload")
    if isinstance(payload, dict):
        operation_id = payload.get("operationId")
        if operation_id is not None and str(operation_id).strip():
            return str(operation_id).strip()
    return None


def _find_sensitive_keys(value: Any, forbidden: frozenset[str], path: str = "") -> list[str]:
    matches: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            key_text = str(key)
            child_path = f"{path}.{key_text}" if path else key_text
            if key_text.casefold() in forbidden:
                matches.append(child_path)
            matches.extend(_find_sensitive_keys(child, forbidden, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            matches.extend(_find_sensitive_keys(child, forbidden, f"{path}[{index}]"))
    return matches


def execute_operation(
    operation_id: str,
    params: dict[str, Any],
    *,
    proxy_caller: Callable[..., dict[str, Any]] = developer_proxy_call,
) -> dict[str, Any]:
    try:
        spec = OPERATION_SPECS[operation_id]
    except KeyError as exc:
        raise ValidationError(f"Unknown Fulfillment Inbound operation: {operation_id}") from exc
    if not isinstance(params, dict):
        raise ValidationError("CLI JSON must be an object")
    forbidden = sorted(_find_sensitive_keys(params, FORBIDDEN_TOKEN_FIELDS_CASEFOLD))
    if forbidden:
        raise ValidationError(
            "Do not pass access or refresh tokens; use sellerId + region. Forbidden field(s): "
            + ", ".join(forbidden)
        )
    overrides = sorted(
        key for key in params if str(key).casefold() in FORBIDDEN_OVERRIDE_FIELDS_CASEFOLD
    )
    if overrides:
        raise ValidationError(
            "Operation wrappers fix the upstream request; do not pass override field(s): "
            + ", ".join(overrides)
        )
    if spec.get("risk") == "commit" and params.get("confirmWrite") is not True:
        raise ValidationError(
            f"{operation_id} is a committing write; show the user the target and choices, "
            "then pass confirmWrite=true after explicit confirmation"
        )

    seller_id = _required_text(params, "sellerId")
    if len(seller_id) > MAX_SELLER_ID_LENGTH:
        raise ValidationError(f"sellerId must not exceed {MAX_SELLER_ID_LENGTH} characters")
    region = _required_text(params, "region").upper()
    if region not in REGIONS:
        raise ValidationError("region must be one of: NA, EU, FE")

    path = build_path(spec, params)
    query_string = build_query_string(spec, params)
    body_obj, body_json = build_request_body(spec, params)
    proxy = proxy_caller(
        region,
        path,
        spec["method"],
        seller_id,
        query_string=query_string,
        body=body_json,
    )
    result: dict[str, Any] = {
        "operationId": operation_id,
        "method": spec["method"],
        "resolvedPath": path,
        "developerProxy": proxy,
        "transportHttpStatus": getattr(proxy, "transport_http_status", 200),
    }
    if query_string:
        result["queryString"] = query_string
    if body_obj is not None:
        result["requestBody"] = body_obj

    if _is_success(proxy, spec["successStatuses"]):
        parsed = _parse_proxy_body(proxy)
        result[spec["resultKey"]] = parsed
        if spec["execution"] == "async":
            async_operation_id = _find_operation_id(parsed)
            if async_operation_id:
                result["nextAction"] = {
                    "operationId": async_operation_id,
                    "script": "get_inbound_operation_status.py",
                    "params": {
                        "sellerId": seller_id,
                        "region": region,
                        "operationId": async_operation_id,
                    },
                    "automaticPolling": False,
                }
    return result


def load_cli_params(argv: list[str] | None = None) -> dict[str, Any]:
    arguments = list(sys.argv[1:] if argv is None else argv)
    positional = [value for value in arguments if value not in {"--inline", "--no-cache"}]
    if len(positional) != 1:
        raise ValidationError("Usage: <script>.py '<JSON parameters>' [--inline]")
    try:
        params = json.loads(positional[0])
    except json.JSONDecodeError as exc:
        raise ValidationError(f"Invalid JSON: {exc}") from exc
    if not isinstance(params, dict):
        raise ValidationError("CLI JSON must be an object")
    return params


def run_operation(operation_id: str) -> None:
    try:
        params = load_cli_params()
        if not params.get("skipDepCheck"):
            ensure_auth_skill_available(OPERATION_SPECS[operation_id]["script"])
        spec = OPERATION_SPECS[operation_id]
        cache_path = _lf_cache_path(operation_id, params)
        cacheable = spec["risk"] in {"read", "generate"}
        use_cache = "--no-cache" not in sys.argv and cacheable
        output = _lf_load_cache(cache_path) if use_cache else None
        cache_hit = output is not None
        if output is None:
            output = execute_operation(operation_id, params)
            succeeded = _is_success(output.get("developerProxy", {}), spec["successStatuses"], output.get("transportHttpStatus"))
            if succeeded and spec["risk"] in {"write", "commit", "generate"}:
                _lf_clear_cache()
            if succeeded and use_cache:
                _lf_save_cache(cache_path, output)
    except (ValidationError, KeyError) as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1) from exc
    if cache_hit:
        print(f"Cache hit: {cache_path}", file=sys.stderr)
    emit_result(output, inline=lf_inline_flag())


def _lf_root() -> str:
    cached = _LF_SESSION_CACHE.get("root")
    if cached:
        return cached
    root = os.path.join(os.getcwd(), "linkfox")
    os.makedirs(root, exist_ok=True)
    probe = os.path.join(root, ".write_probe")
    with open(probe, "w", encoding="utf-8") as handle:
        handle.write("")
    os.remove(probe)
    absolute = os.path.abspath(root)
    _LF_SESSION_CACHE["root"] = absolute
    return absolute


def _lf_cache_path(operation_id: str, params: dict[str, Any]) -> str:
    normalized = {key: value for key, value in params.items() if key not in {"skipDepCheck"}}
    raw = json.dumps(
        {
            "operationId": operation_id,
            "params": normalized,
            "sessionId": _lf_session_id(time.time()),
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]
    session_key = hashlib.sha256(_lf_session_id(time.time()).encode("utf-8")).hexdigest()[:16]
    directory = os.path.join(_lf_root(), ".cache", SLUG, session_key)
    os.makedirs(directory, exist_ok=True)
    return os.path.join(directory, f"{operation_id}-{digest}.json")


def _lf_clear_cache() -> None:
    session_key = hashlib.sha256(_lf_session_id(time.time()).encode("utf-8")).hexdigest()[:16]
    directory = os.path.join(_lf_root(), ".cache", SLUG, session_key)
    if not os.path.isdir(directory):
        return
    for entry in os.scandir(directory):
        if entry.is_file() and entry.name.endswith(".json"):
            try:
                os.unlink(entry.path)
            except OSError:
                pass


def _lf_load_cache(path: str) -> Any | None:
    if not os.path.isfile(path) or time.time() - os.path.getmtime(path) > 24 * 60 * 60:
        return None
    try:
        with open(path, encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, json.JSONDecodeError):
        return None


def _lf_save_cache(path: str, payload: Any) -> None:
    try:
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
    except OSError:
        pass


def _lf_iso(timestamp: float) -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime(timestamp))


def _lf_session_id(timestamp: float) -> str:
    configured = os.environ.get("SESSION_ID")
    if configured and configured.strip():
        raw = configured.strip()
        safe = re.sub(r"[^A-Za-z0-9._-]", "_", raw).strip("._-")[:80]
        if not safe:
            safe = "session"
        if safe != raw:
            safe += "-" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:8]
        return safe
    if "session" not in _LF_SESSION_CACHE:
        _LF_SESSION_CACHE["session"] = (
            time.strftime("%H%M%S", time.localtime(timestamp)) + "-" + secrets.token_hex(3)
        )
    return _LF_SESSION_CACHE["session"]


def _lf_find_main_list(value: Any) -> tuple[str | None, list[Any] | None]:
    best_path: str | None = None
    best_list: list[Any] | None = None

    def walk(node: Any, path: str) -> None:
        nonlocal best_path, best_list
        if isinstance(node, list):
            if best_list is None or len(node) > len(best_list):
                best_path, best_list = path, node
        elif isinstance(node, dict):
            for key, child in node.items():
                walk(child, f"{path}.{key}" if path else key)

    walk(value, "")
    return best_path, best_list


def _lf_summarize(result: Any) -> None:
    if not isinstance(result, dict):
        print(f"Response type: {type(result).__name__}")
        print(json.dumps(result, ensure_ascii=False)[:500])
        return
    print(f"Top-level keys: {list(result.keys())}")
    for key in (
        "errcode",
        "errorCode",
        "code",
        "errmsg",
        "msg",
        "total",
        "totalCount",
        "count",
        "success",
    ):
        if key in result and isinstance(result[key], (int, float, bool, str)):
            print(f"  {key}: {result[key]}")
    list_path, main_list = _lf_find_main_list(result)
    if list_path is not None and main_list:
        sample = main_list[:3]
        print(f"Main list field: `{list_path}` (length={len(main_list)})")
        print(f"Sample (first {len(sample)} of {len(main_list)}):")
        print(json.dumps(sample, indent=2, ensure_ascii=False))


def _lf_ensure_meta(root: str, session_dir: str, date_text: str, session_id: str, timestamp: float) -> None:
    meta_path = os.path.join(session_dir, "_meta.json")
    if os.path.exists(meta_path):
        return
    meta = {
        "session_id": session_id,
        "date": date_text,
        "started_at": _lf_iso(timestamp),
        "skills_called": [],
        "deliverables": [],
        "data_files": [],
        "media_files": [],
    }
    with open(meta_path, "w", encoding="utf-8") as handle:
        json.dump(meta, handle, ensure_ascii=False, indent=2)
    try:
        with open(os.path.join(root, "index.jsonl"), "a", encoding="utf-8") as handle:
            handle.write(
                json.dumps(
                    {
                        "session_id": session_id,
                        "date": date_text,
                        "path": os.path.relpath(session_dir, root),
                        "started_at": _lf_iso(timestamp),
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )
    except OSError:
        pass


def _lf_update_meta(session_dir: str, file_path: str, timestamp: float) -> None:
    meta_path = os.path.join(session_dir, "_meta.json")
    try:
        with open(meta_path, encoding="utf-8") as handle:
            meta = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return
    if SLUG not in meta.setdefault("skills_called", []):
        meta["skills_called"].append(SLUG)
    relative = os.path.relpath(file_path, session_dir)
    if relative not in meta.setdefault("data_files", []):
        meta["data_files"].append(relative)
    meta["last_used_at"] = _lf_iso(timestamp)
    with open(meta_path, "w", encoding="utf-8") as handle:
        json.dump(meta, handle, ensure_ascii=False, indent=2)


def emit_result(result: Any, slug: str = SLUG, inline: bool = False) -> None:
    """Persist the complete response, printing full JSON only when reasonably small."""
    serialized = json.dumps(result, ensure_ascii=False, indent=2)
    timestamp = time.time()
    date_text = time.strftime("%Y-%m-%d", time.localtime(timestamp))
    session_id = _lf_session_id(timestamp)
    root = _lf_root()
    session_dir = os.path.join(root, date_text, session_id)
    os.makedirs(session_dir, exist_ok=True)
    _lf_ensure_meta(root, session_dir, date_text, session_id, timestamp)
    data_dir = os.path.join(session_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    output_path = os.path.join(data_dir, f"{slug}-{int(timestamp * 1_000_000)}.json")
    try:
        with open(output_path, "w", encoding="utf-8") as handle:
            handle.write(serialized)
        print(f"Saved full response: {output_path} ({len(serialized)} bytes)")
        _lf_update_meta(session_dir, output_path, timestamp)
    except OSError as exc:
        print(f"Failed to save to {output_path}: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
    if inline or len(serialized.encode("utf-8")) <= LF_SMALL_THRESHOLD:
        print(serialized)
    else:
        _lf_summarize(result)


def lf_inline_flag() -> bool:
    return "--inline" in sys.argv
