# 视频翻译与任务查询 接口说明

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
- **请求地址**：`${LINKFOX_AI_API_URL}/image/video/model/config/list?bizType=96`。
- **基础地址**：`LINKFOX_AI_API_URL`，默认 `https://ai-api.linkfox.com`，与生成网关独立配置。
- **请求头**：`Referer: https://wiki.linkfox.com/`、`User-Agent: LinkFox-Skill/2.0`；无需认证，不发送生成密钥或会话身份头。

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| bizType | integer（查询参数） | 是 | 本技能固定为 `96`。 |

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

`python scripts/video_translation_async.py --list-models --inline`

脚本返回 `source`、`models` 和完整结果路径 `dataFile`；选型使用 `models[].name`，创建参数使用 `models[].requestValue`。优先使用 `apiCode`，缺失时使用脚本已知映射；无法确定时为 `null`，须先核实，不能猜测。
查询支持 `--no-cache` 和 `--allowed-models '<JSON 数组>'`，后者仅按明确业务限制筛选模型。查询不创建任务或改写生成参数。

仅查询失败时返回 `source=fallback` 并使用本技能的静态列表，需告知用户正在使用兜底信息；查询成功但列表为空、模型缺失或处于维护状态时，不恢复静态选项。

## 接口：视频翻译

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/aigc/videoTranslation`

### 请求参数

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| requestId | String | 否 | 可选兼容字段；提供时原样转发，缺失时不补充 |
| chatId | String | 否 | Agent会话ID，最长128字符 |
| messageId | String | 否 | Agent消息ID，最长128字符 |
| title | String | 否 | 业务展示标题 |
| params | Object | 是 | 非空业务参数对象，字段见下表；身份由认证凭证解析，不传顶层memberId |

#### params 业务参数

以下为业务必填项及模型限制；网关本地只校验 params 非空，具体业务校验由下游执行。

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| params.sourceVideoUrl | String | 是 | 待翻译原视频的公网 URL；服务端会读取真实媒体时长用于计费|
| params.targetLanguage | String | 是 | 目标语言，支持短代码或 BCP-47 代码，详见下方语言表|
| params.sourceVideoName | String | 否 | 原视频文件名，仅用于历史记录展示|
| params.lipSync | Boolean | 否 | 是否同步口型；默认 true |
| params.videoType | String | 否 | 模型枚举优先通过[查询模型枚举](#接口查询模型枚举)获取，使用脚本结果的 `models[].requestValue`；仅查询失败时使用下方静态列表兜底。未传时使用默认模型。 |

`sourceVideoName`、`lipSync`、`videoType` 均可省略；省略时分别不指定展示文件名、默认开启口型同步、使用默认模型。

#### 任务上下文与素材限制

- 外层仅定义 `requestId`、`chatId`、`messageId`、`title`、`params`；身份及团队由服务端认证解析，禁止发送顶层 `memberId`。普通 skill 未发送渠道头时 `externalAgentPlatform` 默认为 `skill`，不伪装 `workbuddy`。
- 网关契约为 `OpenApiImageMakeDto`；`params` 非空是网关本地校验要求，业务必填和模型条件由下游校验。不要根据本地校验较少而省略业务必填项。
- 业务脚本保留 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 环境变量到同名请求头的透传；查询及上传入口使用相同约定。
- 全部源视频，包括外部 HTTP(S) 地址，必须先按 [file-upload.md](file-upload.md) 上传；真正发送到本接口的 `params.sourceVideoUrl` 只使用返回的 `viewUrl`，上传失败停止。低层创建脚本不负责自动上传。
- 实际下游为 `/image/auth/agent/imagemake/videoTranslation`；V3 的 `/image/v3/make/videoTranslation` 及 V4 业务说明仅作字段与能力参考，不是额外可调用的网关接口，也不应替换本节端点。

#### 支持的语言

`targetLanguage` 必须使用下表中的语言。源语言由服务端自动识别，不提供源语言请求参数。

| 语言 | 短代码 | BCP-47 代码 |
| --- | --- | --- |
| 中文 | `zh` | `zh-CN` |
| 英语 | `en` | `en-US` |
| 日语 | `ja` | `ja-JP` |
| 韩语 | `ko` | `ko-KR` |
| 西班牙语 | `es` | `es-ES` |
| 法语 | `fr` | `fr-FR` |
| 德语 | `de` | `de-DE` |
| 葡萄牙语 | `pt` | `pt-BR` |
| 阿拉伯语 | `ar` | `ar-SA` |
| 泰语 | `th` | `th-TH` |
| 越南语 | `vi` | `vi-VN` |
| 印尼语 | `id` | `id-ID` |
| 马来语 | `ms` | `ms-MY` |

目标语言代码匹配不区分大小写，并兼容下划线形式（例如 `en_US`）。

#### 模型与计费限制

以下静态模型列表及能力仅在查询失败时兜底，不限制查询成功时的可选范围。

自动识别源语言，不提供源语言请求参数。`lipSync` 默认开启；不传 `videoType` 使用默认模型。所有模型（含可灵参考能力）均跟随源视频时长，不支持自定义时长，不传 `videoTime` 或 `duration`。不要据此推断未列出的可调用模型。

模型扣费配置如下，实际配置以本次返回为准。

| 模型 | 扣费配置（点/秒） |
| --- | --- |
| happyhorse-v2 | 按时长：**39** |
| doubao-seedance-2-5 （配置默认） | 按时长：支持有声 **71** |

> 扣点数 = 单价（点/秒）× 计费时长（秒）。计费时长按原视频实际时长向下取整为整数秒；如果当前模型设置了计费时长上限，则以该上限为准。

源视频地址应在异步执行期间持续可访问并返回可解析的视频；无法读取时长时核对地址是否过期。实际扣费配置可调整，以实报为准。下游 `count` 按 2000 倍换算，不能把下游 `id/status/count` 封装当成网关字段使用。

#### 脚本选项与缓存

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| JSON 参数 | object | 是 | 第一个位置参数；完整请求对象。 |
| --inline | CLI flag | 否 | 强制全量打印响应并保存。 |
| --no-cache | CLI flag | 否 | 显式禁用本次创建缓存；不是允许自动重建的依据。 |

`--inline`、`--no-cache` 均可位于 JSON 参数前或后。

创建入口提供 24 小时缓存，唯一缓存位于 `<cwd>/linkfox/.cache/linkfox-aigc-video-translate/`，键按完整参数计算；可读取同路径已接受任务的缓存，不设置第二层缓存。缓存只复用正常且带任务编号的创建结果。任务编号已存在时优先恢复查询，生成失败或结果不明均不得自动重提。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| taskId | string | 已受理任务编号，不代表生成完成。 |
| costToken | integer / string | 创建体返回 0，不表示免费；响应头存在时以头中实际值覆盖。 |
| costCredit | integer / string | 仅实际返回时保留；由 `X-Cost-Credit` 提供，未返回为未知。 |
| errcode | integer / string / boolean / null | 网关业务状态；按基础规则判断，不将 0 或 false 当成功。 |
| errmsg | string | 业务或认证错误说明；仅实际返回时存在。 |
| code | integer / string | 仅实际返回时保留的业务兼容码；与 errcode 区分，依赖链仍检查此字段。 |
| error | string / boolean | 脚本规范化的网络、HTTP 或异常响应错误；存在有效错误时停止依赖链。 |
| details | string | 非 JSON/XML 错误的原始响应；仅异常时存在，展示前脱敏。 |
| _transportHttpStatus | integer / null | 业务兼容层仅在失败时保留的外层 HTTP 状态；连接失败为 null。 |
| _cache.hit | boolean | 脚本复用本地创建缓存时为 true，不是服务端字段。 |

脚本保留 `X-Cost-Token` / `X-Cost-Credit` 头中的实际费用（整数可解析则转整数，否则保留原值），并兼容网关 `ToolErrorResponse` XML，规范化为 `errcode`、`errmsg`。不保存上传请求或凭证。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 正常响应还必须具有 `taskId` 才表示受理；创建费用 0 不能作为完成或免费依据。
- 模型不可用时核对公开模型名称；不自动换模型重提。参数错误核对必填、语言代码和媒体可访问性；403 表示归属或权限，不能通过充值处理。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/aigc/videoTranslation" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"params":{"sourceVideoUrl":"<上传返回的viewUrl>","targetLanguage":"en","lipSync":true}}'
```

