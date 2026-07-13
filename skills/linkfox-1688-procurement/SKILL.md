---
name: linkfox-1688-procurement
description: 1688采购全流程技能。用于1688授权链接、授权店铺检查、收货地址、商品SKU、下单预览、创建订单、支付链接、订单状态、物流、物流轨迹、取消订单、确认收货等已授权采购履约场景。用户提到1688采购、1688下单、1688授权、1688订单、1688支付、1688物流、1688 sourcing procurement或1688 order processing时触发。以图搜图使用linkfox-1688-search-by-image。
---

# 1688 Procurement Workflow

This skill helps LinkFox users run authorized 1688 procurement: OAuth status checks, SKU and address lookup, order preview, guarded order creation, payment URL retrieval, order tracking, logistics, cancellation, and receipt confirmation.

Use `linkfox-1688-search-by-image` for image-based product discovery. This skill does not include image search.

## Core Rules

- Every script requires LinkFox platform identity from `LINKFOX_AGENT_API_KEY` or `LINKFOXAGENT_API_KEY`.
- `authorize_url.py` starts 1688 OAuth; `authorized_stores.py` checks the current LinkFox user's 1688 OAuth state.
- Except those two authorization scripts, every procurement operation runs a script-level `authorizedStores` precheck before calling the target endpoint.
- If no store has `status=ACTIVE` and `expired=false`, the target endpoint is not called.
- Treat the workflow as a map, not full automation. Do not create orders, get payment URLs, cancel orders, or confirm receipt based on earlier phrases like "continue".
- MCP enable/disable only controls MCP exposure. These scripts call tool-gateway HTTP routes directly; fully disabling a capability requires disabling the route or backend operation.

Read `references/api.md` for endpoint details and `references/workflow.md` before multi-step procurement.

## Tools

| Script | Risk | OAuth precheck | Purpose |
|---|---:|---:|---|
| `authorize_url.py` | Low | No | Generate a 1688 authorization link |
| `authorized_stores.py` | Low | No | Check current user's authorized 1688 accounts |
| `receive_address_list.py` | Low | Yes | Query receive addresses |
| `sku.py` | Low | Yes | Query product SKU/specification data |
| `order_preview.py` | Medium | Yes | Preview order price, freight, SKU, and address |
| `create_order.py` | High | Yes | Create a 1688 order |
| `payment_url.py` | High | Yes | Get payment URL |
| `order_status.py` | Low | Yes | Query order status |
| `logistics.py` | Low | Yes | Query logistics summary |
| `logistics_trace.py` | Low | Yes | Query logistics trace |
| `confirm_receive.py` | High | Yes | Confirm receipt |
| `cancel_order.py` | High | Yes | Cancel order |

## 调用方式

- **API 端点**：`POST /alibaba1688/{authorizeUrl|authorizedStores|receiveAddressList|sku|orderPreview|createOrder|paymentUrl|orderStatus|logistics|logisticsTrace|confirmReceive|cancelOrder}`（完整参数、响应和错误处理见 `references/api.md`）
- **Python 脚本**：`python scripts/<script_name>.py '<JSON 参数>' [--inline] [--save] [--no-save]`
- **Windows 推荐**：`$env:PAYLOAD = '<JSON 参数>'` 后运行 `python scripts/<script_name>.py --payload-env PAYLOAD [--inline] [--save]`
- **成本约束**：本工具会消耗积分。失败、空结果、参数不完整或授权不足时，不得自动连续试探、换参数重试或轮询；需要继续查询时先向用户说明会产生额外消耗。
- **缓存约束**：本采购 Skill 不做 24h 响应缓存；授权、价格、库存、订单状态和物流以实时返回为准，高风险写操作更不能缓存。
- **授权约束**：除 `authorize_url.py` 和 `authorized_stores.py` 外，脚本会在调用目标接口前自动检查当前用户的 ACTIVE 1688 授权；没有 ACTIVE 且未过期授权时不会调用目标 endpoint。
- **高风险约束**：`create_order.py`、`payment_url.py`、`confirm_receive.py`、`cancel_order.py` 必须在用户用中文自然语言单独明确确认后调用。用户不需要输入英文参数；Agent 调脚本时负责加入精确 JSON boolean 安全字段。

