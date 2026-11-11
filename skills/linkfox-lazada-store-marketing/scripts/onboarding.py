#!/usr/bin/env python3
"""LinkFox account setup, credential checks and compute billing."""

import argparse
import base64
from http.client import HTTPException
import json
import os
import re
import sys
from urllib.error import HTTPError
from urllib.parse import urlsplit
from urllib.request import Request, build_opener

from call_api import (
    NoRedirect, configure_stdout, decode, gateway_failure, gateway_request,
    get_api_base, get_api_key, ok, output_path, sanitize,
)


AGREEMENTS = {
    "user_agreement": "https://agent.linkfox.com/agreement/term",
    "service_agreement": "https://agent.linkfox.com/agreement/service",
    "privacy_policy": "https://agent.linkfox.com/agreement/privacy",
}
PAY_METHODS = {"wechat": "WX_PAY", "alipay": "ALI_PAY"}
LOGIN_UID = "eyJhX2lkIjoiNmEyMmM4YjA1YmM5MTZhIiwiZF9pZCI6IiJ9"
ORDER_STATES = {
    "wait_pay": "unpaid", "paid": "paid", "finished": "paid",
    "expire": "expired", "expired": "expired", "cancel": "cancelled", "cancelled": "cancelled",
}


class GatewayFailure(Exception):
    def __init__(self, diagnostic):
        self.diagnostic = diagnostic


def gateway(method, path, key, params=None):
    base = (os.environ.get("LINKFOX_AGENT_API_URL") or get_api_base()).rstrip("/")
    try:
        status, raw = gateway_request(path, params or {}, key, method=method, base=base, timeout=30)
        payload = decode(raw)
    except (HTTPException, OSError, ValueError):
        raise GatewayFailure({"error": "GATEWAY_REQUEST_FAILED"}) from None
    if not ok(status, payload):
        raise GatewayFailure(sanitize(gateway_failure(status, payload), payload, key, frozenset()))
    return payload


def payload_data(payload):
    return payload["data"] if isinstance(payload.get("data"), dict) else payload


def auth_headers(origin, source, token="", user_id="", group_id=""):
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json;charset=UTF-8",
        "Origin": f"https://{origin}",
        "Referer": f"https://{origin}/",
        "source": source,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
        "uid": os.environ.get("LINKFOX_LOGIN_FIXED_UID") or LOGIN_UID,
    }
    if token:
        headers["Authorization"] = token
    if user_id:
        parts = token.split(".")
        claims = {}
        if len(parts) >= 2:
            try:
                part = parts[1]
                decoded = json.loads(base64.urlsafe_b64decode(part + "=" * (-len(part) % 4)))
                if isinstance(decoded, dict):
                    claims = decoded
            except ValueError:
                pass
        raw = json.dumps({"a_id": claims.get("a", ""), "d_id": user_id}, separators=(",", ":")).encode()
        headers["uid"] = base64.urlsafe_b64encode(raw).decode()
    if group_id:
        headers["tid"] = group_id
    return headers


def _http_post(base, path, body, headers, stage):
    try:
        request = Request(base + path, json.dumps(body).encode("utf-8"), headers, method="POST")
        with build_opener(NoRedirect).open(request, timeout=30) as response:
            payload = json.loads(response.read())
    except HTTPError as error:
        error.close()
        raise GatewayFailure({"error": f"{stage}: HTTP_{error.code}"}) from None
    except (HTTPException, OSError, ValueError):
        raise GatewayFailure({"error": f"{stage}: REQUEST_FAILED"}) from None
    if not isinstance(payload, dict):
        raise GatewayFailure({"error": f"{stage}: INVALID_RESPONSE"})
    return payload


def login_base():
    return (os.environ.get("LINKFOX_LOGIN_API_URL") or "https://api.linkfox.com").rstrip("/")


def auth_accepted(payload):
    return payload.get("success") is True or payload.get("code") == "OK"


def send_code(phone):
    response = _http_post(login_base(), "/user/v1/web/login", {
        "type": "sms", "method": "getVerifyCode",
        "data": {"authPhone": phone, "areaCode": "+86", "clientChannel": "LinkFoxAgent"},
    }, auth_headers("ai.linkfox.com", "ai-linkfox-web"), "send-code")
    if not auth_accepted(response):
        raise GatewayFailure({"error": "send-code: SMS_REJECTED", "sent": False})
    return {"sent": True, "phone": f"{phone[:3]}****{phone[-4:]}",
            "area_code": "+86", "agreements": AGREEMENTS}


