# 脚本输入、构参与本地结果

profileId 接收 Long 范围内的正整数或十进制数字字符串，发送到网关时为 integer；不接受布尔值、小数、零、负数或越界值。

网关接口定义见 [sb-v4.md](sb-v4.md)。以下表格描述脚本参数、构参或本地解析行为；不作为网关DTO或上游完整schema。

## 接口：SB V4 创建广告组

### 脚本输入与构参

| 转发属性 | 本操作约定 |
|---|---|
| method | POST |
| path | sb/v4/adGroups |
| contentType | application/vnd.sbadgroupresource.v4+json |
| accept | application/vnd.sbadgroupresource.v4+json |

#### 脚本 JSON 参数与选项

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| profileId | integer/string | 是 | 从广告授权技能解析，不能要求用户报数字。 |
| region | string | 是 | NA / EU / FE。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已完成依赖检测时使用，不绕过授权。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存响应。 |
| --no-cache | CLI flag | 否 | 业务调用始终附加；响应缓存关闭。公共调用器会建立空缓存目录，但不读写响应缓存。 |
| payload | object / array | 是 | Amazon 原生请求体；不自行改写字段或推定未记录的枚举；作为 body JSON 字符串发送。 |

依赖检测为本地文件检查：0 表示存在认证技能；42 且 stderr 含 `DEPENDENCY_MISSING:` 时先安装 `linkfox-amazon-ads-auth`。认证与运行限制见 [总览](../api.md)。

SB 版本边界见 [共存规则](sb-coexistence.md)；V3 只兼容 Legacy，已知多广告组活动拒绝；不自动回落其他版本。

### 脚本输出与解析

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| success | boolean | 查询或写操作处理状态；批量逐项结果仍须检查。 |
| transportHttpStatus | integer / null | 失败时保留的 LinkFox 外层状态；连接失败为 null。 |
| error | string | 失败原因；不自动重试。 |
| details | object / string / null | 网关错误原始内容。 |
| httpStatus | integer / null | 错误或写入时保留上游状态。 |
| body | string / null | 错误时保留上游原文。 |
| data | object / array / string | 解析后的 Amazon 批量结果；无法解析时保留原文，不把 HTTP 成功等同所有实体成功。 |
| apiVersion | string | V3 / V4，表示 CLI 入口/结构意图。 |
| amazonResourceVersion | string | V3 / V4 / V3_SHARED_TARGETING / SHARED_TARGETING / SHARED；与 apiVersion 不同不是回落。 |


## 接口：SB V4 创建广告

### 脚本输入与构参

| 转发属性 | 本操作约定 |
|---|---|
| method | POST |
| path | sb/v4/ads/{adType} |
| contentType | application/vnd.sbadresource.v4+json |
| accept | application/vnd.sbadresource.v4+json |

#### 脚本 JSON 参数与选项

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| profileId | integer/string | 是 | 从广告授权技能解析，不能要求用户报数字。 |
| region | string | 是 | NA / EU / FE。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已完成依赖检测时使用，不绕过授权。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存响应。 |
| --no-cache | CLI flag | 否 | 业务调用始终附加；响应缓存关闭。公共调用器会建立空缓存目录，但不读写响应缓存。 |
| payload | object / array | 是 | Amazon 原生请求体；不自行改写字段或推定未记录的枚举；作为 body JSON 字符串发送。 |
| adType | string | 是 | autoCollection / manualCollection / brandVideo / video / productCollection / productCollectionExtended / storeSpotlight；非法报 SB_INVALID_AD_TYPE。 |

依赖检测为本地文件检查：0 表示存在认证技能；42 且 stderr 含 `DEPENDENCY_MISSING:` 时先安装 `linkfox-amazon-ads-auth`。认证与运行限制见 [总览](../api.md)。

SB 版本边界见 [共存规则](sb-coexistence.md)；V3 只兼容 Legacy，已知多广告组活动拒绝；不自动回落其他版本。

### 脚本输出与解析

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| success | boolean | 查询或写操作处理状态；批量逐项结果仍须检查。 |
| transportHttpStatus | integer / null | 失败时保留的 LinkFox 外层状态；连接失败为 null。 |
| error | string | 失败原因；不自动重试。 |
| details | object / string / null | 网关错误原始内容。 |
| httpStatus | integer / null | 错误或写入时保留上游状态。 |
| body | string / null | 错误时保留上游原文。 |
| data | object / array / string | 解析后的 Amazon 批量结果；无法解析时保留原文，不把 HTTP 成功等同所有实体成功。 |
| apiVersion | string | V3 / V4，表示 CLI 入口/结构意图。 |
| amazonResourceVersion | string | V3 / V4 / V3_SHARED_TARGETING / SHARED_TARGETING / SHARED；与 apiVersion 不同不是回落。 |


## 接口：SB V4 创建预算规则

### 脚本输入与构参

| 转发属性 | 本操作约定 |
|---|---|
| method | POST |
| path | sb/budgetRules |
| contentType | application/json |
| accept | application/json |

#### 脚本 JSON 参数与选项

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| profileId | integer/string | 是 | 从广告授权技能解析，不能要求用户报数字。 |
| region | string | 是 | NA / EU / FE。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已完成依赖检测时使用，不绕过授权。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存响应。 |
| --no-cache | CLI flag | 否 | 业务调用始终附加；响应缓存关闭。公共调用器会建立空缓存目录，但不读写响应缓存。 |
| payload | object / array | 是 | Amazon 原生请求体；不自行改写字段或推定未记录的枚举；作为 body JSON 字符串发送；SB 预算规则子字段按 Amazon 原生请求要求传入，不据 SP/SD 结构推定。 |

依赖检测为本地文件检查：0 表示存在认证技能；42 且 stderr 含 `DEPENDENCY_MISSING:` 时先安装 `linkfox-amazon-ads-auth`。认证与运行限制见 [总览](../api.md)。

SB 版本边界见 [共存规则](sb-coexistence.md)；V3 只兼容 Legacy，已知多广告组活动拒绝；不自动回落其他版本。

### 脚本输出与解析

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| success | boolean | 查询或写操作处理状态；批量逐项结果仍须检查。 |
| transportHttpStatus | integer / null | 失败时保留的 LinkFox 外层状态；连接失败为 null。 |
| error | string | 失败原因；不自动重试。 |
| details | object / string / null | 网关错误原始内容。 |
| httpStatus | integer / null | 错误或写入时保留上游状态。 |
| body | string / null | 错误时保留上游原文。 |
| data | object / array / string | 解析后的 Amazon 批量结果；无法解析时保留原文，不把 HTTP 成功等同所有实体成功。 |
| apiVersion | string | V3 / V4，表示 CLI 入口/结构意图。 |
| amazonResourceVersion | string | V3 / V4 / V3_SHARED_TARGETING / SHARED_TARGETING / SHARED；与 apiVersion 不同不是回落。 |


## 接口：SB V4 创建广告活动

### 脚本输入与构参

| 转发属性 | 本操作约定 |
|---|---|
| method | POST |
| path | sb/v4/campaigns |
| contentType | application/vnd.sbcampaignresource.v4+json |
| accept | application/vnd.sbcampaignresource.v4+json |

#### 脚本 JSON 参数与选项

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| profileId | integer/string | 是 | 从广告授权技能解析，不能要求用户报数字。 |
| region | string | 是 | NA / EU / FE。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已完成依赖检测时使用，不绕过授权。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存响应。 |
| --no-cache | CLI flag | 否 | 业务调用始终附加；响应缓存关闭。公共调用器会建立空缓存目录，但不读写响应缓存。 |
| payload | object / array | 是 | Amazon 原生请求体；不自行改写字段或推定未记录的枚举；作为 body JSON 字符串发送。 |

依赖检测为本地文件检查：0 表示存在认证技能；42 且 stderr 含 `DEPENDENCY_MISSING:` 时先安装 `linkfox-amazon-ads-auth`。认证与运行限制见 [总览](../api.md)。

SB 版本边界见 [共存规则](sb-coexistence.md)；V3 只兼容 Legacy，已知多广告组活动拒绝；不自动回落其他版本。

### 脚本输出与解析

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| success | boolean | 查询或写操作处理状态；批量逐项结果仍须检查。 |
| transportHttpStatus | integer / null | 失败时保留的 LinkFox 外层状态；连接失败为 null。 |
| error | string | 失败原因；不自动重试。 |
| details | object / string / null | 网关错误原始内容。 |
| httpStatus | integer / null | 错误或写入时保留上游状态。 |
| body | string / null | 错误时保留上游原文。 |
| data | object / array / string | 解析后的 Amazon 批量结果；无法解析时保留原文，不把 HTTP 成功等同所有实体成功。 |
| apiVersion | string | V3 / V4，表示 CLI 入口/结构意图。 |
| amazonResourceVersion | string | V3 / V4 / V3_SHARED_TARGETING / SHARED_TARGETING / SHARED；与 apiVersion 不同不是回落。 |


## 接口：SB V4 创建创意

### 脚本输入与构参

| 转发属性 | 本操作约定 |
|---|---|
| method | POST |
| path | sb/ads/creatives/{creativeType} |
| contentType | application/vnd.sbAdCreativeResource.v4+json |
| accept | application/vnd.sbAdCreativeResource.v4+json |

