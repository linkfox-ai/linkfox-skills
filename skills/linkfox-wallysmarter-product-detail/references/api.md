# WallySmarter Walmart 商品详情 接口说明

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

## 接口：商品详情

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/wallysmarter/productDetail`

### 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| productId | integer | 是 | 商品ID（ItemId），商品详情链接中包含的数字ID。例如：`https://www.walmart.com/ip/5169493923` 中的 `5169493923` |
| includeStats | boolean | 否 | 是否包含历史价/历史销量，默认 `true`；仅查当前详情时须显式传 `false`，省略此字段仍会包含历史统计 |

#### 使用限制

- 仅支持 Walmart 数字 ItemId，每次请求只查询一个商品；不支持批量参数。用户要求查询多个商品时，逐个编号分别调用，并事先说明合计消耗。
- 请求中的 `productId` 是数字 ItemId，不是响应商品对象中可能含字母的 `productId`；数字编号对应响应中的 `usItemId`。
- 历史数据可用性取决于 WallySmarter 的追踪覆盖范围；实际覆盖期间以返回的日期为准，不保证每个商品都有完整历史。

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| JSON 参数 | object | 是 | 首个位置参数，字段见上表，原样转发 |
| --inline | CLI flag | 否 | 强制完整打印，仍保存完整响应 |
| --no-cache | CLI flag | 否 | 跳过缓存读取和写入；默认启用 24 小时本地缓存 |

缓存位于 `<cwd>/linkfox/.cache/linkfox-wallysmarter-product-detail/`，以参数排序后的 JSON 的 SHA-256 前 16 位为键；命中时标记 `_cache.hit=true`。仅使用公共调用器这一层缓存，不叠加业务缓存。缓存可保存错误或空结果；需要重新请求时显式使用 `--no-cache`，并遵守算力约束。

支持通过 `LINKFOX_TOOL_GATEWAY` 覆盖网关地址；支持两种密钥环境变量，`LINKFOX_AGENT_API_KEY` 优先于 `LINKFOXAGENT_API_KEY`，并透传 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 请求头。响应文件和会话元数据保存在当前工作目录；业务入口在请求前检查该目录可写，禁止写入 `/tmp`，不可写时报错，不回退家目录或临时目录。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer | 错误码，认证失败时可返回 `401`；通用状态判断见公共规则 |
| errmsg | string | 错误消息，认证失败时可返回 `authorized error` |
| code | string | 返回码（`"200"` 表示成功） |
| msg | string | 消息（成功时为 `"ok"`，失败时为错误描述） |
| total | integer | 返回的商品数量（本接口通常为 1） |
| products | array | 商品列表（见下方商品对象） |
| columns | array | 列定义（描述 products 中各字段的元信息，含 field、title、cellType 等） |
| type | string | 响应渲染类型（固定值 `"productWorkbenches"`） |
| costTime | integer | 接口耗时（毫秒） |
| costToken | integer | 消耗 Token 数量 |

#### 脚本本地附加字段

- `_http_status`：业务脚本记录的实际 HTTP 状态码，不是网关响应字段。先按该状态检查公共规则，再判断 `errcode` 和本接口的 `code`；HTTP 非 2xx 时，即使响应体含 `code=200` 也不表示查询成功。网络连接失败时保留 `error`，没有 HTTP 状态码。
- 缓存命中时，`_http_status` 是生成缓存时的历史状态，不代表本次发起了请求。旧缓存可能没有该字段，不能据此推断 HTTP 成功；结合已有错误信息判断。确需重新确认时，说明额外消耗后使用 `--no-cache`。

#### columns[*] 列定义

| 字段 | 类型 | 说明 |
|------|------|------|
| field | 以实际返回为准 | 对应的商品字段标识 |
| title | 以实际返回为准 | 列标题 |
| cellType | 以实际返回为准 | 单元格渲染类型 |

以上为列元信息的常见字段；字段类型及 `cellType` 取值以实际返回为准，不限定完整字段或枚举集合。保留响应中的其他列元信息，不自行补造。

