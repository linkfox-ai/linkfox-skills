# LinkFox 多场景视频生成

子能力标识 `linkfox-aigc-videogen-multi`。创建 endpoint `/aigc/multiImageVideoGenAsync`，精确 `toolName` 为 `aigc/multiImageVideoGenAsync`；查询 endpoint `/aigc/taskQuery`，精确 `toolName` 为 `aigc/taskQuery`。

先读 [video-common.md](video-common.md) 的素材准备、模型命名、查询与交付规则。全部业务调用通过 `LinkFox.proxy_call`，WorkBuddy 自动注入 Authorization，不传凭证，不运行旧网关或自动轮询脚本。下面模型表为随包参数参考，不宣称实时模型配置或价格；不要跨入口套用支持范围。

## 参数结构

字段直接位于 `arguments`，不包 `params`。仅使用可公开访问的图片URL；本地图片按 [file-upload.md](file-upload.md) 上传，不能传本地路径或Base64。

| 参数 | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| imageList | array[string] | 是 | - | 多参考图列表。可灵Omni最多7张，Seedance 2.5最多30张，其他已开放模型最多9张 |
| videoType | string | 是 | 可灵Omni | 内部模型请求值，按下方“内部执行映射”填写；不得向用户展示该字段值 |
| videoTime | integer | 是 | - | 视频时长(秒)，见下方各模型支持对照 |
| prompt | string | 否 | - | 强化内容描述（3000字符以内） |
| promptOptimizer | boolean | 否 | false | 是否开启提示词优化 |
| isPro | boolean | 否 | - | 仅在所选模型支持且用户明确需要时传入 |
| voice | boolean | 否 | - | 仅在所选模型支持且用户明确需要时传入 |
| aspectRatio | string | 否 | 按模型 | 视频比例，以所选模型配置为准；仅在所选模型支持时传入 |
| resolution | string | 否 | 按模型 | 新增模型默认值见下方；旧模型保持原默认值 |

### 各模型参数支持对照（随包参数参考）

| 参数 | 可灵Omni | Seedance 2.0 | Seedance 2.0 fast | HappyHorse 1.1 |
|------|:---:|:---:|:---:|:---:|
| videoTime | 5/10/15秒 | 4～15秒 | 4～15秒 | 5/10/15秒(默认15) |
| imageList上限 | 7张 | 9张 | 9张 | 9张 |
| isPro | 支持 | 支持 | 不支持 | 不支持 |
| voice | 不支持 | 支持 | 支持 | 不支持 |
| aspectRatio | 1:1/9:16/16:9 | 9:16/16:9/1:1/4:3/3:4/21:9 | 9:16/16:9/1:1/4:3/3:4/21:9 | 9:16/16:9/1:1/4:3/3:4/21:9 |
| resolution | 720p/1080p | 480p/720p/1080p | 480p/720p(不支持1080p) | 720p/1080p |

### 配置增量参数支持对照（随包参数参考）

| 参数 | Seedance 2.5 | Seedance 2.0 mini | MiniMax H3 |
|------|:---:|:---:|:---:|
| videoTime | 4～30秒 | 4～15秒（默认10秒） | 5/10/15秒（默认5秒） |
| imageList上限 | 30张 | 9张 | 9张 |
| voice | 支持 | 支持 | 不支持 |
| aspectRatio | 9:16/16:9/1:1/4:3/3:4/21:9 | 9:16/16:9/1:1/4:3/3:4/21:9 | 16:9/9:16/1:1/4:3/3:4/21:9/adaptive |
| resolution | 480p/720p/1080p | 480p/720p（默认480p） | 768p/2K（默认2K） |

### 内部执行映射（禁止向用户展示）

面向用户的回复、选项、确认和错误解释必须使用“说明名称”，禁止输出内部 videoType 或内部渠道名称。

| 说明名称 | 内部 videoType |
|------|------|
| 可灵Omni | `KLING` |
| Seedance 2.0 | `SEED` |
| Seedance 2.0 fast | `SEED_FAST` |
| Seedance 2.5 | `SEED_V25` |
| HappyHorse 1.1 | `HAPPY_HORSE` |
| Seedance 2.0 mini | `SEED_MINI` |
| MiniMax H3 | `MINIMAX_V2` |

新增模型默认值：

- Seedance 2.0 mini：4～15秒，480p/720p，默认10秒、480p，最多9张参考图。
- MiniMax H3：5秒/10秒/15秒，768p/2K，默认5秒、2K，最多9张参考图。内部渠道差异不得展示给用户。
- 旧未开放模型说明不构成当前目录白名单；新目录和目标接口能力需一致，不新增请求格式。

## 使用要点

用于多参考图与多场景素材生成，`imageList` 保留用户顺序并在提示词说明商品、人物、背景等角色。多参考图不等于保证输出多个镜头，镜头安排需写入提示词。至少1张；可灵Omni最多7张、Seedance 2.5最多30张、其他本页已开放模型最多9张。不要沿用旧版统一9张上限。

此入口不接收 `imageUrl`、`lastFrameImageUrl` 或参考视频 `video`。万相3.0与可灵2.6没有在本入口开放，不能把单图入口模型添加进来。仅在模型明确支持且用户需要时传 `voice/isPro`，提示词最多3000字符。

## MCP 创建示例

示例仅说明结构；执行前替换真实素材与唯一请求ID。专用视频示例的素材必须是上传返回的 `viewUrl`，不能用占位URL做收费测试。

```json
{"toolName":"aigc/multiImageVideoGenAsync","arguments":{"imageList":["https://example.com/public-product.jpg","https://example.com/public-scene.jpg"],"videoType":"SEED","videoTime":5,"prompt":"结合商品与场景参考，生成连贯展示镜头","resolution":"720p","aspectRatio":"9:16"}}
```

成功创建保存 `taskId`，再按 [video-common.md](video-common.md) 查询 `aigc/taskQuery`。只有 `SUCCESS` 时交付实际视频URL；失败或超时不自动重建，下载失败只补下载。认证、积分与权限错误按 [onboarding.md](onboarding.md)。
