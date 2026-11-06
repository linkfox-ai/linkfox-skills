# 卖家精灵商品搜索 接口说明

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

## 接口：商品搜索（productSearch）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/sellersprite/productSearch`

### 请求参数

POST Body（JSON）。以下字段与工具网关当前登记的「卖家精灵-选产品」入参 schema 一致（同步日期 2026-04-30）。

#### 会话 / 网关（可选）

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| chatId | string | 否 | 对话 id，`maxLength` 1000 |
| uid | string | 否 | 用户 id，`maxLength` 1000 |
| requestId | string | 否 | 推送 id，`maxLength` 1000 |
| teamId | string | 否 | 团队 id，`maxLength` 1000 |

#### 搜索与关键词

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| keyword | string | 否 | 搜索关键词；请尽量翻译为对应国家的语言，比如美国用英语关键词，德国用德语关键词等；`maxLength` 10240 |
| matchType | integer | 否 | 匹配方式：1=词组匹配（默认，标题包含关键词词组），2=模糊匹配（覆盖相关词），3=精准匹配（严格字符串匹配） |
| excludeKeywords | string | 否 | 排除关键词；`maxLength` 10240 |
| marketplace | string | 否 | 市场站点代码，默认 `US`。**仅允许** `US`、`UK`、`DE`、`FR`、`JP`、`CA`、`IT`、`ES`、`MX`、`IN`（须符合该枚举，不含 AU、TR 等未列出站点） |

#### 类目筛选

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| nodeLabel | string | 否 | 亚马逊类目名称；`maxLength` 1000 |
| nodeIdPath | string | 否 | 亚马逊类目节点 ID；`maxLength` 1000 |
| filterSubNode | boolean | 否 | 是否筛选子类目节点；仅在 nodeLabel 或 nodeIdPath 有值时生效；传 JSON 布尔值 `true` / `false` |

#### 数据快照

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| dataSnapshotMonth | string | 否 | 商品数据快照年月，格式 `yyyyMM`（如 `202412` 表示2024年12月的数据快照），或 `nearly` 表示最近30天实时数据。默认值：`nearly`。用于历史分析和同期对比，仅支持已存在的历史快照，不支持未来日期；`maxLength` 1000 |

#### 价格与利润

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| minPrice | number | 否 | 最低价格（>= 0） |
| maxPrice | number | 否 | 最高价格（>= 0） |
| minProfit | number | 否 | 最小毛利率，单位 %（1-100） |
| maxProfit | number | 否 | 最大毛利率，单位 %（1-100） |
| minRevenue | number | 否 | 最低月销售额（>= 0） |
| maxRevenue | number | 否 | 最高月销售额（>= 0） |
| minFba | number | 否 | 最低FBA运费（>= 0） |
| maxFba | number | 否 | 最高FBA运费（>= 0） |

#### 销量与BSR

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| minUnits | integer | 否 | 最低月销量（>= 0） |
| maxUnits | integer | 否 | 最高月销量（>= 0） |
| minAmzUnit | integer | 否 | 最低子体近 30 日销量（**仅** `dataSnapshotMonth` 为「近 30 日」类查询时支持）；`minimum` 0 |
| maxAmzUnit | integer | 否 | 最高子体近 30 日销量（**仅**近 30 日查询支持）；`minimum` 0 |
| minUnitsGrowthRate | number | 否 | 月销量最低增长率，单位 % |
| maxUnitsGrowthRate | number | 否 | 月销量最高增长率，单位 % |
| minBsr | integer | 否 | 大类BSR最低排名 |
| maxBsr | integer | 否 | 大类BSR最高排名 |
| minBsrGrowthRate | number | 否 | BSR最低增长率，单位 % |
| maxBsrGrowthRate | number | 否 | BSR最高增长率，单位 % |
| minBsrGrowthCount | integer | 否 | BSR最低增长数 |
| maxBsrGrowthCount | integer | 否 | 大类BSR最高增长数 |
| minSubNodeBsrRank | integer | 否 | 子类目BSR最低排名（需 filterSubNode = true） |
| maxSubNodeBsrRank | integer | 否 | 子类目BSR最大排名（需 filterSubNode = true） |

