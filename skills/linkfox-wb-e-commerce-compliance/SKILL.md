---
name: linkfox-wb-e-commerce-compliance
display_name: LinkFox 电商合规检测
display_name_en: LinkFox E-commerce Compliance Detection
description: 面向电商上架与产品合规审查的专利检索、核验、比对和证据整理能力。
description_zh: 面向电商上架、产品开发和风险复核的专利合规检测能力，支持按专利号或检索式获取著录、全文、翻译、附图、法律状态、家族、引用、PDF，并支持基于产品图片检索外观或实用新型专利；返回可核验的专利记录、筛选结果、状态与引用证据。涉及侵权结论、自由实施意见或法律意见时仅提供数据依据并提示咨询专业人士。用户需要专利风险排查、专利信息核验、产品图片找相似专利、专利全文翻译或合规证据整理时触发。完整参数见 references/，业务调用通过 Linkfox LinkFox MCP 执行。
description_en: Patent-oriented e-commerce compliance detection for product launch, sourcing, and risk review. Retrieve and compare bibliographic records, search-expression results, claims, descriptions, translations, drawings, legal status, families, citations, and PDFs; search similar design or utility-model patents from a product image; and return auditable records and evidence. Provide factual data rather than legal infringement, FTO, litigation, or legal advice, and recommend professional counsel for legal conclusions. Trigger for patent risk checks, patent verification, image-based patent discovery, patent full-text translation, or compliance evidence preparation. Full parameters are in references/ and business calls use Linkfox LinkFox MCP.
icon: icons/logo.png
version: 1.2.0
author: Linkfox
---

> [!IMPORTANT]
本 Skill 必须依赖 MCP “LinkFox”。如未安装该MCP，请明确通知用户：
> 请先安装 LinkFox 连接器：
> - 在 WorkBuddy 左侧找到 “专家·技能·连接器” → “连接器”；
> - 搜索关键词 “LinkFox”，并安装连接器 “LinkFox”（注意：是 linkfox，不是 linkfox-product-selection），按指引完成登录授权；
> - 返回 WorkBuddy 重试。


# LinkFox 电商合规检测（LinkFox E-commerce Compliance Detection）

面向电商产品上架、选品和合规复核，提供从“发现相似专利”到“核验专利状态与权利范围”的连续数据工作流。可按公开号、内部专利 ID、检索式或产品图片调用相应操作，输出结构化专利记录、全文资料、图片地址、法律事件、家族与引用证据。

本能力包含 17 个子能力、17 个 API operation：基础与详细著录、检索式发现、权利要求与说明书（含翻译）、摘要与全文附图、法律状态、专利家族、被引用与参考文献、PDF，以及外观/实用新型图片检索。每个子能力的完整参数、响应字段、错误码和限制见对应 reference。

## 能力边界

### 能力范围

- **按专利号核验基本信息**：使用 `linkfox-simple-bibliography` 获取标题、摘要、申请人、发明人、分类号、日期和引用字段；需要完整分类、优先权或到期信息时使用 `linkfox-bibliography`。
- **发现相关专利**：使用 `linkfox-retrieval-patent-search` 按 Analytics 检索式、排序、分页和家族去重发现候选专利；它只返回检索列表，详情需再用著录或全文操作核验。
- **按产品图片找相似专利**：使用 `linkfox-patent-image-search` 检索外观设计，或 `linkfox-utility-patent-image-search` 检索实用新型；本地图片先用 `scripts/upload_image.py` 转为可公开访问 URL。
- **核对权利要求与说明书**：使用 `linkfox-claim-data`、`linkfox-claim-data-translated`、`linkfox-description-data` 和 `linkfox-description-data-translated` 获取原文或中/英/日翻译，用于产品特征与权利要求的人工比对。
- **读取专利图纸与摘要图**：使用 `linkfox-abstract-image` 获取摘要附图，使用 `linkfox-fulltext-image` 获取全文附图及图纸路径。
- **复核存续与关联关系**：使用 `linkfox-legal-status` 查看法律状态和事件历史，使用 `linkfox-patent-family` 查看简单同族与跨国同族。
- **整理引用证据与文件**：使用 `linkfox-patent-cited` 查看被引用次数和引用专利，使用 `linkfox-patent-forward-citation` 查看本专利引用的专利/非专利文献，使用 `linkfox-pdf-data` 获取单篇或批量 PDF 链接。

### 边界与限制

