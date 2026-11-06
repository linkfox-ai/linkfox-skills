# 智慧芽专利简要著录 接口说明

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

## 接口：查询专利简要著录

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/zhihuiya/simpleBibliography`

### 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| patentId | string | 条件必填 | 专利ID（专利ID和公开号两个参数必须要有一个，如果两个都存在，会优先使用专利ID）。多个专利ID之间用英文逗号 `,` 隔开，最大支持100个 |
| patentNumber | string | 条件必填 | 公开公告号（专利ID和公开号两个参数必须要有一个，如果两个都存在，会优先使用专利ID）。多个公开公告号之间用英文逗号 `,` 隔开，最大支持100个 |

#### 参数约定与使用限制

- `patentId` 是智慧芽内部专利标识，`patentNumber` 是公开公告号，例如 `US11234567B2`、`CN115000000A`。
- 本接口只查询已知标识的简要著录数据，不提供关键词或语义检索、权利要求与说明书全文、法律状态与审查历史、家族与同族分析，也不承担专利估值、专利布局、自由实施或侵权分析。

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 默认值与说明 |
|------|------|------|------|
| JSON 参数 | object | 是 | 首个位置参数，使用上述请求参数；按 JSON 字符串传入。 |
| --inline | CLI flag | 否 | 默认关闭；强制全量打印响应，同时保存文件。 |
| --no-cache | CLI flag | 否 | 默认关闭；本次不读取、不保存响应缓存。 |

缓存由公共调用器统一管理，仅使用一层缓存：有效期为 24 小时，路径为 `<cwd>/linkfox/.cache/linkfox-zhihuiya-simple-bibliography/`；键为排序参数 JSON 的 SHA-256 前 16 位，文件名为 `linkfox-zhihuiya-simple-bibliography-<key>.json`，同路径、同键的有效缓存可直接复用。缓存命中时标记 `_cache.hit=true`，仍保存本次完整响应。失败或空结果也可能被缓存，过期或损坏的缓存不复用；不得因此自动改参连续试探。

认证密钥优先读取 `LINKFOX_AGENT_API_KEY`，回退读取 `LINKFOXAGENT_API_KEY`；`LINKFOX_TOOL_GATEWAY` 可覆盖默认网关。`SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 透传至请求头。业务脚本固定使用当前工作目录的 `linkfox/` 保存数据，不回退到临时目录；请求前检查根目录、会话元信息及实际 `data/` 目录是否可写，不可用时直接报错，避免请求后才发现无法保存响应。完整响应以 UTF-8 保存；不超过 8000 字节时全量输出，超过时输出摘要，`--inline` 强制全量输出。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer | 网关业务码，按公共规则判断；认证错误响应可包含 `errcode:401` |
| errmsg | string | 网关业务消息，认证错误消息示例为 `authorized error` |
| errorCode | integer | 接口业务码，`200` 表示成功、其他值表示业务错误；仅在实际返回时检查，与公共响应码规则一并判断 |
| total | integer | 记录数 |
| allRecordsCount | integer | 总记录数 |
| data | array | 著录项列表（详见下方数据字段说明） |
| columns | array | 渲染的列定义 |
| type | string | 渲染的样式 |
| costToken | integer | 接口计费 token，不直接等同于用户算力；算力预估见 SKILL.md |

#### 数据字段（`data` 数组中每个元素）

| 字段 | 类型 | 说明 |
|------|------|------|
| patentId | string | 专利ID |
| title | string | 专利标题 |
| abstractContent | string | 专利摘要 |
| publicationNumber | string | 公开号 |
| pn | string | 公开公告号 |
| country | string | 国家代码 |
| publicationCountry | string | 公开国家 |
| publicationDate | string | 公开日期 |
| publicationKind | string | 公开类型代码 |
| patentType | string | 专利类型（发明、实用新型、外观设计等） |
| kind | string | 专利类型代码 |
| applicationNo | string | 申请号 |
| applicationDate | string | 申请日期 |
| applicants | array | 申请人列表 |
| inventors | array | 发明人列表 |
| assignees | array | 专利权人列表 |
| assigneeAddresses | array | 专利权人地址列表 |
| ipcMain | string | IPC主分类号 |
| ipcFurther | array | IPC副分类号列表 |
| cpcMain | string | CPC主分类号 |
| cpcFurther | array | CPC副分类号列表 |
| loc | array | 洛迦诺（Locarno）分类号列表，适用于外观设计专利 |
| gbc | array | GBC分类号列表 |
| priorityClaims | array | 优先权声明列表 |
| pctApplicationNo | string | PCT申请号 |
| pctFilingDate | string | PCT申请日期 |
| pctEntryDate | string | PCT进入日期 |
| citedPatents | array | 引用专利列表 |
| citedNonPatents | array | 引用非专利文献列表 |

上述数组及 `columns` 未约定元素的固定子字段；按实际返回结构读取，不推断嵌套字段。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 若实际返回 `errorCode`，还需检查该接口业务码；其表示业务错误时，不因 HTTP 正常或缺少 `errcode` 而将查询视为成功。未返回时不自行补造该字段。
- 查询失败时，依据实际错误消息建议核对专利号或 ID 格式；不自动更换标识继续付费试探。

### curl 示例

```bash
curl -X POST https://tool-gateway.linkfox.com/zhihuiya/simpleBibliography \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"patentNumber": "US11234567B2"}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-zhihuiya-simple-bibliography",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
