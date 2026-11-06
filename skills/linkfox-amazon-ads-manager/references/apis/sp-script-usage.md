# 脚本输入、构参与本地结果

profileId 接收 Long 范围内的正整数或十进制数字字符串，发送到网关时为 integer；不接受布尔值、小数、零、负数或越界值。

网关接口定义见 [sp.md](sp.md)。以下表格描述脚本参数、构参或本地解析行为；不作为网关DTO或上游完整schema。

## 接口：SP 创建广告组

### 脚本输入与构参

| 转发属性 | 本操作约定 |
|---|---|
| method | POST |
| path | sp/adGroups |
| contentType | application/vnd.spAdGroup.v3+json |
| accept | 未显式指定 |

#### 脚本 JSON 参数与选项

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| profileId | integer/string | 是 | 从广告授权技能解析，不能要求用户报数字。 |
| region | string | 是 | NA / EU / FE。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已完成依赖检测时使用，不绕过授权。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存响应。 |
| --no-cache | CLI flag | 否 | 业务调用始终附加；响应缓存关闭。公共调用器会建立空缓存目录，但不读写响应缓存。 |
| payload | object / array | 是 | {"adGroups":[{...}]}；作为 body JSON 字符串发送。 |

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
| payload 实体 / data 对应实体：state | string | ENABLED / PAUSED / ARCHIVED |
| payload 实体 / data 对应实体：defaultBid | number | 默认出价 |


## 接口：SP 创建预算规则

### 脚本输入与构参

| 转发属性 | 本操作约定 |
|---|---|
| method | POST |
| path | sp/budgetRules |
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
| payload | object / array | 是 | {"budgetRules":[{"name":"...","ruleType":"SCHEDULE","duration":{...},"budgetIncreaseBy":{...}}]}；作为 body JSON 字符串发送。 |
| payload.budgetRules | array<object> | 按原生操作 | 预算规则数组 |
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


## 接口：SP 创建预算规则关联

### 脚本输入与构参

| 转发属性 | 本操作约定 |
|---|---|
| method | POST |
| path | sp/budgetRulesAssociation |
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
| payload | object / array | 是 | {"budgetRulesAssociations":[{"ruleId":"...","campaignIds":[...]}]}；作为 body JSON 字符串发送。 |
| payload.budgetRulesAssociations | array<object> | 是 | 规则关联数组 |
| payload.budgetRulesAssociations[].ruleId | string | 是 | 规则 ID |
| payload.budgetRulesAssociations[].campaignIds | array | 是 | 活动 ID 列表 |

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


## 接口：SP 创建活动级否定关键词

### 脚本输入与构参

| 转发属性 | 本操作约定 |
|---|---|
| method | POST |
| path | sp/campaignNegativeKeywords |
| contentType | application/vnd.spCampaignNegativeKeyword.v3+json |
| accept | 未显式指定 |

#### 脚本 JSON 参数与选项

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| profileId | integer/string | 是 | 从广告授权技能解析，不能要求用户报数字。 |
| region | string | 是 | NA / EU / FE。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已完成依赖检测时使用，不绕过授权。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存响应。 |
| --no-cache | CLI flag | 否 | 业务调用始终附加；响应缓存关闭。公共调用器会建立空缓存目录，但不读写响应缓存。 |
| payload | object / array | 是 | {"campaignNegativeKeywords":[{...}]}；作为 body JSON 字符串发送。 |

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
| payload 实体 / data 对应实体：keywordId | number / string | 关键词 ID |
| payload 实体 / data 对应实体：adGroupId | number / string | 广告组 ID |
| payload 实体 / data 对应实体：campaignId | number / string | 活动 ID |
| payload 实体 / data 对应实体：keywordText | string | 关键词文本 |
| payload 实体 / data 对应实体：matchType | string | NEGATIVE_EXACT / NEGATIVE_PHRASE |
| payload 实体 / data 对应实体：state | string | ENABLED / PAUSED / ARCHIVED |
| payload 实体 / data 对应实体：bid | number | 出价 |


## 接口：SP 创建活动级否定定向

### 脚本输入与构参

| 转发属性 | 本操作约定 |
|---|---|
| method | POST |
| path | sp/campaignNegativeTargets |
| contentType | application/vnd.spCampaignNegativeTargetingClause.v3+json |
| accept | 未显式指定 |

#### 脚本 JSON 参数与选项

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| profileId | integer/string | 是 | 从广告授权技能解析，不能要求用户报数字。 |
| region | string | 是 | NA / EU / FE。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已完成依赖检测时使用，不绕过授权。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存响应。 |
| --no-cache | CLI flag | 否 | 业务调用始终附加；响应缓存关闭。公共调用器会建立空缓存目录，但不读写响应缓存。 |
| payload | object / array | 是 | {"campaignNegativeTargetingClauses":[{...}]}；作为 body JSON 字符串发送。 |

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
| payload 实体 / data 对应实体：state | string | ENABLED / PAUSED / ARCHIVED |
| payload 实体 / data 对应实体：expression | array | 定向表达式，内容原样保留 |
| payload 实体 / data 对应实体：expressionType | string | AUTO / MANUAL |
| payload 实体 / data 对应实体：bid | number | 出价 |


## 接口：SP 创建广告活动

### 脚本输入与构参

| 转发属性 | 本操作约定 |
|---|---|
| method | POST |
| path | sp/campaigns |
| contentType | application/vnd.spCampaign.v3+json |
| accept | 未显式指定 |

