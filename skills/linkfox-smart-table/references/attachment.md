# 附件列传图

本文件覆盖 `uploadAttachment` 一个操作：往附件列（`type: attachment`）的**一格**里**追加一张**图片。服务端下载图片 → 存进表格自己的存储 → 追加到这一格已有附件的末尾。
附件列存的是文件，用本操作写；图片列（`type: image`）存的只是外链字符串，直接用 `createRecords` / `updateRecords` 写 URL（两种列的区别见 `references/fields.md`）。

## uploadAttachment —— 往附件列的一格里追加一张图片

**何时用 / 不该用**：
- 用：把生成的图、采集到的商品图存进表格的附件列；给某一行补一张附件图。
- 图片列（`type: image`）写外链 → `updateRecords` / `createRecords`（见 `references/records-write.md`）。
- 删除、替换、调整附件顺序 → 让用户在页面上操作。
- 上传 PDF、Excel 等非图片文件 → 暂不支持。
- 读已有附件的查看地址 → `listRecords`（见 `references/records-read.md`）。

链路：`addFields`（`type: attachment`，先有附件列）→ `createRecords`（先有这一行）→ `uploadAttachment`（往格子里追加图）→ `listRecords`（取图片查看地址）。

**调用**：`python scripts/smart_table.py uploadAttachment '<JSON>'`

### 参数

| 参数 | 类型 | 必填 | 默认 | 约束 | 说明 |
|---|---|---|---|---|---|
| tableId | string | **是** | - | 以 `tbl` 开头 | 表 id |
| recordId | string | **是** | - | 以 `rec` 开头 | 要追加图片的那一行，必须已存在 |
| fieldName | string | **是** | - | 非空 | 附件列的**字段名**（`listFields` 里 `type: attachment` 的那列） |
| imageUrl | string | 二选一 | - | http/https，公网可访问，≤ 20MB，`image/*` | 服务端去下载的图片地址 |
| imagePath | string | 二选一 | - | 本地图片文件，≤ 20MB，扩展名 png/jpg/jpeg/gif/webp/bmp/svg | 脚本先传到平台 OSS 换成公开地址，再当 `imageUrl` 交给服务端。需要 `oss2` 依赖（`pip install oss2`） |

`imageUrl` 和 `imagePath` **必须且只能给一个**。**接口本身只收 `imageUrl`**，`imagePath` 是脚本层的能力。

### 响应

| 字段 | 类型 | 说明 |
|---|---|---|
| recordId | string | 入参原样回传 |
| fieldName | string | 入参原样回传 |
| attachment | object | 刚追加进去的那一项（不是整格），见下 |
| attachment.id | string | 附件项 id（`act` 开头） |
| attachment.name | string | 文件名（取自图片地址） |
| attachment.token | string | 文件标识，可复用（见下） |
| attachment.mimetype | string | 如 `image/png` |
| attachment.size | integer | 字节数 |
| attachment.width / height | integer | 图片宽高（可能缺） |
| attachment.presignedUrl | string | 原图查看地址，**临时** |
| attachment.smThumbnailUrl / lgThumbnailUrl | string | 小 / 大缩略图地址。缩略图异步生成，刚传完时可能等于原图地址 |

```json
{"errcode": 200, "errmsg": "ok", "recordId": "recXXXXXXXX", "fieldName": "商品图",
 "attachment": {"id": "actXXXXXXXX", "name": "a.jpg", "token": "xxxxxxxx", "mimetype": "image/jpeg",
   "size": 183245, "width": 800, "height": 800,
   "presignedUrl": "https://...", "smThumbnailUrl": "https://...", "lgThumbnailUrl": "https://..."}}
```

### 语义与坑

**只追加，一次一张**。这一格原有的图都保留，新图排在最后。要删图、换图、调顺序，让用户在页面上操作。多张图就调多次。

⚠️ **同一格并发追加会丢图**：服务端是「读出这一格 → 拼上新图 → 整格写回」，两个请求同时进来，后写的会覆盖先写的。多张图**一张一张串行调**，不要并行。

