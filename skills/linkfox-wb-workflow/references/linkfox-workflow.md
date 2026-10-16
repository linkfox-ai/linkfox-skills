# LinkFox 运营流程 API 与执行契约

本 reference 归档 `linkfox-workflow` 的能力范围、11 个 endpoint、Agentflow v2 结构、身份规则、执行和历史版本安全约束。业务接口统一使用 `LinkFox.proxy_call`；`toolName` 与 endpoint 完全相同且不带前导斜杠。路径变量在调用时以真实 ID 代入，业务请求对象直接放入 `arguments`。

## 能力定义与边界

该能力面向运营流程的设计、解释、校验、服务端管理、执行跟踪和版本历史。支持的服务端操作为创建/读取/更新 flow、sourceKey 映射查询、执行一次 flow、读取执行记录、读取/比较版本及经确认还原版本。不包含发布、删除 flow、删除执行记录、外部运行时资源创建或自动绑定。

仅使用 Agentflow v2。顶层对象为 `{description, usecases, nodes, edges}`。系统支持 24 类节点，包含 BusinessStart、CrossBorderExpert、DataReader、FillForm、SendNotification、WriteFile、LinkfoxHTTP、End、CustomPythonFunction，以及 Agent、LLM、Tool、Retriever、Condition、ConditionAgent、Loop、Iteration、HumanInput、HTTP、CustomFunction、ExecuteFlow、DirectReply、StickyNote 等。`Start` 已弃用，起点使用 BusinessStart。根据业务语义选节点，不造节点类型，不把锚点名称误作 output 字段。

模型、凭据、知识库、向量库、店铺、专家、子流程等运行时对象均保留待配置占位。通知 webhook、签名密钥及密码类型配置不得从别的 flow 或记忆沿用。记录触发器需用户在工作流界面保存后才实际触发；触发和写表应绑定用户选择的真实表。

## Endpoint 与请求合同

所有 endpoint 的方法、常用参数和作用如下。ID 路径参数须用实际值解析；以大括号模板列出的 endpoint/toolName 是路由名，不可改写为别名。除明确列出的请求字段外，不要臆造 API 字段；只传目标 API 要求的对象。

| 方法 | endpoint 与精确 toolName | arguments 请求对象 | 用途与主要响应 |
|---|---|---|---|
| POST | `api/v1/chatflows` | `{"name":"<展示名>","type":"AGENTFLOW","flowData":{"description":"...","usecases":[],"nodes":[...],"edges":[...]}}` | 创建 flow。响应提供服务端 flow 信息和新 `workflowId`。创建成功只说明服务端创建，不代表已发布或执行通过。 |
| GET / PUT | `api/v1/chatflows/{workflowId}` | GET：`{"workflowId":"<id>"}`。PUT：`{"workflowId":"<id>","name":"<展示名>","type":"AGENTFLOW","flowData":{...}}` | GET 读取完整 flow 与 flow type；PUT 更新同一 ID 的 flow。更新前应读取当前基线并保留未指定字段。 |
| GET | `api/v1/chatflows/{workflowId}/version-history` | `{"workflowId":"<id>"}` | 读取 flow 的历史变更概况。 |
| GET | `api/v1/chatflows/{workflowId}/versions` | `{"workflowId":"<id>","page":1,"limit":20}` | 按页列出历史版本及版本元信息。分页默认小页，避免不必要的重复查询。 |
| GET | `api/v1/chatflows/{workflowId}/versions/{version}` | `{"workflowId":"<id>","version":2}` | 读取某版本详情/快照。 |
| GET | `api/v1/chatflows/{workflowId}/versions/{fromVersion}/diff/{toVersion}` | `{"workflowId":"<id>","fromVersion":1,"toVersion":2}` | 比较任意两版；方向为 from → to，提取实际变化摘要。 |
| POST | `api/v1/chatflows/{workflowId}/versions/{version}/restore` | `{"workflowId":"<id>","version":2,"expectedUpdatedDate":"<当前版本更新时间>"}` | 还原服务端版本。并发条件若该部署要求 `expectedUpdatedDate`，必须使用刚查询到的值；不猜时间戳。还原写入新的历史状态。 |
| GET | `api/v1/proxy/workflow-mappings/{sourceKey}` | `{"sourceKey":"<sourceKey>","flowType":"AGENTFLOW"}` | 读取 sourceKey 与服务端 workflow 的映射。`workflowId` 才是已有 flow 的唯一身份；映射响应不授权创建重复 flow。 |
| POST | `api/v1/prediction/{workflowId}` | 按触发类型提供输入，例如 `{"workflowId":"<id>","question":"<输入>"}`；其他键需从当前 flow 触发器契约确认 | 发起一次运行。响应中的 `executionId` 用于后续查询。不要凭空加入 webhook、session 或资源字段。 |
| GET | `api/v1/executions` | `{"agentflowId":"<workflowId>","page":1,"limit":10}` | 列出某 flow 的执行记录，读取 `total`、`data[]` 中的执行 ID、状态、时间和错误摘要。 |
| GET | `api/v1/executions/{executionId}` | `{"executionId":"<executionId>"}` | 查询单次记录，读取运行状态、逐节点轨迹、输入/输出和错误。谨慎展示敏感字段。 |

