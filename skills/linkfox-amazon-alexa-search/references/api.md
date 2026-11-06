# 亚马逊 Alexa 购物助手 接口说明

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

## 接口：Alexa 购物问答（alexaSearch）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/amazon/alexaSearch`

### 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| prompts | string[] | 是 | 长度在255个字符以内。对话提示词数组，仅支持 **1 条**。每次调用只能传入 1 个问题。如需追问，agent 须自行总结上一轮回答的关键信息（推荐商品、ASIN、关键结论等），拼接新问题后作为新的 `prompts[0]` 发起新请求。每次调用是独立的新会话，不保留跨次调用的历史上下文 |
| format | string | 否 | 响应格式，`markdown`（默认）返回可读报告；`json` 返回结构化数据数组 |
| url | string | 否 | 联动页面 URL，用于补充 Alexa 当前答复的页面上下文。仅在用户提供了**具体页面**（分类页 / 搜索结果页 / 商品详情页等）时才传入；没有具体页面时省略，不传亚马逊首页（如 `https://www.amazon.com/`），首页不提供有用的页面上下文 |

#### 使用限制与脚本约定

- 主要基于 amazon.com 的 Alexa 前台体验；非美国站可用性取决于 Alexa 的上线情况。
- Alexa 回答随时间、流量及上下文变化，不保证同一输入得到相同结果；精选商品不能替代完整 SERP 提取，也不适合作为扁平数据表进行 SQL 式聚合。

| 脚本参数 / 约定 | 类型 | 默认值 | 说明 |
|------|------|------|------|
| JSON 参数 | object | 无 | 第一个位置参数，传递上述请求体。 |
| --inline | CLI flag | 关闭 | 强制全量打印，仍保存完整响应。 |
| --no-cache | CLI flag | 关闭 | 禁用缓存读取与写入，直接请求。 |
| 响应缓存 | 本地 JSON 文件 | 24 小时 | 仅公共调用器维护一套缓存；键为请求参数排序 JSON 的 SHA-256 前 16 位，缓存目录为 `<cwd>/linkfox/.cache/linkfox-amazon-alexa-search/`，可读取该目录内已有缓存文件。命中时标记 `_cache.hit=true` 并提示；响应（包括错误或空结果）也会进入缓存，过期或损坏时重新请求。 |
| 输出目录 | 本地路径 | 当前工作目录 | 业务脚本在请求前检查 `<cwd>/linkfox` 是否可写，失败则报错退出，不回退至家目录、临时目录或 `ACPX_WORKSPACES`；输出按 `SESSION_ID` 聚合，未设置时自动生成。文件名使用微秒时间，遇到已有文件时递增，避免同秒执行覆盖完整响应。 |
| 运行环境 | 环境变量 | 按公共规则 | 优先使用 `LINKFOX_AGENT_API_KEY`，兼容 `LINKFOXAGENT_API_KEY`；`LINKFOX_TOOL_GATEWAY` 支持自定义地址并去掉末尾斜杠。透传 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 请求头。 |

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| stdout | string | Markdown 格式问答报告，包含每一轮的用户问题、Alexa 回答、推荐商品、可继续追问的问题；仅 `format=markdown` 时返回 |
| data | array | 结构化对话结果数组；仅 `format=json` 时返回 |
| resultsNum | integer | Alexa 实际答复的对话轮次数量；为 0 表示未产生有效回答 |
| code | string | 业务状态码；成功示例为 `"200"`，为 `errcode` 的字符串表示，正常响应判断遵循公共规则 |
| errcode | integer | 业务状态码（HTTP 层一般为 200，业务成功与否以此字段为准） |
| msg | string | 响应消息，成功为 `ok` |
| errmsg | string | 响应消息，成功为 `ok`；异常时保留原因 |
| costTime | integer | 接口耗时，单位毫秒 |
| costToken | integer | 本次调用消耗 Token 数；上游成功才计费 |
| taskId | string | 上游返回的本次任务标识 |
| type | string | 渲染样式：`stdoutWorkbenches`（markdown）或 `json` |

#### `data[*]` 结构（`format=json`）

| 字段 | 类型 | 说明 |
|------|------|------|
| prompt | string | 当前轮次发送给 Alexa 的提示词 |
| content | string | Alexa 本轮回答的文本内容 |
| screenshot | string | 本轮对话截图链接 |
| followUpQuestions | string[] | Alexa 推荐继续追问的问题列表 |
| products | array | 推荐商品分组列表，每个分组包含 `title` 和 `items` |
| products[].items | array | 当前分组中的推荐商品列表 |
| products[].title | string | 推荐分组标题 |
| products[].items[].asin | string | 商品 ASIN |
| products[].items[].title | string | 商品标题 |
| products[].items[].url | string | 商品详情页 URL |
| products[].items[].cover | string | 商品封面图 URL |
| products[].items[].price | string | 现价（带币种） |
| products[].items[].originalPrice | string | 原价或划线价 |
| products[].items[].score | string | 评分 |
| products[].items[].ratingsCount | string | 评价数量 |
| products[].items[].describe | string | 商品简介 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 正常响应后，`resultsNum=0` 或结构化格式下 `data` 为空，表示 Alexa 未产生可用答复；可建议改写问题或结合具体页面，不能将空结果当成推荐成功，也不得自动连续请求。
- `format=markdown` 读取 `stdout`；`format=json` 读取 `data`，不能因 Markdown 响应没有 `data` 就判为空结果。

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/amazon/alexaSearch" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"prompts": ["best electric kettle on Amazon US"], "format": "json"}'
```

### 响应示例

```json
{
  "msg": "ok",
  "errcode": 200,
  "code": "200",
  "stdout": "# 亚马逊 Alexa 购物助手\n\n## 问题 1：best wireless earbuds for running\n\n### Alexa 回答\n- ...\n\n### 推荐商品\n- ...\n\n### 可继续追问的问题\n- ...\n",
  "resultsNum": 1,
  "costTime": 12000,
  "costToken": 1500,
  "type": "stdoutWorkbenches",
  "taskId": "1779367311421-d728ce53704fc86e"
}
```

---

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-amazon-alexa-search",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
