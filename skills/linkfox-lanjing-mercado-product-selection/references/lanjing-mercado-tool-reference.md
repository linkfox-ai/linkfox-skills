# Lanjing Mercado XP-MCP Tool Reference

> 美客多（Mercado Libre）平台 MCP (Model Context Protocol) 服务接口文档  
> 版本：1.0.0  
> 协议：STREAMABLE (SSE)

---

## 目录

- [1. 商品相关 (Item)](#1-商品相关-item)
- [2. 官链/目录相关 (Catalog/Product)](#2-官链目录相关-catalogproduct)
- [3. 关键词相关 (Keyword)](#3-关键词相关-keyword)
- [4. 类目相关 (Category)](#4-类目相关-category)
- [5. 趋势分析相关 (Trend)](#5-趋势分析相关-trend)
- [6. 店铺相关 (Seller)](#6-店铺相关-seller)
- [7. 评论相关 (Review)](#7-评论相关-review)
- [8. 站点相关 (Site)](#8-站点相关-site)
- [9. 个人中心 (Me)](#9-个人中心-me)

---

## 1. 商品相关 (Item)

### 1.1 itemInfo - 查询商品基本信息

**描述**：美客多平台，根据站点和商品ID查询基本信息

**是否收费**：是（需要套餐额度）

**参数说明**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| siteId | String | ✅ | 站点ID，可选值：MLM（墨西哥）、MLB（巴西）、MLA（阿根廷）、MLC（智利） |
| itemId | String | ✅ | 商品ID，如：MLM178237632 |

**使用示例**：
---

### 1.2 itemHistory - 查询商品销量历史

**描述**：美客多平台，根据商品ID查询商品销量历史信息

**是否收费**：是（需要套餐额度）

**参数说明**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| itemId | String | ✅ | 商品ID，如：MLM178237632 |
| productId | String | ❌ | 官链ID，如：MLM21333 |

**使用示例**：
---

### 1.3 itemSearch - 商品搜索

**描述**：美客多平台商品搜索工具。支持按站点、关键词、类目、价格、销量（总销量/30天销量）、评分、评论数、重量及上架时间等多维度筛选商品，并支持排序。

**是否收费**：是（需要套餐额度）

**参数说明**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| siteId | String | ✅ | 【必填】站点ID。可选值：MLM（墨西哥）、MLB（巴西）、MLC（智利）、MLA（阿根廷）、MCO（哥伦比亚） |
| title | String | ❌ | 【选填】搜索关键词，匹配商品标题。例如：蓝牙耳机 |
| categoryId | String | ❌ | 【选填】类目ID，用于限定搜索范围。例如：MLM458037 |
| sellerId | String | ❌ | 【选填】店铺ID或店铺名称，指定查询特定店铺的商品 |
| itemUrl | String | ❌ | 【选填】商品链接 |
| priceBegin | Integer | ❌ | 【选填】最低价格（整数） |
| priceEnd | Integer | ❌ | 【选填】最高价格（整数） |
| soldTotalBegin | Integer | ❌ | 【选填】最低总销量（整数） |
| soldTotalEnd | Integer | ❌ | 【选填】最高总销量（整数） |
| sale30Start | Integer | ❌ | 【选填】最低30天销量（整数） |
| sale30End | Integer | ❌ | 【选填】最高30天销量（整数） |
| scoreStart | BigDecimal | ❌ | 【选填】最低商品评分（支持小数，如4.5） |
| scoreEnd | BigDecimal | ❌ | 【选填】最高商品评分（支持小数，如5.0） |
| commentBegin | Integer | ❌ | 【选填】最低评论数（整数） |
| commentEnd | Integer | ❌ | 【选填】最高评论数（整数） |
| weightStart | Integer | ❌ | 【选填】最低商品重量，单位：克(G) |
| weightEnd | Integer | ❌ | 【选填】最高商品重量，单位：克(G) |
| startTimeAdded | Integer | ❌ | 【选填】上架时间范围。可选值：15（最近15天）、30、60、90、180、365 |
| startTimeBegin | String | ❌ | 【选填】自定义上架时间开始日期，格式：yyyy-MM-dd。例如：2026-03-01 |
| startTimeEnd | String | ❌ | 【选填】自定义上架时间结束日期，格式：yyyy-MM-dd。例如：2026-03-24 |
| storageType | String | ❌ | 【选填】仓储类型。可选值：None（全部）、FULL（官方仓）、CBT,LOCAL（自发货） |
| sellerType | String | ❌ | 【选填】店铺类型。可选值：None（全部）、LOCAL（本土店）、CBT（跨境店） |
| follow | Integer | ❌ | 【选填】是否跟卖。0：否，1：是 |
| isUsaFull | Boolean | ❌ | 【选填】是否美国转运仓。true：是，false：否 |
| itemStatus | String | ❌ | 【选填】商品状态。active：活跃，paused：暂停 |
| sortKey | String | ❌ | 【选填】排序字段。可选值：title（商品名称）、price（价格）、sale7（7天销量）、sale30d（30天销量）、sold_quantity（总销量）、sales_amount30（30天销售额）、available_quantity（库存数）、start_time（上架时间）、brand_id（品牌）、bsr（最佳销售）。默认为综合排序 |
| sortOrder | String | ❌ | 【选填】排序方式。asc：升序，desc：降序。默认为降序 |
| pageNo | Integer | ❌ | 【选填】当前页码，默认为1 |
| pageSize | Integer | ❌ | 【选填】每页条数，默认为50 |

**使用示例**：
---

## 2. 官链/目录相关 (Catalog/Product)

### 2.1 catalogInfo - 查询官链基本信息

**描述**：美客多平台，根据站点和官链（或目录链接）ID查询基本信息

**是否收费**：是（需要套餐额度）

**参数说明**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| siteId | String | ✅ | 站点ID，可选值：MLM（墨西哥）、MLB（巴西）、MLA（阿根廷）、MLC（智利） |
| productId | String | ✅ | 官链（或目录链接）ID，如：MLM178237632 |

**使用示例**：
---

### 2.2 catalogHistory - 查询官链销量历史

**描述**：美客多平台，根据站点和官链（或目录链接）ID查询销量历史信息

**是否收费**：是（需要套餐额度）

**参数说明**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| siteId | String | ✅ | 站点ID，可选值：MLM（墨西哥）、MLB（巴西）、MLA（阿根廷）、MLC（智利） |
| productId | String | ✅ | 官链（或目录链接）ID，如：MLM178237632 |

**使用示例**：
---

### 2.3 catalogSearch - 官链搜索

**描述**：美客多平台官链（或目录链接）搜索工具，支持按站点、关键词、类目、价格、销量、评分、BSR排名等多维度筛选官链

**是否收费**：是（需要套餐额度）

**参数说明**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| siteId | String | ✅ | 站点ID，可选值：MLM（墨西哥）、MLB（巴西）、MLA（阿根廷）、MLC（智利）、MCO（哥伦比亚） |
| searchText | String | ❌ | 搜索关键词 |
| catalogId | String | ❌ | 官链（或目录链接）ID |
| categoryId | String | ❌ | 类目ID |
| bland | String | ❌ | 品牌名称 |
| sellerId | String | ❌ | 店铺ID |
| priceVolStart | Integer | ❌ | 最低价格 |
| priceVolEnd | Integer | ❌ | 最高价格 |
| sales30VolStart | Integer | ❌ | 30天销量最小值 |
| sales30VolEnd | Integer | ❌ | 30天销量最大值 |
| hisVolStart | Integer | ❌ | 历史销量最小值 |
| hisVolEnd | Integer | ❌ | 历史销量最大值 |
| scoreVolStart | String | ❌ | 最低评分 |
| scoreVolEnd | String | ❌ | 最高评分 |
| commentVolStart | Integer | ❌ | 评论数最小值 |
| commentVolEnd | Integer | ❌ | 评论数最大值 |
| stockVolStart | Integer | ❌ | 库存最小值 |
| stockVolEnd | Integer | ❌ | 库存最大值 |
| weightStart | Integer | ❌ | 重量最小值（单位：克） |
| weightEnd | Integer | ❌ | 重量最大值（单位：克） |
| bsrVolStart | Integer | ❌ | BSR排名最小值 |
| bsrVolEnd | Integer | ❌ | BSR排名最大值 |
| followVol | Integer | ❌ | 是否跟卖，0：否，1：是 |
| isUsaFull | Boolean | ❌ | 是否美国转运仓，true：是，false：否 |
| storageTypeVol | String | ❌ | 仓储类型，FULL：官方仓，CBT：跨境店，LOCAL：本土店 |
| sellerTypeVol | String | ❌ | 店铺类型，LOCAL：本土店，CBT：跨境店 |
| storeStatusVol | String | ❌ | 商品状态，active：活跃，paused：暂停 |
| sortKey | String | ❌ | 排序字段，sold_his：历史销量，price：价格，sale30d：30天销量，sale7：7天销量，bsr：BSR排名 |
| sortOrder | String | ❌ | 排序方式，asc：升序，desc：降序，默认desc |
| pageNo | Integer | ❌ | 页码，默认1 |
| pageSize | Integer | ❌ | 每页条数，默认50，最大200 |
| month | String | ❌ | 查询月份，格式：YYYYMM |
| addedVol | Integer | ❌ | 上架时间天数，如：15、30、60、90、180、365 |

**使用示例**：
---

## 3. 关键词相关 (Keyword)

### 3.1 keywordDateSearch - 按天搜索热搜词

**描述**：美客多平台，根据站点和日期查询按天热搜词信息

**注意**：最大分页深度上限是 10000

**是否收费**：是（需要套餐额度）

**参数说明**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| siteId | String | ✅ | 站点ID，可选值：MLM（墨西哥）、MLB（巴西）、MLA（阿根廷）、MLC（智利） |
| runDate | String | ✅ | 搜索日期，格式：YYYYMMDD |
| categoryId | String | ❌ | 类目ID |
| searchText | String | ❌ | 搜索词 |
| sort | Object | ❌ | 排序字段，包含：key（排序字段：sale30-30天销量、item_total_count-商品数量、visit30-30天搜索量、view_count-30天访问量），order（排序方式：ascending/descending） |
| sale30 | Object | ❌ | 30天销量过滤范围，包含：start（最小值）、end（最大值） |
| visit30 | Object | ❌ | 访问量过滤范围，包含：start（最小值）、end（最大值） |
| totalItem | Object | ❌ | 商品数量过滤范围，包含：start（最小值）、end（最大值） |
| adCount | Object | ❌ | 广告数量过滤范围，包含：start（最小值）、end（最大值） |
| pageNo | Integer | ❌ | 页码，默认1 |
| pageSize | Integer | ❌ | 每页条数，默认50 |

**使用示例**：
---

### 3.2 keywordMonthSearch - 月度热搜词

**描述**：美客多平台，根据站点和月份查询月度热搜词信息

**注意**：最大分页深度上限是 10000

**是否收费**：是（需要套餐额度）

**参数说明**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| siteId | String | ✅ | 站点ID，可选值：MLM（墨西哥）、MLB（巴西）、MLA（阿根廷）、MLC（智利） |
| runMonth | String | ✅ | 搜索月份，格式：YYYYMM |
| categoryId | String | ❌ | 类目ID |
| searchText | String | ❌ | 搜索词 |
| sort | Object | ❌ | 排序字段，包含：key（排序字段：sale30-30天销量、item_total_count-商品数量、visit30-30天搜索量、view_count-30天访问量），order（排序方式：ascending/descending） |
| sale30 | Object | ❌ | 30天销量过滤范围，包含：start（最小值）、end（最大值） |
| visit30 | Object | ❌ | 访问量过滤范围，包含：start（最小值）、end（最大值） |
| totalItem | Object | ❌ | 商品数量过滤范围，包含：start（最小值）、end（最大值） |
| pageNo | Integer | ❌ | 页码，默认1 |
| pageSize | Integer | ❌ | 每页条数，默认50 |

**使用示例**：
---

### 3.3 keywordReverse - 流量词反查

**描述**：美客多平台，流量词反查

**是否收费**：是（需要套餐额度）

**参数说明**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| siteId | String | ✅ | 站点ID，可选值：MLM（墨西哥）、MLB（巴西）、MLA（阿根廷）、MLC（智利） |
| itemId | String | ✅ | 商品ID，如：MLM178237632 |

**使用示例**：
---

## 4. 类目相关 (Category)

### 4.1 categorySearch - 搜索类目

**描述**：（免费）搜索类目信息，根据站点和类目名称(西文或葡文)

**是否收费**：否（免费接口）

**参数说明**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| siteId | String | ✅ | 站点ID，可选值：MLM（墨西哥）、MLB（巴西）、MLA（阿根廷）、MLC（智利） |
| searchText | String | ✅ | 类目名称，支持西文、中文 |

**使用示例**：
---

### 4.2 categorySmallSearch - 搜索最小子类目

**描述**：（免费）搜索最小类目信息，根据站点和类目名称(西文或葡文)

**是否收费**：否（免费接口）

**参数说明**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| siteId | String | ✅ | 站点ID，可选值：MLM（墨西哥）、MLB（巴西）、MLA（阿根廷）、MLC（智利） |
| searchText | String | ✅ | 类目名称，支持西文、中文 |

**使用示例**：
---

## 5. 趋势分析相关 (Trend)

### 5.1 trendBrandTopBrand - 热门品牌排行榜

**描述**：美客多平台，查询指定类目下的热门品牌排行榜数据

**是否收费**：是（需要套餐额度）

**参数说明**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| siteId | String | ✅ | 站点ID，可选值：MLM（墨西哥）、MLB（巴西）、MLA（阿根廷）、MLC（智利）、MCO（哥伦比亚） |
| categoryId | String | ✅ | 类目ID |

**使用示例**：
---

### 5.2 trendBrandTopItem - 热门商品排行榜

**描述**：美客多平台，查询指定类目下的热门商品排行榜数据

**是否收费**：是（需要套餐额度）

**参数说明**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| siteId | String | ✅ | 站点ID，可选值：MLM（墨西哥）、MLB（巴西）、MLA（阿根廷）、MLC（智利）、MCO（哥伦比亚） |
| categoryId | String | ✅ | 类目ID |

**使用示例**：
---

### 5.3 trendBrandTopSeller - 热门店铺排行榜

**描述**：美客多平台，查询指定类目下的热门店铺排行榜数据

**是否收费**：是（需要套餐额度）

**参数说明**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| siteId | String | ✅ | 站点ID，可选值：MLM（墨西哥）、MLB（巴西）、MLA（阿根廷）、MLC（智利）、MCO（哥伦比亚） |
| categoryId | String | ✅ | 类目ID |

**使用示例**：
---

### 5.4 trendNewItems - 新品机会分析

**描述**：美客多平台，查询指定类目的新品机会数据，包括新品销量、占比等信息

**是否收费**：是（需要套餐额度）

**参数说明**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| siteId | String | ✅ | 站点ID，可选值：MLM（墨西哥）、MLB（巴西）、MLA（阿根廷）、MLC（智利）、MCO（哥伦比亚） |
| categoryId | String | ✅ | 类目ID |

**使用示例**：
---

### 5.5 trendPrice - 价格分布趋势

**描述**：美客多平台，查询指定类目的价格分布趋势数据

**是否收费**：是（需要套餐额度）

**参数说明**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| siteId | String | ✅ | 站点ID，可选值：MLM（墨西哥）、MLB（巴西）、MLA（阿根廷）、MLC（智利）、MCO（哥伦比亚） |
| categoryId | String | ✅ | 类目ID |

**使用示例**：
---

### 5.6 trendSale - 销量分布

**描述**：美客多平台，查询指定类目的销量分布数据，支持按月查询

**是否收费**：是（需要套餐额度）

**参数说明**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| siteId | String | ✅ | 站点ID，可选值：MLM（墨西哥）、MLB（巴西）、MLA（阿根廷）、MLC（智利）、MCO（哥伦比亚） |
| categoryId | String | ✅ | 类目ID |
| month | String | ❌ | 查询月份，格式：YYYYMM |

**使用示例**：
---

### 5.7 trendSoldHis - 销售历史趋势

**描述**：美客多平台，查询指定类目的销售历史趋势数据

**是否收费**：是（需要套餐额度）

**参数说明**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| siteId | String | ✅ | 站点ID，可选值：MLM（墨西哥）、MLB（巴西）、MLA（阿根廷）、MLC（智利）、MCO（哥伦比亚） |
| categoryId | String | ✅ | 类目ID |

**使用示例**：
---

### 5.8 trendStatistical - 类目汇总统计

**描述**：美客多平台，查询指定类目的汇总统计数据，包括总商品数、销量、销售额等

**是否收费**：是（需要套餐额度）

**参数说明**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| siteId | String | ✅ | 站点ID，可选值：MLM（墨西哥）、MLB（巴西）、MLA（阿根廷）、MLC（智利）、MCO（哥伦比亚） |
| categoryId | String | ✅ | 类目ID |

**使用示例**：
---

### 5.9 trendStoreInventoryType - 仓储类型分布

**描述**：美客多平台，查询指定类目的仓储类型分布数据，包括FBM、FULL、CBT等仓储类型的销售情况

**是否收费**：是（需要套餐额度）

**参数说明**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| siteId | String | ✅ | 站点ID，可选值：MLM（墨西哥）、MLB（巴西）、MLA（阿根廷）、MLC（智利）、MCO（哥伦比亚） |
| categoryId | String | ✅ | 类目ID |
| month | String | ❌ | 查询月份，格式：YYYYMM |

**使用示例**：
---

## 6. 店铺相关 (Seller)

### 6.1 sellerSearch - 店铺搜索

**描述**：美客多平台店铺搜索工具，支持按站点、店铺类型、店铺等级等条件筛选店铺

**是否收费**：是（需要套餐额度）

**参数说明**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| siteId | String | ✅ | 站点ID，可选值：MLM（墨西哥）、MLB（巴西）、MLA（阿根廷）、MLC（智利）、MCO（哥伦比亚） |
| sellerType | String | ❌ | 店铺类型，可选值：LOCAL（本土店）、CBT（跨境店）、CBT_OTHER（CBT的remote店）、CBT_FBM（CBT的full店铺） |
| levelId | String | ❌ | 店铺等级，可选值：5_green（绿）、4_light_green（浅绿）、3_yellow（黄） |
| powerType | String | ❌ | 优质卖家等级，可选值：platinum（铂金）、gold（黄金）、silver（白银） |
| pageNo | Integer | ❌ | 页码，默认1 |
| pageSize | Integer | ❌ | 每页条数，默认50 |

**使用示例**：
---

## 7. 评论相关 (Review)

### 7.1 reviewSearch - 查询商品评论

**描述**：美客多平台，按商品ID获取评论列表详情

**是否收费**：否（免费接口）

**参数说明**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| itemId | String | ✅ | 商品ID，如：MLM178237632 |
| pageNo | Integer | ❌ | 当前页码，默认为1 |
| pageSize | Integer | ❌ | 每页条数，默认为50 |

**使用示例**：
---

## 8. 站点相关 (Site)

### 8.1 rateInfo - 汇率查询

**描述**：【免费接口】美客多平台，按站点，查询对应国家币种汇率(美元)，及折算人民币汇率信息

**是否收费**：否（免费接口）

**参数说明**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| siteId | String | ✅ | 站点ID，可选值：MLM（墨西哥）、MLB（巴西）、MLA（阿根廷）、MLC（智利） |

**使用示例**：
---

## 9. 个人中心 (Me)

### 9.1 myUsage - 查询套餐使用量

**描述**：【免费接口】购买的套餐及使用量

**是否收费**：否（免费接口）

**参数说明**：无需参数（自动从认证信息中获取用户ID）

**使用示例**：
---

## 附录

### A. 站点ID对照表

| 站点ID | 国家/地区 |
|--------|----------|
| MLM | 墨西哥 |
| MLB | 巴西 |
| MLA | 阿根廷 |
| MLC | 智利 |
| MCO | 哥伦比亚 |

### B. 认证说明

本 Skill 不直连蓝鲸 XP-MCP。上游认证由 LinkFox Java 后端统一托管，Agent / Skill 侧只调用 LinkFox 生产网关 `POST https://tool-gateway.linkfox.com/lingdong/call`，不要向用户索要或传递蓝鲸上游凭证。

### C. 分页说明

- `pageNo`：页码，从 1 开始
- `pageSize`：每页条数，默认 50，部分接口最大限制为 200
- 最大分页深度限制：10000（部分接口）

### D. 排序说明

- `sortOrder`：
  - `asc`：升序
  - `desc`：降序（默认）

### E. 错误码说明

| 错误码 | 说明 |
|--------|------|
| -32000 | 系统错误 |
| -32001 | 已过期 |
| -32002 | 配额超出 |
| -32003 | 认证失败 |

---

**文档生成时间**：2026-06-29  
**技术支持**：蓝鲸选品团队
