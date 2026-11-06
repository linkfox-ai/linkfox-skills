# Temu 美国站取消订单 接口说明

6 个取消订单操作独立维护于 [apis/README.md](apis/README.md)；本页定义辅助文件接口与脚本运行约定。操作与文档的完整对应见 SKILL.md 的接口清单，Partner 目录见 [partner-us-catalog.md](partner-us-catalog.md)。

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

### 入口与参数映射

美国站专用脚本及 `temu_us_proxy.py` 默认 `site=us`、`managementType=semi-managed`；`storeKey` 取令牌时默认用途 `order-shipping`。支持显式站点与托管类型覆盖，但本技能业务流程仅用于美国站；其他区域转交相应技能。`type` 由专用脚本固定，通用脚本须显式指定。

美国站脚本若 `params` 为对象则优先原样作为业务块，否则提取顶层业务字段（例如 `request`）；`token`、`linkfoxToken`、`linkfox_token`、`accessToken`、`storeKey`、`site`、`managementType`、`tokenPurpose`、`type`、`params` 不进入业务块。非空业务块才发送 `params`。通用 `temu_proxy.py` 保留显式 `site`、`managementType`、`type` 校验，只接受对象类型的 `params`；通用文件脚本也要求显式站点与托管类型。

`resolve_access_token` 优先使用直接传入的 accessToken，否则按 `storeKey + site + managementType + tokenPurpose` 精确查找本地令牌。支持本地令牌存储、替换、读取及默认脱敏，具体见 [access-token.md](access-token.md)。本地存储是授权凭据存储，不是响应缓存。

美国站代理的令牌查找规则：仅在未传 tokenPurpose 且使用 storeKey 时补充默认站点、托管类型及用途供令牌查找；若显式传 tokenPurpose 且仅传 storeKey，调用方需同时提供 site 与 managementType。美国站文件入口仅默认 site；storeKey 调用时需显式 managementType。不要把通用/美国站脚本的默认值混用。

### 认证、网关与探测

LinkFox 用户密钥按 JSON `token` → `linkfoxToken` → `linkfox_token` → 环境变量 `LINKFOX_AGENT_API_KEY` → `LINKFOXAGENT_API_KEY` 的顺序取第一个非空值；兼容同时发送同值 `Authorization` 和 `Token` 请求头。同时发送 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 会话请求头。

网关地址按 `LINKFOX_TOOL_GATEWAY` → `TEMU_API_BASE_URL` → `STORE_API_BASE_URL` → 默认正式地址选择。HTTP timeout 为 150 秒；不自动重试或重复提交。

`python scripts/check_linkfox_token.py ['<JSON 参数>']` 会向 `/temu/proxy` 发最小 `site=cn`、`managementType=full-managed`、`accessToken=probe`、`type=probe` 探测；它不定义新的业务操作。识别“无法识别当前用户 / 重新登录”、HTTP / errcode=401 及常见鉴权失败消息；探测通过时仅输出脱敏令牌。连接失败、HTTP / errcode 不满足公共规则、脚本报告 error 或 code=1003 时返回 ok=false、退出码 1，不能确认令牌有效。HTTP 与 errcode 满足公共规则且无上述失败时，code=1002 可作为无效探测参数被网关受理的响应；不把 errcode=1002 视为公共规则中的正常响应。403 仅表示无权限，不引导为重新配置密钥。其 ok=true 仍不能证明 Temu 店铺授权、取消权限或订单状态。

认证探测以 JSON 输出，字段如下：

| 字段 | 类型 | 说明 |
|---|---|---|
| ok | boolean | 探测是否通过；失败退出码为 1。 |
| reason | string | 失败原因：linkfox_token_invalid 表示鉴权失败；gateway_probe_failed 表示连接、网关响应或转发异常。 |
| linkfoxToken | string | 仅探测通过时返回脱敏密钥；不输出完整密钥。 |
| gatewayReachable | boolean | 探测通过时为 true；非鉴权失败分支按是否收到 HTTP 响应判断，连接失败为 false。 |
| httpStatus | integer / null | 仅 gateway_probe_failed 分支返回；连接失败为 null。 |
| message / hint / note | string / object | 失败说明及配置提示或成功说明，按实际分支返回；不表示 Temu 业务成功。 |
| gatewayResponse | object | 仅 gateway_probe_failed 分支返回完整网关响应；原始响应也由公共调用器落盘。 |

### 缓存与落盘

