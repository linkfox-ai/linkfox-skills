# 1688采购流程 API 参考

本文记录 `linkfox-1688-procurement` 的 tool-gateway 调用规范、脚本入口、风险等级和关键字段。具体入参以网关当前 MCP schema 为准。

## 调用规范

- 请求地址：`${LINKFOX_TOOL_GATEWAY}<path>`，默认网关为 `https://tool-gateway.linkfox.com`
- 请求方式：`POST`
- Content-Type：`application/json; charset=utf-8`
- 认证方式：Header `Authorization: <api_key>`
- API key 读取顺序：`LINKFOX_AGENT_API_KEY`，然后 `LINKFOXAGENT_API_KEY`（如未配置 按 SKILL.md 的 **## 解决认证和积分问题** 处理）
- User-Agent：`LinkFox-Skill/2.0`
- 透传 Header：`SESSION_ID`、`MODE_ID`、`APP_NAME`
- 超时：120s
- 输出保存：小响应默认不落盘；大响应、`--save` 或 `LINKFOX_SKILL_SAVE_RESPONSE=1` 时保存脱敏完整响应；`--no-save` 或 `LINKFOX_SKILL_NO_SAVE=1` 可禁止保存
- 缓存策略：不做 24h 响应缓存。授权、价格、库存、订单状态和物流以实时返回为准，高风险写操作不得缓存或自动重放。

Windows 推荐使用 `--payload-env` 或 `--payload-file`，避免 shell 转义破坏 JSON。

```powershell
$env:PAYLOAD = "{}"
python scripts/authorized_stores.py --payload-env PAYLOAD --inline
```

## 授权规则

`authorizedStores` 是当前 LinkFox 用户的 1688 OAuth 授权检查入口。它依赖 API key 中的 LinkFox 用户身份，后端应只返回当前用户的授权店铺。

脚本层规则：

- `authorizeUrl` 不做 1688 OAuth 前置检查，因为它用于发起授权。
- `authorizedStores` 不做 1688 OAuth 前置检查，因为它本身就是检查入口。
- 其他采购操作在调用目标 endpoint 前，脚本会先调用 `authorizedStores`。
- 没有 `status=ACTIVE` 且 `expired=false` 的店铺时，脚本返回 `authorization_required`，不会调用目标 endpoint。

这层检查不能替代后端鉴权；后端仍必须按 `Token.uid` 或等价用户身份过滤和校验授权。

## MCP 与 Skill 暴露关系

MCP 工具启停和 Skill HTTP 调用是两层能力：

| 层级 | 控制内容 | 对本 Skill 的影响 |
|---|---|---|
| MCP tool enabled | 是否出现在 MCP 工具列表或 Agent 工具调用面 | 不决定脚本是否能 HTTP 调用 |
| Gateway route enabled | tool-gateway 是否转发对应 HTTP path | 决定脚本是否可用 |
| Backend capability enabled | ecom-plat 是否处理业务 | 决定最终业务是否可用 |

因此，MCP 停用但 gateway route 仍启用时，Skill 脚本可以继续使用。若要完全停用某能力，应关闭 gateway route 或后端能力。

## 禁止作为 Skill 能力的端点

以下是授权闭环或 MyERP/ecom-plat 后端回调路径，不是 MCP 工具，不应写成 Skill 脚本：

- `/alibaba1688/proxy/callback`
- `/alibaba1688/authorizeCallback`
- `/alibaba1688/oauth/callback`

## API 与脚本一览

