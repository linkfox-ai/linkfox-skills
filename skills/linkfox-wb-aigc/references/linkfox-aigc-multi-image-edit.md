# linkfox-aigc-multi-image-edit

## 功能与边界

把多张参考图片融合成一个连贯视觉，可用于搭配融图和搭配上身。`params.imageList`、`params.provider` 必填，`prompt` 最多 3000 字符；图片顺序影响结果，必须原样保留。

## Endpoint 与请求

| operation | 原 endpoint | 精确 toolName | arguments |
|---|---|---|---|
| 创建 | `/aigc/multiImageFusion` | `aigc/multiImageFusion` | `{"params":{"imageList","provider",...}}` |
| 查询 | `/aigc/taskQuery` | `aigc/taskQuery` | `{taskId}` |
| 素材上传 | `/aigc/uploadByBase64` | `aigc/uploadByBase64` | `{fileName, base64}` |

可选字段包括 `prompt`、`outputNum`、`template`（搭配融图或搭配上身）、`needOptimize`、`aspectRatio`、`resolution`、`supplyType` 和 `quality`。不同模型的图片上限不同，例如 BANANA 通常 1 至 3 张，GPT_2_5_IMAGE 通常 1 至 10 张，必须以当前模型表为准。

先上传每个本地素材并用对应 `viewUrl` 组成 `imageList`。创建返回 taskId，查询使用共享 `aigc/taskQuery`。失败、超时或上传失败都不自动重复收费动作。

## 特殊规则

- 模板中的 provider 和 needOptimize 可以覆盖入参可选值；质量档位只对支持的模型传入。
- 只有需要多源融合时选择此入口；一张图的普通生成或编辑要换用对应入口。
- 源融合、上传、下载和 onboarding 脚本不进入成品。
