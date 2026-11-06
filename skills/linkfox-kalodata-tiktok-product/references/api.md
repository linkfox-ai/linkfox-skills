# Kalodata TikTok 商品榜单与详情 接口说明

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

## 接口：商品榜单

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/kalodata/product/rank`

### 请求参数

POST Body（JSON），所有参数均可选：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| region | string | 否 | TikTok Shop 市场区域代码，例如 `US`。未指定时默认按服务端缺省（通常 US） |
| dateRange | string | 否 | 相对日期范围，例如 `last7Day`、`last30Day` |
| currency | string | 否 | 货币代码，例如 `USD` |
| language | string | 否 | 返回语言，例如 `zh-CN`、`en-US` |
| category_ids | array<string> | 否 | 类目 ID 列表筛选 |
| shop_id | string | 否 | 店铺 ID 筛选 |
| creator_id | string | 否 | 达人 ID 筛选 |
| video_id | string | 否 | 返回指定视频关联的商品 |
| livestream_id | string | 否 | 返回指定直播关联的商品 |
| revenue_range | string | 否 | 成交金额 / GMV 范围，左闭右开 |
| is_affiliate | string | 否 | 是否联盟商品：`PUBLIC_PLAN`（是）或 `NON_AFFILIATE`（否） |
| commission_rate | number | 否 | 联盟商品佣金率，例如 `0.15` |
| is_tts_product | integer | 否 | 是否全托管商品：`1`（全托管）或 `0`（非全托管） |
| unit_price_range | string | 否 | 商品价格范围，左闭右开 |
| sortField | object | 否 | 排序规格对象，省略时使用默认排行 |
| pageNumber | integer | 否 | 页码，范围 1–5 |
| pageSize | integer | 否 | 每页条数，范围 5–100 |

> 该接口用于浏览商品榜单，不支持关键词搜索。`sortField` 的可用排序字段以网关实际接受的为准；若传入不支持的排序字段，按服务端 `errmsg` 处理，不要臆造字段名或尝试绕过逻辑。

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 默认值与说明 |
|------|------|------|------|
| JSON 参数 | object | 是 | 命令行首个位置参数；字段与上述请求体一致，原值透传，不添加筛选或自动改参。 |
| --inline | CLI flag | 否 | 默认关闭；强制完整打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 默认关闭；跳过业务缓存的读取与写入。业务封装调用公共 `call_api.run` 时始终添加此选项，以免产生第二层响应缓存。 |

本地响应缓存有效期为 24 小时，位于 `<cwd>/linkfox/.cache/linkfox-kalodata-tiktok-product/`。缓存键由接口路径与按键排序后的参数共同计算摘要，仅匹配该键的缓存可命中，避免榜单与详情同参串用缓存。命中时标记 `_cache.hit=true`，仍保存本次完整响应。缓存保存完整响应（包括错误或空结果），不据缓存命中推断业务成功；需重新请求时由用户决定是否使用 `--no-cache`。

网关优先读取 `LINKFOX_TOOL_GATEWAY`，缺省使用正式地址；认证优先读取 `LINKFOX_AGENT_API_KEY`，回退 `LINKFOXAGENT_API_KEY`。请求头包含 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME`。禁止自动重试、换参数或批量翻页。

完整响应与会话 `_meta.json`、`index.jsonl` 保存在当前工作目录的 `linkfox/` 下；归档采用微秒时间戳，并在路径已存在时递增，避免同接口同一时刻覆盖；`skills_called` 按本技能名称登记。请求前检查当前目录是否可写，不回退家目录或临时目录。业务封装复用公共调用器已保存的响应路径，不额外生成第二份响应。输出阈值为 8000 个 UTF-8 字节，大响应仅展示摘要与前三条样本；`--inline` 强制完整输出。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer | 业务状态码，200 表示成功 |
| data | array | 商品榜单列表 |
| costToken | integer | 本次调用扣费 token，通常为 14000 |
| errmsg | string | 状态消息，成功时为 `ok` |

商品列表位于 `data` 数组；不返回 `total` 或总页数，返回条数使用 `data.length`。

#### data[*] 商品榜单对象

