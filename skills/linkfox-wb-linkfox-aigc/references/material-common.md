# 商品图像与专用视频任务共同契约

适用于 `aigc/productMarketMaterial`、`aigc/wearCollection`、`aigc/imageEdit`、`aigc/multiImageFusion`，以及 `aigc/imageToVideo`、`aigc/salesVideo`、`aigc/videoReclone`、`aigc/videoEditing`、`aigc/videoTranslation`。这些 endpoint 不带 `Async` 后缀，但仍创建异步任务；不要自行补后缀或改成下游版本化路径。下方套图条件和图像模型表仅适用于对应图像任务，视频规则另见 [video-common.md](video-common.md)。

## MCP 请求结构

```json
{"toolName":"aigc/imageEdit","arguments":{"requestId":"<unique-request-id>","title":"商品修图","params":{"imageUrl":"<uploaded-viewUrl>","prompt":"将背景改为白色","provider":"GPT_2_5_IMAGE","outputNum":1}}}
```

| 外层字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `requestId` | string | 否 | 建议使用唯一且稳定的业务请求ID；新任务新建，原任务不重复提交 |
| `chatId` | string | 否 | 已知的会话ID，最长128字符，不编造 |
| `messageId` | string | 否 | 已知的消息ID，最长128字符，不编造 |
| `title` | string | 否 | 展示标题 |
| `params` | object | 是 | 非空业务参数；完整字段见各能力 reference |

不传顶层 `memberId`；身份和渠道由 WorkBuddy 授权链路处理。原生 `params` 必须保留，不再包 `body` / `data`。所有素材按 [aigc-upload.md](aigc-upload.md) 先取得 `viewUrl`，包括外部公开 URL；`imageUrl` 与 `imageList` 不可混用。

## 查询与交付

创建成功读取 `taskId`；可能同时返回 `costToken=0`，不表示免费。不消费下游文档中的 `data.id`、数字状态或 `count`，WorkBuddy 使用统一网关契约：

```json
{"toolName":"aigc/taskQuery","arguments":{"taskId":"<returned-taskId>"}}
```

查询支持可选 `memberId`，仅在已有真实任务上下文明确要求时沿用，不用它指定创建归属。不传 `format` 或虚构查询选项。

| 返回字段 | 说明 |
|---|---|
| `taskId` | 原任务ID |
| `status` | `PROCESSING` / `SUCCESS` / `FAILED` |
| `resultList` | 成功时媒体列表 |
| `resultList[].id` | 资源ID |
| `resultList[].url` | 生成媒体URL |
| `resultList[].type` | 素材类别，按实际值分类 |
| `errorMsg` | 任务级错误 |
| `costToken` | 若返回则保留实际计费字段及原单位，缺失为未知 |

当前契约不保证单项 `status/errorCode/errorMsg`、宽高、格式、文件大小或完整 `extendField`。不要用下游文档中的扩展字段补造结果，也不能仅凭任务成功断言所有计划图片均已返回。

创建后可查一次；处理中的任务保留编号，建议至少等待10秒后由用户明确继续查询。失败、空结果或连接中断不自动重建任务。下载失败只补下载。错误分层按 [onboarding.md](onboarding.md)。

## 套图条件

商品与服装套图至少一种图片类型数量为1～12，其余默认为0。手机版 A+ 基于高级 A+，开启 `aPlusHasPhone` 必须有 `aPlusProNum>0`，并计入交付数量与费用影响。图片数量使用各类 `*Num`，不是 `outputNum`。

`sellerPoint` 最长2500字符，未开启 `isExtractPrePoint` 时必须提供。开启自动提取也不能将模型推断当作已确认规格或功效。`brandKey` 可选，直接使用用户提供的品牌设置，无需执行品牌提取前置任务。

| `brandKey` 字段 | 类型 | 说明 |
|---|---|---|
| `brandColor` | string | `#RRGGBB` |
| `fontStyle` | string | 字体风格 |
| `salesRegion` | string | 销售地区 |
| `language` | string | 图片文字语言 |
| `platform` | string | 目标平台 |
| `customSettings` | string | 用户自定义要求，包括已确认的尺码信息等 |

`aPlusStyles` / `pointStyles` 每项为 `{"id":"<existing-layout-id>"}` 或 `{"prompt":"<layout-description>"}`。提供列表时，长度分别不少于 `aPlusNum+aPlusProNum` 和 `sellerTypeNum`；省略列表使用默认排版。不能把图片 URL 填入 `id` 或编造素材库 ID。用户已有排版描述时直接填 `prompt`，不调用未覆盖的排版提取接口。

`sensitiveLibraryId` / `replaceLibraryId` 只用已知真实库ID。词库处理不等于平台合规保证。修图模板中的 `provider`、`needOptimize` 配置可覆盖入参，用户明确要求模型时应避免模板与之冲突。

## 模型名称与质量

以下是套图及修图的请求枚举，不是通用生图的 `LF_*` 别名。仅传当前能力模型表列出的模型，不跨能力扩大支持范围。

| 请求枚举 | 用户可读名称 |
|---|---|
| `BANANA` | LF全能模型 |
| `BANANA_2` | LF全能模型 2 |
| `BANANA_2_LITE` | LF全能模型 2 Lite |
| `BANANA_PRO` | LF全能模型 Pro |
| `GPT_2_IMAGE` | LF智能模型 G-2 |
| `GPT_2_5_IMAGE` | LF智能模型 G-2.5 Sunburst |
| `GPT_2_5_F_IMAGE` | LF智能模型 G-2.5 Flare |
| `AIDRAW_EDIT` | Linkfox-Image-1 |
| `WAN2_7` | Wan 2.7 |
| `SEEDREAM5_PRO` | Seedream 5.0 Pro |
| `QWEN_IMAGE_3_PRO` | Qwen Image 3 Pro |
| `KONTEXT` | Kontext |

套图省略模型时当前默认 `GPT_2_5_IMAGE`，两种修图必须传 `provider`。用户选择优先，模型表为随包参数参考，不代表实时配置或价格。服务端拒绝时报告错误，不自行降级或试探模型。

`quality` 仅用于 GPT 系列：G-2 支持 `low/medium/high`；G-2.5 两款支持 `low/medium/high/xhigh/max`，默认 `medium`。其他模型省略。`supplyType` 仅在对应模型当前提供时传，不推断所有模型支持经济或稳定通道。精确比例、分辨率及参考图上限见各能力 reference。
