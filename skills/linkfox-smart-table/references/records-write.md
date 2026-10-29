# 写记录

本文件覆盖 `createRecords`（加行）、`updateRecords`（改已有行）、`deleteRecords`（删行）三个操作。
三者都按**字段名**寻址、按 `recordId` 定位行；下面「共用规则」对三个操作都成立，各节只写自己特有的部分。

## 共用规则（三个写操作都适用）

### 新增 vs 修改：先分流，用错的后果不对称

| 意图 | 用哪条 | 用错会怎样 |
|---|---|---|
| 表里还没这行 | `createRecords` | — |
| 表里已有这行、改它的值 | `updateRecords` | 用 `createRecords` 去「改」会**多出一行重复数据**，且返回 200 看起来像成功 |
| 删掉指定的行 | `deleteRecords` | — |

- 一句话：**有 `recordId` 用 update，没有用 create**。用户说「把这批数据写进表里」而表里还没有对应行，那是**新增**。
- 反方向（拿 `updateRecords` 去新增）没有 `recordId` 可填，本地预检直接挡住；拿一个不存在的 `recordId` 去改则会被静默跳过（见 `updateRecords` 的条数核对）。拿不准时**先用 `listRecords` 读一遍**，确认那一行在不在。
- 不做 upsert（「有则改无则增」）：匹配改动请自己先读后判。
- 链路：`createTable`（只建结构，不收数据）→ `createRecords`（写数据、拿 `recordId`）→ `updateRecords` / `deleteRecords`。新建的空表**只能**靠 `createRecords` 填数据，也只有它能给出后续改删所需的 `recordId`。

### 字段名、recordId、typecast

- **字段名要和表里完全一致**（含中英文、空格、大小写）。对不上会报错，不会自动建列。不确定有哪些列先用 `listFields`（见 `references/fields.md`）读表头：它给出字段名、类型、单选的可选项，以及哪些列是公式/汇总算出来的（这些**写不进去也改不了**）。别靠 `listRecords` 读一行去推：空单元格整个不出现，空表更是什么都推不出来。
- 表里**缺一列**、要先补上再写 → `addFields`（见 `references/fields.md`）。
- **`tableId` 从 `listMyTables` / `listSharedTables` 取**：那两条出参是两层的，数据表在 `notebooks[].tables[]` 和 `looseTables.tables[]` 里，两处都要找；顶层的 `notebookId` 是容器 id，不能当 `tableId` 用（见 `references/tables.md`）。
- **`recordId` 从 `listRecords` 或 `createRecords` 的返回里来，不能猜也不能拼**。
- **`typecast` 默认开**（与上游相反，上游为保证数据完整性默认关）：agent 和工作流传过来的值基本都是字符串，默认开能省掉大量类型错误（数字字段收到 `"25.99"` 会被自动转换）。要严格校验时显式传 `typecast: false`，此时类型不匹配会 400。
  ⚠️ 开着 `typecast` 时写进去的值可能被转换过，**以响应里返回的 `records` 为准**，别假设等于你发出去的。

### 单次上限、撤销、权限

- **create / update 有单次单元格数上限**，按 `Σ(每条记录的字段数)` 算，不是记录数：宽表 100 条 × 50 列和窄表 100 条 × 2 列代价差 25 倍。默认量级是万级，可由运维调整，超了返回 400 并说明是「单元格数」超了。大批量请分批，每批之间核对返回的 `created` / `updated`。`deleteRecords` 的上限另算（按条数，见该节）。
- **不进前端撤销栈**。内网写入没有窗口上下文，不会出现在任何人的前端撤销历史里，用户在页面上按 Ctrl+Z 撤不回来。这是想要的行为，但要**提前告知用户**。
- 只能写**自己团队 base 内**、且自己在这张表上有对应权限（`record|create` / `record|update` / `record|delete`）的表。

### 图片列与附件列怎么写

两种列怎么从 `listFields` 里认出来见 `references/fields.md`。写入时：

| 列类型 | 能写的值 | 效果 |
|---|---|---|
| `image` | 一个图片外链字符串，如 `"https://example.com/a.jpg"` | 写入/覆盖这一格（换图就是覆盖）。**不用上传、不用 token** |
| `image` | `null` | 清空（不要传 `""`） |
| `attachment` | `[{"name": "a.png", "token": "<token>"}]` | **整格替换**成这些附件（不是追加，原有的图会被换掉） |
| `attachment` | `null` | 清空 / 留空 |

