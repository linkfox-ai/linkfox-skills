---
name: linkfox-wb-workflow
display_name: LinkFox 运营流程
display_name_en: LinkFox Workflow Operations
description: 面向运营团队设计、维护和运行 Agentflow v2 流程，支持校验、执行跟踪与版本管理。
description_zh: 当用户需要从自然语言创建或修改运营流程、解释或校验流程 JSON、运行已有流程、查看执行结果或比较和还原历史版本时使用。通过 LinkFox MCP 管理 Agentflow v2，并提供可审阅的流程结构、运行状态和版本变更摘要。流程运行可能产生外部业务动作并消耗积分；不负责发布、删除流程或删除执行记录。
description_en: Use when users need to design or update an Agentflow v2 operations workflow from natural language, explain or validate a workflow, run an existing workflow, inspect execution records, or compare and restore versions. Uses LinkFox MCP to manage workflows and report reviewable structures, run states, and version changes. Runs may trigger external actions and consume credits. Does not publish or delete workflows or execution records.
icon: icons/logo.png
version: 1.0.0
author: Linkfox
---


> [!IMPORTANT]
本 Skill 必须依赖 MCP “LinkFox”。如未安装该MCP，请明确通知用户：
> 请先安装 LinkFox 连接器：
> - 在 WorkBuddy 左侧找到 “专家·技能·连接器” → “连接器”；
> - 搜索关键词 “LinkFox”，并安装连接器 “LinkFox”（注意：是 linkfox，不是 linkfox-product-selection），按指引完成登录授权；
> - 返回 WorkBuddy 重试。

# LinkFox 运营流程（LinkFox Workflow Operations）

为运营人员设计、维护和运行 Agentflow v2 流程：把业务目标转成结构清晰、可检查的流程；在获得所需确认后保存或更新；用户明确要求时运行流程、查看执行记录、比较历史版本或还原指定版本。运行结果以服务端状态和节点详情为准，不把“已保存”说成“已验证”，也不把“执行结束”说成业务验收通过。

本能力覆盖子能力标识 `linkfox-workflow` 和 11 个 API operation，分别处理流程创建、读取与更新，执行、执行记录以及版本历史。所有业务 API 统一经 `LinkFox.proxy_call` 调用；参数、方法、响应字段及安全约束见 [references/linkfox-workflow.md](references/linkfox-workflow.md)。认证异常处理见 [references/onboarding.md](references/onboarding.md)。

## 能力边界

### 能力范围

- **创建与维护流程**：按用户的运营目标生成或修改 Agentflow v2 的 `{description, usecases, nodes, edges}` 结构，说明使用的节点和主要分支；通过 `POST api/v1/chatflows` 创建，通过 `GET` / `PUT api/v1/chatflows/{workflowId}` 读取或更新流程。精确映射和请求体见 reference。业务动作应选自受支持的 24 类节点，起点使用 `BusinessStart`。
- **解释与校验流程**：解释用户提供的 Agentflow v2 JSON，检查顶层结构、节点身份、边和引用关系、运行时占位与业务逻辑；校验问题和建议以实际工作流结构及本 skill 的节点契约为准。解释和校验本身不修改服务端流程。
- **查询流程身份与映射**：按 `sourceKey` 查询 `api/v1/proxy/workflow-mappings/{sourceKey}`，或按 `workflowId` 读取流程详情。更新已有流程始终以 `workflowId` 为唯一身份；流程名和文件名不是身份替代品。
- **执行与排障**：用户明确要求执行时，经 `POST api/v1/prediction/{workflowId}` 发起一次运行；读取返回的 `executionId`，再使用 `GET api/v1/executions` 和 `GET api/v1/executions/{executionId}` 查询运行列表或详情。区分 `runStatus`、服务端执行状态、节点错误和业务断言。
- **历史查看、比较与还原**：通过版本历史、版本列表和版本详情读取变更，使用 `api/v1/chatflows/{workflowId}/versions/{fromVersion}/diff/{toVersion}` 比较任意两版。还原使用 `POST api/v1/chatflows/{workflowId}/versions/{version}/restore`，必须先展示影响并取得用户对该次还原的明确确认。

