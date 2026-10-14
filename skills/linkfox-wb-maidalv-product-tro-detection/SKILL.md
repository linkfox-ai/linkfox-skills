---
name: linkfox-wb-maidalv-product-tro-detection
display_name: Linkfox 卖大律TRO检测
display_name_en: LinkFox Maidalv TRO Detection
description: 面向电商产品图片与商品文本的 TRO 及知识产权侵权风险检测能力，输出风险等级、命中项、TRO 原告信息和 AI 法律评估报告。
description_zh: 面向电商上架前与产品合规审查的卖大律 TRO/知识产权风险检测能力。接收主商品图片，可结合参考图、产品图片、IP 图片、产品文本和 IP 关键词，识别商标、版权、专利及 TRO 相关风险，返回总体风险等级、高风险命中、低风险 IP 项、TRO 原告与案件信息、数值风险分和按语言生成的 AI 法律评估报告。当用户要检查产品是否可能侵权、是否存在 TRO 风险、是否适合上架或需要查看原告信息时触发。通过 Linkfox MCP 调用，完整参数、响应字段、错误码与本地图片上传流程见 references/。
description_en: E-commerce product TRO and intellectual-property risk detection for pre-listing and compliance review through Linkfox MCP. Accept a required main product image plus optional reference images, additional product images, IP images, product text and IP keywords; return overall risk level, high-risk hits, lower-risk IP items, TRO plaintiff and case details, numeric risk scores and an AI legal assessment report localized by language. Use when users need to check possible trademark, copyright, patent or TRO exposure, listing readiness, or plaintiff details.
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


# Linkfox 卖大律TRO检测（LinkFox Maidalv TRO Detection）

面向电商卖家、选品人员和合规审核人员，依据产品图片、补充证据和产品文本评估 TRO（Temporary Restraining Order，临时限制令）及商标、版权、专利相关风险。能力入口为 `linkfox-maidalv-product-tro-detection`，通过两个精确 MCP endpoint 完成风险检测和本地图片预签名，并保留一个仅负责外部存储 PUT 的本地 helper。

## 能力边界

### ✅ 能力范围

- **产品 TRO 与知识产权风险检测**（`linkfox-maidalv-product-tro-detection`）：使用必填的 `mainProductImage`，将产品主图与知识产权资产和 TRO 案件相关记录进行匹配，覆盖 `Trademark`、`Copyright`、`Patent` 三类 IP，返回 `riskLevel`、`checkId`、`results`、`nonResults`、`costToken` 和报告等字段；通过 MCP `toolName=maidalv/checkApiFlash` 调用。
- **多证据风险核验**（`linkfox-maidalv-product-tro-detection`）：在主图之外，可传入最多 3 张 `referenceImages`、5 张 `otherProductImages`、3 张 `ipImages`，以及 `referenceText`、`description` 和最多 20 个 `ipKeywords`，用于补充相似产品、商品描述或待核查 IP 线索。
- **TRO 原告与案件线索呈现**（`linkfox-maidalv-product-tro-detection`）：对返回的 `plaintiffName`、`plaintiffId`、`numberOfCases`、`lastCaseDocket`、`lastCaseDateFiled` 进行结构化展示；这些字段仅在相关 IP 出现在 TRO 案件中时按需出现。
- **AI 法律评估报告**（`linkfox-maidalv-product-tro-detection`）：通过 `language=zh` 或 `language=en` 指定 `report` 的语言；该参数只影响报告文字，不改变 IP 字段值。
- **本地图片准备**：先通过 MCP `toolName=oss/file/presignedPut` 获取预签名 URL，再用 `scripts/upload_image.py` 仅向该存储 URL 上传本地图片，得到有效期约 24 小时的公开 URL；也可自行转换为带 `data:image/...;base64,` 前缀的 data URI。
- **自动授权与积分引导**：WorkBuddy 自动注入授权。MCP/401/402/403 按 `references/onboarding.md` 分层处理，不索取凭证、不自动购买套餐或支付。

### ❌ 边界与限制

