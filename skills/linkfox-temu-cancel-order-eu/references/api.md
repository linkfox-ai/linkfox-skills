# Temu 欧洲站取消订单接口说明

6 个取消业务操作经同一端点转发，加签文件下载为第 7 个操作；通用代理及令牌探测复用已列端点，不另计操作。上游网关为 `https://openapi-b-eu.temu.com/openapi/router`，由 LinkFox 按 site 解析。

| 操作 | 接口文档 |
|---|---|
| `bg.aftersales.cancel.list.get` | [apis/bg-aftersales-cancel-list-get.md](apis/bg-aftersales-cancel-list-get.md) |
| `bg.aftersales.cancel.agree` | [apis/bg-aftersales-cancel-agree.md](apis/bg-aftersales-cancel-agree.md) |
| `temu.order.cancel.appeal.apply` | [apis/temu-order-cancel-appeal-apply.md](apis/temu-order-cancel-appeal-apply.md) |
| `temu.order.cancel.appeal.result.get` | [apis/temu-order-cancel-appeal-result-get.md](apis/temu-order-cancel-appeal-result-get.md) |
| `temu.order.cancel.outofstock.apply` | [apis/temu-order-cancel-outofstock-apply.md](apis/temu-order-cancel-outofstock-apply.md) |
| `temu.order.cancel.outofstock.result.get` | [apis/temu-order-cancel-outofstock-result-get.md](apis/temu-order-cancel-outofstock-result-get.md) |
| `/temu/fileDownload` | 本文「接口：加签文件下载」 |

Partner 菜单与官方文档地址见 [partner-eu-catalog.md](partner-eu-catalog.md)；[授权流程](authorization-flow.md)、[本地令牌说明](access-token.md)、[接口索引](apis/README.md)。

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

| 项目 | 类型 / 默认 | 约定 |
|---|---|---|
| 网关环境变量 | string | 优先 `LINKFOX_TOOL_GATEWAY`，其次 `TEMU_API_BASE_URL`、`STORE_API_BASE_URL`，默认 `https://tool-gateway.linkfox.com`；去掉末尾斜杠。 |
| LinkFox 密钥 | string | JSON `token` / `linkfoxToken` / `linkfox_token` 按顺序优先，其后为 `LINKFOX_AGENT_API_KEY`、`LINKFOXAGENT_API_KEY`；头部 `Authorization` 与 `Token` 同值，保留会话追踪头。 |
| Temu accessToken | string | 用户在 Temu 后台手动授权复制，无自动 OAuth；与 LinkFox 密钥不同。直接令牌优先，否则按 storeKey、站点、托管类型和用途查本地保存值。 |
| EU 默认值 | string | `site=eu`、`managementType=semi-managed`、`tokenPurpose=order-shipping`。EU 脚本规范化站点及托管类型的小写；通用脚本显式填写并校验小写枚举。 |
| 令牌存储 | 本地 JSON | 默认 `~/.linkfox/temu-access-tokens.json`，可通过 `TEMU_TOKEN_STORE_PATH` 覆盖；按店铺键与三维场景隔离，默认列表脱敏，可显式 `mask=false`；同维度保存替换旧值。 |
| 业务提取 | object | EU 专用及 EU 通用代理先使用显式对象 params，否则提取除认证、站点、type、params 等保留键之外的顶层字段，保留 request 整体。通用 temu_proxy.py 只接受显式 params 对象。 |
| `--inline` | CLI flag | 强制完整打印，仍保存完整响应。 |
| `--no-cache` | CLI flag | 所有业务封装调用公共 run 时始终传此项，不读取或写入响应缓存；公共调用器仍会创建空的 .cache 目录。 |
| HTTP 超时 | integer / 150 秒 | 业务封装保留 timeout 参数，公共调用器负责实际 HTTP 传输；无自动重试。 |
| 输出 | JSON / 摘要 | 当前工作目录必须可写，请求前检查；不允许回退家目录或临时目录。每个操作保存到 SKILL.md 所述路径；微秒时间戳避免同秒重复调用覆盖。 |
| 令牌检查 | `check_linkfox_token.py` | 保留最小 probe 请求与脱敏输出；会访问网关，不是离线校验。兼容 message、error、errmsg 中的认证、用量及权限提示；未知业务错误码、网络或认证/用量失败不能报告有效，不作为必须预检步骤。 |

