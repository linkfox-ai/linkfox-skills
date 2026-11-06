# Shopee 获取品牌列表 接口说明

[接口索引](../api.md#接口索引) · [脚本运行约定](../api.md#脚本运行约定) · [认证与算力引导](../onboarding.md)

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

## 接口：获取品牌列表（get_brand_list）

查询类目品牌；page_size 最大 100。

> 官方：[get_brand_list](https://open.shopee.com/documents/v2/v2.global_product.get_brand_list?module=90&type=1)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/shopee/developerProxy`

### 请求参数

#### 网关 POST Body

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| path | string | 是 | 固定 `api/v2/global_product/get_brand_list`；全球商品路径使用 `api/v2/global_product/` 前缀。 |
| method | string | 是 | 上游方法固定 `GET`；网关本身使用 POST。 |
| shopId | string | 与 merchantId 至少一个 | 已授权店铺 ID；发布或映射操作按实际目标提供。 |
| merchantId | string | 与 shopId 至少一个 | 跨境 GlobalProduct 通常为商户级，优先使用已授权商户 ID；可与 shopId 同时传入。 |
| queryString | string | 按业务需要 | 不含 `?`，查询值须 URL 编码。CLI 从顶层业务字段构造，不接收预拼接查询串选项。 |
| body | string | 本操作不使用 | 上游 GET 不发送请求体。 |
| contentType | string | 本操作不使用 | GET 不传 body，也不在网关请求体内传此字段。 |

#### 脚本 JSON 参数

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| shopId | string | 与 merchantId 至少一个 | 店铺 ID；脚本发往网关时转为字符串。 |
| merchantId | string | 与 shopId 至少一个 | 商户 ID；脚本发往网关时转为字符串。 |
| offset | — | 是 | Query 必填；类型以本操作官方文档为准，按官方字段值提供。 |
| page_size | — | 是 | Query 必填；类型以本操作官方文档为准，按官方字段值提供。 最大 100。 |
| category_id | — | 是 | Query 必填；类型以本操作官方文档为准，按官方字段值提供。 |
| 其他顶层业务字段 | 标量 | 按官方要求 | 除保留字段外，非 null 标量会进入查询串；布尔值转为小写 true / false；其他对象 / 数组忽略。 |

保留字段为 `shopId`、`merchantId`、`skipDepCheck`、`body`、`requestBody`、`api`、`contentType`，不会进入上游查询。`global_item_id_list` 与 `item_id_list` 如提供则均按非空、最多 50 项规范化。

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| api | string | 仅通用入口必填 | `scripts/global_product_api.py` 选择注册表中的操作；独立脚本固定操作。 |
| skipDepCheck | boolean | 否 | 默认 false；已由外部流程完成依赖检查时可跳过本地检查，不绕过店铺授权。 |
| --inline | CLI flag | 否 | 强制完整打印，仍保存完整响应。 |
| --no-cache | CLI flag | 否 | 业务脚本不启用响应缓存；调用公共 run 时始终添加此选项，重复运行会重新请求接口。 |

依赖检测、环境变量兼容、无缓存例外和会话数据保存要求见 [脚本运行约定](../api.md#脚本运行约定)。

### 响应结构

#### 网关原始响应

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 网关业务状态；可缺失，按基础规则判断。 |
| errmsg | string | 网关消息，原样保留错误原因。 |
| httpStatus | integer | 转发后的 Shopee 上游 HTTP 状态，与 LinkFox 外层 HTTP 状态区分。 |
| body | string | Shopee 原始 JSON 字符串，先判断网关与上游状态，再解析。 |
| contentType | string | 网关返回时保留上游内容类型。 |
| transportHttpStatus | integer / null | 封装补充的 LinkFox 外层 HTTP 状态；连接失败为 null。 |
| error | string | 传输错误时保留的错误说明。 |
| details | string | 传输错误时可用的原始详情。 |

#### 脚本输出

| 字段 | 类型 | 说明 |
|---|---|---|
| api | string | 本次操作 `get_brand_list`。 |
| developerProxy | object | 完整网关响应及外层 HTTP 状态，保留所有原始字段。 |
| resolvedPath | string | 实际路径 `api/v2/global_product/get_brand_list`。 |
| queryString | string | GET 实际发送的编码后查询串，非空时输出。 |
| requestBody | object / array / scalar / null | POST 请求体解析结果；不改写原有嵌套结构。 |
| getBrandList | object / array / scalar / null | 网关正常且上游 httpStatus 为 200 时解析的完整 Shopee body；空或无法解析时为 null。 |
| getBrandListResponse | 任意 JSON | 上述对象内 response 非 null 时提取的业务数据。内部字段按实际响应展示，不补造 schema。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 先按基础规则检查 LinkFox 外层 HTTP 与网关 errcode，再检查 `developerProxy.httpStatus`；上游状态不是 200 时不生成解析后的业务成功数据。
- 上游 body 即使可解析，仍须结合其中实际错误内容解释结果，不能仅以解析成功认定业务完成。

| errcode | 含义 | 处理 |
|---|---|---|
| 1002 | 参数错误或未登录 | 检查商户 / 店铺标识与 API Key。 |
| 1003 | 代理或网络异常 | 说明原因；按调用约束决定是否重试，不自动连续试探。 |
| 1004 | 无授权记录 | 交给授权技能处理。 |
| 1005 | path 未加入白名单 | 核对 `api/v2/global_product/...` 并请求后端确认。 |

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/shopee/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '
{
  "path": "api/v2/global_product/get_brand_list",
  "method": "GET",
  "merchantId": "12345",
  "queryString": "offset=0&page_size=20&category_id=123"
}
'
```

模块反馈见 [Feedback](../api.md#Feedback)。

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-shopee-store-global-product",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
