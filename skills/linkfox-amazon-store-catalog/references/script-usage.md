# 脚本输入、构参与本地输出

网关参数与响应定义见 [api.md](api.md)。本文件的本地输入、输出与上游构参不属于网关 DTO；只使用实际响应已有的业务字段。

共享脚本约定适用于本文件各操作；操作差异以对应小节为准。

## 接口：查询商品类目（listCatalogCategories）

### 脚本输入与构参

#### 脚本 JSON 参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| sellerId | string | 是 | 已授权店铺 Seller ID。 |
| region | string | 是 | `NA` / `EU` / `FE`。 |
| marketplaceId / marketplaceIds | string / string[] | 是 | 支持单值别名或数组、逗号分隔字符串；必须只提供一个站点。若两者均传，优先 `marketplaceIds`；取唯一站点写入 `MarketplaceId`，多个站点会在本地报错，不静默截取。 |
| asin / ASIN | string | 条件 | 与 sellerSku 二选一；优先读取 `asin`，兼容 `ASIN`。 |
| sellerSku / SellerSKU | string | 条件 | 与 asin 二选一；优先读取 `sellerSku`，兼容 `SellerSKU`。 |

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| skipDepCheck | boolean | 否 | 默认 false；仅在外部流程已确认依赖时跳过安装检测，不绕过店铺授权。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 业务封装调用 `call_api.run` 时始终添加此选项，不读取或写入响应缓存。公共脚本仍可能创建空的 `.cache` 目录。 |
| --help / -h | CLI flag | 否 | 本地显示用法，不发起请求。 |

依赖检查返回 0 表示找到认证技能；返回 42 且 stderr 含 `DEPENDENCY_MISSING:` 表示缺失，应先安装 `linkfox-amazon-store-auth`。依赖检测支持兼容别名 `linkfox-amazon-spapi-auth`，并按环境变量、多宿主和 Hermes 目录查找安装位置。不得在本技能内自行获取店铺令牌。

业务脚本采用 `LINKFOX_TOOL_GATEWAY` → `STORE_API_BASE_URL` → `SPAPI_BASE_URL` → `https://tool-gateway.linkfox.com` 的地址优先级，以及两种 API Key 环境变量。会话头 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 由公共调用器透传。输出必须保存到当前工作目录的 `linkfox/`；请求前检查实际会话的 `data/` 目录可写，不可写时报错，不回退家目录、`/tmp` 或其他工作区。每次响应独立落盘，保留 `_meta.json` 和 `index.jsonl` 的会话记录。`SESSION_ID` 必须为单个非空目录名，不接受路径分隔符、绝对路径、`.` 或 `..`；保存失败会报错，不将仅标准输出的响应当作落盘成功。

#### 上游路径与 Query

转发 `GET catalog/v0/categories`，固定为 Catalog v0，不接受目录版本切换。Query 键大小写敏感，值经百分号编码；不传 `?`。

| 参数名 | 类型 | 必填 | 说明 |
|------|------|------|------|
| MarketplaceId | string | 是 | 单数、首字母大写，区别于 search/get 的 `marketplaceIds`。 |
| ASIN | string | 条件 | 与 SellerSKU 二选一。 |
| SellerSKU | string | 条件 | 与 ASIN 二选一；保留包含空格、斜线、中文等值的 URL 编码。 |

### 脚本输出与业务结果

#### 脚本输出

| 字段 | 类型 | 说明 |
|------|------|------|
| developerProxy | object | 网关完整响应；保留错误内容和未列出的扩展字段。 |
| resolvedPath | string | 实际转发的编码后相对路径。 |
| queryString | string | 实际发送的查询串，无 `?`。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态，连接失败为 null。 |
| categories | object / array / null | 网关正常响应且 Amazon `httpStatus=200` 时解析 `body`；空 body 为 null。该值是完整上游响应，不额外抽取或重塑内部对象。 |
| categoriesRaw | string | 仅 JSON 解析失败时保留原始 body，此时 `categories` 为 null。 |

