# 表与多维表：listMyTables / listSharedTables / createTable / addTable

本文件覆盖 4 个操作：列出我的表（`listMyTables`）、列出共享给我的表（`listSharedTables`）、新建多维表并建第一张表（`createTable`）、往已有多维表里加表（`addTable`）。
共用概念「两层出参」：表挂在两种容器下——多维表（`notebooks[].tables[]`）和不在任何多维表里的散表（`looseTables.tables[]`），找表时两层都要看；容器层的 `notebookId` 是多维表 ID，不是 tableId。

## listMyTables —— 列出当前团队里我创建的多维表及其下的数据表

**何时用 / 不该用**：这是拿 `tableId` 的**入口**——读/改/删记录、看字段都要 `tableId`，而它只能从这里或 `listSharedTables` 拿到；用户说「读一下我那张 XX 表」却没给 tableId 时，先用它按表名找。要往已有多维表里加表但手上没有 `notebookId` 时也用它。
不该用：别人共享给我的 → `listSharedTables`（见本文件）；读表里的数据 → `listRecords`（见 `references/records-read.md`）；新建多维表 + 一张表 → `createTable`、往**已有**多维表里加一张表 → `addTable`（都见本文件）；飞书/Lark 多维表格不是同一个系统 → `lark-base`。

**调用**：`python scripts/smart_table.py listMyTables '<JSON>'`（无参等价于 `'{}'`）

### 参数

全部可选，`{}` 即取默认第一页。

| 参数 | 类型 | 必填 | 默认 | 约束 | 说明 |
|---|---|---|---|---|---|
| page | integer | 否 | 1 | ≥ 1 | 页码，从 1 起 |
| perPage | integer | 否 | 100 | 1–100 | 每页条数，**限的是多维表（容器）数**，不是数据表数 |

**不接受** `baseId` / `spaceId` / `viewId` / `userId` / `teamId` 等内部或身份概念，传了会被静默忽略。调用者身份只由网关注入的头推导（memberId → 用户 + 团队），请求体里的身份字段一律忽略，无法指定「看别人的表」。

### 响应

⚠️ 出参是两层的：顶层是 `notebooks`（多维表），**不是** `tables`。数据表只能存在于多维表之下，所以「列出我的表」实际返回「我的多维表，各自带着里面的数据表」。分页落在**容器**上。

| 字段 | 类型 | 说明 |
|---|---|---|
| total | integer | **多维表总数**（不是数据表总数，也不是本页条数） |
| perPage | integer | 每页条数（回显），限制的是容器数 |
| currentPage | integer | 当前页码（回显） |
| notebooks | array | 多维表列表，每项见「多维表对象」 |
| looseTables | object | 不属于任何多维表的散表，**为空时整个字段不出现**，见「looseTables」 |

多维表对象（`notebooks[]`）：

| 字段 | 类型 | 说明 |
|---|---|---|
| notebookId | string | 多维表 id，`nbk` 开头。往它里面加表（`addTable`）要用它；**不是 tableId** |
| name | string | 多维表名 |
| icon | string | 图标（emoji），没设置时字段不出现 |
| url | string | 可点开的页面地址。服务端未配置站点地址时字段不出现——**不要自己拼** |
| createdTime | string | 创建时间，ISO 8601 |
| tables | array | 这个多维表里的数据表，每项见「数据表对象」。**不分页**，有多少返回多少 |

数据表对象（`notebooks[].tables[]` 与 `looseTables.tables[]` 同一形状）：

| 字段 | 类型 | 说明 |
|---|---|---|
| tableId | string | 数据表 id，`tbl` 开头。后续读/改/删记录都用它 |
| name | string | 表名，**可能重复**（建表不去重） |
| icon | string | 图标（emoji），没设置时字段不出现 |
| refKey | string | 稳定引用键，恒有值。复制多维表时副本里的表拿到新 `tableId`，但 `refKey` **不变**（恒等于血缘里最早那张表的 id）；没被复制过的表就等于自己的 `tableId`。⚠️ **只在同一个多维表内唯一**，跨容器同一个 `refKey` 对应不同的表；读写记录仍然用 `tableId` |
| url | string | 可点开的页面地址，没有时同样不要自己拼 |
| createdTime | string | 建表时间，ISO 8601 |

looseTables：

| 字段 | 类型 | 说明 |
|---|---|---|
| total | integer | 散表总数 |
| tables | array | 散表列表，形状同「数据表对象」 |

