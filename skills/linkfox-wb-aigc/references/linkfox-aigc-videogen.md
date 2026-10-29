# linkfox-aigc-videogen

## 功能与边界

用首帧图和可选尾帧图生成视频。`imageUrl`、`videoType`、`videoTime` 必填，`prompt` 最长 3000 字符；`lastFrameImageUrl` 仅在当前模型配置支持时使用。多参考图不走此入口，HappyHorse 的多图入口保持使用 `linkfox-aigc-videogen-multi`。

## Endpoint 与请求

| operation | 原 endpoint | 精确 toolName | arguments |
|---|---|---|---|
| 创建 | `/aigc/videoGenAsync` | `aigc/videoGenAsync` | `{imageUrl, videoType, videoTime, prompt?, promptOptimizer?, isPro?, voice?, lastFrameImageUrl?, aspectRatio?, resolution?}` |
| 查询 | `/aigc/taskQuery` | `aigc/taskQuery` | `{taskId}` |

说明名称包括可灵Omni、Seedance 2.0、Seedance 2.0 fast、Seedance 2.5、海螺2.3、Seedance 2.0 mini、万相3.0、MiniMax H3 和可灵2.6；请求内部使用对应 `videoType`。动态目录优先，静态表仅在查询失败时兜底。

创建返回 `taskId`。查询返回 `status`、`resultList[].id/url/type` 和失败 `errorMsg`。初始等待约 120 秒，之后每 10 秒查询，最长 20 分钟。

## 特殊规则

- 尾帧只有万相3.0和 MiniMax H3 等当前配置明确支持的模型可用；声音和分辨率也按模型能力检查。
- 超时不等于后端失败，不自动重提；只用原 taskId 续查。`10007` 通常表示时长、分辨率、比例、声音或尾帧不匹配，`10009` 表示任务不存在。
- 源生视频脚本、动态模型脚本和 onboarding 脚本不进入成品。
