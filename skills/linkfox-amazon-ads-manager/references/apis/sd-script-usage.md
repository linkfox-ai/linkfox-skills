# 脚本输入、构参与本地结果

profileId 接收 Long 范围内的正整数或十进制数字字符串，发送到网关时为 integer；不接受布尔值、小数、零、负数或越界值。

网关接口定义见 [sd.md](sd.md)。以下表格描述脚本参数、构参或本地解析行为；不作为网关DTO或上游完整schema。

## 接口：SD 创建广告组

### 脚本输入与构参

| 转发属性 | 本操作约定 |
|---|---|
| method | POST |
| path | sd/adGroups |
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
| payload | object / array | 是 | [{...}]；作为 body JSON 字符串发送。 |

依赖检测为本地文件检查：0 表示存在认证技能；42 且 stderr 含 `DEPENDENCY_MISSING:` 时先安装 `linkfox-amazon-ads-auth`。认证与运行限制见 [总览](../api.md)。

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

#### 实体字段

以下为常见实体字段；原生写操作按创建/更新要求取用，非所有字段都必填，未记录的必填规则不推定。

| 字段 | 类型 | 说明 |
|---|---|---|
| payload 实体 / data 对应实体：adGroupId | number / string | 广告组 ID |
| payload 实体 / data 对应实体：campaignId | number / string | 活动 ID |
| payload 实体 / data 对应实体：name | string | 名称 |
| payload 实体 / data 对应实体：state | string | enabled / paused / archived；筛选入参兼容 ENABLED / PAUSED / ARCHIVED |
| payload 实体 / data 对应实体：defaultBid | number | 默认出价 |
| payload 实体 / data 对应实体：bidOptimization | 原生值 | 竞价优化，类型按上游返回值处理 |
| payload 实体 / data 对应实体：creativeType | string | 创意类型，原样保留 |


## 接口：SD 创建预算规则

### 脚本输入与构参

| 转发属性 | 本操作约定 |
|---|---|
| method | POST |
| path | sd/budgetRules |
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
| payload | object / array | 是 | {"budgetRulesDetails":[{...}]}；作为 body JSON 字符串发送。 |
| payload.budgetRulesDetails | array<object> | 按原生操作 | 预算规则数组 |
| 规则[].ruleId | string | 更新时按原生要求 | 规则 ID |
| 规则[].name | string | 按原生操作 | 规则名 |
| 规则[].ruleType | string | 按原生操作 | 示例 SCHEDULE |
| 规则[].duration | object | 按原生操作 | 生效周期，子字段按 Amazon 原生请求要求传入 |
| 规则[].budgetIncreaseBy | object | 按原生操作 | 预算提升设置，子字段按 Amazon 原生请求要求传入 |

依赖检测为本地文件检查：0 表示存在认证技能；42 且 stderr 含 `DEPENDENCY_MISSING:` 时先安装 `linkfox-amazon-ads-auth`。认证与运行限制见 [总览](../api.md)。

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


## 接口：SD 创建广告活动

### 脚本输入与构参

| 转发属性 | 本操作约定 |
|---|---|
| method | POST |
| path | sd/campaigns |
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
| payload | object / array | 是 | [{...}]；作为 body JSON 字符串发送。 |

依赖检测为本地文件检查：0 表示存在认证技能；42 且 stderr 含 `DEPENDENCY_MISSING:` 时先安装 `linkfox-amazon-ads-auth`。认证与运行限制见 [总览](../api.md)。

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

#### 实体字段

以下为常见实体字段；原生写操作按创建/更新要求取用，非所有字段都必填，未记录的必填规则不推定。

| 字段 | 类型 | 说明 |
|---|---|---|
| payload 实体 / data 对应实体：campaignId | number / string | 活动 ID |
| payload 实体 / data 对应实体：name | string | 名称 |
| payload 实体 / data 对应实体：state | string | enabled / paused / archived；筛选入参兼容 ENABLED / PAUSED / ARCHIVED |
| payload 实体 / data 对应实体：tactic | string | T00020 / T00030 |
| payload 实体 / data 对应实体：costType | string | cpc / vcpm |
| payload 实体 / data 对应实体：budget | number | 预算 |
| payload 实体 / data 对应实体：budgetType | string | 预算类型 |
| payload 实体 / data 对应实体：startDate | string | 开始日期 |
| payload 实体 / data 对应实体：endDate | string | 结束日期 |
| payload 实体 / data 对应实体：portfolioId | number / string | 组合 ID |


## 接口：SD 创建创意

### 脚本输入与构参

| 转发属性 | 本操作约定 |
|---|---|
| method | POST |
| path | sd/creatives |
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
| payload | object / array | 是 | [{"adGroupId":123,"type":"...","properties":{...}}]；作为 body JSON 字符串发送。 |
| payload[].adGroupId | number / string | 按原生要求 | 广告组 ID |
| payload[].type | string | 按原生要求 | 创意类型 |
| payload[].properties | object | 按原生要求 | 创意属性 |

依赖检测为本地文件检查：0 表示存在认证技能；42 且 stderr 含 `DEPENDENCY_MISSING:` 时先安装 `linkfox-amazon-ads-auth`。认证与运行限制见 [总览](../api.md)。

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

#### 实体字段

以下为常见实体字段；原生写操作按创建/更新要求取用，非所有字段都必填，未记录的必填规则不推定。

| 字段 | 类型 | 说明 |
|---|---|---|
| payload 实体 / data 对应实体：creativeId | number / string | 创意 ID |
| payload 实体 / data 对应实体：adGroupId | number / string | 广告组 ID |
| payload 实体 / data 对应实体：name | string | 名称 |
| payload 实体 / data 对应实体：creativeType | string | 上游原值 |
| payload 实体 / data 对应实体：properties | object | 依 creativeType 而异 |
| payload 实体 / data 对应实体：properties.headline | string | 标题 |
| payload 实体 / data 对应实体：properties.brandLogoAssetID | string | 品牌标识素材 ID |
| payload 实体 / data 对应实体：properties.video | 原生值 | 视频资料，类型依创意而异 |
| payload 实体 / data 对应实体：moderationStatus | 原生值 | 审核状态 |


## 接口：SD 创建否定定向

### 脚本输入与构参

| 转发属性 | 本操作约定 |
|---|---|
| method | POST |
| path | sd/negativeTargets |
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
| payload | object / array | 是 | [{...}]；作为 body JSON 字符串发送。 |

