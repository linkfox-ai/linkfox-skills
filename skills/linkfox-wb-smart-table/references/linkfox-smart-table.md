# LinkFox 多维表格 API reference

本 reference 归档 `linkfox-smart-table` 的业务契约。全部 operation 使用 `LinkFox.proxy_call`，arguments 直接传下列 JSON 请求对象。响应业务字段通常平铺在顶层，成功判断须检查 `errcode` 及 operation 特有的计数、状态字段。具体响应随数据情况省略空值。

## 公共概念和规则

### 18 个 operation 的精确 MCP 路由

原 endpoint 为下表“原 endpoint”列，传入 MCP 的值必须使用对应的 `toolName`，不能添加前导斜线或替换大小写。

| operation | 原 endpoint | toolName |
|---|---|---|
| `listMyTables` | `/smartTable/listMyTables` | `smartTable/listMyTables` |
| `listSharedTables` | `/smartTable/listSharedTables` | `smartTable/listSharedTables` |
| `createTable` | `/smartTable/createTable` | `smartTable/createTable` |
| `addTable` | `/smartTable/addTable` | `smartTable/addTable` |
| `listFields` | `/smartTable/listFields` | `smartTable/listFields` |
| `addFields` | `/smartTable/addFields` | `smartTable/addFields` |
| `deleteFields` | `/smartTable/deleteFields` | `smartTable/deleteFields` |
| `listRecords` | `/smartTable/listRecords` | `smartTable/listRecords` |
| `createRecords` | `/smartTable/createRecords` | `smartTable/createRecords` |
| `updateRecords` | `/smartTable/updateRecords` | `smartTable/updateRecords` |
| `deleteRecords` | `/smartTable/deleteRecords` | `smartTable/deleteRecords` |
| `uploadAttachment` | `/smartTable/uploadAttachment` | `smartTable/uploadAttachment` |
| `fillAiField` | `/smartTable/fillAiField` | `smartTable/fillAiField` |
| `getAiFillStatus` | `/smartTable/getAiFillStatus` | `smartTable/getAiFillStatus` |
| `registerWorkflow` | `/smartTable/registerWorkflow` | `smartTable/registerWorkflow` |
| `listWorkflows` | `/smartTable/listWorkflows` | `smartTable/listWorkflows` |
| `updateWorkflowTriggerTable` | `/smartTable/updateWorkflowTriggerTable` | `smartTable/updateWorkflowTriggerTable` |
| `unregisterWorkflow` | `/smartTable/unregisterWorkflow` | `smartTable/unregisterWorkflow` |

- ID 不可混用：`notebookId` 是多维表容器 ID（`nbk`），`tableId` 是数据表 ID（`tbl`），`recordId` 是记录 ID（`rec`），`flowId` 是工作流侧生成的 ID。所有 ID 必须来自接口结果或对应业务侧，不得猜测或拼造。
- 表名不保证唯一。找表须遍历 `notebooks[].tables[]` 和 `looseTables.tables[]`；同名多表须把候选交给用户选。`listMyTables` 和 `listSharedTables` 的分页针对 notebook 容器数，不针对其下的 tables。
- 字段写入始终按字段 `name`，保持大小写、空格和中英文原样；`fieldId` 仅是工作流触发配置可用的标识，不用于记录读写。写数据前先 `listFields`，不从记录值推导字段清单。
- 资源范围由 WorkBuddy 自动身份决定，仅限当前团队和当前用户有权访问的表。请求中不传 `baseId`、`teamId`、`userId` 等身份或内部字段。
- 普通读写不改变撤销栈。删除字段、删除记录没有本接口恢复方式；创建/追加表等请求遇超时应先查询实际状态再决定是否重试。
- 原脚本中的 `imagePath` 是本地文件上传辅助参数，不是业务 API 参数。本 MCP 调用仅接受 `imageUrl`；上传前应已有公网可访问的 HTTPS 图片地址。附件删除、替换和排序由用户在页面操作。

## 表和多维表

### listMyTables

列出当前团队里用户创建的多维表及其数据表。

```json
{"page":1,"perPage":100}
```

