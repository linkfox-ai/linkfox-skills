---
name: linkfox-shopee-store-bundle-deal
description: Shopee（虾皮）套装优惠 Bundle Deal（与 linkfox-shopee-store-auth 同系列），经 /shopee/developerProxy 转发 Shopee Open API Bundle Deal 模块全部 10 个接口：add_bundle_deal、get_bundle_deal_list、add_bundle_deal_item、update_bundle_deal、end_bundle_deal 等。当用户提到 Shopee 套装优惠、Bundle Deal、组合促销、add_bundle_deal、bundle_deal_id、满件优惠 时触发。即使未明确提及"套装"，只要涉及已授权 Shopee 店铺的 Bundle Deal 活动管理，也应触发。
---

# Shopee 套装优惠 Bundle Deal

Shopee Open Platform **Bundle Deal 模块**（10 个 API）。**依赖 `linkfox-shopee-store-auth`**：先取 `accessToken`，再经 **`POST /shopee/developerProxy`** 转发（`path` 须 `api/v2/bundle_deal/...`）。

## 调用方式

- **API 端点**：`POST /shopee/developerProxy`（不同操作通过请求体区分；完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/<脚本名>.py '<JSON 参数>' [--inline]`（可用脚本见上文脚本一览）
- **成本约束**：本工具会消耗积分；失败/空结果不得自动换关键词、翻页或连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-shopee-store-bundle-deal-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
- 响应体 ≤ 8 KB：落盘后把完整 JSON 打印到 stdout
- 响应体 > 8 KB：落盘后 stdout 只输出摘要（顶层字段、常见计数如 `total`/`costToken`、最大列表字段的长度 + 前 3 条样本）
- 加 `--inline` 强制全量打印到 stdout（同样落盘）

**读数据建议**：先看摘要判断是否足够；需要具体字段时优先用 `jq`或`ConvertFrom-Json` 从保存的 json 文件按需抽取，避免整份 JSON 进入上下文。

## 官方参考

Bundle Deal 模块索引：[v2.bundle_deal.add_bundle_deal](https://open.shopee.com/documents/v2/v2.bundle_deal.add_bundle_deal?module=110&type=1)

---

## Prerequisites

1. 运行 `python scripts/check_auth_dependency.py`；exit code **42** → 先安装 **`linkfox-shopee-store-auth`**。
2. 限时折扣 → `linkfox-shopee-store-discount`；Add-On Deal → `linkfox-shopee-store-add-on-deal`；Voucher → `linkfox-shopee-store-voucher`。

## 可用脚本（10 个 API）

| 脚本 | API | Method |
|------|-----|--------|
| `add_bundle_deal.py` | add_bundle_deal | POST |
| `add_bundle_deal_item.py` | add_bundle_deal_item | POST |
| `get_bundle_deal_list.py` | get_bundle_deal_list | GET |
| `get_bundle_deal.py` | get_bundle_deal | GET |
| `get_bundle_deal_item.py` | get_bundle_deal_item | GET |
| `update_bundle_deal.py` | update_bundle_deal | POST |
| `update_bundle_deal_item.py` | update_bundle_deal_item | POST |
| `end_bundle_deal.py` | end_bundle_deal | POST |
| `delete_bundle_deal.py` | delete_bundle_deal | POST |
| `delete_bundle_deal_item.py` | delete_bundle_deal_item | POST |
| `bundle_deal_api.py` | 通用入口 | — |

## Usage Scenarios

### 1. 创建套装优惠
1. `add_bundle_deal.py` 传完整 `body`
2. `add_bundle_deal_item.py` 添加商品
3. `get_bundle_deal_list.py` 确认状态

## Not Applicable

- 店铺授权 → `linkfox-shopee-store-auth`
- 限时折扣 Discount → `linkfox-shopee-store-discount`
- 商品 listing → `linkfox-shopee-store-product`

**Feedback:** 见 `references/api.md`。


---
*For more high-quality, professional cross-border e-commerce skills, visit [LinkFox Skills](https://skill.linkfox.com/).*
