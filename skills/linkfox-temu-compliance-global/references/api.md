# Temu 全球站商品合规 接口说明

除 Feedback 外共 10 个接口：9 个已定义的合规操作与 1 个文件下载接口。通用代理和 Token 探测复用已有端点，不额外计数。Temu 操作由 Body.type 标识，type 不是 URL 路径。

| 接口 | 端点 | 接口文档 | 对应脚本 | 说明 |
|---|---|---|---|---|
| 待上传资质项查询（`bg.arbok.open.cert.queryNeedUploadItems`） | POST `/temu/proxy` -> 上游 path：`/openapi/router`，Body `type=bg.arbok.open.cert.queryNeedUploadItems` | [apis/bg-arbok-open-cert-query-need-upload-items.md](apis/bg-arbok-open-cert-query-need-upload-items.md) | `scripts/global_compliance_arbok_cert_query_need_upload_items.py` | 待上传资质项查询。 |
| 上传商品资质（`bg.arbok.open.cert.uploadProductCert`） | POST `/temu/proxy` -> 上游 path：`/openapi/router`，Body `type=bg.arbok.open.cert.uploadProductCert` | [apis/bg-arbok-open-cert-upload-product-cert.md](apis/bg-arbok-open-cert-upload-product-cert.md) | `scripts/global_compliance_arbok_cert_upload_product_cert.py` | 上传商品资质。 |
| 商品资质查询（`bg.arbok.open.product.cert.query`） | POST `/temu/proxy` -> 上游 path：`/openapi/router`，Body `type=bg.arbok.open.product.cert.query` | [apis/bg-arbok-open-product-cert-query.md](apis/bg-arbok-open-product-cert-query.md) | `scripts/global_compliance_arbok_product_cert_query.py` | 商品资质查询。 |
| 合规文件上传（`bg.arbok.open.upload.uploadFile`） | POST `/temu/proxy` -> 上游 path：`/openapi/router`，Body `type=bg.arbok.open.upload.uploadFile` | [apis/bg-arbok-open-upload-upload-file.md](apis/bg-arbok-open-upload-upload-file.md) | `scripts/global_compliance_arbok_upload_upload_file.py` | 合规文件上传。 |
| 合规编辑（`bg.compliance.edit`） | POST `/temu/proxy` -> 上游 path：`/openapi/router`，Body `type=bg.compliance.edit` | [apis/bg-compliance-edit.md](apis/bg-compliance-edit.md) | `scripts/global_compliance_edit.py` | 合规编辑。 |
| 合规模板元数据查询（`bg.compliance.metadata.get`） | POST `/temu/proxy` -> 上游 path：`/openapi/router`，Body `type=bg.compliance.metadata.get` | [apis/bg-compliance-metadata-get.md](apis/bg-compliance-metadata-get.md) | `scripts/global_compliance_metadata_get.py` | 合规模板元数据查询。 |
| 实拍图上传（Flash）（`bg.flash.open.upload.real.image`） | POST `/temu/proxy` -> 上游 path：`/openapi/router`，Body `type=bg.flash.open.upload.real.image` | [apis/bg-flash-open-upload-real-image.md](apis/bg-flash-open-upload-real-image.md) | `scripts/global_compliance_flash_upload_real_image.py` | 实拍图上传（Flash）。 |
| 上传识别（Flash）（`bg.flash.open.upload.recognize`） | POST `/temu/proxy` -> 上游 path：`/openapi/router`，Body `type=bg.flash.open.upload.recognize` | [apis/bg-flash-open-upload-recognize.md](apis/bg-flash-open-upload-recognize.md) | `scripts/global_compliance_flash_upload_recognize.py` | 上传识别（Flash）。 |
| 合规标签查询（`bg.goods.compliancelabel.get`） | POST `/temu/proxy` -> 上游 path：`/openapi/router`，Body `type=bg.goods.compliancelabel.get` | [apis/bg-goods-compliancelabel-get.md](apis/bg-goods-compliancelabel-get.md) | `scripts/global_compliance_goods_compliancelabel_get.py` | 合规标签查询。 |
| 加签文件下载 | POST `/temu/fileDownload` | [api.md](api.md) | `scripts/temu_global_file_download.py` / `scripts/temu_file_download.py` | 下载 Temu 加签资源。 |

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

## 接口：加签文件下载（fileDownload）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/fileDownload`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| site | string | 是 | Global 下载入口默认 global；通用下载入口必须显式传入 cn / partner / us / global / eu 之一。 |
| managementType | string | 是 | Global 入口默认 semi-managed；通用入口显式传入 full-managed / semi-managed。 |
| accessToken | string | 与 storeKey 二选一 | Temu 店铺令牌；脚本优先使用直接传入值。 |
| storeKey | string | 与 accessToken 二选一 | 脚本本地取 token 的键，不转发。 |
| tokenPurpose | string | 否 | Global 入口默认 product-inventory；通用入口默认 default，用于本地定位，不转发。 |
| token / linkfoxToken / linkfox_token | string | 否 | 仅脚本认证别名，依次优先于环境密钥，设置同值 Authorization + Token 头，不转发为 Body。 |
| url | string | 是 | 非空的 Temu 加签资源 URL；原样转发，保留 URL 编码与签名。 |

认证别名、根地址覆盖和 CLI 参数见下方运行约定。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 若返回，按公共规则判断。 |
| errmsg | string | 若返回，保留实际消息。 |
| code | integer | 若返回 1002 / 1003，分别表示参数/Token 问题或转发失败。 |
| body | string | 网关响应内容；下载接口的文件表示、其他字段和嵌套结构未单独定义，以实际 JSON 响应为准，不虚构下载结果。下载脚本不添加 temuBody。 |

