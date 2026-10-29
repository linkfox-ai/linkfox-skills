---
name: linkfox-wb-aigc
display_name: LinkFox 跨境电商图片视频
display_name_en: LinkFox Cross-Border Commerce Image and Video Studio
description: 面向跨境电商的图片、文案与视频生成编辑能力，支持商品素材制作、营销套图和视频本地化
description_zh: 当用户需要为跨境电商生成或编辑商品图片、服装套图、营销文案、商品视频、带货口播、视频复刻、视频编辑或视频翻译时使用；支持异步任务、素材上传、任务查询和结果交付，但不替代店铺运营、投放、订单或合规判断
description_en: Use for cross-border commerce image, copy, and video creation or editing, including product assets, apparel suites, marketing copy, sales videos, video recreation, editing, and translation; it supports asynchronous tasks, media preparation, task queries, and result delivery, but not store operations, advertising, orders, or compliance decisions
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

# LinkFox 跨境电商图片视频（LinkFox Cross-Border Commerce Image and Video Studio）

为跨境电商把商品素材、服装素材和营销意图转成可交付的图片、文案或视频，或对已有素材进行编辑、融合、复刻和本地化。用户提出生图、生文、图像编辑、商品或服装营销套图、单图或多图生视频、图转视频、带货口播、商品视频复刻、视频编辑、视频翻译或口型同步时触发。所有业务调用都通过 `LinkFox.proxy_call` 完成，创建任务后保存 `taskId` 并查询终态。

本能力覆盖 13 个子能力标识和 35 个 endpoint 绑定。`aigc/taskQuery` 是图片与视频任务的共享查询入口，文本任务使用 `aigc/textTaskQuery`；完整字段、模型限制和特殊规则按需读取对应 reference。

## 能力边界

### 能力范围

- **通用图片生成**：适用于文生图和参考图生图，使用 `linkfox-aigc-imagegen` 的 `aigc/imageGenAsync` 创建和 `aigc/taskQuery` 查询；可选择动态可用的图片模型、分辨率、比例、质量和输出数量。
- **文本生成与多模态理解**：适用于商品文案、翻译、图片理解和视频分析，使用 `linkfox-aigc-textgen` 的 `aigc/textGenAsync` 创建和 `aigc/textTaskQuery` 查询；无媒体时 `imageUrls` 传空数组。
- **单图或首尾帧生视频**：适用于一张首帧图或受模型支持的首尾帧动画，使用 `linkfox-aigc-videogen` 的 `aigc/videoGenAsync` 和 `aigc/taskQuery`；模型、时长、分辨率、声音和尾帧能力以当前配置为准。
- **多参考图生视频**：适用于多张图片共同控制视频内容，使用 `linkfox-aigc-videogen-multi` 的 `aigc/multiImageVideoGenAsync` 和 `aigc/taskQuery`；保留图片顺序并遵守模型图片上限。
- **商品营销套图**：适用于卖点图、场景图、特写图、白底图和 A+ 素材，使用 `linkfox-aigc-product-suite` 的 `aigc/productMarketMaterial`、`aigc/taskQuery` 和素材准备 endpoint `aigc/uploadByBase64`。
- **服装营销套图**：适用于模特图、卖点图、种草图、尺码图、白底图和 A+ 素材，使用 `linkfox-aigc-clothing-suite` 的 `aigc/wearCollection`、`aigc/taskQuery` 和 `aigc/uploadByBase64`。
- **单图编辑**：适用于换背景、改风格、去除或添加元素、文字处理和商品视觉修整，使用 `linkfox-aigc-image-edit` 的 `aigc/imageEdit`、`aigc/taskQuery` 和 `aigc/uploadByBase64`。
- **多图融合编辑**：适用于搭配融图、搭配上身和多素材合成，使用 `linkfox-aigc-multi-image-edit` 的 `aigc/multiImageFusion`、`aigc/taskQuery` 和 `aigc/uploadByBase64`。
- **图转视频**：适用于从图片或图片组生成可控时长的视频，也支持参考视频、模板、运镜和尾帧，使用 `linkfox-aigc-image-to-video` 的 `aigc/imageToVideo`、`aigc/taskQuery` 和 `aigc/uploadByBase64`。
- **带货口播视频**：适用于把商品图和卖点脚本转成电商口播视频，使用 `linkfox-aigc-sales-video` 的 `aigc/salesVideo`、`aigc/taskQuery` 和 `aigc/uploadByBase64`。
- **商品视频复刻**：适用于参考视频、商品图和销售地区或语言驱动的相似营销视频，使用 `linkfox-aigc-video-reclone` 的 `aigc/videoReclone`、`aigc/taskQuery` 和 `aigc/uploadByBase64`。
- **视频编辑**：适用于背景替换、风格调整和按指令修改已有视频，使用 `linkfox-aigc-video-edit` 的 `aigc/videoEditing`、`aigc/taskQuery` 和 `aigc/uploadByBase64`。
- **视频翻译与口型同步**：适用于把已有视频翻译到目标语言并按需同步口型，使用 `linkfox-aigc-video-translate` 的 `aigc/videoTranslation`、`aigc/taskQuery` 和 `aigc/uploadByBase64`。

