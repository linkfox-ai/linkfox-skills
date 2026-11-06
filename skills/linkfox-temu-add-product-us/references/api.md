# Temu 美国站商品发布与维护 接口说明

19 个商品操作的字段定义分别见：

- [product-query-apis.md](product-query-apis.md)
- [product-edit-apis.md](product-edit-apis.md)
- [product-publish-apis.md](product-publish-apis.md)
- [category-spec-apis.md](category-spec-apis.md)
- [stock-price-apis.md](stock-price-apis.md)

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

### 认证与环境兼容

| 配置 / 参数 | 类型 | 说明 |
|------|------|------|
| token / linkfoxToken / linkfox_token | string | 脚本 JSON 中依次优先取非空值，覆盖环境密钥；不进入 Temu 业务 params。 |
| LINKFOX_AGENT_API_KEY / LINKFOXAGENT_API_KEY | 环境变量 | JSON 无密钥时依次使用；支持这两种变量名。 |
| Authorization / Token | HTTP header | 两个请求头必须使用相同 LinkFox 密钥；保留 Content-Type、User-Agent、SESSION_ID、MESSAGE_ID、MODE_ID、APP_NAME。 |
| LINKFOX_TOOL_GATEWAY / TEMU_API_BASE_URL / STORE_API_BASE_URL | 环境变量 | 依次选择非空网关地址，缺省 https://tool-gateway.linkfox.com，去掉尾部斜杠。 |
| TEMU_TOKEN_STORE_PATH | 环境变量 | 覆盖默认 `~/.linkfox/temu-access-tokens.json`；这是本地授权令牌存储，不是响应缓存。 |
| --inline | CLI flag | 强制全量输出，仍保存响应。 |
| --no-cache | CLI flag | 接受此选项；业务封装始终向公共 run 传入 --no-cache，无论用户是否提供，不读写响应缓存。 |

脚本 CLI 为 `python scripts/<脚本名>.py '<JSON 参数>' [--inline] [--no-cache]`。JSON 必须为对象；通用代理必须显式提供小写 site、managementType 和 type，通用下载必须显式提供 site、managementType 和 url。US 封装默认 site=us、managementType=semi-managed、tokenPurpose=product-inventory，并对站点和管理方式作小写归一化。

商品封装优先使用对象形式的 params；否则把顶层业务字段放入 params，剔除 token、linkfoxToken、linkfox_token、accessToken、storeKey、site、managementType、tokenPurpose、type、params。固定商品脚本自行设置 type，通用代理按提供的 type 透传。

直接 accessToken 优先于 storeKey；storeKey 必须按 storeKey/site/managementType/tokenPurpose 精确匹配，不回退其他店铺、站点或用途。US 封装补齐默认值后再查本地令牌；通用脚本未给 tokenPurpose 时查 default。

网关按 `/temu-proxy/{site}/{managementType}` 转发到 Temu；美国站上游为 `https://openapi-b-us.temu.com/openapi/router`，调用方不得直连。type 是 Body 字段，不是独立 URL path。site、managementType 必须按授权匹配，不能为试错自动切换。

响应在当前工作目录的 linkfox/<日期>/<session>/data 下保存一次；禁止回退到家目录或临时目录，当前目录不可写时在请求前报错。公共调用器可能建立空 .cache 目录，但业务脚本不读取或写入响应缓存。响应阈值为 8000 字节；--inline 仍落盘。

非对象网关 JSON 属于格式异常；封装将原值保留在 body 并增加 error，不据此认定认证或业务成功。

### 本地授权工具

| 脚本 | 作用与约定 |
|------|------|
| scripts/check_linkfox_token.py | 复用 /temu/proxy 的最小 probe 请求校验 LinkFox 用户令牌，先遵循公共响应规则，仅接受正常网关响应及预期的网关 code=1002 参数错误；errcode=1002 仍为异常。连接、认证、用量或非预期业务错误返回失败；探测结果不能推断 Temu 店铺已授权，不计为独立接口。 |
| scripts/temu_token_guide.py | 按 shopType（也兼容 managementType）、tokenPurpose、site 输出后台步骤，不发起 OAuth。 |
| scripts/save_temu_access_token.py | 按 storeKey/site/managementType/tokenPurpose 保存或替换令牌；支持 label。 |
| scripts/list_temu_access_tokens.py | 默认脱敏列出令牌，JSON mask=false 可显式读取原文。 |
| scripts/get_temu_access_token.py | 精确读取指定令牌；不存在时 found=false 并返回失败。 |

授权细节见 [access-token.md](access-token.md) 与 [authorization-flow.md](authorization-flow.md)。

## 接口：加签文件下载

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/fileDownload`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| site | string | 是 | US 封装默认 `us`；兼容 `cn` / `partner` / `global` / `eu`，按目标店铺授权选择。 |
| managementType | string | 是 | US 封装默认 `semi-managed`；通用脚本支持 `full-managed` / `semi-managed`。 |
| accessToken | string | 与 storeKey 二选一 | Temu 店铺令牌，最长约 8192；直接提供时优先使用。 |
| storeKey | string | 与 accessToken 二选一 | 脚本本地店铺键，解析后发送 accessToken；不发送 storeKey。 |
| tokenPurpose | string | 否 | 本地令牌用途；US 封装默认 `product-inventory`，通用脚本默认 `default`；不发送此字段。 |
| url | string | 是 | Temu 加签资源文件 URL，保留原签名和 URL 编码。 |

US 下载默认值、通用下载参数要求与认证兼容见上方运行约定。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | LinkFox 响应码，遵循公共规则。 |
| errmsg | string | 网关消息。 |
| code | integer | 网关错误码，1002 参数或令牌问题，1003 转发失败。 |
| message | string | 网关说明。 |
| transportHttpStatus | integer / null | 脚本记录的外层 HTTP 状态；连接失败为 null。 |
| error / details | string | 网络或非 JSON HTTP 错误及原文（出现时）。 |

加签下载的成功业务字段以实际返回为准；脚本保留完整网关 JSON，不臆造文件地址、Base64 或二进制结构，不自动写本地素材文件。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 外层正常后，再检查网关 code/message；1002 表示参数校验或 LinkFox 用户 Token 问题，修正后再调用；1003 表示转发或上游失败，检查 Temu accessToken、IP 白名单和网络，后续调用遵守调用约束。
- 网关请求完成不代表文件已保存到本地；根据实际返回内容说明下一步，保留原始签名 URL。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/temu/fileDownload" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Token: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"site":"us","managementType":"semi-managed","accessToken":"TEMU_PRODUCT_TOKEN","url":"https://example.com/signed-file?signature=EXAMPLE"}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-temu-add-product-us",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