#### 脚本 JSON 参数与选项

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| profileId | integer/string | 是 | 从广告授权技能解析，不能要求用户报数字。 |
| region | string | 是 | NA / EU / FE。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已完成依赖检测时使用，不绕过授权。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存响应。 |
| --no-cache | CLI flag | 否 | 业务调用始终附加；响应缓存关闭。公共调用器会建立空缓存目录，但不读写响应缓存。 |
| payload | object / array | 是 | {"campaigns":[{...}]}；作为 body JSON 字符串发送。 |

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
| payload 实体 / data 对应实体：state | string | ENABLED / PAUSED / ARCHIVED |
| payload 实体 / data 对应实体：targetingType | string | 定向方式 |
| payload 实体 / data 对应实体：budget | object | 预算对象 |
| payload 实体 / data 对应实体：budget.budget | number | 预算值 |
| payload 实体 / data 对应实体：budget.budgetType | string | 预算类型 |
| payload 实体 / data 对应实体：startDate | string | 开始日期 |
| payload 实体 / data 对应实体：endDate | string | 结束日期 |
| payload 实体 / data 对应实体：dynamicBidding | object | 动态竞价 |
| payload 实体 / data 对应实体：dynamicBidding.strategy | string | 动态竞价策略 |
| payload 实体 / data 对应实体：portfolioId | number / string | 组合 ID |


## 接口：SP 创建关键词

### 脚本输入与构参

| 转发属性 | 本操作约定 |
|---|---|
| method | POST |
| path | sp/keywords |
| contentType | application/vnd.spKeyword.v3+json |
| accept | 未显式指定 |

#### 脚本 JSON 参数与选项

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| profileId | integer/string | 是 | 从广告授权技能解析，不能要求用户报数字。 |
| region | string | 是 | NA / EU / FE。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已完成依赖检测时使用，不绕过授权。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存响应。 |
| --no-cache | CLI flag | 否 | 业务调用始终附加；响应缓存关闭。公共调用器会建立空缓存目录，但不读写响应缓存。 |
| payload | object / array | 是 | {"keywords":[{...}]}；作为 body JSON 字符串发送。 |

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
| payload 实体 / data 对应实体：keywordId | number / string | 关键词 ID |
| payload 实体 / data 对应实体：adGroupId | number / string | 广告组 ID |
| payload 实体 / data 对应实体：campaignId | number / string | 活动 ID |
| payload 实体 / data 对应实体：keywordText | string | 关键词文本 |
| payload 实体 / data 对应实体：matchType | string | BROAD / PHRASE / EXACT |
| payload 实体 / data 对应实体：state | string | ENABLED / PAUSED / ARCHIVED |
| payload 实体 / data 对应实体：bid | number | 出价 |


## 接口：SP 创建否定关键词

### 脚本输入与构参

| 转发属性 | 本操作约定 |
|---|---|
| method | POST |
| path | sp/negativeKeywords |
| contentType | application/vnd.spNegativeKeyword.v3+json |
| accept | 未显式指定 |

#### 脚本 JSON 参数与选项

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| profileId | integer/string | 是 | 从广告授权技能解析，不能要求用户报数字。 |
| region | string | 是 | NA / EU / FE。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已完成依赖检测时使用，不绕过授权。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存响应。 |
| --no-cache | CLI flag | 否 | 业务调用始终附加；响应缓存关闭。公共调用器会建立空缓存目录，但不读写响应缓存。 |
| payload | object / array | 是 | {"negativeKeywords":[{...}]}；作为 body JSON 字符串发送。 |

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
| payload 实体 / data 对应实体：keywordId | number / string | 关键词 ID |
| payload 实体 / data 对应实体：adGroupId | number / string | 广告组 ID |
| payload 实体 / data 对应实体：campaignId | number / string | 活动 ID |
| payload 实体 / data 对应实体：keywordText | string | 关键词文本 |
| payload 实体 / data 对应实体：matchType | string | NEGATIVE_EXACT / NEGATIVE_PHRASE |
| payload 实体 / data 对应实体：state | string | ENABLED / PAUSED / ARCHIVED |
| payload 实体 / data 对应实体：bid | number | 出价 |


## 接口：SP 创建否定定向

### 脚本输入与构参

| 转发属性 | 本操作约定 |
|---|---|
| method | POST |
| path | sp/negativeTargets |
| contentType | application/vnd.spNegativeTargetingClause.v3+json |
| accept | 未显式指定 |

#### 脚本 JSON 参数与选项

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| profileId | integer/string | 是 | 从广告授权技能解析，不能要求用户报数字。 |
| region | string | 是 | NA / EU / FE。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已完成依赖检测时使用，不绕过授权。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存响应。 |
| --no-cache | CLI flag | 否 | 业务调用始终附加；响应缓存关闭。公共调用器会建立空缓存目录，但不读写响应缓存。 |
| payload | object / array | 是 | {"negativeTargetingClauses":[{...}]}；作为 body JSON 字符串发送。 |

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
| payload 实体 / data 对应实体：state | string | ENABLED / PAUSED / ARCHIVED |
| payload 实体 / data 对应实体：expression | array | 定向表达式，内容原样保留 |
| payload 实体 / data 对应实体：expressionType | string | AUTO / MANUAL |
| payload 实体 / data 对应实体：bid | number | 出价 |


## 接口：SP 创建商品广告

### 脚本输入与构参

| 转发属性 | 本操作约定 |
|---|---|
| method | POST |
| path | sp/productAds |
| contentType | application/vnd.spProductAd.v3+json |
| accept | 未显式指定 |

#### 脚本 JSON 参数与选项

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| profileId | integer/string | 是 | 从广告授权技能解析，不能要求用户报数字。 |
| region | string | 是 | NA / EU / FE。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已完成依赖检测时使用，不绕过授权。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存响应。 |
| --no-cache | CLI flag | 否 | 业务调用始终附加；响应缓存关闭。公共调用器会建立空缓存目录，但不读写响应缓存。 |
| payload | object / array | 是 | {"productAds":[{...}]}；作为 body JSON 字符串发送。 |

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
| payload 实体 / data 对应实体：asin | string | ASIN |
| payload 实体 / data 对应实体：sku | string | SKU |
| payload 实体 / data 对应实体：state | string | ENABLED / PAUSED / ARCHIVED |


