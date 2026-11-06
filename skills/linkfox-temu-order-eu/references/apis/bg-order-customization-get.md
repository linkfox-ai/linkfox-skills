# 订单定制商品内容批量查询 接口说明

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

| 项 | 值 |
|----| ----- |
| **脚本** | `scripts/eu_order_customization_get.py` |
| **Partner 文档** | https://partner-eu.temu.com/documentation?menu_code=dbd3d395963a408984b8ae7dbc5f64f9（按 `type` 在 Partner EU 后台打开） |
| **网关** | `POST /temu/proxy`，`type`=`bg.order.customization.get`，业务载荷放在 Body 的 `params` |

用于订单定制商品内容批量查询。

> **网关鉴权字段**由本技能网关脚本处理；业务参数见下方 `request`。建议使用 **`tokenPurpose=order-shipping`**。  
> 入参为**子订单号** `orderSn`（非 `parentOrderSn`），可从 `bg.order.list.v2.get` / `bg.order.detail.v2.get` 的 `orderList[].orderSn` 取得。

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
| type | string | 是 | 固定为 `bg.order.customization.get`；Temu 操作名写在 Body，不是 LinkFox URL 路径。 |
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
| orderSnList | STRING[] | 否 | 子订单号列表；**单次最多查询 10 个订单** |

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
| result | OBJECT[] | 各子订单的定制内容列表（与请求的 `orderSnList` 对应） |

#### `result[]` 元素

| 参数 | 类型 | 说明 |
|------|------| ------ |
| orderSn | STRING | 对应该定制信息的子订单号 |
| customizedType | INTEGER | 定制类型，见下表 |
| customizedData | STRING | 图文定制内容，JSON 字符串；**仅当 `customizedType=2` 时返回** |
| previewList | OBJECT[] | 图文定制预览信息；**仅当 `customizedType=2` 时返回** |
| templateId | LONG | 用户创建定制信息时的模板 ID；商品无模板时为 `null` |
| templateType | INTEGER | 定制模板类型；商品无模板时为 `null`，见下表 |
| customizedText | STRING | 纯文本定制内容；**仅当 `customizedType=1` 时返回**（位于 `result[]` 元素顶层，与 `previewList[].customizedText` 不同） |
| customizedSvgList | OBJECT[] | SVG 格式定制信息列表 |

#### `customizedType`

| 值 | 说明 |
|----| ------ |
| `1` | 纯文本定制，无定制模板 |
| `2` | 图文定制，有定制模板 |

#### `templateType`

| 值 | 说明 |
|----| ------ |
| `1` | 仅图片 |
| `2` | 仅文字 |
| `3` | 文字 + 图片 |

> 商品无定制模板时，`templateId` / `templateType` 为 `null`。

#### `previewList[]` 元素

| 参数 | 类型 | 说明 |
|------|------| ------ |
| previewType | INTEGER | 预览项类型，见下表 |
| imageUrl | STRING | 图片 URL |
| customizedText | STRING | 预览项中的定制文字 |
| customizedAreaId | STRING | 定制区域 ID（`previewList[].customizedAreaId`）；**仅当 `templateType=3` 且 `previewType=3` 或 `4` 时返回** |

#### `previewType`

| 值 | 说明 |
|----| ------ |
| `1` | 整体预览图；若商品未配置定制区域，则为商家上传的效果图 |
| `3` | 用户上传图片 |
| `4` | 定制文字 |

#### `customizedSvgList[]` 元素

| 参数 | 类型 | 说明 |
|------|------| ------ |
| compressedFileUrl | STRING | 图片/压缩包下载 URL；调用方需 **GET** 该 URL 拉取文件；**创建后 10 分钟内有效**，过期需重新调本接口获取新 URL |

#### 下载 `compressedFileUrl` 的 TOA 请求头

对 `compressedFileUrl` 发起 **GET** 时，需在 Header 携带以下公共参数（与 Partner 文档一致）：

| Header | 类型 | 必填 | 说明 |
|---|---|---|---|
| `toa-app-key` | string | 是 | `${app_key}`，应用密钥。 |
| `toa-access-token` | string | 是 | `${access_token}`，店铺令牌。 |
| `toa-random` | string | 是 | 32 位随机数字符串。 |
| `toa-timestamp` | string | 是 | 时间戳。 |
| `toa-sign` | string | 是 | 签名（见下）。 |

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

- 先应用外层 HTTP / errcode 基础规则，再检查网关 `code`、解析 `body`，按 Temu 的 `success`、`errorCode`、`errorMsg` 和 `result` 解释业务结果；不能仅因 JSON 可解析就认定业务成功。
- 网关 `code=1002`：核对参数及 LinkFox Token；`code=1003`：检查 Temu 令牌、用途、IP 白名单及网络。Temu 业务失败时保留 `errorMsg` 和原始响应。

- 下载链接创建后仅 10 分钟有效，过期需重新获取；不得自动连续重试。

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
  "skillName": "linkfox-temu-order-eu",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
