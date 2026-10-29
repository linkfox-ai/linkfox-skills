# linkfox-aigc-video-reclone

## 功能与边界

根据参考商品视频和商品图片生成相似的营销视频，可按销售国家、目标语言、商品信息和目标时长调整。`params.videoType`、`refVideoUrl`、`refImageList`、`resolution`、`saleCountry`、`targetLanguage` 必填；`videoTime`、`aspectRatio`、`productInfo` 和 `prompt` 可选。

## Endpoint 与请求

| operation | 原 endpoint | 精确 toolName | arguments |
|---|---|---|---|
| 创建 | `/aigc/videoReclone` | `aigc/videoReclone` | `{"params":{...}}` |
| 查询 | `/aigc/taskQuery` | `aigc/taskQuery` | `{taskId}` |
| 素材上传 | `/aigc/uploadByBase64` | `aigc/uploadByBase64` | `{fileName, base64}` |

`refVideoUrl` 应为长期可访问的参考视频 URL，`refImageList` 至少一张。未传 `prompt` 时由服务端分析参考视频和商品图；传入后跳过分析并按该 prompt 生成。支持模型包括 minimax、wan3、doubao-seedance 和 happyhorse 系列，分辨率、时长和图片上限按模型表核对。

先将本地或外部素材通过上传 endpoint 转为 `viewUrl`，再一次性创建任务。创建返回 taskId，使用 `aigc/taskQuery` 查询结果和实际费用。

## 特殊规则

- `saleCountry` 和 `targetLanguage` 影响本地化表达，不能省略；`productInfo` 最多 2500 字符。
- 参考视频和商品图必须能被服务端读取，不要传短期失效签名或本地路径。
- 源复刻、上传、下载和 onboarding 脚本不进入成品。
