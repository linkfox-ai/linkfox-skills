# 脚本输入、构参与本地结果

profileId 接收 Long 范围内的正整数或十进制数字字符串，发送到网关时为 integer；不接受布尔值、小数、零、负数或越界值。

网关接口定义见 [sb-v3.md](sb-v3.md)。以下表格描述脚本参数、构参或本地解析行为；不作为网关DTO或上游完整schema。

## 接口：SB V3 Legacy 创建广告活动

### 脚本输入与构参

| 转发属性 | 本操作约定 |
|---|---|
| method | POST |
| path | sb/campaigns |
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
| payload | object / array | 是 | 原生 JSON，V3 Campaign 的 creative 内嵌其中；作为 body JSON 字符串发送。 |
| payload 中的 creative | object | 按原生活动要求 | Legacy 品牌名、标题、ASIN 和素材内嵌；没有独立 V3 Creative CRUD；其他子字段按 Amazon 原生 Campaign 请求要求传入。 |

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


## 接口：SB V3 Legacy 查询广告组

### 脚本输入与构参

| 转发属性 | 本操作约定 |
|---|---|
| method | GET |
| path | sb/adGroups |
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
| campaignStructure | string | 否 | V3 本地保护：MULTI_AD_GROUP 拒绝；LEGACY 用于声明已确认的历史结构。 |
| isMultiAdGroupsEnabled | boolean / string / number | 否 | V3 中 true、1、true/yes/y/on 字符串均拒绝；递归检查 payload；保护标志本身不作为查询参数。 |
| fetchAll | boolean / string / number | 否 | 默认 true；false 只取一页。兼容布尔、0/1、true/false/yes/no/y/n/on/off 字符串，非法值报 SB_INVALID_BOOLEAN。 |
| maxPages | integer | 否 | 默认 50；达到上限停止并标记 truncated。 |
| maxResults | integer | 否 | 默认 100，单页 1–100；偏移分页对应 count 并钳制到 1–100；POST list 原样发给上游，由上游校验。 |
| adGroupIdFilter | string / array / object | 否 | 接受字符串、数组或 {include:[...]}；ID 拼为逗号串，状态/匹配类型转小写，name/keywordText/locale 取首项。 |
| adGroupIdFilter.include | array<string> | 对象形态按过滤要求 | 包含的 ID、状态、匹配类型或文本值；字段本身允许数组/单值时按上述规则规范化。 |
| campaignIdFilter | string / array / object | 否 | 接受字符串、数组或 {include:[...]}；ID 拼为逗号串，状态/匹配类型转小写，name/keywordText/locale 取首项。 |
| campaignIdFilter.include | array<string> | 对象形态按过滤要求 | 包含的 ID、状态、匹配类型或文本值；字段本身允许数组/单值时按上述规则规范化。 |
| stateFilter | string / array / object | 否 | 接受字符串、数组或 {include:[...]}；ID 拼为逗号串，状态/匹配类型转小写，name/keywordText/locale 取首项。 |
| stateFilter.include | array<string> | 对象形态按过滤要求 | 包含的 ID、状态、匹配类型或文本值；字段本身允许数组/单值时按上述规则规范化。 |
| nameFilter | string / array / object | 否 | 接受字符串、数组或 {include:[...]}；ID 拼为逗号串，状态/匹配类型转小写，name/keywordText/locale 取首项。 |
| nameFilter.include | array<string> | 对象形态按过滤要求 | 包含的 ID、状态、匹配类型或文本值；字段本身允许数组/单值时按上述规则规范化。 |
| creativeType | string / array / object | 否 | SB GET 创意类型；转小写逗号串。 |
| creativeType.include | array<string> | 对象形态按过滤要求 | 包含的 ID、状态、匹配类型或文本值；字段本身允许数组/单值时按上述规则规范化。 |

#### Amazon 查询串字段

| 字段 | 类型 | 必填 | 默认值与说明 |
|---|---|---|---|
| queryString.startIndex | integer | 否 | 默认 0；业务 CLI 从 0 开始，逐页增加 count，不接收顶层 startIndex。 |
| queryString.count | integer | 否 | 默认 100；CLI 由 maxResults 决定，钳制到 1–100。 |
| queryString.adGroupIdFilter | string | 否 | 对应 adGroupIdFilter；多个值以逗号连接后 URL 编码。 |
| queryString.campaignIdFilter | string | 否 | 对应 campaignIdFilter；多个值以逗号连接后 URL 编码。 |
| queryString.stateFilter | string | 否 | 对应 stateFilter；多个值以逗号连接，整体 URL 编码；状态转小写。 |
| queryString.name | string | 否 | 对应 nameFilter；仅取首项作精确匹配，特殊字符必须 URL 编码。 |
| queryString.creativeType | string | 否 | 对应 creativeType；多个值以逗号连接后 URL 编码。 |

依赖检测为本地文件检查：0 表示存在认证技能；42 且 stderr 含 `DEPENDENCY_MISSING:` 时先安装 `linkfox-amazon-ads-auth`。认证与运行限制见 [总览](../api.md)。

SB 版本边界见 [共存规则](sb-coexistence.md)；V3 只兼容 Legacy，已知多广告组活动拒绝；不自动回落其他版本。

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
| adGroups | array<object> | 聚合实体数组，保留返回字段。 |
| total | integer | 本次聚合、客户端过滤后的实体数，不是上游全量总数。 |
| pagesFetched | integer | 已取得页数。 |
| truncated | boolean | 达到页数限制或保留部分结果；为 true 时必须告知数据未取完。 |
| apiVersion | string | V3 / V4，表示 CLI 入口/结构意图。 |
| amazonResourceVersion | string | V3 / V4 / V3_SHARED_TARGETING / SHARED_TARGETING / SHARED；与 apiVersion 不同不是回落。 |


