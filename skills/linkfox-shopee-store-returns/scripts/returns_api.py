#!/usr/bin/env python3
"""Shopee 店铺退货退款通用入口；JSON 中的 api 选择 15 个 Returns 操作之一。

官方：https://open.shopee.com/documents/v2/v2.returns.<api>?module=102&type=1
参数、兼容与输出约定见 references/api.md。
"""

from _returns_api_runner import run_cli


def main() -> None:
    run_cli()


if __name__ == "__main__":
    main()
