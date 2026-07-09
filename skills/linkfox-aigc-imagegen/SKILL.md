---
name: linkfox-aigc-imagegen
description: AI生图工具，根据提示词和参考图生成图片。支持多种模型（BANANA/BANANA_2/BANANA_PRO/GPT_2_IMAGE/AIDRAW_EDIT/WAN2_7/SEEDREAM5），可控制分辨率、宽高比、输出数量。用户说"生成图片"、"AI画图"、"AI生图"、"帮我画"、"图片生成"、"image generation"、"generate image"、"画一张图"、"做张图"、"图生图"时触发。
---

# AI 生图

根据提示词和参考图生成图片，支持多种 AI 模型，异步创建任务后轮询获取结果。

## 核心特点

- **多模型选择**：7 种模型可选，各有不同特长和分辨率支持。
- **图生图**：可传入参考图+提示词生成新图。
- **批量输出**：单次最多生成 10 张图片。
- **异步模式**：创建任务立即返回 taskId，脚本自动轮询直到完成（超时 10 分钟）。

## 模型说明

| 模型（provider） | 说明 | 特点 |
|------|------|------|
| BANANA | LFBanana（基础版） | 仅支持 1K 分辨率 |
| BANANA_2 | LFBanana2 | 支持更高分辨率 |
| BANANA_PRO | LFBanana Pro（默认） | 综合效果最好 |
| GPT_2_IMAGE | Img2 | 支持 quality 参数控制质量 |
| AIDRAW_EDIT | Linkfox-Image-1 | 适合编辑类场景 |
| WAN2_7 | Wan 2.7 | 万相模型 |
| SEEDREAM5 | Seedream 5.0 | 仅支持2K |

## 参数概览

- **必填字段**：`prompt`、`imageUrls`、`outputNum`（默认 `1`）、`resolution`（默认 `1K`）、`quality`（默认 `high`，仅 GPT_2_IMAGE）

完整参数表、响应字段结构与错误码，见 [`references/api.md`](references/api.md)。

## 调用方式

- **创建任务**：`POST /aigc/imageGenAsync` → 返回 `{taskId}`
- **轮询结果**：`POST /aigc/taskQuery` → 传入 `{taskId}` → 返回状态和结果
- **Python 脚本**：`python scripts/aigc_imagegen.py '<JSON 参数>'`（脚本内部自动完成创建+轮询）

**异步流程**：
1. 脚本调用 `/aigc/imageGenAsync` 创建任务，获得 `taskId`
2. 轮询 `/aigc/taskQuery`，初始间隔 10 秒，每次递减 1 秒至最低 5 秒，最长等待 10 分钟
3. 成功后自动下载图片到会话 `media/` 目录

**文件存储路径约定**（遵循 CLAUDE.md 规范）：

所有文件存储在 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/` 下，按类型划分目录：

| 内容类型 | 目录 | 路径格式 | 说明 |
|----------|------|----------|------|
| 生成的图片 | `media/` | `<session>/media/linkfox-aigc-imagegen-<ts_ms>.<ext>` | 如 `media/linkfox-aigc-imagegen-1718000000000.png` |
| 原始 API 响应 | `data/` | `<session>/data/linkfox-aigc-imagegen-<ts>.json` | 含完整 taskId、状态、临时 URL 等 |

**输出策略（脚本默认行为）**：

1. **成功生成图片时**（无论多少张）：
   - stdout 输出 `Saved full response: <路径数组>` 格式的行，例如：
     - 1张：`Saved full response: ["/path/to/media/a.png"]`
     - 多张：`Saved full response: ["/path/to/media/a.png", "/path/to/media/b.png"]`
   - 原始 API 响应（含临时 URL 等）静默落盘到 `data/`。
   - 前端 UI 可解析 stdout 中**所有** `Saved full response:` 行，把后续 JSON 数组渲染出来。
   - 每次调用脚本通常输出一行；分多次调用时会有多行。

2. **无图片产物时**（失败/无结果）：
   - stdout 输出原始响应路径：`Saved full response: /path/to/data/xxx.json`

**读数据建议**：**禁止** Read 转存的图片文件内容（避免 base64 进入上下文）。直接把 `Saved full response:` 后的本地路径提供给用户即可。

## 使用指引

1. **模型选择**：一般场景用 `BANANA_PRO`（默认）；需要高质量画质控制用 `GPT_2_IMAGE`；编辑现有图片用 `AIDRAW_EDIT`。
2. **提示词**：描述越具体效果越好，建议用英文提示词获得更好效果。
3. **参考图**：必须提供至少一张参考图 URL。
4. **分辨率**：支持 1K/2K/4K，默认 1K。

### 示例

**1. 用默认模型生成商品场景图**
```json
{"imageUrls": ["https://example.com/product.jpg"], "prompt": "product photography on white background, studio lighting", "provider": "BANANA_PRO", "outputNum": 1, "resolution": "1K", "aspectRatio": "1:1", "quality": "high"}
```

**2. 用 GPT_2_IMAGE 高质量生图**
```json
{"imageUrls": ["https://example.com/ref.jpg"], "prompt": "modern minimalist product showcase", "provider": "GPT_2_IMAGE", "outputNum": 1, "resolution": "1K", "aspectRatio": "16:9", "quality": "high"}
```

**3. 批量生成多张**
```json
{"imageUrls": ["https://example.com/ref.jpg"], "prompt": "creative product ad design", "provider": "BANANA_PRO", "outputNum": 4, "resolution": "2K", "aspectRatio": "1:1", "quality": "high"}
```

## 限制

- 必须提供至少一张参考图 URL。
- 单次最多生成 10 张。
- 生成时间视模型和分辨率不同，通常 10-120 秒。脚本自动轮询，超时 10 分钟。
- 失败时不重试（仅尝试 1 次）。

## 不适用

**不适用**：
- 纯文字生成 → `linkfox-aigc-textgen`
- 视频生成 → `linkfox-aigc-videogen`

## 反馈

参见 `references/api.md`。

## 执行指令

**重要**：收到本文档末尾的 `ARGUMENTS:` 字段后，必须立即调用 `python scripts/aigc_imagegen.py '<JSON>'` 执行，**禁止等待用户确认或额外输入**。
