---
name: linkfox-shopee-store-account-health
description: Shopee（虾皮）账户健康 Account Health（与 linkfox-shopee-store-auth 同系列），经 /shopee/developerProxy 转发 Shopee Open API Account Health 模块全部 6 个接口：get_shop_performance、get_metric_source_detail、get_penalty_point_history、get_punishment_history、get_listings_with_issues、get_late_orders。当用户提到 Shopee 账户健康、Account Health、店铺绩效、扣分记录、处罚历史、逾期订单、listing问题 时触发。即使未明确提及"账户健康"，只要涉及已授权 Shopee 店铺的健康指标与处罚数据查询，也应触发。
---

# Shopee 账户健康 Account Health

Shopee Open Platform **Account Health 模块**（6 个 API，均为 GET）。**依赖 `linkfox-shopee-store-auth`**：先取 `accessToken`，再经 **`POST /shopee/developerProxy`** 转发（`path` 须 `api/v2/account_health/...`）。

## 调用方式

- **API 端点**：`POST /shopee/developerProxy`（不同操作通过请求体区分；完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/<脚本名>.py '<JSON 参数>' [--inline]`（可用脚本见上文脚本一览）
- **成本约束**：本工具会消耗积分；失败/空结果不得自动换关键词、翻页或连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-shopee-store-account-health-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
- 响应体 ≤ 8 KB：落盘后把完整 JSON 打印到 stdout
- 响应体 > 8 KB：落盘后 stdout 只输出摘要（顶层字段、常见计数如 `total`/`costToken`、最大列表字段的长度 + 前 3 条样本）
- 加 `--inline` 强制全量打印到 stdout（同样落盘）

**读数据建议**：先看摘要判断是否足够；需要具体字段时优先用 `jq`或`ConvertFrom-Json` 从保存的 json 文件按需抽取，避免整份 JSON 进入上下文。

## 官方参考

Account Health 模块索引：[v2.account_health.get_shop_performance](https://open.shopee.com/documents/v2/v2.account_health.get_shop_performance?module=103&type=1)

---

## Prerequisites

1. 运行 `python scripts/check_auth_dependency.py`；exit code **42** → 先安装 **`linkfox-shopee-store-auth`**。
2. 订单详情 → `linkfox-shopee-store-orders`；商品 listing → `linkfox-shopee-store-product`。

## 可用脚本（6 个 API）

| 脚本 | API | Method |
|------|-----|--------|
| `get_shop_performance.py` | get_shop_performance | GET |
| `get_metric_source_detail.py` | get_metric_source_detail | GET |
| `get_penalty_point_history.py` | get_penalty_point_history | GET |
| `get_punishment_history.py` | get_punishment_history | GET |
| `get_listings_with_issues.py` | get_listings_with_issues | GET |
| `get_late_orders.py` | get_late_orders | GET |
| `account_health_api.py` | 通用入口 | — |

## Usage Scenarios

### 1. 查看店铺健康概况
1. `get_shop_performance.py` 获取绩效指标
2. `get_metric_source_detail.py` 下钻具体指标
3. `get_late_orders.py` / `get_listings_with_issues.py` 定位问题

### 2. 查处罚与扣分记录
1. `get_penalty_point_history.py` 扣分历史
2. `get_punishment_history.py` 处罚历史

## Not Applicable

- 店铺授权 → `linkfox-shopee-store-auth`
- 订单处理 → `linkfox-shopee-store-orders`
- 商品 listing → `linkfox-shopee-store-product`
- 店铺基础信息 → `linkfox-shopee-store-shop`

**Feedback:** 见 `references/api.md`。


---
*For more high-quality, professional cross-border e-commerce skills, visit [LinkFox Skills](https://skill.linkfox.com/).*
