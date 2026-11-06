# Temu 全球站电商促销 接口说明

本技能定义 6 个促销转发操作与 1 个加签文件下载接口。通用代理、站点兼容入口与认证探测复用这些端点，不另计接口。公共认证及算力引导脚本用于处理认证或用量问题，不计为促销业务操作。

| 操作 | 独立接口文档 |
|---|---|
| `bg.promotion.activity.query` | [促销活动查询](apis/bg-promotion-activity-query.md) |
| `bg.promotion.activity.candidate.goods.query` | [活动候选商品查询](apis/bg-promotion-activity-candidate-goods-query.md) |
| `bg.promotion.activity.goods.query` | [活动已报名商品查询](apis/bg-promotion-activity-goods-query.md) |
| `bg.promotion.activity.goods.enroll` | [活动商品报名](apis/bg-promotion-activity-goods-enroll.md) |
| `bg.promotion.activity.goods.operation.query` | [活动商品操作结果查询](apis/bg-promotion-activity-goods-operation-query.md) |
| `bg.promotion.activity.goods.update` | [活动商品更新](apis/bg-promotion-activity-goods-update.md) |
| 加签文件下载 | [本页接口定义](#接口加签文件下载) |

Partner 菜单定位见 [partner-global-catalog.md](partner-global-catalog.md)，辅助脚本与店铺令牌见 [access-token.md](access-token.md)。

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

## 运行约定

### 网关、认证兼容与令牌

| 项目 | 约定 |
|---|---|
| 基础地址 | `LINKFOX_TOOL_GATEWAY` 优先，其次 `TEMU_API_BASE_URL`、`STORE_API_BASE_URL`，默认 `https://tool-gateway.linkfox.com`；去除尾部 `/`。 |
| LinkFox 密钥 | JSON `token` → `linkfoxToken` → `linkfox_token` 优先，其次 `LINKFOX_AGENT_API_KEY` → `LINKFOXAGENT_API_KEY`。业务脚本同时发送 `Authorization` 与 `Token`，值一致。 |
| Temu 店铺令牌 | 直接 accessToken 优先；否则用 storeKey + site + managementType + tokenPurpose 从本地读取；不将 storeKey 发送到网关。 |
| 全球促销默认值 | site=`global`、managementType=`semi-managed`、tokenPurpose=`product-inventory`；tokenPurpose 只用于本地令牌匹配。 |
| 上游 Global 路径 | POST `https://openapi-b-global.temu.com/openapi/router`，网关根据 site 选择；业务操作写 Body.type，不拼入 URL。 |
| 业务参数映射 | 全球促销入口优先使用对象 params，否则收集顶层非保留业务字段（含 request）为 params。多站点 temu_proxy.py 仅接受显式对象 params，非对象时本地报错。 |
| 缓存 | 业务入口均以 `--no-cache` 调用公共 run，不读取或保存响应缓存，也不提供第二层缓存；公共调用器可能创建空缓存目录。 |
| 输出 | 业务脚本将完整响应保存到当前工作目录 linkfox 下，禁止回退 /tmp；先验证当前目录可写，再发请求。响应超过 8 KB 时输出摘要，可用 --inline 全量展示；文件名含微秒以免同秒覆盖。 |
| 辅助 CLI | check_linkfox_token.py 输出脱敏密钥及可达性判断；temu_token_guide.py 输出授权步骤；save_temu_access_token.py 保存令牌并返回元数据；list_temu_access_tokens.py 默认脱敏；get_temu_access_token.py 读取并返回原始 accessToken。详见授权说明。 |
| Python 超时兼容 | CLI 默认 HTTP 超时 150 秒；Python 辅助函数支持 timeout 参数，由业务封装交给公共调用器的传输函数，不另建 HTTP 实现。 |

`check_linkfox_token.py` 使用同一 `/temu/proxy` 的最小探测请求（site=cn、managementType=full-managed、accessToken=probe、type=probe），不是新的有效促销操作；识别 message、error、errmsg、msg 中的认证、余额或配额错误，以及外层 HTTP 401。正常 HTTP 下只将预期的 code=1002 参数类探测结果或明确的 2xx errcode 视为网关接受密钥的证据；空对象、连接错误和其他失败均不报告有效，不自动重试。
通用代理支持已有 Temu type，但本技能只提供清单内 6 个促销操作的业务定义；其余 type 必须有对应资料，不从示例推断接口。

## 接口：加签文件下载

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/fileDownload`

### 请求参数

本接口额外要求 Header `Token` 与 `Authorization` 同值。调用脚本：全球站 `scripts/temu_global_file_download.py`；多站点兼容 `scripts/temu_file_download.py`。

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| site | string | 是 | 全球站入口默认 global；通用入口显式传入 cn / partner / us / global / eu，必须小写。 |
| managementType | string | 是 | 全球站入口默认 semi-managed；通用入口显式传入 full-managed / semi-managed，必须小写。 |
| accessToken | string | 是（线上请求） | Temu 店铺令牌；脚本支持由 storeKey 解析。 |
| url | string | 是 | 原始加签文件 URL，保持完整内容，不丢失签名查询参数。 |

| 脚本参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| storeKey | string | 与 accessToken 二选一 | 本地店铺键；选择令牌后不发送到网关。 |
| tokenPurpose | string | 否 | 全球站入口默认 product-inventory；通用入口默认 default，仅用于本地令牌查找。 |
| token / linkfoxToken / linkfox_token | string | 否 | 兼容 JSON LinkFox 密钥，优先于环境变量；不与 accessToken 混用。 |
| --inline | CLI flag | 否 | 全量输出，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 封装始终添加，不读取或保存响应缓存。 |

### 响应结构

下表定义网关外层字段；下载内容的业务结构以实际返回为准，不将接口结果推断为已保存本地素材文件。

| 字段 | 类型 | 说明 |
|---|---|---|
| transportHttpStatus | integer / null | 脚本提供的 LinkFox 外层 HTTP 状态码；连接失败为 null。与网关 code 和 Temu errorCode 分开判断，不以业务 success 覆盖 HTTP 失败。 |
| errcode | integer / string / null | 按公共响应码基本规则判断。 |
| errmsg | string | 网关错误说明。 |
| code | integer | 网关错误码，1002 参数或令牌问题、1003 转发失败。 |
| body | string | 若返回，则保留原始内容；下载入口不添加 temuBody。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- `code=1002` 时检查参数和 LinkFox 密钥；`code=1003` 时检查 Temu 令牌、tokenPurpose、白名单和 URL。保留原始错误，不连续试探。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/temu/fileDownload" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Token: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '
{
  "site": "global",
  "managementType": "semi-managed",
  "accessToken": "TOKEN",
  "url": "https://example.com/signed-file-url"
}
'
```

---

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-temu-promotion-global",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
