# linkfox-shopee-store-voucher — 参数与字段参考

Shopee **Voucher 模块**全部 6 个 API，经 **`POST /shopee/developerProxy`** 转发。

授权见 **`linkfox-shopee-store-auth`**。官方索引：[v2.voucher.add_voucher](https://open.shopee.com/documents/v2/v2.voucher.add_voucher?module=112&type=1)

## 通用约定

- **path**：须 `api/v2/voucher/...`
- **标识**：通常传 **`shopId`**
- **官方文档 URL 规则**：`https://open.shopee.com/documents/v2/v2.voucher.{api}?module=112&type=1`

---

## Voucher 模块总览

| # | API | Method | path | 脚本 | 官方文档 |
|---|-----|--------|------|------|----------|
| 1 | add_voucher | POST | `api/v2/voucher/add_voucher` | `add_voucher.py` | [doc](https://open.shopee.com/documents/v2/v2.voucher.add_voucher?module=112&type=1) |
| 2 | delete_voucher | POST | `api/v2/voucher/delete_voucher` | `delete_voucher.py` | [doc](https://open.shopee.com/documents/v2/v2.voucher.delete_voucher?module=112&type=1) |
| 3 | end_voucher | POST | `api/v2/voucher/end_voucher` | `end_voucher.py` | [doc](https://open.shopee.com/documents/v2/v2.voucher.end_voucher?module=112&type=1) |
| 4 | get_voucher | GET | `api/v2/voucher/get_voucher` | `get_voucher.py` | [doc](https://open.shopee.com/documents/v2/v2.voucher.get_voucher?module=112&type=1) |
| 5 | get_voucher_list | GET | `api/v2/voucher/get_voucher_list` | `get_voucher_list.py` | [doc](https://open.shopee.com/documents/v2/v2.voucher.get_voucher_list?module=112&type=1) |
| 6 | update_voucher | POST | `api/v2/voucher/update_voucher` | `update_voucher.py` | [doc](https://open.shopee.com/documents/v2/v2.voucher.update_voucher?module=112&type=1) |
通用入口：`voucher_api.py`（JSON 含 `"api": "<上表 API 名>"`）。

---

## 常用接口说明

| API | 要点 |
|-----|------|
| `add_voucher` | 创建店铺优惠券；POST `body` |
| `get_voucher_list` | 优惠券列表 |
| `get_voucher` | 优惠券详情 |
| `update_voucher` | 更新优惠券 |
| `end_voucher` | 提前结束 |
| `delete_voucher` | 删除优惠券 |

---

## curl 示例

```bash
curl -X POST ${LINKFOX_TOOL_GATEWAY}/shopee/developerProxy \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "path": "api/v2/voucher/get_voucher_list",
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
  -d '{"skillName":"linkfox-shopee-store-voucher","sentiment":"POSITIVE",
       "category":"OTHER","content":"优惠券查询正常"}'
```
