# 极目亚马逊关键词细分市场分析 接口说明

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

## 接口：按关键词获取细分市场信息

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/jiimore/getNicheInfoByKeyword`

### 请求参数

POST Body（JSON）：

#### 必填参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| keyword | string | 是 | 未声明 | 关键词（必填，并根据所选国家，翻译关键词为对应国家的语言），最大长度1000字符 |

#### 站点与分页

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| countryCode | string | 否 | US | 国家编码，可选值：`US`（美国）、`JP`（日本）、`DE`（德国） |
| page | integer | 否 | 1 | 页码（从1开始） |
| pageSize | integer | 否 | 50 | 每页返回数量（10-100） |
| sortField | string | 否 | unitsSoldT7 | 排序字段（枚举见下方排序选项） |
| sortType | string | 否 | desc | 排序方式：`desc`（降序）或 `asc`（升序） |

#### 筛选参数（均为可选）

**商品与价格**：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| productCountMin | integer | 否 | 未声明 | 商品数量（当前）最小值 |
| productCountMax | integer | 否 | 未声明 | 商品数量（当前）最大值 |
| avgPriceMin | number | 否 | 未声明 | 平均价格（当前）最小值 |
| avgPriceMax | number | 否 | 未声明 | 平均价格（当前）最大值 |

**搜索与销售（7天统计）**：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| searchVolumeT7Min | integer | 否 | 未声明 | 搜索量（7天统计）最小值 |
| searchVolumeT7Max | integer | 否 | 未声明 | 搜索量（7天统计）最大值 |
| unitsSoldT7Min | integer | 否 | 未声明 | 销售量（7天统计）最小值 |
| unitsSoldT7Max | integer | 否 | 未声明 | 销售量（7天统计）最大值 |
| clickCountT7Min | integer | 否 | 未声明 | 点击量（7天统计）最小值 |
| clickCountT7Max | integer | 否 | 未声明 | 点击量（7天统计）最大值 |
| clickConversionRateT7Min | number | 否 | 未声明 | 点击转换率（7天统计）最小值，数值范围为0-1，代表0%-100% |
| clickConversionRateT7Max | number | 否 | 未声明 | 点击转换率（7天统计）最大值，数值范围为0-1，代表0%-100% |

**品牌指标**：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| brandCountMin | integer | 否 | 未声明 | 品牌数量最小值 |
| brandCountMax | integer | 否 | 未声明 | 品牌数量最大值 |
| top5BrandsClickShareMin | number | 否 | 未声明 | 前5个品牌所占细分市场的点击量份额最小值，数值范围为0-1，代表0%-100% |
| top5BrandsClickShareMax | number | 否 | 未声明 | 前5个品牌所占细分市场的点击量份额最大值，数值范围为0-1，代表0%-100% |
| avgBrandAgeMin | number | 否 | 未声明 | 平均品牌年龄（当前）最小值 |
| avgBrandAgeMax | number | 否 | 未声明 | 平均品牌年龄（当前）最大值 |
| avgBrandAgeQoqMin | number | 否 | 未声明 | 平均品牌年龄（90天统计）最小值 |
| avgBrandAgeQoqMax | number | 否 | 未声明 | 平均品牌年龄（90天统计）最大值 |
| avgBrandAgeYoyMin | number | 否 | 未声明 | 平均品牌年龄（360天统计）最小值 |
| avgBrandAgeYoyMax | number | 否 | 未声明 | 平均品牌年龄（360天统计）最大值 |

**卖家指标**：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| avgSellingPartnerAgeMin | number | 否 | 未声明 | 平均销售伙伴年龄最小值 |
| avgSellingPartnerAgeMax | number | 否 | 未声明 | 平均销售伙伴年龄最大值 |
| avgSellingPartnerAgeQoqMin | number | 否 | 未声明 | 平均销售伙伴年龄（90天统计）最小值 |
| avgSellingPartnerAgeQoqMax | number | 否 | 未声明 | 平均销售伙伴年龄（90天统计）最大值 |
| avgSellingPartnerAgeYoyMin | number | 否 | 未声明 | 平均销售伙伴年龄（360天统计）最小值 |
| avgSellingPartnerAgeYoyMax | number | 否 | 未声明 | 平均销售伙伴年龄（360天统计）最大值 |

**竞争与广告**：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| top5ProductsClickShareMin | number | 否 | 未声明 | 排名前5位的商品点击份额（当前）最小值，数值范围为0-1，代表0%-100% |
| top5ProductsClickShareMax | number | 否 | 未声明 | 排名前5位的商品点击份额（当前）最大值，数值范围为0-1，代表0%-100% |
| sponsoredProductsPercentageMin | number | 否 | 未声明 | SP广告占比最小值，数值范围为0-1，代表0%-100% |
| sponsoredProductsPercentageMax | number | 否 | 未声明 | SP广告占比最大值，数值范围为0-1，代表0%-100% |
| cpcMediumMin | number | 否 | 未声明 | CPC（当前）最小值 |
| cpcMediumMax | number | 否 | 未声明 | CPC（当前）最大值 |

**新品与退货**：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| launchRateT180Min | number | 否 | 未声明 | 发布商品的成功率（180天统计）最小值，数值范围为0-1，代表0%-100% |
| launchRateT180Max | number | 否 | 未声明 | 发布商品的成功率（180天统计）最大值，数值范围为0-1，代表0%-100% |
| newProductRateT180 | number | 否 | 未声明 | 新商品占比（180天统计）最小值，数值范围为0-1，代表0%-100% |
| returnRateT360Min | number | 否 | 未声明 | 退货率（360天统计）最小值，数值范围为0-1，代表0%-100% |
| returnRateT360Max | number | 否 | 未声明 | 退货率（360天统计）最大值，数值范围为0-1，代表0%-100% |

#### 排序选项

| 值 | 说明 |
|------|------|
| unitsSoldT7 | 7天销量 |
| searchVolumeT7 | 7天搜索量 |
| demand | 需求得分 |
| avgPrice | 商品均价 |
| maximumPrice | 商品最高价 |
| minimumPrice | 商品最低价 |
| productCount | 商品数量 |
| searchConversionRateT7 | 7天搜索转化率 |
| clickConversionRateT7 | 7天点击转化率 |
| searchVolumeGrowthT7 | 搜索增长率 |
| clickCountT7 | 周点击量 |
| clickCountT90 | 90天点击量 |
| brandCount | 品牌数量 |
| top5BrandsClickShare | 前五品牌点击份额 |
| top5ProductsClickShare | 前五商品点击份额 |
| newProductsLaunchedT180 | 180 天新发布商品数 |
| successfulLaunchesT180 | 180 天成功发布商品数 |
| launchRateT180 | 180 天发布成功率 |
| returnRateT360 | 360 天退货率 |
| clickConversionRateT90 | 90天点击转化率 |
| searchConversionRateT90 | 90天搜索转化率 |
| searchVolumeT90 | 90天搜索量 |
| unitsSoldT90 | 90天销量 |
| unitsSoldGrowthT90 | 90天销量增长率 |
| searchVolumeGrowthT90 | 90天搜索增长率 |
| acos | 广告销售成本比 |
| profitRate50 | 50%自然单的利润率 |

#### 参数与使用限制

- 每次查询必须提供关键词，按所选国家使用对应语言：美国英语、日本日语、德国德语；用户提供其他语言时，先翻译再查询。
- 仅支持 US、JP、DE，其他站点编码将被拒绝；缺少关键词无法返回结果。
- 比例、份额和占比筛选均使用 0–1 表示 0%–100%，不可直接传 0–100。
- 每页最多 100 条；分页、排序及范围筛选字段以各表定义为准。不自动改关键词、翻页或改邮编连续试探失败或空结果。
- 请求排序字段采用 T7 / T90 / T180 / T360 等命名，响应使用 Weekly / Quarterly / Semiannual / Annual 等命名；不得假定请求与响应字段同名。

#### 脚本选项与缓存约定

| 选项或配置 | 类型 | 默认值 | 说明 |
|------------|------|--------|------|
| JSON 参数 | string | 无 | 首个位置参数，传入上述请求 JSON。 |
| --inline | CLI flag | 关闭 | 强制全量打印，仍保存完整响应。 |
| --no-cache | CLI flag | 关闭 | 不读写响应缓存；可能产生新的算力消耗。 |
| LINKFOX_TOOL_GATEWAY | string | https://tool-gateway.linkfox.com | 自定义网关基础地址，去除末尾斜杠后拼接接口路径。 |
| LINKFOX_AGENT_API_KEY / LINKFOXAGENT_API_KEY | string | 无 | `LINKFOX_AGENT_API_KEY` 优先，未设置时使用 `LINKFOXAGENT_API_KEY`；均未配置时按认证引导处理。 |
| SESSION_ID / MESSAGE_ID / MODE_ID / APP_NAME | string | 空字符串 | 原样透传同名请求头；SESSION_ID 也用于聚合输出。 |

业务脚本使用公共调用器的单层 24 小时缓存，缓存路径为 `<cwd>/linkfox/.cache/linkfox-jiimore-get-niche-info-by-keyword/`；按参数排序后的 JSON 生成摘要键。同参重用缓存，过期重新请求，命中时附带 `_cache.hit=true`。失败或空结果也会缓存；需要重新获取时由用户决定是否使用 `--no-cache`。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 网关业务状态码，响应判断遵循公共规则。 |
| errmsg | string | 响应消息，错误时说明原因。 |
| errorCode | integer | 业务状态码，200 表示成功，其他值表示业务错误，401 表示未授权；与 `errcode` 是否同时返回以实际响应为准。存在此字段时，还须按下方业务规则判断。 |
| total | integer | 总数 |
| data | array | 细分市场信息列表（见下方细分市场对象字段） |
| columns | array | 渲染的列 |
| title | string | 标题 |
| type | string | 渲染的样式 |
| costToken | integer | 消耗 Token 数量 |

#### 细分市场对象字段（`data` 数组内）

| 字段 | 类型 | 说明 |
|------|------|------|
| nicheId | string | 细分市场ID |
| nicheTitle | string | 细分市场标题 |
| translationZh | string | 细分市场标题(中文) |
| demand | integer | 细分市场得分 |
| productCount | integer | 商品数量 |
| avgPrice | number | 产品均价 |
| minimumPrice | number | 产品最低价 |
| maximumPrice | number | 产品最高价 |
| searchVolumeWeekly | integer | 搜索量（周数据） |
| searchVolumeQuarterly | integer | 搜索量（季度数据） |
| searchVolumeGrowthWeekly | number | 搜索量增长率（周数据） |
| searchVolumeGrowthQuarterly | number | 搜索量增长率（季度数据） |
| unitsSoldWeekly | integer | 销售数量（周数据） |
| unitsSoldQuarterly | integer | 销售数量（季度数据） |
| clickCountWeekly | integer | 点击量（周数据） |
| clickCountQuarterly | integer | 点击量（季度数据） |
| clickToSaleConversionWeekly | number | 点击转换率（周数据） |
| clickConversionRateQuarterly | number | 点击转换率（季度数据） |
| searchConversionRateWeekly | number | 搜索转换率（周数据） |
| searchConversionRateQuarterly | number | 搜索转换率（季度数据） |
| brandCount | integer | 品牌数量 |
| top5BrandsClickShare | number | 前5个品牌所占细分市场的点击量份额 |
| top5ProductsClickShare | number | 排名前5位的商品点击份额 |
| avgBrandAgeNow | number | 平均品牌年龄(当前) |
| avgBrandAgeQuarterly | number | 平均品牌年龄(季度数据) |
| newProductsLaunchedSemiannual | integer | 已发布新产品的数量（半年数据） |
| successfulLaunchedSemiannual | integer | 成功发布商品的数量（半年数据） |
| launchRateSemiannual | number | 发布商品的成功率（半年数据） |
| returnRateAnnual | number | 退货率（全年数据） |
| acos | number | （ACOS）广告销售成本比 |
| profitMarginGt50PctSkuRatio | number | 利润率大于50%的商品比例 |
| breakEvenRatio | number | 盈亏平衡自然占比 |
| cpc | object | CPC 数据，子字段见下表。 |
| categorieList | array | 商品品类列表 |
| referenceAsinImageUrl | string | 细分市场参考图片地址 |

#### CPC 对象字段

| 字段 | 类型 | 说明 |
|------|------|------|
| cpc.high | number | 最高价。 |
| cpc.medium | number | 中间价。 |
| cpc.low | number | 最低价。 |

`categorieList`、`columns` 的元素结构以实际响应为准，不预设元素字段。比例展示时转为百分比，字段的周、季度、半年和全年口径分别保留。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 响应包含 `errorCode` 时，`200` 表示业务成功，其他值表示业务错误；不能仅因 HTTP 成功或 `errcode` 缺失而将其视为成功。若为 `401`，按 `references/onboarding.md` 处理；其他错误依据实际消息解释原因。该业务判断不替代公共响应码规则。
- 查询失败时依据实际消息解释原因，建议核对关键词或放宽筛选；继续查询前说明额外消耗，不自动更换参数连续重试。

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/jiimore/getNicheInfoByKeyword" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
    "keyword": "yoga mat",
    "countryCode": "US",
    "top5BrandsClickShareMax": 0.5,
    "brandCountMin": 20,
    "searchVolumeT7Min": 5000,
    "sortField": "unitsSoldT7",
    "sortType": "desc",
    "page": 1,
    "pageSize": 50
  }'
```

