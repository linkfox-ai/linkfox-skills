# Etsy 商品查询 接口说明

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

## 接口：Etsy 商品查询（`_ehunt_productQuery`）

LinkFox MCP 工具名为 `_ehunt_productQuery`，展示名为“Etsy商品查询”，`serverName` 为“第三方数据服务”。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/ehunt/etsy/productQuery`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| beginFavorites | integer，≥0 | 否 | 收藏数（起始），与结束值共同组成上游 favorites |
| beginFavoritesWeekly | integer，≥0 | 否 | 周新增收藏数（起始），与结束值共同组成上游 favorites_weekly |
| beginPrice | number，≥0 | 否 | 价格（起始），与结束价共同组成上游 price（如 20~100）；仅填一侧时上游为 起始~ 或 ~结束 |
| beginReviews | integer，≥0 | 否 | 评论数（起始），与结束值共同组成上游 reviews |
| beginReviewsWeekly | integer，≥0 | 否 | 周新增评论数（起始），与结束值共同组成上游 reviews_weekly |
| beginSales | integer，≥0 | 否 | 总销量（起始），与结束值共同组成上游 sales |
| beginSalesWeekly | integer，≥0 | 否 | 周销量（起始），与结束值共同组成上游 sales_weekly（如 1~100） |
| category | string, maxLen=1000 | 否 | 商品分类 ID（单品类），详见 商品分类接口 |
| country | string, maxLen=1000 | 否 | 发货国家 |
| currencyCode | string, default=USD, maxLen=1000 | 否 | 货币代码 |
| endFavorites | integer，≥0 | 否 | 收藏数（结束） |
| endFavoritesWeekly | integer，≥0 | 否 | 周新增收藏数（结束） |
| endPrice | number，≥0 | 否 | 价格（结束），与起始价共同组成上游 price |
| endReviews | integer，≥0 | 否 | 评论数（结束） |
| endReviewsWeekly | integer，≥0 | 否 | 周新增评论数（结束） |
| endSales | integer，≥0 | 否 | 总销量（结束） |
| endSalesWeekly | integer，≥0 | 否 | 周销量（结束） |
| isBestsell | integer | 否 | 是否畅销商品 |
| isPick | integer | 否 | 是否 Pick 商品 |
| isRaving | integer | 否 | 是否 Raving 商品 |
| listedTime | string, pattern | 否 | 上架时间不早于该日期（YYYY-MM-DD） |
| page | integer，≥1，默认 1 | 否 | 页码（从 1 开始） |
| pageSize | integer，1~100，默认 20 | 否 | 每页条数，最大 100，建议不超过 50 |
| productType | string，须符合 schema 正则 | 否 | 商品类型，多个逗号分隔：1=手工 2=复古 3=数字 4=定制 9=其他 |
| searchKey | string, maxLen=500 | 否 | 搜索关键词或 Etsy 商品 URL |
| sortBy | integer (1~6) | 否 | 排序字段（对应上游 sort_by，取值 1~6） |
| sortDesc | integer | 否 | 排序方向（对应上游 `desc`）。schema 示例：降序 `1`、升序 `2`（与店铺查询 `_ehunt_storeQuery` 的 1/0 编码不同） |
| status | integer | 否 | 商品状态（示例：1 上架，0 下架） |

#### 参数约束与使用限制

- `begin*` / `end*` 分别为同一范围的起止值，通常成对设置；价格允许单侧范围，具体约定见上表。
- `sortBy` 各数字对应的字段及 `productType` 的具体 schema 正则尚不明确；仅使用已确认的排序映射和符合网关 schema 的商品类型值，不自行补造映射或正则。
- 参数与返回结构以当前网关返回为准。未明确的标签筛选值和嵌套字段不猜测；响应中不存在的字段不补造。

#### 脚本选项与运行约定

业务脚本为 `scripts/etsy_product_query.py`，仅依赖 Python 3 标准库，所有业务 HTTP 调用均由 `scripts/call_api.py` 的 `run` 执行。

| 参数 / 配置 | 类型 | 必填 | 说明 |
|------|------|------|------|
| 第一个位置参数 | JSON | 是 | 查询参数对象，字段见上表。 |
| --inline | CLI flag | 否 | 强制完整打印标准输出，同时仍保存完整响应。 |
| --no-cache | CLI flag | 否 | 禁用响应缓存的读取与写入；不删除已有缓存。 |
| LINKFOX_AGENT_API_KEY | 环境变量 | 与备用变量任选其一 | 优先读取的接口密钥。 |
| LINKFOXAGENT_API_KEY | 环境变量 | 与主变量任选其一 | 备用接口密钥变量；主变量为空时读取。 |
| LINKFOX_TOOL_GATEWAY | 环境变量 | 否 | 优先使用的网关基础地址，默认 `https://tool-gateway.linkfox.com`；移除末尾 `/`。 |
| LINKFOX_TOOL_GATEWAY_BASE | 环境变量 | 否 | 备用网关变量；仅当 `LINKFOX_TOOL_GATEWAY` 为空时使用。 |
| LINKFOX_EHUNT_PRODUCT_QUERY_PATH | 环境变量 | 否 | 接口路径覆盖变量；默认 `ehunt/etsy/productQuery`，允许有或无开头 `/`。 |
| SESSION_ID | 环境变量 | 否 | 聚合同一任务；未提供时生成进程内稳定的会话标识。 |
| MESSAGE_ID / MODE_ID / APP_NAME | 环境变量 | 否 | 随同会话标识作为请求头传递，未提供则为空字符串。 |

