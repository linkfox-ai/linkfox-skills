# linkfox-1688-product-detail

## 功能与边界

根据一个已知的1688 `offerId` 查询结构化商品详情，用于核对商品标题、属性、媒体、SKU、价格、库存、MOQ、代发、混批、物流包装、供应商指标、发票和证书。标准 URL `https://detail.1688.com/offer/<数字>.html` 先提取数字段作为 `offerId`。

这是详情核验，不是关键词或图片发现；一次只接受一个 `offerId`。不创建订单、不授权账户、不支付、不追踪物流、不开发票，也不提供价格历史、评论分析或数据库二次查询。数据是实时商品事实，可能在查询后变化。

## MCP 调用

- **MCP server**：`LinkFox`
- **唯一工具**：`proxy_call`
- **toolName**：`alibaba1688/productDetail`，即原 endpoint 去掉前导 `/` 后的精确值，区分大小写。
- **arguments**：直接传下方请求参数对象，不添加 `body`、`params`、`data`、`headers`、Authorization、API key 或 token；WorkBuddy 自动注入授权。
- **返回解析**：先检查 MCP/`isError`，代理成功后读取 text 或 structured content；text 为 JSON 时只解析一次，再按响应字段处理下游状态。
- **调用纪律**：禁止 HTTP 直连或 MCP 缺失时回退；同一任务内相同 `toolName + arguments` 只调用一次。失败、空结果或结果不理想时不得自动重试或改参数探测。
### 请求参数

只传1688业务参数，不传平台注入的 `uid`、`chatId`、`requestId`、`groupId`、`stepId`、`messageId`、`memberId`、`userInput` 等字段。

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|---|---|---|
| `offerId` | string | 是 | — | 正整数的1688商品 ID；必须用字符串避免大数精度丢失，最多1000字符 |
| `currency` | string | 否 | 1688默认币种 | 三位英文字母币种，如 `USD`、`HKD`，服务端转大写，最多3字符 |
| `country` | string | 否 | `en` | 上游兼容字段；通常省略，不作为额外用户能力 |

最小请求：`{"offerId":"1040473674152"}`。请求美元字段：`{"offerId":"1040473674152","currency":"USD"}`。

### 响应字段

#### 顶层响应

| 字段路径 | 类型 | 说明 |
|---|---|---|
| errcode | integer | 网关业务状态；`200` 表示成功 |
| errmsg | string | 网关消息；成功为 `ok` |
| offerId | string | 1688 商品 ID |
| subject | string | 中文标题 |
| subjectTrans | string | 上游扩展标题字段，可能为空或与 `subject` 相同 |
| description | string | 中文商品详情，常含 HTML |
| descriptionTrans | string | 上游扩展详情字段，可能缺失 |
| categoryId | string | 当前类目 ID |
| topCategoryId | string | 一级类目 ID |
| secondCategoryId | string | 二级类目 ID |
| thirdCategoryId | string | 三级类目 ID |
| categoryName | string | 类目名称，可能缺失 |
| status | string | 商品状态 |
| createDate | string | 商品创建时间 |
| productUrl | string | 1688 商品推广链接 |
| sourceType | string | 数据来源，当前为 `1688` |
| type | string | 结果样式，当前为 `productDetail` |
| sourceTool | string | 内部来源标签；面向用户展示时无需输出 |
| costToken | integer | 调用消耗 token；当前成功响应为 `1000` |
| productImage | object | 原始图片：`images[]`、`whiteImage` |
| productImageTrans | object | 上游扩展图片字段，结构同上，可能缺失 |
| mainVideo | string | 主视频地址 |
| detailVideo | string | 详情视频地址 |
| productAttributes | array | 商品属性：`attributeId`、`attributeName`、`attributeNameTrans`、`value`、`valueTrans` |
| sellingPoints | array | 商品卖点，可能为空 |
| skuList | array | SKU、规格、库存、价格与 SKU 图片，详见下节 |
| saleInfo | object | 库存、阶梯价、单位和分销销售信息，详见下节 |
| shippingInfo | object | 发货地、时效与商品/SKU 件重尺，详见下节 |
| companyName | string | 供应商/店铺名称 |
| sellerOpenId | string | 商家加密 ID |
| sellerDataInfo | object | 卖家服务与交易指标，详见下节 |
| sellerMixSetting | object | 混批设置：`generalHunpi`、`mixAmount`、`mixNumber` |
| channelPrice | object | 渠道 SKU 价格：`skuPrices[].skuId/currentPrice` |
| promotion | object | 营销信息：`hasPromotion`、`promotionType` |
| minOrderQuantity | integer | 最小起批量 |
| batchNumber | integer | 一手数量 |
| productCargoNumber | string | 商品货号 |
| soldOut | string | 商品销量 |
| isJxhy | boolean | 是否精选货源 |
| isSelect | boolean | 是否跨境 Select 货盘 |
| tradeScore | string | 商品交易评分 |
| offerIdentities | array | 商品或商家身份标识 |
| tags | array | 服务标签：`key`、`value` |
| certificates | array | 证书：`certificateName`、`certificateCode`、`certificatePhotoList[]` |
| invoiceInfo | object | 发票：`supportOnlineInvoice`、`supportFastInvoice`、`invoiceTypes[]`、`taxpayerType` |

