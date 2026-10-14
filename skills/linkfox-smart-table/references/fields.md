# 表结构：listFields / addFields / deleteFields

本文件覆盖读表头（`listFields`）、加列（`addFields`）、删列（`deleteFields`）三个操作。
三者共用下面的「字段类型总表」：建列时 `type` 从这十种里选，写值时按「怎么写值」一列填。
这套接口的入参**全程按字段名寻址**；出参里的 `fieldId` 只给工作流配触发条件用（见 § listFields）。

## 字段类型总表（十种可建类型）

| 对外名 `type` | 中文 | 怎么写值（`createRecords` / `updateRecords`） | 建列要求 | 能否当 `createTable` / `addTable` 首列 |
|---|---|---|---|---|
| `singleLineText` | 单行文本 | 字符串 | 最通用；不确定就用它 | 能 |
| `longText` | 多行文本 | 字符串 | | 能 |
| `number` | 数字 | 数字（开了 typecast 时字符串也行） | | 能 |
| `singleSelect` | 单选 | 字符串，**须在 `choices` 里** | **必须给 `choices`** | 能 |
| `multipleSelect` | 多选 | **数组**，元素须在 `choices` 里 | **必须给 `choices`** | 能 |
| `date` | 日期 | ISO 字符串 | | 能 |
| `checkbox` | 勾选 | 布尔 | | **不能**（会 400） |
| `rating` | 评分 | 整数，`max` 是上限（超过会被截断） | | 能 |
| `image` | 图片（外链） | **一个图片 URL 字符串**，不用上传、不用 token | | 能 |
| `attachment` | 附件 | ⚠️ **不能直接写 URL**（会 400）；见下一节 | 无需任何选项 | **不能**（会 400） |

- 首列（主字段，最左那列，代表"这一行是什么"）限制只针对 `createTable` / `addTable` 的 `fields[0]`；**`addFields` 没有首列限制**，加的列永远排在已有列后面，不会成为主字段。
- `choices[].color` 传的话要是站点色名（如 `blueBright`），**不是** `#RRGGBB`；不传由前端自动配色。
- 单行文本还有"点开跳转"等其它展示形态（网址/邮箱/电话），**这套接口不开放配置**，要用户在页面上改。

### `image` 与 `attachment` 别搞混

`image` 在底层就是一列**单行文本**，存的是图片外链，只是表格把这一格的值当图片画出来；`attachment` 存的是真正的文件。
出参 `fields[].type` 把前者报成 `image`（不是 `singleLineText`），就是为了让调用方知道**这一列该写图片 URL**。

| | `image` | `attachment` |
|---|---|---|
| 值 | 一个 URL 字符串 | 附件对象数组（含 token） |
| 怎么写 | `createRecords` / `updateRecords` **直接给字符串**，如 `{"主图": "https://example.com/a.jpg"}` | 只能用 `uploadAttachment`（见 `references/attachment.md`）一张张追加，或写 `[{name, token}]`（**整格替换**，不是追加）；**直接写 URL 会 400** |
| 怎么读 | 就是那个字符串 | `listRecords` 返回的 `presignedUrl`（见 `references/records-read.md`；临时，最长约 3 小时） |
| 文件在哪 | 别人的服务器（原站） | 我们的对象存储 |
| 一格几张 | 一个链接 | 多张 |

- `image` **服务端不校验** URL 形态（单行文本的校验就是"是个字符串"），写什么存什么；链接失效、或压根不是图片时，表格里显示占位图，不会报错。
- ⚠️ 反过来也成立：一列报成 `singleLineText` 就**不是**图片列，往它写 URL 只会显示成一串文字。要图片列得在建列时指定 `image`（`addFields` / `createTable` / `addTable`），或让用户在页面上改这一列的展示形态。

### `listFields` 会报出、但不能建的类型

表可能是用户在页面上建的，所以 `listFields` 还会报出下面这些类型。**能读，但这套接口建不了**（`addFields` / `createTable` / `addTable` 传了会 400），其中多数也**写不进去**：

