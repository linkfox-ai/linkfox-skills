# 表与多维表：listMyTables / listSharedTables / createTable / addTable / copyNotebook / deleteNotebook / deleteTable / deleteNotebookItem / renameNotebook / renameTable / renameNotebookItem

本文件覆盖 11 个操作：列出我的表（`listMyTables`）、列出共享给我的表（`listSharedTables`）、新建多维表并建第一张表（`createTable`）、往已有多维表里加表（`addTable`）、复制整个多维表（`copyNotebook`）、删除整个多维表（`deleteNotebook`）、删除一张数据表（`deleteTable`）、删除多维表里的仪表盘 / 文件夹 / 页面 / 应用（`deleteNotebookItem`），以及给这三类对象改名（`renameNotebook` / `renameTable` / `renameNotebookItem`）。三个删除一律进回收站，共用规则见「删除的共用规则」；三个改名的共用规则见「改名的共用规则」。
共用概念「两层出参」：表挂在两种容器下——多维表（`notebooks[].tables[]`）和不在任何多维表里的散表（`looseTables.tables[]`），找表时两层都要看；容器层的 `notebookId` 是多维表 ID，不是 tableId。

## listMyTables —— 列出当前团队里我创建的多维表及其下的数据表

**何时用 / 不该用**：这是拿 `tableId` 的**入口**——读/改/删记录、看字段都要 `tableId`，而它只能从这里或 `listSharedTables` 拿到；用户说「读一下我那张 XX 表」却没给 tableId 时，先用它按表名找。要往已有多维表里加表但手上没有 `notebookId` 时也用它。要删东西（多维表 / 数据表 / 仪表盘 / 文件夹 / 页面 / 应用）时，也先用它拿 id、并列出会连带删掉什么给用户确认；要给它们改名时同样先用它拿 id。
不该用：别人共享给我的 → `listSharedTables`（见本文件）；读表里的数据 → `listRecords`（见 `references/records-read.md`）；新建多维表 + 一张表 → `createTable`、往**已有**多维表里加一张表 → `addTable`（都见本文件）；飞书/Lark 多维表格不是同一个系统 → `lark-base`。

**调用**：`python scripts/smart_table.py listMyTables '<JSON>'`（无参等价于 `'{}'`）

### 参数

全部可选，`{}` 即取默认第一页。

| 参数 | 类型 | 必填 | 默认 | 约束 | 说明 |
|---|---|---|---|---|---|
| page | integer | 否 | 1 | ≥ 1 | 页码，从 1 起 |
| perPage | integer | 否 | 100 | 1–100 | 每页条数，**限的是多维表（容器）数**，不是数据表数 |
| notebookId | string | 否 | — | `nbk` 开头 | 只看这一个多维表。传了时只回它（`total` 为 1），**不回 `looseTables`** |

**不接受** `baseId` / `spaceId` / `viewId` / `userId` / `teamId` 等内部或身份概念，传了会被静默忽略。调用者身份只由网关注入的头推导（memberId → 用户 + 团队），请求体里的身份字段一律忽略，无法指定「看别人的表」。

**只看一个多维表**：手上已经有 `notebookId`（比如刚 `createTable` / `copyNotebook` 完、或用户给了多维表链接）、只想看它里面有什么时传 `notebookId`，不用翻全部。它不是你创建的时回 404：共享给你的，`errmsg` 会直接说「请用 listSharedTables 查」，照做即可；不存在 / 已进回收站 / 你看不到的，统一是 `Notebook … not found`。**不会回空列表**，所以 `notebooks` 里有它就是查到了。

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
| dashboards | array | 仪表盘，每项见「多维表内容对象」。**为空时字段不出现** |
| folders | array | 文件夹，同上 |
| pages | array | 页面（多维表侧栏里的页面节点），同上 |
| applications | array | 应用，同上 |

多维表内容对象（`dashboards[]` / `folders[]` / `pages[]` / `applications[]` 同一形状）：

| 字段 | 类型 | 说明 |
|---|---|---|
| itemId | string | `deleteNotebookItem` / `renameNotebookItem` 要的 id；`itemType` 就是它所在的数组（`dashboards` → `dashboard`，`folders` → `folder`，`pages` → `page`，`applications` → `application`）。文件夹 `bnf` 开头、页面 `pag` 开头、应用 `apl` 开头；仪表盘**不一定**有前缀（早期的是无前缀的 id） |
| name | string | 名字，可能重复 |
| folderId | string | 所在文件夹（**最近那一层**的 `bnf…`）；直接挂在多维表下时不出现。文件夹自己的这一项是它的**上层**文件夹 |
| createdTime | string | 创建时间，ISO 8601 |

只给寻址要的几项，不给链接和内容。**工作流（自动化）不在这几组里**，用 `listWorkflows` 查。

数据表对象（`notebooks[].tables[]` 与 `looseTables.tables[]` 同一形状）：

| 字段 | 类型 | 说明 |
|---|---|---|
| tableId | string | 数据表 id，`tbl` 开头。后续读/改/删记录都用它 |
| name | string | 表名，**可能重复**（建表、改名都不去重） |
| icon | string | 图标（emoji），没设置时字段不出现 |
| refKey | string | 稳定引用键，恒有值。复制多维表时副本里的表拿到新 `tableId`，但 `refKey` **不变**（恒等于血缘里最早那张表的 id）；没被复制过的表就等于自己的 `tableId`。⚠️ **只在同一个多维表内唯一**，跨容器同一个 `refKey` 对应不同的表；读写记录仍然用 `tableId` |
| url | string | 可点开的页面地址，没有时同样不要自己拼 |
| createdTime | string | 建表时间，ISO 8601 |
| folderId | string | 所在文件夹（最近那一层的 `bnf…`，对应 `folders[].itemId`）；直接挂在多维表下时不出现。**删那个文件夹会连这张表一起删** |

looseTables：

| 字段 | 类型 | 说明 |
|---|---|---|
| total | integer | 散表总数 |
| tables | array | 散表列表，形状同「数据表对象」 |

**不返回** `baseId`（内部概念）、`createdBy`（内部用户 id，对调用方无意义）。

### 语义与坑

```
notebooks[]                  ← 多维表（容器），分页落在这一层，total 是容器数
  ├─ notebookId (nbk...)     ← 往这个容器里加数据表 / 删整个多维表 / 改多维表名要用它
  ├─ name / url / createdTime
  ├─ tables[]                ← 这个容器里的数据表（不分页）
  │    ├─ tableId (tbl...)   ← 读/改/删记录、删表、改表名用它
  │    ├─ folderId (bnf...)  ← 在哪个文件夹里，直接挂在多维表下时不出现
  │    └─ name / url / createdTime
  └─ dashboards[] / folders[] / pages[] / applications[]   ← 为空时不出现
       ├─ itemId             ← deleteNotebookItem / renameNotebookItem 用它，itemType = 所在数组
       ├─ folderId           ← 同上（文件夹的这一项 = 上层文件夹）
       └─ name / createdTime
looseTables                  ← 不属于任何多维表的散表，为空时整个字段不出现
  ├─ total
  └─ tables[]                ← 形状同上
```

- ⚠️ **按表名找 `tableId` 必须遍历两处**：所有 `notebooks[].tables[]`，**以及** `looseTables.tables[]`。只扫顶层什么也找不到——顶层的 id 是 `nbk` 开头的容器 id，拿它去读记录会因为前缀校验直接 400。
- **表名可能重复**：建表不去重，同名表可以有多张，还可能分散在**不同的多维表**里。按名字匹配到多条时，把候选（**所在多维表** + 表名 + 创建时间 + 链接）列给用户挑，不要替用户猜——带上容器名很重要，那往往是用户区分它们的唯一线索。
- **列表为空 ≠ 出错**：团队还没有任何多维表时正常返回 `total: 0`、`notebooks: []`（`looseTables` 也不出现）。
- **`total` 是多维表数，不是数据表数**，翻页翻的也是容器。跟用户说「你有 N 张表」之前先自己数一遍 `tables`，别直接念 `total`。
- **容器内的数据表不分页**：`perPage` 只限容器数，一个容器里有多少表就全部返回。
- **多维表里除了数据表还有别的**：仪表盘、文件夹、页面、应用分别在 `dashboards` / `folders` / `pages` / `applications` 里，各自为空时字段不出现；工作流不在这里（用 `listWorkflows`）。说「这个多维表里有什么」时把它们也算上。
- **文件夹是树**：`folderId` 只标最近那一层。要说清「删这个文件夹会带走什么」，在 `tables` 和四个数组里找 `folderId` 等于它的，遇到子文件夹再按子文件夹的 `itemId` 往下找。
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
| `必须是多维表 id（以 nbk 开头）`（400） | `notebookId` 传成了 tableId 之类 | 多维表 id 是 `notebooks[].notebookId`，`nbk` 开头 |
| `… 是共享给你的：请用 listSharedTables 查`（404） | 传了 `notebookId`，但它不是你创建的 | 同样的 `notebookId` 改调 `listSharedTables` |
| `Notebook … not found`（404） | 传了 `notebookId`，但它不存在、已进回收站，或你看不到 | 去掉 `notebookId` 重新列一遍找对的 id |
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

