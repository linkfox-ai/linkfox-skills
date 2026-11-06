# 订单核验信息上传 接口说明

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

## 接口：订单核验信息上传（temu.local.order.verification.upload）

| 项 | 值 |
|----| ----- |
| **脚本** | `scripts/eu_order_verification_upload.py` |
| **Partner 文档** | https://partner-eu.temu.com/documentation?menu_code=dbd3d395963a408984b8ae7dbc5f64f9（按 `type` 在 Partner EU 后台打开） |
| **网关** | `POST /temu/proxy`，`type`=`temu.local.order.verification.upload`，业务载荷放在 Body 的 `params` |

用于订单核验信息上传。

> **网关鉴权字段**由本技能网关脚本处理；业务参数见下方 `request`。建议使用 **`tokenPurpose=order-shipping`**。  
> 入参为**子订单号** `orderSn`（可从 `bg.order.detail.v2.get` 等接口的 `orderList[].orderSn` 取得）。

---

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/proxy`

### 请求参数

#### 网关 POST Body

| 参数 | 类型 | 必填 | 说明 |
|---|---|---| --- |
| site | string | 是 | EU 封装默认 `eu`；通用脚本支持 `cn`、`partner`、`us`、`global`、`eu`，须为小写。 |
| managementType | string | 是 | EU 封装默认 `semi-managed`；通用脚本允许 `full-managed`、`semi-managed`，须为小写。 |
| accessToken | string | 是 | Temu 店铺令牌；使用脚本的 `storeKey` 时在本地读取后写入此字段。 |
| type | string | 是 | 固定为 `temu.local.order.verification.upload`；Temu 操作名写在 Body，不是 LinkFox URL 路径。 |
| params | object | 否 | Temu 业务参数，本接口的业务块为 `params.request`。 |

#### 脚本参数与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---| --- |
| token / linkfoxToken / linkfox_token | string | 否 | LinkFox 密钥别名，按此顺序取首个非空值，优先于环境变量；不转发到 Temu。 |
| storeKey | string | 与 accessToken 二选一 | 本地店铺键；以 site、managementType、tokenPurpose 精确读取，accessToken 非空时优先。 |
| tokenPurpose | string | 否 | EU 封装在仅用 storeKey 且未显式指定时默认 `order-shipping`；通用脚本默认 `default`。不转发到 Temu。 |
| params | object | 否 | EU 封装优先使用该对象，否则将剔除保留控制字段后的顶层业务字段整体放入网关 params；`request` 的层级保持不变。 |
| --inline | CLI flag | 否 | 强制完整打印，并保存完整响应。 |
| --no-cache | CLI flag | 否 | 业务脚本不启用响应缓存，调用公共 run 时始终加入该选项，不读写响应缓存；公共调用器可能创建空缓存目录。 |

网关地址按 `LINKFOX_TOOL_GATEWAY` → `TEMU_API_BASE_URL` → `STORE_API_BASE_URL` → 正式地址选择。保留 `Authorization` 与 `Token` 同值双请求头及会话头。HTTP 默认超时 150 秒，不自动重试。完整响应只保存在当前工作目录的 linkfox 会话目录；不可写则请求前报错，禁止回退到家目录或临时目录。同秒多次结果使用微秒文件名避免覆盖。

本地令牌保存在 `~/.linkfox/temu-access-tokens.json`，可用 `TEMU_TOKEN_STORE_PATH` 覆盖；提供保存、读取、列举与授权指引 CLI，详见 [授权说明](../access-token.md)。本地令牌存储不属于接口响应缓存。


#### 业务对象

| 参数 | 类型 | 必填 | 说明 |
|---|---|---| --- |
| params.request | OBJECT | 否 | 官方业务请求对象；嵌套字段的必填性见下表。 |

#### `params.request` 内字段

| 参数 | 类型 | 必填 | 说明 |
|------|------|------| ------ |
| orderList | OBJECT[] | 否 | 订单唯一标识/核验信息列表；按子订单维度批量上传 |

#### `orderList[]` 元素

| 参数 | 类型 | 必填 | 说明 |
|------|------|------| ------ |
| orderSn | STRING | 否 | 子订单号 |
| verificationInfo | OBJECT[] | 否 | 高价值/电子产品唯一标识列表，如 SN、IMEI |
| secondHandVerificationInfo | OBJECT[] | 否 | 二手商品鉴真/认证信息列表 |

#### `verificationInfo[]` 元素

| 参数 | 类型 | 必填 | 说明 |
|------|------|------| ------ |
| serialNumber | STRING | 否 | 序列号 SN |
| imeiNumberList | STRING[] | 否 | IMEI 号码列表 |

> 高价值商品场景：按实际商品要求填写 `serialNumber` 和/或 `imeiNumberList`；同一 `orderSn` 可包含多条 `verificationInfo`（例如多件商品各一条 SN）。

#### `secondHandVerificationInfo[]` 元素

| 参数 | 类型 | 必填 | 说明 |
|------|------|------| ------ |
| secondHandProofCertificateCode | STRING | 否 | 二手商品鉴真/证明证书编码 |

> 二手商品场景：填写 `secondHandProofCertificateCode`；与高价值 `verificationInfo` 按订单实际类型择一或组合使用（以 Partner 与订单标签为准）。

### 响应结构

#### 网关与脚本输出

| 字段 | 类型 | 说明 |
|---|---| --- |
| errcode | integer / string / null | 公共响应业务状态；是否正常按基础规则判断。 |
| errmsg | string | 公共响应消息，错误时依据实际内容解释。 |
| body | string | Temu 原始 JSON 字符串，完整保留；可解析时脚本增加 temuBody。 |
| code | integer | 网关错误码；`1002` 表示参数或 LinkFox Token 无效，`1003` 表示转发失败，不覆盖公共 errcode 规则。 |
| temuBody | object / array / scalar / null | 脚本对非空合法 JSON body 解析后的值；解析失败不添加该字段。 |
| transportHttpStatus | integer / null | 脚本保留的外层 LinkFox HTTP 状态码；连接失败为 null。 |

下面字段属于 `body` 解析后的 Temu 响应，不属于外层网关对象。

#### `response` 顶层字段

| 参数 | 类型 | 说明 |
|------|------| ------ |
| success | BOOLEAN | 是否成功 |
| errorCode | INTEGER | 错误码 |
| errorMsg | STRING | 错误信息 |
| result | OBJECT | 业务结果对象；官方出参表未展开子字段，上传成功时通常以 `success=true` 为准，具体以 Temu 实际返回为准 |

#### `result`

| 参数 | 类型 | 说明 |
|------|------| ------ |
| _(无子字段)_ | — | Partner 文档未列出 `result` 内嵌套属性；若响应体含其它字段，以实际 JSON 为准 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 先应用外层 HTTP / errcode 基础规则，再检查网关 `code`、解析 `body`，按 Temu 的 `success`、`errorCode`、`errorMsg` 和 `result` 解释业务结果；不能仅因 JSON 可解析就认定业务成功。
- 网关 `code=1002`：核对参数及 LinkFox Token；`code=1003`：检查 Temu 令牌、用途、IP 白名单及网络。Temu 业务失败时保留 `errorMsg` 和原始响应。

- 上传成功以 Temu 返回的 success 为准；result 未展开子字段，不据此虚构逐单核验结果。结果不确定时先核实，避免重复上传。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/temu/proxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Token: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "site": "eu",
  "managementType": "semi-managed",
  "accessToken": "TOKEN",
  "type": "temu.local.order.verification.upload",
  "params": {
    "request": {
      "orderList": [
        {
          "orderSn": "SO-123456789",
          "verificationInfo": [
            {
              "serialNumber": "SN-001234567890",
              "imeiNumberList": [
                "352099001761481",
                "352099001761482"
              ]
            }
          ]
        }
      ]
    }
  }
}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-temu-order-eu",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