### 边界与限制

- 这是素材生成和编辑能力，不负责发布到电商平台、店铺装修、广告投放、订单履约、版权或合规结论。
- 不能把本地路径直接放入生成参数。对包含 `aigc/uploadByBase64` 的流程，先把文件编码后调用该 endpoint，成功取得 `viewUrl` 再提交创建任务；上传失败时停止，不提交生成任务。
- 公开 URL 是否需要上传由对应 reference 决定。只要该 endpoint 要求前置素材上传，就不能直接复用外部 URL；轮询时不得重复上传。
- 模型 code、provider、videoType、签名 URL、原始 Base64、认证信息和内部工具标识不展示给用户。向用户解释模型时只用 reference 中的说明名称。
- 异步创建返回 `taskId` 不代表成品已经生成。超时只保留并查询原任务，不自动重建、更换模型、扩大数量或重复扣费。
- 当前接口未返回的单项错误、尺寸、格式或扩展字段不得推断；缺少可用模型或不支持的参数时应按真实错误提示用户修正。

## 工具选择指南

| 需求 / 用户说 | 默认推荐 | 何时换用其他 |
|---|---|---|
| “生成一张商品图”“文生图”“参考图改造” | `linkfox-aigc-imagegen` | 已有图片需要精确编辑时用单图编辑；多张图要合成时用多图融合编辑 |
| “写商品描述”“分析图片或视频”“生成营销文案” | `linkfox-aigc-textgen` | 若文案要直接驱动后续图像或视频任务，先完成生文并把返回内容作为下游 prompt |
| “一张图做动态”“首尾帧视频” | `linkfox-aigc-videogen` | 多张参考图、HappyHorse 多图入口或复杂图片组用多参考图生视频；需要模板或商品卖点口播用图转视频或带货口播 |
| “多张图生成视频” | `linkfox-aigc-videogen-multi` | 如果用户只有一张图且需要尾帧，优先单图或首尾帧入口；不要为了凑多图改写请求 |
| “商品套图”“服装套图”“A+” | 按商品或服装主题分别选 `linkfox-aigc-product-suite` 或 `linkfox-aigc-clothing-suite` | 只需改一张图用单图编辑；需要多图搭配合成用多图融合编辑 |
| “把图片变成视频”“商品模板视频” | `linkfox-aigc-image-to-video` | 需要口播脚本和商品卖点用带货口播；已有视频需改造用视频编辑 |
| “商品口播”“带货视频” | `linkfox-aigc-sales-video` | 用户要复刻参考视频结构用商品视频复刻；只做运动效果用图转视频 |
| “复刻这个商品视频”“换成我的商品” | `linkfox-aigc-video-reclone` | 只改已有视频画面用视频编辑；只翻语言和口型用视频翻译 |
| “翻译视频”“换语言”“口型同步” | `linkfox-aigc-video-translate` | 用户要求改变画面内容或风格时用视频编辑，不要把翻译字段当编辑 prompt |

