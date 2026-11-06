# 脚本输入、构参与本地结果

profileId 接收 Long 范围内的正整数或十进制数字字符串，发送到网关时为 integer；不接受布尔值、小数、零、负数或越界值。

网关接口定义见 [api.md](api.md)。以下表格描述脚本参数、构参或本地解析行为；不作为网关DTO或上游完整schema。

## 接口：查询 advertiser accounts

### 脚本输入与构参

上游 path 固定为 `adsApi/v1/query/advertiserAccounts`。Ads v1 不发送 `Amazon-Advertising-API-Scope`；只传 profile，由后端选择并刷新 Token，禁止调用方传 Amazon 凭证或自定义认证请求头。额外透传环境变量 `SESSION_ID` / `MESSAGE_ID` / `MODE_ID` / `APP_NAME`。网关及报告分片下载超时均为 150 秒。

#### 上游 body（JSON 字符串内）

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| isGlobalAccountFilter | object | 否 | 首轮 `{}` 查询 global accounts，第二轮查询 non-global。 |
| isGlobalAccountFilter.include | array<boolean> | 第二轮是 | 第二轮固定 `[false]`。 |
| nextToken | string | 分页时 | 沿响应 token 翻页；空页有 token 仍继续，重复 token 停止防死循环。 |

### 脚本输出与解析

#### 本地解析规则

| 字段 | 类型 | 说明 |
|---|---|---|
| 账户列表容器 | object/array | 账号可位于嵌套对象或数组中；递归收集具有账号 ID 和 alternate 列表的对象。 |
| 账户.advertiserAccountId / id | string/number | 账号 ID；优先 advertiserAccountId。 |
| 账户.alternateIds / alternateIdentifiers | array | profile 对应的别名列表；优先 alternateIds。 |
| 账户.alternateIds[] | object/string/number | 兼容对象或标量；对象中 value、id、alternateId、profileId 任一转字符串匹配当前 profile。 |
| 账户.alternateIds[].value / id / alternateId / profileId | string/number | 可匹配的别名值；alternateIdentifiers 的条目使用相同约定。 |
| nextToken / nextPageToken | string | 下一页 token，兼容两种名称。 |
| pagination | object | 可选嵌套分页对象。 |
| pagination.nextToken / pagination.nextPageToken | string | 顶层无 token 时使用的分页兼容字段。 |


## 接口：创建洞察报告

### 脚本输入与构参

上游 path 固定为 `adsApi/v1/create/reports`。Ads v1 不发送 `Amazon-Advertising-API-Scope`；只传 profile，由后端选择并刷新 Token，禁止调用方传 Amazon 凭证或自定义认证请求头。额外透传环境变量 `SESSION_ID` / `MESSAGE_ID` / `MODE_ID` / `APP_NAME`。网关及报告分片下载超时均为 150 秒。

#### 上游 body（JSON 字符串内）

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| accessRequestedAccounts | array<object> | 是 | 脚本只构造一个报告目标账号。 |
| accessRequestedAccounts[].advertiserAccountId | string | 是 | 由账号映射返回，或显式恢复参数提供。 |
| reports | array<object> | 是 | 脚本每次只创建一份报告。 |
| reports[].format | string | 是 | 固定 `CSV`。 |
| reports[].periods | array<object> | 是 | 本次报告日期区间。 |
| reports[].periods[].datePeriod | object | 是 | 包含 startDate、endDate。 |
| reports[].periods[].datePeriod.startDate | string | 是 | `YYYY-MM-DD`，不晚于 endDate。 |
| reports[].periods[].datePeriod.endDate | string | 是 | `YYYY-MM-DD`，不得晚于今天；当天可能不完整。 |
| reports[].query | object | 是 | 固定报告查询定义。 |
| reports[].query.fields | array<string> | 是 | 固定字段完整表见 [Audience](sp-audience-reporting-v1.md) 或 [Search Impression Share](sp-search-impression-share-v1.md)。 |
| reports[].query.filter | object | 是 | 固定广告产品过滤，不接受自定义。 |
| reports[].query.filter.on | object | 是 | 包含 field、comparisonOperator、not、values。 |
| reports[].query.filter.on.field | string | 是 | 固定 `adProduct.value`。 |
| reports[].query.filter.on.comparisonOperator | string | 是 | 固定 `EQUALS`。 |
| reports[].query.filter.on.not | boolean | 是 | 固定 `false`。 |
| reports[].query.filter.on.values | array<string> | 是 | 固定 `["SPONSORED_PRODUCTS"]`。 |

### 脚本输出与解析

#### 本地解析规则

