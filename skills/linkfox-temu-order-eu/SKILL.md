---
name: linkfox-temu-order-eu
description: Temu 欧洲站订单管理 API，经 LinkFox 网关转发 Partner EU 订单接口：订单列表/详情/收货地址/金额/合并发货/定制/SN鉴真上传(bg.order.*、temu.local.order.verification.upload)等。当用户提到 Temu EU 订单、Temu欧洲站订单、上传SN、IMEI、verification upload、定制商品、合并发货、parentOrderSn、site=eu order-shipping 时触发。商品管理用 linkfox-temu-manage-product-eu；价格用 linkfox-temu-price-eu；履约/发货用 linkfox-temu-fulfillment-eu；退货退款用 linkfox-temu-returns-refunds-eu；取消用 linkfox-temu-cancel-order-eu。
---

# Temu 欧洲站订单管理 API（Manage Order）

本 skill（`linkfox-temu-order-eu`）覆盖 Partner Platform for EU **Order** 菜单（`menu_code=dbd3d395963a408984b8ae7dbc5f64f9`）下 **10** 个订单 `bg.order.*` / `temu.order.*` / `temu.local.order.*` 接口（`type` 与 US 对齐，默认 `site=eu`）。美国站请用 **`linkfox-temu-order-us`**；全球站（非 US/EU）请用 **`linkfox-temu-order-global`**。

详见 [partner-eu-catalog.md](./references/partner-eu-catalog.md)。

> 当前已接入 **10** 个接口；其余订单接口将按 Partner 文档逐条补充到 `references/apis/` 与 `eu_order_*.py`。

**网关（本 skill 内置）**：

| 能力 | 方法 | 路径 |
|------|------|------|
| 订单 OpenAPI（`eu_order_*`、`temu_eu_proxy`） | POST | `https://tool-gateway.linkfox.com/temu/proxy` |
| 加签文件下载 | POST | `https://tool-gateway.linkfox.com/temu/fileDownload` |

## 相关 skill

| 场景 | skill |
|------|--------|
| 商品列表/详情/编辑/库存/上下架 | `linkfox-temu-manage-product-eu` |
| 发品、类目、V2 add | `linkfox-temu-add-product-us` |
| 价格/供货价、定价单 | `linkfox-temu-price-eu` |
| 取消订单 | `linkfox-temu-cancel-order-eu` |
| 退货与退款 | `linkfox-temu-returns-refunds-eu` |
| 履约/发货（购标、合作仓、自发货、跟踪） | `linkfox-temu-fulfillment-eu` |
| 网关与 Temu token | 本 skill `scripts/` |

## 调用方式

- **API 端点**：`POST /temu/proxy`（不同操作通过请求体区分；完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/<脚本名>.py '<JSON 参数>' [--inline]`（可用脚本见上文脚本一览）
- **成本约束**：本工具会消耗积分；失败/空结果不得自动换关键词、翻页或连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/<skill-name>-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
- 响应体 ≤ 8 KB：落盘后把完整 JSON 打印到 stdout
- 响应体 > 8 KB：落盘后 stdout 只输出摘要（顶层字段、常见计数如 `total`/`costToken`、最大列表字段的长度 + 前 3 条样本）
- 加 `--inline` 强制全量打印到 stdout（同样落盘）

**读数据建议**：先看摘要判断是否足够；需要具体字段时优先用 `jq`或`ConvertFrom-Json` 从保存的 json 文件按需抽取，避免整份 JSON 进入上下文。


| 文档 | 内容 |
|------|------|
| [api.md](./references/api.md) | 网关、鉴权、错误码、扩展流程 |
| [partner-eu-catalog.md](./references/partner-eu-catalog.md) | 接口目录 + Partner URL + 脚本（随接入更新） |
| [apis/README.md](./references/apis/README.md) | **按接口分文件**（`apis/<type-slug>.md`） |

## 默认参数

| 字段 | 默认 | 说明 |
|------|------|------|
| site | `eu` | Partner EU |
| managementType | `semi-managed` | 半托管 |
| tokenPurpose | `order-shipping` | 订单/发货场景 token（见 [access-token.md](./references/access-token.md)） |

## 鉴权

1. **LinkFox**：`LINKFOXAGENT_API_KEY` → Header `Authorization` + `Token`
2. **Temu**：`accessToken` 或 `storeKey`（`storeKey` 时建议带 `tokenPurpose=order-shipping`）

## Scripts（按 type）

| 脚本 | type | 状态 |
|------|------|------|
| `eu_order_list_v2_get.py` | `bg.order.list.v2.get` | 已接入 |
| `eu_order_detail_v2_get.py` | `bg.order.detail.v2.get` | 已接入 |
| `eu_order_shippinginfo_v2_get.py` | `bg.order.shippinginfo.v2.get` | 已接入 |
| `eu_order_decryptshippinginfo_get.py` | `bg.order.decryptshippinginfo.get` | 已接入 |
| `eu_order_amount_query.py` | `bg.order.amount.query` | 已接入 |
| `eu_order_amount_v2_query.py` | `temu.order.amount.v2.query` | 已接入 |
| `eu_order_amount_v3_query.py` | `temu.order.amount.v3.query` | 已接入 |
| `eu_order_combinedshipment_list_get.py` | `bg.order.combinedshipment.list.get` | 已接入 |
| `eu_order_customization_get.py` | `bg.order.customization.get` | 已接入 |
| `eu_order_verification_upload.py` | `temu.local.order.verification.upload` | 已接入 |
| `temu_eu_proxy.py` | 任意 `type` | 通用 |
| `temu_eu_file_download.py` | 加签文件下载 | 通用 |

## 接入新接口（约定）

你每提供一条 Partner 文档（`type` + 参数表 + 可选 `sub_menu_code`），将：

1. 新增 `references/apis/<type-slug>.md`（完整入参/出参层级）
2. 新增 `scripts/eu_order_<slug>.py`（调用 `_eu_order_script.run_cli`）
3. 更新 [partner-eu-catalog.md](./references/partner-eu-catalog.md)、[apis/README.md](./references/apis/README.md) 与本表

## 示例

```bash
export LINKFOXAGENT_API_KEY="<key>"