只看一个多维表里有什么：
```json
{"notebookId": "nbkXXXXXXXXXXXXXXXX"}
```

## listSharedTables —— 列出当前团队里别人共享给我的多维表及其下的数据表

**何时用 / 不该用**：用户问「有谁给我共享了表」「我能访问哪些别人的表」；要对一张共享来的表做后续操作但手上没有 `tableId`。
「共享给我」= 我能看见、**且不是我创建的**；自己建的只在 `listMyTables`（见本文件）里。⚠️ 用户笼统地说「我能看到哪些表」「我所有的表」时**两条都要调**再合并展示。
不该用：读表里的数据 → `listRecords`（见 `references/records-read.md`）；往共享来的多维表里加表 → `addTable`（见本文件，要对那个容器有写权，没有会 404）；飞书/Lark 多维表格 → `lark-base`（不是同一个系统）。

**调用**：`python scripts/smart_table.py listSharedTables '<JSON>'`（无参等价于 `'{}'`）

### 参数

与 `listMyTables` 完全一致：全部可选，`page`（≥1，默认 1）、`perPage`（1–100，默认 100，**限的是容器数**）、`notebookId`（只看这一个，不回 `looseTables`）。
传了 `notebookId` 而它是你自己创建的 → 404，`errmsg` 会说「请用 listMyTables 查」；不存在 / 已进回收站 / 你看不到 → `Notebook … not found`。
**不接受** `baseId` / `spaceId` / `viewId` / `userId` / `teamId`，传了静默忽略；身份只由网关注入的头推导，请求体里的身份字段一律忽略，不传也无法指定看谁的。

### 响应

结构与 `listMyTables` **完全一致**（两层：`notebooks[]` 多维表 → `notebooks[].tables[]` 数据表，另有 `looseTables` 散表，为空时整个字段不出现；`total` 是**多维表总数**；字段表见上文 `listMyTables` § 响应）。只有以下不同：

| 字段 | 类型 | 说明 |
|---|---|---|
| notebooks[].tables | array | 这个多维表里**我有权看的**数据表——**可能不是容器的全部内容**，见下 |
| notebooks[].dashboards / folders / pages / applications | array | 形状同 `listMyTables`。**只在我对这个多维表有协作角色时出现**；只被共享了其中某几张表的，这四组一律不出现（与页面上看到的一致：只看得到那几张表）。各自为空时同样不出现 |

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
- **`tables: []`、又没有那四组的容器不一定是空的**：可能只是我在容器上没角色，只看得到被单独共享的表（四组不出现），其余内容我都没权限。
- **数据表的 `folderId` 照样会给**（只要那张表在文件夹里），但只靠表级共享进来时没有 `folders` 可以对照名字，只能看到 id。
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
不该用：往已有表里**加行** → `createRecords`、改已有行的值 → `updateRecords`（都见 `references/records-write.md`）；找已有的表 → `listMyTables` / `listSharedTables`（见本文件）；想知道**已有表**有哪些列 → `listFields`、往**已有表**加列 → `addFields`（都见 `references/fields.md`）；往附件列里放图 → `uploadAttachment`（见 `references/attachment.md`）；删除多维表或表 → `deleteNotebook` / `deleteTable`（见本文件，进回收站）；重命名多维表或表 → `renameNotebook` / `renameTable`（见本文件）；飞书/Lark 多维表格 → `lark-base`（不是同一个系统）。

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
| ai | object | 否 | 只能配在 `attachment` 列上：建成 AI 出图列（按提示词出图，可带参考图）。`{列名}` 可以引用本次一起建的列。字段、模型与触发方式见 `references/ai.md` |
| lookup | object | `lookup` 列**必填** | 查找引用配置（引用哪张表、取哪一列、查找条件、计算方式）。条件里的 `valueFromField` 可以引用本次一起建的普通列。形状见 `references/fields.md` § 查找引用 |

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
| fields | array | 实际建出的列：`{fieldId, name, type, isPrimary?, isComputed?}`。`fieldId`（`fld` 开头）**只用于配工作流的触发条件，不能当写入的 key**——写数据一律按 `name`。`isComputed: true` 的列（如查找引用）写不进去；要看查找引用的配置调 `listFields` |
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
- ⚠️ **首列不能是 `checkbox` / `attachment` / `lookup`**（主字段要能代表一行的内容），放第一位会 **400**（脚本本地预检也会拦）。主字段用 `singleLineText` 之类最稳，把这类字段放到后面。
- **选项类字段（`singleSelect` / `multipleSelect`）必须给 `choices`**：`[{"name": "待处理"}, {"name": "已完成"}]`。
- **查找引用列（`lookup`）可以随表一起建**：被引用的表必须是**你自己创建的、已经存在的**表（不能引用这次正在建的新表——它还没有 `tableId`；要引用新表，先建表、再 `addFields` 加查找列）。所有引用问题都在**建表之前**查，查不过整批 400、什么都不建。⚠️ 万一表建好了、补建查找列那一步失败，报错里会带 `tableId`：**表已经在了，不要重新 `createTable`**（会多出一个容器），用 `addFields` 只补报错里点名的那几列。
- **只开放基础类型 + 查找引用**：关联 / 公式 / 汇总 / 成员 / 系统字段 / 按钮第一版**不开放**——它们要引用别的表、别的字段（公式/汇总的表达式要内部字段 id，而这套接口入参全程按字段名寻址；出参的 `fieldId` 要等字段建出来才有，建表这一刻还不存在），外部调用极难一次填对、填错时报的是内部错误。逐个说：`link`（关联）要另一张表的 `tblXXX`；`formula` / `rollup` 要引用内部字段 id；`user` / `createdBy` / `lastModifiedBy`（成员类）值是内部用户 id，对调用方无意义；`createdTime` / `lastModifiedTime` / `autoNumber`（系统字段）建表时给了也只是噪音；`button` 是纯 UI 交互。需要的话先用基础类型建表，再到前端页面上补。
- **不传 `fields`** 会建一张只有一列「名称」（单行文本）的表。用户没说列的时候，最好先问清要存哪些信息，别默认建空表。
- ⚠️ **幂等键 `requestKey`**：自动化/工作流里**务必传**（比如带上业务单号）。只防两件事：**并发**（两个实例同时收到同一请求）和**超时重试**——同一个 key 在短窗口内重复调用，返回**上次那个容器和表**并带 `idempotentHit: true`，本次没有新建。
  - **窗口是分钟级、存在缓存里，不是永久账本**。隔很久用同一个 key 再调会建出新的容器。这是刻意的：它解决「这次调用没收到响应」，不是「这个业务只准建一次表」。
  - 返回 **409** = 同 key 的上一次调用还在进行中：等几秒用**同一个 key** 重试；**换 key 会建出第二个容器**。