### 边界与限制

- **只支持 Agentflow v2**：不生成旧版 chatflow 或 v1 multiagent，不自造节点类型。`Start` 已弃用；新流程使用唯一 `BusinessStart` 起点。节点类别、输出字段及引用规则见 reference。
- **不发布、不删除**：不发布或删除流程，不删除执行记录；不把保存或上传等同于发布、部署或上线。
- **不自动运行**：生成、修改或还原后不顺手执行。只有用户清楚要求运行时才发起执行；包含通知、写文件、外部接口等副作用节点时，先简要说明实际影响，并在适用时取得针对本次运行的明确确认。
- **已有流程身份不可猜**：refine、运行、执行记录和历史操作均需可靠的 `workflowId`。已有流程更新必须原地更新该 ID，不能因名称相似或本地文件名相同而新建副本。缺少身份且无法从会话上下文确定时，需请用户指明流程。
- **用户配置留空**：模型、凭据、知识库、店铺、专家、子流程和外部资源等运行时对象不能猜测或从其他流程复制。通知 webhook、签名密钥及密码类字段留空，除非用户在当前流程配置中明确提供。
- **不承诺旧脚本能力**：MCP 调用不会自动提供旧脚本的本地落盘、缓存、stdout 摘要或本地索引行为。没有 MCP 支持时停止并提示安装或重载 LinkFox 连接器，不回退其他调用方式。
- **计费和实时状态**：执行会消耗积分并可能产生真实业务动作；不要为确认结果而重复运行、自动重试写操作或连续轮询。只报告实际返回的状态和错误。

## 工具选择指南

先根据用户希望得到的结果选择最小的一组只读或写入 operation，再到【业务需求路由速查】查 reference、endpoint 和精确 `toolName`。同一需求涉及多个阶段时应分步呈现结果，不把查询、更新、运行、还原连成未经确认的自动流程。

| 需求 / 用户说 | 默认推荐 | 何时换用其他 |
|---|---|---|
| “按这个目标设计一个运营流程”“修改这段流程 JSON” | 自然语言生成或修改方案；创建用 `api/v1/chatflows`，更新前先识别 `workflowId` 并读取详情 | 只想了解现有结构时只用详情查询；用户只是贴 JSON 求解释或检查时不写入服务端 |
| “这个流程保存了吗”“查 sourceKey 对应哪个流程” | `api/v1/proxy/workflow-mappings/{sourceKey}` | 已有 `workflowId` 时直接查询 `api/v1/chatflows/{workflowId}` 取详情；不要根据显示名猜 ID |
| “看一下这个流程”“解释这个 flow” | `GET api/v1/chatflows/{workflowId}` 或解释用户提供的 JSON | 要检查结构时走校验说明；要编辑时先给出变更方案并按确认策略更新原流程 |
| “帮我检查 JSON 是否符合规范” | 本地按 Agentflow v2 契约检查，不改服务端 | 需要知道服务端保存版本时另行查询详情或历史，不将校验冒充服务端写入验证 |
| “运行一下这个流程” | `POST api/v1/prediction/{workflowId}` 一次 | 用户要查看之前某次执行时使用执行记录接口；超时或 504 时先检查执行记录，不重跑 |
| “上次为什么失败”“列出最近运行” | `GET api/v1/executions`，按 `agentflowId`、`page`、`limit` 查列表 | 要看单次节点轨迹或输入输出时，取到 `executionId` 后用详情接口 |
| “列出历史版本”“看看第 3 版改了什么” | `GET .../versions`、`GET .../versions/{version}` | 要比较两版结构差异时用 `.../diff/{toVersion}`；还原需另行确认 |
| “撤回到第 N 版” | 先查询最新版本并生成差异摘要 | 展示将改动内容，用户确认本次还原后才调用 restore；如果期间有新版本，停止并重新核对 |

### 选择思路

