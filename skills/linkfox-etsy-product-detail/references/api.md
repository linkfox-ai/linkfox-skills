# Etsy 商品详情 接口说明

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

## 接口：Etsy 商品详情

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/etsy/product/detail`

### 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| productUrl | string | 是 | - | Etsy 商品 HTTPS 直链。不得含 userinfo；Host 必须为 `etsy.com` 或其子域，端口须省略或为 `443`；路径须为 `/listing/<数字ID>`，最多再带一个非空标题 slug，可带尾斜杠与查询参数 |

不接受 Etsy 搜索页、店铺页、非 Etsy 域名或缺少数字 listing ID 的 URL。每次调用仅查询一个 Listing；若上游返回的有效商品数量不是 1，接口返回业务错误。

#### 认证与运行兼容

| 项目 | 类型 | 必填 | 默认值 / 说明 |
|------|------|------|------|
| LINKFOX_TOOL_GATEWAY | 环境变量 | 否 | 默认 `https://tool-gateway.linkfox.com`；去除结尾斜杠后拼接端点 |
| LINKFOX_AGENT_API_KEY | 环境变量 | 条件必填 | 优先使用；为空时回退到 `LINKFOXAGENT_API_KEY`，两者均为空则按认证指引处理 |
| LINKFOXAGENT_API_KEY | 环境变量 | 条件必填 | `LINKFOX_AGENT_API_KEY` 为空时使用的备用密钥变量 |
| SESSION_ID / MESSAGE_ID / MODE_ID / APP_NAME | 环境变量 / 请求头 | 否 | 从同名环境变量原样透传，未配置时为空字符串；`SESSION_ID` 同时用于本地任务数据聚合 |
| --inline | CLI flag | 否 | 强制打印完整响应，同时仍保存文件 |
| --no-cache | CLI flag | 否 | 本次禁用响应缓存读取和写入 |

CLI 用法为 `python scripts/etsy_product_detail.py '<JSON 参数>' [--inline] [--no-cache]`。脚本在请求前校验 JSON 对象和商品直链，不改写 URL、查询参数或已编码字符。

默认 24 小时本地缓存路径为 `<cwd>/linkfox/.cache/linkfox-etsy-product-detail/linkfox-etsy-product-detail-<hash>.json`，其中 `<hash>` 为对 `ensure_ascii=False, sort_keys=True` 的参数 JSON 做 SHA256 后取前 16 位；有效期按文件修改时间计算。缓存由公共调用器单层实现，业务封装不叠加缓存。所有响应均可写入缓存，包括错误响应；缓存命中不代表接口业务成功，仍须按响应码及业务规则检查。缓存损坏或过期时重新查询；使用 `--no-cache` 时不读写响应缓存。

完整响应和会话元数据固定保存在当前工作目录的 `linkfox/`；忽略其他输出根目录候选，不回退到家目录或临时目录。请求前检查完整会话目录及 `data/` 的可写性，路径不可写时提前报错；若请求后仍保存失败或文件不完整，脚本返回非零退出码，不自动重新请求，已保存的缓存仍可复用。缺省 `SESSION_ID` 时使用进程内稳定的自动会话标识。

#### 使用限制

- 页面结构变化可能导致字段缺失、空字符串、null 或偶发误识别。`star`、价格、配送估算、店铺资料与徽章不保证每个 Listing 都返回。
- 仅提供公开页面的当前快照和评论聚合信息，不提供逐条买家评论、历史价格、Etsy 关键词排名或保证准确的销量估算。
- 本接口不执行关键词搜索、批量筛选、独立店铺检索或排名，也不执行刊登及订单等卖家账号操作。

### 响应结构

成功响应为 LinkFox 统一包装：

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer | 业务状态码；`200` 表示成功 |
| errmsg | string | 业务状态消息；成功时为 `ok` |
| data | array | 商品对象数组；成功时固定 1 条 |
| total | integer | 成功时固定为 `1` |
| costToken | integer | 消耗 token |
| type | string | 固定为 `tableListWorkbenches` |
| columns | array | 根据商品顶层字段生成的渲染列定义 |

#### data[*] 商品对象

