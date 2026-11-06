# 极目亚马逊商品发掘 接口说明

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

## 接口：商品发掘（productDiscovery）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/jiimore/productDiscovery`

### 请求参数

POST Body（JSON）：

#### 必填参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| keyword | string | 是 | 关键词；必填，不支持无关键词浏览。按目标站点语言翻译：US 用英语、JP 用日语、DE 用德语 |

#### 筛选参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| countryCode | string | 否 | 国家，使用国家简称。默认 `US`。可选值：`US`、`JP`、`DE` |
| priceMin | number | 否 | 最低商品价格 |
| priceMax | number | 否 | 最高商品价格 |
| totalReviewsMin | integer | 否 | 最低评论数 |
| totalReviewsMax | integer | 否 | 最高评论数 |
| customerRatingMin | number | 否 | 最低评分 |
| customerRatingMax | number | 否 | 最高评分 |
| clickConversionRateMin | number | 否 | 最低点击购买转化率，数值范围为0-1，0.1表示10% |
| clickConversionRateMax | number | 否 | 最高点击购买转化率，数值范围为0-1，0.1表示10% |
| clickConversionRateCompositeMin | number | 否 | 最低综合转化率，数值范围为0-1，0.1表示10% |
| clickConversionRateCompositeMax | number | 否 | 最高综合转化率，数值范围为0-1，0.1表示10% |
| clickCountT7Min | integer | 否 | 最低周点击量 |
| clickCountT7Max | integer | 否 | 最高周点击量 |
| clickCountT30Min | integer | 否 | 最低月点击量 |
| clickCountT30Max | integer | 否 | 最高月点击量 |
| clickCountGrowthT7Min | number | 否 | 最低周点击增长率，数值范围为0-1，0.1表示10% |
| clickCountGrowthT7Max | number | 否 | 最高周点击增长率，数值范围为0-1，0.1表示10% |
| clickCountGrowthT30Min | number | 否 | 最低月点击增长率，数值范围为0-1，0.1表示10% |
| clickCountGrowthT30Max | number | 否 | 最高月点击增长率，数值范围为0-1，0.1表示10% |
| salesVolumeT360Min | integer | 否 | 最低年销售量 |
| salesVolumeT360Max | integer | 否 | 最高年销售量 |
| grossProfitMarginMin | number | 否 | 最低毛利率；比例参数使用 0–1 小数，如 0.3 表示 30% |
| grossProfitMarginMax | number | 否 | 最高毛利率；比例参数使用 0–1 小数，如 0.3 表示 30% |
| fbaFeeMin | number | 否 | 最低FBA佣金 |
| fbaFeeMax | number | 否 | 最高FBA佣金 |
| launchDateMin | string | 否 | 最小上架时间，格式为：`yyyyMMdd000000` |
| launchDateMax | string | 否 | 最大上架时间，格式为：`yyyyMMdd000000` |
| nicheCountMin | integer | 否 | 最低细分市场数量 |
| nicheCountMax | integer | 否 | 最高细分市场数量 |
| sellerCountry | string | 否 | 卖家国家地区编码，选择多个的情况下用逗号隔开，如：`CN,US` |

#### 排序与分页

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| sortField | string | 否 | 排序字段。默认 `purchasedClicksT360`。可选值：`totalReviews`（总评论数）、`price`（价格）、`launchDate`（上架时间）、`clickCountT7`（7天点击量）、`clickCountT30`（30天点击量）、`clickCountT90`（90天点击量）、`clickConversionRate`（点击购买转化率）、`clickConversionRateComposite`（综合点击购买转化率）、`customerRating`（评分）、`purchasedClicksT360`（360天购买量）、`clickCountGrowthT7`（周点击增长率）、`clickCountGrowthT30`（月点击增长率）、`currentPrice`（当前价格）、`fbaFee`（FBA佣金）、`shippingFee`（FBA运费）、`gpm`（毛利率） |
| sortType | string | 否 | 排序方式。默认 `desc`。可选值：`desc`（降序）、`asc`（升序） |
| page | integer | 否 | 页码。默认 `1` |
| pageSize | integer | 否 | 每页数量（10-100）。默认 `50` |


