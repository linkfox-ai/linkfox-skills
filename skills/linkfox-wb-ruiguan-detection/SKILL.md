---
name: linkfox-wb-ruiguan-detection
display_name: LinkFox 睿观合规检测
display_name_en: LinkFox Ruiguan Compliance Detection
description: 面向电商上架前的图片与 Listing 文本知识产权、政策合规风险检测能力。
description_zh: 当用户需要检查商品图片或 Listing 文本的版权、图形商标、文字商标、外观专利、实用新型或发明专利、以及图片政策合规风险时，使用本能力调用睿观检测服务，返回相似度、权利人、法律状态、TRO 维权史、雷达判定与匹配详情，并按数据结果给出可审计的风险提示。支持公开图片 URL、本地图片预签名上传、指定国家或地区和标题描述上下文；完整参数见 references，业务调用使用 Linkfox LinkFox MCP。
description_en: Use this capability for pre-listing e-commerce checks of image and Listing-text risks involving copyright, graphic trademarks, text trademarks, design patents, utility or invention patents, and image policy compliance. It calls Ruiguan detection services and returns similarity, rights holders, validity, TRO history, radar findings, and matched records for an auditable risk review. It supports public image URLs, presigned local-image upload, target regions, and title or description context; see references for complete parameters, and use Linkfox LinkFox MCP for business calls.
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


# LinkFox 睿观合规检测（LinkFox Ruiguan Compliance Detection）

面向商品上架前的统一知识产权与图片政策风险排查：根据用户给出的图片、标题、描述和目标市场，选择合适的检测路径，返回可追溯的匹配记录、相似度、权利人或申请人、法律状态、TRO 维权史、雷达结果及 `costToken`。本能力覆盖 6 个检测子能力和 1 个图片预签名支持 operation；完整请求参数、响应字段、错误码与 MCP 示例归档在对应 `references/<子能力标识>.md`。

## MCP 调用

| 项 | 固定值 |
|---|---|
| MCP server | `LinkFox` |
| 唯一工具 | `proxy_call` |
| `toolName` allowlist | `ruiguan/copyrightDetection`、`ruiguan/trademarkGraphicDetection`、`ruiguan/textTrademarkDetection`、`ruiguan/detectionPatentDesign`、`ruiguan/utilityPatentDetection`、`ruiguan/gunPartsSearch`、`oss/file/presignedPut` |
| 调用结构 | `{"toolName":"<精确 endpoint>","arguments":{...}}`；原请求体直接作为 `arguments` |

- `toolName` 必须从 allowlist 选择，精确匹配且区分大小写。
- WorkBuddy 自动注入 MCP Authorization；MCP 配置、文档和 `arguments` 中不得增加 `headers`、API Key、token、JWT、手机号或其他凭证。
- 禁止 curl、`urllib`、`requests`、`httpx` 或其他 HTTP 方式直连工具网关；MCP 或 `proxy_call` 缺失时停止，不得静默 fallback。
- 同一任务内相同 `toolName + arguments` 不得重复调用；收费调用失败、空结果或结果不理想时不得自动重试。
- 先检查 MCP/schema/`isError`，再读取 text/structured content；text JSON 只解析一次。随后检查下游 `errcode`、`errorCode`、`code`、`errmsg` 或 `msg`，最后读取业务字段。
- 新 MCP 检测链路不提供旧脚本的 24 小时缓存、JSON 落盘或 stdout 摘要；仅记录非敏感调用摘要和状态用于追溯。

## Endpoint 映射

| 原 endpoint | 精确 `toolName` |
|---|---|
| `/ruiguan/copyrightDetection` | `ruiguan/copyrightDetection` |
| `/ruiguan/trademarkGraphicDetection` | `ruiguan/trademarkGraphicDetection` |
| `/ruiguan/textTrademarkDetection` | `ruiguan/textTrademarkDetection` |
| `/ruiguan/detectionPatentDesign` | `ruiguan/detectionPatentDesign` |
| `/ruiguan/utilityPatentDetection` | `ruiguan/utilityPatentDetection` |
| `/ruiguan/gunPartsSearch` | `ruiguan/gunPartsSearch` |
| `/oss/file/presignedPut` | `oss/file/presignedPut` |

