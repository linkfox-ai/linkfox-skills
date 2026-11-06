# 商品视频复刻 接口说明

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

## 接口：查询模型枚举

### 调用规范

- **请求方式**：GET，超时 5 秒。
- **请求地址**：`${LINKFOX_AI_API_URL}/image/video/model/config/list?bizType=89`。
- **基础地址**：`LINKFOX_AI_API_URL`，默认 `https://ai-api.linkfox.com`，与生成网关独立配置。
- **请求头**：`Referer: https://wiki.linkfox.com/`、`User-Agent: LinkFox-Skill/2.0`；无需认证，不发送生成密钥或会话身份头。

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| bizType | integer（查询参数） | 是 | 本技能固定为 `89`。 |

### 响应结构

接口返回 `code` 和 `data`：HTTP 请求成功、`code` 为 `200` 或 `"200"` 且 `data` 为数组时，查询成功。

| 字段 | 类型 | 说明 |
|---|---|---|
| data[].code | string | 模型配置标识。 |
| data[].name | string | 模型展示名称。 |
| data[].apiCode | string | 下游模型标识，按实际返回提供。 |
| data[].supportedRatios / supportedResolutions / supportedDurations / supportedQualities | array[string] / null | 支持的比例、分辨率、时长和质量档位。 |
| data[].refImageCount | integer | 模型参考图上限，仍须遵守创建接口的素材数量限制。 |
| data[].isMaintenance | boolean | 维护标记；脚本排除维护中的模型。 |

### 脚本调用

`python scripts/video_reclone_async.py --list-models --inline`

脚本返回 `source`、`models` 和完整结果路径 `dataFile`；选型使用 `models[].name`，创建参数使用 `models[].requestValue`。优先使用 `apiCode`，缺失时使用脚本已知映射；无法确定时为 `null`，须先核实，不能猜测。
查询支持 `--no-cache` 和 `--allowed-models '<JSON 数组>'`，后者仅按明确业务限制筛选模型。查询不创建任务或改写生成参数。

仅查询失败时返回 `source=fallback` 并使用本技能的静态列表，需告知用户正在使用兜底信息；查询成功但列表为空、模型缺失或处于维护状态时，不恢复静态选项。

## 接口：商品视频复刻（videoReclone）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/aigc/videoReclone`

### 请求参数


| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| requestId | String | 否 | 可选兼容字段；提供时原样转发，缺失时不补充 |
| chatId | String | 否 | Agent会话ID，最长128字符 |
| messageId | String | 否 | Agent消息ID，最长128字符 |
| title | String | 否 | 业务展示标题 |
| params | Object | 是 | 非空业务参数对象，字段见下表；身份由认证凭证解析，不传顶层memberId |

#### params 业务参数

