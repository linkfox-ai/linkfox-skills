---
name: linkfox-amazon-ads-manager
description: 管理已授权亚马逊广告账号的 Sponsored Products、Sponsored Brands 和 Sponsored Display 广告，支持查询、创建、调价、修改预算与状态、否定投放、预算规则及创意管理，兼容 SB 历史 Legacy 与多广告组活动。适用于账户广告实体维护；不适用于指标报表、广告授权、DSP 或 Sponsored Television。
---

# Amazon Ads 广告管理

## 适用范围

### 适用

查询和维护自己已授权广告账号的 SP / SB / SD 实体，包括活动、广告组、关键词、定向、商品广告、否定投放、预算规则以及支持的 Ad / Creative Version。

**场景速查**

| 用户表达 | 查询场景 |
|---|---|
| 看美国站活跃广告，按 ASIN 找投放 | 查询实体与客户端精确筛选。 |
| 调整出价、预算、暂停广告 | 在明确授权范围内修改广告实体。 |
| 给品牌广告新增多个广告组或新创意 | 默认按 SB V4 活动结构处理。 |
| 维护历史 Legacy 品牌广告 | 确认结构后使用 SB V3 兼容能力。 |
| 创建或关联预算规则 | 核对账号、活动及规则后维护。 |

### 边界

曝光、点击、花费、转化等指标交给 `linkfox-amazon-ads-report`，按实体 ID 关联；账号授权交给 `linkfox-amazon-ads-auth`。不覆盖 DSP / ST；其他操作边界见接口参考。

## 接口清单

外层统一 POST；下表 method 是 Amazon 上游方法。共 73 个转发操作，含 79 个版本化业务 CLI；SB 共享资源不重复计数。完整约定见 `references/api.md`。