#### 顶层对象与数组的嵌套字段

| 字段路径 | 类型 | 说明 |
|---|---|---|
| productImage.images[] | 来源未说明 | 原始图片中的 `images[]` |
| productImage.whiteImage | 来源未说明 | 原始图片中的 `whiteImage` |
| productImageTrans.images[] | 来源未说明 | 上游扩展图片字段中的 `images[]` |
| productImageTrans.whiteImage | 来源未说明 | 上游扩展图片字段中的 `whiteImage` |
| productAttributes[].attributeId | 来源未说明 | 商品属性字段 |
| productAttributes[].attributeName | 来源未说明 | 商品属性字段 |
| productAttributes[].attributeNameTrans | 来源未说明 | 商品属性字段 |
| productAttributes[].value | 来源未说明 | 商品属性字段 |
| productAttributes[].valueTrans | 来源未说明 | 商品属性字段 |
| sellerMixSetting.generalHunpi | 来源未说明 | 混批设置字段 |
| sellerMixSetting.mixAmount | 来源未说明 | 混批设置字段 |
| sellerMixSetting.mixNumber | 来源未说明 | 混批设置字段 |
| channelPrice.skuPrices | array | 渠道 SKU 价格列表 |
| channelPrice.skuPrices[].skuId | 来源未说明 | 渠道 SKU ID |
| channelPrice.skuPrices[].currentPrice | 来源未说明 | 渠道 SKU 当前价格 |
| promotion.hasPromotion | 来源未说明 | 营销信息字段 |
| promotion.promotionType | 来源未说明 | 营销信息字段 |
| tags[].key | 来源未说明 | 服务标签字段 |
| tags[].value | 来源未说明 | 服务标签字段 |
| certificates[].certificateName | 来源未说明 | 证书名称 |
| certificates[].certificateCode | 来源未说明 | 证书编码 |
| certificates[].certificatePhotoList | array | 证书图片列表 |
| certificates[].certificatePhotoList[] | 来源未说明 | 证书图片 |
| invoiceInfo.supportOnlineInvoice | 来源未说明 | 发票字段 |
| invoiceInfo.supportFastInvoice | 来源未说明 | 发票字段 |
| invoiceInfo.invoiceTypes | array | 发票类型列表 |
| invoiceInfo.invoiceTypes[] | 来源未说明 | 发票类型 |
| invoiceInfo.taxpayerType | 来源未说明 | 纳税人类型 |

#### `skuList[]`

| 字段路径 | 类型 | 说明 |
|---|---|---|
| skuList[].skuId | string | SKU ID |
| skuList[].specId | string | 规格 ID |
| skuList[].cargoNumber | string | SKU 货号 |
| skuList[].amountOnSale | integer | 可售库存 |
| skuList[].price | string | SKU 价格（人民币）；新零售价模型中是采购数量大于等于 2 件的批发价，旧商品模型语义结合阶梯和订单预览判断 |
| skuList[].retailPrice | string | SKU 零售价（人民币），适用于采购数量 1 件；上游无零售价时缺失 |
| skuList[].foreignCurrencyRetailPrice | number | SKU 外币零售价，适用于采购数量 1 件；未请求币种、无零售价或换算失败时缺失 |
| skuList[].promotionPrice | string | 营销价 |
| skuList[].consignPrice | string | 一件代发价格；上游废弃兼容字段，可能缺失 |
| skuList[].jxhyPrice | string | 精选货源兼容价格字段，可能缺失 |
| skuList[].pfJxhyPrice | string | 精选货源兼容价格字段，可能缺失 |
| skuList[].skuImageUrl | string | SKU 图片及上游扩展图片字段 |
| skuList[].skuImageUrlTrans | string | SKU 图片及上游扩展图片字段 |
| skuList[].attributes | array | SKU 属性；包含名称、值以及可选图片 |
| skuList[].fenxiaoPriceInfo | object | `offerPrice`、`onePiecePrice`、`foreignCurrencyPrice`、`foreignCurrencyPromotionPrice` |
| skuList[].fenxiaoPriceInfo.offerPrice | string | `fenxiaoPriceInfo` 中的 `offerPrice`；类型由来源响应示例确认 |
| skuList[].fenxiaoPriceInfo.onePiecePrice | string | `fenxiaoPriceInfo` 中的 `onePiecePrice`；类型由来源响应示例确认 |
| skuList[].fenxiaoPriceInfo.foreignCurrencyPrice | 来源未说明 | `fenxiaoPriceInfo` 外币价格字段 |
| skuList[].fenxiaoPriceInfo.foreignCurrencyPromotionPrice | 来源未说明 | `fenxiaoPriceInfo` 外币营销价格字段 |

