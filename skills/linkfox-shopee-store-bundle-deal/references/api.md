# linkfox-shopee-store-bundle-deal — 参数与字段参考

Shopee **Bundle Deal 模块**全部 10 个 API，经 **`POST /shopee/developerProxy`** 转发。

授权见 **`linkfox-shopee-store-auth`**。官方索引：[v2.bundle_deal.add_bundle_deal](https://open.shopee.com/documents/v2/v2.bundle_deal.add_bundle_deal?module=110&type=1)

## 通用约定

- **path**：须 `api/v2/bundle_deal/...`
- **标识**：通常传 **`shopId`**
- **官方文档 URL 规则**：`https://open.shopee.com/documents/v2/v2.bundle_deal.{api}?module=110&type=1`

---

## Bundle Deal 模块总览

| # | API | Method | path | 脚本 | 官方文档 |
|---|-----|--------|------|------|----------|
| 1 | add_bundle_deal | POST | `api/v2/bundle_deal/add_bundle_deal` | `add_bundle_deal.py` | [doc](https://open.shopee.com/documents/v2/v2.bundle_deal.add_bundle_deal?module=110&type=1) |
| 2 | add_bundle_deal_item | POST | `api/v2/bundle_deal/add_bundle_deal_item` | `add_bundle_deal_item.py` | [doc](https://open.shopee.com/documents/v2/v2.bundle_deal.add_bundle_deal_item?module=110&type=1) |
| 3 | delete_bundle_deal | POST | `api/v2/bundle_deal/delete_bundle_deal` | `delete_bundle_deal.py` | [doc](https://open.shopee.com/documents/v2/v2.bundle_deal.delete_bundle_deal?module=110&type=1) |
| 4 | delete_bundle_deal_item | POST | `api/v2/bundle_deal/delete_bundle_deal_item` | `delete_bundle_deal_item.py` | [doc](https://open.shopee.com/documents/v2/v2.bundle_deal.delete_bundle_deal_item?module=110&type=1) |
| 5 | end_bundle_deal | POST | `api/v2/bundle_deal/end_bundle_deal` | `end_bundle_deal.py` | [doc](https://open.shopee.com/documents/v2/v2.bundle_deal.end_bundle_deal?module=110&type=1) |
| 6 | get_bundle_deal | GET | `api/v2/bundle_deal/get_bundle_deal` | `get_bundle_deal.py` | [doc](https://open.shopee.com/documents/v2/v2.bundle_deal.get_bundle_deal?module=110&type=1) |
| 7 | get_bundle_deal_item | GET | `api/v2/bundle_deal/get_bundle_deal_item` | `get_bundle_deal_item.py` | [doc](https://open.shopee.com/documents/v2/v2.bundle_deal.get_bundle_deal_item?module=110&type=1) |
| 8 | get_bundle_deal_list | GET | `api/v2/bundle_deal/get_bundle_deal_list` | `get_bundle_deal_list.py` | [doc](https://open.shopee.com/documents/v2/v2.bundle_deal.get_bundle_deal_list?module=110&type=1) |
| 9 | update_bundle_deal | POST | `api/v2/bundle_deal/update_bundle_deal` | `update_bundle_deal.py` | [doc](https://open.shopee.com/documents/v2/v2.bundle_deal.update_bundle_deal?module=110&type=1) |
| 10 | update_bundle_deal_item | POST | `api/v2/bundle_deal/update_bundle_deal_item` | `update_bundle_deal_item.py` | [doc](https://open.shopee.com/documents/v2/v2.bundle_deal.update_bundle_deal_item?module=110&type=1) |
通用入口：`bundle_deal_api.py`（JSON 含 `"api": "<上表 API 名>"`）。

---

## 常用接口说明

| API | 要点 |
|-----|------|
| `add_bundle_deal` | 创建套装优惠；POST `body` |
| `add_bundle_deal_item` | 添加参与商品 |
| `get_bundle_deal_list` | 套装活动列表 |
| `get_bundle_deal` | 活动详情 |
| `get_bundle_deal_item` | 活动内商品 |
| `update_bundle_deal` / `update_bundle_deal_item` | 更新活动/商品 |
| `end_bundle_deal` | 提前结束 |
| `delete_bundle_deal` / `delete_bundle_deal_item` | 删除活动/商品 |

---

## curl 示例

```bash
curl -X POST ${LINKFOX_TOOL_GATEWAY}/shopee/developerProxy \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "path": "api/v2/bundle_deal/get_bundle_deal_list",
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
  -d '{"skillName":"linkfox-shopee-store-bundle-deal","sentiment":"POSITIVE",
       "category":"OTHER","content":"套装优惠查询正常"}'
```
