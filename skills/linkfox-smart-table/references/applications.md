# 应用：listApplications / createApplication / publishApplication / unpublishApplication

本文件覆盖四个操作：`listApplications` 列出「我能看到的全部应用」，重点是**顺手给出 `sessionId`**；`createApplication` 往一个**已有多维表**里**按模板**建应用，回 `applicationId`、进编辑器的 `sessionId`，以及这个应用源代码包的下载地址 `sourceUrl`；`publishApplication` 把**改完代码**的应用发上线，传创建时拿到的 `sessionId` + 自己上传的新代码包地址，回 `publishUrl`；`unpublishApplication` 把已上线的应用**下线**，传 `applicationId`，清掉发布地址并撤销公开分享凭据。

「应用」是多维表里的一种节点（与数据表、仪表盘、文件夹、页面并列），侧栏里点开是一个独立的页面/对话编辑器。它**注册在我们这边、内容在应用服务那边**，所以这里只存它的名字、归属、发布状态，外加一个 `${sessionId}` —— 那个 id 正是进编辑器要用的键。

## 优先用一条命令

建应用 / 发布 / 改完重发都优先用 `scripts/create_app.py`，它已经把下面四个操作串好并处理了
409 锁、不幂等重试、`sourceUrl` 落盘、下载、打包、上传、发布、列表校验：

```bash
python scripts/create_app.py templates          # 选模板（resourceId）
python scripts/create_app.py create --template amazon-search --name 我的选品库
python scripts/create_app.py dev --dir ./linkfox-apps/amazon-search-aplXxx   # 本地 pnpm dev 预览（SSO 登录）
python scripts/create_app.py publish --dir ./linkfox-apps/amazon-search-aplXxx  # 用户确认后才发布
python scripts/create_app.py apps --name 关键词  # 修改已有应用前先看
```

⚠️ 在本机执行，不要在远端沙箱里跑 `--build`（沙箱没有 pnpm）。
下游协议细节仍以本文件下面各节为准。

**与 `listMyTables` / `listSharedTables` 里的 `applications` 数组的区别**：那两个是导航结构的一部分，每个多维表嵌自己那几个应用，出参只有 `itemId`（= 这里的 `applicationId`）、`name`、`folderId`、`createdTime`，**不含 `sessionId`**；出参是**两层**的（容器 → 内容）。`listApplications` 是**一层扁平列表**，分页落在应用上，且带 `sessionId` / `publishUrl` / `publishVisibility` / `notebookName`。

## 可见范围

与侧栏同一份口径（容器级角色，含部门授权）+ 我创建的容器。两句话记住：

- **我创建的**多维表下的应用 + **别人共享给我**（在容器上有角色）的多维表下的应用，都在这里，`source` 分别是 `mine` / `shared`。
- **只被共享了其中某几张数据表**的多维表，里面的应用**不列** —— 那种人在侧栏里也看不到容器内容。所以「列表里没有某个应用」不等于「这个团队里没有」，可能是没权限看那个容器。

范围永远限于**调用方自己团队**（一团队一 base），不收 `baseId`。身份由网关注入，请求体里的身份字段一律被忽略。

## 五个 id / 字段别混

| 字段 | 是什么 | 从哪来 | 注意 |
|---|---|---|---|
| `applicationId` | 应用在我们这边的关联行 id，`apl` 开头 | 本操作；两个列表的 `applications[].itemId` 是同一个值 | `deleteNotebookItem` / `renameNotebookItem` 传它时 `itemType` 用 `application` |
| `sessionId` | 应用服务那边的会话 id（**编辑器主键**） | 只有本操作给 | **可能是 `null`**，见下 |
| `notebookId` | 所属多维表，`nbk` 开头 | 本操作直接给 | 别跟 `tableId`（`tbl`）混 |
| `notebookName` | 所属多维表的名字 | 本操作 join 出来的 | 容器行缺失时会是空串 `""`，不当异常 |
| `folderId` | 在哪个文件夹里 | 本操作；为空时不带这个字段 | 要文件夹名字再 `listMyTables` 看 `folders[]` |

**`sessionId` 为 `null` 是正常回退**：存量应用、或创建时出站失败。含义是**这个应用进不去编辑器**，不是接口出错、也不是权限问题，别当异常处理、也别重试。要打开只能用 `applicationId` 走页面。