## 接口：SP 创建商品定向

### 脚本输入与构参

| 转发属性 | 本操作约定 |
|---|---|
| method | POST |
| path | sp/targets |
| contentType | application/vnd.spTargetingClause.v3+json |
| accept | 未显式指定 |

#### 脚本 JSON 参数与选项

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| profileId | integer/string | 是 | 从广告授权技能解析，不能要求用户报数字。 |
| region | string | 是 | NA / EU / FE。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已完成依赖检测时使用，不绕过授权。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存响应。 |
| --no-cache | CLI flag | 否 | 业务调用始终附加；响应缓存关闭。公共调用器会建立空缓存目录，但不读写响应缓存。 |
| payload | object / array | 是 | {"targetingClauses":[{...}]}；作为 body JSON 字符串发送。 |

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
| payload 实体 / data 对应实体：state | string | ENABLED / PAUSED / ARCHIVED |
| payload 实体 / data 对应实体：expression | array | 定向表达式，内容原样保留 |
| payload 实体 / data 对应实体：expressionType | string | AUTO / MANUAL |
| payload 实体 / data 对应实体：bid | number | 出价 |


## 接口：SP 查询广告组

### 脚本输入与构参

| 转发属性 | 本操作约定 |
|---|---|
| method | POST |
| path | sp/adGroups/list |
| contentType | application/vnd.spAdGroup.v3+json |
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
| includeExtendedDataFields | boolean | 否 | 默认不发送；按原生接口支持情况透传请求体标志。 |
| locale | string | 否 | 本地化字段，keywords 支持；其他原生支持情况由上游决定。 |
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
| campaignTargetingTypeFilter | string | 否 | AUTO / MANUAL；兼容 include 对象或数组，取首项。 |

#### Amazon 查询请求体字段

下表表示 body 字符串 JSON 解码后的分页字段；筛选结构及嵌套定义见本接口的脚本参数表。

| 字段 | 类型 | 必填 | 默认值与说明 |
|---|---|---|---|
| body.maxResults | integer | 否 | 默认 100；单页 1–100，由上游校验。 |
| body.nextToken | string | 否 | 默认不传；后续请求使用上一页令牌。 |

SP 普通实体 CLI 不接收起始 nextToken；直接调用接口时可在 body 中指定。

依赖检测为本地文件检查：0 表示存在认证技能；42 且 stderr 含 `DEPENDENCY_MISSING:` 时先安装 `linkfox-amazon-ads-auth`。认证与运行限制见 [总览](../api.md)。

分页：跟随 nextToken；无后续 token 或 fetchAll=false 时结束。普通实体 CLI 使用固定 maxPages=50，不读取顶层 maxPages；达到上限时标记 truncated，不自动重试失败请求。

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
| body.nextToken | string | 后续页令牌；脚本聚合后不一定回显。 |

#### 实体字段

以下为常见实体字段；原生写操作按创建/更新要求取用，非所有字段都必填，未记录的必填规则不推定。

| 字段 | 类型 | 说明 |
|---|---|---|
| adGroups[].adGroupId | number / string | 广告组 ID |
| adGroups[].campaignId | number / string | 活动 ID |
| adGroups[].name | string | 名称 |
| adGroups[].state | string | ENABLED / PAUSED / ARCHIVED |
| adGroups[].defaultBid | number | 默认出价 |


## 接口：SP 查询预算规则

### 脚本输入与构参

| 转发属性 | 本操作约定 |
|---|---|
| method | GET |
| path | sp/budgetRules |
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


## 接口：SP 查询广告活动

### 脚本输入与构参

| 转发属性 | 本操作约定 |
|---|---|
| method | POST |
| path | sp/campaigns/list |
| contentType | application/vnd.spCampaign.v3+json |
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
| includeExtendedDataFields | boolean | 否 | 默认不发送；按原生接口支持情况透传请求体标志。 |
| locale | string | 否 | 本地化字段，keywords 支持；其他原生支持情况由上游决定。 |
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

SP 普通实体 CLI 不接收起始 nextToken；直接调用接口时可在 body 中指定。

依赖检测为本地文件检查：0 表示存在认证技能；42 且 stderr 含 `DEPENDENCY_MISSING:` 时先安装 `linkfox-amazon-ads-auth`。认证与运行限制见 [总览](../api.md)。

分页：跟随 nextToken；无后续 token 或 fetchAll=false 时结束。普通实体 CLI 使用固定 maxPages=50，不读取顶层 maxPages；达到上限时标记 truncated，不自动重试失败请求。

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
| body.nextToken | string | 后续页令牌；脚本聚合后不一定回显。 |

#### 实体字段

以下为常见实体字段；原生写操作按创建/更新要求取用，非所有字段都必填，未记录的必填规则不推定。

| 字段 | 类型 | 说明 |
|---|---|---|
| campaigns[].campaignId | number / string | 活动 ID |
| campaigns[].name | string | 名称 |
| campaigns[].state | string | ENABLED / PAUSED / ARCHIVED |
| campaigns[].targetingType | string | 定向方式 |
| campaigns[].budget | object | 预算对象 |
| campaigns[].budget.budget | number | 预算值 |
| campaigns[].budget.budgetType | string | 预算类型 |
| campaigns[].startDate | string | 开始日期 |
| campaigns[].endDate | string | 结束日期 |
| campaigns[].dynamicBidding | object | 动态竞价 |
| campaigns[].dynamicBidding.strategy | string | 动态竞价策略 |
| campaigns[].portfolioId | number / string | 组合 ID |


## 接口：SP 查询关键词

### 脚本输入与构参

