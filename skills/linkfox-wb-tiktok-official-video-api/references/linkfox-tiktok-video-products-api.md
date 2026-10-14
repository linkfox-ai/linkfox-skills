# TikTok 可挂车商品 API

## MCP 调用

- MCP server：`LinkFox`
- 唯一工具：`proxy_call`
- 本 reference 的精确 `toolName`：`tiktokVideo/developerProxy`
- `arguments` 使用 `openId` 选择已授权达人，并保留 `path`、`method`、`region`、`queryString`。不得传 headers、API Key 或 token。

返回时先检查 MCP/`isError`，再读代理包络；`body` 是 JSON 字符串时只解析一次。相同 `toolName + arguments` 不重复调用，失败、空结果或结果不理想不自动重试，不作 HTTP fallback。

### 代理响应包络

| 响应字段路径 | 类型 | 说明 |
|---|---|---|
| httpStatus | integer | 上游 HTTP 状态码 |
| contentType | string | 响应 Content-Type |
| body | string | TikTok API 原始响应正文（JSON 字符串） |

## 1. 店铺商品

上游路径：`affiliate_creator/202509/shop_products`；精确 `toolName`：`tiktokVideo/developerProxy`。

| 业务参数 | 必填 | 类型 | 默认/范围 | 说明 |
|---|---|---|---|---|
| openId | 是 | string | 来源未说明 | 已授权 creator open_id；网关据此解析授权上下文 |
| title_keyword | 否 | string | 来源未说明 | 商品标题关键词 |
| sort_field | 否 | string | `PRODUCT_ID` | `PRODUCT_ID` / `PRICE` / `SALE` |
| sort_order | 否 | string | `DESC` | `DESC` / `ASC` |
| page_size | 是 | int32 | 1~20，推荐 20 | 每页返回商品数 |
| page_token | 否 | string | 来源未说明 | 上一页游标；首页不传 |

```json
{"toolName":"tiktokVideo/developerProxy","arguments":{"openId":"<creator_open_id>","path":"affiliate_creator/202509/shop_products","method":"GET","region":"global","queryString":"title_keyword=apple&sort_field=SALE&sort_order=DESC&page_size=20"}}
```

### TikTok body 响应

| 响应字段路径 | 类型 | 说明 |
|---|---|---|
| code | int | 业务状态码 |
| message | string | 业务消息 |
| request_id | string | 请求日志 ID |
| data | object | 商品检索结果（含 `next_page_token` 等）；内部字段来源未说明 |

首次不传 `page_token`；只有用户明确要求下一页且 `data.next_page_token` 非空时再调用。来源未提供 `data` 的完整子字段表，因此不能声称 `product_id` 的具体层级；按实际响应定位并保留原字段。

错误码：`16015006` 无选品区域；`16015007` 无销售区域；`16501011` 无权限；`16504002` 查询达人信息失败；`36009002` 请求过于频繁。

## 2. 橱窗/直播袋商品

上游路径：`affiliate_creator/202405/showcases/products`；精确 `toolName`：`tiktokVideo/developerProxy`。

| 业务参数 | 必填 | 类型 | 默认/范围 | 说明 |
|---|---|---|---|---|
| openId | 是 | string | 来源未说明 | 已授权 creator open_id；网关据此解析授权上下文 |
| page_size | 是 | int | 1~20 | 每页返回数 |
| page_token | 否 | string | 来源未说明 | 上一页游标 |
| origin | 是 | string | `SHOWCASE` | `SHOWCASE`=橱窗，`LIVE`=直播袋 |

```json
{"toolName":"tiktokVideo/developerProxy","arguments":{"openId":"<creator_open_id>","path":"affiliate_creator/202405/showcases/products","method":"GET","region":"global","queryString":"page_size=20&origin=SHOWCASE"}}
```

### TikTok body 响应

| 响应字段路径 | 类型 | 说明 |
|---|---|---|
| code | int | 业务状态码 |
| message | string | 业务消息 |
| request_id | string | 请求日志 ID |
| data | object | 商品列表与分页信息；内部字段来源未说明 |

错误码：`18001405` 达人账号无选品区域；`36009003` 内部错误。分页和每次状态/列表查询均为新计费调用，未经用户要求不继续。

网关层：`1002` 参数校验失败；`1003` 上游异常；`1005` path 不在白名单。报告原错误，不自动重试。

## Feedback API（不迁移到 MCP）

用户明确反馈时可独立 `POST https://skill-api.linkfox.com/api/v1/public/feedback`，字段为 `skillName`（`linkfox-tiktok-video-products`）、`sentiment`、`category` 和 `content`。它不使用 `proxy_call`；失败不影响商品查询且不自动重试。

## 响应字段来源

代理包络与两种 TikTok 响应仅据 `skills/linkfox-tiktok-video-products/references/api.md` 的 `developerProxy 出参` 和两节 `上游响应` 表恢复。来源未给 `data` 子字段，列为未说明而未补猜。
