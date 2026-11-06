# Shopee 更新秒杀活动 接口说明

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

## 接口：更新秒杀活动（update_shop_flash_sale）

> 官方：[update_shop_flash_sale](https://open.shopee.com/documents/v2/v2.shop_flash_sale.update_shop_flash_sale?module=123&type=1)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/shopee/developerProxy`

### 请求参数

#### 网关 POST Body

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| path | string | 是 | 本接口的 Shopee 相对路径，见本节操作约定；不含主机名。 |
| method | string | 是 | 本接口上游方法，见本节操作约定；网关请求本身仍为 POST。 |
| shopId | string | 与 merchantId 至少一项 | 店铺 ID，推荐；辅助函数会将数字转为字符串。本秒杀模块的脚本要求 shopId 与 merchantId 至少一项，不适用 Public 等无店铺接口的省略规则。 |
| merchantId | string | 与 shopId 至少一项 | 商户 ID；兼容同时传入两个标识，脚本不擅自择一。 |
| queryString | string | 否 | 辅助函数 `developer_proxy_call(query_string=...)` 可显式传入无 `?` 查询串；本 POST 脚本不生成此字段。 |
| body | string | 否（网关）；本 POST CLI 与 requestBody 至少一项 | Shopee 业务 JSON 字符串。脚本输入可为任意 JSON 值：非字符串序列化为紧凑 JSON，字符串保留原文本；空字符串透传。 |
| contentType | string | 否 | 默认 `application/json`；脚本可指定。未传或传空值时使用默认值。 |

#### 本接口操作约定

| 项 | 值 / 说明 |
|---|---|
| 上游方法 | `POST` |
| path | `api/v2/shop_flash_sale/update_shop_flash_sale`，必须属于 `api/v2/shop_flash_sale/` 模块。 |
| 专用脚本 | `scripts/update_shop_flash_sale.py`（相对技能根目录）。 |
| 通用入口 | `scripts/shop_flash_sale_api.py`，api 固定为 `update_shop_flash_sale`。 |
| 业务用途 | 更新秒杀活动设置。 |
| 请求映射 | POST 传完整 body / requestBody；字段及嵌套结构由官方文档确定。下方示例仅演示封装，必须替换占位业务字段后才可提交。 |

#### 脚本 JSON 参数与选项

| 参数 / 选项 | 类型 | 必填 | 默认值 / 说明 |
|---|---|---|---|
| api | string | 仅通用入口是 | `scripts/shop_flash_sale_api.py` 必须传本节操作名；专用入口固定操作，传入的 api 不会覆盖它。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已确认依赖时跳过本地安装检查，不替代店铺授权。 |
| requestBody | JSON value | 与 body 至少一项 | 脚本输入 body 的兼容别名，接收类型和序列化规则同上；body 字段存在时优先，即使其值为 null 或空字符串。 |
| 顶层业务字段 | 以 body schema 为准 | 不适用 | 本 POST 注册项未配置 body_fields，顶层业务字段不会自动进入请求体，须放入 body / requestBody。 |
| --inline | CLI flag | 否 | 默认关闭；开启时完整打印，仍保存完整响应。 |
| --no-cache | CLI flag | 否 | 本技能封装始终传给公共调用器；不读取或写入响应缓存。 |

脚本中的 shopId、merchantId、contentType 沿用上表定义。保留字段 `shopId`、`merchantId`、`skipDepCheck`、`body`、`requestBody`、`api`、`contentType` 不会自动进入 Shopee query/body；用户显式提供的 body 内容按原值发送，不删除其中字段。本 POST 脚本不把未知顶层字段写入 body；常规调用只传选店标识，由服务端解析店铺令牌。

本 POST 注册项没有 body_fields 声明，必须提供 body / requestBody；body 内的对象、数组及嵌套结构完整保留。除兼容空字符串外，无效 JSON 文本会在请求前退出。

依赖检测、网关环境变量、落盘与缓存的实际约定见 [脚本运行约定](../api.md#脚本运行约定)；出现认证或算力问题时读取 [引导说明](../onboarding.md)。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 网关业务状态；允许缺失，按公共规则判断，不将 0 或 false 当成功。 |
| errmsg | string | 网关消息；根据实际错误说明处理。 |
| httpStatus | integer | Shopee 上游 HTTP 状态，与调用 LinkFox 的外层 HTTP 状态不同。 |
| contentType | string / null | Shopee 上游响应内容类型，由网关返回。 |
| body | string | Shopee 原始 JSON 响应；上游嵌套字段以官方文档和实际响应为准。 |

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| api | string | 实际执行的秒杀操作名。 |
| developerProxy | object | 上述完整网关响应；异常时保留错误对象。 |
| resolvedPath | string | 实际转发的 Shopee 相对路径。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败时为 null。 |
| developerProxy.error | string | 本地调用层生成的 HTTP 或连接异常描述；仅对应异常出现。 |
| developerProxy.details | string | 本地调用层在 HTTP 错误体无法解析为 JSON 时保留的原文。 |
| requestBody | JSON value / null | 仅 POST 返回；由发送的 body 解析，空字符串为 null。 |
| updateShopFlashSale | JSON value / null | 网关正常且上游 httpStatus 为 200 时，解析 Shopee 完整 body；空 body 或无法解析为 null，非成功不生成。 |
| updateShopFlashSaleResponse | JSON value | 仅 updateShopFlashSale 为对象且其 response 不为 null 时，从 response 提取；false、0、空数组仍保留。 |

updateShopFlashSale 是脚本输出的完整 Shopee 响应解析结果，updateShopFlashSaleResponse 才是其中的 response，二者不能混淆。业务字段、类型、必填项、分页/状态枚举和上游错误码以本节官方文档及实际响应为准，不把注册表未校验视作上游不要求。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 先判断外层 HTTP 与网关业务状态，再看 `developerProxy.httpStatus`；上游不为 200 时不生成 `updateShopFlashSale` 成功解析字段。
- Shopee 完整 body 与其中 response 分别保留；业务成功不能仅凭解析字段存在判断，需查看实际业务消息和结果。
- 本接口专有错误码按上游 body 和官方文档解释，不自动重试或扩展操作范围。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/shopee/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
    "path": "api/v2/shop_flash_sale/update_shop_flash_sale",
    "method": "POST",
    "shopId": "67890",
    "body": "{\"<官方业务字段>\":\"<按用户资料填写>\"}",
    "contentType": "application/json"
}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-shopee-store-shop-flash-sale",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
