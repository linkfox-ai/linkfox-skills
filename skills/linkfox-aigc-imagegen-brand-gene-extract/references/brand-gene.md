# 品牌基因输入、视觉规范与输出约定

本文件定义本地编排与下游 textgen 的数据约定；LinkFox 服务接口见 [接口定义](api.md)。

## 输入参数

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| images | list[image] | — | 用户上传的商品图片列表（至少 1 张），用于分析商品色彩与气质 |
| brandKey | object | — | 用户输入的品牌基因信息（见下方字段说明） |

### brandKey 字段说明

| 字段 | 类型 | 默认 | 说明 |
|------|------|------|------|
| brandColor | string | "" | 品牌主色（HEX 值），非空时直接使用，为空时自动提取 |
| fontStyle | string | "" | 字体风格，非空时直接使用，为空时自动提取 |
| brandName | string | "" | 品牌名称，用于品牌植入策略 |
| language | string | "英文" | 目标市场语言 |
| platform | string | "亚马逊" | 发布平台（Amazon/TikTok/Shopee 等） |
| salesRegion | string | "美国" | 销售地区/国家 |

`language`、`platform`、`salesRegion` 缺失或为空时分别使用“英文”“亚马逊”“美国”；`brandKey` 完全为空时同样填充这些默认值，主色和字体自动提取。

## 品牌视觉基因提取指令

- **输入**：步骤 1 的决策路由表、`brandKey` 全部字段
- **操作**：将以下品牌视觉基因提取指令与 `brandKey` 参数拼装为完整 prompt，传入步骤 3：

  **角色**：你是顶尖品牌视觉专家和创意总监，基于商品图片与参数，构建一套统一的视觉语言，确保品牌在不同场景下的高度一致性。

  **A. 统一视觉主题（UNIFIED_VISUAL_THEME）**

  1. **Brand Color（品牌主色）**：用户给定 `brandColor` 时直接采用，不受自动选色规则覆盖；为空时按以下规则自动提取：
     - 定义一个具有"世界观"的核心色，而不仅仅是色板
     - 唯一性：全案只能定义 1 个核心 HEX 色值
     - 来源：必须考虑商品本身的颜色，具备极高审美
     - ⚠️ **黑白灰协议（CRITICAL）**：除非商品本身为黑白灰，否则禁止使用黑白灰作为主色，必须输出具体色值（如 #EAF86C）

  2. **背景策略（Background Strategy）**：必须**完整输出以下 4 个子字段，缺一不可**，每个都给出具体内容（不得留空、不得只写字段名）：
     - **背景策略-风格定义**：根据 `salesRegion` 做文化本土化的整体环境风格。追求 100% 摄影级写实环境，严禁分层背景图层感，侧重生活方式与情感共鸣。
       示例：`"现代北欧极简家居，原木与暖白色调，落地窗自然采光，符合美国中产审美"`
     - **背景策略-场景关键词**：逗号分隔的具体场景/道具关键词。
       示例：`"原木长桌, 亚麻桌布, 绿植, 陶瓷器皿, 晨光"`
     - **背景策略-光影**：明确的光线方向、色温与氛围（**这是必填字段，最易被漏，务必输出**）。
       示例：`"柔和自然侧光，暖色温 4000K，营造清晨慵懒氛围，轻微长投影增强立体感"`
     - **Brand Injection（品牌植入）**：品牌主色 / Logo / 标识元素如何自然融入场景（**这是必填字段，最易被漏，务必输出**）。
       示例：`"品牌主色作为抱枕/标签点缀色出现，Logo 以低饱和压印形式出现在道具上，不喧宾夺主"`

  **B. 绝对字体锁定（LOCKED_TYPOGRAPHY）**

  1. **字体风格**：用户给定 `fontStyle` 时直接采用；为空时从以下库中锁定唯一一种风格：
     - 几何无衬线体：Jost, League Spartan, Montserrat, Manrope, Outfit
     - 硬朗无衬线体：Bebas Neue, Oswald, Barlow Condensed, Anton, Fjalla One
     - 经典优雅衬线体：Bodoni Moda, Playfair Display, Prata, Cormorant Garamond, DM Serif Display
     - 圆润童趣字体：Nunito, Quicksand, Varela Round, Fredoka, Baloo 2
     - 俏皮手写风格: Pacifico, Permanent Marker, Amatic SC, Caveat, Luckiest Guy

  2. **颜色策略**：
     - 标题色（Heading Color）：必须使用品牌主色或反白色；当标题底部颜色是品牌主色或同色系时，自动触发"灵活反白"；其次考虑使用品牌主色同色系颜色（禁止接近黑色的颜色，颜色不能过深）
     - 正文色（Body Color）：与标题色区分，确保可读性
     - ⚠️ **输出格式注意**：颜色策略输出格式为 `["Heading Color"：颜色值]` 和 `["Body color"：颜色值]`，这是颜色定义而非文本内容

  3. **灵活反白权限**：当使用深色背景或纯品牌色色块时，授权切换为哑光白（#FFFFFF）文本

  4. **排版限制**：统一为非斜体（Non-italic），行距适中（standard leading）

  **输出要求**：严格按照下方「输出格式」输出完整 JSON，禁止输出任何解释性文字或代码块标记。

