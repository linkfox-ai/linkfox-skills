# 脚本输入、构参与本地输出

网关参数与响应定义见 [api.md](api.md)。本文件的本地输入、输出与上游构参不属于网关 DTO；只使用实际响应已有的业务字段。

共享脚本约定适用于本文件各操作；操作差异以对应小节为准。

## 接口：获取单条刊登（getListingsItem）

### 脚本输入与构参

#### 脚本 JSON 参数

| 字段 | 必填 | 说明 |
|------|------|------|
| sellerId | 是 | 已授权 Seller ID |
| region | 是 | `NA` / `EU` / `FE` |
| sku | 是 | **卖家 SKU**（非 ASIN） |
| marketplaceIds | 是 | 建议仅 **一个** marketplace id |
| includedData / issueLocale | 否 | 见 `references/api.md` |

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| skipDepCheck | boolean | 否 | 默认 false；仅在外部流程已确认依赖时跳过本地安装检测，不绕过店铺授权。 |
| --inline | CLI flag | 否 | 强制完整打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 本技能不启用响应缓存；本接口脚本调用 run 时始终添加此选项，读取和写入均不复用或保存响应缓存。 |

本地依赖检查返回 0 表示找到认证技能；返回 42 且 stderr 含 `DEPENDENCY_MISSING:` 表示依赖缺失，应先安装 `linkfox-amazon-store-auth`。不得在本技能内绕过依赖实现授权或令牌逻辑。
保留 `LINKFOX_TOOL_GATEWAY` 优先，其次 `STORE_API_BASE_URL`、`SPAPI_BASE_URL` 的旧环境变量兼容行为。会话数据必须保存在当前工作目录；不可写时在请求前报错，不回退到临时目录。

#### HTTP 与方法（Amazon）

- **Method**：`GET`
- **资源路径模板**（写入 `developerProxy.path`）：

```text
listings/2021-08-01/items/{sellerId}/{sku}
```

其中 **`{sellerId}`**、**`{sku}`** 须做 **URL path 分段编码**（例如空格、`/` 等字符）；本仓库脚本使用百分号编码后拼入 `path`。

> 说明：不同区域 SP-API **主机名**不同（na/eu/fe 等），由网关按 `sellerId` + `region` 解析店铺令牌，调用方**只传相对 path** 即可。

#### Path 参数（写入 path 的占位段）

| 名称 | 类型 | 必填 | 说明 |
|------|------|------|------|
| sellerId | string | 是 | 卖家标识，与已授权店铺一致（与 `/spApi/storeTokens` 所用 `sellerId` 相同） |
| sku | string | 是 | **卖家自定义 SKU**（Seller SKU），不是 ASIN。须与 Listing 在目标站点下实际存在的 seller SKU 一致 |

#### Query 参数（写入 `developerProxy.queryString`，无 `?`）

以下按 Amazon 文档整理；**键名大小写**须与官方一致。

| 参数名 | 类型 | 必填 | 约束 / 说明 |
|--------|------|------|----------------|
| marketplaceIds | string | **是** | 目标 marketplace id。官方 schema 常见为 **单站点**（文档标注 length ≤ 1 时应只传 **一个** id）。多个 id 时本仓库脚本 **仅取第一个** 并打 stderr 警告。示例：`ATVPDKIKX0DER`（美国）。**Query 中写法**：`marketplaceIds=ATVPDKIKX0DER`（单值；若网关要求重复键名以官方为准，一般单站点即可） |
| includedData | string | 否 | 逗号分隔数据集列表，控制响应中包含哪些块。**不传**时上游通常等价于默认 **`summaries`**（以实网为准）。可选值（与官方一致）：`summaries`、`attributes`、`issues`、`offers`、`fulfillmentAvailability`、`procurement`、`relationships`、`productTypes`。示例：`includedData=summaries,attributes` |
| issueLocale | string | 否 | **issues** 等字段的本地化语言。示例：`en_US`、`fr_CA`。未传时通常使用第一个 marketplace 的默认语言；不可用回退行为以 Amazon 为准 |

