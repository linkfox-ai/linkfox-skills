---
name: linkfox-wb-smart-table
display_name: LinkFox 多维表格
display_name_en: LinkFox Smart Table
description: 通过 LinkFox 多维表格管理团队数据表、记录、附件、AI 图片任务和表格自动化关联。
description_zh: 当用户需要查找或共享多维表、创建表与字段、筛选或维护记录、保存图片、生成 AI 图片，或管理多维表与工作流的关联时使用。支持读取、结构变更、记录写入、附件与 AI 任务、自动化关联查询和维护，并按操作返回表结构、记录结果、图片地址或任务状态；不负责创建工作流本身或操作飞书多维表格。
description_en: Use when users need to manage LinkFox team tables, fields, records, attachments, AI image generation, or table-to-workflow associations. It supports table discovery and creation, filtered reads, record and field changes, image attachments, asynchronous AI image tasks, and workflow association management, returning the relevant table, record, attachment, or task results. It does not create workflows or operate Lark Base.
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

# LinkFox 多维表格（LinkFox Smart Table）

为用户管理 LinkFox 团队多维表中的表结构、业务记录、图片附件、AI 出图任务和自动化关联。用户提出表格查询或维护、数据整理回写、图片归档、批量出图或自动化触发表排查时使用；根据请求返回表清单、字段定义、筛选结果、写入结果、附件查看地址或工作流关联状态。能力覆盖子能力标识 `linkfox-smart-table` 下的 18 个 operation，全部通过 LinkFox MCP 的 `proxy_call` 调用。完整参数、响应字段和业务限制见 [references/linkfox-smart-table.md](references/linkfox-smart-table.md)。

## 能力边界

### 能力范围

- **发现和创建表**：按当前团队权限读取自己创建或共享给自己的多维表，分别调用 `smartTable/listMyTables` 和 `smartTable/listSharedTables`；新建多维表与首张数据表调用 `smartTable/createTable`，在已有多维表下加数据表调用 `smartTable/addTable`。`linkfox-smart-table` 的表清单、两层容器结构和 ID 区分规则见 reference。
- **读取及维护字段**：用 `smartTable/listFields` 读取字段名、类型、选项和计算字段标记；用 `smartTable/addFields` 追加字段，或用 `smartTable/deleteFields` 删除整列。字段增删前先核对表头；删除整列会连同列数据删除。
- **筛选和维护记录**：`smartTable/listRecords` 支持字段投影、分页和类型化筛选；`smartTable/createRecords` 新增记录，`smartTable/updateRecords` 部分更新已有记录，`smartTable/deleteRecords` 按记录 ID 删除。写入字段须使用真实字段名，按返回条数核对结果。
- **记录图片附件**：对附件类型字段调用 `smartTable/uploadAttachment` 追加公网可访问的图片 URL；读取临时图片地址用 `smartTable/listRecords`。图片外链字段与附件字段是不同类型；MCP 请求只传 endpoint 支持的业务参数。
- **AI 图片字段与任务**：在创建或追加附件字段时配置 `ai`，使用 `smartTable/fillAiField` 发起异步填充，并用 `smartTable/getAiFillStatus` 查询任务。AI 出图会消耗调用方积分；覆盖已有图前必须明确告知用户并确认。
- **工作流关联管理**：`smartTable/registerWorkflow` 登记已存在的工作流，`smartTable/listWorkflows` 查看关联，`smartTable/updateWorkflowTriggerTable` 更换或清空触发表，`smartTable/unregisterWorkflow` 解除关联。工作流定义、节点、名称和启停状态须在工作流侧处理。

### 边界与限制

- 数据访问只覆盖当前 LinkFox 用户可见且有权限的团队表；请求参数不能指定其他用户、团队或 base。`notebookId` 是多维表容器 ID，`tableId` 是数据表 ID，`recordId` 是记录 ID，`flowId` 是工作流侧 ID；只使用已返回或由用户/工作流侧提供的 ID。
- 不能通过这些 operation 改字段名、改字段类型、调整字段顺序、删除或重命名表；复杂字段如关联、公式、汇总、成员和系统字段也不能通过创建字段接口建立。需要这些操作时请用户在表格页面处理。
- 不提供视图、仪表盘、跨团队访问、复杂嵌套筛选、指定排序、整表清空、恢复已删除数据、附件删除或排序能力。按行号定位不可靠，应按字段值筛选后使用 `recordId`。
- 不能创建、编辑或删除工作流本身，也不能提供工作流名称、节点或运行记录；只管理多维表侧的关联。`tableId` 触发器必须在关联所属多维表内。
- 不适用于飞书/Lark 多维表格，也不负责把表格数据制作成网页或看板。
- 不请求或暴露任何凭证。WorkBuddy 自动注入授权；MCP 不可用时停止并提示安装或重载 LinkFox 连接器，不得走旧 HTTP 网关或本地直连脚本。

