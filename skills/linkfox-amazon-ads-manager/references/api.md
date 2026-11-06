# Amazon Ads 广告管理 接口说明

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

### 接口文档与计数

除 Feedback 外，79 个版本化业务 CLI 对应 73 个转发操作（按上游 method + path 模板去重，SB 关键词和定向的 6 个操作各有 V3/V4 入口）。SD 扩展路径和广告/创意类型是同一操作的路径变体，已在各自接口表列出。scripts/sb/*.py 的 12 个兼容薄封装不重复计数。

| 文档 | 操作数 | 内容 |
|---|---|---|
| [SP](apis/sp.md) | 28 | 活动、广告组、关键词、否定、商品、定向和预算规则 |
| [SB V3 Legacy](apis/sb-v3.md) | 4 | Legacy 活动查询/创建/修改及广告组查询 |
| [SB V4 与共享资源](apis/sb-v4.md) | 20 | V4 主资源、关键词/定向共享资源、Creative Version 和预算 |
| [SD](apis/sd.md) | 21 | 活动、广告组、商品、定向、否定、创意和预算 |

### 认证与运行限制

- 外层始终 POST /amazonAds/developerProxy；内层 method、path、body、queryString、contentType、accept 独立透传。不得把网关请求误改为 GET / PUT。
- 网关地址优先 LINKFOX_TOOL_GATEWAY，其次兼容 AMAZON_ADS_BASE_URL，再用正式地址；API key 支持 LINKFOX_AGENT_API_KEY / LINKFOXAGENT_API_KEY。SESSION_ID / MESSAGE_ID / MODE_ID / APP_NAME 保留为请求头。
- 业务调用使用profileId，由服务端选择并管理授权凭证。
- 每个业务脚本接收一个 JSON 位置参数，支持 --inline / --no-cache。响应缓存始终关闭；公共调用器仍可能建空 .cache 目录，但不读写缓存响应；业务脚本不使用公共调用器提供的 24 小时缓存能力。
- 公共调用器保存各页原始响应，业务封装保存聚合结果和错误结果；文件名使用技能标识，--inline 仅控制打印。
- 业务封装在请求前验证当前工作目录的 linkfox 可写；禁止回退用户目录或临时目录；--inline 只控制打印，不关闭落盘。
- 遵守[账号保护](ads-protection.md)中的业务限制；非 2xx 不自动重试，冷却不代表封号或套餐限制。
- 不提供 DELETE；通过 update state=ARCHIVED 归档时不可逆。SB negativeKeywords / negativeTargets / themes / recommendations / Legacy→V4 Migration 不覆盖；SD 按 ID 单查、brandSafety、recommendations、forecasts、optimizationRules、locations 不覆盖。SD 已有基础实体 create/update 和预算规则操作仍保留。

### 原始响应与分页失败

公共调用器保存每页网关响应，业务封装另存聚合结果；后者沿用 `linkfox-amazon-ads-manager-<timestamp>.json` 命名，原始页使用 `linkfox-amazon-ads-manager-gateway-<timestamp>.json`。非对象网关响应在业务层包装为 error/details 后保存，原值保留在 details 中。连接或解码异常结构化报错，不自动重试；此时 transportHttpStatus 可能为 null，不能据此推定上游状态或写入是否完成。

| 字段或情况 | 处理约定 |
|---|---|
| 分页中途错误 | success=false；保留已取实体及 total、pagesFetched，truncated=true，并保留原始错误、保护码及冷却字段。SP/SD 商品广告的部分结果仍执行 ASIN/SKU 精确筛选。 |
| 非对象或无效 JSON 分页响应 | 保存 body 原文并结构化报错，保留先前已取数据，不将异常响应当作空列表成功。 |
| costToken | 上游若返回该原生字段，原文保留，摘要按原值展示；未返回时不补算。 |
| 写入结果不确定 | 先查询已知实体或任务状态，禁止直接重放原写入。 |

### 实体与指标关联

本技能只提供实体元数据；通过 `linkfox-amazon-ads-report` 取得指标后按实体 ID 关联。报表类型示例如下，不表示全部可用报表：

| 广告产品 | reportTypeId 示例 |
|---|---|
| SP | spTargeting |
| SB | sbCampaigns |
| SD | sdCampaigns |

### 业务状态与本地退出码

| 状态 | 含义 | 处理 |
|---|---|---|
| Amazon 400 | 入参结构异常 | 核对对应产品过滤器与原生请求体，不按原参数自动重试。 |
| Amazon 401 | Ads 授权失效或服务端 token 异常 | 停止自动重试，检查授权状态；认证或密钥引导见 onboarding.md。 |
| 402 或余额提示 | 算力或余额异常 | 按 onboarding.md 处理。 |
| Amazon 403 | profile 无权限 | 核对账号归属、应用权限、区域与授权，不当作注册或充值问题。 |
| Amazon 429 | 上游限流 | 停止自动重试；短等待建议为 2–5 秒，有 retryAfter / blockedUntil 或保护码时优先遵守账号保护时长，不以短等待绕过。 |
| exit 42 | 缺少认证依赖 | 先安装 linkfox-amazon-ads-auth，stderr 提供 DEPENDENCY_MISSING。 |
| SB_V4_CAMPAIGN_NOT_SUPPORTED | V3 不能处理多广告组结构 | 请求前拒绝；按已知结构改用 V4，不作为失败后自动回落机制。 |
| SB_INVALID_BOOLEAN / SB_INVALID_TARGET_FILTERS | 布尔或原生 filters 数组不合法 | 检查字段和值；脚本会给出结构化本地错误。 |
| SB_INVALID_AD_TYPE / SB_INVALID_CREATIVE_TYPE / SB_CREATIVE_AD_ID_REQUIRED | Ad / Creative 参数不符合操作要求 | 按各接口字段表补齐，不连续试探。 |

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-amazon-ads-manager",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
