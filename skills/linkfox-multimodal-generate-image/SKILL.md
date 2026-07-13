---
name: linkfox-multimodal-generate-image
description: AI驱动的图片生成与编辑工具，用于制作高质量产品图。当用户要求生成图片、制作图片、编辑照片、文生图、图生图、换背景、变换风格、替换图片中的物体、将产品合成到场景中、换模特、制作任何类型的AI生成视觉内容、AI drawing, image generation, text-to-image, image-to-image, background replacement, style transfer, product image creation, AI image editing时触发此技能。即使用户未明确说"AI图片"，只要其请求涉及生成、修改或变换图片，也应触发此技能。
---

# AI Image Generation

This skill guides you on how to generate and edit images using the AI image generation service, helping users create high-quality product images, modify existing images, and perform creative visual transformations.

## Core Concepts

The AI Image Generation tool produces new images based on a text prompt and optional reference images. It supports a wide range of use cases:

- **Text-to-image**: Generate a brand-new image purely from a text description.
- **Image-to-image**: Provide one or more reference images and a prompt to generate a new image that preserves elements from the references.
- **Image editing**: Modify specific elements, colors, backgrounds, or styles in an existing image.
- **Product compositing**: Place a product from one image into a scene from another image.
- **Model swapping**: Replace the model or mannequin in a product photo.

**Reference images are strongly recommended** when the user wants the output to closely resemble an existing product or scene. Up to 3 reference image URLs can be provided, separated by commas.

## Parameter Guide

| Parameter | Required | Description | Default |
|-----------|----------|-------------|---------|
| prompt | Yes | Text description of the desired image. Supports text-to-image, image-to-image, editing, model swapping, and more. Max 1000 characters. | -- |
| referenceImageUrl | No | URL(s) of reference image(s). Separate multiple URLs with commas. Up to 3 images supported. Max 1000 characters. | -- |
| aspectRatio | No | Aspect ratio of the output image. | 1:1 |

### Supported Aspect Ratios

| Value | Description |
|-------|-------------|
| 1:1 | Square (default) |
| 3:4 | Portrait |
| 4:3 | Landscape |
| 9:16 | Vertical fullscreen |
| 16:9 | Horizontal fullscreen |

### Prompt Writing Tips

1. **Be specific and descriptive**: Clearly describe the subject, scene, lighting, style, and mood you want.
2. **Reference images by number**: When using reference images, refer to them as "image 1", "image 2", etc., in the order they appear in `referenceImageUrl`.
3. **State the operation explicitly**: Use clear action verbs like "replace", "change", "put", "combine", "generate".
4. **Keep within 1000 characters**: Prompts have a maximum length of 1000 characters.

### Prompt Examples by Scenario

**Object replacement**:
```
Replace the vase on the table in image 1 with a potted plant
```

**Background color change**:
```
Change the background color of image 1 to pure white
```

**Product compositing**:
```
Place the product from image 2 onto the marble countertop in image 1
```

**Style transfer**:
```
Transform image 1 into the artistic style shown in image 2
```

**Text-to-image (no reference)**:
```
A professional product photo of a sleek black wireless headphone on a gradient blue background, studio lighting, 8K quality
```

**Model swapping**:
```
Replace the model in image 1 with a different model while keeping the same clothing and pose
```

## Local Image Upload

This tool requires **publicly accessible image URLs** for reference images. If the user provides a local image file path (e.g., `C:\Users\...\photo.png`, `/home/.../image.jpg`), you must upload it first to obtain a public URL.

Run the upload script:
```bash
python scripts/upload_image.py /path/to/local/image.png
```

The script will return a public URL (valid for 24 hours) that can be used as the reference image URL parameter.

## 调用方式

- **API 端点**：`POST /multimodal/generateImage`（完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/multimodal_generate_image.py '<JSON 参数>' [--inline]`
- **成本约束**：本工具会消耗积分；同一会话同一参数组合默认只调用一次，脚本带 24h 本地缓存。失败/空结果不得自动换关键词、翻页或改邮编连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-multimodal-generate-image-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
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

1. **Show the generated image**: When the response contains image content in the `text` field, display it directly to the user using markdown image syntax.
2. **Status reporting**: Check the `status` and `finished` fields. If image generation is still in progress, inform the user and advise waiting.
3. **Prompt transparency**: Briefly describe what prompt and parameters were sent so the user understands what was requested.
4. **Aspect ratio confirmation**: If the user does not specify dimensions, use the default 1:1 ratio but mention it so they can request a different ratio if needed.
5. **Reference image guidance**: If the user wants a result close to an existing image but did not provide a reference URL, proactively suggest they provide one for better fidelity.
6. **Error handling**: When generation fails, explain the issue based on the response `status` field and suggest adjustments (e.g., simplify the prompt, check reference image URLs, try a different aspect ratio).
## Important Limitations

- **Reference image limit**: A maximum of 3 reference image URLs can be provided per request.
- **Prompt length**: The prompt must not exceed 1000 characters.
- **URL validity**: Reference image URLs must be publicly accessible. Private or expired URLs will cause failures.
- **Aspect ratio options**: Only 1:1, 3:4, 4:3, 9:16, and 16:9 are supported.

## User Expression & Scenario Quick Reference

**Applicable** -- Requests involving image generation or editing:

| User Says | Scenario |
|-----------|----------|
| "Generate an image", "Create a picture" | Text-to-image generation |
| "Edit this photo", "Modify the image" | Image editing |
| "Change the background", "Make it white background" | Background replacement |
| "Put the product on this scene" | Product compositing |
| "Make it look like this style" | Style transfer |
| "Swap the model", "Change the person" | Model swapping |
| "Create a product photo" | Product image generation |
| "Make a vertical/landscape version" | Aspect ratio adjustment |

**Not applicable** -- Needs beyond image generation:

- Image analysis or recognition (reading text from images, identifying objects)
- Video generation or editing
- Image file format conversion
- Batch processing of hundreds of images
- Image hosting or storage

## 积分消耗规则

按动态规则计费：消耗积分 = rawTokens × 0.045。

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
