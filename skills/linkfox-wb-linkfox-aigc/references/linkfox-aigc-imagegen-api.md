# AI 生图 API 参考


## MCP 调用

响应字段来源：`skills/linkfox-aigc-imagegen/references/api.md`，由原 endpoint 和调用脚本确认。

- MCP server：`LinkFox`
- 唯一工具：`proxy_call`
- 创建 `toolName`：`aigc/imageGenAsync`
- 查询 `toolName`：`aigc/taskQuery`
- `arguments` 直接使用对应请求参数表对象；WorkBuddy 自动注入 Authorization，禁止 headers、Key 或 token。
- 禁止 HTTP fallback；同一任务相同 `toolName + arguments` 不重复调用。`PROCESSING` 时保留 taskId，等待用户后续明确继续。
- 先检查 MCP/代理错误；text JSON 只解析一次，再检查下游错误字段与 `status`。

创建示例：

```json
{"toolName":"aigc/imageGenAsync","arguments":{"imageUrls":["https://example.com/ref.jpg"],"prompt":"product on white background","provider":"BANANA_PRO","outputNum":1,"resolution":"1K","aspectRatio":"1:1","quality":"high"}}
```

查询示例：

```json
{"toolName":"aigc/taskQuery","arguments":{"taskId":"123456789"}}
```


本页为 `linkfox-aigc-imagegen` 技能调用的底层接口规格。SKILL.md 面向"怎么用"的决策层，本文档面向"接口精确格式"。

## 接口说明

> 工具中文名：AI生图

采用异步两步模式：先创建任务获得 `taskId`，再按用户指示查询任务状态和结果。



## 接口一：创建生图任务

- **路径**：`POST /aigc/imageGenAsync`
- **说明**：提交生图请求，立即返回 taskId

### 请求参数

| 参数 | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| imageUrls | array[string] | 是 | - | 参考图列表（1张或多张图片URL） |
| prompt | string | 是 | - | 提示词，描述期望生成的图片内容 |
| provider | string | 否 | BANANA_PRO | 模型枚举值：`BANANA`(基础版仅1K) / `BANANA_2`(香蕉2) / `BANANA_PRO`(香蕉Pro) / `GPT_2_IMAGE`(Image2) / `AIDRAW_EDIT`(Linkfox-Image-1) / `WAN2_7`(Wan2.7) / `SEEDREAM5`(Seedream5.0仅2K) |
| outputNum | integer | 是 | 1 | 输出张数，取值范围 [1, 10]。必须显式传入 |
| resolution | string | 是 | 1K | 分辨率：`1K` / `2K` / `4K`。必须显式传入 |
| aspectRatio | string | 是 | 1:1 | 宽高比：`1:1` / `16:9` / `9:16`。必须显式传入 |
| quality | string | 是 | high | 图片质量，仅 GPT_2_IMAGE 支持：`low` / `medium` / `high`。必须显式传入 |

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| `taskId` | string | 异步任务ID，用于后续状态查询 |

### 响应示例

```json
{"taskId": "123456789"}
```

---

## 接口二：查询任务状态

- **路径**：`POST /aigc/taskQuery`
- **说明**：根据 taskId 查询一次任务状态，成功时返回结果列表

### 请求参数

| 参数 | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| taskId | string | 是 | - | 创建任务时返回的任务ID |

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| `taskId` | string | 任务ID |
| `status` | string | 任务状态：`PROCESSING`(处理中) / `SUCCESS`(成功) / `FAILED`(失败) |
| `resultList` | array[object] | 结果列表（仅 SUCCESS 时有值） |
| `resultList[].id` | string | 资源ID |
| `resultList[].url` | string | 生成的图片URL（已转存至OSS） |
| `resultList[].type` | string | 资源类型 |
| `errorMsg` | string | 错误信息（仅 FAILED 时有值） |

### 响应示例

处理中：
```json
{"taskId": "123456789", "status": "PROCESSING", "resultList": null, "errorMsg": null}
```

成功：
```json
{"taskId": "123456789", "status": "SUCCESS", "resultList": [{"id": "1001", "url": "https://oss.example.com/aigc/123456789/result_1001.png", "type": "image"}], "errorMsg": null}
```

失败：
```json
{"taskId": "123456789", "status": "FAILED", "resultList": null, "errorMsg": "生成失败"}
```

---

## 状态查询策略

- 每次用户明确要求继续后，使用原 `taskId` 查询一次；不得自动循环查询。
- `PROCESSING`：返回 `taskId`，建议至少等待 10 秒，再由用户决定是否继续查询。
- `SUCCESS` 或 `FAILED`：作为终态处理；不得创建重复任务或自动重试失败任务。

---

## 错误码

HTTP 200 时业务成功与否看响应体 `errcode`/`errorCode`（200=成功）；HTTP 401 表示未授权。

| errcode | 含义 | 处理 |
|---------|------|------|
| 200 | 成功 | 正常解析业务字段 |
| 400 | 参数错误 | 检查必填参数是否正确传入 |
| 401 | 认证失败 | HTTP 401 或 authorized error：按 SKILL.md 的 **## 解决认证和积分问题** 处理。 |
| 402 | 积分或余额不足 | HTTP 402：按 SKILL.md 的 **## 解决认证和积分问题** 处理。 |
| 10009 | 任务不存在 | 检查 taskId 是否正确 |
| 其他 | 业务异常 | 参考 `errmsg` 字段 |

错误响应示例：
```json
{"errcode": 401, "errmsg": "authorized error"}
```


---

## Feedback API

> 该端点与上方工具 API 分离，请勿混用 base URL。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **Content-Type:** `application/json`

```json
{
  "skillName": "linkfox-aigc-imagegen",
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

