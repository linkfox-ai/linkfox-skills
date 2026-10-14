---
name: linkfox-aigc-videogen-multi
description: 多参考图生视频工具，根据多张参考图和提示词生成视频。支持配置中已开放的多种多图视频模型，可控制时长、声音、宽高比和分辨率。用户说"多图生视频"、"多图视频"、"多张图片生成视频"、"多参考图生视频"、"multi image video"、"multiple images to video"时触发。
---

# 多参考图生视频

根据多张参考图和提示词生成视频，支持 7 种 AI 视频模型，异步创建任务后轮询获取结果。

## 核心特点

- **7 种模型选择**：覆盖不同风格和时长需求。
- **多图参考**：传入多张图片作为参考，AI 综合生成视频。
- **丰富参数**：支持 Pro 模式、声音生成、宽高比、分辨率等。
- **异步模式**：创建任务立即返回 taskId，脚本自动轮询直到完成（超时 20 分钟）。

## 模型说明

| 说明名称 | 时长 | 默认分辨率 | 图片上限 |
|------|------|----------|----------|
| 可灵Omni | 5秒/10秒/15秒 | 720p | ≤7张 |
| Seedance 2.0 | 4～15秒 | 480p，可选720p/1080p | ≤9张 |
| Seedance 2.0 fast | 4～15秒 | 480p，可选720p | ≤9张 |
| Seedance 2.5 | 4～30秒 | 480p，可选720p/1080p | ≤30张 |
| HappyHorse 1.1 | 5秒/10秒/15秒（默认15秒） | 720p | ≤9张 |
| Seedance 2.0 mini | 4～15秒，默认10秒 | 480p，可选720p | ≤9张 |
| MiniMax H3 | 5秒/10秒/15秒，默认5秒 | 2K，可选768p | ≤9张 |

## 展示规则

- 面向用户介绍、推荐、确认模型或解释错误时，只能使用上表的**说明名称**。
- 禁止向用户展示 videoType、provider、模型 code 或内部渠道名称。
- 万相3.0不开放多图，不得在多图模型选项中展示或调用。
- MiniMax H3 的多个内部渠道只对用户展示为 **MiniMax H3**。

## 参数概览

- **必填字段**：`imageList`、`videoType`、`videoTime`
- **可选核心**：`prompt`（3000字符以内）、`aspectRatio`、`resolution`

完整参数表、响应字段结构与错误码，见 [`references/api.md`](references/api.md)。

## 调用方式

- **创建任务**：`POST /aigc/multiImageVideoGenAsync` → 返回 `{taskId}`
- **轮询结果**：`POST /aigc/taskQuery` → 传入 `{taskId}` → 返回状态和结果
- **Python 脚本**：`python scripts/aigc_videogen_multi.py '<JSON 参数>'`（脚本内部自动完成创建+轮询）

**异步流程**：
1. 脚本调用 `/aigc/multiImageVideoGenAsync` 创建任务，获得 `taskId`
2. 等待 2 分钟后开始轮询 `/aigc/taskQuery`，每 10 秒一次，最长等待 20 分钟
3. 成功后自动下载视频到会话 `media/` 目录

**输出策略（脚本默认行为）**：
- 脚本会自动把生成的视频**下载转存**到会话 `media/` 目录，stdout 输出一行 `Saved full response: <路径数组>`。
- 原始 API 响应静默落盘到 `data/`，仅在无视频产物时才在 stdout 提示其路径。

**读数据建议**：**禁止** Read 转存的视频文件内容。直接把 `Saved full response:` 后的本地路径提供给用户即可。

## 解决认证和算力问题
发生以下异常情况时，采用 references/onboarding.md 引导解决问题：

### 异常情况
- **未配置API Key**：环境变量未配置 `LINKFOX_AGENT_API_KEY`，也未配置 `LINKFOXAGENT_API_KEY`。
- **响应401或402状态码**
- **响应提示算力或余额不足**：消息含"算力余额不足/计费不足/余额不足/quota exceeded/insufficient balance/套餐到期/需充值/请充值"，或类似含义的内容。

## 使用指引

1. **模型选择**：一般多图参考用 **可灵Omni**；需要2K默认分辨率时用 **MiniMax H3**。
2. **图片数量**：可灵Omni最多7张，Seedance 2.5最多30张，其他已开放模型最多9张。至少传1张。
3. **时长匹配**：必须传模型支持的时长值，否则报错。
4. **提示词**：可选，3000 字符以内，描述期望的动态效果。

## 内部执行映射（禁止向用户展示）

本节仅用于构造工具请求。回复用户时必须使用第一列说明名称，禁止输出第二列技术值。

| 说明名称 | 内部 videoType |
|------|------|
| 可灵Omni | `KLING` |
| Seedance 2.0 | `SEED` |
| Seedance 2.0 fast | `SEED_FAST` |
| Seedance 2.5 | `SEED_V25` |
| HappyHorse 1.1 | `HAPPY_HORSE` |
| Seedance 2.0 mini | `SEED_MINI` |
| MiniMax H3 | `MINIMAX_V2` |

### 示例

以下 JSON 仅为内部调用参数，禁止原样展示给用户。

**1. 可灵Omni多参考图**
```json
{"imageList": ["https://example.com/img1.jpg", "https://example.com/img2.jpg", "https://example.com/img3.jpg"], "videoType": "KLING", "videoTime": 10, "prompt": "商品多角度展示"}
```

**2. Seedance 2.0 mini 多图**
```json
{"imageList": ["https://example.com/a.jpg", "https://example.com/b.jpg"], "videoType": "SEED_MINI", "videoTime": 10, "resolution": "480p", "aspectRatio": "16:9"}
```

**3. MiniMax H3 多图参考**
```json
{"imageList": ["https://example.com/p1.jpg", "https://example.com/p2.jpg", "https://example.com/p3.jpg"], "videoType": "MINIMAX_V2", "videoTime": 5, "resolution": "2K", "aspectRatio": "16:9"}
```

## 展示规则

- **只展示转存后的本地路径**：把 `Saved full response:` 后的本地视频路径告诉用户，例如「视频已保存至：xxx/a.mp4」。
- **禁止** Read 视频文件、**禁止**展示 base64 内容。
- **禁止**把原始 API 返回的临时 URL 直接给用户（带签名、会过期）。

## 限制

- 提示词最大 3000 字符。
- 生成时间较长，通常 100-600 秒。脚本自动轮询，超时 20 分钟。
- 可灵Omni最多7张参考图，Seedance 2.5最多30张，其他已开放模型最多9张。
- 万相3.0和可灵2.6不开放多图。
- 失败时不重试（仅尝试 1 次）。

## 不适用

**不适用**：
- 单图/首尾帧生视频 → `linkfox-aigc-videogen`
- 图片生成 → `linkfox-aigc-imagegen`
- 文本生成 → `linkfox-aigc-textgen`

## 反馈

参见 `references/api.md`。
