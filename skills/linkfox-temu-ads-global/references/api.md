# Temu 全球站电商广告 接口说明

本技能定义 9 项操作：7 个广告 type、通用转发与加签下载；认证探测复用通用转发，公共 onboarding 不计入业务接口。Temu type 位于 Body，不是额外的 URL path。

[7 个广告接口独立文档](apis/README.md)；[Partner 菜单与文档来源](partner-global-catalog.md)。

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

| 项目 | 约定 |
|------|------|
| 网关根地址 | `LINKFOX_TOOL_GATEWAY` → `TEMU_API_BASE_URL` → `STORE_API_BASE_URL` → `https://tool-gateway.linkfox.com`，去除尾部 `/`。 |
| LinkFox 认证 | JSON `token` → `linkfoxToken` → `linkfox_token` → `LINKFOX_AGENT_API_KEY` → `LINKFOXAGENT_API_KEY`；非空 JSON 值去除首尾空白。Authorization 与 Token 请求头同值。 |
| Temu 认证 | accessToken 优先；否则按 storeKey、site、managementType、tokenPurpose 精确匹配本地令牌。两套令牌不能混淆。 |
| 全球站默认 | site=`global`、managementType=`semi-managed`、tokenPurpose=`product-inventory`；显式值优先，站点和托管类型在全球站封装中转小写。特定 Ads 的 tokenPurpose 以 Partner 要求为准。 |
| 通用脚本校验 | temu_proxy.py / temu_file_download.py 必须显式提供 site 和 managementType，且小写；site 为 cn / partner / us / global / eu，managementType 为 full-managed / semi-managed。 |
| 业务参数包装 | global_ads_* 与 temu_global_proxy.py：有对象 params 时优先使用；否则把除认证、店铺、site、managementType、tokenPurpose、type、params 外的顶层字段整体作为 params。request 必须保持完整层级，不自动去掉 request。temu_proxy.py 只转发显式对象 params，非对象报错。 |
| 本地存储 | 默认 `~/.linkfox/temu-access-tokens.json`，可用 `TEMU_TOKEN_STORE_PATH` 覆盖；维度为 storeKey + site + managementType + tokenPurpose，重复维度替换令牌。列表默认脱敏，可传 mask=false，读取脚本返回原令牌。 |
| --inline | 强制全量 stdout，同时保留完整响应文件。 |
| --no-cache | 所有业务封装调用 run 时始终加入该选项，不读写响应缓存；公共调用器可能创建空 .cache 目录。复用数据时读取已保存的完整响应。 |
| 会话输出 | 数据写入当前工作目录的 linkfox/<日期>/<SESSION_ID 或自动会话>/data；请求前检查可写性，不回退到家目录或临时目录。公共调用器统一保存一次，包含原 body 与可解析的 temuBody；连续调用用微秒时间戳避免覆盖。 |
| HTTP | 使用公共 call_api.run，默认 150 秒；内部 timeout 参数继续生效，保持 SESSION_ID / MESSAGE_ID / MODE_ID / APP_NAME 追踪头。 |
| 探测脚本 | check_linkfox_token.py 发起一次 /temu/proxy 的 type=probe 最小请求，会产生外部调用；识别“无法识别当前用户 / 重新登录”消息，并按 HTTP / errcode 识别异常；HTTP 或 errcode 为 401 / 402 分别提示认证或用量错误，连接失败及其他异常返回失败，不误报可达或认证成功；仅正常探测返回脱敏 LinkFox Token，原始响应静默落盘。 |

授权应用、主账号、多站点、Token 有效期及 IP 白名单要求见 [access-token.md](access-token.md)；授权步骤见 [authorization-flow.md](authorization-flow.md)。

### 本地授权 CLI

