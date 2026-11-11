# Lazada 店铺商品管理接口

## 公共规则

### 调用规范

- LinkFox 网关 `POST /lazada/products` 接收 `connectionId`、`operation` 和对象 `params`。读操作可省略无参数的 `params`。按原样传入已授权记录的连接 ID。
- 请求头、网关地址、超时和 LinkFox Key 配置见 [接口总览](api.md)。`scripts/products_api.py` 从命令行选择固定操作，支持内联 JSON 或 `--params-file <UTF-8 JSON 文件>`。每次业务调用均为实时请求。
- `params` 按下表传 JSON 原生对象、数组或文本。接口明确要求 JSON 或 XML 文本时，使用 JSON 字符串。采用真实上一步返回的 ID，避免因浮点数转换丢失精度。

### 写入与续查

已确认的写动作请求另需 `requestId` UUID。后端按当前用户、店铺连接、UUID 和请求内容识别重复请求。结果不明时执行 `python scripts/products_api.py operationStatus '<JSON 参数>'`，输入仅含 `connectionId` 和原 `requestId`。该命令调用 LinkFox `POST /lazada/operationStatus`。

| CLI 保存字段 | 类型 | 含义 |
| --- | --- | --- |
| `data` | 对象、数组或 null | 脱敏业务响应，查询写记录或提交重复请求时可能为 null。各操作表格均以保存后的路径为准。 |
| `requestId` | 字符串或 null | Lazada 上游请求标识。 |
| `clientRequestId` | 字符串 | 写动作原 UUID，供状态查询使用。只读业务查询无此字段。 |
| `status` | 字符串 | 写记录状态。只读业务查询无此字段。 |
| `success` | 布尔值 | CLI 调用结果。写入仅 `SUCCEEDED` 视为成功。状态查询成功后仍需读取 `status`。 |

`PENDING` 时按原 UUID 续查。`SUCCEEDED` 表示上游确认写入，仍需结合各项业务结果。`REJECTED` 时核对失败原因。`PARTIAL` 时逐项检查成功与失败范围。`UNKNOWN` 时核对店铺的实际状态。写操作失败或结果不明时保留原 UUID，避免自动重放。部署侧默认关闭写入，需由接入方启用。

`LAZADA_WRITES_DISABLED` 表示部署未启用写入。`LAZADA_REQUEST_ID_CONFLICT` 时检查原 UUID 与原请求参数。`LAZADA_OPERATION_NOT_FOUND` 时核对店铺连接和 UUID，并检查目标当前状态。

## 类目树（`getCategoryTree`）

上游 `GET /category/tree/get`。只读。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `language_code` | 字符串 | 否 | 默认 `en_US`，各站可用。站点语言按市场选用 `en_SG`、`th_TH`、`id_ID`、`vi_VN`、`fil_PH` 或 `ms_MY`。 |

| CLI 保存字段 | 类型 | 说明 |
| --- | --- | --- |
| `data` | 对象数组 | 该站点的类目树。 |
| `data[].category_id`、`data[].name` | 字符串 | 类目 ID、名称。 |
| `data[].leaf`、`data[].var` | 布尔值 | 是否叶子类目、是否支持变体。 |
| `data[].children` | 对象数组 | 子类目，节点结构相同。 |

## 类目属性（`getCategoryAttributes`）

上游 `GET /category/attributes/get`。只读。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `primary_category_id` | 正整数或数字字符串 | 是 | 从当前站点类目树取得的类目 ID。 |
| `language_code` | 字符串 | 否 | 语言和默认值同类目树。 |

| CLI 保存字段 | 类型 | 说明 |
| --- | --- | --- |
| `data` | 对象数组 | 类目属性定义。 |
| `data[].id`、`data[].name`、`data[].label` | 字符串 | 属性 ID、请求键、展示标签。 |
| `data[].is_mandatory`、`data[].is_sale_prop` | 整数或数字字符串 | 是否必填、是否为销售属性。 |
| `data[].attribute_type`、`data[].input_type` | 字符串 | 属性类型和输入方式。 |
| `data[].options` | 对象数组 | 选项值，条目包含字符串字段 `id`、`name`、`en_name`。 |
| `data[].advanced`、`data[].unit` | 对象 | 扩展属性和数值单位规则。`unit.type` 为字符串数组，`numericMin`、`numericMax` 为字符串，`precision` 为整数或数字字符串。 |

## 品牌列表（`listBrands`）

