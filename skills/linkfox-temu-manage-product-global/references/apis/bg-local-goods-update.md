# Temu 全球站商品管理接口说明

[公共运行约定](../api.md#运行约定) · [完整接口索引](README.md)

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

## 接口：全量编辑 — `bg.local.goods.update`

提交商品完整属性，例如描述、品牌、图片和属性。

> Partner 文档：https://partner-global.temu.com/documentation?menu_code=fb16b05f7a904765aac4af3a24b87d4a&sub_menu_code=b05f4b7598fb4dc7ac47c864aa5d5fc4
> 部分 sub_menu_code 使用 US 文档编号；须在 Global Partner 后台按 type 核对，索引链接不代表地址已实时校验。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/proxy`

### 请求参数

#### 网关 POST Body

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| site | string | 是 | 本技能默认 `global`，全球区（非 US/EU）；由网关选择上游 `https://openapi-b-global.temu.com/openapi/router`。兼容脚本可显式指定 `cn` / `partner` / `us` / `global` / `eu`，须与实际授权区域一致。 |
| managementType | string | 是 | 本技能默认 `semi-managed`；通用脚本支持 `full-managed` / `semi-managed`。 |
| accessToken | string | 是 | Temu 店铺令牌；与 LinkFox 用户密钥不同。使用 `storeKey` 时由业务脚本读取本地令牌并转换为此字段。 |
| type | string | 是 | 本接口固定 `bg.local.goods.update`。 |
| params | object | 否 | 本接口业务载荷；通常为 `{"request": {...}}`，具体结构见下文。 |

#### 脚本兼容参数与选项

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| token / linkfoxToken / linkfox_token | string | 否 | 仅脚本鉴权参数，按所列顺序取首个非空值，优先于环境变量；不转发到 Temu 业务参数。 |
| LINKFOX_AGENT_API_KEY / LINKFOXAGENT_API_KEY | 环境变量 | 无 JSON 密钥时必填 | 优先使用前者，同时支持两个变量；`Authorization` 与 `Token` 请求头同值。 |
| storeKey | string | 与 accessToken 二选一 | 从本地 store 取 Temu 令牌；直接传入 accessToken 时优先使用该值。 |
| tokenPurpose | string | 否 | Global 包装默认 `product-inventory`；与 storeKey、site、managementType 一起精确匹配，不回退到其他区域或用途的令牌。 |
| params | object | 否 | 显式传入时优先使用整个 params；否则将顶层除鉴权、店铺、站点、type、params 外的字段作为业务载荷。 |
| --inline | CLI flag | 否 | 完整打印响应，仍保存文件。 |
| --no-cache | CLI flag | 否 | 本技能不使用响应缓存，业务包装调用 run 时始终添加此选项，不读写响应缓存。 |

Global 脚本自动补全站点、管理模式和令牌用途；`temu_proxy.py` 兼容入口要求显式传 site、managementType 和 type。业务载荷保持原始层级，不自动展平 request。授权步骤和本地令牌 CLI 见 [access-token.md](../access-token.md)。

#### 业务包装

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| params.request | OBJECT | 否 | 业务请求包装为选填，内部必填字段仍按下表执行。 |

> 与 [partial.update](./bg-local-goods-partial-update.md) 共用同一 **`request` 顶层结构**（`goodsBasic` 与 `skuList` 等**同级**）。全量更新须提交**完整**商品数据，且 **`skuList` 必填**；建议先 `bg.local.goods.detail.query` 拉详情再改。
> `goodsBasic`、`goodsProperty`、`skuList[]` 等嵌套字段定义见本页下方各表；结构与局部编辑一致。

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
| goodsBasic | OBJECT | 否 | 商品基础信息 → [goodsBasic](#goodsbasic) |
| goodsServicePromise | OBJECT | 否 | 商家服务承诺 → [partial 文档](#requestgoodsservicepromise) |
| goodsProperty | OBJECT | 否 | 商品属性 → [partial 文档](#requestgoodsproperty) |
| goodsOriginInfo | OBJECT | 否 | 原产国家或地区 → [partial 文档](#requestgoodsorigininfo) |
| bulletPoints | STRING[] | 否 | 商品卖点 |
| goodsDesc | STRING | 否 | 商品描述 |
| guideFileInfo | OBJECT | 否 | 指南文件信息 → [partial 文档](#requestguidefileinfo) |
| goodsSizeChartList | OBJECT | 否 | 商品尺码表列表 → [partial 文档](#requestgoodssizechartlist) |
| goodsSizeImage | STRING[] | 否 | 尺码表图片 URL |
| skuList | OBJECT[] | **是** | SKU 列表 → [partial 文档](#requestskulist) |
| goodsTrademark | OBJECT | 否 | 商品商标 → [partial 文档](#requestgoodstrademark) |
| goodsVehiclePropertyRelation | OBJECT | 否 | 车型数据 → [partial 文档](#requestgoodsvehiclepropertyrelation) |
| secondHand | OBJECT | 否 | 二手商品信息 → [partial 文档](#requestsecondhand) |
| modifyId | STRING | 否 | 商品信息修改 ID；goods 唯一，后续可凭此 ID 查审核结果 |

> **勿**使用发品接口字段名（`productName`、`carouselImageUrls`、`productPropertyReqs` 等）。`skuList` 放在 `request` 下，**不要**放进 `goodsBasic`。

#### goodsBasic

仅包含**商品基础信息**相关字段（Partner 文档中 `goodsBasic` 子树）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| goodsName | STRING | 否 | 商品名称 |
| goodsGallery | OBJECT | 否 | 商品图库，见下 |
| importDesignation | STRING | 否 | `Imported` / `Made in the USA` / `Made in the USA and Imported` / `Made in the USA or Imported` |

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
| shipmentLimitDay | INTEGER | 否 | 备货天数；可选 `1`、`2` |
| fulfillmentType | INTEGER | 否 | `1`=Self-Delivery，`2`=Platform Delivery |
| costTemplateId | STRING | 否 | 配送模板 ID |

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
| refPid | LONG | 否 | 引用属性 ID |
| numberInputValue | STRING | 否 | 数值输入 |

#### request.goodsOriginInfo

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| originRegion1 | STRING | 否 | 一级地址（国家或地区） |
| originRegion2 | STRING | 否 | 二级地址；**一级地址为 China 时必填** |
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
| images | STRING[] | **是** | 图片 |
| multiplePackage | OBJECT | 否 | `skuClassification`、`mixedSetType`、`numberOfPieces`、`pieceUnitCode`、`originNetContentNumber`、`originTotalNetContentNumber`、`netContentUnitCode`、`individuallyPacked` |

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
| level | INTEGER | 否 | 成色 |

#### 其他嵌套字段定义

下表列出以 request 为根的嵌套字段路径；未明确的类型、必填性和语义以接口实际定义为准，不推测补造。

| 字段路径 | 类型 | 必填 | 说明 |
|------|------|------|------|
| goodsBasic.goodsGallery.detailVideo.vid / goodsBasic.goodsGallery.carouselVideo.vid | 未明确 | 未明确 | 视频 ID。 |
| goodsBasic.goodsGallery.detailVideo.videoUrl / goodsBasic.goodsGallery.carouselVideo.videoUrl | 未明确 | 未明确 | 视频 URL。 |
| skuList[].basePrice.amount | 未明确 | 未明确 | 金额；新增 SKU 的 basePrice 必填，修改时不传。 |
| skuList[].basePrice.currency | 未明确 | 未明确 | 币种；新增 SKU 的 basePrice 必填，修改时不传。 |
| goodsSizeChartList.goodsSizeChartList[].classId | 未明确 | 未明确 | 尺码表分类 ID。 |
| goodsSizeChartList.goodsSizeChartList[].meta | 未明确 | 未明确 | 尺码表元信息。 |
| goodsSizeChartList.goodsSizeChartList[].groups | array | 未明确 | 尺码分组。 |
| goodsSizeChartList.goodsSizeChartList[].groups[].id / goodsSizeChartList.goodsSizeChartList[].groups[].name | 未明确 | 未明确 | 分组标识与名称。 |
| goodsSizeChartList.goodsSizeChartList[].groups[].elements / goodsSizeChartList.goodsSizeChartList[].groups[].records / goodsSizeChartList.goodsSizeChartList[].groups[].values | array | 未明确 | 元素、记录、值数组。 |
| goodsSizeChartList.goodsSizeChartList[].bodyMeta | 未明确 | 未明确 | 身体尺码元信息。 |
| goodsSizeChartList.goodsSizeChartList[].bodyRecords | array | 未明确 | 身体尺码记录。 |
| skuList[].multiplePackage.skuClassification | 未明确 | 未明确 |  SKU 分类字段。 |
| skuList[].multiplePackage.mixedSetType | 未明确 | 未明确 | 混合套装类型。 |
| skuList[].multiplePackage.numberOfPieces | 未明确 | 未明确 | 件数字段。 |
| skuList[].multiplePackage.pieceUnitCode | 未明确 | 未明确 | 件数单位代码。 |
| skuList[].multiplePackage.originNetContentNumber | 未明确 | 未明确 | 原净含量数值。 |
| skuList[].multiplePackage.originTotalNetContentNumber | 未明确 | 未明确 | 原总净含量数值。 |
| skuList[].multiplePackage.netContentUnitCode | 未明确 | 未明确 | 净含量单位代码。 |
| skuList[].multiplePackage.individuallyPacked | 未明确 | 未明确 | 独立包装字段。 |

### 响应结构

#### 网关与脚本输出字段

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 网关业务状态；按公共规则判断。未出现时仍须结合外层 HTTP 状态与下列业务字段。 |
| errmsg | string | 网关错误或提示消息。 |
| code | integer | 网关错误码：1002 表示参数或 LinkFox Token 无效，1003 表示转发失败；不能替代外层 HTTP/errcode 判断。 |
| body | string | Temu 原始 JSON 字符串；保留原文。 |
| temuBody | object / array / scalar | 脚本附加字段，仅当 body 为可解析 JSON 字符串时生成；解析仅用于展示，不代表业务成功。 |

下面的字段以解析后的 Temu body 为作用域；未展开定义的子对象按实际返回解释，不推测补造字段。

| 参数 | 类型 | 说明 |
|------|------|------|
| success | BOOLEAN | 是否成功 |
| errorCode | INTEGER | 错误码 |
| errorMsg | STRING | 错误信息 |
| result | OBJECT | 编辑结果对象。 |
| result.goodsId | LONG | 商品 ID |
| result.productType | INTEGER | `1` 普通商品（Normal），`2` 定制商品（Custom），`3` 按单生产商品（Made-to-order） |
| result.skuInfoList | OBJECT[] | SKU 信息列表 |

**`result.skuInfoList[]`**

| 参数 | 类型 | 说明 |
|------|------|------|
| skuId | LONG | SKU ID |
| outSkuSn | STRING | 外部 SKU 编码 |
| specList | OBJECT[] | 规格信息 |
| specList[].specId | LONG | 规格 ID |
| specList[].parentSpecId | LONG | 父规格 ID |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 基础规则通过后，核对网关 code，再检查 body 中的 success、errorCode、errorMsg 与 result。仅 body 解析成功不能认定操作成功。
- code=1002 时核对参数与 LinkFox 用户令牌；code=1003 时核对 Temu 店铺令牌、IP 白名单与转发情况。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/temu/proxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Token: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "site": "global",
  "managementType": "semi-managed",
  "accessToken": "TOKEN",
  "type": "bg.local.goods.update",
  "params": {
    "request": {
      "goodsId": 123456,
      "goodsBasic": {
        "goodsName": "Full Title",
        "goodsGallery": {
          "goodsCarouselImage": [
            "https://..."
          ]
        }
      },
      "goodsProperty": {
        "goodsProperties": [
          {
            "vid": 100,
            "value": "Cotton"
          }
        ]
      },
      "skuList": [
        {
          "skuId": 999,
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
  "skillName": "linkfox-temu-manage-product-global",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