- **东西归调用方所有**：容器和表都建在**调用方自己的团队**里，不能指定建到别的团队/别的位置。工作流用哪个人的 key，东西就是那个人的。调用方就是这个容器的创建者，所以它随后出现在 `listMyTables`（而不是 `listSharedTables`）里。
- **限制**：`fields` 最多 200 列，表名/字段名最长 255 字。名字建完还能改：多维表用 `renameNotebook`、数据表用 `renameTable`（两者**各改各的**，建出来时同名，见「改名的共用规则」）；**列名、列类型这套接口改不了**（只能到页面上改），列建错了只能用 `deleteNotebook` 删掉重建（进回收站，要先经用户确认）——列尽量一次问清。

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
| `第一个字段不能是 checkbox` / `attachment` / `lookup` | 主字段用了这几种 | 换成 `singleLineText` 之类，把它挪到后面 |
| `lookup` 相关（`不是你创建的` / `指向的表不存在` / `不是表「X」的列` / `computeMode ... 不能用在`） | 查找引用配置有误，什么都没建 | 见 `references/fields.md` § addFields 常见错误 |
| `表已建好（tableId: …），但这几列查找引用没建成` | 表已建好，只有查找列失败 | **别重新建表**，用 `addFields` 对这个 `tableId` 补那几列 |
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
不该用：往已有表里**加行** → `createRecords`（见 `references/records-write.md`）；往已有表里**加列**（不是加表）→ `addFields`（见 `references/fields.md`）；找多维表 / 拿 `notebookId` → `listMyTables` / `listSharedTables`（见本文件）；读表里的数据 → `listRecords`（见 `references/records-read.md`）；删除多维表或表 → `deleteNotebook` / `deleteTable`（见本文件，进回收站）；重命名多维表或表 → `renameNotebook` / `renameTable`（见本文件）；飞书/Lark 多维表格 → `lark-base`（不是同一个系统）。

**调用**：`python scripts/smart_table.py addTable '<JSON>'`

### 参数

| 参数 | 类型 | 必填 | 默认 | 约束 | 说明 |
|---|---|---|---|---|---|
| notebookId | string | **是** | - | `nbk` 开头 | 加到哪个多维表下面 |
| name | string | **是** | - | 1–255 字 | 新数据表的表名 |
| fields | array[object] | 否 | 单列「名称」单行文本表 | 1–200 项 | 列定义，**第一项是主字段**；每项 `{name, type, choices?, ai?, lookup?}`，形状与约束同 `createTable` § 参数 |
| ~~records~~ | - | - | - | **显式拒绝** | 不接受初始数据，传了直接 400 |
| ~~requestKey~~ | - | - | - | **不支持** | 这条接口**没有幂等键**（`createTable` 才有） |

`notebookId` 从哪来：

| 来源 | 取哪个字段 |
|---|---|
| `createTable` 的响应 | `notebookId` |
| `listMyTables` 的响应 | `notebooks[].notebookId` |
| `listSharedTables` 的响应 | `notebooks[].notebookId` |

字段类型白名单与 `createTable` **完全同一份**；可用类型、写值方式、首列限制见 `references/fields.md` 的字段类型总表。含查找引用 `lookup`。被排除的类型（`link` / `formula` / `rollup` / 成员类 / 系统字段 / `button`）与 `createTable` 同一个理由（见上文 `createTable` § 语义与坑）。

### 响应

| 字段 | 类型 | 说明 |
|---|---|---|
| tableId | string | 新数据表 id，`tbl` 开头。写数据要用它 |
| name | string | 实际表名。**可能与入参不同**（同名时可能被加上「 2」后缀），别假定它等于入参 |
| notebookId | string | 回显加到了哪个多维表下（与入参一致） |
| refKey | string | 稳定引用键。新建的表还没有血缘，**恒等于 `tableId`**（含义见 `listMyTables` § 响应） |
| url | string | 可点开的页面地址。服务端未配置站点地址时字段不出现——**不要自己拼** |
| createdTime | string | 建表时间，ISO 8601 |
| fields | array | 实际建出的列：`{fieldId, name, type, isPrimary?, isComputed?}`。`fieldId`（`fld` 开头）**只用于配工作流的触发条件，不能当写入的 key**——写数据一律按 `name`。`isComputed: true` 的列（如查找引用）写不进去 |

注意：**没有** `notebookName`、**没有** `idempotentHit`（这两个只有 `createTable` 有）。

### 语义与坑

- ⚠️ **按 `notebookId`（容器）寻址，不是 `tableId`**——这套接口里**只有它**这样，其余全部按 `tableId`（表还不存在，没有 `tableId` 可传）。`nbk` 开头的是多维表（容器），`tbl` 开头的是数据表，别搞反；`bse` 开头的是内部概念，不接受。脚本本地预检会拦：缺 `notebookId`、误传 `tableId`、不是 `nbk` 开头。
- ⚠️ **表名不保证唯一，而且没有幂等键**：同一个容器里同名反复加**不报错也不复用**——可能得到两张都叫「X」的表，也可能第二张被加上「 2」后缀（取决于后端引擎）。**别把表名当唯一标识，认 `tableId`，别按表名找表。**
- ⚠️ **这条接口没有 `requestKey`**（`createTable` 才有），重复调用会重复加表。超时或不确定是否成功时，**先用 `listMyTables` 看那张表是不是已经加上了**，再决定要不要重试——直接重试会多一张表。
- ⚠️ **不接受初始数据**：传 `records` 会被明确拒绝。流程是：加表 → 拿 `tableId` → 调 `createRecords`（见 `references/records-write.md`）写入 → 拿回 `recordId` 后才能 `updateRecords` / `deleteRecords`。**不是 `updateRecords`**：那条只能改**已有行**，刚建的表是 0 行。
- ⚠️ **多维表不在自己团队一律 404**：`notebookId` 不属于调用方团队时返回 **404**，与「id 根本不存在」是同一个响应——刻意如此，看不见的东西连存在都不告诉你（不告诉调用方「这个 id 存在但你没权限」）。拿到 404 时两种可能都要考虑：id 打错了，或那个多维表属于别人的团队。用 `listMyTables` / `listSharedTables` 重新查一次 `notebookId`。只能往**自己团队**的多维表里加。
- ⚠️ **报 403 / 404 也可能是没有写权限**：判权维度是**容器级**（对这个多维表有没有写权），不是表级。能在列表里看到一个容器（包括共享给你的），不等于能往里面加表——要有相应角色。
- ⚠️ **首列不能是 `checkbox` / `attachment` / `lookup`**：新表的第一个字段是主字段，要能代表一行的内容，放第一位会 **400**（脚本本地预检也会拦）。用 `singleLineText` 之类最稳，把这类字段放到后面。
- **选项类字段必须给 `choices`**：`[{"name": "待处理"}, {"name": "已完成"}]`。`color` 可选，传的话要是站点色名（如 `blueBright`），不是 `#RRGGBB`；不传由前端自动配色。
- **查找引用列（`lookup`）可以随表一起建**，规则同 `createTable`：只能引用你自己创建的已有表；表建好但查找列补建失败时，报错带 `tableId`，**别重新 `addTable`**（会多一张表），用 `addFields` 补那几列。
- **只开放基础类型 + 查找引用**：关联 / 公式 / 汇总 / 成员不开放，需要的先用基础类型建表，再到前端页面上补。
- **不传 `fields`** 会建一张只有一列「名称」（单行文本）的表。用户没说列的时候，最好先问清要存哪些信息。
- **一次只能加一张表**，要加多张就多次调用。
- **限制**：`fields` 最多 200 列，表名/字段名最长 255 字。表名加完还能用 `renameTable` 改；**列名、列类型这套接口改不了**（只能到页面上改）；加错了可以用 `deleteTable` 删掉（进回收站，要先经用户确认）。

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
| `第一个字段不能是 checkbox` / `attachment` / `lookup` | 主字段用了这几种 | 换成 `singleLineText` 之类，把它挪到后面 |
| `lookup` 相关（`不是你创建的` / `指向的表不存在` / `不是表「X」的列` / `computeMode ... 不能用在`） | 查找引用配置有误，什么都没建 | 见 `references/fields.md` § addFields 常见错误 |
| `表已建好（tableId: …），但这几列查找引用没建成` | 表已建好，只有查找列失败 | **别重新建表**，用 `addFields` 对这个 `tableId` 补那几列 |
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

## copyNotebook —— 复制整个多维表（创建副本 / 分享另存为副本）

**何时用 / 不该用**：用户要「复制一份多维表」「创建副本」「把别人分享给我的表存一份到我这里」时用。效果与页面上一样：复制**整个多维表**，连同里面的数据表（字段、视图、记录、附件）、仪表盘、自动化（工作流）、页面。副本**一律**落在调用者自己的团队里、归调用者本人。
不该用：只想在同一个多维表里再加一张空表 → `addTable`；只想新建 → `createTable`；只想看别人的表 → `listSharedTables` + `listRecords`，不必复制。

