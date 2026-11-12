---
name: linkfox-lazada-store-product
description: 查询和维护已授权 Lazada 店铺的商品，适用于查询商品、类目、品牌、仓库和质检状态，以及刊登商品、维护价格库存和迁移商品素材。
---

# Lazada 店铺商品管理

## 适用范围

### 适用

查询和维护已授权 Lazada 卖家店铺的商品，获取刊登和库存操作所需的辅助资料。

**场景速查**

| 用户表达 | 查询场景 |
| --- | --- |
| 查看这个店铺的商品，按状态或时间筛选 | 商品列表，按条件请求一页商品。 |
| 查这个卖家 SKU 对应的商品 | 商品列表，通过 `sku_seller_list` 筛选。 |
| 核对这件商品的属性或 SKU | 商品详情，使用该店铺的 `item_id`。 |
| 查刊登所需类目、属性、品牌或仓库 | 按站点查询辅助资料。 |
| 刊登、更新商品或维护价格和库存 | 核对商品与变更明细后执行相应操作。 |

### 边界

店铺绑定或授权失效时使用 `linkfox-lazada-store-auth`。促销活动使用 `linkfox-lazada-store-marketing`。

## 接口清单

| 操作 | LinkFox 网关与 Lazada 上游 | 接口文档 | 对应脚本 | 性质 |
| --- | --- | --- | --- | --- |
| 商品列表 `listProducts` | `POST /lazada/developerProxy` → `GET /products/get` | [接口说明](references/api.md#接口商品列表listproducts) | `scripts/list_products.py` | 只读 |
| 商品详情 `getProduct` | `POST /lazada/developerProxy` → `GET /product/item/get` | [接口说明](references/api.md#接口商品详情getproduct) | `scripts/get_product.py` | 只读 |
| 类目树 `getCategoryTree` | `POST /lazada/products` → `GET /category/tree/get` | [接口说明](references/product-operations.md#接口类目树getcategorytree) | `scripts/products_api.py getCategoryTree` | 只读 |
| 类目属性 `getCategoryAttributes` | `POST /lazada/products` → `GET /category/attributes/get` | [接口说明](references/product-operations.md#接口类目属性getcategoryattributes) | `scripts/products_api.py getCategoryAttributes` | 只读 |
| 品牌列表 `listBrands` | `POST /lazada/products` → `GET /category/brands/query` | [接口说明](references/product-operations.md#接口品牌列表listbrands) | `scripts/products_api.py listBrands` | 只读 |
| 商品质检 `getProductQcStatus` | `POST /lazada/products` → `GET /product/qc/status/get` | [接口说明](references/product-operations.md#接口商品质检getproductqcstatus) | `scripts/products_api.py getProductQcStatus` | 只读 |
| 仓库列表 `listWarehouses` | `POST /lazada/products` → `GET /rc/warehouse/get` | [接口说明](references/product-operations.md#接口仓库列表listwarehouses) | `scripts/products_api.py listWarehouses` | 只读 |
| 刊登商品 `createProduct` | `POST /lazada/products` → `POST /product/create` | [接口说明](references/product-operations.md#接口刊登商品createproduct) | `scripts/products_api.py createProduct` | 写入 |
| 更新商品 `updateProduct` | `POST /lazada/products` → `POST /product/update` | [接口说明](references/product-operations.md#接口更新商品updateproduct) | `scripts/products_api.py updateProduct` | 写入 |
| 更新价格和库存 `updatePriceQuantity` | `POST /lazada/products` → `POST /product/price_quantity/update` | [接口说明](references/product-operations.md#接口更新价格和库存updatepricequantity) | `scripts/products_api.py updatePriceQuantity` | 写入 |
| 设定可售库存 `updateSellableQuantity` | `POST /lazada/products` → `POST /product/stock/sellable/update` | [接口说明](references/product-operations.md#接口设定可售库存updatesellablequantity) | `scripts/products_api.py updateSellableQuantity` | 写入 |
| 增减可售库存 `adjustSellableQuantity` | `POST /lazada/products` → `POST /product/stock/sellable/adjust` | [接口说明](references/product-operations.md#接口增减可售库存adjustsellablequantity) | `scripts/products_api.py adjustSellableQuantity` | 写入 |
| 迁移公开图片 URL `migrateImage` | `POST /lazada/products` → `POST /image/migrate` | [接口说明](references/product-operations.md#接口迁移公开图片-urlmigrateimage) | `scripts/products_api.py migrateImage` | 写入 |
| 下架商品或 SKU `deactivateProduct` | `POST /lazada/products` → `POST /product/deactivate` | [接口说明](references/product-operations.md#接口下架商品或-skudeactivateproduct) | `scripts/products_api.py deactivateProduct` | 写入 |
| 删除指定 SKU `removeProduct` | `POST /lazada/products` → `POST /product/remove` | [接口说明](references/product-operations.md#接口删除指定-skuremoveproduct) | `scripts/products_api.py removeProduct` | 写入 |
| 批量迁移公开图片 `migrateImages` | `POST /lazada/products` → `POST /images/migrate` | [接口说明](references/product-operations.md#接口批量迁移公开图片migrateimages) | `scripts/products_api.py migrateImages` | 写入 |
| 批量迁移结果 `getImageMigrationResult` | `POST /lazada/products` → `GET /image/response/get` | [接口说明](references/product-operations.md#接口批量迁移结果getimagemigrationresult) | `scripts/products_api.py getImageMigrationResult` | 只读 |
| 本地图片上传 `uploadImage` | `POST /lazada/products` → `POST /image/upload` | [接口说明](references/product-operations.md#接口本地图片上传uploadimage) | `scripts/products_api.py uploadImage` | 写入 |
| 创建视频上传任务 `initVideoUpload` | `POST /lazada/products` → `POST /media/video/block/create` | [接口说明](references/product-operations.md#接口创建视频上传任务initvideoupload) | `scripts/products_api.py initVideoUpload` | 写入 |
| 上传视频分块 `uploadVideoBlock` | `POST /lazada/products` → `POST /media/video/block/upload` | [接口说明](references/product-operations.md#接口上传视频分块uploadvideoblock) | `scripts/products_api.py uploadVideoBlock` | 写入 |
| 完成视频上传 `completeVideoUpload` | `POST /lazada/products` → `POST /media/video/block/commit` | [接口说明](references/product-operations.md#接口完成视频上传completevideoupload) | `scripts/products_api.py completeVideoUpload` | 写入 |
| 视频详情 `getVideo` | `POST /lazada/products` → `GET /media/video/get` | [接口说明](references/product-operations.md#接口视频详情getvideo) | `scripts/products_api.py getVideo` | 只读 |
| 视频额度 `getVideoQuota` | `POST /lazada/products` → `GET /media/video/quota/get` | [接口说明](references/product-operations.md#接口视频额度getvideoquota) | `scripts/products_api.py getVideoQuota` | 只读 |
| 删除视频 `removeVideo` | `POST /lazada/products` → `POST /media/video/remove` | [接口说明](references/product-operations.md#接口删除视频removevideo) | `scripts/products_api.py removeVideo` | 写入 |
| 查询写入状态 `operationStatus` | `POST /lazada/operationStatus` | [写入与续查](references/product-operations.md#接口查询写入状态operationstatus) | `scripts/products_api.py operationStatus` | 只读 |

## 前置条件

配置当前用户的 LinkFox Key，再通过 `linkfox-lazada-store-auth` 确定已授权的目标店铺和站点。后续查询使用对应的 `connectionId`，店铺授权由服务端管理。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md` 及接口清单中的对应文档。
- **脚本调用（推荐）**：使用 Python 3.9+，`python <脚本路径> '<JSON 参数>' [--inline] [--no-cache]`。
- **业务操作入口**：`python scripts/products_api.py <操作> '<JSON 参数>' [--inline] [--no-cache]`，也可用 `--params-file <UTF-8 JSON 文件>` 提供参数。
- **成本约束**：本技能不消耗算力，业务调用通过输出预检后实时请求一次，不启用 24 小时响应缓存。按用户任务范围分页或查询原申请／写记录，不因失败或空结果自动扩大范围或重放写入。

本地输入、默认值、构参映射及保存结果见 [脚本使用说明](references/script-usage.md)。

### 输出策略

- 始终保存可保存的完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/<技能名>-<操作>-<时间>.json`。会话优先取 `SESSION_ID`。输出或会话元数据不可写时，在发请求前报错。
- 响应体不超过 8000 字节：保存后，将完整脱敏 JSON 打印到标准输出。
- 响应体超过 8000 字节：保存后，标准输出仅展示摘要，包括顶层字段、可用诊断、最大列表字段的长度和最多前三项样本。
- 添加 `--inline` 可强制全量打印可保存数据，同时仍保存文件。
- HTTP、网关或响应格式错误时，脚本保存可用的脱敏诊断并以非零状态退出。

先通过摘要判断数据是否足够。以 `Saved full response:` 后的实际文件路径为准；需要具体字段时，优先使用 `jq` 或 `ConvertFrom-Json` 从保存的 JSON 文件按需提取，避免将整份响应载入上下文。

## 执行规则

1. 按状态、时间或卖家 SKU 筛选时查询商品列表。核对具体商品时，使用用户给出的商品 ID 或列表中确认的商品 ID 查询详情。
2. 需要下一页时，按接口参考推进偏移量。
3. 刊登前先确认叶子类目、必填属性、品牌和素材。更新价格库存前核对目标 SKU、站点、仓库和当前状态，区分库存设定值与增减量。
4. 写操作前向用户列明目标、变更及影响，取得明确授权。使用新 UUID 提交已确认的动作。超时或结果不明时，用同一 UUID 查询 `operationStatus`。
5. 用户要求迁移图片时，使用明确指定的公开 URL。批量迁移取得 `batch_id` 后按原 ID 查结果。本地图片上传和视频分块上传按素材接口的格式、大小和上传顺序执行。

### 算力消耗

本 Skill 的商品查询、商品管理、辅助资料及写入状态查询均为 0 算力/次。

**声明**：算力消耗以实际扣除为准；如因需要调整算力消耗标准，恕不另行通知。最终解释权归 LinkFox 官方所有。

### 解决认证和算力问题

出现以下情况时，按 `references/onboarding.md` 的指引处理：

- 未配置接口密钥：`LINKFOX_AGENT_API_KEY` 和 `LINKFOXAGENT_API_KEY` 均为空。
- HTTP 状态码为 `401` 或 `402`；先结合接口诊断确认是 LinkFox 用户认证或计费问题。
- 响应提示算力或余额不足、计费不足、配额超限、套餐到期或需要充值。英文错误消息也按其含义判断。

Lazada 店铺授权失效、卖家未验证、应用权限或代理限制按接口参考处理。短信、登录和算力订单按用户已授权范围执行；订单结果不明先核对原订单。可选二维码依赖为 qrcode 和 Pillow，未安装时使用支付链接，不静默安装。

### 约束与建议

- 展示时注明店铺、站点和返回范围。空数组表示本次没有匹配商品，字段缺失时保留为未知。
- 商品 ID 和卖家 SKU 按字符串保留。同一个 SKU 在不同店铺可能对应不同商品，详情使用所选店铺返回的商品 ID。

## 使用示例

替换命令中的店铺连接和商品 ID。

```sh
python scripts/list_products.py '{"connectionId":"11111111-1111-4111-8111-111111111111","queryParams":{"offset":0,"limit":20}}'
python scripts/products_api.py getCategoryTree '{"connectionId":"11111111-1111-4111-8111-111111111111","params":{}}'
python scripts/get_product.py '{"connectionId":"11111111-1111-4111-8111-111111111111","queryParams":{"item_id":"123456789"}}'
```

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引整理脱敏反馈，不要打断用户当前流程。仅在用户授权发送后提交。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。
