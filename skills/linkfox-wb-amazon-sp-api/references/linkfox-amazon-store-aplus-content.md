# Reference archive: linkfox-amazon-store-aplus-content

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
    "path": "aplus/2020-11-01/contentDocuments",
    "method": "GET",
    "queryString": "<按本 reference 的参数规则编码；无查询参数时省略>"
  }
}
```

`toolName` 必须精确匹配并区分大小写。WorkBuddy 自动注入 Authorization；`arguments` 中不得加入网关 `headers`、API Key、Amazon access/refresh token、JWT、手机号或其他凭证。MCP/`proxy_call` 缺失时停止，禁止 curl、`urllib`、`requests`、`httpx` 或本地脚本回退。同一任务内相同 `toolName + arguments` 不重复调用；失败、空结果或不理想时不自动重试。先检查 MCP/schema/`isError`，再读取 structured content 或仅解析一次 text JSON，随后检查下游 `errcode`/`code`、`errmsg`/`msg`、`httpStatus`，最后按响应字段读取结果。

## 来源响应字段表

来源：`skills/linkfox-amazon-store-aplus-content/references/api.md`。仅转录来源响应章节明确给出的字段或响应 JSON；未说明属性不作推断。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `errcode` | number | 来源响应契约字段；来源未提供的必填、可空、枚举或格式属性不补猜。 |
| `httpStatus` | number | 来源响应契约字段；来源未提供的必填、可空、枚举或格式属性不补猜。 |
| `body` | string | 来源响应契约字段；来源未提供的必填、可空、枚举或格式属性不补猜。 |


---
name: linkfox-amazon-store-aplus-content
description: 亚马逊店铺 A+ Content（增强品牌内容）管理。用于查询、创建和更新 A+ 内容文档，关联或解除 ASIN，校验关联关系，查询发布记录，提交审核以及暂停展示等品牌详情页运营场景。用户提到亚马逊 A+ 页面、A+ Content、增强品牌内容、EBC、图文详情、A+ 审核、A+ 发布、ASIN 关联、contentReferenceKey、contentPublishRecords 时触发。即使未明确提及 A+ API，只要希望管理亚马逊商品详情页中的品牌图文模块，也应触发此技能。
---

# Amazon 店铺 A+ Content Management


| 操作 | 官方参考 |
|------|----------|
| 搜索文档列表 | [searchContentDocuments](https://developer-docs.amazon.com/sp-api/reference/searchcontentdocuments) |
| 新建文档 | [createContentDocument](https://developer-docs.amazon.com/sp-api/reference/createcontentdocument) |
| 获取文档（内容/元数据） | [getContentDocument](https://developer-docs.amazon.com/sp-api/reference/getcontentdocument) |
| 更新文档 | [updateContentDocument](https://developer-docs.amazon.com/sp-api/reference/updatecontentdocument) |
| 列出 ASIN 关联 | [listContentDocumentAsinRelations](https://developer-docs.amazon.com/sp-api/reference/listcontentdocumentasinrelations) |
| 替换 ASIN 关联 | [postContentDocumentAsinRelations](https://developer-docs.amazon.com/sp-api/reference/postcontentdocumentasinrelations) |
| 校验文档与 ASIN | [validateContentDocumentAsinRelations](https://developer-docs.amazon.com/sp-api/reference/validatecontentdocumentasinrelations) |
| 按 ASIN 查发布记录 | [searchContentPublishRecords](https://developer-docs.amazon.com/sp-api/reference/searchcontentpublishrecords) |
| 提交审核/发布 | [postContentDocumentApprovalSubmission](https://developer-docs.amazon.com/sp-api/reference/postcontentdocumentapprovalsubmission) |
| 暂停前台展示 | [postContentDocumentSuspendSubmission](https://developer-docs.amazon.com/sp-api/reference/postcontentdocumentsuspendsubmission) |

---

## 调用方式

仅按本文开头的 MCP 契约调用；预签名上传/下载例外仅使用本 skill 保留的对应本地 helper。


## 认证和积分问题

按 `references/onboarding.md` 分层处理 MCP 401、下游 401/402、403 和其他业务错误。


## Prerequisites（必须先读）

本 skill **依赖** **`linkfox-amazon-store-auth`**。

2. **不要**在本 skill 内绕过依赖实现授权或令牌逻辑。

---

## Current Capabilities

| 能力 | Path 要点 | 脚本 |
|------|-----------|------|
| 搜索 A+ 文档 | `aplus/2020-11-01/contentDocuments` + `marketplaceId` | `search_content_documents` 操作 |
| 创建 A+ 文档 | 同上 **POST** + body `contentDocument` | `create_content_document` 操作 |
| 获取单篇文档 | `.../contentDocuments/{contentReferenceKey}` + `includedDataSet`（必填，至少 1 项） | `get_content_document` 操作 |
| 更新文档 | 同上 **POST** + body | `update_content_document` 操作 |
| 列出关联 ASIN | `.../contentDocuments/{key}/asins` | `list_content_document_asin_relations` 操作 |
| 全量替换关联 ASIN | `.../asins` **POST** + body `asinSet` | `post_content_document_asin_relations` 操作 |
| 校验与 ASIN 的可用性 | `.../contentAsinValidations` **POST** | `validate_content_document_asin_relations` 操作 |
| 发布记录（按 ASIN） | `.../contentPublishRecords` + `asin` | `search_content_publish_records` 操作 |
| 提交审核 | `.../approvalSubmissions` **POST** | `post_content_document_approval_submission` 操作 |
| 暂停展示 | `.../suspendSubmissions` **POST** | `post_content_document_suspend_submission` 操作 |

**注意**：`postContentDocumentAsinRelations` 为 **全量替换** `asinSet`；从集合中移除 ASIN 会导致该 ASIN 上内容被 **suspend**（以 Amazon 行为为准）。详见 **`references/api.md`**。

---

## Quick Parameters

### 通用

| 字段 | 必填 | 说明 |
|------|------|------|
| sellerId | 是 | 已授权 Seller ID（与 `storeTokens` 一致） |
| region | 是 | `NA` / `EU` / `FE` |
| marketplaceId **或** marketplaceIds | 是 | 目标站点；数组时脚本仅取 **第一个** |

### contentReferenceKey

多数操作需要 **`contentReferenceKey`**（来自 `searchContentDocuments` 等）。官方说明该 key **非永久链接**、未来可能变化。

### getContentDocument

| 字段 | 必填 | 说明 |
|------|------|------|
| includedDataSet | 是 | 至少一项；**`CONTENTS`**、**`METADATA`**（可并存） |

### searchContentPublishRecords

| 字段 | 必填 | 说明 |
|------|------|------|
| asin | 是 | 长度 ≥ 10 |

---

## Scripts

- **`search_content_documents` 操作**
- **`create_content_document` 操作**
- **`get_content_document` 操作**
- **`update_content_document` 操作**
- **`list_content_document_asin_relations` 操作**
- **`post_content_document_asin_relations` 操作**
- **`validate_content_document_asin_relations` 操作**
- **`search_content_publish_records` 操作**
- **`post_content_document_approval_submission` 操作**
- **`post_content_document_suspend_submission` 操作**
- **`amazon_store_aplus_content__check_auth_dependency` 操作**

示例：



---

## Display Rules

1. 先展示网关 **`errcode` / `httpStatus`**；成功后再解析 **`developerProxy.body`** 或各脚本附带的 **`*Response`** 字段。
2. 说明 **`contentReferenceKey`** 与前台「A+ ID」不一定一致。
3. 写操作（创建/更新/关联/校验/提交/暂停）前确认用户意图；**替换 ASIN** 与 **暂停展示** 影响线上详情页。

---

## Important Limitations

- **应用权限**：Seller Central 应用须具备 A+ Content 相关 **角色/权限**；否则 **403**。
- **白名单**：`aplus/2020-11-01/` 须在网关 developerProxy 放行；**1005** 需运维配置。
- **`contentDocument`** 结构复杂，须符合 **Amazon 官方模型**；本 skill 只做透传，不内置模板校验。
- **marketplaceId**：A+ 接口 Query 使用单数 **`marketplaceId`**（与 Listings 的 `marketplaceIds` 不同）。

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

**Feedback：** 见 `references/api.md`，`skillName`：`linkfox-amazon-store-aplus-content`。

---
*更多跨境 skill：[LinkFox Skills](https://skill.linkfox.com/)*

## Archived reference: api.md

# Amazon 店铺 A+ Content Management API 参考（v2020-11-01）


> 官方参考：[searchContentDocuments](https://developer-docs.amazon.com/sp-api/reference/searchcontentdocuments) · [createContentDocument](https://developer-docs.amazon.com/sp-api/reference/createcontentdocument) · [getContentDocument](https://developer-docs.amazon.com/sp-api/reference/getcontentdocument) · [updateContentDocument](https://developer-docs.amazon.com/sp-api/reference/updatecontentdocument) · [listContentDocumentAsinRelations](https://developer-docs.amazon.com/sp-api/reference/listcontentdocumentasinrelations) · [postContentDocumentAsinRelations](https://developer-docs.amazon.com/sp-api/reference/postcontentdocumentasinrelations) · [validateContentDocumentAsinRelations](https://developer-docs.amazon.com/sp-api/reference/validatecontentdocumentasinrelations) · [searchContentPublishRecords](https://developer-docs.amazon.com/sp-api/reference/searchcontentpublishrecords) · [postContentDocumentApprovalSubmission](https://developer-docs.amazon.com/sp-api/reference/postcontentdocumentapprovalsubmission) · [postContentDocumentSuspendSubmission](https://developer-docs.amazon.com/sp-api/reference/postcontentdocumentsuspendsubmission)

> ⚠️ **依赖**：需已安装 **`linkfox-amazon-store-auth`** 并完成店铺授权。

---

## 调用规范

| 项 | 说明 |
|----|------|
| **SP-API 转发** | `proxy_call` 的 `spApi/developerProxy` |

---

## `proxy_call` 的 `spApi/developerProxy`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| region | string | 是 | `NA` / `EU` / `FE` |
| path | string | 是 | **不含**主机名；本 API 统一前缀 **`aplus/2020-11-01/...`**（见各节） |
| method | string | 是 | **`GET`** 或 **`POST`**（A+ 的创建/更新/校验/关联/提交均为 **POST**） |
| queryString | string | 视操作 | **无 `?` 前缀**；Query 键名与官方一致（注意单数 **`marketplaceId`**） |
| body | string | 视操作 | **POST** 且带 JSON body 时，为 JSON 字符串；**GET** 不传 |
| contentType | string | 视操作 | 有 body 时建议 **`application/json`** |

**网关响应**（与其它店铺 skill 一致）：解析 **`errcode`**、**`httpStatus`**，再将 **`body`** 字符串 `JSON.parse`。

### 白名单

`path` 须在网关 **`sp-api.developer-proxy.allowed-path-prefixes`** 内。若 **`errcode=1005`**，需运维放行前缀（常见）：**`aplus/2020-11-01/`**。

### 速率（文档默认值）

各操作文档默认多为 **10 req/s**，burst **10**；以响应头 `x-amzn-RateLimit-Limit` 及账号实际配额为准。

### 错误码

- **401**：HTTP 401 或 authorized error：按 SKILL.md 的 **## 解决认证和积分问题** 处理。
- **402**：HTTP 402：按 SKILL.md 的 **## 解决认证和积分问题** 处理。

---

## 路径与 Query 总览

| 操作 | Method | `developerProxy.path` 模板 |
|------|--------|---------------------------|
| searchContentDocuments | GET | `aplus/2020-11-01/contentDocuments` |
| createContentDocument | POST | `aplus/2020-11-01/contentDocuments` |
| getContentDocument | GET | `aplus/2020-11-01/contentDocuments/{contentReferenceKey}` |
| updateContentDocument | POST | `aplus/2020-11-01/contentDocuments/{contentReferenceKey}` |
| listContentDocumentAsinRelations | GET | `aplus/2020-11-01/contentDocuments/{contentReferenceKey}/asins` |
| postContentDocumentAsinRelations | POST | `aplus/2020-11-01/contentDocuments/{contentReferenceKey}/asins` |
| validateContentDocumentAsinRelations | POST | `aplus/2020-11-01/contentAsinValidations` |
| searchContentPublishRecords | GET | `aplus/2020-11-01/contentPublishRecords` |
| postContentDocumentApprovalSubmission | POST | `aplus/2020-11-01/contentDocuments/{contentReferenceKey}/approvalSubmissions` |
| postContentDocumentSuspendSubmission | POST | `aplus/2020-11-01/contentDocuments/{contentReferenceKey}/suspendSubmissions` |

**Path 编码**：`contentReferenceKey` 等路径段须 **百分号编码**（脚本已处理）。

---

## searchContentDocuments（GET）

| Query | 必填 | 说明 |
|-------|------|------|
| marketplaceId | 是 | 目标站点 id |
| pageToken | 否 | 分页 |

返回文档列表（**元数据**为主）；完整内容需 **`getContentDocument`**。

---

## createContentDocument（POST）

| Query | 必填 | 说明 |
|-------|------|------|
| marketplaceId | 是 | 目标站点 id |

| Body JSON | 必填 | 说明 |
|-----------|------|------|
| contentDocument | 是 | A+ 文档对象（结构以 Amazon 模型为准） |

---

## getContentDocument（GET）

| Query | 必填 | 说明 |
|-------|------|------|
| marketplaceId | 是 | 目标站点 id |
| includedDataSet | **是**（≥1） | 可重复键；取值：**`CONTENTS`**、**`METADATA`** |

---

## updateContentDocument（POST）

| Query | 必填 | 说明 |
|-------|------|------|
| marketplaceId | 是 | 目标站点 id |

| Body JSON | 必填 | 说明 |
|-----------|------|------|
| contentDocument | 是 | 更新后的 A+ 文档 |

---

## listContentDocumentAsinRelations（GET）

| Query | 必填 | 说明 |
|-------|------|------|
| marketplaceId | 是 | 目标站点 id |
| includedDataSet | 否 | 可选 **`METADATA`**；不传则通常仅返回关联 ASIN |
| asinSet | 否 | 可重复；筛选指定 ASIN |
| pageToken | 否 | 分页 |

---

## postContentDocumentAsinRelations（POST）

| Query | 必填 | 说明 |
|-------|------|------|
| marketplaceId | 是 | 目标站点 id |

| Body JSON | 必填 | 说明 |
|-----------|------|------|
| asinSet | 是 | **替换**该文档关联的全部 ASIN（官方语义为全量替换；移除 ASIN 会 suspend 该 ASIN 上的内容）。可为 **字符串数组**，或与官方 schema 一致的对象数组 |

---

## validateContentDocumentAsinRelations（POST）

| Query | 必填 | 说明 |
|-------|------|------|
| marketplaceId | 是 | 目标站点 id |
| asinSet | 否 | 可重复；待校验 ASIN 集合 |

| Body JSON | 必填 | 说明 |
|-----------|------|------|
| contentDocument | 是 | 待校验的 A+ 文档 |

---

## searchContentPublishRecords（GET）

| Query | 必填 | 说明 |
|-------|------|------|
| marketplaceId | 是 | 目标站点 id |
| asin | 是 | ASIN，文档要求 **length ≥ 10** |
| pageToken | 否 | 分页 |

---

## postContentDocumentApprovalSubmission（POST）

| Query | 必填 | 说明 |
|-------|------|------|
| marketplaceId | 是 | 目标站点 id |

**Body**：官方无必填 body；本 reference 的请求构造 **不传** `developerProxy.body`。

---

## postContentDocumentSuspendSubmission（POST）

| Query | 必填 | 说明 |
|-------|------|------|
| marketplaceId | 是 | 目标站点 id |

请求暂停详情页可见 A+；**不删除**文档与 ASIN 关联。脚本 **不传** body。

---

## 脚本入参约定（JSON 一行）

各脚本均需 **`sellerId`**、**`region`**；站点 id 使用 **`marketplaceId`** 或 **`marketplaceIds`**（数组时仅取第一个，与其它店铺 skill 一致）。

| 脚本 | 额外必填 | 可选 |
|------|----------|------|
| `search_content_documents` 操作 | — | `pageToken` |
| `create_content_document` 操作 | `contentDocument` | — |
| `get_content_document` 操作 | `contentReferenceKey`, `includedDataSet` | — |
| `update_content_document` 操作 | `contentReferenceKey`, `contentDocument` | — |
| `list_content_document_asin_relations` 操作 | `contentReferenceKey` | `includedDataSet`, `asinSet`, `pageToken` |
| `post_content_document_asin_relations` 操作 | `contentReferenceKey`, `asinSet` | — |
| `validate_content_document_asin_relations` 操作 | `contentDocument` | `asinSet`（写入 Query） |
| `search_content_publish_records` 操作 | `asin` | `pageToken` |
| `post_content_document_approval_submission` 操作 | `contentReferenceKey` | — |
| `post_content_document_suspend_submission` 操作 | `contentReferenceKey` | — |

全局可选：**`skipDepCheck`: true**（跳过本地依赖探测，不建议常规使用）。

---

## MCP 示例见本文开头（网关层示意）



---

## Feedback

与其它 LinkFox 店铺 skill 相同：若仓库或产品内提供 Feedback API，上报时 **`skillName`** 请使用 **`linkfox-amazon-store-aplus-content`**。

## Archived reference: onboarding.md

认证和积分问题统一按本 skill 的 `references/onboarding.md` 处理。
