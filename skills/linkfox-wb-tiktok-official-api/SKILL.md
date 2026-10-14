---
name: linkfox-wb-tiktok-official-api
display_name: LinkFox TikTok官方运营API
display_name_en: LinkFox TikTok Official Operations API
description: TikTok Shop 官方运营 API 能力，覆盖授权、店铺、商品、订单、履约、仓库、售后、视频发布与经营分析。
description_zh: 面向 TikTok Shop 卖家运营的官方 API 能力，支持 ERP 店铺授权和选店、商品刊登与维护、订单查询、履约拆单判断、仓库查询、售后拒因查询与店铺视频表现分析；同时归档达人资料、橱窗商品和可购物视频接口契约，但达人链路因后端授权映射未确认而暂不可调用。当用户需要 TikTok Shop 官方运营接口、授权管理、Listing、订单、仓库、售后、视频带货或经营数据时触发。完整参数、响应、错误码及阻塞见 references/；可执行业务调用只使用 Linkfox LinkFox MCP。
description_en: Official TikTok Shop seller operations API capability covering ERP authorization and store selection, product listing and maintenance, order lookup, fulfillment split checks, warehouse lookup, return or cancellation reject reasons, and shop video analytics. Creator profile, showcase, and shoppable-video contracts are archived but cannot be called until backend creator-authorization mapping is confirmed. Use it for TikTok Shop official operations, listings, orders, warehouses, after-sales, creator commerce contracts, or performance data. Full parameters, responses, errors, and blockers are in references/; executable business calls use only Linkfox LinkFox MCP.
icon: icons/logo.png
version: 2.1.0
author: Linkfox
---

> [!IMPORTANT]
本 Skill 必须依赖 MCP “LinkFox”。如未安装该MCP，请明确通知用户：
> 请先安装 LinkFox 连接器：
> - 在 WorkBuddy 左侧找到 “专家·技能·连接器” → “连接器”；
> - 搜索关键词 “LinkFox”，并安装连接器 “LinkFox”（注意：是 linkfox，不是 linkfox-product-selection），按指引完成登录授权；
> - 返回 WorkBuddy 重试。


# LinkFox TikTok官方运营API（LinkFox TikTok Official Operations API）

为 TikTok Shop 卖家和达人运营提供统一的官方接口执行能力：完成店铺授权与选店，管理商品和库存，查询订单与仓库，判断订单拆单属性，读取售后拒因并分析店铺视频表现；达人商品与可购物视频工作流保留接口契约，但当前存在授权映射阻塞。当前归档 8 个业务域、45 个 API operation；35 个 ERP operation 可通过 `proxy_call` 执行，`storeTokens` 仅保留响应契约且不得用于读取凭证，1 个 ERP multipart 文件上传 operation 仅保留官方参数参考；8 个达人 operation 在网关实现 WorkBuddy 授权上下文到上游达人授权的自动映射前均不可执行，其中视频文件上传另受 multipart 限制。各业务域标识、完整 operation、端点、本地辅助脚本和参数参考见下方路由表。

## MCP 调用

| 项 | 固定值 |
|---|---|
| MCP server | `LinkFox` |
| 唯一工具 | `proxy_call` |
| `toolName` allowlist | `tiktokShop/developerProxy`、`tiktokShop/authorizeUrl`、`tiktokShop/authorizedStores`、`tiktokShop/storeTokens`、`tiktokShop/refreshToken` |
| 调用结构 | `{"toolName":"<精确 endpoint>","arguments":{...}}`；原请求体直接作为 `arguments` |

- `toolName` 精确匹配且区分大小写；共享 `developerProxy` 的 `appType`、`openId`、`path`、`method`、`queryString`、`body` 等继续放在 `arguments`。
- WorkBuddy 自动注入 MCP Authorization；禁止在 MCP 配置或 `arguments` 中增加 LinkFox `headers`、API Key、`token`、JWT、手机号或其他凭证。
- 禁止 curl、`urllib`、`requests`、`httpx` 或其他 HTTP 方式直连工具网关；MCP 缺失时停止，不得静默 fallback。
- 收费调用失败、空结果或不理想时不得自动重试；同一任务内相同 `toolName + arguments` 不得重复调用。网关对 TikTok 店铺令牌的内部续签不等于 Agent 重试。
- 先检查 MCP/schema/`isError`，再读取 text/structured content；text 为 JSON 字符串时只解析一次。随后检查下游 `errcode`/`errorCode`/`code`/`errmsg`/`message`，最后读取业务字段。
- 新 MCP 链路不提供旧脚本的 24 小时缓存、响应落盘或 stdout 摘要；仅记录非敏感调用摘要和状态用于追溯。
## 能力边界

