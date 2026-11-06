# Kalodata TikTok Shop 店铺榜单与详情 接口说明

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

## 接口：店铺榜单

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/kalodata/shop/rank`

### 请求参数

#### POST Body（JSON）


| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| region | string | 否 | 地区/市场编码，例如 `US`。最大长度 1000 |
| dateRange | string | 否 | 时间范围，例如 `last7Day`（近7天）、`last30Day`（近30天）。最大长度 1000 |
| pageNumber | integer | 否 | 页码，取值 1-5（超范围返回 `errcode 501`） |
| pageSize | integer | 否 | 每页数量，取值 5-100 |
| language | string | 否 | 返回语言，例如 `zh-CN`、`en-US`。最大长度 1000 |
| currency | string | 否 | 货币单位，例如 `USD`。最大长度 1000 |
| category_ids | array<string> | 否 | 类目 ID 列表筛选；指定后返回对应类目下的成交金额 |
| revenue_range | string | 否 | 成交金额 / GMV 范围，左闭右开 |
| shop_type | string | 否 | 店铺类型：`BRAND`（品牌）或 `RETAILER`（零售商） |
| sortField | object | 否 | 排序条件；不排序时传空对象 `{}` 走默认榜单顺序 |

所有参数均可选，服务端默认地区、区间、页码、页大小、语言和币种均未明确，不自行假定。默认按 `revenue`（GMV）降序，每条记录带 `rank` 位次。`sortField` 不排序时传 `{}`；可用字段以网关实际接受的为准，不支持的字段回退默认排序，不尝试绕过逻辑。

本接口浏览榜单，不是关键词搜索。响应不包含 `total` 或总页数，即使 `outputSchema` 声明 `total`，也不能据此补造。需要继续翻页时，在用户任务范围与成本约束内请求下一页；某页条数少于 `pageSize` 时停止，且始终遵守 `pageNumber` 1–5、`pageSize` 5–100 的限制。

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| JSON 参数 | object | 是 | CLI 第一个位置参数为 JSON 对象，字段见上表；不自动补充市场、币种或日期范围。 |
| --inline | CLI flag | 否 | 强制完整打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 跳过业务缓存的读取和写入；不改变参数及输出策略。 |
| LINKFOX_TOOL_GATEWAY | string | 否 | 网关基础地址，默认 `https://tool-gateway.linkfox.com`，去掉尾部斜线后拼接接口路径。 |
| LINKFOX_AGENT_API_KEY | string | 否 | 优先使用的密钥；为空时回退 `LINKFOXAGENT_API_KEY`，均为空时退出。 |
| SESSION_ID | string | 否 | 请求头透传并用于会话目录；缺省时生成进程内稳定的会话标识。 |
| MESSAGE_ID / MODE_ID / APP_NAME | string | 否 | 分别原样透传同名请求头，缺省为空。 |

脚本提供 24 小时本地缓存：参数按键排序后 JSON 序列化，取 SHA-256 前 16 位作为键；缓存保留网关响应及本地 HTTP 状态，命中时添加 `_cache.hit=true`。不同接口的缓存文件按接口标识隔离，避免相同参数串用榜单与详情；缓存位置为 `<cwd>/linkfox/.cache/linkfox-kalodata-tiktok-shop/linkfox-kalodata-tiktok-shop-rank-<hash>.json`。过期或损坏时重新调用；业务缓存包括失败或空响应，不自动绕过缓存重试，需要明确重试时使用 `--no-cache`。业务封装调用 `call_api.run` 时始终传入 `--no-cache`，公共调用器不读写第二层响应缓存。

