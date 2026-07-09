---
name: linkfox-shopee-store-first-mile
description: Shopee（虾皮）头程物流 FirstMile（与 linkfox-shopee-store-auth 同系列），经 /shopee/developerProxy 转发 Shopee Open API FirstMile 模块全部 16 个接口：get_unbind_order_list、generate_first_mile_tracking_number、bind_first_mile_tracking_number、get_waybill、get_channel_list 等。当用户提到 Shopee 头程、FirstMile、头程运单、绑定头程、first mile tracking、中转仓、get_unbind_order_list 时触发。即使未明确提及"头程"，只要涉及已授权 Shopee 店铺的头程运单绑定或面单，也应触发。
---

# Shopee 头程 FirstMile

Shopee Open Platform **FirstMile 模块**（16 个 API）。**依赖 `linkfox-shopee-store-auth`**：先取 `accessToken`，再经 **`POST /shopee/developerProxy`** 转发（`path` 须 `api/v2/first_mile/...`）。

## 调用方式

- **API 端点**：`POST /shopee/developerProxy`（不同操作通过请求体区分；完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/first_mile_api.py '{"api": "get_unbind_order_list", ...}' [--inline]`（可用脚本见上文脚本一览）
- **成本约束**：本工具会消耗积分；失败/空结果不得自动换关键词、翻页或连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/<skill-name>-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
- 响应体 ≤ 8 KB：落盘后把完整 JSON 打印到 stdout
- 响应体 > 8 KB：落盘后 stdout 只输出摘要（顶层字段、常见计数如 `total`/`costToken`、最大列表字段的长度 + 前 3 条样本）
- 加 `--inline` 强制全量打印到 stdout（同样落盘）

**读数据建议**：先看摘要判断是否足够；需要具体字段时优先用 `jq`或`ConvertFrom-Json` 从保存的 json 文件按需抽取，避免整份 JSON 进入上下文。

## 官方参考

FirstMile 模块索引：[v2.first_mile.get_unbind_order_list](https://open.shopee.com/documents/v2/v2.first_mile.get_unbind_order_list?module=96&type=1)

---

## Prerequisites

1. 运行 `python scripts/check_auth_dependency.py`；exit code **42** → 先安装 **`linkfox-shopee-store-auth`**。
2. **头程 vs 正向物流**：本 skill 为跨境**头程**（First Mile）；店铺发货/面单见 `linkfox-shopee-store-logistics`。

## 可用脚本（16 个 API）

| 分组 | 脚本 |
|------|------|
| 绑定/解绑 | `get_unbind_order_list.py`、`generate_first_mile_tracking_number.py`、`bind_first_mile_tracking_number.py`、`generate_and_bind_first_mile_tracking_number.py`、`unbind_first_mile_tracking_number.py` |
| 运单/面单 | `get_tracking_number_list.py`、`get_waybill.py`、`get_detail.py` |
| 渠道/仓库 | `get_channel_list.py`、`get_transit_warehouse_list.py`、`get_courier_delivery_channel_list.py` |
| 快递头程 | `bind_courier_delivery_first_mile_tracking_number.py`、`get_courier_delivery_detail.py`、`get_courier_delivery_waybill.py` 等 |
| 通用入口 | `first_mile_api.py` |

完整列表见 `references/api.md`。

## Usage Scenarios

### 1. 绑定头程运单
1. `get_unbind_order_list.py` 查未绑定订单
2. `generate_and_bind_first_mile_tracking_number.py` 或分步 generate + bind
3. `get_waybill.py` 获取面单

## Not Applicable

- 店铺授权 → `linkfox-shopee-store-auth`
- 正向物流发货 → `linkfox-shopee-store-logistics`
- SBS 仓储库存 → `linkfox-shopee-store-sbs`
- 订单查询 → `linkfox-shopee-store-orders`

**Feedback:** 见 `references/api.md`。

---
*For more high-quality, professional cross-border e-commerce skills, visit [LinkFox Skills](https://skill.linkfox.com/).*