| 转发属性 | 本操作约定 |
|---|---|
| method | POST |
| path | sp/keywords/list |
| contentType | application/vnd.spKeyword.v3+json |
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
| includeExtendedDataFields | boolean | 否 | 默认不发送；按原生接口支持情况透传请求体标志。 |
| locale | string | 否 | 本地化字段，keywords 支持；其他原生支持情况由上游决定。 |
| keywordIdFilter | object / array / string | 否 | {include:[...]} / {exclude:[...]}；兼容裸数组或字符串，规范化为对象。 |
| keywordIdFilter.include | array<string> | 对象形态按过滤要求 | 包含的 ID、状态、匹配类型或文本值；字段本身允许数组/单值时按上述规则规范化。 |
| keywordIdFilter.exclude | array<string> | 否 | 对象型过滤器可用的排除值；按原生接口支持范围透传，不在客户端模拟排除。 |
| adGroupIdFilter | object / array / string | 否 | {include:[...]} / {exclude:[...]}；兼容裸数组或字符串，规范化为对象。 |
| adGroupIdFilter.include | array<string> | 对象形态按过滤要求 | 包含的 ID、状态、匹配类型或文本值；字段本身允许数组/单值时按上述规则规范化。 |
| adGroupIdFilter.exclude | array<string> | 否 | 对象型过滤器可用的排除值；按原生接口支持范围透传，不在客户端模拟排除。 |
| campaignIdFilter | object / array / string | 否 | {include:[...]} / {exclude:[...]}；兼容裸数组或字符串，规范化为对象。 |
| campaignIdFilter.include | array<string> | 对象形态按过滤要求 | 包含的 ID、状态、匹配类型或文本值；字段本身允许数组/单值时按上述规则规范化。 |
| campaignIdFilter.exclude | array<string> | 否 | 对象型过滤器可用的排除值；按原生接口支持范围透传，不在客户端模拟排除。 |
| stateFilter | object / array / string | 否 | {include:[...]} / {exclude:[...]}；兼容裸数组或字符串，规范化为对象。 |
| stateFilter.include | array<string> | 对象形态按过滤要求 | 包含的 ID、状态、匹配类型或文本值；字段本身允许数组/单值时按上述规则规范化。 |
| stateFilter.exclude | array<string> | 否 | 对象型过滤器可用的排除值；按原生接口支持范围透传，不在客户端模拟排除。 |
| matchTypeFilter | array | 否 | SP 裸数组；keywords：BROAD / PHRASE / EXACT；negativeKeywords：NEGATIVE_EXACT / NEGATIVE_PHRASE；兼容 include 对象或单值。 |
| keywordTextFilter | object | 否 | {queryTermMatchType:BROAD_MATCH / EXACT_MATCH, include:[文本]}，原样透传。 |
| keywordTextFilter.include | array<string> | 对象形态按过滤要求 | 包含的 ID、状态、匹配类型或文本值；字段本身允许数组/单值时按上述规则规范化。 |
| keywordTextFilter.queryTermMatchType | string | 文本过滤按原生要求 | BROAD_MATCH / EXACT_MATCH；原样透传。 |

#### Amazon 查询请求体字段

下表表示 body 字符串 JSON 解码后的分页字段；筛选结构及嵌套定义见本接口的脚本参数表。

| 字段 | 类型 | 必填 | 默认值与说明 |
|---|---|---|---|
| body.maxResults | integer | 否 | 默认 100；单页 1–100，由上游校验。 |
| body.nextToken | string | 否 | 默认不传；后续请求使用上一页令牌。 |

SP 普通实体 CLI 不接收起始 nextToken；直接调用接口时可在 body 中指定。

依赖检测为本地文件检查：0 表示存在认证技能；42 且 stderr 含 `DEPENDENCY_MISSING:` 时先安装 `linkfox-amazon-ads-auth`。认证与运行限制见 [总览](../api.md)。

分页：跟随 nextToken；无后续 token 或 fetchAll=false 时结束。普通实体 CLI 使用固定 maxPages=50，不读取顶层 maxPages；达到上限时标记 truncated，不自动重试失败请求。

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
| body.nextToken | string | 后续页令牌；脚本聚合后不一定回显。 |

#### 实体字段

以下为常见实体字段；原生写操作按创建/更新要求取用，非所有字段都必填，未记录的必填规则不推定。

| 字段 | 类型 | 说明 |
|---|---|---|
| keywords[].keywordId | number / string | 关键词 ID |
| keywords[].adGroupId | number / string | 广告组 ID |
| keywords[].campaignId | number / string | 活动 ID |
| keywords[].keywordText | string | 关键词文本 |
| keywords[].matchType | string | BROAD / PHRASE / EXACT |
| keywords[].state | string | ENABLED / PAUSED / ARCHIVED |
| keywords[].bid | number | 出价 |


## 接口：SP 查询否定关键词

### 脚本输入与构参

