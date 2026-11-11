# 附件列上传文件

本文件覆盖 `uploadAttachment` 一个操作：往附件列（`type: attachment`）的**一格**里**追加一份**文件（图片、视频、PDF、Word/Excel/PPT、音频、压缩包等任意类型，与页面上传一致）。写进表格自己的存储 → 追加到这一格已有附件的末尾。
附件列存的是文件，用本操作写；图片列（`type: image`）存的只是外链字符串，直接用 `createRecords` / `updateRecords` 写 URL（两种列的区别见 `references/fields.md`）。

## uploadAttachment —— 往附件列的一格里追加一份文件

**何时用 / 不该用**：
- 用：把生成的图、采集到的商品图、手上的视频、PDF 手册、Excel 报表存进表格的附件列；给某一行补一份附件。
- 图片列（`type: image`）写外链 → `updateRecords` / `createRecords`（见 `references/records-write.md`）。
- 删除、替换、调整附件顺序 → 让用户在页面上操作。
- 一次传多份 → 本操作**一次只追加一份**，多份就串行调多次。
- 读已有附件的查看地址 → `listRecords`（见 `references/records-read.md`）。

链路：`addFields`（`type: attachment`，先有附件列）→ `createRecords`（先有这一行）→ `uploadAttachment`（往格子里追加）→ `listRecords`（取查看地址）。

**调用**：`python scripts/smart_table.py uploadAttachment '<JSON>'`

### 两种来源：让服务端下载，还是自己直传

同一条接口，按入参自动选。**脚本已经封装好，正常只管给 `imageUrl` 或 `filePath`**，下面这些是为了看懂输出和排错。

| 入参 | 谁把文件搬到存储 | 适用 |
|---|---|---|
| `imageUrl` | **服务端**下载后再入桶 | 网上现成的、公网可访问的文件地址 |
| `filePath`（旧名 `imagePath`） | **本机直传 S3**，不经过服务端 | 本地文件。脚本自动走三步：申请上传地址 → 直传 → 完成 |
| `uploadId` | 文件已经传完，只差「完成」 | 收尾用。完成是**幂等**的，重复调不会让一格挂两份 |
| `ticketPath` | 复用上次申请到的地址续传 | 直传中途失败时用，省一次重新申请 |

`filePath` 那条为什么要调两次：S3 直传没有回调，服务端不知道你什么时候传完，所以要回来调一次「完成」（带上 `uploadId`），它才去核对桶里真实的类型/大小、把附件挂到格子上。**这两步脚本替你连着做**，只在直传失败时才会剩下第一步让你续。

### 参数

| 参数 | 类型 | 必填 | 默认 | 约束 | 说明 |
|---|---|---|---|---|---|
| tableId | string | **是** | - | 以 `tbl` 开头 | 表 id |
| recordId | string | **是** | - | 以 `rec` 开头 | 要追加附件的那一行，必须已存在 |
| fieldName | string | **是** | - | 非空 | 附件列的**字段名**（`listFields` 里 `type: attachment` 的那列） |
| imageUrl | string | 四选一 | - | http/https，公网可访问；大小按类型分档（见下） | 让服务端去下载的地址 |
| filePath | string | 四选一 | - | 本地文件，任意类型；大小按类型分档（见下） | 本地文件，脚本直传 S3。`imagePath` 是旧名，照旧可用 |
| uploadId | string | 四选一 | - | 签发时返回的那个 id | 已经传完、只差完成 |
| ticketPath | string | 四选一 | - | 上次输出里 `Saved upload ticket` 的路径 | 续传，复用同一个 `uploadId` |
| filename | string | 否 | 文件名 | - | 展示名（格子里显示的名字） |
| contentType | string | 否 | 按扩展名猜 | 任意 mimetype | 只在扩展名猜不准时才需要显式给（它会被签进上传地址，事后改不了） |

上面四种来源**必须且只能给一个**。

### 大小上限（按文件类型分档）

| 类型 | 上限 |
|---|---|
| 图片（`image/*`） | 20MB |
| 视频（`video/*`） | 50MB |
| Excel（`application/vnd.ms-excel`、`...spreadsheetml.sheet`，即 xls / xlsx） | 50MB |
| 其余（PDF、Word、PPT、音频、压缩包等） | 不设专门上限，由全局阈值兜底：50MB |

⚠️ CSV **不算 Excel**，按「其余」走——落到全局阈值那档（也是 50MB），不是 Excel 那一档。

### 响应