| 能力 | MCP tool | Path | Script | 风险 | OAuth 前置检查 | 确认字段 |
|---|---|---|---|---|---|---|
| 生成授权链接 | `_alibaba1688_authorizeUrl` | `/alibaba1688/authorizeUrl` | `authorize_url.py` | 低 | 否 | - |
| 查询已授权账号 | `_alibaba1688_authorizedStores` | `/alibaba1688/authorizedStores` | `authorized_stores.py` | 低 | 否 | - |
| 查询收货地址 | `_alibaba1688_receiveAddressList` | `/alibaba1688/receiveAddressList` | `receive_address_list.py` | 低 | 是 | - |
| 查询 SKU | `_alibaba1688_sku` | `/alibaba1688/sku` | `sku.py` | 低 | 是 | - |
| 下单预览 | `_alibaba1688_orderPreview` | `/alibaba1688/orderPreview` | `order_preview.py` | 中 | 是 | - |
| 创建订单 | `_alibaba1688_createOrder` | `/alibaba1688/createOrder` | `create_order.py` | 高 | 是 | `confirmCreateOrder=true` |
| 获取支付链接 | `_alibaba1688_paymentUrl` | `/alibaba1688/paymentUrl` | `payment_url.py` | 高 | 是 | `confirmGetPaymentUrl=true` |
| 查询订单状态 | `_alibaba1688_orderStatus` | `/alibaba1688/orderStatus` | `order_status.py` | 低 | 是 | - |
| 查询物流 | `_alibaba1688_logistics` | `/alibaba1688/logistics` | `logistics.py` | 低 | 是 | - |
| 查询物流轨迹 | `_alibaba1688_logisticsTrace` | `/alibaba1688/logisticsTrace` | `logistics_trace.py` | 低 | 是 | - |
| 确认收货 | `_alibaba1688_confirmReceive` | `/alibaba1688/confirmReceive` | `confirm_receive.py` | 高 | 是 | `confirmReceive=true` |
| 取消订单 | `_alibaba1688_cancelOrder` | `/alibaba1688/cancelOrder` | `cancel_order.py` | 高 | 是 | `confirmCancel=true` |

`_alibaba1688_imageSearch` 由 `linkfox-1688-search-by-image` 独立承担，本 Skill 不包含图搜脚本。

## 入参要点

| 能力 | 关键字段说明 |
|---|---|
| `authorizeUrl` | 按 schema 传授权展示字段；如需账号标签，优先使用 `accountName` |
| `authorizedStores` | 通常无需业务参数；用户身份来自 LinkFox API key |
| `receiveAddressList` | 依赖当前用户 ACTIVE 1688 授权 |
| `sku` | 通常需要 `offerId` |
| `orderPreview` | 通常需要 `offerId`、SKU/规格、数量、收货地址等下单参数 |
| `createOrder` | 下单参数与预览保持一致，并必须加 `confirmCreateOrder=true` |
| `paymentUrl` | 通常需要订单号，并必须加 `confirmGetPaymentUrl=true` |
| `orderStatus` | 通常需要订单号 |
| `logistics` | 通常需要订单号 |
| `logisticsTrace` | 通常需要订单号及物流标识，以 schema 为准 |
| `confirmReceive` | 订单号 + `confirmReceive=true` |
| `cancelOrder` | 订单号、取消原因（如 schema 要求）+ `confirmCancel=true` |

## 高风险校验

用户侧只需要用中文自然语言做单独明确确认，例如“确认创建这个订单”“确认获取这个订单的支付链接”“确认取消这个订单”“确认收货”。不要要求用户输入英文参数名或 `=true`。

Agent 在收到中文确认后，调用脚本时必须自动加入对应 JSON boolean 安全字段。高风险脚本会在本地先校验确认字段，确认字段不满足时不会联网：

| 脚本 | 本地拒绝条件 |
|---|---|
| `create_order.py` | 缺少 JSON boolean `confirmCreateOrder=true` |
| `payment_url.py` | 缺少 JSON boolean `confirmGetPaymentUrl=true` |
| `confirm_receive.py` | 缺少 JSON boolean `confirmReceive=true` |
| `cancel_order.py` | 缺少 JSON boolean `confirmCancel=true` |

字符串 `"true"`、数字 `1`、大小写变体都不算确认。

## 响应与错误处理

- HTTP 401 或 authorized error：按 SKILL.md 的 **## 解决认证和积分问题** 处理。
- HTTP 402：按 SKILL.md 的 **## 解决认证和积分问题** 处理。
- `authorization_required`：没有当前用户 ACTIVE 1688 OAuth 授权；先运行 `authorize_url.py`，用户授权后再运行 `authorized_stores.py` 验证。
- 下单预览失败：停止，不要进入创建订单；向用户说明失败原因并重新确认参数。
- 高风险写操作失败：不要自动重试，避免重复下单、重复取消或重复确认收货。

## 敏感信息规则

脚本会对常见敏感字段做脱敏落盘。Agent 展示结果时仍需避免暴露：

- LinkFox API key / JWT
- 1688 access token / refresh token
- Authorization header
- OAuth callback `code`
- app secret / session key / refresh secret

## Feedback API

此端点独立于 tool-gateway，不要混用 base URL。

- POST `https://skill-api.linkfox.com/api/v1/public/feedback`
- Content-Type：`application/json`

```json
{
  "skillName": "linkfox-1688-procurement",
  "sentiment": "NEUTRAL",
  "category": "SUGGESTION",
  "content": "Describe what did not match the user's intent or actual gateway behavior."
}
```
