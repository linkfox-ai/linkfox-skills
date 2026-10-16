---
name: linkfox-aigc-videogen
description: AI生视频工具（单图/首尾帧模式），根据原图和提示词生成视频，支持配置中已开放的多种视频模型。用户说"生成视频"、"AI视频"、"图生视频"、"做个视频"、"video generation"、"generate video"、"图片转视频"、"动态视频"时触发。
---

# AI 生视频（首尾帧/单图模式）

根据原图（首帧）和可选尾帧图生成视频，支持多种 AI 视频模型，异步创建任务后轮询获取结果。

## 动态模型列表（仅替换目录来源）

- 模型配置域名由 `LINKFOX_AI_API_URL` 覆盖（默认 `https://ai-api.linkfox.com`），与生成网关 `LINKFOX_TOOL_GATEWAY` 独立；测试/生产配置见 [references/model-config.md](references/model-config.md)。
- 选择模型前调用 `python scripts/aigc_videogen.py --list-models --inline`；图片查 bizType=201，两个视频入口查 bizType=88。
- 普通场景按动态完整列表选择，不由旧模型目录封顶。明确的专用业务范围只在查询时用 `--allowed-models` 取交集；生成仍按原脚本 JSON 调用，不传这个新查询参数。
- 只有查询失败才用下方原静态表兜底；成功但缺失/维护中不补回，不自动换模型。
- 正常生成不额外查询或存档配置，不新增提交前参数校验，不更改请求参数、默认策略、轮询、下载及交付。
- HappyHorse 系列保留原多图入口路由：即使只有一张参考图，也通过 `linkfox-aigc-videogen-multi` 的 `imageList` 提交；未挂载多图 Skill 时提示安装，不改造成单图/首尾帧请求。
- 模型能力用于介绍和选择选项，不作为一套新的生成请求白名单；编码适配、异常和落盘说明见 [references/model-config.md](references/model-config.md)。

## 核心特点

- **动态模型选择**：按动态配置读取可用状态和能力，查询失败使用原静态表。
- **首尾帧控制**：尾帧是否可用以当前动态目录的 `supportLastFrame` 和模式能力为准。
- **丰富参数**：支持 Pro 模式、声音生成、宽高比和分辨率等。
- **异步模式**：创建任务立即返回 taskId，脚本自动轮询直到完成（超时 20 分钟）。

## 模型说明（仅配置查询失败时兜底）

| 说明名称 | 时长 | 默认分辨率/备注 |
|------|------|------------|
| 可灵Omni | 5秒/10秒/15秒 | 720p，旧调用默认5秒 |
| Seedance 2.0 | 4～15秒 | 480p，可选720p/1080p |
| Seedance 2.0 fast | 4～15秒 | 480p，可选720p |
| Seedance 2.5 | 4～30秒 | 480p，可选720p/1080p |
| 海螺2.3 | 6秒/10秒 | 768p |
| Seedance 2.0 mini | 4～15秒，默认10秒 | 480p，可选720p |
| 万相3.0 | 5/10/15/20/25/30秒，默认10秒 | 480p，可选720p/1080p，支持尾帧 |
| MiniMax H3 | 5秒/10秒/15秒，默认5秒 | 2K，可选768p，支持尾帧 |
| 可灵2.6 | 5秒/10秒，默认10秒 | 720p，可选1080p；声音能力仅在1080p使用 |

## 展示规则

- 面向用户介绍、推荐、确认模型或解释错误时，只能使用动态配置返回的 **name**（查询失败时使用上表的**说明名称**）。
- 禁止向用户展示 videoType、provider、模型 code 或内部渠道名称。
- MiniMax H3 的多个内部渠道只对用户展示为 **MiniMax H3**。

## 参数概览

- **必填字段**：`imageUrl`、`videoType`、`videoTime`
- **可选核心**：`lastFrameImageUrl`（仅万相3.0、MiniMax H3）、`prompt`（3000字符以内）

完整参数表、响应字段结构与错误码，见 [`references/api.md`](references/api.md)。

## 首尾帧上传（file-upload）

- `imageUrl`（首帧）及实际提供的 `lastFrameImageUrl`（尾帧）接收可访问的图片 URL，不接收本地文件路径。尾帧仍为可选，是否支持按所选模型能力处理。
- 已有可公开访问的 HTTP(S) URL 直接复用；本地图片或附件先按本 skill 内置的 [references/file-upload.md](references/file-upload.md) 上传，再将成功项的 `url` 填入对应字段，保留首尾帧对应关系。同一图片用于多个字段时复用 URL，无需查找或安装额外上传 skill。
- 上传失败时停止本次生成并说明原因。生成脚本不自动上传，须在创建任务前完成素材准备；轮询原任务时不重复上传。

## 调用方式