- 所有业务调用均由 WorkBuddy 自动授权；各 operation 可能独立计费、限频和受套餐权限限制。
- 图片检索只接受可公开访问的图片 URL；上传脚本生成的 URL 有效期有限，不能把本地路径直接作为检索参数。
- 检索式必须是有效 Analytics 表达式；分页、扩大 limit、改写表达式或重复同参调用都可能产生额外消耗，不能在空结果或报错后自动试探。
- 图片检索中的 `D`/model 1–2 只对应外观设计，`U`/model 3–4 只对应实用新型；不得交叉填写。
- 数据仅反映数据库返回的记录和更新时间，不能单独证明侵权、不侵权、有效性、FTO 或诉讼结果；法律结论、权利范围解释和诉讼策略须由专业人士完成。
- 不办理专利申请、注册、年费、许可谈判或权利人沟通；不执行店铺运营、广告、物流、供应链和非专利类版权/商标检测。

## 工具选择指南

| 需求 / 用户说 | 默认推荐 | 何时换用其他 |
|---|---|---|
| “找与这张产品图相似的外观专利” | `linkfox-patent-image-search` | 目标是实用新型时换 `linkfox-utility-patent-image-search`；需要风险判定而非相似列表时仍应先取得记录再人工复核 |
| “用图片找相似实用新型专利” | `linkfox-utility-patent-image-search` | 目标是外观设计时换 `linkfox-patent-image-search` |
| “查这个公开号是谁申请、何时公开” | `linkfox-simple-bibliography` | 需要完整分类、优先权、同族线索时换 `linkfox-bibliography` |
| “查完整专利信息/优先权/到期日” | `linkfox-bibliography` | 只需标题、摘要、申请人和发明人时用轻量的 `linkfox-simple-bibliography` |
| “按关键词/检索式发现专利” | `linkfox-retrieval-patent-search` | 已知专利号时不要用检索式发现，直接走著录操作 |
| “看权利要求” | `linkfox-claim-data` | 需要翻译时换 `linkfox-claim-data-translated` |
| “看说明书/全文” | `linkfox-description-data` | 需要翻译时换 `linkfox-description-data-translated`；只要文件下载时换 `linkfox-pdf-data` |
| “翻译摘要、权利要求或说明书” | 对应的 `*-translated` 操作 | 先判断用户需要的文本层级，不要用摘要翻译替代权利要求或说明书翻译 |
| “这项专利还有效吗” | `linkfox-legal-status` | 需要跨国等同关系时再加 `linkfox-patent-family` |
| “它被谁引用/它引用了什么” | 被引用用 `linkfox-patent-cited`；引用了什么用 `linkfox-patent-forward-citation` | 两者语义相反，按用户的主语和方向选择 |
| “下载专利 PDF/批量下载” | `linkfox-pdf-data` | 需要可检索文本时另取 claims/description，PDF 链接本身不替代结构化字段 |
| “看专利图纸” | `linkfox-abstract-image` | 需要全部图纸时换 `linkfox-fulltext-image` |

选择时先判断输入类型（专利号、检索式或图片）和输出目的（发现、核验、比对或下载），再按所需字段选择最小 operation。多个操作都可满足时优先使用返回范围更小、成本更低的操作；需要扩展结果或追加证据时先说明可能产生的额外积分，由用户决定。

## 业务需求路由速查