- ⚠️ `image` 列**服务端不校验** URL 形态（底层是单行文本，校验就是「是个字符串」）：写进去的不是图片链接也会成功，只是表格里显示占位图。**不会报错，链接对不对要自己把住。**
- `image` 列一格只存一个链接，多张图塞不进去；要一格多张用 `attachment` 列 + `uploadAttachment`。
- 报成 `singleLineText` 的列**不是**图片列，往它写 URL 只会显示成一串文字。
- ⚠️ 往 `attachment` 列写**裸 URL 字符串**（或其它任意形状）会 **400**，`errmsg` 指向 `uploadAttachment`。以前这种写法会被**静默丢弃**还返回 200（格子是空的），现在改成显式报错。
- `token` 来自 `uploadAttachment` 的响应，或 `listRecords` 读到的附件对象。同一张图挂到别的格子不用重新上传，写 `[{name, token}]` 即可，但记住是整格替换。
- 要往附件列**放新图**用 `uploadAttachment`（见 `references/attachment.md`）：新行先用 `createRecords` 建出来（附件列不写），拿 `recordId` 后一张张追加。

## createRecords —— 往已有表里批量加行，返回服务端生成的 recordId

**何时用 / 不该用**：
- 用：新建表之后写入第一批数据；把分析/采集结果作为新行追加进表里。
- 改已有行的值 → `updateRecords`（用本操作去「改」会多一行重复数据）。
- 表还不存在 → 先 `createTable`（见 `references/tables.md`）。表里缺列 → 先 `addFields`。
- 删行 → `deleteRecords`。

**调用**：`python scripts/smart_table.py createRecords '<JSON>'`

### 参数

| 参数 | 类型 | 必填 | 默认 | 约束 | 说明 |
|---|---|---|---|---|---|
| tableId | string | **是** | - | 以 `tbl` 开头 | 必须是**已存在**的表。从列表接口的 `tables[].tableId` 取，不是 `notebookId` |
| records | array[object] | **是** | - | 非空数组 | 要新增的记录，每项 `{fields}` |
| records[].fields | object | 是 | - | 非空对象 | key 是**字段名**（不是 `fldXXX`），value 是要写入的值。没给的字段留空，这是允许的 |
| typecast | boolean | 否 | **true** | - | 自动把值转成字段该有的类型 |
| ~~recordId~~ | - | - | - | **显式拒绝** | 写在 `records[]` 里面还是顶层都会被拒，见下 |

### 响应

| 字段 | 类型 | 说明 |
|---|---|---|
| created | integer | 实际新增的记录数。**必须与入参条数比对** |
| records | array | 新增后的记录 `{recordId, fields}`，**带服务端生成的 `recordId`**（`rec` + 16 位 = 19 字符） |

`recordId` 是本操作最有价值的出参：它是后续 `updateRecords` / `deleteRecords` / `uploadAttachment` 定位这些行的唯一途径。响应过大时脚本 stdout 只打摘要（`created` + 前 3 条新记录）。

### 语义与坑

- **不要传 `recordId`**。id 由服务端生成，传了会被**明确拒绝**而不是静默忽略：静默忽略会让你以为自己指定了 id，回头拿它去 update 却找不到那一行。
  - 内外两层都拦：`records[i].recordId` 和顶层 `recordId` 都报 400，`errmsg` 末尾的 `at "..."` 指明位置（内层是 `records[0].recordId`，顶层是 `recordId`）。脚本本地预检也逐条扫 `records[i]`。
  - 服务端 2026-08-17 之前那道守卫只挡顶层，写在 `records[]` 内层的会被静默忽略、然后**多建一行重复数据**；已修（内外各一道）。走脚本从来不会踩到，**不经脚本直接打接口**的调用方在旧镜像上会踩到。
