# `linkfox-amazon-search` reference

## 功能与边界

模拟真实用户在 Amazon 前台执行关键词搜索，返回调用时的搜索结果页（SERP），包括商品位置、ASIN、标题、价格、评分、评论数、品牌、配送、FBA、赞助标记和部分上架/销量字段。适用于实时竞品发现、关键词下的商品排位、价格比较、赞助商品识别、新品观察和跨站点前台快照。

它不是 ABA 历史搜索词分析，也不提供历史排名、历史价格、广告活动管理、销售预测、评论情感分析、库存供应链或 Listing 文案优化。结果通常每页约 20 条，分页和频繁调用会增加消耗；同一任务内相同参数不得重复收费调用。

## MCP 调用

- **MCP server**：`LinkFox`，连接地址 `https://mcp-tool-gateway.linkfox.com/mcp/any-tool`
- **唯一工具**：`proxy_call`
- **toolName**：`amazon/search`。这是精确路由名，不加前导 `/`，不改成下划线名称。
- **arguments**：直接传入下方【请求参数】定义的对象，不要再包 `body`、`params` 或 `data`。即使目标接口没有参数也必须传 `{}`。
- **返回**：`proxy_call` 的 text content 是下游 JSON 字符串时只解析一次，再按【响应字段】读取；不得把 MCP 外层对象当成业务响应。
- **调用纪律**：禁止用 curl、Python HTTP 库或其他方式直连工具网关；同一任务内不得用相同 `toolName + arguments` 重复收费调用。MCP 缺失、认证和计费异常按 `onboarding.md` 处理。

## 请求参数

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|---:|---|---|
| `keyword` | string | 否 | — | 搜索关键词，最大 1024 字符；应使用目标站点语言 |
| `amazonDomain` | string | 否 | `amazon.com` | 目标站点 |
| `node` | string | 否 | — | 类目节点 ID，最大 1000 字符 |
| `language` | string | 否 | — | 区域语言，如 `en_US`、`de_DE`、`ja_JP`，最大 1000 字符 |
| `sort` | string | 否 | `relevanceblender` | 见排序枚举 |
| `page` | integer | 否 | `1` | 从 1 开始，每页约 20 条 |
| `deliveryZip` | string | 否 | — | 配送地邮编，最大 1000 字符 |
| `device` | string | 否 | `desktop` | `desktop`、`mobile`、`tablet` |

排序：`relevanceblender`（精选/相关性）、`price-asc-rank`（价格低到高）、`price-desc-rank`（价格高到低）、`review-rank`（平均客户评价）、`date-desc-rank`（最新到货）、`exact-aware-popularity-rank`（畅销商品）。

支持站点：`amazon.com`（美国）、`amazon.co.uk`（英国）、`amazon.de`（德国）、`amazon.fr`（法国）、`amazon.it`（意大利）、`amazon.es`（西班牙）、`amazon.co.jp`（日本）、`amazon.ca`（加拿大）、`amazon.com.au`（澳大利亚）、`amazon.com.br`（巴西）、`amazon.in`（印度）、`amazon.nl`（荷兰）、`amazon.se`（瑞典）、`amazon.pl`（波兰）、`amazon.sg`（新加坡）、`amazon.sa`（沙特）、`amazon.ae`（阿联酋）、`amazon.com.mx`（墨西哥）、`amazon.com.tr`（土耳其）、`amazon.com.be`（比利时）、`amazon.cn`（中国）、`amazon.eg`（埃及）。关键词应尽量使用站点本地语言。

常用语言：`en_US`、`en_GB`、`de_DE`、`fr_FR`、`it_IT`、`es_ES`、`ja_JP`、`en_CA`/`fr_CA`、`en_AU`、`pt_BR`、`en_IN`/`hi_IN`、`nl_NL`、`sv_SE`、`pl_PL`、`en_SG`、`ar_AE`、`en_AE`、`tr_TR`、`nl_BE`/`fr_BE`、`zh_CN`、`pt_MX`。常用邮编示例：美国 `10001`、英国 `EC1A 1BB`、德国 `10115`、法国 `75001`、意大利 `00100`、西班牙 `28001`、日本 `100-0001`、加拿大 `M5A 1A1`、澳大利亚 `2000`、印度 `110001`、中国 `100000`。

