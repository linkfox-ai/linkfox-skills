# 读记录

本文件覆盖 `listRecords` 一个操作：按 `tableId` 分页读记录，可以按条件筛行、按字段名取列。
字段一律**按名称**寻址，这套接口不暴露 `fldXXX` 这类内部字段 id。
空单元格、附件格的形状这两条读侧语义，写入前定位行时也要用到。

## listRecords —— 读一张表里的记录（筛行 + 分页 + 取列）

**何时用 / 不该用**：
- 用：拿表里的数据做分析、汇总、生成报告；改/删/传图之前先看现状、拿 `recordId`；看附件列里的图（取查看地址）。
- 手上只有表名没有 `tableId` → 先用 `listMyTables` / `listSharedTables`（见 `references/tables.md`）。
- 只想知道**有哪些列**（不要数据）→ 用 `listFields`（见 `references/fields.md`）。比读一行推字段可靠：空单元格整个不出现，空表更是什么都推不出来。
- 要改已有行 → `updateRecords`；要加新行 → `createRecords`（见 `references/records-write.md`）。
- 飞书/Lark 多维表格 → `lark-base`，不是同一个系统。

**调用**：`python scripts/smart_table.py listRecords '<JSON>'`

### 参数

| 参数 | 类型 | 必填 | 默认 | 约束 | 说明 |
|---|---|---|---|---|---|
| tableId | string | **是** | - | 以 `tbl` 开头 | 数据表 id。从 `listMyTables` / `listSharedTables` 的 `notebooks[].tables[].tableId` 或 `looseTables.tables[].tableId` 取，**不是**顶层的 `notebookId`（那是容器） |
| page | integer | 否 | 1 | ≥ 1 | 页码，从 1 起 |
| perPage | integer | 否 | 100 | 1–100 | 每页条数 |
| fieldNames | array[string] | 否 | - | **非空数组**，元素非空串 | 只取这些字段（按**名称**）。少取列就少烧 token，对 LLM 场景这是最值的一个参数 |
| filter | object | 否 | - | 见下 | **行筛选**。大表上定位数据的唯一可行手段 |
| cellFormat | string | 否 | `json` | `json` \| `text` | `json` 保留结构；`text` 是人可读字符串但丢结构 |
| ~~search~~ | - | - | - | **显式拒绝** | 传了直接 400。按关键词找行用 `filter` 的 `contains` |

**不接受**：`baseId` / `viewId` / `spaceId`（内部概念）、`fldXXX` 形式的字段 id。`orderBy` 暂未开放，**不能指定排序**，返回的是创建顺序。

**filter 的结构**：

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| conjunction | string | 否 | `and`（默认）/ `or`，所有条件共用这一个关系 |
| conditions | array | **是** | 1–20 条，**扁平数组、不支持嵌套分组** |
| conditions[].fieldName | string | 是 | 字段名（不是 `fldXXX`） |
| conditions[].operator | string | 是 | 见算子矩阵，必须与字段类型匹配 |
| conditions[].value | any | 随算子 | 形状见下 |

**算子矩阵**（按字段类型，用错会 400 并列出该字段可用的算子）：

| 字段类型 | 可用算子 |
|---|---|
| 单行文本 / 多行文本 | `is` `isNot` `contains` `doesNotContain` `isEmpty` `isNotEmpty` |
| 数字 / 评分 | `is` `isNot` `isGreater` `isGreaterEqual` `isLess` `isLessEqual` `isEmpty` `isNotEmpty` |
| 单选 | `is` `isNot` `isAnyOf` `isNoneOf` `isEmpty` `isNotEmpty` |
| 多选 | `hasAnyOf` `hasAllOf` `hasNoneOf` `isExactly` `isNotExactly` `isEmpty` `isNotEmpty` |
| 勾选 | **只有 `is`** |
| 日期 | `is` `isNot` `isBefore` `isAfter` `isOnOrBefore` `isOnOrAfter` `isWithIn` `isEmpty` `isNotEmpty` |

**value 的形状随算子变**：

| 算子 | value |
|---|---|
| `isEmpty` / `isNotEmpty` | **不传**（传了会 400） |
| `isAnyOf` `isNoneOf` `hasAnyOf` `hasAllOf` `hasNoneOf` `isExactly` `isNotExactly` | **数组**，不能空 |
| 其余 | **单个值**（字符串/数字/布尔），不能是数组 |

### 响应

| 字段 | 类型 | 说明 |
|---|---|---|
| total | integer | **筛选后的行数**（没传 `filter` 时就是全表行数），**不是本页条数**。据此判断要不要翻页 |
| perPage | integer | 每页条数（回显） |
| currentPage | integer | 当前页码（回显） |
| records | array | 每项 `{recordId, fields}` |
| records[].recordId | string | 以 `rec` 开头。改/删记录、往附件列传图都要用它 |
| records[].fields | object | key 是**字段名**，value 是单元格值。**空单元格的 key 整个不出现** |

