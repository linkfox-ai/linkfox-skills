#!/usr/bin/env python3
"""getItemReviewTrends — https://developer-docs.amazon.com/sp-api/reference/getitemreviewtrends"""

from _spapi_customer_feedback_common import (
    load_cli_params,
    query_marketplace_only,
    run_item_get,
)

if __name__ == "__main__":
    run_item_get(
        load_cli_params(),
        path_suffix="reviews/trends",
        result_key="itemReviewTrends",
        query_builder=query_marketplace_only,
        caller="get_item_review_trends.py",
    )
