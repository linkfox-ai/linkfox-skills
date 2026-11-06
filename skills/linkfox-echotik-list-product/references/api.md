# EchoTik TikTok 商品搜索 接口说明

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

## 接口：TikTok 商品搜索

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/echotik/listProduct`

### 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| keyword | string | 否 | 商品关键词（请翻译为当地语言）。最大长度 1000 |
| region | string | 否 | 区域，默认 `US`。可选值：US（美国）、ID（印度尼西亚）、TH（泰国）、PH（菲律宾）、MY（马来西亚）、VN（越南）、GB（英国）、MX（墨西哥）、SG（新加坡）、SA（沙特阿拉伯）、BR（巴西）、ES（西班牙）、JP（日本）、DE（德国）、IT（意大利）、FR（法国） |
| categoryKeywordCN | string | 否 | 商品分类（请输入中文）。最大长度 1000 |
| minTotalSaleCnt | integer | 否 | 总销量（最小值） |
| maxTotalSaleCnt | integer | 否 | 总销量（最大值） |
| minTotalSale30dCnt | integer | 否 | 30天销量（最小值） |
| maxTotalSale30dCnt | integer | 否 | 30天销量（最大值） |
| minTotalSaleGmvAmt | string | 否 | 商品交易总额（最小值）。最大长度 1000 |
| maxTotalSaleGmvAmt | string | 否 | 商品交易总额（最大值）。最大长度 1000 |
| minTotalSaleGmv30dAmt | string | 否 | 商品交易总额（30天）（最小值）。最大长度 1000 |
| maxTotalSaleGmv30dAmt | string | 否 | 商品交易总额（30天）（最大值）。最大长度 1000 |
| minSpuAvgPrice | number | 否 | SPU平均价格（最小值） |
| maxSpuAvgPrice | number | 否 | SPU平均价格（最大值） |
| minProductRating | number | 否 | 商品评分（最小值） |
| maxProductRating | number | 否 | 商品评分（最大值） |
| minReviewCount | integer | 否 | 商品评价数（最小值） |
| maxReviewCount | integer | 否 | 商品评价数（最大值） |
| minProductCommissionRate | number | 否 | 商品佣金比例（最小值），输入值为百分比时自动转成小数，例如：5%->0.05 |
| maxProductCommissionRate | number | 否 | 商品佣金比例（最大值），输入值为百分比时自动转成小数，例如：5%->0.05 |
| minTotalIflCnt | integer | 否 | 带货达人数（最小值） |
| maxTotalIflCnt | integer | 否 | 带货达人数（最大值） |
| minTotalVideoCnt | integer | 否 | 带货视频数（最小值） |
| maxTotalVideoCnt | integer | 否 | 带货视频数（最大值） |
| minTotalViewsCnt | integer | 否 | 带货播放数（最小值） |
| maxTotalViewsCnt | integer | 否 | 带货播放数（最大值） |
| minFirstCrawlDt | integer | 否 | 商品上架时间（最小值），格式 YYYYMMDD（例如：20200101 代表 2020-01-01） |
| maxFirstCrawlDt | integer | 否 | 商品上架时间（最大值），格式 YYYYMMDD |
| saleDays | integer | 否 | 商品上架销售天数，单位是天 |
| productSortField | integer | 否 | 排序字段：1=总销量、2=商品交易总额、3=SPU平均价格、4=7天销量、5=30天销量、6=7天商品交易额、7=30天商品交易额。默认 `1` |
| sortType | integer | 否 | 排序方式：0=升序（asc）、1=降序（desc）。默认 `1` |
| pageNum | integer | 否 | 分页页码。默认 `1` |
| pageSize | integer | 否 | 每页条数。默认 `50` |

#### 参数整理与使用限制

- 用户未指定市场时使用 `US`；关键词应翻译为目标市场当地语言，`categoryKeywordCN` 必须使用中文。
- 佣金入参为小数。用户给出百分比时，在调用前换算，例如 `5%` 转为 `0.05`；脚本透传 JSON 数值，不会把百分比字符串自动转换为数字。
- 上架日期使用整数 `YYYYMMDD`，例如 `20240101` 表示 2024-01-01；`saleDays` 的单位为天。
- 同一会话、同一参数默认只查询一次。失败或空结果时不得自动换词、翻页或更改邮编连续试探；后续检索前说明额外算力消耗。

#### 脚本选项与缓存约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| JSON 参数 | object | 是 | CLI 的首个参数，以 JSON 对象传入上方筛选条件。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 跳过缓存读取与写入；不删除已有缓存，调用可能产生额外费用。 |

脚本提供 24 小时本地缓存：使用排序后的完整 JSON 参数计算 SHA-256 前 16 位，文件位于 `<cwd>/linkfox/.cache/linkfox-echotik-list-product/linkfox-echotik-list-product-<hash>.json`。相同参数可命中有效缓存，键顺序不影响命中；缓存未按账号或市场默认值归一化。返回的错误或空结果也会被缓存，不能把缓存结果误认为一次新查询。业务入口仅使用公共调用器的一层缓存。每次执行（包括缓存命中）仍保存完整响应；命中时响应增加 `_cache.hit=true` 并输出提示。

原始数据保存在当前工作目录，使用 `SESSION_ID` 聚合任务；未设置时自动生成进程内稳定的会话标识。请求前检查当前目录及实际会话 `data` 目录的可写性；路径被文件占用或不可写时直接报错，不回退到家目录或临时目录，不写入 `/tmp`。目录约束由业务入口 `scripts/echotik_list_product.py` 实现。

#### 环境变量兼容

| 环境变量 | 类型 | 必填 | 说明 |
|------|------|------|------|
| LINKFOX_AGENT_API_KEY | string | 二选一 | 优先使用的认证密钥，以原值写入 `Authorization`。 |
| LINKFOXAGENT_API_KEY | string | 二选一 | 兼容变量名；优先变量为空时使用。 |
| LINKFOX_TOOL_GATEWAY | string | 否 | 网关基础地址，默认 `https://tool-gateway.linkfox.com`；移除末尾 `/` 后拼接接口路径。 |
| SESSION_ID | string | 否 | 透传同名请求头，并用于会话数据聚合；未设置时请求头为空，会话目录自动生成标识。 |
| MESSAGE_ID | string | 否 | 透传同名请求头，未设置时为空字符串。 |
| MODE_ID | string | 否 | 透传同名请求头，未设置时为空字符串。 |
| APP_NAME | string | 否 | 透传同名请求头，未设置时为空字符串。 |

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 网关状态码，按公共规则判断；认证错误示例为 401。 |
| errmsg | string | 网关消息；认证错误示例为 authorized error。 |
| errorCode | 以实际返回为准 | 业务状态字段；认证错误示例使用 errcode。若出现，保留原值用于诊断，不替代公共响应规则。 |
| total | integer | 记录数 |
| products | array | 产品信息列表（详见下方） |
| columns | array | 渲染的列 |
| type | string | 渲染的样式 |
| costToken | integer | 消耗token |

