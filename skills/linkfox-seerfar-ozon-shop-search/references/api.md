# Seerfar Ozon 店铺商品搜索 接口说明

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

## 接口：店铺商品搜索

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/seerfar/ozon/shopSearch`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | integer | 是 | 店铺（卖家）ID，即其他 Seerfar Ozon 工具返回的 `sellerId`；负值为 Ozon 平台自营卖家（如 `-2` Ozon Express、`-4` Ozon Fresh），正值为第三方卖家 |
| page | object | 是 | 分页与排序：`{page, pageSize, orders[]}` |
| page.page | integer | 否 | 页码，从 1 开始，默认 1 |
| page.pageSize | integer | 否 | 每页条数，默认 20，**最大 20**（超出返回 `errcode 1002`） |
| page.orders | array | 否 | 排序规则数组，每项为包含 `field` 与 `direction` 的对象，子字段定义见下方。 |
| page.orders[].field | string | 未单独约定 | 排序字段；常用值：`sales`、`price`、`reviewRating`、`upTime`。 |
| page.orders[].direction | string | 未单独约定 | 排序方向：`DESC`（倒序）/ `ASC`（正序）。 |
| uId | string | 否 | 用户 ID（最长 1000） |
| memberId | string | 否 | 成员 ID（一个成员唯一标识，一个用户可归属多个团队，数据归属于 memberId，最长 1000） |

#### 参数约束与使用限制

- `id` 与 `page` 缺任意一项返回 `errcode 400`；分页大小限制见参数表，翻页通过递增 `page.page`，以 `hasNextPage` 判断是否还有下一页。
- 建议始终传入 `page.orders`：按 `sales` 降序查畅销商品，按 `upTime` 降序查新品，按 `price` 降序查高价商品，避免无序翻页。
- 仅按店铺查询，不提供店名、文本或关键词过滤；只有名称时先通过其他 Seerfar Ozon 商品数据源取得 `sellerId`。

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| JSON 参数 | object | 是 | 命令行首个位置参数，内容为上述请求体。 |
| --inline | CLI flag | 否 | 强制完整打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 禁用本次响应缓存的读取与写入；默认缓存 24 小时。 |
| LINKFOX_TOOL_GATEWAY | 环境变量 | 否 | 优先使用指定网关，未配置时使用公共规则中的默认值。 |
| LINKFOX_AGENT_API_KEY / LINKFOXAGENT_API_KEY | 环境变量 | 是，二选一 | 前者优先，兼容后者；缺失时按认证指引处理。缓存命中时不发网络请求。 |
| SESSION_ID | 环境变量 | 否 | 聚合同一任务的数据；未配置时自动生成会话标识。 |
| MESSAGE_ID / MODE_ID / APP_NAME | 环境变量 | 否 | 与 `SESSION_ID` 一起作为同名请求头透传；未配置时为空。 |

业务入口调用公共 `call_api.run`，使用公共调用器的一层缓存。缓存位于 `<cwd>/linkfox/.cache/linkfox-seerfar-ozon-shop-search/`，缓存文件名为 `linkfox-seerfar-ozon-shop-search-<key>.json`，其中 `<key>` 为参数 JSON 排序序列化后 SHA-256 的前 16 位，有效期为 24 小时。缓存命中返回 `_cache.hit=true`。脚本会缓存返回结果（含空结果或错误体）；需要重新请求时显式使用 `--no-cache`，同时遵守成本约束。

完整数据与会话元信息必须保存在当前工作目录，业务入口在请求前使用与响应文件等长的名称检查输出路径可写，包括 Windows 路径长度限制；不采用 `ACPX_WORKSPACES`、家目录或临时目录回退。输出阈值、摘要与 `--inline` 行为见 `SKILL.md`。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| code | string | 返回码，`"200"` 表示成功（成功时返回） |
| errcode | integer | 错误码，`200` 表示成功；业务错误时仅返回此项（成功时与 `code` 并存） |
| msg | string | 消息；成功为 `ok` |
| errmsg | string | 错误消息；成功为 `ok`，业务错误时为原因描述 |
| total | integer | **本页返回记录数**（等于当前页数据条数，并非店铺商品总数） |
| totalSales | integer | 店铺近 30 天总销量，全店汇总，不受当前分页影响 |
| totalRevenue | integer | 店铺总销售额（卢布），全店汇总，不受当前分页影响 |
| dailySales | integer | 店铺日均销量，全店汇总，不受当前分页影响 |
| rating | number | 店铺评分（0-5） |
| productCount | integer | 店铺商品总数（全店铺，非本页条数） |
| fulfillment | object | 店铺配送方式分布，键为配送方式（`FBO`/`FBS`），值为该方式商品数，如 `{"FBO": 72, "FBS": 4}`（与商品级 `fulfillment` 数组不同） |
| data | array | 店铺商品列表（详见下方） |
| products | array | 店铺商品列表，内容与 `data` 完全一致 |
| hasNextPage | boolean | 是否有下一页 |
| columns | array | 列定义，元素字段见下方「columns[*] 列定义」 |
| type | string | 响应展示类型，如 `productWorkbenches` |
| costTime | integer | 接口耗时（毫秒） |
| costToken | integer | 消耗 Token 数量 |

#### data[*] / products[*] 店铺商品对象字段

| 字段 | 类型 | 说明 |
|------|------|------|
| productId | integer | 统一商品 ID，映射自 `sku` |
| sku | integer | 商品 SKU |
| rating | number | 统一评分，映射自 `reviewRating` |
| reviewRating | number | 商品评分 |
| weight | number | 商品重量，单位 g |
| sales | integer | 商品近 30 天销量 |
| monthlySalesUnits | integer | 统一月销量，映射自 `sales` |
| upTime | integer | 商品上架时间，毫秒时间戳 |
| price | number | 商品价格（卢布） |
| currency | string | 币种，固定 `₽` |
| imageUrl | string | 统一主图 URL |
| fulfillment | array | 商品配送方式，如 `["FBO"]`，可能含多个值 |
| sellerType | integer | 卖家类型：`0` 本土，`1` 跨境 |
| returnCancellationRate | number | 商品退货取消率（%）；第三方卖家普遍返回，平台自营卖家（负数 `id`）常缺失，使用前需判空。 |
| sourceType | string | 数据源，固定 `ozon` |
| sourceTool | string | 来源工具，如 `Seerfar-Ozon-查店铺` |

#### outputSchema 中定义但实际不返回的字段

| 字段 | 类型 | 说明 |
|------|------|------|
| data[*].productPageUrl / products[*].productPageUrl | 未约定 | 统一商品页 URL。上游无对应字段，schema 标注保持 null，实际响应直接省略，不是返回 null 或空值，不可依赖。 |
| data[*].monthlySalesRevenue / products[*].monthlySalesRevenue | 未约定 | 统一月销售额。上游无对应字段，schema 标注保持 null，实际响应直接省略，不是返回 null 或空值，不可依赖。 |
| data[*].brand / products[*].brand | 未约定 | 统一品牌。上游无对应字段，schema 标注保持 null，实际响应直接省略，不是返回 null 或空值，不可依赖。 |

#### columns[*] 列定义

下列子字段的类型未约定，以实际响应为准。

| 字段 | 类型 | 说明 |
|------|------|------|
| field | 未约定 | 列对应的字段。 |
| title | 未约定 | 列标题。 |
| cellType | 未约定 | 单元格类型。 |
| sortable | 未约定 | 是否支持排序。 |
| filterable | 未约定 | 是否支持过滤。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

本接口常见业务错误仍以 HTTP 200 返回，响应体仅含非正常的 `errcode` 与原因 `errmsg`，可能没有 `code`。

| errcode | 含义 | 处理建议 |
|---------|------|----------|
| 400 | 参数错误 | 查看 `errmsg`，常见原因是 `id 为必填参数` 或 `page 为必填参数`。 |
| 1002 | 分页参数超出限制 | 错误消息为 `分页参数超出限制，请检查输入。参数 page.pageSize 最大为 20，请调小后重试。`，按参数表修正后再决定是否重新调用。 |
| 1003 | 请求过于频繁 | 限流，稍候重试；遵守 `SKILL.md` 的成本约束。 |

不存在的店铺 `id` 不会报系统错误，可能返回 `errcode:200`、`total:0`、`data:[]`。正常响应下根据 `total=0` 判断本页无数据，提示用户核对店铺编号，不自动连续试探。

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/seerfar/ozon/shopSearch" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
    "id": 1362816,
    "page": {"page": 1, "pageSize": 20, "orders": [{"field": "sales", "direction": "DESC"}]}
  }'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-seerfar-ozon-shop-search",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```