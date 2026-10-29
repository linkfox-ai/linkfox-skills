# linkfox-workflow Agentflow v2：HTTP、函数、子流程与回复节点

计划使用 HTTP、CustomFunction、ExecuteFlow 或 DirectReply 时读取本文件。通用结构与 edge 规则见 `flow-structure.md`；输出路径不确定时读 `output-and-state.md`。

## HTTP

- `data.name`: `httpAgentflow`；`data.type`: `HTTP`；`version`: `1.1`；`color`: `#FF7F7F`。
- 必填：`method`（默认 `GET`；枚举 `GET` / `POST` / `PUT` / `PATCH` / `DELETE`——不含 `HEAD`/`OPTIONS`）和 `url`（可使用 `{{ }}`）。
- 可选：
  - `headers[]`、`queryParams[]`：**type `array`**，每项 `{key, value}`（不是单个 JSON 对象）。
  - `bodyType`：`json`（默认）/ `raw` / `formData` / `xWwwFormUrlencoded`。
  - `body`：有**两个同名字段**——`type: 'string'`（`show: bodyType∈['raw','json']`）与 `type: 'array'` of `{key, value}`（`show: bodyType∈['formData','xWwwFormUrlencoded']`）。
  - `responseType`：`json`（默认）/ `text` / `arraybuffer` / `base64`。
  - Credential 可选，凭据类型 `httpBasicAuth` / `httpBearerToken` / `httpApiKey`（同一节点存在多种时优先级 basic → bearer → api-key）。
- **`inputParams` 整个字段别写**：HTTP 的 `inputParams` 由 `save_workflow.py` 代填，`body` 的 string / array 变体按 `inputs.bodyType` 自动挑。写成 `[]` 不算省略、会报 error。
- 输出锚点：`<id>-output-httpAgentflow`。
- 响应体为 `{{ <id>.output.http.data }}`；状态码、状态文本、响应头为 `.output.http.status` / `.statusText` / `.headers`。禁止把 `{{ <id>.output }}` 用作下游值。
- 请求（含重定向）只能访问公网地址，内网地址会被拦截；`GET` 请求会忽略 `body`。
- HTTP 由 linkfox-workflow 系统服务端发起；`ipinfo.io/json` 看到的是服务端出网 IP，不是浏览器访问者 IP。需要访问者 IP 时，由入口或反向代理显式传入。

## CustomFunction

- `data.name`: `customFunctionAgentflow`；`data.type`: `CustomFunction`；`version`: `1.1`；`color`: `#E4B7FF`。
- 必填 `customFunctionJavascriptFunction`（type `code`）：沙箱 JS，必须 `return` 字符串或可序列化对象。可用变量：`$flow.sessionId` / `$flow.chatId` / `$flow.chatflowId` / `$flow.input` / `$flow.state`、后处理数据挂在 `$flow` 上（`rawOutput`、`chatHistory`、`sourceDocuments`、`usedTools`、`artifacts`、`fileAnnotations`）；`$vars.<name>` 访问全局变量。沙箱**只预导入 `axios`**——`node-fetch` 等需要在函数体内 `require`。
- 可选 `customFunctionInputVariables[]`：每项**只能**是 `{variableName, variableValue}`；代码以 `$<variableName>` 读取。写成 `name` / `value` 会被忽略，导致变量未定义。

  ```json
  {
    "variableName": "<变量名>",
    "variableValue": "{{ httpAgentflow_1.output.http.data }}"
  }
  ```

  代码中使用 `const data = $<变量名>;`。