#### 官方默认与速率（摘要）

- **includedData** 默认集：文档为 **`summaries`**（若需结构化属性、报价、库存等，请在 `includedData` 中显式增加对应 token）。
- **Usage plan（文档默认值）**：约 **5 req/s**，burst **10**（以响应头 `x-amzn-RateLimit-Limit` 及账号实际配额为准）。

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|------|------|------|
| developerProxy | object | 上述网关完整响应，错误时保留完整错误消息。 |
| resolvedPath | string | 实际使用的编码后资源路径。 |
| queryString | string | 实际发送的不带问号的查询串。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败时为 null。 |
| listing | object / null | 网关正常响应且上游 httpStatus 为 200 时解析的 body；解析失败为 null。 |
| listingRaw | string | 仅解析失败时保留原始 body。 |

#### 上游成功 / 常见错误（httpStatus）

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

## 接口：搜索刊登列表（searchListingsItems）

### 脚本输入与构参

#### 脚本 JSON 参数

| 字段 | 必填 | 说明 |
|------|------|------|
| sellerId | 是 | 已授权 Seller ID |
| region | 是 | `NA` / `EU` / `FE` |
| marketplaceIds | 是 | 建议仅 **一个** marketplace id |
| identifiers + identifiersType | 否 | 最多 **20** 个；与 `variationParentSku`、`packageHierarchySku` **不能同用** |
| variationParentSku / packageHierarchySku | 否 | 与 identifiers **互斥** |
| 时间窗 / 状态 / 排序 / 分页 | 否 | `createdAfter`、`lastUpdatedBefore`、`withStatus`、`sortBy`、`pageSize`（≤20）、`pageToken` 等，见 **`references/api.md`** |

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| skipDepCheck | boolean | 否 | 默认 false；仅在外部流程已确认依赖时跳过本地安装检测，不绕过店铺授权。 |
| --inline | CLI flag | 否 | 强制完整打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 本技能不启用响应缓存；本接口脚本调用 run 时始终添加此选项，读取和写入均不复用或保存响应缓存。 |

本地依赖检查返回 0 表示找到认证技能；返回 42 且 stderr 含 `DEPENDENCY_MISSING:` 表示依赖缺失，应先安装 `linkfox-amazon-store-auth`。不得在本技能内绕过依赖实现授权或令牌逻辑。
保留 `LINKFOX_TOOL_GATEWAY` 优先，其次 `STORE_API_BASE_URL`、`SPAPI_BASE_URL` 的旧环境变量兼容行为。会话数据必须保存在当前工作目录；不可写时在请求前报错，不回退到临时目录。

#### HTTP 与方法

- **Method**：`GET`
- **资源路径**（写入 `developerProxy.path`，仅含 `sellerId`，**无**路径尾段的 SKU）：

```text
listings/2021-08-01/items/{sellerId}
```

`{sellerId}` 须 **URL 编码**（对每个 path 分段分别百分号编码）。

#### Path 参数

| 名称 | 类型 | 必填 | 说明 |
|------|------|------|------|
| sellerId | string | 是 | 卖家标识，与已授权店铺及 `storeTokens` 一致 |

#### Query 参数（写入 `queryString`）

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

#### 互斥规则（官方 Note）

以下 **不能混用**（本仓库 `search_listings_items.py` 会做校验）：

1. 使用 **`identifiers` / `identifiersType`** 时，**不得**再传 `variationParentSku` 或 `packageHierarchySku`。
2. 使用 **`variationParentSku`** 时，**不得**使用 `identifiers`（及 `identifiersType`）或 `packageHierarchySku`。
3. 使用 **`packageHierarchySku`** 时，**不得**使用 `identifiers` 或 `variationParentSku`。
4. **`variationParentSku`** 与 **`packageHierarchySku`** 亦不得同时使用。

#### 速率（文档摘要）

