# 脚本输入、构参与本地输出

网关参数与响应定义见 [api.md](api.md)。本文件的本地输入、输出与上游构参不属于网关 DTO；只使用实际响应已有的业务字段。

共享脚本约定适用于本文件各操作；操作差异以对应小节为准。

## 接口：商品价格（getPricing）

### 脚本输入与构参

上游方法：`GET`；转发 path：`products/pricing/v0/price`。只传相对 path，区域主机由网关选择。

#### 脚本 JSON 参数与 CLI

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| sellerId | string | 是 | 已授权卖家 ID。 |
| region | string | 是 | `NA` / `EU` / `FE`。 |
| marketplaceId | string | 与 marketplaceIds 至少一个 | 映射 Query `MarketplaceId`，美国示例 `ATVPDKIKX0DER`。 |
| marketplaceIds | array[string] / string | 否 | 兼容别名；marketplaceId 优先，否则数组仅取首项，多于一个时 stderr 警告；也兼容非空字符串。 |
| itemType | string | 是 | 大小写敏感：`Asin` 或 `Sku`。 |
| asins | array[string] / string | itemType=Asin 时 | 至少 1 个、最多 20 个；脚本兼容单个字符串，去除首尾空白。 |
| skus | array[string] / string | itemType=Sku 时 | 至少 1 个、最多 20 个；脚本兼容单个字符串，去除首尾空白；另一组标识会被忽略并告警。 |
| itemCondition | string | 否 | 映射 ItemCondition；`New`、`Used`、`Collectible`、`Refurbished`、`Club`。 |
| offerType | string | 否 | `B2C` / `B2B`；不传通常 B2C，以上游为准。 |
| skipDepCheck | boolean | 否 | 默认 false；true 仅跳过本地安装检测，不绕过店铺授权。 |
| --inline | CLI flag | 否 | 强制完整打印，仍保存完整响应。 |
| --no-cache | CLI flag | 否 | CLI 兼容接受；业务封装始终向 run 传入此项，不读取或保存响应缓存。公共调用器可能建立空缓存目录，不代表启用缓存。 |

本地依赖检查返回 0 表示找到认证技能；返回 42 且 stderr 含 `DEPENDENCY_MISSING:` 表示缺失，应先安装 `linkfox-amazon-store-auth`，不得绕过依赖自行授权。`check_auth_dependency.py --json` 保留结构化输出，并兼容旧认证技能目录名及 OpenClaw / Hermes 安装路径与环境变量。

基础地址优先级为 `LINKFOX_TOOL_GATEWAY`、`STORE_API_BASE_URL`、`SPAPI_BASE_URL`，默认 `https://tool-gateway.linkfox.com`；密钥兼容 `LINKFOX_AGENT_API_KEY` 和 `LINKFOXAGENT_API_KEY`。保留 SESSION_ID、MESSAGE_ID、MODE_ID、APP_NAME 请求头。会话数据写入当前工作目录；`/tmp` 及其子目录禁止作为输出位置；SESSION_ID 或既有目录链接不得使实际 data 路径越出当前目录的 linkfox。请求前检查根目录和实际会话 data 目录是否可写，失败即报错，不回退家目录或临时目录。

#### Query 参数（写入 queryString）

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| MarketplaceId | string | 是 | 单个站点，勿与 Listings 的 marketplaceIds 混用。 |
| ItemType | string | 是 | `Asin` / `Sku`。 |
| Asins | 重复 string 键 | ItemType=Asin 时 | 最多 20 个；`Asins=A&Asins=B`，不是逗号拼接。 |
| Skus | 重复 string 键 | ItemType=Sku 时 | 最多 20 个；逐项 URL 编码后重复键拼接。 |
| ItemCondition | string | 否 | `New`、`Used`、`Collectible`、`Refurbished`、`Club`。 |
| OfferType | string | 否 | `B2C` / `B2B`，默认通常 B2C，以上游为准。 |

#### 权限与使用限制

需 Product Pricing 及相关角色；2022-05-01 能力可能还需应用内配置，以 Amazon 为准。默认速率约 0.5 req/s，burst 1，以实际账号配额和响应为准；注意上游 429，禁止自动并发试探。

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|------|------|------|
| developerProxy | object | 完整网关响应；错误时保留原始错误消息。 |
| resolvedPath | string | 实际编码后的资源路径。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败时 null。 |
| queryString | string | 实际发送的查询串，无问号。 |
| pricing | object / array / null | 外层正常且上游 httpStatus=200 时解析 body；解析失败为 null，未满足成功条件时不生成此字段。 |
| pricingRaw | string | 仅 JSON 解析失败时保留原始 body。 |