#### products[*] 商品对象

| 字段 | 类型 | 说明 |
|------|------|------|
| usItemId | integer | 商品内部 ID（即请求中的 productId） |
| productId | string | Walmart 商品唯一标识（字母数字混合，如 `"6YBM50F6ZXAE"`） |
| title | string | 商品名称 |
| description | string | 商品描述 |
| price | number | 当前售价（美元） |
| wasPrice | number | 划线价（美元），无折扣时可能为 null |
| minPrice | number | 最低价格（美元） |
| brand | string | 品牌名称 |
| rating | number | 商品评分（0.0–5.0） |
| reviews | integer | 评论数量（条） |
| salesEstimate | integer | 销量估算（件，近期周期内） |
| revenue | number | 收入估算（美元） |
| sellerName | string | 卖家名称 |
| fulfillmentType | string | 配送类型：`"MARKETPLACE"`（第三方卖家自配送）或 `"WFS"`（Walmart Fulfillment Services） |
| productPageUrl | string | 商品页面 URL |
| imageUrl | string | 商品图片 URL（缩略图） |
| departmentName | string | 所属部门名称（如 `"Cell Phones"`） |
| departmentId | integer | 所属部门 ID |
| listingScore | integer | Listing 质量评分 |
| contentScore | integer | 内容质量分 |
| outOfStock | integer | 是否缺货（`0`=有货，`1`=缺货） |
| sponsored | integer | 是否广告商品（`0`=否，`1`=是） |
| isBranded | integer | 是否品牌商品（`0`=否，`1`=是） |
| multipleOptionsAvailable | integer | 是否有变体（`0`=否，`1`=是） |
| createdAt | string | WallySmarter 首次收录时间（格式：`yyyy-MM-dd'T'HH:mm:ss.SSSSSS'Z'`） |
| updatedAt | string | 最近一次数据更新时间（格式同上） |
| stats | object/null | 历史统计数据（仅当 `includeStats=true` 时返回，否则为 null。结构见下方） |
| sourceTool | string | 来源工具标识 |
| sourceType | string | 商品来源平台（固定值 `"walmart"`） |

#### stats 对象结构

当 `includeStats=true`（默认）时返回，按天聚合、按时间升序，时区为 UTC，覆盖商品被 WallySmarter 收录以来的可用历史，实际覆盖范围遵循上方使用限制。包含两个时间序列数组：

| 字段 | 类型 | 说明 |
|------|------|------|
| stats.price | array | 历史售价时间序列（按日期升序）。每项为单条日期-售价映射 |
| stats.sales | array | 历史销量时间序列（按日期升序）。每项为单条日期-销量映射 |

**数组元素结构：**

每个元素是只包含一个键值对的对象：

| 字段 / 位置 | 类型 | 说明 |
|------|------|------|
| stats.price[*] | object | 单条日期与售价映射，仅一个键值对 |
| stats.sales[*] | object | 单条日期与销量映射，仅一个键值对 |
| 映射的 key | string | 日期，格式 `yyyy-MM-dd`，时区 UTC |
| stats.price[*] 的 value | number | 当日售价，美元 |
| stats.sales[*] 的 value | number | 当日销量，件 |

**示例片段：**

```json
{
  "stats": {
    "price": [
      {"2025-08-18": 279.94},
      {"2025-09-29": 279.94}
    ],
    "sales": [
      {"2025-08-18": 62},
      {"2025-09-29": 79}
    ]
  }
}
```

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 公共规则通过后，再检查本接口的 `code`：以 `200`（数字或字符串）表示业务成功，其他值为业务异常，结合 `msg` 解释具体原因。不要以 HTTP 请求完成代替商品详情查询成功。
- 业务异常通常在 HTTP 200 响应体中体现；商品列表为空时说明未取得商品数据，提示核对编号和追踪覆盖情况，后续查询遵守成本约束。

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/wallysmarter/productDetail" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"productId": 5177343351, "includeStats": true}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-wallysmarter-product-detail",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```