- 默认约 **5 req/s**，burst **5**（以 `x-amzn-RateLimit-Limit` 与账号配额为准；与 getListingsItem 的 burst 可能不同）。

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|------|------|------|
| developerProxy | object | 上述网关完整响应，错误时保留完整错误消息。 |
| resolvedPath | string | 实际使用的编码后资源路径。 |
| queryString | string | 实际发送的不带问号的查询串。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败时为 null。 |
| searchResult | object / null | 网关正常响应且上游 httpStatus 为 200 时解析的 body；解析失败为 null。 |
| searchResultRaw | string | 仅解析失败时保留原始 body。 |

#### 成功响应

- **`httpStatus=200`** 时，`body` 为 JSON 字符串，通常含 **列表 + 分页**（字段名以 Amazon 响应为准，常见含 `items`、`numberOfResults`、`pagination` 等）。

## 接口：部分更新刊登（patchListingsItem）

### 脚本输入与构参

#### 脚本 JSON 参数

| 字段 | 必填 | 说明 |
|------|------|------|
| sellerId | 是 | 已授权 Seller ID |
| region | 是 | `NA` / `EU` / `FE` |
| sku | 是 | **卖家 SKU** |
| marketplaceIds | 是 | 数组或逗号字符串；脚本拼入 Query |
| productType | 是 | Amazon product type |
| patches | 是 | **至少 1 条** JSON Patch（`op`、`path` 等） |
| includedData / mode / issueLocale | 否 | 见 **`references/api.md`** |

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| skipDepCheck | boolean | 否 | 默认 false；仅在外部流程已确认依赖时跳过本地安装检测，不绕过店铺授权。 |
| --inline | CLI flag | 否 | 强制完整打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 本技能不启用响应缓存；本接口脚本调用 run 时始终添加此选项，读取和写入均不复用或保存响应缓存。 |

本地依赖检查返回 0 表示找到认证技能；返回 42 且 stderr 含 `DEPENDENCY_MISSING:` 表示依赖缺失，应先安装 `linkfox-amazon-store-auth`。不得在本技能内绕过依赖实现授权或令牌逻辑。
保留 `LINKFOX_TOOL_GATEWAY` 优先，其次 `STORE_API_BASE_URL`、`SPAPI_BASE_URL` 的旧环境变量兼容行为。会话数据必须保存在当前工作目录；不可写时在请求前报错，不回退到临时目录。

#### HTTP 与方法

- **Method**：`PATCH`（经 `developerProxy.method` 传入 **`PATCH`**）
- **Path**（含 **sellerId** 与 **卖家 SKU**）：

```text
listings/2021-08-01/items/{sellerId}/{sku}
```

两段路径均需 **URL 编码**。

#### Query 参数（`queryString`）

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| marketplaceIds | string | **是** | 逗号分隔的 marketplace id 列表（脚本接受 JSON 数组并拼为逗号）。与 get 不同，patch 文档为 **列表**；多站点时一并传入 |
| includedData | string | 否 | 逗号分隔；默认文档为 **`issues`**。可选：`identifiers`、`issues`。文档说明：**`identifiers`** 仅在 **`mode=VALIDATION_PREVIEW`** 时可请求 |
| mode | string | 否 | 枚举：**`VALIDATION_PREVIEW`**（校验预览模式，与 `includedData=identifiers` 等组合以官方为准） |
| issueLocale | string | 否 | 如 `en_US`、`fr_CA`；issues 本地化 |

#### Body（`developerProxy.body`，JSON 字符串）

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

#### 速率（文档摘要）

- 默认约 **5 req/s**，burst **5**（以响应头与账号配额为准）。

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|------|------|------|
| developerProxy | object | 上述网关完整响应，错误时保留完整错误消息。 |
| resolvedPath | string | 实际使用的编码后资源路径。 |
| queryString | string | 实际发送的不带问号的查询串。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败时为 null。 |
| requestBody | object | 本次提交的上游 JSON 对象，发往网关时序列化为 body 字符串。 |
| patchResult | object / null | 网关正常响应且上游 httpStatus 为 200 时解析的 body；解析失败为 null。 |
| patchResultRaw | string | 仅解析失败时保留原始 body。 |

