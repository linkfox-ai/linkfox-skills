# Temu 美国站订单管理 接口说明

8 个订单操作经 POST `/temu/proxy`，以 Body `type` 区分，上游 path 均为 `/openapi/router`；加签下载另走 POST `/temu/fileDownload`。

- [订单金额/供货价查询（`bg.order.amount.query`）](apis/bg-order-amount-query.md)
- [可合并发货订单组列表（`bg.order.combinedshipment.list.get`）](apis/bg-order-combinedshipment-list-get.md)
- [订单定制商品内容批量查询（`bg.order.customization.get`）](apis/bg-order-customization-get.md)
- [订单收货地址解密查询（`bg.order.decryptshippinginfo.get`）](apis/bg-order-decryptshippinginfo-get.md)
- [订单详情查询 V2（`bg.order.detail.v2.get`）](apis/bg-order-detail-v2-get.md)
- [订单列表查询 V2（`bg.order.list.v2.get`）](apis/bg-order-list-v2-get.md)
- [订单收货地址查询 V2（`bg.order.shippinginfo.v2.get`）](apis/bg-order-shippinginfo-v2-get.md)
- [订单核验信息上传（`temu.local.order.verification.upload`）](apis/temu-local-order-verification-upload.md)
- [加签文件下载](#接口加签文件下载)

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

### 认证、环境和默认值

| 字段 / 环境变量 | 类型 | 必填 / 默认 | 说明 |
|---|---|---|---|
| token / linkfoxToken / linkfox_token | string | 否 | JSON 中按此顺序读取非空值，优先于环境变量，仅用于 LinkFox 鉴权，不转发到 Temu 业务参数。 |
| LINKFOX_AGENT_API_KEY / LINKFOXAGENT_API_KEY | string | 无 JSON 密钥时必填 | 按此前后顺序读取；请求同时保留同值 `Authorization` 与 `Token` 头。 |
| accessToken | string | 与 storeKey 二选一 | 显式 Temu 令牌优先，不是 LinkFox 密钥。 |
| storeKey | string | 与 accessToken 二选一 | 本地已保存店铺键；按 site、managementType、tokenPurpose 精确匹配，不跨店铺或用途回退。 |
| site | string | US 封装默认 us | 通用脚本须显式提供；通用脚本校验 `cn`、`partner`、`us`、`global`、`eu`；保留通用兼容能力，本技能工作流限定美国站。 |
| managementType | string | US 封装默认 semi-managed | 通用脚本须显式提供；通用校验值为 `full-managed` / `semi-managed`。 |
| tokenPurpose | string | US 封装默认 order-shipping | 用 storeKey 时供本地查找，不写入网关 Body；通用封装默认 `default`。 |
| TEMU_TOKEN_STORE_PATH | path | ~/.linkfox/temu-access-tokens.json | 覆盖本地令牌存储位置；保存/读取按同一四元组匹配，保存覆盖同键条目。 |
| LINKFOX_TOOL_GATEWAY | URL | https://tool-gateway.linkfox.com | 优先级最高；缺省依次兼容 `TEMU_API_BASE_URL`、`STORE_API_BASE_URL`。 |
| SESSION_ID / MESSAGE_ID / MODE_ID / APP_NAME | string | 否 | 透传同名请求头；SESSION_ID 同时聚合会话输出。 |
| --inline | CLI flag | 否 | 强制完整打印，仍保存完整响应。 |
| --no-cache | CLI flag | 封装始终启用 | 传给公共 run 的 argv 固定包含此项，不读写响应缓存，无第二层缓存。公共调用器可能创建空缓存目录。 |

订单脚本保持 `python scripts/us_order_*.py '<JSON 参数>' [--inline] [--no-cache]`；US 通用入口为 `temu_us_proxy.py`，必须提供 `type`。多站点兼容入口为 `temu_proxy.py`、`temu_file_download.py`。订单脚本与 US 代理优先使用对象类型的 `params`，否则将顶层非保留键作为业务参数，常见结构为 `request`；多站点 `temu_proxy.py` 仅转发显式提供的 `params`，不自动提取顶层业务字段。类型、认证和站点等保留键不会发给业务参数。

US 代理及文件下载会去除 site / managementType 首尾空白、转为小写并应用默认值；本地令牌查找与网关 Body 使用相同的规范化值。通用脚本校验显式输入。使用 storeKey 时补全默认站点、管理模式及订单用途，显式提供的 tokenPurpose 保持优先。

完整响应保存于当前工作目录 `linkfox/<日期>/<session>/data/`，文件名前缀为 `linkfox-temu-order-us-<接口标识>`；调用前验证当前目录可写，不回退家目录或临时目录。小响应全量打印，大于 8000 字节显示摘要，`--inline` 覆盖打印策略；微秒文件名避免同秒调用覆盖。业务封装调用公共 `call_api.run`，原始 body 与解析后的 temuBody 在同份文件中保存。外层 HTTP 状态另打印到 stderr，连接失败显示 None，不与响应内的业务状态混淆。非对象 JSON 由封装保存为 `gatewayResponse`，其值完整保留原始 JSON；这是脚本输出字段，不是网关字段。

### 本地授权工具

| 脚本 | JSON 参数 / CLI | 行为 |
|---|---|---|
| check_linkfox_token.py | 可选 token / linkfoxToken / linkfox_token | 通过 `/temu/proxy` 的最小 `type=probe` 请求在线探测 LinkFox 认证，输出脱敏密钥及检测结果；不能仅凭网关接受密钥认定店铺授权有效。HTTP / errcode 按公共规则判断；认证错误、连接失败、计费或权限错误、非对象响应及 code=1003 均输出 ok=false 并退出 1；网关正常响应且 code=1002 时输出 ok=true。 |
| temu_token_guide.py | shopType（或 managementType）、tokenPurpose、site | 仅输出授权步骤；shopType 支持 semi-managed / full-managed / local-native；用途另支持 product-inventory / order-shipping / full-managed / local-native / default。 |
| save_temu_access_token.py | storeKey、site、managementType、accessToken 必填；tokenPurpose 默认 default，label 可选 | 本地保存店铺令牌；不调用网关。 |
| list_temu_access_tokens.py | mask 默认 true | 列出本地店铺与用途，默认脱敏；mask=false 时显示原令牌。 |
| get_temu_access_token.py | storeKey、site、managementType 必填；tokenPurpose 默认 default | 精确查找本地令牌，未找到返回 found=false 并退出 1；找到时输出 accessToken。 |

#### LinkFox 认证探测输出

| 字段 | 类型 | 说明 |
|---|---|---|
| ok | boolean | 探测是否符合上方兼容规则；不证明 Temu 店铺授权有效。 |
| linkfoxToken | string | 仅成功时返回脱敏后的 LinkFox 密钥。 |
| gatewayReachable | boolean | 是否取得外层 HTTP 响应；连接失败为 false。 |
| note | string | 成功时的探测说明。 |
| reason | string | 失败原因：linkfox_token_invalid 为认证错误；gateway_check_failed 表示其他错误或无法确认。 |
| message | JSON value | 失败时保留网关消息或完整原始响应。 |
| transportHttpStatus | integer / null | 失败时返回外层 HTTP 状态，连接失败为 null。 |
| hint | string | 失败时的处理提示。 |

授权说明见 [access-token.md](access-token.md) 与 [authorization-flow.md](authorization-flow.md)。接口扩展按 [Partner 目录](partner-us-catalog.md) 维护；上游美国站地址为 `https://openapi-b-us.temu.com/openapi/router`，由网关路由，不直接用脚本请求。

## 接口：加签文件下载

获取 Temu 授权资源；US 入口为 `scripts/temu_us_file_download.py`，通用入口为 `scripts/temu_file_download.py`。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/fileDownload`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| site | string | 是 | 美国站为 us；US 封装默认 us。 |
| managementType | string | 是 | 美国半托管为 semi-managed；US 封装默认此值。 |
| accessToken | string | 是 | Temu 店铺令牌；脚本可使用 storeKey，由本地存储解析后发送，详见上方运行约定。 |
| url | string | 是 | 需要加签下载的原始文件 URL，不改写 URL 或丢弃查询参数。 |

脚本支持的认证别名、storeKey、tokenPurpose 和 CLI 选项见上方运行约定。定制压缩包的独立 GET / TOA 签名约定保留在 [定制内容接口](apis/bg-order-customization-get.md)，不能将两个下载协议混为一谈。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 网关业务状态码，按公共规则判断。 |
| errmsg | string | 网关业务消息，原样保留。 |
| code | integer | 网关错误码：1002 参数或 Token 错误，1003 转发失败。 |
| body | string | 网关返回的原始内容（若存在）；下载脚本不额外解析为 temuBody。 |
| error | string | HTTP 非 JSON 错误或连接错误信息（仅错误时出现）。 |
| details | string | 非 JSON HTTP 错误的原始响应（仅错误时出现）。 |
| gatewayResponse | JSON value | 仅当网关返回非对象 JSON 时，由脚本在落盘与展示层包装原始值；调用函数返回原始 JSON 值。 |

下载成功载荷按实际 JSON 原样保存和展示；不预设文件内容、编码方式、下载链接字段或其他未明确的结构。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 网关 `code=1002` 表示参数或 LinkFox Token 无效，核对参数与认证；`code=1003` 表示转发失败，核对 Temu token、用途、IP 白名单与网络。
- 下载结果和业务状态以网关实际响应为准，不推测额外的业务状态码或成功字段。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/temu/fileDownload" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Token: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"site":"us","managementType":"semi-managed","accessToken":"TOKEN","url":"https://example.com/signed-file-url"}'
```

---

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-temu-order-us",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