## 接口：竞争价格（getCompetitivePricing）

### 脚本输入与构参

上游方法：`GET`；转发 path：`products/pricing/v0/competitivePrice`。只传相对 path，区域主机由网关选择。

#### 脚本 JSON 参数与 CLI

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| sellerId | string | 是 | 已授权卖家 ID。 |
| region | string | 是 | `NA` / `EU` / `FE`。 |
| marketplaceId | string | 与 marketplaceIds 至少一个 | 映射 Query `MarketplaceId`，美国示例 `ATVPDKIKX0DER`。 |
| marketplaceIds | array[string] / string | 否 | 兼容别名；marketplaceId 优先，否则数组仅取首项，多于一个时 stderr 警告；也兼容非空字符串。 |
| itemType | string | 是 | 大小写敏感：`Asin` 或 `Sku`。 |
| asins | array[string] / string | itemType=Asin 时 | 至少 1 个、最多 20 个；脚本兼容单个字符串，去除首尾空白。 |
| skus | array[string] / string | itemType=Sku 时 | 至少 1 个、最多 20 个；脚本兼容单个字符串，去除首尾空白；另一组标识会被忽略并告警。 |
| customerType | string | 否 | 映射 CustomerType；`Consumer` / `Business`；不传通常为 Consumer，以上游为准。 |
| skipDepCheck | boolean | 否 | 默认 false；true 仅跳过本地安装检测，不绕过店铺授权。 |
| --inline | CLI flag | 否 | 强制完整打印，仍保存完整响应。 |
| --no-cache | CLI flag | 否 | CLI 兼容接受；业务封装始终向 run 传入此项，不读取或保存响应缓存。公共调用器可能建立空缓存目录，不代表启用缓存。 |

本地依赖检查返回 0 表示找到认证技能；返回 42 且 stderr 含 `DEPENDENCY_MISSING:` 表示缺失，应先安装 `linkfox-amazon-store-auth`，不得绕过依赖自行授权。`check_auth_dependency.py --json` 保留结构化输出，并兼容旧认证技能目录名及 OpenClaw / Hermes 安装路径与环境变量。

基础地址优先级为 `LINKFOX_TOOL_GATEWAY`、`STORE_API_BASE_URL`、`SPAPI_BASE_URL`，默认 `https://tool-gateway.linkfox.com`；密钥兼容 `LINKFOX_AGENT_API_KEY` 和 `LINKFOXAGENT_API_KEY`。保留 SESSION_ID、MESSAGE_ID、MODE_ID、APP_NAME 请求头。会话数据写入当前工作目录；`/tmp` 及其子目录禁止作为输出位置；SESSION_ID 或既有目录链接不得使实际 data 路径越出当前目录的 linkfox。请求前检查根目录和实际会话 data 目录是否可写，失败即报错，不回退家目录或临时目录。

#### Query 参数（写入 queryString）

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| MarketplaceId | string | 是 | 单个站点，勿与 Listings 的 marketplaceIds 混用。 |
| ItemType | string | 是 | `Asin` / `Sku`。 |
| Asins | 重复 string 键 | ItemType=Asin 时 | 最多 20 个；`Asins=A&Asins=B`，不是逗号拼接。 |
| Skus | 重复 string 键 | ItemType=Sku 时 | 最多 20 个；逐项 URL 编码后重复键拼接。 |
| CustomerType | string | 否 | `Consumer` / `Business`；不传通常为 Consumer，以上游为准。 |

getCompetitivePricing 没有 getPricing 的 ItemCondition 和 OfferType 参数，勿混用。

#### 权限与使用限制

需 Product Pricing 及相关角色；2022-05-01 能力可能还需应用内配置，以 Amazon 为准。默认速率约 0.5 req/s，burst 1，以实际账号配额和响应为准；注意上游 429，禁止自动并发试探。

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|------|------|------|
| developerProxy | object | 完整网关响应；错误时保留原始错误消息。 |
| resolvedPath | string | 实际编码后的资源路径。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败时 null。 |
| queryString | string | 实际发送的查询串，无问号。 |
| competitivePricing | object / array / null | 外层正常且上游 httpStatus=200 时解析 body；解析失败为 null，未满足成功条件时不生成此字段。 |
| competitivePricingRaw | string | 仅 JSON 解析失败时保留原始 body。 |

