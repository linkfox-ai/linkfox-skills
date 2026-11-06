# Temu 欧洲站退货与退款 接口说明

9 个售后操作与 1 个下载操作；通用代理与专用 CLI 不重复计数，公共 onboarding 辅助能力不计为本技能业务接口。

| 操作 | 端点与转发标识 | 接口文档 |
|------|------|------|
| 子售后单列表查询 | POST `/temu/proxy` → Body.type：`bg.aftersales.aftersales.list.get` | [bg.aftersales.aftersales.list.get](apis/bg-aftersales-aftersales-list-get.md) |
| 父售后单列表查询 | POST `/temu/proxy` → Body.type：`bg.aftersales.parentaftersales.list.get` | [bg.aftersales.parentaftersales.list.get](apis/bg-aftersales-parentaftersales-list-get.md) |
| 父退货物流信息 | POST `/temu/proxy` → Body.type：`bg.aftersales.parentreturnorder.get` | [bg.aftersales.parentreturnorder.get](apis/bg-aftersales-parentreturnorder-get.md) |
| 承运商列表 | POST `/temu/proxy` → Body.type：`temu.aftersales.carrier.get` | [temu.aftersales.carrier.get](apis/temu-aftersales-carrier-get.md) |
| 父售后单详情 | POST `/temu/proxy` → Body.type：`temu.aftersales.parentaftersales.detail.get` | [temu.aftersales.parentaftersales.detail.get](apis/temu-aftersales-parentaftersales-detail-get.md) |
| 退货地址查询 | POST `/temu/proxy` → Body.type：`temu.aftersales.returnaddress.get` | [temu.aftersales.returnaddress.get](apis/temu-aftersales-returnaddress-get.md) |
| 退货面单准备信息 | POST `/temu/proxy` → Body.type：`temu.aftersales.returnlabel.prepare.get` | [temu.aftersales.returnlabel.prepare.get](apis/temu-aftersales-returnlabel-prepare-get.md) |
| 售后签名获取 | POST `/temu/proxy` → Body.type：`temu.aftersales.signature.get` | [temu.aftersales.signature.get](apis/temu-aftersales-signature-get.md) |
| 上传退货面单 | POST `/temu/proxy` → Body.type：`temu.aftersales.upload.returnlabel` | [temu.aftersales.upload.returnlabel](apis/temu-aftersales-upload-returnlabel.md) |
| 加签文件下载 | POST `/temu/fileDownload` | [本页](#接口加签文件下载filedownload) |

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


## 认证兼容与脚本运行约定

- LinkFox 根地址按 `LINKFOX_TOOL_GATEWAY`、`TEMU_API_BASE_URL`、`STORE_API_BASE_URL` 的顺序取首个非空值，默认 `https://tool-gateway.linkfox.com`；去除末尾斜线。EU 上游为 `https://openapi-b-eu.temu.com/openapi/router`，由网关按 site 转发，脚本不直接请求上游。
- 除公共 Authorization 外，Temu 请求保留同值 Token 请求头；JSON `token` / `linkfoxToken` / `linkfox_token` 优先于环境密钥，SESSION_ID、MESSAGE_ID、MODE_ID、APP_NAME 转发为请求头。
- 所有业务入口均经 `call_api.run` 且强制 `--no-cache`，不读写响应缓存；公共调用器可能创建空 `.cache` 目录。需要复用数据时读取已保存的会话响应文件。
- 业务响应必须保存在 cwd 的 linkfox 会话目录，请求前检查实际目标文件可写性，不可写则报错；公共调用器与业务加工复用同一响应文件及会话元数据，禁止回退到家目录或临时目录。响应原始 body 与脚本 temuBody 保存到同一文件，保留大响应摘要和 --inline；多站点通用 CLI 可用，只在用户明确指定相应站点时使用。
- `check_linkfox_token.py '[JSON]'` 使用最小参数探测（site=cn、managementType=full-managed、accessToken=probe、type=probe），不是独立售后接口或实际售后操作；它会发网关请求，仅在确有认证诊断需要时使用。HTTP 或 errcode 未正常响应、明确认证失败、网关 code=1002/1003 或 error 均返回 ok=false；1002 可能表示参数或 Token 无效，不能据此确认凭据有效。探测不验证 Temu 店铺令牌。
- 网关 1002 表示参数或 LinkFox Token 无效；1003 表示转发失败，核对 Temu token、tokenPurpose、白名单和网络。401/402 与余额问题按 [onboarding.md](onboarding.md)；其他错误保留实际响应，不自动翻页、改条件或重试写入。
- Temu 手动授权、应用名称、主子账号、多站点授权、IP 白名单和本地令牌 CLI 见 [access-token.md](access-token.md) 与 [authorization-flow.md](authorization-flow.md)。通用 CLI 默认 tokenPurpose=default；EU 专用 CLI 用 storeKey 时默认 order-shipping，按店铺、站点、经营类型和用途精确匹配，禁止误用其他店铺或用途的令牌。

### 辅助本地 CLI 字段

| 脚本 | 参数 | 类型 / 必填 / 默认 | 说明 |
|------|------|------|------|
| check_linkfox_token.py | token / linkfoxToken / linkfox_token | string，否 | 同业务脚本的密钥优先级，输出密钥脱敏。 |
| temu_token_guide.py | shopType / managementType | string，是 | 优先 shopType，兼容 managementType；semi-managed / full-managed / local-native。 |
| temu_token_guide.py | tokenPurpose | string，否，default | product-inventory / order-shipping / full-managed / local-native / default。 |
| temu_token_guide.py | site | string，否 | 按店铺类型和用途返回推荐站点；EU 任务显式选 eu。 |
| save_temu_access_token.py | storeKey、site、managementType、accessToken | string，是 | site 与 managementType 小写，枚举同接口表。 |
| save_temu_access_token.py | tokenPurpose、label | string，否 | 用途默认 default；label 为店铺显示名称，默认 storeKey。 |
| get_temu_access_token.py | storeKey、site、managementType | string，是 | 精确匹配本地令牌，tokenPurpose 可选且默认 default。 |
| list_temu_access_tokens.py | mask | boolean，否，true | 默认脱敏，显式 false 可查看本地原令牌。 |

保存令牌时相同 storeKey + site + managementType + tokenPurpose 覆盖旧值，不同用途与站点分别保留；保存结果包含 storePath、updatedAt、replaced，读取缺失返回 found=false，列表默认脱敏。以上本地保存、读取与授权步骤输出不请求业务网关。

## 接口：加签文件下载（fileDownload）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/fileDownload`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| site | string | 是 | EU 包装默认 eu；多站点通用脚本显式提供 cn / partner / us / global / eu。 |
| managementType | string | 是 | EU 包装默认 semi-managed；通用脚本显式提供 full-managed / semi-managed。 |
| accessToken | string | 是 | Temu 店铺令牌；脚本也可用 storeKey 解析后填入。 |
| url | string | 是 | 需要加签下载的 Temu 资源 URL，非空；保留原值，不自行增加编码或改写签名。 |

#### 脚本专用参数

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| storeKey | string | 与 accessToken 二选一 | 本地店铺令牌键；同时提供时优先 accessToken。 |
| tokenPurpose | string | 否 | EU 包装用本地令牌默认 order-shipping，多站点通用脚本默认 default。 |
| token / linkfoxToken / linkfox_token | string | 否 | 按顺序优先于 LINKFOX_AGENT_API_KEY / LINKFOXAGENT_API_KEY，仅用于 Authorization + Token 请求头。 |
| --inline | CLI flag | 否 | 完整打印并保存响应。 |
| --no-cache | CLI flag | 否 | 封装始终传入公共 run，禁用响应缓存。 |

脚本分别为 `scripts/temu_eu_file_download.py` 与 `scripts/temu_file_download.py`；storeKey、tokenPurpose、LinkFox 密钥不进入网关 Body。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 若返回，按公共规则判断。 |
| errmsg | string | 若返回，保留网关消息。 |
| code | integer | 网关错误码 1002（参数或 Token）/ 1003（转发失败）。 |
| body | string | 若返回，原样保存；下载业务体字段以实际响应为准，脚本不自行解析或补造下载字段。 |
| transportHttpStatus | integer / null | 脚本记录 LinkFox 外层 HTTP 状态码；连接失败时为 null。 |

下载脚本接收并保存网关 JSON 响应，不直接保存二进制素材。下载结果的其他字段以实际响应为准，不能把未知字段假定为本地文件路径。

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

保留原始网关 JSON 与错误信息；code=1002 / 1003 依上方运行约定处理，不能将 HTTP 成功直接解释为文件已下载到本地。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/temu/fileDownload" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Token: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"site":"eu","managementType":"semi-managed","accessToken":"TOKEN","url":"https://example.com/signed-label.pdf"}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-temu-returns-refunds-eu",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