| 脚本 | 输入与输出 |
|------|------|
| scripts/temu_token_guide.py | JSON shopType 或 managementType；shopType 为 semi-managed / full-managed / local-native；tokenPurpose 为 product-inventory / order-shipping / full-managed / local-native / default；site 可选，输出对应后台步骤。 |
| scripts/save_temu_access_token.py | JSON storeKey、site、managementType、accessToken 必填，tokenPurpose 默认 default、label 可选；返回 storeKey、site、managementType、tokenPurpose、storePath、updatedAt、replaced。 |
| scripts/list_temu_access_tokens.py | 可选 JSON mask（默认 true）；返回 storePath 和 stores，包含 storeKey、label、tokens（site、managementType、tokenPurpose、accessToken、updatedAt）。 |
| scripts/get_temu_access_token.py | JSON storeKey、site、managementType 必填，tokenPurpose 默认 default；返回 found、店铺维度及 accessToken；缺失时 found=false、hint 并退出 1。 |
| scripts/check_linkfox_token.py | 可选 JSON LinkFox 密钥别名；成功返回 ok、linkfoxToken（脱敏）、gatewayReachable、note；失败返回 ok=false、reason、message、hint 并退出 1；reason 为 linkfox_token_invalid / linkfox_billing_error / gateway_probe_failed。probe 的业务参数错误仍可用于确认网关可达，但不能证明目标 Temu 店铺已授权。 |

### 探测脚本响应字段

| 字段 | 类型 | 说明 |
|------|------|------|
| ok | boolean | 探测结果；异常为 false，不能把网络故障当作密钥有效。 |
| linkfoxToken | string | 正常探测时返回脱敏密钥；短密钥返回 ***。 |
| gatewayReachable | boolean | 正常探测时为 true。 |
| note | string | 正常探测说明，不证明 Temu 店铺授权有效。 |
| reason | string | 失败原因：linkfox_token_invalid / linkfox_billing_error / gateway_probe_failed。 |
| message | string / object | 失败时的错误消息或完整网关响应。 |
| hint | string | 失败时的后续处理建议；失败退出码为 1。 |

### 接入资料维护

后续如用户另行提供 Partner 文档（type、sub_menu_code、URL、完整请求与响应表），再扩展本技能内对应 references/apis 文档与调用 _global_ads_script.run_cli 的封装，并同步接口清单、[文档索引](apis/README.md)和 [Partner 目录](partner-global-catalog.md)。现有未给出的枚举、单位和子字段不补造。

## 接口：通用广告转发（temuProxy）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/proxy`

### 请求参数

#### 网关 POST Body

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| site | string | 是 | 全球站封装默认 `global`；多站点通用脚本显式指定 `cn` / `partner` / `us` / `global` / `eu`。 |
| managementType | string | 是 | 全球站封装默认 `semi-managed`；通用脚本支持 `full-managed` / `semi-managed`。 |
| accessToken | string | 是 | Temu 店铺令牌；脚本中与 storeKey 二选一，直接令牌优先；可用本地 storeKey 解析后填入。 |
| type | string | 是 | Temu 操作标识，写在 Body 而不是 URL path；由调用者指定所需的 Temu type；已接入广告操作见上方文档索引，通用脚本保留任意 type 转发能力。 |
| params | object | 否 | 业务载荷，广告字段放入 `params.request`。全球站封装只发送非空对象；temu_proxy.py 保留显式空对象。 |

#### 脚本 JSON 兼容参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| storeKey | string | 与 accessToken 二选一 | 本地令牌库的店铺键；不发送到网关。 |
| tokenPurpose | string | 否 | 全球站封装默认 `product-inventory`，通用脚本默认 `default`；用于本地令牌选择，封装不将此项发送到网关；Partner 某 Ads 接口要求其他用途时以该接口文档为准。 |
| token / linkfoxToken / linkfox_token | string | 否 | LinkFox 密钥别名，按此顺序优先于环境变量；不发送到 Temu 业务载荷。 |

全球站脚本 temu_global_proxy.py 提供默认值；temu_proxy.py 保留多站点显式参数入口。上游 Global 地址为 `https://openapi-b-global.temu.com/openapi/router`；网关按 site 解析，不需要手工签名。

### 响应结构

#### 网关与脚本输出