依赖检测为本地文件检查：0 表示存在认证技能；42 且 stderr 含 `DEPENDENCY_MISSING:` 时先安装 `linkfox-amazon-ads-auth`。认证与运行限制见 [总览](../api.md)。

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

#### 实体字段

以下为常见实体字段；原生写操作按创建/更新要求取用，非所有字段都必填，未记录的必填规则不推定。

| 字段 | 类型 | 说明 |
|---|---|---|
| payload 实体 / data 对应实体：targetId | number / string | 定向 ID |
| payload 实体 / data 对应实体：adGroupId | number / string | 广告组 ID |
| payload 实体 / data 对应实体：campaignId | number / string | 活动 ID |
| payload 实体 / data 对应实体：state | string | enabled / paused / archived；筛选入参兼容 ENABLED / PAUSED / ARCHIVED |
| payload 实体 / data 对应实体：expression | array | 定向表达式 |
| payload 实体 / data 对应实体：expression[].type | string | 仅 asinSameAs / asinBrandSameAs |
| payload 实体 / data 对应实体：expression[].value | 原生值 | 表达式值，原样保留 |


## 接口：SD 创建商品广告

### 脚本输入与构参

| 转发属性 | 本操作约定 |
|---|---|
| method | POST |
| path | sd/productAds |
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
| payload | object / array | 是 | [{...}]；作为 body JSON 字符串发送。 |

依赖检测为本地文件检查：0 表示存在认证技能；42 且 stderr 含 `DEPENDENCY_MISSING:` 时先安装 `linkfox-amazon-ads-auth`。认证与运行限制见 [总览](../api.md)。

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

#### 实体字段

以下为常见实体字段；原生写操作按创建/更新要求取用，非所有字段都必填，未记录的必填规则不推定。

| 字段 | 类型 | 说明 |
|---|---|---|
| payload 实体 / data 对应实体：adId | number / string | 广告 ID |
| payload 实体 / data 对应实体：adGroupId | number / string | 广告组 ID |
| payload 实体 / data 对应实体：campaignId | number / string | 活动 ID |
| payload 实体 / data 对应实体：state | string | enabled / paused / archived；筛选入参兼容 ENABLED / PAUSED / ARCHIVED |
| payload 实体 / data 对应实体：asin | string | ASIN |
| payload 实体 / data 对应实体：sku | string | SKU |
| payload 实体 / data 对应实体：landingPageURL | string | 落地页 URL |
| payload 实体 / data 对应实体：landingPageType | string | 落地页类型 |


## 接口：SD 创建商品定向

### 脚本输入与构参

| 转发属性 | 本操作约定 |
|---|---|
| method | POST |
| path | sd/targets |
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
| payload | object / array | 是 | [{...}]；作为 body JSON 字符串发送。 |

依赖检测为本地文件检查：0 表示存在认证技能；42 且 stderr 含 `DEPENDENCY_MISSING:` 时先安装 `linkfox-amazon-ads-auth`。认证与运行限制见 [总览](../api.md)。

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

#### 实体字段

以下为常见实体字段；原生写操作按创建/更新要求取用，非所有字段都必填，未记录的必填规则不推定。

| 字段 | 类型 | 说明 |
|---|---|---|
| payload 实体 / data 对应实体：targetId | number / string | 定向 ID |
| payload 实体 / data 对应实体：adGroupId | number / string | 广告组 ID |
| payload 实体 / data 对应实体：campaignId | number / string | 活动 ID |
| payload 实体 / data 对应实体：state | string | enabled / paused / archived；筛选入参兼容 ENABLED / PAUSED / ARCHIVED |
| payload 实体 / data 对应实体：expressionType | string | auto / manual |
| payload 实体 / data 对应实体：expression | array | 定向表达式 |
| payload 实体 / data 对应实体：expression[].type | string | asinSameAs / asinCategorySameAs / audience / views / purchases 等 |
| payload 实体 / data 对应实体：expression[].value | 原生值 | 表达式值，原样保留 |
| payload 实体 / data 对应实体：bid | number | 出价 |


## 接口：SD 查询广告组

### 脚本输入与构参

| 转发属性 | 本操作约定 |
|---|---|
| method | GET |
| path | sd/adGroups；扩展：sd/adGroups/extended |
| contentType | GET 不传 |
| accept | 未显式指定 |

#### 脚本 JSON 参数与选项

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| profileId | integer/string | 是 | 从广告授权技能解析，不能要求用户报数字。 |
| region | string | 是 | NA / EU / FE。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已完成依赖检测时使用，不绕过授权。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存响应。 |
| --no-cache | CLI flag | 否 | 业务调用始终附加；响应缓存关闭。公共调用器会建立空缓存目录，但不读写响应缓存。 |
| fetchAll | boolean | 否 | 默认 true；传 JSON false 只取一页。 |
| maxResults | integer | 否 | 默认 100，单页 1–100；偏移分页对应 count 并钳制到 1–100；POST list 原样发给上游，由上游校验。 |
| includeExtendedDataFields | boolean | 否 | 默认 false；true 时切到本接口上表的 extended 路径。 |
| adGroupIdFilter | string / array / object | 否 | 接受字符串、数组或 {include:[...]}；ID 拼为逗号串，stateFilter 转小写；nameFilter 仅精确匹配并取首项。 |
| adGroupIdFilter.include | array<string> | 对象形态按过滤要求 | 包含的 ID、状态、匹配类型或文本值；字段本身允许数组/单值时按上述规则规范化。 |
| campaignIdFilter | string / array / object | 否 | 接受字符串、数组或 {include:[...]}；ID 拼为逗号串，stateFilter 转小写；nameFilter 仅精确匹配并取首项。 |
| campaignIdFilter.include | array<string> | 对象形态按过滤要求 | 包含的 ID、状态、匹配类型或文本值；字段本身允许数组/单值时按上述规则规范化。 |
| stateFilter | string / array / object | 否 | 接受字符串、数组或 {include:[...]}；ID 拼为逗号串，stateFilter 转小写；nameFilter 仅精确匹配并取首项。 |
| stateFilter.include | array<string> | 对象形态按过滤要求 | 包含的 ID、状态、匹配类型或文本值；字段本身允许数组/单值时按上述规则规范化。 |
| nameFilter | string / array / object | 否 | 接受字符串、数组或 {include:[...]}；ID 拼为逗号串，stateFilter 转小写；nameFilter 仅精确匹配并取首项。 |
| nameFilter.include | array<string> | 对象形态按过滤要求 | 包含的 ID、状态、匹配类型或文本值；字段本身允许数组/单值时按上述规则规范化。 |
| nameFilter.queryTermMatchType | string | 文本过滤按原生要求 | BROAD_MATCH / EXACT_MATCH；SD 仅精确匹配，其他模式会提示并取首项。 |

