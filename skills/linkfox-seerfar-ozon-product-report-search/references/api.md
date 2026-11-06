# Seerfar Ozon 商品报表搜索 接口说明

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

## 接口：商品报表搜索

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/seerfar/ozon/productReportSearch`

### 请求参数

POST Body（JSON）。以下字段与接口 `inputSchema` 一致。

#### 分页与排序

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | object | 是 | 唯一必填项；不传会被拒绝。分页与排序：`{page, pageSize, orders[]}` |
| page.page | integer | 否 | 页码，从 1 开始，默认 1 |
| page.pageSize | integer | 否 | 每页条数，默认 20 |
| page.orders | array | 否 | 排序规则，元素 `{field, direction}`；常用字段为 `sales`、`revenue`、`price`、`reviewRating`、`reviewCount`、`salesRate` |
| page.orders[].field | string | 随排序项提供 | 响应指标字段；是否支持排序由 `columns[].sortable` 标记，示例见上一行 |
| page.orders[].direction | string | 随排序项提供 | `DESC` 倒序或 `ASC` 正序 |

#### 筛选条件

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| skus | array<integer> | 否 | SKU 数组（最多 10 个），用于精确查报指定商品 |
| keywords | array<string> | 否 | 关键词数组，按商品标题筛选 |
| categoryIds | array<string> | 否 | 类目 ID 数组（Seerfar 类目 ID，非类目名） |
| sellerName | array<string> | 否 | 卖家名称数组 |
| brand | object | 否 | 品牌筛选：`{brandName, type}`，子字段见下方 |
| brand.brandName | array<string> | 否 | 品牌名称列表，配合 `brand.type` 使用 |
| brand.type | integer | 否 | `0` 包含品牌、`1` 排除品牌、`2` 无品牌 |
| fulfillment | array<string> | 否 | 配送方式数组，固定可选值：`OZON`、`FBO`、`FBS`、`RFBS`、`FBP` |
| labels | array<integer> | 否 | 标签数组，固定可选值：`0` 新品、`1` 正品、`2` 畅销品 |
| creationDate | integer | 否 | 上架时间筛选（月），固定可选值：`1` 近30天、`3` 近90天、`6` 近180天、`12` 近一年、`24` 近两年；不传不筛选 |
| variationsMerge | integer | 否 | 是否合并变体：`0` 不合并、`1` 合并 |
| searchDate | string | 否 | 查询日期 `yyyy-MM-dd`（如 `2026-04-01`）；不传默认近 30 天，传 `2026-04-01` 查 2026 年 3 月数据 |
| tag | string | 否 | 标签词 |
| uId | string | 否 | 用户 ID |
| memberId | string | 否 | 成员 ID（一个成员唯一标识，数据归属于 memberId） |

#### 范围筛选

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| monthlySales | object | 否 | {min, max}；筛选月销量 `sales`，单位/说明：件 |
| monthlySalesRate | object | 否 | {min, max}；筛选销量增长率 `salesRate`，单位/说明：% |
| monthlyRevenue | object | 否 | {min, max}；筛选月销售额 `revenue`，单位/说明：卢布 |
| price | object | 否 | {min, max}；筛选价格 `price`，单位/说明：卢布 |
| convToCartPdp | object | 否 | {min, max}；筛选购物车转化率 `convToCartPdp`，单位/说明：% |
| reviewRating | object | 否 | {min, max}；筛选评分 `reviewRating`，单位/说明：0~5 |
| reviewCount | object | 否 | {min, max}；筛选评论数 `reviewCount`，单位/说明：条 |
| questionsAndAnswers | object | 否 | {min, max}；筛选QA 数量 `questionsAndAnswers`，单位/说明：条 |
| variants | object | 否 | {min, max}；筛选变体数 `variants`，单位/说明：个 |
| drr | object | 否 | {min, max}；筛选广告费用份额 `drr`，单位/说明：比例 |
| grossMargin | object | 否 | {min, max}；筛选毛利率 `grossMargin`，单位/说明：% |
| returnCancellationRate | object | 否 | {min, max}；筛选退货取消率 `returnCancellationRate`，单位/说明：% |
| weight | object | 否 | {min, max}；筛选重量 `weight`，单位/说明：g |
| volume | object | 否 | {min, max}；筛选体积 `volume`，单位/说明：L |

以下子字段适用于上述每一个范围对象；可单边或双边传值。

| 子字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| min | number | 否 | 下界，仅传此值时做下界过滤 |
| max | number | 否 | 上界，仅传此值时做上界过滤 |

排序使用响应指标字段，结合类目、品牌、卖家缩小范围后再分页，避免在无序大结果集中盲目遍历。本接口的 `pageSize` 上限未定义，以实际响应中的校验结果为准，不套用其他接口的限制。

#### 脚本选项与运行约定

| 选项 / 环境变量 | 类型 | 必填 | 说明 |
|------|------|------|------|
| JSON 参数 | JSON | 是 | 位置参数，按上述请求对象传入 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存完整响应 |
| --no-cache | CLI flag | 否 | 禁用默认 24 小时响应缓存，重新查询且不更新缓存 |
| LINKFOX_TOOL_GATEWAY | string | 否 | 自定义网关，优先使用此值，否则使用公共规则中的默认地址；自动去掉末尾斜杠 |
| LINKFOX_AGENT_API_KEY / LINKFOXAGENT_API_KEY | string | 否 | 两者任一非空即可认证，前者优先；均为空时输出“API Key 未配置”并退出 |
| SESSION_ID | string | 否 | 用于落盘的会话标识，未设置时在进程内生成稳定标识；请求头仅发送环境变量原值，未设置时为空字符串 |
| MESSAGE_ID / MODE_ID / APP_NAME | string | 否 | 原样随同名请求头发送，未设置时为空字符串 |

缓存位于 `<cwd>/linkfox/.cache/linkfox-seerfar-ozon-product-report-search/`，键为按字段名排序的 JSON 参数的 SHA-256 前 16 位；有效期 24 小时。缓存仅保留一层，命中标记为 `_cache.hit=true`。业务错误和空结果也可被缓存，显式 `--no-cache` 可绕过缓存。缓存命中时仍保存完整响应。

按 SKILL.md 的输出策略在可写项目目录运行，禁止选择临时目录。业务脚本在请求前检查会话数据目录与元信息文件可写，并将公共调用器的输出根目录固定为 `<cwd>/linkfox/`；不可写时退出，不回退到 `ACPX_WORKSPACES`、家目录或临时目录。文件与元信息按会话聚合，保留 `_meta.json` 和 `index.jsonl`。

脚本仅执行一次网络请求，不自动翻页、换筛选或重试；HTTP 错误优先保留 JSON 响应，非 JSON 错误保留 `error` / `details`，连接错误保留 `error`。这些本地错误包装不替代公共响应判断。

**脚本本地附加字段**：对象响应的 `_http_status` 保留实际 HTTP 状态，供公共响应规则及 `401` / `402` 引导判断使用；它由业务封装添加，不是网关字段。连接失败没有 HTTP 状态，应按 `error` 解释，不能视为成功。缓存命中时，`_http_status` 是缓存写入时的历史状态，不代表新请求；已有缓存若缺少此字段，不能据此推断 HTTP 成功，也不自动绕过缓存重查，确需刷新时先说明额外消耗，再使用 `--no-cache`。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| code | string | 返回码，`"200"` 表示成功（成功时返回） |
| errcode | integer | 错误码，`200` 表示成功；业务错误时仅返回此项（成功时与 `code` 并存） |
| msg | string | 消息；成功为 `ok` |
| errmsg | string | 错误消息；成功为 `ok`，业务错误时为原因描述 |
| total | integer | 总匹配记录数（无筛选时可达数千万；按 `skus` 精确查时为命中数） |
| data | array | 商品报表数据（详见下方），与 `products` 内容完全一致 |
| products | array | 商品报表数据（与 `data` 完全一致，同一份数据的两个键） |
| columns | array | 列定义，元素含 `{field, title, cellType, sortable, filterable}`，标识可排序/可筛选字段 |
| type | string | 响应展示类型，如 `productWorkbenches` |
| costTime | integer | 接口耗时（毫秒） |
| costToken | integer | 消耗 Token 数量 |

#### data[*] / products[*] 商品报表对象字段

**标识与基础**

| 字段 | 类型 | 说明 |
|------|------|------|
| sku | integer | 商品 SKU |
| productId | integer | 统一商品 ID（= `sku`） |
| title | string | 商品标题（俄语原文） |
| imageUrl | string | 商品主图 URL |
| productUrl | string | 商品链接 |
| productPageUrl | string | 统一商品页 URL（= `productUrl`） |
| currency | string | 币种，固定 `₽` |
| sourceType | string | 数据源，固定 `ozon` |
| sourceTool | string | 来源工具标识（如 `Seerfar-Ozon-查热销榜单`） |

**销量与销售**

| 字段 | 类型 | 说明 |
|------|------|------|
| sales | integer | 月销量 |
| monthlySalesUnits | integer | 统一月销量（= `sales`） |
| revenue | number | 月销售额（卢布） |
| monthlySalesRevenue | number | 统一月销售额（= `revenue`） |
| missedRevenue | number | 损失销售额（卢布） |
| price | number | 价格（卢布） |

**转化与增长**

| 字段 | 类型 | 说明 |
|------|------|------|
| convToCartPdp | number | 购物车转化率（%） |
| orderConversionRate | number | 下单转化率（%） |
| salesRate | number | 销量增长率（%） |
| revenueRate | number | 销售额增长率（%） |
| drr | number | 广告费用份额（比例） |
| grossMargin | number | 毛利率（%） |
| returnCancellationRate | number | 退货取消率（%） |
| views | integer | 浏览量 |

**评价与互动**

| 字段 | 类型 | 说明 |
|------|------|------|
| reviewRating | number | 评分（0~5） |
| rating | number | 统一评分（= `reviewRating`） |
| reviewCount | integer | 评论数 |
| questionsAndAnswers | integer | QA 数量 |
| variants | integer | 变体数 |

**履约与物流**

| 字段 | 类型 | 说明 |
|------|------|------|
| fulfillment | array<string> | 配送方式（取值 `OZON`/`FBO`/`FBS`/`RFBS`/`FBP`） |
| weight | number | 重量（g） |
| volume | number | 体积（L） |

**上架时间**

| 字段 | 类型 | 说明 |
|------|------|------|
| upTime | integer | 上架时间戳（毫秒） |
| upDays | integer | 上架天数 |
| upMonths | integer | 上架月数 |

**品牌与卖家**

| 字段 | 类型 | 说明 |
|------|------|------|
| brandName | string | 品牌名称 |
| brand | string | 统一品牌（= `brandName`） |
| brandId | integer | 品牌 ID |
| brandUrl | string | 品牌链接 |
| sellerName | string | 卖家名称 |
| sellerId | integer | 卖家 ID（Ozon 自营可能为负值） |
| categoryInfo | object | 类目信息（详见下方） |

#### categoryInfo 类目信息对象字段

| 字段 | 类型 | 说明 |
|------|------|------|
| cnTitlePath | string | 中文类目路径 |
| enTitlePath | string | 英文类目路径 |
| titlePath | string | 俄语类目路径 |
| fullCategoryId | array<string> | 完整类目 ID 层级数组 |
| category | object | 类目节点：`{cnTitle, enTitle, title, level, id, pid, crossBorderSellable, disabled}` |

#### categoryInfo.category 类目节点

| 字段 | 类型 | 说明 |
|------|------|------|
| cnTitle | string | 中文类目名称 |
| enTitle | string | 英文类目名称 |
| title | string | 俄语类目名称 |
| level | integer | 类目层级 |
| id | string | 类目 ID |
| pid | string | 父类目 ID |
| crossBorderSellable | boolean | 是否可跨境销售 |
| disabled | boolean | 是否禁用 |

#### columns[*] 列定义

| 字段 | 类型 | 说明 |
|------|------|------|
| field | 未声明 | 对应字段名；类型以实际响应为准 |
| title | 未声明 | 展示列标题；类型以实际响应为准 |
| cellType | 未声明 | 单元格展示类型；类型及取值以实际响应为准 |
| sortable | 未声明 | 标记列是否可排序；类型以实际响应为准 |
| filterable | 未声明 | 标记列是否可筛选；类型以实际响应为准 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

| errcode | 含义 | 处理建议 |
|---------|------|----------|
| 400 | 参数错误 | 根据 `errmsg` 核对缺少 `page`、`searchDate` 格式错误或类目 ID 不合法等情况 |
| 1003 | 请求过于频繁 | 等待后再处理，不通过减小 `pageSize` 绕过限流；继续请求仍遵守成本约束 |

错误响应可能仅有 `errcode` 与 `errmsg`，没有 `code`；不要要求同时存在两个状态字段。空商品列表需结合筛选范围与匹配总数解释，不自动改参继续试探。其他错误按基础规则及实际 `errmsg` 处理。

错误响应示例：

```json
{"errcode": 1003, "errmsg": "请求过于频繁，请稍后再试。"}
```

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/seerfar/ozon/productReportSearch" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
    "page": {"page": 1, "pageSize": 3, "orders": [{"field": "sales", "direction": "DESC"}]}
  }'
```

