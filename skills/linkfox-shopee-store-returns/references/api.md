# linkfox-shopee-store-returns — 参数与字段参考

Shopee **Returns 模块**全部 15 个 API，经 **`POST /shopee/developerProxy`** 转发。

授权见 **`linkfox-shopee-store-auth`**。官方索引：[v2.returns.get_return_list](https://open.shopee.com/documents/v2/v2.returns.get_return_list?module=102&type=1)

## 通用约定

- **Base URL**：`${LINKFOX_TOOL_GATEWAY}`
- **Method**：POST（网关），上游 Method 见各接口
- **Auth**：Header `Authorization: <api_key>`（从 `LINKFOX_AGENT_API_KEY` 或 `LINKFOXAGENT_API_KEY` 读取）
- **流程**：`POST /shopee/storeTokens` → `POST /shopee/developerProxy`
- **path**：须 `api/v2/returns/...`
- **标识**：店铺级 API，通常传 **`shopId`**
- **官方文档 URL 规则**：`https://open.shopee.com/documents/v2/v2.returns.{api}?module=102&type=1`
- **复杂 POST**（如 `dispute`、`offer`）：推荐传完整 `body` 对象

---

## Returns 模块总览

| # | API | Method | path | 脚本 | 官方文档 |
|---|-----|--------|------|------|----------|
| 1 | accept_offer | POST | `api/v2/returns/accept_offer` | `accept_offer.py` | [doc](https://open.shopee.com/documents/v2/v2.returns.accept_offer?module=102&type=1) |
| 2 | cancel_dispute | POST | `api/v2/returns/cancel_dispute` | `cancel_dispute.py` | [doc](https://open.shopee.com/documents/v2/v2.returns.cancel_dispute?module=102&type=1) |
| 3 | confirm | POST | `api/v2/returns/confirm` | `confirm.py` | [doc](https://open.shopee.com/documents/v2/v2.returns.confirm?module=102&type=1) |
| 4 | convert_image | POST | `api/v2/returns/convert_image` | `convert_image.py` | [doc](https://open.shopee.com/documents/v2/v2.returns.convert_image?module=102&type=1) |
| 5 | dispute | POST | `api/v2/returns/dispute` | `dispute.py` | [doc](https://open.shopee.com/documents/v2/v2.returns.dispute?module=102&type=1) |
| 6 | get_available_solutions | GET | `api/v2/returns/get_available_solutions` | `get_available_solutions.py` | [doc](https://open.shopee.com/documents/v2/v2.returns.get_available_solutions?module=102&type=1) |
| 7 | get_return_detail | GET | `api/v2/returns/get_return_detail` | `get_return_detail.py` | [doc](https://open.shopee.com/documents/v2/v2.returns.get_return_detail?module=102&type=1) |
| 8 | get_return_dispute_reason | GET | `api/v2/returns/get_return_dispute_reason` | `get_return_dispute_reason.py` | [doc](https://open.shopee.com/documents/v2/v2.returns.get_return_dispute_reason?module=102&type=1) |
| 9 | get_return_list | GET | `api/v2/returns/get_return_list` | `get_return_list.py` | [doc](https://open.shopee.com/documents/v2/v2.returns.get_return_list?module=102&type=1) |
| 10 | get_reverse_tracking_info | GET | `api/v2/returns/get_reverse_tracking_info` | `get_reverse_tracking_info.py` | [doc](https://open.shopee.com/documents/v2/v2.returns.get_reverse_tracking_info?module=102&type=1) |
| 11 | get_shipping_carrier | GET | `api/v2/returns/get_shipping_carrier` | `get_shipping_carrier.py` | [doc](https://open.shopee.com/documents/v2/v2.returns.get_shipping_carrier?module=102&type=1) |
| 12 | offer | POST | `api/v2/returns/offer` | `offer.py` | [doc](https://open.shopee.com/documents/v2/v2.returns.offer?module=102&type=1) |
| 13 | query_proof | GET | `api/v2/returns/query_proof` | `query_proof.py` | [doc](https://open.shopee.com/documents/v2/v2.returns.query_proof?module=102&type=1) |
| 14 | upload_proof | POST | `api/v2/returns/upload_proof` | `upload_proof.py` | [doc](https://open.shopee.com/documents/v2/v2.returns.upload_proof?module=102&type=1) |
| 15 | upload_shipping_proof | POST | `api/v2/returns/upload_shipping_proof` | `upload_shipping_proof.py` | [doc](https://open.shopee.com/documents/v2/v2.returns.upload_shipping_proof?module=102&type=1) |
通用入口：`returns_api.py`（JSON 含 `"api": "<上表 API 名>"`）。

---

## 常用接口说明

### 查询

| API | 要点 |
|-----|------|
| `get_return_list` | 退货/退款列表；可选 `page_no`、`page_size`、时间筛选 |
| `get_return_detail` | 必填 `return_sn` |
| `get_reverse_tracking_info` | 逆向物流轨迹 |

### 卖家处理

| API | 要点 |
|-----|------|
| `confirm` | 卖家确认退货；POST `body` 含 `return_sn` |
| `get_available_solutions` | 必填 `return_sn`；可用解决方案 |
| `offer` / `accept_offer` | 提出/接受解决方案 |
| `dispute` / `cancel_dispute` | 发起/取消争议 |

### 凭证与物流

| API | 要点 |
|-----|------|
| `upload_proof` / `query_proof` | 上传/查询退货凭证 |
| `convert_image` | 图片转换 |
| `get_shipping_carrier` | 退货物流承运商 |
| `upload_shipping_proof` | 上传退货运单凭证 |
| `get_return_dispute_reason` | 争议原因列表 |

---

## 网关错误码

| errcode | 含义 | 建议 |
|---------|------|------|
| 1002 | 参数/未登录 | 检查 shopId 与 API Key |
| 1003 | 代理/网络异常 | 重试 |
| 1004 | 无授权记录 | auth skill |
| 1005 | path 未白名单 | 确认 `api/v2/returns/...` |

---

## curl 示例

```bash
export KEY=$LINKFOXAGENT_API_KEY
BASE=https://tool-gateway.linkfox.com

curl -X POST $BASE/shopee/developerProxy -H "Authorization: $KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "path": "api/v2/returns/get_return_list",
    "method": "GET",
    "accessToken": "xxx",
    "shopId": "67890",
    "queryString": "page_no=1&page_size=20"
  }'
```

---

## Feedback API

```bash
curl -X POST https://skill-api.linkfox.com/api/v1/public/feedback \
  -H "Content-Type: application/json" \
  -d '{"skillName":"linkfox-shopee-store-returns","sentiment":"POSITIVE",
       "category":"OTHER","content":"退货列表查询正常"}'
```