#### Amazon 查询串字段

| 字段 | 类型 | 必填 | 默认值与说明 |
|---|---|---|---|
| queryString.startIndex | integer | 否 | 默认 0；业务 CLI 从 0 开始，逐页增加 count，不接收顶层 startIndex。 |
| queryString.count | integer | 否 | 默认 100；CLI 由 maxResults 决定，钳制到 1–100。 |
| queryString.adGroupIdFilter | string | 否 | 对应 adGroupIdFilter；多个值以逗号连接后 URL 编码。 |
| queryString.campaignIdFilter | string | 否 | 对应 campaignIdFilter；多个值以逗号连接后 URL 编码。 |
| queryString.stateFilter | string | 否 | 对应 stateFilter；多个值以逗号连接，整体 URL 编码；状态转小写。 |
| queryString.name | string | 否 | 对应 nameFilter；仅取首项作精确匹配，特殊字符必须 URL 编码。 |

依赖检测为本地文件检查：0 表示存在认证技能；42 且 stderr 含 `DEPENDENCY_MISSING:` 时先安装 `linkfox-amazon-ads-auth`。认证与运行限制见 [总览](../api.md)。

分页：startIndex + count 从 0 递增，本页少于 count 结束。普通实体 CLI 使用固定 maxPages=50，不读取顶层 maxPages；达到上限时标记 truncated，不自动重试失败请求。

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

#### 实体字段

以下为常见实体字段；原生写操作按创建/更新要求取用，非所有字段都必填，未记录的必填规则不推定。

| 字段 | 类型 | 说明 |
|---|---|---|
| adGroups[].adGroupId | number / string | 广告组 ID |
| adGroups[].campaignId | number / string | 活动 ID |
| adGroups[].name | string | 名称 |
| adGroups[].state | string | enabled / paused / archived；筛选入参兼容 ENABLED / PAUSED / ARCHIVED |
| adGroups[].defaultBid | number | 默认出价 |
| adGroups[].bidOptimization | 原生值 | 竞价优化，类型按上游返回值处理 |
| adGroups[].creativeType | string | 创意类型，原样保留 |


## 接口：SD 查询预算规则

### 脚本输入与构参

| 转发属性 | 本操作约定 |
|---|---|
| method | GET |
| path | sd/budgetRules |
| contentType | GET 不传 |
| accept | 未显式指定 |

#### 脚本 JSON 参数与选项

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| profileId | integer/string | 是 | 从广告授权技能解析，不能要求用户报数字。 |
| region | string | 是 | NA / EU / FE。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已完成依赖检测时使用，不绕过授权。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存响应。 |
| --no-cache | CLI flag | 否 | 业务调用始终附加；响应缓存关闭。公共调用器会建立空缓存目录，但不读写响应缓存。 |
| fetchAll | boolean | 否 | 默认 true；传 JSON false 只取一页。 |
| maxPages | integer | 否 | 默认 50；达到上限停止并标记 truncated。 |
| nextToken | string | 否 | 起始续页令牌，默认不传；经 URL 编码加入 queryString，后续自动跟随。 |

#### Amazon 查询串字段

| 字段 | 类型 | 必填 | 默认值与说明 |
|---|---|---|---|
| queryString.nextToken | string | 否 | 默认不传；续页 token 必须 URL 编码，不直接拼接。 |

依赖检测为本地文件检查：0 表示存在认证技能；42 且 stderr 含 `DEPENDENCY_MISSING:` 时先安装 `linkfox-amazon-ads-auth`。认证与运行限制见 [总览](../api.md)。

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
| body.budgetRules / body.budgetRulesDetails | array | SP / SD 预算原生列表兼容字段。 |
| body.nextToken | string | 后续页令牌；脚本聚合后不一定回显。 |


## 接口：SD 查询广告活动

### 脚本输入与构参

| 转发属性 | 本操作约定 |
|---|---|
| method | GET |
| path | sd/campaigns；扩展：sd/campaigns/extended |
| contentType | GET 不传 |
| accept | 未显式指定 |

#### 脚本 JSON 参数与选项

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| profileId | integer/string | 是 | 从广告授权技能解析，不能要求用户报数字。 |
| region | string | 是 | NA / EU / FE。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已完成依赖检测时使用，不绕过授权。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存响应。 |
| --no-cache | CLI flag | 否 | 业务调用始终附加；响应缓存关闭。公共调用器会建立空缓存目录，但不读写响应缓存。 |
| fetchAll | boolean | 否 | 默认 true；传 JSON false 只取一页。 |
| maxResults | integer | 否 | 默认 100，单页 1–100；偏移分页对应 count 并钳制到 1–100；POST list 原样发给上游，由上游校验。 |
| includeExtendedDataFields | boolean | 否 | 默认 false；true 时切到本接口上表的 extended 路径。 |
| campaignIdFilter | string / array / object | 否 | 接受字符串、数组或 {include:[...]}；ID 拼为逗号串，stateFilter 转小写；nameFilter 仅精确匹配并取首项。 |
| campaignIdFilter.include | array<string> | 对象形态按过滤要求 | 包含的 ID、状态、匹配类型或文本值；字段本身允许数组/单值时按上述规则规范化。 |
| stateFilter | string / array / object | 否 | 接受字符串、数组或 {include:[...]}；ID 拼为逗号串，stateFilter 转小写；nameFilter 仅精确匹配并取首项。 |
| stateFilter.include | array<string> | 对象形态按过滤要求 | 包含的 ID、状态、匹配类型或文本值；字段本身允许数组/单值时按上述规则规范化。 |
| nameFilter | string / array / object | 否 | 接受字符串、数组或 {include:[...]}；ID 拼为逗号串，stateFilter 转小写；nameFilter 仅精确匹配并取首项。 |
| nameFilter.include | array<string> | 对象形态按过滤要求 | 包含的 ID、状态、匹配类型或文本值；字段本身允许数组/单值时按上述规则规范化。 |
| nameFilter.queryTermMatchType | string | 文本过滤按原生要求 | BROAD_MATCH / EXACT_MATCH；SD 仅精确匹配，其他模式会提示并取首项。 |
| portfolioIdFilter | string / array / object | 否 | 接受字符串、数组或 {include:[...]}；ID 拼为逗号串，stateFilter 转小写；nameFilter 仅精确匹配并取首项。 |
| portfolioIdFilter.include | array<string> | 对象形态按过滤要求 | 包含的 ID、状态、匹配类型或文本值；字段本身允许数组/单值时按上述规则规范化。 |