#### 脚本 JSON 参数与选项

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| profileId | integer/string | 是 | 从广告授权技能解析，不能要求用户报数字。 |
| region | string | 是 | NA / EU / FE。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已完成依赖检测时使用，不绕过授权。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存响应。 |
| --no-cache | CLI flag | 否 | 业务调用始终附加；响应缓存关闭。公共调用器会建立空缓存目录，但不读写响应缓存。 |
| payload | object / array | 是 | Amazon 原生请求体；不自行改写字段或推定未记录的枚举；作为 body JSON 字符串发送。 |
| creativeType | string | 是 | productCollection / productCollectionExtended / storeSpotlight / video / brandVideo；非法报 SB_INVALID_CREATIVE_TYPE。 |
| payload.adId | string / number | 按原生操作 | 目标广告 ID |
| payload.creative | object | 按原生操作 | 新版本素材 |
| payload.creative.asins | array<string> | 按原生创意 | 商品 ASIN |
| payload.creative.headline | string | 按原生创意 | 标题 |

依赖检测为本地文件检查：0 表示存在认证技能；42 且 stderr 含 `DEPENDENCY_MISSING:` 时先安装 `linkfox-amazon-ads-auth`。认证与运行限制见 [总览](../api.md)。

SB 版本边界见 [共存规则](sb-coexistence.md)；V3 只兼容 Legacy，已知多广告组活动拒绝；不自动回落其他版本。

### 脚本输出与解析

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| success | boolean | 查询或写操作处理状态；批量逐项结果仍须检查。 |
| transportHttpStatus | integer / null | 失败时保留的 LinkFox 外层状态；连接失败为 null。 |
| error | string | 失败原因；不自动重试。 |
| details | object / string / null | 网关错误原始内容。 |
| httpStatus | integer / null | 错误或写入时保留上游状态。 |
| body | string / null | 错误时保留上游原文。 |
| data | object / array / string | 解析后的 Amazon 批量结果；无法解析时保留原文，不把 HTTP 成功等同所有实体成功。 |
| apiVersion | string | V3 / V4，表示 CLI 入口/结构意图。 |
| amazonResourceVersion | string | V3 / V4 / V3_SHARED_TARGETING / SHARED_TARGETING / SHARED；与 apiVersion 不同不是回落。 |


## 接口：SB V4 创建关键词

### 脚本输入与构参

| 转发属性 | 本操作约定 |
|---|---|
| method | POST |
| path | sb/keywords |
| contentType | application/json |
| accept | application/vnd.sbkeywordresponse.v3+json |

#### 脚本 JSON 参数与选项

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| profileId | integer/string | 是 | 从广告授权技能解析，不能要求用户报数字。 |
| region | string | 是 | NA / EU / FE。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已完成依赖检测时使用，不绕过授权。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存响应。 |
| --no-cache | CLI flag | 否 | 业务调用始终附加；响应缓存关闭。公共调用器会建立空缓存目录，但不读写响应缓存。 |
| campaignStructure | string | 否 | V3 本地保护：MULTI_AD_GROUP 拒绝；LEGACY 用于声明已确认的历史结构。 |
| isMultiAdGroupsEnabled | boolean / string / number | 否 | V3 中 true、1、true/yes/y/on 字符串均拒绝；递归检查 payload；保护标志本身不作为查询参数。 |
| payload | object / array | 是 | Amazon 原生请求体；不自行改写字段或推定未记录的枚举；作为 body JSON 字符串发送。 |
| payload[].keywordId | number / string | 按原生更新要求 | 关键词 ID，更新示例使用此字段 |
| payload[].campaignId | number / string | 按原生要求 | 活动 ID |
| payload[].adGroupId | number / string | 按原生要求 | 广告组 ID |
| payload[].bid | number | 按原生要求 | 出价，更新示例为 1.2 |

依赖检测为本地文件检查：0 表示存在认证技能；42 且 stderr 含 `DEPENDENCY_MISSING:` 时先安装 `linkfox-amazon-ads-auth`。认证与运行限制见 [总览](../api.md)。

SB 版本边界见 [共存规则](sb-coexistence.md)；V3 只兼容 Legacy，已知多广告组活动拒绝；不自动回落其他版本。

关键词创建/更新及定向创建最多 100 个；定向更新的批量上限按上游实际校验处理，不套用其他操作的限制。

V3 共享入口的 media 约定：GET 不显式指定 Accept，创建/更新使用 application/json 且不显式指定 Accept；V4 入口使用上表 Accept。两者路径相同，结构意图和返回版本标记不同。

### 脚本输出与解析

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| success | boolean | 查询或写操作处理状态；批量逐项结果仍须检查。 |
| transportHttpStatus | integer / null | 失败时保留的 LinkFox 外层状态；连接失败为 null。 |
| error | string | 失败原因；不自动重试。 |
| details | object / string / null | 网关错误原始内容。 |
| httpStatus | integer / null | 错误或写入时保留上游状态。 |
| body | string / null | 错误时保留上游原文。 |
| data | object / array / string | 解析后的 Amazon 批量结果；无法解析时保留原文，不把 HTTP 成功等同所有实体成功。 |
| apiVersion | string | V3 / V4，表示 CLI 入口/结构意图。 |
| amazonResourceVersion | string | V3 / V4 / V3_SHARED_TARGETING / SHARED_TARGETING / SHARED；与 apiVersion 不同不是回落。 |


## 接口：SB V4 创建商品定向

### 脚本输入与构参

| 转发属性 | 本操作约定 |
|---|---|
| method | POST |
| path | sb/targets |
| contentType | application/json |
| accept | 未显式指定 |

#### 脚本 JSON 参数与选项

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| profileId | integer/string | 是 | 从广告授权技能解析，不能要求用户报数字。 |
| region | string | 是 | NA / EU / FE。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已完成依赖检测时使用，不绕过授权。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存响应。 |
| --no-cache | CLI flag | 否 | 业务调用始终附加；响应缓存关闭。公共调用器会建立空缓存目录，但不读写响应缓存。 |
| campaignStructure | string | 否 | V3 本地保护：MULTI_AD_GROUP 拒绝；LEGACY 用于声明已确认的历史结构。 |
| isMultiAdGroupsEnabled | boolean / string / number | 否 | V3 中 true、1、true/yes/y/on 字符串均拒绝；递归检查 payload；保护标志本身不作为查询参数。 |
| payload | object / array | 是 | Amazon 原生请求体；不自行改写字段或推定未记录的枚举；作为 body JSON 字符串发送。 |
| payload.targets | array<object> | 按原生操作 | 创建示例的定向数组包装；不改写原生请求 |
| payload.targets[].campaignId | number / string | 按原生要求 | 活动 ID |
| payload.targets[].adGroupId | number / string | 按原生要求 | 广告组 ID |
| payload.targets[].expressions | array<object> | 按原生要求 | SB 使用复数 expressions |
| payload.targets[].expressions[].type | string | 按原生要求 | 示例 asinSameAs |
| payload.targets[].expressions[].value | string | 按原生要求 | 示例 B0EXAMPLE |
| payload.targets[].bid | number | 按原生要求 | 示例 1.25 |

依赖检测为本地文件检查：0 表示存在认证技能；42 且 stderr 含 `DEPENDENCY_MISSING:` 时先安装 `linkfox-amazon-ads-auth`。认证与运行限制见 [总览](../api.md)。

SB 版本边界见 [共存规则](sb-coexistence.md)；V3 只兼容 Legacy，已知多广告组活动拒绝；不自动回落其他版本。

关键词创建/更新及定向创建最多 100 个；定向更新的批量上限按上游实际校验处理，不套用其他操作的限制。

### 脚本输出与解析

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| success | boolean | 查询或写操作处理状态；批量逐项结果仍须检查。 |
| transportHttpStatus | integer / null | 失败时保留的 LinkFox 外层状态；连接失败为 null。 |
| error | string | 失败原因；不自动重试。 |
| details | object / string / null | 网关错误原始内容。 |
| httpStatus | integer / null | 错误或写入时保留上游状态。 |
| body | string / null | 错误时保留上游原文。 |
| data | object / array / string | 解析后的 Amazon 批量结果；无法解析时保留原文，不把 HTTP 成功等同所有实体成功。 |
| apiVersion | string | V3 / V4，表示 CLI 入口/结构意图。 |
| amazonResourceVersion | string | V3 / V4 / V3_SHARED_TARGETING / SHARED_TARGETING / SHARED；与 apiVersion 不同不是回落。 |


## 接口：SB V4 查询广告组

### 脚本输入与构参

| 转发属性 | 本操作约定 |
|---|---|
| method | POST |
| path | sb/v4/adGroups/list |
| contentType | application/vnd.sbadgroupresource.v4+json |
| accept | application/vnd.sbadgroupresource.v4+json |

