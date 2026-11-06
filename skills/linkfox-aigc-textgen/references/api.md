# AI 生文 接口说明

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

## 接口：创建生文任务（textGenAsync）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/aigc/textGenAsync`

### 请求参数

| 参数 | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| prompt | string | 是 | - | 提示词，描述需要生成的内容（最大10万字符） |
| imageUrls | array[string] | 是 | [] | 媒体 URL 列表（图片或视频）。纯文本时传 `[]`；图片最多10张；视频分析通常传1个视频 URL |
| model | string | 否 | GEM_3_FLASH | 模型枚举值：`GEM_3_FLASH`(快速响应) / `GEM_3_1_PRO`(高质量复杂分析) |
| thinkingLevel | string | 是 | minimal | 思考等级：`minimal` / `low` / `medium` / `high`（GEM_3_1_PRO 不支持 minimal） |
| memberId | string | 否 | - | 用户成员ID，用于任务记录关联 |

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| `taskId` | string | 异步任务ID，用于后续轮询 |

响应示例：`{"taskId":"123456789"}`。脚本兼容以下实际包裹和错误字段，不要求服务端补齐未返回字段。

| 字段 | 类型 | 说明 |
|---|---|---|
| data / result | object | 可选任务对象包裹；内部 `taskId` 同上。 |
| errcode / errorCode / code | integer / string / null | 可选业务状态字段，按响应码规则判断。 |
| errmsg | string | 业务消息；发生异常时保留。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 创建成功须取得非空 `taskId`；兼容顶层及 `data.taskId` / `result.taskId`。缺少任务标识不能进入轮询。
- `errorCode` / `code` 使用与 `errcode` 相同的判断规则；保留服务端原始错误字段。
- 创建不自动重试；连接超时也可能已成功创建，不能盲目重发。先保留已知任务标识，按已有任务查询。

#### 参数与使用限制

- `prompt`、`imageUrls`、`thinkingLevel` 必须显式传入；表中 `thinkingLevel` 的 `minimal` 为建议值，脚本不代填必填字段。`model` 不传由接口采用 `GEM_3_FLASH`。
- `imageUrls` 接收图片或视频 URL，不接受本地路径。纯文本用 `[]`；本地媒体先按 [file-upload.md](file-upload.md) 上传，已有公开 HTTP(S) URL 直接使用，保留顺序；上传失败不创建任务。
- `imageUrls` 最多 10 个 URL；视频通常只传 1 个，不建议混传图片和视频。禁止自行新增 `videoUrl` / `videoUrls` 字段。
- `prompt` 最大 10 万字符。`GEM_3_1_PRO` 不支持 `minimal`；快速场景选 `minimal` / `low`，深度推理选 `high`，复杂视频分析建议 `GEM_3_1_PRO` 配 `low`。
- 已确认失败最多重试 3 次，创建重试须先排除重复任务且遵守成本约束；脚本不会自动重建任务。视频不可读、媒体访问失败、`10005` 或空内容时，可按业务场景抽帧成图片后再分析；额外调用先说明消耗，不无条件重试。
- 创建封装对公共 runner 始终传 `--no-cache`，不复用响应缓存。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/aigc/textGenAsync" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"prompt":"为无线音箱写商品描述","imageUrls":[],"model":"GEM_3_FLASH","thinkingLevel":"minimal"}'
```

## 接口：查询生文任务（textTaskQuery）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/aigc/textTaskQuery`

### 请求参数

| 参数 | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| taskId | string | 是 | - | 创建任务时返回的任务ID |
| memberId | string | 否 | - | 用户成员ID，用于任务记录关联 |

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| `taskId` | string | 任务ID |
| `status` | string | 任务状态：`PROCESSING`(处理中) / `SUCCESS`(成功) / `FAILED`(失败) |
| `content` | string | 生成的文本内容（仅 SUCCESS 时有值） |
| `promptTokens` | integer | 输入 token 数量（仅 SUCCESS 时有值） |
| `completionTokens` | integer | 输出 token 数量（仅 SUCCESS 时有值） |
| `totalTokens` | integer | 总 token 数量（仅 SUCCESS 时有值） |
| `errorMsg` | string | 错误信息（仅 FAILED 时有值） |

| 字段 | 类型 | 说明 |
|---|---|---|
| data / result | object | 可选业务包裹，包含上表任务、状态、文本及 token 字段。 |
| errcode / errorCode / code | integer / string / null | 可选业务状态字段，按响应码规则判断。 |
| errmsg | string | 业务消息；失败时保留。 |

### 响应示例

```json
{"taskId":"123456789","status":"SUCCESS","content":"生成的文本","promptTokens":120,"completionTokens":350,"totalTokens":470}
```

