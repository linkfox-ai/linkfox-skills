# 1688 商品详情 接口说明

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

## 接口：1688 商品详情

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/alibaba1688/productDetail`

### 请求参数

POST Body（JSON）只需传 1688 业务参数：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| offerId | string | 是 | - | 正整数格式的 1688 商品 ID；必须使用字符串，避免大数精度丢失；最大长度 1000 |
| country | string | 否 | `en` | 上游兼容字段；本技能不将其作为用户能力，通常省略 |
| currency | string | 否 | 1688 默认币种 | 三位字母币种编码，如 `USD`、`HKD`；服务端会转为大写；最大长度 3 |

#### 平台上下文字段

以下字段由平台按上下文自动注入，普通脚本调用不要填写。其类型、必填性和默认值由平台管理，本接口不作单独约定。

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|------|------|
| uid | 未约定 | 平台管理 | 未约定 | 由平台上下文注入。 |
| chatId | 未约定 | 平台管理 | 未约定 | 由平台上下文注入。 |
| requestId | 未约定 | 平台管理 | 未约定 | 由平台上下文注入。 |
| groupId | 未约定 | 平台管理 | 未约定 | 由平台上下文注入。 |
| stepId | 未约定 | 平台管理 | 未约定 | 由平台上下文注入。 |
| messageId | 未约定 | 平台管理 | 未约定 | 由平台上下文注入。 |
| userInput | 未约定 | 平台管理 | 未约定 | 由平台上下文注入。 |
| memberId | 未约定 | 平台管理 | 未约定 | 由平台上下文注入。 |

#### 参数校验

- `offerId` 缺失或空字符串：返回参数错误。
- `offerId` 不是十进制整数或小于等于 0：返回参数错误。
- `country` 空白时使用服务端默认值；非空时去除首尾空白并原样传给 1688。
- `currency` 非空时必须匹配三位英文字母，服务端转为大写；例如 `usd` 会按 `USD` 请求。

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|------|------|
| JSON 参数 | JSON object | 是 | 无 | 第一个位置参数；业务字段见上表，不自动从 URL 提取编号。 |
| --inline | CLI flag | 否 | 关闭 | 强制全量输出，仍保存完整响应。 |
| --no-cache | CLI flag | 否 | 关闭 | 跳过响应缓存读取与写入；用于采购成本、利润率、报价或下单前的实时查询。 |

- 命令行入口为 `python scripts/alibaba1688_product_detail.py '<JSON 参数>' [--inline] [--no-cache]`；参数校验由服务端执行，脚本不擅自补齐平台上下文字段或改变业务字段。
- 脚本提供 24 小时本地响应缓存，由 `scripts/call_api.py` 执行一层缓存。缓存路径为 `<cwd>/linkfox/.cache/linkfox-1688-product-detail/linkfox-1688-product-detail-<参数摘要>.json`，以排序后的完整 JSON 参数计算 SHA-256 前 16 位，超时或不可解析的缓存不复用。
- 命中缓存时保留 `_cache.hit=true` 标记，仍落盘完整响应；新响应默认写缓存，`--no-cache` 时不读写响应缓存。缓存结果不保证实时价格。
- 环境变量 `LINKFOX_TOOL_GATEWAY` 可覆盖基础地址；认证优先读取 `LINKFOX_AGENT_API_KEY`，回退读取 `LINKFOXAGENT_API_KEY`。透传同名环境变量 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 为请求头，未配置时传空字符串。
- 业务入口在请求前检查 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/` 可写，并固定公共调用器使用当前目录；禁止落盘到系统临时目录（含 `/tmp`），不可写时退出，不发送商品详情请求，也不回退到 `ACPX_WORKSPACES`、家目录或其他位置。完整响应保存、会话元数据、文件登记和大小响应输出策略见 `SKILL.md` 的“执行方式”。小响应阈值为 UTF-8 编码后 8000 字节。
- 错误响应也可能被缓存。认证或用量问题解决后，如需重新验证，应明确额外消耗并使用 `--no-cache`，避免复用先前的错误响应，不自动重复请求。