#### 评分与评论

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| minRating | number | 否 | 最低评分值（0-5） |
| maxRating | number | 否 | 最高评分值（0-5），3.8-4.3为产品改良机会区间 |
| minRatings | integer | 否 | 最低评分数（0-10000） |
| maxRatings | integer | 否 | 最高评分数（0-10000） |
| minRatingsGrowthCount | integer | 否 | 最低月新增评分数（>= 0） |
| maxRatingsGrowthCount | integer | 否 | 最高月新增评分数（>= 0） |
| minListingQualityScore | number | 否 | 最低 Listing 页面质量分（>= 0） |
| maxListingQualityScore | number | 否 | 最高 Listing 页面质量分（>= 0） |

#### 商品属性

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| minVariations | integer | 否 | 最低变体数 |
| maxVariations | integer | 否 | 最高变体数 |
| minWeights | number | 否 | 最小重量（>= 0） |
| maxWeights | number | 否 | 最大重量（>= 0） |
| weightUnit | string | 否 | 重量单位：g、kg、oz、lb。如果参数中包含重量筛选，则必须指定此字段；用户未给单位时先请用户确认，不自行猜测 |
| dimensionType | string | 否 | 包装尺寸类型（各站点代码不同，见下方说明） |
| minSellers | integer | 否 | 最小卖家数量 |
| maxSellers | integer | 否 | 最大卖家数量 |

#### 标识与配送

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| badgeBestSeller | string | 否 | Best Seller 标识筛选：`Y`、`N` 或留空（全部） |
| badgeAmazonsChoice | string | 否 | Amazon's Choice 标识筛选：`Y`、`N` 或留空（全部） |
| badgeNewRelease | string | 否 | New Release 标识筛选：`Y`、`N` 或留空（全部） |
| fulfillment | string | 否 | 配送方式：单选 `AMZ` / `FBA` / `FBM`，或多选如 `AMZ,FBA`、`FBA,FBM`、`AMZ,FBA,FBM` 等；多条件用英文逗号；留空表示不限制 |
| showVariation | string | 否 | 是否查询变体：`Y` 或 `N`，默认 `N` |
| hideUnlistedProduct | boolean | 否 | 是否隐藏已下架商品，默认 `true` |
| listedWithinLastMonths | integer | 否 | 上架时间范围（月），**仅**允许：`1`、`3`、`6`、`12`、`24`（与枚举含义一致，勿传其他整数） |

#### 卖家与品牌

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| sellerNation | string | 否 | 卖家所属地代码（如 US、CN、HK），多条件用逗号隔开，默认不限制 |
| includeSellers | string | 否 | 包含卖家；`maxLength` 10240 |
| excludeSellers | string | 否 | 排除卖家；`maxLength` 10240 |
| includeBrands | string | 否 | 包含品牌；`maxLength` 10240 |
| excludeBrands | string | 否 | 排除品牌；`maxLength` 10240 |

#### 排序与分页

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| order | object | 否 | 排序配置；若传入，须同时提供 `field` 与 `desc`（子 schema 中二者为 required）；默认按 `total_units` 降序 |
| order.field | string | 传 order 时必填 | 排序字段：`total_units`（月销量）、`total_amount`（月销售额）、`bsr_rank`、`price`、`rating`、`reviews`、`profit`、`reviews_rate`、`available_date`、`questions`、`total_units_growth`、`total_amount_growth`、`reviews_increasement`、`bsr_rank_cv`、`bsr_rank_cr`、`amz_unit`（子体销量）。默认 `total_units`。传空字符串 `""` 表示不按上述业务字段排序（查询全部排序语义由服务端处理） |
| order.desc | string | 传 order 时必填 | `"true"` 降序，`"false"` 升序；默认 `"true"`；`maxLength` 1000 |
| page | integer | 否 | 页码，从1开始，默认 1；分页最多只能查询排序结果中的前 2000 条记录 |
| size | integer | 否 | 每页条数（10-100），默认 20；`page * size` 不得超过 2000 |

