# linkfox-shopee-store-sbs — 参数与字段参考

Shopee **SBS 模块**全部 5 个 API，经 **`POST /shopee/developerProxy`** 转发。

授权见 **`linkfox-shopee-store-auth`**。官方索引：[v2.sbs.get_bound_whs_info](https://open.shopee.com/documents/v2/v2.sbs.get_bound_whs_info?module=124&type=1)

## 通用约定

- **path**：须 `api/v2/sbs/...`
- **标识**：通常传 **`shopId`**
- **官方文档 URL 规则**：`https://open.shopee.com/documents/v2/v2.sbs.{api}?module=124&type=1`

---

## SBS 模块总览

| # | API | Method | path | 脚本 | 官方文档 |
|---|-----|--------|------|------|----------|
| 1 | get_bound_whs_info | GET | `api/v2/sbs/get_bound_whs_info` | `get_bound_whs_info.py` | [doc](https://open.shopee.com/documents/v2/v2.sbs.get_bound_whs_info?module=124&type=1) |
| 2 | get_current_inventory | GET | `api/v2/sbs/get_current_inventory` | `get_current_inventory.py` | [doc](https://open.shopee.com/documents/v2/v2.sbs.get_current_inventory?module=124&type=1) |
| 3 | get_expiry_report | GET | `api/v2/sbs/get_expiry_report` | `get_expiry_report.py` | [doc](https://open.shopee.com/documents/v2/v2.sbs.get_expiry_report?module=124&type=1) |
| 4 | get_stock_aging | GET | `api/v2/sbs/get_stock_aging` | `get_stock_aging.py` | [doc](https://open.shopee.com/documents/v2/v2.sbs.get_stock_aging?module=124&type=1) |
| 5 | get_stock_movement | GET | `api/v2/sbs/get_stock_movement` | `get_stock_movement.py` | [doc](https://open.shopee.com/documents/v2/v2.sbs.get_stock_movement?module=124&type=1) |
通用入口：`sbs_api.py`（JSON 含 `"api": "<上表 API 名>"`）。

---

## 常用接口说明

| API | 要点 |
|-----|------|
| `get_bound_whs_info` | 已绑定仓库信息 |
| `get_current_inventory` | 当前 SBS 库存 |
| `get_expiry_report` | 效期报表 |
| `get_stock_aging` | 库龄报表 |
| `get_stock_movement` | 库存变动记录 |

---

## curl 示例

```bash
curl -X POST ${LINKFOX_TOOL_GATEWAY}/shopee/developerProxy \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "path": "api/v2/sbs/get_bound_whs_info",
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
  -d '{"skillName":"linkfox-shopee-store-sbs","sentiment":"POSITIVE",
       "category":"OTHER","content":"SBS库存查询正常"}'
```