**不返回** `baseId`（内部概念）、`createdBy`（内部用户 id，对调用方无意义）。

### 语义与坑

```
notebooks[]                  ← 多维表（容器），分页落在这一层，total 是容器数
  ├─ notebookId (nbk...)     ← 往这个容器里加数据表要用它
  ├─ name / url / createdTime
  └─ tables[]                ← 这个容器里的数据表（不分页）
       ├─ tableId (tbl...)   ← 读/改/删记录用它
       └─ name / url / createdTime
looseTables                  ← 不属于任何多维表的散表，为空时整个字段不出现
  ├─ total
  └─ tables[]                ← 形状同上
```

- ⚠️ **按表名找 `tableId` 必须遍历两处**：所有 `notebooks[].tables[]`，**以及** `looseTables.tables[]`。只扫顶层什么也找不到——顶层的 id 是 `nbk` 开头的容器 id，拿它去读记录会因为前缀校验直接 400。
- **表名可能重复**：建表不去重，同名表可以有多张，还可能分散在**不同的多维表**里。按名字匹配到多条时，把候选（**所在多维表** + 表名 + 创建时间 + 链接）列给用户挑，不要替用户猜——带上容器名很重要，那往往是用户区分它们的唯一线索。
- **列表为空 ≠ 出错**：团队还没有任何多维表时正常返回 `total: 0`、`notebooks: []`（`looseTables` 也不出现）。
- **`total` 是多维表数，不是数据表数**，翻页翻的也是容器。跟用户说「你有 N 张表」之前先自己数一遍 `tables`，别直接念 `total`。
- **容器内的数据表不分页**：`perPage` 只限容器数，一个容器里有多少表就全部返回。
- **`tables: []` 的容器不一定是空的**：一个多维表下面可能同时有数据表和仪表盘，这套接口只能操作数据、只列数据表，不列仪表盘。别告诉用户「这个项目是空的」。
- **`looseTables` 不出现是正常的**，绝大多数团队都这样。出现了说明有表不在任何多维表下面（早期建的、或被人从容器里搬出来的），它们照样能读写。它存在的意义是**防静默消失**：只列容器的话这些表会整个不可见，调用方会以为表被删了。
- **只含当前团队**：memberId 编码了「谁 + 哪个团队」，跨团队创建的表看不到。
- **只含我创建的**：按**容器的创建者**判。别人共享给我的在 `listSharedTables`，两个列表互不重叠。
- **`refKey` ≠ `tableId`**：副本容器里的表 `refKey` 是源头那张表的 id，所以**别拿 `refKey` 当 tableId 去读写**，也别跨多维表按 `refKey` 认表（它只在同一个多维表内唯一）。它是给「跨副本认出是同一张表」用的。
- **零参数可用**：身份由网关注入的头决定，不需要（也无法）指定看谁的表。
- **顺带拿到 `notebookId`**：用户接着说「在这个项目里再加一张表」时，用它调 `addTable`。

**展示规则**：
- **按多维表分组展示**，这也是用户在页面上看到的样子：多维表名下面列它的数据表（表名 + 创建时间 + 链接）。
- `tableId` / `notebookId` 是给后续接口用的，除非用户要，不必念给用户听。
- 用户要「打开某张表」给那张表的 `url`；要「打开那个项目」给容器的 `url`。**没有 `url` 字段时不要自己拼**（服务端未配置站点地址，拼出来是错链接）。
- 有 `looseTables` 时单独列一组，可以说「这些表不在任何多维表下面」，不必解释为什么。
- 空列表时说明「当前团队里没有你创建的多维表」，并提示共享给你的要用 `listSharedTables` 查。

### 常见错误

| errmsg 关键词 | 原因 | 怎么办 |
|---|---|---|
| `perPage must be less than or equal to 100` | `perPage` 超过 100（errcode 400） | 改成 ≤100，靠 `page` 翻页 |
| 其他 errcode 400 | 入参不合法 | 按 `errmsg` 改 |

401 / 403 / 500 / 503 等通用错误码的处理见 SKILL.md。

### 示例

看我有哪些表：
```json
{}
```

翻到第 2 页、每页 20 条（20 个多维表）：
```json
{"page": 2, "perPage": 20}
```

## listSharedTables —— 列出当前团队里别人共享给我的多维表及其下的数据表

