# 智慧芽专利被引查询 接口说明

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

## 接口：专利被引查询

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/zhihuiya/patentCited`

### 请求参数

请求体为 JSON 对象。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| patentId | string | 条件必填 | 智慧芽内部专利 ID。多个用英文逗号分隔，上限 100 条，最大长度 60000 字符。与 `patentNumber` 至少提供一个；两者同时存在时优先使用 `patentId`。用户提供内部 ID 时使用此字段。 |
| patentNumber | string | 条件必填 | 公开公告号。多个用英文逗号分隔，上限 100 条，最大长度 60000 字符。与 `patentId` 至少提供一个；用户提供公开公告号（如 `US10123456B2`）时使用此字段。 |

#### 脚本选项与运行约定

| 参数 / 约定 | 类型 | 必填 | 说明 |
|------|------|------|------|
| JSON 参数 | CLI 位置参数 | 是 | `python scripts/zhihuiya_cited_by.py '<JSON 参数>' [--inline] [--no-cache]`；业务字段见上表。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 仅本次禁用响应缓存读写；默认启用 24 小时本地缓存。 |
| LINKFOX_TOOL_GATEWAY | 环境变量 | 否 | 网关基础地址覆盖项，去掉末尾 `/` 后拼接本接口路径。 |
| SESSION_ID | 环境变量 | 否 | 聚合同一任务数据；未提供时生成进程内稳定的会话标识。 |
| MESSAGE_ID / MODE_ID / APP_NAME | 环境变量 | 否 | 通过同名请求头透传。 |
| Accept | 请求头 | 否 | 业务脚本设置 `Accept: application/json` 响应协商，由公共调用器执行请求。 |
| 缓存 | 本地文件 | 否 | 缓存路径为 `<cwd>/linkfox/.cache/linkfox-zhihuiya-patent-cited/`，缓存键为参数 JSON 按键排序后计算的 SHA-256 前 16 位；以文件修改时间判断 24 小时有效期。由通用调用器独立管理，不叠加第二层缓存。缓存命中时标注 `_cache.hit=true`，仍保存本次完整响应。 |
| 保存目录 | 本地目录 | 是 | 完整响应写入当前工作目录的 `linkfox/<YYYY-MM-DD>/<session>/data/`，不回退到家目录或临时目录；不可写时在请求前报错。 |

同一会话、同一参数组合默认只调用一次。失败或空结果时不得自动更换参数或连续试探；继续查询前说明额外消耗。缓存会保存返回结果，包含失败或空结果；重新请求时需明确使用 `--no-cache`，遵守已有授权范围和成本约束。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| total | integer | 记录数。 |
| data | array | 专利被引结果列表，元素字段见下表。 |
| columns | array | 渲染的列定义，元素结构以实际返回为准。 |
| costToken | integer | 消耗 Token 数量，不直接等同于用户算力；本接口按 SKILL.md 的固定费用预估。 |
| type | string | 渲染样式。 |
| errcode | integer / string / null | 网关业务状态码，按公共规则判断；错误示例为 401。 |
| errmsg | string | 网关消息或错误原因，认证错误示例为 `authorized error`。 |
| errorCode | integer | 业务状态码兼容字段，200 表示业务成功，其他值表示业务错误，401 表示未授权。若实际返回则按业务规则判断，不以此替换公共规则中的 `errcode` 判断。 |

#### data 数组元素字段

| 字段 | 类型 | 说明 |
|------|------|------|
| patentId | string | 专利 ID。 |
| pn | string | 公开（公告）号。 |
| citedBy3y | integer | 公开后三年内被引用次数。 |
| citedBy5y | integer | 公开后五年内被引用次数。 |
| citedBySimpleFamily | integer | 简单同族被引专利数量。 |
| citedByInpadocFamily | integer | INPADOC 同族被引专利数量。 |
| citedByPatsnapFamily | integer | PatSnap 同族被引专利数量。 |
| citedByPatents | array | 引用当前专利的专利列表，即前向被引详情；元素字段以实际返回内容为准。 |

#### 脚本本地附加字段

| 字段 | 类型 | 说明 |
|------|------|------|
| _http_status | integer | 业务脚本记录的实际 HTTP 状态码，不是网关响应体字段。HTTP 错误返回 JSON 时仍保留该状态及原错误体。连接失败未收到 HTTP 响应时不生成该字段。 |

缓存命中时，`_http_status` 为生成该缓存的请求状态，不代表本次发起了 HTTP 请求。缓存不含此字段时，不从 `errcode` 或 `errorCode` 反推 HTTP 状态；结合实际返回的业务码、消息判断。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 响应包含 `errorCode` 时，200 表示业务成功，其他值表示业务错误；即使 HTTP 为 200，也需检查此字段。此判断与公共规则中的 HTTP 状态及 `errcode` 判断同时适用。
- HTTP 状态或响应业务码为 401、402，或消息提示认证、算力问题时，按 `onboarding.md` 的指引处理。
- 其他业务异常依据 `errmsg` 说明原因，核对公开公告号或内部标识，遵守本接口的成本与重试约束。

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/zhihuiya/patentCited" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"patentNumber": "US10123456B2,CN112345678A"}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-zhihuiya-patent-cited",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```