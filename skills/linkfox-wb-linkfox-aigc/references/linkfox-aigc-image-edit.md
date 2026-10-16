# LinkFox 智能修图

子能力标识 `linkfox-aigc-image-edit`。创建 endpoint 为 `/aigc/imageEdit`，精确 `toolName` 为 `aigc/imageEdit`；查询 endpoint 为 `/aigc/taskQuery`，精确 `toolName` 为 `aigc/taskQuery`。素材辅助 endpoint `/aigc/uploadByBase64`，精确 `toolName` 为 `aigc/uploadByBase64`。

调用前读取 [material-common.md](material-common.md) 的原生请求外层、响应、模型显示名称及状态机；素材按 [aigc-upload.md](aigc-upload.md) 上传。通过 `LinkFox.proxy_call` 调用，业务字段放在 `arguments.params`，外层字段为 `requestId`、`chatId`、`messageId`、`title`、`params`。不增加其他包装、不传凭证。

## params 完整参数

下表中可选字段的条件见说明与共同契约。不要把可选字段全部填上；按用户需求传值。模型表是随包参数参考，不代表实时能力或价格。

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| params.imageUrl | String | 是 | 原图；格式： jpg、jpeg、png、webp；尺寸： 300×300～4096×4096；宽高比： 0.4～2.5|
| params.prompt | String | 是 | 提示词，不能为空；最多 3000 个字符|
| params.provider | String | 是 | 模型，可选值详见比例与分辨率|
| params.outputNum | Integer | 可选或条件必填 | 输出张数，取值范围 1～4；默认 1 |
| params.template | String | 可选或条件必填 | 提示词模板名称，模板中的 provider、needOptimize 配置优先于入参可选值 白底图 / 商品主图精修 / 生成场景 / 海报制作 / 加人或物 / 换动物 / 服装平铺 / 3D服装 / 人台换模特 / 卡通插画 / 改身材 / 更换风格 / 移除元素 / 文字消除 / 去除水印 / 添加水印|
| params.needOptimize | Boolean | 可选或条件必填 | 是否需要提示词优化，true：需要，false：不需要 |
| params.aspectRatio | String | 可选或条件必填 | 输出比例，模型支持范围详见比例与分辨率|
| params.resolution | String | 可选或条件必填 | 输出分辨率，详见比例与分辨率|
| params.supplyType | String | 可选或条件必填 | 供应模式；是否支持该字段及可选值，以当前模型实际提供为准|
| params.quality | String | 可选或条件必填 | 输出品质；仅适用于 GPT_2_IMAGE / GPT_2_5_IMAGE / GPT_2_5_F_IMAGE；GPT_2_IMAGE：low / medium / high；GPT_2_5_IMAGE / GPT_2_5_F_IMAGE：low / medium / high / xhigh / max；默认 medium|

## 比例、分辨率及参考图数量

| provider | 支持比例 | 支持分辨率 | 默认分辨率 |
| --- | --- | --- | --- |
| BANANA | 1:1 / 16:9 / 9:16 / 3:4 / 4:3 / 3:2 / 2:3 / 4:5 / 5:4 / 21:9 | 1K | 1K |
| BANANA_2_LITE | 1:1 / 3:2 / 2:3 / 3:4 / 4:3 / 4:5 / 5:4 / 9:16 / 16:9 / 21:9 | 1K | 1K |
| BANANA_2 | 1:1 / 3:2 / 2:3 / 3:4 / 4:3 / 4:5 / 5:4 / 16:9 / 9:16 / 21:9 | 1K / 2K / 4K | 2K |
| BANANA_PRO | 1:1 / 16:9 / 9:16 / 3:4 / 4:3 / 3:2 / 2:3 / 4:5 / 5:4 / 21:9 | 1K / 2K / 4K | 2K |
| WAN2_7 | 1:1 / 1:4 / 4:1 / 3:2 / 2:3 / 3:4 / 4:3 / 4:5 / 5:4 / 16:9 / 9:16 / 21:9 | 1K / 2K | 2K |
| QWEN_IMAGE_3_PRO | 1:1 / 1:4 / 4:1 / 1:8 / 8:1 / 3:2 / 2:3 / 3:4 / 4:3 / 4:5 / 5:4 / 16:9 / 9:16 / 21:9 / 9:21 | 1K / 2K | 2K |
| KONTEXT | 按原图比例 | 1K | 1K |
| SEEDREAM5_PRO | 1:1 / 3:4 / 4:3 / 9:16 / 16:9 / 3:2 / 2:3 / 21:9 | 1K / 2K | 2K |
| GPT_2_IMAGE | 1:1 / 3:4 / 4:3 / 2:3 / 3:2 / 9:16 / 16:9 / 4:5 / 5:4 / 21:9 / 9:21 | 1K / 2K / 4K | 2K |
| GPT_2_5_IMAGE | 1:1 / 3:4 / 4:3 / 2:3 / 3:2 / 9:16 / 16:9 / 4:5 / 5:4 / 21:9 / 9:21 | 1K / 2K / 4K | 2K |
| GPT_2_5_F_IMAGE | 1:1 / 3:4 / 4:3 / 2:3 / 3:2 / 9:16 / 16:9 / 4:5 / 5:4 / 21:9 / 9:21 | 1K / 2K / 4K | 2K |
| AIDRAW_EDIT | 1:1 / 2:3 / 3:2 / 3:4 / 4:3 / 9:16 / 16:9 / 21:9 | 1K / 2K | 2K |

## 使用要点

用于一张原图的背景替换、精修、去除元素或风格调整。使用单数 `imageUrl`，原图jpg/jpeg/png/webp，尺寸300×300～4096×4096，宽高比0.4～2.5；素材上传另有10MB及最长边4096限制。

`prompt` 非空且最多3000字符，`provider` 必填，`outputNum` 为1～4，默认1。用户只要局部修改时在提示词明确保留主体形状、颜色、标识及非修改区域。`KONTEXT` 按原图比例输出，不替它指定虚构比例。

模板可选“白底图”“商品主图精修”“生成场景”“海报制作”“加人或物”“换动物”“服装平铺”“3D服装”“人台换模特”“卡通插画”“改身材”“更换风格”“移除元素”“文字消除”“去除水印”“添加水印”。模板的 `provider` 和 `needOptimize` 配置优先于入参，避免与用户明确选择冲突。

认证、权限、积分及业务错误按 [onboarding.md](onboarding.md) 分层处理；失败不自动重建或换模型。成功返回的URL可直接交付，下载失败只补下载。