- **主图必填**：`mainProductImage` 必须是可公开访问的图片 URL，或带 `data:image/...;base64,` 前缀的 Base64 data URI，长度不超过 1000；本地路径不能直接作为检测输入。
- **图片数量与文本长度受限**：`referenceImages` 最多 3 张、`otherProductImages` 最多 5 张、`ipImages` 最多 3 张、`ipKeywords` 最多 20 个；`referenceText` 和 `description` 各最多 1000 字符。
- **一次性分析**：一次检测直接返回当前分析结果，不提供二次 SQL/数据查询或单独的原告详情查询；不要把 `columns` 当作结果数量来源，应使用 `results` 和 `nonResults` 数组。
- **字段按需返回**：非 TRO 或未评分项目可能只包含基础字段；`plaintiffName`、案件字段和 `riskLevel`/`riskScore`/`riskDescription` 可能缺失而非为 `null`，缺失不代表接口错误。
- **不是法律意见**：结果是视觉/文本匹配与案件数据风险提示，AI 报告也不替代律师意见，不直接给出侵权成立、FTO、诉讼策略或最终上架许可结论。
- **调用成本与重试**：检测会消耗积分；同一任务内相同 MCP `toolName + arguments` 不得重复调用。失败、空结果或参数错误时不得自动换主图、换关键词、连续试探或重复收费调用，需继续检测时先说明额外消耗并由用户决定。
- **数据边界**：结果依赖接口当前知识产权资产和 TRO 案件数据；不存在命中不等于绝对没有风险，存在命中也不等于已经构成法律侵权。
- **不在范围内**：供应商或商品找货、Amazon/1688 搜索、Listing 文案优化、关键词分析、专利全文或权利要求检索、店铺运营、广告投放、订单库存、注册申请和与平台/权利人的直接沟通。

## 工具选择指南

本能力只有一个业务端点，但可以按用户目标决定输入证据的丰富程度和输出语言。先根据下表选择请求形态，再到【业务需求路由速查】定位端点、脚本和 reference。

| 需求 / 用户说 | 默认推荐 | 何时换用其他 |
|---|---|---|
| “这张产品图有没有 TRO/侵权风险” | 仅传 `mainProductImage` 调用 `linkfox-maidalv-product-tro-detection` | 有参考图、产品描述或 IP 线索时增加对应可选参数；不要因此改用外部搜索或二次查询 |
| “上架前检查商标、版权、专利风险” | `mainProductImage` + `description`，必要时补充 `referenceImages` 或 `otherProductImages` | 用户明确提供 IP 证据图时加入 `ipImages`；需核对文字线索时加入 `referenceText`/`ipKeywords` |
| “这个产品会不会被 TRO 原告起诉”“查原告案件数” | 调用检测端点并重点读取 `results`/`nonResults` 中的原告与案件字段 | 不存在独立原告查询 operation；不要把缺失的案件字段当作零，也不要自行补查 |
| “给我英文法律评估报告” | 设置 `language: "en"` | 只想看中文报告时使用默认 `zh`；语言参数不翻译其他响应字段 |
| “我只有本地图片” | 先调用 `oss/file/presignedPut` 获取预签名 URL，再通过标准输入交给 `scripts/upload_image.py` 执行 PUT，最后调用检测端点 | 也可将图片转为完整 data URI；不直接把本地文件路径传给 API |
| “检测失败，想重新试几张图/几个关键词” | 先解释 `errcode`/`errmsg` 和输入问题 | 只有用户明确决定承担额外积分后才可修改参数重试；网络临时错误可按脚本结果处理，不连续试探 |

### 工具选择思路

- 需求核心是产品图片的 TRO、商标、版权或专利风险时，统一使用 `linkfox-maidalv-product-tro-detection`；不要将 `results` 与 `nonResults` 拆成互相独立的判断。
- 主图是最低输入，补充图片和文本只在用户已有相应证据或确实需要增强核验时加入；参数越多不代表一定得到更高风险等级。
- 用户只要中文/英文报告时通过 `language` 控制报告，不要把它误解为整个响应的翻译开关。
- 满足程度相同的情况下使用默认的主图检测，并在多次检测、换图或扩展关键词前说明积分消耗，由用户决定是否继续。

## 业务需求路由速查

按【工具选择指南】确定请求形态后，使用下表定位完整参数、响应字段、错误码和脚本。

| 子能力 | 业务能力 | reference | 原 endpoint | 精确 MCP `toolName` | 本地 helper |
|---|---|---|---|---|---|
| `linkfox-maidalv-product-tro-detection` | 产品图片、文本与 IP 线索的 TRO/商标/版权/专利风险检测 | `references/linkfox-maidalv-product-tro-detection.md` | `/maidalv/checkApiFlash` | `maidalv/checkApiFlash` | 无 |
| `linkfox-maidalv-product-tro-detection` | 本地图片上传的预签名准备 | `references/linkfox-maidalv-product-tro-detection.md` | `/oss/file/presignedPut` | `oss/file/presignedPut` | `scripts/upload_image.py` 仅执行预签名 PUT |

