# Temu 欧洲站电商广告 接口说明

本技能定义 7 个广告操作和 1 个加签文件下载操作（不含 Feedback）。广告操作均经 POST `/temu/proxy` 转发到 Temu 上游 path `/openapi/router`，以 Body 的 type 区分；不向请求体新增 path。通用代理是相同操作的兼容入口，不另计接口。

| 操作 | 接口文档 |
|---|---|
| 创建广告（`temu.searchrec.ad.create`） | [apis/temu-searchrec-ad-create.md](apis/temu-searchrec-ad-create.md) |
| 广告详情查询（`temu.searchrec.ad.detail.query`） | [apis/temu-searchrec-ad-detail-query.md](apis/temu-searchrec-ad-detail-query.md) |
| 广告可创建商品查询（`temu.searchrec.ad.goods.create.query`） | [apis/temu-searchrec-ad-goods-create-query.md](apis/temu-searchrec-ad-goods-create-query.md) |
| 广告操作日志查询（`temu.searchrec.ad.log.query`） | [apis/temu-searchrec-ad-log-query.md](apis/temu-searchrec-ad-log-query.md) |
| 修改广告（`temu.searchrec.ad.modify`） | [apis/temu-searchrec-ad-modify.md](apis/temu-searchrec-ad-modify.md) |
| 店铺广告报表查询（`temu.searchrec.ad.reports.mall.query`） | [apis/temu-searchrec-ad-reports-mall-query.md](apis/temu-searchrec-ad-reports-mall-query.md) |
| 广告 ROAS 预测（`temu.searchrec.ad.roas.pred`） | [apis/temu-searchrec-ad-roas-pred.md](apis/temu-searchrec-ad-roas-pred.md) |
| 加签文件下载 | [本页接口定义](#接口加签文件下载) |

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

## 网关与运行约定

### 认证与兼容

| 项目 | 约定 |
|---|---|
| 网关地址 | LINKFOX_TOOL_GATEWAY 优先，其次 TEMU_API_BASE_URL、STORE_API_BASE_URL，默认 https://tool-gateway.linkfox.com；去掉末尾斜杠。 |
| LinkFox 用户认证 | JSON 的 token、linkfoxToken、linkfox_token 按顺序优先；再取 LINKFOX_AGENT_API_KEY 或 LINKFOXAGENT_API_KEY。请求头 Authorization 与 Token 同值，并保留 SESSION_ID / MESSAGE_ID / MODE_ID / APP_NAME。 |
| Temu 店铺认证 | accessToken 优先；否则以 storeKey + site + managementType + tokenPurpose 读取本地令牌。不会自动申请 OAuth。 |
| 本地存储 | 默认 ~/.linkfox/temu-access-tokens.json；TEMU_TOKEN_STORE_PATH 可覆盖。按店铺、站点、托管模式与用途精确选择，不跨店铺或跨用途回退。 |
| EU 默认值 | site=eu、managementType=semi-managed；仅 storeKey 且无 accessToken 时默认 tokenPurpose=product-inventory。明确的其他用途保留，具体权限以该 Ads 接口 Partner 文档为准。 |
| Temu 上游 | EU 为 https://openapi-b-eu.temu.com/openapi/router，服务端按 site 解析。 |
| 通用兼容入口 | temu_proxy.py / temu_file_download.py 支持多站点入口与参数校验；site、managementType 必填且小写。通用代理只转发显式 params；EU 专用脚本支持顶层 request 或显式 params 对象，后者优先。 |
| 缓存 | 业务封装调用 call_api.run 时始终传 --no-cache，不读写响应缓存；公共调用器可能建立空 .cache 目录。 |
| 输出 | 保留完整网关响应、transportHttpStatus 和可解析的 temuBody；只保存一份最终结果，按 8000 字节切换完整输出与摘要，--inline 强制完整输出。数据只写当前工作目录的 linkfox/，不得回退到 /tmp、主目录或其他工作区；请求前检查最终日期/会话/data 目录的可写性，不可写时直接报错。连续调用使用微秒文件名，避免同秒覆盖。 |

授权步骤见 [access-token.md](access-token.md) 与 [authorization-flow.md](authorization-flow.md)，LinkFox 认证或算力异常按 [onboarding.md](onboarding.md) 处理。

### 本地辅助脚本

| 脚本 | CLI / 参数 | 行为 |
|---|---|---|
| scripts/check_linkfox_token.py | 可选 JSON，支持三种 LinkFox 密钥参数 | 使用同一 /temu/proxy 的 probe 请求检查「无法识别当前用户 / 重新登录」；仅用于网关认证探测。正常响应返回 ok、脱敏 linkfoxToken、gatewayReachable 和 note；认证错误或 HTTP / errcode 异常、连接失败、code=1003 时返回 ok=false 和 reason / message / hint 并退出 1，网关异常还返回 transportHttpStatus，连接失败时 gatewayReachable=false。保留 probe 的参数类 code=1002 探测约定，不能把 ok 当成店铺业务权限已验证。 |
| scripts/temu_token_guide.py | JSON：shopType（或 managementType）、tokenPurpose（默认 default）、site（可选） | 输出手动授权步骤；shopType 支持 semi-managed / full-managed / local-native，tokenPurpose 支持 product-inventory / order-shipping / full-managed / local-native / default。 |
| scripts/save_temu_access_token.py | JSON：storeKey、site、managementType、accessToken 必填；tokenPurpose 默认 default，label 可选 | 保存或替换同一令牌键，输出店铺键、站点、托管模式、用途、storePath、updatedAt、replaced，不回显令牌。 |
| scripts/list_temu_access_tokens.py | 无参数或 JSON：mask 默认 true | 列出本地 stores 与 tokens；默认脱敏，mask=false 才输出完整令牌。 |
| scripts/get_temu_access_token.py | JSON：storeKey、site、managementType 必填；tokenPurpose 默认 default | 精确读取并返回 found 和完整 accessToken；未找到时返回 hint 并退出 1。 |

## 接口：加签文件下载

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/fileDownload`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| site | string | 是 | EU 入口默认 eu；通用脚本必填，支持 cn / partner / us / global / eu。 |
| managementType | string | 是 | EU 入口默认 semi-managed；通用脚本必填，支持 full-managed / semi-managed。 |
| accessToken | string | 是 | Temu 令牌；脚本可通过 storeKey 解析后填入。 |
| url | string | 是 | 原始加签资源 URL；保留完整查询串，不自行解码或删除签名。 |

#### 脚本兼容参数

| 参数 | 类型 | 必填 | 默认 / 说明 |
|---|---|---|---|
| storeKey | string | 与 accessToken 二选一 | 使用本地店铺键；accessToken 直接传入时优先。 |
| tokenPurpose | string | 否 | EU 入口仅 storeKey 且无 accessToken 时默认 product-inventory；通用入口默认 default。仅用于本地选择，不转发。 |
| token / linkfoxToken / linkfox_token | string | 否 | LinkFox 用户密钥兼容参数；优先级见运行约定，不作为 Temu 令牌。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存。 |
| --no-cache | CLI flag | 否 | 封装始终禁用响应缓存。 |

脚本为 scripts/temu_eu_file_download.py；兼容多站点入口为 scripts/temu_file_download.py。EU 文件入口在仅传 storeKey 时同样补齐默认 site / managementType，用于本地令牌查找。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| transportHttpStatus | integer / null | 脚本补充的 LinkFox 外层 HTTP 状态；连接失败时为 null。与网关 code、Temu errorCode 分层判断，401/402 按 onboarding 指引处理。 |
| errcode | integer / string / null | 若返回，按公共规则判断。 |
| errmsg | string | 若返回，保留原消息。 |
| code | integer | 网关错误码：1002 参数或 Token 问题；1003 转发失败。 |
| body | string | 网关返回的原始内容；文件下载脚本原样保存整个 JSON 响应，不主动解析为 temuBody。 |

加签文件的其他结果字段、编码与资源交付方式以实际 JSON 返回为准；本入口不提供二进制文件落盘协议，不套用广告 result 结构。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- code=1002 时核对参数和 LinkFox 密钥；code=1003 时核对 Temu 令牌、用途、IP 白名单及网络。
- 不因外层请求完成就声称文件已在本地保存；该入口保存的是网关 JSON 响应，资源交付状态以实际结果为准。

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
  "skillName": "linkfox-temu-ads-eu",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
