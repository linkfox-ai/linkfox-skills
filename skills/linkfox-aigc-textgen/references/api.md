# AI 生文 API 参考

本页对应AgentOS工具接口，不把内部AI的接口路径、实际供应商模型名或整数价格参考表另复制成一套实现。

## 通用调用规则

- 基础地址读取LINKFOX_TOOL_GATEWAY，未配置时沿用公共封装的正式网关默认值。
- POST，Content-Type: application/json；Authorization读取LINKFOX_AGENT_API_KEY，兼容LINKFOXAGENT_API_KEY。不要输出密钥、STS凭证或完整Authorization。
- HTTP与业务状态都要校验。正常HTTP为200–299；errcode/errorCode/code若存在，则空值或200–299的整数/数字字符串为成功，0和false不当成空。保留原始错误字段，不以HTTP200掩盖业务失败。
- 兼容顶层以及data/result对象包裹。公共封装保留真实transportHttpStatus；认证和算力问题按[onboarding.md](onboarding.md)处理。
- 创建、查询和临时凭证请求都禁用响应缓存。脚本不运行模型调用重试，不因网络不确定而重新创建任务。

## 创建任务：textGenAsync

POST /aigc/textGenAsync

| 参数 | 类型 | 必填 | 默认与限制 |
|---|---|---|---|
| prompt | string | 是 | 最多100000字符 |
| model | string | 否 | 默认GEM_3_1_PRO；建议显式指定标准编码；未知值报错 |
| thinkingLevel | string | 否 | GT未传为medium，GEM未传由模型处理；非法值不自动降级 |
| systemPrompt | string | 否 | 仅GT支持，GEM须把指令放在prompt |
| imageUrlList | array[string] | 否 | 标准图片字段，可省略或[]；最多10张HTTP(S)图片 |
| imageUrls | array[string] | 否 | 兼容旧图片字段；与imageUrlList同时传时必须一致 |
| memberId | string | 否 | 当前认证成员的记录关联，不能借此指定其他成员扣款 |

图片本地路径先按[file-upload.md](file-upload.md)上传；保留输入顺序，上传失败不创建任务。标准文本/图片链路不接收原生视频或音频，GT明确不支持这些输入。不要编造videoUrl/videoUrls字段。视频业务按其既有分镜/抽帧流程提供图片；旧入口视频能力须单独确认，不能混同为新模型通用支持。

### 模型编码与思考等级

| model | thinkingLevel |
|---|---|
| GEM_3_1_PRO | low / medium / high |
| GEM_3_7_FLASH | minimal / low / medium / high |
| GEM_4_A | low / medium / high |
| GT_6_1_S | low / medium / high / xhigh / max |
| GT_6_1_T | none / low / medium / high / xhigh / max |
| GT_6_L | none / low / medium / high / xhigh / max |
| GT_6_A | low / medium / high / xhigh / max |

- LF_GEM_1保持映射GEM_3_FLASH，LF_GEM_2保持映射GEM_3_1_PRO；GEM_3_FLASH仅作历史兼容，支持minimal/low/medium/high。不要将LF_GEM_1改指向3.7。
- 模型码大小写不敏感，空model仍默认Pro。GT不支持minimal/ultra，none仅GT_6_1_T和GT_6_L支持。GEM_4_A与Pro不支持minimal。
- 实际可用模型取决于环境开通和新计费启用状态。未启用或不支持时保留真实错误，不自动换贵模型、不探测重建收费任务。
- xhigh/max可能需要更长等待并消耗更多输出Token；使用--poll-timeout延长客户端等待，或保留taskId稍后恢复查询。

### 示例

~~~json
{"prompt":"写三条无线音箱卖点","model":"GEM_3_7_FLASH","thinkingLevel":"minimal","imageUrlList":[]}
~~~

~~~json
{"prompt":"分析商品图并生成三条卖点","model":"GT_6_1_S","systemPrompt":"用中文，每条一句话","thinkingLevel":"xhigh","imageUrlList":["https://example.com/product.jpg"]}
~~~

创建成功须取得非空taskId，按字符串保存。兼容顶层taskId及data.taskId/result.taskId。创建时costToken=0不表示最终免费。

~~~json
{"taskId":"123456789","costToken":0}
~~~

创建只调用一次。超时或连接中断可能已创建成功，不自动重发；若已知taskId则只查询原任务，未知时保留诊断交人工核对。

## 查询任务：textTaskQuery

POST /aigc/textTaskQuery

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| taskId | string | 是 | 已创建任务的标识；不重建任务 |
| memberId | string | 否 | 当前认证成员 |

