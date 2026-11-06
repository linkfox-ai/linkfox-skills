# 智慧芽检索式专利检索 接口说明

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

## 接口：检索式专利检索

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/zhihuiya/querySearchPatent`

### 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| queryText | string | 是 | 有效的 Analytics 检索式，最大 12000 字符；字段前缀和布尔语法见下表。 |
| limit | integer | 否 | 返回专利个数，范围 1–1000，默认 10。 |
| offset | integer | 否 | 偏移量，范围 0–19999，默认 0；`limit + offset` 不能超过 20000。 |
| sort | array | 否 | 排序条件数组，每个元素为 `{field, order}`，结构见下表。接口未声明默认排序；技能在用户未指定时主动传入 `SCORE` / `DESC`，脚本不擅自覆盖请求。 |
| stemming | integer | 否 | 是否开启截词检索：`1` 开启 / `0` 关闭，默认关闭。 |
| collapseType | string | 否 | 去重方式，默认 `ALL`：`ALL`（不去重）、`APNO`（按申请号）、`DOCDB`（按简单同族）、`INPADOC`（按 INPADOC 同族）、`EXTEND`（按 PatSnap 扩展同族）。 |
| collapseBy | string | 否 | 选择去重后保留的代表记录所用字段：`APD`（申请日）、`PBD`（公开日）、`AUTHORITY`（受理局）、`SCORE`（相关性）。 |
| collapseOrder | string | 否 | 去重排序顺序：`OLDEST`（最早）/ `LATEST`（最新）。 |
| collapseOrderAuthority | array | 否 | 受理局优先级数组，仅 `collapseBy=AUTHORITY` 时有效；按输入顺序保留对应受理局的专利。 |

#### sort 数组元素

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| field | string | 是（提供排序元素时） | `PBDT_YEARMONTHDAY`（公开日）、`APD_YEARMONTHDAY`（申请日）、`ISD`（授权日）、`SCORE`（查询相关性）。 |
| order | string | 是（提供排序元素时） | `DESC`（降序）/ `ASC`（升序）。例如 `[{"field":"SCORE","order":"DESC"}]`。 |

#### 检索式语法

| 语法 | 含义 |
|------|------|
| `TACD: <term>` | 在标题、摘要、权利要求和说明书中检索。 |
| `TAC: <term>` | 在标题、摘要和权利要求中检索。 |
| `TA: <term>` | 在标题和摘要中检索。 |
| `AND` / `OR` / `NOT` | 布尔运算，组合检索词或字段条件。 |

例如，`TACD: virtual reality` 在标题、摘要、权利要求、说明书中检索 virtual reality；`TAC: drone AND camera` 在标题、摘要、权利要求中检索同时包含 drone 和 camera 的专利。

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| JSON 参数 | JSON object | 是 | 与上方请求体一致，作为第一个非选项参数传入；非对象 JSON 在本地报错，不发送请求。脚本不自动改写关键词、排序、分页或去重条件。 |
| --inline | CLI flag | 否 | 强制完整打印，同时保存响应。 |
| --no-cache | CLI flag | 否 | 禁用默认的 24 小时本地响应缓存；不读取或保存缓存，仍保存完整响应。 |

- 默认缓存路径为 `<cwd>/linkfox/.cache/linkfox-zhihuiya-retrieval-patent-search/linkfox-zhihuiya-retrieval-patent-search-<hash>.json`，`<hash>` 为对按键排序、`ensure_ascii=False` 的 JSON 参数进行 SHA-256 后取前 16 位；有效期 24 小时。可读取该路径下仍在有效期内的缓存，缓存命中会标记 `_cache.hit=true`；仅由公共调用器维护这一层缓存。
- 完整响应只保存在当前工作目录的 `linkfox/<YYYY-MM-DD>/<session>/data/`；优先用 `SESSION_ID` 聚合同一任务，否则在进程内生成稳定会话标识。请求前检查实际会话及 `data` 保存目录是否可写，不可写时报错；禁止回退 `/tmp`、家目录、临时目录或其他工作区。
- `LINKFOX_TOOL_GATEWAY` 可覆盖默认网关，尾部 `/` 会移除。认证优先读取 `LINKFOX_AGENT_API_KEY`，为空时兼容 `LINKFOXAGENT_API_KEY`；两个变量均为空时不发送请求，按 `onboarding.md` 处理。
- 透传环境变量 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 作为同名请求头；超时、请求方式及其他请求头沿用公共规则。
- 同一会话、同一参数组合默认只调用一次。失败或空结果不得自动更换关键词、改写检索式、翻页或连续重试；必须先说明额外消耗并取得用户确认，再执行后续调用。
- 仅返回专利列表与基本字段；完整著录、全文、法律状态、同族、图片或 PDF 需要将 `patentId` / `pn` 交给对应专利技能查询。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer | 业务状态码，成功值为 `200`；完整判定按公共规则。 |
| errmsg | string | 成功消息为 `ok`，否则为错误描述。 |
| total | integer | 本次返回结果数。 |
| data | array | 专利记录列表，每项含下表定义的基本资料，以实际返回为准。 |
| columns | array | 列渲染元信息，并非专利记录；长度可能与 `data` 不一致，甚至更长；元素子字段以实际返回为准，不预设固定结构。 |
| type | string | 渲染样式，例如 `tableListWorkbenches`。 |
| costToken | integer | 接口返回的计费 Token 数值，不能直接等同于用户算力，也不按 `data` 条数自行累乘；用户算力预估见 SKILL.md，实际扣除以网关计费为准。 |
| allRecordsCount | integer | 检索式命中的专利总数，与本页返回数不同。 |

#### data 数组元素

| 字段 | 类型 | 说明 |
|------|------|------|
| patentId | string | 智慧芽内部专利 ID。 |
| pn | string | 公开（公告）号。 |
| title | string | 专利标题。 |
| apdt | integer | 申请日，格式 `YYYYMMDD`。 |
| pbdt | integer | 公开日，格式 `YYYYMMDD`。 |
| apno | string | 申请号。 |
| authority | string | 受理局，例如 `US`。 |
| inventor | string | 发明人，多人以 `\|` 分隔。 |
| originalAssignee | string | 原始申请人，多个以 `\|` 分隔。 |
| currentAssignee | string | 当前申请人，多个以 `\|` 分隔。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

| errcode / 场景 | 含义 | 处理建议 |
|------|------|------|
| 400 | 参数错误。 | 缺少 `queryText` 时返回 `{"errcode":400,"errmsg":"queryText 为必填项"}`；核对检索式和分页边界，不自动付费重试。 |
| 401，或消息含 `authorized error` | 认证失败，即使外层 HTTP 为 200 也应处理。 | 按 `onboarding.md` 的认证流程处理，不因外层 HTTP 成功而忽略业务错误。 |
| 402 | 算力不足，即使外层 HTTP 为 200 也应处理。 | 按 `onboarding.md` 的算力流程处理。 |
| 501，消息含 `No permission or API package quota has exceeded the limit` | 当前 Key 未开通检索式检索专利权限，或套餐配额已用尽。 | 属权限或套餐问题，不能仅靠充值解决；停止重试，提示用户开通、启用或恢复对应检索式检索专利 API 套餐及配额，再由用户决定后续查询。 |
| 正常响应但没有专利记录 | 未找到匹配结果。 | 展示本次空结果，不自动更换关键词、改写检索式或翻页。 |

权限错误示例：`{"errcode":501,"errmsg":"检索式检索专利失败: No permission or API package quota has exceeded the limit!"}`。

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/zhihuiya/querySearchPatent" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"queryText":"TACD: virtual reality","limit":10,"sort":[{"field":"SCORE","order":"DESC"}]}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-zhihuiya-retrieval-patent-search",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```