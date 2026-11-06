# 智慧芽专利引用查询 接口说明

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

## 接口：查询专利引用（patentForwardCitation）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/zhihuiya/patentForwardCitation`

### 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| patentId | string | 条件必填 | 专利ID（专利ID和公开号两个参数必须要有一个，如果两个都存在，会优先使用专利ID）。多个用英文逗号隔开，上限100条。最大长度60000字符。 |
| patentNumber | string | 条件必填 | 公开公告号（专利ID和公开号两个参数必须要有一个，如果两个都存在，会优先使用专利ID）。多个用英文逗号隔开，上限100条。最大长度60000字符。 |

- 每次请求至少需要提供 `patentId` 或 `patentNumber` 其中之一

两项均无默认值；未使用的标识可省略。不改写用户提供的标识；超过单次上限时，先说明额外消耗并由用户决定是否拆分，不自动连续调用。

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 默认值 / 说明 |
|------|------|------|------|
| JSON 参数 | object | 是 | 命令行首个位置参数，字段同上方 POST Body。 |
| --inline | CLI flag | 否 | 默认关闭；强制全量打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 默认关闭；跳过响应缓存的读取和写入。 |

- 脚本入口为 `scripts/zhihuiya_cited_references.py`；由它调用公共 `scripts/call_api.py` 的 `run`，不另设 HTTP transport 或第二层响应缓存。
- 唯一响应缓存有效期 24 小时，路径为 `<cwd>/linkfox/.cache/linkfox-zhihuiya-patent-forward-citation/linkfox-zhihuiya-patent-forward-citation-<hash>.json`。`<hash>` 为对参数排序后的 JSON 求 SHA-256 并取前 16 位。缓存命中会在输出添加 `_cache.hit=true`，不再次请求；空结果或错误也可能被缓存，判断仍按响应码规则。
- 环境变量：`LINKFOX_TOOL_GATEWAY` 覆盖默认网关，`LINKFOX_AGENT_API_KEY` 优先于兼容变量 `LINKFOXAGENT_API_KEY`。公共调用器透传 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 请求头。
- 完整 JSON 必须以 UTF-8 保存在当前工作目录的会话数据目录，并维护 `_meta.json` 与 `index.jsonl`；`SESSION_ID` 未设置时自动生成进程内稳定的会话标识。业务入口在请求前检查当前目录和实际会话 `data` 目录可写；目录被同名文件占用或不可写时，以退出码 1 停止，不调用接口。禁止将数据保存到 `/tmp`，不使用公共调用器向其他工作区、家目录或临时目录回退的行为。
- 脚本通过公共调用器使用 8000 字节的输出阈值，文档简称 8 KB；大响应展示顶层字段、常见计数、最大列表长度及前 3 条样本，`--inline` 可强制完整输出。无参数或 JSON 格式错误时退出码为 1。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| total | integer | 记录数 |
| data | array | 专利列表，每个元素包含引用详情 |
| data[].patentId | string | 查询专利的专利ID |
| data[].pn | string | 查询专利的公开（公告）号 |
| data[].citedPatents | array | 引用专利列表 |
| data[].citedOthers | array | 引用非专利文献列表 |
| columns | array | 渲染的列定义 |
| costToken | integer | 消耗token |
| type | string | 渲染的样式 |

#### 状态及本地标记

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 网关业务状态码，判定以公共规则为准；错误示例使用此字段。 |
| errmsg | string | 网关错误原因，例如 `authorized error`。 |
| errorCode | 未统一定义 | 此字段如有返回，保留其实际值；状态判定使用 `errcode` 的公共判断规则，不据 `errorCode` 单独认定成功。 |
| _cache.hit | boolean | 本地缓存命中标记，由脚本添加，不属于服务端字段。 |
| _http_status | integer | 业务入口在发生 HTTP 错误时保存的实际状态码；不覆盖正文 `errcode`，不属于服务端字段。缓存命中时代表产生该缓存的历史请求状态。 |
| _response | 任意 JSON 值 | 仅 HTTP 错误正文解析为非对象时使用，保留完整的解析结果；对象正文的字段保持原位。 |

`citedPatents`、`citedOthers` 和 `columns` 元素的内部字段、默认值或枚举按实际返回处理；保留原始嵌套对象，不补造结构。`total` 是响应记录数，不等于两类引用文献的合计数。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 本接口无额外业务状态码约定。查询正常返回空列表或确认无引用时，说明没有返回引用文献；字段缺失与明确空列表应分别说明，不自动扩大查询范围。
- 脚本返回 `_http_status` 时，先按其实际 HTTP 状态判定错误，即使正文 `errcode` 缺失或为成功值也不能认定成功；`401` / `402` 按认证和算力指引处理，`403` 为无权限。缓存中的状态是历史状态，不代表发起了新请求；旧缓存没有该字段时不能从正文推断实际 HTTP 状态。
- 本地 `error` / `details` 保存连接失败、空错误正文或非 JSON 错误正文的原因；出现这些错误时应说明失败，不能将缺少 `errcode` 当作成功，不自动重试。
- 错误消息示例为 `{"errcode":401,"errmsg":"authorized error"}`；仅作为消息识别示例，状态判定遵守基础规则。

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/zhihuiya/patentForwardCitation" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"patentNumber": "US10000000B2"}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-zhihuiya-patent-forward-citation",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```