| 字段 | 类型 | 说明 |
|------|------|------|
| product_id | string | 商品 ID（字符串格式，避免大整数精度丢失）；作为 `productId` 查询详情 |
| product_name | string | 商品标题 |
| unit_price | number | 单价（货币随 `region`，如 `US` 为 USD） |
| sales_volumn | integer | 销量（件数）。注意接口字段名为 `sales_volumn`（原样拼写，非 `volume`），用 `jq`/`ConvertFrom-Json` 取值时须用此名 |
| revenue | number | 总销售额（GMV），= `video_revenue` + `live_revenue` + `showcase_revenue` |
| video_revenue | number | 视频渠道销售额 |
| live_revenue | number | 直播渠道销售额 |
| showcase_revenue | number | 橱窗/展示渠道销售额 |
| revenue_growth_rate | number | 销售额增长率（百分比，如 `27.94` 表示 27.94%） |
| commission_rate | number | 佣金率（百分比，如 `25.0` 表示 25%；**非基点**） |
| launch_date | string | 上架日期（`YYYY-MM-DD`） |

#### 脚本附加字段

| 字段 | 类型 | 说明 |
|------|------|------|
| _cache | object | 仅本地缓存命中时附加，不是网关字段。 |
| _cache.hit | boolean | 命中时为 true；不表示接口业务成功。 |
| _http_status | integer / null | 实际请求的 HTTP 状态；连接失败为 null。仅由脚本附加，非网关字段；缓存命中时表示被缓存请求的状态。 |

脚本附加的 `_http_status` 用于判断实际 HTTP 状态；连接失败时为 `null`，错误原因见 `error`。HTTP 非 2xx 时，即使正文没有 `errcode` 或其值为 200，也不属于正常响应。缓存命中时该字段表示被缓存请求的状态；既有缓存缺少该字段时，HTTP 状态未知。需要重新请求时，遵守成本约束并使用 `--no-cache`。

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

| 场景 | 说明与处理 |
|------|------|
| 正常响应但无数据 | 合法但无数据的请求（例如不支持的 `region`）可能返回 `errcode=200`，且不含 `data`，仍会扣费；说明为空结果，不自动改参探测。 |
| errcode=501，上游瞬时失败 | `errmsg` 如 `调用 Kalodata 接口失败: Kalodata API HTTP 522: `，也可能为 554 等上游 5xx。遵守成本约束，说明额外消耗后可用相同参数重试 1–2 次；脚本重试时加 `--no-cache`，否则会再次读取已缓存的错误，不会请求上游。不自动改参；持续失败联系网关侧检查上游配置（如服务端 `KALODATA_SECRET_KEY`）。脚本本身不自动重试。 |
| errcode=501，参数校验错误 | 按 `errmsg` 修正请求参数；例如 `page_number 范围为 1-5，当前: 99`。参数越界校验在计费前，不扣费。 |

#### 分页与使用限制

需要且用户已知额外消耗时，按用户任务范围逐页查询；某页条数少于 `pageSize` 或已到第 5 页即停止，不依赖不存在的总条数或总页数。

### 响应示例

```json
{
  "errcode": 200,
  "data": [
    {
      "revenue_growth_rate": 27.94,
      "revenue": 620518.0,
      "video_revenue": 592599.0,
      "sales_volumn": 33872,
      "product_id": "1729508370969629931",
      "showcase_revenue": 311.0,
      "commission_rate": 15.0,
      "launch_date": "2026-03-18",
      "unit_price": 18.32,
      "product_name": "[NEW] [medicube] PDRN Pink Collagen Volume Multi Balm | All In One Volufiline, PDRN, NAD Stick for Youthful-Looking, Helping Look of Fine Lines, Firming Care, Anti-Aging Care | For Under-Eyes, Neck, Forehead, Smile Lines, Lip Care | Korean Skincare",
      "live_revenue": 27608.0
    }
  ],
  "costToken": 14000,
  "errmsg": "ok"
}
```

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/kalodata/product/rank" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"region":"US","dateRange":"last7Day","pageSize":20,"pageNumber":1,"currency":"USD"}'
```

## 接口：商品详情

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/kalodata/product/detail`