## 工具选择指南

先确定用户要处理的是表、字段、记录、附件/AI 任务还是工作流关联，再用下表选择最贴近问题的 operation。改数据前尽量先读当前状态；用户意图模糊或同名对象有多个候选时，展示候选并请用户选择。

| 需求 / 用户说 | 默认推荐 | 何时换用其他 |
|---|---|---|
| “找我的表 / 哪个多维表里有这张表” | `smartTable/listMyTables` | 别人共享给我的表使用 `smartTable/listSharedTables`；两者都查找不到再告知结果为空，不要猜 ID |
| “建一个多维表 / 在项目里再加张数据表” | 从零开始用 `smartTable/createTable` | 已有 `notebookId` 时用 `smartTable/addTable`；往现有表加列则用 `smartTable/addFields` |
| “表头有哪些列 / 写入前确认字段” | `smartTable/listFields` | 只需要记录数据时用 `smartTable/listRecords`；不能从有值记录反推完整表头 |
| “筛出符合条件的行 / 看几列数据” | `smartTable/listRecords` | 条件用 `filter.conditions`，关键词在文本列用 `contains`；不要用不支持的 `search` 或行号定位 |
| “往表里新增结果 / 修改某行某个值” | 新行用 `smartTable/createRecords` | 已有行用 `smartTable/updateRecords`；更新前先筛选唯一命中记录，不能用新增接口模拟更新 |
| “删掉记录 / 删除某些列” | 行用 `smartTable/deleteRecords` | 列用 `smartTable/deleteFields`；两者都要先展示目标对象并取得明确确认，删除不可逆 |
| “给附件列放一张图片 / 查看表格图片” | 写入用 `smartTable/uploadAttachment` | 读取附件查看地址用 `smartTable/listRecords`；`image` 类型的外链列直接写 URL 到记录字段 |
| “用 AI 批量生成图片 / 查看生成进度” | 先确保附件列已配置 AI，再用 `smartTable/fillAiField` | 查异步进度用 `smartTable/getAiFillStatus`；已有图片默认跳过，`mode=all` 会覆盖，必须确认并说明积分消耗 |
| “把自动化挂到表 / 自动化没触发 / 换触发表” | 查询用 `smartTable/listWorkflows` | 新建关联用 `smartTable/registerWorkflow`；换表或停触发用 `smartTable/updateWorkflowTriggerTable`；彻底解除关联用 `smartTable/unregisterWorkflow` |

### 工具选择思路

- 表名定位按层遍历 `notebooks[].tables[]` 和 `looseTables.tables[]`；若命中多个同名表，列出容器名、表名、创建时间和可用链接，让用户选择。
- 写记录前先 `listFields` 确认字段类型和单选/多选选项。改记录前 `listRecords` 筛选并确认唯一命中，随后只传要改的字段；新增记录与更新已有记录不可混用。
- 选择 `image` 还是 `attachment` 时，外链字符串用 `image`；需把文件存入表格附件并查看临时签名 URL 时用 `attachment`。AI 出图列必须是 `attachment` 类型。
- 自动化不触发时先 `listWorkflows` 检查 `tableId` 是否为 `null`。清空触发表表示停止记录变更触发但保留关联；解除关联会从多维表移除该流，二者后果不同。

## 业务需求路由速查

路由表逐项列出 18 个 operation。endpoint 是原 API 路径，`toolName` 使用去掉前导 `/` 后的精确值。

