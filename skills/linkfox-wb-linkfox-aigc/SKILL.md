---
name: linkfox-wb-linkfox-aigc
display_name: LinkFox 跨境商品图片和视频
display_name_en: LinkFox Product Images and Video
description: 面向跨境电商的商品图像、视频与文案创作，支持营销套图、智能修图、视频生成、图转视频、带货口播、视频复刻、编辑和翻译。
description_zh: 根据提示词、商品图片和品牌要求生成商品与服装营销套图，支持单图修图、多图融合、文案及媒体理解，并可生成单图或多场景视频、模板化商品视频和带货口播视频，复刻参考视频、编辑已有视频及翻译视频语音和同步口型。适用于Listing、广告创意与商品内容本地化。
description_en: Create product and apparel marketing images, videos and copy. Supports image editing and fusion, single-image and multi-reference video generation, product video templates, sales narration, video recreation, editing, translation and lip sync, plus text generation and media understanding.
icon: icons/logo.png
version: 3.1.0
author: Linkfox
---

> [!IMPORTANT]
本 Skill 必须依赖 MCP “LinkFox”。如未安装该MCP，请明确通知用户：
> 请先安装 LinkFox 连接器：
> - 在 WorkBuddy 左侧找到 “专家·技能·连接器” → “连接器”；
> - 搜索关键词 “LinkFox”，并安装连接器 “LinkFox”（注意：是 linkfox，不是 linkfox-product-selection），按指引完成登录授权；
> - 返回 WorkBuddy 重试。

# LinkFox 商品图像与视频（LinkFox Product Images and Video）

根据商品素材、提示词和用途生成或编辑跨境营销内容，交付文本、图片、视频链接及任务编号。覆盖13个子能力、15个生成与查询 endpoint，另有 AIGC 素材上传与通用文件上传2个辅助 endpoint。

## 能力边界

- 通用生图：文生图或参考图生图，使用 `linkfox-aigc-imagegen` 的 `/aigc/imageGenAsync`，精确 `toolName` 为 `aigc/imageGenAsync`。
- 文本与媒体理解：营销文案、改写及图片或视频分析，使用 `linkfox-aigc-textgen` 的 `/aigc/textGenAsync`，精确 `toolName` 为 `aigc/textGenAsync`。
- 商品营销套图：非服装商品的白底、场景、特写、卖点及 A+ 图，使用 `linkfox-aigc-product-suite` 的 `/aigc/productMarketMaterial`，精确 `toolName` 为 `aigc/productMarketMaterial`。
- 服装营销套图：服装的模特、种草、尺码、卖点、白底及 A+ 图，使用 `linkfox-aigc-clothing-suite` 的 `/aigc/wearCollection`，精确 `toolName` 为 `aigc/wearCollection`。
- 智能修图：按要求修改一张原图，使用 `linkfox-aigc-image-edit` 的 `/aigc/imageEdit`，精确 `toolName` 为 `aigc/imageEdit`。
- 多图融合修图：按素材角色融合多张参考图，使用 `linkfox-aigc-multi-image-edit` 的 `/aigc/multiImageFusion`，精确 `toolName` 为 `aigc/multiImageFusion`。
- 视频生成：单图或所选模型支持的首尾帧生成，使用 `linkfox-aigc-videogen` 的 `/aigc/videoGenAsync`，精确 `toolName` 为 `aigc/videoGenAsync`。
- 多场景视频生成：结合多参考图的商品、人物与场景生成视频，使用 `linkfox-aigc-videogen-multi` 的 `/aigc/multiImageVideoGenAsync`，精确 `toolName` 为 `aigc/multiImageVideoGenAsync`。
- 图转视频：商品图、模板及可选参考视频驱动的视频创作，使用 `linkfox-aigc-image-to-video` 的 `/aigc/imageToVideo`，精确 `toolName` 为 `aigc/imageToVideo`。
- 带货口播视频：按商品图和口播脚本生成营销视频，使用 `linkfox-aigc-sales-video` 的 `/aigc/salesVideo`，精确 `toolName` 为 `aigc/salesVideo`。
- 商品视频复刻：参考视频与当前商品图结合生成，使用 `linkfox-aigc-video-reclone` 的 `/aigc/videoReclone`，精确 `toolName` 为 `aigc/videoReclone`。
- 视频编辑：按指令修改原视频，可选参考图，使用 `linkfox-aigc-video-edit` 的 `/aigc/videoEditing`，精确 `toolName` 为 `aigc/videoEditing`。
- 视频翻译：翻译原视频语音并可同步口型，使用 `linkfox-aigc-video-translate` 的 `/aigc/videoTranslation`，精确 `toolName` 为 `aigc/videoTranslation`。