#### 使用限制

- 一次仅接受一个 `offerId`，不支持按关键词或图片搜索；查询不改变采购状态，不执行授权、下单、支付或开票。
- 商品、价格、库存、物流和供应商数据会变化；采购敏感查询需禁用缓存，最终成交条件通过订单预览确认。
- 视频、证书、促销和部分物流字段可能缺失；请求外币不保证每个 SKU、零售价或批发阶梯都有外币字段，外币零售价缺失也可能是换算失败。
- 结果不存入分析数据库，不能据此进行二次 SQL 或数据查询处理；不提供历史价格趋势或买家评论。

### 响应结构

成功响应为一个 JSON object。网关会加入 `errcode=200` 与 `errmsg=ok`；业务字段来自标准化的 1688 商详模型。上游未返回的可选字段可能不出现在 JSON 中，不应把“字段缺失”解释为 `false`、`0` 或空字符串。

#### 网关与核心字段

| 字段 | 类型 | 说明 |
|------|------|------|
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

#### 商品、媒体与采购字段

| 字段 | 类型 | 说明 |
|------|------|------|
| productImage | object | 原始商品图片，子字段见下方嵌套字段表 |
| productImageTrans | object | 上游扩展图片字段，结构同上，可能缺失 |
| mainVideo | string | 主视频地址 |
| detailVideo | string | 详情视频地址 |
| productAttributes | array | 商品属性，子字段见下方嵌套字段表 |
| sellingPoints | array | 商品卖点，可能为空 |
| skuList | array | SKU、规格、库存、价格与 SKU 图片，详见下节 |
| saleInfo | object | 库存、阶梯价、单位和分销销售信息，详见下节 |
| shippingInfo | object | 发货地、时效与商品/SKU 件重尺，详见下节 |
| companyName | string | 供应商/店铺名称 |
| sellerOpenId | string | 商家加密 ID |
| sellerDataInfo | object | 卖家服务与交易指标，详见下节 |
| sellerMixSetting | object | 混批设置，子字段见下方嵌套字段表 |
| channelPrice | object | 渠道 SKU 价格，子字段见下方嵌套字段表 |
| promotion | object | 营销信息，子字段见下方嵌套字段表 |
| minOrderQuantity | integer | 最小起批量 |
| batchNumber | integer | 一手数量 |
| productCargoNumber | string | 商品货号 |
| soldOut | string | 商品销量 |
| isJxhy | boolean | 是否精选货源 |
| isSelect | boolean | 是否跨境 Select 货盘 |
| tradeScore | string | 商品交易评分 |
| offerIdentities | array | 商品或商家身份标识 |
| tags | array | 服务标签，子字段见下方嵌套字段表 |
| certificates | array | 证书，子字段见下方嵌套字段表 |
| invoiceInfo | object | 发票信息，子字段见下方嵌套字段表 |

#### `skuList[]`

| 字段 | 类型 | 说明 |
|------|------|------|
| skuId | string | SKU ID |
| specId | string | 规格 ID |
| cargoNumber | string | SKU 货号 |
| amountOnSale | integer | 可售库存 |
| price | string | SKU 价格（人民币）；新零售价模型中是采购数量大于等于 2 件的批发价，旧商品模型语义结合阶梯和订单预览判断 |
| retailPrice | string | SKU 零售价（人民币），适用于采购数量 1 件；上游无零售价时缺失 |
| foreignCurrencyRetailPrice | number | SKU 外币零售价，适用于采购数量 1 件；未请求币种、无零售价或换算失败时缺失 |
| promotionPrice | string | 营销价 |
| consignPrice | string | 一件代发价格；上游废弃兼容字段，可能缺失 |
| jxhyPrice | string | 精选货源兼容价格字段，可能缺失 |
| pfJxhyPrice | string | 精选货源兼容价格字段，可能缺失 |
| skuImageUrl | string | SKU 图片 |
| skuImageUrlTrans | string | 上游扩展 SKU 图片字段 |
| attributes | array | SKU 属性；包含名称、值以及可选图片 |
| fenxiaoPriceInfo | object | 分销价格信息，子字段见下方嵌套字段表 |