#### 脚本 JSON 参数与选项

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| profileId | integer/string | 是 | 从广告授权技能解析，不能要求用户报数字。 |
| region | string | 是 | NA / EU / FE。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已完成依赖检测时使用，不绕过授权。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存响应。 |
| --no-cache | CLI flag | 否 | 业务调用始终附加；响应缓存关闭。公共调用器会建立空缓存目录，但不读写响应缓存。 |
| fetchAll | boolean / string / number | 否 | 默认 true；false 只取一页。兼容布尔、0/1、true/false/yes/no/y/n/on/off 字符串，非法值报 SB_INVALID_BOOLEAN。 |
| maxPages | integer | 否 | 默认 50；达到上限停止并标记 truncated。 |
| maxResults | integer | 否 | 默认 100，单页 1–100；偏移分页对应 count 并钳制到 1–100；POST list 原样发给上游，由上游校验。 |
| nextToken | string | 否 | 起始续页令牌，默认不传；原样作为 body.nextToken，payload 内的值优先。 |
| includeExtendedDataFields | boolean | 否 | 默认不发送；按原生接口支持情况透传请求体标志。 |
| payload | object | 否 | Amazon 原生查询体；主资源覆盖规范化顶层过滤，Creative/Target 等保留原生字段。 |
| filters | array<object> | 否 | 原生查询数组，按上游要求透传；本资源不执行 Target 顶层过滤映射。 |
| filters[].filterType | string | 按原生接口要求 | 本资源的可用枚举由上游校验，不套用 Target 枚举。 |
| filters[].values | array<string> | 按原生接口要求 | 原生过滤值数组，脚本不改写。 |
| adGroupIdFilter | object / array / string | 否 | {include:[...]} / {exclude:[...]}；兼容裸数组或字符串，规范化为对象。 |
| adGroupIdFilter.include | array<string> | 对象形态按过滤要求 | 包含的 ID、状态、匹配类型或文本值；字段本身允许数组/单值时按上述规则规范化。 |
| adGroupIdFilter.exclude | array<string> | 否 | 对象型过滤器可用的排除值；按原生接口支持范围透传，不在客户端模拟排除。 |
| campaignIdFilter | object / array / string | 否 | {include:[...]} / {exclude:[...]}；兼容裸数组或字符串，规范化为对象。 |
| campaignIdFilter.include | array<string> | 对象形态按过滤要求 | 包含的 ID、状态、匹配类型或文本值；字段本身允许数组/单值时按上述规则规范化。 |
| campaignIdFilter.exclude | array<string> | 否 | 对象型过滤器可用的排除值；按原生接口支持范围透传，不在客户端模拟排除。 |
| stateFilter | object / array / string | 否 | {include:[...]} / {exclude:[...]}；兼容裸数组或字符串，规范化为对象。 |
| stateFilter.include | array<string> | 对象形态按过滤要求 | 包含的 ID、状态、匹配类型或文本值；字段本身允许数组/单值时按上述规则规范化。 |
| stateFilter.exclude | array<string> | 否 | 对象型过滤器可用的排除值；按原生接口支持范围透传，不在客户端模拟排除。 |
| nameFilter | object | 否 | {queryTermMatchType:BROAD_MATCH / EXACT_MATCH, include:[文本]}；按规范原样透传。 |
| nameFilter.include | array<string> | 对象形态按过滤要求 | 包含的 ID、状态、匹配类型或文本值；字段本身允许数组/单值时按上述规则规范化。 |
| nameFilter.queryTermMatchType | string | 文本过滤按原生要求 | BROAD_MATCH / EXACT_MATCH；原样透传。 |

#### Amazon 查询请求体字段

下表表示 body 字符串 JSON 解码后的分页字段；筛选结构及嵌套定义见本接口的脚本参数表。

| 字段 | 类型 | 必填 | 默认值与说明 |
|---|---|---|---|
| body.maxResults | integer | 否 | 默认 100；单页 1–100，由上游校验。 |
| body.nextToken | string | 否 | 默认不传；后续请求使用上一页令牌。 |

依赖检测为本地文件检查：0 表示存在认证技能；42 且 stderr 含 `DEPENDENCY_MISSING:` 时先安装 `linkfox-amazon-ads-auth`。认证与运行限制见 [总览](../api.md)。

SB 版本边界见 [共存规则](sb-coexistence.md)；V3 只兼容 Legacy，已知多广告组活动拒绝；不自动回落其他版本。

分页：跟随 nextToken；无后续 token 或 fetchAll=false 时结束。达到页数兜底时标记 truncated，不自动重试失败请求。

### 脚本输出与解析

`body.*` 表示 body 字符串 JSON 解码后的字段；分页失败时保留已取实体、原始错误和保护信息，停止后续请求。


#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| success | boolean | 查询处理状态；分页中途失败为 false，保留已取数据。 |
| transportHttpStatus | integer / null | 失败时保留的 LinkFox 外层状态；连接失败为 null。 |
| error | string | 失败原因；不自动重试。 |
| details | object / string / null | 网关错误原始内容。 |
| httpStatus | integer / null | 错误或写入时保留上游状态。 |
| body | string / null | 错误时保留上游原文。 |
| adGroups | array<object> | 聚合实体数组，保留返回字段。 |
| total | integer | 本次聚合、客户端过滤后的实体数，不是上游全量总数。 |
| pagesFetched | integer | 已取得页数。 |
| truncated | boolean | 达到页数限制或保留部分结果；为 true 时必须告知数据未取完。 |
| apiVersion | string | V3 / V4，表示 CLI 入口/结构意图。 |
| amazonResourceVersion | string | V3 / V4 / V3_SHARED_TARGETING / SHARED_TARGETING / SHARED；与 apiVersion 不同不是回落。 |
| body.nextToken | string | 后续页令牌；脚本聚合后不一定回显。 |
| body.totalCount | integer | 原始上游可用总量；脚本 total 仍按已聚合实体数。 |


## 接口：SB V4 查询广告

### 脚本输入与构参

| 转发属性 | 本操作约定 |
|---|---|
| method | POST |
| path | sb/v4/ads/list |
| contentType | application/vnd.sbadresource.v4+json |
| accept | application/vnd.sbadresource.v4+json |

#### 脚本 JSON 参数与选项

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| profileId | integer/string | 是 | 从广告授权技能解析，不能要求用户报数字。 |
| region | string | 是 | NA / EU / FE。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已完成依赖检测时使用，不绕过授权。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存响应。 |
| --no-cache | CLI flag | 否 | 业务调用始终附加；响应缓存关闭。公共调用器会建立空缓存目录，但不读写响应缓存。 |
| fetchAll | boolean / string / number | 否 | 默认 true；false 只取一页。兼容布尔、0/1、true/false/yes/no/y/n/on/off 字符串，非法值报 SB_INVALID_BOOLEAN。 |
| maxPages | integer | 否 | 默认 50；达到上限停止并标记 truncated。 |
| maxResults | integer | 否 | 默认 100，单页 1–100；偏移分页对应 count 并钳制到 1–100；POST list 原样发给上游，由上游校验。 |
| nextToken | string | 否 | 起始续页令牌，默认不传；原样作为 body.nextToken，payload 内的值优先。 |
| includeExtendedDataFields | boolean | 否 | 默认不发送；按原生接口支持情况透传请求体标志。 |
| payload | object | 否 | Amazon 原生查询体；主资源覆盖规范化顶层过滤，Creative/Target 等保留原生字段。 |
| filters | array<object> | 否 | 原生查询数组，按上游要求透传；本资源不执行 Target 顶层过滤映射。 |
| filters[].filterType | string | 按原生接口要求 | 本资源的可用枚举由上游校验，不套用 Target 枚举。 |
| filters[].values | array<string> | 按原生接口要求 | 原生过滤值数组，脚本不改写。 |
| adIdFilter | object / array / string | 否 | {include:[...]} / {exclude:[...]}；兼容裸数组或字符串，规范化为对象。 |
| adIdFilter.include | array<string> | 对象形态按过滤要求 | 包含的 ID、状态、匹配类型或文本值；字段本身允许数组/单值时按上述规则规范化。 |
| adIdFilter.exclude | array<string> | 否 | 对象型过滤器可用的排除值；按原生接口支持范围透传，不在客户端模拟排除。 |
| adGroupIdFilter | object / array / string | 否 | {include:[...]} / {exclude:[...]}；兼容裸数组或字符串，规范化为对象。 |
| adGroupIdFilter.include | array<string> | 对象形态按过滤要求 | 包含的 ID、状态、匹配类型或文本值；字段本身允许数组/单值时按上述规则规范化。 |
| adGroupIdFilter.exclude | array<string> | 否 | 对象型过滤器可用的排除值；按原生接口支持范围透传，不在客户端模拟排除。 |
| campaignIdFilter | object / array / string | 否 | {include:[...]} / {exclude:[...]}；兼容裸数组或字符串，规范化为对象。 |
| campaignIdFilter.include | array<string> | 对象形态按过滤要求 | 包含的 ID、状态、匹配类型或文本值；字段本身允许数组/单值时按上述规则规范化。 |
| campaignIdFilter.exclude | array<string> | 否 | 对象型过滤器可用的排除值；按原生接口支持范围透传，不在客户端模拟排除。 |
| stateFilter | object / array / string | 否 | {include:[...]} / {exclude:[...]}；兼容裸数组或字符串，规范化为对象。 |
| stateFilter.include | array<string> | 对象形态按过滤要求 | 包含的 ID、状态、匹配类型或文本值；字段本身允许数组/单值时按上述规则规范化。 |
| stateFilter.exclude | array<string> | 否 | 对象型过滤器可用的排除值；按原生接口支持范围透传，不在客户端模拟排除。 |

