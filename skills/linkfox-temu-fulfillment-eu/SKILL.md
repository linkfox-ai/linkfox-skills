---
name: linkfox-temu-fulfillment-eu
description: Temu 欧洲站电商履行/发货 API（合一）：Buy-Shipping购标面单、合作仓履约、卖家自发货、物流跟踪、自配送POD上传与审核等30个接口。当用户提到 Temu EU 发货、购标、POD、proof of delivery、self delivery pod、合作仓、自发货、tracking、order-shipping 时触发。订单用 linkfox-temu-order-eu。
---

# Temu 欧洲站 — 电商履行 / 发货（Fulfillment）

本 skill（`linkfox-temu-fulfillment-eu`）合并原 **Buy-Shipping**、**Co-Warehouse**、**Self-Fulfilled Shipments**、**Tracking** 四个 skill，覆盖 Partner EU **Fulfillment** 域 **30** 个已接入 `type`。

| 域 | 脚本前缀 | 接口数 |
|----|----------|--------|
| Buy-Shipping | `eu_buy_shipping_*` | 17 |
| Co-Warehouse | `eu_co_warehouse_*` | 4 |
| Self-Fulfilled | `eu_self_fulfilled_*` | 5 |
| Tracking | `eu_tracking_*` | 1 |
| Self-Delivery POD | `eu_self_fulfilled_*pod*` | 3 |

详见 [partner-eu-catalog.md](./references/partner-eu-catalog.md)。

**网关**：

| 能力 | 方法 | 路径 |
|------|------|------|
| 履约 OpenAPI | POST | `https://tool-gateway.linkfox.com/temu/proxy` |
| 加签文件下载 | POST | `https://tool-gateway.linkfox.com/temu/fileDownload` |

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

## 相关 skill

| 场景 | skill |
|------|--------|
| 订单列表/详情/地址 | `linkfox-temu-order-eu` |
| 取消订单 | `linkfox-temu-cancel-order-eu` |
| 商品管理 | `linkfox-temu-manage-product-eu` |
| 退货退款 | `linkfox-temu-returns-refunds-eu` |
| 美国站履约/发货 | `linkfox-temu-fulfillment-us` |
| 全球站履约 | `linkfox-temu-fulfillment-global`（无 Scan Form） |

## 默认参数

| 字段 | 默认 |
|------|------|
| site | `eu` |
| managementType | `semi-managed` |
| tokenPurpose | `order-shipping` |

## Scripts（按域）

### Buy-Shipping（`eu_buy_shipping_*`）

购标、面单、Scan Form、上门揽收等 — 见 [apis/README.md](./references/apis/README.md#buy-shipping购标面单scan-form)。

### Co-Warehouse（`eu_co_warehouse_*`）

`bg.cooperativewarehouse.*` — 合作仓授权、提交/取消履约。

### Self-Fulfilled（`eu_self_fulfilled_*`）

`bg.logistics.shipment.v2.*`、`shippingtype.update` 等 — 卖家自带运单号。

### Tracking（`eu_tracking_*`）

`temu.track.trackinginfo.get`

### Self-Delivery POD（`eu_self_fulfilled_*pod*`）

- `temu.logistics.self.delivery.pod.upload.signature.query`
- `temu.logistics.self.delivery.pod.upload`
- `temu.logistics.self.delivery.pod.audit.result.get`

### 通用

| 脚本 | 说明 |
|------|------|
| `temu_eu_proxy.py` | 任意 `type` |
| `temu_eu_file_download.py` | 加签文件下载 |

薄封装统一调用 **`_eu_fulfillment_script.run_cli`**。

## 示例

```bash
export LINKFOXAGENT_API_KEY="<key>"

# Buy-Shipping 购标
python scripts/eu_buy_shipping_logistics_shipment_create.py '{
  "accessToken": "TOKEN",
  "tokenPurpose": "order-shipping",
  "request": { }
}'

# 卖家自发货更新跟踪号
python scripts/eu_self_fulfilled_logistics_shipment_shippingtype_update.py '{
  "accessToken": "TOKEN",
  "request": { "editPackageRequestList": [{ "packageSn": "PKG-1", "trackingNumber": "1Z..." }] }
}'
```

## 积分消耗规则

不消耗积分。

**Feedback：** `skillName`：`linkfox-temu-fulfillment-eu`

