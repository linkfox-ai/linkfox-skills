# Sorftime 亚马逊商品详情与趋势 接口说明

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

## 接口：商品详情与趋势（productDetail）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/sorftime/amazon/productDetail`

### 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| asin | string | 是 | 亚马逊标准识别号（ASIN），支持多个（最多10个），以英文逗号隔开。示例：`B0088PUEPK` 或 `B0088PUEPK,B00U26V4VQ` |
| marketplace | string | 是 | 亚马逊站点代码：us、gb、de、fr、in、ca、jp、es、it、mx、ae、au、br、sa |
| includeTrend | integer | 否 | 是否包含趋势数据。`1`：包含（默认）；`2`：不包含 |
| queryTrendStartDate | string | 否 | 趋势开始日期，格式 `yyyy-MM-dd`。默认仅返回近15天，查询天数>15天时扣费加倍 |
| queryTrendEndDate | string | 否 | 趋势截止日期，格式 `yyyy-MM-dd` |

#### 参数约束与使用限制

| 项目 | 约定 |
|------|------|
| ASIN 批量 | 同站点对比优先在上述数量限制内批量查询，避免逐个调用。 |
| 站点 | 必须显式传入小写代码；用户未指定站点时填 `us`。英国使用 `gb`，不是 `uk`。 |
| 趋势选择 | 只需基本资料时关闭趋势，以减少消耗并缩短响应时间；取值及默认范围见请求表。 |
| 历史范围 | 按用户需要设置起止日期；历史趋势可追溯至 2021 年，以实际返回为准。超出默认范围的计费规则见请求表。 |
| 动态计费 | Sorftime 内部查询次数 × 6；内部次数由 Sorftime 根据查询条件决定，可能一次消耗大量算力。 |
| 二次分析限制 | 返回数据不支持通过 `_dataQuery_executeDynamicQuery` 进行二次分析。 |
| 非标准类目 | 如 Amazon Renewed 等非标准类目或类目变更场景，销量、销售额可能为 `-1`，表示无法预估。 |

#### 支持站点

| 代码 | 站点 | 代码 | 站点 |
|------|------|------|------|
| us | 美国 | gb | 英国 |
| de | 德国 | fr | 法国 |
| in | 印度 | ca | 加拿大 |
| jp | 日本 | es | 西班牙 |
| it | 意大利 | mx | 墨西哥 |
| ae | 阿联酋 | au | 澳大利亚 |
| br | 巴西 | sa | 沙特阿拉伯 |

#### 脚本选项与运行约定

| 参数 / 环境变量 | 类型 | 必填 | 说明 |
|------|------|------|------|
| JSON 参数 | object | 是 | 首个位置参数为请求 JSON，字段与上方请求表一致；脚本不自动补站点或修改趋势条件。 |
| --inline | CLI flag | 否 | 全量打印响应，同时仍保存完整数据。 |
| --no-cache | CLI flag | 否 | 禁用本次缓存读取和写入；不自动追加此选项，默认使用 24 小时缓存。 |
| LINKFOX_TOOL_GATEWAY | string | 否 | 网关基础地址，优先使用此变量，否则使用公共规则的默认地址；去掉末尾 `/`。 |
| LINKFOX_AGENT_API_KEY / LINKFOXAGENT_API_KEY | string | 否 | 认证密钥，按列出顺序读取，取首个非空值；都未配置时按认证引导处理。 |
| SESSION_ID | string | 否 | 配置后用于请求头中的会话标识及本地会话目录名；未配置时请求头传空字符串，本地目录使用进程内稳定的自动生成标识。 |
| MESSAGE_ID / MODE_ID / APP_NAME | string | 否 | 原样携带到同名请求头，未配置时传空字符串。 |

缓存键为排序后的 JSON 参数 SHA-256 前 16 位，缓存路径为 `<cwd>/linkfox/.cache/linkfox-sorftime-amazon-product-detail/linkfox-sorftime-amazon-product-detail-<key>.json`。有效缓存文件可复用，过期或损坏时重新查询；命中时附加 `_cache.hit=true`。业务脚本只使用公共调用器的一层缓存，不额外实现缓存或自动重试。完整响应、摘要、会话元数据和索引均由公共调用器处理；业务入口固定在当前工作目录落盘，不回退到家目录或临时目录，当前目录不可写时在请求前报错。

### 响应结构

#### 顶层字段