> **分页上限**：无论 `total` 显示多少条匹配结果，接口最多只能查询当前排序结果中的前 2000 条记录。若需查看第 2000 条之后的数据，请增加或收紧筛选条件后重新查询。


#### 各站点包装尺寸类型代码


##### 美国站（US）

| 代码 | 说明 |
|------|------|
| SS | 小号标准尺寸 |
| LS | 大号标准尺寸 |
| SO | 小号大件 |
| MO | 中号大件 |
| LO / LB | 大号大件 |
| SP | 特殊大件 |
| O | 其他尺寸 |
| ELO | 超大尺寸：0至50磅 |
| EL5O | 超大尺寸：50到70磅（不含50磅） |
| EL7O | 超大尺寸：70至150磅（不含70磅） |
| EL15O | 超大尺寸：150磅以上（不含150磅） |

##### 日本站（JP）

| 代码 | 说明 |
|------|------|
| SM | 小号 |
| ST | 标准 |
| OV | 大件 |
| SS | 超大尺寸 |
| O | 其他尺寸 |

##### 加拿大站（CA）

| 代码 | 说明 |
|------|------|
| EN | 信封装 |
| ST | 标准 |
| SO | 小号大件 |
| MO | 中号大件 |
| LO | 大号大件 |
| SP | 特殊大件 |
| O | 其他尺寸 |

##### 英国 / 法国 / 德国 / 意大利 / 西班牙站（UK / FR / DE / IT / ES）

| 代码 | 说明 |
|------|------|
| SL | 小号信封 |
| NL | 标准信封 |
| LL | 大号信封 |
| ELL | 超大号信封 |
| SM | 小包裹 |
| SD | 标准包裹 |
| SB | 小号大件 |
| NB | 标准大件 |
| LB | 大号大件 |
| SPO | 特殊大件 |
| O | 其他尺寸 |


#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| JSON 参数 | object | 是 | CLI 的首个位置参数；按上述网关字段原样传入。 |
| --inline | CLI flag | 否 | 强制打印完整 JSON，仍保存完整响应。 |
| --no-cache | CLI flag | 否 | 禁用响应缓存的读取和写入；默认启用缓存。 |