`publishVisibility` 只有 `public` / `private` 两档：`public` = 已公开分享，`private` = 没分享或只分享给了指定人；认不出的库值一律按 `private` 报（档位是授权依据，猜错方向等于把私有应用当公开的报出去）。`publishUrl` 与它**正交**：可以是 `public` 而 `publishUrl` 仍为 `null`（还没生成过），所以「有 URL」才是能直接发给别人的充分条件。

---

## listApplications —— 列出我的应用（含协作给我的）

**何时用 / 不该用**：
- 用：用户说「我的应用 / 有哪些应用 / 应用列表 / 某某应用 / 这个多维表里有哪些应用」；要拿 `sessionId` 去应用编辑器；要看某个应用发布没发布。
- 不该用：要看多维表里**全部内容**（表 + 仪表盘 + 文件夹 + 页面 + 应用）的导航结构 → `listMyTables` / `listSharedTables`；要**删 / 改名**应用 → 先在这里拿 id，再 `deleteNotebookItem` / `renameNotebookItem`（`itemType: "application"`）；要**建应用** → `createApplication`（见本文件下半节）；要看表里的**数据** → `listRecords`。

**调用**：`python scripts/smart_table.py listApplications '{}'`。参数整个省略等价于 `{}`。

### 参数
全部可选、可任意叠加（叠加即 AND）。

| 参数 | 类型 | 必填 | 默认 | 约束 | 说明 |
|---|---|---|---|---|---|
| name | string | 否 | 不传 | 1~255 字 | 应用名，**包含匹配**、大小写不敏感。不用给全名 |
| notebookId | string | 否 | 不传 | `nbk` 开头的非空字符串 | 只看这一个多维表。**看不见或不存在 → 404**（两者不区分，防探测） |
| notebookName | string | 否 | 不传 | 1~255 字 | 多维表名，**包含匹配**、大小写不敏感，服务端解析。命中多个多维表就列出这些多维表下的全部应用 |
| source | string | 否 | `all` | `mine` / `shared` / `all` | `mine` = 我创建的（按 `createdBy`），`shared` = 协作给我的。两档合起来就是 `all`，不重不漏 |
| page | integer | 否 | 1 | ≥1 | 第几页（从 1 起） |
| perPage | integer | 否 | 100 | 1~100 | 每页几条 |

### 响应
| 字段 | 类型 | 说明 |
|---|---|---|
| total | integer | **应用总数**（已套用全部过滤条件），不是多维表数 |
| perPage / currentPage | integer | 回显入参 |
| applications | array[object] | 当前页的应用，按创建时间倒序（不可参数化） |
| applications[].applicationId | string | `apl` 开头 |
| applications[].name | string | 应用名 |
| applications[].notebookId | string | 所属多维表 |
| applications[].notebookName | string | 所属多维表的名字；容器行缺失时为空串 |
| applications[].sessionId | string \| null | **编辑器主键**。`null` = 进不去编辑器，正常回退 |
| applications[].source | `mine` \| `shared` | 我创建的 / 协作给我的 |
| applications[].publishUrl | string \| null | 发布地址。`null` = 还没发布过（常态） |
| applications[].publishVisibility | `private` \| `public` | 认不出的库值按 `private` 报 |
| applications[].folderId | string | 所在文件夹（最近那层）。直接挂在多维表下时**不带这个字段** |
| applications[].createdTime | string | ISO 8601 |

### 语义与坑
- **出参是一层扁平的**，跟两个列表的两层形状不同：`total` 是应用数，每项自带 `notebookId` + `notebookName`。
- **`notebookName` 是过滤器，不是寻址**：0 个多维表命中时回**空列表**（不是 404）。只有 `notebookId` 才 404。
- **`notebookId` 不可见 / 不存在 / 在回收站里 → 一律 404**，`errmsg` 只说「Notebook xxx not found」。这是刻意的：区分这两种情况等于让人拿 id 探别人的容器。别把它读成「这个多维表里没有应用」，也不要去猜是哪种成因。
- **`source` 判的是 `createdBy`**，不是容器角色：别人建的多维表里我建的应用算 `mine`。出参**不回 `createdBy`**（组织结构信息），只有归一后的 `mine` / `shared`。
- **空结果是成功**，成因有三种，脚本会在 stdout 提醒：① 确实一个应用都没有；② 名字 / 多维表名没匹配上（两者都是包含匹配）；③ 那些多维表当前身份看不见。汇报时把可能的成因说清，别只报「没有应用」。
- **没有 `sessionId` 的应用**会在 stdout 被列出来（最多 10 个）。汇报时按「进不去编辑器」说，别说失败。
- 名称过滤是 `contains` 扫描，不加索引；量级是每个容器个位数，不用担心。

