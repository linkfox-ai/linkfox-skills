#!/usr/bin/env python3
"""
Shopee Store — batch_update_tpf_warehouse_tracking_status

官方: https://open.shopee.com/documents/v2/v2.logistics.batch_update_tpf_warehouse_tracking_status?module=95&type=1

入参说明见 references/apis/batch-update-tpf-warehouse-tracking-status.md。
"""

from __future__ import annotations

import json
import sys

from _logistics_api_runner import run_logistics_api


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: batch_update_tpf_warehouse_tracking_status.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    run_logistics_api("batch_update_tpf_warehouse_tracking_status", params, "batch_update_tpf_warehouse_tracking_status.py")


if __name__ == "__main__":
    main()
