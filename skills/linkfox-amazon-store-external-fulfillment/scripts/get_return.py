#!/usr/bin/env python3
"""
Amazon Store — getReturn (External Fulfillment Returns v2024-09-11)
==================================================================

GET `externalFulfillment/2024-09-11/returns/{returnId}`

官方参考: https://developer-docs.amazon.com/sp-api/reference/getreturn
"""

from __future__ import annotations


from _spapi_ef_common import (
    PATH_RETURNS,
    run_proxy,
    enc_path_seg,
    ensure_auth_skill_available,
    load_params_or_exit,
    require_fields,
)


def main() -> None:
    params = load_params_or_exit(
        "Usage: get_return.py '<JSON>'\nRequired: sellerId, region, returnId"
    )
    if not params.get("skipDepCheck"):
        ensure_auth_skill_available("get_return.py")
    require_fields(params, ["sellerId", "region", "returnId"])

    path = f"{PATH_RETURNS}/{enc_path_seg(params['returnId'])}"
    run_proxy(str(params['region']), path, 'GET', str(params['sellerId']), result_field='returnItem', operation='get_return')


if __name__ == "__main__":
    main()