- **写完把 `recordId` 留住**。用户在页面上看不到它、也没法告诉你。除非用户要，不必念给用户听，但你自己要留着以备后续操作。
- **核对 `created` 与入参条数**。不相等时脚本 stderr 会告警（`⚠️ 只新增了 N/M 条`）；这时用 `listRecords` 核对实际状态，**别直接当成全部写入成功**，并明确告诉用户「有 N 条没写进去」，不要只说「新增成功」。
- **500 / 503 后重试前，先用 `listRecords` 确认是不是已经写进去了**，避免写重。
- 写错了只能用 `deleteRecords` 删掉重写（不进撤销栈）。
- 成功后告诉用户加了几行、加进哪张表。不要声称写成功了，除非返回 `errcode: 200`。

### 常见错误

| errmsg 关键词 | 原因 | 怎么办 |
|---|---|---|
| `缺少 tableId` / `缺少 records（非空数组）` / `必须是对象` / `的 fields 必须是非空对象`（本地预检） | 入参形状不对 | 照提示补全；`fields` 的 key 用字段名 |
| `不该带 recordId`（本地预检）/ `新增记录不接受 recordId` | 拿 create 去改已有行 | 改已有行用 `updateRecords`；真要新增就去掉 `recordId` |
| `Too many cells in one call: X > Y` | 单元格数超上限 | 分批写，每批核对 `created` |
| `是附件列，值必须是 [{"name": ..., "token": ...}] 或 null` | 往附件列写了 URL 等其它形状 | 附件列先不写，建完行用 `uploadAttachment` 传图 |
| `Attachment(token) not found` | `[{name, token}]` 里的 token 不存在 | token 从 `uploadAttachment` 响应或 `listRecords` 的附件对象里取 |
| 字段名对不上 / 类型不匹配的 400 | 字段名与表里不一致；`typecast: false` 时值类型不对 | 用 `listFields` 核对字段名与类型；或去掉 `typecast: false` |
| `No access to table` / `Missing permission record\|create` | 表不在你团队里，或没有新增权限 | 换表，或找表的所有者 |
| `Table not found` | `tableId` 写错，或表已被删除 | 重新从列表接口取 |
| 500 / 503 | 服务端异常 / 数据库暂不可用 | **先用 `listRecords` 确认是否已写入**，再决定是否重试 |

### 示例

**1. 批量加多行（字符串会被 typecast 转成数字）**
```json
{"tableId": "tblXXXXXXXX", "records": [
  {"fields": {"商品标题": "无线充电器", "价格": "25.99", "状态": "待评估"}},
  {"fields": {"商品标题": "手机支架", "价格": "8.50"}}
]}
```

**2. 只填部分字段，图片列写外链**
```json
{"tableId": "tblXXXXXXXX", "records": [{"fields": {"商品标题": "无线耳机", "主图": "https://example.com/a.jpg"}}]}
```
（没给的字段留空；`主图` 须是 `listFields` 报成 `image` 的列。）

**3. 严格类型，不做自动转换**
```json
{"tableId": "tblXXXXXXXX", "typecast": false, "records": [{"fields": {"价格": 25.99}}]}
```

## updateRecords —— 批量改已有行的单元格（只改传了的字段）

**何时用 / 不该用**：
- 用：把分析/生成结果回写到表里；批量修正某几列的值；改某一格（见下「改某一格的标准做法」）。
- 加新行 / 往表里加数据 → `createRecords`。本操作**只改已有行**，`recordId` 必须已存在。
- 删记录 → `deleteRecords`。改**表结构**（加列/删列）→ `addFields` / `deleteFields`（见 `references/fields.md`）。
- 往附件列**追加**新图 → `uploadAttachment`（见 `references/attachment.md`），不是本操作。

**调用**：`python scripts/smart_table.py updateRecords '<JSON>'`

### 参数

| 参数 | 类型 | 必填 | 默认 | 约束 | 说明 |
|---|---|---|---|---|---|
| tableId | string | **是** | - | 以 `tbl` 开头 | 从列表接口的 `tables[].tableId` 取，不是 `notebookId` |
| records | array[object] | **是** | - | 非空数组 | 要改的记录，每项 `{recordId, fields}` |
| records[].recordId | string | 是 | - | 以 `rec` 开头，**必须已存在** | 从 `listRecords` / `createRecords` 的返回取 |
| records[].fields | object | 是 | - | 非空对象 | key 是**字段名**，value 是新值。**只包含你要改的字段** |
| typecast | boolean | 否 | **true** | - | 自动把值转成字段该有的类型 |

