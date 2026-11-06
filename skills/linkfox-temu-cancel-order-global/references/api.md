# Temu 全球站取消订单 接口说明

取消订单共 6 个操作，均通过 `/temu/proxy` 转发到 Temu `/openapi/router`，以 Body 的 type 区分操作；上游地址为 `https://openapi-b-global.temu.com/openapi/router`。另提供 `/temu/fileDownload` 加签下载，共 7 个实际接口；Feedback 与公共认证引导不计入业务接口数。

业务接口各自独立定义，请按需读取：

| 接口 | 接口文档 |
|---|---|
| 取消订单售后列表查询 | [apis/bg-aftersales-cancel-list-get.md](apis/bg-aftersales-cancel-list-get.md) |
| 同意取消订单 | [apis/bg-aftersales-cancel-agree.md](apis/bg-aftersales-cancel-agree.md) |
| 卖家发起取消申请 | [apis/temu-order-cancel-appeal-apply.md](apis/temu-order-cancel-appeal-apply.md) |
| 查询取消申请结果 | [apis/temu-order-cancel-appeal-result-get.md](apis/temu-order-cancel-appeal-result-get.md) |
| 缺货取消申请 | [apis/temu-order-cancel-outofstock-apply.md](apis/temu-order-cancel-outofstock-apply.md) |
| 查询缺货取消审核结果 | [apis/temu-order-cancel-outofstock-result-get.md](apis/temu-order-cancel-outofstock-result-get.md) |
| 加签文件下载 | [本页 fileDownload](#接口加签文件下载filedownload) |

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

## 运行与认证兼容约定

业务脚本通过 `scripts/call_api.py` 的 `run` 调用 LinkFox；业务封装负责参数拼装、双请求头、两种密钥环境变量的读取和响应加工。对象响应使用公共调用器输出；其他合法 JSON 类型在传输完成后交给 `emit_result` 输出辅助函数，保存原始值且仅落盘一次。所有业务调用始终传 `--no-cache`，不读取或写入响应缓存，也没有第二层缓存。

### 脚本选项与认证兼容

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| accessToken | string | 与 storeKey 二选一 | 直接传入优先；与 LinkFox 用户 Token 是不同令牌。 |
| storeKey | string | 与 accessToken 二选一 | 本地店铺记录键；脚本读取令牌后只把 accessToken 发给网关，不转发 storeKey。 |
| site | string | 否 | Global 专用脚本去首尾空白并转小写，缺省或空值使用 global；通用兼容脚本要求显式传入小写 cn / partner / us / global / eu。 |
| managementType | string | 否 | Global 专用脚本去首尾空白并转小写，缺省或空值使用 semi-managed；通用兼容脚本要求显式传入小写 full-managed / semi-managed。 |
| tokenPurpose | string | 否 | Global 专用脚本读取 storeKey 时默认 order-shipping；通用兼容脚本默认 default。按店铺、站点、托管类型、用途精确查找，不跨用途回退。 |
| token / linkfoxToken / linkfox_token | string | 否 | LinkFox 用户 Token，按上述顺序优先于环境变量 LINKFOX_AGENT_API_KEY、LINKFOXAGENT_API_KEY。同时发送 Authorization 与 Token 同值请求头，不转发为业务字段。 |
| params | object | 否 | Global 专用脚本优先使用嵌套 params 对象；未提供时，将除认证、站点、type、params 等保留键以外的顶层字段作为业务参数，例如顶层 request 整体进入 params.request。 |
| --inline | CLI flag | 否 | 强制打印完整响应，同时保存文件。 |
| --no-cache | CLI flag | 否 | 业务调用不使用响应缓存；业务封装调用 call_api.run 时始终加入此选项，读取与写入均不缓存响应。 |

基础地址依次取 LINKFOX_TOOL_GATEWAY → TEMU_API_BASE_URL → STORE_API_BASE_URL → https://tool-gateway.linkfox.com；默认超时 150 秒。请求携带 SESSION_ID、MESSAGE_ID、MODE_ID、APP_NAME 请求头。
完整响应必须落到当前工作目录，写入前检查可写性，不回退家目录或临时目录。公共调用器即使禁用缓存仍可能创建空的 .cache 目录，该目录不保存响应，也不会复用旧响应。

### 本地授权工具与诊断

| 脚本 | 参数与行为 |
|---|---|
| scripts/temu_token_guide.py | shopType（或 managementType）必填，支持 semi-managed / full-managed / local-native；tokenPurpose 默认 default，支持 product-inventory / order-shipping / full-managed / local-native / default；site 可选，输出对应授权步骤。 |
| scripts/save_temu_access_token.py | storeKey、site、managementType、accessToken 必填；tokenPurpose 默认 default，label 可选。按店铺、站点、托管类型、用途更新同一记录，不覆盖其他用途。 |
| scripts/list_temu_access_tokens.py | 无参数默认脱敏；JSON mask=false 可显式查看原令牌。 |
| scripts/get_temu_access_token.py | storeKey、site、managementType 必填，tokenPurpose 默认 default；输出 found 与所取令牌，缺失退出 1。 |
| scripts/check_linkfox_token.py | 可传 token / linkfoxToken / linkfox_token，否则取密钥环境变量；用 site=cn、managementType=full-managed、accessToken=probe、type=probe 发送一次最小诊断请求。识别“无法识别当前用户”或“重新登录”时输出 ok=false 并退出 1；否则输出 ok=true、gatewayReachable=true 诊断结果，但此结果不能证明真实店铺授权有效。 |

本地令牌文件默认为 `~/.linkfox/temu-access-tokens.json`，可用 `TEMU_TOKEN_STORE_PATH` 覆盖。授权指引见 [access-token.md](access-token.md) 与 [authorization-flow.md](authorization-flow.md)。
通用 `temu_proxy.py` 要求 site、managementType、type；params 若提供必须是对象。Global 专用入口有默认站点与托管类型；不将这些兼容能力扩展为本技能之外的业务流程。LinkFox 请求默认超时 150 秒，并支持显式 timeout，不自动重试业务写入。

### 扩展维护约定

维护接入时，每个新增 type 对应 `references/apis/<type-slug>.md` 及调用 `_global_cancel_order_script.run_cli` 的 `scripts/global_cancel_*` 或 `global_seller_cancel_*` 入口，并同步 SKILL 接口清单、[Partner 目录](partner-global-catalog.md) 和 [分文档索引](apis/README.md)。这是后续维护约定，不代表当前执行任务应自行新增业务接口。

## 接口：加签文件下载（fileDownload）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/fileDownload`

### 请求参数

#### 网关 POST Body

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| site | string | 是 | 全球站为 global，Global 专用脚本默认 global；非 US/EU。 |
| managementType | string | 是 | 本业务使用 semi-managed，Global 专用脚本默认此值。 |
| accessToken | string | 是 | Temu 店铺令牌。直接请求必须传入；脚本可从 storeKey 对应本地记录解析。 |
| url | string | 是 | Temu 加签资源 URL；原样放入 JSON 字段，不额外 URL 编码。 |

#### 脚本选项与运行约定

Global 入口为 `scripts/temu_global_file_download.py`，通用兼容入口为 `scripts/temu_file_download.py`。使用上方认证与 CLI 约定，Global 入口默认 global / semi-managed / order-shipping；通用入口显式传 site、managementType，读取本地令牌默认用途 default。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 如返回，按公共规则判断。 |
| errmsg | string | 如返回，为网关消息。 |
| code | integer | 网关错误码：1002 参数或 Token 无效；1003 转发失败。 |
| 其他返回字段 | 实际返回类型 | 下载结果以实际返回的 JSON 字段、类型和编码为准；脚本原样保存并展示 JSON，不预设成功字段或本地文件结构，也不将响应默认为二进制文件。 |
| _http_status | integer | 脚本本地附加字段，仅 HTTP 非 2xx 的对象响应添加，保存实际 HTTP 状态；不是网关返回字段。非对象响应保留原 JSON，状态另写标准错误输出。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 网关 code=1002 时核对参数与 LinkFox 用户 Token；code=1003 时核对店铺令牌、用途、IP 白名单和网络。下载成功内容以实际 JSON 为准，不自动解析 Temu body。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/temu/fileDownload" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Token: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '
{
  "site": "global",
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
  "skillName": "linkfox-temu-cancel-order-global",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