## 接口：单 SKU 报价（getListingOffers）

### 脚本输入与构参

上游方法：`GET`；转发 path：`products/pricing/v0/listings/{SellerSKU}/offers`。只传相对 path，区域主机由网关选择。

#### 脚本 JSON 参数与 CLI

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| sellerId | string | 是 | 已授权卖家 ID。 |
| region | string | 是 | `NA` / `EU` / `FE`。 |
| sku | string | 是 | 非空；对应 path 占位段，逐段百分号编码，使用 quote(..., safe="")；SKU 是卖家 SKU，非 ASIN。 |
| marketplaceId | string | 与 marketplaceIds 至少一个 | 映射 Query `MarketplaceId`，美国示例 `ATVPDKIKX0DER`。 |
| marketplaceIds | array[string] / string | 否 | 兼容别名；marketplaceId 优先，否则数组仅取首项，多于一个时 stderr 警告；也兼容非空字符串。 |
| itemCondition | string | 是 | `New`、`Used`、`Collectible`、`Refurbished`、`Club`。 |
| customerType | string | 否 | `Consumer` / `Business`；不传通常为 Consumer，以上游为准。 |
| skipDepCheck | boolean | 否 | 默认 false；true 仅跳过本地安装检测，不绕过店铺授权。 |
| --inline | CLI flag | 否 | 强制完整打印，仍保存完整响应。 |
| --no-cache | CLI flag | 否 | CLI 兼容接受；业务封装始终向 run 传入此项，不读取或保存响应缓存。公共调用器可能建立空缓存目录，不代表启用缓存。 |

本地依赖检查返回 0 表示找到认证技能；返回 42 且 stderr 含 `DEPENDENCY_MISSING:` 表示缺失，应先安装 `linkfox-amazon-store-auth`，不得绕过依赖自行授权。`check_auth_dependency.py --json` 保留结构化输出，并兼容旧认证技能目录名及 OpenClaw / Hermes 安装路径与环境变量。

基础地址优先级为 `LINKFOX_TOOL_GATEWAY`、`STORE_API_BASE_URL`、`SPAPI_BASE_URL`，默认 `https://tool-gateway.linkfox.com`；密钥兼容 `LINKFOX_AGENT_API_KEY` 和 `LINKFOXAGENT_API_KEY`。保留 SESSION_ID、MESSAGE_ID、MODE_ID、APP_NAME 请求头。会话数据写入当前工作目录；`/tmp` 及其子目录禁止作为输出位置；SESSION_ID 或既有目录链接不得使实际 data 路径越出当前目录的 linkfox。请求前检查根目录和实际会话 data 目录是否可写，失败即报错，不回退家目录或临时目录。

#### Query 参数（写入 queryString）

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| MarketplaceId | string | 是 | 单个站点。 |
| ItemCondition | string | 是 | `New`、`Used`、`Collectible`、`Refurbished`、`Club`。 |
| CustomerType | string | 否 | `Consumer` / `Business`；不传通常为 Consumer，以上游为准。 |

语义：返回单个目标在指定站点、成色下的较低报价信息（lowest priced offers），以 Amazon 返回为准。路径段须百分号编码，Query 各值也分别编码。

#### 权限与使用限制

需 Product Pricing 及相关角色；2022-05-01 能力可能还需应用内配置，以 Amazon 为准。默认速率约 1 req/s，burst 2，以实际账号配额和响应为准；注意上游 429，禁止自动并发试探。

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|------|------|------|
| developerProxy | object | 完整网关响应；错误时保留原始错误消息。 |
| resolvedPath | string | 实际编码后的资源路径。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败时 null。 |
| queryString | string | 实际发送的查询串，无问号。 |
| listingOffers | object / array / null | 外层正常且上游 httpStatus=200 时解析 body；解析失败为 null，未满足成功条件时不生成此字段。 |
| listingOffersRaw | string | 仅 JSON 解析失败时保留原始 body。 |

## 接口：单 ASIN 报价（getItemOffers）

### 脚本输入与构参

上游方法：`GET`；转发 path：`products/pricing/v0/items/{Asin}/offers`。只传相对 path，区域主机由网关选择。

