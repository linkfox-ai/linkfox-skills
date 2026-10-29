---
name: linkfox-wb-sif-compliance-detection
display_name: LinkFox SIF 外观专利检测
display_name_en: LinkFox SIF Design Patent Detection
description: 通过商品图片检索外观登记相似候选并辅助排查外观风险
description_zh: 面向商品图片的外观登记相似候选检索能力，支持地区、来源归属、洛迦诺分类和法律状态筛选，返回匹配证据与覆盖提示用于进一步审查，不作侵权判定
description_en: Search design registration candidates similar to a product image with region, jurisdiction, Locarno and legal status filters, returning evidence and coverage warnings for further review without making an infringement determination
icon: icons/logo.png
version: 1.0.0
author: Linkfox
---


> [!IMPORTANT]
本 Skill 必须依赖 MCP “LinkFox”。如未安装该MCP，请明确通知用户：
> 请先安装 LinkFox 连接器：
> - 在 WorkBuddy 左侧找到 “专家·技能·连接器” → “连接器”；
> - 搜索关键词 “LinkFox”，并安装连接器 “LinkFox”（注意：是 linkfox，不是 linkfox-product-selection），按指引完成登录授权；
> - 返回 WorkBuddy 重试。

# LinkFox SIF 外观专利检测（LinkFox SIF Design Patent Detection）

该能力用于从商品图片检索外观登记相似候选，帮助用户定位可能需要进一步核验的登记号、来源归属、分类、法律状态和匹配证据。它适合以图查外观登记、做产品上市前的外观风险候选排查，并返回来源覆盖度与警告；它不能替代专利法律意见，也不输出侵权或自由实施结论。

当前包含 1 个子能力、1 个 API operation 和 1 个业务 endpoint。子能力标识为 `linkfox-sif-compliance-detection`，operation 为 `designSimilarSearch`，对应原 endpoint `/ecDw/designSimilarSearch`。

## 能力边界

能力范围：

- 商品图片外观相似检索。适用于用户提供公网图片 URL 或本地图片内容，并希望查找外观登记候选的场景。请求通过 `ecDw/designSimilarSearch`，精确 `toolName` 为 `ecDw/designSimilarSearch`，业务参数和字段限制见 [references/linkfox-sif-compliance-detection.md](references/linkfox-sif-compliance-detection.md)。对应子能力为 `linkfox-sif-compliance-detection`。
- 以标题补充图片语义。`title` 只能作为图片检索的辅助上下文，图像与文本是分开的匹配模态，不能把原始图像分数和文本分数相加。使用同一 endpoint 和同一精确 `toolName`。
- 按地区、来源归属、洛迦诺分类和法律状态筛选候选。`regions` 使用 ISO-2 地区码，`jurisdictionCodes` 使用来源标识，二者同时给出时取交集；`topLoc` 是两位洛迦诺主分类前缀，`locarnoClasses` 是完整分类码，`patentStatus` 只能使用规定的整数数组。完整约束见 reference。
- 呈现候选登记标识、持有人和设计人、标题、匹配模态、相似度、分类、日期、法律状态、风险提示、coverage 和 warnings。缺失或 null 代表来源事实未知，不能由 Agent 补全。

边界与限制：

- 必须且只能提供 `imageUrl` 或 `imageBase64` 其中一个；只有标题、同时提供两种图片来源或把标题当图片均不构成有效请求。
- 结果是候选审查材料，不是侵权判定、有效性结论、自由实施结论或法律意见。空结果也不代表没有风险。
- 不提供专利全文检索、商标或 TRO 检测、卖家账号管理、商品搜索、采购履约或其他平台运营能力。
- 不自行重筛 unknown 或 pending 法律状态，不删除缺失分类的候选，不把来源覆盖失败解释成零命中，也不臆造候选图片 URL。
- 不自动换图片、改筛选、拆分请求、跟随重定向、重试或轮询。MCP 不可用时停止，不改走其他网络调用方式。

## 工具选择指南

当用户要查商品外观登记相似候选时，先确认图片来源，再按用户明确提出的筛选条件组成一次最小请求。当前只有一个业务 endpoint，选择差异主要在图片输入形式和筛选范围，不应为了试探结果连续发起多次收费调用。