#### Amazon 查询串字段

| 字段 | 类型 | 必填 | 默认值与说明 |
|---|---|---|---|
| queryString.startIndex | integer | 否 | 默认 0；业务 CLI 从 0 开始，逐页增加 count，不接收顶层 startIndex。 |
| queryString.count | integer | 否 | 默认 100；CLI 由 maxResults 决定，钳制到 1–100。 |
| queryString.campaignIdFilter | string | 否 | 对应 campaignIdFilter；多个值以逗号连接后 URL 编码。 |
| queryString.stateFilter | string | 否 | 对应 stateFilter；多个值以逗号连接，整体 URL 编码；状态转小写。 |
| queryString.name | string | 否 | 对应 nameFilter；仅取首项作精确匹配，特殊字符必须 URL 编码。 |
| queryString.portfolioIdFilter | string | 否 | 对应 portfolioIdFilter；多个值以逗号连接后 URL 编码。 |

依赖检测为本地文件检查：0 表示存在认证技能；42 且 stderr 含 `DEPENDENCY_MISSING:` 时先安装 `linkfox-amazon-ads-auth`。认证与运行限制见 [总览](../api.md)。

分页：startIndex + count 从 0 递增，本页少于 count 结束。普通实体 CLI 使用固定 maxPages=50，不读取顶层 maxPages；达到上限时标记 truncated，不自动重试失败请求。

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

#### 实体字段

以下为常见实体字段；原生写操作按创建/更新要求取用，非所有字段都必填，未记录的必填规则不推定。

| 字段 | 类型 | 说明 |
|---|---|---|
| campaigns[].campaignId | number / string | 活动 ID |
| campaigns[].name | string | 名称 |
| campaigns[].state | string | enabled / paused / archived；筛选入参兼容 ENABLED / PAUSED / ARCHIVED |
| campaigns[].tactic | string | T00020 / T00030 |
| campaigns[].costType | string | cpc / vcpm |
| campaigns[].budget | number | 预算 |
| campaigns[].budgetType | string | 预算类型 |
| campaigns[].startDate | string | 开始日期 |
| campaigns[].endDate | string | 结束日期 |
| campaigns[].portfolioId | number / string | 组合 ID |


## 接口：SD 查询创意

### 脚本输入与构参

| 转发属性 | 本操作约定 |
|---|---|
| method | GET |
| path | sd/creatives |
| contentType | GET 不传 |
| accept | 未显式指定 |

#### 脚本 JSON 参数与选项

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| profileId | integer/string | 是 | 从广告授权技能解析，不能要求用户报数字。 |
| region | string | 是 | NA / EU / FE。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已完成依赖检测时使用，不绕过授权。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存响应。 |
| --no-cache | CLI flag | 否 | 业务调用始终附加；响应缓存关闭。公共调用器会建立空缓存目录，但不读写响应缓存。 |
| fetchAll | boolean | 否 | 默认 true；传 JSON false 只取一页。 |
| maxResults | integer | 否 | 默认 100，单页 1–100；偏移分页对应 count 并钳制到 1–100；POST list 原样发给上游，由上游校验。 |
| includeExtendedDataFields | boolean | 否 | 本接口无 extended 路径，传入不会生效。 |
| creativeIdFilter | string / array / object | 否 | 接受字符串、数组或 {include:[...]}；ID 拼为逗号串，stateFilter 转小写；nameFilter 仅精确匹配并取首项。 |
| creativeIdFilter.include | array<string> | 对象形态按过滤要求 | 包含的 ID、状态、匹配类型或文本值；字段本身允许数组/单值时按上述规则规范化。 |
| adGroupIdFilter | string / array / object | 否 | 接受字符串、数组或 {include:[...]}；ID 拼为逗号串，stateFilter 转小写；nameFilter 仅精确匹配并取首项。 |
| adGroupIdFilter.include | array<string> | 对象形态按过滤要求 | 包含的 ID、状态、匹配类型或文本值；字段本身允许数组/单值时按上述规则规范化。 |

#### Amazon 查询串字段

| 字段 | 类型 | 必填 | 默认值与说明 |
|---|---|---|---|
| queryString.startIndex | integer | 否 | 默认 0；业务 CLI 从 0 开始，逐页增加 count，不接收顶层 startIndex。 |
| queryString.count | integer | 否 | 默认 100；CLI 由 maxResults 决定，钳制到 1–100。 |
| queryString.creativeIdFilter | string | 否 | 对应 creativeIdFilter；多个值以逗号连接后 URL 编码。 |
| queryString.adGroupIdFilter | string | 否 | 对应 adGroupIdFilter；多个值以逗号连接后 URL 编码。 |

依赖检测为本地文件检查：0 表示存在认证技能；42 且 stderr 含 `DEPENDENCY_MISSING:` 时先安装 `linkfox-amazon-ads-auth`。认证与运行限制见 [总览](../api.md)。

creativeIdFilter 与 adGroupIdFilter 互斥；同时传会警告并透传，由上游返回 400 / 422；不得据此无限试探。

分页：startIndex + count 从 0 递增，本页少于 count 结束。普通实体 CLI 使用固定 maxPages=50，不读取顶层 maxPages；达到上限时标记 truncated，不自动重试失败请求。

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

#### 实体字段

以下为常见实体字段；原生写操作按创建/更新要求取用，非所有字段都必填，未记录的必填规则不推定。

| 字段 | 类型 | 说明 |
|---|---|---|
| creatives[].creativeId | number / string | 创意 ID |
| creatives[].adGroupId | number / string | 广告组 ID |
| creatives[].name | string | 名称 |
| creatives[].creativeType | string | 上游原值 |
| creatives[].properties | object | 依 creativeType 而异 |
| creatives[].properties.headline | string | 标题 |
| creatives[].properties.brandLogoAssetID | string | 品牌标识素材 ID |
| creatives[].properties.video | 原生值 | 视频资料，类型依创意而异 |
| creatives[].moderationStatus | 原生值 | 审核状态 |


## 接口：SD 查询否定定向

### 脚本输入与构参