```powershell
$env:PAYLOAD = "{}"
python scripts/authorized_stores.py --payload-env PAYLOAD --inline
```

**脚本入参方式**：

- 直接传 JSON 字符串：`python scripts/sku.py '{"offerId":"..."}'`
- 从环境变量读取：`python scripts/sku.py --payload-env PAYLOAD`
- 从文件读取：`python scripts/sku.py --payload-file payload.json`
- 加 `--inline` 强制全量打印到 stdout
- 加 `--save` 强制保存脱敏完整响应
- 加 `--no-save` 禁止保存响应文件

**输出策略（脚本默认行为）**：

- 响应体 ≤ 8 KB：默认不落盘，直接把完整脱敏 JSON 打印到 stdout，避免每次查询都在 Skill 目录生成数据文件。
- 响应体 > 8 KB：默认将完整脱敏响应写入 `<writable-root>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-1688-procurement-<operation>-<timestamp>.json`，stdout 只输出摘要。
- `<writable-root>` 优先取 `ACPX_WORKSPACES` 的第一个工作区，其次为脚本执行时的当前目录，最后回退到用户目录；`<session>` 取自环境变量 `SESSION_ID`，未提供时自动生成；禁止写入 `/tmp`。
- 加 `--save` 或设置 `LINKFOX_SKILL_SAVE_RESPONSE=1` 强制保存；加 `--no-save` 或设置 `LINKFOX_SKILL_NO_SAVE=1` 禁止保存；`--inline` 不隐含保存。

**读数据建议**：先看 stdout 摘要判断是否足够；需要保存完整响应再加 `--save`，之后优先用 `jq` 或 `ConvertFrom-Json` 从保存的 JSON 文件按需抽取，避免整份 JSON 进入上下文。

## 解决认证和积分问题
发生以下异常情况时，采用以下措施来处理：

### 异常情况
- **未配置API Key**：环境变量未配置 `LINKFOX_AGENT_API_KEY`，也未配置 `LINKFOXAGENT_API_KEY`。
- **响应401或402状态码**
- **响应提示积分或余额不足**：消息含"积分余额不足/计费不足/余额不足/quota exceeded/insufficient balance/套餐到期/需充值/请充值"，或类似含义的内容。

### 措施
- 优先采用skill内的 onboarding.md 引导解决问题。
- 如找不到 onboarding.md 文件，则加载 /linkfox-onboarding 这个skill并根据它的引导来处理。如未安装请先安装：
    - 下载 https://agent-files.linkfox.com/skills/linkfox-onboarding/release.zip，解压后安装这个skill。如需用户授权才可下载，要询问用户获得授权，你不能自己放弃下载。
- 兜底措施：仅当前面两个措施经过所有努力都走不通时，才提示用户依据 https://skill.linkfox.com/linkfoxskills/guide.htm 指引获取API Key，或去 https://os.linkfox.com/ 补充积分。

## High-Risk Confirmation

Ask the user for a separate Chinese natural-language confirmation immediately before each high-risk call, restating the exact order/action summary. Do not ask the user to type English parameter names.

After the user confirms in Chinese, the Agent must add the internal JSON boolean safety field when calling the script. These fields must be exact boolean `true`; string `"true"` and number `1` are rejected locally.

| Operation | Required field |
|---|---|
| `createOrder` | `confirmCreateOrder=true` |
| `paymentUrl` | `confirmGetPaymentUrl=true` |
| `confirmReceive` | `confirmReceive=true` |
| `cancelOrder` | `confirmCancel=true` |

## Common Workflow