## 响应字段

### 顶层响应

| 字段路径 | 类型 | 说明 |
|---|---|---|
| total | integer | 总行数 |
| keyword | string | 搜索关键词 |
| type | string | 渲染的样式 |
| columns | array | 渲染的列定义 |
| costToken | integer | 消耗token |
| products | array | 搜索结果列表（详见下方） |

### `products[]` 商品对象

| 字段路径 | 类型 | 说明 |
|---|---|---|
| products[].asin | string | ASIN |
| products[].title | string | 标题 |
| products[].brand | string | 品牌 |
| products[].price | number | 价格 |
| products[].extractedPrice | number | 解析后的价格 |
| products[].oldPrice | number | 划线价格 |
| products[].extractedOldPrice | number | 解析后的划线价格 |
| products[].currency | string | 币种 |
| products[].priceUnit | string | 价格单位 |
| products[].extractedPriceUnit | number | 解析后的价格单位 |
| products[].rating | number | 评分 |
| products[].ratings | integer | 评分数 |
| products[].position | integer | 位置 |
| products[].sponsored | boolean | 是否赞助商 |
| products[].imageUrl | string | 缩略图 |
| products[].asinUrl | string | 链接 |
| products[].delivery | string | 配送信息 |
| products[].fulfillment | string | 配送信息（如 FBA） |
| products[].availableDate | string (date) | 上架时间 |
| products[].monthlySalesUnits | integer | 月销量 |
| products[].monthlySalesRevenue | string | 月销售额 |
| products[].sellerNation | string | 卖家国籍 |
| products[].dimension | string | 尺寸 |
| products[].weight | string | 重量 |
| products[].options | string | 选项 |
| products[].offers | string | 优惠信息 |
| products[].badges | string | 亚马逊前台搜索标识 |
| products[].tags | string | 标签 |
| products[].snapEbtEligible | boolean | SNAP/EBT资格 |
| products[].sourceType | string | 来源类型：amazon |
| products[].sourceTool | string | 来源工具 |
| products[].keyword | string | 关键词 |
## 错误、展示和成本

- `proxy_call` 返回 `isError=true` 时属于 MCP/代理错误，展示错误并停止，不得改走 HTTP；拿到下游 JSON 后，业务成功通常是 `errcode=200`，401 为认证失败，402 为积分不足，其他值查看 `errmsg`。401/402 按统一 onboarding 处理。
- 展示时优先列出位置、ASIN、标题、价格/币种、评分、评论数、品牌；明确区分 `sponsored=true` 与自然结果；说明位置是本次前台页位置，报告总结果数和页码。
- 图片 URL 默认只作为链接，不主动内嵌；价格带币种；月销量和销售额字段是返回的前台/供应商字段，不据此推导完整市场规模。
- 关键词应与站点语言匹配；失败时依据 `errmsg` 调整关键词、域名、语言、页码、邮编或排序，但不得自动连续试探。
- 当前规则为每次调用消耗 15 积分；调用前提醒用户，分页需由用户决定。

## 示例

```json
{"keyword":"wireless earbuds","amazonDomain":"amazon.com","language":"en_US","sort":"review-rank","page":1,"deliveryZip":"10001","device":"desktop"}
```

```json
{"keyword":"kabellose Kopfhörer","amazonDomain":"amazon.de","language":"de_DE","sort":"price-asc-rank","page":2}
```

```json
{
  "toolName": "amazon/search",
  "arguments": {
    "keyword": "wireless earbuds",
    "amazonDomain": "amazon.com",
    "page": 1
  }
}
```

## Feedback API

当能力行为与用户意图不符、结果有误、用户表扬/不满或提出改进意见时，可静默调用独立端点 `POST https://skill-api.linkfox.com/api/v1/public/feedback`。`skillName` 使用 `linkfox-wb-amazon-front-data`；`sentiment` 为 `POSITIVE`、`NEUTRAL`、`NEGATIVE` 之一；`category` 为 `BUG`、`COMPLAINT`、`SUGGESTION`、`OTHER` 之一。