只暴露批量形式：单条就是 `records` 里只放一项。同理**没有单独的「改单元格」接口**：改一格就是 `records` 里一项、`fields` 里一个字段。

### 响应

| 字段 | 类型 | 说明 |
|---|---|---|
| updated | integer | 实际更新的记录数。**必须与入参条数比对**（见下） |
| records | array | 更新**后**的记录 `{recordId, fields}`，用来核对最终值；开了 `typecast` 时以这里为准 |

响应过大时脚本 stdout 只打摘要（`updated` + 前 3 条更新后的记录）。

### 语义与坑

**PATCH 语义：`fields` 里没出现的字段不会被改动**。两个引擎都核对过代码：V1 的 UPDATE 列清单是从传入的 key 推出来的，没传的字段不出现在语句里；V2 遍历表字段时跳过未提供的，写入层给每列带「是否提供」标志位，没提供就保留原值。
- ⚠️ **所以不要「读整行 → 改一个值 → 发整行」**。那样会把每个单元格都重写一遍（`__last_modified_time` 等都会变），且 `typecast` 有机会改动你本没打算碰的值。不要为了「保险」整行回发。

**清空单元格：传 `null`，不要传 `""`**。
- `null`：两个引擎都是清空。`notNull` 字段会拒绝并报 `validation.field.not_null`。
- `""`：两个引擎**不一致**，文本字段上 V1 会把空串/纯空白转成 `null`（等于清空），V2 老实存一个空字符串。所以一律用 `null`。
- **省略某个 key 永远不等于清空**，它只是「不改这个字段」。

**失败整体回滚，但成功可能是「部分」的**。
- 整批在一个数据库事务里，任何校验或写入失败都会**整体回滚**：报错就意味着**一条都没改**，改完入参可以安全地整批重跑，不必担心「改了一半」。
- ⚠️ 反过来不成立：某个 `recordId` 已经不存在（比如被别人删了）时，那几条会被**静默跳过**，接口仍然返回 `errcode: 200`，只是 `updated` 和返回的 `records` 少几条。脚本此时会在 stderr 告警（`⚠️ 只更新了 N/M 条`）。
  （`recordId` **格式**不对时不一样：整批 400 `Invalid recordId`，一条都不改。）
- **每次都要比对 `updated` 与入参条数**。不相等就用 `listRecords` 查清那几条的状态再决定怎么办，**别把 200 直接当成「全改好了」**，并告诉用户「有 N 条没改到（记录可能已被删除）」。
- 不要声称改成功了，除非返回 `errcode: 200` **且** `updated` 等于入参条数。

**先读后写**。用 `listRecords` 拿到 `recordId` 和现有值，确认要改的是哪几行、哪几个字段，再写。改动前如需保留原值（撤销栈里没有），先读一份存下来。

**展示**：成功后告诉用户改了几条、改了哪些字段，并把返回的最终值念给用户核对（尤其开了 `typecast` 时）。报错时说明**没有任何改动生效**。

#### 改某一格的标准做法

用户说「把无线充电器的价格改成 199」「把第三行的状态改成已完成」时，固定两步：

1. **`listRecords` 用 `filter` 定位，拿 `recordId`**（见 `references/records-read.md`）。按主字段或用户给的值精确匹配，只取要看的列：
   ```json
   {"tableId": "tblXXXXXXXX", "fieldNames": ["商品标题", "价格"],
    "filter": {"conditions": [{"fieldName": "商品标题", "operator": "is", "value": "无线充电器"}]}}
   ```
   看 `total`：等于 1 才往下走；为 0 告诉用户没找到；**命中多条就把候选（主字段值 + 要改的列）列给用户挑，别替用户猜**。改错行是静默的，接口照样返回 200。
2. **`updateRecords` 只传那一个字段**：
   ```json
   {"tableId": "tblXXXXXXXX", "records": [{"recordId": "recAAAAAAAA", "fields": {"价格": 199}}]}
   ```
   这一行的其他字段都不会被动。核对 `updated` 是 1，把返回的最终值告诉用户。

