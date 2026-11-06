# 亚马逊商品评论 接口说明

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

## 接口：异步提交评论任务

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/amazon/reviews/async/submit`

### 请求参数

| 参数 | 类型 | 必填 | 说明                                                                                                                             |
|------|------|------|--------------------------------------------------------------------------------------------------------------------------------|
| asin | string | 是 | 亚马逊商品ASIN                                                                                                                      |
| domainCode | string | 否 | 亚马逊域名代码，默认 `com`。可选值：`com`、`ca`、`co.uk`、`in`、`de`、`fr`、`it`、`es`、`co.jp`、`com.au`、`com.br`、`nl`、`se`、`com.mx`、`ae`。美国站使用 `com` |
| star1Num | integer | 否 | 1星评论数量，整数 0–100；未传任何星级时默认 10，显式指定任意星级后其余默认 0                                                                                                          |
| star2Num | integer | 否 | 2星评论数量，整数 0–100；未传任何星级时默认 10，显式指定任意星级后其余默认 0                                                                                                          |
| star3Num | integer | 否 | 3星评论数量，整数 0–100；未传任何星级时默认 10，显式指定任意星级后其余默认 0                                                                                                          |
| star4Num | integer | 否 | 4星评论数量，整数 0–100；未传任何星级时默认 10，显式指定任意星级后其余默认 0                                                                                                          |
| star5Num | integer | 否 | 5星评论数量，整数 0–100；未传任何星级时默认 10，显式指定任意星级后其余默认 0                                                                                                          |
| filterByKeyword | string | 否 | 按关键词筛选评论，最大长度1000字符                                                                                                            |
| sortBy | string | 否 | 评论排序方式：`recent`（最新评论）或 `helpful`（最有用评论），默认 `recent`                                                                            |
| reviewerType | string | 否 | 评论者类型：`all_reviews`（所有评论）或 `avp_only_reviews`（仅认证购买），默认 `all_reviews`                                                          |
| mediaType | string | 否 | 媒体类型：`all_contents`（所有内容）或 `media_reviews_only`（仅包含媒体的评论），默认 `all_contents`                                                    |
| formatType | string | 否 | 格式类型：`all_formats`（所有格式）或 `current_format`（当前格式），默认 `all_formats`                                                           |

无需传 `provider`。后端根据 `domainCode` 自动选择 Pango 或 Apify，实际供应商在提交和查询响应的 `provider` 字段中返回。

#### 使用限制与站点

- 每次仅接受一个 ASIN；多个 ASIN 必须分别请求。数量上限见参数表，不保证返回足量评论。
- filterByKeyword、reviewerType、mediaType 均用于提交阶段，美国站 com 也支持；sortBy 与 formatType 同样属于提交参数，查询接口只需要 taskId。
- 实时抓取，不提供历史快照；评论正文保持买家发布时的原语言。

| 站点 | domainCode |
|---|---|
| 美国 | com |
| 加拿大 | ca |
| 英国 | co.uk |
| 德国 | de |
| 法国 | fr |
| 意大利 | it |
| 西班牙 | es |
| 日本 | co.jp |
| 印度 | in |
| 澳大利亚 | com.au |
| 巴西 | com.br |
| 墨西哥 | com.mx |
| 荷兰 | nl |
| 瑞典 | se |
| 阿拉伯联合酋长国 | ae |

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| --inline | CLI flag | 否 | 完整打印响应，仍保存文件。 |
| --no-cache | CLI flag | 否 | 忽略并不写入业务任务缓存。用提交商品参数会新提交付费任务，仅用户明确要求重试时使用；查询已有任务应传 taskId。 |

业务层提供 24 小时任务缓存；公共 call_api.run 始终传 --no-cache，不另建响应缓存。每次运行仅一次提交或查询，不循环、不休眠。网关默认 HTTP 超时 150s；业务脚本提交和查询的 HTTP 超时均为 30s，并发送 Accept: application/json。会话数据强制保存在 cwd/linkfox，不使用 ACPX_WORKSPACES、家目录或临时目录回退；请求前检查输出目录可写。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| taskId | string | 后续查询使用的任务ID |
| provider | string | 实际选择的供应商 |
| status | string | 初始状态，通常为 `PENDING` |
| pollAfterMillis | integer | 建议下次查询前等待的毫秒数 |

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 网关业务状态码，按公共规则判断。 |
| errmsg | string | 网关消息或具体错误原因。 |
| costToken | integer / string | 若返回 X-Cost-Token，脚本将其写入此字段；提交响应为 0 不代表任务免费。 |
| data / result | object | 兼容网关在其中包装 taskId 和 provider；不保证每次返回包装层。 |

#### 脚本任务标记

| 字段 | 类型 | 说明 |
|---|---|---|
| _asyncTask | object | 脚本的本地任务标记，不是后端结果结构。 |
| _asyncTask.taskId | string | 保存的任务标识。 |
| _asyncTask.provider | string / null | 后端实际选择的供应商。 |
| _asyncTask.status | string / null | 本地保存的任务状态，通常 PENDING。 |
| _asyncTask.pollAfterMillis | integer | 后端建议间隔，未返回时脚本使用 2000 毫秒。 |
| _asyncTask.submittedAt | integer | 本地提交时间，Unix 秒。 |
| _asyncTask.estimatedReadyInSeconds | object | 经验时间窗口，不是 SLA。 |
| _asyncTask.estimatedReadyInSeconds.min | integer | Pango 为 10、Apify 为 15，未知供应商为 10 秒。 |
| _asyncTask.estimatedReadyInSeconds.max | integer | Pango 为 30、Apify 为 60，未知供应商为 60 秒。 |
| _asyncTask.suggestedNextCheckAfterSeconds | integer | 首次为经验下限；后续通常为 10 秒。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 提交只调用一次并立即返回任务标记；任务未完成或单次查询失败不得重新提交。
- 不传 provider；后端根据 domainCode 自动选择 Pango 或 Apify。
- Pango 经验耗时 10–30 秒，Apify 15–60 秒，均非 SLA；优先继续其他工作，到建议时间再查。
- 动态计费与空结果、部分失败、全失败的计费条件见 `../SKILL.md` 的“算力消耗预估”；预估不作为已扣费用。

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/amazon/reviews/async/submit" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -H "Content-Type: application/json" \
  -d '{
    "asin": "B08N5WRWNW",
    "domainCode": "com",
    "star1Num": 10,
    "star2Num": 10,
    "star3Num": 0,
    "star4Num": 0,
    "star5Num": 0,
    "sortBy": "recent",
    "reviewerType": "all_reviews"
  }'
```