- 可选 `customFunctionEnvVariables[]`：每项 `{variableName, variableValue}`，执行时注入 `process.env`，代码里 `process.env.REGION` 读取。**默认什么都不注入**——没配这一栏时 `process` 是 `undefined`，部署进程的环境变量一个都带不进去。`variableValue` 支持 `{{ }}`；密钥用内置绑定（见下方「沙箱环境变量」），不要手填明文。
- 可选 `customFunctionUpdateState[]`。
- **可以 `await`，所以本节点兼当"延时节点"**（平台没有 delay / wait / sleep 节点）。轮询异步任务时用它隔开两次查询：

  ```javascript
  const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
  await sleep(<毫秒>);
  return 'waited';
  ```

  ⚠️ **不要用 `Atomics.wait`**：它同步阻塞，会拖停整个实例上所有用户的流程。`await sleep()` 只挂起当前流程。
  完整的轮询环（sleep → 查询 → Condition → Loop 回跳 sleep）和四条硬规则见 `nodes-linkfox-custom.md` 的"异步任务接口：必须自己搭轮询循环"。
- **`inputParams` 整个字段别写**：CustomFunction 的 `inputParams`（含 `customFunctionInputVariables[].variableValue` 与 `customFunctionUpdateState` 的 `acceptVariable` / `acceptNodeOutputAsVariable`）由 `save_workflow.py` 代填。写成 `[]` 不算省略、会报 error。
- 输出锚点：`<id>-output-customFunctionAgentflow`；函数返回值位于 `{{ <id>.output.content }}`。若返回对象，linkfox-workflow 系统会将其 JSON 序列化为字符串——**下游没法按字段取**，要字段只能先经 `customFunctionUpdateState` 写进 state。需要按字段取值时改用 CustomPythonFunction。
- **执行位置**：本节点在沙箱里执行，当前部署走远程沙箱（`E2B_SANDBOX_NODES` 点名了 `customFunctionAgentflow`），单次执行上限**默认 30 分钟**（部署配置 `E2B_SANDBOX_TIMEOUT`，部署可调）。所以 `await sleep()` 按毫秒写即可，`sleep(300000)` 也不会超时。不过等待期间这条执行一直挂着，轮询间隔仍按 10–30 秒写；单个 sleep 建议不超过 5 分钟，再长的等待先问用户是否真要同步等。沙箱里的 `$flow.state` 是值拷贝，执行完只写回**改过的键**，`delete $flow.state.x` 不生效。

### 沙箱环境变量（两个代码节点通用规则）

`CustomFunction` 用 `customFunctionEnvVariables`、`CustomPythonFunction` 用 `customPythonFunctionEnvVariables`，各有一个字段、不共用。规则一致：

- 每项 `{variableName, variableValue}`；名字 `^[A-Za-z_][A-Za-z0-9_]*$`、≤128 字符、不重名、≤32 条；值只能是文本 / 数字 / 布尔（对象和数组会被拒）、≤8192 字符。
- **保留名不能碰**：`PATH` / `HOME` / `PYTHONPATH` / `PYTHONHOME` / `PYTHONSTARTUP` / `NODE_PATH` / `NODE_OPTIONS` / `LD_PRELOAD` / `LD_LIBRARY_PATH`——pip / npm 安装、解释器启动、动态库加载都读它们。
- **内置运行时 key**：`{{$vars.LINKFOX_AGENT_API_KEY}}`（推荐）/ `{{$vars.LINKFOXAGENT_API_KEY}}`（旧名，同一把 key）。按当前工作流属主在运行时取，每次执行取一次，可以嵌在文本里（如 `Bearer {{$vars.LINKFOX_AGENT_API_KEY}}`）；取不到就报错，不降级成空串。
  **只在这两个字段里解析**——写进 Prompt / HTTP Body / 别的 `acceptVariable` 字段不会被替换，会原样留给用户看。这层作用域就是安全边界。
- **绑定的值明文落在编排 JSON 里**，所以密钥一律用 `{{$vars.X}}` 引用，禁止手填；也不要让用户去页面上绑沙箱凭据。`save_workflow.py` 对「名字像密钥（含 KEY / TOKEN / SECRET / PASSWORD / AUTH / CREDENTIAL）却填了字面量」直接报 **error** 拒绝落盘；它本来就不是密钥的（如 `TOKEN_TTL=3600` 这类配置数值）换个名字即可。
- 值是「只发点名的那几条」：工作区全局变量、部署环境变量都不会整包下发。