套图由服务端一次创建，品牌要求直接填可选 `brandKey`，自动卖点提取使用 `isExtractPrePoint`。不要求先提取品牌基因，不在本地逐张编排套图。尺码、规格和功效等事实必须有用户资料支持，缺少尺码数据先补充资料，不从图片猜测尺寸。

不执行平台发布、店铺操作或知识产权检测。视频内容理解只产出分析文本；用户要求视频产物时选择相应视频接口。生成、复刻、翻译和编辑结果不等于平台审核通过。

## 工具选择指南

| 需求 / 用户说 | 默认推荐 | 何时换用其他 |
|---|---|---|
| “按描述生成一张广告图” | 通用生图 | 有原图且要求局部修改时用智能修图 |
| “写英文卖点”或“分析这段视频” | 文本生成 | 要求图片产物时选择相应图像能力 |
| “给商品做一套主图和A+” | 商品营销套图 | 服装用服装套图，单张自定义创意可用通用生图 |
| “做模特图、种草图和尺码图” | 服装营销套图 | 只改已有模特图时用智能修图 |
| “把这张图背景换成白色” | 智能修图 | 多图分别提供商品、背景或搭配元素时用多图融合 |
| “把图一商品放进图二场景” | 多图融合修图 | 只有一张原图时用智能修图 |
| “让这张图动起来”或“从首帧过渡到尾帧” | 视频生成 | 需要商品模板、参考视频或专用模型能力时用图转视频，尾帧必须符合该入口的模型限制 |
| “结合这些商品图和场景做视频” | 多场景视频生成 | 需要产品展示、UGC等模板或参考视频动作时用图转视频 |
| “用商品图做产品展示、UGC或家居场景视频” | 图转视频 | 明确的带货口播脚本用口播视频，有参考视频结构需复刻时用复刻 |
| “按这些卖点做英文带货口播” | 带货口播视频 | 仅需要文案时用文本生成，已有视频只需译配时用视频翻译 |
| “参考这个视频，换成我的商品” | 商品视频复刻 | 保留原视频并局部修改时用视频编辑 |
| “修改视频背景或风格” | 视频编辑 | 只翻译语音、同步口型时用视频翻译 |
| “把这段视频翻译成英语并对口型” | 视频翻译 | 只要视频内容分析文本时用文本生成 |

先确定交付物，再确定素材角色、类型和数量。沿用用户已明确的模型、语言、比例与数量，只补充影响结果或费用的缺失信息。不因为套图含多个图片类型而额外创建多次通用生图，也不为普通单图任务先做一次收费文本分析。

## 业务需求路由速查

