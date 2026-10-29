# 认证和算力问题

- 缺少 Key：引导用户按 https://skill.linkfox.com/linkfoxskills/guide.htm 获取 Key，配置 `LINKFOX_AGENT_API_KEY`（或兼容变量 `LINKFOXAGENT_API_KEY`），然后重启会话。不要在聊天中索取或回显完整 Key。
- 网关 `errcode=401`：检查 Key 与网关环境是否匹配；`403` 表示权限不足，需检查工具权限。
- 网关余额不足：说明当前端点每次成功查询消耗5算力，由用户自行管理账户余额；不自动购买、支付或创建订单。
- 上游账号、额度、限流或可用性异常：展示安全错误信息并停止，由服务端管理员处理；不要要求用户提供 EchoTik 供应商密码，也不要把供应商异常当作充值指令。
