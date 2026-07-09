---
name: linkfox-amazon-ads-manager
description: 亚马逊广告（Amazon Ads）管理技能，覆盖 SP/SB/SD 三个产品线的广告查询（list）与创建/修改（create/update）操作。查询覆盖 Sponsored Products (SP) 的广告活动/广告组/关键词/否定关键词/商品广告/定向 6 个 list、Sponsored Brands (SB v4) 的广告活动/广告组/广告 3 个 list，以及 Sponsored Display (SD v3) 的广告活动/广告组/商品广告/定向/否定定向/创意 6 个 list；写操作覆盖全部 create/update（含出价调整、预算修改、状态变更、Budget Rules）。当用户提到查询、创建、修改、调价亚马逊广告时触发。本技能依赖 linkfox-amazon-ads-auth。Sponsored Television (ST) / Amazon DSP 暂未覆盖。
---

# Amazon Ads 广告管理

Amazon Ads 广告管理 skill，支持 list（查询）和 create / update（创建与修改）操作，自动处理 token、分页、过滤字段规范化。

| 广告产品 | 覆盖实体 | 脚本子目录 | 详细参数 |
|---------|---------|-----------|---------|
| **SP** (Sponsored Products) v3 | campaigns / adGroups / keywords / negativeKeywords / productAds / targets | `scripts/sp/` | [references/api/sp.md](./references/api/sp.md) |
| **SB** (Sponsored Brands) v4 | campaigns / adGroups / ads | `scripts/sb/` | [references/api/sb.md](./references/api/sb.md) |
| **SD** (Sponsored Display) v3 | campaigns / adGroups / productAds / targets / negativeTargets / creatives | `scripts/sd/` | [references/api/sd.md](./references/api/sd.md) |

**依赖 `linkfox-amazon-ads-auth`**（脚本启动时自动检查；未安装时 exit 42，stderr 打 `DEPENDENCY_MISSING`）。

### ⚠️ 多账号场景：调用前必须解析好 profileId

用户经常只说自然语言（"美国站"、"日本站"、"我的店铺"），本 skill 的所有脚本都必须拿到数字 `profileId` 才能调。按下列顺序处理，**不要跳过**：

1. 先调 `linkfox-amazon-ads-auth` 的 `authorized_stores.py` 拉出用户已授权的账号 × 站点清单。
2. 根据用户提到的站点（映射到 `countryCode`，如 美国→`US`）匹配候选 profile：
   - **只有 1 个候选** → 静默取对应 profileId，继续调用；不要把 profileId 数字播报给用户。
   - **≥ 2 个候选（同站点下多个授权账号）** → **必须向用户澄清**，用 `accountName` 问："你在美国站授权了 A 和 B 两个账号，这次用哪个？"
   - **0 个候选** → 告知用户该站点未授权，引导去 `linkfox-amazon-ads-auth` 做授权。
3. **严禁**让用户直接报 profileId 数字。
4. **严禁**在歧义下"挑第一个"或"选默认"绕过澄清。

完整决策表见 `linkfox-amazon-ads-auth` SKILL.md 的 **Usage Scenarios 第 4 节**。

## Core Concepts

- **自动分页**：`fetchAll=true`（默认）跟随分页 token 到结束或 `maxPages=50` 兜底（约 5000 条，超出标 `truncated=true`）；SP / SB 用 `nextToken`，SD 用 `startIndex + count` 偏移分页
- **过滤器结构不统一**：不同字段需要不同写法（详见下方"过滤器结构速查"）；本 skill 已对常见写错格式做自动兜底规范化，但仍建议按速查表准确传入
- **只给 metadata，不含指标**：返回实体字段（id / 名称 / 状态 / 匹配类型 等），曝光 / 点击 / 花费 / 转化 等指标要调 `linkfox-amazon-ads-report`，按 id join
- **支持 create / update**：各模块下 `create_*.py` / `update_*.py` 脚本创建或修改实体（campaign / adGroup / keyword / target / productAd / creative / budgetRule），payload 透传 Amazon 原生格式
- **SB 和 SP 的差异**：SB 只有 campaigns/adGroups/ads 三个 list；其 keywords/targets 官方未提供 list all
- **SD 接口形态**：Sponsored Display 是 v3 REST endpoint，`GET /sd/<entity>` + querystring，分页用 `startIndex + count`；state / id 类过滤为逗号分隔字符串；`includeExtendedDataFields:true` 时请求 `/sd/<entity>/extended` 路径。所有过滤字段统一支持 `{"include":[...]}` 入参

