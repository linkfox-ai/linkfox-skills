# 授权脚本参数与本地输出

网关定义见 [api.md](api.md)。本文件的CLI选项、默认值、输出字段属于脚本约定。

## 接口：生成授权链接（authorizeUrl）

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；API 必填，手动 CLI 缺失或空值时补 NA。NA 为美加墨巴，EU 为英德法意西荷、印度和中东等，FE 为日澳新。 |
| accountName | string | 是 | 非空字符串，用于在已授权列表识别账号；手动 CLI 去除首尾空白。自动模式使用所选紫鸟店铺 storeName，不另询问。 |

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| --inline | CLI flag | 否 | 常规 CLI 强制完整输出，仍保存响应。 |
| --no-cache | CLI flag | 否 | 接受此选项；业务封装调用 run 时始终添加，所有请求均不读写响应缓存。 |
| LINKFOX_TOOL_GATEWAY | 环境变量 | 否 | 网关优先配置；其次兼容 AMAZON_ADS_BASE_URL，再使用正式网关。 |
| LINKFOX_AGENT_API_KEY | 环境变量 | 是，二选一 | 优先身份凭证；兼容 LINKFOXAGENT_API_KEY，不加 Bearer 前缀。 |
| SESSION_ID / MESSAGE_ID / MODE_ID / APP_NAME | 环境变量 | 否 | 透传请求头；SESSION_ID 用于会话数据归档。 |

无自动重试，超时 150 秒。常规 CLI 请求前检查当前目录可写，完整响应落到当前工作目录；不回退到 HOME 或系统临时目录。自动辅助 CLI 与各脚本 call_api() 兼容函数通过公共 run 在内存中取得结果，不保存响应、不写剪贴板，只返回一个 JSON 对象供安全捕获。所有模式始终关闭响应缓存。

手动 CLI：`python scripts/authorize_url.py '<JSON 参数>' [--inline] [--no-cache]`。成功后尝试写系统剪贴板和 `~/.cache/linkfox/last_authorize_url.txt`，文件不可写时兼容回退系统临时目录的 `linkfox_last_authorize_url.txt`；此项是干净 URL 导出，不是响应缓存。剪贴板按 Windows clip.exe、macOS pbcopy、Linux xclip / xsel / wl-copy 顺序兼容，失败静默降级。

自动 CLI：`python scripts/automatic_authorize_url.py --region <region> --account-name <storeName>`。

| 自动脚本选项 | 类型 | 必填 | 默认 / 约束 |
|---|---|---|---|
| --region | string | 是 | 无默认值；NA / EU / FE。 |
| --account-name | string | 是 | 无默认值；使用所选紫鸟 storeName，去除首尾空白后须非空。 |

Linux 返回 `auto-auth-unsupported-linux` 且不发请求。Windows/macOS 还须由 Agent 在调用前确认用户本机环境。自动入口不执行手动 CLI 的 URL 文件或剪贴板导出，输出必须在本机安全捕获。

## 接口：列已授权账号（authorizedStores）

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| 无 | — | — | 发送空对象 {}，用当前用户身份查询。 |

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| --inline | CLI flag | 否 | 常规 CLI 强制完整输出，仍保存响应。 |
| --no-cache | CLI flag | 否 | 接受此选项；业务封装调用 run 时始终添加，所有请求均不读写响应缓存。 |
| LINKFOX_TOOL_GATEWAY | 环境变量 | 否 | 网关优先配置；其次兼容 AMAZON_ADS_BASE_URL，再使用正式网关。 |
| LINKFOX_AGENT_API_KEY | 环境变量 | 是，二选一 | 优先身份凭证；兼容 LINKFOXAGENT_API_KEY，不加 Bearer 前缀。 |
| SESSION_ID / MESSAGE_ID / MODE_ID / APP_NAME | 环境变量 | 否 | 透传请求头；SESSION_ID 用于会话数据归档。 |

无自动重试，超时 150 秒。常规 CLI 请求前检查当前目录可写，完整响应落到当前工作目录；不回退到 HOME 或系统临时目录。自动辅助 CLI 与各脚本 call_api() 兼容函数通过公共 run 在内存中取得结果，不保存响应、不写剪贴板，只返回一个 JSON 对象供安全捕获。所有模式始终关闭响应缓存。

常规 CLI：`python scripts/authorized_stores.py [--inline] [--no-cache]`，也接受位置参数 `{}`。自动核验：`python scripts/automatic_verify.py --source authorized-stores`；仅返回一个 JSON 对象，不保存响应。

