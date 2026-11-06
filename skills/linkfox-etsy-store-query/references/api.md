# Etsy 店铺查询 接口说明

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

## 接口：Etsy 店铺查询（_ehunt_storeQuery）

工具名 `_ehunt_storeQuery`（LinkFox MCP，`serverName`：第三方数据服务），MCP 展示名为「Etsy店铺查询」。参数与返回结构以当前网关返回为准。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/ehunt/etsy/storeQuery`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| beginFavorites | integer，≥0 | 否 | 店铺收藏数（起始），与结束值组成上游 favorites |
| beginFavoritesWeekly | integer，≥0 | 否 | 店铺周新增收藏（起始），与结束值组成上游 favorites_weekly |
| beginReviews | integer，≥0 | 否 | 店铺评论数（起始），与结束值组成上游 reviews |
| beginReviewsWeekly | integer，≥0 | 否 | 店铺周新增评论（起始），与结束值组成上游 reviews_weekly |
| beginSales | integer，≥0 | 否 | 店铺总销量（起始），与结束值组成上游 sales |
| beginSalesWeekly | integer，≥0 | 否 | 店铺周销量（起始），与结束值组成上游 sales_weekly，如 10,100 |
| beginStoreOpenedAt | string, pattern | 否 | 店铺开店时间区间起始（YYYY-MM-DD），与结束日期组成上游 start_at，如 2020-01-01~2023-01-01 |
| category | string, maxLen=1000 | 否 | 店铺主营分类 |
| country | string, maxLen=1000 | 否 | 店铺所在国家 |
| endFavorites | integer，≥0 | 否 | 店铺收藏数（结束） |
| endFavoritesWeekly | integer，≥0 | 否 | 店铺周新增收藏（结束） |
| endReviews | integer，≥0 | 否 | 店铺评论数（结束） |
| endReviewsWeekly | integer，≥0 | 否 | 店铺周新增评论（结束） |
| endSales | integer，≥0 | 否 | 店铺总销量（结束） |
| endSalesWeekly | integer，≥0 | 否 | 店铺周销量（结束） |
| endStoreOpenedAt | string, pattern | 否 | 店铺开店时间区间结束（YYYY-MM-DD） |
| isRaving | integer | 否 | 是否 Raving 店铺：1=是 |
| isStar | integer | 否 | 是否星标店铺：1=是 |
| page | integer，≥1，默认 1 | 否 | 页码（从 1 开始） |
| pageSize | integer，1~100，默认 20 | 否 | 每页条数，最大 100 |
| searchKey | string, maxLen=500 | 否 | 搜索关键词或店铺名称、店铺 URL |
| sortBy | integer (8~11) | 否 | 排序字段 sort_by：8=总销量，9=周销量，10=评论数，11=收藏数 |
| sortDesc | integer | 否 | 排序方向（对应上游 desc）：1=降序，0=升序；勿与商品接口的同名参数混用，也不要转换为布尔值。 |
| status | integer | 否 | 店铺状态：1=活跃，0=非活跃 |

#### 参数约束与使用限制

`begin*` / `end*` 对应同一上游范围的两端。数值区间组合为逗号范围（例如 `10,100`），日期区间对应上游 `start_at`（例如 `2020-01-01~2023-01-01`）；只填一侧时表示「起始~」或「~结束」，不要擅自补另一侧。

每页都是一次独立请求，算力预估见 [SKILL.md 的算力消耗预估](../SKILL.md#算力消耗预估)；`costToken` 保留接口原始值。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| total | integer | 记录数（本页返回条数） |
| sourceTool | string | 工具类型：ehunt |
| sourceType | string | 来源类型：etsy |
| stores | array | 店铺列表 |
| columns | array | 渲染的列 |
| costToken | integer | 消耗 token（按本页返回条数估算） |
| storeNum | integer | 符合条件的店铺总数（上游 store_num） |
| title | string | 标题 |
| type | string | 渲染的样式 |

#### `stores[]` 元素

| 字段 | 类型 | 说明 |
|------|------|------|
| category | array | 主营类目列表 |
| country | array | 国家/地区列表 |
| favorites | integer | 收藏数 |
| favoritesWeekly | integer | 周新增收藏数 |
| isRaving | integer | 是否 Raving：1=是 |
| isStar | integer | 是否星标：1=是 |
| logoUrl | string | 店铺头像 URL |
| productCount | integer | 店铺商品数量 |
| rating | number | 评分 |
| reviews | integer | 评论数 |
| reviewsWeekly | integer | 周新增评论数 |
| salesTotal | integer | 总销量 |
| salesWeekly | integer | 周销量 |
| shopWebsite | string | 店铺官网/外链 |
| startAt | string | 开店日期 |
| status | integer | 店铺状态：1=活跃，0=非活跃 |
| storeId | string | 店铺 ID |
| storeName | string | 店铺名称 |
| storeUrl | string | 店铺链接 |

#### 公共状态字段（如返回）

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 网关业务状态；按公共规则判断，不要求成功时必须存在。 |
| errmsg | string | 网关消息；根据实际返回解释原因。 |
| code | 未限定 | 上游 JSON 根级返回码，如返回则保留；成功值以实际网关定义为准，不预设为 0 或 200。 |

### 脚本与运行约定

`scripts/etsy_store_query.py` 使用 Python 3 标准库，通过公共 `scripts/call_api.py` 发送与 MCP 入参一致的 JSON，不加工或丢弃筛选字段。

| 参数 / 配置 | 类型 | 说明 |
|------|------|------|
| JSON 参数 | CLI 位置参数 | 第一个参数为完整 JSON 请求对象；脚本原样传递，不补默认值或转换整数筛选标记。 |
| --inline | CLI flag | 强制完整打印，同时保存完整响应。 |
| --no-cache | CLI flag | 禁用本次缓存读取和写入；默认缓存有效期为 24 小时。 |
| LINKFOX_AGENT_API_KEY | 环境变量 | 首选 API Key；为空时兼容 `LINKFOXAGENT_API_KEY`。 |
| LINKFOXAGENT_API_KEY | 环境变量 | 备用 API Key 变量；`LINKFOX_AGENT_API_KEY` 为空时使用。 |
| LINKFOX_TOOL_GATEWAY | 环境变量 | 优先使用的网关根 URL，默认 `https://tool-gateway.linkfox.com`。 |
| LINKFOX_TOOL_GATEWAY_BASE | 环境变量 | 备用网关根 URL 配置；仅未配置 `LINKFOX_TOOL_GATEWAY` 时使用。 |
| LINKFOX_EHUNT_STORE_QUERY_PATH | 环境变量 | 接口路径覆盖配置，默认 `ehunt/etsy/storeQuery`，不含域名，可带前导 `/`。 |
| SESSION_ID | 环境变量 | 会话目录聚合标识，同时随请求头传递；未配置时，落盘目录使用生成的进程内稳定标识，请求头值为空字符串。 |
| MESSAGE_ID / MODE_ID / APP_NAME | 环境变量 | 随同名请求头透传，未配置时为空字符串。 |