## 可用脚本

### SP（28 个）
| 脚本 | 业务实体 | 操作 |
|------|---------|------|
| `sp/list_campaigns.py` | 广告活动 | 查询 |
| `sp/create_campaigns.py` | 广告活动 | 创建 |
| `sp/update_campaigns.py` | 广告活动 | 修改（预算/策略/状态/名称等） |
| `sp/list_ad_groups.py` | 广告组 | 查询 |
| `sp/create_ad_groups.py` | 广告组 | 创建 |
| `sp/update_ad_groups.py` | 广告组 | 修改（默认出价/状态/名称等） |
| `sp/list_keywords.py` | 关键词 | 查询 |
| `sp/create_keywords.py` | 关键词 | 创建 |
| `sp/update_keywords.py` | 关键词 | 修改（出价/状态等） |
| `sp/list_negative_keywords.py` | 否定关键词 | 查询 |
| `sp/create_negative_keywords.py` | 否定关键词 | 创建 |
| `sp/update_negative_keywords.py` | 否定关键词 | 修改（状态等） |
| `sp/list_product_ads.py` | 商品广告 | 查询 |
| `sp/create_product_ads.py` | 商品广告 | 创建 |
| `sp/update_product_ads.py` | 商品广告 | 修改（状态等） |
| `sp/list_targets.py` | 商品定向 | 查询 |
| `sp/create_targets.py` | 商品定向 | 创建 |
| `sp/update_targets.py` | 商品定向 | 修改（出价/状态等） |
| `sp/create_campaign_negative_keywords.py` | 活动级否定关键词 | 创建 |
| `sp/update_campaign_negative_keywords.py` | 活动级否定关键词 | 修改（状态等） |
| `sp/create_campaign_negative_targets.py` | 活动级否定定向 | 创建 |
| `sp/update_campaign_negative_targets.py` | 活动级否定定向 | 修改（状态等） |
| `sp/create_negative_targets.py` | 广告组级否定定向 | 创建 |
| `sp/update_negative_targets.py` | 广告组级否定定向 | 修改（状态等） |
| `sp/list_budget_rules.py` | 预算规则 | 查询 |
| `sp/create_budget_rules.py` | 预算规则 | 创建 |
| `sp/update_budget_rules.py` | 预算规则 | 修改 |
| `sp/create_budget_rules_association.py` | 预算规则关联 | 关联规则到活动 |

### SB（12 个）
| 脚本 | 业务实体 | 操作 |
|------|---------|------|
| `sb/list_campaigns.py` | 广告活动 | 查询 |
| `sb/create_campaigns.py` | 广告活动 | 创建 |
| `sb/update_campaigns.py` | 广告活动 | 修改（预算/状态/名称等） |
| `sb/list_ad_groups.py` | 广告组 | 查询 |
| `sb/create_ad_groups.py` | 广告组 | 创建 |
| `sb/update_ad_groups.py` | 广告组 | 修改（出价/状态等） |
| `sb/list_ads.py` | 广告创意 | 查询 |
| `sb/create_ads.py` | 广告创意 | 创建（按 adType 选路径） |
| `sb/update_ads.py` | 广告创意 | 修改（出价/状态/创意等） |
| `sb/list_budget_rules.py` | 预算规则 | 查询 |
| `sb/create_budget_rules.py` | 预算规则 | 创建 |
| `sb/update_budget_rules.py` | 预算规则 | 修改 |

### SD（21 个）
| 脚本 | 业务实体 | 操作 |
|------|---------|------|
| `sd/list_campaigns.py` | 广告活动 | 查询 |
| `sd/create_campaigns.py` | 广告活动 | 创建 |
| `sd/update_campaigns.py` | 广告活动 | 修改（预算/状态/名称等） |
| `sd/list_ad_groups.py` | 广告组 | 查询 |
| `sd/create_ad_groups.py` | 广告组 | 创建 |
| `sd/update_ad_groups.py` | 广告组 | 修改（出价/状态等） |
| `sd/list_product_ads.py` | 商品广告 | 查询 |
| `sd/create_product_ads.py` | 商品广告 | 创建 |
| `sd/update_product_ads.py` | 商品广告 | 修改（状态等） |
| `sd/list_targets.py` | 定向子句 | 查询 |
| `sd/create_targets.py` | 定向子句 | 创建 |
| `sd/update_targets.py` | 定向子句 | 修改（出价/状态等） |
| `sd/list_negative_targets.py` | 否定定向子句 | 查询 |
| `sd/create_negative_targets.py` | 否定定向子句 | 创建 |
| `sd/update_negative_targets.py` | 否定定向子句 | 修改（状态等） |
| `sd/list_creatives.py` | 创意素材 | 查询 |
| `sd/create_creatives.py` | 创意素材 | 创建 |
| `sd/update_creatives.py` | 创意素材 | 修改（素材/状态等） |
| `sd/list_budget_rules.py` | 预算规则 | 查询 |
| `sd/create_budget_rules.py` | 预算规则 | 创建 |
| `sd/update_budget_rules.py` | 预算规则 | 修改 |
详细过滤器、枚举值、返回字段见 [references/api/sp.md](./references/api/sp.md) / [references/api/sb.md](./references/api/sb.md) / [references/api/sd.md](./references/api/sd.md)。