**调用**：`python scripts/smart_table.py copyNotebook '<JSON>'`

### 两个入口（二选一）

| 入口 | 对应页面操作 | 能复制什么 |
|---|---|---|
| `notebookId` | 多维表菜单里的「创建副本」 | **你创建的**，或你是这个**多维表协作者**的（「可查看」也行）。也就是 `listMyTables` / `listSharedTables` 里能看到的多维表 |
| `shareUrl`（+ `password`） | 分享页上的「另存为副本」 | 分享人把链接设成「**可另存为副本**」的才行。「可查看」「可编辑」的链接**不能**复制（与页面一致）。链接可以来自别的团队 |

⚠️ **先分清手上是哪种地址**（agent 最常走错的一步）：
- `…/share/shrXXXX/…` 才是**分享链接** → 传 `shareUrl`。
- `…/table/<baseId>/<tableId>`（数据表页面）或 `…/table/<baseId>/notebook/<nbkId>`（多维表页面）是**站内页面地址**，不是分享链接 → 说明这张表你本来就能看到，走 `notebookId`：多维表页面直接取地址里的 `nbk…`；数据表页面先 `listMyTables`（找不到再 `listSharedTables`），在 `notebooks[].tables[]` 里找到那个 `tableId`，取它所在多维表的 `notebookId`。
  把页面地址塞进 `shareUrl` 只会拿到 400，脚本本地就会拦下并告诉你该怎么改。

⚠️ 两个容易误判的边界：
- 只被加进了多维表里**某一张表**（不是整个多维表）的协作者，`listSharedTables` 里能看到这个多维表，但**复制不了**（回 404）—— 页面上也一样。
- 拿到一条「可查看」的分享链接**不等于**能复制。能不能复制只看分享人选没选「可另存为副本」。拿不准时可以先问用户，或直接调一次看回的是不是 403。

### 参数

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|---|---|---|
| notebookId | string | 二选一 | — | 要复制的多维表，`nbk` 开头。从 `listMyTables` / `listSharedTables` 的 `notebooks[].notebookId` 拿；**不是 tableId** |
| shareUrl | string | 二选一 | — | 分享链接（`/share/shr…` 形状），完整地址或裸 `shr…` id 都行。**数据表 / 多维表页面地址不是分享链接**，见上面「先分清手上是哪种地址」 |
| password | string | 否 | — | 分享链接设了密码时必填。只能和 `shareUrl` 一起传 |
| name | string | 否 | 见说明 | 副本名。`notebookId` 入口不传时叫「原名 副本」，`shareUrl` 入口不传时沿用原名；与你已有的多维表重名时自动加后缀 |
| includeRecords | boolean | 否 | true | 是否连记录一起复制。false 只复制结构（字段、视图、仪表盘） |
| requestKey | string | 否 | 脚本自动生成 | 幂等键。脚本没收到时会生成一个并打印出来，**超时重试时必须用同一个** |

**不接受** `baseId` / `spaceId` / 目标用户 / 目标团队之类的参数：副本落在哪、归谁，只由网关注入的身份决定，传了也会被忽略。

### 响应

| 字段 | 类型 | 说明 |
|---|---|---|
| notebookId | string | **副本**的多维表 id（不是源的）。往里加表用 `addTable` |
| name | string | 副本的最终名字（可能带去重后缀） |
| icon | string | 图标，没设置时不出现 |
| url | string | 副本的页面地址，服务端未配置站点地址时不出现——**不要自己拼** |
| createdTime | string | 创建时间，ISO 8601 |
| tables | array | 副本里的数据表，形状同 `listMyTables` 的数据表对象。⚠️ `tableId` 全是**新的**，后续读写一律用它们；`refKey` 与源表相同，可用来把源表和副本表对上 |
| workflowCopyFailed | boolean | 自动化没有完整复制过来。**仅为真时出现**，副本本身是好的，告诉用户去副本里核对自动化 |
| pageCopyFailed | boolean | 页面没有完整复制过来。**仅为真时出现**，同上 |
| applicationCopyFailed | boolean | 应用没有完整复制过来。**仅为真时出现**，同上 |
| idempotentHit | boolean | true = 命中幂等键，返回的是**上次那份**副本，这次没有新建 |

```json
{
  "errcode": 200,
  "errmsg": "ok",
  "notebookId": "nbkCopyAaBbCcDd",
  "name": "选品台账 副本",
  "url": "https://os.linkfox.com/table/bseXXXX/notebook/nbkCopyAaBbCcDd",
  "createdTime": "2026-10-16T03:20:11.000Z",
  "tables": [
    { "tableId": "tblNew111", "name": "竞品对比", "refKey": "tblSrc111", "createdTime": "2026-10-16T03:20:11.000Z" }
  ]
}
```

### 慢操作：超时与重试

复制是同步的，带记录的大多维表可能要几十秒到几分钟（脚本最多等 300 秒）。**超时不代表失败**，服务端通常还在继续复制：

1. 先 `listMyTables`，看副本（「原名 副本」或你给的 `name`）是不是已经出现；
2. 出现了就用它，**不要再复制**；
3. 没出现再用**同一个 `requestKey`** 重试 —— 上次已完成会直接回上次那份（`idempotentHit: true`），还在进行会回 409。
   换一个新 key 重发会复制出**两份**。

同一个用户同一时间只能跑一个复制，第二个会回 409。要复制多个就一个一个来。

### 常见错误

| errmsg / errcode | 原因 | 怎么办 |
|---|---|---|
| `notebookId 和 shareUrl 必须传且只传一个`（400） | 两个都传了或都没传 | 按场景只传一个 |
| `shareUrl 不是分享链接`（400） | `shareUrl` 里抠不出分享 id —— 最常见的是把数据表页面地址当分享链接传了 | 页面地址改走 `notebookId`（见上面「先分清手上是哪种地址」）；真是分享链接就确认是 `/share/shr…` 形状 |
| `这条分享链接分享的不是多维表`（400） | 分享的是单张表 / 仪表盘 | 这类链接没有「另存为副本」，告诉用户 |
| `这条分享链接设了密码，请传 password`（400） | 带密码的链接没给密码 | 问用户要访问密码 |
| `分享链接的密码不对`（400） | 密码错了，或分享人刚改了密码 | 让用户核对密码 |
| `分享人没有开「可另存为副本」`（403） | 链接是「可查看 / 可编辑」档 | 请分享人把链接权限改成「可另存为副本」 |
| `Notebook … not found`（404） | 你看不到这个多维表：不是你创建 / 协作的、不在当前团队、或已进回收站 | 用 `listMyTables` / `listSharedTables` 重新拿 `notebookId` |
| `Share … not found`（404） | 分享链接已关闭，或分享的多维表进了回收站 | 请分享人重新发 |
| 行数超限相关（400） | 副本里某张表的行数超过你的套餐上限 | 换 `includeRecords: false` 只复制结构，或让用户升级 |
| errcode 409 | 同一个 `requestKey` 还在复制，或你有另一个复制没跑完 | 等一会儿，按上面「超时与重试」先确认，别换 key 重发 |
| errcode 500 / 503 | 服务端异常 / 数据库暂不可用 | **重试前先 `listMyTables` 确认**副本是不是已经建出来了 |

### 示例

复制自己的多维表（连记录）：
```json
{"notebookId": "nbkAaBbCcDdEeFf"}
```

只复制结构、并改名：
```json
{"notebookId": "nbkAaBbCcDdEeFf", "name": "选品台账（Q4 模板）", "includeRecords": false}
```

按分享链接另存（带密码）：
```json
{"shareUrl": "https://os.linkfox.com/share/shrAbCdEfGh123456/base", "password": "1234"}
```

复制完往副本里写数据：
```
python scripts/smart_table.py copyNotebook '{"notebookId":"nbkXXXX"}'       → 拿到 tables[].tableId（新的）
python scripts/smart_table.py createRecords '{"tableId":"<副本里的 tableId>","records":[...]}'
```

## 删除的共用规则（deleteNotebook / deleteTable / deleteNotebookItem）