- CLI：`python scripts/sellersprite_product_search.py '<JSON 参数>' [--inline] [--no-cache]`。无参数或 JSON 格式无效时退出码为 1，不发送请求。
- 使用公共 `scripts/call_api.py` 的一层缓存，有效期为 24 小时；缓存键为按排序键序列化参数后计算的 SHA-256 前 16 位，缓存路径为 `<cwd>/linkfox/.cache/linkfox-sellersprite-product-search/linkfox-sellersprite-product-search-<hash>.json`。命中对象响应时添加 `_cache.hit=true`；缓存损坏或到期视为未命中。响应未按成功与否区分缓存，错误或空结果也可能被缓存；不要自动绕过缓存连续试探。
- 业务脚本在请求前检查当前工作目录下的会话数据目录可写，并固定公共调用器输出根目录为 `<cwd>/linkfox`；失败即报错，不回退到家目录、`ACPX_WORKSPACES` 或临时目录。禁止将业务输出写到 `/tmp`。
- 完整响应始终以 UTF-8 保存至 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-sellersprite-product-search-<timestamp>.json`，包括缓存命中。文件名冲突时递增时间戳编号并原子占位，避免同一秒内连续查询覆盖既有响应。会话标识优先取 `SESSION_ID`，未设置时进程内生成稳定标识；同时维护 `_meta.json`、`index.jsonl` 和文件登记。
- `LINKFOX_TOOL_GATEWAY` 可覆盖默认网关，去掉地址末尾 `/`；认证优先 `LINKFOX_AGENT_API_KEY`，兼容 `LINKFOXAGENT_API_KEY`。请求携带 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 追踪头。
- 保存后，不超过 8000 字节时打印完整 JSON；超过时打印顶层字段、常见计数、最大列表长度及前 3 条样本，`--inline` 可覆盖摘要选择。摘要递归查找最大列表，不固定商品字段名。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 网关业务状态码，按公共规则判断；可能缺省。 |
| errmsg | string | 网关错误原因，认证失败时可返回 `authorized error`。 |
| errorCode | 未单独约定 | 兼容响应中的业务状态字段；200 表示成功，其他值表示业务错误，未授权时为 401。仅在实际返回此字段时按下方业务规则检查，不替代公共规则中的 `errcode` 判断。 |
| total | integer | 匹配商品总数 |
| products | array | 商品列表（详见下方商品对象字段） |
| columns | array | 渲染的列定义 |
| keyword | string | 搜索使用的关键词（如有） |
| nodeIdPath | string | 搜索的类目节点 |
| nodeLabel | string | 亚马逊类目名称 |
| dataSnapshotMonth | string | 数据查询月份 |
| sourceType | string | 来源类型（如 "amazon"） |
| type | string | 渲染样式 |
| message | string | 附加消息或错误信息 |
| costToken | integer | 消耗token |

#### products[*] 商品对象字段

| 字段 | 类型 | 说明 |
|------|------|------|
| asin | string | 亚马逊ASIN |
| title | string | 商品标题 |
| asinUrl | string | 亚马逊商品详情页URL |
| imageUrl | string | 商品图片URL |
| price | number | 当前价格 |
| averagePrice | number | 平均价格 |
| primePrice | number | Prime价格，-1表示没有 |
| currency | string | 币种 |
| monthlySalesUnits | integer | 月销量 |
| monthlySalesRevenue | number | 月销售额 |
| monthlySalesUnitsGrowthRate | number | 月销量增长率 |
| bsr | integer | BSR排名 |
| bsrGrowthRate | number | BSR增长率 |
| rating | number | 评分 |
| ratings | integer | 评分数 |
| ratingsRate | number | 留评率 |
| profit | number | 毛利率（%） |
| fba | number | FBA运费 |
| sellerNum | integer | 卖家数 |
| sellerId | string | BuyBox卖家ID |
| sellerName | string | BuyBox卖家名称 |
| sellerNation | string | BuyBox卖家国籍 |
| brand | string | 品牌 |
| brandUrl | string | 品牌页URL |
| fulfillment | string | 配送方式（AMZ / FBA / FBM） |
| availableDate | string | 上架时间（时间戳） |
| availableDateString | string | 上架日期（格式化字符串） |
| variationNum | integer | 变体数 |
| variant30DayUnits | integer | 子体月销量（件数） |
| variant30DayRevenue | number | 子体月销售额（金额） |
| variant30DayUpdatedAt | string | 子体数据更新时间 |
| weight | string | 重量 |
| packageWeight | string | 包装重量 |
| dimension | string | 尺寸 |
| packageDimensions | string | 包装尺寸 |
| dimensionsType | string | 尺寸类型 |
| packageDimensionType | string | 包装尺寸类型 |
| listingQualityScore | number | Listing质量得分 |
| deliveryPrice | number | 卖家运费，-1表示没有 |
| nodeLabelPath | string | 类目路径 |
| nodeIdPath | string | 节点ID路径 |
| nodeId | integer | 节点ID |
| dataSnapshotMonth | string | 数据查询月份 |
| badgeBestSeller | string | Best Seller标识（Y/N） |
| badgeAmazonChoice | string | Amazon's Choice标识（Y/N） |
| badgeNewRelease | string | New Release标识（Y/N） |
| badgeVideo | string | 视频介绍（Y/N） |
| badgeEbc | string | A+页面（Y/N） |
| badge | object | 标识汇总对象，包含：bestSeller、amazonChoice、newRelease、video、ebc |
| subcategories | array | 子类目列表，每项包含 code（类目code）、rank（排名）、label（名称） |
| sku | string | SKU |
| keyword | string | 对应筛选的关键词 |
| sourceType | string | 来源类型 |
| sourceTool | string | 来源工具标识 |

#### 商品嵌套字段

以下成员未单独约定类型或必返性；保留实际值，不补造缺失字段。

| 字段 | 类型 | 说明 |
|------|------|------|
| products[*].badge.bestSeller | 未单独约定 | Best Seller 标识。 |
| products[*].badge.amazonChoice | 未单独约定 | Amazon's Choice 标识。 |
| products[*].badge.newRelease | 未单独约定 | New Release 标识。 |
| products[*].badge.video | 未单独约定 | 视频介绍标识。 |
| products[*].badge.ebc | 未单独约定 | A+ 页面标识。 |
| products[*].subcategories[*].code | 未单独约定 | 子类目 code。 |
| products[*].subcategories[*].rank | 未单独约定 | 子类目排名。 |
| products[*].subcategories[*].label | 未单独约定 | 子类目名称。 |

#### 脚本输出附加字段

| 字段 | 类型 | 说明 |
|------|------|------|
| _cache | object | 脚本本地缓存元信息，不是接口业务字段。 |
| _cache.hit | boolean | 缓存命中时由脚本添加为 true。 |
| _http_status | integer | 业务脚本记录的实际 HTTP 状态，不是网关业务字段。缓存命中时保留缓存产生时的状态，不表示重新发起了请求；旧缓存可能无此字段，此时不能推定 HTTP 成功。连接失败、尚未收到 HTTP 响应时不添加此字段。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 使用业务脚本时，以 `_http_status` 作为公共规则中的 HTTP 状态判据，并结合 `errcode` 判断；`401` / `402` 按认证或用量问题处理。缓存命中时说明该状态来自历史响应；若旧缓存缺少 HTTP 状态且结果不明确，不宣告成功，也不自动绕过缓存追加查询。
- 若实际响应带有 `errorCode`，还须按该字段检查业务结果：200 表示业务成功，其他值表示业务错误；401 按认证问题处理。不得因公共规则中的 `errcode` 缺省或正常而忽略此字段报告的错误，也不得将 `errorCode` 缺省当成失败。两种状态字段矛盾时保留原始响应并说明异常，不宣告业务成功。
- 查询失败时结合 `message` 与 `errmsg` 说明原因，保留原始响应。空商品列表表示本次条件未返回商品，不据此认定整个市场没有需求。
- `total` 是匹配总数，可能超过可查询窗口；不能将其等同于可分页获取的条数。收紧筛选后是新的查询，应遵守成本约束。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/sellersprite/productSearch" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
    "keyword": "yoga mat",
    "marketplace": "US",
    "minUnits": 300,
    "minPrice": 10,
    "maxPrice": 50,
    "order": {"field": "total_units", "desc": "true"},
    "page": 1,
    "size": 20
  }'
```

### 响应示例（简略）

```json
{
  "total": 1523,
  "sourceType": "amazon",
  "dataSnapshotMonth": "nearly",
  "keyword": "yoga mat",
  "nodeLabel": "",
  "products": [
    {
      "asin": "B07XXXXXXX",
      "title": "Premium Yoga Mat - Non Slip, Eco Friendly...",
      "price": 29.99,
      "monthlySalesUnits": 12500,
      "monthlySalesRevenue": 374875.0,
      "bsr": 156,
      "rating": 4.6,
      "ratings": 35420,
      "profit": 42.5,
      "fulfillment": "FBA",
      "brand": "ExampleBrand",
      "sellerNation": "CN",
      "availableDateString": "2021-03-15",
      "badgeBestSeller": "Y",
      "badgeAmazonChoice": "N"
    }
  ],
  "message": "",
  "costToken": 1
}
```


---

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-sellersprite-product-search",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
