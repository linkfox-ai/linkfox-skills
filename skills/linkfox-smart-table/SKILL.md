---
name: linkfox-smart-table
description: 读写智能表格（LinkFox 在线多维表格/数据表）的全部操作：找表（我创建的、共享给我的）、建多维表、加数据表、复制多维表（创建副本、按分享链接另存为副本）、删除多维表 / 数据表 / 多维表里的仪表盘、文件夹、页面、应用（移到回收站）、给它们重命名、看表头、加列删列、查记录（筛选/分页/取列）、新增/修改/删除记录、往附件列传图片并取图片地址、建 AI 出图的附件列并触发生成、查看工作流（自动化）挂在哪个多维表下、由哪张表触发。当用户提到智能表格、多维表格、数据表、我的表、共享给我的表、建表、加一张表、复制多维表、创建副本、另存为副本、把别人分享的表存一份、删除多维表、删除数据表、删表、删除仪表盘、删除文件夹、删除页面、删除应用、移到回收站、重命名多维表、改多维表名、重命名数据表、改表名、重命名仪表盘、重命名文件夹、重命名页面、重命名应用、改名、表头、有哪些列、加一列、删列、查表里的数据、筛选、找出满足条件的行、往表里加数据、新增记录、把结果写进表格、改表、更新记录、改某一格、删记录、把图片传到表格里、附件列、图片地址、AI 生成图片、AI 出图、用 AI 做场景图、批量生成商品图、这张表挂了哪些自动化、自动化为什么没触发，以及 smart table, my tables, create table, copy notebook, duplicate table, save shared table as copy, delete table, delete notebook, move to trash, rename table, rename notebook, list fields, add column, list records, filter rows, add records, update records, delete records, upload image to table, attachment url, AI image column, generate images, list workflows 时触发此技能。功能索引在正文第一节，按操作读对应的 references/*.md。不适用：飞书/Lark 多维表格（走 lark-base）；把表格数据做成网页/看板（走 linkfox-smart-table-page；本技能说的「删除页面」是删多维表里已有的页面节点）；从回收站还原、改列名 / 改列类型、改图标（只能在页面上操作）；新建/编辑/停用/删除工作流、给多维表加自动化、换触发表（都在工作流侧做，保存后自动同步到多维表；本技能只能查看关联）。
---

# 智能表格（LinkFox 在线多维表格）

一条统一入口，22 个操作。**先在下面的功能索引里找到操作，再读它对应的 `references/*.md`**；参数、出参、坑点都在那里。

```bash
python scripts/smart_table.py <op> '<JSON 参数>' [--inline] [--yes]
```

`<op>` 用接口名（camelCase）；旧写法 `create-records` 这种也认。不带参数运行会打印全部操作。

## 功能索引

| 操作 | 用途 | 必填参数 | 最容易错的一点 | 细节 |
|---|---|---|---|---|
| `listMyTables` | 我创建的多维表和数据表 | 无（可选 `notebookId` 只看一个） | 表在 `notebooks[].tables[]` **和** `looseTables.tables[]`，两处都要找；顶层 `notebookId` 不是 tableId；传 `notebookId` 而它是共享来的会 404 并提示改用 `listSharedTables` | [tables.md](references/tables.md) |
| `listSharedTables` | 别人共享给我的表 | 无（可选 `notebookId` 只看一个） | 出参同样两层；自己建的不在这里（传自己建的 `notebookId` 会 404 并提示改用 `listMyTables`） | [tables.md](references/tables.md) |
| `createTable` | 新建多维表 + 一张数据表 | `name` | 建的是**容器**；已有多维表要加表用 `addTable`；首列不能是 checkbox / attachment / lookup | [tables.md](references/tables.md) |
| `addTable` | 往已有多维表里加数据表 | `notebookId`, `name` | 没有幂等键，超时重试前先 `listMyTables` 确认 | [tables.md](references/tables.md) |
| `copyNotebook` | 复制整个多维表：创建副本 / 按分享链接另存为副本 | `notebookId` 或 `shareUrl` 二选一 | 只能复制自己创建或协作的；分享链接必须是「可另存为副本」档；慢，超时先 `listMyTables` 确认，再用**同一个** `requestKey` 重试 | [tables.md](references/tables.md) |
| `deleteNotebook` | 删整个多维表（连同里面的数据表、仪表盘、文件夹、页面、应用），进回收站 | `notebookId`, `--yes` | 只有创建者能删，协作者一律 404；先 `listMyTables` 把会一起删掉的内容复述给用户 | [tables.md](references/tables.md) |
| `deleteTable` | 删一张数据表（连记录、字段、视图），进回收站 | `tableId`, `--yes` | 多维表的最后一张删不了（400）；只有表或多维表的创建者能删（403）；以它为触发表的自动化会被置空 | [tables.md](references/tables.md) |
| `deleteNotebookItem` | 删多维表里的仪表盘 / 文件夹 / 页面 / 应用，进回收站 | `itemType`, `itemId`, `--yes` | `itemId` 只从列表的 `dashboards` / `folders` / `pages` / `applications` 拿，`itemType` 取它所在的数组；**删文件夹连里面的表一起删** | [tables.md](references/tables.md) |
| `renameNotebook` | 改多维表的名字 | `notebookId`, `name` | 只有创建者能改（协作者 404）；同一创建者名下重名 400（回收站里的也算）；**里面数据表的名字不跟着变** | [tables.md](references/tables.md) |
| `renameTable` | 改一张数据表的名字 | `tableId`, `name` | 只有表或多维表的创建者能改（403）；允许重名，一律按 `tableId` 改；**多维表名不跟着变**；改不了列名 | [tables.md](references/tables.md) |
| `renameNotebookItem` | 改多维表里的仪表盘 / 文件夹 / 页面 / 应用的名字 | `itemType`, `itemId`, `name` | 创建者或「可编辑」能改（「可查看」404）；只有文件夹在同一多维表内不能重名；`itemId` / `itemType` 规则同 `deleteNotebookItem` | [tables.md](references/tables.md) |
| `listFields` | 看表头：字段名、类型、可选项 | `tableId` | **写数据前先调它**；别靠读一行记录推字段（空单元格整个不出现） | [fields.md](references/fields.md) |
| `addFields` | 追加新列（≤50）；附件列可带 `ai` 建成 AI 出图列；`type: "lookup"` 建查找引用列 | `tableId`, `fields[]` | 重名直接 400；只能加，不能改列名/类型；`ai` 见 [ai.md](references/ai.md)；查找引用只能引用自己创建的表 | [fields.md](references/fields.md) |
| `deleteFields` | 按列名删整列（连数据） | `tableId`, `fieldNames`, `--yes` | 不可逆；传列名不是 fldXXX；先向用户复述要删哪几列 | [fields.md](references/fields.md) |
| `listRecords` | 读记录：筛选、分页、取列 | `tableId` | 空单元格整个不出现；大表用 `filter` 定位，`perPage` ≤100 | [records-read.md](references/records-read.md) |
| `createRecords` | 往已有表加新行 | `tableId`, `records[].fields` | 拿它去「改」会**多一行重复数据**；不收 recordId | [records-write.md](references/records-write.md) |
| `updateRecords` | 改已有行（只改传了的字段） | `tableId`, `records[].recordId`, `records[].fields` | 200 也要比对 `updated` 与入参条数：查不到的 id 被静默跳过 | [records-write.md](references/records-write.md) |
| `deleteRecords` | 按 recordId 删行 | `tableId`, `recordIds`, `--yes` | 物理硬删、全有全无：一个 id 不存在就一条都不删 | [records-write.md](references/records-write.md) |
| `uploadAttachment` | 往附件列一格追加一张图 | `tableId`, `recordId`, `fieldName`, `imageUrl`/`imagePath` 二选一 | 只追加、一次一张；同一格并发追加会丢图，要串行 | [attachment.md](references/attachment.md) |
| `fillAiField` | 触发一列 AI 出图（异步） | `tableId`, `fieldName` | **扣调用方积分**；默认只填空格，`mode: "all"` 会整格覆盖；单次 ≤50 行 / 整列 ≤100 行 | [ai.md](references/ai.md) |
| `getAiFillStatus` | 查 AI 出图进度与失败原因 | `tableId`, `taskId` | 一行最长约 10 分钟，隔 30~60 秒查一次；失败多半是提示词引用的列为空，或参考图用不了 | [ai.md](references/ai.md) |
| `listWorkflows` | 查流挂在哪、由哪张表触发（只读） | 无 | `tableId` 为 null = 不会触发；空列表 ≠ 流不存在；关联只能看，改要到工作流侧 | [workflow.md](references/workflow.md) |

## 核心链路

**只有表名、没有 tableId**：`listMyTables` → 找不到再 `listSharedTables`。两处都要在 `notebooks[].tables[]` 和 `looseTables.tables[]` 里找；同名多张就列给用户挑，别自己猜。

**建一张表并写数据**：`createTable`（只建结构，不收数据）→ 拿出参的 `tableId` → `createRecords` → 拿返回的 `recordId` 留着后续改删。已有多维表里再加一张用 `addTable`。

**复制一个多维表（创建副本 / 另存为副本）**：自己能看到的多维表 → `listMyTables` / `listSharedTables` 拿 `notebookId` → `copyNotebook`；别人发来的分享链接 → 直接 `copyNotebook` 传 `shareUrl`（设了密码再带 `password`）。⚠️ 只有 `/share/shr…` 才是分享链接；用户给的是数据表页面地址（`/table/<baseId>/<tableId>`）时**不要**塞进 `shareUrl`，按地址里的 `tableId` 在 `listMyTables` / `listSharedTables` 里找到它的 `notebookId` 再复制。副本连同数据表、仪表盘、自动化、页面一起复制，归调用者本人。出参 `tables[].tableId` 全是**新的**，后续读写用它们，别用源表的 id。超时先 `listMyTables` 看副本在不在，再决定要不要重试。

**删除多维表 / 数据表 / 仪表盘 / 文件夹 / 页面 / 应用**：`listMyTables`（找不到再 `listSharedTables`）定位要删的对象和它的 id → 向用户复述**要删的是哪个、会连带删掉什么**（删多维表 = 里面全部内容；删文件夹 = 各数组里 `folderId` 指向它的那些）→ 用户明确同意后 `deleteNotebook` / `deleteTable` / `deleteNotebookItem` 加 `--yes`。一律进回收站，**还原只能由用户在网页左侧栏底部的「回收站」里操作**，本技能没有还原接口；**在回收站里放满 30 天会被自动彻底删除、找不回来**，跟用户说「能还原」时要带上这一句。报 400「关联列」时什么都没删：把报错里列出的列告诉用户，同意后才带 `allowBreakingLinks: true` 重试（那些列会变成单行文本，还原也转不回来）。这里的「页面」指多维表里的页面节点，与 `linkfox-smart-table-page` 技能无关。一次删一个，没有批量。

**重命名多维表 / 数据表 / 仪表盘 / 文件夹 / 页面 / 应用**：`listMyTables`（找不到再 `listSharedTables`）按名字找到对象和它的 id（数据表、仪表盘、页面、应用都可能重名，命中多个就列给用户挑，**一律按 id 改**）→ 多维表用 `renameNotebook`，数据表用 `renameTable`，其余四类用 `renameNotebookItem`。⚠️ **多维表名和里面数据表的名字互相独立**，改一个不会动另一个；`createTable` 建出来时两者同名，用户说「把这个表改成 X」而多维表与表同名时，先问清改哪一个（都要改就分别调）。改名可逆，不用 `--yes`；改成原名直接回成功，超时用同样的参数重试是安全的。报 400 重名（多维表在同一创建者名下、文件夹在同一多维表内不能重名）时什么都没改：告诉用户、请他换个名字，**不要自己加后缀重试**。只能改名字：图标、列名都改不了（列名只能在页面上改）。

**改某一格**：`listRecords` 带 `filter` 按字段名定位，拿到 `recordId` → `updateRecords` 只传要改的那一个字段（其余字段原样保留）。命中多条就让用户挑，别按「第几行」定位。

**往附件列放图、再取图片地址**：没有附件列先 `addFields` 加一列 `type: "attachment"` → 行不存在先 `createRecords` → `uploadAttachment`（每次一张，串行）→ 要看图时 `listRecords` 取 `presignedUrl`（约 3 小时有效，现取不存）。

**AI 生成图片（如商品图 → 场景图）**：`addFields` 加一列 `type: "attachment"` 并带 `ai`（提示词，可选参考图来源列，模型不写用默认）→ 配了参考列的话先把图传好 → `fillAiField` 触发（**会扣用户积分，先说清楚**）→ 隔 30~60 秒 `getAiFillStatus` 查到结束 → `listRecords` 取图。接口建的 AI 列不会自动生成，只有 `fillAiField` 会。细节见 [ai.md](references/ai.md)。

**从另一张表取值（查找引用，如订单表按 SKU 取库存）**：`listMyTables` 拿被引用表的 `tableId`（只能是自己创建的）→ 对两张表各 `listFields` 确认列名 → `addFields` 加一列 `type: "lookup"`，`lookup` 里写取哪列、`conditions`（`fieldName` 写对方表的列，`valueFromField` 写本表的列）、`computeMode`。这一列是算出来的，写数据时跳过。细节见 [fields.md](references/fields.md) § 查找引用。

**自动化（工作流）**：建流、选触发表、换表、停用、删流**全部在工作流侧做**，工作流侧保存时会自动把关联同步到多维表。本技能**刻意不提供**登记 / 换触发表 / 解除这类写操作——只改多维表这一侧、工作流侧的订阅不跟着变，两边对不上，自动化会静默不触发。这里只能用 `listWorkflows` 查看关联；`tableId` 为 null 或该有的流不在列表里，让用户到工作流侧重新选触发表并保存。

## 通用规则

1. **成功看 `errcode`，不看 HTTP 状态码**（恒为 200）。脚本遇到业务错误会在 stderr 打 `Business error: errcode=… errmsg=…`，**但退出码仍是 0** —— 别靠退出码判断成败。
2. **写操作成功也要核对条数**：`created` / `updated` / `deleted` 与入参条数不一致时，用 `listRecords` 查实际状态并如实告诉用户，别说「全部成功」。
3. **字段一律按名称寻址**，要与 `listFields` 返回的完全一致（含中英文、空格、大小写）。名字对不上会报错，不会自动建列。
4. **三种 id 别混**：`notebookId`（nbk，多维表容器）、`tableId`（tbl，数据表，在 `tables[]` 里）、`recordId`（rec，只从 `listRecords` / `createRecords` 的返回拿）。`flowId` 只从工作流侧或 `listWorkflows` 拿；仪表盘 / 文件夹 / 页面 / 应用的 `itemId` 只从列表接口里那个多维表的 `dashboards` / `folders` / `pages` / `applications` 拿。**任何 id 都不要自己编**。
5. **新增 ≠ 修改**：表里还没有这一行用 `createRecords`，已有这一行用 `updateRecords`。拿不准先 `listRecords` 看一眼 —— 用错方向不会报错，只会多一行重复数据。
6. **删除类操作**（`deleteFields` / `deleteRecords` / `deleteNotebook` / `deleteTable` / `deleteNotebookItem`）脚本要 `--yes` 才执行。加 `--yes` 之前先向用户复述要删的具体对象（以及会连带删掉的东西）并得到确认。后三个进回收站、能在页面上还原；这不是跳过确认的理由。
7. **写入不进撤销栈**：用户在页面上按 Ctrl+Z 撤不回来。写错了只能再改回去或删掉重写。
8. **报错时把 `errmsg` 原文转述给用户**（错误信息是按「调用方能照着改」写的），并说明这次有没有改动生效。
9. **范围**：只能看到、写到**调用方自己团队**里自己有权限的表；跨团队拿到的 tableId 会被拒（403 / 404）。身份由网关注入的头决定，请求体里的身份字段一律被忽略。唯一的例外是 `copyNotebook` 传 `shareUrl`：分享链接可以来自别的团队，但副本仍然只落在调用方自己团队里。

## 调用与输出

- 网关地址取环境变量 `LINKFOX_TOOL_GATEWAY`（缺省正式地址）；API Key 取 `LINKFOX_AGENT_API_KEY`（或 `LINKFOXAGENT_API_KEY`），放在 `Authorization` 头里，**值就是 key 本身，不带 `Bearer`**。脚本已处理好，直接调脚本即可。
- **始终**把完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-smart-table-<操作>-<timestamp>.json`（`<session>` 取自 `SESSION_ID`；**禁止写 /tmp**）。
- 响应 ≤ 8 KB：落盘后把完整 JSON 打印到 stdout；更大时只打摘要。`--inline` 强制全量打印。
- 字段名或值含中文时，JSON 参数用单引号整体包住传给脚本；不要直接 curl 内联中文。
- 不计费（读写的是自己团队的数据）。

**通用错误码**（各操作特有的错误见对应 reference 的「常见错误」）：

| errcode | 含义 | 怎么办 |
|---|---|---|
| 400 | 入参不对 | 按 `errmsg` 改 |
| 401 | 身份未确立：网关没注入身份头，或该成员在用户中心查不到 | 检查 API Key 配置，换参数解决不了 |
| 403 | 无权：表不在你团队、你没有这个动作的权限 | 换表，或请表的所有者授权 |
| 404 | 多维表/表/记录不存在，或不在你团队里 | 用 `listMyTables` / `listSharedTables` 重新拿 id |
| 409 | 同一个 `requestKey` 的请求还在进行；`copyNotebook` 还表示你有一个复制没跑完；三个删除操作（`deleteNotebook` / `deleteTable` / `deleteNotebookItem`）表示同一个多维表里有另一个删除还在进行（这次什么都没删） | 等一会儿，先用读接口（删除用 `listMyTables`）确认上一次是否已生效，**别换 key 重发** |
| 500 | 服务端异常（`errmsg` 已消毒） | **写操作重试前先用读接口确认是否已生效** —— `createTable` / `addTable` / `createRecords` 重试会建重；三个删除操作重试是安全的（已进回收站的回 `alreadyInTrash`）；三个改名操作用同样的参数重试也是安全的（改成原名直接回成功） |
| 503 | 数据库暂不可用 | 稍后重试，写操作同样先确认状态 |

## 反馈

参见 [`references/feedback.md`](references/feedback.md)。`content` 里写清是哪个操作（如 `createRecords`）出的问题。