## 接口：查询任务

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/aigc/taskQuery`

### 请求参数

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| taskId | string | 是 | 保存的网关任务编号；同一任务始终复用。 |
| memberId | string | 否 | 查询兼容字段，不用于创建时指定身份。 |

本接口同时服务翻译任务和已有图像、视频任务，不存在独立 `makeTaskQuery`。每次至少间隔 10 秒；视频默认先等待 120 秒，总等待上限 20 分钟。`query_task.py` 始终向公共调用器传 `--no-cache`，即使用户省略也不复用或保存查询响应缓存；支持 `--inline` 和显式 `--no-cache`。不要通过查询传 `format` 或 `containsSyntheticPerformer`。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| taskId | string | 任务编号。 |
| status | string | `PROCESSING` / `SUCCESS` / `FAILED`。 |
| resultList | array<object> | 已生成资源列表；仅使用实际返回项。 |
| resultList[].id | string | 资源编号。 |
| resultList[].url | string | 成品下载地址。 |
| resultList[].type | string | 资源类型，来源于下游 `extendField.type`。 |
| errorMsg | string | 任务级错误。 |
| costToken | integer / string | 查询实际报告的消耗；头中存在时以 `X-Cost-Token` 覆盖，不以创建的 0 覆盖。 |
| costCredit | integer / string | 实报的 `X-Cost-Credit`；没有费用字段时表示未知。 |
| errcode | integer / string / boolean / null | 网关业务状态，按基础规则判断。 |
| errmsg | string | 网关消息。 |
| code | integer / string | 仅实际返回时保留的业务兼容码；不能替代公共 errcode 判断。 |
| error | string / boolean | 脚本规范化的网络、HTTP 或异常响应错误。 |
| details | string | 非 JSON/XML 错误响应内容；仅异常时存在，展示前脱敏。 |
| _transportHttpStatus | integer / null | 兼容层仅失败时记录的 HTTP 状态；连接失败为 null。 |

当前网关不透出单项 `status/errorCode/errorMsg`、`width/height/format/size`、完整 `extendField` 或 `containsSyntheticPerformer`。不能根据下游文档推断缺失项。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- `PROCESSING` 继续按节奏查询；`SUCCESS` 才可下载；`FAILED` 保存任务级错误并停止，不自动重建。
- 未知状态、无任务状态或查询错误均保留任务编号并停止；404 表示任务不存在，核对编号和归属，不自动创建新任务。
- 下游响应中的 `data.id`、`data.status=3/4` 与 `data.resultList[].url` 属于下游响应封装，不能替代网关的 `taskId` 及字符串状态。
- 任务失败或长时间无结果时，核对视频地址是否在异步执行期间持续可访问，并检查内容合规、账户算力和上游模型状态；保留任务编号，不自动重建。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/aigc/taskQuery" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"taskId":"<已接受任务编号>"}'
```

