# Lazada 店铺商品管理接口

## 公共规则

请求头、网关基础地址、请求字段、响应 envelope、响应码和写入恢复统一见 [接口总览](api.md#公共规则)。本页各操作只补充业务差异。CLI 参数映射与本地输出见 [script-usage.md](script-usage.md)。

## 接口：类目树（getCategoryTree）

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/products`。
- **上游方法与路径**：`GET /category/tree/get`。本操作为只读。

### 请求参数

公共顶层字段见 [业务操作请求字段](api.md#业务操作请求字段)。本操作 `operation=getCategoryTree`；下表列出 `params` 内部字段。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `language_code` | 字符串 | 否 | 默认 `en_US`，各站可用。站点语言按市场选用 `en_SG`、`th_TH`、`id_ID`、`vi_VN`、`fil_PH` 或 `ms_MY`。 |

### 响应结构

公共响应 envelope 见 [网关成功响应](api.md#网关成功响应)。以下为该业务结果的字段与含义。

| 响应字段 | 类型 | 说明 |
| --- | --- | --- |
| `data` | 对象数组 | 该站点的类目树。 |
| `data[].category_id`、`data[].name` | 字符串 | 类目 ID、名称。 |
| `data[].leaf`、`data[].var` | 布尔值 | 是否叶子类目、是否支持变体。 |
| `data[].children` | 对象数组 | 子类目，节点结构相同。 |

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 正常响应后仍按本节响应结构判断业务结果；格式缺失不补造数据。

## 接口：类目属性（getCategoryAttributes）

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/products`。
- **上游方法与路径**：`GET /category/attributes/get`。本操作为只读。

### 请求参数

公共顶层字段见 [业务操作请求字段](api.md#业务操作请求字段)。本操作 `operation=getCategoryAttributes`；下表列出 `params` 内部字段。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `primary_category_id` | 正整数或数字字符串 | 是 | 从当前站点类目树取得的类目 ID。 |
| `language_code` | 字符串 | 否 | 语言和默认值同类目树。 |

### 响应结构

公共响应 envelope 见 [网关成功响应](api.md#网关成功响应)。以下为该业务结果的字段与含义。

| 响应字段 | 类型 | 说明 |
| --- | --- | --- |
| `data` | 对象数组 | 类目属性定义。 |
| `data[].id`、`data[].name`、`data[].label` | 字符串 | 属性 ID、请求键、展示标签。 |
| `data[].is_mandatory`、`data[].is_sale_prop` | 整数或数字字符串 | 是否必填、是否为销售属性。 |
| `data[].attribute_type`、`data[].input_type` | 字符串 | 属性类型和输入方式。 |
| `data[].options` | 对象数组 | 选项值，条目包含字符串字段 `id`、`name`、`en_name`。 |
| `data[].advanced`、`data[].unit` | 对象 | 扩展属性和数值单位规则。`unit.type` 为字符串数组，`numericMin`、`numericMax` 为字符串，`precision` 为整数或数字字符串。 |

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 正常响应后仍按本节响应结构判断业务结果；格式缺失不补造数据。

## 接口：品牌列表（listBrands）

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/products`。
- **上游方法与路径**：`GET /category/brands/query`。本操作为只读。

### 请求参数

公共顶层字段见 [业务操作请求字段](api.md#业务操作请求字段)。本操作 `operation=listBrands`；下表列出 `params` 内部字段。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `startRow` | 整数或数字字符串 | 是 | 要跳过的记录数，非负。 |
| `pageSize` | 整数或数字字符串 | 是 | 该请求的页容量，1 至 200。 |

### 响应结构

公共响应 envelope 见 [网关成功响应](api.md#网关成功响应)。以下为该业务结果的字段与含义。

本操作固定提取上游业务 `data` 作为网关 `data`，即使上游同时带独立跟踪字段也不增加业务包装层。

| 响应字段 | 类型 | 说明 |
| --- | --- | --- |
| `data.module` | 对象数组 | 品牌列表，含 `brand_id`、`name`、`name_en`、`global_identifier` 字符串字段。 |
| `data.start_row`、`data.page_index`、`data.page_size` | 整数或数字字符串 | 起点、页索引、页容量。 |
| `data.total_record`、`data.total_page` | 整数或数字字符串 | 总记录数、总页数。 |
| `data.enable_total` | 布尔值或布尔字符串 | 是否提供总数统计。 |

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 正常响应后仍按本节响应结构判断业务结果；格式缺失不补造数据。

## 接口：商品质检（getProductQcStatus）

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/products`。
- **上游方法与路径**：`GET /product/qc/status/get`。本操作为只读。

### 请求参数

公共顶层字段见 [业务操作请求字段](api.md#业务操作请求字段)。本操作 `operation=getProductQcStatus`；下表列出 `params` 内部字段。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `offset` | 整数或数字字符串 | 是 | 跳过的审核记录数，非负。 |
| `limit` | 整数或数字字符串 | 是 | 要返回的最大记录数，正整数。 |
| `seller_skus` | 字符串数组 | 是 | 该店铺待查询的卖家 SKU，至少一项。 |

### 响应结构

公共响应 envelope 见 [网关成功响应](api.md#网关成功响应)。以下为该业务结果的字段与含义。

| 响应字段 | 类型 | 说明 |
| --- | --- | --- |
| `data` | 对象数组 | 审核记录。 |
| `data[].seller_sku`、`data[].status` | 字符串 | 卖家 SKU、审核状态。 |
| `data[].reason`、`data[].data_changed` | 字符串 | 原因及上游数据变更标志。 |

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 正常响应后仍按本节响应结构判断业务结果；格式缺失不补造数据。

## 接口：仓库列表（listWarehouses）

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/products`。
- **上游方法与路径**：`GET /rc/warehouse/get`。本操作为只读。

### 请求参数

公共顶层字段见 [业务操作请求字段](api.md#业务操作请求字段)。本操作 `operation=listWarehouses`；下表列出 `params` 内部字段。

无业务参数，`params` 可使用 `{}`。

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `params` | 对象 | 否 | 本操作无业务参数，可省略或传 `{}`。 |

### 响应结构

公共响应 envelope 见 [网关成功响应](api.md#网关成功响应)。以下为该业务结果的字段与含义。

| 响应字段 | 类型 | 说明 |
| --- | --- | --- |
| `data.result.module` | 对象 | Lazada 仓库载荷。按实际仓库标识和站点选择库存操作目标。 |
| `data.result.success` | 对象 | 上游成功信息。 |
| `data.result.not_success`、`data.result.repeated`、`data.result.retry` | 布尔值或布尔字符串 | 上游失败、重复、重试标志。 |
| `data.result.error_code` | 字符串 | 上游错误码，按实际返回解释。 |

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 正常响应后仍按本节响应结构判断业务结果；格式缺失不补造数据。

## 接口：刊登商品（createProduct）

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/products`。
- **上游方法与路径**：`POST /product/create`。本操作为写入。

### 请求参数

公共顶层字段见 [业务操作请求字段](api.md#业务操作请求字段)。本操作 `operation=createProduct`；下表列出 `params` 内部字段。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `payload` | 字符串 | 是 | Lazada CreateProduct 要求的 JSON 或 XML 文本，根结构为 Request.Product。先查询叶子类目及其必填属性，再准备 SKU 和 Lazada 图片地址。 |

`Request.Product` 内包含 `PrimaryCategory`、`Attributes`、`Skus.Sku`；JSON 中 `Sku` 是数组，图片使用 `Images.Image` 数组，每组最多 8 张 Lazada 内链图片。新增 SKU 使用 `SellerSku`，常规商品准备价格及包装尺寸、重量；按当前类目的 `is_mandatory`、`is_sale_prop` 和卖家模式填写属性。品牌优先使用品牌查询返回的 `brand_id`。空 `<Request/>` 不构成有效刊登请求；后端透传 payload，由 Lazada 校验动态类目规则。详见 [官方刊登参数说明](https://open.lazada.com/apps/doc/doc?nodeId=30720&docId=120949)。

### 响应结构

公共响应 envelope 见 [网关成功响应](api.md#网关成功响应)。以下为该业务结果的字段与含义。

| 响应字段 | 类型 | 说明 |
| --- | --- | --- |
| `data.item_id` | 字符串 | 上游接受创建后给出的商品 ID。 |
| `data.item_status` | 字符串 | 商品状态，按实际质检结果核对是否可售。 |
| `data.sku_list` | 对象数组 | SKU 结果，含 `sku_id`、`seller_sku`、`shop_sku` 字符串字段。 |

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 按 [写入与续查](api.md#写入与续查) 核对原写记录及本节业务字段，不以 HTTP 200 单独判断业务完成。

## 接口：更新商品（updateProduct）

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/products`。
- **上游方法与路径**：`POST /product/update`。本操作为写入。

### 请求参数

公共顶层字段见 [业务操作请求字段](api.md#业务操作请求字段)。本操作 `operation=updateProduct`；下表列出 `params` 内部字段。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `payload` | 字符串 | 是 | Lazada UpdateProduct 要求的 JSON 或 XML 文本，根结构为 Request.Product。Skus.Sku 中使用真实 SkuId 定位，仅填写本次要修改的属性。 |

更新时未传字段通常保持原值。图片替换需提供目标完整图片集合；传空值不等于删除属性，仅使用官方支持的删除字段。类目属性按当前类目查询结果填写，不能把刊登时的必填项全部强加给局部更新。详见 [官方更新参数说明](https://open.lazada.com/apps/doc/doc?nodeId=30715&docId=121228)。

### 响应结构

公共响应 envelope 见 [网关成功响应](api.md#网关成功响应)。以下为该业务结果的字段与含义。

| 响应字段 | 类型 | 说明 |
| --- | --- | --- |
| `data.item_status` | 字符串 | 上游返回的商品状态，可能省略。 |
| `data.variation` | 对象 | 可选。变体定义可能含 `Variation1` 至 `Variation4`，每项包含 `name`、`has_image`、`customize`、`options`。 |

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 按 [写入与续查](api.md#写入与续查) 核对原写记录及本节业务字段，不以 HTTP 200 单独判断业务完成。

## 接口：更新价格和库存（updatePriceQuantity）

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/products`。
- **上游方法与路径**：`POST /product/price_quantity/update`。本操作为写入。

### 请求参数

公共顶层字段见 [业务操作请求字段](api.md#业务操作请求字段)。本操作 `operation=updatePriceQuantity`；下表列出 `params` 内部字段。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `payload` | 字符串 | 是 | Lazada UpdatePriceQuantity 请求文本。库存路径为 Request.Product.Skus.Sku，使用 ItemId、SkuId 与 Quantity；核对 SKU、价格、币种及库存口径。 |

`Quantity` 是总库存；可售库存的两个接口使用 `SellableQuantity`。库存批次最多 50 个 SKU，多仓卖家使用 `MultiWarehouseInventories.MultiWarehouseInventory` 的 `WarehouseCode` 与对应数量，单仓卖家不传多仓结构。数量须满足现有占用和活动锁定限制。详见 [官方库存参数说明](https://open.lazada.com/apps/doc/doc?nodeId=42713&docId=121234)。

### 响应结构

公共响应 envelope 见 [网关成功响应](api.md#网关成功响应)。以下为该业务结果的字段与含义。

| 响应字段 | 类型 | 说明 |
| --- | --- | --- |
| `data` | 对象 | 上游业务结果，可能是空对象。需要核实实际值时查询商品。 |

提交真实 SKU 及本次要修改的价格或库存值。空 `<Request/>` 即使返回 code=0，也不表示 SKU 已更新；写入结果不明时按原 UUID 续查，不自动重发。

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 按 [写入与续查](api.md#写入与续查) 核对原写记录及本节业务字段，不以 HTTP 200 单独判断业务完成。

## 接口：设定可售库存（updateSellableQuantity）

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/products`。
- **上游方法与路径**：`POST /product/stock/sellable/update`。本操作为写入。

### 请求参数

公共顶层字段见 [业务操作请求字段](api.md#业务操作请求字段)。本操作 `operation=updateSellableQuantity`；下表列出 `params` 内部字段。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `payload` | 字符串 | 是 | Request.Product.Skus.Sku 下以 ItemId、SkuId 定位，SellableQuantity 为非负目标值，覆盖可售库存；每批最多 50 个 SKU。多仓结构及限制同官方库存参数说明。 |

### 响应结构

公共响应 envelope 见 [网关成功响应](api.md#网关成功响应)。以下为该业务结果的字段与含义。

| 响应字段 | 类型 | 说明 |
| --- | --- | --- |
| `data` | 对象 | 上游结果，可能为空对象。 |

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 按 [写入与续查](api.md#写入与续查) 核对原写记录及本节业务字段，不以 HTTP 200 单独判断业务完成。

## 接口：增减可售库存（adjustSellableQuantity）

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/products`。
- **上游方法与路径**：`POST /product/stock/sellable/adjust`。本操作为写入。

### 请求参数

公共顶层字段见 [业务操作请求字段](api.md#业务操作请求字段)。本操作 `operation=adjustSellableQuantity`；下表列出 `params` 内部字段。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `payload` | 字符串 | 是 | Request.Product.Skus.Sku 下以 ItemId、SkuId 定位，SellableQuantity 为正或负增量；每批最多 50 个 SKU。最终可售库存不得低于 0 或活动锁定量。多仓结构及限制同官方库存参数说明。 |

### 响应结构

公共响应 envelope 见 [网关成功响应](api.md#网关成功响应)。以下为该业务结果的字段与含义。

| 响应字段 | 类型 | 说明 |
| --- | --- | --- |
| `data` | 对象 | 上游结果，可能为空对象。 |

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 按 [写入与续查](api.md#写入与续查) 核对原写记录及本节业务字段，不以 HTTP 200 单独判断业务完成。

## 接口：迁移公开图片 URL（migrateImage）

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/products`。
- **上游方法与路径**：`POST /image/migrate`。本操作为写入。

### 请求参数

公共顶层字段见 [业务操作请求字段](api.md#业务操作请求字段)。本操作 `operation=migrateImage`；下表列出 `params` 内部字段。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `payload` | 字符串 | 是 | XML 请求文本，在 `Request/Image/Url` 放入用户指定的可访问公开图片 URL。 |

### 响应结构

公共响应 envelope 见 [网关成功响应](api.md#网关成功响应)。以下为该业务结果的字段与含义。

| 响应字段 | 类型 | 说明 |
| --- | --- | --- |
| `data.image.url`、`data.image.hash_code` | 字符串 | Lazada 图片地址及哈希。刊登或更新使用返回的 `url`。 |

[Lazada 图片迁移说明](https://open.lazada.com/apps/doc/doc?docId=120947&nodeId=30718)

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 按 [写入与续查](api.md#写入与续查) 核对原写记录及本节业务字段，不以 HTTP 200 单独判断业务完成。

## 接口：下架商品或 SKU（deactivateProduct）

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/products`。
- **上游方法与路径**：`POST /product/deactivate`。本操作为写入。

### 请求参数

公共顶层字段见 [业务操作请求字段](api.md#业务操作请求字段)。本操作 `operation=deactivateProduct`；下表列出 `params` 内部字段。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `apiRequestBody` | 字符串 | 是 | 按[官方下架示例](https://open.lazada.com/apps/doc/api?path=%2Fproduct%2Fdeactivate)传 XML 文本，根结构为 `Request/Product`，包含实际 `ItemId`；仅下架部分 SKU 时在 `Skus` 中指定 `SkuId`。 |

### 响应结构

公共响应 envelope 见 [网关成功响应](api.md#网关成功响应)。以下为该业务结果的字段与含义。

| 响应字段 | 类型 | 说明 |
| --- | --- | --- |
| `data` | 对象 | 上游下架结果，可能为空对象。 |

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 按 [写入与续查](api.md#写入与续查) 核对原写记录及本节业务字段，不以 HTTP 200 单独判断业务完成。

## 接口：删除指定 SKU（removeProduct）

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/products`。
- **上游方法与路径**：`POST /product/remove`。本操作为写入。

### 请求参数

公共顶层字段见 [业务操作请求字段](api.md#业务操作请求字段)。本操作 `operation=removeProduct`；下表列出 `params` 内部字段。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `sku_id_list` | JSON 数组字符串 | 二选一 | 1 至 50 个 `SkuId_<itemId>_<skuId>` 字符串。 |
| `seller_sku_list` | JSON 数组字符串 | 二选一 | 1 至 50 个卖家 SKU 字符串。 |

先从目标店铺查询 SKU 并确认删除范围，优先提交 `sku_id_list`。官方错误码说明已将 `seller_sku_list` 标为弃用；LinkFox 保留旧参数兼容且要求二选一，不依赖两者同时提交时的优先级。[Lazada 删除接口](https://open.lazada.com/apps/doc/api?path=%2Fproduct%2Fremove)

### 响应结构

公共响应 envelope 见 [网关成功响应](api.md#网关成功响应)。以下为该业务结果的字段与含义。

| 响应字段 | 类型 | 说明 |
| --- | --- | --- |
| `data` | 对象 | 上游删除结果，可能为空对象。 |

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 按 [写入与续查](api.md#写入与续查) 核对原写记录及本节业务字段，不以 HTTP 200 单独判断业务完成。

## 接口：批量迁移公开图片（migrateImages）

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/products`。
- **上游方法与路径**：`POST /images/migrate`。本操作为写入。

### 请求参数

公共顶层字段见 [业务操作请求字段](api.md#业务操作请求字段)。本操作 `operation=migrateImages`；下表列出 `params` 内部字段。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `payload` | 字符串 | 是 | XML 请求文本。`Request/Images` 下为每张图传一个 `Url`。最多 8 个用户指定的公开 JPG 或 PNG 图片 URL。 |

### 响应结构

公共响应 envelope 见 [网关成功响应](api.md#网关成功响应)。以下为该业务结果的字段与含义。

| 响应字段 | 类型 | 说明 |
| --- | --- | --- |
| `data.batch_id` | 字符串 | 已受理的迁移批次号。将原编号传给 `getImageMigrationResult`，按图片核对最终结果。 |

[Lazada 图片迁移说明](https://open.lazada.com/apps/doc/doc?docId=120947&nodeId=30718)

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 按 [写入与续查](api.md#写入与续查) 核对原写记录及本节业务字段，不以 HTTP 200 单独判断业务完成。

## 接口：批量迁移结果（getImageMigrationResult）

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/products`。
- **上游方法与路径**：`GET /image/response/get`。本操作为只读。

### 请求参数

公共顶层字段见 [业务操作请求字段](api.md#业务操作请求字段)。本操作 `operation=getImageMigrationResult`；下表列出 `params` 内部字段。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `batch_id` | 字符串 | 是 | 批量迁移返回的原始批次号。 |

### 响应结构

公共响应 envelope 见 [网关成功响应](api.md#网关成功响应)。以下为该业务结果的字段与含义。

| 响应字段 | 类型 | 说明 |
| --- | --- | --- |
| `data.images` | 对象数组 | 成功图片，条目包含 `url` 和 `hash_code` 字符串。只将成功图片地址交给下游刊登。 |
| `data.errors` | 对象数组 | 失败图片，条目包含 `field`、`msg`、`original_url` 字符串。 |

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 正常响应后仍按本节响应结构判断业务结果；格式缺失不补造数据。

## 接口：视频详情（getVideo）

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/products`。
- **上游方法与路径**：`GET /media/video/get`。本操作为只读。

### 请求参数

公共顶层字段见 [业务操作请求字段](api.md#业务操作请求字段)。本操作 `operation=getVideo`；下表列出 `params` 内部字段。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `videoId` | 正整数或数字字符串 | 是 | 该店铺的视频 ID，使用上传提交返回的 `video_id`。 |

### 响应结构

公共响应 envelope 见 [网关成功响应](api.md#网关成功响应)。以下为该业务结果的字段与含义。

| 响应字段 | 类型 | 说明 |
| --- | --- | --- |
| `data.state` | 字符串 | `READY_FOR_TRANSCODE`、`TRANSCODING`、`TRANSCODE_FAILED`、`READY_FOR_AUDIT`、`AUDIT_FAILED`、`AUDIT_SUCCESS` 或 `DELETED`。 |
| `data.title`、`data.cover_url`、`data.video_url` | 字符串 | 视频标题、封面地址、视频地址。 |
| `data.success` | 布尔值或布尔字符串 | 上游业务状态。 |
| `data.result_code`、`data.result_message` | 字符串 | 上游结果码、结果说明。 |

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 正常响应后仍按本节响应结构判断业务结果；格式缺失不补造数据。

## 接口：视频额度（getVideoQuota）

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/products`。
- **上游方法与路径**：`GET /media/video/quota/get`。本操作为只读。

### 请求参数

公共顶层字段见 [业务操作请求字段](api.md#业务操作请求字段)。本操作 `operation=getVideoQuota`；下表列出 `params` 内部字段。

无业务参数，`params` 可使用 `{}`。

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `params` | 对象 | 否 | 本操作无业务参数，可省略或传 `{}`。 |

### 响应结构

公共响应 envelope 见 [网关成功响应](api.md#网关成功响应)。以下为该业务结果的字段与含义。

| 响应字段 | 类型 | 说明 |
| --- | --- | --- |
| `data.capacity_size`、`data.used_size` | 整数或数字字符串 | 总额度、已用空间，单位按上游实际口径。 |
| `data.success`、`data.result_code`、`data.result_message` | 布尔值或布尔字符串、字符串、字符串 | 上游业务状态、结果码、说明。 |

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 正常响应后仍按本节响应结构判断业务结果；格式缺失不补造数据。

## 接口：删除视频（removeVideo）

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/products`。
- **上游方法与路径**：`POST /media/video/remove`。本操作为写入。

### 请求参数

公共顶层字段见 [业务操作请求字段](api.md#业务操作请求字段)。本操作 `operation=removeVideo`；下表列出 `params` 内部字段。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `videoId` | 正整数或数字字符串 | 是 | 视频 ID。提交前核对店铺、视频及关联商品并取得明确授权。 |

### 响应结构

公共响应 envelope 见 [网关成功响应](api.md#网关成功响应)。以下为该业务结果的字段与含义。

| 响应字段 | 类型 | 说明 |
| --- | --- | --- |
| `data.success`、`data.result_code`、`data.result_message` | 布尔值或布尔字符串、字符串、字符串 | 上游业务状态、结果码、说明。 |

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 按 [写入与续查](api.md#写入与续查) 核对原写记录及本节业务字段，不以 HTTP 200 单独判断业务完成。

## 接口：本地图片上传（uploadImage）

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/products`。
- **上游方法与路径**：`POST /image/upload`。本操作为写入。

### 请求参数

公共顶层字段见 [业务操作请求字段](api.md#业务操作请求字段)。本操作 `operation=uploadImage`；下表列出 `params` 内部字段。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `image` | Base64 字符串 | 是 | 用户明确选中的 JPG 或 PNG，原文件不超过 1 MiB，宽、高分别为 330–5000 像素。 |

图片尺寸不符或无法读取时后端直接拒绝，不发起上游写入。尺寸要求见 [Lazada 图片说明](https://open.lazada.com/apps/doc/doc?docId=120947&nodeId=30715)。

### 响应结构

公共响应 envelope 见 [网关成功响应](api.md#网关成功响应)。以下为该业务结果的字段与含义。

| 响应字段 | 类型 | 说明 |
| --- | --- | --- |
| `data.image.url`、`data.image.hash_code` | 字符串 | Lazada 图片地址及哈希。刊登使用返回的 `url`。 |

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 按 [写入与续查](api.md#写入与续查) 核对原写记录及本节业务字段，不以 HTTP 200 单独判断业务完成。

## 接口：创建视频上传任务（initVideoUpload）

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/products`。
- **上游方法与路径**：`POST /media/video/block/create`。本操作为写入。

### 请求参数

公共顶层字段见 [业务操作请求字段](api.md#业务操作请求字段)。本操作 `operation=initVideoUpload`；下表列出 `params` 内部字段。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `fileName` | 字符串 | 是 | 实际视频文件名，不带路径。 |
| `fileBytes` | 整数或数字字符串 | 是 | 视频总字节数，至少 1 字节且小于 100 MiB。 |

### 响应结构

公共响应 envelope 见 [网关成功响应](api.md#网关成功响应)。以下为该业务结果的字段与含义。

| 响应字段 | 类型 | 说明 |
| --- | --- | --- |
| `data.upload_id` | 字符串 | 上传任务 ID。后续请求将该值传给 `uploadId`。 |
| `data.success`、`data.result_code`、`data.result_message` | 布尔值或布尔字符串、字符串、字符串 | 上游业务状态、结果码、说明。 |

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 按 [写入与续查](api.md#写入与续查) 核对原写记录及本节业务字段，不以 HTTP 200 单独判断业务完成。

## 接口：上传视频分块（uploadVideoBlock）

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/products`。
- **上游方法与路径**：`POST /media/video/block/upload`。本操作为写入。

### 请求参数

公共顶层字段见 [业务操作请求字段](api.md#业务操作请求字段)。本操作 `operation=uploadVideoBlock`；下表列出 `params` 内部字段。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `uploadId` | 字符串 | 是 | 视频初始化返回的 `upload_id`。 |
| `blockNo` | 整数或数字字符串 | 是 | 分块序号，从 0 开始且小于总块数。 |
| `blockCount` | 整数或数字字符串 | 是 | 总块数，1 至 1000。 |
| `file` | Base64 字符串 | 是 | 选中的视频分块，原始分块不超过 3 MiB。 |

### 响应结构

公共响应 envelope 见 [网关成功响应](api.md#网关成功响应)。以下为该业务结果的字段与含义。

| 响应字段 | 类型 | 说明 |
| --- | --- | --- |
| `data.e_tag` | 字符串 | 成功分块标识，按序号记录。 |
| `data.success`、`data.result_code`、`data.result_message` | 布尔值或布尔字符串、字符串、字符串 | 上游业务状态、结果码、说明。 |

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 按 [写入与续查](api.md#写入与续查) 核对原写记录及本节业务字段，不以 HTTP 200 单独判断业务完成。

## 接口：完成视频上传（completeVideoUpload）

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/products`。
- **上游方法与路径**：`POST /media/video/block/commit`。本操作为写入。

### 请求参数

公共顶层字段见 [业务操作请求字段](api.md#业务操作请求字段)。本操作 `operation=completeVideoUpload`；下表列出 `params` 内部字段。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `uploadId` | 字符串 | 是 | 视频初始化返回的 `upload_id`。 |
| `parts` | JSON 字符串 | 是 | 按上游分块提交格式组织同一任务的全部成功分块 `e_tag`。 |
| `title`、`coverUrl` | 字符串 | 是 | 视频标题、封面 URL。 |
| `videoUsage` | 字符串 | 否 | `pro_main_video` 为商品主视频，`im` 为会话视频。 |

### 响应结构

公共响应 envelope 见 [网关成功响应](api.md#网关成功响应)。以下为该业务结果的字段与含义。

| 响应字段 | 类型 | 说明 |
| --- | --- | --- |
| `data.video_id` | 字符串 | 上游受理后的视频 ID。作为 `videoId` 传给 `getVideo` 查询实际处理状态。 |
| `data.success`、`data.result_code`、`data.result_message` | 布尔值或布尔字符串、字符串、字符串 | 上游业务状态、结果码、说明。 |

[Lazada 视频提交 API](https://open.lazada.com/apps/doc/api?path=%2Fmedia%2Fvideo%2Fblock%2Fcommit)

[Lazada 商品操作](https://open.lazada.com/apps/doc/doc?docId=120945&nodeId=29614) [类目与属性](https://open.lazada.com/apps/doc/doc?docId=120946&nodeId=30715) [可售库存](https://open.lazada.com/apps/doc/doc?docId=121233&nodeId=42713)

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 按 [写入与续查](api.md#写入与续查) 核对原写记录及本节业务字段，不以 HTTP 200 单独判断业务完成。


## 接口：查询写入状态（operationStatus）

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/operationStatus`。读取 LinkFox 已有写记录，不重新调用上游写接口。

### 请求参数

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `connectionId` | 字符串 | 是 | 原写入的店铺连接，最长 36 字符。 |
| `requestId` | UUID 字符串 | 是 | 原写入 UUID，最长 36 字符。 |

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| `data` | null | 查询已存写记录不重取业务结果。 |
| `requestId` | 字符串或 null | 已存上游请求标识。 |
| `clientRequestId` | 字符串 | 原写入 UUID。 |
| `status` | 字符串 | `PENDING`、`SUCCEEDED`、`REJECTED`、`PARTIAL` 或 `UNKNOWN`。 |

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 查询成功不等于写入成功。按 [写入与续查](api.md#写入与续查) 处理原状态；记录不存在时核对原用户、连接及 UUID，不换 UUID 自动重放。
