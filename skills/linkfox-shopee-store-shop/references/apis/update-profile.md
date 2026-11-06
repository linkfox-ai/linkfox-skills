# Shopee 更新店铺资料 接口说明

[接口导航与运行约定](../api.md) · [认证与用量引导](../onboarding.md)

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

## 接口：更新店铺资料（update_profile）

> 官方：[v2.shop.update_profile](https://open.shopee.com/documents/v2/v2.shop.update_profile?module=92&type=1)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/shopee/developerProxy`

### 请求参数

#### 网关 POST Body

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| shopId | string | 与 merchantId 至少一项 | 已授权店铺 ID，推荐；脚本转为字符串。 |
| merchantId | string | 与 shopId 至少一项 | 已授权商户 ID；两者同时传入时均保留，不擅自更换目标。 |
| path | string | 是 | 本接口固定上游相对路径，见下方；必须以 api/v2 开头。 |
| method | string | 是 | 本接口上游方法，见下方；网关外层始终 POST。 |
| queryString | string | 否 | GET 业务查询串，不含 ?；脚本对参数值做 URL 编码。 |
| body | string | POST 时 | 上游请求体的 JSON 字符串。 |
| contentType | string | 否 | 传 body 时默认 application/json。 |

上游方法：`POST`；固定 path：`api/v2/shop/update_profile`。

#### 脚本选项与映射

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| api | string | 仅通用入口必填 | shop_api.py 使用当前操作名；专用脚本无需传入。 |
| shopId / merchantId | string | 至少一项 | 网关选店字段，不进入上游查询串或 body。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已确认依赖时跳过本地安装检查，不绕过授权。 |
| body / requestBody | object / string | POST 可选 | 优先 body，其次 requestBody，再取本接口支持的顶层业务字段；必须是有效 JSON 对象。 |
| contentType | string | 否 | 默认 application/json；传给网关的请求体内容类型。 |
| --inline | CLI flag | 否 | 完整打印并保存响应。 |
| --no-cache | CLI flag | 否 | 公共调用器与业务封装始终使用此选项，不读写响应缓存；保留命令行传入兼容。 |

POST 按 body、requestBody、已登记顶层业务字段的优先级构建请求体；不把顶层选店字段混入请求体。本操作不构建 queryString。请求体不是有效 JSON 对象时，脚本在发送请求前报错并退出 1。

#### 上游 Body 字段

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| shop_name | string | 至少一项 | 新店名；30 天内仅可修改一次。 |
| shop_logo | string | 至少一项 | Shopee 图片 URL。 |
| description | string | 至少一项 | 描述，不超过 500 字符。 |

### 响应结构

#### 网关响应

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | LinkFox 网关状态码，遵循公共规则。 |
| errmsg | string | 网关消息。 |
| httpStatus | integer | Shopee 上游状态码，与外层 HTTP 状态不同。 |
| body | string | Shopee 返回的原始 JSON 字符串。 |
| contentType | string（如返回） | 上游内容类型；保留实际响应。 |

#### 脚本输出

| 字段 | 类型 | 说明 |
|---|---|---|
| api | string | 当前操作名 update_profile。 |
| developerProxy | object | 完整网关响应。 |
| resolvedPath | string | api/v2/shop/update_profile。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败为 null。 |
| requestBody | object（POST 时） | 实际发送的解析后请求体。 |
| updateProfile | object / null | 网关正常且上游 httpStatus=200 时解析 body 得到的完整 Shopee 对象；空 body 或解析失败为 null。 |
| updateProfileResponse | 任意 JSON 值（如存在） | updateProfile.response 非 null 时提取的业务响应；不是整个 Shopee 对象。 |

#### Shopee body 与业务字段

| 字段 | 类型 | 说明 |
|---|---|---|
| error | string（如返回） | Shopee 业务错误；非空时不能宣称业务成功。 |
| message | string（如返回） | Shopee 业务错误说明。 |
| response | 结构以实际返回为准 | 实际业务数据；如返回 response 则保留其内容；下列业务字段按实际响应层级读取，不强制假定都位于 response 内。 |

本操作成功响应的具体业务字段以保存的真实上游响应为准，不假定固定 schema。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 网关正常后，再判断上游 httpStatus；仅 200 时解析业务响应。Shopee error 非空时解释 message，不将 HTTP 请求完成等同于业务成功。
- 网关 httpStatus 与 Shopee 原始 body 始终保留，字段缺失或解析失败不得补造数据。

| errcode | 含义 | 处理 |
|---|---|---|
| 1002 | 参数错误或未登录 | 检查选店标识及 API Key。 |
| 1003 | 代理或网络异常 | 保留错误，后续重试遵守 SKILL.md 成本约束，不自动连续试探。 |
| 1004 | 无授权记录 | 转交授权技能检查授权。 |
| 1005 | 路径未在白名单或授权信息已失效 | 按 errmsg 区分：核对 api/v2/shop/... 路径；提示重新授权时转交授权技能。 |

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/shopee/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"shopId": "67890", "path": "api/v2/shop/update_profile", "method": "POST", "body": "{\"description\":\"用户提供的新简介\"}", "contentType": "application/json"}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-shopee-store-shop",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
