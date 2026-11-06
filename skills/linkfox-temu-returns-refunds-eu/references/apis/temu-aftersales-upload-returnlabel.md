# 上传退货面单 接口说明

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


## 接口：上传退货面单（temu.aftersales.upload.returnlabel）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/proxy`

### 请求参数

#### 网关 POST Body

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| site | string | 是 | EU 包装脚本默认 `eu`；通用脚本显式传入。兼容枚举：`cn` / `partner` / `us` / `global` / `eu`。 |
| managementType | string | 是 | EU 包装脚本默认 `semi-managed`；通用脚本显式传入。兼容枚举：`full-managed` / `semi-managed`。 |
| accessToken | string | 是 | Temu 店铺令牌；脚本也可用本地 `storeKey` 解析后填入，不能把 LinkFox 密钥放入此字段。 |
| type | string | 是 | 本接口的 Temu 操作标识，见接口标题；是 Body 字段，不是 URL path。 |
| params | object | 否 | 业务载荷，本接口使用下方 `request` 对象。 |

#### 脚本参数与选项

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| token / linkfoxToken / linkfox_token | string | 否 | 按此顺序选首个非空值，优先于 `LINKFOX_AGENT_API_KEY`，再回退 `LINKFOXAGENT_API_KEY`；仅用于网关请求头，不转发为业务字段。 |
| storeKey | string | 与 accessToken 二选一 | 从本地令牌库解析店铺令牌；同时提供时优先 accessToken。 |
| tokenPurpose | string | 否 | EU 包装脚本用 storeKey 时默认 `order-shipping`，通用脚本默认 `default`；必须与保存令牌时的用途一致，不是网关 Body 字段。 |
| request | OBJECT | 否 | 可放在脚本 JSON 顶层，或嵌套在 `params.request`；存在对象类型的 params 时优先使用该对象，其他顶层业务字段不合并。 |
| --inline | CLI flag | 否 | 全量打印，仍保存完整响应。 |
| --no-cache | CLI flag | 否 | 业务封装调用公共 run 时始终加入此项，不读写响应缓存，不因 CLI 未提供此项而开启缓存。 |

`storeKey`、`tokenPurpose` 和 LinkFox 密钥只由脚本处理，不发送到 Temu 业务参数中。令牌库路径由 `TEMU_TOKEN_STORE_PATH` 覆盖，默认 `~/.linkfox/temu-access-tokens.json`。通用入口 `temu_eu_proxy.py` 显式传 type；各专用脚本固定 type。

#### 业务参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| params.request | OBJECT | 否 | Partner 顶层 request 标记为选填；下列必填业务字段仍须放在此对象中。 |

#### params.request 子字段

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| parentAfterSalesSn | STRING | **是** | 父售后单号。 |
| parentOrderSn | STRING | **是** | 父订单号。 |
| returnLabelDTOList | OBJECT[] | 否 | 退货面单信息列表。 |
| pickUpTimeScheduleMode | INTEGER | 否 | 上门揽收时必填；1 / 2 / 3 的含义见下方枚举表。 |
| startTimestamp | LONG | 否 | 时间段起点，毫秒；上传面单的预约模式 1、2 时必填。 |
| endTimestamp | LONG | 否 | 时间段终点，毫秒；上传面单的预约模式 1、2 时必填。 |
| latestTimestamp | LONG | 否 | 最晚揽收时间，毫秒；预约模式 3 时必填。 |

##### `returnLabelDTOList[]`（Partner 请求表为折叠行，按请求示例展开）

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| mallWarehouseId | STRING | 否 | 商家退货仓 ID，对应面单准备接口的 warehouseId。 |
| returnLabelUrl | STRING | 否 | 退货面单文件 URL。 |
| carrierId | LONG | 否 | 承运商 ID；上传面单时来自承运商查询结果。 |
| trackingNumber | STRING | 否 | 物流跟踪号。 |
| pickUpCertificateImageUrl | STRING | 否 | 上门揽收凭证图片 URL。 |

##### `pickUpTimeScheduleMode`

| 值 | 说明 |
|----|------|
| `1` | Select user's preferred time interval（选择用户偏好时间段） |
| `2` | Re-schedule time interval（重新预约时间段） |
| `3` | Select latest pick-up time point（选择最晚揽收时间点） |

经网关时业务字段位于 `params.request`；Partner 原始请求示例的顶层业务写法不能直接作为网关 Body。

### 响应结构

#### 网关响应与脚本加工

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 若返回，按公共响应码基本规则判断，不用 Temu 的 success 替代网关判断。 |
| errmsg | string | 若返回，保留网关消息。 |
| body | string | Temu 原始 JSON 字符串；先检查网关状态，再解析业务结果。 |
| code | integer | 网关业务错误字段，1002 表示参数或 LinkFox Token 无效，1003 表示转发失败；这些错误不能当作业务成功。 |
| transportHttpStatus | integer / null | 脚本记录的 LinkFox 外层 HTTP 状态码，连接失败时为 null；不与 Temu errorCode 混淆。 |
| temuBody | object / array / scalar / null | 仅脚本加工字段：body 是可解析的非空 JSON 字符串时加入；保留原始 body，解析失败时不补造此字段。 |

Temu 文档中的顶层是 `response` 对象，也可能直接位于解析后的根级；依实际层级读取下方字段。应先确认 LinkFox 外层 HTTP 与 errcode，再检查 code、解析 body，最后判断 Temu `success`、`errorCode`、`errorMsg` 与 `result`。

#### Temu 顶层字段（`response` 内，或根级）

| 参数 | 类型 | 说明 |
|------|------|------|
| success | BOOLEAN | 当前 Temu 请求是否成功；上传面单以严格等于 true 判断业务成功。 |
| errorCode | INTEGER | Temu 业务错误码，见下方业务规则。 |
| errorMsg | STRING | Temu 业务错误信息，保留实际返回值。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

本接口会提交退货面单；成功时没有 result，以 Temu success === true 判断上传成功，不能因缺少 result 判失败。结果不确定时先查售后详情及退货物流，不盲目重复提交。

| errorCode | errorMsg | 处理建议 |
|-----------|----------|----------------------|
| 130010000 | system error | 见 Partner 文档；修正入参或售后状态后重试 |
| 130010001 | The parameter is illegal. Please check if the input parameter meets the regulations. | 见 Partner 文档；修正入参或售后状态后重试 |
| 130010004 | no afterSales found | 见 Partner 文档；修正入参或售后状态后重试 |
| 130010005 | operate forbid | 见 Partner 文档；修正入参或售后状态后重试 |
| 130010006 | return label invalid | 见 Partner 文档；修正入参或售后状态后重试 |
| 130010007 | tracking number invalid | 见 Partner 文档；修正入参或售后状态后重试 |

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
  "type": "temu.aftersales.upload.returnlabel",
  "params": {
    "request": {
      "parentOrderSn": "PO-001",
      "parentAfterSalesSn": "PAS-001",
      "returnLabelDTOList": [
        {
          "mallWarehouseId": "WH-001",
          "returnLabelUrl": "https://example.com/label.pdf",
          "carrierId": 1,
          "trackingNumber": "1Z999",
          "pickUpCertificateImageUrl": "https://example.com/pickup.jpg"
        }
      ],
      "pickUpTimeScheduleMode": 1,
      "startTimestamp": 1714521600000,
      "endTimestamp": 1714525200000
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
  "skillName": "linkfox-temu-returns-refunds-eu",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
