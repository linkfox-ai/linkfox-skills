# Temu 全球站退货与退款 接口说明

九项具名售后操作与一项加签文件下载；通用代理及 Token 校验复用现有入口，不另增业务操作。Temu 的 `type` 写在 Body，不作为 URL 路径。

| 操作 | 说明 | 接口文档 |
|---|---|---|
| `bg.aftersales.aftersales.list.get` | 子售后单列表查询 | [bg-aftersales-aftersales-list-get.md](apis/bg-aftersales-aftersales-list-get.md) |
| `bg.aftersales.parentaftersales.list.get` | 父售后单列表查询 | [bg-aftersales-parentaftersales-list-get.md](apis/bg-aftersales-parentaftersales-list-get.md) |
| `bg.aftersales.parentreturnorder.get` | 父退货物流信息 | [bg-aftersales-parentreturnorder-get.md](apis/bg-aftersales-parentreturnorder-get.md) |
| `temu.aftersales.carrier.get` | 承运商列表 | [temu-aftersales-carrier-get.md](apis/temu-aftersales-carrier-get.md) |
| `temu.aftersales.parentaftersales.detail.get` | 父售后单详情 | [temu-aftersales-parentaftersales-detail-get.md](apis/temu-aftersales-parentaftersales-detail-get.md) |
| `temu.aftersales.returnaddress.get` | 退货地址查询 | [temu-aftersales-returnaddress-get.md](apis/temu-aftersales-returnaddress-get.md) |
| `temu.aftersales.returnlabel.prepare.get` | 退货面单准备信息 | [temu-aftersales-returnlabel-prepare-get.md](apis/temu-aftersales-returnlabel-prepare-get.md) |
| `temu.aftersales.signature.get` | 售后签名获取 | [temu-aftersales-signature-get.md](apis/temu-aftersales-signature-get.md) |
| `temu.aftersales.upload.returnlabel` | 上传退货面单 | [temu-aftersales-upload-returnlabel.md](apis/temu-aftersales-upload-returnlabel.md) |
| `/temu/fileDownload` | 加签文件下载 | 本文「接口：加签文件下载」 |

授权见 [access-token.md](access-token.md)、[authorization-flow.md](authorization-flow.md)；Partner 来源见 [partner-global-catalog.md](partner-global-catalog.md)；文档索引见 [apis/README.md](apis/README.md)。

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

| 配置 / 行为 | 类型 | 说明 |
|---|---|---|
| LINKFOX_TOOL_GATEWAY | string | 最高优先级网关地址；缺省依次使用 TEMU_API_BASE_URL、STORE_API_BASE_URL、https://tool-gateway.linkfox.com。 |
| LINKFOX_AGENT_API_KEY / LINKFOXAGENT_API_KEY | string | 环境密钥，依次读取；请求 JSON 中 token、linkfoxToken、linkfox_token 依次优先于环境变量。 |
| Authorization / Token | HTTP header | 两者发送相同 LinkFox 用户密钥；勿混淆 Temu accessToken。会话头 SESSION_ID、MESSAGE_ID、MODE_ID、APP_NAME 保留。 |
| 超时 | integer | 默认 150 秒；保留 Python 调用 timeout 参数，不自动重试。 |
| 输出目录 | path | 业务封装强制当前工作目录 linkfox/<日期>/<session>/data；请求前检查可写，不回退家目录或 /tmp。微秒命名避免同秒响应覆盖。 |
| 响应缓存 | boolean | 所有业务请求通过 call_api.run 并始终 --no-cache，无第二层缓存。公共调用器可能创建空 .cache 目录，不读取或写入响应缓存文件。 |
| --inline | CLI flag | 小响应完整输出，大于 8000 字节默认摘要及前三条样本；加此选项完整输出，均保存原始 JSON。Python 调用 emit_result(result, inline=True) 也强制全量展示，不重复落盘。 |
| --no-cache | CLI flag | 兼容接收；本技能业务封装始终关闭响应缓存。 |
| --help | CLI flag | onboarding.py 支持；其余 JSON CLI 缺少参数时返回用法。 |

业务入口：`python scripts/<脚本名>.py '<JSON 参数>' [--inline] [--no-cache]`。Global 专用脚本默认 site=global、managementType=semi-managed、tokenPurpose=order-shipping；站点和托管类型去除首尾空白并转为小写，使用 `storeKey` 时也按相同值读取本地令牌。`storeKey` 按站点、托管类型、用途读取本地令牌，不把本地选择字段发送到网关。直接 accessToken 优先于 storeKey。

