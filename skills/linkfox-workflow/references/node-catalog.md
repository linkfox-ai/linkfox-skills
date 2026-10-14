# linkfox-workflow Agentflow v2 节点索引

不要一次加载全部节点细节。先读本文件确定需要的节点，再**只读取**对应的分类参考；所有完整参数、版本、输出锚点和限制都在分类文件中。

| 需求或节点 | 读取文件 |
| --- | --- |
| 任意 flow 的骨架、ID、edge、变量、Start、StickyNote | `flow-structure.md`（生成/修改/校验时必读） |
| Agent、LLM、Tool、Retriever、结构化输出 | `nodes-ai-and-knowledge.md` |
| Condition、ConditionAgent、Loop、Iteration、HumanInput | `nodes-control-flow.md` |
| HTTP、CustomFunction、**CustomPythonFunction**、ExecuteFlow、DirectReply | `nodes-integration-and-output.md` |
| **LinkFox 自定义节点**：BusinessStart / CrossBorderExpert / DataReader / FillForm / SendNotification / WriteFile / LinkfoxHTTP / End | `nodes-linkfox-custom.md` |
| 使用变量引用（`{{...}}`）的任何节点 | `variable-substitution.md`（必读！） |
| **引用什么字段**：各节点真实 output 字段、`$flow.state` 读写、内置变量 | `output-and-state.md`（**固定读**，与本文件、`flow-structure.md` 同级） |

## 读取规则

1. 生成、修改或校验 flow 时，本文件 + `flow-structure.md` + `output-and-state.md` 是**三个固定读项**，不按需、不跳过。
2. **`inputParams` 大半由脚本代填,不用手写**：BusinessStart / FillForm / CustomFunction / CustomPythonFunction / CrossBorderExpert / SendNotification / WriteFile / End / Condition / LinkfoxHTTP / HTTP / HumanInput(fixed) 整个 `inputParams` 字段别写，`save_workflow.py` 自动代填（含 `acceptVariable` 标记）。**只有 flow 里出现要手写 `inputParams` 的节点**（Agent / LLM / Tool / Retriever / ConditionAgent / ExecuteFlow / Loop / Iteration / DataReader / DirectReply，或 HumanInput 的 dynamic 分支）**才需要读 `variable-substitution.md`**。它与固定项 `output-and-state.md` 分工明确：前者管"字段要不要标 `acceptVariable`"，后者管"引用哪个字段"。最高频的错法是把输出锚名（`data` / `sent` / `written`）当成 output 字段——那样运行时不报错也不替换，用户看到的是字面量。
3. 只要计划使用某个节点，就读取其所在分类文件；涉及多个分类时可同时读取多个。
4. 不生成未读取其分类说明的节点；不要靠节点名猜 inputs、operation 或 output 路径。

## 支持节点

**原生 15 个**（`Start` 已弃用，禁止生成；开始节点一律用 `BusinessStart`）：`Start` / `Agent` / `LLM` / `Tool` / `Retriever` / `Condition` / `ConditionAgent` / `Loop` / `Iteration` / `HumanInput` / `HTTP` / `CustomFunction` / `ExecuteFlow` / `DirectReply` / `StickyNote`。

**LinkFox 自定义 9 个**（本 linkfox-workflow 系统分支已注册，全部属于 `Agent Flows` 分类）：`BusinessStart` / `CrossBorderExpert` / `DataReader` / `FillForm` / `SendNotification` / `WriteFile` / `LinkfoxHTTP` / `End` / `CustomPythonFunction`。前 8 个详见 `nodes-linkfox-custom.md`；`CustomPythonFunction`（沙箱里执行 Python）与 CustomFunction 同类，写在 `nodes-integration-and-output.md`。

**代码节点默认 JS**：两者都能实现时用 `CustomFunction`（JS）。只有下游要按字段取结果、要 pandas / 解析 PDF·Word·Excel·PPT·HTML、或用户明确要 Python 时才用 `CustomPythonFunction`（引用 `output.result.<字段>`）；延时 sleep 永远用 JS。两者都跑在沙箱里、单次 60 秒上限，选型细则见 `nodes-integration-and-output.md` 末尾。

选择规则：涉及亚马逊授权店铺 / 业务定时启动 / 邮件、飞书、钉钉通知 / 跨境专家平台 / Linkfox 多维表 / CSV / Excel 读取等场景时，**优先使用 LinkFox 自定义节点**，不要用原生 HTTP + CustomFunction 手工模拟。调 Linkfox 工具网关（`tool-gateway.linkfox.com`）或其他 Linkfox 内部服务时用 `LinkfoxHTTP`（只填相对路径，认证头自动注入），只有调第三方外部 API 才用原生 `HTTP`。

**涉及模型 / AI 推理的场景（对话生成、语言理解判断、动态分支等）优先使用 `CrossBorderExpert`**（调用跨境专家平台已配置的专家，见 `nodes-linkfox-custom.md`），**不要默认生成原生 `Agent` / `LLM` / `ConditionAgent`**。仅当需求确实依赖 `CrossBorderExpert` 不支持的能力——Tool 调用、RAG 知识库检索、Structured Output，或需要节点内直接由 LLM 做动态自然语言分支判断——才允许使用原生 `Agent` / `LLM` / `ConditionAgent` 兜底，并在方案里点明兜底原因（"因为需要 XX 能力所以用原生节点，不是默认选择"）。`Tool` / `Retriever` 不受此限制：它们是确定性调用 / 检索，不是"调用模型做推理"。

不要生成旧 chatflow 节点、v1 multiagent 节点或自造节点。

节点契约的机械部分（`data.name` / `data.type` / 顶层 `type` / `version` / `color` / `baseClasses` / 输出锚名）由 `save_workflow.py` 落盘前逐字段机械校验，以它报的 `ERROR:` 为准（不要去 Read `scripts/` 下的源码）：未注册的 `data.name`、`data.type` 或顶层 `type` 不匹配一律 error。这些常量**缺失时会被自动补齐**，所以生成时可以省略；一旦写了就必须写对。
