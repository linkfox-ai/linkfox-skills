# 极目亚马逊同细分市场竞品挖掘 接口说明

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

## 接口：按 ASIN 挖掘同细分市场竞品

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/jiimore/pageAsinsByAsin`

### 请求参数

POST Body（JSON）：

#### 必填参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| asin | string | 是 | 参考 ASIN，用于查询与该 ASIN 同属细分市场（Niche）的竞品列表，最大长度1000字符 |

#### 站点与分页

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| countryCode | string | 否 | US | 仅支持 `US`（美国）、`JP`（日本）、`DE`（德国），其他站点编码会被拒绝。 |
| page | integer | 否 | 1 | 页码（从1开始） |
| pageSize | integer | 否 | 50 | 每页返回数量（10-100） |
| sortField | string | 否 | purchasedClicksT360 | 排序字段（见下方排序选项） |
| sortType | string | 否 | desc | 排序方式：`desc`（降序）或 `asc`（升序） |

#### 筛选参数（均为可选）

**价格与FBA**：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| priceMin | number | 否 | 未声明 | 最低产品价格 |
| priceMax | number | 否 | 未声明 | 最高产品价格 |
| fbaFeeMin | number | 否 | 未声明 | 最低FBA佣金 |
| fbaFeeMax | number | 否 | 未声明 | 最高FBA佣金 |
| grossProfitMarginMin | number | 否 | 未声明 | 最低毛利率，取值范围 0–1，例如 0.3 表示 30%，不使用 0–100。 |
| grossProfitMarginMax | number | 否 | 未声明 | 最高毛利率，取值范围 0–1，例如 0.3 表示 30%，不使用 0–100。 |

**评论与评分**：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| totalReviewsMin | integer | 否 | 未声明 | 最少评论数量 |
| totalReviewsMax | integer | 否 | 未声明 | 最多评论数量 |
| customerRatingMin | number | 否 | 未声明 | 最低评分，取值范围 0.0-5.0 |
| customerRatingMax | number | 否 | 未声明 | 最高评分，取值范围 0.0-5.0 |

**点击数据（7天）**：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| clickCountT7Min | integer | 否 | 未声明 | 最低周点击量 |
| clickCountT7Max | integer | 否 | 未声明 | 最高周点击量 |
| clickCountGrowthT7Min | number | 否 | 未声明 | 最低周点击增长率，取值范围 0-1，例如 0.1 表示 10% |
| clickCountGrowthT7Max | number | 否 | 未声明 | 最高周点击增长率，取值范围 0-1，例如 0.1 表示 10% |
| clickConversionRateMin | number | 否 | 未声明 | 最低点击转化率，取值范围 0-1，例如 0.1 表示 10% |
| clickConversionRateMax | number | 否 | 未声明 | 最高点击转化率，取值范围 0-1，例如 0.1 表示 10% |

**点击数据（30天）**：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| clickCountT30Min | integer | 否 | 未声明 | 最低月点击量 |
| clickCountT30Max | integer | 否 | 未声明 | 最高月点击量 |
| clickCountGrowthT30Min | number | 否 | 未声明 | 最低月点击增长率，取值范围 0-1，例如 0.1 表示 10% |
| clickCountGrowthT30Max | number | 否 | 未声明 | 最高月点击增长率，取值范围 0-1，例如 0.1 表示 10% |

**综合转化率**：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| clickConversionRateCompositeMin | number | 否 | 未声明 | 最低综合点击转化率，取值范围 0-1，例如 0.1 表示 10% |
| clickConversionRateCompositeMax | number | 否 | 未声明 | 最高综合点击转化率，取值范围 0-1，例如 0.1 表示 10% |

**销量与上架时间**：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| salesVolumeT360Min | integer | 否 | 未声明 | 最低 360 天销量 |
| salesVolumeT360Max | integer | 否 | 未声明 | 最高 360 天销量 |
| launchDateMin | string | 否 | 未声明 | 最早上架时间，格式为 yyyyMMdd000000，例如 `20240101000000` 表示 2024 年 1 月 1 日。 |
| launchDateMax | string | 否 | 未声明 | 最晚上架时间，格式为 yyyyMMdd000000 |

**细分市场与卖家**：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| nicheCountMin | integer | 否 | 未声明 | 最少细分市场数量 |
| nicheCountMax | integer | 否 | 未声明 | 最多细分市场数量 |
| sellerCountry | string | 否 | 未声明 | 卖家国家的国家码，选择多个国家的用英文逗号隔开，如：CN,US |

#### 排序选项

| 值 | 说明 |
|------|------|
| purchasedClicksT360 | 360天购买点击（默认） |
| totalReviews | 评论数量 |
| price | 价格 |
| launchDate | 上架时间 |
| clickCountT30 | 30天点击量 |
| clickCountT90 | 90天点击量 |
| clickCountT7 | 7天点击量 |
| clickConversionRate | 点击转化率（7天点击转化率） |
| clickConversionRateComposite | 综合点击转化率 |
| customerRating | 评分 |
| clickCountGrowthT7 | 周点击增长率 |
| clickCountGrowthT30 | 月点击增长率 |
| currentPrice | 当前价格 |
| fbaFee | FBA佣金 |
| shippingFee | FBA运费 |
| gpm | 毛利率 |

#### 脚本选项与运行约定

| 选项或配置 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| JSON 参数 | object | 是 | 无 | 命令行第一个位置参数，作为完整请求体；参数直接透传。 |
| --inline | CLI flag | 否 | 关闭 | 强制全量打印，仍保存完整响应。 |
| --no-cache | CLI flag | 否 | 关闭 | 禁用本次响应缓存读取和写入；仍保存会话数据。 |
| LINKFOX_TOOL_GATEWAY | 环境变量 | 否 | https://tool-gateway.linkfox.com | 网关地址，去掉末尾斜线后拼接接口路径。 |
| LINKFOX_AGENT_API_KEY | 环境变量 | 与兼容变量二选一 | 无 | 首选认证密钥；缺失时读取 `LINKFOXAGENT_API_KEY`。 |
| LINKFOXAGENT_API_KEY | 环境变量 | 与首选变量二选一 | 无 | 兼容认证变量。 |
| SESSION_ID | 环境变量 | 否 | 自动生成 | 会话数据分组；缺省生成进程内稳定的会话编号。 |
| MESSAGE_ID / MODE_ID / APP_NAME | 环境变量 | 否 | 空字符串 | 由公共调用器透传至同名请求头。 |

- 本地响应缓存有效期为 24 小时，路径为 `<cwd>/linkfox/.cache/linkfox-jiimore-page-asins-by-asin/linkfox-jiimore-page-asins-by-asin-<hash>.json`；`hash` 为参数按键排序后序列化的 SHA-256 前 16 位，参数键顺序不影响命中。缓存过期或无法解析时重新请求，命中时添加 `_cache.hit=true`。缓存由公共调用器维护，业务入口不叠加第二层缓存。
- 未禁用缓存时会保存返回结果，包括错误或空结果；不因缓存缺失或结果异常而自动更换条件、翻页或反复请求。
- 每次运行（含缓存命中）保存完整 UTF-8 响应到主文档约定的会话数据路径，并维护 `_meta.json` 与 `index.jsonl`。业务封装以微秒时间戳和独占创建避免同秒调用覆盖已有文件，不改变缓存键。当前工作目录不可写时在请求前报错，不改用家目录或临时目录；忽略 `ACPX_WORKSPACES` 对本业务输出位置的覆盖。
- 全量输出阈值为 8000 字节，超过阈值时展示摘要和最大列表的前 3 条样本；`--inline` 覆盖该阈值。`--no-cache` 仍可能创建空的缓存目录，但不读写响应缓存文件。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 业务状态码；成功与否遵循公共规则，错误示例为 401。 |
| errmsg | string | 返回消息，错误时说明原因，例如 `authorized error`。 |
| errorCode | 未注明 | 可能返回的错误状态字段；若实际返回则原样保留，不据此替代公共 `errcode` 判断。 |
| total | integer | 总记录数 |
| pages | integer | 总页数 |
| page | integer | 当前页 |
| pageSize | integer | 每页大小 |
| data | array | ASIN 产品列表（见下方产品对象字段） |
| columns | array | 渲染的列 |
| type | string | 渲染的样式 |
| costToken | integer | 消耗token |

#### 产品对象字段（`data` 数组内）

| 字段 | 类型 | 说明 |
|------|------|------|
| asin | string | 亚马逊产品ASIN |
| parentAsin | string | 亚马逊产品父ASIN |
| title | string | 产品标题 |
| brand | string | 品牌 |
| price | number | 价格 |
| currentPrice | number | 当前价格 |
| currency | string | 币种 |
| customerRating | number | 评分 |
| totalReviews | integer | 评论数 |
| launchDate | string | 上架时间 |
| link | string | ASIN链接 |
| imagesUrl | string | 产品主图 |
| sellerName | string | 卖家名称 |
| sellerId | string | 卖家ID |
| fbaFee | number | FBA佣金 |
| shippingFee | number | FBA运费 |
| gpm | number | 毛利率 |
| clickConversionRate | number | 点击转化率（7天点击转化率） |
| clickConversionRateComposite | number | 综合点击转化率 |
| clickConversionRateType | string | 转化率计算类型 |
| clickConversionRateCompositeType | string | 综合转化率计算类型 |
| clickCountT7 | integer | 7天点击量 |
| clickCountT30 | integer | 30天点击量 |
| clickCountT90 | integer | 90天点击量 |
| clickCountGrowthT7 | number | 周点击增长率 |
| clickCountGrowthT30 | number | 月点击增长率 |
| purchasedClicksT360 | integer | 360天购买点击 |
| salesVolumeT360 | integer | 360 天销量 |
| nicheCount | integer | 所属细分市场数 |
| sameNicheTitle | string | 同细分市场（Niche）标题 |
| involvedNum | integer | 涉及的关键词数量 |
| involvedFrequency | integer | 涉及的关键词频次 |
| categoryNames | array | 类目信息 |
| hasMetric | boolean | 标识是否有指标 |
| searchValueType | string | 搜索类型: exact(精准匹配), sameNiche(与参考 ASIN 同属细分市场), category(类目) |
| niches | array | top3 细分市场；元素字段见下方细分市场对象表。 |
| bestSellersRanking | array | 畅销榜排名；元素字段见下方畅销榜对象表。 |
| trends | array | 90 天趋势数据；元素字段见下方趋势对象表。 |
| lastUpdateTime | string | 最后更新时间 |

#### data[*].niches[*] 细分市场对象

以下嵌套对象仅约定字段及含义，未约定字段类型、必填性或默认值；以实际响应为准，不补造缺失数据。

| 字段 | 类型 | 说明 |
|------|------|------|
| nicheId | 未注明 | 细分市场编号。 |
| nicheTitle | 未注明 | 细分市场标题。 |
| demand | 未注明 | 市场评分。 |
| image | 未注明 | 细分市场图片。 |
| marketplaceId | 未注明 | 站点标识。 |

#### data[*].bestSellersRanking[*] 畅销榜对象

| 字段 | 类型 | 说明 |
|------|------|------|
| rank | 未注明 | 排名。 |
| category | 未注明 | 类目名称。 |

#### data[*].trends[*] 90 天趋势对象

| 字段 | 类型 | 说明 |
|------|------|------|
| day | 未注明 | 日期。 |
| clickCountT7 | 未注明 | 周点击量。 |
| reviewCount | 未注明 | 评论数。 |
| reviewRating | 未注明 | 评分。 |
| bestSellerRanking | 未注明 | BSR 排名。 |
| averagePriceT7 | 未注明 | 周平均价格。 |
| totalOfferDepthT7 | 未注明 | 7 天新增 offer。 |

`categoryNames`、`columns` 的元素结构未作约定，保留实际返回内容。

#### 脚本附加字段

| 字段 | 类型 | 说明 |
|------|------|------|
| _cache | object | 本地缓存元数据，不是接口原始业务字段。 |
| _cache.hit | boolean | 为 true 时表示本次命中本地缓存。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 公共规则判定正常响应后，空 `data` 表示本次条件下未返回竞品；告知用户核对参考 ASIN 或筛选条件，不自动放宽条件继续付费检索。

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/jiimore/pageAsinsByAsin" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
    "asin": "B0GC4RPX79",
    "countryCode": "US",
    "clickConversionRateCompositeMin": 0.15,
    "clickCountT30Min": 2000,
    "totalReviewsMax": 100,
    "sortField": "clickConversionRateComposite",
    "sortType": "desc",
    "page": 1,
    "pageSize": 50
  }'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-jiimore-page-asins-by-asin",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```