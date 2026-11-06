# Shopee AMS：查询结算验证报告 接口说明

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

## 接口：查询结算验证报告（get_validation_report）

> 官方：[get_validation_report](https://open.shopee.com/documents/v2/v2.ams.get_validation_report?module=127&type=1)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/shopee/developerProxy`

### 请求参数

#### 网关 POST Body

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| path | string | 是 | 固定 `api/v2/ams/get_validation_report`。 |
| method | string | 是 | 上游方法固定 `GET`；网关自身使用 POST。 |
| shopId | string | 与 merchantId 至少提供一个 | 目标店铺 ID，店铺级 AMS 推荐使用；脚本转成字符串。 |
| merchantId | string | 与 shopId 至少提供一个 | 商户 ID；两者同时提供时不丢弃。 |
| queryString | string | 否 | 网关可选字段，不带 `?`；脚本按本操作上游要求将顶层业务标量生成查询串。 |
| body | string | 否 | GET 入口不生成或转发请求体。 |
| contentType | string | 否 | GET 入口不发送。 |

#### 脚本 JSON 参数与选项

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| shopId | string | 与 merchantId 至少提供一个 | 脚本选店保留字段，不进入脚本生成的业务 query/body；网关会另行添加对应的 shop_id / merchant_id 查询参数。 |
| merchantId | string | 与 shopId 至少提供一个 | 脚本选店保留字段，不进入脚本生成的业务 query/body；网关会另行添加对应的 shop_id / merchant_id 查询参数。 |
| api | string | 仅通用入口必填 | 通用入口 scripts/ams_api.py 使用 `get_validation_report`；专用脚本已固定。 |
| skipDepCheck | boolean | 否 | 默认 false；仅在外部流程已确认依赖时跳过本地检测，不绕过店铺授权。 |
| contentType | string | 否 | 默认 application/json；仅对 POST 请求体生效。 |
| 业务字段（原名） | string / number / boolean | 以本操作官方要求为准 | 放 JSON 顶层；除 null 外的标量进入 queryString，空字符串、0 和 false 均保留，值 URL 编码，布尔值转小写；对象/数组不进入查询串，不可据此猜测业务列表格式。 |
| body / requestBody | JSON value / JSON string | 否 | GET 保留键，不进入查询或请求体。 |
| --inline | CLI flag | 否 | 强制完整打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 兼容选项；本技能始终禁用响应缓存，无论是否显式传入。 |

#### 参数约束与使用限制

本操作的业务字段、枚举、默认分页和上限按上方官方链接所对应的业务定义准备，不能凭接口名补造；选店、保留键、依赖检测、认证兼容、输出和缓存约定见 [脚本兼容与使用限制](../api.md#脚本兼容与使用限制)。所有 AMS 操作均要求选店，不能套用 Public 接口可省略店铺的通用说明。

### 响应结构

#### 网关响应

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 网关业务状态码；按基础规则判断，不将 0 或 false 视为空。 |
| errmsg | string | 网关结果或错误说明。 |
| httpStatus | integer | 转发后的 Shopee 上游 HTTP 状态，与 LinkFox 外层 HTTP 状态不同。 |
| contentType | string | 若返回，表示上游响应内容类型。 |
| body | string | Shopee 返回的 JSON 字符串；先判断网关与上游状态，再解析。 |

#### 脚本加工结果

| 字段 | 类型 | 说明 |
|---|---|---|
| api | string | 当前操作 `get_validation_report`。 |
| developerProxy | object | 保留完整网关响应和错误。 |
| resolvedPath | string | 实际转发路径 `api/v2/ams/get_validation_report`。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态，连接失败为 null。 |
| queryString | string | GET 实际发送的查询串；非空时输出。 |
| getValidationReport | JSON value / null | 网关正常且上游 httpStatus=200 时解析的完整 Shopee body；空内容或解析失败为 null，不只包含 response。 |
| getValidationReportResponse | 以实际响应为准 | 上述完整对象的 response 非 null 时另行提取，保留原嵌套结构。 |
| body 中的业务字段 | 以实际响应为准 | 按本操作官方定义解释实际返回的业务字段，不推测缺失字段。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 上游 `httpStatus` 不为 200 时，不生成业务解析字段；即使上游为 200，也应检查 Shopee body 内实际错误与业务结果，不能把 HTTP 成功等同于业务完成。
- 先看 `developerProxy.httpStatus` 和网关状态，再读本操作的解析结果及 `Response` 字段；解析失败时完整原始 body 仍保留在 developerProxy。

| errcode | 含义 | 处理 |
|---|---|---|
| 1002 | 参数错误或未登录 | 检查店铺标识、API Key 和业务参数。 |
| 1003 | 代理或网络异常 | 保留错误；读取重试遵守调用约束，写入先核对实际状态，避免重复操作。 |
| 1004 | 无授权记录 | 转交 `linkfox-shopee-store-auth` 处理。 |
| 1005 | path 未白名单 | 核对本操作 `api/v2/ams/...`，由服务端确认白名单。 |

### curl 示例

以下演示选店与路径，查询所需业务参数按本操作官方要求补入 queryString。

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/shopee/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"path":"api/v2/ams/get_validation_report","method":"GET","shopId":"67890"}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-shopee-store-ams",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