- **一律进回收站**，不是彻底删除。还原**只能**由用户在网页左侧栏底部的「回收站」里操作——这套接口**没有还原**；回收站里的东西也改不了名（三个改名操作都会拒，要先还原）。跟用户说「已移到回收站，可以在回收站里还原」，别说「永久删除了」，也别承诺「我帮你恢复」。
- **先确认再删**：脚本不带 `--yes` 一律拒绝（exit 2）。先用 `listMyTables`（不是自己建的用 `listSharedTables`）找到对象，向用户复述**名字 + 会连带删掉的东西**，拿到明确同意再加 `--yes`。
- **一次删一个对象**，没有批量。要删多个就逐个调、逐个确认结果。
- ⚠️ **关联列默认拦下**：被删的表之外，还有别的表的关联列指向它们时，整条 400、**什么都没删**；`errmsg` 列出这些列（只列你看得到的表，其余只给数量）。删下去这些列会被**转成单行文本**，**从回收站还原也转不回来**。把列名告诉用户、拿到同意后，才带 `allowBreakingLinks: true` 重试。**绝不自己加这个开关。**
- ⚠️ **多维表至少要留一张数据表**：删的是最后一张表（`deleteTable`），或文件夹里装着多维表的全部数据表（`deleteNotebookItem` 删文件夹）时 400「至少要保留一张数据表」，什么都没删。要全删 → `deleteNotebook`；只是想换一张 → 先 `addTable` 新建再删旧的。
- **`alreadyInTrash: true` 是成功**：它本来就在回收站里（多半是上一次超时其实已经删成功了），这次什么都没做。如实跟用户说「已经在回收站里了」。
- **超时 / 500 / 503 = 说不准删没删**：先 `listMyTables` 看对象还在不在——不在就是删掉了；还在就原样重试。重试是安全的：已进回收站的再删会回 `alreadyInTrash`，不会重复删。`deleteNotebook` 和删文件夹可能很慢（脚本最多等 300 秒），超时是常态。
- **409** = 同一个多维表里有另一个删除还在进行，这次什么都没删。等一会儿，先 `listMyTables` 确认那一次的结果，再决定要不要重试。
- 其余 4xx：**什么都没删**。把 `errmsg` 原文转述给用户。**不要声称删掉了，除非返回 `errcode: 200`。**
- **工作流（自动化）不归这三条删**，删流在工作流侧做。`deleteTable` 会把以那张表为触发表的流置空触发表（流还在，但不会再被触发，见 `references/workflow.md`）。

## deleteNotebook —— 删除整个多维表（连同里面的全部内容，进回收站）

**何时用 / 不该用**：用户要「删掉这个多维表 / 这个项目」。里面的数据表、仪表盘、文件夹、页面、应用**一起**进回收站，还原时整包回来。
不该用：只删其中一张表 → `deleteTable`；只删仪表盘 / 文件夹 / 页面 / 应用 → `deleteNotebookItem`（都见本文件）；只想清空数据、保留表结构 → 没有这个接口（`deleteRecords` 只能按 recordId 删行）；删工作流 → 到工作流侧。

**权限**：只有多维表的**创建者**能删。协作者（「可编辑」「可查看」）都删不了，一律 **404**——这时多半是权限不够，不是多维表真的不存在。

**调用**：`python scripts/smart_table.py deleteNotebook '<JSON>' --yes`

### 参数

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|---|---|---|
| notebookId | string | **是** | - | 多维表 id，`nbk` 开头。从 `listMyTables` / `listSharedTables` 的 `notebooks[].notebookId` 拿；**不是 tableId** |
| allowBreakingLinks | boolean | 否 | false | 多维表外有关联列指向里面的表时，照样删（那些列转成单行文本）。**只在用户看过报错列出的列、明确同意后才传** |

只收这两个。多传的参数服务端会**静默丢弃、照样删整个多维表**，所以脚本本地就拦（尤其是带着 `tableId` 想只删一张表的情况）。

### 响应

| 字段 | 类型 | 说明 |
|---|---|---|
| notebookId | string | 被删的多维表 id |
| name | string | 多维表名 |
| trashedTables | array | 一起进回收站的数据表 `[{tableId, name}]`。没有表时不出现 |
| brokenLinks | array | 传了 `allowBreakingLinks` 时，被转成单行文本的关联列 `[{tableId, tableName, fieldName}]`（只列你看得到的表）。没有时不出现 |
| hiddenBrokenLinkCount | integer | 被转成文本、但在你看不到的表里的关联列数。为 0 时不出现 |
| alreadyInTrash | boolean | `true` = 本来就在回收站里，这次什么都没做（此时没有 `trashedTables` / `brokenLinks`）。仅为真时出现 |

```json
{
  "errcode": 200,
  "errmsg": "ok",
  "notebookId": "nbkAaBbCcDdEeFf",
  "name": "选品台账",
  "trashedTables": [
    { "tableId": "tblAaa111", "name": "竞品对比" },
    { "tableId": "tblBbb222", "name": "供应商" }
  ]
}
```

**展示规则**：
- 成功后说「已把多维表 X 连同里面的 N 张表、仪表盘、页面……移到回收站，可以在网页左侧栏底部的回收站里还原」。
- 有 `brokenLinks` / `hiddenBrokenLinkCount` 时，明确告诉用户哪些关联列变成了单行文本、还原也转不回来。
- `alreadyInTrash: true` 时说「它已经在回收站里了」，别说「刚删掉了」。

### 常见错误

前 4 行是脚本**本地预检**（发请求前报到 stderr），其余是服务端返回。

| errmsg 关键词 | 原因 | 怎么办 |
|---|---|---|
| `拒绝执行：这会把多维表 … 连同里面的全部内容`（exit 2） | 没带 `--yes` | `listMyTables` 找到它，向用户复述名字和里面有什么，同意后加 `--yes` 重跑 |
| `deleteNotebook 删的是整个多维表…不收 tableId` / `这是数据表 id（tbl 开头）` | 拿 tableId 来删多维表 | 只删这张表 → `deleteTable`；真要删整个多维表 → `listMyTables` 里找到这张表所在那一项的 `notebookId` |
| `notebookId 必须以 nbk 开头`（带 `bnf` / `pag` / `apl` / `dsh` 提示） | 拿了文件夹 / 页面 / 应用 / 仪表盘的 id | 按提示改用 `deleteNotebookItem` |
| `deleteNotebook 只收 notebookId、allowBreakingLinks，多了 […]` | 多传了参数 | 只想删一部分 → 换 `deleteTable` / `deleteNotebookItem`；确实要删整个 → 去掉多余参数 |
| `有 N 个关联列指向将被删除的数据表`（400） | 多维表外有关联列指向里面的表，什么都没删 | 把列名告诉用户，同意后带 `allowBreakingLinks: true` 重试 |
| `Notebook … not found`（404） | id 错、不在当前团队，或你不是它的创建者 | `listMyTables` / `listSharedTables` 核对；是别人的多维表就请创建者来删 |
| errcode 409 | 同一个多维表里有另一个删除还在进行 | 等一会儿，`listMyTables` 确认后再决定 |
| 超时 / errcode 500 / 503 | 说不准删没删 | `listMyTables` 看还在不在：不在就是删了；还在就原样重试 |

### 示例

```json
{"notebookId": "nbkAaBbCcDdEeFf"}
```

用户看过报错里的关联列、同意转成文本后：
```json
{"notebookId": "nbkAaBbCcDdEeFf", "allowBreakingLinks": true}
```

完整流程：
```
python scripts/smart_table.py listMyTables                                      → 找到多维表，列出 tables / dashboards / folders / pages / applications
（向用户复述要删的多维表和里面的内容，拿到明确同意）
python scripts/smart_table.py deleteNotebook '{"notebookId":"nbkXXXX"}' --yes
```

## deleteTable —— 删除一张数据表（进回收站）

**何时用 / 不该用**：用户要「删掉这张表」。表连同它的全部记录、字段、视图进回收站。
不该用：只删几行 → `deleteRecords`（见 `references/records-write.md`）；只删几列 → `deleteFields`（见 `references/fields.md`）；清空全表数据、保留表结构 → 没有这个接口，让用户到页面上操作；删多维表的**最后一张**表 / 删整个多维表 → `deleteNotebook`；连同所在文件夹一起删 → `deleteNotebookItem` 传 `itemType: "folder"`（都见本文件）。

