---
name: linkfox-amazon-store-aplus-content
description: 亚马逊店铺 A+ Content（增强图文页）管理（与 linkfox-amazon-store-auth / linkfox-amazon-store-listings 同系列），经 LinkFox /spApi/developerProxy 调用 SP-API A+ Content Management v2020-11-01：searchContentDocuments、createContentDocument、getContentDocument、updateContentDocument、list/post ContentDocument ASIN 关联、validateContentDocumentAsinRelations、searchContentPublishRecords、提交审核 postContentDocumentApprovalSubmission、暂停展示 postContentDocumentSuspendSubmission。当用户提到 A+ 页面、A+ Content、增强品牌内容、EBC、图文详情、searchContentDocuments、getContentDocument、contentReferenceKey、A+ 审核、A+ 发布记录、contentPublishRecords 时触发。
---

# Amazon 店铺 A+ Content Management

本 skill 与 **`linkfox-amazon-store-auth`**、**`linkfox-amazon-store-listings`** 等同属 **Amazon Store** 系列：使用 **`POST /spApi/storeTokens`** 取 `accessToken`，再经 **`POST /spApi/developerProxy`** 转发上游 **GET** 或 **POST**。

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

## Prerequisites（必须先读）

本 skill **依赖** **`linkfox-amazon-store-auth`**。

1. 运行 `python scripts/check_auth_dependency.py`；若 exit code **42** 且 stderr 含 `DEPENDENCY_MISSING:`，请先安装 **`linkfox-amazon-store-auth`**。
2. **不要**在本 skill 内绕过依赖实现授权或令牌逻辑。

---

## Current Capabilities

| 能力 | Path 要点 | 脚本 |
|------|-----------|------|
| 搜索 A+ 文档 | `aplus/2020-11-01/contentDocuments` + `marketplaceId` | `scripts/search_content_documents.py` |
| 创建 A+ 文档 | 同上 **POST** + body `contentDocument` | `scripts/create_content_document.py` |
| 获取单篇文档 | `.../contentDocuments/{contentReferenceKey}` + `includedDataSet`（必填，至少 1 项） | `scripts/get_content_document.py` |
| 更新文档 | 同上 **POST** + body | `scripts/update_content_document.py` |
| 列出关联 ASIN | `.../contentDocuments/{key}/asins` | `scripts/list_content_document_asin_relations.py` |
| 全量替换关联 ASIN | `.../asins` **POST** + body `asinSet` | `scripts/post_content_document_asin_relations.py` |
| 校验与 ASIN 的可用性 | `.../contentAsinValidations` **POST** | `scripts/validate_content_document_asin_relations.py` |
| 发布记录（按 ASIN） | `.../contentPublishRecords` + `asin` | `scripts/search_content_publish_records.py` |
| 提交审核 | `.../approvalSubmissions` **POST** | `scripts/post_content_document_approval_submission.py` |
| 暂停展示 | `.../suspendSubmissions` **POST** | `scripts/post_content_document_suspend_submission.py` |

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

- **`scripts/search_content_documents.py`**
- **`scripts/create_content_document.py`**
- **`scripts/get_content_document.py`**
- **`scripts/update_content_document.py`**
- **`scripts/list_content_document_asin_relations.py`**
- **`scripts/post_content_document_asin_relations.py`**
- **`scripts/validate_content_document_asin_relations.py`**
- **`scripts/search_content_publish_records.py`**
- **`scripts/post_content_document_approval_submission.py`**
- **`scripts/post_content_document_suspend_submission.py`**
- **`scripts/check_auth_dependency.py`**

示例：

```bash
export LINKFOXAGENT_API_KEY="<your-key>"

python scripts/search_content_documents.py '{"sellerId":"A1...","region":"NA","marketplaceId":"ATVPDKIKX0DER"}'

python scripts/get_content_document.py '{"sellerId":"A1...","region":"NA","marketplaceId":"ATVPDKIKX0DER","contentReferenceKey":"YOUR_KEY","includedDataSet":["CONTENTS","METADATA"]}'

python scripts/post_content_document_asin_relations.py '{"sellerId":"A1...","region":"NA","marketplaceId":"ATVPDKIKX0DER","contentReferenceKey":"YOUR_KEY","asinSet":["B0XXXXXXXXXX"]}'

python scripts/search_content_publish_records.py '{"sellerId":"A1...","region":"NA","marketplaceId":"ATVPDKIKX0DER","asin":"B0XXXXXXXXXX"}'

python scripts/post_content_document_approval_submission.py '{"sellerId":"A1...","region":"NA","marketplaceId":"ATVPDKIKX0DER","contentReferenceKey":"YOUR_KEY"}'
```

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

**Feedback：** 见 `references/api.md`，`skillName`：`linkfox-amazon-store-aplus-content`。

---
*更多跨境 skill：[LinkFox Skills](https://skill.linkfox.com/)*
