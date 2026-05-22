---
name: linkfox-amazon-store-feeds
description: 亚马逊店铺 Feeds（与 linkfox-amazon-store-auth / report / listings / pricing / orders 同系列），经 /spApi/developerProxy 调用 SP-API Feeds v2021-06-30：createFeedDocument、getFeedDocument、createFeed、getFeed、getFeeds、cancelFeed；另含 upload_feed_document 向预签名 URL 上传内容。当用户提到亚马逊 Feed、提交库存/Listing Feed、POST_FLAT_FILE、feedType、feedDocumentId、feedId、取消 Feed、查询 Feed 处理状态、Feeds API、SP-API 上传文件 时触发。
---

# Amazon 店铺 Feeds

本 skill 与 **`linkfox-amazon-store-auth`** 等同属 **Amazon Store** 系列：先 **`POST /spApi/storeTokens`**，再 **`POST /spApi/developerProxy`** 转发 **GET / POST / DELETE**。

## 官方参考索引

| 能力 | 文档 |
|------|------|
| createFeedDocument | [createFeedDocument](https://developer-docs.amazon.com/sp-api/reference/createfeeddocument) |
| getFeedDocument | [getFeedDocument](https://developer-docs.amazon.com/sp-api/reference/getfeeddocument) |
| createFeed | [createFeed](https://developer-docs.amazon.com/sp-api/reference/createfeed) |
| getFeed | [getFeed](https://developer-docs.amazon.com/sp-api/reference/getfeed) |
| getFeeds | [getFeeds](https://developer-docs.amazon.com/sp-api/reference/getfeeds) |
| cancelFeed | [cancelFeed](https://developer-docs.amazon.com/sp-api/reference/cancelfeed) |

---

## Prerequisites

1. 依赖 **`linkfox-amazon-store-auth`**；运行 `python scripts/check_auth_dependency.py`，exit **42** 时需先安装授权 skill。
2. 应用需具备 **Feeds** 相关角色；`feedType` 须与上传文件格式匹配（见 Amazon Feed Type Values 文档）。

---

## 典型工作流

1. **`create_feed_document.py`** → 得到 `feedDocumentId` 与 **`url`**（上传地址）。
2. **`upload_feed_document.py`** → 对 `url` **PUT** 上传 feed 文件（**不经** developerProxy）。
3. **`create_feed.py`** → 传入 `inputFeedDocumentId`、`feedType`、`marketplaceIds`。
4. **`get_feed.py`** / **`get_feeds.py`** → 轮询 `processingStatus`（如 IN_QUEUE、IN_PROGRESS、DONE、FATAL）。
5. 处理完成后用 **`get_feed_document.py`** 下载 **resultFeedDocumentId** 对应文档（再按返回 URL 自行下载结果文件）。

---

## Current Capabilities

| 能力 | path | method | 脚本 |
|------|------|--------|------|
| createFeedDocument | `feeds/2021-06-30/documents` | POST | `create_feed_document.py` |
| getFeedDocument | `feeds/2021-06-30/documents/{feedDocumentId}` | GET | `get_feed_document.py` |
| createFeed | `feeds/2021-06-30/feeds` | POST | `create_feed.py` |
| getFeed | `feeds/2021-06-30/feeds/{feedId}` | GET | `get_feed.py` |
| getFeeds | `feeds/2021-06-30/feeds` | GET | `get_feeds.py` |
| cancelFeed | `feeds/2021-06-30/feeds/{feedId}` | DELETE | `cancel_feed.py` |
| 上传文档内容 | createFeedDocument 返回的 URL | PUT | `upload_feed_document.py` |

共享模块：**`_spapi_feeds_common.py`**。

---

## Scripts 示例

```bash
export LINKFOXAGENT_API_KEY="<your-key>"

python scripts/create_feed_document.py '{"sellerId":"A1...","region":"NA","contentType":"text/tab-separated-values; charset=UTF-8"}'

python scripts/upload_feed_document.py '{"uploadUrl":"<from createFeedDocument>","contentType":"text/tab-separated-values; charset=UTF-8","filePath":"./inventory.tsv"}'

python scripts/create_feed.py '{"sellerId":"A1...","region":"NA","feedType":"POST_FLAT_FILE_INVLOADER_DATA","marketplaceIds":["ATVPDKIKX0DER"],"inputFeedDocumentId":"<feedDocumentId>"}'
```

---

## Display Rules

1. 先看 **`developerProxy.errcode` / `httpStatus`**；createFeedDocument 常为 **201**，createFeed 常为 **202**。
2. **getFeeds** 分页：仅用上一页 **`nextToken`** 作为下一请求的 **`paginationToken` 参数名在 Amazon 侧为 `nextToken`**（脚本字段名 `nextToken`）。
3. **upload** 失败与 SP-API 网关无关，检查 `uploadUrl` 是否过期、**Content-Type** 是否与 createFeedDocument 一致。
4. 网关 path 白名单需包含 **`feeds/2021-06-30/`** 前缀。

---

## Important Limitations

- 本 skill **不**代替 Amazon 侧 feed 文件 schema 校验；`feedType`、TSV/XML 格式以官方为准。
- 下载 **getFeedDocument** 返回的 **url** 内容需另行 HTTP GET（与 upload 类似，不经 developerProxy）。
- 详见 **`references/api.md`**。

**Feedback：** `skillName`：`linkfox-amazon-store-feeds`。

---
*更多跨境 skill：[LinkFox Skills](https://skill.linkfox.com/)*
