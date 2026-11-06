# 卖家精灵类目市场统计 接口说明

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

## 接口：选市场统计

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/sellersprite/market/statistics`

### 请求参数

| 参数 | 类型 | 必填 | 约束 | 说明 |
|------|------|------|------|------|
| marketplace | string | 是 | maxLength 1000，默认 `US` | 站点编码，见 [marketplace](#marketplace-可选值) |
| nodeIdPath | string | 是 | maxLength 1000 | 节点 ID 路径字符串，如 `1064954:1069242:1069784:1069820:1069838:1069828` |
| month | string | 否 | 见 [month](#month) | 筛选日期：`nearly` 或 `yyyyMM` |
| topN | integer | 否 | 默认 `10` | 头部 Listing 数量（用于头部相关指标口径） |
| newProduct | integer | 否 | 默认 `6` | 新品定义（月） |

#### marketplace 可选值

| 取值 | 含义 |
|------|------|
| US | 美国站 USD($) |
| JP | 日本站 JPY(￥) |
| UK | 英国站 GBP(£) |
| DE | 德国站 EUR(€) |
| FR | 法国站 EUR(€) |
| IT | 意大利站 EUR(€) |
| ES | 西班牙站 EUR(€) |
| CA | 加拿大站 C$($) |
| IN | 印度站 INR(₹) |

#### month

- **格式**：正则 `^(nearly|(19|20)\d{2}(0[1-9]|1[0-2]))$`
- **`nearly`**：最近 30 天
- **`yyyyMM`**：具体月份（如 `202507`）；最多支持**当前月往前共 24 个月内**的月份

#### 参数与使用限制

- `nodeIdPath` 必须为合法类目节点路径，不能以类目名称替代。

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| JSON 参数 | JSON string | 是 | 首个位置参数，内容为上方请求参数对象。 |
| --inline | CLI flag | 否 | 强制全量打印到标准输出，仍保存完整响应。 |
| --no-cache | CLI flag | 否 | 禁用本次缓存读取和写入；未传时启用 24 小时缓存。 |

- 调用入口：`python scripts/sellersprite_market_statistics.py '<JSON 参数>' [--inline] [--no-cache]`。
- 只有公共调用器提供的一层缓存：缓存键为参数 JSON 按键排序后的 SHA-256 前 16 位，位置为 `<cwd>/linkfox/.cache/linkfox-sellersprite-market-statistics/linkfox-sellersprite-market-statistics-<key>.json`；24 小时内可复用，命中时字典结果附带 `_cache.hit=true`。缓存文件使用 JSON 格式。
- 缓存仅由请求参数决定，不含 API Key 或网关地址。切换网关或账号后需要实时结果时，显式使用 `--no-cache`；该操作会发起新的请求并可能扣费。
- 完整响应使用 UTF-8 保存到 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-sellersprite-market-statistics-<timestamp>.json`，会话优先采用 `SESSION_ID`，否则进程内生成稳定会话标识；维护 `_meta.json` 和 `index.jsonl`。
- 输出根目录固定为当前工作目录下的 `linkfox/`，禁止写入 `/tmp`，目录不可写时应报错；请求前创建会话数据目录并检查可写性，不回退家目录或临时目录。
- 以 UTF-8 序列化响应的 **8000 字节**为界：不超过则全量打印，超过则摘要；摘要含顶层字段、常见计数、最大列表长度及前 3 条样本。
- `LINKFOX_TOOL_GATEWAY` 支持自定义网关并去掉末尾 `/`；认证优先 `LINKFOX_AGENT_API_KEY`，兼容 `LINKFOXAGENT_API_KEY`，透传 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 请求头。

### 响应结构

#### 顶层字段

| 字段 | 类型 | 说明 |
|------|------|------|
| total | integer | 总条数 |
| marketplace | string | 站点编码 |
| data | array | 统计结果列表（对应第三方 `data`） |
| columns | array | 渲染的列 |
| costToken | integer | 消耗 token |
| type | string | 渲染的样式 |

#### 脚本本地附加字段