#### 响应（httpStatus）

- **200**：已理解 patch 请求；是否被接受须解析 **`body`** 内 issues / status（以 Amazon 响应 schema 为准）。
- **400 / 403 / 413 / 415 / 429 / 500 / 503**：与通用 SP-API 语义一致。

## 接口：创建或全量更新刊登（putListingsItem）

### 脚本输入与构参

#### 脚本 JSON 参数

| 字段 | 必填 | 说明 |
|------|------|------|
| sellerId | 是 | 已授权 Seller ID |
| region | 是 | `NA` / `EU` / `FE` |
| sku | 是 | **卖家 SKU** |
| marketplaceIds | 是 | **恰好一个** marketplace id |
| productType | 是 | Amazon product type |
| requirements | 是 | `LISTING` \| `LISTING_PRODUCT_ONLY` \| `LISTING_OFFER_ONLY` |
| attributes | 是 | 须符合该 product type schema |
| includedData / mode / issueLocale | 否 | 见 **`references/api.md`** |

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| skipDepCheck | boolean | 否 | 默认 false；仅在外部流程已确认依赖时跳过本地安装检测，不绕过店铺授权。 |
| --inline | CLI flag | 否 | 强制完整打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 本技能不启用响应缓存；本接口脚本调用 run 时始终添加此选项，读取和写入均不复用或保存响应缓存。 |

本地依赖检查返回 0 表示找到认证技能；返回 42 且 stderr 含 `DEPENDENCY_MISSING:` 表示依赖缺失，应先安装 `linkfox-amazon-store-auth`。不得在本技能内绕过依赖实现授权或令牌逻辑。
保留 `LINKFOX_TOOL_GATEWAY` 优先，其次 `STORE_API_BASE_URL`、`SPAPI_BASE_URL` 的旧环境变量兼容行为。会话数据必须保存在当前工作目录；不可写时在请求前报错，不回退到临时目录。

#### HTTP 与方法

- **Method**：`PUT`（经 `developerProxy.method` 传入 **`PUT`**）
- **Path**（含 **sellerId** 与 **卖家 SKU**）：

```text
listings/2021-08-01/items/{sellerId}/{sku}
```

两段路径均需 **URL 编码**。

#### Query 参数（`queryString`）

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| marketplaceIds | string | **是** | 官方约束：**length ≤ 1**（仅 **一个** marketplace id）。脚本在传入多个 id 时 **报错**（与 patch 允许多 id 不同） |
| includedData | string | 否 | 逗号分隔；默认文档为 **`issues`**。可选：`identifiers`、`issues`。**`identifiers`** 仅在 **`mode=VALIDATION_PREVIEW`** 时可请求 |
| mode | string | 否 | **`VALIDATION_PREVIEW`**（校验预览） |
| issueLocale | string | 否 | issues 本地化，如 `en_US` |

#### Body（`developerProxy.body`，JSON 字符串）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| productType | string | **是** | Amazon product type（与目录一致，参见 [Product Type Definitions](https://developer-docs.amazon.com/sp-api/reference/getdefinitionsproducttype)） |
| requirements | string | **是** | **`LISTING`**（商品事实 + 销售条款）\| **`LISTING_PRODUCT_ONLY`**（仅商品事实）\| **`LISTING_OFFER_ONLY`**（仅销售条款；**Vendor 不支持**，会 **400**） |
| attributes | object | **是** | 以属性名为键的结构化刊登数据；须满足该 product type 的 schema |

#### 速率（文档摘要）

- 默认约 **5 req/s**，burst **10**（以响应头与账号配额为准）。

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|------|------|------|
| developerProxy | object | 上述网关完整响应，错误时保留完整错误消息。 |
| resolvedPath | string | 实际使用的编码后资源路径。 |
| queryString | string | 实际发送的不带问号的查询串。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败时为 null。 |
| requestBody | object | 本次提交的上游 JSON 对象，发往网关时序列化为 body 字符串。 |
| putResult | object / null | 网关正常响应且上游 httpStatus 为 200 时解析的 body；解析失败为 null。 |
| putResultRaw | string | 仅解析失败时保留原始 body。 |

