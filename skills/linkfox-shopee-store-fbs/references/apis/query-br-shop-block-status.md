# 查询巴西 FBS 店铺封禁状态 接口说明

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

## 接口：查询巴西 FBS 店铺封禁状态（query_br_shop_block_status）

> 官方参考：[v2.fbs.query_br_shop_block_status](https://open.shopee.com/documents/v2/v2.fbs.query_br_shop_block_status?module=126&type=1)。下列字段表说明网关参数与脚本映射；上游业务字段以实际响应为准，不假设固定 schema，不臆造字段或枚举。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/shopee/developerProxy`

### 请求参数

#### 网关 POST Body

| 参数 | 类型 | 必填 | 默认值 / 说明 |
|------|------|------|------|
| path | string | 是 | 固定 `api/v2/fbs/query_br_shop_block_status`。 |
| method | string | 是 | 固定 `GET`，指 Shopee 上游方法；网关本身使用 POST。 |
| shopId | string | 与 merchantId 至少一项 | 巴西店铺 ID，推荐；服务端解析已授权店铺 token。两者都提供时均保留。 |
| merchantId | string | 与 shopId 至少一项 | 商户 ID。 |
| queryString | string | 否 | 无 `?` 前缀；脚本将顶层额外标量业务参数编码为查询串，空串不发送。 |
| body | string | 否 | 代理兼容字段；本 GET 查询不发送。 |
| contentType | string | 否 | 代理 body 的类型，底层兼容函数默认 `application/json`；本 GET 查询省略。 |

#### 脚本 JSON 参数与 CLI 选项

| 参数 / 选项 | 类型 | 必填 | 默认值 / 说明 |
|------|------|------|------|
| shopId | string | 与 merchantId 至少一项 | 店铺 ID；不进入 runner 生成的 `queryString`，由网关另以 `shop_id` 转发。 |
| merchantId | string | 与 shopId 至少一项 | 商户 ID；不进入 runner 生成的 `queryString`，由网关另以 `merchant_id` 转发。 |
| api | string | 仅通用入口必填 | `fbs_api.py` 选择 `query_br_shop_block_status`；专用入口固定操作。属于保留字段。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已确认依赖时跳过安装检测，不跳过选店校验或服务端授权。 |
| contentType | string | 否 | 默认 `application/json`；本 GET 查询不使用，属于保留字段。 |
| body / requestBody | string / object / array / number / boolean / null | 否 | 兼容 runner 的保留字段，本 GET 查询不使用，不进入查询串。 |
| 其他顶层业务参数 | string / number / boolean / null / object / array | 否 | 脚本不额外校验必填业务参数。标量值经百分号编码进入查询串；布尔值为小写 `true` / `false`；null、object、array 跳过。只按实际接口定义补充业务参数。 |
| --inline | CLI flag | 否 | 强制完整打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 所有入口内部始终传入；不读写响应缓存，显式添加也可兼容。公共调用器可能建立空缓存目录。 |

#### 参数约束和使用限制

- 面向巴西 BR 的 FBS 已授权店铺；无论依赖检测是否跳过，都必须提供 `shopId` 或 `merchantId`。网关标识会转为字符串。
- 业务字段放脚本 JSON 顶层，runner 拼进不含问号的 `queryString`；`shopId`、`merchantId`、`skipDepCheck`、`api`、`body`、`requestBody`、`contentType` 均不进入 runner 生成的 `queryString`；网关仍将店铺标识另以 `shop_id` / `merchant_id` 转发。
- GET 查询未配置列表归一化字段，不把数组自动拼成列表参数，也不虚构分页或上游速率限制。
- 运行 `python scripts/check_auth_dependency.py`，返回 42 表示先安装 `linkfox-shopee-store-auth`；不得另建授权或令牌流程。底层代理兼容函数要求 path 以 `api/v2` 开始，正常入口固定使用本接口路径。
- 网关环境变量优先级为 `LINKFOX_TOOL_GATEWAY`、`SHOPEE_API_BASE_URL`、默认正式网关；保留两种 API Key 环境变量以及会话请求头。
- 脚本不读写响应缓存，调用 `call_api.run` 始终带 `--no-cache`。完整处理结果保存到当前工作目录的会话数据目录；不可写时在请求前报错，不回退到临时目录。
- 失败或空结果不自动换条件、翻页或连续试探；继续查询前说明查询范围。

### 响应结构

#### 网关原始响应

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 网关业务状态码，可能不存在；按响应码基本规则判断，不与上游状态混同。 |
| errmsg | string | 网关消息，按实际返回保留。 |
| httpStatus | integer / 数字字符串 | Shopee 上游 HTTP 状态；脚本以整数转换后是否为 200 决定解析 body。 |
| contentType | string / null | 上游响应 Content-Type。 |
| body | string | Shopee 返回的正文，通常为 JSON 字符串；完整上游字段以实际响应为准。 |

#### 本地附加字段（developerProxy 内）

| 字段 | 类型 | 说明 |
|------|------|------|
| error | string | 公共调用器在 HTTP 错误或连接失败时生成的错误信息，不是网关保证字段。 |
| details | string | HTTP 错误响应无法解析为 JSON 时，公共调用器保留的原始文本。 |

#### 脚本处理结果

| 字段 | 类型 | 说明 |
|------|------|------|
| api | string | 本次操作名 `query_br_shop_block_status`。 |
| developerProxy | object | 完整网关响应，含其 errcode、httpStatus、body 等实际字段；错误内容也保留。 |
| resolvedPath | string | `api/v2/fbs/query_br_shop_block_status`。 |
| queryString | string | 非空时返回实际编码后的查询串，不含 `?`。 |
| requestBody | object / array / scalar / null | 兼容 runner 的请求 body 解析结果；本 GET 查询不返回。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败为 null。 |
| queryBrShopBlockStatus | object / array / scalar / null | 网关正常且上游 httpStatus 为 200 时，解析后的完整 Shopee body；空或非法 JSON 为 null。此字段保存完整 body，其中的 response 另行提取。 |
| queryBrShopBlockStatusResponse | object / array / scalar | 完整 body 为对象且 response 不为 null 时，额外提取其中 response；未定义固定内部字段、枚举或默认值。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 仅在公共规则判定网关正常，且 Shopee 上游 `developerProxy.httpStatus` 可转换为整数 200 时解析业务结果；上游其他状态保留原始响应，不推断业务状态。
- 空 body 或非法 JSON 的解析字段为 null；上游 body 中的错误和 response 含义按实际返回解释，解析成功不代表已入驻、未封禁或无发票错误。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/shopee/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"path":"api/v2/fbs/query_br_shop_block_status","method":"GET","shopId":"67890"}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-shopee-store-fbs",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