### 常见错误
| errmsg 关键词 | 原因 | 怎么办 |
|---|---|---|
| 本地：`notebookId 传的是数据表 id（tbl 开头）` | 把 `tableId` 当 `notebookId` 传了 | 改取多维表的 `notebookId`（`nbk` 开头） |
| 本地：`source 只能是 mine / shared / all` | 传了别的值 | 三选一，或整个省略 |
| 本地：`xxx 必须是非空字符串，或整个省略` | 传了空串 / 非字符串 | 传值或省略该参数 |
| 404 `Notebook … not found` | 指定的多维表不存在、进了回收站、或不是我能看见的 | 用 `listMyTables` / `listSharedTables` 重新确认；不要换 id 猜 |
| 400 入参不合法 | 参数不对 | 按 `errmsg` 改 |
| 401 | 身份未确立：网关未注入身份头，或该成员在用户中心查不到 | 检查 API Key 配置 |
| 500 / 503 | 服务端异常 / 数据库暂不可用 | 只读接口，稍后重试即可，安全 |

### 示例
**1. 列出全部应用**
```json
{}
```

**2. 按应用名找**
```json
{"name": "销量"}
```

**3. 只看某个多维表下的、只要协作给我的**
```json
{"notebookName": "门店经营", "source": "shared"}
```

**4. 翻页**
```json
{"page": 2, "perPage": 20}
```

---

## createApplication —— 按模板在已有多维表里建应用

**何时用 / 不该用**：
- 用：用户说「按这个模板建个应用 / 在这个多维表里建个应用 / 给我建个应用 / 新建应用 / 创建应用」，而且这个**多维表已经存在**、要用的**应用模板**也定了。
- 不该用：连多维表都还没有 → 先 `createTable`（或 `copyNotebook`）拿到 `notebookId`；要建的是**数据表** → `addTable`；还没选模板 / 不知道有哪些应用模板 → 先 `listOfficialTemplates` 传 `{"templateType":"app"}`；只是想看有哪些应用 / 拿 `sessionId` → `listApplications`。

**调用**：`python scripts/smart_table.py createApplication '{"notebookId":"nbkXXX","templateId":"<模板 resourceId>"}'`

### 参数
| 参数 | 类型 | 必填 | 默认 | 约束 | 说明 |
|---|---|---|---|---|---|
| notebookId | string | **是** | —— | `nbk` 开头的非空字符串 | 建在哪个多维表下。取 `listMyTables` / `listSharedTables` 顶层 `notebooks[].notebookId`，或 `createTable` / `copyNotebook` 的出参 |
| templateId | string | **是** | —— | 非空字符串，取 `list[].resourceId`（短横线 slug，如 `blank-template`） | 用哪个**应用模板**建。⚠️ `listOfficialTemplates` 每项有**两个** id：`id` 是 32 位十六进制（只给本接口自己按 `id` 精确筛选用），`resourceId` 是 slug —— **这里要的是 `resourceId`**。传 32 位 `id` 会回 424 `App template directory not found`。它不是 `notebookId`、也不是本地路径 |
| name | string | 否 | `应用` | 1~255 字，首尾空白会被去掉 | 应用名。不传就用「应用」 |

`notebookId` 传成数据表 id（`tbl` 开头）在本地就会被拦下 —— 不拦的话服务端回的是 `Notebook tblxxx not found`，很容易被误读成「这个多维表不存在」。

`templateId` 忘了传也在本地就拦下：服务端那边它是必填，少了只会回一个笼统的入参错误，看不出是缺了模板。

