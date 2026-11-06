# 网页搜索与在线信息检索 接口说明

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

## 接口：网页搜索

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/tsearch/search`

### 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| keyword | string | 是 | 搜索关键词，最大长度 1000 字符；每次仅传一个字符串，无默认值。 |

#### 使用限制

- 每次调用只接收一个 `keyword` 字符串；多角度调研需使用不同关键词分别调用，继续检索遵守 SKILL.md 成本约束。

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| JSON 参数 | object | 是 | `python scripts/tsearch_web_search.py '<JSON 参数>' [--inline] [--no-cache]`；参数原样传入上述接口。 |
| --inline | CLI flag | 否 | 默认关闭；强制完整打印，仍保存完整响应。 |
| --no-cache | CLI flag | 否 | 默认关闭；跳过读取和写入响应缓存。对时效要求高且用户已知额外消耗时，可显式刷新。 |

- 脚本提供 24 小时本地缓存，由 `scripts/call_api.py` 的 `run` 统一管理；业务入口不额外建立缓存层。
- 缓存位置为 `<cwd>/linkfox/.cache/linkfox-tsearch-search/linkfox-tsearch-search-<参数哈希>.json`。参数按键排序后以 `ensure_ascii=False` 序列化，取 SHA-256 前 16 位；有效期依据文件修改时间，命中时添加 `_cache.hit=true`。过期或无法解析时重新请求。错误及空响应也可能被缓存，不应据此自动重试。
- 支持通过 `LINKFOX_TOOL_GATEWAY` 自定义网关，并去除网关地址尾部的 `/`；密钥优先读取 `LINKFOX_AGENT_API_KEY`，其次读取 `LINKFOXAGENT_API_KEY`。两者均为空时在发请求前输出错误并以 1 退出。
- 请求额外透传 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 请求头，未配置时为空字符串；仅发一次请求，不自动重试。
- 完整响应落盘并维护会话 `_meta.json` 和 `linkfox/index.jsonl`；会话优先使用 `SESSION_ID`，否则在进程内生成稳定标识。输出阈值为序列化后的 8000 个 UTF-8 字节，大响应摘要包含最大列表的前 3 条样本。
- 输出根目录优先选择 `ACPX_WORKSPACES` 第一个路径下可写的 `linkfox/`，其次选择当前目录下的 `linkfox/`；响应缓存仍固定在当前目录。业务入口在请求前检查输出根目录、会话 `data/` 目录以及与响应文件名等长的 JSON 文件可创建；无法在工作区或当前目录保存时，以 1 退出，不发请求，不回退到用户目录或系统临时目录，也不写入 `/tmp`。输出目录预检不增加响应缓存层。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| searchList | array | 搜索结果列表，元素结构见下列嵌套字段。 |
| searchList[].score | number | 结果相关性分数，例如 0.95。 |
| searchList[].title | string | 结果的页面标题。 |
| searchList[].url | string | 结果的来源页面链接。 |
| searchList[].content | string | 已提取的页面正文；为非结构化文本。 |
| costToken | integer | 本次请求消耗的 token 数，例如 1500；不将其等同于算力金额。 |
| errcode | integer / string / null | 网关业务状态码，按公共规则判断；认证错误示例为 401。 |
| errmsg | string | 网关错误消息；认证失败示例为 `authorized error`。 |
| errorCode | integer / string | 若响应包含此业务状态字段，200 表示成功，其他值表示业务错误；同时按公共规则检查 `errcode`。 |

#### 脚本本地输出字段

| 字段 | 类型 | 说明 |
|------|------|------|
| _cache | object | 仅本地缓存命中时追加的元信息，不是接口字段。 |
| _cache.hit | boolean | 命中缓存时为 true。 |
| error | string | 非 JSON HTTP 错误或连接错误时，由公共调用器返回的错误说明。 |
| details | string | HTTP 错误响应无法解析为 JSON 时保留的原始响应内容。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 响应包含 `errorCode` 且其值不是 `200`（数字或数字字符串）时，按业务错误处理，结合错误消息说明原因；不能仅因 `errcode` 缺失或为成功值而将其作为成功搜索材料。`errorCode` 为 `401` / `402` 时，按 SKILL.md 的认证和算力问题指引处理。
- `searchList` 为空或正文不相关时，应解释为未取得合适的搜索材料，建议细化关键词；不因空列表直接认定接口失败。
- 脚本错误输出：HTTP 错误正文可解析为 JSON 时原样返回；否则保留 `error` 和可能的 `details`。连接失败返回 `error`。错误正文缺少状态信息时，不得把缺少 `errcode` 当作已经取得搜索结果；依据错误消息处理。

### 响应示例

`searchList` 中单个元素：

```json
{
  "score": 0.95,
  "title": "页面标题",
  "url": "https://example.com/article",
  "content": "提取的页面正文内容..."
}
```

认证错误：

```json
{
  "errcode": 401,
  "errmsg": "authorized error"
}
```

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/tsearch/search" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"keyword": "best wireless chargers 2026 review"}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-tsearch-search",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```