#### 脚本选项与运行约定

| 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| --inline | 命令行开关 | 否 | 强制完整打印，同时保存响应。 |
| --no-cache | 命令行开关 | 否 | 跳过响应缓存的读取与写入；默认启用 24 小时缓存。 |

缓存仅由 `scripts/call_api.py` 管理，缓存键为参数排序后的 SHA-256 前 16 位，有效期为 24 小时，路径为 `<cwd>/linkfox/.cache/linkfox-jiimore-product-discovery/linkfox-jiimore-product-discovery-<hash>.json`，可复用该路径下键匹配且未过期的缓存，使用单层缓存。失败或空结果也会缓存；命中缓存时仍保存完整响应并附加 `_cache.hit`，不重复请求。缓存过期、文件损坏或未命中时才按本次显式调用请求，不自动重试或扩大检索范围。

输出以当前工作目录为准，不因 `ACPX_WORKSPACES` 改写业务数据目录；请求前检查根目录、会话元数据和实际 `data` 目录能否保存，路径被文件占用或不可写时立即报错，不回退到家目录或临时目录。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| total | integer | 总数 |
| sourceTool | string | 工具类型：`jiimore` |
| sourceType | string | 来源类型：`amazon` |
| type | string | 渲染的样式 |
| title | string | 标题 |
| costToken | integer | 消耗token |
| columns | array | 渲染的列 |
| products | array | 产品列表（详见下方） |

#### products[*] 产品对象字段

| 字段 | 类型 | 说明 |
|------|------|------|
| asin | string | 亚马逊商品ASIN |
| parentAsin | string | 亚马逊商品父ASIN |
| title | string | 产品标题 |
| brand | string | 品牌 |
| price | number | 价格 |
| imageUrl | string | 产品主图 |
| productImageUrls | array | 产品图片链接列表 |
| asinUrl | string | ASIN链接 |
| ratings | integer | 评论数 |
| availableDate | string | 上架时间（时间戳） |
| availableDateString | string | 上架日期（字符串） |
| categoryNames | array | 类目信息 |
| marketplaceId | string | 站点ID |
| clickCountT7 | integer | 周点击量 |
| clickCountT30 | integer | 月点击量 |
| clickCountT90 | integer | 季度点击量 |
| clickConversionRate | number | 点击购买转化率 |
| clickConversionRateComposite | number | 综合转化率 |
| grossProfitMargin | number | 毛利率 |
| fbaFee | number | 亚马逊佣金 |
| shippingFee | number | FBA运费 |
| sourceTool | string | 工具类型：`jiimore` |
| sourceType | string | 来源类型：`amazon` |

#### 状态与脚本本地字段

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer | 错误响应中的业务码；统一判断见下方基础规则。 |
| errmsg | string | 错误响应中的原因，如 `authorized error`。 |
| errorCode | 类型未限定 | 可能返回的业务状态字段，以实际响应为准；含义见下方业务规则，不替代公共响应判定。 |
| error | string | 脚本遇到网络错误或无法解析的 HTTP 错误时返回的本地说明。 |
| details | string | 无法解析为 JSON 的 HTTP 错误响应正文；有正文时可能返回。 |
| _cache | object | 本地缓存命中时附加的信息，不属于远端业务字段。 |
| _cache.hit | boolean | 缓存命中时为 true。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

`errorCode` 为 200 表示成功，其他值表示业务错误，未授权时可能为 401；错误响应也可能使用 `errcode`（如 `errcode: 401`、`errmsg: "authorized error"`）。保留实际返回的字段，若出现 `errorCode`，结合错误消息说明其业务含义；统一正常响应判定仍遵循公共规则。

### curl 示例

```bash
curl -X POST https://tool-gateway.linkfox.com/jiimore/productDiscovery \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
    "keyword": "wireless charger",
    "countryCode": "US",
    "clickConversionRateMin": 0.1,
    "priceMin": 10,
    "priceMax": 50,
    "sortField": "clickConversionRate",
    "sortType": "desc",
    "page": 1,
    "pageSize": 20
  }'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-jiimore-product-discovery",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