#### Amazon 查询请求体字段

下表表示 body 字符串 JSON 解码后的分页字段；筛选结构及嵌套定义见本接口的脚本参数表。

| 字段 | 类型 | 必填 | 默认值与说明 |
|---|---|---|---|
| body.maxResults | integer | 否 | 默认 100；单页 1–100，由上游校验。 |
| body.nextToken | string | 否 | 默认不传；后续请求使用上一页令牌。 |

依赖检测为本地文件检查：0 表示存在认证技能；42 且 stderr 含 `DEPENDENCY_MISSING:` 时先安装 `linkfox-amazon-ads-auth`。认证与运行限制见 [总览](../api.md)。

SB 版本边界见 [共存规则](sb-coexistence.md)；V3 只兼容 Legacy，已知多广告组活动拒绝；不自动回落其他版本。

分页：跟随 nextToken；无后续 token 或 fetchAll=false 时结束。达到页数兜底时标记 truncated，不自动重试失败请求。

### 脚本输出与解析

`body.*` 表示 body 字符串 JSON 解码后的字段；分页失败时保留已取实体、原始错误和保护信息，停止后续请求。


#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| success | boolean | 查询处理状态；分页中途失败为 false，保留已取数据。 |
| transportHttpStatus | integer / null | 失败时保留的 LinkFox 外层状态；连接失败为 null。 |
| error | string | 失败原因；不自动重试。 |
| details | object / string / null | 网关错误原始内容。 |
| httpStatus | integer / null | 错误或写入时保留上游状态。 |
| body | string / null | 错误时保留上游原文。 |
| ads | array<object> | 聚合实体数组，保留返回字段。 |
| total | integer | 本次聚合、客户端过滤后的实体数，不是上游全量总数。 |
| pagesFetched | integer | 已取得页数。 |
| truncated | boolean | 达到页数限制或保留部分结果；为 true 时必须告知数据未取完。 |
| apiVersion | string | V3 / V4，表示 CLI 入口/结构意图。 |
| amazonResourceVersion | string | V3 / V4 / V3_SHARED_TARGETING / SHARED_TARGETING / SHARED；与 apiVersion 不同不是回落。 |
| body.nextToken | string | 后续页令牌；脚本聚合后不一定回显。 |
| body.totalCount | integer | 原始上游可用总量；脚本 total 仍按已聚合实体数。 |


## 接口：SB V4 查询预算规则

### 脚本输入与构参

| 转发属性 | 本操作约定 |
|---|---|
| method | GET |
| path | sb/budgetRules |
| contentType | GET 不传 |
| accept | application/json |

#### 脚本 JSON 参数与选项

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| profileId | integer/string | 是 | 从广告授权技能解析，不能要求用户报数字。 |
| region | string | 是 | NA / EU / FE。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已完成依赖检测时使用，不绕过授权。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存响应。 |
| --no-cache | CLI flag | 否 | 业务调用始终附加；响应缓存关闭。公共调用器会建立空缓存目录，但不读写响应缓存。 |
| fetchAll | boolean / string / number | 否 | 默认 true；false 只取一页。兼容布尔、0/1、true/false/yes/no/y/n/on/off 字符串，非法值报 SB_INVALID_BOOLEAN。 |
| maxPages | integer | 否 | 默认 50；达到上限停止并标记 truncated。 |
| maxResults | integer | 否 | 默认 100，单页 1–100；偏移分页对应 count；SD 与 SB 偏移会钳制范围。 |
| nextToken | string | 否 | 起始续页令牌，默认不传；经 URL 编码加入 queryString，后续自动跟随。 |
| pageSize | integer | 否 | 默认 maxResults 或 100，钳制 1–100；查询 sb/budgetRules 时实际发送 pageSize + nextToken。 |

#### Amazon 查询串字段

| 字段 | 类型 | 必填 | 默认值与说明 |
|---|---|---|---|
| queryString.nextToken | string | 否 | 默认不传；续页 token 必须 URL 编码，不直接拼接。 |
| queryString.pageSize | integer | 是（脚本自动提供） | 优先 pageSize，再取 maxResults，最后为 100；钳制到 1–100。 |

依赖检测为本地文件检查：0 表示存在认证技能；42 且 stderr 含 `DEPENDENCY_MISSING:` 时先安装 `linkfox-amazon-ads-auth`。认证与运行限制见 [总览](../api.md)。

SB 版本边界见 [共存规则](sb-coexistence.md)；V3 只兼容 Legacy，已知多广告组活动拒绝；不自动回落其他版本。

分页：跟随 nextToken；无后续 token 或 fetchAll=false 时结束。达到页数兜底时标记 truncated，不自动重试失败请求。

### 脚本输出与解析

`body.*` 表示 body 字符串 JSON 解码后的字段；分页失败时保留已取实体、原始错误和保护信息，停止后续请求。


#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| success | boolean | 查询处理状态；分页中途失败为 false，保留已取数据。 |
| transportHttpStatus | integer / null | 失败时保留的 LinkFox 外层状态；连接失败为 null。 |
| error | string | 失败原因；不自动重试。 |
| details | object / string / null | 网关错误原始内容。 |
| httpStatus | integer / null | 错误或写入时保留上游状态。 |
| body | string / null | 错误时保留上游原文。 |
| budgetRules | array<object> | 聚合实体数组，保留返回字段。 |
| total | integer | 本次聚合、客户端过滤后的实体数，不是上游全量总数。 |
| pagesFetched | integer | 已取得页数。 |
| truncated | boolean | 达到页数限制或保留部分结果；为 true 时必须告知数据未取完。 |
| apiVersion | string | V3 / V4，表示 CLI 入口/结构意图。 |
| amazonResourceVersion | string | V3 / V4 / V3_SHARED_TARGETING / SHARED_TARGETING / SHARED；与 apiVersion 不同不是回落。 |
| body.budgetRulesForAdvertiserResponse | array | SB 预算原生列表字段。 |
| body.nextToken | string | 后续页令牌；脚本聚合后不一定回显。 |


## 接口：SB V4 查询广告活动

### 脚本输入与构参

| 转发属性 | 本操作约定 |
|---|---|
| method | POST |
| path | sb/v4/campaigns/list |
| contentType | application/vnd.sbcampaignresource.v4+json |
| accept | application/vnd.sbcampaignresource.v4+json |

#### 脚本 JSON 参数与选项

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| profileId | integer/string | 是 | 从广告授权技能解析，不能要求用户报数字。 |
| region | string | 是 | NA / EU / FE。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已完成依赖检测时使用，不绕过授权。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存响应。 |
| --no-cache | CLI flag | 否 | 业务调用始终附加；响应缓存关闭。公共调用器会建立空缓存目录，但不读写响应缓存。 |
| fetchAll | boolean / string / number | 否 | 默认 true；false 只取一页。兼容布尔、0/1、true/false/yes/no/y/n/on/off 字符串，非法值报 SB_INVALID_BOOLEAN。 |
| maxPages | integer | 否 | 默认 50；达到上限停止并标记 truncated。 |
| maxResults | integer | 否 | 默认 100，单页 1–100；偏移分页对应 count 并钳制到 1–100；POST list 原样发给上游，由上游校验。 |
| nextToken | string | 否 | 起始续页令牌，默认不传；原样作为 body.nextToken，payload 内的值优先。 |
| includeExtendedDataFields | boolean | 否 | 默认不发送；按原生接口支持情况透传请求体标志。 |
| payload | object | 否 | Amazon 原生查询体；主资源覆盖规范化顶层过滤，Creative/Target 等保留原生字段。 |
| filters | array<object> | 否 | 原生查询数组，按上游要求透传；本资源不执行 Target 顶层过滤映射。 |
| filters[].filterType | string | 按原生接口要求 | 本资源的可用枚举由上游校验，不套用 Target 枚举。 |
| filters[].values | array<string> | 按原生接口要求 | 原生过滤值数组，脚本不改写。 |
| campaignIdFilter | object / array / string | 否 | {include:[...]} / {exclude:[...]}；兼容裸数组或字符串，规范化为对象。 |
| campaignIdFilter.include | array<string> | 对象形态按过滤要求 | 包含的 ID、状态、匹配类型或文本值；字段本身允许数组/单值时按上述规则规范化。 |
| campaignIdFilter.exclude | array<string> | 否 | 对象型过滤器可用的排除值；按原生接口支持范围透传，不在客户端模拟排除。 |
| stateFilter | object / array / string | 否 | {include:[...]} / {exclude:[...]}；兼容裸数组或字符串，规范化为对象。 |
| stateFilter.include | array<string> | 对象形态按过滤要求 | 包含的 ID、状态、匹配类型或文本值；字段本身允许数组/单值时按上述规则规范化。 |
| stateFilter.exclude | array<string> | 否 | 对象型过滤器可用的排除值；按原生接口支持范围透传，不在客户端模拟排除。 |
| nameFilter | object | 否 | {queryTermMatchType:BROAD_MATCH / EXACT_MATCH, include:[文本]}；按规范原样透传。 |
| nameFilter.include | array<string> | 对象形态按过滤要求 | 包含的 ID、状态、匹配类型或文本值；字段本身允许数组/单值时按上述规则规范化。 |
| nameFilter.queryTermMatchType | string | 文本过滤按原生要求 | BROAD_MATCH / EXACT_MATCH；原样透传。 |
| portfolioIdFilter | object / array / string | 否 | {include:[...]} / {exclude:[...]}；兼容裸数组或字符串，规范化为对象。 |
| portfolioIdFilter.include | array<string> | 对象形态按过滤要求 | 包含的 ID、状态、匹配类型或文本值；字段本身允许数组/单值时按上述规则规范化。 |
| portfolioIdFilter.exclude | array<string> | 否 | 对象型过滤器可用的排除值；按原生接口支持范围透传，不在客户端模拟排除。 |

