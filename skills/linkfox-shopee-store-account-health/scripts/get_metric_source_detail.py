#!/usr/bin/env python3
"""
Shopee 店铺账户健康 — get_metric_source_detail (v2.account_health.get_metric_source_detail)

官方: https://open.shopee.com/documents/v2/v2.account_health.get_metric_source_detail?module=103&type=1

入参说明见 references/apis/get-metric-source-detail.md。

用法：
  python get_metric_source_detail.py '{"shopId":"67890","metric_id":3,"page_no":1,"page_size":20}'
"""

from _account_health_api_runner import account_health_cli


def main() -> None:
    account_health_cli('get_metric_source_detail')


if __name__ == "__main__":
    main()