## 调用方式

- **API 端点**：`POST /amazonAds/developerProxy`（不同操作通过请求体区分；完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/<脚本名>.py '<JSON 参数>' [--inline]`（可用脚本见上文脚本一览）
- **成本约束**：本工具会消耗积分；失败/空结果不得自动换关键词、翻页或连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-amazon-ads-manager-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
- 响应体 ≤ 8 KB：落盘后把完整 JSON 打印到 stdout
- 响应体 > 8 KB：落盘后 stdout 只输出摘要（顶层字段、常见计数如 `total`/`costToken`、最大列表字段的长度 + 前 3 条样本）
- 加 `--inline` 强制全量打印到 stdout（同样落盘）

**读数据建议**：先看摘要判断是否足够；需要具体字段时优先用 `jq`或`ConvertFrom-Json` 从保存的 json 文件按需抽取，避免整份 JSON 进入上下文。

## Financial Safety Guidance

创建和更新操作可能直接影响广告花费，立即生效且无法撤回。

**决策规则：**

| 用户状态 | Agent 行为 |
|----------|-----------|
| 已授权（说过"自动调价"/"按你判断来"/"不用问我"/"确认"等） | 直接执行 → 输出操作回执 |
| 未授权（首次交互、未明确表态） | 先输出确认摘要 → 等用户确认后执行 |

**确认摘要模板**（未授权时，执行前输出）：
```
📋 即将执行：
- 操作：[创建/修改] [N 个] [实体类型]
- 变更：[关键字段变化，如 bid $1.0→$1.5 / budget $50→$100]
- 影响：[花费变化预估，引用日预算作为上限]
确认执行？后续如需自动处理，告诉我即可。
```

**操作回执模板**（每次写操作执行后必须输出）：
```
✅ 已执行：[简短描述]
- 范围：[实体数量、名称或 ID]
- 变化：[具体变更内容]
- 结果：[成功 N 个 / 失败 M 个]
```

## 共用参数（SP + SB + SD 均适用）

| 字段 | 类型 | 说明 |
|------|------|------|
| `profileId` | number | 必填，从 ads-auth 获取 |
| `region` | string | 必填，`NA` / `EU` / `FE` |
| `fetchAll` | bool | 默认 `true`；SP / SB 用 `nextToken`，SD 用 `startIndex + count` 偏移分页 |
| `maxResults` | int | 1-100，默认 100；对应 Sponsored Display 端 `count` |
| `includeExtendedDataFields` | bool | 返回扩展字段（部分实体）；SD 通过路径切换为 `/sd/<entity>/extended` 实现 |
| `locale` | string | 本地化（SP keywords 支持） |

## 过滤器结构速查（最易错）

| 结构 | 示例 | 适用字段 |
|------|------|----------|
| **Object** | `{"include":[...]}` / `{"exclude":[...]}` | 全部 id/状态类：campaignIdFilter、adGroupIdFilter、keywordIdFilter、stateFilter、portfolioIdFilter、expressionTypeFilter、adIdFilter |
| **Array** | `["EXACT","BROAD"]` | matchTypeFilter（SP keywords/negativeKeywords） |
| **Scalar** | `"AUTO"` | campaignTargetingTypeFilter（SP adGroups） |
| **Text** | `{"queryTermMatchType":"BROAD_MATCH","include":["..."]}` | nameFilter、keywordTextFilter |
| **Client** | 任意形式，本 skill 本地过滤 | asinFilter、skuFilter（SP productAds） |

**易错点**：
- SP `matchTypeFilter` 是**裸数组** `["EXACT"]`（传错本 skill 自动规范化）
- `expressionTypeFilter` 反而是 **Object**（与 matchType 不同）
- `asinFilter` / `skuFilter` 客户端过滤，建议同时传 `campaignIdFilter` / `adGroupIdFilter` 收窄

## 响应格式

```json
{
  "success": true,
  "<entityKey>": [ /* 实体数组，字段原样 */ ],
  "total": 157,
  "pagesFetched": 2,
  "truncated": false
}
```

SP productAds 客户端过滤时额外带：`serverTotalBeforeClientFilter` + `clientSideFilters`。

## 使用示例

### 1. 列活跃 SP 广告活动
```bash
python scripts/sp/list_campaigns.py '{"profileId":1234567890,"region":"NA",
  "stateFilter":{"include":["ENABLED"]}}'