| 转发属性 | 本操作约定 |
|---|---|
| method | GET |
| path | sd/negativeTargets；扩展：sd/negativeTargets/extended |
| contentType | GET 不传 |
| accept | 未显式指定 |

#### 脚本 JSON 参数与选项

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| profileId | integer/string | 是 | 从广告授权技能解析，不能要求用户报数字。 |
| region | string | 是 | NA / EU / FE。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已完成依赖检测时使用，不绕过授权。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存响应。 |
| --no-cache | CLI flag | 否 | 业务调用始终附加；响应缓存关闭。公共调用器会建立空缓存目录，但不读写响应缓存。 |
| fetchAll | boolean | 否 | 默认 true；传 JSON false 只取一页。 |
| maxResults | integer | 否 | 默认 100，单页 1–100；偏移分页对应 count 并钳制到 1–100；POST list 原样发给上游，由上游校验。 |
| includeExtendedDataFields | boolean | 否 | 默认 false；true 时切到本接口上表的 extended 路径。 |
| adGroupIdFilter | string / array / object | 否 | 接受字符串、数组或 {include:[...]}；ID 拼为逗号串，stateFilter 转小写；nameFilter 仅精确匹配并取首项。 |
| adGroupIdFilter.include | array<string> | 对象形态按过滤要求 | 包含的 ID、状态、匹配类型或文本值；字段本身允许数组/单值时按上述规则规范化。 |
| campaignIdFilter | string / array / object | 否 | 接受字符串、数组或 {include:[...]}；ID 拼为逗号串，stateFilter 转小写；nameFilter 仅精确匹配并取首项。 |
| campaignIdFilter.include | array<string> | 对象形态按过滤要求 | 包含的 ID、状态、匹配类型或文本值；字段本身允许数组/单值时按上述规则规范化。 |
| stateFilter | string / array / object | 否 | 接受字符串、数组或 {include:[...]}；ID 拼为逗号串，stateFilter 转小写；nameFilter 仅精确匹配并取首项。 |
| stateFilter.include | array<string> | 对象形态按过滤要求 | 包含的 ID、状态、匹配类型或文本值；字段本身允许数组/单值时按上述规则规范化。 |

#### Amazon 查询串字段

| 字段 | 类型 | 必填 | 默认值与说明 |
|---|---|---|---|
| queryString.startIndex | integer | 否 | 默认 0；业务 CLI 从 0 开始，逐页增加 count，不接收顶层 startIndex。 |
| queryString.count | integer | 否 | 默认 100；CLI 由 maxResults 决定，钳制到 1–100。 |
| queryString.adGroupIdFilter | string | 否 | 对应 adGroupIdFilter；多个值以逗号连接后 URL 编码。 |
| queryString.campaignIdFilter | string | 否 | 对应 campaignIdFilter；多个值以逗号连接后 URL 编码。 |
| queryString.stateFilter | string | 否 | 对应 stateFilter；多个值以逗号连接，整体 URL 编码；状态转小写。 |

依赖检测为本地文件检查：0 表示存在认证技能；42 且 stderr 含 `DEPENDENCY_MISSING:` 时先安装 `linkfox-amazon-ads-auth`。认证与运行限制见 [总览](../api.md)。

分页：startIndex + count 从 0 递增，本页少于 count 结束。普通实体 CLI 使用固定 maxPages=50，不读取顶层 maxPages；达到上限时标记 truncated，不自动重试失败请求。

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
| negativeTargetingClauses | array<object> | 聚合实体数组，保留返回字段。 |
| total | integer | 本次聚合、客户端过滤后的实体数，不是上游全量总数。 |
| pagesFetched | integer | 已取得页数。 |
| truncated | boolean | 达到页数限制或保留部分结果；为 true 时必须告知数据未取完。 |

#### 实体字段

以下为常见实体字段；原生写操作按创建/更新要求取用，非所有字段都必填，未记录的必填规则不推定。

| 字段 | 类型 | 说明 |
|---|---|---|
| negativeTargetingClauses[].targetId | number / string | 定向 ID |
| negativeTargetingClauses[].adGroupId | number / string | 广告组 ID |
| negativeTargetingClauses[].campaignId | number / string | 活动 ID |
| negativeTargetingClauses[].state | string | enabled / paused / archived；筛选入参兼容 ENABLED / PAUSED / ARCHIVED |
| negativeTargetingClauses[].expression | array | 定向表达式 |
| negativeTargetingClauses[].expression[].type | string | 仅 asinSameAs / asinBrandSameAs |
| negativeTargetingClauses[].expression[].value | 原生值 | 表达式值，原样保留 |


## 接口：SD 查询商品广告

### 脚本输入与构参

| 转发属性 | 本操作约定 |
|---|---|
| method | GET |
| path | sd/productAds；扩展：sd/productAds/extended |
| contentType | GET 不传 |
| accept | 未显式指定 |

#### 脚本 JSON 参数与选项

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| profileId | integer/string | 是 | 从广告授权技能解析，不能要求用户报数字。 |
| region | string | 是 | NA / EU / FE。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已完成依赖检测时使用，不绕过授权。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存响应。 |
| --no-cache | CLI flag | 否 | 业务调用始终附加；响应缓存关闭。公共调用器会建立空缓存目录，但不读写响应缓存。 |
| fetchAll | boolean | 否 | 默认 true；传 JSON false 只取一页。 |
| maxResults | integer | 否 | 默认 100，单页 1–100；偏移分页对应 count 并钳制到 1–100；POST list 原样发给上游，由上游校验。 |
| includeExtendedDataFields | boolean | 否 | 默认 false；true 时切到本接口上表的 extended 路径。 |
| adIdFilter | string / array / object | 否 | 接受字符串、数组或 {include:[...]}；ID 拼为逗号串，stateFilter 转小写；nameFilter 仅精确匹配并取首项。 |
| adIdFilter.include | array<string> | 对象形态按过滤要求 | 包含的 ID、状态、匹配类型或文本值；字段本身允许数组/单值时按上述规则规范化。 |
| adGroupIdFilter | string / array / object | 否 | 接受字符串、数组或 {include:[...]}；ID 拼为逗号串，stateFilter 转小写；nameFilter 仅精确匹配并取首项。 |
| adGroupIdFilter.include | array<string> | 对象形态按过滤要求 | 包含的 ID、状态、匹配类型或文本值；字段本身允许数组/单值时按上述规则规范化。 |
| campaignIdFilter | string / array / object | 否 | 接受字符串、数组或 {include:[...]}；ID 拼为逗号串，stateFilter 转小写；nameFilter 仅精确匹配并取首项。 |
| campaignIdFilter.include | array<string> | 对象形态按过滤要求 | 包含的 ID、状态、匹配类型或文本值；字段本身允许数组/单值时按上述规则规范化。 |
| stateFilter | string / array / object | 否 | 接受字符串、数组或 {include:[...]}；ID 拼为逗号串，stateFilter 转小写；nameFilter 仅精确匹配并取首项。 |
| stateFilter.include | array<string> | 对象形态按过滤要求 | 包含的 ID、状态、匹配类型或文本值；字段本身允许数组/单值时按上述规则规范化。 |
| asinFilter | object / array / string | 否 | 客户端按 asin 精确匹配；不发给上游。建议同时带 campaignIdFilter / adGroupIdFilter / adIdFilter 收窄，缺少时 stderr 提示。 |
| asinFilter.include | array<string> | 对象形态按过滤要求 | 包含的 ID、状态、匹配类型或文本值；字段本身允许数组/单值时按上述规则规范化。 |
| skuFilter | object / array / string | 否 | 客户端按 sku 精确匹配；不发给上游；与其他客户端过滤取交集。 |
| skuFilter.include | array<string> | 对象形态按过滤要求 | 包含的 ID、状态、匹配类型或文本值；字段本身允许数组/单值时按上述规则规范化。 |

