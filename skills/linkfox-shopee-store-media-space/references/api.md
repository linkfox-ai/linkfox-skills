# linkfox-shopee-store-media-space — 参数与字段参考

Shopee **MediaSpace 模块**全部 6 个 API，经 **`POST /shopee/developerProxy`** 转发。

授权见 **`linkfox-shopee-store-auth`**。官方索引：[v2.media_space.init_video_upload](https://open.shopee.com/documents/v2/v2.media_space.init_video_upload?module=91&type=1)

## 通用约定

- **Base URL**：`https://tool-gateway.linkfox.com`
- **Method**：POST（网关），上游 Method 见各接口
- **Auth**：Header `Authorization: <api_key>`（`LINKFOXAGENT_API_KEY`）（如未配置 按 SKILL.md 的 **## 解决认证和积分问题** 处理）
- **流程**：`POST /shopee/storeTokens` → `POST /shopee/developerProxy`
- **path**：须 `api/v2/media_space/...`
- **标识**：通常传 **`shopId`**
- **官方文档 URL 规则**：`https://open.shopee.com/documents/v2/v2.media_space.{api}?module=91&type=1`
- **上传类接口**：视频分片上传需按顺序 `init_video_upload` → `upload_video_part`(多次) → `complete_video_upload` → `get_video_upload_result`

---

## MediaSpace 模块总览

| # | API | Method | path | 脚本 | 官方文档 |
|---|-----|--------|------|------|----------|
| 1 | cancel_video_upload | POST | `api/v2/media_space/cancel_video_upload` | `cancel_video_upload.py` | [doc](https://open.shopee.com/documents/v2/v2.media_space.cancel_video_upload?module=91&type=1) |
| 2 | complete_video_upload | POST | `api/v2/media_space/complete_video_upload` | `complete_video_upload.py` | [doc](https://open.shopee.com/documents/v2/v2.media_space.complete_video_upload?module=91&type=1) |
| 3 | get_video_upload_result | GET | `api/v2/media_space/get_video_upload_result` | `get_video_upload_result.py` | [doc](https://open.shopee.com/documents/v2/v2.media_space.get_video_upload_result?module=91&type=1) |
| 4 | init_video_upload | POST | `api/v2/media_space/init_video_upload` | `init_video_upload.py` | [doc](https://open.shopee.com/documents/v2/v2.media_space.init_video_upload?module=91&type=1) |
| 5 | upload_image | POST | `api/v2/media_space/upload_image` | `upload_image.py` | [doc](https://open.shopee.com/documents/v2/v2.media_space.upload_image?module=91&type=1) |
| 6 | upload_video_part | POST | `api/v2/media_space/upload_video_part` | `upload_video_part.py` | [doc](https://open.shopee.com/documents/v2/v2.media_space.upload_video_part?module=91&type=1) |
通用入口：`media_space_api.py`（JSON 含 `"api": "<上表 API 名>"`）。

---

## 接口说明

### 视频分片上传流程

| 步骤 | API | 说明 |
|------|-----|------|
| 1 | `init_video_upload` | 初始化上传，获取 upload_id 等 |
| 2 | `upload_video_part` | 上传各分片（可多次调用） |
| 3 | `complete_video_upload` | 完成上传 |
| 4 | `get_video_upload_result` | 查询上传结果/视频 URL |
| — | `cancel_video_upload` | 取消进行中的上传 |

### 图片上传

| API | 说明 |
|-----|------|
| `upload_image` | 上传图片，返回 Shopee 图片 URL（可用于 add_item 等） |

---

## 网关错误码

| errcode | 含义 | 建议 |
|---------|------|------|
| 1002 | 参数/未登录 | 检查 shopId 与 API Key |
| 1003 | 代理/网络异常 | 重试 |
| 1004 | 无授权记录 | auth skill |
| 1005 | path 未白名单 | 确认 `api/v2/media_space/...` |

---

## curl 示例

```bash
export KEY=$LINKFOX_AGENT_API_KEY
BASE=${LINKFOX_TOOL_GATEWAY}

curl -X POST $BASE/shopee/developerProxy -H "Authorization: $KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "path": "api/v2/media_space/init_video_upload",
    "method": "POST",
    "accessToken": "xxx",
    "shopId": "67890",
    "body": "{\"file_size\": 1048576, \"file_name\": \"demo.mp4\"}"
  }'
```

---

## Feedback API

```bash
curl -X POST https://skill-api.linkfox.com/api/v1/public/feedback \
  -H "Content-Type: application/json" \
  -d '{"skillName":"linkfox-shopee-store-media-space","sentiment":"POSITIVE",
       "category":"OTHER","content":"图片上传正常"}'
```
