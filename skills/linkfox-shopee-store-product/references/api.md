# linkfox-shopee-store-product — 参数与字段参考

Shopee **Product 模块**全部 57 个 API，经 **`POST /shopee/developerProxy`** 转发。

授权见 **`linkfox-shopee-store-auth`**。官方索引：[v2.product.get_category](https://open.shopee.com/documents/v2/v2.product.get_category?module=89&type=1)

## 通用约定

- **Base URL**：`${LINKFOX_TOOL_GATEWAY}`
- **Method**：POST（网关），上游 Method 见各接口
- **Auth**：Header `Authorization: <api_key>`（从 `LINKFOX_AGENT_API_KEY` 或 `LINKFOXAGENT_API_KEY` 读取）（如未配置 按 SKILL.md 的 **## 解决认证和积分问题** 处理）
- **流程**：`POST /shopee/storeTokens` → `POST /shopee/developerProxy`
- **path**：须 `api/v2/product/...`
- **官方文档 URL 规则**：`https://open.shopee.com/documents/v2/v2.product.{api}?module=89&type=1`
- **复杂 POST**（如 `add_item`、`update_item`）：推荐传完整 `body` 对象

---

## Product 模块总览

| # | API | Method | path | 脚本 | 官方文档 |
|---|-----|--------|------|------|----------|
| 1 | add_item | POST | `api/v2/product/add_item` | `add_item.py` | [doc](https://open.shopee.com/documents/v2/v2.product.add_item?module=89&type=1) |
| 2 | add_kit_item | POST | `api/v2/product/add_kit_item` | `add_kit_item.py` | [doc](https://open.shopee.com/documents/v2/v2.product.add_kit_item?module=89&type=1) |
| 3 | add_model | POST | `api/v2/product/add_model` | `add_model.py` | [doc](https://open.shopee.com/documents/v2/v2.product.add_model?module=89&type=1) |
| 4 | boost_item | POST | `api/v2/product/boost_item` | `boost_item.py` | [doc](https://open.shopee.com/documents/v2/v2.product.boost_item?module=89&type=1) |
| 5 | category_recommend | POST | `api/v2/product/category_recommend` | `category_recommend.py` | [doc](https://open.shopee.com/documents/v2/v2.product.category_recommend?module=89&type=1) |
| 6 | delete_item | POST | `api/v2/product/delete_item` | `delete_item.py` | [doc](https://open.shopee.com/documents/v2/v2.product.delete_item?module=89&type=1) |
| 7 | delete_model | POST | `api/v2/product/delete_model` | `delete_model.py` | [doc](https://open.shopee.com/documents/v2/v2.product.delete_model?module=89&type=1) |
| 8 | generate_kit_image | POST | `api/v2/product/generate_kit_image` | `generate_kit_image.py` | [doc](https://open.shopee.com/documents/v2/v2.product.generate_kit_image?module=89&type=1) |
| 9 | get_aitem_by_pitem_id | GET | `api/v2/product/get_aitem_by_pitem_id` | `get_aitem_by_pitem_id.py` | [doc](https://open.shopee.com/documents/v2/v2.product.get_aitem_by_pitem_id?module=89&type=1) |
| 10 | get_all_vehicle_list | GET | `api/v2/product/get_all_vehicle_list` | `get_all_vehicle_list.py` | [doc](https://open.shopee.com/documents/v2/v2.product.get_all_vehicle_list?module=89&type=1) |
| 11 | get_attribute_tree | GET | `api/v2/product/get_attribute_tree` | `get_attribute_tree.py` | [doc](https://open.shopee.com/documents/v2/v2.product.get_attribute_tree?module=89&type=1) |
| 12 | get_boosted_list | GET | `api/v2/product/get_boosted_list` | `get_boosted_list.py` | [doc](https://open.shopee.com/documents/v2/v2.product.get_boosted_list?module=89&type=1) |
| 13 | get_brand_list | GET | `api/v2/product/get_brand_list` | `get_brand_list.py` | [doc](https://open.shopee.com/documents/v2/v2.product.get_brand_list?module=89&type=1) |
| 14 | get_category | GET | `api/v2/product/get_category` | `get_category.py` | [doc](https://open.shopee.com/documents/v2/v2.product.get_category?module=89&type=1) |
| 15 | get_comment | GET | `api/v2/product/get_comment` | `get_comment.py` | [doc](https://open.shopee.com/documents/v2/v2.product.get_comment?module=89&type=1) |
| 16 | get_direct_item_list | GET | `api/v2/product/get_direct_item_list` | `get_direct_item_list.py` | [doc](https://open.shopee.com/documents/v2/v2.product.get_direct_item_list?module=89&type=1) |
| 17 | get_direct_shop_recommended_price | POST | `api/v2/product/get_direct_shop_recommended_price` | `get_direct_shop_recommended_price.py` | [doc](https://open.shopee.com/documents/v2/v2.product.get_direct_shop_recommended_price?module=89&type=1) |
| 18 | get_item_base_info | GET | `api/v2/product/get_item_base_info` | `get_item_base_info.py` | [doc](https://open.shopee.com/documents/v2/v2.product.get_item_base_info?module=89&type=1) |
| 19 | get_item_content_diagnosis_result | GET | `api/v2/product/get_item_content_diagnosis_result` | `get_item_content_diagnosis_result.py` | [doc](https://open.shopee.com/documents/v2/v2.product.get_item_content_diagnosis_result?module=89&type=1) |
| 20 | get_item_extra_info | GET | `api/v2/product/get_item_extra_info` | `get_item_extra_info.py` | [doc](https://open.shopee.com/documents/v2/v2.product.get_item_extra_info?module=89&type=1) |
| 21 | get_item_limit | GET | `api/v2/product/get_item_limit` | `get_item_limit.py` | [doc](https://open.shopee.com/documents/v2/v2.product.get_item_limit?module=89&type=1) |
| 22 | get_item_list | GET | `api/v2/product/get_item_list` | `get_item_list.py` | [doc](https://open.shopee.com/documents/v2/v2.product.get_item_list?module=89&type=1) |
| 23 | get_item_list_by_content_diagnosis | GET | `api/v2/product/get_item_list_by_content_diagnosis` | `get_item_list_by_content_diagnosis.py` | [doc](https://open.shopee.com/documents/v2/v2.product.get_item_list_by_content_diagnosis?module=89&type=1) |
| 24 | get_item_promotion | GET | `api/v2/product/get_item_promotion` | `get_item_promotion.py` | [doc](https://open.shopee.com/documents/v2/v2.product.get_item_promotion?module=89&type=1) |
| 25 | get_item_violation_info | GET | `api/v2/product/get_item_violation_info` | `get_item_violation_info.py` | [doc](https://open.shopee.com/documents/v2/v2.product.get_item_violation_info?module=89&type=1) |
| 26 | get_kit_item_info | GET | `api/v2/product/get_kit_item_info` | `get_kit_item_info.py` | [doc](https://open.shopee.com/documents/v2/v2.product.get_kit_item_info?module=89&type=1) |
| 27 | get_kit_item_limit | GET | `api/v2/product/get_kit_item_limit` | `get_kit_item_limit.py` | [doc](https://open.shopee.com/documents/v2/v2.product.get_kit_item_limit?module=89&type=1) |
| 28 | get_main_item_list | GET | `api/v2/product/get_main_item_list` | `get_main_item_list.py` | [doc](https://open.shopee.com/documents/v2/v2.product.get_main_item_list?module=89&type=1) |
| 29 | get_mart_item_by_outlet_item_id | GET | `api/v2/product/get_mart_item_by_outlet_item_id` | `get_mart_item_by_outlet_item_id.py` | [doc](https://open.shopee.com/documents/v2/v2.product.get_mart_item_by_outlet_item_id?module=89&type=1) |
| 30 | get_mart_item_mapping_by_id | GET | `api/v2/product/get_mart_item_mapping_by_id` | `get_mart_item_mapping_by_id.py` | [doc](https://open.shopee.com/documents/v2/v2.product.get_mart_item_mapping_by_id?module=89&type=1) |
| 31 | get_model_list | GET | `api/v2/product/get_model_list` | `get_model_list.py` | [doc](https://open.shopee.com/documents/v2/v2.product.get_model_list?module=89&type=1) |
| 32 | get_product_certification_rule | GET | `api/v2/product/get_product_certification_rule` | `get_product_certification_rule.py` | [doc](https://open.shopee.com/documents/v2/v2.product.get_product_certification_rule?module=89&type=1) |
| 33 | get_recommend_attribute | POST | `api/v2/product/get_recommend_attribute` | `get_recommend_attribute.py` | [doc](https://open.shopee.com/documents/v2/v2.product.get_recommend_attribute?module=89&type=1) |
| 34 | get_size_chart_detail | GET | `api/v2/product/get_size_chart_detail` | `get_size_chart_detail.py` | [doc](https://open.shopee.com/documents/v2/v2.product.get_size_chart_detail?module=89&type=1) |
| 35 | get_size_chart_list | GET | `api/v2/product/get_size_chart_list` | `get_size_chart_list.py` | [doc](https://open.shopee.com/documents/v2/v2.product.get_size_chart_list?module=89&type=1) |
| 36 | get_ssp_info | GET | `api/v2/product/get_ssp_info` | `get_ssp_info.py` | [doc](https://open.shopee.com/documents/v2/v2.product.get_ssp_info?module=89&type=1) |
| 37 | get_ssp_list | GET | `api/v2/product/get_ssp_list` | `get_ssp_list.py` | [doc](https://open.shopee.com/documents/v2/v2.product.get_ssp_list?module=89&type=1) |
| 38 | get_variations | GET | `api/v2/product/get_variations` | `get_variations.py` | [doc](https://open.shopee.com/documents/v2/v2.product.get_variations?module=89&type=1) |
| 39 | get_vehicle_list_by_compatibility_detail | GET | `api/v2/product/get_vehicle_list_by_compatibility_detail` | `get_vehicle_list_by_compatibility_detail.py` | [doc](https://open.shopee.com/documents/v2/v2.product.get_vehicle_list_by_compatibility_detail?module=89&type=1) |
| 40 | get_weight_recommendation | POST | `api/v2/product/get_weight_recommendation` | `get_weight_recommendation.py` | [doc](https://open.shopee.com/documents/v2/v2.product.get_weight_recommendation?module=89&type=1) |
| 41 | init_tier_variation | POST | `api/v2/product/init_tier_variation` | `init_tier_variation.py` | [doc](https://open.shopee.com/documents/v2/v2.product.init_tier_variation?module=89&type=1) |
| 42 | link_ssp | POST | `api/v2/product/link_ssp` | `link_ssp.py` | [doc](https://open.shopee.com/documents/v2/v2.product.link_ssp?module=89&type=1) |
| 43 | publish_item_to_outlet_shop | POST | `api/v2/product/publish_item_to_outlet_shop` | `publish_item_to_outlet_shop.py` | [doc](https://open.shopee.com/documents/v2/v2.product.publish_item_to_outlet_shop?module=89&type=1) |
| 44 | register_brand | POST | `api/v2/product/register_brand` | `register_brand.py` | [doc](https://open.shopee.com/documents/v2/v2.product.register_brand?module=89&type=1) |
| 45 | reply_comment | POST | `api/v2/product/reply_comment` | `reply_comment.py` | [doc](https://open.shopee.com/documents/v2/v2.product.reply_comment?module=89&type=1) |
| 46 | search_attribute_value_list | POST | `api/v2/product/search_attribute_value_list` | `search_attribute_value_list.py` | [doc](https://open.shopee.com/documents/v2/v2.product.search_attribute_value_list?module=89&type=1) |
| 47 | search_item | GET | `api/v2/product/search_item` | `search_item.py` | [doc](https://open.shopee.com/documents/v2/v2.product.search_item?module=89&type=1) |
| 48 | search_unpackaged_model_list | POST | `api/v2/product/search_unpackaged_model_list` | `search_unpackaged_model_list.py` | [doc](https://open.shopee.com/documents/v2/v2.product.search_unpackaged_model_list?module=89&type=1) |
| 49 | unlink_ssp | POST | `api/v2/product/unlink_ssp` | `unlink_ssp.py` | [doc](https://open.shopee.com/documents/v2/v2.product.unlink_ssp?module=89&type=1) |
| 50 | unlist_item | POST | `api/v2/product/unlist_item` | `unlist_item.py` | [doc](https://open.shopee.com/documents/v2/v2.product.unlist_item?module=89&type=1) |
| 51 | update_item | POST | `api/v2/product/update_item` | `update_item.py` | [doc](https://open.shopee.com/documents/v2/v2.product.update_item?module=89&type=1) |
| 52 | update_kit_item | POST | `api/v2/product/update_kit_item` | `update_kit_item.py` | [doc](https://open.shopee.com/documents/v2/v2.product.update_kit_item?module=89&type=1) |
| 53 | update_model | POST | `api/v2/product/update_model` | `update_model.py` | [doc](https://open.shopee.com/documents/v2/v2.product.update_model?module=89&type=1) |
| 54 | update_price | POST | `api/v2/product/update_price` | `update_price.py` | [doc](https://open.shopee.com/documents/v2/v2.product.update_price?module=89&type=1) |
| 55 | update_sip_item_price | POST | `api/v2/product/update_sip_item_price` | `update_sip_item_price.py` | [doc](https://open.shopee.com/documents/v2/v2.product.update_sip_item_price?module=89&type=1) |
| 56 | update_stock | POST | `api/v2/product/update_stock` | `update_stock.py` | [doc](https://open.shopee.com/documents/v2/v2.product.update_stock?module=89&type=1) |
| 57 | update_tier_variation | POST | `api/v2/product/update_tier_variation` | `update_tier_variation.py` | [doc](https://open.shopee.com/documents/v2/v2.product.update_tier_variation?module=89&type=1) |
通用入口：`product_api.py`（JSON 含 `"api": "<上表 API 名>"`）。

---

## 常用接口说明

### 类目与属性

| API | 要点 |
|-----|------|
| `get_category` | 类目树；可选 `language` |
| `get_attribute_tree` | 必填 `category_id`；上架前获取必填属性 |
| `get_brand_list` | 必填 `offset`、`page_size`、`category_id` |
| `category_recommend` | POST body：根据标题/图片推荐类目 |
| `get_recommend_attribute` | POST：推荐属性值 |

### 商品 CRUD

| API | 要点 |
|-----|------|
| `get_item_list` | 必填 `offset`、`page_size`；可选 `item_status` |
| `get_item_base_info` | 必填 `item_id_list`（最多 50，逗号分隔） |
| `add_item` / `update_item` | POST `body`：完整商品结构 |
| `delete_item` | 必填 `item_id` |
| `unlist_item` | POST `body.item_list` 上下架 |

### SKU / 价格 / 库存

| API | 要点 |
|-----|------|
| `get_model_list` | 必填 `item_id` |
| `init_tier_variation` / `update_tier_variation` | 规格/SKU 结构 |
| `update_price` / `update_stock` | POST body 含 `item_id` 与 price/stock 列表 |
| `boost_item` | 置顶推广，最多 5 个 item |

### SSP（Shopee Standard Product）

| API | 要点 |
|-----|------|
| `get_ssp_list` | 搜索 SSP 标准品 |
| `get_ssp_info` | 按 ssp_id / gtin / oem 查详情 |
| `link_ssp` | 将已有 listing 关联到 SSP |
| `unlink_ssp` | 解除 SSP 关联 |

### 搜索与评论

| API | 要点 |
|-----|------|
| `search_item` | 店内商品搜索 |
| `get_comment` / `reply_comment` | 评价查询与回复 |

### 扩展能力

Kit 组合商品、Direct Shop、Mart/Outlet、车辆兼容、内容诊断、尺码表、违规信息等 — 见上表对应 API 及官方文档。

---

## 网关错误码

| errcode | 含义 | 建议 |
|---------|------|------|
| 1002 | 参数/未登录 | 检查 shopId 与 API Key |
| 1003 | 代理/网络异常 | 重试 |
| 1004 | 无授权记录 | auth skill |
| 1005 | path 未白名单 | 确认 `api/v2/product/...` |
| HTTP 402 | 积分不足 | HTTP 402：按 SKILL.md 的 **## 解决认证和积分问题** 处理。 |

---

## curl 示例

```bash
export KEY=$LINKFOXAGENT_API_KEY
BASE=https://tool-gateway.linkfox.com

# 类目树
curl -X POST $BASE/shopee/developerProxy -H "Authorization: $KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "path": "api/v2/product/get_category",
    "method": "GET",
    "accessToken": "xxx",
    "shopId": "67890",
    "queryString": "language=zh-hans"
  }'

# 商品列表
curl -X POST $BASE/shopee/developerProxy -H "Authorization: $KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "path": "api/v2/product/get_item_list",
    "method": "GET",
    "accessToken": "xxx",
    "shopId": "67890",
    "queryString": "offset=0&page_size=20&item_status=NORMAL"
  }'
```

---

## Feedback API

```bash
curl -X POST https://skill-api.linkfox.com/api/v1/public/feedback \
  -H "Content-Type: application/json" \
  -d '{"skillName":"linkfox-shopee-store-product","sentiment":"POSITIVE",
       "category":"OTHER","content":"商品列表查询正常"}'
```