### 参数和代理调用细则

- 采用结构 `{"toolName":"<精确 endpoint>","arguments":{...}}`。路径参数既用于确定 endpoint 对象，也按当前 `proxy_call` schema 放入 `arguments`；查询字段与 JSON 字段同处一个对象。不要包裹 `body`、`params` 或 `data`。
- GET 参数应只包含接口路径变量与查询字段；POST/PUT 参数包含接口请求 JSON 的直接字段。方法由 endpoint 路由契约决定，不能把 GET 改成 POST 或反之。
- 返回结构先检查 MCP 的 `isError` 和 MCP schema，再检查下游 `errcode`、`errorCode`、`code`、`success`、消息和 data。text JSON 只解析一次。下游 HTTP 成功响应不保证内部运行成功。
- `api/v1/proxy/workflow-mappings/{sourceKey}` 的路径和查询参数应由 reference 上的接口映射语义组合；如当前连接器 schema 对路径变量的编码方式有明确要求，以 schema 为准。不能把 `sourceKey` 变成另一个自造 endpoint。

## 业务动作与身份规则

### 创建、更新、解释和校验

1. 按意图区分 generate、refine、explain、validate、export、run、runs 和 history。run/runs/history 不生成 JSON。
2. 创建或修改流程时先说明触发器、主路径、节点选择、分支和关键输入。用户需求明确或已明确要求立即处理时，可在同一轮先说明方案再执行；若业务目标关键条件缺失，不凭空决定外部动作或资源。
3. 修改已有 flow 时，使用对话中的 `<linkfox-flow-info id="...">` 或当前接口查得的 workflowId；服务端详情是基线。身份固定，不得因本地文件、sourceKey 或名称生成副本。
4. 未改的节点 id、位置、inputs、credentials 与连线维持服务端值。节点级修改只改用户指定节点及必要的下游引用。触发器配置在 refine 中默认锁定；只有用户明确要求时才更换。
5. 解释和校验不写入服务端。校验 Agentflow v2 顶层结构、节点类型、`id` 与 `data.id`、边的锚点/target、条件分支、跨节点 output 路径及运行时占位。
6. 生成后不自动运行，不将保存、服务端 mapping 或 JSON 校验说成运行验证。服务端响应未确认写入成功时，报告阶段性结果，不报告完整成功。

### 节点建模和数据引用

- BusinessStart 唯一且无入边。Loop、DirectReply 和 End 无出边；分支节点的出口与其条件一一对应；Iteration 子节点带正确 parentNode 关系。
- 边连接不表示数据自动传递。跨节点值使用该节点真实 `output` 字段引用。常见字段包括 LinkfoxHTTP/HTTP `output.http.data`；Agent、LLM、Tool、Retriever、CustomFunction、DirectReply、ExecuteFlow `output.content`；DataReader `output.<outputVariableName>`；CrossBorderExpert `output.expertResult`；SendNotification `output.status`、`successChannels`、`failedChannels`；WriteFile `output.recordCount`、`target`、`result`；FillForm `output.filledForm`。以节点 reference 和实际类型为准。
- `{{ }}` 变量引用必须落在实际存在的上游 output 或 state 字段。BusinessStart 不提供可预声明的 startState。Flow State 只用于必要的跨节点状态；优先直接引用 Node Output。
- LinkfoxHTTP 每个节点都需核实对应 API 的 path、method 和真实业务 body；不能以空对象占位代替必需业务参数。异步创建接口需要查询 taskId 并按状态控制等待与结束，不在创建后立即引用最终结果。
- 不用 HTTP/CustomFunction 手工模拟已有专用 LinkFox 自定义节点。需要代码时优先 CustomFunction；仅用户明确要求 Python，或下游确需结构化 Python result / 专用解析能力时考虑 CustomPythonFunction。

