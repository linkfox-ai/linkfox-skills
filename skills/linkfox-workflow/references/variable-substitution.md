# linkfox-workflow Agentflow v2：变量替换与 inputParams

> **先看要不要读本文件。** `inputParams` 大半由 `save_workflow.py` 代填（见 SKILL.md 的「`inputParams` 交给脚本」一节）：BusinessStart / FillForm / CustomFunction / CustomPythonFunction / CrossBorderExpert / SendNotification / WriteFile / End / Condition / LinkfoxHTTP / HTTP / HumanInput(fixed) 这些节点**整个 `inputParams` 字段别写**，`acceptVariable` 已标好。只用这些节点的 flow 不用读本文件。
>
> 仍需读的情况：flow 里有 **Agent / LLM / Tool / Retriever / ConditionAgent / ExecuteFlow / Loop / Iteration / DataReader / DirectReply**（这些要自己手写 `inputParams`），或 `HumanInput` 用了 `dynamic` 分支。
>
> 下面第 2、3 节的 Condition / HTTP 完整 JSON 已原样进了 `scripts/input_params_specs.py`，留在这里作为对照：改脚本模板前先改这里，反之亦然。

## 机制

变量替换（`{{nodeId.output.path}}`）只对 `inputParams` 里声明了 `acceptVariable: true` 的字段生效。`inputParams` 为空数组或缺少某字段的定义时，该字段里的变量**不会被替换**。

## 核心规则

### 1. `inputParams` 必须完整定义（省略 ≠ 空数组）

要么**整个字段别写**（限脚本覆盖的节点，由 `save_workflow.py` 代填），要么写一份完整定义。`data.inputParams` **不能是空数组** `[]`：空数组是"明确表态没有字段"，不会被代填，`save_workflow.py` 按 error 拒绝落盘。

自己写时必须包含该节点所有可配置字段的完整元数据，尤其是：

- 支持变量替换的字段显式标 `"acceptVariable": true`
- 数组类型字段（如 Condition 的 `conditions`、HTTP 的 `headers`）写完整的 `array` 子字段定义
- 数组子字段中的字符串字段同样各自标 `acceptVariable: true`

### 2. Condition 节点的 inputParams（**operation 名称必须逐字匹配下列枚举**）

`operation` 的 `name` 只能取下列枚举值。写错任何一个（例如 `startWith` / `is` / `greaterThan`）都会让比较失效，永远走 Else 分支：

```json
"inputParams": [
  {
    "label": "Conditions",
    "name": "conditions",
    "type": "array",
    "description": "Values to compare",
    "acceptVariable": true,
    "default": [
      { "type": "string", "value1": "", "operation": "equal", "value2": "" }
    ],
    "array": [
      {
        "label": "Type",
        "name": "type",
        "type": "options",
        "options": [
          {"label": "String", "name": "string"},
          {"label": "Number", "name": "number"},
          {"label": "Boolean", "name": "boolean"}
        ],
        "default": "string"
      },
      {
        "label": "Value 1",
        "name": "value1",
        "type": "string",
        "acceptVariable": true
      },
      {
        "label": "Operation",
        "name": "operation",
        "type": "options",
        "options": [
          {"label": "Contains", "name": "contains"},
          {"label": "Not Contains", "name": "notContains"},
          {"label": "Ends With", "name": "endsWith"},
          {"label": "Starts With", "name": "startsWith"},
          {"label": "Equal", "name": "equal"},
          {"label": "Not Equal", "name": "notEqual"},
          {"label": "Regex", "name": "regex"},
          {"label": "Is Empty", "name": "isEmpty"},
          {"label": "Not Empty", "name": "notEmpty"},
          {"label": "Smaller", "name": "smaller"},
          {"label": "Smaller Equal", "name": "smallerEqual"},
          {"label": "Larger", "name": "larger"},
          {"label": "Larger Equal", "name": "largerEqual"}
        ],
        "default": "equal"
      },
      {
        "label": "Value 2",
        "name": "value2",
        "type": "string",
        "acceptVariable": true
      }
    ]
  }
]
```

**关键点**：

- **不存在** `startWith` / `endWith` / `is` / `isNot` / `isNotEmpty` / `greaterThan` / `lessThan` / `greaterThanOrEqual` / `lessThanOrEqual` 这些操作名，只能用上表的驼峰变体。
- **不存在** `ifConditionName` / `elseConditionName` 字段。Condition 的输出是**固定 2 个锚点** `0` 和 `1`（Else），不通过字段命名。
- string 类型的 `value2` 在 `operation ∈ [isEmpty, notEmpty]` 时隐藏；number 类型的 `value2` 默认 `0`；boolean 类型的 `value1` / `value2` 默认 `false`。
- `regex` 的模式直接写 `\d+` / `\[.*\]`，不必额外转义反斜杠。

### 3. HTTP 节点的 inputParams（**headers/queryParams 是 array，不是 json**）

