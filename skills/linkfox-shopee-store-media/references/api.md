# linkfox-shopee-store-media — 参数与字段参考

Shopee **Media 模块**全部 6 个 API，经 **`POST /shopee/developerProxy`** 转发。

授权见 **`linkfox-shopee-store-auth`**。官方索引：[v2.media.upload_image](https://open.shopee.com/documents/v2/v2.media.upload_image?module=130&type=1)

> **Media vs MediaSpace**：本 skill 使用 `api/v2/media/...`（module=130）；`linkfox-shopee-store-media-space` 使用 `api/v2/media_space/...`（module=91）。接口名相同但 path 前缀不同，请按网关白名单选择。

## 通用约定

- **Base URL**：`https://tool-gateway.linkfox.com`
- **path**：须 `api/v2/media/...`
- **官方文档 URL 规则**：`https://open.shopee.com/documents/v2/v2.media.{api}?module=130&type=1`

---

## Media 模块总览

| # | API | Method | path | 脚本 | 官方文档 |
|---|-----|--------|------|------|----------|
| 1 | cancel_video_upload | POST | `api/v2/media/cancel_video_upload` | `cancel_video_upload.py` | [doc](https://open.shopee.com/documents/v2/v2.media.cancel_video_upload?module=130&type=1) |
| 2 | complete_video_upload | POST | `api/v2/media/complete_video_upload` | `complete_video_upload.py` | [doc](https://open.shopee.com/documents/v2/v2.media.complete_video_upload?module=130&type=1) |
| 3 | get_video_upload_result | GET | `api/v2/media/get_video_upload_result` | `get_video_upload_result.py` | [doc](https://open.shopee.com/documents/v2/v2.media.get_video_upload_result?module=130&type=1) |
| 4 | init_video_upload | POST | `api/v2/media/init_video_upload` | `init_video_upload.py` | [doc](https://open.shopee.com/documents/v2/v2.media.init_video_upload?module=130&type=1) |
| 5 | upload_image | POST | `api/v2/media/upload_image` | `upload_image.py` | [doc](https://open.shopee.com/documents/v2/v2.media.upload_image?module=130&type=1) |
| 6 | upload_video_part | POST | `api/v2/media/upload_video_part` | `upload_video_part.py` | [doc](https://open.shopee.com/documents/v2/v2.media.upload_video_part?module=130&type=1) |
通用入口：`media_api.py`（JSON 含 `"api": "<上表 API 名>"`）。

---

## 接口说明

| API | 说明 |
|-----|------|
| `upload_image` | 上传图片，返回 Shopee 图片 URL |
| `init_video_upload` | 初始化视频分片上传 |
| `upload_video_part` | 上传视频分片 |
| `complete_video_upload` | 完成视频上传 |
| `get_video_upload_result` | 查询上传结果 |
| `cancel_video_upload` | 取消上传 |

视频分片流程：`init_video_upload` → `upload_video_part`(×N) → `complete_video_upload` → `get_video_upload_result`

---

## curl 示例

```bash
curl -X POST ${LINKFOX_TOOL_GATEWAY}/shopee/developerProxy \
  -H "Authorization: $LINKFOX_AGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "path": "api/v2/media/upload_image",
    "method": "POST",
    "accessToken": "xxx",
    "shopId": "67890",
    "body": "..."
  }'
```

---

## Feedback API

```bash
curl -X POST https://skill-api.linkfox.com/api/v1/public/feedback \
  -H "Content-Type: application/json" \
  -d '{"skillName":"linkfox-shopee-store-media","sentiment":"POSITIVE",
       "category":"OTHER","content":"图片上传正常"}'
```