| 需求 / 用户说 | 默认推荐 | 何时换用其他 |
|---|---|---|
| “用这个公网商品图找相似外观登记” | `imageUrl` + `ecDw/designSimilarSearch` | 图片无法稳定公开访问时，改用 `imageBase64`；不能同时传两者 |
| “我有本地图片，查美国和欧洲候选” | `imageBase64` + `regions:["US","EM"]` | 用户明确给出登记来源时，用 `jurisdictionCodes`；两者都指定时仅保留交集 |
| “只看某个洛迦诺大类或完整分类” | `topLoc` 或 `locarnoClasses` | 需要同时限制大类和完整分类时按用户要求同时传入；不要把二者互换 |
| “只看有效或失效登记” | `patentStatus:[1]` 或 `patentStatus:[0]` | 用户要两类都看时传 `[0,1]`；未提出状态偏好时省略 |
| “多返回一些候选” | 调整 `topK`，范围 1–200 | 不要为了凑数量自动改图或重复检索；候选数不是收费单位 |
| “帮我判断是否侵权” | 先返回相似候选、证据、coverage 和 warnings | 不能换成本能力给出法律结论，应说明需要独立法律审查 |

选择思路：

- 先保证有且仅有一种图片来源，再决定是否加入标题和筛选条件；没有图片时不调用。
- `regions` 是 ISO-2 地区范围，`jurisdictionCodes` 是来源归属码，不能把登记号或候选字段机械改写成另一类筛选值。
- 只传用户明确要求的筛选，不静默选择地区、分类或法律状态；未使用的可选字段优先省略。
- 同一 `toolName` 与同一 `arguments` 在当前任务内只调用一次。要换图、换筛选或刷新结果，先说明可能产生额外积分消耗并由用户决定。

## 业务需求路由速查

| 子能力 | 业务能力 | reference | 原 endpoint | 精确 `toolName` |
|---|---|---|---|---|
| `linkfox-sif-compliance-detection` | 商品图片外观相似登记候选检索（`designSimilarSearch`） | [references/linkfox-sif-compliance-detection.md](references/linkfox-sif-compliance-detection.md) | `/ecDw/designSimilarSearch` | `ecDw/designSimilarSearch` |

本能力不保留本地业务 helper。大图片可由调用方在本地准备 JSON 参数文件，随后把其内容作为 MCP `arguments` 传入；这只是输入准备，不是额外 endpoint，也不应写入凭证或自定义请求头。

## MCP 调用方式

- 唯一业务调用是 `LinkFox.proxy_call`，结构固定为 `{"toolName":"ecDw/designSimilarSearch","arguments":{...}}`。`toolName` 保持大小写和路径分隔符，不带前导 `/`；原请求对象直接放在 `arguments`，不增加 `body`、`params`、`data` 或第二层 `arguments`。
- WorkBuddy 自动注入 LinkFox Authorization。不要在 skill、MCP 配置或 `arguments` 中加入 `headers`、Authorization、API Key、token、JWT、手机号或其他凭证。
- 先检查 MCP 连接、工具是否存在、schema 是否可用以及外层 `isError`。若 MCP 返回 text 内容且它是 JSON，只解析一次，再读取业务层 `errcode`、`errorCode`、`code`、`success` 和消息字段；不要把 MCP 外层响应误当作业务 envelope。
- 成功至少同时满足可用的 MCP 调用成功状态、业务 `errcode: 200` 和上游 `data.code: OK`。候选位于 `data.data.candidates`，coverage、warnings 和费用字段按实际响应读取。
- 失败、超时、结果不明确或业务错误时停止，不自动重试、重放、改参数、换图片或连续轮询。不要用其他网络工具替代 `LinkFox.proxy_call`。
- 同一任务内对相同 `toolName + arguments` 去重。MCP 迁移后不承诺旧脚本的缓存、落盘、stdout 摘要或费用头合并；只展示 MCP 实际返回的数据和费用字段。
- 完整请求字段、响应路径、失败代码和反馈字段见 [references/linkfox-sif-compliance-detection.md](references/linkfox-sif-compliance-detection.md)。

## 使用示例

以下示例是 `LinkFox.proxy_call` 的业务调用形状。示例中的图片地址和文本仅用于说明字段位置，真实调用必须使用用户提供的可访问图片或实际图片 Base64。

### 1. 公网图片的基础检索

```json
{
  "toolName": "ecDw/designSimilarSearch",
  "arguments": {
    "imageUrl": "https://example.invalid/product.png",
    "topK": 20
  }
}
```

读取 `data.data.candidates`、`data.data.coverage` 和 `data.data.warnings`。候选为空时如实报告为空，不能据此说产品没有外观风险；这是可能计费的业务调用，不能用占位地址实际请求。

### 2. 本地图片与地区和分类筛选

```json
{
  "toolName": "ecDw/designSimilarSearch",
  "arguments": {
    "imageBase64": "<raw-base64-without-data-url-prefix>",
    "title": "portable bottle",
    "regions": ["US", "EM"],
    "topLoc": ["09"],
    "locarnoClasses": ["09-01"],
    "topK": 50
  }
}
```

