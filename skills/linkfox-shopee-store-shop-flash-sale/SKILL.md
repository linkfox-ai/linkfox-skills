---
name: linkfox-shopee-store-shop-flash-sale
description: Shopee（虾皮）店铺秒杀 Shop Flash Sale（与 linkfox-shopee-store-auth 同系列），经 /shopee/developerProxy 转发 Shopee Open API Shop Flash Sale 模块全部 11 个接口：get_time_slot_id、create_shop_flash_sale、get_shop_flash_sale_list、add_shop_flash_sale_items、update_shop_flash_sale 等。当用户提到 Shopee 店铺秒杀、Shop Flash Sale、限时秒杀、get_time_slot_id、flash_sale_id、秒杀时段 时触发。即使未明确提及"秒杀"，只要涉及已授权 Shopee 店铺的 Flash Sale 活动管理，也应触发。
---

# Shopee 店铺秒杀 Shop Flash Sale

Shopee Open Platform **Shop Flash Sale 模块**（11 个 API）。**依赖 `linkfox-shopee-store-auth`**：先取 `accessToken`，再经 **`POST /shopee/developerProxy`** 转发（`path` 须 `api/v2/shop_flash_sale/...`）。

## 调用方式

- **API 端点**：`POST /shopee/developerProxy`（不同操作通过请求体区分；完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/<脚本名>.py '<JSON 参数>' [--inline]`（可用脚本见上文脚本一览）
- **成本约束**：本工具会消耗积分；失败/空结果不得自动换关键词、翻页或连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/<skill-name>-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
- 响应体 ≤ 8 KB：落盘后把完整 JSON 打印到 stdout
- 响应体 > 8 KB：落盘后 stdout 只输出摘要（顶层字段、常见计数如 `total`/`costToken`、最大列表字段的长度 + 前 3 条样本）
- 加 `--inline` 强制全量打印到 stdout（同样落盘）

**读数据建议**：先看摘要判断是否足够；需要具体字段时优先用 `jq`或`ConvertFrom-Json` 从保存的 json 文件按需抽取，避免整份 JSON 进入上下文。

## 官方参考

Shop Flash Sale 模块索引：[v2.shop_flash_sale.get_time_slot_id](https://open.shopee.com/documents/v2/v2.shop_flash_sale.get_time_slot_id?module=123&type=1)

---

## Prerequisites

1. 运行 `python scripts/check_auth_dependency.py`；exit code **42** → 先安装 **`linkfox-shopee-store-auth`**。
2. 其它促销：Discount / Bundle Deal / Voucher / Shop Flash Sale / Follow Prize → 对应促销 skill。

## 可用脚本（11 个 API）

| 脚本 | API | Method |
|------|-----|--------|
| `get_time_slot_id.py` | get_time_slot_id | GET |
| `create_shop_flash_sale.py` | create_shop_flash_sale | POST |
| `get_item_criteria.py` | get_item_criteria | GET |
| `add_shop_flash_sale_items.py` | add_shop_flash_sale_items | POST |
| `get_shop_flash_sale_list.py` | get_shop_flash_sale_list | GET |
| `get_shop_flash_sale.py` | get_shop_flash_sale | GET |
| `get_shop_flash_sale_items.py` | get_shop_flash_sale_items | GET |
| `update_shop_flash_sale.py` | update_shop_flash_sale | POST |
| `update_shop_flash_sale_items.py` | update_shop_flash_sale_items | POST |
| `delete_shop_flash_sale.py` | delete_shop_flash_sale | POST |
| `delete_shop_flash_sale_items.py` | delete_shop_flash_sale_items | POST |
| `shop_flash_sale_api.py` | 通用入口 | — |

## Usage Scenarios

### 1. 创建店铺秒杀
1. `get_time_slot_id.py` 获取可用时段
2. `create_shop_flash_sale.py` 创建活动
3. `add_shop_flash_sale_items.py` 添加商品
4. `get_shop_flash_sale_list.py` 确认状态

## Not Applicable

- 店铺授权 → `linkfox-shopee-store-auth`
- 限时折扣 Discount → `linkfox-shopee-store-discount`
- 优惠券 Voucher → `linkfox-shopee-store-voucher`
- 商品 listing → `linkfox-shopee-store-product`

**Feedback:** 见 `references/api.md`。

---
*For more high-quality, professional cross-border e-commerce skills, visit [LinkFox Skills](https://skill.linkfox.com/).*