### 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| productId | string | 是 | TikTok 商品 ID，例如 `1729508370969629931`（字符串，避免大整数精度丢失），可从商品榜单响应的 `product_id` 获取 |
| region | string | 否 | 地区/市场编码，例如 `US` |
| dateRange | string | 否 | 时间范围，例如 `last7Day`（近7天）、`last30Day`（近30天） |
| language | string | 否 | 返回语言，例如 `zh-CN`、`en-US` |
| currency | string | 否 | 货币单位，例如 `USD` |

> `productId` 为必填，缺失时网关返回业务错误。其余参数可选，省略时网关按默认处理。`region`/`dateRange`/`currency` 决定货币字段（`revenue`、`unit_price`、`min_price`、`max_price` 及渠道收入拆分）的口径与单位。本接口不支持按关键词/标题搜索商品；需先用榜单接口发现商品并获取 `product_id`，再用 `productId` 查询详情。

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 默认值与说明 |
|------|------|------|------|
| JSON 参数 | object | 是 | 命令行首个位置参数；字段与上述请求体一致，原值透传，不添加筛选或自动改参。 |
| --inline | CLI flag | 否 | 默认关闭；强制完整打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 默认关闭；跳过业务缓存的读取与写入。业务封装调用公共 `call_api.run` 时始终添加此选项，以免产生第二层响应缓存。 |

本地响应缓存有效期为 24 小时，位于 `<cwd>/linkfox/.cache/linkfox-kalodata-tiktok-product/`。缓存键由接口路径与按键排序后的参数共同计算摘要，仅匹配该键的缓存可命中，避免榜单与详情同参串用缓存。命中时标记 `_cache.hit=true`，仍保存本次完整响应。缓存保存完整响应（包括错误或空结果），不据缓存命中推断业务成功；需重新请求时由用户决定是否使用 `--no-cache`。