选择时先按输入媒体数量和目标输出确定入口，再按是否需要模板、口播、复刻或翻译细分；最后读取对应 reference 核对必填字段、模型限制和积分风险。相近入口不能通过拼接字段混用。

## 业务需求路由速查

| 子能力 | 业务能力 | reference | 原 endpoint | 精确 `toolName` |
|---|---|---|---|---|
| linkfox-aigc-imagegen | 通用图片生成 | [linkfox-aigc-imagegen.md](references/linkfox-aigc-imagegen.md) | `/aigc/imageGenAsync` | `aigc/imageGenAsync` |
| linkfox-aigc-imagegen | 图片任务查询 | [linkfox-aigc-imagegen.md](references/linkfox-aigc-imagegen.md) | `/aigc/taskQuery` | `aigc/taskQuery` |
| linkfox-aigc-textgen | 文本生成 | [linkfox-aigc-textgen.md](references/linkfox-aigc-textgen.md) | `/aigc/textGenAsync` | `aigc/textGenAsync` |
| linkfox-aigc-textgen | 文本任务查询 | [linkfox-aigc-textgen.md](references/linkfox-aigc-textgen.md) | `/aigc/textTaskQuery` | `aigc/textTaskQuery` |
| linkfox-aigc-videogen | 单图或首尾帧视频生成 | [linkfox-aigc-videogen.md](references/linkfox-aigc-videogen.md) | `/aigc/videoGenAsync` | `aigc/videoGenAsync` |
| linkfox-aigc-videogen | 视频任务查询 | [linkfox-aigc-videogen.md](references/linkfox-aigc-videogen.md) | `/aigc/taskQuery` | `aigc/taskQuery` |
| linkfox-aigc-videogen-multi | 多参考图视频生成 | [linkfox-aigc-videogen-multi.md](references/linkfox-aigc-videogen-multi.md) | `/aigc/multiImageVideoGenAsync` | `aigc/multiImageVideoGenAsync` |
| linkfox-aigc-videogen-multi | 多图视频任务查询 | [linkfox-aigc-videogen-multi.md](references/linkfox-aigc-videogen-multi.md) | `/aigc/taskQuery` | `aigc/taskQuery` |
| linkfox-aigc-product-suite | 商品营销套图生成 | [linkfox-aigc-product-suite.md](references/linkfox-aigc-product-suite.md) | `/aigc/productMarketMaterial` | `aigc/productMarketMaterial` |
| linkfox-aigc-product-suite | 商品营销任务查询 | [linkfox-aigc-product-suite.md](references/linkfox-aigc-product-suite.md) | `/aigc/taskQuery` | `aigc/taskQuery` |
| linkfox-aigc-product-suite | 商品素材 Base64 上传 | [linkfox-aigc-product-suite.md](references/linkfox-aigc-product-suite.md) | `/aigc/uploadByBase64` | `aigc/uploadByBase64` |
| linkfox-aigc-clothing-suite | 服装营销套图生成 | [linkfox-aigc-clothing-suite.md](references/linkfox-aigc-clothing-suite.md) | `/aigc/wearCollection` | `aigc/wearCollection` |
| linkfox-aigc-clothing-suite | 服装营销任务查询 | [linkfox-aigc-clothing-suite.md](references/linkfox-aigc-clothing-suite.md) | `/aigc/taskQuery` | `aigc/taskQuery` |
| linkfox-aigc-clothing-suite | 服装素材 Base64 上传 | [linkfox-aigc-clothing-suite.md](references/linkfox-aigc-clothing-suite.md) | `/aigc/uploadByBase64` | `aigc/uploadByBase64` |
| linkfox-aigc-image-edit | 单图编辑 | [linkfox-aigc-image-edit.md](references/linkfox-aigc-image-edit.md) | `/aigc/imageEdit` | `aigc/imageEdit` |
| linkfox-aigc-image-edit | 单图编辑任务查询 | [linkfox-aigc-image-edit.md](references/linkfox-aigc-image-edit.md) | `/aigc/taskQuery` | `aigc/taskQuery` |
| linkfox-aigc-image-edit | 编辑素材 Base64 上传 | [linkfox-aigc-image-edit.md](references/linkfox-aigc-image-edit.md) | `/aigc/uploadByBase64` | `aigc/uploadByBase64` |
| linkfox-aigc-multi-image-edit | 多图融合编辑 | [linkfox-aigc-multi-image-edit.md](references/linkfox-aigc-multi-image-edit.md) | `/aigc/multiImageFusion` | `aigc/multiImageFusion` |
| linkfox-aigc-multi-image-edit | 多图融合任务查询 | [linkfox-aigc-multi-image-edit.md](references/linkfox-aigc-multi-image-edit.md) | `/aigc/taskQuery` | `aigc/taskQuery` |
| linkfox-aigc-multi-image-edit | 融合素材 Base64 上传 | [linkfox-aigc-multi-image-edit.md](references/linkfox-aigc-multi-image-edit.md) | `/aigc/uploadByBase64` | `aigc/uploadByBase64` |
| linkfox-aigc-image-to-video | 图转视频 | [linkfox-aigc-image-to-video.md](references/linkfox-aigc-image-to-video.md) | `/aigc/imageToVideo` | `aigc/imageToVideo` |
| linkfox-aigc-image-to-video | 图转视频任务查询 | [linkfox-aigc-image-to-video.md](references/linkfox-aigc-image-to-video.md) | `/aigc/taskQuery` | `aigc/taskQuery` |
| linkfox-aigc-image-to-video | 图转视频素材 Base64 上传 | [linkfox-aigc-image-to-video.md](references/linkfox-aigc-image-to-video.md) | `/aigc/uploadByBase64` | `aigc/uploadByBase64` |
| linkfox-aigc-sales-video | 带货口播视频 | [linkfox-aigc-sales-video.md](references/linkfox-aigc-sales-video.md) | `/aigc/salesVideo` | `aigc/salesVideo` |
| linkfox-aigc-sales-video | 带货视频任务查询 | [linkfox-aigc-sales-video.md](references/linkfox-aigc-sales-video.md) | `/aigc/taskQuery` | `aigc/taskQuery` |
| linkfox-aigc-sales-video | 带货素材 Base64 上传 | [linkfox-aigc-sales-video.md](references/linkfox-aigc-sales-video.md) | `/aigc/uploadByBase64` | `aigc/uploadByBase64` |
| linkfox-aigc-video-reclone | 商品视频复刻 | [linkfox-aigc-video-reclone.md](references/linkfox-aigc-video-reclone.md) | `/aigc/videoReclone` | `aigc/videoReclone` |
| linkfox-aigc-video-reclone | 复刻任务查询 | [linkfox-aigc-video-reclone.md](references/linkfox-aigc-video-reclone.md) | `/aigc/taskQuery` | `aigc/taskQuery` |
| linkfox-aigc-video-reclone | 复刻素材 Base64 上传 | [linkfox-aigc-video-reclone.md](references/linkfox-aigc-video-reclone.md) | `/aigc/uploadByBase64` | `aigc/uploadByBase64` |
| linkfox-aigc-video-edit | 视频编辑 | [linkfox-aigc-video-edit.md](references/linkfox-aigc-video-edit.md) | `/aigc/videoEditing` | `aigc/videoEditing` |
| linkfox-aigc-video-edit | 视频编辑任务查询 | [linkfox-aigc-video-edit.md](references/linkfox-aigc-video-edit.md) | `/aigc/taskQuery` | `aigc/taskQuery` |
| linkfox-aigc-video-edit | 视频编辑素材 Base64 上传 | [linkfox-aigc-video-edit.md](references/linkfox-aigc-video-edit.md) | `/aigc/uploadByBase64` | `aigc/uploadByBase64` |
| linkfox-aigc-video-translate | 视频翻译与口型同步 | [linkfox-aigc-video-translate.md](references/linkfox-aigc-video-translate.md) | `/aigc/videoTranslation` | `aigc/videoTranslation` |
| linkfox-aigc-video-translate | 翻译任务查询 | [linkfox-aigc-video-translate.md](references/linkfox-aigc-video-translate.md) | `/aigc/taskQuery` | `aigc/taskQuery` |
| linkfox-aigc-video-translate | 翻译素材 Base64 上传 | [linkfox-aigc-video-translate.md](references/linkfox-aigc-video-translate.md) | `/aigc/uploadByBase64` | `aigc/uploadByBase64` |

