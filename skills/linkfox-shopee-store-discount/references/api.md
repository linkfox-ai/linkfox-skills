# linkfox-shopee-store-discount — 参数与字段参考

Shopee **Discount 模块**全部 12 个 API，经 **`POST /shopee/developerProxy`** 转发。

授权见 **`linkfox-shopee-store-auth`**。官方索引：[v2.discount.add_discount](https://open.shopee.com/documents/v2/v2.discount.add_discount?module=99&type=1)

## 通用约定

- **path**：须 `api/v2/discount/...`
- **标识**：通常传 **`shopId`**
- **官方文档 URL 规则**：`https://open.shopee.com/documents/v2/v2.discount.{api}?module=99&type=1`

---

## Discount 模块总览

| # | API | Method | path | 脚本 | 官方文档 |
|---|-----|--------|------|------|----------|
| 1 | add_discount | POST | `api/v2/discount/add_discount` | `add_discount.py` | [doc](https://open.shopee.com/documents/v2/v2.discount.add_discount?module=99&type=1) |
| 2 | add_discount_item | POST | `api/v2/discount/add_discount_item` | `add_discount_item.py` | [doc](https://open.shopee.com/documents/v2/v2.discount.add_discount_item?module=99&type=1) |
| 3 | delete_discount | POST | `api/v2/discount/delete_discount` | `delete_discount.py` | [doc](https://open.shopee.com/documents/v2/v2.discount.delete_discount?module=99&type=1) |
| 4 | delete_discount_item | POST | `api/v2/discount/delete_discount_item` | `delete_discount_item.py` | [doc](https://open.shopee.com/documents/v2/v2.discount.delete_discount_item?module=99&type=1) |
| 5 | delete_sip_discount | POST | `api/v2/discount/delete_sip_discount` | `delete_sip_discount.py` | [doc](https://open.shopee.com/documents/v2/v2.discount.delete_sip_discount?module=99&type=1) |
| 6 | end_discount | POST | `api/v2/discount/end_discount` | `end_discount.py` | [doc](https://open.shopee.com/documents/v2/v2.discount.end_discount?module=99&type=1) |
| 7 | get_discount | GET | `api/v2/discount/get_discount` | `get_discount.py` | [doc](https://open.shopee.com/documents/v2/v2.discount.get_discount?module=99&type=1) |
| 8 | get_discount_list | GET | `api/v2/discount/get_discount_list` | `get_discount_list.py` | [doc](https://open.shopee.com/documents/v2/v2.discount.get_discount_list?module=99&type=1) |
| 9 | get_sip_discounts | GET | `api/v2/discount/get_sip_discounts` | `get_sip_discounts.py` | [doc](https://open.shopee.com/documents/v2/v2.discount.get_sip_discounts?module=99&type=1) |
| 10 | set_sip_discount | POST | `api/v2/discount/set_sip_discount` | `set_sip_discount.py` | [doc](https://open.shopee.com/documents/v2/v2.discount.set_sip_discount?module=99&type=1) |
| 11 | update_discount | POST | `api/v2/discount/update_discount` | `update_discount.py` | [doc](https://open.shopee.com/documents/v2/v2.discount.update_discount?module=99&type=1) |
| 12 | update_discount_item | POST | `api/v2/discount/update_discount_item` | `update_discount_item.py` | [doc](https://open.shopee.com/documents/v2/v2.discount.update_discount_item?module=99&type=1) |
通用入口：`discount_api.py`（JSON 含 `"api": "<上表 API 名>"`）。

---

## 常用接口说明

| API | 要点 |
|-----|------|
| `add_discount` | 创建折扣活动；POST `body` |
| `add_discount_item` | 向活动添加商品/SKU |
| `get_discount_list` | 折扣活动列表 |
| `get_discount` | 单个活动详情 |
| `update_discount` / `update_discount_item` | 更新活动/商品折扣 |
| `end_discount` | 提前结束活动 |
| `delete_discount` / `delete_discount_item` | 删除活动/商品 |
| `get_sip_discounts` / `set_sip_discount` / `delete_sip_discount` | SIP 跨境折扣 |

---

## curl 示例

```bash
curl -X POST ${LINKFOX_TOOL_GATEWAY}/shopee/developerProxy \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "path": "api/v2/discount/get_discount_list",
    "method": "GET",
    "accessToken": "xxx",
    "shopId": "67890",
    "queryString": "discount_status=ongoing&page_no=1&page_size=20"
  }'
```

---

## Feedback API

```bash
curl -X POST https://skill-api.linkfox.com/api/v1/public/feedback \
  -H "Content-Type: application/json" \
  -d '{"skillName":"linkfox-shopee-store-discount","sentiment":"POSITIVE",
       "category":"OTHER","content":"折扣活动查询正常"}'
```