#### Amazon 查询请求体字段

下表表示 body 字符串 JSON 解码后的分页字段；筛选结构及嵌套定义见本接口的脚本参数表。

| 字段 | 类型 | 必填 | 默认值与说明 |
|---|---|---|---|
| body.maxResults | integer | 否 | 默认 100；单页 1–100，由上游校验。 |
| body.nextToken | string | 否 | 默认不传；后续请求使用上一页令牌。 |

依赖检测为本地文件检查：0 表示存在认证技能；42 且 stderr 含 `DEPENDENCY_MISSING:` 时先安装 `linkfox-amazon-ads-auth`。认证与运行限制见 [总览](../api.md)。

SB 版本边界见 [共存规则](sb-coexistence.md)；V3 只兼容 Legacy，已知多广告组活动拒绝；不自动回落其他版本。

分页：跟随 nextToken；无后续 token 或 fetchAll=false 时结束。达到页数兜底时标记 truncated，不自动重试失败请求。

### 脚本输出与解析

`body.*` 表示 body 字符串 JSON 解码后的字段；分页失败时保留已取实体、原始错误和保护信息，停止后续请求。


#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| success | boolean | 查询处理状态；分页中途失败为 false，保留已取数据。 |
| transportHttpStatus | integer / null | 失败时保留的 LinkFox 外层状态；连接失败为 null。 |
| error | string | 失败原因；不自动重试。 |
| details | object / string / null | 网关错误原始内容。 |
| httpStatus | integer / null | 错误或写入时保留上游状态。 |
| body | string / null | 错误时保留上游原文。 |
| campaigns | array<object> | 聚合实体数组，保留返回字段。 |
| total | integer | 本次聚合、客户端过滤后的实体数，不是上游全量总数。 |
| pagesFetched | integer | 已取得页数。 |
| truncated | boolean | 达到页数限制或保留部分结果；为 true 时必须告知数据未取完。 |
| apiVersion | string | V3 / V4，表示 CLI 入口/结构意图。 |
| amazonResourceVersion | string | V3 / V4 / V3_SHARED_TARGETING / SHARED_TARGETING / SHARED；与 apiVersion 不同不是回落。 |
| body.nextToken | string | 后续页令牌；脚本聚合后不一定回显。 |
| body.totalCount | integer | 原始上游可用总量；脚本 total 仍按已聚合实体数。 |

#### 活动结构字段

| 字段 | 类型 | 说明 |
|---|---|---|
| campaigns[].isMultiAdGroupsEnabled | boolean | 用于判断活动结构的标志；为 true 时禁止交给 V3。 |
| campaignStructure | string | 本地已知结构可标为 LEGACY / MULTI_AD_GROUP；不凭 campaignId 推测，也不补造上游缺失字段。 |


## 接口：SB V4 查询创意

### 脚本输入与构参

| 转发属性 | 本操作约定 |
|---|---|
| method | POST |
| path | sb/ads/creatives/list |
| contentType | application/vnd.sbAdCreativeResource.v4+json |
| accept | application/vnd.sbAdCreativeResource.v4+json |

#### 脚本 JSON 参数与选项

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| profileId | integer/string | 是 | 从广告授权技能解析，不能要求用户报数字。 |
| region | string | 是 | NA / EU / FE。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已完成依赖检测时使用，不绕过授权。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存响应。 |
| --no-cache | CLI flag | 否 | 业务调用始终附加；响应缓存关闭。公共调用器会建立空缓存目录，但不读写响应缓存。 |
| fetchAll | boolean / string / number | 否 | 默认 true；false 只取一页。兼容布尔、0/1、true/false/yes/no/y/n/on/off 字符串，非法值报 SB_INVALID_BOOLEAN。 |
| maxPages | integer | 否 | 默认 50；达到上限停止并标记 truncated。 |
| maxResults | integer | 否 | 默认 100，单页 1–100；偏移分页对应 count 并钳制到 1–100；POST list 原样发给上游，由上游校验。 |
| nextToken | string | 否 | 起始续页令牌，默认不传；原样作为 body.nextToken，payload 内的值优先。 |
| includeExtendedDataFields | boolean | 否 | 默认不发送；按原生接口支持情况透传请求体标志。 |
| payload | object | 否 | Amazon 原生查询体；主资源覆盖规范化顶层过滤，Creative/Target 等保留原生字段。 |
| filters | array<object> | 否 | 原生查询数组，按上游要求透传；本资源不执行 Target 顶层过滤映射。 |
| filters[].filterType | string | 按原生接口要求 | 本资源的可用枚举由上游校验，不套用 Target 枚举。 |
| filters[].values | array<string> | 按原生接口要求 | 原生过滤值数组，脚本不改写。 |
| adId | string / number | 是，可在 payload 内 | 按 Ad 查询 Creative Version；顶层会转成字符串；缺失报 SB_CREATIVE_AD_ID_REQUIRED，不是全账号列表。 |

#### Amazon 查询请求体字段

下表表示 body 字符串 JSON 解码后的分页字段；筛选结构及嵌套定义见本接口的脚本参数表。

| 字段 | 类型 | 必填 | 默认值与说明 |
|---|---|---|---|
| body.maxResults | integer | 否 | 默认 100；单页 1–100，由上游校验。 |
| body.nextToken | string | 否 | 默认不传；后续请求使用上一页令牌。 |

依赖检测为本地文件检查：0 表示存在认证技能；42 且 stderr 含 `DEPENDENCY_MISSING:` 时先安装 `linkfox-amazon-ads-auth`。认证与运行限制见 [总览](../api.md)。

SB 版本边界见 [共存规则](sb-coexistence.md)；V3 只兼容 Legacy，已知多广告组活动拒绝；不自动回落其他版本。

分页：跟随 nextToken；无后续 token 或 fetchAll=false 时结束。达到页数兜底时标记 truncated，不自动重试失败请求。

### 脚本输出与解析

`body.*` 表示 body 字符串 JSON 解码后的字段；分页失败时保留已取实体、原始错误和保护信息，停止后续请求。


#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| success | boolean | 查询处理状态；分页中途失败为 false，保留已取数据。 |
| transportHttpStatus | integer / null | 失败时保留的 LinkFox 外层状态；连接失败为 null。 |
| error | string | 失败原因；不自动重试。 |
| details | object / string / null | 网关错误原始内容。 |
| httpStatus | integer / null | 错误或写入时保留上游状态。 |
| body | string / null | 错误时保留上游原文。 |
| creatives | array<object> | 聚合实体数组，保留返回字段。 |
| total | integer | 本次聚合、客户端过滤后的实体数，不是上游全量总数。 |
| pagesFetched | integer | 已取得页数。 |
| truncated | boolean | 达到页数限制或保留部分结果；为 true 时必须告知数据未取完。 |
| apiVersion | string | V3 / V4，表示 CLI 入口/结构意图。 |
| amazonResourceVersion | string | V3 / V4 / V3_SHARED_TARGETING / SHARED_TARGETING / SHARED；与 apiVersion 不同不是回落。 |
| body.nextToken | string | 后续页令牌；脚本聚合后不一定回显。 |


## 接口：SB V4 查询关键词

### 脚本输入与构参

| 转发属性 | 本操作约定 |
|---|---|
| method | GET |
| path | sb/keywords |
| contentType | GET 不传 |
| accept | application/vnd.sbkeyword.v3+json |