- `_http_status`：业务脚本保留的实际 HTTP 状态码，不是网关响应字段。结合该值和响应体 `errcode` 按公共规则判断；HTTP `401` / `402` 按 `references/onboarding.md` 处理，即使响应体未提供相应错误码。
- `_response_body`：仅当响应 JSON 不是对象时，用于保留原始 JSON 值；非 JSON 响应保存在 `details` 中，并带有 `error`，不能作为有效市场统计解读。
- 缓存中的 `_http_status` 是生成缓存时的历史状态，不代表本次重新请求；旧缓存若无此字段，不能据此假定 HTTP 成功。需要确认当前状态时，先说明额外消耗，再使用 `--no-cache`，不自动重试。

#### data[] 元素（单条节点统计）

工具 schema 中 `hl*` 表示 **头部 Listing 前 N 名**（N 由请求参数 `topN` 决定）。

##### 节点与站点

| 字段 | 类型 | 说明 |
|------|------|------|
| nodeIdPath | string | 节点 ID 路径 |
| nodeLabelPath | string | 节点名称路径 |
| nodeLabelLocale | string | 节点名称翻译 |
| nodeLabelPathLocale | string | 节点名称路径翻译 |
| marketplace | string | 市场标志 |
| countryCode | string | 国家二简码 |
| currency | string | 该市场的货币类型 |

##### 规模与样本

| 字段 | 类型 | 说明 |
|------|------|------|
| totalProducts | integer | 商品总数 |
| products | integer | 样品商品数 |
| sellers | integer | 卖家数 |
| brands | integer | 品牌数 |
| avgSellers | number | 平均卖家数 |
| hlProducts | integer | 头部 Listing 前 N 名商品样本数 |

##### 市场整体指标

| 字段 | 类型 | 说明 |
|------|------|------|
| avgUnits | integer | 月均销量 |
| avgRevenue | number | 月均销售额 |
| avgPrice | number | 平均价格 |
| avgRating | number | 平均星级 |
| avgRatings | integer | 平均评分数 |
| avgRatingsCv | integer | 月评论平均增长数 |
| avgBsr | integer | 平均 BSR |
| avgProfit | number | 平均利润率 |
| avgWeight | number | 平均重量(pound) |
| baseAvgWeight | number | 平均重量(g) |
| avgVolume | number | 平均体积(in³) |
| baseAvgVolume | number | 平均体积(cm³) |

##### 头部 Listing（前 N 名，N = topN）

| 字段 | 类型 | 说明 |
|------|------|------|
| hlAvgUnits | integer | 头部 Listing 前 N 名商品月均销量 |
| hlAvgRevenue | number | 头部 Listing 前 N 名商品月均销售额 |
| hlAvgPrice | number | 头部 Listing 前 N 名商品平均价格 |
| hlAvgRating | number | 头部 Listing 前 N 名商品平均星级 |
| hlAvgRatings | integer | 头部 Listing 前 N 名商品平均评论数 |
| hlAvgRatingsCv | integer | 头部 Listing 前 N 名商品月评论平均增长数 |
| hlAvgBsr | integer | 头部 Listing 前 N 名商品平均 BSR |

##### 新品（口径由 newProduct 定义）

| 字段 | 类型 | 说明 |
|------|------|------|
| newProducts | integer | 新品数量 |
| newProductProportion | number | 新品数量占比 |
| newAvgUnits | integer | 新品月均销量 |
| newAvgRevenue | number | 新品月均销售额 |
| newAvgPrice | number | 新品平均价格 |
| newAvgRating | number | 新品平均星级 |
| newAvgRatings | integer | 新品平均评分数 |
| minNewRatings | integer | 最低新品评分数 |
| maxNewRatings | integer | 最高新品评分数 |

##### 上架时间

| 字段 | 类型 | 说明 |
|------|------|------|
| firstShelfDate | string | 商品首次上架日期 |
| lastShelfDate | string | 商品最新上架日期 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 该接口未声明额外业务错误码；依据公共响应码规则和响应体的 `errmsg` 判断，不根据未声明的数值自行推断成功或失败。
- 空统计结果应结合本次站点、节点和月份解释；不自动修改参数反复查询。

### curl 示例

```bash
curl -X POST https://tool-gateway.linkfox.com/sellersprite/market/statistics \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"marketplace":"US","nodeIdPath":"172282:281407","month":"nearly","topN":10,"newProduct":6}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-sellersprite-market-statistics",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```