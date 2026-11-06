# 智慧芽专利法律状态查询 接口说明

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

## 接口：专利法律状态查询

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/zhihuiya/legalStatus`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| patentId | string | 条件必填 | 专利ID。`patentId` 和 `patentNumber` 两个参数必须至少提供一个，如果两个都存在，会优先使用 `patentId`。多个用英文逗号隔开，上限100条。最大长度：60000字符。 |
| patentNumber | string | 条件必填 | 公开(公告)号。`patentId` 和 `patentNumber` 两个参数必须至少提供一个，如果两个都存在，会优先使用 `patentId`。多个用英文逗号隔开，上限100条。最大长度：60000字符。 |


### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| total | integer | 记录数 |
| data | array | 专利法律状态列表；每条对应一条专利法律状态结果。 |
| data[].patentId | string | 专利ID |
| data[].pn | string | 公开(公告)号 |
| data[].simpleLegalStatus | array | 简单法律状态。可选值：失效-Inactive、有效-Active、审中-Pending、未确认-Undetermined、PCT指定期内-PCT designated period、PCT指定期满-PCT designated expiration |
| data[].legalStatus | array | 法律状态。可选值：公开-Published、实质审查-Examining、授权-Granted、避重授权-Double、放弃-未指定类型-Abandoned-Undetermined、放弃-主动放弃-Abandoned-Voluntarily、放弃-视为放弃-Abandoned-Deemed、撤回-未指定类型-Withdrawn-Undetermined、撤回-主动撤回-Withdrawn-Voluntarily、撤回-视为撤回-Withdrawn-Deemed、驳回-Rejected、全部撤销-Revoked、期限届满-Expired、未缴年费-Non-Payment、权利恢复-Restoration、权利终止-Ceased、部分无效-P-Revoked、申请终止-Discontinuation、PCT国际公布-PCT published、PCT进入指定国（指定期内）-PCT entering(designated period)、PCT进入指定国（指定期满）-PCT entering(designated expiration)、PCT未进指定国-PCT unentered |
| data[].eventStatus | array | 法律事件。可选值：权利转移-Transfer、许可-License、质押/担保-Pledge、信托-Trust、异议-Opposition、复审-Re-examination、海关备案-Customs、诉讼-Litigation、保全-Preservation、无效程序-Invalid-procedure、口头审理-Oral-procedure、国防解密-Declassification、一案双申-Double application |
| data[].legalDate | integer | 法律状态更新日期（时间戳） |
| errcode | integer / string / null | 公共响应码，判断规则见「公共规则」。 |
| errmsg | string | 响应说明或错误原因。 |
| errorCode | integer | 业务码：200 表示成功，其他值表示业务错误；实际返回时保留展示，基础响应判定仍按公共规则，不与 errcode 混淆。 |
| columns | array | 渲染的列定义 |
| costToken | integer | 消耗token；按返回原值保留，用户算力以网关实际扣费记录为准，不按记录条数自行换算。 |
| type | string | 渲染的样式 |

### 参数约束与使用限制

- 公开号示例为 `CN115000000A`、`US11000000B2`、`EP3000000A1`，使用 `patentNumber`；内部专利 ID 使用 `patentId`。两者的条件必填、优先级、逗号分隔、条数及长度约束见请求参数表。
- 状态与事件字段均为数组，保留所有返回值；数组元素按实际返回结构读取，不假定额外嵌套字段。
- `legalDate` 为整数时间戳；秒或毫秒单位需依据实际数据确认，不得擅自固定单位。
- `columns` 仅定义为渲染列数组，未给出内部字段结构；保留原始返回，不杜撰子字段。
- 结果受智慧芽数据库覆盖范围限制，近期申请或状态变化可能尚未更新。

### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| JSON 参数 | object | 是 | 第一个位置参数；请求字段见上方参数表。 |
| --inline | CLI flag | 否 | 强制完整打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 跳过缓存读取与写入；不传时使用 24 小时本地缓存。 |
| --help | CLI flag | 否 | 显示本地用法，不请求接口。 |
| SESSION_ID | 环境变量 string | 否 | 聚合同一任务的数据；未设置时在进程内生成会话标识。 |
| MESSAGE_ID / MODE_ID / APP_NAME | 环境变量 string | 否 | 透传到同名请求头。 |
| LINKFOX_TOOL_GATEWAY | 环境变量 string | 否 | 覆盖网关基础地址，去除末尾 `/`；默认地址见公共规则。 |
| LINKFOX_AGENT_API_KEY / LINKFOXAGENT_API_KEY | 环境变量 string | 条件必填 | 主名称优先，兼容旧名称；两者均为空时按认证引导处理。 |

业务入口调用公共 `call_api.run`，使用一层本地缓存：路径为 `<cwd>/linkfox/.cache/linkfox-zhihuiya-legal-status/`，缓存键为排序后 JSON 的 SHA-256 前 16 位，有效期为 24 小时。有效缓存可直接复用；命中时仍落盘，并标记 `_cache.hit`。响应体缓存不另作成功过滤；处理错误和空结果仍遵守执行规则。

完整响应按 UTF-8 写入当前工作目录的会话数据目录。业务封装在请求前检查会话目录、元数据和 `data` 目录可写；路径被普通文件占用或不可写时直接报错，不发起查询。数据根目录固定为 `<cwd>/linkfox`，禁止写入 `/tmp`；不向工作区、家目录或临时目录回退。输出策略见 SKILL.md。

### 本地附加字段

- `_http_status`：业务脚本保存的实际 HTTP 状态码，属于本地诊断字段，不是网关响应字段。HTTP 错误时另附 `_http_error` 保留状态码和原因，响应正文中的业务字段原样保留；非 JSON 正文保存在 `details`，非对象 JSON 正文保存在 `_response`。
- 缓存命中时这些字段反映缓存生成时的 HTTP 状态，本次未发起请求。已有缓存可能不含这些字段，缺失时不能据此推断 HTTP 成功，也不要为补齐诊断信息自动重发查询。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 脚本返回 `_http_status` 时，使用它执行基础 HTTP 判定；即使正文没有 `errcode` 或其值表示成功，HTTP 非 2xx 仍是失败。HTTP 401 / 402 按认证和算力引导处理；连接错误 `error` 也不能作为成功或空结果展示。
- 响应含 `errorCode` 且其值不为 200 时，按 `errmsg` 解释业务错误，不将其作为成功查询展示；基础响应判定仍遵守公共规则。
- 正常响应中若 `data` 为空或 `total` 为 0，说明本次未返回专利法律状态；核对标识和数据库覆盖情况，不将空结果直接认定为系统故障。

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/zhihuiya/legalStatus" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"patentNumber": "CN115000000A"}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-zhihuiya-legal-status",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```