| 子能力 | 业务能力 | reference | 原 endpoint | 精确 `toolName` |
|---|---|---|---|---|
| `linkfox-aigc-imagegen` | 创建通用生图 | [图像生成](references/linkfox-aigc-imagegen.md) | `/aigc/imageGenAsync` | `aigc/imageGenAsync` |
| `linkfox-aigc-imagegen` | 查询图片 | 同上 | `/aigc/taskQuery` | `aigc/taskQuery` |
| `linkfox-aigc-textgen` | 创建文本或媒体理解任务 | [文本生成](references/linkfox-aigc-textgen.md) | `/aigc/textGenAsync` | `aigc/textGenAsync` |
| `linkfox-aigc-textgen` | 查询文本 | 同上 | `/aigc/textTaskQuery` | `aigc/textTaskQuery` |
| `linkfox-aigc-product-suite` | 创建商品套图 | [商品营销套图](references/linkfox-aigc-product-suite.md) | `/aigc/productMarketMaterial` | `aigc/productMarketMaterial` |
| `linkfox-aigc-product-suite` | 查询套图 | 同上 | `/aigc/taskQuery` | `aigc/taskQuery` |
| `linkfox-aigc-clothing-suite` | 创建服装套图 | [服装营销套图](references/linkfox-aigc-clothing-suite.md) | `/aigc/wearCollection` | `aigc/wearCollection` |
| `linkfox-aigc-clothing-suite` | 查询套图 | 同上 | `/aigc/taskQuery` | `aigc/taskQuery` |
| `linkfox-aigc-image-edit` | 创建单图修图 | [智能修图](references/linkfox-aigc-image-edit.md) | `/aigc/imageEdit` | `aigc/imageEdit` |
| `linkfox-aigc-image-edit` | 查询修图 | 同上 | `/aigc/taskQuery` | `aigc/taskQuery` |
| `linkfox-aigc-multi-image-edit` | 创建多图融合 | [多图融合修图](references/linkfox-aigc-multi-image-edit.md) | `/aigc/multiImageFusion` | `aigc/multiImageFusion` |
| `linkfox-aigc-multi-image-edit` | 查询融合图 | 同上 | `/aigc/taskQuery` | `aigc/taskQuery` |
| `linkfox-aigc-videogen` | 创建单图或首尾帧视频 | [视频生成](references/linkfox-aigc-videogen.md) | `/aigc/videoGenAsync` | `aigc/videoGenAsync` |
| `linkfox-aigc-videogen` | 查询视频 | 同上 | `/aigc/taskQuery` | `aigc/taskQuery` |
| `linkfox-aigc-videogen-multi` | 创建多参考图视频 | [多场景视频生成](references/linkfox-aigc-videogen-multi.md) | `/aigc/multiImageVideoGenAsync` | `aigc/multiImageVideoGenAsync` |
| `linkfox-aigc-videogen-multi` | 查询视频 | 同上 | `/aigc/taskQuery` | `aigc/taskQuery` |
| `linkfox-aigc-image-to-video` | 创建商品图转视频 | [图转视频](references/linkfox-aigc-image-to-video.md) | `/aigc/imageToVideo` | `aigc/imageToVideo` |
| `linkfox-aigc-image-to-video` | 查询视频 | 同上 | `/aigc/taskQuery` | `aigc/taskQuery` |
| `linkfox-aigc-sales-video` | 创建带货口播视频 | [带货口播视频](references/linkfox-aigc-sales-video.md) | `/aigc/salesVideo` | `aigc/salesVideo` |
| `linkfox-aigc-sales-video` | 查询视频 | 同上 | `/aigc/taskQuery` | `aigc/taskQuery` |
| `linkfox-aigc-video-reclone` | 创建商品视频复刻 | [商品视频复刻](references/linkfox-aigc-video-reclone.md) | `/aigc/videoReclone` | `aigc/videoReclone` |
| `linkfox-aigc-video-reclone` | 查询复刻视频 | 同上 | `/aigc/taskQuery` | `aigc/taskQuery` |
| `linkfox-aigc-video-edit` | 创建视频编辑 | [视频编辑](references/linkfox-aigc-video-edit.md) | `/aigc/videoEditing` | `aigc/videoEditing` |
| `linkfox-aigc-video-edit` | 查询编辑视频 | 同上 | `/aigc/taskQuery` | `aigc/taskQuery` |
| `linkfox-aigc-video-translate` | 创建视频翻译 | [视频翻译](references/linkfox-aigc-video-translate.md) | `/aigc/videoTranslation` | `aigc/videoTranslation` |
| `linkfox-aigc-video-translate` | 查询翻译视频 | 同上 | `/aigc/taskQuery` | `aigc/taskQuery` |
| 套图、修图与专用视频共用 | 上传生成素材 | [AIGC素材上传](references/aigc-upload.md) | `/aigc/uploadByBase64` | `aigc/uploadByBase64` |
| 通用文件辅助 | 获取OSS上传凭证 | [文件上传](references/file-upload.md) | `/oss/getStsVoucherByAPI` | `oss/getStsVoucherByAPI` |

本地辅助 `scripts/local/download_results.py` 下载成功任务返回的图片或视频 URL，不创建或查询任务、不访问业务网关。参数表和模型限制按需读取对应 reference；套图、修图及专用视频的外层契约见 [material-common.md](references/material-common.md)，视频查询、模型与交付规则见 [video-common.md](references/video-common.md)。

## MCP 调用方式

所有业务请求使用 `LinkFox.proxy_call`，`toolName` 为原 endpoint 去掉前导 `/` 的精确值，保留大小写。原请求对象直接放入 `arguments`，不得额外包 `body` / `data` 或第二层 `arguments`。

**区分两类请求结构：**通用生图、生文、`videoGenAsync`、`multiImageVideoGenAsync` 及查询参数直接位于 `arguments`，例如 `arguments.prompt` 或 `arguments.taskId`。商品套图、服装套图、两种修图，以及图转视频、口播、复刻、编辑、翻译原生具有外层结构，必须保留 `arguments.requestId` 和 `arguments.params`，业务参数放进 `params`，创建时不传顶层 `memberId`。不能把这些接口的业务字段提升到顶层，也不能给直接传参的接口增加 `params`。视频的 `videoType` 枚举、声音、尾帧、参考图数量和时长规则按所选入口读取，不能互换。

