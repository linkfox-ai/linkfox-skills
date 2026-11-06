# MPSTATS Ozon 品牌商品查询 接口说明

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

## 接口：品牌商品查询

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/mpstats/ozon/brandProducts`

### 请求参数

POST Body（JSON）。以下字段与工具网关当前登记的「MPSTATS-Ozon-品牌商品」入参 schema 一致（同步日期 2026-04-30）。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| brandName | string | 是 | Ozon 前台品牌展示名，通常为俄语（西里尔字母）或拉丁字母，如 `adidas`、`Xiaomi`；必须精确匹配，不支持模糊匹配，不得传类目路径、卖家 ID 或内部品牌代码。拼写错误可能返回空结果，名称不确定时先通过 MPSTATS Ozon 商品搜索核对。 |
| startDate | string | 否 | 统计起始日，`YYYY-MM-DD`；最晚昨日 |
| endDate | string | 否 | 统计结束日，`YYYY-MM-DD`；最晚昨日（T-1），不能为今天或未来日期 |
| page | integer | 否 | 页码，从 1 开始 |
| pageSize | integer | 否 | 每页行数，1-100，默认 100 |
| sortField | string | 否 | 排序列名（snake_case），如 `sales`、`revenue`、`final_price`、`balance`、`rating` |
| sortDirection | string | 否 | `asc` 升序 / `desc` 降序 |
| currency | string | 否 | 结果金额货币代码，默认 `RUB`，如 `USD` / `EUR` / `CNY`；非默认货币由服务端换算，历史换算值可能与用户参考汇率略有差异。 |
| currencyRate | integer | 否 | 自定义汇率，配合非默认货币覆盖默认汇率。 |
| includeFbs | boolean | 否 | `true` 将 FBS 库存和销售合并计入指标；`false` 仅保留 FBO 数据。省略时以实际返回为准，需要明确配送口径时显式传入 `true` 或 `false`。 |
| filters | array | 否 | 数值筛选条件列表，每项 `{field, op, value, value2?}`，多条件 AND |

#### filters 子字段

| 子字段 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| field | string | 是 | 列名（snake_case），常用见下 |
| op | string | 是 | `GTE` / `LTE` / `GT` / `LT` / `EQ` / `NOT_EQ` / `BETWEEN` |
| value | number | 是 | 主值（`BETWEEN` 时为下界） |
| value2 | number | `BETWEEN` 必填 | 上界（闭区间） |

#### 常用筛选字段

| field | 说明 |
|-------|------|
| sales | 月销。 |
| final_price | 售价，RUB。 |
| rating | 评分，0–5。 |
| comments | 评论数。 |
| balance | 库存。 |
| revenue | 销售额，RUB。 |
| days_in_stock | 有货天数。 |
| turnover_days | 周转天数。 |
| lost_profit | 损失销售额，RUB。 |
| category_position | 类目排名。 |

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|-------------|------|------|------|
| JSON 参数 | JSON object | 是 | 第一个位置参数为接口请求体，不改写品牌、筛选和排序。 |
| --inline | CLI flag | 否 | 强制全量输出，完整响应仍落盘。 |
| --no-cache | CLI flag | 否 | 禁用响应缓存读取和写入。默认复用 24 小时缓存。 |
| --help / -h | CLI flag | 否 | 显示本地帮助，不发出请求。 |

- 业务封装调用公共 `call_api.run`，使用一层缓存；缓存目录为 `<cwd>/linkfox/.cache/linkfox-mpstats-ozon-brand-products/`，参数以排序后的 JSON 计算 SHA-256 前 16 位，文件有效期 24 小时。命中时在响应标记 `_cache.hit=true`，不发起接口请求。
- 支持 `LINKFOX_TOOL_GATEWAY` 网关覆盖、两种 API Key 环境变量及 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 请求头透传。
- 完整响应写入当前工作目录的会话数据路径，使用 UTF-8。封装在请求前检查目标数据目录可写，并固定公共调用器的输出根目录；不可写时报错，不回退到 `ACPX_WORKSPACES`、家目录或临时目录。
- 数据文件名使用微秒时间戳，避免同一秒内的多次查询相互覆盖；路径与会话元数据仍由公共调用器生成和登记。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| code | string | 返回码，`"200"` 成功 |
| msg | string | 消息；成功为 `ok` |
| total | integer | 品牌下命中商品总数 |
| products | array | 商品列表（详见下方） |
| columns | array | 渲染列定义 |
| costTime | integer | 接口耗时（毫秒） |
| costToken | integer | 消耗 Token 数量 |
| type | string | 响应类型 |

#### products[*] 商品对象字段（39 个）

按官方 outputSchema 定义（`_mpstats_ozon_brandProducts`，同步日期 2026-05-06）。该 schema 与 `productSearch` / `categoryProducts` / `sellerProducts` **完全共用**；4 个端点只是查询维度不同，返回的商品卡字段集完全一致。

**身份与基础信息**

| 字段 | 类型 | 说明 |
|------|------|------|
| productId | integer | SKU ID |
| title | string | 商品名称（俄语） |
| brand | string | 品牌 |
| brandId | integer | 品牌 ID |
| sellerName | string | 卖家名 |
| sellerId | integer | 卖家 ID |
| category | string | 品类路径（俄语，`/` 分隔） |
| nicheName | string | 赛道路径（俄语） |
| nicheId | integer | 赛道 ID |
| country | string | 销售国，Ozon 恒为 `RU` |
| firstDate | string | 上架日期（`yyyy-MM-dd`） |
| imageUrl | string | 主图 URL |
| productPageUrl | string | 商品页 URL |
| sourceTool | string | 来源工具标识 |
| sourceType | string | 数据源标识 |

**价格与货币**

| 字段 | 类型 | 说明 |
|------|------|------|
| price | number | 当前售价 |
| oldPrice | number | 折扣前原价 |
| ozonCardPrice | number | Ozon Card 价 |
| minPrice | number | 统计期内最低价 |
| maxPrice | number | 统计期内最高价 |
| averagePrice | number | 统计期内均价 |
| currency | string | 币种符号（`₽` / `$` / `€`） |

**评分与评论**

| 字段 | 类型 | 说明 |
|------|------|------|
| rating | number | 评分，0-5 |
| reviewCount | integer | 评论数 |

**库存与 FBS**

| 字段 | 类型 | 说明 |
|------|------|------|
| balance | integer | 当前库存（件） |
| balanceFbs | integer | FBS 库存（卖家自发货件数） |
| frozenStocks | integer | 滞销库存 |
| warehousesCount | integer | FBO 分仓数 |
| isFbs | boolean | 是否 FBS 发货 |

**销售与周转**

| 字段 | 类型 | 说明 |
|------|------|------|
| salesPerDay | number | 日均销量（件/日） |
| monthlySalesUnits | integer | 统计期销量（件） |
| monthlySalesRevenue | number | 统计期销售额 |
| lostProfit | number | 损失销售额（缺货等造成） |
| daysInSite | integer | 在售天数（统计期，含缺货日） |
| daysInStock | integer | 有货天数 |
| turnoverDays | number | 周转天数（越小越快） |

**排名与占比**

| 字段 | 类型 | 说明 |
|------|------|------|
| position | integer | 当前查询维度（本端点为品牌）内排名 |
| categoryPosition | integer | 品类内排名 |
| revenueSharePercent | number | 该 SKU 在当前查询维度（本接口为品牌结果集）的销售额占比，0-100 |

`columns` 为渲染列定义数组，元素子字段以实际返回为准，不补造嵌套结构。

#### 本地附加字段

| 字段 | 类型 | 说明 |
|------|------|------|
| _cache | object | 仅本地命中缓存时由脚本附加，不属于接口业务字段。 |
| _cache.hit | boolean | 缓存命中时为 true。 |
| _http_status | integer | 业务脚本附加的实际 HTTP 状态，不属于网关业务字段；保留 JSON 错误体中的原始业务码和消息。连接失败时无此字段。 |

缓存中的 `_http_status` 是首次请求的历史状态，命中缓存不代表重新发出了请求。旧缓存可能没有此字段，缺失时不得推断 HTTP 成功。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- `code`、`msg` 是本接口的业务字段，成功定义为 `code="200"`、`msg="ok"`；不得用它们替换公共规则对 HTTP 和 `errcode` 的判断。
- 使用业务脚本时，按 `_http_status` 判断实际 HTTP 状态；即使响应体写着成功，HTTP `401` / `402` 仍进入认证或算力引导，其他非 `2xx` 状态仍按未正常响应处理。缓存命中时该状态仅用于解释已保存的响应，不自动重试。
- 其他业务异常保留 `errmsg` 或 `msg` 原文；常见线索为品牌拼写错误、日期越过昨日等，先核对参数，不擅自补造响应码。
- 正常响应但 `total=0` 或 `products=[]` 时说明本次未命中数据，核对品牌及筛选条件；不得自动更换品牌、改日期或翻页连续试探。

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/mpstats/ozon/brandProducts" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"brandName":"adidas","sortField":"sales","sortDirection":"desc","pageSize":50,"filters":[{"field":"rating","op":"GTE","value":4.5}]}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-mpstats-ozon-brand-products",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```