**何时用 / 不该用**：用户问「有谁给我共享了表」「我能访问哪些别人的表」；要对一张共享来的表做后续操作但手上没有 `tableId`。
「共享给我」= 我能看见、**且不是我创建的**；自己建的只在 `listMyTables`（见本文件）里。⚠️ 用户笼统地说「我能看到哪些表」「我所有的表」时**两条都要调**再合并展示。
不该用：读表里的数据 → `listRecords`（见 `references/records-read.md`）；往共享来的多维表里加表 → `addTable`（见本文件，要对那个容器有写权，没有会 404）；飞书/Lark 多维表格 → `lark-base`（不是同一个系统）。

**调用**：`python scripts/smart_table.py listSharedTables '<JSON>'`（无参等价于 `'{}'`）

### 参数

与 `listMyTables` 完全一致：全部可选，`page`（≥1，默认 1）、`perPage`（1–100，默认 100，**限的是容器数**）。
**不接受** `baseId` / `spaceId` / `viewId` / `userId` / `teamId`，传了静默忽略；身份只由网关注入的头推导，请求体里的身份字段一律忽略，不传也无法指定看谁的。

### 响应

结构与 `listMyTables` **完全一致**（两层：`notebooks[]` 多维表 → `notebooks[].tables[]` 数据表，另有 `looseTables` 散表，为空时整个字段不出现；`total` 是**多维表总数**；字段表见上文 `listMyTables` § 响应）。只有以下不同：

| 字段 | 类型 | 说明 |
|---|---|---|
| notebooks[].tables | array | 这个多维表里**我有权看的**数据表——**可能不是容器的全部内容**，见下 |

**不返回** `baseId`、`createdBy`、**共享者信息**、**我在容器或表上的角色**。

### 语义与坑

- ⚠️ **按表名找 `tableId` 必须遍历两处**：所有 `notebooks[].tables[]`，**以及** `looseTables.tables[]`。顶层那一层的 id 是 `nbk` 开头的容器 id，拿去读记录会直接 400。
- ⚠️ **同一个容器返回的表可能不是它的全部内容**。可见性有两个来源：
  ① 我在这个**多维表**上有协作角色 → 容器里的表**全部**列出；
  ② 我在容器上没角色，但对里面**某张表**有表级协作行 → 容器**照样出现**，但只嵌我有权的那几张。
  所以别把 `tables` 当成容器的完整清单，**别告诉用户「这个项目里只有 N 张表」**，说「你有权访问其中 N 张」更准确。
- **与「我的表」严格互补**：按**多维表（容器）的创建者**分界——我建的容器归 `listMyTables`，这里刻意排除，两个列表不会重复。
- ⚠️ **只算直接共享给我的**：内网这条路径**没有部门（organization）上下文**，**按部门共享的看不到**。用户觉得「少了表」时，先解释这一点，再建议让对方按人再共享一次。
- **只含当前团队**：跨团队的不会出现。
- **共享给我 ≠ 我能改**：这里只回「我能看到」的；读/改/删由各自接口按动作维度判权，被拒时按提示告知用户权限不足。
- **空列表 ≠ 出错**：没人共享给你就是 `total: 0`、`notebooks: []`。
- **`total` 是多维表数，不是数据表数**，别直接念给用户听；翻页翻的是多维表，容器内的表不分页。
- **`tables: []` 的容器不一定是空的**：这套接口只列数据表、不列仪表盘，容器里可能只有仪表盘，也可能其余表我都没权限。
- **「我所有的表」= 本接口 + `listMyTables`**，**按多维表合并**展示，并标注哪些容器是自己建的、哪些是共享来的。两条接口形状完全一样，可以直接拼。
- **零参数可用**；容器和数据表各自带 `url`，可以直接发给用户打开。

**展示规则**：
- **按多维表分组展示**：容器名下面列它的数据表（表名 + 创建时间 + 链接），并说明这是**共享给你的**。
- 没有 `url` 字段时不要自己拼链接（服务端未配置站点地址）。
- 空列表时明确说「没有别人共享给你的多维表」，并提示自己创建的要用 `listMyTables` 查。
- 用户问「这个项目里就这些表吗」时，如实说**只能看到你有权访问的那些**，别断言那是全部。

### 常见错误

| errmsg 关键词 | 原因 | 怎么办 |
|---|---|---|
| `perPage must be less than or equal to 100` | `perPage` 超过 100（errcode 400） | 改成 ≤100，靠 `page` 翻页 |
| `Unauthorized` | errcode 401，身份未确立 | 按 SKILL.md 的认证/通用错误码处理 |