```json
"inputParams": [
  {
    "label": "Method",
    "name": "method",
    "type": "options",
    "options": [
      {"label": "GET", "name": "GET"},
      {"label": "POST", "name": "POST"},
      {"label": "PUT", "name": "PUT"},
      {"label": "PATCH", "name": "PATCH"},
      {"label": "DELETE", "name": "DELETE"}
    ],
    "default": "GET"
  },
  {
    "label": "URL",
    "name": "url",
    "type": "string",
    "acceptVariable": true
  },
  {
    "label": "Headers",
    "name": "headers",
    "type": "array",
    "acceptVariable": true,
    "optional": true,
    "array": [
      {"label": "Key", "name": "key", "type": "string", "acceptVariable": true},
      {"label": "Value", "name": "value", "type": "string", "acceptVariable": true}
    ]
  },
  {
    "label": "Query Params",
    "name": "queryParams",
    "type": "array",
    "acceptVariable": true,
    "optional": true,
    "array": [
      {"label": "Key", "name": "key", "type": "string", "acceptVariable": true},
      {"label": "Value", "name": "value", "type": "string", "acceptVariable": true}
    ]
  },
  {
    "label": "Body Type",
    "name": "bodyType",
    "type": "options",
    "options": [
      {"label": "JSON", "name": "json"},
      {"label": "Raw", "name": "raw"},
      {"label": "Form Data", "name": "formData"},
      {"label": "x-www-form-urlencoded", "name": "xWwwFormUrlencoded"}
    ],
    "default": "json"
  },
  {
    "label": "Body",
    "name": "body",
    "type": "string",
    "acceptVariable": true,
    "optional": true
  },
  {
    "label": "Response Type",
    "name": "responseType",
    "type": "options",
    "options": [
      {"label": "JSON", "name": "json"},
      {"label": "Text", "name": "text"},
      {"label": "Array Buffer", "name": "arraybuffer"},
      {"label": "Base64", "name": "base64"}
    ],
    "default": "json"
  }
]
```

- `headers` / `queryParams` **必须**是 `type: "array"`（每项 `{key, value}`），不是 `type: "json"`。写成 json 会绕过变量替换和 UI 校验。
- `body` 有两种形态：`bodyType ∈ [json, raw]` 用 string 版；`bodyType ∈ [formData, xWwwFormUrlencoded]` 用 array 版（每项 `{key, value}`）。按实际 `bodyType` 选一份写入 `inputParams`。
- `GET` 请求即使填了 `body` 也会被忽略。

### 4. Agent / LLM / ConditionAgent 提示词字段

`agentMessages` / `llmMessages` 是 `type: "array"`；单个 message 的 `content` 需要 `acceptVariable: true`。`agentUserMessage` / `llmUserMessage` / `conditionAgentInput` 都需要 `acceptVariable: true`。memory 字段（`agentMemoryWindowSize` 等）的默认值是**字符串**（`'20'` / `'2000'`），不要写成数字。

### 5. `<node>UpdateState[]` 的 value

Agent / LLM / Tool / CustomFunction / ConditionAgent 的 `<name>UpdateState[]` 内层 `value` 支持 `acceptNodeOutputAsVariable: true`（画布上会弹出节点输出下拉）；`inputParams` 里保留这个标记即可。

## 示例：按字段值判断分支

**错误**（`inputParams` 为空，变量不替换）：

```json
{
  "id": "conditionAgentflow_2",
  "data": {
    "name": "conditionAgentflow",
    "type": "Condition",
    "inputParams": [],
    "inputs": {
      "conditions": [{
        "type": "string",
        "value1": "{{httpAgentflow_1.output.http.data.<字段名>}}",
        "operation": "equal",
        "value2": "<String>"
      }]
    }
  }
}
```

**正确**：整个 `inputParams` 字段别写（Condition 由脚本代填），或采用第 2 节的完整定义；`sourceHandle` 用 `-output-0` / `-output-1`。

## 生成工作流时的检查清单

输出最终 JSON 前必须检查：

1. 没有任何节点写 `inputParams: []`（脚本覆盖的节点整个字段别出现；其余节点写完整定义）。
2. 手写的 `inputParams` 里，使用变量引用（`{{...}}`）的字段包含 `acceptVariable: true`。字段已声明、只漏了这个布尔时，`save_workflow.py` 会自愈并记进 `normalized`（仅 `string` / `array` / `json` 类型）；字段整块没声明仍报 error。
3. Condition 的 `operation` 逐字属于枚举（`contains` / `notContains` / `endsWith` / `startsWith` / `equal` / `notEqual` / `regex` / `isEmpty` / `notEmpty` / `smaller` / `smallerEqual` / `larger` / `largerEqual`），boolean 类型只允许 `equal` / `notEqual`。
4. HTTP 的 `headers` / `queryParams` 是 `array`，`body` 依 `bodyType` 选 string 或 array 变体。
5. HumanInput 的输出锚点用 `proceed` / `reject`，不是 `0` / `1`。
6. Condition / ConditionAgent 的输出**只有 2 个锚点**（`0` 和 `1`），需要多路分支就串联。

## 不确定 inputParams 时

以 linkfox-workflow 系统画布导出的工作流 JSON 里的 `inputParams` 为准，不要凭记忆或猜测。
