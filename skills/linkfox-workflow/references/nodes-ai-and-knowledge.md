# linkfox-workflow Agentflow v2：AI、工具与知识节点

计划使用 Agent、LLM、Tool、Retriever，或需要结构化输出时读取本文件。通用结构与 edge 规则见 `flow-structure.md`。

> ⚠️ **`Agent` / `LLM` 是模型推理场景的兜底节点，不是默认选择**。涉及模型 / AI 推理的场景优先用 `CrossBorderExpert`（见 `node-catalog.md` 选择规则、`nodes-linkfox-custom.md`）。只有需求确实依赖 `CrossBorderExpert` 不支持的能力——Tool 调用、RAG 知识库检索、Structured Output——才用 `Agent` / `LLM`，并在方案里点出兜底原因。`Tool` / `Retriever` 不受此限制，正常按需使用。

## Agent

- `data.name`: `agentAgentflow`；`data.type`: `Agent`；`version`: `3.2`；`color`: `#4DD0E1`。
- 用于动态调用 tools、检索知识和多步推理。
- 必填：`agentModel`、`agentModelConfig`、`agentReturnResponseAs`（`userMessage` 默认，或 `assistantMessage`）。
- `agentModelConfig` 至少含 `modelName`、`temperature` 和空的 `FLOWISE_CREDENTIAL_ID`；模型和凭据不确定时留占位，不杜撰实例配置。
- 可选：
  - `agentMessages[]`：`{role, content}`；role 为 `system` / `user` / `assistant` / `developer`，content 是 HTML。
  - `agentTools[]`：`{agentSelectedTool, agentSelectedToolConfig:{FLOWISE_CREDENTIAL_ID,...}, agentSelectedToolRequiresHumanInput?}`。tool name 会被清洗成 `[a-z0-9_-]`（最长 64）。加了 tools 就必须选支持 function calling 的模型。
  - `agentToolsBuiltInOpenAI[]`：仅在 `agentModel === 'chatOpenAI'` 时出现，multiOptions，取值 `web_search_preview` / `code_interpreter` / `image_generation`。
  - `agentToolsBuiltInGemini[]`：仅在选用 Gemini 系模型时出现，multiOptions。
  - `agentKnowledgeDocumentStores[]`：`{documentStore:"<id>:<name>", docStoreDescription, returnSourceDocuments?}`。
  - `agentKnowledgeVSEmbeddings[]`：`{vectorStore, vectorStoreConfig, embeddingModel, embeddingModelConfig, knowledgeName, knowledgeDescription}`。
  - `agentEnableMemory`（默认 `true`）；`show: enableMemory` 的字段：`agentMemoryType`（`allMessages` / `windowSize` / `conversationSummary` / `conversationSummaryBuffer`）、`agentUserMessage`；`agentMemoryWindowSize`（`show: memoryType==='windowSize'`，默认 `'20'` 字符串）、`agentMemoryMaxTokenLimit`（`show: memoryType==='conversationSummaryBuffer'`，默认 `'2000'` 字符串）。
  - `agentStructuredOutput[]`、`agentUpdateState[]`（内层 `value` 支持 `acceptNodeOutputAsVariable: true`）。
- `agentModel` 必填，缺了执行失败。
- **`inputParams` 要自己写完整**（Agent 字段多、带 `show` 联动，不在脚本代填范围内）：提示词字段（`agentMessages`、`agentUserMessage`）需要 `acceptVariable: true` 才能正确替换变量。详见 `variable-substitution.md`。
- 输出锚点：`<id>-output-agentAgentflow`。

## LLM

- `data.name`: `llmAgentflow`；`data.type`: `LLM`；`version`: `1.1`；`color`: `#64B5F6`。
- 只做语言处理，不带 tool 或知识库。
- 必填：`llmModel`、`llmModelConfig`、`llmReturnResponseAs`（默认 `userMessage`，另一枚 `assistantMessage`）。模型配置规则与 Agent 相同。
- 可选：
  - `llmMessages[]`：`{role, content}`，role 枚举 `system` / `assistant` / `developer` / `user`。
  - `llmEnableMemory`（默认 `true`）；`show: llmEnableMemory` 的字段：`llmMemoryType`（4 值枚举同 Agent）、`llmUserMessage`；`llmMemoryWindowSize`（`show: memoryType==='windowSize'`，默认 `'20'`）、`llmMemoryMaxTokenLimit`（`show: memoryType==='conversationSummaryBuffer'`，默认 `'2000'`）。
  - `llmStructuredOutput[]`、`llmUpdateState[]`（同 Agent）。
- **`inputParams` 要自己写完整**（LLM 同 Agent，不在脚本代填范围内）：提示词字段需要 `acceptVariable: true` 才能正确替换变量。详见 `variable-substitution.md`。
- 输出锚点：`<id>-output-llmAgentflow`。

## Tool

- `data.name`: `toolAgentflow`；`data.type`: `Tool`；`version`: `1.2`；`color`: `#d4a373`。
- 在确定必须调用某个 tool 时使用；需要自主选 tool 时使用 Agent。
- 必填：`toolAgentflowSelectedTool`（选中后会自动生成 `toolAgentflowSelectedToolConfig`；不可选 `chainTool` / `retrieverTool` / `webBrowser`）、`toolAgentflowSelectedToolConfig`（含空的 `FLOWISE_CREDENTIAL_ID` 和 tool 原生字段）、`toolInputArgs[]`（`show: toolAgentflowSelectedTool==='.+'`；每项 `{inputArgName,inputArgValue}`，name 必须匹配 tool JSON schema）。
- 可选 `toolUpdateState[]`：内层 `value` 支持 `acceptNodeOutputAsVariable: true`。
- 输出锚点：`<id>-output-toolAgentflow`（Tool 有输出，不要当作无输出节点）。

## Retriever

- `data.name`: `retrieverAgentflow`；`data.type`: `Retriever`；`version`: `1.1`；`color`: `#b8bedd`。
- 从已 upsert 的 Document Store 检索（只能选状态为 `UPSERTED` 的 store）。
- 必填：`retrieverKnowledgeDocumentStores[]`（至少一项，**每项只含单字段** `documentStore`，格式 `<uuid>:<name>`，生成时留空占位；不像 Agent 那样有 `docStoreDescription` / `returnSourceDocuments`）、`retrieverQuery`、`outputFormat`（`text` 默认或 `textWithMetadata`）。
- `textWithMetadata` 输出完整 Document 数组的 JSON 文本。
- 输出锚点：`<id>-output-retrieverAgentflow`（有输出）。

## Structured Output（不是节点）

**仅 Agent 和 LLM** 可使用 `<name>StructuredOutput[]`（ConditionAgent 无此字段）。每项：

```json
{
  "key": "<字段名>",
  "type": "string | stringArray | number | boolean | enum | jsonArray",
  "enumValues": "仅 enum（`show: type==='enum'`），逗号分隔",
  "jsonSchema": "仅 jsonArray（`show: type==='jsonArray'`，`hideCodeExecute: true`），字符串化 JSON schema",
  "description": "<字段说明>"
}
```

下游用 `{{ <nodeId>.output.<key> }}` 引用相应字段。

## 选择规则

- 多步自主决策 / 多工具协同 → Agent。
- 单次文本生成、总结、翻译、抽取 → LLM。
- 必须顺序执行某个已知 tool → Tool。
- 从 Document Store 直接检索 → Retriever。
