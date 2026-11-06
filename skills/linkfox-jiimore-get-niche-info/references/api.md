# 极目亚马逊细分市场洞察 接口说明

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

## 接口：细分市场洞察信息（getNicheInfo）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/jiimore/getNicheInfo`

### 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| nicheId | string | 是 | 细分市场 ID，最大长度 1000 字符；每次只支持单个 ID，不支持批量查询。必须已有编号，本接口不能按关键词或类目搜索市场。 |
| countryCode | string | 否 | 国家编码，仅支持 `US`（美国）、`JP`（日本）、`DE`（德国），默认 `US`。仅当用户明确指定日本或德国时改为对应编码。 |

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| JSON 参数 | object | 是 | CLI 的首个位置参数；请求字段见上表。 |
| --inline | CLI flag | 否 | 强制完整打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 禁用本次本地响应缓存的读取与写入；不删除已有缓存。 |

脚本提供 24 小时本地缓存：以排序后的请求 JSON 的 SHA-256 前 16 位作为键，保存在 `<cwd>/linkfox/.cache/linkfox-jiimore-get-niche-info/`；字段顺序变化不会产生新的缓存键。命中时添加 `_cache.hit=true`。正常响应、业务错误或空结果均可能被缓存；过期或损坏时重新请求，不自动重试。业务封装调用 `call_api.run` 时始终传入 `--no-cache`，关闭公共调用器的响应缓存，仅使用这一层缓存。

接口密钥兼容两种环境变量，优先 `LINKFOX_AGENT_API_KEY`，其次 `LINKFOXAGENT_API_KEY`；网关优先 `LINKFOX_TOOL_GATEWAY`，默认正式地址。调用器保留 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 请求头。完整响应始终以 UTF-8 保存在当前目录的会话数据路径，并维护 `_meta.json` 和 `index.jsonl`；禁止写入 `/tmp`，当前目录不可写时在请求前报错，不回退到家目录或临时目录。正式写入失败或文件内容不完整时以非零状态退出，不自动再次请求。无 `SESSION_ID` 时自动生成进程内稳定的会话编号。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 业务状态码；按公共响应码基本规则判断。 |
| errorCode | 以实际返回为准 | 补充状态字段，`200` 表示成功、其他值表示业务错误，未授权时为 `401`。若返回则保留实际值，响应判定仍按公共规则，不将其替代 `errcode`。 |
| errmsg | string | 错误消息，业务异常时用于说明原因。 |
| total | integer | 记录数 |
| data | array | 细分市场信息列表，每个元素为包含以下字段的对象 |
| columns | array | 渲染的列 |
| costToken | integer | 消耗token |
| type | string | 渲染的样式 |

#### data[*] 细分市场对象

##### 市场概览

| 字段 | 类型 | 说明 |
|------|------|------|
| nicheId | string | 细分市场ID |
| nicheTitle | string | 细分市场标题 |
| translationZh | string | 细分市场标题(中文) |
| referenceAsinImageUrl | string | 细分市场参考图片地址 |
| marketplaceId | string | 市场ID |
| demand | integer | 细分市场得分 |
| categorieList | array | 商品品类列表 |

##### 商品与品牌数量

| 字段 | 类型 | 说明 |
|------|------|------|
| productCount | integer | 商品数量 |
| productCountNow | integer | 商品数量(当前) |
| productCountT90Before | integer | 商品数量(90天前) |
| productCountT360Before | integer | 商品数量(360天前) |
| brandCount | integer | 品牌数量 |
| brandCountNow | integer | 品牌数量(当前) |
| brandCountT90Before | integer | 品牌数量(90天前) |
| brandCountT360Before | integer | 品牌数量(360天前) |
| brandCountT360Now | integer | 品牌数量(360天统计)(当前) |
| brandCountT360T90Before | integer | 品牌数量(360天统计)(90天前) |
| brandCountT360T360Before | integer | 品牌数量(360天统计)(360天前) |
| sellingPartnerCountNow | integer | 销售伙伴数量(当前) |
| sellingPartnerCountT90Before | integer | 销售伙伴数量(90天前) |
| sellingPartnerCountT360Before | integer | 销售伙伴数量(360天前) |
| sellingPartnerCountT360Now | integer | 销售伙伴数量(360 天统计)(当前) |
| sellingPartnerCountT360T90Before | integer | 销售伙伴数量(360 天统计)(90天前) |
| sellingPartnerCountT360T360Before | integer | 销售伙伴数量(360 天统计)(360天前) |