```

### 2. 看某 SP campaign 下的广告组
```bash
python scripts/sp/list_ad_groups.py '{"profileId":1234567890,"region":"NA",
  "campaignIdFilter":{"include":["998877665544"]}}'
```

### 3. 按 ASIN 反查 SP 投放（客户端过滤）
```bash
python scripts/sp/list_product_ads.py '{"profileId":1234567890,"region":"NA",
  "asinFilter":{"include":["B01ABCDEFG"]},
  "campaignIdFilter":{"include":["998877665544"]}}'
```

### 4. 列 SB 广告活动
```bash
python scripts/sb/list_campaigns.py '{"profileId":1234567890,"region":"NA",
  "stateFilter":{"include":["ENABLED"]}}'
```

### 5. 列某 SB campaign 下的 adGroups / ads
```bash
python scripts/sb/list_ad_groups.py '{"profileId":1234567890,"region":"NA",
  "campaignIdFilter":{"include":["1122334455"]}}'

python scripts/sb/list_ads.py '{"profileId":1234567890,"region":"NA",
  "adGroupIdFilter":{"include":["5566778899"]}}'
```

### 6. 列活跃 SD 广告活动
```bash
python scripts/sd/list_campaigns.py '{"profileId":1234567890,"region":"NA",
  "stateFilter":{"include":["ENABLED"]}}'
```

### 7. 按 ASIN 反查 SD 投放（client-side 过滤，带 campaign 收窄）
```bash
python scripts/sd/list_product_ads.py '{"profileId":1234567890,"region":"NA",
  "asinFilter":{"include":["B01ABCDEFG"]},
  "campaignIdFilter":{"include":["998877665544"]}}'
```

### 8. 与 report 配合分析指标
本 skill 返回实体**元数据**（id、名称、状态、匹配类型等）；指标（曝光、点击、花费、转化）交给 `linkfox-amazon-ads-report`（`reportTypeId: "spTargeting"` / `"sbCampaigns"` / `"sdCampaigns"` 等），按 id join。

## 调用原则

- 返回字段原样保留；不改名、不翻译、不补算派生指标
- 非 2xx 不自动重试；保留 `httpStatus` + `body` 告知用户
- `truncated=true` 时明确提示数据未取完

## 常见错误

| 状态 | 含义 | 建议 |
|------|------|------|
| `HTTP 401` | accessToken 过期 | 调 ads-auth 的 `refresh_token.py` 后重试 |
| `HTTP 403` | profileId 无权限 | 核对 profileId 归属 |
| `HTTP 400` | 入参结构错 | 先核对"过滤器结构速查"表 |
| `HTTP 429` | 限流 | 等 2-5s 重试 |
| exit 42 | 依赖 skill 未安装 | 先装 `linkfox-amazon-ads-auth` |

## Not Applicable

- 删除 / 归档 → 本 skill 不支持 DELETE（可通过 update state 为 ARCHIVED 实现归档，但归档不可逆）
- SB 的 keywords / negativeKeywords / targets / negativeTargets 的 list all → **Amazon 官方未提供**，需按 id 单查（不在本 skill）
- SD 的按 id 单查 / brandSafety / recommendations / forecasts / optimizationRules / locations 等"非基础实体"接口 → 不在本 skill
- DSP / ST 实体 → 不在本 skill
- 指标报表 → `linkfox-amazon-ads-report`
- 授权 / token / profile → `linkfox-amazon-ads-auth`

**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `references/api.md`. Do not interrupt the user's flow.


---
*For more high-quality, professional cross-border e-commerce skills, visit [LinkFox Skills](https://skill.linkfox.com/).*