**写之前先确认两件事**：
- **那一列是附件列**：用 `listFields`（见 `references/fields.md`），`type` 必须是 `attachment`。是 `image` 就不用本操作，直接用 `updateRecords` 写 URL 字符串。表里还没有附件列，先用 `addFields` 加一列 `{"name": "商品图", "type": "attachment"}`。
- **这一行已存在**：本操作只往已有行的格子里追加。行还不存在就先用 `createRecords` 新增，拿返回的 `recordId`。

**校验顺序**：先校验字段和记录，**再**下载图片。字段名写错、记录不存在时不会产生任何文件。

**图片来源的限制**：单张 **20MB** 以内；必须是图片，服务端按下载到的 Content-Type 判 `image/*`（脚本对本地文件按扩展名先拦一道）；`imageUrl` 只支持 http/https，且要**公网能访问**，内网/本机地址会被拒绝。拿不到公网地址时改用本地文件 `imagePath`。

**服务端要先下载图片再入桶**，比普通写接口慢，脚本超时放宽到 180 秒。

**`token` 可以复用**：同一张图要挂到别的格子上，不用重新上传，用 `updateRecords` 写 `{"附件列": [{"name": "a.png", "token": "<token>"}]}`。⚠️ 这样写是**整格替换**，不是追加（见 `references/records-write.md`）。

**查看地址是临时的**：
- ⚠️ 所有 `*Url` 都是临时签名地址，最长约 **3 小时**有效。**不要存下来长期用**，之后要看图，用 `listRecords` 现取。
- `presignedUrl` 在浏览器里直接打开是**下载**而不是预览（响应头 `Content-Disposition: attachment`）；放进 `<img src>` 能正常显示。给用户「点开看图」时要说明这一点。

**不进撤销栈**。传错了让用户在页面上删掉那张图。

**权限**：只能写**自己团队 base 内**、且自己有 record 修改权限的表。

**展示**：成功后告诉用户图片已加到哪张表、哪一行、哪一列。用户要看图时把 `presignedUrl` 给出来，并说明这个链接几个小时后会失效。不要声称传成功了，除非返回 `errcode: 200`。

### 常见错误

| errmsg 关键词 | 原因 | 怎么办 |
|---|---|---|
| `缺少 tableId` / `缺少 fieldName`（本地预检） | 缺参数 | 补上 |
| `缺少 recordId`（本地预检） | 没给行 | 还没有这一行就先用 `createRecords` 新增，拿返回的 `recordId` |
| `imageUrl 和 imagePath 必须且只能给一个`（本地预检） | 两种来源都给了或都没给 | 二选一 |
| `imageUrl 只支持 http/https` / `imageUrl 必须是完整的图片地址` | 地址不是 http(s) 完整 URL | 本地文件改用 `imagePath` |
| `imagePath 指向的文件不存在` / `imagePath 不是图片文件` / `图片超过 20MB 上限`（本地预检） | 本地文件不存在、扩展名不是图片、超 20MB | 换文件或压缩后再传 |
| `本地图片上传失败` | 传平台 OSS 失败（如 `缺少 oss2 依赖`、凭证获取失败） | 按提示处理，缺依赖就 `pip install oss2` |
| `不是附件列` | `fieldName` 指向的不是 attachment 列 | `listFields` 确认列类型；`image` 列改用 `updateRecords` 写 URL；没有附件列就 `addFields` 加一列 |
| `字段 "..." 不存在` | 字段名写错 | 照报错里列出的字段名改 |
| `Record ... not found` | `recordId` 不在这张表里 | 先 `createRecords` 新增这一行 |
| `不是图片` | 下载到的不是 `image/*` | 换成真正的图片地址 |
| `File size exceeds` | 超过 20MB | 压缩后再传 |
| `Url reject` | 图片地址下载失败或被拒（内网地址、无法访问） | 换一个公网能访问的地址，或改用本地文件 `imagePath` |
| `No access to table` / `Missing permission` | 不是自己团队的表、或没有记录修改权限 | 换表或找表的所有者 |

### 示例

**1. 公网图片地址**
```json
{"tableId": "tblXXXXXXXX", "recordId": "recXXXXXXXX", "fieldName": "商品图", "imageUrl": "https://example.com/a.jpg"}
```

**2. 本地图片**
```json
{"tableId": "tblXXXXXXXX", "recordId": "recXXXXXXXX", "fieldName": "商品图", "imagePath": "./output/主图.png"}
```