def login(phone, code, channel):
    response = _http_post(login_base(), "/user/v3/web/login", {
        "type": "sms", "method": "login", "systemId": "LinkFoxAgent",
        "data": {"areaCode": "+86", "authPhone": phone, "authCode": code, "sourceChannel": channel},
    }, auth_headers("ai.linkfox.com", "ai-linkfox-web"), "login")
    data = response.get("data")
    if not auth_accepted(response) or not isinstance(data, dict):
        raise GatewayFailure({"error": "login: LOGIN_REJECTED"})
    token, user_id = data.get("accessToken"), data.get("userId")
    if not isinstance(token, str) or not token or not user_id:
        raise GatewayFailure({"error": "login: INVALID_IDENTITY_RESPONSE"})

    agent_base = (os.environ.get("LINKFOX_AGENT_USER_API_URL") or "https://agent-api.linkfox.com").rstrip("/")
    if data.get("newUser") or data.get("isFirstRegister"):
        try:
            _http_post(agent_base, "/account/loginByToken", {
                "token": token, "refreshToken": data.get("refreshToken") or "",
                "device": {"aid": "3026344186", "did": "", "type": "Windows",
                           "os": "10", "model": "149.0.0.0", "brand": "Chrome"},
            }, auth_headers("agent.linkfox.com", "agent-linkfox-web", token), "loginByToken")
        except GatewayFailure:
            pass  # The optional first-login reward must not block Key setup.

    profile = _http_post(login_base(), "/linkFoxApp/api/userCenter/userInfo", {},
                        auth_headers("agent.linkfox.com", "agent-linkfox-web", token, str(user_id)), "userInfo")
    teams = payload_data(profile).get("teamList")
    if profile.get("code") != "OK" or not isinstance(teams, list):
        raise GatewayFailure({"error": "userInfo: INVALID_TEAM_RESPONSE"})
    teams = [team for team in teams if isinstance(team, dict) and team.get("agentTeamId")]
    if not teams:
        raise GatewayFailure({"error": "userInfo: OPEN_TEAM_IN_LINKFOX_PORTAL"})
    team = next((team for team in teams if team.get("isSelect") == 1), teams[0])
    group_id = str(team["agentTeamId"])
    headers = auth_headers("ai.linkfox.com", "agent-linkfox-web", token, str(user_id), group_id)
    body = {"id": group_id}
    for stage in ("getApiToken", "generateApiToken"):
        result = _http_post(agent_base, f"/group/{stage}", body, headers, stage)
        if result.get("errcode") not in (200, "200"):
            raise GatewayFailure({"error": f"{stage}: API_KEY_REQUEST_REJECTED"})
        key = payload_data(result).get("token")
        if isinstance(key, str) and key and key != token and key != data.get("refreshToken"):
            return {"api_key": key, "phone": f"{phone[:3]}****{phone[-4:]}",
                    "source": "existing" if stage == "getApiToken" else "generated"}
        if key != "":
            break
    raise GatewayFailure({"error": "login: API_KEY_MISSING"})


def normalize_package(package):
    if not isinstance(package, dict) or not isinstance(package.get("packageId"), str):
        return None
    price = package.get("packagePrice")
    if type(price) not in (int, float, str) or not re.fullmatch(r"[0-9]+(?:\.[0-9]+)?", str(price)):
        return None
    if float(price) <= 0:
        return None
    return {
        "plan_id": package["packageId"], "name": package.get("packageName"), "price": price,
        "currency": "CNY", "credits": package.get("creditAmount"),
        "validity_period": package.get("validityPeriod"),
        "validity_period_type": package.get("validityPeriodType"),
        "available_methods": list(PAY_METHODS),
    }


def current_account(key):
    user = payload_data(gateway("GET", "/account/currentByAPI", key))
    if type(user.get("isTeamUser")) is not bool:
        raise GatewayFailure({"error": "INVALID_ACCOUNT_RESPONSE"})
    return user


def list_plans(key, user=None):
    if user is None:
        user = current_account(key)
    raw = gateway("POST", "/package/getByTypeByAPI", key, {"packageType": 7 if user["isTeamUser"] else 1})
    packages = payload_data(raw).get("packageList")
    if not isinstance(packages, list):
        raise GatewayFailure({"error": "INVALID_PLAN_RESPONSE"})
    plans = [plan for plan in map(normalize_package, packages) if plan is not None]
    return sanitize({"plans": plans}, raw, key, frozenset())


def payment_link(value):
    if not isinstance(value, str) or not value or "[redacted]" in value or any(ch.isspace() for ch in value):
        return None
    try:
        url = urlsplit(value)
        if url.scheme in {"https", "weixin"} and url.hostname and not url.username and not url.password:
            return value
    except ValueError:
        pass
    return None


