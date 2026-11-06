---
name: linkfox-wb-sif-compliance-detection
display_name: LinkFox SIF 外观专利检测
display_name_en: LinkFox SIF Design Patent Compliance Detection
description: 按商品图片检索外观登记相似候选并呈现来源风险线索，支持外观专利候选排查与人工复核，不作侵权判定。
description_zh: 当用户需要根据商品图片查找外观登记相似候选、按地区或洛迦诺分类筛选、查看相似度与来源法域时使用。能力返回候选标识、图片、法律状态、保护法域和 TRO 关联线索，供人工复核；不提供侵权结论、专利全文或独立登记详情查询。
description_en: Use when a user needs image-based discovery of similar design-registration candidates with optional region, source-jurisdiction, Locarno, and legal-status filters. Present returned identifiers, images, source status, protection jurisdictions, and TRO association clues for human review. This capability does not issue infringement verdicts, retrieve patent full text, or provide a separate registration-detail lookup.
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

> [!IMPORTANT]
> 本能力依赖 MCP “LinkFox”。如未安装或 `proxy_call` 不可见，必须停止业务调用并读取 [references/onboarding.md](references/onboarding.md) 的安装与错误处理说明。

# LinkFox SIF 外观专利检测（LinkFox SIF Design Patent Compliance Detection）

根据一张商品图片检索外观登记相似候选，帮助用户在上架前或竞品复核时快速定位可能相关的外观登记，并把来源标识、相似度、法域、法律状态、分类、图片和 TRO 关联线索整理成可复核结果。当前业务能力标识为 `linkfox-sif-compliance-detection`，包含 1 个可调用 operation，统一通过 `LinkFox.proxy_call` 访问 `ecDw/designSimilarSearch`。结果是候选检索与来源事实，不是侵权概率、自由实施意见或法律结论。

## 能力边界

### ✅ 能力范围

- **商品图片外观候选检索**：用户提供公网 `imageUrl` 或原始 `imageBase64` 二选一时，调用 `ecDw/designSimilarSearch`，可附带 `title`、`topK`、`regions`、`jurisdictionCodes`、`topLoc`、`locarnoClasses` 和 `patentStatus`，返回按来源排序的候选登记记录。
- **筛选与候选复核**：根据用户明确的地区、来源归属码、洛迦诺分类或法律状态偏好透传筛选条件；展示 `design_registration_id`、`primary_identifier`、`similarity`、`risk_level`、`simple_legal_status`、权利人、设计人、日期、图片、`protected_jurisdictions` 与 `tro_cases` 等实际返回字段。
- **本地图片输入**：本地文件可由调用方在内存中编码成不带 data URL 前缀的纯 Base64，再放入 `arguments`；本能力不需要本地上传 helper，也不承诺将文件落盘或生成长期公开链接。
- **来源事实标注**：保留请求追踪号、业务状态和本次返回的费用字段；对缺失或空值标注“来源未提供”，让用户知道哪些内容需要进一步人工核验。

### ❌ 边界与限制

- **不作侵权判定**：相似度、`risk_level`、法律状态或 TRO 关联都不能单独证明侵权、无侵权、无风险或自由实施；空结果也不能证明不存在相关权利。
- **不提供独立详情接口**：当前 WorkBuddy MCP 契约只暴露图片相似检索 `ecDw/designSimilarSearch`，不承诺按登记 ID、主号码、公开号获取完整登记详情、专利全文或下载登记图片。
- **不替换筛选语义**：`regions` 是 ISO-2 地区筛选，`jurisdictionCodes` 是来源归属码，二者同时存在时取交集；不得把二者互相改写，也不得把缺失分类或 unknown/pending 状态的候选自行删除。
- **图片来源必须唯一**：`imageUrl` 与 `imageBase64` 必须且只能提供一个；标题只能辅助图片，不能独立发起检索。Base64 不得带 `data:image/...;base64,` 前缀，长度上限见 [references/api.md](references/api.md)。
- **不提供其他知识产权或经营能力**：不处理商标、发明专利全文、独立 TRO 搜索、卖家账号、商品采购、广告、订单或上架执行。
- **不绕过 MCP**：MCP 或 `proxy_call` 缺失、schema 错误、连接失败或业务错误时停止，不猜测其他工具名、不自动改参数、不自动重复付费调用。

## 工具选择指南

本能力当前只有一个可用业务 operation。先判断用户是否有商品图片和是否需要筛选，再决定是否在同一次检索中加入可选参数；不要为了满足登记详情或法律结论请求而伪造第二个 operation。