#### `saleInfo`

| 字段 | 类型 | 说明 |
|------|------|------|
| amountOnSale | integer | 商品总库存 |
| retailPrice | string | 商品级零售价（人民币），适用于采购数量 1 件；上游无零售价时缺失 |
| foreignCurrencyRetailPrice | number | 商品级外币零售价，适用于采购数量 1 件；未请求币种、无零售价或换算失败时缺失 |
| quoteType | integer | `0` 无 SKU 按商品数量；`1` 按 SKU 规格；`2` 有 SKU 按商品数量 |
| priceRanges | array | 批发阶梯价，子字段见下方嵌套字段表 |
| unitInfo | object | 单位信息，子字段见下方嵌套字段表 |
| fenxiaoSaleInfo | object | 分销销售信息，子字段见下方嵌套字段表 |
| consignPrice | string | 上游废弃兼容字段，可能缺失 |
| jxhyPrice | string | 上游废弃兼容字段，可能缺失 |

#### `shippingInfo`

| 字段 | 类型 | 说明 |
|------|------|------|
| sendGoodsAddressText | string | 发货地 |
| shippingTimeGuarantee | string | 发货保障 |
| length | number | 商品长度，单位 cm |
| width | number | 商品宽度，单位 cm |
| height | number | 商品高度，单位 cm |
| weight | number | 商品重量，单位 kg |
| officialLength | number | 官方测量长度，单位 cm |
| officialWidth | number | 官方测量宽度，单位 cm |
| officialHeight | number | 官方测量高度，单位 cm |
| officialWeight | number | 官方测量重量，单位 kg |
| pkgSizeSource | string | 商品件重尺数据来源 |
| skuShippingInfoList | array | SKU 物流规格，重量与尺寸单位见下方嵌套字段表 |
| skuShippingDetails | array | SKU 件重尺，重量与尺寸单位见下方嵌套字段表 |

#### `sellerDataInfo`

| 字段 | 类型 | 说明 |
|------|------|------|
| tradeMedalLevel | string | 卖家交易勋章 |
| compositeServiceScore | string | 综合服务分 |
| logisticsExperienceScore | string | 物流体验分 |
| disputeComplaintScore | string | 纠纷解决分 |
| offerExperienceScore | string | 商品体验分 |
| consultingExperienceScore | string | 咨询体验分 |
| afterSalesExperienceScore | string | 退换体验分 |
| repeatPurchasePercent | string | 卖家回头率 |
| collect30DayWithin48HPercent | string | 最近 30 天 48 小时揽收率 |
| qualityRefundWithin30Day | string | 最近 30 天品质退款率 |

#### 其他已命名的嵌套字段

以下列出容器内的子字段。类型标注“未约定”的字段没有固定类型约定，不据名称猜测类型；标注“示例”的类型仅说明下方示例中的值类型，实际值以响应为准。可选字段缺失时保持缺失，不补默认值。