def create_order(key, plan_id, method):
    user = current_account(key)
    plans = list_plans(key, user)["plans"]
    if not any(plan["plan_id"] == plan_id and method in plan["available_methods"] for plan in plans):
        raise GatewayFailure({"error": "ORDER_PLAN_OR_METHOD_UNAVAILABLE"})
    group_id = user.get("currentGroupId")
    if not isinstance(group_id, str) or not group_id:
        raise GatewayFailure({"error": "INVALID_ACCOUNT_GROUP"})
    path = "/order/createTeamOrderByAPI" if user["isTeamUser"] else "/order/createByAPI"

    try:
        import qrcode
        from qrcode.image.pil import PilImage
    except ImportError:
        qrcode = None
    qr_path = None
    if qrcode is not None:
        try:
            qr_path = output_path("linkfox-compute-order").with_suffix(".png")
            fd = os.open(qr_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            os.close(fd)
        except (OSError, ValueError):
            raise GatewayFailure({"error": "ORDER_QR_OUTPUT_NOT_WRITABLE"}) from None

    keep_qr = False
    try:
        try:
            raw = gateway("POST", path, key, {
                "packageId": plan_id, "payType": PAY_METHODS[method], "payDeviceType": "PC",
                "memberId": "ignored", "groupId": group_id,
            })
        except GatewayFailure as failure:
            status = failure.diagnostic.get("httpStatus")
            if status not in (400, 401, 402, 403, 404, 409, 422):
                failure.diagnostic["error"] = "ORDER_RESULT_UNKNOWN"
            raise
        data = payload_data(raw)
        result = sanitize({"order_id": data.get("orderId"), "state": data.get("state"),
                           "pay_price": data.get("payPrice"), "time_left": data.get("timeLeft"),
                           "pay_url": data.get("payUrl"), "qr_content": data.get("payQrcode")},
                          raw, key, frozenset())
        if not isinstance(result["order_id"], str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,128}", result["order_id"]):
            raise GatewayFailure({"error": "ORDER_RESULT_UNKNOWN"})
        qr_content = payment_link(result.pop("qr_content"))
        result["pay_url"] = payment_link(result["pay_url"]) or qr_content
        if result["pay_url"] is None:
            raise GatewayFailure({"error": "ORDER_PAYMENT_LINK_MISSING", "order_id": result["order_id"]})
        if qr_path is not None:
            try:
                qr = qrcode.QRCode(border=1, image_factory=PilImage)
                qr.add_data(qr_content or result["pay_url"])
                qr.make(fit=True)
                qr.make_image(fill_color="black", back_color="white").save(qr_path)
                result["png_path"] = str(qr_path)
                keep_qr = True
            except (OSError, ValueError, qrcode.exceptions.DataOverflowError):
                result["qr_render_error"] = "ORDER_QR_RENDER_FAILED"
        return result
    finally:
        if qr_path is not None and not keep_qr:
            try:
                qr_path.unlink(missing_ok=True)
            except OSError:
                pass


def query_order(key, order_id):
    raw = gateway("POST", "/order/getByAPI", key, {"orderId": order_id})
    data = payload_data(raw)
    state = data.get("state")
    if not isinstance(state, str) or not state:
        raise GatewayFailure({"error": "INVALID_ORDER_RESPONSE"})
    result = {"order_id": order_id, "status": ORDER_STATES.get(state, "unknown"),
              "paid_at": data.get("payDate"), "pay_price": data.get("payPrice"),
              "time_left": data.get("timeLeft")}
    return sanitize(result, raw, key, frozenset())


def main(argv=None):
    configure_stdout()
    parser = argparse.ArgumentParser(description="LinkFox 账号与算力引导")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("check-key", help="检查当前会话是否已配置 LinkFox Key")
    sms = commands.add_parser("send-code", help="发送短信验证码")
    sms.add_argument("phone")
    sign_in = commands.add_parser("login", help="验证码登录并获取 API Key")
    sign_in.add_argument("phone")
    sign_in.add_argument("code")
    sign_in.add_argument("--channel", default="skill")
    commands.add_parser("list-plans", help="只读查询可用的算力套餐")
    order = commands.add_parser("order", help="创建已确认的算力订单")
    order.add_argument("plan_id")
    order.add_argument("method", choices=PAY_METHODS)
    query = commands.add_parser("query", help="只读查询已有 LinkFox 算力订单")
    query.add_argument("order_id")
    args = parser.parse_args(argv)
    key = get_api_key()
    try:
        if args.command == "check-key":
            result, exit_code = {"configured": bool(key)}, 0 if key else 2
        elif args.command in {"send-code", "login"}:
            phone = args.phone.strip()
            if not re.fullmatch(r"[0-9]{11}", phone):
                result, exit_code = {"error": f"{args.command}: INVALID_PHONE"}, 2
            elif args.command == "send-code":
                result, exit_code = send_code(phone), 0
            elif not re.fullmatch(r"[0-9]{4,8}", args.code.strip()):
                result, exit_code = {"error": "login: INVALID_CODE"}, 2
            else:
                result, exit_code = login(phone, args.code.strip(), args.channel or "skill"), 0
        elif not key:
            result, exit_code = {"error": "LINKFOX_KEY_REQUIRED"}, 2
        elif args.command == "list-plans":
            result, exit_code = list_plans(key), 0
        elif args.command == "order":
            result, exit_code = create_order(key, args.plan_id, args.method), 0
        elif re.fullmatch(r"[A-Za-z0-9_-]{1,128}", args.order_id):
            result, exit_code = query_order(key, args.order_id), 0
        else:
            result, exit_code = {"error": "INVALID_ORDER_ID"}, 2
    except GatewayFailure as failure:
        result, exit_code = failure.diagnostic, 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