其他通用错误码（403 / 500 / 503）见 SKILL.md。

### 示例

看有哪些共享给我：
```json
{}
```

翻页（翻的是多维表）：
```json
{"page": 2, "perPage": 50}
```

## createTable —— 新建一个多维表（容器）并带第一张数据表，只建表结构

**何时用 / 不该用**：用户要一个新表来存结果/清单/记录；工作流需要落地一张结构化的表；用户要「新建一个多维表」。
⚠️ **与 `addTable` 分流**：手上**没有** `notebookId`、要一个新容器 → `createTable`；往**已有多维表**里再加一张表（有 `notebookId`）→ `addTable`（见本文件）。用错会**多建一个容器**。
不该用：往已有表里**加行** → `createRecords`、改已有行的值 → `updateRecords`（都见 `references/records-write.md`）；找已有的表 → `listMyTables` / `listSharedTables`（见本文件）；想知道**已有表**有哪些列 → `listFields`、往**已有表**加列 → `addFields`（都见 `references/fields.md`）；往附件列里放图 → `uploadAttachment`（见 `references/attachment.md`）；删除/重命名容器或表 → **没有接口**，只能到页面上操作；飞书/Lark 多维表格 → `lark-base`（不是同一个系统）。

**调用**：`python scripts/smart_table.py createTable '<JSON>'`

### 参数

| 参数 | 类型 | 必填 | 默认 | 约束 | 说明 |
|---|---|---|---|---|---|
| name | string | **是** | - | 1–255 字 | 表名。容器和默认表**同名**，都用它 |
| fields | array[object] | 否 | 单列「名称」单行文本表 | 1–200 项 | 列定义，数组顺序就是表里从左到右的列，**第一项是主字段**（代表「这一行是什么」的那列） |
| requestKey | string | 否 | - | 1–200 字 | 幂等键，见「语义与坑」 |
| ~~records~~ | - | - | - | **显式拒绝** | 不接受初始数据，传了直接 400 |
| ~~notebookId~~ | - | - | - | **本地预检拦截** | 本接口总是新建容器、不接受它；服务端对未声明字段**静默丢弃**，不拦的话你会以为表加进了那个容器，实际多出一个新容器 |

`fields` 每项：

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| name | string | 是 | 列名，1–255 字 |
| type | string | 是 | 字段类型 |
| choices | array[object] | 选项类**必填** | `[{"name": "...", "color": "..."}]`。`color` 可选，传的话要是站点色名（如 `blueBright`），**不是** `#RRGGBB`；不传由前端自动配色 |
| ai | object | 否 | 只能配在 `attachment` 列上：建成 AI 出图列（提示词 + 参考图）。`{列名}` 可以引用本次一起建的列。字段、模型与触发方式见 `references/ai.md` |

可用类型、写值方式、首列限制见 `references/fields.md` 的字段类型总表。

### 响应

| 字段 | 类型 | 说明 |
|---|---|---|
| notebookId | string | **新建的多维表（容器）id**，`nbk` 开头。往它里面再加表（`addTable`）要用它 |
| notebookName | string | 多维表的**实际名字**。**一定会去重**，可能与入参不同（连建两次「X」→「X」「X 2」）。**要显示给用户的是这个**，不是入参那个 |
| tableId | string | 容器里那张**默认数据表**的 id，`tbl` 开头。写数据要用它 |
| name | string | 默认数据表的名字。**可能被加了后缀**（去重行为取决于后端引擎），别假定它等于入参 |
| refKey | string | 稳定引用键。新建的表还没有血缘，**恒等于 `tableId`**（含义见 `listMyTables` § 响应） |
| url | string | 可点开的页面地址，建完可直接发给用户。服务端未配置站点地址时字段不出现——**不要自己拼** |
| createdTime | string | 建表时间，ISO 8601 |
| fields | array | 实际建出的列：`{fieldId, name, type, isPrimary?}`。`fieldId`（`fld` 开头）**只用于配工作流的触发条件，不能当写入的 key**——写数据一律按 `name` |
| idempotentHit | boolean | `true` = 命中幂等键、返回的是之前那个容器和表，**本次没有新建**。未命中时字段不出现 |

### 语义与坑

