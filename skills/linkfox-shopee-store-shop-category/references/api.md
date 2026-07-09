# linkfox-shopee-store-shop-category — 参数与字段参考

Shopee **Shop Category 模块**全部 7 个 API，经 **`POST /shopee/developerProxy`** 转发。

授权见 **`linkfox-shopee-store-auth`**。官方索引：[v2.shop_category.add_shop_category](https://open.shopee.com/documents/v2/v2.shop_category.add_shop_category?module=101&type=1)

## 通用约定

- **path**：须 `api/v2/shop_category/...`
- **标识**：通常传 **`shopId`**
- **官方文档 URL 规则**：`https://open.shopee.com/documents/v2/v2.shop_category.{api}?module=101&type=1`

---

## Shop Category 模块总览

| # | API | Method | path | 脚本 | 官方文档 |
|---|-----|--------|------|------|----------|
| 1 | add_item_list | POST | `api/v2/shop_category/add_item_list` | `add_item_list.py` | [doc](https://open.shopee.com/documents/v2/v2.shop_category.add_item_list?module=101&type=1) |
| 2 | add_shop_category | POST | `api/v2/shop_category/add_shop_category` | `add_shop_category.py` | [doc](https://open.shopee.com/documents/v2/v2.shop_category.add_shop_category?module=101&type=1) |
| 3 | delete_item_list | POST | `api/v2/shop_category/delete_item_list` | `delete_item_list.py` | [doc](https://open.shopee.com/documents/v2/v2.shop_category.delete_item_list?module=101&type=1) |
| 4 | delete_shop_category | POST | `api/v2/shop_category/delete_shop_category` | `delete_shop_category.py` | [doc](https://open.shopee.com/documents/v2/v2.shop_category.delete_shop_category?module=101&type=1) |
| 5 | get_item_list | GET | `api/v2/shop_category/get_item_list` | `get_item_list.py` | [doc](https://open.shopee.com/documents/v2/v2.shop_category.get_item_list?module=101&type=1) |
| 6 | get_shop_category_list | GET | `api/v2/shop_category/get_shop_category_list` | `get_shop_category_list.py` | [doc](https://open.shopee.com/documents/v2/v2.shop_category.get_shop_category_list?module=101&type=1) |
| 7 | update_shop_category | POST | `api/v2/shop_category/update_shop_category` | `update_shop_category.py` | [doc](https://open.shopee.com/documents/v2/v2.shop_category.update_shop_category?module=101&type=1) |
通用入口：`shop_category_api.py`（JSON 含 `"api": "<上表 API 名>"`）。

---

## 常用接口说明

| API | 要点 |
|-----|------|
| `add_shop_category` | 创建店铺分类；POST `body` |
| `get_shop_category_list` | 分类列表 |
| `update_shop_category` | 更新分类 |
| `delete_shop_category` | 删除分类 |
| `add_item_list` | 向分类添加商品 |
| `get_item_list` | 分类内商品列表 |
| `delete_item_list` | 从分类移除商品 |

---

## curl 示例

请求地址从环境变量 `${LINKFOX_TOOL_GATEWAY}` 读取（默认 `https://tool-gateway.linkfox.com`）。认证从 `LINKFOX_AGENT_API_KEY` 或 `LINKFOXAGENT_API_KEY` 任一环境变量读取。

```bash
curl -X POST ${LINKFOX_TOOL_GATEWAY}/shopee/developerProxy \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "path": "api/v2/shop_category/get_shop_category_list",
    "method": "GET",
    "accessToken": "xxx",
    "shopId": "67890"
  }'
```

---

## Feedback API

```bash
curl -X POST https://skill-api.linkfox.com/api/v1/public/feedback \
  -H "Content-Type: application/json" \
  -d '{"skillName":"linkfox-shopee-store-shop-category","sentiment":"POSITIVE",
       "category":"OTHER","content":"店铺分类查询正常"}'
```