#### 脚本 JSON 参数与 CLI

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| sellerId | string | 是 | 已授权卖家 ID。 |
| region | string | 是 | `NA` / `EU` / `FE`。 |
| asin | string | 是 | 非空 ASIN；对应 path 占位段，逐段百分号编码。 |
| marketplaceId | string | 与 marketplaceIds 至少一个 | 映射 Query `MarketplaceId`，美国示例 `ATVPDKIKX0DER`。 |
| marketplaceIds | array[string] / string | 否 | 兼容别名；marketplaceId 优先，否则数组仅取首项，多于一个时 stderr 警告；也兼容非空字符串。 |
| itemCondition | string | 是 | `New`、`Used`、`Collectible`、`Refurbished`、`Club`。 |
| customerType | string | 否 | `Consumer` / `Business`；不传通常为 Consumer，以上游为准。 |
| skipDepCheck | boolean | 否 | 默认 false；true 仅跳过本地安装检测，不绕过店铺授权。 |
| --inline | CLI flag | 否 | 强制完整打印，仍保存完整响应。 |
| --no-cache | CLI flag | 否 | CLI 兼容接受；业务封装始终向 run 传入此项，不读取或保存响应缓存。公共调用器可能建立空缓存目录，不代表启用缓存。 |

本地依赖检查返回 0 表示找到认证技能；返回 42 且 stderr 含 `DEPENDENCY_MISSING:` 表示缺失，应先安装 `linkfox-amazon-store-auth`，不得绕过依赖自行授权。`check_auth_dependency.py --json` 保留结构化输出，并兼容旧认证技能目录名及 OpenClaw / Hermes 安装路径与环境变量。

基础地址优先级为 `LINKFOX_TOOL_GATEWAY`、`STORE_API_BASE_URL`、`SPAPI_BASE_URL`，默认 `https://tool-gateway.linkfox.com`；密钥兼容 `LINKFOX_AGENT_API_KEY` 和 `LINKFOXAGENT_API_KEY`。保留 SESSION_ID、MESSAGE_ID、MODE_ID、APP_NAME 请求头。会话数据写入当前工作目录；`/tmp` 及其子目录禁止作为输出位置；SESSION_ID 或既有目录链接不得使实际 data 路径越出当前目录的 linkfox。请求前检查根目录和实际会话 data 目录是否可写，失败即报错，不回退家目录或临时目录。

#### Query 参数（写入 queryString）

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| MarketplaceId | string | 是 | 单个站点。 |
| ItemCondition | string | 是 | `New`、`Used`、`Collectible`、`Refurbished`、`Club`。 |
| CustomerType | string | 否 | `Consumer` / `Business`；不传通常为 Consumer，以上游为准。 |

语义：返回单个目标在指定站点、成色下的较低报价信息（lowest priced offers），以 Amazon 返回为准。路径段须百分号编码，Query 各值也分别编码。

#### 权限与使用限制

需 Product Pricing 及相关角色；2022-05-01 能力可能还需应用内配置，以 Amazon 为准。默认速率约 0.5 req/s，burst 1，以实际账号配额和响应为准；注意上游 429，禁止自动并发试探。

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|------|------|------|
| developerProxy | object | 完整网关响应；错误时保留原始错误消息。 |
| resolvedPath | string | 实际编码后的资源路径。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败时 null。 |
| queryString | string | 实际发送的查询串，无问号。 |
| itemOffers | object / array / null | 外层正常且上游 httpStatus=200 时解析 body；解析失败为 null，未满足成功条件时不生成此字段。 |
| itemOffersRaw | string | 仅 JSON 解析失败时保留原始 body。 |

## 接口：批量 ASIN 报价（getItemOffersBatch）

### 脚本输入与构参

上游方法：`POST`；转发 path：`batches/products/pricing/v0/itemOffers`。只传相对 path，区域主机由网关选择。

#### 脚本 JSON 参数与 CLI

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| sellerId | string | 是 | 已授权卖家 ID。 |
| region | string | 是 | `NA` / `EU` / `FE`。 |
| requests | array[object] | 是 | 非空，1～20 条子请求；字段见下表。 |
| useAmazonRequestShape | boolean | 否 | 默认 false；true 时直接透传官方原始 requests 数组，仍检查非空与条数，不再次展开或改写。 |
| skipDepCheck | boolean | 否 | 默认 false；true 仅跳过本地安装检测，不绕过店铺授权。 |
| --inline | CLI flag | 否 | 强制完整打印，仍保存完整响应。 |
| --no-cache | CLI flag | 否 | CLI 兼容接受；业务封装始终向 run 传入此项，不读取或保存响应缓存。公共调用器可能建立空缓存目录，不代表启用缓存。 |