通用 Global 代理为 `scripts/temu_global_proxy.py`，多站点兼容代理为 `scripts/temu_proxy.py`；操作类型及业务结构以各独立文档为准。Global 入口存在对象 `params` 时使用它，否则移除认证与控制字段后转发顶层业务字段。专用脚本固定自身 type，不使用用户传入的其他 type。

### 本地授权与 Token CLI

下列脚本仅操作本地数据或输出引导，不构成新的 LinkFox 接口。Temu 无 LinkFox 自动 OAuth，应用名称、分店铺类型步骤、子账号限制、多站点授权、有效期与 IP 白名单见 [授权说明](access-token.md)。

| 脚本 | JSON 字段 | 行为 |
|---|---|---|
| `scripts/temu_token_guide.py` | shopType（必填，兼容 managementType）、tokenPurpose（默认 default）、site（可选） | 输出对应授权步骤；类型及用途枚举见授权说明。 |
| `scripts/save_temu_access_token.py` | storeKey、site、managementType、accessToken 必填；tokenPurpose 默认 default；label 可选 | 保存或替换同一店铺、站点、托管类型、用途组合的 Token。 |
| `scripts/list_temu_access_tokens.py` | mask 可选，默认 true | 默认脱敏列出；显式 mask=false 时显示原值。 |
| `scripts/get_temu_access_token.py` | storeKey、site、managementType 必填；tokenPurpose 默认 default | 返回 found 与 Token；不存在时 found=false，退出码 1。 |

Token 存储默认 `~/.linkfox/temu-access-tokens.json`，可由 `TEMU_TOKEN_STORE_PATH` 覆盖；这是店铺凭证存储，不是接口响应缓存。

### LinkFox Token 校验 CLI

`scripts/check_linkfox_token.py` 可不传 JSON 使用环境密钥，也支持三个请求密钥别名。它通过 `/temu/proxy` 发送 site=cn、managementType=full-managed、accessToken=probe、type=probe 的最小探测，不额外执行售后操作。身份被接受后可能返回参数类 code=1002；不能把连接错误、401/402、其他网关失败判为认证成功。

| 输出字段 | 类型 | 说明 |
|---|---|---|
| ok | boolean | Token 探测是否符合接受规则。 |
| linkfoxToken | string | 成功时为脱敏密钥。 |
| gatewayReachable | boolean | 仅表示收到了网关 HTTP 响应。 |
| note | string | 成功说明。 |
| reason | string | 失败原因，如 linkfox_token_invalid 或 gateway_probe_failed。 |
| message | string / object | 原始失败说明。 |
| hint | string | 配置指引。 |

## 接口：加签文件下载

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/fileDownload`

### 请求参数

| 参数 | 类型 | 必填 | 默认值 / 说明 |
|---|---|---|---|
| site | string | 是 | Global 专用脚本默认 global；多站点脚本须显式提供 cn / partner / us / global / eu，小写。 |
| managementType | string | 是 | Global 专用脚本默认 semi-managed；多站点脚本显式提供 full-managed / semi-managed，小写。 |
| accessToken | string | 与 storeKey 二选一 | Temu 令牌，直接请求网关时必填。 |
| storeKey | string | 与 accessToken 二选一 | 仅脚本本地选择店铺 Token，不发到网关。 |
| tokenPurpose | string | 否 | 仅本地选择用途，Global 专用脚本默认 order-shipping；多站点默认 default，不发到网关。 |
| url | string | 是 | 待下载的加签文件 URL，完整保留签名与编码，不自行拆分重编码。 |
| token / linkfoxToken / linkfox_token | string | 否 | 脚本兼容密钥别名，按顺序优先于环境变量；不发到业务 Body。 |
| --inline / --no-cache | CLI flag | 否 | 见上方运行约定，始终关闭响应缓存。 |

脚本为 `scripts/temu_global_file_download.py`（Global 默认值）及 `scripts/temu_file_download.py`（多站点显式参数）。网关 Body 仅包含 site、managementType、accessToken、url。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 若存在，按公共基础规则判断。 |
| errmsg | string | 若存在，为网关消息。 |
| code | integer | 网关兼容错误码：1002 参数或 Token 无效；1003 转发失败。 |
| body | string | 网关原始响应字段；下载脚本不添加 temuBody，不假设固定文件链接或二进制格式。 |
| transportHttpStatus | integer / null | 脚本记录的外层 HTTP 状态，连接失败为 null。 |

文件下载的业务返回以实际响应为准；保持真实响应字段，不杜撰下载链接或本地文件路径。该 CLI 保存网关 JSON，不代表已将 PDF 等二进制文件下载到本地。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- code=1002 时核对参数或 LinkFox Token；code=1003 时核对 Temu Token、用途、白名单和网络。按实际消息解释，不自动重试或修改文件 URL。

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
  "skillName": "linkfox-temu-returns-refunds-global",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
