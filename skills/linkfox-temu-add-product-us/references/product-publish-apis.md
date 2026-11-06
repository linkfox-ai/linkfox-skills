# 商品发布 API — 参数参考（V2 Recommended）

文档导航：[网关与运行约定](api.md)、[Partner US 目录](partner-us-catalog.md)。

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

## 接口：发布商品 V2（temu.local.goods.v2.add）

- **Partner 文档分区**：`sub_menu_code=91657460a9be4a609df2eef01bc6deef`
- **脚本**：`scripts/us_goods_add.py`
- **用途**：在美国站创建新商品（V2 推荐发品接口）。与同族 `bg.local.goods.add`、`temu.goods.add` 载荷结构一致或为其超集。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/proxy`

### 请求参数

#### 网关 POST Body

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| site | string | 是 | US 封装默认 `us`；兼容 `cn` / `partner` / `global` / `eu`，按目标店铺授权选择。 |
| managementType | string | 是 | US 封装默认 `semi-managed`；通用脚本支持 `full-managed` / `semi-managed`。 |
| accessToken | string | 与 storeKey 二选一 | Temu 店铺令牌，最长约 8192；直接提供时优先使用。 |
| storeKey | string | 与 accessToken 二选一 | 脚本本地店铺键，解析后发送 accessToken；不发送 storeKey。 |
| tokenPurpose | string | 否 | 本地令牌用途；US 封装默认 `product-inventory`，通用脚本默认 `default`；不发送此字段。 |
| type | string | 是 | 固定 `temu.local.goods.v2.add`，写入 Body，不是 URL 路径。 |
| params | object | 是 | 本接口业务参数，须包含下表的必填项；US 脚本省略空对象的行为不免除必填要求。 |

脚本认证别名、CLI、默认值与本地令牌解析见 [运行约定](api.md#运行约定)。

#### 业务参数（`params`）— 顶层

以下字段来自同族 `bg.local.goods.add` / `temu.goods.add` 发品模型；**具体必填项由类目属性接口返回的 `required` 决定**。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| goodsBasic | object | 是 | 商品基础信息（标题、类目、轮播图等） |
| skuList | array | 是 | SKU 列表（价格、库存、规格、图片等） |
| certificationInfo | object | 否 | 合规/认证（证书、GPSR、实拍图等，类目要求时必填） |
| productPropertyReqs | array | 否 | 普通属性（亦可放在 `goodsBasic` 内，以官方字段为准） |
| productSpecPropertyReqs | array | 否 | 销售规格属性 |
| productSemiManagedReq | object | 否 | 半托管绑定站点等 |
| productShipmentReq | object | 否 | 半托管配送/运费模板 |
| addProductChannelType | integer | 是 | 发品渠道（同族接口必填） |

#### `goodsBasic` 常见字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| catId / leafCatId | integer | 是 | 叶子类目 ID（或 cat1Id…cat10Id 逐级类目，与同族 `temu.goods.add` 一致） |
| productName | string | 是 | 商品标题，通常 1–250 字符 |
| carouselImageUrls | array | 是 | 轮播图 URL 列表（须先 `image.v2.upload`），常 ≥5 张 |
| materialImgUrl | string | 否 | 素材图 URL |
| carouselImageI18nReqs | array | 否 | 多语言轮播图（非服饰类常必填） |
| productOuterPackageImageReqs | array | 否 | 外包装图 |
| productOuterPackageReq | object | 否 | 外包装信息 |
| productPropertyReqs | array | 是 | 类目属性值，元素见下表 |
| productSpecPropertyReqs | array | 条件 | 多规格时的规格属性 |
| productWhExtAttrReq | object | 是 | 仓配扩展（产地、重量体积等） |
| productSaleExtAttrReq | object | 否 | 销售扩展 |
| productSkcReqs | array | 是 | SKC 维度数据（含 SKU 列表） |
| sizeTemplateIds | array | 否 | 尺码表模板 ID，无尺码传 `[]` |
| showSizeTemplateIds | array | 否 | 展示用尺码表，至多 2 个 |
| goodsModelReqs | array | 否 | 模特信息 |
| productGuideFileReqs | array | 否 | 说明书文件 |
| goodsLayerDecorationReqs | array | 否 | 商详装饰模块 |
| personalizationSwitch | integer | 否 | 0 非定制品，1 定制品 |
| productCarouseVideoReqList | array | 否 | 主图视频 |
| materialMultiLanguages | array | 否 | 图片多语言 |
| addProductChannelType | integer | 是 | 发品渠道 |

#### `productPropertyReqs[]` 元素（发品回填属性）

| 字段 | 类型 | 说明 |
|------|------|------|
| pid | integer | 属性 ID（来自 attributes.get） |
| vid | integer | 属性值 ID |
| propName | string | 属性名 |
| propValue | string | 属性值文本 |
| templatePid | integer | 模板属性 ID |
| refPid | integer | 引用属性 ID |
| numberInputValue | string | 数值录入 |
| valueUnit | string | 单位 |

#### `skuList[]` 元素（同族 `bg.local.goods.add`）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| images | array | 是 | SKU 图片 URL 列表 |
| quantity | integer | 是 | 库存数量 |
| externalProductType | integer | 否 | 外部商品类型 |
| supplierPrice / price | object | 条件 | 供货价（金额 + 币种） |
| specIdList | array | 条件 | 规格 ID 列表（多规格） |
| outSkuSn / extCode | string | 否 | 商家 SKU 编码 |
| multiplePackage | object | 否 | 多件装：`numberOfPieces`、`individuallyPacked`、`skuClassification` 等 |

#### `certificationInfo` 常见块（合规类目）

| 块 | 说明 |
|----|------|
| certificateInfo | 证书类型、文件 URL、authCode 等 |
| extraTemplate | 合规模板扩展字段 |
| actualPhoto | 实拍图（`skuPhotoInfoList`、`position`） |
| gpsrInfo | 欧盟 GPSR：制造商、责任人 |
| repInfo | 代表信息 |

完整嵌套字段以 Partner 后台 **Add Product V2** 文档为准；上表覆盖 EU 同族 `bg.local.goods.add` 公开示例中的主要块。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | LinkFox 响应码，遵循公共规则；不将 0 或 false 视为空。 |
| errmsg | string | LinkFox 错误消息。 |
| code | integer | 网关错误码（非 Temu 业务码），如 1002 参数或用户 Token 无效、1003 转发失败。 |
| message | string | 网关说明，结合 code 判断。 |
| body | string | Temu 原始 JSON 字符串；脚本尽量解析为 temuBody，并保留原文。 |
| temuBody | object / array / scalar | 脚本成功解析 body 后添加的结果；无有效 JSON 时不添加。 |
| transportHttpStatus | integer / null | 脚本记录的 LinkFox 外层 HTTP 状态，连接失败为 null。 |
| error | string | 本地网络或非 JSON HTTP 错误说明（出现时）。 |
| details | string | 非 JSON HTTP 错误原文（出现时）。 |

#### Temu 业务信封（body 解析后）

| 字段 | 类型 | 说明 |
|------|------|------|
| success | boolean | Temu 业务是否成功。 |
| errorCode | integer | Temu 业务码；1000000 或 0 常表示成功，须结合 success 和实际接口返回，不代替 LinkFox 基础规则。 |
| errorMsg | string | Temu 错误说明，成功时多为空。 |
| requestId | string | 请求追踪 ID。 |
| result | object | 业务数据；部分接口可为空对象，结构依接口而异。 |

#### 本接口 result

| 字段 | 类型 | 说明 |
|------|------|------|
| productId | integer | 新建货品 ID |
| goodsId | integer | 商品 ID（部分接口命名） |
| productSkcList | array | `{ productSkcId }` |
| productSkuList | array | `{ productSkuId, productSkcId, extCode, skuSpecList[] }` |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 外层正常后，再检查网关 code/message；1002 表示参数校验或 LinkFox 用户 Token 问题，修正后再调用；1003 表示转发或上游失败，检查 Temu accessToken、IP 白名单和网络，后续调用遵守调用约束。
- 解析 body 后结合 success、errorCode、errorMsg 判断 Temu 业务结果，不将 HTTP 成功直接当成发品、编辑或库存更新成功；无法确认写入结果时先查当前商品或库存，避免直接重放。

### curl 示例

示例仅展示结构；发品等写操作须按目标类目返回的要求补齐真实资料。

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/temu/proxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Token: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "site": "us",
  "managementType": "semi-managed",
  "accessToken": "TEMU_PRODUCT_TOKEN",
  "type": "temu.local.goods.v2.add",
  "params": {
    "goodsBasic": {
      "catId": 12345,
      "productName": "Example Product",
      "carouselImageUrls": [
        "https://..."
      ],
      "productPropertyReqs": [
        {
          "pid": 1,
          "vid": 100
        }
      ],
      "addProductChannelType": 0
    },
    "skuList": [
      {
        "images": [
          "https://..."
        ],
        "quantity": 99,
        "supplierPrice": {
          "amount": "19.99",
          "currency": "USD"
        }
      }
    ],
    "addProductChannelType": 0
  }
}'
```

