# Temu 欧洲站电商税务 接口说明

本技能定义 7 个税务 type 和 1 个加签下载接口。各税务操作独立定义请求与响应，见 [税务接口索引](apis/README.md)；Partner 标识见 [目录](partner-eu-catalog.md)。

| 接口 | 文档 |
|------|------|
| 申请导出税务报表 | [temu-pay-tax-apply-export-report.md](apis/temu-pay-tax-apply-export-report.md) |
| 获取 Galerie 签名 | [temu-pay-tax-get-galerie-signature.md](apis/temu-pay-tax-get-galerie-signature.md) |
| 发票明细查询 | [temu-pay-tax-invoice-detail-query.md](apis/temu-pay-tax-invoice-detail-query.md) |
| 发票信息查询 | [temu-pay-tax-invoice-info-query.md](apis/temu-pay-tax-invoice-info-query.md) |
| 发票 PDF 下载 | [temu-pay-tax-invoice-pdf-download.md](apis/temu-pay-tax-invoice-pdf-download.md) |
| 商家税务报表下载 | [temu-pay-tax-merchant-report-download.md](apis/temu-pay-tax-merchant-report-download.md) |
| 商家上传发票 | [temu-pay-tax-merchant-upload-invoice.md](apis/temu-pay-tax-merchant-upload-invoice.md) |
| 加签文件下载 | 本文件“接口：加签文件下载” |

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

## 运行与认证约定

### 网关与授权

| 项目 | 约定 |
|------|------|
| 网关基础地址 | `LINKFOX_TOOL_GATEWAY` 优先，其次 `TEMU_API_BASE_URL`、`STORE_API_BASE_URL`，默认 `https://tool-gateway.linkfox.com`；移除末尾斜杠。 |
| LinkFox 密钥 | 脚本 JSON `token` → `linkfoxToken` → `linkfox_token` → 环境变量 `LINKFOX_AGENT_API_KEY` → `LINKFOXAGENT_API_KEY`；空 JSON 密钥跳过。 |
| 兼容请求头 | 在公共请求头之外保留 `Token`，与 `Authorization` 同值；保留 SESSION_ID / MESSAGE_ID / MODE_ID / APP_NAME。 |
| EU 默认值 | `site=eu`、`managementType=semi-managed`、`tokenPurpose=product-inventory`；Partner 指定其他用途时遵循对应文档。 |
| 上游 EU 地址 | `https://openapi-b-eu.temu.com/openapi/router`，由网关选择；不是直接请求地址。 |
| 上游转发 path | `/temu-proxy/{site}/{managementType}`；税务操作通过 Body `type` 区分，没有独立 URL path。 |
| 本地令牌 | 默认 `~/.linkfox/temu-access-tokens.json`，可用 `TEMU_TOKEN_STORE_PATH` 覆盖；以 storeKey + site + managementType + tokenPurpose 精确匹配。 |
| 响应缓存 | 不启用响应缓存；所有业务封装调用 `call_api.run` 时固定加 `--no-cache`，不读取也不写入响应缓存。创建空缓存目录不表示缓存了响应。 |
| 落盘 | 当前目录下 `linkfox/<YYYY-MM-DD>/<session>/data/linkfox-temu-tax-eu-<接口标识>-<timestamp>.json`；保留微秒时间戳。当前目录不可写时请求前报错，不回退至临时目录。 |

### CLI 与本地工具

