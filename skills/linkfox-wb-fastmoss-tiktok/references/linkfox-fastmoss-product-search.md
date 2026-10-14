# `linkfox-fastmoss-product-search` 参考

## 功能与边界

按关键词和多维条件搜索 TikTok Shop 商品，支持价格、销量、GMV、佣金、达人带货、店铺类型和履约标签等筛选。支持 `US`、`GB`、`MX`、`ES`、`DE`、`IT`、`FR`、`ID`、`VN`、`MY`、`TH`、`PH`、`BR`、`JP`、`SG`。所有字段均可选，但至少提供 `keyword` 或 `category` 才有明确筛选语义。

## MCP 调用

- MCP Server：`LinkFox`
- Server URL：`https://mcp-tool-gateway.linkfox.com/mcp/any-tool`
- MCP Tool：`proxy_call`
- `toolName`：`fastmoss/productSearch`
- `arguments`：直接传下述业务请求对象，不增加包装层。
- WorkBuddy 自动注入授权信息；调用参数中不得添加认证字段或凭据。
- 先检查 MCP/schema/`isError`，再读取 text/structured content；text 为 JSON 字符串时只解析一次，最后检查下游 `errcode`/`errmsg`、`code`/`msg`。
- MCP/代理错误与下游业务错误必须分层；禁止回退旧 HTTP 网关或旧脚本。
- 失败或空结果不得自动换关键词、改筛选、翻页或重复调用。

## 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---:|---|
| `keyword` | string | 否 | 商品标题模糊搜索关键词。 |
| `region` | string | 否 | 支持的市场代码；未指定时按 `US` 处理并注明。 |
| `category` | string | 否 | 英文 TikTok 类目名称；非英文输入先转换为英文。 |
| `shopType` | integer | 否 | `1`=本地店铺，`2`=跨境店铺。 |
| `isTopSelling` | boolean | 否 | 仅热销商品。 |
| `isNewListed` | boolean | 否 | 仅新上架商品。 |
| `isSshop` | boolean | 否 | 仅 TikTok 全托管商品。 |
| `isFreeShipping` | boolean | 否 | 仅包邮商品。 |
| `isLocalWarehouse` | boolean | 否 | 仅本地仓发货商品。 |
| `unitsSoldRange` | object | 否 | 销量范围，如 `{"min":100,"max":5000}`。 |
| `commissionRateRange` | object | 否 | 佣金率范围，小数表示，如 `{"min":0.05,"max":0.20}`。 |
| `creatorCountRange` | object | 否 | 带货达人数范围，如 `{"min":10,"max":500}`。 |
| `orderField` | string | 否 | `day7_units_sold`、`day7_gmv`、`commission_rate`、`total_units_sold`、`total_gmv` 或 `creator_count`；默认降序。 |
| `page` | integer | 否 | 页码，从 `1` 开始，默认 `1`。 |
| `pageSize` | integer | 否 | 每页条数，默认 `10`，最大 `10`。 |

## 完整 MCP 示例

```json
{
  "toolName": "fastmoss/productSearch",
  "arguments": {
    "keyword": "beauty",
    "region": "US",
    "commissionRateRange": {"min": 0.1},
    "creatorCountRange": {"min": 50},
    "orderField": "creator_count",
    "page": 1,
    "pageSize": 10
  }
}
```

## 响应字段

字段定义仅来自 `skills/linkfox-fastmoss-product-search/references/api.md` 的响应部分。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `total` | integer | 符合条件的总记录数 |
| `products` | array | 商品信息列表（详见下方） |
| `columns` | array | 渲染列定义 |
| `columns[]` | 来源未说明 | 渲染列定义的元素；来源未说明元素结构 |
| `type` | string | 渲染样式类型 |
| `costToken` | integer | 消耗 token 数 |
| `products[].title` | string | 商品标题 |
| `products[].productId` | string | 商品唯一标识ID |
| `products[].region` | string | 市场区域代码 |
| `products[].price` | number | 商品价格 |
| `products[].minPrice` | number | 最低价格 |
| `products[].maxPrice` | number | 最高价格 |
| `products[].currency` | string | 货币代码 |
| `products[].totalSaleCnt` | integer | 累计总销量 |
| `products[].totalSale1dCnt` | integer | 1天销量 |
| `products[].totalSale7dCnt` | integer | 7天销量 |
| `products[].totalSale28dCnt` | integer | 28天销量 |
| `products[].totalSale90dCnt` | integer | 90天销量 |
| `products[].totalSaleGmvAmt` | number | 累计总GMV |
| `products[].totalSaleGmv7dAmt` | number | 7天GMV |
| `products[].totalSaleGmv28dAmt` | number | 28天GMV |
| `products[].totalVideoCnt` | integer | 带货视频数 |
| `products[].totalLiveCnt` | integer | 直播带货数 |
| `products[].totalIflCnt` | integer | 带货达人数 |
| `products[].productCommissionRate` | number | 商品佣金比例（小数，0.10=10%） |
| `products[].productRating` | number | 商品评分 |
| `products[].reviewCount` | integer | 评论数量 |
| `products[].skuCount` | integer | SKU数量 |
| `products[].shopName` | string | 店铺名称 |
| `products[].shopSellerId` | string | 卖家ID |
| `products[].shopTotalUnitsSold` | integer | 店铺总销量 |
| `products[].isCrossBorder` | integer | 是否跨境：1=跨境，0=本地 |
| `products[].isSShopText` | string | 是否全托管店铺（是/否） |
| `products[].freeShippingText` | string | 是否包邮（是/否） |
| `products[].availableDate` | string | 上架时间 |
| `products[].categoryName` | string | 商品品类名称 |
| `products[].salesTrendFlagText` | string | 销售趋势标记 |
| `products[].tiktokUrl` | string | TikTok商品链接 |
| `products[].fastmossUrl` | string | FastMoss商品详情链接 |
| `products[].imageUrl` | string | 商品图片URL |

## 响应处理与错误

先检查 MCP 层，再检查代理层；若代理结果中的 `text` 为 JSON 字符串，只解析一次，最后检查业务状态。成功时读取 `total`、`products` 与 `costToken`。授权、计费和权限异常按 `onboarding.md` 处理；其他异常按实际消息说明。不得用榜单或外部数据补齐缺失字段。

## 展示规则

1. 标注市场、关键词/类目、筛选、排序、页码和 `total`，不要把当前页当成全量。
2. 价格和 GMV 连同 `currency` 展示；佣金小数乘以 100 后展示百分比。
3. `isCrossBorder`、`isSShopText`、`freeShippingText` 和趋势标记按返回值解释。
4. 达人、视频与直播字段只代表数量，不推导内容效果或利润。
5. 调用会消耗积分；翻页或改条件前由用户决定。

## 质量反馈端点

质量反馈使用独立的 `POST https://skill-api.linkfox.com/api/v1/public/feedback`。统一能力的 `skillName` 固定为 `linkfox-wb-fastmoss-tiktok`；规则见 `feedback.md`。