参数 `page` 为从 1 开始的页码；`perPage` 为 1–100，默认 100，限制 notebook 数。返回 `total`（notebook 总数）、`notebooks[]` 和可选 `looseTables`。Notebook 对象有 `notebookId`、`name`、可选 `url`、`createdTime`、`tables[]`；table 对象有 `tableId`、`name`、`refKey`、可选 `url`、`createdTime`。`refKey` 不是用于读写的 tableId。URL 缺失时不能自行拼接。自己创建的列表与共享列表不重叠。

### listSharedTables

列出共享给当前用户的表，参数、两层响应形状和分页语义同 `listMyTables`。无参数时传 `{}`。为空是正常结果。查询自己创建的表应调用 `listMyTables`。

### createTable

新建一个 notebook 容器和其中第一张数据表；不能指定已有 notebook，也不接受初始记录。

```json
{"name":"选品清单","fields":[{"name":"商品标题","type":"singleLineText"},{"name":"价格","type":"number"}],"requestKey":"optional-stable-key"}
```

- `name` 必填，1–255 字；`fields` 可选，最多 200 项，未提供时默认一列“名称”。字段顺序决定列顺序，第一列是主字段。
- 支持类型：`singleLineText`、`longText`、`number`、`singleSelect`、`multipleSelect`、`date`、`checkbox`、`rating`、`image`、`attachment`。`checkbox` 和 `attachment` 不能作为首列。单选/多选字段必须有非空 `choices` 对象数组，如 `[ {"name":"待处理"} ]`。`color` 为可选站点色名，不是 HEX 色值。
- `fields[].ai` 可为附件列设置 AI，规则见“AI 字段”。
- 可选 `requestKey` 为 1–200 字，适用于并发或超时重试的短时间幂等；不是长期唯一约束。相同 key 请求仍在进行时可能返回 409，应使用原 key 稍后再试。
- 返回 `notebookId`、实际容器名 `notebookName`、首表 `tableId`、`name`、`url`、`createdTime`、字段清单和可选 `idempotentHit`。以 `notebookName` 为实际容器名；`idempotentHit: true` 表示复用已有结果而未新建。
- `records` 和 `notebookId` 不受支持。500/503 后先用 `listMyTables` 查是否已创建。

### addTable

在已有 notebook 下新建一张数据表。`notebookId`、`name` 必填；可选 `fields` 最多 200 项，字段结构同 `createTable`。不接受 `records` 或 `requestKey`，没有幂等键。

```json
{"notebookId":"nbkXXXXXXXX","name":"竞品对比","fields":[{"name":"竞品名称","type":"singleLineText"}]}
```

返回 `tableId`、实际 `name`、`notebookId`、`refKey`、可选 `url`、`createdTime` 和字段列表。字段没给则默认一列“名称”。超时或 500/503 后先调 `listMyTables` 确认，直接重试可能重复建表。同名表可能重复，不能按名称当唯一键。`notebookId` 必须来自当前可见多维表，容器权限不足可能表现为 403/404。

## 字段结构

### listFields

查询完整字段定义，不分页。`tableId` 必填；`includeChoices` 可选，默认 `true`。

```json
{"tableId":"tblXXXXXXXX","includeChoices":true}
```

响应包含 `tableId`、`name`、`total`、`fields[]`。字段对象包含 `fieldId`、`name`、`type`，可选 `isPrimary`、`isComputed`、`isMultipleCellValue`、`choices`、`max`、`description`。布尔属性仅在为 true 时出现。隐藏字段也会返回。`includeChoices:false` 可缩小响应，但写单选/多选值前应读取选项。

`listFields` 可能返回接口不能新建的类型，例如 `link`、`user`、`createdBy`、`lastModifiedBy`、`formula`、`rollup`、`conditionalRollup`、`autoNumber`、`createdTime`、`lastModifiedTime` 和 `button`。`isComputed` 字段不能写入。`image` 的值是 URL 字符串；`attachment` 不能直接写 URL，须用 `uploadAttachment`。

### addFields

追加 1–50 个字段至表尾，不支持改名、改类型或调整顺序。调用前先 `listFields`，排除重名。

```json
{"tableId":"tblXXXXXXXX","fields":[{"name":"状态","type":"singleSelect","choices":[{"name":"待处理"},{"name":"完成"}]}]}
```