| 转发属性 | 本操作约定 |
|---|---|
| method | POST |
| path | sp/negativeKeywords/list |
| contentType | application/vnd.spNegativeKeyword.v3+json |
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
| includeExtendedDataFields | boolean | 否 | 默认不发送；按原生接口支持情况透传请求体标志。 |
| locale | string | 否 | 本地化字段，keywords 支持；其他原生支持情况由上游决定。 |
| negativeKeywordIdFilter | object / array / string | 否 | {include:[...]} / {exclude:[...]}；兼容裸数组或字符串，规范化为对象。 |
| negativeKeywordIdFilter.include | array<string> | 对象形态按过滤要求 | 包含的 ID、状态、匹配类型或文本值；字段本身允许数组/单值时按上述规则规范化。 |
| negativeKeywordIdFilter.exclude | array<string> | 否 | 对象型过滤器可用的排除值；按原生接口支持范围透传，不在客户端模拟排除。 |
| adGroupIdFilter | object / array / string | 否 | {include:[...]} / {exclude:[...]}；兼容裸数组或字符串，规范化为对象。 |
| adGroupIdFilter.include | array<string> | 对象形态按过滤要求 | 包含的 ID、状态、匹配类型或文本值；字段本身允许数组/单值时按上述规则规范化。 |
| adGroupIdFilter.exclude | array<string> | 否 | 对象型过滤器可用的排除值；按原生接口支持范围透传，不在客户端模拟排除。 |
| campaignIdFilter | object / array / string | 否 | {include:[...]} / {exclude:[...]}；兼容裸数组或字符串，规范化为对象。 |
| campaignIdFilter.include | array<string> | 对象形态按过滤要求 | 包含的 ID、状态、匹配类型或文本值；字段本身允许数组/单值时按上述规则规范化。 |
| campaignIdFilter.exclude | array<string> | 否 | 对象型过滤器可用的排除值；按原生接口支持范围透传，不在客户端模拟排除。 |
| stateFilter | object / array / string | 否 | {include:[...]} / {exclude:[...]}；兼容裸数组或字符串，规范化为对象。 |
| stateFilter.include | array<string> | 对象形态按过滤要求 | 包含的 ID、状态、匹配类型或文本值；字段本身允许数组/单值时按上述规则规范化。 |
| stateFilter.exclude | array<string> | 否 | 对象型过滤器可用的排除值；按原生接口支持范围透传，不在客户端模拟排除。 |
| matchTypeFilter | array | 否 | SP 裸数组；keywords：BROAD / PHRASE / EXACT；negativeKeywords：NEGATIVE_EXACT / NEGATIVE_PHRASE；兼容 include 对象或单值。 |
| keywordTextFilter | object | 否 | {queryTermMatchType:BROAD_MATCH / EXACT_MATCH, include:[文本]}，原样透传。 |
| keywordTextFilter.include | array<string> | 对象形态按过滤要求 | 包含的 ID、状态、匹配类型或文本值；字段本身允许数组/单值时按上述规则规范化。 |
| keywordTextFilter.queryTermMatchType | string | 文本过滤按原生要求 | BROAD_MATCH / EXACT_MATCH；原样透传。 |

#### Amazon 查询请求体字段

下表表示 body 字符串 JSON 解码后的分页字段；筛选结构及嵌套定义见本接口的脚本参数表。

| 字段 | 类型 | 必填 | 默认值与说明 |
|---|---|---|---|
| body.maxResults | integer | 否 | 默认 100；单页 1–100，由上游校验。 |
| body.nextToken | string | 否 | 默认不传；后续请求使用上一页令牌。 |

SP 普通实体 CLI 不接收起始 nextToken；直接调用接口时可在 body 中指定。

依赖检测为本地文件检查：0 表示存在认证技能；42 且 stderr 含 `DEPENDENCY_MISSING:` 时先安装 `linkfox-amazon-ads-auth`。认证与运行限制见 [总览](../api.md)。

分页：跟随 nextToken；无后续 token 或 fetchAll=false 时结束。普通实体 CLI 使用固定 maxPages=50，不读取顶层 maxPages；达到上限时标记 truncated，不自动重试失败请求。

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
| negativeKeywords | array<object> | 聚合实体数组，保留返回字段。 |
| total | integer | 本次聚合、客户端过滤后的实体数，不是上游全量总数。 |
| pagesFetched | integer | 已取得页数。 |
| truncated | boolean | 达到页数限制或保留部分结果；为 true 时必须告知数据未取完。 |
| body.nextToken | string | 后续页令牌；脚本聚合后不一定回显。 |

#### 实体字段

以下为常见实体字段；原生写操作按创建/更新要求取用，非所有字段都必填，未记录的必填规则不推定。

| 字段 | 类型 | 说明 |
|---|---|---|
| negativeKeywords[].keywordId | number / string | 关键词 ID |
| negativeKeywords[].adGroupId | number / string | 广告组 ID |
| negativeKeywords[].campaignId | number / string | 活动 ID |
| negativeKeywords[].keywordText | string | 关键词文本 |
| negativeKeywords[].matchType | string | NEGATIVE_EXACT / NEGATIVE_PHRASE |
| negativeKeywords[].state | string | ENABLED / PAUSED / ARCHIVED |
| negativeKeywords[].bid | number | 出价 |


## 接口：SP 查询商品广告

### 脚本输入与构参

| 转发属性 | 本操作约定 |
|---|---|
| method | POST |
| path | sp/productAds/list |
| contentType | application/vnd.spProductAd.v3+json |
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
| includeExtendedDataFields | boolean | 否 | 默认不发送；按原生接口支持情况透传请求体标志。 |
| locale | string | 否 | 本地化字段，keywords 支持；其他原生支持情况由上游决定。 |
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
| asinFilter | object / array / string | 否 | 客户端按 asin 精确匹配；不发给上游。建议同时带 campaignIdFilter / adGroupIdFilter / adIdFilter 收窄，缺少时 stderr 提示。 |
| asinFilter.include | array<string> | 对象形态按过滤要求 | 包含的 ID、状态、匹配类型或文本值；字段本身允许数组/单值时按上述规则规范化。 |
| skuFilter | object / array / string | 否 | 客户端按 sku 精确匹配；不发给上游；与其他客户端过滤取交集。 |
| skuFilter.include | array<string> | 对象形态按过滤要求 | 包含的 ID、状态、匹配类型或文本值；字段本身允许数组/单值时按上述规则规范化。 |

#### Amazon 查询请求体字段

下表表示 body 字符串 JSON 解码后的分页字段；筛选结构及嵌套定义见本接口的脚本参数表。

| 字段 | 类型 | 必填 | 默认值与说明 |
|---|---|---|---|
| body.maxResults | integer | 否 | 默认 100；单页 1–100，由上游校验。 |
| body.nextToken | string | 否 | 默认不传；后续请求使用上一页令牌。 |

SP 普通实体 CLI 不接收起始 nextToken；直接调用接口时可在 body 中指定。

依赖检测为本地文件检查：0 表示存在认证技能；42 且 stderr 含 `DEPENDENCY_MISSING:` 时先安装 `linkfox-amazon-ads-auth`。认证与运行限制见 [总览](../api.md)。