上游 `GET /category/brands/query`。只读。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `startRow` | 整数或数字字符串 | 是 | 要跳过的记录数，非负。 |
| `pageSize` | 整数或数字字符串 | 是 | 该请求的页容量，1 至 200。 |

| CLI 保存字段 | 类型 | 说明 |
| --- | --- | --- |
| `data.module` | 对象数组 | 品牌列表，含 `brand_id`、`name`、`name_en`、`global_identifier` 字符串字段。 |
| `data.start_row`、`data.page_index`、`data.page_size` | 整数或数字字符串 | 起点、页索引、页容量。 |
| `data.total_record`、`data.total_page` | 整数或数字字符串 | 总记录数、总页数。 |
| `data.enable_total` | 布尔值或布尔字符串 | 是否提供总数统计。 |

## 商品质检（`getProductQcStatus`）

上游 `GET /product/qc/status/get`。只读。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `offset` | 整数或数字字符串 | 是 | 跳过的审核记录数，非负。 |
| `limit` | 整数或数字字符串 | 是 | 要返回的最大记录数，正整数。 |
| `seller_skus` | 字符串数组 | 是 | 该店铺待查询的卖家 SKU，至少一项。 |

| CLI 保存字段 | 类型 | 说明 |
| --- | --- | --- |
| `data` | 对象数组 | 审核记录。 |
| `data[].seller_sku`、`data[].status` | 字符串 | 卖家 SKU、审核状态。 |
| `data[].reason`、`data[].data_changed` | 字符串 | 原因及上游数据变更标志。 |

## 仓库列表（`listWarehouses`）

上游 `GET /rc/warehouse/get`。只读。

无业务参数，`params` 可使用 `{}`。

| CLI 保存字段 | 类型 | 说明 |
| --- | --- | --- |
| `data.result.module` | 对象 | Lazada 仓库载荷。按实际仓库标识和站点选择库存操作目标。 |
| `data.result.success` | 对象 | 上游成功信息。 |
| `data.result.not_success`、`data.result.repeated`、`data.result.retry` | 布尔值或布尔字符串 | 上游失败、重复、重试标志。 |
| `data.result.error_code` | 字符串 | 上游错误码，按实际返回解释。 |

## 刊登商品（`createProduct`）

上游 `POST /product/create`。写入。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `payload` | 字符串 | 是 | Lazada CreateProduct 要求的 JSON 或 XML 文本。先准备叶子类目、属性、SKU 和 Lazada 图片地址。 |

| CLI 保存字段 | 类型 | 说明 |
| --- | --- | --- |
| `data.item_id` | 字符串 | 上游接受创建后给出的商品 ID。 |
| `data.item_status` | 字符串 | 商品状态，按实际质检结果核对是否可售。 |
| `data.sku_list` | 对象数组 | SKU 结果，含 `sku_id`、`seller_sku`、`shop_sku` 字符串字段。 |

## 更新商品（`updateProduct`）

上游 `POST /product/update`。写入。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `payload` | 字符串 | 是 | Lazada UpdateProduct 要求的 JSON 或 XML 文本。使用真实商品和 SKU 标识，预览修改字段。 |

| CLI 保存字段 | 类型 | 说明 |
| --- | --- | --- |
| `data.item_status` | 字符串 | 上游返回的商品状态，可能省略。 |
| `data.variation` | 对象 | 可选。变体定义可能含 `Variation1` 至 `Variation4`，每项包含 `name`、`has_image`、`customize`、`options`。 |

## 更新价格和库存（`updatePriceQuantity`）

上游 `POST /product/price_quantity/update`。写入。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `payload` | 字符串 | 是 | Lazada UpdatePriceQuantity 请求文本。核对 SKU、价格、币种及库存口径。 |

| CLI 保存字段 | 类型 | 说明 |
| --- | --- | --- |
| `data` | 对象 | 上游业务结果，可能是空对象。需要核实实际值时查询商品。 |

## 设定可售库存（`updateSellableQuantity`）

上游 `POST /product/stock/sellable/update`。写入。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `payload` | 字符串 | 是 | Lazada UpdateSellableQuantity 请求文本，按确认的目标值覆盖可售库存。 |

| CLI 保存字段 | 类型 | 说明 |
| --- | --- | --- |
| `data` | 对象 | 上游结果，可能为空对象。 |

## 增减可售库存（`adjustSellableQuantity`）

上游 `POST /product/stock/sellable/adjust`。写入。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `payload` | 字符串 | 是 | Lazada AdjustSellableQuantity 请求文本，按确认的增减量调整可售库存。 |

