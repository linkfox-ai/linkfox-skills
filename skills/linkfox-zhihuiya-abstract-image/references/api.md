# 智慧芽专利摘要附图 接口说明

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

## 接口：专利摘要附图

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/zhihuiya/abstractImage`

### 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| patentId | string | 条件必填 | 专利ID。`patentId` 和 `patentNumber` 两个参数必须至少提供一个，如果两个都存在，会优先使用 `patentId`。多个用英文逗号隔开，上限100条。最大长度60000字符。 |
| patentNumber | string | 条件必填 | 公开公告号。`patentId` 和 `patentNumber` 两个参数必须至少提供一个，如果两个都存在，会优先使用 `patentId`。多个用英文逗号隔开，上限100条。最大长度60000字符。 |


#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| JSON 参数 | object | 是 | 第一个位置参数，按上方请求参数传入 JSON。 |
| --inline | CLI flag | 否 | 强制打印完整响应，同时仍保存文件。 |
| --no-cache | CLI flag | 否 | 本次跳过缓存读取和写入；默认使用 24 小时缓存。 |

- 脚本使用标准库，无额外业务依赖。网关地址优先使用 `LINKFOX_TOOL_GATEWAY`，未设置时使用默认正式地址；认证兼容两个密钥环境变量，优先使用 `LINKFOX_AGENT_API_KEY`。
- 脚本使用一层响应缓存，由公共调用器负责。缓存文件为 `<cwd>/linkfox/.cache/linkfox-zhihuiya-abstract-image/linkfox-zhihuiya-abstract-image-<key>.json`，key 为参数按键排序后以 `ensure_ascii=False` 序列化所得 JSON 的 SHA-256 前 16 位。同参缓存可跨进程复用；损坏或超过 24 小时的缓存视为未命中。
- 缓存命中时添加 `_cache.hit=true` 标记。响应（含失败或空结果）也可缓存；不可自动绕过缓存连续试探。
- 会话原始数据、元数据及索引必须落在当前工作目录下的 `linkfox/`，不使用其他工作区、家目录或临时目录回退。请求前检查实际会话的 `data/`、`_meta.json` 和根目录的 `index.jsonl` 是否可写，受阻即报错；禁止写入 `/tmp`。响应文件名使用微秒时间戳，避免同一秒内多次调用覆盖已保存的数据。
- 使用 `SESSION_ID` 聚合会话；请求同时透传 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 请求头，HTTP 超时 150 秒，不自动重试。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| total | integer | 记录数 |
| data | array | 专利摘要附图结果列表；每条对应一条专利摘要附图结果。 |
| data[].patentId | string | 专利ID |
| data[].pn | string | 公开(公告)号 |
| data[].abstractDrawingPath | string | 摘要附图图片下载路径 |
| columns | array | 渲染的列定义 |
| costToken | integer | 消耗token；按返回原值保留，用户算力以网关实际扣费记录为准，不按记录条数自行换算。 |
| type | string | 渲染的样式 |

#### 网关状态与本地标记

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 网关状态码，按公共响应码基本规则判断。认证失败示例为 401。 |
| errmsg | string | 网关消息；如 `authorized error`，根据实际消息解释原因。 |
| errorCode | 未约定 | 辅助排查字段，类型未约定；若响应包含此字段，保留其实际值供排查，不替代公共规则中的 `errcode` 判定。 |
| _cache.hit | boolean | 仅本地缓存命中时添加的标记，不是上游业务字段。 |
| _http_status | integer | 本技能脚本记录的实际 HTTP 状态，不是上游业务字段；缓存命中时为原请求的历史状态，本次没有发起请求。旧缓存可能不含此字段，缺失时不能据此推断 HTTP 成功。 |

`columns` 的元素结构及其他字段的默认值、枚举无固定约定，以实际响应为准。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 某件专利的 `abstractDrawingPath` 为空时，说明该专利没有可用摘要附图，不把缺图解释为整批请求失败。
- 查询失败时保留实际错误消息，提示核对专利标识；不自动修改标识继续查询。
- 脚本输出含 `_http_status` 时，以该状态结合公共响应码规则判断结果；`401` / `402` 即使错误体没有 `errcode` 也按认证或用量错误处理。大响应摘要也展示该状态。旧缓存若缺少状态且错误体不足以判定，说明状态无法确认，不自动绕过缓存重查。

### curl 示例

```bash
curl -X POST https://tool-gateway.linkfox.com/zhihuiya/abstractImage \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"patentNumber": "CN115059423A"}'
```

### 响应示例

认证失败响应示例：

```json
{
  "errcode": 401,
  "errmsg": "authorized error"
}
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-zhihuiya-abstract-image",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```