## 能力边界

### ✅ 能力范围

- **图片版权风险检测**：将公开图片 URL 与已登记版权作品库进行视觉比对，返回 `similarity`、`rightsOwner`、版权标识、来源、TRO 维权史和 `subRadarResult`；使用 `ruiguan/copyrightDetection`。
- **图形商标与 Logo 风险检测**：识别产品图中的 Logo-like 区域，并与多国图形商标库比对，返回商标名称、状态、尼斯分类、申请人、注册信息、框选坐标及雷达结果；使用 `ruiguan/trademarkGraphicDetection`。
- **文字商标风险检测**：扫描产品标题及可选的描述、五点等 `productText`，返回命中商标、地区、风险分数、权利人、黑名单、白名单和整体风险等级；使用 `ruiguan/textTrademarkDetection`。
- **外观设计专利风险检测**：用产品图片及可选标题描述检索多国外观设计专利，支持实物图、线稿图和混合模式、LOC 分类、有效性筛选、TRO 与 AI 雷达分析；使用 `ruiguan/detectionPatentDesign`。
- **实用新型 / 发明专利风险检测**：根据产品标题、功能结构描述和目标地区检索相似功能性专利，返回中英文标题、摘要、权利要求、说明书、有效性、到期日、TRO 标记和分类信息；使用 `ruiguan/utilityPatentDetection`，当前地区只支持 `US`。
- **图片政策合规检测**：将产品图片与已知违规或禁售商品库做视觉相似度检索，返回匹配图片、英文及中文标题和 `cosine`；使用 `ruiguan/gunPartsSearch`。
- **图片输入准备与审计留痕**：图片类路径仅使用可公开访问的 URL；本地文件先由 `oss/file/presignedPut` 取得上传 URL，再用 `scripts/upload_image.py` PUT 到该预签名 URL。公开 URL 原流程有效期约 24 小时。

### ❌ 边界与限制

- **认证与计费**：WorkBuddy 自动注入 MCP Authorization。检测请求会消耗积分；同一任务内相同 `toolName + arguments` 只调用一次，失败或空结果不得自动换图、改文本、翻页或连续试探参数。
- **输入限制**：版权、图形商标、外观专利和图片政策检测需要图片 URL；URL 最长 1000 字符且必须由网关可访问。文字商标的 `productTitle` 和 `productText` 各最长 1000 字符。外观专利的文本字段最长 1000 字符；实用新型的标题和描述各最长 1000 字符。
- **地区与结果上限**：图形商标覆盖给定的 15 个受理局代码；外观专利支持 `US, EU, CN, JP, KR, DE, GB, FR, IT, AU, CA, BR, MX, IN, TH, SE, CH, IE, IL, DK, NZ, AT, BX, FI, WO`；文字商标支持 15 个地区代码；实用新型 / 发明专利当前仅支持 `US`。各端点的结果上限和默认值以对应 reference 为准。
- **结果性质**：相似度、雷达标记、TRO 记录、商标状态和专利有效性是检测服务的数据指标，不是侵权、可销售性或诉讼结果的法律结论。需要正式清权、FTO、注册申请、诉讼策略或平台最终裁决时，转交专业律师或平台合规流程。
- **不在范围内**：商标、专利、版权的注册申请或登记办理；音乐/视频版权；图片编辑；非图片政策检测的商品分类认证；店铺运营、广告、物流、供应链和与权利人或平台的直接沟通。

## 工具选择指南

先根据输入形态和用户真正要回答的问题选择一条检测路径，再到【业务需求路由速查】取 reference、端点和脚本。多个路径都可用时，向用户说明推荐理由、覆盖范围和额外成本，由用户决定是否继续。

