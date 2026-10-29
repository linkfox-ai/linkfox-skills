# linkfox-aigc-textgen

## 功能与边界

根据提示词生成文本，也可结合图片或视频 URL 做多模态理解。支持快速模型 GEM_3_FLASH 和复杂分析模型 GEM_3_1_PRO；`thinkingLevel` 为 `minimal`、`low`、`medium` 或 `high`，GEM_3_1_PRO 不支持 `minimal`。

不用于直接生成图片或视频。需要媒体时，媒体统一放在 `imageUrls`，不要使用未定义的 `videoUrl` 或 `videoUrls`；纯文本必须传空数组 `[]`。

## Endpoint 与请求

| operation | 原 endpoint | 精确 toolName | arguments |
|---|---|---|---|
| 创建 | `/aigc/textGenAsync` | `aigc/textGenAsync` | `{prompt, imageUrls, model?, thinkingLevel}` |
| 查询 | `/aigc/textTaskQuery` | `aigc/textTaskQuery` | `{taskId}` |

创建必填 `prompt`、`imageUrls` 和 `thinkingLevel`。`prompt` 最长 100000 字符，图片最多 10 张，视频通常 1 个。创建返回 `taskId`；查询返回 `status`、成功时的 `content` 以及 `promptTokens`、`completionTokens`、`totalTokens`，失败时返回 `errorMsg`。

## 特殊规则

- `GEM_3_FLASH` 适合常规文案、翻译和简单分析；`GEM_3_1_PRO` 适合长文和复杂推理。
- 轮询间隔 5 至 10 秒，总等待建议不超过 600 秒。可将成功 `content` 作为后续图像或视频 prompt，但必须先确认下游参数和积分。
- 401、402、10009 和其他业务码按主文档分层处理，不自动换模型或重建任务。
- 源 `aigc_textgen.py` 和 onboarding 脚本不进入成品；不存在本地 helper。