## CustomPythonFunction（自定义 Python 函数）

LinkFox 分支新增的节点，**在沙箱里执行一段 Python**，没有本地回落。

- `data.name`: `customPythonFunctionAgentflow`；`data.type`: `CustomPythonFunction`；`version`: `1.0`；`color`: `#4B8BBE`；`baseClasses`: `["CustomPythonFunction"]`。
- **没有 credential 字段**：沙箱由部署方统一配置，不要写 `credential`，也不要在补配置指引里让用户去绑凭据。
- `inputs`：

  | 字段 | 类型 | 说明 |
  | --- | --- | --- |
  | `customPythonFunctionCode` | code，必填 | Python 代码。**把结果赋值给 `result`** |
  | `customPythonFunctionLibraries` | string，可选 | 要 pip 安装的包，逗号分隔。模板预装的直接 `import`，**不用填**；白名单外的包会报错 |
  | `customPythonFunctionInputVariables[]` | array，可选 | 每项 `{variableName, variableValue}`，`variableValue` 可用 `{{ }}`；每项成为**同名 Python 变量**（裸名字，不带 `$`） |
  | `customPythonFunctionEnvVariables[]` | array，可选 | 每项 `{variableName, variableValue}`，执行时注入 `os.environ`；规则见上方「沙箱环境变量」 |
  | `customPythonFunctionTimeout` | number，可选 | **实际不生效**：部署配置的 `E2B_SANDBOX_TIMEOUT`（默认 30 分钟）优先于节点值，填多少都被它覆盖。留空即可 |
  | `customPythonFunctionUpdateState[]` | array，可选 | 同其它节点的 `UpdateState`，`{{ output.<字段> }}` 指本节点的 `result`（不用写 `.result`），保留原类型 |

- **`inputParams` 整个字段别写**：由 `save_workflow.py` 代填。
- 输出锚点：`<id>-output-customPythonFunctionAgentflow`。

### 写代码的四条约定（照 JS 习惯写必错）

1. **结果赋值给 `result`**，不是 `return`。顶格写 `return` 是 SyntaxError（`save_workflow.py` 报 error）；没赋值不报错，输出是空串（warning）。
2. **`print()` 是日志，不是返回值**，进 `output.logs`。本节点是最后一个节点时 `print` 会实时推给用户，调试信息别 `print`。
3. **`flow` 是 dict**：`flow["input"]` / `flow["state"]` / `flow["chatflowId"]` / `flow["sessionId"]` / `flow["chatId"]`。**没有** `$vars`、`chatHistory`、`$tools`；要全局变量就在 Input Variables 里写 `{{$vars.<变量名>}}` 显式传进来。改 `flow["state"]["<键>"]` 执行完会写回流程状态。
4. **输入变量名**必须是合法 Python 标识符，不能是关键字、不能以 `__` 开头、**不能叫 `flow` / `result`**，否则被拒（`save_workflow.py` 报 error）。变量值进来是**字符串**——上游传的是 JSON 时先 `json.loads`。

```python
import json
rows = json.loads(table_json)            # Input Variables: table_json = {{ dataReaderAgentflow_0.output.tableData }}
top = sorted(rows["rows"], key=lambda r: -float(r["<字段名>"] or 0))[:<Number>]
print("rows:", len(rows["rows"]))        # 只进 logs
result = {"count": len(top), "items": [r["<字段名>"] for r in top]}
```

### 输出与下游取值

| 字段 | 类型 | 内容 |
| --- | --- | --- |
| `output.content` | 字符串 | `result` 转成的文本（dict/list → 缩进 JSON；`None`/未赋值 → `""`）。**`{{<id>}}` 默认取它** |
| `output.result` | 原类型 | `result` 原样（未赋值为 `null`）。**按字段取值走这里** |
| `output.logs` | 字符串 | `print()` 输出 |
| `output.stderr` | 字符串 | stderr，**不视为失败**（pip、库的弃用告警都写这里） |

