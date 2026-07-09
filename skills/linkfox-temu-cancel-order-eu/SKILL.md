---
name: linkfox-temu-cancel-order-eu
description: Temu 欧洲站取消订单 API（买家+卖家合一），经 LinkFox 网关转发 Partner EU：买家售后取消(bg.aftersales.cancel.*)、卖家申诉/缺货取消(temu.order.cancel.*)等。当用户提到 Temu EU 取消订单、欧洲站买家取消、卖家缺货取消、afterSalesStatusGroup、applySn、site=eu order-shipping 时触发。订单用 linkfox-temu-order-eu；美国站用 linkfox-temu-cancel-order-us；全球站用 linkfox-temu-cancel-order-global。
---

# Temu 欧洲站 — 取消订单（买家 + 卖家）

本 skill（`linkfox-temu-cancel-order-eu`）覆盖 Partner Platform for EU **取消订单**相关接口：

- **买家/消费者**：`bg.aftersales.cancel.list.get`、`bg.aftersales.cancel.agree`
- **店家/卖家**：`temu.order.cancel.appeal.apply`、`temu.order.cancel.appeal.result.get`、`temu.order.cancel.outofstock.apply`、`temu.order.cancel.outofstock.result.get`

详见 [partner-eu-catalog.md](./references/partner-eu-catalog.md)（**6** 个接口）。

**网关（本 skill 内置）**：

| 能力 | 方法 | 路径 |
|------|------|------|
| 取消单 OpenAPI（`eu_cancel_*`、`eu_seller_cancel_*`、`temu_eu_proxy`） | POST | `https://tool-gateway.linkfox.com/temu/proxy` |
| 加签文件下载 | POST | `https://tool-gateway.linkfox.com/temu/fileDownload` |

## 相关 skill

| 场景 | skill |
|------|--------|
| 订单列表/详情/发货/地址/金额 | `linkfox-temu-order-eu` |
| 美国站取消订单 | `linkfox-temu-cancel-order-us` |
| 全球站（非 US/EU）取消订单 | `linkfox-temu-cancel-order-global` |
| Self-Fulfilled Shipments | `linkfox-temu-fulfillment-eu`（`site=eu`） |
| 商品管理 | `linkfox-temu-manage-product-eu` |
| 退货与退款 | `linkfox-temu-returns-refunds-eu` |
| 网关与 Temu token | 本 skill `scripts/` |

## 调用方式

- **API 端点**：`POST /temu/proxy`（业务操作通过请求体中的 type 区分；完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/<脚本名>.py '<JSON 参数>' [--inline]`（可用脚本见上文脚本一览）
- **成本约束**：本工具会消耗积分；失败/空结果不得自动换关键词、翻页或连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-temu-cancel-order-eu-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
- 响应体 ≤ 8 KB：落盘后把完整 JSON 打印到 stdout
- 响应体 > 8 KB：落盘后 stdout 只输出摘要（顶层字段、常见计数如 `total`/`costToken`、最大列表字段的长度 + 前 3 条样本）
- 加 `--inline` 强制全量打印到 stdout（同样落盘）

**读数据建议**：先看摘要判断是否足够；需要具体字段时优先用 `jq`或`ConvertFrom-Json` 从保存的 json 文件按需抽取，避免整份 JSON 进入上下文。

## 默认参数

| 字段 | 默认 | 说明 |
|------|------|------|
| site | `eu` | Partner EU |
| managementType | `semi-managed` | 半托管 |
| tokenPurpose | `order-shipping` | 订单/取消场景 token |

## 鉴权

1. **LinkFox**：`LINKFOXAGENT_API_KEY` → Header `Authorization` + `Token`
2. **Temu**：`accessToken` 或 `storeKey`（建议 `tokenPurpose=order-shipping`）

## Scripts（按 type）

### 买家取消

| 脚本 | type |
|------|------|
| `eu_cancel_aftersales_cancel_list_get.py` | `bg.aftersales.cancel.list.get` |
| `eu_cancel_aftersales_cancel_agree.py` | `bg.aftersales.cancel.agree` |

### 卖家取消

| 脚本 | type |
|------|------|
| `eu_seller_cancel_order_cancel_appeal_apply.py` | `temu.order.cancel.appeal.apply` |
| `eu_seller_cancel_order_cancel_appeal_result_get.py` | `temu.order.cancel.appeal.result.get` |
| `eu_seller_cancel_order_cancel_outofstock_apply.py` | `temu.order.cancel.outofstock.apply` |
| `eu_seller_cancel_order_cancel_outofstock_result_get.py` | `temu.order.cancel.outofstock.result.get` |

### 通用

| 脚本 | 说明 |
|------|------|
| `temu_eu_proxy.py` | 任意 `type` |
| `temu_eu_file_download.py` | 加签文件下载 |

## 接入新接口（约定）

1. 新增 `references/apis/<type-slug>.md`
2. 新增 `scripts/eu_cancel_*` 或 `eu_seller_cancel_*`（调用 `_eu_cancel_order_script.run_cli`）
3. 更新 [partner-eu-catalog.md](./references/partner-eu-catalog.md)、[apis/README.md](./references/apis/README.md)

## 示例

```bash
export LINKFOXAGENT_API_KEY="<key>"

python scripts/eu_cancel_aftersales_cancel_list_get.py '{
  "accessToken": "TOKEN",
  "tokenPurpose": "order-shipping",
  "site": "eu",
  "request": { "pageNo": 1, "pageSize": 20, "afterSalesStatusGroup": 8 }
}'

python scripts/eu_seller_cancel_order_cancel_outofstock_apply.py '{
  "accessToken": "TOKEN",
  "tokenPurpose": "order-shipping",
  "site": "eu",
  "request": {
    "parentOrderSn": "PO-123456789",
    "orderSnList": ["O-111111111"]
  }
}'
```

**Feedback：** `skillName`：`linkfox-temu-cancel-order-eu`

## 网关与授权脚本

授权说明：[references/access-token.md](./references/access-token.md)