| 子能力 | 业务能力 | reference | 精确 `toolName` | 本地 helper |
|---|---|---|---|---|
| `linkfox-abstract-image` | 获取摘要附图 | `references/linkfox-abstract-image.md` | `zhihuiya/abstractImage` | — |
| `linkfox-abstract-data-translated` | 标题与摘要翻译 | `references/linkfox-abstract-data-translated.md` | `zhihuiya/abstractDataTranslated` | — |
| `linkfox-bibliography` | 详细著录信息 | `references/linkfox-bibliography.md` | `zhihuiya/bibliography` | — |
| `linkfox-patent-cited` | 被引用统计与列表 | `references/linkfox-patent-cited.md` | `zhihuiya/patentCited` | — |
| `linkfox-patent-forward-citation` | 参考文献/在先技术 | `references/linkfox-patent-forward-citation.md` | `zhihuiya/patentForwardCitation` | — |
| `linkfox-claim-data` | 权利要求原文 | `references/linkfox-claim-data.md` | `zhihuiya/claimData` | — |
| `linkfox-claim-data-translated` | 权利要求翻译 | `references/linkfox-claim-data-translated.md` | `zhihuiya/claimDataTranslated` | — |
| `linkfox-description-data` | 说明书原文 | `references/linkfox-description-data.md` | `zhihuiya/descriptionData` | — |
| `linkfox-description-data-translated` | 说明书翻译 | `references/linkfox-description-data-translated.md` | `zhihuiya/descriptionDataTranslated` | — |
| `linkfox-fulltext-image` | 全文附图 | `references/linkfox-fulltext-image.md` | `zhihuiya/fulltextImage` | — |
| `linkfox-legal-status` | 法律状态与事件 | `references/linkfox-legal-status.md` | `zhihuiya/legalStatus` | — |
| `linkfox-patent-family` | 专利家族 | `references/linkfox-patent-family.md` | `zhihuiya/patentFamily` | — |
| `linkfox-patent-image-search` | 外观设计以图检索 | `references/linkfox-patent-image-search.md` | `zhihuiya/patentImageSearch` | `scripts/upload_image.py`（仅本地图片时） |
| `linkfox-utility-patent-image-search` | 实用新型以图检索 | `references/linkfox-utility-patent-image-search.md` | `zhihuiya/patentImageSearch` | `scripts/upload_image.py`（仅本地图片时） |
| `linkfox-pdf-data` | 专利 PDF 链接 | `references/linkfox-pdf-data.md` | `zhihuiya/pdfData` | — |
| `linkfox-retrieval-patent-search` | 检索式发现专利 | `references/linkfox-retrieval-patent-search.md` | `zhihuiya/querySearchPatent` | — |
| `linkfox-simple-bibliography` | 简要著录信息 | `references/linkfox-simple-bibliography.md` | `zhihuiya/simpleBibliography` | — |
| 本地图片上传 | 获取对象存储预签名 URL | 两个图片检索 reference | `oss/file/presignedPut` | `scripts/upload_image.py`（仅 PUT 预签名 URL） |

## MCP 调用方式

MCP server 为 `LinkFox`（`https://mcp-tool-gateway.linkfox.com/mcp/any-tool`），唯一工具为 `proxy_call`。允许的精确 `toolName` 如下；外观与实用新型共用 `zhihuiya/patentImageSearch`：

`zhihuiya/abstractImage`、`zhihuiya/abstractDataTranslated`、`zhihuiya/bibliography`、`zhihuiya/patentCited`、`zhihuiya/patentForwardCitation`、`zhihuiya/claimData`、`zhihuiya/claimDataTranslated`、`zhihuiya/descriptionData`、`zhihuiya/descriptionDataTranslated`、`zhihuiya/fulltextImage`、`zhihuiya/legalStatus`、`zhihuiya/patentFamily`、`zhihuiya/patentImageSearch`、`zhihuiya/pdfData`、`zhihuiya/querySearchPatent`、`zhihuiya/simpleBibliography`、`oss/file/presignedPut`。

```json
{"toolName":"zhihuiya/querySearchPatent","arguments":{"queryText":"TACD: virtual reality","limit":10,"offset":0}}
```

`toolName` 是原 endpoint 去掉前导斜杠后的精确值，区分大小写；请求参数对象直接作为 `arguments`。WorkBuddy 自动注入 Authorization，禁止增加 headers、API Key、token、JWT、手机号或其他凭证。禁止 curl、`urllib`、`requests`、`httpx` 或脚本直连工具网关；MCP 缺失时禁止 HTTP fallback。

收费调用失败、空结果或结果不理想时不得自动重试；同一任务内相同 `toolName + arguments` 不重复调用。先检查 MCP/schema/`isError`，再读取 structured content 或只解析一次 text JSON，之后检查下游业务错误，最后按 reference 的响应字段表读取结果。MCP 不提供旧 wrapper 的 24 小时缓存、自动落盘或 stdout 摘要。


本地图片采用两阶段流程：先以 `oss/file/presignedPut` 获取 URL，再由 `scripts/upload_image.py` 仅向该预签名对象存储 URL PUT 文件。PDF 和附图下载地址按响应展示，不声称自动下载或落盘。

## 使用示例

### 1. 按检索式发现候选专利

```json
{"queryText":"TACD: virtual reality","limit":10,"sort":[{"field":"SCORE","order":"DESC"}],"collapseType":"DOCDB","collapseBy":"APD","collapseOrder":"LATEST"}
```

调用 `zhihuiya/querySearchPatent`。重点展示 `allRecordsCount`、当前页、`pn`、`title`、日期、`inventor`、`currentAssignee` 和 `costToken`；`limit + offset` 不得超过 20000，翻页前提醒消耗。

### 2. 用图片检索外观设计或实用新型

外观设计：

