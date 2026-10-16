---
name: linkfox-aigc-imagegen
description: AI生图工具，根据提示词或参考图生成图片。支持配置中已开放的多种图片模型，可控制分辨率、宽高比、质量和输出数量。用户说"生成图片"、"AI画图"、"AI生图"、"帮我画"、"图片生成"、"image generation"、"generate image"、"画一张图"、"做张图"、"图生图"时触发。
---

# AI 生图

根据提示词和参考图生成图片，支持多种 AI 模型，异步创建任务后轮询获取结果。

## 动态模型列表（仅替换目录来源）

- 模型配置域名由 `LINKFOX_AI_API_URL` 覆盖（默认 `https://ai-api.linkfox.com`），与生成网关 `LINKFOX_TOOL_GATEWAY` 独立；测试/生产配置见 [references/model-config.md](references/model-config.md)。
- 选择模型前调用 `python scripts/aigc_imagegen.py --list-models --inline`；图片查 bizType=201，两个视频入口查 bizType=88。
- 普通场景按动态完整列表选择，不由旧模型目录封顶。明确的专用业务范围只在查询时用 `--allowed-models` 取交集；生成仍按原脚本 JSON 调用，不传这个新查询参数。
- 只有查询失败才用下方原静态表兜底；成功但缺失/维护中不补回，不自动换模型。
- 正常生成不额外查询或存档配置，不新增提交前参数校验，不更改请求参数、默认策略、轮询、下载及交付。
- 模型能力用于介绍和选择选项，不作为一套新的生成请求白名单；编码适配、异常和落盘说明见 [references/model-config.md](references/model-config.md)。

## 核心特点

- **多模型选择**：优先读取动态模型配置，静态表仅用于查询失败兜底。
- **文生图/图生图**：可仅使用提示词生成，也可传入参考图+提示词生成新图。
- **批量输出**：单次最多生成 10 张图片。
- **异步模式**：创建任务立即返回 taskId，脚本自动轮询直到完成（超时 10 分钟）。

## 模型说明（仅配置查询失败时兜底）

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

- 面向用户介绍、推荐、确认模型或解释错误时，只能使用动态配置返回的 **name**（查询失败时使用上表的**说明名称**）。
- 禁止向用户展示请求字段值、模型别名、provider 或下游模型 code。
- 用户未指定模型时使用 **LF全能模型 Pro**，不得改为跟随后台默认模型。

## 参数概览

- **必填字段**：`prompt`
- **参考图**：`imageUrls` 可选；不传或传空列表时为文生图，传入时为参考图生图。
- **常用可选字段**：`outputNum`（默认 `1`）、`resolution`、`aspectRatio`、`quality`

完整参数表、响应字段结构与错误码，见 [`references/api.md`](references/api.md)。

## 参考图上传（file-upload）

- `imageUrls` 接收可访问的图片 URL，不接收本地文件路径。仅在传入参考图时执行素材准备；文生图不传或传空数组，无需上传。
- 逐项检查 `imageUrls`，保持原顺序：已有可公开访问的 HTTP(S) URL 直接复用；本地图片或附件先按本 skill 内置的 [references/file-upload.md](references/file-upload.md) 上传，再用成功项的 `url` 替换对应路径。无需查找或安装额外上传 skill。
- 上传失败时停止本次生成并说明原因，不把本地路径或失败项传给生成接口。生成脚本不自动上传，素材准备完成后再创建任务。

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

1. **模型选择**：一般场景用 **LF全能模型 Pro**（兼容默认）；需要更高质量档位时用 **LF智能模型 G-2.5 Sunburst** 或 **LF智能模型 G-2.5 Flare**；编辑现有图片用 **Linkfox-Image-1**。
2. **提示词**：描述越具体效果越好，建议用英文提示词获得更好效果。
3. **参考图**：可选；传入时以上述动态查询返回的参考图上限为准；查询失败才用静态表。
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

已有模型保留上表请求别名；动态新增且无旧别名的图片模型使用配置 apiCode，由脚本完成规范化。

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

**重要**：收到本文档末尾的 `ARGUMENTS:` 字段后，先按上述参考图上传指引完成必要的素材准备，再立即调用 `python scripts/aigc_imagegen.py '<JSON>'` 执行；已有可用 URL 或纯文生图直接调用。上传授权按内置文档处理，其余生成参数齐全时不额外等待确认。