Amazon 内部字段模式及类目、商品摘要、图片等嵌套资料随版本和数据集变化，以本接口官方 schema 与实际 `body` 为准，不将未返回的字段补齐或假定为成功。


#### 本地调用器补充字段

| 字段 | 类型 | 说明 |
|---|---|---|
| error | string | HTTP 或连接失败时可能返回的说明。 |
| details | string | 非 JSON HTTP 错误的原始响应内容。 |

## 接口：搜索目录商品（searchCatalogItems）

### 脚本输入与构参

#### 脚本 JSON 参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| sellerId | string | 是 | 已授权店铺 Seller ID，也作为 SKU 检索默认的 Query sellerId。 |
| region | string | 是 | `NA` / `EU` / `FE`。 |
| marketplaceIds / marketplaceId | string[] / string | 是 | 支持数组、逗号分隔字符串或单数别名；优先 `marketplaceIds`，最多一个站点，超出报错。 |
| keywords | string[] / string | 条件 | 与 identifiers 互斥，两组必须选一组；最多 20 个，字符串以逗号拆分。 |
| identifiers | string[] / string | 条件 | 与 keywords 互斥，最多 20 个；必须配 identifiersType。 |
| identifiersType | string | 条件 | `ASIN`、`EAN`、`GTIN`、`ISBN`、`JAN`、`MINSAN`、`SKU`、`UPC`；脚本去首尾空白并归一为大写。 |
| includedData | string[] / string | 否 | 所需目录数据集，下表列出数据集示例；字符串以逗号拆分。 |
| brandNames | string[] / string | 否 | 品牌筛选，用于限缩关键词搜索。 |
| classificationIds | string[] / string | 否 | 分类筛选，用于限缩关键词搜索。 |
| locale | string | 否 | 返回资料语言，不传则交由 Amazon 决定。 |
| keywordsLocale | string | 否 | 搜索词语言，不传则交由 Amazon 决定。 |
| pageSize | integer | 否 | 1～20，Amazon 默认 10；脚本未传时不主动填值，兼容整数字符串，拒绝布尔值、带小数部分或非有限数值，不静默截断。 |
| pageToken | string | 否 | 使用上次响应的分页 token，不自动翻页。 |
| catalogItemsVersion | string | 否 | 默认 `2022-04-01`，仅可选 `2020-12-01`。 |
| sellerIdForCatalog | string | 否 | 覆盖 Query 中的 sellerId；不改变外层已授权 sellerId。未覆盖且 identifiersType=SKU 时自动使用外层 sellerId。 |

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| skipDepCheck | boolean | 否 | 默认 false；仅在外部流程已确认依赖时跳过安装检测，不绕过店铺授权。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 业务封装调用 `call_api.run` 时始终添加此选项，不读取或写入响应缓存。公共脚本仍可能创建空的 `.cache` 目录。 |
| --help / -h | CLI flag | 否 | 本地显示用法，不发起请求。 |

依赖检查返回 0 表示找到认证技能；返回 42 且 stderr 含 `DEPENDENCY_MISSING:` 表示缺失，应先安装 `linkfox-amazon-store-auth`。依赖检测支持兼容别名 `linkfox-amazon-spapi-auth`，并按环境变量、多宿主和 Hermes 目录查找安装位置。不得在本技能内自行获取店铺令牌。

业务脚本采用 `LINKFOX_TOOL_GATEWAY` → `STORE_API_BASE_URL` → `SPAPI_BASE_URL` → `https://tool-gateway.linkfox.com` 的地址优先级，以及两种 API Key 环境变量。会话头 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 由公共调用器透传。输出必须保存到当前工作目录的 `linkfox/`；请求前检查实际会话的 `data/` 目录可写，不可写时报错，不回退家目录、`/tmp` 或其他工作区。每次响应独立落盘，保留 `_meta.json` 和 `index.jsonl` 的会话记录。`SESSION_ID` 必须为单个非空目录名，不接受路径分隔符、绝对路径、`.` 或 `..`；保存失败会报错，不将仅标准输出的响应当作落盘成功。

#### 上游路径与 Query

