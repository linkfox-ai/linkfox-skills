# 智慧芽专利著录信息 接口说明

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

## 接口：专利著录信息查询

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/zhihuiya/bibliography`

### 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| patentId | string | 条件必填 | 智慧芽内部专利 ID；与 patentNumber 至少提供一项，同时提供时优先使用 patentId。多个用英文逗号隔开，逗号两侧不加空格，上限 100 条，最大长度 60,000 字符。 |
| patentNumber | string | 条件必填 | 公开公告号；与 patentId 至少提供一项，同时提供时优先使用 patentId。多个用英文逗号隔开，逗号两侧不加空格，上限 100 条，最大长度 60,000 字符。 |

#### 标识识别与批量约定

- `US10123456B2`、`CN112345678A`、`EP3456789B1`、`WO2023123456A1` 等符合公开公告号形式的标识使用 `patentNumber`。
- 用户给出的纯数字或其他不符合标准公开号形式的内部、不透明标识使用 `patentId`；来源不明确时先核对，不凭主题编造编号。
- 多件标识按上述规则组成逗号分隔字符串，不传数组；超出单次限制时先说明分批产生的额外消耗，再按用户决定执行。

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| JSON 参数 | string | 是 | 首个位置参数，内容为上方 POST Body。 |
| --inline | CLI flag | 否 | 强制完整打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 跳过响应缓存的读取与写入；默认启用 24 小时缓存。 |
| --help | CLI flag | 否 | 查看本地帮助，不发送请求。 |

脚本为 `scripts/zhihuiya_bibliography.py`。使用公共 `scripts/call_api.py` 的 `run` 完成请求、缓存、会话记录和输出，不设置第二层响应缓存。缓存位置为 `<cwd>/linkfox/.cache/linkfox-zhihuiya-bibliography/`，以排序后的 JSON 参数的 SHA-256 前 16 位作为缓存键，文件名为 `linkfox-zhihuiya-bibliography-<缓存键>.json`；缓存命中标记为 `_cache.hit=true`。过期或损坏缓存视为未命中；`--no-cache` 不读取、写入或清除已有缓存。脚本缓存取得的响应，包括空结果及错误响应。

使用 `LINKFOX_AGENT_API_KEY` 优先，兼容 `LINKFOXAGENT_API_KEY`；`LINKFOX_TOOL_GATEWAY` 可覆盖默认网关。请求携带 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 环境变量对应的头。完整响应使用 UTF-8 保存，同时记录会话元数据与索引。业务入口在请求前检查当前目录下的输出目录可写，固定使用 `<cwd>/linkfox/`，不受 `ACPX_WORKSPACES` 重定向，不回退到家目录或临时目录；当前目录位于 `/tmp` 时拒绝执行。

JSON 解析失败时直接退出，不创建输出目录。`SESSION_ID` 解析后的会话路径必须位于当前工作目录的当日会话目录内；越界路径或越界的目录链接在创建会话及请求前报错。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| total | integer | 记录数。 |
| data | array | 著录项目数据列表，元素字段见下表；每条对应一条专利著录项结果。 |
| columns | array | 渲染的列。元素内部字段按实际响应保留。 |
| type | string | 渲染的样式。 |
| costToken | integer | 消耗 token；按返回原值保留，用户算力以网关实际扣费记录为准，不按记录条数自行换算。 |
| errcode | integer / string / null | 网关业务状态码，按公共规则判断；认证错误示例为 401。 |
| errmsg | string | 错误原因；认证错误示例为 authorized error。 |
| errorCode | 类型未限定 | 业务状态字段；若实际返回则保留，不替代公共规则的判断依据。 |

#### data 数组中的每个对象

| 字段 | 类型 | 说明 |
|------|------|------|
| patentId | string | 专利ID |
| pn | string | 公开公告号 |
| inventionTitle | array | 专利标题语言和名称 |
| abstracts | array | 专利摘要 |
| patentType | string | 专利类型，其中APPLICATION：发明申请（已公开、尚未授权），PATENT：授权发明，UTILITY：实用新型，DESIGN：外观设计 |
| applicants | array | 原始申请人 |
| assignees | array | 当前申请(专利权)人 |
| inventors | array | 发明人 |
| agents | array | 专利代理人，按实际返回展示并与 applicants 区分 |
| agency | array | 申请代理机构 |
| examiners | array | 审查员信息 |
| priorityClaims | array | 优先权声明 |
| applicationReference | object | 申请文件引用数据 |
| publicationReference | object | 公开文件引用数据 |
| datesOfPublicAvailability | object | 公开可用日期 |
| classificationIpcr | object | IPC国际专利分类号 |
| classificationCpc | object | CPC合作专利分类号 |
| classificationUpc | object | 美国专利分类号 |
| classificationLoc | array | LOC分类号（外观设计洛迦诺分类） |
| classificationFi | array | FI分类号（日本） |
| classificationFterm | array | F_term分类号（日本） |
| classificationGbc | object | GBC分类号 |
| referenceCitedPatents | array | 引用专利文献 |
| referenceCitedOthers | array | 引用非专利文献 |
| relatedDocuments | array | 分案继续申请信息 |
| pctOrRegionalFilingData | object | PCT或区域阶段申请数据 |
| pctOrRegionalPublishingData | object | PCT或区域阶段公开数据 |
| exdt | integer | 智慧芽专利预估到期日 |

以上对象和数组的内部子字段以实际响应为准，不推测嵌套结构。`inventionTitle` 保留标题语言与名称，其他嵌套资料按完整原始响应读取。

#### 脚本本地附加字段

- `_http_status`：业务脚本记录的实际 HTTP 状态，不是网关业务字段。按公共规则判断时同时检查此值与 `errcode`；HTTP 401/402 即使正文缺少 `errcode` 也按认证或算力问题处理。非 JSON 正文保留在 `details`，非对象 JSON 保留在 `_response_body`，不将其当作著录记录。
- 缓存命中时，`_http_status` 为取得该缓存时的历史状态，不代表本次发送了请求。已有缓存若没有此字段，HTTP 状态无法从正文反推；有 `error` 或错误消息时不得因缺少 `errcode` 而判为成功。核对缓存正文并遵守成本约束，不为补取状态自动重发请求。

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 正常响应但 `data` 为空时，说明未取得对应专利著录项，提示核对标识，不据此断言专利不存在。
- 响应中的 `errorCode` 与 `errcode` 按实际返回保留，以公共规则判断；不将 `errorCode=200` 另行设为成功的必备条件。

### 响应示例

认证错误示例：

```json
{"errcode": 401, "errmsg": "authorized error"}
```

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/zhihuiya/bibliography" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"patentNumber": "US10123456B2"}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-zhihuiya-bibliography",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```