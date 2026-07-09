---
name: linkfox-aigc-videogen
description: AI生视频工具（首尾帧/单图模式），根据原图和提示词生成视频，支持可选尾帧图控制结束画面。支持模型KLING可灵/WAN万相/SEED豆包/SEED_FAST/HAILUO海螺。用户说"生成视频"、"AI视频"、"图生视频"、"做个视频"、"video generation"、"generate video"、"图片转视频"、"动态视频"时触发。
---

# AI 生视频（首尾帧/单图模式）

根据原图（首帧）和可选尾帧图生成视频，支持多种 AI 视频模型，异步创建任务后轮询获取结果。

## 核心特点

- **5 种模型选择**：覆盖不同风格和时长需求。
- **首尾帧控制**：可选尾帧图控制视频结束画面。
- **丰富参数**：支持 Pro 模式、声音生成、运镜控制、宽高比等。
- **异步模式**：创建任务立即返回 taskId，脚本自动轮询直到完成（超时 20 分钟）。

## 模型说明

| 模型（videoType） | 说明 | 支持时长       |
|------|------|------------|
| KLING | 可灵 | 5秒/10秒     |
| WAN | 万相 | 5秒/10秒/15秒 |
| SEED | Seedance/豆包 | 5秒/10秒/15秒 |
| SEED_FAST | Seedance 2.0 Fast | 5秒/10秒/15秒 |
| HAILUO | 海螺 | 6秒/10秒     |

## 参数概览

- **必填字段**：`imageUrl`、`videoType`、`videoTime`
- **可选核心**：`lastFrameImageUrl`（尾帧图）、`prompt`（2000字以内）

完整参数表、响应字段结构与错误码，见 [`references/api.md`](references/api.md)。

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

## 使用指引

1. **模型选择**：一般商品视频用 `KLING`；长时长用 `WAN`/`SEED`。
2. **首尾帧**：传 `imageUrl`（首帧，必传）+ 可选 `lastFrameImageUrl`（尾帧），支持模型：KLING仅Pro / WAN / SEED。
3. **时长匹配**：必须传模型支持的时长值，否则报错。
4. **提示词**：可选，2000 字以内，描述期望的动态效果。

### 示例

**1. KLING — 商品展示**
```json
{"imageUrl": "https://example.com/product.jpg", "videoType": "KLING", "videoTime": 10, "prompt": "商品展示视频"}
```


**3. WAN 万相 — 带声音和运镜**
```json
{"imageUrl": "https://example.com/scene.jpg", "videoType": "WAN", "videoTime": 15, "voice": true, "camera": "single"}
```

**4. SEED — 高分辨率**
```json
{"imageUrl": "https://example.com/scene.jpg", "videoType": "SEED", "videoTime": 10, "resolution": "1080p", "aspectRatio": "16:9"}
```

## 展示规则

- **只展示转存后的本地路径**：把 `Saved full response:` 后的本地视频路径告诉用户，例如「视频已保存至：xxx/a.mp4」。
- **禁止** Read 视频文件、**禁止**展示 base64 内容。
- **禁止**把原始 API 返回的临时 URL 直接给用户（带签名、会过期）。

## 限制

- 提示词最大 2000 字符。
- 生成时间较长，通常 100-600 秒。脚本自动轮询，超时 20 分钟。
- KLING 尾帧图仅 Pro 模式下支持。
- 本接口仅支持单图/首尾帧模式。多参考图请使用 `linkfox-aigc-videogen-multi`。
- 失败时不重试（仅尝试 1 次）。

## 不适用
**不适用**：
- 多参考图生视频 → `linkfox-aigc-videogen-multi`
- 图片生成 → `linkfox-aigc-imagegen`
- 文本生成 → `linkfox-aigc-textgen`

## 反馈

参见 `references/api.md`。