#### 脚本 JSON 参数与选项

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| profileId | integer/string | 是 | 从广告授权技能解析，不能要求用户报数字。 |
| region | string | 是 | NA / EU / FE。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已完成依赖检测时使用，不绕过授权。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存响应。 |
| --no-cache | CLI flag | 否 | 业务调用始终附加；响应缓存关闭。公共调用器会建立空缓存目录，但不读写响应缓存。 |
| campaignStructure | string | 否 | V3 本地保护：MULTI_AD_GROUP 拒绝；LEGACY 用于声明已确认的历史结构。 |
| isMultiAdGroupsEnabled | boolean / string / number | 否 | V3 中 true、1、true/yes/y/on 字符串均拒绝；递归检查 payload；保护标志本身不作为查询参数。 |
| fetchAll | boolean / string / number | 否 | 默认 true；false 只取一页。兼容布尔、0/1、true/false/yes/no/y/n/on/off 字符串，非法值报 SB_INVALID_BOOLEAN。 |
| maxPages | integer | 否 | 默认 50；达到上限停止并标记 truncated。 |
| maxResults | integer | 否 | 默认 100，单页 1–100；偏移分页对应 count 并钳制到 1–100；POST list 原样发给上游，由上游校验。 |
| keywordIdFilter | string / array / object | 否 | 接受字符串、数组或 {include:[...]}；ID 拼为逗号串，状态/匹配类型转小写，name/keywordText/locale 取首项。 |
| keywordIdFilter.include | array<string> | 对象形态按过滤要求 | 包含的 ID、状态、匹配类型或文本值；字段本身允许数组/单值时按上述规则规范化。 |
| adGroupIdFilter | string / array / object | 否 | 接受字符串、数组或 {include:[...]}；ID 拼为逗号串，状态/匹配类型转小写，name/keywordText/locale 取首项。 |
| adGroupIdFilter.include | array<string> | 对象形态按过滤要求 | 包含的 ID、状态、匹配类型或文本值；字段本身允许数组/单值时按上述规则规范化。 |
| campaignIdFilter | string / array / object | 否 | 接受字符串、数组或 {include:[...]}；ID 拼为逗号串，状态/匹配类型转小写，name/keywordText/locale 取首项。 |
| campaignIdFilter.include | array<string> | 对象形态按过滤要求 | 包含的 ID、状态、匹配类型或文本值；字段本身允许数组/单值时按上述规则规范化。 |
| stateFilter | string / array / object | 否 | 接受字符串、数组或 {include:[...]}；ID 拼为逗号串，状态/匹配类型转小写，name/keywordText/locale 取首项。 |
| stateFilter.include | array<string> | 对象形态按过滤要求 | 包含的 ID、状态、匹配类型或文本值；字段本身允许数组/单值时按上述规则规范化。 |
| matchTypeFilter | string / array / object | 否 | 接受字符串、数组或 {include:[...]}；ID 拼为逗号串，状态/匹配类型转小写，name/keywordText/locale 取首项。 |
| matchTypeFilter.include | array<string> | 对象形态按过滤要求 | 包含的 ID、状态、匹配类型或文本值；字段本身允许数组/单值时按上述规则规范化。 |
| keywordText | string / array / object | 否 | SB GET 关键词文本；多值只取首项。 |
| keywordText.include | array<string> | 对象形态按过滤要求 | 包含的 ID、状态、匹配类型或文本值；字段本身允许数组/单值时按上述规则规范化。 |
| creativeType | string / array / object | 否 | SB GET 创意类型；转小写逗号串。 |
| creativeType.include | array<string> | 对象形态按过滤要求 | 包含的 ID、状态、匹配类型或文本值；字段本身允许数组/单值时按上述规则规范化。 |
| locale | string / array / object | 否 | 本地化语言；SB GET 只取首项；SP keywords 支持。 |
| locale.include | array<string> | 对象形态按过滤要求 | 包含的 ID、状态、匹配类型或文本值；字段本身允许数组/单值时按上述规则规范化。 |

#### Amazon 查询串字段

| 字段 | 类型 | 必填 | 默认值与说明 |
|---|---|---|---|
| queryString.startIndex | integer | 否 | 默认 0；业务 CLI 从 0 开始，逐页增加 count，不接收顶层 startIndex。 |
| queryString.count | integer | 否 | 默认 100；CLI 由 maxResults 决定，钳制到 1–100。 |
| queryString.keywordIdFilter | string | 否 | 对应 keywordIdFilter；多个值以逗号连接后 URL 编码。 |
| queryString.adGroupIdFilter | string | 否 | 对应 adGroupIdFilter；多个值以逗号连接后 URL 编码。 |
| queryString.campaignIdFilter | string | 否 | 对应 campaignIdFilter；多个值以逗号连接后 URL 编码。 |
| queryString.stateFilter | string | 否 | 对应 stateFilter；多个值以逗号连接，整体 URL 编码；状态转小写。 |
| queryString.matchTypeFilter | string | 否 | 对应 matchTypeFilter；多个值以逗号连接后 URL 编码。 |
| queryString.keywordText | string | 否 | 对应 keywordText；仅取首项作精确匹配，特殊字符必须 URL 编码。 |
| queryString.creativeType | string | 否 | 对应 creativeType；多个值以逗号连接后 URL 编码。 |
| queryString.locale | string | 否 | 对应 locale；仅取首项作精确匹配，特殊字符必须 URL 编码。 |

依赖检测为本地文件检查：0 表示存在认证技能；42 且 stderr 含 `DEPENDENCY_MISSING:` 时先安装 `linkfox-amazon-ads-auth`。认证与运行限制见 [总览](../api.md)。

SB 版本边界见 [共存规则](sb-coexistence.md)；V3 只兼容 Legacy，已知多广告组活动拒绝；不自动回落其他版本。

V3 共享入口的 media 约定：GET 不显式指定 Accept，创建/更新使用 application/json 且不显式指定 Accept；V4 入口使用上表 Accept。两者路径相同，结构意图和返回版本标记不同。

分页：startIndex + count 从 0 递增，本页少于 count 结束。达到页数兜底时标记 truncated，不自动重试失败请求。

### 脚本输出与解析

`body.*` 表示 body 字符串 JSON 解码后的字段；分页失败时保留已取实体、原始错误和保护信息，停止后续请求。


#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| success | boolean | 查询处理状态；分页中途失败为 false，保留已取数据。 |
| transportHttpStatus | integer / null | 失败时保留的 LinkFox 外层状态；连接失败为 null。 |
| error | string | 失败原因；不自动重试。 |
| details | object / string / null | 网关错误原始内容。 |
| httpStatus | integer / null | 错误或写入时保留上游状态。 |
| body | string / null | 错误时保留上游原文。 |
| keywords | array<object> | 聚合实体数组，保留返回字段。 |
| total | integer | 本次聚合、客户端过滤后的实体数，不是上游全量总数。 |
| pagesFetched | integer | 已取得页数。 |
| truncated | boolean | 达到页数限制或保留部分结果；为 true 时必须告知数据未取完。 |
| apiVersion | string | V3 / V4，表示 CLI 入口/结构意图。 |
| amazonResourceVersion | string | V3 / V4 / V3_SHARED_TARGETING / SHARED_TARGETING / SHARED；与 apiVersion 不同不是回落。 |


## 接口：SB V4 查询商品定向

### 脚本输入与构参

| 转发属性 | 本操作约定 |
|---|---|
| method | POST |
| path | sb/targets/list |
| contentType | application/json |
| accept | 未显式指定 |

#### 脚本 JSON 参数与选项

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| profileId | integer/string | 是 | 从广告授权技能解析，不能要求用户报数字。 |
| region | string | 是 | NA / EU / FE。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已完成依赖检测时使用，不绕过授权。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存响应。 |
| --no-cache | CLI flag | 否 | 业务调用始终附加；响应缓存关闭。公共调用器会建立空缓存目录，但不读写响应缓存。 |
| campaignStructure | string | 否 | V3 本地保护：MULTI_AD_GROUP 拒绝；LEGACY 用于声明已确认的历史结构。 |
| isMultiAdGroupsEnabled | boolean / string / number | 否 | V3 中 true、1、true/yes/y/on 字符串均拒绝；递归检查 payload；保护标志本身不作为查询参数。 |
| fetchAll | boolean / string / number | 否 | 默认 true；false 只取一页。兼容布尔、0/1、true/false/yes/no/y/n/on/off 字符串，非法值报 SB_INVALID_BOOLEAN。 |
| maxPages | integer | 否 | 默认 50；达到上限停止并标记 truncated。 |
| maxResults | integer | 否 | 默认 100，单页 1–100；偏移分页对应 count 并钳制到 1–100；POST list 原样发给上游，由上游校验。 |
| nextToken | string | 否 | 起始续页令牌，默认不传；原样作为 body.nextToken，payload 内的值优先。 |
| includeExtendedDataFields | boolean | 否 | 默认不发送；按原生接口支持情况透传请求体标志。 |
| payload | object | 否 | Amazon 原生查询体；主资源覆盖规范化顶层过滤，Creative/Target 等保留原生字段。 |
| filters | array<object> | 否 | 原生过滤器数组，元素 {filterType,values}；同类原生过滤优先于顶层映射。 |
| filters[].filterType | string | 元素必填 | 过滤器类型；Target：CAMPAIGN_ID / AD_GROUP_ID / TARGETING_STATE / TARGET_ID / CREATIVE_TYPE。 |
| filters[].values | array<string> | 元素必填 | 过滤值数组；Target 顶层 stateFilter 自动转小写。 |
| campaignIdFilter | object / array / string | 否 | 接受 {include:[...]}、数组或单值；不把 exclude 解释为 include；映射至 filters[].filterType=CAMPAIGN_ID |
| campaignIdFilter.include | array<string> | 对象形态按过滤要求 | 包含的 ID、状态、匹配类型或文本值；字段本身允许数组/单值时按上述规则规范化。 |
| adGroupIdFilter | object / array / string | 否 | 接受 {include:[...]}、数组或单值；不把 exclude 解释为 include；映射至 filters[].filterType=AD_GROUP_ID |
| adGroupIdFilter.include | array<string> | 对象形态按过滤要求 | 包含的 ID、状态、匹配类型或文本值；字段本身允许数组/单值时按上述规则规范化。 |
| stateFilter | object / array / string | 否 | 接受 {include:[...]}、数组或单值；不把 exclude 解释为 include；映射至 filters[].filterType=TARGETING_STATE；转为小写状态值。 |
| stateFilter.include | array<string> | 对象形态按过滤要求 | 包含的 ID、状态、匹配类型或文本值；字段本身允许数组/单值时按上述规则规范化。 |
| targetIdFilter | object / array / string | 否 | 接受 {include:[...]}、数组或单值；不把 exclude 解释为 include；映射至 filters[].filterType=TARGET_ID |
| targetIdFilter.include | array<string> | 对象形态按过滤要求 | 包含的 ID、状态、匹配类型或文本值；字段本身允许数组/单值时按上述规则规范化。 |
| creativeTypeFilter | object / array / string | 否 | 接受 {include:[...]}、数组或单值；不把 exclude 解释为 include；映射至 filters[].filterType=CREATIVE_TYPE |
| creativeTypeFilter.include | array<string> | 对象形态按过滤要求 | 包含的 ID、状态、匹配类型或文本值；字段本身允许数组/单值时按上述规则规范化。 |

