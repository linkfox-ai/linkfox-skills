#!/usr/bin/env python3
"""getBrowseNodeReviewTopics — https://developer-docs.amazon.com/sp-api/reference/getbrowsenodereviewtopics"""

from _spapi_customer_feedback_common import (
    load_cli_params,
    query_marketplace_and_sort_by,
    run_browse_node_get,
)

if __name__ == "__main__":
    run_browse_node_get(
        load_cli_params(),
        path_suffix="reviews/topics",
        result_key="browseNodeReviewTopics",
        query_builder=query_marketplace_and_sort_by,
        caller="get_browse_node_review_topics.py",
    )
