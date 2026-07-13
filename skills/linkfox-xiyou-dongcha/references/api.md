# 西柚找词 API 参考

> 本文档按 **路由** 逐个给出完整说明：每个路由都独立列出「调用信息 + 入参 + 出参（含嵌套对象字段）」，无需跨章节查阅。
> 全局通用的鉴权、站点枚举、公共响应字段见「通用约定」，各路由不再重复整张表。

## 调用规范

- **网关地址**：`${LINKFOX_TOOL_GATEWAY}/xiyou/<路由名>`（如 `asinTraffic` → `.../xiyou/asinTraffic`）
- **请求方式**：POST，`Content-Type: application/json`
- **LinkFox 认证**：请求头 `Authorization: <LINKFOX_AGENT_API_KEY 或 LINKFOXAGENT_API_KEY>`（如未配置 按 SKILL.md 的 **## 解决认证和积分问题** 处理）
- **西柚认证**：请求体 JSON 中的 `clientId`、`clientSecret`（脚本从环境变量 `XIYOU_CLIENT_ID`、`XIYOU_CLIENT_SECRET` 自动注入，**无需**在 `--params` 中手写）
- **上游服务**：西柚找词 OpenAPI（`https://openapi.xiyouzhaoci.com`），经 LinkFox 网关转发

### 环境变量

| 变量 | 必填 | 说明 |
|------|------|------|
| `LINKFOXAGENT_API_KEY` | 是 | LinkFox Agent API Key（如未配置 按 SKILL.md 的 **## 解决认证和积分问题** 处理） |
| `XIYOU_CLIENT_ID` | 是 | 西柚 OpenAPI Client ID（16 位） |
| `XIYOU_CLIENT_SECRET` | 是 | 西柚 OpenAPI Client Secret（24 位） |