**权限**：这张表的**创建者**，或它所在**多维表的创建者**。能看、能改都不够，其余人 403。

**连带影响**：
- 以这张表为**触发表**的自动化（工作流）会被**置空触发表**：流还在，但不会再被触发，要让用户到工作流侧重新选表保存。想在确认时说清楚，先用 `listWorkflows` 看有没有流的 `tableId` 是它。
- 别的表指向它的关联列、多维表至少留一张表：见「删除的共用规则」。

**调用**：`python scripts/smart_table.py deleteTable '<JSON>' --yes`

### 参数

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|---|---|---|
| tableId | string | **是** | - | 数据表 id，`tbl` 开头。从 `listMyTables` / `listSharedTables` 的 `tables[].tableId` 拿 |
| allowBreakingLinks | boolean | 否 | false | 别的表有关联列指向这张表时照样删（那些列转成单行文本）。**只在用户看过报错列出的列、明确同意后才传** |

只收这两个，一次一张。脚本本地会拦多余参数——尤其是照着 `deleteRecords` / `deleteFields` 的习惯带了 `recordIds` / `fieldNames`：服务端会静默丢掉它们、**整张表照删**。

### 响应

| 字段 | 类型 | 说明 |
|---|---|---|
| tableId | string | 被删的表 id |
| name | string | 表名 |
| notebookId | string \| null | 它所在的多维表；不在任何多维表里的散表为 `null` |
| brokenLinks / hiddenBrokenLinkCount | - | 同 `deleteNotebook` |
| alreadyInTrash | boolean | 同 `deleteNotebook`：本来就在回收站里，这次什么都没做 |

```json
{"errcode": 200, "errmsg": "ok", "tableId": "tblAaa111", "name": "竞品对比", "notebookId": "nbkAaBbCcDdEeFf"}
```

**展示规则**：说「已把表 X（在多维表 Y 里）移到回收站，可以在回收站里还原」；有自动化以它为触发表的话，提醒用户那些流不会再触发了。其余同 `deleteNotebook`。

### 常见错误

前 4 行是脚本**本地预检**（发请求前报到 stderr），其余是服务端返回。

| errmsg 关键词 | 原因 | 怎么办 |
|---|---|---|
| `拒绝执行：这会把数据表 …`（exit 2） | 没带 `--yes` | 向用户复述表名和所在多维表，同意后加 `--yes` 重跑 |
| `deleteTable 删的是一张数据表…不收 notebookId` / `这是多维表 id（nbk 开头）` | 拿 notebookId 来删表 | 删整个多维表 → `deleteNotebook`；删其中一张 → `listMyTables` 找它的 `tableId` |
| `tableId 必须以 tbl 开头`（带 `bnf` / `pag` / `apl` / `dsh` / `fld` / `rec` 提示） | id 拿错了 | 按提示换操作 |
| `deleteTable 删的是整张表，不收 [...]` / `deleteTable 只收 tableId、allowBreakingLinks` | 多传了参数 | 只删行 / 列就换 `deleteRecords` / `deleteFields`；确实要删整张表就去掉多余参数 |
| `有 N 个关联列指向将被删除的数据表`（400） | 别的表有关联列指向它，什么都没删 | 把列名告诉用户，同意后带 `allowBreakingLinks: true` 重试 |
| `至少要保留一张数据表`（400） | 这是多维表里最后一张表 | 要全删 → `deleteNotebook`；要换 → 先 `addTable` 再删 |
| `Only the table creator can perform this operation` / `No access to table` / `Missing permission table\|delete`（403） | 你不是表或多维表的创建者，或没有删除权 | 请表的创建者来删 |
| `Table not found`（404） | id 错，或不在当前团队 | `listMyTables` / `listSharedTables` 重新拿 |
| errcode 409 / 超时 / 500 / 503 | 见「删除的共用规则」 | 先 `listMyTables` 确认 |

### 示例

```json
{"tableId": "tblAaa111"}
```

## deleteNotebookItem —— 删除多维表里的仪表盘 / 文件夹 / 页面 / 应用（进回收站）

**何时用 / 不该用**：用户要删多维表里的某个仪表盘、文件夹、页面或应用。这里的「页面」是多维表侧栏里的页面节点，与 `linkfox-smart-table-page` 技能（生成页面）无关。
不该用：删数据表 → `deleteTable`；删整个多维表 → `deleteNotebook`（都见本文件）；删工作流 → 到工作流侧。

**权限**：所在多维表的**创建者**，或「**可编辑**」的协作者。「可查看」的删不了。不在任何多维表里的对象一律 404。

⚠️ **删文件夹 = 连里面的东西一起删**：数据表、仪表盘、页面、应用、子文件夹全部进回收站（还原时一起回来）。
- 删之前在 `listMyTables` 里找出 `folderId` 等于它的所有表和内容（子文件夹再按它的 `itemId` 往下找），**全部列给用户确认**。
- 还要求文件夹里**每张数据表**你都能用 `deleteTable` 单独删（表或多维表的创建者），有一张不行就 403、**什么都不删**。
- 「至少留一张数据表」和关联列预检也只有删文件夹会碰到；删仪表盘 / 页面 / 应用不涉及数据表。

**调用**：`python scripts/smart_table.py deleteNotebookItem '<JSON>' --yes`

### 参数

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|---|---|---|
| itemType | string | **是** | - | `dashboard` / `folder` / `page` / `application` 四选一（单数、小写），**取 `itemId` 所在的数组**：`dashboards` → `dashboard`，以此类推 |
| itemId | string | **是** | - | 从 `listMyTables` / `listSharedTables` 里那个多维表的 `dashboards` / `folders` / `pages` / `applications` 拿。文件夹 `bnf`、页面 `pag`、应用 `apl` 开头，脚本会校验；仪表盘**不校验前缀**（早期仪表盘的 id 没有 `dsh` 前缀） |
| allowBreakingLinks | boolean | 否 | false | 只对删文件夹有意义：别处有关联列指向文件夹里的表时照样删。**只在用户看过报错列出的列、明确同意后才传** |

只收这三个，**不用传 `notebookId`**（服务端按 `itemId` 自己找所在的多维表）；一次一个，没有批量。

### 响应

| 字段 | 类型 | 说明 |
|---|---|---|
| itemType | string | 回显 |
| itemId | string | 被删对象的 id |
| name | string | 名字 |
| notebookId | string | 它所在的多维表 |
| trashedTables | array | 只有删文件夹会有：跟着进回收站的数据表 `[{tableId, name}]`。没有时不出现 |
| brokenLinks / hiddenBrokenLinkCount / alreadyInTrash | - | 同 `deleteNotebook` |

```json
{
  "errcode": 200,
  "errmsg": "ok",
  "itemType": "folder",
  "itemId": "bnfAaBbCc112233",
  "name": "历史数据",
  "notebookId": "nbkAaBbCcDdEeFf",
  "trashedTables": [{ "tableId": "tblOld001", "name": "2025 订单" }]
}
```

**展示规则**：说「已把 X（仪表盘 / 文件夹 / 页面 / 应用）移到回收站，可以在回收站里还原」；删的是文件夹就把跟着走的表和内容一起说出来。其余同 `deleteNotebook`。

### 常见错误

前 5 行是脚本**本地预检**（发请求前报到 stderr），其余是服务端返回。