本地依赖检查返回 0 表示找到认证技能；返回 42 且 stderr 含 `DEPENDENCY_MISSING:` 表示缺失，应先安装 `linkfox-amazon-store-auth`，不得绕过依赖自行授权。`check_auth_dependency.py --json` 保留结构化输出，并兼容旧认证技能目录名及 OpenClaw / Hermes 安装路径与环境变量。

基础地址优先级为 `LINKFOX_TOOL_GATEWAY`、`STORE_API_BASE_URL`、`SPAPI_BASE_URL`，默认 `https://tool-gateway.linkfox.com`；密钥兼容 `LINKFOX_AGENT_API_KEY` 和 `LINKFOXAGENT_API_KEY`。保留 SESSION_ID、MESSAGE_ID、MODE_ID、APP_NAME 请求头。会话数据写入当前工作目录；`/tmp` 及其子目录禁止作为输出位置；SESSION_ID 或既有目录链接不得使实际 data 路径越出当前目录的 linkfox。请求前检查根目录和实际会话 data 目录是否可写，失败即报错，不回退家目录或临时目录。

#### Amazon body 与子请求

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| requests | array[object] | 是 | Amazon body 根字段；网关 body 是该对象的 JSON 字符串。 |

简化输入字段：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| requests[].asin | string | 简化模式必填 | 非空；编码后填入 uri 的资源路径段。 |
| requests[].marketplaceId | string | 简化模式必填 | 非空；映射 MarketplaceId。 |
| requests[].itemCondition | string | 简化模式必填 | `New`、`Used`、`Collectible`、`Refurbished`、`Club`；映射 ItemCondition。 |
| requests[].customerType | string | 否 | `Consumer` / `Business`；不传通常为 Consumer，以上游为准。 映射 CustomerType。 |
| requests[].headers | object | 否 | 子请求 headers 原样保留。 |

官方原始子请求字段（useAmazonRequestShape=true，或简化输入展开后）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| requests[].uri | string | 是 | `/products/pricing/v0/items/{Asin}/offers`，以 / 开头，不含 Query。 |
| requests[].method | string | 是 | `GET`，简化模式自动补充。 |
| requests[].MarketplaceId | string | 是 | 单站点。 |
| requests[].ItemCondition | string | 是 | `New`、`Used`、`Collectible`、`Refurbished`、`Club`。 |
| requests[].CustomerType | string | 否 | `Consumer` / `Business`；不传通常为 Consumer，以上游为准。 |
| requests[].headers | object | 否 | 子请求头，原样透传。 |

#### 权限与使用限制

需 Product Pricing 及相关角色；2022-05-01 能力可能还需应用内配置，以 Amazon 为准。默认速率约 0.1 req/s，burst 1，以实际账号配额和响应为准；注意上游 429，禁止自动并发试探。

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|------|------|------|
| developerProxy | object | 完整网关响应；错误时保留原始错误消息。 |
| resolvedPath | string | 实际编码后的资源路径。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败时 null。 |
| requestBody | object | 已组装并发送的 Amazon JSON 对象；错误时仍保留。 |
| itemOffersBatch | object / array / null | 外层正常且上游 httpStatus=200 时解析 body；解析失败为 null，未满足成功条件时不生成此字段。 |
| itemOffersBatchRaw | string | 仅 JSON 解析失败时保留原始 body。 |

批量业务对象内需逐条核对状态、错误和对应商品，不能将整批 200 当作所有子请求成功。子响应完整结构以 Amazon 实际返回为准，原样保留响应对象，不虚构字段。

## 接口：批量 SKU 报价（getListingOffersBatch）

### 脚本输入与构参

上游方法：`POST`；转发 path：`batches/products/pricing/v0/listingOffers`。只传相对 path，区域主机由网关选择。

