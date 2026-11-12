#!/usr/bin/env python3
"""getItemBrowseNode — https://developer-docs.amazon.com/sp-api/reference/getitembrowsenode"""

from _spapi_customer_feedback_common import (
    load_cli_params,
    query_marketplace_only,
    run_item_get,
)

if __name__ == "__main__":
    run_item_get(
        load_cli_params(),
        path_suffix="browseNode",
        result_key="itemBrowseNode",
        query_builder=query_marketplace_only,
        caller="get_item_browse_node.py",
    )
