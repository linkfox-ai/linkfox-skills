# Seerfar Ozon 类目商品搜索 接口说明

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

## 接口：类目商品搜索

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/seerfar/ozon/categorySearch`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| categoryId | string | 是 | Ozon 类目 ID，从 Ozon 类目文档或其他 Seerfar Ozon 工具获取。形如 `15621032_15621049_115951147`（多级类目以 `_` 连接） |
| page | object | 是 | 分页与排序：`{page, pageSize, orders[]}` |
| page.page | integer | 否 | 页码，从 1 开始，默认 1 |
| page.pageSize | integer | 否 | 每页条数，默认 20，**最大 20**（超出返回 `errcode 1002`） |
| page.orders | array | 否 | 排序规则，元素 `{field, direction}`（两者均必填）；`direction` 取 `DESC`（倒序）/ `ASC`（正序）。常用排序字段：`sales`、`price`、`revenue`、`reviewRating` |
| date | string | 否 | 查询历史月份，格式 `yyyy-MM`（如 `2026-02`）；不传默认近 30 天 |
| fulfillment | string | 否 | 配送方式过滤，固定可选值：`FBO`、`FBS`、`RFBS`、`FBP`、`OZON`；不传查询全部。**注意是单个字符串，不是数组** |
| uId | string | 否 | 用户 ID（最长 1000） |
| memberId | string | 否 | 成员 ID（一个成员唯一标识，一个用户可归属多个团队，数据归属于 memberId，最长 1000） |

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| code | string | 返回码，`"200"` 表示成功（成功时返回） |
| errcode | integer | 错误码，`200` 表示成功；业务错误时仅返回此项（成功时与 `code` 并存） |
| msg | string | 消息；成功为 `ok` |
| errmsg | string | 错误消息；成功为 `ok`，业务错误时为原因描述 |
| id | string | 回显的类目 ID |
| total | integer | **本页返回记录数**（等于当前页 `data` 条数，并非类目商品总数） |
| totalSales | integer | 类目总销量（统计区间内） |
| totalRevenue | number | 类目总销售额（卢布） |
| avgPrice | number | 类目商品平均价格（卢布） |
| rating | number | 类目商品平均评分 |
| seasonalityAmplitude | string | 季节性强度，如 `STRONG_SEASONALITY` |
| seasonalityCoef | string | 季节性阶段，如 `OFF_SEASON` |
| startDate | string | 统计起始日期 |
| endDate | string | 统计结束日期 |
| sellerType | object | **配送方式分布**（非卖家本土/跨境类型），键为配送方式、值为该方式商品数，如 `{"FBO":218,"RFBS":528,"FBP":5,"FBS":240,"OZON":1}` |
| categoryInfo | object | 类目元信息，结构见下方「categoryInfo 结构」 |
| data | array | 类目商品列表（详见下方） |
| products | array | 类目商品列表，内容与 `data` 完全一致 |
| hasNextPage | boolean | 是否有下一页 |
| columns | array | 列定义，元素含 `{field, title, cellType, sortable, filterable}` |
| type | string | 响应展示类型 |
| costTime | integer | 接口耗时（毫秒） |
| costToken | integer | 消耗 Token 数量 |

#### data[*] / products[*] 类目商品对象字段

| 字段 | 类型 | 说明 |
|------|------|------|
| sku | integer | 商品 SKU |
| productId | integer | 统一商品 ID，映射自 `sku` |
| title | string | 商品标题 |
| price | number | 商品价格（卢布） |
| currency | string | 币种，固定 `₽` |
| sales | integer | 商品销量 |
| monthlySalesUnits | integer | 统一月销量，映射自 `sales` |
| revenue | number | 商品销售额 |
| monthlySalesRevenue | number | 统一月销售额，映射自 `revenue` |
| reviewRating | number | 商品评分 |
| rating | number | 统一评分，映射自 `reviewRating` |
| reviewCount | integer | 评论数 |
| brandName | string | 品牌名称 |
| brand | string | 统一品牌，映射自 `brandName` |
| sellerName | string | 卖家名称 |
| fulfillment | array | 商品配送方式，如 `["FBO"]`，可能含多个值 |
| imageUrl | string | 商品图片链接 |
| productUrl | string | 商品链接 |
| productPageUrl | string | 统一商品页 URL，映射自 `productUrl` |
| categoryInfo | object | 商品类目归属信息，结构见下方「categoryInfo 结构」 |
| sourceType | string | 数据源，固定 `ozon` |
| sourceTool | string | 来源工具，如 `Seerfar-Ozon-查类目` |

#### categoryInfo 结构（顶层与每个商品均返回）

| 字段 | 类型 | 说明 |
|------|------|------|
| cnTitlePath | string | 中文类目路径，如 `鞋类 > 运动鞋和工作鞋 > 举重鞋` |
| enTitlePath | string | 英文类目路径，如 `Footwear > Sports and Work Footwear > Weightlifting Shoes` |
| titlePath | string | 俄文（前台）类目路径，如 `Обувь > Спортивная и рабочая обувь > Штангетки` |
| fullCategoryId | array | 各级类目 ID 数组，如 `["15621032","15621032_15621049","15621032_15621049_115951147"]` |
| category | object | 末级类目对象，含 `cnTitle`/`enTitle`/`title`(俄文)/`level`/`crossBorderSellable`(是否可跨境销售)/`pid`/`disabled`/`id` |

> `categoryInfo` 在顶层与每个 `data[*]` 中均返回且内容一致，可用于核对类目名称（中/英/俄）与可否跨境销售（`category.crossBorderSellable`）。

### 响应码规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- **不存在的类目 ID**：传入不存在的 `categoryId` 通常返回 `errcode:200`、`total:0`、`data:[]`（空结果）。判断"类目无数据"应基于 `total=0`，而非 `errcode`。

### 请求示例

```bash
curl -X POST https://tool-gateway.linkfox.com/seerfar/ozon/categorySearch \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
    "categoryId": "15621032_15621049_115951147",
    "page": {"page": 1, "pageSize": 5, "orders": [{"field": "sales", "direction": "DESC"}]}
  }'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-seerfar-ozon-category-search",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```