##### 价格

| 字段 | 类型 | 说明 |
|------|------|------|
| avgPrice | number | 产品均价 |
| avgProductPriceNow | number | 产品均价(当前) |
| avgProductPriceT90Before | number | 产品均价(90天前) |
| avgProductPriceT360Before | number | 产品均价(360天前) |
| minimumPrice | number | 产品最低价 |
| maximumPrice | number | 产品最高价 |

##### 搜索与转化

| 字段 | 类型 | 说明 |
|------|------|------|
| searchVolumeWeekly | integer | 搜索量（周数据） |
| searchVolumeQuarterly | integer | 搜索量（季度数据） |
| searchVolumeGrowthWeekly | number | 搜索量增长率（周数据） |
| searchVolumeGrowthQuarterly | number | 搜索量增长率（季度数据） |
| searchConversionRateWeekly | number | 搜索转换率（周数据） |
| searchConversionRateQuarterly | number | 搜索转换率（季度数据） |
| clickCountWeekly | integer | 点击量（周数据） |
| clickCountQuarterly | integer | 点击量（季度数据） |
| clickConversionRateQuarterly | number | 点击转换率（季度数据） |
| clickToSaleConversionWeekly | number | 点击转换率（周数据） |
| unitsSoldWeekly | integer | 销售数量（周数据） |
| unitsSoldQuarterly | integer | 销售数量（季度数据） |

##### 竞争 - 商品点击份额

| 字段 | 类型 | 说明 |
|------|------|------|
| top5ProductsClickShare | number | 排名前 5 位的商品点击份额 |
| top5ProductsClickShareNow | number | 前5个商品所占细分市场的点击量份额(当前) |
| top5ProductsClickShareT90Before | number | 前5个商品所占细分市场的点击量份额(90天前) |
| top5ProductsClickShareT360Before | number | 前5个商品所占细分市场的点击量份额(360天前) |
| top5ProductsClickShareT360Now | number | 排名前 5 位的商品点击份额（360天统计）(当前) |
| top5ProductsClickShareT360T90Before | number | 排名前 5 位的商品点击份额（360天统计）(90天前) |
| top5ProductsClickShareT360T360Before | number | 排名前 5 位的商品点击份额（360天统计）(360天前) |
| top20ProductsClickShareNow | number | 前20个商品所占细分市场的点击量份额（当前) |
| top20ProductsClickShareT90Before | number | 前20个商品所占细分市场的点击量份额（90天前) |
| top20ProductsClickShareT360Before | number | 前20个商品所占细分市场的点击量份额（360天前) |
| top20ProductsClickShareT360Now | number | 排名前20位的商品点击份额(360 天统计)(当前) |
| top20ProductsClickShareT360T90Before | number | 排名前20位的商品点击份额(360 天统计)(90天前) |
| top20ProductsClickShareT360T360Before | number | 排名前20位的商品点击份额(360 天统计)(360天前) |

##### 竞争 - 品牌点击份额