每项需 `name`（1–255 字）和 `type`；支持类型同 `createTable`。单选/多选必须给非空对象数组 `choices`；可带 `ai` 的仅限附件字段。任一字段无效或重名时整批失败，不会部分添加。返回 `added` 和添加后的完整 `fields`。

### deleteFields

按列名删除整列及其中数据。`tableId` 与非空 `fieldNames` 必填。此为不可逆物理删除，先查询字段、复述表名和将删列并取得明确确认，再调用。没有模拟确认字段或恢复接口。

```json
{"tableId":"tblXXXXXXXX","fieldNames":["旧备注","临时列"]}
```

字段名必须精确匹配，不能传 `fieldId`。返回 `deleted` 数量；发生错误时读取原始 `errmsg`。不要在确认之前调用。

## 记录读取和写入

### listRecords

分页读取记录，可投影字段并按字段类型筛选。`tableId` 必填；`page` 默认 1，`perPage` 默认 100 且最大 100；`fieldNames` 可选但若提供必须是非空数组；`cellFormat` 为 `json`（默认）或 `text`。

```json
{"tableId":"tblXXXXXXXX","fieldNames":["商品标题","价格"],"perPage":50,"filter":{"conjunction":"and","conditions":[{"fieldName":"商品标题","operator":"contains","value":"充电器"}]}}
```

`filter` 支持 1–20 个扁平条件和单一 `conjunction`（`and` 默认，也可 `or`），不支持嵌套。条件含 `fieldName`、`operator`，及依算子要求的 `value`。文本支持 `is`、`isNot`、`contains`、`doesNotContain`、`isEmpty`、`isNotEmpty`；数字/评分支持相等、不等、大于、大于等于、小于、小于等于及判空；单选支持相等、不等、`isAnyOf`、`isNoneOf` 及判空；多选支持 `hasAnyOf`、`hasAllOf`、`hasNoneOf`、`isExactly`、`isNotExactly` 及判空；checkbox 仅支持 `is`；日期支持 `is`、`isNot`、`isBefore`、`isAfter`、`isOnOrBefore`、`isOnOrAfter`、`isWithIn` 及判空。`isEmpty`/`isNotEmpty` 不传 value；集合算子传非空数组；其他算子传单值。日期值是日期对象格式，若需精确日期规则先参照源系统日期契约，不猜测时区结构。

响应含筛选后的 `total`、分页字段和 `records[]`（`recordId`、`fields`）。空单元格字段 key 会整个消失，不表示字段不存在。附件格在 JSON 格式下是附件对象数组，含 `token` 和临时 `presignedUrl`/缩略图 URL；签名地址最长约三小时，不可长期保存。

不支持 `search`、排序、`viewId`、`baseId` 或 `fieldId`。关键词查找使用文本字段 `contains`。修改或删除记录时按值精确筛选并检查 `total`；只有唯一命中才继续，不能用“第 N 行”。大表优先用 filter 收窄结果。返回的记录顺序是创建顺序，未必与用户视图一致。

### createRecords

往现有表新增记录。`tableId` 和非空 `records` 必填，每条包含非空 `fields` 对象；字段 key 是字段名，不接受 `recordId`。`typecast` 默认 true，可设置 false。

```json
{"tableId":"tblXXXXXXXX","records":[{"fields":{"商品标题":"无线充电器","价格":"25.99"}}],"typecast":true}
```

成功响应含 `created`、`records[]`（新生成 `recordId` 和字段）。比较 `created` 与输入数量；不一致时用 `listRecords` 核实。500/503 后先读状态以免写重。附件字段不能传裸 URL；新建记录后用 `uploadAttachment` 追加图片。`image` 类型字段可以直接传 URL。选项值须在 `listFields.choices` 中。

### updateRecords

部分更新已有行。`tableId` 与非空 `records` 必填；每项包含真实 `recordId` 和非空 `fields`，可选 `typecast` 默认 true。

```json
{"tableId":"tblXXXXXXXX","records":[{"recordId":"recAAAAAAAA","fields":{"状态":"已完成"}}],"typecast":true}
```

仅更新所传字段；未出现的字段原样保留。清空用 `null`，不要用空字符串；`notNull` 字段不允许清空。不可用于新增行。响应含 `updated` 和更新后记录；有不存在的 recordId 时可能返回成功但跳过该行，因此核对 `updated`。先 `listRecords` 定位，单格更新只传一项字段。附件列追加新图使用 `uploadAttachment`；通过 `{name, token}` 写入附件会整格替换。