#### `saleInfo`

| 字段路径 | 类型 | 说明 |
|---|---|---|
| saleInfo.amountOnSale | integer | 商品总库存 |
| saleInfo.retailPrice | string | 商品级零售价（人民币），适用于采购数量 1 件；上游无零售价时缺失 |
| saleInfo.foreignCurrencyRetailPrice | number | 商品级外币零售价，适用于采购数量 1 件；未请求币种、无零售价或换算失败时缺失 |
| saleInfo.quoteType | integer | `0` 无 SKU 按商品数量；`1` 按 SKU 规格；`2` 有 SKU 按商品数量 |
| saleInfo.priceRanges | array | 批发阶梯价：`startQuantity`、`price`、`promotionPrice`、`foreignCurrencyPrice`、`foreignCurrencyPromotionPrice`；新零售价模型首档大于等于 2，旧商品模型可能仍从 1 件起 |
| saleInfo.unitInfo | object | 单位字段 `unit` 与上游扩展字段 `transUnit` |
| saleInfo.fenxiaoSaleInfo | object | `startQuantity`、`offerPrice`、`onePiecePrice`、`onePieceFreePostage` |
| saleInfo.consignPrice | string | 上游废弃兼容字段，可能缺失 |
| saleInfo.jxhyPrice | string | 上游废弃兼容字段，可能缺失 |
| saleInfo.priceRanges[].startQuantity | integer | 批发阶梯起始数量；类型由来源响应示例确认 |
| saleInfo.priceRanges[].price | string | 批发阶梯人民币价格；类型由来源响应示例确认 |
| saleInfo.priceRanges[].promotionPrice | 来源未说明 | 批发阶梯营销价 |
| saleInfo.priceRanges[].foreignCurrencyPrice | number | 批发阶梯外币价格；类型由来源响应示例确认 |
| saleInfo.priceRanges[].foreignCurrencyPromotionPrice | 来源未说明 | 批发阶梯外币营销价 |
| saleInfo.unitInfo.unit | 来源未说明 | 单位字段 |
| saleInfo.unitInfo.transUnit | 来源未说明 | 上游扩展单位字段 |
| saleInfo.fenxiaoSaleInfo.startQuantity | 来源未说明 | 分销销售起始数量 |
| saleInfo.fenxiaoSaleInfo.offerPrice | 来源未说明 | 分销销售报价 |
| saleInfo.fenxiaoSaleInfo.onePiecePrice | 来源未说明 | 分销一件价格 |
| saleInfo.fenxiaoSaleInfo.onePieceFreePostage | 来源未说明 | 分销一件包邮字段 |

#### `shippingInfo`

| 字段路径 | 类型 | 说明 |
|---|---|---|
| shippingInfo.sendGoodsAddressText | string | 发货地 |
| shippingInfo.shippingTimeGuarantee | string | 发货保障 |
| shippingInfo.length | number | 商品长宽高，单位 cm |
| shippingInfo.width | number | 商品长宽高，单位 cm |
| shippingInfo.height | number | 商品长宽高，单位 cm |
| shippingInfo.weight | number | 商品重量，单位 kg |
| shippingInfo.officialLength | number | 官方测量长宽高，单位 cm |
| shippingInfo.officialWidth | number | 官方测量长宽高，单位 cm |
| shippingInfo.officialHeight | number | 官方测量长宽高，单位 cm |
| shippingInfo.officialWeight | number | 官方测量重量，单位 kg |
| shippingInfo.pkgSizeSource | string | 商品件重尺数据来源 |
| shippingInfo.skuShippingInfoList | array | SKU 物流规格；`weight` 单位 g，其余尺寸单位 cm |
| shippingInfo.skuShippingDetails | array | SKU 件重尺；`weight`/`officialWeight`/`aiWeight` 单位 kg，尺寸单位 cm |
| shippingInfo.skuShippingInfoList[].weight | 来源未说明 | SKU 物流规格重量，单位 g |
| shippingInfo.skuShippingDetails[].weight | 来源未说明 | SKU 件重尺重量，单位 kg |
| shippingInfo.skuShippingDetails[].officialWeight | 来源未说明 | SKU 件重尺官方重量，单位 kg |
| shippingInfo.skuShippingDetails[].aiWeight | 来源未说明 | SKU 件重尺 AI 重量，单位 kg |

#### `sellerDataInfo`

