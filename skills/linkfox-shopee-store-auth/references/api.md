# Shopee 店铺授权与管理 接口说明

## 公共规则

### 调用规范

- **请求基础地址**：`LINKFOX_TOOL_GATEWAY` 默认 `https://tool-gateway.linkfox.com`
- **请求方式**：POST, HTTP 超时 150s
- **请求头**
  - Content-Type: application/json
  - User-Agent: LinkFox-Skill/2.0
  - Authorization: <api_key> (<api_key> 从环境变量 `LINKFOX_AGENT_API_KEY` 或 `LINKFOXAGENT_API_KEY` 读取，未配置则按 SKILL.md 的 **## 解决认证和算力问题** 处理)

### 响应码基本规则

- **正常响应**: HTTP 状态码为 `200`–`299`，且响应体的 `errcode` 不存在、为 `null`、为空字符串（含纯空白）或为 `200`–`299`（数字或数字字符串）。授权接口也兼容旧版成功码整数 `0` 和字符串 `"0"`。
- **未正常响应**: HTTP 状态码不属于 `200`–`299`，或响应体的 `errcode` 不符合上述取值。布尔值 `false` 为无效业务码。
- **认证或用量错误**: HTTP 状态码为 `401` / `402`，按 onboarding.md 的指引处理
- **其他情况**: 依据响应体的 `errmsg` 判断具体原因

## 接口：生成授权 URL（authorizeUrl）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/shopee/authorizeUrl`

### 请求参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| shopName | string | 否 | 无 | 店铺展示名，最多 256 字符，便于列表识别。脚本去除首尾空白；空白字符串不发送。 |
| region | string | 否 | cn | `cn`（中国跨境）/ `global`（全球授权页）/ `br`（巴西）。脚本缺失或空值时按 `cn` 处理，其他值本地拒绝。 |
| appType | string | 否 | erp | 只允许 `erp` 或 `ad`。脚本对非空值去除首尾空白并转小写，缺失、null 或纯空白视为 `erp`。 |

服务端自动组装 `state`、`callbackUrl`、`redirectUrl`。授权 URL 约 1 小时有效，每次授权必须重新请求，不能复用旧地址或缓存链接。ERP 与 AD 分开生成链接并分别授权。

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| --inline | CLI flag | 否 | 强制完整打印，同时落盘；可放在 JSON 参数前后。 |
| --no-cache | CLI flag | 否 | 业务脚本禁用响应缓存，始终向 `call_api.run` 添加此选项，不读取或写入响应缓存。公共调用器虽提供 24 小时缓存能力，本技能保持禁用；空缓存目录不等于缓存响应。 |
| --help | CLI flag | 否 | 仅展示本地用法，不发起网络请求。 |

网关地址优先取 `LINKFOX_TOOL_GATEWAY`，其次兼容 `SHOPEE_API_BASE_URL`，否则使用公共规则默认地址；支持两种 API Key 环境变量。完整响应保存在当前工作目录的会话数据目录，不回退到主目录或临时目录；不可写时在请求前报错。调用编排与兼容逻辑位于 `scripts/_shopee_auth_common.py`。

CLI：`python scripts/authorize_url.py '<JSON 参数>' [--inline] [--no-cache]`，JSON 对象必需，可传 `{}` 使用默认区域与应用。脚本将完整 URL 写入 `~/.cache/linkfox/last_shopee_authorize_url.txt`；失败时尝试系统临时目录的 `linkfox_last_shopee_authorize_url.txt`。这是便于复制的最近链接文件，不用于跳过接口调用。支持 Windows `clip.exe`、macOS `pbcopy`、Linux `xclip` / `xsel` / `wl-copy`；不可用时继续提供文件或 JSON 的 `authorizeUrl` 字段，不因此重新请求。响应数据本身仍只能落盘当前工作目录。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| sourceType | string | 响应示例为 `shopee`。 |
| authorizeUrl | string | 完整授权地址，包含服务端生成的状态信息；需完整复制，不受终端软换行影响。 |
| errcode | integer / string / null | 网关业务码，可能缺省；依据基础规则判断。成功码示例为 200。 |
| errmsg | string | 错误消息；失败消息示例为“未找到授权记录”。 |
| error | string | 网络连接失败或无法解析的 HTTP 错误说明；属于脚本传输错误输出，不是授权成功数据。 |
| details | string | 仅 HTTP 错误体无法解析为 JSON 时保留的原始文本。 |
| _http_status | integer / null | 脚本本地附加字段：仅非 2xx HTTP 响应或连接失败时保存；前者为实际 HTTP 状态码，后者为 null。不是网关响应字段。 |

授权完成后，Shopee 将 Token POST 至内部 `/shopee/oauth/tokenCallback`，系统按 `state` 落库；浏览器跳转 `/shopee/oauth/redirect`。这两个系统内部地址不作为公开操作计数，也无需用户手动调用。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

| errcode | 含义 | 处理 |
|---|---|---|
| 1002 | 参数错误、appType 非 erp/ad 或未登录 | 修正参数或登录状态，不重试相同请求。 |
| 1003 | 授权服务异常或网络失败 | 说明原因；后续授权必须重新获取链接。 |

失败请求不自动重试；需要再次请求时遵循执行方式中的成本约束。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/shopee/authorizeUrl" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"shopName":"我的虾皮店铺","region":"cn","appType":"erp"}'
```

## 接口：列出已授权店铺（authorizedStores）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/shopee/authorizedStores`

### 请求参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| 无业务参数 | — | — | {} | 使用当前 API Key 的用户上下文，POST 空 JSON 对象。 |

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| --inline | CLI flag | 否 | 强制完整打印，同时落盘；可放在 JSON 参数前后。 |
| --no-cache | CLI flag | 否 | 业务脚本禁用响应缓存，始终向 `call_api.run` 添加此选项，不读取或写入响应缓存。公共调用器虽提供 24 小时缓存能力，本技能保持禁用；空缓存目录不等于缓存响应。 |
| --help | CLI flag | 否 | 仅展示本地用法，不发起网络请求。 |

网关地址优先取 `LINKFOX_TOOL_GATEWAY`，其次兼容 `SHOPEE_API_BASE_URL`，否则使用公共规则默认地址；支持两种 API Key 环境变量。完整响应保存在当前工作目录的会话数据目录，不回退到主目录或临时目录；不可写时在请求前报错。调用编排与兼容逻辑位于 `scripts/_shopee_auth_common.py`。

支持无 JSON 的 CLI：`python scripts/authorized_stores.py [--inline] [--no-cache]`；也支持通用形式 `python scripts/authorized_stores.py '{}' [--inline] [--no-cache]`。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| total | integer | 授权记录总数；同店可有 ERP、AD 两条记录，并非去重店铺数。 |
| stores | array<object> | 已授权店铺列表，每项字段见下表。 |
| errcode | integer / string / null | 网关业务码，可能缺省；依据基础规则判断。成功码示例为 200。 |
| errmsg | string | 网关错误消息。 |
| error | string | 网络连接失败或无法解析的 HTTP 错误说明；属于脚本传输错误输出，不是店铺列表。 |
| details | string | 仅 HTTP 错误体无法解析为 JSON 时保留的原始文本。 |
| _http_status | integer / null | 脚本本地附加字段：仅非 2xx HTTP 响应或连接失败时保存；前者为实际 HTTP 状态码，后者为 null。不是网关响应字段。 |

#### stores[*] 店铺授权记录

| 字段 | 类型 | 说明 |
|---|---|---|
| authRecordId | integer | 单条应用授权记录 ID，与对应应用的 access/refresh token 绑定。 |
| shopId | string | 店铺 ID；下游网关使用此身份定位，Shopee 上游资源中对应 `shop_id`。 |
| merchantId | string | 商户 ID，可作为店铺身份的另一种定位方式；Shopee 上游资源中对应 `merchant_id`。 |
| shopIdList | string | 本次授权绑定的全部店铺 ID，JSON 字符串，例如 `"[67890]"`，不是原生数组。部分记录可缺省。 |
| merchantIdList | string | 本次授权绑定的全部商户 ID，JSON 字符串，例如 `"[12345]"`，不是原生数组。部分记录可缺省。 |
| shopName | string | 店铺展示名。 |
| region | string | 授权区域：`cn` / `global` / `br`。 |
| appType | string / null | `erp` 或 `ad`；缺失、null、空白的历史记录在展示与 ERP 查找时视为 `erp`，不能据此认为已获 AD 授权。兼容字段 `app_type` 采用同一含义。 |

判断授权必须同时匹配 `shopId` 或 `merchantId` 与目标 `appType`；同一店铺可以有两条记录，不能合并后丢失应用差异。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

| errcode | 含义 | 处理 |
|---|---|---|
| 1002 | 参数错误或未登录 | 核对用户上下文，不重试相同请求。 |
| 1003 | 授权服务异常或网络失败 | 说明原因，保留现有信息，后续调用按用户需要进行。 |

失败请求不自动重试；需要再次请求时遵循执行方式中的成本约束。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/shopee/authorizedStores" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{}'
```

## 接口：查询授权状态（storeTokens）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/shopee/storeTokens`

### 请求参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| shopId | string | 与 merchantId 二选一 | 无 | 店铺 ID，最多 64 字符。脚本至少要求两种身份之一非空，不强制互斥，可同时传入。 |
| merchantId | string | 与 shopId 二选一 | 无 | 商户 ID，最多 64 字符。 |
| appType | string | 否 | erp | 只允许 `erp` 或 `ad`；脚本对非空值去除首尾空白并转小写，缺失、null 或纯空白按 `erp`。 |

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| --inline | CLI flag | 否 | 强制完整打印，同时落盘；可放在 JSON 参数前后。 |
| --no-cache | CLI flag | 否 | 业务脚本禁用响应缓存，始终向 `call_api.run` 添加此选项，不读取或写入响应缓存。公共调用器虽提供 24 小时缓存能力，本技能保持禁用；空缓存目录不等于缓存响应。 |
| --help | CLI flag | 否 | 仅展示本地用法，不发起网络请求。 |

网关地址优先取 `LINKFOX_TOOL_GATEWAY`，其次兼容 `SHOPEE_API_BASE_URL`，否则使用公共规则默认地址；支持两种 API Key 环境变量。完整响应保存在当前工作目录的会话数据目录，不回退到主目录或临时目录；不可写时在请求前报错。调用编排与兼容逻辑位于 `scripts/_shopee_auth_common.py`。

CLI：`python scripts/store_tokens.py '<JSON 参数>' [--inline] [--no-cache]`。本接口仅读数据库，不触发刷新。不能为后续 `/shopee/developerProxy` 调用先取原始令牌。

### 响应结构

只提供授权状态与元数据，不应返回原始 access token 或 refresh token。脚本在响应落盘、打印及状态摘要前剥离原始令牌，保留其他字段；兼容嵌套对象/数组与下划线命名，防止响应中的令牌泄露。

| 字段 | 类型 | 说明 |
|---|---|---|
| authRecordId | integer | 对应应用授权记录 ID。 |
| shopId | string | 店铺 ID。 |
| merchantId | string | 商户 ID。 |
| shopIdList | string | 本次授权绑定的全部店铺 ID，JSON 字符串，不是原生数组。 |
| merchantIdList | string | 本次授权绑定的全部商户 ID，JSON 字符串，不是原生数组。 |
| appType | string / null | 查询对应的应用；`erp` / `ad`，历史缺失、null 或空白按 ERP 理解。 |
| tokenType | 未约定 | 兼容历史响应的令牌类型元数据；当前网关 VO 未定义，不保证返回。 |
| expireIn | integer | 数据库保存的 access token 有效期（秒），直接读取存储值，不是实时剩余秒数；不能据此判断当前是否到期或计算倒计时。本接口不刷新令牌。 |
| status | string | `ACTIVE` / `EXPIRED`；当前服务按库内 access token 是否非空设置，不进行实时上游验证，`ACTIVE` 不保证令牌仍可用。 |
| tokenExpiresAt | 未约定 | 状态摘要支持的到期时间字段；类型和格式未约定，按实际返回解释。 |
| expiresIn | 未约定 | 状态摘要支持的剩余有效时长字段；类型和单位未约定，按实际返回解释。 |
| accessTokenExpireIn | 未约定 | 状态摘要支持的 access token 有效时长元数据；类型和单位未约定，按实际返回解释。 |
| refreshTokenExpireIn | 未约定 | 状态摘要支持的 refresh token 有效时长元数据；类型和单位未约定，按实际返回解释。 |
| userType | 未约定 | 状态摘要支持的用户类型；类型和枚举未约定，按实际返回解释。 |
| grantedScopes | 未约定 | 状态摘要支持的已授予权限；类型和结构未约定，按实际返回解释。 |
| message | string | 授权状态说明；当前提示令牌已由后台管理，不经 Agent 返回。 |
| errcode | integer / string / null | 网关业务码，可能缺省；依据基础规则判断。成功码示例为 200。 |
| errmsg | string | 失败消息示例为“未找到授权记录”。 |
| accessToken / refreshToken | string | 服务端可能误返回的原始令牌，脚本剥离，不展示、不落盘，也不传给下游。 |
| error | string | 网络连接失败或无法解析的 HTTP 错误说明；属于脚本传输错误输出，不是授权状态。 |
| details | string | 仅 HTTP 错误体无法解析为 JSON 时保留的原始文本。 |
| _http_status | integer / null | 脚本本地附加字段：仅非 2xx HTTP 响应或连接失败时保存；前者为实际 HTTP 状态码，后者为 null。不是网关响应字段。 |

标为兼容或“未约定”的元数据均非保证返回；类型以真实响应为准，不将缺失字段理解为未授权。状态查询不触发刷新；下游 `developerProxy` 在上游报告令牌过期或无效时，由服务端刷新并重发一次，客户端无需先获取令牌或调用刷新接口。若最终仍提示授权失效，再按目标应用重新授权。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

| errcode | 含义 | 处理 |
|---|---|---|
| 1002 | 参数错误、appType 非 erp/ad 或未登录 | 核对身份参数、目标应用与登录状态，不重试相同请求。 |
| 1003 | 授权服务异常或网络失败 | 说明原因，后续调用按用户需要进行。 |
| 1004 | 找不到目标应用的店铺授权 | 先核对已授权列表中的店铺身份与应用；缺失时按能力补授权。 |
| 1005 | Token 失效 | 按对应 appType 重新授权，不用另一应用令牌替代。 |

失败请求不自动重试；需要再次请求时遵循执行方式中的成本约束。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/shopee/storeTokens" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"shopId":"67890","appType":"ad"}'
```

## 接口：业务转发（developerProxy，下游协议）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/shopee/developerProxy`

### 请求参数

此操作由下游业务技能调用，本技能不提供对应脚本或自动转发工作流。转发定义与限制如下；具体业务参数、写入范围及上游响应由相应业务技能负责。

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| path | string | 是 | 无 | Shopee 相对资源路径，最多 2048 字符，规范化后须为 `api/v2` 或以 `api/v2/` 开头，并通过配置白名单；可带前导 `/`，不传主机名，不含 `..` 或 `//`。商品列表示例为 `api/v2/product/get_item_list`，广告余额示例为 `api/v2/ads/get_total_balance`。 |
| method | string | 是 | 无 | `GET` / `POST` / `PUT` / `DELETE`；服务端去除首尾空白并转大写。外层 LinkFox 请求始终为 POST。 |
| shopId | string | 与 merchantId 至少传一个 | 无 | 店铺身份，最多 64 字符，由服务端注入对应应用令牌；不要自行改为网关入参 `shop_id`。 |
| merchantId | string | 与 shopId 至少传一个 | 无 | 商户身份，最多 64 字符，由服务端注入对应应用令牌；不要自行改为网关入参 `merchant_id`。 |
| queryString | string | 否 | 无 | 不含 `?` 的查询串，最多 4096 字符。商品列表示例为 `offset=0&page_size=20&item_status=NORMAL`；动态值按上游约定编码，保持字段名与已有百分号编码。 |
| body | string | 否 | 无 | 上游请求正文，最多 1048576 字符；POST/PUT 可传 JSON 字符串或其他正文，缺失或空白时发送空正文；GET/DELETE 不转发正文。具体结构由业务技能确定。 |
| contentType | string | 否 | POST/PUT 默认 application/json; charset=utf-8 | 上游正文的 Content-Type，最多 128 字符；不是外层网关请求头。 |
| accessToken | string | 否；已废弃 | 无 | 兼容调用字段，传入也会被忽略；当前流程不传、不从 storeTokens 获取。 |
| appType | string | 不应传入 | 无 | 不作为转发的应用选择依据。服务端按 path 自动路由：`api/v2/ads/**` 走 AD，其余 `api/v2/**` 走 ERP。 |

必须先核对目标店铺的对应应用授权；只有 ERP 不能使用广告接口。参数、白名单或令牌错误不得通过更换应用、店铺或反复试探路径绕过。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 网关业务码，可能缺省；按基础规则判断。成功码示例为 200。 |
| errmsg | string | 错误说明；错误消息示例为“未找到授权记录”。 |
| httpStatus | integer | 上游 HTTP 状态码，与外层网关 HTTP 状态区分；外层正常响应不代表上游业务成功。 |
| contentType | string | 上游响应 Content-Type，可为 null。 |
| body | string | 上游响应正文，通常为 JSON 字符串；按 contentType 和对应业务定义解析，保留原始内容，不假设已是对象。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

| errcode | 含义 | 处理 |
|---|---|---|
| 1002 | 参数错误、应用参数不合法或未登录 | 核对参数与用户状态；转发不应传 appType。 |
| 1003 | 授权服务异常或网络失败 | 说明原因；是否重新调用按业务范围与成本约束决定。 |
| 1004 | 找不到目标应用的店铺授权 | 核对店铺身份与路径对应的应用，先补授权，不直接继续业务请求。 |
| 1005 | Token 失效或资源路径不在白名单 | 失效时按对应应用重新授权；路径必须以 api/v2 开头，并核对业务路径是否放行。 |

失败请求不自动重试；需要再次请求时遵循执行方式中的成本约束。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/shopee/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"path":"api/v2/product/get_item_list","method":"GET","shopId":"67890","queryString":"offset=0&page_size=20&item_status=NORMAL"}'
```

---

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-shopee-store-auth",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
