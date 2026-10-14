# Shopee 单品详情

## 功能与边界

通过一个 Shopee 公共商品直链读取当前 listing 详情，适合核验价格、折扣、销量、库存、SKU 变体、图片、品牌、类目、店铺和评分。它不是关键词搜索或批量筛选。

- 每次只查询一个商品；站点、货币和 locale 从 URL host 推导。
- 仅接受 HTTPS 公共链接，路径必须以 `-i.<数字shopId>.<数字itemId>` 结尾或包含该格式；canonical `/product/<shopId>/<itemId>` URL 不接受。
- 支持 `shopee.sg`、`shopee.co.id`、`shopee.com.my`、`shopee.ph`、`shopee.co.th`、`shopee.tw`、`shopee.vn` 和 `shopee.com.br`。
- 返回请求时公共页面快照；不同站点和 listing 状态会造成字段缺失，越南、巴西和台湾可能返回较轻量记录。
- 不提供关键词搜索、历史趋势、完整评论、情感分析、授权卖家账号、订单、广告、物流或店铺运营。

## MCP 调用

- MCP Server：`LinkFox`
- Server URL：`https://mcp-tool-gateway.linkfox.com/mcp/any-tool`
- 唯一工具：`proxy_call`
- `toolName`：`shopee/product/detail`
- `arguments`：直接使用下述请求参数对象，不增加包装层。
- WorkBuddy 自动注入授权信息；调用参数中不得添加认证字段或凭据。
- 禁止 HTTP fallback。同一任务内相同 `toolName + arguments` 只调用一次；错误、空结果或字段较少时不得自动换站点、替换链接或重试。
- 先检查 MCP 层，再检查代理层；代理结果中的 text 是 JSON 字符串时只解析一次，最后检查下游业务状态。

## 请求参数

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|---:|---|---|
| `productUrl` | string | 是 | — | Shopee HTTPS 商品链接；host 必须在支持列表，端口须省略或为 443，路径须以 `-i.<数字shopId>.<数字itemId>` 结尾 |

工具内部固定使用 URL 自动识别模式。搜索、分类、排序、抓取数量和延迟参数不对外开放。若有效商品数不是 1，或返回 ID 与链接中的 shop ID/item ID 不一致，接口返回业务错误。

## 完整 MCP 示例

```json
{
  "toolName": "shopee/product/detail",
  "arguments": {
    "productUrl": "https://shopee.sg/%28LENECT-OFFICIAL-STORE%29-Flash-I-Aurora-Dual-Highlighter-7.2g-COCOMO-i.9641401.29691169956"
  }
}
```

## 响应字段

字段定义仅来自 `skills/linkfox-shopee-product-detail/references/api.md` 的响应部分。来源以“常用字段”分组列出大量商品字段，但只为响应示例实际出现的字段提供了可确认的 JSON 类型；其余类型均标记为“来源未说明”。

### 统一包装与渲染列

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `errcode` | integer | 业务状态码；`200` 表示成功 |
| `errmsg` | string | 业务状态消息；成功时为 `ok` |
| `data` | array | Shopee 商品数组；成功时固定 1 条 |
| `data[]` | object | 商品对象；对象类型可由来源响应示例确认 |
| `total` | integer | 成功时固定为 `1` |
| `costToken` | integer | 消耗 token |
| `type` | string | 固定为 `tableListWorkbenches` |
| `columns` | array | 根据常用商品字段生成的渲染列 |
| `columns[]` | object | 渲染列对象；对象类型可由来源响应示例确认 |
| `columns[].field` | string | 来源响应示例中的渲染字段名 |
| `columns[].title` | string | 来源响应示例中的渲染标题 |
| `columns[].cellType` | string | 来源响应示例中的单元格类型 |