#### Amazon 查询请求体字段

下表表示 body 字符串 JSON 解码后的分页字段；筛选结构及嵌套定义见本接口的脚本参数表。

| 字段 | 类型 | 必填 | 默认值与说明 |
|---|---|---|---|
| body.maxResults | integer | 否 | 默认 100；单页 1–100，由上游校验。 |
| body.nextToken | string | 否 | 默认不传；后续请求使用上一页令牌。 |

依赖检测为本地文件检查：0 表示存在认证技能；42 且 stderr 含 `DEPENDENCY_MISSING:` 时先安装 `linkfox-amazon-ads-auth`。认证与运行限制见 [总览](../api.md)。

SB 版本边界见 [共存规则](sb-coexistence.md)；V3 只兼容 Legacy，已知多广告组活动拒绝；不自动回落其他版本。

分页：跟随 nextToken；无后续 token 或 fetchAll=false 时结束。达到页数兜底时标记 truncated，不自动重试失败请求。

### 脚本输出与解析

`body.*` 表示 body 字符串 JSON 解码后的字段；分页失败时保留已取实体、原始错误和保护信息，停止后续请求。


#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| success | boolean | 查询处理状态；分页中途失败为 false，保留已取数据。 |
| transportHttpStatus | integer / null | 失败时保留的 LinkFox 外层状态；连接失败为 null。 |
| error | string | 失败原因；不自动重试。 |
| details | object / string / null | 网关错误原始内容。 |
| httpStatus | integer / null | 错误或写入时保留上游状态。 |
| body | string / null | 错误时保留上游原文。 |
| targets | array<object> | 聚合实体数组，保留返回字段。 |
| total | integer | 本次聚合、客户端过滤后的实体数，不是上游全量总数。 |
| pagesFetched | integer | 已取得页数。 |
| truncated | boolean | 达到页数限制或保留部分结果；为 true 时必须告知数据未取完。 |
| apiVersion | string | V3 / V4，表示 CLI 入口/结构意图。 |
| amazonResourceVersion | string | V3 / V4 / V3_SHARED_TARGETING / SHARED_TARGETING / SHARED；与 apiVersion 不同不是回落。 |
| body.nextToken | string | 后续页令牌；脚本聚合后不一定回显。 |


## 接口：SB V4 修改广告组

### 脚本输入与构参

| 转发属性 | 本操作约定 |
|---|---|
| method | PUT |
| path | sb/v4/adGroups |
| contentType | application/vnd.sbadgroupresource.v4+json |
| accept | application/vnd.sbadgroupresource.v4+json |

#### 脚本 JSON 参数与选项

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| profileId | integer/string | 是 | 从广告授权技能解析，不能要求用户报数字。 |
| region | string | 是 | NA / EU / FE。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已完成依赖检测时使用，不绕过授权。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存响应。 |
| --no-cache | CLI flag | 否 | 业务调用始终附加；响应缓存关闭。公共调用器会建立空缓存目录，但不读写响应缓存。 |
| payload | object / array | 是 | Amazon 原生请求体；不自行改写字段或推定未记录的枚举；作为 body JSON 字符串发送。 |

依赖检测为本地文件检查：0 表示存在认证技能；42 且 stderr 含 `DEPENDENCY_MISSING:` 时先安装 `linkfox-amazon-ads-auth`。认证与运行限制见 [总览](../api.md)。

SB 版本边界见 [共存规则](sb-coexistence.md)；V3 只兼容 Legacy，已知多广告组活动拒绝；不自动回落其他版本。

### 脚本输出与解析

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| success | boolean | 查询或写操作处理状态；批量逐项结果仍须检查。 |
| transportHttpStatus | integer / null | 失败时保留的 LinkFox 外层状态；连接失败为 null。 |
| error | string | 失败原因；不自动重试。 |
| details | object / string / null | 网关错误原始内容。 |
| httpStatus | integer / null | 错误或写入时保留上游状态。 |
| body | string / null | 错误时保留上游原文。 |
| data | object / array / string | 解析后的 Amazon 批量结果；无法解析时保留原文，不把 HTTP 成功等同所有实体成功。 |
| apiVersion | string | V3 / V4，表示 CLI 入口/结构意图。 |
| amazonResourceVersion | string | V3 / V4 / V3_SHARED_TARGETING / SHARED_TARGETING / SHARED；与 apiVersion 不同不是回落。 |


## 接口：SB V4 修改广告

### 脚本输入与构参

| 转发属性 | 本操作约定 |
|---|---|
| method | PUT |
| path | sb/v4/ads |
| contentType | application/vnd.sbadresource.v4+json |
| accept | application/vnd.sbadresource.v4+json |

#### 脚本 JSON 参数与选项

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| profileId | integer/string | 是 | 从广告授权技能解析，不能要求用户报数字。 |
| region | string | 是 | NA / EU / FE。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已完成依赖检测时使用，不绕过授权。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存响应。 |
| --no-cache | CLI flag | 否 | 业务调用始终附加；响应缓存关闭。公共调用器会建立空缓存目录，但不读写响应缓存。 |
| payload | object / array | 是 | Amazon 原生请求体；不自行改写字段或推定未记录的枚举；作为 body JSON 字符串发送。 |

依赖检测为本地文件检查：0 表示存在认证技能；42 且 stderr 含 `DEPENDENCY_MISSING:` 时先安装 `linkfox-amazon-ads-auth`。认证与运行限制见 [总览](../api.md)。

SB 版本边界见 [共存规则](sb-coexistence.md)；V3 只兼容 Legacy，已知多广告组活动拒绝；不自动回落其他版本。

### 脚本输出与解析

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| success | boolean | 查询或写操作处理状态；批量逐项结果仍须检查。 |
| transportHttpStatus | integer / null | 失败时保留的 LinkFox 外层状态；连接失败为 null。 |
| error | string | 失败原因；不自动重试。 |
| details | object / string / null | 网关错误原始内容。 |
| httpStatus | integer / null | 错误或写入时保留上游状态。 |
| body | string / null | 错误时保留上游原文。 |
| data | object / array / string | 解析后的 Amazon 批量结果；无法解析时保留原文，不把 HTTP 成功等同所有实体成功。 |
| apiVersion | string | V3 / V4，表示 CLI 入口/结构意图。 |
| amazonResourceVersion | string | V3 / V4 / V3_SHARED_TARGETING / SHARED_TARGETING / SHARED；与 apiVersion 不同不是回落。 |


## 接口：SB V4 修改预算规则

### 脚本输入与构参

| 转发属性 | 本操作约定 |
|---|---|
| method | PUT |
| path | sb/budgetRules |
| contentType | application/json |
| accept | application/json |

#### 脚本 JSON 参数与选项

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| profileId | integer/string | 是 | 从广告授权技能解析，不能要求用户报数字。 |
| region | string | 是 | NA / EU / FE。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已完成依赖检测时使用，不绕过授权。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存响应。 |
| --no-cache | CLI flag | 否 | 业务调用始终附加；响应缓存关闭。公共调用器会建立空缓存目录，但不读写响应缓存。 |
| payload | object / array | 是 | Amazon 原生请求体；不自行改写字段或推定未记录的枚举；作为 body JSON 字符串发送；SB 预算规则子字段按 Amazon 原生请求要求传入，不据 SP/SD 结构推定。 |

依赖检测为本地文件检查：0 表示存在认证技能；42 且 stderr 含 `DEPENDENCY_MISSING:` 时先安装 `linkfox-amazon-ads-auth`。认证与运行限制见 [总览](../api.md)。

SB 版本边界见 [共存规则](sb-coexistence.md)；V3 只兼容 Legacy，已知多广告组活动拒绝；不自动回落其他版本。