| 需求 / 用户说 | 默认推荐 | 何时换用其他 |
|---|---|---|
| 图片有没有版权问题、版权相似度或版权 TRO 风险 | `linkfox-ruiguan-copyright-detection` | 关注 Logo 用 `linkfox-ruiguan-trademark-graphic-detection`；关注产品外观专利用 `linkfox-ruiguan-detection-patent-design` |
| 商品图有没有 Logo / 图形商标风险 | `linkfox-ruiguan-trademark-graphic-detection` | 用户只给标题、品牌词或 Listing 文本时换 `linkfox-ruiguan-text-trademark-detection` |
| 标题、五点或描述中是否含侵权品牌词 | `linkfox-ruiguan-text-trademark-detection` | 需要判断图片中的 Logo 时换图形商标检测；需要结构或外观专利时换对应专利检测 |
| 商品外观是否可能侵犯设计专利、是否有外观 TRO | `linkfox-ruiguan-detection-patent-design` | 需要功能结构专利时换 `linkfox-ruiguan-utility-patent-detection`；该路径默认 US，可按用户指定地区调整 |
| 产品结构、功能或工作方式是否有实用新型 / 发明专利风险 | `linkfox-ruiguan-utility-patent-detection` | 用户只有图片且关注外观时换外观专利检测；此路径的地区不是 US 时先说明当前不支持 |
| 产品图是否接近违规、禁售商品 | `linkfox-ruiguan-gun-parts-search` | 用户问的是知产权利而不是平台政策时，改用版权、商标或专利路径 |

选择思路：图片中的视觉元素优先区分版权、Logo 和外观专利；文本中的品牌词使用文字商标；功能、结构和技术特征使用实用新型 / 发明专利；“违规/禁售/政策”使用图片政策检测。`enableRadar` 仅在对应端点支持时开启；需要快速相似度扫描时可关闭雷达或减少召回数，需要更完整审计时再使用较高召回数，但不得未经用户同意连续增加调用。

## 业务需求路由速查

| 子能力 | 业务能力 | reference | `toolName` | 本地辅助 |
|---|---|---|---|---|
| `linkfox-ruiguan-copyright-detection` | 图片版权作品相似度、权利人、TRO 与雷达检测 | `references/linkfox-ruiguan-copyright-detection.md` | `ruiguan/copyrightDetection` | 本地图片使用 `scripts/upload_image.py` |
| `linkfox-ruiguan-trademark-graphic-detection` | 产品图片图形商标 / Logo 检测 | `references/linkfox-ruiguan-trademark-graphic-detection.md` | `ruiguan/trademarkGraphicDetection` | 本地图片使用 `scripts/upload_image.py` |
| `linkfox-ruiguan-gun-parts-search` | 图片政策违规 / 禁售商品相似检索 | `references/linkfox-ruiguan-gun-parts-search.md` | `ruiguan/gunPartsSearch` | 本地图片使用 `scripts/upload_image.py` |
| `linkfox-ruiguan-detection-patent-design` | 图片外观设计专利相似度、有效性、TRO 与雷达检测 | `references/linkfox-ruiguan-detection-patent-design.md` | `ruiguan/detectionPatentDesign` | 本地图片使用 `scripts/upload_image.py` |
| `linkfox-ruiguan-text-trademark-detection` | Listing 标题和文本的文字商标风险检测 | `references/linkfox-ruiguan-text-trademark-detection.md` | `ruiguan/textTrademarkDetection` | 无 |
| `linkfox-ruiguan-utility-patent-detection` | 标题描述驱动的实用新型 / 发明专利检测 | `references/linkfox-ruiguan-utility-patent-detection.md` | `ruiguan/utilityPatentDetection` | 无 |

支持 operation：`oss/file/presignedPut` 使用 `{"contentType":"image/png","fileExtension":"png"}` 取得预签名 URL；`scripts/upload_image.py` 只检查文件或向该 URL PUT。认证与积分规则见 `references/onboarding.md`。

## 调用方式

