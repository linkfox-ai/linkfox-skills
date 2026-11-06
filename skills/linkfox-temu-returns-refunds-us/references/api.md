# Temu 美国站退货与退款 接口说明

已定义 10 项操作：9 项 Partner 售后操作和加签文件下载。通用代理是这些操作的调用入口，不重复计数；认证与计费引导为公共基础设施。

| 操作 | 接口文档 |
|------|------|
| `bg.aftersales.aftersales.list.get` | [子售后单列表查询](apis/bg-aftersales-aftersales-list-get.md) |
| `bg.aftersales.parentaftersales.list.get` | [父售后单列表查询](apis/bg-aftersales-parentaftersales-list-get.md) |
| `bg.aftersales.parentreturnorder.get` | [父退货物流信息](apis/bg-aftersales-parentreturnorder-get.md) |
| `temu.aftersales.carrier.get` | [承运商列表](apis/temu-aftersales-carrier-get.md) |
| `temu.aftersales.parentaftersales.detail.get` | [父售后单详情](apis/temu-aftersales-parentaftersales-detail-get.md) |
| `temu.aftersales.returnaddress.get` | [退货地址查询](apis/temu-aftersales-returnaddress-get.md) |
| `temu.aftersales.returnlabel.prepare.get` | [退货面单准备信息](apis/temu-aftersales-returnlabel-prepare-get.md) |
| `temu.aftersales.signature.get` | [售后签名获取](apis/temu-aftersales-signature-get.md) |
| `temu.aftersales.upload.returnlabel` | [上传退货面单](apis/temu-aftersales-upload-returnlabel.md) |
| 加签文件下载 | [本文件](#接口加签文件下载) |

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

### 认证与网关兼容

- LinkFox 密钥与 Temu accessToken 是两套令牌；前者按 JSON `token`、`linkfoxToken`、`linkfox_token` 顺序优先，再取 `LINKFOX_AGENT_API_KEY`、`LINKFOXAGENT_API_KEY`。Authorization 与 Token 请求头必须同值，保留会话追踪头。
- 基础地址优先 `LINKFOX_TOOL_GATEWAY`，再取 `TEMU_API_BASE_URL`、`STORE_API_BASE_URL`，默认正式网关。业务脚本通过公共 `call_api.run` 调用，HTTP 默认超时 150 秒，业务封装支持传入 timeout。
- US 脚本默认 `site=us`、`managementType=semi-managed`；本地 Token 查找默认 `tokenPurpose=order-shipping`。US 封装先将站点和管理模式去除首尾空白并转为小写，再按相同值查找 Token 和转发请求；不改变店铺键或用途。通用多站点脚本要求显式站点与管理模式，本地用途默认 `default`。本地存储默认 `~/.linkfox/temu-access-tokens.json`，可用 `TEMU_TOKEN_STORE_PATH` 覆盖；按 storeKey、site、managementType、tokenPurpose 精确匹配，不切换店铺或其他用途兜底。
- Temu 无自动 OAuth，需在卖家后台手动复制 Token；授权应用、店铺类型、站点、IP 白名单和有效期见 [Token 授权说明](access-token.md) 与 [授权流程](authorization-flow.md)。

### CLI、缓存与输出

| 选项 / 行为 | 类型 | 约定 |
|------|------|------|
| JSON 参数 | object | 作为首个位置参数；适用于业务专用脚本、US 通用脚本、多站点脚本及本地 Token 工具。 |
| --inline | CLI flag | 强制打印全量 JSON，仍保存完整响应。 |
| --no-cache | CLI flag | 兼容公共 CLI；业务封装始终传入此项，禁用响应缓存。公共调用器可能创建空缓存目录，但不读写响应缓存文件。 |
| 输出位置 | path | 严格保存到 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-temu-returns-refunds-us-<timestamp>.json`；不回退 ACPX_WORKSPACES、家目录或临时目录。请求前检查根目录及实际会话 data 目录可写，不可写即报错。 |
| SESSION_ID | string | 优先按环境变量聚合同一会话；未配置则进程内生成。 |
| 摘要阈值 | integer | UTF-8 响应体不超过 8000 字节时全量输出；更大时输出顶层字段、常见计数、最大列表长度与前 3 条。 |
| 响应加工 | object | 先由公共调用器保存网关结果，业务脚本解析 body 后更新同一个文件，不生成第二份重复响应文件。HTTP 状态另保存在 transportHttpStatus，以实际 HTTP 状态为准，不接受响应体同名字段覆盖。 |

### 本地授权工具与鉴权探测

| 脚本 | CLI | 行为 |
|------|------|------|
| scripts/temu_token_guide.py | `'<JSON 参数>'` | shopType（或 managementType）、tokenPurpose、site；输出对应手动授权步骤，不请求网络。 |
| scripts/save_temu_access_token.py | `'<JSON 参数>'` | 必填 storeKey、site、managementType、accessToken；选填 tokenPurpose（默认 default）、label；同一组合覆盖保存。 |
| scripts/list_temu_access_tokens.py | `['<JSON 参数>']` | 默认 mask=true 脱敏，mask=false 显示原值。 |
| scripts/get_temu_access_token.py | `'<JSON 参数>'` | 必填 storeKey、site、managementType；tokenPurpose 默认 default；读取原值，找不到时退出 1。 |
| scripts/check_linkfox_token.py | `['<JSON 参数>']` | 通过 /temu/proxy 的 probe 请求校验 LinkFox 密钥；属于同一转发入口的鉴权辅助工具，不是额外售后操作；显式需要时才运行。 |

新增 Partner 操作时，以用户提供的 type、sub_menu_code、URL 和完整请求/响应表为依据，新增单独文档与调用 `_us_returns_refunds_script.run_cli` 的业务入口，并同步接口清单、[Partner 目录](partner-us-catalog.md) 和 [接口索引](apis/README.md)；不得把未知 type 描述为已接入。

## 接口：加签文件下载

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/fileDownload`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| site | string | 是 | 美国站默认 `us`；通用脚本支持 `cn`、`partner`、`us`、`global`、`eu`。US 封装会转小写，通用脚本要求小写。 |
| managementType | string | 是 | US 默认 `semi-managed`；通用脚本支持 `semi-managed`、`full-managed`，要求小写。 |
| accessToken | string | 与 storeKey 二选一 | Temu 店铺令牌；直接提供时优先于本地查找。 |
| storeKey | string | 与 accessToken 二选一 | 脚本本地选店键，按站点、管理模式和用途读取 Token，解析为 accessToken 后发送，不原样传网关。 |
| tokenPurpose | string | 否 | 本地 Token 用途；US 售后默认 `order-shipping`，多站点通用脚本默认 `default`；仅参与本地解析。 |
| url | string | 是 | 需要加签下载的资源 URL；保留原值，不擅自改写或截断查询串。 |
| token / linkfoxToken / linkfox_token | string | 否 | 仅脚本使用的 LinkFox 密钥兼容别名，不发送到 Temu 业务体。 |

脚本 `scripts/temu_us_file_download.py` 支持 US 默认；`scripts/temu_file_download.py` 要求显式 site 与 managementType。两者均先解析本地 Token，实际发送 site、managementType、accessToken、url；CLI 与无缓存约定见上方运行约定。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 按公共规则判断的 LinkFox 外层状态。 |
| errmsg | string | 网关错误说明（若返回）。 |
| body | string | 网关原始载荷（若返回）；下载脚本保留原值，不自动添加 temuBody。 |
| code | integer | 网关错误码：1002 参数或 Token 无效，1003 转发失败。 |
| transportHttpStatus | integer / null | 业务封装记录的外层 HTTP 状态，连接失败为 null。 |
| error | string | HTTP 或连接错误描述（若返回）。 |
| details | string | 非 JSON HTTP 错误原文（若返回）。 |

下载结果保留网关实际返回的全部字段，不假定固定的下载专属结果结构，不推断下载结果字段或将响应 JSON 当作文件二进制。

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- `code=1002` 时核对参数或 LinkFox Token；`code=1003` 时核对 Temu Token、用途、IP 白名单和资源链接，不自动连续重试。
- 保留网关下载响应，不能仅凭请求完成宣称文件已保存；如有 Temu 业务内容，按其实际错误信息解释。

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/temu/fileDownload" \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Token: $LINKFOXAGENT_API_KEY" \
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
  "skillName": "linkfox-temu-returns-refunds-us",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