网关优先读取 `LINKFOX_TOOL_GATEWAY`，缺省使用正式地址；认证优先读取 `LINKFOX_AGENT_API_KEY`，回退 `LINKFOXAGENT_API_KEY`。请求头包含 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME`。禁止自动重试、换参数或批量翻页。

完整响应与会话 `_meta.json`、`index.jsonl` 保存在当前工作目录的 `linkfox/` 下；归档采用微秒时间戳，并在路径已存在时递增，避免同接口同一时刻覆盖；`skills_called` 按本技能名称登记。请求前检查当前目录是否可写，不回退家目录或临时目录。业务封装复用公共调用器已保存的响应路径，不额外生成第二份响应。输出阈值为 8000 个 UTF-8 字节，大响应仅展示摘要与前三条样本；`--inline` 强制完整输出。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer | 业务状态码，200 表示成功 |
| data | array | 单商品详情数据，正常有数据时固定为 1 元素数组 |
| costToken | integer | 本次调用扣费 token，通常为 14000 |
| errmsg | string | 状态消息，成功时为 `ok` |

详情的 `data` 固定为 1 元素数组，读取 `data[0]`；不返回 `total` 或总页数。

#### data[0] 商品详情对象

| 字段 | 类型 | 说明 |
|------|------|------|
| product_id | string | 商品唯一 ID（字符串，避免大整数精度丢失） |
| product_name | string | 商品名称 |
| product_region | string | 商品所在地区/市场（如 `us`） |
| product_shop_id | string | 所属店铺 ID |
| pri_cate_id | string | 一级类目 ID |
| sec_cate_id | string | 二级类目 ID |
| ter_cate_id | string | 三级类目 ID |
| unit_price | number | 件单价（按请求的 `currency` 货币） |
| min_price | number | 最低价（按请求的 `currency` 货币） |
| max_price | number | 最高价（按请求的 `currency` 货币） |
| revenue | number | 总销售额 / GMV（按请求的 `currency` 货币），等于 `video_revenue` + `live_revenue` + `shopping_mall_revenue` |
| sales_volumn | integer | 销量（件数），接口拼写为 `volumn`，用 `jq` / `ConvertFrom-Json` 抽取时不要改成 `volume` |
| commission_rate | number | 佣金率，**直接百分比**（25.0 表示 25%） |
| product_review_count | integer | 商品评论数 |
| launch_date | string | 上架日期（`YYYY-MM-DD`） |
| delivery_type | string | 配送方式（如 `local`） |
| video_number | integer | 关联视频数 |
| video_revenue | number | 视频带来的销售额（按请求的 `currency` 货币） |
| live_number | integer | 关联直播数 |
| live_revenue | number | 直播带来的销售额（按请求的 `currency` 货币） |
| shopping_mall_revenue | number | 商城销售额（按请求的 `currency` 货币） |
| creator_number | integer | 关联达人数 |

#### 脚本附加字段

| 字段 | 类型 | 说明 |
|------|------|------|
| _cache | object | 仅本地缓存命中时附加，不是网关字段。 |
| _cache.hit | boolean | 命中时为 true；不表示接口业务成功。 |
| _http_status | integer / null | 实际请求的 HTTP 状态；连接失败为 null。仅由脚本附加，非网关字段；缓存命中时表示被缓存请求的状态。 |

脚本附加的 `_http_status` 用于判断实际 HTTP 状态；连接失败时为 `null`，错误原因见 `error`。HTTP 非 2xx 时，即使正文没有 `errcode` 或其值为 200，也不属于正常响应。缓存命中时该字段表示被缓存请求的状态；既有缓存缺少该字段时，HTTP 状态未知。需要重新请求时，遵守成本约束并使用 `--no-cache`。

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

| 场景 | 说明与处理 |
|------|------|
| 正常响应但无数据 | 合法但无数据的请求（例如不支持的 `region`）可能返回 `errcode=200`，且不含 `data`，仍会扣费；说明为空结果，不自动改参探测。 |
| errcode=501，上游瞬时失败 | `errmsg` 如 `调用 Kalodata 接口失败: Kalodata API HTTP 522: `，也可能为 554 等上游 5xx。遵守成本约束，说明额外消耗后可用相同参数重试 1–2 次；脚本重试时加 `--no-cache`，否则会再次读取已缓存的错误，不会请求上游。不自动改参；持续失败联系网关侧检查上游配置（如服务端 `KALODATA_SECRET_KEY`）。脚本本身不自动重试。 |
| errcode=501，参数校验错误 | 按 `errmsg` 修正请求参数；例如 `productId` 缺失或非法。参数校验在计费前，不扣费。 |

### 响应示例

```json
{
  "errcode": 200,
  "data": [
    {
      "sec_cate_id": "848776",
      "product_region": "us",
      "creator_number": 4164,
      "video_revenue": 592599.0,
      "sales_volumn": 33872,
      "video_number": 8271,
      "ter_cate_id": "601611",
      "unit_price": 18.32,
      "product_name": "[NEW] [medicube] PDRN Pink Collagen Volume Multi Balm | All In One Volufiline, PDRN, NAD Stick for Youthful-Looking, Helping Look of Fine Lines, Firming Care, Anti-Aging Care | For Under-Eyes, Neck, Forehead, Smile Lines, Lip Care | Korean Skincare",
      "revenue": 620518.0,
      "max_price": 19.0,
      "min_price": 19.0,
      "delivery_type": "local",
      "product_review_count": 42277,
      "product_id": "1729508370969629931",
      "pri_cate_id": "601450",
      "live_number": 2053,
      "commission_rate": 15.0,
      "launch_date": "2026-03-18",
      "shopping_mall_revenue": 311.0,
      "product_shop_id": "7495514739648989419",
      "live_revenue": 27608.0
    }
  ],
  "costToken": 14000,
  "errmsg": "ok"
}
```

> 上例中 `revenue` (620518.0) = `video_revenue` (592599.0) + `live_revenue` (27608.0) + `shopping_mall_revenue` (311.0)，渠道拆分自洽。脚本落盘的完整 JSON 包含全部字段，建议用 `jq` 或 `ConvertFrom-Json` 按需抽取。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/kalodata/product/detail" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"productId":"1729508370969629931","region":"US","dateRange":"last7Day","currency":"USD"}'
```

---

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-kalodata-tiktok-product",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