#### 脚本 JSON 参数与 CLI

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| sellerId | string | 是 | 已授权卖家 ID。 |
| region | string | 是 | `NA` / `EU` / `FE`。 |
| requests | array[object] | 是 | 非空，1～20 条子请求；字段见下表。 |
| useAmazonRequestShape | boolean | 否 | 默认 false；true 时直接透传官方原始 requests 数组，仍检查非空与条数，不再次展开或改写。 |
| skipDepCheck | boolean | 否 | 默认 false；true 仅跳过本地安装检测，不绕过店铺授权。 |
| --inline | CLI flag | 否 | 强制完整打印，仍保存完整响应。 |
| --no-cache | CLI flag | 否 | CLI 兼容接受；业务封装始终向 run 传入此项，不读取或保存响应缓存。公共调用器可能建立空缓存目录，不代表启用缓存。 |

本地依赖检查返回 0 表示找到认证技能；返回 42 且 stderr 含 `DEPENDENCY_MISSING:` 表示缺失，应先安装 `linkfox-amazon-store-auth`，不得绕过依赖自行授权。`check_auth_dependency.py --json` 保留结构化输出，并兼容旧认证技能目录名及 OpenClaw / Hermes 安装路径与环境变量。

基础地址优先级为 `LINKFOX_TOOL_GATEWAY`、`STORE_API_BASE_URL`、`SPAPI_BASE_URL`，默认 `https://tool-gateway.linkfox.com`；密钥兼容 `LINKFOX_AGENT_API_KEY` 和 `LINKFOXAGENT_API_KEY`。保留 SESSION_ID、MESSAGE_ID、MODE_ID、APP_NAME 请求头。会话数据写入当前工作目录；`/tmp` 及其子目录禁止作为输出位置；SESSION_ID 或既有目录链接不得使实际 data 路径越出当前目录的 linkfox。请求前检查根目录和实际会话 data 目录是否可写，失败即报错，不回退家目录或临时目录。

#### Amazon body 与子请求

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| requests | array[object] | 是 | Amazon body 根字段；网关 body 是该对象的 JSON 字符串。 |

简化输入字段：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| requests[].sku | string | 简化模式必填 | 非空；编码后填入 uri 的资源路径段。 |
| requests[].marketplaceId | string | 简化模式必填 | 非空；映射 MarketplaceId。 |
| requests[].itemCondition | string | 简化模式必填 | `New`、`Used`、`Collectible`、`Refurbished`、`Club`；映射 ItemCondition。 |
| requests[].customerType | string | 否 | `Consumer` / `Business`；不传通常为 Consumer，以上游为准。 映射 CustomerType。 |
| requests[].headers | object | 否 | 子请求 headers 原样保留。 |

官方原始子请求字段（useAmazonRequestShape=true，或简化输入展开后）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| requests[].uri | string | 是 | `/products/pricing/v0/listings/{SellerSKU}/offers`，以 / 开头，不含 Query。 |
| requests[].method | string | 是 | `GET`，简化模式自动补充。 |
| requests[].MarketplaceId | string | 是 | 单站点。 |
| requests[].ItemCondition | string | 是 | `New`、`Used`、`Collectible`、`Refurbished`、`Club`。 |
| requests[].CustomerType | string | 否 | `Consumer` / `Business`；不传通常为 Consumer，以上游为准。 |
| requests[].headers | object | 否 | 子请求头，原样透传。 |

#### 权限与使用限制

需 Product Pricing 及相关角色；2022-05-01 能力可能还需应用内配置，以 Amazon 为准。默认速率约 0.5 req/s，burst 1，以实际账号配额和响应为准；注意上游 429，禁止自动并发试探。

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|------|------|------|
| developerProxy | object | 完整网关响应；错误时保留原始错误消息。 |
| resolvedPath | string | 实际编码后的资源路径。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败时 null。 |
| requestBody | object | 已组装并发送的 Amazon JSON 对象；错误时仍保留。 |
| listingOffersBatch | object / array / null | 外层正常且上游 httpStatus=200 时解析 body；解析失败为 null，未满足成功条件时不生成此字段。 |
| listingOffersBatchRaw | string | 仅 JSON 解析失败时保留原始 body。 |

批量业务对象内需逐条核对状态、错误和对应商品，不能将整批 200 当作所有子请求成功。子响应完整结构以 Amazon 实际返回为准，原样保留响应对象，不虚构字段。

## 接口：预期 Featured Offer 价格（getFeaturedOfferExpectedPriceBatch）

### 脚本输入与构参

上游方法：`POST`；转发 path：`batches/products/pricing/2022-05-01/offer/featuredOfferExpectedPrice`。只传相对 path，区域主机由网关选择。