| CLI 保存字段 | 类型 | 说明 |
| --- | --- | --- |
| `data` | 对象 | 上游结果，可能为空对象。 |

## 迁移公开图片 URL（`migrateImage`）

上游 `POST /image/migrate`。写入。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `payload` | 字符串 | 是 | XML 请求文本，在 `Request/Image/Url` 放入用户指定的可访问公开图片 URL。 |

| CLI 保存字段 | 类型 | 说明 |
| --- | --- | --- |
| `data.image.url`、`data.image.hash_code` | 字符串 | Lazada 图片地址及哈希。刊登或更新使用返回的 `url`。 |

[Lazada 图片迁移说明](https://open.lazada.com/apps/doc/doc?docId=120947&nodeId=30718)

## 下架商品或 SKU（`deactivateProduct`）

上游 `POST /product/deactivate`。写入。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `apiRequestBody` | 字符串 | 是 | Lazada 请求文本。包含实际 `ItemId`，可用 `Skus` 指定下架范围。 |

| CLI 保存字段 | 类型 | 说明 |
| --- | --- | --- |
| `data` | 对象 | 上游下架结果，可能为空对象。 |

## 删除指定 SKU（`removeProduct`）

上游 `POST /product/remove`。写入。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `sku_id_list` | JSON 数组字符串 | 二选一 | 1 至 50 个 `SkuId_<itemId>_<skuId>` 字符串。 |
| `seller_sku_list` | JSON 数组字符串 | 二选一 | 1 至 50 个卖家 SKU 字符串。 |

先从目标店铺查询 SKU 并确认删除范围，再提交其中一个参数。

| CLI 保存字段 | 类型 | 说明 |
| --- | --- | --- |
| `data` | 对象 | 上游删除结果，可能为空对象。 |

## 批量迁移公开图片（`migrateImages`）

上游 `POST /images/migrate`。写入。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `payload` | 字符串 | 是 | XML 请求文本。`Request/Images` 下为每张图传一个 `Url`。最多 8 个用户指定的公开 JPG 或 PNG 图片 URL。 |

| CLI 保存字段 | 类型 | 说明 |
| --- | --- | --- |
| `data.batch_id` | 字符串 | 已受理的迁移批次号。将原编号传给 `getImageMigrationResult`，按图片核对最终结果。 |

[Lazada 图片迁移说明](https://open.lazada.com/apps/doc/doc?docId=120947&nodeId=30718)

## 批量迁移结果（`getImageMigrationResult`）

上游 `GET /image/response/get`。只读。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `batch_id` | 字符串 | 是 | 批量迁移返回的原始批次号。 |

| CLI 保存字段 | 类型 | 说明 |
| --- | --- | --- |
| `data.images` | 对象数组 | 成功图片，条目包含 `url` 和 `hash_code` 字符串。只将成功图片地址交给下游刊登。 |
| `data.errors` | 对象数组 | 失败图片，条目包含 `field`、`msg`、`original_url` 字符串。 |

## 视频详情（`getVideo`）

上游 `GET /media/video/get`。只读。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `videoId` | 正整数或数字字符串 | 是 | 该店铺的视频 ID，使用上传提交返回的 `video_id`。 |

| CLI 保存字段 | 类型 | 说明 |
| --- | --- | --- |
| `data.state` | 字符串 | `READY_FOR_TRANSCODE`、`TRANSCODING`、`TRANSCODE_FAILED`、`READY_FOR_AUDIT`、`AUDIT_FAILED`、`AUDIT_SUCCESS` 或 `DELETED`。 |
| `data.title`、`data.cover_url`、`data.video_url` | 字符串 | 视频标题、封面地址、视频地址。 |
| `data.success` | 布尔值或布尔字符串 | 上游业务状态。 |
| `data.result_code`、`data.result_message` | 字符串 | 上游结果码、结果说明。 |

## 视频额度（`getVideoQuota`）

上游 `GET /media/video/quota/get`。只读。无业务参数，`params` 可使用 `{}`。

| CLI 保存字段 | 类型 | 说明 |
| --- | --- | --- |
| `data.capacity_size`、`data.used_size` | 整数或数字字符串 | 总额度、已用空间，单位按上游实际口径。 |
| `data.success`、`data.result_code`、`data.result_message` | 布尔值或布尔字符串、字符串、字符串 | 上游业务状态、结果码、说明。 |

## 删除视频（`removeVideo`）

上游 `POST /media/video/remove`。写入。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `videoId` | 正整数或数字字符串 | 是 | 视频 ID。提交前核对店铺、视频及关联商品并取得明确授权。 |

| CLI 保存字段 | 类型 | 说明 |
| --- | --- | --- |
| `data.success`、`data.result_code`、`data.result_message` | 布尔值或布尔字符串、字符串、字符串 | 上游业务状态、结果码、说明。 |

## 本地图片上传（`uploadImage`）

上游 `POST /image/upload`。写入。此操作需要紫鸟 multipart 通道验证和单独开关启用。

当本地图片或分块视频上传未启用时，脚本返回 `LAZADA_UPLOADS_DISABLED`。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `image` | Base64 字符串 | 是 | 用户明确选中的 JPG 或 PNG，原文件不超过 1 MiB。 |

只通过 `--params-file` 传入解析后位于当前工作目录内的私有 UTF-8 JSON 文件。参数文件最大 1,406,296 字节。

| CLI 保存字段 | 类型 | 说明 |
| --- | --- | --- |
| `data.image.url`、`data.image.hash_code` | 字符串 | Lazada 图片地址及哈希。刊登使用返回的 `url`。 |

## 创建视频上传任务（`initVideoUpload`）

上游 `POST /media/video/block/create`。写入。此操作需要紫鸟 multipart 通道验证和单独开关启用。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `fileName` | 字符串 | 是 | 实际视频文件名，不带路径。 |
| `fileBytes` | 整数或数字字符串 | 是 | 视频总字节数，至少 1 字节且小于 100 MiB。 |

| CLI 保存字段 | 类型 | 说明 |
| --- | --- | --- |
| `data.upload_id` | 字符串 | 上传任务 ID。后续请求将该值传给 `uploadId`。 |
| `data.success`、`data.result_code`、`data.result_message` | 布尔值或布尔字符串、字符串、字符串 | 上游业务状态、结果码、说明。 |

## 上传视频分块（`uploadVideoBlock`）

上游 `POST /media/video/block/upload`。写入。此操作需要紫鸟 multipart 通道验证和单独开关启用。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `uploadId` | 字符串 | 是 | 视频初始化返回的 `upload_id`。 |
| `blockNo` | 整数或数字字符串 | 是 | 分块序号，从 0 开始且小于总块数。 |
| `blockCount` | 整数或数字字符串 | 是 | 总块数，1 至 1000。 |
| `file` | Base64 字符串 | 是 | 选中的视频分块，原始分块不超过 3 MiB。 |

只通过 `--params-file` 传入解析后位于当前工作目录内的私有 UTF-8 JSON 文件。参数文件最大 4,202,496 字节。

| CLI 保存字段 | 类型 | 说明 |
| --- | --- | --- |
| `data.e_tag` | 字符串 | 成功分块标识，按序号记录。 |
| `data.success`、`data.result_code`、`data.result_message` | 布尔值或布尔字符串、字符串、字符串 | 上游业务状态、结果码、说明。 |

## 完成视频上传（`completeVideoUpload`）

上游 `POST /media/video/block/commit`。写入。此操作需要紫鸟 multipart 通道验证和单独开关启用。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `uploadId` | 字符串 | 是 | 视频初始化返回的 `upload_id`。 |
| `parts` | JSON 字符串 | 是 | 按上游分块提交格式组织同一任务的全部成功分块 `e_tag`。 |
| `title`、`coverUrl` | 字符串 | 是 | 视频标题、封面 URL。 |
| `videoUsage` | 字符串 | 否 | `pro_main_video` 为商品主视频，`im` 为会话视频。 |

| CLI 保存字段 | 类型 | 说明 |
| --- | --- | --- |
| `data.video_id` | 字符串 | 上游受理后的视频 ID。作为 `videoId` 传给 `getVideo` 查询实际处理状态。 |
| `data.success`、`data.result_code`、`data.result_message` | 布尔值或布尔字符串、字符串、字符串 | 上游业务状态、结果码、说明。 |

[Lazada 视频提交 API](https://open.lazada.com/apps/doc/api?path=%2Fmedia%2Fvideo%2Fblock%2Fcommit)

[Lazada 商品操作](https://open.lazada.com/apps/doc/doc?docId=120945&nodeId=29614) [类目与属性](https://open.lazada.com/apps/doc/doc?docId=120946&nodeId=30715) [可售库存](https://open.lazada.com/apps/doc/doc?docId=121233&nodeId=42713)
