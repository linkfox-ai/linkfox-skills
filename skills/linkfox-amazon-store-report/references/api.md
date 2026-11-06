# Amazon 店铺报告 接口说明

## 公共规则

### 调用规范

- **请求基础地址**：`LINKFOX_TOOL_GATEWAY` 默认 `https://tool-gateway.linkfox.com`
- **请求方式**：POST, HTTP 超时 150s
- **请求头**
  - Content-Type: application/json
  - User-Agent: LinkFox-Skill/2.0
  - Authorization: <api_key> (<api_key> 从环境变量 `LINKFOX_AGENT_API_KEY` 或 `LINKFOXAGENT_API_KEY` 读取，未配置则按 SKILL.md 的 **## 解决认证和算力问题** 处理)

### 响应码基本规则

- **正常响应**: HTTP 状态码为 `200`–`299`，且响应体的 `errcode` 不存在、为 `null`、为空字符串（含纯空白）或为 `200`–`299`（数字或数字字符串）。
- **未正常响应**: HTTP 状态码不属于 `200`–`299`，或响应体的 `errcode` 为非空且不属于 `200`–`299` 的值；`0` 和 `false` 不视为空。
- **认证或用量错误**: HTTP 状态码为 `401` / `402`，按 onboarding.md 的指引处理
- **其他情况**: 依据响应体的 `errmsg` 判断具体原因

### 网关错误响应

接口成功对象与错误对象分别处理。统一错误模型仅包含以下字段；本地脚本补充字段见脚本参考。

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer | 网关错误码；HTTP 200 仍可能包含业务错误。 |
| errmsg | string | 网关错误说明，保留原文。 |

参数异常可返回 HTTP 400、errcode=400；上游连接异常可返回 HTTP 200、errcode=1503。代理定位授权时，1002 表示缺少身份或店铺参数，1004 表示未找到当前成员绑定的授权，1005 也可能表示授权失效；路径白名单拒绝同样使用 1005，须结合 errmsg 区分。不得把本地 error、details、transportHttpStatus、outputError 或解析后的业务对象视为网关 DTO 字段。



## 接口：列出现有报告（getReports）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `reports/2021-06-30/reports`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
| method | string | 是 | 本操作上游方法为 `GET`；LinkFox 外层始终 POST。 |
| queryString | string | 否 | 不含 ? 的查询字符串，最长 4096 字符；键值按 RFC 3986 百分号编码，+ 按字面加号处理。 |
| body | string | 否 | 上游请求正文字符串，最长 1,048,576 字符；网关不定义内部业务字段。 |
| contentType | string | 否 | 上游正文类型，最长 128 字符；有正文时默认 application/json。 |

操作所需的脚本输入、路径、查询串与正文构造见 [script-usage.md](script-usage.md)。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| httpStatus | integer | Amazon 上游 HTTP 状态，与 LinkFox 外层 HTTP 状态分别判断。 |
| contentType | string | 上游 Content-Type；响应头缺失时可为空。 |
| body | string | 上游原始响应正文；可为空字符串。网关不定义其内部业务字段。 |
| xAmznRequestId | string | 上游 x-amzn-requestid 响应头原值，可为空。 |
| retryAfter | string | 上游 Retry-After 响应头原值，可为空；不限定为数字。 |
| xAmznRateLimitLimit | string | 上游 x-amzn-RateLimit-Limit 响应头原值，可为空。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 网关正常响应后，本操作仅在上游 `httpStatus=200` 时进入后续业务步骤；先检查状态再解析 body。

| 状态 | 含义与处理 |
|---|---|
| errcode=1002 | 缺参数或认证失败；核对必填项和 API key。 |
| errcode=1503 | 上游连接异常；保留原始说明，不自动重放。 |
| errcode=1005 | 结合 errmsg 区分授权失效与路径未放行；后者联系后端核对放行配置。 |
| 上游 400 | 参数错误；核对 reportType、marketplaceIds、日期及请求体。 |
| 上游 403 | 店铺权限、区域、令牌或品牌备案不满足；不当作计费错误。 |
| 上游 404 | 资源不存在；核对任务或文档 ID 及所属店铺。 |
| 上游 429 | 请求过快；遵循店铺保护及退避要求，不自动并发重试。 |
| 上游 500 | Amazon 服务异常；保留任务 ID，由用户决定延后查询。 |
| 450 / 453 / 454 / 459 | 完整触发阈值、冷却、停止范围及恢复要求见 [店铺保护与重试](spapi-protection.md)。优先遵循 retryAfter / blockedUntil。 |

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "region": "NA",
  "sellerId": "A1EC6SZ7XAMURH",
  "path": "reports/2021-06-30/reports",
  "method": "GET",
  "queryString": "reportTypes=GET_MERCHANT_LISTINGS_ALL_DATA&marketplaceIds=ATVPDKIKX0DER"
}'
```


## 接口：创建报告（createReport）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `reports/2021-06-30/reports`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
| method | string | 是 | 本操作上游方法为 `POST`；LinkFox 外层始终 POST。 |
| queryString | string | 否 | 不含 ? 的查询字符串，最长 4096 字符；键值按 RFC 3986 百分号编码，+ 按字面加号处理。 |
| body | string | 否 | 上游请求正文字符串，最长 1,048,576 字符；网关不定义内部业务字段。 |
| contentType | string | 否 | 上游正文类型，最长 128 字符；有正文时默认 application/json。 |

操作所需的脚本输入、路径、查询串与正文构造见 [script-usage.md](script-usage.md)。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| httpStatus | integer | Amazon 上游 HTTP 状态，与 LinkFox 外层 HTTP 状态分别判断。 |
| contentType | string | 上游 Content-Type；响应头缺失时可为空。 |
| body | string | 上游原始响应正文；可为空字符串。网关不定义其内部业务字段。 |
| xAmznRequestId | string | 上游 x-amzn-requestid 响应头原值，可为空。 |
| retryAfter | string | 上游 Retry-After 响应头原值，可为空；不限定为数字。 |
| xAmznRateLimitLimit | string | 上游 x-amzn-RateLimit-Limit 响应头原值，可为空。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 网关正常响应后，本操作仅在上游 `httpStatus=202` 时进入后续业务步骤；先检查状态再解析 body。
- 缺少 reportId 时停止；创建结果不确定时先查已有任务，不重放创建。

| 状态 | 含义与处理 |
|---|---|
| errcode=1002 | 缺参数或认证失败；核对必填项和 API key。 |
| errcode=1503 | 上游连接异常；保留原始说明，不自动重放。 |
| errcode=1005 | 结合 errmsg 区分授权失效与路径未放行；后者联系后端核对放行配置。 |
| 上游 400 | 参数错误；核对 reportType、marketplaceIds、日期及请求体。 |
| 上游 403 | 店铺权限、区域、令牌或品牌备案不满足；不当作计费错误。 |
| 上游 404 | 资源不存在；核对任务或文档 ID 及所属店铺。 |
| 上游 429 | 请求过快；遵循店铺保护及退避要求，不自动并发重试。 |
| 上游 500 | Amazon 服务异常；保留任务 ID，由用户决定延后查询。 |
| 450 / 453 / 454 / 459 | 完整触发阈值、冷却、停止范围及恢复要求见 [店铺保护与重试](spapi-protection.md)。优先遵循 retryAfter / blockedUntil。 |

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "region": "NA",
  "sellerId": "A1EC6SZ7XAMURH",
  "path": "reports/2021-06-30/reports",
  "method": "POST",
  "body": "{\"reportType\":\"GET_MERCHANT_LISTINGS_ALL_DATA\",\"marketplaceIds\":[\"ATVPDKIKX0DER\"]}",
  "contentType": "application/json"
}'
```


