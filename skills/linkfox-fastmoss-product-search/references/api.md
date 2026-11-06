# FastMoss TikTok 商品搜索 接口说明

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

## 接口：商品搜索

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/fastmoss/productSearch`

### 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| keyword | string | 否 | 搜索关键词（商品标题模糊匹配） |
| region | string | 否 | 市场区域代码。可选值：US（美国）、GB（英国）、MX（墨西哥）、ES（西班牙）、DE（德国）、IT（意大利）、FR（法国）、ID（印度尼西亚）、VN（越南）、MY（马来西亚）、TH（泰国）、PH（菲律宾）、BR（巴西）、JP（日本）、SG（新加坡） |
| category | string | 否 | 英文类目名称，系统自动匹配TikTok类目ID。非英文需先翻译为英文 |
| shopType | integer | 否 | 店铺类型：1=本地店铺，2=跨境店铺 |
| isTopSelling | boolean | 否 | 仅筛选热销商品 |
| isNewListed | boolean | 否 | 仅筛选新上架商品 |
| isSshop | boolean | 否 | 仅筛选TikTok全托管（S-shop）商品 |
| isFreeShipping | boolean | 否 | 仅筛选包邮商品 |
| isLocalWarehouse | boolean | 否 | 仅筛选本地仓发货商品 |
| unitsSoldRange | object | 否 | 销量范围筛选，格式：`{"min": 100, "max": 5000}` |
| commissionRateRange | object | 否 | 佣金率范围筛选，格式：`{"min": 0.05, "max": 0.20}`（小数，0.10=10%） |
| creatorCountRange | object | 否 | 带货达人数范围筛选，格式：`{"min": 10, "max": 500}` |
| orderField | string | 否 | 排序字段：day7_units_sold（7天销量）、day7_gmv（7天GMV）、commission_rate（佣金率）、total_units_sold（总销量）、total_gmv（总GMV）、creator_count（达人数）。默认降序排列 |
| page | integer | 否 | 页码，默认 1 |
| pageSize | integer | 否 | 每页条数，最大 10，默认 10 |

#### 范围对象字段

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| unitsSoldRange.min | integer | 否 | 销量下限；范围对象使用 min / max。 |
| unitsSoldRange.max | integer | 否 | 销量上限。 |
| commissionRateRange.min | number | 否 | 佣金率下限，使用小数，例如 0.10 表示 10%。 |
| commissionRateRange.max | number | 否 | 佣金率上限，使用小数。 |
| creatorCountRange.min | integer | 否 | 带货达人数下限。 |
| creatorCountRange.max | integer | 否 | 带货达人数上限。 |

#### 参数与使用限制

- 所有请求字段均可选；为取得有意义的结果，建议至少提供 keyword 或 category。
- 范围筛选使用对象，不能替换为数组或拼接字符串；可以只传 min，如下方 curl 示例。

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| JSON 参数 | object | 是 | CLI 的首个位置参数，内容为上述请求对象。 |
| --inline | CLI flag | 否 | 强制完整打印，仍保存完整响应。 |
| --no-cache | CLI flag | 否 | 禁用本次缓存读取与写入；默认使用 24 小时缓存。 |

脚本为 `scripts/fastmoss_product_search.py`。缓存位于 `<cwd>/linkfox/.cache/linkfox-fastmoss-product-search/`，缓存键使用按参数名排序的 JSON 计算 SHA-256，取前 16 位；文件名为 `linkfox-fastmoss-product-search-<缓存键>.json`，TTL 为 24 小时，仅由公共调用器维护这一层响应缓存。有效缓存命中时添加 `_cache.hit=true`，不另发请求；过期或无法解析的缓存重新获取。缓存也会保存失败或空结果，重复参数先复用结果，不自动重试。缓存文件写入失败会被忽略；读取已有缓存不需要写入缓存文件。即使指定 `--no-cache`，脚本仍会确保缓存目录存在；目录不存在且无法创建时会报错。

网关优先使用 `LINKFOX_TOOL_GATEWAY`，默认 `https://tool-gateway.linkfox.com`；密钥优先使用 `LINKFOX_AGENT_API_KEY`，兼容 `LINKFOXAGENT_API_KEY`。请求携带 SESSION_ID、MESSAGE_ID、MODE_ID、APP_NAME 请求头。