- 先区分**只读**与**写入/运行**：详情、映射、执行记录和历史版本读取是只读；创建、更新、执行和还原会改变服务端状态或触发真实动作。
- 用户同时说“修改并运行”时，先处理流程修改并报告是否成功，再把运行作为明确独立步骤；不得因更新成功推断用户已授权运行。
- 执行记录列表适合定位近期成功或失败，详情适合检查某次运行的节点轨迹。不要用反复运行替代历史排障。
- 版本详情回答单一版本内容，diff 回答两版间的变化。还原会写入新的服务端版本，不能当作无副作用的查询。
- 用户意图、目标流程或恢复版本不明确时，先把已有只读信息整理出来；只有依赖的信息确实缺失时才请求用户补充，不猜测身份或版本。

## 业务需求路由速查

| 子能力 | 业务能力 | reference | 原 endpoint | 精确 toolName |
|---|---|---|---|
| `linkfox-workflow` / 创建流程（`POST`） | `references/linkfox-workflow.md` | `api/v1/chatflows` | `api/v1/chatflows` |
| `linkfox-workflow` / 读取或更新流程（`GET` / `PUT`） | `references/linkfox-workflow.md` | `api/v1/chatflows/{workflowId}` | `api/v1/chatflows/{workflowId}` |
| `linkfox-workflow` / 查询版本变更历史（`GET`） | `references/linkfox-workflow.md` | `api/v1/chatflows/{workflowId}/version-history` | `api/v1/chatflows/{workflowId}/version-history` |
| `linkfox-workflow` / 列出版本（`GET`） | `references/linkfox-workflow.md` | `api/v1/chatflows/{workflowId}/versions` | `api/v1/chatflows/{workflowId}/versions` |
| `linkfox-workflow` / 查看指定版本（`GET`） | `references/linkfox-workflow.md` | `api/v1/chatflows/{workflowId}/versions/{version}` | `api/v1/chatflows/{workflowId}/versions/{version}` |
| `linkfox-workflow` / 比较两个版本（`GET`） | `references/linkfox-workflow.md` | `api/v1/chatflows/{workflowId}/versions/{fromVersion}/diff/{toVersion}` | `api/v1/chatflows/{workflowId}/versions/{fromVersion}/diff/{toVersion}` |
| `linkfox-workflow` / 还原指定版本（`POST`） | `references/linkfox-workflow.md` | `api/v1/chatflows/{workflowId}/versions/{version}/restore` | `api/v1/chatflows/{workflowId}/versions/{version}/restore` |
| `linkfox-workflow` / 查询 sourceKey 映射 | `references/linkfox-workflow.md` | `api/v1/proxy/workflow-mappings/{sourceKey}` | `api/v1/proxy/workflow-mappings/{sourceKey}` |
| `linkfox-workflow` / 执行一次流程（`POST`） | `references/linkfox-workflow.md` | `api/v1/prediction/{workflowId}` | `api/v1/prediction/{workflowId}` |
| `linkfox-workflow` / 查询执行列表（`GET`） | `references/linkfox-workflow.md` | `api/v1/executions` | `api/v1/executions` |
| `linkfox-workflow` / 查询执行详情（`GET`） | `references/linkfox-workflow.md` | `api/v1/executions/{executionId}` | `api/v1/executions/{executionId}` |

路径参数以实际资源 ID 填充，`toolName` 保持上述模板的精确路径和大小写；其余路径、查询及请求对象直接作为 `arguments`。所有 API 的参数位置、方法和返回结构见 [references/linkfox-workflow.md](references/linkfox-workflow.md)。

## MCP 调用方式