#### 响应（httpStatus）

- **200**：已理解创建/全量更新请求；是否被接受须解析 **`body`** 内 issues 等（以 Amazon 响应为准）。
- **400 / 403 / 413 / 415 / 429 / 500 / 503**：与通用 SP-API 语义一致。

## 接口：删除刊登（deleteListingsItem）

### 脚本输入与构参

#### 脚本 JSON 参数

| 字段 | 必填 | 说明 |
|------|------|------|
| sellerId | 是 | 已授权 Seller ID |
| region | 是 | `NA` / `EU` / `FE` |
| sku | 是 | **卖家 SKU** |
| marketplaceIds | 是 | **恰好一个** marketplace id |
| issueLocale | 否 | 见 **`references/api.md`** |

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| skipDepCheck | boolean | 否 | 默认 false；仅在外部流程已确认依赖时跳过本地安装检测，不绕过店铺授权。 |
| --inline | CLI flag | 否 | 强制完整打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 本技能不启用响应缓存；本接口脚本调用 run 时始终添加此选项，读取和写入均不复用或保存响应缓存。 |

本地依赖检查返回 0 表示找到认证技能；返回 42 且 stderr 含 `DEPENDENCY_MISSING:` 表示依赖缺失，应先安装 `linkfox-amazon-store-auth`。不得在本技能内绕过依赖实现授权或令牌逻辑。
保留 `LINKFOX_TOOL_GATEWAY` 优先，其次 `STORE_API_BASE_URL`、`SPAPI_BASE_URL` 的旧环境变量兼容行为。会话数据必须保存在当前工作目录；不可写时在请求前报错，不回退到临时目录。

#### HTTP 与方法

- **Method**：`DELETE`（经 `developerProxy.method` 传入 **`DELETE`**）
- **Path**（含 **sellerId** 与 **卖家 SKU**）：

```text
listings/2021-08-01/items/{sellerId}/{sku}
```

两段路径均需 **URL 编码**。

#### Query 参数（`queryString`）

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| marketplaceIds | string | **是** | 官方约束：**length ≤ 1**（仅 **一个** marketplace id） |
| issueLocale | string | 否 | 本地化，如 `en_US`、`fr_CA` |

#### 速率（文档摘要）

- 默认约 **5 req/s**，burst **5**（以响应头与账号配额为准）。

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|------|------|------|
| developerProxy | object | 上述网关完整响应，错误时保留完整错误消息。 |
| resolvedPath | string | 实际使用的编码后资源路径。 |
| queryString | string | 实际发送的不带问号的查询串。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败时为 null。 |
| deleteResult | object / null | 网关正常响应且上游 httpStatus 为 200 时解析的 body；解析失败为 null。 |
| deleteResultRaw | string | 仅解析失败时保留原始 body。 |

#### 响应（httpStatus）

- **200**：已理解删除请求；是否被接受须解析 **`body`**（以 Amazon 响应为准）。
- **400 / 403 / 413 / 415 / 429 / 500 / 503**：与通用 SP-API 语义一致。

## 接口：查询刊登限制（getListingsRestrictions）

### 脚本输入与构参

#### 脚本 JSON 参数

| 字段 | 必填 | 说明 |
|------|------|------|
| sellerId | 是 | 用于网关店铺授权识别与 Query |
| region | 是 | `NA` / `EU` / `FE` |
| asin | 是 | 目录 ASIN |
| marketplaceIds | 是 | 数组或逗号字符串 |
| conditionType / reasonLocale | 否 | 见 **`references/api.md`** |

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| skipDepCheck | boolean | 否 | 默认 false；仅在外部流程已确认依赖时跳过本地安装检测，不绕过店铺授权。 |
| --inline | CLI flag | 否 | 强制完整打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 本技能不启用响应缓存；本接口脚本调用 run 时始终添加此选项，读取和写入均不复用或保存响应缓存。 |

