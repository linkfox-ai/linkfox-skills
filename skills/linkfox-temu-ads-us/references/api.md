# Temu 美国站广告 接口说明

广告操作经统一端点转发，按 type 区分；本技能共 7 项广告操作及 1 项加签文件下载。通用代理与 Token 探测复用相同端点，不重复计数。

7 项广告操作的独立文档见 [广告接口目录](apis/README.md)；加签文件下载定义见 [下方接口](#接口加签文件下载)。完整端点、操作与脚本清单见 [技能入口](../SKILL.md#接口清单)。

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

## 运行约定

### 认证、网关与参数兼容

| 项目 | 约定 |
|------|------|
| 网关环境变量 | 依次使用 `LINKFOX_TOOL_GATEWAY`、`TEMU_API_BASE_URL`、`STORE_API_BASE_URL`，默认 `https://tool-gateway.linkfox.com`；移除末尾 `/`。 |
| LinkFox 密钥 | 请求 JSON 的 `token`、`linkfoxToken`、`linkfox_token` 依次优先；再取 `LINKFOX_AGENT_API_KEY`、`LINKFOXAGENT_API_KEY`。这些字段只用于请求头。 |
| 请求头兼容 | 在公共规则的请求头之外，保留同值的 `Authorization` 和 `Token`，以及 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME`。 |
| Temu 令牌 | 直接 `accessToken` 优先；否则按 storeKey、site、managementType、tokenPurpose 精确读取本地存储，过期须手动重新授权。 |
| US 默认值 | `site=us`、`managementType=semi-managed`、`tokenPurpose=product-inventory`；site、managementType 转为小写，不能据此判断实际授权有效。 |
| 多站点兼容入口 | `temu_proxy.py`、`temu_file_download.py` 仍要求显式 site 与 managementType；site 仅 `cn/partner/us/global/eu`，managementType 仅 `full-managed/semi-managed`。 |
| 转发 path | 本技能的实际 LinkFox path 为 `/temu/proxy` 与 `/temu/fileDownload`；广告操作写在 Body 的 type 中。`/temu-proxy/{site}/{managementType}` 是紫鸟转发路径，不是 LinkFox 请求地址。 |

### CLI 与输出

| 参数 / 行为 | 类型 | 说明 |
|------|------|------|
| 首个参数 | JSON object | 各业务脚本使用 JSON 入口；US 专用脚本允许顶层业务字段或 params 对象，通用多站点代理只接受 params 对象作为业务载荷。 |
| --inline | CLI flag | 全量打印，仍保存响应。 |
| --no-cache | CLI flag | 本技能不提供响应缓存；业务封装调用 call_api.run 时始终加入，重复调用不读取或写入响应缓存。公共调用器仍可能创建空 `.cache` 目录。 |
| 完整响应 | JSON file | 保存到 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-temu-ads-us-<接口标识>-<timestamp>.json`；当前目录不可写则在请求前报错，不回退家目录或临时目录。 |
| 小响应与摘要 | stdout | 不超过 8000 个 UTF-8 字节则全量打印；否则输出顶层键、常见计数和最大列表的前 3 项。 |
| transportHttpStatus | integer / null | 保留为 transportHttpStatus；网关失败时保留原响应，不通过解析 body 将失败包装成成功。 |

公共调用器统一执行请求、落盘与输出；业务封装负责认证兼容和 Temu body 解析，不另设响应缓存。业务封装始终通过 `--no-cache` 关闭公共调用器的响应缓存。

### 本地授权辅助脚本

| 脚本 | 参数 / 选项 | 行为 |
|------|------|------|
| scripts/temu_token_guide.py | shopType（或 managementType）、tokenPurpose、site | 按店铺类型及用途生成后台授权步骤，无网络调用；shopType 支持 semi-managed/full-managed/local-native，tokenPurpose 支持 product-inventory/order-shipping/full-managed/local-native/default。 |
| scripts/save_temu_access_token.py | storeKey、site、managementType、accessToken 必填；tokenPurpose 默认 default；label 可选 | 按站点、管理方式和用途新增或替换同店铺令牌，不把不同用途相互覆盖。 |
| scripts/list_temu_access_tokens.py | mask 默认 true | 默认脱敏；显式 mask=false 才显示原值。 |
| scripts/get_temu_access_token.py | storeKey、site、managementType 必填；tokenPurpose 默认 default | 找到时显示令牌，未找到返回 found=false 并退出 1。 |
| scripts/check_linkfox_token.py | 可选 token/linkfoxToken/linkfox_token | 复用 `/temu/proxy` 的最小 probe 请求探测 LinkFox Token，不是独立接口；只有外层 HTTP 正常且明确返回参数类响应时可说明鉴权通过；其他层的认证、用量或网络错误不能解释为有效。不自动运行此探测。 |

本地存储默认 `~/.linkfox/temu-access-tokens.json`，可用 `TEMU_TOKEN_STORE_PATH` 覆盖。详见 [授权与获取](access-token.md)、[授权流程](authorization-flow.md)。

## 接口：加签文件下载

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/fileDownload`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| site | string | 是 | US 脚本默认 us；多站点脚本要求显式提供，取 cn/partner/us/global/eu。 |
| managementType | string | 是 | US 脚本默认 semi-managed；多站点脚本要求显式提供，取 full-managed/semi-managed。 |
| accessToken | string | 与 storeKey 二选一 | Temu 店铺令牌；脚本优先使用直接值。 |
| storeKey | string | 与 accessToken 二选一 | 脚本按店铺及授权范围读取令牌后填充 accessToken，不直接发往网关。 |
| tokenPurpose | string | 否 | US 脚本本地查找默认 product-inventory；多站点脚本默认 default；不直接发往网关。 |
| url | string | 是 | 需加签下载的资源 URL；原值转发，不重复编码，不改动签名参数。 |

JSON 密钥兼容、CLI 和本地存储规则见上方运行约定。请求 Body 只发送 site、managementType、accessToken、url。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| body | string | 网关响应封装的业务内容；下载脚本保留原始值，不额外解析为 temuBody；下载结果内部字段按实际响应展示。 |
| code | integer | 网关业务错误码；1002 参数或 Token 问题，1003 转发失败。 |
| transportHttpStatus | integer / null | 脚本记录的 LinkFox 外层 HTTP 状态；连接失败时为 null。 |
| gatewayResponse | 任意 JSON 类型 | 仅网关返回非对象 JSON 时，脚本用此字段保留原始值。 |

其余下载结果按实际响应展示，不补造文件路径、Base64 或二进制字段定义。

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- code=1002 时核对参数与 LinkFox Token；code=1003 时核对 Temu token、tokenPurpose、IP 白名单及网络；保留原始错误，不自动重试。
- 加签文件下载不表示已经在本地生成文件；只能依据真实返回结果说明下载状态。

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
  "skillName": "linkfox-temu-ads-us",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
