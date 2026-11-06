# Shopee SBS 仓储服务 接口说明

SBS 业务接口按操作拆分，全部通过 `POST /shopee/developerProxy` 转发；另提供共享模块中的授权状态辅助查询。账户引导公共资源不计入业务接口清单。

| 操作 | 接口文档 | 上游方法与 path |
|---|---|---|
| 绑定仓库（`get_bound_whs_info`） | [apis/get-bound-whs-info.md](apis/get-bound-whs-info.md) | GET `api/v2/sbs/get_bound_whs_info` |
| 当前库存（`get_current_inventory`） | [apis/get-current-inventory.md](apis/get-current-inventory.md) | GET `api/v2/sbs/get_current_inventory` |
| 效期报表（`get_expiry_report`） | [apis/get-expiry-report.md](apis/get-expiry-report.md) | GET `api/v2/sbs/get_expiry_report` |
| 库龄报表（`get_stock_aging`） | [apis/get-stock-aging.md](apis/get-stock-aging.md) | GET `api/v2/sbs/get_stock_aging` |
| 库存变动（`get_stock_movement`） | [apis/get-stock-movement.md](apis/get-stock-movement.md) | GET `api/v2/sbs/get_stock_movement` |
| 授权状态（`storeTokens`） | [apis/store-tokens.md](apis/store-tokens.md) | POST `/shopee/storeTokens`（非 Shopee 转发 path） |

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

| 项目 | 约定 |
|---|---|
| 专用入口 | `python scripts/<操作名>.py '<JSON 参数>' [--inline] [--no-cache]`。 |
| 通用入口 | `python scripts/sbs_api.py '<含 api 字段的 JSON 参数>' [--inline] [--no-cache]`；`api` 仅可为上表五个 SBS 操作名。 |
| 依赖检查 | `python scripts/check_auth_dependency.py [--json]`；找到依赖返回 0，缺失或检测失败返回 42，stderr 含 `DEPENDENCY_MISSING:`；先安装 `linkfox-shopee-store-auth`。 |
| 依赖目录探测 | 探测 `LINKFOX_SKILLS_DIR`、`SKILLS_DIR`、`CURSOR_SKILLS_DIR`、`HERMES_SKILLS_EXTERNAL_DIRS`、OpenClaw 工作区与 skills 环境变量、当前目录、相邻技能目录及常见用户安装目录。 |
| 认证 | 优先 `LINKFOX_AGENT_API_KEY`，兼容 `LINKFOXAGENT_API_KEY`，缺失时退出 1 并按 [onboarding.md](onboarding.md) 处理。 |
| 网关 | 优先 `LINKFOX_TOOL_GATEWAY`，其次 `SHOPEE_API_BASE_URL`，默认公共网关；配置在模块加载时解析。 |
| 会话头 | 保留 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME`。 |
| 响应缓存 | 脚本不启用响应缓存，业务封装调用公共 `call_api.run` 时始终添加 `--no-cache`；公共调用器可能建立空缓存目录，但不读取或保存响应缓存。 |
| 落盘 | 加工后的完整响应一次保存到 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-shopee-store-sbs-<接口标识>-<timestamp>.json`，保留会话元数据和索引；同秒请求使用细粒度时间戳分别保存。 |
| 目录要求 | 必须使用可写当前工作目录，请求前检查根目录及日期、会话、data 子目录（含会话元数据）；路径冲突或不可写时先报错，不发起请求。禁止回退到 `/tmp`、其他临时目录或用户目录。 |
| 输出 | 不超过 8000 字节完整打印，否则摘要含顶层字段、顶层存在的常见计数、非空最大列表长度及前 3 条；`--inline` 强制全量打印，仍保存完整响应。 |
| 重复调用 | 不自动换店铺、重试、翻页或试探；失败或空结果后继续调用须遵守 SKILL.md 调用约束。 |

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-shopee-store-sbs",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