每个 reference 都包含该子能力的完整 endpoint 清单、必填字段、关键可选字段、异步响应和特殊限制。成品不保留源脚本，因为它们承担旧传输层；没有需要分发的本地 helper。

## MCP 调用方式

- 只调用 `LinkFox.proxy_call`，结构固定为 `{"toolName":"<精确 endpoint 去掉前导斜杠>","arguments":{...}}`。`toolName` 区分大小写，不使用 inventory 展示名、源标识或自造别名。
- 原请求对象直接放到 `arguments`。通用生图、生文和首尾帧入口按其 reference 使用字段；商品、服装和 V3 业务入口按 reference 使用外层 `params` 包装；不得再包 `body`、`data`、`params` 或第二层 `arguments`。
- `aigc/uploadByBase64` 的业务参数是 `fileName` 与 `base64`，返回的 `viewUrl` 才能填入后续生成请求。只在路由表列出的子能力中使用该上传 endpoint。上传失败立即停止；成功后不得在轮询阶段重复上传。
- WorkBuddy 会自动注入 Linkfox Authorization。不要索取、展示、写入或配置任何凭证，也不要把认证字段放进 `arguments`。
- 先判断 MCP 连接和 `proxy_call` schema，再检查 `isError`；随后解析 `structuredContent` 或 text content。text JSON 只解析一次，之后再检查 `errcode`、`errorCode`、`code`、`success` 和消息字段。HTTP 或 MCP 成功不等于业务成功。
- 创建成功后只保存服务端返回的 `taskId`。图片和视频按 `aigc/taskQuery` 查询，文本按 `aigc/textTaskQuery` 查询；处理中按 reference 建议间隔查询，超时保留 taskId 并让用户稍后续查，不重建任务。
- 同一会话中相同参数组合只创建一次。失败、超时、下载失败或查询异常都不能自动换模型或再次提交收费创建；可在不创建新任务的前提下重查原 taskId。
- `structuredContent` 或查询响应只展示真实返回的状态、结果列表、文本内容和可用费用字段。不要承诺 MCP 自动下载、缓存、落盘或生成 stdout 摘要；若 WorkBuddy 没有本地媒体路径，就展示可信结果 URL 或说明暂不可交付。

