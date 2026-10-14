---
name: linkfox-amazon-ads-manager
description: 亚马逊广告（Amazon Ads）管理技能，覆盖 SP/SB/SD 的查询与创建/修改。Sponsored Brands 同时支持 V3 Legacy 与 V4：新活动、多 Ad Group、Ad/Creative Version 默认走 V4，历史 Legacy 可显式走 V3，Keyword/Target 按 Campaign 结构通过版本化脚本调用 Amazon 共享 targeting 资源；禁止 V4 失败后自动回落 V3，禁止用 V3 静默截断多 Ad Group 数据。适用于查询、创建、调价、改预算、改状态及管理 SP/SB/SD 广告。本技能依赖 linkfox-amazon-ads-auth；不覆盖 Sponsored Television / DSP。
---

# Amazon Ads 广告管理

Amazon Ads 广告管理 skill，支持 list（查询）和 create / update（创建与修改）操作；经 `developerProxy` 传 `profileId`，由服务端解析 token（勿先 `storeTokens` 取 raw token）。自动处理分页、过滤字段规范化。

| 广告产品 | 覆盖实体 | 脚本子目录 | 详细参数 |
|---------|---------|-----------|---------|
| **SP** (Sponsored Products) v3 | campaigns / adGroups / keywords / negativeKeywords / productAds / targets | `scripts/sp/` | [references/api/sp.md](./references/api/sp.md) |
| **SB** V3 Legacy + V4 | V3 Legacy campaigns/keywords/targets；V4 campaigns/adGroups/ads/creative versions；keywords/targets 走 V4 脚本入口但底层是共享 targeting 路径 | `scripts/sb/v3/`、`scripts/sb/v4/` | [references/api/sb.md](./references/api/sb.md) |
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

- **自动分页**：`fetchAll=true`（默认）跟随分页到结束或 `maxPages=50` 兜底；SP 与 SB V4 主资源 list 使用 `nextToken`，SB Target/BudgetRule 使用 `nextToken`（BudgetRule 查询必须带 `pageSize`），SB Keyword GET、SB V3 GET 与 SD 使用 `startIndex + count`
- **过滤器结构不统一**：不同字段需要不同写法（详见下方"过滤器结构速查"）；本 skill 已对常见写错格式做自动兜底规范化，但仍建议按速查表准确传入
- **只给 metadata，不含指标**：返回实体字段（id / 名称 / 状态 / 匹配类型 等），曝光 / 点击 / 花费 / 转化 等指标要调 `linkfox-amazon-ads-report`，按 id join
- **支持 create / update**：各模块下 `create_*.py` / `update_*.py` 脚本创建或修改实体（campaign / adGroup / keyword / target / productAd / budgetRule），payload 透传 Amazon 原生格式；SB Creative 仅支持按 `adId` 查询 Creative Version 与创建新版本，没有通用 update 脚本
- **SB V3/V4 共存**：默认使用 `scripts/sb/v4/`；只有确认是 Legacy 或用户明确要求 V3 时使用 `scripts/sb/v3/`。不自动执行 V4→V3 回落；已知 Multi-Ad-Group Campaign 必须拒绝 V3
- **SB 共享 Targeting**：Amazon 的 Keyword/Target 仍使用 `sb/keywords`、`sb/targets[/list]`，没有伪造的 `/sb/v4/keywords`；V3/V4 脚本入口隔离，但底层共享官方 targeting 资源
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

### SB V3 Legacy（10 个）
| 脚本组 | 业务实体 | 操作 |
|------|---------|------|
| `sb/v3/list/create/update_campaigns.py` | Legacy 广告活动（Creative 内嵌） | 查询/创建/修改 |
| `sb/v3/list_ad_groups.py` | Legacy 广告组 | 查询 |
| `sb/v3/list/create/update_keywords.py` | 关键词 | 查询/创建/修改 |
| `sb/v3/list/create/update_targets.py` | 商品定向 | 查询/创建/修改 |

V3 仅兼容 Legacy。若参数包含 `campaignStructure:"MULTI_AD_GROUP"` 或 `isMultiAdGroupsEnabled:true`，脚本返回 `SB_V4_CAMPAIGN_NOT_SUPPORTED`。脚本没有本地 Campaign 数据库，因此调用前应先用 V4 Campaign list 确认结构。