| 字段 | 类型 | 说明 |
|------|------|------|
| top5BrandsClickShare | number | 前5个品牌所占细分市场的点击量份额 |
| top5BrandsClickShareNow | number | 前5个品牌所占细分市场的点击量份额(当前) |
| top5BrandsClickShareT90Before | number | 前5个品牌所占细分市场的点击量份额(90天前) |
| top5BrandsClickShareT360Before | number | 前5个品牌所占细分市场的点击量份额(360天前) |
| top5BrandsClickShareT360Now | number | 前5个品牌所占细分市场的点击量份额(360 天统计)(当前) |
| top5BrandsClickShareT360T90Before | number | 前5个品牌所占细分市场的点击量份额(360 天统计)(90天前) |
| top5BrandsClickShareT360T360Before | number | 前5个品牌所占细分市场的点击量份额(360 天统计)(360天前) |
| top20BrandsClickShareNow | number | 前20个品牌所占细分市场的点击量份额(当前) |
| top20BrandsClickShareT90Before | number | 前20个品牌所占细分市场的点击量份额(90天前) |
| top20BrandsClickShareT360Before | number | 前20个品牌所占细分市场的点击量份额(360天前) |
| top20BrandsClickShareT360Now | number | 前20个品牌所占细分市场的点击量份额(360天统计)（当前) |
| top20BrandsClickShareT360T90Before | number | 前20个品牌所占细分市场的点击量份额(360天统计)（90天前) |
| top20BrandsClickShareT360T360Before | number | 前20个品牌所占细分市场的点击量份额(360天统计)（360天前) |

##### 商品上架

