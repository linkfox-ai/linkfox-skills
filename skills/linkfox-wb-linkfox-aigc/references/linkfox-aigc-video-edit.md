# LinkFox 视频编辑

子能力标识 `linkfox-aigc-video-edit`。创建 endpoint `/aigc/videoEditing`，精确 `toolName` 为 `aigc/videoEditing`；查询 endpoint `/aigc/taskQuery`，精确 `toolName` 为 `aigc/taskQuery`。

先读 [video-common.md](video-common.md) 的素材准备、模型命名、查询与交付规则。全部业务调用通过 `LinkFox.proxy_call`，WorkBuddy 自动注入 Authorization，不传凭证，不运行旧网关或自动轮询脚本。下面模型表为随包参数参考，不宣称实时模型配置或价格；不要跨入口套用支持范围。

## 原生请求外层与 params

原生请求外层为 `requestId`、`chatId`、`messageId`、`title`、`params`，所有业务字段放 `arguments.params`，不传顶层 `memberId`。完整外层与响应契约见 [material-common.md](material-common.md)。素材辅助 endpoint `/aigc/uploadByBase64`，精确 `toolName` 为 `aigc/uploadByBase64`；本地与外部URL都先按 [aigc-upload.md](aigc-upload.md) 换成 `viewUrl`。

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| params.sourceVideoUrl | String | 是 | 待编辑原视频的公网 URL；跟随原视频模型会由服务端读取真实媒体时长用于执行与计费|
| params.prompt | String | 是 | 视频编辑指令，最多 2500 字符|
| params.videoType | String | 是 | 选择下方模型参数中的公开模型名称|
| params.videoTime | Integer | 可选或条件必填 | 输出时长（秒），见下方时长规则；固定时长模型未传时使用当前模型默认值 |
| params.refImageList | List<String> | 可选或条件必填 | 参考图片 URL 列表，数量上限见下方模型参数|

### 模型参数

`videoType` 请使用下表中的公开模型名称；模型是否可用以接口实际返回为准。

| videoType | 模型名称 | videoTime 允许值 | refImageList 上限 |
| --- | --- | --- | --- |
| `kling-v3-omni` | 可灵 V3-Omni | `-1` | 4 张 |
| `gemini-omni-flash` | Gemini Omni Flash 1.1 | `-1` | 10 张 |
| `doubao-seedance-2-0` | 豆包 Seedance 2.0 | 5 / 10 / 15 | 6 张 |
| `happyhorse-v2` | HappyHorse | `-1` | 9 张 |
| `WAN3` | 万相 3.0 | 5 / 10 / 15 | 10 张 |
| `doubao-seedance-2-5` | 豆包 Seedance 2.5 | `-1` | 30 张 |

---

### 时长规则

#### 跟随原视频时长

`videoTime=-1` 表示输出时长跟随原视频。以下模型只支持该模式：

- `kling-v3-omni`
- `gemini-omni-flash`
- `happyhorse-v2`
- `doubao-seedance-2-5`

> `happy-horse-v2` 是兼容别名，新接入请使用 `happyhorse-v2`。

- 系统会读取原视频的真实时长；视频无法访问或无法识别时长时，任务不会创建。
- 上述模型不要传 5、10、15 等固定时长，否则会返回参数错误。

#### 固定时长可选

- `doubao-seedance-2-0` 和 `WAN3` 支持 5 / 10 / 15 秒。
- 不传 `videoTime` 时使用当前模型默认时长；这两类模型不支持 `-1`。

#### 原视频时长限制

- 固定输出时长不等于原视频时长上限；可处理的原视频长度以模型实际能力为准。
- 建议使用稳定可访问的 HTTPS 视频地址，并控制原视频长度，避免任务在生成阶段失败。

---


## 使用要点

修改已有视频；`sourceVideoUrl/prompt/videoType` 必填，`refImageList` 可选，不要求用户额外提供图片。提示词最多2500字符。

对跟随原视频模型显式传 `videoTime=-1` 或省略，对固定时长模型按表传5/10/15秒；不要自动截短或将固定时长默认值移植到跟随模式。模型无权访问源视频、无法识别时长或素材超限时停止，不换模型重建。

当前契约不定义 `resolution/aspectRatio` 编辑参数，不能从图转视频接口补造这些字段。新请求使用 `happyhorse-v2` 而非兼容别名，`WAN3` 保持大写。

## MCP 创建示例

示例仅说明结构；执行前替换真实素材与唯一请求ID。专用视频示例的素材必须是上传返回的 `viewUrl`，不能用占位URL做收费测试。

```json
{"toolName":"aigc/videoEditing","arguments":{"requestId":"<unique-video-edit-request>","params":{"sourceVideoUrl":"https://example.com/uploaded-source-viewUrl.mp4","prompt":"将背景替换为摄影棚，保留商品外观和主体动作","videoType":"kling-v3-omni","videoTime":-1}}}
```

成功创建保存 `taskId`，再按 [video-common.md](video-common.md) 查询 `aigc/taskQuery`。只有 `SUCCESS` 时交付实际视频URL；失败或超时不自动重建，下载失败只补下载。认证、积分与权限错误按 [onboarding.md](onboarding.md)。
