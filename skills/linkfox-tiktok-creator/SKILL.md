---
name: linkfox-tiktok-creator
description: TikTok 达人（Creator/affiliate creator）数据与可购物视频技能，经 LinkFox 网关代理调用 TikTok Shop 达人开放接口：达人主页/档案、达人绑定店铺商品、橱窗商品、可购物视频的上传/内容预检/发布/发布状态查询。需要达人 access_token（user_type=1），由 linkfox-tiktok-auth 以 appType=creator 授权获得。当用户提到 TikTok 达人、TikTok creator、达人主页、达人档案、达人资料、达人店铺商品、达人绑定店铺商品、达人橱窗商品、showcase 商品、上传可购物视频、发布可购物视频、视频发布状态、视频内容预检、shoppable video、affiliate creator、TikTok 带货达人信息、TikTok creator profile、shop products、showcase products、post shoppable video、video status、precheck 时触发此技能。即使用户未写 EHunt/紫鸟，只要需求是查 TikTok Shop 达人的资料、绑定商品或可购物视频带货操作，也应触发。
---

# TikTok 达人（Creator）数据

本 skill 通过 **LinkFox 网关 → 紫鸟代理 → TikTok Shop 达人(affiliate_creator)开放接口**，提供 TikTok 带货达人的数据查询（达人资料、绑定店铺商品、橱窗商品）与可购物视频带货操作（上传、内容预检、发布、状态查询）。全部接口收录在 `references/api.md`。

> 📌 **前置依赖**：本 skill 需要 **达人 access_token（`user_type=1`）**。请先用 `linkfox-tiktok-auth` 以 **`appType=creator`** 完成达人授权并取得 `accessToken`，再作为本 skill 调用的 `ttsAccessToken` 传入。

## Core Concepts

- **调用链路**：业务请求统一经 LinkFox 网关的 **`/tiktokShop/developerProxy`** 转发：传入 **`appType=creator`**、TikTok Shop API 的相对 `path`（如 `affiliate_creator/202508/profiles`）、`method` 与达人令牌 `ttsAccessToken`；紫鸟自动注入 `app_key` / `timestamp` / `sign`，并透传 TikTok 原始响应。达人接口的 `appType` 必须为 `creator`（脚本已默认）。
- **达人令牌**：`ttsAccessToken` 为达人 access_token（`user_type=1`），来自 `linkfox-tiktok-auth`（`appType=creator`）。令牌过期时回到该 skill 刷新。
- **响应透传**：网关返回 `httpStatus` / `contentType` / `body`，其中 `body` 为 TikTok 原始 JSON 字符串；TikTok 业务层的成功/失败以其 `code` / `message` 为准。

## API Usage

本 skill 经 LinkFox 网关代理调用，详见 `references/api.md`。

### Available Scripts

- `scripts/creator_proxy.py` — 通用达人接口代理：按 `path` + `method` + `ttsAccessToken` 调用任意已收录的达人接口。

### 已收录接口

| 能力 | 上游 path | Method |
|------|-----------|--------|
| 获取达人主页/档案（Get Creator Profile） | `affiliate_creator/202508/profiles` | GET |
| 搜索达人绑定店铺的商品（Get Shop Products） | `affiliate_creator/202509/shop_products` | GET |
| 达人橱窗商品列表（Get Showcase Products） | `affiliate_creator/202405/showcases/products` | GET |
| 上传可购物视频文件（Upload Shoppable Video File，multipart） | `affiliate_creator/202505/videos/video_files` | POST |
| 发布可购物视频（Post Shoppable Video） | `affiliate_creator/202603/videos` | POST |
| 查询可购物视频发布状态（Get Shoppable Video Status） | `affiliate_creator/202509/videos/{video_id}/status` | GET |
| 可购物视频内容预检（Pre-check Shoppable Video） | `affiliate_creator/202511/videos/precheck_task` | POST |
| 查询视频预检结果（Get Shoppable Video Pre-check Result） | `affiliate_creator/202511/videos/precheck_tasks/{task_id}` | GET |

> ⚠️ 含 `multipart/form-data` 二进制上传的接口（Upload Shoppable Video File）不走通用 `creator_proxy.py`，需 multipart 链路，详见 `references/api.md`。

## 典型编排流程

**A. 选品 / 查达人数据**
1. 达人资料：Get Creator Profile（接口 1）
2. 商品：Get Shop Products（接口 2，按关键词搜店铺商品）或 Get Showcase Products（接口 3，达人橱窗/直播袋）→ 拿到 `product_id`

