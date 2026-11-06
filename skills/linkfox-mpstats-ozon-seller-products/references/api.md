# MPSTATS Ozon 卖家商品 接口说明

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

## 接口：卖家商品查询

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/mpstats/ozon/sellerProducts`

### 请求参数

POST Body（JSON）。以下字段与工具网关当前登记的「MPSTATS-Ozon-卖家商品」入参 schema 一致（同步日期 2026-04-30）。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| sellerId | string | 是 | Ozon 卖家 ID（数字字符串），与商品列表/卖家榜中的卖家标识一致 |
| startDate | string | 否 | 统计起始日 `YYYY-MM-DD`；最晚昨日 |
| endDate | string | 否 | 统计结束日 `YYYY-MM-DD`；最晚昨日 |
| page | integer | 否 | 页码，从 1 开始 |
| pageSize | integer | 否 | 每页行数 1-100，默认 100 |
| sortField | string | 否 | 排序列名（snake_case），如 `sales`、`revenue`、`final_price`、`balance`、`rating` |
| sortDirection | string | 否 | `asc` / `desc` |
| currency | string | 否 | 货币代码，默认 `RUB`，如 `USD`、`EUR`、`CNY` |
| currencyRate | integer | 否 | 自定义汇率（配合非默认货币） |
| includeFbs | boolean | 否 | `true` 纳入 FBS，`false` 仅 FBO；未传时以服务实际默认值为准 |
| filters | array | 否 | 数值筛选条件列表，每项 `{field, op, value, value2?}`，多条件 AND |

#### filters 子字段

| 子字段 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| field | string | 是 | 列名（snake_case）。常用：`sales`、`final_price`、`rating`、`comments`、`balance`、`revenue`、`days_in_stock`、`turnover_days`、`lost_profit`、`category_position`。 |
| op | string | 是 | `GTE` / `LTE` / `GT` / `LT` / `EQ` / `NOT_EQ` / `BETWEEN` |
| value | number | 是 | 主值（`BETWEEN` 时为下界） |
| value2 | number | `BETWEEN` 必填 | 上界（闭区间） |

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| JSON 参数 | object | 是 | 首个位置参数，与上述请求体一致。 |
| --inline | CLI flag | 否 | 强制全量打印，仍保存完整响应。 |
| --no-cache | CLI flag | 否 | 跳过响应缓存读写；仍保存本次完整响应。 |

业务脚本调用公共 `call_api.run`，由公共调用器提供唯一一层 24 小时缓存，不另建业务缓存。缓存路径为：`<cwd>/linkfox/.cache/linkfox-mpstats-ozon-seller-products/linkfox-mpstats-ozon-seller-products-<hash>.json`，`hash` 为按键排序、`ensure_ascii=False` 的 JSON 参数串的 SHA-256 前 16 位。键序不影响命中，不主动补写默认参数。默认缓存返回体（包括空结果或错误体），过期、损坏或缺失时重新调用；命中对象附加 `_cache.hit=true`。相同参数可继续命中已有缓存；更换身份或网关后如需重新获取数据，显式使用 `--no-cache`。

网关优先读取 `LINKFOX_TOOL_GATEWAY` 并去除尾部 `/`。认证优先读取 `LINKFOX_AGENT_API_KEY`，其次 `LINKFOXAGENT_API_KEY`；两者均空时本地退出。保留 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 请求头透传。

业务入口在请求前检查当前目录及会话 `data` 目录可写，并将输出根目录限定在 `<cwd>/linkfox`，不回退到 `ACPX_WORKSPACES`、家目录或临时目录。`SESSION_ID` 用于任务聚合；未设置时生成同进程稳定的时间和随机标识。保存 `_meta.json`、`index.jsonl` 及完整数据文件；同秒多次调用时递增文件名中的微秒时间戳，避免覆盖先前响应。超过 8000 个 UTF-8 字节时仅输出摘要和最大列表前 3 项，`--inline` 除外。

#### 使用限制

- 只支持 Ozon 俄罗斯站。`sellerId` 必须是数字字符串；传名称、品牌或类目路径不会自动解析。仅有名称时先使用商品搜索确定卖家编号。
- 每页最多 100 条；日期为 T-1 数据，起止日期最晚昨日，不能把今日或未来日期作为结束日。
- 数值筛选条件按 AND 合并，`BETWEEN` 为闭区间且必须提供 `value2`；排序和筛选列使用 snake_case，不能直接用响应中的 camelCase 字段名替代。
- 同一会话、同一参数组合默认只调用一次；失败或空结果不自动更换关键词、翻页或修改邮编。继续查询前说明额外算力消耗。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 网关业务状态码（若返回），按公共响应码基本规则判断。 |
| errmsg | string | 网关消息（若返回），用于解释错误原因。 |
| code | string | 返回码，`"200"` 成功 |
| msg | string | 消息；成功为 `ok` |
| total | integer | 卖家下命中商品总数 |
| products | array | 商品列表（详见下方） |
| columns | array | 渲染列定义 |
| costTime | integer | 接口耗时（毫秒） |
| costToken | integer | 消耗 Token 数量 |
| type | string | 响应类型 |

#### products[*] 商品对象字段

按官方 outputSchema 定义（`_mpstats_ozon_sellerProducts`，同步日期 2026-05-06）。该 schema 与 `productSearch` / `brandProducts` / `categoryProducts` **完全共用**；4 个端点只是查询维度不同，返回的商品卡字段集完全一致。

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
| sourceTool | string | 来源工具 |
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
| position | integer | 当前查询维度（本端点为卖家）内排名 |
| categoryPosition | integer | 品类内排名 |
| revenueSharePercent | number | 该 SKU 在当前查询维度的销售额占比，0-100 |

#### 脚本附加字段

下列字段由本地调用与缓存逻辑按需产生，不属于商品对象。

| 字段 | 类型 | 说明 |
|------|------|------|
| _cache | object | 仅命中缓存的对象响应附加本地缓存标识。 |
| _cache.hit | boolean | 缓存命中时为 `true`。 |
| _http_status | integer | 业务入口为对象响应保留的实际 HTTP 状态；不是网关字段。缓存命中时为生成该缓存时的历史状态，不代表本次发起请求。旧缓存可能没有此字段，不补造状态。 |
| error | string | HTTP 错误体为空或不是有效 JSON、或连接失败时的本地错误说明；有效 JSON 错误体原样保留。 |
| details | string | HTTP 错误体非空且不是有效 JSON 时保留的原始内容。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。
- 脚本输出通过本地 `_http_status` 保留 HTTP 状态，并保留错误体中的业务字段、`error` 和 `details`。`401` / `402` 按认证或算力问题处理，其他非 `2xx` 状态按异常解释；连接失败没有 HTTP 状态，依据 `error` 解释。旧缓存缺少状态时不能仅因缺少 `errcode` 就确认成功，结合已有业务状态与消息判断；需要重新取得状态时先说明额外消耗，由用户决定是否以 `--no-cache` 刷新，不自动重试。

#### 业务规则

- 响应中的 `code` 为字符串，成功值为 `"200"`，`msg` 成功为 `ok`；保留这些业务字段，不用它们替代公共规则对 HTTP 和 `errcode` 的判断。
- 业务异常时结合 `errmsg`、`msg` 或完整错误体解释原因，常见情况为卖家编号不是数字、编号不存在、日期越过昨日。不自动改参数重试。
- `total` 为卖家下命中商品总数；`products` 为空时按空结果解释，不补造商品。计费规则为消耗算力 12；列表为空返回 0 算力 （限时），最终以实际扣除为准。
- `columns` 为接口返回的渲染列定义；子字段以实际返回为准，保留原始内容，不推断或补造结构。

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/mpstats/ozon/sellerProducts" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
    "sellerId": "3628678",
    "sortField": "revenue",
    "sortDirection": "desc",
    "pageSize": 100
  }'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-mpstats-ozon-seller-products",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```