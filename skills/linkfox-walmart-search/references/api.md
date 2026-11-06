# Walmart 商品搜索 接口说明

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

## 接口：搜索商品列表

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/walmart/search`

### 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| keyword | string | 否* | 搜索关键词，最大长度1024字符。*与 categoryId 至少提供一个 |
| categoryId | string | 否* | 类目ID，*与 keyword 至少提供一个。`0` 表示所有部门。例如：`976759_976787` 表示"Cookies" |
| sort | string | 否 | 排序方式。可选值：`price_low`（价格从低到高）、`price_high`（价格从高到低）、`best_seller`（最畅销）、`best_match`（最佳匹配） |
| page | integer | 否 | 页码，用于分页，范围 1–100，默认 1 |
| minPrice | number | 否 | 最低价格 |
| maxPrice | number | 否 | 最高价格 |
| spelling | boolean | 否 | 激活拼写修正，默认 `true`。`true` 包含拼写修正，`false` 不包含 |
| softSort | boolean | 否 | 按相关性排序，默认为 `true`。设置为 `false` 可禁用按相关性排序 |
| storeId | string | 否 | 商店ID，用于按特定商店筛选产品 |
| device | string | 否 | 设备类型，默认 `desktop`。可选值：`desktop`（桌面浏览器）、`tablet`（平板浏览器）、`mobile`（移动浏览器） |
| facet | string | 否 | 过滤条件，格式为 key:value 对，用 `\|\|` 分隔 |
| nextDayEnabled | boolean | 否 | 仅显示NextDay配送结果，默认 `false`。`true` 启用，`false` 禁用 |
| jsonRestrictor | string | 否 | JSON字段限制器 |

#### 参数约束与使用限制

- `keyword` 与 `categoryId` 至少提供一个，可以同时使用。仅按类目浏览时可不传关键词。
- 不传 `sort` 时使用默认相关性排名；接口不提供评分排序参数，评分比较仅基于实际返回的商品，不代表全站排名。
- 仅返回当前列表数据；评论信息限评分与数量，不含评论正文，也不提供历史价格或历史销量。

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| JSON 参数 | JSON | 是 | 第一个位置参数，内容为上方 POST Body。 |
| --inline | CLI flag | 否 | 强制完整打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 绕过缓存读取与写入，不删除已有缓存；公共调用器仍可能创建缓存目录。 |

- 脚本使用公共调用器的一层 24 小时缓存。目录为 `<cwd>/linkfox/.cache/linkfox-walmart-search/`，文件名为 `linkfox-walmart-search-<key>.json`；键为参数按字段名排序、保留非 ASCII 字符的 JSON 序列化后的 SHA-256 前 16 位。缓存按文件修改时间判断有效期；命中时添加 `_cache.hit=true`。
- 缓存按参数区分，不按密钥、网关或会话区分；失败响应也可能被缓存。需要明确刷新时使用 `--no-cache`，避免把缓存快照当成实时复查。
- 完整响应按 `SESSION_ID` 聚合，并更新会话 `_meta.json` 和 `index.jsonl`。业务脚本只写当前工作目录的 `linkfox/`，在请求前准备会话元数据，并检查根目录及实际 `data/` 目录能否创建与写入，不可用时直接报错，不使用家目录或临时目录回退。
- 网关使用 `LINKFOX_TOOL_GATEWAY`，缺省为公共规则中的正式地址；认证优先 `LINKFOX_AGENT_API_KEY`，其次 `LINKFOXAGENT_API_KEY`。请求包含 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 请求头，超时为 150 秒。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 网关业务状态码，按公共规则判断；认证失败时可返回 401。 |
| errmsg | string | 错误消息，认证失败时可返回 authorized error。 |
| errorCode | integer | 业务码，200 表示业务成功，其他值表示业务错误；与 errcode 分别读取，不替代公共规则中的 errcode 判断。 |
| total | integer | 记录数 |
| products | array | 产品列表（见下方产品对象） |
| columns | array | 渲染的列 |
| type | string | 渲染的样式 |
| costToken | integer | 消耗token |

#### products[*] 产品对象

| 字段 | 类型 | 说明 |
|------|------|------|
| productId | string | 产品ID |
| usItemId | string | US商品ID |
| title | string | 标题 |
| description | string | 描述 |
| price | number | 价格 |
| wasPrice | number | 原价（was_price） |
| currency | string | 货币单位 |
| minPrice | number | 最低价格（用于多选项商品） |
| pricePerUnitAmount | string | 单价金额 |
| pricePerUnit | string | 单价单位 |
| rating | number | 评分 |
| reviews | integer | 评价数 |
| sellerName | string | 卖家名称 |
| sellerId | string | 卖家ID |
| imageUrl | string | 缩略图 |
| productPageUrl | string | 产品页面URL |
| sponsored | boolean | 是否是赞助商品 |
| outOfStock | boolean | 是否缺货 |
| freeShipping | boolean | 是否免运费 |
| twoDayShipping | boolean | 是否支持两日配送 |
| freeShippingWithWalmartPlus | boolean | Walmart Plus会员免运费 |
| shippingPrice | number | 运费 |
| multipleOptionsAvailable | boolean | 是否有多个选项或变体 |
| variantSwatches | array | 变体样本列表，各项字段见下方变体对象。 |
| sourceTool | string | 来源工具 |
| sourceType | string | 来源类型：walmart |

#### products[*].variantSwatches[*] 变体对象

以下字段的类型、是否返回及默认值以实际响应为准，不预设类型或补造缺省值。

| 字段 | 类型 | 说明 |
|------|------|------|
| name | 以实际响应为准 | 变体名称。 |
| imageUrl | 以实际响应为准 | 变体图片URL。 |
| productPageUrl | 以实际响应为准 | 变体产品页面URL。 |
| variantFieldId | 以实际响应为准 | 变体字段ID。 |


### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 先按基础规则判断 HTTP 与网关状态；响应另含 `errorCode` 时，`200` 表示业务成功，其他值表示业务错误，结合 `errmsg` 解释原因。分别读取 `errorCode` 和 `errcode`，不互相替代；HTTP 200 本身不能证明业务成功。
- 认证失败（401 或 `authorized error`）及计费不足（402）按 SKILL.md 的“解决认证和算力问题”处理；其他业务异常依据 `errmsg` 说明原因，不自动连续试探。
- 脚本对 HTTP 错误返回的可解析 JSON 只保存响应体，不额外记录实际 HTTP 状态；不可解析或空正文时，`error` 中包含 HTTP 状态，`details`（如有）保留正文。读取脚本结果时结合 `errcode`、`errorCode` 和错误消息判断；缺少状态码不能据此证明 HTTP 成功。缓存命中仅表示复用了历史响应，不表示本次请求已成功或认证、余额已恢复。

认证错误响应示例：

```json
{
  "errcode": 401,
  "errmsg": "authorized error"
}
```

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/walmart/search" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"keyword": "wireless earbuds", "sort": "best_seller", "page": 1}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-walmart-search",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