## 执行与执行记录

### 一次执行

- 仅当用户明确要求运行已存在 flow 时执行。目标必须有 workflowId；身份缺失时不能按展示名猜测。
- 执行前检视当前 flow type 和可用的运行时资源配置。模板节点缺模型、店铺、专家、表、通知机器人或子流程时说明缺项并停止；不要自行绑定凭证。linkfoxAgentApi 凭据由系统管理，不要求用户在画布绑定。
- 如果运行会发通知、改表、调用外部接口或执行其他不可逆业务动作，执行前概述动作和目标；用户已明确说“直接执行/我知道”时不重复要求同义确认，但仍要让其知道实际影响。
- 每次只发起一条 prediction。成功响应要有 `executionId`；没有 ID 不能宣称已记录一次运行。`runStatus` 不是 `FINISHED` 时不得称执行成功。`FINISHED` 仍要检查失败节点、必需节点是否到达、业务断言及 action result。
- 执行超时或 504 后不要再发起 prediction。先用执行列表查是否存在最新 `INPROGRESS`，再查该 execution 的详情；按需间隔检查，不连续刷新。执行记录可用于核对实际节点输入/输出，但用户敏感信息仅最小化展示。
- FillForm / HumanInput 人工交互节点不能通过一次普通 prediction 自动完成提交。应说明该流程需要在 WorkBuddy/工作流界面完成人工输入。

### 执行记录

- 列表请求使用 `agentflowId`、`page`、`limit`。用户请求最近记录时小页查询即可；列表项报告时间、状态、`executionId` 和错误摘要。
- 单次详情以 executionId 查询；节点轨迹中的 `data.input`、`data.output`、`data.error` 可帮助定位错误。只展示与问题相关的字段，不泄露凭证、完整个人联系方式或不必要的业务数据。
- 无结果如实说明暂无记录。执行状态字段 `state`、工作流级 `runStatus` 和业务断言是不同维度，分别解释。

## 版本历史与还原

- 查看历史：先按需读取版本历史概况或列表。展示版本号、操作者、时间和可读变更说明；不必为了确认列表响应再重复读同一数据。
- 查看版本：用准确版本号读取版本详情。比较版本时用 from → to 顺序，允许非相邻版本，不把变化方向颠倒。
- 还原是写操作，必须先确认目标 workflowId 和版本号，查询当前最新版本并获取还原将覆盖的差异，向用户展示影响，再等待本次明确确认。
- 若服务端提供并发保护值，把刚读到的 `expectedUpdatedDate` 用于 restore。发生版本竞争、并发冲突、权限错误或用户目标无法验证时停止，报告新版本信息并重新查询；不得把并发校验改成最新值后静默覆盖。
- 只有 restore 响应明确成功才报告还原成功，并说明服务端新版本号（如果返回）。历史读取失败或权限不足时不通过更新 flow JSON 手工模拟还原。

## 错误、费用与隐私

- MCP 缺失、schema 错误、MCP 401 与下游业务 401/402/403 分层处理。MCP 401 查看 WorkBuddy 连接器；下游 401 检查业务账号/资源状态；402 报告积分/余额不足；403 报告权限不足。详细用户指引见 [onboarding.md](onboarding.md)。
- 相同 `toolName + arguments` 同一任务内不重复调用。写操作响应不明时先只读核验，禁止自动重放；对可重复的 GET 也应按用户意图和计费需要控制调用。
- WorkBuddy 自动注入授权。Skill 与 MCP 参数不得包含 authorization header、API Key、token、JWT、手机号或连接器凭证。错误日志和结果不得回显凭证。
- 流程执行、版本写入和部分服务端管理可能消耗积分。高频或用户对费用预期不明确时应在执行前提醒并由用户决定；不能基于旧工具行为承诺免费、缓存或自动落盘。

## 已盘点源脚本类别

输入目录脚本按职责盘点后，所有访问服务端的脚本均不纳入本包；旧认证引导脚本也不纳入。保存、上传、拉取、运行、执行列表、历史版本和 API 文档查询脚本均包含网络请求，不得从本 skill 调用。旧认证模块不保留。纯结构校验、身份映射、预检和本地路径等脚本也未保留为 helper：MCP 契约不提供那些旧本地缓存、文件写入或 stdout 行为，本 skill 的业务调用只经 `LinkFox.proxy_call`。有价值的结构校验、幂等、确认、脱敏和状态机规则已在本 reference 与顶层 skill 中表达。
