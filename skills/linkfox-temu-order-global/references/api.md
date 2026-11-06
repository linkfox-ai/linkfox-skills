# Temu 全球站订单管理 接口说明

本技能定义 9 个订单操作和 1 个加签文件下载接口，共 10 个（不含 Feedback）。订单统一以 `POST /temu/proxy` 转发，操作标识为 Body `type`，不是 URL path；紫鸟转发 path 为 `/temu-proxy/{site}/{managementType}`，本技能默认 `/temu-proxy/global/semi-managed`；上游全球网关为 `https://openapi-b-global.temu.com/openapi/router`。具体 sub_menu_code 与官方地址见 [partner-global-catalog.md](partner-global-catalog.md)。

| 操作 | 接口文档 | 对应脚本 |
|------|------|------|
| `bg.order.list.v2.get` | [apis/bg-order-list-v2-get.md](apis/bg-order-list-v2-get.md) | `scripts/global_order_list_v2_get.py` |
| `bg.order.detail.v2.get` | [apis/bg-order-detail-v2-get.md](apis/bg-order-detail-v2-get.md) | `scripts/global_order_detail_v2_get.py` |
| `bg.order.shippinginfo.v2.get` | [apis/bg-order-shippinginfo-v2-get.md](apis/bg-order-shippinginfo-v2-get.md) | `scripts/global_order_shippinginfo_v2_get.py` |
| `bg.order.decryptshippinginfo.get` | [apis/bg-order-decryptshippinginfo-get.md](apis/bg-order-decryptshippinginfo-get.md) | `scripts/global_order_decryptshippinginfo_get.py` |
| `bg.order.amount.query` | [apis/bg-order-amount-query.md](apis/bg-order-amount-query.md) | `scripts/global_order_amount_query.py` |
| `temu.order.amount.v2.query` | [apis/temu-order-amount-v2-query.md](apis/temu-order-amount-v2-query.md) | `scripts/global_order_amount_v2_query.py` |
| `bg.order.combinedshipment.list.get` | [apis/bg-order-combinedshipment-list-get.md](apis/bg-order-combinedshipment-list-get.md) | `scripts/global_order_combinedshipment_list_get.py` |
| `bg.order.customization.get` | [apis/bg-order-customization-get.md](apis/bg-order-customization-get.md) | `scripts/global_order_customization_get.py` |
| `temu.local.order.verification.upload` | [apis/temu-local-order-verification-upload.md](apis/temu-local-order-verification-upload.md) | `scripts/global_order_verification_upload.py` |
| 加签文件下载 | [本页文件下载接口](#接口加签文件下载) | `scripts/temu_global_file_download.py` |

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

## 脚本运行与授权兼容

授权说明见 [access-token.md](access-token.md)，决策流程见 [authorization-flow.md](authorization-flow.md)。Temu 没有 LinkFox 自动 OAuth，需在目标区域卖家后台通过服务市场手动授权并复制 accessToken。订单使用 Cyber-ERP酷鸟助手；商品/全托管使用酷鸟卖家助手，本土店使用 Cyber-ERP。授权需注意主账号权限、Token 有效期、分站授权和紫鸟 IP 白名单约束。

| 脚本 | CLI / 行为 |
|------|------|
| `scripts/temu_global_proxy.py` | JSON 输入；type + params，默认 global / semi-managed / order-shipping。 |
| `scripts/temu_proxy.py` | JSON 输入；显式传 site、managementType、type、params，保留多站点兼容。 |
| `scripts/temu_global_file_download.py` | JSON 输入；全球区默认值，accessToken 或 storeKey，url 必填。 |
| `scripts/temu_file_download.py` | JSON 输入；显式 site、managementType、url，保留多站点兼容。 |
| `scripts/check_linkfox_token.py` | 可选 JSON token；会发一次网关探测，不是纯本地检查；不在未授权情况下主动探测。HTTP/errcode 异常或连接失败退出 1；参数类 code=1002 只表示探测已响应，不能据此确认令牌有效或 Temu 业务授权成功。 |
| `scripts/temu_token_guide.py` | JSON shopType（或 managementType）、tokenPurpose、site；纯本地输出授权步骤。 |
| `scripts/save_temu_access_token.py` | JSON storeKey、site、managementType、accessToken，另可传 tokenPurpose（默认 default）、label；同店同站同类型同用途覆盖，不匹配则新增。 |
| `scripts/list_temu_access_tokens.py` | 无参数或 JSON mask；默认脱敏，mask=false 返回完整令牌。 |
| `scripts/get_temu_access_token.py` | JSON storeKey、site、managementType、tokenPurpose（默认 default）；未找到时 found=false 且退出码 1，找到时返回 accessToken。 |

本地令牌存储默认 `~/.linkfox/temu-access-tokens.json`，可由 `TEMU_TOKEN_STORE_PATH` 覆盖；这是授权凭据存储，不是业务响应缓存。全球区脚本使用 storeKey 时，未显式传 tokenPurpose 则选 order-shipping；通用脚本使用 default。site 和 managementType 必须小写，全球区包装会先去空白并转小写。
全球区文件下载使用 storeKey 时同样补齐默认站点与托管类型，避免误取其他区域令牌。所有业务入口支持 JSON CLI 和 --inline；公共 run 始终加 --no-cache，无自动重试或第二层缓存。包装通过公共调用器完成 LinkFox HTTP，临时兼容的密钥、额外 Token 请求头和基础地址仅在一次调用内生效，结束后恢复。

## 接口：加签文件下载

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/fileDownload`

### 请求参数

#### 网关 POST Body

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| site | string | 是 | 本技能默认 `global`；全球区，非 US/EU。通用脚本兼容 `cn` / `partner` / `us` / `global` / `eu`。 |
| managementType | string | 是 | 本技能默认 `semi-managed`；通用脚本兼容 `full-managed` / `semi-managed`。 |
| accessToken | string | 是 | Temu 店铺令牌；脚本支持直接传入，或通过 `storeKey` 从本地读取后填入此字段。 |
| url | string | 是 | 待下载的 Temu 加签资源 URL；原样传递查询串，不重复 URL 编码。 |

#### 脚本参数与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| accessToken | string | 与 storeKey 二选一 | 直接提供时优先于本地令牌。 |
| storeKey | string | 与 accessToken 二选一 | 本地令牌键；按 site + managementType + tokenPurpose 精确匹配，不跨店铺、站点或用途回退。 |
| tokenPurpose | string | 否 | 全球区订单脚本默认 `order-shipping`；仅用于本地令牌选择，不转发为业务字段。 |
| token / linkfoxToken / linkfox_token | string | 否 | 按此顺序读取首个非空值，优先于环境变量；用于 LinkFox 用户鉴权，与 Temu accessToken 不同。 |
| --inline | CLI flag | 否 | 保存完整响应并强制全量打印。 |
| --no-cache | CLI flag | 否 | 业务脚本不使用响应缓存；调用公共 run 时始终传入此选项，不读取或保存响应缓存。 |

LinkFox 环境变量按 `LINKFOX_AGENT_API_KEY`、`LINKFOXAGENT_API_KEY` 顺序读取；Header `Authorization` 与 `Token` 同值。基础地址按 `LINKFOX_TOOL_GATEWAY`、`TEMU_API_BASE_URL`、`STORE_API_BASE_URL` 顺序兼容，默认正式网关。HTTP 超时默认 150 秒。
下载 URL 原样转发；全球区脚本补齐站点、托管类型和令牌用途，通用下载脚本需显式传站点与托管类型。令牌存储与授权 CLI 见 [access-token.md](access-token.md)。
会话数据保存在当前工作目录，禁止回退到临时目录；目录不可写时在请求前报错。无响应缓存仍可能由公共调用器创建空缓存目录，不保存响应缓存文件。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 外层网关响应码，遵循公共规则。 |
| errmsg | string | 网关消息。 |
| code | integer | 网关错误码，1002 参数/Token，1003 转发失败。 |
| transportHttpStatus | integer / null | 脚本记录的外层 HTTP 状态，连接失败为 null。 |
| 其他返回字段 | 以实际返回为准 | 下载响应内部字段以实际 JSON 为准，完整保留返回内容，不预设 URL、文件内容或落地文件路径。 |

本脚本提交加签下载请求，返回并保存网关 JSON，不额外实现本地二进制写文件。定制 SVG 压缩包的独立 GET + TOA 签名约定见 [apis/bg-order-customization-get.md](apis/bg-order-customization-get.md)，与 LinkFox JSON 转发区分。

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- `code=1002`：修正参数或 LinkFox Token；`code=1003`：检查 Temu 令牌、用途、IP 白名单和转发情况。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/temu/fileDownload" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Token: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"site":"global","managementType":"semi-managed","accessToken":"TOKEN","url":"https://example.com/signed-file-url"}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-temu-order-global",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