| type | 含义 | 能否写入 |
|---|---|---|
| `link` | 关联另一张表 | **这套接口写不了** |
| `user` / `createdBy` / `lastModifiedBy` | 人（成员类） | 值是内部用户 id，对调用方无意义；`createdBy` / `lastModifiedBy` 是算出来的（`isComputed: true`） |
| `formula` / `rollup` / `conditionalRollup` / `autoNumber` / `createdTime` / `lastModifiedTime` / `button` | 公式 / 汇总 / 自动编号 / 系统时间 / 按钮 | **写不进去**（`isComputed: true`），值是系统算出来的 |

**为什么只开放那十种**：刻意只放"自足"的类型——只看这个字段的定义本身就能建出来，不需要引用别的表、别的字段（`attachment` 建列本身无需任何选项，往里放图另有专门接口）。被排除的不是不重要，而是**外部调用极难一次填对**、且填错时报的是内部错误：

- `link`（关联）：要另一张表的 `tblXXX`，还会产生跨表的对称字段
- `formula` / `rollup` / `conditionalRollup`（公式 / 汇总）：表达式里要引用内部字段 id（`fldXXX`），而这套接口的**入参**全程按字段名寻址、不接受字段 id（出参里的 `fieldId` 是给工作流配触发条件用的，不能拿来写表达式：建表这一刻那些 id 还不存在）
- `user` / `createdBy` / `lastModifiedBy`（成员类）：值是内部用户 id（`usrXXX`），对调用方无意义
- `createdTime` / `lastModifiedTime` / `autoNumber`（系统字段）：建了也只是噪音
- `button`：纯 UI 交互

需要这些的场景：先用基础类型建列，再请用户到页面上补。

---

## listFields —— 读一张表有哪些列、每列什么类型、选项列有哪些可选项

**何时用 / 不该用**：
- **往表里写数据前必须先调它**，这是写入的第一步——不知道字段名就写不进去。流程：`listMyTables` 找到表 → **`listFields` 看表头** → `createRecords` 写数据。
- 用户问"这张表有哪些字段"；拼 `listRecords` 的 `fieldNames` 或 `filter` 之前确认字段名。
- 手上只有表名没有 `tableId` → 先用 `listMyTables` / `listSharedTables`（见 `references/tables.md`）。⚠️ 那两条的出参是**两层**的：数据表在 `notebooks[].tables[]` 和 `looseTables.tables[]` 里，两处都要找；顶层的 `notebookId` 是容器 id，不能当 `tableId` 用。
- 要读表里的**数据** → `listRecords`（见 `references/records-read.md`）；要往表里加行 → `createRecords`（见 `references/records-write.md`）。
- 要**加列** → `addFields`；要**删列** → `deleteFields`（都在本文件）；要**改列名/改类型** → 这套接口做不到，请用户在页面上改。
- 飞书/Lark 多维表格 → `lark-base`（不是同一个系统）。

**调用**：`python scripts/smart_table.py listFields '{"tableId":"tblXXX"}'`

### 参数

| 参数 | 类型 | 必填 | 默认 | 约束 | 说明 |
|---|---|---|---|---|---|
| tableId | string | **是** | - | 以 `tbl` 开头 | 从 `listMyTables` / `listSharedTables` 的 `notebooks[].tables[].tableId`（或 `looseTables.tables[].tableId`）取 —— **不是**顶层的 `notebookId` |
| includeChoices | boolean | 否 | `true` | | 是否返回单选/多选字段的可选项。宽表嫌响应大可以设 `false` |

**不接受**：`baseId` / `viewId` / `spaceId`（内部概念）、分页参数（本接口一次返回全部字段）。

**为什么 `includeChoices` 默认开**：不给可选项，调用方只能猜单选值，猜错换来一次写入报错往返。这条接口存在的意义就是"一次问清、一次写对"，所以默认给全。

### 响应

| 字段 | 类型 | 说明 |
|---|---|---|
| tableId | string | 回显 |
| name | string | **表名**（回显，省掉再查一次 `listMyTables`） |
| total | integer | 字段总数（= `fields.length`，本接口不分页） |
| fields | array | 字段列表，**顺序即表格里的列顺序** |

字段对象 `fields[]`：

