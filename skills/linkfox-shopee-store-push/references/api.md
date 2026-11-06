# Shopee Push 推送机制 接口说明

4 个 Push 业务操作和 1 个令牌兼容操作，共 5 个接口（不含 Feedback 与公共账号引导）。

- [设置推送配置（set_app_push_config）](apis/set-app-push-config.md)
- [获取推送配置（get_app_push_config）](apis/get-app-push-config.md)
- [获取丢失推送消息（get_lost_push_message）](apis/get-lost-push-message.md)
- [确认消费丢失推送消息（confirm_consumed_lost_push_message）](apis/confirm-consumed-lost-push-message.md)
- [店铺令牌兼容查询（storeTokens）](#接口店铺令牌兼容查询storetokens)

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

## 脚本运行约定

| 项目 | 说明 |
|---|---|
| 依赖检查 | `python scripts/check_auth_dependency.py [--json]`；找到依赖返回 0；缺失返回 42，stderr 含 `DEPENDENCY_MISSING:`。 |
| 独立入口 | `python scripts/<接口名>.py '<JSON 参数>' [--inline] [--no-cache]`。 |
| 通用入口 | `python scripts/push_api.py '<JSON 参数>' [--inline] [--no-cache]`，JSON 必须包含 `api`，值为清单中的 4 个 Push 操作之一。 |
| 无缓存 | 业务封装调用公共 `call_api.run` 时始终传 `--no-cache`，不读取或保存响应缓存。公共调用器可能建立空缓存目录，不代表启用响应缓存。 |
| 网关兼容 | 优先 `LINKFOX_TOOL_GATEWAY`，其次 `SHOPEE_API_BASE_URL`，默认 `https://tool-gateway.linkfox.com`；两个 API Key 环境变量均保留。 |
| 请求追踪 | 保留 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 请求头。 |
| 输出 | 完整结果保存于当前工作目录的 `linkfox/<日期>/<session>/data/`；不回退家目录或临时目录，在请求前预建具体会话目录并预留输出文件，不可写时立即报错；请求后若保存失败则报错，不自动重发。小于等于 8000 字节全量输出，大响应摘要，`--inline` 强制全量。 |
| 调用约束 | 同一会话、同一参数组合默认只调用一次；调用关闭响应缓存，应优先读取已保存的结果，不依赖缓存跳过请求。 |

Push 业务通过 `POST /shopee/developerProxy` 转发，上游路径必须为 `api/v2/push/...`。Push 配置与补推通常属于 Partner/App 级；经本网关调用时，无论直接调用还是业务脚本，都必须提供 `shopId` 或 `merchantId` 至少一个，由网关读取后台授权令牌。两者同时传入时均保留；网关还会将它们分别作为 `shop_id` / `merchant_id` 加入上游查询串。`skipDepCheck` 仅跳过本地依赖安装检测，不绕过授权。

业务参数和响应分别见各接口文件；脚本仅映射参数，不内置上游未列明的字段枚举、分页上限或消息体结构。失败、空结果或写入结果不确定时，不自动翻页、重发配置或重复确认。

## 接口：店铺令牌兼容查询（storeTokens）

共享函数 `resolve_store_tokens(params)` 提供令牌兼容查询；授权由授权技能负责，4 个业务入口不自动调用该函数。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/shopee/storeTokens`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| shopId | string | 与 merchantId 至少一个 | 店铺 ID；兼容函数将非空值转为字符串。 |
| merchantId | string | 与 shopId 至少一个 | 商户 ID；两者同时提供时都发送。 |

### 响应结构

| 字段 / 对象 | 类型 | 说明 |
|---|---|---|
| 完整响应 | JSON value | 函数直接返回完整令牌查询 JSON；令牌字段及嵌套结构以实际返回为准。正常预期为 object，异常非对象 JSON 的输出封装见下表。 |
| errcode | integer / string / null | 返回时按公共响应码基本规则判断。 |
| errmsg | string | 返回时保留网关说明。 |

#### 异常非对象响应的脚本输出

正常对象响应保持原样；仅在该兼容函数收到非对象 JSON 时，公共输出层使用下列对象落盘和打印，函数仍返回原 JSON 值，不误判为业务成功。

| 字段 | 类型 | 说明 |
|---|---|---|
| gatewayResponse | array / string / number / boolean / null | 完整非对象原始响应。 |
| transportHttpStatus | integer / null | LinkFox 外层状态；连接失败为 null。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 未指定店铺或商户时，本地退出 1，不发送请求。令牌和授权处理继续使用授权技能，不将该兼容函数扩展成新的授权工作流。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/shopee/storeTokens" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"shopId":"67890"}'
```

---

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-shopee-store-push",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