## 使用示例

以下示例展示传给 `proxy_call` 的关键结构。示例 URL 仅用于说明字段形状，不得直接作为收费测试素材。

### 1. 通用图片生成与查询

```json
{"toolName":"aigc/imageGenAsync","arguments":{"prompt":"studio product photo of a reusable bottle, clean background","provider":"LF_BN_3","outputNum":1,"resolution":"1K","aspectRatio":"1:1","quality":"high"}}
```

创建成功后用 `{"toolName":"aigc/taskQuery","arguments":{"taskId":"<创建返回的 taskId>"}}` 查询。`imageUrls` 可选；有参考图时先确认 URL 可访问并保持顺序。面向用户只说模型说明名称，不展示 provider code。

### 2. 生文或视频分析

```json
{"toolName":"aigc/textGenAsync","arguments":{"prompt":"Write five concise US marketplace bullet points for this product","imageUrls":[],"model":"GEM_3_FLASH","thinkingLevel":"minimal"}}
```

创建后用 `aigc/textTaskQuery` 传 `taskId`。需要图片或视频理解时，将公开媒体 URL 按 `imageUrls` 传入；纯文本必须传 `[]`。结果关注 `content` 和 token 字段，失败只呈现真实 `errorMsg`。

### 3. 商品套图

```json
{"toolName":"aigc/productMarketMaterial","arguments":{"params":{"imageList":["<已准备好的 viewUrl>"],"sellerPoint":"Lightweight and easy to clean","sellerTypeNum":2,"sceneTypeNum":2,"whiteBgTypeNum":1,"aPlusNum":1,"isExtractPrePoint":false}}}
```