#### 脚本 JSON 参数与 CLI

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| sellerId | string | 是 | 已授权卖家 ID。 |
| region | string | 是 | `NA` / `EU` / `FE`。 |
| requests | array[object] | 是 | 非空，1～40 条子请求；字段见下表。 |
| useAmazonRequestShape | boolean | 否 | 默认 false；true 时直接透传官方原始 requests 数组，仍检查非空与条数，不再次展开或改写。 |
| skipDepCheck | boolean | 否 | 默认 false；true 仅跳过本地安装检测，不绕过店铺授权。 |
| --inline | CLI flag | 否 | 强制完整打印，仍保存完整响应。 |
| --no-cache | CLI flag | 否 | CLI 兼容接受；业务封装始终向 run 传入此项，不读取或保存响应缓存。公共调用器可能建立空缓存目录，不代表启用缓存。 |

本地依赖检查返回 0 表示找到认证技能；返回 42 且 stderr 含 `DEPENDENCY_MISSING:` 表示缺失，应先安装 `linkfox-amazon-store-auth`，不得绕过依赖自行授权。`check_auth_dependency.py --json` 保留结构化输出，并兼容旧认证技能目录名及 OpenClaw / Hermes 安装路径与环境变量。

基础地址优先级为 `LINKFOX_TOOL_GATEWAY`、`STORE_API_BASE_URL`、`SPAPI_BASE_URL`，默认 `https://tool-gateway.linkfox.com`；密钥兼容 `LINKFOX_AGENT_API_KEY` 和 `LINKFOXAGENT_API_KEY`。保留 SESSION_ID、MESSAGE_ID、MODE_ID、APP_NAME 请求头。会话数据写入当前工作目录；`/tmp` 及其子目录禁止作为输出位置；SESSION_ID 或既有目录链接不得使实际 data 路径越出当前目录的 linkfox。请求前检查根目录和实际会话 data 目录是否可写，失败即报错，不回退家目录或临时目录。

#### Amazon body 与子请求

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| requests | array[object] | 是 | Amazon body 根字段；网关 body 是该对象的 JSON 字符串。 |

简化输入字段：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| requests[].marketplaceId | string | 是 | 非空站点 ID。 |
| requests[].sku | string | 是 | 非空卖家 SKU。 |
| requests[].segment | object | 是 | FOEP 细分场景，须符合 Amazon 模型（地理、配送等）；脚本检查为对象，内部字段以上游模型和实际输入为准。 |

官方原始子请求字段（useAmazonRequestShape=true，或简化输入展开后）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| requests[].uri | string | 是 | `/products/pricing/2022-05-01/offer/featuredOfferExpectedPrice`，简化模式补充。 |
| requests[].method | string | 是 | `POST`，简化模式补充。 |
| requests[].marketplaceId | string | 是 | 非空站点 ID。 |
| requests[].sku | string | 是 | 非空卖家 SKU。 |
| requests[].segment | object | 是 | FOEP 细分场景，须符合 Amazon 模型（地理、配送等）；脚本检查为对象，内部字段以上游模型和实际输入为准。 |

#### 权限与使用限制

需 Product Pricing 及相关角色；2022-05-01 能力可能还需应用内配置，以 Amazon 为准。默认速率约 0.033 req/s，burst 1，以实际账号配额和响应为准；注意上游 429，禁止自动并发试探。

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|------|------|------|
| developerProxy | object | 完整网关响应；错误时保留原始错误消息。 |
| resolvedPath | string | 实际编码后的资源路径。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败时 null。 |
| requestBody | object | 已组装并发送的 Amazon JSON 对象；错误时仍保留。 |
| featuredOfferExpectedPriceBatch | object / array / null | 外层正常且上游 httpStatus=200 时解析 body；解析失败为 null，未满足成功条件时不生成此字段。 |
| featuredOfferExpectedPriceBatchRaw | string | 仅 JSON 解析失败时保留原始 body。 |

批量业务对象内需逐条核对状态、错误和对应商品，不能将整批 200 当作所有子请求成功。子响应完整结构以 Amazon 实际返回为准，原样保留响应对象，不虚构字段。

## 接口：竞争摘要（getCompetitiveSummary）

### 脚本输入与构参

上游方法：`POST`；转发 path：`batches/products/pricing/2022-05-01/items/competitiveSummary`。只传相对 path，区域主机由网关选择。