| 字段 | 类型 | 说明 |
|---|---|---|
| recordId | string | 入参原样回传 |
| fieldName | string | 入参原样回传 |
| attachment | object | 刚追加进去的那一项（不是整格），见下 |
| attachment.id | string | 附件项 id（`act` 开头） |
| attachment.name | string | 展示名 |
| attachment.token | string | 文件标识，可复用（见下）。⚠️ **与签发时的 `uploadId` 是同一个值**，不是两个 id |
| attachment.mimetype | string | 如 `image/png`、`video/mp4` |
| attachment.size | integer | 字节数 |
| attachment.width / height | integer | 图片宽高（图片才有，可能缺） |
| attachment.presignedUrl | string | 原文件地址，**临时** |
| attachment.smThumbnailUrl / lgThumbnailUrl | string | 缩略图地址，**只有图片和 PDF 有**；异步生成，刚传完可能等于原图地址。PDF 取首页（空白页会跳过）。**视频和其它类型没有缩略图** |

```json
{"errcode": 200, "errmsg": "ok", "recordId": "recXXXXXXXX", "fieldName": "商品视频",
 "attachment": {"id": "actXXXXXXXX", "name": "a.mp4", "token": "xxxxxxxx", "mimetype": "video/mp4",
   "size": 12582912, "presignedUrl": "https://..."}}
```

申请上传地址那一步（`filePath` 模式的第一步）的响应长这样，脚本会把它落盘并用在下一步：

| 字段 | 说明 |
|---|---|
| uploadId | 上传标识，等于最终附件的 `token`；完成时要把它传回去 |
| url | 预签名上传地址，直接 PUT 文件到这个地址 |
| uploadMethod | 用哪个 HTTP 方法传（`PUT`） |
| requestHeaders | 传的时候必须**原样带上**的请求头（`Content-Type` 签进了地址，事后改不了） |
| expiresIn | 这个地址还有多少秒过期（默认 1 小时，可能被服务端缩短） |

### 语义与坑

**只追加，一次一份**。这一格原有的附件都保留，新附件排在最后。要删、换、调顺序，让用户在页面上操作。多份就调多次。

⚠️ **同一格并发追加会丢失**：服务端是「读出这一格 → 拼上新附件 → 整格写回」，两个请求同时进来，后写的会覆盖先写的。多份**一份一份串行调**，不要并行。

**写之前先确认两件事**：
- **那一列是附件列**：用 `listFields`（见 `references/fields.md`），`type` 必须是 `attachment`。是 `image` 就不用本操作，直接用 `updateRecords` 写 URL 字符串。表里还没有附件列，先用 `addFields` 加一列 `{"name": "商品图", "type": "attachment"}`。
- **这一行已存在**：本操作只往已有行的格子里追加。行还不存在就先用 `createRecords` 新增，拿返回的 `recordId`。

**校验顺序**：先校验字段和记录，**再**动文件。字段名写错、记录不存在时不会产生任何文件，也不会白传。

**类型不设限**：图片、视频、PDF、Word/Excel/PPT、音频、压缩包等都能传，与页面上传一致。大小按类型分档（见上表），几档不通用——20MB 的图不能放宽成 50MB。`imageUrl` 只支持 http/https 且要**公网能访问**，内网/本机地址会被拒绝；拿不到公网地址时改用本地文件 `filePath`。

**服务端会按桶里文件的实测类型/大小再判一次**。直传时声明的大小不参与校验（只有 `Content-Type` 被签进了地址），所以「填小一点混过去」不成立：完成时超限会被拒，**那份文件也会被删掉**，得压缩后重传。

**`imageUrl` 模式服务端要先下载整个文件再入桶**，比普通写接口慢，脚本超时放宽到 180 秒。

**上传地址 1 小时内有效**（`expiresIn` 可能有更短的值，以输出为准）。过期了重新跑一次 `filePath` 即可，不用清理什么。

**`token` 可以复用**：同一份文件要挂到别的格子上，不用重新上传，用 `updateRecords` 写 `{"附件列": [{"name": "a.png", "token": "<token>"}]}`。⚠️ 这样写是**整格替换**，不是追加（见 `references/records-write.md`）。

**查看地址是临时的**：
- ⚠️ 所有 `*Url` 都是临时签名地址，最长约 **3 小时**有效。**不要存下来长期用**，之后要看，用 `listRecords` 现取。
- `presignedUrl` 在浏览器里直接打开是**下载**而不是预览（响应头 `Content-Disposition: attachment`）；图片放进 `<img src>` 能正常显示，**视频在页面里没有播放器**，只能下载下来看。给用户「点开看」时要说明这一点。

**不进撤销栈**。传错了让用户在页面上删掉那一份。

