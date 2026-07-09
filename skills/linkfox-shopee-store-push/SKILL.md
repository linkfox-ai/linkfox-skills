---
name: linkfox-shopee-store-push
description: Shopee（虾皮）Push 推送机制（与 linkfox-shopee-store-auth 同系列），经 /shopee/developerProxy 转发 Shopee Open API Push 模块全部 4 个接口：set_app_push_config、get_app_push_config、get_lost_push_message、confirm_consumed_lost_push_message。当用户提到 Shopee Push、推送回调、Push Mechanism、set_app_push_config、丢失推送补推、webhook 配置 时触发。即使未明确提及"Push"，只要涉及 Shopee 开放平台 Push 配置或补推消息管理，也应触发。
---

# Shopee Push 推送机制

Shopee Open Platform **Push 模块**（4 个 API）。**依赖 `linkfox-shopee-store-auth`** 作为同系列前置；经 **`POST /shopee/developerProxy`** 转发（`path` 须 `api/v2/push/...`）。

## 调用方式

- **API 端点**：`POST /shopee/developerProxy`（不同操作通过请求体区分；完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/<脚本名>.py '<JSON 参数>' [--inline]`（可用脚本见上文脚本一览）
- **成本约束**：本工具会消耗积分；失败/空结果不得自动换关键词、翻页或连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/<skill-name>-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
- 响应体 ≤ 8 KB：落盘后把完整 JSON 打印到 stdout
- 响应体 > 8 KB：落盘后 stdout 只输出摘要（顶层字段、常见计数如 `total`/`costToken`、最大列表字段的长度 + 前 3 条样本）
- 加 `--inline` 强制全量打印到 stdout（同样落盘）

**读数据建议**：先看摘要判断是否足够；需要具体字段时优先用 `jq`或`ConvertFrom-Json` 从保存的 json 文件按需抽取，避免整份 JSON 进入上下文。

## 官方参考

Push 模块索引：[v2.push.set_app_push_config](https://open.shopee.com/documents/v2/v2.push.set_app_push_config?module=105&type=1)

---

## Prerequisites

1. 运行 `python scripts/check_auth_dependency.py`；exit code **42** → 先安装 **`linkfox-shopee-store-auth`**。
2. OAuth / Partner 公共接口 → `linkfox-shopee-store-public`。

## 可用脚本（4 个 API）

| 脚本 | API | Method |
|------|-----|--------|
| `set_app_push_config.py` | set_app_push_config | POST |
| `get_app_push_config.py` | get_app_push_config | GET |
| `get_lost_push_message.py` | get_lost_push_message | GET |
| `confirm_consumed_lost_push_message.py` | confirm_consumed_lost_push_message | POST |
| `push_api.py` | 通用入口 | — |

## Usage Scenarios

### 1. 配置 Push 回调
1. `set_app_push_config.py` 传完整 POST `body`（回调 URL 等）
2. `get_app_push_config.py` 确认配置

### 2. 补推丢失消息
1. `get_lost_push_message.py` 拉取丢失消息
2. `confirm_consumed_lost_push_message.py` 确认已消费

## Not Applicable

- 用户侧授权流程 → `linkfox-shopee-store-auth`
- Public OAuth / Partner 查询 → `linkfox-shopee-store-public`
- 订单/商品等业务 API → 对应业务 skill

**Feedback:** 见 `references/api.md`。


---
*For more high-quality, professional cross-border e-commerce skills, visit [LinkFox Skills](https://skill.linkfox.com/).*
