---
name: linkfox-wb-amazon-ads
display_name: LinkFox 亚马逊广告
display_name_en: LinkFox Amazon Ads
description: 面向 Amazon Ads 的账号授权、广告实体管理、标准效果报告与 Sponsored Products 洞察报告能力。
description_zh: 面向亚马逊广告运营的统一 WorkBuddy 能力。完成广告账号授权与站点选择，查询及创建/修改 SP、SB、SD 广告实体，获取标准广告指标报告，并获取 SP 受众与搜索词展示份额/排名洞察。支持 profileId 解析、分页和异步报告状态管理；不覆盖 Amazon DSP、Sponsored Television、Brand Analytics、Retail Analytics 或法律/经营结论。
description_en: A unified WorkBuddy capability for Amazon Ads operations. authorize ad accounts and resolve marketplace profiles, query and create/update SP, SB, and SD entities, retrieve standard performance reports, and obtain SP audience and search-term impression-share/rank insights. It supports profile resolution, pagination, and asynchronous report state management; it does not cover Amazon DSP, Sponsored Television, Brand Analytics, Retail Analytics, or legal/business conclusions.
icon: icons/logo.png
version: 2.1.0
author: Linkfox
---

> [!IMPORTANT]
本 Skill 必须依赖 MCP “LinkFox”。如未安装该MCP，请明确通知用户：
> 请先安装 LinkFox 连接器：
> - 在 WorkBuddy 左侧找到 “专家·技能·连接器” → “连接器”；
> - 搜索关键词 “LinkFox”，并安装连接器 “LinkFox”（注意：是 linkfox，不是 linkfox-product-selection），按指引完成登录授权；
> - 返回 WorkBuddy 重试。


# LinkFox 亚马逊广告

本 skill 统一处理 Amazon Ads 账号授权、SP/SB/SD 实体管理、标准报告和 SP v1 洞察报告。所有工具网关业务调用只能通过 WorkBuddy 的 LinkFox MCP 执行。

## MCP 契约

- MCP server：`LinkFox`
- 唯一工具：`proxy_call`
- 调用结构：`{"toolName":"<endpoint 去掉前导 / 的精确值>","arguments":{...}}`
- `toolName` 区分大小写，必须精确匹配下列 allowlist：
  - `amazonAds/authorizeUrl`
  - `amazonAds/authorizedStores`
  - `amazonAds/profiles`
  - `amazonAds/refreshToken`
  - `amazonAds/storeTokens`
  - `amazonAds/developerProxy`
- WorkBuddy 自动注入 Authorization。MCP 配置、文档和 `arguments` 中都不得加入 `headers`、API Key、token、JWT、手机号或其他凭证。
- 禁止用 curl、`urllib`、`requests`、`httpx` 或其他方式直连 `tool-gateway.linkfox.com`；MCP 或 `proxy_call` 缺失时停止，不得静默 HTTP fallback。
- 原请求体直接作为 `arguments`，不得额外包裹 `body`、`params`、`data` 或第二层 `arguments`。共享 `developerProxy` 的业务路由字段 `region`、`path`、`method`、`profileId`、`body`、`contentType` 仍保留在 `arguments` 中。
- 同一任务内相同 `toolName + arguments` 只调用一次。收费调用失败、空结果或结果不理想时不得自动重试、换账号、扩日期或改参数。
- 先检查 MCP schema、`isError` 和代理层错误；代理成功后读取 structured/text content，text 是 JSON 字符串时只解析一次；再检查下游 `errcode`、`errorCode`、`code`、`errmsg`、`msg` 或 developerProxy 的 `httpStatus/body`。

MCP 配置缺失时使用：

```json
{
  "mcpServers": {
    "LinkFox": {
      "type": "streamableHttp",
      "url": "https://mcp-tool-gateway.linkfox.com/mcp/any-tool"
    }
  }
}
```

## 能力路由

| 子能力 | 业务范围 | reference | toolName | 本地脚本 |
|---|---|---|---|---|
| Ads Auth | 授权 URL、账号×站点、profiles、刷新和状态 | `references/auth_api.md` | 对应 5 个 `amazonAds/*` 精确值 | 无 |
| Ads Manager | SP/SB/SD 查询、创建、修改、预算规则 | `references/manager_api.md` 及产品 reference | `amazonAds/developerProxy` | 无 |
| Standard Reports | 22 类 SP/SB/SD 报告的创建、状态查询 | `references/report_api.md` 与 `references/report_types_*.md` | `amazonAds/developerProxy` | 无 |
| SP Insights | Audience、Search Term Impression Share/Rank | `references/insights_api.md` 与两个专项 reference | `amazonAds/developerProxy` | 无 |

每个业务 reference 的“`MCP 调用`”章节给出精确 `toolName`、arguments 和响应契约。报告类型 reference 仅定义该报告的合法配置和完整列集合，传输契约统一读取 `report_api.md`。

