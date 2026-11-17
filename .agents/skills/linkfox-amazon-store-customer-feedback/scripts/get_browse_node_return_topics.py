#!/usr/bin/env python3
"""getBrowseNodeReturnTopics — https://developer-docs.amazon.com/sp-api/reference/getbrowsenodereturntopics"""

from _spapi_customer_feedback_common import (
    load_cli_params,
    query_marketplace_and_sort_by,
    run_browse_node_get,
)

if __name__ == "__main__":
    run_browse_node_get(
        load_cli_params(),
        path_suffix="returns/topics",
        result_key="browseNodeReturnTopics",
        query_builder=query_marketplace_and_sort_by,
        caller="get_browse_node_return_topics.py",
    )