### 响应示例（简略）

```json
{
  "code": "200",
  "msg": "ok",
  "errcode": 200,
  "errmsg": "ok",
  "total": 27879682,
  "type": "productWorkbenches",
  "costTime": 1492,
  "costToken": 16000,
  "data": [
    {
      "sku": 2107989735,
      "productId": 2107989735,
      "title": "Туалетная Бумага ROSE 12 рулонов 3 слоя с ароматом Розы",
      "imageUrl": "https://ir.ozone.ru/s3/multimedia-1-a/wc300/7814428966.jpg",
      "productUrl": "https://www.ozon.ru/product/2107989735",
      "productPageUrl": "https://www.ozon.ru/product/2107989735",
      "price": 297.0,
      "currency": "₽",
      "sales": 307524,
      "monthlySalesUnits": 307524,
      "revenue": 83095800.0,
      "monthlySalesRevenue": 83095800.0,
      "missedRevenue": 0.0,
      "salesRate": 56.0,
      "revenueRate": 58.0,
      "convToCartPdp": 25.1,
      "orderConversionRate": 87.9,
      "reviewRating": 4.9,
      "rating": 4.9,
      "reviewCount": 492242,
      "questionsAndAnswers": 277,
      "variants": 2,
      "views": 48680877,
      "drr": 0.23,
      "grossMargin": 12.7,
      "returnCancellationRate": 4.9,
      "weight": 718.0,
      "volume": 11.088,
      "upTime": 1746565200000,
      "upDays": 421,
      "upMonths": 14,
      "brandName": "Лилия",
      "brand": "Лилия",
      "brandId": 100218750,
      "brandUrl": "https://www.ozon.ru/brand/100218750",
      "sellerName": "ЛИЛИЯ",
      "sellerId": 1275208,
      "fulfillment": ["FBO"],
      "sourceType": "ozon",
      "sourceTool": "Seerfar-Ozon-查热销榜单",
      "categoryInfo": {
        "cnTitlePath": "美容和卫生 > 个人卫生用品 > 卫生纸",
        "enTitlePath": "Beauty & Hygiene > Personal Hygiene Products > Toilet Paper",
        "titlePath": "Красота и гигиена > Товары личной гигиены > Туалетная бумага",
        "fullCategoryId": ["17027489", "17027489_200001243", "17027489_200001243_93507"],
        "category": {
          "cnTitle": "卫生纸",
          "enTitle": "Toilet Paper",
          "title": "Туалетная бумага",
          "level": 3,
          "id": "17027489_200001243_93507",
          "pid": "17027489_200001243",
          "crossBorderSellable": true,
          "disabled": false
        }
      }
    }
  ]
}
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-seerfar-ozon-product-report-search",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```