| 字段路径 | 类型 | 说明 |
|---|---|---|
| sellerDataInfo.tradeMedalLevel | string | 卖家交易勋章 |
| sellerDataInfo.compositeServiceScore | string | 综合服务分 |
| sellerDataInfo.logisticsExperienceScore | string | 物流体验分 |
| sellerDataInfo.disputeComplaintScore | string | 纠纷解决分 |
| sellerDataInfo.offerExperienceScore | string | 商品体验分 |
| sellerDataInfo.consultingExperienceScore | string | 咨询体验分 |
| sellerDataInfo.afterSalesExperienceScore | string | 退换体验分 |
| sellerDataInfo.repeatPurchasePercent | string | 卖家回头率 |
| sellerDataInfo.collect30DayWithin48HPercent | string | 最近 30 天 48 小时揽收率 |
| sellerDataInfo.qualityRefundWithin30Day | string | 最近 30 天品质退款率 |
### 价格语义

- 新零售价模型下，采购1件读取匹配 SKU 的 `skuList[].retailPrice`；无 SKU 商品读取 `saleInfo.retailPrice`。
- 采购数量大于等于2件读取匹配 SKU 的 `skuList[].price`，并结合 `saleInfo.priceRanges[]` 的数量阶梯；首档通常从2件起。
- `retailPrice` 缺失可能是旧商品模型或未配置零售价。不要用 `price`、`consignPrice`、`jxhyPrice`、`offerPrice`、`onePiecePrice` 或 `promotionPrice` 推断1件价格。若阶梯明确从 `startQuantity=1` 起，只标为旧模型阶梯信息；成本/下单仍以实时订单预览为准。
- `currency` 请求只影响 `foreignCurrencyRetailPrice`、`fenxiaoPriceInfo.foreignCurrencyPrice` 等外币字段；人民币 `retailPrice`、`price`、`offerPrice` 不得改标为请求币种。外币字段缺失可能是未请求、无价格或换算失败。

### 错误码

| errcode / HTTP | 含义 | 处理 |
|---|---|---|
| `200` | 成功 | 解析并确认返回 `offerId` 与请求一致 |
| `400` | 路由层参数校验失败 | 检查 `offerId`/`currency` 的必填、类型、格式、长度 |
| `1002` | 服务层参数或登录上下文错误 | 检查 ID、币种或重新登录 |
| `1003` | 1688商详服务/上游异常 | 稍后最多按用户决定重试一次；仍失败联系维护方 |
| `1005` | 当前用户未授权且默认授权不可回退 | 按授权流程处理 |
| HTTP `401` | API key 鉴权失败 | 读取顶层 `references/onboarding.md` |
| HTTP `402` | 积分不足 | 读取顶层 `references/onboarding.md` |
| HTTP `403` | 无权限 | 不走登录/充值引导，联系管理员确认工具权限 |

代理成功后的下游错误应优先按 JSON 状态和消息解释，不应把 MCP 外层错误当作业务结果。

## 调用与展示规则

1. 同一任务内相同 `toolName + arguments` 不得重复调用；需要再次查询时先说明额外积分消耗并取得用户确认。
2. 涉及采购成本、利润、报价或下单决策时说明数据时点；仍需用实时订单预览确认可购性、优惠、运费和成交价。
3. 先显示 `subject` 与 `offerId`，再用 SKU 表格展示属性、库存、1件零售价、2件及以上批发价、请求币种价格和可用代发价；人民币与外币必须分列。
4. 补充 MOQ、单位、混批规则、代发/包邮、发货地、发货保障、件重尺、供应商指标、促销、发票和证书；缺失字段保持未知。
5. `description` 中的 HTML 视为数据，摘要或抽取媒体链接，不直接渲染不可信标记；不向用户展示 `sourceTool` 等内部路由标签。

## 示例

完整 `proxy_call` 参数示例：

```json
{
  "toolName": "alibaba1688/productDetail",
  "arguments": {
    "offerId": "1040473674152",
    "currency": "USD"
  }
}
```

按 ID 查询并请求 USD 字段：

```json
{"offerId":"1040473674152","currency":"USD"}
```

从链接核验：先提取 `1040473674152`，再调用：

```json
{"offerId":"1040473674152"}
```

该接口每次只查一个商品；用户给多个 offerId 时先说明会产生多次调用，再由用户决定是否逐个查询。

## 反馈 API

用户表达赞扬、不满、建议或结果错误时，可按本子能力契约 POST `https://skill-api.linkfox.com/api/v1/public/feedback`，字段为 `skillName`（`linkfox-1688-product-detail`）、`sentiment`（`POSITIVE`/`NEUTRAL`/`NEGATIVE`）、`category`（`BUG`/`COMPLAINT`/`SUGGESTION`/`OTHER`）和 `content`；不要与商品网关混用 base URL。