| 字段 | 类型 | 何时出现 | 说明 |
|---|---|---|---|
| fieldId | string | 总是 | 内部字段 id（`fldXXX`）。**只用于工作流的触发配置，不能当写入的 key** —— 见下 |
| name | string | 总是 | **字段名**。写入接口就是按它寻址 |
| type | string | 总是 | 见文件开头的类型总表 |
| isPrimary | boolean | 仅为 true 时 | 主字段（最左那列，代表"这一行是什么"） |
| isComputed | boolean | 仅为 true 时 | **算出来的字段，写不进去**。见下 |
| isMultipleCellValue | boolean | 仅为 true 时 | 该格放多个值 ⇒ **写入时传数组**（如多选），其余传单个值 |
| choices | array[string] | 选项类字段且 `includeChoices` 为 true | 可选项名称列表 |
| max | integer | 评分字段 | 上限（写入时超过会被截断） |
| description | string | 表设计者写了备注时 | 字段说明，对理解该填什么很有用 |

> **布尔项只在为 `true` 时出现**（与主字段标记一致），不要用 `field["isComputed"] is False` 判断，用 `field.get("isComputed")`。

```json
{
  "errcode": 200, "errmsg": "ok",
  "tableId": "tblAbCdEfGhIjKl", "name": "选品清单", "total": 6,
  "fields": [
    {"fieldId": "fldAbCdEfGhIjKlMnO", "name": "商品标题", "type": "singleLineText", "isPrimary": true},
    {"fieldId": "fldPqRsTuVwXyZ01234", "name": "价格", "type": "number", "description": "美元含税价"},
    {"fieldId": "fld56789AbCdEfGhIj", "name": "状态", "type": "singleSelect", "choices": ["待处理", "已选中", "已淘汰"]},
    {"fieldId": "fldKlMnOpQrStUvWxY", "name": "标签", "type": "multipleSelect", "isMultipleCellValue": true, "choices": ["清仓", "新品", "主推"]},
    {"fieldId": "fldZ0123456789AbCd", "name": "评分", "type": "rating", "max": 5},
    {"fieldId": "fldEfGhIjKlMnOpQrS", "name": "利润率", "type": "formula", "isComputed": true}
  ]
}
```

### 语义与坑

**为什么必须用这条接口，不能从数据里推字段**（实测结果，不是推测）。写入接口（`createRecords` / `updateRecords`）按**字段名**寻址，名字写错是**整批拒绝**（`404 Field "xxx" does not exist in this table`），所以字段名是写入的前置条件。而：

| 试图用来推字段的办法 | 实际结果 |
|---|---|
| `listRecords` 读一行看 `fields` 的 key | **推不全**。实测 9 个字段的表只推出 5 个——**空单元格整个不出现**（不是 `null`），另外 4 列不是不存在，是那几格恰好为空；加上视图隐藏列 |
| `listRecords` 读空表 | **什么都推不出**。而"刚建的空表要填数据"正是最常见的场景 |
| `listRecords` 的 `fieldNames` 传个猜的名字试探 | **静默失效**：回 `errcode 200` + 每行 `fields: {}`，既不报错也不给线索 |
| 故意用不存在的字段名去 `filter` | 能拿到全清单（400 报错里会列出可用字段名），但那是**靠触发报错读结构**，不是正当途径 |

**写入侧是安全的**（可以放心试）：`createRecords` 遇到未知字段名是**明确报错且整批拒绝**，混了一个真字段也照样整批拒。所以最坏情况是试一次、按报错改，**不会写进去一半、不会污染数据**。但既然有这条接口，就不该靠试。

**⚠️ `isComputed` 是本接口最该看的一项**：`formula`、`rollup` / `conditionalRollup`、`autoNumber`、`createdTime` / `lastModifiedTime`、`createdBy` / `lastModifiedBy`、`button` 的值是**系统算出来的**，写入接口不接受。不看这个标记的后果：把公式列当普通列去写，然后拿到一个底层报错。**写入前先按 `isComputed` 过滤一遍，这些字段直接跳过**，不要放进要写的 `fields` 里；也要明确告诉用户哪些列是算出来的、不能填。

**单选/多选按 `choices` 填**，才不会被拒，不要自己造值。用户给的值不在 `choices` 里时，先问用户是要改成已有选项、还是确实要加新选项（**给已有列加选项这套接口做不到**，得在页面上改）。

