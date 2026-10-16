# LinkFox 多图融合修图

子能力标识 `linkfox-aigc-multi-image-edit`。创建 endpoint 为 `/aigc/multiImageFusion`，精确 `toolName` 为 `aigc/multiImageFusion`；查询 endpoint 为 `/aigc/taskQuery`，精确 `toolName` 为 `aigc/taskQuery`。素材辅助 endpoint `/aigc/uploadByBase64`，精确 `toolName` 为 `aigc/uploadByBase64`。

调用前读取 [material-common.md](material-common.md) 的原生请求外层、响应、模型显示名称及状态机；素材按 [aigc-upload.md](aigc-upload.md) 上传。通过 `LinkFox.proxy_call` 调用，业务字段放在 `arguments.params`，外层字段为 `requestId`、`chatId`、`messageId`、`title`、`params`。不增加其他包装、不传凭证。

## params 完整参数

下表中可选字段的条件见说明与共同契约。不要把可选字段全部填上；按用户需求传值。模型表是随包参数参考，不代表实时能力或价格。

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| params.imageList | List<String> | 是 | 图片列表，请求张数见下方模型对照表；格式： jpg、jpeg、png、webp；大小： 单张不超过 10 MB；尺寸： 800×800～4096×4096|
| params.prompt | String | 可选或条件必填 | 强化内容描述，用于补充说明图片融合目标和要求；最多 3000 个字符|
| params.provider | String | 是 | 模型，可选值详见比例与分辨率|
| params.outputNum | Integer | 可选或条件必填 | 输出张数；默认 1 |
| params.template | String | 可选或条件必填 | 提示词模板名称（多图模板），模板中的 provider、needOptimize 配置优先于入参可选值 搭配融图 / 搭配上身|
| params.needOptimize | Boolean | 可选或条件必填 | 是否需要提示词优化，true：需要，false：不需要 |
| params.aspectRatio | String | 可选或条件必填 | 输出比例，模型支持范围详见比例与分辨率|
| params.resolution | String | 可选或条件必填 | 输出分辨率，详见比例与分辨率|
| params.supplyType | String | 可选或条件必填 | 供应模式；是否支持该字段及可选值，以当前模型实际提供为准|
| params.quality | String | 可选或条件必填 | 输出品质；仅适用于 GPT_2_IMAGE / GPT_2_5_IMAGE / GPT_2_5_F_IMAGE；GPT_2_IMAGE：low / medium / high；GPT_2_5_IMAGE / GPT_2_5_F_IMAGE：low / medium / high / xhigh / max；默认 medium|

## 比例、分辨率及参考图数量

| provider | 支持比例 | 支持分辨率 | 默认分辨率 | 请求图片 |
| --- | --- | --- | --- | --- |
| BANANA | 1:1 / 16:9 / 9:16 / 3:4 / 4:3 / 3:2 / 2:3 / 4:5 / 5:4 / 21:9 | 1K | 1K | 1～3 张 |
| BANANA_2_LITE | 1:1 / 3:2 / 2:3 / 3:4 / 4:3 / 4:5 / 5:4 / 9:16 / 16:9 / 21:9 | 1K | 1K | 1～10 张 |
| BANANA_2 | 1:1 / 3:2 / 2:3 / 3:4 / 4:3 / 4:5 / 5:4 / 16:9 / 9:16 / 21:9 | 1K / 2K / 4K | 2K | 1～10 张 |
| BANANA_PRO | 1:1 / 16:9 / 9:16 / 3:4 / 4:3 / 3:2 / 2:3 / 4:5 / 5:4 / 21:9 | 1K / 2K / 4K | 2K | 1～10 张 |
| WAN2_7 | 1:1 / 1:4 / 4:1 / 3:2 / 2:3 / 3:4 / 4:3 / 4:5 / 5:4 / 16:9 / 9:16 / 21:9 | 1K / 2K | 2K | 1～9 张 |
| QWEN_IMAGE_3_PRO | 1:1 / 1:4 / 4:1 / 1:8 / 8:1 / 3:2 / 2:3 / 3:4 / 4:3 / 4:5 / 5:4 / 16:9 / 9:16 / 21:9 / 9:21 | 1K / 2K | 2K | 1～3 张 |
| SEEDREAM5_PRO | 1:1 / 3:4 / 4:3 / 9:16 / 16:9 / 3:2 / 2:3 / 21:9 | 1K / 2K | 2K | 1～10 张 |
| GPT_2_IMAGE | 1:1 / 3:4 / 4:3 / 2:3 / 3:2 / 4:5 / 5:4 / 9:16 / 16:9 / 9:21 / 21:9 | 1K / 2K / 4K | 2K | 1～6 张 |
| GPT_2_5_IMAGE | 1:1 / 3:4 / 4:3 / 2:3 / 3:2 / 9:16 / 16:9 / 4:5 / 5:4 / 21:9 / 9:21 | 1K / 2K / 4K | 2K | 1～10 张 |
| GPT_2_5_F_IMAGE | 1:1 / 3:4 / 4:3 / 2:3 / 3:2 / 9:16 / 16:9 / 4:5 / 5:4 / 21:9 / 9:21 | 1K / 2K / 4K | 2K | 1～10 张 |
| AIDRAW_EDIT | 1:1 / 2:3 / 3:2 / 3:4 / 4:3 / 9:16 / 16:9 / 21:9 | 1K / 2K | 2K | 1～4 张 |

## 使用要点

用于多参考素材融合，先明确各图商品、背景、人物或搭配元素角色并保留顺序。接口模型表允许部分模型只传1张图；只有单张原图且要求直接修改时优先单图编辑。图片单张≤10MB，尺寸800×800～4096×4096。

`prompt` 可选，最多3000字符；没有足够信息确定目标时先补充描述。`provider` 必填，`outputNum` 默认1，不能套用通用生图的最多10张规则；服务端具体输出限制以模型实际响应为准。模板可选“搭配融图”或“搭配上身”，模板中的模型和优化配置可能覆盖入参。

认证、权限、积分及业务错误按 [onboarding.md](onboarding.md) 分层处理；失败不自动重建或换模型。成功返回的URL可直接交付，下载失败只补下载。