```text
{{customPythonFunctionAgentflow_0.output.result.count}}          → <Number>
{{customPythonFunctionAgentflow_0.output.result.items[0]}}       → 列表下标
{{customPythonFunctionAgentflow_0.output.result.items}}          → 对象插入时变成 JSON 文本
```

**不要写 `output.content.<字段>`**：`content` 是字符串，运行时不报错也不替换，用户看到字面量。`save_workflow.py` 会报 error 并给出 `output.result.<字段>` 的改法。

### 预装库（直接 `import`，Libraries 不用填）

- 基础：`requests` / `httpx` / `aiohttp` / `numpy` / `pandas` / `scipy` / `matplotlib` / `plotly` / `seaborn` / `scikit-learn` / `beautifulsoup4`(`bs4`) / `lxml` / `html5lib` / `chardet` / `pillow`(`PIL`) / `python-dateutil` / `pytz` / `pyyaml` / `regex` / `tabulate`
- 表格：`openpyxl` / `xlrd` / `xlsxwriter` / `pyarrow`
- 文档：`pypdf` / `pdfplumber` / `reportlab` / `pypdfium2` / `python-docx`(`docx`) / `mammoth` / `python-pptx`(`pptx`)

清单外的包要部署方先放行才装得上，而且每次执行现装、多等几秒到几十秒。**生成时不要往 Libraries 里写清单外的包**，确实需要就在方案里点明"需部署方放行 <包名>"。

### 代价与限制（方案里要讲）

- **每次执行新建沙箱，要多等几秒启动**，多个 Python 节点叠加。别把它放进高频轮询环当延时用——延时仍用 JS CustomFunction 的 `await sleep()`。
- **数据出境**：代码、输入变量的值、环境变量的值都会发到外部沙箱执行。用户说数据不能出境时不要用。
- **单次执行上限默认 30 分钟**（同上，由部署配置 `E2B_SANDBOX_TIMEOUT` 决定，不是无限）。
- 沙箱里生成的文件（`report.docx`、PDF）**执行完即销毁**，节点只能把结果以 `result` 交出去（如 base64 或文本）；要"导出文件给用户"仍然没有落地通道（见 prompt-compiler 的 `capability-gaps.md` §5.2）。
- 沙箱能访问公网，但**不是** Linkfox 网关：调 Linkfox 工具仍用 `LinkfoxHTTP`，不要在 Python 里拿 `requests` 去打 `tool-gateway.linkfox.com`（没有认证头）。

## ExecuteFlow

- `data.name`: `executeFlowAgentflow`；`data.type`: `ExecuteFlow`；`version`: `2.0`；`color`: `#a3b18a`；面板名「执行工作流」。
- 调用另一条工作流，把子工作流的回复作为本节点输出继续往下走。请求经 Linkfox 工具网关 → workflow-studio 转发，以凭据所属成员的身份执行。
- `inputs` 字段：

  | 字段 | name | 必填 | 说明 |
  |---|---|---|---|
  | 选择工作流 | `executeFlowSelectedFlow` | 是 | `asyncOptions`，目标 flow 的 id。生成时留 `""`，由用户在界面里选 |
  | 输入 | `executeFlowInput` | 是 | 作为子工作流的 `question`，`acceptVariable: true`。默认 `{{ question }}`，见下方「输入怎么写」 |
  | 覆盖配置 | `executeFlowOverrideConfig` | 否 | type `json`，必须是合法 JSON，透传为子工作流的 `overrideConfig` |
  | 返回消息角色 | `executeFlowReturnResponseAs` | 是 | `userMessage`（默认）/ `assistantMessage`，子工作流回复以哪种角色进入后续上下文 |
  | 更新流程状态 | `executeFlowUpdateState` | 否 | `{key, value}[]`，把结果写回 `$flow.state` |

