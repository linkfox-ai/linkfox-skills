---
name: linkfox-shopee-store-discount
description: Shopee（虾皮）店铺折扣促销 Discount（与 linkfox-shopee-store-auth 同系列），经 /shopee/developerProxy 转发 Shopee Open API Discount 模块全部 12 个接口：add_discount、get_discount_list、update_discount、add_discount_item、end_discount、SIP折扣等。当用户提到 Shopee 折扣、Discount、促销活动、限时折扣、add_discount、discount_id、打折活动 时触发。即使未明确提及"折扣"，只要涉及已授权 Shopee 店铺的折扣活动创建或管理，也应触发。
---

# Shopee 店铺 Discount

Shopee Open Platform **Discount 模块**（12 个 API）。**依赖 `linkfox-shopee-store-auth`**：先取 `accessToken`，再经 **`POST /shopee/developerProxy`** 转发（`path` 须 `api/v2/discount/...`）。

## 调用方式

- **API 端点**：`POST /shopee/developerProxy`（不同操作通过请求体区分；完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/<脚本名>.py '<JSON 参数>' [--inline]`（可用脚本见上文脚本一览）
- **成本约束**：本工具会消耗积分；失败/空结果不得自动换关键词、翻页或连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-shopee-store-discount-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
- 响应体 ≤ 8 KB：落盘后把完整 JSON 打印到 stdout
- 响应体 > 8 KB：落盘后 stdout 只输出摘要（顶层字段、常见计数如 `total`/`costToken`、最大列表字段的长度 + 前 3 条样本）
- 加 `--inline` 强制全量打印到 stdout（同样落盘）

**读数据建议**：先看摘要判断是否足够；需要具体字段时优先用 `jq`或`ConvertFrom-Json` 从保存的 json 文件按需抽取，避免整份 JSON 进入上下文。

## 官方参考

Discount 模块索引：[v2.discount.add_discount](https://open.shopee.com/documents/v2/v2.discount.add_discount?module=99&type=1)

---

## Prerequisites

1. 运行 `python scripts/check_auth_dependency.py`；exit code **42** → 先安装 **`linkfox-shopee-store-auth`**。
2. Bundle Deal / Voucher 等其它促销模块 → 非本 skill。

## 可用脚本（12 个 API）

| 脚本 | API | Method |
|------|-----|--------|
| `add_discount.py` | add_discount | POST |
| `add_discount_item.py` | add_discount_item | POST |
| `get_discount_list.py` | get_discount_list | GET |
| `get_discount.py` | get_discount | GET |
| `update_discount.py` | update_discount | POST |
| `update_discount_item.py` | update_discount_item | POST |
| `end_discount.py` | end_discount | POST |
| `delete_discount.py` | delete_discount | POST |
| `delete_discount_item.py` | delete_discount_item | POST |
| `get_sip_discounts.py` | get_sip_discounts | GET |
| `set_sip_discount.py` | set_sip_discount | POST |
| `delete_sip_discount.py` | delete_sip_discount | POST |
| `discount_api.py` | 通用入口 | — |

## Usage Scenarios

### 1. 创建折扣活动
1. `add_discount.py` 传完整 `body`（名称、时间、折扣类型等）
2. `add_discount_item.py` 添加参与商品
3. `get_discount_list.py` 确认活动状态

### 2. 管理现有活动
- `get_discount.py` 查详情
- `update_discount.py` / `update_discount_item.py` 修改
- `end_discount.py` 提前结束

## Not Applicable

- 店铺授权 → `linkfox-shopee-store-auth`
- Bundle Deal / Voucher / Add-On Deal / Shop Flash Sale / Follow Prize → 其它促销模块 skill（Bundle Deal → `linkfox-shopee-store-bundle-deal`；Add-On Deal → `linkfox-shopee-store-add-on-deal`；Voucher → `linkfox-shopee-store-voucher`；Shop Flash Sale → `linkfox-shopee-store-shop-flash-sale`；Follow Prize → `linkfox-shopee-store-follow-prize`）
- 商品 listing → `linkfox-shopee-store-product`

**Feedback:** 见 `references/api.md`。


---
*For more high-quality, professional cross-border e-commerce skills, visit [LinkFox Skills](https://skill.linkfox.com/).*