本地依赖检查返回 0 表示找到认证技能；返回 42 且 stderr 含 `DEPENDENCY_MISSING:` 表示依赖缺失，应先安装 `linkfox-amazon-store-auth`。不得在本技能内绕过依赖实现授权或令牌逻辑。
保留 `LINKFOX_TOOL_GATEWAY` 优先，其次 `STORE_API_BASE_URL`、`SPAPI_BASE_URL` 的旧环境变量兼容行为。会话数据必须保存在当前工作目录；不可写时在请求前报错，不回退到临时目录。

#### HTTP 与方法

- **Method**：`GET`
- **Path**（固定，无 path 参数）：

```text
listings/2021-08-01/restrictions
```

#### Query 参数（`queryString`）

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| asin | string | **是** | 目录 ASIN |
| sellerId | string | **是** | 卖家标识（与 `storeTokens` 所用可一致） |
| marketplaceIds | string | **是** | 逗号分隔 marketplace id 列表（脚本接受数组并拼接） |
| conditionType | string | 否 | 商品状况枚举，用于过滤限制（如 `new`、`used_like_new` 等，以官方枚举为准） |
| reasonLocale | string | 否 | 原因文案本地化，如 `en_US` |

#### 速率（文档摘要）

- 默认约 **5 req/s**，burst **10**。

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|------|------|------|
| developerProxy | object | 上述网关完整响应，错误时保留完整错误消息。 |
| resolvedPath | string | 实际使用的编码后资源路径。 |
| queryString | string | 实际发送的不带问号的查询串。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败时为 null。 |
| restrictionsResult | object / null | 网关正常响应且上游 httpStatus 为 200 时解析的 body；解析失败为 null。 |
| restrictionsResultRaw | string | 仅解析失败时保留原始 body。 |

#### 响应

- **200**：成功返回限制信息；**404** 等资源类错误以 Amazon 为准。

## 接口：搜索商品类型（searchDefinitionsProductTypes）

### 脚本输入与构参

#### 脚本 JSON 参数

| 字段 | 必填 | 说明 |
|------|------|------|
| sellerId | 是 | 用于网关店铺授权识别 |
| region | 是 | `NA` / `EU` / `FE` |
| marketplaceIds | 是 | 数组或逗号字符串 |
| keywords **或** itemName | 否 | **二者不可同时传**（非空时互斥） |
| locale / searchLocale | 否 | 见 **`references/api.md`** |

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| skipDepCheck | boolean | 否 | 默认 false；仅在外部流程已确认依赖时跳过本地安装检测，不绕过店铺授权。 |
| --inline | CLI flag | 否 | 强制完整打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 本技能不启用响应缓存；本接口脚本调用 run 时始终添加此选项，读取和写入均不复用或保存响应缓存。 |

本地依赖检查返回 0 表示找到认证技能；返回 42 且 stderr 含 `DEPENDENCY_MISSING:` 表示依赖缺失，应先安装 `linkfox-amazon-store-auth`。不得在本技能内绕过依赖实现授权或令牌逻辑。
保留 `LINKFOX_TOOL_GATEWAY` 优先，其次 `STORE_API_BASE_URL`、`SPAPI_BASE_URL` 的旧环境变量兼容行为。会话数据必须保存在当前工作目录；不可写时在请求前报错，不回退到临时目录。

#### HTTP 与方法

- **Method**：`GET`
- **Path**：

```text
definitions/2020-09-01/productTypes
```

#### Query 参数

| 参数名 | 必填 | 说明 |
|--------|------|------|
| marketplaceIds | **是** | 逗号分隔（脚本接受数组） |
| keywords | 否 | 逗号分隔关键词列表；**不可与** `itemName` **同用** |
| itemName | 否 | ASIN 商品标题用于推荐 product type；**不可与** `keywords` **同用** |
| locale / searchLocale | 否 | 展示语言、搜索所用 locale |

