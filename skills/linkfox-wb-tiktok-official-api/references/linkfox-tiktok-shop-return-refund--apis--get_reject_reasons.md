# Get Reject Reasons

## MCP 调用

| 项 | 固定值 |
|---|---|
| MCP server | `LinkFox` |
| 唯一工具 | `proxy_call` |
| `toolName` | `tiktokShop/developerProxy` |
| `arguments` | 直接使用本 reference 的请求对象；不得额外包裹 `body`、`data` 或另一层 `arguments` |
| 响应字段来源 | `skills/linkfox-tiktok-shop-return-refund/references/apis/get_reject_reasons.md`；只按其响应契约核对字段表 |

```json
{
  "toolName": "tiktokShop/developerProxy",
  "arguments": {"appType": "erp", "openId": "<openId>", "path": "return_refund/202309/reject_reasons", "method": "GET"}
}
```

- `toolName` 精确匹配且区分大小写；MCP 缺失时停止，禁止 HTTP fallback。
- WorkBuddy 自动注入 MCP Authorization；不得传 LinkFox `headers`、API Key、`token`、JWT 或手机号。
- 收费失败、空结果或结果不理想时不自动重试；相同 `toolName + arguments` 在同一任务内不重复调用。
- 先处理 MCP/schema/`isError`；text JSON 只解析一次；再检查下游错误字段和业务结果。

> 官方文档：https://partner.tiktokshop.com/docv2/page/get-reject-reasons-202309

## LinkFox 转发映射（本 skill）

| 项 | 值 |
|----|----|
| 具名 api | `get_reject_reasons` |
| 脚本 | `proxy_call` |
| 网关 | `POST tiktokShop/developerProxy` |
| appType | **`erp`（固定）** |
| 上游 path | `return_refund/202309/reject_reasons` |
| method | `GET` |
| shop_cipher | 是 |
| 令牌 | 网关按 `openId` + `appType=erp` 从库取 token（401/过期自动刷新并重试一次） |

### developerProxy 示例

```json
{
  "appType": "erp",
  "openId": "7010...",
  "path": "return_refund/202309/reject_reasons",
  "method": "GET",
  "queryString": "shop_cipher=GCP_...&return_or_cancel_id=4035633471902223141"
}
```

### 脚本示例

> 旧 HTTP/脚本示例已移除；使用本页 `MCP 调用` 的完整 `proxy_call` 参数结构。

---

## 官方接口原文（整理）

# Path: /return_refund/202309/reject_reasons
# Method: [GET]
# Function Description
Retrieve the list of valid reject reasons for a return or cancellation request. Call this before rejecting a return/cancellation so the seller can pick an allowed reason.

# Common Parameters
| Properties | Location | Type | Require | Sample | Properties description |
| --- | --- | --- | --- | --- | --- |
| shop_cipher | query | string | Y | GCP_... | Shop cipher from Get Authorized Shops |
| content-type | header | string | Y | application/json | Allowed type: application/json |

# Request Query Parameters
| Properties | Type | Require | Sample | Properties description |
| --- | --- | --- | --- | --- |
| return_or_cancel_id | string | Y | 4035633471902223141 | Unique ID of the return or cancellation request |
| locale | string | N | en-US | Locale for localized reason text |

> `app_key` / `sign` / `timestamp` 由紫鸟注入，调用方不要传。

# Request Sample
```Plain Text
https://open-api.tiktokglobalshop.com/return_refund/202309/reject_reasons?shop_cipher=ROW_...&return_or_cancel_id=4035633471902223141&app_key=...&timestamp=...&sign=...
```

# Response Parameters
| Properties | Type | Sample | Properties description |
| --- | --- | --- | --- |
| code | int | 0 | Status code |
| message | string | Success | Message |
| request_id | string | ... | Request id |
| data | object |  | Payload |
| ^reject_reasons | []object |  | Available reject reasons |
| ^^name / reason_code | string | PRODUCT_DAMAGED | Reason key/code |
| ^^text / reason_description | string | Product is damaged | Localized description |

# Response Sample
```json
{
  "code": 0,
  "data": {
    "reject_reasons": [
      {
        "name": "PRODUCT_DAMAGED",
        "text": "Product is damaged"
      },
      {
        "name": "INSUFFICIENT_EVIDENCE",
        "text": "Evidence provided is insufficient"
      }
    ]
  },
  "message": "Success",
  "request_id": "202407021210000112233445566AABB"
}
```

## Agent 注意事项

1. 必须先有 `return_or_cancel_id`（来自售后列表/详情；后续可扩 search returns）。
2. 展示时列出 `name`/`text`（或 `reason_code`/`reason_description`，以线上响应为准）。
3. 真正拒绝退货/取消走 Reject Return / Reject Cancellation（可后续纳入本 skill）。
