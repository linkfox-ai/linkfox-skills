---
name: linkfox-aigc-imagegen
description: AI生图工具，根据提示词或参考图生成图片。支持配置中已开放的多种图片模型，可控制分辨率、宽高比、质量和输出数量。用户说"生成图片"、"AI画图"、"AI生图"、"帮我画"、"图片生成"、"image generation"、"generate image"、"画一张图"、"做张图"、"图生图"时触发。
---

# AI 生图

根据提示词和参考图生成图片，支持多种 AI 模型，异步创建任务后轮询获取结果。

## 核心特点

- **多模型选择**：10 种模型可选，各有不同特长和分辨率支持。
- **文生图/图生图**：可仅使用提示词生成，也可传入参考图+提示词生成新图。
- **批量输出**：单次最多生成 10 张图片。
- **异步模式**：创建任务立即返回 taskId，脚本自动轮询直到完成（超时 10 分钟）。

## 模型说明

| 说明名称 | 支持分辨率 | 参考图上限 | 特点 |
|------|------|------|------|
| LF全能模型 | 1K | 6张 | 基础生成 |
| LF全能模型 2 | 1K/2K/4K | 10张 | 支持更高分辨率 |
| LF全能模型 Pro（兼容默认） | 1K/2K/4K | 10张 | 保持旧调用默认行为 |
| LF智能模型 G-2 | 1K/2K/4K | 10张 | 支持 low/medium/high 质量档位 |
| Linkfox-Image-1 | 2K | 4张 | 适合编辑类场景 |
| Wan 2.7 | 1K/2K | 6张 | 创意增强 |
| Seedream 5.0 | 2K | 6张 | 仅支持2K |
| LF智能模型 G-2.5 Sunburst | 1K/2K/4K（默认2K） | 10张 | 支持 low/medium/high/xhigh/max 质量档位 |
| LF智能模型 G-2.5 Flare | 1K/2K/4K（默认2K） | 10张 | 支持 low/medium/high/xhigh/max 质量档位 |
| Seedream 5.0 Pro | 1K/2K | 6张 | 不使用 quality 档位 |

## 展示规则

- 面向用户介绍、推荐、确认模型或解释错误时，只能使用上表的**说明名称**。
- 禁止向用户展示请求字段值、模型别名、provider 或下游模型 code。
- 用户未指定模型时使用 **LF全能模型 Pro**，不得改为跟随后台默认模型。

## 参数概览

- **必填字段**：`prompt`
- **参考图**：`imageUrls` 可选；不传或传空列表时为文生图，传入时为参考图生图。
- **常用可选字段**：`outputNum`（默认 `1`）、`resolution`、`aspectRatio`、`quality`

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

## 解决认证和算力问题
发生以下异常情况时，采用 references/onboarding.md 引导解决问题：

### 异常情况
- **未配置API Key**：环境变量未配置 `LINKFOX_AGENT_API_KEY`，也未配置 `LINKFOXAGENT_API_KEY`。
- **响应401或402状态码**
- **响应提示算力或余额不足**：消息含"算力余额不足/计费不足/余额不足/quota exceeded/insufficient balance/套餐到期/需充值/请充值"，或类似含义的内容。

## 使用指引

1. **模型选择**：一般场景用 **LF全能模型 Pro**（兼容默认）；需要更高质量档位时用 **LF智能模型 G-2.5 Sunburst** 或 **LF智能模型 G-2.5 Flare**；编辑现有图片用 **Linkfox-Image-1**。
2. **提示词**：描述越具体效果越好，建议用英文提示词获得更好效果。
3. **参考图**：可选；传入时具体上限按模型说明表执行。
4. **分辨率**：必须选择模型支持的分辨率。两个 G-2.5 模型未指定时默认2K；旧模型继续保留原调用默认行为，Skill 内部调用仍应显式传入合法分辨率。

## 内部执行映射（禁止向用户展示）

本节仅用于构造工具请求。回复用户时必须使用第一列说明名称，禁止输出第二列技术值。

| 说明名称 | 内部请求值 |
|------|------|
| LF全能模型 | `LF_BN_1` |
| LF全能模型 2 | `LF_BN_2` |
| LF全能模型 Pro | `LF_BN_3` |
| LF智能模型 G-2 | `LF_GT_1` |
| Linkfox-Image-1 | `LF_AD_1` |
| Wan 2.7 | `LF_WN_1` |
| Seedream 5.0 | `LF_SD_1` |
| LF智能模型 G-2.5 Sunburst | `LF_GT_2` |
| LF智能模型 G-2.5 Flare | `LF_GT_2_F` |
| Seedream 5.0 Pro | `LF_SD_2` |

工具端继续兼容历史请求值，但新调用统一使用上表内部请求值。

### 示例

以下 JSON 仅为内部调用参数，禁止原样展示给用户。

**1. 用 LF全能模型 Pro 生成商品场景图**
```json
{"imageUrls": ["https://example.com/product.jpg"], "prompt": "product photography on white background, studio lighting", "provider": "LF_BN_3", "outputNum": 1, "resolution": "1K", "aspectRatio": "1:1", "quality": "high"}
```

**2. 用 LF智能模型 G-2.5 Sunburst 高质量生图**
```json
{"imageUrls": ["https://example.com/ref.jpg"], "prompt": "modern minimalist product showcase", "provider": "LF_GT_2", "outputNum": 1, "resolution": "2K", "aspectRatio": "16:9", "quality": "xhigh"}
```

**3. 批量生成多张**
```json
{"imageUrls": ["https://example.com/ref.jpg"], "prompt": "creative product ad design", "provider": "LF_BN_3", "outputNum": 4, "resolution": "2K", "aspectRatio": "1:1", "quality": "high"}
```

## 限制

- 参考图 URL 可选；传入时具体上限按所选模型配置执行。
- 单次最多生成 10 张。
- 生成时间视模型和分辨率不同，通常 10-120 秒。脚本自动轮询，超时 10 分钟。
- 失败时不重试（仅尝试 1 次）。

## 不适用

**不适用**：
- 文本生成 → `linkfox-aigc-textgen`
- 视频生成 → `linkfox-aigc-videogen`

## 反馈

参见 `references/api.md`。

## 执行指令

**重要**：收到本文档末尾的 `ARGUMENTS:` 字段后，必须立即调用 `python scripts/aigc_imagegen.py '<JSON>'` 执行，**禁止等待用户确认或额外输入**。
