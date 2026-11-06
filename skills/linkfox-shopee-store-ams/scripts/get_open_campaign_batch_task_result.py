#!/usr/bin/env python3
"""Shopee AMS：查询开放推广批量任务结果。

官方: https://open.shopee.com/documents/v2/v2.ams.get_open_campaign_batch_task_result?module=127&type=1
入参说明见 references/apis/get-open-campaign-batch-task-result.md。
"""
from _ams_api_runner import cli_main

def main():
    cli_main("get_open_campaign_batch_task_result")

if __name__ == "__main__":
    main()