认证和积分异常见 `references/onboarding.md`；本地图片公开化必须先由 MCP 获取预签名 URL，再由 `scripts/upload_image.py` 完成外部存储 PUT。

## MCP 调用方式

- **MCP server**：`LinkFox`；唯一工具：`proxy_call`。
- **允许的精确 `toolName`**：检测为 `maidalv/checkApiFlash`；本地图片预签名为 `oss/file/presignedPut`。两者都是原 endpoint 去掉前导 `/` 后的精确值，区分大小写。
- **检测参数**：将 `mainProductImage`、可选图片数组、文本、关键词和 `language` 直接放入 `proxy_call.arguments`，不得额外包裹 `body`、`params` 或 `data`。
- **预签名参数**：将本地图片 MIME 放入 `contentType`，无点号扩展名放入 `fileExtension`；MCP 成功且下游 `errcode=200` 后读取 `url`，不要显示其签名查询参数。
- **本地 PUT**：运行 `python scripts/upload_image.py "<local_image_path>"`，并仅通过标准输入提供预签名 URL；不得把签名 URL 放入命令行参数、日志或用户可见输出。helper 只校验文件格式并向绝对 HTTPS 预签名 URL 上传字节，不读取 LinkFox 凭证、不访问工具网关。支持 JPG/JPEG、PNG、GIF、WebP、HEIC。
- **自动授权**：WorkBuddy 自动注入授权上下文；MCP 配置、检测参数和预签名参数中禁止加入 `headers`、Authorization、API Key、token、JWT、手机号或其他凭证。
- **返回解析**：先检查 MCP 连接、工具、schema 与 `isError`，再读取 text/structured content；text JSON 只解析一次。随后检查下游 `errcode`/`errmsg`，最后读取检测字段或预签名 `url`。
- **去重与回退**：同一任务内相同 `toolName + arguments` 只调用一次。收费检测失败、空结果或不理想时不自动换图、换词或重试；预签名/PUT 失败或过期也不静默重做。MCP 不可用时禁止回退旧 HTTP 网关、检测脚本或其他工具。
- **本地能力变化**：旧检测脚本的 24 小时缓存、自动响应落盘、会话元数据和 stdout 摘要已移除；不要声称 MCP 提供这些能力。保留实际 `toolName`、参数摘要、`checkId`、检测时间和 `costToken` 便于复核。
- **详细契约**：请求、完整嵌套响应、错误、成本、图片上传和 Feedback API 见 `references/linkfox-maidalv-product-tro-detection.md`；认证与积分异常见 `references/onboarding.md`。

## 使用示例

以下示例使用真实参数形状。每次未命中缓存的检测都会消耗积分；扩展图片、文本或关键词、跳过缓存或再次尝试前，先告知用户可能产生的额外消耗。

### 基础产品风险检测

**1. 只用主图进行检测**

```json
{
  "toolName": "maidalv/checkApiFlash",
  "arguments": {"mainProductImage":"https://example.com/product.jpg","language":"zh"}
}
```

读取 `riskLevel` 和 `checkId` 作为结论入口，再展示 `total`、`results`、`nonResults` 和 `costToken`。图片 URL 必须公开可访问；返回的 `report` 以中文生成。

### 多证据与文字线索检测

**2. 带参考图、产品图、IP 图与文本**

```json
{
  "toolName": "maidalv/checkApiFlash",
  "arguments": {"mainProductImage":"https://example.com/product-main.jpg","referenceImages":["https://example.com/reference.jpg"],"otherProductImages":["https://example.com/product-side.jpg"],"ipImages":["https://example.com/ip-evidence.jpg"],"referenceText":"Similar product title","description":"Compact USB-C charger with foldable plug","ipKeywords":["brand-name","product-line"],"language":"zh"}
}
```

重点读取 `results[]` 中的 `ipType`、`text`、`ipOwner`、`riskScore`、`riskDescription` 与 `ipAssetUrls`；如存在 `plaintiffName`，同时读取案件数、最近案号和立案日期。数组数量和文本长度必须符合 reference 的上限。

**3. 只增加文字线索**

