# 脚本输入、构参与本地结果

profileId 接收 Long 范围内的正整数或十进制数字字符串，发送到网关时为 integer；不接受布尔值、小数、零、负数或越界值。

网关接口定义见 [api.md](api.md)。以下表格描述脚本参数、构参或本地解析行为；不作为网关DTO或上游完整schema。

## 接口：创建广告报告

### 脚本输入与构参

| 项目 | 值 |
|---|---|
| 网关方法 | POST |
| 上游方法 | POST |
| path | `reporting/reports` |


#### 脚本 JSON 参数（全链路模式）

| 字段 | 类型 | 必填 | 默认值 / 说明 |
|---|---|---|---|
| profileId | integer/string | 是 | 从 Ads 认证技能取得。 |
| region | string | 是 | `NA` / `EU` / `FE`。 |
| reportTypeId | string | 是 | [完整类型目录](report-types/index.md)，覆盖 SP / SB / SD。 |
| adProduct | string | 是 | `SPONSORED_PRODUCTS` / `SPONSORED_BRANDS` / `SPONSORED_DISPLAY`，取对应 frontmatter。 |
| groupBy | array[string] | 是 | 从类型文档的配置选取；非空且须与该类型相容。 |
| columns | array[string] | 是 | 基础指标与适用分组附加指标中的子集，显式传入，不能推导不存在的字段。 |
| startDate | string | 是 | `YYYY-MM-DD`，含当天。 |
| endDate | string | 是 | `YYYY-MM-DD`，含当天。 |
| name | string | 否 | 默认 `{reportTypeId}_{startDate}_{endDate}`。 |
| timeUnit | string | 否 | 脚本默认 `SUMMARY`；可选 `DAILY` / `SUMMARY`。Agent 默认选择规则见 [运行规则](report-runtime.md#默认构参规则)。 |
| format | string | 否 | 默认 `GZIP_JSON`；部分报告支持 `CSV` / `XLSX`，以对应类型文档为准。 |
| filters | array[object] | 否 | 默认不加；各类型规定可筛选字段、值与适用分组。 |
| filters[].field | string | 使用筛选时是 | 上游筛选字段，对应类型 frontmatter 的 `filters[].name`。 |
| filters[].values | array[string] | 使用筛选时是 | 对应类型定义的枚举值。 |

#### 上游创建请求 body 解码后的结构

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| name | string | 是（脚本生成） | 报告显示名称。 |
| startDate | string | 是 | 起始日期。 |
| endDate | string | 是 | 结束日期。 |
| configuration | object | 是 | 报告配置。 |
| configuration.adProduct | string | 是 | 脚本 adProduct。 |
| configuration.groupBy | array[string] | 是 | 脚本 groupBy。 |
| configuration.columns | array[string] | 是 | 脚本 columns。 |
| configuration.reportTypeId | string | 是 | 脚本 reportTypeId。 |
| configuration.timeUnit | string | 是 | 脚本 timeUnit。 |
| configuration.format | string | 是 | 脚本 format。 |
| configuration.filters | array[object] | 否 | 脚本 filters 原样传入；元素含 field、values，定义见上表。 |

#### 脚本流程参数与 CLI

| 参数 / 选项 | 类型 | 必填 | 默认值 / 说明 |
|---|---|---|---|
| reportId | string | 否 | 非空时跳过创建，进入仅轮询模式，只需 profileId、region、reportId。 |
| pollInterval | number | 否 | 30，秒。 |
| maxAttempts | integer | 否 | 15，最多查询次数，默认等待窗口约 7.5 分钟。 |
| skipDepCheck | boolean | 否 | false；只跳过本地依赖安装检测。 |
| serveExtractedFileHttp | boolean | 否 | true；启用本机已解压文件 HTTP 服务。 |
| serveHost | string | 否 | `127.0.0.1`，默认仅本机可访问。 |
| servePort | integer | 否 | 0，系统分配端口。 |
| serveSeconds | integer | 否 | 300；开启服务时最少 10 秒。 |
| includeAmazonSourceUrl | boolean | 否 | false；是否返回 Amazon 预签名源 URL。 |
| --inline | CLI flag | 否 | 强制完整打印，同时保存响应。 |
| --no-cache | CLI flag | 否 | 兼容公共 CLI；业务封装始终传入，报告请求不启用响应缓存。 |

依赖检测、认证、URL 编码、会话落盘、下载与临时服务行为见 [运行规则](report-runtime.md#脚本运行与恢复)。

### 脚本输出与解析

#### 脚本读取的业务结果

| 字段 | 类型 | 说明 |
|---|---|---|
| reportId | string | 新任务 ID；缺失时脚本报错。 |
| code | string | 上游错误码，如重复报告时 `425`。 |
| detail | string | 上游错误详情，重复时含旧任务 UUID。 |

#### 脚本最终结果

| 字段 | 类型 | 说明 |
|---|---|---|
| success | boolean | 完成下载为 true；失败或未完成为 false。 |
| reportId | string | 新建、去重复用或恢复的任务 ID。 |
| reportTypeId | string / null | 调用方给定的报告类型；仅轮询模式可空。 |
| profileId | integer | 本次广告账号。 |
| downloadPath | string | 下载并按需解压后的绝对路径。 |
| fileName | string | 最终文件名。 |
| localFileUri | string | 本地文件 URI。 |
| tempDirectory | string | 下载工作目录，位于当前会话数据内。 |
| fileSize | integer | 文件字节数。 |
| extractedFileHttpUrl | string | 本机服务启动成功时返回的 `/download` 链接。 |
| extractedFileHttpServeSeconds | integer | 实际保持服务秒数。 |
| extractedFileHttpNote | string | 链接访问范围和时效说明。 |
| amazonDownloadUrl | string | 仅 includeAmazonSourceUrl=true 时返回；通常为压缩包源地址。 |
| amazonDownloadUrlNote | string | 源地址与解压链接的区别说明。 |
| status | string | 失败状态或 `STILL_PROCESSING`；上游完成状态为 `COMPLETED`（兼容 `SUCCESS`），脚本最终成功结果使用 success=true，不保证包含 status。 |
| error | string | 失败原因。 |
| failureReason | string / null | 上游报告生成失败原因。 |
| pollAttempts | integer | 失败或等待窗口耗尽时的轮询次数；脚本最终成功结果不保证包含此字段。 |
| elapsedSeconds | integer | 等待窗口耗尽时的估算等待秒数；脚本最终成功结果不保证包含此字段。 |
| lastStatus | string / null | 等待窗口耗尽时的最后上游状态。 |
| message | string | 等待耗尽的中文说明。 |
| resumeHint | object | 仅未完成时提供的恢复信息。 |
| resumeHint.mode | string | 固定 `poll-only`。 |
| resumeHint.note | string | 使用同一任务继续等待的说明。 |
| resumeHint.params | object | 可直接作为下次 CLI JSON 参数。 |
| resumeHint.params.profileId | number | 原广告账号。 |
| resumeHint.params.region | string | 原区域。 |
| resumeHint.params.reportId | string | 原任务 ID。 |
| resumeHint.params.maxAttempts | integer | 提示续跑默认 60，可由用户选择 120。 |
| resumeHint.params.pollInterval | integer | 原轮询间隔。 |

#### 业务适配错误字段

| 字段 | 类型 | 说明 |
|---|---|---|
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败为 null。 |
| error | string | 网关未正常响应或连接失败时的错误标记，不覆盖原消息。 |
| details | string / object / array / number / boolean / null | 非 JSON HTTP 错误的原始正文或异常响应内容（如存在），不截断。 |

网关错误保留完整原始响应；异常的非对象 JSON 响应保存在 details，不按成功处理。上游 body 解码后也必须是 JSON 对象，否则停止并报错。具体错误见本接口业务规则。


## 接口：查询广告报告

### 脚本输入与构参

| 项目 | 值 |
|---|---|
| 网关方法 | POST |
| 上游方法 | GET |
| path | `reporting/reports/{reportId}` |


#### 脚本 JSON 参数（仅轮询模式）

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| profileId | integer/string | 是 | 已授权广告账号。 |
| region | string | 是 | `NA` / `EU` / `FE`。 |
| reportId | string | 是 | 路径中的任务 ID，脚本按路径分段 URL 编码。 |
| reportTypeId | string | 否 | 用于最终输出展示，可省。 |
| startDate | string | 否 | 仅可选上下文，不重新创建或修改原报告。 |
| endDate | string | 否 | 仅可选上下文，不重新创建或修改原报告。 |

创建所需的 adProduct、groupBy、columns 无需在仅轮询模式传入；其他可选流程参数如下。

#### 脚本流程参数与 CLI

| 参数 / 选项 | 类型 | 必填 | 默认值 / 说明 |
|---|---|---|---|
| pollInterval | number | 否 | 30，秒。 |
| maxAttempts | integer | 否 | 15，最多查询次数，默认等待窗口约 7.5 分钟。 |
| skipDepCheck | boolean | 否 | false；只跳过本地依赖安装检测。 |
| serveExtractedFileHttp | boolean | 否 | true；启用本机已解压文件 HTTP 服务。 |
| serveHost | string | 否 | `127.0.0.1`，默认仅本机可访问。 |
| servePort | integer | 否 | 0，系统分配端口。 |
| serveSeconds | integer | 否 | 300；开启服务时最少 10 秒。 |
| includeAmazonSourceUrl | boolean | 否 | false；是否返回 Amazon 预签名源 URL。 |
| --inline | CLI flag | 否 | 强制完整打印，同时保存响应。 |
| --no-cache | CLI flag | 否 | 兼容公共 CLI；业务封装始终传入，报告请求不启用响应缓存。 |

依赖检测、认证、URL 编码、会话落盘、下载与临时服务行为见 [运行规则](report-runtime.md#脚本运行与恢复)。

### 脚本输出与解析

#### 脚本读取的业务结果

| 字段 | 类型 | 说明 |
|---|---|---|
| reportId | string | 报告任务标识（如上游返回）。 |
| status | string | `PENDING` / `PROCESSING` / `COMPLETED` / `FAILED`；脚本兼容状态见运行规则。 |
| url | string | 完成时的 Amazon 预签名源地址；缺失即报错。 |
| failureReason | string / null | 生成失败原因，原样透传。 |
| code | string | 上游业务错误码，如存在。 |
| detail | string | 上游业务错误详情，如存在。 |

#### 脚本最终结果

| 字段 | 类型 | 说明 |
|---|---|---|
| success | boolean | 完成下载为 true；失败或未完成为 false。 |
| reportId | string | 新建、去重复用或恢复的任务 ID。 |
| reportTypeId | string / null | 调用方给定的报告类型；仅轮询模式可空。 |
| profileId | integer | 本次广告账号。 |
| downloadPath | string | 下载并按需解压后的绝对路径。 |
| fileName | string | 最终文件名。 |
| localFileUri | string | 本地文件 URI。 |
| tempDirectory | string | 下载工作目录，位于当前会话数据内。 |
| fileSize | integer | 文件字节数。 |
| extractedFileHttpUrl | string | 本机服务启动成功时返回的 `/download` 链接。 |
| extractedFileHttpServeSeconds | integer | 实际保持服务秒数。 |
| extractedFileHttpNote | string | 链接访问范围和时效说明。 |
| amazonDownloadUrl | string | 仅 includeAmazonSourceUrl=true 时返回；通常为压缩包源地址。 |
| amazonDownloadUrlNote | string | 源地址与解压链接的区别说明。 |
| status | string | 失败状态或 `STILL_PROCESSING`；上游完成状态为 `COMPLETED`（兼容 `SUCCESS`），脚本最终成功结果使用 success=true，不保证包含 status。 |
| error | string | 失败原因。 |
| failureReason | string / null | 上游报告生成失败原因。 |
| pollAttempts | integer | 失败或等待窗口耗尽时的轮询次数；脚本最终成功结果不保证包含此字段。 |
| elapsedSeconds | integer | 等待窗口耗尽时的估算等待秒数；脚本最终成功结果不保证包含此字段。 |
| lastStatus | string / null | 等待窗口耗尽时的最后上游状态。 |
| message | string | 等待耗尽的中文说明。 |
| resumeHint | object | 仅未完成时提供的恢复信息。 |
| resumeHint.mode | string | 固定 `poll-only`。 |
| resumeHint.note | string | 使用同一任务继续等待的说明。 |
| resumeHint.params | object | 可直接作为下次 CLI JSON 参数。 |
| resumeHint.params.profileId | number | 原广告账号。 |
| resumeHint.params.region | string | 原区域。 |
| resumeHint.params.reportId | string | 原任务 ID。 |
| resumeHint.params.maxAttempts | integer | 提示续跑默认 60，可由用户选择 120。 |
| resumeHint.params.pollInterval | integer | 原轮询间隔。 |

#### 业务适配错误字段

| 字段 | 类型 | 说明 |
|---|---|---|
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败为 null。 |
| error | string | 网关未正常响应或连接失败时的错误标记，不覆盖原消息。 |
| details | string / object / array / number / boolean / null | 非 JSON HTTP 错误的原始正文或异常响应内容（如存在），不截断。 |

网关错误保留完整原始响应；异常的非对象 JSON 响应保存在 details，不按成功处理。上游 body 解码后也必须是 JSON 对象，否则停止并报错。具体错误见本接口业务规则。