| 字段 | 类型 | 说明 |
|------|------|------|
| productImage.images[] | 未约定 | 原始商品图片列表中的图片。 |
| productImage.whiteImage | 未约定 | 原始白底图片。 |
| productImageTrans.images[] | 未约定 | 上游扩展图片，与原始图片结构相同，可能缺失。 |
| productImageTrans.whiteImage | 未约定 | 上游扩展白底图片，可能缺失。 |
| productAttributes[].attributeId | 未约定 | 商品属性 ID。 |
| productAttributes[].attributeName | 未约定 | 商品属性名称。 |
| productAttributes[].attributeNameTrans | 未约定 | 上游扩展属性名称。 |
| productAttributes[].value | 未约定 | 商品属性值。 |
| productAttributes[].valueTrans | 未约定 | 上游扩展属性值。 |
| skuList[].attributes[] | 未约定 | SKU 属性元素，含名称、值和可选图片；内部字段名以实际响应为准。 |
| skuList[].fenxiaoPriceInfo.offerPrice | string（示例） | 分销报价，人民币，不直接标为请求币种。 |
| skuList[].fenxiaoPriceInfo.onePiecePrice | string（示例） | 分销兼容价格，不作为缺失零售价的替代。 |
| skuList[].fenxiaoPriceInfo.foreignCurrencyPrice | 未约定 | 请求币种对应的外币报价。 |
| skuList[].fenxiaoPriceInfo.foreignCurrencyPromotionPrice | 未约定 | 请求币种对应的外币营销价。 |
| saleInfo.priceRanges[].startQuantity | integer（示例） | 阶梯起始数量；新零售价模型首档大于等于 2，旧模型可能从 1 起。 |
| saleInfo.priceRanges[].price | string（示例） | 阶梯价格，人民币。 |
| saleInfo.priceRanges[].promotionPrice | 未约定 | 阶梯营销价，不替代零售价。 |
| saleInfo.priceRanges[].foreignCurrencyPrice | number（示例） | 请求币种对应的阶梯价格。 |
| saleInfo.priceRanges[].foreignCurrencyPromotionPrice | 未约定 | 请求币种对应的阶梯营销价。 |
| saleInfo.unitInfo.unit | 未约定 | 商品单位。 |
| saleInfo.unitInfo.transUnit | 未约定 | 上游扩展单位字段。 |
| saleInfo.fenxiaoSaleInfo.startQuantity | 未约定 | 分销起订数量。 |
| saleInfo.fenxiaoSaleInfo.offerPrice | 未约定 | 分销报价。 |
| saleInfo.fenxiaoSaleInfo.onePiecePrice | 未约定 | 分销兼容价格。 |
| saleInfo.fenxiaoSaleInfo.onePieceFreePostage | 未约定 | 一件代发包邮条款。 |
| shippingInfo.skuShippingInfoList[].weight | 未约定 | SKU 物流重量，单位 g；该列表其余尺寸单位 cm，尺寸字段名以实际响应为准。 |
| shippingInfo.skuShippingDetails[].weight | 未约定 | SKU 件重尺重量，单位 kg。 |
| shippingInfo.skuShippingDetails[].officialWeight | 未约定 | SKU 官方测量重量，单位 kg。 |
| shippingInfo.skuShippingDetails[].aiWeight | 未约定 | SKU AI 重量，单位 kg；该列表尺寸单位 cm，尺寸字段名以实际响应为准。 |
| sellerMixSetting.generalHunpi | 未约定 | 混批设置。 |
| sellerMixSetting.mixAmount | 未约定 | 混批金额。 |
| sellerMixSetting.mixNumber | 未约定 | 混批数量。 |
| channelPrice.skuPrices[] | 未约定 | 渠道 SKU 价格列表。 |
| channelPrice.skuPrices[].skuId | 未约定 | 渠道价格对应 SKU。 |
| channelPrice.skuPrices[].currentPrice | 未约定 | 渠道当前价格。 |
| promotion.hasPromotion | 未约定 | 是否存在营销活动。 |
| promotion.promotionType | 未约定 | 营销类型。 |
| tags[].key | 未约定 | 服务标签键。 |
| tags[].value | 未约定 | 服务标签值。 |
| certificates[].certificateName | 未约定 | 证书名称。 |
| certificates[].certificateCode | 未约定 | 证书编号。 |
| certificates[].certificatePhotoList[] | 未约定 | 证书图片。 |
| invoiceInfo.supportOnlineInvoice | 未约定 | 在线开票支持信息。 |
| invoiceInfo.supportFastInvoice | 未约定 | 快速开票支持信息。 |
| invoiceInfo.invoiceTypes[] | 未约定 | 支持的发票类型。 |
| invoiceInfo.taxpayerType | 未约定 | 纳税人类型。 |

