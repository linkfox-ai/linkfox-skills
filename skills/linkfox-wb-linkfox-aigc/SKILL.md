---
name: linkfox-wb-linkfox-aigc
display_name: LinkFox 跨境商品图片和视频
display_name_en: LinkFox Cross-border Product Image and Video
description: 面向跨境电商的商品视觉内容生成能力，按商品类型和创作目标生成商品图、服饰图、品牌视觉基因、营销文案及单图或多参考图视频。
description_zh: 面向跨境电商商品内容生产：根据参考图片、提示词和品牌信息生成商品主图、场景图、特写图、卖点图、A+图、服饰模特图、尺码图及单图或多参考图视频，并支持品牌视觉基因提取、图文/视频理解和文案生成。适用于 Listing 视觉素材、广告素材、品牌视觉统一和商品视频制作；完整参数、响应字段、错误码与套图规则见 references/。
description_en: Cross-border e-commerce visual content generation for product listings and marketing. Create product and apparel images, model and size images, selling-point and A+ creatives, single-image or multi-reference videos, brand visual genes, and supporting copy or media analysis from reference assets and prompts.
icon: icons/logo.png
version: 2.1.0
author: Linkfox
---

> [!IMPORTANT]
本 Skill 必须依赖 MCP “LinkFox”。如未安装该MCP，请明确通知用户：
> 请先安装 LinkFox 连接器：
> - 在 WorkBuddy 左侧找到 “专家·技能·连接器” → “连接器”；
> - 搜索关键词 “LinkFox”，并安装连接器 “LinkFox”（注意：是 linkfox，不是 linkfox-product-selection），按指引完成登录授权；
> - 返回 WorkBuddy 重试。


# LinkFox 跨境商品图片和视频

## MCP 契约

- MCP server：`LinkFox`
- 唯一工具：`proxy_call`
- 调用结构：向 `proxy_call` 传 `toolName`（endpoint 去前导 `/` 的精确值）和对应请求对象 `arguments`。
- 允许的 `toolName`：
  - `aigc/imageGenAsync`
  - `aigc/taskQuery`
  - `aigc/textGenAsync`
  - `aigc/textTaskQuery`
  - `aigc/videoGenAsync`
  - `aigc/multiImageVideoGenAsync`
  - `oss/getStsVoucherByAPI`（本地文件上传的临时凭证）
- `toolName` 区分大小写；请求对象直接作为 `arguments`，不得再包 `body` / `params` / `data`。
- WorkBuddy 自动注入 Authorization；禁止 `headers`、API Key、token、JWT、手机号或其他凭证。
- 禁止 curl、`urllib`、`requests`、`httpx` 等方式直连旧网关；MCP 缺失时不得 HTTP fallback。
- 同一任务相同 `toolName + arguments` 不重复调用。生成失败、空结果或结果不理想时不得自动换模型、改素材或重建任务。
- 先检查 MCP schema、`isError` 和代理错误；text JSON 只解析一次，再检查下游 `errcode` / `errorCode` / `errmsg` / `errorMsg` / `status`。

配置：

```json
{"mcpServers":{"LinkFox":{"type":"streamableHttp","url":"https://mcp-tool-gateway.linkfox.com/mcp/any-tool"}}}
```

## 能力路由

| 需求 | reference | 创建 toolName | 查询 toolName | 本地辅助 |
|---|---|---|---|---|
| 通用生图 | `linkfox-aigc-imagegen-api.md` | `aigc/imageGenAsync` | `aigc/taskQuery` | `scripts/local/download_results.py` |
| 生文、图片/视频理解 | `linkfox-aigc-textgen-api.md` | `aigc/textGenAsync` | `aigc/textTaskQuery` | 无 |
| 单图/首尾帧视频 | `linkfox-aigc-videogen-api.md` | `aigc/videoGenAsync` | `aigc/taskQuery` | `scripts/local/download_results.py` |
| 多参考图视频 | `linkfox-aigc-videogen-multi-api.md` | `aigc/multiImageVideoGenAsync` | `aigc/taskQuery` | `scripts/local/download_results.py` |
| 品牌视觉基因 | `linkfox-aigc-imagegen-brand-gene-extract.md` + textgen API | `aigc/textGenAsync` | `aigc/textTaskQuery` | `scripts/brand/save_brand_gene.py` |
| 服饰套图 | `linkfox-aigc-imagegen-cloth.md` 及同前缀 reference | 按任务选 image/text 创建 endpoint | 对应查询 endpoint | `scripts/cloth/` 中 builder、计划落盘与 summary |
| 非服饰商品套图 | `linkfox-aigc-imagegen-product.md` 及同前缀 reference | 按任务选 image/text 创建 endpoint | 对应查询 endpoint | `scripts/product/` 中 builder、计划落盘与 summary |
| 本地文件 / 图片上传为公开 URL | [references/file-upload.md](references/file-upload.md) | `oss/getStsVoucherByAPI` | 无 | 按内置文档提取临时 Python 脚本执行 OSS 上传 |

