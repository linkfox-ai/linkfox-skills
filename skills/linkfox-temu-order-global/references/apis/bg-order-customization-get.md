# 订单定制商品内容批量查询 接口说明

接口总览见 [../api.md](../api.md)，认证指引见 [../onboarding.md](../onboarding.md)。

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

## 接口：订单定制商品内容批量查询（bg.order.customization.get）

批量读取子订单的文字、图文和 SVG 定制内容。

使用子订单 orderSn，可从列表或详情的 orderList[].orderSn 取得；父单 parentOrderSn 不能替代子单号。

官方文档：https://partner-global.temu.com/documentation?menu_code=dbd3d395963a408984b8ae7dbc5f64f9

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/proxy`

### 请求参数

#### 网关 POST Body

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| site | string | 是 | 本技能默认 `global`；全球区，非 US/EU。通用脚本兼容 `cn` / `partner` / `us` / `global` / `eu`。 |
| managementType | string | 是 | 本技能默认 `semi-managed`；通用脚本兼容 `full-managed` / `semi-managed`。 |
| accessToken | string | 与 storeKey 二选一 | Temu 店铺令牌；业务脚本优先直接使用，或从本地令牌存储读取后填入。 |
| storeKey | string | 与 accessToken 二选一 | 令牌键，对应 `~/.linkfox/temu-access-tokens.json` 中的记录（路径可由 `TEMU_TOKEN_STORE_PATH` 覆盖）；本技能脚本在本地解析，不把此字段转发到网关。 |
| tokenPurpose | string | 否 | 令牌用途，订单建议 `order-shipping`；本技能脚本仅用于本地选取令牌，不转发此字段。 |
| type | string | 是 | 本接口操作名，见下方操作标识；Temu 操作放在 Body，不是 URL path。 |
| params | object | 否 | 业务参数，使用本接口下方定义的 `request` 结构；无业务字段时脚本可省略。 |

#### 脚本参数与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| accessToken | string | 与 storeKey 二选一 | 直接提供时优先于本地令牌。 |
| storeKey | string | 与 accessToken 二选一 | 本地令牌键；按 site + managementType + tokenPurpose 精确匹配，不跨店铺、站点或用途回退。 |
| tokenPurpose | string | 否 | 全球区订单脚本默认 `order-shipping`；仅用于本地令牌选择，不转发为业务字段。 |
| token / linkfoxToken / linkfox_token | string | 否 | 按此顺序读取首个非空值，优先于环境变量；用于 LinkFox 用户鉴权，与 Temu accessToken 不同。 |
| --inline | CLI flag | 否 | 保存完整响应并强制全量打印。 |
| --no-cache | CLI flag | 否 | 业务脚本不使用响应缓存；调用公共 run 时始终传入此选项，不读取或保存响应缓存。 |

LinkFox 环境变量按 `LINKFOX_AGENT_API_KEY`、`LINKFOXAGENT_API_KEY` 顺序读取；Header `Authorization` 与 `Token` 同值。基础地址按 `LINKFOX_TOOL_GATEWAY`、`TEMU_API_BASE_URL`、`STORE_API_BASE_URL` 顺序兼容，默认正式网关。HTTP 超时默认 150 秒。
全球区专用脚本允许业务字段放在输入顶层，或放在对象 `params` 内；后者优先。顶层 `request` 整体作为 `params.request` 转发，不自动把任意业务字段再包一层。通用 `temu_proxy.py` 需显式传 site、managementType、type 和对象 params。令牌存储与授权 CLI 见 [../access-token.md](../access-token.md)。
会话数据保存在当前工作目录，禁止回退到临时目录；目录不可写时在请求前报错。无响应缓存仍可能由公共调用器创建空缓存目录，不保存响应缓存文件。

本接口 `type` 固定为 `bg.order.customization.get`；对应脚本 `scripts/global_order_customization_get.py`。

#### params 业务载荷

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| request | OBJECT | 否 | 业务请求对象，官方标注为选填；子字段必填性见下表。 |

#### `request` 内字段

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| orderSnList | STRING[] | 否 | orderSnList（子订单号列表）；**单次最多查询 10 个订单** |

### 响应结构

#### 网关与脚本输出

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | LinkFox 外层状态；遵循公共响应码基本规则，不替换为 Temu 成功判断。 |
| errmsg | string | LinkFox 外层消息；错误时保留。 |
| code | integer | 网关错误码：1002 为参数或 Token 问题，1003 为转发失败。 |
| body | string | Temu 原始 JSON 字符串；保留原文。 |
| temuBody | object / array | 脚本对非空且合法的 body 解析所得；解析失败时不生成，不补造业务结果。 |
| transportHttpStatus | integer / null | 脚本记录的外层 HTTP 状态，连接失败时为 null。 |
| error / details | string | 连接异常或非 JSON HTTP 错误的说明与原始内容（存在时保留）。 |

先检查外层 HTTP 与 errcode，再检查网关 code（如有错误），然后解析 body，依据 Temu 的 success / errorCode / errorMsg / result 解释结果。下列为 Temu body 解析后的原始业务字段。

#### `response` 顶层字段

| 参数 | 类型 | 说明 |
|------|------|------|
| success | BOOLEAN | 当前请求是否成功（success） |
| errorCode | INTEGER | 错误码（error code） |
| errorMsg | STRING | 错误消息（error message） |
| result | OBJECT[] | 各子订单的定制内容列表（与请求的 `orderSnList` 对应） |

#### `result[]` 元素

| 参数 | 类型 | 说明 |
|------|------|------|
| orderSn | STRING | OrderSn corresponding to customized information（对应该定制信息的子订单号） |
| customizedType | INTEGER | Customized type（定制类型），见下表 |
| customizedData | STRING | Graphic customization content, in **json format**（图文定制内容，JSON 字符串）；**仅当 `customizedType=2` 时返回** |
| previewList | OBJECT[] | Graphic customization preview information（图文定制预览信息）；**仅当 `customizedType=2` 时返回** |
| templateId | LONG | Customization template ID when user created customized information（用户创建定制信息时的模板 ID）；商品无模板时为 `null` |
| templateType | INTEGER | Customization template type when user created customized information（定制模板类型）；商品无模板时为 `null`，见下表 |
| customizedText | STRING | Customization text（纯文本定制内容）；**仅当 `customizedType=1` 时返回**（位于 `result[]` 元素顶层，与 `previewList[].customizedText` 不同） |
| customizedSvgList | OBJECT[] | Customized information list in **SVG format**（SVG 格式定制信息列表） |

##### `customizedType`

| 值 | 说明 |
|----|------|
| `1` | pure text customization, no customized templates（纯文本定制，无定制模板） |
| `2` | customized graphics and text, with customized templates available（图文定制，有定制模板） |

##### `templateType`

| 值 | 说明 |
|----|------|
| `1` | only image（仅图片） |
| `2` | only text（仅文字） |
| `3` | text and image（文字 + 图片） |

> 商品无定制模板时，`templateId` / `templateType` 为 `null`。

#### `previewList[]` 元素

| 参数 | 类型 | 说明 |
|------|------|------|
| previewType | INTEGER | type of preview item（预览项类型），见下表 |
| imageUrl | STRING | Image URL（图片 URL） |
| customizedText | STRING | Customized Text（预览项中的定制文字） |
| customizedAreaId | STRING | Customized Area ID（定制区域 ID）；**仅当 `templateType=3` 且 `previewType=3` 或 `4` 时返回** |

##### `previewType`

| 值 | 说明 |
|----|------|
| `1` | overall preview image（整体预览图；若商品未配置定制区域，则为商家上传的效果图） |
| `3` | user uploaded image（用户上传图片） |
| `4` | customized text（定制文字） |

#### `customizedSvgList[]` 元素

| 参数 | 类型 | 说明 |
|------|------|------|
| compressedFileUrl | STRING | Image URL and Compression file URL（图片/压缩包下载 URL）；调用方需 **GET** 该 URL 拉取文件；**创建后 10 分钟内有效**，过期需重新调本接口获取新 URL |

##### 下载 `compressedFileUrl` 的 TOA 请求头

对 `compressedFileUrl` 发起 **GET** 时，需在 Header 携带以下公共参数（与 Partner 文档一致）：

| Header | 说明 |
|--------|------|
| `toa-app-key` | 应用密钥标识（`${app_key}`） |
| `toa-access-token` | 店铺授权令牌（`${access_token}`） |
| `toa-random` | 32 位随机数字符串 |
| `toa-timestamp` | 时间戳 |
| `toa-sign` | 签名（见下） |

**`toa-sign` 计算逻辑：**

1. 将 Header 中参与签名的参数按参数名 **ASCII 升序**排序：`toa-app-key`、`toa-access-token`、`toa-random`、`toa-timestamp`
2. 按 `参数名 + 参数值` 依次拼接（中间**无**分隔符），得到长字符串
3. 在拼接结果**首尾**各拼接一次 `app_secret`，得到签名字符串
4. 对签名字符串做 **MD5**，再将密文转为**大写**，即为 `toa-sign`

> 实际 `app_key` / `access_token` / `app_secret` 以店铺授权与 Partner 应用配置为准；经 LinkFox 网关调用本 `type` 时，业务 JSON 仍走 `POST /temu/proxy`，**文件下载**为对上述 URL 的独立 GET + TOA 头。

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- `code=1002`：修正参数或 LinkFox Token；`code=1003`：检查 Temu 令牌、用途、IP 白名单和转发情况。
- Temu `success=false` 时根据 `errorCode`、`errorMsg` 解释失败；外层 HTTP 正常不代表 Temu 操作成功。保留 `result` 与 warning，不自动重试、翻页或换参数试探。
- body 不是合法 JSON 时保留原文，不把解析失败当作空业务结果。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/temu/proxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Token: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '
{
  "site": "global",
  "managementType": "semi-managed",
  "accessToken": "TOKEN",
  "type": "bg.order.customization.get",
  "params": {
    "request": {
      "orderSnList": [
        "SO-001",
        "SO-002"
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
  "skillName": "linkfox-temu-order-global",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