分页：跟随 nextToken；无后续 token 或 fetchAll=false 时结束。普通实体 CLI 使用固定 maxPages=50，不读取顶层 maxPages；达到上限时标记 truncated，不自动重试失败请求。

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
| body.nextToken | string | 后续页令牌；脚本聚合后不一定回显。 |

#### 实体字段

以下为常见实体字段；原生写操作按创建/更新要求取用，非所有字段都必填，未记录的必填规则不推定。

| 字段 | 类型 | 说明 |
|---|---|---|
| productAds[].adId | number / string | 广告 ID |
| productAds[].adGroupId | number / string | 广告组 ID |
| productAds[].campaignId | number / string | 活动 ID |
| productAds[].asin | string | ASIN |
| productAds[].sku | string | SKU |
| productAds[].state | string | ENABLED / PAUSED / ARCHIVED |


## 接口：SP 查询商品定向

### 脚本输入与构参

| 转发属性 | 本操作约定 |
|---|---|
| method | POST |
| path | sp/targets/list |
| contentType | application/vnd.spTargetingClause.v3+json |
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
| includeExtendedDataFields | boolean | 否 | 默认不发送；按原生接口支持情况透传请求体标志。 |
| locale | string | 否 | 本地化字段，keywords 支持；其他原生支持情况由上游决定。 |
| targetIdFilter | object / array / string | 否 | {include:[...]} / {exclude:[...]}；兼容裸数组或字符串，规范化为对象。 |
| targetIdFilter.include | array<string> | 对象形态按过滤要求 | 包含的 ID、状态、匹配类型或文本值；字段本身允许数组/单值时按上述规则规范化。 |
| targetIdFilter.exclude | array<string> | 否 | 对象型过滤器可用的排除值；按原生接口支持范围透传，不在客户端模拟排除。 |
| adGroupIdFilter | object / array / string | 否 | {include:[...]} / {exclude:[...]}；兼容裸数组或字符串，规范化为对象。 |
| adGroupIdFilter.include | array<string> | 对象形态按过滤要求 | 包含的 ID、状态、匹配类型或文本值；字段本身允许数组/单值时按上述规则规范化。 |
| adGroupIdFilter.exclude | array<string> | 否 | 对象型过滤器可用的排除值；按原生接口支持范围透传，不在客户端模拟排除。 |
| campaignIdFilter | object / array / string | 否 | {include:[...]} / {exclude:[...]}；兼容裸数组或字符串，规范化为对象。 |
| campaignIdFilter.include | array<string> | 对象形态按过滤要求 | 包含的 ID、状态、匹配类型或文本值；字段本身允许数组/单值时按上述规则规范化。 |
| campaignIdFilter.exclude | array<string> | 否 | 对象型过滤器可用的排除值；按原生接口支持范围透传，不在客户端模拟排除。 |
| stateFilter | object / array / string | 否 | {include:[...]} / {exclude:[...]}；兼容裸数组或字符串，规范化为对象。 |
| stateFilter.include | array<string> | 对象形态按过滤要求 | 包含的 ID、状态、匹配类型或文本值；字段本身允许数组/单值时按上述规则规范化。 |
| stateFilter.exclude | array<string> | 否 | 对象型过滤器可用的排除值；按原生接口支持范围透传，不在客户端模拟排除。 |
| expressionTypeFilter | object | 否 | {include:[AUTO / MANUAL]}，不是裸数组；兼容字符串或数组后包 include。 |
| expressionTypeFilter.include | array<string> | 对象形态按过滤要求 | 包含的 ID、状态、匹配类型或文本值；字段本身允许数组/单值时按上述规则规范化。 |
| expressionTypeFilter.exclude | array<string> | 否 | 对象型过滤器可用的排除值；按原生接口支持范围透传，不在客户端模拟排除。 |

#### Amazon 查询请求体字段

下表表示 body 字符串 JSON 解码后的分页字段；筛选结构及嵌套定义见本接口的脚本参数表。

| 字段 | 类型 | 必填 | 默认值与说明 |
|---|---|---|---|
| body.maxResults | integer | 否 | 默认 100；单页 1–100，由上游校验。 |
| body.nextToken | string | 否 | 默认不传；后续请求使用上一页令牌。 |

SP 普通实体 CLI 不接收起始 nextToken；直接调用接口时可在 body 中指定。

依赖检测为本地文件检查：0 表示存在认证技能；42 且 stderr 含 `DEPENDENCY_MISSING:` 时先安装 `linkfox-amazon-ads-auth`。认证与运行限制见 [总览](../api.md)。

分页：跟随 nextToken；无后续 token 或 fetchAll=false 时结束。普通实体 CLI 使用固定 maxPages=50，不读取顶层 maxPages；达到上限时标记 truncated，不自动重试失败请求。

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
| body.nextToken | string | 后续页令牌；脚本聚合后不一定回显。 |

#### 实体字段

以下为常见实体字段；原生写操作按创建/更新要求取用，非所有字段都必填，未记录的必填规则不推定。

| 字段 | 类型 | 说明 |
|---|---|---|
| targetingClauses[].targetId | number / string | 定向 ID |
| targetingClauses[].adGroupId | number / string | 广告组 ID |
| targetingClauses[].campaignId | number / string | 活动 ID |
| targetingClauses[].state | string | ENABLED / PAUSED / ARCHIVED |
| targetingClauses[].expression | array | 定向表达式，内容原样保留 |
| targetingClauses[].expressionType | string | AUTO / MANUAL |
| targetingClauses[].bid | number | 出价 |


## 接口：SP 修改广告组

### 脚本输入与构参

| 转发属性 | 本操作约定 |
|---|---|
| method | PUT |
| path | sp/adGroups |
| contentType | application/vnd.spAdGroup.v3+json |
| accept | 未显式指定 |