**`type` 的读法**：`image` 列写图片 URL 字符串；`attachment` 列不能直接写 URL；报成 `singleLineText` 的列**不是**图片列——详见文件开头「`image` 与 `attachment` 别搞混」。

**⚠️ `fieldId` 只能用在工作流的触发配置上，不能拿去写入**。出参给了 id，不等于入参认 id。这套接口的写入侧全部**只认字段名**：

| 用在哪 | 该传什么 |
|---|---|
| `createRecords` / `updateRecords` 的 `fields` 的 key | **字段名** |
| `listRecords` 的 `fieldNames` 和 `filter.conditions[].fieldName` | **字段名** |
| `deleteFields` 的 `fieldNames` | **字段名** |
| 工作流（自动化）的触发条件、字段匹配 | **`fieldId`** |

传 `fldXXX` 当写入 key 会被当成一个**不存在的字段名**报错（`404 Field "fldXXX" does not exist in this table`）。
`fieldId` 是 2026-09-10 加的，原因只有一个：多维表推给工作流的变更消息里，字段的 key 是 `fldXXX`，工作流侧配触发条件必须用 id，而**不允许自己建「字段名 → id」的映射**——字段名在库里没有唯一约束，同名列理论上存在，映射会让两格挤进同一个 key 而丢数据。所以要那份 id 清单，只能从这条接口拿。**不是在配工作流，就忽略 `fieldId`。**

**其它**：
- **隐藏列也会列出来**。这套接口不区分"视图里藏起来的列"——藏起来的列照样能写入。
- **字段名可能带空格或中文**，原样使用，不要自己规范化大小写或去空格。
- **不分页**，一次返回全部字段。**只读**：加列用 `addFields`、删列用 `deleteFields`，**改列名/改类型这套接口做不到**，要在页面上操作。
- 只能读**自己团队 base 内、且自己有读权限**的表；别人团队的 `tableId` 会报表不存在。
- **展示给用户**：字段不多时列成表格（字段名、类型、可选项），并明确标出哪些列是算出来的、不能填；报错时把 `errmsg` 原文转述——这套接口的错误信息是按"调用方能照着改"写的。

### 常见错误

| errmsg 关键词 | 原因 | 怎么办 |
|---|---|---|
| `Missing required parameter: tableId`（本地预检，未发请求） | 没传 `tableId` | 补上 |
| `tableId 必须以 tbl 开头`（本地预检，未发请求） | 传了 `notebookId`、表名等 | 用 `listMyTables` 按表名找到 `tbl` 开头的 id |
| 400 入参不合法 | `tableId` 前缀不对 | 同上 |
| 403 无权读这张表 | 表不在你团队里，或你在这张表上没有读权限 | 换表或请表的所有者授权 |
| 404 表不存在 | `tableId` 写错、表已被删除，或是别人团队的表 | 重新用 `listMyTables` / `listSharedTables` 取 |
| 500 / 503 | 服务端异常（`errmsg` 已消毒）/ 数据库暂不可用 | 500 可重试一次；503 稍后重试 |

### 示例

```json
{"tableId": "tblAbCdEfGhIjKl"}
```

```json
{"tableId": "tblAbCdEfGhIjKl", "includeChoices": false}
```

---

## addFields —— 往已有表追加新列（一次 1～50 列，一律加到最后）

**何时用 / 不该用**：
- 用户明确要往某张表加列；或写数据时发现缺一列，需要先补上。
- **调用前先用 `listFields` 看现有列**，这一步不能省：既避免重名报错，也避免加一列其实已经有的东西。
- 想加一列显示图片的（主图、商品图、封面）：只存外链用 `image`（值是图片 URL 字符串、不用上传文件）；要把图存进表格自己的存储用 `attachment`（加完用 `uploadAttachment` 放图，见 `references/attachment.md`）。
- 手上只有表名没有 `tableId` → 先 `listMyTables` / `listSharedTables`（见 `references/tables.md`；⚠️ 出参两层，数据表在 `notebooks[].tables[]` 和 `looseTables.tables[]` 里，两处都要找；顶层 `notebookId` 不能当 `tableId`）。
- 往已有**多维表**里加一张**表**（不是加列）→ `addTable`；要建一张**新表** → `createTable`（都见 `references/tables.md`）。
- 只是想知道有哪些列 → `listFields`；要**删列** → `deleteFields`；要加**行**（数据）不是列 → `createRecords`（见 `references/records-write.md`）。
- 要**改列名/改类型**、调顺序 → **不要用本操作**，它只能加新列；请用户在页面上改。
- 飞书/Lark 多维表格 → `lark-base`（不是同一个系统）。