## 选择规则

- 授权、列站点或检查授权状态：Ads Auth。生成授权 URL 前必须取得非空 `accountName`；一次授权可能产生多个 marketplace profile。
- campaign、ad group、广告、关键词、否定项、target、creative 或预算规则的元数据查询/变更：Ads Manager。它不返回曝光、点击、花费、销售或转化指标。
- 常规 SP/SB/SD 指标：Standard Reports。按用户目标选择 `reportTypeId`，从对应 `report_types_*.md` 取得合法 `adProduct`、`groupBy`、`columns`、`timeUnit`、过滤器和日期限制。
- 明确的 SP Audience 或搜索词 impression share/rank：SP Insights。普通搜索词表现仍用标准报告 `spSearchTerm`；洞察不得追加 campaign、adGroup、target、keyword 或自定义 fields。
- SB 新活动、多广告组、广告和 creative 默认 V4。V4 失败不得自动切换 V3；只有确认 Legacy 或用户明确要求时用 V3。`MULTI_AD_GROUP` 或 `isMultiAdGroupsEnabled=true` 必须拒绝 V3。关键词和商品定向继续使用共享 targeting 资源。

## 账号与凭证保护

- 用户只给站点或店铺名称时，先以 `amazonAds/authorizedStores` 根据 `accountName`、`countryCode` 解析。唯一匹配可选择；同站点多账号必须让用户确认，不能猜测。
- 正常交互不要要求用户手填 `profileId`。`profileId` 与 `region`（`NA` / `EU` / `FE`）确定后再调用 manager/report/insights。
- access token、refresh token、LWA 密钥和内部授权记录不得展示或传入 `developerProxy`。`storeTokens` 只用于状态检查，不得把返回凭证交给用户或用于业务 arguments。
- MCP 连接 401：提示用户重新登录 WorkBuddy、重载连接，仍失败则联系 WorkBuddy 管理员；不得要求用户手工填写 MCP Authorization。
- 代理成功但下游 JSON 为 401：按 WorkBuddy 自动授权或 Amazon Ads 下游授权失败处理，可用既有授权操作检查/刷新；不得把 Key/token 放入 `arguments`。
- 下游 402 或积分不足：引导访问 `https://agent.linkfox.com/`；不得自动选套餐、下单、支付或轮询。403 按对应业务权限处理，不得归类为 401/402。

详细恢复规则见 `references/onboarding.md`。Feedback API 与工具网关分离，不迁移到 MCP，也不得在未获用户请求时自动调用。

## 写操作安全门

创建、修改、调价、改预算、改状态、归档和关联预算规则可能立即影响投放与花费，且部分操作不可撤回：

1. 执行前展示操作类型、实体数量/ID、关键字段变化、预算或状态影响。
2. 必须等待用户明确确认；已有明确的“确认执行/无需再次确认”指令除外。
3. 确认后只调用一次，不因超时、空结果或回执不理想重复提交。
4. 执行后展示成功数、失败数、范围、变化和失败实体；不得掩盖部分失败。

## 报告状态机

- 标准报告通过 `amazonAds/developerProxy` 调用 `POST /reporting/reports` 创建，再调用 `GET /reporting/reports/{reportId}` 查询；洞察按专项 reference 依次调用 `adsApi/v1/query/advertiserAccounts`、`adsApi/v1/create/reports`、`adsApi/v1/retrieve/reports`。
- `PENDING` / `PROCESSING` 不是失败。继续前告知用户并取得确认，始终复用原 `reportId`；禁止重新创建同一报告。
- `COMPLETED` 后若响应含预签名下载 URL，可向用户返回该资源链接。旧脚本提供的本地下载、解压、CSV/JSON 落盘、临时 HTTP 服务和 24 小时缓存已随 HTTP 脚本移除，新 MCP 链路不承诺这些能力。
- 成功空报告是合法结果，不扩大日期、切换账号或改字段重试。
- Reporting API v1 属 open beta，不承诺 GA 稳定性；403 可能表示账号未开放相应权限。

## 分页与结果展示

- 按各 reference 的 `nextToken`、`nextPageToken`、offset/limit 约束分页。每次下一页都是不同 arguments 的收费调用；先展示已取数量并征得用户同意，避免无界拉取。
- 保留 Amazon 原始字段和 ID；数据缺失写“未返回”，不要补猜。
- 实体结果说明其为 metadata；报告结果说明 reportType、日期、状态和可用资源。结论只基于返回数据，不做法律、侵权或确定性经营承诺。

## 边界

不支持 Amazon DSP、Sponsored Television、Brand Analytics、Retail Analytics、Attribution、订单/库存/财务、广告删除接口、定时任务、法律意见、侵权结论或自动化经营决策。
