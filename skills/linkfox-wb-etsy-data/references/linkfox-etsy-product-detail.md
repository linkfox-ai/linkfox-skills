# `linkfox-etsy-product-detail` 参考

## 能力说明

查询一个 Etsy Listing 直链的当前公开商品详情，用于 Listing 内容提取、价格和变体审查、竞品页面拆解以及店铺/评论概况查看。结果是结构化公开页面快照，不是搜索、批量筛选或逐条评论接口。

## 输入边界

- `productUrl` 必填，必须是 Etsy HTTPS URL：Host 为 `etsy.com` 或其子域，默认 HTTPS 端口或 `443`，路径为 `/listing/<数字ID>`，最多再带一个非空标题 slug，可带尾斜杠和查询参数。
- 不接受 Etsy 搜索页、店铺页、非 Etsy Host、包含 userinfo 的 URL、路径层级过深或缺少数字 Listing ID 的 URL。
- 一次调用只查询一个 Listing；若上游有效商品数不是 1，接口返回业务错误。
- 页面结构变化可能造成字段缺失、空字符串、`null` 或偶发误识别；调用方必须如实展示，不要静默修复。

## MCP 调用

- **MCP server**：`LinkFox`
- **唯一工具**：`proxy_call`
- **toolName**：`etsy/product/detail`
- **arguments**：直接使用下表请求参数对象，不增加 `body`、`data`、`params` 或凭证字段。
- WorkBuddy 自动注入 Authorization；配置和 `arguments` 不得加入 headers、API Key、token、JWT 或手机号。
- 先检查 MCP/schema/`isError`，再读取代理内容；text JSON 只解析一次，最后检查下游 `errcode`、`errmsg`。
- MCP 缺失或失败时停止，不得 HTTP fallback；相同 `toolName + arguments` 不得重复收费调用，失败、空结果或返回不理想时不得自动重试。

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---:|---|
| `productUrl` | string | 是 | 合法 Etsy Listing HTTPS 直链，格式见【输入边界】 |

示例：

```json
{"productUrl":"https://www.etsy.com/listing/1710567856/its-okay-to-make-some-mistakes-shirt"}
```

### 响应包装

| 字段 | 类型 | 说明 |
|---|---|---|
| `errcode` | integer | 业务状态码；`200` 表示成功 |
| `errmsg` | string | 业务状态消息；成功时为 `ok` |
| `data` | array | 商品对象数组；成功时固定 1 条 |
| `total` | integer | 成功时固定为 `1` |
| `costToken` | integer | 消耗 token |
| `type` | string | 固定为 `tableListWorkbenches` |
| `columns` | array | 根据商品顶层字段生成的渲染列定义 |

### `data[]` 商品对象

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `data[].productId` | string | Etsy listing ID |
| `data[].shopId` | string | 店铺 ID |
| `data[].shopUrl` | string | 店铺 URL；页面异常时可能为空或误识别 |
| `data[].shopSales` | string | 店铺公开销量文本 |
| `data[].shopName` | string | 店铺名称；页面异常时可能为空或误识别 |
| `data[].productUrl` | string | 商品 URL |
| `data[].searchPosition` | string | 来源搜索位置；直链查询通常为空 |
| `data[].image` | string | 主图 URL |
| `data[].images` | array | 图片 URL 列表 |
| `data[].images[]` | string | 来源示例中的图片 URL 元素 |
| `data[].maxQuantity` | integer | 页面报告的最大可购数量 |
| `data[].variants` | array | 商品变体；无变体时为空数组 |
| `data[].variants[]` | 来源未说明 | 商品变体元素；来源未说明内部字段 |
| `data[].title` | string | 商品标题 |
| `data[].description` | array | 描述段落列表 |
| `data[].description[]` | 来源未说明 | 描述段落元素 |
| `data[].deliveryDaysMin` | integer/null | 预计送达天数范围；来源为空时可能为 null 或不返回该字段 |
| `data[].deliveryDaysMax` | integer/null | 预计送达天数范围；来源为空时可能为 null 或不返回该字段 |
| `data[].shopReviews` | integer | 店铺评论数量 |
| `data[].reviews` | integer | 当前 Listing 评论数量 |
| `data[].star` | string | 当前评分，可能为空字符串 |
| `data[].highlightsTags` | array | 买家反馈亮点标签 |
| `data[].highlightsTags[]` | 来源未说明 | 买家反馈亮点标签元素 |
| `data[].reviewsTags` | array | 评论标签及频次对象 |
| `data[].reviewsTags[]` | 来源未说明 | 评论标签及频次对象；来源未说明内部字段 |
| `data[].yearsOnEtsy` | string | 店铺在 Etsy 的公开年限 |
| `data[].hasRatingsBadge` | boolean | 是否有评分徽章 |
| `data[].hasConvosBadge` | boolean | 是否有沟通徽章 |
| `data[].hasShippingBadge` | boolean | 是否有配送徽章 |
| `data[].reviewsScores` | object | 动态评论分项；键和值随页面而变 |
| `data[].category` | string | 类目面包屑 |
| `data[].price` | string | 价格字段，部分字段可能为空 |
| `data[].lowPrice` | string | 价格字段，部分字段可能为空 |
| `data[].highPrice` | string | 价格字段，部分字段可能为空 |
| `data[].oldPrice` | string | 价格字段，部分字段可能为空 |
| `data[].countryShippingFrom` | string | 发货国家/地区 |
| `data[].currency` | string | 币种代码 |
| `data[].moreLikeUrl` | string | 相似推荐链接，可能为空 |

