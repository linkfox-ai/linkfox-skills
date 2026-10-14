# Seerfar Ozon 店铺商品搜索 API 参考

## MCP 调用

| 项 | 固定值 |
|---|---|
| MCP server | `LinkFox` |
| 唯一工具 | `proxy_call` |
| `toolName` | `seerfar/ozon/shopSearch` |
| `arguments` | 直接使用本 reference 的请求参数对象；不得包裹 `body`、`params`、`data` 或另一层 `arguments` |
| 响应字段来源 | `skills/linkfox-seerfar-ozon-shop-search/references/api.md`；仅按该来源的响应字段契约核对 |

```json
{
  "toolName": "seerfar/ozon/shopSearch",
  "arguments": {
    "id": 1362816,
    "page": {
      "page": 1,
      "pageSize": 10,
      "orders": [
        {
          "field": "sales",
          "direction": "DESC"
        }
      ]
    }
  }
}
```

- `toolName` 精确匹配且区分大小写；MCP 缺失时停止，不得使用 HTTP fallback。
- WorkBuddy 自动注入 MCP Authorization；不得传 `headers`、API Key、token、JWT、手机号或其他凭证。
- 同一任务内相同 `toolName + arguments` 不重复调用；收费调用失败、空结果或结果不理想时不自动重试。
- 先检查 MCP/schema/`isError`，再读取 text/structured content；text JSON 只解析一次，随后检查下游 `errcode`/`errorCode`/`code`/`errmsg`/`msg`，最后读取业务字段。
## 请求参数

POST Body（JSON）。以下字段与接口 `inputSchema` 一致。`id` 与 `page` 必填，其余可选。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | integer | 是 | 店铺（卖家）ID，即其他 Seerfar Ozon 工具返回的 `sellerId`；负值为 Ozon 平台自营卖家（如 `-2` Ozon Express、`-4` Ozon Fresh），正值为第三方卖家 |
| page | object | 是 | 分页与排序：`{page, pageSize, orders[]}` |
| page.page | integer | 否 | 页码，从 1 开始，默认 1 |
| page.pageSize | integer | 否 | 每页条数，默认 20，**最大 20**（超出返回 `errcode 1002`） |
| page.orders | array | 否 | 排序规则，元素 `{field, direction}`；`direction` 取 `DESC`（倒序）/ `ASC`（正序）。常用排序字段：`sales`、`price`、`reviewRating`、`upTime` |
| uId | string | 否 | 用户 ID（最长 1000） |
| memberId | string | 否 | 成员 ID（一个成员唯一标识，一个用户可归属多个团队，数据归属于 memberId，最长 1000） |

> **必填约束**：`id` 与 `page` 均为必填；缺任意一项返回 `errcode 400`。
> **分页上限**：`page.pageSize` 最大为 20，翻页请通过 `page.page` 递增。
> **排序**：建议通过 `page.orders` 按核心指标排序（如 `sales` DESC 看爆品、`upTime` DESC 看新品），避免在无序结果中翻页。

## 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| code | string | 返回码，`"200"` 表示成功（成功时返回） |
| errcode | integer | 错误码，`200` 表示成功；业务错误时仅返回此项（成功时与 `code` 并存） |
| msg | string | 消息；成功为 `ok` |
| errmsg | string | 错误消息；成功为 `ok`，业务错误时为原因描述 |
| total | integer | **本页返回记录数**（等于当前页数据条数，并非店铺商品总数） |
| totalSales | integer | 店铺近 30 天总销量 |
| totalRevenue | integer | 店铺总销售额（卢布） |
| dailySales | integer | 店铺日均销量 |
| rating | number | 店铺评分（0-5） |
| productCount | integer | 店铺商品总数（全店铺，非本页条数） |
| fulfillment | object | 店铺配送方式分布，键为配送方式（`FBO`/`FBS`），值为该方式商品数，如 `{"FBO": 72, "FBS": 4}`（与商品级 `fulfillment` 数组不同） |
| data | array | 店铺商品列表（详见下方） |
| products | array | 店铺商品列表，内容与 `data` 完全一致 |
| hasNextPage | boolean | 是否有下一页 |
| columns | array | 列定义，元素含 `{field, title, cellType, sortable, filterable}` |
| type | string | 响应展示类型，如 `productWorkbenches` |
| costTime | integer | 接口耗时（毫秒） |
| costToken | integer | 消耗 Token 数量 |

### data[*] / products[*] 店铺商品对象字段

| 字段 | 类型 | 说明 |
|------|------|------|
| productId | integer | 统一商品 ID，映射自 `sku` |
| sku | integer | 商品 SKU |
| rating | number | 统一评分，映射自 `reviewRating` |
| reviewRating | number | 商品评分 |
| weight | number | 商品重量，单位 g |
| sales | integer | 商品近 30 天销量 |
| monthlySalesUnits | integer | 统一月销量，映射自 `sales` |
| upTime | integer | 商品上架时间，毫秒时间戳 |
| price | number | 商品价格（卢布） |
| currency | string | 币种，固定 `₽` |
| imageUrl | string | 统一主图 URL |
| fulfillment | array | 商品配送方式，如 `["FBO"]`，可能含多个值 |
| sellerType | integer | 卖家类型：`0` 本土，`1` 跨境 |
| returnCancellationRate | number | 商品退货取消率（%） |
| sourceType | string | 数据源，固定 `ozon` |
| sourceTool | string | 来源工具，如 `Seerfar-Ozon-查店铺` |