#### 脚本 JSON 参数与选项

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| profileId | integer/string | 是 | 从广告授权技能解析，不能要求用户报数字。 |
| region | string | 是 | NA / EU / FE。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已完成依赖检测时使用，不绕过授权。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存响应。 |
| --no-cache | CLI flag | 否 | 业务调用始终附加；响应缓存关闭。公共调用器会建立空缓存目录，但不读写响应缓存。 |
| payload | object / array | 是 | {"adGroups":[{"adGroupId":123,...}]}；作为 body JSON 字符串发送。 |

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
| payload 实体 / data 对应实体：state | string | ENABLED / PAUSED / ARCHIVED |
| payload 实体 / data 对应实体：defaultBid | number | 默认出价 |


## 接口：SP 修改预算规则

### 脚本输入与构参

| 转发属性 | 本操作约定 |
|---|---|
| method | PUT |
| path | sp/budgetRules |
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
| payload | object / array | 是 | {"budgetRules":[{"ruleId":"...","name":"...",...}]}；作为 body JSON 字符串发送。 |
| payload.budgetRules | array<object> | 按原生操作 | 预算规则数组 |
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


## 接口：SP 修改活动级否定关键词

### 脚本输入与构参

| 转发属性 | 本操作约定 |
|---|---|
| method | PUT |
| path | sp/campaignNegativeKeywords |
| contentType | application/vnd.spCampaignNegativeKeyword.v3+json |
| accept | 未显式指定 |

#### 脚本 JSON 参数与选项

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| profileId | integer/string | 是 | 从广告授权技能解析，不能要求用户报数字。 |
| region | string | 是 | NA / EU / FE。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已完成依赖检测时使用，不绕过授权。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存响应。 |
| --no-cache | CLI flag | 否 | 业务调用始终附加；响应缓存关闭。公共调用器会建立空缓存目录，但不读写响应缓存。 |
| payload | object / array | 是 | {"campaignNegativeKeywords":[{"keywordId":123,...}]}；作为 body JSON 字符串发送。 |

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
| payload 实体 / data 对应实体：keywordId | number / string | 关键词 ID |
| payload 实体 / data 对应实体：adGroupId | number / string | 广告组 ID |
| payload 实体 / data 对应实体：campaignId | number / string | 活动 ID |
| payload 实体 / data 对应实体：keywordText | string | 关键词文本 |
| payload 实体 / data 对应实体：matchType | string | NEGATIVE_EXACT / NEGATIVE_PHRASE |
| payload 实体 / data 对应实体：state | string | ENABLED / PAUSED / ARCHIVED |
| payload 实体 / data 对应实体：bid | number | 出价 |


## 接口：SP 修改活动级否定定向

### 脚本输入与构参

| 转发属性 | 本操作约定 |
|---|---|
| method | PUT |
| path | sp/campaignNegativeTargets |
| contentType | application/vnd.spCampaignNegativeTargetingClause.v3+json |
| accept | 未显式指定 |

#### 脚本 JSON 参数与选项

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| profileId | integer/string | 是 | 从广告授权技能解析，不能要求用户报数字。 |
| region | string | 是 | NA / EU / FE。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已完成依赖检测时使用，不绕过授权。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存响应。 |
| --no-cache | CLI flag | 否 | 业务调用始终附加；响应缓存关闭。公共调用器会建立空缓存目录，但不读写响应缓存。 |
| payload | object / array | 是 | {"campaignNegativeTargetingClauses":[{"targetId":123,...}]}；作为 body JSON 字符串发送。 |

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
| payload 实体 / data 对应实体：state | string | ENABLED / PAUSED / ARCHIVED |
| payload 实体 / data 对应实体：expression | array | 定向表达式，内容原样保留 |
| payload 实体 / data 对应实体：expressionType | string | AUTO / MANUAL |
| payload 实体 / data 对应实体：bid | number | 出价 |


## 接口：SP 修改广告活动

### 脚本输入与构参

| 转发属性 | 本操作约定 |
|---|---|
| method | PUT |
| path | sp/campaigns |
| contentType | application/vnd.spCampaign.v3+json |
| accept | 未显式指定 |

#### 脚本 JSON 参数与选项

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| profileId | integer/string | 是 | 从广告授权技能解析，不能要求用户报数字。 |
| region | string | 是 | NA / EU / FE。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已完成依赖检测时使用，不绕过授权。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存响应。 |
| --no-cache | CLI flag | 否 | 业务调用始终附加；响应缓存关闭。公共调用器会建立空缓存目录，但不读写响应缓存。 |
| payload | object / array | 是 | {"campaigns":[{"campaignId":123,...}]}；作为 body JSON 字符串发送。 |

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
| payload 实体 / data 对应实体：state | string | ENABLED / PAUSED / ARCHIVED |
| payload 实体 / data 对应实体：targetingType | string | 定向方式 |
| payload 实体 / data 对应实体：budget | object | 预算对象 |
| payload 实体 / data 对应实体：budget.budget | number | 预算值 |
| payload 实体 / data 对应实体：budget.budgetType | string | 预算类型 |
| payload 实体 / data 对应实体：startDate | string | 开始日期 |
| payload 实体 / data 对应实体：endDate | string | 结束日期 |
| payload 实体 / data 对应实体：dynamicBidding | object | 动态竞价 |
| payload 实体 / data 对应实体：dynamicBidding.strategy | string | 动态竞价策略 |
| payload 实体 / data 对应实体：portfolioId | number / string | 组合 ID |


## 接口：SP 修改关键词

### 脚本输入与构参

| 转发属性 | 本操作约定 |
|---|---|
| method | PUT |
| path | sp/keywords |
| contentType | application/vnd.spKeyword.v3+json |
| accept | 未显式指定 |