### SB V4（20 个）
| 脚本组 | 业务实体 | 操作 |
|------|---------|------|
| `sb/v4/list/create/update_campaigns.py` | 广告活动 | 查询/创建/修改 |
| `sb/v4/list/create/update_ad_groups.py` | 广告组 | 查询/创建/修改 |
| `sb/v4/list/create/update_ads.py` | 广告 | 查询/创建/修改 |
| `sb/v4/list/create/update_keywords.py` | 关键词（Amazon 共享 targeting 路径 `sb/keywords`） | 查询/创建/修改 |
| `sb/v4/list/create/update_targets.py` | 商品定向（Amazon 共享 targeting 路径 `sb/targets[/list]`） | 查询/创建/修改 |
| `sb/v4/list_creatives.py`、`create_creatives.py` | 独立 Creative Version | 按 `adId` 查询/创建新版本 |
| `sb/v4/list/create/update_budget_rules.py` | 预算规则 | 查询/创建/修改 |

原 `scripts/sb/*.py` 继续作为既有 V4 操作的兼容入口（薄封装转发到 `scripts/sb/v4/`）；新调用统一使用带版本目录。完整规则见 [references/api/sb-coexistence.md](./references/api/sb-coexistence.md)。

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
- **Python 脚本**：`python scripts/<脚本名>.py '<JSON 参数>' [--inline]`；SB 新调用必须显式使用 `scripts/sb/v3/` 或 `scripts/sb/v4/`
- **成本约束**：本工具会消耗算力；失败/空结果不得自动换关键词、翻页或连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-amazon-ads-manager-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
- 响应体 ≤ 8 KB：落盘后把完整 JSON 打印到 stdout
- 响应体 > 8 KB：落盘后 stdout 只输出摘要（顶层字段、常见计数如 `total`/`costToken`、最大列表字段的长度 + 前 3 条样本）
- 加 `--inline` 强制全量打印到 stdout（同样落盘）

**读数据建议**：先看摘要判断是否足够；需要具体字段时优先用 `jq`或`ConvertFrom-Json` 从保存的 json 文件按需抽取，避免整份 JSON 进入上下文。

## 解决认证和算力问题
发生以下异常情况时，采用 references/onboarding.md 引导解决问题：

### 异常情况
- **未配置API Key**：环境变量未配置 `LINKFOX_AGENT_API_KEY`，也未配置 `LINKFOXAGENT_API_KEY`。
- **响应401或402状态码**
- **响应提示算力或余额不足**：消息含"算力余额不足/计费不足/余额不足/quota exceeded/insufficient balance/套餐到期/需充值/请充值"，或类似含义的内容。

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
| `fetchAll` | bool | 默认 `true`；SP 与 SB V4 主资源 list 使用 `nextToken`，SB Target/BudgetRule 使用 `nextToken`（BudgetRule 查询必须带 `pageSize`），SB Keyword GET、SB V3 GET 与 SD 使用 `startIndex + count` |
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
  "apiVersion": "V3 | V4",
  "amazonResourceVersion": "V4 | V3_SHARED_TARGETING | SHARED_TARGETING | SHARED",
  "<entityKey>": [ /* 实体数组，字段原样 */ ],
  "total": 157,
  "pagesFetched": 2,
  "truncated": false
}
```

SB 的 `apiVersion` 表示调用入口/结构意图，`amazonResourceVersion` 表示实际 Amazon 资源版本；两者不同不代表发生自动回落。SP productAds 客户端过滤时额外带：`serverTotalBeforeClientFilter` + `clientSideFilters`。

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

### 4. 列 SB V4 广告活动（默认）
```bash
python scripts/sb/v4/list_campaigns.py '{"profileId":1234567890,"region":"NA",
  "stateFilter":{"include":["ENABLED"]}}'
```

### 5. 列某 SB V4 campaign 下的 adGroups / ads
```bash
python scripts/sb/v4/list_ad_groups.py '{"profileId":1234567890,"region":"NA",
  "campaignIdFilter":{"include":["1122334455"]}}'

python scripts/sb/v4/list_ads.py '{"profileId":1234567890,"region":"NA",
  "adGroupIdFilter":{"include":["5566778899"]}}'
```

### 6. 管理 SB V4 campaign 的关键词（共享 targeting 路径）
```bash
python scripts/sb/v4/list_keywords.py '{"profileId":1234567890,"region":"NA",
  "campaignIdFilter":["1122334455"],"adGroupIdFilter":["5566778899"]}'
```

### 7. 查询已确认的 V3 Legacy campaign
```bash
python scripts/sb/v3/list_campaigns.py '{"profileId":1234567890,"region":"NA",
  "campaignStructure":"LEGACY","stateFilter":["enabled","paused"]}'
```

### 8. 列活跃 SD 广告活动
```bash
python scripts/sd/list_campaigns.py '{"profileId":1234567890,"region":"NA",
  "stateFilter":{"include":["ENABLED"]}}'
