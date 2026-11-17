#!/usr/bin/env python3
"""getBrowseNodeReviewTrends — https://developer-docs.amazon.com/sp-api/reference/getbrowsenodereviewtrends"""

from _spapi_customer_feedback_common import (
    load_cli_params,
    query_marketplace_only,
    run_browse_node_get,
)

if __name__ == "__main__":
    run_browse_node_get(
        load_cli_params(),
        path_suffix="reviews/trends",
        result_key="browseNodeReviewTrends",
        query_builder=query_marketplace_only,
        caller="get_browse_node_review_trends.py",
    )