> **字段差异**：`returnCancellationRate` 对第三方卖家普遍返回，但对 Ozon 平台自营卖家（`id` 为负值）常常缺失，使用前需判空。
> **schema 中定义但实际不返回**：`productPageUrl`（统一商品页 URL）、`monthlySalesRevenue`（统一月销售额）、`brand`（统一品牌）在 outputSchema 中标注"上游无对应字段，保持 null"，实际响应中**不返回**这些字段（既非 null 也非空），不要依赖它们。

## 错误码

正常情况下 HTTP 状态码为 200，业务结果通过响应体区分：
- **成功**：返回 `code:"200"` + `errcode:200`（`msg` / `errmsg` 均为 `ok`）。
- **业务错误**：HTTP 仍为 200，但仅返回 `errcode`（非 200）+ `errmsg`（原因），无 `code` 字段。
- **认证失败**：HTTP 状态码 401，响应体 `{"errcode":401,"errmsg":"authorized error"}`。

| errcode | 含义 | 处理建议 |
|---------|------|----------|
| 200 | 成功 | 正常解析 `data` / `products` 字段 |
| 400 | 参数错误 | 查看 `errmsg`；常见为缺 `id`（`id 为必填参数`）、缺 `page`（`page 为必填参数`） |
| 1002 | 分页参数超出限制 | `page.pageSize` 最大为 20，调小后重试 |
| 1003 | 请求过于频繁 | 限流，稍后重试 |
| 401 | 认证失败 | HTTP 401 或 authorized error：按 SKILL.md 的 **## 解决认证和积分问题** 处理。 |
| 402 | 计费失败 | HTTP 402：按 SKILL.md 的 **## 解决认证和积分问题** 处理。 |
| 其他非 200 值 | 业务异常 | 查看 `errmsg` 获取具体原因 |

> **不存在的店铺 ID**：传入不存在的 `id` 不会报错，而是返回 `errcode:200`、`total:0`、`data:[]`（空结果）。判断"店铺无数据"应基于 `total=0`，而非 `errcode`。

错误响应示例：

```json
{
    "errcode": 1002,
    "errmsg": "分页参数超出限制，请检查输入。参数 page.pageSize 最大为 20，请调小后重试。"
}
```

```json
{
    "errcode": 400,
    "errmsg": "id 为必填参数"
}
```

## MCP 示例

完整 `proxy_call` 参数见本页“**MCP 调用**”；本页不提供工具网关 HTTP/curl fallback。
## 响应示例（简略）

```json
{
  "code": "200",
  "msg": "ok",
  "errcode": 200,
  "errmsg": "ok",
  "total": 20,
  "totalSales": 8528,
  "totalRevenue": 15113703,
  "dailySales": 284,
  "rating": 4.9,
  "productCount": 76,
  "fulfillment": {"FBO": 72, "FBS": 4},
  "hasNextPage": true,
  "type": "productWorkbenches",
  "costTime": 2985,
  "costToken": 16000,
  "data": [
    {
      "productId": 1591817986,
      "sku": 1591817986,
      "rating": 4.9,
      "reviewRating": 4.9,
      "weight": 2950.0,
      "sales": 869,
      "monthlySalesUnits": 869,
      "upTime": 1717084800000,
      "price": 1556.0,
      "currency": "₽",
      "imageUrl": "https://ir.ozone.ru/s3/multimedia-1-y/wc300/11054085154.jpg",
      "fulfillment": ["FBO"],
      "sellerType": 0,
      "returnCancellationRate": 17.5,
      "sourceType": "ozon",
      "sourceTool": "Seerfar-Ozon-查店铺"
    }
  ],
  "products": []
}
```

> `products` 内容与 `data` 完全一致，示例中用 `[ ... ]` 表示省略，实际返回与 `data` 相同的完整商品数组。

---

## Feedback API

> 该接口与上方工具接口不同，**请勿混用两个基础 URL**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **Content-Type:** `application/json`

```json
{
  "skillName": "linkfox-seerfar-ozon-shop-search",
  "sentiment": "POSITIVE",
  "category": "OTHER",
  "content": "User successfully retrieved a competitor shop's best-sellers and 30-day total sales."
}
```

**字段说明：**
- `skillName`：使用本 skill 的 YAML `name`
- `sentiment`：`POSITIVE` / `NEUTRAL` / `NEGATIVE` 三选一
- `category`：`BUG` / `COMPLAINT` / `SUGGESTION` / `OTHER` 四选一
- `content`：用户表达、实际现象、为什么算问题或好评
