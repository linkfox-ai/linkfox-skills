---
name: linkfox-shopee-store-fbs
description: Shopee（虾皮）FBS 巴西仓储（与 linkfox-shopee-store-auth 同系列），经 /shopee/developerProxy 转发 Shopee Open API FBS 模块全部 4 个接口：query_br_shop_enrollment_status、query_br_shop_invoice_error、query_br_shop_block_status、query_br_sku_block_status。当用户提到 Shopee FBS、巴西FBS、店铺入驻状态、发票错误、封禁状态、query_br_shop_enrollment_status 时触发。即使未明确提及"FBS"，只要涉及已授权 Shopee 巴西店铺的 FBS 入驻/封禁/发票状态查询，也应触发。
---

# Shopee FBS 巴西仓储

Shopee Open Platform **FBS 模块**（4 个 API，均为 GET，面向巴西 BR）。**依赖 `linkfox-shopee-store-auth`**：先取 `accessToken`，再经 **`POST /shopee/developerProxy`** 转发（`path` 须 `api/v2/fbs/...`）。

## 调用方式

- **API 端点**：`POST /shopee/developerProxy`（不同操作通过请求体区分；完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/<脚本名>.py '<JSON 参数>' [--inline]`（可用脚本见上文脚本一览）
- **成本约束**：本工具会消耗积分；失败/空结果不得自动换关键词、翻页或连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-shopee-store-fbs-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
- 响应体 ≤ 8 KB：落盘后把完整 JSON 打印到 stdout
- 响应体 > 8 KB：落盘后 stdout 只输出摘要（顶层字段、常见计数如 `total`/`costToken`、最大列表字段的长度 + 前 3 条样本）
- 加 `--inline` 强制全量打印到 stdout（同样落盘）

**读数据建议**：先看摘要判断是否足够；需要具体字段时优先用 `jq`或`ConvertFrom-Json` 从保存的 json 文件按需抽取，避免整份 JSON 进入上下文。

## 官方参考

FBS 模块索引：[v2.fbs.query_br_shop_enrollment_status](https://open.shopee.com/documents/v2/v2.fbs.query_br_shop_enrollment_status?module=126&type=1)

---

## Prerequisites

1. 运行 `python scripts/check_auth_dependency.py`；exit code **42** → 先安装 **`linkfox-shopee-store-auth`**。
2. 通用 SBS 仓储 → `linkfox-shopee-store-sbs`；物流 → `linkfox-shopee-store-logistics`。

## 可用脚本（4 个 API）

| 脚本 | API | Method |
|------|-----|--------|
| `query_br_shop_enrollment_status.py` | query_br_shop_enrollment_status | GET |
| `query_br_shop_invoice_error.py` | query_br_shop_invoice_error | GET |
| `query_br_shop_block_status.py` | query_br_shop_block_status | GET |
| `query_br_sku_block_status.py` | query_br_sku_block_status | GET |
| `fbs_api.py` | 通用入口 | — |

## Usage Scenarios

### 1. 查巴西 FBS 店铺状态
1. `query_br_shop_enrollment_status.py` 入驻状态
2. `query_br_shop_block_status.py` 店铺封禁
3. `query_br_sku_block_status.py` SKU 封禁

### 2. 排查发票问题
`query_br_shop_invoice_error.py` 查发票错误

## Not Applicable

- 店铺授权 → `linkfox-shopee-store-auth`
- SBS 通用仓储库存 → `linkfox-shopee-store-sbs`
- 物流发货 → `linkfox-shopee-store-logistics`
- 商品 listing → `linkfox-shopee-store-product`

**Feedback:** 见 `references/api.md`。


---
*For more high-quality, professional cross-border e-commerce skills, visit [LinkFox Skills](https://skill.linkfox.com/).*