```

### 9. 按 ASIN 反查 SD 投放（client-side 过滤，带 campaign 收窄）
```bash
python scripts/sd/list_product_ads.py '{"profileId":1234567890,"region":"NA",
  "asinFilter":{"include":["B01ABCDEFG"]},
  "campaignIdFilter":{"include":["998877665544"]}}'
```

### 10. 与 report 配合分析指标
本 skill 返回实体**元数据**（id、名称、状态、匹配类型等）；指标（曝光、点击、花费、转化）交给 `linkfox-amazon-ads-report`（`reportTypeId: "spTargeting"` / `"sbCampaigns"` / `"sdCampaigns"` 等），按 id join。

## 调用原则

- 返回字段原样保留；不改名、不翻译、不补算派生指标
- 非 2xx 不自动重试；保留 `httpStatus` + `body` 告知用户
- `truncated=true` 时明确提示数据未取完

## 常见错误

| 状态 | 含义 | 建议 |
|------|------|------|
| `HTTP 401` | Ads 授权失效或服务端令牌异常 | 停止自动重试，检查授权状态；必要时重新授权 |
| `HTTP 403` | profileId 无权限 | 核对 profileId 归属 |
| `HTTP 400` | 入参结构错 | 先核对"过滤器结构速查"表 |
| `HTTP 429` | 限流 | 等 2-5s 重试 |
| exit 42 | 依赖 skill 未安装 | 先装 `linkfox-amazon-ads-auth` |

## Not Applicable

- 删除 / 归档 → 本 skill 不支持 DELETE（可通过 update state 为 ARCHIVED 实现归档，但归档不可逆）
- SB 不支持把 V4 Multi-Ad-Group Campaign 降级成 V3；V3 独立 Creative CRUD 不存在，Legacy Creative 通过 Campaign payload 管理
- SB negativeKeywords / negativeTargets / themes / recommendations 与 Legacy→V4 Migration 暂不在本次 A+B+C 范围
- SD 的按 id 单查 / brandSafety / recommendations / forecasts / optimizationRules / locations 等"非基础实体"接口 → 不在本 skill
- DSP / ST 实体 → 不在本 skill
- 指标报表 → `linkfox-amazon-ads-report`
- 授权 / token / profile → `linkfox-amazon-ads-auth`

## Amazon Ads API 接口保护与重试指引

同一广告账号/profile 连续收到 Amazon Ads API 的 400、403、404 或 429 时，网关会返回 450、453、454 或 459 并短暂冷却。这些自定义状态码不是 Amazon 原生状态，也不表示封号；目的是避免持续异常或高频调用扩大广告账号风险。

| 状态与 message | 范围 | 触发与冷却 | 处理 |
|---|---|---|---|
| `450`：`400，请求异常，请优化您的参数` | 广告账号/profile+接口 | 60 秒内超过 3 次：5 分钟；10 分钟内超过 4 次：20 分钟 | 停止原参数重试，检查 profileId、region、实体/报告 ID、日期和请求体 |
| `453`：`403，店铺未授权，请先授权` | 广告账号/profile 全部接口 | 60 秒内超过 2 次：5 分钟；10 分钟内超过 4 次：30 分钟 | 停止该广告账号调用，检查 Ads 授权、应用权限、profile 归属和区域 |
| `454`：`404，资源不存在，请优化您的参数` | 广告账号/profile+接口 | 60 秒内超过 3 次：5 分钟；10 分钟内超过 4 次：30 分钟 | 确认资源 ID、所属 profile/区域、资源状态和接口路径 |
| `459`：`429限流中，请降低频率` | 广告账号/profile+接口 | 首次：15 秒；2 分钟内超过 2 次：30 秒；3 分钟内超过 4 次：2 分钟 | 降低并发、分页和轮询频率并逐级退避 |

- 立即停止自动或并发重试，不得通过换脚本或重复创建任务绕过保护；优先遵循 `retryAfter`、`blockedUntil`，没有时按表中时长说明。
- 450/453/454 必须先修正参数、授权或资源标识，冷却后最多谨慎重试一次；再次触发则停止调用。453 期间停止该广告账号/profile 全部 Ads API。
- 保留已有 `reportId` 等任务 ID；写操作结果不确定时先查询状态，不直接重放。
- 向用户先说明广告账号保护，再给原因、处理和等待时间。可回复：“为保护您的亚马逊广告账号安全，检测到 Amazon Ads API 连续返回{原因}，当前已进入短暂保护。请先{处理动作}，预计{等待时间}后再试；这不代表封号，也不是套餐或积分限制。”不要只说“LinkFox 限流”或“服务器繁忙”。

## 算力消耗规则

不消耗算力。

**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `references/api.md`. Do not interrupt the user's flow.


---
*For more high-quality, professional cross-border e-commerce skills, visit [LinkFox Skills](https://skill.linkfox.com/).*