- **输出**：完整的 textgen prompt 字符串
- **用途**：作为步骤 3 的 prompt 输入

## textgen 参数约定

使用 `linkfox-aigc-textgen` 的默认模式，经 `--stdin` 传入 UTF-8 JSON 参数文件；不用 `--content-only`，因为需要回读 content 做字段提取，而非直接串入出图链。

| 字段 | 类型 | 必填 | 约定 |
|---|---|---|---|
| prompt | string | 是 | 完整品牌视觉指令、brandKey 信息与本文件的输出格式要求。 |
| imageUrls | array[string] | 是 | 按原始图片顺序复用或上传得到的公开 HTTP(S) URL，不传本地路径或失败项。 |
| model | string | 是 | `GEM_3_1_PRO`，需要视觉理解与复杂推理。 |
| thinkingLevel | string | 是 | `high`。 |

| 返回值 | 类型 | 约定 |
|---|---|---|
| content | string | 解析方式遵循下游 textgen 的输出契约；将 `⏎` 先还原为换行，再提取品牌基因字段。 |


## 输出格式

严格按照以下 JSON 格式输出，输出为长度为 1 的列表：

```json
[
  {
    "brandColor": {
      "brandColor (品牌主色)": "颜色名称与HEX值",
      "背景策略-风格定义": "基于 salesRegion 的风格描述",
      "背景策略-场景关键词": "关键词1, 关键词2, ...",
      "背景策略-光影": "光影氛围描述",
      "Brand Injection（品牌植入）": "品牌元素如何植入场景"
    },
    "fontStyle": {
      "字体策略": "选定的字体家族名称",
      "字体风格": "选定的具体字体名称",
      "颜色策略-Heading": "[\"Heading Color\"：颜色值/反白逻辑]",
      "颜色策略-Body/Sub": "[\"Body color\"：颜色值]",
      "灵活反白": "You are authorized to switch to Matte White (#FFFFFF) text whenever using a dark background or a solid brand-color panel.",
      "排版": "Non-italic, standard leading"
    }
  }
]
```

