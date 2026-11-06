# MPSTATS Ozon 类目商品 接口说明

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

## 接口：类目商品（categoryProducts）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/mpstats/ozon/categoryProducts`

### 请求参数

POST Body（JSON）。以下字段与工具网关当前登记的「MPSTATS-Ozon-类目商品」入参 schema 一致（同步日期 2026-04-30）。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| categoryPath | string | 是 | Ozon 俄语类目全路径，层级用 `/` 分隔，例如 `Одежда/Женская одежда/Футболки и топы женские` |
| startDate | string | 否 | 统计起始日 `YYYY-MM-DD`；最晚昨日 |
| endDate | string | 否 | 统计结束日 `YYYY-MM-DD`；最晚昨日 |
| page | integer | 否 | 页码，从 1 开始 |
| pageSize | integer | 否 | 每页行数 1-100，默认 100 |
| sortField | string | 否 | 排序列名（snake_case），如 `sales`、`revenue`、`final_price`、`balance`、`rating` |
| sortDirection | string | 否 | `asc` / `desc` |
| currency | string | 否 | 货币代码，默认 `RUB`，如 `USD`、`EUR`、`CNY` |
| currencyRate | integer | 否 | 自定义汇率（配合非默认货币） |
| includeFbs | boolean | 否 | 是否纳入 FBS 库存及销量；`true` 合并 FBS，`false` 仅保留 FBO |
| filters | array | 否 | 数值筛选条件列表，每项 `{field, op, value, value2?}`，多条件 AND |

#### filters 子字段

| 子字段 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| field | string | 是 | 列名（snake_case）。常用：`sales`（月销）、`final_price`（售价 RUB）、`rating`（评分 0-5）、`comments`（评论数）、`balance`（库存）、`revenue`（销售额 RUB）、`days_in_stock`、`turnover_days`、`lost_profit`、`category_position`。 |
| op | string | 是 | `GTE` / `LTE` / `GT` / `LT` / `EQ` / `NOT_EQ` / `BETWEEN` |
| value | number | 是 | 主值（`BETWEEN` 时为下界） |
| value2 | number | `BETWEEN` 必填 | 上界（闭区间） |

#### 参数约束与使用限制

- `categoryPath` 必须是 Ozon 平台完整俄语类目路径，各级用 `/` 分隔。片段、英文翻译或仅根类目通常返回空列表；本接口不浏览类目树，需从上游类目查询或商品详情、搜索的 `category` 取得准确路径。
- `startDate` 与 `endDate` 最晚为昨日，不能请求今日或未来数据。
- `filters` 中所有条件按 AND 组合；`BETWEEN` 使用 `value` 与 `value2` 表示闭区间。
- 请求排序和筛选使用 snake_case 列名，响应中的商品字段多为 camelCase，不直接用响应字段名替代查询列名。

#### 脚本选项与缓存

| 参数 / 约定 | 类型 | 必填 | 说明 |
|------|------|------|------|
| JSON 参数 | JSON object | 是 | 作为首个位置参数传入，内容为上表 POST Body，不自动更改条件或翻页。 |
| --inline | CLI flag | 否 | 强制全量打印，仍保存完整响应。 |
| --no-cache | CLI flag | 否 | 禁用本次响应缓存的读取与写入，不删除既有缓存。 |
| 响应缓存 | 本地文件 | 否 | 默认启用，时效 24 小时；按排序后的完整 JSON 参数生成缓存键，目录为 `<cwd>/linkfox/.cache/linkfox-mpstats-ozon-category-products/`。缓存由公共调用器管理，文件直接存储 JSON 响应，命中时添加标记 `_cache.hit`。 |
| 认证环境变量 | string | 是 | `LINKFOX_AGENT_API_KEY` 优先，兼容 `LINKFOXAGENT_API_KEY`；两者均无值时报告未配置密钥并退出。 |
| LINKFOX_TOOL_GATEWAY | string | 否 | 自定义网关基础地址，去掉尾部 `/`；未配置时使用公共规则中的默认地址。 |
| 会话请求头 | string | 否 | 读取环境变量 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME`，缺失时发空字符串。 |

完整响应固定保存在当前工作目录的 `linkfox/` 下，不受 `ACPX_WORKSPACES` 或公共调用器缓存的输出根目录影响；当前目录不可写时，在请求前报错，不回退到家目录或临时目录。同一秒内连续完成的调用使用高精度时间戳分别保存，避免覆盖前一份响应。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| code | string | 返回码，`"200"` 成功 |
| msg | string | 消息；成功为 `ok` |
| errcode | integer / string / null | 业务错误码；出现时按公共响应码基本规则判断 |
| errmsg | string | 错误说明，业务异常时用于判断原因 |
| total | integer | 类目下命中商品总数 |
| products | array | 商品列表（详见下方） |
| columns | array | 渲染列定义 |
| costTime | integer | 接口耗时（毫秒） |
| costToken | integer | 消耗 Token 数量 |
| type | string | 响应类型 |

#### products[*] 商品对象字段（39 个）

按官方 outputSchema 定义（`_mpstats_ozon_categoryProducts`，同步日期 2026-05-06）。该 schema 与 `productSearch` / `brandProducts` / `sellerProducts` **完全共用**；4 个端点只是查询维度不同，返回的商品卡字段集完全一致。

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
| position | integer | 当前查询维度（本端点为类目）内排名 |
| categoryPosition | integer | 品类内排名 |
| revenueSharePercent | number | 该 SKU 在当前查询维度的销售额占比，0-100 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- `code` 和 `msg` 的取值约定见响应结构，不覆盖公共规则对外层 HTTP 和 `errcode` 的判断。
- 正常响应后解析 `products`。`total` 表示类目下命中商品总数；空列表需结合查询条件解释，不自动更换路径或翻页试探。
- 类目路径非俄语、非完整路径或日期越过昨日可能导致业务异常；依据 `errmsg` 核对具体原因。

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/mpstats/ozon/categoryProducts" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
    "categoryPath": "Одежда/Женская одежда/Футболки и топы женские",
    "sortField": "revenue",
    "sortDirection": "desc",
    "pageSize": 100,
    "filters": [
      {"field": "sales", "op": "GTE", "value": 50},
      {"field": "rating", "op": "GTE", "value": 4.5}
    ]
  }'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-mpstats-ozon-category-products",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