- **创建任务**：`POST /aigc/videoGenAsync` → 返回 `{taskId}`
- **轮询结果**：`POST /aigc/taskQuery` → 传入 `{taskId}` → 返回状态和结果
- **Python 脚本**：`python scripts/aigc_videogen.py '<JSON 参数>'`（脚本内部自动完成创建+轮询）

**异步流程**：
1. 脚本调用 `/aigc/videoGenAsync` 创建任务，获得 `taskId`
2. 等待 2 分钟后开始轮询 `/aigc/taskQuery`，每 10 秒一次，最长等待 20 分钟
3. 成功后自动下载视频到会话 `media/` 目录

**输出策略（脚本默认行为）**：
- 脚本会自动把生成的视频**下载转存**到会话 `media/` 目录，stdout 输出一行 `Saved full response: <路径数组>`。
- 原始 API 响应静默落盘到 `data/`，仅在无视频产物时才在 stdout 提示其路径。

**读数据建议**：**禁止** Read 转存的视频文件内容。直接把 `Saved full response:` 后的本地路径提供给用户即可。

## 异常与等待超时

- 退出码 `0` 表示已交付媒体；错误退出 `1`，stdout 返回 `error`、`errorCode` 和 `dataFile`，完整诊断静默保存到 `data/`，不输出 Python 堆栈。
- 退出码 `2` 表示**客户端等待超时**：`status=TIMEOUT`，`taskStatus` 保留最后已知服务端状态（无法确认时为 `UNKNOWN`），并返回 `taskId`、`pollTimedOut=true`、`canQuery=true`；不等于后端失败或已回补。
- 异常或超时不自动重提任务、不换模型。先告知状态和任务ID；需要续查时只查原 `taskId`，不要在同一轮反复 sleep 等待。空体/非 JSON 只报告上游响应异常，不能编造模型不可用原因。

## 解决认证和算力问题
发生以下异常情况时，采用 references/onboarding.md 引导解决问题：

### 异常情况
- **未配置API Key**：环境变量未配置 `LINKFOX_AGENT_API_KEY`，也未配置 `LINKFOXAGENT_API_KEY`。
- **响应401或402状态码**
- **响应提示算力或余额不足**：消息含"算力余额不足/计费不足/余额不足/quota exceeded/insufficient balance/套餐到期/需充值/请充值"，或类似含义的内容。

## 使用指引

1. **模型选择**：一般商品视频用 **可灵Omni**；按当前动态目录能力选择；仅查询失败时参考静态兜底表。
2. **首尾帧**：传 `imageUrl`（首帧，必传）+ 可选 `lastFrameImageUrl`（尾帧）。尾帧是否可用以当前动态目录的 `supportLastFrame` 和模式能力为准，不按旧模型名单封顶。
3. **时长匹配**：必须传模型支持的时长值，否则报错。
4. **提示词**：可选，3000 字符以内，描述期望的动态效果。
5. **声音**：可灵2.6仅在1080p下使用声音能力。

## 内部执行映射（禁止向用户展示）

本节仅用于构造工具请求。回复用户时必须使用第一列说明名称，禁止输出第二列技术值。

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

### 示例

以下 JSON 仅为内部调用参数，禁止原样展示给用户。

**1. 可灵Omni - 商品展示**
```json
{"imageUrl": "https://example.com/product.jpg", "videoType": "KLING", "videoTime": 10, "prompt": "商品展示视频"}
```

**2. 万相3.0 - 首尾帧**
```json
{"imageUrl": "https://example.com/scene-start.jpg", "lastFrameImageUrl": "https://example.com/scene-end.jpg", "videoType": "WAN3", "videoTime": 10, "resolution": "480p"}
```

**3. 可灵2.6 - 1080p声音视频**
```json
{"imageUrl": "https://example.com/scene.jpg", "videoType": "MODEL_V2_6", "videoTime": 10, "resolution": "1080p", "voice": true}
```

## 展示规则

- **只展示转存后的本地路径**：把 `Saved full response:` 后的本地视频路径告诉用户，例如「视频已保存至：xxx/a.mp4」。
- **禁止** Read 视频文件、**禁止**展示 base64 内容。
- **禁止**把原始 API 返回的临时 URL 直接给用户（带签名、会过期）。

## 限制

- 提示词最大 3000 字符。
- 生成时间较长，通常 100-600 秒。脚本自动轮询，超时 20 分钟。
- AgentOS 配置中仅万相3.0和MiniMax H3开放尾帧能力。
- 本接口仅支持单图/首尾帧模式。多参考图请使用 `linkfox-aigc-videogen-multi`。
- 失败时不重试（仅尝试 1 次）。

## 不适用
**不适用**：
- 多参考图生视频 → `linkfox-aigc-videogen-multi`
- 图片生成 → `linkfox-aigc-imagegen`
- 文本生成 → `linkfox-aigc-textgen`

## 反馈

参见 `references/api.md`。