### `data[]` 商品对象

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `data[].itemId` | string | 标识字段；类型可由来源响应示例确认 |
| `data[].shopId` | string | 标识字段；类型可由来源响应示例确认 |
| `data[].url` | string | 标识字段；类型可由来源响应示例确认 |
| `data[].name` | string | 标识字段；类型可由来源响应示例确认 |
| `data[].brand` | 来源未说明 | 标识字段；来源未说明类型和具体含义 |
| `data[].categoryId` | 来源未说明 | 标识字段；来源未说明类型和具体含义 |
| `data[].categoryBreadcrumb` | 来源未说明 | 标识字段；来源未说明类型和具体含义 |
| `data[].image` | 来源未说明 | 图片视频字段；来源未说明类型和具体含义 |
| `data[].images` | array | 图片视频字段；数组类型可由来源响应示例确认 |
| `data[].images[]` | string | 图片元素；字符串类型可由来源响应示例确认 |
| `data[].videos` | 来源未说明 | 图片视频字段；来源未说明类型和元素结构 |
| `data[].price` | number | 价格字段；类型可由来源响应示例确认 |
| `data[].priceBeforeDiscount` | 来源未说明 | 价格字段；来源未说明类型和具体含义 |
| `data[].priceMin` | 来源未说明 | 价格字段；来源未说明类型和具体含义 |
| `data[].priceMax` | 来源未说明 | 价格字段；来源未说明类型和具体含义 |
| `data[].discountPercent` | number | 价格字段；类型可由来源响应示例确认 |
| `data[].currency` | string | 价格字段；类型可由来源响应示例确认 |
| `data[].sold` | 来源未说明 | 销售评价字段；来源未说明类型和具体含义 |
| `data[].soldDisplayed` | 来源未说明 | 销售评价字段；来源未说明类型和具体含义 |
| `data[].rating` | number | 销售评价字段；类型可由来源响应示例确认 |
| `data[].ratingCount` | 来源未说明 | 销售评价字段；来源未说明类型和具体含义 |
| `data[].ratingDistribution` | 来源未说明 | 销售评价字段；来源未说明类型和嵌套结构 |
| `data[].likedCount` | 来源未说明 | 销售评价字段；来源未说明类型和具体含义 |
| `data[].stock` | 来源未说明 | 库存变体字段；来源未说明类型和具体含义 |
| `data[].tierVariations` | 来源未说明 | 库存变体字段；来源未说明类型和嵌套结构 |
| `data[].models` | array | 库存变体字段；数组类型可由来源响应示例确认 |
| `data[].models[]` | object | 变体对象；对象类型可由来源响应示例确认 |
| `data[].models[].name` | string | 来源响应示例中的变体名称 |
| `data[].models[].model_id` | number | 来源响应示例中的变体 ID；JSON 数字类型 |
| `data[].shopName` | string | 店铺字段；类型可由来源响应示例确认 |
| `data[].shopRating` | 来源未说明 | 店铺字段；来源未说明类型和具体含义 |
| `data[].shopLocation` | string | 店铺字段；类型可由来源响应示例确认 |
| `data[].isMall` | 来源未说明 | 店铺字段；来源未说明类型和具体含义 |
| `data[].isOfficialShop` | 来源未说明 | 店铺字段；来源未说明类型和具体含义 |
| `data[].isShopeeVerified` | 来源未说明 | 店铺字段；来源未说明类型和具体含义 |
| `data[].shop` | 来源未说明 | 嵌套 shop 数据；来源未说明类型和内部字段 |
| `data[].description` | 来源未说明 | 内容字段；来源未说明类型和具体含义 |
| `data[].attributes` | 来源未说明 | 内容字段；来源未说明类型和嵌套结构 |

来源说明还提到“类目、可售状态和商品条件等来源可用字段”以及新增或低频根级字段，但没有给出这些字段的名称、类型或结构，因此不能继续枚举或猜测。字段可能为 `null`。

## 错误与成本

- 成功：统一包装且 `errcode=200`，按 `data[]` 解析。
- URL 为空或非法：要求受支持 host 且含 `-i.<shopId>.<itemId>` 的 HTTPS 链接。
- 商品无效、已移除、站点不匹配、上游错误行、缺少 ID、ID 不一致或有效商品数不是 1：视为业务错误，不自动换站或重复调用。
- 401、402、403 分别按 `onboarding.md` 的授权、计费和权限规则处理；超时、5xx 或其他上游异常如实说明。

每次调用可能消耗积分，实际消耗以 `costToken` 为准。再次查询前说明额外消耗，由用户决定。

## 展示规则

1. 首行展示商品名称、item ID、shop ID、店铺、市场、当前价格、币种、库存和公开销量；缺失项标记 N/A。
2. 当前价、原价、价格区间和折扣按返回值展示，不转换货币。
3. 有 `models` 或 `tierVariations` 时用紧凑表格展示来源实际返回的变体和库存；没有独立价格时明确说明。
4. 商城、官方店和优选标识分开呈现，不从店铺名称推断。
5. 评论正文和历史趋势不在返回范围；图片只展示必要样本。

## Feedback API

该反馈端点与 Shopee 详情 MCP 分离。用户明确表扬、不满、结果与意图不符或发现功能问题时，以 `skillName=linkfox-wb-shopee-product-selection` 上报，不打断业务结果。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- `sentiment`：`POSITIVE`、`NEUTRAL`、`NEGATIVE` 三选一
- `category`：`BUG`、`COMPLAINT`、`SUGGESTION`、`OTHER` 四选一
- `content`：说明用户意图、实际表现和问题/表扬原因，不得包含敏感信息