## 接口：查询报告状态（getReport）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `reports/2021-06-30/reports/{reportId}`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
| method | string | 是 | 本操作上游方法为 `GET`；LinkFox 外层始终 POST。 |
| queryString | string | 否 | 不含 ? 的查询字符串，最长 4096 字符；键值按 RFC 3986 百分号编码，+ 按字面加号处理。 |
| body | string | 否 | 上游请求正文字符串，最长 1,048,576 字符；网关不定义内部业务字段。 |
| contentType | string | 否 | 上游正文类型，最长 128 字符；有正文时默认 application/json。 |

操作所需的脚本输入、路径、查询串与正文构造见 [script-usage.md](script-usage.md)。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| httpStatus | integer | Amazon 上游 HTTP 状态，与 LinkFox 外层 HTTP 状态分别判断。 |
| contentType | string | 上游 Content-Type；响应头缺失时可为空。 |
| body | string | 上游原始响应正文；可为空字符串。网关不定义其内部业务字段。 |
| xAmznRequestId | string | 上游 x-amzn-requestid 响应头原值，可为空。 |
| retryAfter | string | 上游 Retry-After 响应头原值，可为空；不限定为数字。 |
| xAmznRateLimitLimit | string | 上游 x-amzn-RateLimit-Limit 响应头原值，可为空。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 网关正常响应后，本操作仅在上游 `httpStatus=200` 时进入后续业务步骤；先检查状态再解析 body。
- IN_QUEUE / IN_PROGRESS 仅轮询原任务；DONE 仍须有 reportDocumentId；FATAL / CANCELLED 或未知状态立即停止，不换类型、不新建。
- FATAL 的常见原因包括该店铺不支持所选报告类型、数据不足或所选时间范围无数据。结合返回详情与该类型的权限、日期要求解释，不能仅凭 FATAL 确定具体原因；停止后由用户决定查权限、核对日期或重试。

