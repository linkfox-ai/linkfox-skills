---
name: linkfox-shopee-store-follow-prize
description: Shopee（虾皮）关注有礼 Follow Prize（与 linkfox-shopee-store-auth 同系列），经 /shopee/developerProxy 转发 Shopee Open API Follow Prize 模块全部 6 个接口：add_follow_prize、get_follow_prize_list、get_follow_prize_detail、update_follow_prize、end_follow_prize、delete_follow_prize。当用户提到 Shopee 关注有礼、Follow Prize、关注送券、add_follow_prize、campaign_id、粉丝福利 时触发。即使未明确提及"关注有礼"，只要涉及已授权 Shopee 店铺的 Follow Prize 活动管理，也应触发。
---

# Shopee 关注有礼 Follow Prize

Shopee Open Platform **Follow Prize 模块**（6 个 API）。**依赖 `linkfox-shopee-store-auth`**：先取 `accessToken`，再经 **`POST /shopee/developerProxy`** 转发（`path` 须 `api/v2/follow_prize/...`）。

## 调用方式

- **API 端点**：`POST /shopee/developerProxy`（不同操作通过请求体区分；完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/follow_prize_api.py '<JSON 参数>' [--inline]`（可用脚本见上文脚本一览）
- **成本约束**：本工具会消耗积分；失败/空结果不得自动换关键词、翻页或连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/<linkfox-shopee-store-follow-prize>-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
- 响应体 ≤ 8 KB：落盘后把完整 JSON 打印到 stdout
- 响应体 > 8 KB：落盘后 stdout 只输出摘要（顶层字段、常见计数如 `total`/`costToken`、最大列表字段的长度 + 前 3 条样本）
- 加 `--inline` 强制全量打印到 stdout（同样落盘）

**读数据建议**：先看摘要判断是否足够；需要具体字段时优先用 `jq`或`ConvertFrom-Json` 从保存的 json 文件按需抽取，避免整份 JSON 进入上下文。

## 官方参考

Follow Prize 模块索引：[v2.follow_prize.add_follow_prize](https://open.shopee.com/documents/v2/v2.follow_prize.add_follow_prize?module=113&type=1)

---

## Prerequisites

1. 运行 `python scripts/check_auth_dependency.py`；exit code **42** → 先安装 **`linkfox-shopee-store-auth`**。
2. 其它促销：Discount / Bundle Deal / Voucher / Shop Flash Sale → 对应促销 skill。

## 可用脚本（6 个 API）

| 脚本 | API | Method |
|------|-----|--------|
| `add_follow_prize.py` | add_follow_prize | POST |
| `delete_follow_prize.py` | delete_follow_prize | POST |
| `end_follow_prize.py` | end_follow_prize | POST |
| `update_follow_prize.py` | update_follow_prize | POST |
| `get_follow_prize_detail.py` | get_follow_prize_detail | GET |
| `get_follow_prize_list.py` | get_follow_prize_list | GET |
| `follow_prize_api.py` | 通用入口 | — |

## Usage Scenarios

### 1. 创建关注有礼活动
1. `add_follow_prize.py` 传完整 `body`
2. `get_follow_prize_list.py` 查看活动列表
3. `update_follow_prize.py` / `end_follow_prize.py` 更新或结束

## Not Applicable

- 店铺授权 → `linkfox-shopee-store-auth`
- 限时折扣 Discount → `linkfox-shopee-store-discount`
- 优惠券 Voucher → `linkfox-shopee-store-voucher`
- 店铺秒杀 Shop Flash Sale → `linkfox-shopee-store-shop-flash-sale`
- 商品 listing → `linkfox-shopee-store-product`

**Feedback:** 见 `references/api.md`。

---
*For more high-quality, professional cross-border e-commerce skills, visit [LinkFox Skills](https://skill.linkfox.com/).*