- 默认使用 24 小时响应缓存；公共调用器是唯一缓存层。路径为 `<cwd>/linkfox/.cache/linkfox-etsy-product-query/linkfox-etsy-product-query-<参数哈希>.json`，哈希为按键排序的 JSON 文本的 SHA-256 前 16 位，符合该路径、哈希和有效期规则的已有缓存可直接复用。命中时标注 `_cache.hit=true`，过期或损坏时重新请求。
- 缓存键仅由查询 JSON 参数组成。切换密钥、网关或接口路径后，若需新结果，显式使用 `--no-cache`，避免复用已有结果。
- 完整响应按 UTF-8 保存到 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-etsy-product-query-<timestamp>.json`，记录 `_meta.json` 和 `index.jsonl`。业务封装使用微秒时间戳并独占预留文件，连续查询也各自留存；命中缓存同样保存一份会话数据。输出展示策略见 SKILL.md 的“输出策略”。
- 会话数据固定在当前工作目录，禁止写入 `/tmp`；目录不可写时在请求前报错，不回退到家目录、临时目录或 `ACPX_WORKSPACES`。目录检查由业务封装完成。
- 不修改接口响应状态或自行判定成功；包括错误在内的完整响应均按上述缓存规则保存，失败时不自动重试或变更条件。使用前按下方响应码规则判断实际结果。
- 认证或余额问题解决后，如用户决定按相同参数重试，使用 `--no-cache` 获取新响应，避免再次读到 24 小时内缓存的错误；该选项不删除或覆盖旧缓存，后续仍需新结果时也应显式使用。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| total | integer | 记录数（本页返回条数，便于与列表长度对齐） |
| sourceTool | string | 工具类型：ehunt |
| sourceType | string | 来源类型：etsy |
| columns | array | 渲染的列 |
| costToken | integer | 消耗 token（按本页返回条数估算） |
| productNum | integer | 符合条件的商品总数（上游 product_num） |
| title | string | 标题 |
| type | string | 渲染的样式 |
| products | array | Etsy 商品列表 |

#### `products[]` 元素

| 字段 | 类型 | 说明 |
|------|------|------|
| category | string | 类目名称 |
| favorites | integer | 收藏数 |
| favoritesWeekly | integer | 周新增收藏数 |
| imageUrl | string | 主图 URL |
| isBestsell | integer | 是否畅销：1=是 |
| isPick | integer | 是否 Pick：1=是 |
| isRaving | integer | 是否 Raving：1=是 |
| price | number | 价格 |
| productUrl | string | 商品链接 |
| releaseTime | string | 上架/发布时间 |
| reviews | integer | 评论数 |
| reviewsWeekly | integer | 周新增评论数 |
| salesTotal | integer | 总销量 |
| salesWeekly | integer | 周销量 |
| shipsFrom | string | 发货国家 |
| status | integer | 商品状态：1=上架，0=下架 |
| storeName | string | 店铺名称 |
| tags | string | 标签 |
| title | string | 商品标题 |

#### 状态与本地缓存字段

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 若网关返回此字段，按公共响应码基本规则判断。 |
| errmsg | string | 若返回，保留网关消息并据其含义解释原因。 |
| code | 以实际响应为准 | 上游可能在 JSON 根级返回；成功值以实际网关定义为准，不替代公共规则。 |
| _cache.hit | boolean | 本地命中缓存时由脚本标记为 true，不是服务端业务字段。 |

`columns` 元素按实际返回内容展示，不补造子字段。算力计算见 SKILL.md 的“算力消耗预估”。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 上游根级 `code` 的成功值以实际网关定义为准；保留原始值，不自行假定 `0` 或 `200` 一定成功。
- 脚本遇到带 JSON 响应体的 HTTP 错误时仅保留该响应体，不另附 HTTP 状态；若响应体未带状态或明确错误信息，不能仅凭缺少 `errcode` 判定成功。需要依据 HTTP 状态诊断时，直接调用接口并保留 HTTP 状态；后续请求仍须遵守 SKILL.md 的成本约束。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/ehunt/etsy/productQuery" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"searchKey":"poster","currencyCode":"USD","page":1,"pageSize":20}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-etsy-product-query",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
