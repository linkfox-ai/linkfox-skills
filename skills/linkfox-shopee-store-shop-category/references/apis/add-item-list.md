# Shopee 店铺分类：向分类添加商品 接口说明

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

## 接口：向分类添加商品（add_item_list）

> 官方：[add_item_list](https://open.shopee.com/documents/v2/v2.shop_category.add_item_list?module=101&type=1)。脚本：`scripts/add_item_list.py`（相对于技能根目录）。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/shopee/developerProxy`

### 请求参数

#### 网关 POST Body

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| path | string | 是 | 固定为 `api/v2/shop_category/add_item_list`。 |
| method | string | 是 | 固定为 `POST`；LinkFox 外层始终 POST。 |
| shopId | string | 与 merchantId 二选一 | 店铺 ID，推荐；分类接口不是可省略店铺标识的 Public 接口。 |
| merchantId | string | 与 shopId 二选一 | 商户 ID；脚本将两个标识转为字符串。 |
| queryString | string | 否 | 本操作 CLI 不发送查询串，业务数据通过 body 发送。 |
| body | string | POST 是 | 上游请求正文字符串；脚本可接收 JSON 对象或字符串并序列化。 |
| contentType | string | POST 否 | 默认 `application/json`；随 body 发送，GET 不发送。 |

#### 脚本 JSON 参数

| 字段 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| shopId | string | 与 merchantId 二选一 | 已授权店铺 ID，推荐。 |
| merchantId | string | 与 shopId 二选一 | 已授权商户 ID。 |
| api | string | 仅通用入口 | 通用入口固定为 `add_item_list`；固定操作脚本忽略此字段。 |
| skipDepCheck | boolean | 否 | 默认 false，仅跳过本地依赖安装检测。 |
| body | object / string / JSON 值 | POST 是（或 requestBody） | 优先于 requestBody；对象序列化为紧凑 JSON，字符串原样发送；字符串需为有效 JSON。 |
| requestBody | object / string / JSON 值 | POST 是（或 body） | 兼容 body 别名，仅在 body 键不存在时使用。 |
| contentType | string | 否 | 默认 `application/json`。 |
| --inline | CLI flag | 否 | 全量打印并保存。 |
| --no-cache | CLI flag | 否 | 内部始终开启，不复用或保存响应缓存。 |

认证、依赖退出和缓存约定见 [脚本运行约定](../api.md#脚本运行约定)。

#### 参数构造与使用限制

POST 接受 `body` / `requestBody`，优先采用存在的 body 键；若两者均无，runner 只从注册的 `body_fields` 取值。本操作未配置 body_fields，故仅提供顶层业务字段会报错，必须提供完整正文。
`shopId`、`merchantId`、`skipDepCheck`、`body`、`requestBody`、`api`、`contentType` 都是保留字段，不进入 GET query；POST 仅转发所选正文，不把网关选店字段混入业务正文。分类操作由网关按店铺标识解析授权信息。

上游业务字段明细、嵌套结构、枚举、默认值及分页上限按本页官方文档和实际响应核对；脚本仅按上述规则包装请求，不补充业务参数默认值或校验分页范围。

### 响应结构

#### 网关响应

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | number / string / boolean / null | 网关业务状态码，按公共基本规则判断；不能将 0 或 false 当空值。 |
| errmsg | string | 网关消息或错误原因。 |
| httpStatus | integer | Shopee 上游状态，与 LinkFox 外层 HTTP 状态不同。 |
| contentType | string | Shopee 上游响应内容类型。 |
| body | string | Shopee 原始响应 JSON 字符串，完整业务字段以实际返回及官方文档为准。 |

#### 本地附加字段

公共调用器在连接失败或 HTTP 错误正文为空或无法解析为 JSON 时，可能在 `developerProxy` 中加入以下诊断字段；它们不是网关业务响应保证。外层状态另见 `transportHttpStatus`。

| 字段 | 类型 | 说明 |
|---|---|---|
| developerProxy.error | string | 连接失败，或 HTTP 错误正文为空或不是有效 JSON 时的错误信息。 |
| developerProxy.details | string | HTTP 错误正文不是有效 JSON 时保留的正文文本。 |

#### 脚本输出

| 字段 | 类型 | 说明 |
|---|---|---|
| api | string | 固定为 `add_item_list`。 |
| developerProxy | JSON 值 | 完整网关响应，包含上表已定义字段；错误响应不丢弃。 |
| resolvedPath | string | 实际转发路径 `api/v2/shop_category/add_item_list`。 |
| transportHttpStatus | integer / null | LinkFox 外层状态码；连接失败时为 null。 |
| queryString | string | 本操作不输出此字段。 |
| requestBody | JSON 值 / null | POST 请求正文解析结果；未发送正文时不输出。 |
| addItemList | JSON 值 / null | 网关正常且上游 httpStatus=200 时解析 body；此字段是完整 Shopee JSON，不仅是 response。空正文、非字符串正文或非法 JSON 时为 null；其他情况不添加。 |
| addItemListResponse | JSON 值 | 仅当解析结果为 object 且 response 非 null 时，提取该 response。 |
| addItemList.response | JSON 值 | Shopee 业务响应；内部字段、类型及嵌套结构以官方定义和实际返回为准。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 网关正常响应后，仅在 `developerProxy.httpStatus` 为 200（兼容字符串 `"200"`）时展开 body；状态缺失、非法或不为 200 时保留原始响应供解释。
- 上游 HTTP 200 只表示能够解析响应，不单独证明分类业务成功；继续检查返回的业务错误与结果，不能把解析键存在当作完成依据。
- 空正文、非法 JSON 或缺少 response 时不补造业务数据；根据原始错误和官方定义解释，后续调用遵守调用约束。

### curl 示例

下例为请求结构示意；写入操作的 body 占位内容需先替换为用户明确要求且符合官方定义的 JSON 正文。

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/shopee/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"path":"api/v2/shop_category/add_item_list","method":"POST","shopId":"67890","body":"<按官方定义准备的完整 JSON 正文>","contentType":"application/json"}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-shopee-store-shop-category",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