#### 脚本 JSON 参数与选项

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| profileId | integer/string | 是 | 从广告授权技能解析，不能要求用户报数字。 |
| region | string | 是 | NA / EU / FE。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已完成依赖检测时使用，不绕过授权。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存响应。 |
| --no-cache | CLI flag | 否 | 业务调用始终附加；响应缓存关闭。公共调用器会建立空缓存目录，但不读写响应缓存。 |
| payload | object / array | 是 | {"keywords":[{"keywordId":123,"bid":1.5}]}；作为 body JSON 字符串发送。 |

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
| payload 实体 / data 对应实体：keywordId | number / string | 关键词 ID |
| payload 实体 / data 对应实体：adGroupId | number / string | 广告组 ID |
| payload 实体 / data 对应实体：campaignId | number / string | 活动 ID |
| payload 实体 / data 对应实体：keywordText | string | 关键词文本 |
| payload 实体 / data 对应实体：matchType | string | BROAD / PHRASE / EXACT |
| payload 实体 / data 对应实体：state | string | ENABLED / PAUSED / ARCHIVED |
| payload 实体 / data 对应实体：bid | number | 出价 |


## 接口：SP 修改否定关键词

### 脚本输入与构参

| 转发属性 | 本操作约定 |
|---|---|
| method | PUT |
| path | sp/negativeKeywords |
| contentType | application/vnd.spNegativeKeyword.v3+json |
| accept | 未显式指定 |

#### 脚本 JSON 参数与选项

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| profileId | integer/string | 是 | 从广告授权技能解析，不能要求用户报数字。 |
| region | string | 是 | NA / EU / FE。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已完成依赖检测时使用，不绕过授权。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存响应。 |
| --no-cache | CLI flag | 否 | 业务调用始终附加；响应缓存关闭。公共调用器会建立空缓存目录，但不读写响应缓存。 |
| payload | object / array | 是 | {"negativeKeywords":[{"keywordId":123,...}]}；作为 body JSON 字符串发送。 |

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
| payload 实体 / data 对应实体：keywordId | number / string | 关键词 ID |
| payload 实体 / data 对应实体：adGroupId | number / string | 广告组 ID |
| payload 实体 / data 对应实体：campaignId | number / string | 活动 ID |
| payload 实体 / data 对应实体：keywordText | string | 关键词文本 |
| payload 实体 / data 对应实体：matchType | string | NEGATIVE_EXACT / NEGATIVE_PHRASE |
| payload 实体 / data 对应实体：state | string | ENABLED / PAUSED / ARCHIVED |
| payload 实体 / data 对应实体：bid | number | 出价 |


## 接口：SP 修改否定定向

### 脚本输入与构参

| 转发属性 | 本操作约定 |
|---|---|
| method | PUT |
| path | sp/negativeTargets |
| contentType | application/vnd.spNegativeTargetingClause.v3+json |
| accept | 未显式指定 |

#### 脚本 JSON 参数与选项

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| profileId | integer/string | 是 | 从广告授权技能解析，不能要求用户报数字。 |
| region | string | 是 | NA / EU / FE。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已完成依赖检测时使用，不绕过授权。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存响应。 |
| --no-cache | CLI flag | 否 | 业务调用始终附加；响应缓存关闭。公共调用器会建立空缓存目录，但不读写响应缓存。 |
| payload | object / array | 是 | {"negativeTargetingClauses":[{"targetId":123,...}]}；作为 body JSON 字符串发送。 |

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
| payload 实体 / data 对应实体：state | string | ENABLED / PAUSED / ARCHIVED |
| payload 实体 / data 对应实体：expression | array | 定向表达式，内容原样保留 |
| payload 实体 / data 对应实体：expressionType | string | AUTO / MANUAL |
| payload 实体 / data 对应实体：bid | number | 出价 |


## 接口：SP 修改商品广告

### 脚本输入与构参

| 转发属性 | 本操作约定 |
|---|---|
| method | PUT |
| path | sp/productAds |
| contentType | application/vnd.spProductAd.v3+json |
| accept | 未显式指定 |

#### 脚本 JSON 参数与选项

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| profileId | integer/string | 是 | 从广告授权技能解析，不能要求用户报数字。 |
| region | string | 是 | NA / EU / FE。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已完成依赖检测时使用，不绕过授权。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存响应。 |
| --no-cache | CLI flag | 否 | 业务调用始终附加；响应缓存关闭。公共调用器会建立空缓存目录，但不读写响应缓存。 |
| payload | object / array | 是 | {"productAds":[{"adId":123,...}]}；作为 body JSON 字符串发送。 |

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
| payload 实体 / data 对应实体：asin | string | ASIN |
| payload 实体 / data 对应实体：sku | string | SKU |
| payload 实体 / data 对应实体：state | string | ENABLED / PAUSED / ARCHIVED |


## 接口：SP 修改商品定向

### 脚本输入与构参

| 转发属性 | 本操作约定 |
|---|---|
| method | PUT |
| path | sp/targets |
| contentType | application/vnd.spTargetingClause.v3+json |
| accept | 未显式指定 |

#### 脚本 JSON 参数与选项

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| profileId | integer/string | 是 | 从广告授权技能解析，不能要求用户报数字。 |
| region | string | 是 | NA / EU / FE。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已完成依赖检测时使用，不绕过授权。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存响应。 |
| --no-cache | CLI flag | 否 | 业务调用始终附加；响应缓存关闭。公共调用器会建立空缓存目录，但不读写响应缓存。 |
| payload | object / array | 是 | {"targetingClauses":[{"targetId":123,"bid":0.8}]}；作为 body JSON 字符串发送。 |

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
| payload 实体 / data 对应实体：state | string | ENABLED / PAUSED / ARCHIVED |
| payload 实体 / data 对应实体：expression | array | 定向表达式，内容原样保留 |
| payload 实体 / data 对应实体：expressionType | string | AUTO / MANUAL |
| payload 实体 / data 对应实体：bid | number | 出价 |