#### 速率（文档摘要）

- 默认约 **5 req/s**，burst **10**。

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|------|------|------|
| developerProxy | object | 上述网关完整响应，错误时保留完整错误消息。 |
| resolvedPath | string | 实际使用的编码后资源路径。 |
| queryString | string | 实际发送的不带问号的查询串。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败时为 null。 |
| productTypesSearchResult | object / null | 网关正常响应且上游 httpStatus 为 200 时解析的 body；解析失败为 null。 |
| productTypesSearchResultRaw | string | 仅解析失败时保留原始 body。 |

## 接口：获取商品类型定义（getDefinitionsProductType）

### 脚本输入与构参

#### 脚本 JSON 参数

| 字段 | 必填 | 说明 |
|------|------|------|
| sellerId | 是 | 用于网关店铺授权识别 |
| region | 是 | `NA` / `EU` / `FE` |
| productType | 是 | 如 `LUGGAGE`（写入 path） |
| marketplaceIds | 是 | **恰好一个** id |
| querySellerId | 否 | 若需上游 Query **`sellerId`**（卖家专属 schema），传入；常与 `sellerId` 相同 |
| productTypeVersion / requirements / requirementsEnforced / locale | 否 | 见 **`references/api.md`** |

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| skipDepCheck | boolean | 否 | 默认 false；仅在外部流程已确认依赖时跳过本地安装检测，不绕过店铺授权。 |
| --inline | CLI flag | 否 | 强制完整打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 本技能不启用响应缓存；本接口脚本调用 run 时始终添加此选项，读取和写入均不复用或保存响应缓存。 |

本地依赖检查返回 0 表示找到认证技能；返回 42 且 stderr 含 `DEPENDENCY_MISSING:` 表示依赖缺失，应先安装 `linkfox-amazon-store-auth`。不得在本技能内绕过依赖实现授权或令牌逻辑。
保留 `LINKFOX_TOOL_GATEWAY` 优先，其次 `STORE_API_BASE_URL`、`SPAPI_BASE_URL` 的旧环境变量兼容行为。会话数据必须保存在当前工作目录；不可写时在请求前报错，不回退到临时目录。

#### HTTP 与方法

- **Method**：`GET`
- **Path**：

```text
definitions/2020-09-01/productTypes/{productType}
```

`{productType}` 须 **URL 编码**（脚本使用 `urllib.parse.quote`）。

#### Query 参数

| 参数名 | 必填 | 说明 |
|--------|------|------|
| marketplaceIds | **是** | 官方说明当前 **limited to one** `marketplaceId`；脚本 **多于 1 个即报错** |
| sellerId | 否 | 传入时填充卖家相关 schema；脚本字段 **`querySellerId`** → Query **`sellerId`**（避免与用于取令牌的 `sellerId` 混淆；通常可设为相同值） |
| productTypeVersion | 否 | 默认 **`LATEST`**；预发布可用 **`RELEASE_CANDIDATE`**（以官方为准） |
| requirements | 否 | `LISTING` \| `LISTING_PRODUCT_ONLY` \| `LISTING_OFFER_ONLY`（默认 **LISTING**） |
| requirementsEnforced | 否 | `ENFORCED` \| `NOT_ENFORCED` |
| locale | 否 | 展示标签等所用 locale（官方枚举见文档） |

#### 速率（文档摘要）

- 默认约 **5 req/s**，burst **10**。大 schema 响应体可能较大。

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|------|------|------|
| developerProxy | object | 上述网关完整响应，错误时保留完整错误消息。 |
| resolvedPath | string | 实际使用的编码后资源路径。 |
| queryString | string | 实际发送的不带问号的查询串。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败时为 null。 |
| productTypeDefinitionResult | object / null | 网关正常响应且上游 httpStatus 为 200 时解析的 body；解析失败为 null。 |
| productTypeDefinitionResultRaw | string | 仅解析失败时保留原始 body。 |