⚠️ **`templateId` 要 `resourceId`，不是 `id`**：`listOfficialTemplates` 每条都有 `id`（32 位十六进制，如 `de2f18da41894e92b2421e5ac6c2f6ec`）和 `resourceId`（slug，如 `blank-template`、`amazon-search`）。应用服务是按 `resourceId` 去找模板源码目录的，传 `id` 会回 `424 App template directory not found` —— 这个报错看着像「模板不存在 / 已下架」，其实只是拿错了字段，别去重建模板或换模板。

### 响应
| 字段 | 类型 | 说明 |
|---|---|---|
| notebookId | string | 回显建在了哪个容器里 |
| applicationId | string | `apl` 开头。**删 / 改名时当 `itemId` 用**（`itemType: "application"`） |
| sessionId | string \| null | 进应用编辑器的会话 id。正常创建必回，`null` 只作契约兜底 |
| sourceUrl | string \| null | 这个应用的**源代码包**（`.tar.gz`）下载地址。外部 agent 下它、改完代码再发布。**服务端不落库**，这次没拿到就再也拿不到（上游没给时是 `null`，应用照样是建好的） |
| name | string | 应用名，**回采自服务端**（不是回显入参） |

### 语义与坑
- ⚠️ **不幂等**：每次调用都会让应用服务新建一个会话、我们这边新建一行应用，没有幂等键。**超时 / 断连 / 拿不准成没成时，先 `listApplications` 看有没有多出这个应用**，确认没建出来再重试；直接重发会多出一个应用（还多一个用不上的会话）。
- ⚠️ **同一用户同时只能建一个**：上一个创建请求还没跑完就再调一次，回 `errcode=409`「已有应用正在创建中」。这是按**用户**挡的 —— 跟是哪个多维表、哪个模板**都无关**。等上一个跑完再调即可；这把锁最长 2 分钟自己过期。**409 时什么都没建**，不是失败重试。
- **`(notebookId, templateId)` 重复是正常需求**：一个多维表里用同一个模板建多个应用**不拦**、也不做内容幂等。别自己加「看起来重复了就不建」的判断。
- ⚠️ **`sourceUrl` 不落库**：它是让外部 agent 下载源码用的临时地址，我们只透传、不留档。这次没拿到就再也拿不到（除非重建一个应用），也别去 `listApplications` 里找 —— 那里没有这个字段。
- **网络失败 ≠ 没建成**：出站请求超时的报错（`应用服务连接失败：…`）只说明没拿到回包，对方**可能已经把会话建好了**。这种情况尤其要先查一遍，实在查不出来就如实告诉用户「可能建了一半」。
- **报 404 有三种成因、故意不区分**：这个多维表不存在、进了回收站、不在你团队里（或当前身份看不见）。`errmsg` 只说 `Notebook xxx not found`。别把它读成某一种，更不要换 id 猜。
- **权限比「能看见」更严**：能往这个多维表里建数据表的人才能建应用（同一个容器写权门）。容器角色是创建者 / 可编辑可以；**「可查看」和无权一律回 404**，不是 403。
- **名字只是创建时的快照**：它会作为标题传给应用服务的会话。之后 `renameNotebookItem` 改名**只改我们这边**，应用服务那边的会话标题不跟着变 —— 别向用户承诺两边同步。
- **应用属于容器，不属于 base**：它挂在多维表节点下，删多维表 / 删文件夹（含它）会一并带走。
- `sessionId` 拿不到时脚本会在 stdout 提醒。那种情况下应用本身是建好了的，用 `applicationId` 走页面；要再拿会话只能重新建一个应用。
- 上游的具体失败文案（状态码、它自己返回的 message）会**原样出现在 `errmsg` 里**，转述给用户就行（见 SKILL.md 通用规则第 8 条）。