- **唯一业务工具**：仅使用 `LinkFox.proxy_call`。调用结构为 `{"toolName":"<精确 endpoint>","arguments":{...}}`，其中 endpoint 不带前导 `/`。`toolName` 保留路径分隔符、大小写和路径变量；把原请求对象直接放入 `arguments`，不增加 `body`、`params`、`data` 或第二层 `arguments`。无业务参数时传 `{}`。
- **路径与请求参数**：用用户明确提供或已查询到的 `workflowId`、`executionId`、`sourceKey` 和版本号填充 endpoint 路径变量。GET 查询参数与 POST/PUT JSON 请求字段都放在同一个 `arguments` 对象中，字段必须来自 reference 或当前 API 契约。
- **WorkBuddy 自动授权**：WorkBuddy 自动注入 Linkfox Authorization。不得索取、展示或在配置、脚本或 arguments 中传入 headers、API Key、token、JWT、手机号或其他凭证。
- **响应解析**：先检查 LinkFox MCP 是否存在、schema 是否通过以及响应 `isError`；然后按 MCP 返回结构读取 `structuredContent` 或 `content`。若 `text` 内容是 JSON，只解析一次，再解释下游 `errcode`、`errorCode`、`code`、`success` 和消息字段。不得将 MCP 外层状态误判为业务成功。
- **写操作和去重**：创建、更新、执行和还原之前核对目标对象及动作；需要确认时复述关键对象、变更或副作用并取得明确确认。相同 `toolName + arguments` 在同一任务内不重复调用。结果不确定或超时后，先用只读详情/执行记录确认状态，不重放写请求。
- **失败纪律**：MCP 或 `proxy_call` 缺失时停止业务调用，告知安装或重载 LinkFox 连接器。禁止回退其他 HTTP 调用、旧脚本或网关。schema 错误按返回字段修正；下游业务错误如实呈现，不擅自更改身份、参数或目标版本后重试。
- **完整参数**：必填与可选字段、查询参数、执行输入、分页、历史恢复并发保护和响应字段均见 [references/linkfox-workflow.md](references/linkfox-workflow.md)。认证类异常见 [references/onboarding.md](references/onboarding.md)。

## 使用示例

以下 JSON 展示传入 MCP 的参数形状。实际调用时把业务对象直接放入 `arguments`，`toolName` 使用路由表中的值。ID 均为示例占位值；真实字段按 reference 和用户已提供的信息填写。

### 1. 创建流程

新建一个流程时先形成业务方案和合法 Agentflow v2 JSON，再写入：

```json
{
  "toolName": "api/v1/chatflows",
  "arguments": {
    "name": "订单异常提醒",
    "type": "AGENTFLOW",
    "flowData": {
      "description": "识别订单异常并通知负责人",
      "usecases": [],
      "nodes": [],
      "edges": []
    }
  }
}
```

示例中的 `nodes` 和 `edges` 为空仅表示请求外形，不能作为完整业务流程上传。必须根据目标补全节点和连线，且运行时配置保持待绑定状态。创建成功以服务端返回的 `workflowId` 为准；创建会修改服务端状态并可能消耗积分。

### 2. 查询及更新流程

按已知 ID 查询详情：

```json
{"toolName":"api/v1/chatflows/{workflowId}","arguments":{"workflowId":"wf_示例"}}
```

更新已有流程时保持相同 `workflowId`，请求体仍是流程 `name`、`type` 与完整 `flowData`；只修改用户指定部分，保留其他节点、边和运行时配置。更新不是新建，也不能凭流程名确定对象。写入前核对变更摘要；MCP 返回不确定时先重新读取详情，不盲目重复更新。

### 3. 执行一次流程

用户明确要求运行时发起一次执行：

```json
{
  "toolName":"api/v1/prediction/{workflowId}",
  "arguments":{"workflowId":"wf_示例","question":"检查订单 ORD-001 的处理状态"}
}
```

执行输入遵照当前流程触发器要求；如需 webhook、session 或其他输入字段，先查 reference 和 flow 契约，不补造字段。执行可能访问外部服务、发送通知或写数据并产生积分消耗。读取响应中的 `executionId`，随后根据用户意图查看执行详情。`FINISHED` 只代表运行终态，仍需查看节点错误、预期节点是否到达及业务断言。

### 4. 查询执行记录

查询某流程最近执行记录：

```json
{
  "toolName":"api/v1/executions",
  "arguments":{"agentflowId":"wf_示例","page":1,"limit":10}
}
```

查询单次执行详情：

```json
{"toolName":"api/v1/executions/{executionId}","arguments":{"executionId":"exec_示例"}}
```

列表用于定位最近的运行状态和错误摘要；详情用于查看节点级轨迹。先通过列表取得目标 `executionId`，不要猜 ID。遇到执行超时先查列表和详情，避免重复运行形成重复业务动作或额外计费。

