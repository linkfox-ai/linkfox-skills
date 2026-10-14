# linkfox-1688-search-by-image

## 功能与边界

通过商品图片在1688检索外观相似或同款货源，返回商品、价格、起批量、月销量、预估销售额、复购率、交易分、服务分、商家身份、发货地和一件代发信息。适合用户有产品图片、想找同款/相似供应商或需要按视觉结果做初筛的场景。

本能力只做实时视觉货源发现，不做文字关键词主搜索、1688榜单、Amazon 以图搜图、评论分析、价格趋势、图片生成或图片编辑。结果不存分析数据库，不能用其他查询逻辑补做未支持的筛选或排序。

## MCP 调用

- **MCP server**：`LinkFox`
- **唯一工具**：`proxy_call`
- **toolName**：图片搜索为 `alibaba1688/imageSearch`；本地图片上传前置预签名为 `oss/file/presignedPut`。两者都是原 endpoint 去掉前导 `/` 后的精确值，区分大小写。
- **arguments**：直接传下方请求参数对象，不添加 `body`、`params`、`data`、`headers`、Authorization、API key 或 token；WorkBuddy 自动注入授权。
- **返回解析**：先检查 MCP/`isError`，代理成功后读取 text 或 structured content；text 为 JSON 时只解析一次，再按响应字段处理下游状态。
- **调用纪律**：禁止 HTTP 直连或 MCP 缺失时回退；同一任务内相同 `toolName + arguments` 只调用一次。失败、空结果或结果不理想时不得自动重试或改参数探测。
### 请求参数

`imageUrl`、`imageBase64`、`imageId` 至少提供一个；分页时优先使用首轮响应的 `imageId`。

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|---|---|---|
| `imageUrl` | string | 条件必填 | — | 可公开访问的图片 URL，最多1000字符，仅 png/jpg/jpeg |
| `imageBase64` | string | 条件必填 | — | 纯 Base64 内容，不含 `data:image/jpeg;base64,` 前缀，仅 png/jpg/jpeg |
| `imageId` | string | 条件必填 | — | 1688 图片 ID，分页时可加速 |
| `page` | int | 否 | 1 | 页码，从1开始 |
| `pageSize` | int | 否 | 20 | 每页1–50条 |
| `priceStart` / `priceEnd` | string | 否 | — | 人民币价格范围 |
| `filter` | string | 否 | — | 逗号分隔的预设筛选值 |
| `sort` | string | 否 | `{"monthSold":"desc"}` | JSON 对象，只支持 `price`、`monthSold`、`rePurchaseRate` 与 `asc/desc` |
| `keyword` | string | 否 | — | 在视觉结果中进一步过滤的关键词 |
| `productCollectionId` | string | 否 | — | 单个货盘 ID |

### 支持的 filter

`1688Selection`（1688严选）、`certifiedFactory`（认证工厂）、`totalEpScoreLv1/2/3/4`（综合体验分5/4/3/2星）、`qrr0`（无品质退款）、`qrr1`/`qrr5`/`qrr10`（品质退款率低于1%/5%/10%）、`shipInToday`（当日发货）、`shipIn24Hours`、`shipIn48Hours`、`noReason7DReturn`、`isOnePsale`、`isOnePsaleFreePost`、`new7`、`new30`、`isQqyx`（全球严选），以及区域专线 `JPFL`、`USFL`、`KRFL`、`VNFL`、`SAFL`、`RUFL`、`KZFL`、`HKFL`、`MOFL`、`TWFL`。多个值用逗号连接，例如 `1688Selection,totalEpScoreLv1,qrr0`。

支持的货盘 ID 为 `262105288`、`262105286`、`262105253`、`262105281`、`262105280`、`262105277`、`262105276`、`262105274`、`262105269`、`262185282`，均用于跨境货盘筛选。

### 响应字段

#### 顶层响应

| 字段路径 | 类型 | 说明 |
|---|---|---|
| imageId | string | 上传后的图片ID（分页查询时回传可加速） |
| total | integer | 本页商品数量 |
| totalPage | integer | 总页数 |
| sourceType | string | 来源类型（固定值 "1688"） |
| type | string | 渲染样式（固定值 "productWorkbenches"） |
| columns | array | 渲染列定义 |
| costToken | integer | 消耗 token |
| products | array | 商品列表（详见下方商品字段） |

#### `products[]`