### 常见错误
| errmsg 关键词 | 原因 | 怎么办 |
|---|---|---|
| 本地：`notebookId 必填` | 没传 | 按上面「参数」节取 `nbk` 开头的 id |
| 本地：`notebookId 传的是数据表 id（tbl 开头）` | 把 `tableId` 当 `notebookId` 传了 | 改取多维表的 `notebookId` |
| 本地：`templateId 必填` | 没传模板 | 先 `listOfficialTemplates` 传 `{"templateType":"app"}`，取每条模板的 **`resourceId`** 当 `templateId` |
| 本地：`templateId 必须是非空字符串` | 传了空串 / 非字符串 | 从 `listOfficialTemplates` 的 `templateType=app` 结果里取 **`resourceId`** |
| 本地：`name 必须是非空字符串，或整个省略` | 传了空串 / 非字符串 | 传个名字，或整个省略（用缺省「应用」） |
| **409 `已有应用正在创建中`** | 你自己上一个创建应用的请求还没跑完 | **什么都没建**。等它跑完再调（锁最长 2 分钟自己过期）；别改参数重试、也别去 `listApplications` 找残留 |
| 404 `Notebook … not found` | 多维表不存在 / 在回收站 / 不在我团队 / 我只是「可查看」 | 用 `listMyTables` / `listSharedTables` 重新确认；没有建表权限就请容器创建者授权 |
| 400 入参不合法 | 参数不对（含模板 `resourceId` 不存在 / 已下架） | 按 `errmsg` 改；`templateId` 重新从 `listOfficialTemplates` 取 `resourceId` |
| **424 `App template directory not found`** | `templateId` 传成了 32 位 `id`（不是 `resourceId`），或该 slug 的模板源码目录确实不存在 | 先核对是不是拿的 `list[].resourceId`；确认无误才当模板问题处理 |
| 401 | 身份未确立：网关未注入身份头，或该成员在用户中心查不到 | 检查 API Key 配置 |
| 403 | 身份对但没权限（少见：容器那条路一律回 404） | 按 `errmsg` 处理，多半是请容器创建者授权 |
| `应用服务连接失败：…` | 出站到应用服务没拿到回包 | **先 `listApplications` 确认没建出来再重试**；可能已建了一半 |
| `应用服务返回错误（424）：…` | 应用服务明确拒绝，括号后是它返回的原文 | 按括号里的原文处理，改参数解决不了就报给用户 |
| `无法创建应用：缺少用户身份信息，请重新登录后再试` | 网关注入的身份里没有 `groupId` / `memberId` | 换参数解决不了，检查 API Key / 网关身份注入 |
| `创建应用失败：本次创建的会话已被占用`（409） | 上游给的会话 id 撞了唯一约束（极少见），**不是**上面那把创建锁 | **什么都没建**。重新发起一次创建即可 |
| 500 / 503 | 服务端异常 / 数据库暂不可用 | **先 `listApplications` 确认没建出来再重试**（不幂等） |

### 示例
**1. 按模板建、用缺省名「应用」**
```json
{"notebookId": "nbkXxx0000001", "templateId": "blank-template"}
```

**2. 带名字**
```json
{"notebookId": "nbkXxx0000001", "templateId": "blank-template", "name": "库存看板"}
```

**3. 典型链条：挑模板 → 找多维表 → 建应用 → 下源码**
```bash
python scripts/smart_table.py listOfficialTemplates '{"templateType":"app"}'   # 取 list[].resourceId 当 templateId
python scripts/smart_table.py listMyTables '{}'                              # 从 notebooks[].notebookId 拿 nbk
python scripts/smart_table.py createApplication '{"notebookId":"nbkXxx0000001","templateId":"blank-template","name":"库存看板"}'
# 出参里 sourceUrl 拿去下载源码包（tar.gz），sessionId 用来进编辑器
```

---

## publishApplication —— 把改完代码的应用发上线

**何时用 / 不该用**：
- 用：`createApplication` 建出应用之后，**已经把源代码改完了**，要让它上线（用户说「发布这个应用 / 把我改的发布上线 / 重新发布一下」）。
- 不该用：还没建应用 → `createApplication`；只是想知道某个应用发布没发布 → `listApplications` 看 `publishUrl` / `publishVisibility`；要**下线** → `unpublishApplication`（见本文件下一节）。

**调用**：`python scripts/smart_table.py publishApplication '{"sessionId":"<创建接口返回的 sessionId>","sourceUrl":"<改完代码包的上传地址>"}'`

### 两个 `sourceUrl` 别搞混（最容易错的一处）