| 子能力 | 业务能力 | reference | 原 endpoint | 精确 toolName |
|---|---|---|---|---|
| `linkfox-smart-table` | 列出我创建的表 | `references/linkfox-smart-table.md#listmytables` | `/smartTable/listMyTables` | `smartTable/listMyTables` |
| `linkfox-smart-table` | 列出共享给我的表 | `references/linkfox-smart-table.md#listsharedtables` | `/smartTable/listSharedTables` | `smartTable/listSharedTables` |
| `linkfox-smart-table` | 新建多维表与首张数据表 | `references/linkfox-smart-table.md#createtable` | `/smartTable/createTable` | `smartTable/createTable` |
| `linkfox-smart-table` | 在现有多维表内加数据表 | `references/linkfox-smart-table.md#addtable` | `/smartTable/addTable` | `smartTable/addTable` |
| `linkfox-smart-table` | 读取字段结构 | `references/linkfox-smart-table.md#listfields` | `/smartTable/listFields` | `smartTable/listFields` |
| `linkfox-smart-table` | 追加字段 | `references/linkfox-smart-table.md#addfields` | `/smartTable/addFields` | `smartTable/addFields` |
| `linkfox-smart-table` | 删除字段 | `references/linkfox-smart-table.md#deletefields` | `/smartTable/deleteFields` | `smartTable/deleteFields` |
| `linkfox-smart-table` | 筛选与读取记录 | `references/linkfox-smart-table.md#listrecords` | `/smartTable/listRecords` | `smartTable/listRecords` |
| `linkfox-smart-table` | 新增记录 | `references/linkfox-smart-table.md#createrecords` | `/smartTable/createRecords` | `smartTable/createRecords` |
| `linkfox-smart-table` | 更新已有记录 | `references/linkfox-smart-table.md#updaterecords` | `/smartTable/updateRecords` | `smartTable/updateRecords` |
| `linkfox-smart-table` | 删除记录 | `references/linkfox-smart-table.md#deleterecords` | `/smartTable/deleteRecords` | `smartTable/deleteRecords` |
| `linkfox-smart-table` | 追加附件图片 | `references/linkfox-smart-table.md#uploadattachment` | `/smartTable/uploadAttachment` | `smartTable/uploadAttachment` |
| `linkfox-smart-table` | 触发 AI 字段生成 | `references/linkfox-smart-table.md#fillaifield` | `/smartTable/fillAiField` | `smartTable/fillAiField` |
| `linkfox-smart-table` | 查询 AI 任务状态 | `references/linkfox-smart-table.md#getaifillstatus` | `/smartTable/getAiFillStatus` | `smartTable/getAiFillStatus` |
| `linkfox-smart-table` | 登记工作流关联 | `references/linkfox-smart-table.md#registerworkflow` | `/smartTable/registerWorkflow` | `smartTable/registerWorkflow` |
| `linkfox-smart-table` | 列出工作流关联 | `references/linkfox-smart-table.md#listworkflows` | `/smartTable/listWorkflows` | `smartTable/listWorkflows` |
| `linkfox-smart-table` | 修改或清空触发表 | `references/linkfox-smart-table.md#updateworkflowtriggertable` | `/smartTable/updateWorkflowTriggerTable` | `smartTable/updateWorkflowTriggerTable` |
| `linkfox-smart-table` | 解除工作流关联 | `references/linkfox-smart-table.md#unregisterworkflow` | `/smartTable/unregisterWorkflow` | `smartTable/unregisterWorkflow` |

## MCP 调用方式

- 只使用 MCP server `LinkFox` 的 `proxy_call`，调用形式为 `LinkFox.proxy_call`，参数结构为 `{"toolName":"smartTable/<Operation>","arguments":{...}}`。`toolName` 区分大小写，不能包含前导 `/`、展示名或自造别名。
- 原请求对象直接放入 `arguments`。不增加 `body`、`params`、`data` 或第二层 `arguments`；无业务参数时传 `{}`。WorkBuddy 自动注入 Linkfox Authorization，arguments 不得带 headers、Authorization、API Key、token、JWT、手机号或身份字段。
- 先处理 MCP 连接、schema 和 `isError`，再读取 structured content；text JSON 只解析一次。之后再检查业务 `errcode`、`errorCode`、`code`、`success`、`status` 及消息字段。不得只凭 HTTP 状态或 MCP 外层成功判断业务成功。
- 收费操作（尤其 AI 出图）在同一任务中不要重复提交相同 `toolName + arguments`。异步 AI 任务只按需每 30–60 秒查询；不连续轮询。写操作超时或响应不明确时先读状态核验，确认未生效后再决定是否重试。`addTable` 没有幂等键，重试前先查表是否已创建。
- 删除字段、删除记录和解除工作流关联不可逆；执行前读取并向用户复述具体对象、影响范围，取得明确确认。`updateWorkflowTriggerTable` 的 `tableId: null` 会停止该流的记录触发，调用前也须确认。
- 若 LinkFox MCP 或 `proxy_call` 缺失、连接失败或 schema 不匹配，停止业务调用并提示安装或重载 LinkFox 连接器。禁止回退 curl、HTTP 客户端、旧脚本或其他网关调用。
- 完整参数、响应字段、算子和错误说明在 `references/linkfox-smart-table.md`。本能力没有需保留的本地 helper。