| 字段 | 类型 | 说明 |
|------|------|------|
| code | integer | 响应码（200表示成功） |
| msg | string | 响应消息 |
| errcode | integer | 网关错误码；例如认证错误返回 `401`，按公共响应码规则判断。 |
| errmsg | string | 网关错误消息；例如 `authorized error`。 |
| total | integer | 结果总数 |
| costTime | integer | 耗时（ms） |
| costToken | integer | 消耗Token数量 |
| requestConsumed | integer | 消耗的请求数 |
| sourceType | string | 来源类型：sorftime |
| type | string | 渲染的样式 |
| columns | array | 渲染的列 |
| products | array | 产品详情列表（详见下方） |

#### 商品对象字段（products 数组元素）

趋势数组均采用交错格式：偶数下标为日期（yyyyMMdd），奇数下标为对应值。

| 字段 | 类型 | 说明 |
|------|------|------|
| asin | string | ASIN |
| title | string | 商品标题 |
| brand | string | 品牌 |
| asinUrl | string | 商品链接，亚马逊Listing详情页URL |
| imageUrl | string | 主图URL |
| productImageUrls | array | 主图列表（所有商品图片URL） |
| ebcPhoto | array | A+图片列表 |
| storeName | string | 店铺名称 |
| description | string | 五点描述 |
| productBadge | array | 产品标志，如Amazon Choice、Best Seller、New Release等 |
| lastUpdate | string | 更新时间，ASIN数据最近采集时间（格式yyyy-MM-dd） |
| offSale | boolean | 是否下架。true=不可售，false=可售 |
| productType | string | 分类，亚马逊产品类目节点名称 |
| weight | string | 重量，单位g |
| size | array | 尺寸，外包装[最长边,第二长边,最短边]，单位cm |
| parentAsin | string | 父ASIN，有子体时为父级ASIN，无子体时为null |
| variationNum | integer | 变体数 |
| variationASIN | array | 子体ASIN列表，无子体时为空 |
| attribute | array | 产品属性，有子体时表示子体属性；元素字段见下方嵌套字段表。 |
| price | number | 销售价，扣除Coupon后的实际售价，单位为当地货币(如美元) |
| coupon | integer | Coupon政策。值>=0为抵扣金额(如500=$5)，值<0为折扣百分比(如-10=10%折扣) |
| platformFee | number | 平台佣金，单位为当地货币(如美元) |
| fbaFees | number | FBA费用，单位为当地货币(如美元) |
| fbaDetail | array | FBA明细。首项为配送费，后续为月份:仓储费，如[475,"1-9:5","10-12:15"] |
| shipCost | number | FBM配送费，单位为当地货币(如美元) |
| shipsFrom | string | 发货方 |
| profitAmount | number | 利润，到手价-FBA费-佣金，单位为当地货币(如美元) |
| profitRate | number | 利润率，例25.83表示25.83% |
| monthlySalesUnits | integer | 官方月销量，亚马逊公布的ASIN月销量，取近7个自然日最新值，无则为0 |
| salesRank | integer | BSR排名，大类排名 |
| category | array | 大类，[大类名称, NodeId] |
| bsrCategory | array | 小类排名列表；元素字段见下方嵌套字段表。 |
| availableDate | string | 上架时间，格式yyyy-MM-dd |
| onlineDays | integer | 上架天数 |
| rating | number | 当前评分（0.0-5.0，如4.70） |
| ratings | integer | 评分数量 |
| fiveStarRatings | number | 5星占比，例57.7表示57.7% |
| fourStarRatings | number | 4星占比 |
| threeStarRatings | number | 3星占比 |
| twoStarRatings | number | 2星占比 |
| oneStarRatings | number | 1星占比 |
| buyboxSeller | string | Buybox卖家名称 |
| buyBoxSellerId | string | Buybox卖家ID |
| buyboxSellerAddress | string | 卖家所在地，Buybox卖家国籍(二字码如CN、US)，亚马逊自营时为null |
| isFBA | boolean | 是否FBA，Buybox卖家是否使用FBA物流 |
| sellerNum | integer | 卖家数 |
| aPlus | boolean | 有A+ |
| hasVideo | boolean | 有视频 |
| hasBrandStore | boolean | 有品牌店 |
| feature | object | 产品特性星级，亚马逊为此产品统计的特性及每个特性的星级，如{"Battery life":4.0} |
| productInfo | object | 产品信息，Listing中部Product Information结构化数据 |
| property | object | 属性列表，含变体属性及Bullet Points上方说明 |
| brandPromotion | string | 品牌促销 |
| dealType | string | Deal标签 |
| extraSavings | array | 关联促销；元素字段见下方嵌套字段表。 |
| rankTrend | array | BSR趋势，大类排名变化历史，交错格式[日期,排名,...] |
| bsrRankTrend | array | 小类排名趋势；各小类的节点与排名数组见下方嵌套字段表。 |
| listingSalesVolumeOfDailyTrend | array | 日销量趋势，值为-1表示无法预估 |
| listingSalesOfDailyTrend | array | 日销售额趋势，单位为当地货币最小单位(如美分)，值为-1表示无法预估 |
| listingSalesVolumeOfMonthTrend | array | 月销量趋势(近30日)，值为-1表示无法预估 |
| listingSalesOfMonthTrend | array | 月销售额趋势，单位为当地货币最小单位(如美分) |
| priceTrend | array | 售价趋势，未扣Coupon，单位为当地货币最小单位，-1表示该日无可用价格 |
| listPriceTrend | array | 原价趋势（划线价历史），单位为当地货币最小单位，-1表示该日无可用价格 |
| dealTrend | array | Deal趋势，值1=有Deal，0=无Deal |

