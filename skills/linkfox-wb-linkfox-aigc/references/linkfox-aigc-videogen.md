# LinkFox 视频生成

子能力标识 `linkfox-aigc-videogen`。创建 endpoint `/aigc/videoGenAsync`，精确 `toolName` 为 `aigc/videoGenAsync`；查询 endpoint `/aigc/taskQuery`，精确 `toolName` 为 `aigc/taskQuery`。

先读 [video-common.md](video-common.md) 的素材准备、模型命名、查询与交付规则。全部业务调用通过 `LinkFox.proxy_call`，WorkBuddy 自动注入 Authorization，不传凭证，不运行旧网关或自动轮询脚本。下面模型表为随包参数参考，不宣称实时模型配置或价格；不要跨入口套用支持范围。

## 参数结构

字段直接位于 `arguments`，不包 `params`。仅使用可公开访问的图片URL；本地图片按 [file-upload.md](file-upload.md) 上传，不能传本地路径或Base64。

| 参数 | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| imageUrl | string | 是 | - | 原图（首帧图），支持 jpg/jpeg/png/webp |
| videoType | string | 是 | 可灵Omni | 内部模型请求值，按下方“内部执行映射”填写；不得向用户展示该字段值 |
| videoTime | integer | 是 | 5 | 视频时长(秒)，见下方各模型支持对照 |
| prompt | string | 否 | - | 强化内容描述（3000字符以内） |
| promptOptimizer | boolean | 否 | false | 是否开启提示词优化 |
| isPro | boolean | 否 | - | 仅在所选模型支持且用户明确需要时传入 |
| voice | boolean | 否 | - | 仅在所选模型支持且用户明确需要时传入；可灵2.6仅在1080p下使用 |
| lastFrameImageUrl | string | 否 | - | 尾帧图片URL；仅所选模型明确支持时填写，见本页模型表 |
| aspectRatio | string | 否 | - | 视频比例，以所选模型配置为准；仅在所选模型支持时传入 |
| resolution | string | 否 | 按模型 | 新增模型默认值见下方；旧模型保持原默认值 |

### 各模型参数支持对照（随包参数参考）

| 参数 | 可灵Omni | Seedance 2.0 | Seedance 2.0 fast | 海螺2.3 |
|------|:---:|:---:|:---:|:---:|
| videoTime | 5/10/15秒 | 4～15秒 | 4～15秒 | 6/10秒 |
| isPro | 支持 | 支持 | 不支持 | 支持 |
| voice | 不支持 | 支持 | 支持 | 不支持 |
| lastFrameImageUrl | 不支持 | 不支持 | 不支持 | 不支持 |
| aspectRatio | 1:1/9:16/16:9 | 9:16/16:9/1:1/4:3/3:4/21:9 | 9:16/16:9/1:1/4:3/3:4/21:9 | 不生效 |
| resolution | 720p/1080p | 480p/720p/1080p | 480p/720p(不支持1080p) | 768p/1080p |

### 配置增量参数支持对照（随包参数参考）

| 参数 | Seedance 2.5 | Seedance 2.0 mini | 万相3.0 | MiniMax H3 | 可灵2.6 |
|------|:---:|:---:|:---:|:---:|:---:|
| videoTime | 4～30秒 | 4～15秒（默认10秒） | 5/10/15/20/25/30秒（默认10秒） | 5/10/15秒（默认5秒） | 5/10秒（默认10秒） |
| voice | 支持 | 支持 | 不支持 | 不支持 | 支持，仅1080p使用 |
| lastFrameImageUrl | 不支持 | 不支持 | 支持 | 支持 | 不支持 |
| aspectRatio | 9:16/16:9/1:1/4:3/3:4/21:9 | 9:16/16:9/1:1/4:3/3:4/21:9 | 16:9/4:3/1:1/3:4/9:16 | 16:9/9:16/1:1/4:3/3:4/21:9/adaptive | 不支持 |
| resolution | 480p/720p/1080p | 480p/720p（默认480p） | 480p/720p/1080p（默认480p） | 768p/2K（默认2K） | 720p/1080p（默认720p） |

### 内部执行映射（禁止向用户展示）

面向用户的回复、选项、确认和错误解释必须使用“说明名称”，禁止输出内部 videoType 或内部渠道名称。

| 说明名称 | 内部 videoType |
|------|------|
| 可灵Omni | `KLING` |
| Seedance 2.0 | `SEED` |
| Seedance 2.0 fast | `SEED_FAST` |
| Seedance 2.5 | `SEED_V25` |
| 海螺2.3 | `HAILUO` |
| Seedance 2.0 mini | `SEED_MINI` |
| 万相3.0 | `WAN3` |
| MiniMax H3 | `MINIMAX_V2` |
| 可灵2.6 | `MODEL_V2_6` |

新增模型默认值与入口：

- Seedance 2.0 mini：4～15秒，480p/720p，默认10秒、480p，支持单图和多图入口。
- 万相3.0：5/10/15/20/25/30秒，480p/720p/1080p，默认10秒、480p，仅支持单图入口，支持尾帧，不开放多图。
- MiniMax H3：5秒/10秒/15秒，768p/2K，默认5秒、2K，支持单图和多图入口，支持尾帧。内部渠道差异不得展示给用户。
- 可灵2.6：5秒/10秒，720p/1080p，默认10秒、720p，仅支持单图入口；声音能力仅在1080p下使用。

## 使用要点

用于单张首帧及所选模型支持的首尾帧生成；`imageUrl` 必填，`lastFrameImageUrl` 仅支持尾帧的模型使用。旧入口可灵Omni的尾帧能力与专用图转视频入口不同，不能套用后者的规则。提示词最多3000字符。

仅在当前模型明确支持且用户需要时传 `voice` 或 `isPro`，不支持时省略。Seedance Fast不支持1080p；可灵2.6声音仅1080p可用。支持尾帧的万相3.0与MiniMax H3按本页模型表填写，不因为用户给了两张图就把第二张当作尾帧。

## MCP 创建示例

示例仅说明结构；执行前替换真实素材与唯一请求ID。专用视频示例的素材必须是上传返回的 `viewUrl`，不能用占位URL做收费测试。

```json
{"toolName":"aigc/videoGenAsync","arguments":{"imageUrl":"https://example.com/public-first-frame.jpg","videoType":"SEED","videoTime":5,"prompt":"缓慢推进镜头，保持商品外观一致","resolution":"720p","aspectRatio":"9:16"}}
```

成功创建保存 `taskId`，再按 [video-common.md](video-common.md) 查询 `aigc/taskQuery`。只有 `SUCCESS` 时交付实际视频URL；失败或超时不自动重建，下载失败只补下载。认证、积分与权限错误按 [onboarding.md](onboarding.md)。