⚠️ **「第 N 行」不可靠，一律按值定位**。`listRecords` 和本操作都不接受 `viewId`，返回的是**创建顺序**；用户在页面上看到的是视图行序（可能带排序/筛选），两者对不上。用户说「改第三行」时，先读回来按主字段的值找到那一条、用它的 `recordId`，匹配到多条就让用户挑。

### 常见错误

400 时整批事务已回滚、**一条都没改**，改完入参可整批重跑。

| errmsg 关键词 | 原因 | 怎么办 |
|---|---|---|
| `缺少 tableId` / `缺少 records（非空数组）` / `必须是对象` / `的 fields 必须是非空对象`（本地预检） | 入参形状不对 | 照提示补全；`fields` 的 key 用字段名 |
| `缺少 recordId（以 rec 开头）；这个接口不能新增行`（本地预检） | 拿 update 去新增 | 加新行用 `createRecords` |
| `必须是记录 id（以 rec 开头）` | `recordId` 不是记录 id | 从 `listRecords` 重新取 |
| `Too many cells in one call: X > Y` | 单元格数超上限 | 分批改，每批核对 `updated` |
| `是附件列，值必须是 [{"name": ..., "token": ...}] 或 null` | 往附件列写了 URL 等其它形状 | 追加图片用 `uploadAttachment`；整格替换才写 `[{name, token}]` |
| `Attachment(token) not found` | token 不存在 | token 从 `uploadAttachment` 响应或 `listRecords` 的附件对象里取 |
| `validation.field.not_null` | 对 `notNull` 字段传了 `null` | 这一列不能清空，给一个值 |
| 字段名对不上 / 类型不匹配的 400 | 字段名与表里不一致；`typecast: false` 时值类型不对 | 用 `listFields` 核对；或去掉 `typecast: false` |
| `No access to table` / `Missing permission record\|update` | 表不在你团队里，或没有更新权限 | 换表，或找表的所有者 |
| `Table not found` | `tableId` 写错，或表已被删除 | 重新从列表接口取 |
| 500 / 503 | 服务端异常 / 数据库暂不可用 | 可重试一次 / 稍后重试 |
| （errcode 200，stderr）`⚠️ 只更新了 N/M 条` | 差额是**已不存在的 recordId**，被静默跳过 | 用 `listRecords` 查清那几条，告诉用户有 N 条没改到 |
| `Invalid recordId in UpdateRecordsCommand` | 某个 `recordId` **格式就不对**（抄漏了字符、自己编的）；整批一条都没改 | `errmsg` 不点名是哪一个：用 `listRecords` 重新取 recordId，别自己拼 |

### 示例

**1. 改一条记录的两个字段**
```json
{"tableId": "tblXXXXXXXX", "records": [
  {"recordId": "recAAAAAAAA", "fields": {"状态": "已完成", "备注": "自动填充"}}
]}
```

**2. 清空一个单元格（传 `null`，不要 `""`）**
```json
{"tableId": "tblXXXXXXXX", "records": [{"recordId": "recAAAAAAAA", "fields": {"备注": null}}]}
```

**3. 批量回写分析结果（`评分` 是数字字段，字符串会被 typecast 转换）**
```json
{"tableId": "tblXXXXXXXX", "records": [
  {"recordId": "recAAAAAAAA", "fields": {"评分": "4.5"}},
  {"recordId": "recBBBBBBBB", "fields": {"评分": "3.8"}}
]}
```

## deleteRecords —— 按 recordId 批量删行（不可逆、全有全无）

**何时用 / 不该用**：
- 用：用户**明确要求**删掉指定的若干行；清理重复/失效数据，且已确认过要删哪些。
- 用户只是「觉得可能要删」→ 先用 `listRecords` 读出来给用户看，别删。
- 删整张表 → `deleteTable`（进回收站，见 `references/tables.md`）；清空全表数据但保留表 → 没有接口，请用户到页面上操作。用户说「清空表」「删掉这张表」时不要用本操作：它只删记录，表和列都还在。
- 只是要改值 → `updateRecords`。要删的是**列**（字段）不是行 → `deleteFields`（见 `references/fields.md`）。

**调用**：`python scripts/smart_table.py deleteRecords '<JSON>' --yes`（**必须带 `--yes`**，缺了拒绝执行，见下）

