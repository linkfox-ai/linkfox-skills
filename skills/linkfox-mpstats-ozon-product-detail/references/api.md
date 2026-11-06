# MPSTATS Ozon 商品详情（单个 SKU）接口说明

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

## 接口：商品详情（单个 SKU）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/mpstats/ozon/productDetail`

### 请求参数

POST Body（JSON）。以下字段与工具网关登记的「MPSTATS-Ozon-商品详情」入参 schema 一致（同步日期 2026-09-01）。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| productId | integer\|string | 是 | 单个 Ozon 商品 ID（SKU）；不接受数组、列表或对象；已废弃 `productIds`。脚本拒绝布尔值、null、缺失及空白字符串，对字符串去除首尾空白。 |
| startDate | string | 否 | 统计起始日，格式 `YYYY-MM-DD`；最晚可选昨日（T-1），不得为今天或未来日期。未提供时的统计区间以服务端实际返回为准。 |
| endDate | string | 否 | 统计结束日，格式 `YYYY-MM-DD`；最晚可选昨日（T-1），不得为今天或未来日期。起止日期决定所有统计期聚合指标的区间。 |
| includeFbs | boolean | 否 | `true` 允许 FBS 商品及其指标进入响应；`false` 或省略时以 FBO 为主。开关作用于整次请求。 |

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| JSON 参数 | object | 是 | `python scripts/mpstats_ozon_product_detail.py '<JSON 参数>' [--inline] [--no-cache]`；字段与上表一致。脚本只校验并规范化商品编号，日期及 `includeFbs` 由服务端校验，不补入未声明的默认值。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 禁用业务封装的 24 小时响应缓存，不读取也不写入缓存；公共调用器每次均使用此选项，不叠加第二层缓存。 |
| --help / -h | CLI flag | 否 | 仅显示本地帮助，不请求接口。 |
| LINKFOX_TOOL_GATEWAY | 环境变量 | 否 | 网关地址优先使用此变量，省略时使用公共规则的默认地址。 |
| LINKFOX_AGENT_API_KEY / LINKFOXAGENT_API_KEY | 环境变量 | 是（任一） | 主变量优先；兼容旧变量；原样作为 Authorization 值，不添加 Bearer 前缀。 |
| SESSION_ID | 环境变量 | 否 | 会话归档标识；未设置时按时间和随机后缀生成，同一进程内稳定。 |
| MESSAGE_ID / MODE_ID / APP_NAME | 环境变量 | 否 | 原样透传至同名请求头，未设置时为空字符串；SESSION_ID 也透传至同名请求头。 |

- 业务缓存保存在 `<cwd>/linkfox/.cache/linkfox-mpstats-ozon-product-detail/`，键为规范化请求 JSON（保留 Unicode、按字段名排序）的 SHA-256 前 16 位，文件名为 `<skill>-<hash>.json`；TTL 根据文件修改时间判断，超过 24 小时失效，不可读、无效 UTF-8 或无效 JSON 的缓存忽略。缓存包括失败及空响应；命中时增加 `_cache.hit=true`，本地 `_cache` 标记不是对象时先将其规范化为对象，继续复用业务数据，不因此重复请求。
- 每次运行仍保存完整响应，按 `SESSION_ID` 聚合并维护 `_meta.json` 和 `index.jsonl`；业务封装固定使用当前工作目录的 `linkfox/`，不受 `ACPX_WORKSPACES` 影响，不回退家目录或临时目录。当前目录不可写时在请求前报错。
- 每次只查一个 SKU；多个 SKU 须逐个请求，并先向用户确认额外算力消耗。比较 FBO 与包含 FBS 的口径也属于不同参数组合，遵守成本约束。
- 部分类目的 FBS 数据覆盖不完整，FBS 商品可能返回较少字段或更稀疏的卡片；本接口仅支持 Ozon，不覆盖 Wildberries。
- 本详情接口字段集与品牌、类目、卖家商品接口不同：包含 `previousSalesUnits`、`previousRevenue`、`revenuePotential`、`deliveryScheme`、`productImageUrls` 等深度字段，但不返回 `brandId`、`country`、`category`、`minPrice`、`maxPrice`、`averagePrice`、`balanceFbs`、`frozenStocks`、`warehousesCount`、`daysInSite`、`daysInStock`、`turnoverDays`、`position`、`categoryPosition`、`revenueSharePercent`、`isFbs`；需要这些字段时使用对应维度的商品技能，不补造缺失值。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| code | string | 返回码（字符串），`"200"` 表示成功 |
| errcode | integer | 返回码（整数），`200` 表示成功 |
| msg | string | 消息；成功为 `ok` |
| errmsg | string | 消息；成功为 `ok` |
| total | integer | 返回的 SKU 数（通常为 0 或 1，= `successCount` + `failedCount`） |
| successCount | integer | 成功返回卡片的 SKU 数（通常为 0 或 1） |
| failedCount | integer | 失败的 SKU 数（通常为 0 或 1） |
| failures | array | 失败 SKU 明细列表（通常最多 1 项，每项含失败的 `productId` 与错误信息） |
| products | array | 商品卡列表（详见下方） |
| columns | array | 渲染列定义 |
| costTime | integer | 接口耗时（毫秒） |
| costToken | integer | 消耗 Token 数量 |
| type | string | 响应类型 |

