# AI 生图 接口说明

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
- **请求地址**：`${LINKFOX_AI_API_URL}/image/model/config/list?bizType=201`。
- **基础地址**：`LINKFOX_AI_API_URL`，默认 `https://ai-api.linkfox.com`，与生成网关独立配置。
- **请求头**：`Referer: https://wiki.linkfox.com/`、`User-Agent: LinkFox-Skill/2.0`；无需认证，不发送生成密钥或会话身份头。

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| bizType | integer（查询参数） | 是 | 本技能固定为 `201`。 |

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

`python scripts/aigc_imagegen.py --list-models --inline`

脚本返回 `source`、`models` 和完整结果路径 `dataFile`；选型使用 `models[].name`，创建参数使用 `models[].requestValue`。图片请求值由 `apiCode` 及兼容别名规范化。
查询支持 `--no-cache` 和 `--allowed-models '<JSON 数组>'`，后者仅按明确业务限制筛选模型。查询不创建任务或改写生成参数。

仅查询失败时返回 `source=fallback` 并使用本技能的静态列表，需告知用户正在使用兜底信息；查询成功但列表为空、模型缺失或处于维护状态时，不恢复静态选项。

完整字段、兼容映射和输出约定见[模型配置说明](model-config.md)。

## 接口：查询视频模型枚举（共用模块兼容分支）

