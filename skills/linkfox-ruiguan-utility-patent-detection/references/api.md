# 睿观实用新型/发明专利检测 接口说明

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

## 接口：实用新型/发明专利检测

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/ruiguan/utilityPatentDetection`

### 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| productTitle | string | 是 | 产品标题，最大 1000 字符；使用实际商品标题或具体描述性标题，例如「便携式 USB-C 65W 快充充电器」，避免仅写「充电器」。 |
| productDescription | string | 是 | 产品描述，最大 1000 字符；包含关键功能、材料、机制和技术属性，信息越充分越有助于相似匹配。 |
| region | string | 是 | 商品想要售卖的国家/地区代码；多地区约定为逗号分隔，当前仅支持 `US`，默认 `US`。通常显式传 `US`；用户指定其他市场时说明暂不支持，不静默改为美国查询。 |
| topNumber | integer | 是 | 召回数量，范围 10–200，默认 `100`；快速初筛可用 10–20，较全面排查可用 200，每次最多返回 200 项。 |

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| JSON 参数 | JSON | 是 | 作为一个命令行参数传入上述请求对象；脚本透传，不自动补默认值、截断输入或改变市场。 |
| --inline | CLI flag | 否 | 强制完整打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 跳过缓存读取和写入；默认使用 24 小时本地缓存。 |

缓存由公共调用器单层维护，以按参数名排序的 JSON 计算 SHA-256，取前 16 位作为缓存键；缓存路径为 `<cwd>/linkfox/.cache/linkfox-ruiguan-utility-patent-detection/`，同参数可复用有效缓存。超过 24 小时或损坏的缓存视为未命中；命中时添加 `_cache.hit=true`。接口返回对象（含错误或空结果）也会保存到缓存，不自动重试；确认需要重新请求时使用 `--no-cache`，并先说明额外消耗。

认证兼容两种密钥环境变量，`LINKFOX_AGENT_API_KEY` 优先。请求携带 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 上下文头。业务脚本固定完整响应保存在当前工作目录的 `linkfox/` 下，不使用其他工作区、家目录或 `/tmp` 兜底；当前目录不可写时在请求前报错。会话标识优先取 `SESSION_ID`，未设置时在进程内生成稳定标识。

#### 使用限制

- 仅支持美国专利检索。标题和描述上限、召回数量限制见上方参数表。
- 同一会话、同一参数组合默认只调用一次。失败或空结果不得自动改词或连续试探；继续检索前先说明额外消耗。
- 本技能消耗较高；调用次数将超过 5 次时，必须先二次确认。使用 `AskUserQuestion`（可用时）或直接向用户询问，明确告知已消耗算力和后续预计消耗，由用户决定是否继续；已用 5 次时，按每次 106 算力估算已用 530 算力，另列拟继续次数及预估，不以估算替代实际扣费记录。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| total | integer | 记录数 |
| detectId | string | 检测ID |
| costToken | integer | 消耗token |
| type | string | 渲染的样式 |
| columns | array | 渲染的列定义 |
| data | array | 专利列表（详见下方） |

#### data[*] 专利对象字段

| 字段 | 类型 | 说明 |
|------|------|------|
| globalUtilityId | string | 专利ID |
| title | string | 发明专利标题 |
| titleCn | string | 发明专利标题（中文） |
| similarity | number | 产品与该专利的相似度（0--1） |
| patentValidity | string | 专利有效性：`Active`（有效）或 `Invalid`（无效） |
| applicationNumber | string | 申请号 |
| applicationDate | string | 申请日（yyyy-MM-dd） |
| publicationNumber | string | 公开号 |
| publicationDate | string | 公开日（yyyy-MM-dd） |
| estimatedDueDate | string | 预估到期日（yyyy-MM-dd） |
| region | string | 受理局 |
| patentAbstract | string | 摘要 |
| patentAbstractCn | string | 摘要（中文） |
| claims | string | 权利要求 |
| claimsCn | string | 权利要求（中文） |
| specification | string | 说明书 |
| specificationCn | string | 说明书（中文） |
| inventors | array | 发明家和国家拼接，数组格式 |
| inventorAddresses | array | 发明人地址，数组格式 |
| applicants | array | 申请人和国家拼接，数组格式 |
| applicantAddresses | array | 权利人地址，数组格式 |
| priorityNumber | array | 优先权号，数组格式 |
| relatedPublicationDate | array | 首次公开日（yyyy-MM-dd），数组格式 |
| patentImageUrl | string | 专利封面图 |
| images | array | 专利附图 |
| classNumList | array | 类别号路径列表，格式：classNum1 > classNum2 > classNum3 |
| cpcKindRaw | array | CPC分类（原始 JSONArray） |
| troCase | boolean | 是否有TRO维权史 |
| troHolder | boolean | 是否是TRO权利人的专利 |

#### 响应状态与兼容字段

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer | 接口错误码字段；响应判断遵循公共规则，认证错误示例为 401。 |
| errmsg | string | 返回消息或具体异常原因，例如 `authorized error`。 |
| errorCode | 未约定 | 兼容字段；若实际响应含此字段，保留原值供诊断，响应判断仍遵循公共规则。 |

`columns` 元素、各数组元素的通用结构及其他未列字段没有进一步约定，不臆造其类型和必填性；保留实际响应。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

本接口未定义额外的业务错误码。

### curl 示例

```bash
curl -X POST https://tool-gateway.linkfox.com/ruiguan/utilityPatentDetection \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"productTitle":"便携式USB-C 65W氮化镓快充充电器","productDescription":"紧凑型65W氮化镓充电器，配可折叠插脚，支持PD3.0和QC4.0，双USB-C端口和一个USB-A端口，适用于笔记本电脑、手机和平板电脑。","region":"US","topNumber":100}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-ruiguan-utility-patent-detection",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
