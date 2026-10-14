# Reference archive: linkfox-amazon-store-uploads

本文件归档该子能力的执行说明、API 契约、参数约束、错误处理和工作流；按需阅读相关章节。

## Capability instructions


## MCP 调用

| 项 | 值 |
|---|---|
| MCP server | `LinkFox` |
| 唯一工具 | `proxy_call` |
| `toolName` | `spApi/developerProxy` |
| `arguments` | 直接使用本 reference 对应的网关请求对象 |

```json
{
  "toolName": "spApi/developerProxy",
  "arguments": {
    "sellerId": "A1234567890",
    "region": "NA",
    "path": "uploads/2020-11-01/uploadDestinations/{resource}",
    "method": "POST",
    "body": "<按本 reference 构造的 JSON 字符串；无请求体时省略>"
  }
}
```

`toolName` 必须精确匹配并区分大小写。WorkBuddy 自动注入 Authorization；`arguments` 中不得加入网关 `headers`、API Key、Amazon access/refresh token、JWT、手机号或其他凭证。MCP/`proxy_call` 缺失时停止，禁止 curl、`urllib`、`requests`、`httpx` 或本地脚本回退。同一任务内相同 `toolName + arguments` 不重复调用；失败、空结果或不理想时不自动重试。先检查 MCP/schema/`isError`，再读取 structured content 或仅解析一次 text JSON，随后检查下游 `errcode`/`code`、`errmsg`/`msg`、`httpStatus`，最后按响应字段读取结果。

## 来源响应字段表

来源：`skills/linkfox-amazon-store-uploads/references/api.md`。仅转录来源响应章节明确给出的字段或响应 JSON；未说明属性不作推断。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `uploadDestination` | 来源未说明 | 来源响应契约字段；来源未提供的必填、可空、枚举或格式属性不补猜。 |
| `uploadDestinationId` | 来源未说明 | 来源响应契约字段；来源未提供的必填、可空、枚举或格式属性不补猜。 |
| `url` | 来源未说明 | 来源响应契约字段；来源未提供的必填、可空、枚举或格式属性不补猜。 |
| `headers` | 来源未说明 | 来源响应契约字段；来源未提供的必填、可空、枚举或格式属性不补猜。 |


---
name: linkfox-amazon-store-uploads
description: 亚马逊 SP-API 通用文件上传。用于为 A+ Content、Messaging 等业务创建 upload destination，计算 contentMD5，并将图片或附件上传到返回的预签名地址。用户提到亚马逊文件上传、A+ 图片上传、Messaging 附件、createUploadDestinationForResource、upload destination、contentMD5、预签名上传、Uploads API、SP-API 上传文件时触发。即使未明确说“Uploads API”，只要其他亚马逊 SP-API 操作需要先获得可引用的上传资源地址，也应触发此技能；Feed 文档上传使用 linkfox-amazon-store-feeds 的专用流程。
---

# Amazon 店铺 Uploads（文件上传）

本 skill 专用于 **向 Amazon 申请上传目的地并上传文件**，与 **`linkfox-amazon-store-auth`** 同系列：依赖 **`linkfox-amazon-store-auth`** 选店（`sellerId`+`region`）；通过 `proxy_call` 的精确 `toolName` `spApi/developerProxy` 传入 `sellerId`+`region` 调用 **createUploadDestinationForResource**，最后用 **`scripts/upload_to_destination.py`** 对返回的 URL 执行 **PUT**（不经网关）。

> 这是 **Uploads API**，不是 Orders 订单接口。订单见 **`linkfox-amazon-store-orders`**；批量 Feed 文件见 **`linkfox-amazon-store-feeds`**。

## 调用方式

仅按本文开头的 MCP 契约调用；预签名上传/下载例外仅使用本 skill 保留的对应本地 helper。


## 认证和积分问题

按 `references/onboarding.md` 分层处理 MCP 401、下游 401/402、403 和其他业务错误。


## 官方参考

