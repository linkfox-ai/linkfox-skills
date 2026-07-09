# 店雷达 1688 选品库 API 参考

## 调用规范

- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/dld/productSearch`
- **请求方式**：POST，Content-Type: application/json
- **认证方式**：Header `Authorization: <api_key>`，api_key 从环境变量 `LINKFOX_AGENT_API_KEY` 或 `LINKFOXAGENT_API_KEY` 读取（如未配置，提示用户前往 https://skill.linkfox.com/linkfoxskills/guide.htm 申请）

## 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| keyWord | string | 否 | - | 搜索关键词（必须为中文，最多50字符） |
| goodsUrl | string | 否 | - | 商品链接地址（与keyWord二选一） |
| productIds | string | 否 | - | 商品ID，多个逗号隔开，最多20个 |
| cycle | string | 否 | - | 统计周期：`7`（近7天）或 `30`（近30天） |
| searchType | integer | 否 | 1 | 搜索类型：1-模糊匹配，3-精准匹配 |
| sortField | string | 否 | orderCount30d | 排序字段：orderCount7d, saleCount7d, saleVolume7d, orderCount30d, saleCount30d, saleVolume30d, offerCreateTime, price, consignPrice |
| sortType | string | 否 | desc | 排序类型：desc（降序）、asc（升序） |
| pageIndex | integer | 否 | 1 | 页码（从1开始） |
| pageSize | integer | 否 | 20 | 每页数量（10-100） |
| beginPrice | number | 否 | - | 批发价（起始） |
| endPrice | number | 否 | - | 批发价（结束） |
| beginConsignPrice | number | 否 | - | 代发价（起始） |
| endConsignPrice | number | 否 | - | 代发价（结束） |
| beginOrderCount | integer | 否 | - | 销售笔数（起始） |
| endOrderCount | integer | 否 | - | 销售笔数（结束） |
| beginSaleCount | integer | 否 | - | 销售件数（起始） |
| endSaleCount | integer | 否 | - | 销售件数（结束） |
| beginSaleVolume | number | 否 | - | 销售额（起始） |
| endSaleVolume | number | 否 | - | 销售额（结束） |
| beginStartQuantity | integer | 否 | - | 起购数量（起始） |
| endStartQuantity | integer | 否 | - | 起购数量（结束） |
| beginTpYear | integer | 否 | - | 诚信通年限（起始） |
| endTpYear | integer | 否 | - | 诚信通年限（结束） |
| beginOfferCreateTime | string | 否 | - | 上架时间起始（格式：YYYY-MM-DD） |
| endOfferCreateTime | string | 否 | - | 上架时间结束（格式：YYYY-MM-DD） |
| companyType | integer | 否 | 0 | 公司类型：0-不限，1-店铺，2-工厂 |
| offerType | integer | 否 | 0 | 商品标识：0-不限，2-新品，3-1688严选，4-跨境，5-支持定制，6-镇店之宝 |
| shiLiType | string | 否 | - | 卖家类型（多选逗号隔开）：superFactory（超级工厂）、Power（实力商家）、TrustPass（诚信通） |
| sendTime | string | 否 | - | 发货时间（多选逗号隔开）：24、48、72 |
| faceToFaceSupport | string | 否 | - | 面单支持（多选逗号隔开）：441218（淘宝）、386434（抖音）、422914（拼多多）、422978（小红书）、386370（快手） |
| proxyRights | string | 否 | - | 代发权益（多选逗号隔开）：4360897（一件代发包邮）、449154（先采后付） |
| shopService | string | 否 | - | 卖家服务（多选逗号隔开）：4057409（安心购）、888777（深度认证报告） |
| buyerProtections | string | 否 | - | 权益保障（多选逗号隔开）：商品包邮、7天包退货、支持运费险 |

## 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| total | integer | 总记录数 |
| type | string | 渲染样式 |
| columns | array | 渲染列定义 |
| products | array | 商品列表（详见下方字段） |

### products 数组元素字段

| 字段 | 类型 | 说明 |
|------|------|------|
| offerId | string | 商品ID |
| asin | string | 商品编号 |
| title | string | 商品标题 |
| asinUrl | string | 商品链接地址 |
| imageUrl | string | 商品图片地址 |
| price | number | 批发价 |
| consignPrice | number | 代发价 |
| quantityPrices | string | 价格区间 |
| quantityBegin | integer | 起批量 |
| unit | string | 单位 |
| currency | string | 币种 |
| salesOrderCount | integer | 销售笔数（按统计周期） |
| salesQuantity | integer | 销售件数（按统计周期） |
| estimatedSalesAmount | integer | 预估销售额（按统计周期） |
| deliveryTime | string | 发货时间 |
| availableDate | string | 商品上架时间 |
| levelName | string | 类目层级名称 |
| company | string | 店铺名称 |
| shopId | string | 店铺ID |
| shopUrl | string | 店铺链接地址 |
| dataType | string | 数据类型：weeklyData（周数据）、monthlyData（月数据） |
| sourceType | string | 来源平台（1688） |
| sourceTool | string | 来源工具 |

## 错误码

正常情况下，接口的 HTTP 状态码均为 200，业务的成功与否通过响应体中的 errorCode 字段区分（errorCode = 200 表示成功，其他值表示业务错误）。当遇到未授权等情况时，HTTP 状态码为 401，且对应的 errorCode 也是 401。

| errcode | 含义 | 处理建议 |
|---------|------|----------|
| 200 | 成功 | 正常解析业务字段 |
| 401 | 认证失败 | 检查请求头 `Authorization` 是否正确携带 API Key；API Key 申请方式请参考上述[调用规范](#调用规范)下的认证方式。|
| 其他非200值 | 业务异常 | 参考 `errmsg` 字段获取具体错误原因 |

错误响应示例：

```json
{
    "errcode": 401,
    "errmsg": "authorized error"
}
```

## curl 示例

```bash
curl -X POST https://tool-gateway.linkfox.com/dld/productSearch \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"keyWord": "瑜伽垫", "cycle": "30", "sortField": "saleCount30d", "sortType": "desc", "pageSize": 20}'
```

---

## Feedback API

> This endpoint is **separate** from the tool API above. Do not mix the two base URLs.

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **Content-Type:** `application/json`

```json
{
  "skillName": "linkfox-xxx-xxx",
  "sentiment": "POSITIVE",
  "category": "OTHER",
  "content": "Results were accurate, user was satisfied."
}
```

**Field rules:**
- `skillName`: Use this skill's `name` from the YAML frontmatter
- `sentiment`: Choose ONE — `POSITIVE` (praise), `NEUTRAL` (suggestion without emotion), `NEGATIVE` (complaint or error)
- `category`: Choose ONE — `BUG` (malfunction or wrong data), `COMPLAINT` (user dissatisfaction), `SUGGESTION` (improvement idea), `OTHER`
- `content`: Include what the user said or intended, what actually happened, and why it is a problem or praise
