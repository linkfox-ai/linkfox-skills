#!/usr/bin/env python3
"""getBrowseNodeReturnTrends — https://developer-docs.amazon.com/sp-api/reference/getbrowsenodereturntrends"""

from _spapi_customer_feedback_common import (
    load_cli_params,
    query_marketplace_only,
    run_browse_node_get,
)

if __name__ == "__main__":
    run_browse_node_get(
        load_cli_params(),
        path_suffix="returns/trends",
        result_key="browseNodeReturnTrends",
        query_builder=query_marketplace_only,
        caller="get_browse_node_return_trends.py",
    )