#### 脚本 JSON 参数与 CLI

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| sellerId | string | 是 | 已授权卖家 ID。 |
| region | string | 是 | `NA` / `EU` / `FE`。 |
| requests | array[object] | 是 | 非空，1～20 条子请求；字段见下表。 |
| useAmazonRequestShape | boolean | 否 | 默认 false；true 时直接透传官方原始 requests 数组，仍检查非空与条数，不再次展开或改写。 |
| skipDepCheck | boolean | 否 | 默认 false；true 仅跳过本地安装检测，不绕过店铺授权。 |
| --inline | CLI flag | 否 | 强制完整打印，仍保存完整响应。 |
| --no-cache | CLI flag | 否 | CLI 兼容接受；业务封装始终向 run 传入此项，不读取或保存响应缓存。公共调用器可能建立空缓存目录，不代表启用缓存。 |

本地依赖检查返回 0 表示找到认证技能；返回 42 且 stderr 含 `DEPENDENCY_MISSING:` 表示缺失，应先安装 `linkfox-amazon-store-auth`，不得绕过依赖自行授权。`check_auth_dependency.py --json` 保留结构化输出，并兼容旧认证技能目录名及 OpenClaw / Hermes 安装路径与环境变量。

基础地址优先级为 `LINKFOX_TOOL_GATEWAY`、`STORE_API_BASE_URL`、`SPAPI_BASE_URL`，默认 `https://tool-gateway.linkfox.com`；密钥兼容 `LINKFOX_AGENT_API_KEY` 和 `LINKFOXAGENT_API_KEY`。保留 SESSION_ID、MESSAGE_ID、MODE_ID、APP_NAME 请求头。会话数据写入当前工作目录；`/tmp` 及其子目录禁止作为输出位置；SESSION_ID 或既有目录链接不得使实际 data 路径越出当前目录的 linkfox。请求前检查根目录和实际会话 data 目录是否可写，失败即报错，不回退家目录或临时目录。

#### Amazon body 与子请求

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| requests | array[object] | 是 | Amazon body 根字段；网关 body 是该对象的 JSON 字符串。 |

简化输入字段：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| requests[].asin | string | 是 | 非空 ASIN。 |
| requests[].marketplaceId | string | 是 | 非空站点 ID。 |
| requests[].includedData | array[string] | 是 | 非空字符串数组，如 featuredBuyingOptions；请求最低价数据时包含 lowestPricedOffers。 |
| requests[].lowestPricedOffersInputs | array[object] | 条件 | includedData 含 lowestPricedOffers 时需要；其余情况可选，脚本原样保留，内部模型以 Amazon 为准。 |

官方原始子请求字段（useAmazonRequestShape=true，或简化输入展开后）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| requests[].uri | string | 是 | `/products/pricing/2022-05-01/items/competitiveSummary`，简化模式补充。 |
| requests[].method | string | 是 | `POST`，简化模式补充。 |
| requests[].asin | string | 是 | 非空 ASIN。 |
| requests[].marketplaceId | string | 是 | 非空站点 ID。 |
| requests[].includedData | array[string] | 是 | 非空字符串数组，如 featuredBuyingOptions；请求最低价数据时包含 lowestPricedOffers。 |
| requests[].lowestPricedOffersInputs | array[object] | 条件 | includedData 含 lowestPricedOffers 时需要；其余情况可选，脚本原样保留，内部模型以 Amazon 为准。 |

#### 权限与使用限制

需 Product Pricing 及相关角色；2022-05-01 能力可能还需应用内配置，以 Amazon 为准。默认速率约 0.033 req/s，burst 1，以实际账号配额和响应为准；注意上游 429，禁止自动并发试探。

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|------|------|------|
| developerProxy | object | 完整网关响应；错误时保留原始错误消息。 |
| resolvedPath | string | 实际编码后的资源路径。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败时 null。 |
| requestBody | object | 已组装并发送的 Amazon JSON 对象；错误时仍保留。 |
| competitiveSummary | object / array / null | 外层正常且上游 httpStatus=200 时解析 body；解析失败为 null，未满足成功条件时不生成此字段。 |
| competitiveSummaryRaw | string | 仅 JSON 解析失败时保留原始 body。 |

批量业务对象内需逐条核对状态、错误和对应商品，不能将整批 200 当作所有子请求成功。子响应完整结构以 Amazon 实际返回为准，原样保留响应对象，不虚构字段。
