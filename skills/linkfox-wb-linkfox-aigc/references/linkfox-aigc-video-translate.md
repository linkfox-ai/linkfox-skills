# LinkFox 视频翻译

子能力标识 `linkfox-aigc-video-translate`。创建 endpoint `/aigc/videoTranslation`，精确 `toolName` 为 `aigc/videoTranslation`；查询 endpoint `/aigc/taskQuery`，精确 `toolName` 为 `aigc/taskQuery`。

先读 [video-common.md](video-common.md) 的素材准备、模型命名、查询与交付规则。全部业务调用通过 `LinkFox.proxy_call`，WorkBuddy 自动注入 Authorization，不传凭证，不运行旧网关或自动轮询脚本。下面模型表为随包参数参考，不宣称实时模型配置或价格；不要跨入口套用支持范围。

## 原生请求外层与 params

原生请求外层为 `requestId`、`chatId`、`messageId`、`title`、`params`，所有业务字段放 `arguments.params`，不传顶层 `memberId`。完整外层与响应契约见 [material-common.md](material-common.md)。素材辅助 endpoint `/aigc/uploadByBase64`，精确 `toolName` 为 `aigc/uploadByBase64`；本地与外部URL都先按 [aigc-upload.md](aigc-upload.md) 换成 `viewUrl`。

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| params.sourceVideoUrl | String | 是 | 待翻译原视频的公网 URL；服务端会读取真实媒体时长用于计费|
| params.targetLanguage | String | 是 | 目标语言，支持短代码或 BCP-47 代码，详见下方语言表|
| params.sourceVideoName | String | 可选或条件必填 | 原视频文件名，仅用于历史记录展示|
| params.lipSync | Boolean | 可选或条件必填 | 是否同步口型；默认 true |
| params.videoType | String | 可选 | 视频翻译模型；不传时使用默认模型，支持值见本页“模型与使用要点” |

### 支持的语言

`targetLanguage` 必须使用下表中的语言。源语言由服务端自动识别，不提供源语言请求参数。

| 语言 | 短代码 | BCP-47 代码 |
| --- | --- | --- |
| 中文 | `zh` | `zh-CN` |
| 英语 | `en` | `en-US` |
| 日语 | `ja` | `ja-JP` |
| 韩语 | `ko` | `ko-KR` |
| 西班牙语 | `es` | `es-ES` |
| 法语 | `fr` | `fr-FR` |
| 德语 | `de` | `de-DE` |
| 葡萄牙语 | `pt` | `pt-BR` |
| 阿拉伯语 | `ar` | `ar-SA` |
| 泰语 | `th` | `th-TH` |
| 越南语 | `vi` | `vi-VN` |
| 印尼语 | `id` | `id-ID` |
| 马来语 | `ms` | `ms-MY` |

目标语言代码匹配不区分大小写，并兼容下划线形式（例如 `en_US`）。

---

### 模型与生成规则

自动识别原视频语言，按 `targetLanguage` 翻译；`lipSync` 控制是否同步口型。不传 `videoType` 时使用默认模型；可灵模型也跟随原视频时长。

---

### 时长规则

所有模型均跟随原视频时长，不支持自定义时长，无需传 `videoTime` 或 `duration`。请使用可持续访问的视频 URL；计费时长按原视频实际时长向下取整为整数秒，实际费用以响应为准。

---


## 模型与使用要点

随包模型值为 `happyhorse-v2` 和 `doubao-seedance-2-5`，省略 `videoType` 时当前默认后者；模型可用性及费用以实际响应为准，不复制静态单价当作实时报价。

只需要 `sourceVideoUrl` 与 `targetLanguage`，`lipSync` 默认true；关闭口型同步明确传false。不要求图片，不提供 `sourceLanguage`，也不传 `videoTime/duration` 自定义时长。`sourceVideoName` 仅用于历史记录展示，不改变源文件。

源语言由服务端自动识别，目标语言使用本页支持表。实际计费基于服务端读取的源视频时长，不用文件大小或口播字数估计已支付费用。翻译结果需核对商品名、单位和数字，不声称模型翻译已获人工审核。

## MCP 创建示例

示例仅说明结构；执行前替换真实素材与唯一请求ID。专用视频示例的素材必须是上传返回的 `viewUrl`，不能用占位URL做收费测试。

```json
{"toolName":"aigc/videoTranslation","arguments":{"requestId":"<unique-video-translate-request>","params":{"sourceVideoUrl":"https://example.com/uploaded-source-viewUrl.mp4","targetLanguage":"en","lipSync":true}}}
```

成功创建保存 `taskId`，再按 [video-common.md](video-common.md) 查询 `aigc/taskQuery`。只有 `SUCCESS` 时交付实际视频URL；失败或超时不自动重建，下载失败只补下载。认证、积分与权限错误按 [onboarding.md](onboarding.md)。
