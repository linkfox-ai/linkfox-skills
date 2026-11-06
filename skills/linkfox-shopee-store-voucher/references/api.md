# Shopee 店铺优惠券 Voucher 接口说明

除 Feedback 外共有 7 个实际接口：六个优惠券操作与一个查询选店授权状态的辅助接口。

| 接口 | 接口文档 |
|---|---|
| 创建优惠券（`add_voucher`） | [apis/add-voucher.md](apis/add-voucher.md) |
| 删除优惠券（`delete_voucher`） | [apis/delete-voucher.md](apis/delete-voucher.md) |
| 提前结束优惠券（`end_voucher`） | [apis/end-voucher.md](apis/end-voucher.md) |
| 查询优惠券详情（`get_voucher`） | [apis/get-voucher.md](apis/get-voucher.md) |
| 查询优惠券列表（`get_voucher_list`） | [apis/get-voucher-list.md](apis/get-voucher-list.md) |
| 更新优惠券（`update_voucher`） | [apis/update-voucher.md](apis/update-voucher.md) |
| 查询选店授权状态（`storeTokens`，辅助） | [本页接口定义](#接口查询选店授权状态storetokens) |

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

依赖 `linkfox-shopee-store-auth`。`check_auth_dependency.py` 支持 `--json`；退出码 0 表示已安装，42 且 stderr 含 `DEPENDENCY_MISSING:` 表示缺失。业务入口默认检查依赖；`skipDepCheck` 只跳过本地安装检测，不绕过服务端授权。搜索路径保留 `LINKFOX_SKILLS_DIR`、`SKILLS_DIR`、`CURSOR_SKILLS_DIR`、`HERMES_SKILLS_EXTERNAL_DIRS`、OpenClaw 路径、当前项目及用户安装路径。

网关优先使用 `LINKFOX_TOOL_GATEWAY`，其次兼容 `SHOPEE_API_BASE_URL`，最后使用公共规则的默认值。认证兼容 `LINKFOX_AGENT_API_KEY` 和 `LINKFOXAGENT_API_KEY`；会话头 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 保留透传。

| 参数 / 选项 | 类型 | 必填 | 默认值与说明 |
|---|---|---|---|
| api | string | 仅通用入口必填 | `voucher_api.py` 按六个已登记操作名分派；独立入口已固定操作。 |
| skipDepCheck | boolean | 否 | 默认 false；跳过本地依赖检查，不改变店铺授权要求。 |
| --inline | CLI flag | 否 | 完整打印并保存完整响应。 |
| --no-cache | CLI flag | 否 | 业务封装调用公共 `call_api.run` 时始终添加；不读取或写入响应缓存文件。公共调用器可能建立空缓存目录。 |

入口形式：`python scripts/<操作名>.py '<JSON 参数>' [--inline] [--no-cache]`；通用入口为 `python scripts/voucher_api.py '<含 api 的 JSON 参数>' [--inline] [--no-cache]`。脚本同时保留供 Python 调用的 runner 与辅助函数。

网关完整响应由公共调用器保存，操作封装后的完整结果另行保存；stdout 仅展示后者。文件统一保存在当前工作目录 `linkfox/<日期>/<会话>/data/`，原始响应文件标识含 `transport`，封装文件标识为 `linkfox-shopee-store-voucher`。小于等于 8000 个 UTF-8 字节时完整打印，更大时显示摘要、网关状态与错误消息及最大列表前三条样本；`--inline` 强制完整打印。业务封装在请求前验证当前目录可写并固定输出根目录，不回退至家目录或临时目录。

## 接口：查询选店授权状态（storeTokens）

共享模块提供 `resolve_store_tokens(params)` 辅助函数，查询当前用户已绑定的选店授权状态，不返回原始令牌。优惠券 runner 不自动调用它；正常操作由服务端根据已选店铺解析令牌，无需额外查询步骤。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/shopee/storeTokens`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| shopId | string | 与 merchantId 至少提供一个 | 店铺 ID；辅助函数将非空输入转为字符串。 |
| merchantId | string | 与 shopId 至少提供一个 | 商户 ID；两者均提供时原样保留，不擅自改选店。 |
| appType | string | 否 | 网关默认 `erp`，枚举 `erp` / `ad`；`resolve_store_tokens` 仅发送选店标识，使用网关默认值。 |

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | 以实际响应为准 | 网关状态字段若返回，按公共规则处理。 |
| errmsg | 以实际响应为准 | 网关消息若返回，保留原文。 |
| authRecordId | Long | 授权主表 ID。 |
| shopId / merchantId | string | 授权记录中的店铺 / 商户 ID。 |
| shopIdList / merchantIdList | string | 对应 ID 列表的 JSON 字符串。 |
| appType | string | 应用类型：`erp` / `ad`。 |
| expireIn | Long | 已记录的令牌有效期，单位为秒；不自行解释为实时剩余有效期。 |
| status | string | `ACTIVE` / `EXPIRED`；当前服务按已存令牌是否非空赋值，不代表实时校验结果。 |
| message | string | 授权说明；服务端说明令牌由后台管理。 |
| 其他原始字段 | 以实际响应为准 | 辅助函数原样返回实际响应，不猜测缺失字段。 |
| transportHttpStatus | integer / null | 业务封装记录的外层 HTTP 状态；连接失败为 null，与上游状态分开。 |
| error | string | 传输失败时的错误说明；HTTP 错误若有可解析 JSON 则保留其原始字段。 |
| details | string | HTTP 错误正文无法解析为 JSON 时保留的原文。 |
| rawResponse | 原响应 JSON 类型 | 仅网关返回非 object JSON 时由兼容封装保留，不将其误作正常对象响应。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 本接口仅查询当前用户已绑定的选店授权状态，不返回原始令牌，也不刷新授权；不在优惠券操作前重复调用。辅助函数未收到选店标识时在本地退出，不发请求。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/shopee/storeTokens" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"shopId":"67890"}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-shopee-store-voucher",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
