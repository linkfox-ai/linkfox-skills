# Temu 欧洲站电商促销 接口说明

共 7 个业务接口：6 个促销操作共用 `/temu/proxy`，通过 `type` 选择操作；另有 `/temu/fileDownload`。上游为 `https://openapi-b-eu.temu.com/openapi/router`，调用方不直接请求上游。
促销请求与响应字段按接口独立维护：

| 接口 | 文档 |
|---|---|
| 促销活动查询（`bg.promotion.activity.query`） | [apis/bg-promotion-activity-query.md](apis/bg-promotion-activity-query.md) |
| 活动候选商品查询（`bg.promotion.activity.candidate.goods.query`） | [apis/bg-promotion-activity-candidate-goods-query.md](apis/bg-promotion-activity-candidate-goods-query.md) |
| 活动已报名商品查询（`bg.promotion.activity.goods.query`） | [apis/bg-promotion-activity-goods-query.md](apis/bg-promotion-activity-goods-query.md) |
| 活动商品报名（`bg.promotion.activity.goods.enroll`） | [apis/bg-promotion-activity-goods-enroll.md](apis/bg-promotion-activity-goods-enroll.md) |
| 活动商品操作结果查询（`bg.promotion.activity.goods.operation.query`） | [apis/bg-promotion-activity-goods-operation-query.md](apis/bg-promotion-activity-goods-operation-query.md) |
| 活动商品更新（`bg.promotion.activity.goods.update`） | [apis/bg-promotion-activity-goods-update.md](apis/bg-promotion-activity-goods-update.md) |

文件下载定义见本页；Partner 菜单与接入约定见 [partner-eu-catalog.md](partner-eu-catalog.md)。

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

### 认证与默认值

#### 脚本选项与认证

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| token / linkfoxToken / linkfox_token | string | 否 | LinkFox 密钥兼容别名，优先级按此顺序，高于环境变量；不会进入业务 params。 |
| --inline | CLI flag | 否 | 强制完整打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 接受该选项；业务封装始终向 call_api.run 传入 --no-cache，不读取或写入响应缓存。 |

网关环境变量优先级为 `LINKFOX_TOOL_GATEWAY` → `TEMU_API_BASE_URL` → `STORE_API_BASE_URL` → 默认网关；密钥环境变量优先 `LINKFOX_AGENT_API_KEY`，其次 `LINKFOXAGENT_API_KEY`。网关请求发送同值 `Authorization` 与 `Token` 请求头。

欧洲站促销封装默认 site=eu、managementType=semi-managed；storeKey 查找默认 tokenPurpose=product-inventory。site 和 managementType 会去除空白并转小写，空串回退默认值；显式传入的非欧洲站值仍保留兼容，但本技能业务范围为 EU。
通用 temu_proxy.py / temu_file_download.py 要求显式提供 site 与 managementType，并校验站点枚举 cn / partner / us / global / eu 及托管枚举 full-managed / semi-managed；tokenPurpose 默认 default。
欧洲站代理和下载均先规范化 site 与 managementType，再使用相同值查找 storeKey；显式提供 tokenPurpose 时同样补齐区域和托管默认值。调用方输入不被改写。

### CLI、缓存与输出