#### products[*] 产品对象字段

| 字段 | 类型 | 说明 |
|------|------|------|
| productId | string | 商品唯一标识ID |
| productName | string | 商品名称 |
| title | string | 商品名称 |
| imageUrl | string | 商品图片URL |
| coverUrl | string | 封面图URL列表 |
| productImageUrls | array | 商品图片URL列表 |
| categoryName | string | 商品品类名称 |
| categoryIds | array | 商品品类ID列表 |
| region | string | 区域代码 |
| currency | string | 货币 |
| price | number | 商品价格 |
| minPrice | number | 最低价格 |
| maxPrice | number | 最高价格 |
| spuAvgPrice | number | SPU平均价格 |
| productRating | number | 商品评分 |
| reviewCount | integer | 评论数量 |
| ratings | integer | 评论数 |
| productCommissionRate | number | 商品佣金比例 |
| totalSaleCnt | integer | 总销量 |
| totalSale1dCnt | integer | 1天内总销量 |
| totalSale7dCnt | integer | 7天内总销量 |
| totalSale15dCnt | integer | 15天内总销量 |
| totalSale30dCnt | integer | 30天内总销量 |
| totalSale60dCnt | integer | 60天内总销量 |
| totalSale90dCnt | integer | 90天内总销量 |
| monthlySalesUnits | integer | 月销量 |
| totalSaleGmvAmt | number | 总销售额 |
| totalSaleGmv1dAmt | number | 1天内总销售额 |
| totalSaleGmv7dAmt | number | 7天内总销售额 |
| totalSaleGmv15dAmt | number | 15天内总销售额 |
| totalSaleGmv30dAmt | number | 30天内总销售额 |
| totalSaleGmv60dAmt | number | 60天内总销售额 |
| totalSaleGmv90dAmt | number | 90天内总销售额 |
| firstCrawlDt | integer | 上架日期，格式 YYYYMMDD（例如 20240101 表示 2024-01-01） |
| availableDate | string | 上架时间(时间戳) |
| discount | string | 折扣信息 |
| freeShippingText | string | 是否包邮 |
| offMarkText | string | 是否有优惠标记 |
| salesFlagText | string | 带货方式 |
| salesTrendFlagText | string | 销售趋势标记 |
| isSShopText | string | 是否S店 |
| salePropsInfo | array | 销售属性信息（商品规格） |
| sourceTool | string | 来源工具 |
| sourceType | string | 商品来源 |
| asin | string | 产品ID |

`columns`、`salePropsInfo` 等数组元素的内部结构以实际返回为准，保留返回内容，不补造嵌套字段。支持按达人、视频和播放量筛选商品；这些展示指标的响应字段名以实际返回为准，仅展示可识别的指标。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 商品列表为空时说明当前筛选未找到商品，不自动更换条件重试；保留响应以便用户决定后续检索。

### 响应示例

认证错误示例：

```json
{"errcode": 401, "errmsg": "authorized error"}
```

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/echotik/listProduct" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
    "keyword": "phone case",
    "region": "US",
    "minTotalSale30dCnt": 1000,
    "productSortField": 5,
    "sortType": 1,
    "pageSize": 20
  }'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-echotik-list-product",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