完整响应保存为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-kalodata-tiktok-shop-rank-<timestamp>.json`，并维护会话 `_meta.json` 与 `index.jsonl`。请求前检查当前目录和实际会话数据文件的可写性，不回退到家目录或临时目录；请求后若完整响应未成功保存，脚本以非零状态退出，不自动再次请求。使用微秒时间戳避免同秒调用覆盖。小响应完整打印，大响应摘要包含顶层字段、常见计数（如 `costToken`）、最大列表及前 3 条样本；阈值为 8000 个 UTF-8 字节。

### 响应结构

#### 顶层字段


| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer | 业务状态码，200 表示成功 |
| data | array | 店铺榜单列表 |
| costToken | integer | 本次调用扣费 token，固定 14000 |
| errmsg | string | 状态消息，成功时为 `ok` |

#### 脚本本地附加字段

- `_http_status`：脚本记录的实际 HTTP 状态码，不是网关业务字段；连接失败为 `null`。按本接口的响应码规则结合它与 `errcode` 判断结果，HTTP `401` / `402` 进入认证或算力引导。终端也单独显示该状态，避免大响应摘要遗漏。
- `_cache.hit=true`：命中本接口本地缓存；此时 `_http_status`、`errcode`、`costToken` 均来自历史响应，不代表本次发起请求或再次扣费。旧缓存未记录 HTTP 状态时，`_http_status=null` 表示历史状态未知，不能当作 HTTP 200；需要重新确认时，按成本约束使用 `--no-cache`，不自动重试。

#### data[*] 店铺对象


| 字段 | 类型 | 说明 |
|------|------|------|
| rank | integer | 排名位次（1 为最高） |
| shop_name | string | 店铺名称 |
| shop_id | string | 店铺唯一 ID（字符串，避免大整数精度丢失） |
| shop_type | string | 店铺类型（如 `BRAND`） |
| revenue | number | 总销售额 / GMV（按请求的 `currency` 货币） |
| sales_volumn | integer | 销量（注意字段拼写为 `volumn`） |
| on_sell_product_count | integer | 在售商品数 |
| unit_price | number | 件单价（按请求的 `currency` 货币） |
| revenue_growth_rate | number | 销售额增长率（%，可正可负） |
| self_promotion_revenue | number | 自营/自推广销售额 |
| affiliate_revenue | number | 达人分销销售额 |
| shopping_mall_revenue | number | 商城销售额 |

榜单的渠道关系为 `revenue` ≈ `self_promotion_revenue` + `affiliate_revenue` + `shopping_mall_revenue`；三项构成总收入，分项独立舍入时应按近似值展示。榜单不返回详情专有的 `creator_number`、`video_number`、`live_number`、`product_number`；不要混用详情的 `seller_type`、`self_account_revenue`、`shoppingmall_revenue`。

两接口均可能存在 T+1 统计延迟。以请求市场、区间与币种解释数据，不补造未返回指标。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

| errcode / 消息 | 含义 | 处理建议 |
|---|---|---|
| 400 | 参数缺失或非法 | 根据 `errmsg` 修正参数。 |
| 501，`page_number 范围为 1-5，当前: 999` 等 | 榜单参数越界 | 修正页码，后续请求遵守成本约束。 |
| 501，`调用 Kalodata 接口失败: Kalodata API HTTP 554: ` 等 | 上游瞬时错误 | 可用相同参数重试 1–2 次，不自动更换参数；重试遵守成本约束，并使用 `--no-cache` 避免复用失败响应。 |

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/kalodata/shop/rank" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"region":"US","dateRange":"last7Day","pageSize":10,"pageNumber":1}'
```

### 响应示例

以下响应示例节选榜单前 2 条，用于说明字段结构：

```json
{
  "errcode": 200,
  "data": [
    {
      "shop_id": "7495514739648989419",
      "revenue_growth_rate": 16.98,
      "revenue": 4036424.77,
      "sales_volumn": 142080,
      "on_sell_product_count": 146,
      "self_promotion_revenue": 133774.9,
      "affiliate_revenue": 3892218.48,
      "shop_type": "BRAND",
      "rank": 1,
      "shop_name": "medicube US Store",
      "unit_price": 28.41,
      "shopping_mall_revenue": 10431.39
    },
    {
      "shop_id": "7495830785034323995",
      "revenue_growth_rate": -4.78,
      "revenue": 2487949.36,
      "sales_volumn": 88156,
      "on_sell_product_count": 147,
      "self_promotion_revenue": 92771.54,
      "affiliate_revenue": 2383899.26,
      "shop_type": "BRAND",
      "rank": 2,
      "shop_name": "Dr.Melaxin",
      "unit_price": 28.22,
      "shopping_mall_revenue": 11278.56
    }
  ],
  "costToken": 14000,
  "errmsg": "ok"
}
```