转发 `GET catalog/{version}/items`；`version` 为 `2022-04-01`（默认）或 `2020-12-01`。列表类值使用重复 Query 键，每个值独立编码，不改成未编码的拼接串。

| 参数名 | 类型 | 必填 | 说明 |
|------|------|------|------|
| marketplaceIds | string | 是 | 单个站点，键名为复数。 |
| keywords | string（重复键） | 条件 | 关键词检索，最多 20 个，与 identifiers 互斥。 |
| identifiers | string（重复键） | 条件 | 标识符检索，最多 20 个，与 keywords 互斥。 |
| identifiersType | string | 条件 | identifiers 非空时必传，枚举与脚本表一致。 |
| includedData | string（重复键） | 否 | 目录数据集。 |
| brandNames | string（重复键） | 否 | 品牌筛选。 |
| classificationIds | string（重复键） | 否 | 分类筛选。 |
| locale | string | 否 | 返回资料语言。 |
| keywordsLocale | string | 否 | 搜索词语言。 |
| sellerId | string | SKU 检索必填 | 默认用授权 sellerId，可由 sellerIdForCatalog 覆盖；不以此覆盖外层授权身份。 |
| pageSize | integer | 否 | 1～20，默认 10。 |
| pageToken | string | 否 | 原样取自响应并作为单个值编码，避免 `+`、`&`、`/` 等造成串参。 |

#### includedData 数据集（2022-04-01）

| 值 | 说明 |
|------|------|
| summaries | 商品标题等摘要。 |
| attributes | 商品属性。 |
| classifications | 商品分类。 |
| dimensions | 尺寸资料。 |
| identifiers | 商品标识。 |
| images | 商品图片。 |
| productTypes | 商品类型。 |
| relationships | 商品关系。 |
| salesRanks | 销售排名。 |
| vendorDetails | Vendor 资料。 |

上述为 2022-04-01 数据集示例；可用值与返回字段以所选 Amazon 版本 schema 为准。脚本不传 `includedData` 时不自行填充默认集，也不按该表硬编码过滤 `2020-12-01` 数据集。

### 脚本输出与业务结果

#### 脚本输出

| 字段 | 类型 | 说明 |
|------|------|------|
| developerProxy | object | 网关完整响应；保留错误内容和未列出的扩展字段。 |
| resolvedPath | string | 实际转发的编码后相对路径。 |
| queryString | string | 实际发送的查询串，无 `?`。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态，连接失败为 null。 |
| catalogItemsVersion | string | 实际使用的 `2022-04-01` 或 `2020-12-01`。 |
| catalogItems | object / array / null | 网关正常响应且 Amazon `httpStatus=200` 时解析 `body`；空 body 为 null。该值是完整上游响应，不额外抽取或重塑内部对象。 |
| catalogItemsRaw | string | 仅 JSON 解析失败时保留原始 body，此时 `catalogItems` 为 null。 |

Amazon 内部字段模式及类目、商品摘要、图片等嵌套资料随版本和数据集变化，以本接口官方 schema 与实际 `body` 为准，不将未返回的字段补齐或假定为成功。


#### 本地调用器补充字段

| 字段 | 类型 | 说明 |
|---|---|---|
| error | string | HTTP 或连接失败时可能返回的说明。 |
| details | string | 非 JSON HTTP 错误的原始响应内容。 |

## 接口：获取目录商品（getCatalogItem）

### 脚本输入与构参

#### 脚本 JSON 参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| sellerId | string | 是 | 已授权店铺 Seller ID。 |
| region | string | 是 | `NA` / `EU` / `FE`。 |
| asin | string | 是 | 商品 ASIN，作为独立 URL path 段编码。 |
| marketplaceIds / marketplaceId | string[] / string | 是 | 支持数组、逗号分隔字符串或单数别名；优先 `marketplaceIds`，最多一个站点。 |
| includedData | string[] / string | 否 | 所需目录数据集，字符串以逗号拆分；下表列出数据集示例。 |
| locale | string | 否 | 返回资料语言，不传则交由 Amazon 决定。 |
| catalogItemsVersion | string | 否 | 默认 `2022-04-01`，可选 `2020-12-01`。 |

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| skipDepCheck | boolean | 否 | 默认 false；仅在外部流程已确认依赖时跳过安装检测，不绕过店铺授权。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 业务封装调用 `call_api.run` 时始终添加此选项，不读取或写入响应缓存。公共脚本仍可能创建空的 `.cache` 目录。 |
| --help / -h | CLI flag | 否 | 本地显示用法，不发起请求。 |