### 工作流 CLI

| 入口 / 参数 | 类型 | 必填 | 默认值 / 约定 |
|---|---|---|---|
| run_task.py parameters | object / `-` | 与参数文件、新任务模式配合 | JSON 请求，或 `-` 从 stdin 读取。 |
| --params-file | path | 否 | UTF-8 JSON 文件；不能与位置参数同时提供。 |
| --task-id | string | 恢复时是 | 只查询原任务，不上传、不创建；不能与创建参数混用。 |
| --member-id | string | 否 | 恢复或查询的可选身份兼容字段。 |
| --timeout | number | 否 | 默认 1200 秒，必须为有限正数。 |
| --poll-interval | number | 否 | 默认 10 秒；保留有限非负 CLI 输入，实际间隔至少 10 秒。 |
| --initial-delay | number | 否 | 新任务默认 120 秒，恢复默认 0；必须为有限非负数。 |
| download_results.py response_file | path | 是 | 已保存的 `SUCCESS` 查询 JSON；只下载，不请求 LinkFox。 |

requestId 仅在提供时原样转发，缺失时不补充；业务字段位于非空 `params`，顶层只接收创建接口定义字段。上传替换发生在内存中，不把 Base64 放到操作系统命令行或请求文件。工作流在请求前验证当前目录可写；`ACPX_WORKSPACES` 指向其他目录则报错，避免公共模板回退目录。Windows 使用 UTF-8 模式。

#### 媒体与资产清单

| 字段 / 路径 | 类型 | 说明 |
|---|---|---|
| `<session>/media/` | directory | 成功下载的媒体；原子下载，失败或空文件不留下半成品。 |
| `<session>/data/` | directory | 原始查询响应和资产清单。 |
| taskId / status | string | 清单记录的任务编号和终态。 |
| costToken / costCredit | integer / string / null | 最终查询费用；缺失为 null，不从创建结果补 0。 |
| items | array<object> | 每个实际资源的记录。 |
| items[].id / items[].type | string | 查询返回的资源编号与类型。 |
| items[].status / items[].errorCode / items[].errorMsg | integer / string | 仅查询 JSON 实际带有这些字段时按兼容字段保留；当前网关未透出，不推断补造。 |
| items[].localPath | string | 成功下载后的绝对路径；失败时不填。 |
| items[].downloadError | string | 下载失败时的说明；从保存查询 JSON 重试下载。 |
| mediaPaths | array<string> | 已下载文件的绝对路径。 |

stdout 的 `Saved full response: ["<absolute media path>", ...]` 是媒体展示协议；原始 API 响应打印的是 JSON 文件路径，二者不能混用。HTTP 150 秒下载超时；只接受 HTTP(S) 资源及跳转。素材和成品下载是必要的非 LinkFox HTTP，不发送接口认证头。

---

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-aigc-video-translate",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