### 场景请求示例

以下六个查询场景的具体参数可作为业务脚本的 JSON 位置参数；这些是请求构造示例，不应自动依次调用。

#### 基础市场探索

美国无线耳机市场，按周销量降序：

```json
{"keyword":"wireless earbuds","countryCode":"US","sortField":"unitsSoldT7","sortType":"desc"}
```

#### 低竞争市场发现

美国瑜伽垫市场，前五品牌点击份额低于 50%、品牌数超过 20，按需求评分降序：

```json
{"keyword":"yoga mat","countryCode":"US","top5BrandsClickShareMax":0.5,"brandCountMin":20,"sortField":"demand","sortType":"desc"}
```

#### 高需求与高转化市场

美国手机壳市场，周搜索量超过一万、点击转化率高于 10%，按周搜索量降序：

```json
{"keyword":"phone case","countryCode":"US","searchVolumeT7Min":10000,"clickConversionRateT7Min":0.1,"sortField":"searchVolumeT7","sortType":"desc"}
```

#### 新品机会分析

美国 LED 灯市场，180 天新品成功率高于 20%、360 天退货率低于 5%，按新品成功率降序：

```json
{"keyword":"LED light","countryCode":"US","launchRateT180Min":0.2,"returnRateT360Max":0.05,"sortField":"launchRateT180","sortType":"desc"}
```

#### 日本市场调研

日本耳机市场，关键词使用日语，按需求评分降序：

```json
{"keyword":"ヘッドホン","countryCode":"JP","sortField":"demand","sortType":"desc"}
```

#### 指定价格带研究

美国背包市场，均价 20–50 美元、SP 广告占比低于 30%，按周销量降序：

```json
{"keyword":"backpack","countryCode":"US","avgPriceMin":20,"avgPriceMax":50,"sponsoredProductsPercentageMax":0.3,"sortField":"unitsSoldT7","sortType":"desc"}
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-jiimore-get-niche-info-by-keyword",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```