#### 嵌套字段补充

下表列出嵌套字段；标为“以实际返回为准”的字段不预设单项类型。

| 字段 | 类型 | 说明 |
|------|------|------|
| attribute[].asin | 以实际返回为准 | 子体 ASIN。 |
| attribute[].name | 以实际返回为准 | 属性名。 |
| attribute[].value | 以实际返回为准 | 属性值。 |
| bsrCategory[].nodeId | 以实际返回为准 | 类目节点 ID，保持小写 `nodeId`。 |
| bsrCategory[].name | 以实际返回为准 | 类目名称。 |
| bsrCategory[].rank | 以实际返回为准 | 该类目排名。 |
| bsrCategory[].date | 以实际返回为准 | 日期，格式 `yyyyMMdd`。 |
| bsrRankTrend[].NodeId | 以实际返回为准 | 小类节点 ID，保持大写 `NodeId`。 |
| bsrRankTrend[].Rank | array | 小类排名的交错日期和值数组。 |
| extraSavings[].Asin | 以实际返回为准 | 关联促销商品 ASIN，保持大写 `Asin`。 |
| extraSavings[].Text | 以实际返回为准 | 促销文案，如 `Save 5%...`，保持大写 `Text`。 |

#### 脚本输出补充

| 字段 | 类型 | 说明 |
|------|------|------|
| _cache.hit | boolean | 仅本地缓存命中时由脚本加入，为 `true`；不属于服务端商品字段。 |

#### 趋势数组与单位

| 项目 | 约定 |
|------|------|
| 交错数组 | 从下标 0 开始：偶数下标为 `yyyyMMdd` 日期，奇数下标为对应值，如 `[20250101,150,20250102,180]`。 |
| 销量、销售额 | `-1` 表示无法预估；月销量趋势为近 30 日口径，不等同于官方月销量 `monthlySalesUnits`。 |
| 金额单位 | 销售额与价格趋势使用当地货币最小单位，如美元美分；当前价格、佣金、FBA/FBM 费用、利润金额使用当地货币标准单位。 |
| 缺失价格 | `priceTrend`、`listPriceTrend` 中 `-1` 表示该日无可用价格。 |
| Coupon | 非负数为最小货币单位的抵扣金额，如 `500=$5`；负数为折扣百分比，如 `-10=10%`。 |
| Deal | 趋势值 `1` 表示当天有 Deal，`0` 表示无 Deal。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 正常业务响应通常使用 HTTP `200`。公共规则判断正常后，商品业务字段 `code=200` 表示成功；其他 `code` 值表示业务异常，结合 `msg` 说明原因，不将 HTTP 正常直接当作商品查询成功。
- 销量或销售额的 `-1` 属于无法预估的数据标记，不代表零销量，也不直接代表整个请求失败。

### 响应示例

认证错误示例（HTTP 401）：

```json
{"errcode": 401, "errmsg": "authorized error"}
```

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/sorftime/amazon/productDetail" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"asin":"B00FLYWNYQ","marketplace":"us","includeTrend":1,"queryTrendStartDate":"2025-01-01","queryTrendEndDate":"2025-03-01"}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-sorftime-amazon-product-detail",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```