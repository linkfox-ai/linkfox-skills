# Shopee 查询秒杀活动列表 接口说明

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

## 接口：查询秒杀活动列表（get_shop_flash_sale_list）

> 官方：[get_shop_flash_sale_list](https://open.shopee.com/documents/v2/v2.shop_flash_sale.get_shop_flash_sale_list?module=123&type=1)

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
| queryString | string | 视业务 | 不含 `?` 的查询串；本 GET 脚本从顶层业务字段生成，未产生字段时省略。 |
| body | string | 否 | 本 GET 脚本不发送；网关仅在 POST / PUT 时向上游发送正文。 |
| contentType | string | 否 | 默认 `application/json`；辅助函数发送 body 时可指定。本 GET 脚本不发送此字段。 |

#### 本接口操作约定

| 项 | 值 / 说明 |
|---|---|
| 上游方法 | `GET` |
| path | `api/v2/shop_flash_sale/get_shop_flash_sale_list`，必须属于 `api/v2/shop_flash_sale/` 模块。 |
| 专用脚本 | `scripts/get_shop_flash_sale_list.py`（相对技能根目录）。 |
| 通用入口 | `scripts/shop_flash_sale_api.py`，api 固定为 `get_shop_flash_sale_list`。 |
| 业务用途 | 查询秒杀活动列表；分页与状态筛选。 |
| 请求映射 | GET 业务字段放脚本 JSON 顶层，由 runner 生成 queryString。 |

#### 脚本 JSON 参数与选项

| 参数 / 选项 | 类型 | 必填 | 默认值 / 说明 |
|---|---|---|---|
| api | string | 仅通用入口是 | `scripts/shop_flash_sale_api.py` 必须传本节操作名；专用入口固定操作，传入的 api 不会覆盖它。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已确认依赖时跳过本地安装检查，不替代店铺授权。 |
| body / requestBody | JSON value | 否 | 本 GET 脚本忽略这两个保留字段，不将其拼入查询串。 |
| 顶层业务字段 | string / number / boolean | 视业务 | 除保留字段和 null 外按原顺序加入 queryString；值逐项 URL 编码，布尔值转小写 true / false，嵌套对象和数组不自动展开。 |
| --inline | CLI flag | 否 | 默认关闭；开启时完整打印，仍保存完整响应。 |
| --no-cache | CLI flag | 否 | 本技能封装始终传给公共调用器；不读取或写入响应缓存。 |

脚本中的 shopId、merchantId、contentType 沿用上表定义。保留字段 `shopId`、`merchantId`、`skipDepCheck`、`body`、`requestBody`、`api`、`contentType` 不会自动进入 Shopee query/body；本 GET 脚本不会使用这两个请求体字段；低层辅助函数接收 body 不表示网关会向 GET 上游发送正文。常规调用只传选店标识，由服务端解析店铺令牌。

本 GET 注册项不启用列表归一化，数组会被忽略；不对本接口附加 50 项上限。内部列表工具的兼容约定见 [脚本运行约定](../api.md#脚本运行约定)。

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
| queryString | string | 仅有查询参数时返回，与实际发送一致，不含问号。 |
| getShopFlashSaleList | JSON value / null | 网关正常且上游 httpStatus 为 200 时，解析 Shopee 完整 body；空 body 或无法解析为 null，非成功不生成。 |
| getShopFlashSaleListResponse | JSON value | 仅 getShopFlashSaleList 为对象且其 response 不为 null 时，从 response 提取；false、0、空数组仍保留。 |

getShopFlashSaleList 是脚本输出的完整 Shopee 响应解析结果，getShopFlashSaleListResponse 才是其中的 response，二者不能混淆。业务字段、类型、必填项、分页/状态枚举和上游错误码以本节官方文档及实际响应为准，不把注册表未校验视作上游不要求。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 先判断外层 HTTP 与网关业务状态，再看 `developerProxy.httpStatus`；上游不为 200 时不生成 `getShopFlashSaleList` 成功解析字段。
- Shopee 完整 body 与其中 response 分别保留；业务成功不能仅凭解析字段存在判断，需查看实际业务消息和结果。
- 本接口专有错误码按上游 body 和官方文档解释，不自动重试或扩展操作范围。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/shopee/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
    "path": "api/v2/shop_flash_sale/get_shop_flash_sale_list",
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
  "skillName": "linkfox-shopee-store-shop-flash-sale",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
