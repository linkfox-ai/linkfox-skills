# Temu 全球站价格与供货价管理 接口说明

本技能包含 5 个定价操作与 1 个加签下载接口；通用代理和认证探测复用既有端点，不重复计数。

- [推荐基础价/供货价估算（`temu.local.goods.baseprice.recommend`）](apis/temu-local-goods-baseprice-recommend.md)
- [推荐供货价查询（`temu.local.goods.recommendedprice.query`）](apis/temu-local-goods-recommendedprice-query.md)
- [定价单列表查询（`bg.local.goods.priceorder.query`）](apis/bg-local-goods-priceorder-query.md)
- [批量修改 SKU 基础价（`bg.local.goods.priceorder.change.sku.price`）](apis/bg-local-goods-priceorder-change-sku-price.md)
- [SKU 供货价列表查询（`bg.local.goods.sku.list.price.query`）](apis/bg-local-goods-sku-list-price-query.md)
- [加签文件下载](#接口加签文件下载)
- [Partner 菜单目录](partner-global-catalog.md)

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

### 认证与站点兼容

| 参数 / 环境变量 | 类型 | 必填 | 说明 |
|---|---|---|---|
| token / linkfoxToken / linkfox_token | string | 否 | JSON 中按此顺序取第一个非空值，优先于环境变量；仅用于 LinkFox 用户认证，不转发到 Temu 业务 params。 |
| LINKFOX_AGENT_API_KEY / LINKFOXAGENT_API_KEY | string | 条件 | JSON 未给密钥时按此顺序读取。 |
| LINKFOX_TOOL_GATEWAY / TEMU_API_BASE_URL / STORE_API_BASE_URL | string | 否 | 基础地址按此顺序读取，默认 https://tool-gateway.linkfox.com，移除尾部斜杠。 |
| storeKey | string | 与 accessToken 二选一 | 本地店铺键，实际网关 Body 传解析出的 accessToken；直接 accessToken 优先。 |
| tokenPurpose | string | 否 | 全球站脚本默认 product-inventory；通用多站点脚本默认 default；用于本地令牌检索，不发往网关。 |
| site / managementType | string | 条件 | 全球站专用入口默认 global / semi-managed，转换为小写；多站点入口必须显式传入并校验枚举。 |
| params | object | 否 | 全球站入口优先取显式 params 对象，否则将非保留顶层业务字段转为 params；顶层 request 整体保留。 |
| --inline | CLI flag | 否 | 强制打印完整响应，同时保存文件。 |
| --no-cache | CLI flag | 否 | 兼容此选项；业务脚本不启用响应缓存，业务封装调用 call_api.run 时始终追加，关闭缓存读取和写入。 |
| TEMU_TOKEN_STORE_PATH | string | 否 | 本地 Token 文件路径，默认 ~/.linkfox/temu-access-tokens.json。 |
| SESSION_ID / MESSAGE_ID / MODE_ID / APP_NAME | string | 否 | 保留同名请求头；SESSION_ID 同时用于任务落盘聚合。 |

网关请求头在公共规则基础上同时发送 `Authorization` 与 `Token`（同值）。LinkFox 密钥与 Temu accessToken 是两套认证，不能互换。Token 本地存储不是业务响应缓存；仅在用户要求保存时运行保存脚本。

全球站专用脚本默认从 `storeKey + global + semi-managed + product-inventory` 读取令牌。显式传 tokenPurpose 时同样补齐默认 site 和 managementType，防止查错或漏查本地店铺记录。

### CLI 与输出

业务入口支持 `python scripts/<脚本>.py '<JSON 参数>' [--inline] [--no-cache]`，不提供 JSON 时输出用法并退出。全量响应只保存一份，再按 8 KB 阈值输出；代理响应保留 body，并在可解析时添加 temuBody，下载响应不强行解析为 Temu 业务对象。输出包含 transportHttpStatus，用于区分网关 HTTP 与 Temu 业务状态。

业务封装无响应缓存；公共调用器具备 24 小时缓存能力，本技能始终禁用读取和写入。公共调用器可能创建空 .cache 目录，不代表已有响应缓存，也不应因此重复请求或复用旧结果。

会话数据保存在当前工作目录 linkfox/<YYYY-MM-DD>/<session>/data/ 下，文件名为 linkfox-temu-price-global-<接口标识>-<timestamp>.json。业务适配层先验证当前目录可写，覆盖公共调用器的目录回退行为，不回退到 /tmp 或家目录；高精度时间戳避免同一秒内覆盖响应。

### 本地授权辅助脚本

| 脚本 | 输入 / 输出与约定 |
|---|---|
| scripts/temu_token_guide.py | shopType（或 managementType）、tokenPurpose、site；输出对应后台授权步骤。 |
| scripts/save_temu_access_token.py | storeKey、site、managementType、accessToken 必填；tokenPurpose 默认 default，label 可选；按店铺、站点、模式与用途覆盖或新增记录。 |
| scripts/list_temu_access_tokens.py | 默认脱敏；JSON mask=false 时读取原值。 |
| scripts/get_temu_access_token.py | storeKey、site、managementType 必填；tokenPurpose 默认 default；返回 found 与 token，未找到时退出 1。 |
| scripts/check_linkfox_token.py | 接受可选 JSON 密钥，以 /temu/proxy 的 probe 请求探测；HTTP 为 2xx 且收到预期 1002 参数响应时才提供认证可用线索，不代表 Temu 店铺已授权或业务接口可用。同时返回 code 与 errcode 时，errcode 必须满足公共正常响应规则；仅含 errcode=1002 的响应也兼容参数探测，不表述为业务成功。此脚本会发请求，不应作为每次业务操作的强制前置。 |

Temu 授权应用、主账号、多站点令牌、过期与 IP 白名单见 [授权说明](access-token.md) 和 [授权流程](authorization-flow.md)。

## 接口：加签文件下载

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/fileDownload`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| site | string | 是；全球入口有默认值 | 全球入口默认 global；多站点入口接受 cn / partner / us / global / eu。 |
| managementType | string | 是；全球入口有默认值 | 全球入口默认 semi-managed；通用入口支持 full-managed / semi-managed。 |
| accessToken | string | 是 | Temu 店铺令牌；脚本可通过 storeKey 解析后注入。 |
| url | string | 是 | 待下载的 Temu 加签资源 URL，保留原 URL 与签名，不自行修改。 |

JSON 密钥、storeKey、tokenPurpose 与 CLI 选项均为脚本兼容项，见脚本运行约定；全球与多站点入口复用同一端点。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 网关状态码，按公共规则判断。 |
| errmsg | string | 网关错误说明。 |
| code | integer | 网关错误码：1002 参数 / Token，1003 转发失败。 |
| body | string（若返回） | 原始网关载荷；下载结果字段以实际返回为准，不预设文件链接或二进制结构。 |
| transportHttpStatus | integer / null | 脚本附加的 LinkFox HTTP 状态；连接失败为 null。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 根据实际返回内容判断资源是否取得；不将 HTTP 请求完成直接表述为文件已保存。
- code=1002 时核对参数与 LinkFox Token；code=1003 时核对 Temu Token、IP 白名单、资源签名及网络。保留返回原文，不循环试探签名 URL。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/temu/fileDownload" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Token: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"site":"global","managementType":"semi-managed","accessToken":"<TEMU_ACCESS_TOKEN>","url":"https://example.com/signed-file-url"}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-temu-price-global",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