| 状态 | 含义与处理 |
|---|---|
| errcode=1002 | 缺参数或认证失败；核对必填项和 API key。 |
| errcode=1503 | 上游连接异常；保留原始说明，不自动重放。 |
| errcode=1005 | 结合 errmsg 区分授权失效与路径未放行；后者联系后端核对放行配置。 |
| 上游 400 | 参数错误；核对 reportType、marketplaceIds、日期及请求体。 |
| 上游 403 | 店铺权限、区域、令牌或品牌备案不满足；不当作计费错误。 |
| 上游 404 | 资源不存在；核对任务或文档 ID 及所属店铺。 |
| 上游 429 | 请求过快；遵循店铺保护及退避要求，不自动并发重试。 |
| 上游 500 | Amazon 服务异常；保留任务 ID，由用户决定延后查询。 |
| 450 / 453 / 454 / 459 | 完整触发阈值、冷却、停止范围及恢复要求见 [店铺保护与重试](spapi-protection.md)。优先遵循 retryAfter / blockedUntil。 |

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "region": "NA",
  "sellerId": "A1EC6SZ7XAMURH",
  "path": "reports/2021-06-30/reports/REPORT_ID",
  "method": "GET"
}'
```


## 接口：获取报告文档（getReportDocument）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `reports/2021-06-30/documents/{reportDocumentId}`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
| method | string | 是 | 本操作上游方法为 `GET`；LinkFox 外层始终 POST。 |
| queryString | string | 否 | 不含 ? 的查询字符串，最长 4096 字符；键值按 RFC 3986 百分号编码，+ 按字面加号处理。 |
| body | string | 否 | 上游请求正文字符串，最长 1,048,576 字符；网关不定义内部业务字段。 |
| contentType | string | 否 | 上游正文类型，最长 128 字符；有正文时默认 application/json。 |

操作所需的脚本输入、路径、查询串与正文构造见 [script-usage.md](script-usage.md)。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| httpStatus | integer | Amazon 上游 HTTP 状态，与 LinkFox 外层 HTTP 状态分别判断。 |
| contentType | string | 上游 Content-Type；响应头缺失时可为空。 |
| body | string | 上游原始响应正文；可为空字符串。网关不定义其内部业务字段。 |
| xAmznRequestId | string | 上游 x-amzn-requestid 响应头原值，可为空。 |
| retryAfter | string | 上游 Retry-After 响应头原值，可为空；不限定为数字。 |
| xAmznRateLimitLimit | string | 上游 x-amzn-RateLimit-Limit 响应头原值，可为空。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 网关正常响应后，本操作仅在上游 `httpStatus=200` 时进入后续业务步骤；先检查状态再解析 body。
- 缺少 url 或下载失败时停止。只有文件已落地才报告下载成功；默认交付已解压文件，Amazon 源地址仅按需输出。

| 状态 | 含义与处理 |
|---|---|
| errcode=1002 | 缺参数或认证失败；核对必填项和 API key。 |
| errcode=1503 | 上游连接异常；保留原始说明，不自动重放。 |
| errcode=1005 | 结合 errmsg 区分授权失效与路径未放行；后者联系后端核对放行配置。 |
| 上游 400 | 参数错误；核对 reportType、marketplaceIds、日期及请求体。 |
| 上游 403 | 店铺权限、区域、令牌或品牌备案不满足；不当作计费错误。 |
| 上游 404 | 资源不存在；核对任务或文档 ID 及所属店铺。 |
| 上游 429 | 请求过快；遵循店铺保护及退避要求，不自动并发重试。 |
| 上游 500 | Amazon 服务异常；保留任务 ID，由用户决定延后查询。 |
| 450 / 453 / 454 / 459 | 完整触发阈值、冷却、停止范围及恢复要求见 [店铺保护与重试](spapi-protection.md)。优先遵循 retryAfter / blockedUntil。 |

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "region": "NA",
  "sellerId": "A1EC6SZ7XAMURH",
  "path": "reports/2021-06-30/documents/DOCUMENT_ID",
  "method": "GET"
}'
```