[createUploadDestinationForResource](https://developer-docs.amazon.com/sp-api/reference/createuploaddestinationforresource) · [Create an upload destination](https://developer-docs.amazon.com/sp-api/docs/create-an-upload-destination)

---

## Prerequisites

1. 依赖 **`linkfox-amazon-store-auth`**。
2. **`resource`** 须与下游 API 文档一致（例如 A+：`aplus/2020-11-01/contentDocuments`；Messaging 为对应 messages 资源路径）。
3. **`contentMD5`** 为待上传文件内容的 **Base64 MD5 摘要**；传 **`filePath`** / **`content`** 时脚本可自动计算。

---

## 工作流

```text
create_upload_destination_for_resource  →  uploadDestination { uploadDestinationId, url, headers }
upload_to_destination (PUT url + headers)  →  在 A+/Messaging 等 API 中引用 uploadDestinationId
```

---

## Scripts

| 脚本 | 说明 |
|------|------|
| `create_upload_destination_for_resource` 操作 | POST `uploads/2020-11-01/uploadDestinations/{resource}` |
| `scripts/upload_to_destination.py` | PUT 到返回的 `url`（带 `headers`） |
| `_spapi_uploads_common` 操作 | 内部公共模块 |

---

## 示例



---

## Display Rules

1. 成功创建目的地常为 **HTTP 201**；先看 **`developerProxy`**，再看 **`uploadDestination`**。
2. **`resource`** 不要带前导 `/`；path 中会对 `/` 做编码。
3. 网关需放行 **`uploads/2020-11-01/`** 前缀。

## Amazon SP-API 接口保护与重试指引

同一店铺连续收到 Amazon SP-API 的 400、403、404 或 429 时，网关会返回 450、453、454 或 459 并短暂冷却。这些自定义状态码不是 Amazon 原生状态，也不表示封号；目的是避免持续异常或高频调用扩大店铺风险。

| 状态与 message | 范围 | 触发与冷却 | 处理 |
|---|---|---|---|
| `450`：`400，请求异常，请优化您的参数` | 店铺+接口 | 60 秒内超过 3 次：5 分钟；10 分钟内超过 4 次：20 分钟 | 停止原参数重试，检查必填字段、marketplace、ID、日期和请求体 |
| `453`：`403，店铺未授权，请先授权` | 店铺全部接口 | 60 秒内超过 2 次：5 分钟；10 分钟内超过 4 次：30 分钟 | 停止该店铺调用，检查授权、权限、店铺归属和区域 |
| `454`：`404，资源不存在，请优化您的参数` | 店铺+接口 | 60 秒内超过 3 次：5 分钟；10 分钟内超过 4 次：30 分钟 | 确认资源 ID、所属店铺/站点、资源状态和接口路径 |
| `459`：`429限流中，请降低频率` | 店铺+接口 | 首次：15 秒；2 分钟内超过 2 次：30 秒；3 分钟内超过 4 次：2 分钟 | 降低并发、分页和轮询频率并逐级退避 |

- 立即停止自动或并发重试，不得通过换脚本或重复创建任务绕过保护；优先遵循 `retryAfter`、`blockedUntil`，没有时按表中时长说明。
- 450/453/454 必须先修正参数、授权或资源标识，冷却后最多谨慎重试一次；再次触发则停止调用。453 期间停止该店铺全部 SP-API。
- 保留已有 `reportId`、`feedId` 等任务 ID；写操作结果不确定时先查询状态，不直接重放。
- 向用户先说明店铺保护，再给原因、处理和等待时间。可回复：“为保护您的亚马逊店铺安全，检测到 Amazon SP-API 连续返回{原因}，当前已进入短暂保护。请先{处理动作}，预计{等待时间}后再试；这不代表封号，也不是套餐或积分限制。”不要只说“LinkFox 限流”或“服务器繁忙”。

## 积分消耗规则

不消耗积分。

**Feedback：** `skillName`：`linkfox-amazon-store-uploads`。

---
*更多跨境 skill：[LinkFox Skills](https://skill.linkfox.com/)*

## Archived reference: api.md

# linkfox-amazon-store-uploads — API 参考

Uploads **v2020-11-01**，用于在调用 A+ Content、Messaging 等 API 之前**上传二进制文件**。

---

## 1. createUploadDestinationForResource

| 项 | 值 |
|----|-----|
| method | POST |
| path | `uploads/2020-11-01/uploadDestinations/{resource}` |
| 脚本 | `create_upload_destination_for_resource` 操作 |

`{resource}` 为下游 API 的资源路径（URL 编码），例如：

- `aplus/2020-11-01/contentDocuments`
- Messaging：`messaging/v1/orders/{amazonOrderId}/messages/...`（以官方为准）

### Query（写入 `queryString`）

| 参数 | 必填 | 说明 |
|------|------|------|
| marketplaceIds | 是 | 单站点 ID（脚本用 `marketplaceId` 或 `marketplaceIds[0]`） |
| contentMD5 | 是 | 文件内容的 Base64 MD5；或由 `filePath`/`content` 自动计算 |
| contentType | 否 | 如 `image/jpeg` |

### 入参 JSON（脚本）

| 字段 | 必填 |
|------|------|
| sellerId, region | 是 |
| resource | 是 |
| marketplaceId | 是 |
| contentMD5 或 filePath/content/contentBase64 | 是（二选一组合） |
| contentType | 建议 |

### 响应解析

字段 **`uploadDestination`**，通常含：

- `uploadDestinationId` — 后续业务 API 引用
- `url` — PUT 上传地址
- `headers` — 上传时必须附带的 HTTP 头

---

## 2. 上传文件（非 SP-API 代理）

| 脚本 | `scripts/upload_to_destination.py` |
|------|---------------------------|
| method | PUT |
| URL | `uploadDestination.url` |
| headers | `uploadDestination.headers` 全文带上 |

| 字段 | 必填 |
|------|------|
| uploadUrl 或 uploadDestination | 是 |
| headers（若未包在 uploadDestination 内） | 是 |
| filePath / content / contentBase64 | 是 |

**注意**：PUT 使用的字节须与申请 `contentMD5` 时一致。

---

## 3. contentMD5 计算

与 Amazon 要求一致：对文件字节做 MD5，再 **Base64** 编码摘要：

```python
base64.b64encode(hashlib.md5(data).digest()).decode("ascii")
```

---

## 4. 常见 resource 示例

| 场景 | resource 示例 |
|------|----------------|
| A+ 内容文档 | `aplus/2020-11-01/contentDocuments` |
| Messaging 附件 | 见 [Messaging API](https://developer-docs.amazon.com/sp-api/docs/messaging-api-v1-reference) 各 message 操作的 resource 说明 |

---

## 5. 错误与白名单

- **403**：Uploads 或下游角色未授权。
- **1005**：网关需放行 `uploads/2020-11-01/`。
- **429**：默认约 0.1 req/s（以官方为准）。

---

## 6. Feedback

`skillName`: **`linkfox-amazon-store-uploads`**

## Archived reference: onboarding.md

认证和积分问题统一按本 skill 的 `references/onboarding.md` 处理。
