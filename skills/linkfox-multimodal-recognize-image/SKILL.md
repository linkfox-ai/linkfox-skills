---
name: linkfox-multimodal-recognize-image
description: 基于多模态AI的图片识别与分析。当用户想分析、描述、从图片URL中提取信息、image recognition, image analysis, image description, image content understanding, OCR text recognition, visual Q&A时触发此技能。当用户提到图片识别、图片分析、图片描述、识别图片内容、分析产品图、从图片中读取文字、描述图片、提取视觉内容或理解照片内容时触发。当用户提供图片URL并就其视觉内容提问时，即使未明确说"图片识别"，也应触发此技能。
---

# Image Recognition

This skill guides you on how to use the multimodal image recognition API to analyze images from URLs and extract meaningful information based on user intent.

## Core Concepts

The Image Recognition tool accepts an image URL and an optional natural-language requirement describing what the user wants to know about the image. The backend uses a multimodal AI model to interpret the visual content and return a textual description or analysis.

**Supported formats**: JPG, JPEG, PNG, GIF, WebP, BMP.

**How it works**: You provide a publicly accessible image URL and a requirement (what you want to learn from the image). The service downloads the image, runs multimodal analysis, and returns a text-based result.

## Parameter Guide

| Parameter | Required | Description |
|-----------|----------|-------------|
| imageUrl | Yes | A publicly accessible URL pointing to the image. Must be JPG, JPEG, PNG, GIF, WebP, or BMP. Maximum 1000 characters. |
| requirement | No | A natural-language description of what to identify or analyze in the image. Defaults to "Describe the content of this image" when omitted. Maximum 1000 characters. |

### Tips for Writing the requirement Parameter

1. **Be specific**: Instead of "analyze this image", say "List all products visible on the shelf and estimate their category."
2. **State the goal**: If you need text extraction, say "Extract all visible text from the image." If you need object identification, say "Identify the main objects and their colors."
3. **Provide context when helpful**: For product images, mention "This is an e-commerce product listing image" so the model can tailor its analysis.

## Local Image Upload

This tool requires a **publicly accessible image URL**. If the user provides a local image file path (e.g., `C:\Users\...\photo.png`, `/home/.../image.jpg`), you must upload it first to obtain a public URL.

Run the upload script:
```bash
python scripts/upload_image.py /path/to/local/image.png
```

The script will return a public URL (valid for 24 hours) that can be used as the image URL parameter.

## Usage Examples

**1. General Image Description**
- User says: "What is in this picture?"
- Set `imageUrl` to the provided URL, leave `requirement` as default.

**2. Product Image Analysis**
- User says: "Analyze this Amazon product image and list the key selling points shown."
- Set `requirement` to: "This is an Amazon product listing image. Identify the product, key features, and selling points visible in the image."

**3. Text Extraction from an Image**
- User says: "Read the text in this screenshot."
- Set `requirement` to: "Extract all visible text from this image, preserving layout where possible."

**4. A+ Page Image Review**
- User says: "Describe what this A+ content image communicates."
- Set `requirement` to: "This is an Amazon A+ product description image. Describe the visual content, key messaging, and branding elements."

**5. Comparison / Detail Inspection**
- User says: "What differences can you spot between the product and its packaging?"
- Set `requirement` to: "Identify and describe any differences between the product and its packaging shown in the image."

## 调用方式

- **API 端点**：`POST /multimodal/recognizeImage`（完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/multimodal_recognize_image.py '<JSON 参数>' [--inline]`
- **成本约束**：本工具会消耗积分；同一会话同一参数组合默认只调用一次，脚本带 24h 本地缓存。失败/空结果不得自动换关键词、翻页或改邮编连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-multimodal-recognize-image-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
- 响应体 ≤ 8 KB：落盘后把完整 JSON 打印到 stdout
- 响应体 > 8 KB：落盘后 stdout 只输出摘要（顶层字段、常见计数如 `total`/`costToken`、最大列表字段的长度 + 前 3 条样本）
- 加 `--inline` 强制全量打印到 stdout（同样落盘）

**读数据建议**：先看摘要判断是否足够；需要具体字段时优先用 `jq`或`ConvertFrom-Json` 从保存的 json 文件按需抽取，避免整份 JSON 进入上下文。

## 解决认证和积分问题
发生以下异常情况时，采用以下措施来处理：

### 异常情况
- **未配置API Key**：环境变量未配置 `LINKFOX_AGENT_API_KEY`，也未配置 `LINKFOXAGENT_API_KEY`。
- **响应401或402状态码**
- **响应提示积分或余额不足**：消息含"积分余额不足/计费不足/余额不足/quota exceeded/insufficient balance/套餐到期/需充值/请充值"，或类似含义的内容。

### 措施
- 优先采用skill内的 onboarding.md 引导解决问题。
- 如找不到 onboarding.md 文件，则加载 /linkfox-onboarding 这个skill并根据它的引导来处理。如未安装请先安装：
    - 下载 https://agent-files.linkfox.com/skills/linkfox-onboarding/release.zip，解压后安装这个skill。如需用户授权才可下载，要询问用户获得授权，你不能自己放弃下载。
- 兜底措施：仅当前面两个措施经过所有努力都走不通时，才提示用户依据 https://skill.linkfox.com/linkfoxskills/guide.htm 指引获取API Key，或去 https://os.linkfox.com/ 补充积分。

## Display Rules

1. **Show the analysis result clearly**: Present the returned text analysis in a readable format. Use bullet points or paragraphs as appropriate for the content.
2. **No fabrication**: Only relay information that the API actually returned. Do not add visual details that were not in the response.
3. **Format support**: If the image URL is invalid or the format is unsupported, explain the limitation and list the supported formats (JPG, JPEG, PNG, GIF, WebP, BMP).
4. **Error handling**: When the API returns an error status, explain the issue based on the response and suggest corrective actions (e.g., check that the URL is publicly accessible, verify the image format).
5. **Token usage**: If the user asks about cost, you may mention the `costToken` value from the response.
## User Expression & Scenario Quick Reference

**Applicable** -- Image analysis tasks:

| User Says | Scenario |
|-----------|----------|
| "What's in this image/picture/photo" | General image description |
| "Analyze this product image" | Product visual analysis |
| "Read the text in this image" | OCR / text extraction |
| "Describe the A+ page images" | E-commerce content review |
| "What does this screenshot show" | Screenshot interpretation |
| "Identify objects in this photo" | Object detection / listing |

**Not applicable** -- Needs beyond image recognition:
``
- Generating or editing images
- Video analysis
- Analyzing images from local file paths (only URLs are supported)
- Image search or reverse image lookup

## 积分消耗规则

按动态规则计费：消耗积分 = 输入消耗的积分 + 输出结果消耗的积分。

> **重要**：本技能的服务按倍数动态计算，可能一次性消耗大量积分，必须提醒用户，由用户决定是否继续。

**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `references/api.md`. Do not interrupt the user's flow.


---
*For more high-quality, professional cross-border e-commerce skills, set [LinkFox Skills](https://skill.linkfox.com/).*