WorkBuddy 自动注入 Authorization，不索取、不展示、不配置凭证，请求不加入 headers、API Key、token、JWT 或手机号。MCP 不可用时读取 [onboarding.md](references/onboarding.md)，不得回退 HTTP 或旧网关脚本。

### 素材准备

- 套图、两种修图与五个专用视频接口：先读取 [aigc-upload.md](references/aigc-upload.md)，本地文件与外部 URL 都通过 `aigc/uploadByBase64` 转为 `viewUrl`。仅复用已知上传成功的 `viewUrl`，不凭域名判断上传状态。保持图片或视频数组顺序，独立的原视频、参考视频、尾帧、模特图、场景图字段也要处理；上传失败不创建任务。视频翻译只需要原视频，视频编辑参考图可选。
- 通用生图、媒体理解与前两项通用视频生成可使用公开可访问的 URL。需要把本地文件或产物公开时，读取并按本 skill 内置的 [references/file-upload.md](references/file-upload.md) 执行。通用 OSS URL 不替代上述九类专用接口要求的 `viewUrl`。
- 仅上传本次任务需要的素材，保存来源与成功 URL 的映射；查询不重新上传。

### 创建、查询和失败处理

1. 创建前确定类型、数量、模型、分辨率、比例及文案语言；视频还需确定时长、声音与素材模式，翻译选择目标语言及口型同步，说明费用未知项。用户已授权的具体生成请求直接执行；新增图片、视频变体、参考视频、手机版 A+ 或额外收费分析必须符合用户要求。
2. 每个请求只创建一次。九类使用原生外层的接口使用唯一 `requestId`，保存返回的 `taskId` 和查询接口。不能把 `requestId` 当作重复创建一定不扣费的保证。
3. 先检查连接、schema 和 `isError`，再读取 structured content 或解析一次 text JSON，检查下游 `error`、`errcode`、`errorCode`、`code`、`success` 和消息字段。空体、无 `taskId` 或无法识别的响应不能当作创建成功。
4. 创建后可查询一次。`PROCESSING` 时返回原编号，图片或文本建议至少等待10秒，视频建议约2分钟；用户后续明确继续时再查询一次，不自动循环。后续获准的状态查询可使用相同 `taskId`，不得重复创建。
5. `SUCCESS` 时使用实际 `resultList[].url` 或文本 `content`；成功但结果为空时报告异常。`FAILED` 展示脱敏 `errorMsg`，不自动重试、换模型或改素材。网络中断导致是否创建未知时说明不确定性，不重新提交。
6. 需要本地图片或视频时，将成功查询的业务对象保存为 UTF-8 JSON，执行 `python <skill-root>/scripts/local/download_results.py <response.json> --out-dir <directory>`。下载失败保留 URL，只补下载，不重新生成。

MCP 不承诺旧脚本的缓存、自动落盘或 stdout 摘要。追溯记录只包含任务编号、请求摘要与脱敏业务响应，不包含凭证或素材 Base64。

## 使用示例

执行前替换占位素材与请求编号，不得用示例地址发起收费测试。内部模型值仅用于调用，面向用户使用可读模型名称。套图、修图和五项专用视频的素材 URL 均代表上传成功后的 `viewUrl`。

**通用生图**：无参考图时 `imageUrls` 可为空。示例生成1张正方形图片，模型显示名为“LF全能模型 Pro”。

```json
{"toolName":"aigc/imageGenAsync","arguments":{"imageUrls":[],"prompt":"A minimalist studio photograph of a ceramic cup on a neutral background","provider":"LF_BN_3","outputNum":1,"resolution":"1K","aspectRatio":"1:1"}}
```

**文本生成**：纯文本传 `imageUrls: []`；分析媒体时替换为真实 URL，模型及思考等级见对应 reference。

```json
{"toolName":"aigc/textGenAsync","arguments":{"prompt":"将已确认卖点改写为三条英文短文案，不增加新事实：便携、可拆洗。","imageUrls":[],"model":"GEM_3_FLASH","thinkingLevel":"minimal"}}
```

**商品营销套图**：一次创建1张卖点图和1张场景图，其余类型默认0。未开启自动提取必须提供真实卖点。

