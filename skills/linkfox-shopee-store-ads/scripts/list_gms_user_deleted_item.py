#!/usr/bin/env python3
"""Shopee 店铺广告：list_gms_user_deleted_item。

官方：https://open.shopee.com/documents/v2/v2.ads.list_gms_user_deleted_item?module=117&type=1
入参与响应见 references/apis/list-gms-user-deleted-item.md。
用法：python scripts/list_gms_user_deleted_item.py '<JSON 参数>' [--inline] [--no-cache]
"""
from _ads_api_runner import cli_main


def main() -> None:
    cli_main("list_gms_user_deleted_item")


if __name__ == "__main__":
    main()
