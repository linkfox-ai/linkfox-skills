# LinkFox 服装营销套图

子能力标识 `linkfox-aigc-clothing-suite`。创建 endpoint 为 `/aigc/wearCollection`，精确 `toolName` 为 `aigc/wearCollection`；查询 endpoint 为 `/aigc/taskQuery`，精确 `toolName` 为 `aigc/taskQuery`。素材辅助 endpoint `/aigc/uploadByBase64`，精确 `toolName` 为 `aigc/uploadByBase64`。

调用前读取 [material-common.md](material-common.md) 的原生请求外层、响应、模型显示名称及状态机；素材按 [aigc-upload.md](aigc-upload.md) 上传。通过 `LinkFox.proxy_call` 调用，业务字段放在 `arguments.params`，外层字段为 `requestId`、`chatId`、`messageId`、`title`、`params`。不增加其他包装、不传凭证。

## params 完整参数

下表中可选字段的条件见说明与共同契约。不要把可选字段全部填上；按用户需求传值。模型表是随包参数参考，不代表实时能力或价格。

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| params.imageList | List<String> | 是 | 商品图片列表，请求张数见下方模型对照表；格式： jpg/jpeg/png/webp；大小： 单张≤10M；尺寸： 384×384～4096×4096|
| params.sellerPoint | String | 可选或条件必填 | 商品卖点描述，≤2500字符（未开启自动提取时必填）|
| params.isExtractPrePoint | Boolean | 可选或条件必填 | 自动提取卖点；默认 false |
| params.provider | String | 可选或条件必填 | 未传时使用当前业务类型的默认启用模型；模型选择，可选值及默认分辨率见比例与分辨率；模型特殊参数；当前默认 GPT_2_5_IMAGE|
| params.aspectRatio | String | 可选或条件必填 | 素材宽高比（卖点图/模特图/种草图等），按模型配置校验，支持比例详见比例与分辨率|
| params.resolution | String | 可选或条件必填 | 输出分辨率，详情见比例与分辨率|
| params.brandKey | BrandKey | 可选或条件必填 | 品牌基因 JSON 对象 |
| params.modelTypeNum | Integer | 可选或条件必填 | 模特图数量，最大12；默认 0 |
| params.sellerTypeNum | Integer | 可选或条件必填 | 卖点图数量，最大12；默认 0 |
| params.insTypeNum | Integer | 可选或条件必填 | 种草图数量，最大12；默认 0 |
| params.sizeTypeNum | Integer | 可选或条件必填 | 尺码图数量，最大12；默认 0 |
| params.whiteTypeNum | Integer | 可选或条件必填 | 白底图数量，最大12；默认 0 |
| params.aPlusNum | Integer | 可选或条件必填 | 普通A+数量，最大12；默认 0 |
| params.aPlusProNum | Integer | 可选或条件必填 | 高级A+数量（Pro版），最大12；默认 0 |
| params.aPlusHasPhone | Boolean | 可选或条件必填 | 是否生成手机版A+（基于高级A+结果，数量与高级A+一致）；默认 false |
| params.aPlusAspectRatio | String | 可选或条件必填 | A+页面宽高比，不填则自动选择；支持格式：16:9、9:16、1:1、1:3.7|
| params.modelImageUrl | String | 可选或条件必填 | 模特参考图，未设置时启动智能模式|
| params.sceneImageUrl | String | 可选或条件必填 | 场景参考图，未设置时启动智能模式|
| params.isExactScene | Boolean | 可选或条件必填 | 场景裂变模式：true 遵循背景 false 相似裂变；默认 true |
| params.modelAndSceneInfo | String | 可选或条件必填 | 可选：描述想要生成的场景内容和模特特征|
| params.noText | Boolean | 可选或条件必填 | 无字模式，开启后排版不含文字，仅输出纯图片素材；默认 false |
| params.aPlusStyles | List<LayoutStyle> | 可选或条件必填 | A+图排版列表，为每张A+图指定排版方式；数量需不少于A+图数量（aPlusNum + aPlusProNum），每项可填 id 或 prompt|
| params.pointStyles | List<LayoutStyle> | 可选或条件必填 | 卖点图排版列表，为每张卖点图指定排版方式；数量需不少于卖点图数量（sellerTypeNum），每项可填 id 或 prompt|
| params.sensitiveLibraryId | Long | 可选或条件必填 | 敏感词库ID，命中的敏感词会经AI改写规避；不传则不启用该能力 |
| params.replaceLibraryId | Long | 可选或条件必填 | 替换词库ID，命中的词按预设替换词直接替换；不传则不启用该能力 |
| params.quality | String | 可选或条件必填 | 输出品质；仅适用于 GPT_2_IMAGE / GPT_2_5_IMAGE / GPT_2_5_F_IMAGE；GPT_2_IMAGE：low / medium / high；GPT_2_5_IMAGE / GPT_2_5_F_IMAGE：low / medium / high / xhigh / max；默认 medium|

