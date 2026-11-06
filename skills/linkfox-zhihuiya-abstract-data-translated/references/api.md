# 智慧芽专利标题与摘要翻译 接口说明

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

## 接口：专利标题与摘要翻译（abstractDataTranslated）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/zhihuiya/abstractDataTranslated`

### 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| patentId | string | patentId 和 patentNumber 至少填一个 | 智慧芽内部专利ID，多个用英文逗号隔开。最大长度 60,000 字符；与 patentNumber 同时提供时优先使用 patentId |
| patentNumber | string | patentId 和 patentNumber 至少填一个 | 公开(公告)号，多个用英文逗号隔开。最大长度 60,000 字符 |
| replaceByRelated | integer | 否 | 摘要无法获取时是否用同族专利摘要替代：`1` 是，`0` 否。默认 `0` |
| lang | string | 否 | 翻译目标语言。可选值：`en`（英文，默认）、`cn`（中文）、`jp`（日语）。最大长度 1,000 字符 |

#### 参数约束与使用限制

- 标识参数支持英文逗号分隔的批量查询；不支持关键词、分类号或申请人检索。
- 查询期间保留用户请求的目标语言，不得因空结果静默改用其他语言。
- 只有用户明确要求原摘要缺失时使用同族摘要，才启用 `replaceByRelated`；不得传布尔值替代整数约定。
- 仅返回标题和摘要翻译，不返回完整专利正文、权利要求或说明书，也不提供法律状态、引用、布局、估值或侵权结论。

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| JSON 参数 | object | 是 | 命令行首个位置参数，字段与上表一致。 |
| --inline | CLI flag | 否 | 强制完整打印响应，同时保存完整响应文件。 |
| --no-cache | CLI flag | 否 | 禁用本次缓存读取和写入；仍保存完整响应。 |
| --help / -h | CLI flag | 否 | 显示本地帮助，不发起请求。 |

业务脚本调用 `call_api.run`，只使用公共调用器的一层 24 小时缓存。缓存目录为 `<cwd>/linkfox/.cache/linkfox-zhihuiya-abstract-data-translated/`，缓存键取参数排序后的 JSON 的 SHA-256 前 16 位，命中时设置 `_cache.hit` 标记。缓存过期后重新查询；使用 `--no-cache` 会产生新请求，须遵守成本约束。

通过 `LINKFOX_TOOL_GATEWAY` 覆盖网关地址；认证优先读取 `LINKFOX_AGENT_API_KEY`，也兼容 `LINKFOXAGENT_API_KEY`。请求使用 150 秒超时，并透传 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 环境信息。

完整响应按 SKILL.md 的输出策略保存。业务脚本在调用前检查 `<cwd>/linkfox/` 及实际会话的 `data/` 目录是否可写，并将公共调用器的数据根目录固定到该路径，不采用 `ACPX_WORKSPACES`、用户目录或临时目录作为回退；不可写时在请求前报错。`SESSION_ID` 必须指向当日数据目录内的会话子目录，不能将输出导向目录外；`data/` 也不得通过符号链接指向会话外。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| total | integer | 返回的专利记录数 |
| data | array | 专利列表；每条对应一条专利摘要翻译结果。 |
| data[].patentId | string | 智慧芽内部专利ID |
| data[].pn | string | 公开(公告)号 |
| data[].title | string | 标题翻译 |
| data[].abstractText | string | 摘要翻译 |
| data[].pnRelated | string | 替代专利的公开号（仅当使用同族专利替代时提供） |
| columns | array | 渲染的列定义 |
| costToken | integer | 消耗token；按返回原值保留，用户算力以网关实际扣费记录为准，不按记录条数自行换算。 |
| type | string | 渲染的样式 |


#### 网关状态字段

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 网关业务状态码，按公共响应码基本规则判断；认证失败示例值为 `401`。 |
| errmsg | string | 网关错误消息，如认证失败时的 `authorized error`；使用实际消息解释原因。 |
| errorCode | 以实际返回为准 | 业务状态字段，`200` 表示成功，其他值表示业务错误（如 `401` 表示未授权）；与 `errcode` 为不同字段，须按实际返回检查，不假定两者一定同时出现。 |

`columns` 数组的元素结构以实际返回为准，不依赖固定嵌套字段。翻译结果以实际返回的专利记录为准。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 业务状态字段包括 `errorCode` 和 `errcode`，按实际返回检查，不擅自重命名或假定两者一定同时出现。仅返回 `errorCode` 时，也须检查其报告的业务错误，不因缺少 `errcode` 就忽略；HTTP 与 `errcode` 的基础判断仍遵循公共规则。
- 空翻译或空列表只说明本次没有返回目标翻译，不等同于专利不存在或全部同语言请求不受支持；需要原文时转交基础著录项查询并核对语言。
- 出现 `data[].pnRelated` 表示采用同族专利替代，须展示来源公开号，不能当作原专利摘要。

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/zhihuiya/abstractDataTranslated" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"patentNumber":"US20200012345A1","lang":"en","replaceByRelated":0}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-zhihuiya-abstract-data-translated",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