## 接口：店铺详情

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/kalodata/shop/detail`

### 请求参数

#### POST Body（JSON）


| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| shopId | string | 是 | TikTok 店铺唯一 ID（字符串，避免大整数精度丢失），例如 `7495514739648989419`。可从店铺榜单响应的 `shop_id` 字段获取 |
| category_id | string | 否 | 类目 ID，可进一步限定返回的类目维度 |
| region | string | 否 | 地区/市场编码，例如 `US`。最大长度 1000 |
| dateRange | string | 否 | 时间范围，例如 `last7Day`、`last30Day`。最大长度 1000 |
| language | string | 否 | 返回语言，例如 `zh-CN`、`en-US`。最大长度 1000 |
| currency | string | 否 | 货币单位，例如 `USD`。最大长度 1000 |

`shopId` 必填，缺省无法返回有效结果；从榜单的 `shop_id` 或用户提供的标识取得，并保留字符串精度。本接口不能仅按关键词或店铺名查找店铺。无分页，成功时 `data` 是固定 1 个元素的数组，不含 `total`。其他可选参数的服务端默认值均未明确，不自行假定。

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| JSON 参数 | object | 是 | CLI 第一个位置参数为 JSON 对象，字段见上表；不自动补充市场、币种或日期范围。 |
| --inline | CLI flag | 否 | 强制完整打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 跳过业务缓存的读取和写入；不改变参数及输出策略。 |
| LINKFOX_TOOL_GATEWAY | string | 否 | 网关基础地址，默认 `https://tool-gateway.linkfox.com`，去掉尾部斜线后拼接接口路径。 |
| LINKFOX_AGENT_API_KEY | string | 否 | 优先使用的密钥；为空时回退 `LINKFOXAGENT_API_KEY`，均为空时退出。 |
| SESSION_ID | string | 否 | 请求头透传并用于会话目录；缺省时生成进程内稳定的会话标识。 |
| MESSAGE_ID / MODE_ID / APP_NAME | string | 否 | 分别原样透传同名请求头，缺省为空。 |

脚本提供 24 小时本地缓存：参数按键排序后 JSON 序列化，取 SHA-256 前 16 位作为键；缓存保留网关响应及本地 HTTP 状态，命中时添加 `_cache.hit=true`。不同接口的缓存文件按接口标识隔离，避免相同参数串用榜单与详情；缓存位置为 `<cwd>/linkfox/.cache/linkfox-kalodata-tiktok-shop/linkfox-kalodata-tiktok-shop-detail-<hash>.json`。过期或损坏时重新调用；业务缓存包括失败或空响应，不自动绕过缓存重试，需要明确重试时使用 `--no-cache`。业务封装调用 `call_api.run` 时始终传入 `--no-cache`，公共调用器不读写第二层响应缓存。