处理中为 `{"taskId":"123456789","status":"PROCESSING"}`；失败为 `{"taskId":"123456789","status":"FAILED","errorMsg":"生成失败"}`。

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- `PROCESSING` 表示继续查询同一任务；`SUCCESS` 才能交付文本；`FAILED` 或兼容值 `4` 表示业务失败，保留 `errorMsg`、`errmsg` 和任务标识，不自动重建。
- `10009` 表示任务不存在，核对 `taskId`；其他业务异常依据 `errmsg`。兼容 `errorCode` / `code` 业务码和顶层、`data`、`result` 包裹，保留原字段。
- 单次 HTTP 超时 150 秒；轮询从 10 秒开始，每次减 1 秒，最低 5 秒；轮询预算 600 秒，已在途请求另受单次 HTTP 超时约束。超时结果保留 `taskId`，可恢复查询。
- 网络错误或 HTTP 408 / 429 / 500 / 502 / 503 / 504 最多额外重试 3 次；认证、算力、明确业务失败立即停止；查询错误不触发创建。
- 本地保存或响应解析错误立即停止，不因本地失败再次查询；超时和连接故障属于传输错误，可在上述上限内查询同一任务。
- 状态查询始终 `--no-cache`，不得缓存 `PROCESSING` 后反复读取旧状态。`SUCCESS` 的空文本按失败退出并保留原响应，供媒体排查。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/aigc/textTaskQuery" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"taskId":"123456789"}'
```

## 脚本 CLI 与输出契约

| 调用方式 | 行为 |
|---|---|
| `python scripts/aigc_textgen.py --stdin` | 推荐；从 stdin 读取 JSON，避免多行提示词的 shell 转义问题。PowerShell 可用 `Get-Content -Raw -Encoding UTF8 params.json` 管道输入。 |
| `python scripts/aigc_textgen.py '<JSON>' [--inline]` | 简单参数可直传；prompt 含真实换行时禁用此传法，使用 stdin。 |
| `python scripts/aigc_textgen.py --stdin --content-only` | 只输出单行 content，供下游组合；失败无文本 stdout，错误写 stderr。 |
| JSON 仅传 `taskId` 和可选 `memberId` | 恢复查询入口；只轮询已有任务，不再创建。 |
| `--no-cache` | 可显式传入；封装无论是否传此选项都禁用公共响应缓存。 |

所有响应始终保存到当前目录的 `linkfox/<YYYY-MM-DD>/<session>/data/`，接口原始响应分别使用 `linkfox-aigc-textgen-create-` / `linkfox-aigc-textgen-query-` 文件名前缀；最终输出使用 `linkfox-aigc-textgen-`。同秒请求采用微秒文件名避免覆盖，`SESSION_ID` 优先，未设置时同一进程内的原始响应、最终输出和上传记录共用稳定会话标识，登记 `_meta.json` 和 `index.jsonl`。跨进程聚合时应显式设置相同的 `SESSION_ID`。保存失败非零退出，不回退到 `/tmp`。

| 输出字段或模式 | 类型 | 说明 |
|---|---|---|
| 默认小结果 / `--inline` | object | 完整 JSON；阈值为 UTF-8 序列化后 8000 字节。 |
| ok | boolean | 仅大结果信封：本次是否成功。 |
| truncated | boolean | 大结果信封固定为 true；完整对象按 savedPath 读取。 |
| savedPath | string | 大结果信封：完整 JSON 的本地路径。 |
| bytes | integer | 大结果信封：完整 JSON 的 UTF-8 字节数。 |
| content | string / null | 大结果信封始终携带完整单行文本，避免链式文本被截断；无文本时为 null。 |
| transportHttpStatus | integer / null | 仅 HTTP 非 2xx 或连接失败时附加，避免 HTTP 错误被正文伪装为成功。 |
| error | string | 网络、本地保存或空结果等错误说明，出现即失败。 |
| localError | boolean | 为 true 时表示本地保存、解析等失败，立即停止，不据此重试接口。 |
| `--content-only` | string | stdout 为纯文本单行 content，例外于 JSON 输出契约。 |

所有 CHAIN-HINT、保存提示、摘要及诊断只写 stderr。成功退出 0；网络错误、HTTP 或业务异常、任务失败、保存失败、成功但内容为空均非 0。agent 优先判断退出码；小结果 `json.loads(stdout)`，大结果读信封 content 或使用 `jq` / `ConvertFrom-Json` 按 savedPath 提取字段。

### 换行占位符与下游参数

脚本在所有模式把 content 的真实 CRLF / CR / LF，以及字面量 `\r\n` / `\n` / `\r` 编码为单字符 `⏎`（U+23CE），输入也递归解码占位符。下游 imagegen / videogen / videogen-multi 的 `decode_nl_in_obj` 会还原换行。占位符自身无需 JSON 转义，但其他引号、反斜杠仍需 JSON 编码器。

```bash
PROMPT=$(python scripts/aigc_textgen.py --stdin --content-only < textgen_params.json)
PARAMS=$(jq -nc --arg p "$PROMPT" '{prompt:$p,imageUrls:["https://example.com/ref.jpg"],provider:"BANANA_PRO",outputNum:1,resolution:"1K",aspectRatio:"1:1"}')
# 将 PARAMS 交给用户已要求的下游 AIGC 技能；脚本位于该技能自身目录。
```

没有 jq 时使用 Python `json.dumps`，不手工拼接。各下游字段参考如下；实际支持值由下游技能定义。

| 下游技能 | 参数参考（prompt 使用上游文本） |
|---|---|
| linkfox-aigc-imagegen | `imageUrls`、`provider: BANANA_PRO`、`outputNum: 1`、`resolution: 1K`、`aspectRatio: 1:1` |
| linkfox-aigc-videogen | `imageUrls`、`model: WAN2_1`、`outputNum: 1`、`resolution: 720P`、`duration: 5` |
| linkfox-aigc-imagegen-cloth | `imageUrls`、`outputNum: 1`、`aspectRatio: 1:1` |
| linkfox-aigc-imagegen-product | `imageUrls`、`outputNum: 1`、`aspectRatio: 1:1` |

---

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-aigc-textgen",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
