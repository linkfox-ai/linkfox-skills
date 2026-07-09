# linkfox-shopee-store-video — 参数与字段参考

Shopee **Video 模块**全部 15 个 API，经 **`POST /shopee/developerProxy`** 转发。

授权见 **`linkfox-shopee-store-auth`**。官方索引：[v2.video.get_cover_list](https://open.shopee.com/documents/v2/v2.video.get_cover_list?module=129&type=1)

## 通用约定

- **Base URL**：`https://tool-gateway.linkfox.com`
- **Method**：POST（网关），上游 Method 见各接口
- **Auth**：Header `Authorization: <api_key>`（`LINKFOXAGENT_API_KEY`）
- **流程**：`POST /shopee/storeTokens` → `POST /shopee/developerProxy`
- **path**：须 `api/v2/video/...`
- **标识**：店铺级 API，通常传 **`shopId`**
- **官方文档 URL 规则**：`https://open.shopee.com/documents/v2/v2.video.{api}?module=129&type=1`
- **官方拼写**：`get_prodcut_performance_list`（product 拼写为 prodcut）

---

## Video 模块总览

| # | API | Method | path | 脚本 | 官方文档 |
|---|-----|--------|------|------|----------|
| 1 | delete_video | POST | `api/v2/video/delete_video` | `delete_video.py` | [doc](https://open.shopee.com/documents/v2/v2.video.delete_video?module=129&type=1) |
| 2 | edit_video_info | POST | `api/v2/video/edit_video_info` | `edit_video_info.py` | [doc](https://open.shopee.com/documents/v2/v2.video.edit_video_info?module=129&type=1) |
| 3 | get_cover_list | GET | `api/v2/video/get_cover_list` | `get_cover_list.py` | [doc](https://open.shopee.com/documents/v2/v2.video.get_cover_list?module=129&type=1) |
| 4 | get_metric_trend | GET | `api/v2/video/get_metric_trend` | `get_metric_trend.py` | [doc](https://open.shopee.com/documents/v2/v2.video.get_metric_trend?module=129&type=1) |
| 5 | get_overview_performance | GET | `api/v2/video/get_overview_performance` | `get_overview_performance.py` | [doc](https://open.shopee.com/documents/v2/v2.video.get_overview_performance?module=129&type=1) |
| 6 | get_prodcut_performance_list | GET | `api/v2/video/get_prodcut_performance_list` | `get_prodcut_performance_list.py` | [doc](https://open.shopee.com/documents/v2/v2.video.get_prodcut_performance_list?module=129&type=1) |
| 7 | get_user_demographics | GET | `api/v2/video/get_user_demographics` | `get_user_demographics.py` | [doc](https://open.shopee.com/documents/v2/v2.video.get_user_demographics?module=129&type=1) |
| 8 | get_video_detail | GET | `api/v2/video/get_video_detail` | `get_video_detail.py` | [doc](https://open.shopee.com/documents/v2/v2.video.get_video_detail?module=129&type=1) |
| 9 | get_video_detail_audience_distribution | GET | `api/v2/video/get_video_detail_audience_distribution` | `get_video_detail_audience_distribution.py` | [doc](https://open.shopee.com/documents/v2/v2.video.get_video_detail_audience_distribution?module=129&type=1) |
| 10 | get_video_detail_metric_trend | GET | `api/v2/video/get_video_detail_metric_trend` | `get_video_detail_metric_trend.py` | [doc](https://open.shopee.com/documents/v2/v2.video.get_video_detail_metric_trend?module=129&type=1) |
| 11 | get_video_detail_performance | GET | `api/v2/video/get_video_detail_performance` | `get_video_detail_performance.py` | [doc](https://open.shopee.com/documents/v2/v2.video.get_video_detail_performance?module=129&type=1) |
| 12 | get_video_detail_product_performance | GET | `api/v2/video/get_video_detail_product_performance` | `get_video_detail_product_performance.py` | [doc](https://open.shopee.com/documents/v2/v2.video.get_video_detail_product_performance?module=129&type=1) |
| 13 | get_video_list | GET | `api/v2/video/get_video_list` | `get_video_list.py` | [doc](https://open.shopee.com/documents/v2/v2.video.get_video_list?module=129&type=1) |
| 14 | get_video_performance_list | GET | `api/v2/video/get_video_performance_list` | `get_video_performance_list.py` | [doc](https://open.shopee.com/documents/v2/v2.video.get_video_performance_list?module=129&type=1) |
| 15 | post_video | POST | `api/v2/video/post_video` | `post_video.py` | [doc](https://open.shopee.com/documents/v2/v2.video.post_video?module=129&type=1) |
通用入口：`video_api.py`（JSON 含 `"api": "<上表 API 名>"`）。

---

## 常用接口说明

### 视频管理

| API | 要点 |
|-----|------|
| `get_cover_list` | 视频封面列表 |
| `post_video` | 发布/上传视频；POST `body` |
| `get_video_list` | 店铺视频列表 |
| `get_video_detail` | 视频详情 |
| `edit_video_info` | 编辑标题/描述/封面 |
| `delete_video` | 删除视频 |

### 效果分析

| API | 要点 |
|-----|------|
| `get_overview_performance` | 整体效果概览 |
| `get_metric_trend` | 指标趋势 |
| `get_user_demographics` | 观众画像 |
| `get_video_performance_list` | 视频效果列表 |
| `get_video_detail_performance` | 单视频效果详情 |
| `get_video_detail_metric_trend` | 单视频指标趋势 |
| `get_video_detail_audience_distribution` | 单视频受众分布 |
| `get_video_detail_product_performance` | 单视频商品效果 |
| `get_prodcut_performance_list` | 商品在视频中的效果（官方拼写 prodcut） |

---

## 网关错误码

| errcode | 含义 | 建议 |
|---------|------|------|
| 1002 | 参数/未登录 | 检查 shopId 与 API Key |
| 1003 | 代理/网络异常 | 重试 |
| 1004 | 无授权记录 | auth skill |
| 1005 | path 未白名单 | 确认 `api/v2/video/...` |

---

## curl 示例

```bash
export KEY=${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}
BASE=${LINKFOX_TOOL_GATEWAY}

curl -X POST $BASE/shopee/developerProxy -H "Authorization: $KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "path": "api/v2/video/get_cover_list",
    "method": "GET",
    "accessToken": "xxx",
    "shopId": "67890"
  }'
```

---

## Feedback API

```bash
curl -X POST https://skill-api.linkfox.com/api/v1/public/feedback \
  -H "Content-Type: application/json" \
  -d '{"skillName":"linkfox-shopee-store-video","sentiment":"POSITIVE",
       "category":"OTHER","content":"视频列表查询正常"}'
```
