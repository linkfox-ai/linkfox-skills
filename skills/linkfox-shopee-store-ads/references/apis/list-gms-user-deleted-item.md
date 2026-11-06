# Shopee 查询 GMS 用户删除商品列表 接口说明

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

## 接口：查询 GMS 用户删除商品列表（list_gms_user_deleted_item）

> 官方：[list_gms_user_deleted_item](https://open.shopee.com/documents/v2/v2.ads.list_gms_user_deleted_item?module=117&type=1)

查询 GMS 用户删除商品列表。对应脚本：`scripts/list_gms_user_deleted_item.py`；通用入口：`scripts/ads_api.py`，JSON 中 `api` 为 `list_gms_user_deleted_item`。

认证与算力问题见 [onboarding.md](../onboarding.md)；完整模块索引见 [api.md](../api.md)。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/shopee/developerProxy`

### 请求参数

#### 网关 POST Body

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| path | string | 是 | 固定为 `api/v2/ads/list_gms_user_deleted_item`，服务端按 Ads 路径选择 AD partner/token。 |
| method | string | 是 | 固定为 `GET`，表示 Shopee 上游方法；调用 LinkFox 网关始终为 POST。 |
| shopId | string | 与 merchantId 至少一个 | 店铺 ID，推荐使用；本操作属于店铺广告。不能套用其他 Public 无店铺接口的省略约定。脚本兼容传入 ID 后转成字符串。 |
| merchantId | string | 与 shopId 至少一个 | 商户 ID，是否适用以 Shopee 本操作要求为准；脚本允许同时提供两种标识。 |
| queryString | string | 按业务需要 | 不含 `?` 的 URL 查询串；GET 业务参数经脚本编码后写入，POST 入口不自动拼接。 |
| body | string | 通常不传 | 本 GET 操作通常不携带请求体。 |
| contentType | string | 通常不传 | 仅随请求体使用。 |
| accessToken | string | 禁止 | 不获取、不传原始 Token，服务端注入 AD Token。 |
| appType | string | 禁止 | 仅认证技能用于授权识别；不能传入本转发请求，服务端按 path 路由到 AD。 |

#### 脚本 JSON 参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| shopId | string | 与 merchantId 至少一个 | 店铺 ID，推荐；须事先确认广告授权。 |
| merchantId | string | 与 shopId 至少一个 | 商户 ID；须核对本操作是否支持。 |
| api | string | 仅通用入口必填 | `ads_api.py` 选择 `list_gms_user_deleted_item`，独立脚本无需传入；不会进入上游 query/body。 |
| skipDepCheck | boolean | 否 | 默认 false；仅跳过本地依赖检查，不绕过店铺广告授权。 |
| contentType | string | 否 | 默认 `application/json`；网关保留字段，不进入业务 query/body。 |
| --inline | CLI flag | 否 | 强制完整打印，同时仍保存完整响应。 |
| --no-cache | CLI flag | 否 | 封装始终加入此选项；不读取或写入响应缓存。 |
| 业务 Query 字段 | string / number / boolean | 按上游定义 | 放在 JSON 顶层；标量逐项 URL 编码，boolean 转成小写 true/false，null 与未声明的 object/array 不进入 query。 |

GET 参数组装为不带 `?` 的 `queryString`；`shopId`、`merchantId`、`skipDepCheck`、`body`、`requestBody`、`api`、`contentType` 为保留字段，不进入上游 query。当前注册表未声明列表 Query 字段；不要假设任意数组会自动转成逗号字符串。封装保留已声明列表字段的转换能力（字符串或数组、非空且最多 50 项），供注册表声明后使用。

#### 参数约束与使用限制

- 调用前由 `linkfox-shopee-store-auth` 确认目标店已有 `appType=ad`；ERP 或历史空授权类型不能替代，缺失时使用认证技能发起广告授权（URL 1 小时有效）。只需要广告时无需先开通 ERP。还须具备 Shopee 侧广告能力，并非所有站点、店铺可用。
- 不在本技能实现授权，不先取 `storeTokens`，禁止传 `accessToken` 或 `appType`。不把缺少 AD 授权的请求当成可通过 ERP 重试的操作。
- 本地依赖检测缺失退出 42，stderr 含 `DEPENDENCY_MISSING:`；确认依赖后再调用。环境变量兼容优先级为 `LINKFOX_TOOL_GATEWAY`、`SHOPEE_API_BASE_URL`、默认地址；API Key 接受公共规则中的两种名称。
- 会话数据只写当前工作目录；不可写时在请求前报错，不回退到临时目录。响应缓存始终禁用，封装始终传 `--no-cache`；公共调用器可创建空缓存目录，但不复用结果。
- 业务 Query/Body 的具体字段、必填条件、默认值、枚举及限制以本接口官方文档为准；此处未声明的上游字段不得自行补造。日期格式常为 `DD-MM-YYYY`，以当前操作定义为准。

### 响应结构

#### 网关响应（脚本 developerProxy 原样保留）

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 网关业务状态码，按公共规则判断；不得把 0 或 false 当作空值。 |
| errmsg | string | 网关消息；错误时据此解释原因。 |
| httpStatus | integer / string | Shopee 上游 HTTP 状态，与 LinkFox 外层 HTTP 不同；本封装只在其为 200 时解析业务 body。 |
| contentType | string | 上游响应内容类型，若返回则原样保留。 |
| body | string | Shopee 原始 JSON 字符串；网关和上游状态通过后才解析。原始内容始终保留，字段以官方定义及实际响应为准。 |

#### 本地传输诊断（位于 developerProxy）

以下字段由公共调用器在连接失败或 HTTP 错误正文不是 JSON 时生成，不属于网关成功响应契约。HTTP 错误正文若为合法 JSON，则原样保留；外层状态见 `transportHttpStatus`。

| 字段 | 类型 | 说明 |
|------|------|------|
| error | string | 连接失败或非 JSON HTTP 错误的说明；不能据此认定广告写入未发生。 |
| details | string | 非 JSON HTTP 错误的原始响应文本（若返回）。 |

#### Shopee body 解析结果

| 字段 | 类型 | 说明 |
|------|------|------|
| error | string | Shopee 业务错误标识（若返回）；非空时不得仅凭上游 HTTP 200 宣称业务成功。 |
| message | string | Shopee 业务消息（若返回），据此解释具体结果。 |
| request_id | string | Shopee 请求标识（若返回），用于追踪。 |
| response | 按上游定义 | Shopee 返回的业务数据，存在且不为 null 时复制为下表的 Response 字段；内部未声明的字段不补造。 |

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|------|------|------|
| api | string | 当前操作 `list_gms_user_deleted_item`。 |
| developerProxy | object / 按实际响应 | 完整网关响应或上述本地传输诊断，错误时也保留。 |
| resolvedPath | string | 实际转发路径 `api/v2/ads/list_gms_user_deleted_item`。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态，连接失败时为 null。 |
| queryString | string | 仅非空 GET 查询时输出，不带问号。 |
| requestBody | object / array / 标量 / null | 仅提供 POST body 时输出其 JSON 解析结果。 |
| listGmsUserDeletedItem | object / array / 标量 / null | 解析的完整 Shopee body，包含其 response（如有）；空 body 或解析失败时为 null，不是单独的 response 子对象。 |
| listGmsUserDeletedItemResponse | 按上游定义 | 仅解析结果为对象且 response 不为 null 时输出该子字段。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 网关正常响应后，还须检查上游 `httpStatus`；不为 200 时不解析成业务结果。即使解析了 body，仍须判断 Shopee 的 error/message，再解释业务是否成功。
- 无效或空 body 返回解析字段 null，原始 body 仍保存在 developerProxy；不得把无数据等同于已创建或已编辑成功。

| HTTP / errcode | 含义 | 处理 |
|------|------|------|
| errcode=1002 | 参数、代理配置错误或无法识别当前用户。 | 按 errmsg 检查目标店铺、路径及 API Key；若提示白名单配置缺失，需处理服务端配置。 |
| HTTP 400 / errcode=400 | 请求参数不合法，如缺少 path 或 method 无效。 | 按 errmsg 修正请求，不连续试探。 |
| HTTP 503 / errcode=503 | 代理请求发生上游 I/O 异常。 | 保留状态与错误原因；稍后按任务需要重试，写入结果不确定时先核对。 |
| errcode=1004 | 未找到当前用户的 AD 授权，或授权缺少刷新所需信息。 | 按 errmsg 核对当前账号、目标店铺和 AD 授权；缺失或无法刷新时通过认证技能重新授权，不得用 ERP 记录继续硬调。 |
| errcode=1005 | Token 失效或 path 不在白名单。 | 按 errmsg 分别处理：授权失效时重新完成 AD 授权；路径被拒时核对本接口路径及后端白名单，重新授权不能解除路径限制。 |

失败或空结果不得自动变更参数、翻页或连续试探；后续查询遵守会话调用约束。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/shopee/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
    "path": "api/v2/ads/list_gms_user_deleted_item",
    "method": "GET",
    "shopId": "67890"
}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-shopee-store-ads",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