| 接口 | 端点 | 接口文档 | 对应脚本 | 说明 |
|---|---|---|---|---|
| SP 创建广告组 | POST `/amazonAds/developerProxy` → 上游 POST path：`sp/adGroups` | `references/apis/sp.md` | `scripts/sp/create_ad_groups.py` | 广告组 |
| SP 创建预算规则 | POST `/amazonAds/developerProxy` → 上游 POST path：`sp/budgetRules` | `references/apis/sp.md` | `scripts/sp/create_budget_rules.py` | 预算规则 |
| SP 创建预算规则关联 | POST `/amazonAds/developerProxy` → 上游 POST path：`sp/budgetRulesAssociation` | `references/apis/sp.md` | `scripts/sp/create_budget_rules_association.py` | 预算规则关联 |
| SP 创建活动级否定关键词 | POST `/amazonAds/developerProxy` → 上游 POST path：`sp/campaignNegativeKeywords` | `references/apis/sp.md` | `scripts/sp/create_campaign_negative_keywords.py` | 活动级否定关键词 |
| SP 创建活动级否定定向 | POST `/amazonAds/developerProxy` → 上游 POST path：`sp/campaignNegativeTargets` | `references/apis/sp.md` | `scripts/sp/create_campaign_negative_targets.py` | 活动级否定定向 |
| SP 创建广告活动 | POST `/amazonAds/developerProxy` → 上游 POST path：`sp/campaigns` | `references/apis/sp.md` | `scripts/sp/create_campaigns.py` | 广告活动 |
| SP 创建关键词 | POST `/amazonAds/developerProxy` → 上游 POST path：`sp/keywords` | `references/apis/sp.md` | `scripts/sp/create_keywords.py` | 关键词 |
| SP 创建否定关键词 | POST `/amazonAds/developerProxy` → 上游 POST path：`sp/negativeKeywords` | `references/apis/sp.md` | `scripts/sp/create_negative_keywords.py` | 否定关键词 |
| SP 创建否定定向 | POST `/amazonAds/developerProxy` → 上游 POST path：`sp/negativeTargets` | `references/apis/sp.md` | `scripts/sp/create_negative_targets.py` | 否定定向 |
| SP 创建商品广告 | POST `/amazonAds/developerProxy` → 上游 POST path：`sp/productAds` | `references/apis/sp.md` | `scripts/sp/create_product_ads.py` | 商品广告 |
| SP 创建商品定向 | POST `/amazonAds/developerProxy` → 上游 POST path：`sp/targets` | `references/apis/sp.md` | `scripts/sp/create_targets.py` | 商品定向 |
| SP 查询广告组 | POST `/amazonAds/developerProxy` → 上游 POST path：`sp/adGroups/list` | `references/apis/sp.md` | `scripts/sp/list_ad_groups.py` | 广告组 |
| SP 查询预算规则 | POST `/amazonAds/developerProxy` → 上游 GET path：`sp/budgetRules` | `references/apis/sp.md` | `scripts/sp/list_budget_rules.py` | 预算规则 |
| SP 查询广告活动 | POST `/amazonAds/developerProxy` → 上游 POST path：`sp/campaigns/list` | `references/apis/sp.md` | `scripts/sp/list_campaigns.py` | 广告活动 |
| SP 查询关键词 | POST `/amazonAds/developerProxy` → 上游 POST path：`sp/keywords/list` | `references/apis/sp.md` | `scripts/sp/list_keywords.py` | 关键词 |
| SP 查询否定关键词 | POST `/amazonAds/developerProxy` → 上游 POST path：`sp/negativeKeywords/list` | `references/apis/sp.md` | `scripts/sp/list_negative_keywords.py` | 否定关键词 |
| SP 查询商品广告 | POST `/amazonAds/developerProxy` → 上游 POST path：`sp/productAds/list` | `references/apis/sp.md` | `scripts/sp/list_product_ads.py` | 商品广告 |
| SP 查询商品定向 | POST `/amazonAds/developerProxy` → 上游 POST path：`sp/targets/list` | `references/apis/sp.md` | `scripts/sp/list_targets.py` | 商品定向 |
| SP 修改广告组 | POST `/amazonAds/developerProxy` → 上游 PUT path：`sp/adGroups` | `references/apis/sp.md` | `scripts/sp/update_ad_groups.py` | 广告组 |
| SP 修改预算规则 | POST `/amazonAds/developerProxy` → 上游 PUT path：`sp/budgetRules` | `references/apis/sp.md` | `scripts/sp/update_budget_rules.py` | 预算规则 |
| SP 修改活动级否定关键词 | POST `/amazonAds/developerProxy` → 上游 PUT path：`sp/campaignNegativeKeywords` | `references/apis/sp.md` | `scripts/sp/update_campaign_negative_keywords.py` | 活动级否定关键词 |
| SP 修改活动级否定定向 | POST `/amazonAds/developerProxy` → 上游 PUT path：`sp/campaignNegativeTargets` | `references/apis/sp.md` | `scripts/sp/update_campaign_negative_targets.py` | 活动级否定定向 |
| SP 修改广告活动 | POST `/amazonAds/developerProxy` → 上游 PUT path：`sp/campaigns` | `references/apis/sp.md` | `scripts/sp/update_campaigns.py` | 广告活动 |
| SP 修改关键词 | POST `/amazonAds/developerProxy` → 上游 PUT path：`sp/keywords` | `references/apis/sp.md` | `scripts/sp/update_keywords.py` | 关键词 |
| SP 修改否定关键词 | POST `/amazonAds/developerProxy` → 上游 PUT path：`sp/negativeKeywords` | `references/apis/sp.md` | `scripts/sp/update_negative_keywords.py` | 否定关键词 |
| SP 修改否定定向 | POST `/amazonAds/developerProxy` → 上游 PUT path：`sp/negativeTargets` | `references/apis/sp.md` | `scripts/sp/update_negative_targets.py` | 否定定向 |
| SP 修改商品广告 | POST `/amazonAds/developerProxy` → 上游 PUT path：`sp/productAds` | `references/apis/sp.md` | `scripts/sp/update_product_ads.py` | 商品广告 |
| SP 修改商品定向 | POST `/amazonAds/developerProxy` → 上游 PUT path：`sp/targets` | `references/apis/sp.md` | `scripts/sp/update_targets.py` | 商品定向 |
| SB V4 创建广告组 | POST `/amazonAds/developerProxy` → 上游 POST path：`sb/v4/adGroups` | `references/apis/sb-v4.md` | `scripts/sb/v4/create_ad_groups.py` | 广告组 |
| SB V4 创建广告 | POST `/amazonAds/developerProxy` → 上游 POST path：`sb/v4/ads/{adType}` | `references/apis/sb-v4.md` | `scripts/sb/v4/create_ads.py` | 广告 |
| SB V4 创建预算规则 | POST `/amazonAds/developerProxy` → 上游 POST path：`sb/budgetRules` | `references/apis/sb-v4.md` | `scripts/sb/v4/create_budget_rules.py` | 预算规则 |
| SB V4 创建广告活动 | POST `/amazonAds/developerProxy` → 上游 POST path：`sb/v4/campaigns` | `references/apis/sb-v4.md` | `scripts/sb/v4/create_campaigns.py` | 广告活动 |
| SB V4 创建创意 | POST `/amazonAds/developerProxy` → 上游 POST path：`sb/ads/creatives/{creativeType}` | `references/apis/sb-v4.md` | `scripts/sb/v4/create_creatives.py` | 创意 |
| SB V4 创建关键词 | POST `/amazonAds/developerProxy` → 上游 POST path：`sb/keywords` | `references/apis/sb-v4.md` | `scripts/sb/v4/create_keywords.py`、`scripts/sb/v3/create_keywords.py` | 共享操作 |
| SB V4 创建商品定向 | POST `/amazonAds/developerProxy` → 上游 POST path：`sb/targets` | `references/apis/sb-v4.md` | `scripts/sb/v4/create_targets.py`、`scripts/sb/v3/create_targets.py` | 共享操作 |
| SB V4 查询广告组 | POST `/amazonAds/developerProxy` → 上游 POST path：`sb/v4/adGroups/list` | `references/apis/sb-v4.md` | `scripts/sb/v4/list_ad_groups.py` | 广告组 |
| SB V4 查询广告 | POST `/amazonAds/developerProxy` → 上游 POST path：`sb/v4/ads/list` | `references/apis/sb-v4.md` | `scripts/sb/v4/list_ads.py` | 广告 |
| SB V4 查询预算规则 | POST `/amazonAds/developerProxy` → 上游 GET path：`sb/budgetRules` | `references/apis/sb-v4.md` | `scripts/sb/v4/list_budget_rules.py` | 预算规则 |
| SB V4 查询广告活动 | POST `/amazonAds/developerProxy` → 上游 POST path：`sb/v4/campaigns/list` | `references/apis/sb-v4.md` | `scripts/sb/v4/list_campaigns.py` | 广告活动 |
| SB V4 查询创意 | POST `/amazonAds/developerProxy` → 上游 POST path：`sb/ads/creatives/list` | `references/apis/sb-v4.md` | `scripts/sb/v4/list_creatives.py` | 创意 |
| SB V4 查询关键词 | POST `/amazonAds/developerProxy` → 上游 GET path：`sb/keywords` | `references/apis/sb-v4.md` | `scripts/sb/v4/list_keywords.py`、`scripts/sb/v3/list_keywords.py` | 共享操作 |
| SB V4 查询商品定向 | POST `/amazonAds/developerProxy` → 上游 POST path：`sb/targets/list` | `references/apis/sb-v4.md` | `scripts/sb/v4/list_targets.py`、`scripts/sb/v3/list_targets.py` | 共享操作 |
| SB V4 修改广告组 | POST `/amazonAds/developerProxy` → 上游 PUT path：`sb/v4/adGroups` | `references/apis/sb-v4.md` | `scripts/sb/v4/update_ad_groups.py` | 广告组 |
| SB V4 修改广告 | POST `/amazonAds/developerProxy` → 上游 PUT path：`sb/v4/ads` | `references/apis/sb-v4.md` | `scripts/sb/v4/update_ads.py` | 广告 |
| SB V4 修改预算规则 | POST `/amazonAds/developerProxy` → 上游 PUT path：`sb/budgetRules` | `references/apis/sb-v4.md` | `scripts/sb/v4/update_budget_rules.py` | 预算规则 |
| SB V4 修改广告活动 | POST `/amazonAds/developerProxy` → 上游 PUT path：`sb/v4/campaigns` | `references/apis/sb-v4.md` | `scripts/sb/v4/update_campaigns.py` | 广告活动 |
| SB V4 修改关键词 | POST `/amazonAds/developerProxy` → 上游 PUT path：`sb/keywords` | `references/apis/sb-v4.md` | `scripts/sb/v4/update_keywords.py`、`scripts/sb/v3/update_keywords.py` | 共享操作 |
| SB V4 修改商品定向 | POST `/amazonAds/developerProxy` → 上游 PUT path：`sb/targets` | `references/apis/sb-v4.md` | `scripts/sb/v4/update_targets.py`、`scripts/sb/v3/update_targets.py` | 共享操作 |
| SB V3 Legacy 创建广告活动 | POST `/amazonAds/developerProxy` → 上游 POST path：`sb/campaigns` | `references/apis/sb-v3.md` | `scripts/sb/v3/create_campaigns.py` | 广告活动 |
| SB V3 Legacy 查询广告组 | POST `/amazonAds/developerProxy` → 上游 GET path：`sb/adGroups` | `references/apis/sb-v3.md` | `scripts/sb/v3/list_ad_groups.py` | 广告组 |
| SB V3 Legacy 查询广告活动 | POST `/amazonAds/developerProxy` → 上游 GET path：`sb/campaigns` | `references/apis/sb-v3.md` | `scripts/sb/v3/list_campaigns.py` | 广告活动 |
| SB V3 Legacy 修改广告活动 | POST `/amazonAds/developerProxy` → 上游 PUT path：`sb/campaigns` | `references/apis/sb-v3.md` | `scripts/sb/v3/update_campaigns.py` | 广告活动 |
| SD 创建广告组 | POST `/amazonAds/developerProxy` → 上游 POST path：`sd/adGroups` | `references/apis/sd.md` | `scripts/sd/create_ad_groups.py` | 广告组 |
| SD 创建预算规则 | POST `/amazonAds/developerProxy` → 上游 POST path：`sd/budgetRules` | `references/apis/sd.md` | `scripts/sd/create_budget_rules.py` | 预算规则 |
| SD 创建广告活动 | POST `/amazonAds/developerProxy` → 上游 POST path：`sd/campaigns` | `references/apis/sd.md` | `scripts/sd/create_campaigns.py` | 广告活动 |
| SD 创建创意 | POST `/amazonAds/developerProxy` → 上游 POST path：`sd/creatives` | `references/apis/sd.md` | `scripts/sd/create_creatives.py` | 创意 |
| SD 创建否定定向 | POST `/amazonAds/developerProxy` → 上游 POST path：`sd/negativeTargets` | `references/apis/sd.md` | `scripts/sd/create_negative_targets.py` | 否定定向 |
| SD 创建商品广告 | POST `/amazonAds/developerProxy` → 上游 POST path：`sd/productAds` | `references/apis/sd.md` | `scripts/sd/create_product_ads.py` | 商品广告 |
| SD 创建商品定向 | POST `/amazonAds/developerProxy` → 上游 POST path：`sd/targets` | `references/apis/sd.md` | `scripts/sd/create_targets.py` | 商品定向 |
| SD 查询广告组 | POST `/amazonAds/developerProxy` → 上游 GET path：`sd/adGroups；扩展：sd/adGroups/extended` | `references/apis/sd.md` | `scripts/sd/list_ad_groups.py` | 广告组 |
| SD 查询预算规则 | POST `/amazonAds/developerProxy` → 上游 GET path：`sd/budgetRules` | `references/apis/sd.md` | `scripts/sd/list_budget_rules.py` | 预算规则 |
| SD 查询广告活动 | POST `/amazonAds/developerProxy` → 上游 GET path：`sd/campaigns；扩展：sd/campaigns/extended` | `references/apis/sd.md` | `scripts/sd/list_campaigns.py` | 广告活动 |
| SD 查询创意 | POST `/amazonAds/developerProxy` → 上游 GET path：`sd/creatives` | `references/apis/sd.md` | `scripts/sd/list_creatives.py` | 创意 |
| SD 查询否定定向 | POST `/amazonAds/developerProxy` → 上游 GET path：`sd/negativeTargets；扩展：sd/negativeTargets/extended` | `references/apis/sd.md` | `scripts/sd/list_negative_targets.py` | 否定定向 |
| SD 查询商品广告 | POST `/amazonAds/developerProxy` → 上游 GET path：`sd/productAds；扩展：sd/productAds/extended` | `references/apis/sd.md` | `scripts/sd/list_product_ads.py` | 商品广告 |
| SD 查询商品定向 | POST `/amazonAds/developerProxy` → 上游 GET path：`sd/targets；扩展：sd/targets/extended` | `references/apis/sd.md` | `scripts/sd/list_targets.py` | 商品定向 |
| SD 修改广告组 | POST `/amazonAds/developerProxy` → 上游 PUT path：`sd/adGroups` | `references/apis/sd.md` | `scripts/sd/update_ad_groups.py` | 广告组 |
| SD 修改预算规则 | POST `/amazonAds/developerProxy` → 上游 PUT path：`sd/budgetRules` | `references/apis/sd.md` | `scripts/sd/update_budget_rules.py` | 预算规则 |
| SD 修改广告活动 | POST `/amazonAds/developerProxy` → 上游 PUT path：`sd/campaigns` | `references/apis/sd.md` | `scripts/sd/update_campaigns.py` | 广告活动 |
| SD 修改创意 | POST `/amazonAds/developerProxy` → 上游 PUT path：`sd/creatives` | `references/apis/sd.md` | `scripts/sd/update_creatives.py` | 创意 |
| SD 修改否定定向 | POST `/amazonAds/developerProxy` → 上游 PUT path：`sd/negativeTargets` | `references/apis/sd.md` | `scripts/sd/update_negative_targets.py` | 否定定向 |
| SD 修改商品广告 | POST `/amazonAds/developerProxy` → 上游 PUT path：`sd/productAds` | `references/apis/sd.md` | `scripts/sd/update_product_ads.py` | 商品广告 |
| SD 修改商品定向 | POST `/amazonAds/developerProxy` → 上游 PUT path：`sd/targets` | `references/apis/sd.md` | `scripts/sd/update_targets.py` | 商品定向 |

