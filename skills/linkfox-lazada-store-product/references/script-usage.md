# 脚本输入、构参与本地输出

网关参数与响应定义见 [api.md](api.md)。本文件说明本地 CLI 输入、构参和保存结果；CLI 补充字段不是网关 DTO。业务字段以各接口参考为准。

## 共享脚本约定

### 脚本输入与构参

使用 Python 3.9+，普通业务入口和公共调用器仅用标准库。具名脚本接受一个 JSON 对象；带操作名的入口接受 `<操作> '<JSON 参数>'` 或 `<操作> --params-file <UTF-8 JSON 文件>`，两种参数来源互斥。各操作名大小写固定，无额外别名。

| 参数／选项 | 类型 | 默认／说明 |
|---|---|---|
| `connectionId` | 字符串 | 从当前用户店铺列表原样取值，不复用其他用户连接。 |
| `params` | 对象 | 业务操作默认 `{}`，有必填业务参数时仍须提供；原生对象／数组不转换为字符串，明确要求 JSON／XML 文本的字段除外。 |
| `queryParams` | 对象 | 商品／订单只读脚本默认 `{}`，按操作校验必填查询条件；不接受 `params` 别名。 |
| `requestId` | 字符串 | 写入或续查须提供带连字符 UUID，脚本转成小写；不自动生成，不用于只读业务查询。 |
| `--params-file` | CLI 选项 | 仅带操作名的入口支持，读取 UTF-8／UTF-8 BOM JSON；不上传参数文件本身。 |
| `--inline` | CLI 开关 | 默认关闭，开启时打印全部可保存数据，同时仍保存文件。 |
| `--no-cache` | CLI 开关 | 所有业务调用均实时执行，无缓存读写；保留此兼容选项，不允许重试或跳过保存。 |