```json
{"errcode": 200, "errmsg": "ok", "total": 128, "perPage": 2, "currentPage": 1,
 "records": [
   {"recordId": "recAAAAAAAA", "fields": {"商品标题": "无线充电器", "价格": 25.99, "状态": "已选中"}},
   {"recordId": "recBBBBBBBB", "fields": {"商品标题": "手机支架"}}
 ]}
```

响应过大时脚本 stdout 只打摘要：`total` / `perPage` / `currentPage`、记录数 + 前 3 条，以及**所有记录里出现过的字段名清单**。宽表/大表先看摘要，再用 `jq` 从落盘的 json 里按需抽字段，别让整份 JSON 进上下文。

**附件列（`type: attachment`）的取值**：`cellFormat: json`（默认）时是**对象数组**，一张图一项：

| 字段 | 说明 |
|---|---|
| id / name / token | 附件 id（`act` 开头）、文件名、存储 token。`token` 可复用，见下 |
| size / mimetype / width / height | 字节数、类型、像素宽高 |
| path | 存储内部路径，调用方用不上 |
| presignedUrl | **原图**查看地址 |
| smThumbnailUrl / lgThumbnailUrl | 小 / 大缩略图地址 |

```json
{"recordId": "recAAAAAAAA", "fields": {"商品图": [
  {"id": "actXXXX", "name": "a.jpg", "token": "xxxx", "size": 102400, "mimetype": "image/jpeg",
   "width": 800, "height": 800, "path": "table/xxxx",
   "presignedUrl": "https://...", "smThumbnailUrl": "https://...", "lgThumbnailUrl": "https://..."}
]}}
```

### 语义与坑

**空单元格会从 `fields` 里整个消失，不是 `null`**。上例第二条只有 `商品标题`：这**不代表**表里没有 `价格` / `状态` 列，而是那两格为空。
- 判空用 `key not in fields`，不要用 `fields[key] is None`；按 key 存在性判断「字段存在与否」会误判。
- 不要根据某一条记录的 key 集合推断表结构，不同记录的 key 集合可能不同。要知道有哪些列用 `listFields`。
- 附件格为空时同样**整个不出现**。
- 给用户展示时说明「空白单元格表示该格为空」。

**要确定性就显式传 `fieldNames`**。不传时服务端套用某个默认视图的隐藏列配置，返回哪些列调用方**无从知晓也关不掉**。

**`fieldNames` 不能传空数组**（会被拒）。底层 `projection: []` 的语义反直觉：它不是「不要字段」，而是「全部字段**且顺带关掉视图隐藏列**」，所以入口直接拒掉。不想筛列就整个不传这个参数。

**大表上必须用 `filter`，不要靠翻页找数据**。几万行的表 `perPage` 上限 100，要翻几百页，不可行。先用 `filter` 把范围缩到几条，再处理。
- `total` 跟着 `filter` 收窄：`filter` 同时喂给记录查询和计数查询，两边口径一致。
- 条件是**扁平数组 + 一个 `conjunction`**，最多 20 条，不支持 `(A or B) and C` 这种嵌套（嵌套树要理解 conjunction 的作用域，agent 极难一次拼对）。真需要时先用能表达的部分筛，再本地过滤。
- **三条「不会静默失效」的保证**：字段名不存在、算子与字段类型不匹配、value 形状不对，都会显式 400，并分别列出该表可用字段名、该字段可用算子、该传数组还是单值。上游默认是打日志然后跳过这个条件，那样调用方会拿着**未过滤的全表数据**当筛选结果用，比报错糟糕得多。
- 内部会把 `fieldName` 翻成 `fldXXX` 再下发。不翻的话 V2 引擎查不到会**静默丢掉该条件**，出现「V1 筛选正常、V2 返回全表但 total 是筛过的」这种分裂。所以字段名照 `listFields` 写准即可，不用也不能自己传 `fldXXX`。
- ⚠️ `contains` **只对文本字段有效**。数字字段上想「模糊找」不行，用范围算子（`isGreaterEqual` + `isLessEqual`）。
- 日期算子的 value 是 `{mode, timeZone, ...}` 对象，比其他类型复杂，不建议自己拼。按日期筛时优先用 `isEmpty` / `isNotEmpty`，或取回本地判断。

