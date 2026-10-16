---
name: linkfox-aigc-video-edit
description: 按编辑指令修改已有视频，可提供参考图片。用于视频编辑、视频背景替换、视频风格修改、video editing。
---

# Video Editing

Edit a source video with an instruction and optional reference images.

## Core Concepts

- This endpoint creates one asynchronous task. A returned taskId is acceptance, not a finished asset.
- Supply a new unique requestId for each newly requested task. Preserve it when checking or retrying the same operation; do not automatically resubmit after a timeout.
- All source images/videos, including external HTTP(S) URLs, must use the **bundled Base64 upload** workflow in [references/file-upload.md](references/file-upload.md): run this skill's bundled `scripts/upload_file.py`, obtain `viewUrl`, then populate the generation media fields. Upload must finish before creating a task; do not use STS/OSS upload or upload again while polling.
- Put all business fields inside the required `params` object. Keep requestId/chatId/messageId/title at the top level; do not send a top-level memberId. Read [references/api.md](references/api.md) and do not substitute legacy model aliases.
- Poll /aigc/taskQuery, which serves both these new tasks and existing image/video tasks. There is no separate makeTaskQuery endpoint in this backend branch.

## Parameter Guide

Required business fields inside `params`: `sourceVideoUrl`, `prompt`, `videoType`

Read [references/api.md](references/api.md) for the complete request schema, conditional requirements and model-specific rules before constructing parameters.

## 调用方式

- **API 端点**：`POST /aigc/videoEditing`（完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/video_editing_async.py '<JSON 参数>' [--inline]`
- **成本约束**：本工具会消耗积分；同一会话同一参数组合默认只调用一次，脚本带 24h 本地缓存。生成失败或超时不得自动更换模型、重建任务或扩大生成数量；下载失败只重试下载，继续生成前说明额外消耗。

以下固定输出策略适用于官方 API 入口。完整生成流程使用 run_task.py，其媒体输出见 Execution Workflow。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-aigc-video-edit-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
- 响应体 ≤ 8 KB：落盘后把完整 JSON 打印到 stdout
- 响应体 > 8 KB：落盘后 stdout 只输出摘要（顶层字段、常见计数如 `total`/`costToken`、最大列表字段的长度 + 前 3 条样本）
- 加 `--inline` 强制全量打印到 stdout（同样落盘）

**读数据建议**：先看摘要判断是否足够；需要具体字段时优先用 `jq`或`ConvertFrom-Json` 从保存的 json 文件按需抽取，避免整份 JSON 进入上下文。

## Runtime Output Preconditions

Run from a writable task working directory and unset ACPX_WORKSPACES for this invocation if output must stay under cwd. Verify the output directory is writable before execution; if not, stop rather than relying on a fallback. The unchanged official template can otherwise choose ACPX_WORKSPACES, home or a temporary-directory fallback: the fixed output policy above is a workflow requirement, not an OS restriction enforced by the script. On Windows use PYTHONUTF8=1 or `python -X utf8` so saved JSON and console output remain UTF-8.

## Execution Workflow

1. Read references/api.md and choose parameters supported by this endpoint. Use user-facing model names from the documented model table when explaining choices; keep provider/videoType codes inside requests. Do not import defaults or legacy aliases from old generation APIs.
2. For a full generation request, run `python <skill-root>/scripts/run_task.py '<JSON parameters>'`. Business fields must be nested inside `params`. Media fields inside `params` may contain local file paths or external URLs: the workflow uploads every distinct source through uploadByBase64 before creation, preserves list order and reuses only its own uploaded-source mapping. Use `--params-file <path>` or `-` for stdin when parameters are long.
3. The workflow creates once, saves the accepted taskId, and polls taskQuery without cache. Image tasks wait up to 10 minutes; video tasks wait 120 seconds initially and up to 20 minutes total. Default polling is 5–10 seconds for images and 10 seconds for videos. A timeout retains the task: resume with `python <skill-root>/scripts/run_task.py --task-id <saved-id>`, never restart creation or uploads.
4. SUCCESS saves successful result files to the session media directory and keeps the original query JSON plus an asset manifest under data. The manifest retains resource IDs/types, download failures and actual query costToken/costCredit; creation costToken=0 never overwrites final cost. A media download failure is retried with `python <skill-root>/scripts/download_results.py <saved-query-json>`, not by creating another task.
5. Parse the `Saved full response: ["<absolute media path>", ...]` line for generated files. Render successful images with Markdown `![label](<absolute-path>)`; for videos show the local file link/player. Read the manifest to report download failures and cost. This backend does not expose per-item generation status/errors. Do not Read binary media or repeat the raw protocol line in the user-facing reply.
6. The official creation and query scripts remain available for explicit low-level use. Creation accepts uploaded viewUrl values only; `query_task.py` must always use `--no-cache`. Finish a low-level successful query by running download_results.py on its saved JSON. Authentication or billing failures follow references/onboarding.md.

## Example

The JSON below uses the required params wrapper and illustrates low-level creation; media values must be viewUrl values from uploadByBase64. For run_task.py, supply the actual source file paths or source URLs in the media fields; it uploads them first. Example requestId/taskId values must not be reused for unrelated tasks.

```json
{
  "requestId": "video-edit-task-001",
  "params": {
    "sourceVideoUrl": "https://example.com/source.mp4",
    "prompt": "Change the background to a studio while preserving the product",
    "videoType": "kling-v3-omni"
  }
}
```

## Display Rules

- Present generated local media, task status, download failures and actual reported cost. Use friendly model names; do not expose request codes or signed source URLs.
- Do not show API keys, Base64 media, authorization headers or internal tool identifiers.
- The official API entries save JSON; run_task.py additionally downloads media and emits the local-path array used for rendering. Never present a JSON file as the generated image/video.

## 解决认证和算力问题

For missing API keys, authentication errors (401 or equivalent auth messages), or insufficient balance (402 or equivalent billing messages), read [references/onboarding.md](references/onboarding.md) and use this skill's `scripts/onboarding.py`. Resolve its absolute path from this SKILL.md. A 403 ownership/permission error is not a recharge problem.

Follow the existing onboarding flow: let the user choose self-service or phone login; send SMS only after that choice, and create a recharge order only after the user selects a plan and payment method. Do not poll payment automatically. Do not save login tokens, SMS codes or API keys into task JSON, cache or source files; the user's API environment variable is the credential configuration.

## Important Limitations

- API keys are read only from LINKFOX_AGENT_API_KEY or LINKFOXAGENT_API_KEY. The gateway is LINKFOX_TOOL_GATEWAY, defaulting to https://tool-gateway.linkfox.com.
- On missing credentials, authentication failure or insufficient balance, stop the generation workflow and follow references/onboarding.md. Do not automatically probe other models or start more chargeable tasks.
- Model-specific media limits and generation defaults are enforced by the API. Do not invent unsupported capabilities.

## User Expression

- **Direct:** 视频编辑。
- **Contextual:** Use this capability when the user's requested operation matches the documented inputs and outputs.
- **Boundary:** Existing generic image generation, old video-generation tasks and unrelated creative operations keep their original workflows.

## Feedback

See [references/api.md](references/api.md#feedback) for error reporting.
