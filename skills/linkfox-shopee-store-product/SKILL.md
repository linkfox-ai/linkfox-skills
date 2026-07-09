---
name: linkfox-shopee-store-product
description: Shopee（虾皮）店铺商品管理（与 linkfox-shopee-store-auth 同系列），经 /shopee/developerProxy 转发 Shopee Open API Product 模块全部 57 个接口：get_category、get_item_list、add_item、update_item、update_price、update_stock、boost_item、search_item 等。当用户提到 Shopee 商品、虾皮 listing、上架、下架、SKU、库存、价格、类目、属性、get_item_list、add_item、商品评论、boost 置顶 时触发。即使未明确提及"商品"，只要涉及已授权 Shopee 店铺的商品查询、创建或更新，也应触发。
---

# Shopee 店铺 Product

Shopee Open Platform **Product 模块**（57 个 API）。**依赖 `linkfox-shopee-store-auth`**：先取 `accessToken`，再经 **`POST /shopee/developerProxy`** 转发（`path` 须 `api/v2/product/...`）。

## 调用方式

- **API 端点**：`POST /shopee/developerProxy`（不同操作通过请求体区分；完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/<脚本名>.py '<JSON 参数>' [--inline]`（可用脚本见上文脚本一览）
- **成本约束**：本工具会消耗积分；失败/空结果不得自动换关键词、翻页或连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/<skill-name>-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
- 响应体 ≤ 8 KB：落盘后把完整 JSON 打印到 stdout
- 响应体 > 8 KB：落盘后 stdout 只输出摘要（顶层字段、常见计数如 `total`/`costToken`、最大列表字段的长度 + 前 3 条样本）
- 加 `--inline` 强制全量打印到 stdout（同样落盘）

**读数据建议**：先看摘要判断是否足够；需要具体字段时优先用 `jq`或`ConvertFrom-Json` 从保存的 json 文件按需抽取，避免整份 JSON 进入上下文。

## 官方参考

Product 模块索引：[v2.product.get_category](https://open.shopee.com/documents/v2/v2.product.get_category?module=89&type=1)

---

## Prerequisites（必须先读）

1. 运行 `python scripts/check_auth_dependency.py`；exit code **42** → 先安装 **`linkfox-shopee-store-auth`** 并授权店铺。
2. **不要**在本 skill 内实现授权/令牌逻辑。

---

## Core Concepts

- **转发链路**：`storeTokens` → `developerProxy` → 紫鸟 `shopee-proxy` → Shopee API
- **上架流程**：`get_category` → `get_attribute_tree` → `add_item`（复杂 body 建议传 `body` 字段）
- **日常运营**：`get_item_list` / `get_item_base_info` 查商品；`update_price` / `update_stock` 改价改库存；`unlist_item` 上下架
- **SKU**：`init_tier_variation` / `get_model_list` / `add_model` 等
- **选品数据**（非店铺 listing）→ `linkfox-youying-shopee-product-search`（不依赖 auth）

## 可用脚本（Product 模块 57 个 API）

| 分组 | 脚本 |
|------|------|
| 类目/属性/品牌 | `get_category.py`、`get_attribute_tree.py`、`get_brand_list.py`、`category_recommend.py`、`get_recommend_attribute.py`、`search_attribute_value_list.py` |
| 商品 CRUD | `get_item_list.py`、`get_item_base_info.py`、`get_item_extra_info.py`、`add_item.py`、`update_item.py`、`delete_item.py`、`unlist_item.py`、`search_item.py` |
| SKU/价格/库存 | `get_model_list.py`、`init_tier_variation.py`、`update_tier_variation.py`、`add_model.py`、`update_model.py`、`delete_model.py`、`update_price.py`、`update_stock.py` |
| 推广/评论 | `boost_item.py`、`get_boosted_list.py`、`get_item_promotion.py`、`get_comment.py`、`reply_comment.py` |
| 扩展 | Kit/SSP/Direct/Mart/Outlet、尺码表、违规、车辆兼容、内容诊断等 — 见 `references/api.md` 完整列表 |
| 通用入口 | `product_api.py`（JSON 含 `api` 字段） |

共享：`_shopee_product_common.py`、`_product_endpoints.py`、`_product_api_runner.py`。

## Usage Scenarios

### 1. 查类目并上架
1. `get_category.py` 获取类目树
2. `get_attribute_tree.py` 传 `category_id` 获取必填属性
3. `add_item.py` 传完整 `body`（含 category_id、item_name、price、image、attribute_list 等）

### 2. 查商品与改库存
1. `get_item_list.py`：`offset`、`page_size`、`item_status`
2. `get_item_base_info.py`：`item_id_list`
3. `update_stock.py` / `update_price.py`：POST `body`

### 3. 上下架与推广
- `unlist_item.py`：批量上下架
- `boost_item.py`：置顶（最多 5 个）

## 调用原则

- 先看 **`developerProxy.httpStatus`**，再读 `*Response` 字段
- GET：业务参数放 JSON 顶层（runner 拼 queryString）
- POST：复杂接口传 `body`；简单接口可传顶层 body 字段或 `body`
- 每个脚本 docstring 含 **官方文档 URL**（`module=89`）

## Not Applicable

- 店铺授权 → `linkfox-shopee-store-auth`
- 商户信息 → `linkfox-shopee-store-merchant`
- 订单 → `linkfox-shopee-store-orders`
- 物流发货 → `linkfox-shopee-store-logistics`
- 退货退款 → `linkfox-shopee-store-returns`
- 站内广告 → `linkfox-shopee-store-ads`
- 支付结算 → `linkfox-shopee-store-payment`
- 联盟营销 AMS → `linkfox-shopee-store-ams`
- 店铺视频 → `linkfox-shopee-store-video`
- 店铺信息 → `linkfox-shopee-store-shop`
- 跨境全球商品 → `linkfox-shopee-store-global-product`
- 折扣促销 → `linkfox-shopee-store-discount`
- 套装优惠 Bundle Deal → `linkfox-shopee-store-bundle-deal`
- 加购优惠 Add-On Deal → `linkfox-shopee-store-add-on-deal`
- 店铺优惠券 Voucher → `linkfox-shopee-store-voucher`
- 店铺秒杀 Shop Flash Sale → `linkfox-shopee-store-shop-flash-sale`
- 关注有礼 Follow Prize → `linkfox-shopee-store-follow-prize`
- 精选商品 Top Picks → `linkfox-shopee-store-top-picks`
- 店铺分类 Shop Category → `linkfox-shopee-store-shop-category`
- 账户健康 Account Health → `linkfox-shopee-store-account-health`
- 跨站选品数据 → `linkfox-youying-shopee-product-search`
- 图片/视频上传（MediaSpace `api/v2/media_space/...`）→ `linkfox-shopee-store-media-space`
- 图片/视频上传（Media `api/v2/media/...`）→ `linkfox-shopee-store-media`

**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `references/api.md`. Do not interrupt the user's flow.


---
*For more high-quality, professional cross-border e-commerce skills, visit [LinkFox Skills](https://skill.linkfox.com/).*
