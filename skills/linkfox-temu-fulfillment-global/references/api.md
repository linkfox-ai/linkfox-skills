# Temu 全球站履约与发货 接口说明

23 个转发操作各自独立成文，另有 1 个加签文件下载接口。

[业务接口索引](apis/README.md) · [Partner 目录](partner-global-catalog.md) · [Temu 授权](access-token.md)

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

### 认证与兼容

- LinkFox 用户密钥与 Temu accessToken 是两套令牌。脚本按 JSON token、linkfoxToken、linkfox_token，再按 LINKFOX_AGENT_API_KEY、LINKFOXAGENT_API_KEY 解析 LinkFox 密钥；同时发送同值 Authorization 与 Token，保留 SESSION_ID、MESSAGE_ID、MODE_ID、APP_NAME 追踪头。
- 网关优先 LINKFOX_TOOL_GATEWAY，其次 TEMU_API_BASE_URL、STORE_API_BASE_URL，最后 https://tool-gateway.linkfox.com；地址去除末尾斜线，超时默认 150 秒。
- 业务 Global 默认 site=global、managementType=semi-managed、tokenPurpose=order-shipping。本地令牌优先直接 accessToken；否则按 storeKey、site、managementType、tokenPurpose 精确取值，不跨店铺或跨用途回退。通用 CLI 支持 cn / partner / us / global / eu 及 full-managed / semi-managed 校验，不据此扩大本技能业务范围。
- 本地文件默认为 `~/.linkfox/temu-access-tokens.json`，可用 TEMU_TOKEN_STORE_PATH 覆盖。授权与保存、读取、脱敏列表 CLI 见 [access-token.md](access-token.md)。
- check_linkfox_token.py 是有网络请求的认证探测 CLI，复用 /temu/proxy 的 probe 请求，不是新的业务接口。仅明确需要时运行；参数类 1002 与用户身份错误要区别，不因连接失败而宣称认证有效。HTTP 必须为 2xx，参数错误线索不能覆盖 errmsg/errorMsg 中的身份错误或其他非空非 2xx errcode。认证探测兼容网关将参数错误放在 errcode 中的响应，专门接受 errcode=1002 的参数错误线索；这不改变正常业务响应的基础规则，也不代表 Temu 店铺令牌有效。

### 请求、输出与缓存

- 23 个专用脚本使用 JSON CLI，经 _global_fulfillment_script.run_cli 编排；temu_global_proxy.py 提供通用 Global 代理，temu_proxy.py 提供通用入口。所有业务 LinkFox 请求统一通过 call_api.run；认证兼容及嵌套加工在 _temu_common.py 完成。
- 业务封装始终向 run 传 --no-cache，既不读取也不写入响应缓存；公共调用器仍可能建立空 .cache 目录，该目录不保存响应缓存。
- 转发路径模板为 `/temu-proxy/{site}/{managementType}`，本技能对应 `/temu-proxy/global/semi-managed`；通过网关 Body 的 type 区分业务操作，调用方仍只请求 `/temu/proxy`，不把该中间转发路径作为新的 LinkFox 端点。
- 请求前检查当前工作目录可写，输出固定在 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/`，不转向家目录或临时目录；SESSION_ID 优先。完整响应只保存一份，包含原 body、可解析时的 temuBody，以及 transportHttpStatus。小响应完整展示，大响应摘要展示，--inline 强制完整打印。
- 接口标识用于输出文件名时移除路径特殊字符；超过 32 字符时以短前缀与稳定哈希表示，保留微秒时间戳以区分同秒请求，避免 Windows 长路径及同秒覆盖。
- 先按公共规则判断 HTTP 和 errcode，再处理网关 code，最后检查 Temu success/errorCode/errorMsg/result。保留无法解析的原始 body；不会因解析失败丢失错误。
- 下载入口只转发 /temu/fileDownload 并保存原 JSON；不增加对任意外部素材的自动 HTTP 下载。


## 接口：加签文件下载

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/fileDownload`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| site | string | 是 | 本技能为 global；Global 下载入口默认 global。temu_file_download.py 通用入口须显式提供并校验站点。 |
| managementType | string | 是 | 本技能为 semi-managed；Global 入口默认此值。通用入口须显式提供并校验。 |
| accessToken | string | 与 storeKey 二选一 | Temu 店铺令牌，实际网关请求必须携带。 |
| storeKey | string | 仅脚本，与 accessToken 二选一 | 先从本地令牌存储解析为 accessToken，不发送 storeKey。 |
| tokenPurpose | string | 否，仅脚本 | Global 下载默认 order-shipping；用于本地令牌选择。 |
| url | string | 是 | 从面单文档接口返回的加签资源链接，保留原链接及查询串，不自行重编码或删签名。 |
| token / linkfoxToken / linkfox_token | string | 否，仅脚本 | LinkFox 密钥兼容别名，优先于环境变量。 |
| --inline | CLI flag | 否 | 全量输出，仍保存完整 JSON。 |
| --no-cache | CLI flag | 否 | 不读取或写入响应缓存，公共 run 始终附加此参数。 |

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 若返回，按公共规则判断。 |
| errmsg | string | 若返回，保留原始错误消息。 |
| code | integer | 网关错误码：1002 参数或 Token 无效；1003 转发失败。 |
| body | string | 网关返回的原始文件协议数据，按实际返回读取；不预设更细字段或假定为 JSON 业务对象。 |
| transportHttpStatus | integer / null | 脚本记录的 LinkFox HTTP 状态，连接失败为 null。 |
| 其他原始字段 | 原响应类型 | 原样保留网关实际返回的文件信息；字段名称、编码和下载路径按实际返回协议读取，不预设固定值。 |

脚本调用加签下载网关并保存/展示其完整 JSON，未实现把响应解码为本地 PDF/PNG，不将 JSON 落盘误报为面单二进制文件已保存。只有实际返回文件内容或地址后才能按返回协议处理，不补造字段。本接口不运行 Temu body 的嵌套 JSON 解析。

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- code=1002 时核对参数与 LinkFox Token；code=1003 时核对 Temu token、用途、白名单与转发错误。
- 文件下载业务错误与二进制协议以实际网关返回为准，不预设专属业务码或编码；HTTP 或网关失败时保留完整消息。

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
  "skillName": "linkfox-temu-fulfillment-global",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