#### products[*] 商品详情字段

以下字段按官方 outputSchema（`_mpstats_ozon_productDetail`，同步日期 2026-05-06）定义。

**身份与基础信息**

| 字段 | 类型 | 说明 |
|------|------|------|
| productId | integer | SKU ID |
| title | string | 商品名称（俄语） |
| brand | string | 品牌 |
| sellerName | string | 卖家名 |
| sellerId | integer | 卖家 ID |
| sellerIsBestSeller | boolean | 卖家是否为畅销卖家 |
| nicheName | string | 赛道路径（俄语，`/` 分隔） |
| nicheId | integer | 赛道 ID |
| firstDate | string | 上架日期（`yyyy-MM-dd`） |
| updated | string | 数据更新时间（`yyyy-MM-dd HH:mm:ss`） |
| note | string | 备注 |
| sourceTool | string | 来源工具标识 |
| sourceType | string | 数据源标识 |

**图片**

| 字段 | 类型 | 说明 |
|------|------|------|
| imageUrl | string | 主图 URL（首张大图） |
| imageCount | integer | 图片总数 |
| productImageUrls | array<string> | 除主图外的其余大图 URL |
| productPageUrl | string | 商品页 URL |

**价格与折扣**

| 字段 | 类型 | 说明 |
|------|------|------|
| price | number | 当前售价 |
| oldPrice | number | 折扣前原价 |
| ozonCardPrice | number | Ozon Card 价（银行卡优惠价） |
| discount | integer | 折扣，百分比整数 0-100 |
| currency | string | 币种符号（`₽` / `$` / `€`） |

**评分**

| 字段 | 类型 | 说明 |
|------|------|------|
| rating | number | 评分，0-5 |
| reviewCount | integer | 评论数 |

**库存与配送**

| 字段 | 类型 | 说明 |
|------|------|------|
| balance | integer | 当前库存（件） |
| deliveryScheme | string | 配送方案；`FBO`=Ozon 仓配，`FBS`=卖家自配 |

**销售与收入（当期 + 上期对比）**

| 字段 | 类型 | 说明 |
|------|------|------|
| salesPerDay | number | 日均销量（件/日） |
| salesPerDayWithStock | number | 有货日均销量（仅计有库存日） |
| dailySalesRevenue | number | 日均销售额 |
| dailySalesRevenueWithStock | number | 有货日均销售额 |
| monthlySalesUnits | integer | 统计期销量（件） |
| monthlySalesRevenue | number | 统计期销售额 |
| previousSalesUnits | integer | 上期销量（与本统计周期等长的前一段时间） |
| previousRevenue | number | 上期销售额 |
| revenuePotential | number | 潜在销售额（按全期有库存估算） |
| lostProfit | number | 损失销售额（缺货等造成） |
| lostProfitPercent | number | 损失销售额占比（%） |

#### 嵌套结构补充

| 字段 | 类型 | 说明 |
|------|------|------|
| failures[*].productId | 以实际返回为准 | 失败商品编号；每项还包含错误信息，其键名及类型以实际返回为准，完整保留返回内容。 |
| columns[*] | 以实际返回为准 | 渲染列定义元素；按实际返回读取，不假定固定子字段结构。 |
| _cache.hit | boolean | 仅脚本命中业务缓存时追加的本地标记，非服务端业务字段。 |
| _http_status | integer | 业务脚本记录的实际 HTTP 响应状态，非网关业务字段；连接失败、未收到 HTTP 响应时不补造状态。缓存命中时是该缓存生成时的历史状态，不代表本次发起了请求。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 脚本结果以本地 `_http_status` 配合响应体 `errcode` 执行基础规则；HTTP `401` / `402` 即使响应体没有错误码也按认证或用量错误处理，HTTP `403` 不归入这两类。旧缓存可能没有 `_http_status`，不得仅凭缺失 `errcode` 断言 HTTP 正常；保留状态未知的说明，不为补齐状态自动重发收费请求。
- 响应体 `errcode` 为 `401` / `402`，或消息含 `authorized error`、鉴权失败、算力或余额不足等含义时，按 `onboarding.md` 的指引处理；不将 `403` 归入认证或余额引导。
- 参数异常按 `errmsg` / `msg` 解释，常见原因包括缺失或非法 `productId`、日期越过昨日；不得把基础规则允许的其他正常状态笼统归为异常。
- 正常响应仍需查看 `successCount`、`failedCount` 和 `failures`；失败商品编号及错误信息须展示。商品列表为空不代表取得了有效商品卡，不自动重试或更换条件。
- 服务端动态计费规则为消耗算力 12，`productId` 为空时消耗 0 算力 （限时）；脚本不发送空编号请求。

### curl 示例

```bash
curl -X POST https://tool-gateway.linkfox.com/mpstats/ozon/productDetail \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
    "productId": 1786874757,
    "startDate": "2025-03-01",
    "endDate": "2025-03-31",
    "includeFbs": true
  }'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-mpstats-ozon-product-detail",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
