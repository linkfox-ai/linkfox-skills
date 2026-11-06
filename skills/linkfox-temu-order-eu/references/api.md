# Temu 欧洲站订单管理 接口说明

本技能定义 10 个具名 Temu 订单操作和 1 个加签文件下载接口，共 11 项。通用代理是这些操作的复用入口，不重复计数；Feedback 与公共账号引导资源不计入业务接口数。具名操作经统一转发端点调用，Temu 操作名写在 Body 的 type；EU 上游为 `https://openapi-b-eu.temu.com/openapi/router`。

| 操作 | 接口文档 |
|---|---|
| `bg.order.list.v2.get` | [订单列表查询 V2](apis/bg-order-list-v2-get.md) |
| `bg.order.detail.v2.get` | [订单详情查询 V2](apis/bg-order-detail-v2-get.md) |
| `bg.order.shippinginfo.v2.get` | [订单收货地址查询 V2](apis/bg-order-shippinginfo-v2-get.md) |
| `bg.order.decryptshippinginfo.get` | [订单收货地址解密查询](apis/bg-order-decryptshippinginfo-get.md) |
| `bg.order.amount.query` | [订单金额/供货价查询](apis/bg-order-amount-query.md) |
| `temu.order.amount.v2.query` | [订单金额查询 V2](apis/temu-order-amount-v2-query.md) |
| `temu.order.amount.v3.query` | [订单金额查询 V3](apis/temu-order-amount-v3-query.md) |
| `bg.order.combinedshipment.list.get` | [可合并发货订单组列表](apis/bg-order-combinedshipment-list-get.md) |
| `bg.order.customization.get` | [订单定制商品内容批量查询](apis/bg-order-customization-get.md) |
| `temu.local.order.verification.upload` | [订单核验信息上传](apis/temu-local-order-verification-upload.md) |

Partner 菜单、sub_menu_code 和官方文档线索见 [Partner EU 目录](partner-eu-catalog.md)，本地授权见 [授权说明](access-token.md) 与 [授权流程](authorization-flow.md)。

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

## 网关封装与运行约定

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/proxy`

### 请求参数

#### 网关 POST Body

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| site | string | 是 | EU 封装默认 `eu`；通用脚本支持 `cn`、`partner`、`us`、`global`、`eu`，须为小写。 |
| managementType | string | 是 | EU 封装默认 `semi-managed`；通用脚本允许 `full-managed`、`semi-managed`，须为小写。 |
| accessToken | string | 是 | Temu 店铺令牌；使用脚本的 `storeKey` 时在本地读取后写入此字段。 |
| type | string | 是 | 用户指定的 `bg.*` / `temu.*` 操作名；Temu 操作名写在 Body，不是 LinkFox URL 路径。 |
| params | object | 否 | Temu 业务参数，本接口的业务块为 `params.request`。 |

#### 脚本参数与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| token / linkfoxToken / linkfox_token | string | 否 | LinkFox 密钥别名，按此顺序取首个非空值，优先于环境变量；不转发到 Temu。 |
| storeKey | string | 与 accessToken 二选一 | 本地店铺键；以 site、managementType、tokenPurpose 精确读取，accessToken 非空时优先。 |
| tokenPurpose | string | 否 | EU 封装在仅用 storeKey 且未显式指定时默认 `order-shipping`；通用脚本默认 `default`。不转发到 Temu。 |
| params | object | 否 | EU 封装优先使用该对象，否则将剔除保留控制字段后的顶层业务字段整体放入网关 params；`request` 的层级保持不变。 |
| --inline | CLI flag | 否 | 强制完整打印，并保存完整响应。 |
| --no-cache | CLI flag | 否 | 业务脚本不启用响应缓存，调用公共 run 时始终加入该选项，不读写响应缓存；公共调用器可能创建空缓存目录。 |

网关地址按 `LINKFOX_TOOL_GATEWAY` → `TEMU_API_BASE_URL` → `STORE_API_BASE_URL` → 正式地址选择。保留 `Authorization` 与 `Token` 同值双请求头及会话头。HTTP 默认超时 150 秒，不自动重试。完整响应只保存在当前工作目录的 linkfox 会话目录；不可写则请求前报错，禁止回退到家目录或临时目录。同秒多次结果使用微秒文件名避免覆盖。

本地令牌保存在 `~/.linkfox/temu-access-tokens.json`，可用 `TEMU_TOKEN_STORE_PATH` 覆盖；提供保存、读取、列举与授权指引 CLI，详见 [授权说明](access-token.md)。本地令牌存储不属于接口响应缓存。

`check_linkfox_token.py` 复用本转发入口，发送最小 `probe` 请求，不另计业务接口。探测仅在外层 HTTP 与 `errcode` 符合基础规则、且未命中认证错误或 `code=1003` 转发失败时报告 `ok=true`；正常网关响应中的参数类 `code=1002` 可作为探测证据。连接失败、HTTP 401/402、其他异常 HTTP 或非正常 `errcode` 均以 `ok=false` 和非零退出码返回，不能据此宣称令牌已被接受。探测不验证 Temu 店铺令牌或订单权限。


#### 通用 CLI 的差异

`temu_eu_proxy.py` 默认 EU 半托管，接受 params 或顶层业务字段；`temu_proxy.py` 支持多站点调用，要求显式提供 site、managementType、type，只透传可选 params 对象，非对象会在本地拒绝。通用转发不增加自动翻页、重试或新业务工作流；具体 type 的参数按相应分接口文档准备。任意新 type 的详细响应结构不在本技能中推断。

### 响应结构

#### 网关与脚本输出

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 公共响应业务状态；是否正常按基础规则判断。 |
| errmsg | string | 公共响应消息，错误时依据实际内容解释。 |
| body | string | Temu 原始 JSON 字符串，完整保留；可解析时脚本增加 temuBody。 |
| code | integer | 网关错误码；`1002` 表示参数或 LinkFox Token 无效，`1003` 表示转发失败，不覆盖公共 errcode 规则。 |
| temuBody | object / array / scalar / null | 脚本对非空合法 JSON body 解析后的值；解析失败不添加该字段。 |
| transportHttpStatus | integer / null | 脚本保留的外层 LinkFox HTTP 状态码；连接失败为 null。 |

下面字段属于 `body` 解析后的 Temu 响应，不属于外层网关对象。


| 字段（temuBody） | 类型 | 说明 |
|---|---|---|
| success | BOOLEAN | Temu 请求是否成功。 |
| errorCode | INTEGER | Temu 业务错误码。 |
| errorMsg | STRING | Temu 业务错误信息。 |
| result | OBJECT / OBJECT[] | 业务结果由具体 type 决定，按分接口文档解释，未定义字段不补造。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 先应用外层 HTTP / errcode 基础规则，再检查网关 `code`、解析 `body`，按 Temu 的 `success`、`errorCode`、`errorMsg` 和 `result` 解释业务结果；不能仅因 JSON 可解析就认定业务成功。
- 网关 `code=1002`：核对参数及 LinkFox Token；`code=1003`：检查 Temu 令牌、用途、IP 白名单及网络。Temu 业务失败时保留 `errorMsg` 和原始响应。


## 接口：加签文件下载

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/fileDownload`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| site | string | 是 | EU 封装默认 `eu`；多站点脚本支持 `cn`、`partner`、`us`、`global`、`eu`。 |
| managementType | string | 是 | EU 封装默认 `semi-managed`；通用脚本允许 `full-managed`、`semi-managed`。 |
| accessToken | string | 是 | Temu 店铺令牌，脚本也可从 storeKey 读取后写入此字段。 |
| url | string | 是 | 待下载的加签资源 URL；原值转发，保留查询串与签名，不自行重编码。 |

