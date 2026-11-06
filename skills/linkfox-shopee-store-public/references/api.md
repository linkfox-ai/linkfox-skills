# Shopee Public 公共模块 接口说明

本技能提供六个 Public 转发操作和一个店铺授权状态辅助调用（不返回原始 token），共七个实际操作（不含 Feedback 和公共 onboarding）。各操作独立文档如下。

| 操作 | 文档 |
|---|---|
| `get_shops_by_partner` | [查询 Partner 下已授权店铺](apis/get-shops-by-partner.md) |
| `get_merchants_by_partner` | [查询 Partner 下已授权商户](apis/get-merchants-by-partner.md) |
| `get_access_token` | [使用授权码交换 token](apis/get-access-token.md) |
| `refresh_access_token` | [刷新 access token](apis/refresh-access-token.md) |
| `get_token_by_resend_code` | [使用 resend code 获取 token](apis/get-token-by-resend-code.md) |
| `get_shopee_ip_ranges` | [查询 Shopee 开放平台 IP 段](apis/get-shopee-ip-ranges.md) |
| `/shopee/storeTokens` | [兼容辅助调用](apis/store-tokens.md) |

日常授权优先使用 `linkfox-shopee-store-auth`。上游官方文档路径为 `https://open.shopee.com/documents/v2/v2.public.{api}?module=104&type=1`。

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

- **运行环境与依赖**：Python 3.10 或以上。依赖检查返回 0 表示找到 `linkfox-shopee-store-auth`；返回 42 且 stderr 含 `DEPENDENCY_MISSING:` 表示缺失，先安装依赖。`skipDepCheck` 只跳过安装检测，不绕过网关授权。
- **依赖探测路径**：支持 `LINKFOX_SKILLS_DIR`、`SKILLS_DIR`、`CURSOR_SKILLS_DIR`、`HERMES_SKILLS_EXTERNAL_DIRS`、`OPENCLAW_WORKSPACE`、`OPENCLAW_ROOT`、`OPENCLAW_WORKDIR`、`OPENCLAW_SKILLS_DIR`，以及当前目录、技能同级目录和用户安装目录的探测规则；详见 `scripts/check_auth_dependency.py`（路径以技能目录为基准）。
- **网关与认证兼容**：网关优先使用 `LINKFOX_TOOL_GATEWAY`，其次 `SHOPEE_API_BASE_URL`，缺省 `https://tool-gateway.linkfox.com`。密钥读取 `LINKFOX_AGENT_API_KEY` 或 `LINKFOXAGENT_API_KEY`；发送 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 请求头。
- **无响应缓存**：业务封装调用 `call_api.run` 始终传 `--no-cache`，不会读取或保存响应缓存；运行时可能创建空缓存目录。
- **落盘与错误处理**：完整结果保存到当前工作目录的 `linkfox/`；请求前预检实际会话数据目录的可写性。不能回退到主目录或临时目录，也禁止写入 `/tmp`。同一请求只保存一次加工后的完整结果，保存失败时报错；不因保存失败自动重发请求。`--inline` 仅控制输出是否完整打印，仍须保存文件。

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-shopee-store-public",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