必填字段及模型限制如下；创建入口本地只校验 params 非空，具体业务校验由下游执行。

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| params.videoType | String | 是 | 模型枚举优先通过[查询模型枚举](#接口查询模型枚举)获取，使用脚本结果的 `models[].requestValue`；仅查询失败时使用下方静态列表兜底。 |
| params.refVideoUrl | String | 是 | 参考视频的公网 URL（需长期有效，避免使用短期签名 URL）。|
| params.refImageList | List<String> | 是 | 参考商品图 URL 列表，至少 1 张；数量上限按模型区分，见下方各模型参数支持情况。|
| params.resolution | String | 是 | 视频分辨率，可选值见下方各模型参数支持情况|
| params.saleCountry | String | 是 | 销售国家（如 CN、US）|
| params.targetLanguage | String | 是 | 目标语言（如 zh、en）|
| params.videoTime | Integer | 否 | 目标视频时长（秒），支持值按模型区分，见下方各模型参数支持情况；不传时使用模型默认值。 |
| params.aspectRatio | String | 否 | 视频比例；不传使用厂商默认比例，传值须受所选模型支持，见下方模型参数说明。 |
| params.productInfo | String | 否 | 补充商品文字信息，用于辅助 AI 分析，最多 2500 字符。|
| params.prompt | String | 否 | 最终提示词。传入后将跳过 AI 分析直接按该提示词生成视频；不传则由系统自动分析参考视频与商品图后生成。|

#### 任务上下文与使用限制

- 网关请求外层为 OpenApiImageMakeDto，对应 tools 的 feature-workbuddy-change 分支契约。顶层仅定义 requestId、chatId、messageId、title、params；业务字段都放在 params，params 必须为非空对象。创建入口仅本地校验 params 非空，完整业务校验由下游执行。
- 成员及团队由认证身份解析，不传顶层 memberId。chatId、messageId 最长 128 字符；不以 memberId 指定创建任务归属。
- 所有素材，包括外部 HTTP(S) URL，都先按 [素材上传](file-upload.md) 下载并上传，生成 API 仅接受返回的 viewUrl；禁止直接使用源 URL、本地路径、Base64 或 data URI。低层创建入口不承担上传或轮询；上传失败停止，不创建收费任务。
- 实际下游为 `/image/auth/agent/imagemake/videoReclone`。V3 `/image/v3/make/videoReclone` 及 V3/V4 仅用于说明业务能力，不作为网关调用入口。
- requestId 为可选兼容字段；提供时原样转发，缺失时不自动生成。同一任务使用已接受的 taskId 恢复查询，不因超时自动重复提交。

#### 各模型参数支持情况

以下静态模型列表及能力仅在查询失败时兜底，不限制查询成功时的可选范围。

| 模型 | 分辨率 | 时长（秒） | 参考图上限 |
| --- | --- | --- | --- |
| minimax-h3-lite | 768P | 5/10/15 | 9 |
| minimax-h3 | 768P / 2K | 5/10/15 | 9 |
| wan3 | 480P / 720P / 1080P | 5/10/15/20/25/30 | 10 |
| doubao-seedance-2-5 | 480P / 720P / 1080P | 5/10/15/20/25/30 | 30 |
| doubao-seedance-2-0 | 480P / 720P / 1080P | 5/10/15 | 6 |
| doubao-seedance-2-0-fast | 480P / 720P | 5/10/15 | 6 |
| doubao-seedance-2-0-mini | 480P / 720P | 5/10/15 | 6 |
| happyhorse-v2 | 720P / 1080P | 5/10/15 | 9 |

#### 模型参数说明

- 参考视频必须为长期稳定可访问的公网地址，Gemini 在异步分析阶段访问；短期签名可能失效。参考图在提交时同步下载，不能访问会立即报错。
- productInfo 最多 2500 字符，仅未传 prompt、走自动分析时生效；可提供商品名和卖点。
- prompt 是最终提示词，传入会跳过 AI 分析直接生成，适合已有分镜或对分析结果二次编辑后提交；不传则分析参考视频与商品图，耗时通常更长。
- aspectRatio 不传使用厂商默认比例。各模型支持的比例枚举未列明，仅传入可确认受支持的值，不推断额外可选值；传入不支持的值会报错。
- doubao-seedance-2-0-fast 与 doubao-seedance-2-0-mini 不支持 1080P，应使用 480P 或 720P。时长、图数和分辨率以模型表为准；不自动改模型或参数试探。

#### 脚本运行约定

| 项目 | 类型 | 说明 |
|---|---|---|
| JSON 参数 | object | 低层入口接收一个 JSON 对象；`--inline` 强制完整打印；`--no-cache` 禁用业务缓存。 |
| 认证环境变量 | string | 优先 `LINKFOX_AGENT_API_KEY`，备用 `LINKFOXAGENT_API_KEY`；不存储于请求参数或落盘产物。 |
| 上下文请求头 | string | 透传 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME`；不主动伪装渠道，未发送渠道头时 `externalAgentPlatform` 默认 skill。 |
| 响应适配 | object | 兼容 JSON 与网关 `ToolErrorResponse` XML；XML 的 `errcode`、`errmsg` 标准化为同名字段。保留 HTTP 状态及费用头，不只依据进程退出码判断。 |
| 会话目录 | path | 当前工作目录必须可写；禁止 `/tmp` 回退；公共调用器原生可回退，业务封装在请求前验证并固定当前目录。文件以 UTF-8 写入，每次保存独立响应文件。 |
| 响应缓存 | object | 创建和直接上传入口使用 24 小时业务缓存及参数哈希；创建缓存位于 `<cwd>/linkfox/.cache/linkfox-aigc-video-reclone/`，上传缓存使用其下 uploadByBase64 子目录隔离接口。缺少 apiPath 的缓存仅在可凭 taskId 或 viewUrl 识别接口归属时兼容复用；归属不明的结果不复用。查询始终禁用缓存。调用 `call_api.run` 一律加 `--no-cache`，不启用第二层缓存。素材辅助入口也始终禁用上传缓存。 |

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| taskId | string | 已接受的异步任务编号；不是完成的媒体。保存后调用 taskQuery。 |
| costToken | integer / string | 创建响应为 0，不代表最终免费；如有 X-Cost-Token 费用头，以响应头实际值为准。能转整数时转整数，否则保留原值。 |
| costCredit | integer / string | 可选；由 X-Cost-Credit 费用头保留，能转为整数时转为整数，其余保留原值。 |
| transportHttpStatus | integer / null | 业务封装保存的实际 HTTP 状态；连接失败为 null；缓存未记录 HTTP 状态时兼容读取结果，并按业务字段判断。 |
| errcode | integer / string | 可选网关业务码；XML 标准化后亦使用此字段。 |
| code | integer / string | 业务响应可能提供的可选状态码；保留原值，兼容 code=0 或字符串 0 表示成功；其余非空值须为 2xx。该兼容不覆盖 HTTP 和 errcode 的基础规则，false 仍为失败。 |
| errmsg | string | 可选网关错误或业务说明。 |
| error | string | 可选连接、HTTP 或无效响应错误；不得继续依赖链。 |
| details | string / object / array | 可选原始异常响应内容；仅供脱敏排查，不视作媒体。 |
| _cache | object | 本地业务缓存元信息，非服务端业务字段。 |
| _cache.hit | boolean | 本地业务缓存命中时为 true。 |
| _cache.apiPath | string | 缓存所属的网关接口；缺失时按业务字段识别归属。 |

下游业务文档的字段仅用于理解，不能替代网关响应契约：

| 下游字段 | 类型 | 说明 |
|---|---|---|
| data.id | 任务编号（类型未限定） | 下游创建返回的编号；网关使用 taskId。 |
| data.status | integer | 下游查询 3 为成功、4 为失败；网关使用 PROCESSING/SUCCESS/FAILED。 |
| data.resultList[].url | string | 下游生成媒体地址；网关读取 resultList[].url。 |
| count | number（扣费值） | 下游费用按 2000 倍换算；不从创建的 0 推断最终费用。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 返回 taskId 只表示任务被接受。缺少编号、存在 error 或业务错误时停止，不盲目执行后续依赖。
- 参数错误检查支持的 videoType、时长、图数、分辨率和比例；素材不可访问或分析失败时核对地址。失败不自动更换模型、重新创建或增加数量。
- 403 是成员归属或权限失败，不通过充值解决；原生账号和支付指引见 [onboarding.md](onboarding.md)，不将验证码、登录 Token 或 Key 写入任务产物。

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/aigc/videoReclone" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H 'Content-Type: application/json' \
  -H 'User-Agent: LinkFox-Skill/2.0' \
  --data '
{"params":{"videoType":"doubao-seedance-2-5","refVideoUrl":"https://example.com/uploaded-reference.mp4","refImageList":["https://example.com/uploaded-product.png"],"resolution":"720P","saleCountry":"US","targetLanguage":"en"}}
'
```

示例只说明结构。素材必须换成上传返回的 viewUrl；requestId 可省略，提供时使用本次新任务的唯一值；不对占位地址执行收费测试。

### 扣费参考

以下为模型配置的扣费参考，实际费用以当前配置和扣除为准。

| 模型 | 扣费配置（点/秒） |
| --- | --- |
| minimax-h3-lite （配置默认） | 768P：**3** |
| wan3 | 480P：**18**<br>720P：**35**<br>1080P：**71** |
| doubao-seedance-2-5 | 480P：**53**<br>720P：**119**<br>1080P：**324** |
| doubao-seedance-2-0-fast | 480P：**21**<br>720P：**43** |
| doubao-seedance-2-0-mini | 480P：**7**<br>720P：**14** |
| doubao-seedance-2-0 | 480P：**45**<br>720P：**85**<br>1080P：**300** |
| happyhorse-v2 | 720P：**37**<br>1080P：**48** |
| minimax-h3 | 768P：**40**<br>2K：**64** |

> 扣点数 = 单价（点/秒）× 视频时长（秒）。



## 接口：创作任务查询（taskQuery）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/aigc/taskQuery`

### 请求参数

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| taskId | String | 是 | 已接受的任务编号；兼容新建及已有图像、视频任务。 |
| memberId | String | 否 | 查询已有任务时可选的成员标识；不能代替凭证或绕过归属权限。 |

#### 使用限制与恢复 CLI

- 查询使用 `/aigc/taskQuery`，不提供独立 makeTaskQuery。每次查询必须禁用响应缓存，query_task.py 即使未显式传 `--no-cache` 也会禁用。
- 不通过查询传 format 或 containsSyntheticPerformer。轮询不再次上传素材或创建任务。
- 完整流程支持 JSON 字符串、`--params-file <路径>` 或 `-` 标准输入，requestId 仅在提供时原样转发，缺失时不补充。恢复使用 `run_task.py --task-id <编号> [--member-id <成员>]`，不得混入创建参数。

| CLI 选项 | 类型 | 默认值与限制 |
|---|---|---|
| --timeout | float | 视频 1200 秒，通用图像分支 600 秒；必须大于 0。 |
| --poll-interval | float | 10 秒，不能为负；视频通常至少间隔 10 秒，图像默认 5–10 秒。 |
| --initial-delay | float | 新视频 120 秒、通用图像分支 10 秒、续查 0；不能为负，不超过本轮超时。 |
| --task-id | string | 仅续查任务，不重新创建；可选 --member-id。 |
| --params-file | path | UTF-8 JSON 文件，不能和位置 JSON 同时提供。 |

#### 脚本运行约定

| 项目 | 类型 | 说明 |
|---|---|---|
| JSON 参数 | object | 低层入口接收一个 JSON 对象；`--inline` 强制完整打印；`--no-cache` 禁用业务缓存。 |
| 认证环境变量 | string | 优先 `LINKFOX_AGENT_API_KEY`，备用 `LINKFOXAGENT_API_KEY`；不存储于请求参数或落盘产物。 |
| 上下文请求头 | string | 透传 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME`；不主动伪装渠道，未发送渠道头时 `externalAgentPlatform` 默认 skill。 |
| 响应适配 | object | 兼容 JSON 与网关 `ToolErrorResponse` XML；XML 的 `errcode`、`errmsg` 标准化为同名字段。保留 HTTP 状态及费用头，不只依据进程退出码判断。 |
| 会话目录 | path | 当前工作目录必须可写；禁止 `/tmp` 回退；公共调用器原生可回退，业务封装在请求前验证并固定当前目录。文件以 UTF-8 写入，每次保存独立响应文件。 |
| 响应缓存 | object | 创建和直接上传入口使用 24 小时业务缓存及参数哈希；创建缓存位于 `<cwd>/linkfox/.cache/linkfox-aigc-video-reclone/`，上传缓存使用其下 uploadByBase64 子目录隔离接口。缺少 apiPath 的缓存仅在可凭 taskId 或 viewUrl 识别接口归属时兼容复用；归属不明的结果不复用。查询始终禁用缓存。调用 `call_api.run` 一律加 `--no-cache`，不启用第二层缓存。素材辅助入口也始终禁用上传缓存。 |

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| taskId | string | 任务编号。 |
| status | string | PROCESSING / SUCCESS / FAILED。未知状态停止轮询并保留任务，不重新创建。 |
| resultList | array<object> | 可用结果列表。 |
| resultList[].id | 未限定 | 资源编号，保留实际返回值，其标量类型未限定。 |
| resultList[].url | string | 结果下载 URL；仅下载 HTTP(S)，不带 API 凭证。 |
| resultList[].type | 未限定 | 来自下游 extendField.type；保留实际返回值，其标量类型未限定。 |
| errorMsg | string | 任务级错误；后端未透出单项生成错误。 |
| costToken | integer / string | 实际查询费用；保留 X-Cost-Token，头部优先，能转为整数时转为整数，否则保留原值。 |
| costCredit | integer / string | 可选实际费用，来自 X-Cost-Credit；缺失时未知。 |
| transportHttpStatus | integer / null | 业务封装保存的实际 HTTP 状态；连接失败为 null；缓存未记录 HTTP 状态时兼容读取结果，并按业务字段判断。 |
| errcode | integer / string | 可选网关业务码；XML 标准化后亦使用此字段。 |
| code | integer / string | 业务响应可能提供的可选状态码；保留原值，兼容 code=0 或字符串 0 表示成功；其余非空值须为 2xx。该兼容不覆盖 HTTP 和 errcode 的基础规则，false 仍为失败。 |
| errmsg | string | 可选网关错误或业务说明。 |
| error | string | 可选连接、HTTP 或无效响应错误；不得继续依赖链。 |
| details | string / object / array | 可选原始异常响应内容；仅供脱敏排查，不视作媒体。 |
| _cache | object | 本地业务缓存元信息，非服务端业务字段。 |
| _cache.hit | boolean | 本地业务缓存命中时为 true。 |
| _cache.apiPath | string | 缓存所属的网关接口；缺失时按业务字段识别归属。 |

当前后端不返回结果项 status、errorCode、errorMsg、width、height、format、size、完整 extendField 或 containsSyntheticPerformer，不推断这些字段。通用下载器兼容已保存响应中存在的单项字段，但不将其当作本接口保证。

成功下载保存媒体和资产清单，终态查询 JSON 保留实际费用与任务级错误；创建 costToken=0 不能覆盖查询费用。

#### 本地资产清单（非 API 返回字段）

| 字段 | 类型 | 说明 |
|---|---|---|
| taskId / status | string | 原查询任务编号与状态。 |
| costToken / costCredit | integer / string / null | 原查询费用；缺失为 null，表示未知。 |
| items | array<object> | 每个结果项的资源、下载情况。 |
| items[].id / items[].type | 原返回值 | 资源标识及类型。 |
| items[].status / errorCode / errorMsg | 原返回值 | 仅兼容已保存响应中存在的单项字段，不补造。 |
| items[].localPath | string | 成功下载文件的绝对路径。 |
| items[].downloadError | string | 下载失败说明；保留查询响应，只重试下载。 |
| mediaPaths | array<string> | 成功下载的本地路径数组，另以 Saved full response 协议行输出。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- PROCESSING 继续查询；SUCCESS 下载媒体；FAILED 保留任务错误并停止。超时保留 taskId，续查不创建新任务。
- 404 表示任务不存在，403 表示归属或权限失败；不将其作为充值问题。查询错误保留已有响应，不自动创建新任务。
- 下载失败只重跑 `scripts/download_results.py <成功查询JSON>`；不触发新的收费生成。没有成功文件时保留查询 JSON，不能以 JSON 代替媒体交付。

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/aigc/taskQuery" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H 'Content-Type: application/json' \
  -H 'User-Agent: LinkFox-Skill/2.0' \
  --data '
{"taskId":"已接受的任务编号"}
'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-aigc-video-reclone",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