### deleteRecords

按记录 ID 删除记录。`tableId` 和非空 `recordIds` 必填，ID 必须来自读取结果且不得重复。物理删除、不可逆、无恢复接口；整个批次全有全无。执行前读取目标记录，向用户复述表名、条数、主字段内容和不可逆影响，取得明确确认。

```json
{"tableId":"tblXXXXXXXX","recordIds":["recAAAAAAAA","recBBBBBBBB"]}
```

成功返回 `deleted`。缺少记录 ID 会导致整批失败，不要拆成单条绕过全有全无规则；大批量须分批且每批重新确认。超时后先查当前状态，不盲目重试。

## 图片附件和 AI

### uploadAttachment

给已存在记录的 `attachment` 类型单元格追加一张图片。必填 `tableId`、`recordId`、`fieldName`，并且 `imageUrl` 与本地辅助参数二选一。MCP 只支持业务 API 的 `imageUrl`，必须为公网可访问的 HTTP(S) 图片地址、图片类型且不超过 20 MB。

```json
{"tableId":"tblXXXXXXXX","recordId":"recAAAAAAAA","fieldName":"商品图","imageUrl":"https://example.com/a.jpg"}
```

先 `listFields` 确认字段为 attachment，并确认记录存在。一次追加一张；同一单元格的多张图必须串行上传，不能并发以免覆盖。响应含附件 `id`、`name`、`token`、`mimetype`、`size`、可选宽高和临时查看/缩略图 URL。`presignedUrl` 浏览器直接打开可能是下载，约三小时失效。接口只追加，不能删除、替换或排序附件；用户需到页面操作。`image` 字段不用此接口，直接写 URL 字符串。

### AI 字段配置

只能给 `attachment` 字段配置 `ai`。对象包含必填 `prompt` 与 `referenceFields`（1–9 个字段名数组），以及可选 `model`、`aspectRatio`、`resolution`。提示词可用 `{列名}` 插入同一行文本列；引用的列须存在且不能在对应行为空。参考图字段须为 `attachment` 或 `image`，图片应直接通过 `referenceFields` 指定，不要把附件列名插入提示词当图片输入。

可用模型与能力以当前系统配置为准，模型选项可能更新。已知参考能力包含 `GPT_2_5_IMAGE`（默认）、`GPT_2_5_F_IMAGE`、`GPT_2_IMAGE`、`GEMINI_NANO_BANANA_2_1`、`GEMINI_FLASH_PRO`、`GEMINI_31_FLASH_IMAGE`、`GEMINI_31_FLASH_LITE`、`SEEDREAM5_PRO`、`WAN2_7`、`AIDRAW_EDIT`。比例/分辨率须符合所选模型。配置接口不会自动生成图片；必须另行调用 `fillAiField`。字段引用错误可能导致整批加字段失败；若 AI 配置失败，先核实字段状态，避免重复添加。

### fillAiField

在已配置 AI 的附件字段发起异步生成。必填 `tableId`、`fieldName`；可选 `recordIds`（指定行最多 50 条）、`mode`（默认 `emptyOnly`；也可 `all`）。不传 recordIds 时对整表候选行处理，单次最多 100 行。

```json
{"tableId":"tblXXXXXXXX","fieldName":"AI 场景图","recordIds":["recAAAAAAAA"],"mode":"emptyOnly"}
```

**会消耗调用方积分**，触发前说明消耗风险并让用户决定是否继续。`emptyOnly` 只补空格，重复触发可避免重复生成；`all` 会整格覆盖已有图片，包括手工上传附件，必须清楚说明并获得用户明确确认。响应含 `taskId`、`rowCount`、`processedCount`、`isLimited` 和 `reused`；`taskId:null` 表示没有待生成行；`reused:true` 表示返回已有运行任务而未新入队。`isLimited:true` 表示仅部分入队，完成后按需继续。

### getAiFillStatus

用触发任务的原表查询进度。必填 `tableId` 和 `taskId`。

```json
{"tableId":"tblXXXXXXXX","taskId":"tskXXXXXXXX"}
```