| 字段 | 类型 | 说明 |
|---|---|---|
| body.success | object/array | 存在时先在该容器递归查找报告；缺失时遍历 body。不等同于本地结果的 success 布尔值。 |
| 报告.reportId | string | 报告任务 ID；创建响应缺失则失败，查询时必须匹配请求任务；找不到相同 ID 则失败，不采用其他任务。 |
| 报告.status | string | 进行中：`PENDING` / `PROCESSING` / `IN_QUEUE` / `IN_PROGRESS`；完成：`COMPLETED` / `SUCCESS`；失败：`FAILED` / `FAILURE` / `CANCELLED` / `CANCELED`。非空未知状态失败，空状态继续等候。 |
| 报告.format | string | 完成时默认 `CSV`；非 CSV 拒绝下载处理。 |
| 报告.completedReportParts / reportParts | array | 完成分片；优先 completedReportParts，兼容 reportParts。无分片可为空报告。 |
| 报告.completedReportParts[] | object/string | 兼容下载描述对象或 URL 字符串；reportParts 的条目约定相同。 |
| 报告.completedReportParts[].url / downloadUrl / location | string | 下载地址的三个兼容名称；全部分片都须下载。URL 不写入最终响应，通用调用的过程记录亦脱敏。 |
| 报告.其他字段 | any | Amazon 原始失败详情保留并脱敏，不限定其错误结构。 |


## 接口：查询洞察报告状态

### 脚本输入与构参

上游 path 固定为 `adsApi/v1/retrieve/reports`。Ads v1 不发送 `Amazon-Advertising-API-Scope`；只传 profile，由后端选择并刷新 Token，禁止调用方传 Amazon 凭证或自定义认证请求头。额外透传环境变量 `SESSION_ID` / `MESSAGE_ID` / `MODE_ID` / `APP_NAME`。网关及报告分片下载超时均为 150 秒。

#### 上游 body（JSON 字符串内）

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| reportIds | array<string> | 是 | 脚本固定传当前原任务 ID：`["REPORT_ID"]`，续跑不重新创建。 |

### 脚本输出与解析

#### 本地解析规则

| 字段 | 类型 | 说明 |
|---|---|---|
| body.success | object/array | 存在时先在该容器递归查找报告；缺失时遍历 body。不等同于本地结果的 success 布尔值。 |
| 报告.reportId | string | 报告任务 ID；创建响应缺失则失败，查询时必须匹配请求任务；找不到相同 ID 则失败，不采用其他任务。 |
| 报告.status | string | 进行中：`PENDING` / `PROCESSING` / `IN_QUEUE` / `IN_PROGRESS`；完成：`COMPLETED` / `SUCCESS`；失败：`FAILED` / `FAILURE` / `CANCELLED` / `CANCELED`。非空未知状态失败，空状态继续等候。 |
| 报告.format | string | 完成时默认 `CSV`；非 CSV 拒绝下载处理。 |
| 报告.completedReportParts / reportParts | array | 完成分片；优先 completedReportParts，兼容 reportParts。无分片可为空报告。 |
| 报告.completedReportParts[] | object/string | 兼容下载描述对象或 URL 字符串；reportParts 的条目约定相同。 |
| 报告.completedReportParts[].url / downloadUrl / location | string | 下载地址的三个兼容名称；全部分片都须下载。URL 不写入最终响应，通用调用的过程记录亦脱敏。 |
| 报告.其他字段 | any | Amazon 原始失败详情保留并脱敏，不限定其错误结构。 |

## 业务入口与运行约定

| 入口 / 选项 | 类型 | 说明 |
|---|---|---|
| `scripts/get_sp_audience_report.py` | CLI | 固定 `reportKind=audience`；参数见 [Audience](sp-audience-reporting-v1.md)。 |
| `scripts/get_sp_search_impression_share.py` | CLI | 固定 `reportKind=search-impression-share`；参数见 [Search Impression Share](sp-search-impression-share-v1.md)。 |
| `--inline` | flag | 强制打印完整响应，仍保存 JSON。 |
| `--no-cache` | flag | 跳过业务成功结果缓存的读取和写入，强制重新获取。 |
| `scripts/check_auth_dependency.py [--json]` | CLI | 本地依赖检查，0 表示找到认证技能；42 且 stderr 含 `DEPENDENCY_MISSING:` 表示缺失，成功含 `DEPENDENCY_OK:`。 |

两个入口自动运行依赖检查，检查器缺失、运行异常或检查不通过均以 42 退出；不跳过依赖。检查器探测环境指定路径、仓库同级、常见安装目录、Hermes 分类及插件路径，完全不联网。