**权限**：只能写**自己团队 base 内**、且自己有 record 修改权限的表。

**展示**：成功后告诉用户文件已加到哪张表、哪一行、哪一列。用户要看时把 `presignedUrl` 给出来，并说明这个链接几个小时后会失效、点开是下载。不要声称传成功了，除非返回 `errcode: 200`。

### 常见错误

| errmsg 关键词 | 原因 | 怎么办 |
|---|---|---|
| `缺少 tableId` / `缺少 fieldName`（本地预检） | 缺参数 | 补上 |
| `缺少 recordId`（本地预检） | 没给行 | 还没有这一行就先用 `createRecords` 新增，拿返回的 `recordId` |
| `必须且只能给一个`（本地预检） | 四种来源给了不止一个 | 只留一个 |
| `缺少上传方式`（本地预检） | 四种来源一个都没给 | 给 `imageUrl` 或 `filePath` |
| `imageUrl 只支持 http/https` | 地址不是 http(s) | 本地文件改用 `filePath` |
| `filePath 指向的文件不存在`（本地预检） | 路径错了 | 换成正确的路径 |
| `的类型没认出来，请显式传 contentType`（本地预检） | 扩展名没映射、`mimetypes` 也猜不出 | 显式传 `contentType`（如 `application/pdf`）；它是签进上传地址的，事后改不了 |
| `是空文件（0 字节）`（本地预检） | 传了个空文件 | 换有内容的文件 |
| `图片最大 20MB` / `视频最大 50MB` / `Excel最大 50MB` / `文件最大 50MB`（本地预检） | 超过本类型那一档 | 压缩后再传 |
| `最大 ... 已删除，请压缩后重传` | 服务端按桶里实测的类型/大小复判超限（本地预检漏掉的） | 压缩后重传；那份文件服务端已删 |
| `不存在或已过期` | `uploadId` 过期（超过 1 小时）或已经用过 | 重新跑一次 `filePath` |
| `不属于这一格` | 拿别处签的 `uploadId` 往这一格塞，或换了 tableId/recordId/列 | 对目标格重新申请 |
| `不是附件列` | `fieldName` 指向的不是 attachment 列 | `listFields` 确认列类型；`image` 列改用 `updateRecords` 写 URL；没有附件列就 `addFields` 加一列 |
| `字段 "..." 不存在` | 字段名写错 | 照报错里列出的字段名改 |
| `Record ... not found` | `recordId` 不在这张表里 | 先 `createRecords` 新增这一行 |
| `imageUrl 指向的文件下载失败` / `Url` 相关 | 地址下载失败或被拒（内网、无法访问） | 换一个公网能访问的地址，或改用 `filePath` |
| `当前存储是 local` / `PRESIGN_ROLE` | 服务端没配好直传（签出来的地址 agent 够不着）。**不是你的参数问题** | 改用 `imageUrl` 方式；长期解要服务端配好 |
| `No access to table` / `Missing permission` | 不是自己团队的表、或没有记录修改权限 | 换表或找表的所有者 |

直传失败时脚本会在 stderr 给出续跑用的 JSON（`ticketPath` 指回票据文件），照它重跑即可，**不会重复挂一份**。

### 示例

**1. 公网图片地址**
```json
{"tableId": "tblXXXXXXXX", "recordId": "recXXXXXXXX", "fieldName": "商品图", "imageUrl": "https://example.com/a.jpg"}
```

**2. 本地图片**
```json
{"tableId": "tblXXXXXXXX", "recordId": "recXXXXXXXX", "fieldName": "商品图", "filePath": "./output/主图.png"}
```

**3. 本地视频**（上限 50MB）
```json
{"tableId": "tblXXXXXXXX", "recordId": "recXXXXXXXX", "fieldName": "商品视频", "filePath": "./output/演示.mp4"}
```

**4. 本地 PDF / Excel**（PDF 走「其余」那档，全局阈值 50MB；xlsx 上限 50MB）
```json
{"tableId": "tblXXXXXXXX", "recordId": "recXXXXXXXX", "fieldName": "资料", "filePath": "./output/产品手册.pdf"}
```
```json
{"tableId": "tblXXXXXXXX", "recordId": "recXXXXXXXX", "fieldName": "报表", "filePath": "./output/对账单.xlsx"}
```

**5. 直传失败后续跑**（路径取自上一次输出里的 `Saved upload ticket`）
```json
{"tableId": "tblXXXXXXXX", "recordId": "recXXXXXXXX", "fieldName": "商品视频", "ticketPath": "/.../linkfox-smart-table-upload-attachment-ticket-xxx.json"}
```