业务封装调用 `call_api.run` 时始终传入 `--no-cache`，不使用公共脚本提供的 24 小时响应缓存，也没有第二层响应缓存。公共调用器可能创建空缓存目录，但不读写响应缓存文件；取消申请与状态查询均获取本次响应。

业务封装在请求前确认当前工作目录可写，固定落盘到 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-temu-cancel-order-us-<timestamp>.json`，不回退到家目录或临时目录。完整响应由公共 run 保存一次；代理响应保存时已附加可解析的 temuBody。若网关顶层返回非对象 JSON，业务封装以 error 标记异常，并在 gatewayResponse 完整保留原值，避免公共调用器落盘前崩溃；Temu body 内部的 JSON 类型不受此限制。输出采用 8000 字节阈值，支持完整输出与摘要模式、--inline、SESSION_ID 聚合及微秒文件名。认证探测也经过统一调用器保存网关原始响应，但其 stdout 输出探测 JSON。

### 扩展维护

接入新的已确认取消操作时，在 `references/apis/<type-slug>.md` 定义接口，入口沿用 `_us_cancel_order_script.run_cli`，同步更新 SKILL.md 接口清单、[partner-us-catalog.md](partner-us-catalog.md) 和 [apis/README.md](apis/README.md)。未知操作不得靠连续真实试调补齐参数。

## 接口：加签文件下载

获取 Temu 授权下的加签资源。对应 `scripts/temu_us_file_download.py` 与 `scripts/temu_file_download.py`。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/fileDownload`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| site | string | 是 | 美国站为 `us`；美国站脚本默认 `us`，去首尾空白并转小写。 |
| managementType | string | 是 | `semi-managed` / `full-managed`，去首尾空白并转小写。直接传 accessToken 时，美国站脚本默认 `semi-managed`；使用 storeKey 读取令牌时须显式提供本字段。通用文件脚本始终要求显式提供。 |
| accessToken | string | 与 storeKey 二选一 | Temu 店铺令牌；脚本优先使用直接传入值，否则从本地读取后填入网关 Body。 |
| storeKey | string | 与 accessToken 二选一 | 脚本本地令牌键，不原样转发；与 site、managementType、tokenPurpose 一起选择令牌。 |
| tokenPurpose | string | 否 | 建议 `order-shipping`；美国站脚本在 storeKey 且未直接传 accessToken、未指定用途时默认使用该值。本字段用于本地令牌选择，不原样转发。 |
| url | string | 是 | 待获取的加签文件 URL，不能为空。 |

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| token / linkfoxToken / linkfox_token | string | 否 | 按此顺序取第一个非空值，优先于环境变量；仅供 LinkFox 用户鉴权，不转发为 Temu 业务字段。 |
| LINKFOX_AGENT_API_KEY / LINKFOXAGENT_API_KEY | 环境变量 | 条件必需 | JSON 未提供 LinkFox 密钥时，按此顺序取值。 |
| --inline | CLI flag | 否 | 强制全量打印，完整响应仍落盘。 |
| --no-cache | CLI flag | 否 | 兼容公共 CLI 选项；业务封装每次调用 run 均强制附加，不读取或保存响应缓存。 |

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| _http_status | integer / null | 脚本附加的本地 HTTP 传输状态，连接失败为 null；用于判断公共 HTTP 规则，不是网关或 Temu 业务字段。大响应摘要前也单独输出该状态。 |
| errcode | integer / string / null | 网关状态码，按公共规则判断。 |
| errmsg | string | 网关错误说明，以实际返回为准。 |
| code | integer | 网关 code 错误码：1002 参数或 Token 问题，1003 转发失败。 |
| error | string | 脚本生成的连接错误或异常响应说明；出现时不能视为已获取文件。 |
| gatewayResponse | 任意 JSON 类型 | 仅网关顶层返回非对象 JSON 时由脚本附加，完整保留异常原值。 |
| 其他实际返回字段 | 以实际返回为准 | 文件响应字段以实际返回为准，脚本原样保存并输出 JSON；不自动执行第二次下载，不补造文件内容、文件路径或 URL 字段。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- code=1002 时检查参数及 LinkFox Token，code=1003 时检查 Temu 令牌、用途、白名单与网络；获取失败不能视为已取得文件。
- 保留加签地址的完整值，脚本通过 JSON 发送，不自行重编码或改写签名查询串。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/temu/fileDownload" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Token: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '
{
  "site": "us",
  "managementType": "semi-managed",
  "accessToken": "TOKEN",
  "url": "https://example.com/signed-file-url"
}
'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-temu-cancel-order-us",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