## 前置条件

依赖 `linkfox-amazon-ads-auth`。运行 `python scripts/check_auth_dependency.py --json` 本地检查安装情况；授权与目标账号仍由认证技能解析。先确定用户站点、广告账号和待维护实体，按任务读取相应接口定义及 SB 共存规则。

## 操作流程

1. 先使用 `linkfox-amazon-ads-auth` 的 `authorized_stores.py` 获取账号 × 站点清单，按用户站点映射 `countryCode`（如美国→US）。仅一个候选时静默取其 profile；同站点两个以上候选时用 `accountName` 请用户选账号；没有候选时引导授权。不得让用户报数字 profileId，也不得在歧义下挑首项或默认账号；不向用户播报内部数字。
2. 确认广告产品和任务范围。SB 新业务、多广告组、Ad 和 Creative 默认 V4；关键词与定向也默认 V4 入口。只有已确认 Legacy 或用户明确要求 V3 才使用 V3；必要时先读 V4 活动结构，不以调用失败作为切换版本的理由。
3. 按接口参考准备查询或原生写入内容，使用对应业务脚本保留过滤、分页及聚合。业务 CLI 不读写响应缓存；同一会话同一参数避免重复调用；失败、空结果不擅自换条件或扩大分页试探，需扩大查询范围时先说明。
4. 写操作按下述授权决策执行。已有明确授权即执行并回执；尚未授权先提供具体变更摘要。结果不确定时先查询状态，不直接重放。按接口定义检查外层、网关、上游与逐项结果。
5. 用保存的数据展示实体和操作结果；说明已取范围及未取完的数据。认证、用量或账号保护错误按对应参考停止和处理。