#### Amazon 查询串字段

| 字段 | 类型 | 必填 | 默认值与说明 |
|---|---|---|---|
| queryString.startIndex | integer | 否 | 默认 0；业务 CLI 从 0 开始，逐页增加 count，不接收顶层 startIndex。 |
| queryString.count | integer | 否 | 默认 100；CLI 由 maxResults 决定，钳制到 1–100。 |
| queryString.adIdFilter | string | 否 | 对应 adIdFilter；多个值以逗号连接后 URL 编码。 |
| queryString.adGroupIdFilter | string | 否 | 对应 adGroupIdFilter；多个值以逗号连接后 URL 编码。 |
| queryString.campaignIdFilter | string | 否 | 对应 campaignIdFilter；多个值以逗号连接后 URL 编码。 |
| queryString.stateFilter | string | 否 | 对应 stateFilter；多个值以逗号连接，整体 URL 编码；状态转小写。 |

依赖检测为本地文件检查：0 表示存在认证技能；42 且 stderr 含 `DEPENDENCY_MISSING:` 时先安装 `linkfox-amazon-ads-auth`。认证与运行限制见 [总览](../api.md)。

分页：startIndex + count 从 0 递增，本页少于 count 结束。普通实体 CLI 使用固定 maxPages=50，不读取顶层 maxPages；达到上限时标记 truncated，不自动重试失败请求。

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
| productAds | array<object> | 聚合实体数组，保留返回字段。 |
| total | integer | 本次聚合、客户端过滤后的实体数，不是上游全量总数。 |
| pagesFetched | integer | 已取得页数。 |
| truncated | boolean | 达到页数限制或保留部分结果；为 true 时必须告知数据未取完。 |
| serverTotalBeforeClientFilter | integer | 客户端过滤前已取得的总数。 |
| clientSideFilters | object | 实际应用的 asinFilter / skuFilter 数组。 |
| clientSideFilters.asinFilter | array<string> | 实际匹配的 ASIN 值，存在相应筛选时返回。 |
| clientSideFilters.skuFilter | array<string> | 实际匹配的 SKU 值，存在相应筛选时返回。 |

#### 实体字段

以下为常见实体字段；原生写操作按创建/更新要求取用，非所有字段都必填，未记录的必填规则不推定。

| 字段 | 类型 | 说明 |
|---|---|---|
| productAds[].adId | number / string | 广告 ID |
| productAds[].adGroupId | number / string | 广告组 ID |
| productAds[].campaignId | number / string | 活动 ID |
| productAds[].state | string | enabled / paused / archived；筛选入参兼容 ENABLED / PAUSED / ARCHIVED |
| productAds[].asin | string | ASIN |
| productAds[].sku | string | SKU |
| productAds[].landingPageURL | string | 落地页 URL |
| productAds[].landingPageType | string | 落地页类型 |


## 接口：SD 查询商品定向

### 脚本输入与构参

| 转发属性 | 本操作约定 |
|---|---|
| method | GET |
| path | sd/targets；扩展：sd/targets/extended |
| contentType | GET 不传 |
| accept | 未显式指定 |

#### 脚本 JSON 参数与选项

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| profileId | integer/string | 是 | 从广告授权技能解析，不能要求用户报数字。 |
| region | string | 是 | NA / EU / FE。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已完成依赖检测时使用，不绕过授权。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存响应。 |
| --no-cache | CLI flag | 否 | 业务调用始终附加；响应缓存关闭。公共调用器会建立空缓存目录，但不读写响应缓存。 |
| fetchAll | boolean | 否 | 默认 true；传 JSON false 只取一页。 |
| maxResults | integer | 否 | 默认 100，单页 1–100；偏移分页对应 count 并钳制到 1–100；POST list 原样发给上游，由上游校验。 |
| includeExtendedDataFields | boolean | 否 | 默认 false；true 时切到本接口上表的 extended 路径。 |
| targetIdFilter | string / array / object | 否 | 接受字符串、数组或 {include:[...]}；ID 拼为逗号串，stateFilter 转小写；nameFilter 仅精确匹配并取首项。 |
| targetIdFilter.include | array<string> | 对象形态按过滤要求 | 包含的 ID、状态、匹配类型或文本值；字段本身允许数组/单值时按上述规则规范化。 |
| adGroupIdFilter | string / array / object | 否 | 接受字符串、数组或 {include:[...]}；ID 拼为逗号串，stateFilter 转小写；nameFilter 仅精确匹配并取首项。 |
| adGroupIdFilter.include | array<string> | 对象形态按过滤要求 | 包含的 ID、状态、匹配类型或文本值；字段本身允许数组/单值时按上述规则规范化。 |
| campaignIdFilter | string / array / object | 否 | 接受字符串、数组或 {include:[...]}；ID 拼为逗号串，stateFilter 转小写；nameFilter 仅精确匹配并取首项。 |
| campaignIdFilter.include | array<string> | 对象形态按过滤要求 | 包含的 ID、状态、匹配类型或文本值；字段本身允许数组/单值时按上述规则规范化。 |
| stateFilter | string / array / object | 否 | 接受字符串、数组或 {include:[...]}；ID 拼为逗号串，stateFilter 转小写；nameFilter 仅精确匹配并取首项。 |
| stateFilter.include | array<string> | 对象形态按过滤要求 | 包含的 ID、状态、匹配类型或文本值；字段本身允许数组/单值时按上述规则规范化。 |

