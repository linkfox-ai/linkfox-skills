# linkfox-shopee-store-add-on-deal — 参数与字段参考

Shopee **Add-On Deal 模块**全部 14 个 API，经 **`POST /shopee/developerProxy`** 转发。

授权见 **`linkfox-shopee-store-auth`**。官方索引：[v2.add_on_deal.add_add_on_deal](https://open.shopee.com/documents/v2/v2.add_on_deal.add_add_on_deal?module=111&type=1)

## 通用约定

- **path**：须 `api/v2/add_on_deal/...`
- **标识**：通常传 **`shopId`**
- **官方文档 URL 规则**：`https://open.shopee.com/documents/v2/v2.add_on_deal.{api}?module=111&type=1`

---

## Add-On Deal 模块总览

| # | API | Method | path | 脚本 | 官方文档 |
|---|-----|--------|------|------|----------|
| 1 | add_add_on_deal | POST | `api/v2/add_on_deal/add_add_on_deal` | `add_add_on_deal.py` | [doc](https://open.shopee.com/documents/v2/v2.add_on_deal.add_add_on_deal?module=111&type=1) |
| 2 | add_add_on_deal_main_item | POST | `api/v2/add_on_deal/add_add_on_deal_main_item` | `add_add_on_deal_main_item.py` | [doc](https://open.shopee.com/documents/v2/v2.add_on_deal.add_add_on_deal_main_item?module=111&type=1) |
| 3 | add_add_on_deal_sub_item | POST | `api/v2/add_on_deal/add_add_on_deal_sub_item` | `add_add_on_deal_sub_item.py` | [doc](https://open.shopee.com/documents/v2/v2.add_on_deal.add_add_on_deal_sub_item?module=111&type=1) |
| 4 | delete_add_on_deal | POST | `api/v2/add_on_deal/delete_add_on_deal` | `delete_add_on_deal.py` | [doc](https://open.shopee.com/documents/v2/v2.add_on_deal.delete_add_on_deal?module=111&type=1) |
| 5 | delete_add_on_deal_main_item | POST | `api/v2/add_on_deal/delete_add_on_deal_main_item` | `delete_add_on_deal_main_item.py` | [doc](https://open.shopee.com/documents/v2/v2.add_on_deal.delete_add_on_deal_main_item?module=111&type=1) |
| 6 | delete_add_on_deal_sub_item | POST | `api/v2/add_on_deal/delete_add_on_deal_sub_item` | `delete_add_on_deal_sub_item.py` | [doc](https://open.shopee.com/documents/v2/v2.add_on_deal.delete_add_on_deal_sub_item?module=111&type=1) |
| 7 | end_add_on_deal | POST | `api/v2/add_on_deal/end_add_on_deal` | `end_add_on_deal.py` | [doc](https://open.shopee.com/documents/v2/v2.add_on_deal.end_add_on_deal?module=111&type=1) |
| 8 | get_add_on_deal | GET | `api/v2/add_on_deal/get_add_on_deal` | `get_add_on_deal.py` | [doc](https://open.shopee.com/documents/v2/v2.add_on_deal.get_add_on_deal?module=111&type=1) |
| 9 | get_add_on_deal_list | GET | `api/v2/add_on_deal/get_add_on_deal_list` | `get_add_on_deal_list.py` | [doc](https://open.shopee.com/documents/v2/v2.add_on_deal.get_add_on_deal_list?module=111&type=1) |
| 10 | get_add_on_deal_main_item | GET | `api/v2/add_on_deal/get_add_on_deal_main_item` | `get_add_on_deal_main_item.py` | [doc](https://open.shopee.com/documents/v2/v2.add_on_deal.get_add_on_deal_main_item?module=111&type=1) |
| 11 | get_add_on_deal_sub_item | GET | `api/v2/add_on_deal/get_add_on_deal_sub_item` | `get_add_on_deal_sub_item.py` | [doc](https://open.shopee.com/documents/v2/v2.add_on_deal.get_add_on_deal_sub_item?module=111&type=1) |
| 12 | update_add_on_deal | POST | `api/v2/add_on_deal/update_add_on_deal` | `update_add_on_deal.py` | [doc](https://open.shopee.com/documents/v2/v2.add_on_deal.update_add_on_deal?module=111&type=1) |
| 13 | update_add_on_deal_main_item | POST | `api/v2/add_on_deal/update_add_on_deal_main_item` | `update_add_on_deal_main_item.py` | [doc](https://open.shopee.com/documents/v2/v2.add_on_deal.update_add_on_deal_main_item?module=111&type=1) |
| 14 | update_add_on_deal_sub_item | POST | `api/v2/add_on_deal/update_add_on_deal_sub_item` | `update_add_on_deal_sub_item.py` | [doc](https://open.shopee.com/documents/v2/v2.add_on_deal.update_add_on_deal_sub_item?module=111&type=1) |
通用入口：`add_on_deal_api.py`（JSON 含 `"api": "<上表 API 名>"`）。

---

## 常用接口说明

| API | 要点 |
|-----|------|
| `add_add_on_deal` | 创建加购优惠；POST `body` |
| `add_add_on_deal_main_item` / `add_add_on_deal_sub_item` | 添加主商品 / 加购商品 |
| `get_add_on_deal_list` | 活动列表 |
| `get_add_on_deal` | 活动详情 |
| `get_add_on_deal_main_item` / `get_add_on_deal_sub_item` | 主商品 / 加购商品列表 |
| `update_add_on_deal` / `update_*_item` | 更新活动或商品 |
| `end_add_on_deal` | 提前结束 |
| `delete_add_on_deal` / `delete_*_item` | 删除活动或商品 |

---

## curl 示例

```bash
curl -X POST ${LINKFOX_TOOL_GATEWAY}/shopee/developerProxy \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "path": "api/v2/add_on_deal/get_add_on_deal_list",
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
  -d '{"skillName":"linkfox-shopee-store-add-on-deal","sentiment":"POSITIVE",
       "category":"OTHER","content":"加购优惠查询正常"}'
```
