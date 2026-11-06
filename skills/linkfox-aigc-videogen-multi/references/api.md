# 多参考图生视频 接口说明

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
- **请求地址**：`${LINKFOX_AI_API_URL}/image/video/model/config/list?bizType=88`。
- **基础地址**：`LINKFOX_AI_API_URL`，默认 `https://ai-api.linkfox.com`，与生成网关独立配置。
- **请求头**：`Referer: https://wiki.linkfox.com/`、`User-Agent: LinkFox-Skill/2.0`；无需认证，不发送生成密钥或会话身份头。

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| bizType | integer（查询参数） | 是 | 本技能固定为 `88`。 |

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

`python scripts/aigc_videogen_multi.py --list-models --inline`

脚本返回 `source`、`models` 和完整结果路径 `dataFile`；选型使用 `models[].name`，创建参数使用 `models[].requestValue`。视频请求值依据 `code` 规范化，不使用 `apiCode`。
查询支持 `--no-cache` 和 `--allowed-models '<JSON 数组>'`，后者仅按明确业务限制筛选模型。查询不创建任务或改写生成参数。

仅查询失败时返回 `source=fallback` 并使用本技能的静态列表，需告知用户正在使用兜底信息；查询成功但列表为空、模型缺失或处于维护状态时，不恢复静态选项。

完整字段、兼容映射和输出约定见[模型配置说明](model-config.md)。

## 接口：创建多参考图视频任务

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/aigc/multiImageVideoGenAsync`

异步创建任务，取得任务编号后查询结果；生成网关未设置时采用公共规则默认地址。

### 请求参数

`imageList` 中若有本地图片或附件，先按 [file-upload.md](file-upload.md) 上传，保持原顺序并用成功项的 `url` 替换；已有可公开访问的 HTTP(S) URL 直接复用。生成接口不接收本地路径，上传失败不创建任务，查询时不重复上传。

| 参数 | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| imageList | array[string] | 是 | - | 多参考图列表，至少 1 张可公开访问的 HTTP(S) 图片 URL，不接收本地路径。上限按所选模型当前动态配置；仅配置查询失败时使用下方静态模型能力表 |
| videoType | string | 是 | 可灵Omni | 模型枚举优先通过[查询模型枚举](#接口查询模型枚举)获取，使用脚本结果的 `models[].requestValue`；仅查询失败时使用下方静态列表兜底。已有兼容请求值不强制改写，内部请求值不向用户展示。 |
| videoTime | integer | 是 | - | 视频时长(秒)，见下方各模型支持对照 |
| prompt | string | 否 | - | 强化内容描述（3000字符以内） |
| promptOptimizer | boolean | 否 | false | 是否开启提示词优化 |
| isPro | boolean | 否 | - | 仅在所选模型支持且用户明确需要时传入 |
| voice | boolean | 否 | - | 仅在所选模型支持且用户明确需要时传入 |
| aspectRatio | string | 否 | 按模型 | 视频比例，以所选模型配置为准；仅在所选模型支持时传入 |
| memberId | string | 否 | 空字符串 | 调用兼容字段；创建请求原样保留，轮询时随任务传递 |
| resolution | string | 否 | 按模型 | 默认值按所选模型确定，见下方静态模型能力表 |

#### 静态模型能力

以下静态模型列表及能力仅在查询失败时兜底，不限制查询成功时的可选范围。

仅配置查询失败时兜底；动态配置正常时不以静态表限定可选范围。至少提供 1 张图，按所选模型能力准备参数；脚本不进行通用执行前参数校验。

| 说明名称 | videoTime（秒） | imageList 上限 | isPro | voice | aspectRatio | resolution（默认值） |
|---|---|---|---|---|---|---|
| 可灵Omni | 5/10/15 | 7 | 支持 | 不支持 | 1:1/9:16/16:9 | 720p/1080p，默认720p |
| Seedance 2.0 | 4～15 | 9 | 支持 | 支持 | 9:16/16:9/1:1/4:3/3:4/21:9 | 480p/720p/1080p，默认480p |
| Seedance 2.0 fast | 4～15 | 9 | 不支持 | 支持 | 9:16/16:9/1:1/4:3/3:4/21:9 | 480p/720p，默认480p，不支持1080p |
| Seedance 2.5 | 4～30 | 30 | 未定义 | 支持 | 9:16/16:9/1:1/4:3/3:4/21:9 | 480p/720p/1080p，默认480p |
| HappyHorse 1.1 | 5/10/15，默认15 | 9 | 不支持 | 不支持 | 9:16/16:9/1:1/4:3/3:4/21:9 | 720p/1080p，默认720p |
| Seedance 2.0 mini | 4～15，默认10 | 9 | 未定义 | 支持 | 9:16/16:9/1:1/4:3/3:4/21:9 | 480p/720p，默认480p |
| MiniMax H3 | 5/10/15，默认5 | 9 | 未定义 | 不支持 | 16:9/9:16/1:1/4:3/3:4/21:9/adaptive | 768p/2K，默认2K |

#### 内部执行映射（禁止向用户展示）

面向用户的回复、选项、确认和错误解释必须使用“说明名称”，禁止输出内部 videoType 或内部渠道名称。

| 说明名称 | 内部 videoType |
|------|------|
| 可灵Omni | `KLING` |
| Seedance 2.0 | `SEED` |
| Seedance 2.0 fast | `SEED_FAST` |
| Seedance 2.5 | `SEED_V25` |
| HappyHorse 1.1 | `HAPPY_HORSE` |
| Seedance 2.0 mini | `SEED_MINI` |
| MiniMax H3 | `MINIMAX_V2` |

可选模型以当前目录和目标接口能力为准；生成请求使用本接口规定的格式。MiniMax H3 内部渠道差异不得展示给用户。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| `taskId` | string | 异步任务ID，用于后续轮询 |
| `costToken` | number | 创建返回的用量，脚本缺失时记为 0，并保留至最终输出 |
| `errcode` | integer / string / null | 网关业务状态码，按公共规则判断 |
| `errmsg` / `msg` / `message` | string | 网关消息（如返回），错误时保留原消息 |
| `code` | integer / string / null | 生成响应兼容业务码；仅缺少 errcode 时检查，0 / 200 表示正常 |
| `errorCode` | integer / string / null | 生成响应业务码；仅缺少 errcode、code 时检查，200 表示正常；失败时保留原值 |

### 响应示例

```json
{"taskId": "123456789"}
```


### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 缺少 `errcode` 时继续检查 `code`，兼容 `0` / `200`；两者均缺少时检查 `errorCode=200`，其他值按业务错误处理。该兼容不改变公共 `errcode` 规则，`errcode=0/false` 仍为异常。
- 参数错误 `400` 或参数校验失败 `10007`：检查参考图、时长、分辨率、比例和声音是否符合所选模型当前能力。
- 创建失败只尝试一次；超时、读错误或缺少任务编号时提交结果可能未知，不自动重建任务。
- 普通生成参数原样提交，不额外查询模型目录，不使用配置白名单或通用执行前参数校验。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/aigc/multiImageVideoGenAsync" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"imageList":["https://example.com/img1.jpg","https://example.com/img2.jpg"],"videoType":"KLING","videoTime":5}'
```