```json
{"toolName":"aigc/productMarketMaterial","arguments":{"requestId":"<unique-product-request>","params":{"imageList":["https://example.com/uploaded-product-viewUrl.png"],"sellerPoint":"便携，可拆洗","provider":"GPT_2_5_IMAGE","resolution":"2K","aspectRatio":"1:1","quality":"medium","sellerTypeNum":1,"sceneTypeNum":1,"brandKey":{"language":"英语","platform":"亚马逊"}}}}
```

**服装营销套图**：一次创建1张模特图和1张白底图。模特、场景描述写入 `modelAndSceneInfo`；尺码图需要用户提供真实尺码。

```json
{"toolName":"aigc/wearCollection","arguments":{"requestId":"<unique-clothing-request>","params":{"imageList":["https://example.com/uploaded-clothing-viewUrl.jpg"],"sellerPoint":"用户已确认的面料与版型描述","provider":"GPT_2_5_IMAGE","resolution":"2K","aspectRatio":"3:4","modelTypeNum":1,"whiteTypeNum":1,"modelAndSceneInfo":"成年模特，简洁摄影棚背景"}}}
```

**智能修图**：使用单数 `imageUrl`，每任务输出1～4张；模板可能覆盖模型及提示词优化选项。

```json
{"toolName":"aigc/imageEdit","arguments":{"requestId":"<unique-edit-request>","params":{"imageUrl":"https://example.com/uploaded-source-viewUrl.png","prompt":"将背景改为纯白，保留商品形状、颜色和标识","provider":"GPT_2_5_IMAGE","outputNum":1,"resolution":"2K","aspectRatio":"1:1","quality":"medium","needOptimize":false}}}
```

**多图融合修图**：使用 `imageList`，明确素材角色；参考图上限依所选模型检查。

```json
{"toolName":"aigc/multiImageFusion","arguments":{"requestId":"<unique-fusion-request>","params":{"imageList":["https://example.com/uploaded-product-viewUrl.png","https://example.com/uploaded-scene-viewUrl.png"],"prompt":"保留第一张的商品外观，将商品自然放入第二张场景，匹配光影和透视","provider":"GPT_2_5_IMAGE","outputNum":1,"resolution":"2K","aspectRatio":"1:1","quality":"medium"}}}
```

**视频生成与多场景视频生成**：前者用 `imageUrl`，后者用 `imageList`，均直接传参数。下例为5秒 Seedance 2.0 视频；若用尾帧，必须重新核对所选入口和模型是否支持。

```json
{"toolName":"aigc/videoGenAsync","arguments":{"imageUrl":"https://example.com/public-first-frame.jpg","videoType":"SEED","videoTime":5,"prompt":"缓慢推进镜头展示商品细节","resolution":"720p","aspectRatio":"9:16"}}
```

```json
{"toolName":"aigc/multiImageVideoGenAsync","arguments":{"imageList":["https://example.com/public-product.jpg","https://example.com/public-scene.jpg"],"videoType":"SEED","videoTime":5,"prompt":"结合商品与场景参考，生成连贯展示镜头","resolution":"720p","aspectRatio":"9:16"}}
```

**图转视频**：商品展示模板与手写 `prompt` 二选一，素材使用上传后的 `viewUrl`。参考视频另有素材互斥与费用倍率，执行前读对应 reference。

```json
{"toolName":"aigc/imageToVideo","arguments":{"requestId":"<unique-image-video-request>","params":{"imageList":["https://example.com/uploaded-product-viewUrl.jpg"],"videoType":"doubao-seedance-2-5","videoTime":10,"templateKey":"product-showcase","productInfo":"用户已确认的商品外观和细节信息","language":"英文","saleCountry":"美国","resolution":"720p","aspectRatio":"9:16"}}}
```

**带货口播视频**：商品图和口播脚本必填，语言、语气及卖点要求写进 `prompt`，不增加未定义的声音或人物ID字段。

```json
{"toolName":"aigc/salesVideo","arguments":{"requestId":"<unique-sales-video-request>","params":{"imageList":["https://example.com/uploaded-product-viewUrl.jpg"],"videoType":"doubao-seedance-2-0","videoTime":10,"prompt":"用自然英文口播介绍用户已确认的商品卖点，结尾邀请了解详情","resolution":"720p","aspectRatio":"9:16"}}}
```

**商品视频复刻**：参考视频与商品图都上传；分辨率、市场和目标语言必填。下面不传 `prompt`，由服务端分析；已有最终脚本时传 `prompt` 将跳过分析。