| errmsg 关键词 | 原因 | 怎么办 |
|---|---|---|
| `拒绝执行：这会把…`（exit 2） | 没带 `--yes` | 向用户复述名字、所在多维表（文件夹还要列出里面的内容），同意后加 `--yes` 重跑 |
| `是数据表 id（tbl 开头）` / `是多维表 id（nbk 开头）` | 拿错了 id | 删数据表 → `deleteTable`；删整个多维表 → `deleteNotebook` |
| `缺少 itemType` / `itemType 写成了 …` / `itemType 只能是 …` | `itemType` 没传或写错（复数、`table`、`workflow`…） | 按提示改成四个值之一；`table` → `deleteTable`，工作流到工作流侧删 |
| `itemType=… 与 itemId=… 对不上` / `的 itemId 应以 … 开头` | `itemType` 与 id 前缀不符 | 以 `itemId` 出现在哪个数组为准 |
| `deleteNotebookItem 只收 itemType、itemId、allowBreakingLinks` / `一次只删一个对象` | 多传了参数（常见是 `notebookId` 或 `itemIds`） | 去掉；多个就逐个调 |
| `有 N 个关联列指向将被删除的数据表`（400） | 文件夹外有关联列指向里面的表，什么都没删 | 把列名告诉用户，同意后带 `allowBreakingLinks: true` 重试 |
| `至少要保留一张数据表`（400） | 文件夹装着多维表的全部数据表 | 要全删 → `deleteNotebook`；否则先 `addTable`（或让用户在页面上把要留的表挪出文件夹）再删 |
| `This folder contains table …, which only its creator or the notebook creator can delete`（403） | 文件夹里有你不能单独删的表，什么都没删 | 请多维表的创建者来删 |
| errcode 403 其他 | 你对这个多维表没有编辑权 | 请多维表的创建者来删，或请他把你设为「可编辑」 |
| `<itemType> <itemId> not found`（404） | id 错、`itemType` 对不上、它不在任何多维表里，或所在多维表已进回收站 | 用 `listMyTables` / `listSharedTables` 重新拿，`itemType` 取它所在的数组 |
| errcode 409 / 超时 / 500 / 503 | 见「删除的共用规则」 | 先 `listMyTables` 确认 |

### 示例

删一个仪表盘：
```json
{"itemType": "dashboard", "itemId": "dshAaBbCc112233"}
```

删一个文件夹（连同里面的内容）：
```json
{"itemType": "folder", "itemId": "bnfAaBbCc112233"}
```

完整流程：
```
python scripts/smart_table.py listMyTables                                      → 在 folders 里找到文件夹，再找 folderId 等于它的表和内容
（向用户复述：文件夹叫什么、会连带删掉哪些表 / 仪表盘 / 页面 / 应用 / 子文件夹，拿到明确同意）
python scripts/smart_table.py deleteNotebookItem '{"itemType":"folder","itemId":"bnfXXXX"}' --yes
```

## 改名的共用规则（renameNotebook / renameTable / renameNotebookItem）

- **一律按 id 改，别按名字改**：数据表、仪表盘、页面、应用都允许重名（还可能分散在不同的多维表里）。先 `listMyTables`（找不到再 `listSharedTables`）定位对象拿 id；用户的描述命中多个时，把候选（所在多维表 + 名字 + 创建时间）列给用户挑，**别自己猜**。
- ⚠️ **多维表名和里面数据表的名字互相独立**：`renameNotebook` 不会改里面的数据表，`renameTable` 也不会改它所在的多维表。`createTable` 建出来时两者同名，用户往往以为是一个东西——用户说「把这个表改成 X」、而多维表和表同名时，先问清改哪一个；两个都要改就分别调。
- **只改名字**：图标改不了；**列名、列类型这套接口也改不了**（只能在页面上改）。
- **名字**：服务端会去掉首尾空白，去掉后要 1–255 字，否则 400（脚本本地先拦）。出参 `name` 是**存下来的值**，跟用户说这个，别照抄入参。
- **重名**：只有两类会报 400、**什么都没改**——多维表（同一创建者名下，**回收站里的也算**，名字还占着）报 `Notebook name already exists`；文件夹（同一个多维表内）报 `Folder name already exists`。把冲突告诉用户、请他换个名字；**不要自己加后缀或编号重试**（这一点和 `createTable` 自动去重不同）。数据表、仪表盘、页面、应用允许重名，不报错。
- **不要 `--yes`**：改名可逆（改回去就行），同 `updateRecords`，没有确认闸门。但用户没说清改哪个、改成什么时，先问，别替用户起名。
- **改成原名直接回成功**（什么都没变），所以**超时 / 500 / 503 用同样的参数原样重试是安全的**；也可以先 `listMyTables` 看名字变没变。
- **回收站里的改不了名**：已进回收站的对象（或它所在的多维表已进回收站）一律被拒，要先请用户在页面上还原。
- 其余 4xx：**名字没有改**。把 `errmsg` 原文转述给用户。**不要声称改好了，除非返回 `errcode: 200`。**

## renameNotebook —— 改多维表的名字

**何时用 / 不该用**：用户要「把这个多维表 / 这个项目改个名」。只改多维表（容器，侧栏里那一项）自己的名字。
不该用：改里面某张数据表的名字 → `renameTable`；改仪表盘 / 文件夹 / 页面 / 应用的名字 → `renameNotebookItem`（都见本文件）；改列名 → 这套接口做不到，请用户在页面上改。

**权限**：只有多维表的**创建者**能改。协作者（「可编辑」「可查看」）一律 **404**——所以 `notebookId` 只从 `listMyTables` 里找；只在 `listSharedTables` 里的多维表是别人的，改不了。

**调用**：`python scripts/smart_table.py renameNotebook '<JSON>'`

### 参数

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|---|---|---|
| notebookId | string | **是** | - | 多维表 id，`nbk` 开头。从 `listMyTables` 的 `notebooks[].notebookId` 拿；**不是 tableId** |
| name | string | **是** | - | 新名字，去掉首尾空白后 1–255 字 |

只收这两个。多传的参数服务端会**静默丢弃**，所以脚本本地就拦——尤其是带着 `tableId`（想改的其实是表名）或 `icon`（图标改不了）。

### 响应

| 字段 | 类型 | 说明 |
|---|---|---|
| notebookId | string | 改名的多维表 id |
| name | string | 存下来的新名字（已去掉首尾空白） |

```json
{"errcode": 200, "errmsg": "ok", "notebookId": "nbkAaBbCcDdEeFf", "name": "选品台账 2026"}
```

**展示规则**：说「已把多维表改名为 X」（X 用出参的 `name`）。用户可能以为里面的表也跟着改了，顺带说一句「里面数据表的名字没变」。

### 常见错误

前 4 行是脚本**本地预检**（发请求前报到 stderr），其余是服务端返回。

| errmsg 关键词 | 原因 | 怎么办 |
|---|---|---|
| `renameNotebook 改的是多维表的名字…不收 tableId` / `这是数据表 id（tbl 开头）` | 拿 tableId 来改多维表名 | 改表名 → `renameTable`；真要改多维表名 → `listMyTables` 里找到这张表所在那一项的 `notebookId` |
| `notebookId 必须以 nbk 开头`（带 `bnf` / `pag` / `apl` / `dsh` / `fld` 提示） | 拿了文件夹 / 页面 / 应用 / 仪表盘 / 字段的 id | 按提示改用 `renameNotebookItem`；字段 → 列名改不了 |
| `缺少 name` / `新名字的参数名是 name` / `name 不能为空` / `name 太长` | 新名字没传、参数名写错（`newName` / `title`…），或去掉空白后为空 / 超过 255 字 | 改成 `name`；名字有问题就问用户，**别自己截断或起名** |
| `renameNotebook 只收 notebookId、name` / `图标改不了` / `列名这套接口改不了` | 多传了参数 | 去掉；图标、列名请用户在页面上改 |
| `Notebook name already exists`（400） | 你名下已有同名多维表（回收站里的也算） | 告诉用户、请他换个名字；**别自己加后缀重试** |
| `Notebook … not found`（404） | id 错、不在当前团队、已进回收站，或你不是它的创建者 | `listMyTables` 核对；是别人的多维表就请创建者来改 |
| 超时 / errcode 500 / 503 | 说不准改没改 | 用同样的参数原样重试（安全），或先 `listMyTables` 看名字变没变 |

### 示例

```json
{"notebookId": "nbkAaBbCcDdEeFf", "name": "选品台账 2026"}
```

多维表和里面那张表都要改（`createTable` 建出来时同名）：
```
python scripts/smart_table.py listMyTables                                      → 找到 notebookId 和里面那张表的 tableId
python scripts/smart_table.py renameNotebook '{"notebookId":"nbkXXXX","name":"选品台账 2026"}'
python scripts/smart_table.py renameTable '{"tableId":"tblXXXX","name":"选品台账 2026"}'
```

## renameTable —— 改一张数据表的名字

