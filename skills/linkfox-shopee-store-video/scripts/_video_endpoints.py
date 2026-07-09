"""Shopee Video module API registry (v2.video.*)."""

from __future__ import annotations

from typing import Literal, TypedDict

SHOPEE_DOC_MODULE = "129"

class VideoEndpoint(TypedDict, total=False):
    path: str
    method: Literal["GET", "POST"]
    response_key: str
    required: list[str]
    body_fields: list[str]
    notes: str

VIDEO_ENDPOINTS: dict[str, VideoEndpoint] = {
    "get_cover_list": {
        "path": "api/v2/video/get_cover_list",
        "method": "GET",
        "response_key": "getCoverList",
        "notes": 'Video cover image list',
    },
    "edit_video_info": {
        "path": "api/v2/video/edit_video_info",
        "method": "POST",
        "response_key": "editVideoInfo",
        "notes": 'Edit video title/description/cover; pass body',
    },
    "post_video": {
        "path": "api/v2/video/post_video",
        "method": "POST",
        "response_key": "postVideo",
        "notes": 'Upload/publish video; pass full body',
    },
    "get_video_list": {
        "path": "api/v2/video/get_video_list",
        "method": "GET",
        "response_key": "getVideoList",
        "notes": 'Shop video list; pagination filters',
    },
    "get_video_detail": {
        "path": "api/v2/video/get_video_detail",
        "method": "GET",
        "response_key": "getVideoDetail",
        "notes": 'Video detail by video_id',
    },
    "delete_video": {
        "path": "api/v2/video/delete_video",
        "method": "POST",
        "response_key": "deleteVideo",
        "notes": 'Delete video; pass body with video_id',
    },
    "get_overview_performance": {
        "path": "api/v2/video/get_overview_performance",
        "method": "GET",
        "response_key": "getOverviewPerformance",
        "notes": 'Video overview performance metrics',
    },
    "get_metric_trend": {
        "path": "api/v2/video/get_metric_trend",
        "method": "GET",
        "response_key": "getMetricTrend",
        "notes": 'Performance metric trends',
    },
    "get_user_demographics": {
        "path": "api/v2/video/get_user_demographics",
        "method": "GET",
        "response_key": "getUserDemographics",
        "notes": 'Viewer demographics',
    },
    "get_video_performance_list": {
        "path": "api/v2/video/get_video_performance_list",
        "method": "GET",
        "response_key": "getVideoPerformanceList",
        "notes": 'Video performance list',
    },
    "get_prodcut_performance_list": {
        "path": "api/v2/video/get_prodcut_performance_list",
        "method": "GET",
        "response_key": "getProdcutPerformanceList",
        "notes": 'Product performance in videos (official spelling: prodcut)',
    },
    "get_video_detail_performance": {
        "path": "api/v2/video/get_video_detail_performance",
        "method": "GET",
        "response_key": "getVideoDetailPerformance",
        "notes": 'Single video performance detail',
    },
    "get_video_detail_metric_trend": {
        "path": "api/v2/video/get_video_detail_metric_trend",
        "method": "GET",
        "response_key": "getVideoDetailMetricTrend",
        "notes": 'Single video metric trend',
    },
    "get_video_detail_audience_distribution": {
        "path": "api/v2/video/get_video_detail_audience_distribution",
        "method": "GET",
        "response_key": "getVideoDetailAudienceDistribution",
        "notes": 'Single video audience distribution',
    },
    "get_video_detail_product_performance": {
        "path": "api/v2/video/get_video_detail_product_performance",
        "method": "GET",
        "response_key": "getVideoDetailProductPerformance",
        "notes": 'Single video product performance',
    },
}

RESERVED_PARAM_KEYS = frozenset({
    "shopId", "merchantId", "skipDepCheck", "body", "requestBody", "api", "contentType",
})

LIST_QUERY_FIELDS = frozenset()

def official_doc_url(api_name: str) -> str:
    return (
        f"https://open.shopee.com/documents/v2/v2.video.{api_name}"
        f"?module={SHOPEE_DOC_MODULE}&type=1"
    )

def list_api_names() -> list[str]:
    return sorted(VIDEO_ENDPOINTS.keys())
