# Shopee 店铺账户健康 接口说明

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

## 运行约定

账户健康六个操作经 `POST /shopee/developerProxy` 转发上游 GET。业务接口独立定义于 `apis/`，每份文档包含完整网关字段、业务参数、响应结构和一个 curl 示例。

| 操作 | 接口文档 | 专用入口 |
|---|---|---|
| get_shop_performance | [apis/get-shop-performance.md](apis/get-shop-performance.md) | `scripts/get_shop_performance.py` |
| get_metric_source_detail | [apis/get-metric-source-detail.md](apis/get-metric-source-detail.md) | `scripts/get_metric_source_detail.py` |
| get_penalty_point_history | [apis/get-penalty-point-history.md](apis/get-penalty-point-history.md) | `scripts/get_penalty_point_history.py` |
| get_punishment_history | [apis/get-punishment-history.md](apis/get-punishment-history.md) | `scripts/get_punishment_history.py` |
| get_listings_with_issues | [apis/get-listings-with-issues.md](apis/get-listings-with-issues.md) | `scripts/get_listings_with_issues.py` |
| get_late_orders | [apis/get-late-orders.md](apis/get-late-orders.md) | `scripts/get_late_orders.py` |

| 项目 | 约定 |
|---|---|
| 通用 CLI | `python scripts/account_health_api.py '<JSON 参数>' [--inline] [--no-cache]`；JSON 必须包含 api，限上述六个操作。 |
| 专用 CLI | `python scripts/<操作名>.py '<JSON 参数>' [--inline] [--no-cache]`。 |
| 认证 | `LINKFOX_AGENT_API_KEY` 优先，其次 `LINKFOXAGENT_API_KEY`；缺失时按 onboarding.md 处理。 |
| 网关兼容 | `LINKFOX_TOOL_GATEWAY` 优先，其次兼容变量 `SHOPEE_API_BASE_URL`，默认 `https://tool-gateway.linkfox.com`。 |
| 上下文请求头 | 公共调用器保留 SESSION_ID、MESSAGE_ID、MODE_ID、APP_NAME 环境变量对应请求头。 |
| 店铺保护 | 至少提供 shopId 或 merchantId，推荐 shopId；不得自动更换店铺，兼容同时传入两者。主流程由服务端解析令牌，不自动额外调用 storeTokens。 |
| 依赖检测 | `python scripts/check_auth_dependency.py [--json]`；找到授权技能返回 0，缺失返回 42，stderr 含 `DEPENDENCY_MISSING:`；返回 searchedRoots 供定位。 |
| 依赖搜索 | 保留 LINKFOX_SKILLS_DIR、SKILLS_DIR、CURSOR_SKILLS_DIR、HERMES_SKILLS_EXTERNAL_DIRS、OPENCLAW_WORKSPACE / ROOT / WORKDIR / SKILLS_DIR，以及当前目录、相邻技能目录和用户常见安装目录。 |
| skipDepCheck | 默认 false；已由外部流程确认依赖时可跳过安装检测，不能绕过授权。 |
| 缓存 | 业务封装始终使用 --no-cache，无第二层响应缓存。公共调用器可能建立空 .cache 目录，但不读取或写入缓存文件。 |
| 输出 | 每次保存完整加工结果至当前目录 linkfox 日期 / 会话 / data，含原始代理响应与解析字段；8 KB 以内全量输出，超过则摘要，包含嵌套网关错误码、消息和上游状态，--inline 强制全量。 |
| 输出保护 | 请求前检查当前目录及最终会话 data 目录可写，失败则报错，不发送请求、不回退至临时目录；环境 ACPX_WORKSPACES 不改变业务输出目标。每次文件使用微秒时间标识，避免同秒调用覆盖。 |
| 调用成本 | 不消耗算力 （限时）；按 SKILL.md 的成本约束避免自动重试、换条件或连续翻页。 |

官方链接规则：`https://open.shopee.com/documents/v2/v2.account_health.{api}?module=103&type=1`。

## 接口：店铺授权状态兼容查询（storeTokens）

共享函数 `resolve_store_tokens(params)` 支持查询店铺授权状态，返回完整响应对象；接口不返回原始令牌。该兼容函数不属于账户健康上游六个操作，不添加至通用 CLI 的 api 枚举；正常账户健康流程使用代理解析已授权令牌，不主动调用本接口或另行实现令牌刷新。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/shopee/storeTokens`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| shopId | string | 与 merchantId 至少一个 | 店铺 ID，推荐使用；兼容函数将非空值转字符串。 |
| merchantId | string | 与 shopId 至少一个 | 商户 ID；同时提供两者时均保留。 |
| appType | string | 否 | 网关可选应用类型：`erp` / `ad`，默认 `erp`。 |

共享函数只提取 `shopId` / `merchantId`，使用网关默认的 `erp`，不转发 `appType` 或其他参数；缺少两个标识时在本地退出，不发请求。直接调用网关可按需传 `appType`。环境变量、认证、落盘与无缓存行为沿用上方运行约定。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 网关业务状态码；若存在则按公共基本规则判断。 |
| errmsg | string | 网关消息；若存在则用于解释原因。 |
| authRecordId | Long | 授权记录 ID。 |
| shopId | string | 店铺 ID。 |
| merchantId | string | 商户 ID。 |
| shopIdList | string | 店铺 ID 列表的 JSON 字符串。 |
| merchantIdList | string | 商户 ID 列表的 JSON 字符串。 |
| appType | string | 应用类型：`erp` / `ad`。 |
| expireIn | Long | access_token 有效期，单位秒。 |
| status | string | 授权状态：`ACTIVE` / `EXPIRED`。 |
| message | string | 状态说明。 |

#### 本地附加字段

共享函数始终追加 `transportHttpStatus`，非对象返回值保存在 `responseBody`。公共调用器在 HTTP 错误正文为空、无法解析为 JSON 或连接失败时，可能构造 `error` / `details`；HTTP 错误若带有有效 JSON，则保留该 JSON。这些本地字段不是网关成功响应的固定字段。

| 字段 | 类型 | 说明 |
|---|---|---|
| error | string | 本地构造的 HTTP 错误或连接失败说明。 |
| details | string | HTTP 错误正文无法解析为 JSON 时保留的原始正文；并非必返。 |
| transportHttpStatus | integer / null | 共享函数追加的 LinkFox 外层 HTTP 状态；连接失败为 null，不属于网关响应字段。 |
| responseBody | JSON 值 | 仅当完整返回值不是对象时，由共享函数保存该值；对象响应的原有字段保留在顶层。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

共享函数保留完整错误响应与实际 `transportHttpStatus`，结合外层 HTTP 状态、业务码与消息判断；直接调用网关则检查实际 HTTP 状态。该调用不替代授权技能的选店与授权流程。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/shopee/storeTokens" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"shopId":"67890"}'
```

---

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-shopee-store-account-health",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
