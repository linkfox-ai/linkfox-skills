# AI 生文 API 参考


## MCP 调用

响应字段来源：`skills/linkfox-aigc-textgen/references/api.md`，由原 endpoint 和调用脚本确认。

- MCP server：`LinkFox`
- 唯一工具：`proxy_call`
- 创建 `toolName`：`aigc/textGenAsync`
- 查询 `toolName`：`aigc/textTaskQuery`
- `arguments` 直接使用对应请求参数表对象；WorkBuddy 自动注入 Authorization，禁止 headers、Key 或 token。
- 禁止 HTTP fallback；同一任务相同 `toolName + arguments` 不重复调用。`PROCESSING` 时保留 taskId，等待用户后续明确继续。
- 先检查 MCP/代理错误；text JSON 只解析一次，再检查下游错误字段与 `status`。

创建示例：

```json
{"toolName":"aigc/textGenAsync","arguments":{"prompt":"Write a product description","imageUrls":[],"model":"GEM_3_FLASH","thinkingLevel":"minimal"}}
```

查询示例：

```json
{"toolName":"aigc/textTaskQuery","arguments":{"taskId":"123456789"}}
```


本页为 `linkfox-aigc-textgen` 技能调用的底层接口规格。SKILL.md 面向"怎么用"的决策层，本文档面向"接口精确格式"。

## 接口说明

> 工具中文名：AI生文

采用异步两步模式：先创建任务获得 `taskId`，再按用户指示查询任务状态和结果。



## 接口一：创建生文任务

- **路径**：`POST /aigc/textGenAsync`
- **说明**：提交生文请求，立即返回 taskId

### 请求参数

| 参数 | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| prompt | string | 是 | - | 提示词，描述需要生成的内容（最大10万字符） |
| imageUrls | array[string] | 是 | [] | 媒体 URL 列表（图片或视频）。纯文本时传 `[]`；图片最多10张；视频分析通常传1个视频 URL |
| model | string | 否 | GEM_3_FLASH | 模型枚举值：`GEM_3_FLASH`(快速响应) / `GEM_3_1_PRO`(高质量复杂分析) |
| thinkingLevel | string | 是 | minimal | 思考等级：`minimal` / `low` / `medium` / `high`（GEM_3_1_PRO 不支持 minimal） |
| memberId | string | 否 | - | 用户成员ID，用于任务记录关联 |

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| `taskId` | string | 异步任务ID，用于后续状态查询 |

### 响应示例

```json
{"taskId": "123456789"}
```

---

## 接口二：查询生文任务状态

- **路径**：`POST /aigc/textTaskQuery`
- **说明**：根据 taskId 查询一次任务状态，成功时返回文本内容

### 请求参数

| 参数 | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| taskId | string | 是 | - | 创建任务时返回的任务ID |
| memberId | string | 否 | - | 用户成员ID，用于任务记录关联 |

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| `taskId` | string | 任务ID |
| `status` | string | 任务状态：`PROCESSING`(处理中) / `SUCCESS`(成功) / `FAILED`(失败) |
| `content` | string | 生成的文本内容（仅 SUCCESS 时有值） |
| `promptTokens` | integer | 输入 token 数量（仅 SUCCESS 时有值） |
| `completionTokens` | integer | 输出 token 数量（仅 SUCCESS 时有值） |
| `totalTokens` | integer | 总 token 数量（仅 SUCCESS 时有值） |
| `errorMsg` | string | 错误信息（仅 FAILED 时有值） |

### 响应示例

处理中：
```json
{"taskId": "123456789", "status": "PROCESSING"}
```

成功：
```json
{
  "taskId": "123456789",
  "status": "SUCCESS",
  "content": "Generated text content...",
  "promptTokens": 120,
  "completionTokens": 350,
  "totalTokens": 470
}
```

失败：
```json
{"taskId": "123456789", "status": "FAILED", "errorMsg": "生成失败"}
```

---

## 错误码

HTTP 200 时业务成功与否看响应体 `errcode`/`errorCode`（200=成功）；HTTP 401 表示未授权。

| errcode | 含义 | 处理 |
|---------|------|------|
| 200 | 成功 | 正常解析业务字段 |
| 401 | 认证失败 | HTTP 401 或 authorized error：按 SKILL.md 的 **## 解决认证和积分问题** 处理。 |
| 402 | 积分不足 | HTTP 402：按 SKILL.md 的 **## 解决认证和积分问题** 处理。 |
| 10009 | 任务不存在 | 检查 taskId 是否正确 |
| 其他 | 业务异常 | 参考 `errmsg` 字段 |


---

## Feedback API

> 该端点与上方工具 API 分离，请勿混用 base URL。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **Content-Type:** `application/json`

```json
{
  "skillName": "linkfox-aigc-textgen",
  "sentiment": "POSITIVE",
  "category": "OTHER",
  "content": "Results were accurate, user was satisfied."
}
```

**字段规则：**
- `skillName`：使用 SKILL.md frontmatter 的 `name`
- `sentiment`：`POSITIVE`（赞扬）/ `NEUTRAL`（建议无情绪）/ `NEGATIVE`（不满或错误）
- `category`：`BUG`（异常或数据错误）/ `COMPLAINT`（不满）/ `SUGGESTION`（改进建议）/ `OTHER`
- `content`：说明用户说了什么/期望什么、实际发生了什么、为什么是问题/赞赏