西柚 `clientId` / `clientSecret` 获取：[西柚洞察 OpenAPI 控制台](https://www.xydc.com/openapi?xiyou-insights-web=%2Fopenapi)

### 命令行示例

```bash
export LINKFOXAGENT_API_KEY=your-linkfox-key
export XIYOU_CLIENT_ID=your-16-char-client-id
export XIYOU_CLIENT_SECRET=your-24-char-client-secret

python scripts/xiyou.py --list-apis
python scripts/xiyou.py --api asinTraffic --params '{"entities":[{"country":"US","asin":"B06XZTZ7GB"}]}'
```

---

## 通用约定

仅以下三类内容为所有路由共用，故集中说明一次；各路由的入参/出参表均**自包含**，不再引用其它章节。

### 鉴权字段（所有路由必填）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `clientId` | string | 是 | 西柚 OpenAPI Client ID（16 位，脚本自动注入） |
| `clientSecret` | string | 是 | 西柚 OpenAPI Client Secret（24 位，脚本自动注入） |

> 下文各路由入参表为简洁起见省略 `clientId` / `clientSecret`，但它们对每个路由都必填。

### 站点国家代码 `country`

2 位大写枚举：`US`(美国)、`CA`(加拿大)、`MX`(墨西哥)、`BR`(巴西)、`UK`(英国)、`DE`(德国)、`ES`(西班牙)、`IT`(意大利)、`FR`(法国)、`JP`(日本)、`AU`(澳大利亚)、`SA`(沙特)、`AE`(阿联酋)。默认 `US`。

**例外**：`asinSearchTermRankTrendHourly` 仅支持 `US` / `UK` / `DE`。

### 公共响应字段

列表/趋势类路由出参除业务字段外，通常还包含以下固定字段（各路由出参表只列业务字段，下列字段默认存在）：

| 字段 | 类型 | 说明 |
|------|------|------|
| `sourceType` | string | 固定 `"amazon"` |
| `sourceTool` | string | 固定 `"xiyou"` |
| `type` | string | 固定 `"tableListWorkbenches"`（工作台表格渲染） |
| `columns` | array | 前端列定义 |
| `title` | string | 接口标题 |
| `total` | integer | 数据条数 / 趋势点数量 |

---

# 一、ASIN 模块

## 1. ASIN 流量得分 — `asinTraffic`

| 项目 | 说明 |
|------|------|
| **路由** | `POST /xiyou/asinTraffic` |
| **上游** | `POST v1/asins/traffic` |
| **计费** | 每 10 个 ASIN 计 1 Credit |
| **用途** | 批量查询 ASIN 近 7 天自然/广告/总流量得分及环比 |

### 入参

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `entities` | array | 是 | ASIN 查询实体列表，最多 100 个 |
| `entities[].country` | string | 是 | 站点国家代码 |
| `entities[].asin` | string | 是 | 10 位 ASIN，如 `B06XZTZ7GB` |

### 出参

| 字段 | 类型 | 说明 |
|------|------|------|
| `entities` | array | ASIN 流量得分列表 |
| `total` | integer | 返回条数 |
| `title` | string | 固定 `"ASIN流量得分"` |
**`entities[]` 元素**

| 字段 | 类型 | 说明 |
|------|------|------|
| `country` | string | 站点国家代码 |
| `asin` | string | ASIN |
| `organicTrafficScore` | integer | 近 7 天自然流量得分 |
| `advertisingTrafficScore` | integer | 近 7 天广告流量得分 |
| `totalTrafficScore` | integer | 近 7 天总流量得分 |
| `organicSearchTermCount` | integer | 近 7 天自然关键词数量 |
| `advertisingSearchTermCount` | integer | 近 7 天广告关键词数量 |
| `previous7DaysOrganicTrafficScore` | integer | 前一个 7 天自然流量得分 |
| `previous7DaysAdvertisingTrafficScore` | integer | 前一个 7 天广告流量得分 |
| `previous7DaysTotalTrafficScore` | integer | 前一个 7 天总流量得分 |
| `organicTrafficScoreRatio` | number | 近 7 天自然流量得分占比 |
| `advertisingTrafficScoreRatio` | number | 近 7 天广告流量得分占比 |
| `organicTrafficScoreGrowthRate` | number | 近 7 天自然流量得分环比增长率 |
| `advertisingTrafficScoreGrowthRate` | number | 近 7 天广告流量得分环比增长率 |
| `totalTrafficScoreGrowthRate` | number | 近 7 天总流量得分环比增长率 |

---

## 2. ASIN 商品信息 — `asinInfo`

| 项目 | 说明 |
|------|------|
| **路由** | `POST /xiyou/asinInfo` |
| **上游** | `POST v1/asins/info` |
| **计费** | 每 5 个 ASIN 计 1 Credit |
| **用途** | 批量查询 ASIN 的标题、价格、评分等基础商品信息 |

### 入参

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `entities` | array | 是 | ASIN 查询实体列表，最多 100 个 |
| `entities[].country` | string | 是 | 站点国家代码 |
| `entities[].asin` | string | 是 | 10 位 ASIN |

### 出参

| 字段 | 类型 | 说明 |
|------|------|------|
| `entities` | array | ASIN 商品信息列表 |
| `total` | integer | 返回条数 |
| `title` | string | 固定 `"ASIN商品信息"` |
**`entities[]` 元素**

| 字段 | 类型 | 说明 |
|------|------|------|
| `country` | string | 站点国家代码 |
| `asin` | string | ASIN |
| `amazonUrl` | string | Listing 链接 |
| `smallPicUrl` | string | 主图 URL（128px） |
| `bigPicUrl` | string | 主图 URL（512px） |
| `currency` | string | 货币代码 |
| `price` | string | 价格 |
| `ratings` | integer | 评论数 |
| `stars` | string | 星级评分 |
| `title` | string | 商品标题 |

---

## 3. ASIN 基础信息变动趋势（天） — `asinInfoChangeTrend`

| 项目 | 说明 |
|------|------|
| **路由** | `POST /xiyou/asinInfoChangeTrend` |
| **上游** | `POST v1/asins/infoChange/trends/daily` |
| **计费** | 每 10 天计 1 Credit |
| **用途** | 查询单个 ASIN 基础信息（标题/价格等）按天的变动前后快照 |

### 入参

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `country` | string | 否 | `US` | 站点 |
| `asin` | string | 是 | — | 10 位 ASIN |
| `startDate` | string | 是 | — | 开始日期 `YYYY-MM-DD` |
| `endDate` | string | 是 | — | 结束日期 `YYYY-MM-DD` |

### 出参

| 字段 | 类型 | 说明 |
|------|------|------|
| `country` | string | 站点 |
| `asin` | string | ASIN |
| `trends` | array | 变动趋势列表 |
| `total` | integer | 趋势点数量 |
| `title` | string | 标题 |
**`trends[]` 元素**

| 字段 | 类型 | 说明 |
|------|------|------|
| `date` | string | 日期 `YYYY-MM-DD` |
| `previous` | object | 变化前快照（ASIN 快照对象，见下） |
| `current` | object | 变化后快照（ASIN 快照对象，见下） |

**`previous` / `current`（ASIN 快照）字段**

| 字段 | 类型 | 说明 |
|------|------|------|
| `title` | string | 标题 |
| `imageUrl` | string | 主图 URL |
| `priceDisplay` | string | 价格展示文案 |
| `priceOrigin` | string | 价格原始值 |
| `priceDisplayType` | string | 价格展示类型 |

---

## 4. ASIN 流量得分趋势（天） — `asinTrafficScoreTrend`

| 项目 | 说明 |
|------|------|
| **路由** | `POST /xiyou/asinTrafficScoreTrend` |
| **上游** | `POST v1/asins/trafficScore/trend/daily` |
| **计费** | 每 10 天计 1 Credit |
| **用途** | 查询单个 ASIN 流量得分按天趋势（自然/广告汇总 + 各展示位） |

### 入参

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `country` | string | 否 | `US` | 站点 |
| `asin` | string | 是 | — | 10 位 ASIN |
| `startDate` | string | 是 | — | 开始日期 `YYYY-MM-DD` |
| `endDate` | string | 是 | — | 结束日期 `YYYY-MM-DD` |

### 出参

| 字段 | 类型 | 说明 |
|------|------|------|
| `country` | string | 站点 |
| `asin` | string | ASIN |
| `trends` | array | 流量得分趋势 |
| `total` | integer | 趋势点数量 |
**`trends[]` 元素**

| 字段 | 类型 | 说明 |
|------|------|------|
| `date` | string | 日期 `YYYY-MM-DD` |
| `summaryTrafficScore` | object | 自然/广告流量得分汇总，键：`organic`、`advertising` |
| `positionTrafficScore` | object | 各展示位流量得分，键：`or`/`sp`/`ac`/`er`/`sb`/`sbv`/`hr`/`trb`/`cpf`/`oor`/`sor` |

---

## 5. ASIN 广告信息变动趋势（天） — `asinAdvertisingChangeTrend`

| 项目 | 说明 |
|------|------|
| **路由** | `POST /xiyou/asinAdvertisingChangeTrend` |
| **上游** | `POST v1/asins/advertisingChange/trends/daily` |
| **计费** | 每 10 天计 1 Credit |
| **用途** | 查询单个 ASIN 广告活动按天的新增/停止变动 |

### 入参

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `country` | string | 否 | `US` | 站点 |
| `asin` | string | 是 | — | 10 位 ASIN |
| `startDate` | string | 是 | — | 开始日期 `YYYY-MM-DD` |
| `endDate` | string | 是 | — | 结束日期 `YYYY-MM-DD` |

### 出参

| 字段 | 类型 | 说明 |
|------|------|------|
| `country` | string | 站点 |
| `asin` | string | ASIN |
| `trends` | array | 广告变动趋势列表 |
| `total` | integer | 趋势点数量 |
**`trends[]` 元素**

| 字段 | 类型 | 说明 |
|------|------|------|
| `date` | string | 日期 `YYYY-MM-DD` |
| `added` | array | 新增广告活动列表（广告活动对象，见下） |
| `removed` | array | 停止广告活动列表（广告活动对象，见下） |

**`added[]` / `removed[]`（广告活动）字段**

| 字段 | 类型 | 说明 |
|------|------|------|
| `campaignId` | string | 广告活动 ID |
| `campaignName` | string | 广告活动名称 |
| `campaignType` | string | 广告类型：`sp` / `sb` / `sbv` |

---

## 6. ASIN BSR 排名趋势（天） — `asinBsrTrend`

| 项目 | 说明 |
|------|------|
| **路由** | `POST /xiyou/asinBsrTrend` |
| **上游** | `POST v1/asins/bsrInfo/trends/daily` |
| **计费** | 每 10 天计 1 Credit |
| **用途** | 查询单个 ASIN 各类目 BSR 排名按天趋势 |

### 入参

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `country` | string | 否 | `US` | 站点 |
| `asin` | string | 是 | — | 10 位 ASIN |
| `startDate` | string | 是 | — | 开始日期 `YYYY-MM-DD` |
| `endDate` | string | 是 | — | 结束日期 `YYYY-MM-DD` |

### 出参

| 字段 | 类型 | 说明 |
|------|------|------|
| `country` | string | 站点 |
| `asin` | string | ASIN |
| `categoryTree` | array | 类目树字典（见下） |
| `trends` | array | BSR 排名趋势（见下） |
| `total` | integer | 趋势点数量 |
**`categoryTree[]` 元素**

| 字段 | 类型 | 说明 |
|------|------|------|
| `categoryId` | string | 类目 ID |
| `name` | string | 类目名称 |
| `root` | boolean | 是否大类（true=大类，false=小类） |

**`trends[]` 元素**

| 字段 | 类型 | 说明 |
|------|------|------|
| `date` | string | 日期 `YYYY-MM-DD` |
| `values` | array | 各类目当日 BSR 排名，元素含 `categoryId`、`rank` |

---

## 7. ASIN 订单量趋势（月） — `asinOrdersTrend`

| 项目 | 说明 |
|------|------|
| **路由** | `POST /xiyou/asinOrdersTrend` |
| **上游** | `POST v1/asins/orders/trends` |
| **计费** | 每 6 个月计 1 Credit |
| **用途** | 查询单个 ASIN 按月订单量趋势 |

### 入参

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `country` | string | 否 | `US` | 站点 |
| `asin` | string | 是 | — | 10 位 ASIN |
| `startMonth` | string | 是 | — | 开始月份 `YYYY-MM` |
| `endMonth` | string | 是 | — | 结束月份 `YYYY-MM` |

### 出参

| 字段 | 类型 | 说明 |
|------|------|------|
| `country` | string | 站点 |
| `asin` | string | ASIN |
| `trends` | array | 订单量趋势列表 |
| `total` | integer | 趋势点数量 |
**`trends[]` 元素**

| 字段 | 类型 | 说明 |
|------|------|------|
| `date` | string | 月份 `YYYY-MM` |
| `orders` | integer | 订单量 |

---

## 8. ASIN 商品信息趋势（天） — `asinInfoDailyTrend`

| 项目 | 说明 |
|------|------|
| **路由** | `POST /xiyou/asinInfoDailyTrend` |
| **上游** | `POST v1/asins/info/trends/daily` |
| **计费** | 每 10 天计 1 Credit |
| **用途** | 查询单个 ASIN 评论数、评分、价格/促销按天趋势 |

### 入参

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `country` | string | 否 | `US` | 站点 |
| `asin` | string | 是 | — | 10 位 ASIN |
| `startDate` | string | 是 | — | 开始日期 `YYYY-MM-DD` |
| `endDate` | string | 是 | — | 结束日期 `YYYY-MM-DD` |

### 出参

| 字段 | 类型 | 说明 |
|------|------|------|
| `country` | string | 站点 |
| `asin` | string | ASIN |
| `trends` | array | 商品信息趋势列表 |
| `total` | integer | 趋势点数量 |
**`trends[]` 元素**

| 字段 | 类型 | 说明 |
|------|------|------|
| `date` | string | 日期 `YYYY-MM-DD` |
| `ratings` | integer | 评论数 |
| `stars` | string | 星级评分 |
| `priceDistribution` | object | 价格及促销数据（见下） |

**`priceDistribution`（价格分布）字段**

| 字段 | 类型 | 说明 |
|------|------|------|
| `display` | string | 展示价格 |
| `deal` | string | Deal 价格 |
| `strikethrough` | string | 划线价 |
| `prime` | string | Prime 价格 |
| `promotion` | string[] | Promotion 列表 |
| `coupon` | string[] | Coupon 列表 |
| `subscribe` | string[] | Subscription 列表 |
| `other` | string[] | 其它促销列表 |

---

## 9. ASIN 反查关键词列表（最近天） — `asinResearchPeriod`

| 项目 | 说明 |
|------|------|
| **路由** | `POST /xiyou/asinResearchPeriod` |
| **上游** | `POST v1/asins/research/list/period` |
| **计费** | 每 50 个关键词计 1 Credit |
| **用途** | 反查某 ASIN 最近周期（默认近 7 天）带来流量的搜索词 |

### 入参

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `country` | string | 否 | `US` | 站点 |
| `asin` | string | 是 | — | 10 位 ASIN |
| `page` | integer | 否 | `1` | 页码 |
| `pageSize` | integer | 否 | `100` | 每页条数，最多 10000 |
| `period` | string | 否 | `last7days` | 最近周期，目前仅 `last7days` |
| `sortField` | string | 否 | `traffic` | 排序字段，可选值见下 |
| `sortOrder` | string | 否 | `desc` | `asc` / `desc` |

**`sortField` 可选值**：`traffic`、`organicTraffic`、`advertisingTraffic`、`trafficAcquisitionRate`、`organicTrafficAcquisitionRate`、`advertisingTrafficAcquisitionRate`、`orRank`、`spRank`

### 出参

| 字段 | 类型 | 说明 |
|------|------|------|
| `list` | array | 反查关键词列表 |
| `total` | integer | 总条数（1 个关键词 = 1 条） |
| `title` | string | 标题 |
**`list[]` 元素**

| 字段 | 类型 | 说明 |
|------|------|------|
| `country` | string | 站点 |
| `searchTerm` | string | 关键词 |
| `ranks` | array | 各展示位排名（排名对象，见下） |
| `trafficSummary` | object | 流量汇总（见下） |

**`ranks[]`（排名）字段**

| 字段 | 类型 | 说明 |
|------|------|------|
| `position` | string | 展示位：`or` / `sp` / `sb` / `sbv` / `sor` 等 |
| `page` | integer | 页码 |
| `pageRank` | integer | 页内排名 |
| `totalRank` | integer | 总排名 |
| `rankTime` | string | 排名时间（ISO 8601） |

**`trafficSummary` 字段**

| 字段 | 类型 | 说明 |
|------|------|------|
| `traffic` | object | 流量对象（见下「流量字段」） |
| `trafficAcquisitionRate` | object | 流量获得率对象（见下「流量获得率字段」） |

**流量字段（`traffic`）**

| 字段 | 类型 | 说明 |
|------|------|------|
| `total` | integer | 总流量 |
| `organic` | integer | 自然流量 |
| `advertising` | integer | 广告流量 |
| `totalGrowthRate` | string | 总流量环比增长率 |
| `organicGrowthRate` | string | 自然流量环比增长率 |
| `advertisingGrowthRate` | string | 广告流量环比增长率 |

**流量获得率字段（`trafficAcquisitionRate`）**

| 字段 | 类型 | 说明 |
|------|------|------|
| `total` | string | 总流量获得率 |
| `organic` | string | 自然流量获得率 |
| `advertising` | string | 广告流量获得率 |
| `totalGrowthRate` | string | 总流量获得率环比增长率 |
| `organicGrowthRate` | string | 自然流量获得率环比增长率 |
| `advertisingGrowthRate` | string | 广告流量获得率环比增长率 |

---

## 10. ASIN 反查关键词列表（月） — `asinResearchMonthly`

| 项目 | 说明 |
|------|------|
| **路由** | `POST /xiyou/asinResearchMonthly` |
| **上游** | `POST v1/asins/research/list/monthly` |
| **计费** | 每 50 个关键词计 1 Credit |
| **用途** | 反查某 ASIN 指定月份区间带来流量的搜索词 |

### 入参

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `country` | string | 否 | `US` | 站点 |
| `asin` | string | 是 | — | 10 位 ASIN |
| `page` | integer | 否 | `1` | 页码 |
| `pageSize` | integer | 否 | `100` | 每页条数，最多 10000 |
| `startMonth` | string | 是 | — | 开始月份 `YYYY-MM` |
| `endMonth` | string | 是 | — | 结束月份 `YYYY-MM` |
| `sortField` | string | 否 | `traffic` | 排序字段，可选值见下 |
| `sortOrder` | string | 否 | `desc` | `asc` / `desc` |

**`sortField` 可选值**：`traffic`、`organicTraffic`、`advertisingTraffic`、`trafficAcquisitionRate`、`organicTrafficAcquisitionRate`、`advertisingTrafficAcquisitionRate`、`orRank`、`spRank`

### 出参

| 字段 | 类型 | 说明 |
|------|------|------|
| `list` | array | 反查关键词列表 |
| `total` | integer | 总条数（1 个关键词 = 1 条） |
| `title` | string | 标题 |
**`list[]` 元素**

| 字段 | 类型 | 说明 |
|------|------|------|
| `country` | string | 站点 |
| `searchTerm` | string | 关键词 |
| `ranks` | array | 各展示位排名（排名对象，见下） |
| `trafficSummary` | object | 流量汇总（见下） |

**`ranks[]`（排名）字段**

| 字段 | 类型 | 说明 |
|------|------|------|
| `position` | string | 展示位：`or` / `sp` / `sb` / `sbv` / `sor` 等 |
| `page` | integer | 页码 |
| `pageRank` | integer | 页内排名 |
| `totalRank` | integer | 总排名 |
| `rankTime` | string | 排名时间（ISO 8601） |

**`trafficSummary` 字段**

| 字段 | 类型 | 说明 |
|------|------|------|
| `traffic` | object | 流量对象（含 `total`/`organic`/`advertising` 及各自 `GrowthRate`） |
| `trafficAcquisitionRate` | object | 流量获得率对象（含 `total`/`organic`/`advertising` 及各自 `GrowthRate`） |

---

## 11. 获取 ASIN 变体 — `asinVariations`

| 项目 | 说明 |
|------|------|
| **路由** | `POST /xiyou/asinVariations` |
| **上游** | `POST v1/asins/variations` |
| **计费** | 固定 2 Credit |
| **用途** | 查询单个 ASIN 的父体/子体变体关系 |

### 入参

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `country` | string | 否 | `US` | 站点 |
| `asin` | string | 是 | — | 10 位 ASIN |

### 出参

| 字段 | 类型 | 说明 |
|------|------|------|
| `asin` | string | ASIN |
| `country` | string | 站点 |
| `parentAsin` | string | 父体 ASIN |
| `childAsins` | string[] | 子体 ASIN 列表 |
| `lastUpdatedTime` | string | 最后更新时间 |
| `title` | string | 固定 `"ASIN变体关系"` |
| `total` | integer | 固定 `1` |

---

# 二、ASIN + 关键词模块

## 12. ASIN 词流量趋势（天） — `asinSearchTermTrafficTrend`

| 项目 | 说明 |
|------|------|
| **路由** | `POST /xiyou/asinSearchTermTrafficTrend` |
| **上游** | `POST v1/asinSearchTerms/traffic/trend/daily` |
| **计费** | 每 10 天计 1 Credit |
| **用途** | 查询某 ASIN 在某关键词下的流量按天趋势 |

### 入参

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `country` | string | 否 | `US` | 站点 |
| `asin` | string | 是 | — | 10 位 ASIN |
| `searchTerm` | string | 是 | — | 亚马逊搜索关键词 |
| `startDate` | string | 是 | — | 开始日期 `YYYY-MM-DD` |
| `endDate` | string | 是 | — | 结束日期 `YYYY-MM-DD` |

### 出参

| 字段 | 类型 | 说明 |
|------|------|------|
| `asin` | string | ASIN |
| `country` | string | 站点 |
| `searchTerm` | string | 关键词 |
| `trends` | array | 词流量趋势列表 |
| `total` | integer | 趋势点数量 |
**`trends[]` 元素**

| 字段 | 类型 | 说明 |
|------|------|------|
| `date` | string | 日期 `YYYY-MM-DD` |
| `summaryTraffic` | object | 自然/广告流量汇总，键：`organic`、`advertising` |
| `positionTraffic` | object | 各展示位流量，键：`or`/`sp`/`sb`/`sbv`/`oor`/`sor` |
| `positionTrafficAcquisitionRate` | object | 各展示位流量获得率（键同上，值为 number） |

---

## 13. ASIN 词排名趋势（天） — `asinSearchTermRankTrendDaily`

| 项目 | 说明 |
|------|------|
| **路由** | `POST /xiyou/asinSearchTermRankTrendDaily` |
| **上游** | `POST v1/asinSearchTerms/rank/trends/daily` |
| **计费** | 每 10 天计 1 Credit |
| **用途** | 查询某 ASIN 在某关键词下各展示位排名按天趋势 |

### 入参

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `country` | string | 否 | `US` | 站点 |
| `asin` | string | 是 | — | 10 位 ASIN |
| `searchTerm` | string | 是 | — | 亚马逊搜索关键词 |
| `startDate` | string | 是 | — | 开始日期 `YYYY-MM-DD` |
| `endDate` | string | 是 | — | 结束日期 `YYYY-MM-DD` |

### 出参

| 字段 | 类型 | 说明 |
|------|------|------|
| `asin` | string | ASIN |
| `country` | string | 站点 |
| `searchTerm` | string | 关键词 |
| `trends` | array | 排名趋势列表 |
| `total` | integer | 趋势点数量 |
**`trends[]` 元素**

| 字段 | 类型 | 说明 |
|------|------|------|
| `date` | string | 日期 `YYYY-MM-DD` |
| `displayPositions` | array | 各展示位排名（展示位排名对象，见下） |

**`displayPositions[]`（展示位排名）字段**

| 字段 | 类型 | 说明 |
|------|------|------|
| `displayPosition` | string | 展示位：`or` / `sp` / `sb` / `sbv` / `oor` / `sor` 等 |
| `page` | integer | 页码 |
| `pageRank` | integer | 页内排名 |
| `totalRank` | integer | 总排名 |

---

## 14. ASIN 词排名趋势（小时） — `asinSearchTermRankTrendHourly`

| 项目 | 说明 |
|------|------|
| **路由** | `POST /xiyou/asinSearchTermRankTrendHourly` |
| **上游** | `POST v1/asinSearchTerms/rank/trends/hourly` |
| **计费** | 固定 2 Credit |
| **用途** | 查询某 ASIN 在某关键词下单日内各展示位排名按小时趋势 |
| **站点限制** | **仅支持** `US` / `UK` / `DE` |

### 入参

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `country` | string | 否 | `US` | **仅** `US` / `UK` / `DE` |
| `asin` | string | 是 | — | 10 位 ASIN |
| `searchTerm` | string | 是 | — | 搜索关键词 |
| `date` | string | 是 | — | 查询日期 `YYYY-MM-DD`（单次仅 1 天） |

### 出参

| 字段 | 类型 | 说明 |
|------|------|------|
| `asin` | string | ASIN |
| `country` | string | 站点 |
| `searchTerm` | string | 关键词 |
| `trends` | array | 排名趋势列表（结构同路由 13，但 `date` 为 ISO 时间戳） |
| `total` | integer | 趋势点数量 |
**`trends[]` 元素**

| 字段 | 类型 | 说明 |
|------|------|------|
| `date` | string | ISO 时间戳（精确到小时） |
| `displayPositions` | array | 各展示位排名（展示位排名对象，见下） |

**`displayPositions[]`（展示位排名）字段**

| 字段 | 类型 | 说明 |
|------|------|------|
| `displayPosition` | string | 展示位：`or` / `sp` / `sb` / `sbv` / `oor` / `sor` 等 |
| `page` | integer | 页码 |
| `pageRank` | integer | 页内排名 |
| `totalRank` | integer | 总排名 |

---

# 三、关键词模块

## 15. 关键词分析列表（最近天） — `searchTermAnalysisPeriod`

| 项目 | 说明 |
|------|------|
| **路由** | `POST /xiyou/searchTermAnalysisPeriod` |
| **上游** | `POST v1/searchTerms/analysis/list/period` |
| **计费** | 每 50 个 ASIN 计 1 Credit |
| **用途** | 查询某关键词下抢占流量的 ASIN 列表及其流量/排名/占比 |

### 入参

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `searchTerm` | string | 是 | — | 搜索关键词 |
| `country` | string | 否 | `US` | 站点 |
| `page` | integer | 否 | `1` | 页码 |
| `pageSize` | integer | 否 | `100` | 每页条数，最多 10000 |
| `period` | string | 否 | `last7days` | 最近周期 |
| `sortField` | string | 否 | `traffic` | 排序字段，可选值见下 |
| `sortOrder` | string | 否 | `desc` | `asc` / `desc` |

**`sortField` 可选值**：`traffic`、`organicTraffic`、`advertisingTraffic`、`trafficAcquisitionRate`、`organicTrafficAcquisitionRate`、`advertisingTrafficAcquisitionRate`、`orRank`、`spRank`、`trafficRatio`

### 出参

| 字段 | 类型 | 说明 |
|------|------|------|
| `searchTerm` | string | 查询的关键词 |
| `country` | string | 站点 |
| `list` | array | 关键词下 ASIN 分析列表 |
| `total` | integer | 总条数（1 个 ASIN = 1 条） |
**`list[]` 元素**

| 字段 | 类型 | 说明 |
|------|------|------|
| `country` | string | 站点 |
| `asin` | string | ASIN |
| `ranks` | array | 各展示位排名（排名对象，见下） |
| `trafficSummary` | object | 流量汇总（见下） |
| `asinInfo` | object | ASIN 商品信息（见下） |

**`ranks[]`（排名）字段**

| 字段 | 类型 | 说明 |
|------|------|------|
| `position` | string | 展示位：`or` / `sp` / `sb` / `sbv` / `sor` 等 |
| `page` | integer | 页码 |
| `pageRank` | integer | 页内排名 |
| `totalRank` | integer | 总排名 |
| `rankTime` | string | 排名时间（ISO 8601） |

**`trafficSummary` 字段**

| 字段 | 类型 | 说明 |
|------|------|------|
| `traffic` | object | 流量对象，含 `total`/`organic`/`advertising` 及各自环比 `GrowthRate` |
| `trafficRatio` | object | 占词总流量比例，含 `total`/`organic`/`advertising` |
| `trafficAcquisitionRate` | object | 流量获得率，含 `total`/`organic`/`advertising` 及各自环比 `GrowthRate` |

**`asinInfo` 字段**

| 字段 | 类型 | 说明 |
|------|------|------|
| `country` | string | 站点 |
| `asin` | string | ASIN |
| `amazonUrl` | string | 商品链接 |
| `picUrl` | string | 主图 |
| `currency` | string | 货币 |
| `price` | number | 价格 |
| `ratings` | integer | 评论数 |
| `stars` | number | 评分 |
| `title` | string | 标题 |

---

## 16. 关键词 ABA 数据趋势（周） — `searchTermAbaWeeklyTrend`

| 项目 | 说明 |
|------|------|
| **路由** | `POST /xiyou/searchTermAbaWeeklyTrend` |
| **上游** | `POST v1/searchTerms/abaReport/trends/weekly` |
| **计费** | ⌈关键词数 ÷ 50⌉ × 周数；最长 52 周 |
| **用途** | 查询多个关键词的 ABA 搜索频率排名、周搜索量、Top ASIN 份额按周趋势 |

### 入参

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `country` | string | 否 | `US` | 站点 |
| `searchTerms` | string | 是 | — | 关键词，英文逗号分隔，最多 100 个 |
| `startWeekStartDate` | string | 是 | — | 起始周开始日期 `YYYY-MM-DD` |
| `startWeekEndDate` | string | 是 | — | 起始周结束日期 `YYYY-MM-DD` |
| `endWeekStartDate` | string | 是 | — | 结束周开始日期 `YYYY-MM-DD` |
| `endWeekEndDate` | string | 是 | — | 结束周结束日期 `YYYY-MM-DD` |

### 出参

| 字段 | 类型 | 说明 |
|------|------|------|
| `entities` | array | 各关键词 ABA 周趋势 |
| `total` | integer | 返回关键词数量 |
**`entities[]` 元素**

| 字段 | 类型 | 说明 |
|------|------|------|
| `country` | string | 站点 |
| `searchTerm` | string | 关键词 |
| `trends` | array | ABA 周趋势列表（见下） |

**`trends[]` 元素**

| 字段 | 类型 | 说明 |
|------|------|------|
| `reportFromDate` | string | 报告开始日期 `YYYY-MM-DD` |
| `reportToDate` | string | 报告结束日期 `YYYY-MM-DD` |
| `searchFrequencyRank` | integer | 搜索频率排名 |
| `weeklySearchVolume` | integer | 周搜索量 |
| `topAsins` | array | Top3 ASIN 份额（见下） |

**`topAsins[]`（ABA Top ASIN）字段**

| 字段 | 类型 | 说明 |
|------|------|------|
| `asin` | string | ASIN |
| `clickShare` | string | 点击份额 |
| `conversionShare` | string | 转化份额 |

---

## 17. 关键词信息（最近一周） — `searchTermInfo`

| 项目 | 说明 |
|------|------|
| **路由** | `POST /xiyou/searchTermInfo` |
| **上游** | `POST v1/searchTerms/info` |
| **计费** | 每 50 个关键词计 1 Credit |
| **用途** | 查询多个关键词的转化率、竞争难度、ABA 报告、建议竞价 |

### 入参

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `country` | string | 否 | `US` | 站点 |
| `searchTerms` | string | 是 | — | 关键词，英文逗号分隔，最多 100 个 |
| `sortField` | string | 否 | `weeklySearchVolume` | 排序字段，可选值见下 |
| `sortOrder` | string | 否 | `desc` | `asc` / `desc` |

**`sortField` 可选值**：`clickConversionRate`、`searchTermCompetitiveDifficulty`、`organicRotation`、`searchFrequencyRank`、`weeklySearchVolume`

### 出参

| 字段 | 类型 | 说明 |
|------|------|------|
| `country` | string | 站点 |
| `list` | array | 关键词信息列表 |
| `total` | integer | 总条数（1 个关键词 = 1 条） |
**`list[]` 元素**

| 字段 | 类型 | 说明 |
|------|------|------|
| `searchTerm` | string | 搜索关键词 |
| `clickConversionRate` | string | 点击转化率（均值） |
| `competitiveDifficulty` | integer | 竞争难度 |
| `organicRotation` | string | 自然滚动率 |
| `abaReport` | object | ABA 报告（见下） |
| `costPerClick` | object | 建议竞价（见下） |

**`abaReport` 字段**

| 字段 | 类型 | 说明 |
|------|------|------|
| `reportFromDate` | string | 报告开始日期 `YYYY-MM-DD` |
| `reportToDate` | string | 报告结束日期 `YYYY-MM-DD` |
| `searchFrequencyRank` | integer | 搜索频率排名 |
| `weeklySearchVolume` | integer | 周搜索量 |
| `topAsins` | array | Top3 ASIN 份额，元素含 `asin`、`clickShare`、`conversionShare` |

**`costPerClick`（建议竞价）字段**

| 字段 | 类型 | 说明 |
|------|------|------|
| `value` | string | 建议 CPC 值 |
| `minSuggestedBid` | string | 最低建议出价 |
| `maxSuggestedBid` | string | 最高建议出价 |

---

## 路由索引

| # | 路由 | 摘要 | 上游 API |
|---|------|------|----------|
| 1 | `asinTraffic` | ASIN 流量得分 | `v1/asins/traffic` |
| 2 | `asinInfo` | ASIN 商品信息 | `v1/asins/info` |
| 3 | `asinInfoChangeTrend` | ASIN 基础信息变动趋势（天） | `v1/asins/infoChange/trends/daily` |
| 4 | `asinTrafficScoreTrend` | ASIN 流量得分趋势（天） | `v1/asins/trafficScore/trend/daily` |
| 5 | `asinAdvertisingChangeTrend` | ASIN 广告信息变动趋势（天） | `v1/asins/advertisingChange/trends/daily` |
| 6 | `asinBsrTrend` | ASIN BSR 排名趋势（天） | `v1/asins/bsrInfo/trends/daily` |
| 7 | `asinOrdersTrend` | ASIN 订单量趋势（月） | `v1/asins/orders/trends` |
| 8 | `asinInfoDailyTrend` | ASIN 商品信息趋势（天） | `v1/asins/info/trends/daily` |
| 9 | `asinResearchPeriod` | ASIN 反查关键词（最近天） | `v1/asins/research/list/period` |
| 10 | `asinResearchMonthly` | ASIN 反查关键词（月） | `v1/asins/research/list/monthly` |
| 11 | `asinVariations` | 获取 ASIN 变体 | `v1/asins/variations` |
| 12 | `asinSearchTermTrafficTrend` | ASIN 词流量趋势（天） | `v1/asinSearchTerms/traffic/trend/daily` |
| 13 | `asinSearchTermRankTrendDaily` | ASIN 词排名趋势（天） | `v1/asinSearchTerms/rank/trends/daily` |
| 14 | `asinSearchTermRankTrendHourly` | ASIN 词排名趋势（小时） | `v1/asinSearchTerms/rank/trends/hourly` |
| 15 | `searchTermAnalysisPeriod` | 关键词分析列表（最近天） | `v1/searchTerms/analysis/list/period` |
| 16 | `searchTermAbaWeeklyTrend` | 关键词 ABA 数据趋势（周） | `v1/searchTerms/abaReport/trends/weekly` |
| 17 | `searchTermInfo` | 关键词信息（最近一周） | `v1/searchTerms/info` |

---

## Feedback API

> 与上方工具网关 API 独立，勿混用 Base URL。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **Content-Type:** `application/json`

```json
{
  "skillName": "linkfox-xiyou-dongcha",
  "sentiment": "POSITIVE",
  "category": "OTHER",
  "content": "Results were accurate, user was satisfied."
}
```

**Field rules:**
- `skillName`: 使用本 skill YAML frontmatter 中的 `name`
- `sentiment`: `POSITIVE` / `NEUTRAL` / `NEGATIVE`
- `category`: `BUG` / `COMPLAINT` / `SUGGESTION` / `OTHER`
- `content`: 简述用户意图、实际结果与问题或好评原因