| 阶段 | 谁给 | 是什么 |
|---|---|---|
| `createApplication` 出参的 `sourceUrl` | 我们返回给你 | 原始代码包的**下载**地址（tar.gz），**拿它下载** |
| `publishApplication` 入参的 `sourceUrl` | **你自己上传后拿到的新地址** | 改完之后整包传到自己的 OSS / S3 / 任何可访问存储得到的地址，**拿它发布** |

**完全没改代码时**，把创建接口给的下载地址直接传进来是可以的：服务端会下载、解包、重新构建，内容就是它刚准备好的成品。**一旦改过代码**就必须走「下载 → 改 → **重新打包上传** → 用新地址发布」，否则发布的是原始代码。

另外：下载包里的 `.env` / `.env.local` **已经由服务端填好** `clientId` / `NEXT_PUBLIC_NOTE_BOOK_ID` / `NEXT_PUBLIC_APPLICATION_ID`，不要再用模板里的占位符覆盖。发布侧会校验这两个文件都存在且含 clientId，缺了会被拒。

### 参数
| 参数 | 类型 | 必填 | 默认 | 约束 | 说明 |
|---|---|---|---|---|---|
| sessionId | string | **是** | —— | 非空字符串 | **创建接口返回的**那个 `sessionId`（进编辑器的会话 id），绑在那一行应用上。不是 `applicationId`、不是 `notebookId` |
| sourceUrl | string | **是** | —— | 非空字符串 | **改完之后自己上传**的代码包地址。只做非空校验，不校验 URL 形状（OSS / S3 / 预签名各有各的样子） |

### 响应
| 字段 | 类型 | 说明 |
|---|---|---|
| applicationId | string | `apl` 开头，发布的是哪个应用 |
| notebookId | string | 应用所在的多维表 |
| sessionId | string | 回显发布的是哪个会话 |
| publishUrl | string | **发布地址**（上游字段叫 `appUrl`）。**已落库**，ui2 侧栏 / 详情页直接显示「已发布」，`listApplications` 也读它 |

### 语义与坑
- ⚠️ **`sourceUrl` 我们只透传、不落库**：不下载、不解析、不留档。落库的是上游返回的**发布地址** `publishUrl`，两者不是一回事。
- **失败时本地一个字节都不写**：上游返回错误（424）整条失败，`publishUrl` 保持原样 —— 可能是**上一次发布的地址**，也可能是空。**别把失败当成「已下线」**，上线状态没变。
- **重复发布同一个 `sessionId` 是安全的**（上游按 session 幂等），换了新的 `sourceUrl` 再发一次就是「用新代码覆盖上线」，这正是迭代的方式。
- ⚠️ **并发发布同一个 `sessionId` 会撞 `errcode=409`**「这个应用正在发布中，请等这次发布完成后再试」。按 `sessionId` 挡的，跟多维表无关；锁最长 2 分钟自己过期。这次**没有**发布。
- **报 404 有三种成因、故意不区分**：这个 `sessionId` 不存在（或根本不是创建接口给的）、它不在你的团队里、或者那个应用所在的多维表你只有「可查看」。`errmsg` 只说 `Application with session … not found`，别读成某一种，更别换 id 猜 —— 用 `listApplications` 重新确认真实的 `sessionId`。
- **权限与创建同一道门**：能往那个多维表里写东西的人才能发布。创建者 / 可编辑可以；「可查看」和无权一律 404，不是 403。
- **`publishUrl` 取不到按失败算**：服务端把「上游 200 但没给发布地址」当失败（424），不会写库、也不会回一个空字符串。
- 上游的具体失败文案会**原样出现在 `errmsg` 里**，转述给用户就行。