#### 脚本参数与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| token / linkfoxToken / linkfox_token | string | 否 | LinkFox 密钥别名，按此顺序取首个非空值，优先于环境变量；不转发到 Temu。 |
| storeKey | string | 与 accessToken 二选一 | 本地店铺键；以 site、managementType、tokenPurpose 精确读取，accessToken 非空时优先。 |
| tokenPurpose | string | 否 | EU 封装在仅用 storeKey 且未显式指定时默认 `order-shipping`；通用脚本默认 `default`。不转发到 Temu。 |
| --inline | CLI flag | 否 | 强制完整打印，并保存完整响应。 |
| --no-cache | CLI flag | 否 | 业务脚本不启用响应缓存，调用公共 run 时始终加入该选项，不读写响应缓存；公共调用器可能创建空缓存目录。 |

网关地址按 `LINKFOX_TOOL_GATEWAY` → `TEMU_API_BASE_URL` → `STORE_API_BASE_URL` → 正式地址选择。保留 `Authorization` 与 `Token` 同值双请求头及会话头。HTTP 默认超时 150 秒，不自动重试。完整响应只保存在当前工作目录的 linkfox 会话目录；不可写则请求前报错，禁止回退到家目录或临时目录。同秒多次结果使用微秒文件名避免覆盖。

本地令牌保存在 `~/.linkfox/temu-access-tokens.json`，可用 `TEMU_TOKEN_STORE_PATH` 覆盖；提供保存、读取、列举与授权指引 CLI，详见 [授权说明](access-token.md)。本地令牌存储不属于接口响应缓存。


`temu_eu_file_download.py` 默认 EU 半托管，`temu_file_download.py` 要求显式 site 与 managementType。文件下载只发送上表字段，不发送 type 或 params。EU 封装使用 storeKey 时，即使显式指定 tokenPurpose，也先补齐 site 与 managementType 默认值，再查本地令牌。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 公共响应状态，按基础规则判断。 |
| errmsg | string | 公共响应消息。 |
| code | integer | 网关错误码，1002 参数/Token，1003 转发失败。 |
| body | string | 网关可能返回的原始内容；下载脚本不将其解析为 temuBody。 |
| transportHttpStatus | integer / null | 脚本记录的外层 HTTP 状态，连接失败为 null。 |

文件下载脚本按网关返回的 JSON 原样保存与展示，不解析文件数据的其他字段、编码或二进制格式；仅依据实际返回内容判断结果，不假定存在 fileUrl、base64 等字段。

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 网关 code=1002 时核对参数和 LinkFox Token；code=1003 时检查 Temu 令牌、用途、白名单与网络。
- 若资源来自定制订单，遵守 [定制内容接口](apis/bg-order-customization-get.md) 的有效期及 TOA 签名要求；加签资源下载与查询定制内容是两个独立操作，不把 JSON 转发当作文件已下载。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/temu/fileDownload" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Token: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"site":"eu","managementType":"semi-managed","accessToken":"TOKEN","url":"https://example.com/signed-file-url"}'
```


## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-temu-order-eu",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
