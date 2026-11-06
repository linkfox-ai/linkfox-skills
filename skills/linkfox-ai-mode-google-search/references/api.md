# Google AI 搜索 接口说明

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

## 接口：Google AI 概览搜索

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/aiMode/googleSearch`

### 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| keyword | string | 是 | Google 搜索关键词，作为 `q=` 参数发起 Google AI Mode 搜索。无已声明默认值；仅支持单轮对话，不支持 `prompts` 追问参数。追问时由 agent 总结上一轮 AI 概览的关键结论、引用与背景，拼接新问题后作为新的 keyword 发起新请求。 |

#### 使用限制

- 每次只处理一个问题，不提供服务端多轮对话上下文。
- 使用 Google 默认 AI Mode 搜索地区，没有显式地区切换参数。可以调整问题的语言和市场措辞，但不能保证实际地区已切换。
- 只返回非结构化 Markdown 文本，不提供结构化商品表或二次数据查询。
- 并非所有关键词都会触发 AI Overview；小众、含糊或敏感主题可能没有概览。
- 未命中本地缓存时实时抓取；相同关键词在不同调用时间可能返回不同结果。

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 默认值与说明 |
|------|------|------|------|
| JSON 参数 | JSON object | 是 | 作为第一个位置参数传入，包含上表字段。 |
| --inline | CLI flag | 否 | 默认关闭；强制全量打印，同时仍保存完整响应。 |
| --no-cache | CLI flag | 否 | 默认关闭；禁用业务脚本的响应缓存读写。公共调用器始终接收此标记，避免与业务缓存重复。 |
| --help / -h | CLI flag | 否 | 仅展示本地帮助，不发送请求。 |

| 环境变量 | 类型 | 必填 | 说明 |
|------|------|------|------|
| LINKFOX_TOOL_GATEWAY | string | 否 | 网关地址覆盖，默认值见公共规则；去除末尾 `/`。 |
| LINKFOX_AGENT_API_KEY | string | 与旧变量二选一 | 优先使用的认证密钥；作为原值放入 Authorization，不添加 Bearer 前缀。 |
| LINKFOXAGENT_API_KEY | string | 与新变量二选一 | 兼容旧认证变量；新变量为空时使用。 |
| SESSION_ID | string | 否 | 用于请求头和本地会话聚合；未配置时本地会话按 `HHMMSS-<6 hex>` 生成，并在同一进程内保持稳定。 |
| MESSAGE_ID / MODE_ID / APP_NAME | string | 否 | 原样透传为同名请求头；未设置时为空字符串。 |

业务脚本提供 24 小时本地缓存：路径为 `<cwd>/linkfox/.cache/linkfox-ai-mode-google-search/linkfox-ai-mode-google-search-<hash>.json`，其中 `<hash>` 是参数按键排序、保留 Unicode 后序列化的 SHA-256 前 16 位。相同参数的键顺序不影响命中；超过 24 小时、JSON 或 UTF-8 编码损坏时重新请求；仅 `_cache` 元信息格式异常时修复命中标记并复用已保存的响应。响应对象包括空结果和错误响应均可能被缓存；不自动重试。

缓存命中也将完整响应保存到本次会话的数据文件，增加 `_cache.hit=true` 标记并提示缓存路径。`--no-cache` 不创建缓存目录，也不读取或写入响应缓存。底层调用 `call_api.run` 时固定传入 `--inline --no-cache`，由业务封装跳过公共调用器的缓存路径创建，只负责一次请求和落盘；最终摘要由业务封装输出，不形成第二层响应缓存。

业务数据固定保存到当前工作目录的 `linkfox/<YYYY-MM-DD>/<session>/data/`，维护 `_meta.json` 与 `index.jsonl`，用于聚合同一任务的会话数据。当前目录不可写时请求前报错，不回退到家目录、`ACPX_WORKSPACES` 或临时目录；不写 `/tmp`。文件使用 UTF-8；阈值为 8000 字节（文档简称 8 KB），超过阈值输出摘要，摘要中的最大列表最多展示前 3 条样本。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| stdout | string | AI 概览正文，Markdown 格式；逐段展示本次问题的概览要点与参考来源链接。 |
| sourceUrl | string | 抓取目标 URL，最终发往 Google 的搜索页地址。 |
| resultsNum | integer | AI 概览块数量；大于 0 表示页面渲染了 AI Overview，0 表示该关键词未触发概览。 |
| code | string | 业务状态码；成功值为 `"200"`，与 errcode 的成功数值对应；用于辅助说明，基础判断遵循公共规则。 |
| errcode | integer | 业务状态码；成功值为 `200`。HTTP 层通常为 200，但不能仅据 HTTP 状态判断业务成功；基础判断遵循公共规则。 |
| msg | string | 响应消息，成功为 `ok`。 |
| errmsg | string | 响应或错误消息，成功为 `ok`，错误时为原因描述。 |
| costTime | integer | 接口耗时，单位毫秒。 |
| costToken | integer | 本次调用消耗 Token 数；上游返回成功才计费。 |
| taskId | string | 上游返回的本次抓取任务标识，用于追溯。 |
| type | string | 渲染样式，固定 `stdoutWorkbenches`，配合 stdout 以 Markdown 渲染。 |

#### 脚本附加字段

| 字段 | 类型 | 说明 |
|------|------|------|
| _cache | object | 本地缓存命中时添加的元信息，不是服务端业务字段。 |
| _cache.hit | boolean | 命中时为 true。 |
| error | string | 公共调用器遇到连接错误或无法解析的 HTTP 错误时提供的本地错误描述，不替代服务端 errcode。 |
| details | string | 无法解析为 JSON 的 HTTP 错误响应正文（如有）。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- `resultsNum=0` 表示当前关键词没有触发概览；应依据该字段解释空概览，不能因请求正常返回就宣称取得了正文。建议改写问题或调整市场语言；本接口没有显式地区开关。
- 错误描述优先保留 `errmsg`，并兼容 `msg`；`authorized error` 等认证错误按 [认证与算力引导](onboarding.md) 处理。未授权情形可能同时为 HTTP 401 与 errcode 401。
- 出现本地 `error` 字段时，说明请求未取得可用业务响应；保留错误与 details，不作为成功概览展示，不自动请求重试。
- 响应或归档文件不是有效 UTF-8 JSON 时，业务脚本报错并退出，不自动重试；不能将该情形解释为空概览。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/aiMode/googleSearch" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"keyword": "best wireless earbuds 2026"}'
```

### 响应示例

成功响应节选：

```json
{
  "msg": "ok",
  "sourceUrl": "https://www.google.com/search?num=10&udm=50&q=best+wireless+earbuds+2026",
  "errcode": 200,
  "code": "200",
  "stdout": "# Google AI Mode 概览 - best wireless earbuds 2026\n\n## AI 概览要点\n- ...\n",
  "costTime": 10799,
  "costToken": 11200,
  "resultsNum": 1,
  "type": "stdoutWorkbenches",
  "taskId": "1779367311421-d728ce53704fc86e"
}
```

认证错误示例：

```json
{"errcode": 401, "errmsg": "authorized error"}
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-ai-mode-google-search",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```