**调用**：`python scripts/smart_table.py addFields '<JSON>'`

### 参数

| 参数 | 类型 | 必填 | 默认 | 约束 | 说明 |
|---|---|---|---|---|---|
| tableId | string | **是** | - | 以 `tbl` 开头 | 表 id |
| fields | array | **是** | - | 非空，**1～50 项** | 要加的列，**一律追加到最后** |
| fields[].name | string | **是** | - | 1～255 字符 | 列名。**与已有列或批内其他列重名会报错**（见下） |
| fields[].type | string | **是** | - | 十种之一 | 见文件开头「字段类型总表」 |
| fields[].choices | array[object] | 单选/多选**必填** | - | 非空；每项必须有 `name` | `[{"name": "选项名", "color": "blueBright"}]`，`color` 可选 |
| fields[].ai | object | 否 | - | 只能配在 `attachment` 列上 | 建成 AI 出图列（提示词 + 参考图）。`{列名}` 可引用已有列或本批一起加的列；引用写错时整批 400、一列都不加。字段、模型与触发方式见 `references/ai.md` |

**不接受**：`baseId` / `viewId`（内部概念）、位置/顺序参数（一律追加到最后，不能插到中间——那是视图概念，这套接口不涉及）、`fldXXX`（本接口**入参**全程按名称寻址；出参里有 `fieldId`，但那是给工作流配触发条件用的）。

**`choices` 的形状**：⚠️ 是**对象数组**，不是字符串数组（注意与 `listFields` 出参的 `choices` 是字符串数组不同）。`color` 传的是站点色名（`blueBright` / `greenBright` / `redBright` …），**不是 `#RRGGBB`**；不确定就不传，前端会自动配色。

```jsonc
"choices": [
  {"name": "待处理"},
  {"name": "已完成", "color": "greenBright"}   // color 可选
]
```

### 响应

| 字段 | 类型 | 说明 |
|---|---|---|
| added | integer | 加了几列（= 入参 `fields.length`） |
| fields | array | **加完之后的完整表头**（不只是新加的），字段对象形状与 `listFields` 一致（`isComputed` / `isMultipleCellValue` / `choices` 等标记含义见 § listFields 响应） |

`fields` 是完整表头，所以**加完可以直接写数据，不必再调一次 `listFields`**。新加的 `image` 列在出参里 `type` 也回显成 `image`。

```json
{
  "errcode": 200, "errmsg": "ok",
  "added": 1,
  "fields": [
    {"fieldId": "fldAbCdEfGhIjKlMnO", "name": "商品标题", "type": "singleLineText", "isPrimary": true},
    {"fieldId": "fldPqRsTuVwXyZ01234", "name": "价格", "type": "number"},
    {"fieldId": "fld56789AbCdEfGhIj", "name": "备注", "type": "singleLineText"}
  ]
}
```

### 语义与坑

**⚠️ 重名是报错，不是自动改名**——这是本操作最该知道的一条，与页面行为相反：

| 场景 | 页面/上游默认行为 | **本接口** |
|---|---|---|
| 加"价格"，表里已有"价格" | **静默改名**成"价格 1" | **400 报错，一列都不加** |
| 同一次请求里两项都叫"备注" | 逐个改名 | **400 报错**（脚本本地先拦） |

改成报错的理由：静默改名之后，调用方会以为自己加的是"价格"、回头往"价格"写数据，**实际写进了原有那一列**，而且全程没有任何提示。
**收到重名报错时不要自作主张改名重试**——那正是这道检查要防的事。把撞上的列名转述给用户，问他是要复用已有那列还是换个名字。

**全有全无**：任何一项不合法（重名、类型不支持、单选缺 `choices`、超 50 列），整批拒绝、**一列都不加**，不会出现"加进去一半"。按 `errmsg` 改了重来即可。

