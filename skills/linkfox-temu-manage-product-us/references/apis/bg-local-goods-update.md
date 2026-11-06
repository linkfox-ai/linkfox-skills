# Temu 美国站全量编辑接口说明

对应脚本：`scripts/us_manage_goods_update.py`。网关及兼容运行约定见 [api.md](../api.md)。

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

## 接口：全量编辑（bg.local.goods.update）

> Partner 官方文档：https://partner-us.temu.com/documentation?menu_code=fb16b05f7a904765aac4af3a24b87d4a&sub_menu_code=b05f4b7598fb4dc7ac47c864aa5d5fc4

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/proxy`

### 请求参数

**用途说明：**全量编辑。

> 与 [partial.update](./bg-local-goods-partial-update.md) 共用同一 **`request` 顶层结构**（`goodsBasic` 与 `skuList` 等**同级**）。全量更新须提交**完整**商品数据，且 **`skuList` 必填**；建议先 `bg.local.goods.detail.query` 拉详情再改。  
> `goodsBasic`、`goodsProperty`、`skuList[]` 等**嵌套字段定义**见 [partial.update](./bg-local-goods-partial-update.md) 对应章节（结构一致）。

#### 网关 POST Body

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| site | string | 是 | 本技能默认 `us`；兼容 `cn`、`partner`、`global`、`eu`，须与令牌来源一致。 |
| managementType | string | 是 | 默认 `semi-managed`，兼容 `full-managed`；区分店铺托管类型。 |
| accessToken | string | 与 storeKey 二选一 | Temu 店铺令牌；传入时优先于本地令牌。 |
| storeKey | string | 脚本兼容 | 本地店铺键，脚本读取令牌后仅发送 accessToken，不将 storeKey 发给网关。 |
| tokenPurpose | string | 否 | 本技能店铺令牌默认用途 `product-inventory`；用于本地定位，不发往网关。 |
| type | string | 是 | 固定为 `bg.local.goods.update`；大小写与原值一致。 |
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
    ├── goodsId                    ← 必填
    ├── goodsBasic
    ├── goodsServicePromise
    ├── goodsProperty
    ├── goodsOriginInfo
    ├── bulletPoints
    ├── goodsDesc
    ├── guideFileInfo
    ├── goodsSizeChartList
    ├── goodsSizeImage
    ├── skuList                    ← 必填（全量）
    ├── goodsTrademark
    ├── goodsVehiclePropertyRelation
    ├── secondHand
    └── modifyId
```

与 **partial.update** 的差异：

| 字段 | partial.update | goods.update（本接口） |
|------|----------------|------------------------|
| `skuList` | 选填，可只传要改的 SKU | **必填**，须传完整 SKU 列表 |
| `saveMode` | 有 | **无**（官方入参未列出） |

