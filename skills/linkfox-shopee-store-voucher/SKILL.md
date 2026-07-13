---
name: linkfox-shopee-store-voucher
description: Shopee（虾皮）店铺优惠券 Voucher（与 linkfox-shopee-store-auth 同系列），经 /shopee/developerProxy 转发 Shopee Open API Voucher 模块全部 6 个接口：add_voucher、get_voucher_list、get_voucher、update_voucher、end_voucher、delete_voucher。当用户提到 Shopee 优惠券、Voucher、店铺券、add_voucher、voucher_id、满减券、折扣码 时触发。即使未明确提及"优惠券"，只要涉及已授权 Shopee 店铺的 Voucher 活动管理，也应触发。
---

# Shopee 店铺优惠券 Voucher

Shopee Open Platform **Voucher 模块**（6 个 API）。**依赖 `linkfox-shopee-store-auth`**：先取 `accessToken`，再经 **`POST /shopee/developerProxy`** 转发（`path` 须 `api/v2/voucher/...`）。

## 调用方式

- **API 端点**：`POST /shopee/developerProxy`（不同 Shopee Open API 操作通过 path/method 区分；完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/<脚本名>.py '<JSON 参数>' [--inline]`（可用脚本见上文脚本一览）
- **成本约束**：本工具会消耗积分；失败/空结果不得自动换关键词、翻页或连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-shopee-store-voucher-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
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

## 官方参考

Voucher 模块索引：[v2.voucher.add_voucher](https://open.shopee.com/documents/v2/v2.voucher.add_voucher?module=112&type=1)

---

## Prerequisites

1. 运行 `python scripts/check_auth_dependency.py`；exit code **42** → 先安装 **`linkfox-shopee-store-auth`**。
2. 其它促销：Discount → `linkfox-shopee-store-discount`；Bundle Deal → `linkfox-shopee-store-bundle-deal`；Add-On Deal → `linkfox-shopee-store-add-on-deal`；Shop Flash Sale → `linkfox-shopee-store-shop-flash-sale`。

## 可用脚本（6 个 API）

| 脚本 | API | Method |
|------|-----|--------|
| `add_voucher.py` | add_voucher | POST |
| `delete_voucher.py` | delete_voucher | POST |
| `end_voucher.py` | end_voucher | POST |
| `update_voucher.py` | update_voucher | POST |
| `get_voucher.py` | get_voucher | GET |
| `get_voucher_list.py` | get_voucher_list | GET |
| `voucher_api.py` | 通用入口 | — |

## Usage Scenarios

### 1. 创建并管理优惠券
1. `add_voucher.py` 传完整 `body`
2. `get_voucher_list.py` 查看活动列表
3. `update_voucher.py` / `end_voucher.py` 更新或结束

## Not Applicable

- 店铺授权 → `linkfox-shopee-store-auth`
- 限时折扣 Discount → `linkfox-shopee-store-discount`
- 套装优惠 Bundle Deal → `linkfox-shopee-store-bundle-deal`
- 加购优惠 Add-On Deal → `linkfox-shopee-store-add-on-deal`
- 商品 listing → `linkfox-shopee-store-product`

## 积分消耗规则

不消耗积分。

**Feedback:** 见 `references/api.md`。

---
*For more high-quality, professional cross-border e-commerce skills, visit [LinkFox Skills](https://skill.linkfox.com/).*
