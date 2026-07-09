# linkfox-shopee-store-global-product — 参数与字段参考

Shopee **GlobalProduct 模块**全部 34 个 API，经 **`POST /shopee/developerProxy`** 转发。

授权见 **`linkfox-shopee-store-auth`**。官方索引：[v2.global_product.get_category](https://open.shopee.com/documents/v2/v2.global_product.get_category?module=90&type=1)

## 通用约定

- **Base URL**：`https://tool-gateway.linkfox.com`
- **Method**：POST（网关），上游 Method 见各接口
- **Auth**：Header `Authorization: <api_key>`（`LINKFOXAGENT_API_KEY`）
- **流程**：`POST /shopee/storeTokens` → `POST /shopee/developerProxy`
- **path**：须 `api/v2/global_product/...`
- **标识**：跨境 GlobalProduct 接口通常用 **`merchantId`**（商户级）；部分发布/映射接口需 **`shopId`**
- **官方文档 URL 规则**：`https://open.shopee.com/documents/v2/v2.global_product.{api}?module=90&type=1`
- **复杂 POST**（如 `add_global_item`、`create_publish_task`）：推荐传完整 `body` 对象

---

## GlobalProduct 模块总览

| # | API | Method | path | 脚本 | 官方文档 |
|---|-----|--------|------|------|----------|
| 1 | add_global_item | POST | `api/v2/global_product/add_global_item` | `add_global_item.py` | [doc](https://open.shopee.com/documents/v2/v2.global_product.add_global_item?module=90&type=1) |
| 2 | add_global_model | POST | `api/v2/global_product/add_global_model` | `add_global_model.py` | [doc](https://open.shopee.com/documents/v2/v2.global_product.add_global_model?module=90&type=1) |
| 3 | category_recommend | POST | `api/v2/global_product/category_recommend` | `category_recommend.py` | [doc](https://open.shopee.com/documents/v2/v2.global_product.category_recommend?module=90&type=1) |
| 4 | create_publish_task | POST | `api/v2/global_product/create_publish_task` | `create_publish_task.py` | [doc](https://open.shopee.com/documents/v2/v2.global_product.create_publish_task?module=90&type=1) |
| 5 | delete_global_item | POST | `api/v2/global_product/delete_global_item` | `delete_global_item.py` | [doc](https://open.shopee.com/documents/v2/v2.global_product.delete_global_item?module=90&type=1) |
| 6 | delete_global_model | POST | `api/v2/global_product/delete_global_model` | `delete_global_model.py` | [doc](https://open.shopee.com/documents/v2/v2.global_product.delete_global_model?module=90&type=1) |
| 7 | get_attribute_tree | GET | `api/v2/global_product/get_attribute_tree` | `get_attribute_tree.py` | [doc](https://open.shopee.com/documents/v2/v2.global_product.get_attribute_tree?module=90&type=1) |
| 8 | get_brand_list | GET | `api/v2/global_product/get_brand_list` | `get_brand_list.py` | [doc](https://open.shopee.com/documents/v2/v2.global_product.get_brand_list?module=90&type=1) |
| 9 | get_category | GET | `api/v2/global_product/get_category` | `get_category.py` | [doc](https://open.shopee.com/documents/v2/v2.global_product.get_category?module=90&type=1) |
| 10 | get_global_item_id | GET | `api/v2/global_product/get_global_item_id` | `get_global_item_id.py` | [doc](https://open.shopee.com/documents/v2/v2.global_product.get_global_item_id?module=90&type=1) |
| 11 | get_global_item_info | GET | `api/v2/global_product/get_global_item_info` | `get_global_item_info.py` | [doc](https://open.shopee.com/documents/v2/v2.global_product.get_global_item_info?module=90&type=1) |
| 12 | get_global_item_limit | GET | `api/v2/global_product/get_global_item_limit` | `get_global_item_limit.py` | [doc](https://open.shopee.com/documents/v2/v2.global_product.get_global_item_limit?module=90&type=1) |
| 13 | get_global_item_list | GET | `api/v2/global_product/get_global_item_list` | `get_global_item_list.py` | [doc](https://open.shopee.com/documents/v2/v2.global_product.get_global_item_list?module=90&type=1) |
| 14 | get_global_model_list | GET | `api/v2/global_product/get_global_model_list` | `get_global_model_list.py` | [doc](https://open.shopee.com/documents/v2/v2.global_product.get_global_model_list?module=90&type=1) |
| 15 | get_local_adjustment_rate | GET | `api/v2/global_product/get_local_adjustment_rate` | `get_local_adjustment_rate.py` | [doc](https://open.shopee.com/documents/v2/v2.global_product.get_local_adjustment_rate?module=90&type=1) |
| 16 | get_publish_task_result | GET | `api/v2/global_product/get_publish_task_result` | `get_publish_task_result.py` | [doc](https://open.shopee.com/documents/v2/v2.global_product.get_publish_task_result?module=90&type=1) |
| 17 | get_publishable_shop | GET | `api/v2/global_product/get_publishable_shop` | `get_publishable_shop.py` | [doc](https://open.shopee.com/documents/v2/v2.global_product.get_publishable_shop?module=90&type=1) |
| 18 | get_published_list | GET | `api/v2/global_product/get_published_list` | `get_published_list.py` | [doc](https://open.shopee.com/documents/v2/v2.global_product.get_published_list?module=90&type=1) |
| 19 | get_recommend_attribute | POST | `api/v2/global_product/get_recommend_attribute` | `get_recommend_attribute.py` | [doc](https://open.shopee.com/documents/v2/v2.global_product.get_recommend_attribute?module=90&type=1) |
| 20 | get_shop_publishable_status | GET | `api/v2/global_product/get_shop_publishable_status` | `get_shop_publishable_status.py` | [doc](https://open.shopee.com/documents/v2/v2.global_product.get_shop_publishable_status?module=90&type=1) |
| 21 | get_size_chart_detail | GET | `api/v2/global_product/get_size_chart_detail` | `get_size_chart_detail.py` | [doc](https://open.shopee.com/documents/v2/v2.global_product.get_size_chart_detail?module=90&type=1) |
| 22 | get_size_chart_list | GET | `api/v2/global_product/get_size_chart_list` | `get_size_chart_list.py` | [doc](https://open.shopee.com/documents/v2/v2.global_product.get_size_chart_list?module=90&type=1) |
| 23 | get_variations | GET | `api/v2/global_product/get_variations` | `get_variations.py` | [doc](https://open.shopee.com/documents/v2/v2.global_product.get_variations?module=90&type=1) |
| 24 | init_tier_variation | POST | `api/v2/global_product/init_tier_variation` | `init_tier_variation.py` | [doc](https://open.shopee.com/documents/v2/v2.global_product.init_tier_variation?module=90&type=1) |
| 25 | search_global_attribute_value_list | POST | `api/v2/global_product/search_global_attribute_value_list` | `search_global_attribute_value_list.py` | [doc](https://open.shopee.com/documents/v2/v2.global_product.search_global_attribute_value_list?module=90&type=1) |
| 26 | set_sync_field | POST | `api/v2/global_product/set_sync_field` | `set_sync_field.py` | [doc](https://open.shopee.com/documents/v2/v2.global_product.set_sync_field?module=90&type=1) |
| 27 | support_size_chart | POST | `api/v2/global_product/support_size_chart` | `support_size_chart.py` | [doc](https://open.shopee.com/documents/v2/v2.global_product.support_size_chart?module=90&type=1) |
| 28 | update_global_item | POST | `api/v2/global_product/update_global_item` | `update_global_item.py` | [doc](https://open.shopee.com/documents/v2/v2.global_product.update_global_item?module=90&type=1) |
| 29 | update_global_model | POST | `api/v2/global_product/update_global_model` | `update_global_model.py` | [doc](https://open.shopee.com/documents/v2/v2.global_product.update_global_model?module=90&type=1) |
| 30 | update_local_adjustment_rate | POST | `api/v2/global_product/update_local_adjustment_rate` | `update_local_adjustment_rate.py` | [doc](https://open.shopee.com/documents/v2/v2.global_product.update_local_adjustment_rate?module=90&type=1) |
| 31 | update_price | POST | `api/v2/global_product/update_price` | `update_price.py` | [doc](https://open.shopee.com/documents/v2/v2.global_product.update_price?module=90&type=1) |
| 32 | update_size_chart | POST | `api/v2/global_product/update_size_chart` | `update_size_chart.py` | [doc](https://open.shopee.com/documents/v2/v2.global_product.update_size_chart?module=90&type=1) |
| 33 | update_stock | POST | `api/v2/global_product/update_stock` | `update_stock.py` | [doc](https://open.shopee.com/documents/v2/v2.global_product.update_stock?module=90&type=1) |
| 34 | update_tier_variation | POST | `api/v2/global_product/update_tier_variation` | `update_tier_variation.py` | [doc](https://open.shopee.com/documents/v2/v2.global_product.update_tier_variation?module=90&type=1) |
通用入口：`global_product_api.py`（JSON 含 `"api": "<上表 API 名>"`）。

---

## 常用接口说明

### 类目与属性

| API | 要点 |
|-----|------|
| `get_category` | 全球商品类目树；可选 `language` |
| `get_attribute_tree` | 必填 `category_id` |
| `get_brand_list` | 必填 `offset`、`page_size`、`category_id` |
| `category_recommend` | POST：推荐类目 |
| `get_recommend_attribute` | POST：推荐属性 |

### 全球商品 CRUD

| API | 要点 |
|-----|------|
| `get_global_item_list` | 必填 `offset`、`page_size` |
| `get_global_item_info` | 必填 `global_item_id_list`（最多 50） |
| `add_global_item` / `update_global_item` | POST `body`：完整全球商品结构 |
| `delete_global_item` | 必填 `global_item_id` |

### SKU / 价格 / 库存

| API | 要点 |
|-----|------|
| `get_global_model_list` | 必填 `global_item_id` |
| `init_tier_variation` / `update_tier_variation` | 全球 SKU 规格 |
| `add_global_model` / `update_global_model` / `delete_global_model` | 全球 SKU 管理 |
| `update_price` / `update_stock` | POST body 含 global_item_id 与 price/stock 列表 |

### 发布到站点

| API | 要点 |
|-----|------|
| `create_publish_task` | 将全球商品发布到各站点店铺 |
| `get_publishable_shop` | 可发布的目标店铺 |
| `get_publish_task_result` | 发布任务结果 |
| `get_published_list` | 已发布列表 |
| `set_sync_field` | 设置同步字段 |
| `get_global_item_id` | shop item_id 映射到 global_item_id |
| `get_shop_publishable_status` | 店铺发布资格 |

### 其他

尺码表（`support_size_chart`、`update_size_chart`、`get_size_chart_*`）、本地调价（`get_local_adjustment_rate`、`update_local_adjustment_rate`）、`search_global_attribute_value_list` 等 — 见上表及官方文档。

---

## 网关错误码

| errcode | 含义 | 建议 |
|---------|------|------|
| 1002 | 参数/未登录 | 检查 merchantId/shopId 与 API Key |
| 1003 | 代理/网络异常 | 重试 |
| 1004 | 无授权记录 | auth skill |
| 1005 | path 未白名单 | 确认 `api/v2/global_product/...` |

---

## curl 示例

```bash
export KEY=$LINKFOX_AGENT_API_KEY
BASE=${LINKFOX_TOOL_GATEWAY}

# 全球类目
curl -X POST $BASE/shopee/developerProxy -H "Authorization: $KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "path": "api/v2/global_product/get_category",
    "method": "GET",
    "accessToken": "xxx",
    "merchantId": "12345",
    "queryString": "language=zh-hans"
  }'

# 全球商品列表
curl -X POST $BASE/shopee/developerProxy -H "Authorization: $KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "path": "api/v2/global_product/get_global_item_list",
    "method": "GET",
    "accessToken": "xxx",
    "merchantId": "12345",
    "queryString": "offset=0&page_size=20"
  }'
```

---

## Feedback API

```bash
curl -X POST https://skill-api.linkfox.com/api/v1/public/feedback \
  -H "Content-Type: application/json" \
  -d '{"skillName":"linkfox-shopee-store-global-product","sentiment":"POSITIVE",
       "category":"OTHER","content":"全球商品查询正常"}'
```