# 订单列表 V2（待发货 parentOrderStatus=2）
python scripts/eu_order_list_v2_get.py '{
  "accessToken": "TOKEN",
  "tokenPurpose": "order-shipping",
  "request": {
    "pageNumber": 1,
    "pageSize": 20,
    "parentOrderStatus": 2
  }
}'

# 按父订单号查询（最多 20 个）
python scripts/eu_order_list_v2_get.py '{
  "accessToken": "TOKEN",
  "request": {
    "parentOrderSnList": ["PO-123456789"]
  }
}'

# 订单详情 V2（须 parentOrderSn）
python scripts/eu_order_detail_v2_get.py '{
  "accessToken": "TOKEN",
  "tokenPurpose": "order-shipping",
  "request": {
    "parentOrderSn": "PO-123456789"
  }
}'

# 收货地址 V2（传 parentOrderSn）
python scripts/eu_order_shippinginfo_v2_get.py '{
  "accessToken": "TOKEN",
  "tokenPurpose": "order-shipping",
  "request": {
    "parentOrderSn": "PO-123456789"
  }
}'

# 敏感收货地址解密（传 parentOrderSn）
python scripts/eu_order_decryptshippinginfo_get.py '{
  "accessToken": "TOKEN",
  "tokenPurpose": "order-shipping",
  "request": {
    "parentOrderSn": "PO-123456789"
  }
}'

# 订单金额/供货价（ERP 对账，传 parentOrderSn）
python scripts/eu_order_amount_query.py '{
  "accessToken": "TOKEN",
  "tokenPurpose": "order-shipping",
  "request": {
    "parentOrderSn": "PO-123456789"
  }
}'

# 可合并发货订单组（request 可为空对象）
python scripts/eu_order_combinedshipment_list_get.py '{
  "accessToken": "TOKEN",
  "tokenPurpose": "order-shipping",
  "request": {}
}'

# 定制商品内容（子订单号 orderSn，单次最多 10 个）
python scripts/eu_order_customization_get.py '{
  "accessToken": "TOKEN",
  "tokenPurpose": "order-shipping",
  "request": {
    "orderSnList": ["SO-123456789", "SO-987654321"]
  }
}'

# 上传 SN/IMEI 或二手鉴真（orderList[].orderSn）
python scripts/eu_order_verification_upload.py '{
  "accessToken": "TOKEN",
  "tokenPurpose": "order-shipping",
  "request": {
    "orderList": [
      {
        "orderSn": "SO-123456789",
        "verificationInfo": [
          {
            "serialNumber": "SN-001234567890",
            "imeiNumberList": ["352099001761481"]
          }
        ]
      }
    ]
  }
}'
```

**Feedback：** `skillName`：`linkfox-temu-order-eu`

## 网关与授权脚本

| 脚本 | 说明 |
|------|------|
| `check_linkfox_token.py` | 校验 LinkFox 用户 Token |
| `temu_token_guide.py` | Temu accessToken 后台授权步骤 |
| `save_temu_access_token.py` | 保存 accessToken 到本地 |
| `list_temu_access_tokens.py` | 列出已保存 token |
| `get_temu_access_token.py` | 读取已保存 token |
| `temu_proxy.py` | 通用网关转发（多 site） |
| `temu_file_download.py` | 加签文件下载（多 site） |

授权说明：[references/access-token.md](./references/access-token.md)

