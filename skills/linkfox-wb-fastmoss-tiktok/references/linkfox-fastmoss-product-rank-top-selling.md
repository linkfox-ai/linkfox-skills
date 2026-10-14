# `linkfox-fastmoss-product-rank-top-selling` 参考

## 功能与边界

查看 TikTok Shop 指定市场的商品热销榜，按日、周或月观察销量、GMV 和增长率，并可按类目和排序字段缩小范围。支持 `US`、`GB`、`MX`、`ES`、`ID`、`VN`、`MY`、`TH`、`PH`。榜单存在 T+1 统计延迟；关键词或精细条件筛选应改用商品搜索端点。

## MCP 调用

- MCP Server：`LinkFox`
- Server URL：`https://mcp-tool-gateway.linkfox.com/mcp/any-tool`
- MCP Tool：`proxy_call`
- `toolName`：`fastmoss/productRankTopSelling`
- `arguments`：直接传下述业务请求对象，不增加包装层。
- WorkBuddy 自动注入授权信息；调用参数中不得添加认证字段或凭据。
- 先检查 MCP/schema/`isError`，再读取 text/structured content；text 为 JSON 字符串时只解析一次，最后检查下游 `errcode`/`errmsg`、`code`/`msg`。
- MCP/代理错误与下游业务错误必须分层；禁止回退旧 HTTP 网关或旧脚本。
- 失败或空结果不得自动改日期、类目、排序、页码、市场或重复调用。

## 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---:|---|
| `region` | string | 是 | 市场代码：`US`、`GB`、`MX`、`ES`、`ID`、`VN`、`MY`、`TH`、`PH`。 |
| `dateInfo` | object | 是 | 日期规格，必须包含 `type` 与 `value`。 |
| `dateInfo.type` | string | 是 | `day`、`week` 或 `month`。 |
| `dateInfo.value` | string | 是 | `day` 使用 `YYYY-MM-DD`；`week` 使用 `YYYY-周数`；`month` 使用 `YYYY-MM`。 |
| `category` | string | 否 | 英文 TikTok 类目名称；非英文输入先转换为英文。 |
| `orderby` | object | 否 | 排序对象，包含 `field` 与 `order`；默认降序。 |
| `orderby.field` | string | 否 | `units_sold`、`gmv`、`total_units_sold`、`total_gmv` 或 `growth_rate`。 |
| `orderby.order` | string | 否 | `desc` 或 `asc`。 |
| `page` | integer | 否 | 页码，从 `1` 开始，默认 `1`。 |
| `pageSize` | integer | 否 | 每页条数，默认 `10`，最大 `10`。 |

必须同时验证 `dateInfo.type` 和 `dateInfo.value` 的格式。`category` 接受类目名，不应传入未经确认的类目 ID。

## 完整 MCP 示例

```json
{
  "toolName": "fastmoss/productRankTopSelling",
  "arguments": {
    "region": "US",
    "dateInfo": {"type": "day", "value": "2026-04-15"},
    "orderby": {"field": "units_sold", "order": "desc"},
    "page": 1,
    "pageSize": 10
  }
}
```

## 响应字段

字段定义仅来自 `skills/linkfox-fastmoss-product-rank-top-selling/references/api.md` 的响应部分。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `errcode` | integer | 业务状态码，`200` 表示成功 |
| `errmsg` | string | 业务状态说明 |
| `page` | integer | 当前页码 |
| `pageSize` | integer | 当前每页条数 |
| `total` | integer | 记录数 |
| `products` | array | 热销商品列表（见下方商品对象） |
| `columns` | array | 渲染的列 |
| `columns[]` | 来源未说明 | 渲染列的元素；来源未说明元素结构 |
| `type` | string | 渲染的样式 |
| `costTime` | integer | 接口耗时（毫秒） |
| `costToken` | integer | 消耗 token；部分响应可能省略 |
| `matchedCategoryIdPath` | string | 匹配到的类目 ID 路径；传入 `category` 时可能返回 |
| `matchedCategoryNamePath` | string | 匹配到的类目名称路径；传入 `category` 时可能返回 |
| `products[].title` | string | 商品名称 |
| `products[].productId` | string | 商品 ID |
| `products[].region` | string | 区域代码 |
| `products[].price` | number | 商品价格 |
| `products[].minPrice` | number | 最低价格；仅价格区间商品返回 |
| `products[].maxPrice` | number | 最高价格；仅价格区间商品返回 |
| `products[].currency` | string | 货币符号或标识 |
| `products[].totalSaleCnt` | integer | 总销量 |
| `products[].totalSale1dCnt` | integer | 近1天销量（dateType=day 时返回） |
| `products[].totalSale7dCnt` | integer | 近7天销量（dateType=week 时返回） |
| `products[].totalSale30dCnt` | integer | 近30天销量（dateType=month 时返回） |
| `products[].totalSaleGmvAmt` | number | 总销售额 |
| `products[].totalSaleGmv1dAmt` | number | 近1天销售额（dateType=day 时返回） |
| `products[].totalSaleGmv7dAmt` | number | 近7天销售额（dateType=week 时返回） |
| `products[].totalSaleGmv30dAmt` | number | 近30天销售额（dateType=month 时返回） |
| `products[].growthRate` | number | 增长率（百分比） |
| `products[].shopName` | string | 店铺名称 |
| `products[].shopTotalUnitsSold` | integer | 店铺总销量 |
| `products[].shopSellerId` | string | 店铺卖家 ID |
| `products[].categoryName` | string | 商品类目 |
| `products[].categoryIds` | array | 商品类目 ID 路径（一级至三级） |
| `products[].categoryIds[]` | 来源未说明 | 商品类目 ID 路径元素；来源未说明元素类型 |
| `products[].productCommissionRate` | number | 商品佣金比例（基点，1000=10%） |
| `products[].imageUrl` | string | 商品图片 URL |
| `products[].coverUrl` | array | 商品封面图 URL 列表 |
| `products[].coverUrl[]` | 来源未说明 | 商品封面图 URL 列表元素；来源未说明元素类型 |
| `products[].shopAvatar` | string | 店铺头像 URL |
| `products[].sourceTool` | string | 来源工具标识 |
| `products[].sourceType` | string | 商品来源类型 |
| `products[].offShelvesText` | string | 是否下架（"是"=已下架，"否"=在售） |

## 响应处理与错误

先检查 MCP 层，再检查代理层；若代理结果中的 `text` 为 JSON 字符串，只解析一次，最后用 `errcode` 和 `errmsg` 判断业务结果。`errcode=200` 表示成功。授权、计费和权限异常按 `onboarding.md` 处理；其他异常按实际消息说明。与日期粒度不对应的周期字段可能缺失，标记为 N/A，不得用总量或其他周期替代。

## 展示规则

1. 标注市场、日期粒度、类目、排序、页码、当前页条数和 `total`。
2. 价格与 GMV 连同 `currency` 展示；佣金基点除以 100 后展示百分比。
3. `growthRate` 标注百分比及日期粒度，`offShelvesText` 按来源定义解释。
4. 说明 T+1 延迟，不推断下架原因、利润或未来销量。
5. 调用会消耗积分；翻页、改条件或切换端点前由用户决定。

## 质量反馈端点

质量反馈使用独立的 `POST https://skill-api.linkfox.com/api/v1/public/feedback`。统一能力的 `skillName` 固定为 `linkfox-wb-fastmoss-tiktok`；规则见 `feedback.md`。
