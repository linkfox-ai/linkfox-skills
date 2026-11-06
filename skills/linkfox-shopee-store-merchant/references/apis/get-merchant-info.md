# 查询商户资料 接口说明

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

## 接口：查询商户资料（get_merchant_info）

> 官方：[get_merchant_info](https://open.shopee.com/documents/v2/v2.merchant.get_merchant_info?module=93&type=1)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/shopee/developerProxy`

### 请求参数

#### 网关 POST Body

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| path | string | 是 | 本接口的 Shopee 相对路径，见本节接口信息；须使用 `api/v2/merchant/...`。 |
| method | string | 是 | 固定 `GET`，是上游方法；网关本身使用 POST。 |
| shopId | string | 与 merchantId 至少一项 | 已授权店铺标识，支持兼容输入；仅传此项不会自动补出上游 merchant_id。 |
| merchantId | string | 与 shopId 至少一项 | 已授权商户标识；Merchant 查询应明确传入，以生成上游 merchant_id。 |
| queryString | string | 否 | URL 编码的查询串，无 `?` 前缀；本接口业务查询字段见下表。 |
| body | string | 否 | 兼容辅助函数保留的请求体字符串；本 GET 操作通常省略。 |
| contentType | string | 否 | 辅助函数带 body 时使用，默认 `application/json`。 |

本接口 `path` 为 `api/v2/merchant/get_merchant_info`，上游方法为 `GET`。此处不发送签名等公共认证参数，令牌由服务端处理。

#### 业务 Query 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| — | — | 否 | 无额外业务查询参数；商户公共参数由授权转发链路处理。 |

#### 脚本 JSON 参数与选项

| 字段 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| shopId | string | 与 merchantId 至少一项 | 已授权店铺 ID；保留兼容输入，不会自动补出上游 merchant_id。 |
| merchantId | string | 与 shopId 至少一项 | 已授权商户 ID；Merchant 查询应明确传入。 |
| api | string | 仅通用入口必填 | 通用入口固定为 `get_merchant_info`；独立脚本隐含此值。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已确认依赖时可跳过本地安装检查，不绕过授权。 |
| contentType | string | 否 | 默认 `application/json`；GET 通常不传。 |
| body / requestBody | string / object | 否 | runner 保留字段，GET 不使用且不进入查询串。 |
| 业务 Query 字段 | 见上表 | 见上表 | 在 JSON 顶层传入，runner 编码后组成 queryString。 |
| 其他业务标量字段 | string / number / boolean | 否 | runner 支持标量透传；布尔转小写，None 值忽略，dict/list 不进入查询串；不代表上游支持任意字段。 |
| --inline | CLI flag | 否 | 强制完整打印，仍然保存完整响应。 |
| --no-cache | CLI flag | 否 | 始终生效；封装本身已强制禁用响应缓存。 |

`shopId`、`merchantId`、`skipDepCheck`、`body`、`requestBody`、`api`、`contentType` 为 runner 保留字段，不拼入业务 query/body；其中 `shopId` / `merchantId` 仍由网关转为上游 `shop_id` / `merchant_id`。查询值保留百分号编码；不要将预拼 queryString 作为普通业务字段传给 CLI。其余依赖、兼容环境变量与文件规则见 [模块运行约定](../api.md#脚本运行约定)。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | LinkFox 网关状态码，按公共基本规则判断；缺失时不推断失败。 |
| errmsg | string | 网关说明或错误信息。 |
| httpStatus | integer | Shopee 上游 HTTP 状态，区别于 LinkFox 外层 HTTP 状态。 |
| contentType | string / null | 上游响应 Content-Type；无可用类型时为 null。 |
| body | string | 上游 JSON 字符串；保留原始响应，按状态检查后解析。 |

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| api | string | 本次操作 `get_merchant_info`。 |
| developerProxy | object / 其他 JSON | 网关完整响应，错误时保留错误原文。 |
| resolvedPath | string | 本次相对路径 `api/v2/merchant/get_merchant_info`。 |
| queryString | string | 实际查询串，非空时存在，无 `?`。 |
| requestBody | object / null | runner 的非 GET 兼容字段；本操作不产生。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态，连接失败时为 null。 |
| getMerchantInfo | object / array / string / number / boolean / null | 网关正常且上游 httpStatus 为 200 时解析的完整 Shopee body；空或非法 JSON 为 null。 |
| getMerchantInfoResponse | object / array / 其他 JSON | 上述解析结果的 `response`，非 null 时存在；与完整 body 不是同一层级。 |
| getMerchantInfo.response | object / array / 其他 JSON | Shopee 业务结果；对应脚本的 getMerchantInfoResponse。 |


#### getMerchantInfoResponse 商户字段

| 字段 | 类型 | 说明 |
|---|---|---|
| merchant_name | string | 商户名称。 |
| merchant_region | string | 商户所属区域。 |
| merchant_currency | string | 商户币种。 |
| auth_time | number | 授权时间；时间单位需依据实际返回确认，不默认按秒或毫秒换算。 |
| expire_time | number | 授权过期时间；时间单位需依据实际返回确认，不默认按秒或毫秒换算。 |
| is_cnsc | boolean | 是否为 CNSC 跨境商户。 |
| is_upgraded_cbsc | boolean | 是否已升级为 CBSC。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 外层正常响应后，先检查 developerProxy.httpStatus，只有上游为 200（兼容数字字符串及其前后空白）才解析 `getMerchantInfo`；Shopee body 内存在业务错误时按实际错误解释，不能因解析成功认定业务成功。
- `errcode=1002`：参数或登录问题，核对 merchantId 与 API Key；`1003`：代理或网络异常，只说明可重试，不自动重试；`1004`：无授权记录，转交认证技能；`1005`：path 未列入白名单，核对 `api/v2/merchant/...`。
- 本接口只读取当前授权商户的数据；空列表与查询失败分开说明，不自动更换商户或连续请求。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/shopee/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"path":"api/v2/merchant/get_merchant_info","method":"GET","merchantId":"12345"}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-shopee-store-merchant",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
