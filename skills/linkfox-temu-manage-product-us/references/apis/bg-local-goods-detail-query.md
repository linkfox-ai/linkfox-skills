# Temu 美国站商品详情接口说明

对应脚本：`scripts/us_manage_detail_query.py`。网关及兼容运行约定见 [api.md](../api.md)。

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

## 接口：商品详情（bg.local.goods.detail.query）

> Partner 官方文档：https://partner-us.temu.com/documentation?menu_code=fb16b05f7a904765aac4af3a24b87d4a&sub_menu_code=9ebbd5d269014322ad4a6c123b1dfdae

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/proxy`

### 请求参数

**用途说明：**商品详情。

#### 网关 POST Body

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| site | string | 是 | 本技能默认 `us`；兼容 `cn`、`partner`、`global`、`eu`，须与令牌来源一致。 |
| managementType | string | 是 | 默认 `semi-managed`，兼容 `full-managed`；区分店铺托管类型。 |
| accessToken | string | 与 storeKey 二选一 | Temu 店铺令牌；传入时优先于本地令牌。 |
| storeKey | string | 脚本兼容 | 本地店铺键，脚本读取令牌后仅发送 accessToken，不将 storeKey 发给网关。 |
| tokenPurpose | string | 否 | 本技能店铺令牌默认用途 `product-inventory`；用于本地定位，不发往网关。 |
| type | string | 是 | 固定为 `bg.local.goods.detail.query`；大小写与原值一致。 |
| params | object | 否 | Temu 业务参数；本接口的 request 及其子字段见下文。 |

#### 脚本参数与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| token / linkfoxToken / linkfox_token | string | 否 | 按此顺序优先于环境变量读取 LinkFox Key；不进入业务参数。 |
| site / managementType / tokenPurpose | string | 否 | 美国站包装器使用上表默认值；通用 temu_proxy.py 要求显式提供 site、managementType，本地令牌用途默认 default。 |
| params | object | 否 | 如为对象，优先作为完整业务参数；否则美国站包装器将顶层非保留字段作为业务参数。 |
| --inline | CLI flag | 否 | 强制全量打印响应，仍保存完整文件。 |
| --no-cache | CLI flag | 否 | 兼容选项；业务封装始终传入，禁用响应缓存。 |

#### Temu 业务参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| request | OBJECT | 否 | 官方业务参数对象；下文子字段必填性、嵌套关系和限制仍须遵守。 |

```text
params
└── request (OBJECT, 选填)
    ├── language
    ├── goodsId              ← 必填
    └── versionQueryType     ← 查哪一版商品信息
```

##### `request` 内字段

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| language | STRING | 否 | 语言 |
| goodsId | LONG | **是** | 商品 ID |
| versionQueryType | INTEGER | 否 | 拉取哪一版商品信息，默认 **`2`** |

###### `versionQueryType` 枚举

| 值 | 说明 |
|----|------|
| `1` | 拉取**当前审核中**的最新版本商品信息 |
| `2` | 拉取**线上在售**快照（编辑前的线上版本），**默认** |

### 响应结构

#### LinkFox 网关与脚本输出

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 如存在，严格按公共响应码基本规则判断。 |
| errmsg | string | 网关错误说明；保留原始内容。 |
| code | integer | 本技能网关业务错误码，1002 表示参数或 Token 问题，1003 表示转发失败；不能用它替代公共 errcode 规则。 |
| body | string | Temu 原始 JSON 字符串；按原始内容保存。 |
| temuBody | object / array / scalar | 仅脚本加工字段：body 为有效 JSON 字符串时解析生成；无效或空字符串不补造。 |
| _httpStatus | integer / null | 仅脚本附加：本次请求网关的实际 HTTP 状态，连接失败为 null；用于判断 HTTP 401/402 等传输结果。完整响应和标准输出均保留，不是网关或 Temu 业务字段。 |

以下表格描述 body 解析后的 Temu 业务对象（脚本输出的 temuBody），不表示网关顶层字段。

```text
response
├── success
├── errorCode
├── errorMsg
└── result
    ├── goodsId
    ├── catId
    ├── subStatus
    ├── goodsName
    ├── goodsDesc
    ├── bulletPoints
    ├── customized
    ├── productType
    ├── sourceSiteInfo
    ├── targetSiteInfo[]
    ├── goodsGallery
    ├── importDesignation
    ├── outGoodsSn
    ├── goodsServicePromise
    ├── goodsProperties[]
    ├── goodsTrademark
    ├── goodsSizeChartList
    ├── goodsSizeImage
    ├── goodsOriginInfo
    ├── secondHand
    ├── itemTaxCode
    ├── skuList[]
    └── saveModeStatus