| 字段 | 类型 | 说明 |
|------|------|------|
| newProductsLaunchedSemiannual | integer | 已发布新产品的数量（半年数据） |
| newProductsLaunchedT180Now | integer | 已发布新产品的数量(180天统计)(当前) |
| newProductsLaunchedT180T90Before | integer | 已发布新产品的数量(180天统计)(90天前) |
| newProductsLaunchedT180T360Before | integer | 已发布新产品的数量(180天统计)(360天前) |
| newProductsLaunchedT360Now | integer | 新上架商品数(360天统计)(当前) |
| newProductsLaunchedT360T90Before | integer | 新上架商品数(360天统计)(90天前) |
| newProductsLaunchedT360T360Before | integer | 新上架商品数(360天统计)(360天前) |
| successfulLaunchedSemiannual | integer | 成功发布商品的数量（半年数据） |
| launchRateSemiannual | number | 发布商品的成功率（半年数据） |
| successfulLaunchesT90Now | integer | 成功上架数(90天统计)(当前） |
| successfulLaunchesT90T90Before | integer | 成功上架数(90天统计)(90天前) |
| successfulLaunchesT90T360Before | integer | 成功上架数(90天统计)(360天前) |
| successfulLaunchesT180Now | integer | 成功发布商品的数量（180 天统计）(当前) |
| successfulLaunchesT180T90Before | integer | 成功发布商品的数量（180 天统计）(90天前) |
| successfulLaunchesT180T360Before | integer | 成功发布商品的数量（180 天统计）(360天前) |
| successfulLaunchesT360Now | integer | 成功发布商品的数量（360 天统计）(当前) |
| successfulLaunchesT360T90Before | integer | 成功发布商品的数量（360 天统计）(90天前) |
| successfulLaunchesT360T360Before | integer | 成功发布商品的数量（360 天统计）(360天前) |

##### 库存与运营

| 字段 | 类型 | 说明 |
|------|------|------|
| avgOOSRateNow | number | 平均缺货率(当前) |
| avgOOSRateT90Before | number | 平均缺货率(90天前) |
| avgOOSRateT360Before | number | 平均缺货率(360天前) |
| avgOOSRateT360Now | number | 平均缺货率(360天统计)(当前) |
| avgOOSRateT360T90Before | number | 平均缺货率(360天统计)(90天前) |
| avgOOSRateT360T360Before | number | 平均缺货率(360天统计)(360天前) |
| primeProductsPercentageNow | number | prime商品的百分比(当前) |
| primeProductsPercentageT90Before | number | prime商品的百分比(90天前) |
| primeProductsPercentageT360Before | number | prime商品的百分比(360天前) |
| primeProductsPercentageT360Now | number | prime商品的百分比(360 天统计）(当前) |
| primeProductsPercentageT360T90Before | number | prime商品的百分比(360 天统计）(90天前) |
| primeProductsPercentageT360T360Before | number | prime商品的百分比(360 天统计）(360天前) |

##### 评论与评分

| 字段 | 类型 | 说明 |
|------|------|------|
| avgReviewRatingNow | number | 平均评论评分(当前) |
| avgReviewRatingT90Before | number | 平均评论评分(90天前) |
| avgReviewRatingT360Before | number | 平均评论评分(360天前) |
| avgReviewCountNow | number | 平均评论数(当前) |
| avgReviewCountT90Before | number | 平均评论数(90天前) |
| avgReviewCountT360Before | number | 平均评论数(360天前) |
| positiveCustomerReviewInsights | array | 正面客户评论见解信息 |
| negativeCustomerReviewInsights | array | 负面客户评论见解信息 |
| productStarRatingImpact | array | 产品星级影响力信息 |

##### 卖家成熟度

| 字段 | 类型 | 说明 |
|------|------|------|
| avgBrandAgeNow | number | 平均品牌年龄(当前) |
| avgBrandAgeT90Before | number | 平均品牌年龄(90天前) |
| avgBrandAgeT360Before | number | 平均品牌年龄(360天前) |
| avgBrandAgeQuarterly | number | 平均品牌年龄(季度数据) |
| avgBrandAgeT360Now | number | 平均品牌年龄(360 天统计)(当前) |
| avgBrandAgeT360T90Before | number | 平均品牌年龄(360 天统计)(90天前) |
| avgBrandAgeT360T360Before | number | 平均品牌年龄(360 天统计)(360天前) |
| avgSellingPartnerAgeNow | number | 平均销售伙伴年龄(当前) |
| avgSellingPartnerAgeT90Before | number | 平均销售伙伴年龄(90天前) |
| avgSellingPartnerAgeT360Before | number | 平均销售伙伴年龄(360天前) |
| avgBestSellerRankNow | number | 平均BestSeller排名(当前) |
| avgBestSellerRankT90Before | number | 平均BestSeller排名(90天前) |
| avgBestSellerRankT360Before | number | 平均BestSeller排名(360天前) |

##### 广告与盈利

| 字段 | 类型 | 说明 |
|------|------|------|
| acos | number | （ACOS）广告销售成本比 |
| sponsoredProductsPercentageNow | number | 已进行商品推广的商品的百分比(当前) |
| sponsoredProductsPercentageT90Before | number | 已进行商品推广的商品的百分比(90天前) |
| sponsoredProductsPercentageT360Before | number | 已进行商品推广的商品的百分比(360天前) |
| sponsoredProductsPercentageT360Now | number | 已进行商品推广的商品的百分比(360 天统计)(当前) |
| sponsoredProductsPercentageT360T90Before | number | 已进行商品推广的商品的百分比(360 天统计)(90天前) |
| sponsoredProductsPercentageT360T360Before | number | 已进行商品推广的商品的百分比(360 天统计)(360天前) |
| profitMarginGt50PctSkuRatio | number | 利润率大于50%的商品比例 |
| breakEvenRatio | number | 盈亏平衡自然占比 |
| returnRateAnnual | number | 退货率（全年数据） |
| cpc | object | CPC（每次点击费用）数据 |

`categorieList`、评论见解、星级影响、`columns` 的元素字段及 `cpc` 的子字段以实际返回的嵌套结构为准，不推测或补造字段。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 查询失败时结合实际返回原因提示核对细分市场编号与国家编码；不要自动变更查询条件连续请求。

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/jiimore/getNicheInfo" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"nicheId": "12345678", "countryCode": "US"}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-jiimore-get-niche-info",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```