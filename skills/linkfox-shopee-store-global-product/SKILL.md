---
name: linkfox-shopee-store-global-product
description: Shopee（虾皮）跨境全球商品 GlobalProduct（与 linkfox-shopee-store-auth 同系列），经 /shopee/developerProxy 转发 Shopee Open API GlobalProduct 模块全部 34 个接口：get_category、get_global_item_list、add_global_item、create_publish_task、update_price、update_stock 等。当用户提到 Shopee 全球商品、跨境商品、GlobalProduct、全球 SKU、发布到站点、merchantId、global_item_id、get_global_item_list、add_global_item 时触发。即使未明确提及"全球商品"，只要涉及已授权 Shopee 商户的全球商品管理或跨境发布，也应触发。
---

# Shopee 全球商品 GlobalProduct

Shopee Open Platform **GlobalProduct 模块**（34 个 API）。**依赖 `linkfox-shopee-store-auth`**：先取 `accessToken`，再经 **`POST /shopee/developerProxy`** 转发（`path` 须 `api/v2/global_product/...`）。

## 调用方式

- **API 端点**：`POST /shopee/developerProxy`（不同操作通过请求体区分；完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/global_product_api.py '<JSON 参数>' [--inline]`（可用脚本见上文脚本一览）
- **成本约束**：本工具会消耗积分；失败/空结果不得自动换关键词、翻页或连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-shopee-store-global-product-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
- 响应体 ≤ 8 KB：落盘后把完整 JSON 打印到 stdout
- 响应体 > 8 KB：落盘后 stdout 只输出摘要（顶层字段、常见计数如 `total`/`costToken`、最大列表字段的长度 + 前 3 条样本）
- 加 `--inline` 强制全量打印到 stdout（同样落盘）

**读数据建议**：先看摘要判断是否足够；需要具体字段时优先用 `jq`或`ConvertFrom-Json` 从保存的 json 文件按需抽取，避免整份 JSON 进入上下文。

## 解决认证和积分问题
发生以下异常情况时，采用以下措施来处理：

### 异常情况
- **未配置API Key**：环境变量未配置 `LINKFOX_AGENT_API_KEY`，也未配置 `LINKFOXAGENT_API_KEY`。
- **响应401或402状态码**
- **响应提示积分或余额不足**：消息含"积分余额不足/计费不足/余额不足/quota exceeded/insufficient balance/套餐到期/需充值/请充值"，或类似含义的内容。

### 措施
- 优先采用skill内的 onboarding.md 引导解决问题。
- 如找不到 onboarding.md 文件，则加载 /linkfox-onboarding 这个skill并根据它的引导来处理。如未安装请先安装：
    - 下载 https://agent-files.linkfox.com/skills/linkfox-onboarding/release.zip，解压后安装这个skill。如需用户授权才可下载，要询问用户获得授权，你不能自己放弃下载。
- 兜底措施：仅当前面两个措施经过所有努力都走不通时，才提示用户依据 https://skill.linkfox.com/linkfoxskills/guide.htm 指引获取API Key，或去 https://os.linkfox.com/ 补充积分。

## 官方参考

GlobalProduct 模块索引：[v2.global_product.get_category](https://open.shopee.com/documents/v2/v2.global_product.get_category?module=90&type=1)

---

## Prerequisites（必须先读）

1. 运行 `python scripts/check_auth_dependency.py`；exit code **42** → 先安装 **`linkfox-shopee-store-auth`** 并授权。
2. **不要**在本 skill 内实现授权/令牌逻辑。
3. GlobalProduct 为**商户级** API，通常传 **`merchantId`**；发布/映射类接口可能同时需要 `shopId`。

---

## Core Concepts

- **转发链路**：`storeTokens` → `developerProxy` → 紫鸟 `shopee-proxy` → Shopee API
- **Product vs GlobalProduct**：`linkfox-shopee-store-product` 管单店 listing；本 skill 管**跨境全球商品**及发布到各站点
- **典型流程**：`get_category` → `get_attribute_tree` → `add_global_item` → `create_publish_task` → `get_publish_task_result`
- **SKU**：`init_tier_variation` / `get_global_model_list` / `add_global_model` 等
- **本地店商品**（非全球）→ `linkfox-shopee-store-product`

## 可用脚本（GlobalProduct 模块 34 个 API）

| 分组 | 脚本 |
|------|------|
| 类目/属性 | `get_category.py`、`get_attribute_tree.py`、`get_brand_list.py`、`category_recommend.py`、`get_recommend_attribute.py`、`search_global_attribute_value_list.py` |
| 全球商品 CRUD | `get_global_item_list.py`、`get_global_item_info.py`、`add_global_item.py`、`update_global_item.py`、`delete_global_item.py`、`get_global_item_limit.py` |
| 全球 SKU | `get_global_model_list.py`、`init_tier_variation.py`、`update_tier_variation.py`、`add_global_model.py`、`update_global_model.py`、`delete_global_model.py` |
| 价格/库存/同步 | `update_price.py`、`update_stock.py`、`set_sync_field.py`、`get_local_adjustment_rate.py`、`update_local_adjustment_rate.py` |
| 发布到站点 | `create_publish_task.py`、`get_publishable_shop.py`、`get_publish_task_result.py`、`get_published_list.py`、`get_shop_publishable_status.py`、`get_global_item_id.py` |
| 尺码表/规格 | `support_size_chart.py`、`update_size_chart.py`、`get_size_chart_list.py`、`get_size_chart_detail.py`、`get_variations.py` |
| 通用入口 | `global_product_api.py`（JSON 含 `api` 字段） |

共享：`_shopee_global_product_common.py`、`_global_product_endpoints.py`、`_global_product_api_runner.py`。

## Usage Scenarios

### 1. 创建全球商品并发布
1. `get_category.py` + `get_attribute_tree.py`（`merchantId`）
2. `add_global_item.py` 传完整 `body`
3. `create_publish_task.py` 发布到目标站点
4. `get_publish_task_result.py` 查发布结果

### 2. 查全球商品与改库存
1. `get_global_item_list.py`：`offset`、`page_size`
2. `get_global_item_info.py`：`global_item_id_list`
3. `update_stock.py` / `update_price.py`：POST `body`

## 调用原则

- 先看 **`developerProxy.httpStatus`**，再读 `*Response` 字段
- GET：业务参数放 JSON 顶层（runner 拼 queryString）
- POST：复杂接口传 `body`；简单接口可传顶层 body 字段
- 每个脚本 docstring 含 **官方文档 URL**（`module=90`）

## Not Applicable

- 店铺授权 → `linkfox-shopee-store-auth`
- 商户信息 → `linkfox-shopee-store-merchant`
- 单店 listing → `linkfox-shopee-store-product`
- 订单 → `linkfox-shopee-store-orders`
- 店铺信息 → `linkfox-shopee-store-shop`
- 图片/视频上传 → MediaSpace 模块

## 积分消耗规则

不消耗积分。

**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `references/api.md`. Do not interrupt the user's flow.

---
*For more high-quality, professional cross-border e-commerce skills, visit [LinkFox Skills](https://skill.linkfox.com/).*