### 能力范围

- **授权与店铺上下文**（`linkfox-tiktok-shop-auth`）：生成 TikTok Shop ERP OAuth 授权链接、列出已授权 ERP 店铺，并在用户明确要求或排查授权异常时手动刷新后台授权；`storeTokens` 仅保留响应契约，不用于读取或展示凭证。`region` 支持 `global` 和 `us`，`appType` 固定为 `erp`。
- **达人资料与带货内容**（`linkfox-tiktok-creator`）：归档达人档案、绑定店铺商品、橱窗/直播袋商品以及可购物视频预检、发布和状态查询契约；当前不得调用，授权映射阻塞见 `references/linkfox-tiktok-creator--api.md`。
- **ERP 商品运营**（`linkfox-tiktok-shop-product`）：通过 `product/` 与 `authorization/` 路径完成刊登前置检查、类目树/类目规则/属性/品牌、类目推荐、商品搜索与详情、创建/全量编辑/部分编辑、刊登校验、上下架、改价、改库存、删除/恢复；本地商品主图可用 `upload_product_image.py` 转为 TikTok URI。
- **ERP 订单查询**（`linkfox-tiktok-shop-order`）：按状态、时间和分页查询订单，并以订单 ID 获取 202507（推荐）或 202309 详情；订单查询结果可继续交给 `linkfox-tiktok-shop-fulfillment` 判断拆单属性。
- **ERP 履约准备**（`linkfox-tiktok-shop-fulfillment`）：查询订单是否可拆单、是否必须拆单及原因；使用 `fulfillment/202309/orders/split_attributes`，订单 ID 通常来自订单查询。
- **ERP 物流仓库**（`linkfox-tiktok-shop-logistics`）：查询店铺销售仓/退货仓等仓库的 ID、类型、状态和地址摘要，为商品库存或多仓运营取得 `warehouse_id`。
- **ERP 售后信息**（`linkfox-tiktok-shop-return-refund`）：根据退货或取消单的 `return_or_cancel_id` 查询可用拒退/拒取消原因和本地化文案。
- **ERP 经营分析**（`linkfox-tiktok-shop-analytics`）：按 `start_date`、`end_date` 查询店铺视频的浏览、点击、订单、GMV 等表现指标，支持分页、币种、排序和粒度参数。
- **统一网关与脚本执行**：ERP 业务经 `POST tiktokShop/developerProxy` 转发，使用非凭证店铺标识 `openId` 选择后台授权上下文。达人来源契约要求单独的上游凭证请求字段，但当前没有证据表明 MCP 会自动映射该字段；不得读取、保存或放入 `arguments`，因此达人 operation 暂停调用。新 MCP 链路不提供旧脚本的缓存、响应落盘或 stdout 摘要。

### 边界与限制

- **凭证不得进入参数**：ERP 业务使用非凭证店铺标识 `openId` 选择后台授权上下文，`appType` 固定 `erp`。达人来源没有定义可替代凭证的账号标识，不能把 ERP `openId` 臆造成达人参数；在后端支持 WorkBuddy 授权上下文自动映射前停止达人调用。
- **接口范围固定**：仅执行路由表中的授权、creator、product、order、fulfillment、logistics、return/refund 和 analytics operation；不能借助通用 proxy 任意调用未收录的 TikTok 路径。
- **multipart 上传限制**：达人 `Upload Shoppable Video File`（`affiliate_creator/202505/videos/video_files`）和商品 `Upload Product File`（`product/202309/files/upload`）需要二进制 `multipart/form-data`，当前仅有官方参考，没有可执行上传脚本；达人接口还受授权映射阻塞。商品主图上传另有 `upload_product_image.py` 的 Base64 网关适配链路。
- **写操作需谨慎**：商品创建、编辑、上下架、改价、改库存、删除/恢复和达人视频发布会改变店铺状态；先确认 `openId`、`shop_cipher`、商品/视频 ID 和请求体，再执行，不能因失败自动换参数连续试探。
- **店铺标识与路径**：多店时必须显式提供正确的 `shop_cipher`；单店也应显式传入，可先调用 Get Authorized Shops 获取。不要自行传 `app_key`、`sign`、`timestamp`，由代理注入；网关 `errcode=1005` 表示对应路径尚未放行。
- **数据与结论边界**：返回值是 TikTok Shop 官方接口或 LinkFox 网关透传数据，不保证字段在所有站点均可用；本能力不替代平台规则、财务核算、法律意见、客服裁决或人工运营决策。