```json
{
  "toolName": "maidalv/checkApiFlash",
  "arguments": {"mainProductImage":"https://example.com/product.jpg","referenceText":"Wireless charging stand","description":"Adjustable charging stand for mobile devices","ipKeywords":["wireless","charging"],"language":"en"}
}
```

适合没有额外图片但需要结合商品标题/描述和关键词核验的场景；`language: "en"` 只影响 AI `report`，`riskLevel`、`ipType` 等字段仍按接口原值返回。

### 本地图片两阶段上传

本地 `product.png` 先请求预签名 URL：

```json
{
  "toolName": "oss/file/presignedPut",
  "arguments": {
    "contentType": "image/png",
    "fileExtension": "png"
  }
}
```

确认 MCP 和下游 `errcode` 成功后，不展示 `url` 的签名查询参数，立即执行：

```text
python scripts/upload_image.py "./product.png"
```

把上一步返回的预签名 URL 仅写入 helper 的标准输入。helper 输出的公开 `url` 可作为检测请求的 `mainProductImage`，输出不得包含签名查询参数。上传不读取 LinkFox Key；预签名过期或 PUT 失败时需告知用户，由用户决定是否重新申请和上传。认证或积分异常按 `references/onboarding.md` 处理。

## 展示规则

1. **先给总体结论**：优先展示 `riskLevel` 和 `checkId`，并说明数据来自卖大律产品 TRO/IP 风险检测；随后给出 `total` 与 `nonResults` 长度。
2. **高风险优先**：`results` 非空时逐条突出 `ipType`、`text`、`ipOwner`、`riskScore`、`riskDescription`；不要把 `nonResults` 的低风险/非高风险项混入高风险结论。
3. **展示 TRO 线索**：项目存在 `plaintiffName` 时展示原告、`numberOfCases`、`lastCaseDocket`、`lastCaseDateFiled`；字段缺失或为 `null` 时标为 N/A，不自行补全案件信息。
4. **展示证据**：`ipAssetUrls` 有值时以内联链接或图片方式展示 IP 证据，说明其为接口返回的对比证据；不要把证据图当作法律裁判文书。
5. **展示 AI 报告**：高风险项存在 `report` 时完整呈现或按用户要求摘要，并标注报告语言由 `language` 控制；报告不能替代律师意见。
6. **处理条件字段**：`riskLevel`、`riskScore`、`riskDescription`、原告字段按需出现，缺失不是异常；`columns` 是渲染元数据，不能用于推断命中数量。
7. **不可用值处理**：`null`、空字符串或接口语义上的不可用字段展示为 N/A 或省略；不要将缺失案件字段表述成“没有 TRO 案件”。
8. **客观与法律边界**：将“接口返回的风险等级/匹配项”与“法律结论”分开，末尾提示结果不构成侵权法律判定、FTO 意见或诉讼策略，必要时咨询专业律师。
9. **错误可行动**：区分 MCP/代理错误与下游 `errcode`/`errmsg`，原样说明脱敏失败原因，并建议修正公开图片 URL、data URI 前缀、图片数量、文本长度或 `language` 取值；不要因错误自动换参数重试。
10. **来源与时间**：标注检测时间、`checkId`、响应中的 `costToken` 和数据来源；若同时展示上传 URL，说明其约 24 小时有效。
11. **反馈处理**：用户明确表扬、不满、指出结果与意图不符或发现功能问题时，按 reference 中的 Feedback API 规则异步上报；反馈内容不得包含 API Key、验证码、完整手机号或支付信息，也不得中断当前结果展示。

## 解决认证和积分问题

发生异常时读取 `references/onboarding.md`：

- MCP 或 `proxy_call` 缺失：停止业务调用，提示检查 `LinkFox` 配置并重新登录或重载连接；禁止 HTTP fallback。
- MCP 连接 401：按 WorkBuddy 自动授权链路异常处理，提示重新登录、重载连接或联系管理员；不得要求手工 Authorization。
- 代理成功但下游 `errcode=401`：按自动授权或下游认证失败处理，不把 Key/token 放入 `arguments`。
- 下游 `errcode=402` 或积分不足：引导用户访问 `https://agent.linkfox.com/` 自助处理；不得自动查询套餐、下单、支付或轮询。
- 403：按权限错误处理，不归入认证或计费问题。

处理完成后是否重新调用由用户决定；收费检测不得自动重试。

## 积分消耗说明

> 用户会因积分消耗而支付费用。请充分评估：当需要高频调用本技能，或用户对积分消耗量预期不足时，务必提醒用户，由用户决定是否继续。