| 字段 | 类型 | 说明 |
|------|------|------|
| body | string | Temu 原始 JSON 字符串；原字段始终保留。 |
| code | integer | 网关错误码：`1002` 表示参数或 Token 问题，`1003` 表示转发失败；不能代替外层 HTTP / errcode 判断。 |
| errcode | integer / string / null | 返回时依公共响应码基本规则判断。 |
| errmsg | string | 返回时为网关错误说明。 |
| _httpStatus | integer / null | 脚本本地附加字段：本次请求的实际 HTTP 状态码，连接失败为 null；不属于网关业务响应。用于识别 401 / 402 等状态，不能代替 Temu 业务结果判断。 |
| temuBody | object / array / 标量 / null | 脚本在 body 是非空且合法的 JSON 字符串时添加的解析值；无效 JSON 不添加此字段。 |

| 字段 | 类型 | 说明 |
|------|------|------|
| temuBody.success | BOOLEAN | Temu 是否成功。 |
| temuBody.errorCode | INTEGER | Temu 业务错误码。 |
| temuBody.errorMsg | STRING | Temu 业务错误消息。 |
| temuBody.result | OBJECT / OBJECT[] | 按所选 type 返回业务结果，完整已接入结构见各广告文档。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 先检查外层 HTTP 与 `errcode`，再检查网关 `code`；`1002` 核对参数及 LinkFox Token，`1003` 核对 Temu Token、用途、IP 白名单和网络。
- 网关未报错后解析 `body`，再依据 Temu `success`、`errorCode`、`errorMsg` 和 `result` 判断业务结果；不能仅因外层 HTTP 正常就宣称广告操作成功。无效 JSON 保留原 body。
- 失败或空结果不自动改参数、翻页或连续重试；后续调用遵守调用约束。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/temu/proxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Token: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "site": "global",
  "managementType": "semi-managed",
  "accessToken": "TOKEN",
  "type": "temu.searchrec.ad.goods.create.query",
  "params": {
    "request": {
      "goodsIdList": [
        100001
      ]
    }
  }
}'
```

## 接口：加签文件下载（temuFileDownload）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/fileDownload`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| site | string | 是 | 全球站封装默认 global；通用脚本显式指定 cn / partner / us / global / eu。 |
| managementType | string | 是 | 全球站封装默认 semi-managed；通用脚本显式指定 full-managed / semi-managed。 |
| accessToken | string | 是 | Temu 店铺令牌；脚本可由 storeKey 解析后填入。 |
| url | string | 是 | 待加签下载的资源 URL，按原值传入，不编码为 Temu type 或 path。 |

#### 脚本 JSON 兼容参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| storeKey | string | 与 accessToken 二选一 | 本地店铺键，accessToken 优先。 |
| tokenPurpose | string | 否 | 全球站默认 product-inventory，通用脚本默认 default；本地选择令牌，不发送到网关。 |
| token / linkfoxToken / linkfox_token | string | 否 | 按此顺序优先于两个环境变量，作为同值 Authorization 与 Token 请求头。 |

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| code | integer | 返回时为网关错误码，1002 参数或 Token 问题，1003 转发失败。 |
| errcode | integer / string / null | 返回时按公共响应码规则判断。 |
| errmsg | string | 返回时为错误消息。 |
| _httpStatus | integer / null | 脚本本地附加字段：本次请求的实际 HTTP 状态码，连接失败为 null；不属于网关业务响应。用于识别 401 / 402 等状态，不能代替 Temu 业务结果判断。 |
| 其他返回字段 | 以实际响应为准 | 文件下载脚本直接保留网关完整 JSON；文件载荷字段及类型以实际返回为准，不推断文件路径、编码或下载结果字段。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 网关 code=1002 核对参数和 Token，code=1003 核对 Temu 令牌、用途、白名单和网络。保留完整结果，不能凭 HTTP 正常推断文件已落到本地。
- 文件下载入口只调用加签下载网关，不另行请求素材 URL；支持全球站与多站点脚本。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/temu/fileDownload" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Token: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "site": "global",
  "managementType": "semi-managed",
  "accessToken": "TOKEN",
  "url": "https://example.com/signed-file-url"
}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-temu-ads-global",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