## 工具选择指南

按用户目标先确定身份上下文（ERP 店铺或达人），再按读/写、单对象/列表、同步/异步和参数位置选择入口。相近需求按下表选择，必要时把候选入口和额外调用成本告知用户后再继续。

| 需求 / 用户说 | 默认推荐 | 何时换用其他 |
|---|---|---|
| 授权、绑定或查看 TikTok Shop 小店 | `linkfox-tiktok-shop-auth` 的 `proxy_call` / `proxy_call` | 达人或视频号授权不走 ERP 授权；已有店铺只需先列店铺取得 `openId` |
| ERP 授权异常或明确要求刷新 | 按 onboarding 排查；仅明确要求时调用 `tiktokShop/refreshToken` | 日常 ERP 业务直接调用 proxy，由网关遇 401 自动刷新一次；不得调用 `storeTokens` 读取或展示凭证 |
| 查达人资料、达人绑定商品、达人橱窗商品 | 当前不可执行；查阅 `linkfox-tiktok-creator` 契约 | 等待网关实现 WorkBuddy 授权上下文到上游达人授权的自动映射；不得读取或传递凭证，也不得用 ERP `openId` 替代 |
| 上传、预检、发布可购物视频或查视频状态 | 当前不可执行；查阅达人 API reference | 授权映射阻塞；视频文件上传还需要当前不具备的 multipart 链路 |
| 商品刊登前条件、类目、属性、品牌 | `linkfox-tiktok-shop-product` 的 `proxy_call`、类目/属性/品牌脚本 | 已有商品维护用详情、编辑或部分编辑；类目不确定时先 `proxy_call` |
| 创建或更新商品 | `proxy_call`、`proxy_call` 或 `proxy_call` | 复杂创建/编辑请求使用 `requestBody`；只改价或库存时分别用专用脚本，避免全量编辑 |
| 搜索/查看、上下架、改价、改库存、删除/恢复商品 | `proxy_call`、`proxy_call` 及对应维护脚本 | 先用 `proxy_call` 确认目标商品和 SKU；多仓库存先查询 `proxy_call` |
| 订单列表或订单详情 | `proxy_call` → `proxy_call`（202507） | 兼容旧接口时改用 `proxy_call`；履约或售后问题不要用订单详情接口代替专用 API |
| 判断订单能否/必须拆单 | `proxy_call` | 需要订单 ID 时先使用订单查询；发货/包裹实际操作不在当前 operation 范围 |
| 查询销售仓、退货仓和 `warehouse_id` | `proxy_call` | 只需店铺 `shop_cipher` 时先用对应域的 `proxy_call` |
| 查询退货/取消可用拒因 | `proxy_call` | 需要同意/拒绝退货等写操作时当前能力不适用 |
| 分析店铺视频浏览、订单或 GMV | `proxy_call` | 达人视频发布/预检属于 creator；时间范围缺失时先补齐 `start_date` / `end_date` |

### 选择思路

- ERP 业务统一先确认授权店铺和 `openId`，再按功能使用 `product`、`order`、`fulfillment`、`logistics`、`return-refund` 或 `analytics` 的专用入口。
- 达人数据和可购物视频的归档请求形态保留 `appType=creator`，但不包含任何凭证或臆造账号标识；授权映射阻塞解除前不得调用，也不要切换到 ERP 商品或分析接口规避阻塞。
- 对同一结果既可用专用脚本又可用 `proxy_call`/`proxy_call` 时，默认使用具名脚本；只有需要完整 path/method 或复用已收录 operation 时才使用通用入口。
- 需要跨域编排时按数据依赖顺序执行：授权/选店 → `shop_cipher` → 订单/商品/仓库查询 → 履约或维护；每一步先检查当前 MCP 响应，再决定是否继续。

## 业务需求路由速查

