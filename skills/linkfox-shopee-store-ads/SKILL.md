---
name: linkfox-shopee-store-ads
description: Shopee（虾皮）店铺站内广告 Ads（与 linkfox-shopee-store-auth 同系列），经 /shopee/developerProxy 转发 Shopee Open API Ads 模块 23 个接口：get_total_balance、create_manual_product_ads、get_product_campaign_daily_performance、GMS 广告等。当用户提到 Shopee 广告、Ads、广告余额、CPC、商品推广、手动广告、campaign、广告效果、ROI、get_total_balance 时触发。即使未明确提及"广告"，只要涉及已授权 Shopee 店铺的广告账户、推广或效果查询，也应触发。
---

# Shopee 店铺 Ads

Shopee Open Platform **Ads 模块**（23 个 API，不含即将下线的 auto product ads）。**依赖 `linkfox-shopee-store-auth`**：先取 `accessToken`，再经 **`POST /shopee/developerProxy`** 转发（`path` 须 `api/v2/ads/...`）。

## 调用方式

- **API 端点**：`POST /shopee/developerProxy`（不同操作通过请求体区分；完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/<脚本名>.py '<JSON 参数>' [--inline]`（可用脚本见上文脚本一览）
- **成本约束**：本工具会消耗积分；失败/空结果不得自动换关键词、翻页或连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-shopee-store-ads-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
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

Ads 模块索引：[v2.ads.get_total_balance](https://open.shopee.com/documents/v2/v2.ads.get_total_balance?module=117&type=1)

---

## Prerequisites（必须先读）

1. 运行 `python scripts/check_auth_dependency.py`；exit code **42** → 先安装 **`linkfox-shopee-store-auth`** 并授权店铺。
2. **不要**在本 skill 内实现授权/令牌逻辑。
3. Ads API 需 Shopee **额外广告权限**；并非所有站点/店铺可用。

---

## Core Concepts

- **转发链路**：`storeTokens` → `developerProxy` → 紫鸟 `shopee-proxy` → Shopee API
- **余额**：`get_total_balance` 查广告账户余额
- **手动商品广告**：`create_manual_product_ads` → `edit_manual_product_ads` / `edit_manual_product_ad_keywords`
- **效果报表**：`get_all_cpc_ads_*_performance`、`get_product_campaign_*_performance`
- **GMS**：`create_gms_product_campaign` 等系列
- **未纳入**：`create_auto_product_ads`、`edit_auto_product_ads`（官方标注 coming offline soon）
- **联盟营销 AMS**（module=127）→ 非本 skill

## 可用脚本（Ads 模块 23 个 API）

| 分组 | 脚本 |
|------|------|
| 账户/推荐 | `get_total_balance.py`、`get_shop_toggle_info.py`、`get_recommended_keyword_list.py`、`get_recommended_item_list.py` |
| CPC 效果 | `get_all_cpc_ads_daily_performance.py`、`get_all_cpc_ads_hourly_performance.py` |
| 商品广告 | `create_manual_product_ads.py`、`edit_manual_product_ads.py`、`get_product_level_campaign_id_list.py` 等 |
| GMS | `create_gms_product_campaign.py`、`get_gms_campaign_performance.py` 等 |
| 通用入口 | `ads_api.py`（JSON 含 `api` 字段） |

完整列表见 `references/api.md`。共享：`_shopee_ads_common.py`、`_ads_endpoints.py`、`_ads_api_runner.py`。

## Usage Scenarios

### 1. 查余额与推荐
1. `get_total_balance.py`
2. `get_recommended_item_list.py` / `get_recommended_keyword_list.py`

### 2. 创建手动商品广告
1. `get_create_product_ad_budget_suggestion.py`
2. `create_manual_product_ads.py` 传完整 `body`
3. `get_product_campaign_daily_performance.py` 查效果

## 调用原则

- 先看 **`developerProxy.httpStatus`**，再读 `*Response` 字段
- GET：业务参数放 JSON 顶层
- POST：复杂接口传 `body`；create/edit 建议传唯一 `reference_id` 防重复
- 每个脚本 docstring 含 **官方文档 URL**（`module=117`）

## Not Applicable

- 店铺授权 → `linkfox-shopee-store-auth`
- 商品 listing → `linkfox-shopee-store-product`
- 联盟营销 AMS（module=127）→ `linkfox-shopee-store-ams`
- Amazon 广告 → `linkfox-amazon-ads-*` 系列

## 积分消耗规则

不消耗积分。

**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `references/api.md`. Do not interrupt the user's flow.


---
*For more high-quality, professional cross-border e-commerce skills, visit [LinkFox Skills](https://skill.linkfox.com/).*