- ⚠️ **建的是「多维表（容器）+ 里面第一张数据表」，不是一张裸表**：数据表只能存在于多维表之下，**不能单独创建**，所以一次建两样东西。容器和默认表**同名**（调用方的心智是「我建了一张叫 X 的表」），对用户仍然可以说「建了一张叫 X 的表」。
- ⚠️ **出参两个 id 别混用**：`tableId`（`tbl`）写数据用（`createRecords` 等）；`notebookId`（`nbk`）往同一个容器里再加表用。传错层级会因为前缀校验直接 400（`tbl` / `nbk` 各自校验）。
- ⚠️ **用户接着说「再给我加一张表」→ `addTable` + 这个 `notebookId`，不要再调 `createTable`**（会多建一个容器）。本接口**不能选择建到哪个已有容器里**，总是新建一个；一次只建**一张**默认表，同一个容器里要更多表逐次调 `addTable`。
- ⚠️ **多维表名一定去重**：连建两次「X」→ 多维表得到「X」和「X 2」（`getUniqName`，后缀从 **2** 起，不是「(1)」）。所以出参 `notebookName` 可能与入参 `name` 不同——**要显示给用户的是 `notebookName`**。
- ⚠️ **数据表名不保证唯一**：去重行为**取决于后端引擎**（有的会加「 2」后缀、有的允许两张同名），所以**永远认 `tableId`、不要把表名当主键/唯一标识**。
- ⚠️ **不接受初始数据**：传 `records` 会被明确拒绝。原因是建表路径上**类型自动转换不可用**（底层写死关闭），值必须已经是精确类型，而这正是外部调用最容易出错、且错误信息来自底层很难懂的地方。正确流程：建表 → 拿 `tableId` → 用 `createRecords`（见 `references/records-write.md`，默认开着 `typecast`）写入 → 拿回 `recordId` 后才能 `updateRecords` / `deleteRecords`。
- ⚠️ **写数据不是 `updateRecords`**：那条只能改**已有行**，刚建的表是 0 行，拿它写数据会失败（早期文档写的是 updateRecords，那是条死路，已纠正）。
- **存量调用不用改**：出参里 `tableId` 仍然在、仍然指向一张可写的表，`createTable → createRecords` 的老链路照旧能跑；多出来的 `notebookId` 是新能力，不是新负担。
- ⚠️ **首列不能是 `checkbox` / `attachment`**（主字段要能代表一行的内容），放第一位会 **400**（脚本本地预检也会拦）。主字段用 `singleLineText` 之类最稳，把这类字段放到后面。
- **选项类字段（`singleSelect` / `multipleSelect`）必须给 `choices`**：`[{"name": "待处理"}, {"name": "已完成"}]`。
- **只开放基础类型**：关联 / 公式 / 汇总 / 成员 / 系统字段 / 按钮第一版**不开放**——它们要引用别的表、别的字段（公式/汇总的表达式要内部字段 id，而这套接口入参全程按字段名寻址；出参的 `fieldId` 要等字段建出来才有，建表这一刻还不存在），外部调用极难一次填对、填错时报的是内部错误。逐个说：`link`（关联）要另一张表的 `tblXXX`；`formula` / `rollup` 要引用内部字段 id；`user` / `createdBy` / `lastModifiedBy`（成员类）值是内部用户 id，对调用方无意义；`createdTime` / `lastModifiedTime` / `autoNumber`（系统字段）建表时给了也只是噪音；`button` 是纯 UI 交互。需要的话先用基础类型建表，再到前端页面上补。
- **不传 `fields`** 会建一张只有一列「名称」（单行文本）的表。用户没说列的时候，最好先问清要存哪些信息，别默认建空表。
- ⚠️ **幂等键 `requestKey`**：自动化/工作流里**务必传**（比如带上业务单号）。只防两件事：**并发**（两个实例同时收到同一请求）和**超时重试**——同一个 key 在短窗口内重复调用，返回**上次那个容器和表**并带 `idempotentHit: true`，本次没有新建。
  - **窗口是分钟级、存在缓存里，不是永久账本**。隔很久用同一个 key 再调会建出新的容器。这是刻意的：它解决「这次调用没收到响应」，不是「这个业务只准建一次表」。
  - 返回 **409** = 同 key 的上一次调用还在进行中：等几秒用**同一个 key** 重试；**换 key 会建出第二个容器**。
- **东西归调用方所有**：容器和表都建在**调用方自己的团队**里，不能指定建到别的团队/别的位置。工作流用哪个人的 key，东西就是那个人的。创建者自动获得 Owner 协作记录，所以这个容器随后出现在 `listMyTables`（而不是 `listSharedTables`）里。
- **限制**：`fields` 最多 200 列，表名/字段名最长 255 字。建完**没有删除/改名的接口**，建错了只能到页面上删——名字和列尽量一次问清。