## 运行约定

### 依赖与认证兼容

每次先检查 `linkfox-amazon-store-auth`。依赖探测器兼容目录别名 `linkfox-amazon-spapi-auth`；返回 0 且 stderr 含 DEPENDENCY_OK 表示已安装，42 且 DEPENDENCY_MISSING 表示缺失。缺失时先尝试安装工具，无工具则引导用户到技能市场安装后重跑；不得直接调用 authorizeUrl、authorizedStores、storeTokens 或 refreshToken 绕过依赖。

探测位置包括相邻/扁平 skills 根、Claude、Cursor、OpenClaw 工作区的 skills 和 .agents/skills、用户级 ~/.openclaw/skills 和 ~/.agents/skills、Hermes 分类及插件目录；Hermes 的 config.yaml 不由脚本解析，external_dirs 用 HERMES_SKILLS_EXTERNAL_DIRS 注入（系统路径分隔符连接）。完整兼容环境变量如下。

| 变量 | 说明 |
|---|---|
| LINKFOX_AGENT_API_KEY / LINKFOXAGENT_API_KEY | LINKFOX_AGENT_API_KEY 优先，兼容 LINKFOXAGENT_API_KEY；均无值时按 onboarding.md 处理。 |
| LINKFOX_TOOL_GATEWAY | 网关地址，最高优先级。 |
| STORE_API_BASE_URL / SPAPI_BASE_URL | 未配置上项时依次兼容，默认 https://tool-gateway.linkfox.com。 |
| SESSION_ID | 会话归档标识；未设置则在进程内生成并保持一致。 |
| MESSAGE_ID / MODE_ID / APP_NAME | 公共调用器保留同名请求头透传。 |
| LINKFOX_SKILLS_DIR / SKILLS_DIR / CURSOR_SKILLS_DIR | 显式指定扁平 skill 根目录。 |
| OPENCLAW_WORKSPACE / OPENCLAW_ROOT / OPENCLAW_WORKDIR | 探测工作区 skills 与 .agents/skills。 |
| OPENCLAW_SKILLS_DIR | 额外 OpenClaw skills 根目录。 |
| HERMES_SKILLS_EXTERNAL_DIRS | 显式外部根目录，按系统路径分隔符连接。 |
| HERMES_SKILLS_HOME | 非默认 Hermes 分类根目录。 |

服务端令牌约 1 小时到期；developerProxy 使用 sellerId + region 解析/续签。需要重新授权或刷新时交给认证技能。后端 `sp-api.developer-proxy.allowed-path-prefixes` 必须放行报告和文档资源路径，默认前缀含 `reports/2021-06-30/reports`；文档路径也需核对。

### 脚本 JSON 参数

`python scripts/get_report.py '<JSON 参数>' [--inline] [--no-cache]`。Python 3.10+；报告流程仅使用标准库。维护报告文档摘录的脚本另需 beautifulsoup4，不参与报告获取。