完整响应保存为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-kalodata-tiktok-shop-detail-<timestamp>.json`，并维护会话 `_meta.json` 与 `index.jsonl`。请求前检查当前目录和实际会话数据文件的可写性，不回退到家目录或临时目录；请求后若完整响应未成功保存，脚本以非零状态退出，不自动再次请求。使用微秒时间戳避免同秒调用覆盖。小响应完整打印，大响应摘要包含顶层字段、常见计数（如 `costToken`）、最大列表及前 3 条样本；阈值为 8000 个 UTF-8 字节。

### 响应结构

#### 顶层字段


| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer | 业务状态码，200 表示成功 |
| data | array | 单店铺详情，固定 1 元素数组 |
| costToken | integer | 本次调用扣费 token，固定 14000 |
| errmsg | string | 状态消息，成功时为 `ok` |

#### 脚本本地附加字段

- `_http_status`：脚本记录的实际 HTTP 状态码，不是网关业务字段；连接失败为 `null`。按本接口的响应码规则结合它与 `errcode` 判断结果，HTTP `401` / `402` 进入认证或算力引导。终端也单独显示该状态，避免大响应摘要遗漏。
- `_cache.hit=true`：命中本接口本地缓存；此时 `_http_status`、`errcode`、`costToken` 均来自历史响应，不代表本次发起请求或再次扣费。旧缓存未记录 HTTP 状态时，`_http_status=null` 表示历史状态未知，不能当作 HTTP 200；需要重新确认时，按成本约束使用 `--no-cache`，不自动重试。

#### data[*] 店铺对象


| 字段 | 类型 | 说明 |
|------|------|------|
| shop_id | string | 店铺唯一 ID（字符串，避免大整数精度丢失） |
| shop_name | string | 店铺名称 |
| seller_type | string | 店铺/卖家类型（如 `BRAND`）——详情用 `seller_type`，非 `shop_type` |
| region | string | 地区/市场（如 `US`） |
| revenue | number | 总销售额 / GMV（按请求的 `currency` 货币） |
| sales_volumn | integer | 销量（注意字段拼写为 `volumn`） |
| product_number | integer | 在售商品数 |
| unit_price | number | 件单价（按请求的 `currency` 货币） |
| self_account_revenue | number | 自营/自播自推销售额——详情用 `self_account_revenue`，非 `self_promotion_revenue` |
| affiliate_revenue | number | 达人分销销售额 |
| shoppingmall_revenue | number | 商城销售额（注意：`shopping` 与 `mall` 之间**无下划线**） |
| creator_number | integer | 达人合作数 |
| video_number | integer | 关联视频数 |
| live_number | integer | 关联直播数 |

详情的渠道关系为 `revenue` ≈ `self_account_revenue` + `affiliate_revenue` + `shoppingmall_revenue`。分项可能独立四舍五入，例如商城收入详情为 `10431.0`，榜单为 `10431.39`，不能视为精确恒等式。详情不返回 `rank`、`revenue_growth_rate`、`on_sell_product_count`，不要用榜单字段代替详情的实际字段。

两接口均可能存在 T+1 统计延迟。以请求市场、区间与币种解释数据，不补造未返回指标。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

| errcode / 消息 | 含义 | 处理建议 |
|---|---|---|
| 400，`shopId 为必填参数` | 店铺标识缺失或参数非法 | 补齐字符串 `shopId`，或按 `errmsg` 修正参数。 |
| 501，`调用 Kalodata 接口失败: Kalodata API HTTP 554: ` 等 | 上游瞬时错误 | 可用相同参数重试 1–2 次，不自动更换参数；重试遵守成本约束，并使用 `--no-cache` 避免复用失败响应。 |

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/kalodata/shop/detail" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"shopId":"7495514739648989419","region":"US","dateRange":"last7Day","currency":"USD"}'
```

### 响应示例

以下响应示例用于说明单店详情的字段结构：

```json
{
  "errcode": 200,
  "data": [
    {
      "self_account_revenue": 133774.9,
      "creator_number": 25367,
      "sales_volumn": 142080,
      "affiliate_revenue": 3892218.48,
      "video_number": 66199,
      "shop_name": "medicube US Store",
      "unit_price": 28.41,
      "shoppingmall_revenue": 10431.0,
      "product_number": 158,
      "shop_id": "7495514739648989419",
      "revenue": 4036424.77,
      "seller_type": "BRAND",
      "live_number": 8433,
      "region": "US"
    }
  ],
  "costToken": 14000,
  "errmsg": "ok"
}
```

---

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-kalodata-tiktok-shop",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
