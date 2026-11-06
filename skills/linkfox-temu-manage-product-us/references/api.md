# Temu 美国站商品管理 接口说明

24 个商品操作见 [接口索引](apis/README.md)；每个操作的 type 是转发标识，不是 URL path。本页定义另一个实际接口：加签文件下载。

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

## 兼容运行约定

### 认证与网关

| 项目 | 约定 |
|------|------|
| 网关地址优先级 | LINKFOX_TOOL_GATEWAY → TEMU_API_BASE_URL → STORE_API_BASE_URL → https://tool-gateway.linkfox.com，去掉末尾斜线。 |
| LinkFox Key 优先级 | JSON token → linkfoxToken → linkfox_token → LINKFOX_AGENT_API_KEY → LINKFOXAGENT_API_KEY；两个请求头 Authorization 与 Token 同值。 |
| 会话头 | 保留 SESSION_ID、MESSAGE_ID、MODE_ID、APP_NAME。 |
| Temu 店铺身份 | accessToken 优先；否则按 storeKey + site + managementType + tokenPurpose 精确读取本地令牌，无自动 OAuth。 |
| 美国站默认值 | site=us，managementType=semi-managed，tokenPurpose=product-inventory；参数校验和授权应用见 [access-token.md](access-token.md)。 |
| 上游地址 | 美国站由网关转发至 https://openapi-b-us.temu.com/openapi/router；紫鸟转发路由为 /temu-proxy/{site}/{managementType}。不直接发送 Temu HTTP 请求。 |
| 参数加工 | 美国站包装器优先采用对象 params，否则将顶层非保留业务字段放入 params；request 包装层保留。通用 temu_proxy.py 则显式接收 params 对象。 |
| 响应缓存 | 本技能所有业务调用 run 时强制 --no-cache，始终禁用响应缓存。缓存目录可能被公共脚本创建，但不读写响应缓存。不会对失败或空结果自动重试。 |
| 输出文件 | 严格写入当前工作目录的 linkfox/<日期>/<session>/data/；不回退 /tmp、用户目录或其他工作区。使用微秒文件名保留同一秒内的多次响应。 |
| 输出展示 | 完整响应落盘；8000 UTF-8 字节以内全量展示，超过时显示最大列表和前三条样本；--inline 强制全量。保留 body 并解析为 temuBody。 |

### 辅助 CLI

| 脚本 | 输入与行为 |
|------|------|
| scripts/check_linkfox_token.py | 可选 JSON token，使用 /temu/proxy 的 site=cn、managementType=full-managed、accessToken=probe、type=probe 探测；这是同一转发接口的认证辅助请求，不执行商品管理操作。不会自动执行。 |
| scripts/temu_token_guide.py | JSON shopType（或 managementType）、tokenPurpose、可选 site；纯本地输出授权步骤。 |
| scripts/save_temu_access_token.py | JSON storeKey、site、managementType、accessToken、可选 tokenPurpose（默认 default）、label；只保存本地令牌。 |
| scripts/list_temu_access_tokens.py | 可选 JSON mask（默认 true），默认脱敏列出本地令牌。 |
| scripts/get_temu_access_token.py | JSON storeKey、site、managementType、可选 tokenPurpose（默认 default）；返回本地令牌，找不到时退出码为 1。 |
| scripts/temu_proxy.py | 多 site 通用转发，site、managementType、type 显式提供；与美国站包装器共用同一网关。 |
| scripts/temu_us_proxy.py | 按 JSON type 选择操作，保留美国站默认值与参数加工。 |
| scripts/temu_file_download.py / temu_us_file_download.py | 多 site / 美国站加签下载，具体字段见下文。 |

### 认证探测输出

`check_linkfox_token.py` 只在用户需要检查身份时运行，不自动探测或重试。HTTP 与 `errcode` 按公共基础规则判断；连接失败、网关异常和转发失败不能报告认证通过。正常网关响应中的 `code=1002` 表示探测已到达业务校验。

| 字段 | 类型 | 说明 |
|------|------|------|
| ok | boolean | 是否通过本次探测；失败时 CLI 退出码为 1，通过时为 0。 |
| linkfoxToken | string | 仅通过时返回脱敏的 LinkFox Key，不显示完整密钥。 |
| reason | string | 失败时返回：`linkfox_token_invalid` 表示 HTTP/errcode 为 401 或消息提示认证无效；`gateway_probe_failed` 表示其他探测失败。 |
| gatewayReachable | boolean | 通过时为 true；网关异常时根据是否取得 HTTP 状态判断，连接失败为 false；认证无效分支未定义此字段。 |
| httpStatus | integer / null | 仅 `gateway_probe_failed` 分支返回实际 HTTP 状态；连接失败为 null。 |
| message | object / string | 失败时保留网关响应或认证消息。 |
| hint | string | 失败时提供修正身份或按认证、网关说明处理的提示。 |
| note | string | 仅通过时返回探测通过说明；不表示商品业务操作成功。 |

## 接口：加签文件下载（fileDownload）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/fileDownload`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| site | string | 是 | 美国站包装器默认 us；通用脚本显式指定，支持 cn / partner / us / global / eu。 |
| managementType | string | 是 | 美国站包装器默认 semi-managed；通用脚本显式指定，支持 full-managed / semi-managed。 |
| accessToken | string | 与 storeKey 二选一 | Temu 店铺令牌，脚本解析本地店铺身份后发送。 |
| url | string | 是 | 待加签下载的资源 URL。 |
| storeKey | string | 脚本兼容 | 本地店铺键，解析后不发给网关。 |
| tokenPurpose | string | 否 | 美国站默认 product-inventory；通用脚本默认 default，仅用于本地令牌定位。 |
| token / linkfoxToken / linkfox_token | string | 否 | LinkFox Key 覆盖值，按兼容运行约定取用，不发送到下载 Body。 |
| --inline | CLI flag | 否 | 保存完整响应后强制全量打印。 |
| --no-cache | CLI flag | 否 | 始终禁用响应缓存。 |

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 如存在，按公共基础规则判断。 |
| errmsg | string | 如存在，保留网关错误消息。 |
| code | integer | 网关错误码：1002 参数或 Token 错误，1003 转发失败。 |
| httpStatus | integer / null | 网关定义的上游 HTTP 状态；当前服务未主动赋值，可能为空或缺失，不能代替本次网关请求的 HTTP 状态。 |
| contentType | string / null | 网关定义的上游 Content-Type；当前服务未主动赋值，可能为空或缺失。 |
| body | string | 网关透传的上游下载响应；可能是文件内容的 Base64 编码或原始响应，不保证编码方式，也不表示已保存为本地素材文件。 |
| _httpStatus | integer / null | 仅脚本附加：本次请求网关的实际 HTTP 状态；连接失败为 null。与上游 httpStatus 分开保存，完整响应和标准输出均保留。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 网关 code=1002 / 1003 时按参数/认证或转发失败处理。下载成功码未明确；须根据实际响应核实结果，不据 HTTP 成功推断文件已保存。
- 本接口返回网关下载结果，不额外直连素材 URL，也不解析为 temuBody。
- 上游 httpStatus 有值时也须检查该状态；body 的具体内容和编码按实际响应核实，不假定存在 downloadUrl 或自动解码保存文件。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/temu/fileDownload" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Token: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"site":"us","managementType":"semi-managed","accessToken":"TOKEN","url":"https://example.com/signed-file-url"}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-temu-manage-product-us",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