| 参数 | 类型 | 必填 | 默认值、约束与说明 |
|---|---|---|---|
| sellerId | string | 是 | 已授权店铺 ID。 |
| region | string | 是 | NA / EU / FE（不区分大小写）；按选店结果原样传递，与授权记录匹配。 |
| reportType | string | 是 | 报告类型枚举。 |
| marketplaceIds | array[string] | 是 | 目标站点列表。 |
| dataStartTime | string | 否/视报告 | 传入 createReport 同名字段。 |
| dataEndTime | string | 否/视报告 | 传入 createReport 同名字段。 |
| lastUpdatedDate | string | 否/视报告 | 仅字符串写入 createReport，部分 Vendor 报告需要。 |
| reportOptions | object | 否/视报告 | 仅对象原样写入 createReport；reportPeriod、asin/asins、dateGranularity、asinGranularity 等的精确键和枚举见对应专页。 |
| pollInterval | integer / number | 否 | 默认 30 秒；正数，轮询间隔须结合实际上游配额/保护时间调大。 |
| maxAttempts | integer | 否 | 默认 20；正整数；达到次数即停止，保留任务 ID。 |
| skipDepCheck | boolean | 否 | 默认 false；仅确认依赖已满足时可跳过本地检查，不绕过授权。 |
| serveExtractedFileHttp | boolean | 否 | 默认 true，启动已解压文件的临时 HTTP。 |
| serveHost | string | 否 | 默认 127.0.0.1。 |
| servePort | integer | 否 | 默认 0，由系统分配空闲端口。 |
| serveSeconds | integer | 否 | 默认 300；开启服务时最少 10 秒，JSON 输出后阻塞保持服务，期满关闭。 |
| includeAmazonSourceUrl | boolean | 否 | 默认 false；为 true 时输出 Amazon 预签名源地址。 |
| omitAmazonDownloadUrl | boolean | 否 | 兼容项优先：true 隐藏源地址，false 输出源地址。 |
| --inline | CLI flag | 否 | 强制完整输出，同时落盘。 |
| --no-cache | CLI flag | 否 | 兼容公共入口；业务脚本调用 run 时始终添加，不读写响应缓存。公共调用器可能创建空缓存目录。 |

### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| success | boolean | 本地下载完成时为 true；不能用创建报告成功代替。 |
| reportId | string | 报告任务 ID。 |
| reportDocumentId | string | 报告文档 ID。 |
| reportType | string | 用户请求的报告类型。 |
| downloadPath | string | 已解压文件的绝对路径，含文件名。 |
| fileName | string | 与 downloadPath 末段一致。 |
| localFileUri | string | 本机 file:// URI。 |
| extractedFileHttpUrl | string | 临时本机 HTTP 地址；仅成功启动时返回。 |
| extractedFileHttpServeSeconds | integer | 服务保持秒数。 |
| extractedFileHttpNote | string | 同一机器、限时有效的说明。 |
| amazonDownloadUrl | string | 按需返回的 Amazon 源地址，多为压缩包。 |
| amazonDownloadUrlNote | string | 源地址与本机已解压地址的区别。 |
| compressionAlgorithm | string | 若返回压缩算法则带上，例如 GZIP。 |
| tempDirectory | string | 本次下载与解压目录，位于当前会话 data 目录内。 |
| fileSize | integer | 文件字节数。 |

### 文件与等待限制

- 完整网关响应按 create-report / get-status / get-document / list-reports 分别落盘；中间文件位置写到 stderr，stdout 展示最终结果及归档提示。业务封装校验保存内容，完整响应未成功保存时立即停止，不继续轮询或下载。最终结果同样保存，8 KB 以上仅展示摘要，--inline 强制完整打印。
- 输出固定到 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/`；请求前检查可写，不回退到用户目录、ACPX_WORKSPACES 或 /tmp。下载与解压使用该会话内的临时子目录。
- Reports API 的参考速率约为 0.0222 req/s；脚本默认轮询间隔为 30 秒，须按实际上游配额、限流和响应提示增加等待。部分财务报告可能生成 10–30 分钟，必要时由用户确定增加等待预算。
- 报告类型可能仅可按计划生成、已弃用、限特定站点或账号，最小请求示例不是通用可用性保证。Brand Analytics 通常需品牌备案；Vendor 类型仅限 Vendor。遵循逐类型文档，不自动试错补参数。
- 下载使用流式写入；GZIP 元数据或 gzip 文件头任一命中即尝试解压。损坏、截断或其他解压失败时保留原下载文件并以退出码 1 停止，不将压缩包或不完整文件标为已解压结果。
- FATAL、CANCELLED、403、解析失败、下载失败或超时均停止，不自动更换报告类型、连续试探或重新创建报告；保留原 reportId / reportDocumentId 以便后续查询。店铺保护的详细阈值与恢复边界见 [spapi-protection.md](spapi-protection.md)。

### 退出码

| 退出码 | 含义 |
|---|---|
| 0 | 下载与结果输出成功。 |
| 1 | 参数、网关、上游、报告生成、下载或超时等错误。 |
| 42 | 认证依赖缺失，stderr 提供 DEPENDENCY_MISSING。 |

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-amazon-store-report",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