`imageBase64` 必须是图片字节的纯 Base64，不含 `data:image/...;base64,` 前缀。`EM` 是本参数使用的欧洲范围码；`locarnoClasses` 保留 `09-01` 这样的字符串格式。大图片应在本地文件中准备 JSON，再将解析后的对象作为 `arguments`，避免命令行长度问题。

### 3. 以来源归属和法律状态筛选

```json
{
  "toolName": "ecDw/designSimilarSearch",
  "arguments": {
    "imageUrl": "https://example.invalid/chair.jpg",
    "jurisdictionCodes": ["USID", "EMID"],
    "patentStatus": [1],
    "topK": 10
  }
}
```

`jurisdictionCodes` 不是 ISO-2 地区码。`patentStatus` 只能是 `[0]`、`[1]` 或 `[0,1]`，省略表示不预设状态偏好。展示时要保留来源返回的 unknown 或 pending 信息；不要根据筛选条件自行二次过滤。新检索可能产生积分消耗，继续改条件前先告知用户。

### 4. 重点出参

成功后优先展示登记标识、来源归属、标题、holder/designer、分类、日期、`matched_modality`、`similarity`、法律状态、`risk_level` 与 `risk_reasons`，并单独展示 coverage、warnings、`capability_version` 和实际费用字段。`similarity` 是来源给出的 0–100 相似度，不是概率；`image_score` 与 `text_score` 是不同模态的原始分数，不能相加。

## 展示规则

1. **保持候选顺序和来源标识**：按返回顺序展示候选，保留 `design_registration_id`、`primary_identifier`、申请号、注册号和公告号等实际返回的标识，不自行重排或补造登记号。
2. **准确解释匹配证据**：分别展示 `image_score`、`text_score`、`similarity` 和 `matched_modality`。不得把相似度称为概率，不得二次换算或把不同模态分数相加。
3. **如实标注未知字段**：候选字段缺失或为 null 时标注未知或省略，不猜测持有人、日期、分类、法律状态、图片地址或下载链接。
4. **保留覆盖和警告**：展示 `coverage`、`metadata_unknown`、`unresolved_hits`、`warnings` 及来源版本。`coverage_ratio` 可能超过 1，不把它当作专利覆盖百分比；覆盖不足或服务失败不能解释成零命中。
5. **谨慎呈现法律含义**：`simple_legal_status`、`risk_level` 和 `risk_reasons` 必须归因于数据源规则提示，不能写成侵权、有效性或自由实施结论。空结果也要明确说明不代表无风险。
6. **候选图片按实际返回**：只有响应中存在可用的真实图片 URL 时才展示图片；`image_available` 只是可用性提示，不能据此拼接 URL。
7. **区分账户用量与用户费用**：`data.usage` 是来源账户用量，不是用户 LinkFox 余额；用户费用只依据实际返回的 `costToken`、`costCredit` 等费用字段，缺失不等于免费。
8. **错误给出修正建议**：保留实际 `errcode`、`errmsg`、上游 `data.code`、`data.message`、请求标识和必要参数摘要；参数错误修正对应字段，认证或余额错误读取 onboarding，其他业务错误停止并等待用户决定。
9. **保护隐私和凭证**：不展示 Authorization、凭证、内部账户余额、原始 Base64 或不必要的内部调试字段；反馈内容只写脱敏的预期与实际差异。

## 解决认证和积分问题

发生以下异常时读取 [references/onboarding.md](references/onboarding.md)。WorkBuddy 自动处理 LinkFox 调用授权，不索取、不展示、不配置任何凭证。

- **MCP 或 `proxy_call` 缺失**：停止业务调用，提示用户安装或重载 LinkFox 连接器，并按 onboarding 的步骤处理；禁止改走其他调用方式。
- **MCP 连接 401**：视为 WorkBuddy 自动授权链路异常，提示重新登录、重载连接或联系管理员；不要要求用户手填 Authorization。
- **代理成功但下游 JSON 401**：报告实际认证错误，提示检查 WorkBuddy 连接和管理员配置，不把凭证放入 `arguments`。
- **下游 JSON 402 或余额不足**：识别积分余额不足、计费不足、余额不足、quota exceeded、insufficient balance、套餐到期、需充值或请充值等同义信息，读取 onboarding 并引导用户访问 `https://agent.linkfox.com/` 自助处理；不自动选套餐、支付或轮询。
- **下游 JSON 403**：按业务权限错误处理，不归类为认证或积分问题，不自动重试。
- **其他错误**：保留错误码、消息、请求标识和必要参数摘要，停止后续依赖调用，不自动换条件或重试。

## 积分消耗说明

> 用户会因积分消耗而支付费用。请充分评估：当需要高频调用本技能，或用户对积分消耗量预期不足时，务必提醒用户，由用户决定是否继续。
