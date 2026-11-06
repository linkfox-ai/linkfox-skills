#!/usr/bin/env python3
"""
Amazon Store — processShipment (External Fulfillment Shipping v2024-09-11)
=========================================================================

POST `externalFulfillment/2024-09-11/shipments/{shipmentId}?operation=CONFIRM|REJECT`
Body 可选（REJECT 时常含 referenceId / lineItems）；可用 requestBody 整包传入。

官方参考: https://developer-docs.amazon.com/sp-api/reference/processshipment
"""

from __future__ import annotations

import json
import sys

from _spapi_ef_common import (
    PATH_SHIPMENTS,
    build_query,
    run_proxy,
    enc_path_seg,
    ensure_auth_skill_available,
    load_params_or_exit,
    require_fields,
)


def main() -> None:
    params = load_params_or_exit(
        "Usage: process_shipment.py '<JSON>'\n"
        "Required: sellerId, region, shipmentId, operation (CONFIRM|REJECT)\n"
        "Optional: requestBody | referenceId, lineItems"
    )
    if not params.get("skipDepCheck"):
        ensure_auth_skill_available("process_shipment.py")
    require_fields(params, ["sellerId", "region", "shipmentId", "operation"])

    op = str(params["operation"]).strip().upper()
    if op not in ("CONFIRM", "REJECT"):
        print("operation must be CONFIRM or REJECT", file=sys.stderr)
        sys.exit(1)

    path = f"{PATH_SHIPMENTS}/{enc_path_seg(params['shipmentId'])}"
    qs = build_query([("operation", op)])

    if params.get("requestBody") is not None:
        rb = params["requestBody"]
        if not isinstance(rb, dict):
            print("requestBody must be a JSON object", file=sys.stderr)
            sys.exit(1)
    else:
        rb = {}
        if params.get("referenceId") is not None:
            rb["referenceId"] = params["referenceId"]
        if params.get("lineItems") is not None:
            rb["lineItems"] = params["lineItems"]

    body_str = json.dumps(rb, ensure_ascii=False) if rb else None
    run_proxy(str(params['region']), path, 'POST', str(params['sellerId']), query_string=qs, body=body_str, result_field='processShipment', operation='process_shipment', ok_statuses=(200, 204), output_fields={'queryString': qs, 'requestBody': rb or None})


if __name__ == "__main__":
    main()