### `columns[]` 元素

以下字段由来源响应示例明确给出；字段说明未提供。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `columns[]` | object | 来源示例中的渲染列定义元素 |
| `columns[].filterable` | boolean | 来源未说明 |
| `columns[].cellType` | string | 来源未说明 |
| `columns[].field` | string | 来源未说明 |
| `columns[].sortable` | boolean | 来源未说明 |
| `columns[].title` | string | 来源未说明 |

接口只返回评论数量、标签与聚合分数，不返回单条买家评论。

## MCP 调用示例

```json
{
  "toolName": "etsy/product/detail",
  "arguments": {
    "productUrl": "https://www.etsy.com/listing/1710567856/its-okay-to-make-some-mistakes-shirt"
  }
}
```

## 错误处理、展示和限制

| 情况 | 处理 |
|---|---|
| `productUrl` 为空或不合法 | 提示使用合法 Etsy Listing HTTPS 直链 |
| 非 Listing 页、非 Etsy Host、路径过深或无数字 ID | 修正 URL，不要自动改链接连续试探 |
| Listing 不存在、不可访问或空数组 | 视为业务错误，不当作成功空列表 |
| 上游返回多个有效 Listing | 视为上游异常；不截断、不转为批量结果 |
| 401 | 按 `references/onboarding.md` 处理认证 |
| 402 | 按 `references/onboarding.md` 处理积分/余额 |
| 超时、5xx 或上游异常 | 告知用户并建议稍后人工重试，不自动连续重试 |

展示时先给标题、Listing ID、店铺名、类目、价格区间和币种；主图内联展示，其余图片默认只给数量；有变体和数量才展示对应字段；只有当两个送达天数都有意义时展示预计送达。不要归一化或换算价格字符串，不把 `star`、店铺字段、徽章或动态评分缺失值补全为推断值。

该接口不提供历史价格、关键词排名、保证性销量估计、Listing 创建/编辑、店铺运营、订单和逐条评论情感分析。

## Feedback API

该 API 与商品详情网关分离，仅在用户反馈结果不符合意图、结果缺失、用户表扬/不满或提出改进建议时按需上报，不中断当前结果。发布为统一能力后，反馈名称使用当前 WorkBuddy 能力名；若接收方要求保留详情子能力标识，则使用 `linkfox-etsy-product-detail`，不得把反馈请求发到 Etsy 数据端点。

- **端点**：`POST https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求头**：`Content-Type: application/json`
- **请求体**：

```json
{
  "skillName": "linkfox-wb-etsy-data",
  "sentiment": "NEGATIVE",
  "category": "BUG",
  "content": "The public listing detail omitted the delivery estimate requested by the user."
}
```

- `sentiment`：`POSITIVE`、`NEUTRAL`、`NEGATIVE` 三选一。
- `category`：`BUG`、`COMPLAINT`、`SUGGESTION`、`OTHER` 四选一。
- `content`：简述用户意图、实际表现及问题或表扬原因。

## 积分

详情查询会消耗积分，实际以响应 `costToken` 为准；重复查询其他 Listing 或追加调用分别计费，继续前应让用户知晓额外消耗。
