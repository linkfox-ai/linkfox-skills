# 智慧芽专利说明书翻译 接口说明

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

## 接口：获取说明书翻译（descriptionDataTranslated）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/zhihuiya/descriptionDataTranslated`

### 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| patentId | string | 条件必填 | 专利 ID。与 `patentNumber` 至少提供一个；同时存在时优先使用 `patentId`。多个用英文逗号分隔，上限 100 条；最大长度 60000 字符。 |
| patentNumber | string | 条件必填 | 公开（公告）号，如 `US10123456B2`。与 `patentId` 至少提供一个；同时存在时优先使用 `patentId`。多个用英文逗号分隔，上限 100 条；最大长度 60000 字符。 |
| lang | string | 否 | 目标翻译语言：`en`（英文，默认）、`cn`（中文）、`jp`（日语）；最大长度 1000 字符。未指定语言时使用 `en`。 |
| replaceByRelated | integer | 否 | 说明书无法获取时是否用同族专利说明书替代：`1` 是、`0` 否，默认 `0`。 |

#### 脚本选项与运行约定

| 选项或约定 | 类型 | 说明 |
|------------|------|------|
| JSON 参数 | string | 第一个位置参数，内容为上述请求对象；请求字段名与值直接传递。 |
| --inline | CLI flag | 强制全量输出，同时保存完整响应。 |
| --no-cache | CLI flag | 本次不读取也不写入响应缓存；默认启用 24 小时本地缓存。 |
| --help | CLI flag | 显示本地用法，不发送请求。 |
| 缓存位置 | path | `<cwd>/linkfox/.cache/linkfox-zhihuiya-description-data-translated/`；按参数排序后的 JSON 计算 SHA-256 前 16 位作为缓存键。业务封装与公共调用器使用相同的缓存位置和缓存键，仅由公共调用器管理，不叠加第二层缓存。Windows 业务封装为该缓存文件提供扩展路径写法，兼容长文件名，不改变实际缓存位置或缓存键。 |
| 完整响应 | path | 保存到 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-zhihuiya-description-data-translated-<timestamp>.json`，使用 UTF-8；会话同时维护 `_meta.json` 和 `index.jsonl`。 |
| 会话标识 | string | 优先使用 `SESSION_ID`，未设置时进程内生成稳定标识。 |
| 输出阈值 | integer | 8000 字节；不超过阈值全量输出，超过则展示顶层字段、常见计数、最大列表长度及前 3 条样本。 |

`LINKFOX_TOOL_GATEWAY` 优先于默认网关；兼容 `LINKFOX_AGENT_API_KEY`（优先）和 `LINKFOXAGENT_API_KEY`，并透传 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 请求头。业务脚本在请求前检查当前目录下的数据目录可写，并将公共调用器落盘根目录固定为 `<cwd>/linkfox`；Windows 使用同一目录的扩展路径写法以支持长文件名。不回退到 `ACPX_WORKSPACES`、家目录或临时目录，禁止在 `/tmp` 下运行落盘。当前目录不可写时报错。

24 小时内相同参数可复用完整响应，命中时加 `_cache.hit=true`；包括失败或空结果在内的返回对象也可能被缓存，不自动重试。禁用缓存会产生一次新的请求，需遵守成本约束。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| total | integer | 记录数。 |
| data | array | 专利列表，元素字段见下表；每条对应一条专利说明书翻译结果。 |
| columns | array | 渲染的列定义；元素内部字段以实际返回为准。 |
| costToken | integer | 消耗 token；按返回原值保留，用户算力以网关实际扣费记录为准，不按记录条数自行换算。 |
| type | string | 渲染的样式。 |
| errcode | integer / string / null | 业务状态码，按公共响应码基本规则判断；错误响应可使用此字段。 |
| errmsg | string | 错误消息，报告实际原因。 |
| errorCode | integer | 本接口的业务状态字段，`200` 表示成功、`401` 表示未授权，其他非 `200` 值表示业务异常；错误响应也可使用 `errcode`。此字段出现时须检查其业务状态，不假定接口始终返回此字段，也不将其取值约定扩展为通用响应码规则。 |

#### data 数组元素字段

| 字段 | 类型 | 说明 |
|------|------|------|
| patentId | string | 专利 ID。 |
| pn | string | 公开（公告）号。 |
| description | string | 说明书翻译文本。 |
| pnRelated | string | 替代专利的公开号，仅当使用同族专利替代时提供。 |

#### 脚本附加字段

| 字段 | 类型 | 说明 |
|------|------|------|
| _cache | object | 仅缓存命中时附加缓存信息。 |
| _cache.hit | boolean | 缓存命中为 `true`。 |
| error | string | 网络错误，或 HTTP 错误响应无法解析为 JSON 时的本地错误说明。 |
| details | string | HTTP 错误响应无法解析为 JSON 时保留原始响应内容。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 除公共响应码检查外，响应若包含 `errorCode`，还须按上表判断本接口业务是否成功；不能仅因 HTTP 成功且 `errcode` 缺失而忽略 `errorCode` 中的业务错误。未授权或算力不足时按 `references/onboarding.md` 处理，其他错误报告实际 `errmsg`，不把业务错误当作空翻译。
- 空翻译不能证明专利不存在，也不能证明所有同语言请求均不受支持。报告真实空结果，保留用户指定的目标语言。
- 用户需要原始说明书时转交 `/zhihuiya/descriptionData` 原文查询能力，并核验返回的专利身份和文本语言；这是转交提示，本技能只定义翻译接口。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/zhihuiya/descriptionDataTranslated" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"patentNumber":"US10123456B2,EP3456789A1,CN112345678A","lang":"cn","replaceByRelated":1}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-zhihuiya-description-data-translated",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```