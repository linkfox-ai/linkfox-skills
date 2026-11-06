# 智慧芽专利家族查询 接口说明

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

## 接口：专利家族查询

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/zhihuiya/patentFamily`

### 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| patentId | string | 条件必填 | 专利 ID，与 `patentNumber` 至少提供一个；两个都存在时优先使用本字段，忽略 `patentNumber`。多个用英文逗号分隔，上限 100 条；最大长度 60000 字符。无默认值。 |
| patentNumber | string | 条件必填 | 公开（公告）号，与 `patentId` 至少提供一个；两个都存在时以 `patentId` 为准。多个用英文逗号分隔，上限 100 条；最大长度 60000 字符。无默认值。 |

#### 使用限制

- 仅查询已知专利的家族信息，不支持关键词、分类号或全文搜索。
- 家族成员数组包含摘要对象；摘要对象的字段以实际返回为准，不预设或补造成员字段。完整书目信息可能需要另外查询。

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| JSON 参数 | object | 是 | 位置参数，以 JSON 字符串传入上述查询字段；原样转交接口。 |
| --inline | CLI flag | 否 | 强制完整打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 本次跳过缓存读取与写入；未传时使用 24 小时缓存。 |

- 业务脚本调用公共 `call_api.run`，使用公共调用器提供的单层响应缓存。缓存目录为 `<cwd>/linkfox/.cache/linkfox-zhihuiya-patent-family/`，缓存键为参数排序后 SHA-256 前 16 位，有效期为 24 小时；命中时添加 `_cache.hit=true`。缓存对失败或空结果也适用；不因此自动重新发起请求。
- `LINKFOX_TOOL_GATEWAY` 优先，缺省使用正式网关；认证优先读取 `LINKFOX_AGENT_API_KEY`，兼容 `LINKFOXAGENT_API_KEY`。传递 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 请求头。
- 完整响应使用 UTF-8 保存到当前工作目录的会话数据路径，优先使用 `SESSION_ID` 聚合同一任务；缺省生成进程内稳定的会话标识，并登记 `_meta.json` 与 `index.jsonl`。请求前创建实际会话数据目录并检查可写性，失败即报错，不回退到家目录或 `/tmp`；不使用外部 `ACPX_WORKSPACES` 改写本技能的数据根目录。
- 默认以 8000 个 UTF-8 字节为完整输出阈值，大响应输出摘要及最大列表前 3 条；`--inline` 强制完整输出。每次调用均保存响应，包括缓存命中；使用微秒时间戳降低同秒输出互相覆盖的风险。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| total | integer | 返回的专利记录数，不是各家族成员数。 |
| data | array | 专利家族结果列表，元素字段见下表。 |
| columns | array | 用于渲染的列定义；元素字段以实际返回为准，不预设字段结构。 |
| costToken | integer | 本次请求消耗的 token。 |
| type | string | 渲染样式提示。 |
| errcode | integer / string / null | 业务状态码，正常与异常判断遵循公共规则；认证失败示例为 401。 |
| errmsg | string | 错误消息，如 `authorized error`；用于解释具体原因。 |
| errorCode | 未约定 | 若实际返回此业务状态字段，200 表示成功，其他值表示业务错误；字段是否出现及类型以响应为准，不据此替代公共规则中的 `errcode` 判断。 |

#### data[] 对象字段

| 字段 | 类型 | 说明 |
|------|------|------|
| patentId | string | 当前记录的专利 ID。 |
| pn | string | 公开（公告）号。 |
| simpleFamilyId | integer | 简单同族的唯一分组 ID。 |
| simpleFamily | array | 简单同族专利成员摘要对象列表。 |
| inpadocFamilyId | integer | INPADOC 同族的唯一分组 ID。 |
| inpadocFamily | array | INPADOC 同族专利成员摘要对象列表。 |
| patsnapFamilyId | integer | PatSnap 同族的唯一分组 ID。 |
| patsnapFamily | array | PatSnap 同族专利成员摘要对象列表。 |

#### 脚本附加输出字段

| 字段 | 类型 | 说明 |
|------|------|------|
| _cache.hit | boolean | 仅缓存命中时由脚本添加，值为 true，并非服务端字段。 |
| _http_status | integer | 业务脚本保留的实际 HTTP 状态，非服务端业务字段。缓存命中时为生成缓存时的历史状态；旧缓存可能没有此字段，不能据此补造状态。连接失败未收到 HTTP 响应时不添加。 |
| error | string | HTTP 错误响应为空或无法解析、或连接失败时公共调用器的错误说明。 |
| details | string | HTTP 错误响应无法解析为 JSON 时保留原始响应正文。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 脚本输出包含 `_http_status` 时，结合该状态与公共规则判断响应；HTTP 非 2xx 即为失败，即使 JSON 正文没有 `errcode` 或正文声称成功。401/402 按认证和算力指引处理，403 不归入认证或余额问题。旧缓存缺少 HTTP 状态时，依据已保留的业务码和错误消息判断，不将缺少 `errcode` 单独作为成功证据，也不为补齐状态自动重试。
- 正常响应但 `total=0` 或 `data` 为空表示没有查到家族记录，提示核对专利标识和数据库收录情况，不推断为不存在相关专利，也不自动更换条件重试。
- 查询结果只涵盖本次实际返回的数据；家族成员摘要不等于完整书目或当前法律状态，缺失信息不补造。

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/zhihuiya/patentFamily" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"patentNumber": "US10000001B2"}'
```

### 响应示例

认证错误示例：

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
  "skillName": "linkfox-zhihuiya-patent-family",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