| 字段 | 类型 | 说明 |
|------|------|------|
| productId | string | Etsy listing ID |
| shopId | string | 店铺 ID |
| shopUrl | string | 店铺 URL；页面异常时可能为空或误识别 |
| shopSales | string | 店铺公开销量文本 |
| shopName | string | 店铺名称；页面异常时可能为空或误识别 |
| productUrl | string | 商品 URL |
| searchPosition | string | 来源搜索位置；直链查询通常为空 |
| image | string | 主图 URL |
| images | array | 图片 URL 列表 |
| maxQuantity | integer | 页面报告的最大可购数量 |
| variants | array | 商品变体；无变体时为空数组 |
| title | string | 商品标题 |
| description | array | 描述段落列表 |
| deliveryDaysMin | integer/null | 预计送达天数下限；来源为空时可能为 null 或不返回该字段 |
| deliveryDaysMax | integer/null | 预计送达天数上限；来源为空时可能为 null 或不返回该字段 |
| shopReviews | integer | 店铺评论数量 |
| reviews | integer | 当前 Listing 评论数量 |
| star | string | 当前评分，可能为空字符串 |
| highlightsTags | array | 买家反馈亮点标签 |
| reviewsTags | array | 评论标签及频次对象 |
| yearsOnEtsy | string | 店铺在 Etsy 的公开年限 |
| hasRatingsBadge | boolean | 是否有评分徽章 |
| hasConvosBadge | boolean | 是否有沟通徽章 |
| hasShippingBadge | boolean | 是否有配送徽章 |
| reviewsScores | object | 动态评论分项；键和值随页面而变 |
| category | string | 类目面包屑 |
| price | string | 当前价格；可能为空 |
| lowPrice | string | 价格区间下限；可能为空 |
| highPrice | string | 价格区间上限；可能为空 |
| oldPrice | string | 原价；可能为空 |
| countryShippingFrom | string | 发货国家/地区 |
| currency | string | 币种代码 |
| moreLikeUrl | string | 相似推荐链接，可能为空 |

接口只返回评论数量、标签与聚合分数，不返回逐条评论内容。

#### columns[*] 渲染列定义

| 字段 | 类型 | 说明 |
|------|------|------|
| filterable | boolean | 是否支持过滤 |
| cellType | string | 单元格类型，示例为 `text` |
| field | string | 对应商品字段名，示例为 `productId` |
| sortable | boolean | 是否支持排序 |
| title | string | 展示标题，示例为“商品 ID” |

`images` 是图片 URL 列表，`description` 是描述段落列表。`variants`、`highlightsTags`、`reviewsTags` 的元素结构及 `reviewsScores` 的动态键和值类型以实际返回为准；保留返回结构，不补造嵌套字段。

### 响应示例

示例（部分商品字段、描述、图片与 `columns` 已截短）：

```json
{
  "errcode": 200,
  "errmsg": "ok",
  "data": [
    {
      "productId": "1710567856",
      "shopId": "35055979",
      "shopName": "",
      "productUrl": "https://www.etsy.com/listing/1710567856/its-okay-to-make-some-mistakes-shirt",
      "title": "It's Okay To Make Some Mistakes Shirt...",
      "images": ["https://i.etsystatic.com/..."],
      "maxQuantity": 952,
      "variants": [],
      "reviews": 134,
      "star": "",
      "lowPrice": "9.76",
      "highPrice": "32.55",
      "currency": "EUR"
    }
  ],
  "total": 1,
  "costToken": 7000,
  "type": "tableListWorkbenches",
  "columns": [
    {
      "filterable": true,
      "cellType": "text",
      "field": "productId",
      "sortable": true,
      "title": "商品 ID"
    }
  ]
}
```

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

| 情况 | 表现 | 处理建议 |
|------|------|----------|
| productUrl 为空或 URL 不合法 | 网关业务错误 | 核对完整 Etsy Listing HTTPS URL；脚本会在请求前拦截 |
| 非 Listing 页面、非 Etsy 域名或路径层级过深 | 网关业务错误 | 按请求参数中的 host、端口和路径要求核对 |
| Listing 不存在、不可访问或返回空数组 | 网关业务错误，不应当作“成功空列表” | 核对链接；不要自动改链接连续试探 |
| 上游返回多个有效 Listing | 网关业务错误 | 视为上游结果异常；本接口不截断、不返回批量结果 |
| 超时或上游异常 | 连接错误、5xx 或业务错误 | 告知用户；不要连续自动重试产生额外费用 |

### curl 示例

```bash
API_KEY="${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}"
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/etsy/product/detail" \
  -H "Authorization: ${API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -H "SESSION_ID: ${SESSION_ID:-}" \
  -H "MESSAGE_ID: ${MESSAGE_ID:-}" \
  -H "MODE_ID: ${MODE_ID:-}" \
  -H "APP_NAME: ${APP_NAME:-}" \
  -d '{
    "productUrl": "https://www.etsy.com/listing/1710567856/its-okay-to-make-some-mistakes-shirt"
  }'
```


## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-etsy-product-detail",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```