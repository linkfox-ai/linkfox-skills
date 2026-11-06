# Shopee 店铺信息与设置 接口说明

共 10 个非 Feedback 操作：9 个 Shop 转发操作及 1 个选店辅助操作。

| 接口 | 接口文档 |
|---|---|
| 获取店铺基本信息（get_shop_info） | [apis/get-shop-info.md](apis/get-shop-info.md) |
| 获取店铺资料（get_profile） | [apis/get-profile.md](apis/get-profile.md) |
| 更新店铺资料（update_profile） | [apis/update-profile.md](apis/update-profile.md) |
| 获取仓库详情（get_warehouse_detail） | [apis/get-warehouse-detail.md](apis/get-warehouse-detail.md) |
| 获取卖家通知（get_shop_notification） | [apis/get-shop-notification.md](apis/get-shop-notification.md) |
| 获取授权经销品牌（get_authorised_reseller_brand） | [apis/get-authorised-reseller-brand.md](apis/get-authorised-reseller-brand.md) |
| 获取巴西店铺入驻信息（get_br_shop_onboarding_info） | [apis/get-br-shop-onboarding-info.md](apis/get-br-shop-onboarding-info.md) |
| 获取假期模式（get_shop_holiday_mode） | [apis/get-shop-holiday-mode.md](apis/get-shop-holiday-mode.md) |
| 设置假期模式（set_shop_holiday_mode） | [apis/set-shop-holiday-mode.md](apis/set-shop-holiday-mode.md) |
| 选店授权状态查询（storeTokens） | [apis/store-tokens.md](apis/store-tokens.md) |

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

## 脚本与运行约定

### CLI

| 入口 | 用法 | 说明 |
|---|---|---|
| 专用业务脚本 | `python scripts/<操作名>.py '<JSON 参数>' [--inline] [--no-cache]` | 操作名与接口清单一致。 |
| 通用入口 | `python scripts/shop_api.py '<JSON 参数>' [--inline] [--no-cache]` | JSON 必须包含 api 字段，值为 9 个 Shop 操作名之一。 |
| 依赖检测 | `python scripts/check_auth_dependency.py [--json]` | 找到依赖返回 0；缺失返回 42，stderr 含 DEPENDENCY_MISSING。 |
| 认证与用量引导 | `python scripts/onboarding.py --help` | 按 [onboarding.md](onboarding.md) 处理，不在业务封装中另实现授权。 |

### 认证与选店

- LINKFOX_AGENT_API_KEY 优先，兼容 LINKFOXAGENT_API_KEY；两者均为空时退出 1。
- 网关优先 LINKFOX_TOOL_GATEWAY，其次兼容 SHOPEE_API_BASE_URL，默认 https://tool-gateway.linkfox.com。
- 依赖检测支持 LINKFOX_SKILLS_DIR、SKILLS_DIR、CURSOR_SKILLS_DIR、HERMES_SKILLS_EXTERNAL_DIRS、OpenClaw 环境变量、项目及用户常见安装目录查找行为。
- 调用链为选店后直接 developerProxy，由服务端注入令牌，经 shopee-proxy 转发；辅助 resolve_store_tokens 仅按需使用，不自动增加一次请求。
- shopId / merchantId 至少一项；skipDepCheck 仅跳过本地依赖安装检测。不得藉此跳过店铺授权或擅自更换店铺。

### 缓存与输出

- 业务脚本不提供响应缓存；业务封装调用共享 call_api.run 时始终传入 --no-cache，不读写响应缓存，也没有第二层缓存。公共脚本可能建立空的 .cache 目录，不代表使用了响应缓存。
- 共享调用器保存一次原始网关响应，业务封装保存一次包含解析结果的完整响应；均位于当前工作目录 linkfox/<日期>/<session>/data/，分别使用 linkfox-shopee-store-shop-transport-<操作标识> 与 linkfox-shopee-store-shop-<操作标识> 文件名前缀。
- 使用 SESSION_ID 聚合并记录会话元数据。每次保存使用微秒时间戳，避免同秒请求覆盖。业务封装强制当前目录落盘；目录不可写时在请求前报错，不回退到用户目录或临时目录。
- 完整结果不超过 8000 UTF-8 字节时全量打印，否则输出顶层字段、计数、最大列表长度和前 3 条；--inline 强制全量打印且仍保存。
- 本技能不消耗算力 （限时）；失败或空结果不自动修改条件、翻页或连续试探，后续调用遵守 SKILL.md 的成本约束。

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-shopee-store-shop",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
