# MCP 认证与积分处理

## MCP 或 `proxy_call` 缺失

本 Skill 必须依赖 MCP “LinkFox”。如未安装该MCP，停止业务调用，不得 HTTP fallback。然后明确通知用户：
> 请先安装 LinkFox 连接器：
> - 在 WorkBuddy 左侧找到 “专家·技能·连接器” → “连接器”；
> - 搜索关键词 “LinkFox”，并安装连接器 “LinkFox”（注意：是 linkfox，不是 linkfox-product-selection），按指引完成登录授权；
> - 返回 WorkBuddy 重试。

保存后重载 WorkBuddy 或开启新会话，并确认 `proxy_call` 可见。Skill 不能自行安装或热加载 MCP。

## 错误分层

| 层级 / 状态 | 处理 |
|-------------|------|
| schema 错误或 `isError=true` | 报告 MCP/代理错误并停止，不猜测其他 `toolName`。 |
| MCP 连接 401 | WorkBuddy 自动授权链路异常；重新登录、重载连接，仍失败则联系 WorkBuddy 管理员。不得要求手填 Authorization。 |
| 代理成功、下游 JSON 401 | WorkBuddy 自动授权或下游业务认证失败；报告原错误并联系管理员，不把 Key 放进 `arguments`。 |
| 下游 JSON 402 / 积分不足 | 引导访问 `https://agent.linkfox.com/`；不得自动选套餐、下单、支付或轮询。 |
| 下游 JSON 403 | 按无权限业务错误处理，不归类为认证或积分问题，不自动重试。 |
| 其他错误 | 保留 `errcode`/`errorCode`/`code`、`errmsg`/`msg` 和参数摘要；不自动换条件或重试。 |

WorkBuddy 自动注入 Authorization。MCP 配置、Skill 文档及 `proxy_call.arguments` 均不得加入 headers、API Key、token、JWT、手机号或其他凭证。
