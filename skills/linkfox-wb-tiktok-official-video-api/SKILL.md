---
name: linkfox-wb-tiktok-official-video-api
display_name: LinkFox TikTok带货视频
display_name_en: LinkFox TikTok Shoppable Video
description: 面向 TikTok 达人视频号的授权、商品挂车、视频文件准备、内容预检、发布与状态查询能力。
description_zh: 面向 TikTok 达人视频号的带货视频全链路能力：生成授权链接、管理已授权账号与令牌，查询店铺/橱窗/直播袋商品，获取达人档案，准备视频文件，执行可购物视频预检、发布和状态查询。当用户需要 TikTok 视频号带货、挂车、视频上传发布或账号授权时触发；仅支持 /tiktokVideo 体系，不适用于 TikTok Shop ERP 小店业务。完整参数见 references/。
description_en: End-to-end TikTok creator shoppable-video operations for account authorization, product lookup, file preparation, pre-check, publishing, and status tracking. This capability is scoped to the /tiktokVideo creator module, not TikTok Shop ERP operations.
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


# LinkFox TikTok带货视频

通过 WorkBuddy 的 Linkfox LinkFox MCP 完成达人授权、商品准备、内容预检、发布和状态查询。视频二进制仅可在取得文件网关 `upload_url` 后由本地 helper 上传。

## MCP 契约

- MCP server：`LinkFox`
- URL：`https://mcp-tool-gateway.linkfox.com/mcp/any-tool`
- 唯一工具：`proxy_call`
- 调用结构：`{"toolName":"<精确 endpoint>","arguments":{...}}`
- allowlist（区分大小写）：`tiktokVideo/authorizeUrl`、`tiktokVideo/authorizedAccounts`、`tiktokVideo/accountTokens`、`tiktokVideo/refreshToken`、`tiktokVideo/developerProxy`。
- WorkBuddy 自动注入 Authorization。配置和 `arguments` 均不得加入 headers、API Key、token、JWT、手机号或其他凭证。
- 禁止用 curl、`urllib`、`requests`、`httpx` 等直连工具网关；MCP 缺失时停止，不得 HTTP fallback。

共享代理调用将 `openId`、`path`、`method`、`region`、`queryString`、`contentType`、`body` 作为原下游业务参数直接放入 `arguments`。不要加入 `ttsAccessToken`；由 WorkBuddy 授权上下文与已绑定的 `openId` 处理认证。若现网 `tiktokVideo/developerProxy` 仍强制要求显式 `ttsAccessToken`，则该业务调用受阻，必须停止并联系 WorkBuddy/LinkFox 管理员，不能读取后再转传令牌。

## 能力边界

- 仅处理 `/tiktokVideo/*` creator 模块；TikTok Shop ERP 商品、订单和卖家授权不在范围。
- 先授权并从账号列表选择 `openId`，再查询档案、商品、预检、发布或状态。
- 不展示 `accessToken`、`refreshToken`；即使查询/刷新响应含这些来源字段，也只报告已掩码值或过期时间。
- `developerProxy` 仅允许 `affiliate_creator`、`video`、`creator` 相对路径；拒绝绝对 URL、`..` 和重复斜杠。
- 小文件 `multipart/form-data` 直传当前不能经 MCP JSON 代理完成。
- 大文件初始化/绑定的 `open/202505/file/*` 当前不在代理白名单；只有拿到可信 `upload_url` 后，本地 `large_file_upload.py` 才能顺序 PUT 分片。
- 发布和预检是写操作。调用前确认 `openId`、`file_id`、`product_id` 和正文；失败后不得自动换参数、重新预检或重新发布。
- 状态为 `PROCESSING` 时报告当前结果；后续相同状态查询仅在用户明确要求时执行，不作为失败重试。

## 路由

| 能力 | reference | `toolName` | 风险 |
|---|---|---|---|
| 生成授权 URL | `references/linkfox-tiktok-video-auth-api.md` | `tiktokVideo/authorizeUrl` | 授权写入 |
| 列出授权账号 | `references/linkfox-tiktok-video-auth-api.md` | `tiktokVideo/authorizedAccounts` | 只读 |
| 查询账号令牌状态 | `references/linkfox-tiktok-video-auth-api.md` | `tiktokVideo/accountTokens` | 敏感只读 |
| 刷新令牌 | `references/linkfox-tiktok-video-auth-api.md` | `tiktokVideo/refreshToken` | 授权写入 |
| 达人档案、店铺商品、橱窗商品 | `references/linkfox-tiktok-video-api.md` | `tiktokVideo/developerProxy` | 只读 |
| 预检、发布、预检/发布状态 | `references/linkfox-tiktok-video-api.md` | `tiktokVideo/developerProxy` | 写入/异步只读 |
| 商品专用说明 | `references/linkfox-tiktok-video-products-api.md` | `tiktokVideo/developerProxy` | 只读 |
| 大文件三步流程 | `references/linkfox-tiktok-video-large-file-upload.md` | `tiktokVideo/developerProxy`（Step 1/3 当前阻塞）；Step 2 非 MCP | 本地文件上传 |

## 标准流程

1. `authorizeUrl` 生成链接；用户在浏览器完成授权。
2. `authorizedAccounts` 选择 `openId`。仅在排错或查看过期时间时调用 `accountTokens`；不要把其令牌放进后续参数。
3. 用共享代理查询商品，取得 `product_id`；首次不传 `page_token`，只有用户要求下一页时才使用返回游标。
4. 使用已有 `file_id`，或在文件初始化/绑定能力已获后端放行后执行上传流程。
5. 用户确认后提交预检，保存 `task_id`；按明确请求查询预检状态。
6. 预检通过且用户确认后发布，保存 `video.id`；按明确请求查询发布状态。

## 调用与响应规则

- 每项业务的完整 `arguments`、响应表、枚举和错误码见对应 reference。
- 同一任务内相同 `toolName + arguments` 不重复调用。收费调用失败、空结果或结果不理想时不自动重试。
- 先检查 MCP 工具/schema/`isError`；代理成功后读 text 或 structured content。text 为 JSON 字符串时只解析一次。
- 再检查代理 `httpStatus`，以及下游 `errcode`、`code`、`message`/`msg`；不得把 MCP 外层对象当下游响应。
- 新链路不提供旧脚本的 24 小时缓存、自动落盘或 stdout 摘要。保留 `request_id`、调用参数摘要和关键业务 ID 以便追溯，但不记录敏感令牌。

## 展示

- 账号突出 `openId` 和 region；商品突出 `product_id`；预检突出 `task_id`、result、issues；发布突出 `video.id`、quota、post_status。
- `PROCESSING` 表示仍在处理；`FAIL` 原样展示风险或错误信息，不擅自重传。
- 列表展示查询条件、分页游标和关键条目，不生成接口未返回的选品或合规结论。
- 认证、积分和 MCP 故障按 `references/onboarding.md` 分层处理。

## 积分消耗

每次 `proxy_call` 可能消耗积分。分页、状态查询、重新预检和重新发布都是新调用；高频调用前说明预计次数并由用户决定。
