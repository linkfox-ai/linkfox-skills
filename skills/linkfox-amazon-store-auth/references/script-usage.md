# 授权脚本输入与本地输出

## 脚本与区域约定

### 脚本与运行约定

| 参数 / 选项 | 类型 | 必填 | 默认值与说明 |
|------|------|------|------|
| --inline | CLI flag | 否 | 强制全量打印，仍保存响应。 |
| --no-cache | CLI flag | 否 | 本技能无响应缓存，所有业务封装始终向公共 run 传此选项；无缓存读取、写入或第二层缓存。 |

网关优先读取 `LINKFOX_TOOL_GATEWAY`，其次 `STORE_API_BASE_URL`、`SPAPI_BASE_URL`，默认正式地址。密钥优先读取 `LINKFOX_AGENT_API_KEY`，其次 `LINKFOXAGENT_API_KEY`。请求透传 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME`，超时 150s，不自动重试。区域按 Amazon 目标站点选择，不按卖家所在地推断。

普通 JSON 入口接受一个 JSON 对象和上述选项；店铺列表入口支持无参数用法，也可传 `{}`。普通 JSON CLI 返回 0 表示本次响应及业务结果正常，1 表示参数、认证、HTTP、业务或输出错误；自动 CLI 的 argparse 用法错误退出码为 2。所有网络调用由公共调用器 `call_api.py` 完成，封装在 `run` 前后处理兼容与展示，不实现第二套传输。

响应在脱敏后按接口标识落盘；文件名在微秒时间戳后附加随机标识，避免同一时钟刻度或并发调用覆盖已有响应。必须在当前工作目录保存，不能回退到临时目录，不可写时在发请求前报错。输出失败时保留已完成请求的结果，不能将它解释为可以重放写操作。

### 区域与使用限制

| 区域 | 站点 |
|------|------|
| NA | 加拿大、美国、墨西哥、巴西 |
| EU | 爱尔兰、西班牙、英国、法国、比利时、荷兰、德国、意大利、瑞典、南非、波兰、沙特阿拉伯、埃及、土耳其、阿联酋、印度 |
| FE | 新加坡、澳大利亚、日本 |

没有独立东南亚区域代码，新加坡使用 FE。区域概念默认 NA，但接口必填项不得省略；解绑必须明确区域，不能套默认。不同区域分别授权；用户只可查看和管理自己授权的店铺。回调地址须在紫鸟授权方加白名单。accessToken 通常 1 小时过期，refreshToken 用于续签，服务端保存更新后的令牌。

## 接口：获取授权链接（authorizeUrl）

本地 JSON 脚本要求 region、sellerName、central、marketplace 均为非空值，central 必须是 seller；自动 CLI 对应四个选项也必填。这是脚本流程校验，网关 authorizeUrl 仅要求 region，sellerName、central、marketplace 的可选性见 api.md。

脚本选项、环境变量、无缓存和区域限制见本文件「脚本与区域约定」。

#### 自动授权 CLI 参数

| 选项 | 类型 | 必填 | 默认值与说明 |
|------|------|------|------|
| --region | string | 是 | 无默认值；NA / EU / FE。 |
| --seller-name | string | 是 | 无默认值；本次紫鸟店铺 storeName，保留 Unicode，去除首尾空白后不得为空。映射 sellerName。 |
| --central | string | 是 | 无默认值；枚举 seller，映射 central。 |
| --marketplace | string | 是 | 无默认值；目标站点代码，去除首尾空白后不得为空，映射 marketplace。 |

## 接口：查询已授权店铺（authorizedStores）

脚本选项、环境变量、无缓存和区域限制见本文件「脚本与区域约定」，每个接口均适用。

## 接口：刷新令牌（refreshToken）

脚本选项、环境变量、无缓存和区域限制见本文件「脚本与区域约定」，每个接口均适用。

## 接口：查询授权状态（storeTokens）

脚本选项、环境变量、无缓存和区域限制见本文件「脚本与区域约定」，每个接口均适用。

## 接口：本地解绑（cancelAuthorization）

脚本选项、环境变量、无缓存和区域限制见本文件「脚本与区域约定」，每个接口均适用。
## 本地输出与脱敏

transportHttpStatus 记录外层 HTTP 状态，连接失败为 null；outputError 表示请求已完成但本地输出失败，须先核验已有结果，不直接重放。costToken / costCredit 是公共调用器从计费响应头取得的本地展示字段，不属于授权接口 VO。所有意外出现的 accessToken / refreshToken（含嵌套字段）在 stdout 与落盘前递归移除。

自动授权输出保持单 JSON 文档，authorizeUrl 只在内存传递；公共调用器只落盘移除链接后的状态元数据。手动模式按 SKILL.md 展示授权链接安全警告。