## 接口：SB V3 Legacy 查询广告活动

### 脚本输入与构参

| 转发属性 | 本操作约定 |
|---|---|
| method | GET |
| path | sb/campaigns |
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
| campaignStructure | string | 否 | V3 本地保护：MULTI_AD_GROUP 拒绝；LEGACY 用于声明已确认的历史结构。 |
| isMultiAdGroupsEnabled | boolean / string / number | 否 | V3 中 true、1、true/yes/y/on 字符串均拒绝；递归检查 payload；保护标志本身不作为查询参数。 |
| fetchAll | boolean / string / number | 否 | 默认 true；false 只取一页。兼容布尔、0/1、true/false/yes/no/y/n/on/off 字符串，非法值报 SB_INVALID_BOOLEAN。 |
| maxPages | integer | 否 | 默认 50；达到上限停止并标记 truncated。 |
| maxResults | integer | 否 | 默认 100，单页 1–100；偏移分页对应 count 并钳制到 1–100；POST list 原样发给上游，由上游校验。 |
| campaignIdFilter | string / array / object | 否 | 接受字符串、数组或 {include:[...]}；ID 拼为逗号串，状态/匹配类型转小写，name/keywordText/locale 取首项。 |
| campaignIdFilter.include | array<string> | 对象形态按过滤要求 | 包含的 ID、状态、匹配类型或文本值；字段本身允许数组/单值时按上述规则规范化。 |
| stateFilter | string / array / object | 否 | 接受字符串、数组或 {include:[...]}；ID 拼为逗号串，状态/匹配类型转小写，name/keywordText/locale 取首项。 |
| stateFilter.include | array<string> | 对象形态按过滤要求 | 包含的 ID、状态、匹配类型或文本值；字段本身允许数组/单值时按上述规则规范化。 |
| nameFilter | string / array / object | 否 | 接受字符串、数组或 {include:[...]}；ID 拼为逗号串，状态/匹配类型转小写，name/keywordText/locale 取首项。 |
| nameFilter.include | array<string> | 对象形态按过滤要求 | 包含的 ID、状态、匹配类型或文本值；字段本身允许数组/单值时按上述规则规范化。 |
| portfolioIdFilter | string / array / object | 否 | 接受字符串、数组或 {include:[...]}；ID 拼为逗号串，状态/匹配类型转小写，name/keywordText/locale 取首项。 |
| portfolioIdFilter.include | array<string> | 对象形态按过滤要求 | 包含的 ID、状态、匹配类型或文本值；字段本身允许数组/单值时按上述规则规范化。 |
| creativeType | string / array / object | 否 | SB GET 创意类型；转小写逗号串。 |
| creativeType.include | array<string> | 对象形态按过滤要求 | 包含的 ID、状态、匹配类型或文本值；字段本身允许数组/单值时按上述规则规范化。 |

#### Amazon 查询串字段

| 字段 | 类型 | 必填 | 默认值与说明 |
|---|---|---|---|
| queryString.startIndex | integer | 否 | 默认 0；业务 CLI 从 0 开始，逐页增加 count，不接收顶层 startIndex。 |
| queryString.count | integer | 否 | 默认 100；CLI 由 maxResults 决定，钳制到 1–100。 |
| queryString.campaignIdFilter | string | 否 | 对应 campaignIdFilter；多个值以逗号连接后 URL 编码。 |
| queryString.stateFilter | string | 否 | 对应 stateFilter；多个值以逗号连接，整体 URL 编码；状态转小写。 |
| queryString.name | string | 否 | 对应 nameFilter；仅取首项作精确匹配，特殊字符必须 URL 编码。 |
| queryString.portfolioIdFilter | string | 否 | 对应 portfolioIdFilter；多个值以逗号连接后 URL 编码。 |
| queryString.creativeType | string | 否 | 对应 creativeType；多个值以逗号连接后 URL 编码。 |

依赖检测为本地文件检查：0 表示存在认证技能；42 且 stderr 含 `DEPENDENCY_MISSING:` 时先安装 `linkfox-amazon-ads-auth`。认证与运行限制见 [总览](../api.md)。

SB 版本边界见 [共存规则](sb-coexistence.md)；V3 只兼容 Legacy，已知多广告组活动拒绝；不自动回落其他版本。

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
| campaigns | array<object> | 聚合实体数组，保留返回字段。 |
| total | integer | 本次聚合、客户端过滤后的实体数，不是上游全量总数。 |
| pagesFetched | integer | 已取得页数。 |
| truncated | boolean | 达到页数限制或保留部分结果；为 true 时必须告知数据未取完。 |
| apiVersion | string | V3 / V4，表示 CLI 入口/结构意图。 |
| amazonResourceVersion | string | V3 / V4 / V3_SHARED_TARGETING / SHARED_TARGETING / SHARED；与 apiVersion 不同不是回落。 |


## 接口：SB V3 Legacy 修改广告活动

### 脚本输入与构参

| 转发属性 | 本操作约定 |
|---|---|
| method | PUT |
| path | sb/campaigns |
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
| payload | object / array | 是 | 原生 JSON，V3 Campaign 的 creative 内嵌其中；作为 body JSON 字符串发送。 |
| payload 中的 creative | object | 按原生活动要求 | Legacy 品牌名、标题、ASIN 和素材内嵌；没有独立 V3 Creative CRUD；其他子字段按 Amazon 原生 Campaign 请求要求传入。 |

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
