# 1688-以图搜图 API 参考

## 调用规范

- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/alibaba1688/imageSearch`
- **请求方式**：POST，Content-Type: application/json
- **认证方式**：Header `Authorization: <api_key>`，api_key 优先从环境变量 `LINKFOX_AGENT_API_KEY` 读取，回退 `LINKFOXAGENT_API_KEY`（如未配置，提示用户前往 https://skill.linkfox.com/linkfoxskills/guide.htm 申请）
- **User-Agent**：`LinkFox-Skill/1.0`
- **超时**：60s

## 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| imageUrl | string | 条件必填 | - | 图片URL地址，请确保图片URL有效且可公开访问。最大长度：1000。仅支持 png/jpg/jpeg 格式，不支持 webp/gif 等。imageUrl/imageBase64/imageId 三选一必填 |
| imageBase64 | string | 条件必填 | - | 图片 Base64 编码字符串，为纯编码内容，不包含 `data:image/jpeg;base64,` 前缀。仅支持 png/jpg/jpeg 格式（imageUrl为空时使用） |
| imageId | string | 条件必填 | - | 图片ID（1688图片ID），以图搜图查询结果中也会返回，建议当分页 page>1 查询时带 imageId，加快响应速度 |
| page | int | 否 | 1 | 页码，从1开始 |
| pageSize | int | 否 | 20 | 每页返回的商品数量，最大不超过50 |
| priceStart | string | 否 | - | 价格筛选起始值（人民币），如 10 |
| priceEnd | string | 否 | - | 价格筛选结束值（人民币），如 100 |
| filter | string | 否 | - | 过滤条件，多个条件用逗号分隔。有效值见下方「支持的过滤条件」 |
| sort | string | 否 | {"monthSold":"desc"} | 排序条件，JSON格式 {排序字段: 排序方式}。有效字段：price、rePurchaseRate、monthSold；方式：asc/desc |
| keyword | string | 否 | - | 关键词，在结果中搜索 |
| productCollectionId | string | 否 | - | 货盘ID，单选。有效值见下方「支持的货盘ID」 |

### 支持的过滤条件

多个条件用逗号分隔，如 `1688Selection,totalEpScoreLv1,qrr0`。

| 值 | 说明 |
|----|------|
| 1688Selection | 1688严选 |
| certifiedFactory | 认证工厂 |
| totalEpScoreLv1 | 综合体验分5星 |
| totalEpScoreLv2 | 综合体验分4星 |
| totalEpScoreLv3 | 综合体验分3星 |
| totalEpScoreLv4 | 综合体验分2星 |
| qrr0 | 无品质退款 |
| qrr1 | 品质退款率<1% |
| qrr5 | 品质退款率<5% |
| qrr10 | 品质退款率<10% |
| shipInToday | 当日发货 |
| shipIn24Hours | 24小时发货 |
| shipIn48Hours | 48小时发货 |
| noReason7DReturn | 7天无理由退货 |
| isOnePsale | 一件代发 |
| isOnePsaleFreePost | 一件代发包邮 |
| new7 | 7天内新品 |
| new30 | 30天内新品 |
| isQqyx | 全球严选 |
| JPFL | 日本专线 |
| USFL | 美国专线 |
| KRFL | 韩国专线 |
| VNFL | 越南专线 |
| SAFL | 沙特专线 |
| RUFL | 俄罗斯专线 |
| KZFL | 哈萨克斯坦专线 |
| HKFL | 香港专线 |
| MOFL | 澳门专线 |
| TWFL | 台湾专线 |

### 支持的排序字段

| 字段 | 说明 |
|------|------|
| price | 价格 |
| monthSold | 月销量 |
| rePurchaseRate | 复购率 |

排序方式：`asc`（升序）、`desc`（降序）。格式示例：`{"price":"asc"}`

### 支持的货盘ID

| ID | 说明 |
|----|------|
| 262105288 | 跨境货盘 |
| 262105286 | 跨境货盘 |
| 262105253 | 跨境货盘 |
| 262105281 | 跨境货盘 |
| 262105280 | 跨境货盘 |
| 262105277 | 跨境货盘 |
| 262105276 | 跨境货盘 |
| 262105274 | 跨境货盘 |
| 262105269 | 跨境货盘 |
| 262185282 | 跨境货盘 |

## 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| imageId | string | 上传后的图片ID（分页查询时回传可加速） |
| total | integer | 本页商品数量 |
| totalPage | integer | 总页数 |
| sourceType | string | 来源类型（固定值 "1688"） |
| type | string | 渲染样式（固定值 "productWorkbenches"） |
| columns | array | 渲染列定义 |
| costToken | integer | 消耗 token |
| products | array | 商品列表（详见下方商品字段） |

### 商品字段

| 字段 | 类型 | 说明 |
|------|------|------|
| offerId | string | 商品ID |
| asin | string | 商品编号（同 offerId） |
| imageUrl | string | 商品图片 |
| title | string | 商品标题 |
| price | number | 批发价（元） |
| consignPrice | number | 一件代发价（元） |
| salesQuantity | integer | 月销售件数 |
| estimatedSalesAmount | number | 预估销售额 |
| asinUrl | string | 商品链接 |
| isOnePsale | string | 是否一件代发（是/否） |
| isJxhy | string | 是否精选货源（是/否） |
| sellerIdentities | string | 商家身份（超级工厂/实力商家/诚信通会员） |
| offerIdentities | string | 商品标（严选） |
| repurchaseRate | string | 复购率 |
| tradeScore | string | 商品交易评分 |
| compositeServiceScore | string | 综合服务体验分 |
| sendGoodsAddressText | string | 发货地 |
| deliveryTime | string | 发货时间（24/48小时） |
| quantityBegin | integer | 起批量 |
| hasPromotion | string | 是否有营销活动（是/否） |
| promotionType | string | 营销类型 |
| isPatentProduct | string | 是否专利商品（是/否） |
| isSelect | string | 跨境select货盘标识 |
| currency | string | 币种（固定值 "¥"） |
| sourceType | string | 来源类型（固定值 "1688"） |
| sourceTool | string | 来源工具（固定值 "1688以图搜图"） |
| dataType | string | 数据类型（固定值 "monthlyData"） |

## 错误码

正常情况下，接口的 HTTP 状态码均为 200，业务的成功与否通过响应体中的 errorCode 字段区分（errorCode = 200 表示成功，其他值表示业务错误）。当遇到未授权等情况时，HTTP 状态码为 401，且对应的 errorCode 也是 401。

| errcode | 含义 | 处理建议 |
|---------|------|----------|
| 200 | 成功 | 正常解析业务字段 |
| 401 | 认证失败 | 检查请求头 `Authorization` 是否正确携带 API Key；API Key 申请方式请参考上述[调用规范](#调用规范)下的认证方式 |
| 其他非200值 | 业务异常 | 参考 `errmsg` 字段获取具体错误原因 |

错误响应示例：

```json
{
    "errcode": 401,
    "errmsg": "authorized error"
}
```

## curl 示例

### 基础以图搜图

```bash
curl -X POST https://tool-gateway.linkfox.com/alibaba1688/imageSearch \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/1.0" \
  -d '{
    "imageUrl": "https://m.media-amazon.com/images/I/719mRAn2VrL._AC_SL1500_.jpg",
    "page": 1,
    "pageSize": 20
  }'
