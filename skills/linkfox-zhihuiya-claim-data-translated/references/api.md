# 智慧芽专利权利要求翻译 接口说明

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

## 接口：专利权利要求翻译

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/zhihuiya/claimDataTranslated`

### 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| patentId | string | 否* | 专利 ID，多个用英文逗号隔开，上限 100 条。当与 `patentNumber` 同时存在时优先使用专利 ID。最大长度：60000 字符。 |
| patentNumber | string | 否* | 公开（公告）号，多个用英文逗号隔开，上限 100 条。最大长度：60000 字符。 |
| lang | string | 否 | 翻译语言，支持 `en`（英文，默认）、`cn`（中文）、`jp`（日语）。最大长度：1000 字符。用户未指定语言时使用英文。 |
| replaceByRelated | integer | 否 | 原权利要求无法获取时是否用同族专利替代：`1` 是，`0` 否（默认）。只有设为 `1` 且原权利要求不可用时才使用替代文本。 |

> *`patentId` 和 `patentNumber` 必须至少提供一个；两个都存在时优先使用 `patentId`。单次最多查询 100 件专利。

### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| JSON 参数 | JSON object | 是 | 首个位置参数，字段与上述 POST Body 一致。 |
| --inline | CLI flag | 否 | 强制完整打印到标准输出，仍保存完整响应。 |
| --no-cache | CLI flag | 否 | 跳过响应缓存读取和写入；默认启用 24 小时缓存。 |

- 入口为 `scripts/zhihuiya_claim_translated.py`，通过同目录的 `scripts/call_api.py` 执行请求、缓存与输出，不单独实现另一层 HTTP 或响应缓存。
- 缓存保存在 `<cwd>/linkfox/.cache/linkfox-zhihuiya-claim-data-translated/`；缓存文件名使用排序后的 JSON 参数的 SHA-256 前 16 位，有效期为 24 小时。命中时标记 `_cache.hit=true`，仍保存本次完整响应。禁用缓存会再次请求并产生消耗。
- 使用 `LINKFOX_TOOL_GATEWAY` 覆盖网关地址；认证优先读取 `LINKFOX_AGENT_API_KEY`，其次 `LINKFOXAGENT_API_KEY`。透传 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 请求头。
- 完整响应以 UTF-8 保存到当前工作目录下的会话数据目录；业务入口固定公共调用器的数据根目录为 `<cwd>/linkfox/`，请求前检查实际输出目录及文件是否可写，不可写时报错且不发起请求，不回退家目录、`ACPX_WORKSPACES` 或临时目录。禁止在 `/tmp` 下执行并保存结果。文件名使用微秒时间戳，并以独占创建避免覆盖既有响应。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| total | integer | 记录数。 |
| data | array | 专利列表，元素字段见下表；每条对应一条专利权利要求翻译结果。 |
| columns | array | 渲染的列定义，元素结构以实际返回为准。 |
| costToken | integer | 消耗 token；按返回原值保留，用户算力以网关实际扣费记录为准，不按记录条数自行换算。 |
| type | string | 渲染的样式。 |
| errcode | integer / string / null | 网关业务状态码，按公共规则判断。错误示例为 `401`。 |
| errmsg | string | 网关消息或具体错误原因，认证失败示例为 `authorized error`。 |
| errorCode | 以实际返回为准 | 状态字段，`200` 表示成功；该字段与 `errcode` 的适用场景及并存时的优先级尚无明确约定。保留原始字段，按下方业务规则解释。 |

#### 脚本本地响应说明

- `_cache.hit=true` 是本地缓存命中标记，不是网关字段。脚本也会缓存错误响应；命中时展示的是历史响应，不代表本次重新请求或再次扣费。
- 公共调用器遇到 HTTP 异常且响应体为 JSON 时仅返回该 JSON，不单独附加 HTTP 状态。不能从保存的响应体反推 HTTP 状态；若状态字段和错误消息不足以判断，应说明状态无法确认，不得仅凭 `errcode` 缺失宣称查询成功。直接调用接口时仍按实际 HTTP 状态及公共规则判断。

#### data[] 对象

| 字段 | 类型 | 说明 |
|------|------|------|
| patentId | string | 专利 ID。 |
| pn | string | 公开（公告）号。 |
| pnRelated | string | 替代专利的公开号，仅当使用同族专利替代时提供。 |
| claims | string | 权利要求翻译文本。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 业务响应按基础规则判断；响应中的 `pnRelated` 仅说明同族替代来源，不作为错误码。
- 若响应仅含 `errorCode`，或其与 `errcode` 的成功/失败含义冲突，保留并说明实际状态字段、`errmsg` 和返回数据，明确状态字段约定尚未确认；不得仅凭 `errcode` 缺失宣称查询成功，也不擅自确定字段优先级或自动重试。

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/zhihuiya/claimDataTranslated" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"patentNumber": "US20210012345A1,EP3456789B1", "lang": "cn", "replaceByRelated": 1}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-zhihuiya-claim-data-translated",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
