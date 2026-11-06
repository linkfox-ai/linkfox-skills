# EchoTik TikTok 店铺商品列表 接口说明

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

## 接口：店铺商品列表（listSellerProduct）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/echotik/listSellerProduct`

### 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| sellerId | string | 是 | - | 店铺ID（TikTok Shop 小店ID）。最大长度 1000。从「EchoTik TikTok 店铺搜索」或「EchoTik TikTok 店铺详情」技能的返回结果获取 |
| sellerProductSortField | integer | 否 | 1 | 列表排序字段：1=总销量(total_sale_cnt)、2=总销售额(total_sale_gmv_amt)、3=SPU平均价格(spu_avg_price)、4=7天销量(total_sale_7d_cnt)、5=7天销售额(total_sale_gmv_7d_amt) |
| sortType | integer | 否 | 1 | 排序顺序：0=升序(asc)、1=降序(desc) |
| pageSize | integer | 否 | 50 | 每页条数。**须为10的倍数，最大100**；非法值可能被拒绝或调整。上游单页最多10条，由服务端按每页10条多次拉取后合并，例如50最多返回50条；业务脚本不自行增加这层分页请求 |
| pageNum | integer | 否 | 1 | 分页页码，从1开始 |

#### 使用限制

- 仅查询一个店铺；店铺所在站点由卖家信息推断。不接受关键词、地区或类目过滤参数。
- `sellerId` 必须是已确认的店铺 ID，不是店铺名称或链接。
- 数据来自实时查询，不存入可供后续查询的数据库，不提供服务端二次 SQL 或数据加工功能；脚本保存的原始 JSON 可用于本地按需提取字段。

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|------|------|
| JSON 参数 | JSON object | 是 | 无 | 位置参数，按上表传递请求内容。 |
| --inline | CLI flag | 否 | 关闭 | 强制完整打印响应，同时仍保存完整文件。 |
| --no-cache | CLI flag | 否 | 关闭 | 跳过本地缓存读取和写入；不删除已有缓存。 |

脚本入口为 `python scripts/echotik_list_seller_product.py '<JSON 参数>' [--inline] [--no-cache]`。由 `call_api.run` 统一调用接口、缓存与输出；只有一层响应缓存。

默认缓存有效期为 24 小时，目录为 `<cwd>/linkfox/.cache/linkfox-echotik-list-seller-product/`。缓存键为请求 JSON 排序序列化后的 SHA-256 前 16 位；有效期内的缓存可复用，命中时包含 `_cache.hit=true`。启用缓存时，空结果和错误响应也会写入缓存，不自动重试或换参。

认证优先读取 `LINKFOX_AGENT_API_KEY`，回退 `LINKFOXAGENT_API_KEY`；网关采用 `LINKFOX_TOOL_GATEWAY` 或公共规则默认地址。请求保留 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 上下文头。

业务入口在调用前确认当前工作目录可写，完整数据及会话元数据只写入 `<cwd>/linkfox/`，不回退 `ACPX_WORKSPACES`、家目录或临时目录；禁止写入 `/tmp`。具体输出形式见 `SKILL.md` 的输出策略。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer | 业务状态码，200 表示成功；判断方式见响应码基础规则 |
| errmsg | string | 业务状态描述 |
| total | integer | 记录数 |
| products | array | 店铺商品列表（详见下方商品字段） |
| columns | array | 渲染的列 |
| type | string | 渲染的样式 |
| costToken | integer | 消耗token |

#### products[*] 商品对象字段

| 字段 | 类型 | 说明 |
|------|------|------|
| productId | string | 商品唯一标识ID |
| asin | string | 产品ID（同 productId） |
| title / productName | string | 商品名称 |
| imageUrl | string | 商品图片URL |
| coverUrl | string | 封面图URL |
| productImageUrls | array | 商品图片URL列表 |
| price | number | 商品价格 |
| spuAvgPrice | number | SPU平均价格 |
| minPrice | number | 最低价格 |
| maxPrice | number | 最高价格 |
| currency | string | 货币 |
| totalSaleCnt | integer | 总销量 |
| totalSale1dCnt | integer | 1天内总销量(增量) |
| totalSale7dCnt | integer | 7天内总销量(增量) |
| totalSale15dCnt | integer | 15天内总销量(增量) |
| totalSale30dCnt | integer | 30天内总销量(增量) |
| totalSale60dCnt | integer | 60天内总销量(增量) |
| totalSale90dCnt | integer | 90天内总销量(增量) |
| monthlySalesUnits | integer | 月销量 |
| totalSaleGmvAmt | number | 总销售额 |
| totalSaleGmv1dAmt | number | 1天内总销售额(增量) |
| totalSaleGmv7dAmt | number | 7天内总销售额(增量) |
| totalSaleGmv15dAmt | number | 15天内总销售额(增量) |
| totalSaleGmv30dAmt | number | 30天内总销售额(增量) |
| totalSaleGmv60dAmt | number | 60天内总销售额(增量) |
| totalSaleGmv90dAmt | number | 90天内总销售额(增量) |
| productRating | number | 商品评分 |
| ratings | integer | 评论数 |
| reviewCount | integer | 评论数量 |
| productCommissionRate | number | 商品佣金比例（小数，如 0.05 表示 5%） |
| categoryName | string | 商品品类名称 |
| categoryIds | array | 商品品类ID列表 |
| salesFlagText | string | 带货方式 |
| salesTrendFlagText | string | 销售趋势标记 |
| firstCrawlDt | integer | 上架日期（yyyyMMdd 格式，如 20240504） |
| availableDate | string | 上架时间(时间戳/日期) |
| discount | string | 折扣信息 |
| offMarkText | string | 是否有优惠标记 |
| freeShippingText | string | 是否包邮 |
| isSShopText | string | 是否S店 |
| salePropsInfo | array | 销售属性信息（含 propId/propName/salePropValues[propValueId/propValue/image]） |
| region | string | 区域代码 |
| sourceTool | string | 来源工具 |
| sourceType | string | 商品来源 |

#### salePropsInfo[*] 销售属性嵌套结构

以下为销售属性的嵌套字段与层级。标量类型和必填性未限定，按实际返回值读取；不为缺失值编造默认值。

| 字段 | 类型 | 说明 |
|------|------|------|
| propId | 未限定 | 销售属性 ID。 |
| propName | 未限定 | 销售属性名称。 |
| salePropValues | array | 该属性的可选值列表。 |
| salePropValues[*].propValueId | 未限定 | 属性值 ID。 |
| salePropValues[*].propValue | 未限定 | 属性值。 |
| salePropValues[*].image | 未限定 | 属性值对应图片。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

| errcode | 含义 | 处理建议 |
|---------|------|----------|
| 400 | 参数校验错误 | 如 `sellerId` 为空或 `pageSize` 不是 10 的倍数，依据 `errmsg` 核对字段与合法值；不自动换参试探。 |

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/echotik/listSellerProduct" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"sellerId":"7495514739648989419","sellerProductSortField":1,"sortType":1,"pageSize":20,"pageNum":1}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-echotik-list-seller-product",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