## 接口：异步查询评论任务

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/amazon/reviews/async/result`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| taskId | string | 是 | 异步提交返回的任务 ID；仅查询此任务，不重新提交商品参数。 |

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| submittedAt | number | 否 | 仅脚本恢复使用，Unix 秒；缓存记录缺失时辅助计算观察窗口，不转发后端。 |
| --inline | CLI flag | 否 | 完整打印响应，仍保存文件。 |
| --no-cache | CLI flag | 否 | 忽略并不写任务缓存；仍只查传入的 taskId。默认保留任务缓存，公共调用器始终禁用响应缓存。 |

可用原提交参数从 24 小时任务缓存恢复同一 taskId，脚本实际只向查询端点传 taskId。保留 30s HTTP 超时、Accept 头和 cwd 会话目录；数据目录不可写时在请求前报错。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| taskId | string | 任务ID |
| provider | string | 实际使用的供应商 |
| status | string | `PENDING`、`RUNNING`、`SUCCEEDED`、`FAILED` 或 `CANCELLED` |
| error | string | 任务失败原因，仅失败时存在 |
| result | object | 成功后的评论结果 |
| pollAfterMillis | integer | 建议下次查询前等待的毫秒数；结束后为0 |
| createdAt | integer | 任务创建时间，Unix毫秒 |
| startedAt | integer | 任务开始时间，Unix毫秒 |
| completedAt | integer | 任务完成时间，Unix毫秒 |
| expiresAt | integer | 任务结果过期时间，Unix毫秒 |
| costToken | integer | 查询本身为 `0`，任务费用由后端独立结算，不代表整个任务免费 |

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 网关业务状态码，按公共规则判断。 |
| errmsg | string | 网关消息或具体错误原因。 |

#### result 评论结果

| 字段 | 类型 | 说明 |
|------|------|------|
| total | integer | 总评论数 |
| data | array | 评论列表（详见下方评论对象） |
| columns | array | 渲染的列 |
| costToken | integer | 领取结果时为 `0`；此字段不表示任务实际费用，任务费用由后台独立结算 |
| type | string | 渲染的样式 |

#### result.data[*] 评论对象

| 字段 | 类型 | 说明 |
|------|------|------|
| reviewId | string | 评论ID |
| asin | string | 产品ASIN |
| title | string | 评论标题 |
| text | string | 评论内容 |
| rating | string | 评分 |
| date | string | 评论日期 |
| userName | string | 评论者名称 |
| verified | boolean | 是否已验证购买 |
| vine | boolean | 是否Vine Voice评论 |
| numberOfHelpful | integer | 有用数量 |
| imageUrlList | array | 评论图片列表 |
| videoUrlList | array | 评论视频列表 |
| domainCode | string | 本次查询的站点代码，不代表每条评论的来源 |
| reviewCountry | string | 单条评论所在国家/地区，Pango 和 Apify 共用；名称可能本地化，如 `Canada`、`Canadá` 均指加拿大。缺失时不要从 `domainCode` 或 `locale.country` 推断 |
| productTitle | string | 产品标题 |
| productRating | string | 产品评分 |
| countRatings | integer | 产品评分数量 |
| countReviews | integer | 产品评论数量 |
| variationId | string | 变体ID |
| variationList | array | 变体列表 |
| profilePath | string | 评论者个人资料路径 |
| currentPage | integer | 当前页码 |
| sortStrategy | string | 排序策略 |
| statusCode | integer | 状态码 |
| statusMessage | string | 状态消息 |
| locale | object | 区域信息 |
| reviewSummary | object | 评论摘要数据 |
| filters | object | 已应用的筛选条件 |

columns、variationList 的元素结构，以及 locale、reviewSummary、filters 的内部结构以实际返回为准，不预设其内部字段。

#### 脚本查询输出与任务缓存

成功时脚本展开 result 为评论结果；未完成时返回提交接口所列 _asyncTask 标记，并按后端响应附加时间字段。失败或超时输出以下本地字段。

| 字段 | 类型 | 说明 |
|---|---|---|
| _asyncTask.createdAt / startedAt / completedAt / expiresAt | integer | 后端任务时间，Unix 毫秒；仅存在时保留。 |
| status | string | 本地状态可为 POLL_TIMEOUT、ALREADY_RECEIVED，或后端 FAILED、CANCELLED。 |
| taskId | string | 查询的原任务标识。 |
| provider | string / null | 实际供应商，若已知。 |
| error | string | 错误原因；文件缺失时也返回。 |
| details | any | 原始失败信息或异常响应。 |
| httpStatus | integer | HTTP 错误时保留外层状态码。 |
| retryable | boolean | 临时查询失败或 POLL_TIMEOUT 时表示可继续查询同一任务，不表示可以重新提交；CANCELLED 时表示可在用户明确要求重试后重新提交，不再查询已领取的终态任务。 |
| elapsedSeconds | integer / null | 自任务创建或本地提交以来的秒数。 |
| upstreamCancellationSupported | boolean | POLL_TIMEOUT 时为 false，停止查询不能取消上游调用。 |
| resultFile | string / null | 已领取结果的本地文件路径；落盘失败时可为空。 |
| fileExists | boolean | 已领取结果文件是否仍存在。 |
| costToken | integer / string | 本次领取、缓存复用或查询通常为 0，不代表整个任务免费；成功结果优先读取 X-Cost-Token。 |
| _cache.hit | boolean | 本地缓存命中标记。 |
| suggestedNextCheckAfterSeconds | integer | 临时查询失败时通常为 10 秒。 |
| message | string | 给 Agent 的恢复、停止或读取文件提示。 |

#### 脚本内部任务记录字段

| 字段 | 类型 | 说明 |
|---|---|---|
| _asyncTaskRef | string | 原提交参数指向规范化 taskId 记录的引用。 |
| _asyncReceipt | object | 成功领取后的文件回执，不保存评论正文。 |
| _asyncReceipt.taskId | string | 已领取的任务 ID。 |
| _asyncReceipt.status | string | 固定为 SUCCEEDED。 |
| _asyncReceipt.resultFile | string / null | 完整结果文件的绝对路径；保存失败时为空。 |
| _asyncReceipt.receivedAt | number | 本地领取时间，Unix 秒。 |

缓存保存在 `cwd/linkfox/.cache/linkfox-amazon-reviews-list`；终态分别用 `.terminal.json` 和 `.received.json` 保存，读取时优先回执和终态，延迟到达的 RUNNING 或错误写入不覆盖终态。兼容读取临时查询错误缓存时恢复同任务查询；读取完整结果缓存且已知 taskId 时转换为文件回执。不论是否已知 taskId，缓存结果的历史 costToken 在本次输出均置 0。公共调用器保存原始响应失败时，仍交由业务层保存已领取数据；最终落盘失败时强制完整输出，并保留空文件回执，避免自动重抓。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 默认脚本首次执行只提交并立即返回；后续每次执行只查询一次结果，不循环、不休眠，使 Agent 可以继续其他工作。
- 可以用原提交参数再次执行脚本并从缓存恢复任务，也可以直接传入 `{"taskId":"..."}` 查询。
- `PENDING`、`RUNNING`：从任务创建时间起最多观察 `200` 秒；窗口内保留同一个 `taskId`，继续其他工作，约 `10~20` 秒后再查询，不按 `pollAfterMillis` 忙轮询。
- 临时查询失败（网络异常、服务暂时不可用等）保留原任务，在观察窗口内稍后查询同一 `taskId`；不缓存为最终结果、不重新提交。认证/参数错误或明确的任务不存在则停止。
- `SUCCEEDED`：读取 `result` 并结束。
- `FAILED`：读取 `error` 并结束，不自动重新提交。
- `CANCELLED`：任务等待异步执行资源超时，尚未调用供应商。向用户友好说明当前评论服务可能请求较多、任务已自动取消且不计费 （限时），建议稍后重新提交。缓存保留原参数到该终态的关联，重复运行不自动新建任务；只有用户明确要求重试后，才可按提交接口的 `--no-cache` 约定重新提交。
- 未读取任务从提交时间起保留 4 小时；首次读取到任一终态后，后端立即删除该任务。脚本将成功结果保存到文件，缓存仅记录“已领取”和文件路径，不再缓存一份评论正文。
- 原参数与 `taskId` 在同一工作目录内共用任务记录；24h 本地缓存有效期内重复执行返回 `ALREADY_RECEIVED`、`resultFile`、`fileExists` 和本次 `costToken: 0`，不再发起后端查询。`ALREADY_RECEIVED` 是脚本本地状态，不是后端状态。应读取 `resultFile`；文件已丢失则提示用户，不自动重新抓取。
- 超过 `200` 秒仍未完成时返回 `POLL_TIMEOUT` 并停止自动查询。用户可以选择继续查询同一个 `taskId`，或停止查询；不得自动提交新任务。
- 当前没有手动取消端点。后端只自动取消尚未调用供应商的 `PENDING` 任务；停止查询不会取消已进入 `RUNNING` 的上游调用。
- 任务不存在或已过期：结束并提示用户；只有用户明确要求重试时才重新提交。
- 调用前的积分公式只用于预估。后端在上游处理结束后独立结算，与是否领取结果无关；提交和查询响应的 `X-Cost-Token`/`costToken` 为 `0` 只表示本次接口不再扣费。实际消耗以消费记录为准，不得因未领取、查询失败或本地观察超时报告任务免费，也不得由客户端推算或补记费用。

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/amazon/reviews/async/result" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -H "Content-Type: application/json" \
  -d '{
    "taskId": "提交接口返回的任务ID"
  }'
```

---

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-amazon-reviews-list",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