### 参数

| 参数 | 类型 | 必填 | 默认 | 约束 | 说明 |
|---|---|---|---|---|---|
| tableId | string | **是** | - | 以 `tbl` 开头 | 从列表接口的 `tables[].tableId` 取，不是 `notebookId` |
| recordIds | array[string] | **是** | - | 非空数组，每项以 `rec` 开头，**不能有重复** | 要删的记录 id，从 `listRecords` 取，**不要构造** |

### 响应

| 字段 | 类型 | 说明 |
|---|---|---|
| deleted | integer | 删掉的条数。因为是全有全无，成功时必然等于入参条数 |

上游批量删除的响应本身无法让调用方确认删了几条，这里显式给出条数，让调用方不必假设。响应很小，一般直接全量打印。

### 语义与坑

**两条必须先告知用户的语义**：
1. **物理硬删，不可逆**。数据进回收站，那是唯一副本；这套接口**不提供恢复**，也不进前端撤销栈。删错了只能到前端页面上看回收站还在不在。
2. **全有全无**。只要有一个 `recordId` 查不到，**整批抛错、一条都不删**，没有「跳过不存在的」这种语义。服务端删之前先确认每个 id 都存在，把「给了不存在的 id」变成一个能照着改的 400（列出缺失的 id，最多列 10 个），而不是删一半或抛一个带内部术语的 500。

**确认闸门（流程固定）**：
1. 用 `listRecords` 读出要删的行；
2. 向用户复述**表名 + 条数 + 每条的主字段内容**（附 `recordId`），明确说「不可逆」；
3. 拿到用户明确的「确认删除」；
4. 才加 `--yes` 调用。缺 `--yes` 时脚本不发请求，打印将要删除的表和条数后以 **exit code 2** 退出。

**失败意味着一条都没删**。不要为了「至少删掉能删的」而拆成单条重试，那正好绕过了全有全无这个保护。先查清哪个 id 不对，再整批重来。

- 脚本本地预检 id 前缀和重复项：重复项要去重后再调（全有全无语义下重复只会增加风险）。
- **单次有条数上限**，默认千级，可由运维调整；超了返回 400 并给出实际条数与上限。大批量分批删，**每批之间重新确认**。
- 没有「删除全部记录」的快捷方式，必须显式给出 id 列表。
- **500 / 503 不要盲目重试删除**，先用 `listRecords` 确认实际状态。
- 执行后说明删了几条、来自哪张表；报错时明确告知**没有任何记录被删除**。不要声称删掉了，除非返回 `errcode: 200`。

### 常见错误

400 时**一条都没删**。

| errmsg 关键词 | 原因 | 怎么办 |
|---|---|---|
| `缺少 tableId` / `缺少 recordIds（非空数组）`（本地预检） | 入参形状不对 | 照提示补全 |
| `recordIds 里有不合法的 id（须以 rec 开头）`（本地预检） | id 不是记录 id | 从 `listRecords` 重新取，不要构造 |
| `recordIds 里有重复项`（本地预检） | 有重复 id | 去重后再调 |
| `拒绝执行：删除不可逆`（本地，exit 2） | 没带 `--yes` | 先向用户复述表和条数、拿到明确确认，再加 `--yes` 重跑 |
| `Records not found in table ...: recXXX. Nothing was deleted` | 有 id 不存在（全有全无，整批没删） | 查清这些 id（可能已被删），去掉后**整批**重来，别拆单条 |
| `Too many records to delete in one call: X > Y` | 超单次条数上限 | 分批删，每批之间重新确认 |
| `No access to table` / `Missing permission record\|delete` | 表不在你团队里，或没有删除权限 | 换表，或找表的所有者 |
| `Table not found` | `tableId` 写错，或表已被删除 | 重新从列表接口取 |
| 500 / 503 | 服务端异常 / 数据库暂不可用 | **不要盲目重试**，先用 `listRecords` 确认实际状态 |

### 示例

**删两条记录（已向用户复述并拿到确认）**
```bash
python scripts/smart_table.py deleteRecords '{"tableId":"tblXXXXXXXX","recordIds":["recAAAAAAAA","recBBBBBBBB"]}' --yes
```
