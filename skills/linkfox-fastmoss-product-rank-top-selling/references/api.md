# FastMoss TikTok 热销商品排行 接口说明

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

## 接口：热销商品排行

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/fastmoss/productRankTopSelling`

### 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| region | string | 是 | 市场区域代码。可选值：US（美国）、GB（英国）、MX（墨西哥）、ES（西班牙）、DE（德国）、IT（意大利）、FR（法国）、ID（印度尼西亚）、VN（越南）、MY（马来西亚）、TH（泰国）、PH（菲律宾）、BR（巴西）、JP（日本）、SG（新加坡）。用户未指定市场时，由调用方使用 `US` |
| dateInfo | object | 是 | 日期规格对象，包含 `type` 和 `value` 两个字段 |
| dateInfo.type | string | 是 | 时间粒度：`day`（日）、`week`（周）、`month`（月） |
| dateInfo.value | string | 是 | 日期值：day 格式 `YYYY-MM-DD`，week 格式 `YYYY-周数`（如 `2025-18`），month 格式 `YYYY-MM`（如 `2025-02`）；day 示例 `2025-02-01` |
| category | string | 否 | 商品类目名称（英文），会匹配到 TikTok 类目 ID。非英文输入需先翻译为英文 |
| orderby | object | 否 | 排序规则对象，包含 `field` 和 `order` 两个字段 |
| orderby.field | string | 否 | 排序字段：`units_sold`（销量）、`gmv`（销售额）、`total_units_sold`（总销量）、`total_gmv`（总销售额）、`growth_rate`（增长率） |
| orderby.order | string | 否 | 排序方向：`desc`（降序）、`asc`（升序），默认 `desc` |
| page | integer | 否 | 页码，从 `1` 开始，默认 `1` |
| pageSize | integer | 否 | 每页条数，最大 `10`，默认 `10` |

#### 使用限制

- 本接口不支持关键词搜索；按关键词找商品使用 `linkfox-fastmoss-product-search`。
- 数据存在 T+1 统计延迟，不将榜单解释为实时成交数据。

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| JSON 参数 | object | 是 | 第一个位置参数，内容为上方 POST Body；脚本不另行填充市场或日期。 |
| --inline | CLI flag | 否 | 强制完整打印响应，同时保存完整数据。 |
| --no-cache | CLI flag | 否 | 跳过响应缓存读取与写入，仍保存本次完整响应。 |
| LINKFOX_TOOL_GATEWAY | 环境变量 | 否 | 自定义网关基础地址，移除末尾 `/` 后拼接接口路径。 |
| SESSION_ID | 环境变量 | 否 | 会话目录标识；未设置时生成进程内稳定的标识。 |
| MESSAGE_ID / MODE_ID / APP_NAME | 环境变量 | 否 | 与 `SESSION_ID` 一起透传到同名请求头；未设置时为空字符串。 |

- 公共调用器提供单层 24 小时缓存，位于 `<cwd>/linkfox/.cache/linkfox-fastmoss-product-rank-top-selling/`。文件名为技能名加参数 JSON（键排序、保留中文）的 SHA-256 前 16 位，采用此路径和命名格式的有效缓存可直接复用。
- 缓存保存完整响应，包括错误和空结果。缓存命中时在对象中添加 `_cache.hit=true` 并提示命中；不自动重试失败或空结果。
- 完整响应及会话索引、元数据保存在当前工作目录的 `linkfox/` 下。业务入口在请求前检查目录可写，固定使用当前目录，不回退到 `ACPX_WORKSPACES`、家目录或临时目录；目录不可写时报错退出。在 POSIX 系统中，当前目录位于 `/tmp` 下（包括符号链接指向该目录）时同样在请求前报错。
- 不做本地依赖安装；业务查询只依赖 Python 标准库。认证环境变量和优先级见公共调用规范。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer | 业务状态码，`200` 表示成功 |
| errmsg | string | 业务状态说明 |
| page | integer | 当前页码 |
| pageSize | integer | 当前每页条数 |
| total | integer | 记录数 |
| products | array | 热销商品列表（见下方商品对象） |
| columns | array | 渲染的列 |
| type | string | 渲染的样式 |
| costTime | integer | 接口耗时（毫秒） |
| costToken | integer | 消耗 token；部分响应可能省略 |
| matchedCategoryIdPath | string | 匹配到的类目 ID 路径；传入 `category` 时可能返回 |
| matchedCategoryNamePath | string | 匹配到的类目名称路径；传入 `category` 时可能返回 |

#### products[*] 商品对象

| 字段 | 类型 | 说明 |
|------|------|------|
| title | string | 商品名称 |
| productId | string | 商品 ID |
| region | string | 区域代码 |
| price | number | 商品价格 |
| minPrice | number | 最低价格；仅价格区间商品返回 |
| maxPrice | number | 最高价格；仅价格区间商品返回 |
| currency | string | 货币符号或标识 |
| totalSaleCnt | integer | 总销量 |
| totalSale1dCnt | integer | 近1天销量（dateType=day 时返回） |
| totalSale7dCnt | integer | 近7天销量（dateType=week 时返回） |
| totalSale30dCnt | integer | 近30天销量（dateType=month 时返回） |
| totalSaleGmvAmt | number | 总销售额 |
| totalSaleGmv1dAmt | number | 近1天销售额（dateType=day 时返回） |
| totalSaleGmv7dAmt | number | 近7天销售额（dateType=week 时返回） |
| totalSaleGmv30dAmt | number | 近30天销售额（dateType=month 时返回） |
| growthRate | number | 增长率（百分比） |
| shopName | string | 店铺名称 |
| shopTotalUnitsSold | integer | 店铺总销量 |
| shopSellerId | string | 店铺卖家 ID |
| categoryName | string | 商品类目 |
| categoryIds | array | 商品类目 ID 路径（一级至三级） |
| productCommissionRate | number | 商品佣金比例（基点，1000=10%） |
| imageUrl | string | 商品图片 URL |
| coverUrl | array | 商品封面图 URL 列表 |
| shopAvatar | string | 店铺头像 URL |
| sourceTool | string | 来源工具标识 |
| sourceType | string | 商品来源类型 |
| offShelvesText | string | 是否下架（"是"=已下架，"否"=在售） |

#### 脚本附加字段

| 字段 | 类型 | 说明 |
|------|------|------|
| _cache | object | 仅本地缓存命中的对象响应可能附加；不是接口业务字段。 |
| _cache.hit | boolean | `true` 表示本次读取了有效的本地缓存。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 返回空 `products` 时如实说明该查询未取得商品，按用户目标核对市场、日期和类目；后续调用遵循 SKILL.md 的成本约束。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/fastmoss/productRankTopSelling" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"region": "US", "dateInfo": {"type": "day", "value": "2026-04-15"}, "page": 1, "pageSize": 10}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-fastmoss-product-rank-top-selling",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```