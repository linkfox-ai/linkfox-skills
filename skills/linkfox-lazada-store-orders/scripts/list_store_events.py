#!/usr/bin/env python3
"""List the notifications recorded for an authorized Lazada store."""
import re

from call_api import run

API_PATH = "/lazada/events"
SLUG = "linkfox-lazada-store-orders-list-store-events"
CURSOR = re.compile(r"[1-9][0-9]{0,18}")
ID_FIELDS = ("eventId", "notifyId", "orderId", "orderItemId", "productId", "skuId",
             "reverseOrderId", "reverseOrderLineId", "packageId")


def valid_cursor(value):
    return isinstance(value, str) and CURSOR.fullmatch(value) and int(value) <= 2**63 - 1


def prepare(params):
    if not isinstance(params.get("connectionId"), str) or not params["connectionId"].strip():
        raise ValueError("请提供已授权店铺的 connectionId")
    if params.keys() - {"connectionId", "limit", "beforeId"}:
        raise ValueError("通知查询仅支持 connectionId、limit 和 beforeId")
    limit = params.get("limit", 20)
    if type(limit) is not int or not 1 <= limit <= 100:
        raise ValueError("limit 须为 1 至 100 的整数")
    if "beforeId" in params and not valid_cursor(params["beforeId"]):
        raise ValueError("beforeId 须使用上页返回的 nextBeforeId")
    return params


def interpret(payload):
    page = payload.get("data", payload)
    if not isinstance(page, dict) or not isinstance(page.get("events"), list):
        return False, {"error": "INVALID_EVENTS_RESPONSE"}
    cursor = page.get("nextBeforeId")
    if cursor is not None and not valid_cursor(cursor):
        return False, {"error": "INVALID_EVENTS_RESPONSE"}
    events = []
    for event in page["events"]:
        if (not isinstance(event, dict) or any(not isinstance(event.get(name), str)
                for name in ("eventId", "notifyId", "type"))
                or type(event.get("occurredAt")) is not int):
            return False, {"error": "INVALID_EVENTS_RESPONSE"}
        public = {name: event[name] for name in (*ID_FIELDS, "status", "type")
                  if isinstance(event.get(name), str)}
        public["occurredAt"] = event["occurredAt"]
        events.append(public)
    return True, {"events": events, "nextBeforeId": cursor}


def main(argv=None):
    return run(API_PATH, SLUG, argv=argv, prepare=prepare, interpret=interpret)


if __name__ == "__main__":
    raise SystemExit(main())