## 比例、分辨率及参考图数量

| provider | 支持比例 | 支持分辨率 | 默认分辨率 | 请求图片 |
| --- | --- | --- | --- | --- |
| BANANA_2 | 1:1 / 3:2 / 2:3 / 3:4 / 4:3 / 4:5 / 5:4 / 16:9 / 9:16 / 21:9 | 1K / 2K / 4K | 2K | 1～5 张 |
| BANANA_2_LITE | 1:1 / 3:2 / 2:3 / 3:4 / 4:3 / 4:5 / 5:4 / 9:16 / 16:9 / 21:9 | 1K | 1K | 1～5 张 |
| BANANA_PRO | 1:1 / 16:9 / 9:16 / 3:4 / 4:3 / 3:2 / 2:3 / 4:5 / 5:4 / 21:9 | 1K / 2K / 4K | 2K | 1～5 张 |
| WAN2_7 | 1:1 / 3:2 / 2:3 / 3:4 / 4:3 / 4:5 / 5:4 / 16:9 / 9:16 / 21:9 | 1K / 2K | 2K | 1～5 张 |
| SEEDREAM5_PRO | 1:1 / 3:4 / 4:3 / 9:16 / 16:9 / 3:2 / 2:3 / 21:9 | 1K / 2K | 2K | 1～5 张 |
| GPT_2_IMAGE | 1:1 / 3:4 / 4:3 / 2:3 / 3:2 / 9:16 / 16:9 / 4:5 / 5:4 / 21:9 / 9:21 | 1K / 2K / 4K | 2K | 1～5 张 |
| GPT_2_5_IMAGE | 1:1 / 3:4 / 4:3 / 2:3 / 3:2 / 9:16 / 16:9 / 4:5 / 5:4 / 21:9 / 9:21 | 1K / 2K / 4K | 2K | 1～5 张 |
| GPT_2_5_F_IMAGE | 1:1 / 3:4 / 4:3 / 2:3 / 3:2 / 9:16 / 16:9 / 4:5 / 5:4 / 21:9 / 9:21 | 1K / 2K / 4K | 2K | 1～5 张 |

## 使用要点

用于服装模特、种草、尺码及营销素材；至少一类数量大于0，每类上限12。`whiteTypeNum` 是服装白底数量，不是商品套图的 `whiteBgTypeNum`。商品图片单张≤10MB，尺寸384×384～4096×4096，格式jpg/jpeg/png/webp。

`modelImageUrl`、`sceneImageUrl` 可选，不提供时采用智能模式；提供时也必须先上传。`isExactScene=true` 遵循场景，false做相似裂变；`modelAndSceneInfo` 填模特与场景要求。尺码图仅使用用户已确认数据，可放入 `sellerPoint` 或 `brandKey.customSettings`，不臆造未定义的 `sizeData` 字段。没有尺码资料时先补充，不自动生成虚构尺码。

按共同契约处理品牌、排版、A+和词库。结果 `type` 可见 `A+`、`APlusPro`、`APlusHasPhone`、`scene`、`point`、`ins`、`size`、`white`，依次为普通A+、高级A+、手机版A+、模特或场景、卖点、种草、尺码及白底。按实际返回分类。

认证、权限、积分及业务错误按 [onboarding.md](onboarding.md) 分层处理；失败不自动重建或换模型。成功返回的URL可直接交付，下载失败只补下载。
