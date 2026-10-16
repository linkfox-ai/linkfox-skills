# LinkFox 商品视频复刻

子能力标识 `linkfox-aigc-video-reclone`。创建 endpoint `/aigc/videoReclone`，精确 `toolName` 为 `aigc/videoReclone`；查询 endpoint `/aigc/taskQuery`，精确 `toolName` 为 `aigc/taskQuery`。

先读 [video-common.md](video-common.md) 的素材准备、模型命名、查询与交付规则。全部业务调用通过 `LinkFox.proxy_call`，WorkBuddy 自动注入 Authorization，不传凭证，不运行旧网关或自动轮询脚本。下面模型表为随包参数参考，不宣称实时模型配置或价格；不要跨入口套用支持范围。

## 原生请求外层与 params

原生请求外层为 `requestId`、`chatId`、`messageId`、`title`、`params`，所有业务字段放 `arguments.params`，不传顶层 `memberId`。完整外层与响应契约见 [material-common.md](material-common.md)。素材辅助 endpoint `/aigc/uploadByBase64`，精确 `toolName` 为 `aigc/uploadByBase64`；本地与外部URL都先按 [aigc-upload.md](aigc-upload.md) 换成 `viewUrl`。

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| params.videoType | String | 是 | 模型类型：minimax-h3-lite、minimax-h3、wan3、doubao-seedance-2-5、doubao-seedance-2-0、doubao-seedance-2-0-fast、doubao-seedance-2-0-mini、happyhorse-v2|
| params.refVideoUrl | String | 是 | 参考视频的公网 URL（需长期有效，避免使用短期签名 URL）。|
| params.refImageList | List<String> | 是 | 参考商品图 URL 列表，至少 1 张；数量上限按模型区分，见下方各模型参数支持情况。|
| params.resolution | String | 是 | 视频分辨率，可选值见下方各模型参数支持情况|
| params.saleCountry | String | 是 | 销售国家（如 CN、US）|
| params.targetLanguage | String | 是 | 目标语言（如 zh、en）|
| params.videoTime | Integer | 可选或条件必填 | 目标视频时长（秒），支持值按模型区分，见下方各模型参数支持情况；不传时使用模型默认值。 |
| params.aspectRatio | String | 可选或条件必填 | 视频比例，可选值见下方各模型参数支持情况|
| params.productInfo | String | 可选或条件必填 | 补充商品文字信息，用于辅助 AI 分析，最多 2500 字符。|
| params.prompt | String | 可选或条件必填 | 最终提示词。传入后将跳过 AI 分析直接按该提示词生成视频；不传则由系统自动分析参考视频与商品图后生成。|

### 各模型参数支持情况

| 模型 | 分辨率 | 时长（秒） | 参考图上限 |
| --- | --- | --- | --- |
| minimax-h3-lite | 768P | 5/10/15 | 9 |
| minimax-h3 | 768P / 2K | 5/10/15 | 9 |
| wan3 | 480P / 720P / 1080P | 5/10/15/20/25/30 | 10 |
| doubao-seedance-2-5 | 480P / 720P / 1080P | 5/10/15/20/25/30 | 30 |
| doubao-seedance-2-0 | 480P / 720P / 1080P | 5/10/15 | 6 |
| doubao-seedance-2-0-fast | 480P / 720P | 5/10/15 | 6 |
| doubao-seedance-2-0-mini | 480P / 720P | 5/10/15 | 6 |
| happyhorse-v2 | 720P / 1080P | 5/10/15 | 9 |

---

### 参数使用建议

- `refVideoUrl` 必须为稳定可访问的公网 URL，Gemini 在异步分析阶段才访问，短期签名 URL 可能已过期。
- `refImageList` 中的图片在提交任务时**同步**下载，若图片无法访问，任务创建立即报错，请确保图片地址长期有效。
- `productInfo` 为可选的文字补充，提供商品名称、卖点等信息可提升复刻效果（仅在未传 `prompt`、走自动分析时生效）。
- `prompt` 为可选的最终提示词：传了则跳过 AI 分析直接生成视频，适合已有分镜/脚本、或对自动分析结果二次编辑后再提交的场景；不传则走完整分析流程。
- `doubao-seedance-2-0-fast` / `doubao-seedance-2-0-mini` 传入 `resolution=1080P` 会报错，建议传 `480P` 或 `720P`。
- `aspectRatio` 不传时各模型使用厂商默认比例。

---


## 使用要点

根据参考视频的结构、节奏或表达生成当前商品视频，必须同时提供 `refVideoUrl` 与至少1张商品图 `refImageList`；两者都先上传。`resolution`、`saleCountry`、`targetLanguage` 必填，缺失时补充，不能从账号身份推断市场。

未传 `prompt` 时服务端自动分析参考视频与商品图；已有最终脚本时传 `prompt` 会跳过分析，`productInfo` 仅自动分析时生效。不自动加一次独立文本分析。注意Seedance 2.0/Fast/Mini参考图最多6张，而其他入口可能允许9张；不能混用数量限制。

## MCP 创建示例

示例仅说明结构；执行前替换真实素材与唯一请求ID。专用视频示例的素材必须是上传返回的 `viewUrl`，不能用占位URL做收费测试。

```json
{"toolName":"aigc/videoReclone","arguments":{"requestId":"<unique-video-reclone-request>","params":{"refVideoUrl":"https://example.com/uploaded-reference-viewUrl.mp4","refImageList":["https://example.com/uploaded-product-viewUrl.jpg"],"videoType":"doubao-seedance-2-0","resolution":"720p","saleCountry":"US","targetLanguage":"en","videoTime":10,"productInfo":"用户已确认的商品名称与卖点"}}}
```

成功创建保存 `taskId`，再按 [video-common.md](video-common.md) 查询 `aigc/taskQuery`。只有 `SUCCESS` 时交付实际视频URL；失败或超时不自动重建，下载失败只补下载。认证、积分与权限错误按 [onboarding.md](onboarding.md)。
