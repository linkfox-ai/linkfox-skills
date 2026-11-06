# Shopee 获取精选集合列表 接口说明

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

## 接口：获取精选集合列表（get_top_picks_list）

> 官方：[v2.top_picks.get_top_picks_list](https://open.shopee.com/documents/v2/v2.top_picks.get_top_picks_list?module=100&type=1)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/shopee/developerProxy`

### 请求参数

#### 网关 POST Body

| 参数 | 类型 | 必填 | 默认与说明 |
|---|---|---|---|
| path | string | 是 | 固定 `api/v2/top_picks/get_top_picks_list`；必须使用 `api/v2/top_picks/` 前缀。 |
| method | string | 是 | 固定 `GET`，表示 Shopee 上游方法；LinkFox 外层始终 POST。 |
| shopId | string | 与 merchantId 至少一个 | 店铺 ID，推荐使用；脚本转为字符串。两者都提供时均转发。Top Picks 不是无店铺 Public 操作。 |
| merchantId | string | 与 shopId 至少一个 | 商户 ID；由服务端按选店信息解析令牌。不能保证任意商户都具备对应 Top Picks 权限，以网关和上游授权结果为准。 |
| queryString | string | 否 | 无 `?` 前缀；GET 时由 CLI 顶层业务标量生成。常规 POST CLI 不生成查询串。 |
| body | string | 否 | 列表 CLI 不发送；网关不向上游转发 GET 正文。 |
| contentType | string | 否 | 仅用于有正文的 POST / PUT；本列表操作不发送。 |

#### 脚本 JSON 参数与选项

| 参数 / 选项 | 类型 | 必填 | 默认与说明 |
|---|---|---|---|
| shopId / merchantId | string | 至少一个 | 用于网关选店，不进入自动构造的上游查询或 body。 |
| api | string | 通用入口必填 | `top_picks_api.py` 的操作名；独立入口使用固定操作，忽略此字段。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已确认安装依赖时可跳过本地检查，不能绕过店铺授权。 |
| body | 任意 JSON 值 | 否 | 本读取操作忽略，不进入查询串。 |
| requestBody | 任意 JSON 值 | 否 | 本读取操作忽略，不进入查询串。 |
| contentType | string | 否 | 本读取操作忽略，不进入查询串。 |
| --inline | CLI flag | 否 | 保存完整响应，同时强制完整打印。 |
| --no-cache | CLI flag | 否 | 可显式传入；业务封装无论是否传入均关闭缓存。 |

依赖检查、无缓存、选店、查询编码、body 优先级及落盘约定见 [运行约定](../api.md#运行约定)。

#### Shopee 业务参数与限制

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| 顶层业务查询字段 | string / number / boolean | 否 | 脚本提供通用查询字段透传，不固定分页字段、默认值或枚举；筛选或分页字段须由对应官方操作支持，不能虚构 page、pageSize 或列表参数。字典和数组不进入查询串。 |

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 网关业务状态；按公共基本规则判断。 |
| errmsg | string | 网关消息；保留原始错误说明。 |
| httpStatus | integer | Shopee 上游 HTTP 状态，与调用 LinkFox 的外层 HTTP 状态不同。 |
| body | string | Shopee 原始 JSON 响应字符串；不删除原始内容。 |
| contentType | string | 上游响应内容类型（若返回）。 |
| error / details | string | HTTP 非 JSON 错误或连接错误时，公共调用器可能返回错误和原始详情。 |

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| api | string | 本次 Top Picks 操作名。 |
| developerProxy | object | 网关完整响应，包括原始 body 和错误。 |
| resolvedPath | string | 实际转发的 `api/v2/top_picks/...` 路径。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败为 null。 |
| queryString | string | 生成的查询串，仅非空时出现。 |
| getTopPicksList | object / 任意 JSON 值 / null | 网关基础状态正常且上游 httpStatus 为 200 时解析 body；空白或无法解析时为 null。 |
| getTopPicksListResponse | 任意 JSON 值 | 解析结果为对象且其 response 非 null 时提取的 Shopee 业务响应。 |

#### Shopee 解析结果

| 字段 | 类型 | 说明 |
|---|---|---|
| response | 任意 JSON 值 | Shopee 业务数据；嵌套集合及商品字段完整保留，以对应官方文档与实际响应为准，不假定固定嵌套结构。 |
| 其他上游字段 | 以实际响应为准 | 包括实际上游返回的状态、错误或追踪字段，不删除、不推测；解析出 response 不等于业务成功。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 网关正常后仍检查 Shopee 的 `httpStatus` 与解析 body 中的业务错误；不能仅凭网关成功或出现 response 宣称操作成功。
- 上游 `httpStatus=200` 才解析业务 body；其他状态保留原始网关响应，不解释成业务成功。
- 列表为空时说明本次返回为空，按用户范围核对店铺与集合，不自动翻页试探。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/shopee/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "path": "api/v2/top_picks/get_top_picks_list",
  "method": "GET",
  "shopId": "67890"
}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-shopee-store-top-picks",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
