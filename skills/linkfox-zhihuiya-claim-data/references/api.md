# 智慧芽专利权利要求查询 接口说明

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

## 接口：专利权利要求查询

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/zhihuiya/claimData`

### 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| patentId | string | 否，二选一至少提供一个 | 智慧芽内部专利 ID，通常来自先前的智慧芽检索结果。多个用英文逗号分隔，上限 100 条，最大长度 60000 字符；与 `patentNumber` 同时提供时优先使用本字段。示例：`98a1b2c3-xxxx-xxxx-xxxx-xxxxxxxxxxxx`。 |
| patentNumber | string | 否，二选一至少提供一个 | 专利公开或公告号，用户提供公开公告号时使用。多个用英文逗号分隔，上限 100 条，最大长度 60000 字符。示例：`CN115000000A`、`US11234567B2`。 |
| replaceByRelated | string | 否 | 目标专利权利要求无法获取时，是否使用同族专利权利要求替代：`1` 是，`0` 否（默认）；最大长度 1000 字符。 |

#### 参数与使用限制

- 并非所有专利都有可用的权利要求数据；用户选择启用 `replaceByRelated` 时可尝试同族替代，但不保证存在可用替代文本。

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| JSON 参数 | JSON object | 是 | 命令行第一个位置参数，字段定义见上表；CLI 入口为 `scripts/zhihuiya_claim_data.py`。 |
| --inline | CLI flag | 否 | 强制全量打印标准输出，仍保存完整响应。 |
| --no-cache | CLI flag | 否 | 跳过响应缓存读取与写入；默认使用 24 小时本地缓存。 |

缓存由 `scripts/call_api.py` 单层管理，路径为：`<cwd>/linkfox/.cache/linkfox-zhihuiya-claim-data/linkfox-zhihuiya-claim-data-<hash>.json`；`hash` 是参数 JSON 按键排序、保留中文后计算 SHA-256 的前 16 个十六进制字符。缓存命中时标记 `_cache.hit=true`，过期或无法解析时按未命中处理；不叠加业务层响应缓存。

业务入口在请求前检查当前工作目录的输出位置，初始化会话元数据，并检查实际 `data` 目录的可写性；目录被文件占用或无法写入时，直接报错退出，不发起请求。完整响应及会话元数据仅写入 `<cwd>/linkfox/`，不回退到家目录、`ACPX_WORKSPACES` 或 `/tmp`。传输保留双密钥环境变量兼容、`LINKFOX_TOOL_GATEWAY` 覆盖及 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 请求头。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| total | integer | 记录数。 |
| data | array | 专利权利要求结果列表，元素结构见下表；每条对应一条专利权利要求结果。 |
| columns | array | 渲染的列定义；列对象的字段以实际响应为准。 |
| costToken | integer | 消耗 token；按返回原值保留，用户算力以网关实际扣费记录为准，不按记录条数自行换算。 |
| type | string | 渲染的样式。 |
| errcode | integer / string / null | 业务状态码；正常响应与异常判断遵循公共规则。 |
| errmsg | string | 业务消息或错误原因；认证失败消息示例为 `authorized error`。 |
| errorCode | integer | 业务状态码，`200` 表示成功，其他值表示业务错误；若实际返回则保留。该字段不替代公共规则对 HTTP 状态和 `errcode` 的判断。 |

#### data[] 元素结构

| 字段 | 类型 | 说明 |
|------|------|------|
| patentId | string | 智慧芽内部专利 ID，示例：`98a1b2c3-...`。 |
| pn | string | 专利公开（公告）号，示例：`CN115000000A`。 |
| pnRelated | string | 同族替代专利的公开号，仅在实际发生同族替代时提供，示例：`US20230001234A1`。 |
| claims | array | 权利要求对象数组，包含权利要求文本及元数据；对象结构可能因专利局和数据源而不同，子字段应按实际返回读取。 |
| claimCount | integer | 该专利的权利要求总数量，示例：15。 |

#### 本地缓存标记（脚本附加）

| 字段 | 类型 | 说明 |
|------|------|------|
| _cache | object | 缓存命中时附加的本地元数据，不属于接口业务字段。 |
| _cache.hit | boolean | `true` 表示本次读取的是本地缓存。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 目标专利没有可用权利要求时，不补造结果；依据实际数据与消息说明缺失，可建议用户核对专利号码或选择同族替代。发起后续请求前遵守 SKILL.md 的成本约束。
- 发生同族替代时，通过 `pnRelated` 识别实际文本来源，展示时必须披露替代专利公开号。

### curl 示例

```bash
curl -X POST https://tool-gateway.linkfox.com/zhihuiya/claimData \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"patentNumber": "CN115000000A,US20230001234A1", "replaceByRelated": "1"}'
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
  "skillName": "linkfox-zhihuiya-claim-data",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```