网关与双 Key 的优先级、请求头及超时见 [公共规则](api.md#公共规则)。未知顶层字段会在请求前拒绝；业务层只构参、检查业务结果，公共 `call_api.run` 统一传输和保存。ID 保持原类型和精度，不把字符串 ID 转成浮点数。

### 脚本输出与业务结果

输出先经过预检，再发起一次请求，不自动重试。结果保存到当前工作目录 `linkfox/<YYYY-MM-DD>/<session>/data/`，优先使用 `SESSION_ID`，缺省使用时间和随机标识；文件名包含技能、操作、时间及随机后缀。输出或元数据不可写时在请求前失败，不回退到临时目录。

| 本地字段 | 类型 | 说明 |
|---|---|---|
| `data` | 对象、数组或操作允许的标量／null | 去除可选网关外层包装后的业务结果，保留内层层次和类型；凭据与不应展示的敏感字段被移除。 |
| `requestId` | 字符串或 null | 上游请求标识。 |
| `clientRequestId` | 字符串 | 写入／续查使用的原 UUID，异常时仍尽可能保留。 |
| `status` | 字符串 | 原写记录或授权申请状态，不与 HTTP 状态混用。 |
| `success` | 布尔值 | CLI 调用结果。写入仅 `SUCCEEDED` 为 true；成功查询状态时仍须检查原 `status`。 |
| `httpStatus`、`errcode`、`errorCode`、`code` | 整数或字符串，可缺省 | 失败时可保留的网关传输诊断；不等于上游 HTTP。 |
| `error` | 字符串，可缺省 | 本地错误分类。 |
| `traceId`、`upstreamCode`、`upstreamRequestId` | 字符串，可缺省 | 经过格式校验的跟踪标识或从服务端安全消息提取的上游诊断。 |

响应不超过 8000 字节时打印完整脱敏 JSON；较大响应打印顶层字段、诊断和最大列表的长度及最多前三项样本。以 `Saved full response:` 后的实际路径为准。`--inline` 不解除脱敏。业务失败、HTTP／网关／结构异常为非零退出；本地参数／输出预检失败通常为 2，远程失败为 1，成功为 0。原始错误正文、Key 和店铺令牌不保存。

`REAUTHORIZATION_REQUIRED` 先核对店铺授权，`LAZADA_PROXY_FORBIDDEN` 核对代理出口；`SellerNotVerified` 表示卖家未验证；范围和权限问题不当作 LinkFox 登录或计费故障。写入结果不明时仅用原 UUID 查询状态，核对目标实际状态后再决定下一步。

## 接口：商品列表（listProducts）

### 脚本输入与构参

`python scripts/list_products.py '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `queryParams` | 对象 | 默认 `{}`，本操作必填项、类型及分页默认值见 [接口请求参数](api.md#接口商品列表listproducts)；不展开为顶层字段。 |

脚本固定填入 `operation=listProducts`，不接受输入额外覆盖。

网关及上游映射为 `POST /lazada/developerProxy` → `GET /products/get`。参数约束与业务字段见 [接口说明](api.md#接口商品列表listproducts)。

### 脚本输出与业务结果

按 [接口响应结构](api.md#接口商品列表listproducts) 保留业务 `data` 路径；去除可选外层网关包装，补充本地 `success`。有效对象／数组及合同允许的空结果成功；格式错误非零退出。

## 接口：商品详情（getProduct）

### 脚本输入与构参

`python scripts/get_product.py '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `queryParams` | 对象 | 默认 `{}`，本操作必填项、类型及分页默认值见 [接口请求参数](api.md#接口商品详情getproduct)；不展开为顶层字段。 |

脚本固定填入 `operation=getProduct`，不接受输入额外覆盖。

网关及上游映射为 `POST /lazada/developerProxy` → `GET /product/item/get`。参数约束与业务字段见 [接口说明](api.md#接口商品详情getproduct)。

### 脚本输出与业务结果

按 [接口响应结构](api.md#接口商品详情getproduct) 保留业务 `data` 路径；去除可选外层网关包装，补充本地 `success`。有效对象／数组及合同允许的空结果成功；格式错误非零退出。

## 接口：类目树（getCategoryTree）

### 脚本输入与构参

`python scripts/products_api.py getCategoryTree '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `params` | 对象 | 默认 `{}`，本操作必填项、类型及分页默认值见 [接口请求参数](product-operations.md#接口类目树getcategorytree)；不展开为顶层字段。 |

脚本固定填入 `operation=getCategoryTree`，不接受输入额外覆盖。

网关及上游映射为 `POST /lazada/products` → `GET /category/tree/get`。参数约束与业务字段见 [接口说明](product-operations.md#接口类目树getcategorytree)。

### 脚本输出与业务结果

按 [接口响应结构](product-operations.md#接口类目树getcategorytree) 保留业务 `data` 路径；去除可选外层网关包装，补充本地 `success`。有效对象／数组及合同允许的空结果成功；格式错误非零退出。

## 接口：类目属性（getCategoryAttributes）

### 脚本输入与构参

`python scripts/products_api.py getCategoryAttributes '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `params` | 对象 | 默认 `{}`，本操作必填项、类型及分页默认值见 [接口请求参数](product-operations.md#接口类目属性getcategoryattributes)；不展开为顶层字段。 |

脚本固定填入 `operation=getCategoryAttributes`，不接受输入额外覆盖。

网关及上游映射为 `POST /lazada/products` → `GET /category/attributes/get`。参数约束与业务字段见 [接口说明](product-operations.md#接口类目属性getcategoryattributes)。

### 脚本输出与业务结果

按 [接口响应结构](product-operations.md#接口类目属性getcategoryattributes) 保留业务 `data` 路径；去除可选外层网关包装，补充本地 `success`。有效对象／数组及合同允许的空结果成功；格式错误非零退出。

## 接口：品牌列表（listBrands）

### 脚本输入与构参

`python scripts/products_api.py listBrands '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `params` | 对象 | 默认 `{}`，本操作必填项、类型及分页默认值见 [接口请求参数](product-operations.md#接口品牌列表listbrands)；不展开为顶层字段。 |

脚本固定填入 `operation=listBrands`，不接受输入额外覆盖。

网关及上游映射为 `POST /lazada/products` → `GET /category/brands/query`。参数约束与业务字段见 [接口说明](product-operations.md#接口品牌列表listbrands)。

### 脚本输出与业务结果

按 [接口响应结构](product-operations.md#接口品牌列表listbrands) 保留业务 `data` 路径；去除可选外层网关包装，补充本地 `success`。有效对象／数组及合同允许的空结果成功；格式错误非零退出。

## 接口：商品质检（getProductQcStatus）

### 脚本输入与构参

`python scripts/products_api.py getProductQcStatus '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `params` | 对象 | 默认 `{}`，本操作必填项、类型及分页默认值见 [接口请求参数](product-operations.md#接口商品质检getproductqcstatus)；不展开为顶层字段。 |

脚本固定填入 `operation=getProductQcStatus`，不接受输入额外覆盖。

网关及上游映射为 `POST /lazada/products` → `GET /product/qc/status/get`。参数约束与业务字段见 [接口说明](product-operations.md#接口商品质检getproductqcstatus)。

### 脚本输出与业务结果

按 [接口响应结构](product-operations.md#接口商品质检getproductqcstatus) 保留业务 `data` 路径；去除可选外层网关包装，补充本地 `success`。有效对象／数组及合同允许的空结果成功；格式错误非零退出。

## 接口：仓库列表（listWarehouses）

### 脚本输入与构参

`python scripts/products_api.py listWarehouses '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `params` | 对象 | 默认 `{}`，本操作必填项、类型及分页默认值见 [接口请求参数](product-operations.md#接口仓库列表listwarehouses)；不展开为顶层字段。 |

脚本固定填入 `operation=listWarehouses`，不接受输入额外覆盖。

网关及上游映射为 `POST /lazada/products` → `GET /rc/warehouse/get`。参数约束与业务字段见 [接口说明](product-operations.md#接口仓库列表listwarehouses)。

### 脚本输出与业务结果

按 [接口响应结构](product-operations.md#接口仓库列表listwarehouses) 保留业务 `data` 路径；去除可选外层网关包装，补充本地 `success`。有效对象／数组及合同允许的空结果成功；格式错误非零退出。

## 接口：刊登商品（createProduct）

### 脚本输入与构参

`python scripts/products_api.py createProduct '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `params` | 对象 | 默认 `{}`，本操作必填项、类型及分页默认值见 [接口请求参数](product-operations.md#接口刊登商品createproduct)；不展开为顶层字段。 |
| `requestId` | UUID 字符串 | 是，原 UUID 转小写发送。 |

脚本固定填入 `operation=createProduct`，不接受输入额外覆盖。

网关及上游映射为 `POST /lazada/products` → `POST /product/create`。参数约束与业务字段见 [接口说明](product-operations.md#接口刊登商品createproduct)。

### 脚本输出与业务结果

按 [接口响应结构](product-operations.md#接口刊登商品createproduct) 保留业务 `data` 路径；去除可选外层网关包装，补充本地 `success`。保存原 `clientRequestId` 和 `status`，仅 `SUCCEEDED` 返回退出码 0；其余状态保留结果并非零退出。

## 接口：更新商品（updateProduct）

### 脚本输入与构参

`python scripts/products_api.py updateProduct '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `params` | 对象 | 默认 `{}`，本操作必填项、类型及分页默认值见 [接口请求参数](product-operations.md#接口更新商品updateproduct)；不展开为顶层字段。 |
| `requestId` | UUID 字符串 | 是，原 UUID 转小写发送。 |

脚本固定填入 `operation=updateProduct`，不接受输入额外覆盖。

网关及上游映射为 `POST /lazada/products` → `POST /product/update`。参数约束与业务字段见 [接口说明](product-operations.md#接口更新商品updateproduct)。

### 脚本输出与业务结果

按 [接口响应结构](product-operations.md#接口更新商品updateproduct) 保留业务 `data` 路径；去除可选外层网关包装，补充本地 `success`。保存原 `clientRequestId` 和 `status`，仅 `SUCCEEDED` 返回退出码 0；其余状态保留结果并非零退出。

## 接口：更新价格和库存（updatePriceQuantity）

### 脚本输入与构参

`python scripts/products_api.py updatePriceQuantity '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `params` | 对象 | 默认 `{}`，本操作必填项、类型及分页默认值见 [接口请求参数](product-operations.md#接口更新价格和库存updatepricequantity)；不展开为顶层字段。 |
| `requestId` | UUID 字符串 | 是，原 UUID 转小写发送。 |

脚本固定填入 `operation=updatePriceQuantity`，不接受输入额外覆盖。

网关及上游映射为 `POST /lazada/products` → `POST /product/price_quantity/update`。参数约束与业务字段见 [接口说明](product-operations.md#接口更新价格和库存updatepricequantity)。

### 脚本输出与业务结果

按 [接口响应结构](product-operations.md#接口更新价格和库存updatepricequantity) 保留业务 `data` 路径；去除可选外层网关包装，补充本地 `success`。保存原 `clientRequestId` 和 `status`，仅 `SUCCEEDED` 返回退出码 0；其余状态保留结果并非零退出。

## 接口：设定可售库存（updateSellableQuantity）

### 脚本输入与构参

`python scripts/products_api.py updateSellableQuantity '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `params` | 对象 | 默认 `{}`，本操作必填项、类型及分页默认值见 [接口请求参数](product-operations.md#接口设定可售库存updatesellablequantity)；不展开为顶层字段。 |
| `requestId` | UUID 字符串 | 是，原 UUID 转小写发送。 |

脚本固定填入 `operation=updateSellableQuantity`，不接受输入额外覆盖。

网关及上游映射为 `POST /lazada/products` → `POST /product/stock/sellable/update`。参数约束与业务字段见 [接口说明](product-operations.md#接口设定可售库存updatesellablequantity)。

### 脚本输出与业务结果

按 [接口响应结构](product-operations.md#接口设定可售库存updatesellablequantity) 保留业务 `data` 路径；去除可选外层网关包装，补充本地 `success`。保存原 `clientRequestId` 和 `status`，仅 `SUCCEEDED` 返回退出码 0；其余状态保留结果并非零退出。

## 接口：增减可售库存（adjustSellableQuantity）

### 脚本输入与构参

`python scripts/products_api.py adjustSellableQuantity '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `params` | 对象 | 默认 `{}`，本操作必填项、类型及分页默认值见 [接口请求参数](product-operations.md#接口增减可售库存adjustsellablequantity)；不展开为顶层字段。 |
| `requestId` | UUID 字符串 | 是，原 UUID 转小写发送。 |

脚本固定填入 `operation=adjustSellableQuantity`，不接受输入额外覆盖。

网关及上游映射为 `POST /lazada/products` → `POST /product/stock/sellable/adjust`。参数约束与业务字段见 [接口说明](product-operations.md#接口增减可售库存adjustsellablequantity)。

### 脚本输出与业务结果

按 [接口响应结构](product-operations.md#接口增减可售库存adjustsellablequantity) 保留业务 `data` 路径；去除可选外层网关包装，补充本地 `success`。保存原 `clientRequestId` 和 `status`，仅 `SUCCEEDED` 返回退出码 0；其余状态保留结果并非零退出。

## 接口：迁移公开图片 URL（migrateImage）

### 脚本输入与构参

`python scripts/products_api.py migrateImage '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `params` | 对象 | 默认 `{}`，本操作必填项、类型及分页默认值见 [接口请求参数](product-operations.md#接口迁移公开图片-urlmigrateimage)；不展开为顶层字段。 |
| `requestId` | UUID 字符串 | 是，原 UUID 转小写发送。 |

脚本固定填入 `operation=migrateImage`，不接受输入额外覆盖。

网关及上游映射为 `POST /lazada/products` → `POST /image/migrate`。参数约束与业务字段见 [接口说明](product-operations.md#接口迁移公开图片-urlmigrateimage)。

### 脚本输出与业务结果

按 [接口响应结构](product-operations.md#接口迁移公开图片-urlmigrateimage) 保留业务 `data` 路径；去除可选外层网关包装，补充本地 `success`。保存原 `clientRequestId` 和 `status`，仅 `SUCCEEDED` 返回退出码 0；其余状态保留结果并非零退出。

## 接口：下架商品或 SKU（deactivateProduct）

### 脚本输入与构参

`python scripts/products_api.py deactivateProduct '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `params` | 对象 | 默认 `{}`，本操作必填项、类型及分页默认值见 [接口请求参数](product-operations.md#接口下架商品或-skudeactivateproduct)；不展开为顶层字段。 |
| `requestId` | UUID 字符串 | 是，原 UUID 转小写发送。 |

脚本固定填入 `operation=deactivateProduct`，不接受输入额外覆盖。

网关及上游映射为 `POST /lazada/products` → `POST /product/deactivate`。参数约束与业务字段见 [接口说明](product-operations.md#接口下架商品或-skudeactivateproduct)。

### 脚本输出与业务结果

按 [接口响应结构](product-operations.md#接口下架商品或-skudeactivateproduct) 保留业务 `data` 路径；去除可选外层网关包装，补充本地 `success`。保存原 `clientRequestId` 和 `status`，仅 `SUCCEEDED` 返回退出码 0；其余状态保留结果并非零退出。

## 接口：删除指定 SKU（removeProduct）

### 脚本输入与构参

`python scripts/products_api.py removeProduct '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `params` | 对象 | 默认 `{}`，本操作必填项、类型及分页默认值见 [接口请求参数](product-operations.md#接口删除指定-skuremoveproduct)；不展开为顶层字段。 |
| `requestId` | UUID 字符串 | 是，原 UUID 转小写发送。 |

脚本固定填入 `operation=removeProduct`，不接受输入额外覆盖。

网关及上游映射为 `POST /lazada/products` → `POST /product/remove`。参数约束与业务字段见 [接口说明](product-operations.md#接口删除指定-skuremoveproduct)。

### 脚本输出与业务结果

按 [接口响应结构](product-operations.md#接口删除指定-skuremoveproduct) 保留业务 `data` 路径；去除可选外层网关包装，补充本地 `success`。保存原 `clientRequestId` 和 `status`，仅 `SUCCEEDED` 返回退出码 0；其余状态保留结果并非零退出。

## 接口：批量迁移公开图片（migrateImages）

### 脚本输入与构参

`python scripts/products_api.py migrateImages '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `params` | 对象 | 默认 `{}`，本操作必填项、类型及分页默认值见 [接口请求参数](product-operations.md#接口批量迁移公开图片migrateimages)；不展开为顶层字段。 |
| `requestId` | UUID 字符串 | 是，原 UUID 转小写发送。 |

脚本固定填入 `operation=migrateImages`，不接受输入额外覆盖。

网关及上游映射为 `POST /lazada/products` → `POST /images/migrate`。参数约束与业务字段见 [接口说明](product-operations.md#接口批量迁移公开图片migrateimages)。

### 脚本输出与业务结果

按 [接口响应结构](product-operations.md#接口批量迁移公开图片migrateimages) 保留业务 `data` 路径；去除可选外层网关包装，补充本地 `success`。保存原 `clientRequestId` 和 `status`，仅 `SUCCEEDED` 返回退出码 0；其余状态保留结果并非零退出。

## 接口：批量迁移结果（getImageMigrationResult）

### 脚本输入与构参

`python scripts/products_api.py getImageMigrationResult '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `params` | 对象 | 默认 `{}`，本操作必填项、类型及分页默认值见 [接口请求参数](product-operations.md#接口批量迁移结果getimagemigrationresult)；不展开为顶层字段。 |

脚本固定填入 `operation=getImageMigrationResult`，不接受输入额外覆盖。

网关及上游映射为 `POST /lazada/products` → `GET /image/response/get`。参数约束与业务字段见 [接口说明](product-operations.md#接口批量迁移结果getimagemigrationresult)。

### 脚本输出与业务结果

按 [接口响应结构](product-operations.md#接口批量迁移结果getimagemigrationresult) 保留业务 `data` 路径；去除可选外层网关包装，补充本地 `success`。有效对象／数组及合同允许的空结果成功；格式错误非零退出。

## 接口：本地图片上传（uploadImage）

### 脚本输入与构参

`python scripts/products_api.py uploadImage '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `params` | 对象 | 默认 `{}`，本操作必填项、类型及分页默认值见 [接口请求参数](product-operations.md#接口本地图片上传uploadimage)；不展开为顶层字段。 |
| `requestId` | UUID 字符串 | 是，原 UUID 转小写发送。 |

脚本固定填入 `operation=uploadImage`，不接受输入额外覆盖。

本操作必须使用 `--params-file`；解析后的文件须在当前工作目录内，最大 1,406,296 字节。素材编码、原文件大小和上传次序见接口参考。

网关及上游映射为 `POST /lazada/products` → `POST /image/upload`。参数约束与业务字段见 [接口说明](product-operations.md#接口本地图片上传uploadimage)。

### 脚本输出与业务结果

按 [接口响应结构](product-operations.md#接口本地图片上传uploadimage) 保留业务 `data` 路径；去除可选外层网关包装，补充本地 `success`。保存原 `clientRequestId` 和 `status`，仅 `SUCCEEDED` 返回退出码 0；其余状态保留结果并非零退出。

## 接口：创建视频上传任务（initVideoUpload）

### 脚本输入与构参

`python scripts/products_api.py initVideoUpload '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `params` | 对象 | 默认 `{}`，本操作必填项、类型及分页默认值见 [接口请求参数](product-operations.md#接口创建视频上传任务initvideoupload)；不展开为顶层字段。 |
| `requestId` | UUID 字符串 | 是，原 UUID 转小写发送。 |

脚本固定填入 `operation=initVideoUpload`，不接受输入额外覆盖。

网关及上游映射为 `POST /lazada/products` → `POST /media/video/block/create`。参数约束与业务字段见 [接口说明](product-operations.md#接口创建视频上传任务initvideoupload)。

### 脚本输出与业务结果

按 [接口响应结构](product-operations.md#接口创建视频上传任务initvideoupload) 保留业务 `data` 路径；去除可选外层网关包装，补充本地 `success`。保存原 `clientRequestId` 和 `status`，仅 `SUCCEEDED` 返回退出码 0；其余状态保留结果并非零退出。

## 接口：上传视频分块（uploadVideoBlock）

### 脚本输入与构参

`python scripts/products_api.py uploadVideoBlock '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `params` | 对象 | 默认 `{}`，本操作必填项、类型及分页默认值见 [接口请求参数](product-operations.md#接口上传视频分块uploadvideoblock)；不展开为顶层字段。 |
| `requestId` | UUID 字符串 | 是，原 UUID 转小写发送。 |

脚本固定填入 `operation=uploadVideoBlock`，不接受输入额外覆盖。

本操作必须使用 `--params-file`；解析后的文件须在当前工作目录内，最大 4,202,496 字节。素材编码、原文件大小和上传次序见接口参考。

网关及上游映射为 `POST /lazada/products` → `POST /media/video/block/upload`。参数约束与业务字段见 [接口说明](product-operations.md#接口上传视频分块uploadvideoblock)。

### 脚本输出与业务结果

按 [接口响应结构](product-operations.md#接口上传视频分块uploadvideoblock) 保留业务 `data` 路径；去除可选外层网关包装，补充本地 `success`。保存原 `clientRequestId` 和 `status`，仅 `SUCCEEDED` 返回退出码 0；其余状态保留结果并非零退出。

## 接口：完成视频上传（completeVideoUpload）

### 脚本输入与构参

`python scripts/products_api.py completeVideoUpload '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `params` | 对象 | 默认 `{}`，本操作必填项、类型及分页默认值见 [接口请求参数](product-operations.md#接口完成视频上传completevideoupload)；不展开为顶层字段。 |
| `requestId` | UUID 字符串 | 是，原 UUID 转小写发送。 |

脚本固定填入 `operation=completeVideoUpload`，不接受输入额外覆盖。

网关及上游映射为 `POST /lazada/products` → `POST /media/video/block/commit`。参数约束与业务字段见 [接口说明](product-operations.md#接口完成视频上传completevideoupload)。

### 脚本输出与业务结果

按 [接口响应结构](product-operations.md#接口完成视频上传completevideoupload) 保留业务 `data` 路径；去除可选外层网关包装，补充本地 `success`。保存原 `clientRequestId` 和 `status`，仅 `SUCCEEDED` 返回退出码 0；其余状态保留结果并非零退出。

## 接口：视频详情（getVideo）

### 脚本输入与构参

`python scripts/products_api.py getVideo '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `params` | 对象 | 默认 `{}`，本操作必填项、类型及分页默认值见 [接口请求参数](product-operations.md#接口视频详情getvideo)；不展开为顶层字段。 |

脚本固定填入 `operation=getVideo`，不接受输入额外覆盖。

网关及上游映射为 `POST /lazada/products` → `GET /media/video/get`。参数约束与业务字段见 [接口说明](product-operations.md#接口视频详情getvideo)。

### 脚本输出与业务结果

按 [接口响应结构](product-operations.md#接口视频详情getvideo) 保留业务 `data` 路径；去除可选外层网关包装，补充本地 `success`。有效对象／数组及合同允许的空结果成功；格式错误非零退出。

## 接口：视频额度（getVideoQuota）

### 脚本输入与构参

`python scripts/products_api.py getVideoQuota '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `params` | 对象 | 默认 `{}`，本操作必填项、类型及分页默认值见 [接口请求参数](product-operations.md#接口视频额度getvideoquota)；不展开为顶层字段。 |

脚本固定填入 `operation=getVideoQuota`，不接受输入额外覆盖。

网关及上游映射为 `POST /lazada/products` → `GET /media/video/quota/get`。参数约束与业务字段见 [接口说明](product-operations.md#接口视频额度getvideoquota)。

### 脚本输出与业务结果

按 [接口响应结构](product-operations.md#接口视频额度getvideoquota) 保留业务 `data` 路径；去除可选外层网关包装，补充本地 `success`。有效对象／数组及合同允许的空结果成功；格式错误非零退出。

## 接口：删除视频（removeVideo）

### 脚本输入与构参

`python scripts/products_api.py removeVideo '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `params` | 对象 | 默认 `{}`，本操作必填项、类型及分页默认值见 [接口请求参数](product-operations.md#接口删除视频removevideo)；不展开为顶层字段。 |
| `requestId` | UUID 字符串 | 是，原 UUID 转小写发送。 |

脚本固定填入 `operation=removeVideo`，不接受输入额外覆盖。

网关及上游映射为 `POST /lazada/products` → `POST /media/video/remove`。参数约束与业务字段见 [接口说明](product-operations.md#接口删除视频removevideo)。

### 脚本输出与业务结果

按 [接口响应结构](product-operations.md#接口删除视频removevideo) 保留业务 `data` 路径；去除可选外层网关包装，补充本地 `success`。保存原 `clientRequestId` 和 `status`，仅 `SUCCEEDED` 返回退出码 0；其余状态保留结果并非零退出。

## 接口：查询写入状态（operationStatus）

### 脚本输入与构参

`python scripts/products_api.py operationStatus '<JSON 参数>' [--inline] [--no-cache]`。

| 输入 | 类型 | 必填／构参 |
|---|---|---|
| `connectionId` | 字符串 | 是，原样发送。 |
| `requestId` | UUID 字符串 | 是，原写入 UUID 转小写发送；不传 `operation` 和 `params`。 |


网关及上游映射为 `POST /lazada/operationStatus`。参数约束与业务字段见 [接口说明](product-operations.md#接口查询写入状态operationstatus)。

### 脚本输出与业务结果

保存原 `clientRequestId`、上游 `requestId`、`status`、`data` 和 `success`。状态查询完成即可 `success=true`；原写入仍可能 `REJECTED`、`PARTIAL` 或 `UNKNOWN`。
