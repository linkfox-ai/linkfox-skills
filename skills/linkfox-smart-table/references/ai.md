# 附件 AI 列：建列时配置 AI 出图 + 显式触发生成

覆盖：建附件列时带 `ai`（`addFields` / `createTable` / `addTable`）、`fillAiField`、`getAiFillStatus`。
只有一种 AI 能力：**提示词 + 参考图出图**（与页面上附件列的 AI 配置同一种）。生成结果写进附件列，读图用 `listRecords`（见 `references/records-read.md`）。

## 可用模型

**改模型只改两处：`scripts/image_models.py` 和下面这张表**（后端不维护模型清单）。
来源：`https://ai-api.linkfox.com/image/model/config/list?bizType=71`，与页面附件列 AI 配置的下拉同一个接口；测试线同一份。2026-10-12 取值。

| model（传这个值） | 名称 | 比例 | 分辨率 | 参考图 | 积分/张（1K / 2K / 4K） |
|---|---|---|---|---|---|
| `GPT_2_5_IMAGE` | LF智能模型 G-2.5 Sunburst（**默认**） | 1:1 3:4 4:3 2:3 3:2 9:16 16:9 4:5 5:4 21:9 9:21 | 1K 2K 4K | 5 | 4~200 / 15~280 / 20~360（按质量档） |
| `GPT_2_5_F_IMAGE` | LF智能模型 G-2.5 Flare | 同上 | 1K 2K 4K | 5 | 同上 |
| `GPT_2_IMAGE` | LF智能模型 G-2 | 同上 | 1K 2K 4K | 5 | 4~120 / 15~150 / 20~300（按质量档） |
| `GEMINI_NANO_BANANA_2_1` | LF全能模型 2.1 | 1:1 3:2 2:3 3:4 4:3 4:5 5:4 16:9 9:16 21:9 | 1K 2K 4K | 5 | 40 / 50 / 60 |
| `GEMINI_FLASH_PRO` | LF全能模型 Pro | 同上（顺序不同） | 1K 2K 4K | 5 | 40 / 40 / 50 |
| `GEMINI_31_FLASH_IMAGE` | LF全能模型 2 | 同上 | 1K 2K 4K | 5 | 40 / 40 / 50 |
| `GEMINI_31_FLASH_LITE` | LF全能模型 Lite | 同上 | **只有 1K** | 5 | 20 |
| `SEEDREAM5_PRO` | Seedream 5.0 Pro | 1:1 3:4 4:3 9:16 16:9 3:2 2:3 21:9 | 1K 2K | 5 | 25 / 50 |
| `WAN2_7` | Wan 2.7 | 1:1 3:2 2:3 3:4 4:3 4:5 5:4 16:9 9:16 21:9 | 1K 2K | 5 | 25 / 25 |
| `AIDRAW_EDIT` | Linkfox-Image-1 | 1:1 2:3 3:2 3:4 4:3 9:16 16:9 21:9 | **只有 2K** | 4 | 20 |

- 不传 `model` 时脚本补 `GPT_2_5_IMAGE`；不传比例/分辨率时取该模型列表的**第一项**（与页面一致）。脚本会拦下模型不支持的比例/分辨率。
- 「参考图」是模型自己声明能用几张；接口每行最多传 9 张，超过模型上限的部分效果不保证。
- 积分扣的是**调用方自己**的账户。GPT 系列按质量档计价，接口不传质量档，实际按上游默认档扣。用户在意成本时先告诉他大概的价位。

## 建列时带 `ai`

只能配在 `type: "attachment"` 的列上。`addFields` / `createTable` / `addTable` 的 `fields[]` 每项都可以带：

| 参数 | 必填 | 说明 |
|---|---|---|
| `prompt` | 是 | 出图提示词。用 `{列名}` 引用同一行**文本类**列的值，如 `把参考图里的商品放进「{场景}」描述的场景里`。参考图不用写进提示词（见下方「语义与坑」） |
| `referenceFields` | 是 | 参考图来源列（列名数组，1~9 个，有序）。只能是 `attachment` 或 `image` 列。图会直接交给模型。**每行至少要有一张参考图**，否则那一行跳过 |
| `model` | 否 | 见上表，默认 `GPT_2_5_IMAGE` |
| `aspectRatio` | 否 | 如 `1:1`、`16:9`，必须在该模型支持的列表里 |
| `resolution` | 否 | `1K` / `2K` / `4K`，必须在该模型支持的列表里 |

```json
{
  "tableId": "tblXXXXXXXX",
  "fields": [
    {"name": "场景", "type": "longText"},
    {"name": "AI 场景图", "type": "attachment",
     "ai": {"prompt": "把参考图里的商品放进「{场景}」描述的场景里，电商主图风格", "referenceFields": ["商品图"], "aspectRatio": "1:1"}}
  ]
}
```

### 语义与坑

