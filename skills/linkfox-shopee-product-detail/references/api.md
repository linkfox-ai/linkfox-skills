# Shopee 商品详情 接口说明

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

## 接口：商品详情查询

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/shopee/product/detail`

### 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| productUrl | string | 是 | - | Shopee HTTPS 商品链接；host 必须是下述 8 个站点之一，端口须省略或为 443，路径须以 `-i.<数字shopId>.<数字itemId>` 结尾。 |

#### 参数约束与接口使用限制

- 支持的 host：`shopee.sg`、`shopee.co.id`、`shopee.com.my`、`shopee.ph`、`shopee.co.th`、`shopee.tw`、`shopee.vn`、`shopee.com.br`。
- 不接受 `/product/<shopId>/<itemId>` 形式的链接。站点、币种与语言环境由 URL host 推导，不额外传入站点参数。
- 仅接受上表中的公共请求参数。工具内部固定使用 URL 自动识别模式；搜索、分类、排序、抓取数量和延迟参数不对外开放。
- 每次调用仅查询一个商品；不支持关键词搜索、排行、批量筛品、历史价格或库存趋势，也不提供已授权卖家商品、订单、促销或账号操作。
- 上游有效商品数量必须为 1，并且返回的 `shopId`、`itemId` 必须与链接一致；否则为业务错误，不截断成单条，也不返回批量结果。
- 不返回逐条买家评论；`ratingCount`、`ratingDistribution` 仅为来源可用的聚合指标。
- `models` 可提供变体库存，但不保证每个变体都有独立价格。
- 字段取决于站点、商品状态、卖家及来源页面完整性。印度尼西亚、新加坡、马来西亚、泰国和菲律宾的云端来源通常较丰富；越南、巴西和台湾可能只返回轻量记录。

#### 透传请求头

除公共请求头外，脚本从同名环境变量读取下列请求头，未配置时发送空字符串。

| 请求头 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| SESSION_ID | string | 否 | 空字符串 | 会话标识。 |
| MESSAGE_ID | string | 否 | 空字符串 | 消息标识。 |
| MODE_ID | string | 否 | 空字符串 | 模式标识。 |
| APP_NAME | string | 否 | 空字符串 | 应用名称。 |

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 默认值 | 说明 |
|-------------|------|------|--------|------|
| JSON 参数 | object | 是 | - | 第一个位置参数，包含上表中的 `productUrl`。 |
| --inline | CLI flag | 否 | 关闭 | 保存完整响应并强制全量打印。 |
| --no-cache | CLI flag | 否 | 关闭 | 同时跳过缓存读取和写入；实际请求会产生新的消耗。 |
| --help / -h | CLI flag | 否 | - | 输出本地帮助，不请求接口。 |

- 脚本入口：`python scripts/shopee_product_detail.py '<JSON 参数>' [--inline] [--no-cache]`。
- 认证优先使用 `LINKFOX_AGENT_API_KEY`，回退到 `LINKFOXAGENT_API_KEY`。基础地址取 `LINKFOX_TOOL_GATEWAY`，默认 `https://tool-gateway.linkfox.com`，去掉末尾 `/`。超时为 150s，不自动重试商品查询。
- 脚本使用公共调用器提供的单层 24 小时缓存。缓存位于 `<cwd>/linkfox/.cache/linkfox-shopee-product-detail/`，文件名为技能名加参数 JSON（键排序、保留中文）的 SHA-256 前 16 位；缓存采用裸 JSON 格式，命中时添加 `_cache.hit=true` 标记。缓存不筛选业务成功状态，错误响应也可能命中；应按响应码规则解释，不把缓存命中视为成功或最新抓取。
- 完整响应与会话索引保存在当前工作目录的 `linkfox/` 下；业务入口先解析 JSON，再在请求前检查根目录、实际会话的 `data/` 目录和元数据可写；路径受阻时直接报错，禁止回退到 `/tmp`、家目录或其他工作区。参数语法错误时不创建缓存或会话目录。缓存命中同样保存本次完整输出。默认 8000 字节以内打印全量，超出仅打印摘要；`--inline` 始终打印全量。