### 脚本本地附加字段

| 字段 | 类型 | 说明 |
|------|------|------|
| _http_status | integer / null | 业务封装记录的实际 HTTP 状态码；连接失败未收到响应时为 null。随完整响应保存，不是文件下载接口的业务字段；HTTP 401 / 402 按认证与算力指引处理。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 核对返回中的实际文件或错误信息；不能仅凭 HTTP 成功就声称文件已保存。此入口返回并保存网关 JSON，不自行下载二进制文件。
- code=1002 时核对参数与 Token，code=1003 时检查 Temu token、白名单与转发错误。签名过期等未枚举错误按实际消息处理。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/temu/fileDownload" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Token: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"site":"global","managementType":"semi-managed","accessToken":"TOKEN","url":"https://example.com/signed-file-url"}'
```

## 脚本兼容与运行约定

### 认证、路由与本地令牌

- LinkFox Token 优先从 JSON 的 `token`、`linkfoxToken`、`linkfox_token` 按此顺序取非空值，再读 `LINKFOX_AGENT_API_KEY` / `LINKFOXAGENT_API_KEY`。请求同时发送同值 `Authorization` 和 `Token`；Temu accessToken 是另一套令牌。
- 网关根地址优先级为 `LINKFOX_TOOL_GATEWAY`、`TEMU_API_BASE_URL`、`STORE_API_BASE_URL`、`https://tool-gateway.linkfox.com`，去掉末尾斜杠；保留根地址中已有的路径前缀。
- Global 脚本将 site、managementType 去空白并转小写；通用入口校验小写枚举。显式 accessToken 优先于 storeKey；storeKey 按 site、managementType、tokenPurpose 精确查找。
- 本地令牌默认为 `~/.linkfox/temu-access-tokens.json`，可用 `TEMU_TOKEN_STORE_PATH` 覆盖。按 storeKey 分店铺，同站点、托管类型和用途组合重复保存时替换并更新时间；列表默认脱敏，`mask=false` 可显示原值。令牌存储不是接口响应缓存。
- Temu 无 LinkFox 自动 OAuth；主账号在对应站点后台手动授权、复制 token。多站点分别授权，过期后重新保存，并配置紫鸟开放平台 IP 白名单。应用选择、后台路径与四类店铺规则见 [授权说明](access-token.md) 和 [授权流程](authorization-flow.md)。Global 合规默认用途不因通用授权指南推荐 cn / partner 而自动改变。

### CLI 与输出

| 参数 / 入口 | 类型 | 说明 |
|------|------|------|
| `<JSON 参数>` | JSON object | 业务入口接受首个 JSON 参数；缺参数或非法 JSON 报错退出。业务操作脚本接受顶层 request 或 params.request，后者优先。 |
| `--inline` | CLI flag | 强制输出完整响应；仍保存文件。 |
| `--no-cache` | CLI flag | 兼容通用命令行；脚本不启用响应缓存，业务封装调用公共 run 时始终传入，任何操作均不读写响应缓存。公共调用器可能建立空缓存目录，不代表启用缓存。 |
| `temu_global_proxy.py` | CLI | 必填 type，默认 Global 路由，保留任意 type + params 透传；不因此扩展本技能业务范围。 |
| `temu_proxy.py` | CLI | 通用代理，显式 site、managementType、type；params 如非空必须为对象。 |
| `temu_global_file_download.py` | CLI | 默认 Global 加签文件下载。 |
| `temu_file_download.py` | CLI | 通用文件下载，显式 site、managementType。 |
| `check_linkfox_token.py` | CLI | 可无 JSON 或传认证 JSON；以 `/temu/proxy` 的 `site=cn`、`managementType=full-managed`、`accessToken=probe`、`type=probe` 探测。HTTP 401 或消息含“无法识别当前用户”/“重新登录”时报告认证错误；连接失败或其他非 2xx 响应时报告请求失败，并保留完整 response（含本地 _http_status 与错误原因）。仅 HTTP 2xx 且未识别到认证错误时返回 ok=true，表示本次探测未发现该类错误，不能据此证明实际业务权限或 Temu token 可用；它会请求网关，本地验证不得真实运行探测。 |
| `temu_token_guide.py` | CLI | 必填 shopType（或 managementType），读取 tokenPurpose、site；本地输出授权步骤，无网络。 |
| `save_temu_access_token.py` | CLI | 必填 storeKey、site、managementType、accessToken；可传 tokenPurpose、label，仅本地写入。 |
| `get_temu_access_token.py` | CLI | 必填 storeKey、site、managementType；可传 tokenPurpose；找到时输出原 token，未找到返回 found=false 并退出 1。 |
| `list_temu_access_tokens.py` | CLI | 无参数默认 mask=true，支持 JSON mask 选项，仅本地读取。 |

- 脚本不读写接口响应缓存；失败或空结果不自动重试，写操作不依赖缓存规避重复提交。
- 业务封装适配参数、双头认证、timeout（默认 150s）与 body 解析，HTTP 传输统一通过公共调用器 call_api.py 的 run；请求前检查实际会话 data 目录可写，响应保存失败时报错且不自动重试。onboarding.py 是公共认证与算力引导资源，按其自身约定运行。
- 完整响应保存在当前工作目录的 linkfox 会话路径；禁止写入 /tmp，当前目录不可写时报错。保留微秒文件名避免连续调用互相覆盖；同一任务由 SESSION_ID 聚合。
- 代理输出保留原 body，并补充 temuBody；仅落盘一次。短响应全量输出，超过 8000 字节输出摘要，--inline 强制全量。空 HTTP 错误体返回 details 空字符串。鉴权探测直接输出结果，不额外展示公共调用器的响应日志。

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-temu-compliance-global",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