## 使用示例

以下示例中的 ID、字段名和图片地址均为占位值。调用前应先阅读对应 reference，并用实际 MCP 响应确认 ID 与字段名。

### 1. 查找表并读取字段

```json
{"toolName":"smartTable/listMyTables","arguments":{"page":1,"perPage":100}}
```

若表在共享列表中，则改用 `smartTable/listSharedTables`，arguments 同为 `{"page":1,"perPage":100}`。遍历 notebook 和散表两处寻找 tableId；有重名时让用户挑选。选定 `tableId` 后读取表头：

```json
{"toolName":"smartTable/listFields","arguments":{"tableId":"tblXXXXXXXX","includeChoices":true}}
```

出参 `fields[]` 包含字段名、类型、选择项和计算字段标记。写入时必须用 `name`，不要用 `fieldId`；读取列表本身通常不涉及 AI 积分。

### 2. 筛选记录

```json
{
  "toolName":"smartTable/listRecords",
  "arguments":{
    "tableId":"tblXXXXXXXX",
    "fieldNames":["商品标题","价格","状态"],
    "perPage":50,
    "filter":{"conjunction":"and","conditions":[
      {"fieldName":"商品标题","operator":"contains","value":"充电器"},
      {"fieldName":"价格","operator":"isGreaterEqual","value":100}
    ]}
  }
}
```

`total` 是筛选后总行数，空单元格字段可能完全不出现。大量结果应先缩小筛选范围并只取需要的列；过滤字段名和算子必须匹配字段类型。

### 3. 新增记录或更新已有记录

新增示例：

```json
{"toolName":"smartTable/createRecords","arguments":{"tableId":"tblXXXXXXXX","records":[{"fields":{"商品标题":"无线充电器","价格":"25.99","状态":"待评估"}}],"typecast":true}}
```

更新示例：

```json
{"toolName":"smartTable/updateRecords","arguments":{"tableId":"tblXXXXXXXX","records":[{"recordId":"recAAAAAAAA","fields":{"状态":"已完成"}}],"typecast":true}}
```

新增出参中的 `recordId` 留作后续更新、删除或上传附件使用。更新前通过筛选确认目标唯一，更新只传要改的字段；清空单元格传 `null`。核对 `created` 或 `updated` 与请求条数，避免把静默跳过的记录报告为成功。

### 4. 上传附件图片

```json
{"toolName":"smartTable/uploadAttachment","arguments":{"tableId":"tblXXXXXXXX","recordId":"recAAAAAAAA","fieldName":"商品图","imageUrl":"https://example.com/product.jpg"}}
```

列类型必须为 `attachment`，记录须已存在。一次追加一张、同一格多图须串行调用；图片须公网可访问且不超过 20 MB。响应中的 `presignedUrl` 是临时查看地址，约三小时后失效。若字段是 `image` 类型，应直接将外链作为记录字段值写入。

### 5. AI 出图和状态查询

确保 AI 附件列、提示词、参考字段和参考图片均已配置后再触发。调用前提醒用户积分消耗并取得其继续意愿：

```json
{"toolName":"smartTable/fillAiField","arguments":{"tableId":"tblXXXXXXXX","fieldName":"AI 场景图","recordIds":["recAAAAAAAA"],"mode":"emptyOnly"}}
```

随后按需查询：

```json
{"toolName":"smartTable/getAiFillStatus","arguments":{"tableId":"tblXXXXXXXX","taskId":"tskXXXXXXXX"}}
```