状态为 `pending`、`running`、`completed`、`failed` 或 `cancelled`，响应含各状态计数及最多 50 项 `failures`，可能有 `failuresTruncated`。一行最长约 10 分钟；通常每 30–60 秒查询一次。任务完成后用 `listRecords` 读取图片。常见失败是该行缺参考图或提示词引用列无值；补齐后仅重跑对应行。余额不足会取消任务并可能返回下游 402。

## 工作流关联

共同约束：`flowId` 由工作流侧提供，不校验格式；一条流最多对应一个 `tableId` 触发表。`tableId` 必须属于该流归属的 notebook，否则 400。多维表侧没有工作流名称、节点或启停数据。`registerWorkflow` 和 `updateWorkflowTriggerTable` 要求对 notebook 有写权限；`listWorkflows` 按可见性过滤；`unregisterWorkflow` 守团队边界，但不要求容器写权限。

### registerWorkflow

登记已存在工作流和 notebook 的关联。`notebookId`、`flowId` 必填；`tableId` 可选，允许 `null`。

```json
{"notebookId":"nbkXXXXXXXX","flowId":"workflow-id","tableId":"tblXXXXXXXX"}
```

响应含 `flowId`、`notebookId`、`tableId`、时间字段及可选 `alreadyRegistered:true`。登记是幂等的；重复登记返回现状，不会更新触发表。`tableId:null` 或省略表示未设触发表，工作流不会由任何表记录变化触发。需要改触发表请用 `updateWorkflowTriggerTable`。

### listWorkflows

只读查询当前用户可见的关联。`notebookId` 可选，缺省列当前团队可见范围内全部关联；不分页。

```json
{"notebookId":"nbkXXXXXXXX"}
```

响应含 `total` 和 `workflows[]`，对象有 `flowId`、`notebookId`、`tableId`（可为 null）、`createdTime`、`lastModifiedTime`。空结果可能表示没有关联，也可能是当前身份看不到相应容器；不能据此断言流不存在。`tableId:null` 表示不触发。

### updateWorkflowTriggerTable

更新一条已登记流的触发表。`flowId` 和 `tableId` 两个键都必填；`tableId` 为 `tbl...` 或 JSON `null`。省略 tableId 不是解绑。

```json
{"flowId":"workflow-id","tableId":null}
```

`null` 会使流不再被任何记录变化触发，但关联仍保留；须先向用户说明并取得确认。响应 `status:"updated"` 才表示生效；`status:"not_found"` 表示没有改动，不能报告成功。替换表必须属于同一个 notebook。表被删除或移出容器后服务端会自动清空触发表，无需重复调用。

### unregisterWorkflow

彻底移除工作流与多维表的关联，不删除工作流本身。必填 `flowId`。先用 `listWorkflows` 核对目标，复述即将解除的流和影响并取得明确确认。

```json
{"flowId":"workflow-id"}
```

返回 `status:"unregistered"` 或 `"not_found"`，二者都表示多维表侧已无该关联；若用户确信关联原本存在，可先检查 flowId。解除后工作流定义仍留在工作流侧；若要恢复，须重新登记并重新配置触发表。

## 通用错误处理

| 下游结果 | 含义与动作 |
|---|---|
| 400 | 参数、字段名、字段类型、过滤条件或容器/表关联不合法。转述 `errmsg` 并按其指出的精确参数修正。 |
| 401 | 下游身份未建立；进入主文档“解决认证和积分问题”，读取 onboarding 引导。 |
| 402 | 积分或余额不足；停止收费调用并读取 onboarding 引导，由用户决定后续。 |
| 403 | 无权访问或修改目标表/关联；作为权限问题处理，不当作登录或余额问题。 |
| 404 | 表、记录或容器不存在、ID 错误，或资源不在当前团队。重新从可见列表取得 ID。 |
| 409 | 常见于 `createTable` 的同 requestKey 请求仍在进行；稍后使用同一 key 查询/重试，不换 key。 |
| 500 / 503 | 服务端或数据库暂时异常。写操作先用只读接口核对状态，避免重复创建、写入或删除；只读操作可稍后再试。 |

各 operation 的实际错误字段和状态字段优先于 HTTP 状态。HTTP 或 MCP 外层成功并不代表业务操作成功。