依赖检查返回 0 表示找到认证技能；返回 42 且 stderr 含 `DEPENDENCY_MISSING:` 表示缺失，应先安装 `linkfox-amazon-store-auth`。依赖检测支持兼容别名 `linkfox-amazon-spapi-auth`，并按环境变量、多宿主和 Hermes 目录查找安装位置。不得在本技能内自行获取店铺令牌。

业务脚本采用 `LINKFOX_TOOL_GATEWAY` → `STORE_API_BASE_URL` → `SPAPI_BASE_URL` → `https://tool-gateway.linkfox.com` 的地址优先级，以及两种 API Key 环境变量。会话头 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 由公共调用器透传。输出必须保存到当前工作目录的 `linkfox/`；请求前检查实际会话的 `data/` 目录可写，不可写时报错，不回退家目录、`/tmp` 或其他工作区。每次响应独立落盘，保留 `_meta.json` 和 `index.jsonl` 的会话记录。`SESSION_ID` 必须为单个非空目录名，不接受路径分隔符、绝对路径、`.` 或 `..`；保存失败会报错，不将仅标准输出的响应当作落盘成功。

#### 上游路径与参数

转发 `GET catalog/{version}/items/{asin}`，`version` 为 `2022-04-01`（默认）或 `2020-12-01`；ASIN 作为独立 path 段去首尾空白、百分号编码，不能将其原样拼接为路径。

| 名称 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| asin | Path | string | 是 | 商品 ASIN。 |
| marketplaceIds | Query | string | 是 | 单个站点，键名为复数。 |
| includedData | Query | string（重复键） | 否 | 逐项编码并使用重复键。 |
| locale | Query | string | 否 | 返回资料语言。 |

#### includedData 数据集（2022-04-01）

| 值 | 说明 |
|------|------|
| summaries | 商品标题等摘要。 |
| attributes | 商品属性。 |
| classifications | 商品分类。 |
| dimensions | 尺寸资料。 |
| identifiers | 商品标识。 |
| images | 商品图片。 |
| productTypes | 商品类型。 |
| relationships | 商品关系。 |
| salesRanks | 销售排名。 |
| vendorDetails | Vendor 资料。 |

上述为 2022-04-01 数据集示例；可用值与返回字段以所选 Amazon 版本 schema 为准。脚本不传 `includedData` 时不自行填充默认集，也不按该表硬编码过滤 `2020-12-01` 数据集。

### 脚本输出与业务结果

#### 脚本输出

| 字段 | 类型 | 说明 |
|------|------|------|
| developerProxy | object | 网关完整响应；保留错误内容和未列出的扩展字段。 |
| resolvedPath | string | 实际转发的编码后相对路径。 |
| queryString | string | 实际发送的查询串，无 `?`。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态，连接失败为 null。 |
| catalogItemsVersion | string | 实际使用的 `2022-04-01` 或 `2020-12-01`。 |
| catalogItem | object / array / null | 网关正常响应且 Amazon `httpStatus=200` 时解析 `body`；空 body 为 null。该值是完整上游响应，不额外抽取或重塑内部对象。 |
| catalogItemRaw | string | 仅 JSON 解析失败时保留原始 body，此时 `catalogItem` 为 null。 |

Amazon 内部字段模式及类目、商品摘要、图片等嵌套资料随版本和数据集变化，以本接口官方 schema 与实际 `body` 为准，不将未返回的字段补齐或假定为成功。


#### 本地调用器补充字段

| 字段 | 类型 | 说明 |
|---|---|---|
| error | string | HTTP 或连接失败时可能返回的说明。 |
| details | string | 非 JSON HTTP 错误的原始响应内容。 |