## 接口：商品图片上传 V2（temu.local.goods.image.v2.upload）

- **Partner 文档分区**：`sub_menu_code=37d470d8c6e149f78953311aa0b0296d`
- **脚本**：`scripts/us_goods_image_upload.py`
- **用途**：上传商品图片（Base64），返回可用于 `goods.v2.add` 的 URL。与同族 `bg.goods.image.upload.global` 一致。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/proxy`

### 请求参数

#### 网关 POST Body

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| site | string | 是 | US 封装默认 `us`；兼容 `cn` / `partner` / `global` / `eu`，按目标店铺授权选择。 |
| managementType | string | 是 | US 封装默认 `semi-managed`；通用脚本支持 `full-managed` / `semi-managed`。 |
| accessToken | string | 与 storeKey 二选一 | Temu 店铺令牌，最长约 8192；直接提供时优先使用。 |
| storeKey | string | 与 accessToken 二选一 | 脚本本地店铺键，解析后发送 accessToken；不发送 storeKey。 |
| tokenPurpose | string | 否 | 本地令牌用途；US 封装默认 `product-inventory`，通用脚本默认 `default`；不发送此字段。 |
| type | string | 是 | 固定 `temu.local.goods.image.v2.upload`，写入 Body，不是 URL 路径。 |
| params | object | 是 | 本接口业务参数，须包含下表的必填项；US 脚本省略空对象的行为不免除必填要求。 |

脚本认证别名、CLI、默认值与本地令牌解析见 [运行约定](api.md#运行约定)。

#### 业务参数（`params`）

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| image | string | 是 | 图片 **Base64**（支持 jpg/jpeg、png 等） |
| imageBizType | integer | 否 | `0` 默认；`1` 外包装专用 URL |
| options | object | 否 | 裁剪/增强选项，见下表 |

#### `options`

| 字段 | 类型 | 说明 |
|------|------|------|
| boost | boolean | 是否 AI 清晰度提升 |
| doIntelligenceCrop | boolean | 是否智能裁剪（true 时可能返回 1 原图 + 3 裁剪图） |
| cateId | integer | 叶子类目 ID（`doIntelligenceCrop=true` 时生效） |
| sizeMode | integer | `0` 原图；`1` 800×800；`2` 1350×1800 |

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | LinkFox 响应码，遵循公共规则；不将 0 或 false 视为空。 |
| errmsg | string | LinkFox 错误消息。 |
| code | integer | 网关错误码（非 Temu 业务码），如 1002 参数或用户 Token 无效、1003 转发失败。 |
| message | string | 网关说明，结合 code 判断。 |
| body | string | Temu 原始 JSON 字符串；脚本尽量解析为 temuBody，并保留原文。 |
| temuBody | object / array / scalar | 脚本成功解析 body 后添加的结果；无有效 JSON 时不添加。 |
| transportHttpStatus | integer / null | 脚本记录的 LinkFox 外层 HTTP 状态，连接失败为 null。 |
| error | string | 本地网络或非 JSON HTTP 错误说明（出现时）。 |
| details | string | 非 JSON HTTP 错误原文（出现时）。 |

#### Temu 业务信封（body 解析后）

| 字段 | 类型 | 说明 |
|------|------|------|
| success | boolean | Temu 业务是否成功。 |
| errorCode | integer | Temu 业务码；1000000 或 0 常表示成功，须结合 success 和实际接口返回，不代替 LinkFox 基础规则。 |
| errorMsg | string | Temu 错误说明，成功时多为空。 |
| requestId | string | 请求追踪 ID。 |
| result | object | 业务数据；部分接口可为空对象，结构依接口而异。 |

#### 本接口 result

| 字段 | 类型 | 说明 |
|------|------|------|
| imageUrl | string | 原图链接 |
| url | string | 单张 AI 裁图链接 |
| urls | array | 多张 AI 裁图链接 |

将 `imageUrl` 或 `urls[]` 填入 `goods.v2.add` 的 `carouselImageUrls`、`skuList[].images`、`materialImgUrl` 等。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 外层正常后，再检查网关 code/message；1002 表示参数校验或 LinkFox 用户 Token 问题，修正后再调用；1003 表示转发或上游失败，检查 Temu accessToken、IP 白名单和网络，后续调用遵守调用约束。
- 解析 body 后结合 success、errorCode、errorMsg 判断 Temu 业务结果，不将 HTTP 成功直接当成发品、编辑或库存更新成功；无法确认写入结果时先查当前商品或库存，避免直接重放。

### curl 示例

示例仅展示结构；发品等写操作须按目标类目返回的要求补齐真实资料。

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/temu/proxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Token: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "site": "us",
  "managementType": "semi-managed",
  "accessToken": "TEMU_PRODUCT_TOKEN",
  "type": "temu.local.goods.image.v2.upload",
  "params": {
    "image": "<BASE64>",
    "options": {
      "doIntelligenceCrop": true,
      "cateId": 12345,
      "sizeMode": 1
    }
  }
}'
```