- **`{列名}` 和 `referenceFields` 可以引用同一次调用里一起建的列**（如上例的「场景」）。
- **参考图走 `referenceFields`，别在提示词里写 `{附件列}`**：附件列代进提示词只是一串「文件名 (token)」，模型看不到图，只会多一段噪音。提示词里说「参考图里的商品」就行。
- **提示词里引用的列，在某一行为空时，这一行整行跳过**（`getAiFillStatus` 的 failures 里报「这一行的「X」没有值」），不会拿半截提示词去出图。可能为空的列别放进提示词，或者先补上值。
- 引用写错（列不存在、参考列类型不对、引用自己）时**整批 400、一列都不建**。拼错 `ai` 里的键名也报错，不会被静默忽略。
- 列建好、写 AI 配置却失败（只有服务端异常才会）时返回 500，`errmsg` 点名哪几列已建成但没挂上 AI：可以 `deleteFields` 删掉后重加，或让用户在页面上配置。
- **接口建的 AI 列不会自动生成**（页面上建的默认会）：写入记录、改参考图都不会触发，只有 `fillAiField` 会。用户想要「改了图自动重算」，让他在页面上打开这一列 AI 配置里的「自动更新」。
- `image` 列不能配 `ai`：它只存外链，放不进生成的图。

## fillAiField —— 触发一列 AI 出图

**何时用**：AI 列配好、参考图也有了，要生成图。**不该用**：往附件列放一张现成的图 → `uploadAttachment`。

**调用**：`python scripts/smart_table.py fillAiField '<JSON>'`

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|---|---|---|
| tableId | string | 是 | - | 以 `tbl` 开头 |
| fieldName | string | 是 | - | 已配置 AI 出图的附件列的列名 |
| recordIds | string[] | 否 | - | 只生成这几行，单次 ≤ 50。不传 = 整张表（忽略视图筛选），单次最多 100 行 |
| mode | string | 否 | `emptyOnly` | `emptyOnly` 只填还没有图的行；`all` **整格覆盖**已有的图（包括手动上传的） |

| 出参 | 说明 |
|---|---|
| taskId | 用它查进度。`null` = 没有要生成的行：emptyOnly 下这些行都已经有图，或者（不传 recordIds 时）表里还没有行 |
| rowCount | 候选行数 |
| processedCount | 这次入队的行数 |
| isLimited | true = 候选超过单次上限，只入队了一部分；跑完再调一次（emptyOnly 会接着填剩下的） |
| reused | true = 这一列已有没结束的任务，返回的是**那个**任务，本次没入队任何行 |

### 语义与坑

- **异步**：立刻返回，图在后台生成，一行最长约 10 分钟。用 `getAiFillStatus` 查，完成后 `listRecords` 取图。
- **扣调用方自己的积分**，余额不足时整个任务被取消（`getAiFillStatus` 里能看到原因）。触发前确认用户知道要扣积分。
- **默认 `emptyOnly`**：重复调用不会重复扣费。`mode: "all"` 会把这一列已有的图（包括用户手动上传的）整格换掉，先跟用户确认。
- 同一列有任务在跑时不会重复入队（`reused: true`）。等它结束再调。
- 判权要这张表的**记录修改**权限。

## getAiFillStatus —— 查 AI 出图进度

**调用**：`python scripts/smart_table.py getAiFillStatus '{"tableId":"tblXXX","taskId":"tskXXX"}'`

| 出参 | 说明 |
|---|---|
| status | `pending` / `running` / `completed` / `failed` / `cancelled` |
| total / completed / failed / running / pending / cancelled | 各状态的行数 |
| failures | 失败的行与原因，最多 50 条；`failuresTruncated: true` 表示还有更多 |

- `tableId` 必须是触发时那张表；拿别的表的 taskId 一律 404。
- 最常见的失败原因有两种，都是这一行缺东西，**不会去调模型，也不扣积分**：
  - 「这一行没有可用的参考图」：参考列是空的。
  - 「这一行的「X」没有值」：提示词里 `{X}` 引用的列是空的。
  先给那几行补上，再 `fillAiField` 带 `recordIds` 重跑。
- 查询不要太频繁：一行要几十秒到几分钟，隔 30~60 秒查一次就够。

## 常见错误

| errmsg 关键词 | 原因 | 怎么办 |
|---|---|---|
| `ai 只能配在 type 为 attachment 的列上` | 给文本/图片列带了 ai | 改成 attachment 列 |
| `不是这张表的列` | `{列名}` 或 referenceFields 写错 | 用 `listFields` 核对列名 |
| `参考图只能取自 attachment 或 image 列` | 参考列选了文本列 | 换成附件列或图片列 |
| `不在可用模型里` / `不被 … 支持` | 脚本本地拦下：模型/比例/分辨率不对 | 照上面的模型表改 |
| `不是配置了 AI 出图的附件列` | fillAiField 指向的列没配 AI | 先建带 ai 的附件列，或在页面上配置 |
| `这一行没有可用的参考图` | （getAiFillStatus 的 failures）参考列为空 | 补参考图后重跑这几行 |
| `这一行的「X」没有值` | （getAiFillStatus 的 failures）提示词引用的列 X 在这一行为空 | 补上 X 的值后重跑这几行 |
| `Records not found in table` | `recordIds` 里有不存在（已删）的行；整批都没入队 | 用 `listRecords` 重新取 recordId |
| `积分` / 402 | 账户积分不足 | 提醒用户充值 |