**展示规则**：
- 建成后展示：表名、链接、列清单（名字 + 类型）。对用户说「建好了一张叫 X 的表」就够了，**不必解释容器这一层**——除非接下来要往同一个地方加表。
- **名字被去重时要说出来**：`notebookName` 与你传的 `name` 不一致（比如变成了「X 2」）说明已经有同名的多维表了，告诉用户实际叫什么，否则他回头找不到。
- `idempotentHit: true` 时要明确说「复用了之前那个，没有新建」，否则用户会以为多了一张。
- 报错时把 `errmsg` 原文转述：错误信息是按「调用方能照着改」写的。
- **不要声称建好了，除非返回 `errcode: 200`**（成功时也先检查 `idempotentHit` 再告知用户）。
- **记住返回的 `notebookId`**：用户接着要第二张表时用得上，否则要重新查一遍列表才能拿到它。

### 常见错误

前 7 行是脚本**本地预检**（发请求前报到 stderr，exit 1），其余是服务端返回。

| errmsg 关键词 | 原因 | 怎么办 |
|---|---|---|
| `缺少 name（表名）` | 没传 `name` | 补上表名 |
| `建表不接受初始数据（records）` | 传了 `records` | 去掉，建完用 `createRecords` 写（不是 `updateRecords`） |
| `createTable 不接受 notebookId` | 想往已有容器里加表 | 改用 `addTable` |
| `fields 要么不传…要么是非空数组` / `fields[i] 必须是对象` / `fields[i] 缺少 name` | `fields` 形状不对 | 按参数表改 |
| `fields[i].type=… 不支持` | 类型不在白名单（关联/公式/汇总/成员等） | 换基础类型，复杂字段到前端补 |
| `必须提供 choices` | 选项类字段缺 `choices`（服务端同样 400：`singleSelect / multipleSelect 必须提供 choices`） | 补 `choices` |
| `第一个字段不能是 checkbox` / `attachment` | 主字段用了 `checkbox` / `attachment` | 换成 `singleLineText` 之类，把它挪到后面 |
| errcode 400 其他 | 入参不合法 | 按 `errmsg` 原文改 |
| errcode 403 | 当前身份不能在该团队建表 | 告知用户无权建表 |
| errcode 409 | 同 `requestKey` 的上一次调用还在进行中 | 等几秒用**同一个 key** 重试；换 key 会建出第二个容器 |
| errcode 500 / 503 | 服务端异常 / 数据库暂不可用 | **重试前先用 `listMyTables` 确认表是不是已经建出来了**，避免建重 |

### 示例

最简，只给表名：
```json
{"name": "选品清单"}
```

定义好列：
```json
{
  "name": "选品清单",
  "fields": [
    {"name": "商品标题", "type": "singleLineText"},
    {"name": "价格", "type": "number"},
    {"name": "状态", "type": "singleSelect", "choices": [{"name": "待评估"}, {"name": "已选中"}, {"name": "已淘汰"}]},
    {"name": "跟进日期", "type": "date"},
    {"name": "已核对", "type": "checkbox"}
  ]
}
```

自动化里带幂等键：
```json
{"name": "日报-20260817", "requestKey": "daily-report-20260817"}
```

## addTable —— 往已经存在的多维表（容器）下面加一张新的数据表，只建表结构

**何时用 / 不该用**：用户说「在这个多维表里再加一张表」「往那个项目里加个表」；刚建完多维表，接着要往同一个地方放第二张表。

| 手上有什么 | 用哪条 | 结果 |
|---|---|---|
| 什么都没有，从零开始 | `createTable` | 建一个**新多维表** + 里面第一张表 |
| 已有 `notebookId` | `addTable` | 在**那个**多维表里加一张表 |

⚠️ **拿 `createTable` 去「加表」会多建一个容器**，用户会看到一个莫名其妙的新多维表。反过来，没有 `notebookId` 时 `addTable` 无法使用——它**不会替你建多维表**。
不该用：往已有表里**加行** → `createRecords`（见 `references/records-write.md`）；往已有表里**加列**（不是加表）→ `addFields`（见 `references/fields.md`）；找多维表 / 拿 `notebookId` → `listMyTables` / `listSharedTables`（见本文件）；读表里的数据 → `listRecords`（见 `references/records-read.md`）；删除/重命名容器或表 → **没有接口**，只能到页面上操作；飞书/Lark 多维表格 → `lark-base`（不是同一个系统）。