**何时用 / 不该用**：用户要「把这张表改个名」。只改这一张数据表的名字，它所在多维表的名字不变。不在任何多维表里的散表（`looseTables`）也能改。
不该用：改多维表（容器）的名字 → `renameNotebook`；改仪表盘 / 文件夹 / 页面 / 应用的名字 → `renameNotebookItem`（都见本文件）；**改列名 / 改列类型 → 这套接口做不到**，请用户在页面上改；改某几行的值 → `updateRecords`（见 `references/records-write.md`）。

**权限**：这张表的**创建者**，或它所在**多维表的创建者**。「可编辑」「可查看」都不够，其余人 **403**（页面上也一样）。

**调用**：`python scripts/smart_table.py renameTable '<JSON>'`

### 参数

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|---|---|---|
| tableId | string | **是** | - | 数据表 id，`tbl` 开头。从 `listMyTables` / `listSharedTables` 的 `tables[].tableId` 拿 |
| name | string | **是** | - | 新表名，去掉首尾空白后 1–255 字。**允许和别的表重名** |

只收这两个，一次一张。脚本本地会拦多余参数——尤其是 `fieldName` / `fieldNames` / `fieldId`：服务端会静默丢掉它们、**把表名改成 `name`**，而用户想改的是列名。

### 响应

| 字段 | 类型 | 说明 |
|---|---|---|
| tableId | string | 改名的表 id |
| name | string | 存下来的新表名（已去掉首尾空白） |
| notebookId | string \| null | 它所在的多维表；不在任何多维表里的散表为 `null` |

```json
{"errcode": 200, "errmsg": "ok", "tableId": "tblAaa111", "name": "竞品对比（Q4）", "notebookId": "nbkAaBbCcDdEeFf"}
```

**展示规则**：说「已把表改名为 X（在多维表 Y 里）」（X 用出参的 `name`）。多维表和表原来同名的，顺带说一句「多维表的名字没变」。表名允许重复，后续读写照样认 `tableId`。

### 常见错误

前 5 行是脚本**本地预检**（发请求前报到 stderr），其余是服务端返回。

| errmsg 关键词 | 原因 | 怎么办 |
|---|---|---|
| `renameTable 改的是一张数据表的名字…不收 notebookId` / `这是多维表 id（nbk 开头）` | 拿 notebookId 来改表名 | 改多维表名 → `renameNotebook`；改其中一张 → `listMyTables` 找它的 `tableId` |
| `tableId 必须以 tbl 开头`（带 `bnf` / `pag` / `apl` / `dsh` / `fld` / `rec` / `viw` 提示） | id 拿错了 | 按提示换操作；`fld` → 列名改不了；`viw` → 视图名改不了 |
| `renameTable 只改表名，不收 [fieldName…]` | 想改列名 | **列名这套接口改不了**，请用户在页面上改 |
| `缺少 name` / `新名字的参数名是 name` / `name 不能为空` / `name 太长` | 同 `renameNotebook` | 同 `renameNotebook` |
| `renameTable 只收 tableId、name` / `图标改不了` / `一次只改一张表` | 多传了参数（常见是 `notebookId`、`icon`、`tableIds`） | 去掉；多张就逐张调 |
| `Only the table creator can perform this operation` / `No access to table` / `Missing permission table\|update`（403） | 你不是表或多维表的创建者，或对这张表没有编辑权 | 请表的创建者来改 |
| `Table not found`（404） | id 错、不在当前团队，或已进回收站 | `listMyTables` / `listSharedTables` 重新拿；回收站里的先请用户还原 |
| 超时 / errcode 500 / 503 | 说不准改没改 | 用同样的参数原样重试（安全），或先 `listMyTables` 看表名变没变 |

### 示例

```json
{"tableId": "tblAaa111", "name": "竞品对比（Q4）"}
```

## renameNotebookItem —— 改多维表里的仪表盘 / 文件夹 / 页面 / 应用的名字

**何时用 / 不该用**：用户要给多维表里的某个仪表盘、文件夹、页面或应用改名。这里的「页面」是多维表侧栏里的页面节点，与 `linkfox-smart-table-page` 技能（生成页面）无关。
不该用：改数据表名 → `renameTable`；改多维表名 → `renameNotebook`（都见本文件）；改列名 → 这套接口做不到；改工作流的名字 → 到工作流侧。

**权限**：所在多维表的**创建者**，或「**可编辑**」的协作者。「可查看」的改不了（404）。回收站里的、不在任何多维表里的对象一律 404。

**重名**：**文件夹**在同一个多维表里不能重名（400）；仪表盘、页面、应用允许重名——所以一律按 `itemId` 改。改文件夹名只改文件夹自己，里面的表和内容原样不动。

**调用**：`python scripts/smart_table.py renameNotebookItem '<JSON>'`

### 参数

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|---|---|---|
| itemType | string | **是** | - | `dashboard` / `folder` / `page` / `application` 四选一（单数、小写），**取 `itemId` 所在的数组**，同 `deleteNotebookItem` |
| itemId | string | **是** | - | 从 `listMyTables` / `listSharedTables` 里那个多维表的 `dashboards` / `folders` / `pages` / `applications` 拿。文件夹 `bnf`、页面 `pag`、应用 `apl` 开头，脚本会校验；仪表盘**不校验前缀** |
| name | string | **是** | - | 新名字，去掉首尾空白后 1–255 字 |

只收这三个，**不用传 `notebookId`**（服务端按 `itemId` 自己找所在的多维表）；一次一个，没有批量。

### 响应

| 字段 | 类型 | 说明 |
|---|---|---|
| itemType | string | 回显 |
| itemId | string | 改名对象的 id |
| name | string | 存下来的新名字（已去掉首尾空白） |
| notebookId | string | 它所在的多维表 |

```json
{"errcode": 200, "errmsg": "ok", "itemType": "folder", "itemId": "bnfAaBbCc112233", "name": "2025 归档", "notebookId": "nbkAaBbCcDdEeFf"}
```

**展示规则**：说「已把 X（仪表盘 / 文件夹 / 页面 / 应用）改名为 Y」（Y 用出参的 `name`）。

### 常见错误

前 5 行是脚本**本地预检**（发请求前报到 stderr），其余是服务端返回。

| errmsg 关键词 | 原因 | 怎么办 |
|---|---|---|
| `是数据表 id（tbl 开头）` / `是多维表 id（nbk 开头）` / `是字段 id（fld 开头）` | 拿错了 id | 改表名 → `renameTable`；改多维表名 → `renameNotebook`；列名改不了 |
| `缺少 itemType` / `itemType 写成了 …` / `itemType 只能是 …` | `itemType` 没传或写错（复数、`table`、`workflow`…） | 按提示改成四个值之一 |
| `itemType=… 与 itemId=… 对不上` / `的 itemId 应以 … 开头` | `itemType` 与 id 前缀不符 | 以 `itemId` 出现在哪个数组为准 |
| `缺少 name` / `新名字的参数名是 name` / `name 不能为空` / `name 太长` | 同 `renameNotebook` | 同 `renameNotebook` |
| `renameNotebookItem 只收 itemType、itemId、name` / `一次只改一个对象` / `图标改不了` | 多传了参数（常见是 `notebookId`、`itemIds`、`icon`） | 去掉；多个就逐个调 |
| `Folder name already exists`（400） | 同一个多维表里已有同名文件夹 | 告诉用户、请他换个名字；**别自己加后缀重试** |
| errcode 403 | 你对这个多维表没有编辑权 | 请多维表的创建者来改，或请他把你设为「可编辑」 |
| `<itemType> <itemId> not found`（404） | id 错、`itemType` 对不上、它或所在多维表已进回收站、它不在任何多维表里，或你只有「可查看」 | 用 `listMyTables` / `listSharedTables` 重新拿；回收站里的先请用户还原 |
| 超时 / errcode 500 / 503 | 说不准改没改 | 用同样的参数原样重试（安全），或先 `listMyTables` 看名字变没变 |

### 示例

改一个仪表盘的名字：
```json
{"itemType": "dashboard", "itemId": "dshAaBbCc112233", "name": "销售看板"}
```

完整流程：
```
python scripts/smart_table.py listMyTables                                      → 在那个多维表的 folders 里按名字找到 itemId（同名多个就让用户挑）
python scripts/smart_table.py renameNotebookItem '{"itemType":"folder","itemId":"bnfXXXX","name":"2025 归档"}'
```
