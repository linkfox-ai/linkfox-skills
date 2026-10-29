# linkfox-aigc-video-translate

## 功能与边界

把已有视频中的语音翻译为目标语言，可选口型同步。`params.sourceVideoUrl`、`targetLanguage` 必填；`sourceVideoName`、`lipSync` 和 `videoType` 可选。源语言由服务端识别，不提供源语言字段。

## Endpoint 与请求

| operation | 原 endpoint | 精确 toolName | arguments |
|---|---|---|---|
| 创建 | `/aigc/videoTranslation` | `aigc/videoTranslation` | `{"params":{"sourceVideoUrl","targetLanguage",...}}` |
| 查询 | `/aigc/taskQuery` | `aigc/taskQuery` | `{taskId}` |
| 素材上传 | `/aigc/uploadByBase64` | `aigc/uploadByBase64` | `{fileName, base64}` |

支持目标语言短代码或 BCP-47 代码，例如中文 `zh`、英语 `en`、日语 `ja`、韩语 `ko`、西班牙语 `es`、法语 `fr` 和德语 `de`。创建返回 taskId，查询返回 `status`、`resultList`、`errorMsg` 和实际费用字段。

外部或本地源视频先通过上传 endpoint 取得 `viewUrl`，再放入 `sourceVideoUrl`；上传失败不创建，查询时不重复上传。创建时费用为零不等于免费，最终费用以终态查询为准。

## 特殊规则

- `lipSync` 默认 true；用户明确不需要口型同步时传 false。不要用翻译接口承担画面编辑或视频复刻。
- 目标语言必须来自支持表；不支持的语言应在创建前说明限制。
- 源翻译、上传、下载和 onboarding 脚本不进入成品。