```json
{"url":"https://example.com/product-image.jpg","patentType":"D","model":1,"country":"CN,US","limit":20,"lang":"cn","field":"SCORE","order":"desc"}
```

实用新型：

```json
{"url":"https://example.com/product-image.jpg","patentType":"U","model":3,"country":"CN,US","limit":20,"lang":"cn","field":"SCORE","order":"desc"}
```

两者均调用 `zhihuiya/patentImageSearch`，但必须分别使用正确的 `patentType` 与 model。重点展示 `patentPn`、`title`、`score`、`authority`、`loc`、申请/公开日和图片 URL；URL 必须公开可访问，图片检索只返回相似记录，不自动下侵权结论。

### 3. 核验单篇专利的著录、状态与家族

```json
{"patentNumber":"US20230012345A1"}
```

将该参数分别用于 `zhihuiya/simpleBibliography`、需要完整字段时的 `zhihuiya/bibliography`、`zhihuiya/legalStatus` 和 `zhihuiya/patentFamily`。优先展示标题、公开号、申请人、发明人、申请/公开日、主要分类、状态事件和家族成员；空字段省略，多个调用的 `costToken` 分开标注。

### 4. 读取权利要求、说明书及翻译

```json
{"patentNumber":"CN115000000A","lang":"en"}
```

著录类接口通常支持 `patentId` 或 `patentNumber` 二选一；具体语言字段、返回层级和批量上限以对应 reference 为准。需要权利要求时调用 `zhihuiya/claimData` 或 `zhihuiya/claimDataTranslated`，需要说明书时调用 `zhihuiya/descriptionData` 或 `zhihuiya/descriptionDataTranslated`，不得用摘要翻译代替权利要求或说明书。

### 5. 整理引用证据和 PDF

```json
{"patentNumber":"EP4000000A1","replaceByRelated":"1"}
```

用 `zhihuiya/pdfData` 获取 `pdfPath`，用 `zhihuiya/patentCited` 查看被引用关系，用 `zhihuiya/patentForwardCitation` 查看该专利引用的文献。批量参数、替代同族 PDF 和返回列表上限必须按对应 reference 检查；下载链接只作为证据入口，不把它解释为权利有效性证明。

## 展示规则

1. **先说明任务口径**：明确本次是候选发现、信息核验、文本比对、状态复核还是文件获取，列出实际调用的 operation 和数据来源路径。
2. **按结果类型展示**：检索和图片结果用表格；单篇著录/状态用键值或分组；全文、翻译和事件按章节或时间顺序展示；PDF 和图片以可点击路径或 URL 展示。
3. **只展示真实字段**：不得补写 API 未返回的标题、日期、权利人、状态、相似度或法律结论；null、空数组和不可用字段省略并说明缺失原因。
4. **标注计数与成本**：展示 `total`、`allRecordsCount`、`costToken` 以及请求的 limit/offset；批量查询注明批量上限和当前返回条数。
5. **图片检索要分型**：显示 `patentType`、model、相似度、受理局和分类命中；D 与 U 结果不得混表或互换解释。
6. **日期统一格式**：将 `YYYYMMDD` 或毫秒时间戳格式化为明确日期，同时保留原始值可追溯；引用、家族和事件按关系方向展示。
7. **错误可操作**：按 MCP、代理和下游业务三层解释错误，不把认证错误当成空结果。
8. **控制大响应**：先给摘要表和前 3 条样本，再按用户指定的 patentId/pn 展开；不要把完整 JSON 直接塞进对话。
9. **合规措辞**：把相似度、状态和引用作为风险线索或事实证据，不表述为确定侵权、确定有效、FTO 或律师意见；必要时提示专业法律复核。

## 解决认证和积分问题

- MCP 或 `proxy_call` 缺失：停止并配置 `LinkFox`，重启或重载 WorkBuddy；不自行安装或 HTTP fallback。
- MCP 连接 401：提示重新登录、重载连接或联系 WorkBuddy 管理员，不要求手工填写 Authorization。
- 代理成功但下游业务 JSON 为 401：按 WorkBuddy 自动授权或下游认证失败处理，不把 Key 放进 `arguments`。
- 下游 402 或积分不足：停止并引导访问 `https://agent.linkfox.com/`，不得自动选套餐、下单、支付或轮询。
- 403、501 和其他错误按业务 reference 处理，不误归为 401/402；501 仍表示检索权限或套餐配额问题。

## 积分消耗说明

> 用户会因积分消耗而支付费用。请充分评估：当需要高频调用本技能，或用户对积分消耗量预期不足时，务必提醒用户，由用户决定是否继续。