| 需求 / 用户说 | 默认推荐 | 何时换用其他 |
|---|---|---|
| “找这件商品外观相似的登记候选” | `ecDw/designSimilarSearch`，只传一项图片来源 | 用户没有可用图片时先补充图片；标题不能替代图片 |
| “只查美国或欧盟、某来源码、某洛迦诺分类” | `ecDw/designSimilarSearch`，在同一请求加入 `regions`、`jurisdictionCodes`、`topLoc` 或 `locarnoClasses` | 若用户未明确筛选条件，省略可选数组，避免误缩小结果 |
| “只看有效或只看失效登记” | `ecDw/designSimilarSearch`，传 `patentStatus` 为 `[1]` 或 `[0]` | 需要同时保留两种状态时传 `[0,1]`；不要传标量或自行二次筛选 |
| “我有登记 ID，帮我查完整权利详情或专利全文” | 当前能力不支持独立详情查询 | 说明当前只提供图片相似候选检索，不能把登记 ID 拼成图片搜索请求 |
| “告诉我一定侵权还是一定安全” | 当前能力不支持法律结论 | 展示来源事实并说明需要专业法律调查或人工复核 |

### 工具选择思路

- 有图片时优先进行一次最小充分的检索；只有用户明确提出时才增加标题和筛选条件。
- `topK` 是候选返回上限，不是计费单位。默认 20 通常足够初筛；用户需要更广候选时可在 1–200 内调整，并先说明一次新调用可能产生费用。
- `regions` 与 `jurisdictionCodes` 都需要时一次传入；结果只代表二者交集，不把请求地区当成候选实际保护法域。
- 检索后如果用户只要求复核当前结果，复用已返回字段，不自动重新调用；需要刷新签名图片或扩大条件时，先说明会产生新的调用，再由用户决定。

## 业务需求路由速查

按工具选择指南确定最小必要请求后，使用下表的精确 `toolName`。当前 `linkfox-sif-compliance-detection` 只有一个 MCP 业务 operation。

| 子能力 | 业务能力 | reference | 原 endpoint | 精确 `toolName` |
|---|---|---|---|---|
| `linkfox-sif-compliance-detection` | 商品图片外观相似登记候选检索 | `references/linkfox-sif-compliance-detection.md`；完整参数与响应见 `references/api.md` | `/ecDw/designSimilarSearch` | `ecDw/designSimilarSearch` |

本能力没有需要保留的本地 helper；所有业务请求都由 `LinkFox.proxy_call` 完成。

## MCP 调用方式

- **唯一业务工具**：使用 MCP server `LinkFox` 的 `proxy_call`，调用结构为 `{"toolName":"ecDw/designSimilarSearch","arguments":{...}}`。`toolName` 保留大小写和路径分隔符，不加前导 `/`。
- **参数位置**：原业务请求对象直接放在 `arguments`，不得再包 `body`、`params`、`data` 或第二层 `arguments`。没有可选筛选时也传空对象以外的实际图片参数，不能省略图片来源。
- **自动授权**：WorkBuddy 自动注入 LinkFox Authorization。不要在 MCP 配置或 `arguments` 中加入 headers、Authorization、token、JWT、手机号或其他凭证，也不要向用户索取这些内容。
- **响应分层**：先检查 MCP 连接、工具是否存在、schema 是否接受请求以及外层 `isError`；再读取 structured content 或 text content。text 若是 JSON，只解析一次，随后检查下游 `errcode`、`errorCode`、`code`、`success` 和消息字段。只有业务状态为 `errcode=200` 且 `data.code=OK` 的响应才按候选结果处理。
- **业务结果位置**：成功结果通常在 `data.data.candidates`，总数在 `data.data.total`。`data.usage.credit_cost` 是来源侧用量，不能当作用户费用；优先展示网关返回的 `costCredit`，缺失不代表免费。
- **去重与失败纪律**：同一任务内相同 `toolName + arguments` 只调用一次。超时、失败、空结果或结果不明确时不自动重试、不自动换图片、不自动扩大 `topK`、不逐条刷新图片；再次调用前说明潜在积分消耗并由用户决定。
- **本地处理边界**：本能力没有本地 helper。图片 Base64 只能由调用环境在请求前完成必要编码；MCP 不自动提供旧脚本的缓存、落盘、stdout 摘要或费用合并能力。

## 使用示例

以下示例只展示 `proxy_call` 的业务参数结构。示例 URL 和 Base64 是占位格式，执行时必须替换为真实可访问图片或真实原始 Base64；不要同时传两种图片来源。

### 1. 用公网图片做基础检索

```json
{
  "toolName": "ecDw/designSimilarSearch",
  "arguments": {
    "imageUrl": "https://public.example/product.png"
  }
}
```

读取 `data.data.candidates` 和 `data.data.total`，按返回顺序展示候选。基础检索使用默认 `topK=20`；一次新调用通常按当前目录口径消耗 5 算力，实际以返回的费用字段为准。

### 2. 用本地图片 Base64 与筛选条件检索