### 常见错误
| errmsg 关键词 | 原因 | 怎么办 |
|---|---|---|
| 本地：`sessionId 必填` | 没传 | 用 `createApplication` 出参那个 `sessionId`；丢了就 `listApplications` 按应用名查回来 |
| 本地：`sourceUrl 必填` | 没传 | 传**改完代码后自己上传**的地址，不是创建接口给的下载地址 |
| **404 `Application with session … not found`** | 会话不存在 / 不在你团队 / 你只是「可查看」 | 上线状态**没变**。用 `listApplications` 确认真实 `sessionId` 和容器权限 |
| **409 `这个应用正在发布中…`** | 同一个 `sessionId` 上一次发布还没跑完 | 这次**没有**发布。等它跑完，用**同样的参数**再发；锁最长 2 分钟自己过期 |
| 400 入参不合法 | `sessionId` / `sourceUrl` 空串或类型不对 | 按 `errmsg` 改 |
| 401 | 身份未确立：网关未注入身份头，或该成员在用户中心查不到 | 检查 API Key 配置 |
| `应用服务连接失败：…` | 出站到应用服务没拿到回包 | **可能已发了一半**：用 `listApplications` 看 `publishUrl` 是不是变成了新的；拿不准就重发一次（同 session 重复发是安全的） |
| `应用服务返回错误（424）：…` | 应用服务明确拒绝，括号后是它返回的原文 | 按括号里的原文处理（多半是 `sourceUrl` 不可读 / 包格式不对），改参数解决不了就报给用户 |
| 500 / 503 | 服务端异常 / 数据库暂不可用 | 稍后重试；同 session 重复发布是安全的，不会发重 |

### 示例
**1. 发布**
```json
{"sessionId": "<创建接口返回的 sessionId>", "sourceUrl": "https://my-oss.example.com/app-build/20261109.tar.gz"}
```

**2. 改完再发一版**（同一个 `sessionId`，换新的 `sourceUrl`）
```json
{"sessionId": "<创建接口返回的 sessionId>", "sourceUrl": "https://my-oss.example.com/app-build/20261109-v2.tar.gz"}
```

**3. 完整链条：建应用 → 下源码 → 改 → 上传 → 发布 → 确认**
```bash
python scripts/smart_table.py createApplication '{"notebookId":"nbkXxx0000001","templateId":"blank-template","name":"库存看板"}'
# 出参：sessionId 留着；sourceUrl 拿去下载源码包（tar.gz）
# …下载、改代码、重新打包、传到你自己的 OSS / S3…
python scripts/smart_table.py publishApplication '{"sessionId":"<上一步的 sessionId>","sourceUrl":"<你自己上传后的新地址>"}'
python scripts/smart_table.py listApplications '{"name":"库存看板"}'   # publishUrl 有值 = 已上线
```

---

## unpublishApplication —— 把已发布的应用下线（取消发布）

**何时用 / 不该用**：
- 用：应用已经发布上线了，要把它**撤下来**（用户说「取消发布 / 把应用下线 / 下线这个应用 / 撤销发布 / 别让人再访问这个地址了」）。
- 不该用：还没发布过 → 没什么可下线的，先 `listApplications` 确认 `publishUrl` 是不是本来就没值；只是想**改成新版本** → 那是 `publishApplication` 换新 `sourceUrl`，不涉及下线；想**删掉这个应用** → `deleteNotebookItem`（`itemType: "application"`），下线不删应用，应用本身和源码都还在。

**调用**：`python scripts/smart_table.py unpublishApplication '{"applicationId":"aplXxx0000001"}'`

它跟 ui2 侧栏那个「取消发布」按钮走的是**同一条**服务逻辑，入参也一样，只是换成网关这条路进来。

### 参数
| 参数 | 类型 | 必填 | 默认 | 约束 | 说明 |
|---|---|---|---|---|---|
| applicationId | string | **是** | —— | `apl` 开头的非空字符串 | 应用在我们这边的关联行 id。取 `listApplications` 出参的 `applicationId`（`createApplication` 出参同名，两个列表的 `applications[].itemId` 也是同一个值） |

⚠️ **入参是 `applicationId`，不是 `sessionId`**：用哪个会话由服务端从应用关联行上自己取。会话 id 不开放给调用方 —— 否则等于允许任何人拿别人的会话下线别人的应用。脚本本地就拦 `sessionId`，别想着两个都传。

### 响应
| 字段 | 类型 | 说明 |
|---|---|---|
| applicationId | string | 回显下线的是哪个应用 |
| notebookId | string | 应用所在的多维表 |
| sessionId | string \| null | 这个应用绑定的会话 id。**可能为 `null`**（存量应用的正常回退），跟下线成功与否无关 |
| publishUrl | `null` | **恒为 `null`** —— 取消发布清的就是发布地址。留这个字段只为与 `publishApplication` 出参同形，别拿它当「地址丢了」的异常。脚本发现它不是 `null` 会提示这次**不算下线成功** |

