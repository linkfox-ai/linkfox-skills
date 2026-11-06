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

## 接口：商品详情 — `bg.local.goods.detail.query`

> Partner 文档：https://partner-global.temu.com/documentation?menu_code=fb16b05f7a904765aac4af3a24b87d4a&sub_menu_code=9ebbd5d269014322ad4a6c123b1dfdae
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
| type | string | 是 | 本接口固定 `bg.local.goods.detail.query`。 |
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
| `2` | 拉取**线上在售**快照（编辑前的 live 版本），**默认** |

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

> **注意**：详情 **Response** 的 `result` 为**扁平结构**（字段直接在 `result` 下），与 **update 请求** 中包在 `request.goodsBasic` 内的层级**不同**。改商品时请按 [partial.update](./bg-local-goods-partial-update.md) / [update](./bg-local-goods-update.md) 的 **Request** 结构组装。

| 参数 | 类型 | 说明 |
|------|------|------|
| goodsId | LONG | 商品 ID |
| catId | LONG | 叶子类目 ID（须与 category version 对应类目树一致） |
| subStatus | INTEGER | 商品草稿状态 |
| goodsName | STRING | 商品名称 |
| goodsDesc | STRING | 商品描述 |
| bulletPoints | STRING[] | 商品卖点 |
| customized | BOOLEAN | 是否定制商品 |
| productType | INTEGER | `1` 普通商品（Normal），`2` 定制商品（Custom），`3` 按单生产商品（Made-to-order） |
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
| itemTaxCode | STRING | 税务代码 |
| skuList | OBJECT[] | SKU 提交查询列表 → SKU 元素结构同 [partial.update §skuList](./bg-local-goods-partial-update.md#requestskulist) |
| saveModeStatus | INTEGER | 自动发布到 Temu 的商品卖家审核状态 |

##### `goodsGallery`（响应常见子字段）

与编辑请求一致，见 [partial.update §goodsGallery](./bg-local-goods-partial-update.md#goodsbasicgoodsgallery)：`detailVideo`、`goodsCarouselImage`、`detailImage`、`carouselVideo`。

#### 详情响应嵌套字段

以下字段与编辑侧结构对应；响应没有 request/goodsBasic 包装。SKU 表中的新增/修改约束是写入侧说明，不用于要求响应字段必须出现。

#### result.goodsGallery

| 参数 | 类型 | 说明 |
|------|------|------|
| detailVideo | OBJECT | 详情视频：`vid`、`videoUrl` |
| goodsCarouselImage | STRING[] | 商品轮播图 |
| detailImage | STRING[] | 商品详情图 |
| carouselVideo | OBJECT | 轮播视频：`vid`、`videoUrl` |

#### result.goodsServicePromise

| 参数 | 类型 | 说明 |
|------|------|------|
| shipmentLimitDay | INTEGER | 备货天数；可选 `1`、`2` |
| fulfillmentType | INTEGER | `1`=Self-Delivery，`2`=Platform Delivery |
| costTemplateId | STRING | 配送模板 ID |

#### result.goodsProperties[]

| 参数 | 类型 | 说明 |
|------|------|------|
| vid | LONG | 非自定义规格值时须传 vid |
| value | STRING | 属性值 |
| valueUnit | STRING | 属性值单位 |
| valueUnitId | LONG | 属性值单位 ID |
| templatePid | LONG | 模板属性 ID |
| parentSpecId | LONG | 非销售属性可不填 |
| specId | LONG | 非销售属性可不填 |
| note | STRING | 备注 |
| imgUrl | STRING | 图片 URL |
| groupId | INTEGER | 属性值分组 ID |
| refPid | LONG | 引用属性 ID |
| numberInputValue | STRING | 数值输入 |

#### result.goodsOriginInfo

| 参数 | 类型 | 说明 |
|------|------|------|
| originRegion1 | STRING | 一级地址（国家或地区） |
| originRegion2 | STRING | 二级地址；**一级地址为 China 时必填** |
| agreeDefaultOriginRegion | BOOLEAN | 默认 `false` |
| proofImageUrls | STRING[] | 产地标签实拍 |
| labelManufacturerProofImageUrls | STRING[] | 标签特写，最多 5 张 |

#### result.goodsSizeChartList

| 参数 | 类型 | 说明 |
|------|------|------|
| goodsSizeChartList | OBJECT[] | 多套尺码表（套装） |

#### result.skuList[]

| 参数 | 类型 | 说明 |
|------|------|------|
| skuId | LONG | **修改 SKU 必填**；**新增 SKU 勿传** |
| basePrice | OBJECT | **修改勿传**；**新增必填** `{ amount, currency }` |
| listPrice | OBJECT | 须高于 basePrice |
| listPriceType | INTEGER | 空或 `0` 时必须填 listPrice |
| quantity | LONG | **修改勿传**；**新增必填** |
| specIdList | LONG[] | **修改勿传**；**新增必填** |
| outSkuSn | STRING | 修改时可选；不传保留，传 `""` 清空 |
| weight | STRING | 重量 |
| weightUnit | STRING | 重量单位 |
| length / width / height | STRING | 尺寸 |
| volumeUnit | STRING | 体积单位 |
| images | STRING[] | 图片 |
| multiplePackage | OBJECT | `skuClassification`、`mixedSetType`、`numberOfPieces`、`pieceUnitCode`、`originNetContentNumber`、`originTotalNetContentNumber`、`netContentUnitCode`、`individuallyPacked` |

#### result.goodsTrademark

| 参数 | 类型 | 说明 |
|------|------|------|
| brandId | LONG | 品牌 ID |
| trademarkId | LONG | 商标 ID |
| noTrademark | BOOLEAN | 默认 `false` |

#### result.secondHand

| 参数 | 类型 | 说明 |
|------|------|------|
| secondHandGoods | BOOLEAN | 是否二手商品 |
| level | INTEGER | 成色 |

#### 详情响应的其他嵌套字段

详情嵌套字段与编辑侧结构对应。下列字段以 result 为根；未注明的类型仍保留为未知，响应不受新增或修改 SKU 的请求必填条件约束。

| 字段路径 | 类型 | 说明 |
|------|------|------|
| result.goodsGallery.detailVideo.vid / result.goodsGallery.carouselVideo.vid | 未明确 | 视频 ID。 |
| result.goodsGallery.detailVideo.videoUrl / result.goodsGallery.carouselVideo.videoUrl | 未明确 | 视频 URL。 |
| result.skuList[].basePrice.amount | 未明确 | 金额；类型未明确。 |
| result.skuList[].basePrice.currency | 未明确 | 币种；类型未明确。 |
| result.goodsSizeChartList.goodsSizeChartList[].classId | 未明确 | 尺码表分类 ID。 |
| result.goodsSizeChartList.goodsSizeChartList[].meta | 未明确 | 尺码表元信息。 |
| result.goodsSizeChartList.goodsSizeChartList[].groups | array | 尺码分组。 |
| result.goodsSizeChartList.goodsSizeChartList[].groups[].id / result.goodsSizeChartList.goodsSizeChartList[].groups[].name | 未明确 | 分组标识与名称。 |
| result.goodsSizeChartList.goodsSizeChartList[].groups[].elements / result.goodsSizeChartList.goodsSizeChartList[].groups[].records / result.goodsSizeChartList.goodsSizeChartList[].groups[].values | array | 元素、记录、值数组。 |
| result.goodsSizeChartList.goodsSizeChartList[].bodyMeta | 未明确 | 身体尺码元信息。 |
| result.goodsSizeChartList.goodsSizeChartList[].bodyRecords | array | 身体尺码记录。 |
| result.skuList[].multiplePackage.skuClassification | 未明确 |  SKU 分类字段。 |
| result.skuList[].multiplePackage.mixedSetType | 未明确 | 混合套装类型。 |
| result.skuList[].multiplePackage.numberOfPieces | 未明确 | 件数字段。 |
| result.skuList[].multiplePackage.pieceUnitCode | 未明确 | 件数单位代码。 |
| result.skuList[].multiplePackage.originNetContentNumber | 未明确 | 原净含量数值。 |
| result.skuList[].multiplePackage.originTotalNetContentNumber | 未明确 | 原总净含量数值。 |
| result.skuList[].multiplePackage.netContentUnitCode | 未明确 | 净含量单位代码。 |
| result.skuList[].multiplePackage.individuallyPacked | 未明确 | 独立包装字段。 |

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
  "type": "bg.local.goods.detail.query",
  "params": {
    "request": {
      "goodsId": 123456,
      "versionQueryType": 2
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
