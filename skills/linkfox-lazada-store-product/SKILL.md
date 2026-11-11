---
name: linkfox-lazada-store-product
description: 查询和维护已授权 Lazada 店铺的商品，适用于查询商品、类目、品牌、仓库和质检状态，以及刊登商品、维护价格库存和迁移商品素材。
---

# Lazada 店铺商品管理

## 适用范围

### 适用

查询和维护已授权 Lazada 卖家店铺的商品，获取刊登和库存操作所需的辅助资料。

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

| 操作 | LinkFox 网关与 Lazada 上游 | 对应脚本 | 接口文档 | 性质 |
| --- | --- | --- | --- | --- |
| 商品列表 `listProducts` | `POST /lazada/developerProxy` → `GET /products/get` | `scripts/list_products.py` | [接口说明](references/api.md#商品列表) | 只读 |
| 商品详情 `getProduct` | `POST /lazada/developerProxy` → `GET /product/item/get` | `scripts/get_product.py` | [接口说明](references/api.md#商品详情) | 只读 |
| 类目树 `getCategoryTree` | `POST /lazada/products` → `GET /category/tree/get` | `scripts/products_api.py getCategoryTree` | [接口说明](references/product-operations.md#类目树getcategorytree) | 只读 |
| 类目属性 `getCategoryAttributes` | `POST /lazada/products` → `GET /category/attributes/get` | `scripts/products_api.py getCategoryAttributes` | [接口说明](references/product-operations.md#类目属性getcategoryattributes) | 只读 |
| 品牌列表 `listBrands` | `POST /lazada/products` → `GET /category/brands/query` | `scripts/products_api.py listBrands` | [接口说明](references/product-operations.md#品牌列表listbrands) | 只读 |
| 商品质检 `getProductQcStatus` | `POST /lazada/products` → `GET /product/qc/status/get` | `scripts/products_api.py getProductQcStatus` | [接口说明](references/product-operations.md#商品质检getproductqcstatus) | 只读 |
| 仓库列表 `listWarehouses` | `POST /lazada/products` → `GET /rc/warehouse/get` | `scripts/products_api.py listWarehouses` | [接口说明](references/product-operations.md#仓库列表listwarehouses) | 只读 |
| 刊登商品 `createProduct` | `POST /lazada/products` → `POST /product/create` | `scripts/products_api.py createProduct` | [接口说明](references/product-operations.md#刊登商品createproduct) | 写入 |
| 更新商品 `updateProduct` | `POST /lazada/products` → `POST /product/update` | `scripts/products_api.py updateProduct` | [接口说明](references/product-operations.md#更新商品updateproduct) | 写入 |
| 更新价格和库存 `updatePriceQuantity` | `POST /lazada/products` → `POST /product/price_quantity/update` | `scripts/products_api.py updatePriceQuantity` | [接口说明](references/product-operations.md#更新价格和库存updatepricequantity) | 写入 |
| 设定可售库存 `updateSellableQuantity` | `POST /lazada/products` → `POST /product/stock/sellable/update` | `scripts/products_api.py updateSellableQuantity` | [接口说明](references/product-operations.md#设定可售库存updatesellablequantity) | 写入 |
| 增减可售库存 `adjustSellableQuantity` | `POST /lazada/products` → `POST /product/stock/sellable/adjust` | `scripts/products_api.py adjustSellableQuantity` | [接口说明](references/product-operations.md#增减可售库存adjustsellablequantity) | 写入 |
| 迁移公开图片 URL `migrateImage` | `POST /lazada/products` → `POST /image/migrate` | `scripts/products_api.py migrateImage` | [接口说明](references/product-operations.md#迁移公开图片-urlmigrateimage) | 写入 |
| 下架商品或 SKU `deactivateProduct` | `POST /lazada/products` → `POST /product/deactivate` | `scripts/products_api.py deactivateProduct` | [接口说明](references/product-operations.md#下架商品或-skudeactivateproduct) | 写入 |
| 删除指定 SKU `removeProduct` | `POST /lazada/products` → `POST /product/remove` | `scripts/products_api.py removeProduct` | [接口说明](references/product-operations.md#删除指定-skuremoveproduct) | 写入 |
| 批量迁移公开图片 `migrateImages` | `POST /lazada/products` → `POST /images/migrate` | `scripts/products_api.py migrateImages` | [接口说明](references/product-operations.md#批量迁移公开图片migrateimages) | 写入 |
| 批量迁移结果 `getImageMigrationResult` | `POST /lazada/products` → `GET /image/response/get` | `scripts/products_api.py getImageMigrationResult` | [接口说明](references/product-operations.md#批量迁移结果getimagemigrationresult) | 只读 |
| 本地图片上传 `uploadImage` | `POST /lazada/products` → `POST /image/upload` | `scripts/products_api.py uploadImage` | [接口说明](references/product-operations.md#本地图片上传uploadimage) | 写入，需启用素材通道 |
| 创建视频上传任务 `initVideoUpload` | `POST /lazada/products` → `POST /media/video/block/create` | `scripts/products_api.py initVideoUpload` | [接口说明](references/product-operations.md#创建视频上传任务initvideoupload) | 写入，需启用素材通道 |
| 上传视频分块 `uploadVideoBlock` | `POST /lazada/products` → `POST /media/video/block/upload` | `scripts/products_api.py uploadVideoBlock` | [接口说明](references/product-operations.md#上传视频分块uploadvideoblock) | 写入，需启用素材通道 |
| 完成视频上传 `completeVideoUpload` | `POST /lazada/products` → `POST /media/video/block/commit` | `scripts/products_api.py completeVideoUpload` | [接口说明](references/product-operations.md#完成视频上传completevideoupload) | 写入，需启用素材通道 |
| 视频详情 `getVideo` | `POST /lazada/products` → `GET /media/video/get` | `scripts/products_api.py getVideo` | [接口说明](references/product-operations.md#视频详情getvideo) | 只读 |
| 视频额度 `getVideoQuota` | `POST /lazada/products` → `GET /media/video/quota/get` | `scripts/products_api.py getVideoQuota` | [接口说明](references/product-operations.md#视频额度getvideoquota) | 只读 |
| 删除视频 `removeVideo` | `POST /lazada/products` → `POST /media/video/remove` | `scripts/products_api.py removeVideo` | [接口说明](references/product-operations.md#删除视频removevideo) | 写入 |
| 查询写入状态 `operationStatus` | `POST /lazada/operationStatus` | `scripts/products_api.py operationStatus` | [写入与续查](references/product-operations.md#写入与续查) | 只读 |

## 前置条件

配置当前用户的 LinkFox Key，再通过 `linkfox-lazada-store-auth` 确定已授权的目标店铺和站点。后续查询使用对应的 `connectionId`，店铺授权由服务端管理。

## 执行方式

- **脚本调用（推荐）**。使用 Python 3.9+ 运行 `python <脚本路径> '<JSON 参数>' [--inline] [--no-cache]`。
- **商品管理**。运行 `python scripts/products_api.py <操作> '<JSON 参数>' [--inline] [--no-cache]`，也可用 `--params-file <UTF-8 JSON 文件>` 提供参数。
- **接口调用**。请求字段、成功结构和错误处理见 [接口参考](references/api.md)。
- **调用约束**。业务脚本通过预检后发起一次实时请求。按用户指定的条件查询，后续翻页或扩大范围按用户要求进行。

### 输出策略

- 可保存的结果写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/<技能名>-<操作>-<时间>.json`。会话优先取 `SESSION_ID`。输出或会话元数据不可写时，在发请求前报错。
- 成功结果不超过 8000 字节时，保存后打印完整 JSON。更大的结果打印摘要，主要列表最多展示前三项。`--inline` 可打印全部可保存数据，同时仍保存文件。
- HTTP、网关或响应格式错误时，脚本保存可用的脱敏诊断并以非零状态退出。
- 以 `Saved full response:` 后的实际文件路径为准。需要更多字段时，从保存的 JSON 按需提取。

## 执行规则

1. 按状态、时间或卖家 SKU 筛选时查询商品列表。核对具体商品时，使用用户给出的商品 ID 或列表中确认的商品 ID 查询详情。
2. 需要下一页时，按接口参考推进偏移量。
3. 刊登前先确认叶子类目、必填属性、品牌和素材。更新价格库存前核对目标 SKU、站点、仓库和当前状态，区分库存设定值与增减量。
4. 写操作前向用户列明目标、变更及影响，取得明确授权。使用新 UUID 提交已确认的动作。超时或结果不明时，用同一 UUID 查询 `operationStatus`。
5. 用户要求迁移图片时，使用明确指定的公开 URL。批量迁移取得 `batch_id` 后按原 ID 查结果。本地图片上传和分块视频上传需由接入方确认紫鸟通道并启用后才可执行。

### 算力消耗

本 Skill 的商品查询、商品管理、辅助资料及写入状态查询均为 0 算力/次。算力消耗以网关实际计费配置为准。

### 解决认证和算力问题

LinkFox Key 未配置或已确认无效时，按 [认证和算力指引](references/onboarding.md) 检查。遇到 401、402 或 403 时，先按 [错误处理](references/api.md#错误处理) 区分网关问题、店铺授权失效与代理限制。

发送短信或使用验证码登录前先取得用户同意。创建算力订单前确认套餐、金额和支付方式。下单结果不明时先核对已有订单。安装了 qrcode 和 Pillow 时可生成二维码图片，也可使用支付链接。

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

技能出现错误、指引不清或结果不符合预期时，可按 [Feedback](references/api.md#feedback) 整理脱敏摘要。用户授权发送后再提交。

---

更多跨境电商技能见 [LinkFox Skill](https://skill.linkfox.com/)。