成功结果缓存 24 小时，按 `SESSION_ID`、报告类型和完整参数隔离，读取前确认缓存为成功结果、分片列表合法且所有 `dataFiles[].path` 仍存在；过期、损坏、失败或文件缺失的缓存不复用。缓存目录为 `<cwd>/linkfox/.cache/linkfox-amazon-ads-sp-insights-report/<安全会话标识>/`；未设 SESSION_ID 时缓存标识为 default。失败和未完成结果不缓存；合法成功空报告可缓存，不自动重试。业务封装调用 `call_api.run` 始终带 `--no-cache`，通用层不额外保存或复用第二层响应缓存，避免缓存创建请求或状态轮询。

报告入口落盘根目录优先取 `ACPX_WORKSPACES` 第一个路径下的 `linkfox/`，其次为当前工作目录的 `linkfox/`；均不可写则请求前报错，不回退家目录或系统临时目录。会话标识清理为字母数字、`-`、`_`，最多 80 字符；未设置时自动生成并在进程内稳定。完整 JSON、CSV 及脱敏的接口过程记录都落在 `<根>/<YYYY-MM-DD>/<session>/data/`，维护 `_meta.json` 和 `index.jsonl`。过程记录使用 `-proxy` 标识，不包含预签名 URL；下载 URL 只在内存中交给非 LinkFox 素材下载函数。两个公开入口以响应体的 UTF-8 编码长度判断输出：不超过 8000 字节时全量打印，超过时输出摘要；`--inline` 强制全量打印。

### 入口调用示例

#### 获取 SP Audience 报告

确认账号与日期后运行：

```bash
python scripts/get_sp_audience_report.py '{"profileId":1234567890,"region":"NA","startDate":"2026-08-01","endDate":"2026-08-07","timeUnit":"DAILY","detailLevel":"ACCOUNT"}'
```

#### 获取搜索词展示份额及排名

```bash
python scripts/get_sp_search_impression_share.py '{"profileId":1234567890,"region":"NA","startDate":"2026-08-01","endDate":"2026-08-07","timeUnit":"DAILY"}'
```

#### 恢复已有任务

向用户确认继续后，使用与已有任务报告类型对应的入口及返回的续跑参数：

```bash
python scripts/get_sp_search_impression_share.py '{"profileId":1234567890,"region":"NA","reportId":"REPORT_ID","pollInterval":60,"maxAttempts":20}' --no-cache
```

## 本地工作流响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| success | boolean | 完成为 true；失败及未完成为 false。 |
| status | string | 完成或失败为上游状态；等待窗口结束为 `STILL_PROCESSING`。参数/传输失败时可能缺失。 |
| reportId | string | 已创建或续跑的原任务标识；后续查询、下载或解析失败也保留，禁止盲目重建。 |
| reportKind | string | 成功时为 `audience` / `search-impression-share`。 |
| profileId | integer | 成功时回显授权 profile，展示给用户时不播报该数字。 |
| advertiserAccountId | string | 创建模式成功时返回；仅轮询可能缺失。 |
| fields | array<string> | 创建模式成功时的实际固定字段。 |
| startDate / endDate | string | 创建模式成功时返回请求日期，YYYY-MM-DD。 |
| dateSpanDays | integer | 创建模式成功时返回包含首尾两日的跨度。 |
| totalRows | integer | 成功时全部 CSV 分片的总数据行数，可为 0。 |
| dataFiles | array<object> | 全部成功下载的 CSV 文件。 |
| dataFiles[].part | integer | 从 1 开始的分片序号。 |
| dataFiles[].path | string | CSV 绝对路径。 |
| dataFiles[].rowCount | integer | 该分片的数据行数。 |
| preview | array<object> | 跨全部分片最多 10 行；CSV 单元格保持字符串；字段表见报告参考。 |
| pollAttempts | integer | 本次轮询次数。 |
| elapsedSeconds | number | 开始轮询后的秒数，保留 3 位小数。 |
| _cacheable | boolean | 成功为 true，失败和未完成为 false。 |
| _cache.hit | boolean | 复用业务缓存时为 true。 |
| error | string | 失败/未完成的原因。 |
| details | any | 脱敏失败详情，包含上游正文、path、httpStatus 或参数字段等信息。 |
| lastStatus | string | 等待窗口耗尽前的最后上游状态。 |
| message | string | 未完成提示，明确任务尚未失败且不得重复创建。 |
| resumeHint | object | 未完成结果的续跑提示。 |
| resumeHint.mode | string | 固定 `poll-only`。 |
| resumeHint.note | string | 继续原任务的提示。 |
| resumeHint.params | object | 可直接交给原入口的续跑参数。 |
| resumeHint.params.profileId | integer | 原授权 profile。 |
| resumeHint.params.region | string | 原区域。 |
| resumeHint.params.reportId | string | 原任务 ID。 |
| resumeHint.params.pollInterval | integer | 保留原轮询间隔。 |
| resumeHint.params.maxAttempts | integer | 原次数乘二，上限 120。 |
