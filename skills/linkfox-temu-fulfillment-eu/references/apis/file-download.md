# Temu 欧洲站加签文件下载 接口说明

[接口导航](../api.md)；[认证与 CLI 兼容](../api.md#运行约定)。

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

## 接口：加签文件下载

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/fileDownload`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| site | string | 是 | EU 入口默认 `eu`，须与令牌所属站点一致。 |
| managementType | string | 是 | EU 入口默认 `semi-managed`。 |
| accessToken | string | 是 | Temu 店铺令牌，脚本也可使用 `storeKey` 本地解析。 |
| url | string | 是 | 从面单 `shippingLabelUrlList[].url` 或 Scan Form `result.url` 获得的加签文件 URL；保留签名和 URL 编码，不拆改查询串。 |

推荐脚本 `scripts/temu_eu_file_download.py`；兼容 `scripts/temu_file_download.py` 的显式站点 CLI。LinkFox 令牌别名、双请求头、环境变量别名和本地选店规则见 [运行约定](../api.md#运行约定)。本地 `tokenPurpose` 默认 `order-shipping`，不发至网关。下载前核对面单可打印时间和对应扫描单状态。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 若返回，按公共规则判断。 |
| errmsg | string | 若返回，为网关消息。 |
| code | integer | 网关错误码 `1002` 表示参数或 Token 无效、`1003` 表示转发失败。 |
| body | string | 通用网关响应字段；下载专属成功字段或文件编码未定义；脚本保留 JSON 原样，按实际返回读取，不假定已在磁盘生成 PDF/PNG。 |
| _http_status | integer / null | 仅对象响应由脚本附加的本次 HTTP 状态码，不是网关字段；连接失败时为 `null`，错误原因保留在 `error`。 |

脚本将下载接口的完整 JSON 响应落盘，不解析为 `temuBody`，也不自行把内容转换为文件；不得虚构下载专属字段。对象响应只附加本地 `_http_status`，原业务字段保留。若实际返回数组、字符串、数字、布尔值或 `null`，保持原 JSON 类型并原样保存，不添加业务包装字段；本次 HTTP 状态码另输出到标准错误流（`HTTP status: ...`）。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

识别网关 `code=1002/1003` 并保留完整错误；源 URL 无效、签名过期或站点不符时核对原文原因，不自动重建链接或反复下载。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/temu/fileDownload" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Token: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"site":"eu","managementType":"semi-managed","accessToken":"TOKEN","url":"https://example.com/signed-label.pdf?signature=SIGNED_VALUE"}'
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