**只能加，不能改**：改列名、改类型、调顺序都不行（删列用 `deleteFields`）；不能指定位置，一律追加到最后。
**只支持十种自足类型**：公式、汇总、关联、人员、自动编号这些**本接口不支持**——它们要引用别的表/别的字段，agent 很难一次填对；用户要这些，告诉他在页面上加（理由见文件开头「不能建的类型」）。
**`addFields` 没有首列限制**：加列不产生主字段，所以 `checkbox` / `attachment` 都能加。

**其它**：
- **加列不影响已有数据**，已有行在新列上都是空的。
- 加列本身**不可撤销地**改了表结构：要去掉只能删列，而删列是不可恢复的。
- 只能改**自己团队 base 内、且自己有字段创建权限**的表。
- **展示给用户**：执行前告诉用户要加哪几列、什么类型，单选列要列出选项；执行后说明加了几列，并把**完整表头**给用户看（哪些是原有的、哪些是新加的）。

### 常见错误

带「本地预检」的是脚本在发请求前拦下的，未调接口、exit 1。

| errmsg 关键词 | 原因 | 怎么办 |
|---|---|---|
| `缺少 tableId` / `tableId 必须以 tbl 开头`（本地预检） | 没传或传了 `notebookId`、表名 | 用 `listMyTables` 按表名找到 `tbl` 开头的 id |
| `缺少 fields（非空数组）`（本地预检） | `fields` 缺失、为空或不是数组 | 补上 |
| `一次最多加 50 列`（本地预检；服务端同样 400） | 超过 50 项 | 分批调用 |
| `缺少 name（列名）`（本地预检） | 某项没给 `name` | 补上 |
| `在本次请求里重复了`（本地预检；服务端同样 400） | 批内重名 | 去掉重复项；名字怎么定问用户 |
| 400 列名与已有列重名 | 表里已有同名列 | **不要改名重试**，问用户复用已有列还是换名 |
| `type ... 不支持`（本地预检；服务端同样 400） | 类型不在十种白名单里 | 换成支持的类型，或请用户在页面上加 |
| `必须提供 choices`（本地预检；服务端同样 400） | 单选/多选没给 `choices` | 补上 |
| `choices 每项必须是 {"name": "选项名"} 这样的对象`（本地预检） | 传成了字符串数组 | 改成对象数组 |
| 403 无权改这张表的结构 | 表不在你团队里，或你在这张表上没有字段创建权限 | 换表或请表的所有者授权 |
| 404 表不存在 | `tableId` 写错，或表已被删除 | 重新用 `listMyTables` / `listSharedTables` 取 |
| 500 / 503 | 服务端异常（`errmsg` 已消毒）/ 数据库暂不可用 | **重试前先调 `listFields` 确认到底加没加上**，再决定是否重试 |

### 示例

加一列文本：
```json
{"tableId": "tblXXXXXXXX", "fields": [{"name": "备注", "type": "singleLineText"}]}
```

一次加两列，其中一列是单选：
```json
{"tableId": "tblXXXXXXXX", "fields": [
  {"name": "负责人备注", "type": "longText"},
  {"name": "进度", "type": "singleSelect", "choices": [{"name": "未开始"}, {"name": "进行中"}, {"name": "已完成"}]}
]}
```

加一列图片外链 + 一列附件：
```json
{"tableId": "tblXXXXXXXX", "fields": [{"name": "主图", "type": "image"}, {"name": "商品图", "type": "attachment"}]}
```

---

## deleteFields —— 按列名删整列（破坏性、按不可恢复对待、全有全无）

**何时用 / 不该用**：
- 用户明确要求删掉指定的某几列；清理建错/多余的列，且已确认过。
- 用户只是"觉得这列没用" → 先用 `listFields` 列出来给用户看，**别删**。
- 删**行**（记录）→ `deleteRecords`，不是本操作；清空一列的值但保留这列 → 本操作做不到，用 `updateRecords` 逐行写空（都见 `references/records-write.md`）。
- 改列名/改类型 → 做不到，请用户在页面上改；加列 → `addFields`；删整张表 → 不做，请到页面上操作。
- 飞书/Lark 多维表格 → `lark-base`（不是同一个系统）。

**调用**：`python scripts/smart_table.py deleteFields '<JSON>' --yes`