### 响应结构

成功响应为 LinkFox 统一包装。字段定义见下表；实际响应状态先按「响应码规则」判断，不把示例中的 `200` 作为额外的唯一成功条件。

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer | 业务状态码；`200` 表示成功，状态判断遵循公共规则。 |
| errmsg | string | 业务状态消息；成功时为 `ok`。 |
| data | array | Shopee 商品数组；成功时固定 1 条。 |
| total | integer | 成功时固定为 `1`。 |
| costToken | integer | 消耗 token，保留来源原值。 |
| type | string | 固定为 `tableListWorkbenches`。 |
| columns | array | 根据常用商品字段生成的渲染列，已知成员字段见下表。 |

#### data[*] 商品对象

商品字段均可能缺失或为 `null`。下表中标明「来源未限定」的字段类型不固定，应保留实际类型和嵌套结构，不据名称强制转换。来源新增或低频顶层字段保留在对象根级。

| 字段 | 类型 | 说明 |
|------|------|------|
| itemId | string / number | 商品 ID；示例为字符串，与 URL 中的 itemId 对应。 |
| shopId | string / number | 店铺 ID；示例为字符串，与 URL 中的 shopId 对应。 |
| url | string | 商品链接。 |
| name | string | 商品标题。 |
| brand | 来源未限定 | 品牌信息。 |
| categoryId | 来源未限定 | 类目 ID，保留来源表示。 |
| categoryBreadcrumb | 来源未限定 | 类目导航路径，保留来源结构。 |
| image | 来源未限定 | 主图信息。 |
| images | array | 商品图片列表；示例为 URL 字符串数组。 |
| videos | 来源未限定 | 视频内容及来源结构。 |
| price | number | 当前价格。 |
| priceBeforeDiscount | 来源未限定 | 折扣前价格。 |
| priceMin | 来源未限定 | 最低价格。 |
| priceMax | 来源未限定 | 最高价格。 |
| discountPercent | number | 折扣百分比，保留来源原值。 |
| currency | string | 币种，示例为 `SGD`。 |
| sold | 来源未限定 | 公开销量。 |
| soldDisplayed | 来源未限定 | 来源展示的销量值。 |
| rating | number | 商品评分。 |
| ratingCount | 来源未限定 | 聚合评价数量，不是逐条评论。 |
| ratingDistribution | 来源未限定 | 聚合星级分布，保留来源嵌套结构。 |
| likedCount | 来源未限定 | 喜欢数量。 |
| stock | 来源未限定 | 商品库存。 |
| tierVariations | 来源未限定 | 变体维度及选项，保留来源结构。 |
| models | array | SKU 变体模型，可提供库存；不保证每个模型的独立价格。 |
| shopName | string | 店铺名称。 |
| shopRating | 来源未限定 | 店铺评分。 |
| shopLocation | string | 店铺位置，示例为 `SG`。 |
| isMall | 来源未限定 | Shopee Mall 标识，独立解释。 |
| isOfficialShop | 来源未限定 | 官方店标识，独立解释。 |
| isShopeeVerified | 来源未限定 | 认证卖家标识，独立解释。 |
| shop | object | 嵌套店铺数据，成员以来源实际返回为准。 |
| description | 来源未限定 | 商品描述。 |
| attributes | 来源未限定 | 商品属性及来源嵌套结构。 |
| 其他来源字段 | 来源未限定 | 类目信息、可售状态、商品条件和新增或低频顶层字段，字段名以实际返回为准，均原样保留。 |

#### data[*].models[*] 已知成员

| 字段 | 类型 | 说明 |
|------|------|------|
| name | string | 变体名称。 |
| model_id | number | 模型 ID，示例为整数。 |
| 其他来源字段 | 来源未限定 | 如来源提供的变体库存；库存字段名和完整 SKU 结构以实际返回为准，按需提取。 |