## 接口：查询任务状态

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/aigc/taskQuery`

### 请求参数

| 参数 | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| taskId | string | 是 | - | 创建任务时返回的任务ID |
| memberId | string | 否 | 空字符串 | 保留原创建参数中的成员标识，脚本查询时传递 |

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| `errcode` | integer / string / null | 网关业务状态码，按公共规则判断 |
| `errmsg` / `msg` / `message` | string | 网关消息（如返回），错误时保留原消息 |
| `code` | integer / string / null | 生成响应兼容业务码；仅缺少 errcode 时检查，0 / 200 表示正常 |
| `errorCode` | integer / string / null | 生成响应业务码；仅缺少 errcode、code 时检查，200 表示正常；失败时保留原值 |
| `taskId` | string | 任务ID |
| `status` | string | 任务状态：`PROCESSING`(处理中) / `SUCCESS`(成功) / `FAILED`(失败) |
| `resultList` | array[object] | 结果列表（仅 SUCCESS 时有值） |
| `resultList[].id` | string | 资源ID |
| `resultList[].url` | string | 生成的视频URL（已转存至OSS） |
| `resultList[].type` | string | 资源类型 |
| `errorMsg` | string | 错误信息（仅 FAILED 时有值） |

### 响应示例

处理中：
```json
{"taskId": "123456789", "status": "PROCESSING", "resultList": null, "errorMsg": null}
```

成功：
```json
{"taskId": "123456789", "status": "SUCCESS", "resultList": [{"id": "1001", "url": "https://oss.example.com/aigc/123456789/result_1001.mp4", "type": "video"}], "errorMsg": null}
```

失败：
```json
{"taskId": "123456789", "status": "FAILED", "resultList": null, "errorMsg": "生成失败"}
```


#### 轮询策略

| 项目 | 约定 |
|---|---|
| 初始等待 | 120 秒 |
| 轮询间隔 | 10 秒 |
| 总等待预算 | 1200 秒（包含初始等待），单次请求最多 150 秒且不超过剩余预算 |
| 终止状态 | `SUCCESS` / `FAILED` |
| 暂态查询错误 | HTTP 408/429/5xx 或连接、超时、读取错误可在原预算内继续查原任务 |
| 其他查询错误 | 立即返回错误与原任务编号，可续查，不重建任务 |
| 通常生成耗时 | 100～600 秒，不保证固定完成时间 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 缺少 `errcode` 时检查 `code`（兼容 `0` / `200`）；两者均缺少时检查 `errorCode=200`，其他值按业务错误处理，不改变公共 `errcode` 规则。
- `PROCESSING` 表示处理中；`SUCCESS` 后下载 `resultList` 中的视频；`FAILED` 使用 `errorMsg` 解释失败。
- `10009` 表示任务不存在，核对原任务编号；`10007` 表示参数校验失败。其他业务错误参考 `errmsg`。
- 等待预算耗尽是客户端超时；不表示服务端失败或算力已回补。查询时不重复上传素材，不重建任务。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/aigc/taskQuery" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"taskId":"123456789","memberId":""}'
```

