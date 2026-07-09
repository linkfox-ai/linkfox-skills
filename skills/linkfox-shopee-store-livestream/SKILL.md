---
name: linkfox-shopee-store-livestream
description: Shopee（虾皮）直播 Livestream（与 linkfox-shopee-store-auth 同系列），经 /shopee/developerProxy 转发 Shopee Open API Livestream 模块全部 25 个接口：create_session、start_session、add_item_list、get_session_detail、get_session_metric、post_comment、upload_image 等。当用户提到 Shopee 直播、Livestream、创建直播场次、直播商品、直播评论、session_id、upload_image 时触发。即使未明确提及"直播"，只要涉及已授权 Shopee 店铺的 Livestream 场次/商品/互动管理，也应触发。
---

# Shopee 直播 Livestream

Shopee Open Platform **Livestream 模块**（25 个 API）。**依赖 `linkfox-shopee-store-auth`**：先取 `accessToken`，再经 **`POST /shopee/developerProxy`** 转发（`path` 须 `api/v2/livestream/...`）。

## 调用方式

- **API 端点**：`POST /shopee/developerProxy`（不同操作通过请求体区分；完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/livestream_api.py '<JSON 参数>' [--inline]`（可用脚本见上文脚本一览）
- **成本约束**：本工具会消耗积分；失败/空结果不得自动换关键词、翻页或连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/<skill-name>-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
- 响应体 ≤ 8 KB：落盘后把完整 JSON 打印到 stdout
- 响应体 > 8 KB：落盘后 stdout 只输出摘要（顶层字段、常见计数如 `total`/`costToken`、最大列表字段的长度 + 前 3 条样本）
- 加 `--inline` 强制全量打印到 stdout（同样落盘）

**读数据建议**：先看摘要判断是否足够；需要具体字段时优先用 `jq`或`ConvertFrom-Json` 从保存的 json 文件按需抽取，避免整份 JSON 进入上下文。

## 官方参考

Livestream 模块索引：[v2.livestream.upload_image](https://open.shopee.com/documents/v2/v2.livestream.upload_image?module=125&type=1)

---

## Prerequisites

1. 运行 `python scripts/check_auth_dependency.py`；exit code **42** → 先安装 **`linkfox-shopee-store-auth`**。
2. 店铺短视频 Video → `linkfox-shopee-store-video`；图片上传 Media → `linkfox-shopee-store-media`。

## 可用脚本（25 个 API）

| 脚本 | API | Method |
|------|-----|--------|
| `upload_image.py` | upload_image | POST |
| `create_session.py` | create_session | POST |
| `update_session.py` | update_session | POST |
| `start_session.py` | start_session | POST |
| `end_session.py` | end_session | POST |
| `get_session_detail.py` | get_session_detail | GET |
| `add_item_list.py` | add_item_list | POST |
| `delete_item_list.py` | delete_item_list | POST |
| `update_item_list.py` | update_item_list | POST |
| `get_item_count.py` | get_item_count | GET |
| `get_item_list.py` | get_item_list | GET |
| `update_show_item.py` | update_show_item | POST |
| `delete_show_item.py` | delete_show_item | POST |
| `get_show_item.py` | get_show_item | GET |
| `get_like_item_list.py` | get_like_item_list | GET |
| `get_recent_item_list.py` | get_recent_item_list | GET |
| `get_item_set_list.py` | get_item_set_list | GET |
| `get_item_set_item_list.py` | get_item_set_item_list | GET |
| `apply_item_set.py` | apply_item_set | POST |
| `get_session_metric.py` | get_session_metric | GET |
| `get_session_item_metric.py` | get_session_item_metric | GET |
| `get_latest_comment_list.py` | get_latest_comment_list | GET |
| `post_comment.py` | post_comment | POST |
| `ban_user_comment.py` | ban_user_comment | POST |
| `unban_user_comment.py` | unban_user_comment | POST |
| `livestream_api.py` | 通用入口 | — |

## Usage Scenarios

### 1. 创建并开播
1. `upload_image.py` 上传封面/素材
2. `create_session.py` 创建场次
3. `add_item_list.py` 添加商品
4. `start_session.py` 开始直播

### 2. 直播中管理
1. `update_show_item.py` 切换展示商品
2. `get_latest_comment_list.py` / `post_comment.py` 评论互动
3. `get_session_metric.py` 查看数据

## Not Applicable

- 店铺授权 → `linkfox-shopee-store-auth`
- 店铺短视频 Video → `linkfox-shopee-store-video`
- 通用图片/视频上传 Media / MediaSpace → 对应 media skill
- 商品 listing → `linkfox-shopee-store-product`

**Feedback:** 见 `references/api.md`。

---
*For more high-quality, professional cross-border e-commerce skills, visit [LinkFox Skills](https://skill.linkfox.com/).*