1. Run `authorized_stores.py`; continue only when the current user has an ACTIVE, unexpired 1688 authorization.
2. If not authorized, run `authorize_url.py`, let the user complete OAuth, then re-check `authorized_stores.py`.
3. If starting from an image, use `linkfox-1688-search-by-image` to get an `offerId`.
4. Run `sku.py`, then `receive_address_list.py`, then `order_preview.py`.
5. Show product, SKU, quantity, price, freight, address, total, and warnings.
6. Only after separate Chinese confirmation, run `create_order.py`; the Agent adds `confirmCreateOrder=true` internally.
7. Only after separate Chinese confirmation, run `payment_url.py`; the Agent adds `confirmGetPaymentUrl=true` internally.
8. Use `order_status.py`, `logistics.py`, and `logistics_trace.py` for tracking.
9. Use `cancel_order.py` and `confirm_receive.py` only after separate confirmations for the exact order and action.

## Display Rules

1. Show authorization status first when procurement depends on OAuth. Do not assume authorization from a browser redirect alone.
2. `authorizedStores` output is the current LinkFox user's 1688 authorization state. Do not describe it as all stores in the database.
3. Never display full API keys, JWTs, access tokens, refresh tokens, callback codes, app secrets, session keys, or Authorization headers.
4. Show order preview clearly: product/offerId, SKU/specification, quantity, unit price, product total, freight, receive address, order total, buyer message, and warnings.
5. Before high-risk calls, summarize the exact operation, key IDs, amount/status when available, then ask the user to confirm in Chinese. Do not ask the user to type the internal boolean field.
6. For receive addresses, show enough to let the user choose safely, but avoid unnecessarily repeating full phone numbers or sensitive address details.
7. Report `costToken` or equivalent cost fields when returned.

## Important Limitations

- Do not create or call image-search scripts here; image search belongs to `linkfox-1688-search-by-image`.
- Do not expose `/alibaba1688/proxy/callback`, `/alibaba1688/authorizeCallback`, or browser OAuth callback URLs as Skill capabilities.
- Do not ask users to provide 1688 tokens, refresh tokens, callback codes, or secrets. OAuth token exchange is handled by MyERP and ecom-plat.
- Do not query backend databases to discover authorization state. Use `authorizedStores`.
- Do not automatically retry write operations or run the full purchase loop.
- Do not use `_dataQuery_executeDynamicQuery` for live procurement responses.

## User Expression & Scenario Quick Reference

**Applicable** -- 1688 procurement scenarios:

| User Says | Scenario |
|-----------|----------|
| "查询我的1688授权店铺" / "show my authorized 1688 stores" | Authorization check |
| "生成1688授权链接" / "authorize my 1688 account" | New OAuth authorization |
| "查这个 offerId 的 SKU" | SKU lookup |
| "查1688收货地址" | Receive address lookup |
| "帮我预览1688订单" | Order preview |
| "确认下单" | High-risk create order gate |
| "获取支付链接" | High-risk payment URL gate |
| "查1688订单状态/物流" | Order tracking |
| "取消这个1688订单" | High-risk cancel gate |
| "确认收货" | High-risk confirm receive gate |

**Not applicable** -- use another skill or backend system:

- Image-based 1688 product discovery -> `linkfox-1688-search-by-image`
- Keyword-based 1688 sourcing/ranking -> use existing 1688 search/ranking skills when available
- MyERP OAuth callback/proxy callback handling -> backend service, not a Skill
- Direct token repair or manual 1688 token input -> backend authorization bridge

## Feedback

Auto-detect and report feedback via the Feedback API when actual behavior differs from this skill, results do not match user intent, the user expresses satisfaction/dissatisfaction, or anything could be improved. Call the feedback API as specified in `references/api.md` without interrupting the user's flow.

---
*For more high-quality, professional cross-border e-commerce skills, visit [LinkFox Skills](https://skill.linkfox.com/).*