### 脚本退出码与续查

| 退出码 | 含义 | 处理 |
|---|---|---|
| 0 | 生成成功且媒体已交付；或目录查询完成 | 媒体使用 `Saved full response: [路径数组]` 标记；目录输出配置 JSON |
| 1 | 创建/查询/服务端失败、参数错误或媒体未交付 | 查看 stdout 摘要和 `dataFile`，不自动重建任务 |
| 2 | 本地轮询预算耗尽 | 保留 `taskId` 续查 |

| 输出字段 | 类型 | 说明 |
|---|---|---|
| error / errorCode | string / integer | 错误说明与分类；空体、无效编码、非 JSON、非对象结构分别为 `EMPTY_RESPONSE` / `INVALID_ENCODING` / `INVALID_JSON_RESPONSE` / `INVALID_RESPONSE` |
| status | string | 本地等待耗尽为 `TIMEOUT`；媒体未交付为 `DELIVERY_FAILED` |
| taskStatus | string | 最后已知服务端状态，未知为 `UNKNOWN` |
| taskId | string | 原任务编号 |
| pollTimedOut | boolean | 等待耗尽时为 true |
| canQuery | boolean | 原任务可继续查询时为 true |
| lastQueryError | object | 超时时最后一次暂态查询错误（如有），结构同错误诊断 |
| dataFile | string / null | 完整诊断文件；存档失败为 null |
| httpStatus | integer | 可用的外层 HTTP 状态 |
| requestId / traceId | string | 可用的请求追踪标识 |
| contentType | string | 上游内容类型（如可用） |
| responseBytes | integer | 原始响应字节数 |
| details | string | 原始无效正文，仅保存诊断，不直接输出到对话 |
| costToken | number | 原创建响应的用量；最终存档保留 |

HTTP 与业务状态分别判断，原业务码和消息保留；不输出 Python 堆栈。连接、超时、读取错误分别保留 `CONNECTION_ERROR` / `REQUEST_TIMEOUT` / `HTTP_READ_ERROR`，缺少任务编号为 `MISSING_TASK_ID`，服务端失败为 `TASK_FAILED`，无媒体为 `NO_MEDIA_DELIVERED`。

仅续查示例（不重新创建，参数定义见本接口）：

```python
from aigc_videogen_multi import query_task
result = query_task("原taskId", "原memberId或空字符串")
```

### CLI 与缓存

| 用法 | 约定 |
|---|---|
| `python scripts/aigc_videogen_multi.py '<JSON>' [--inline] [--no-cache]` | 执行创建、轮询、下载；JSON 必须为对象；可选标记不改变媒体交付协议 |
| `--list-models [--allowed-models '<JSON数组>'] [--inline]` | 仅查询目录，详见 [model-config.md](model-config.md) |
| 缓存 | 无响应缓存；所有业务 `call_api.run` 调用均传 `--no-cache`；业务适配层跳过公共调用器的缓存目录创建，不读写响应缓存，也不因 cwd 缓存目录不可写而中断会话路径回退 |
| 认证 | 主变量 `LINKFOX_AGENT_API_KEY`，兼容 `LINKFOXAGENT_API_KEY`；保留 SESSION_ID / MESSAGE_ID / MODE_ID / APP_NAME 请求头 |
| 会话落盘 | ACPX_WORKSPACES 首路径、cwd、用户目录、系统临时目录依次选择可写位置；完整响应存 `data/`，视频存 `media/`，登记 `_meta.json` 与 `index.jsonl`；公共响应和媒体共用同一会话，未设置 SESSION_ID 时也不拆分 |

内部映射和 curl 仅供执行，禁止直接向用户展示请求中的内部模型值。

---

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-aigc-videogen-multi",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