## 本地文件与图片上传

- 输入为本地临时文件、图片或需公开的产物时，读取并按本 skill 内置的 [references/file-upload.md](references/file-upload.md) 执行上传，无需查找或安装额外上传 skill。
- 先按文档确认文件可公开，再通过 `LinkFox.proxy_call` 调用 `{"toolName":"oss/getStsVoucherByAPI","arguments":{}}`；取得并校验临时凭证后，按内置文档通过标准输入交给临时脚本执行 OSS 上传，完成后删除脚本。
- 仅使用成功项的公开 HTTPS `url` 替换对应本地路径，保持输入顺序；已是公开 URL 的输入直接复用。依赖、服务端限制、错误处理和凭证保护按内置文档执行。
- 套图 manifest 若仍含本地 `media/` 路径，需要公开交付时先按该内置文档上传并更新 URL。

## 异步状态机

1. 创建前确认模型、输出数量、分辨率、时长及预计积分影响。
2. 调用创建 endpoint 一次，保存返回的 `taskId`。
3. 同一任务最多查询一次状态。`PROCESSING` 时返回 taskId 和建议等待时间，后续由用户明确继续；不得创建重复任务。
4. `SUCCESS` 时读取 `content` 或 `resultList[].url`。图片/视频 URL 可直接交付，或用 `scripts/local/download_results.py` 下载至本地；该脚本只访问响应中的 HTTP(S) 结果 URL，不访问 LinkFox 网关。
5. `FAILED` 时展示 `errorMsg`，不得自动重试。

旧核心脚本的自动轮询、网关响应落盘和 stdout 摘要已移除。MCP 不提供旧 24 小时缓存。结果追溯依靠 `taskId`、原始 MCP 响应和套图本地状态文件。

## 套图流程

- 根据 cloth/product reference 判断图片类型、场景、布局、品牌和敏感词规则。
- 使用保留的 `build_imagegen_prompt.py` / `build_textgen_params.py` 构造参数；它们只做本地参数转换。
- 规划结果可由 `save_image_plan.py` 保存。向用户展示图片类型、数量、模型、比例和成本影响并确认。
- 确认后，Agent 按计划逐任务调用 MCP；每个任务保存 taskId 和终态结果。不得使用已移除的旧 dispatch runner。
- 将成功媒体 URL 用 `download_results.py` 下载后，交给保留的 `collection_summary.py` 汇总；product 可继续生成 `collection-asset-manifest.json`。
- 品牌基因用 textgen 生成后，按品牌 reference 补齐完整字段，再用 `save_brand_gene.py` 校验落盘。已有完整 `brandGeneJson` 不重复提取。

## 参数与安全

- 图片、生文和视频参数、模型枚举、数量、比例、分辨率、时长及互斥约束以四个 API reference 为准。
- 生图最多 10 张；文本媒体列表图片最多 10 张；多图视频 KLING 最多 7 张，SEED/SEED_FAST/HAPPY_HORSE 最多 9 张。
- 单图需求不启动套图流程；纯文本 `imageUrls` 传空数组；不要混淆 `imageUrl`、`imageUrls` 与 `imageList`。
- 写入图片的文案、品牌信息和产品事实必须来自用户素材或明确输入，不臆造认证、功效、销量或平台合规结论。
- 生成结果标注 AI 生成/模型分析；不代表平台审核、知识产权清洁或法律意见。

## 认证与错误

- MCP 或工具缺失、MCP 401、下游 401/402、403 和其他错误的分层处理见 `references/onboarding.md`。
- 402/算力不足引导访问 `https://agent.linkfox.com/`；不得自动选套餐、下单、支付或轮询。
- Feedback API 位于 `https://skill-api.linkfox.com/api/v1/public/feedback`，与工具网关分离，不迁移；仅在用户明确要求时调用。
