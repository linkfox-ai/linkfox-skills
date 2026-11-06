# 全量编辑 接口说明

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

## 接口：全量编辑（`bg.local.goods.update`）

编辑商品完整属性，包括描述、品牌、图片和属性。

> 与 [partial.update](./bg-local-goods-partial-update.md) 共用同一 **`request` 顶层结构**（`goodsBasic` 与 `skuList` 等**同级**）。全量更新须提交**完整**商品数据，且 **`skuList` 必填**；建议先 `bg.local.goods.detail.query` 拉详情再改。  
> `goodsBasic`、`goodsProperty`、`skuList[]` 等**嵌套字段定义**见 [partial.update](./bg-local-goods-partial-update.md) 对应章节（结构一致）。

> Partner EU 文档：https://partner-eu.temu.com/documentation?menu_code=7289390cfd724be4a196f11ebe45a896&sub_menu_code=9ec69ff253ff4403bed421ca114144ef

对应脚本：`scripts/eu_manage_goods_update.py`；从技能根目录运行。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/proxy`

转发 path：`/temu/proxy` → 上游 `/openapi/router`，Body `type=bg.local.goods.update`；`type` 不拼入 URL。

### 请求参数

#### 网关 POST Body

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| site | string | 是 | 欧洲站为 `eu`，EU 脚本默认 `eu`；通用脚本须显式传入。兼容 `cn`、`partner`、`us`、`global`。 |
| managementType | string | 是 | EU 脚本默认 `semi-managed`；通用脚本须显式传入。可选 `full-managed`、`semi-managed`。 |
| accessToken | string | 与 storeKey 二选一 | Temu 店铺令牌；脚本优先直接使用，或按本地 storeKey 查出后填入网关 Body。 |
| storeKey | string | 与 accessToken 二选一 | 本地令牌库的店铺键；脚本结合 site、managementType、tokenPurpose 查找，不将 storeKey 发到网关。 |
| tokenPurpose | string | 否 | EU 脚本查找本地令牌时默认 `product-inventory`，通用脚本默认 `default`；建议商品库存使用 `product-inventory`。此项用于本地查找。 |
| type | string | 是 | 本接口的 Temu 操作名，见上方调用规范；不是 URL 路径。专用脚本固定该值。 |
| params | object | 否 | Temu 业务载荷，通常为 `{ "request": { ... } }`，完整字段见下文。 |

#### 脚本参数与兼容约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| token / linkfoxToken / linkfox_token | string | 否 | LinkFox 用户密钥，按此顺序优先于环境变量 `LINKFOX_AGENT_API_KEY`、`LINKFOXAGENT_API_KEY`；与 Temu accessToken 分开。不会作为业务字段转发。 |
| request | object | 否 | 专用脚本可在 JSON 顶层传入此业务对象，也可放在 `params.request`；显式 object 类型的 params 优先，支持顶层业务字段透传。官方 request 为选填包装，内部必填项仍按下表执行。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 本技能不启用响应缓存；业务封装始终向公共 run 加入此选项，不读取或写入响应缓存。公共调用器可能创建空缓存目录。 |

兼容请求头 `Authorization` 与 `Token` 同值，以及 SESSION_ID、MESSAGE_ID、MODE_ID、APP_NAME 透传。网关地址依次取 `LINKFOX_TOOL_GATEWAY`、`TEMU_API_BASE_URL`、`STORE_API_BASE_URL`，默认正式网关。HTTP 超时为 150 秒。输出保存在当前工作目录，不可写则在请求前报错，不回退到家目录或临时目录。专用脚本接受 JSON 参数及 `--inline`，兼容 `--no-cache`；通用脚本保留站点与托管类型校验。

#### Temu 业务参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| request | OBJECT | 否 | 官方顶层业务请求包装；子字段的必填要求见下文。 |

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

#### `request` 内字段一览

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| language | STRING | 否 | 语言 |
| goodsId | LONG | **是** | 商品编号 |
| goodsBasic | OBJECT | 否 | 商品基础信息 → [goodsBasic](#goodsbasic) |
| goodsServicePromise | OBJECT | 否 | 商品服务承诺 → [partial 文档](#requestgoodsservicepromise) |
| goodsProperty | OBJECT | 否 | 商品属性 → [partial 文档](#requestgoodsproperty) |
| goodsOriginInfo | OBJECT | 否 | 原产国家/地区 → [partial 文档](#requestgoodsorigininfo) |
| bulletPoints | STRING[] | 否 | 商品卖点 |
| goodsDesc | STRING | 否 | 商品描述 |
| guideFileInfo | OBJECT | 否 | 说明文件信息 → [partial 文档](#requestguidefileinfo) |
| goodsSizeChartList | OBJECT | 否 | 商品尺码表 → [partial 文档](#requestgoodssizechartlist) |
| goodsSizeImage | STRING[] | 否 | 尺码表图片 URL |
| skuList | OBJECT[] | **是** | SKU 列表 → [partial 文档](#requestskulist) |
| goodsTrademark | OBJECT | 否 | 商品商标 → [partial 文档](#requestgoodstrademark) |
| goodsVehiclePropertyRelation | OBJECT | 否 | 车型数据 → [partial 文档](#requestgoodsvehiclepropertyrelation) |
| secondHand | OBJECT | 否 | 二手信息 → [partial 文档](#requestsecondhand) |
| modifyId | STRING | 否 | 商品信息修改 ID；goods 唯一，后续可凭此 ID 查审核结果 |

> **勿**使用发品接口字段名（`productName`、`carouselImageUrls`、`productPropertyReqs` 等）。`skuList` 放在 `request` 下，**不要**放进 `goodsBasic`。

#### 全量编辑嵌套结构

全量编辑与部分编辑使用相同的嵌套字段定义；全量编辑需提交完整数据及完整 SKU 列表，且不包含 saveMode。

<a id="goodsbasic"></a>

#### goodsBasic

仅包含 **商品基础信息** 相关字段（Partner 文档中 `goodsBasic` 子树）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| goodsName | STRING | 否 | 商品名称 |
| goodsGallery | OBJECT | 否 | 商品图库，见下 |
| importDesignation | STRING | 否 | `Imported` / `Made in the USA` / `Made in the USA and Imported` / `Made in the USA or Imported` |

<a id="goodsbasicgoodsgallery"></a>

#### `goodsBasic.goodsGallery`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| detailVideo | OBJECT | 否 | 详情视频：`vid`、`videoUrl` |
| goodsCarouselImage | STRING[] | 否 | 商品轮播图 |
| detailImage | STRING[] | 否 | 商品详情图 |
| carouselVideo | OBJECT | 否 | 轮播视频：`vid`、`videoUrl` |

<a id="requestgoodsservicepromise"></a>

#### request.goodsServicePromise

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| shipmentLimitDay | INTEGER | 否 | 备货时间（天）；可选 `1`、`2` |
| fulfillmentType | INTEGER | 否 | `1`=自行配送，`2`=平台配送 |
| costTemplateId | STRING | 否 | 运费模板 ID |

<a id="requestgoodsproperty"></a>

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
| numberInputValue | STRING | 否 | 数字输入 |

<a id="requestgoodsorigininfo"></a>

#### request.goodsOriginInfo

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| originRegion1 | STRING | 否 | 一级地址（国家或地区） |
| originRegion2 | STRING | 否 | 二级地址；**一级地址为 China 时必填** |
| agreeDefaultOriginRegion | BOOLEAN | 否 | 默认 `false` |
| proofImageUrls | STRING[] | 否 | 产地标签实拍 |
| labelManufacturerProofImageUrls | STRING[] | 否 | 标签特写，最多 5 张 |

<a id="requestguidefileinfo"></a>

#### request.guideFileInfo

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| lang2GuideFileUrl | MAP | 否 | 语言 → PDF URL；**须含英文** |

<a id="requestgoodssizechartlist"></a>

#### request.goodsSizeChartList

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| goodsSizeChartList | OBJECT[] | 否 | 多套尺码表（套装） |

尺码表数组元素及分组字段见下方嵌套字段表。

<a id="requestskulist"></a>

#### request.skuList[]

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| skuId | LONG | 条件 | **修改 SKU 必填**；**新增 SKU 勿传** |
| basePrice | OBJECT | 条件 | **修改勿传**；**新增必填**；金额和币种字段见下方嵌套字段表。 |
| listPrice | OBJECT | 否 | 须高于 `basePrice` |
| listPriceType | INTEGER | 否 | 空或 `0` 时必须填 `listPrice` |
| quantity | LONG | 条件 | **修改勿传**；**新增必填** |
| specIdList | LONG[] | 条件 | **修改勿传**；**新增必填** |
| outSkuSn | STRING | 否 | 修改时可选；不传保留，传 `""` 清空 |
| weight | STRING | **是** | 重量 |
| weightUnit | STRING | **是** | 重量单位 |
| length / width / height | STRING | **是** | 尺寸 |
| volumeUnit | STRING | **是** | 体积单位 |
| images | STRING[] | **是** | 图片 |
| multiplePackage | OBJECT | 否 | SKU 包装信息，子字段见下方嵌套字段表。 |

<a id="requestgoodstrademark"></a>

#### request.goodsTrademark

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| brandId | LONG | 否 | 品牌 ID |
| trademarkId | LONG | 否 | 商标 ID |
| noTrademark | BOOLEAN | 否 | 默认 `false` |

<a id="requestgoodsvehiclepropertyrelation"></a>

#### request.goodsVehiclePropertyRelation

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| relationId | LONG | 否 | relationType=`1` 时查兼容车型库 |
| ktype | LONG[] | 否 | K-type 映射 |
| leafPropertyValueDependencyIdList | LONG[] | 否 | 末级属性值依赖 ID |

<a id="requestsecondhand"></a>

#### request.secondHand

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| secondHandGoods | BOOLEAN | 否 | 是否为二手商品 |
| level | INTEGER | 否 | 成色 |

#### 嵌套字段

下表列出嵌套字段；类型或必填性未限定的字段，以实际接口要求为准，不凭示例推断约束。

| 字段路径 | 类型 | 必填 | 说明 |
|------|------|------|------|
| request.goodsBasic.goodsGallery.detailVideo.vid | 未限定 | 未限定 | 视频标识。 |
| request.goodsBasic.goodsGallery.detailVideo.videoUrl | 未限定 | 未限定 | 视频 URL。 |
| request.goodsBasic.goodsGallery.carouselVideo.vid | 未限定 | 未限定 | 轮播视频标识。 |
| request.goodsBasic.goodsGallery.carouselVideo.videoUrl | 未限定 | 未限定 | 轮播视频 URL。 |
| request.goodsSizeChartList.goodsSizeChartList[].classId | 未限定 | 未限定 | 尺码表分类标识。 |
| request.goodsSizeChartList.goodsSizeChartList[].meta | 未限定 | 未限定 | 尺码表元信息。 |
| request.goodsSizeChartList.goodsSizeChartList[].groups | 数组（元素类型未单列） | 未限定 | 尺码分组。 |
| request.goodsSizeChartList.goodsSizeChartList[].groups[].id | 未限定 | 未限定 | 分组标识。 |
| request.goodsSizeChartList.goodsSizeChartList[].groups[].name | 未限定 | 未限定 | 分组名称。 |
| request.goodsSizeChartList.goodsSizeChartList[].groups[].elements | 数组（元素类型未单列） | 未限定 | 分组元素。 |
| request.goodsSizeChartList.goodsSizeChartList[].groups[].records | 数组（元素类型未单列） | 未限定 | 分组记录。 |
| request.goodsSizeChartList.goodsSizeChartList[].groups[].values | 数组（元素类型未单列） | 未限定 | 分组值。 |
| request.goodsSizeChartList.goodsSizeChartList[].bodyMeta | 未限定 | 未限定 | 身体尺寸元信息。 |
| request.goodsSizeChartList.goodsSizeChartList[].bodyRecords | 数组（元素类型未单列） | 未限定 | 身体尺寸记录。 |
| request.skuList[].basePrice.amount | 未限定 | 未限定 | 基础价格金额，与 currency 组成价格对象。 |
| request.skuList[].basePrice.currency | 未限定 | 未限定 | 基础价格币种。 |
| request.skuList[].multiplePackage.skuClassification | 未限定 | 未限定 | SKU 包装分类。 |
| request.skuList[].multiplePackage.mixedSetType | 未限定 | 未限定 | 混合套装类型。 |
| request.skuList[].multiplePackage.numberOfPieces | 未限定 | 未限定 | 件数。 |
| request.skuList[].multiplePackage.pieceUnitCode | 未限定 | 未限定 | 件数单位编码。 |
| request.skuList[].multiplePackage.originNetContentNumber | 未限定 | 未限定 | 原始净含量。 |
| request.skuList[].multiplePackage.originTotalNetContentNumber | 未限定 | 未限定 | 原始总净含量。 |
| request.skuList[].multiplePackage.netContentUnitCode | 未限定 | 未限定 | 净含量单位编码。 |
| request.skuList[].multiplePackage.individuallyPacked | 未限定 | 未限定 | 是否独立包装。 |

### 响应结构

#### 网关与脚本响应

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 网关状态码，按基础规则判断；不存在或空值不代替业务结果判断。 |
| errmsg | string | 网关错误说明，以实际返回为准。 |
| body | string | Temu 原始 JSON 字符串，保留原文。 |
| code | integer | 网关业务错误码：`1002` 为参数或 LinkFox Token 问题，`1003` 为转发失败；未定义的 code 不擅自推断为成功。 |
| temuBody | object / array / scalar / null | 脚本对非空且合法 JSON 的 body 解析后追加；解析失败保留 body，不添加此字段。下文为 Temu 对象响应的字段。 |
| transportHttpStatus | integer / null | 脚本追加的 LinkFox HTTP 状态；连接失败时为 null。 |
| error | string | 连接失败或无法解析的 HTTP 错误消息，仅出现时返回。 |
| details | string | 无法解析的 HTTP 错误原文，仅出现时返回。 |

#### Temu 业务响应

| 参数 | 类型 | 说明 |
|------|------|------|
| success | BOOLEAN | 当前请求是否成功 |
| errorCode | INTEGER | 错误码 |
| errorMsg | STRING | 错误信息 |
| result.goodsId | LONG | 商品 ID |
| result.productType | INTEGER | `1` 普通商品，`2` 定制商品，`3` 按单生产商品 |
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

- 网关基础规则通过后，继续检查网关业务 `code`；`1002` 时修正参数与 LinkFox Token，`1003` 时检查 Temu token、IP 白名单与网络。
- 再解析 `body`，检查 Temu `success`、`errorCode`、`errorMsg` 和 `result`。Temu 的 `errorCode=0` 与网关 `errcode=0` 是不同层级，不能混用；body 无法解析时保留原文，不能宣称操作成功。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/temu/proxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Token: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "site": "eu",
  "managementType": "semi-managed",
  "accessToken": "TEMU_EU_TOKEN",
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
  "skillName": "linkfox-temu-manage-product-eu",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
