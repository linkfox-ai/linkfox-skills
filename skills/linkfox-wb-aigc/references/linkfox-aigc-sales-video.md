# linkfox-aigc-sales-video

## 功能与边界

根据商品图、场景图或品牌图和口播脚本生成带货视频。`params.videoType`、`params.prompt`、`params.imageList` 必填，`imageList` 至少一张；适合电商上新、促销和详情页补充素材。

## Endpoint 与请求

| operation | 原 endpoint | 精确 toolName | arguments |
|---|---|---|---|
| 创建 | `/aigc/salesVideo` | `aigc/salesVideo` | `{"params":{...}}` |
| 查询 | `/aigc/taskQuery` | `aigc/taskQuery` | `{taskId}` |
| 素材上传 | `/aigc/uploadByBase64` | `aigc/uploadByBase64` | `{fileName, base64}` |

可选 `videoTime`、`resolution`、`aspectRatio` 和 `isPro`。模型包括 minimax-h3-lite、minimax-h3、wan3、doubao-seedance-2-5、doubao-seedance-2-0、doubao-seedance-2-0-fast、doubao-seedance-2-0-mini 和 happyhorse-v2；面向用户用友好名称解释，请求值只放 arguments。

参考图上限因模型而异，约 9 至 30 张；时长约 5 至 30 秒，分辨率约 480P 至 2K，以当前返回的模型能力为准。成功创建后用 `aigc/taskQuery` 查询并展示结果。

## 特殊规则

- prompt 建议包含商品名称、卖点、目标人群、语气和行动指令；不能把 `productInfo` 等图转视频模板字段混入此接口。
- 使用素材前先通过上传 endpoint 取得 `viewUrl`；下载失败只重试下载，不重建任务。
- 源带货脚本、上传、下载和 onboarding 脚本不进入成品。