```

| 参数 | 类型 | 说明 |
|------|------|------|
| success | BOOLEAN | 是否成功 |
| errorCode | INTEGER | 错误码 |
| errorMsg | STRING | 错误信息 |
| result | OBJECT | 商品详情 |

##### `result` 顶层字段（官方）

> **注意**：详情**响应** 的 `result` 为**扁平结构**（字段直接在 `result` 下），与 **update 请求** 中包在 `request.goodsBasic` 内的层级**不同**。改商品时请按 [partial.update](./bg-local-goods-partial-update.md) / [update](./bg-local-goods-update.md) 的 **请求**结构组装。

| 参数 | 类型 | 说明 |
|------|------|------|
| goodsId | LONG | 商品 ID |
| catId | LONG | 叶子类目 ID（须与 category version 对应类目树一致） |
| subStatus | INTEGER | 商品草稿状态 |
| goodsName | STRING | 商品名称 |
| goodsDesc | STRING | 商品描述 |
| bulletPoints | STRING[] | 商品卖点 |
| customized | BOOLEAN | 是否定制商品 |
| productType | INTEGER | `1` 普通商品，`2` 定制商品，`3` 按单生产商品 |
| sourceSiteInfo | OBJECT | 来源站点商品 ID（子字段见 Partner 展开） |
| targetSiteInfo | OBJECT[] | 目标站点商品 ID（子字段见 Partner 展开） |
| goodsGallery | OBJECT | 图库/视频；最多 49 张图 URI、1 个视频 URI，顺序即 Temu 展示顺序，视频在画廊顶部 |
| importDesignation | STRING | 仅 USA：`Imported` / `Made in the USA` / `Made in the USA and Imported` / `Made in the USA or Imported` |
| outGoodsSn | STRING | 外部商品编码，店内唯一，最长 40 字符，勿首尾空格 |
| goodsServicePromise | OBJECT | 商家服务信息 → 结构同 [partial.update §goodsServicePromise](./bg-local-goods-partial-update.md#requestgoodsservicepromise) |
| goodsProperties | OBJECT[] | 商品通用属性（**非** `goodsProperty.goodsProperties`）→ 元素结构同 [partial.update §goodsProperties](./bg-local-goods-partial-update.md#requestgoodsproperty) |
| goodsTrademark | OBJECT | 商标信息 → 同 [partial.update §goodsTrademark](./bg-local-goods-partial-update.md#requestgoodstrademark) |
| goodsSizeChartList | OBJECT | 尺码表（套装可多套）→ 同 [partial.update §goodsSizeChartList](./bg-local-goods-partial-update.md#requestgoodssizechartlist) |
| goodsSizeImage | STRING[] | 尺码表图片 URL |
| goodsOriginInfo | OBJECT | 商品产地信息 → 同 [partial.update §goodsOriginInfo](./bg-local-goods-partial-update.md#requestgoodsorigininfo) |
| secondHand | OBJECT | 二手商品信息 → 同 [partial.update §secondHand](./bg-local-goods-partial-update.md#requestsecondhand) |
| itemTaxCode | STRING | 税务编码 |
| skuList | OBJECT[] | SKU 提交查询列表 → SKU 元素结构同 [partial.update §skuList](./bg-local-goods-partial-update.md#requestskulist) |
| saveModeStatus | INTEGER | 自动发布到 Temu 商品的卖家审核状态 |

##### `goodsGallery`（响应常见子字段）

与编辑请求一致，见 [partial.update §goodsGallery](./bg-local-goods-partial-update.md#goodsbasicgoodsgallery)：`detailVideo`、`goodsCarouselImage`、`detailImage`、`carouselVideo`。

#### 详情对象的嵌套字段定义

以下嵌套字段仅说明返回内容，不保证全部字段必返。新增、修改及条件必填规则见编辑接口的请求参数，不作为详情响应要求。

#### result.goodsGallery

| 字段 | 类型 | 说明 |
|------|------|------|
| detailVideo | OBJECT | 详情视频：`vid`、`videoUrl` |
| goodsCarouselImage | STRING[] | 商品轮播图 |
| detailImage | STRING[] | 商品详情图 |
| carouselVideo | OBJECT | 轮播视频：`vid`、`videoUrl` |

#### result.goodsServicePromise

| 字段 | 类型 | 说明 |
|------|------|------|
| shipmentLimitDay | INTEGER | 备货时间（天）；可选 `1`、`2` |
| fulfillmentType | INTEGER | `1`=商家自配送，`2`=平台配送 |
| costTemplateId | STRING | 运费模板 ID |

#### result.goodsProperties[]

| 字段 | 类型 | 说明 |
|------|------|------|
| vid | LONG | 属性值 ID；非自定义规格值的编辑规则见请求定义 |
| value | STRING | 属性值 |
| valueUnit | STRING | 属性值单位 |
| valueUnitId | LONG | 属性值单位 ID |
| templatePid | LONG | 模板属性 ID |
| parentSpecId | LONG | 非销售属性可不填 |
| specId | LONG | 非销售属性可不填 |
| note | STRING | 备注 |
| imgUrl | STRING | 图片 URL |
| groupId | INTEGER | 属性值分组 ID |
| refPid | LONG | 参考属性 ID |
| numberInputValue | STRING | 数字输入 |

#### result.goodsOriginInfo

| 字段 | 类型 | 说明 |
|------|------|------|
| originRegion1 | STRING | 一级地址（国家或地区） |
| originRegion2 | STRING | 二级地址；编辑时一级地址为中国则必填 |
| agreeDefaultOriginRegion | BOOLEAN | 默认 `false` |
| proofImageUrls | STRING[] | 产地标签实拍 |
| labelManufacturerProofImageUrls | STRING[] | 标签特写，最多 5 张 |

#### result.goodsSizeChartList

| 字段 | 类型 | 说明 |
|------|------|------|
| goodsSizeChartList | OBJECT[] | 多套尺码表（套装） |

**数组元素：** `classId`、`meta`、`groups[]`（`id`、`name`、`elements[]`、`records[]`、`values[]`）、`bodyMeta`、`bodyRecords[]`。

#### result.skuList[]

| 字段 | 类型 | 说明 |
|------|------|------|
| skuId | LONG | SKU ID |
| basePrice | OBJECT | 基础价格对象，包含 amount、currency |
| listPrice | OBJECT | 须高于 basePrice |
| listPriceType | INTEGER | 市场价类型；编辑时为空或 `0` 则须填 listPrice |
| quantity | LONG | 库存数量 |
| specIdList | LONG[] | 规格 ID 列表 |
| outSkuSn | STRING | 外部 SKU 编码；编辑时不传保留，传 `""` 清空 |
| weight | STRING | 重量 |
| weightUnit | STRING | 重量单位 |
| length / width / height | STRING | 尺寸 |
| volumeUnit | STRING | 体积单位 |
| images | STRING[] | 图片列表 |
| multiplePackage | OBJECT | 包装规格字段：`skuClassification`、`mixedSetType`、`numberOfPieces`、`pieceUnitCode`、`originNetContentNumber`、`originTotalNetContentNumber`、`netContentUnitCode`、`individuallyPacked` |

#### result.goodsTrademark

| 字段 | 类型 | 说明 |
|------|------|------|
| brandId | LONG | 品牌 ID |
| trademarkId | LONG | 商标 ID |
| noTrademark | BOOLEAN | 默认 `false` |

#### result.secondHand

| 字段 | 类型 | 说明 |
|------|------|------|
| secondHandGoods | BOOLEAN | 是否二手商品 |
| level | INTEGER | 成色状态 |

#### 详情嵌套字段补充

以下字段属于共用嵌套结构，不表示字段必返；未明确的类型不作推测。

| 字段路径 | 类型 | 说明 |
|------|------|------|
| result.goodsGallery.detailVideo.vid | 未明确 | 视频 ID。 |
| result.goodsGallery.detailVideo.videoUrl | 未明确 | 视频 URL。 |
| result.goodsGallery.carouselVideo.vid | 未明确 | 视频 ID。 |
| result.goodsGallery.carouselVideo.videoUrl | 未明确 | 视频 URL。 |
| result.skuList[].basePrice.amount | 未明确 | 金额，单位未明确。 |
| result.skuList[].basePrice.currency | 未明确 | 币种。 |
| result.skuList[].listPrice.amount | 未明确 | 金额，单位未明确。 |
| result.skuList[].listPrice.currency | 未明确 | 币种。 |
| result.skuList[].length | STRING | 长、宽、高之一，单位由 volumeUnit 指定。 |
| result.skuList[].width | STRING | 长、宽、高之一，单位由 volumeUnit 指定。 |
| result.skuList[].height | STRING | 长、宽、高之一，单位由 volumeUnit 指定。 |
| result.skuList[].multiplePackage.skuClassification | 未明确 | SKU 分类。 |
| result.skuList[].multiplePackage.mixedSetType | 未明确 | 混合套装类型。 |
| result.skuList[].multiplePackage.numberOfPieces | 未明确 | 件数。 |
| result.skuList[].multiplePackage.pieceUnitCode | 未明确 | 件数单位代码。 |
| result.skuList[].multiplePackage.originNetContentNumber | 未明确 | 原始净含量。 |
| result.skuList[].multiplePackage.originTotalNetContentNumber | 未明确 | 原始总净含量。 |
| result.skuList[].multiplePackage.netContentUnitCode | 未明确 | 净含量单位代码。 |
| result.skuList[].multiplePackage.individuallyPacked | 未明确 | 是否独立包装。 |
| result.goodsSizeChartList.goodsSizeChartList[].classId | 未明确 | 尺码表分类 ID。 |
| result.goodsSizeChartList.goodsSizeChartList[].meta | 未明确 | 尺码表元数据。 |
| result.goodsSizeChartList.goodsSizeChartList[].bodyMeta | 未明确 | 身体数据元信息。 |
| result.goodsSizeChartList.goodsSizeChartList[].bodyRecords[] | 未明确 | 身体数据记录。 |
| result.goodsSizeChartList.goodsSizeChartList[].groups[].id | 未明确 | 尺码表分组 ID。 |
| result.goodsSizeChartList.goodsSizeChartList[].groups[].name | 未明确 | 分组名称。 |
| result.goodsSizeChartList.goodsSizeChartList[].groups[].elements[] | 未明确 | 分组元素。 |
| result.goodsSizeChartList.goodsSizeChartList[].groups[].records[] | 未明确 | 分组记录。 |
| result.goodsSizeChartList.goodsSizeChartList[].groups[].values[] | 未明确 | 分组值。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 按公共基础规则确认网关正常后，检查本技能 code（1002 / 1003 为失败），再解析 body；Temu success 为 false 时依据 errorCode / errorMsg 解释原因，保留原始响应。
- 仅根据本接口返回的业务字段报告结果；未展开的 result 子字段以实际响应为准，不套用其他接口或补造字段。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/temu/proxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Token: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "site": "us",
  "managementType": "semi-managed",
  "accessToken": "TOKEN",
  "type": "bg.local.goods.detail.query",
  "params": {
    "request": {
      "goodsId": 123456
    }
  }
}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-temu-manage-product-us",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