| 脚本 | 参数及行为 |
|------|------------|
| `scripts/eu_tax_*.py` | 绑定对应 type；JSON + 可选 --inline / --no-cache；支持业务字段置顶或嵌套 params。 |
| `scripts/temu_eu_proxy.py` | 接收 type，保留 EU 默认值和顶层业务字段提取；params 对象优先。 |
| `scripts/temu_eu_file_download.py` | EU 默认参数，接收 accessToken 或 storeKey 以及 url。 |
| `scripts/temu_proxy.py` | 通用 CLI；显式提供 site、managementType、type；params 必须为对象或 null，业务参数只取 params。 |
| `scripts/temu_file_download.py` | 通用 CLI；显式提供 site、managementType、url。 |
| `scripts/check_linkfox_token.py` | 可选 JSON 密钥，使用最小 probe 请求检查网关鉴权；会发起真实网关请求，不属于纯本地检测。 |
| `scripts/temu_token_guide.py` | JSON 中 shopType（兼容 managementType）、tokenPurpose、site；仅输出手动授权步骤。 |
| `scripts/save_temu_access_token.py` | JSON 中 storeKey、site、managementType、accessToken 必填，tokenPurpose 默认 default、label 可选；同组合替换，否则追加。 |
| `scripts/get_temu_access_token.py` | JSON 中 storeKey、site、managementType 必填，tokenPurpose 默认 default；找到返回 found=true 和 accessToken，未找到退出 1。 |
| `scripts/list_temu_access_tokens.py` | 可不带参数；JSON mask 默认 true，false 时显式展示原令牌。 |

授权入口、后台应用、主账号、多站点、有效期和 IP 白名单要求见 [access-token.md](access-token.md)；[authorization-flow.md](authorization-flow.md) 保留完整授权决策表。
通用本地授权工具默认 tokenPurpose=default，与 EU 调用封装的 product-inventory 不同；保存 EU 税务令牌时应显式指定用途。

## 接口：加签文件下载

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/fileDownload`

### 请求参数

#### 网关 POST Body

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| site | string | 是 | EU 封装默认 eu；通用脚本支持 cn / partner / us / global / eu，须小写。 |
| managementType | string | 是 | EU 封装默认 semi-managed；通用脚本支持 full-managed / semi-managed，须小写。 |
| accessToken | string | 是 | Temu 店铺令牌；脚本支持从 storeKey 精确查找后填入。 |
| url | string | 是 | 待下载的加签资源 URL；按原始 URL 传入，保留查询串及其编码。 |

#### 脚本参数与选项

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| token / linkfoxToken / linkfox_token | string | 否 | LinkFox 用户密钥，优先顺序见运行与认证约定；不转发到业务 Body。 |
| accessToken | string | 与 storeKey 二选一 | 直接传入优先。 |
| storeKey | string | 与 accessToken 二选一 | 本地店铺键。 |
| site | string | 否 / 通用脚本必填 | EU 封装默认 eu，去空白并转小写。 |
| managementType | string | 否 / 通用脚本必填 | EU 封装默认 semi-managed，去空白并转小写。 |
| tokenPurpose | string | 否 | EU 封装默认 product-inventory，仅供本地令牌选择；通用脚本默认 default。 |
| url | string | 是 | 资源 URL。 |
| --inline | CLI flag | 否 | 强制全量打印，仍落盘。 |
| --no-cache | CLI flag | 否 | 封装始终禁用响应缓存。 |

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 网关业务状态，按公共规则处理。 |
| errmsg | string | 网关响应消息。 |
| code | integer | 网关错误码：1002 参数或 Token 问题、1003 转发失败。 |
| body | string | 网关透传内容；文件下载响应内部结构未定义，按实际返回解析，不补造文件字段。 |

#### 脚本本地附加字段

| 字段 | 类型 | 说明 |
|------|------|------|
| _linkfoxHttpStatus | integer / null | 实际 HTTP 状态；连接失败为 null。仅由脚本记录，不是网关字段；按此状态执行 401 / 402 等处理。 |
| _rawGatewayResponse | array / scalar / null | 仅当网关响应不是 JSON 对象时，由脚本保存原始 JSON 值；此时不据此宣称文件下载成功。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- code=1002 时核对请求参数、LinkFox 用户密钥和店铺令牌；code=1003 时核对 Temu 令牌、IP 白名单和转发情况。
- 保留真实网关返回；资源链接和下载成功分别展示，不把未知响应结构直接解释成已下载文件。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/temu/fileDownload" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Token: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '
{
  "site": "eu",
  "managementType": "semi-managed",
  "accessToken": "TOKEN",
  "url": "https://example.com/signed-file?signature=SIGNED"
}'
```

---

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-temu-tax-eu",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