```

### 带筛选和排序

```bash
curl -X POST https://tool-gateway.linkfox.com/alibaba1688/imageSearch \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/1.0" \
  -d '{
    "imageUrl": "https://m.media-amazon.com/images/I/719mRAn2VrL._AC_SL1500_.jpg",
    "page": 1,
    "pageSize": 20,
    "filter": "1688Selection,totalEpScoreLv1,qrr0",
    "sort": "{\"price\":\"desc\"}"
  }'
```

### 分页查询（使用 imageId）

```bash
curl -X POST https://tool-gateway.linkfox.com/alibaba1688/imageSearch \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/1.0" \
  -d '{
    "imageId": "abc123456",
    "page": 2,
    "pageSize": 20
  }'
```

### 价格区间筛选

```bash
curl -X POST https://tool-gateway.linkfox.com/alibaba1688/imageSearch \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/1.0" \
  -d '{
    "imageUrl": "https://m.media-amazon.com/images/I/719mRAn2VrL._AC_SL1500_.jpg",
    "page": 1,
    "pageSize": 20,
    "priceStart": "10",
    "priceEnd": "100"
  }'
```

---

## Feedback API

> This endpoint is **separate** from the tool API above. Do not mix the two base URLs.

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **Content-Type:** `application/json`

```json
{
  "skillName": "linkfox-1688-search-by-image",
  "sentiment": "POSITIVE",
  "category": "OTHER",
  "content": "Results were accurate, user was satisfied."
}
```

**Field rules:**
- `skillName`: Use this skill's `name` from the YAML frontmatter (`linkfox-1688-search-by-image`)
- `sentiment`: Choose ONE — `POSITIVE` (praise), `NEUTRAL` (suggestion without emotion), `NEGATIVE` (complaint or error)
- `category`: Choose ONE — `BUG` (malfunction or wrong data), `COMPLAINT` (user dissatisfaction), `SUGGESTION` (improvement idea), `OTHER`
- `content`: Include what the user said or intended, what actually happened, and why it is a problem or praise