```json
{
  "toolName": "ecDw/designSimilarSearch",
  "arguments": {
    "imageBase64": "<raw-base64-without-data-url-prefix>",
    "title": "Bottle",
    "topK": 20,
    "regions": ["US", "EM"],
    "jurisdictionCodes": ["USID", "EMID"],
    "topLoc": ["09", "22"],
    "locarnoClasses": ["22-06"],
    "patentStatus": [1]
  }
}
```

`imageBase64` 必须是图片字节的纯 Base64，不能传文件路径、Markdown、HTML 或 data URL。`regions` 与 `jurisdictionCodes` 同时存在时取交集；`topLoc` 是两位洛迦诺主分类前缀，`locarnoClasses` 是完整分类；筛选数组不应重复或混入 null。筛选越窄越可能减少候选，但不代表覆盖完整。

### 3. 从返回结果中选择候选进行人工复核

候选返回 `design_registration_id`、`primary_identifier`、`similarity`、`simple_legal_status`、`image_url`、`images`、`protected_jurisdictions` 和 `tro_cases` 等字段时，复用本次响应做人工复核摘要。当前没有可执行的详情 `toolName`，不得因为用户要求更完整资料而自造登记详情请求；若用户需要法律意见，应转人工专业调查。

## 展示规则

1. **保留来源顺序**：按 `data.data.candidates` 原数组展示 Top-K，包含同分项；`similarity` 是 0–100 的最终排序分，不是概率或侵权概率，不重算、不乘 100、不重新排序。
2. **分开呈现风险字段**：`risk_level`、`simple_legal_status`、`similarity` 和 `tro_cases` 分别标注来源含义，不把它们合并成“侵权风险结论”。
3. **完整呈现可复核标识**：优先展示 `design_registration_id`、`primary_identifier`、申请号、登记号、公开号、标题、权利人、设计人、申请/登记/公布日期、Locarno 分类和来源法域；空值或缺失统一标注“来源未提供”。
4. **区分法域**：`registration_jurisdiction_code`、`jurisdiction_iso2`、请求中的 `regions` 与 `protected_jurisdictions` 含义不同。保护法域必须以返回的 `protected_jurisdictions` 为准，不能用请求地区补齐。
5. **谨慎展示图片**：`image_url` 是首图，若有 `images` 则与 `images[0]` 对应；使用完整 URL，不改域名或签名。签名图片通常只在有限期限内有效，优先展示首图并按需懒加载其他视图，不批量下载或付费刷新。
6. **正确解释 TRO 线索**：`tro_cases=[]` 只表示当前来源语料没有关联记录，不表示“没有 TRO”、无诉讼或安全；有记录时展示来源线索，不替用户做法律判断。
7. **标注数据时间与费用**：保留 `upstreamRequestId` 或 `data.request_id` 供排查，注明结果来自本次 SIF 检索；将 `costCredit` 与 `costToken` 作为调用费用信息，不能把 `data.usage` 解释成用户余额。
8. **错误与不可用字段**：MCP 错误、`isError=true`、业务失败、空结果和字段缺失都要如实说明；错误或空结果不能改写成“未发现专利”。根据返回消息给出修正建议，禁止猜测缺失字段。
9. **保护隐私**：不展示任何凭证、授权上下文或内部配置；申请人地址等敏感来源字段仅在用户确有复核需要时最小化展示。

## 解决认证和积分问题

发生认证、MCP 连接或积分异常时读取 [references/onboarding.md](references/onboarding.md)，并按以下分层处理：

- **MCP 或 `proxy_call` 缺失**：停止业务调用，提示用户安装或重载 LinkFox 连接器，确认 `proxy_call` 可见后再重试。
- **MCP 连接 401**：视为 WorkBuddy 自动授权链路异常，提示重新登录、重载连接或联系管理员；不得要求用户手填 Authorization。
- **代理成功但下游 JSON 401**：保留下游错误消息并停止，说明自动授权或下游业务认证失败；不把凭证塞入 `arguments`。
- **下游 JSON 402 或余额不足**：读取 `references/onboarding.md`，引导用户访问 `https://agent.linkfox.com/` 自助处理；不自动选套餐、下单、支付或轮询。
- **403**：按权限错误处理，不归类为认证或积分不足，不自动重试或绕过权限。
- **其他错误**：保留 `errcode`、`errorCode`、`code`、`errmsg`、`msg` 或 `message` 及必要的请求标识，给出字段修正或人工排查建议，不自动换条件、不重复付费调用。

WorkBuddy 会自动注入 Authorization。Skill、MCP 配置和 `proxy_call.arguments` 均不得出现 headers、凭证、token、JWT、手机号或其他认证材料；本能力不提供登录、注册、套餐查询或支付脚本流程。

## 积分消耗说明

> 用户会因积分消耗而支付费用。请充分评估：当需要高频调用本技能，或用户对积分消耗量预期不足时，务必提醒用户，由用户决定是否继续。