## 接口：发布商品（半托管/跨境）（temu.goods.add）

- **sub_menu_code**：`1b99296745854ae08d39a7bbe1e4f7a8`
- **脚本**：`scripts/us_goods_add_legacy.py`
- **说明**：非 V2 发品接口；美国站 Partner US 发品优先用 `temu.local.goods.v2.add`。载荷与同族 `temu.goods.add` 一致。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/proxy`

### 请求参数

#### 网关 POST Body

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| site | string | 是 | US 封装默认 `us`；兼容 `cn` / `partner` / `global` / `eu`，按目标店铺授权选择。 |
| managementType | string | 是 | US 封装默认 `semi-managed`；通用脚本支持 `full-managed` / `semi-managed`。 |
| accessToken | string | 与 storeKey 二选一 | Temu 店铺令牌，最长约 8192；直接提供时优先使用。 |
| storeKey | string | 与 accessToken 二选一 | 脚本本地店铺键，解析后发送 accessToken；不发送 storeKey。 |
| tokenPurpose | string | 否 | 本地令牌用途；US 封装默认 `product-inventory`，通用脚本默认 `default`；不发送此字段。 |
| type | string | 是 | 固定 `temu.goods.add`，写入 Body，不是 URL 路径。 |
| params | object | 是 | 本接口业务参数，须包含下表的必填项；US 脚本省略空对象的行为不免除必填要求。 |

脚本认证别名、CLI、默认值与本地令牌解析见 [运行约定](api.md#运行约定)。

#### 业务参数（`params`）

同族发品模型主要块如下：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| cat1Id … cat10Id | integer | 是 | 各级类目（至少到叶子） |
| productName | string | 是 | 商品标题 |
| carouselImageUrls | array | 是 | 轮播图 URL，通常 ≥5 张 |
| productPropertyReqs | array | 是 | 类目属性 |
| productSkcReqs | array | 是 | SKC/SKU 结构 |
| addProductChannelType | integer | 是 | 发品渠道 |

同族嵌套字段展开如下；实际载荷层级以 Partner 后台文档为准。


#### 同族模型嵌套结构（goodsBasic / skuList）


| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| catId / leafCatId | integer | 是 | 叶子类目 ID（或 cat1Id…cat10Id 逐级类目，与同族 `temu.goods.add` 一致） |
| productName | string | 是 | 商品标题，通常 1–250 字符 |
| carouselImageUrls | array | 是 | 轮播图 URL 列表（须先 `image.v2.upload`），常 ≥5 张 |
| materialImgUrl | string | 否 | 素材图 URL |
| carouselImageI18nReqs | array | 否 | 多语言轮播图（非服饰类常必填） |
| productOuterPackageImageReqs | array | 否 | 外包装图 |
| productOuterPackageReq | object | 否 | 外包装信息 |
| productPropertyReqs | array | 是 | 类目属性值，元素见下表 |
| productSpecPropertyReqs | array | 条件 | 多规格时的规格属性 |
| productWhExtAttrReq | object | 是 | 仓配扩展（产地、重量体积等） |
| productSaleExtAttrReq | object | 否 | 销售扩展 |
| productSkcReqs | array | 是 | SKC 维度数据（含 SKU 列表） |
| sizeTemplateIds | array | 否 | 尺码表模板 ID，无尺码传 `[]` |
| showSizeTemplateIds | array | 否 | 展示用尺码表，至多 2 个 |
| goodsModelReqs | array | 否 | 模特信息 |
| productGuideFileReqs | array | 否 | 说明书文件 |
| goodsLayerDecorationReqs | array | 否 | 商详装饰模块 |
| personalizationSwitch | integer | 否 | 0 非定制品，1 定制品 |
| productCarouseVideoReqList | array | 否 | 主图视频 |
| materialMultiLanguages | array | 否 | 图片多语言 |
| addProductChannelType | integer | 是 | 发品渠道 |

#### `productPropertyReqs[]` 元素（发品回填属性）

| 字段 | 类型 | 说明 |
|------|------|------|
| pid | integer | 属性 ID（来自 attributes.get） |
| vid | integer | 属性值 ID |
| propName | string | 属性名 |
| propValue | string | 属性值文本 |
| templatePid | integer | 模板属性 ID |
| refPid | integer | 引用属性 ID |
| numberInputValue | string | 数值录入 |
| valueUnit | string | 单位 |

#### `skuList[]` 元素（同族 `bg.local.goods.add`）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| images | array | 是 | SKU 图片 URL 列表 |
| quantity | integer | 是 | 库存数量 |
| externalProductType | integer | 否 | 外部商品类型 |
| supplierPrice / price | object | 条件 | 供货价（金额 + 币种） |
| specIdList | array | 条件 | 规格 ID 列表（多规格） |
| outSkuSn / extCode | string | 否 | 商家 SKU 编码 |
| multiplePackage | object | 否 | 多件装：`numberOfPieces`、`individuallyPacked`、`skuClassification` 等 |

#### `certificationInfo` 常见块（合规类目）

| 块 | 说明 |
|----|------|
| certificateInfo | 证书类型、文件 URL、authCode 等 |
| extraTemplate | 合规模板扩展字段 |
| actualPhoto | 实拍图（`skuPhotoInfoList`、`position`） |
| gpsrInfo | 欧盟 GPSR：制造商、责任人 |
| repInfo | 代表信息 |

完整嵌套字段以 Partner 后台 **Add Product V2** 文档为准；上表覆盖 EU 同族 `bg.local.goods.add` 公开示例中的主要块。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | LinkFox 响应码，遵循公共规则；不将 0 或 false 视为空。 |
| errmsg | string | LinkFox 错误消息。 |
| code | integer | 网关错误码（非 Temu 业务码），如 1002 参数或用户 Token 无效、1003 转发失败。 |
| message | string | 网关说明，结合 code 判断。 |
| body | string | Temu 原始 JSON 字符串；脚本尽量解析为 temuBody，并保留原文。 |
| temuBody | object / array / scalar | 脚本成功解析 body 后添加的结果；无有效 JSON 时不添加。 |
| transportHttpStatus | integer / null | 脚本记录的 LinkFox 外层 HTTP 状态，连接失败为 null。 |
| error | string | 本地网络或非 JSON HTTP 错误说明（出现时）。 |
| details | string | 非 JSON HTTP 错误原文（出现时）。 |

#### Temu 业务信封（body 解析后）

| 字段 | 类型 | 说明 |
|------|------|------|
| success | boolean | Temu 业务是否成功。 |
| errorCode | integer | Temu 业务码；1000000 或 0 常表示成功，须结合 success 和实际接口返回，不代替 LinkFox 基础规则。 |
| errorMsg | string | Temu 错误说明，成功时多为空。 |
| requestId | string | 请求追踪 ID。 |
| result | object | 业务数据；部分接口可为空对象，结构依接口而异。 |

#### 本接口 result

| 字段 | 类型 | 说明 |
|------|------|------|
| productId | integer | 新建货品 ID |
| productSkcList | array | `{ productSkcId }` |
| productSkuList | array | `{ productSkuId, extCode, skuSpecList }` |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 外层正常后，再检查网关 code/message；1002 表示参数校验或 LinkFox 用户 Token 问题，修正后再调用；1003 表示转发或上游失败，检查 Temu accessToken、IP 白名单和网络，后续调用遵守调用约束。
- 解析 body 后结合 success、errorCode、errorMsg 判断 Temu 业务结果，不将 HTTP 成功直接当成发品、编辑或库存更新成功；无法确认写入结果时先查当前商品或库存，避免直接重放。

### curl 示例

示例仅展示结构；发品等写操作须按目标类目返回的要求补齐真实资料。

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/temu/proxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Token: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "site": "us",
  "managementType": "semi-managed",
  "accessToken": "TEMU_PRODUCT_TOKEN",
  "type": "temu.goods.add",
  "params": {
    "cat1Id": 1,
    "productName": "示例商品",
    "carouselImageUrls": [
      "https://example.com/temu-image.jpg"
    ],
    "productPropertyReqs": [],
    "productSkcReqs": [],
    "addProductChannelType": 0
  }
}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-temu-add-product-us",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
