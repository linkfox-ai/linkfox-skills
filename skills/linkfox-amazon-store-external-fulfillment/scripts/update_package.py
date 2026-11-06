#!/usr/bin/env python3
"""
Amazon Store — updatePackage (External Fulfillment Shipping v2024-09-11)
=======================================================================

PUT `externalFulfillment/2024-09-11/shipments/{shipmentId}/packages/{packageId}`

官方参考: https://developer-docs.amazon.com/sp-api/reference/updatepackage
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
        "Usage: update_package.py '<JSON>'\n"
        "Required: sellerId, region, shipmentId, packageId, requestBody"
    )
    if not params.get("skipDepCheck"):
        ensure_auth_skill_available("update_package.py")
    require_fields(params, ["sellerId", "region", "shipmentId", "packageId", "requestBody"])

    rb = params["requestBody"]
    if not isinstance(rb, dict):
        print("requestBody must be a JSON object", file=sys.stderr)
        sys.exit(1)

    path = (
        f"{PATH_SHIPMENTS}/{enc_path_seg(params['shipmentId'])}"
        f"/packages/{enc_path_seg(params['packageId'])}"
    )
    body_str = json.dumps(rb, ensure_ascii=False)
    run_proxy(str(params['region']), path, 'PUT', str(params['sellerId']), body=body_str, result_field='updatePackage', operation='update_package', ok_statuses=(200, 204), output_fields={'requestBody': rb})


if __name__ == "__main__":
    main()
