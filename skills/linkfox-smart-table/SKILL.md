---
name: linkfox-smart-table
description: 读写智能表格（LinkFox 在线多维表格/数据表）的全部操作：找表（我创建的、共享给我的）、建多维表、加数据表、看表头、加列删列、查记录（筛选/分页/取列）、新增/修改/删除记录、往附件列传图片并取图片地址、建 AI 出图的附件列并触发生成、把工作流（自动化）登记到多维表、改触发表、解除关联。当用户提到智能表格、多维表格、数据表、我的表、共享给我的表、建表、加一张表、表头、有哪些列、加一列、删列、查表里的数据、筛选、找出满足条件的行、往表里加数据、新增记录、把结果写进表格、改表、更新记录、改某一格、删记录、把图片传到表格里、附件列、图片地址、AI 生成图片、AI 出图、用 AI 做场景图、批量生成商品图、给多维表加自动化、监听这张表、换触发表、解除工作流关联，以及 smart table, my tables, create table, list fields, add column, list records, filter rows, add records, update records, delete records, upload image to table, attachment url, AI image column, generate images, register workflow, trigger table 时触发此技能。功能索引在正文第一节，按操作读对应的 references/*.md。不适用：飞书/Lark 多维表格（走 lark-base）；把表格数据做成网页/看板（走 linkfox-smart-table-page）；新建/编辑工作流本身（在工作流侧做，本技能只负责把建好的流登记到多维表）。
---

# 智能表格（LinkFox 在线多维表格）

一条统一入口，18 个操作。**先在下面的功能索引里找到操作，再读它对应的 `references/*.md`**；参数、出参、坑点都在那里。

```bash
python scripts/smart_table.py <op> '<JSON 参数>' [--inline] [--yes]
```

`<op>` 用接口名（camelCase）；旧写法 `create-records` 这种也认。不带参数运行会打印全部操作。

## 功能索引

| 操作 | 用途 | 必填参数 | 最容易错的一点 | 细节 |
|---|---|---|---|---|
| `listMyTables` | 我创建的多维表和数据表 | 无 | 表在 `notebooks[].tables[]` **和** `looseTables.tables[]`，两处都要找；顶层 `notebookId` 不是 tableId | [tables.md](references/tables.md) |
| `listSharedTables` | 别人共享给我的表 | 无 | 出参同样两层；自己建的不在这里 | [tables.md](references/tables.md) |
| `createTable` | 新建多维表 + 一张数据表 | `name` | 建的是**容器**；已有多维表要加表用 `addTable`；首列不能是 checkbox / attachment | [tables.md](references/tables.md) |
| `addTable` | 往已有多维表里加数据表 | `notebookId`, `name` | 没有幂等键，超时重试前先 `listMyTables` 确认 | [tables.md](references/tables.md) |
| `listFields` | 看表头：字段名、类型、可选项 | `tableId` | **写数据前先调它**；别靠读一行记录推字段（空单元格整个不出现） | [fields.md](references/fields.md) |
| `addFields` | 追加新列（≤50）；附件列可带 `ai` 建成 AI 出图列 | `tableId`, `fields[]` | 重名直接 400；只能加，不能改列名/类型；`ai` 见 [ai.md](references/ai.md) | [fields.md](references/fields.md) |
| `deleteFields` | 按列名删整列（连数据） | `tableId`, `fieldNames`, `--yes` | 不可逆；传列名不是 fldXXX；先向用户复述要删哪几列 | [fields.md](references/fields.md) |
| `listRecords` | 读记录：筛选、分页、取列 | `tableId` | 空单元格整个不出现；大表用 `filter` 定位，`perPage` ≤100 | [records-read.md](references/records-read.md) |
| `createRecords` | 往已有表加新行 | `tableId`, `records[].fields` | 拿它去「改」会**多一行重复数据**；不收 recordId | [records-write.md](references/records-write.md) |
| `updateRecords` | 改已有行（只改传了的字段） | `tableId`, `records[].recordId`, `records[].fields` | 200 也要比对 `updated` 与入参条数：查不到的 id 被静默跳过 | [records-write.md](references/records-write.md) |
| `deleteRecords` | 按 recordId 删行 | `tableId`, `recordIds`, `--yes` | 物理硬删、全有全无：一个 id 不存在就一条都不删 | [records-write.md](references/records-write.md) |
| `uploadAttachment` | 往附件列一格追加一张图 | `tableId`, `recordId`, `fieldName`, `imageUrl`/`imagePath` 二选一 | 只追加、一次一张；同一格并发追加会丢图，要串行 | [attachment.md](references/attachment.md) |
| `fillAiField` | 触发一列 AI 出图（异步） | `tableId`, `fieldName` | **扣调用方积分**；默认只填空格，`mode: "all"` 会整格覆盖；单次 ≤50 行 / 整列 ≤100 行 | [ai.md](references/ai.md) |
| `getAiFillStatus` | 查 AI 出图进度与失败原因 | `tableId`, `taskId` | 一行最长约 10 分钟，隔 30~60 秒查一次；失败多半是那行没参考图 | [ai.md](references/ai.md) |
| `registerWorkflow` | 把建好的流登记到多维表 | `notebookId`, `flowId` | notebookId 取列表顶层 nbk；重复登记不改 tableId | [workflow.md](references/workflow.md) |
| `listWorkflows` | 查流挂在哪、由哪张表触发 | 无 | `tableId` 为 null = 不会触发；空列表 ≠ 流不存在 | [workflow.md](references/workflow.md) |
| `updateWorkflowTriggerTable` | 换触发表 / 解绑（传 null） | `flowId`, `tableId` | 200 + `status: not_found` = 什么都没改，别报成功 | [workflow.md](references/workflow.md) |
| `unregisterWorkflow` | 解除流与多维表的关联 | `flowId`, `--yes` | 不删流本身；只想暂停用 `updateWorkflowTriggerTable` 传 null | [workflow.md](references/workflow.md) |

## 核心链路

**只有表名、没有 tableId**：`listMyTables` → 找不到再 `listSharedTables`。两处都要在 `notebooks[].tables[]` 和 `looseTables.tables[]` 里找；同名多张就列给用户挑，别自己猜。

**建一张表并写数据**：`createTable`（只建结构，不收数据）→ 拿出参的 `tableId` → `createRecords` → 拿返回的 `recordId` 留着后续改删。已有多维表里再加一张用 `addTable`。

**改某一格**：`listRecords` 带 `filter` 按字段名定位，拿到 `recordId` → `updateRecords` 只传要改的那一个字段（其余字段原样保留）。命中多条就让用户挑，别按「第几行」定位。

**往附件列放图、再取图片地址**：没有附件列先 `addFields` 加一列 `type: "attachment"` → 行不存在先 `createRecords` → `uploadAttachment`（每次一张，串行）→ 要看图时 `listRecords` 取 `presignedUrl`（约 3 小时有效，现取不存）。

**AI 生成图片（如商品图 → 场景图）**：`addFields` 加一列 `type: "attachment"` 并带 `ai`（提示词 + 参考图来源列，模型不写用默认）→ 参考图列有图的行 → `fillAiField` 触发（**会扣用户积分，先说清楚**）→ 隔 30~60 秒 `getAiFillStatus` 查到结束 → `listRecords` 取图。接口建的 AI 列不会自动生成，只有 `fillAiField` 会。细节见 [ai.md](references/ai.md)。

**给多维表加自动化**：流本身在工作流侧建（本技能不建、不改、不删流）→ 拿到 `flowId` 后 `registerWorkflow` 挂到多维表 → 要监听某张表用 `updateWorkflowTriggerTable` 设触发表。

## 通用规则

1. **成功看 `errcode`，不看 HTTP 状态码**（恒为 200）。脚本遇到业务错误会在 stderr 打 `Business error: errcode=… errmsg=…`，**但退出码仍是 0** —— 别靠退出码判断成败。
2. **写操作成功也要核对条数**：`created` / `updated` / `deleted` 与入参条数不一致时，用 `listRecords` 查实际状态并如实告诉用户，别说「全部成功」。
3. **字段一律按名称寻址**，要与 `listFields` 返回的完全一致（含中英文、空格、大小写）。名字对不上会报错，不会自动建列。
4. **三种 id 别混**：`notebookId`（nbk，多维表容器）、`tableId`（tbl，数据表，在 `tables[]` 里）、`recordId`（rec，只从 `listRecords` / `createRecords` 的返回拿）。`flowId` 只从工作流侧或 `listWorkflows` 拿。**任何 id 都不要自己编**。
5. **新增 ≠ 修改**：表里还没有这一行用 `createRecords`，已有这一行用 `updateRecords`。拿不准先 `listRecords` 看一眼 —— 用错方向不会报错，只会多一行重复数据。
6. **不可逆操作**（`deleteFields` / `deleteRecords` / `unregisterWorkflow`）脚本要 `--yes` 才执行。加 `--yes` 之前先向用户复述要删/解除的具体对象并得到确认。
7. **写入不进撤销栈**：用户在页面上按 Ctrl+Z 撤不回来。写错了只能再改回去或删掉重写。
8. **报错时把 `errmsg` 原文转述给用户**（错误信息是按「调用方能照着改」写的），并说明这次有没有改动生效。
9. **范围**：只能看到、写到**调用方自己团队**里自己有权限的表；跨团队拿到的 tableId 会被拒（403 / 404）。身份由网关注入的头决定，请求体里的身份字段一律被忽略。

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
| 500 | 服务端异常（`errmsg` 已消毒） | **写操作重试前先用读接口确认是否已生效** —— `createTable` / `addTable` / `createRecords` 重试会建重 |
| 503 | 数据库暂不可用 | 稍后重试，写操作同样先确认状态 |

## 反馈

参见 [`references/feedback.md`](references/feedback.md)。`content` 里写清是哪个操作（如 `createRecords`）出的问题。