### 5. 比较版本与还原

比较第 2 版与第 4 版：

```json
{
  "toolName":"api/v1/chatflows/{workflowId}/versions/{fromVersion}/diff/{toVersion}",
  "arguments":{"workflowId":"wf_示例","fromVersion":2,"toVersion":4}
}
```

还原前先读取版本列表与差异，向用户说明将恢复的流程内容和当前最新版本。得到本次明确确认后调用：

```json
{
  "toolName":"api/v1/chatflows/{workflowId}/versions/{version}/restore",
  "arguments":{"workflowId":"wf_示例","version":2,"expectedUpdatedDate":"从当前版本查询所得的时间戳"}
}
```

并发保护字段以接口实际返回为准；不能编造时间戳。若最新版本已变化或服务端拒绝并发条件，停止还原并重新查询、展示新差异，不用更新后的值绕过用户确认。还原会改变服务端流程并产生新的历史记录。

## 展示规则

1. **方案与流程结构**：用简体中文概述业务目标、触发方式、主路径和关键分支，再列节点设计的要点。展示流程 JSON 时保留字段含义，不把空白运行时凭据描述成已配置。
2. **写入结果**：明确区分已创建、已更新和已还原；报告真实 `workflowId` 与服务端返回的状态。没有写入成功证据时，不说已保存、已部署或已发布。
3. **运行结果**：展示执行时间、`executionId`、终态、失败节点及错误摘要。`runStatus` 不是 `FINISHED` 时不得报告执行成功；即使为 `FINISHED`，也检查 `nodeErrors`、`businessCheck`、`notReachedNodes` 和 action results 后再描述业务结果。
4. **执行记录**：列表按时间和状态摘要，详情按节点汇总输入、输出与错误。避免直接倾倒大型原始 JSON；凭证、个人信息和敏感内容应遮蔽或省略。
5. **历史比较与还原**：用版本号、变更人、时间和实际变化说明差异。还原前说明影响并等待明确确认；还原成功后报告目标版本及新版本号，预览或失败不能报告为已还原。
6. **不确定和空字段**：标注服务端未提供、不可用或空值的字段，不作推断；错误消息按原意转述，并给出与错误对应的修正建议。区分 MCP 层错误和下游业务错误。
7. **数据来源与成本**：说明结果来自 LinkFox 工作流或执行接口，并标注状态查询时间。用户高频运行或未预期积分成本时，运行前提示成本和副作用，由用户决定是否继续。

## 解决认证和积分问题

- **MCP / `proxy_call` 缺失**：停止业务调用，提示用户在 WorkBuddy 安装或重载 LinkFox 连接器；不使用其他调用方式。按需阅读 [references/onboarding.md](references/onboarding.md)。
- **MCP 连接 401**：按连接器认证异常处理，阅读 onboarding 指引并提示用户在 WorkBuddy 检查 LinkFox 登录授权或重载连接器。不要索取或展示认证信息。
- **代理调用成功、下游返回 401**：这是工作流服务的业务认证错误。先报告下游错误语义，并按 onboarding 指引检查账号或服务权限；不要把它当作 MCP 连接授权失败，也不要自行附加凭证重试。
- **下游 402 / 余额不足**：停止执行或写入，说明积分或余额不足，按 onboarding 指引处理。不得通过重复请求探测余额或自动创建订单。
- **下游 403**：报告当前账号或资源无权执行此操作，建议确认是否对目标流程有权限；不通过更换身份或猜测另一个流程继续。
- **其他业务错误**：展示安全的错误摘要和受影响的对象。按错误信息修复流程数据或由用户补全缺失配置；相同参数不自动重试，写入结果不明时优先只读核验。
- **自动授权与凭证**：WorkBuddy 自动注入 Authorization。不得向用户索取、回显、写入或配置凭证，也不得保留 API Key 登录、注册或套餐查询流程。

## 积分消耗说明

> 用户会因积分消耗而支付费用。请充分评估：当需要高频调用本技能，或用户对积分消耗量预期不足时，务必提醒用户，由用户决定是否继续。
