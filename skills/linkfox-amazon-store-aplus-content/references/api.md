# Amazon 店铺 A+ Content Management API 参考（v2020-11-01）

本文档描述通过 **LinkFox 店铺网关** 调用 Selling Partner API **A+ Content Management v2020-11-01**：`searchContentDocuments`、`createContentDocument`、`getContentDocument`、`updateContentDocument`、`listContentDocumentAsinRelations`、`postContentDocumentAsinRelations`、`validateContentDocumentAsinRelations`、`searchContentPublishRecords`、`postContentDocumentApprovalSubmission`、`postContentDocumentSuspendSubmission`。流程与 **`linkfox-amazon-store-report`** / **`linkfox-amazon-store-listings`** 一致：先 **`POST /spApi/storeTokens`**，再 **`POST /spApi/developerProxy`** 转发上游 **GET** 或 **POST**。

> 官方参考：[searchContentDocuments](https://developer-docs.amazon.com/sp-api/reference/searchcontentdocuments) · [createContentDocument](https://developer-docs.amazon.com/sp-api/reference/createcontentdocument) · [getContentDocument](https://developer-docs.amazon.com/sp-api/reference/getcontentdocument) · [updateContentDocument](https://developer-docs.amazon.com/sp-api/reference/updatecontentdocument) · [listContentDocumentAsinRelations](https://developer-docs.amazon.com/sp-api/reference/listcontentdocumentasinrelations) · [postContentDocumentAsinRelations](https://developer-docs.amazon.com/sp-api/reference/postcontentdocumentasinrelations) · [validateContentDocumentAsinRelations](https://developer-docs.amazon.com/sp-api/reference/validatecontentdocumentasinrelations) · [searchContentPublishRecords](https://developer-docs.amazon.com/sp-api/reference/searchcontentpublishrecords) · [postContentDocumentApprovalSubmission](https://developer-docs.amazon.com/sp-api/reference/postcontentdocumentapprovalsubmission) · [postContentDocumentSuspendSubmission](https://developer-docs.amazon.com/sp-api/reference/postcontentdocumentsuspendsubmission)

> ⚠️ **依赖**：需已安装 **`linkfox-amazon-store-auth`** 并完成店铺授权。

---

## 调用规范

| 项 | 说明 |
|----|------|
| **Base URL** | `${LINKFOX_TOOL_GATEWAY}`（可用 `STORE_API_BASE_URL` 或 `SPAPI_BASE_URL` 覆盖） |
| **网关认证** | Header `Authorization: <api_key>`，环境变量 `LINKFOX_AGENT_API_KEY` 或 `LINKFOXAGENT_API_KEY` |
| **店铺令牌** | `POST /spApi/storeTokens`，Body：`{"sellerId":"...","region":"NA\|EU\|FE"}` → `accessToken` |
| **SP-API 转发** | `POST /spApi/developerProxy` |

---

## `POST /spApi/developerProxy`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| region | string | 是 | `NA` / `EU` / `FE` |
| path | string | 是 | **不含**主机名；本 API 统一前缀 **`aplus/2020-11-01/...`**（见各节） |
| method | string | 是 | **`GET`** 或 **`POST`**（A+ 的创建/更新/校验/关联/提交均为 **POST**） |
| amzAccessToken | string | 是 | `storeTokens` 返回的 `accessToken` |
| queryString | string | 视操作 | **无 `?` 前缀**；Query 键名与官方一致（注意单数 **`marketplaceId`**） |
| body | string | 视操作 | **POST** 且带 JSON body 时，为 JSON 字符串；**GET** 不传 |
| contentType | string | 视操作 | 有 body 时建议 **`application/json`** |

**网关响应**（与其它店铺 skill 一致）：解析 **`errcode`**、**`httpStatus`**，再将 **`body`** 字符串 `JSON.parse`。

### 白名单

`path` 须在网关 **`sp-api.developer-proxy.allowed-path-prefixes`** 内。若 **`errcode=1005`**，需运维放行前缀（常见）：**`aplus/2020-11-01/`**。

### 速率（文档默认值）

各操作文档默认多为 **10 req/s**，burst **10**；以响应头 `x-amzn-RateLimit-Limit` 及账号实际配额为准。

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

**Body**：官方无必填 body；本仓库脚本 **不传** `developerProxy.body`。

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
| `search_content_documents.py` | — | `pageToken` |
| `create_content_document.py` | `contentDocument` | — |
| `get_content_document.py` | `contentReferenceKey`, `includedDataSet` | — |
| `update_content_document.py` | `contentReferenceKey`, `contentDocument` | — |
| `list_content_document_asin_relations.py` | `contentReferenceKey` | `includedDataSet`, `asinSet`, `pageToken` |
| `post_content_document_asin_relations.py` | `contentReferenceKey`, `asinSet` | — |
| `validate_content_document_asin_relations.py` | `contentDocument` | `asinSet`（写入 Query） |
| `search_content_publish_records.py` | `asin` | `pageToken` |
| `post_content_document_approval_submission.py` | `contentReferenceKey` | — |
| `post_content_document_suspend_submission.py` | `contentReferenceKey` | — |

全局可选：**`skipDepCheck`: true**（跳过本地依赖探测，不建议常规使用）。

---

## curl 示例（网关层示意）

```bash
export LINKFOXAGENT_API_KEY="<your-key>"

# 1) 取令牌（示意）
curl -sS -X POST "https://tool-gateway.linkfox.com/spApi/storeTokens" \
  -H "Authorization: $LINKFOXAGENT_API_KEY" -H "Content-Type: application/json" \
  -d '{"sellerId":"A1...","region":"NA"}'

# 2) 转发 searchContentDocuments（将 ACCESS_TOKEN 替换为上一步 accessToken）
curl -sS -X POST "https://tool-gateway.linkfox.com/spApi/developerProxy" \
  -H "Authorization: $LINKFOXAGENT_API_KEY" -H "Content-Type: application/json" \
  -d '{
    "region":"NA",
    "path":"aplus/2020-11-01/contentDocuments",
    "method":"GET",
    "amzAccessToken":"ACCESS_TOKEN",
    "queryString":"marketplaceId=ATVPDKIKX0DER"
  }'
```

---

## Feedback

与其它 LinkFox 店铺 skill 相同：若仓库或产品内提供 Feedback API，上报时 **`skillName`** 请使用 **`linkfox-amazon-store-aplus-content`**。