```bash
python scripts/etsy_store_query.py '{"searchKey":"ceramic","country":"US","page":1,"pageSize":20}' --inline
```

缓存键为排序后 JSON 参数的 SHA-256 前 16 位，缓存位置为 `<cwd>/linkfox/.cache/linkfox-etsy-store-query/`；由公共调用器维护唯一一层缓存。命中时标记 `_cache.hit` 并保留缓存命中提示；过期后重新查询。完整响应落盘、8 KB（8000 字节）输出阈值、摘要和会话元数据由公共调用器处理。完整响应的保存目录按以下顺序选择可写位置：`ACPX_WORKSPACES`、当前工作目录、用户目录、临时目录；正常运行应选择可写的项目工作目录。

缓存目录固定在当前工作目录下，不参与完整响应保存目录的回退选择；该目录需要可写。`--no-cache` 仍会初始化缓存目录，但不读取或写入缓存文件。

缓存也会保存网关业务错误或连接错误的响应，不会因结果为空或报错自动重试。缓存键仅包含请求参数，不包含 API Key、网关地址或路径；切换这些配置不会自动失效已有缓存。完成认证修复或确认需要重新请求时，可显式使用 `--no-cache` 跳过本次缓存读取和写入；它不会删除既有缓存，后续普通调用仍可能命中有效期内的现有缓存文件。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 若返回 404，可能是部署上的 HTTP 路径与默认不一致；用已有的 `listEnabledTool` 信息或由运维确认实际 path 后设置 `LINKFOX_EHUNT_STORE_QUERY_PATH`，不要自行试探未知路径。
- 没有匹配店铺时结合 `stores`、`total` 和 `storeNum` 说明空结果，不推断为认证失败。

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/ehunt/etsy/storeQuery" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"searchKey":"ceramic","country":"US","page":1,"pageSize":20}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-etsy-store-query",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```