##### `request` 内字段一览

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| language | STRING | 否 | 语言 |
| goodsId | LONG | **是** | 商品编号 |
| goodsBasic | OBJECT | 否 | 商品基本信息 → [goodsBasic](./bg-local-goods-partial-update.md#goodsbasic) |
| goodsServicePromise | OBJECT | 否 | 商品服务承诺 → [partial 文档](./bg-local-goods-partial-update.md#requestgoodsservicepromise) |
| goodsProperty | OBJECT | 否 | 商品属性 → [partial 文档](./bg-local-goods-partial-update.md#requestgoodsproperty) |
| goodsOriginInfo | OBJECT | 否 | 原产国家或地区 → [partial 文档](./bg-local-goods-partial-update.md#requestgoodsorigininfo) |
| bulletPoints | STRING[] | 否 | 商品卖点 |
| goodsDesc | STRING | 否 | 商品描述 |
| guideFileInfo | OBJECT | 否 | 说明文件信息 → [partial 文档](./bg-local-goods-partial-update.md#requestguidefileinfo) |
| goodsSizeChartList | OBJECT | 否 | 商品尺码表列表 → [partial 文档](./bg-local-goods-partial-update.md#requestgoodssizechartlist) |
| goodsSizeImage | STRING[] | 否 | 尺码表图片 URL |
| skuList | OBJECT[] | **是** | SKU 列表 → [partial 文档](./bg-local-goods-partial-update.md#requestskulist) |
| goodsTrademark | OBJECT | 否 | 商品商标 → [partial 文档](./bg-local-goods-partial-update.md#requestgoodstrademark) |
| goodsVehiclePropertyRelation | OBJECT | 否 | 车型数据 → [partial 文档](./bg-local-goods-partial-update.md#requestgoodsvehiclepropertyrelation) |
| secondHand | OBJECT | 否 | 二手商品信息 → [partial 文档](./bg-local-goods-partial-update.md#requestsecondhand) |
| modifyId | STRING | 否 | 商品信息修改 ID；goods 唯一，后续可凭此 ID 查审核结果 |

> **勿**使用发品接口字段名（`productName`、`carouselImageUrls`、`productPropertyReqs` 等）。`skuList` 放在 `request` 下，**不要**放进 `goodsBasic`。

#### goodsBasic

仅包含 **商品基本信息** 相关字段（Partner 文档中 `goodsBasic` 子树）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| goodsName | STRING | 否 | 商品名称 |
| goodsGallery | OBJECT | 否 | 商品图库，见下 |
| importDesignation | STRING | 否 | 进口标识枚举：`Imported` / `Made in the USA` / `Made in the USA and Imported` / `Made in the USA or Imported` |

##### `goodsBasic.goodsGallery`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| detailVideo | OBJECT | 否 | 详情视频：`vid`、`videoUrl` |
| goodsCarouselImage | STRING[] | 否 | 商品轮播图 |
| detailImage | STRING[] | 否 | 商品详情图 |
| carouselVideo | OBJECT | 否 | 轮播视频：`vid`、`videoUrl` |

#### request.goodsServicePromise

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| shipmentLimitDay | INTEGER | 否 | 备货时间（天）；可选 `1`、`2` |
| fulfillmentType | INTEGER | 否 | `1`=商家自配送，`2`=平台配送 |
| costTemplateId | STRING | 否 | 运费模板 ID |

#### request.goodsProperty

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| goodsProperties | OBJECT[] | 否 | 商品属性列表 |

**`goodsProperties[]`**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| vid | LONG | 否 | 非自定义规格值时须传 vid |
| value | STRING | 否 | 属性值 |
| valueUnit | STRING | 否 | 属性值单位 |
| valueUnitId | LONG | 否 | 属性值单位 ID |
| templatePid | LONG | 否 | 模板属性 ID |
| parentSpecId | LONG | 否 | 非销售属性可不填 |
| specId | LONG | 否 | 非销售属性可不填 |
| note | STRING | 否 | 备注 |
| imgUrl | STRING | 否 | 图片 URL |
| groupId | INTEGER | 否 | 属性值分组 ID |
| refPid | LONG | 否 | 参考属性 ID |
| numberInputValue | STRING | 否 | 数字输入 |

#### request.goodsOriginInfo

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| originRegion1 | STRING | 否 | 一级地址（国家或地区） |
| originRegion2 | STRING | 否 | 二级地址；**一级地址为中国时必填** |
| agreeDefaultOriginRegion | BOOLEAN | 否 | 默认 `false` |
| proofImageUrls | STRING[] | 否 | 产地标签实拍 |
| labelManufacturerProofImageUrls | STRING[] | 否 | 标签特写，最多 5 张 |

#### request.guideFileInfo

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| lang2GuideFileUrl | MAP | 否 | 语言 → PDF URL；**须含英文** |

#### request.goodsSizeChartList

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| goodsSizeChartList | OBJECT[] | 否 | 多套尺码表（套装） |

**数组元素：** `classId`、`meta`、`groups[]`（`id`、`name`、`elements[]`、`records[]`、`values[]`）、`bodyMeta`、`bodyRecords[]`。

#### request.skuList[]

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| skuId | LONG | 条件 | **修改 SKU 必填**；**新增 SKU 勿传** |
| basePrice | OBJECT | 条件 | **修改勿传**；**新增必填** `{ amount, currency }` |
| listPrice | OBJECT | 否 | 须高于 basePrice |
| listPriceType | INTEGER | 否 | 空或 `0` 时必须填 listPrice |
| quantity | LONG | 条件 | **修改勿传**；**新增必填** |
| specIdList | LONG[] | 条件 | **修改勿传**；**新增必填** |
| outSkuSn | STRING | 否 | 修改时可选；不传保留，传 `""` 清空 |
| weight | STRING | **是** | 重量 |
| weightUnit | STRING | **是** | 重量单位 |
| length / width / height | STRING | **是** | 尺寸 |
| volumeUnit | STRING | **是** | 体积单位 |
| images | STRING[] | **是** | 图片列表 |
| multiplePackage | OBJECT | 否 | 包装规格字段：`skuClassification`、`mixedSetType`、`numberOfPieces`、`pieceUnitCode`、`originNetContentNumber`、`originTotalNetContentNumber`、`netContentUnitCode`、`individuallyPacked` |

#### request.goodsTrademark

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| brandId | LONG | 否 | 品牌 ID |
| trademarkId | LONG | 否 | 商标 ID |
| noTrademark | BOOLEAN | 否 | 默认 `false` |

#### request.goodsVehiclePropertyRelation

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| relationId | LONG | 否 | relationType=`1` 时查兼容车型库 |
| ktype | LONG[] | 否 | K-type 映射 |
| leafPropertyValueDependencyIdList | LONG[] | 否 | 末级属性值 dependency id |

#### request.secondHand

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| secondHandGoods | BOOLEAN | 否 | 是否二手商品 |
| level | INTEGER | 否 | 成色状态 |

#### 嵌套字段补充

以下为对象的嵌套字段；未明确的类型或子字段必填性不作推测，适用条件继承对应父字段。

| 字段路径 | 类型 | 必填 | 说明 |
|------|------|------|------|
| request.goodsBasic.goodsGallery.detailVideo.vid | 未明确 | 继承父对象条件；子字段必填性未明确 | 视频 ID。 |
| request.goodsBasic.goodsGallery.detailVideo.videoUrl | 未明确 | 继承父对象条件；子字段必填性未明确 | 视频 URL。 |
| request.goodsBasic.goodsGallery.carouselVideo.vid | 未明确 | 继承父对象条件；子字段必填性未明确 | 视频 ID。 |
| request.goodsBasic.goodsGallery.carouselVideo.videoUrl | 未明确 | 继承父对象条件；子字段必填性未明确 | 视频 URL。 |
| request.skuList[].basePrice.amount | 未明确 | 继承父对象条件；子字段必填性未明确 | 金额，单位未明确。 |
| request.skuList[].basePrice.currency | 未明确 | 继承父对象条件；子字段必填性未明确 | 币种。 |
| request.skuList[].listPrice.amount | 未明确 | 继承父对象条件；子字段必填性未明确 | 金额，单位未明确。 |
| request.skuList[].listPrice.currency | 未明确 | 继承父对象条件；子字段必填性未明确 | 币种。 |
| request.skuList[].length | STRING | 是 | 长、宽、高之一，单位由 volumeUnit 指定。 |
| request.skuList[].width | STRING | 是 | 长、宽、高之一，单位由 volumeUnit 指定。 |
| request.skuList[].height | STRING | 是 | 长、宽、高之一，单位由 volumeUnit 指定。 |
| request.skuList[].multiplePackage.skuClassification | 未明确 | 继承父对象条件；子字段必填性未明确 | SKU 分类。 |
| request.skuList[].multiplePackage.mixedSetType | 未明确 | 继承父对象条件；子字段必填性未明确 | 混合套装类型。 |
| request.skuList[].multiplePackage.numberOfPieces | 未明确 | 继承父对象条件；子字段必填性未明确 | 件数。 |
| request.skuList[].multiplePackage.pieceUnitCode | 未明确 | 继承父对象条件；子字段必填性未明确 | 件数单位代码。 |
| request.skuList[].multiplePackage.originNetContentNumber | 未明确 | 继承父对象条件；子字段必填性未明确 | 原始净含量。 |
| request.skuList[].multiplePackage.originTotalNetContentNumber | 未明确 | 继承父对象条件；子字段必填性未明确 | 原始总净含量。 |
| request.skuList[].multiplePackage.netContentUnitCode | 未明确 | 继承父对象条件；子字段必填性未明确 | 净含量单位代码。 |
| request.skuList[].multiplePackage.individuallyPacked | 未明确 | 继承父对象条件；子字段必填性未明确 | 是否独立包装。 |
| request.goodsSizeChartList.goodsSizeChartList[].classId | 未明确 | 继承父对象条件；子字段必填性未明确 | 尺码表分类 ID。 |
| request.goodsSizeChartList.goodsSizeChartList[].meta | 未明确 | 继承父对象条件；子字段必填性未明确 | 尺码表元数据。 |
| request.goodsSizeChartList.goodsSizeChartList[].bodyMeta | 未明确 | 继承父对象条件；子字段必填性未明确 | 身体数据元信息。 |
| request.goodsSizeChartList.goodsSizeChartList[].bodyRecords[] | 未明确 | 继承父对象条件；子字段必填性未明确 | 身体数据记录。 |
| request.goodsSizeChartList.goodsSizeChartList[].groups[].id | 未明确 | 继承父对象条件；子字段必填性未明确 | 尺码表分组 ID。 |
| request.goodsSizeChartList.goodsSizeChartList[].groups[].name | 未明确 | 继承父对象条件；子字段必填性未明确 | 分组名称。 |
| request.goodsSizeChartList.goodsSizeChartList[].groups[].elements[] | 未明确 | 继承父对象条件；子字段必填性未明确 | 分组元素。 |
| request.goodsSizeChartList.goodsSizeChartList[].groups[].records[] | 未明确 | 继承父对象条件；子字段必填性未明确 | 分组记录。 |
| request.goodsSizeChartList.goodsSizeChartList[].groups[].values[] | 未明确 | 继承父对象条件；子字段必填性未明确 | 分组值。 |

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

| 参数 | 类型 | 说明 |
|------|------|------|
| success | BOOLEAN | 是否成功 |
| errorCode | INTEGER | 错误码 |
| errorMsg | STRING | 错误信息 |
| result.goodsId | LONG | 商品 ID |
| result.productType | INTEGER | `1` 普通商品，`2` 定制商品，`3` 按单生产商品 |
| result.skuInfoList | OBJECT[] | SKU 信息列表 |

**`result.skuInfoList[]`**

| 参数 | 类型 | 说明 |
|------|------|------|
| skuId | LONG | SKU 编号 |
| outSkuSn | STRING | 外部 SKU 编码 |
| specList | OBJECT[] | 规格信息 |
| specList[].specId | LONG | 规格 ID |
| specList[].parentSpecId | LONG | 父规格 ID |

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
  "type": "bg.local.goods.update",
  "params": {
    "request": {
      "goodsId": 123456,
      "language": "en",
      "goodsBasic": {
        "goodsName": "Updated Full Product",
        "goodsGallery": {
          "goodsCarouselImage": [
            "https://..."
          ],
          "detailImage": [
            "https://..."
          ]
        }
      },
      "goodsDesc": "Updated description",
      "skuList": [
        {
          "skuId": 58224724203874,
          "weight": "500",
          "weightUnit": "g",
          "length": "10",
          "width": "10",
          "height": "10",
          "volumeUnit": "cm",
          "images": [
            "https://..."
          ]
        }
      ]
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
