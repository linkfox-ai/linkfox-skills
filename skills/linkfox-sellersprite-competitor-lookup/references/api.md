# 卖家精灵竞品查询 接口说明

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

## 接口：竞品查询

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/sellersprite/competitor-lookup`

### 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| marketplace | string | 否 | 亚马逊站点代码，默认 `US`。可选值：US、UK、DE、FR、JP、CA、IT、ES、MX、AU、TR、IN |
| keyword | string | 否 | 搜索关键词。请尽量翻译为对应国家的语言，比如美国用英语关键词，德国用德语关键词等 |
| asinList | string | 否 | ASIN，多个ASIN使用英文逗号分隔，最多40个。格式：`^[A-Z0-9]+(,[A-Z0-9]+){0,39}$` |
| sellerName | string | 否 | 卖家名称筛选 |
| brand | string | 否 | 品牌名称筛选 |
| nodeLabel | string | 否 | 亚马逊类目名称，支持多层级类目名称，层级之间用英文冒号 `:` 分割，例如 `Electronics:Headphones` |
| nodeIdPath | string | 否 | 亚马逊类目ID路径 |
| matchType | integer | 否 | 匹配方式。1 = 词组匹配（默认），2 = 模糊匹配，3 = 精准匹配 |
| showVariation | string | 否 | 是否查询变体。`Y` = 是，`N` = 否（默认） |
| dataSnapshotMonth | string | 否 | 亚马逊商品数据快照年月。默认 `nearly`（查询最近30天实时数据）。使用 `yyyyMM` 格式查询历史快照（如 `202412` 表示2024年12月）。仅支持已存在的历史快照，不支持未来日期。建议季节性分析时查询去年同期快照进行对比 |
| page | integer | 否 | 页码，从1开始（默认1）；分页最多只能查询排序结果中的前 2000 条记录 |
| size | integer | 否 | 每页条数，返回10-100条数据（默认50）；`page * size` 不得超过 2000 |
| order | object | 否 | 排序配置（见下方说明） |

> **分页上限**：无论 `total` 显示多少条匹配结果，接口最多只能查询当前排序结果中的前 2000 条记录。若需查看第 2000 条之后的数据，请增加或收紧筛选条件后重新查询。

不要假定接口支持未定义的评分、价格或配送方式筛选入参；可在取得商品后按实际返回指标分析。

#### 排序对象（order）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| field | string | 是 | 排序字段。可选值：`total_units`（月销量）、`total_amount`（月销售额）、`bsr_rank`（BSR排名）、`price`（价格）、`rating`（评分）、`reviews`（评分数）、`profit`（毛利率）、`reviews_rate`（留评率）、`available_date`（上架时间）、`questions`（Q&A数）、`total_units_growth`（月销量增长率）、`total_amount_growth`（月销售额增长率）、`reviews_increasement`（月新增评分数）、`bsr_rank_cv`（近7天BSR增长数）、`bsr_rank_cr`（近7天BSR增长率）、`amz_unit`（子体销量）。默认：`total_units` |
| desc | string | 是 | 排序方向。`true` = 降序，`false` = 升序。默认：`true` |

#### 脚本选项与运行约定

| 参数 / 约定 | 类型 | 必填 | 说明 |
|------|------|------|------|
| JSON 参数 | object | 是 | 命令行首个位置参数为 JSON 对象，字段见上述请求参数；脚本透传，不擅自添加筛选条件 |
| --inline | CLI flag | 否 | 强制完整打印到标准输出，同时保存完整响应 |
| --no-cache | CLI flag | 否 | 绕过默认缓存的读取和写入 |
| 默认响应缓存 | 本地文件 | 否 | 有效期 24 小时；目录为 `<cwd>/linkfox/.cache/linkfox-sellersprite-competitor-lookup/`；文件名为 `linkfox-sellersprite-competitor-lookup-<hash>.json`；hash 为 `json.dumps(params, ensure_ascii=False, sort_keys=True)` 的 UTF-8 字节经 SHA-256 后取前 16 位十六进制字符 |
| 缓存命中标记 | object | 否 | 命中后在响应中添加 `_cache.hit=true`，仍保存完整响应并展示缓存命中提示；不再发起请求 |
| 会话数据目录 | 本地目录 | 是 | 业务入口固定使用当前工作目录的 `linkfox/`，不会因 `ACPX_WORKSPACES` 或公共调用器的回退目录改变输出位置。当前目录不可写，或在非 Windows 系统的 `/tmp` 下运行时，在请求前报错；目录检查不另建响应缓存 |
| LINKFOX_TOOL_GATEWAY | 环境变量 | 否 | 优先使用该网关地址，去掉末尾 `/`；默认值见公共规则 |
| LINKFOX_AGENT_API_KEY / LINKFOXAGENT_API_KEY | 环境变量 | 调用时是 | 前者优先，兼容后者；缺失时退出并引导认证 |
| SESSION_ID / MESSAGE_ID / MODE_ID / APP_NAME | 环境变量 | 否 | 按同名请求头透传，未配置时为空字符串 |
| Accept | 请求头 | 否 | 业务封装设置 `Accept: application/json` 请求头，请求由公共调用器发送 |

公共调用器统一处理请求、缓存和输出，业务脚本不额外维护第二层缓存。HTTP 错误 JSON 或连接错误均保留供解释，不自动重试。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 业务状态码，按公共响应码基本规则判断；认证失败示例值为 401 |
| errmsg | string | 网关消息或错误原因 |
| errorCode | 以实际响应为准 | 业务状态字段：200 表示成功、其他值表示业务错误，未授权值为 401。字段名以实际响应为准，不假定它与 `errcode` 同时存在或等价；HTTP 状态与 `errcode` 的判断统一遵循公共规则，不以此字段替换公共规则 |
| total | integer | 匹配结果总数 |
| sourceType | string | 来源类型（如 `amazon`） |
| message | string | 执行消息或错误描述 |
| type | string | 渲染样式 |
| nodeLabel | string | 类目名称回显 |
| columns | array | 渲染的列定义 |
| products | array | 竞品列表（见下方说明） |
| costToken | integer | 消耗token |

#### 竞品对象字段（products[*]）

| 字段 | 类型 | 说明 |
|------|------|------|
| asin | string | 商品ASIN |
| title | string | 商品标题 |
| price | number | 当前价格 |
| primePrice | number | Prime价格 |
| averagePrice | number | 平均价格 |
| currency | string | 币种 |
| monthlySalesUnits | integer | 月销量（件数） |
| monthlySalesRevenue | number | 月销售额 |
| monthlySalesUnitsGrowthRate | number | 月销量增长率 |
| bsr | integer | BSR排名 |
| bsrGrowthRate | number | BSR增长率 |
| bsrGrowthCount | integer | BSR增长数 |
| rating | number | 评分 |
| ratings | integer | 评分数 |
| ratingsGrowth | integer | 月新增评分数 |
| ratingsRate | number | 留评率 |
| brand | string | 品牌 |
| brandUrl | string | 品牌URL |
| sellerName | string | BuyBox卖家名称 |
| sellerId | string | BuyBox卖家ID |
| sellerNation | string | BuyBox卖家国籍 |
| sellerNum | integer | 卖家数 |
| fulfillment | string | 配送方式：AMZ、FBA、FBM |
| availableDate | string | 上架时间（日期格式） |
| availableDateString | string | 上架日期（字符串格式） |
| profit | number | 毛利率 |
| fba | number | FBA运费 |
| deliveryPrice | number | 卖家运费 |
| imageUrl | string | 商品图片URL |
| parent | string | 父体ASIN |
| variationNum | integer | 变体数 |
| variant30DayUnits | integer | 子体月销量（件数） |
| variant30DayRevenue | number | 子体月销售额 |
| variant30DayUpdatedAt | string | 子体数据更新时间（时间戳） |
| amzUnitDateString | string | 子体销量更新日期 |
| listingQualityScore | number | Listing质量得分 |
| nodeLabelPath | string | 类目路径 |
| nodeIdPath | string | 节点ID路径 |
| nodeId | integer | 节点ID |
| dimension | string | 商品尺寸 |
| dimensionsType | string | 尺寸类型 |
| weight | string | 商品重量 |
| packageDimensions | string | 包装尺寸 |
| packageDimensionType | string | 包装尺寸类型 |
| packageWeight | string | 包装重量 |
| sku | string | SKU |
| keyword | string | 匹配的关键词（如通过关键词搜索，则显示对应关键词） |
| dataSnapshotMonth | string | 数据查询月份 |
| sourceTool | string | 来源工具 |
| sourceType | string | 来源类型 |
| badgeBestSeller | string | Best Seller标识（Y/N） |
| badgeAmazonChoice | string | Amazon's Choice标识（Y/N） |
| badgeNewRelease | string | New Release标识（Y/N） |
| badgeEbc | string | A+页面（Y/N） |
| badgeVideo | string | 视频介绍（Y/N） |
| badge | object | 标识详情对象，包含：`bestSeller`、`amazonChoice`、`newRelease`、`ebc`、`video`（均为 Y/N 字符串） |
| subcategories | array | 子类目排名，每项包含 `code`（类目code）、`rank`（排名）、`label`（名称） |

#### 标识详情（products[*].badge）

| 字段 | 类型 | 说明 |
|------|------|------|
| bestSeller | string | Best Seller 标识，Y/N |
| amazonChoice | string | Amazon's Choice 标识，Y/N |
| newRelease | string | New Release 标识，Y/N |
| ebc | string | A+ 页面标识，Y/N |
| video | string | 视频介绍标识，Y/N |

#### 子类目排名（products[*].subcategories[*]）

| 字段 | 类型 | 说明 |
|------|------|------|
| code | 以实际响应为准 | 类目 code，保留实际响应值 |
| rank | 以实际响应为准 | 类目排名，保留实际响应值 |
| label | 以实际响应为准 | 类目名称，保留实际响应值 |

`columns` 的元素结构以实际响应为准，不假定额外字段。

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 竞品结果从 `products` 读取，`total` 是匹配结果总数，可能超过可访问的分页范围。不要将商品结果解释为流量关键词列表。
- 查询失败时，除公共规则中的 `errmsg` 外，结合接口的 `message` 说明业务原因；连接错误或非 JSON HTTP 错误会由脚本保留在 `error`、`details` 等错误信息中，不将其视为商品数据。

### curl 示例

```bash
curl -X POST https://tool-gateway.linkfox.com/sellersprite/competitor-lookup \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"marketplace": "US", "keyword": "wireless earbuds", "matchType": 1, "order": {"field": "total_units", "desc": "true"}, "page": 1, "size": 20}'
```

### 响应示例

认证失败示例：

```json
{"errcode": 401, "errmsg": "authorized error"}
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-sellersprite-competitor-lookup",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```