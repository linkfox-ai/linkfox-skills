# LinkFox 文本生成

子能力标识 `linkfox-aigc-textgen`。生成或改写营销文案，理解图片、视频内容；不产出图片或视频文件，不为每个图像生成任务自动增加一次付费分析。

## MCP 契约

通过 `LinkFox.proxy_call` 创建 endpoint `/aigc/textGenAsync`，精确 `toolName` 为 `aigc/textGenAsync`；查询 endpoint `/aigc/textTaskQuery`，精确 `toolName` 为 `aigc/textTaskQuery`。字段直接位于 `arguments`，不包 `params/body/data`。WorkBuddy 自动注入 Authorization，不传凭证。

| 创建字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `prompt` | string | 是 | 需求、输出语言及事实约束，最多10万字符 |
| `imageUrls` | array[string] | 是 | 纯文本传 `[]`；图片最多10张；视频分析通常传1个视频URL |
| `model` | string | 否 | `GEM_3_FLASH` 快速响应，或 `GEM_3_1_PRO` 复杂分析，默认前者 |
| `thinkingLevel` | string | 是 | `minimal/low/medium/high`；`GEM_3_1_PRO` 不支持 `minimal` |
| `memberId` | string | 否 | 已知的真实成员ID，供任务关联；不编造、不用它覆盖授权身份 |

媒体需要公开可访问，本地文件按 [file-upload.md](file-upload.md) 上传。先确认分析目标和语言，不把模型观察写成已验证商品事实。

```json
{"toolName":"aigc/textGenAsync","arguments":{"prompt":"根据已确认卖点编写三条英文短文案，不增加新事实。","imageUrls":[],"model":"GEM_3_FLASH","thinkingLevel":"minimal"}}
```

创建成功保存 `taskId`，用文本专用查询，不使用 `aigc/taskQuery`：

```json
{"toolName":"aigc/textTaskQuery","arguments":{"taskId":"<returned-taskId>"}}
```

| 查询字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `taskId` | string | 是 | 创建返回的任务编号 |
| `memberId` | string | 否 | 若创建时有真实成员上下文则沿用 |

| 响应字段 | 说明 |
|---|---|
| `taskId` | 任务编号 |
| `status` | `PROCESSING` / `SUCCESS` / `FAILED` |
| `content` | 成功时文本内容 |
| `promptTokens` | 输入token数量，若返回 |
| `completionTokens` | 输出token数量，若返回 |
| `totalTokens` | 总token数量，若返回，不等同于已支付积分 |
| `errorMsg` | 失败原因 |

每个请求创建一次，创建后可查一次；处理中保留编号，建议至少等待10秒后由用户明确继续查询。不自动循环、重建或换模型。成功但 `content` 为空时报告异常，直接交付实际生成文本而非虚构下载链接。

业务 `errcode/errorCode` 存在时200为成功；401/402/403按 [onboarding.md](onboarding.md) 分层处理，10009表示任务不存在。其他错误保留实际码和脱敏消息，不自动重试。文本与媒体理解结果应标明 AI 生成或模型分析性质。
