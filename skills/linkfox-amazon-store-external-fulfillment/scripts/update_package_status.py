#!/usr/bin/env python3
"""
Amazon Store — updatePackageStatus (External Fulfillment Shipping v2024-09-11)
==============================================================================

PATCH `externalFulfillment/2024-09-11/shipments/{shipmentId}/packages/{packageId}`
Body: status / subStatus / reason；或 requestBody 整包。

官方参考: https://developer-docs.amazon.com/sp-api/reference/updatepackagestatus
"""

from __future__ import annotations

import json
import sys

from _spapi_ef_common import (
    PATH_SHIPMENTS,
    run_proxy,
    enc_path_seg,
    ensure_auth_skill_available,
    load_params_or_exit,
    require_fields,
)


def main() -> None:
    params = load_params_or_exit(
        "Usage: update_package_status.py '<JSON>'\n"
        "Required: sellerId, region, shipmentId, packageId, "
        "requestBody | (status [, subStatus, reason])"
    )
    if not params.get("skipDepCheck"):
        ensure_auth_skill_available("update_package_status.py")
    require_fields(params, ["sellerId", "region", "shipmentId", "packageId"])

    if params.get("requestBody") is not None:
        rb = params["requestBody"]
        if not isinstance(rb, dict):
            print("requestBody must be a JSON object", file=sys.stderr)
            sys.exit(1)
    else:
        if "status" not in params:
            print("Missing status or requestBody", file=sys.stderr)
            sys.exit(1)
        rb = {"status": params["status"]}
        if params.get("subStatus") is not None:
            rb["subStatus"] = params["subStatus"]
        if params.get("reason") is not None:
            rb["reason"] = params["reason"]

    path = (
        f"{PATH_SHIPMENTS}/{enc_path_seg(params['shipmentId'])}"
        f"/packages/{enc_path_seg(params['packageId'])}"
    )
    body_str = json.dumps(rb, ensure_ascii=False)
    run_proxy(str(params['region']), path, 'PATCH', str(params['sellerId']), body=body_str, result_field='updatePackageStatus', operation='update_package_status', ok_statuses=(200, 204), output_fields={'requestBody': rb})


if __name__ == "__main__":
    main()