**本地 CLI**：`temu_token_guide.py` 输出授权步骤；`save_temu_access_token.py` 保存令牌；`list_temu_access_tokens.py` 默认脱敏列举；`get_temu_access_token.py` 读取精确场景令牌。支持全部已列脚本入口，`temu_eu_proxy.py` 用于已知定义的 type 透传，兼容 `temu_proxy.py` 与 `temu_file_download.py`。

授权需主账号具备服务市场权限；多站点分别授权，过期后重新复制保存，并联系紫鸟配置调用 IP 白名单。订单类半托管使用 Cyber-ERP酷鸟助手；商品/全托管使用酷鸟卖家助手；本土主体使用 Cyber-ERP，完整流程见授权文档。

**维护接入约定**：扩展时新增 `references/apis/<type-slug>.md`、调用 `_eu_cancel_order_script.run_cli` 的专用入口，并同步接口清单、[Partner 目录](partner-eu-catalog.md) 与 [接口索引](apis/README.md)。尚未接入的 `temu.order.query.signature` 仅为申诉图片的外部准备依赖，不计为本技能接口。

## 接口：加签文件下载

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/fileDownload`

### 请求参数

#### 网关 POST Body 与脚本认证参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| site | string | 是；EU 脚本可省略 | EU 脚本默认 `eu`；通用脚本需显式填写。通用兼容值 `cn` / `partner` / `us` / `global` / `eu`，须小写并与令牌区域一致。 |
| managementType | string | 是；EU 脚本可省略 | EU 脚本默认 `semi-managed`；通用脚本显式传入 `full-managed` / `semi-managed`，须小写。 |
| accessToken | string | 与 storeKey 二选一 | Temu 店铺令牌；直接提供时优先使用。不是 LinkFox 用户密钥。 |
| storeKey | string | 与 accessToken 二选一 | 脚本本地令牌键；按 site、managementType、tokenPurpose 读取后，仅把 accessToken 发给网关。 |
| tokenPurpose | string | 否 | EU 默认 `order-shipping`；通用脚本默认 `default`。令牌用途维度，仅供脚本本地解析。 |
| token / linkfoxToken / linkfox_token | string | 否 | 脚本 LinkFox 密钥兼容参数，按此顺序优先于环境变量；不进入业务载荷。 |
| url | string | 是 | Temu 加签资源 URL；须非空，脚本原样发送，不移除或重新编码签名查询参数。 |

此接口没有 type、params 或 request 业务块；`storeKey`、`tokenPurpose` 和 LinkFox 密钥参数只用于本地解析。兼容请求头 `Token` 与 `Authorization` 同值。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 网关状态（若返回），遵循公共规则。 |
| errmsg | string | 网关消息（若返回）。 |
| code | integer | 网关错误码 `1002` 参数或 Token 错误、`1003` 转发失败。 |
| transportHttpStatus | integer / null | 脚本附加的外层 HTTP 状态；连接失败为 null。 |
| 其他原始字段 | 以实际响应为准 | 下载成功载荷以网关实际返回为准；脚本保存并返回完整 JSON，不约定固定成功字段、字段类型或二进制落盘协议，不据此声称文件内容已保存。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 网关 `code=1002`：核对参数及 LinkFox 用户密钥；`code=1003`：核对 Temu 令牌、用途、IP 白名单和网络。按网关错误说明排查；本接口不约定 Temu 业务响应的嵌套结构。

- 此接口用于加签资源下载，保留网关原始响应；不根据一个未定义的下载字段判断文件已保存。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/temu/fileDownload" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Token: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "site": "eu",
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
  "skillName": "linkfox-temu-cancel-order-eu",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
