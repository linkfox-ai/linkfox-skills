#!/usr/bin/env python3
"""getItemReviewTopics — https://developer-docs.amazon.com/sp-api/reference/getitemreviewtopics"""

from _spapi_customer_feedback_common import (
    load_cli_params,
    query_marketplace_and_sort_by,
    run_item_get,
)

if __name__ == "__main__":
    run_item_get(
        load_cli_params(),
        path_suffix="reviews/topics",
        result_key="itemReviewTopics",
        query_builder=query_marketplace_and_sort_by,
        caller="get_item_review_topics.py",
    )
