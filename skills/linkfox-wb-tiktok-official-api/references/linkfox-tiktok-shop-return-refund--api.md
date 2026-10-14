# TikTok Shop ERP Return & Refund API Reference

## MCP 调用

| 项 | 固定值 |
|---|---|
| MCP server | `LinkFox` |
| 唯一工具 | `proxy_call` |
| `toolName` | `tiktokShop/developerProxy` |
| `arguments` | 直接使用本 reference 的请求对象；不得额外包裹 `body`、`data` 或另一层 `arguments` |
| 响应字段来源 | `skills/linkfox-tiktok-shop-return-refund/references/api.md`；只按其响应契约核对字段表 |

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

> ⚠️ 依赖 **`linkfox-tiktok-shop-auth`**（`appType=erp`）。
> 官方入口：[Get Reject Reasons](https://partner.tiktokshop.com/docv2/page/get-reject-reasons-202309)。

## 转发约定

- 入口：`POST tiktokShop/developerProxy`，固定 `appType=erp`，传 `openId`（token 后台化；401 自动刷新）。
- path 白名单：`authorization/`、`return_refund/`
- `ttsAccessToken` 已废弃忽略。

## 接口索引

| api | Method | path | shop_cipher | 参考 | 官方 |
|-----|--------|------|-------------|------|------|
| `get_authorized_shops` | GET | `authorization/202309/shops` | 否 | [doc](linkfox-tiktok-shop-return-refund--apis--get_authorized_shops.md) | [link](https://partner.tiktokshop.com/docv2/page/get-authorized-shops-202309) |
| `get_reject_reasons` | GET | `return_refund/202309/reject_reasons` | 是 | [doc](linkfox-tiktok-shop-return-refund--apis--get_reject_reasons.md) | [link](https://partner.tiktokshop.com/docv2/page/get-reject-reasons-202309) |

> 旧 HTTP/脚本示例已移除；使用本页 `MCP 调用` 的完整 `proxy_call` 参数结构。

## Notes

1. `return_or_cancel_id` 为 Query 必填。
2. 勿输出完整 ERP token。