- **凭据**：`data.credential` 收 `linkfoxAgentApi`，必填，与 LinkfoxHTTP 等节点共用同一份凭据。生成时留 `""`，不写类型名，上传后由后台自动绑定，补配置指引里不提示绑凭据（规则同 `nodes-linkfox-custom.md`）。补配置只点名「选择工作流」。没有 Base URL 字段，地址取凭据里的 `baseUrl`；不要写 `executeFlowBaseURL`，也不要写 `chatflowApi` 凭据（`save_workflow.py` 对 `executeFlowBaseURL` 报 warning）。
- **输入怎么写**：开始节点是 BusinessStart 时 `question` 通常为空（手动启动恒为 `""`），默认的 `{{ question }}` 会把空串传给子工作流。要给子工作流传数据时，显式引用上游节点输出，如 `{{ llmAgentflow_0.output.content }}`。
- **`inputParams` 要自己写完整**（本节点不在脚本代填范围内）：`executeFlowInput` / `executeFlowOverrideConfig` / `executeFlowUpdateState` 需要 `acceptVariable: true` 才能正确替换变量。详见 `variable-substitution.md`。
- 输出：`output.content` 是子工作流回复文本；输出锚点 `<id>-output-executeFlowAgentflow`。
- **可选的目标范围**：只能调凭据所属成员可见的工作流——普通成员只能调自己的，组 owner 能调全组的。用户说"调同事那条流程"时如实说明可能选不到。
- **积分扣两次**：子工作流按一次独立执行计费，父工作流照常计费；余额不足时节点报 `Execute Flow: 积分不足，请充值`。生成计划里要提醒用户这一点。
- **禁止调自身**（报 `Cannot call the same agentflow!`）。A → B → A 这类环运行时不拦，嵌套无深度限制，生成时要自己避免；要重复执行用 Loop / Iteration。
- 子工作流的消息挂在父工作流同一个会话下。

## DirectReply

- `data.name`: `directReplyAgentflow`；`data.type`: `DirectReply`；`version`: `1.0`；`color`: `#4DDBBB`；`hideOutput: true`。
- 直接把 `directReplyMessage`（可用 `{{ }}`）回复用户，终止当前分支。
- **`inputParams` 要自己写完整**（本节点不在脚本代填范围内）：`directReplyMessage` 需要 `acceptVariable: true` 才能正确替换变量。详见 `variable-substitution.md`。
- 内部消息值位于 `{{ <id>.output.content }}`，但没有 output anchor；禁止接后续 edge。

## 选择规则

**代码节点默认用 JS 的 CustomFunction**。两者都能实现时一律选 JS：少一次沙箱冷启动、少一个节点类型要用户读懂。只有下面三种情况才换 CustomPythonFunction：

1. 下游要**按字段取**结果（写多维表的多列、Condition 判某个字段、通知里拼几个数）——JS 的输出是 JSON 字符串，取不了字段。引用 `output.result.<字段>`。
2. 要用标准库以外的包：pandas 做表格统计、bs4 / lxml 解析 HTML、pdfplumber / python-docx / openpyxl / python-pptx 读文档。**普通的排序、去重、过滤、求和、拼接 JS 都能做，不算这一条。**
3. 用户明确说"用 Python"。这时在节点 `description` 里写「用户指定用 Python」。

其余选型：

- 调第三方 API / webhook → HTTP。
- 拼接 / 截断 / 格式转换 / 排序去重 / 简单计算，结果整体往下传 → CustomFunction（JS）。
- **延时 / 轮询环里的 sleep** → CustomFunction（JS），单个 sleep 建议 ≤ 5 分钟（上限默认 30 分钟，但没人真会同步等那么久）。
- 用户说"数据不能出境" → 两个都在外部沙箱执行，如实说明。

`save_workflow.py` 对三条都不满足的 Python 节点给 warning（没 import 第三方包、下游和自己的 UpdateState 都没按字段取 `result`、description 里没有「用户指定用 Python」），看到就改成 CustomFunction。
- 调用已存在的另一条 flow → ExecuteFlow。
- 面向用户的末端回复 → DirectReply。
