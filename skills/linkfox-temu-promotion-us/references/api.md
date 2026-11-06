# Temu 美国站电商促销 接口说明

本技能包含 6 项促销操作和 1 项加签文件下载，共 7 项；Feedback 与公共账号引导不计入业务接口。通用代理和认证探测复用 /temu/proxy，不另计业务操作。

| type | 说明 | 接口文档 |
|------|------|----------|
| `bg.promotion.activity.candidate.goods.query` | 活动候选商品查询 | [apis/bg-promotion-activity-candidate-goods-query.md](apis/bg-promotion-activity-candidate-goods-query.md) |
| `bg.promotion.activity.goods.enroll` | 活动商品报名 | [apis/bg-promotion-activity-goods-enroll.md](apis/bg-promotion-activity-goods-enroll.md) |
| `bg.promotion.activity.goods.operation.query` | 活动商品操作结果查询 | [apis/bg-promotion-activity-goods-operation-query.md](apis/bg-promotion-activity-goods-operation-query.md) |
| `bg.promotion.activity.goods.query` | 活动已报名商品查询 | [apis/bg-promotion-activity-goods-query.md](apis/bg-promotion-activity-goods-query.md) |
| `bg.promotion.activity.goods.update` | 活动商品更新 | [apis/bg-promotion-activity-goods-update.md](apis/bg-promotion-activity-goods-update.md) |
| `bg.promotion.activity.query` | 促销活动查询 | [apis/bg-promotion-activity-query.md](apis/bg-promotion-activity-query.md) |

Partner 菜单与接口文档地址见 [partner-us-catalog.md](partner-us-catalog.md)，促销索引见 [apis/README.md](apis/README.md)。

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

## 脚本运行与认证兼容

- 促销请求通过 POST /temu/proxy 转发；Temu type 位于 Body，不是 URL path。US 上游地址为 https://openapi-b-us.temu.com/openapi/router；授权链路中的紫鸟转发路径为 /temu-proxy/{site}/{managementType}。
- 根地址优先级：LINKFOX_TOOL_GATEWAY → TEMU_API_BASE_URL → STORE_API_BASE_URL → https://tool-gateway.linkfox.com；去掉末尾斜杠。
- 业务封装优先读取 JSON token / linkfoxToken / linkfox_token，再取 LINKFOX_AGENT_API_KEY / LINKFOXAGENT_API_KEY；Authorization 与 Token 请求头同值，并传递 SESSION_ID、MESSAGE_ID、MODE_ID、APP_NAME。
- 专用促销脚本固定 type；temu_us_proxy.py 可传任意 type，temu_proxy.py 校验多站点参数。这些是同一代理的兼容入口，并非本技能额外定义了其他促销接口。
- 业务封装调用 call_api.run 并固定 --no-cache，不读取或写入 API 响应缓存。公共调用器可能建立空缓存目录；完整响应仍按输出策略保存。
- 业务输出只落当前工作目录的 linkfox/，忽略 ACPX_WORKSPACES 的替代目录，不回退家目录或临时目录；拒绝 /tmp 路径。SESSION_ID 必须是非空的单级目录名，不含路径分隔符、盘符或 . / ..；无有效目录名时在请求前报错。请求前检查会话数据目录可写。完整响应只保留一份，body 可解析时补充 temuBody 后更新同一文件，再打印完整结果或摘要。
- HTTP 成功但响应不是有效 JSON 时，保留原文至 details 并记录 error 与 transportHttpStatus；不把它当作业务成功，不自动重试。
- 脚本调用命令为 `python scripts/<脚本名>.py '<JSON 参数>' [--inline] [--no-cache]`；小响应按 UTF-8 字节数不超过 8000 时完整显示，大响应仅显示摘要，--inline 强制全量。
- 本地授权工具保留：temu_token_guide.py 输出手动授权步骤；save_temu_access_token.py 保存，list_temu_access_tokens.py 默认脱敏（mask=false 可显式查看），get_temu_access_token.py 精确读取。默认文件 ~/.linkfox/temu-access-tokens.json，可由 TEMU_TOKEN_STORE_PATH 覆盖；同一店铺、站点、托管方式、用途覆盖旧值，其他令牌隔离保留。这是令牌存储，不是 API 响应缓存。
- 授权细节见 [access-token.md](access-token.md) 与 [authorization-flow.md](authorization-flow.md)。本技能 US 默认与通用授权指南中的 cn / partner 推荐用途分别说明，不静默换站点或换令牌用途。
- check_linkfox_token.py 是诊断用探测 CLI，发送 site=cn、managementType=full-managed、accessToken=probe、type=probe 至同一代理；仅在用户需要诊断时执行，不作为每次调用的自动前置请求。网络错误、非 2xx、认证或用量错误不可报告鉴权成功；预期参数错误只能说明网关可达并且未明确拒绝该 Token，不代表店铺授权有效。

## 接口：加签文件下载

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/fileDownload`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| site | string | 是 | 美国站 us；temu_us_file_download.py 默认 us；通用脚本支持 cn / partner / us / global / eu 并要求显式提供。 |
| managementType | string | 是 | US 脚本默认 semi-managed；通用脚本显式提供 full-managed / semi-managed。 |
| accessToken | string | 是 | Temu 店铺令牌；可由脚本从本地 storeKey 解析填入。 |
| url | string | 是 | 要通过 Temu 加签下载的资源 URL，不传空字符串。 |

#### 脚本参数与选项

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| storeKey | string | 与 accessToken 二选一 | 本地店铺索引，仅用于读取，不发送网关；直接 accessToken 优先。 |
| tokenPurpose | string | 否 | US 默认 product-inventory；通用默认 default，按四元组精确读取令牌。 |
| token / linkfoxToken / linkfox_token | string | 否 | JSON 中依次优先的 LinkFox 密钥；否则读两种 API key 环境变量。 |
| --inline | CLI flag | 否 | 完整打印且保留落盘。 |
| --no-cache | CLI flag | 否 | 始终禁用 API 响应缓存。 |

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| body | string | 网关返回的原始响应字符串；按实际返回解释内容，不预设下载链接、编码、文件类型或成功枚举。 |
| code | integer | 网关业务错误：1002 参数或 Token，1003 转发失败。 |
| errcode | integer / string / null | 若返回，按公共响应码规则判断。 |
| errmsg | string | 若返回，按实际网关消息解释。 |
| transportHttpStatus | integer / null | 脚本记录的外层 HTTP 状态；连接失败为 null。 |
| rawResponse | 任意 JSON 类型 | 网关非对象 JSON 的保留值。 |
| error / details | string | 连接错误或非 JSON 响应的说明与原文；HTTP 成功但响应非 JSON 时也保留，不自动重试。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 检查网关 code 与返回内容；1002 核对参数和 LinkFox Token，1003 核对 Temu Token、用途、IP 白名单及网络。下载入口输出网关 JSON，不自动解析或写出未知格式的文件内容。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/temu/fileDownload" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Token: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"site":"us","managementType":"semi-managed","accessToken":"TOKEN","url":"https://example.com/signed-file-url"}'
```

---

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-temu-promotion-us",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
