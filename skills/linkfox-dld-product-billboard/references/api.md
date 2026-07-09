# 店雷达-1688商品榜单 API 参考

## 调用规范

- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/dld/productBillboard`
- **请求方式**：POST，Content-Type: application/json
- **认证方式**：Header `Authorization: <api_key>`，api_key 从环境变量 `LINKFOX_AGENT_API_KEY` 或 `LINKFOXAGENT_API_KEY` 读取（如未配置，提示用户前往 https://skill.linkfox.com/linkfoxskills/guide.htm 申请）

## 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| keyWord | string | 否 | 商品搜索关键字（搜索关键词必须是中文，如果不是请先翻译），最大长度50 |
| date | string | 否 | 查询时间。周榜：传入该周的周天日期，如 `2025-06-15`（最长近90天）；月榜：传入该月第一天，如 `2025-06-01`（最长近一年） |
| pageType | integer | 否 | 榜单类型：`2` = 周榜，`3` = 月榜。默认 `3` |
| pageIndex | integer | 否 | 页码（从1开始），默认 `1` |
| pageSize | integer | 否 | 每页返回数量（10-100），默认 `20` |
| sortField | string | 否 | 排序字段，默认 `orderCount`。可选值：`orderCount`（销售笔数）、`saleCount`（销售件数）、`saleVolume`（预估销售额）、`offerCreateTime`（上架时间）、`price`（批发价）、`consignPrice`（代发价） |
| sortType | string | 否 | 排序类型：`desc`（降序）、`asc`（升序），默认 `desc` |
| searchType | integer | 否 | 商品关键词搜索类型：`1` = 模糊匹配，`3` = 精准匹配。默认 `1` |
| offerType | integer | 否 | 商品标识：`0` = 不限制，`2` = 新品，`3` = 1688严选，`4` = 跨境，`5` = 支持定制，`6` = 镇店之宝。默认 `0` |
| companyType | integer | 否 | 公司类型：`0` = 不限，`1` = 店铺，`2` = 工厂 |
| shiLiType | string | 否 | 卖家会员类型（多选），多个使用","号隔开。可选值：`superFactory`（超级工厂）、`Power`（实力商家）、`TrustPass`（仅诚信通会员） |
| beginTpYear | integer | 否 | 开始诚信通年限 |
| endTpYear | integer | 否 | 结束诚信通年限 |
| beginPrice | number | 否 | 批发价（起始） |
| endPrice | number | 否 | 批发价（结束） |
| beginConsignPrice | number | 否 | 代发价（起始） |
| endConsignPrice | number | 否 | 代发价（结束） |
| beginOrderCount | integer | 否 | 销售笔数（起始） |
| endOrderCount | integer | 否 | 销售笔数（结束） |
| beginSaleCount | integer | 否 | 销售件数（起始） |
| endSaleCount | integer | 否 | 销售件数（结束） |
| beginSaleVolume | number | 否 | 销售额（起始） |
| endSaleVolume | number | 否 | 销售额（结束） |
| beginStartQuantity | integer | 否 | 起始起批量 |
| endStartQuantity | integer | 否 | 结束起批量 |
| beginOfferCreateTime | string | 否 | 上架时间（起始），格式：`YYYY-MM-DD` |
| endOfferCreateTime | string | 否 | 上架时间（结束），格式：`YYYY-MM-DD` |
| sendTime | string | 否 | 发货时间（多选），多个使用","号隔开。可选值：`24`（24小时）、`48`（48小时）、`72`（72小时） |
| proxyRights | string | 否 | 代发权益（多选），多个使用","号隔开。可选值：`4360897`（一件代发包邮）、`449154`（先采后付） |
| shopService | string | 否 | 卖家服务（多选），多个使用","号隔开。可选值：`4057409`（安心购）、`888777`（深度认证报告） |
| buyerProtections | string | 否 | 权益保障（多选），多个用","隔开。可选值：`商品包邮`、`7天包退货`、`支持运费险` |
| faceToFaceSupport | string | 否 | 面单支持（多选），多个使用","号隔开。可选值：`441218`（淘宝）、`386434`（抖音）、`422914`（拼多多）、`422978`（小红书）、`386370`（快手） |
| productIds | string | 否 | 商品ID，顿号隔开搜索多个，最多20个 |
| goodsUrl | string | 否 | 商品链接地址 |


## 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| total | integer | 记录数 |
| type | string | 渲染的样式 |
| columns | array | 渲染的列 |
| products | array | 商品列表（见下方商品对象） |

### 商品对象

| 字段 | 类型 | 说明 |
|------|------|------|
| offerId | string | 商品id |
| asin | string | 商品编号 |
| title | string | 商品标题 |
| price | number | 批发价 |
| consignPrice | number | 代发价 |
| currency | string | 币种 |
| unit | string | 单位 |
| quantityBegin | integer | 起批量 |
| quantityPrices | string | 价格区间 |
| salesOrderCount | integer | 销售笔数（按统计周期返回对应的值） |
| salesQuantity | integer | 销售件数（按统计周期返回对应的值） |
| estimatedSalesAmount | integer | 预估销售额（按统计周期返回对应的值） |
| dataType | string | 数据类型：`weeklyData` = 周数据，`monthlyData` = 月数据 |
| availableDate | string | 商品上架时间，格式为 `yyyy-MM-dd HH:mm:ss` |
| deliveryTime | string | 发货时间 |
| levelName | string | 类目层级名称 |
| company | string | 店铺名称 |
| shopId | string | 店铺id |
| shopUrl | string | 店铺链接地址 |
| asinUrl | string | 商品链接地址 |
| imageUrl | string | 图片地址 |
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
curl -X POST https://tool-gateway.linkfox.com/dld/productBillboard \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "keyWord": "手机壳",
    "pageType": 3,
    "date": "2026-03-01",
    "sortField": "orderCount",
    "sortType": "desc",
    "pageSize": 20,
    "pageIndex": 1
  }'
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
