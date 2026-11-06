# Temu 欧洲站 物流轨迹详情查询 接口说明

[接口导航](../api.md)；[授权与脚本兼容约定](../api.md#运行约定)。

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

## 接口：物流轨迹详情查询（temu.track.trackinginfo.get）

> 官方：[Partner EU 文档](https://partner-eu.temu.com/documentation?menu_code=7289390cfd724be4a196f11ebe45a896)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/proxy`

### 请求参数

#### 网关 POST Body

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| site | string | 是 | 本技能默认 `eu`；必须匹配店铺令牌所属站点。 |
| managementType | string | 是 | 本技能默认 `semi-managed`；合作仓仅支持半托管。 |
| accessToken | string | 与 storeKey 二选一 | Temu 店铺令牌；与 LinkFox API Key 不同。脚本调用网关前解析本地选店并填入此字段。 |
| storeKey | string | 与 accessToken 二选一 | 本地令牌库中的店铺键，指向 `~/.linkfox/temu-access-tokens.json`；当前脚本在本地读取并转换为 `accessToken`，不发送此字段。 |
| tokenPurpose | string | 否 | 建议 `order-shipping`；脚本用于本地令牌选择，不发送至网关。 |
| type | string | 是 | 当前操作的 Temu 接口标识，见本接口说明。 |
| params | object | 否 | Temu 业务参数；通常使用下方 `request` 对象。 |

本操作的 `type` 固定为 `temu.track.trackinginfo.get`。脚本：`scripts/eu_tracking_track_trackinginfo_get.py`（相对技能根目录）。

#### params 业务对象

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| request | OBJECT | 否（请求表标注） | 业务请求对象；其子字段、条件必填与特殊约定见下文。业务请求以各子字段要求为准。 |

#### 业务前提与限制

（物流轨迹详情查询接口：按 **packageSn** 查询包裹的物流跟踪号及轨迹节点列表。）

> **关联能力：** **`packageSn`** 来自 **`linkfox-temu-fulfillment-eu`**（如 **`bg.logistics.shipment.create`** / **`bg.logistics.shipment.result.get`**）；订单上下文见 **`linkfox-temu-order-eu`**。
> **`language`** 用于轨迹文案语言；不支持的语言将报错 **170070012**（见 Partner **TEMU Logistics Tracking API Documentation** 指南）。

#### `request` 内字段

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| packageSn | STRING | 否 | packageSn（Temu 包裹号；购标/履约后由 **`bg.logistics.shipment.create`** 等返回，用于查询该包裹的物流轨迹） |
| language | STRING | 否 | language（轨迹节点 **`statusText`** 等展示语言的 locale/语言代码；须为平台支持的语言，否则报错 **170070012 Unsupported languages, {*}`**） |

> 官方请求表将顶层 **`request`** 标为选填（False），且 **`packageSn`**、**`language`** 在表中亦为选填；实际查询须传入有效的 **`packageSn`**（及按需的 **`language`**）。Partner **请求示例** CURL 将 **`packageSn`**、**`language`** 写在 JSON 顶层，经 LinkFox 网关时建议放在 **`params.request`**（与 请求表结构一致）。

### 响应结构

#### 网关与脚本响应

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 若返回此字段，按公共规则判断，不将 `0` 或 `false` 视为空。 |
| errmsg | string | 若返回此字段，为网关消息；保留原文。 |
| body | string | Temu 原始 JSON 字符串；先判断网关状态，再解析业务内容。 |
| code | integer | 网关错误码：`1002` 为参数或 Token 无效，`1003` 为转发失败；不可当作 Temu 错误码。 |
| temuBody | object / array / scalar | 脚本在 `body` 可解析为 JSON 时增加的字段，完整保留原 `body`；不可解析时不增加。 |
| _http_status | integer / null | 仅脚本附加的本次 HTTP 状态码，不是网关字段；连接失败无 HTTP 响应时为 `null`，错误原因仍保留在 `error`。大响应摘要也展示该状态。 |

网关正常响应后，解析 `body`；若存在 `response` 包装则读取其业务对象。以下为 Temu 业务字段，不能替代外层 HTTP 与 `errcode` 判断。

Partner **响应** 表顶层为 **`response`** 对象。
**`result`** 子行在导出 HTML 中为折叠状态；下列层级按 **响应表 + 响应示例** 全部展开。

#### 顶层字段（`response` 内，或根级）

| 参数 | 类型 | 说明 |
|------|------|------|
| success | BOOLEAN | success（当前请求是否成功，True 成功，False 失败） |
| errorCode | INTEGER | error code（错误码） |
| errorMsg | STRING | error message（错误信息） |
| result | OBJECT | 业务结果对象（物流轨迹详情） |

#### `result` 内字段

| 参数 | 类型 | 说明 |
|------|------|------|
| packageSn | STRING | packageSn（包裹号；与请求 **`packageSn`** 对应） |
| trackingNum | STRING | Tracking number（物流运单号/跟踪号；Partner **响应示例** 字段名为 **`trackingNum`**） |
| trackingInfo | OBJECT[] | Logistics tracking information list（物流轨迹节点列表，按时间顺序展示承运商扫描/状态更新） |

##### `trackingInfo[]` 元素字段

| 参数 | 类型 | 说明 |
|------|------|------|
| logisticsStatus | STRING | Logistics status code（物流状态码；承运商/平台内部状态标识，具体枚举以 Temu 与承运商约定为准） |
| logisticsUpdatedAt | STRING | Logistics updated time（该轨迹节点更新时间；Partner **响应示例** 为字符串，一般为时间戳或 ISO 时间字符串） |
| statusText | STRING | Status description text（状态描述文案；语言由请求 **`language`** 决定） |

> 调用成功时先判断 **`success === true`**，再读取 **`result.trackingNum`** 与 **`result.trackingInfo`**。若返回 **170070011 Tracking Number Not Found**，表示暂无轨迹或单号无效，可稍后重试或核对 **`packageSn`**。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

网关正常后，判断 Temu 的 `success`、`errorCode`、`errorMsg` 与各项业务状态；`success=true` 不代表异步履约或审核已最终完成。业务错误保留原文，不自动重试写入。

| 错误码 | 错误信息（原文） | 处理建议 |
|--------|------------------|----------|
| 170070012 | Unsupported languages, {*} | Change the supported language（更换为 Partner **TEMU Logistics Tracking API Documentation** 支持的语言代码） |
| 170070011 | Tracking Number Not Found | Tracking information for this logistics number was not found. Please confirm the number is correct or try again later.（确认 **`packageSn`** 正确；包裹可能尚未产生轨迹，稍后重试） |
| 170070010 | Invalid Parameters: {*} | Parameters are invalid or missing. Please check the value and format of the {field name} field.（检查 **`packageSn`**、**`language`** 等字段格式与必填逻辑） |

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/temu/proxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Token: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '
{
  "site": "eu",
  "managementType": "semi-managed",
  "accessToken": "TOKEN",
  "type": "temu.track.trackinginfo.get",
  "params": {
    "request": {
      "packageSn": "PKG-001",
      "language": "en"
    }
  }
}
'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-temu-fulfillment-eu",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
