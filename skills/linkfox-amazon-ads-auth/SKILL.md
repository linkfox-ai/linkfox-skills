---
name: linkfox-amazon-ads-auth
description: 管理亚马逊广告（Amazon Ads）账号的授权连接，支持手动授权、紫鸟自动或批量授权、已授权账号与站点查询、广告 profile 查询和当前成员连接解绑。适用于广告账号绑定、恢复授权、为广告查询或报告选定账号和站点；不适用于广告活动管理、广告报告拉取、Amazon 原始令牌读取或卖家订单库存管理。
---
# Amazon Ads 授权与广告账户管理

## 适用范围

### 适用

完成 Amazon Ads 的 LWA OAuth 授权、发现 profile 并管理当前用户的授权连接。此技能是广告管理和报告技能的前置依赖。

**场景速查**

| 用户表达 | 查询场景 |
|---|---|
| 绑定或恢复我的广告账号 | 选择手动或紫鸟 CLI 自动授权。 |
| 全部店铺自动授权 | 仅执行所选 Amazon 店铺的 Ads 授权。 |
| 看已授权的广告账户和站点 | 列出账号与站点。 |
| 查 profile，给美国站拉报告做准备 | 查询并解析目标广告 profile。 |
| 解绑或断开广告连接 | 核对整份连接影响后解除当前成员绑定。 |

### 边界

广告活动、组、关键词、商品广告和定向查询使用 `linkfox-amazon-ads-manager`；广告指标报告使用 `linkfox-amazon-ads-report`。这两个下游技能为只读，不用于创建、修改或删除广告；卖家订单、库存、财务转交对应 `linkfox-amazon-store-*` 技能。Amazon 官方撤销授权与本技能的本地连接解绑不同。

## 接口清单

| 接口 | 端点 | 对应脚本 | 说明 |
|---|---|---|---|
| 生成授权链接（authorizeUrl） | POST `/amazonAds/authorizeUrl` | `scripts/authorize_url.py`；自动模式 `scripts/automatic_authorize_url.py` | 发起本次 OAuth 请求。 |
| 列已授权账号（authorizedStores） | POST `/amazonAds/authorizedStores` | `scripts/authorized_stores.py`；自动核验 `scripts/automatic_verify.py` | 按 profile 聚合账号与站点。 |
| 列广告 profile（profiles） | POST `/amazonAds/profiles` | `scripts/profiles.py`；自动核验 `scripts/automatic_verify.py` | 查询快照或刷新上游数据。 |
| 解绑广告连接（cancelAuthorization） | POST `/amazonAds/cancelAuthorization` | `scripts/cancel_authorization.py` | 解除当前成员的整份连接。 |

## 前置条件

LinkFox Key 用于识别当前成员并隔离授权数据；所有接口均需要身份凭证。手动授权准备可识别的账号名称；自动授权先确认执行环境并读取 `references/automatic-authorization.md`。接口参数、区域、CLI 与缓存兼容约定见 `references/api.md`。

## 授权、选店与解绑流程

1. **先路由授权方式。** 仅新增、恢复或批量授权时选择方式，查询和解绑直接进入对应流程。用户尚未选择时，先展示“手动授权”及一句说明：“紫鸟 CLI 自动授权（推荐，仅支持本机 Windows/macOS；Agent 会自动检查并推进，只有登录、系统确认或审核等必要步骤才需要你操作）”。用户明确要求自动授权时直接进入，不重复询问，也不先询问手动账号名称。
2. **手动授权。** 先询问可识别的账号名称，再生成 URL，以文本形式交给用户在日常运营店铺的安全网络环境打开，提示优先使用紫鸟等专业防关联浏览器，避免陌生或公共网络。完成后系统自动保存令牌并同步 profile；按需查询已授权列表确认。
3. **紫鸟自动或批量授权。** 先根据宿主信息确认是用户可见的本机 Windows/macOS，CLI、客户端和 Bridge 同机；仅操作系统类型、已登录或 Bridge 连通不证明是本机。远程主机、虚拟机、云端、容器、WSL、Linux 或位置不明时，禁止安装 CLI、申请 Key、列店铺或生成链接，引导在本机执行或改手动。确认后完整执行 `references/automatic-authorization.md`，后台复用已有可用配置，只在必要步骤交给用户。使用所选紫鸟店铺名称作授权标记，不另问手动账号名称；“全部授权”只创建 Ads worker。每店沿本次 OAuth 链路推进，遵守环境准备、窗口归属、恢复、MFA、成功证据与清理规则。
4. **列已授权账号。** 查询列表并展示账号与站点；需要连接完整范围或更丰富的业务字段时查询 profile。
5. **给下游选店。** 用户只说“美国站”“我的店铺”时，解析真实授权数据，不要求用户报数字标识。仅一个账号时按站点定位；多个账号且只有站点时按账号名澄清；账号名与站点齐全或用户显式给出标识时直接使用。匹配成功不播报数字标识，仅在歧义或失败时询问。下游传解析出的 profile 和区域，令牌由服务端注入。
6. **解绑连接。** 仅在用户要求时，先查 profile 快照定位整份连接，不能以按 profile 去重的已授权列表判断完整关系。展示连接下全部账户与站点；用户只要求单站点时，先取得对整份连接解绑的明确同意。按授权记录解绑，说明保留令牌和其他成员绑定，再重新查询连接，不自动重新授权。API Key 对应同一成员身份的使用者会一起受影响。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **脚本调用（推荐）**：`python <脚本路径> '<JSON 参数>' [--inline] [--no-cache]`。
- **调用约束**：不消耗算力 （限时）。所有业务入口始终关闭响应缓存。同一会话、同一参数组合避免重复调用；失败或空结果时先解释原因，不擅自重试，按 `references/ads-protection.md` 处理保护状态与冷却。