⚠️ **确认闸门**：缺 `--yes` 时脚本拒绝执行（stderr 打印将删哪几列、哪张表，**退出码 2**，不发请求）。流程固定为：先 `listFields` 确认列名、看清哪列是主字段、哪些是公式列 → 向用户列出要删的列名 + 类型 → 说明不可恢复 → 拿到明确确认 → 才加 `--yes` 调用。

### 参数

| 参数 | 类型 | 必填 | 默认 | 约束 | 说明 |
|---|---|---|---|---|---|
| tableId | string | **是** | - | 以 `tbl` 开头 | 从 `listMyTables` / `listSharedTables` 的 `notebooks[].tables[].tableId` 取（那两条出参是两层的，顶层 `notebookId` 是容器、不能用在这里） |
| fieldNames | array[string] | **是** | - | 非空，**1～50 项**，不能重复、不能有空值 | 要删的**列名**（**不是 `fldXXX`**）。全有全无 |
| allowBreakingDependents | boolean | 否 | `false` | | 允许弄坏依赖这些列的公式/汇总/lookup 列。见下「守卫④」 |

**不接受**：`baseId` / `viewId`（内部概念）、`fldXXX`（本接口**入参**全程按名称寻址；出参里有 `fieldId`，但那是给工作流配触发条件用的）。
列名从 `listFields` 的 `name` 取，**原样传**（带空格、中文都不要规范化）。⚠️ 取的是 `name`，**不是 `fieldId`**——传 `fldXXX` 会被当成一个不存在的列名报错（脚本本地先拦）。

### 响应

| 字段 | 类型 | 说明 |
|---|---|---|
| deleted | integer | 删了几列（= 入参 `fieldNames.length`，因为全有全无） |
| brokenDependents | array[string] | 被弄坏的列名。**只有传了 `allowBreakingDependents: true` 时才可能非空**；成功后要检查它 |
| fields | array | 删完之后的**完整表头**，字段对象形状与 `listFields` 一致 |

一起被删的列之间互相引用**不算**"被弄坏"——它们都要走，不会出现在 `brokenDependents` 里。

```json
{"errcode": 200, "errmsg": "ok", "deleted": 1, "brokenDependents": [],
 "fields": [
   {"fieldId": "fldAbCdEfGhIjKlMnO", "name": "商品标题", "type": "singleLineText", "isPrimary": true},
   {"fieldId": "fldPqRsTuVwXyZ01234", "name": "价格", "type": "number"}
 ]}
```

带连带损伤的响应：

```json
{"errcode": 200, "errmsg": "ok", "deleted": 1, "brokenDependents": ["利润率", "订单表.汇总价格"],
 "fields": [{"fieldId": "fldAbCdEfGhIjKlMnO", "name": "商品标题", "type": "singleLineText", "isPrimary": true}]}
```

### 语义与坑

**先说清楚破坏范围**：
- 删一行，没了**一行**；删一列，没了**每一行的那一格**，破坏范围比删行大一个量级。
- **按不可恢复对待。** 删列会把整列的值快照进表格回收站，理论上能恢复（重建列 + 回灌值），但恢复需要的权限**这套接口给不了**，只能到页面上试；物理列是真的删掉了。**不要向用户承诺能恢复。**
- **不进前端撤销栈**，用户在页面上撤不回来。
- **全有全无**，不支持部分成功。失败意味着**一列都没删**；**400 一律意味着一列都没删**，可以放心按报错改了重来。⚠️ **不要拆成单列重试去"至少删掉能删的"**——那正好绕过全有全无这个保护。
- **删列不影响别的列的数据**（除了依赖它的公式列会失效）。
- 宽表（几万行）删列会比较慢——整列的值要先快照下来。
- 只能删**自己团队 base 内、且自己有字段删除权限**的表。

**四道守卫**，按顺序判，任何一道不过就整批拒绝、**一列都不删**：

| # | 守卫 | 为什么 | 怎么办 |
|---|---|---|---|
| ① | 列名要都能查到 | 任何一个查不到就 400，`errmsg` 里会**列出这张表实际有哪些列** | 照着改 |
| ② | **主字段**（最左那列）删不了 | 它代表"这一行是什么"，表必须有它 | 换主字段只能在页面上操作 |
| ③ | **关联列**（`link`）删不了 | 删双向关联会连带删掉**另一张表**里对应的那一列，影响范围越出这张表 | 请用户在页面上删 |
| ④ | **有列依赖时默认拒绝** | 见下 | 见下 |

