# LinkFox 带货口播视频

子能力标识 `linkfox-aigc-sales-video`。创建 endpoint `/aigc/salesVideo`，精确 `toolName` 为 `aigc/salesVideo`；查询 endpoint `/aigc/taskQuery`，精确 `toolName` 为 `aigc/taskQuery`。

先读 [video-common.md](video-common.md) 的素材准备、模型命名、查询与交付规则。全部业务调用通过 `LinkFox.proxy_call`，WorkBuddy 自动注入 Authorization，不传凭证，不运行旧网关或自动轮询脚本。下面模型表为随包参数参考，不宣称实时模型配置或价格；不要跨入口套用支持范围。

## 原生请求外层与 params

原生请求外层为 `requestId`、`chatId`、`messageId`、`title`、`params`，所有业务字段放 `arguments.params`，不传顶层 `memberId`。完整外层与响应契约见 [material-common.md](material-common.md)。素材辅助 endpoint `/aigc/uploadByBase64`，精确 `toolName` 为 `aigc/uploadByBase64`；本地与外部URL都先按 [aigc-upload.md](aigc-upload.md) 换成 `viewUrl`。

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| params.videoType | String | 是 | 模型类型：minimax-h3-lite、minimax-h3、wan3、doubao-seedance-2-5、doubao-seedance-2-0、doubao-seedance-2-0-fast、doubao-seedance-2-0-mini、happyhorse-v2|
| params.prompt | String | 是 | 口播脚本/视频提示词。建议包含：产品卖点、使用场景、人群、语气风格|
| params.imageList | List<String> | 是 | 参考图列表（商品图、场景图、品牌图等），至少 1 张可访问外网的图片 URL；数量上限按模型区分，见下方各模型参数支持情况|
| params.videoTime | Integer | 可选或条件必填 | 视频时长（秒），不同类型支持的时长不同，见下方各模型参数支持情况 |
| params.resolution | String | 可选或条件必填 | 视频分辨率。详见各模型参数支持情况|
| params.aspectRatio | String | 可选或条件必填 | 视频比例：16:9 / 9:16 / 1:1 / 4:3 / 3:4 / 21:9；不传则使用模型默认值|
| params.isPro | Boolean | 可选或条件必填 | 是否开启高质量模式；适用于 doubao-seedance-2-0 / doubao-seedance-2-0-fast / doubao-seedance-2-0-mini / doubao-seedance-2-5，未传 resolution 时，true 使用 720p；默认 false |

### 各模型参数支持情况

| 模型 | 分辨率 | 时长（秒） | 参考图上限 |
| --- | --- | --- | --- |
| minimax-h3-lite | 768P | 5/10/15 | 9 |
| minimax-h3 | 768P / 2K | 5/10/15 | 9 |
| wan3 | 480P / 720P / 1080P | 5/10/15/20/25/30 | 10 |
| doubao-seedance-2-5 | 480P / 720P / 1080P | 5/10/15/20/25/30 | 30 |
| doubao-seedance-2-0 | 480P / 720P / 1080P | 5/10/15 | 9 |
| doubao-seedance-2-0-fast | 480P / 720P | 5/10/15 | 9 |
| doubao-seedance-2-0-mini | 480P / 720P | 5/10/15 | 9 |
| happyhorse-v2 | 720P / 1080P | 5/10/15 | 9 |

---

### 参数使用建议

- `prompt` 建议明确：商品名称 + 核心卖点 + 目标人群 + 结尾行动指令（如"立即下单"）。
- `imageList` 必填，传入商品主图/细节图通常能提升一致性和转化表达。
- 根据用户选定渠道确定模型和时长，不自动组合测试或额外生成。
- 使用 doubao-seedance-2-0 / doubao-seedance-2-0-fast / doubao-seedance-2-0-mini / doubao-seedance-2-5 且未传 `resolution` 时，可通过 `isPro=true` 使用 720p。
- `happyhorse-v2` 分辨率默认 720p，如需更高清可传 `resolution: "1080p"`。

---


## 使用要点

用于商品卖点、场景、人群与语气明确的口播或UGC营销视频。`prompt` 和至少1张 `imageList` 必填；保留真实商品事实，不新增未确认功效或真人背书。人物、口播语言和脚本要求写进 `prompt`，不编造 `speakerId`、`voiceId`、`targetLanguage` 等未定义字段。

仅使用本页模型表。接口未定义通用 `voice` 开关，不从旧入口移植该字段；有音轨、人物表演和口型的具体效果以生成结果为准，不承诺所有模型都提供真人式口播。根据用户要求选择时长、比例及分辨率，不自动做模型对比测试。

## MCP 创建示例

示例仅说明结构；执行前替换真实素材与唯一请求ID。专用视频示例的素材必须是上传返回的 `viewUrl`，不能用占位URL做收费测试。

```json
{"toolName":"aigc/salesVideo","arguments":{"requestId":"<unique-sales-video-request>","params":{"imageList":["https://example.com/uploaded-product-viewUrl.jpg"],"videoType":"doubao-seedance-2-0","videoTime":10,"prompt":"用自然英文口播介绍用户已确认的商品卖点，结尾邀请了解详情","resolution":"720p","aspectRatio":"9:16"}}}
```

成功创建保存 `taskId`，再按 [video-common.md](video-common.md) 查询 `aigc/taskQuery`。只有 `SUCCESS` 时交付实际视频URL；失败或超时不自动重建，下载失败只补下载。认证、积分与权限错误按 [onboarding.md](onboarding.md)。