| 返回字段 | 类型 | 说明 |
|---|---|---|
| taskId | string | 原任务标识 |
| status | string | PROCESSING / SUCCESS / FAILED |
| content | string | 生成文本，仅成功时读取 |
| promptTokens | integer | 输入Token数，不由客户端猜测 |
| completionTokens | integer | 输出Token数 |
| totalTokens | integer | 总Token数 |
| count | integer | 新AI计费任务的实际扣点，以此为准；旧任务可能没有 |
| points | integer | 按usage计算的点数，不等于实际扣点，不能代替count |
| costToken | integer | 网关计费用量，不是模型Token数；新任务AI已负责扣点，固定0以免二次扣费 |
| billingStatus | string | 例如CALCULATED、USAGE_UNAVAILABLE、DEDUCTION_UNCONFIRMED；只透传已返回值 |
| pricingVersion | string | 服务端定价版本，可选 |
| errorMsg | string | 任务失败原因 |

~~~json
{"taskId":"123456789","status":"SUCCESS","content":"商品卖点文本","promptTokens":120,"completionTokens":80,"totalTokens":200,"points":2,"count":1,"costToken":0,"billingStatus":"CALCULATED"}
~~~

示例的points/count差异只说明余额/成员额度封顶时可能实扣不足，不是固定价格。响应可能包在data/result中，缺失字段不得补造。

### 计费与异常处理

- 新任务创建不预扣；执行前可用额度至少100点，受成员额度约束；成功按内部AI生文相同的模型单价和真实usage计算，输入输出费用合计向上取整，应扣最低1点，正常生成失败不扣点。
- 价格、GT缓存/长上下文等规则由AI后端及任务快照决定。技能不再按旧150积分/元等公式重算新任务费用；整数单价参考不是最终账单。
- 新任务生成成功时由AI统一账本一次结算，重复查询不新增扣点；以count实际值展示，不把costToken=0或points=0判为免费。
- 旧任务仍沿用服务端旧链路。不能把“新任务查询不再收费”承诺套到旧任务上；保留旧响应中的costToken，不改写成0、不自行补算count，也不反复成功查询来验证费用。
- USAGE_UNAVAILABLE表示用量不足以正常计价；DEDUCTION_UNCONFIRMED表示账本状态需核对。保留生成内容与taskId，在stderr明确提示核对原任务/账本，不把零点视为正常免费，不自动重建或退款。

### 轮询与恢复

默认客户端等待600秒，HTTP最长150秒；轮询间隔从10秒递减到5秒。--poll-timeout正数秒可延长本次等待，查询HTTP超时不超过剩余等待预算。客户端超时返回POLL_TIMEOUT、原taskId和可恢复标识，不伪装成服务端FAILED。

~~~bash
python scripts/aigc_textgen.py '{"taskId":"123456789"}' --poll-timeout 1800
~~~

- 查询仅对网络或HTTP408/429/500/502/503/504等暂时传输故障最多额外重试3次；认证、额度、明确业务失败或本地保存/解析错误立即停止。
- 状态查询永远不转为创建。查询失败或客户端等待超时后，不用改model、thinkingLevel或重新提交prompt来猜测任务结果。

## CLI、落盘与输出

| 方式 | 行为 |
|---|---|
| --stdin | 从stdin读JSON，推荐用于多行prompt |
| 单个JSON参数 | 简单请求可直接传；多行内容仍用stdin |
| --content-only | stdout只放单行content；诊断与计费异常放stderr |
| --inline | stdout打印完整JSON |
| --no-cache | 兼容选项；请求始终禁用缓存 |
| --poll-timeout 秒数 | 正数秒数，默认600，不改变服务端任务期限或收费 |
| JSON含taskId | 恢复查询，不创建；模型参数不会用于生成新任务 |

完整原始响应与最终输出保存在当前目录linkfox/<YYYY-MM-DD>/<session>/data/，SESSION_ID优先，保存失败非零退出，不回退到/tmp。接口原始响应前缀为linkfox-aigc-textgen-create-/query-，最终输出前缀为linkfox-aigc-textgen-。

默认不超过8000字节时输出完整JSON；大结果输出ok/truncated/savedPath/bytes/content信封，并保留实际返回的count、points、costToken、billingStatus、pricingVersion。摘要和计费警告只写stderr。成功文本的计费待核对不触发重新生成；生成失败、网络/业务/本地错误或空成功内容以非零状态退出。

内容换行沿用⏎占位符；下游参数须用jq --arg或Python json.dumps等JSON编码器构造，不能手工拼接引号、反斜杠。下游imagegen/videogen等已有流程解码占位符；不要因本次生文改造擅自增加未要求的收费下游操作。

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-aigc-textgen",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
