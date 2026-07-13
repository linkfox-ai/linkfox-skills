# Amazon 店铺 Listings API 参考（Listings Items / Restrictions / Product Type Definitions）

本文档描述通过 **LinkFox 店铺网关** 调用 Selling Partner API 中与刊登相关的接口：**Listings Items v2021-08-01**（`getListingsItem`、`searchListingsItems`、`patchListingsItem`、`putListingsItem`、`deleteListingsItem`）、**Listings Restrictions v2021-08-01**（`getListingsRestrictions`）、**Product Type Definitions v2020-09-01**（`searchDefinitionsProductTypes`、`getDefinitionsProductType`）。流程与 `linkfox-amazon-store-report` **完全一致**——先取店铺令牌，再经 **`POST /spApi/developerProxy`** 转发上游 HTTP。

> 官方参考：[getListingsItem](https://developer-docs.amazon.com/sp-api/reference/getlistingsitem) · [searchListingsItems](https://developer-docs.amazon.com/sp-api/reference/searchlistingsitems) · [patchListingsItem](https://developer-docs.amazon.com/sp-api/reference/patchlistingsitem) · [putListingsItem](https://developer-docs.amazon.com/sp-api/reference/putlistingsitem) · [deleteListingsItem](https://developer-docs.amazon.com/sp-api/reference/deletelistingsitem) · [getListingsRestrictions](https://developer-docs.amazon.com/sp-api/reference/getlistingsrestrictions) · [searchDefinitionsProductTypes](https://developer-docs.amazon.com/sp-api/reference/searchdefinitionsproducttypes) · [getDefinitionsProductType](https://developer-docs.amazon.com/sp-api/reference/getdefinitionsproducttype)（路径、Query、Body、响应以 Amazon 文档为准）。

> ⚠️ **依赖**：调用前需已安装并完成授权流程 **`linkfox-amazon-store-auth`**（`/spApi/storeTokens` 等），参见本 skill 的 `SKILL.md`。

---

## 调用规范（与 store-report 相同）

| 项 | 说明 |
|----|------|
| **Base URL** | `${LINKFOX_TOOL_GATEWAY}`（默认 `https://tool-gateway.linkfox.com`；可用 `STORE_API_BASE_URL` 或 `SPAPI_BASE_URL` 覆盖） |
| **网关认证** | Header `Authorization: <api_key>`，环境变量 `LINKFOX_AGENT_API_KEY` 或 `LINKFOXAGENT_API_KEY`（如未配置 按 SKILL.md 的 **## 解决认证和积分问题** 处理） |
| **店铺令牌** | `POST /spApi/storeTokens`，Body：`{"sellerId":"...","region":"NA\|EU\|FE"}` → `accessToken` |
| **SP-API 转发** | `POST /spApi/developerProxy`，Body 见下节 |

---

## 通用接口：`POST /spApi/developerProxy`

与 `linkfox-amazon-store-report` 的 `references/api.md` 中 **Developer Proxy** 定义相同。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| region | string | 是 | `NA` / `EU` / `FE`，须与店铺授权区域一致 |
| path | string | 是 | **不含** SP-API 主机名前缀，仅 **资源路径**（见下文 Listings **items** / **restrictions**、**definitions/.../productTypes** 等模板） |
| method | string | 是 | **`GET`**（读操作）、**`PATCH`**、**`PUT`** 或 **`DELETE`**（写操作） |
| amzAccessToken | string | 是 | `/spApi/storeTokens` 返回的 `accessToken` |
| queryString | string | 视操作 | **无 `?` 前缀**。各操作必填/可选 Query 见各节（**put** / **delete** / **getDefinitionsProductType** 的 `marketplaceIds` 等见官方 **length ≤ 1** 说明） |
| body | string | 视操作 | **PATCH / PUT** 时 JSON 字符串。**GET** / **DELETE** 通常不传 |
| contentType | string | 视操作 | **PATCH / PUT** 建议 **`application/json`**。**GET** / **DELETE** 通常省略 |

**网关响应**（与报告 skill 一致）：

```json
{
  "errcode": 200,
  "errmsg": "ok",
  "httpStatus": 200,
  "contentType": "application/json",
  "body": "{... Amazon 返回的 JSON 字符串 ...}"
}
```

解析步骤：**先看 `errcode`**，再 **`httpStatus`**，最后将 **`body`** 做 `JSON.parse`。

### 白名单与错误码

- `path` 必须在后端 **`sp-api.developer-proxy.allowed-path-prefixes`** 白名单内。若 **`errcode=1005`**，需联系后端放行（常见前缀，以运维为准）：
  - **`listings/2021-08-01/items`**：`get` / `patch` / `put` / `delete` 为 `.../items/{sellerId}/{sku}`，`searchListingsItems` 为 `.../items/{sellerId}`；
  - **`listings/2021-08-01/restrictions`**：`getListingsRestrictions`（**无** path 变量，固定 `.../restrictions`）；
  - **`definitions/2020-09-01/productTypes`**：`searchDefinitionsProductTypes` 与 **`getDefinitionsProductType`**（后者 path 含 **`/{productType}`** 段）。
- 网关须允许 **`PATCH`**、**`PUT`**、**`DELETE`**（及已有 **GET**）转发。
- 其它 **`errcode`** / **`httpStatus`** 含义与处置与 `linkfox-amazon-store-report` 的 `references/api.md` 中 **Error Codes** / **Developer Proxy 上游状态码** 表格一致（400 参数、403 令牌/权限、404 无此 SKU 等）。
- HTTP 401 或 authorized error：按 SKILL.md 的 **## 解决认证和积分问题** 处理。
- HTTP 402：按 SKILL.md 的 **## 解决认证和积分问题** 处理。

---

## getListingsItem — 上游语义与网关映射

### HTTP 与方法（Amazon）

- **Method**：`GET`
- **资源路径模板**（写入 `developerProxy.path`）：

```text
listings/2021-08-01/items/{sellerId}/{sku}
```

其中 **`{sellerId}`**、**`{sku}`** 须做 **URL path 分段编码**（例如空格、`/` 等字符）；本仓库脚本使用百分号编码后拼入 `path`。

> 说明：不同区域 SP-API **主机名**不同（na/eu/fe 等），由网关按 `region` + `amzAccessToken` 解析，调用方**只传相对 path** 即可。

### Path 参数（写入 path 的占位段）

| 名称 | 类型 | 必填 | 说明 |
|------|------|------|------|
| sellerId | string | 是 | 卖家标识，与已授权店铺一致（与 `/spApi/storeTokens` 所用 `sellerId` 相同） |
| sku | string | 是 | **卖家自定义 SKU**（Seller SKU），不是 ASIN。须与 Listing 在目标站点下实际存在的 seller SKU 一致 |

### Query 参数（写入 `developerProxy.queryString`，无 `?`）

以下按 Amazon 文档整理；**键名大小写**须与官方一致。

| 参数名 | 类型 | 必填 | 约束 / 说明 |
|--------|------|------|----------------|
| marketplaceIds | string | **是** | 目标 marketplace id。官方 schema 常见为 **单站点**（文档标注 length ≤ 1 时应只传 **一个** id）。多个 id 时本仓库脚本 **仅取第一个** 并打 stderr 警告。示例：`ATVPDKIKX0DER`（美国）。**Query 中写法**：`marketplaceIds=ATVPDKIKX0DER`（单值；若网关要求重复键名以官方为准，一般单站点即可） |
| includedData | string | 否 | 逗号分隔数据集列表，控制响应中包含哪些块。**不传**时上游通常等价于默认 **`summaries`**（以实网为准）。可选值（与官方一致）：`summaries`、`attributes`、`issues`、`offers`、`fulfillmentAvailability`、`procurement`、`relationships`、`productTypes`。示例：`includedData=summaries,attributes` |
| issueLocale | string | 否 | **issues** 等字段的本地化语言。示例：`en_US`、`fr_CA`。未传时通常使用第一个 marketplace 的默认语言；不可用回退行为以 Amazon 为准 |

### 官方默认与速率（摘要）

- **includedData** 默认集：文档为 **`summaries`**（若需结构化属性、报价、库存等，请在 `includedData` 中显式增加对应 token）。
- **Usage plan（文档默认值）**：约 **5 req/s**，burst **10**（以响应头 `x-amzn-RateLimit-Limit` 及账号实际配额为准）。

### 上游成功 / 常见错误（httpStatus）

| httpStatus | 含义（摘要） |
|------------|----------------|
| 200 | 成功，`body` 为 Listing 详情 JSON |
| 400 | Query / Path 非法或无法解析 |
| 403 | 拒绝访问（令牌、签名、权限等） |
| 404 | 指定 `sellerId`+`sku`+`marketplaceIds` 下无该 listing |
| 413 | 请求过大 |
| 415 | 不支持的媒体类型 |
| 429 | 限流 |
| 500 / 503 | 上游异常或维护 |

---

## 脚本参数映射（`scripts/get_listings_item.py`）

| 脚本 JSON 字段 | 映射到 developerProxy |
|----------------|-------------------------|
| sellerId | 用于 `storeTokens`；并编码进 `path` 第一段 |
| region | `region` |
| sku | 编码进 `path` 第二段 |
| marketplaceIds | `array[string]` 或单个 `string` → `queryString.marketplaceIds`（多元素时仅首元素） |
| includedData | 可选，`array` 用逗号拼接 → `queryString.includedData` |
| issueLocale | 可选 → `queryString.issueLocale` |

脚本在 stdout 打印 JSON：含 `developerProxy` 原始包、`resolvedPath`、`queryString`；若 `errcode==200` 且 `httpStatus==200`，额外解析 `listing` 对象（`body` 的 JSON）。

---

## searchListingsItems — 上游语义与网关映射

> 官方：[searchListingsItems](https://developer-docs.amazon.com/sp-api/reference/searchlistingsitems)

### HTTP 与方法

- **Method**：`GET`
- **资源路径**（写入 `developerProxy.path`，仅含 `sellerId`，**无**路径尾段的 SKU）：

```text
listings/2021-08-01/items/{sellerId}
```

`{sellerId}` 须 **URL 编码**（与 getListingsItem 相同约定）。

### Path 参数

| 名称 | 类型 | 必填 | 说明 |
|------|------|------|------|
| sellerId | string | 是 | 卖家标识，与已授权店铺及 `storeTokens` 一致 |

### Query 参数（写入 `queryString`）

| 参数名 | 类型 | 必填 | 约束 / 说明 |
|--------|------|------|-------------|
| marketplaceIds | string | **是** | 文档为 **length ≤ 1** 的 marketplace id 列表（逗号分隔语义）；本仓库脚本与 get 一致：**多传时仅取第一个** 并告警。示例：`ATVPDKIKX0DER` |
| issueLocale | string | 否 | 本地化 issues 等，如 `en_US`、`fr_CA`；未传时行为以 Amazon 为准 |
| includedData | string | 否 | 逗号分隔，默认文档为 **`summaries`**。可选：`summaries`、`attributes`、`issues`、`offers`、`fulfillmentAvailability`、`procurement`、`relationships`、`productTypes` |
| identifiers | string | 条件 | **最多 20 个**商品标识，逗号分隔（脚本接受 JSON 数组，输出为逗号拼接）。**与 `identifiersType` 成对出现**：传了 identifiers 必须带 identifiersType，反之亦然 |
| identifiersType | string | 条件 | 标识类型枚举：`SKU`、`ASIN`、`EAN`、`FNSKU`、`GTIN`、`ISBN`、`JAN`、`MINSAN`、`UPC`（以官方为准） |
| variationParentSku | string | 条件 | 只返回该 **父 SKU** 下的变体子体。**禁止**与 `identifiers` / `packageHierarchySku` 同时使用 |
| packageHierarchySku | string | 条件 | 返回包含或由该 SKU 构成的层级相关 listing。**禁止**与 `identifiers` / `variationParentSku` 同时使用 |
| createdAfter | string | 否 | ISO 8601 **date-time**，筛选创建时间 ≥ 该时刻 |
| createdBefore | string | 否 | ISO 8601，创建时间 ≤ 该时刻 |
| lastUpdatedAfter | string | 否 | ISO 8601，最后更新时间 ≥ 该时刻 |
| lastUpdatedBefore | string | 否 | ISO 8601，最后更新时间 ≤ 该时刻 |
| withIssueSeverity | string | 否 | 逗号分隔；取值：`ERROR`、`WARNING`（仅包含有对应严重度 issue 的刊登） |
| withStatus | string | 否 | 逗号分隔；取值：`BUYABLE`、`DISCOVERABLE`（文档注明 BUYABLE 不适用于 vendor listings） |
| withoutStatus | string | 否 | 逗号分隔；同上枚举，表示 **排除** 含该状态的刊登 |
| sortBy | string | 否 | 默认文档 **`lastUpdatedDate`**。允许：`sku`、`createdDate`、`lastUpdatedDate` |
| sortOrder | string | 否 | 默认 **`DESC`**。允许：`ASC`、`DESC` |
| pageSize | integer | 否 | 默认 **10**，**最大 20**（超出时脚本会截断为 20 并告警） |
| pageToken | string | 否 | 下一页令牌（上一页响应中的分页字段，以 `body` JSON 为准） |

### 互斥规则（官方 Note）

以下 **不能混用**（本仓库 `search_listings_items.py` 会做校验）：

1. 使用 **`identifiers` / `identifiersType`** 时，**不得**再传 `variationParentSku` 或 `packageHierarchySku`。
2. 使用 **`variationParentSku`** 时，**不得**使用 `identifiers`（及 `identifiersType`）或 `packageHierarchySku`。
3. 使用 **`packageHierarchySku`** 时，**不得**使用 `identifiers` 或 `variationParentSku`。
4. **`variationParentSku`** 与 **`packageHierarchySku`** 亦不得同时使用。

### 速率（文档摘要）

- 默认约 **5 req/s**，burst **5**（以 `x-amzn-RateLimit-Limit` 与账号配额为准；与 getListingsItem 的 burst 可能不同）。

### 成功响应

- **`httpStatus=200`** 时，`body` 为 JSON 字符串，通常含 **列表 + 分页**（字段名以 Amazon 响应为准，常见含 `items`、`numberOfResults`、`pagination` 等）。

---

## 脚本参数映射（`scripts/search_listings_items.py`）

| 脚本 JSON 字段 | 映射 |
|----------------|------|
| sellerId | `storeTokens` + path 编码 |
| region | `region` |
| marketplaceIds | 同 get；→ `marketplaceIds` |
| issueLocale / includedData | → Query |
| identifiers | `array` 或逗号字符串，≤20 个 → `identifiers` |
| identifiersType | → `identifiersType` |
| variationParentSku / packageHierarchySku | → 同名 Query |
| createdAfter / createdBefore / lastUpdatedAfter / lastUpdatedBefore | → 同名 Query |
| withIssueSeverity / withStatus / withoutStatus | `array` 或逗号字符串 → 逗号拼接 |
| sortBy / sortOrder / pageSize / pageToken | → 同名 Query |

成功且 `errcode==200`、`httpStatus==200` 时，脚本 stdout 中额外包含 **`searchResult`**（`body` 解析后的对象）。

---

## patchListingsItem — 上游语义与网关映射

> 官方：[patchListingsItem](https://developer-docs.amazon.com/sp-api/reference/patchlistingsitem)

仅支持对 **顶层** listing 属性做 JSON Patch；嵌套属性 patch 行为以 Amazon 文档为准。**Vendor** 场景下 **`delete`** 可能返回 **400**（官方说明）。

### HTTP 与方法

- **Method**：`PATCH`（经 `developerProxy.method` 传入 **`PATCH`**）
- **Path**（与 getListingsItem 相同，含 **sellerId** 与 **卖家 SKU**）：

```text
listings/2021-08-01/items/{sellerId}/{sku}
```

两段路径均需 **URL 编码**。

### Query 参数（`queryString`）

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| marketplaceIds | string | **是** | 逗号分隔的 marketplace id 列表（脚本接受 JSON 数组并拼为逗号）。与 get 不同，patch 文档为 **列表**；多站点时一并传入 |
| includedData | string | 否 | 逗号分隔；默认文档为 **`issues`**。可选：`identifiers`、`issues`。文档说明：**`identifiers`** 仅在 **`mode=VALIDATION_PREVIEW`** 时可请求 |
| mode | string | 否 | 枚举：**`VALIDATION_PREVIEW`**（校验预览模式，与 `includedData=identifiers` 等组合以官方为准） |
| issueLocale | string | 否 | 如 `en_US`、`fr_CA`；issues 本地化 |

### Body（`developerProxy.body`，JSON 字符串）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| productType | string | **是** | Amazon **product type**（如 `LUGGAGE`、`PRODUCT` 等，须与该 listing 在目录中的类型一致，以 [Product Type Definitions](https://developer-docs.amazon.com/sp-api/reference/getdefinitionsproducttype) 为准） |
| patches | array | **是** | **至少 1 条** [JSON Patch](https://datatracker.ietf.org/doc/html/rfc6902) 操作（Amazon 支持子集） |

**单条 patch 对象**（`patches[]`）：

| 字段 | 必填 | 说明 |
|------|------|------|
| op | 是 | `add` \| `replace` \| `merge` \| `delete` |
| path | 是 | **JSON Pointer**，指向待修改属性（如 `/attributes/item_name`） |
| value | 视 op | `add` / `replace` / `merge` 通常需要；`delete` 可无（Vendor 可能不支持 delete） |

### 速率（文档摘要）

- 默认约 **5 req/s**，burst **5**（以响应头与账号配额为准）。

### 响应（httpStatus）

- **200**：已理解 patch 请求；是否被接受须解析 **`body`** 内 issues / status（以 Amazon 响应 schema 为准）。
- **400 / 403 / 413 / 415 / 429 / 500 / 503**：与通用 SP-API 语义一致。

---

## 脚本参数映射（`scripts/patch_listings_item.py`）

| 脚本 JSON 字段 | 映射 |
|----------------|------|
| sellerId / region / sku | `storeTokens` + `path` 编码 |
| marketplaceIds | 数组或逗号字符串 → `marketplaceIds`（Query，逗号拼接） |
| productType / patches | → **PATCH body** |
| includedData / mode / issueLocale | → Query |

成功且 `errcode==200`、`httpStatus==200` 时，stdout 额外含 **`patchResult`**（解析后的 `body`）。

---

## putListingsItem — 上游语义与网关映射

> 官方：[putListingsItem](https://developer-docs.amazon.com/sp-api/reference/putlistingsitem)

**创建**新刊登或对现有刊登做**全量**更新（非部分 patch）；请求体为完整 **`attributes`** 对象，须符合该 **productType** 的 JSON Schema。

### HTTP 与方法

- **Method**：`PUT`（经 `developerProxy.method` 传入 **`PUT`**）
- **Path**（与 getListingsItem / patchListingsItem 相同）：

```text
listings/2021-08-01/items/{sellerId}/{sku}
```

两段路径均需 **URL 编码**。

### Query 参数（`queryString`）

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| marketplaceIds | string | **是** | 官方约束：**length ≤ 1**（仅 **一个** marketplace id）。脚本在传入多个 id 时 **报错**（与 patch 允许多 id 不同） |
| includedData | string | 否 | 逗号分隔；默认文档为 **`issues`**。可选：`identifiers`、`issues`。**`identifiers`** 仅在 **`mode=VALIDATION_PREVIEW`** 时可请求 |
| mode | string | 否 | **`VALIDATION_PREVIEW`**（校验预览） |
| issueLocale | string | 否 | issues 本地化，如 `en_US` |

### Body（`developerProxy.body`，JSON 字符串）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| productType | string | **是** | Amazon product type（与目录一致，参见 [Product Type Definitions](https://developer-docs.amazon.com/sp-api/reference/getdefinitionsproducttype)） |
| requirements | string | **是** | **`LISTING`**（商品事实 + 销售条款）\| **`LISTING_PRODUCT_ONLY`**（仅商品事实）\| **`LISTING_OFFER_ONLY`**（仅销售条款；**Vendor 不支持**，会 **400**） |
| attributes | object | **是** | 以属性名为键的结构化刊登数据；须满足该 product type 的 schema |

### 速率（文档摘要）

- 默认约 **5 req/s**，burst **10**（以响应头与账号配额为准）。

### 响应（httpStatus）

- **200**：已理解创建/全量更新请求；是否被接受须解析 **`body`** 内 issues 等（以 Amazon 响应为准）。
- **400 / 403 / 413 / 415 / 429 / 500 / 503**：与通用 SP-API 语义一致。

---

## 脚本参数映射（`scripts/put_listings_item.py`）

| 脚本 JSON 字段 | 映射 |
|----------------|------|
| sellerId / region / sku | `storeTokens` + `path` 编码 |
| marketplaceIds | 数组或逗号字符串 → **恰好 1 个** id 写入 Query（多于 1 个则脚本拒绝） |
| productType / requirements / attributes | → **PUT body** |
| includedData / mode / issueLocale | → Query |

成功且 `errcode==200`、`httpStatus==200` 时，stdout 额外含 **`putResult`**（解析后的 `body`）。

---

## deleteListingsItem — 上游语义与网关映射

> 官方：[deleteListingsItem](https://developer-docs.amazon.com/sp-api/reference/deletelistingsitem)

删除指定 **marketplace** 下该 **sellerId + sku** 的刊登项；**无请求体**。

### HTTP 与方法

- **Method**：`DELETE`（经 `developerProxy.method` 传入 **`DELETE`**）
- **Path**（与 get / patch / put 相同）：

```text
listings/2021-08-01/items/{sellerId}/{sku}
```

两段路径均需 **URL 编码**。

### Query 参数（`queryString`）

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| marketplaceIds | string | **是** | 官方约束：**length ≤ 1**（仅 **一个** marketplace id） |
| issueLocale | string | 否 | 本地化，如 `en_US`、`fr_CA` |

### 速率（文档摘要）

- 默认约 **5 req/s**，burst **5**（以响应头与账号配额为准）。

### 响应（httpStatus）

- **200**：已理解删除请求；是否被接受须解析 **`body`**（以 Amazon 响应为准）。
- **400 / 403 / 413 / 415 / 429 / 500 / 503**：与通用 SP-API 语义一致。

---

## 脚本参数映射（`scripts/delete_listings_item.py`）

| 脚本 JSON 字段 | 映射 |
|----------------|------|
| sellerId / region / sku | `storeTokens` + `path` 编码 |
| marketplaceIds | 数组或逗号字符串 → **恰好 1 个** id 写入 Query（多于 1 个则脚本拒绝） |
| issueLocale | 否 → Query |

成功且 `errcode==200`、`httpStatus==200` 时，stdout 额外含 **`deleteResult`**（解析后的 `body`）。

---

## getListingsRestrictions — 上游语义与网关映射

> 官方：[getListingsRestrictions](https://developer-docs.amazon.com/sp-api/reference/getlistingsrestrictions)

返回目录 **ASIN** 在指定 **sellerId** 与 **marketplaceIds** 下的刊登限制。

### HTTP 与方法

- **Method**：`GET`
- **Path**（固定，无 path 参数）：

```text
listings/2021-08-01/restrictions
```

### Query 参数（`queryString`）

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| asin | string | **是** | 目录 ASIN |
| sellerId | string | **是** | 卖家标识（与 `storeTokens` 所用可一致） |
| marketplaceIds | string | **是** | 逗号分隔 marketplace id 列表（脚本接受数组并拼接） |
| conditionType | string | 否 | 商品状况枚举，用于过滤限制（如 `new`、`used_like_new` 等，以官方枚举为准） |
| reasonLocale | string | 否 | 原因文案本地化，如 `en_US` |

### 速率（文档摘要）

- 默认约 **5 req/s**，burst **10**。

### 响应

- **200**：成功返回限制信息；**404** 等资源类错误以 Amazon 为准。

---

## 脚本参数映射（`scripts/get_listings_restrictions.py`）

| 脚本 JSON 字段 | 映射 |
|----------------|------|
| sellerId / region | `storeTokens` |
| asin / marketplaceIds / conditionType / reasonLocale | → Query |

成功且 `errcode==200`、`httpStatus==200` 时，stdout 额外含 **`restrictionsResult`**。

---

## searchDefinitionsProductTypes — 上游语义与网关映射

> 官方：[searchDefinitionsProductTypes](https://developer-docs.amazon.com/sp-api/reference/searchdefinitionsproducttypes)

搜索可用的 **product type** 定义列表。

### HTTP 与方法

- **Method**：`GET`
- **Path**：

```text
definitions/2020-09-01/productTypes
```

### Query 参数

| 参数名 | 必填 | 说明 |
|--------|------|------|
| marketplaceIds | **是** | 逗号分隔（脚本接受数组） |
| keywords | 否 | 逗号分隔关键词列表；**不可与** `itemName` **同用** |
| itemName | 否 | ASIN 商品标题用于推荐 product type；**不可与** `keywords` **同用** |
| locale / searchLocale | 否 | 展示语言、搜索所用 locale |

### 速率（文档摘要）

- 默认约 **5 req/s**，burst **10**。

---

## 脚本参数映射（`scripts/search_definitions_product_types.py`）

| 脚本 JSON 字段 | 映射 |
|----------------|------|
| sellerId / region | `storeTokens` |
| marketplaceIds | → Query |
| keywords / itemName | → Query（**互斥**，脚本校验） |
| locale / searchLocale | → Query |

成功且 `errcode==200`、`httpStatus==200` 时，stdout 额外含 **`productTypesSearchResult`**。

---

## getDefinitionsProductType — 上游语义与网关映射

> 官方：[getDefinitionsProductType](https://developer-docs.amazon.com/sp-api/reference/getdefinitionsproducttype)

按 **productType** 名称拉取 JSON Schema 定义。

### HTTP 与方法

- **Method**：`GET`
- **Path**：

```text
definitions/2020-09-01/productTypes/{productType}
```

`{productType}` 须 **URL 编码**（脚本使用 `urllib.parse.quote`）。

### Query 参数

| 参数名 | 必填 | 说明 |
|--------|------|------|
| marketplaceIds | **是** | 官方说明当前 **limited to one** `marketplaceId`；脚本 **多于 1 个即报错** |
| sellerId | 否 | 传入时填充卖家相关 schema；脚本字段 **`querySellerId`** → Query **`sellerId`**（避免与用于取令牌的 `sellerId` 混淆；通常可设为相同值） |
| productTypeVersion | 否 | 默认 **`LATEST`**；预发布可用 **`RELEASE_CANDIDATE`**（以官方为准） |
| requirements | 否 | `LISTING` \| `LISTING_PRODUCT_ONLY` \| `LISTING_OFFER_ONLY`（默认 **LISTING**） |
| requirementsEnforced | 否 | `ENFORCED` \| `NOT_ENFORCED` |
| locale | 否 | 展示标签等所用 locale（官方枚举见文档） |

### 速率（文档摘要）

- 默认约 **5 req/s**，burst **10**。大 schema 响应体可能较大。

---

## 脚本参数映射（`scripts/get_definitions_product_type.py`）

| 脚本 JSON 字段 | 映射 |
|----------------|------|
| sellerId / region | `storeTokens`（`sellerId` 为授权店铺） |
| productType | → path 末段（编码） |
| marketplaceIds | → Query，**恰好 1 个** id |
| querySellerId | → Query `sellerId`（可选） |
| productTypeVersion / requirements / requirementsEnforced / locale | → Query |

成功且 `errcode==200`、`httpStatus==200` 时，stdout 额外含 **`productTypeDefinitionResult`**。

---

## curl 示例（两步：取令牌 + 代理 GET / PATCH / PUT / DELETE）

**1）取 `accessToken`（与 store-report 相同）**

```bash
curl -sS -X POST "https://tool-gateway.linkfox.com/spApi/storeTokens" \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"sellerId":"A1BCDEFGHIJK2","region":"NA"}'
```

**2）getListingsItem（path 与 query 按实际 sellerId / sku / marketplace 替换）**

```bash
curl -sS -X POST "https://tool-gateway.linkfox.com/spApi/developerProxy" \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "region": "NA",
    "path": "listings/2021-08-01/items/A1BCDEFGHIJK2/My-Seller-SKU-001",
    "method": "GET",
    "amzAccessToken": "Atza|IwEBI...",
    "queryString": "marketplaceIds=ATVPDKIKX0DER&includedData=summaries,attributes"
  }'
```

> 若 `sku` 或 `sellerId` 含需编码字符，请使用与脚本一致的 **百分号编码** 后再放入 `path`。

**3）searchListingsItems（path 仅到 `sellerId`，query 含 marketplaceIds 与分页等）**

```bash
curl -sS -X POST "https://tool-gateway.linkfox.com/spApi/developerProxy" \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "region": "NA",
    "path": "listings/2021-08-01/items/A1BCDEFGHIJK2",
    "method": "GET",
    "amzAccessToken": "Atza|IwEBI...",
    "queryString": "marketplaceIds=ATVPDKIKX0DER&pageSize=10&sortBy=lastUpdatedDate&sortOrder=DESC&includedData=summaries"
  }'
```

按 ASIN 搜索时，在 `queryString` 中增加 `identifiers` 与 `identifiersType`（**勿与** `variationParentSku` / `packageHierarchySku` 同用），例如：`identifiers=B08N5WRWNW&identifiersType=ASIN`（示例 ASIN 请替换为真实值）。

**4）patchListingsItem（`method` 为 `PATCH`，`body` 为 JSON 字符串；`productType` 与 `patches` 须按官方 schema 填写）**

```bash
curl -sS -X POST "https://tool-gateway.linkfox.com/spApi/developerProxy" \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "region": "NA",
    "path": "listings/2021-08-01/items/A1BCDEFGHIJK2/My-Seller-SKU-001",
    "method": "PATCH",
    "amzAccessToken": "Atza|IwEBI...",
    "queryString": "marketplaceIds=ATVPDKIKX0DER&includedData=issues",
    "contentType": "application/json",
    "body": "{\"productType\":\"LUGGAGE\",\"patches\":[{\"op\":\"replace\",\"path\":\"/attributes/item_name\",\"value\":[{\"value\":\"Example\",\"marketplace_id\":\"ATVPDKIKX0DER\"}]}]}"
  }'
```

> 上例 **`body` 仅演示字段形态**；真实 `path` / `value` 必须与 **product type JSON Schema** 一致，否则会 **400**。

**5）putListingsItem（`method` 为 `PUT`；`marketplaceIds` 在 Query 中仅 **一个** id；`body` 含 `productType`、`requirements`、`attributes`）**

```bash
curl -sS -X POST "https://tool-gateway.linkfox.com/spApi/developerProxy" \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "region": "NA",
    "path": "listings/2021-08-01/items/A1BCDEFGHIJK2/My-Seller-SKU-001",
    "method": "PUT",
    "amzAccessToken": "Atza|IwEBI...",
    "queryString": "marketplaceIds=ATVPDKIKX0DER&includedData=issues",
    "contentType": "application/json",
    "body": "{\"productType\":\"LUGGAGE\",\"requirements\":\"LISTING\",\"attributes\":{\"item_name\":[{\"value\":\"Example Title\",\"marketplace_id\":\"ATVPDKIKX0DER\"}]}}"
  }'
```

> 上例 **`attributes` 仅演示键形态**；须与 **product type schema** 一致。**LISTING_OFFER_ONLY** 对 Vendor 会 **400**。

**6）deleteListingsItem（`method` 为 `DELETE`；`queryString` 仅含 **一个** `marketplaceIds`；不传 `body`）**

```bash
curl -sS -X POST "https://tool-gateway.linkfox.com/spApi/developerProxy" \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "region": "NA",
    "path": "listings/2021-08-01/items/A1BCDEFGHIJK2/My-Seller-SKU-001",
    "method": "DELETE",
    "amzAccessToken": "Atza|IwEBI...",
    "queryString": "marketplaceIds=ATVPDKIKX0DER"
  }'
```

**7）getListingsRestrictions（固定 path `listings/2021-08-01/restrictions`，Query 含 asin、sellerId、marketplaceIds）**

```bash
curl -sS -X POST "https://tool-gateway.linkfox.com/spApi/developerProxy" \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "region": "NA",
    "path": "listings/2021-08-01/restrictions",
    "method": "GET",
    "amzAccessToken": "Atza|IwEBI...",
    "queryString": "asin=B08N5WRWNW&sellerId=A1BCDEFGHIJK2&marketplaceIds=ATVPDKIKX0DER"
  }'
```

**8）searchDefinitionsProductTypes（path `definitions/2020-09-01/productTypes`；`keywords` 与 `itemName` 勿同用）**

```bash
curl -sS -X POST "https://tool-gateway.linkfox.com/spApi/developerProxy" \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "region": "NA",
    "path": "definitions/2020-09-01/productTypes",
    "method": "GET",
    "amzAccessToken": "Atza|IwEBI...",
    "queryString": "marketplaceIds=ATVPDKIKX0DER&keywords=luggage,suitcase"
  }'
```

**9）getDefinitionsProductType（path 末段为 product type 名称；`marketplaceIds` 仅一个）**

```bash
curl -sS -X POST "https://tool-gateway.linkfox.com/spApi/developerProxy" \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "region": "NA",
    "path": "definitions/2020-09-01/productTypes/LUGGAGE",
    "method": "GET",
    "amzAccessToken": "Atza|IwEBI...",
    "queryString": "marketplaceIds=ATVPDKIKX0DER&requirements=LISTING&productTypeVersion=LATEST"
  }'
```

---

## Feedback API

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **Content-Type:** `application/json`

```json
{
  "skillName": "linkfox-amazon-store-listings",
  "sentiment": "POSITIVE",
  "category": "OTHER",
  "content": "getListingsItem / searchListingsItems / patchListingsItem / putListingsItem / deleteListingsItem / getListingsRestrictions / searchDefinitionsProductTypes / getDefinitionsProductType 结果符合预期。"
}
```
