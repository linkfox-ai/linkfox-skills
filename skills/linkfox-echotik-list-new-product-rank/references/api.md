# EchoTik TikTok Shop 新品排行 接口说明

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

## 接口：新品排行（listNewProductRank）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/echotik/listNewProductRank`

### 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| date | string | 是 | 查询日期，格式为 `YYYY-MM-DD`；必填，无默认日期 |
| region | string | 否 | 区域，默认 `US`。可选值：US（美国）、ID（印度尼西亚）、TH（泰国）、PH（菲律宾）、MY（马来西亚）、VN（越南）、GB（英国）、MX（墨西哥）、SG（新加坡）、SA（沙特阿拉伯）、BR（巴西）、ES（西班牙）、JP（日本）、DE（德国）、IT（意大利）、FR（法国） |
| pageNum | integer | 否 | 分页页码，从 1 开始，默认 `1` |
| pageSize | integer | 否 | 每页商品数，默认 `50`；最大值未明确 |

#### 参数约定与使用限制

- 提供每日快照，不提供周或月粒度榜单，也不用于跨多月的历史趋势分析。
- 结果分页返回，单次查询不保证返回全部商品；通过 `pageNum` 和 `pageSize` 查看指定范围。

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| JSON 参数 | JSON object | 是 | 第一个位置参数；字段与上方请求参数一致 |
| --inline | CLI flag | 否 | 强制全量打印到标准输出，同时保存完整响应 |
| --no-cache | CLI flag | 否 | 禁用响应缓存读取和写入；默认启用 24 小时本地缓存 |

缓存目录为 `<cwd>/linkfox/.cache/linkfox-echotik-list-new-product-rank/`，缓存键为参数排序后计算的 SHA-256 前 16 位，仅使用这一层缓存。失败和空结果也会缓存；命中缓存会标记 `_cache.hit=true`。只有明确需要重新请求时才使用 `--no-cache`，并遵守成本约束。

认证优先读取 `LINKFOX_AGENT_API_KEY`，为空时读取 `LINKFOXAGENT_API_KEY`；`LINKFOX_TOOL_GATEWAY` 可覆盖网关地址。请求携带 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 追踪头。完整响应按 `SESSION_ID` 聚合并登记会话元数据；业务入口固定在当前工作目录保存，不回退到家目录或临时目录，当前目录不可写时在请求前报错。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 业务状态码，按公共规则判断；`401` 表示未授权 |
| errmsg | string | 业务消息或具体错误原因 |
| errorCode | 未明确 | 字段类型及是否独立返回尚未确认。值 `200` 表示成功、`401` 表示未授权；仅在实际响应中出现时保留，响应判断遵循公共规则，不据此另定成功条件 |
| total | integer | 记录数 |
| products | array | 最新商品列表（见下方商品对象） |
| columns | array | 渲染的列 |
| type | string | 渲染的样式 |
| costToken | integer | 消耗的 Token 数量 |

#### products[*] 商品对象

| 字段 | 类型 | 说明 |
|------|------|------|
| title | string | 商品名称 |
| asin | string | 商品ID |
| region | string | 区域代码 |
| price | number | SPU平均价格 |
| minPrice | number | 最低价格 |
| maxPrice | number | 最高价格 |
| currency | string | 货币 |
| totalSaleCnt | integer | 总销量 |
| totalSale30dCnt | integer | 近30天销量 |
| totalSaleGmvAmt | number | 总销售额 |
| totalSaleGmv30dAmt | number | 近30天销售额 |
| salesTrendFlagText | string | 销售趋势标识，0=平稳 1=上升 2=下降 |
| totalVideoCnt | integer | 视频总数 |
| totalLiveCnt | integer | 直播总数 |
| totalIflCnt | integer | 总达人数 |
| productCommissionRate | number | 商品佣金比例 |
| productRating | number | 商品评分 |
| reviewCount | integer | 评论数量 |
| availableDate | string (date) | 首次爬取日期 |
| categoryId | string | 商品分类ID |
| imageUrl | string | 商品图片 |
| productImageUrls | array | 商品图片URL列表 |
| sourceTool | string | 来源工具 |
| sourceType | string | 商品来源 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/echotik/listNewProductRank" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"date": "2025-06-15", "region": "US", "pageNum": 1, "pageSize": 50}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-echotik-list-new-product-rank",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```