**调用**：`python scripts/smart_table.py addTable '<JSON>'`

### 参数

| 参数 | 类型 | 必填 | 默认 | 约束 | 说明 |
|---|---|---|---|---|---|
| notebookId | string | **是** | - | `nbk` 开头 | 加到哪个多维表下面 |
| name | string | **是** | - | 1–255 字 | 新数据表的表名 |
| fields | array[object] | 否 | 单列「名称」单行文本表 | 1–200 项 | 列定义，**第一项是主字段**；每项 `{name, type, choices?, ai?}`，形状与约束同 `createTable` § 参数 |
| ~~records~~ | - | - | - | **显式拒绝** | 不接受初始数据，传了直接 400 |
| ~~requestKey~~ | - | - | - | **不支持** | 这条接口**没有幂等键**（`createTable` 才有） |

`notebookId` 从哪来：

| 来源 | 取哪个字段 |
|---|---|
| `createTable` 的响应 | `notebookId` |
| `listMyTables` 的响应 | `notebooks[].notebookId` |
| `listSharedTables` 的响应 | `notebooks[].notebookId` |

字段类型白名单与 `createTable` **完全同一份**；可用类型、写值方式、首列限制见 `references/fields.md` 的字段类型总表。被排除的类型（`link` / `formula` / `rollup` / 成员类 / 系统字段 / `button`）与 `createTable` 同一个理由（见上文 `createTable` § 语义与坑）。

### 响应

| 字段 | 类型 | 说明 |
|---|---|---|
| tableId | string | 新数据表 id，`tbl` 开头。写数据要用它 |
| name | string | 实际表名。**可能与入参不同**（同名时可能被加上「 2」后缀），别假定它等于入参 |
| notebookId | string | 回显加到了哪个多维表下（与入参一致） |
| refKey | string | 稳定引用键。新建的表还没有血缘，**恒等于 `tableId`**（含义见 `listMyTables` § 响应） |
| url | string | 可点开的页面地址。服务端未配置站点地址时字段不出现——**不要自己拼** |
| createdTime | string | 建表时间，ISO 8601 |
| fields | array | 实际建出的列：`{fieldId, name, type, isPrimary?}`。`fieldId`（`fld` 开头）**只用于配工作流的触发条件，不能当写入的 key**——写数据一律按 `name` |

注意：**没有** `notebookName`、**没有** `idempotentHit`（这两个只有 `createTable` 有）。

### 语义与坑

- ⚠️ **按 `notebookId`（容器）寻址，不是 `tableId`**——这套接口里**只有它**这样，其余全部按 `tableId`（表还不存在，没有 `tableId` 可传）。`nbk` 开头的是多维表（容器），`tbl` 开头的是数据表，别搞反；`bse` 开头的是内部概念，不接受。脚本本地预检会拦：缺 `notebookId`、误传 `tableId`、不是 `nbk` 开头。
- ⚠️ **表名不保证唯一，而且没有幂等键**：同一个容器里同名反复加**不报错也不复用**——可能得到两张都叫「X」的表，也可能第二张被加上「 2」后缀（取决于后端引擎）。**别把表名当唯一标识，认 `tableId`，别按表名找表。**
- ⚠️ **这条接口没有 `requestKey`**（`createTable` 才有），重复调用会重复加表。超时或不确定是否成功时，**先用 `listMyTables` 看那张表是不是已经加上了**，再决定要不要重试——直接重试会多一张表。
- ⚠️ **不接受初始数据**：传 `records` 会被明确拒绝。流程是：加表 → 拿 `tableId` → 调 `createRecords`（见 `references/records-write.md`）写入 → 拿回 `recordId` 后才能 `updateRecords` / `deleteRecords`。**不是 `updateRecords`**：那条只能改**已有行**，刚建的表是 0 行。
- ⚠️ **多维表不在自己团队一律 404**：`notebookId` 不属于调用方团队时返回 **404**，与「id 根本不存在」是同一个响应——刻意如此，看不见的东西连存在都不告诉你（不告诉调用方「这个 id 存在但你没权限」）。拿到 404 时两种可能都要考虑：id 打错了，或那个多维表属于别人的团队。用 `listMyTables` / `listSharedTables` 重新查一次 `notebookId`。只能往**自己团队**的多维表里加。
- ⚠️ **报 403 / 404 也可能是没有写权限**：判权维度是**容器级**（对这个多维表有没有写权），不是表级。能在列表里看到一个容器（包括共享给你的），不等于能往里面加表——要有相应角色。
- ⚠️ **首列不能是 `checkbox` / `attachment`**：新表的第一个字段是主字段，要能代表一行的内容，放第一位会 **400**（脚本本地预检也会拦）。用 `singleLineText` 之类最稳，把这类字段放到后面。
- **选项类字段必须给 `choices`**：`[{"name": "待处理"}, {"name": "已完成"}]`。`color` 可选，传的话要是站点色名（如 `blueBright`），不是 `#RRGGBB`；不传由前端自动配色。
- **只开放基础类型**：关联 / 公式 / 汇总 / 成员不开放，需要的先用基础类型建表，再到前端页面上补。
- **不传 `fields`** 会建一张只有一列「名称」（单行文本）的表。用户没说列的时候，最好先问清要存哪些信息。
- **一次只能加一张表**，要加多张就多次调用。
- **限制**：`fields` 最多 200 列，表名/字段名最长 255 字。加完**没有删除/改名的接口**，加错了只能到页面上删。

