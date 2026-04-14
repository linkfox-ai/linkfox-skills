# 友鹰-Shopee 商品选品 API 参考

## 调用规范

- **请求地址**：`https://tool-gateway.linkfox.com/youying/shopee/getProductInfos`
- **请求方式**：POST，Content-Type: application/json
- **认证方式**：Header `Authorization: <api_key>`，api_key 从环境变量 `LINKFOXAGENT_API_KEY` 读取（如未配置，提示用户前往 https://yxgb3sicy7.feishu.cn/wiki/GIkkweGghiyzkqkRXQKc2n0Tnre 申请）

## 请求参数

POST Body（JSON）：

### 必填参数

| 参数 | 类型 | 说明 |
|------|------|------|
| station | string | **必填**。Shopee站点，可传名称或代码。见下方站点映射表 |

### 站点映射

| 站点 | station 值 | 代码 |
|------|-----------|------|
| 马来西亚 | malaysia | MY |
| 台湾 | taiwan_china | Taiwan_CHN |
| 印度尼西亚 | indonesia | ID |
| 泰国 | thailand | TH |
| 菲律宾 | philippines | PH |
| 新加坡 | singapore | SG |
| 越南 | vietnam | VN |
| 巴西 | brazil | BR |
| 墨西哥 | mexico | MX |
| 智利 | chile | CL |
| 哥伦比亚 | columbia | CO |

### 关键词筛选

| 参数 | 类型 | 说明 |
|------|------|------|
| keyword | string | 商品标题关键词 |
| keywordType | integer | 匹配模式：1=整句语句(默认)，2=多词AND，3=多词OR |
| notExistKeyword | string | 排除包含此关键词的商品 |
| notExistKeywordType | integer | 排除匹配模式：1=整句(默认)，2=多词AND，3=多词OR |

### 价格筛选

| 参数 | 类型 | 说明 |
|------|------|------|
| priceMin | number | 商品总价起始值（当地货币） |
| priceMax | number | 商品总价结束值 |

### 销量筛选

| 参数 | 类型 | 说明 |
|------|------|------|
| soldMin | integer | 前30天销售件数起始值 |
| soldMax | integer | 前30天销售件数结束值 |
| estimateSoldStart | integer | 估算前30天销售件数起始值 |
| estimateSoldEnd | integer | 估算前30天销售件数结束值 |
| historicalSoldStart | integer | 商品总销售件数起始值 |
| historicalSoldEnd | integer | 商品总销售件数结束值 |
| paymentStart | number | 前30天销售金额起始值 |
| paymentEnd | number | 前30天销售金额结束值 |

### 评价筛选

| 参数 | 类型 | 说明 |
|------|------|------|
| ratingMin | number | 商品评分最小值（0-5） |
| ratingMax | number | 商品评分最大值 |
| ratingsMin | integer | 评分数起始值 |
| ratingsMax | integer | 评分数结束值 |
| favoriteMin | integer | 收藏数起始值 |
| favoriteMax | integer | 收藏数结束值 |

### SKU 筛选

| 参数 | 类型 | 说明 |
|------|------|------|
| skuNumberStart | integer | SKU总数起始值 |
| skuNumberEnd | integer | SKU总数结束值 |

### 时间筛选

| 参数 | 类型 | 说明 |
|------|------|------|
| listingDateFrom | string | 商品上架时间起始值（格式: yyyy-MM-dd） |
| listingDateTo | string | 商品上架时间结束值（格式: yyyy-MM-dd） |
| statTimeStart | string | 统计时间起始值（格式: yyyy-MM-dd HH:mm:ss） |
| statTimeEnd | string | 统计时间结束值（格式: yyyy-MM-dd HH:mm:ss） |
| lastModiTimeStart | string | 最新抓取时间起始值（格式: yyyy-MM-dd） |
| lastModiTimeEnd | string | 最新抓取时间结束值（格式: yyyy-MM-dd） |
| approvedDateStart | string | 店铺开张时间起始值（格式: yyyy-MM-dd） |
| approvedDateEnd | string | 店铺开张时间结束值（格式: yyyy-MM-dd） |

### 类目筛选

| 参数 | 类型 | 说明 |
|------|------|------|
| pL1Id | string | 1级类目ID |
| pL2Id | string | 2级类目ID |
| pL3Id | string | 3级类目ID |
| cidList | string | 类目id列表，完整路径，多组用`｜`隔开，如: `AAA,BBB,CCC｜DDD,EEE` |

### 店铺筛选

| 参数 | 类型 | 说明 |
|------|------|------|
| shopIdList | string | 指定店铺id列表，多个逗号隔开 |
| notExistShopIdList | string | 排除店铺id列表，多个逗号隔开 |
| merchant | string | 店铺名称或用户名称 |
| shopLocation | string | 店铺所在地 |