所有业务入口支持 `python scripts/<脚本名>.py '<JSON 参数>' [--inline] [--no-cache]`。六个专用入口固定 type，temu_eu_proxy.py 接受任意 type；本技能仅维护上列六个操作的字段，不假定其他操作可用。
全部业务封装调用 call_api.run 时始终传入 --no-cache；查询、写入和下载均不读取或写入响应缓存，公共调用器可能创建空的 `.cache` 目录。
完整响应只保存一次，先解析可解析的 body 为 temuBody，再落盘；原始 body 与网关字段保留，追加 transportHttpStatus。按接口标识区分文件，并使用微秒时间戳避免同秒覆盖。
输出根目录固定 `<cwd>/linkfox`；业务请求前检查可写性，失败即报错，不回退家目录或临时目录。超过 8 KB 默认展示摘要，--inline 强制全量输出；`SESSION_ID` 聚合同一会话。`SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 继续随请求头传递。

### 本地授权辅助 CLI

Temu 无 LinkFox 侧自动 OAuth。授权与用途说明见 [access-token.md](access-token.md)、[authorization-flow.md](authorization-flow.md)。以下命令仅操作本地文件或输出授权指引：

| 脚本 | JSON 参数 | 输出与行为 |
|---|---|---|
| temu_token_guide.py | shopType（或 managementType）、tokenPurpose、site | 输出按店铺类型与用途生成的授权步骤；shopType 必填，tokenPurpose 默认 default。支持 semi-managed / full-managed / local-native；用途支持 product-inventory / order-shipping / full-managed / local-native / default。 |
| save_temu_access_token.py | storeKey、site、managementType、accessToken 必填；tokenPurpose、label 可选 | 默认 tokenPurpose=default；按 storeKey + site + managementType + tokenPurpose 新增或覆盖，输出 storeKey、site、managementType、tokenPurpose、storePath、updatedAt、replaced。 |
| list_temu_access_tokens.py | 可选对象，mask 默认 true | 列出 stores，包括 storeKey、label、tokens；令牌项含 site、managementType、tokenPurpose、accessToken、updatedAt。长令牌显示前 6 / 后 4 位，短令牌显示 ***；mask=false 时返回原值。 |
| get_temu_access_token.py | storeKey、site、managementType 必填；tokenPurpose 默认 default | 找到时返回 found=true 和 accessToken；找不到时 found=false、hint，退出码 1。均回显店铺、站点、托管类型和用途。 |

Token 默认文件为 `~/.linkfox/temu-access-tokens.json`，可用 `TEMU_TOKEN_STORE_PATH` 覆盖；按用途精确匹配，不交叉复用其他区域或用途的令牌。授权需要主账号操作、多站点分别授权、到期重新复制，并联系紫鸟配置调用 IP 白名单。令牌存储用于凭证持久化，不属于响应缓存。

### LinkFox Token 校验

check_linkfox_token.py 可无参数或接收与上表兼容的 LinkFox 密钥 JSON 参数；复用 POST /temu/proxy，发送固定探测 body：site=cn、managementType=full-managed、accessToken=probe、type=probe。不消耗额外业务操作定义；并非每次业务调用必须执行的前置步骤。
该探测使用同值 Authorization / Token 请求头及相同密钥优先级。HTTP/errcode 按公共规则判断；连接或认证失败不得报告网关可达，预期的参数类 code=1002 不等于 Temu 业务调用成功。HTTP/errcode 为 402 时单独报告算力或余额问题，不提示令牌无效；403 保留为权限或网关错误。
输出 ok、脱敏 linkfoxToken、gatewayReachable、note；失败时输出 ok=false、reason（linkfox_token_invalid / linkfox_billing_error / gateway_request_failed）、message、hint，退出码 1。不会输出完整 LinkFox 密钥。

## 接口：加签文件下载

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/fileDownload`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| site | string | 是 | 欧洲站默认 `eu`。通用脚本支持 `cn`、`partner`、`us`、`global`、`eu`，须与授权区域一致。 |
| managementType | string | 是 | 默认 `semi-managed`；通用脚本允许 `full-managed` / `semi-managed`，须与授权一致。 |
| accessToken | string | 与 storeKey 二选一 | Temu 店铺令牌；直接提供时优先使用。脚本解析本地 storeKey 后仅向网关发送 accessToken。 |
| storeKey | string | 与 accessToken 二选一 | 使用 storeKey + site + managementType + tokenPurpose 定位令牌。业务脚本从 `~/.linkfox/temu-access-tokens.json` 本地解析该键，不随构造后的请求发送。 |
| tokenPurpose | string | 否 | 可选的令牌用途字段，建议 `product-inventory`；欧洲站封装读取 storeKey 时以此为默认值，本地查找后不随构造后的请求发送。 |
| url | string | 是 | 已有 Temu 加签资源 URL，保持原字符串及其查询参数，不自行追加编码。 |

欧洲站入口为 scripts/temu_eu_file_download.py，通用入口为 scripts/temu_file_download.py。请求体仅发送 site、managementType、accessToken、url。LinkFox 密钥、CLI 与认证头兼容规则见本页运行约定；下载不会缓存。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 若网关返回此字段，按公共响应码基本规则判断，不将 0 或 false 视为空。 |
| errmsg | string | 网关返回的错误说明（如有）。 |
| code | integer | 网关错误码：1002 表示参数或 LinkFox Token 问题，1003 表示转发失败；其他值按实际响应判断，不推测成功码。 |
| body | string | Temu 原始 JSON 字符串；脚本保留原值，并在可解析时增加 temuBody。 |
| transportHttpStatus | integer / null | 脚本增加的外层 HTTP 状态；连接失败为 null，不属于 Temu 上游状态码。 |
| temuBody | JSON value | 仅 body 为有效 JSON 字符串时增加；业务响应通常是 object / array，保留实际 JSON 类型。Temu 可在根级或 response 内返回业务对象，脚本不擅自改写层级。 |
| error | string | 连接失败、非 JSON 的 HTTP 错误或网关返回非对象时的脚本错误说明。 |
| details | string | HTTP 错误响应不是 JSON 时保留其原始文本。 |
| gatewayBody | JSON value | 仅网关返回非对象时保留原响应，并同时标记 error。 |

文件下载结果按实际返回展示，不假定包含额外字段、文件字节流或本地文件路径，不推测链接或自动下载二进制文件。调用层仅在 body 为有效 JSON 字符串时追加 temuBody，保留原字段。

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- code=1002 表示参数或 LinkFox Token 问题；code=1003 表示转发失败，检查 Temu 授权、用途、IP 白名单与 URL。不自动刷新链接或重试。
- 如返回可解析的 Temu 业务状态，依据 success、errorCode、errorMsg 说明结果，不因 HTTP 成功就断言素材可用。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/temu/fileDownload" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Token: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"site":"eu","managementType":"semi-managed","accessToken":"TOKEN","url":"https://example.com/signed-file-url"}'
```

---

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-temu-promotion-eu",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