### 写入授权与回执

创建和更新操作可能直接影响广告花费，立即生效且无法撤回。

**写入授权决策：**

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

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **脚本调用（推荐）**：`python <脚本路径> '<JSON 参数>' [--inline] [--no-cache]`。
- **调用约束**：业务脚本关闭响应缓存，同一会话、同一参数组合避免重复调用。失败或空结果时，不得自动更换条件、扩大分页或连续试探；按接口规则排查，需扩大查询范围时先向用户说明。

### 输出策略

- 始终保存完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-amazon-ads-manager-<timestamp>.json`。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，用于聚合同一任务的数据。禁止写入 `/tmp`，当前目录不可写时应报错。
- 响应体的 UTF-8 编码长度不超过 8,000 字节：保存后，将完整 JSON 打印到标准输出。
- 响应体的 UTF-8 编码长度超过 8,000 字节：保存后，标准输出仅展示摘要，包括顶层字段、常见计数（如 `total`、上游返回的 `costToken`）、最大列表字段的长度和前 3 条样本。
- 添加 `--inline` 可强制全量打印到标准输出，同时仍保存文件。

先通过摘要判断数据是否足够。需要具体字段时，优先使用 `jq` 或 `ConvertFrom-Json` 从保存的 JSON 文件按需提取，避免将整份响应载入上下文。

## 执行规则

### 算力消耗预估

不消耗算力 （限时）。

**声明**：算力消耗以实际扣除为准；如因需要调整算力消耗标准，恕不另行通知。最终解释权归 LinkFox 官方所有。

### 解决认证和算力问题

出现以下情况时，按 `references/onboarding.md` 的指引处理：

- 未配置接口密钥：`LINKFOX_AGENT_API_KEY` 和 `LINKFOXAGENT_API_KEY` 均为空。
- HTTP 状态码为 `401` 或 `402`。
- 响应提示算力或余额不足、计费不足、配额超限、套餐到期或需要充值。英文错误消息也按其含义判断。

### 约束与建议

- **清晰展示数据**：先注明账号、站点、广告产品与 SB 版本；表格展示实体 ID、名称、状态、匹配方式等可用字段。返回字段原样保留，不改名、不翻译、不补算派生指标。
- **元数据与指标**：本技能返回实体元数据；指标使用 `linkfox-amazon-ads-report`，按 ID 关联，不把实体数解释为广告表现；报表类型示例见 `references/api.md`。
- **自动分页与客户端过滤**：业务脚本保留分页和格式规范化；具体模式与限制见相应接口。SP / SD 按 ASIN / SKU 筛选在本地精确匹配，建议先缩小活动或广告组范围；数据截断时明确告知。
- **SB 版本概念**：入口版本表示结构意图，资源版本表示实际 Amazon 资源；共享 Keyword/Target 路径不代表自动降级。不得把多广告组数据经 V3 静默截断。Creative Version 支持按 Ad 查询和创建新版本，不宣称通用更新或完整 CRUD；详见 `references/apis/sb-coexistence.md`。
- **错误展示**：保留上游状态与原始响应，解释具体原因；遇到账号保护先说明保护账号的目的，再给修正动作和等待时间，完整阈值见 `references/ads-protection.md`。


## 使用示例

### 查询 SP 或 SD 广告

用户：看看美国站活跃广告，并找出这个 ASIN 的投放。

解析唯一账号或用账号名称澄清，按活动范围查询并按 ASIN 本地筛选，展示实体和本次数据范围。

### 管理 SB 活动与创意

用户：给这个品牌广告增加广告组，再创建新创意版本。

核对账号与活动结构，默认走 V4，按已有授权准备变更并提交，展示逐项结果，不切到 V3 重试。

### 修改出价、预算或状态

用户：把这几个关键词按我给出的价格调整，并暂停指定活动。

核对目标和明确变更；用户已经授权时执行并回执，未授权时先给具体摘要。归档不可逆，不能与暂停混淆。

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。