- **请求方式及地址**：GET `${LINKFOX_AI_API_URL}/image/video/model/config/list?bizType=88`。
- **请求参数**：`bizType` 为必填整数，固定为 `88`。
- **调用与响应**：超时、请求头、原始响应结构和失败兜底规则同[查询模型枚举](#接口查询模型枚举)；视频请求值依据 `code` 规范化。

该接口仅供共用模块的 `load_catalog("video")` 或 `load_catalog("video_multi")` 使用，图片命令行入口不调用。详细映射见[模型配置说明](model-config.md#接口查询视频模型目录共用模块兼容分支)。

## 接口：创建生图任务（imageGenAsync）

异步提交一次任务，立即返回任务 ID。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/aigc/imageGenAsync`

### 请求参数

`imageUrls` 中若有本地图片或附件，先按 [file-upload.md](file-upload.md) 上传，用成功项的 `url` 替换；已有可公开访问的 HTTP(S) URL 直接复用，文生图无需上传。生成接口不接收本地路径，上传失败不创建任务。

| 参数 | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| imageUrls | array[string] | 否 | - | 参考图列表；不传或传空列表时为文生图，传入时为参考图生图，具体上限以动态配置 refImageCount 为准；查询失败用静态兜底表 |
| prompt | string | 是 | - | 提示词，描述期望生成的图片内容 |
| provider | string | 否 | LF智能模型 G-2.5 Sunburst | 模型枚举优先通过[查询模型枚举](#接口查询模型枚举)获取，使用脚本结果的 `models[].requestValue`；仅查询失败时使用下方静态列表兜底。用户指定时沿用其选择；内部请求值不向用户展示。 |
| outputNum | integer | 否 | 1 | 输出张数，取值范围 [1, 10]；未传时默认1 |
| resolution | string | 否 | 按模型 | 分辨率：`1K` / `2K` / `4K`，必须使用所选模型支持的值。Sunburst 首轮未指定时显式传 1K；其他模型按其支持的规格传参，用户指定的值原样透传 |
| aspectRatio | string | 否 | 由下游决定 | 宽高比以所选模型配置为准；工具端未指定时不透传此字段，建议显式传入合法比例 |
| quality | string | 否 | low | 图片质量：`low` / `medium` / `high` / `xhigh` / `max`。未指定时先用 `low`；用户确认后若选择重出 2K，改为 `medium` |

#### 内部执行映射（禁止向用户展示）

以下静态模型列表及能力仅在查询失败时兜底，不限制查询成功时的可选范围。

面向用户的回复、选项、确认和错误解释必须使用“说明名称”，禁止输出内部请求值。

| 说明名称 | provider 内部请求值 |
|------|------|
| LF全能模型 | `LF_BN_1` |
| LF全能模型 2 | `LF_BN_2` |
| LF全能模型 Pro | `LF_BN_3` |
| LF智能模型 G-2 | `LF_GT_1` |
| Linkfox-Image-1 | `LF_AD_1` |
| Wan 2.7 | `LF_WN_1` |
| Seedream 5.0 | `LF_SD_1` |
| LF智能模型 G-2.5 Sunburst | `LF_GT_2` |
| LF智能模型 G-2.5 Flare | `LF_GT_2_F` |
| Seedream 5.0 Pro | `LF_SD_2` |

上表模型支持所列请求别名；动态目录中未列于上表的图片模型使用 apiCode 构造请求参考值，由目录模块规范化。未传 provider 时按 LF全能模型 Pro 执行。

#### 图片模型参数支持对照（仅配置查询失败时兜底）

| 参数 | LF智能模型 G-2.5 Sunburst | LF智能模型 G-2.5 Flare | Seedream 5.0 Pro |
|------|:---:|:---:|:---:|
| resolution | 1K/2K/4K（未指定先1K） | 1K/2K/4K（默认2K） | 1K/2K |
| imageUrls上限 | 10张 | 10张 | 6张 |
| quality | low/medium/high/xhigh/max | low/medium/high/xhigh/max | 不使用 |
| aspectRatio | 1:1/3:4/4:3/2:3/3:2/9:16/16:9/4:5/5:4/21:9/9:21 | 1:1/3:4/4:3/2:3/3:2/9:16/16:9/4:5/5:4/21:9/9:21 | 1:1/3:4/4:3/9:16/16:9/3:2/2:3/21:9 |

#### 补充兼容字段与使用限制

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|---|---|---|
| memberId | string | 否 | 空字符串 | 脚本读取后原样用于任务查询；创建 JSON 中若有此字段也原样透传。 |

参数原样透传，`⏎` 会在字符串中解码为换行，嵌套数组和对象同样处理。内部选择时显式传入所选模型的合法分辨率。A+ 版位比例 `1464:600`、`970:600`、`600:450` 原样传递，不逐字符串误拦，不裁切、补边或近似替换。完整静态能力、有效参考图上限与渠道去重规则见 [model-config.md](model-config.md)。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| taskId | string | 异步任务 ID，用于后续轮询。 |
| costToken | number | 脚本读取的算力消耗；缺失时按 0 记录，不据此推断免费。 |
| errcode | integer / string / null | 业务状态码；判断方式见公共规则。 |
| errmsg | string | 业务消息。 |
| code / msg / message / errorCode / error | 原值 | 脚本兼容的消息与错误字段；未返回时不补造。 |

### 响应示例

```json
{"taskId": "123456789"}
```

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 请求完成不等于图片已生成；缺少 `taskId` 返回 `MISSING_TASK_ID`，不得自动重提。
- `400` 表示参数错误，检查必填参数；`401` / `authorized error` 为认证失败，`402` 为算力或余额不足，按 [onboarding.md](onboarding.md) 引导；其他业务异常根据实际消息解释。
- 业务封装兼容仅有 `code` 而无 `errcode` 的响应：code 为 0 或 200（含对应字符串）时视为业务成功，其他非 null 值按业务错误处理；这不改变公共 errcode 判断，errcode=0 / false 仍为错误。
- 生成通常需要 10–120 秒，视模型与分辨率而异；创建失败不自动重试，仅提交一次。

### curl 示例

内部调用示例，禁止向用户展示模型技术值。

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/aigc/imageGenAsync" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"imageUrls":["https://example.com/ref.jpg"],"prompt":"product on white background","provider":"LF_GT_2","outputNum":1,"resolution":"1K","aspectRatio":"1:1","quality":"low"}'
```

## 接口：查询任务状态（taskQuery）

根据原任务 ID 查询状态与结果，不创建新任务。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/aigc/taskQuery`

### 请求参数

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|---|---|---|
| taskId | string | 是 | — | 创建任务返回的任务 ID。 |
| memberId | string | 否 | 空字符串 | 脚本从创建 JSON 读取的成员标识，查询时原样发送。 |

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| taskId | string | 任务 ID。 |
| status | string | `PROCESSING`（处理中）/ `SUCCESS`（成功）/ `FAILED`（失败）。 |
| resultList | array[object] / null | 结果列表，仅 SUCCESS 时有值。 |
| resultList[].id | string | 资源 ID。 |
| resultList[].url | string | 生成图片 URL，已转存至 OSS。 |
| resultList[].type | string | 资源类型。 |
| errorMsg | string / null | 错误消息，仅 FAILED 时有值。 |
| errcode | integer / string / null | 业务状态码；判断方式见公共规则。 |
| errmsg | string | 业务消息。 |
| code / msg / message / errorCode / error | 原值 | 兼容的业务码、消息及错误字段；仅保留上游已返回的值。 |

### 响应示例

```json
{"taskId":"123456789","status":"SUCCESS","resultList":[{"id":"1001","url":"https://oss.example.com/aigc/123456789/result_1001.png","type":"image"}],"errorMsg":null}
```

处理中为 `status=PROCESSING`，`resultList=null`、`errorMsg=null`；失败为 `status=FAILED`，`resultList=null`，`errorMsg` 说明失败原因。

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- `10009` 表示任务不存在，检查任务 ID。服务端 `FAILED` 表示生成失败；不自动重新创建任务。
- 业务封装兼容仅有 `code` 而无 `errcode` 的响应：0 / 200（含对应字符串）视为业务成功，其他非 null 值按业务错误处理；errcode 仍按公共规则。
- 初始轮询间隔 10 秒，每次减 1 秒至最低 5 秒，最多等待 600 秒；`SUCCESS` 或 `FAILED` 终止轮询，单次请求时限不超过剩余等待预算与 150 秒中的较小值。
- 查询遇到 408、429、5xx 或连接、请求超时、读取错误时，可在本次等待预算内继续查询同一任务；其他查询错误停止，保留任务 ID 与最后已知状态。
- 超时是客户端等待结束，不能解释为后端失败、取消或费用回补；不在同一轮反复 sleep，也不换模型。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/aigc/taskQuery" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"taskId":"123456789","memberId":""}'
```

### 脚本 CLI、落盘与异常

| 入口或选项 | 类型 | 说明 |
|---|---|---|
| `python scripts/aigc_imagegen.py '<JSON>'` | CLI | 一次创建、轮询、下载与交付，不额外查询模型，不拦截未知模型请求值。 |
| `--inline` | CLI flag | 生成仍保留媒体路径数组交付；模型查询强制输出完整能力。 |
| `--list-models` / `--allowed-models` | CLI flag / JSON array | 仅查询模型，详见 [model-config.md](model-config.md)。 |
| `--no-cache` | CLI flag / 内部固定选项 | 业务封装每次调用 `call_api.run` 固定加入，不读写响应缓存，不依赖响应缓存目录。 |

续查只使用原 ID，可由同目录模块调用（不会创建任务）：

```python
import sys
sys.path.insert(0, "<skill目录>/scripts")
from aigc_imagegen import query_task, _download_results
result = query_task("原 taskId", "原 memberId 或空字符串")
if result.get("status") == "SUCCESS" and not result.get("error"):
    paths = _download_results(result)
```

生成网关默认 `https://tool-gateway.linkfox.com`，允许 `LINKFOX_TOOL_GATEWAY` 覆盖；认证同时兼容两种密钥变量。`SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 请求头透传。

生成的完整最终响应或失败诊断由业务封装静默保存到会话 `data/`，中间创建与轮询响应不额外写文件，公共调用器不另建自动会话；图片落到 `media/`。根目录依次尝试 `ACPX_WORKSPACES` 的首个路径、当前工作目录、用户目录、系统临时目录下的 `linkfox/`，选中后进程内固定。优先 `SESSION_ID`，否则自动生成并在进程内固定；登记 `_meta.json` 与 `index.jsonl`。所有候选根目录均不可写时报告存档错误。数据文件用微秒时间戳避免同秒覆盖；媒体同样使用微秒命名（如 `linkfox-aigc-imagegen-<ts_us>.png`）。

成功只向 stdout 输出媒体路径数组，完整最终结果静默保存；部分图片下载成功时交付已下载路径，失败项由 stderr 提示，不自动重建任务；失败时 stdout 输出 `Saved full response: <原始响应路径>` 和错误 JSON，不输出堆栈，媒体不能作为文本读取。公共调用器的中间输出被封装捕获，避免任务原始 URL 或模型技术值混入媒体交付。

| 退出码 | 含义 | 处理 |
|---|---|---|
| 0 | 生成成功且媒体已交付；模型查询成功运行也正常结束 | 图片使用路径数组标记；模型目录使用普通 JSON。 |
| 1 | 创建、查询、服务端失败或媒体未交付 | 读取错误摘要和 `dataFile`，不自动重建任务。 |
| 2 | 本地轮询预算耗尽 | 保留原 taskId 续查，不能理解为后端失败。 |

#### 脚本错误与诊断字段

| 字段 | 类型 | 说明 |
|---|---|---|
| error / errorCode | string | 错误消息和错误标识。 |
| errcode / code / errmsg / msg | 原值 | 保留上游已返回的业务字段。 |
| traceId / requestId | string | 上游追踪 ID；请求 ID 也可来自 X-Request-Id / X-Kong-Request-Id。 |
| httpStatus | integer | 可取得的 HTTP 状态。 |
| contentType / responseBytes | string / integer | 响应类型与原始字节数。 |
| details | string | 非 JSON 等完整原始诊断，仅写入数据文件，不出现在失败 stdout 摘要。 |
| dataFile | string / null | 完整诊断路径，存档失败时为 null。 |
| status | string | 本地等待耗尽为 TIMEOUT；交付失败为 DELIVERY_FAILED；其他错误默认 ERROR。 |
| taskStatus | string | 最后已知服务端状态，未知为 UNKNOWN。 |
| taskId | string | 续查的原任务 ID。 |
| pollTimedOut | boolean | 等待预算耗尽时为 true。 |
| canQuery | boolean | 保留原任务供续查时为 true。 |
| lastQueryError | object | 仅等待超时且曾遇到可重试查询错误时保留。 |
| costToken | number | 最终结果保留创建响应的算力字段，缺失时 0。 |

| errorCode | 说明 |
|---|---|
| INVALID_PARAMETERS | JSON 无法解析或不是对象。 |
| EMPTY_RESPONSE / INVALID_ENCODING / INVALID_JSON_RESPONSE / INVALID_RESPONSE | 空体、非 UTF-8、非 JSON 或 JSON 非对象，不能编造模型不可用原因。 |
| HTTP_ERROR / HTTP_READ_ERROR | HTTP 状态异常或协议读取失败；提交结果可能未知。 |
| CONNECTION_ERROR / REQUEST_TIMEOUT | 连接异常或请求超时；不自动重提任务。 |
| MISSING_TASK_ID | 创建响应缺任务 ID，禁止自动重提。 |
| TASK_FAILED | 服务端 FAILED 或原任务查询失败。 |
| POLL_TIMEOUT | 本地等待结束，taskStatus 保留最后已知状态。 |
| NO_MEDIA_DELIVERED | 没有成功下载媒体，服务端可能已成功，只查原任务。 |

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-aigc-imagegen",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