### 脚本输出与解析

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| success | boolean | 查询或写操作处理状态；批量逐项结果仍须检查。 |
| transportHttpStatus | integer / null | 失败时保留的 LinkFox 外层状态；连接失败为 null。 |
| error | string | 失败原因；不自动重试。 |
| details | object / string / null | 网关错误原始内容。 |
| httpStatus | integer / null | 错误或写入时保留上游状态。 |
| body | string / null | 错误时保留上游原文。 |
| data | object / array / string | 解析后的 Amazon 批量结果；无法解析时保留原文，不把 HTTP 成功等同所有实体成功。 |
| apiVersion | string | V3 / V4，表示 CLI 入口/结构意图。 |
| amazonResourceVersion | string | V3 / V4 / V3_SHARED_TARGETING / SHARED_TARGETING / SHARED；与 apiVersion 不同不是回落。 |


## 接口：SB V4 修改广告活动

### 脚本输入与构参

| 转发属性 | 本操作约定 |
|---|---|
| method | PUT |
| path | sb/v4/campaigns |
| contentType | application/vnd.sbcampaignresource.v4+json |
| accept | application/vnd.sbcampaignresource.v4+json |

#### 脚本 JSON 参数与选项

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| profileId | integer/string | 是 | 从广告授权技能解析，不能要求用户报数字。 |
| region | string | 是 | NA / EU / FE。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已完成依赖检测时使用，不绕过授权。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存响应。 |
| --no-cache | CLI flag | 否 | 业务调用始终附加；响应缓存关闭。公共调用器会建立空缓存目录，但不读写响应缓存。 |
| payload | object / array | 是 | Amazon 原生请求体；不自行改写字段或推定未记录的枚举；作为 body JSON 字符串发送。 |

依赖检测为本地文件检查：0 表示存在认证技能；42 且 stderr 含 `DEPENDENCY_MISSING:` 时先安装 `linkfox-amazon-ads-auth`。认证与运行限制见 [总览](../api.md)。

SB 版本边界见 [共存规则](sb-coexistence.md)；V3 只兼容 Legacy，已知多广告组活动拒绝；不自动回落其他版本。

### 脚本输出与解析

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| success | boolean | 查询或写操作处理状态；批量逐项结果仍须检查。 |
| transportHttpStatus | integer / null | 失败时保留的 LinkFox 外层状态；连接失败为 null。 |
| error | string | 失败原因；不自动重试。 |
| details | object / string / null | 网关错误原始内容。 |
| httpStatus | integer / null | 错误或写入时保留上游状态。 |
| body | string / null | 错误时保留上游原文。 |
| data | object / array / string | 解析后的 Amazon 批量结果；无法解析时保留原文，不把 HTTP 成功等同所有实体成功。 |
| apiVersion | string | V3 / V4，表示 CLI 入口/结构意图。 |
| amazonResourceVersion | string | V3 / V4 / V3_SHARED_TARGETING / SHARED_TARGETING / SHARED；与 apiVersion 不同不是回落。 |


## 接口：SB V4 修改关键词

### 脚本输入与构参

| 转发属性 | 本操作约定 |
|---|---|
| method | PUT |
| path | sb/keywords |
| contentType | application/json |
| accept | application/vnd.sbkeywordresponse.v3+json |

#### 脚本 JSON 参数与选项

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| profileId | integer/string | 是 | 从广告授权技能解析，不能要求用户报数字。 |
| region | string | 是 | NA / EU / FE。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已完成依赖检测时使用，不绕过授权。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存响应。 |
| --no-cache | CLI flag | 否 | 业务调用始终附加；响应缓存关闭。公共调用器会建立空缓存目录，但不读写响应缓存。 |
| campaignStructure | string | 否 | V3 本地保护：MULTI_AD_GROUP 拒绝；LEGACY 用于声明已确认的历史结构。 |
| isMultiAdGroupsEnabled | boolean / string / number | 否 | V3 中 true、1、true/yes/y/on 字符串均拒绝；递归检查 payload；保护标志本身不作为查询参数。 |
| payload | object / array | 是 | Amazon 原生请求体；不自行改写字段或推定未记录的枚举；作为 body JSON 字符串发送。 |
| payload[].keywordId | number / string | 按原生更新要求 | 关键词 ID，更新示例使用此字段 |
| payload[].campaignId | number / string | 按原生要求 | 活动 ID |
| payload[].adGroupId | number / string | 按原生要求 | 广告组 ID |
| payload[].bid | number | 按原生要求 | 出价，更新示例为 1.2 |

依赖检测为本地文件检查：0 表示存在认证技能；42 且 stderr 含 `DEPENDENCY_MISSING:` 时先安装 `linkfox-amazon-ads-auth`。认证与运行限制见 [总览](../api.md)。

SB 版本边界见 [共存规则](sb-coexistence.md)；V3 只兼容 Legacy，已知多广告组活动拒绝；不自动回落其他版本。

关键词创建/更新及定向创建最多 100 个；定向更新的批量上限按上游实际校验处理，不套用其他操作的限制。

V3 共享入口的 media 约定：GET 不显式指定 Accept，创建/更新使用 application/json 且不显式指定 Accept；V4 入口使用上表 Accept。两者路径相同，结构意图和返回版本标记不同。

### 脚本输出与解析

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| success | boolean | 查询或写操作处理状态；批量逐项结果仍须检查。 |
| transportHttpStatus | integer / null | 失败时保留的 LinkFox 外层状态；连接失败为 null。 |
| error | string | 失败原因；不自动重试。 |
| details | object / string / null | 网关错误原始内容。 |
| httpStatus | integer / null | 错误或写入时保留上游状态。 |
| body | string / null | 错误时保留上游原文。 |
| data | object / array / string | 解析后的 Amazon 批量结果；无法解析时保留原文，不把 HTTP 成功等同所有实体成功。 |
| apiVersion | string | V3 / V4，表示 CLI 入口/结构意图。 |
| amazonResourceVersion | string | V3 / V4 / V3_SHARED_TARGETING / SHARED_TARGETING / SHARED；与 apiVersion 不同不是回落。 |


## 接口：SB V4 修改商品定向

### 脚本输入与构参

| 转发属性 | 本操作约定 |
|---|---|
| method | PUT |
| path | sb/targets |
| contentType | application/json |
| accept | 未显式指定 |

#### 脚本 JSON 参数与选项

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| profileId | integer/string | 是 | 从广告授权技能解析，不能要求用户报数字。 |
| region | string | 是 | NA / EU / FE。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已完成依赖检测时使用，不绕过授权。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存响应。 |
| --no-cache | CLI flag | 否 | 业务调用始终附加；响应缓存关闭。公共调用器会建立空缓存目录，但不读写响应缓存。 |
| campaignStructure | string | 否 | V3 本地保护：MULTI_AD_GROUP 拒绝；LEGACY 用于声明已确认的历史结构。 |
| isMultiAdGroupsEnabled | boolean / string / number | 否 | V3 中 true、1、true/yes/y/on 字符串均拒绝；递归检查 payload；保护标志本身不作为查询参数。 |
| payload | object / array | 是 | Amazon 原生请求体；不自行改写字段或推定未记录的枚举；作为 body JSON 字符串发送。 |
| payload.targets | array<object> | 按原生操作 | 创建示例的定向数组包装；不改写原生请求 |
| payload.targets[].campaignId | number / string | 按原生要求 | 活动 ID |
| payload.targets[].adGroupId | number / string | 按原生要求 | 广告组 ID |
| payload.targets[].expressions | array<object> | 按原生要求 | SB 使用复数 expressions |
| payload.targets[].expressions[].type | string | 按原生要求 | 示例 asinSameAs |
| payload.targets[].expressions[].value | string | 按原生要求 | 示例 B0EXAMPLE |
| payload.targets[].bid | number | 按原生要求 | 示例 1.25 |

依赖检测为本地文件检查：0 表示存在认证技能；42 且 stderr 含 `DEPENDENCY_MISSING:` 时先安装 `linkfox-amazon-ads-auth`。认证与运行限制见 [总览](../api.md)。

SB 版本边界见 [共存规则](sb-coexistence.md)；V3 只兼容 Legacy，已知多广告组活动拒绝；不自动回落其他版本。

关键词创建/更新及定向创建最多 100 个；定向更新的批量上限按上游实际校验处理，不套用其他操作的限制。

### 脚本输出与解析

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| success | boolean | 查询或写操作处理状态；批量逐项结果仍须检查。 |
| transportHttpStatus | integer / null | 失败时保留的 LinkFox 外层状态；连接失败为 null。 |
| error | string | 失败原因；不自动重试。 |
| details | object / string / null | 网关错误原始内容。 |
| httpStatus | integer / null | 错误或写入时保留上游状态。 |
| body | string / null | 错误时保留上游原文。 |
| data | object / array / string | 解析后的 Amazon 批量结果；无法解析时保留原文，不把 HTTP 成功等同所有实体成功。 |
| apiVersion | string | V3 / V4，表示 CLI 入口/结构意图。 |
| amazonResourceVersion | string | V3 / V4 / V3_SHARED_TARGETING / SHARED_TARGETING / SHARED；与 apiVersion 不同不是回落。 |
