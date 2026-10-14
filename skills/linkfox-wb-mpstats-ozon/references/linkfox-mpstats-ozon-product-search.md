# linkfox-mpstats-ozon-product-search

## 能力说明

按 Ozon 俄罗斯站实际使用的俄语或拉丁形式搜索关键词，或按 Ozon SKU 列表反查商品身份。它适合发现商品并解析后续查询所需的 `productId`、品牌和卖家；不提供价格、销量、评分、库存、周转或排名指标。关键词至少一个 `keyword`/`productIds`，两者可同时传入。英文/中文关键词应先翻译为俄语并注明。

不适用于品牌、类目或卖家维度的指标下钻；不适用于单 SKU 分日走势。单次调用没有分页、排序和筛选参数，上游最多约返回 36 条，结果超过返回量时应收窄关键词、SKU 或日期窗口。

## MCP 调用与请求参数

- 响应字段来源：`skills/linkfox-mpstats-ozon-product-search/references/api.md`。仅从该文件核对并恢复响应字段。
- MCP server：`LinkFox`
- 唯一工具：`proxy_call`
- `toolName`：`mpstats/ozon/productSearch`
- `arguments`：直接使用本 reference 请求参数对象，不包裹 `body`、`params` 或 `data`。
- WorkBuddy 自动注入 Authorization；禁止传入 headers、Key、token、JWT、手机号或其他凭证。
- 先检查 MCP schema 与 `isError`；代理成功后读取 text/structured content，text 为 JSON 字符串时只解析一次，再检查下游业务代码与消息。
- MCP 缺失或失败时停止，不得 HTTP fallback。收费调用失败、空结果或不理想时不得自动重试；同一任务相同 `toolName + arguments` 只调用一次。

```json
{
  "toolName": "mpstats/ozon/productSearch",
  "arguments": {
    "keyword": "кроссовки"
  }
}
```

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `keyword` | string | 与 `productIds` 至少一个 | 俄语搜索关键词，如 `кроссовки` |
| `productIds` | array<integer\|string> | 与 `keyword` 至少一个 | Ozon SKU 列表 |
| `startDate` | string | 否 | `YYYY-MM-DD`；缺省按一年前；最晚昨日 |
| `endDate` | string | 否 | `YYYY-MM-DD`；缺省按昨日；不能为今天/未来 |

## 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| code | string | 返回码（字符串），`"200"` 表示成功 |
| msg | string | 消息；成功为 `ok`，失败为错误描述 |
| total | integer | 命中总数 |
| products | array | 商品列表（详见下方） |
| columns | array | 渲染列定义 |
| costTime | integer | 接口耗时（毫秒） |
| costToken | integer | 消耗 Token 数量 |
| type | string | 响应类型 |

### products[*] 商品对象字段（10 个）

按后端 `OzonProductSearchItem` DTO 定义（同步日期 2026-05-11）。**search 端点为身份解析用途，不返回价/销/评/库存/周转/排名等业务指标**——这是硬契约，不是 sparse payload。如果需要那些指标：

- 单/批 SKU 全量卡：改用 `productDetail`（36 字段，含价格、销量、收入、周期对比等）
- 维度下钻：改用 `brandProducts` / `categoryProducts` / `sellerProducts`（39 字段全量商品卡）

| 字段 | 类型 | 说明 |
|------|------|------|
| productId | integer | SKU ID |
| title | string | 商品名称（俄语） |
| productPageUrl | string | 商品页 URL |
| imageUrl | string | 主图 URL |
| brand | string | 品牌名 |
| brandId | integer | 品牌 ID |
| sellerName | string | 卖家名 |
| sellerId | integer | 卖家 ID |
| sourceType | string | 数据源标识，恒为 `ozon` |
| sourceTool | string | 来源工具名，恒为 `MPSTATS-Ozon商品搜索` |

## 错误与展示

- `200`：解析 `products`；`401`：认证失败；`402`：积分或余额不足；其他非 200 值读取 `msg`/`errmsg`，常见原因是缺少 keyword/productIds、非俄语关键词或日期超过昨日。
- 展示优先列 `productId/title/brand/sellerName`，保留俄语原文；`total` 大于实际返回量时说明无分页并建议收窄查询。

## Feedback API

用户明确表达满意、不满、结果不符或改进建议时，按响应后调用 `POST https://skill-api.linkfox.com/api/v1/public/feedback`，body 使用本能力标识：

```json
{"skillName":"linkfox-mpstats-ozon-product-search","sentiment":"POSITIVE|NEUTRAL|NEGATIVE","category":"BUG|COMPLAINT|SUGGESTION|OTHER","content":"记录用户表达与实际现象"}
```

认证/计费处理见 `references/onboarding.md`。