**⚠️ 守卫④：有列依赖时默认拒绝**。有公式 / 汇总（rollup）/ lookup 列引用了要删的列时，默认 400，并**点名哪些列会失效**。
- **为什么必须有这道**：底层的默认行为是把那些列**悄悄标记成出错、但仍然返回成功**（还会沿公式链继续传递），调用方拿到 200 却不知道表里多了几个坏掉的列。
- 收到这个报错时**先把会失效的列名告诉用户、拿到确认**，再传 `allowBreakingDependents: true` 重调。**不要自己直接加上重试。**（缺 `--yes` 时若带了这个开关，脚本的拒绝文案会额外提醒这一点。）
- 出参的 `brokenDependents` 是被弄坏的列名，**要转述给用户去页面上修**。
- 跨表的依赖方会带上表名前缀（如 `订单表.汇总价格`）——那个列不在本表里，不带表名的话调用方会找不到它。
- 只报**直接**依赖。错误会沿公式链继续传递（A 引用 B、B 引用被删的列），但把整条链展开会让错误信息长到没法读；直接依赖足够说明"这一删有连带损伤"。

**展示给用户**：
- 执行前：列出要删的列名 + 类型，明确说"删了每一行的这一格都会没有，且按不可恢复对待"，等用户确认。
- 执行后：说明删了哪几列，并给出**删完之后的完整表头**；`brokenDependents` 非空时明确告诉用户哪些公式列已经失效、需要去页面上修。
- 报错时把 `errmsg` 原文转述，并明确告知**一列都没有被删除**。
- **不要声称删掉了，除非返回 `errcode: 200`**。

### 常见错误

带「本地预检」的是脚本在发请求前拦下的，未调接口、exit 1；确认闸门 exit 2。

| errmsg 关键词 | 原因 | 怎么办 |
|---|---|---|
| `拒绝执行：删列按不可恢复对待`（确认闸门，exit 2） | 没加 `--yes` | 按上面流程向用户复述并拿到确认后，加 `--yes` 重跑 |
| `缺少 tableId` / `tableId 必须以 tbl 开头`（本地预检） | 没传或传了 `notebookId`、表名 | 用 `listMyTables` 按表名找到 `tbl` 开头的 id |
| `缺少 fieldNames`（本地预检） | `fieldNames` 缺失、为空或不是数组 | 补上**列名**数组 |
| `一次最多删 50 列`（本地预检；服务端同样 400） | 超过 50 项 | 分批调用 |
| `fieldNames 里有空值或非字符串`（本地预检） | 数组里有空串 / 非字符串 | 去掉 |
| `这些看起来是字段 id 而不是列名`（本地预检） | 传了 `fldXXX` | 改用 `listFields` 的 `name` |
| `fieldNames 里有重复项`（本地预检） | 列名重复 | 去重后再调 |
| 400 列名不存在 | 守卫①；`errmsg` 会列出可用列名 | 照着改，原样传 |
| 400 要删主字段 | 守卫② | 请用户在页面上换主字段 |
| 400 有列依赖它 | 守卫④；`errmsg` 点名会失效的列 | 告诉用户、拿到确认后加 `allowBreakingDependents: true` |
| 403 | 无权删这张表的列，或要删的是关联列（守卫③） | 权限不足，或改用页面操作 |
| 404 表不存在 | `tableId` 写错，或表已被删除 | 重新用 `listMyTables` / `listSharedTables` 取 |
| 500 / 503 | 服务端异常（`errmsg` 已消毒）/ 数据库暂不可用 | **重试前先调 `listFields` 确认到底删没删掉**，再决定是否重试 |

### 示例

删一列（已向用户复述并拿到确认，命令行带 `--yes`）：
```json
{"tableId": "tblXXXXXXXX", "fieldNames": ["备注"]}
```

用户确认了要连带弄坏依赖它的公式列（同样带 `--yes`）：
```json
{"tableId": "tblXXXXXXXX", "fieldNames": ["价格"], "allowBreakingDependents": true}
```