#### Amazon 查询串字段

| 字段 | 类型 | 必填 | 默认值与说明 |
|---|---|---|---|
| queryString.startIndex | integer | 否 | 默认 0；业务 CLI 从 0 开始，逐页增加 count，不接收顶层 startIndex。 |
| queryString.count | integer | 否 | 默认 100；CLI 由 maxResults 决定，钳制到 1–100。 |
| queryString.targetIdFilter | string | 否 | 对应 targetIdFilter；多个值以逗号连接后 URL 编码。 |
| queryString.adGroupIdFilter | string | 否 | 对应 adGroupIdFilter；多个值以逗号连接后 URL 编码。 |
| queryString.campaignIdFilter | string | 否 | 对应 campaignIdFilter；多个值以逗号连接后 URL 编码。 |
| queryString.stateFilter | string | 否 | 对应 stateFilter；多个值以逗号连接，整体 URL 编码；状态转小写。 |

依赖检测为本地文件检查：0 表示存在认证技能；42 且 stderr 含 `DEPENDENCY_MISSING:` 时先安装 `linkfox-amazon-ads-auth`。认证与运行限制见 [总览](../api.md)。

分页：startIndex + count 从 0 递增，本页少于 count 结束。普通实体 CLI 使用固定 maxPages=50，不读取顶层 maxPages；达到上限时标记 truncated，不自动重试失败请求。

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
| targetingClauses | array<object> | 聚合实体数组，保留返回字段。 |
| total | integer | 本次聚合、客户端过滤后的实体数，不是上游全量总数。 |
| pagesFetched | integer | 已取得页数。 |
| truncated | boolean | 达到页数限制或保留部分结果；为 true 时必须告知数据未取完。 |

#### 实体字段

以下为常见实体字段；原生写操作按创建/更新要求取用，非所有字段都必填，未记录的必填规则不推定。

| 字段 | 类型 | 说明 |
|---|---|---|
| targetingClauses[].targetId | number / string | 定向 ID |
| targetingClauses[].adGroupId | number / string | 广告组 ID |
| targetingClauses[].campaignId | number / string | 活动 ID |
| targetingClauses[].state | string | enabled / paused / archived；筛选入参兼容 ENABLED / PAUSED / ARCHIVED |
| targetingClauses[].expressionType | string | auto / manual |
| targetingClauses[].expression | array | 定向表达式 |
| targetingClauses[].expression[].type | string | asinSameAs / asinCategorySameAs / audience / views / purchases 等 |
| targetingClauses[].expression[].value | 原生值 | 表达式值，原样保留 |
| targetingClauses[].bid | number | 出价 |


## 接口：SD 修改广告组

### 脚本输入与构参

| 转发属性 | 本操作约定 |
|---|---|
| method | PUT |
| path | sd/adGroups |
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
| payload | object / array | 是 | [{"adGroupId":123,...}]；作为 body JSON 字符串发送。 |

依赖检测为本地文件检查：0 表示存在认证技能；42 且 stderr 含 `DEPENDENCY_MISSING:` 时先安装 `linkfox-amazon-ads-auth`。认证与运行限制见 [总览](../api.md)。

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

#### 实体字段

以下为常见实体字段；原生写操作按创建/更新要求取用，非所有字段都必填，未记录的必填规则不推定。

| 字段 | 类型 | 说明 |
|---|---|---|
| payload 实体 / data 对应实体：adGroupId | number / string | 广告组 ID |
| payload 实体 / data 对应实体：campaignId | number / string | 活动 ID |
| payload 实体 / data 对应实体：name | string | 名称 |
| payload 实体 / data 对应实体：state | string | enabled / paused / archived；筛选入参兼容 ENABLED / PAUSED / ARCHIVED |
| payload 实体 / data 对应实体：defaultBid | number | 默认出价 |
| payload 实体 / data 对应实体：bidOptimization | 原生值 | 竞价优化，类型按上游返回值处理 |
| payload 实体 / data 对应实体：creativeType | string | 创意类型，原样保留 |


## 接口：SD 修改预算规则

### 脚本输入与构参

| 转发属性 | 本操作约定 |
|---|---|
| method | PUT |
| path | sd/budgetRules |
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
| payload | object / array | 是 | {"budgetRulesDetails":[{"ruleId":"...",...}]}；作为 body JSON 字符串发送。 |
| payload.budgetRulesDetails | array<object> | 按原生操作 | 预算规则数组 |
| 规则[].ruleId | string | 更新时按原生要求 | 规则 ID |
| 规则[].name | string | 按原生操作 | 规则名 |
| 规则[].ruleType | string | 按原生操作 | 示例 SCHEDULE |
| 规则[].duration | object | 按原生操作 | 生效周期，子字段按 Amazon 原生请求要求传入 |
| 规则[].budgetIncreaseBy | object | 按原生操作 | 预算提升设置，子字段按 Amazon 原生请求要求传入 |

依赖检测为本地文件检查：0 表示存在认证技能；42 且 stderr 含 `DEPENDENCY_MISSING:` 时先安装 `linkfox-amazon-ads-auth`。认证与运行限制见 [总览](../api.md)。

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


## 接口：SD 修改广告活动

### 脚本输入与构参

| 转发属性 | 本操作约定 |
|---|---|
| method | PUT |
| path | sd/campaigns |
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
| payload | object / array | 是 | [{"campaignId":123,...}]；作为 body JSON 字符串发送。 |

依赖检测为本地文件检查：0 表示存在认证技能；42 且 stderr 含 `DEPENDENCY_MISSING:` 时先安装 `linkfox-amazon-ads-auth`。认证与运行限制见 [总览](../api.md)。

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

#### 实体字段

以下为常见实体字段；原生写操作按创建/更新要求取用，非所有字段都必填，未记录的必填规则不推定。

| 字段 | 类型 | 说明 |
|---|---|---|
| payload 实体 / data 对应实体：campaignId | number / string | 活动 ID |
| payload 实体 / data 对应实体：name | string | 名称 |
| payload 实体 / data 对应实体：state | string | enabled / paused / archived；筛选入参兼容 ENABLED / PAUSED / ARCHIVED |
| payload 实体 / data 对应实体：tactic | string | T00020 / T00030 |
| payload 实体 / data 对应实体：costType | string | cpc / vcpm |
| payload 实体 / data 对应实体：budget | number | 预算 |
| payload 实体 / data 对应实体：budgetType | string | 预算类型 |
| payload 实体 / data 对应实体：startDate | string | 开始日期 |
| payload 实体 / data 对应实体：endDate | string | 结束日期 |
| payload 实体 / data 对应实体：portfolioId | number / string | 组合 ID |