### 输出字段定义

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| 根节点 | array[object] | 是 | 长度为 1 的列表。所有下列叶子字段必须存在且为非空字符串。 |
| [0].brandColor | object | 是 | 主色与背景策略。 |
| [0].brandColor.brandColor (品牌主色) | string | 是 | 自动提取为颜色名称与 HEX 值；用户给定主色时直接使用。 |
| [0].brandColor.背景策略-风格定义 | string | 是 | 结合 salesRegion 的文化本土化摄影级写实场景。 |
| [0].brandColor.背景策略-场景关键词 | string | 是 | 逗号分隔的场景和道具关键词。 |
| [0].brandColor.背景策略-光影 | string | 是 | 光线方向、色温与氛围。 |
| [0].brandColor.Brand Injection（品牌植入） | string | 是 | 品牌主色、Logo 和标识自然融入场景的方式。 |
| [0].fontStyle | object | 是 | 字体、颜色与排版策略。 |
| [0].fontStyle.字体策略 | string | 是 | 选定的字体家族名称。 |
| [0].fontStyle.字体风格 | string | 是 | 唯一具体字体；用户给定字体时直接使用。 |
| [0].fontStyle.颜色策略-Heading | string | 是 | `["Heading Color"：颜色值/反白逻辑]`；是颜色定义而非文本内容。 |
| [0].fontStyle.颜色策略-Body/Sub | string | 是 | `["Body color"：颜色值]`，与标题色区分并保证可读性。 |
| [0].fontStyle.灵活反白 | string | 是 | 按上方 JSON 保留深色或品牌色色块背景切换 #FFFFFF 文本的授权。 |
| [0].fontStyle.排版 | string | 是 | `Non-italic, standard leading`。 |


## 产物与 CLI

| 产物 | 目录 | 说明 |
|------|------|------|
| `brand_gene_params.json` | `<session>/data/` | textgen 入参（步骤 3 中间文件） |
| `brandGeneJson` 最终结果 | `<session>/data/linkfox-aigc-imagegen-brand-gene-extract-<ts>.json` | 经 `save_brand_gene.py` 落盘，供套图 S3 与单张 `--brand-gene-file` 复用 |

路径协议：`<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/`，与仓库 `CLAUDE.md`「输出文件位置」一致。首次运行 `--datadir` 后，保存时用 `--data-dir` 复用返回的目录和 `_meta.json`。

| 脚本参数 | 类型 | 必填 | 约定 |
|---|---|---|---|
| save_brand_gene.py input | 文件路径 | 否 | UTF-8 JSON；省略则从 stdin 读取。序列化保留中文与完整嵌套结构。 |
| --datadir | flag | 否 | 创建并打印会话 data/ 绝对路径，不读取 JSON。 |
| --data-dir | 目录路径 | 否 | 显式复用首次 `--datadir` 返回的绝对目录；最终保存时传入，也适用于 stdin。目录必须已存在并具有对应会话的 `_meta.json`。 |
| SESSION_ID | 环境变量 | 否 | 优先用此聚合同一会话；未设置时仅在进程内生成稳定 ID，不保证两次独立调用得到同一 ID，因此分步保存须传 `--data-dir`。 |
| ACPX_WORKSPACES | 环境变量 | 否 | 使用路径列表中的首个工作区作为候选根；其后依次尝试 cwd、用户家目录、临时目录。 |
| stdout | string | 输出 | 保存成功打印 `Saved full response: <绝对路径> (<N> bytes)`。 |
| _meta.json | object | 输出 | 登记技能到 skills_called、最终相对路径到 data_files，并更新 last_used_at；首次创建会话时追加 index.jsonl。 |

中间参数文件用 Write 工具或 `json.dumps` 生成，不手拼带引号与反斜杠的 JSON。`save_brand_gene.py` 只负责完整序列化与登记，不代替上游核对全部品牌字段。


## 错误处理

| 情况 | 处理 |
|------|------|
| images 为空 | 停止执行，提示用户上传至少 1 张商品图片 |
| brandKey 完全为空 | 所有字段按默认值填充（salesRegion=美国、language=英文、platform=亚马逊），主色与字体走自动提取 |
| 商品为纯黑白灰且无法提取彩色主色 | 允许使用黑白灰作为主色（黑白灰协议的唯一豁免条件） |

## 已知局限

- 品牌主色提取基于 `GEM_3_1_PRO` 对商品图片的视觉理解，可能与专业设计师判断有偏差
- 自动提取字体时限定在预设的 5 类 25 款字体中；用户给定 `fontStyle` 时直接采用该值
- 背景策略的文化本土化依赖 salesRegion 的语义理解，非结构化地域数据库
- 品牌基因 JSON 必须经 `save_brand_gene.py` 落盘到会话 `data/`，不可仅存于对话上下文
- 依赖 `linkfox-aigc-textgen` skill 可用；若 textgen 调用失败，品牌基因提取无法完成
