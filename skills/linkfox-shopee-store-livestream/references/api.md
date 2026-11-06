# Shopee 店铺直播接口说明

25 个直播操作经同一个转发端点提供，另提供兼容 `storeTokens` 操作。各文档独立列出已知封装字段；具体 Shopee 业务字段及嵌套 schema 以各接口官方定义和实际响应为准，不把未知字段补造为固定契约。

| 操作 | 接口文档 |
|---|---|
| `upload_image` | [上传直播图片](./apis/upload-image.md) |
| `create_session` | [创建直播场次](./apis/create-session.md) |
| `update_session` | [更新直播场次](./apis/update-session.md) |
| `start_session` | [开始直播](./apis/start-session.md) |
| `end_session` | [结束直播](./apis/end-session.md) |
| `get_session_detail` | [获取场次详情](./apis/get-session-detail.md) |
| `add_item_list` | [添加直播商品](./apis/add-item-list.md) |
| `delete_item_list` | [删除直播商品](./apis/delete-item-list.md) |
| `update_item_list` | [更新直播商品列表](./apis/update-item-list.md) |
| `get_item_count` | [获取商品数量](./apis/get-item-count.md) |
| `get_item_list` | [获取商品列表](./apis/get-item-list.md) |
| `update_show_item` | [更新展示商品](./apis/update-show-item.md) |
| `delete_show_item` | [删除展示商品](./apis/delete-show-item.md) |
| `get_show_item` | [获取展示商品](./apis/get-show-item.md) |
| `get_like_item_list` | [获取点赞商品列表](./apis/get-like-item-list.md) |
| `get_recent_item_list` | [获取最近展示商品](./apis/get-recent-item-list.md) |
| `get_item_set_list` | [获取商品集列表](./apis/get-item-set-list.md) |
| `get_item_set_item_list` | [获取商品集商品列表](./apis/get-item-set-item-list.md) |
| `apply_item_set` | [应用商品集](./apis/apply-item-set.md) |
| `get_session_metric` | [获取场次指标](./apis/get-session-metric.md) |
| `get_session_item_metric` | [获取场次商品指标](./apis/get-session-item-metric.md) |
| `get_latest_comment_list` | [获取最新评论](./apis/get-latest-comment-list.md) |
| `post_comment` | [发表评论](./apis/post-comment.md) |
| `ban_user_comment` | [禁言用户](./apis/ban-user-comment.md) |
| `unban_user_comment` | [解除用户禁言](./apis/unban-user-comment.md) |
| `storeTokens` | [兼容令牌查询](./apis/store-tokens.md) |

## 公共规则

### 调用规范

- **请求基础地址**：`LINKFOX_TOOL_GATEWAY` 默认 `https://tool-gateway.linkfox.com`
- **请求方式**：POST, HTTP 超时 150s
- **请求头**
  - Content-Type: application/json
  - User-Agent: LinkFox-Skill/2.0
  - Authorization: <api_key> (<api_key> 从环境变量 `LINKFOX_AGENT_API_KEY` 或 `LINKFOXAGENT_API_KEY` 读取，未配置则按 SKILL.md 的 **## 解决认证和算力问题** 处理)

### 响应码基本规则

- **正常响应**: HTTP 状态码为 `200`–`299`，且响应体的 `errcode` 不存在、为 `null`、为空字符串（含纯空白）或为 `200`–`299`（数字或数字字符串）。
- **未正常响应**: HTTP 状态码不属于 `200`–`299`，或响应体的 `errcode` 为非空且不属于 `200`–`299` 的值；`0` 和 `false` 不视为空。
- **认证或用量错误**: HTTP 状态码为 `401` / `402`，按 onboarding.md 的指引处理
- **其他情况**: 依据响应体的 `errmsg` 判断具体原因

## 脚本运行约定

- 专用入口：`python scripts/<操作名>.py '<JSON 参数>' [--inline] [--no-cache]`；通用入口：`python scripts/livestream_api.py '<含 api 的 JSON 参数>' [--inline] [--no-cache]`。通用入口只接受清单中的 25 个直播操作。
- 所有业务封装调用公共 `call_api.run` 时强制传入 `--no-cache`，不读取或保存响应缓存。公共调用器仍可能创建空 `.cache` 目录，该目录不代表启用了缓存。
- 网关地址优先取 `LINKFOX_TOOL_GATEWAY`，其次取 `SHOPEE_API_BASE_URL`，最后使用默认网关；两个 API Key 环境变量的优先级遵循公共规则。
- 本地依赖检测返回 0 表示找到认证技能；返回 42 且 stderr 含 `DEPENDENCY_MISSING:` 表示缺失。JSON 字段 `skipDepCheck` 默认 false，只有外部流程已确认依赖时才使用；它只跳过本地安装检测，不绕过店铺授权。
- 完整业务响应按 `SESSION_ID` 聚合并保存到当前工作目录的 `linkfox/<日期>/<session>/data/`；请求前准备会话目录，并检查输出根目录和实际 data 目录的可写性，失败时报错，不回退到家目录、`ACPX_WORKSPACES` 或临时目录，不写 `/tmp`。同一秒内重复操作也使用独立文件名。
- 业务脚本使用 `linkfox-shopee-store-livestream-<操作名>` 作为文件标识；完整输出、8 KB 摘要和 `--inline` 由公共调用器处理。兼容函数 `resolve_store_tokens` 只在内存返回原始令牌结果，保存的副本不含令牌正文。
- 直播 CLI 和 Python 封装均按店铺或商户标识调用 developerProxy，由服务端解析令牌；直播 CLI 不调用兼容令牌查询。

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-shopee-store-livestream",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