1. 按路由表选择 detection reference 和精确 `toolName`，将其请求参数对象直接作为 `arguments`。
2. 本地图片先执行 reference 中的预签名两阶段流程；检测 endpoint 只接收最终公开 URL，不接收本地路径。
3. 调用 `proxy_call` 一次并按 MCP 外层、代理内容、下游错误、业务字段顺序解析。
4. 检测是收费操作，以 `costToken` 为准；失败、空结果或低相似度不自动换图、改条件或扩大 `topNumber`。
5. 新链路不承诺缓存或落盘；展示时保留 `detectId`、查询地区、参数快照、`costToken` 和非敏感调用状态。

## 使用示例

以下示例均为单次请求 Body；实际执行前确认图片 URL 对网关公开可访问，并把返回的 `costToken` 纳入用户可见结果。对同一会话同一参数组合不要重复调用。

### 1. 图片版权检测

```json
{
  "imageUrl": "https://example.com/product-image.jpg",
  "topNumber": 100,
  "enableRadar": true
}
```

使用 `toolName=ruiguan/copyrightDetection` 调用 `proxy_call`。重点读取 `data[].similarity`、`rightsOwner`、`copyrightCode`、`subRadarResult`、`troCase`、`troHolder`、`pathThumb` 和 `link`，以及顶层 `total`、`detectId`、`costToken`。雷达适合完整风险审计；只需相似度时可关闭，但会失去雷达判定。

### 2. 图形商标 / Logo 检测

```json
{
  "imageUrl": "https://example.com/product-image.jpg",
  "topNumber": 10,
  "productTitle": "Wireless Bluetooth Headphones",
  "regions": "US,EM",
  "enableLocalizing": true,
  "enableRadar": true
}
```

使用 `toolName=ruiguan/trademarkGraphicDetection` 调用 `proxy_call`。重点读取 `boundingBoxCount`、`radarResult`、`data[].image`、`similarity`、`trademarkName`、`tradeMarkStatus`、`registrationOfficeCode`、`niceClassName` 和 `applicantName`。图片越清晰越有利于定位 Logo；未指定 `regions` 时按服务默认搜索全部支持地区。

### 3. 文字商标检测

```json
{
  "productTitle": "Wireless Bluetooth Headphones Noise Cancelling Over Ear",
  "productText": "Compatible with iPhone and Samsung Galaxy, premium sound quality",
  "regions": "US,EM,GB",
  "limit": 100
}
```

使用 `ruiguan_text_trademark_detection.py`，不需要图片。先读取 `textTrademarkRadar`（`0` 低风险、`1` 待人工核查、`2` 高风险）和 `blacklistTrademarks`，再展示 `data[]` 的商标词、地区、`highestModeScore`（0 到 5）、状态、权利人、申请号、著名/活跃维权标记；`whitelistTrademarks` 作为豁免或安全提示。标题和附加文本各不得超过 1000 字符。

### 4. 外观设计专利检测

```json
{
  "imageUrl": "https://example.com/product.jpg",
  "queryMode": "hybrid",
  "topNumber": 50,
  "regions": "US,EU,CN",
  "productTitle": "Portable Wireless Charger Stand",
  "productDescription": "A foldable wireless charging stand for smartphones",
  "patentStatus": "1",
  "enableRadar": true
}
```

使用 `toolName=ruiguan/detectionPatentDesign` 调用 `proxy_call`。重点读取 `data[]` 的 `similarity`、`applicationNumber`、`publicationNumber`、`patentProdCn`、`patentImageUrl`、`images`、`patentValidity`、`troCase`、`troHolder`、`radarResult.same` 和 `radarResult.exp`。`queryMode` 必须是 `physical`、`line` 或 `hybrid`；需要限定分类时传一级 LOC，例如 `topLoc: "06,07"`。

### 5. 实用新型 / 发明专利检测

```json
{
  "productTitle": "Portable USB-C 65W GaN Fast Charger",
  "productDescription": "Compact 65W GaN USB-C charger with foldable plug, PD3.0 and QC4.0, two USB-C ports and one USB-A port",
  "region": "US",
  "topNumber": 100
}
```

使用 `toolName=ruiguan/utilityPatentDetection` 调用 `proxy_call`。重点读取 `data[]` 的 `title`、`titleCn`、`similarity`、`patentValidity`、申请/公开编号与日期、`estimatedDueDate`、`claims`、`specification`、分类、`troCase` 和 `troHolder`。标题与描述应包含结构、材料、机制和技术特征；当前仅支持 `US`，结果表示相似性筛查而非确认侵权。