**按关键词找行用 `filter` 的 `contains`，不是 `search`**。`search` 被显式拒绝：底层要求关键词搜索同时给出字段键列表且是位置元组，「搜全部字段**且**过滤行」表达不出来，退化写法能搜到但**不过滤行数**，`total` 会变成未搜时的总数。`filter` 没这个问题。

**要定位某一行去改/删，靠 `filter` 不靠「第几行」**。返回顺序是创建顺序，与用户在页面上看到的视图顺序**不一定一致**（视图可能带排序/筛选），按位置取会操作错行。用 `filter` 精确匹配，拿 `total` 确认只命中一条，再用它的 `recordId`；命中多条就把候选列给用户挑。完整流程见 `references/records-write.md` 的「改某一格的标准做法」。

**翻页要稳**：大表分页读取期间有人改数据，行序可能变化。要求严格一致时缩小时间窗，或一次取完（`perPage` 100 内）。

**附件格的地址是临时的**：
- `presignedUrl` 是原图，`smThumbnailUrl` / `lgThumbnailUrl` 是小 / 大缩略图。
- ⚠️ 三个地址都是**临时签名地址**，最长约 **3 小时**有效（受签名角色会话时长截断，可能更短）。**不要存下来长期用**，要用时再调 `listRecords` **现取**。
- `presignedUrl` 在浏览器里直接打开是**下载**而不是预览，放进 `<img src>` 正常显示（详见 `references/attachment.md`）。
- `cellFormat: "text"` 时附件格是 `文件名 (token)`，多张用逗号拼接（如 `a.png (tokA),b.jpg (tokB)`），**没有任何地址**。要看图就用默认的 `json`。
- `token` 可复用：用 `updateRecords` 写 `[{name, token}]` 能把同一张图挂到别的格子，但那是**整格替换**（见 `references/records-write.md`）。
- 往附件列**放新图**用 `uploadAttachment`（见 `references/attachment.md`），不是 `updateRecords`。

**权限与副作用**：只能读**自己团队 base 内、且自己有读权限**的表。读取不写历史、不影响表的修改时间。

**展示**：少量数据（十几条内）直接列成表格；大量数据先给 `total`、列名和前几行样本，问用户要看什么。

### 常见错误

| errmsg 关键词 | 原因 | 怎么办 |
|---|---|---|
| `Missing required parameter: tableId`（本地预检） | 没给 `tableId` | 补上，以 `tbl` 开头 |
| `必须是表 id（以 tbl 开头）` | 把 `notebookId` 或别的 id 当成了 `tableId` | 回 `listMyTables` / `listSharedTables` 取 `tables[].tableId` |
| `字段 "..." 不存在。这张表的字段有：...` | `filter` 里字段名写错 | 照报错列出的字段名改 |
| `不支持算子` / `可用：...` | 算子与字段类型不匹配（常见：数字字段用了 `contains`） | 换成报错里列出的算子 |
| `时不要传 value` / `时必须传 value` / `value 必须是数组` / `value 不能是空数组` / `value 不能是数组` | value 形状与算子不符 | 按「value 的形状」那张表改 |
| `conditions 不能为空` | `filter.conditions` 是空数组 | 至少给一条；不筛就整个不传 `filter` |
| `不支持 search` | 传了 `search` | 改用 `filter` 的 `contains`。报错原文里「用 fieldNames 取列后自行过滤」是旧说法，`filter` 已可用 |
| 指向 `perPage` / `fieldNames` 的 400 | `perPage` 超 100，或 `fieldNames` 传了空数组 | `perPage` ≤ 100；不想筛列就别传 `fieldNames` |
| `No access to table` / `Missing permission` | 表不在你团队里，或你在这张表上没有读权限 | 换表，或找表的所有者 |
| `Table not found` | `tableId` 写错，或表已被删除 | 重新从列表接口取 |
| 500 / 503 | 服务端异常 / 数据库暂不可用 | 可重试一次 / 稍后重试 |

### 示例

**1. 只取两列、每页 50 条**
```json
{"tableId": "tblXXXXXXXX", "fieldNames": ["商品标题", "价格"], "perPage": 50}
```

**2. 按关键词 + 范围筛行（几万行的表就靠这个）**
```json
{"tableId": "tblXXXXXXXX", "fieldNames": ["商品标题", "价格", "状态"],
 "filter": {"conjunction": "and", "conditions": [
   {"fieldName": "商品标题", "operator": "contains", "value": "充电器"},
   {"fieldName": "价格", "operator": "isGreaterEqual", "value": 100},
   {"fieldName": "价格", "operator": "isLessEqual", "value": 500}
 ]}}
```

**3. 找空值的行（判空算子不传 value）**
```json
{"tableId": "tblXXXXXXXX", "filter": {"conditions": [{"fieldName": "状态", "operator": "isEmpty"}]}}
```