#### columns[*] 已知成员

| 字段 | 类型 | 说明 |
|------|------|------|
| field | string | 对应商品字段名，示例为 `itemId`。 |
| title | string | 展示列标题，示例为「商品 ID」。 |
| cellType | string | 展示单元格类型，示例为 `text`；不据此推导完整枚举。 |

#### 脚本本地附加字段

| 字段 | 类型 | 说明 |
|------|------|------|
| _http_status | integer | 业务脚本记录的实际 HTTP 状态，不是网关响应字段；结合 `errcode` 按响应码规则判断。缓存命中时为原请求的历史状态，不代表本次重新请求。 |
| _response_body | 来源实际类型 | 仅当响应正文为非 object 的 JSON 时，由脚本在此保留完整正文，避免丢失错误内容。 |

连接失败没有 HTTP 状态，保留 `error` 中的具体原因。旧缓存可能没有 `_http_status`；此时 HTTP 状态未知，不能仅因缺少 `errcode` 就断言请求成功，也不要为补状态自动发起收费查询。大响应摘要未列出状态时，从保存的完整 JSON 读取。

### 响应示例

以下为响应示例节选，不代表每个站点都有全部字段或相同数据。

```json
{
  "errcode": 200,
  "errmsg": "ok",
  "data": [
    {
      "itemId": "29691169956",
      "shopId": "9641401",
      "url": "https://shopee.sg/%28LENECT-OFFICIAL-STORE%29-Flash-I-Aurora-Dual-Highlighter-7.2g-COCOMO-i.9641401.29691169956",
      "name": "Le'nect Aurora Dual Highlighter",
      "price": 36,
      "discountPercent": 23,
      "currency": "SGD",
      "rating": 5,
      "images": ["https://down-sg.img.susercontent.com/file/example"],
      "models": [
        {"name": "(BUY 1) AURORA HGLTR", "model_id": 281458233416}
      ],
      "shopName": "COCOMO Official Store",
      "shopLocation": "SG"
    }
  ],
  "total": 1,
  "costToken": 70000,
  "type": "tableListWorkbenches",
  "columns": [
    {"field": "itemId", "title": "商品 ID", "cellType": "text"}
  ]
}
```

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

| 情况 | 表现 | 处理建议 |
|------|------|----------|
| productUrl 为空或格式非法 | 网关业务错误 | 使用支持站点、路径以 `-i.<shopId>.<itemId>` 结尾的 HTTPS 商品链接。 |
| 商品无效、已移除或站点不匹配 | 网关业务错误，不是成功空列表 | 核对链接；不要自动换站点重复查询。 |
| 上游 warning/error row 或缺少 itemId/shopId | 网关业务错误 | 视为无有效商品，不计入成功数据。 |
| 上游商品 ID 与请求 URL 不一致 | 网关业务错误 | 不返回错误商品，核对链接后再决定是否重试。 |
| 上游返回多个有效商品 | 网关业务错误 | 视为上游异常；本接口不截断，不返回批量结果。 |
| 无权限（403） | 不归入认证或算力不足 | 说明权限问题，不走注册或充值流程。 |
| 超时或上游异常 | 连接错误、5xx 或业务错误 | 告知用户，不连续自动重试产生额外费用。 |

### curl 示例

```bash
API_KEY="${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}"
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/shopee/product/detail" \
  -H "Authorization: ${API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -H "SESSION_ID: ${SESSION_ID:-}" \
  -H "MESSAGE_ID: ${MESSAGE_ID:-}" \
  -H "MODE_ID: ${MODE_ID:-}" \
  -H "APP_NAME: ${APP_NAME:-}" \
  -d '{
    "productUrl": "https://shopee.sg/%28LENECT-OFFICIAL-STORE%29-Flash-I-Aurora-Dual-Highlighter-7.2g-COCOMO-i.9641401.29691169956"
  }'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-shopee-product-detail",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```