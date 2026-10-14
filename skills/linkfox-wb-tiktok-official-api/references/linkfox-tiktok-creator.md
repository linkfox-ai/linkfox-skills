---
name: linkfox-tiktok-creator
description: TikTok 达人（Creator/affiliate creator）数据与可购物视频接口契约，覆盖达人主页/档案、达人绑定店铺商品、橱窗商品、可购物视频的上传/内容预检/发布/发布状态查询。当前 LinkFox MCP 尚无已确认的达人授权上下文自动映射，所有达人 operation 暂不可执行；不得读取、保存或转发任何凭证。当用户提到 TikTok 达人、TikTok creator、达人主页、达人档案、达人资料、达人店铺商品、达人绑定店铺商品、达人橱窗商品、showcase 商品、上传可购物视频、发布可购物视频、视频发布状态、视频内容预检、shoppable video、affiliate creator、TikTok 带货达人信息、TikTok creator profile、shop products、showcase products、post shoppable video、video status、precheck 时触发此技能并说明阻塞。
---

## MCP 调用

| 项 | 固定值 |
|---|---|
| MCP server | `LinkFox` |
| 唯一工具 | `proxy_call` |
| `toolName` | `tiktokShop/developerProxy` |
| `arguments` | 直接使用本 reference 的请求对象；不得额外包裹 `body`、`data` 或另一层 `arguments` |
| 响应字段来源 | `skills/linkfox-tiktok-creator/SKILL.md`；只按其响应契约核对字段表 |

- `toolName` 精确匹配且区分大小写；MCP 缺失时停止，禁止 HTTP fallback。
- WorkBuddy 自动注入 MCP Authorization；不得传 LinkFox `headers`、API Key、`token`、JWT 或手机号。
- 收费失败、空结果或结果不理想时不自动重试；相同 `toolName + arguments` 在同一任务内不重复调用。
- 先处理 MCP/schema/`isError`；text JSON 只解析一次；再检查下游错误字段和业务结果。
- **后端契约阻塞**：来源契约要求调用方提供独立的上游达人凭证，仓库中没有证据证明 MCP 会从 WorkBuddy 授权上下文自动映射该凭证，也没有定义可替代凭证的达人账号标识。`openId` 是 ERP 店铺标识，不能臆造成达人参数。映射能力确认前不得调用本 reference 的 8 个 operation。

# TikTok 达人（Creator）数据

本 reference 归档 **LinkFox 网关 → 紫鸟代理 → TikTok Shop 达人(affiliate_creator)开放接口** 的数据查询（达人资料、绑定店铺商品、橱窗商品）与可购物视频操作（上传、内容预检、发布、状态查询）契约。全部接口收录在 `linkfox-tiktok-creator--api.md`；当前仅供识别需求和参数，不表示可执行。

> **当前状态**：达人 operation 仅保留业务契约。WorkBuddy 自动注入 MCP Authorization，但现有后端来源契约仍要求另一项上游达人凭证；在网关完成自动映射前停止调用，不从任何授权接口读取凭证，也不在本地保存或转发凭证。

## Core Concepts

- **调用链路契约**：业务路由使用 LinkFox 网关的 **`tiktokShop/developerProxy`**，非凭证字段包括 **`appType=creator`**、TikTok Shop API 相对 `path`（如 `affiliate_creator/202508/profiles`）、`method`、可选 `queryString`、`contentType` 和 `body`；紫鸟代理负责 `app_key` / `timestamp` / `sign`。当前仅作接口归档，不得据此发起达人调用。
- **账号选择**：来源契约未定义可用于选择达人账号的非凭证请求字段。不得使用 ERP `openId` 替代，也不得要求用户提供任何凭证。
- **响应透传**：网关返回 `httpStatus` / `contentType` / `body`，其中 `body` 为 TikTok 原始 JSON 字符串；TikTok 业务层的成功/失败以其 `code` / `message` 为准。

## 调用方式

- **API 端点**：`POST tiktokShop/developerProxy`（完整参数/响应/错误码见 `linkfox-tiktok-creator--api.md`）
> 旧脚本调用已移除；使用本页 `MCP 调用`。
- **成本约束**：本工具会消耗积分；同一任务内相同 `toolName + arguments` 只调用一次。失败/空结果不得自动换关键词、翻页或改邮编连续试探；需要继续检索时先向用户说明会产生额外消耗。新 MCP 链路不提供旧脚本的本地缓存。

**输出策略**：新 MCP 链路不承诺旧脚本的响应落盘或 stdout 摘要。解析 `proxy_call` 返回后，按当前任务仅展示必要字段，并保留非敏感的调用摘要和状态用于追溯。

### Available Scripts

- `proxy_call` — endpoint 与非凭证业务参数契约已归档；授权映射阻塞解除前不得调用。

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

> ⚠️ 含 `multipart/form-data` 二进制上传的接口（Upload Shoppable Video File）不走通用 `proxy_call`，需 multipart 链路，详见 `linkfox-tiktok-creator--api.md`。

## 解决认证和积分问题
发生以下异常情况时，采用 references/onboarding.md 引导解决问题：

### 异常情况
- MCP 或 `proxy_call` 缺失时停止调用，按 `references/onboarding.md` 配置并重载连接。
- MCP 连接 401 按 WorkBuddy 自动授权链路异常处理；不得要求用户手工填写 Authorization。
- 代理成功后的下游 401、402、403 或积分不足，按 `references/onboarding.md` 分层处理。

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

> 当前整个达人链路不可执行。不得从其他 skill 或接口读取凭证后回传；后端必须先提供 WorkBuddy 授权上下文到上游达人授权的自动映射。

## Display Rules

1. **只呈现数据**：展示达人资料字段即可，不做主观评价。
2. **凭证隔离**：不得请求、读取、展示、保存或转发任何达人凭证。
3. **错误说明**：失败时依据 TikTok 业务 `code` / `message` 与网关 `httpStatus` 解释原因。
4. **前置校验**：授权映射能力未确认时直接说明后端契约阻塞，不引导用户手工提供凭证。

## Important Limitations

- **授权映射阻塞**：来源后端契约硬性要求独立的上游达人凭证，而 LinkFox MCP 自动映射能力未得到确认；全部 operation 暂不可调用。
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
- TikTok 达人授权或凭证管理本身不在本 reference 范围；不得通过其他 skill 取出凭证再传给本接口。
- TikTok 选品 / 商品销量（EchoTik 等数据源）→ 由对应 skill 负责。

## 积分消耗规则

不消耗积分。

**Feedback**：

当出现以下任一情况时，自动通过 Feedback API 上报反馈：
1. 本 skill 描述的功能与实际行为不符
2. skill 的结果与用户意图不符
3. 用户表达了对本 skill 的不满或赞赏
4. 任何你认为可以改进的点

按 `linkfox-tiktok-creator--api.md` 中的规范调用 Feedback API，不要打断用户的主流程。



---
*For more high-quality, professional cross-border e-commerce skills, visit [LinkFox Skills](https://skill.linkfox.com/).*