| 自动核验选项 | 类型 | 必填 | 默认 / 约束 |
|---|---|---|---|
| --source | string | 否 | 默认 authorized-stores；可选 authorized-stores / profiles。本接口对应 authorized-stores，始终发送空对象。 |

## 接口：列广告 profile（profiles）

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| refresh | boolean | 否 | 默认 false：读取本地快照；true：穿透上游 /v2/profiles 重新拉取并落库。 |

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| --inline | CLI flag | 否 | 常规 CLI 强制完整输出，仍保存响应。 |
| --no-cache | CLI flag | 否 | 接受此选项；业务封装调用 run 时始终添加，所有请求均不读写响应缓存。 |
| LINKFOX_TOOL_GATEWAY | 环境变量 | 否 | 网关优先配置；其次兼容 AMAZON_ADS_BASE_URL，再使用正式网关。 |
| LINKFOX_AGENT_API_KEY | 环境变量 | 是，二选一 | 优先身份凭证；兼容 LINKFOXAGENT_API_KEY，不加 Bearer 前缀。 |
| SESSION_ID / MESSAGE_ID / MODE_ID / APP_NAME | 环境变量 | 否 | 透传请求头；SESSION_ID 用于会话数据归档。 |

无自动重试，超时 150 秒。常规 CLI 请求前检查当前目录可写，完整响应落到当前工作目录；不回退到 HOME 或系统临时目录。自动辅助 CLI 与各脚本 call_api() 兼容函数通过公共 run 在内存中取得结果，不保存响应、不写剪贴板，只返回一个 JSON 对象供安全捕获。所有模式始终关闭响应缓存。

常规 CLI：`python scripts/profiles.py ['<JSON 参数>'] [--inline] [--no-cache]`，无 JSON 时发送 `{}` 读取快照。自动核验：`python scripts/automatic_verify.py --source profiles`，不主动刷新、不落盘。

| 自动核验选项 | 类型 | 必填 | 默认 / 约束 |
|---|---|---|---|
| --source | string | 否 | 默认 authorized-stores；可选 authorized-stores / profiles。核验本接口时须显式选 profiles，始终发送空对象，不添加 refresh=true。 |


refresh=true表示尝试刷新，不保证上游同步成功；应结合返回列表与本次授权证据核验。

## 接口：解绑广告连接（cancelAuthorization）

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| authRecordId | string / integer | 是 | 正整数字符串或JSON整数，数值为1–9223372036854775807；拒绝bool、浮点、指数、前导零、空白与溢出。发送网关时统一为string，不能用profileId替代。 |

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| --inline | CLI flag | 否 | 常规 CLI 强制完整输出，仍保存响应。 |
| --no-cache | CLI flag | 否 | 接受此选项；业务封装调用 run 时始终添加，所有请求均不读写响应缓存。 |
| LINKFOX_TOOL_GATEWAY | 环境变量 | 否 | 网关优先配置；其次兼容 AMAZON_ADS_BASE_URL，再使用正式网关。 |
| LINKFOX_AGENT_API_KEY | 环境变量 | 是，二选一 | 优先身份凭证；兼容 LINKFOXAGENT_API_KEY，不加 Bearer 前缀。 |
| SESSION_ID / MESSAGE_ID / MODE_ID / APP_NAME | 环境变量 | 否 | 透传请求头；SESSION_ID 用于会话数据归档。 |

无自动重试，超时 150 秒。常规 CLI 请求前检查当前目录可写，完整响应落到当前工作目录；不回退到 HOME 或系统临时目录。自动辅助 CLI 与各脚本 call_api() 兼容函数通过公共 run 在内存中取得结果，不保存响应、不写剪贴板，只返回一个 JSON 对象供安全捕获。所有模式始终关闭响应缓存。

CLI：`python scripts/cancel_authorization.py '<JSON 参数>' [--inline] [--no-cache]`，校验后只发送 authRecordId。HTTP、XML/JSON 错误、连接失败、基础响应未正常完成或 success 不为 true 时返回非零退出码。ToolErrorResponse XML（含命名空间）归一化为 errcode/errmsg，并保留计费响应头映射。完整响应保存失败不得重新提交解绑，应先查连接状态。

## 本地输出字段

costToken / costCredit仅在响应头提供X-Cost-Token / X-Cost-Credit时附加，以响应头为准；error表示HTTP、连接、响应格式或业务错误；transportHttpStatus记录外层HTTP状态，连接失败为null；details保留非JSON正文或非对象响应。它们均不属于接口成功VO。

常规CLI在当前工作目录落盘完整结果；自动辅助函数只在内存取得JSON。保存失败不代表可以重放解绑；先核验已有结果。
