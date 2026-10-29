# linkfox-aigc-videogen-multi

## 功能与边界

用多张参考图生成视频，适合多个商品角度、人物和场景共同约束的画面。`imageList`、`videoType`、`videoTime` 必填，`prompt` 最长 3000 字符；图片顺序必须保持。单图或首尾帧优先走单图入口，除非模型配置明确要求多图入口。

## Endpoint 与请求

| operation | 原 endpoint | 精确 toolName | arguments |
|---|---|---|---|
| 创建 | `/aigc/multiImageVideoGenAsync` | `aigc/multiImageVideoGenAsync` | `{imageList, videoType, videoTime, prompt?, promptOptimizer?, isPro?, voice?, aspectRatio?, resolution?}` |
| 查询 | `/aigc/taskQuery` | `aigc/taskQuery` | `{taskId}` |

模型说明名称与单图视频入口共享可灵、Seedance、万相和 MiniMax 等目录，但多图上限不同。兜底规则为可灵Omni最多 7 张、Seedance 2.5 最多 30 张，其余已开放模型通常最多 9 张；以动态配置为准。

创建返回 `taskId`，查询返回 `PROCESSING`、`SUCCESS` 或 `FAILED`，成功结果在 `resultList`。初始等待约 120 秒，之后每 10 秒查询，最长 20 分钟。

## 特殊规则

- 仅在模型支持时传 `isPro`、`voice`、`aspectRatio` 或 `resolution`；不要将单图入口参数改名后混用。
- 失败和超时只查询原任务，不重建、不更换模型、不重复上传。
- 源多图视频脚本、动态模型脚本和 onboarding 脚本不进入成品。