### 商品属性筛选

| 参数 | 类型 | 说明 |
|------|------|------|
| shippingIconType | integer | 店铺所在地：0=本地, 1=海外 |
| cbOption | integer | 发货地点：0=本土, 1=跨境 |
| isShopeeVerified | integer | 虾皮优选：0=非优选, 1=优选 |
| isOfficialShop | integer | 官方店铺：0=否, 1=是 |
| isHotSales | integer | 是否热销：0=非热销, 1=热销 |
| pids | string | 商品id列表(最多500个)，逗号隔开 |

### 排序与分页

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| orderBy | string | - | 排序字段：`rating`(评分), `price`(价格), `historical_sold`(总销量), `sold`(30天销量), `payment`(30天销售额), `favorite`(收藏数), `ratings`(评分数), `gen_time`(上架时间), `estimate_sold`(估算销量) |
| orderByType | string | DESC | 排序方向：`ASC`(升序), `DESC`(降序) |
| page | integer | 1 | 页码（从1开始） |
| pageSize | integer | 1000 | 每页商品数（范围1-1000） |

## 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| total | integer | 当前返回记录数 |
| totalSize | integer | 总结果数 |
| sourceTool | string | 来源工具标识 |
| sourceType | string | 来源类型：`shopee` |
| columns | array | 渲染列定义 |
| costToken | integer | 消耗 token |
| type | string | 渲染样式 |
| products | array | 商品列表（见下方字段） |

### products 数组中每个商品对象

| 字段 | 类型 | 说明 |
|------|------|------|
| pid | string | 商品唯一ID |
| title | string | 商品标题 |
| description | string | 商品描述 |
| imageUrl | string | 商品主图URL |
| productUrl | string | Shopee商品链接 |
| price | number | 商品默认价（当地货币） |
| minPrice | number | SKU最低价 |
| maxPrice | number | SKU最高价 |
| sold | integer | 前30天销售件数 |
| estimateSold | integer | 估算前30天销售件数 |
| historicalSold | integer | 商品总销售件数 |
| payment | number | 前30天销售额（当地货币） |
| rating | number | 商品评分（0-5） |
| ratings | integer | 评分数 |
| favorite | integer | 收藏数 |
| viewCount | integer | 浏览数 |
| stock | integer | 库存数 |
| skuNumber | integer | SKU数量 |
| genTime | string | 上架时间 |
| statTime | string | 统计时间 |
| lastModiTime | string | 最新抓取时间 |
| categoryStructure | string | 类目结构路径 |
| cid | string | 类目ID（逗号分隔） |
| shopId | string | 店铺ID |
| shopName | string | 店铺名称 |
| shopUrl | string | 店铺链接 |
| userName | string | 店主名称 |
| shopLocation | string | 店铺所在地 |
| shopProductsCount | integer | 店铺商品总数 |
| approvedDate | string | 店铺开张时间 |
| isOfficialShop | integer | 是否官方店铺（1=是, 0=否） |
| isShopeeVerified | integer | 虾皮优选（1=是, 0=否） |
| isHotSales | integer | 是否热销（1=是, 0=否） |
| shippingIconType | integer | 店铺所在地类型（0=本地, 1=海外, 3或null=未知） |
| cbOption | integer | 发货地点（0=本土, 1=跨境） |
| estimatedDays | integer | 预计到货天数 |
| status | integer | 商品状态（1=正常, 0=下架, 8=列表中排除） |
| notExist | integer | 是否存在（0=存在, 1=不存在） |

## 错误码

正常情况下，接口的 HTTP 状态码均为 200，业务的成功与否通过响应体中的 errorCode 字段区分（errorCode = 200 表示成功，其他值表示业务错误）。当遇到未授权等情况时，HTTP 状态码为 401，且对应的 errorCode 也是 401。

| errcode | 含义 | 处理建议 |
|---------|------|----------|
| 200 | 成功 | 正常解析 `products` 等业务字段 |
| 401 | 认证失败 | 检查请求头 `Authorization` 是否正确携带 API Key |
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
curl -X POST https://tool-gateway.linkfox.com/youying/shopee/getProductInfos \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"station": "malaysia", "keyword": "Storage Box", "keywordType": 2, "soldMin": 100, "orderBy": "sold", "orderByType": "DESC", "pageSize": 50}'
```

---

## Feedback API

> This endpoint is **separate** from the tool API above. Do not mix the two base URLs.

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **Content-Type:** `application/json`

```json
{
  "skillName": "linkfox-youying-shopee-product-search",
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