完整响应及会话元数据仅落在当前工作目录的 `linkfox/` 下，按 SESSION_ID 聚合；缺省会话标识由时间与随机后缀生成。业务封装在请求前检查会话数据目录的可写性，不回退到 ACPX_WORKSPACES、家目录或临时目录。写入 UTF-8，按 UTF-8 字节数选择全量输出或摘要。

### 响应结构

#### 顶层字段

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 可选业务状态码；认证错误示例为 401，判定遵循公共规则。 |
| errmsg | string | 可选业务消息；认证错误示例为 authorized error。 |
| errorCode | 未明确 | 业务状态码（若返回）；200 表示成功，其他值表示业务错误。类型以实际响应为准，不替代基于 HTTP 状态码和 errcode 的公共响应判断。 |
| total | integer | 符合条件的总记录数 |
| products | array | 商品信息列表（详见下方） |
| columns | array | 渲染列定义 |
| type | string | 渲染样式类型 |
| costToken | integer | 消耗 token 数 |

#### 商品对象字段（products 数组）

| 字段 | 类型 | 说明 |
|------|------|------|
| title | string | 商品标题 |
| productId | string | 商品唯一标识ID |
| region | string | 市场区域代码 |
| price | number | 商品价格 |
| minPrice | number | 最低价格 |
| maxPrice | number | 最高价格 |
| currency | string | 货币代码 |
| totalSaleCnt | integer | 累计总销量 |
| totalSale1dCnt | integer | 1天销量 |
| totalSale7dCnt | integer | 7天销量 |
| totalSale28dCnt | integer | 28天销量 |
| totalSale90dCnt | integer | 90天销量 |
| totalSaleGmvAmt | number | 累计总GMV |
| totalSaleGmv7dAmt | number | 7天GMV |
| totalSaleGmv28dAmt | number | 28天GMV |
| totalVideoCnt | integer | 带货视频数 |
| totalLiveCnt | integer | 直播带货数 |
| totalIflCnt | integer | 带货达人数 |
| productCommissionRate | number | 商品佣金比例（小数，0.10=10%） |
| productRating | number | 商品评分 |
| reviewCount | integer | 评论数量 |
| skuCount | integer | SKU数量 |
| shopName | string | 店铺名称 |
| shopSellerId | string | 卖家ID |
| shopTotalUnitsSold | integer | 店铺总销量 |
| isCrossBorder | integer | 是否跨境：1=跨境，0=本地 |
| isSShopText | string | 是否全托管店铺（是/否） |
| freeShippingText | string | 是否包邮（是/否） |
| availableDate | string | 上架时间 |
| categoryName | string | 商品品类名称 |
| salesTrendFlagText | string | 销售趋势标记 |
| tiktokUrl | string | TikTok商品链接 |
| fastmossUrl | string | FastMoss商品详情链接 |
| imageUrl | string | 商品图片URL |

#### 本地缓存标记

| 字段 | 类型 | 说明 |
|------|------|------|
| _cache | object | 本地缓存命中时由脚本添加，不属于服务端商品字段。 |
| _cache.hit | boolean | true 表示此次响应来自本地缓存。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- `errmsg=authorized error` 表示认证异常，按 `onboarding.md` 处理；保留实际返回的错误原因，不自动换条件重试。
- 正常响应中的 `products` 为空时，展示本次无匹配商品；参数调整和后续检索遵循成本约束。

### 响应示例

认证错误示例：

```json
{"errcode": 401, "errmsg": "authorized error"}
```

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/fastmoss/productSearch" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
    "keyword": "beauty",
    "region": "US",
    "commissionRateRange": {"min": 0.10},
    "creatorCountRange": {"min": 50},
    "orderField": "commission_rate",
    "pageSize": 10
  }'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-fastmoss-product-search",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