本入口要求 `params.imageList`，数量字段上限通常为每类 12 张，卖点未自动提取时传 `sellerPoint`。完成后以 `aigc/taskQuery` 查询结果，不要依据创建时的零费用字段判断免费。

### 4. 图转视频与带货视频

```json
{"toolName":"aigc/imageToVideo","arguments":{"params":{"videoType":"doubao-seedance-2-5","videoTime":10,"imageUrl":"<已准备好的 viewUrl>","prompt":"Show the product from three angles in a bright home setting","resolution":"720P","aspectRatio":"16:9"}}}
```

如果用户要口播，改用 `aigc/salesVideo`，例如 `params` 至少包含 `videoType`、`prompt` 和非空 `imageList`。图片或视频素材先调用本子能力对应的 `aigc/uploadByBase64`，请求形如 `{"fileName":"product.jpg","base64":"<运行时编码>"}`，成功后只使用返回的 `viewUrl`。

### 5. 视频翻译

```json
{"toolName":"aigc/videoTranslation","arguments":{"params":{"sourceVideoUrl":"<已准备好的 viewUrl>","targetLanguage":"en","lipSync":true}}}
```

`targetLanguage` 使用支持的短代码或 BCP-47 代码，源语言由服务端识别。需要复刻、编辑或改画面时不要把这些需求塞进翻译接口；应按工具选择指南切换入口。

## 展示规则

1. 先展示任务阶段：创建成功、处理中、成功或失败，并在创建成功时记录 `taskId`；不能把 `taskId` 当成成品。
2. 成功的图片或视频只展示真实返回的媒体结果；如果返回 URL 具备签名或短期有效性，不把它包装成永久下载链接。没有本地交付能力时明确说明结果为远端 URL。
3. 文本结果展示 `content`，必要时说明输入、输出和总 token；不要将 JSON 信封、内部字段或原始协议响应整段复制给用户。
4. 说明模型时使用当前 reference 或动态配置的用户友好名称；隐藏 provider、videoType、模型 code、渠道名、内部 endpoint 和认证信息。
5. 展示生成数量、语言、分辨率、比例、时长、口型同步、参考素材数量等真实返回或用户明确指定的条件；接口未返回的尺寸、格式、单项错误或费用不要推断。
6. 失败时引用真实错误消息并给出最小修正建议。401 或连接问题按认证章节处理，402 或余额不足停止收费调用，403 视为权限或归属问题，400/10007 等参数错误回到对应 reference 核对字段。
7. 任何本地附件上传失败都不继续创建；不要展示 Base64 或本地临时内容。查询超时保留 taskId，告知可续查且不自动重建。

## 解决认证和积分问题

发生异常时读取 [references/onboarding.md](references/onboarding.md)，并按下面分层处理。WorkBuddy 自动注入 Authorization，不索取、不展示、不配置凭证。

- **MCP 或 `proxy_call` 缺失**：停止业务调用，提示安装或重载 LinkFox 连接器；禁止回退命令行 HTTP、旧脚本或其他网络入口。
- **MCP 连接返回 401**：按 onboarding 引导检查连接状态并重载；不要让用户在对话中粘贴凭证。
- **代理调用成功但下游返回 401**：说明下游授权或归属不可用，停止创建和重试，按 onboarding 处理。
- **下游返回 402、余额不足或套餐不可用**：停止新的收费任务，读取 onboarding 给出充值或账户处理引导，由用户明确决定后续操作。
- **403**：按权限、资源归属或素材访问问题处理，不把它误判为余额不足，也不自动重试。
- **400、10007、404 及其他业务错误**：保留真实错误信息，回到对应 reference 修正参数或 taskId；没有证据时不猜测原因。

## 积分消耗说明

> 用户会因积分消耗而支付费用。请充分评估：当需要高频调用本技能，或用户对积分消耗量预期不足时，务必提醒用户，由用户决定是否继续。
