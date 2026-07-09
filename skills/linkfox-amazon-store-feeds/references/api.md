# linkfox-amazon-store-feeds — API 参考（Feeds v2021-06-30）

## 1. 调用链

| 步骤 | 端点 | 说明 |
|------|------|------|
| 1 | `POST {BASE}/spApi/storeTokens` | `{"sellerId","region"}` → `accessToken` |
| 2 | `POST {BASE}/spApi/developerProxy` | 转发 SP-API（除文档上传/下载 URL 外） |

环境变量：`LINKFOX_AGENT_API_KEY`（或 `LINKFOXAGENT_API_KEY`，必填）；`LINKFOX_TOOL_GATEWAY`（可选，默认 `https://tool-gateway.linkfox.com`，回退 `STORE_API_BASE_URL` / `SPAPI_BASE_URL`）。

### developerProxy Body

| 字段 | 说明 |
|------|------|
| region | NA / EU / FE |
| path | 如 `feeds/2021-06-30/feeds`，无前导 `/` |
| method | GET / POST / DELETE |
| amzAccessToken | storeTokens 返回值 |
| queryString | 无 `?` 前缀 |
| body | POST 时为 JSON 字符串 |
| contentType | 一般 `application/json` |

网关响应：`errcode`、`httpStatus`、`body`（字符串）。成功 HTTP 可能为 **200 / 201 / 202 / 204**。

---

## 2. 脚本入参摘要

### 公共

| 字段 | 必填 | 说明 |
|------|------|------|
| sellerId | 是 | 卖家 ID |
| region | 是 | 区域 |
| skipDepCheck | 否 | 跳过本地 auth 探测 |

### create_feed_document.py

| 字段 | 必填 | 说明 |
|------|------|------|
| contentType | 是 | 与将要上传的文件 MIME 一致，如 `text/tab-separated-values; charset=UTF-8` |

解析字段：**`feedDocument`**（含 `feedDocumentId`、`url` 等，以 Amazon 为准）。

### upload_feed_document.py（不经 developerProxy）

| 字段 | 必填 | 说明 |
|------|------|------|
| uploadUrl | 是 | createFeedDocument 返回的 `url` |
| contentType | 是 | 与 createFeedDocument 相同 |
| filePath | 三选一 | 本地文件路径 |
| content | 三选一 | UTF-8 字符串内容 |
| contentBase64 | 三选一 | Base64 编码内容 |

### create_feed.py

| 字段 | 必填 | 说明 |
|------|------|------|
| feedType | 是 | 如 `POST_FLAT_FILE_INVLOADER_DATA` |
| marketplaceIds | 是 | 1～25 个站点 ID |
| inputFeedDocumentId | 是 | 已上传内容的文档 ID |
| feedOptions | 否 | 因 feedType 而异的对象 |

### get_feed.py / cancel_feed.py

| 字段 | 必填 |
|------|------|
| feedId | 是 |

### get_feeds.py

| 字段 | 必填 | 说明 |
|------|------|------|
| feedTypes | 条件 | 与 nextToken 二选一；最多 10 个 |
| nextToken | 条件 | 分页时**单独**传此参数 |
| marketplaceIds | 否 | 最多 10 个 |
| processingStatuses | 否 | CANCELLED, DONE, FATAL, IN_PROGRESS, IN_QUEUE |
| createdSince / createdUntil | 否 | ISO 8601 |
| pageSize | 否 | 1～100，默认 10 |

### get_feed_document.py

| 字段 | 必填 | 说明 |
|------|------|------|
| feedDocumentId | 是 | |
| enableContentEncodingUrlHeader | 否 | boolean；GZIP 时便于客户端自动解压 |

---

## 3. Feed 标准流程

```text
createFeedDocument → PUT uploadUrl (upload_feed_document.py)
    → createFeed → poll getFeed until DONE/FATAL
    → getFeedDocument(resultFeedDocumentId) → GET 结果 url
```

---

## 4. 常见 feedType（示例）

以 [Feed Type Values](https://developer-docs.amazon.com/sp-api/docs/feed-type-values) 为准，例如：

- `POST_PRODUCT_DATA` / `POST_INVENTORY_AVAILABILITY_DATA`
- `POST_FLAT_FILE_INVLOADER_DATA`
- `POST_ORDER_FULFILLMENT_DATA`

---

## 5. 错误与限制

- **403**：权限或 feedType 未授权。
- **1005**（网关）：path 未在白名单，需放行 `feeds/2021-06-30/`。
- **429**：降频；getFeeds 等有独立 usage plan。
- 上传 URL 有时效，过期需重新 createFeedDocument。

---

## 6. Feedback

上报问题时注明 **`skillName`: `linkfox-amazon-store-feeds`**，并附 `developerProxy` JSON（脱敏）。