路由表中的 `reference` 文件包含对应 operation 的完整参数、响应、错误码和官方示例。`authorization/202309/shops` 在每个 ERP 业务域中都保留了独立适配脚本，用于取得该域调用所需的 `shop_cipher`。

| 子能力 | 业务能力 | reference | 端点 | 脚本 |
|---|---|---|---|---|
| `linkfox-tiktok-creator` | 获取达人主页/档案 `Get Creator Profile` | `references/linkfox-tiktok-creator--api.md` | `POST tiktokShop/developerProxy` → `GET affiliate_creator/202508/profiles` | —（授权映射阻塞） |
| `linkfox-tiktok-creator` | 搜索达人绑定店铺商品 `Get Shop Products` | `references/linkfox-tiktok-creator--api.md` | `POST tiktokShop/developerProxy` → `GET affiliate_creator/202509/shop_products` | —（授权映射阻塞） |
| `linkfox-tiktok-creator` | 获取达人橱窗/直播袋商品 `Get Showcase Products` | `references/linkfox-tiktok-creator--api.md` | `POST tiktokShop/developerProxy` → `GET affiliate_creator/202405/showcases/products` | —（授权映射阻塞） |
| `linkfox-tiktok-creator` | 上传可购物视频文件 `Upload Shoppable Video File` | `references/linkfox-tiktok-creator--api.md` | `POST tiktokShop/developerProxy` → `POST affiliate_creator/202505/videos/video_files`（multipart） | —（当前无 multipart 脚本） |
| `linkfox-tiktok-creator` | 发布可购物视频 `Post Shoppable Video` | `references/linkfox-tiktok-creator--api.md` | `POST tiktokShop/developerProxy` → `POST affiliate_creator/202603/videos` | —（授权映射阻塞） |
| `linkfox-tiktok-creator` | 查询可购物视频发布状态 `Get Shoppable Video Status` | `references/linkfox-tiktok-creator--api.md` | `POST tiktokShop/developerProxy` → `GET affiliate_creator/202509/videos/{video_id}/status` | —（授权映射阻塞） |
| `linkfox-tiktok-creator` | 创建可购物视频预检任务 `Pre-check Shoppable Video` | `references/linkfox-tiktok-creator--api.md` | `POST tiktokShop/developerProxy` → `POST affiliate_creator/202511/videos/precheck_task` | —（授权映射阻塞） |
| `linkfox-tiktok-creator` | 查询视频预检结果 `Get Shoppable Video Pre-check Result` | `references/linkfox-tiktok-creator--api.md` | `POST tiktokShop/developerProxy` → `GET affiliate_creator/202511/videos/precheck_tasks/{task_id}` | —（授权映射阻塞） |
| `linkfox-tiktok-shop-auth` | 生成 ERP 授权 URL `Get Authorization URL` | `references/linkfox-tiktok-shop-auth--api.md` | `POST tiktokShop/authorizeUrl` | `proxy_call` |
| `linkfox-tiktok-shop-auth` | 列出已授权 ERP 店铺 `List Authorized Stores` | `references/linkfox-tiktok-shop-auth--api.md` | `POST tiktokShop/authorizedStores` | `proxy_call` |
| `linkfox-tiktok-shop-auth` | ERP 令牌响应契约 `Query Store Tokens` | `references/linkfox-tiktok-shop-auth--api.md` | `POST tiktokShop/storeTokens` | —（仅契约记录，不读取凭证） |
| `linkfox-tiktok-shop-auth` | 手动刷新 ERP 令牌 `Refresh Token` | `references/linkfox-tiktok-shop-auth--api.md` | `POST tiktokShop/refreshToken` | `proxy_call` |
| `linkfox-tiktok-shop-order` | 获取已授权店铺与 cipher `Get Authorized Shops` | `references/linkfox-tiktok-shop-order--apis--get_authorized_shops.md` | `POST tiktokShop/developerProxy` → `GET authorization/202309/shops` | `proxy_call` |
| `linkfox-tiktok-shop-order` | 搜索订单 `Get Order List` | `references/linkfox-tiktok-shop-order--apis--get_order_list.md` | `POST tiktokShop/developerProxy` → `POST order/202309/orders/search` | `proxy_call` |
| `linkfox-tiktok-shop-order` | 获取订单详情（202507）`Get Order Detail` | `references/linkfox-tiktok-shop-order--apis--get_order_detail.md` | `POST tiktokShop/developerProxy` → `GET order/202507/orders` | `proxy_call` |
| `linkfox-tiktok-shop-order` | 获取订单详情（202309）`Get Order Detail` | `references/linkfox-tiktok-shop-order--apis--get_order_detail_202309.md` | `POST tiktokShop/developerProxy` → `GET order/202309/orders` | `proxy_call` |
| `linkfox-tiktok-shop-product` | 上传商品主图 `Upload Product Image` | `references/linkfox-tiktok-shop-product--apis--upload_product_image.md` | `POST tiktokShop/developerProxy` → `POST product/202309/images/upload` | `proxy_call` |
| `linkfox-tiktok-shop-product` | 获取已授权店铺与 cipher `Get Authorized Shops` | `references/linkfox-tiktok-shop-product--apis--get_authorized_shops.md` | `POST tiktokShop/developerProxy` → `GET authorization/202309/shops` | `proxy_call` |
| `linkfox-tiktok-shop-product` | 刊登前置检查 `Check Listing Prerequisites` | `references/linkfox-tiktok-shop-product--apis--check_listing_prerequisites.md` | `POST tiktokShop/developerProxy` → `GET product/202312/prerequisites` | `proxy_call` |
| `linkfox-tiktok-shop-product` | 获取类目树 `Get Categories` | `references/linkfox-tiktok-shop-product--apis--get_categories.md` | `POST tiktokShop/developerProxy` → `GET product/202309/categories` | `proxy_call` |
| `linkfox-tiktok-shop-product` | 获取类目规则 `Get Category Rules` | `references/linkfox-tiktok-shop-product--apis--get_category_rules.md` | `POST tiktokShop/developerProxy` → `GET product/202309/categories/{category_id}/rules` | `proxy_call` |
| `linkfox-tiktok-shop-product` | 获取类目属性 `Get Attributes` | `references/linkfox-tiktok-shop-product--apis--get_attributes.md` | `POST tiktokShop/developerProxy` → `GET product/202309/categories/{category_id}/attributes` | `proxy_call` |
| `linkfox-tiktok-shop-product` | 推荐类目 `Recommend Category` | `references/linkfox-tiktok-shop-product--apis--recommend_category.md` | `POST tiktokShop/developerProxy` → `POST product/202309/categories/recommend` | `proxy_call` |
| `linkfox-tiktok-shop-product` | 获取品牌列表 `Get Brands` | `references/linkfox-tiktok-shop-product--apis--get_brands.md` | `POST tiktokShop/developerProxy` → `GET product/202309/brands` | `proxy_call` |
| `linkfox-tiktok-shop-product` | 搜索商品 `Search Products` | `references/linkfox-tiktok-shop-product--apis--search_products.md` | `POST tiktokShop/developerProxy` → `POST product/202502/products/search` | `proxy_call` |
| `linkfox-tiktok-shop-product` | 获取商品详情 `Get Product` | `references/linkfox-tiktok-shop-product--apis--get_product.md` | `POST tiktokShop/developerProxy` → `GET product/202309/products/{product_id}` | `proxy_call` |
| `linkfox-tiktok-shop-product` | 创建商品 `Create Product` | `references/linkfox-tiktok-shop-product--apis--create_product.md` | `POST tiktokShop/developerProxy` → `POST product/202309/products` | `proxy_call` |
| `linkfox-tiktok-shop-product` | 全量编辑商品 `Edit Product` | `references/linkfox-tiktok-shop-product--apis--edit_product.md` | `POST tiktokShop/developerProxy` → `PUT product/202309/products/{product_id}` | `proxy_call` |
| `linkfox-tiktok-shop-product` | 部分编辑商品 `Partial Edit Product` | `references/linkfox-tiktok-shop-product--apis--partial_edit_product.md` | `POST tiktokShop/developerProxy` → `POST product/202309/products/{product_id}/partial_edit` | `proxy_call` |
| `linkfox-tiktok-shop-product` | 商品刊登校验 `Check Product Listing` | `references/linkfox-tiktok-shop-product--apis--check_product_listing.md` | `POST tiktokShop/developerProxy` → `POST product/202309/products/listing_check` | `proxy_call` |
| `linkfox-tiktok-shop-product` | 商品上架 `Activate Product` | `references/linkfox-tiktok-shop-product--apis--activate_product.md` | `POST tiktokShop/developerProxy` → `POST product/202309/products/activate` | `proxy_call` |
| `linkfox-tiktok-shop-product` | 商品下架 `Deactivate Products` | `references/linkfox-tiktok-shop-product--apis--deactivate_products.md` | `POST tiktokShop/developerProxy` → `POST product/202309/products/deactivate` | `proxy_call` |
| `linkfox-tiktok-shop-product` | 更新 SKU 价格 `Update Price` | `references/linkfox-tiktok-shop-product--apis--update_price.md` | `POST tiktokShop/developerProxy` → `POST product/202309/products/{product_id}/prices/update` | `proxy_call` |
| `linkfox-tiktok-shop-product` | 更新 SKU 库存 `Update Inventory` | `references/linkfox-tiktok-shop-product--apis--update_inventory.md` | `POST tiktokShop/developerProxy` → `POST product/202309/products/{product_id}/inventory/update` | `proxy_call` |
| `linkfox-tiktok-shop-product` | 删除商品 `Delete Products` | `references/linkfox-tiktok-shop-product--apis--delete_products.md` | `POST tiktokShop/developerProxy` → `DELETE product/202309/products` | `proxy_call` |
| `linkfox-tiktok-shop-product` | 恢复商品 `Recover Products` | `references/linkfox-tiktok-shop-product--apis--recover_products.md` | `POST tiktokShop/developerProxy` → `POST product/202309/products/recover` | `proxy_call` |
| `linkfox-tiktok-shop-product` | 上传商品文件 `Upload Product File` | `references/linkfox-tiktok-shop-product--apis--upload_product_file.md` | `POST tiktokShop/developerProxy` → `POST product/202309/files/upload`（multipart） | —（当前无 multipart 脚本） |
| `linkfox-tiktok-shop-fulfillment` | 获取已授权店铺与 cipher `Get Authorized Shops` | `references/linkfox-tiktok-shop-fulfillment--apis--get_authorized_shops.md` | `POST tiktokShop/developerProxy` → `GET authorization/202309/shops` | `proxy_call` |
| `linkfox-tiktok-shop-fulfillment` | 查询订单拆单属性 `Get Order Split Attributes` | `references/linkfox-tiktok-shop-fulfillment--apis--get_order_split_attributes.md` | `POST tiktokShop/developerProxy` → `GET fulfillment/202309/orders/split_attributes` | `proxy_call` |
| `linkfox-tiktok-shop-logistics` | 获取已授权店铺与 cipher `Get Authorized Shops` | `references/linkfox-tiktok-shop-logistics--apis--get_authorized_shops.md` | `POST tiktokShop/developerProxy` → `GET authorization/202309/shops` | `proxy_call` |
| `linkfox-tiktok-shop-logistics` | 获取仓库列表 `Get Warehouse List` | `references/linkfox-tiktok-shop-logistics--apis--get_warehouse_list.md` | `POST tiktokShop/developerProxy` → `GET logistics/202309/warehouses` | `proxy_call` |
| `linkfox-tiktok-shop-return-refund` | 获取已授权店铺与 cipher `Get Authorized Shops` | `references/linkfox-tiktok-shop-return-refund--apis--get_authorized_shops.md` | `POST tiktokShop/developerProxy` → `GET authorization/202309/shops` | `proxy_call` |
| `linkfox-tiktok-shop-return-refund` | 获取拒退/拒取消原因 `Get Reject Reasons` | `references/linkfox-tiktok-shop-return-refund--apis--get_reject_reasons.md` | `POST tiktokShop/developerProxy` → `GET return_refund/202309/reject_reasons` | `proxy_call` |
| `linkfox-tiktok-shop-analytics` | 获取已授权店铺与 cipher `Get Authorized Shops` | `references/linkfox-tiktok-shop-analytics--apis--get_authorized_shops.md` | `POST tiktokShop/developerProxy` → `GET authorization/202309/shops` | `proxy_call` |
| `linkfox-tiktok-shop-analytics` | 获取店铺视频表现 `Get Video Performances` | `references/linkfox-tiktok-shop-analytics--apis--get_video_performances.md` | `POST tiktokShop/developerProxy` → `GET analytics/202403/shop_videos/performance` | `proxy_call` |

