# AI 生视频（单图与首尾帧）接口说明

接口按创建、任务查询、上传凭证和模型枚举分为四项；上传见[文件上传](file-upload.md)，模型枚举定义见下文。认证和算力问题按 [onboarding.md](onboarding.md) 处理。

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

`python scripts/aigc_videogen.py --list-models --inline`

脚本返回 `source`、`models` 和完整结果路径 `dataFile`；选型使用 `models[].name`，创建参数使用 `models[].requestValue`。视频请求值依据 `code` 规范化，不使用 `apiCode`。
查询支持 `--no-cache` 和 `--allowed-models '<JSON 数组>'`，后者仅按明确业务限制筛选模型。查询不创建任务或改写生成参数。

仅查询失败时返回 `source=fallback` 并使用本技能的静态列表，需告知用户正在使用兜底信息；查询成功但列表为空、模型缺失或处于维护状态时，不恢复静态选项。

完整字段、兼容映射和输出约定见[模型配置说明](model-config.md)。

## 接口：创建生视频任务（videoGenAsync）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/aigc/videoGenAsync`

### 请求参数

`imageUrl` 及实际提供的 `lastFrameImageUrl` 若为本地图片或附件，先按 [file-upload.md](file-upload.md) 上传，用成功项的 `url` 填入对应字段；已有可公开访问的 HTTP(S) URL 直接复用。生成接口不接收本地路径，上传失败不创建任务，查询时不重复上传。

