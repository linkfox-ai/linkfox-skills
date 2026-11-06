# Amazon 店铺授权与管理 接口说明

## 公共规则

### 调用规范

- **请求基础地址**：`LINKFOX_TOOL_GATEWAY` 默认 `https://tool-gateway.linkfox.com`
- **请求方式**：POST, HTTP 超时 150s
- **请求头**
  - Content-Type: application/json
  - User-Agent: LinkFox-Skill/2.0
  - Authorization: <api_key> (<api_key> 从环境变量 `LINKFOX_AGENT_API_KEY` 或 `LINKFOXAGENT_API_KEY` 读取，未配置则按 SKILL.md 的 **## 解决认证和算力问题** 处理)

### 响应码基本规则

- **正常响应**: HTTP 状态码为 `200`–`299`，且响应体的 `errcode` 不存在、为 `null`、为空字符串（含纯空白）或为 `200`–`299`（数字或数字字符串）。授权接口也兼容旧版成功码整数 `0` 和字符串 `"0"`。
- **未正常响应**: HTTP 状态码不属于 `200`–`299`，或响应体的 `errcode` 不符合上述取值。布尔值 `false` 为无效业务码。
- **认证或用量错误**: HTTP 状态码为 `401` / `402`，按 onboarding.md 的指引处理
- **其他情况**: 依据响应体的 `errmsg` 判断具体原因
### 网关错误响应

成功对象与错误对象分别处理。统一错误模型为 errcode（integer）和 errmsg（string）；HTTP 200 也可能是业务错误。HTTP 401 / 402 按认证引导处理，其他错误保留原始 errmsg。脚本补充的 transportHttpStatus、outputError 及计费头展示不属于接口成功 DTO。

本技能操作仅面向当前 API Key 对应成员。原始 accessToken、refreshToken 均由服务端保存，storeTokens 仅返回授权状态；下游代理使用 sellerId + region。脚本仍须对意外出现的令牌字段脱敏，详见脚本参考。

## 接口：获取授权链接（authorizeUrl）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/authorizeUrl`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | 服务端检查非空；格式 NA / EU / FE。 |
| sellerName | string | 否 | 店铺展示名，最长 64 字符；服务端可保存为空。本技能脚本流程要求填写，见脚本参考。 |
| central | string | 否 | seller / vendor，默认 seller；脚本授权流程使用 seller。 |
| marketplace | string | 否 | 最长 32 字符；vendor 授权时常用，按 Amazon 市场英文名称填写，如 US、UK、Germany；脚本流程有单独必填要求。 |

脚本流程、CLI 必填项与本地输出见 [script-usage.md](script-usage.md)。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| authorizeUrl | string | Amazon 完整授权 URL，约一小时内完成授权，不手工拼接。 |
| sourceType | string | amazon_sp_api。 |
| sourceTool | string | 紫鸟开发者授权代理。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 生成链接不等于授权成功；回调、换取及保存令牌属于服务端内部流程，不列为客户端接口。
- 手动脚本使用 JSON CLI；校验店铺名与区域，并要求当前流程所需的 central 和 marketplace。
- 自动 CLI：`python scripts/automatic_authorize_url.py --region NA --seller-name '中文店铺' --central seller --marketplace US`。选项均必填；保留 Unicode 店铺名，拒绝空白值。仅本机 Windows/macOS，Linux/WSL、云端、容器和远程主机不支持；宿主不明确时不得安装、申请 Key、列店铺或生成链接。
- 自动脚本 stdout 保持单 JSON 文档，OAuth URL 只在内存传递；公共 run 仅保存递归移除 authorizeUrl 字段、隐藏消息中重复授权链接后的状态元数据，不将完整 URL 写文件或日志。手动模式按常规输出并逐字展示 SKILL.md 的安全警告。
- `errcode=1002`：缺少参数；`1003`：获取授权地址失败，核对网络与回调白名单；不得自动连续换参数请求。
- 完整自动授权的配置复用、并发、窗口归属、登录/MFA、成功证据及收尾限制见 [自动授权](automatic-authorization.md)。
- 收到 450 / 453 / 454 / 459 时按 [店铺保护与重试](spapi-protection.md) 停止对应范围的调用，优先遵循 retryAfter / blockedUntil。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/authorizeUrl" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"region": "NA", "sellerName": "我的店铺", "central": "seller", "marketplace": "US"}'
```

### 响应示例

```json
{
  "authorizeUrl": "https://sellercentral.amazon.com/apps/authorize/consent?..."
}
```

## 接口：查询已授权店铺（authorizedStores）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/authorizedStores`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| 请求体 | object | 否 | 无业务参数，使用当前 API Key 对应的成员上下文，脚本发送 {}。 |

脚本流程、CLI 必填项与本地输出见 [script-usage.md](script-usage.md)。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| total | integer | 已授权店铺条数。 |
| stores | array<object> | 当前成员已绑定的店铺列表。 |
| stores[].sellerName | string | 卖家名称，可为空。 |
| stores[].sellerId | string | 卖家 ID。 |
| stores[].region | string | 区域 NA / EU / FE。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 服务端查询当前成员绑定、关联授权记录并去重，按 sellerId、region 排序；空列表只说明当前成员未查询到绑定，不自动授权。
- `errcode=1002`：无法识别当前用户，检查认证。
- `python scripts/authorized_stores.py` 保持无参数用法；`python scripts/automatic_verify.py` 保持只输出一个 JSON 文档，公共 run 的落盘摘要不混入 stdout。核验必须结合本次成功回调及准确卖家身份/区域，不能仅凭历史列表或紫鸟名称认定成功。
- 收到 450 / 453 / 454 / 459 时按 [店铺保护与重试](spapi-protection.md) 停止对应范围的调用，优先遵循 retryAfter / blockedUntil。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/authorizedStores" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{}'
```

### 响应示例

```json
{
  "stores": [
    {
      "sellerName": "我的店铺",
      "sellerId": "A1234567890",
      "region": "NA"
    }
  ],
  "total": 1
}
```

## 接口：刷新令牌（refreshToken）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/refreshToken`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| sellerId | string | 是 | 非空 Seller ID，最长 64 字符。 |
| region | string | 否 | NA / EU / FE，用于精确匹配；不传时服务端匹配该 sellerId 第一条记录，生产调用建议明确区域，脚本不擅自补默认。 |

脚本流程、CLI 必填项与本地输出见 [script-usage.md](script-usage.md)。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| authRecordId | integer（Long） | 授权主表记录 ID。 |
| success | boolean | 刷新是否成功。 |
| message | string | 刷新结果说明。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 校验记录属于当前成员后，由服务端向紫鸟 `/developer-proxy/{region}/auth/o2/token` 换取并更新令牌，refresh_token 本身可能更新；这些不是本技能客户端调用接口。
- 正常响应仍须检查 success；false 不能认定刷新成功。后台保存令牌，后续 developerProxy 使用相同 sellerId + region，不先取 raw token。
- `1002`：缺 sellerId；`1004`：记录不存在、不属于当前用户或缺 refresh_token，核对账号，记录异常时重新授权；`1003`：刷新第三方请求失败，检查网络/白名单，不自动重试。
- 收到 450 / 453 / 454 / 459 时按 [店铺保护与重试](spapi-protection.md) 停止对应范围的调用，优先遵循 retryAfter / blockedUntil。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/refreshToken" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"sellerId": "A1234567890", "region": "NA"}'
```

### 响应示例

```json
{
  "authRecordId": 123,
  "success": true,
  "message": "刷新成功并已更新数据库，token 已后台化管理"
}
```

## 接口：查询授权状态（storeTokens）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/storeTokens`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| sellerId | string | 是 | 非空 Seller ID，最长 64 字符。 |
| region | string | 是 | NA / EU / FE。 |

脚本流程、CLI 必填项与本地输出见 [script-usage.md](script-usage.md)。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| sellerId | string | 卖家 ID。 |
| region | string | 区域。 |
| authRecordId | integer（Long） | 授权主表记录 ID。 |
| status | string | 按当前访问令牌是否非空返回 ACTIVE 或 EXPIRED。 |
| tokenExpiresAt | integer（Long） | 当前实现取入库的 expiresIn 秒数；可为空，不解作绝对时间。 |
| message | string | 授权状态说明。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 仅读取本地授权状态，不执行刷新。EXPIRED 时可按任务调用 refreshToken；当前成员已解绑时须重新授权，不能将共享记录标记为 REVOKED。
- 不将状态响应作为下游 token 来源；下游通过 developerProxy 传 sellerId + region。
- `1002`：缺 sellerId 或 region；`1004`：记录不存在或不属于当前成员，先核对列表与区域再决定是否授权。
- 收到 450 / 453 / 454 / 459 时按 [店铺保护与重试](spapi-protection.md) 停止对应范围的调用，优先遵循 retryAfter / blockedUntil。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/storeTokens" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"sellerId": "A1234567890", "region": "NA"}'
```

### 响应示例

```json
{
  "sellerId": "A1234567890",
  "region": "NA",
  "authRecordId": 123,
  "status": "ACTIVE",
  "tokenExpiresAt": 3600,
  "message": "授权信息已后台化管理，token 不再经由 Agent 返回"
}
```

## 接口：本地解绑（cancelAuthorization）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/cancelAuthorization`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| sellerId | string | 是 | 非空 Seller ID，去首尾空白后最多 64 字符。 |
| region | string | 是 | NA / EU / FE，必须明确，不支持单站点解绑。 |

脚本流程、CLI 必填项与本地输出见 [script-usage.md](script-usage.md)。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| success | boolean | 成功标志；未绑定或重复解绑也为 true。 |
| sellerId | string | 卖家 ID。 |
| region | string | 区域。 |
| removedBindings | integer | 移除的当前成员绑定数，重复解绑为 0。 |
| localAuthorizationRevoked | boolean | 固定 false，保留授权主记录及令牌。 |
| amazonRevoked | boolean | 固定 false，未执行 Amazon 官方撤销。 |
| message | string | 解绑结果说明。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 只移除当前 API Key 对应成员的 sellerId + region 绑定；授权主记录、token 及其他成员绑定保留。同一成员身份/API Key 的共用者一起受影响。
- 解绑覆盖整个区域；仅要求单站点时，须先取得整个区域解绑的明确同意，不使用默认区域代替选择。
- 未绑定或重复解绑仍返回 success=true、removedBindings=0，两个 revoked 字段均为 false。必须同时满足基础正常响应与 success=true 才报告完成。
- 已发出请求和未完成 OAuth 回调不受影响；后者可能恢复绑定。结果不确定时先查店铺，不直接重放，不自动重新授权。
- Amazon 官方撤销由卖家在 Seller Central → Manage Your Apps → Disable authorization 操作；不得将本地解绑描述为 Amazon 撤权。
- 参数注解校验可返回 400；服务层缺 sellerId / region 或区域无效返回 1002。未绑定或重复解绑按 success=true、removedBindings=0 处理。XML 错误按 errcode/errmsg 解析，并保留 HTTP 状态及计费头。
- 收到 450 / 453 / 454 / 459 时按 [店铺保护与重试](spapi-protection.md) 停止对应范围的调用，优先遵循 retryAfter / blockedUntil。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/cancelAuthorization" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"sellerId": "A1234567890", "region": "NA"}'
```

### 响应示例

```json
{
  "success": true,
  "sellerId": "A1234567890",
  "region": "NA",
  "removedBindings": 1,
  "localAuthorizationRevoked": false,
  "amazonRevoked": false,
  "message": "已解除当前用户的店铺绑定；授权与 token 保留，其他用户不受影响；未撤销 Amazon 授权"
}
```

---

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-amazon-store-auth",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