下线同时清三样：`publishUrl` → `null`、`publishVisibility` → `private`、`publicShareId` → `null`。之后 `listApplications` 看到的 `publishUrl` 就是 `null`，ui2 侧栏也回到「未发布」。

### 语义与坑
- ⚠️ **公开分享凭据一并撤销，且不可逆**：如果这个应用**公开分享**过，下线会把那条公开凭据（`publicShareId`）一起撤掉，**撤了回不来**。之后重新发布为「公开」会铸一条**新的**链接，之前发给别人的旧链接**永久失效**。下线前如果用户已经把链接发出去了，先把这个后果讲清楚再动手。
- **幂等**：重复取消发布是安全的，上游照常成功，本地也是同一个结果。**不像发布那样会撞 409** —— 别把「又调了一次」当成重复操作去防。
- **失败时本地一个字节都不写**：上游返回错误（424）整条失败，`publishUrl` 保持原样 —— 多半还是**上次发布的地址**。**别把失败当成「已下线」**，上线状态没变。
- **报 404 有三种成因、故意不区分**：这个 `applicationId` 不存在、它不在你的团队里、或者那个应用所在的多维表你只有「可查看」。`errmsg` 只说 `Application xxx not found`，别读成某一种，更别换 id 猜 —— 用 `listApplications` 重新确认真实的 `applicationId`。
- **报 400 多半是「没有可下线的会话」**：存量应用的 `sessionId` 为空时，服务端没有会话可派下去，回 400。这时**上线状态没变**；要彻底撤掉那个地址得在页面上操作，或者告诉用户这个应用是存量数据。
- **权限与创建 / 发布同一道门**：能往那个多维表里写东西的人才能下线。创建者 / 可编辑可以；「可查看」和无权一律 404，不是 403。
- **下线 ≠ 删除**：应用还在、源码还在、`applicationId` 不变，随时能再发布上线。
- 上游的具体失败文案会**原样出现在 `errmsg` 里**，转述给用户就行。

### 常见错误
| errmsg 关键词 | 原因 | 怎么办 |
|---|---|---|
| 本地：`applicationId 必填` | 没传 | `listApplications` 按应用名查到 `applicationId`（`apl` 开头） |
| 本地：`applicationId 必须是非空字符串` | 传了空串 / 非字符串 / 传成了 `sessionId` | 取 `apl` 开头的那个 id |
| 本地：`sessionId 不需要传` | 把 `sessionId` 和 `applicationId` 一起传了 | 只传 `applicationId` |
| **404 `Application … not found`** | 应用不存在 / 不在你团队 / 你只是「可查看」 | 上线状态**没变**。用 `listApplications` 确认真实 `applicationId` 和容器权限 |
| 400 | 入参不合法，或这个应用没有可下线的会话（存量应用 `sessionId` 为空） | 先看 `errmsg`；确实是存量应用就告诉用户要去页面上操作，上线状态没变 |
| 401 | 身份未确立：网关未注入身份头，或该成员在用户中心查不到 | 检查 API Key 配置 |
| `应用服务连接失败：…` | 出站到应用服务没拿到回包 | **可能已下线了一半**：用 `listApplications` 看 `publishUrl` 是不是变 `null` 了；拿不准就再调一次（幂等，安全） |
| `应用服务返回错误（424）：…` | 应用服务明确拒绝，括号后是它返回的原文 | 按括号里的原文处理；上线状态没变 |
| 500 / 503 | 服务端异常 / 数据库暂不可用 | 稍后重试；取消发布幂等，重复调不会调坏 |

### 示例
**1. 按应用名找到再下线**
```bash
python scripts/smart_table.py listApplications '{"name":"库存看板"}'   # 取 applications[].applicationId
python scripts/smart_table.py unpublishApplication '{"applicationId":"aplXxx0000001"}'
python scripts/smart_table.py listApplications '{"name":"库存看板"}'   # publishUrl 变 null、publishVisibility 变 private = 已下线
```

**2. 下线（已知 id）**
```json
{"applicationId": "aplXxx0000001"}
```
