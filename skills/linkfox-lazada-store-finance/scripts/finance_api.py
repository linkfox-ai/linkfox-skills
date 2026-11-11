#!/usr/bin/env python3
"""查询已授权 Lazada 店铺的资金记录。"""
from _operations import main

API_PATH = "/lazada/finance"
SLUG = "linkfox-lazada-store-finance"
OPERATIONS = {
    "listPayouts": False,
    "listTransactionDetails": False,
    "listAccountTransactions": False,
}


if __name__ == "__main__":
    raise SystemExit(main(API_PATH, SLUG, OPERATIONS,
                          private_fields={"payeeaccount", "remarks", "remark"}))