### 6. 图片政策合规检测

```json
{
  "imageUrl": "https://example.com/product-image.jpg"
}
```

使用 `toolName=ruiguan/gunPartsSearch` 调用 `proxy_call`。读取顶层 `total`、`detectId`、`costToken` 及 `data[].cosine`、`pdImgOssUrl`、`pdTitle`、`pdTitleCHNCensored`。`cosine` 越高表示越接近已知违规商品；该接口只做图片相似检索，不分析标题或一般商品认证，也不构成平台最终政策裁决。

## 展示规则

1. **客观呈现结果**：按检测类型用表格展示匹配项，至少保留相似度或风险分数、权利人/申请人、状态、地区、TRO、雷达和来源链接；标注数据来自 `ruiguan_ip_detection` 及具体子能力标识。
2. **按风险排序**：版权、图形商标、专利和政策结果按相似度或 `cosine` 降序展示；文字商标先展示整体 `textTrademarkRadar` 和黑名单，再展示逐条命中。结果过多时展示最相关条目并说明 `total`，不得伪装成完整列表。
3. **高风险高亮**：版权或图形商标的 `similarity >= 0.80`、`subRadarResult=1` 或存在 `troCase/troHolder=true` 时标为高风险；外观专利的 `similarity >= 0.70`、`radarResult.same=true` 或存在 TRO 时标为重点复核；图片政策的 `cosine > 0.80` 标为强匹配；实用新型 / 发明专利的高相似、有效状态或 TRO 标记要单独提示。
4. **解释状态和指标**：说明 `similarity`/`cosine` 越高代表视觉相似度越高；说明文字商标 `highestModeScore` 的 0 到 5 范围和 `textTrademarkRadar` 的 0/1/2 含义；区分专利 `Active` 与 `Invalid`，并明确地区覆盖范围。值为 `0` 或 `-1` 且代表不可用时显示 `N/A` 或省略，不把缺失值当成真实结论。
5. **展示证据**：有 `path`、`pathThumb`、商标 `image`、专利 `patentImageUrl` 或 `images` 时提供预览/链接；有 `radarResult.exp` 时同时展示说明；有申请号、注册号、日期、分类、摘要或权利要求时按用户需求展开，不截断高风险记录的关键证据。
6. **TRO 与法律提示**：`troCase` 或 `troHolder` 表示相关权利人/专利有既往 TRO 维权信号，应醒目提示但不得表述为当前必然被诉。所有结果均基于数据比对或相似度，不能替代侵权判定、FTO 或律师意见；报告末尾建议咨询专业知识产权律师或核对目标平台政策。
7. **失败与不可用数据**：请求失败时展示 `errcode`/`errorCode`、`errmsg` 和受影响端点，建议检查 MCP/下游认证、图片公开可达性、文本长度、地区代码、`queryMode`、结果范围或图片质量。标注无法取得的字段，不编造权利人、法律状态或结论；多次检测时保留每条结果的查询时间和来源。

## 解决认证和积分问题

- MCP 或 `proxy_call` 缺失：停止业务调用，按 `references/onboarding.md` 配置并重载客户端，不使用 HTTP fallback。
- MCP 连接 401：提示重新登录 WorkBuddy、重载连接或联系管理员；不得要求用户填写 Authorization。
- 代理成功后的下游 401：按 WorkBuddy 自动授权或下游业务认证失败处理，不在 `arguments` 中传凭证。
- 下游 402 或积分不足：引导用户访问 <https://agent.linkfox.com/>；不自动选套餐、下单、支付或轮询。
- `403` 和其他错误按对应 reference 处理。完成处理后不自动重放检测请求，因为重放会再次消耗积分。
## 积分消耗说明

> 用户会因积分消耗而支付费用。请充分评估：当需要高频调用本技能，或用户对积分消耗量预期不足时，务必提醒用户，由用户决定是否继续。