| 字段路径 | 类型 | 说明 |
|---|---|---|
| products[].offerId | string | 商品ID |
| products[].asin | string | 商品编号（同 offerId） |
| products[].imageUrl | string | 商品图片 |
| products[].title | string | 商品标题 |
| products[].price | number | 批发价（元） |
| products[].consignPrice | number | 一件代发价（元） |
| products[].salesQuantity | integer | 月销售件数 |
| products[].estimatedSalesAmount | number | 预估销售额 |
| products[].asinUrl | string | 商品链接 |
| products[].isOnePsale | string | 是否一件代发（是/否） |
| products[].isJxhy | string | 是否精选货源（是/否） |
| products[].sellerIdentities | string | 商家身份（超级工厂/实力商家/诚信通会员） |
| products[].offerIdentities | string | 商品标（严选） |
| products[].repurchaseRate | string | 复购率 |
| products[].tradeScore | string | 商品交易评分 |
| products[].compositeServiceScore | string | 综合服务体验分 |
| products[].sendGoodsAddressText | string | 发货地 |
| products[].deliveryTime | string | 发货时间（24/48小时） |
| products[].quantityBegin | integer | 起批量 |
| products[].hasPromotion | string | 是否有营销活动（是/否） |
| products[].promotionType | string | 营销类型 |
| products[].isPatentProduct | string | 是否专利商品（是/否） |
| products[].isSelect | string | 跨境select货盘标识 |
| products[].currency | string | 币种（固定值 "¥"） |
| products[].sourceType | string | 来源类型（固定值 "1688"） |
| products[].sourceTool | string | 来源工具（固定值 "1688以图搜图"） |
| products[].dataType | string | 数据类型（固定值 "monthlyData"） |

#### `oss/file/presignedPut` 响应（本地图片上传前置）

| 字段路径 | 类型 | 说明 |
|---|---|---|
| errcode | integer | 业务状态码；来源上传脚本以 `200` 判断成功 |
| errmsg | string | 预签名请求失败时的业务错误消息 |
| url | string | 成功时返回的预签名 PUT URL |
### 错误处理

正常 HTTP 状态通常为200，业务成功由 `errcode=200` 判断（部分响应也可能有 `errorCode`）。`401` 表示认证失败，`402` 表示积分不足，其他非200业务值读取 `errmsg` 修正参数；HTTP 401/402 按顶层认证引导执行。错误示例：`{"errcode":401,"errmsg":"authorized error"}`。不要因空结果自动改图片、关键词、筛选或页码。

## 调用与展示规则

1. 先确认图片输入满足格式与可访问性；本地图片先调用 `oss/file/presignedPut`，再运行上传 helper，不能把本地路径直接放进 `imageUrl`。
2. 同一任务内相同参数组合不得重复调用；需要再次查询时先说明额外积分消耗并取得用户确认。
4. 结果表至少包含图片、标题、offerId、批发价、代发价、月销量、起批量、复购率、卖家身份和链接；显示 `total`、当前页/总页数，有下一页时提示用户主动请求。
5. 未支持的 filter/sort 不要尝试替代方案；缺失字段标为未知，不能推断为无或0。

### 本地图片上传

先确认用户同意上传，根据扩展名确定 `contentType`，再调用预签名 endpoint：

```json
{
  "toolName": "oss/file/presignedPut",
  "arguments": {
    "contentType": "image/png",
    "fileExtension": "png"
  }
}
```

确认下游 `errcode=200` 且存在 `url` 后执行：

```bash
python scripts/upload_image.py "C:\\images\\product.png" --presigned-url "<proxy_call 返回的 url>"
```

helper 只向预签名 OSS URL 执行 PUT，输出去掉 query 的公开 `url`；不得记录或展示预签名 query。上传失败时停止，不自动重复上传或搜索。

## 示例

完整 `proxy_call` 参数示例：

```json
{
  "toolName": "alibaba1688/imageSearch",
  "arguments": {
    "imageUrl": "https://example.com/product.jpg",
    "page": 1,
    "pageSize": 20
  }
}
```

基础查询：

```json
{"imageUrl":"https://example.com/product.jpg","page":1,"pageSize":20}
```

筛选认证工厂、24小时发货并按价格升序：

```json
{"imageUrl":"https://example.com/product.jpg","filter":"certifiedFactory,shipIn24Hours,isOnePsale","sort":"{\"price\":\"asc\"}","priceStart":"10","priceEnd":"100","page":1,"pageSize":20}
```

翻页：

```json
{"imageId":"abc123456","page":2,"pageSize":20}
```

以图搜索只返回视觉匹配结果；如果用户需要 SKU、阶梯价、件重尺或证书，取 `offerId` 后转到 `linkfox-1688-product-detail`。

## 反馈 API

用户表达赞扬、不满、建议或结果错误时，可按本子能力契约 POST `https://skill-api.linkfox.com/api/v1/public/feedback`，JSON 字段为 `skillName`（`linkfox-1688-search-by-image`）、`sentiment`（`POSITIVE`/`NEUTRAL`/`NEGATIVE`）、`category`（`BUG`/`COMPLAINT`/`SUGGESTION`/`OTHER`）和描述意图、实际结果及原因的 `content`；不要与商品网关混用 base URL。