## 调用方式

1. 先按身份选择 ERP 店铺或 Creator，并从路由表打开对应 reference。
2. ERP 授权能力使用其专属 `toolName`；ERP 业务使用 `tiktokShop/developerProxy`，保留 reference 定义的 `path`、`method`、`queryString` 和字符串化 `body`。达人 operation 仅保留契约，授权映射阻塞解除前不得执行。
3. `shop_cipher`、路径参数、分页和请求体均严格按 reference 构造。写操作先展示目标与副作用并取得确认；异步查询每次均视为新的收费调用。
4. 本地商品图片可先运行 `scripts/upload_product_image.py` 生成 Base64 `arguments`，再由 Agent 调 `proxy_call`；脚本不联网、不读取凭证。
## 展示规则

1. **客观呈现**：按接口返回展示字段、状态、时间和计数，区分网关 `httpStatus` 与 TikTok `body` 内 `code` / `message`，不把接口数据扩写成平台保证或法律/财务结论。
2. **来源标注**：说明数据来自 TikTok Shop ERP 授权、商品、订单、履约、物流、售后、分析或达人接口，并在必要时标注接口版本（如订单 202507/202309、分析 202403）。
3. **敏感信息**：授权响应中存在的凭证字段仅用于契约识别，不得读取后展示、保存或转发；`shop_cipher` 只在业务需要时展示。授权链接约 1 小时有效，过期时间字段是 Unix 时间戳。
4. **授权结果**：店铺列表只展示 `appType=erp` 店铺的 `openId`、名称、区域等；授权链接和授权维护结果明确标记其 ERP 限定，凭证字段不得读取后展示、保存或转发。
5. **达人工作流**：当前仅保留响应契约；授权映射阻塞解除后，预检展示 `task_id`、`result` 和 `issues[]`，只有 `SUCCESS` 才建议发布。发布状态区分 `SUCCESS`、`FAIL`、`PROCESSING`，不把异步任务创建当作发布完成。
6. **商品结果**：刊登检查逐条展示 `check_item` 和 `fail_reasons`；搜索/详情展示商品 ID、标题、状态、SKU、价格、库存和更新时间；写操作返回失败时先确认商品 ID、SKU、仓库和店铺。
7. **订单与履约**：订单列表优先展示订单号、状态、金额、创建/更新时间和分页游标；详情再展开地址、包裹和行项目。拆单结果优先展示 `can_split`、`must_split` 与原因，不能把拆单判断描述为已发货。
8. **仓库、售后、分析**：仓库展示 `id/name/type/effect_status/is_default` 和地址摘要；拒因展示 `reason_code` 与本地化文本；视频分析展示 `video_id`、指标、时间窗、币种、排序和分页信息。
9. **不可用字段**：空值、缺失值或接口未返回的字段标记为 N/A 或省略，不猜测默认值；分页游标只在响应明确返回时继续使用。
10. **错误处理**：根据 HTTP 状态、`errcode`、TikTok `code`/`message` 给出可操作修正。`1005` 提示路径未白名单；ERP 401/过期由网关自动刷新一次。达人 operation 当前在调用前即因授权映射未确认而停止，不通过传入凭证尝试修复。
11. **不可执行限制**：商品文件上传明确说明“需要 multipart、当前无脚本”；8 个达人 operation 明确说明授权映射阻塞，其中视频文件上传还受 multipart 限制。不伪造成功结果，也不把普通 JSON 示例当成可上传文件。

## 解决认证和积分问题

- MCP 或 `proxy_call` 缺失：停止调用，配置 `LinkFox`（`https://mcp-tool-gateway.linkfox.com/mcp/any-tool`）并重启或重载客户端。
- MCP 连接 401：提示重新登录 WorkBuddy、重载连接或联系 WorkBuddy 管理员；不得要求用户手填 Authorization。
- 代理成功但下游 JSON 为 401：按 WorkBuddy 自动授权或 TikTok 店铺/达人业务授权失败处理，不得加入 LinkFox Key/token。
- 下游 402 或积分不足：引导访问 <https://agent.linkfox.com/>；不得自动选套餐、下单、支付或轮询。403 和其他错误按业务 reference 处理。
## 积分消耗说明

> 用户会因积分消耗而支付费用。请充分评估：当需要高频调用本技能，或用户对积分消耗量预期不足时，务必提醒用户，由用户决定是否继续。