## 接口：SD 修改创意

### 脚本输入与构参

| 转发属性 | 本操作约定 |
|---|---|
| method | PUT |
| path | sd/creatives |
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
| payload | object / array | 是 | [{"creativeId":"...",...}]；作为 body JSON 字符串发送。 |
| payload[].adGroupId | number / string | 按原生要求 | 广告组 ID |
| payload[].type | string | 按原生要求 | 创意类型 |
| payload[].properties | object | 按原生要求 | 创意属性 |

依赖检测为本地文件检查：0 表示存在认证技能；42 且 stderr 含 `DEPENDENCY_MISSING:` 时先安装 `linkfox-amazon-ads-auth`。认证与运行限制见 [总览](../api.md)。

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

#### 实体字段

以下为常见实体字段；原生写操作按创建/更新要求取用，非所有字段都必填，未记录的必填规则不推定。

| 字段 | 类型 | 说明 |
|---|---|---|
| payload 实体 / data 对应实体：creativeId | number / string | 创意 ID |
| payload 实体 / data 对应实体：adGroupId | number / string | 广告组 ID |
| payload 实体 / data 对应实体：name | string | 名称 |
| payload 实体 / data 对应实体：creativeType | string | 上游原值 |
| payload 实体 / data 对应实体：properties | object | 依 creativeType 而异 |
| payload 实体 / data 对应实体：properties.headline | string | 标题 |
| payload 实体 / data 对应实体：properties.brandLogoAssetID | string | 品牌标识素材 ID |
| payload 实体 / data 对应实体：properties.video | 原生值 | 视频资料，类型依创意而异 |
| payload 实体 / data 对应实体：moderationStatus | 原生值 | 审核状态 |


## 接口：SD 修改否定定向

### 脚本输入与构参

| 转发属性 | 本操作约定 |
|---|---|
| method | PUT |
| path | sd/negativeTargets |
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
| payload | object / array | 是 | [{"targetId":123,...}]；作为 body JSON 字符串发送。 |

依赖检测为本地文件检查：0 表示存在认证技能；42 且 stderr 含 `DEPENDENCY_MISSING:` 时先安装 `linkfox-amazon-ads-auth`。认证与运行限制见 [总览](../api.md)。

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

#### 实体字段

以下为常见实体字段；原生写操作按创建/更新要求取用，非所有字段都必填，未记录的必填规则不推定。

| 字段 | 类型 | 说明 |
|---|---|---|
| payload 实体 / data 对应实体：targetId | number / string | 定向 ID |
| payload 实体 / data 对应实体：adGroupId | number / string | 广告组 ID |
| payload 实体 / data 对应实体：campaignId | number / string | 活动 ID |
| payload 实体 / data 对应实体：state | string | enabled / paused / archived；筛选入参兼容 ENABLED / PAUSED / ARCHIVED |
| payload 实体 / data 对应实体：expression | array | 定向表达式 |
| payload 实体 / data 对应实体：expression[].type | string | 仅 asinSameAs / asinBrandSameAs |
| payload 实体 / data 对应实体：expression[].value | 原生值 | 表达式值，原样保留 |


## 接口：SD 修改商品广告

### 脚本输入与构参

| 转发属性 | 本操作约定 |
|---|---|
| method | PUT |
| path | sd/productAds |
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
| payload | object / array | 是 | [{"adId":123,...}]；作为 body JSON 字符串发送。 |

依赖检测为本地文件检查：0 表示存在认证技能；42 且 stderr 含 `DEPENDENCY_MISSING:` 时先安装 `linkfox-amazon-ads-auth`。认证与运行限制见 [总览](../api.md)。

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

#### 实体字段

以下为常见实体字段；原生写操作按创建/更新要求取用，非所有字段都必填，未记录的必填规则不推定。

| 字段 | 类型 | 说明 |
|---|---|---|
| payload 实体 / data 对应实体：adId | number / string | 广告 ID |
| payload 实体 / data 对应实体：adGroupId | number / string | 广告组 ID |
| payload 实体 / data 对应实体：campaignId | number / string | 活动 ID |
| payload 实体 / data 对应实体：state | string | enabled / paused / archived；筛选入参兼容 ENABLED / PAUSED / ARCHIVED |
| payload 实体 / data 对应实体：asin | string | ASIN |
| payload 实体 / data 对应实体：sku | string | SKU |
| payload 实体 / data 对应实体：landingPageURL | string | 落地页 URL |
| payload 实体 / data 对应实体：landingPageType | string | 落地页类型 |


## 接口：SD 修改商品定向

### 脚本输入与构参

| 转发属性 | 本操作约定 |
|---|---|
| method | PUT |
| path | sd/targets |
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
| payload | object / array | 是 | [{"targetId":123,"bid":0.8}]；作为 body JSON 字符串发送。 |

依赖检测为本地文件检查：0 表示存在认证技能；42 且 stderr 含 `DEPENDENCY_MISSING:` 时先安装 `linkfox-amazon-ads-auth`。认证与运行限制见 [总览](../api.md)。

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

#### 实体字段

以下为常见实体字段；原生写操作按创建/更新要求取用，非所有字段都必填，未记录的必填规则不推定。

| 字段 | 类型 | 说明 |
|---|---|---|
| payload 实体 / data 对应实体：targetId | number / string | 定向 ID |
| payload 实体 / data 对应实体：adGroupId | number / string | 广告组 ID |
| payload 实体 / data 对应实体：campaignId | number / string | 活动 ID |
| payload 实体 / data 对应实体：state | string | enabled / paused / archived；筛选入参兼容 ENABLED / PAUSED / ARCHIVED |
| payload 实体 / data 对应实体：expressionType | string | auto / manual |
| payload 实体 / data 对应实体：expression | array | 定向表达式 |
| payload 实体 / data 对应实体：expression[].type | string | asinSameAs / asinCategorySameAs / audience / views / purchases 等 |
| payload 实体 / data 对应实体：expression[].value | 原生值 | 表达式值，原样保留 |
| payload 实体 / data 对应实体：bid | number | 出价 |