**展示规则**：
- 加成后展示：表名、链接、列清单（名字 + 类型），并说明它加在**哪个多维表**下面。
- 报错时把 `errmsg` 原文转述：错误信息是按「调用方能照着改」写的。
- **不要声称加好了，除非返回 `errcode: 200`**。
- 记住返回的 `tableId`：接着写数据要用它。

### 常见错误

前 9 行是脚本**本地预检**（发请求前报到 stderr，exit 1），其余是服务端返回。

| errmsg 关键词 | 原因 | 怎么办 |
|---|---|---|
| `addTable 要的是 notebookId…不是 tableId` | 照着别的操作传了 `tableId` | 用 `listMyTables` 查出目标多维表的 `notebooks[].notebookId` |
| `缺少 notebookId` | 没传 `notebookId` | 从 `createTable` 出参或 `listMyTables` / `listSharedTables` 的 `notebooks[].notebookId` 拿 |
| `看起来不是多维表 id` | `notebookId` 不是 `nbk` 开头（传了 `tbl` / `bse`） | 换成 `nbk` 开头的容器 id（服务端同样 400） |
| `缺少 name（新数据表的表名）` | 没传 `name` | 补上表名 |
| `加表不接受初始数据（records）` | 传了 `records` | 去掉，加完用 `createRecords` 写（不是 `updateRecords`） |
| `fields 要么不传…` / `fields[i] 必须是对象` / `fields[i] 缺少 name` | `fields` 形状不对 | 按参数表改 |
| `fields[i].type=… 不支持` | 类型不在白名单 | 换基础类型，复杂字段到前端补 |
| `必须提供 choices` | 选项类字段缺 `choices` | 补 `choices` |
| `第一个字段不能是 checkbox` / `attachment` | 主字段用了 `checkbox` / `attachment` | 换成 `singleLineText` 之类，把它挪到后面 |
| errcode 400 其他 | 入参不合法 | 按 `errmsg` 原文改 |
| errcode 403 | 无权往这个多维表里加表（能看到 ≠ 能写） | 让容器的所有者给相应角色 |
| `Notebook not found: nbk…`（errcode 404） | id 打错了，或多维表不属于你的团队 | 用 `listMyTables` / `listSharedTables` 重新查 `notebookId` |
| errcode 500 / 503 | 服务端异常 / 数据库暂不可用 | **重试前先用 `listMyTables` 确认表是不是已经加出来了**（没有幂等键） |

### 示例

最简，往某个多维表里加一张表：
```json
{"notebookId": "nbkAaBbCcDdEeFf", "name": "竞品对比"}
```

定义好列：
```json
{
  "notebookId": "nbkAaBbCcDdEeFf",
  "name": "竞品对比",
  "fields": [
    {"name": "竞品名称", "type": "singleLineText"},
    {"name": "售价", "type": "number"},
    {"name": "威胁等级", "type": "singleSelect", "choices": [{"name": "高"}, {"name": "中"}, {"name": "低"}]},
    {"name": "已分析", "type": "checkbox"}
  ]
}
```

建完容器接着加第二张表：
```
python scripts/smart_table.py createTable '{"name":"选品项目"}'                         → 拿到 notebookId
python scripts/smart_table.py addTable '{"notebookId":"<上一步的>","name":"竞品对比"}'
```