#### 脚本补充字段

以下由调用器在特定情况下生成，不是上游商品属性。

| 字段 | 类型 | 说明 |
|------|------|------|
| error | string | HTTP 错误体为空、不是 JSON 或连接失败时的错误说明。可解析的 HTTP 错误 JSON 仍原样保留。 |
| details | string | HTTP 错误体不是 JSON 时保留的原始正文。 |
| _cache | object | 命中响应缓存时添加的本地元数据。 |
| _cache.hit | boolean | `true` 表示复用了 24 小时内的缓存；不表示当前实时价格。 |

### 响应示例

以下示例说明含零售价模型的字段位置和类型，不保证指定 offerId 返回全部示例字段；实际字段和值以实时响应为准。

```json
{
  "errcode": 200,
  "errmsg": "ok",
  "offerId": "1040473674152",
  "subject": "专业采耳工具掏耳朵耳朵鹅绒毛毛棒打毛毛扣挖耳勺采耳按摩鹅毛棒",
  "skuList": [
    {
      "skuId": "6226287579433",
      "retailPrice": "4.80",
      "foreignCurrencyRetailPrice": 0.73,
      "price": "4.05",
      "amountOnSale": 457,
      "fenxiaoPriceInfo": {
        "offerPrice": "4.05",
        "onePiecePrice": "4.05"
      }
    }
  ],
  "saleInfo": {
    "amountOnSale": 1917,
    "retailPrice": "4.80",
    "foreignCurrencyRetailPrice": 0.73,
    "priceRanges": [
      {
        "startQuantity": 2,
        "price": "4.05",
        "foreignCurrencyPrice": 0.62
      }
    ]
  },
  "sourceType": "1688",
  "type": "productDetail",
  "costToken": 1000
}
```


### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

按基础规则判断后，正常响应仍需确认 `offerId` 与请求一致。脚本尽量将 HTTP 错误体解析为 JSON；非 JSON 错误体保留在 `details`，连接失败返回 `error`，不因网关 4xx/5xx 打印 Python 堆栈。

| errcode / HTTP | 含义 | 处理建议 |
|------|------|------|
| 400 | 路由层参数校验失败 | 检查必填、类型、格式与长度；错误响应可能回显已接收的参数。 |
| 1002 | 服务层参数或登录上下文错误 | 检查 `offerId`、`currency`，或重新登录。 |
| 1003 | 1688 商详服务或上游响应异常 | 可建议稍后重试一次；仍失败则联系网关维护者。任何后续调用先遵守成本约束，不自动重试。 |
| 1005 | 当前用户未授权且默认授权不可回退 | 按 1688 授权流程处理。 |
| HTTP 403 | 无权限 | 不属于登录或充值引导，联系管理员确认工具权限。 |

参数错误响应可能形如 `{"errcode":400,"offerId":"","errmsg":"offerId 为必填参数"}`。

### curl 示例

```bash
API_KEY="${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}"

curl --location "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/alibaba1688/productDetail" \
  --header "Authorization: ${API_KEY}" \
  --header "Content-Type: application/json" \
  --header "User-Agent: LinkFox-Skill/2.0" \
  --header "SESSION_ID: ${SESSION_ID:-}" \
  --header "MESSAGE_ID: ${MESSAGE_ID:-}" \
  --header "MODE_ID: ${MODE_ID:-}" \
  --header "APP_NAME: ${APP_NAME:-}" \
  --data '{
    "offerId": "1040473674152",
    "currency": "USD"
  }'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-1688-product-detail",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```

