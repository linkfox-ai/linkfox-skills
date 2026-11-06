# Shopee 关注有礼 接口说明

## 活动操作文档索引

- [创建关注有礼活动（add_follow_prize）](./apis/add-follow-prize.md)
- [删除关注有礼活动（delete_follow_prize）](./apis/delete-follow-prize.md)
- [提前结束关注有礼活动（end_follow_prize）](./apis/end-follow-prize.md)
- [更新关注有礼活动（update_follow_prize）](./apis/update-follow-prize.md)
- [查询关注有礼详情（get_follow_prize_detail）](./apis/get-follow-prize-detail.md)
- [查询关注有礼列表（get_follow_prize_list）](./apis/get-follow-prize-list.md)

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

## 接口：查询店铺授权状态（storeTokens）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/shopee/storeTokens`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| shopId | string | 与 merchantId 至少一个 | 店铺 ID，辅助函数将其转为字符串；两者均有值则均转发。 |
| merchantId | string | 与 shopId 至少一个 | 商户 ID，辅助函数将其转为字符串。 |
| appType | string | 否 | 直接网关请求可选 `erp` / `ad`，默认 `erp`；本技能辅助函数仅传选店字段，因此使用默认 `erp`。 |

辅助入口为 `scripts/_shopee_follow_prize_common.py` 的 `resolve_store_tokens(params)`，无独立 CLI；该函数不自动进行依赖检测，调用方须先完成授权依赖检查与选店。活动脚本默认不调用本接口，不额外查询授权状态。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| authRecordId | integer（Long） | 授权记录 ID。 |
| shopId / merchantId | string | 授权记录中的店铺 / 商户 ID。 |
| shopIdList / merchantIdList | string | 店铺 / 商户 ID 列表的 JSON 字符串。 |
| appType | string | 授权应用类型：`erp` / `ad`。 |
| expireIn | integer（Long） | access_token 有效期（秒），不据此推算未提供的到期时间。 |
| status | string | `ACTIVE` / `EXPIRED`；当前服务按授权记录是否有 accessToken 判定，不保证下一次活动请求必然成功。 |
| message | string | 授权状态说明。 |
| errcode | integer / string / null | 若返回，按公共基本规则判断。 |
| errmsg | string | 若返回，保留网关消息。 |

#### 脚本本地附加字段

辅助函数保留网关 JSON 字段，并添加外层状态用于判断认证或请求失败；服务端管理令牌，不返回原始 token。

| 字段 | 类型 | 说明 |
|------|------|------|
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败为 null。 |
| error | string | 公共调用器在连接错误或非 JSON HTTP 错误时生成的本地诊断，非网关成功响应字段。 |
| details | string | 公共调用器保留的非 JSON HTTP 错误正文，存在时输出。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 返回值用于查看已有授权的状态，不能将调用完成理解为新授权完成；成功时没有 token 字段是正常行为。授权记录缺失或状态为 `EXPIRED` 时交回授权技能处理；网关认证或用量错误按 onboarding 指引处理。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/shopee/storeTokens" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"shopId":"67890"}'
```

## 脚本运行约定

本节适用于六个活动 CLI 及公共辅助函数；各接口的业务参数和响应字段见对应接口定义。

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| skipDepCheck | boolean | 否 | 仅六个活动 CLI 和通用入口识别，默认 false；跳过本地依赖安装检查，不绕过店铺授权。`resolve_store_tokens(params)` 不读取该字段，调用方应先完成依赖检查。 |
| --inline | CLI flag | 否 | 六个活动 CLI 和通用入口支持，强制全量打印，仍保存完整响应；辅助函数按进程 argv 中的同名选项决定展示方式。 |
| --no-cache | CLI flag | 否 | 业务封装无响应缓存；所有业务封装调用公共 run 时均加入此选项，不读取或写入响应缓存。公共调用器可能建立空缓存目录。 |

依赖检查返回 0 表示找到 `linkfox-shopee-store-auth`；返回 42 且 stderr 含 `DEPENDENCY_MISSING:` 表示缺失。检测路径由 `scripts/check_auth_dependency.py` 的 `candidate_skill_roots()` 确定；活动脚本的依赖检测超时为 10 秒，检测异常或返回非 0 时均以 42 退出。
网关地址按 `LINKFOX_TOOL_GATEWAY`、`SHOPEE_API_BASE_URL`、`https://tool-gateway.linkfox.com` 顺序选择；密钥兼容 `LINKFOX_AGENT_API_KEY` 和 `LINKFOXAGENT_API_KEY`。公共请求同时携带环境变量中的 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME`。
业务响应保存到当前工作目录的 `linkfox/<日期>/<session>/data/`，使用 `SESSION_ID` 聚合；文件名保留微秒时间戳，避免同秒覆盖。请求前检查完整会话目录并预留输出文件；目录或文件不可写时直接报错，不回退到 `/tmp`。不自动重试、翻页或更换条件。

通用入口：`python scripts/follow_prize_api.py '<JSON 参数>' [--inline] [--no-cache]`；JSON 中的 `api` 取接口清单中六个活动操作名之一。单操作 CLI 的用法相同，但操作已由脚本固定，无需传 `api`。


---

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-shopee-store-follow-prize",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
