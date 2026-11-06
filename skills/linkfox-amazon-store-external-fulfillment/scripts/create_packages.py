#!/usr/bin/env python3
"""
Amazon Store — createPackages (External Fulfillment Shipping v2024-09-11)
========================================================================

POST `externalFulfillment/2024-09-11/shipments/{shipmentId}/packages`
传 packages 数组，或 requestBody 整包（含 packages）。

官方参考: https://developer-docs.amazon.com/sp-api/reference/createpackages
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
        "Usage: create_packages.py '<JSON>'\n"
        "Required: sellerId, region, shipmentId, packages | requestBody"
    )
    if not params.get("skipDepCheck"):
        ensure_auth_skill_available("create_packages.py")
    require_fields(params, ["sellerId", "region", "shipmentId"])

    if params.get("requestBody") is not None:
        rb = params["requestBody"]
        if not isinstance(rb, dict):
            print("requestBody must be a JSON object", file=sys.stderr)
            sys.exit(1)
    elif params.get("packages") is not None:
        rb = {"packages": params["packages"]}
    else:
        print("Missing packages or requestBody", file=sys.stderr)
        sys.exit(1)

    path = f"{PATH_SHIPMENTS}/{enc_path_seg(params['shipmentId'])}/packages"
    body_str = json.dumps(rb, ensure_ascii=False)
    run_proxy(str(params['region']), path, 'POST', str(params['sellerId']), body=body_str, result_field='createPackages', operation='create_packages', ok_statuses=(200, 204), output_fields={'requestBody': rb})


if __name__ == "__main__":
    main()