```json
{"toolName":"aigc/videoReclone","arguments":{"requestId":"<unique-reclone-request>","params":{"refVideoUrl":"https://example.com/uploaded-reference-viewUrl.mp4","refImageList":["https://example.com/uploaded-product-viewUrl.jpg"],"videoType":"doubao-seedance-2-0","resolution":"720p","saleCountry":"US","targetLanguage":"en","videoTime":10}}}
```

**视频编辑**：原视频必填，参考图片可选。下例模型仅跟随原视频时长，`videoTime=-1`，不传固定秒数。

```json
{"toolName":"aigc/videoEditing","arguments":{"requestId":"<unique-video-edit-request>","params":{"sourceVideoUrl":"https://example.com/uploaded-source-viewUrl.mp4","prompt":"将背景替换为摄影棚，保留商品外观和主体动作","videoType":"kling-v3-omni","videoTime":-1}}}
```

**视频翻译**：目标语言与原视频必填，口型同步默认开启，所有模型跟随原视频时长，不传 `videoTime`。

```json
{"toolName":"aigc/videoTranslation","arguments":{"requestId":"<unique-video-translation-request>","params":{"sourceVideoUrl":"https://example.com/uploaded-source-viewUrl.mp4","targetLanguage":"en","lipSync":true}}}
```

图像及视频任务返回 `taskId` 后使用 `aigc/taskQuery`，文本任务使用 `aigc/textTaskQuery`，不能混用：

```json
{"toolName":"aigc/taskQuery","arguments":{"taskId":"<image-taskId>"}}
```

```json
{"toolName":"aigc/textTaskQuery","arguments":{"taskId":"<text-taskId>"}}
```

## 展示规则

1. 先交付可用产物：文本直接给内容，图片给预览，视频给可播放或可点击 URL；本地交付附真实路径。创建成功不表示媒体已生成。
2. 多张结果按实际 `type` 分类，不识别的标为未分类。分别列出计划数量和返回数量，不按返回顺序猜类型或承诺全部成功。
3. 未完成时展示任务编号和状态，失败给错误摘要与可行的下一步。不展示原始 MCP 包装、Base64 或认证信息。
4. 模型用可读名称。通用生图的 `LF_*` 别名与套图、修图的 `GPT_*` 等枚举不可直接互换，按对应 reference 填写。
5. 仅展示实际返回的计费字段及原单位；创建响应 `costToken=0` 不表示免费，费用缺失记为未知，不把历史扣点称为实时价格。
6. 商品事实来自用户资料。标注 AI 生成或模型分析性质，不声称平台审核、认证或侵权检测通过；单项错误、宽高、格式等未返回字段不能推断为已核实。
7. 视频模型名称和参数按各入口解释；实际音轨、口型或人物效果以结果为准，不把合成人物口播展示为真实用户背书。视频翻译应核对商品名、数字与单位，不声称已获人工审核。

## 解决认证和积分问题

遇到连接器缺失、认证、权限或积分异常时读取 [references/onboarding.md](references/onboarding.md)。WorkBuddy 自动注入 Authorization，不索取、不展示、不配置凭证。

| 异常层级 | 处理 |
|---|---|
| MCP 或 `proxy_call` 缺失 | 按开头提示安装或重载 LinkFox 连接器，停止业务调用 |
| MCP 连接 401 | 检查 WorkBuddy 登录与连接器授权，重载仍失败联系管理员 |
| 代理成功但下游 401 | 报告下游认证失败，不把凭证放入 `arguments` |
| 下游 402 / 积分不足 | 引导访问 `https://agent.linkfox.com/`，不自动选套餐、下单或支付 |
| 下游 403 | 报告权限或归属错误，不当作积分不足处理 |
| schema、参数或其他业务错误 | 保留错误码与脱敏消息，不猜工具名、不自动换参数重试 |

用户明确要求反馈时，可使用独立反馈接口 `https://skill-api.linkfox.com/api/v1/public/feedback`，字段为 `skillName`、`sentiment`、`category`、`content`。`skillName` 使用本 skill 名称，`sentiment` 取 `POSITIVE` / `NEUTRAL` / `NEGATIVE`，`category` 取 `BUG` / `COMPLAINT` / `SUGGESTION` / `OTHER`；只发送脱敏问题摘要。

## 积分消耗说明

> 用户会因积分消耗而支付费用。请充分评估：当需要高频调用本技能，或用户对积分消耗量预期不足时，务必提醒用户，由用户决定是否继续。