| 参数 | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| imageUrl | string | 是 | - | 原图（首帧图），支持 jpg/jpeg/png/webp |
| videoType | string | 是 | 可灵Omni | 模型枚举优先通过[查询模型枚举](#接口查询模型枚举)获取，使用脚本结果的 `models[].requestValue`；仅查询失败时使用下方静态列表兜底。内部请求值不向用户展示。 |
| videoTime | integer | 是 | 5 | 视频时长(秒)，见下方各模型支持对照 |
| prompt | string | 否 | - | 强化内容描述（3000字符以内） |
| promptOptimizer | boolean | 否 | false | 是否开启提示词优化 |
| isPro | boolean | 否 | - | 仅在所选模型支持且用户明确需要时传入 |
| voice | boolean | 否 | - | 仅在所选模型支持且用户明确需要时传入；可灵2.6仅在1080p下使用 |
| lastFrameImageUrl | string | 否 | - | 尾帧图片URL；AgentOS配置中是否支持以当前动态配置的 `supportLastFrame` 为准 |
| aspectRatio | string | 否 | - | 视频比例，以所选模型配置为准；仅在所选模型支持时传入 |
| resolution | string | 否 | 按模型 | 各模型默认值见下方；脚本不自行补写默认值 |

#### 各模型参数支持对照（仅配置查询失败时兜底）

以下静态模型列表及能力仅在查询失败时兜底，不限制查询成功时的可选范围。

| 参数 | 可灵Omni | Seedance 2.0 | Seedance 2.0 fast | 海螺2.3 |
|------|:---:|:---:|:---:|:---:|
| videoTime | 5/10/15秒 | 4～15秒 | 4～15秒 | 6/10秒 |
| isPro | 支持 | 支持 | 不支持 | 支持 |
| voice | 不支持 | 支持 | 支持 | 不支持 |
| lastFrameImageUrl | 不支持 | 不支持 | 不支持 | 不支持 |
| aspectRatio | 1:1/9:16/16:9 | 9:16/16:9/1:1/4:3/3:4/21:9 | 9:16/16:9/1:1/4:3/3:4/21:9 | 不生效 |
| resolution | 720p/1080p | 480p/720p/1080p | 480p/720p(不支持1080p) | 768p/1080p |

#### 更多模型参数支持对照（仅配置查询失败时兜底）

| 参数 | Seedance 2.5 | Seedance 2.0 mini | 万相3.0 | MiniMax H3 | 可灵2.6 |
|------|:---:|:---:|:---:|:---:|:---:|
| videoTime | 4～30秒 | 4～15秒（默认10秒） | 5/10/15/20/25/30秒（默认10秒） | 5/10/15秒（默认5秒） | 5/10秒（默认10秒） |
| voice | 支持 | 支持 | 不支持 | 不支持 | 支持，仅1080p使用 |
| lastFrameImageUrl | 不支持 | 不支持 | 支持 | 支持 | 不支持 |
| aspectRatio | 9:16/16:9/1:1/4:3/3:4/21:9 | 9:16/16:9/1:1/4:3/3:4/21:9 | 16:9/4:3/1:1/3:4/9:16 | 16:9/9:16/1:1/4:3/3:4/21:9/adaptive | 不支持 |
| resolution | 480p/720p/1080p | 480p/720p（默认480p） | 480p/720p/1080p（默认480p） | 768p/2K（默认2K） | 720p/1080p（默认720p） |

#### 内部执行映射（禁止向用户展示）

面向用户的回复、选项、确认和错误解释必须使用“说明名称”，禁止输出内部 videoType 或内部渠道名称。

| 说明名称 | 内部 videoType |
|------|------|
| 可灵Omni | `KLING` |
| Seedance 2.0 | `SEED` |
| Seedance 2.0 fast | `SEED_FAST` |
| Seedance 2.5 | `SEED_V25` |
| 海螺2.3 | `HAILUO` |
| Seedance 2.0 mini | `SEED_MINI` |
| 万相3.0 | `WAN3` |
| MiniMax H3 | `MINIMAX_V2` |
| 可灵2.6 | `MODEL_V2_6` |

#### 模型默认值、入口与请求兼容（仅配置查询失败时兜底）

| 模型 | 默认时长 | 默认分辨率 | 说明 |
|---|---|---|---|
| 可灵Omni | 5秒 | 720p | 一般商品视频的默认推荐。 |
| Seedance 2.0 | 按调用传值 | 480p | 客户端不注入默认值。 |
| Seedance 2.0 fast | 按调用传值 | 480p | 客户端不注入默认值。 |
| Seedance 2.5 | 按调用传值 | 480p | 4～30秒。 |
| 海螺2.3 | 按调用传值 | 768p | 6秒或10秒。 |
| Seedance 2.0 mini | 10秒 | 480p | 支持单图和多图入口。 |
| 万相3.0 | 10秒 | 480p | 仅单图入口，支持尾帧，不开放多图。 |
| MiniMax H3 | 5秒 | 2K | 支持单图和多图入口、尾帧；内部渠道差异不向用户展示。 |
| 可灵2.6 | 10秒 | 720p | 仅单图入口；声音能力仅在1080p下使用。 |

上述表和参数表记录服务端/业务默认策略，生成脚本按 JSON 原值提交，不自行补写默认值或调用模型目录校验。模型能力、尾帧与时长均以当前动态目录为准；只有目录查询失败才使用静态表。静态兜底表中仅万相3.0、MiniMax H3支持尾帧，这不构成动态目录的能力上限。实际时长必须符合所选模型能力，否则服务端报错。普通参数不能据目录静默重写。

#### 补充透传字段与脚本选项

| 参数 / 选项 | 类型 | 必填 | 默认 | 说明 |
|---|---|---|---|---|
| memberId | string | 否 | 空字符串 | 生成 JSON 可传；轮询使用同一值。 |
| --inline | CLI flag | 否 | false | 目录查询时完整打印目录；生成仍只输出媒体路径，不泄露临时 URL。 |
| --no-cache | CLI flag | 否 | 始终生效 | 业务封装禁用响应缓存；调用 run 都添加此选项，无第二层缓存。适配器跳过公共调用器的空缓存目录准备，不读写响应缓存。 |
| --help / -h | CLI flag | 否 | - | 只打印本地帮助，不发请求；与 --list-models 同时使用时仍优先显示帮助。 |

脚本 CLI：`python scripts/aigc_videogen.py '<JSON>' [--inline] [--no-cache]`（从 skill 根目录运行）。未知业务字段原样透传，换行占位符 `⏎` 递归还原为换行；生成前不按能力白名单拦截请求。模型查询选项见 [model-config.md](model-config.md)。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| taskId | string | 异步任务ID，用于后续轮询。 |
| costToken | number | 响应中的实际消耗字段；缺失时脚本按 0 记录，最终结果保留，该缺省值不代表免费。 |
| errcode | integer / string / null | 网关业务状态；按公共基础规则判断，不把 0 或 false 当成功。 |
| errmsg | string | 网关业务消息；失败时保留。 |
| errorCode | string / number | 上游已有错误码，错误时保留，不代替 errcode 基础判断。 |
| code | string / number（以实际返回为准） | 上游兼容诊断码，原样保留，不代替 errcode 基础判断。 |
| msg | string | 上游兼容消息，存在时原样保留。 |
| message | string | 上游兼容消息，存在时原样保留。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 正常响应仍须存在 `taskId` 才可轮询；缺失时返回 `MISSING_TASK_ID`，创建结果可能未知，不自动重提。
- `10007` 表示参数校验失败，检查时长、分辨率、比例、声音或尾帧；`400` 为参数错误，其他业务异常保留原消息。基础认证/用量处理遵循公共规则。
- 生成一般需 100～600 秒；创建失败仅尝试一次，不更换模型或自动重建任务。空体或非 JSON 只说明上游响应异常，不推测模型不可用。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/aigc/videoGenAsync" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"imageUrl":"https://example.com/product.jpg","videoType":"KLING","videoTime":5}'
```

## 接口：查询任务状态（taskQuery）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/aigc/taskQuery`

### 请求参数

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|---|---|---|
| taskId | string | 是 | - | 创建时返回的任务ID；续查必须使用原值。 |
| memberId | string | 否 | 空字符串 | 封装从生成参数提取并随每次查询发送。 |

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| taskId | string | 任务ID。 |
| status | string | `PROCESSING`（处理中）/ `SUCCESS`（成功）/ `FAILED`（失败）。未知状态原样保留，不捏造成功或失败。 |
| resultList | array[object] / null | 成功时的结果列表。 |
| resultList[].id | string | 资源ID。 |
| resultList[].url | string | 已转存 OSS 的生成视频 URL；下载后只向用户展示本地路径。 |
| resultList[].type | string | 资源类型。 |
| errorMsg | string / null | FAILED 时的错误信息。 |
| errcode | integer / string / null | 网关业务状态，按基础规则判断。 |
| errmsg | string | 网关错误消息。 |
| errorCode | string / number | 上游原始错误码，出现时保留。 |
| code | string / number（以实际返回为准） | 上游兼容诊断码，原样保留，不代替 errcode 基础判断。 |
| msg | string | 上游兼容消息，出现时保留。 |
| message | string | 上游兼容消息，出现时保留。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- `10009` 表示任务不存在，核对 taskId；只查原任务，不自动创建新任务。
- `SUCCESS` 或 `FAILED` 才结束服务端状态轮询；只有媒体下载成功才算完成交付，FAILED 保留 errorMsg。
- 轮询预算：先等 120 秒，每 10 秒查一次，包含初始等待的总上限 1200 秒；单次查询最多 150 秒，并缩短到剩余预算。查询遇 HTTP 408/429/5xx 或连接、读取、请求超时可在此预算内续查；非暂态错误立即退出，不重提生成。
- 客户端超时不等于服务端失败、取消或算力回补；返回原 taskId、最后已知 taskStatus 和可续查标志。不要在同一轮反复 sleep；需要续查时直接调用本接口。

原任务续查可在 Python 中将本技能 `scripts/` 加入模块路径后导入 `aigc_videogen.query_task(task_id, member_id)`，只调用一次；不要调用会创建新任务的 main。SUCCESS 时复用同模块 `_download_results(result)` 下载并交付本地路径；处理中或失败时报告状态和任务ID，不把结果 URL 直接给用户。直接调用公共 run 时也应显式传 `--no-cache`。

#### 生成脚本输出与退出码

| 字段 / 标记 | 类型 | 说明 |
|---|---|---|
| Saved full response: [路径数组] | stdout 文本 | 成功交付媒体到会话 `media/`；禁止 Read 视频文件或展示 base64、临时 URL。 |
| error / errorCode | string / number | 失败摘要及错误码；完整原始响应静默存 data/，无堆栈输出。 |
| dataFile | string / null | 失败诊断文件；保存失败时为 null。 |
| httpStatus | integer | 可用时保存 HTTP 状态。 |
| contentType | string | 可用时保存响应内容类型。 |
| responseBytes | integer | 可用时保存原始响应体字节数。 |
| requestId | string | 可用时保留请求标识。 |
| traceId | string | 可用时保留追踪标识。 |
| status | string | 本地异常为 ERROR、TIMEOUT 或 DELIVERY_FAILED，服务端状态另存。 |
| taskStatus | string | 最后已知服务端状态，无法确认时 UNKNOWN。 |
| taskId | string | 已取得的原任务ID。 |
| pollTimedOut | boolean | 本地轮询超时为 true。 |
| canQuery | boolean | 仍可续查原任务；超时或交付失败时保留。 |
| lastQueryError | object | 超时时仅写入诊断的最后一次查询错误。 |
| costToken | number | 从创建响应保留的消耗字段。 |

| 退出码 | 含义 | 后续动作 |
|---|---|---|
| 0 | 视频媒体已交付；目录查询成功使用其配置输出协议 | 提供本地媒体路径或目录结果。 |
| 1 | 创建/查询失败、服务端失败或无媒体交付 | 读错误摘要及 dataFile；不自动重建任务。 |
| 2 | 本地轮询预算耗尽 | TIMEOUT 不是后端失败；保留原 taskId 续查。 |

生成封装捕获公共调用器 stdout，使用媒体交付协议；`--inline` 不改变该协议。每次创建/查询的完整响应均由公共调用器存档，最终结果另存会话 data/；数据、媒体及索引按会话聚合，支持 `ACPX_WORKSPACES` 和 `SESSION_ID`。根目录依次尝试 `ACPX_WORKSPACES` 的首个路径、当前工作目录、用户目录、系统临时目录下的 linkfox/。公共调用器文件名的接口标识包含操作名和纳秒序号，防止同秒覆盖。视频脚本与上传器复用公共调用器的进程内会话状态；未设置 `SESSION_ID` 时，同一进程的响应、配置、媒体与上传记录也聚合到同一目录。这只稳定会话目录，不是响应缓存，不保证不同进程自动归入同一会话。正常业务环境使用可写的工作目录，避免路径回退。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/aigc/taskQuery" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"taskId":"123456789","memberId":""}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-aigc-videogen",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