**B. 可购物视频带货（发布全链路）**
1. **上传视频**：Upload Shoppable Video File（接口 4）→ 拿 `file_id`（⚠️ multipart，见限制）
2. **内容预检**：Pre-check Shoppable Video（接口 7，传 `file_id` + `product_id`）→ 拿 `task_id`
3. **查预检结果**：Get Shoppable Video Pre-check Result（接口 8，凭 `task_id`）→ `result=SUCCESS` 才继续；`FAIL` 看 `issues[]` 整改
4. **发布**：Post Shoppable Video（接口 5，传 `file_id` + `product_id` + 标题/封面）→ 拿 `video.id`
5. **查发布状态**：Get Shoppable Video Status（接口 6，凭 `video_id`）→ `post_status` 为 `SUCCESS`/`FAIL`/`PROCESSING`

> 所有调用都需先经 `linkfox-tiktok-auth`（`appType=creator`）拿到达人 `accessToken` 作为 `ttsAccessToken`。

## Display Rules

1. **只呈现数据**：展示达人资料字段即可，不做主观评价。
2. **令牌安全**：不要明文输出完整 `ttsAccessToken`，仅展示掩码。
3. **错误说明**：失败时依据 TikTok 业务 `code` / `message` 与网关 `httpStatus` 解释原因。
4. **前置校验**：无达人令牌时，先引导用户经 `linkfox-tiktok-auth`（`appType=creator`）授权。

## Important Limitations

- **达人令牌必备**：所有接口都需 `user_type=1` 的达人 access_token；店铺(erp)令牌不适用。
- **达人权限**：达人须具备相应电商（EC）/选品区域权限，否则返回 16015006 / 16015007 / 16504002 等。
- **限流**：短时间内请求过多会触发 36009002，请退避重试。

## User Expression & Scenario Quick Reference

**Applicable**：

| User Says | Scenario |
|-----------|----------|
| "查一下这个 TikTok 达人的资料" / "Get TikTok creator profile" | 获取达人主页/档案 |
| "搜一下达人店铺里的商品" / "Get shop products of the creator" | 搜索达人绑定店铺的商品 |
| "看看达人橱窗里有哪些商品" / "Get creator showcase products" | 达人橱窗商品列表 |
| "上传一个可购物视频" / "Upload shoppable video" | 上传可购物视频文件 |
| "发布可购物视频 / 把视频和商品绑定发出去" / "Post shoppable video" | 发布可购物视频 |
| "视频发布成功了吗 / 查下视频发布状态" / "Get shoppable video status" | 查询可购物视频发布状态 |
| "发布前先检测下视频有没有违规" / "Pre-check shoppable video" | 可购物视频内容预检 |
| "预检结果出来了吗 / 视频违规检测结果" / "Get video pre-check result" | 查询视频预检结果 |
| "看看达人的带货信息" | 达人数据查询（按已收录接口） |

**Not applicable**：
- TikTok 达人授权本身 → 用 `linkfox-tiktok-auth`（`appType=creator`）。
- TikTok 选品 / 商品销量（EchoTik 等数据源）→ 由对应 skill 负责。

**Feedback**：

当出现以下任一情况时，自动通过 Feedback API 上报反馈：
1. 本 skill 描述的功能与实际行为不符
2. skill 的结果与用户意图不符
3. 用户表达了对本 skill 的不满或赞赏
4. 任何你认为可以改进的点

按 `references/api.md` 中的规范调用 Feedback API，不要打断用户的主流程。

<!-- LF_LARGE_RESPONSE_BLOCK -->
## Handling Large Responses

To avoid overflowing the agent context, persist the response to disk and extract only the fields you need:

```
python scripts/response_io.py run --script scripts/creator_proxy.py --out-dir <DIR> '<params>'
python scripts/response_io.py read <file> --fields "<paths>"   # or --path "<JMESPath>"
```

> Pick `--out-dir` outside any git working tree (e.g. `/tmp/...` on Unix, `%TEMP%/...` on Windows). Persisted responses may contain PII, pricing, or auth-sensitive data — do not commit them. Files are not auto-deleted; clean up when the task is done.

`run` writes the full response to a file and emits only a schema preview + file path. `read` projects specific fields, with `--limit/--offset` for slicing and `--format json|jsonl|csv|table` for output.

**When to prefer this pattern** — apply your judgment based on the response characteristics, e.g.:
- High field count per record, or fields you don't need
- Batch/paginated results (multiple items per call)
- Long-text fields (descriptions, reviews, HTML, time series)
- Output reused across later steps rather than consumed immediately

For small, single-use responses, calling the main script directly is fine.

⚠️ The preview is a truncated schema + sample, not the full data. Any field-level decision must read from the persisted file via `read`.
<!-- /LF_LARGE_RESPONSE_BLOCK -->

---
*For more high-quality, professional cross-border e-commerce skills, visit [LinkFox Skills](https://skill.linkfox.com/).*