`emptyOnly` 默认只填空格；`all` 会整格覆盖已有附件，必须事先确认。任务异步且单行最长约 10 分钟；出图失败时检查参考图和提示词引用字段是否为空。完成后用 `listRecords` 获取结果，避免频繁轮询。

### 6. 工作流关联

登记一条已在工作流侧创建的流：

```json
{"toolName":"smartTable/registerWorkflow","arguments":{"notebookId":"nbkXXXXXXXX","flowId":"workflow-id","tableId":"tblXXXXXXXX"}}
```

查看当前触发器时调用 `smartTable/listWorkflows`，可传 `{"notebookId":"nbkXXXXXXXX"}`。若返回 `tableId: null`，明确说明它不会因记录变化触发。解绑触发表要调用 `smartTable/updateWorkflowTriggerTable` 并显式传 `"tableId":null`，这会停止触发但保留关联；解除整个关联则使用 `smartTable/unregisterWorkflow`，先确认该动作。

## 展示规则

1. **表清单**：按多维表容器分组展示其下的数据表；`looseTables.tables[]` 单独列出。表名重复时给出容器名、创建时间和服务端实际返回的链接，缺失 URL 时不要自行拼接。
2. **字段结构**：列出字段名、类型和可选项；标注 `isComputed` 字段不可写。始终区分 `fieldId` 与用于读写的字段名。
3. **记录查询**：少量结果用表格呈现；大量数据报告筛选后的 `total`、字段名和少量样本，再按用户关注点继续读取。说明空白单元格可能未在 `fields` 对象中出现，且结果顺序是创建顺序，不保证与页面视图一致。
4. **写入结果**：明确新增、更新或删除的实际条数以及目标表；比对 `created`、`updated`、`deleted` 与请求条数。若数量不符，先读取实际状态并说明差异，不把部分成功表述为全部成功。
5. **附件与 AI**：展示附件所在表、记录和字段；临时 `presignedUrl` 标明有效期。AI 任务显示状态、成功/失败/待处理数量和失败原因；积分消耗和覆盖风险在调用前说明。
6. **工作流关联**：只说 `flowId`，不编造工作流名称；`tableId: null` 明确标注为未设置触发表且不会被触发。`updateWorkflowTriggerTable` 返回 `status: not_found` 表示未修改，不能报成功。
7. **错误与限制**：尽可能保留并转述下游 `errmsg` 原文，说明是否已产生变更，并提供可执行的字段名、ID、类型或权限修正建议。不可用字段要明确指出，数据来源标注为 LinkFox 多维表 API 实时响应。

## 解决认证和积分问题

WorkBuddy 自动注入 Authorization。不得索取、展示、配置或传递任何 API Key、token、JWT、手机号或 Authorization Header。

1. **MCP 或 `proxy_call` 缺失**：停止请求，提示用户在 WorkBuddy 左侧“专家·技能·连接器”中安装或重载 LinkFox 连接器，然后重试。不得调用旧脚本或 HTTP 网关。
2. **MCP 连接 401**：这是 MCP 连接认证层异常，提示用户检查 LinkFox 连接器登录状态并重新连接；不要将它误当成多维表的下游业务错误。
3. **代理成功、下游 401**：下游身份未建立或用户身份不可用。停止本次操作，读取 `references/onboarding.md` 引导用户检查 WorkBuddy 的 LinkFox 连接器授权并重新加载会话；不得要求用户提供凭证。
4. **下游 402 或余额不足**：停止收费操作，读取 `references/onboarding.md` 说明积分不足的处理入口。告知用户可能产生费用，是否补充积分或继续由用户决定；不要自动重试或换模型重跑。
5. **下游 403**：按权限问题处理，说明当前用户无权执行该表、字段或工作流操作。请用户确认团队/共享权限，不进入认证或充值引导。
6. **其他业务错误**：按下游 `errcode`、`errorCode`、`code`、`success`、`status` 和消息字段处理，转述原始错误并说明本次是否有改动。对于写请求超时先读取当前状态，不能盲目重放。

## 积分消耗说明

> 用户会因积分消耗而支付费用。请充分评估：当需要高频调用本技能，或用户对积分消耗量预期不足时，务必提醒用户，由用户决定是否继续。
