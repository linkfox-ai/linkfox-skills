---
name: linkfox-aigc-videogen-multi
description: 多参考图生视频工具，根据多张参考图和提示词生成视频。支持模型KLING可灵/SEED豆包/SEED_FAST/HAPPY_HORSE百炼，可控制时长、Pro模式、声音、宽高比、生视频"、"多图视频"、"多张图片生成视频"、"多参考图生视频"、"multi image video"、"multiple images to video"时触发。
---

# 多参考图生视频

根据多张参考图和提示词生成视频，支持 3 种 AI 视频模型，异步创建任务后轮询获取结果。

## 核心特点

- **4 种模型选择**：KLING/SEED/SEED_FAST/HAPPY_HORSE，覆盖不同风格和时长。
- **多图参考**：传入多张图片作为参考，AI 综合生成视频。
- **丰富参数**：支持 Pro 模式、声音生成、宽高比、分辨率等。
- **异步模式**：创建任务立即返回 taskId，脚本自动轮询直到完成（超时 20 分钟）。

## 模型说明

| 模型（videoType） | 说明 | 支持时长 | 图片上限 |
|------|------|----------|----------|
| KLING | 可灵 | 5秒/10秒 | ≤7张 |
| SEED | Seedance/豆包 | 5秒/10秒/15秒 | ≤9张 |
| SEED_FAST | Seedance 2.0 Fast | 5秒/10秒/15秒 | ≤9张 |
| HAPPY_HORSE | 百炼HappyHorse | 5秒/10秒/15秒(默认15) | ≤9张 |

## 参数概览

- **必填字段**：`imageList`、`videoType`、`videoTime`
- **可选核心**：`prompt`（2000字以内）、`aspectRatio`、`resolution`

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

## 使用指引

1. **模型选择**：一般多图参考用 `KLING`；高分辨率用 `SEED`；百炼风格用 `HAPPY_HORSE`。
2. **图片数量**：KLING 最多 7 张，SEED/HAPPY_HORSE 最多 9 张。至少传 1 张。
3. **时长匹配**：必须传模型支持的时长值，否则报错。
4. **提示词**：可选，2000 字以内，描述期望的动态效果。

### 示例

**1. KLING 多参考图**
```json
{"imageList": ["https://example.com/img1.jpg", "https://example.com/img2.jpg", "https://example.com/img3.jpg"], "videoType": "KLING", "videoTime": 10, "prompt": "商品多角度展示"}
```

**2. SEED 高分辨率多图**
```json
{"imageList": ["https://example.com/a.jpg", "https://example.com/b.jpg"], "videoType": "SEED", "videoTime": 15, "resolution": "1080p", "aspectRatio": "16:9"}
```

**3. HAPPY_HORSE 多图参考**
```json
{"imageList": ["https://example.com/p1.jpg", "https://example.com/p2.jpg", "https://example.com/p3.jpg"], "videoType": "HAPPY_HORSE", "videoTime": 15, "resolution": "1080p", "aspectRatio": "16:9"}
```

## 展示规则

- **只展示转存后的本地路径**：把 `Saved full response:` 后的本地视频路径告诉用户，例如「视频已保存至：xxx/a.mp4」。
- **禁止** Read 视频文件、**禁止**展示 base64 内容。
- **禁止**把原始 API 返回的临时 URL 直接给用户（带签名、会过期）。

## 限制

- 提示词最大 2000 字符。
- 生成时间较长，通常 100-600 秒。脚本自动轮询，超时 20 分钟。
- KLING 最多 7 张参考图，SEED/HAPPY_HORSE 最多 9 张。
- HAPPY_HORSE 不支持 isPro。
- 失败时不重试（仅尝试 1 次）。

## 不适用

**不适用**：
- 单图/首尾帧生视频 → `linkfox-aigc-videogen`
- 图片生成 → `linkfox-aigc-imagegen`
- 文本生成 → `linkfox-aigc-textgen`

## 反馈

参见 `references/api.md`。
