# linkfox-aigc-image-to-video

## 功能与边界

把单张或多张图片转成视频，也可使用参考视频、模板、运镜和尾帧。`params.videoType`、`params.videoTime` 必填；`imageUrl` 与 `imageList` 二选一，HappyHorse 和部分 MiniMax 入口必须用 `imageList`；不使用 `templateKey` 时 `prompt` 必填。

## Endpoint 与请求

| operation | 原 endpoint | 精确 toolName | arguments |
|---|---|---|---|
| 创建 | `/aigc/imageToVideo` | `aigc/imageToVideo` | `{"params":{...}}` |
| 查询 | `/aigc/taskQuery` | `aigc/taskQuery` | `{taskId}` |
| 素材上传 | `/aigc/uploadByBase64` | `aigc/uploadByBase64` | `{fileName, base64}` |

`params` 支持 `video`、`promptOptimizer`、`isPro`、`voice`、`lastFrameImageUrl`、`camera`、`templateKey`、`productInfo`、`language`、`saleCountry`、`imageUrl`、`imageList`、`prompt`、`resolution` 和 `aspectRatio`。模板 key 包括 `product-showcase`、`ugc-seeding`、`pain-solution` 和 `furniture-scene`，传模板时服务端生成 prompt，不能再依赖手写 prompt。

模型能力决定时长、分辨率、比例、声音、尾帧和参考图上限。成功创建返回 taskId，使用 `aigc/taskQuery` 查询 `PROCESSING`、`SUCCESS` 或 `FAILED`。

## 特殊规则

- 所有实际使用的本地或外部媒体先经 `aigc/uploadByBase64`，再把返回 `viewUrl` 放入业务字段；查询阶段不重复上传。
- `videoTime`、`resolution`、`aspectRatio` 和 `voice` 组合必须符合当前模型配置；`isPro` 已逐步由 resolution 替代。
- 源图转视频、上传、下载和 onboarding 脚本不进入成品。