### 输出策略

- 手动授权和常规查询、解绑 CLI 始终保存完整响应；自动辅助 CLI 与程序化调用仅返回内存结果。保存目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-amazon-ads-auth-<timestamp>.json`。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，用于聚合同一任务的数据。完整响应禁止写入 `/tmp`，当前目录不可写时应报错；手动授权的干净 URL 导出及其回退路径见 `references/api.md`。
- 响应体不超过 8 KB：保存后，将完整 JSON 打印到标准输出。
- 响应体超过 8 KB：保存后，标准输出仅展示摘要，包括顶层字段、常见计数（如 `total`、由 `X-Cost-Token` 响应头附加的 `costToken`）、最大列表字段的长度和前 3 条样本。`costCredit` 在提供对应响应头时保存在完整 JSON 中，需按需提取。
- 添加 `--inline` 可强制全量打印到标准输出，同时仍保存文件。

先通过摘要判断数据是否足够。需要具体字段时，优先使用 `jq` 或 `ConvertFrom-Json` 从保存的 JSON 文件按需提取，避免将整份响应载入上下文。

## 执行规则

### 算力消耗预估

不消耗算力 （限时）。

**声明**：算力消耗以实际扣除为准；如因需要调整算力消耗标准，恕不另行通知。最终解释权归 LinkFox 官方所有。

### 解决认证和算力问题

出现以下情况时，按 `references/onboarding.md` 的指引处理：

- 未配置接口密钥：`LINKFOX_AGENT_API_KEY` 和 `LINKFOXAGENT_API_KEY` 均为空。
- HTTP 状态码为 `401` 或 `402`。
- 响应提示算力或余额不足、计费不足、配额超限、套餐到期或需要充值。英文错误消息也按其含义判断。

### 约束与建议

- **理解 ID 关系**：一次 OAuth 对应一份授权连接，一份连接可覆盖多个 marketplace，每个站点有业务 profile；广告主实体标识跨 marketplace 稳定。选店与解绑使用不同标识，详见接口参考。
- **清晰展示数据**：账号列表优先展示 `profileId / accountInfoName / countryCode / region`；站点关键词参考美国/US、英国/UK、日本/JP、德国/DE，以真实 `countryCode` 兜底。授权自动化汇总服务、紫鸟店铺、结果、原因或证据、用户下一步。
- **保护凭证**：不向用户索取、读取、展示或传递 Amazon raw token；本技能不提供原始令牌读取或手动刷新能力。自动模式不得把 OAuth URL 回显到聊天、写剪贴板或临时文件；应安全捕获自动脚本输出并只在内存传给紫鸟。
- **输出与缓存**：所有业务入口始终关闭响应缓存。手动和常规查询 CLI 按输出策略保存响应；自动辅助 CLI 与程序化调用仅返回内存结果，不能用常规 CLI 替代自动入口。具体选项、兼容环境变量与保存行为见 `references/api.md`。
- **避免重复调用**：授权失败先解释原因，不擅自重试。保护状态、冷却时长与允许重试次数严格按 `references/ads-protection.md` 执行，不换脚本或创建任务绕过保护。
- **修复链接复制问题**：手动链接软换行可能插入空格或 `+`，污染 `client_id` 并引发 Amazon 400 `StegoRuntimeOAuth2ClientManager:getClientDefinition`。优先从脚本写入的剪贴板或 `~/.cache/linkfox/last_authorize_url.txt` 复制完整 URL，建议无痕窗口；自动模式仅使用内存中完整 URL。
- **解释同步失败**：回调显示 `profile_sync_failed` 时，可到 [Amazon Ads 控制台](https://advertising.amazon.com/) 的 Manager accounts 创建经理账户并关联广告账户后重新授权；自动模式需人工排查，不能仅凭同步失败断言无 profile、权限不足或后端错误，也不以旧记录冒充本次成功。
- **以文本形式展示链接**：授权链接只能以文本展示（plaintext），不要转成链接给用户。

## 使用示例

### 手动绑定新广告账号

用户：帮我绑定美国广告账号，我选择手动授权。

询问账号名称，生成授权链接，提示安全网络与完整 URL 复制方式，授权完成后按需核验。

### 紫鸟批量授权

用户：给我选中的紫鸟店铺全部自动授权 Ads。

确认用户本机环境后按自动授权参考推进；沿用店铺名称，仅核验本次回调并汇总真实结果。

### 为美国站报告准备账号

用户：我要看美国站广告报告。

从已授权账号解析站点；存在多账号歧义时按名称澄清，交给下游报告技能。

### 解除广告连接

用户：断开这份广告授权连接。

核对连接下全部账户和站点后解绑，说明仅移除当前成员连接，并查询最终状态。

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。
